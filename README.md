# BIG – ReAct Agentic Scaffold

This is a minimal but extensible scaffold for a **ReAct Agentic AI application** using:

- [LangChain](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- Tools & sub‑agents
- Typed state
- Config + logging driven by `.env`

For now, the application performs **two sequential sub‑agent steps**:

1. Generate a *general analytical context* for:
   - `AXIS_OF_EXPLORATION`
   - `UNIT_OF_ANALYSIS`
2. Using that context, generate an *"ideal roles" prompt opening* as described in your specification.

The program then prints the step‑2 result and exits.

---

## 1. Create and activate a virtualenv

From the folder that *contains* this project (i.e. the parent of `big_react_agent/`):

```bash
python -m venv .venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

Upgrade pip (recommended):

```bash
python -m pip install --upgrade pip
```

---

## 2. Install dependencies

```bash
cd big_react_agent
pip install -r requirements.txt
```

---

## 3. Environment variables

Copy the example file and fill in your own API keys / settings:

```bash
cp .env.example .env
```

Then edit `.env` and set at least:

- `OPENAI_API_KEY`

You can also adjust:

- `AXIS_OF_EXPLORATION`
- `UNIT_OF_ANALYSIS`
- `IDEAL_ROLES`
- `LOG_LEVEL`
- etc.

> **Security note:** never commit your real keys to source control.

---

## 4. Run the application

From the project root:

```bash
python -m app.main
```

You should see logging output and finally something like:

```text
=== Final output ===

You will embody the following roles to analyse demographic changes:
1. ...
...
```

---

## 5. Project structure

```text
big_react_agent/
  README.md
  requirements.txt
  .env.example
  app/
    __init__.py
    main.py
    logging_config.py
    config/
      __init__.py
      settings.py
      loader.py
    agents/
      __init__.py
      base.py
      tools.py
    prompts/
      __init__.py
      coordinator.py
```

- `app/main.py` – entry point; wires settings, logging, LLM, agent and runs a single ReAct episode.
- `config/` – loading `.env` and mapping them into a `Settings` object.
- `logging_config.py` – small helper to configure Python logging from settings.
- `agents/` – ReAct agent scaffold and two sub‑agents implemented as tools.
- `prompts/` – coordinator prompt factory that injects `.env` values.

This is intentionally simple but structured enough to extend with:

- more tools / sub‑agents
- LangGraph flows
- external search tools
- persistent memory, DB, etc.



### BACKEND A
cd "C:\Users\MagnodaSilvaLeite(t2\Documents\Magno_Personal\AI\Portfolio\langgraph_ai_big_deep_agents_A/backend"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

### FRONTEND A
cd "C:\Users\MagnodaSilvaLeite(t2\Documents\Magno_Personal\AI\Portfolio\langgraph_ai_big_deep_agents_A/frontend"
.venv/Scripts/Activate
python manage.py runserver 8002
Quit the server with CTRL-BREAK.

### BACKEND B
cd "C:\Users\MagnodaSilvaLeite(t2\Documents\Magno_Personal\AI\Portfolio\langgraph_ai_big_deep_agents_B"
uvicorn app.api:app --reload


