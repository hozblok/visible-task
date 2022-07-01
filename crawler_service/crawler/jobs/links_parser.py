import logging
from time import sleep, strftime

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.chromium.service import ChromiumService
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


class LinksSelenium:
    """Hyperlinks parser using Selenium.

    TODO: support progress and partial parsing."""

    @staticmethod
    def _collect_links(
        url: str, *, driver: webdriver.Chrome
    ) -> tuple[str | None, list[str]]:
        """Open page by url and getting all hyperlinks from `a` tags."""
        try:
            driver.get(url)
        except WebDriverException as ex:
            return str(ex), []
        else:
            # TODO: implement lock bypass (CAPTCHA, TOO MANY REQUESTS, etc) and
            # a smart algorithm that simulates user behavior
            sleep(0.1)

            href_elements = driver.find_elements(By.XPATH, ".//a[@href!='']")
            links = (el.get_attribute("href") for el in href_elements)
            # TODO: Clarify functional requirements
            filtered_links = [el for el in links if not el.startswith(f"{url}#") and el != url]
            return None, filtered_links

    @staticmethod
    def collect_links_with_nested(url: str) -> dict:
        """Parse page with Selenium and gather all hyperlinks from the page."""
        error: str | None = None
        links = []

        options = ChromiumOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = ChromiumService(
            "/usr/bin/chromedriver",
            start_error_message="%s\t" % strftime("[%Y-%m-%d %H:%M:%S]"),
        )

        with webdriver.Chrome(service=service, options=options) as driver:
            error, hrefs = LinksSelenium._collect_links(url, driver=driver)
            logger.info("URL: %s Number of links: %s", url, len(hrefs))
            for href in hrefs:
                logger.info("PARSE: %s", href)
                (nested_error, nested_hrefs) = LinksSelenium._collect_links(
                    href, driver=driver
                )
                nested_result = {"url": href, "links": nested_hrefs}
                if nested_error:
                    nested_result["error"] = nested_error
                links.append(nested_result)

        result = {"links": links}
        if error:
            result["error"] = error
        return result
