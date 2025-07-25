import random
import string

from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


def get_tokens_for_user(user: User) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def generate_invite_code() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))
