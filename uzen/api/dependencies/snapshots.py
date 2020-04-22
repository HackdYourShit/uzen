from datetime import date, datetime
from typing import Optional, Union

from fastapi import Query


class SearchFilters:
    def __init__(
        self,
        asn: Optional[str] = Query(None, title="AS number"),
        content_type: Optional[str] = Query(None, title="Content type"),
        hostname: Optional[str] = Query(None, title="Hostname"),
        ip_address: Optional[str] = Query(None, title="IP address"),
        server: Optional[str] = Query(None, title="Server"),
        sha256: Optional[str] = Query(None, title="SHA256"),
        status: Optional[int] = Query(None, title="Status"),
        url: Optional[str] = Query(None, title="URL"),
        from_at: Optional[Union[datetime, date]] = Query(
            None, title="From at", description="Datetime or date in ISO 8601 format"
        ),
        to_at: Optional[Union[datetime, date]] = Query(
            None, title="To at", description="Datetime or date in ISO 8601 format"
        ),
    ):
        self.asn = asn
        self.content_type = content_type
        self.hostname = hostname
        self.ip_address = ip_address
        self.server = server
        self.sha256 = sha256
        self.status = status
        self.url = url
        self.from_at = from_at
        self.to_at = to_at
