#!/bin/bash
#
# Neo4j Setup Script for Kosmos
#
# This script automates Neo4j setup and startup using Docker Compose.
# It creates necessary directories, validates configuration, and starts the Neo4j container.
#
# Usage:
#   ./scripts/setup_neo4j.sh
#
# Requirements:
#   - Docker installed and running
#   - docker-compose.yml configured (already present in Kosmos)
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
readonly SCRIPT_NAME="Neo4j Setup for Kosmos"
readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly NEO4J_HTTP_PORT=7474
readonly NEO4J_BOLT_PORT=7687
readonly HEALTH_CHECK_TIMEOUT=60
readonly HEALTH_CHECK_INTERVAL=2

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
# Prerequisites Check
#============================================================================

check_docker() {
    print_step "Checking Docker availability..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        print_info "Please install Docker first:"
        print_info "  ${BLUE}./scripts/setup_docker_wsl2.sh${NC}"
        exit 1
    fi
    print_success "Docker is installed"

    # Check if Docker daemon is running
    if ! docker ps &> /dev/null; then
        print_error "Docker daemon is not running"
        print_info "Please start Docker:"
        print_info "  ${BLUE}sudo service docker start${NC}"
        print_info "Or if using Docker Desktop, start it from Windows"
        exit 1
    fi
    print_success "Docker daemon is running"

    # Check for docker compose
    if docker compose version &> /dev/null; then
        print_success "Docker Compose is available"
    else
        print_error "Docker Compose plugin not found"
        exit 1
    fi
}

check_working_directory() {
    print_step "Checking working directory..."

    cd "$PROJECT_ROOT"

    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found in $PROJECT_ROOT"
        exit 1
    fi
    print_success "Found docker-compose.yml"

    # Check if neo4j service is defined
    if ! grep -q "neo4j:" docker-compose.yml; then
        print_error "Neo4j service not found in docker-compose.yml"
        exit 1
    fi
    print_success "Neo4j service is defined"
}

#============================================================================
# Environment Configuration
#============================================================================

check_env_configuration() {
    print_step "Checking environment configuration..."

    # Check for .env file
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning ".env file not found"
            print_info "Copying .env.example to .env..."
            cp .env.example .env
            print_success "Created .env from .env.example"
            print_warning "Please review .env and update with your configuration"
        else
            print_error "Neither .env nor .env.example found"
            exit 1
        fi
    else
        print_success ".env file exists"
    fi

    # Check for required Neo4j variables
    if [ -f ".env" ]; then
        source .env 2>/dev/null || true

        # Check Neo4j URI
        if [ -z "${NEO4J_URI:-}" ]; then
            print_warning "NEO4J_URI not set in .env (will use default)"
        else
            print_success "NEO4J_URI configured: $NEO4J_URI"
        fi

        # Check Neo4j password
        if [ -z "${NEO4J_PASSWORD:-}" ]; then
            print_warning "NEO4J_PASSWORD not set in .env (will use default from docker-compose.yml)"
        else
            print_success "NEO4J_PASSWORD configured"
        fi
    fi
}

#============================================================================
# Directory Setup
#============================================================================

create_data_directories() {
    print_step "Creating data directories..."

    local directories=(
        "neo4j_data"
        "neo4j_logs"
        "neo4j_import"
        "neo4j_plugins"
        "postgres_data"
        "redis_data"
        "logs"
        "results"
    )

    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_info "Created: $dir/"
        else
            print_info "Exists: $dir/"
        fi
    done

    print_success "Data directories ready"
}

#============================================================================
# Neo4j Container Management
#============================================================================

check_existing_neo4j() {
    print_step "Checking for existing Neo4j container..."

    if docker ps -a --format '{{.Names}}' | grep -q "kosmos-neo4j"; then
        local container_status=$(docker inspect -f '{{.State.Status}}' kosmos-neo4j 2>/dev/null || echo "not found")

        if [ "$container_status" == "running" ]; then
            print_warning "Neo4j container is already running"
            echo ""
            read -p "Restart Neo4j container? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_info "Restarting Neo4j..."
                docker compose restart neo4j
                print_success "Neo4j restarted"
                return 0
            else
                print_info "Using existing running container"
                return 0
            fi
        elif [ "$container_status" == "exited" ] || [ "$container_status" == "created" ]; then
            print_warning "Neo4j container exists but is not running (status: $container_status)"
            print_info "Starting existing container..."
            docker compose start neo4j
            return 0
        fi
    fi

    return 1
}

start_neo4j() {
    print_step "Starting Neo4j container..."

    # Start Neo4j with docker compose
    print_info "Running: docker compose up -d neo4j"
    docker compose up -d neo4j

    print_success "Neo4j container started"
}

#============================================================================
# Health Checks
#============================================================================

