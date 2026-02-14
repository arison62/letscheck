from ninja import Schema
from datetime import datetime
from typing import Optional, List
import uuid

class InstitutionSchema(Schema):
    name: str
    logo_url: Optional[str] = None
    country_code: str
    type: str

class DocumentInfoSchema(Schema):
    institution: InstitutionSchema
    signed_at: datetime
    file_type: str
    key_algorithm: str
    status: str

class VerifyHashSchema(Schema):
    document_hash: str
    method: str

class VerificationResultSchema(Schema):
    result: str
    document_hash: str
    document: Optional[DocumentInfoSchema] = None
    certificate_url: Optional[str] = None
    verification_id: uuid.UUID

class ReportCreateSchema(Schema):
    document_hash: str
    report_type: str
    reason: str
    reporter_email: Optional[str] = None
    reporter_name: Optional[str] = None

class ReportSchema(Schema):
    id: uuid.UUID
    document_hash: str
    report_type: str
    reason: str
    status: str
    created_at: datetime

class PublicInstitutionSchema(Schema):
    name: str
    slug: str
    logo_url: Optional[str] = None
    country_code: str
    type: str

class PublicStatsSchema(Schema):
    total_verifications: int
    total_institutions: int
    total_documents_signed: int
