"""
Django management command to seed test property data
Usage: python manage.py seed_test_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant
from apps.properties.models import Property
from apps.documents.models import Document
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with test property data for Costa Rica'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Seeding test data...'))

        # Get or create default tenant
        tenant, created = Tenant.objects.get_or_create(
            slug='default',
            defaults={
                'name': 'Kelly Phillipps Real Estate',
                'domain': 'goldfish-app-3hc23.ondigitalocean.app',
                'subscription_tier': 'pro',
                'max_properties': 1000,
                'max_users': 50
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Created tenant: {tenant.name}'))
        else:
            self.stdout.write(f'ℹ️  Using existing tenant: {tenant.name}')

        # Sample properties data
        properties_data = [
            {
                'title': 'Villa de Lujo Frente al Mar - Tamarindo',
                'description': 'Impresionante villa de 4 habitaciones con vista al océano Pacífico. Piscina infinity, cocina gourmet, acabados de lujo. A 2 minutos caminando de Playa Tamarindo. Ideal para inversión o residencia.',
                'price': Decimal('850000.00'),
                'currency': 'USD',
                'beds': 4,
                'baths': 3,
                'size_m2': Decimal('320.00'),
                'lot_m2': Decimal('800.00'),
                'location': 'Tamarindo, Guanacaste',
                'property_type': 'house',
                'status': 'sale',
                'amenities': ['piscina', 'vista al mar', 'jardín', 'garaje', 'aire acondicionado'],
                'source_url': 'https://example.com/tamarindo-villa',
            },
            {
                'title': 'Apartamento Moderno en San José Centro',
                'description': 'Apartamento de 2 habitaciones en edificio moderno. Ubicación céntrica, cerca de Avenida Escazú. Seguridad 24/7, gimnasio, piscina comunitaria. Perfecto para profesionales.',
                'price': Decimal('195000.00'),
                'currency': 'USD',
                'beds': 2,
                'baths': 2,
                'size_m2': Decimal('95.00'),
                'lot_m2': None,
                'location': 'San José Centro',
                'property_type': 'apartment',
                'status': 'sale',
                'amenities': ['piscina', 'gimnasio', 'seguridad 24/7', 'parqueo'],
                'source_url': 'https://example.com/sj-apartment',
            },
            {
                'title': 'Casa de Playa con Piscina - Jacó',
                'description': 'Hermosa casa de 3 habitaciones a 5 minutos de Playa Jacó. Piscina privada, rancho BBQ, jardín tropical. Zona tranquila, perfecta para familia o alquiler vacacional.',
                'price': Decimal('425000.00'),
                'currency': 'USD',
                'beds': 3,
                'baths': 2,
                'size_m2': Decimal('180.00'),
                'lot_m2': Decimal('500.00'),
                'location': 'Jacó, Puntarenas',
                'property_type': 'house',
                'status': 'sale',
                'amenities': ['piscina', 'jardín', 'BBQ', 'cerca de playa'],
                'source_url': 'https://example.com/jaco-beach-house',
            },
            {
                'title': 'Lote con Vista Panorámica - Manuel Antonio',
                'description': 'Terreno de 2,500 m² con vista espectacular al Océano Pacífico y Parque Nacional Manuel Antonio. Servicios públicos disponibles, acceso pavimentado. Ideal para desarrollo residencial.',
                'price': Decimal('280000.00'),
                'currency': 'USD',
                'beds': None,
                'baths': None,
                'size_m2': None,
                'lot_m2': Decimal('2500.00'),
                'location': 'Manuel Antonio, Puntarenas',
                'property_type': 'land',
                'status': 'sale',
                'amenities': ['vista al mar', 'servicios públicos', 'acceso pavimentado'],
                'source_url': 'https://example.com/manuel-antonio-lot',
            },
            {
                'title': 'Condominio Playero - Flamingo Beach',
                'description': 'Condo de 2 habitaciones en resort frente a Playa Flamingo. Totalmente amueblado, piscina infinity, restaurante, spa. Excelente para renta turística. ROI 8% anual.',
                'price': Decimal('385000.00'),
                'currency': 'USD',
                'beds': 2,
                'baths': 2,
                'size_m2': Decimal('110.00'),
                'lot_m2': None,
                'location': 'Playa Flamingo, Guanacaste',
                'property_type': 'apartment',
                'status': 'sale',
                'amenities': ['piscina', 'frente al mar', 'amueblado', 'spa', 'restaurante', 'seguridad'],
                'source_url': 'https://example.com/flamingo-condo',
            },
            {
                'title': 'Finca Cafetalera - Valle Central',
                'description': 'Propiedad agrícola de 5 hectáreas con plantación de café establecida. Casa principal de 3 habitaciones, bodega, beneficio. Producción anual de 50 quintales. Agua propia.',
                'price': Decimal('650000.00'),
                'currency': 'USD',
                'beds': 3,
                'baths': 2,
                'size_m2': Decimal('200.00'),
                'lot_m2': Decimal('50000.00'),
                'location': 'Grecia, Alajuela',
                'property_type': 'land',
                'status': 'sale',
                'amenities': ['agua propia', 'plantación café', 'bodega', 'producción activa'],
                'source_url': 'https://example.com/coffee-farm',
            },
            {
                'title': 'Villa de Lujo con Helipuerto - Papagayo',
                'description': 'Espectacular villa de 6 habitaciones en Peninsula Papagayo. 700 m² construcción, piscina infinity, helipuerto, cine privado. Staff quarters. Acabados importados de primera.',
                'price': Decimal('3500000.00'),
                'currency': 'USD',
                'beds': 6,
                'baths': 7,
                'size_m2': Decimal('700.00'),
                'lot_m2': Decimal('2000.00'),
                'location': 'Península Papagayo, Guanacaste',
                'property_type': 'house',
                'status': 'sale',
                'amenities': ['piscina', 'helipuerto', 'cine', 'vista al mar', 'staff quarters', 'gimnasio'],
                'source_url': 'https://example.com/papagayo-luxury-villa',
            },
            {
                'title': 'Apartamento para Inversión - Ciudad Colón',
                'description': 'Apartamento de 1 habitación en zona universitaria. Actualmente alquilado $450/mes. Edificio nuevo con amenidades. Perfecto para inversionista que busca renta mensual.',
                'price': Decimal('95000.00'),
                'currency': 'USD',
                'beds': 1,
                'baths': 1,
                'size_m2': Decimal('52.00'),
                'lot_m2': None,
                'location': 'Ciudad Colón, San José',
                'property_type': 'apartment',
                'status': 'sale',
                'amenities': ['parqueo', 'seguridad', 'alquilado'],
                'source_url': 'https://example.com/colon-investment',
            },
        ]

        # Create properties
        created_count = 0
        for prop_data in properties_data:
            property_obj, created = Property.objects.get_or_create(
                source_url=prop_data['source_url'],
                tenant=tenant,
                defaults=prop_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ Created: {property_obj.title[:60]}...')
                
                # Create document for RAG
                Document.objects.get_or_create(
                    property=property_obj,
                    defaults={
                        'content': f"{property_obj.title}\n\n{property_obj.description}\n\nPrecio: ${property_obj.price:,.0f} {property_obj.currency}\nUbicación: {property_obj.location}\nHabitaciones: {property_obj.beds or 'N/A'}\nBaños: {property_obj.baths or 'N/A'}\nÁrea: {property_obj.size_m2 or 'N/A'} m²",
                        'source_type': 'manual',
                        'tenant': tenant
                    }
                )
            else:
                self.stdout.write(f'  ℹ️  Already exists: {property_obj.title[:60]}...')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Seeding complete!'))
        self.stdout.write(f'   📊 Created {created_count} new properties')
        self.stdout.write(f'   📍 Total properties: {Property.objects.filter(tenant=tenant).count()}')
        self.stdout.write('')
        self.stdout.write('⚠️  IMPORTANT: Run embeddings generation next:')
        self.stdout.write('   python manage.py generate_embeddings')
