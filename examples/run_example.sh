#!/bin/bash

# AI Prototyping Tool - Example Usage Script
# This script demonstrates various ways to use the AI prototyping tool

set -e  # Exit on any error

echo "🚀 AI Prototyping Tool - Example Usage"
echo "======================================"

# Check if LM Studio is running
echo "📡 Checking LM Studio connection..."
if curl -s http://localhost:1234/v1/models > /dev/null 2>&1; then
    echo "✅ LM Studio is running"
else
    echo "❌ LM Studio is not running. Please start LM Studio and load a model."
    echo "   Visit: https://lmstudio.ai/"
    exit 1
fi

# Example 1: Basic usage with a simple prompt
echo ""
echo "📝 Example 1: Basic Problem Analysis"
echo "====================================="
python ../ai_prototyping_tool.py \
    --prompt "Create a mobile app for tracking daily water intake and hydration goals" \
    --output-json "example1_output.json" \
    --output-md "example1_report.md"

echo "✅ Example 1 complete. Check example1_report.md for results."

# Example 2: Interactive mode
echo ""
echo "🎯 Example 2: Interactive Mode"
echo "=============================="
echo "Note: This will prompt for user input. Press Ctrl+C to skip."
echo "Sample prompt: 'Design a project management tool for remote teams'"
echo ""
# Uncomment the next line to run interactive mode
# python ../ai_prototyping_tool.py --interactive

# Example 3: Custom LM Studio URL (for remote instances)
echo ""
echo "🌐 Example 3: Custom LM Studio URL"
echo "=================================="
echo "Note: This example shows how to connect to a remote LM Studio instance"
echo "Command: python ../ai_prototyping_tool.py --url 'http://remote-server:1234' --prompt 'Your idea'"

# Example 4: Multiple rapid prototypes
echo ""
echo "⚡ Example 4: Rapid Prototyping Multiple Ideas"
echo "============================================="

IDEAS=(
    "Smart home automation system for elderly users"
    "Expense tracking app for freelancers"
    "Language learning platform for children"
)

for i in "${!IDEAS[@]}"; do
    idea="${IDEAS[$i]}"
    echo "Processing idea $((i+1)): $idea"

    python ../ai_prototyping_tool.py \
        --prompt "$idea" \
        --output-json "rapid_${i}_output.json" \
        --output-md "rapid_${i}_report.md"

    echo "✅ Idea $((i+1)) processed"
done

echo ""
echo "🎉 All examples completed!"
echo "========================="
echo "Generated files:"
ls -la *.json *.md 2>/dev/null || echo "No output files found"

echo ""
echo "💡 Next steps:"
echo "- Review the generated markdown reports"
echo "- Use the CoPilot365 prompts in Microsoft 365"
echo "- Follow the implementation instructions"
echo "- Iterate on the ideas based on the plan evaluation"

echo ""
echo "🔧 Troubleshooting:"
echo "- If you get connection errors, ensure LM Studio is running"
echo "- If responses are poor quality, try a different model in LM Studio"
echo "- For timeout issues, reduce the complexity of your prompts"

echo ""
echo "📚 For more information, see the README.md file"
