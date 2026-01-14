#!/usr/bin/env python
"""
Test script for Brevitas extractor with AI enhancement.
"""

import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from core.scraping.scraper import scrape_url
from core.scraping.extractors import get_extractor


def test_brevitas_extraction():
    """Test Brevitas extractor with real URL."""
    
    url = "https://brevitas.com/p/jjdasED/oceanfront-titled-property-with-direct-beach-access-main-house-guest-house-pool"
    
    print("=" * 80)
    print("🧪 TESTING BREVITAS EXTRACTOR")
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
    print(f"\n🔧 Step 2: Getting extractor for brevitas.com...")
    try:
        extractor = get_extractor(url)
        print(f"✅ Using extractor: {extractor.__class__.__name__}")
    except Exception as e:
        print(f"❌ Failed to get extractor: {e}")
        return
    
    # Step 3: Extract property data
    print("\n🔧 Step 3: Extracting property data...")
    try:
        extracted_data = extractor.extract(scraped_data['html'], url)
        print(f"✅ Extraction complete!")
        print(f"📊 Extracted {len(extracted_data)} fields")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print("\n" + "=" * 80)
    print("📋 EXTRACTED DATA")
    print("=" * 80)
    
    fields_to_show = [
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
        ('description', 'Descripción'),
        ('amenities', 'Amenidades'),
    ]
    
    filled_count = 0
    for field, label in fields_to_show:
        value = extracted_data.get(field)
        if value and value != 'N/A':
            filled_count += 1
            if field == 'amenities' and isinstance(value, list):
                print(f"\n✅ {label}:")
                if len(value) > 5:
                    print(f"   {len(value)} items: {', '.join(value[:5])}...")
                else:
                    print(f"   {', '.join(value)}")
            elif field == 'description' and len(str(value)) > 100:
                print(f"\n✅ {label}:")
                print(f"   {str(value)[:100]}...")
            else:
                print(f"\n✅ {label}:")
                print(f"   {value}")
        else:
            print(f"\n❌ N/A {label}:")
            print(f"   N/A")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"\n✅ Fields filled: {filled_count}/{len(fields_to_show)}")
    print(f"📈 Completion rate: {(filled_count/len(fields_to_show)*100):.1f}%")
    
    # Check if AI was used
    if extracted_data.get('description') and len(extracted_data.get('description', '')) > 200:
        print(f"\n✅ AI Enhancement: DETECTED")
    else:
        print(f"\n⚠️  AI Enhancement: NOT DETECTED")
    
    # Save to JSON
    output_file = 'test_brevitas_output.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Full data saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save to file: {e}")
    
    print("\n" + "=" * 80)
    print("🎉 TEST COMPLETED")
    print("=" * 80)


if __name__ == '__main__':
    test_brevitas_extraction()
