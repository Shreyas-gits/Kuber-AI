#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting development environment setup...${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ------UV Installation and Setup-------
# Check if uv is installed
echo "Checking for uv installation..."
if command_exists uv; then
    print_status "uv is already installed"
    uv --version
else
    echo "Installing uv..."
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        # Try normal installation first
        if curl -LsSf https://astral.sh/uv/install.sh | sh; then
            print_status "uv installed successfully"
        else
            print_warning "Standard installation failed, trying with --insecure flag..."
            if curl -LsSf --insecure https://astral.sh/uv/install.sh | sh; then
                print_status "uv installed successfully (with --insecure)"
            else
                print_error "Failed to install uv even with --insecure flag"
                print_error "Please install uv manually: https://docs.astral.sh/uv/getting-started/installation/"
                exit 1
            fi
        fi
        
        # Add uv to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"
        
        # Try to source shell configs safely (only if they exist and we're in the right shell)
        if [[ -n "$ZSH_VERSION" ]] && [[ -f "$HOME/.zshrc" ]]; then
            source "$HOME/.zshrc" 2>/dev/null || true
        elif [[ -n "$BASH_VERSION" ]] && [[ -f "$HOME/.bashrc" ]]; then
            source "$HOME/.bashrc" 2>/dev/null || true
        fi
    else
        print_error "Unsupported OS for automatic uv installation"
        exit 1
    fi
    
    # Verify uv is now available
    if command_exists uv; then
        print_status "uv is now available"
        uv --version
    else
        print_error "uv installation failed or not in PATH"
        print_error "Manual steps:"
        print_error "1. Add to your shell profile: export PATH=\"\$HOME/.local/bin:\$PATH\""
        print_error "2. Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
        print_error "3. Re-run this script"
        exit 1
    fi
fi

# Create virtual environment
echo "Setting up virtual environment..."
if [[ -d ".venv" ]]; then
    print_warning "Virtual environment already exists"
else
    uv venv
    print_status "Virtual environment created"
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
uv sync
print_status "Dependencies installed from uv.lock"

# Install pre-commit if not already installed
echo "Setting up pre-commit..."
if uv run python -c "import pre_commit" 2>/dev/null; then
    print_status "pre-commit is already installed"
else
    uv add --dev pre-commit
    print_status "pre-commit installed"
fi

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
uv run pre-commit install
print_status "Pre-commit hooks installed"

# Add pre-commit dependencies to dev requirements
echo "Adding pre-commit tools to dev dependencies..."
uv add --dev black ruff
print_status "Dev dependencies added"

echo ""
echo -e "${GREEN}🎉 Development environment setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Your dependencies are installed from uv.lock"
echo "3. Pre-commit is configured and ready to use"
echo "4. Run 'uv run pre-commit run --all-files' to test pre-commit hooks"
echo ""
echo "Happy coding! 🚀"

