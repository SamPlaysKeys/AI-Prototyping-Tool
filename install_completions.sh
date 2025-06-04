#!/bin/bash

# AI Prototyping Tool - Shell Completion Installation Script
# This script installs shell completion for the ai-proto CLI tool

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

get_shell() {
    local shell_name=$(basename "$SHELL")
    echo "$shell_name"
}

install_bash_completion() {
    local shell_type="$1"
    local completion_file="completions/ai-proto-complete.bash"

    if [[ ! -f "$completion_file" ]]; then
        log_error "Bash completion file not found: $completion_file"
        return 1
    fi

    # Try system-wide installation first (if running as root)
    if [[ $EUID -eq 0 ]]; then
        log_info "Installing bash completion system-wide..."
        if [[ -d "/etc/bash_completion.d" ]]; then
            cp "$completion_file" "/etc/bash_completion.d/ai-proto"
            log_success "Bash completion installed system-wide"
            return 0
        fi
    fi

    # User installation
    log_info "Installing bash completion for current user..."
    local user_completion_dir="$HOME/.local/share/bash-completion/completions"
    mkdir -p "$user_completion_dir"
    cp "$completion_file" "$user_completion_dir/ai-proto"

    # Add to .bashrc if not already present
    local bashrc="$HOME/.bashrc"
    if [[ -f "$bashrc" ]]; then
        if ! grep -q "bash-completion" "$bashrc"; then
            echo "" >> "$bashrc"
            echo "# Enable bash completion" >> "$bashrc"
            echo "if [ -f ~/.local/share/bash-completion/completions/* ]; then" >> "$bashrc"
            echo "    for completion_file in ~/.local/share/bash-completion/completions/*; do" >> "$bashrc"
            echo "        [ -r \"\$completion_file\" ] && source \"\$completion_file\"" >> "$bashrc"
            echo "    done" >> "$bashrc"
            echo "fi" >> "$bashrc"
            log_info "Added completion loading to ~/.bashrc"
        fi
    fi

    log_success "Bash completion installed for current user"
    log_info "Please restart your shell or run: source ~/.bashrc"
}

install_zsh_completion() {
    local completion_file="completions/_ai-proto"

    if [[ ! -f "$completion_file" ]]; then
        log_error "Zsh completion file not found: $completion_file"
        return 1
    fi

    log_info "Installing zsh completion for current user..."

    # Check if oh-my-zsh is installed
    if [[ -d "$HOME/.oh-my-zsh" ]]; then
        log_info "Detected oh-my-zsh, installing completion..."
        local omz_completion_dir="$HOME/.oh-my-zsh/completions"
        mkdir -p "$omz_completion_dir"
        cp "$completion_file" "$omz_completion_dir/"
        log_success "Zsh completion installed for oh-my-zsh"
    else
        # Standard zsh installation
        local zsh_completion_dir="$HOME/.zsh/completions"
        mkdir -p "$zsh_completion_dir"
        cp "$completion_file" "$zsh_completion_dir/"

        # Add to .zshrc if not already present
        local zshrc="$HOME/.zshrc"
        if [[ -f "$zshrc" ]]; then
            if ! grep -q "fpath=(.*\.zsh/completions" "$zshrc"; then
                echo "" >> "$zshrc"
                echo "# Add custom completions" >> "$zshrc"
                echo "fpath=(~/.zsh/completions \$fpath)" >> "$zshrc"
                echo "autoload -U compinit && compinit" >> "$zshrc"
                log_info "Added completion loading to ~/.zshrc"
            fi
        fi

        log_success "Zsh completion installed for current user"
    fi

    log_info "Please restart your shell or run: exec zsh"
}

install_fish_completion() {
    local completion_file="completions/ai-proto.fish"

    if [[ ! -f "$completion_file" ]]; then
        log_error "Fish completion file not found: $completion_file"
        return 1
    fi

    log_info "Installing fish completion for current user..."

    # User installation
    local fish_completion_dir="$HOME/.config/fish/completions"
    mkdir -p "$fish_completion_dir"
    cp "$completion_file" "$fish_completion_dir/"

    log_success "Fish completion installed for current user"
    log_info "Completion will be available in new fish sessions"
}

show_usage() {
    echo "AI Prototyping Tool - Shell Completion Installation"
    echo ""
    echo "Usage: $0 [shell]"
    echo ""
    echo "Shells:"
    echo "  bash    Install bash completion"
    echo "  zsh     Install zsh completion"
    echo "  fish    Install fish completion"
    echo "  all     Install completion for all supported shells"
    echo "  auto    Auto-detect shell and install (default)"
    echo ""
    echo "Examples:"
    echo "  $0           # Auto-detect and install"
    echo "  $0 bash      # Install bash completion only"
    echo "  $0 all       # Install for all shells"
}

main() {
    local target_shell="${1:-auto}"

    # Check if we're in the right directory
    if [[ ! -d "completions" ]]; then
        log_error "Completions directory not found. Please run this script from the project root."
        exit 1
    fi

    log_info "AI Prototyping Tool - Shell Completion Installation"
    echo ""

    case "$target_shell" in
        "auto")
            local current_shell=$(get_shell)
            log_info "Auto-detected shell: $current_shell"
            case "$current_shell" in
                "bash")
                    install_bash_completion "bash"
                    ;;
                "zsh")
                    install_zsh_completion
                    ;;
                "fish")
                    install_fish_completion
                    ;;
                *)
                    log_warning "Unsupported shell: $current_shell"
                    log_info "Supported shells: bash, zsh, fish"
                    log_info "You can manually install completion by running: $0 [shell]"
                    ;;
            esac
            ;;
        "bash")
            install_bash_completion "bash"
            ;;
        "zsh")
            install_zsh_completion
            ;;
        "fish")
            install_fish_completion
            ;;
        "all")
            log_info "Installing completion for all supported shells..."
            install_bash_completion "bash"
            install_zsh_completion
            install_fish_completion
            ;;
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown shell: $target_shell"
            echo ""
            show_usage
            exit 1
            ;;
    esac

    echo ""
    log_success "Shell completion installation completed!"
    log_info "You may need to restart your shell for changes to take effect."
    log_info "Test completion by typing: ai-proto <TAB>"
}

# Run main function
main "$@"
