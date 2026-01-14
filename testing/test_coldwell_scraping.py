#!/usr/bin/env python
"""
Script to analyze Coldwell Banker page structure.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from core.scraping.scraper import scrape_url
from core.scraping.extractors import get_extractor
from bs4 import BeautifulSoup

url = 'https://www.coldwellbankercostarica.com/property/land-for-sale-in-la-fortuna/12381'
print(f'🔍 Scraping: {url}\n')

# Scrape the page
result = scrape_url(url)

if result.get('success'):
    html = result.get('html', '')
    print(f'✅ Successfully scraped {len(html):,} characters\n')
    
    # Save HTML to file for inspection
    output_file = '/tmp/coldwell_banker_page.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'📁 HTML saved to: {output_file}\n')
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    print('=' * 80)
    print('HTML STRUCTURE ANALYSIS')
    print('=' * 80)
    
    # Find title
    title = soup.find('title')
    print(f'\n📄 TITLE: {title.text if title else "Not found"}')
    
    # Find h1 tags
    h1_tags = soup.find_all('h1')
    print(f'\n📌 H1 TAGS ({len(h1_tags)}):')
    for i, h1 in enumerate(h1_tags[:5], 1):
        print(f'  {i}. {h1.text.strip()[:100]}')
    
    # Find price elements (common class names)
    price_selectors = [
        ('class', 'price'),
        ('class', 'property-price'),
        ('class', 'listing-price'),
        ('id', 'price'),
        ('itemprop', 'price'),
    ]
    
    print(f'\n💰 PRICE ELEMENTS:')
    for attr, value in price_selectors:
        elements = soup.find_all(attrs={attr: value})
        if elements:
            print(f'  [{attr}="{value}"] found {len(elements)} elements:')
            for el in elements[:3]:
                print(f'    - {el.text.strip()[:100]}')
    
    # Look for property details
    print(f'\n🏠 PROPERTY DETAILS:')
    detail_keywords = ['bedroom', 'bathroom', 'sqft', 'square', 'lot', 'area']
    for keyword in detail_keywords:
        elements = soup.find_all(string=lambda text: text and keyword.lower() in text.lower())
        if elements:
            print(f'  "{keyword}": {len(elements)} matches')
            for el in elements[:2]:
                parent = el.parent
                print(f'    - {parent.name}: {el.strip()[:80]}')
    
    # Find images
    images = soup.find_all('img')
    print(f'\n🖼️  IMAGES: {len(images)} found')
    property_images = [img.get('src') or img.get('data-src') for img in images if img.get('src') or img.get('data-src')]
    print(f'  Property images: {len(property_images)}')
    if property_images:
        print(f'  First 3 images:')
        for img in property_images[:3]:
            print(f'    - {img}')
    
    # Find description
    print(f'\n📝 DESCRIPTION:')
    desc_selectors = [
        ('class', 'description'),
        ('class', 'property-description'),
        ('id', 'description'),
        ('itemprop', 'description'),
    ]
    for attr, value in desc_selectors:
        elements = soup.find_all(attrs={attr: value})
        if elements:
            print(f'  [{attr}="{value}"] found:')
            for el in elements[:1]:
                text = el.text.strip()
                print(f'    {text[:200]}...')
    
    # Find structured data (JSON-LD)
    print(f'\n🔍 STRUCTURED DATA (JSON-LD):')
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    print(f'  Found {len(json_ld_scripts)} JSON-LD scripts')
    for i, script in enumerate(json_ld_scripts[:2], 1):
        print(f'  Script {i}: {script.string[:200] if script.string else "empty"}...')
    
    # Try the extractor
    print(f'\n' + '=' * 80)
    print('TESTING EXTRACTOR')
    print('=' * 80)
    extractor = get_extractor(url)
    print(f'\n🔧 Extractor: {extractor.__class__.__name__}')
    
    if extractor.__class__.__name__ != 'BaseExtractor':
        print(f'✅ Site-specific extractor found: {extractor.site_name}')
        extracted_data = extractor.extract(html, url)
        
        print(f'\n📊 EXTRACTED DATA:')
        print(f'  Title: {extracted_data.get("title", "N/A")}')
        print(f'  Price: ${extracted_data.get("price_usd", "N/A"):,}' if extracted_data.get("price_usd") else '  Price: N/A')
        print(f'  Bedrooms: {extracted_data.get("bedrooms", "N/A")}')
        print(f'  Bathrooms: {extracted_data.get("bathrooms", "N/A")}')
        print(f'  Area (m²): {extracted_data.get("area_m2", "N/A")}')
        print(f'  Lot Size (m²): {extracted_data.get("lot_size_m2", "N/A")}')
        print(f'  Location: {extracted_data.get("location", "N/A")}')
        print(f'  Images: {len(extracted_data.get("images", []))}')
        print(f'  Description length: {len(extracted_data.get("description", ""))} chars')
    else:
        print('⚠️  Using base extractor (no site-specific extractor)')
    
    # Print common div classes
    print(f'\n' + '=' * 80)
    print('COMMON DIV CLASSES (first 20)')
    print('=' * 80)
    divs_with_class = soup.find_all('div', class_=True)
    class_counts = {}
    for div in divs_with_class:
        classes = div.get('class', [])
        for cls in classes:
            class_counts[cls] = class_counts.get(cls, 0) + 1
    
    sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
    for cls, count in sorted_classes[:20]:
        print(f'  .{cls}: {count}')
    
else:
    print(f'❌ Failed to scrape: {result.get("error")}')
    sys.exit(1)

print(f'\n' + '=' * 80)
print('Analysis complete!')
print('=' * 80)
