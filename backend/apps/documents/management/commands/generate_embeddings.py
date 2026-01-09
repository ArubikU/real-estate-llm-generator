"""
Django management command to generate embeddings for all documents
Usage: python manage.py generate_embeddings
"""

from django.core.management.base import BaseCommand
from apps.documents.models import Document
from core.llm.embeddings import generate_embedding
from django.conf import settings
import time


class Command(BaseCommand):
    help = 'Generates embeddings for all documents without embeddings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate embeddings even if they already exist',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write(self.style.SUCCESS('🔮 Generating embeddings...'))
        self.stdout.write('')

        # Get documents that need embeddings
        if force:
            documents = Document.objects.all()
            self.stdout.write(f'🔄 Force mode: Regenerating ALL {documents.count()} documents')
        else:
            documents = Document.objects.filter(embedding__isnull=True)
            self.stdout.write(f'📊 Found {documents.count()} documents without embeddings')

        if not documents.exists():
            self.stdout.write(self.style.SUCCESS('✅ All documents already have embeddings!'))
            return

        success_count = 0
        error_count = 0
        total = documents.count()
        
        self.stdout.write('')
        
        for i, doc in enumerate(documents, 1):
            try:
                # Generate embedding
                content = doc.content or ''
                if not content.strip():
                    self.stdout.write(f'  ⚠️  [{i}/{total}] Skipping empty document: {doc.id}')
                    continue
                
                # Truncate if too long (OpenAI has token limits)
                max_chars = 8000
                if len(content) > max_chars:
                    content = content[:max_chars]
                
                embedding = generate_embedding(content)
                doc.embedding = embedding
                doc.save()
                
                success_count += 1
                property_title = doc.property.title[:50] if doc.property else 'N/A'
                self.stdout.write(f'  ✅ [{i}/{total}] {property_title}...')
                
                # Small delay to avoid rate limits
                if i % 10 == 0:
                    time.sleep(0.5)
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ❌ [{i}/{total}] Error: {str(e)[:100]}')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Embedding generation complete!'))
        self.stdout.write(f'   ✅ Success: {success_count}')
        
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'   ❌ Errors: {error_count}'))
        
        self.stdout.write('')
        self.stdout.write('🎉 RAG system is now ready to use!')
