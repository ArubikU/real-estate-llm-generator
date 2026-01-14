# Google Sheets Integration Guide

Esta guía explica cómo configurar y usar la integración con Google Sheets para procesamiento en lote de propiedades.

## 1. Configuración Inicial

### 1.1 Crear Cuenta de Servicio en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google Sheets:
   - Ve a "APIs & Services" > "Library"
   - Busca "Google Sheets API"
   - Click en "Enable"

4. Crear credenciales de cuenta de servicio:
   - Ve a "APIs & Services" > "Credentials"
   - Click en "Create Credentials" > "Service Account"
   - Nombre: `property-ingestion-service`
   - Role: `Editor` (o permisos personalizados)
   - Click en "Done"

5. Crear clave JSON:
   - Click en la cuenta de servicio creada
   - Ve a la pestaña "Keys"
   - Click "Add Key" > "Create new key"
   - Selecciona "JSON"
   - Guarda el archivo como `google-sheets-credentials.json`

### 1.2 Configurar el Backend

1. Coloca el archivo `google-sheets-credentials.json` en una ubicación segura:
   ```bash
   mkdir -p backend/credentials
   mv google-sheets-credentials.json backend/credentials/
   ```

2. Agrega la variable de entorno al archivo `.env`:
   ```env
   GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/backend/credentials/google-sheets-credentials.json
   ```

3. Instala las dependencias:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### 1.3 Configurar Email (para notificaciones)

Agrega las siguientes variables al archivo `.env`:

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-app
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

**Nota:** Para Gmail, necesitas crear una "App Password":
1. Ve a tu cuenta de Google > Seguridad
2. Activa la verificación en 2 pasos
3. Ve a "App passwords"
4. Genera una contraseña para "Mail"
5. Usa esa contraseña en `EMAIL_HOST_PASSWORD`

## 2. Crear Template de Google Sheet

### Opción A: Usando la API

```bash
curl -X POST http://localhost:8080/ingest/create-sheet-template/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Propiedades Enero 2026"
  }'
```

Respuesta:
```json
{
  "status": "success",
  "spreadsheet_id": "1abc123...",
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1abc123.../edit",
  "message": "Template created successfully"
}
```

### Opción B: Manual

1. Crea un nuevo Google Sheet
2. Agrega las siguientes columnas en la fila 1:
   - **A:** URL de la propiedad
   - **B:** Tipo (Propiedad/Tour/Restaurante/Info Local)
   - **C:** Status (Pendiente/Procesado/Error)
   - **D:** Fecha procesada
   - **E:** Notas

3. Comparte el sheet con la cuenta de servicio:
   - Copia el email de la cuenta de servicio (del archivo JSON: `client_email`)
   - Click en "Share" en el Google Sheet
   - Pega el email y dale permisos de "Editor"

## 3. Workflow de Uso

### 3.1 Preparar el Sheet

1. Abre tu Google Sheet
2. En la columna A, pega las URLs de las propiedades (una por línea)
3. En la columna B, especifica el tipo (opcional)
4. En la columna C, escribe "Pendiente" para cada URL

Ejemplo:
```
| URL de la propiedad                           | Tipo       | Status    | Fecha procesada | Notas |
|-----------------------------------------------|------------|-----------|-----------------|-------|
| https://encuentra24.com/property/123          | Propiedad  | Pendiente |                 |       |
| https://brevitas.com/listing/456              | Propiedad  | Pendiente |                 |       |
| https://coldwellbankercostarica.com/prop/789  | Propiedad  | Pendiente |                 |       |
```

### 3.2 Procesar el Sheet

**Procesamiento Asíncrono (Recomendado):**

```bash
curl -X POST http://localhost:8080/ingest/google-sheet/ \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "1abc123...",
    "notify_email": "asistente@example.com",
    "async": true
  }'
```

**Procesamiento Síncrono:**

```bash
curl -X POST http://localhost:8080/ingest/google-sheet/ \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "1abc123...",
    "notify_email": "asistente@example.com",
    "async": false
  }'
```

### 3.3 Monitorear Progreso

El script automáticamente:
1. ✅ Lee todas las filas con status "Pendiente"
2. ✅ Envía cada URL a la API de ingesta
3. ✅ Actualiza el status a "Procesado" o "Error"
4. ✅ Escribe la fecha y hora en la columna D
5. ✅ Agrega notas en la columna E (Property ID o mensaje de error)

