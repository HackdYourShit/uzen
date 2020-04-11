import asyncio
import dataclasses
import itertools
from typing import List

from loguru import logger

from uzen.models.classifications import Classification
from uzen.models.dns_records import DnsRecord
from uzen.models.matches import Match
from uzen.schemas.matches import MatchResult
from uzen.models.scripts import Script
from uzen.models.snapshots import Snapshot
from uzen.services.classifications import ClassificationBuilder
from uzen.services.dns_records import DnsRecordBuilder
from uzen.services.rule_matcher import RuleMatcher
from uzen.services.scripts import ScriptBuilder


async def create_scripts(snapshot: Snapshot, insert_to_db=True) -> List[Script]:
    logger.debug(f"Fetch scripts from {snapshot.url}")
    scripts = []
    try:
        scripts = await ScriptBuilder.build_from_snapshot(snapshot)
        if insert_to_db:
            await Script.bulk_create(scripts)
    except Exception as e:
        logger.error(
            f"Failed to process create_scrpts job. URL: {snapshot.url} / Error: {e}"
        )

    return scripts


async def create_dns_records(snapshot: Snapshot, insert_to_db=True) -> List[DnsRecord]:
    logger.debug(f"Fetch DNS records from {snapshot.hostname}")
    records = []
    try:
        records = DnsRecordBuilder.build_from_snapshot(snapshot)
        if insert_to_db:
            await DnsRecord.bulk_create(records)
    except Exception as e:
        logger.error(
            f"Failed to process create_dns_records job. URL: {snapshot.url} / Error: {e}"
        )

    return records


async def create_classifications(
    snapshot: Snapshot, insert_to_db=True
) -> List[Classification]:
    logger.debug(f"Fetch classifications of {snapshot.url}")
    classifications = []
    try:
        classifications = ClassificationBuilder.build_from_snapshot(snapshot)
        if insert_to_db:
            await Classification.bulk_create(classifications)
    except Exception as e:
        logger.error(
            f"Failed to process create_classifications job. URL: {snapshot.url} / Error: {e}"
        )

    return classifications


@dataclasses.dataclass
class Results:
    classifications: List[Classification]
    dns_records: List[DnsRecord]
    scripts: List[Script]


async def run_enrhichment_jobs(snapshot, insert_to_db=True) -> Results:
    jobs = [
        create_classifications(snapshot, insert_to_db),
        create_dns_records(snapshot, insert_to_db),
        create_scripts(snapshot, insert_to_db),
    ]
    completed, pending = await asyncio.wait(jobs)
    results = list(itertools.chain(*[t.result() for t in completed]))

    scripts = []
    classifications = []
    dns_records = []
    for result in results:
        if isinstance(result, Classification):
            classifications.append(result)
        elif isinstance(result, DnsRecord):
            dns_records.append(result)
        elif isinstance(result, Script):
            scripts.append(result)

    return Results(
        classifications=classifications, dns_records=dns_records, scripts=scripts
    )


async def run_matching_job(snapshot):
    logger.debug("Starting matching job...")

    snapshot_ = await Snapshot.get(id=snapshot.id)
    matcher = RuleMatcher(snapshot_)
    results: List[MatchResult] = await matcher.scan()

    matches = [
        Match(
            snapshot_id=snapshot.id,
            rule_id=result.rule_id,
            matches=[match.dict() for match in result.matches],
        )
        for result in results
    ]
    await Match.bulk_create(matches)

    logger.debug(f"Snapshot {snapshot.id} matches with {len(matches)} rule(s)")
    logger.debug("Matching job is finished")
