---
description: How to use the ArchIntel MVP features
---
# ArchIntel MVP Quick Start

Welcome to the ArchIntel Minimum Viable Product. Below are the steps to utilize the key structural intelligence features.

## 1. Project Registration & Sync
- Go to the **Registry** (`/projects`).
- Click **New Repository** to add a GitHub URL.
- Use the **Sync** (Refresh) icon on any project card to re-trigger architectural analysis if the codebase changes.

## 2. Architectural Explorer
- Click **Explorer** on any project node.
- Browse the **File Registry** on the left.
- Use the **System Architecture** tab for high-level synthesis.
- Toggle **Structural Graph** to see a dependency map of your modules.

## 3. Architecture Search (Intelligence Node)
- Press `Cmd+K` (or `Ctrl+K`) anywhere in the Explorer.
- Ask questions like:
  - "Where is the main entry point?"
  - "List all external API integrations."
  - "Trace the data flow for user authentication."
- The **Oracle Node** will synthesize an answer based on AST structural analysis.

## 4. CLI Access
- Click **CLI Access** on the Registry page.
- Follow the instructions to use `python backend/cli.py`.
- Commands: `list`, `analyze <url>`, `query <id> <text>`.

## 5. Exporting Reports
- In the **System Architecture** tab, use the **Export Report** button to download a full markdown documentation of the system's structural design.
