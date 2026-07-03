# Jamalek
<img width="1183" height="701" alt="image" src="https://github.com/user-attachments/assets/db7dabfb-5ce2-41e3-8cd7-521494295017" />


Jamalek ("your beauty" in Arabic) is a beauty assistant that keeps track of your skin. You show it a selfie or tell it what your skin is doing that day, and it takes you from skincare prep through to a finished makeup look, pulling from products you already own before it suggests buying anything new.

Built for the Google x Kaggle 5-Day AI Agents Intensive capstone, Concierge track. Framework is Google's ADK (Python), models are Gemini.

## Why I built it

Most beauty tools are stateless. You ask "what foundation suits me" and it answers from scratch every time. No idea about your undertone, no memory that something broke you out last month, no clue you already own three foundations. So it points you at whatever's trending and a checkout page.

The interesting part isn't matching a shade once. It's an assistant that builds up a picture of you over time and reasons about what's already in your bag.

## What it does

- Reads undertone and skin concerns (dryness, oiliness, breakouts) from a selfie using Gemini vision, and suggests a prep step first.
- Matches shades to your undertone and plans a look, checking what you already own before recommending anything new.
- Finds cheaper dupes when you actually need something new ("a $12 version of this $48 foundation") by looking them up over MCP.
- Remembers all of it (undertone, inventory, breakout history) between sessions.

## Architecture

```mermaid
graph TD
    User([User]) -->|Selfie / Request| Root[Root Orchestrator]
    Root -->|Delegate| SM[Shade Matcher]
    Root -->|Delegate| SP[Skin / Routine Planner]
    Root -->|Delegate| PR[Product Researcher]
    
    SM <-->|Read / Write| Profile[(Beauty Profile)]
    SP <-->|Read / Write| Profile
    PR <-->|Read / Write| Profile
    
    Profile <-->|Session & Memory| MB[Memory Bank]
    
    PR <-->|Query| MCP[MCP Server]
```

A root agent decides which specialist to hand off to. The three sub-agents share one beauty profile that lives in ADK's session state, with Memory Bank holding the long-term parts. Product data comes in through a read-only MCP server, so the agent can't reach past the catalog.

## Course concepts

The capstone needs at least three concepts from the course. Jamalek uses five in the code, plus two more shown in the video:

- **Multi-agent (ADK)** — root orchestrator plus three specialist sub-agents.
- **MCP server** — read-only product/dupe catalog lookup.
- **Agent skills** — each capability is a SKILL.md folder, loaded only when it's needed.
- **Sessions + long-term memory** — the beauty profile persists across sessions via session state and Memory Bank.
- **Security** — selfies handled ephemerally, human confirmation before any write or purchase (see `SECURITY.md`).
- **Antigravity and deployability** — shown in the video, deploying to Cloud Run.

## Running it

Needs Python 3.10+ and a Gemini API key from AI Studio. Keys go in environment variables.

```bash
git clone https://github.com/lailabasyouni1000-cyber/jamalek.git
cd jamalek

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export GEMINI_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"

# start the Flask web application (automatically hosts orchestrator and triggers MCP tool subprocesses)
python app.py
```

Drag and drop a selfie or tell Jamalek about your skin to get started!

## Deploying

```bash
gcloud run deploy jamalek \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,GOOGLE_API_KEY=$GOOGLE_API_KEY
```

The key is passed in at runtime, never baked into the container.

## Layout

```
jamalek/
├── agents/             # Root orchestrator & sub-agents
│   ├── orchestrator.py
│   ├── skin_analyst.py
│   ├── shade_matcher.py
│   ├── routine_planner.py
│   └── product_researcher.py
├── data/               # Product catalog database
│   └── products.json
├── skills/             # Instruction skills loaded by agents
│   ├── product_researcher.md
│   ├── routine_planner.md
│   ├── shade_matcher.md
│   └── skin_analyst.md
├── templates/          # Web frontend template
│   └── index.html
├── app.py              # Main Flask application
├── mcp_server.py       # Catalog query tool (Stdio MCP server)
├── memory.py           # Profile loading and saving logic
├── Dockerfile          # Container specification
├── SECURITY.md         # Data privacy and safety statement
├── README.md
└── requirements.txt
```

## Security

Selfies are processed purely in-memory and are never stored on disk. Anything that updates your profile asks you for consent first (consent gate). Details are in [SECURITY.md](file:///Users/lailabasyouni/.gemini/antigravity/scratch/jamalak/SECURITY.md).

## Demo

- **Video**: <VIDEO_LINK>
- **Live (Cloud Run)**: https://jamalek-724220720710.us-central1.run.app
