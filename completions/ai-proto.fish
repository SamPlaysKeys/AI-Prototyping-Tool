# Fish completion script for ai-proto CLI tool
#
# Installation:
#   cp ai-proto.fish ~/.config/fish/completions/
#   # Or for system-wide installation:
#   sudo cp ai-proto.fish /usr/share/fish/vendor_completions.d/

# Main commands
complete -c ai-proto -f -n "__fish_use_subcommand" -a "generate" -d "Generate AI documentation from prompts"
complete -c ai-proto -f -n "__fish_use_subcommand" -a "models" -d "List available models in LM Studio"
complete -c ai-proto -f -n "__fish_use_subcommand" -a "deliverables" -d "List available deliverable types"
complete -c ai-proto -f -n "__fish_use_subcommand" -a "health" -d "Check LM Studio connection and health"

# Global options
complete -c ai-proto -s v -l verbose -d "Increase verbosity (use multiple times)"
complete -c ai-proto -l version -d "Show version information"
complete -c ai-proto -l config-file -r -d "Path to configuration file"
complete -c ai-proto -l help -d "Show help message"

# Generate command options
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -s p -l prompt -d "Text prompt for generation"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -s f -l prompt-file -r -d "File containing prompt text"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -s t -l deliverable-types -d "Types of deliverables to generate"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -s m -l model -d "LM Studio model to use"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l lm-studio-url -d "LM Studio base URL" -a "http://localhost:1234/v1"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l api-key -d "API key for LM Studio"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -s o -l output -r -d "Output directory"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l output-format -a "markdown json" -d "Output format"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l show-html -d "Generate HTML preview of markdown content"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l raw -d "Output raw content without formatting"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l merge -d "Merge multiple deliverables into single document"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l no-merge -d "Do not merge deliverables"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l max-tokens -d "Maximum tokens for generation"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l temperature -d "Temperature for generation (0.0-1.0)"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l top-p -d "Top-p for generation (0.0-1.0)"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l completion-mode -a "sequential batch streaming" -d "Completion mode"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l save-config -r -d "Save current configuration to file"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate" -l dry-run -d "Show what would be generated without actually generating"

# Deliverable types for -t/--deliverable-types option
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate; and __fish_prev_arg_in -t --deliverable-types" -a "problem_statement" -d "Generate problem statement documentation"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate; and __fish_prev_arg_in -t --deliverable-types" -a "personas" -d "Create user personas"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate; and __fish_prev_arg_in -t --deliverable-types" -a "use_cases" -d "Develop use cases and scenarios"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate; and __fish_prev_arg_in -t --deliverable-types" -a "tool_outline" -d "Create tool architecture outline"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate; and __fish_prev_arg_in -t --deliverable-types" -a "implementation_instructions" -d "Generate implementation guide"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate; and __fish_prev_arg_in -t --deliverable-types" -a "copilot365_presentation_prompt" -d "Create presentation prompts for Copilot 365"
complete -c ai-proto -f -n "__fish_seen_subcommand_from generate; and __fish_prev_arg_in -t --deliverable-types" -a "effectiveness_assessment" -d "Generate effectiveness assessment framework"

# Models and health command options
complete -c ai-proto -f -n "__fish_seen_subcommand_from models health" -l lm-studio-url -d "LM Studio base URL" -a "http://localhost:1234/v1"
complete -c ai-proto -f -n "__fish_seen_subcommand_from models health" -l api-key -d "API key for LM Studio"
complete -c ai-proto -f -n "__fish_seen_subcommand_from models health" -l help -d "Show help message"

# Deliverables command options
complete -c ai-proto -f -n "__fish_seen_subcommand_from deliverables" -l help -d "Show help message"
