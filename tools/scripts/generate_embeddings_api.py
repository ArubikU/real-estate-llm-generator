#!/usr/bin/env python3
"""
Script to generate embeddings for properties via API endpoint.
Sends a POST request to the /ingest/generate-embeddings/ endpoint.
"""

import requests
import json
import sys

# Production URL
PROD_URL = "https://goldfish-app-3hc23.ondigitalocean.app"

def generate_embeddings(force=False):
    """
    Call the generate embeddings endpoint.
    
    Args:
        force: If True, regenerate embeddings even if they exist
    """
    url = f"{PROD_URL}/ingest/generate-embeddings/"
    
    print(f"🔮 Sending request to: {url}")
    print(f"   Force mode: {force}")
    print()
    
    payload = {
        "force": force
    }
    
    try:
        response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ SUCCESS!")
            print()
            print("📊 Results:")
            print(f"   Total Properties: {data.get('total_properties')}")
            print(f"   With Embeddings: {data.get('with_embeddings')}")
            print(f"   Coverage: {data.get('coverage_percent')}%")
            print()
            print(f"   Processed: {data.get('processed')}")
            print(f"   Success: {data.get('success')}")
            print(f"   Errors: {data.get('errors')}")
            
            if data.get('error_details'):
                print()
                print("❌ Error Details:")
                for error in data['error_details']:
                    print(f"   - {error}")
            
            print()
            print(f"💬 Message: {data.get('message')}")
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (exceeded 5 minutes)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check for --force flag
    force = "--force" in sys.argv
    
    if force:
        print("⚠️  WARNING: Force mode will regenerate ALL embeddings")
        response = input("Are you sure? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            sys.exit(0)
        print()
    
    generate_embeddings(force=force)
