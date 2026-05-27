# Schitzo Neural Router

Neural router for LLM model selection and routing using Clean Architecture principles.

## Setup

1. Activate virtual environment:
   ```bash
   router/venv/Scripts/activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python main.py
   ```

## Architecture

- `domain/` - Business logic and entities
- `application/` - Use cases and services  
- `infrastructure/` - External interfaces and adapters

## Dependencies

- FastAPI 0.104.1 - Web framework
- Uvicorn 0.24.0 - ASGI server
- LiteLLM 1.17.9 - LLM routing
- Langfuse 2.21.0 - Observability
- Pydantic 2.5.0 - Data validation