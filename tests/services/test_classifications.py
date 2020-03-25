import vcr

from tests.utils import make_snapshot
from uzen.services.classifications import ClassificationBuilder


@vcr.use_cassette(
    "tests/fixtures/vcr_cassettes/classifications.yaml", filter_query_parameters=["key"]
)
def test_build_from_snapshot():
    snapshot = make_snapshot()

    classifications = ClassificationBuilder.build_from_snapshot(snapshot)
    assert len(classifications) > 0

    first = classifications[0]
    assert not first.malicious
