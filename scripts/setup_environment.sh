#!/bin/bash
#
# Kosmos Development Environment Setup Script
#
# This script automates the complete development environment setup for Kosmos.
# It handles Python environment, dependencies, database setup, and configuration.
#
# Usage:
#   ./scripts/setup_environment.sh
#
# Requirements:
#   - Python 3.11 or higher
#   - pip
#   - git (for version detection)
#

set -e  # Exit on error
set -u  # Error on undefined variables
set -o pipefail  # Catch errors in pipes

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Script configuration
readonly SCRIPT_NAME="Kosmos Environment Setup"
readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly PYTHON_MIN_VERSION="3.11"
readonly VENV_DIR="venv"

#============================================================================
# Helper Functions
#============================================================================

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "  $1"
}

#============================================================================
# Python Version Check
#============================================================================

check_python() {
    print_step "Checking Python version..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        print_info "Please install Python ${PYTHON_MIN_VERSION} or higher"
        exit 1
    fi

    local python_version=$(python3 --version | grep -oP '\d+\.\d+')
    print_info "Found Python $python_version"

    # Compare versions
    if awk "BEGIN {exit !($python_version >= $PYTHON_MIN_VERSION)}"; then
        print_success "Python version is ${python_version} (>= ${PYTHON_MIN_VERSION})"
    else
        print_error "Python ${python_version} is too old"
        print_info "Please install Python ${PYTHON_MIN_VERSION} or higher"
        exit 1
    fi

    # Check for pip
    if ! python3 -m pip --version &> /dev/null; then
        print_error "pip is not installed"
        print_info "Install pip: sudo apt install python3-pip"
        exit 1
    fi
    print_success "pip is available"

    # Check for venv module
    if ! python3 -m venv --help &> /dev/null; then
        print_warning "venv module not found"
        print_info "Installing python3-venv..."
        sudo apt install -y python3-venv || print_error "Failed to install python3-venv"
    fi
    print_success "venv module is available"
}

#============================================================================
# Virtual Environment Setup
#============================================================================

setup_virtual_environment() {
    print_step "Setting up virtual environment..."

    cd "$PROJECT_ROOT"

    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR/"
        echo ""
        read -p "Recreate virtual environment? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi

    print_info "Creating virtual environment in $VENV_DIR/..."
    python3 -m venv "$VENV_DIR"

    print_success "Virtual environment created"
}

activate_virtual_environment() {
    print_step "Activating virtual environment..."

    # Source the activation script
    source "$PROJECT_ROOT/$VENV_DIR/bin/activate"

    # Verify activation
    if [ -n "${VIRTUAL_ENV:-}" ]; then
        print_success "Virtual environment activated: $VIRTUAL_ENV"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi

    # Upgrade pip
    print_info "Upgrading pip..."
    python -m pip install --upgrade pip --quiet

    print_success "pip upgraded to $(pip --version | grep -oP '\d+\.\d+\.\d+')"
}

#============================================================================
# Dependencies Installation
#============================================================================

install_dependencies() {
    print_step "Installing Kosmos dependencies..."

    cd "$PROJECT_ROOT"

    # Check for requirements files
    if [ ! -f "pyproject.toml" ] && [ ! -f "requirements.txt" ]; then
        print_error "Neither pyproject.toml nor requirements.txt found"
        exit 1
    fi

    # Install in editable mode if pyproject.toml exists
    if [ -f "pyproject.toml" ]; then
        print_info "Installing from pyproject.toml (editable mode)..."
        pip install -e . --quiet
        print_success "Kosmos installed in editable mode"
    elif [ -f "requirements.txt" ]; then
        print_info "Installing from requirements.txt..."
        pip install -r requirements.txt --quiet
        print_success "Dependencies installed"
    fi

    # Install development dependencies if available
    if [ -f "requirements-dev.txt" ]; then
        print_info "Installing development dependencies..."
        pip install -r requirements-dev.txt --quiet
        print_success "Development dependencies installed"
    fi
}

verify_installation() {
    print_step "Verifying Kosmos installation..."

    # Try to import kosmos
    if python -c "import kosmos; print('✓ Kosmos version:', kosmos.__version__)" 2>/dev/null; then
        print_success "Kosmos package is importable"
    else
        print_warning "Could not import kosmos package"
        print_info "This may be normal if using requirements.txt instead of setup.py"
    fi

    # Check for kosmos CLI
    if command -v kosmos &> /dev/null; then
        local kosmos_version=$(kosmos --version 2>/dev/null || echo "unknown")
        print_success "kosmos CLI is available: $kosmos_version"
    else
        print_warning "kosmos CLI not found in PATH"
        print_info "You may need to activate the virtual environment:"
        print_info "  source $VENV_DIR/bin/activate"
    fi
}

#============================================================================
# Configuration Setup
#============================================================================

