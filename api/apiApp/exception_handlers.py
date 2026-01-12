from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses across the API.
    
    Args:
        exc (Exception): The raised exception
        context (dict): Context information about the exception
        
    Returns:
        Response: Standardized error response with status and message
    """
    
    # Handle Django's ObjectDoesNotExist
    if isinstance(exc, ObjectDoesNotExist):
        return Response(
            {
                'status': False,
                'message': 'The requested resource does not exist.',
                'error': 'not_found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Handle database integrity errors
    if isinstance(exc, IntegrityError):
        error_msg = str(exc)
        if 'duplicate' in error_msg.lower() or 'unique constraint' in error_msg.lower():
            return Response(
                {
                    'status': False,
                    'message': 'This record already exists. Duplicate entries are not allowed.',
                    'error': 'duplicate_entry'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                'status': False,
                'message': 'Database integrity error. Please check your data.',
                'error': 'integrity_error'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Handle authentication failures
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        error_msg = str(exc)
        
        if 'invalid_token' in error_msg or 'expired' in error_msg.lower():
            return Response(
                {
                    'status': False,
                    'message': 'Your session has expired. Please log in again.',
                    'error': 'token_expired'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        elif 'credentials were not provided' in error_msg or 'missing_token' in error_msg:
            return Response(
                {
                    'status': False,
                    'message': 'Authentication credentials were not provided.',
                    'error': 'authentication_required'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        else:
            return Response(
                {
                    'status': False,
                    'message': 'Authentication failed. Please check your credentials.',
                    'error': 'authentication_failed'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    # Handle permission denied
    if isinstance(exc, PermissionDenied):
        return Response(
            {
                'status': False,
                'message': 'You do not have permission to perform this action.',
                'error': 'permission_denied'
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Handle throttling (rate limiting)
    if isinstance(exc, Throttled):
        wait_time = getattr(exc, 'wait', None)
        message = f'Too many requests. Please try again in {wait_time} seconds.' if wait_time else 'Too many requests. Please try again later.'
        return Response(
            {
                'status': False,
                'message': message,
                'error': 'rate_limit_exceeded',
                'retry_after': wait_time
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Handle validation errors
    if isinstance(exc, ValidationError):
        return Response(
            {
                'status': False,
                'message': 'Validation error. Please check your input.',
                'error': 'validation_error',
                'details': exc.detail
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Handle not found errors
    if isinstance(exc, NotFound):
        return Response(
            {
                'status': False,
                'message': 'The requested resource was not found.',
                'error': 'not_found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Handle method not allowed
    if isinstance(exc, MethodNotAllowed):
        return Response(
            {
                'status': False,
                'message': f'Method {exc.detail} is not allowed for this endpoint.',
                'error': 'method_not_allowed'
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    # Handle TypeError (usually programming errors)
    if isinstance(exc, TypeError):
        error_msg = str(exc)
        if "required positional argument" in error_msg:
            return Response(
                {
                    'status': False,
                    'message': 'Invalid request format. Please check the API documentation.',
                    'error': 'invalid_format'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Fall back to DRF's default exception handler
    response = exception_handler(exc, context)
    
    # If DRF handled it, format the response consistently
    if response is not None:
        return Response(
            {
                'status': False,
                'message': response.data.get('detail', 'An error occurred.'),
                'error': 'api_error',
                'details': response.data
            },
            status=response.status_code
        )
    
    # Unhandled exception - log it and return generic error
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f'Unhandled exception: {exc}', exc_info=True)
    
    return Response(
        {
            'status': False,
            'message': 'An unexpected error occurred. Please try again later.',
            'error': 'internal_server_error'
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def format_success_response(data=None, message='Success', status_code=status.HTTP_200_OK):
    """
    Helper function to format success responses consistently.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        Response: Formatted success response
    """
    response_data = {
        'status': True,
        'message': message,
    }
    
    if data is not None:
        response_data['data'] = data
    
    return Response(response_data, status=status_code)


    