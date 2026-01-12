export type Language = 'es' | 'en';

export interface Translations {
  // Dashboard
  dashboard: {
    title: string;
    subtitle: string;
    dataCollector: string;
    dataCollectorDesc: string;
    properties: string;
    propertiesDesc: string;
    chatbot: string;
    chatbotDesc: string;
    access: string;
    backendStatus: string;
    connected: string;
  };
  
  // Header
  header: {
    logo: string;
    dataCollector: string;
    chatbot: string;
    properties: string;
  };
  
  // Sidebar
  sidebar: {
    savedProperties: string;
    organizedBy: string;
    noProperties: string;
    refresh: string;
    clearAll: string;
  };
  
  // Categories
  categories: {
    newProjects: string;
    housesForSale: string;
    apartmentsForSale: string;
    businessForSale: string;
    lotsLand: string;
    farmsForSale: string;
    housesForRent: string;
    apartmentsForRent: string;
    commercialForRent: string;
    other: string;
  };
  
  // PropertyList
  propertyList: {
    loading: string;
    title: string;
    subtitle: string;
    totalProperties: string;
    withEmbeddings: string;
    indexed: string;
    notIndexed: string;
    priceNotAvailable: string;
    suggestedQueries: string;
    howMuchCost: string;
    tellMeMore: string;
    thePropertyIn: string;
    thisProperty: string;
    chatbotTips: string;
    askLocations: string;
    useFilters: string;
    compareProperties: string;
    askAmenities: string;
    bedrooms: string;
    bathrooms: string;
    propertiesIn: string;
    housesWith: string;
    under: string;
    whatsDifference: string;
    between: string;
    and: string;
    withPool: string;
  };
  
  // DataCollector
  dataCollector: {
    title: string;
    subtitle: string;
    backToSearch: string;
    inputType: string;
    url: string;
    textHtml: string;
    sourceWebsite: string;
    loading: string;
    propertyUrl: string;
    propertyUrlPlaceholder: string;
    propertyText: string;
    propertyTextPlaceholder: string;
    processProperty: string;
    processing: string;
    connectedRealtime: string;
    scrapingFrom: string;
    propertiesProcessedToday: string;
    recentProperties: string;
    mayTake: string;
    extractedData: string;
    confidence: string;
    source: string;
    propertyName: string;
    listingId: string;
    listingStatus: string;
    price: string;
    type: string;
    location: string;
    bedrooms: string;
    bathrooms: string;
    squareMeters: string;
    lotSize: string;
    dateListed: string;
    status: string;
    description: string;
    viewOnMaps: string;
    saveToDatabase: string;
    editDetails: string;
    newProperty: string;
    extractionError: string;
    noPropertiesSaved: string;
    startProcessing: string;
    savedProperties: string;
    organizedBy: string;
    refresh: string;
    clearAllHistory: string;
    quickLinks: string;
    copyIndividualUrls: string;
    fastExtraction: string;
    aiPowered: string;
    duplicateDetected: string;
    alreadyExists: string;
    notSavedAgain: string;
    name: string;
    savedSuccessfully: string;
    propertyId: string;
    errorSaving: string;
    sureDeleteAll: string;
  };
  
  // Chatbot
  chatbot: {
    welcome: string;
    conversations: string;
    newChat: string;
    noConversations: string;
    messages: string;
    sources: string;
    relevance: string;
    placeholder: string;
    changeToSpanish: string;
    changeToEnglish: string;
    newConversation: string;
    exampleBeaches: string;
    exampleBedrooms: string;
    exampleLuxury: string;
    queryBeaches: string;
    queryBedrooms: string;
    queryLuxury: string;
  };
  
  // ErrorBoundary
  error: {
    somethingWrong: string;
    unexpectedError: string;
    reload: string;
  };
  
  // Common
  common: {
    na: string;
    yes: string;
    no: string;
    cancel: string;
    confirm: string;
    save: string;
    edit: string;
    delete: string;
    close: string;
    back: string;
  };
}

