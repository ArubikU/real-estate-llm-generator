#!/bin/bash

# Simula el proceso de build de Digital Ocean App Platform
# para identificar errores antes de deployar

set -e  # Exit on any error

echo "🔍 Simulando Digital Ocean Build Process..."
echo ""

echo "📦 Step 1: Limpiando node_modules..."
rm -rf node_modules
echo "✅ Limpieza completa"
echo ""

echo "📦 Step 2: Ejecutando npm ci (como Digital Ocean)..."
npm ci
echo "✅ Dependencies instaladas"
echo ""

echo "🔨 Step 3: Ejecutando build..."
npm run build
echo "✅ Build exitoso"
echo ""

echo "📊 Step 4: Verificando output..."
if [ -d "dist" ]; then
    echo "✅ Directorio dist/ creado"
    echo ""
    echo "📁 Archivos generados:"
    ls -lh dist/
    echo ""
    echo "🎉 BUILD EXITOSO - Listo para Digital Ocean!"
else
    echo "❌ ERROR: No se generó el directorio dist/"
    exit 1
fi
