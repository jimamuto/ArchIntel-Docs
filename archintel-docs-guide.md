# ArchIntel Docs – Project Guide

> AI-native documentation for complex codebases, powered by static analysis, Git history, and team communication.

---

## 1. Vision & Outcomes

ArchIntel Docs is an AI-powered documentation generator that understands code structure, Git history, and team communication to produce accurate, evolving documentation for complex software systems.[web:34][web:39]

### 1.1 Product Vision

- Ingest code, commits, and team comms (PRs, issues, messages) into a unified knowledge graph of the system.[web:34][web:39]  
- Use static analysis + NLP to answer “how/why” questions about architecture and generate docs on demand.[web:23][web:27][web:34]  
- Integrate into dev workflows (CI, Git hooks, IDE, chat) so documentation updates are automatic, not manual.[web:26][web:39]

### 1.2 Outcome-Based Milestones

Instead of time-based deadlines, the project is split into four outcome-based milestones:

1. **Local Code Intel MVP** – Generate docs from a single repo’s code structure.  
2. **History-Aware Docs** – Use Git history to explain evolution and changes.  
3. **Context-Aware Docs** – Enrich docs with PR/issue discussion and rationale.  
4. **Workflow Integration** – CI integration, auth, multi-repo support, polished UX.

**Recommended video – Big picture**

- Static analysis & code intelligence overview:  
  https://www.youtube.com/watch?v=TP5Eo4n-L5w [web:42]

---

## 2. High-Level Architecture

This section defines the core components: frontend (Next.js), backend (FastAPI), and database (Supabase).[web:30][web:35][web:40]

### 2.1 System Components

- **Frontend (Next.js + React)**  
  - Docs explorer: sidebar (files/modules), main panel (docs, history, rationale).[web:31][web:41]  
  - “Ask a question” chat UI over code + history.  
  - Project selection & settings.

- **Backend (FastAPI)**  
  - Ingestion: code parser, Git miner, comms ingester.  
  - Analysis: static analysis, embeddings, summarization.  
  - Doc generation & QA endpoints.[web:30][web:35]

- **Database (Supabase/Postgres)**  
  - Entities: projects, repositories, files, functions, commits, docs, messages.  
  - Supabase Auth for multi-user support.[web:40]

- **LLM + Integrations**  
  - LLM provider (Groq) for generation.  
  - Git (via `git` CLI or library) for history.[web:28][web:38]

**Recommended videos**

- FastAPI example application & patterns:  
  https://www.youtube.com/watch?v=0sOvCWFmrtA [web:30][web:35]  
- Supabase intro & auth:  
  https://www.youtube.com/watch?v=8qgUtfJ_9pQ [web:40]  
- Next.js documentation site with Nextra:  
  https://www.youtube.com/watch?v=mVDMvYQL7-A [web:41]

---

## 3. Milestone 1 – Local Code Intel MVP

**Outcome:** Given a single repo, ArchIntel Docs can parse the codebase and generate basic module-level documentation pages.[web:23][web:27][web:34]

### 3.1 Scope

- Parse repo source files.  
- Build an internal structural map (AST → modules, classes, functions).  
- Generate basic docs per file and module using templates + Groq LLM.  
- Display docs in a Next.js UI (sidebar nav + main content).[web:31][web:41]

### 3.2 Backend Tasks (You – FastAPI)

- Set up FastAPI project with routers for:
  - `POST /projects` – register a project and repo path/URL.  
  - `POST /projects/{id}/ingest/code` – run static analysis.  
  - `GET /projects/{id}/structure` – fetch files, modules, functions.  
  - `GET /projects/{id}/docs` – fetch generated docs.[web:30][web:35]
- Implement static analysis script for your primary language (e.g., Python):
  - Walk repo (ignore `venv`, `node_modules`, etc.).  
  - Use `ast` to parse files and extract symbols.[web:23][web:27]  
  - Store structure in Supabase tables (files, symbols, relationships).[web:40]
