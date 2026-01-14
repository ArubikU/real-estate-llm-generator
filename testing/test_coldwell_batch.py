#!/usr/bin/env python
"""
Test batch processing of Coldwell Banker URLs with the optimized extractor
"""
import os
import sys
import django
import asyncio
import json
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from core.scraping.scraper import WebScraper
from core.scraping.extractors.coldwell_banker import ColdwellBankerExtractor

# Test URLs
URLS = [
    "https://www.coldwellbankercostarica.com/property/land-for-sale-in-samara/2660",
    "https://www.coldwellbankercostarica.com/property/2-bed-land-for-sale-in-dominical/13235",
    "https://www.coldwellbankercostarica.com/property/land-for-sale-in-la-fortuna/12381",
    "https://www.coldwellbankercostarica.com/property/land-for-sale-in-la-fortuna/10249",
    "https://www.coldwellbankercostarica.com/property/2-bed-single-family-homes-for-sale-in-la-fortuna/1181",
    "https://www.coldwellbankercostarica.com/property/4-bed-single-family-homes-for-sale-in-la-fortuna/1257",
    "https://www.coldwellbankercostarica.com/property/3-bed-single-family-homes-for-sale-in-la-fortuna/12031",
    "https://www.coldwellbankercostarica.com/property/land-for-sale-in-ojochal/2441",
    "https://www.coldwellbankercostarica.com/property/land-for-sale-in-dominical/4878",
    "https://www.coldwellbankercostarica.com/property/land-for-sale-in-uvita/3899",
    "https://www.coldwellbankercostarica.com/property/land-for-sale-in-curridabat/2897",
    "https://www.coldwellbankercostarica.com/property/land-for-sale-in-curridabat/2785",
]

async def test_url(url, index):
    """Test a single URL"""
    print(f"\n{'='*80}")
    print(f"[{index+1}/{len(URLS)}] Testing: {url}")
    print(f"{'='*80}")
    
    try:
        # Scrape the URL
        scraper = WebScraper()
        result = await scraper.scrape(url)
        
        if not result.get('success'):
            print(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
            return {
                'url': url,
                'success': False,
                'error': result.get('error', 'Unknown error')
            }
        
        html_content = result['html']
        text_content = result.get('text', '')
        
        print(f"✅ Scraped successfully")
        print(f"   HTML size: {len(html_content):,} chars")
        print(f"   Text size: {len(text_content):,} chars")
        
        # Extract data (extractor will extract clean text internally)
        extractor = ColdwellBankerExtractor()
        data = extractor.extract(html_content, url)
        
        # Calculate completion rate
        fields = ['title', 'price', 'bedrooms', 'bathrooms', 'area_m2', 
                 'lot_size_m2', 'description', 'location', 'property_type', 'amenities']
        filled = sum(1 for f in fields if data.get(f) not in [None, 'N/A', '', []])
        completion_rate = (filled / len(fields)) * 100
        
        # Display results
        print(f"\n📊 EXTRACTION RESULTS:")
        print(f"   Completion: {completion_rate:.1f}% ({filled}/{len(fields)} fields)")
        print(f"   Title: {data.get('title', 'N/A')[:80]}")
        print(f"   Price: {data.get('price', 'N/A')}")
        print(f"   Type: {data.get('property_type', 'N/A')}")
        print(f"   Location: {data.get('location', 'N/A')}")
        print(f"   Bedrooms: {data.get('bedrooms', 'N/A')}")
        print(f"   Bathrooms: {data.get('bathrooms', 'N/A')}")
        print(f"   Area: {data.get('area_m2', 'N/A')} m²")
        print(f"   Lot Size: {data.get('lot_size_m2', 'N/A')} m²")
        print(f"   Amenities: {len(data.get('amenities', []))} items")
        
        if data.get('description'):
            print(f"   Description: {data['description'][:100]}...")
        
        return {
            'url': url,
            'success': True,
            'completion_rate': completion_rate,
            'filled_fields': filled,
            'data': data
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'url': url,
            'success': False,
            'error': str(e)
        }

async def main():
    """Test all URLs"""
    print(f"\n{'#'*80}")
    print(f"# COLDWELL BANKER BATCH TEST - {len(URLS)} URLs")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}")
    
    results = []
    
    # Test each URL sequentially
    for i, url in enumerate(URLS):
        result = await test_url(url, i)
        results.append(result)
        
        # Small delay between requests
        if i < len(URLS) - 1:
            await asyncio.sleep(2)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n✅ Successful: {len(successful)}/{len(URLS)}")
    print(f"❌ Failed: {len(failed)}/{len(URLS)}")
    
    if successful:
        avg_completion = sum(r['completion_rate'] for r in successful) / len(successful)
        print(f"\n📊 Average Completion Rate: {avg_completion:.1f}%")
        print(f"   Best: {max(r['completion_rate'] for r in successful):.1f}%")
        print(f"   Worst: {min(r['completion_rate'] for r in successful):.1f}%")
    
    if failed:
        print(f"\n❌ Failed URLs:")
        for r in failed:
            print(f"   - {r['url']}")
            print(f"     Error: {r.get('error', 'Unknown')}")
    
    # Save detailed results
    output_file = 'test_coldwell_batch_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print(f"\n{'#'*80}")

if __name__ == '__main__':
    asyncio.run(main())
