**ArchIntel Docs** project.

***

# ArchIntel Docs

ArchIntel Docs is an AI-powered documentation system that understands your codebase, its history, and the discussions around it.  
It uses static analysis, Git mining, and NLP to generate evolving, architecture-aware documentation for complex software projects.

***

## 1. What Is ArchIntel Docs?

ArchIntel Docs ingests your repository, analyzes the code structure, reads Git history, and optionally pulls in team communication (PRs, issues, chats) to build a unified understanding of how your system works and why it evolved that way.  
On top of this understanding, it generates human-friendly documentation and answers natural language questions about the codebase.

You can think of it as:  
**“Architecture Intelligence + AI documentation generator for your codebase.”**

Key capabilities:

- Map the structure of the codebase (modules, files, classes, functions).  
- Track how code changes over time and summarize important changes.  
- Capture the rationale behind changes from PRs/issues.  
- Generate and update documentation automatically as the code evolves.  
- Provide a UI to browse docs and a chat-like interface to ask questions.

***

## 2. Core Features

### 2.1 Static Code Understanding

- Parses the repository to build a structural model (files, symbols, relationships).  
- Extracts key entities such as modules, classes, functions, and their dependencies.  
- Stores this structure in a database so it can be queried and used for documentation.

### 2.2 Git History & Evolution

- Mines the Git history to understand how files and modules have changed over time.  
- Links commits to specific files and symbols to show a change timeline.  
- Generates change summaries that describe what changed and why it matters.

### 2.3 Team Communication & Rationale

- Ingests PR descriptions, issue threads, and optionally chat exports.  
- Associates discussions with the code they affect (files, modules, commits).  
- Produces “Design Rationale” and “Known Trade-offs” sections for documentation.

### 2.4 Documentation Generation

- Generates per-file and per-module documentation using LLMs, guided by templates.  
- Produces structured sections like overview, public API, dependencies, history, and rationale.  
- Can regenerate docs automatically when the code or history changes.

### 2.5 Question Answering

- Exposes an endpoint and UI where users can ask natural language questions about the system.  
- Uses the indexed code, history, and discussions to answer questions like:
  - “Where is authentication implemented?”  
  - “What changed in the payment flow last month?”  
  - “Why was service X introduced?”

### 2.6 Workflow Integration

- Hooks into CI to refresh analysis and documentation on pushes/PRs.  
- Designed to integrate with Git hosting (GitHub, etc.) and potentially IDEs or chat tools.  
- Supports multiple projects and multiple users through authentication.

***

## 3. Tech Stack

**Frontend**

- Framework: Next.js (React).  
- Responsibilities:
  - Projects dashboard (list projects, create new ones).  
  - Documentation explorer (file tree + doc view).  
  - History and rationale tabs.  
  - Q&A/chat interface over the codebase.

**Backend**

- Framework: FastAPI (Python).  
- Responsibilities:
  - Code ingestion and static analysis.  
  - Git mining (commits, diffs, file-level history).  
  - Team communication ingestion (PRs, issues, chats).  
  - Documentation generation and retrieval endpoints.  
  - Question answering API.

**Database**

- Platform: Supabase (Postgres).  
- Responsibilities:
  - Store projects, repositories, files, symbols, docs, commits, and discussions.  
  - Manage user accounts and authentication.  
  - Optionally store embeddings or references to a vector store.

**AI / NLP**

- Uses LLMs via an external provider (e.g., Groq/OpenAI) to:
  - Summarize code and diffs.  
  - Generate documentation sections.  
  - Answer natural language questions about the codebase.

***

## 4. High-Level Architecture

The system is composed of several cooperating services:

1. **Ingestion Service**
   - Registers projects and repositories.  
   - Runs static analysis and Git mining jobs.  
   - Writes structured data into Supabase.

2. **Analysis Service**
   - Extracts AST-level structure from source files.  
   - Computes relationships between symbols and modules.  
   - Aggregates commit and discussion data for each entity.

3. **Documentation Service**
   - Builds prompts from structure + history + discussions.  
   - Calls an LLM to generate and update docs.  
   - Stores documents by type (file/module/history/rationale).

4. **QA Service**
   - Accepts questions scoped to a project.  
   - Retrieves relevant code, history, and discussion context.  
   - Uses an LLM to generate answers.

5. **Frontend Web App**
   - Consumes backend APIs.  
   - Provides views for:
     - Project list and status.  
     - Documentation explorer (with tabs for overview, history, rationale).  
     - Q&A and search.

***

## 5. Milestones (Outcome-Based)

Instead of deadlines, ArchIntel Docs is broken down into four clear milestones.  
Each milestone is “done” when its outcome is achieved end-to-end.

### Milestone 1 – Local Code Intel MVP

Outcome:

