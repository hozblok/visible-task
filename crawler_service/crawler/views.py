import json

from asgiref.sync import sync_to_async
from django.core.validators import URLValidator, integer_validator
from django.http import HttpRequest, HttpResponseNotAllowed, JsonResponse

from crawler.jobs.job_manager import JobStatus, job_manager
from crawler.models import LinksJobModel


@sync_to_async
def _get_list(job_id: int | None, *, offset: int, limit: int):
    queryset = LinksJobModel.objects.order_by("-created_at")
    if job_id is not None:
        queryset = queryset.filter(pk=job_id)
    return list(queryset[offset : offset + limit].values())


async def jobs(
    request: HttpRequest, job_id: int | None = None
) -> JsonResponse | HttpResponseNotAllowed:
    """Gets a list of recent jobs with statuses and results"""
    if not request.method == "GET":
        return HttpResponseNotAllowed(permitted_methods=["GET"])
    # Validate offset, limit.
    offset, limit = request.GET.get("offset", "0"), request.GET.get("limit", "10")
    integer_validator(offset)
    integer_validator(limit)
    # Get data from db.
    res_jobs = await _get_list(job_id, offset=int(offset), limit=int(limit))
    return JsonResponse({"jobs": res_jobs})


@sync_to_async
def _create_job(url: str):
    job = LinksJobModel.objects.create(
        url=url, status=JobStatus.SUBMITTED.value, result={}
    )
    return job


async def parse(request: HttpRequest) -> JsonResponse | HttpResponseNotAllowed:
    if not request.method == "POST":
        return HttpResponseNotAllowed(permitted_methods=["GET", "POST"])
    # Validate input url.
    url = json.loads(request.body).get("url", "")
    validator = URLValidator(schemes=["http", "https"])
    validator(url)
    # Submit new parsing job task.
    job = await _create_job(url)
    # Send the task for separate execution.
    _ = job_manager.run_in_executor(job.id)
    return JsonResponse({"job_id": job.pk, "created": job.created_at})
