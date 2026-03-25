# Python Development Template

Minimal Python template with Docker and code-server for remote VSCode development.

## Setup

1. **Clone and navigate:**
   ```bash
   git clone <repo> my-python-project
   cd my-python-project
   ```

2. **Start development environment:**
   ```bash
   docker compose up -d
   ```

3. **Access VSCode:**
   - Open: `http://localhost:8443`
   - Password: `dev`

## Using as Base for New Projects

1. Remove git history: `rm -rf .git`
2. Add your dependencies to `requirements.txt`
3. Rebuild: `docker compose build --no-cache`

## Common Commands

- Start: `docker compose up -d`
- Stop: `docker compose down`
- Rebuild: `docker compose build --no-cache`
- View logs: `docker compose logs -f dev`
- Execute command: `docker compose exec dev python script.py`
