# DecisionTrace Backend

FastAPI backend with multi-agent AI reasoning system for decision analysis.

## Features

- **4 AI Agents**: Decision structuring, bias detection, outcome simulation, reflection
- **REST API**: FastAPI with automatic OpenAPI documentation
- **PostgreSQL**: Persistent storage with SQLAlchemy ORM
- **Validation**: Pydantic schemas for all inputs/outputs
- **Migrations**: Alembic for database version control

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- OpenRouter API key

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/decisiontrace
OPENROUTER_API_KEY=your_key_here
```

3. **Run migrations:**
```bash
alembic upgrade head
```

4. **Start server:**
```bash
python -m uvicorn app.main:app --reload
```

Server runs at http://localhost:8000

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── agents/           # AI agent implementations
│   │   ├── base.py       # Base agent class
│   │   ├── decision_structuring.py
│   │   ├── bias_detection.py
│   │   ├── outcome_simulation.py
│   │   ├── reflection.py
│   │   └── orchestrator.py
│   ├── api/
│   │   └── routes/       # API endpoints
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── middleware/       # Request/response middleware
│   ├── config.py         # Configuration
│   ├── database.py       # Database connection
│   └── main.py           # FastAPI app
├── alembic/              # Database migrations
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
└── alembic.ini          # Alembic configuration
```

## Testing

Run tests:
```bash
pytest tests/
```

Run specific test:
```bash
pytest tests/test_backend_fixes.py
```

## API Endpoints

### Decisions
- `POST /api/decisions` - Create new decision
- `GET /api/decisions` - List all decisions
- `GET /api/decisions/{id}` - Get decision by ID
- `POST /api/decisions/{id}/reflect` - Add reflection

### Health
- `GET /health` - Health check

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key | Yes |
| `LOG_LEVEL` | Logging level (default: INFO) | No |

## Development

### Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

### Code Style

The project follows PEP 8 style guidelines.

## Deployment

See main project documentation in `.kiro/docs/DEPLOYMENT_GUIDE.md`

## License

MIT License
