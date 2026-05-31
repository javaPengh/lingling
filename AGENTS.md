# AGENTS.md

## Python Environment

The backend always uses the Conda `base` Python environment:

```powershell
D:\ai_study_app\anaconda3\python.exe
```

Use this environment for running the backend, installing backend dependencies, and executing backend scripts.

## Backend Placement Rule

Follow the FastAPI layering under `server/`:

- HTTP request/response only: `server/api/routes/`
- Business logic: `server/services/`
- SQLite access only: `server/dao/`
- Pydantic entities and DTOs: `server/models/`
- LLM adapters and prompts: `server/llm/`
- Global config and enums: `server/core/`

When adding files, place them by responsibility rather than convenience.

## Documentation Rule

- New files need a file-level docstring or comment explaining their responsibility.
- New public interfaces and functions need docstrings explaining what they do.
- New entity classes need class docstrings, and every entity field needs a field description.
- New enum classes need class docstrings, and every enum member needs a short comment.
