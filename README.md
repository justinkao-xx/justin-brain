# Justin Brain

A personal knowledge bot that answers questions about Justin's work, processes, and projects — as if Justin himself were responding. Ask it anything via Slack.

---

## What it does

- Answers questions in Slack (DMs, @mentions, or `/ask-justin`) using your own documents and references as the source of truth
- Responds in first person, in your voice
- Lets you add new knowledge at any time via `/add-doc` in Slack or the CLI
- Supports files (PDF, DOCX, TXT, Markdown, etc.) and URLs (docs sites, wikis, Google Docs, Notion pages, etc.)

---

## How it works

```
You add a file or URL
        ↓
Text is chunked and embedded (OpenAI text-embedding-3-small)
        ↓
Vectors stored in ChromaDB (persistent)
        ↓
Slack message arrives → relevant chunks retrieved
        ↓
Claude (claude-opus-4-6) answers using retrieved context
        ↓
Response sent back to Slack
```

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/justinkao-xx/justin-brain.git
cd justin-brain
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in:

| Variable | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `SLACK_BOT_TOKEN` | Your Slack app → OAuth & Permissions |
| `SLACK_SIGNING_SECRET` | Your Slack app → Basic Information |

### 3. Customize your voice

Open `retrieval/query.py` and edit the `SYSTEM_PROMPT` constant. This is what tells Claude to answer as you — describe your role, your tone, your area of expertise, and anything specific people should know about how you communicate.

```python
SYSTEM_PROMPT = """You are Justin's digital brain..."""
```

### 4. Create your Slack app

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → From Scratch
2. Under **OAuth & Permissions**, add these Bot Token Scopes:
   - `chat:write`
   - `commands`
   - `im:history`
   - `app_mentions:read`
3. Install the app to your workspace and copy the **Bot User OAuth Token**
4. Under **Basic Information**, copy the **Signing Secret**
5. Under **Slash Commands**, create two commands:
   - `/ask-justin` → Request URL: `https://your-app.railway.app/slack/events`
   - `/add-doc` → Request URL: `https://your-app.railway.app/slack/events`
6. Under **Event Subscriptions**, enable events and set the Request URL to `https://your-app.railway.app/slack/events`, then subscribe to:
   - `app_mention`
   - `message.im`

### 5. Deploy to Railway

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select `justin-brain`
3. Add all environment variables from your `.env` file in the Railway dashboard
4. Add a **Volume** mounted at `/app/data` so the vector database persists across deploys
5. Railway will auto-deploy on every push to `main`

---

## Adding knowledge

### Via Slack (recommended)

```
/add-doc https://your-company-wiki.com/some-page
/add-doc https://docs.google.com/document/d/...
```

### Via CLI

```bash
# Single file
python ingest/ingest.py --file path/to/runbook.pdf

# Entire folder
python ingest/ingest.py --dir path/to/docs/

# URL
python ingest/ingest.py --url https://example.com/process-doc
```

Supported file types: PDF, DOCX, TXT, Markdown, CSV, HTML, and most plain-text formats.

---

## Using the bot in Slack

| Method | Example |
|---|---|
| DM the bot | Just message it directly |
| @mention in a channel | `@Justin Brain how do I request time off?` |
| Slash command | `/ask-justin what's the process for deploying to prod?` |

---

## Project structure

```
justin-brain/
├── bot/
│   └── app.py          # Slack bot and Flask webhook server
├── ingest/
│   └── ingest.py       # CLI to add files and URLs to the knowledge base
├── retrieval/
│   └── query.py        # RAG query logic + Claude prompt
├── data/               # Local vector DB (gitignored, persisted via Railway volume)
├── config.py           # Loads all environment variables
├── requirements.txt
├── Procfile            # Tells Railway how to start the app
└── .env.example        # Template for required environment variables
```

---

## Updating the app

### Updating knowledge

To add new documents or remove stale ones, use the ingest CLI or `/add-doc` in Slack. There is currently no delete command — to fully reset the knowledge base, delete the `data/chroma` directory (locally) or wipe the Railway volume and re-ingest.

### Updating the voice / system prompt

Edit `SYSTEM_PROMPT` in `retrieval/query.py`, commit, and push. Railway will redeploy automatically.

### Updating dependencies

```bash
pip install -r requirements.txt
# after adding a new package:
pip freeze > requirements.txt
git add requirements.txt && git commit -m "update dependencies"
git push
```

### Deploying changes

```bash
git add .
git commit -m "describe your change"
git push
```

Railway auto-deploys on every push to `main`.

---

## Tech stack

| Component | Tool |
|---|---|
| LLM | Claude (claude-opus-4-6) via Anthropic API |
| Embeddings | OpenAI text-embedding-3-small |
| RAG framework | LlamaIndex |
| Vector database | ChromaDB (local, persisted) |
| Slack interface | Slack Bolt + Flask |
| Hosting | Railway |