- Implement doc generator utility:
  - Build prompts from AST info (name, docstring, imports, relations).  
  - Call Groq LLM to generate summaries and persist them.

### 3.3 Frontend Tasks (Next.js / React)

- Set up Next.js app with:
  - Projects page: list projects, form to register a new repo.  
  - Docs explorer page:
    - Left sidebar: file/module tree.  
    - Main area: doc content with headings and code snippets.[web:31][web:41]
- Integrate with FastAPI:
  - Fetch structure and docs via API.  
  - Add loading/error states and basic styling.

**Recommended videos**

- Static analysis basics with AST:  
  https://www.youtube.com/watch?v=MMx0G5vVL0Q [web:23]  
- FastAPI project structure & routers:  
  https://www.youtube.com/watch?v=0sOvCWFmrtA&t=3600s [web:30][web:35]  
- Next.js 14 App Router intro:  
  https://www.youtube.com/watch?v=ZVnjOPwW4ZA [web:41]

---

## 4. Milestone 2 – Git History & Change-Aware Docs

**Outcome:** Documentation becomes time-aware and shows key changes and evolution per file/module.[web:28][web:38][web:34]

### 4.1 Git Mining Service

Backend tasks:

- Implement Git mining:
  - For a project’s repo, iterate commits and capture:
    - Commit hash, author, date, message.  
    - Files changed in each commit.[web:28][web:38]
  - For selected commits, compute diffs and map changed lines to functions/files.
- Persist:
  - `commits` table.  
  - `file_commits` or similar join table.  
  - Optional: commit-level “tags” (e.g., refactor, bugfix).

API endpoints:

- `POST /projects/{id}/ingest/history` – mine or refresh Git history.  
- `GET /projects/{id}/history/{file_id}` – list commits & summaries for a file.[web:38]

### 4.2 Change Summaries & UI

NLP tasks:

- Generate commit-level summaries from:
  - Commit message + diff snippet.[web:34][web:39]
- Generate file/module “evolution summaries” (how it changed over time).

Frontend tasks:

- Add “History” tab in the docs view:
  - Timeline of commits affecting the file/module.  
  - Short summary, author, date.  
  - Expand to see more detail.

**Recommended videos**

- Mining software repositories (intro):  
  https://www.youtube.com/watch?v=2X5sPjBG2Xg [web:28]  
- Git internals & commit graph deep dive:  
  https://www.youtube.com/watch?v=qsTthZi23VE [web:28]  
- AI summarization of code changes (pattern):  
  https://www.youtube.com/watch?v=4P3iNsjGMiI [web:34]

---

## 5. Milestone 3 – Team Communication & Rationale

**Outcome:** Docs now explain *why* things were built, using PR/issue/meeting discussions.[web:34][web:39]

### 5.1 Ingesting Team Communication

Backend tasks:

- Add ingestion for:
  - PR titles and descriptions.  
  - Issue titles and descriptions.  
  - Optional: exported chat threads (Slack/Discord).[web:34]
- Map each PR/issue to:
  - Commits and files it affected.  
  - Related modules/functions (via file paths).

Schema:

- `discussions` table: type (PR/issue), title, body, URL.  
- `discussion_links` table: link discussions to commits/files.

### 5.2 Rationale Generation

NLP tasks:

- For each file/module:
  - Aggregate associated PR/issue text and commit summaries.  
  - Generate “Design Rationale” and “Known Trade-offs” sections.[web:34][web:39]

Frontend tasks:

- Add “Rationale” tab:
  - High-level rationale summary.  
  - Links out to original PRs/issues.

**Recommended videos**

- NLP for software engineering:  
  https://www.youtube.com/watch?v=6ZwK1hN7mKo [web:34]  
- Intro to modern NLP pipelines:  
  https://www.youtube.com/watch?v=fNxaJsNG3-s [web:34]  
- Code documentation generation case study:  
  https://www.youtube.com/watch?v=PGYJ4vU9h4s [web:29][web:34]

---

## 6. Milestone 4 – Workflow Integration & UX Quality

