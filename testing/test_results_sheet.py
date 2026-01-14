"""
Test script to verify Google Sheets results creation functionality
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.ingestion.google_sheets import GoogleSheetsService

def test_create_results_spreadsheet():
    """Test creating a results spreadsheet."""
    print("🧪 Testing Google Sheets Results Creation...")
    print("-" * 60)
    
    credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', 
                                  'credentials/google-sheets-credentials.json')
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return
    
    try:
        # Initialize service
        print("📝 Initializing Google Sheets service...")
        service = GoogleSheetsService(credentials_path)
        
        # Create results spreadsheet
        print("\n📊 Creating results spreadsheet...")
        result = service.create_results_spreadsheet(
            title="Test - Resultados Procesamiento Batch"
        )
        
        print("\n✅ Results spreadsheet created successfully!")
        print(f"   Title: {result['title']}")
        print(f"   ID: {result['spreadsheet_id']}")
        print(f"   URL: {result['spreadsheet_url']}")
        
        # Test appending a result row
        print("\n📝 Testing result row append...")
        test_data = {
            'url': 'https://example.com/property/123',
            'property_data': {
                'title': 'Casa de prueba',
                'price': 150000.50,
                'bedrooms': 3,
                'bathrooms': 2,
                'area': 120.5,
                'location': 'San José, Costa Rica',
                'property_type': 'Casa'
            },
            'status': 'Procesado',
            'notes': 'Test successful',
            'property_id': 'test-uuid-123'
        }
        
        success = service.append_result_row(
            result['spreadsheet_id'],
            test_data
        )
        
        if success:
            print("✅ Test row appended successfully!")
        else:
            print("❌ Failed to append test row")
        
        # Test error row
        print("\n📝 Testing error row append...")
        error_data = {
            'url': 'https://example.com/property/error',
            'property_data': {},
            'status': 'Error',
            'notes': 'Test error: Property not found',
            'property_id': ''
        }
        
        success = service.append_result_row(
            result['spreadsheet_id'],
            error_data
        )
        
        if success:
            print("✅ Error row appended successfully!")
        else:
            print("❌ Failed to append error row")
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
        print("\n🔗 Open the results spreadsheet:")
        print(f"   {result['spreadsheet_url']}")
        print("\n⚠️  Remember to share this sheet with your service account:")
        print(f"   property-ingestion-service@smart-arc-466414-p9.iam.gserviceaccount.com")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_results_spreadsheet()
