"""
WebSocket consumer for real-time progress updates during property ingestion.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class ProgressConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer that sends progress updates for property ingestion tasks.
    
    URL: ws://localhost:8000/ws/progress/<task_id>/
    """
    
    async def connect(self):
        """Accept WebSocket connection and join task-specific group."""
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.group_name = f'progress_{self.task_id}'
        
        logger.info(f"🔌 WebSocket connecting for task: {self.task_id}")
        
        # Join task-specific group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'task_id': self.task_id,
            'message': 'Connected to progress updates'
        }))
        
        logger.info(f"✅ WebSocket connected for task: {self.task_id}")
    
    async def disconnect(self, close_code):
        """Leave task-specific group on disconnect."""
        logger.info(f"🔌 WebSocket disconnecting for task: {self.task_id}, code: {close_code}")
        
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket (client -> server)
    async def receive(self, text_data):
        """Handle incoming WebSocket messages from client."""
        try:
            data = json.loads(text_data)
            logger.debug(f"📨 Received WebSocket message: {data}")
            
            # Could handle client commands here if needed
            # For now, this is primarily server -> client
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON received: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    # Receive message from channel layer (broadcast -> this consumer)
    async def progress_update(self, event):
        """Send progress update to WebSocket client."""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'progress',
            'progress': event.get('progress', 0),
            'status': event.get('status', ''),
            'message': event.get('message', ''),
            'stage': event.get('stage', ''),
            'substage': event.get('substage', ''),
            'step': event.get('step'),
            'total_steps': event.get('total_steps'),
        }))
    
    async def task_complete(self, event):
        """Send completion message to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'complete',
            'message': event.get('message', 'Task completed successfully'),
            'data': event.get('data', {})
        }))
    
    async def task_error(self, event):
        """Send error message to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': event.get('message', 'An error occurred'),
            'error': event.get('error', '')
        }))
