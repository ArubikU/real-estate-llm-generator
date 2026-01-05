#!/usr/bin/env python
"""
Management command to generate embeddings for all properties and documents.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from apps.properties.models import Property
from apps.documents.models import Document
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate embeddings for properties and documents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--properties',
            action='store_true',
            help='Generate embeddings for properties only',
        )
        parser.add_argument(
            '--documents',
            action='store_true',
            help='Generate embeddings for documents only',
        )
        parser.add_argument(
            '--tenant',
            type=str,
            help='Filter by tenant slug',
        )

    def handle(self, *args, **options):
        
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Determine what to process
        do_properties = options.get('properties') or not options.get('documents')
        do_documents = options.get('documents') or not options.get('properties')
        tenant_slug = options.get('tenant')
        
        # Process properties
        if do_properties:
            self.stdout.write(self.style.SUCCESS('Generating property embeddings...'))
            
            properties = Property.objects.filter(embedding__isnull=True)
            
            if tenant_slug:
                properties = properties.filter(tenant__slug=tenant_slug)
            
            total = properties.count()
            
            if total == 0:
                self.stdout.write(self.style.WARNING('No properties need embeddings'))
            else:
                for prop in tqdm(properties, desc="Properties", total=total):
                    try:
                        # Generate search content
                        if not prop.content_for_search:
                            prop.content_for_search = prop.generate_search_content()
                        
                        # Generate embedding
                        embedding = embeddings.embed_query(prop.content_for_search)
                        prop.embedding = embedding
                        prop.save(update_fields=['embedding', 'content_for_search'])
                        
                    except Exception as e:
                        logger.error(f"Error processing property {prop.id}: {e}")
                        self.stdout.write(
                            self.style.ERROR(f"Failed: {prop.property_name} - {e}")
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Generated embeddings for {total} properties')
                )
        
        # Process documents
        if do_documents:
            self.stdout.write(self.style.SUCCESS('Generating document embeddings...'))
            
            documents = Document.objects.filter(embedding__isnull=True)
            
            if tenant_slug:
                documents = documents.filter(tenant__slug=tenant_slug)
            
            total = documents.count()
            
            if total == 0:
                self.stdout.write(self.style.WARNING('No documents need embeddings'))
            else:
                for doc in tqdm(documents, desc="Documents", total=total):
                    try:
                        # Generate embedding
                        embedding = embeddings.embed_query(doc.content)
                        doc.embedding = embedding
                        doc.save(update_fields=['embedding'])
                        
                    except Exception as e:
                        logger.error(f"Error processing document {doc.id}: {e}")
                        self.stdout.write(
                            self.style.ERROR(f"Failed: {doc.get_content_type_display()} - {e}")
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Generated embeddings for {total} documents')
                )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Embedding generation complete!'))