export const translations: Record<Language, Translations> = {
  es: {
    dashboard: {
      title: 'Plataforma KP Real Estate',
      subtitle: 'Sistema integral de gestión inmobiliaria con IA',
      dataCollector: 'Colector de Datos',
      dataCollectorDesc: 'Recolección y gestión de propiedades',
      properties: 'Propiedades',
      propertiesDesc: 'Ver propiedades indexadas',
      chatbot: 'Chatbot IA',
      chatbotDesc: 'Asistente virtual inmobiliario',
      access: 'Acceder',
      backendStatus: 'API Backend',
      connected: 'Conectado',
    },
    header: {
      logo: 'LLM Inmobiliario',
      dataCollector: 'Colector de Datos',
      chatbot: 'Chatbot',
      properties: 'Propiedades',
    },
    sidebar: {
      savedProperties: 'Propiedades Guardadas',
      organizedBy: 'Organizadas por categoría',
      noProperties: 'Aún no hay propiedades guardadas',
      refresh: 'Actualizar',
      clearAll: 'Borrar Todo el Historial',
    },
    categories: {
      newProjects: 'Proyectos Nuevos',
      housesForSale: 'Casas en Venta',
      apartmentsForSale: 'Apartamentos en Venta',
      businessForSale: 'Negocios en Venta',
      lotsLand: 'Lotes/Terrenos',
      farmsForSale: 'Fincas en Venta',
      housesForRent: 'Casas en Alquiler',
      apartmentsForRent: 'Apartamentos en Alquiler',
      commercialForRent: 'Locales Comerciales',
      other: 'Otros',
    },
    propertyList: {
      loading: 'Cargando propiedades...',
      title: 'Propiedades Indexadas',
      subtitle: 'Propiedades disponibles para consultas del chatbot',
      totalProperties: 'Total de Propiedades',
      withEmbeddings: 'Con Embeddings',
      indexed: 'Indexada',
      notIndexed: 'No indexada',
      priceNotAvailable: 'Precio no disponible',
      suggestedQueries: 'Consultas sugeridas:',
      howMuchCost: '¿Cuánto cuesta',
      tellMeMore: 'Cuéntame más sobre',
      thePropertyIn: 'la propiedad en',
      thisProperty: 'esta propiedad',
      chatbotTips: 'Consejos para el Chatbot',
      askLocations: 'Pregunta por ubicaciones específicas:',
      useFilters: 'Usa filtros:',
      compareProperties: 'Compara propiedades:',
      askAmenities: 'Pregunta sobre amenidades:',
      bedrooms: 'habitaciones',
      bathrooms: 'baños',
      propertiesIn: '¿Propiedades en',
      housesWith: 'Casas con',
      under: 'bajo',
      whatsDifference: '¿Cuál es la diferencia entre',
      between: 'entre',
      and: 'y',
      withPool: '¿Propiedades con piscina?',
    },
    dataCollector: {
      title: 'Colector de Datos de Propiedades',
      subtitle: 'Pega una URL o texto de propiedad para extraer automáticamente datos estructurados',
      backToSearch: 'Volver a la Búsqueda',
      inputType: 'Tipo de Entrada',
      url: 'URL',
      textHtml: 'Texto/HTML',
      sourceWebsite: 'Sitio Web de Origen',
      loading: 'Cargando...',
      propertyUrl: 'URL de la Propiedad',
      propertyUrlPlaceholder: 'https://encuentra24.com/property/...',
      propertyText: 'Texto/HTML de la Propiedad',
      propertyTextPlaceholder: 'Pega la descripción, HTML o texto de la propiedad aquí...',
      processProperty: 'Procesar Propiedad',
      processing: 'Procesando desde',
      connectedRealtime: 'Conectado en tiempo real',
      scrapingFrom: 'Extrayendo de',
      propertiesProcessedToday: 'Propiedades procesadas hoy',
      recentProperties: 'Últimas Propiedades Agregadas',
      mayTake: 'Esto puede tomar 10-30 segundos',
      extractedData: 'Datos Extraídos de la Propiedad',
      confidence: 'Confianza',
      source: 'Origen:',
      propertyName: 'Nombre de la Propiedad',
      listingId: 'ID de Listado',
      listingStatus: 'Estado del Listado',
      price: 'Precio (USD)',
      type: 'Tipo',
      location: 'Ubicación',
      bedrooms: 'Habitaciones',
      bathrooms: 'Baños',
      squareMeters: 'Metros Cuadrados',
      lotSize: 'Tamaño del Lote (m²)',
      dateListed: 'Fecha de Listado',
      status: 'Estado',
      description: 'Descripción',
      viewOnMaps: 'Ver en Google Maps',
      saveToDatabase: 'Guardar en Base de Datos',
      editDetails: 'Editar Detalles',
      newProperty: 'Nueva Propiedad',
      extractionError: '⚠️ Error de Extracción',
      noPropertiesSaved: 'Aún no hay propiedades guardadas',
      startProcessing: 'Comienza procesando una URL de propiedad',
      savedProperties: 'Propiedades Guardadas',
      organizedBy: 'Organizadas por categoría',
      refresh: 'Actualizar',
      clearAllHistory: 'Borrar Todo el Historial',
      quickLinks: 'Enlaces rápidos',
      copyIndividualUrls: 'Copia URLs de propiedades individuales (no páginas de búsqueda/listado).',
      fastExtraction: 'Extracción rápida (específica del sitio)',
      aiPowered: 'Extracción con IA',
      duplicateDetected: '⚠️ Propiedad Duplicada Detectada',
      alreadyExists: 'Esta propiedad ya existe en la base de datos:',
      notSavedAgain: 'La propiedad NO se guardó nuevamente.',
      name: 'Nombre:',
      savedSuccessfully: '✓ ¡Propiedad guardada exitosamente!',
      propertyId: 'ID de Propiedad:',
      errorSaving: 'Error al guardar la propiedad:',
      sureDeleteAll: '¿Estás seguro de que deseas eliminar todas las propiedades guardadas?',
    },
    chatbot: {
      welcome: `¡Hola! Soy tu asistente de Kelly Properties. Puedo ayudarte a encontrar la propiedad perfecta en Costa Rica. ¿Qué estás buscando?

Puedes preguntar sobre:
• Propiedades por ubicación (Tamarindo, Manuel Antonio, etc.)
• Filtros específicos (precio, habitaciones, amenidades)
• Información sobre una propiedad en particular`,
      conversations: 'Conversaciones',
      newChat: 'Nuevo Chat',
      noConversations: 'No hay conversaciones aún',
      messages: 'mensajes',
      sources: 'Fuentes consultadas:',
      relevance: 'relevancia',
      placeholder: 'Escribe tu pregunta aquí...',
      changeToSpanish: 'Cambiar a Español',
      changeToEnglish: 'Switch to English',
      newConversation: 'Nueva conversación',
      exampleBeaches: 'Playas',
      exampleBedrooms: '3 habitaciones',
      exampleLuxury: 'Lujo',
      queryBeaches: '¿Propiedades en Tamarindo?',
      queryBedrooms: 'Casas con 3 habitaciones bajo $300K',
      queryLuxury: '¿Propiedades de lujo con piscina?',
    },
    error: {
      somethingWrong: 'Algo salió mal',
      unexpectedError: 'Ocurrió un error inesperado',
      reload: 'Recargar Página',
    },
    common: {
      na: 'N/A',
      yes: 'Sí',
      no: 'No',
      cancel: 'Cancelar',
      confirm: 'Confirmar',
      save: 'Guardar',
      edit: 'Editar',
      delete: 'Eliminar',
      close: 'Cerrar',
      back: 'Volver',
    },
  },
  en: {
    dashboard: {
      title: 'KP Real Estate Platform',
      subtitle: 'Comprehensive AI-powered real estate management system',
      dataCollector: 'Data Collector',
      dataCollectorDesc: 'Property collection and management',
      properties: 'Properties',
      propertiesDesc: 'View indexed properties',
      chatbot: 'AI Chatbot',
      chatbotDesc: 'Virtual real estate assistant',
      access: 'Access',
      backendStatus: 'Backend API',
      connected: 'Connected',
    },
    header: {
      logo: 'Real Estate LLM',
      dataCollector: 'Data Collector',
      chatbot: 'Chatbot',
      properties: 'Properties',
    },
    sidebar: {
      savedProperties: 'Saved Properties',
      organizedBy: 'Organized by category',
      noProperties: 'No properties saved yet',
      refresh: 'Refresh',
      clearAll: 'Clear All History',
    },
    categories: {
      newProjects: 'New Projects',
      housesForSale: 'Houses for Sale',
      apartmentsForSale: 'Apartments for Sale',
      businessForSale: 'Businesses for Sale',
      lotsLand: 'Lots/Land',
      farmsForSale: 'Farms for Sale',
      housesForRent: 'Houses for Rent',
      apartmentsForRent: 'Apartments for Rent',
      commercialForRent: 'Commercial for Rent',
      other: 'Other',
    },
    propertyList: {
      loading: 'Loading properties...',
      title: 'Indexed Properties',
      subtitle: 'Properties available for chatbot queries',
      totalProperties: 'Total Properties',
      withEmbeddings: 'With Embeddings',
      indexed: 'Indexed',
      notIndexed: 'Not indexed',
      priceNotAvailable: 'Price not available',
      suggestedQueries: 'Suggested queries:',
      howMuchCost: 'How much does',
      tellMeMore: 'Tell me more about',
      thePropertyIn: 'the property in',
      thisProperty: 'this property',
      chatbotTips: 'Chatbot Tips',
      askLocations: 'Ask for specific locations:',
      useFilters: 'Use filters:',
      compareProperties: 'Compare properties:',
      askAmenities: 'Ask about amenities:',
      bedrooms: 'bedrooms',
      bathrooms: 'bathrooms',
      propertiesIn: 'Properties in',
      housesWith: 'Houses with',
      under: 'under',
      whatsDifference: "What's the difference between",
      between: 'between',
      and: 'and',
      withPool: 'Properties with pool?',
    },
    dataCollector: {
      title: 'Property Data Collector',
      subtitle: 'Paste a property URL or text to automatically extract structured data',
      backToSearch: 'Back to Search',
      inputType: 'Input Type',
      url: 'URL',
      textHtml: 'Text/HTML',
      sourceWebsite: 'Source Website',
      loading: 'Loading...',
      propertyUrl: 'Property URL',
      propertyUrlPlaceholder: 'https://encuentra24.com/property/...',
      propertyText: 'Property Text/HTML',
      propertyTextPlaceholder: 'Paste property description, HTML, or text here...',
      processProperty: 'Process Property',
      processing: 'Processing from',
      connectedRealtime: 'Connected in real-time',
      scrapingFrom: 'Extracting from',
      propertiesProcessedToday: 'Properties processed today',
      recentProperties: 'Recently Added Properties',
      mayTake: 'This may take 10-30 seconds',
      extractedData: 'Extracted Property Data',
      confidence: 'Confidence',
      source: 'Source:',
      propertyName: 'Property Name',
      listingId: 'Listing ID',
      listingStatus: 'Listing Status',
      price: 'Price (USD)',
      type: 'Type',
      location: 'Location',
      bedrooms: 'Bedrooms',
      bathrooms: 'Bathrooms',
      squareMeters: 'Square Meters',
      lotSize: 'Lot Size (m²)',
      dateListed: 'Date Listed',
      status: 'Status',
      description: 'Description',
      viewOnMaps: 'View on Google Maps',
      saveToDatabase: 'Save to Database',
      editDetails: 'Edit Details',
      newProperty: 'New Property',
      extractionError: '⚠️ Extraction Error',
      noPropertiesSaved: 'No properties saved yet',
      startProcessing: 'Start by processing a property URL',
      savedProperties: 'Saved Properties',
      organizedBy: 'Organized by category',
      refresh: 'Refresh',
      clearAllHistory: 'Clear All History',
      quickLinks: 'Quick links',
      copyIndividualUrls: 'Copy individual property URLs (not search/listing pages).',
      fastExtraction: 'Fast extraction (site-specific)',
      aiPowered: 'AI-powered extraction',
      duplicateDetected: '⚠️ Duplicate Property Detected',
      alreadyExists: 'This property already exists in the database:',
      notSavedAgain: 'The property was NOT saved again.',
      name: 'Name:',
      savedSuccessfully: '✓ Property saved successfully!',
      propertyId: 'Property ID:',
      errorSaving: 'Error saving property:',
      sureDeleteAll: 'Are you sure you want to delete all saved properties?',
    },
    chatbot: {
      welcome: `Hello! I'm your Kelly Properties assistant. I can help you find the perfect property in Costa Rica. What are you looking for?

You can ask about:
• Properties by location (Tamarindo, Manuel Antonio, etc.)
• Specific filters (price, bedrooms, amenities)
• Information about a particular property`,
      conversations: 'Conversations',
      newChat: 'New Chat',
      noConversations: 'No conversations yet',
      messages: 'messages',
      sources: 'Sources consulted:',
      relevance: 'relevance',
      placeholder: 'Type your question here...',
      changeToSpanish: 'Cambiar a Español',
      changeToEnglish: 'Switch to English',
      newConversation: 'New conversation',
      exampleBeaches: 'Beaches',
      exampleBedrooms: '3 bedrooms',
      exampleLuxury: 'Luxury',
      queryBeaches: 'Properties in Tamarindo?',
      queryBedrooms: 'Houses with 3 bedrooms under $300K',
      queryLuxury: 'Luxury properties with pool?',
    },
    error: {
      somethingWrong: 'Something went wrong',
      unexpectedError: 'An unexpected error occurred',
      reload: 'Reload Page',
    },
    common: {
      na: 'N/A',
      yes: 'Yes',
      no: 'No',
      cancel: 'Cancel',
      confirm: 'Confirm',
      save: 'Save',
      edit: 'Edit',
      delete: 'Delete',
      close: 'Close',
      back: 'Back',
    },
  },
};

export function getTranslation(lang: Language): Translations {
  return translations[lang];
}
