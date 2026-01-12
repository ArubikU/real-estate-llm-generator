"""ColdwellBankerCostaRica.com specific extractor.
"""

from typing import Optional
from bs4 import BeautifulSoup
from decimal import Decimal
import re
import openai
from django.conf import settings
from .base import BaseExtractor


class ColdwellBankerExtractor(BaseExtractor):
    """Extractor for coldwellbankercostarica.com listings."""
    
    def __init__(self):
        super().__init__()
        self.site_name = "coldwellbankercostarica.com"
    
    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property title."""
        # Try title-wrap section
        title_section = soup.find('div', class_='title-wrap')
        if title_section:
            title = title_section.find('h1')
            if title:
                return title.get_text(strip=True)
        
        return super().extract_title(soup)
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract price from title-wrap section."""
        title_section = soup.find('div', class_='title-wrap')
        if title_section:
            price_text = title_section.get_text()
            match = re.search(r'\$\s*([\d,]+)', price_text)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return Decimal(price_str)
                except:
                    pass
        
        return super().extract_price(soup)
    
    def extract_bedrooms(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract bedrooms from ul-specs."""
        specs = soup.find('ul', class_='ul-specs')
        if specs:
            text = specs.get_text()
            match = re.search(r'(\d+)\s*(bed|habitacion|dormitorio)', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Try more-details section
        more_details = soup.find('div', class_='more-details')
        if more_details:
            text = more_details.get_text()
            match = re.search(r'(\d+)\s*(bed|habitacion|dormitorio)', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return super().extract_bedrooms(soup)
    
    def extract_bathrooms(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract bathrooms from ul-specs."""
        specs = soup.find('ul', class_='ul-specs')
        if specs:
            text = specs.get_text()
            match = re.search(r'(\d+\.?\d*)\s*(bath|baño)', text, re.IGNORECASE)
            if match:
                return Decimal(match.group(1))
        
        # Try more-details section
        more_details = soup.find('div', class_='more-details')
        if more_details:
            text = more_details.get_text()
            match = re.search(r'(\d+\.?\d*)\s*(bath|baño)', text, re.IGNORECASE)
            if match:
                return Decimal(match.group(1))
        
        return super().extract_bathrooms(soup)
    
    def extract_area(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract building area from specs."""
        specs = soup.find('ul', class_='ul-specs')
        if specs:
            text = specs.get_text()
            # Look for sq ft or m2
            match = re.search(r'([\d,]+\.?\d*)\s*(sq\s*ft|sqft|m[²2])', text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    value = Decimal(value_str)
                    # Convert sq ft to m2 if needed
                    if 'ft' in match.group(2).lower():
                        value = value * Decimal('0.092903')
                    return value
                except:
                    pass
        
        return super().extract_area(soup)
    
    def extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract property description."""
        # Try desc-wrap section (main description container)
        desc_wrap = soup.find('div', class_='desc-wrap')
        if desc_wrap:
            # Try to get the complete description first
            desc_complete = desc_wrap.find('div', class_='desc-content-complete')
            if desc_complete:
                # Remove "Read More" / "Leer menos" links
                for link in desc_complete.find_all('a', class_='read-toggle'):
                    link.decompose()
                text = desc_complete.get_text(separator='\n', strip=True)
                if text:
                    return text
            
            # Fallback to partial description
            desc_partial = desc_wrap.find('div', class_='desc-content-partial')
            if desc_partial:
                for link in desc_partial.find_all('a', class_='read-toggle'):
                    link.decompose()
                text = desc_partial.get_text(separator='\n', strip=True)
                if text:
                    return text
            
            # Try general desc-content
            desc_content = desc_wrap.find('div', class_='desc-content')
            if desc_content:
                # Remove read-toggle links
                for link in desc_content.find_all('a', class_='read-toggle'):
                    link.decompose()
                text = desc_content.get_text(separator='\n', strip=True)
                if text:
                    return text
        
        # Try property-description as fallback
        desc = soup.find('div', class_='property-description')
        if desc:
            return desc.get_text(separator='\n', strip=True)
        
        # Try meta description as last resort
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content = meta_desc.get('content', '').strip()
            if content:
                return content
        
        return super().extract_description(soup)
    
    def extract_amenities(self, soup: BeautifulSoup) -> list:
        """Extract amenities from property-features."""
        amenities = []
        features_section = soup.find('div', class_='property-features')
        if features_section:
            # Find list items
            items = features_section.find_all('li')
            for item in items:
                amenity = item.get_text(strip=True)
                if amenity:
                    amenities.append(amenity)
        
        return amenities if amenities else super().extract_amenities(soup)
    
    def extract_latitude(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract latitude from map iframe."""
        # Look for Google Maps iframe
        iframe = soup.find('iframe', src=lambda x: x and 'google.com/maps' in x)
        if iframe:
            src = iframe.get('src', '')
            # Extract coordinates from iframe src
            # Format: https://maps.google.com/maps?q=LAT,LNG&...
            match = re.search(r'[?&]q=([-\d.]+),([-\d.]+)', src)
            if match:
                try:
                    return Decimal(match.group(1))
                except:
                    pass
        
        # Try map-container data attributes
        map_container = soup.find('div', class_='map-container')
        if map_container:
            lat = map_container.get('data-lat') or map_container.get('data-latitude')
            if lat:
                try:
                    return Decimal(lat)
                except:
                    pass
        
        return super().extract_latitude(soup)
    
    def extract_longitude(self, soup: BeautifulSoup) -> Optional[Decimal]:
        """Extract longitude from map iframe."""
        # Look for Google Maps iframe
        iframe = soup.find('iframe', src=lambda x: x and 'google.com/maps' in x)
        if iframe:
            src = iframe.get('src', '')
            match = re.search(r'[?&]q=([-\d.]+),([-\d.]+)', src)
            if match:
                try:
                    return Decimal(match.group(2))
                except:
                    pass
        
        # Try map-container data attributes
        map_container = soup.find('div', class_='map-container')
        if map_container:
            lng = map_container.get('data-lng') or map_container.get('data-longitude')
            if lng:
                try:
                    return Decimal(lng)
                except:
                    pass
        
        return super().extract_longitude(soup)
    
    def extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract full location string."""
        # Try to find h3 with location info in main content sections
        sections = soup.find_all('section')
        for section in sections:
            h3_tags = section.find_all('h3')
            for h3 in h3_tags:
                text = h3.get_text(strip=True)
                # Check if it contains location keywords
                if 'ubicación:' in text.lower() or 'location:' in text.lower():
                    # Split and get the part after the colon
                    parts = text.split(':', 1)
                    if len(parts) > 1:
                        location = parts[1].strip()
                        if location:
                            return location
        
        # Try location-wrap section
        location_section = soup.find('div', class_='location-wrap')
        if location_section:
            # Try to find address in the section
            addr = location_section.find('address')
            if addr:
                return addr.get_text(strip=True)
            
            # Or try paragraphs
            paragraphs = location_section.find_all('p')
            if paragraphs:
                return paragraphs[0].get_text(strip=True)
        
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
    
    def extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract address from location-wrap or any h3 with location info."""
        # Try to find h3 with location info in main content sections
        sections = soup.find_all('section')
        for section in sections:
            h3_tags = section.find_all('h3')
            for h3 in h3_tags:
                text = h3.get_text(strip=True)
                # Check if it contains location keywords
                if 'ubicación:' in text.lower() or 'location:' in text.lower():
                    # Split and get the part after the colon
                    parts = text.split(':', 1)
                    if len(parts) > 1:
                        location = parts[1].strip()
                        if location:
                            return location
        
        # Try location-wrap section
        location_section = soup.find('div', class_='location-wrap')
        if location_section:
            # Try to find address in the section
            addr = location_section.find('address')
            if addr:
                return addr.get_text(strip=True)
            
            # Or try paragraphs
            paragraphs = location_section.find_all('p')
            if paragraphs:
                return paragraphs[0].get_text(strip=True)
        
        # Fallback: Use OpenAI to extract location from description
        description = self.extract_description(soup)
        if description and len(description) > 50:
            try:
                location = self._extract_location_with_ai(description)
                if location:
                    return location
            except Exception as e:
                print(f"Error extracting location with AI: {e}")
        
        return super().extract_address(soup)
    
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
