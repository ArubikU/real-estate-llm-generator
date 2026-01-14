# Solución al Problema de Storage del Service Account

## Problema Identificado

El error `storageQuotaExceeded` ocurre porque **los Service Accounts NO tienen espacio de almacenamiento en Google Drive**. No pueden crear archivos propios.

## Solución Temporal (Más Simple)

**Crear el Google Sheet manualmente** en tu cuenta personal y compartirlo con el service account:

### Pasos:

1. **Ve a Google Sheets**: https://sheets.google.com

2. **Crea un nuevo spreadsheet** con cualquier nombre (ej: "Propiedades Real Estate")

3. **Agrega los headers en la primera fila** (A1 a E1):
   ```
   URL de la propiedad | Tipo | Status | Fecha procesada | Notas
   ```

4. **Comparte el sheet con el service account**:
   - Clic en "Share" (Compartir) arriba a la derecha
   - Pegar este email: `property-ingestion-service@smart-arc-466414-p9.iam.gserviceaccount.com`
   - Rol: **Editor**
   - Desmarcar "Notify people" (no enviar notificación)
   - Clic en "Share"

5. **Copia el ID del spreadsheet** de la URL:
   ```
   https://docs.google.com/spreadsheets/d/1ABC123xyz.../edit
                                          ^^^^^^^^^^^^
                                          Este es el ID
   ```

6. **Usa ese ID para procesar el sheet** en la interfaz web:
   - Ve a http://localhost:5173/google-sheets
   - Panel "Procesar Google Sheet"
   - Pega el ID del spreadsheet
   - Ingresa tu email para notificaciones
   - Clic en "Procesar Sheet"

---

## Soluciones Permanentes

### Opción A: Domain-Wide Delegation (Para Google Workspace)

Si tienes Google Workspace (no cuenta gratuita):

1. Ve a: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Busca: `property-ingestion-service@smart-arc-466414-p9.iam.gserviceaccount.com`
3. Clic en los 3 puntos > "Manage details"
4. Pestaña "Advanced settings"
5. Marca "Enable Google Workspace Domain-wide Delegation"
6. Guarda

Luego en Admin Console de Google Workspace:
- Security > API Controls > Domain-wide Delegation
- Agregar Client ID con scopes

### Opción B: Usar OAuth 2.0 en lugar de Service Account

Cambiar a autenticación OAuth con cuenta de usuario real (más complejo, requiere flow de autorización).

### Opción C: Modificar el código para usar un Drive "compartido"

Crear un Google Drive compartido (Shared Drive) y dar acceso al service account.

---

## Recomendación

**USAR LA SOLUCIÓN TEMPORAL** es lo más práctico:
- ✅ Funciona inmediatamente
- ✅ No requiere configuración adicional
- ✅ Seguro (solo el service account tiene acceso)
- ✅ Fácil de implementar

El flujo sería:
1. Tú creas el sheet manualmente (1 vez)
2. Lo compartes con el service account
3. Agregas URLs en el sheet (columna A, filas 2+)
4. Marcas Status = "Pendiente" (columna C)
5. Usas la interfaz para procesar
6. El sistema actualiza automáticamente Status, Fecha, y Notas

