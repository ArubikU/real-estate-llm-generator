"""
Utility functions for sending progress updates via WebSockets.
"""
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    Helper class to send progress updates to WebSocket clients.
    
    Usage:
        tracker = ProgressTracker(task_id)
        tracker.update(20, "Downloading content...", stage="Scraping")
        tracker.complete({"property": property_data})
        tracker.error("Failed to parse content")
    """
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.group_name = f'progress_{task_id}'
        self.channel_layer = get_channel_layer()
    
    def _send_to_group(self, event_type: str, data: dict):
        """Send message to WebSocket group."""
        if not self.channel_layer:
            logger.warning(f"Channel layer not configured, skipping progress update")
            return
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    'type': event_type,
                    **data
                }
            )
            logger.debug(f"📤 Sent {event_type} to {self.group_name}: {data}")
        except Exception as e:
            logger.error(f"❌ Error sending to channel layer: {e}")
    
    def update(
        self, 
        progress: int, 
        status: str, 
        stage: str = None, 
        substage: str = None,
        step: int = None,
        total_steps: int = None
    ):
        """
        Send progress update.
        
        Args:
            progress: Progress percentage (0-100)
            status: Status message
            stage: Current stage (e.g., "Scraping", "Extracting", "Saving")
            substage: Sub-stage description
            step: Current step number
            total_steps: Total number of steps
        """
        self._send_to_group('progress_update', {
            'progress': progress,
            'status': status,
            'message': status,
            'stage': stage,
            'substage': substage,
            'step': step,
            'total_steps': total_steps,
        })
    
    def complete(self, data: dict = None, message: str = "Task completed successfully"):
        """
        Send completion message.
        
        Args:
            data: Result data to send to client
            message: Completion message
        """
        self._send_to_group('task_complete', {
            'message': message,
            'data': data or {}
        })
    
    def error(self, message: str, error: str = None):
        """
        Send error message.
        
        Args:
            message: Error message
            error: Detailed error information
        """
        self._send_to_group('task_error', {
            'message': message,
            'error': error or message
        })
