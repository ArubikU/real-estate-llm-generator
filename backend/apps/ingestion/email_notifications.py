"""
Email notification service for Google Sheets batch processing
"""

import logging
from typing import Dict, Any, List
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_batch_completion_email(
    recipient_email: str,
    results: Dict[str, Any],
    spreadsheet_id: str,
    admin_panel_url: str = None
) -> bool:
    """
    Send email notification when batch processing is complete.
    
    Args:
        recipient_email: Email address to send notification to
        results: Dictionary with processing results (total, processed, failed)
        spreadsheet_id: The Google Sheets ID
        admin_panel_url: Optional URL to admin panel
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        total = results.get('total', 0)
        processed = results.get('processed', 0)
        failed = results.get('failed', 0)
        
        # Create sheet URL
        sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        
        # Build subject
        if failed == 0:
            subject = f"✅ Batch completado: {processed} propiedades procesadas exitosamente"
        else:
            subject = f"⚠️ Batch completado: {processed} procesadas, {failed} fallaron"
        
        # Build HTML email
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .stats {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; 
                         box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .stat-row {{ display: flex; justify-content: space-between; padding: 10px 0; 
                            border-bottom: 1px solid #e5e7eb; }}
                .stat-row:last-child {{ border-bottom: none; }}
                .stat-label {{ font-weight: 600; color: #6b7280; }}
                .stat-value {{ font-weight: bold; font-size: 1.2em; }}
                .success {{ color: #10b981; }}
                .error {{ color: #ef4444; }}
                .button {{ display: inline-block; background: #667eea; color: white; 
                          padding: 12px 24px; text-decoration: none; border-radius: 6px; 
                          margin: 10px 5px; font-weight: 600; }}
                .button:hover {{ background: #5568d3; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Procesamiento Completado</h1>
                    <p>Tu batch de propiedades ha terminado de procesarse</p>
                </div>
                
                <div class="content">
                    <h2>Resumen de Resultados</h2>
                    
                    <div class="stats">
                        <div class="stat-row">
                            <span class="stat-label">Total de propiedades:</span>
                            <span class="stat-value">{total}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Procesadas exitosamente:</span>
                            <span class="stat-value success">{processed}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Fallidas:</span>
                            <span class="stat-value error">{failed}</span>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{sheet_url}" class="button">📊 Ver Google Sheet Actualizado</a>
                        {f'<a href="{admin_panel_url}" class="button">🏠 Ver Propiedades en Admin Panel</a>' if admin_panel_url else ''}
                    </div>
                    
                    {f'''
                    <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <strong>⚠️ Atención:</strong> {failed} propiedades no pudieron ser procesadas. 
                        Revisa el Google Sheet para ver los detalles de los errores.
                    </div>
                    ''' if failed > 0 else ''}
                    
                    <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <strong>💡 Próximos pasos:</strong>
                        <ul style="margin: 10px 0;">
                            <li>Revisa las propiedades procesadas en el admin panel</li>
                            <li>Verifica que los datos extraídos sean correctos</li>
                            <li>Corrige las URLs que fallaron y vuelve a procesarlas</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Este es un mensaje automático del sistema de ingesta de propiedades.</p>
                    <p>Si tienes alguna pregunta, contacta al equipo de soporte.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
        Procesamiento de Batch Completado
        
        Resumen de Resultados:
        - Total de propiedades: {total}
        - Procesadas exitosamente: {processed}
        - Fallidas: {failed}
        
        Google Sheet actualizado: {sheet_url}
        {f'Admin Panel: {admin_panel_url}' if admin_panel_url else ''}
        
        {'⚠️ Atención: ' + str(failed) + ' propiedades no pudieron ser procesadas.' if failed > 0 else ''}
        
        Este es un mensaje automático del sistema de ingesta de propiedades.
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Batch completion email sent to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending batch completion email: {e}", exc_info=True)
        return False


def send_error_notification(
    recipient_email: str,
    error_message: str,
    spreadsheet_id: str = None
) -> bool:
    """
    Send email notification when batch processing fails completely.
    
    Args:
        recipient_email: Email address to send notification to
        error_message: Description of the error
        spreadsheet_id: Optional Google Sheets ID
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = "❌ Error en procesamiento de batch"
        
        sheet_link = ""
        if spreadsheet_id:
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
            sheet_link = f"\n\nGoogle Sheet: {sheet_url}"
        
        message = f"""
        Error en Procesamiento de Batch
        
        Ha ocurrido un error al intentar procesar el batch de propiedades:
        
        {error_message}
        {sheet_link}
        
        Por favor, revisa la configuración y vuelve a intentar.
        
        Este es un mensaje automático del sistema de ingesta de propiedades.
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        logger.info(f"Error notification email sent to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending error notification email: {e}", exc_info=True)
        return False
