"""
Views for Property Ingestion API.
Handles URL scraping and text-based property extraction.
"""

import logging
import uuid
import threading
from decimal import Decimal
from datetime import datetime, date, timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.tenants.models import Tenant
from apps.users.models import CustomUser

from core.scraping.scraper import scrape_url, ScraperError
from core.scraping.extractors import get_extractor, EXTRACTORS
from core.llm.extraction import extract_property_data, ExtractionError
from core.llm.embeddings import generate_property_embedding
from core.utils.website_detector import detect_source_website
from apps.properties.models import Property, PropertyImage
from apps.properties.serializers import PropertyDetailSerializer
from .serializers import SupportedWebsiteSerializer
from .progress import ProgressTracker

logger = logging.getLogger(__name__)


def serialize_for_json(obj):
    """Convert non-JSON-serializable objects to JSON-serializable types."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    return obj


class SupportedWebsitesView(APIView):
    """
    Endpoint to get list of supported websites with their configurations.
    
    GET /ingest/supported-websites/
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return list of supported websites."""
        
        # Define supported websites with their configurations
        websites = [
            {
                'id': 'brevitas',
                'name': 'Brevitas',
                'url': 'https://brevitas.com',
                'color': '#f59e0b',
                'active': True,
                'has_extractor': 'brevitas.com' in EXTRACTORS
            },
            {
                'id': 'encuentra24',
                'name': 'Encuentra24',
                'url': 'https://encuentra24.com/costa-rica-en',
                'color': '#10b981',
                'active': True,
                'has_extractor': 'encuentra24.com' in EXTRACTORS
            },
            {
                'id': 'coldwellbanker',
                'name': 'Coldwell Banker',
                'url': 'https://www.coldwellbankercostarica.com',
                'color': '#8b5cf6',
                'active': True,
                'has_extractor': 'coldwellbankercostarica.com' in EXTRACTORS
            },
            {
                'id': 'other',
                'name': 'Other Sources',
                'url': None,
                'color': '#6b7280',
                'active': True,
                'has_extractor': False
            }
        ]
        
        serializer = SupportedWebsiteSerializer(websites, many=True)
        
        return Response({
            'status': 'success',
            'websites': serializer.data,
            'total_extractors': len(EXTRACTORS),
            'extractor_sites': list(EXTRACTORS.keys())
        }, status=status.HTTP_200_OK)


class IngestionStatsView(APIView):
    """
    Endpoint to get ingestion statistics.
    
    GET /ingest/stats/
    Returns: {
        "properties_today": 15,
        "properties_this_week": 42,
        "properties_this_month": 156,
        "recent_properties": [
            {
                "id": "uuid",
                "title": "Casa en...",
                "location": "San José",
                "price_usd": 250000,
                "created_at": "2026-01-12T15:30:00Z"
            },
            ...
        ]
    }
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get ingestion statistics."""
        try:
            # Get timezone-aware dates
            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=now.weekday())
            month_start = today_start.replace(day=1)
            
            # Count properties created today, this week, and this month
            properties_today = Property.objects.filter(created_at__gte=today_start).count()
            properties_this_week = Property.objects.filter(created_at__gte=week_start).count()
            properties_this_month = Property.objects.filter(created_at__gte=month_start).count()
            
            # Get last 10 properties
            recent_properties = Property.objects.order_by('-created_at')[:10]
            recent_properties_data = [
                {
                    'id': str(prop.id),
                    'title': prop.property_name or 'Sin título',
                    'location': prop.location or 'Ubicación no especificada',
                    'price_usd': float(prop.price_usd) if prop.price_usd else None,
                    'bedrooms': prop.bedrooms,
                    'bathrooms': float(prop.bathrooms) if prop.bathrooms else None,
                    'source_website': prop.source_website or 'Desconocido',
                    'created_at': prop.created_at.isoformat()
                }
                for prop in recent_properties
            ]
            
            return Response({
                'status': 'success',
                'properties_today': properties_today,
                'properties_this_week': properties_this_week,
                'properties_this_month': properties_this_month,
                'recent_properties': recent_properties_data,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching ingestion stats: {e}", exc_info=True)
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IngestURLView(APIView):
    """
    Endpoint to ingest property from URL.
    
    POST /ingest/url
    {
        "url": "https://encuentra24.com/property/123",
        "use_websocket": true  // Optional: enables real-time progress updates
    }
    """
    
    authentication_classes = []  # No authentication required
    permission_classes = [AllowAny]
    
    def _process_url_with_progress(self, url: str, source_website_override: str, task_id: str):
        """Process URL in background thread with progress updates."""
        import time
        tracker = ProgressTracker(task_id)
        
        try:
            # Small delay to allow frontend WebSocket to connect
            time.sleep(0.5)
            
            # Step 1: Scraping (0-30%)
            tracker.update(5, "Iniciando scraping...", stage="Scraping", substage="Conectando al sitio web")
            logger.info(f"Step 1: Scraping URL: {url}")
            
            scraped_data = scrape_url(url)
            tracker.update(20, "Contenido descargado", stage="Scraping", substage="Procesando HTML")
            
            if not scraped_data.get('success'):
                tracker.error("Failed to scrape URL")
                return
            
            html_content = scraped_data.get('html', scraped_data.get('text', ''))
            tracker.update(30, f"HTML extraído ({len(html_content)} caracteres)", stage="Scraping", substage="Completado")
            time.sleep(0.3)  # Allow UI to show stage
            
            # Step 2: Detection (30-40%)
            tracker.update(35, "Detectando sitio web...", stage="Análisis", substage="Identificando fuente")
            time.sleep(0.2)
            
            if source_website_override:
                source_website = source_website_override
            else:
                source_website = detect_source_website(url)
            
            tracker.update(40, f"Sitio detectado: {source_website}", stage="Análisis")
            time.sleep(0.2)
            
            # Step 3: Extraction (40-80%)
            tracker.update(45, "Obteniendo extractor...", stage="Extracción", substage="Configurando herramientas")
            time.sleep(0.2)
            extractor = get_extractor(url)
            extractor_name = extractor.__class__.__name__
            use_site_extractor = extractor_name != 'BaseExtractor'
            
            if use_site_extractor:
                tracker.update(50, f"Usando extractor específico: {extractor.site_name}", stage="Extracción", substage="Extracción rápida")
                time.sleep(0.3)
                extracted_data = extractor.extract(html_content, url)
                tracker.update(75, "Datos extraídos con éxito", stage="Extracción", substage="Completado")
                time.sleep(0.3)
                extraction_method = 'site_specific'
                extraction_confidence = 0.95
            else:
                tracker.update(50, "Usando extracción con IA...", stage="Extracción", substage="Procesando con LLM")
                extracted_data = extract_property_data(html_content, url=url)
                tracker.update(75, "IA completó la extracción", stage="Extracción", substage="Completado")
                extraction_method = 'llm_based'
                extraction_confidence = extracted_data.get('extraction_confidence', 0.5)
            
            # Step 4: Finalization (80-100%)
            time.sleep(0.2)
            tracker.update(85, "Finalizando...", stage="Procesamiento", substage="Limpiando datos")
            time.sleep(0.3)
            
            extracted_data['source_website'] = source_website
            tenant = Tenant.objects.first()
            extracted_data['tenant'] = tenant
            
            if 'user_roles' not in extracted_data or not extracted_data['user_roles']:
                extracted_data['user_roles'] = ['buyer', 'staff', 'admin']
            
            # Clean metadata fields
            metadata_fields = ['tokens_used', 'raw_html', 'confidence_reasoning', 'extracted_at', 'field_confidence']
            for field in metadata_fields:
                extracted_data.pop(field, None)
            
            evidence_fields = [key for key in extracted_data.keys() if key.endswith('_evidence')]
            for field in evidence_fields:
                extracted_data.pop(field, None)
            
            tenant_id = extracted_data['tenant'].id if extracted_data.get('tenant') else None
            extracted_data['tenant_id'] = tenant_id
            extracted_data.pop('tenant', None)
            
            tracker.update(95, "Datos listos", stage="Procesamiento", substage="Preparando respuesta")
            
            # Send completion with serialized data
            tracker.complete(serialize_for_json({
                'property': extracted_data,
                'extraction_method': extraction_method,
                'extraction_confidence': extraction_confidence,
                'extractor_used': extractor_name,
            }), message="Extracción completada exitosamente")
            
            tracker.update(100, "¡Completado!", stage="Completado")
            
        except Exception as e:
            logger.error(f"❌ Error in background processing: {e}", exc_info=True)
            tracker.error(f"Error: {str(e)}")
    
    def post(self, request):
        """Process URL and extract property data."""
        
        logger.info(f"=== IngestURLView POST request received ===")
        
        url = request.data.get('url')
        source_website_override = request.data.get('source_website')
        use_websocket = request.data.get('use_websocket', False)
        
        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If WebSocket requested, start background processing and return task_id
        if use_websocket:
            task_id = str(uuid.uuid4())
            logger.info(f"🔌 WebSocket mode - Starting background task: {task_id}")
            
            # Start processing in background thread
            thread = threading.Thread(
                target=self._process_url_with_progress,
                args=(url, source_website_override, task_id)
            )
            thread.daemon = True
            thread.start()
            
            return Response({
                'status': 'processing',
                'task_id': task_id,
                'message': 'Processing started. Connect to WebSocket for progress updates.'
            }, status=status.HTTP_202_ACCEPTED)
        
        # Original synchronous processing (fallback)
        try:
            # Step 1: Scrape the URL
            logger.info(f"Step 1: Scraping URL: {url}")
            scraped_data = scrape_url(url)
            logger.info(f"Scraping result: success={scraped_data.get('success')}")
            
            if not scraped_data.get('success'):
                logger.error("Scraping failed")
                return Response(
                    {'error': 'Failed to scrape URL'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            html_content = scraped_data.get('html', scraped_data.get('text', ''))
            logger.info(f"Original HTML size: {len(html_content)} chars")
            
            # Step 2: Detect source website and get appropriate extractor
            if source_website_override:
                source_website = source_website_override
                logger.info(f"Step 2: Using user-selected source website: {source_website}")
            else:
                source_website = detect_source_website(url)
                logger.info(f"Step 2: Auto-detected source website: {source_website}")
            
            # Step 3: Get site-specific extractor
            extractor = get_extractor(url)
            extractor_name = extractor.__class__.__name__
            logger.info(f"Step 3: Using extractor: {extractor_name} for {extractor.site_name}")
            
            # Check if we have a site-specific extractor (not BaseExtractor)
            use_site_extractor = extractor_name != 'BaseExtractor'
            
            if use_site_extractor:
                logger.info(f"✓ Using site-specific extractor - no LLM needed")
                
                # Extract using site-specific rules (fast, free, precise)
                extracted_data = extractor.extract(html_content, url)
                logger.info(f"Extraction complete using {extractor_name}")
                logger.info(f"Extracted fields: {[k for k, v in extracted_data.items() if v is not None]}")
                
                extraction_method = 'site_specific'
                extraction_confidence = 0.95  # High confidence for rule-based extraction
                
            else:
                logger.info(f"⚠ No site-specific extractor available - falling back to LLM")
                
                # Fallback to LLM-based extraction (slower, costs tokens, less precise)
                # The PropertyExtractor._clean_content() method will use BeautifulSoup
                # to intelligently extract relevant sections before sending to LLM
                logger.info("Extracting property data with LLM...")
                extracted_data = extract_property_data(html_content, url=url)
                logger.info(f"Extraction complete. Confidence: {extracted_data.get('extraction_confidence')}")
                
                extraction_method = 'llm_based'
                extraction_confidence = extracted_data.get('extraction_confidence', 0.5)
            
            # Step 4: Add source website and tenant
            extracted_data['source_website'] = source_website
            
            tenant = Tenant.objects.first()
            logger.info(f"Using tenant: {tenant.name if tenant else 'None'}")
            extracted_data['tenant'] = tenant
            
            # Set default user_roles if not specified
            if 'user_roles' not in extracted_data or not extracted_data['user_roles']:
                extracted_data['user_roles'] = ['buyer', 'staff', 'admin']
            logger.info(f"User roles: {extracted_data['user_roles']}")
            
            # Remove fields that are not in the Property model
            metadata_fields = ['tokens_used', 'raw_html', 'confidence_reasoning', 'extracted_at', 'field_confidence']
            for field in metadata_fields:
                extracted_data.pop(field, None)
            
            # Also remove all *_evidence fields
            evidence_fields = [key for key in extracted_data.keys() if key.endswith('_evidence')]
            for field in evidence_fields:
                extracted_data.pop(field, None)
            
            logger.info(f"Cleaned extracted_data keys: {list(extracted_data.keys())}")
            
            # DON'T create Property - just return the extracted data for preview
            # Property will be created via separate save endpoint when user clicks "Save"
            logger.info("✓ Extraction successful - returning data for preview")
            
            # Convert tenant object to ID for JSON serialization
            tenant_id = extracted_data['tenant'].id if extracted_data.get('tenant') else None
            extracted_data['tenant_id'] = tenant_id
            extracted_data.pop('tenant', None)  # Remove the non-serializable tenant object
            
            # Return extracted data without saving to database
            response_data = {
                'status': 'success',
                'message': f'Property data extracted successfully using {extraction_method} (not saved yet)',
                'property': extracted_data,
                'extraction_method': extraction_method,
                'extraction_confidence': extraction_confidence,
                'extractor_used': extractor_name,
            }
            
            logger.info(f"=== Request completed successfully ===")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ScraperError as e:
            logger.error(f"❌ Scraping error: {e}", exc_info=True)
            return Response(
                {'error': f'Scraping failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except ExtractionError as e:
            logger.error(f"❌ Extraction error: {e}", exc_info=True)
            return Response(
                {'error': f'Extraction failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"❌ Unexpected error in IngestURLView: {e}", exc_info=True)
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IngestTextView(APIView):
    """
    Endpoint to ingest property from text.
    
    POST /ingest/text
    {
        "text": "Beautiful 3-bedroom villa in Tamarindo..."
    }
    """
    
    authentication_classes = []  # No authentication required
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Process text and extract property data."""
        
        text = request.data.get('text')
        source_website_override = request.data.get('source_website')  # Optional: user-selected website
        
        if not text:
            return Response(
                {'error': 'Text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Extract property data with LLM
            logger.info("Extracting property data from text...")
            extracted_data = extract_property_data(text)
            
            # Set source_website from user selection or default to 'other'
            extracted_data['source_website'] = source_website_override if source_website_override else 'other'
            logger.info(f"Using source_website: {extracted_data['source_website']}")
            
            # Add tenant
            tenant = Tenant.objects.first()
            extracted_data['tenant_id'] = tenant.id if tenant else None
            
            # Set default user_roles
            if 'user_roles' not in extracted_data or not extracted_data['user_roles']:
                extracted_data['user_roles'] = ['buyer', 'staff', 'admin']
            
            # DON'T create Property - just return extracted data for preview
            logger.info("✓ Extraction successful from text - returning data for preview")
            
            return Response({
                'status': 'success',
                'message': 'Property data extracted successfully (not saved yet)',
                'property': extracted_data,
                'extraction_confidence': extracted_data.get('extraction_confidence', 0),
                'field_confidence': extracted_data.get('field_confidence', {}),
            }, status=status.HTTP_200_OK)
            
        except ExtractionError as e:
            logger.error(f"Extraction error: {e}")
            return Response(
                {'error': f'Extraction failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IngestBatchView(APIView):
    """
    Endpoint to ingest multiple properties at once.
    
    POST /ingest/batch
    {
        "urls": ["https://...", "https://..."],
        "async": true
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Process multiple URLs in batch."""
        
        urls = request.data.get('urls', [])
        run_async = request.data.get('async', False)
        
        if not urls or not isinstance(urls, list):
            return Response(
                {'error': 'URLs array is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(urls) > 10:
            return Response(
                {'error': 'Maximum 10 URLs per batch'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if run_async:
            # Queue for async processing with Celery
            from apps.ingestion.tasks import ingest_url_task
            
            task_ids = []
            for url in urls:
                if request.user.is_authenticated:
                    tenant_id = str(request.user.tenant_id)
                    user_id = str(request.user.id)
                else:
                    tenant_id = str(Tenant.objects.first().id)
                    user_id = str(CustomUser.objects.first().id)

                task = ingest_url_task.delay(
                    url=url,
                    tenant_id=tenant_id,
                    user_id=user_id
                )
                task_ids.append(task.id)
            
            return Response({
                'status': 'queued',
                'message': f'{len(urls)} properties queued for processing',
                'task_ids': task_ids
            }, status=status.HTTP_202_ACCEPTED)
        
        else:
            # Process synchronously
            results = []
            for url in urls:
                try:
                    scraped_data = scrape_url(url)
                    extracted_data = extract_property_data(
                        scraped_data.get('html', ''), 
                        url=url
                    )
                    if request.user.is_authenticated:
                        extracted_data['tenant'] = request.user.tenant
                    else:
                        extracted_data['tenant'] = Tenant.objects.first()
                    extracted_data['user_roles'] = ['buyer', 'staff', 'admin']
                    
                    property_obj = Property.objects.create(**extracted_data)
                    
                    results.append({
                        'url': url,
                        'status': 'success',
                        'property_id': str(property_obj.id)
                    })
                    
                except Exception as e:
                    results.append({
                        'url': url,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return Response({
                'status': 'completed',
                'results': results
            }, status=status.HTTP_200_OK)


class SavePropertyView(APIView):
    """
    Endpoint to save extracted property data to database.
    
    POST /ingest/save
    {
        "property_data": { ... extracted property fields ... }
    }
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Save property data to database."""
        
        logger.info("=== SavePropertyView POST request received ===")
        
        property_data = request.data.get('property_data')
        
        if not property_data:
            return Response(
                {'error': 'property_data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Convert tenant_id back to tenant object
            tenant_id = property_data.get('tenant_id')
            if tenant_id:
                property_data['tenant'] = Tenant.objects.get(id=tenant_id)
                property_data.pop('tenant_id', None)
            elif 'tenant' not in property_data or not property_data['tenant']:
                property_data['tenant'] = Tenant.objects.first()
            
            # Set default user_roles
            if 'user_roles' not in property_data or not property_data['user_roles']:
                property_data['user_roles'] = ['buyer', 'staff', 'admin']
            
            # Remove fields that shouldn't be saved
            metadata_fields = ['tokens_used', 'raw_html', 'confidence_reasoning']
            for field in metadata_fields:
                property_data.pop(field, None)
            
            # Remove all *_evidence fields
            evidence_fields = [key for key in list(property_data.keys()) if key.endswith('_evidence')]
            for field in evidence_fields:
                property_data.pop(field, None)
            
            # Map extractor field names to Property model field names
            field_mapping = {
                'title': 'property_name',
                'area_m2': 'square_meters',
                'listing_type': 'status',  # for_sale -> available
            }
            
            for old_name, new_name in field_mapping.items():
                if old_name in property_data:
                    property_data[new_name] = property_data.pop(old_name)
            
            # Convert listing_type values to status values
            if 'status' in property_data:
                status_mapping = {
                    'for_sale': 'available',
                    'for_rent': 'available',
                    'sold': 'sold',
                }
                property_data['status'] = status_mapping.get(property_data['status'], 'available')
            
            # Ensure property_type has a default value if missing or None
            if not property_data.get('property_type'):
                property_data['property_type'] = 'house'  # Default to 'house' if not specified
                logger.info(f"⚠️ property_type was missing/null, defaulting to 'house'")
            
            # Build location from address/city/province if location is empty
            if not property_data.get('location') and (property_data.get('city') or property_data.get('address')):
                location_parts = []
                if property_data.get('address'):
                    location_parts.append(property_data['address'])
                if property_data.get('city'):
                    location_parts.append(property_data['city'])
                if property_data.get('province'):
                    location_parts.append(property_data['province'])
                property_data['location'] = ', '.join(location_parts)
            
            # If location is still empty, use coordinates or default
            if not property_data.get('location'):
                if property_data.get('latitude') and property_data.get('longitude'):
                    property_data['location'] = f"{property_data['latitude']}, {property_data['longitude']}"
                    logger.info(f"⚠️ location was missing, using coordinates: {property_data['location']}")
                else:
                    property_data['location'] = 'Unknown Location'
                    logger.info(f"⚠️ location was missing, defaulting to 'Unknown Location'")
            
            # Remove fields that don't exist in Property model
            fields_to_remove = ['address', 'city', 'province', 'country', 'agent_name', 'agent_phone', 'agent_email']
            for field in fields_to_remove:
                property_data.pop(field, None)
            
            # Check for duplicate by source_url
            source_url = property_data.get('source_url')
            logger.info(f"🔍 Checking for duplicate - source_url: {source_url}")
            
            if source_url:
                existing = Property.objects.filter(
                    source_url=source_url,
                    tenant=property_data.get('tenant')
                ).first()
                
                if existing:
                    logger.warning(f"⚠️ DUPLICATE DETECTED - Property already exists:")
                    logger.warning(f"   - URL: {source_url}")
                    logger.warning(f"   - Existing ID: {existing.id}")
                    logger.warning(f"   - Existing Name: {existing.property_name}")
                    return Response({
                        'status': 'error',
                        'message': f'This property already exists in the database (ID: {existing.id})',
                        'property_id': str(existing.id),
                        'property_name': existing.property_name,
                        'duplicate': True
                    }, status=status.HTTP_409_CONFLICT)
                else:
                    logger.info(f"✅ No duplicate found - OK to save")
            
            # Separate ManyToMany fields (must be set after object creation)
            images_data = property_data.pop('images', [])
            amenities_data = property_data.pop('amenities', [])
            
            # Create Property
            logger.info("Creating Property object from saved data...")
            property_obj = Property.objects.create(**property_data)
            
            # Create PropertyImage objects from URL list
            if images_data:
                logger.info(f"Creating {len(images_data)} PropertyImage objects...")
                created_count = 0
                for idx, image_url in enumerate(images_data):
                    if isinstance(image_url, str):  # Only process if it's a URL string
                        PropertyImage.objects.create(
                            property=property_obj,
                            image_url=image_url,
                            order=created_count,
                            is_primary=(created_count == 0)  # First image is primary
                        )
                        created_count += 1
                logger.info(f"✓ Created {created_count} images")
            
            # Set amenities (ArrayField - can be set directly)
            if amenities_data:
                logger.info(f"Setting {len(amenities_data)} amenities...")
                property_obj.amenities = amenities_data
                property_obj.save(update_fields=['amenities'])
            
            logger.info(f"✓ Property saved successfully: {property_obj.id}")
            logger.info(f"  - Name: {property_obj.property_name}")
            logger.info(f"  - Price: ${property_obj.price_usd}")
            
            # Generate embeddings in background thread (non-blocking)
            logger.info("🔮 Starting background embedding generation...")
            import threading
            
            def generate_embedding_background():
                """Generate embedding in background thread."""
                try:
                    from core.llm.embeddings import generate_property_embedding
                    embedding = generate_property_embedding(property_obj)
                    if embedding:
                        property_obj.embedding = embedding
                        property_obj.save(update_fields=['embedding'])
                        logger.info(f"✅ [BACKGROUND] Embedding generated: {property_obj.property_name}")
                    else:
                        logger.warning(f"⚠️ [BACKGROUND] Embedding generation failed: {property_obj.id}")
                except Exception as e:
                    logger.error(f"❌ [BACKGROUND] Error generating embedding: {e}", exc_info=True)
            
            thread = threading.Thread(target=generate_embedding_background, daemon=True)
            thread.start()
            logger.info("✅ Background embedding thread started")
            
            # Return serialized property immediately without waiting for embedding
            serializer = PropertyDetailSerializer(property_obj)
            
            return Response({
                'status': 'success',
                'message': 'Property saved successfully',
                'property_id': str(property_obj.id),
                'property': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"❌ Error saving property: {e}", exc_info=True)
            return Response(
                {'error': f'Failed to save property: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GenerateEmbeddingsView(APIView):
    """
    Admin endpoint to generate embeddings for all properties without embeddings.
    
    POST /ingest/generate-embeddings
    {
        "force": false  // Optional: regenerate even if embeddings exist
    }
    """
    
    authentication_classes = []
    permission_classes = [AllowAny]  # TODO: Add admin-only permission in production
    
    def post(self, request):
        """Generate embeddings for properties."""
        
        logger.info("=== GenerateEmbeddingsView POST request received ===")
        
        force = request.data.get('force', False)
        
        try:
            from apps.properties.models import Property
            
            # Get properties that need embeddings
            if force:
                properties = Property.objects.all()
                message = f'Force mode: Processing ALL {properties.count()} properties'
            else:
                properties = Property.objects.filter(embedding__isnull=True)
                message = f'Found {properties.count()} properties without embeddings'
            
            logger.info(message)
            
            if not properties.exists():
                return Response({
                    'status': 'success',
                    'message': 'All properties already have embeddings!',
                    'total_properties': Property.objects.count(),
                    'with_embeddings': Property.objects.filter(embedding__isnull=False).count(),
                    'processed': 0,
                    'errors': 0
                }, status=status.HTTP_200_OK)
            
            success_count = 0
            error_count = 0
            errors = []
            
            for property_obj in properties:
                try:
                    logger.info(f"Generating embedding for: {property_obj.property_name}")
                    
                    embedding = generate_property_embedding(property_obj)
                    
                    if embedding:
                        property_obj.embedding = embedding
                        property_obj.save(update_fields=['embedding'])
                        success_count += 1
                        logger.info(f"✓ Embedding generated for: {property_obj.property_name}")
                    else:
                        error_count += 1
                        error_msg = f"Failed to generate embedding for property: {property_obj.id}"
                        errors.append(error_msg)
                        logger.warning(error_msg)
                        
                except Exception as e:
                    error_count += 1
                    error_msg = f"Error processing property {property_obj.id}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg, exc_info=True)
            
            # Get final statistics
            total_properties = Property.objects.count()
            with_embeddings = Property.objects.filter(embedding__isnull=False).count()
            coverage = (with_embeddings / total_properties * 100) if total_properties > 0 else 0
            
            logger.info(f"✅ Embedding generation complete!")
            logger.info(f"   Success: {success_count}, Errors: {error_count}")
            logger.info(f"   Coverage: {with_embeddings}/{total_properties} ({coverage:.1f}%)")
            
            return Response({
                'status': 'success',
                'message': 'Embedding generation complete',
                'total_properties': total_properties,
                'with_embeddings': with_embeddings,
                'coverage_percent': round(coverage, 1),
                'processed': success_count + error_count,
                'success': success_count,
                'errors': error_count,
                'error_details': errors[:10] if errors else []  # Return first 10 errors
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Error in GenerateEmbeddingsView: {e}", exc_info=True)
            return Response(
                {'error': f'Failed to generate embeddings: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
