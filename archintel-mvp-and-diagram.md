# ArchIntel Docs MVP (Milestone 1)

## MVP Requirements

**Goal:** Given a single repo, parse the codebase and generate module-level documentation pages.

### Backend (FastAPI)
- Set up FastAPI project with endpoints:
  - `POST /projects` – Register a project and repo path/URL
  - `POST /projects/{id}/ingest/code` – Run static analysis
  - `GET /projects/{id}/structure` – Fetch files, modules, functions
  - `GET /projects/{id}/docs` – Fetch generated docs
- Implement static analysis script (e.g., Python AST):
  - Walk repo, parse files, extract symbols
  - Store structure in Supabase (files, symbols, relationships)
- Doc generator utility:
  - Build prompts from AST info
  - Call Groq LLM to generate summaries and persist them

### Frontend (Next.js)
- Projects page: list projects, form to register new repo
- Docs explorer page:
  - Sidebar: file/module tree
  - Main area: doc content (headings, code snippets)
- Integrate with FastAPI endpoints
- Add loading/error states and basic styling

### Database (Supabase/Postgres)
- Store projects, files, symbols, docs

### LLM Integration
- Use Groq as the LLM provider for doc generation

---

## System Flow Diagram (MVP)

```mermaid
flowchart TD
    User((User))
    FE[Frontend (Next.js)]
    BE[Backend (FastAPI)]
    DB[(Supabase/Postgres)]
    LLM[Groq LLM Provider]

    User -- UI Actions --> FE
    FE -- API Calls --> BE
    BE -- Store/Retrieve --> DB
    BE -- Generate Docs --> LLM
    BE -- Serve Docs/Structure --> FE
    FE -- Display Docs --> User
```

---

**Flow:**
1. User registers project via frontend
2. Frontend calls backend to ingest code
3. Backend parses code, stores structure in DB
4. Backend generates docs using Groq LLM, stores in DB
5. Frontend fetches docs/structure and displays to user
