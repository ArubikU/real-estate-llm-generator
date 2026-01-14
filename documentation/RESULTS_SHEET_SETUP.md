# Configuración de Google Sheets - Crear Hojas de Resultados

## ⚠️ Limitación con Cuentas Personales

Con cuentas de Google **personales** (no Workspace), las service accounts **NO pueden crear archivos nuevos en Drive** debido a restricciones de permisos de Google.

## ✅ Solución Simple: Crear Template Manual

### Paso 1: Crear el Google Sheet de Resultados (Una sola vez)
1. Ve a https://sheets.google.com
2. Crea un nuevo Google Sheet
3. Nómbralo: **"Resultados Procesamiento - Template"**
4. Copia el **Spreadsheet ID** de la URL

### Paso 2: Agregar Headers
Copia y pega estos headers en la **fila 1** (A1:L1):
```
URL Original | Título Propiedad | Precio USD | Habitaciones | Baños | Área (m²) | Ubicación | Tipo Propiedad | Estado Procesamiento | Fecha Procesamiento | Notas | Property ID
```

### Paso 3: Compartir con la Service Account
1. Click en **"Compartir"** (botón azul arriba a la derecha)
2. Agrega este email con permisos de **Editor**:
   ```
   property-ingestion-service@smart-arc-466414-p9.iam.gserviceaccount.com
   ```
3. Click en **"Enviar"**

### Paso 4: Configurar en el Sistema
Agrega esta variable de entorno en tu backend:
```bash
# backend/.env
RESULTS_SPREADSHEET_ID=tu-spreadsheet-id-aqui
```

## Cómo Usar

### Opción A: Sheet Compartido (RECOMENDADO)
El sistema escribirá todos los resultados en el mismo sheet template:
- ✅ Todos los procesamientos en un solo lugar
- ✅ Fácil análisis histórico
- ✅ Sin límites de permisos
- ✅ Puedes crear pestañas para organizar por fecha

### Opción B: Clonar Manualmente
Para cada procesamiento, puedes clonar el template:
1. File → Make a copy
2. Compartir la copia con la service account
3. Pasar el nuevo ID al sistema

## Ventajas de Esta Solución
- ✅ **Funciona con cuentas personales** sin necesitar Workspace
- ✅ **Sin configuraciones complicadas** de Google Cloud
- ✅ **Todos los datos en un lugar** fácil de revisar
- ✅ **Puedes compartir** el sheet con otras personas
- ✅ **Formato profesional** con colores y estructura clara

## Estructura del Sheet de Resultados

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| URL Original | URL procesada | https://example.com/property/123 |
| Título Propiedad | Título extraído | Casa moderna en San José |
| Precio USD | Precio en dólares | $250,000.00 |
| Habitaciones | Número | 3 |
| Baños | Número | 2 |
| Área (m²) | Metros cuadrados | 120.5 |
| Ubicación | Ciudad/dirección | San José, Costa Rica |
| Tipo Propiedad | Tipo | Casa |
| Estado Procesamiento | Status | Procesado / Error |
| Fecha Procesamiento | Timestamp | 2026-01-13 12:30:45 |
| Notas | Detalles | Property ID: abc-123 |
| Property ID | UUID | a3afdbd3-9069-4a70... |

## Por Qué No Funciona la Creación Automática

Google Cloud Service Accounts con cuentas personales tienen estas limitaciones:
- ❌ No pueden crear archivos en tu Drive
- ❌ El scope `drive.file` solo funciona con archivos que ellas crean
- ❌ El scope `drive` completo requiere OAuth de usuario, no service account

La solución manual es **estándar** y usada por la mayoría de aplicaciones con cuentas personales.
