import logging
import uuid
from typing import Optional

from apps.core.models import AuditLog, User

# Configure a logger for the service
logger = logging.getLogger(__name__)

class AuditService:
    """
    Service pour la journalisation des actions critiques dans le système.
    Chaque méthode correspond à un type d'événement spécifique et crée un enregistrement AuditLog.
    """

    @classmethod
    def log_login(cls, user: User, ip_address: str, success: bool, user_agent: Optional[str] = None):
        """
        Enregistre une tentative de connexion.

        Args:
            user (User): L'utilisateur qui tente de se connecter.
            ip_address (str): L'adresse IP de la requête.
            success (bool): True si la connexion a réussi, False sinon.
            user_agent (Optional[str]): L'user-agent du client.
        """
        try:
            AuditLog.objects.create(
                user=user,
                action_type=AuditLog.ActionType.LOGIN if success else AuditLog.ActionType.LOGIN_FAILED,
                resource_type=AuditLog.ResourceType.USER,
                resource_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent or '',
                success=success,
                details={'username': user.username}
            )
        except Exception as e:
            logger.error(f"Failed to log login event for user {user.username}: {e}")

    @classmethod
    def log_document_sign(cls, user: User, document_id: uuid.UUID, original_filename: str, ip_address: str, user_agent: Optional[str] = None):
        """
        Enregistre la signature d'un document.

        Args:
            user (User): L'utilisateur qui a signé le document.
            document_id (uuid.UUID): L'ID du document signé.
            original_filename (str): Le nom original du fichier.
            ip_address (str): L'adresse IP de la requête.
            user_agent (Optional[str]): L'user-agent du client.
        """
        try:
            AuditLog.objects.create(
                user=user,
                action_type=AuditLog.ActionType.SIGN,
                resource_type=AuditLog.ResourceType.DOCUMENT,
                resource_id=document_id,
                ip_address=ip_address,
                user_agent=user_agent or '',
                success=True,
                details={'document_id': str(document_id), 'filename': original_filename}
            )
        except Exception as e:
            logger.error(f"Failed to log document sign event for document {document_id}: {e}")

    @classmethod
    def log_document_verify(cls, document_hash: str, ip_address: str, result: str, user_agent: Optional[str] = None, document_id: Optional[uuid.UUID] = None):
        """
        Enregistre une tentative de vérification de document.

        Args:
            document_hash (str): Le hash du document vérifié.
            ip_address (str): L'adresse IP du vérificateur.
            result (str): Le résultat de la vérification (ex: 'AUTHENTIC').
            user_agent (Optional[str]): L'user-agent du client.
            document_id (Optional[uuid.UUID]): L'ID du document si trouvé.
        """
        success = result == 'AUTHENTIC'
        try:
            AuditLog.objects.create(
                user=None,  # La vérification est souvent publique
                action_type=AuditLog.ActionType.VERIFY,
                resource_type=AuditLog.ResourceType.DOCUMENT,
                resource_id=document_id,
                ip_address=ip_address,
                user_agent=user_agent or '',
                success=success,
                details={'document_hash': document_hash, 'result': result}
            )
        except Exception as e:
            logger.error(f"Failed to log document verify event for hash {document_hash}: {e}")

    @classmethod
    def log_key_created(cls, user: User, key_id: uuid.UUID, key_fingerprint: str, key_algorithm: str, ip_address: str, user_agent: Optional[str] = None):
        """
        Enregistre la création d'une nouvelle clé cryptographique.

        Args:
            user (User): L'utilisateur (admin ou institutionnel) qui a créé la clé.
            key_id (uuid.UUID): L'ID de la clé cryptographique.
            key_fingerprint (str): L'empreinte de la clé.
            key_algorithm (str): L'algorithme de la clé.
            ip_address (str): L'adresse IP de la requête.
            user_agent (Optional[str]): L'user-agent du client.
        """
        try:
            AuditLog.objects.create(
                user=user,
                action_type=AuditLog.ActionType.KEY_CREATED,
                resource_type=AuditLog.ResourceType.KEY,
                resource_id=key_id,
                ip_address=ip_address,
                user_agent=user_agent or '',
                success=True,
                details={'key_fingerprint': key_fingerprint, 'algorithm': key_algorithm}
            )
        except Exception as e:
            logger.error(f"Failed to log key created event for key {key_id}: {e}")

    @classmethod
    def log_institution_validated(cls, admin_user: User, institution_id: uuid.UUID, institution_name: str, ip_address: str, user_agent: Optional[str] = None):
        """
        Enregistre la validation d'une institution par un administrateur.

        Args:
            admin_user (User): L'administrateur qui a validé l'institution.
            institution_id (uuid.UUID): L'ID de l'institution validée.
            institution_name (str): Le nom de l'institution.
            ip_address (str): L'adresse IP de la requête.
            user_agent (Optional[str]): L'user-agent du client.
        """
        try:
            AuditLog.objects.create(
                user=admin_user,
                action_type=AuditLog.ActionType.INSTITUTION_VALIDATED,
                resource_type=AuditLog.ResourceType.INSTITUTION,
                resource_id=institution_id,
                ip_address=ip_address,
                user_agent=user_agent or '',
                success=True,
                details={'institution_name': institution_name, 'validated_by': admin_user.username}
            )
        except Exception as e:
            logger.error(f"Failed to log institution validated event for institution {institution_id}: {e}")
