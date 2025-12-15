import base64
import hashlib
import uuid
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import qrcode
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.http import HttpResponse

from django.core.files.uploadedfile import UploadedFile
from apps.documents.models import SignedDocument
from apps.core.models import AuditLog

class VerificationService:
    @staticmethod
    def generate_certificate(document: SignedDocument, verification_id: uuid.UUID) -> HttpResponse:
        """Generates a PDF verification certificate for an authentic document."""
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Header
        p.setFont("Helvetica-Bold", 18)
        p.drawCentredString(width / 2.0, height - inch, "Certificat de Vérification")

        # Document Info
        p.setFont("Helvetica", 12)
        text = p.beginText(inch, height - 2 * inch)
        text.textLine(f"Document Hash: {document.document_hash}")
        text.textLine(f"Institution: {document.institution.name}")
        text.textLine(f"Date de Signature: {document.signed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        text.textLine(f"Date de Vérification: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        text.textLine(f"ID de Vérification: {verification_id}")
        p.drawText(text)

        # Result
        p.setFont("Helvetica-Bold", 16)
        p.setFillColorRGB(0, 0.5, 0) # Green
        p.drawCentredString(width / 2.0, height - 3.5 * inch, "AUTHENTIQUE ✓")

        # QR Code
        qr_data = f"https://letscheck.cm/verify?hash={document.document_hash}"
        qr_img = qrcode.make(qr_data)
        p.drawInlineImage(qr_img, width / 2.0 - inch, height - 5.5 * inch, width=2*inch, height=2*inch)

        # Footer
        p.setFont("Helvetica-Oblique", 9)
        p.drawCentredString(width / 2.0, inch, "Ce certificat a été généré automatiquement par Let's Check.")

        p.showPage()
        p.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificat-{document.document_hash[:10]}.pdf"'
        return response

    @staticmethod
    def verify_document(document_hash: str, ip_address: str) -> dict:
        """
        Verifies the authenticity of a document based on its hash.
        Logs the verification attempt in the audit log.
        """
        try:
            document = SignedDocument.objects.select_related("institution", "key").get(
                document_hash=document_hash
            )
        except SignedDocument.DoesNotExist:
            AuditLog.objects.create(
                action_type='VERIFY',
                resource_type='DOCUMENT',
                details=f"Verification attempt for non-existent hash: {document_hash}",
                ip_address=ip_address,
                success=False,
            )
            return {"result": "NOT_FOUND", "verification_id": uuid.uuid4()}

        # Check document and key statuses
        if document.status == "REVOKED":
            return {
                "result": "REVOKED",
                "document": document,
                "revoked_at": document.revoked_at,
                "reason": document.revocation_reason,
                "verification_id": uuid.uuid4(),
            }

        if document.key.status != "ACTIVE":
            return {
                "result": "KEY_EXPIRED",
                "document": document,
                "verification_id": uuid.uuid4(),
            }

        # Perform cryptographic verification
        try:
            public_key = serialization.load_pem_public_key(
                document.key.public_key.encode()
            )
            public_key.verify(
                base64.b64decode(document.signature),
                document_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            result = "AUTHENTIC"
            success = True
        except (InvalidSignature, ValueError):
            result = "INVALID_SIGNATURE"
            success = False
        except Exception:
            # Catch other potential crypto errors
            result = "VERIFICATION_ERROR"
            success = False

        # Create an audit log for the attempt
        AuditLog.objects.create(
            action_type='VERIFY',
            resource_type='DOCUMENT',
            resource_id=str(document.id),
            ip_address=ip_address,
            success=success,
            details=f"Verification result: {result}"
        )

        return {
            "result": result,
            "document": document,
            "verification_id": uuid.uuid4(),
        }
