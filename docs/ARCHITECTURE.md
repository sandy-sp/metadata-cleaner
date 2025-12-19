# DOC: Dual Orchestrator Orchestrator ("Twin-Turbo" Edition)
### The Local-First, Agentic Pair-Programming Environment

**Version:** 2.1.0 ("Mnemosyne" Release)
**Status:** Architecture Blueprint
**Core Stack:** Python (FastAPI), React (Next.js), Local Git, ChromaDB
**AI Engines:** Anthropic Claude Code & OpenAI Codex (CLI)

---

## 1. Executive Summary

**DOC (Dual Orchestrator Orchestrator)** is a locally hosted "Agentic IDE" that transforms your terminal into a self-learning software development agency.

Instead of relying on a single chat interface, DOC orchestrates two expert AI agents—**Claude Code** and **OpenAI Codex**—to work as **Peer Engineers**. They operate in parallel, utilizing a "Twin-Turbo" workflow where they plan, code, and review each other's work simultaneously.

Distinct from standard coding assistants, DOC possesses **Persistent Memory**. It utilizes a "Brain" directory (`.brain/`) in your project to maintain architectural patterns, debugging history, and user preferences, ensuring that mistakes are never repeated.

---

## 2. Core Philosophy: "Extreme Programming" with AI

DOC moves beyond the "Human-Manager / AI-Worker" paradigm. It implements an **AI Pair Programming** model:

1.  **Twin-Terminal Execution:** Claude and Codex run in separate, parallel subprocesses.
2.  **Shared-State Concurrency:** Agents work on isolated local Git branches (`feature/claude` and `feature/codex`) to prevent file overwrite conflicts.
3.  **The "Huddle" Protocol:** Agents communicate via a live `HUDDLE.md` file to coordinate architecture before writing code.
4.  **Cross-Review:** Code written by Codex is reviewed by Claude, and vice-versa, before merging into `main`.

---

## 3. System Architecture

The system follows a **Three-Tier Architecture**, fully hosted on your local machine.

### Tier 1: The Interface (Web App)
* **Technology:** Next.js (React) + Tailwind CSS + xterm.js.
* **Role:** The "Mission Control."
* **Key Features:**
    * **Twin-Terminal View:** Watch both agents coding in real-time side-by-side.
    * **Chat Console:** Send natural language commands ("Refactor the Auth module").
    * **Conflict Arena:** A UI for resolving merge conflicts when agents disagree.
    * **Visual Knowledge Graph:** A node view of your project structure (Repo Map).

### Tier 2: The Orchestrator (Backend "Scrum Master")
* **Technology:** Python 3.11+ (FastAPI).
* **Role:** Managing the lifecycle of the agents.
* **Responsibilities:**
    * **Subprocess Management:** Wraps `claude` and `codex` CLIs, capturing `stdout/stderr` streams.
    * **Git Operations:** Handles branching, committing, and merging strategies.
    * **Intervention Protocol:** Pauses execution if an agent requests risky permissions (e.g., "Delete 10 files?").
    * **State Machine:** Tracks project state (`PLANNING`, `SPRINTING`, `MERGING`, `REVIEWING`).

### Tier 3: The Memory Core (The "Brain")
DOC implements a **3-Tier Memory Architecture** to solve context window limitations and amnesia.

| Tier | Type | Implementation | Role |
| :--- | :--- | :--- | :--- |
| **L1** | **Hot Memory** | **Context Window** | The active file content and immediate instruction. |
| **L2** | **Warm Memory** | **`.brain/context/*.md`** | "RAM" for the project. Keeps track of *current* goals and architecture. |
| **L3** | **Cold Memory** | **ChromaDB (Local)** | "Hard Drive." Stores vector embeddings of *all* past decisions, bugs, and user preferences. |

---

## 4. The "Brain" Directory Structure

Every DOC-managed project contains a hidden `.brain` folder acting as the Single Source of Truth.

