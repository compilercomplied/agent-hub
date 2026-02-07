# Agent Hub API

A FastAPI-based REST API for agent orchestration and prompt processing.

## Features

- POST endpoint at `/api/v1/prompt` for prompt processing
- Health check endpoint at `/health`
- Comprehensive end-to-end testing
- Strict type checking with `basedpyright`
- Docker containerization with multi-stage builds and type safety enforcement
- Strict code quality enforcement with Ruff
- Automated CI/CD with GitHub Actions

## Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- uv (recommended for dependency management)

### Local Development

1. Install dependencies:
```bash
uv sync --all-extras --dev
```

2. Run the application with type checking:
```bash
mise run start
```

3. Access the API:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Testing

### Run E2E Tests with Docker

```bash
./scripts/run-e2e.sh
```

Or manually:
```bash
docker compose -f docker-compose.e2e.yaml up --abort-on-container-exit
```

### Run Tests Locally

```bash
# Start the API
export AGENT_HUB_ANTHROPIC_API_KEY=your_api_key_here
uvicorn src.main:app &

# Run tests
export API_BASE_URL=http://localhost:8000
pytest e2e/ -v
```

## Code Quality

### Type Checking

The project uses `basedpyright` for strict type checking. The application will not build or run if there are type errors.

```bash
# Run strict type check
mise run check:types
```

### Linting and Formatting

```bash
# Check code
ruff check .

# Format code
ruff format .

# Auto-fix issues
ruff check --fix .
```

## API Endpoints

### POST /api/v1/prompt

Process a prompt and receive a response.

**Request:**
```json
{
  "prompt": "Your prompt text here"
}
```

**Response:**
```json
{
  "message": "hello world"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Project Structure

```
.
├── .github/workflows/    # CI/CD workflows
├── e2e/                  # End-to-end tests
│   ├── client.py        # HTTP client configuration
│   └── test_prompt_api.py
├── scripts/             # Utility scripts
│   └── run-e2e.sh      # E2E test runner
├── src/                 # Application source code
│   ├── __init__.py
│   └── main.py         # FastAPI application
├── Dockerfile           # Multi-stage Docker build with type-checking
├── docker-compose.e2e.yaml
├── pyproject.toml       # Project configuration
├── pyrightconfig.json   # Strict type-checking configuration
├── ruff.toml           # Ruff configuration
├── mise.toml           # Task runner configuration
└── README.md
```

## Docker

### Build and Run

The Docker build includes a mandatory strict type check step. If there are any type errors, the build will fail.

```bash
# Build the image (includes type check)
docker build -t agent-hub-api .

# Run the container
docker run -p 8000:8000 agent-hub-api
```

### Multi-Stage Builds

The Dockerfile includes multiple stages:
- `base`: Base Python environment
- `builder`: Dependency installation
- `runtime`: Production runtime
- `test`: Test execution environment

## CI/CD

GitHub Actions workflow runs automatically on pull requests:
- Builds Docker images
- Runs e2e tests
- Performs code quality checks with Ruff

## License

MIT
