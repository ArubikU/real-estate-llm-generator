"""
Script to extract property URLs from database and verify they are accessible.
Useful for testing batch processing and Google Sheets integration.
"""

import os
import sys
import django
import requests
from typing import List, Dict

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.properties.models import Property

def verify_url(url: str) -> Dict[str, any]:
    """
    Verify if a URL is accessible.
    
    Returns:
        Dict with status, status_code, and error if any
    """
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return {
            'url': url,
            'accessible': response.status_code < 400,
            'status_code': response.status_code,
            'error': None
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'accessible': False,
            'status_code': None,
            'error': str(e)
        }

def extract_property_urls(limit: int = 20, verify: bool = True) -> List[Dict]:
    """
    Extract property URLs from database.
    
    Args:
        limit: Maximum number of URLs to extract
        verify: Whether to verify URL accessibility
        
    Returns:
        List of dictionaries with URL info
    """
    print(f"🔍 Extracting up to {limit} property URLs from database...")
    print("-" * 80)
    
    # Get properties with source URLs
    properties = Property.objects.filter(
        source_url__isnull=False
    ).exclude(
        source_url=''
    ).order_by('-created_at')[:limit]
    
    if not properties:
        print("❌ No properties with URLs found in database.")
        return []
    
    print(f"✅ Found {properties.count()} properties with URLs\n")
    
    results = []
    for i, prop in enumerate(properties, 1):
        url = prop.source_url
        property_info = {
            'number': i,
            'url': url,
            'property_id': str(prop.id),
            'title': prop.property_name or 'N/A',
            'price': f"${prop.price_usd:,.2f}" if prop.price_usd else 'N/A',
            'location': prop.location or 'N/A',
            'created_at': prop.created_at.strftime('%Y-%m-%d %H:%M')
        }
        
        # Verify URL if requested
        if verify:
            print(f"[{i}/{properties.count()}] Verificando: {url[:70]}...")
            verification = verify_url(url)
            property_info.update(verification)
            
            status_icon = "✅" if verification['accessible'] else "❌"
            status_text = f"{verification['status_code']}" if verification['status_code'] else "Error"
            print(f"          {status_icon} Status: {status_text}")
            
            if verification['error']:
                print(f"          ⚠️  Error: {verification['error'][:60]}...")
        else:
            property_info['accessible'] = None
            property_info['status_code'] = None
            property_info['error'] = None
        
        results.append(property_info)
    
    return results

def save_urls_to_file(results: List[Dict], filename: str = 'property_urls.txt'):
    """Save URLs to a text file (one per line)."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(result['url'] + '\n')
    
    print(f"\n💾 URLs guardadas en: {filepath}")
    return filepath

def save_accessible_urls(results: List[Dict], filename: str = 'accessible_urls.txt'):
    """Save only accessible URLs to a text file."""
    accessible = [r for r in results if r.get('accessible')]
    
    if not accessible:
        print("\n⚠️  No hay URLs accesibles para guardar")
        return None
    
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for result in accessible:
            f.write(result['url'] + '\n')
    
    print(f"💾 URLs accesibles guardadas en: {filepath}")
    print(f"   Total: {len(accessible)}/{len(results)} URLs accesibles")
    return filepath

def print_summary(results: List[Dict]):
    """Print summary statistics."""
    print("\n" + "=" * 80)
    print("📊 RESUMEN")
    print("=" * 80)
    
    total = len(results)
    accessible = sum(1 for r in results if r.get('accessible') is True)
    inaccessible = sum(1 for r in results if r.get('accessible') is False)
    not_verified = sum(1 for r in results if r.get('accessible') is None)
    
    print(f"Total URLs extraídas:     {total}")
    if not_verified == 0:
        print(f"URLs accesibles:          {accessible} ({accessible/total*100:.1f}%)")
        print(f"URLs inaccesibles:        {inaccessible} ({inaccessible/total*100:.1f}%)")
        
        if accessible > 0:
            print(f"\n✅ Puedes usar estas URLs para probar:")
            print(f"   • Batch Processing: /batch-processing")
            print(f"   • Google Sheets: Copia de accessible_urls.txt")

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract and verify property URLs')
    parser.add_argument('-l', '--limit', type=int, default=20, 
                        help='Number of URLs to extract (default: 20)')
    parser.add_argument('-n', '--no-verify', action='store_true',
                        help='Skip URL verification')
    parser.add_argument('-s', '--save', action='store_true',
                        help='Save URLs to files')
    
    args = parser.parse_args()
    
    # Extract URLs
    results = extract_property_urls(limit=args.limit, verify=not args.no_verify)
    
    if not results:
        return
    
    # Print summary
    print_summary(results)
    
    # Save to files if requested
    if args.save:
        print("\n📝 Guardando archivos...")
        save_urls_to_file(results, 'property_urls.txt')
        if not args.no_verify:
            save_accessible_urls(results, 'accessible_urls.txt')
    
    # Print sample URLs
    print("\n📋 Ejemplo de URLs (primeras 5):")
    print("-" * 80)
    for i, result in enumerate(results[:5], 1):
        status = "✅" if result.get('accessible') else ("❌" if result.get('accessible') is False else "?")
        print(f"{i}. {status} {result['url']}")
        print(f"   Título: {result['title'][:60]}")
        print(f"   Precio: {result['price']} | Ubicación: {result['location'][:30]}")
        print()
    
    if len(results) > 5:
        print(f"... y {len(results) - 5} URLs más\n")
    
    print("💡 Tip: Usa --save para guardar las URLs en archivos")
    print("💡 Tip: Usa --limit 50 para extraer más URLs")
    print("💡 Tip: Usa --no-verify para extraer sin verificar (más rápido)")

if __name__ == "__main__":
    main()
