#!/usr/bin/env python3
"""
Script de ejemplo para procesar propiedades desde Google Sheets.
Uso: python process_sheet.py <spreadsheet_id> <email>
"""

import sys
import requests
import json

def process_google_sheet(spreadsheet_id: str, notify_email: str, api_base: str = "http://localhost:8080"):
    """
    Procesar un Google Sheet con propiedades pendientes.
    
    Args:
        spreadsheet_id: ID del Google Sheet
        notify_email: Email para recibir notificación
        api_base: URL base de la API
    """
    
    url = f"{api_base}/ingest/google-sheet/"
    
    payload = {
        "spreadsheet_id": spreadsheet_id,
        "notify_email": notify_email,
        "async": True  # Procesamiento asíncrono
    }
    
    print(f"📊 Procesando Google Sheet...")
    print(f"📧 Notificación se enviará a: {notify_email}")
    print(f"🔗 Sheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
    print()
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('status') == 'queued':
            print("✅ ¡Procesamiento iniciado exitosamente!")
            print(f"📋 Task ID: {result.get('task_id')}")
            print(f"📊 Puedes ver el progreso en el sheet")
            print(f"📧 Recibirás un email cuando termine")
            return True
        else:
            print(f"⚠️  Estado inesperado: {result}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al procesar: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Detalle: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Respuesta: {e.response.text}")
        return False


def create_template(title: str = "Property Ingestion Template", api_base: str = "http://localhost:8080"):
    """
    Crear un nuevo Google Sheet template.
    
    Args:
        title: Título del nuevo sheet
        api_base: URL base de la API
    """
    
    url = f"{api_base}/ingest/create-sheet-template/"
    
    payload = {
        "title": title
    }
    
    print(f"📝 Creando nuevo template: {title}")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        print("✅ ¡Template creado exitosamente!")
        print(f"🆔 Spreadsheet ID: {result.get('spreadsheet_id')}")
        print(f"🔗 URL: {result.get('spreadsheet_url')}")
        print()
        print("📋 Próximos pasos:")
        print("1. Abre el link del sheet")
        print("2. Compártelo con la cuenta de servicio (si no lo hiciste)")
        print("3. Pega las URLs en la columna A")
        print("4. Escribe 'Pendiente' en la columna C")
        print("5. Ejecuta el procesamiento")
        
        return result.get('spreadsheet_id')
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al crear template: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Detalle: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Respuesta: {e.response.text}")
        return None


def main():
    """Función principal."""
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  Procesar sheet existente:")
        print("    python process_sheet.py <spreadsheet_id> <email>")
        print()
        print("  Crear nuevo template:")
        print("    python process_sheet.py --create-template \"Título del Sheet\"")
        print()
        print("Ejemplos:")
        print("  python process_sheet.py 1abc123xyz asistente@example.com")
        print("  python process_sheet.py --create-template \"Propiedades Enero 2026\"")
        sys.exit(1)
    
    if sys.argv[1] == "--create-template":
        title = sys.argv[2] if len(sys.argv) > 2 else "Property Ingestion Template"
        create_template(title)
    else:
        if len(sys.argv) < 3:
            print("❌ Error: Debes proporcionar spreadsheet_id y email")
            print("Uso: python process_sheet.py <spreadsheet_id> <email>")
            sys.exit(1)
        
        spreadsheet_id = sys.argv[1]
        email = sys.argv[2]
        
        process_google_sheet(spreadsheet_id, email)


if __name__ == "__main__":
    main()
