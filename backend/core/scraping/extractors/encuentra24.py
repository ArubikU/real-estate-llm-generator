"""Encuentra24.com specific extractor.
"""

from typing import Optional
from bs4 import BeautifulSoup
from decimal import Decimal
import re
import json
import openai
from django.conf import settings
from .base import BaseExtractor


class Encuentra24Extractor(BaseExtractor):
    """Extractor for encuentra24.com listings."""
    
    def __init__(self):
        super().__init__()
        self.site_name = "encuentra24.com"
    
    def extract(self, html: str, url: Optional[str] = None):
        """Override extract to include custom fields and AI enhancement."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract ALL relevant text from page (clean, no HTML tags)
        full_text = self.extract_all_text(soup)
        print(f"📝 Texto limpio extraído: {len(full_text)} caracteres (vs {len(html)} chars HTML)")
        
        # Extract construction stage from timeline
        construction_stage = self.extract_construction_stage(soup)
        
        # Use AI to process ALL the text and extract fields
        ai_enhanced_data = self.enhance_with_ai(full_text, construction_stage)
        
        # Call parent extract
        data = super().extract(html, url)
        
        # Merge AI-enhanced data (AI data takes precedence)
        data.update(ai_enhanced_data)
        
        # Add custom fields
        data['listing_id'] = self.extract_listing_id(soup)
        data['date_listed'] = self.extract_date_listed(soup)
        data['construction_stage'] = construction_stage
        
        return data
    
    def extract_structured_details(self, soup: BeautifulSoup) -> dict:
        """Extract all details from d3-property-details__content section."""
        details = {}
        
        # Find the content section
        content_div = soup.find('div', class_='d3-property-details__content')
        if not content_div:
            return details
        
        # Extract all label-detail pairs
        labels = content_div.find_all('div', class_='d3-property-details__detail-label')
        
        for label_div in labels:
            label_text = label_div.get_text(strip=True)
            detail_p = label_div.find('p', class_='d3-property-details__detail')
            
            if detail_p:
                detail_text = detail_p.get_text(strip=True)
                
                # Parse different fields
                if 'Categoria' in label_text or 'Categoría' in label_text:
                    details['category'] = detail_text
                elif 'Localización' in label_text or 'Ubicación' in label_text:
                    details['location'] = detail_text
                elif 'Modelo' in label_text:
                    details['model'] = detail_text
                elif 'Precio' in label_text and 'M²' not in label_text:
                    # Remove quotes and parse price
                    price_clean = detail_text.replace("'", "").replace(",", "").strip()
                    details['price_text'] = price_clean
                    try:
                        details['price'] = int(re.sub(r'[^\d]', '', price_clean))
                    except:
                        pass
                elif 'Precio / m²' in label_text or 'Precio / M²' in label_text:
                    details['price_per_sqm'] = detail_text
                elif 'M²' in label_text and 'Precio' not in label_text:
                    details['area_m2'] = detail_text
                elif 'Recámara' in label_text or 'Recamara' in label_text:
                    try:
                        details['bedrooms'] = int(detail_text)
                    except:
                        details['bedrooms'] = detail_text
                elif 'Baño' in label_text:
                    try:
                        details['bathrooms'] = int(detail_text)
                    except:
                        details['bathrooms'] = detail_text
                elif 'Parking' in label_text:
                    details['parking'] = detail_text
                elif 'Piscina' in label_text:
                    details['pool'] = detail_text
                elif 'Piso' in label_text:
                    details['floor'] = detail_text
                else:
                    # Store any other detail
                    clean_label = label_text.replace(':', '').strip()
                    details[clean_label.lower()] = detail_text
        
        return details
    
    def extract_all_text(self, soup: BeautifulSoup) -> str:
        """Extract ALL relevant visible text from the page, organized by sections."""
        sections = []
        
        # 1. Title/Header
        title = soup.find('h1')
        if title:
            sections.append(f"TÍTULO: {title.get_text(strip=True)}")
        
        # 2. Property Details Section (d3-property-details__content)
        details_section = soup.find('div', class_='d3-property-details__content')
        if details_section:
            details_text = []
            labels = details_section.find_all('div', class_='d3-property-details__detail-label')
            for label in labels:
                label_text = label.get_text(strip=True)
                detail = label.find('p', class_='d3-property-details__detail')
                if detail:
                    detail_text = detail.get_text(strip=True)
                    details_text.append(f"{label_text} {detail_text}")
            if details_text:
                sections.append("DETALLES:\n" + "\n".join(details_text))
        
        # 3. Description (d3-property-about__text)
        description = soup.find('div', class_='d3-property-about__text')
        if description:
            desc_text = description.get_text(strip=True)
            if desc_text:
                sections.append(f"DESCRIPCIÓN:\n{desc_text}")
        
        # 4. Amenities/Features section
        amenities_section = soup.find('div', class_='d3-property-features')
        if amenities_section:
            amenities = amenities_section.find_all('li')
            if amenities:
                amenity_list = [li.get_text(strip=True) for li in amenities]
                sections.append("AMENIDADES:\n" + "\n".join(amenity_list))
        
        # 5. Location information
        location = soup.find('div', class_='d3-property-location')
        if location:
            loc_text = location.get_text(strip=True)
            if loc_text:
                sections.append(f"UBICACIÓN:\n{loc_text}")
        
        # Join all sections with clear separators
        return "\n\n".join(sections)
    
    def extract_construction_stage(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract construction stage from timeline."""
        timeline = soup.find('div', class_='d3-new-property-stage__time-line')
        if not timeline:
            return None
        
        # Find all active stages
        active_items = timeline.find_all('div', class_='d3-new-property-stage__time-line-item--active')
        
        if active_items:
            # Get the last active stage
            last_active = active_items[-1]
            label = last_active.find('p', class_='d3-new-property-stage__time-line-label')
            if label:
                return label.get_text(strip=True)
        
        return None
    
    def enhance_with_ai(self, full_text: str, construction_stage: str) -> dict:
        """Use OpenAI to process clean text and extract ALL fields."""
        try:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                print("⚠️ OpenAI API key not configured, skipping AI enhancement")
                return {}
            
            client = openai.OpenAI(api_key=api_key)
            
            # Limit text to reasonable size (GPT-4o-mini can handle this easily)
            text_to_process = full_text[:8000] if len(full_text) > 8000 else full_text
            
            # Add construction stage to context
            context = f"""{text_to_process}

ETAPA DE CONSTRUCCIÓN: {construction_stage or 'No especificada'}
"""
            
            # Save text to file for inspection
            try:
                with open('ai_input_text.txt', 'w', encoding='utf-8') as f:
                    f.write(context)
                print(f"💾 Texto guardado en: ai_input_text.txt ({len(context)} caracteres)")
            except Exception as e:
                print(f"⚠️ No se pudo guardar archivo: {e}")
            
            prompt = """Analyze the real estate property information and extract/normalize the following fields in JSON format:

{
  "title": "Property name or descriptive title (max 100 chars)",
  "price_usd": <numeric price in USD>,
  "bedrooms": <number or null>,
  "bathrooms": <number or null>,
  "area_m2": <number or null>,
  "lot_size_m2": <number or null>,
  "property_type": "Casa|Apartamento|Terreno|Lote|Condominio|etc",
  "listing_type": "sale|rent",
  "location": "City, Province, Country",
  "amenities": ["amenity1", "amenity2", ...],
  "parking_spaces": <number or null>,
  "pool": <boolean>,
  "description": "Professional property description (2-3 sentences, max 500 chars)",
  "model": "Property model if mentioned",
  "construction_stage": "Planos|Preventa|En construcción|Listo"
}

CRITICAL INSTRUCTIONS:

TITLE:
- Extract the actual property/project NAME from the description (e.g., "A'Mar", "Vista del Mar", "Residencial Los Sueños")
- If there's a project name, use format: "ProjectName - Property Type in Location"
- Example: "A'Mar - Condominio en Jacó" NOT "Agendar una visita virtual"
- If no project name, use: "Property Type in Location" (e.g., "Apartamento en San José")
- Keep it concise and descriptive (max 100 chars)

DESCRIPTION:
- Write a professional, concise summary highlighting key selling points
- Include: property name/type, location, size, main features, unique aspects
- Focus on what makes this property attractive to buyers/renters
- Use complete sentences, proper grammar
- 2-3 sentences maximum (around 300-500 characters)
- Example: "A'Mar is an exclusive 20-story beachfront condominium in Jacó offering 2-bedroom apartments from $179,000. Features resort-style amenities including pools, gym, pickleball court, and 24/7 security. Prime location steps from the beach with stunning ocean views."

PRICE:
- Extract the REAL sale/rent price (NOT price per m²)
- Format "179'000" or "179,000" → convert to 179000
- Ignore "Precio / m²" values

OTHER FIELDS:
- Parse bedrooms/bathrooms as integers
- Extract ALL amenities mentioned (pool, gym, parking, security, BBQ area, etc.)
- Use location from "Localización" field
- Identify property type from "Categoria" or description
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a real estate data extraction expert. Extract and normalize property information accurately. Always return valid JSON."},
                    {"role": "user", "content": f"{prompt}\n\n{context}"}
                ],
                temperature=0,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            import json
            ai_data = json.loads(response.choices[0].message.content)
            
            # Convert AI response to expected format
            cleaned_data = {}
            
            if ai_data.get('title'):
                cleaned_data['title'] = ai_data['title']
            
            if ai_data.get('price_usd'):
                try:
                    cleaned_data['price_usd'] = Decimal(str(ai_data['price_usd']))
                except:
                    pass
            
            if ai_data.get('bedrooms'):
                try:
                    cleaned_data['bedrooms'] = int(ai_data['bedrooms'])
                except:
                    pass
            
            if ai_data.get('bathrooms'):
                try:
                    cleaned_data['bathrooms'] = Decimal(str(ai_data['bathrooms']))
                except:
                    pass
            
            if ai_data.get('area_m2'):
                try:
                    cleaned_data['area_m2'] = Decimal(str(ai_data['area_m2']))
                except:
                    pass
            
            if ai_data.get('lot_size_m2'):
                try:
                    cleaned_data['lot_size_m2'] = Decimal(str(ai_data['lot_size_m2']))
                except:
                    pass
            
            if ai_data.get('property_type'):
                cleaned_data['property_type'] = ai_data['property_type']
            
            if ai_data.get('listing_type'):
                cleaned_data['listing_type'] = ai_data['listing_type']
            
            if ai_data.get('location'):
                cleaned_data['location'] = ai_data['location']
            
            if ai_data.get('amenities') and isinstance(ai_data['amenities'], list):
                cleaned_data['amenities'] = ai_data['amenities']
            
            if ai_data.get('parking_spaces'):
                try:
                    cleaned_data['parking_spaces'] = int(ai_data['parking_spaces'])
                except:
                    pass
            
            if ai_data.get('description'):
                cleaned_data['description'] = ai_data['description']
            
            print(f"✅ AI enhanced data: {len(cleaned_data)} fields extracted")
            return cleaned_data
            
        except Exception as e:
            print(f"❌ AI enhancement error: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _dict_to_text(self, d: dict) -> str:
        """Convert dict to readable text format."""
        lines = []
        for key, value in d.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property title from Encuentra24."""
        # Try d3-property-details__title (new design)
        title = soup.find(class_='d3-property-details__title')
        if title:
            return title.get_text(strip=True)
        
        # Try property-detail section (old design)
        title = soup.find('h1', class_='property-detail')
        if title:
            return title.get_text(strip=True)
        
        # Try property-info section
        title = soup.find('h1', class_='property-info')
        if title:
            return title.get_text(strip=True)
        
        return super().extract_title(soup)
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract price from property details."""
        # Try d3-property-insight__attribute-details (new design)
        insights = soup.find_all(class_='d3-property-insight__attribute-details')
        for insight in insights:
            text = insight.get_text(strip=True)
            # Check for USD price
            usd_match = re.search(r'\$\s*([\d,]+)', text)
            if usd_match:
                price_str = usd_match.group(1).replace(',', '')
                try:
                    return Decimal(price_str)
                except:
                    pass
            
            # Check for CRC (colones) price
            crc_match = re.search(r'₡\s*([\d,]+)', text)
            if crc_match:
                price_str = crc_match.group(1).replace(',', '')
                try:
                    # Convert CRC to USD (approximate rate: 1 USD = 520 CRC)
                    crc_price = Decimal(price_str)
                    usd_price = crc_price / Decimal('520')
                    return usd_price.quantize(Decimal('0.01'))
                except:
                    pass
        
        # Look in property-detail or property-info sections (old design)
        for class_name in ['property-detail', 'property-info', 'listing-detail']:
            section = soup.find(class_=class_name)
            if section:
                price_text = section.get_text()
                match = re.search(r'\$\s*([\d,]+)', price_text)
                if match:
                    price_str = match.group(1).replace(',', '')
                    try:
                        return Decimal(price_str)
                    except:
                        pass
        
        return super().extract_price(soup)
    
    def extract_bedrooms(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract bedrooms from property details."""
        # Try d3-property-insight__attribute-details (new design)
        insights = soup.find_all(class_='d3-property-insight__attribute-details')
        for insight in insights:
            text = insight.get_text(strip=True)
            match = re.search(r'(\d+)\s*(recamara|recámara|habitacion|habitación|bedroom|dormitorio)', text, re.IGNORECASE)
            if not match:
                # Try with number after the word (e.g., "Recámaras2")
                match = re.search(r'(recamara|recámara|habitacion|habitación|bedroom|dormitorio)s?\s*(\d+)', text, re.IGNORECASE)
                if match:
                    return int(match.group(2))
            else:
                return int(match.group(1))
        
        # Search in property sections (old design)
        for class_name in ['property-detail', 'property-info', 'listing-detail']:
            section = soup.find(class_=class_name)
            if section:
                text = section.get_text()
                match = re.search(r'(\d+)\s*(recamara|recámara|habitacion|habitación|bedroom|dormitorio)', text, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        
        return super().extract_bedrooms(soup)
    
    def extract_bathrooms(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract bathrooms from property details."""
        # Try d3-property-insight__attribute-details (new design)
        insights = soup.find_all(class_='d3-property-insight__attribute-details')
        for insight in insights:
            text = insight.get_text(strip=True)
            match = re.search(r'(\d+\.?\d*)\s*(baño|baños|bathroom)', text, re.IGNORECASE)
            if not match:
                # Try with number after the word (e.g., "Baños2")
                match = re.search(r'(baño|baños|bathroom)s?\s*(\d+\.?\d*)', text, re.IGNORECASE)
                if match:
                    return Decimal(match.group(2))
            else:
                return Decimal(match.group(1))
        
        # Search in property sections (old design)
        for class_name in ['property-detail', 'property-info', 'listing-detail']:
            section = soup.find(class_=class_name)
            if section:
                text = section.get_text()
                match = re.search(r'(\d+\.?\d*)\s*(baño|baños|bathroom)', text, re.IGNORECASE)
                if match:
                    return Decimal(match.group(1))
        
        return super().extract_bathrooms(soup)
    
    def extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property description."""
        # Try d3-property-about__text (new design)
        desc = soup.find(class_='d3-property-about__text')
        if desc:
            # Remove all <br> tags and get clean text
            for br in desc.find_all('br'):
                br.replace_with('\n')
            text = desc.get_text(strip=True)
            if text and len(text) > 20:
                return text
        
        # Try description class (most common)
        desc = soup.find(class_='description')
        if desc:
            text = desc.get_text(separator='\n', strip=True)
            if text and len(text) > 20:
                return text
        
        # Try property-detail or listing-detail sections
        for class_name in ['property-detail', 'property-info', 'listing-detail']:
            desc = soup.find('div', class_=class_name)
            if desc:
                # Find paragraphs within
                paragraphs = desc.find_all('p')
                if paragraphs:
                    return '\n'.join([p.get_text(strip=True) for p in paragraphs])
        
        return super().extract_description(soup)
    
    def extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract location from property details."""
        # Try breadcrumb or location elements
        breadcrumb = soup.find(class_='adaptor-breadcrumb-detailpager')
        if breadcrumb:
            # Extract location from breadcrumb text
            text = breadcrumb.get_text(strip=True)
            # Look for location patterns
            match = re.search(r'(Alquiler|Venta)\s+de\s+[^>]+>\s*([^>]+)', text)
            if match:
                location = match.group(2).strip()
                if location and len(location) > 2:
                    return location
        
        # Try to find location in title
        title = self.extract_title(soup)
        if title:
            # Extract location from patterns like "Casa en San José"
            match = re.search(r'\ben\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)', title)
            if match:
                location = match.group(1)
                if location and len(location) > 2:
                    return location
        
        # Fallback: Use OpenAI to extract location from description
        description = self.extract_description(soup)
        if description and len(description) > 50:
            try:
                location = self._extract_location_with_ai(description)
                if location:
                    return location
            except Exception as e:
                print(f"Error extracting location with AI: {e}")
        
        return super().extract_location(soup)
    
    def _extract_location_with_ai(self, description: str) -> Optional[str]:
        """Use OpenAI to extract location from description."""
        try:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return None
            
            client = openai.OpenAI(api_key=api_key)
            
            instruction = "Extract the location (city, region, country) from this property description. Return ONLY the location in format: 'City, Region' or 'City, Region, Country'. If no clear location is found, return 'Unknown'."
            prompt = f"{instruction}\n\nDescription:\n{description[:1000]}\n\nLocation:"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a real estate data extraction assistant. Extract location information accurately and concisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=100
            )
            
            location = response.choices[0].message.content.strip()
            
            # Validate the response
            if location and location.lower() not in ['unknown', 'n/a', 'none', '']:
                return location
            
            return None
            
        except Exception as e:
            print(f"OpenAI extraction error: {e}")
            return None
    
    def extract_listing_id(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract listing ID/reference number."""
        # Try d3-property-details__code class
        code_span = soup.find('span', class_='d3-property-details__code')
        if code_span:
            text = code_span.get_text(strip=True)
            # Extract number from "Ref.: 2315"
            ref_match = re.search(r'Ref\.?:\s*(\d+)', text, re.IGNORECASE)
            if ref_match:
                return ref_match.group(1)
        
        # Fallback: search in full text
        text = soup.get_text()
        ref_match = re.search(r'Ref\.?:\s*(\d+)', text, re.IGNORECASE)
        if ref_match:
            return ref_match.group(1)
        
        # Try to find ID in URL or message text like "(31846620)"
        id_match = re.search(r'\((\d{8})\)', text)
        if id_match:
            return id_match.group(1)
        
        return None
    
    def extract_property_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property type (Casa, Apartamento, etc.)."""
        # Try to find in title or breadcrumb
        title = self.extract_title(soup)
        if title:
            # Look for property types in Spanish
            types = {
                'casa': 'Casa',
                'casas': 'Casa',
                'apartamento': 'Apartamento',
                'apto': 'Apartamento',
                'terreno': 'Terreno',
                'lote': 'Lote',
                'bodega': 'Bodega',
                'local': 'Local Comercial',
                'oficina': 'Oficina',
                'finca': 'Finca',
                'quinta': 'Quinta'
            }
            
            title_lower = title.lower()
            for key, value in types.items():
                if key in title_lower:
                    return value
        
        return None
    
    def extract_listing_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract listing type (Alquiler/Venta)."""
        # Try d3-property-insight__attribute-details
        insights = soup.find_all(class_='d3-property-insight__attribute-details')
        for insight in insights:
            text = insight.get_text(strip=True)
            if 'Alquiler' in text:
                return 'rent'
            if 'Venta' in text:
                return 'sale'
        
        # Try in title or breadcrumb
        text = soup.get_text()
        if re.search(r'\bAlquiler\b', text, re.IGNORECASE):
            return 'rent'
        if re.search(r'\bVenta\b', text, re.IGNORECASE):
            return 'sale'
        
        return None
    
    def extract_lot_size(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract lot size (M² totales)."""
        # Find all d3-property-details__detail-label
        labels = soup.find_all('div', class_='d3-property-details__detail-label')
        for label in labels:
            text = label.get_text(strip=True)
            # Look for "M² totales120" pattern (label and value together)
            match = re.search(r'M?²?\s*totales\s*([\d,]+)', text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    return Decimal(value_str)
                except:
                    pass
        
        return super().extract_lot_size(soup)
    
    def extract_date_listed(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract listing date (Publicado 11/01/2026)."""
        # Find all d3-property-details__detail-label
        labels = soup.find_all('div', class_='d3-property-details__detail-label')
        for label in labels:
            text = label.get_text(strip=True)
            # Look for "Publicado11/01/2026" pattern (label and value together)
            match = re.search(r'Publicado\s*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Convert to ISO format: DD/MM/YYYY -> YYYY-MM-DD
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                    return date_obj.strftime('%Y-%m-%d')
                except:
                    return date_str
        
        return None
