# Orchestration Fundamentals for Agentic Development — Labs

Course materials and the practice codebase for the hands-on labs.

## Get started

```
git clone https://github.com/bensethbell/orchestration-fundamentals-labs.git
cd orchestration-fundamentals-labs/taskboard
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed_demo.py
```

See [taskboard/README.md](taskboard/README.md) for running the app and tests.

## What's here

- **Pre-Work - Tech Requirements.md** — complete before the session
- **Lab 1 - Decomposition.md**, **Lab 2 - Model Selection.md**, **Lab 3 - Orchestration.md** — lab handouts
- **Lab 4a - Orchestrator Agent.md**, **Lab 4b - Agent Teams.md** — optional extensions. Each runs on its own branch (`lab-4a-start`, `lab-4b-start`) with a fresh copy of the app; Labs 1–3 stay on `main`
- **Cheat Sheet.md** — quick reference
- **Orchestration Fundamentals - Slide Deck.pptx** — slides
- **taskboard/** — the Flask app you'll work on in the labs
