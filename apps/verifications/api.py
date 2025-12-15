import uuid
from ninja import Router, Query
from ninja.pagination import paginate, PageNumberPagination
from typing import List

from .schemas import (
    VerifyHashSchema,
    VerificationResultSchema,
    ReportCreateSchema,
    ReportSchema,
    PublicInstitutionSchema,
    PublicStatsSchema,
    DocumentInfoSchema,
    InstitutionSchema,
)
from .services import VerificationService
from .tasks import send_report_notification
from apps.documents.models import SignedDocument
from apps.institutions.models import Institution
from apps.verifications.models import SuspiciousReport
from django.shortcuts import get_object_or_404

router = Router()

@router.post("/verify/hash", response=VerificationResultSchema)
def verify_hash_endpoint(request, payload: VerifyHashSchema):
    """
    Verifies the authenticity of a document given its hash.
    """
    client_ip = request.META.get("REMOTE_ADDR", "127.0.0.1")
    result_data = VerificationService.verify_document(
        document_hash=payload.document_hash, ip_address=client_ip
    )

    response_data = {
        "result": result_data["result"],
        "verification_id": result_data["verification_id"],
        "document_hash": payload.document_hash,
    }

    if result_data.get("document"):
        doc = result_data["document"]
        document_info = DocumentInfoSchema(
            institution=InstitutionSchema.from_orm(doc.institution),
            signed_at=doc.signed_at,
            file_type="Unknown",  # This can be improved later
            key_algorithm=doc.key.algorithm,
            status=doc.status,
        )
        response_data["document"] = document_info
        if result_data["result"] == "AUTHENTIC":
            response_data["certificate_url"] = f"/api/v1/verifications/verify/{doc.id}/certificate"

    return VerificationResultSchema(**response_data)


@router.get("/verify/{doc_hash}", response=DocumentInfoSchema)
def get_document_info(request, doc_hash: str):
    """
    Retrieves public information about a signed document by its hash.
    """
    doc = get_object_or_404(SignedDocument.objects.select_related('institution', 'key'), document_hash=doc_hash)
    return DocumentInfoSchema.from_orm(doc)


@router.get("/verify/{document_id}/certificate")
def get_verification_certificate(request, document_id: uuid.UUID):
    """
    Generates and returns a PDF certificate for an authentic document.
    """
    doc = get_object_or_404(SignedDocument, id=document_id, status='AUTHENTIC')
    verification_id = uuid.uuid4()  # A new ID for this specific verification event
    return VerificationService.generate_certificate(doc, verification_id)


@router.post("/reports", response=ReportSchema)
def create_report(request, payload: ReportCreateSchema):
    """
    Creates a new report for a suspicious document.
    """
    report = SuspiciousReport.objects.create(**payload.dict())
    send_report_notification.delay(report.id)
    return report


@router.get("/reports/{report_id}", response=ReportSchema)
def get_report_status(request, report_id: uuid.UUID):
    """
    Retrieves the status of a specific report.
    """
    return get_object_or_404(SuspiciousReport, id=report_id)


@router.get("/institutions", response=List[PublicInstitutionSchema])
@paginate(PageNumberPagination, page_size=50)
def list_institutions(request, status: str = 'ACTIVE', type: str = None, country_code: str = None, search: str = None):
    """
    Lists active and public institutions with filtering and pagination.
    """
    qs = Institution.objects.filter(status=status)
    if type:
        qs = qs.filter(type=type)
    if country_code:
        qs = qs.filter(country_code__iexact=country_code)
    if search:
        qs = qs.filter(name__icontains=search)
    return qs


@router.get("/institutions/{slug}", response=PublicInstitutionSchema)
def get_institution_details(request, slug: str):
    """
    Retrieves public details for a single institution.
    """
    return get_object_or_404(Institution, slug=slug, status='ACTIVE')


from apps.core.models import AuditLog

@router.get("/stats/public", response=PublicStatsSchema)
def get_public_stats(request):
    """
    Retrieves aggregated public statistics.
    """
    stats = {
        "total_verifications": AuditLog.objects.filter(action_type='VERIFY').count(),
        "total_institutions": Institution.objects.filter(status='ACTIVE').count(),
        "total_documents_signed": SignedDocument.objects.count(),
    }
    return stats
