from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.core import signing
from apps.core.models import User

def verify_account(request: HttpRequest, token: str) -> HttpResponse:
    """
    Verifies a user's account using a signed token.

    Args:
        request: The Django HttpRequest object.
        token: The signed token from the verification URL.

    Returns:
        An HttpResponse indicating success or failure.
    """
    try:
        user_id = signing.loads(token, salt='user-verification', max_age=86400)  # Token valid for 24 hours
    except signing.SignatureExpired:
        return HttpResponseBadRequest("Le lien de vérification a expiré.")
    except signing.BadSignature:
        return HttpResponseBadRequest("Lien de vérification invalide.")

    try:
        user = User.objects.get(id=user_id, status=User.Status.PENDING)
    except User.DoesNotExist:
        return HttpResponseNotFound("Utilisateur non trouvé ou déjà vérifié.")

    user.status = User.Status.ACTIVE
    user.email_verified = True
    user.save()

    return HttpResponse("Votre compte a été vérifié avec succès !")
