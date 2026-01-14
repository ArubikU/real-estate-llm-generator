"""
Celery tasks for property ingestion.
"""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def ingest_url_task(self, url, tenant_id, user_id):
    """
    Async task to ingest property from URL.
    
    Args:
        url: Property URL to scrape
        tenant_id: Tenant UUID
        user_id: User UUID who initiated the task
    """
    
    from core.scraping.scraper import scrape_url, ScraperError
    from core.llm.extraction import extract_property_data, ExtractionError
    from apps.properties.models import Property
    from apps.tenants.models import Tenant
    
    try:
        logger.info(f"Starting async ingestion for URL: {url}")
        
        # Scrape URL
        scraped_data = scrape_url(url)
        
        if not scraped_data.get('success'):
            raise Exception("Failed to scrape URL")
        
        # Extract property data
        html_content = scraped_data.get('html', scraped_data.get('text', ''))
        extracted_data = extract_property_data(html_content, url=url)
        
        # Get tenant
        tenant = Tenant.objects.get(id=tenant_id)
        extracted_data['tenant'] = tenant
        
        # Set default user_roles
        if 'user_roles' not in extracted_data or not extracted_data['user_roles']:
            extracted_data['user_roles'] = ['buyer', 'staff', 'admin']
        
        # Create property
        property_obj = Property.objects.create(**extracted_data)
        
        logger.info(f"Property created successfully: {property_obj.id}")
        
        return {
            'status': 'success',
            'property_id': str(property_obj.id),
            'property_name': property_obj.property_name
        }
        
    except (ScraperError, ExtractionError) as e:
        logger.error(f"Ingestion error: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    
    except Exception as e:
        logger.error(f"Unexpected error in ingestion task: {e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def generate_property_embedding_task(property_id):
    """
    Generate embedding for property content.
    
    Args:
        property_id: Property UUID
    """
    
    from apps.properties.models import Property
    from langchain_openai import OpenAIEmbeddings
    from django.conf import settings
    
    try:
        property_obj = Property.objects.get(id=property_id)
        
        if not property_obj.content_for_search:
            property_obj.content_for_search = property_obj.generate_search_content()
        
        # Generate embedding
        embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        embedding = embeddings.embed_query(property_obj.content_for_search)
        property_obj.embedding = embedding
        property_obj.save(update_fields=['embedding', 'content_for_search'])
    except Exception as e:
        logger.error(f"Error generating embedding for property {property_id}: {e}")


@shared_task(bind=True, max_retries=3)
def generate_embedding_async(self, property_id: str):
    """
    Generate embedding for a property asynchronously (NEW version).
    Uses the new embedding system from core.llm.embeddings
    
    Args:
        property_id: UUID of the property
        
    Returns:
        dict with success status and details
    """
    try:
        from apps.properties.models import Property
        from core.llm.embeddings import generate_property_embedding
        
        logger.info(f"🔮 [ASYNC] Starting embedding generation for property: {property_id}")
        
        # Get property
        property_obj = Property.objects.get(id=property_id)
        
        # Generate embedding
        embedding = generate_property_embedding(property_obj)
        
        if embedding:
            property_obj.embedding = embedding
            property_obj.save(update_fields=['embedding'])
            logger.info(f"✅ [ASYNC] Embedding generated successfully for: {property_obj.property_name} (dimension: {len(embedding)})")
            return {
                'success': True,
                'property_id': str(property_id),
                'property_name': property_obj.property_name,
                'dimension': len(embedding)
            }
        else:
            logger.warning(f"⚠️ [ASYNC] Failed to generate embedding for: {property_id}")
            return {
                'success': False,
                'property_id': str(property_id),
                'error': 'Embedding generation returned None'
            }
            
    except Property.DoesNotExist:
        logger.error(f"❌ [ASYNC] Property not found: {property_id}")
        return {
            'success': False,
            'property_id': str(property_id),
            'error': 'Property not found'
        }
        
    except Exception as e:
        logger.error(f"❌ [ASYNC] Error generating embedding for {property_id}: {e}", exc_info=True)
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            logger.info(f"🔄 Retrying... (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        
        return {
            'success': False,
            'property_id': str(property_id),
            'error': str(e)
        }
        
        logger.info(f"Generated embedding for property {property_id}")
        
        return {'status': 'success'}
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def generate_document_embedding_task(document_id):
    """
    Generate embedding for document content.
    
    Args:
        document_id: Document UUID
    """
    
    from apps.documents.models import Document
    from langchain_openai import OpenAIEmbeddings
    from django.conf import settings
    
    try:
        document = Document.objects.get(id=document_id)
        
        # Generate embedding
        embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        embedding = embeddings.embed_query(document.content)
        document.embedding = embedding
        document.save(update_fields=['embedding'])
        
        logger.info(f"Generated embedding for document {document_id}")
        
        return {'status': 'success'}
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True, max_retries=3)
def process_google_sheet_task(
    self, 
    spreadsheet_id: str, 
    notify_email: str,
    task_id: str = None,
    create_results_sheet: bool = False,
    results_sheet_id: str = None
):
    """
    Process all pending rows from a Google Sheet asynchronously.
    
    Args:
        spreadsheet_id: The Google Sheets ID
        notify_email: Email to send notification when complete
        task_id: Optional task ID for progress tracking
        create_results_sheet: If True, writes to results spreadsheet
        results_sheet_id: Optional ID of pre-created results spreadsheet
    """
    from apps.tenants.models import Tenant
    from apps.properties.models import Property
    from core.scraping.scraper import scrape_url
    from core.llm.extraction import extract_property_data
    from apps.ingestion.google_sheets import process_sheet_batch
    from apps.ingestion.email_notifications import send_batch_completion_email, send_error_notification
    
    logger.info(f"Starting Google Sheet processing: {spreadsheet_id}")
    
    def process_url(url: str):
        """Process a single URL and return success status."""
        try:
            scraped_data = scrape_url(url)
            
            if not scraped_data.get('success'):
                return False, {'error': 'Failed to scrape URL'}
            
            html_content = scraped_data.get('html', scraped_data.get('text', ''))
            extracted_data = extract_property_data(html_content, url=url)
            
            # Set tenant
            extracted_data['tenant'] = Tenant.objects.first()
            extracted_data['user_roles'] = ['buyer', 'staff', 'admin']
            
            # Clean metadata
            metadata_fields = ['tokens_used', 'raw_html', 'confidence_reasoning', 
                             'extracted_at', 'field_confidence']
            for field in metadata_fields:
                extracted_data.pop(field, None)
            
            evidence_fields = [key for key in extracted_data.keys() if key.endswith('_evidence')]
            for field in evidence_fields:
                extracted_data.pop(field, None)
            
            # Create property
            property_obj = Property.objects.create(**extracted_data)
            
            return True, {'property_id': str(property_obj.id)}
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            return False, {'error': str(e)}
    
    try:
        # Process the sheet
        results = process_sheet_batch(
            spreadsheet_id=spreadsheet_id,
            process_callback=process_url,
            task_id=task_id,
            create_results_sheet=create_results_sheet,
            results_sheet_id=results_sheet_id
        )
        
        # Send completion email
        admin_panel_url = "http://localhost:8080/admin/properties/property/"  # Update with actual URL
        send_batch_completion_email(
            recipient_email=notify_email,
            results=results,
            spreadsheet_id=spreadsheet_id,
            admin_panel_url=admin_panel_url
        )
        
        logger.info(f"Google Sheet processing completed: {results['processed']} processed, {results['failed']} failed")
        
        result_data = {
            'status': 'completed',
            'results': results
        }
        
        # Include results spreadsheet info if it was created
        if 'results_spreadsheet' in results:
            result_data['results_spreadsheet'] = results['results_spreadsheet']
            logger.info(f"Results spreadsheet created: {results['results_spreadsheet']['spreadsheet_url']}")
        
        return result_data
        
    except Exception as e:
        logger.error(f"Error in Google Sheet task: {e}", exc_info=True)
        
        # Send error notification
        send_error_notification(
            recipient_email=notify_email,
            error_message=str(e),
            spreadsheet_id=spreadsheet_id
        )
        
        # Retry the task
        raise self.retry(exc=e, countdown=60)

