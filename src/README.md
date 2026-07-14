# Blank — Web Project Template

A scaffold template for building web applications with a Python backend, a
Node.js frontend, and a PostgreSQL database running in Docker.

## Project Structure

```
src/
├── backend/         # Python application (FastAPI, business logic)
├── frontend/        # Node.js application (React + Vite)
├── docker/           # Dockerfiles, Caddy & Nginx configuration
├── bin/              # Helper scripts (compose, init-*)
├── compose.yaml      # Base Docker Compose configuration
├── compose.{env}.yaml  # Environment-specific overrides
├── env/              # Environment variable files
├── secrets/          # Secrets (gitignored except directory structure)
├── Makefile          # Convenience targets for common operations
└── VERSION           # Application version (SemVer)
```

## Prerequisites

| Tool           | Minimum version | Notes                      |
| -------------- | --------------- | -------------------------- |
| **Docker**     | latest          | Includes Docker Compose v2  |
| **Python**     | `>= 3.14`       | Backend runtime (for local dev without Docker) |
| **Node.js**    | `>= 24`         | Frontend runtime (for local dev without Docker) |

PostgreSQL, Caddy, and all service dependencies run as containers — only Docker
is strictly required.

```bash
docker --version     # Docker with Compose v2
python --version     # Python 3.14 or newer (optional)
node --version       # v24 or newer (optional)
```

## Quick Start (Development)

```bash
cd src

# 1. Initialize the development environment (secrets, env file, VERSION)
make init

# 2. Validate the Compose configuration
make ENV=dev config

# 3. Start all services
make ENV=dev up
```

The application is now available at **http://localhost:8080**.

To stop:

```bash
make ENV=dev down
```

## Environments

The project supports four environments managed through Docker Compose
overlay files and environment-specific variable files.

### Environment Overview

| Environment | Compose files                          | Env file        | Make example         |
| ----------- | -------------------------------------- | --------------- | -------------------- |
| `dev`       | `compose.yaml` + `compose.dev.yaml`    | `env/dev.env`   | `make ENV=dev up`    |
| `test`      | `compose.yaml` + `compose.test.yaml`   | `env/test.env`  | `make ENV=test up`   |
| `staging`   | `compose.yaml` + `compose.prod.yaml`   | `env/staging.env` | _(see below)_     |
| `prod`      | `compose.yaml` + `compose.prod.yaml`   | `env/prod.env`  | _(see below)_        |

### Development (`dev`)

For daily development. Backend and frontend run with hot-reload, Caddy
proxies requests on port 8080.

```bash
make init                    # Generate secrets and env files
make ENV=dev config          # Validate configuration
make ENV=dev up              # Start services (detached)
make ENV=dev logs            # Follow logs
make ENV=dev down            # Stop and remove containers
```

Individual services from the host (without Docker):

```bash
# Backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && pnpm dev
```

### Test (`test`)

Runs the test suite in ephemeral containers. The database uses a `tmpfs`
volume — data is discarded when containers stop.

```bash
make init-test               # Generate test secrets and env files
make ENV=test config         # Validate configuration
make ENV=test build          # Build test images
make ENV=test up             # Run tests (containers exit when done)
make ENV=test down --volumes # Clean up
```

Individual test runs from the host:

```bash
cd backend
uv run pytest                              # All tests
uv run pytest -v                           # Verbose
uv run pytest tests/test_health.py         # Single file
uv run pytest -k "health and not full"     # Filter by expression
uv run pytest -x                           # Stop on first failure
```

### Staging (`staging`)

Pre-production validation. Uses production-like Compose configuration.

```bash
# 1. Copy and edit the environment file
cp env/staging.env.example env/staging.env
# → Edit env/staging.env with your staging values

# 2. Create secrets directory and files
mkdir -p secrets/staging
openssl rand -hex 32 > secrets/staging/health_full_token
openssl rand -base64 18 | tr -d '\n/+=' > secrets/staging/postgres_password

# 3. Deploy
make ENV=staging config
make ENV=staging up
```

### Production (`prod`)

Production deployment. Uses immutable image digests, strict security
settings, and HTTPS via Caddy with Let's Encrypt.

```bash
# 1. Copy and edit the environment file
cp env/prod.env.example env/prod.env
# → Edit env/prod.env with your production values

# 2. Create secrets directory and files
mkdir -p /etc/myapp/secrets/prod
openssl rand -hex 32 > /etc/myapp/secrets/prod/health_full_token
openssl rand -base64 18 | tr -d '\n/+=' > /etc/myapp/secrets/prod/postgres_password

# 3. Deploy
make ENV=prod config
make ENV=prod up
```

## Makefile Reference

| Target       | Description                                      |
| ------------ | ------------------------------------------------ |
| `init`       | Generate dev secrets, env files, and VERSION     |
| `init-test`  | Generate test secrets and env files              |
| `config`     | Validate the Compose configuration               |
| `build`      | Build (or rebuild) service images                |
| `up`         | Start services (validates config first)          |
| `start`      | Start stopped services without rebuilding        |
| `stop`       | Stop services without removing containers        |
| `restart`    | Restart services                                 |
| `down`       | Stop and remove containers                       |
| `logs`       | Follow logs of the `app` service                 |
| `ps`         | List running services                            |
| `shell`      | Open a shell in the `app` container              |
| `run`        | Run a one-off command (`CMD=... make run`)       |
| `test`       | Run the full test suite via Docker Compose       |
| `destroy`    | Remove containers **and volumes** (needs `CONFIRM=yes`) |

All targets accept `ENV` to select the environment:

```bash
make ENV=dev up        # Start dev
make ENV=test up       # Run tests
make ENV=staging up    # Start staging
make ENV=prod config   # Validate production config
```

## Reusing This Template

1. **Clone** the repository: `git clone ...`
2. **Rename** the project in key files:
   - `src/backend/pyproject.toml` — `name`, `description`
   - `src/frontend/package.json` — `name`, `description`
   - `src/env/*.env` and `src/env/*.env.example` — replace `myapp` prefix
   - `src/compose.yaml` — `name` field
3. **Initialize** the dev environment: `make init`
4. **Start** coding!

## License

_To be defined._
