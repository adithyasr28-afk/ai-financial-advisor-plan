import json
from datetime import date
from pathlib import Path
from ..models import Filing
from ..http import get_json


def parse_submissions(payload: dict) -> list[Filing]:
    recent = payload["filings"]["recent"]
    cik = str(payload["cik"]).zfill(10)
    result = []
    for accession, form, filing_date, document in zip(recent["accessionNumber"], recent["form"], recent["filingDate"], recent["primaryDocument"], strict=True):
        result.append(Filing(source="sec_edgar", cik=cik, accession_number=accession, form=form, filing_date=date.fromisoformat(filing_date), primary_document=document))
    return result


def parse_fixture(path: Path) -> list[Filing]:
    return parse_submissions(json.loads(path.read_text(encoding="utf-8")))


def fetch_submissions(cik: str, user_agent: str) -> list[Filing]:
    normalized = cik.zfill(10)
    payload = get_json(f"https://data.sec.gov/submissions/CIK{normalized}.json", {"User-Agent": user_agent})
    return parse_submissions(payload)