### 3.4 Recibir Notificación

Cuando el proceso termina, recibirás un email con:
- ✅ Resumen: "Se procesaron 23 propiedades, 2 fallaron"
- ✅ Link al Google Sheet actualizado
- ✅ Link al admin panel para revisar las propiedades
- ✅ Detalles de errores (si los hay)

## 4. Ejemplo de Email de Notificación

```
Asunto: ✅ Batch completado: 23 propiedades procesadas exitosamente

Procesamiento de Batch Completado

Resumen de Resultados:
- Total de propiedades: 25
- Procesadas exitosamente: 23
- Fallidas: 2

Google Sheet actualizado: https://docs.google.com/spreadsheets/d/1abc.../edit
Admin Panel: http://localhost:8080/admin/properties/property/

⚠️ Atención: 2 propiedades no pudieron ser procesadas.

Próximos pasos:
• Revisa las propiedades procesadas en el admin panel
• Verifica que los datos extraídos sean correctos
• Corrige las URLs que fallaron y vuelve a procesarlas
```

## 5. API Endpoints

### 5.1 Crear Template

**POST** `/ingest/create-sheet-template/`

Request:
```json
{
  "title": "Propiedades Enero 2026"
}
```

Response:
```json
{
  "status": "success",
  "spreadsheet_id": "1abc123...",
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1abc123.../edit"
}
```

### 5.2 Procesar Sheet

**POST** `/ingest/google-sheet/`

Request:
```json
{
  "spreadsheet_id": "1abc123...",
  "notify_email": "asistente@example.com",
  "async": true
}
```

Response (async):
```json
{
  "status": "queued",
  "message": "Google Sheet processing queued",
  "task_id": "task-uuid",
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1abc123.../edit"
}
```

Response (sync):
```json
{
  "status": "completed",
  "total": 25,
  "processed": 23,
  "failed": 2,
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1abc123.../edit"
}
```

## 6. Troubleshooting

### Error: "Credentials not found"
- Verifica que `GOOGLE_SHEETS_CREDENTIALS_PATH` esté configurado en `.env`
- Verifica que el archivo JSON existe en la ruta especificada

### Error: "Permission denied"
- Asegúrate de compartir el sheet con la cuenta de servicio (email en el JSON)
- Verifica que la cuenta tiene permisos de "Editor"

### No recibo emails
- Verifica la configuración de email en `.env`
- Para Gmail, asegúrate de usar una "App Password"
- Revisa los logs del backend: `tail -f backend/logs/django.log`

### Propiedades no se procesan
- Verifica que el status sea exactamente "Pendiente" (case-insensitive)
- Verifica que las URLs sean válidas
- Revisa la columna "Notas" para ver mensajes de error específicos

## 7. Buenas Prácticas

1. **Organización:**
   - Crea un sheet diferente para cada lote o periodo
   - Usa nombres descriptivos: "Propiedades Enero 2026 - Lote 1"

2. **Preparación:**
   - Verifica que todas las URLs sean válidas antes de procesar
   - Usa el tipo correcto en la columna B

3. **Monitoreo:**
   - Revisa el sheet después de procesar
   - Corrige URLs con errores y vuelve a marcar como "Pendiente"

4. **Seguridad:**
   - No compartas las credenciales de la cuenta de servicio
   - Mantén el archivo JSON fuera del repositorio (usa `.gitignore`)

5. **Performance:**
   - Para lotes grandes (>50), usa procesamiento asíncrono
   - Divide lotes muy grandes en múltiples sheets

## 8. Automatización con Google Apps Script

Puedes agregar un script al Google Sheet para ejecutar el procesamiento con un botón:

```javascript
function procesarPropiedades() {
  const spreadsheetId = SpreadsheetApp.getActiveSpreadsheet().getId();
  const email = "asistente@example.com";
  
  const options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify({
      'spreadsheet_id': spreadsheet_id,
      'notify_email': email,
      'async': true
    })
  };
  
  const response = UrlFetchApp.fetch(
    'http://localhost:8080/ingest/google-sheet/',
    options
  );
  
  SpreadsheetApp.getUi().alert('¡Procesamiento iniciado! Recibirás un email cuando termine.');
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Propiedades')
    .addItem('Procesar Pendientes', 'procesarPropiedades')
    .addToUi();
}
```

Este script agrega un menú "Propiedades" con la opción "Procesar Pendientes".