```text
my-project/
├── .brain/
│   ├── SKILLS.md            # The "Skillbook" - Lessons learned from past errors.
│   ├── HUDDLE.md            # The Chat Room where Agents talk to each other.
│   ├── repo_map.txt         # Compressed AST map of the codebase (Classes/Funcs).
│   ├── memory.db/           # ChromaDB folder for vector search.
│   └── context/
│       ├── projectBrief.md  # High-level user goals.
│       ├── systemPatterns.md# Architecture rules (e.g., "Use Repository Pattern").
│       ├── activeContext.md # Current sprint status.
│       └── logs.json        # Execution history.
├── src/                     # Your actual source code.
└── .gitignore               # Configured to ignore .brain/logs but keep SKILLS.md.
````

-----

## 5\. The "Twin-Turbo" Workflow Loop

When you submit a task (e.g., "Build a React Todo App with FastAPI Backend"), DOC initiates the following loop:

### Phase 1: Ingestion & Planning (The Huddle)

1.  **Orchestrator** embeds the query and checks **L3 Memory (Chroma)** for similar past tasks.
2.  **Orchestrator** generates/updates the **Repo Map**.
3.  **Agents** are summoned to `HUDDLE.md`.
      * *Claude:* "I'll handle the FastAPI backend. Codex, can you take the React frontend?"
      * *Codex:* "Agreed. I will mock the API calls until you are ready."

### Phase 2: The Sprint (Parallel Execution)

The Orchestrator spins up two threads:

  * **Thread A (Claude):** Checks out `feature/backend`. Reads `SKILLS.md`. Starts coding `main.py`.
  * **Thread B (Codex):** Checks out `feature/frontend`. Reads `SKILLS.md`. Starts coding `App.jsx`.
  * *Constraint:* If an agent is stuck for \> 60s, the Orchestrator interrupts it.

### Phase 3: The Merge & Cross-Review

1.  **Orchestrator** attempts to merge `feature/frontend` and `feature/backend` into `dev`.
2.  **Cross-Review:**
      * Claude reads Codex's code diff.
      * Codex reads Claude's code diff.
3.  **Refinement:** If Claude spots a security flaw in Codex's code, it creates a "Fix Ticket" in `activeContext.md`, and Codex fixes it immediately.

### Phase 4: Learning (The Skillbook Update)

  * If a build error occurs (e.g., "Module Not Found"), the agent resolving it updates `SKILLS.md`:
    > *"Rule: When using Python 3.12+, always install `setuptools` explicitly."*
  * This ensures the error is never repeated in future sessions.

-----

## 6\. Installation & Setup

### Prerequisites

1.  **Node.js & Python 3.11+** installed.
2.  **Git** installed.
3.  **Paid Accounts:**
      * Anthropic Console (for `claude` CLI).
      * ChatGPT Plus (for `codex` CLI).

### Step 1: Install AI Engines

```bash
# Install the official CLIs
npm install -g @anthropic-ai/claude-code
npm install -g @openai/codex

# Authenticate (One-time setup)
claude login
codex login
```

### Step 2: Install DOC System

```bash
git clone [https://github.com/your-repo/dco-twin-turbo.git](https://github.com/your-repo/dco-twin-turbo.git)
cd dco-twin-turbo

# Setup Backend (Orchestrator)
cd backend
pip install -r requirements.txt

# Setup Frontend (Interface)
cd ../frontend
npm install
```

### Step 3: Launch

```bash
# From project root
make start
```

*Access the Web Dashboard at `http://localhost:3000`.*

-----

## 7\. User Guide

### Onboarding a New Project

1.  Open DOC Dashboard.
2.  Click **"Import Repository"** and select your local folder.
3.  DOC initializes `.brain/`, scans your code, and builds the **L3 Vector Index** (\~30s).

### The Chat Interface

  * **Standard Mode:** Chat with the Orchestrator to assign tasks.
  * **Huddle Mode:** Watch the agents converse in `HUDDLE.md`.
  * **Manual Override:** If the agents are arguing over a conflict, use the "Conflict Arena" to manually pick the winning code block.

### Setting "Rules of Engagement"

You can manually edit `.brain/context/systemPatterns.md` to enforce rules:

  * *"Always use Functional Components in React."*
  * *"Never expose API keys in frontend code."*
  * *"Use Snake Case for Python variables."*

-----

## 8\. Roadmap & Future Features

  * **v2.5 - Voice Interface:** Speak instructions directly to the Orchestrator.
  * **v3.0 - Swarm Mode:** Spin up multiple Codex instances to work on 5+ files simultaneously.
  * **MCP Integration:** Support for the *Model Context Protocol* to connect external tools (PostgreSQL, Linear, Slack).
