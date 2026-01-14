"""
Script to find real property URLs by scraping property listing sites.
Uses WebScraper to get actual, current property listings from specific sites.
"""

import os
import sys
import json
import django
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

django.setup()

from core.scraping.scraper import WebScraper

async def scrape_site_listings(site_name: str, base_url: str, num_properties: int = 5) -> list:
    """
    Scrape property listings from a specific site.
    
    Args:
        site_name: Name of the site (for display)
        base_url: URL to scrape
        num_properties: Number of properties to extract
        
    Returns:
        List of property URLs found
    """
    print(f"\n🔍 Buscando en {site_name}...")
    print(f"   URL: {base_url}")
    
    try:
        scraper = WebScraper()
        result = await scraper.scrape(base_url)
        
        if not result.get('success'):
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            return []
        
        html = result.get('html', '')
        
        # Extract property links based on common patterns
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        property_urls = set()  # Use set to avoid duplicates
        
        # Patterns for each site
        if 'encuentra24' in base_url.lower():
            # Encuentra24 property links - look for listing cards
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Encuentra24 uses patterns like /inmuebles-venta-<id>-<title>
                if '/inmuebles-' in href or 'listing' in href:
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('//'):
                        full_url = 'https:' + href
                    elif href.startswith('/'):
                        full_url = 'https://www.encuentra24.com' + href
                    else:
                        continue
                    
                    # Only add if it's a full listing URL (not category pages)
                    if 'inmuebles-' in full_url and '-en-' in full_url:
                        property_urls.add(full_url)
                        if len(property_urls) >= num_properties:
                            break
                            
        elif 'coldwellbanker' in base_url.lower():
            # Coldwell Banker property links
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Look for property detail pages
                if ('/property/' in href or '/propiedad/' in href or 
                    '/listing/' in href or 'property-' in href):
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = 'https://www.coldwellbankercostarica.com' + href
                    else:
                        continue
                    
                    # Verify it looks like a property detail page
                    if any(x in full_url for x in ['/property/', '/propiedad/', 'property-']):
                        property_urls.add(full_url)
                        if len(property_urls) >= num_properties:
                            break
                            
        elif 'brevitas' in base_url.lower():
            # Brevitas property links
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Brevitas uses /property/<slug> pattern
                if '/property/' in href or '/propiedad/' in href:
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = 'https://www.brevitas.com' + href
                    else:
                        continue
                    
                    # Only property detail pages
                    if '/property/' in full_url:
                        property_urls.add(full_url)
                        if len(property_urls) >= num_properties:
                            break
        
        result_list = list(property_urls)[:num_properties]
        print(f"   ✅ Encontradas {len(result_list)} URLs")
        return result_list
        
    except Exception as e:
        print(f"   ❌ Error al scraper: {str(e)}")
        return []

async def find_property_urls(num_properties: int = 15) -> list:
    """
    Find real property URLs by scraping listing sites.
    
    Args:
        num_properties: Total number of properties to find
        
    Returns:
        List of property URLs
    """
    print(f"🔍 Buscando {num_properties} propiedades reales...")
    print("🌐 Usando WebScraper para obtener URLs actuales")
    print("-" * 80)
    
    # Sites to scrape
    sites = [
        {
            'name': 'Encuentra24',
            'url': 'https://www.encuentra24.com/costa-rica-es/bienes-raices-venta',
            'props': num_properties // 3
        },
        {
            'name': 'Coldwell Banker Costa Rica',
            'url': 'https://coldwellbankercostarica.com/properties/',
            'props': num_properties // 3
        },
        {
            'name': 'Brevitas',
            'url': 'https://www.brevitas.com/costa-rica/properties',
            'props': num_properties // 3
        }
    ]
    
    all_properties = []
    
    for site in sites:
        urls = await scrape_site_listings(site['name'], site['url'], site['props'])
        
        for url in urls:
            all_properties.append({
                'url': url,
                'source_site': site['name'],
                'title': 'To be extracted',
                'price': 'N/A',
                'location': 'N/A'
            })
    
    print("\n" + "=" * 80)
    print(f"✅ Total URLs encontradas: {len(all_properties)}")
    print("=" * 80)
    
    return all_properties

def save_urls_to_file(properties: list, filename: str = 'found_property_urls.txt'):
    """Save found URLs to a text file."""
    if not properties:
        print("\n⚠️  No hay URLs para guardar")
        return None
    
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for prop in properties:
            f.write(prop.get('url', '') + '\n')
    
    print(f"\n💾 URLs guardadas en: {filepath}")
    return filepath

def save_detailed_json(properties: list, filename: str = 'found_properties.json'):
    """Save detailed property information to JSON file."""
    if not properties:
        return None
    
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({'properties': properties}, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Detalles guardados en: {filepath}")
    return filepath

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Find real property URLs by scraping listing sites')
    parser.add_argument('-n', '--num', type=int, default=15,
                        help='Number of properties to find (default: 15)')
    parser.add_argument('-s', '--save', action='store_true',
                        help='Save results to files')
    
    args = parser.parse_args()
    
    # Find properties (run async function)
    properties = asyncio.run(find_property_urls(num_properties=args.num))
    
    if not properties:
        print("\n❌ No se encontraron propiedades")
        return
    
    # Display results
    print("\n📋 URLs encontradas:")
    print("-" * 80)
    for i, prop in enumerate(properties, 1):
        print(f"\n{i}. {prop['source_site']}")
        print(f"   URL: {prop['url']}")
    
    # Save to files if requested
    if args.save:
        print("\n📝 Guardando archivos...")
        save_urls_to_file(properties)
        save_detailed_json(properties)
    
    print("\n✅ Proceso completado!")
    print(f"\n💡 URLs encontradas: {len(properties)}")
    print(f"💡 Puedes usar estas URLs en /batch-processing")
    
    if not args.save:
        print(f"\n💡 Tip: Usa --save para guardar las URLs en archivos")

if __name__ == "__main__":
    main()