- Load a local repo.  
- Parse code structure and store it in the database.  
- Generate basic per-file and per-module documentation.  
- View docs in the Next.js UI (sidebar + main content).

Focus:

- Static analysis basics and AST parsing.  
- Initial FastAPI endpoints for projects, structure, and docs.  
- Basic docs explorer UI.

### Milestone 2 – History-Aware Documentation

Outcome:

- Mine Git history for a project.  
- Show the evolution of files and modules over time.  
- Generate summaries of important changes.  
- Display a “History” tab alongside the docs.

Focus:

- Commit and diff processing.  
- Linking commits to files and symbols.  
- History timeline and summary generation.

### Milestone 3 – Context & Rationale

Outcome:

- Ingest PRs, issues, and/or chat logs.  
- Associate discussions with the code they affect.  
- Generate “Design Rationale” and “Known Trade-offs” for modules and features.  
- Display a “Rationale” tab in the docs UI.

Focus:

- Ingestion and mapping of communication data.  
- Rationale summarization using LLMs.  
- UI for rationale display and links to original PRs/issues.

### Milestone 4 – Productization & Integration

Outcome:

- Authenticated, multi-project app.  
- CI integration to automatically run ingestion and doc updates.  
- Solid UX that dev teams can use in their daily workflow.

Focus:

- Supabase auth and project scoping.  
- CI pipeline and optional repository webhooks.  
- UX polish, error handling, and project settings.

***

## 6. Data Model Overview

At a high level, the data model includes:

- `users` – accounts for people using ArchIntel Docs.  
- `projects` – logical groupings of repositories and configuration.  
- `repositories` – code repositories linked to a project.  
- `files` – individual files in a repository, with language and path.  
- `symbols` – functions, classes, or other code entities plus relationships.  
- `docs` – generated documentation pieces (overview/history/rationale/etc.).  
- `commits` – Git commits, linked to files and projects.  
- `file_commits` – join between commits and files.  
- `discussions` – PRs, issues, or chat threads.  
- `discussion_links` – mapping from discussions to commits/files/symbols.

This structure is designed to support:

- Efficient retrieval of documentation per file/module.  
- History views per file or module.  
- Rationale aggregated from multiple sources.

***

## 7. Frontend Overview

The frontend is built with Next.js (App Router) and centers on a few key views:

- **Landing / Marketing (optional)** – short explanation of the product.  
- **Projects Dashboard** – list projects, show ingestion status, and allow creation of new projects.  
- **Project Overview** – high-level info, recent activity, quick access to docs.  
- **Docs Explorer** – tree of files/modules with:
  - Overview tab.  
  - History tab.  
  - Rationale tab.  
- **Q&A Page** – ask free-form questions and view answers, with links to relevant docs.

The design aims to be clean and human, with strong typography and layout rather than generic AI-style visuals.

***

## 8. Backend Overview

The backend exposes a set of FastAPI endpoints around:

- Project management:
  - Create/list projects.  
  - Attach repositories and configuration.

- Ingestion:
  - Trigger static analysis for a project.  
  - Trigger Git history mining.  
  - Trigger team communication ingestion.

- Documentation:
  - Generate or regenerate documentation sections.  
  - Retrieve documentation for a project, module, or file.

- Question answering:
  - Accept queries and return answers along with any relevant links or entities.

Async tasks or background workers are used for long-running ingestion jobs.

***

## 9. How to Use This Project

High-level intended usage:

1. **Install and configure** the backend (FastAPI) and frontend (Next.js), and connect them to your Supabase instance.  
2. **Create a project** in the UI and link it to a repo (local path or remote).  
3. **Run ingestion** to analyze code structure and Git history.  
4. **Browse documentation** in the docs explorer and inspect the generated content.  
5. **Connect communication sources** (PRs/issues) to unlock rationale and trade-offs.  
6. **Integrate with CI** so docs stay up to date with each push/PR.  
7. **Use the Q&A interface** to quickly understand parts of the system.

***

## 10. Project Status and Future Work

ArchIntel Docs is designed to grow over time, with several clear directions:

- Support more programming languages by adding additional parsing backends.  
- Improve static analysis depth (control/data flow, potential bug detection).  
- Auto-generate architecture diagrams from dependency graphs.  
- Provide official IDE extensions (VS Code, etc.) and chat integrations (Slack/Discord).  
- Add quality metrics such as documentation coverage and risky-module detection.

***

## 11. License & Contributions

You can adapt this section depending on your goals:

- **License:** Choose an appropriate license (e.g., MIT, Apache-2.0, or a custom license).  
- **Contributions:**  
  - Open an issue before large changes.  
  - Use descriptive branch names and commit messages.  
  - Keep architectural decisions and UX discussions documented.

***

This README is intentionally high-level and product-focused, so you can pair it with `archintel-docs-guide.md` for detailed implementation steps, API design, and learning links.