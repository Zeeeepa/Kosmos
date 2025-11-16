# Automated Setup Guide

**Purpose:** Comprehensive guide to automated installation and configuration of Kosmos

**For:** Users who want the fastest, easiest setup experience

---

## Overview

Kosmos provides automated setup scripts that handle the entire installation process. Instead of running multiple commands manually, you can use one-line commands to:

- Install Docker (if needed)
- Setup Python environment and dependencies
- Configure Neo4j knowledge graphs
- Verify everything works

**Time savings:** 5-10 minutes vs. 30-60 minutes manual setup

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Automation Scripts](#automation-scripts)
4. [Step-by-Step Guide](#step-by-step-guide)
5. [Using the Makefile](#using-the-makefile)
6. [Troubleshooting](#troubleshooting)
7. [Manual vs. Automated Comparison](#manual-vs-automated-comparison)
8. [Platform-Specific Notes](#platform-specific-notes)

---

## Quick Start

**For first-time setup on WSL2/Linux:**

```bash
# 1. Clone and enter directory
git clone https://github.com/jimmc414/Kosmos.git
cd Kosmos

# 2. Run complete automated setup
make install

# 3. (Optional) Setup Docker and Neo4j
make setup-docker  # One-time Docker installation (WSL2)
make setup-neo4j   # Setup knowledge graphs

# 4. Verify installation
make verify

# Done! 🎉
```

**For Mac/Windows with Docker Desktop already installed:**

```bash
# 1. Clone and enter directory
git clone https://github.com/jimmc414/Kosmos.git
cd Kosmos

# 2. Run environment setup
make install

# 3. Setup Neo4j
make setup-neo4j

# Done! 🎉
```

---

## Prerequisites

Before running automation scripts, ensure you have:

### Required
- **Python 3.11 or 3.12**
  ```bash
  python3 --version  # Should show 3.11.x or 3.12.x
  ```

- **Git** (to clone the repository)
  ```bash
  git --version
  ```

- **Make** (usually pre-installed on Linux/Mac)
  ```bash
  make --version
  ```

### Optional (for knowledge graphs)
- **Docker** (will be installed by `setup_docker_wsl2.sh` if needed)
- **Neo4j** (will be setup by `setup_neo4j.sh`)

### Platform-Specific

**WSL2 (Windows Subsystem for Linux):**
- Ubuntu 20.04+ or Debian-based distribution
- sudo privileges for Docker installation

**Mac:**
- Homebrew (for easy Python installation)
- Docker Desktop for Mac (recommended)

**Linux:**
- apt or yum package manager
- sudo privileges for Docker installation

---

## Automation Scripts

Kosmos provides four main automation scripts:

### 1. `scripts/setup_environment.sh`

**Purpose:** Complete Python environment setup

**What it does:**
- ✓ Checks Python 3.11+ is installed
- ✓ Creates virtual environment in `venv/`
- ✓ Upgrades pip to latest version
- ✓ Installs all Kosmos dependencies
- ✓ Copies `.env.example` to `.env` (if needed)
- ✓ Creates data directories (`data/`, `logs/`, `results/`, etc.)
- ✓ Runs database migrations (if configured)
- ✓ Runs `kosmos doctor` verification (if available)

**Usage:**
```bash
./scripts/setup_environment.sh
```

**Time:** 3-5 minutes

**Idempotent:** Safe to run multiple times

---

### 2. `scripts/setup_docker_wsl2.sh`

**Purpose:** Install Docker Engine on WSL2

**What it does:**
- ✓ Detects WSL2 environment and distribution
- ✓ Checks if Docker is already installed
- ✓ Adds Docker's official repository
- ✓ Installs Docker CE, CLI, and Compose plugin
- ✓ Starts Docker service
- ✓ Adds user to docker group
- ✓ Verifies installation with hello-world

**Usage:**
```bash
./scripts/setup_docker_wsl2.sh
```

**Time:** 5-10 minutes

**Note:** Requires logout/login after installation for group permissions

**Platform:** WSL2 only (Ubuntu/Debian)

---

### 3. `scripts/setup_neo4j.sh`

**Purpose:** Setup and start Neo4j knowledge graph database

**What it does:**
- ✓ Checks Docker is installed and running
- ✓ Verifies `docker-compose.yml` has Neo4j service
- ✓ Checks/creates `.env` configuration
- ✓ Creates data directories (`neo4j_data/`, `neo4j_logs/`, etc.)
- ✓ Starts Neo4j container via docker-compose
- ✓ Waits for Neo4j to be ready (health check)
- ✓ Verifies connectivity to ports 7474 and 7687
- ✓ Displays connection information and credentials

**Usage:**
```bash
./scripts/setup_neo4j.sh
```

**Time:** 1-2 minutes

**Requires:** Docker installed and running

**Idempotent:** Safe to run multiple times (restarts if already running)

---

### 4. Makefile Targets

**Purpose:** Convenient shortcuts for all automation

**Main targets:**

```bash
make help          # Show all available targets
make install       # Run setup_environment.sh
make setup-docker  # Run setup_docker_wsl2.sh
make setup-neo4j   # Run setup_neo4j.sh
make start         # Start all services
make stop          # Stop all services
make verify        # Run verification checks
make test          # Run test suite
```

See [Using the Makefile](#using-the-makefile) section for complete list.

---

## Step-by-Step Guide

### Scenario 1: Complete First-Time Setup (WSL2)

**Goal:** Install everything from scratch on WSL2

```bash
# Step 1: Clone repository
git clone https://github.com/jimmc414/Kosmos.git
cd Kosmos

# Step 2: Install Docker (one-time, requires sudo)
make setup-docker
# OR: ./scripts/setup_docker_wsl2.sh

# Step 3: IMPORTANT - Logout and login for docker group to take effect
exit
# Close and reopen terminal, then cd back to Kosmos directory
cd /path/to/Kosmos

# Step 4: Setup Python environment
make install
# OR: ./scripts/setup_environment.sh

# Step 5: Setup Neo4j
make setup-neo4j
# OR: ./scripts/setup_neo4j.sh

# Step 6: Configure API keys
nano .env
# Set your ANTHROPIC_API_KEY or other LLM provider credentials

# Step 7: Verify everything works
make verify
# OR: ./scripts/verify_deployment.sh

# Step 8: Run your first research query
source venv/bin/activate
kosmos research "How do neural networks learn?"
```

**Total time:** 15-20 minutes (including Docker installation)

---

### Scenario 2: Quick Setup (Docker Already Installed)

**Goal:** Setup Kosmos when Docker is already available

```bash
# Step 1: Clone repository
git clone https://github.com/jimmc414/Kosmos.git
cd Kosmos

# Step 2: Run automated setup
make install

# Step 3: Setup Neo4j
make setup-neo4j

# Step 4: Configure API keys
nano .env

# Step 5: Start using Kosmos
source venv/bin/activate
kosmos --help
```

**Total time:** 5-8 minutes

---

### Scenario 3: Environment Only (No Docker)

**Goal:** Setup Python environment without Docker services

```bash
# Step 1: Clone repository
git clone https://github.com/jimmc414/Kosmos.git
cd Kosmos

# Step 2: Setup Python environment
make install

# Step 3: Configure API keys
nano .env

# Step 4: Use Kosmos without knowledge graphs
source venv/bin/activate
kosmos research "Your question"
# Note: Knowledge graphs won't persist without Neo4j
```

**Total time:** 3-5 minutes

**Note:** Kosmos works without Neo4j, but knowledge graphs won't persist between sessions.

---

## Using the Makefile

The Makefile provides convenient shortcuts for all operations.

### Setup Commands

```bash
make install        # Complete environment setup
make setup-docker   # Install Docker (WSL2)
make setup-neo4j    # Setup Neo4j
make setup-env      # Python environment only
```

### Service Management

```bash
make start          # Start all services (dev profile)
make start-prod     # Start services (production profile)
make stop           # Stop all services
make restart        # Restart all services
make status         # Show service status
```

### Development

```bash
make verify         # Run deployment verification
make test           # Run all tests
make test-unit      # Unit tests only
make test-int       # Integration tests (requires services)
make lint           # Run linters
make format         # Format code
```

### Logs

```bash
make logs           # View logs from all services
make logs-neo4j     # Neo4j logs only
make logs-postgres  # PostgreSQL logs only
```

### Maintenance

```bash
make clean          # Remove caches and temp files
make clean-all      # Remove caches and venv
make db-migrate     # Run database migrations
make info           # Show environment information
```

### Knowledge Graph

```bash
make graph-stats    # View graph statistics
make graph-export   # Export graph to JSON
make graph-reset    # Clear all graph data
```

### Getting Help

```bash
make help           # Show all available targets
make info           # Show environment information
```

---

## Troubleshooting

### Issue: "Python 3.11 not found"

**Problem:** Python 3.11+ is required but not installed

**Solution:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

**Mac (with Homebrew):**
```bash
brew install python@3.11
```

**Verify:**
```bash
python3.11 --version
```

---

### Issue: "make: command not found"

**Problem:** Make is not installed

**Solution:**

**Ubuntu/Debian:**
```bash
sudo apt install make
```

**Mac:**
```bash
# Make is pre-installed with Xcode Command Line Tools
xcode-select --install
```

**Alternative:** Run scripts directly instead of using Makefile:
```bash
./scripts/setup_environment.sh  # Instead of: make install
```

---

### Issue: "Docker is not installed" (when running setup_neo4j.sh)

**Problem:** Neo4j setup requires Docker

**Solution:**

**Option 1: Use setup_docker_wsl2.sh (WSL2 only)**
```bash
./scripts/setup_docker_wsl2.sh
# Then logout/login
./scripts/setup_neo4j.sh
```

**Option 2: Install Docker Desktop (Windows/Mac)**
- Download from [docker.com](https://www.docker.com/products/docker-desktop/)
- Install and start Docker Desktop
- Run `./scripts/setup_neo4j.sh`

**Option 3: Use Kosmos without Neo4j**
- Skip Neo4j setup entirely
- Knowledge graphs won't persist, but research still works

---

### Issue: "Permission denied" when running scripts

**Problem:** Scripts don't have execute permissions

**Solution:**
```bash
chmod +x scripts/*.sh
```

Or run with bash explicitly:
```bash
bash scripts/setup_environment.sh
```

---

### Issue: "Docker daemon not running"

**Problem:** Docker is installed but not started

**Solution:**

**WSL2:**
```bash
sudo service docker start
```

**Docker Desktop (Windows/Mac):**
- Open Docker Desktop application
- Wait for "Docker is running" in system tray

**Verify:**
```bash
docker ps  # Should show running containers or empty table
```

---

### Issue: "Need to logout/login for docker group"

**Problem:** User added to docker group but permissions not yet applied

**Solution:**
```bash
# Exit WSL2 terminal
exit

# Close and reopen terminal
# Or from Windows PowerShell:
wsl --shutdown
wsl

# Verify docker works without sudo
docker ps
```

---

### Issue: "Neo4j health check failing"

**Problem:** Neo4j container starting but not becoming healthy

**Solution:**

```bash
# Check logs for specific error
docker compose logs neo4j

# Common issues:
# 1. Port conflict (something using 7474 or 7687)
docker ps -a  # Check for other containers

# 2. Insufficient memory
# Edit docker-compose.yml, increase memory limits

# 3. First-time startup taking longer
# Wait 60 seconds and try again
sleep 60
docker compose ps
```

---

### Issue: "Virtual environment activation not working"

**Problem:** `source venv/bin/activate` doesn't change prompt

**Solution:**

**Make sure you're in project directory:**
```bash
cd /path/to/Kosmos
ls venv/  # Should show bin/, lib/, etc.
```

**Try explicit path:**
```bash
source ./venv/bin/activate
```

**Verify activation:**
```bash
which python  # Should show /path/to/Kosmos/venv/bin/python
```

---

### Issue: "Module not found" errors after installation

**Problem:** Dependencies not installed correctly

**Solution:**

```bash
# Activate virtual environment first
source venv/bin/activate

# Reinstall dependencies
pip install -e .

# Or full reinstall
rm -rf venv/
./scripts/setup_environment.sh
```

---

## Manual vs. Automated Comparison

### Manual Installation

```bash
# ~30-60 minutes total

# 1. Install Docker (10-15 min)
# - Download Docker Desktop or follow official Docker install guide
# - Configure WSL2 integration
# - Start Docker
# - Verify installation

# 2. Setup Python Environment (10-15 min)
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e .
cp .env.example .env
nano .env  # Configure manually

# 3. Create Directories (2-3 min)
mkdir -p data logs results neo4j_data neo4j_logs postgres_data redis_data

# 4. Start Neo4j (5-10 min)
docker compose up -d neo4j
# Wait for startup
docker compose logs neo4j
# Verify ports
curl http://localhost:7474

# 5. Configure Database (5-10 min)
alembic upgrade head

# 6. Verify (5-10 min)
pytest tests/unit/ -v
kosmos doctor
```

### Automated Installation

```bash
# ~10-20 minutes total

# Complete setup
make install          # Python environment (3-5 min)
make setup-docker     # Docker installation (5-10 min, one-time)
# Logout/login for group permissions
make setup-neo4j      # Neo4j setup (1-2 min)
make verify           # Verification (1-2 min)

# Configure API keys
nano .env
```

**Time Savings:** 20-40 minutes

**Error Reduction:** Automated scripts handle:
- ✓ Correct repository setup
- ✓ Package dependency resolution
- ✓ Permission configuration
- ✓ Health check verification
- ✓ Common error detection

---

## Platform-Specific Notes

### WSL2 (Windows Subsystem for Linux)

**Recommended Setup:**

```bash
# Use setup_docker_wsl2.sh for Docker installation
./scripts/setup_docker_wsl2.sh

# This installs Docker Engine directly in WSL2 (not Docker Desktop)
```

**Advantages:**
- Native Linux Docker
- Better performance
- No Windows GUI dependency
- Direct docker-compose integration

**Considerations:**
- Requires `sudo service docker start` after WSL2 restart
- OR use Docker Desktop with WSL2 integration for automatic startup

**Alternative:** Docker Desktop for Windows
- Integrates with WSL2
- Auto-starts with Windows
- GUI management
- Simpler for beginners

---

### Mac

**Recommended Setup:**

1. **Install Docker Desktop for Mac** (manual step)
   - Download from [docker.com](https://www.docker.com/products/docker-desktop/)
   - Install and start

2. **Run automated setup:**
   ```bash
   make install
   make setup-neo4j
   ```

**Notes:**
- `setup_docker_wsl2.sh` is WSL2-specific, skip it on Mac
- Use Docker Desktop instead
- All other scripts work identically

---

### Linux (Native)

**Recommended Setup:**

```bash
# Install Docker (modify for your distro)
./scripts/setup_docker_wsl2.sh  # Works on Ubuntu/Debian

# For other distros, install Docker via official guide
# Then proceed with:
make install
make setup-neo4j
```

**Notes:**
- `setup_docker_wsl2.sh` works on Ubuntu/Debian
- For Fedora/RHEL/Arch, use your package manager
- All other scripts are distribution-agnostic

---

## Advanced Topics

### Running Individual Script Steps

If you prefer more control, run scripts individually:

```bash
# 1. Environment only
./scripts/setup_environment.sh

# 2. Docker only (WSL2)
./scripts/setup_docker_wsl2.sh

# 3. Neo4j only
./scripts/setup_neo4j.sh

# 4. Verification only
./scripts/verify_deployment.sh
```

### Customizing Script Behavior

**Skip virtual environment recreation:**
```bash
# When prompted by setup_environment.sh, answer "N"
# OR delete venv/ first if you want clean reinstall
rm -rf venv/
./scripts/setup_environment.sh
```

**Use existing .env:**
```bash
# Scripts preserve existing .env files
# They only create from .env.example if .env doesn't exist
```

**Non-interactive mode:**
```bash
# Most scripts support yes/no prompts
# Answer automatically in scripts:
yes | ./scripts/setup_neo4j.sh
```

### Integration with CI/CD

**GitHub Actions example:**

```yaml
name: Setup Kosmos
on: [push]
jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run automated setup
        run: |
          make install
          source venv/bin/activate
          kosmos doctor

      - name: Run tests
        run: make test-unit
```

---

## Next Steps After Setup

Once automated setup is complete:

1. **Configure API Keys** (`.env` file):
   ```bash
   nano .env
   # Set ANTHROPIC_API_KEY or your preferred LLM provider
   ```

2. **Run First Research Query:**
   ```bash
   source venv/bin/activate
   kosmos research "How do transformers work in neural networks?"
   ```

3. **Explore Knowledge Graph:**
   ```bash
   # View accumulated knowledge
   kosmos graph --stats

   # Access Neo4j Browser
   # Open: http://localhost:7474
   # Login: neo4j / kosmos-password
   ```

4. **Read Documentation:**
   - [User Guide](user-guide.md) - Complete feature reference
   - [World Model Guide](world_model_guide.md) - Knowledge graph usage
   - [Provider Setup](../providers/README.md) - LLM provider configuration

---

## Getting Help

### Documentation

- **This guide:** Automated setup procedures
- **README.md:** Quick start and overview
- **User Guide:** Complete feature documentation
- **World Model Guide:** Knowledge graph features

### Verification

```bash
# Run comprehensive verification
make verify

# Or manually:
./scripts/verify_deployment.sh
```

### Common Commands

```bash
# Show environment info
make info

# Show all Make targets
make help

# Check service status
make status

# View logs
make logs
```

### Support

- **GitHub Issues:** [github.com/jimmc414/Kosmos/issues](https://github.com/jimmc414/Kosmos/issues)
- **Discussions:** [github.com/jimmc414/Kosmos/discussions](https://github.com/jimmc414/Kosmos/discussions)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-15
**Status:** ✅ Complete automation available
