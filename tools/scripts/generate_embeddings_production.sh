#!/bin/bash

# Script to generate embeddings for existing properties in production
# This connects to DigitalOcean and runs the management command

echo "🔮 Generating embeddings for properties in production..."
echo ""

# Get DigitalOcean App ID from deployment files
APP_ID="3hc23"

echo "📡 Connecting to DigitalOcean App Platform..."
echo ""

# Execute the management command on the backend service
doctl apps exec $APP_ID --component backend -- python manage.py generate_property_embeddings

echo ""
echo "✅ Embedding generation complete!"
echo ""
echo "💡 Tip: New properties will automatically have embeddings generated when saved."