setup_configuration() {
    print_step "Setting up configuration..."

    cd "$PROJECT_ROOT"

    # Create .env from example if needed
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_info "Creating .env from .env.example..."
            cp .env.example .env
            print_success ".env file created"
            print_warning "Please review .env and update with your API keys and settings"
        else
            print_warning ".env.example not found - skipping .env creation"
        fi
    else
        print_success ".env file already exists"
    fi

    # Create config directory if needed
    if [ ! -d "config" ]; then
        print_info "Creating config directory..."
        mkdir -p config
    fi
}

#============================================================================
# Data Directories Setup
#============================================================================

create_data_directories() {
    print_step "Creating data directories..."

    cd "$PROJECT_ROOT"

    local directories=(
        "data"
        "logs"
        "results"
        "experiments"
        "neo4j_data"
        "neo4j_logs"
        "postgres_data"
        "redis_data"
    )

    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_info "Created: $dir/"
        fi
    done

    print_success "Data directories created"
}

#============================================================================
# Database Setup
#============================================================================

setup_databases() {
    print_step "Setting up databases..."

    cd "$PROJECT_ROOT"

    # Check if alembic is available
    if command -v alembic &> /dev/null; then
        print_info "Running database migrations..."
        if alembic upgrade head 2>/dev/null; then
            print_success "Database migrations complete"
        else
            print_warning "Database migrations failed or not configured"
            print_info "You may need to configure your database first"
        fi
    else
        print_info "alembic not found - skipping migrations"
        print_info "Run migrations manually when database is configured:"
        print_info "  alembic upgrade head"
    fi
}

#============================================================================
# Verification
#============================================================================

run_verification() {
    print_step "Running system verification..."

    cd "$PROJECT_ROOT"

    # Check if kosmos doctor command exists
    if command -v kosmos &> /dev/null && kosmos doctor --help &> /dev/null 2>&1; then
        print_info "Running kosmos doctor..."
        if kosmos doctor 2>&1 | head -20; then
            print_success "System verification complete"
        else
            print_warning "Some checks may have failed - review output above"
        fi
    else
        print_info "kosmos doctor command not available - skipping automated verification"

        # Manual verification checks
        print_info "Checking key dependencies..."

        local deps=("anthropic" "pydantic" "sqlalchemy" "numpy" "pandas")
        for dep in "${deps[@]}"; do
            if python -c "import $dep" 2>/dev/null; then
                print_info "  ✓ $dep"
            else
                print_info "  ✗ $dep (not installed)"
            fi
        done
    fi
}

#============================================================================
# Display Next Steps
#============================================================================

display_next_steps() {
    print_header "Environment Setup Complete"

    echo -e "${GREEN}Kosmos development environment is ready!${NC}\n"

    echo "Your virtual environment is located at:"
    echo "  ${BLUE}$PROJECT_ROOT/$VENV_DIR/${NC}"
    echo ""

    echo "To use Kosmos:"
    echo "  1. Activate the virtual environment:"
    echo "     ${BLUE}source $VENV_DIR/bin/activate${NC}"
    echo ""
    echo "  2. Configure your .env file with API keys:"
    echo "     ${BLUE}nano .env${NC}"
    echo ""
    echo "  3. (Optional) Set up Neo4j for knowledge graphs:"
    echo "     ${BLUE}./scripts/setup_neo4j.sh${NC}"
    echo ""
    echo "  4. Run your first research query:"
    echo "     ${BLUE}kosmos research \"Your research question\"${NC}"
    echo ""

    echo "Useful commands:"
    echo "  ${BLUE}kosmos --help${NC}          - Show all commands"
    echo "  ${BLUE}kosmos doctor${NC}          - Verify installation"
    echo "  ${BLUE}kosmos config --show${NC}   - Show configuration"
    echo "  ${BLUE}kosmos graph --stats${NC}   - View knowledge graph (if Neo4j running)"
    echo ""

    if [ -f ".env.example" ] && [ -f ".env" ]; then
        print_warning "Don't forget to update .env with your API keys!"
        echo "  Required: ANTHROPIC_API_KEY or LLM_PROVIDER configuration"
        echo ""
    fi
}

#============================================================================
# Main Setup Flow
#============================================================================

main() {
    print_header "$SCRIPT_NAME"

    echo "This script will set up your complete Kosmos development environment."
    echo "It will:"
    echo "  - Verify Python ${PYTHON_MIN_VERSION}+ installation"
    echo "  - Create and configure virtual environment"
    echo "  - Install all dependencies"
    echo "  - Set up configuration files"
    echo "  - Create data directories"
    echo "  - Run database migrations"
    echo "  - Verify installation"
    echo ""

    # Run setup steps
    check_python
    setup_virtual_environment
    activate_virtual_environment
    install_dependencies
    verify_installation
    setup_configuration
    create_data_directories
    setup_databases
    run_verification
    display_next_steps

    print_success "Setup complete!"
    echo ""
    echo -e "${YELLOW}Note:${NC} Your virtual environment is currently activated in this shell."
    echo "To use Kosmos in a new terminal, run:"
    echo "  ${BLUE}source $VENV_DIR/bin/activate${NC}"
}

# Run main function
main "$@"
