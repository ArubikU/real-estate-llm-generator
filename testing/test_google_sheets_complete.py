#!/usr/bin/env python
"""
Test script for Google Sheets integration with complete data saving.
Tests:
1. Reading pending rows
2. Ensuring headers exist
3. Updating rows with complete property data
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.ingestion.google_sheets import GoogleSheetsService

def test_google_sheets_integration():
    """Test complete Google Sheets workflow"""
    
    SPREADSHEET_ID = '1sBJvL_UIDULvZeycsm-PPk0V3_LEXM9fIrWh5osQVCc'
    
    print("=" * 80)
    print("🧪 TESTING GOOGLE SHEETS INTEGRATION")
    print("=" * 80)
    
    try:
        # Initialize service
        print("\n1️⃣ Initializing Google Sheets service...")
        service = GoogleSheetsService()
        print("   ✅ Service initialized successfully")
        
        # Test ensure headers
        print("\n2️⃣ Ensuring headers exist...")
        headers_ok = service.ensure_headers(SPREADSHEET_ID)
        if headers_ok:
            print("   ✅ Headers verified/created successfully")
        else:
            print("   ❌ Failed to ensure headers")
            return
        
        # Read pending rows
        print("\n3️⃣ Reading pending rows...")
        pending_rows = service.read_pending_rows(SPREADSHEET_ID)
        print(f"   📊 Found {len(pending_rows)} pending rows")
        
        if pending_rows:
            for row in pending_rows:
                print(f"      - Row {row['row_index']}: {row['url'][:60]}...")
        
        # Test update with complete property data
        print("\n4️⃣ Testing row update with property data...")
        test_property_data = {
            'price_usd': Decimal('933.65'),
            'bedrooms': 2,
            'bathrooms': Decimal('2'),
            'square_meters': Decimal('99'),
            'location': 'Cartago, El Guarco',
            'property_id': 'test-property-id-12345'
        }
        
        # Find a row to update (use first pending row or row 2)
        test_row = pending_rows[0]['row_index'] if pending_rows else 2
        
        print(f"   📝 Updating row {test_row} with test data...")
        print(f"      Precio: ${test_property_data['price_usd']}")
        print(f"      Habitaciones: {test_property_data['bedrooms']}")
        print(f"      Baños: {test_property_data['bathrooms']}")
        print(f"      M²: {test_property_data['square_meters']}")
        print(f"      Ubicación: {test_property_data['location']}")
        print(f"      Property ID: {test_property_data['property_id']}")
        
        update_success = service.update_row_status(
            spreadsheet_id=SPREADSHEET_ID,
            row_index=test_row,
            status='Procesado',
            notes='✅ Test completado exitosamente',
            property_data=test_property_data
        )
        
        if update_success:
            print(f"   ✅ Row {test_row} updated successfully with complete data!")
            print(f"\n   🔗 Check your sheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
            print(f"      Columns C-K should be filled with data")
        else:
            print(f"   ❌ Failed to update row {test_row}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Service initialization: OK")
        print(f"✅ Headers: OK")
        print(f"✅ Reading rows: OK ({len(pending_rows)} pending)")
        print(f"{'✅' if update_success else '❌'} Row update with data: {'OK' if update_success else 'FAILED'}")
        print("\n🎉 All tests completed!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_google_sheets_integration()
    sys.exit(0 if success else 1)