**Outcome:** ArchIntel Docs feels like a real tool: CI integration, auth, multi-repo support, clean UI.[web:26][web:32][web:35]

### 6.1 CI & GitHub Integration

Backend & DevOps tasks:

- Add GitHub App/webhook or simpler:
  - CI job on push/PR that calls:
    - `/projects/{id}/ingest/code`  
    - `/projects/{id}/ingest/history`  
    - “regenerate docs” endpoint.[web:26][web:38]
- Optionally:
  - Post PR comments with doc impact and summaries.

**CI video**

- GitHub Actions for Python projects:  
  https://www.youtube.com/watch?v=R8_veQiYBjI [web:26]  
- CI-based docs generation pattern:  
  https://www.youtube.com/watch?v=Nt62FNxfDNA [web:26]

### 6.2 Auth, Projects, and UX

Backend tasks:

- Configure Supabase Auth (email/OTP or OAuth).  
- Scope all tables per user/team/workspace.[web:40]
- Add endpoints for:
  - Listing user projects.  
  - Inviting collaborators (later).

Frontend tasks:

- Auth flows (login/register) using Supabase client.  
- Projects dashboard with:
  - List of projects.  
  - “Create project” wizard (repo path/URL + language).  
  - Status indicators (ingesting, ready, error).[web:41]
- UX polish:
  - Clear navigation structure (Projects → Docs → File → History/Rationale).  
  - Consistent typography and spacing; avoid “AI look” via restrained gradients and more thoughtful layout.

**UI/UX videos**

- UI/UX principles for devs:  
  https://www.youtube.com/watch?v=_Hp_dI0DzY4 [web:39]  
- Dashboard design in React:  
  https://www.youtube.com/watch?v=hQAHSlTtcmY [web:31]

---

## 7. NLP & Documentation Patterns

This section describes how to structure prompts and outputs so docs stay consistent.[web:34][web:39]

### 7.1 Core NLP Tasks

- **Code summarization** – function/module overviews.  
- **Doc generation** – module overview, public API, integration notes.  
- **QA over codebase** – answer questions like:
  - “Where is authentication implemented?”  
  - “What changed in the payment flow in the last month?”[web:34]

Implementation hints:

- Use structured context:
  - AST info (names, relationships).  
  - Git summaries (why/when).  
  - Discussion snippets (rationale).[web:34][web:39]

### 7.2 Content Templates

Keep templates consistent:

- **File Overview**  
  - What this file is responsible for.  
  - Key public functions/classes.  
  - Dependencies and collaborators.

- **Module Overview**  
  - Responsibilities, invariants, and entry points.  
  - Upstream/downstream modules.  
  - Known trade-offs and future work.

- **History Summary**  
  - Major refactors.  
  - Bug fixes.  
  - Performance/scale changes.

- **Design Rationale**  
  - Core decisions.  
  - Alternatives considered.  
  - Reasons and trade-offs.

**Videos**

- Building an AI code assistant with embeddings:  
  https://www.youtube.com/watch?v=T-D1OfcDW1M [web:34]  
- AI documentation tools walkthrough:  
  https://www.youtube.com/watch?v=Zk0U-2D2ZpU [web:39]

---

## 8. Data Model (Supabase / Postgres)

Suggested high-level tables (simplify as needed).[web:40]

- `users`  
- `projects`  
- `repositories` (per project, per VCS host)  
- `files` (path, language, hash)  
- `symbols` (functions/classes + relations)  
- `docs` (type: file/module/history/rationale, content, version)  
- `commits`  
- `file_commits`  
- `discussions` (PRs/issues)  
- `discussion_links` (discussion ↔ file/commit)

You can later add:

- `embeddings` table or external vector store.  
- `events` table for ingestion and errors.

**Video**

- Supabase schema & SQL basics:  
  https://www.youtube.com/watch?v=8qgUtfJ_9pQ [web:40]

---

## 9. Frontend Structure (Next.js)

Suggested structure for the app router.[web:31][web:41]

