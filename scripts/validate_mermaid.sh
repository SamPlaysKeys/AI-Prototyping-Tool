#!/bin/bash

# Mermaid Documentation Validation Script
# This script validates all Mermaid diagrams for syntax correctness

set -e

echo "🔍 Validating Mermaid Documentation"
echo "====================================="

# Check if mermaid-cli is installed
if ! command -v mmdc &> /dev/null; then
    echo "⚠️  mermaid-cli not found. Install with: npm install -g @mermaid-js/mermaid-cli"
    echo "   Or validate manually using GitHub or mermaid.live"
    exit 1
fi

# Find all .mmd files
MERMAID_FILES=($(find docs/ -name "*.mmd" -type f))

if [ ${#MERMAID_FILES[@]} -eq 0 ]; then
    echo "❌ No Mermaid files found in docs/ directory"
    exit 1
fi

echo "Found ${#MERMAID_FILES[@]} Mermaid files to validate:"
for file in "${MERMAID_FILES[@]}"; do
    echo "  - $file"
done
echo ""

# Validate each file
VALID_COUNT=0
ERROR_COUNT=0

for file in "${MERMAID_FILES[@]}"; do
    echo -n "Validating $(basename "$file")... "

    if mmdc -i "$file" -o /dev/null 2>/dev/null; then
        echo "✅ Valid"
        ((VALID_COUNT++))
    else
        echo "❌ Invalid"
        echo "   Error in: $file"
        # Show the actual error
        mmdc -i "$file" -o /dev/null 2>&1 | head -3 | sed 's/^/   /'
        ((ERROR_COUNT++))
    fi
done

echo ""
echo "Validation Summary:"
echo "=================="
echo "✅ Valid files: $VALID_COUNT"
echo "❌ Invalid files: $ERROR_COUNT"
echo "Total files: ${#MERMAID_FILES[@]}"

if [ $ERROR_COUNT -gt 0 ]; then
    echo ""
    echo "⚠️  Some files have validation errors. Please fix them before committing."
    exit 1
else
    echo ""
    echo "🎉 All Mermaid files are valid!"
    exit 0
fi
