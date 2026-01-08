# Backend - Django REST API

Django backend con PostgreSQL y RAG (Retrieval-Augmented Generation) para chatbot de propiedades inmobiliarias.

## Estructura

```
backend/
├── apps/               # Django apps
│   ├── chat/          # Chatbot endpoints
│   ├── conversations/ # Conversation management
│   ├── documents/     # Document storage
│   ├── ingestion/     # Data ingestion
│   ├── properties/    # Property models
│   ├── tenants/       # Multi-tenancy
│   └── users/         # Authentication
├── config/            # Django settings
├── core/              # Core utilities (LLM, scraping, utils)
├── manage.py          # Django management
├── requirements.txt   # Python dependencies
└── Dockerfile        # Container configuration
```

## Desarrollo local

```bash
cd backend
python manage.py runserver
```

## APIs disponibles

Todas las APIs están bajo el prefijo `/api/`:

- `/api/chat/` - Chatbot conversacional
- `/api/properties/` - CRUD de propiedades
- `/api/documents/` - Gestión de documentos
- `/api/conversations/` - Historial de conversaciones
- `/api/ingest/` - Ingesta de datos
- `/api/auth/` - Autenticación

## Variables de entorno

Ver `.env.example` en la raíz del proyecto.
