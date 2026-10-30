from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

ImportEntityType = Literal["underlying", "issuer", "network", "issuer_product", "deployment"]

class ImportStrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class ImportRecordInput(ImportStrictModel):
    entity_type: ImportEntityType
    source_namespace: str = Field(min_length=1, max_length=100)
    external_id: str = Field(min_length=1, max_length=220)
    payload: dict[str, Any]

class ImportBatchCreate(ImportStrictModel):
    source: str = Field(min_length=1, max_length=100)
    source_version: str | None = Field(default=None, max_length=160)
    submitted_by: str = Field(min_length=1, max_length=160)
    records: list[ImportRecordInput] = Field(min_length=1, max_length=500)

class ImportDecision(ImportStrictModel):
    action: Literal["link_existing", "create_new", "reject"]
    reviewer: str = Field(min_length=1, max_length=160)
    evidence_ref: str | None = Field(default=None, min_length=1, max_length=500)
    target_entity_id: str | None = Field(default=None, min_length=1, max_length=36)
    note: str | None = Field(default=None, max_length=1000)
    canonical_payload_override: dict[str, Any] | None = None

class ImportCandidateRead(BaseModel):
    id: str
    candidate_entity_type: str
    candidate_entity_id: str
    match_basis: str
    confidence: float
    evidence_ref: str | None

class ImportRecordRead(BaseModel):
    id: str
    batch_id: str
    row_number: int
    entity_type: str
    source_namespace: str
    external_id: str
    payload: dict[str, Any]
    status: str
    resolution_method: str | None
    resolved_entity_type: str | None
    resolved_entity_id: str | None
    evidence_ref: str | None
    decision_note: str | None
    reviewed_by: str | None
    reviewed_at: str | None
    candidates: list[ImportCandidateRead]

class ImportBatchRead(BaseModel):
    id: str
    source: str
    source_version: str | None
    submitted_by: str
    status: str
    total_records: int
    created_at: str
    completed_at: str | None

class ImportAuditRead(BaseModel):
    id: str
    batch_id: str
    import_record_id: str | None
    actor: str
    action: str
    details: dict[str, Any]
    created_at: str


class ProviderRunCreate(ImportStrictModel):
    provider: str = Field(min_length=1, max_length=100)
    dataset: str = Field(min_length=1, max_length=120)
    source_version: str = Field(min_length=1, max_length=160)
    started_by: str = Field(min_length=1, max_length=160)
    manifest_sha256: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
    coverage: dict[str, Any] = Field(default_factory=dict)

class ProviderRunUpdate(ImportStrictModel):
    status: Literal["snapshot_ready", "awaiting_review", "partial", "completed", "failed"] | None = None
    manifest_sha256: str | None = Field(default=None, min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
    coverage: dict[str, Any] | None = None
    staged_batch_ids: list[str] | None = Field(default=None, max_length=200)
    error_summary: str | None = Field(default=None, max_length=2000)

class ProviderRunRead(BaseModel):
    id: str
    provider: str
    dataset: str
    source_version: str
    started_by: str
    status: str
    manifest_sha256: str
    coverage: dict[str, Any]
    staged_batch_ids: list[str]
    error_summary: str | None
    created_at: str
    updated_at: str
    completed_at: str | None
