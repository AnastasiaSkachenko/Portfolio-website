from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()
class customJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Extract token from Authorization header
        authorization_header = request.headers.get('Authorization', None)
        
        if not authorization_header:
            return None  # No token, so no authentication

        # Token should be in the form of "Bearer <token>"
        parts = authorization_header.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise AuthenticationFailed('Authorization header must be in the form "Bearer <token>"')

        access_token = parts[1]

        try:
            # Validate and decode the access token
            decoded_token = AccessToken(access_token)
            user_id = decoded_token["user_id"]
            user = User.objects.get(id=user_id)
        except Exception as e:
            raise AuthenticationFailed('Invalid or expired token.')

        return (user, None)  # Return the user and None because no credentials are needed in the second element
