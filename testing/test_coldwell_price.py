#!/usr/bin/env python
"""Quick test to verify price extraction"""
import os
import sys
import django
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from core.scraping.scraper import WebScraper
from core.scraping.extractors.coldwell_banker import ColdwellBankerExtractor

async def test_price(url):
    print(f"\n🧪 Testing: {url}\n")
    
    scraper = WebScraper()
    result = await scraper.scrape(url)
    
    if not result.get('success'):
        print(f"❌ Scraping failed")
        return
    
    extractor = ColdwellBankerExtractor()
    data = extractor.extract(result['html'], url)
    
    price = data.get('price_usd')
    title = data.get('title', 'N/A')
    
    if price:
        try:
            price_num = int(price)
            print(f"✅ PRECIO EXTRAÍDO: ${price_num:,}")
        except:
            print(f"✅ PRECIO EXTRAÍDO: ${price}")
    else:
        print(f"❌ NO SE EXTRAJO PRECIO")
    
    print(f"   Título: {title}")
    print()

async def main():
    # Test 3 diferentes URLs
    urls = [
        "https://www.coldwellbankercostarica.com/property/land-for-sale-in-samara/2660",  # $1,600,000
        "https://www.coldwellbankercostarica.com/property/2-bed-single-family-homes-for-sale-in-la-fortuna/1181",  # Casa
        "https://www.coldwellbankercostarica.com/property/land-for-sale-in-uvita/3899",  # Terreno grande
    ]
    
    for url in urls:
        await test_price(url)
        await asyncio.sleep(2)

if __name__ == '__main__':
    asyncio.run(main())
