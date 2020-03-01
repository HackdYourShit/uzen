from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
    HTTP_400_BAD_REQUEST,
)

from uzen.models import Snapshot
from uzen import settings


class TestSetup(HTTPEndpoint):
    async def get(self, request) -> JSONResponse:
        if not settings.TESTING:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="cannot parse request body"
            )

        for i in range(0, 10):
            snapshot = Snapshot(
                url=f"http://example{i}.com",
                status=200,
                hostname="example.com",
                ip_address="1.1.1.1",
                asn="AS15133 MCI Communications Services, Inc. d/b/a Verizon Business",
                server="ECS (sjc/4E5D)",
                content_type="text/html; charset=UTF-8",
                content_length=1256,
                headers={},
                body="foo bar",
                sha256="fbc1a9f858ea9e177916964bd88c3d37b91a1e84412765e29950777f265c4b75",
                screenshot="yoyo",
            )
            await snapshot.save()
        return JSONResponse(
            {"snapshot": snapshot.to_dict()}, status_code=HTTP_201_CREATED
        )


class TestTearDown(HTTPEndpoint):
    async def get(self, request) -> JSONResponse:
        if not settings.TESTING:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="cannot parse request body"
            )

        await Snapshot.all().delete()
        snapshots = await Snapshot.all()
        for s in snapshots:
            print(s.id)
        return JSONResponse({}, status_code=HTTP_204_NO_CONTENT)
