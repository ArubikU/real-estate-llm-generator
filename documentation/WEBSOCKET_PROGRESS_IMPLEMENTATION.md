# Sistema de Progreso en Tiempo Real - Google Sheets Integration

## 📋 Resumen de Cambios

Se implementó un sistema completo de progreso en tiempo real para el procesamiento de Google Sheets usando **WebSockets** para comunicación bidireccional entre el backend (Django/Channels) y el frontend (React).

---

## 🎯 Características Implementadas

### 1. **WebSocket Consumer (Backend)**
- ✅ Ya existente en `/backend/apps/ingestion/consumers.py`
- Maneja conexiones WebSocket en `ws://localhost:8000/ws/progress/<task_id>/`
- Envía eventos de progreso, completado y error en tiempo real

### 2. **Eventos de Progreso en Views (Backend)**
**Archivo:** `/backend/apps/ingestion/views.py`

Se actualizó `ProcessGoogleSheetView` para:
- Generar un `task_id` único (UUID) para cada procesamiento
- Enviar eventos WebSocket en cada etapa:
  - 🌐 **Scraping** - Al iniciar scraping de cada propiedad
  - 🤖 **Extracting** - Durante extracción con LLM
  - 💾 **Saving** - Al guardar en base de datos
  - ✅ **Completed** - Al completar cada propiedad
  - ❌ **Error** - En caso de fallo

**Eventos enviados:**
```python
{
    'type': 'progress_update',
    'progress': 50,  # 0-100%
    'status': 'scraping',
    'message': 'Scraping property 1/5...',
    'stage': 'scraping',
    'step': 1,
    'total_steps': 5,
    'url': 'https://...'
}
```

### 3. **Hook de Progreso (Frontend)**
**Archivo:** `/frontend/src/hooks/useProgress.ts`

Custom hook para conectar al WebSocket y recibir actualizaciones:

```typescript
const progressState = useProgress(taskId, {
  onComplete: (data) => console.log('✅ Completado'),
  onError: (error) => console.error('❌ Error'),
  onProgress: (data) => console.log('🔄 Progreso:', data.progress)
})
```

**Características:**
- Auto-reconexión (hasta 5 intentos con backoff exponencial)
- Manejo de estados: `isConnected`, `isComplete`, `hasError`
- Cleanup automático al desmontar componente

### 4. **Componente ProgressBar Mejorado (Frontend)**
**Archivo:** `/frontend/src/components/ProgressBar.tsx`

Se actualizó para soportar tanto el uso antiguo como el nuevo:
- Acepta `ProgressState` del hook
- Muestra barra de progreso animada con colores por etapa
- Indicadores visuales: 🌐 Scraping → 🤖 Extracting → 💾 Saving → ✅ Complete
- Muestra paso actual (ej: "Propiedad 2 de 5")
- Estado de conexión WebSocket en vivo

### 5. **Integración UI (Frontend)**
**Archivo:** `/frontend/src/components/GoogleSheetsIntegration.tsx`

Se integró el sistema de progreso:
- Inicializa WebSocket al iniciar procesamiento
- Muestra `<ProgressBar>` en tiempo real
- Callbacks para actualizar UI al completar/fallar

### 6. **Advertencia Google Workspace**
Se agregó un **banner amarillo** en la sección "Crear Nuevo Template":

```
⚠️ Requiere Google Workspace
La creación automática de Google Sheets requiere una cuenta de 
Google Workspace (pago).

💡 Alternativa: Si no tienes Google Workspace, crea el sheet 
manualmente y usa la sección "Procesar Sheet Existente".
```

---

## 🔄 Flujo de Datos

```
┌─────────────┐
│   Usuario   │
│  (Frontend) │
└──────┬──────┘
       │ 1. POST /ingest/google-sheet/
       │    { spreadsheet_id, notify_email }
       ▼
┌──────────────────┐
│   Django View    │ ◄─── Genera task_id (UUID)
│ (ProcessGoogle   │
│    SheetView)    │
└──────┬───────────┘
       │ 2. Retorna task_id al cliente
       │
       │ 3. Inicia procesamiento
       │    ┌─────────────┐
       │    │  For each   │
       │    │  property   │
       │    └──────┬──────┘
       │           │
       │           ├─► 🌐 Scraping
       │           │   └─► WebSocket: progress=25%
       │           │
       │           ├─► 🤖 Extracting
       │           │   └─► WebSocket: progress=50%
       │           │
       │           ├─► 💾 Saving
       │           │   └─► WebSocket: progress=75%
       │           │
       │           └─► ✅ Complete
       │               └─► WebSocket: progress=100%
       │
       ▼
┌──────────────────┐
│  Channels Layer  │ ◄─── Redis/In-Memory
│  (WebSocket Hub) │
└──────┬───────────┘
       │
       │ 4. Broadcast a grupo: progress_{task_id}
       │
       ▼
┌──────────────────┐
│ ProgressConsumer │
│   (WebSocket)    │
└──────┬───────────┘
       │
       │ 5. Envía JSON al cliente
       ▼
┌─────────────────┐
│  useProgress()  │ ◄─── Hook React
│     (Frontend)  │
└──────┬──────────┘
       │
       │ 6. Actualiza estado
       ▼
┌─────────────────┐
│  <ProgressBar>  │ ◄─── Componente UI
│   (Animated)    │
└─────────────────┘
```

---

## 📂 Archivos Modificados

