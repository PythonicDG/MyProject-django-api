from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'status_code': response.status_code,
            'error': response.status_text,
            'details': response.data,
        }
    else:
        # Handle unexpected exceptions (like 500 errors)
        return Response({
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'error': 'Internal Server Error',
            'details': str(exc),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