wait_for_neo4j() {
    print_step "Waiting for Neo4j to be ready..."

    local elapsed=0
    local ready=false

    print_info "This may take up to ${HEALTH_CHECK_TIMEOUT}s for first-time startup..."

    while [ $elapsed -lt $HEALTH_CHECK_TIMEOUT ]; do
        # Check HTTP port
        if curl -s http://localhost:${NEO4J_HTTP_PORT} > /dev/null 2>&1; then
            ready=true
            break
        fi

        # Show progress
        echo -n "."
        sleep $HEALTH_CHECK_INTERVAL
        elapsed=$((elapsed + HEALTH_CHECK_INTERVAL))
    done
    echo ""

    if [ "$ready" = true ]; then
        print_success "Neo4j is ready (${elapsed}s)"
    else
        print_error "Neo4j did not become ready within ${HEALTH_CHECK_TIMEOUT}s"
        print_info "Check logs with: docker compose logs neo4j"
        exit 1
    fi
}

verify_connectivity() {
    print_step "Verifying Neo4j connectivity..."

    # Check HTTP port (Web UI)
    if curl -s http://localhost:${NEO4J_HTTP_PORT} > /dev/null; then
        print_success "HTTP port ${NEO4J_HTTP_PORT} is accessible"
    else
        print_error "Cannot connect to HTTP port ${NEO4J_HTTP_PORT}"
    fi

    # Check Bolt port (database connection)
    if nc -zv localhost ${NEO4J_BOLT_PORT} 2>&1 | grep -q "succeeded\|open"; then
        print_success "Bolt port ${NEO4J_BOLT_PORT} is accessible"
    else
        print_warning "Cannot verify Bolt port ${NEO4J_BOLT_PORT} (nc not available or port not open)"
        print_info "Neo4j may still be initializing"
    fi

    # Check container health
    local health_status=$(docker inspect --format='{{.State.Health.Status}}' kosmos-neo4j 2>/dev/null || echo "unknown")
    if [ "$health_status" == "healthy" ]; then
        print_success "Container health check: healthy"
    elif [ "$health_status" == "starting" ]; then
        print_warning "Container health check: starting (still initializing)"
    else
        print_warning "Container health check: $health_status"
    fi
}

#============================================================================
# Display Connection Information
#============================================================================

display_connection_info() {
    print_header "Neo4j is Ready"

    echo -e "${GREEN}Neo4j has been successfully configured and started!${NC}\n"

    echo "Connection Details:"
    echo "  ${BLUE}Web UI:${NC}      http://localhost:${NEO4J_HTTP_PORT}"
    echo "  ${BLUE}Bolt URI:${NC}    bolt://localhost:${NEO4J_BOLT_PORT}"
    echo "  ${BLUE}Username:${NC}    neo4j"
    echo "  ${BLUE}Password:${NC}    kosmos-password (from docker-compose.yml)"
    echo ""

    echo "Useful Commands:"
    echo "  ${BLUE}View logs:${NC}"
    echo "    docker compose logs neo4j"
    echo ""
    echo "  ${BLUE}Follow logs:${NC}"
    echo "    docker compose logs -f neo4j"
    echo ""
    echo "  ${BLUE}Stop Neo4j:${NC}"
    echo "    docker compose stop neo4j"
    echo ""
    echo "  ${BLUE}Restart Neo4j:${NC}"
    echo "    docker compose restart neo4j"
    echo ""
    echo "  ${BLUE}Access Neo4j shell:${NC}"
    echo "    docker exec -it kosmos-neo4j cypher-shell -u neo4j -p kosmos-password"
    echo ""

    echo "Next Steps:"
    echo "  1. Open Neo4j Browser: ${BLUE}http://localhost:${NEO4J_HTTP_PORT}${NC}"
    echo "  2. Login with credentials above"
    echo "  3. Run Kosmos research to build knowledge graph:"
    echo "     ${BLUE}kosmos research \"Your research question\"${NC}"
    echo "  4. View graph statistics:"
    echo "     ${BLUE}kosmos graph --stats${NC}"
    echo ""

    # Test Python connectivity (optional)
    print_info "Testing Python connectivity..."
    if command -v python3 &> /dev/null; then
        if python3 -c "from kosmos.config import get_config; print('✓ Configuration loaded')" 2>/dev/null; then
            print_success "Kosmos configuration is valid"
        else
            print_warning "Could not load Kosmos configuration (may not be installed)"
        fi
    fi
}

#============================================================================
# Main Setup Flow
#============================================================================

main() {
    print_header "$SCRIPT_NAME"

    echo "This script will set up and start Neo4j for Kosmos."
    echo ""

    # Run setup steps
    check_docker
    check_working_directory
    check_env_configuration
    create_data_directories

    # Handle existing container or start new one
    if ! check_existing_neo4j; then
        start_neo4j
    fi

    wait_for_neo4j
    verify_connectivity
    display_connection_info

    print_success "Setup complete!"
}

# Run main function
main "$@"
