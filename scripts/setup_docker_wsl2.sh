#!/bin/bash
#
# Docker Installation Script for WSL2
#
# This script automates Docker Engine installation on WSL2 (Ubuntu/Debian).
# It follows the official Docker installation guide and includes proper error handling.
#
# Usage:
#   ./scripts/setup_docker_wsl2.sh
#
# Requirements:
#   - WSL2 environment
#   - Ubuntu or Debian-based distribution
#   - sudo privileges
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
readonly SCRIPT_NAME="Docker WSL2 Setup"
readonly DOCKER_MIN_VERSION="20.10"

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
# Environment Detection
#============================================================================

detect_environment() {
    print_step "Detecting environment..."

    # Check if running in WSL2
    if ! grep -qi microsoft /proc/version; then
        print_error "This script is designed for WSL2 environments"
        print_info "Detected: $(uname -a)"
        exit 1
    fi
    print_success "WSL2 environment detected"

    # Detect distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        print_success "Distribution: $NAME $VERSION"

        # Check if Ubuntu or Debian
        if [[ "$ID" != "ubuntu" ]] && [[ "$ID" != "debian" ]]; then
            print_warning "This script is tested on Ubuntu/Debian"
            print_info "Your distribution: $ID"
            read -p "Continue anyway? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    else
        print_error "Cannot detect Linux distribution"
        exit 1
    fi
}

#============================================================================
# Docker Installation Check
#============================================================================

check_existing_docker() {
    print_step "Checking for existing Docker installation..."

    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
        print_success "Docker already installed: v$DOCKER_VERSION"

        # Check if Docker is running
        if docker ps &> /dev/null; then
            print_success "Docker daemon is running"
        else
            print_warning "Docker is installed but daemon is not running"
            print_info "Attempting to start Docker..."
            sudo service docker start || print_error "Failed to start Docker service"
        fi

        echo
        read -p "Docker is already installed. Reinstall? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Skipping installation. Exiting."
            exit 0
        fi
    else
        print_info "Docker not found. Proceeding with installation."
    fi
}

#============================================================================
# Pre-installation
#============================================================================

install_prerequisites() {
    print_step "Installing prerequisites..."

    print_info "Updating package index..."
    sudo apt-get update -qq

    print_info "Installing required packages..."
    sudo apt-get install -y -qq \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        apt-transport-https \
        software-properties-common

    print_success "Prerequisites installed"
}

#============================================================================
# Docker Installation
#============================================================================

add_docker_repository() {
    print_step "Adding Docker repository..."

    # Create keyrings directory
    sudo mkdir -p /etc/apt/keyrings

    # Remove old GPG key if exists
    sudo rm -f /etc/apt/keyrings/docker.gpg

    # Add Docker's official GPG key
    print_info "Downloading Docker GPG key..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Set up the repository
    print_info "Adding Docker repository to sources..."
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    print_success "Docker repository added"
}

install_docker() {
    print_step "Installing Docker Engine..."

    # Update package index
    print_info "Updating package index with Docker repository..."
    sudo apt-get update -qq

    # Install Docker packages
    print_info "Installing Docker packages..."
    sudo apt-get install -y -qq \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-compose-plugin

    print_success "Docker Engine installed"
}

#============================================================================
# Post-installation Configuration
#============================================================================

configure_docker() {
    print_step "Configuring Docker..."

    # Add current user to docker group
    print_info "Adding user '$USER' to docker group..."
    sudo usermod -aG docker "$USER"

    # Start Docker service
    print_info "Starting Docker service..."
    sudo service docker start

    # Enable Docker to start on boot (if systemd available)
    if command -v systemctl &> /dev/null; then
        print_info "Enabling Docker service..."
        sudo systemctl enable docker 2>/dev/null || print_warning "systemctl not fully available in WSL2"
    fi

    print_success "Docker configured"
}

#============================================================================
# Verification
#============================================================================

verify_installation() {
    print_step "Verifying Docker installation..."

    # Check Docker version
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
        print_success "Docker version: $DOCKER_VERSION"
    else
        print_error "Docker command not found"
        return 1
    fi

    # Check Docker Compose
    if docker compose version &> /dev/null; then
        COMPOSE_VERSION=$(docker compose version --short)
        print_success "Docker Compose version: $COMPOSE_VERSION"
    else
        print_warning "Docker Compose not available"
    fi

    # Check Docker daemon
    if sudo docker ps &> /dev/null; then
        print_success "Docker daemon is running"
    else
        print_error "Docker daemon is not running"
        print_info "Try: sudo service docker start"
        return 1
    fi

    # Run hello-world container
    print_info "Testing Docker with hello-world container..."
    if sudo docker run --rm hello-world &> /dev/null; then
        print_success "Docker is working correctly"
    else
        print_warning "Docker test container failed (this may be normal on first run)"
    fi
}

#============================================================================
# Post-installation Instructions
#============================================================================

print_next_steps() {
    print_header "Installation Complete"

    echo -e "${GREEN}Docker has been successfully installed!${NC}\n"

    print_warning "IMPORTANT: You need to log out and log back in for group changes to take effect"
    print_info "After logging back in, you can use Docker without sudo\n"

    echo "Next steps:"
    echo "  1. Log out of WSL2:"
    echo "     ${BLUE}exit${NC}"
    echo ""
    echo "  2. Close and reopen your terminal"
    echo ""
    echo "  3. Verify Docker works without sudo:"
    echo "     ${BLUE}docker run hello-world${NC}"
    echo ""
    echo "  4. Start Neo4j for Kosmos:"
    echo "     ${BLUE}cd /mnt/c/python/Kosmos${NC}"
    echo "     ${BLUE}./scripts/setup_neo4j.sh${NC}"
    echo ""
    echo "Alternative (use now with sudo until you logout/login):"
    echo "  ${BLUE}sudo docker run hello-world${NC}"
    echo ""
}

#============================================================================
# Main Installation Flow
#============================================================================

main() {
    print_header "$SCRIPT_NAME"

    echo "This script will install Docker Engine on WSL2."
    echo "It will:"
    echo "  - Install Docker CE (Community Edition)"
    echo "  - Install Docker Compose plugin"
    echo "  - Configure Docker to run on startup"
    echo "  - Add your user to the docker group"
    echo ""
    read -p "Continue with installation? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled."
        exit 0
    fi
    echo ""

    # Run installation steps
    detect_environment
    check_existing_docker
    install_prerequisites
    add_docker_repository
    install_docker
    configure_docker
    verify_installation

    # Success
    print_next_steps
}

# Run main function
main "$@"
