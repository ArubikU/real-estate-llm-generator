"""
Test script for Encuentra24 extractor with AI enhancement.
Tests the URL: https://www.encuentra24.com/costa-rica-es/bienes-raices-proyectos-nuevos/venta-de-apartamento-en-jaco/31553057
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from core.scraping.scraper import scrape_url
from core.scraping.extractors import get_extractor
import json
from decimal import Decimal

def decimal_default(obj):
    """JSON serializer for Decimal objects."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def test_encuentra24_extraction():
    """Test Encuentra24 extractor with real URL."""
    
    url = "https://www.encuentra24.com/costa-rica-es/bienes-raices-proyectos-nuevos/venta-de-apartamento-en-jaco/31553057"
    
    print("=" * 80)
    print("🧪 TESTING ENCUENTRA24 EXTRACTOR")
    print("=" * 80)
    print(f"\n📍 URL: {url}\n")
    
    # Step 1: Scrape the URL
    print("🔧 Step 1: Scraping URL with Playwright...")
    try:
        scraped_data = scrape_url(url)
        print(f"✅ Scraping successful!")
        print(f"📊 HTML size: {len(scraped_data.get('html', ''))} characters")
        print(f"📄 Title: {scraped_data.get('title', 'N/A')}")
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return
    
    # Step 2: Get extractor and extract data
    print(f"\n🔧 Step 2: Getting extractor for encuentra24.com...")
    try:
        extractor = get_extractor(url)  # Pass full URL
        print(f"✅ Using extractor: {extractor.__class__.__name__}")
    except Exception as e:
        print(f"❌ Failed to get extractor: {e}")
        return
    
    # Step 3: Extract property data
    print("\n🔧 Step 3: Extracting property data...")
    try:
        extracted_data = extractor.extract(scraped_data['html'], url)
        print(f"✅ Extraction complete!")
        print(f"📊 Extracted {len(extracted_data)} fields\n")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Display results
    print("=" * 80)
    print("📋 EXTRACTED DATA")
    print("=" * 80)
    
    # Display each field
    fields_to_check = [
        ('title', 'Nombre de la Propiedad'),
        ('price_usd', 'Precio (USD)'),
        ('property_type', 'Tipo'),
        ('listing_type', 'Estado del Listado'),
        ('location', 'Ubicación'),
        ('bedrooms', 'Habitaciones'),
        ('bathrooms', 'Baños'),
        ('area_m2', 'Metros Cuadrados'),
        ('lot_size_m2', 'Tamaño del Lote (m²)'),
        ('parking_spaces', 'Espacios de Parking'),
        ('listing_id', 'ID de Listado'),
        ('date_listed', 'Fecha de Listado'),
        ('construction_stage', 'Etapa de Construcción'),
        ('description', 'Descripción'),
        ('amenities', 'Amenidades'),
        ('raw_details', 'Detalles Estructurados'),
    ]
    
    for field_key, field_label in fields_to_check:
        value = extracted_data.get(field_key)
        
        if value is None or value == '' or value == []:
            status = "❌ N/A"
            value_str = "N/A"
        elif isinstance(value, dict):
            status = "✅"
            value_str = json.dumps(value, indent=2, ensure_ascii=False, default=decimal_default)
        elif isinstance(value, list):
            status = "✅"
            if len(value) > 5:
                value_str = f"{len(value)} items: {', '.join(str(v) for v in value[:5])}..."
            else:
                value_str = ', '.join(str(v) for v in value)
        elif isinstance(value, str) and len(value) > 100:
            status = "✅"
            value_str = value[:100] + "..."
        else:
            status = "✅"
            value_str = str(value)
        
        print(f"\n{status} {field_label}:")
        print(f"   {value_str}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    total_fields = len(fields_to_check)
    filled_fields = sum(1 for field, _ in fields_to_check if extracted_data.get(field) not in [None, '', []])
    
    print(f"\n✅ Fields filled: {filled_fields}/{total_fields}")
    print(f"📈 Completion rate: {(filled_fields/total_fields*100):.1f}%")
    
    # Check AI enhancement
    if extracted_data.get('raw_details'):
        print("\n🤖 AI Enhancement: ACTIVE")
        print(f"   Structured details captured: {len(extracted_data.get('raw_details', {}))} fields")
    else:
        print("\n⚠️  AI Enhancement: NOT DETECTED")
    
    # Save full data to JSON file for inspection
    output_file = "test_encuentra24_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False, default=decimal_default)
    
    print(f"\n💾 Full data saved to: {output_file}")
    print("\n" + "=" * 80)
    print("🎉 TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_encuentra24_extraction()
