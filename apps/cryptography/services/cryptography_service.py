import base64
import hashlib
import logging
from datetime import datetime
from typing import Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from django.db import transaction

from apps.core.models import User
from apps.cryptography.models import CryptographicKey, KeyRotation
from apps.institutions.models import Institution

logger = logging.getLogger(__name__)

class CryptographyService:
    """
    Service for handling cryptographic operations and key management.
    """

    @staticmethod
    def validate_public_key(public_key_pem: str, algorithm: str) -> bool:
        """
        Validates the format and type of a PEM-encoded public key.
        """
        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode())
            if 'RSA' in algorithm and not isinstance(public_key, rsa.RSAPublicKey):
                return False
            if 'ECDSA' in algorithm and not isinstance(public_key, ec.EllipticCurvePublicKey):
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def calculate_fingerprint(public_key_pem: str) -> str:
        """
        Calculates the SHA-256 fingerprint of a public key.
        """
        hasher = hashlib.sha256()
        hasher.update(public_key_pem.encode())
        return hasher.hexdigest()

    @staticmethod
    def verify_signature(public_key_pem: str, message: bytes, signature: bytes) -> bool:
        """
        Verifies a signature against a message using the public key.
        """
        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode())
            signature = base64.b64decode(signature)

            if isinstance(public_key, rsa.RSAPublicKey):
                public_key.verify(
                    signature,
                    message,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            elif isinstance(public_key, ec.EllipticCurvePublicKey):
                public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            else:
                return False
            return True
        except (InvalidSignature, ValueError):
            return False

    @classmethod
    @transaction.atomic
    def register_key_metadata(
        cls,
        institution: Institution,
        public_key_pem: str,
        algorithm: str,
        expires_at: datetime
    ) -> Optional[CryptographicKey]:
        """
        Registers a new cryptographic key for an institution.
        """
        if not cls.validate_public_key(public_key_pem, algorithm):
            logger.error(f"Invalid public key provided for institution {institution.id}")
            return None

        fingerprint = cls.calculate_fingerprint(public_key_pem)
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        key_size = public_key.key_size

        try:
            key = CryptographicKey.objects.create(
                institution=institution,
                public_key=public_key_pem,
                fingerprint=fingerprint,
                algorithm=algorithm,
                key_size=key_size,
                expires_at=expires_at,
            )
            return key
        except Exception as e:
            logger.error(f"Failed to register key for institution {institution.id}: {e}")
            return None

    @classmethod
    @transaction.atomic
    def rotate_key(
        cls,
        old_key: CryptographicKey,
        new_public_key_pem: str,
        reason: str,
        user: User
    ) -> Optional[CryptographicKey]:
        """
        Rotates an existing cryptographic key.
        """
        if not cls.validate_public_key(new_public_key_pem, old_key.algorithm):
            logger.error(f"Invalid new public key provided for rotation of key {old_key.id}")
            return None

        new_key = cls.register_key_metadata(
            institution=old_key.institution,
            public_key_pem=new_public_key_pem,
            algorithm=old_key.algorithm,
            expires_at=old_key.expires_at,  # Or a new expiration date
        )

        if new_key:
            new_key.parent_key = old_key
            new_key.save()

            old_key.status = CryptographicKey.Status.ROTATED
            old_key.save()

            KeyRotation.objects.create(
                old_key=old_key,
                new_key=new_key,
                rotation_type=KeyRotation.RotationType.MANUAL,  # Assuming manual for now
                reason=reason,
                performed_by=user,
            )
            return new_key
        return None
