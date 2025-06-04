# Getting Started with AI Prototyping Tool

This guide will help you get up and running with the AI Prototyping Tool in just a few minutes.

## 📝 Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed on your system
- **Git** for cloning the repository
- **LM Studio** downloaded and installed ([lmstudio.ai](https://lmstudio.ai/))
- **Modern web browser** for web interface usage

## 📦 Installation

### Step 1: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd AI-Prototyping-Tool

# Install the package
pip install -e .

# Verify installation
ai-proto --version
```

### Step 2: Set Up LM Studio

1. **Download LM Studio** from [lmstudio.ai](https://lmstudio.ai/)
2. **Install and launch** the application
3. **Download a model** (recommended: Mistral 7B Instruct, Llama 2 7B, or similar)
4. **Load the model** and start the local server
5. **Verify the server** is running at `http://localhost:1234`

### Step 3: Test Connection

```bash
# Test LM Studio connection
ai-proto health

# List available models
ai-proto models

# Check available deliverable types
ai-proto deliverables
```

## 🚀 Your First Generation

### CLI Quick Start

```bash
# Generate complete documentation for a simple project
ai-proto generate -p "Create a simple task management app for personal use"

# View the generated files
ls output/
```

Expected output structure:
```
output/
├── problem_statement.md
├── personas.md
├── use_cases.md
├── tool_outline.md
├── implementation_instructions.md
└── effectiveness_assessment.md
```

### Web Interface Quick Start

```bash
# Start the web application
cd web
python app.py

# Open your browser to http://localhost:8000
```

1. **Enter a prompt**: "Design a simple blog platform"
2. **Select deliverable types** or use defaults
3. **Click "Generate"** and watch real-time progress
4. **Download or view** the generated documentation

## 📖 Understanding the Output

### Generated Deliverables

The tool generates several types of professional documentation:

#### 1. Problem Statement
- Executive summary of the project
- Current state analysis
- Problem description and impact
- Success criteria and constraints

#### 2. Personas
- User profiles and characteristics
- Goals, motivations, and pain points
- Technical proficiency levels
- Usage scenarios

#### 3. Use Cases
- Detailed user interaction scenarios
- Functional requirements
- User flows and workflows
- Edge cases and exceptions

#### 4. Tool Outline
- Technical architecture overview
- Feature specifications
- Technology stack recommendations
- Implementation priorities

#### 5. Implementation Instructions
- Step-by-step development guide
- Code structure and patterns
- Testing strategies
- Deployment considerations

#### 6. Effectiveness Assessment
- Success metrics and KPIs
- Evaluation criteria
- Monitoring and analytics
- Continuous improvement plans

### Output Formats

- **Markdown** (default): Clean, readable format perfect for documentation
- **JSON**: Structured data format for programmatic processing
- **HTML**: Web-ready format with styling and navigation

## 📊 Next Steps

### Explore Advanced Features

```bash
# Generate specific deliverables only
ai-proto generate -p "E-commerce platform" \
  -t problem_statement \
  -t personas \
  -t use_cases

# Use custom generation parameters
ai-proto generate -p "Mobile banking app" \
  --temperature 0.5 \
  --max-tokens 4096 \
  -o ./my-project-docs

# Generate with HTML preview
ai-proto generate -p "Social media dashboard" \
  --show-html
```

### Customize Your Workflow

1. **Save configurations** for repeated use:
   ```bash
   ai-proto generate -p "API Gateway" \
     --temperature 0.3 \
     --save-config my-config.json
   ```

2. **Use configuration files**:
   ```bash
   ai-proto generate -p "New project" \
     --config-file my-config.json
   ```

3. **Install shell completions**:
   ```bash
   ./install_completions.sh
   ```

### Learn More

- **[CLI Reference](cli-reference.md)** - Complete command-line documentation
- **[Web Interface](web-interface.md)** - Web application features
- **[Configuration](configuration.md)** - Advanced configuration options
- **[Templates](templates.md)** - Customizing output templates

## 🔧 Troubleshooting

### Common Issues

**Problem**: `ai-proto: command not found`

**Solution**:
```bash
# Ensure the package is installed correctly
pip install -e .

# Check if the entry point is registered
pip show ai-prototyping-tool
```

**Problem**: `Connection refused` when connecting to LM Studio

**Solution**:
```bash
# Check if LM Studio is running
ai-proto health

# Test with curl
curl http://localhost:1234/v1/models

# Verify server is started in LM Studio
```

**Problem**: Generation fails or produces poor results

**Solution**:
```bash
# Check if a model is loaded
ai-proto models

# Try with a smaller prompt
ai-proto generate -p "Simple todo app"

# Adjust generation parameters
ai-proto generate -p "Your prompt" \
  --temperature 0.7 \
  --max-tokens 2048
```

### Getting Help

```bash
# Show help for any command
ai-proto --help
ai-proto generate --help

# Enable verbose logging
ai-proto generate -p "test" -vvv
```

## 📚 What's Next?

Now that you have the basics working:

1. **Experiment** with different prompts and projects
2. **Explore** the web interface for interactive usage
3. **Customize** templates for your specific needs
4. **Integrate** the tool into your development workflow
5. **Share** generated documentation with your team

Ready to dive deeper? Check out the [Architecture Overview](architecture.md) to understand how the tool works under the hood.

---

*Need help? Check the [troubleshooting section](../README.md#-troubleshooting) or open an issue on GitHub.*
