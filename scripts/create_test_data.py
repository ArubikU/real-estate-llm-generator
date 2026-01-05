"""
Script to create test data for development.
"""

from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant
from apps.properties.models import Property, PropertyType, PropertyStatus
from apps.documents.models import Document, ContentType
from decimal import Decimal
from datetime import date

User = get_user_model()


def create_test_data():
    """Create test tenant, users, properties, and documents."""
    
    print("Creating test data...")
    
    # Create tenant
    tenant, created = Tenant.objects.get_or_create(
        slug='kelly-properties',
        defaults={
            'name': 'Kelly Phillipps Real Estate',
            'domain': 'https://kelly-properties.com',
            'subscription_tier': 'pro',
            'max_properties': 500,
            'max_users': 50
        }
    )
    
    if created:
        print(f"✓ Created tenant: {tenant.name}")
    else:
        print(f"✓ Tenant already exists: {tenant.name}")
    
    # Create test users
    users_data = [
        {
            'username': 'john_buyer',
            'email': 'john@example.com',
            'password': 'testpass123',
            'role': 'buyer',
            'first_name': 'John',
            'last_name': 'Investor'
        },
        {
            'username': 'sarah_tourist',
            'email': 'sarah@example.com',
            'password': 'testpass123',
            'role': 'tourist',
            'first_name': 'Sarah',
            'last_name': 'Guest'
        },
        {
            'username': 'mike_staff',
            'email': 'mike@example.com',
            'password': 'testpass123',
            'role': 'staff',
            'first_name': 'Mike',
            'last_name': 'Manager'
        }
    ]
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                **user_data,
                'tenant': tenant
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"✓ Created user: {user.username} ({user.role})")
        else:
            print(f"✓ User already exists: {user.username}")
    
    # Create test properties
    properties_data = [
        {
            'property_name': 'Villa Mar - Luxury Beachfront',
            'price_usd': Decimal('450000'),
            'bedrooms': 3,
            'bathrooms': Decimal('2.5'),
            'property_type': PropertyType.VILLA,
            'location': 'Tamarindo, Guanacaste',
            'description': 'Stunning beachfront villa with panoramic ocean views. Features modern architecture, infinity pool, and direct beach access.',
            'square_meters': Decimal('250'),
            'lot_size_m2': Decimal('800'),
            'amenities': ['pool', 'ocean view', 'air conditioning', 'modern kitchen'],
            'status': PropertyStatus.AVAILABLE,
            'user_roles': ['buyer', 'staff', 'admin']
        },
        {
            'property_name': 'Casa Verde - Jungle Retreat',
            'price_usd': Decimal('280000'),
            'bedrooms': 2,
            'bathrooms': Decimal('2'),
            'property_type': PropertyType.HOUSE,
            'location': 'Manuel Antonio',
            'description': 'Peaceful jungle house with wildlife sightings. Eco-friendly design with solar panels and rainwater collection.',
            'square_meters': Decimal('180'),
            'amenities': ['solar panels', 'jungle view', 'garden'],
            'status': PropertyStatus.AVAILABLE,
            'user_roles': ['buyer', 'staff', 'admin']
        },
        {
            'property_name': 'Condo Pacifico - Downtown Living',
            'price_usd': Decimal('195000'),
            'bedrooms': 1,
            'bathrooms': Decimal('1'),
            'property_type': PropertyType.CONDO,
            'location': 'San José',
            'description': 'Modern condo in the heart of San José. Walking distance to restaurants, shops, and entertainment.',
            'square_meters': Decimal('85'),
            'amenities': ['gym', 'security', 'parking'],
            'status': PropertyStatus.AVAILABLE,
            'user_roles': ['buyer', 'staff', 'admin']
        }
    ]
    
    for prop_data in properties_data:
        prop, created = Property.objects.get_or_create(
            property_name=prop_data['property_name'],
            tenant=tenant,
            defaults=prop_data
        )
        
        if created:
            print(f"✓ Created property: {prop.property_name}")
        else:
            print(f"✓ Property already exists: {prop.property_name}")
    
    # Create test documents
    documents_data = [
        {
            'content': 'Tamarindo is one of Costa Rica\'s most popular beach towns, known for excellent surfing, vibrant nightlife, and growing real estate market. Average property appreciation: 8-12% annually.',
            'content_type': ContentType.MARKET,
            'user_roles': ['buyer', 'staff', 'admin'],
            'freshness_date': date(2024, 1, 1),
            'source_reference': 'Market Analysis Q1 2024'
        },
        {
            'content': 'Foreign buyers in Costa Rica can own property directly. Title transfer requires a lawyer, notary, and registration in the National Registry. Typical closing costs: 4-5% of purchase price.',
            'content_type': ContentType.LEGAL,
            'user_roles': ['buyer', 'staff', 'admin'],
            'freshness_date': date(2024, 1, 1),
            'source_reference': 'Legal Guide for Foreign Buyers'
        },
        {
            'content': 'Best restaurants in Tamarindo: Pangas Beach Club (upscale seafood), Seasons by Shlomy (Mediterranean), Nogi\'s (sushi), Dragonfly Bar & Grill (fusion). Reserve in advance during high season.',
            'content_type': ContentType.RESTAURANT,
            'user_roles': ['tourist', 'staff', 'admin'],
            'freshness_date': date(2024, 1, 1),
            'source_reference': 'Tamarindo Dining Guide'
        },
        {
            'content': 'Popular activities in Tamarindo: Surf lessons ($50-75), zip-lining ($85), catamaran sunset cruise ($80), ATV tours ($120), snorkeling trips ($65). Book through reputable operators.',
            'content_type': ContentType.ACTIVITY,
            'user_roles': ['tourist', 'staff', 'admin'],
            'freshness_date': date(2024, 1, 1),
            'source_reference': 'Activities Guide'
        }
    ]
    
    for doc_data in documents_data:
        doc, created = Document.objects.get_or_create(
            content=doc_data['content'],
            tenant=tenant,
            defaults=doc_data
        )
        
        if created:
            print(f"✓ Created document: {doc.get_content_type_display()}")
        else:
            print(f"✓ Document already exists: {doc.get_content_type_display()}")
    
    print("\n✅ Test data creation complete!")
    print(f"\nTest Credentials:")
    print(f"  Buyer: john_buyer / testpass123")
    print(f"  Tourist: sarah_tourist / testpass123")
    print(f"  Staff: mike_staff / testpass123")


if __name__ == '__main__':
    create_test_data()