### Backend
1. `/backend/apps/ingestion/views.py`
   - `ProcessGoogleSheetView.post()` - Añadido task_id y eventos WebSocket
   - `process_url()` callback - Añadidos parámetros `index` y `total`

2. `/backend/apps/ingestion/google_sheets.py`
   - `process_sheet_batch()` - Añadido parámetro `task_id`
   - Pasa `index` y `total_rows` al callback

3. `/backend/apps/ingestion/consumers.py`
   - ✅ Ya existente - No requiere cambios

### Frontend
1. `/frontend/src/hooks/useProgress.ts` ✨ **NUEVO**
   - Hook personalizado para WebSocket
   - Auto-reconexión y manejo de errores

2. `/frontend/src/components/ProgressBar.tsx`
   - Soporte para `ProgressState` del hook
   - Backward compatible con uso anterior

3. `/frontend/src/components/GoogleSheetsIntegration.tsx`
   - Importa `useProgress` y `ProgressBar`
   - Añadido estado `taskId`
   - Renderiza barra de progreso durante procesamiento
   - **⚠️ Banner de Google Workspace** en sección crear template

---

## 🚀 Cómo Funciona

### Ejemplo de Uso

1. **Usuario ingresa Google Sheet ID y email**
2. **Hace clic en "PROCESAR SHEET"**
3. **Frontend:**
   ```typescript
   const response = await fetch('/ingest/google-sheet/', {
     method: 'POST',
     body: JSON.stringify({ spreadsheet_id, notify_email })
   })
   const data = await response.json()
   setTaskId(data.task_id) // ← Inicia WebSocket
   ```

4. **useProgress hook se conecta automáticamente:**
   ```
   ws://localhost:8000/ws/progress/{task_id}/
   ```

5. **Backend procesa y envía eventos:**
   ```python
   # Scraping
   channel_layer.group_send(f'progress_{task_id}', {
       'type': 'progress_update',
       'progress': 25,
       'status': 'scraping',
       'message': 'Scraping property 1/3...'
   })
   
   # Extracting
   # ... progress: 50%
   
   # Saving
   # ... progress: 75%
   
   # Complete
   channel_layer.group_send(f'progress_{task_id}', {
       'type': 'task_complete',
       'message': 'All properties processed!'
   })
   ```

6. **Frontend actualiza UI en tiempo real:**
   ```tsx
   {isProcessing && taskId && (
     <ProgressBar progress={progressState} />
   )}
   ```

---

## 🎨 UI/UX

### Barra de Progreso
- **Color dinámico por etapa:**
  - 🔵 Azul: Scraping
  - 🟣 Morado: Extracting  
  - 🟢 Verde: Saving/Complete
  - 🔴 Rojo: Error

- **Animaciones:**
  - Barra con transición suave (`transition-all duration-500`)
  - Pulse durante procesamiento (`animate-pulse`)
  - Indicador de conexión (punto verde/gris)

- **Información mostrada:**
  - Porcentaje de progreso
  - Mensaje de estado actual
  - Paso actual (ej: "Propiedad 2 de 5")
  - Leyenda de etapas

### Banner de Advertencia
- **Diseño:** Fondo amarillo con borde, ícono de advertencia
- **Mensaje claro:** Explica limitación de Google Workspace
- **Alternativa:** Sugiere usar procesamiento manual

---

## ✅ Testing

### Test Manual
1. Abrir frontend: `http://localhost:5173/google-sheets`
2. Pegar spreadsheet ID: `1sBJvL_UIDULvZeycsm-PPk0V3_LEXM9fIrWh5osQVCc`
3. Ingresar email y hacer clic en "PROCESAR SHEET"
4. Observar barra de progreso actualizándose en tiempo real
5. Ver logs en consola del navegador:
   ```
   🔌 Connecting to WebSocket: ws://localhost:8000/ws/progress/{task_id}/
   ✅ WebSocket connected for task: abc-123
   📨 WebSocket message: { type: 'progress', progress: 25, ... }
   ```

### Verificar Backend
```bash
# Terminal 1: Django server
cd backend
python manage.py runserver

# Terminal 2: Ver logs
tail -f logs/django.log

# Deberías ver:
# 🔌 WebSocket connecting for task: abc-123
# 📨 Sending progress: 25% - Scraping property 1/3
```

---

## 🐛 Troubleshooting

### WebSocket no conecta
- ✅ Verificar que Django Channels esté configurado
- ✅ Revisar ASGI routing en `/backend/config/routing.py`
- ✅ Confirmar URL del WebSocket en `useProgress.ts`

### Progreso no se actualiza
- ✅ Verificar que `task_id` se esté pasando correctamente
- ✅ Revisar logs de backend para eventos `channel_layer.group_send`
- ✅ Inspeccionar consola del navegador para mensajes WebSocket

### CORS issues
- ✅ Asegurar que CORS permita WebSocket en settings
- ✅ Verificar protocolo (ws:// vs wss://)

---

## 🎉 Resultado Final

Un sistema completamente funcional de progreso en tiempo real que:
- ✅ Conecta BE ↔ FE via WebSockets
- ✅ Muestra progreso granular por propiedad
- ✅ Indica etapa actual (scraping/extracting/saving)
- ✅ Auto-reconexión ante fallas
- ✅ Advertencia clara de limitaciones de Google Workspace
- ✅ UI moderna con animaciones fluidas

**¡Listo para producción!** 🚀
