from typing import Union

from tortoise import fields
from tortoise.models import Model

from uzen.schemas.screenshots import BaseScreenshot
from uzen.schemas.screenshots import Screenshot as ScreenshotModel


class Screenshot(Model):
    data = fields.TextField()

    snapshot: fields.OneToOneRelation["Snapshot"] = fields.OneToOneField(
        "models.Snapshot", related_name="_screenshot"
    )

    def to_model(self) -> Union[ScreenshotModel, BaseScreenshot]:
        if self.snapshot_id is not None:
            return ScreenshotModel.from_orm(self)

        return BaseScreenshot.from_orm(self)

    class Meta:
        table = "screenshots"