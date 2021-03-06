from __future__ import annotations

from typing import Any, List, Optional, Union
from uuid import UUID

from tortoise import fields
from tortoise.exceptions import NoValuesFetched

from uzen.models.base import AbstractBaseModel
from uzen.models.mixins import TimestampMixin
from uzen.schemas.classifications import BaseClassification, Classification
from uzen.schemas.dns_records import BaseDnsRecord, DnsRecord
from uzen.schemas.rules import Rule
from uzen.schemas.screenshots import BaseScreenshot, Screenshot
from uzen.schemas.scripts import BaseScript, Script
from uzen.schemas.snapshots import BaseSnapshot
from uzen.schemas.snapshots import Snapshot as SnapshotModel


class Snapshot(TimestampMixin, AbstractBaseModel):
    """An ORM class for snapshots table"""

    url = fields.TextField()
    submitted_url = fields.TextField()
    status = fields.IntField()
    hostname = fields.TextField()
    ip_address = fields.CharField(max_length=255)
    asn = fields.TextField()
    server = fields.TextField(null=True)
    content_type = fields.TextField(null=True)
    content_length = fields.IntField(null=True)
    body = fields.TextField()
    sha256 = fields.CharField(max_length=64)
    headers = fields.JSONField()
    whois = fields.TextField(null=True)
    certificate = fields.TextField(null=True)
    request = fields.JSONField()
    processing = fields.BooleanField(default=True)

    _screenshot: fields.OneToOneRelation["Screenshot"]

    _scripts: fields.ReverseRelation["Script"]
    _dns_records: fields.ReverseRelation["DnsRecord"]
    _classifications: fields.ReverseRelation["Classification"]

    _rules: fields.ManyToManyRelation["Rule"] = fields.ManyToManyField(
        "models.Rule",
        related_name="_snapshots",
        through="matches",
        forward_key="rule_id",
        backward_key="snapshot_id",
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.screenshot_: Optional[Union[BaseScreenshot, Screenshot]] = None

        self.scripts_: Optional[List[Union[Script, BaseScript]]] = None
        self.dns_records_: Optional[List[Union[DnsRecord, BaseDnsRecord]]] = None
        self.classifications_: Optional[
            List[Union[Classification, BaseClassification]]
        ] = None

        self.rules_: Optional[List[Rule]] = None

    @property
    def screenshot(self) -> Optional[Union[BaseScreenshot, Screenshot]]:
        if hasattr(self, "screenshot_") and self.screenshot_ is not None:
            return self.screenshot_

        if self._screenshot is not None:
            return self._screenshot.to_model()

        return None

    @screenshot.setter
    def screenshot(self, screenshot: Union[BaseScreenshot, Screenshot]):
        self.screenshot_ = screenshot

    @property
    def rules(self) -> List[Rule]:
        try:
            return [rule.to_model() for rule in self._rules]
        except NoValuesFetched:
            return []

    @property
    def scripts(self) -> List[Union[Script, BaseScript]]:
        if hasattr(self, "scripts_") and self.scripts_ is not None:
            return self.scripts_

        try:
            return [script.to_model() for script in self._scripts]
        except NoValuesFetched:
            return []

    @scripts.setter
    def scripts(self, scripts: List[Union[Script, BaseScript]]):
        self.scripts_ = scripts

    @property
    def dns_records(self) -> List[Union[DnsRecord, BaseDnsRecord]]:
        if hasattr(self, "dns_records_") and self.dns_records_ is not None:
            return self.dns_records_

        try:
            return [record.to_model() for record in self._dns_records]
        except NoValuesFetched:
            return []

    @dns_records.setter
    def dns_records(self, dns_records: List[Union[DnsRecord, BaseDnsRecord]]):
        self.dns_records_ = dns_records

    @property
    def classifications(self) -> List[Union[Classification, BaseClassification]]:
        if hasattr(self, "classifications_") and self.classifications_ is not None:
            return self.classifications_

        try:
            return [
                classification.to_model() for classification in self._classifications
            ]
        except NoValuesFetched:
            return []

    @classifications.setter
    def classifications(
        self, classifications: List[Union[Classification, BaseClassification]]
    ):
        self.classifications_ = classifications

    def to_model(self) -> Union[BaseSnapshot, SnapshotModel]:
        if self.created_at is not None:
            return SnapshotModel.from_orm(self)
        return BaseSnapshot.from_orm(self)

    def to_dict(self) -> dict:
        model = self.to_model()
        return model.dict()

    @classmethod
    async def get_by_id(cls, id_: UUID, include_screenshot: bool = False) -> Snapshot:
        if include_screenshot:
            return await cls.get(id=id_).prefetch_related(
                "_screenshot", "_scripts", "_dns_records", "_classifications", "_rules"
            )
        return await cls.get(id=id_).prefetch_related(
            "_scripts", "_dns_records", "_classifications", "_rules"
        )

    @classmethod
    async def find_by_ip_address(cls, ip_address: str, size=20) -> List[Snapshot]:
        return await cls.filter(ip_address=ip_address).limit(size)

    @classmethod
    async def find_by_hostname(cls, hostname: str, size=20) -> List[Snapshot]:
        return await cls.filter(hostname=hostname).limit(size)

    class Meta:
        table = "snapshots"
        ordering = ["-created_at"]
