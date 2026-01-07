from django.http import JsonResponse
from django.db import connection
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Simplified health check for DigitalOcean.
    Only checks database connection.
    """
    logger.info("🏥 Health check started")
    health_status = {
        'status': 'healthy',
        'database': 'unknown'
    }
    
    # Check database only
    try:
        logger.info("🔍 Checking database connection...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['database'] = 'ok'
        logger.info("✅ Database OK")
        status_code = 200
    except Exception as e:
        logger.error(f"❌ Database error: {str(e)}")
        health_status['status'] = 'unhealthy'
        health_status['database'] = f'error: {str(e)}'
        status_code = 503
    
    logger.info(f"🏥 Health check completed: {health_status['status']} (HTTP {status_code})")
    return JsonResponse(health_status, status=status_code)