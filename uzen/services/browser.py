from typing import Optional, cast

import pyppeteer
from pyppeteer import connect, launch
from pyppeteer.errors import PyppeteerError

from uzen.core import settings
from uzen.models.screenshots import Screenshot
from uzen.models.snapshots import Snapshot
from uzen.schemas.utils import SnapshotResult
from uzen.services.certificate import Certificate
from uzen.services.utils import (
    calculate_sha256,
    get_asn_by_ip_address,
    get_hostname_from_url,
    get_ip_address_by_hostname,
)
from uzen.services.whois import Whois
from uzen.utils.patch_pyppeteer import patch_pyppeteer

# apply a patch to download chromium
patch_pyppeteer()


async def launch_browser(
    ignore_https_errors: bool = False,
) -> pyppeteer.browser.Browser:
    if settings.BROWSER_WS_ENDPOINT != "":
        return await connect(
            browserWSEndpoint=settings.BROWSER_WS_ENDPOINT,
            headless=True,
            ignoreHTTPSErrors=ignore_https_errors,
            args=["--no-sandbox"],
        )

    return await launch(
        headless=True, ignoreHTTPSErrors=ignore_https_errors, args=["--no-sandbox"],
    )


class Browser:
    @staticmethod
    async def take_snapshot(
        url: str,
        accept_language: Optional[str] = None,
        ignore_https_errors: bool = False,
        referer: Optional[str] = None,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
    ) -> SnapshotResult:
        """Take a snapshot of a website by puppeteer

        Arguments:
            url {str} -- A URL of a website

        Keyword Arguments:
            user_agent {Optional[str]} -- User agent to use (default: {None})
            timeout {Optional[int]} -- Maximum time to wait for in seconds (default: {None})
            ignore_https_errors {bool} -- Whether to ignore HTTPS errors (default: {False})

        Returns:
            Snapshot -- Snapshot ORM instance
        """
        submitted_url: str = url
        try:
            browser = await launch_browser(ignore_https_errors)
            page = await browser.newPage()

            if user_agent is not None:
                await page.setUserAgent(user_agent)

            referer = referer or ""
            headers = {"Referer": referer}
            if accept_language is not None:
                headers["Accept-Language"] = accept_language
            await page.setExtraHTTPHeaders(headers)

            # default timeout = 30 seconds
            timeout = timeout or 30 * 1000
            res = await page.goto(url, timeout=timeout)

            request = {
                "accept_language": accept_language,
                "browser": await browser.version(),
                "ignore_https_errors": ignore_https_errors,
                "referer": referer,
                "timeout": timeout,
                "user_agent": user_agent or await browser.userAgent(),
            }

            url = page.url
            status = res.status
            screenshot_data = await page.screenshot(encoding="base64")
            body = await page.content()
            sha256 = calculate_sha256(body)
            headers = res.headers
        except PyppeteerError as e:
            await browser.close()
            raise (e)
        else:
            await browser.close()

        server = headers.get("server")
        content_type = headers.get("content-type")
        content_length = headers.get("content-length")

        hostname = cast(str, get_hostname_from_url(url))
        certificate = Certificate.load_and_dump_from_url(url)
        ip_address = cast(str, get_ip_address_by_hostname(hostname))
        asn = await get_asn_by_ip_address(ip_address) or ""
        whois = Whois.whois(hostname)

        snapshot = Snapshot(
            url=url,
            submitted_url=submitted_url,
            status=status,
            body=body,
            sha256=sha256,
            headers=headers,
            hostname=hostname,
            ip_address=ip_address,
            asn=asn,
            server=server,
            content_length=content_length,
            content_type=content_type,
            whois=whois,
            certificate=certificate,
            request=request,
        )
        screenshot = Screenshot(data=screenshot_data)

        return SnapshotResult(screenshot=screenshot, snapshot=snapshot)
