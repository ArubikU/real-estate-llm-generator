#!/usr/bin/env python
"""
Script detallado para diagnosticar permisos de Google Cloud
"""
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def check_project_and_apis():
    """Verifica el proyecto y las APIs habilitadas"""
    print("\n" + "="*80)
    print("VERIFICACIÓN DETALLADA DE CONFIGURACIÓN")
    print("="*80)
    
    credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
    
    with open(credentials_path, 'r') as f:
        creds_data = json.load(f)
    
    project_id = creds_data.get('project_id')
    client_email = creds_data.get('client_email')
    
    print(f"\n📋 Información del Service Account:")
    print(f"   Project ID: {project_id}")
    print(f"   Client Email: {client_email}")
    
    # Verificar APIs usando Service Usage API
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/cloud-platform.read-only'
    ]
    
    credentials = service_account.Credentials.from_service_account_info(
        creds_data, scopes=scopes
    )
    
    print("\n🔍 Intentando verificar APIs habilitadas...")
    try:
        service = build('serviceusage', 'v1', credentials=credentials)
        
        # Verificar Google Sheets API
        sheets_api_name = f"projects/{project_id}/services/sheets.googleapis.com"
        sheets_status = service.services().get(name=sheets_api_name).execute()
        print(f"   ✓ Google Sheets API: {sheets_status.get('state')}")
        
        # Verificar Google Drive API
        drive_api_name = f"projects/{project_id}/services/drive.googleapis.com"
        drive_status = service.services().get(name=drive_api_name).execute()
        print(f"   ✓ Google Drive API: {drive_status.get('state')}")
        
    except HttpError as e:
        if e.resp.status == 403:
            print(f"   ⚠️  No se puede verificar (necesita permisos adicionales)")
            print(f"   Verifica manualmente en:")
            print(f"   https://console.cloud.google.com/apis/dashboard?project={project_id}")
        else:
            print(f"   ✗ Error: {e}")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    # Probar con scope más específico para Drive
    print("\n🧪 TEST: Crear archivo en Drive con scope drive.file")
    try:
        drive_scopes = ['https://www.googleapis.com/auth/drive.file']
        drive_creds = service_account.Credentials.from_service_account_info(
            creds_data, scopes=drive_scopes
        )
        drive_service = build('drive', 'v3', credentials=drive_creds)
        
        # Intentar crear un archivo simple
        file_metadata = {
            'name': 'TEST_DRIVE_PERMISSIONS',
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        
        file = drive_service.files().create(body=file_metadata, fields='id,webViewLink').execute()
        file_id = file.get('id')
        file_url = file.get('webViewLink')
        
        print(f"   ✅ ÉXITO! Archivo creado en Drive")
        print(f"   ID: {file_id}")
        print(f"   URL: {file_url}")
        
        # Limpiar
        drive_service.files().delete(fileId=file_id).execute()
        print(f"   ✓ Archivo de prueba eliminado")
        
        return True
        
    except HttpError as e:
        print(f"   ❌ ERROR {e.resp.status}: {e.error_details}")
        
        if e.resp.status == 403:
            print("\n🔴 PROBLEMA IDENTIFICADO:")
            print("   El service account NO puede crear archivos en Google Drive")
            print("\n💡 POSIBLES SOLUCIONES:")
            print("\n   OPCIÓN 1 - Habilitar Domain-Wide Delegation:")
            print("   1. Ve a: https://console.cloud.google.com/iam-admin/serviceaccounts")
            print(f"   2. Busca: {client_email}")
            print("   3. Haz clic en los 3 puntos > 'Manage details'")
            print("   4. En la pestaña 'Advanced settings':")
            print("   5. Marca 'Enable Google Workspace Domain-wide Delegation'")
            print("   6. Guarda los cambios")
            print("\n   OPCIÓN 2 - Usar una cuenta de usuario (OAuth):")
            print("   En lugar de service account, usar OAuth con cuenta de Google personal")
            print("\n   OPCIÓN 3 - Crear sheets y compartirlos manualmente:")
            print("   El service account puede leer/escribir sheets que le compartas")
            
        return False
        
    except Exception as e:
        print(f"   ✗ Error inesperado: {e}")
        return False

if __name__ == '__main__':
    check_project_and_apis()
