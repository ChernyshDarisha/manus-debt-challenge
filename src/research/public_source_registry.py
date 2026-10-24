"""Internal public-source indicator registry for MANUS+ Debt Challenge Automation.

This module stores source-grounded status records. It does not scrape personal data,
make legal determinations, assign political scores, or publish allegations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha3_256
from typing import Any, Mapping
from urllib.parse import urlparse


class EvidenceLevel(StrEnum):
    """Strength of documentary support for an indicator record."""

    E1 = "E1"  # Primary official legal or administrative record.
    E2 = "E2"  # Official procedural or administrative notice.
    E3 = "E3"  # Independent contextual reporting; not sufficient for publication alone.
    E4 = "E4"  # Unverified signal; excluded from profiles and conclusions.


class PublicationDecision(StrEnum):
    """Permitted workflow states for a research record."""

    PUBLISH = "publish"
    INTERNAL_REVIEW = "internal_review"
    EXCLUDE = "exclude"


APPROVED_INDICATORS = frozenset(
    {
        "sanctions",
        "court_status",
        "corruption_registry",
        "declaration_disclosure",
        "official_vote",
        "official_decision",
        "regulatory_impact",
        "official_procedural_notice",
    }
)

HIGH_RISK_LABELS = (
    "зрадник",
    "державна зрада",
    "корупціонер",
    "колаборант",
    "агент держави-агресора",
    "сприяє агресору",
    "перешкоджає бізнесу",
    "блокує бізнес",
)


@dataclass(frozen=True)
class ValidationResult:
    """Validation findings; success never establishes a claim's truthfulness."""

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def accepted(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class SourceArtifact:
    """Provenance metadata for a locally retained source extract."""

    url: str
    publisher: str
    document_date: str
    retrieved_at: str
    copy_sha3_256: str
    source_access_status: str = "verified"

    @classmethod
    def from_bytes(
        cls,
        *,
        url: str,
        publisher: str,
        document_date: str,
        extract: bytes,
        source_access_status: str = "verified",
    ) -> "SourceArtifact":
        return cls(
            url=url,
            publisher=publisher,
            document_date=document_date,
            retrieved_at=datetime.now(UTC).isoformat(),
            copy_sha3_256=f"sha3-256:{sha3_256(extract).hexdigest()}",
            source_access_status=source_access_status,
        )


@dataclass
class PublicSourceRiskRecord:
    """A neutral, status-specific indicator record awaiting review."""

    record_id: str
    subject: dict[str, str]
    public_role: dict[str, str]
    indicator_type: str
    status: str
    evidence_level: EvidenceLevel
    source: SourceArtifact
    excerpt: str
    publication_decision: PublicationDecision = PublicationDecision.INTERNAL_REVIEW
    context: dict[str, str] = field(default_factory=dict)
    public_summary: str = ""
    prepared_by: str = ""
    reviewed_by: str = ""
    reviewed_at: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "subject": self.subject,
            "public_role": self.public_role,
            "indicator_type": self.indicator_type,
            "status": self.status,
            "evidence_level": self.evidence_level.value,
            "source": {
                "url": self.source.url,
                "publisher": self.source.publisher,
                "document_date": self.source.document_date,
                "retrieved_at": self.source.retrieved_at,
                "copy_sha3_256": self.source.copy_sha3_256,
                "source_access_status": self.source.source_access_status,
            },
            "excerpt": self.excerpt,
            "context": self.context,
            "review": {
                "prepared_by": self.prepared_by,
                "reviewed_by": self.reviewed_by,
                "reviewed_at": self.reviewed_at,
            },
            "publication": {
                "decision": self.publication_decision.value,
                "public_summary": self.public_summary,
            },
        }


class PublicSourceRecordValidator:
    """Apply conservative workflow controls to a proposed indicator record."""

    def validate(self, record: PublicSourceRiskRecord) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        if record.indicator_type not in APPROVED_INDICATORS:
            errors.append("indicator_type is not approved for this registry.")
        if not record.record_id.startswith("UA-PSR-"):
            errors.append("record_id must use the UA-PSR- prefix.")
        if not record.subject.get("display_name") or not record.subject.get("public_identifier"):
            errors.append("subject must include a public display name and a public identifier.")
        if not all(record.public_role.get(key) for key in ("title", "body", "jurisdiction", "term")):
            errors.append("public_role must include title, body, jurisdiction, and term.")
        if not self._is_https_url(record.source.url):
            errors.append("source URL must be a concrete HTTPS URL.")
        if len(record.excerpt.strip()) < 20:
            errors.append("excerpt must provide source-grounded context of at least 20 characters.")
        if record.source.source_access_status not in {
            "verified",
            "source_currently_unavailable",
            "not_verified",
        }:
            errors.append("source_access_status is invalid.")

        if record.evidence_level is EvidenceLevel.E4:
            if record.publication_decision is not PublicationDecision.EXCLUDE:
                errors.append("E4 material must be excluded from conclusions and publication.")
        if record.evidence_level is EvidenceLevel.E3:
            if record.publication_decision is PublicationDecision.PUBLISH:
                errors.append("E3-only material cannot be published as a personalized risk fact.")
        if record.evidence_level in {EvidenceLevel.E1, EvidenceLevel.E2}:
            if record.publication_decision is PublicationDecision.PUBLISH and not record.reviewed_by:
                errors.append("Publishing E1/E2 material requires a second reviewer.")

        wording = " ".join(
            [record.status, record.excerpt, record.public_summary, *record.context.values()]
        ).lower()
        labels = [label for label in HIGH_RISK_LABELS if label in wording]
        if labels:
            errors.append(
                "High-risk labels require replacement with a source-attributed, status-specific description: "
                + ", ".join(labels)
            )

        if not record.context.get("updates_or_appeals"):
            warnings.append("Record the absence or presence of appeals, corrections, and later updates.")
        if record.source.source_access_status != "verified":
            warnings.append("Do not infer a negative result from an unavailable or unverified source.")

        return ValidationResult(tuple(errors), tuple(warnings))

    @staticmethod
    def _is_https_url(value: str) -> bool:
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.netloc)


def create_internal_record(
    *,
    record_id: str,
    subject: Mapping[str, str],
    public_role: Mapping[str, str],
    indicator_type: str,
    status: str,
    evidence_level: EvidenceLevel,
    source: SourceArtifact,
    excerpt: str,
    prepared_by: str,
) -> PublicSourceRiskRecord:
    """Create a new record in the safe default `internal_review` state."""

    return PublicSourceRiskRecord(
        record_id=record_id,
        subject=dict(subject),
        public_role=dict(public_role),
        indicator_type=indicator_type,
        status=status,
        evidence_level=evidence_level,
        source=source,
        excerpt=excerpt,
        prepared_by=prepared_by,
    )
