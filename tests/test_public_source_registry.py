import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.research.public_source_registry import (
    EvidenceLevel,
    PublicationDecision,
    PublicSourceRecordValidator,
    SourceArtifact,
    create_internal_record,
)


def main() -> None:
    artifact = SourceArtifact.from_bytes(
        url="https://example.gov.ua/decision/123",
        publisher="Приклад офіційного органу",
        document_date="2026-08-20",
        extract=b"Official decision excerpt retained as a local evidence artifact.",
    )
    record = create_internal_record(
        record_id="UA-PSR-2026-000001",
        subject={"display_name": "Тестовий суб’єкт", "public_identifier": "public-id-123"},
        public_role={
            "title": "Депутат",
            "body": "Тестова рада",
            "jurisdiction": "Україна",
            "term": "2025-2026",
        },
        indicator_type="official_decision",
        status="Офіційний акт оприлюднено на порталі органу.",
        evidence_level=EvidenceLevel.E1,
        source=artifact,
        excerpt="Офіційний документ містить відомості про ухвалене рішення без висновків про мотиви.",
        prepared_by="test-author",
    )

    validator = PublicSourceRecordValidator()
    accepted = validator.validate(record)
    assert accepted.accepted, accepted.errors
    assert accepted.warnings

    record.evidence_level = EvidenceLevel.E4
    record.publication_decision = PublicationDecision.INTERNAL_REVIEW
    blocked = validator.validate(record)
    assert not blocked.accepted
    assert any("E4" in message for message in blocked.errors)

    print("registry validation tests: PASS")


if __name__ == "__main__":
    main()
