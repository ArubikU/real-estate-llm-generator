"""Encuentra24.com specific extractor.
"""

from typing import Optional
from bs4 import BeautifulSoup
from decimal import Decimal
import re
import openai
from django.conf import settings
from .base import BaseExtractor


class Encuentra24Extractor(BaseExtractor):
    """Extractor for encuentra24.com listings."""
    
    def __init__(self):
        super().__init__()
        self.site_name = "encuentra24.com"
    
    def extract(self, html: str, url: Optional[str] = None):
        """Override extract to include custom fields."""
        # Call parent extract first
        data = super().extract(html, url)
        
        # Add custom fields
        soup = BeautifulSoup(html, 'html.parser')
        data['listing_id'] = self.extract_listing_id(soup)
        data['date_listed'] = self.extract_date_listed(soup)
        
        return data
    
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
