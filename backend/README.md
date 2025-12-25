# ArchIntel Docs Backend

This folder contains the FastAPI backend for the ArchIntel Docs MVP.

## Setup

1. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```sh
   pip install -r 
   ```
3. Copy `.env.example` to `.env` and fill in your Supabase and Groq credentials.
4. Run the FastAPI server:
   ```sh
   uvicorn main:app --reload
   ```

## Project Structure

- `main.py` – FastAPI app entrypoint, includes modular routers
- `routers/` – Modular API endpoints for projects and docs
- `.env.example` – Environment variable template
- `requirements.txt` – Python dependencies

## Endpoints (MVP)

- `POST /projects` – Register a project
- `POST /projects/{id}/ingest/code` – Ingest code for a project
- `GET /projects/{id}/structure` – Get code structure
- `requirements.txtGET /docs/{project_id}` – Get generated docs

## Troubleshooting

- Ensure all environment variables in `.env` are set correctly (see `.env.example`).
- Supabase credentials must be valid and the database schema must match the expected tables.
- The Groq API key must be set for doc generation.
- Use `uvicorn main:app --reload` to run the backend in development mode.
- Check logs for errors during code ingestion or doc generation.
- For integration tests, ensure the backend is running and accessible at the correct API base URL.

## Further Improvements

- Add authentication and authorization for endpoints.
- Improve error handling and user feedback.
- Add more unit and integration tests.
- Expand static analysis to support more languages.
- Enhance frontend UI/UX and accessibility.

---

Follow best practices for modularization, environment management, and documentation.

For deployment, see the main `README.md` for monorepo-level instructions and best practices.