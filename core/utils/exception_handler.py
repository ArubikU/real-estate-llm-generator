"""
Custom exception handler for REST API.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Standardize error response format
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
        }
        
        # Add error details
        if isinstance(response.data, dict):
            # If it's a dict, merge it
            if 'detail' in response.data:
                custom_response_data['message'] = response.data['detail']
            else:
                custom_response_data['errors'] = response.data
        elif isinstance(response.data, list):
            custom_response_data['errors'] = response.data
        else:
            custom_response_data['message'] = str(response.data)
        
        response.data = custom_response_data
    
    else:
        # Log unexpected exceptions
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        # Return a generic error response
        response = Response(
            {
                'error': True,
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred. Please try again later.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response
