# Agendalo

A calendar API for managing working hours and schedules with intelligent optimization using constraint programming.

## Overview

Agendalo is a FastAPI-based scheduling system that helps organizations optimize staff assignments by matching people's availability with business service hour requirements. The system uses Google OR-Tools for constraint programming to generate optimal schedules based on different optimization strategies.

## Features

- **People Management**: Create and manage staff members
- **Role Management**: Define roles and their requirements
- **Availability Hours**: Track when people are available to work (recurring or specific dates)
- **Business Service Hours**: Define when services need to be covered (recurring or specific dates)
- **Intelligent Scheduling**: Generate optimized agendas using constraint programming
- **Multiple Optimization Strategies**:
  - `maximize_coverage`: Maximize the number of time slots covered
  - `minimize_gaps`: Minimize gaps between assignments for each person
  - `balance_workload`: Balance the total hours worked across all people
- **Coverage Tracking**: Monitor which time slots are covered and which need attention

## Tech Stack

- **Python 3.10+**
- **FastAPI**: Modern web framework for building APIs
- **SQLite**: Lightweight database for data persistence
- **OR-Tools**: Google's optimization library for constraint programming
- **Uvicorn**: ASGI server for running the application
- **Pytest**: Testing framework

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip or uv (package manager)

### Installation

1. **Clone the repository** (if applicable):
```bash
git clone <repository-url>
cd agendalo
```

2. **Install dependencies**:

Using pip:
```bash
pip install -e .
```

Using uv (recommended):
```bash
uv pip install -e .
```

The project uses `pyproject.toml` for dependency management. All required packages will be installed automatically:
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- ortools>=9.8.0
- pytest==7.4.3
- pytest-asyncio==0.21.1
- httpx==0.25.2
- email-validator>=2.0.0

### Running the Application

**Important**: The backend must be run from the project root directory (`/home/diego/agendalo`), not from inside `modules/main_backend`.

Start the development server:

Using uvicorn directly:
```bash
cd /home/diego/agendalo
uvicorn modules.main_backend.main:app --reload
```

Using uv (recommended):
```bash
cd /home/diego/agendalo
uv run uvicorn modules.main_backend.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000 (or http://localhost:8001 if port 8000 is in use)
- **Interactive API Documentation**: http://localhost:8000/docs (or http://localhost:8001/docs)
- **Alternative API Documentation**: http://localhost:8000/redoc (or http://localhost:8001/redoc)

### Database

The application uses SQLite and automatically creates the database file (`agendalo.db`) on first run. The database schema is initialized automatically when the application starts.

## API Endpoints

### People
- `POST /api/people` - Create a new person
- `GET /api/people` - Get all people

### Roles
- `POST /api/roles` - Create a new role
- `GET /api/roles` - Get all roles
- `GET /api/roles/{role_id}` - Get a specific role

### Availability Hours
- `POST /api/availability-hours` - Create availability hours for a person
- `GET /api/availability-hours` - Get availability hours (filtered by person_id and/or role_id)

### Business Service Hours
- `POST /api/business-service-hours` - Create business service hours for a role
- `GET /api/business-service-hours` - Get business service hours (filtered by role_id)

### Agendas
- `POST /api/agendas/generate` - Generate a new agenda with optimization
- `GET /api/agendas` - Get agendas (filtered by role_id and optional status)
- `GET /api/agendas/{agenda_id}` - Get a specific agenda with entries and coverage

### Calendar
- `GET /api/calendar` - Get calendar view with availability and business service hours

## Usage Example

1. **Create a role**:
```bash
curl -X POST "http://localhost:8000/api/roles" \
  -H "Content-Type: application/json" \
  -d '{"name": "Nurse", "description": "Registered Nurse"}'
```

2. **Create a person**:
```bash
curl -X POST "http://localhost:8000/api/people" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

3. **Add availability hours** (recurring Monday-Friday, 9 AM - 5 PM):
```bash
curl -X POST "http://localhost:8000/api/availability-hours" \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": "<person_id>",
    "role_id": "<role_id>",
    "day_of_week": 0,
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "is_recurring": true
  }'
```

4. **Add business service hours** (recurring Monday-Friday, 8 AM - 6 PM):
```bash
curl -X POST "http://localhost:8000/api/business-service-hours" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": "<role_id>",
    "day_of_week": 0,
    "start_time": "08:00:00",
    "end_time": "18:00:00",
    "is_recurring": true
  }'
```

5. **Generate an optimized agenda**:
```bash
curl -X POST "http://localhost:8000/api/agendas/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": "<role_id>",
    "weeks": [1, 2],
    "year": 2024,
    "optimization_strategy": "balance_workload"
  }'
```

## Optimization Strategies

### maximize_coverage
Maximizes the number of time slots that are covered by assignments. This strategy ensures the highest possible coverage of business service hours.

### minimize_gaps
Minimizes the gaps between consecutive assignments for each person. This helps create more compact schedules with fewer idle periods.

### balance_workload
Balances the total hours worked across all people. This ensures a fair distribution of work hours among staff members.

## Testing

Run the test suite:

```bash
uv run pytest
```

Run tests with verbose output:

```bash
uv run pytest -v
```

The test suite includes integration tests for all API endpoints and uses an in-memory SQLite database for isolation.

## Project Structure

```
agendalo/
├── app/
│   ├── api/
│   │   └── routes/          # API route handlers
│   ├── database/            # Database connection and initialization
│   ├── domain/              # Domain models and schemas
│   ├── repositories/        # Data access layer
│   ├── schedulers/          # Scheduling optimization logic
│   ├── services/            # Business logic
│   ├── config.py            # Application configuration
│   └── main.py              # FastAPI application entry point
├── tests/
│   └── integration/         # Integration tests
├── pyproject.toml           # Project dependencies and configuration
└── README.md                # This file
```

## License

[Add your license here]

