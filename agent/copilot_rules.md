# GitHub Copilot Agent Rules for Python Projects

## General Coding Rules
- Write clear, concise, and well-documented code.
- Use type hints for all function signatures and class attributes.
- Follow PEP8 style guidelines for formatting and naming.
- Prefer async/await for I/O-bound operations.
- Use dataclasses for simple data containers.
- Add docstrings to all public classes, methods, and functions.
- Use f-strings for string formatting.
- Avoid global variables; use dependency injection or class attributes.
- Handle exceptions gracefully and log errors with context.
- Write modular, reusable functions and classes.

## Project Structure
- Place main application code in the `agent/` directory.
- Use `tests/` for unit and integration tests.
- Store configuration in YAML or `.env` files; never hardcode secrets.
- Use `requirements.txt` for dependencies.
- Document all scripts and modules in a `README.md`.

## Async and Streaming
- Use `asyncio` for concurrency and streaming.
- Prefer `async def` for all I/O and network-bound functions.
- Use `async with` for resource management (e.g., files, HTTP clients).
- Stream responses using `asyncio.Queue` for real-time updates.

## API and Models
- Use Pydantic models for API request/response validation.
- Validate all incoming data and handle invalid input with clear errors.
- Use FastAPI for HTTP APIs; prefer OpenAPI-compatible endpoints.
- Return errors in a consistent, structured format.

## Logging and Observability
- Use the `logging` module for all logs; avoid print statements in production.
- Add structured logs for key events, errors, and agent actions.
- Include trace IDs or session IDs in logs for debugging.

## Security
- Never log sensitive data (API keys, passwords, PII).
- Use environment variables for secrets and credentials.
- Validate and sanitize all user input.

## Testing
- Write unit tests for all core logic and utilities.
- Use async test frameworks (e.g., pytest-asyncio) for async code.
- Mock external dependencies in tests.

## Copilot-Specific Guidance
- When generating code, always:
  - Use proper markdown code blocks with language specified.
  - Add comments to explain non-trivial logic.
  - Prefer idiomatic, modern Python (3.8+).
  - Suggest improvements or refactoring if code is unclear or repetitive.
- For streaming/chat agents, show how to stream intermediate results or chain-of-thought traces.
- For FastAPI/FastMCP, show how to define and document endpoints/tools.

---

*These rules help ensure high-quality, maintainable, and secure Python code for agent-based projects using GitHub Copilot.*
