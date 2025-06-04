#!/bin/bash

# Bash completion script for ai-proto CLI tool
#
# Installation:
#   # For system-wide installation (requires sudo):
#   sudo cp ai-proto-complete.bash /etc/bash_completion.d/ai-proto
#
#   # For user installation:
#   mkdir -p ~/.local/share/bash-completion/completions
#   cp ai-proto-complete.bash ~/.local/share/bash-completion/completions/ai-proto
#
#   # Or source it directly in your .bashrc:
#   echo "source /path/to/ai-proto-complete.bash" >> ~/.bashrc

_ai_proto_completions() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    commands="generate models deliverables health"

    # Global options
    global_opts="--help --version -v --verbose --config-file"

    # Generate command options
    generate_opts="--prompt -p --prompt-file -f --deliverable-types -t --model -m --lm-studio-url --api-key --output -o --output-format --show-html --raw --merge --no-merge --max-tokens --temperature --top-p --completion-mode --save-config --dry-run --help"

    # Deliverable types
    deliverable_types="problem_statement personas use_cases tool_outline implementation_instructions copilot365_presentation_prompt effectiveness_assessment"

    # Output formats
    output_formats="markdown json"

    # Completion modes
    completion_modes="sequential batch streaming"

    case ${COMP_CWORD} in
        1)
            # Complete main commands
            COMPREPLY=($(compgen -W "${commands} ${global_opts}" -- ${cur}))
            return 0
            ;;
    esac

    case ${prev} in
        # File completions
        --prompt-file|-f|--config-file|--save-config)
            COMPREPLY=($(compgen -f -- ${cur}))
            return 0
            ;;
        # Directory completions
        --output|-o)
            COMPREPLY=($(compgen -d -- ${cur}))
            return 0
            ;;
        # Deliverable types
        --deliverable-types|-t)
            COMPREPLY=($(compgen -W "${deliverable_types}" -- ${cur}))
            return 0
            ;;
        # Output formats
        --output-format)
            COMPREPLY=($(compgen -W "${output_formats}" -- ${cur}))
            return 0
            ;;
        # Completion modes
        --completion-mode)
            COMPREPLY=($(compgen -W "${completion_modes}" -- ${cur}))
            return 0
            ;;
        # Numeric values - no completion
        --max-tokens|--temperature|--top-p)
            return 0
            ;;
        # String values - no completion
        --prompt|-p|--model|-m|--lm-studio-url|--api-key)
            return 0
            ;;
    esac

    # Get the first command
    local cmd=""
    for ((i=1; i<COMP_CWORD; i++)); do
        if [[ ${COMP_WORDS[i]} != -* ]]; then
            cmd=${COMP_WORDS[i]}
            break
        fi
    done

    case ${cmd} in
        generate)
            COMPREPLY=($(compgen -W "${generate_opts}" -- ${cur}))
            ;;
        models|deliverables|health)
            # These commands have limited options
            local simple_opts="--help --lm-studio-url --api-key"
            COMPREPLY=($(compgen -W "${simple_opts}" -- ${cur}))
            ;;
        *)
            # Default to main commands and global options
            COMPREPLY=($(compgen -W "${commands} ${global_opts}" -- ${cur}))
            ;;
    esac
}

# Register the completion function
complete -F _ai_proto_completions ai-proto
