import asyncio
from concurrent.futures import ProcessPoolExecutor
import logging
from enum import Enum
from os import environ

from django.db import transaction

from crawler.jobs.links_parser import LinksSelenium
from crawler.models import LinksJobModel

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job execution status."""

    SUBMITTED = "s"
    IN_PROGRESS = "i"
    DONE = "d"
    ERROR = "e"


class CollectLinksJobManager:
    """Collects hyperlinks from the url using the following steps:
    1. Select the row for update and change status from SUBMITTED to
    IN_PROGRESS. Return False if select-for-update is not possible.
    2. Performing job with dedicated process
    (see `CollectLinksJobManager.ProcessPoolExecutor`) and saving result to the db.

    (!) The maximum number of tasks that can be calculated in parallel is set via
    MAX_JOB_WORKERS environment variable. If not set, 1 will be used.

    (!) If all computing resources are busy, all new tasks will be placed in a
    thread-safe queue with no limit on the number of elements.

    TODO: Set max_limit for the Queue.
    TODO: Support force termination on demand.
    """

    MAX_JOB_WORKERS = max(1, int(environ.get("MAX_JOB_WORKERS", "1")))
    EXECUTOR = ProcessPoolExecutor(MAX_JOB_WORKERS)
    LOOP = asyncio.new_event_loop()

    @classmethod
    @transaction.atomic()
    def _mark_job_as_in_progress(cls, job_id: int) -> LinksJobModel | None:
        """Change the status of the row in db to IN_PROGRESS.
        Block the row in db for selecting queries to prevent race conditions.
        If there is no such row in the database, or if the job is
        already being calculated, return None.
        """
        try:
            obj = (
                LinksJobModel.objects.filter(
                    pk=job_id, status=JobStatus.SUBMITTED.value
                )
                .select_for_update()
                .get()
            )
        except LinksJobModel.DoesNotExist:
            return None
        else:
            obj.status = JobStatus.IN_PROGRESS.value
            obj.save()
            return obj

    @classmethod
    def _run_job(cls, job_id: int):
        obj: LinksJobModel | None = cls._mark_job_as_in_progress(job_id)
        if obj is None:
            # LinksJob does not exist in database or has a status different from SUBMITTED.
            # Nothing to update.
            # TODO: support restart for completed jobs (with errors or not...)
            logger.error("ERR LinksJob %s could not be started!", job_id)
            return

        # TODO: support max execution time for the job.
        result = LinksSelenium.collect_links_with_nested(obj.url)
        LinksJobModel.objects.filter(pk=job_id).update(
            result=result,
            status=JobStatus.ERROR.value if "error" in result else JobStatus.DONE.value,
        )

    @classmethod
    def run_in_executor(cls, job_id: int):
        future = cls.LOOP.run_in_executor(cls.EXECUTOR, cls._run_job, job_id)
        return future


job_manager = CollectLinksJobManager()
