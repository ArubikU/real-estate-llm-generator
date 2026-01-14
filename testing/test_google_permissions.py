#!/usr/bin/env python
"""
Script de diagnóstico para verificar permisos de Google Sheets API
Revisa: credenciales, scopes, APIs habilitadas, y permisos IAM
"""
import os
import sys
import json
from pathlib import Path

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

def print_section(title):
    """Imprime un título de sección"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_credentials():
    """Test 1: Verificar que las credenciales existen y son válidas"""
    print_section("TEST 1: CREDENCIALES DE SERVICE ACCOUNT")
    
    try:
        credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
        print(f"✓ Path de credenciales: {credentials_path}")
        
        if not credentials_path:
            print("✗ ERROR: GOOGLE_SHEETS_CREDENTIALS_PATH no está configurado")
            return None
        
        if not os.path.exists(credentials_path):
            print(f"✗ ERROR: Archivo no existe: {credentials_path}")
            return None
        
        print(f"✓ Archivo de credenciales existe")
        
        # Leer el archivo JSON
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)
        
        print(f"✓ Archivo JSON válido")
        print(f"  - Tipo: {creds_data.get('type')}")
        print(f"  - Project ID: {creds_data.get('project_id')}")
        print(f"  - Client Email: {creds_data.get('client_email')}")
        print(f"  - Private Key ID: {creds_data.get('private_key_id', 'N/A')[:20]}...")
        
        return creds_data
        
    except json.JSONDecodeError as e:
        print(f"✗ ERROR: Archivo JSON inválido: {e}")
        return None
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return None

def test_scopes():
    """Test 2: Verificar los scopes necesarios"""
    print_section("TEST 2: SCOPES REQUERIDOS")
    
    required_scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    print("Scopes necesarios para crear y gestionar Google Sheets:")
    for scope in required_scopes:
        print(f"  ✓ {scope}")
    
    print("\nDescripción de permisos:")
    print("  • spreadsheets: Leer y escribir datos en Google Sheets")
    print("  • drive.file: Crear y gestionar archivos creados por la app en Drive")
    
    return required_scopes

def test_api_connection(creds_data, scopes):
    """Test 3: Intentar conectar con las APIs"""
    print_section("TEST 3: CONEXIÓN A GOOGLE APIS")
    
    try:
        credentials = service_account.Credentials.from_service_account_info(
            creds_data,
            scopes=scopes
        )
        print("✓ Credenciales cargadas correctamente")
        
        # Test Google Sheets API
        print("\nProbando Google Sheets API...")
        sheets_service = build('sheets', 'v4', credentials=credentials)
        print("✓ Servicio de Sheets construido correctamente")
        
        # Test Google Drive API
        print("\nProbando Google Drive API...")
        drive_service = build('drive', 'v3', credentials=credentials)
        print("✓ Servicio de Drive construido correctamente")
        
        return sheets_service, drive_service
        
    except Exception as e:
        print(f"✗ ERROR al construir servicios: {e}")
        return None, None

def test_sheets_create(sheets_service, drive_service):
    """Test 4: Intentar crear un spreadsheet de prueba"""
    print_section("TEST 4: CREAR SPREADSHEET DE PRUEBA")
    
    if not sheets_service:
        print("✗ No se puede realizar el test sin servicio de Sheets")
        return None
    
    try:
        test_title = f"TEST_PERMISOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"Intentando crear spreadsheet: {test_title}")
        
        spreadsheet = {
            'properties': {
                'title': test_title
            },
            'sheets': [
                {
                    'properties': {
                        'title': 'Test Sheet',
                        'gridProperties': {
                            'rowCount': 10,
                            'columnCount': 5
                        }
                    }
                }
            ]
        }
        
        result = sheets_service.spreadsheets().create(body=spreadsheet).execute()
        
        spreadsheet_id = result.get('spreadsheetId')
        spreadsheet_url = result.get('spreadsheetUrl')
        
        print(f"\n✓✓✓ ¡ÉXITO! Spreadsheet creado correctamente")
        print(f"  - ID: {spreadsheet_id}")
        print(f"  - URL: {spreadsheet_url}")
        
        return spreadsheet_id
        
    except HttpError as e:
        print(f"\n✗✗✗ ERROR HTTP {e.resp.status}: {e.error_details}")
        
        if e.resp.status == 403:
            print("\n🔴 ERROR 403: PERMISSION DENIED")
            print("\nPosibles causas:")
            print("  1. El Service Account NO tiene permisos IAM en el proyecto")
            print("  2. Las APIs NO están habilitadas")
            print("  3. Los scopes NO están correctamente configurados")
            
            print("\n📋 SOLUCIONES NECESARIAS:")
            print("\nA. Verificar APIs habilitadas en Google Cloud Console:")
            print("   https://console.cloud.google.com/apis/dashboard")
            print("   - Google Sheets API ✓ DEBE estar ENABLED")
            print("   - Google Drive API ✓ DEBE estar ENABLED")
            
            print("\nB. Otorgar permisos IAM al Service Account:")
            print("   1. Ir a: https://console.cloud.google.com/iam-admin/iam")
            print("   2. Buscar: property-ingestion-service@...")
            print("   3. Si NO aparece, hacer clic en 'Grant Access'")
            print("   4. En 'New principals': pegar el email del service account")
            print("   5. En 'Select a role': elegir uno de estos roles:")
            print("      • Editor (acceso amplio - recomendado para desarrollo)")
            print("      • Service Account User")
            print("      • Viewer + permisos específicos de Sheets/Drive")
            print("   6. Hacer clic en 'Save'")
            print("   7. ESPERAR 30-60 segundos para que se propaguen los permisos")
            
            print("\nC. Si usas Domain-Wide Delegation:")
            print("   - Ir a Admin Console de Google Workspace")
            print("   - Security > API Controls > Domain-wide Delegation")
            print("   - Agregar el Client ID con los scopes necesarios")
            
        elif e.resp.status == 404:
            print("\n🔴 ERROR 404: API NO ENCONTRADA")
            print("   - Verificar que Google Sheets API está habilitada")
            
        return None
        
    except Exception as e:
        print(f"\n✗ ERROR inesperado: {type(e).__name__}: {e}")
        return None

def test_drive_permissions(drive_service, spreadsheet_id):
    """Test 5: Verificar permisos del archivo creado"""
    print_section("TEST 5: VERIFICAR PERMISOS DEL ARCHIVO")
    
    if not drive_service or not spreadsheet_id:
        print("✗ No se puede verificar permisos (no hay spreadsheet creado)")
        return
    
    try:
        file_metadata = drive_service.files().get(
            fileId=spreadsheet_id,
            fields='id,name,owners,permissions,capabilities'
        ).execute()
        
        print(f"✓ Archivo recuperado: {file_metadata.get('name')}")
        print(f"\nOwners:")
        for owner in file_metadata.get('owners', []):
            print(f"  - {owner.get('emailAddress')}")
        
        print(f"\nCapabilities:")
        caps = file_metadata.get('capabilities', {})
        print(f"  - Can edit: {caps.get('canEdit')}")
        print(f"  - Can share: {caps.get('canShare')}")
        print(f"  - Can delete: {caps.get('canDelete')}")
        
    except HttpError as e:
        print(f"✗ ERROR al obtener info del archivo: {e}")
    except Exception as e:
        print(f"✗ ERROR: {e}")

def cleanup_test_file(sheets_service, drive_service, spreadsheet_id):
    """Test 6: Limpiar archivo de prueba"""
    print_section("TEST 6: LIMPIEZA")
    
    if not drive_service or not spreadsheet_id:
        print("No hay archivo para eliminar")
        return
    
    try:
        response = input(f"\n¿Eliminar el spreadsheet de prueba? (y/n): ")
        if response.lower() == 'y':
            drive_service.files().delete(fileId=spreadsheet_id).execute()
            print(f"✓ Archivo de prueba eliminado")
        else:
            print(f"✓ Archivo de prueba conservado para revisión manual")
            
    except HttpError as e:
        print(f"✗ ERROR al eliminar: {e}")
    except Exception as e:
        print(f"✗ ERROR: {e}")

def main():
    """Ejecuta todos los tests de diagnóstico"""
    print("\n" + "="*80)
    print(" 🔍 DIAGNÓSTICO DE PERMISOS GOOGLE SHEETS API")
    print("="*80)
    
    # Test 1: Credenciales
    creds_data = test_credentials()
    if not creds_data:
        print("\n❌ No se pueden ejecutar más tests sin credenciales válidas")
        return
    
    # Test 2: Scopes
    scopes = test_scopes()
    
    # Test 3: Conexión API
    sheets_service, drive_service = test_api_connection(creds_data, scopes)
    if not sheets_service:
        print("\n❌ No se pueden ejecutar más tests sin conexión a la API")
        return
    
    # Test 4: Crear spreadsheet
    spreadsheet_id = test_sheets_create(sheets_service, drive_service)
    
    # Test 5: Verificar permisos (solo si se creó el archivo)
    if spreadsheet_id:
        test_drive_permissions(drive_service, spreadsheet_id)
        
        # Test 6: Limpiar
        cleanup_test_file(sheets_service, drive_service, spreadsheet_id)
    
    # Resumen final
    print_section("RESUMEN")
    if spreadsheet_id:
        print("✅ TODOS LOS TESTS PASARON")
        print("   El Service Account tiene los permisos necesarios")
    else:
        print("❌ TESTS FALLARON")
        print("   Revisa los errores arriba y sigue las soluciones indicadas")
    
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
