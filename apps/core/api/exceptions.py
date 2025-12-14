
class BaseAPIException(Exception):
    """Classe de base pour les exceptions de l'API."""
    status_code = 500
    default_detail = "Une erreur interne est survenue."

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail