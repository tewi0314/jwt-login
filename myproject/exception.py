from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken

def custom_exception_handler(exc, context):
    if isinstance(exc, NotAuthenticated):
        return Response({
            "error": {
                "code": "TOKEN_NOT_FOUND",
                "message": "토큰이 없습니다."
            }
        }, status=status.HTTP_401_UNAUTHORIZED)

    elif isinstance(exc, AuthenticationFailed):
        return Response({
            "error": {
                "code": "INVALID_TOKEN",
                "message": "토큰이 유효하지 않습니다."
            }
        }, status=status.HTTP_401_UNAUTHORIZED)

    elif isinstance(exc, InvalidToken):
        return Response({
            "error": {
                "code": "INVALID_TOKEN",
                "message": "토큰이 유효하지 않습니다."
            }
        }, status=status.HTTP_401_UNAUTHORIZED)

    return exception_handler(exc, context)
