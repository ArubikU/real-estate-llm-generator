# Análisis de Estructura HTML - Coldwell Banker Costa Rica
## URL Analizada
https://www.coldwellbankercostarica.com/property/land-for-sale-in-la-fortuna/12381

## Información Extraída por el Sistema Actual

### ✅ Datos Exitosamente Extraídos
- **Título**: "Stunning Volcano & Lake View Property Prime Investment with Unlimited Potential"
- **Precio**: $1,500,000 USD
- **Habitaciones**: 2
- **Baños**: 2
- **Imágenes**: 59 imágenes encontradas

### ⚠️ Datos Faltantes o con Problemas
- **Descripción**: `None` (NULL) - **PROBLEMA PRINCIPAL**
- **Área (m²)**: No encontrada
- **Tamaño del Lote (m²)**: No encontrada
- **Ubicación**: No encontrada
- **Coordenadas GPS**: No encontradas

## Estructura HTML de la Página

### 1. Título (H1)
```html
<h1>Stunning Volcano & Lake View Property Prime Investment with Unlimited Potential</h1>
```
- ✅ Se extrae correctamente

### 2. Meta Tags
```html
<meta name="description" content="Stunning Volcano & Lake View Property...">
<meta name="twitter:description" content="...">
```
- 📝 Puede usarse como fallback para la descripción

### 3. Clases CSS Comunes Encontradas
Las clases más frecuentes en la página:
- `.col-md-*` (91+ ocurrencias) - Sistema de grid
- `.col-6` (35 ocurrencias)
- `.form-control` - Campos de formulario
- `.row` - Contenedores
- `.btn` - Botones
- `.modal-*` - Modales
- `.f-*` - Elementos featured
- `.property-*` - Elementos relacionados con propiedades

### 4. Secciones de Datos Clave

#### Precio
- **Ubicación**: Dentro de `.title-wrap` o similar
- **Formato**: `$1,500,000` o `$1.500.000`
- **Patrón regex**: `\$\s*([\d,]+)`

#### Descripción de Propiedad
```html
<div class="property-description">
  [Texto descriptivo de la propiedad]
</div>
```
- 🔴 **PROBLEMA**: No se está extrayendo correctamente
- Puede tener contenido dentro de `<p>` o `<div>` anidados

#### Especificaciones
```html
<ul class="ul-specs">
  <li>Bedrooms: 2</li>
  <li>Bathrooms: 2</li>
  <li>Area: XXX m²</li>
</ul>
```

#### Características/Amenidades
```html
<div class="property-features">
  <ul>
    <li>Piscina</li>
    <li>Garage</li>
    <li>Jardín</li>
  </ul>
</div>
```

### 5. Mapa y Ubicación
```html
<iframe src="https://www.google.com/maps/embed?...pb=!1m3!2m1!1s10.01608,-84.21374!6i15">
</iframe>
```
- **Coordenadas encontradas**: 10.01608, -84.21374
- **Formato**: En el parámetro `pb=` del iframe

### 6. Imágenes
- **Total encontradas**: 59 imágenes
- **Formatos**:
  - `https://www.coldwellbankercostarica.com/assets/demo2/images/...`
  - `https://img.coldwellbankercostarica.com/...`
- Incluye logos, iconos y fotos de la propiedad

## Recomendaciones para Mejorar el Extractor

### 1. Arreglar Extracción de Descripción ✅ PRIORITARIO
```python
def extract_description(self, soup: BeautifulSoup) -> Optional[str]:
    # Intentar múltiples selectores
    selectors = [
        ('div', 'property-description'),
        ('div', 'description'),
        ('div', 'property-details'),
        ('section', 'property-info'),
    ]
    
    for tag, class_name in selectors:
        desc = soup.find(tag, class_=class_name)
        if desc:
            return desc.get_text(separator='\n', strip=True)
    
    # Fallback: usar meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        return meta_desc.get('content', '').strip()
    
    return None
```

### 2. Extraer Coordenadas del Mapa
```python
def extract_coordinates_from_iframe(self, soup: BeautifulSoup):
    # Buscar iframe de Google Maps
    iframe = soup.find('iframe', src=lambda x: x and 'google.com/maps' in x)
    if iframe:
        src = iframe.get('src', '')
        # Extraer del parámetro pb=
        match = re.search(r'!1s([-\d.]+),([-\d.]+)', src)
        if match:
            return Decimal(match.group(1)), Decimal(match.group(2))
    return None, None
```

### 3. Extraer Área/Lote
```python
def extract_lot_area(self, soup: BeautifulSoup):
    # Buscar en specs
    specs = soup.find('ul', class_='ul-specs')
    if specs:
        text = specs.get_text()
        # Buscar "Lot Size: XXX m²" o "Terreno: XXX m²"
        match = re.search(r'(lot|terreno|lote)[:\s]+([\d,]+\.?\d*)\s*(m[²2]|sq\s*ft)', text, re.IGNORECASE)
        if match:
            value_str = match.group(2).replace(',', '')
            value = Decimal(value_str)
            # Convertir sq ft a m2 si es necesario
            if 'ft' in match.group(3).lower():
                value = value * Decimal('0.092903')
            return value
    return None
```

### 4. Mejorar Extracción de Ubicación
```python
def extract_location(self, soup: BeautifulSoup):
    # 1. Buscar en section de ubicación
    location_wrap = soup.find('div', class_='location-wrap')
    if location_wrap:
        paragraphs = location_wrap.find_all('p')
        if paragraphs:
            return paragraphs[0].get_text(strip=True)
    
    # 2. Buscar en breadcrumbs
    breadcrumb = soup.find('nav', class_='breadcrumb')
    if breadcrumb:
        items = breadcrumb.find_all('li')
        if len(items) > 2:  # Excluir Home y Property Type
            return items[-1].get_text(strip=True)
    
    # 3. Buscar en h2 o subtitle
    subtitle = soup.find('h2', class_='property-subtitle')
    if subtitle:
        return subtitle.get_text(strip=True)
    
    return None
```

## Campos Disponibles en Coldwell Banker

### ✅ Campos que SE PUEDEN Extraer:
1. **Título** ✓
2. **Precio** ✓
3. **Habitaciones** ✓
4. **Baños** ✓
5. **Descripción** (necesita fix)
6. **Imágenes** ✓
7. **Coordenadas GPS** (del iframe de mapa)
8. **Ubicación/Dirección** (de varios lugares)
9. **Área construida** (de specs)
10. **Tamaño del lote** (de specs)
11. **Amenidades/Características** (de property-features)
12. **Tipo de propiedad** (Casa, Apartamento, Terreno, etc.)
13. **Agente** (nombre, teléfono, email)
14. **ID de propiedad** (de la URL: 12381)

### ❌ Campos que NO están disponibles:
1. Año de construcción (raro encontrarlo)
2. Espacios de parqueo (a veces en amenidades)
3. Estado del inmueble (Nuevo, Usado, etc.)

## Estado Actual del Extractor

### Funciona Bien:
- ✅ Precio
- ✅ Título
- ✅ Habitaciones
- ✅ Baños
- ✅ Imágenes

### Necesita Mejoras:
- 🔴 Descripción (retorna None)
- 🟡 Coordenadas GPS
- 🟡 Ubicación/Dirección
- 🟡 Área/Lote
- 🟡 Amenidades

## Siguiente Paso

Actualizar el archivo:
`/backend/core/scraping/extractors/coldwell_banker.py`

Con las mejoras sugeridas arriba para extraer todos los campos disponibles.
