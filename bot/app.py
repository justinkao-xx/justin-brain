"""
Slack bot for Justin's brain.

Responds to:
  - DMs to the bot
  - @mentions in any channel
  - /ask-justin <question>   — slash command
  - /add-doc <url or path>   — ingest a new source on the fly
"""
import logging
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from config import PORT, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET
from ingest.ingest import ingest_file, ingest_url
from retrieval.query import query

logging.basicConfig(level=logging.INFO)

slack_app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)


# ── Slash command: /ask-justin ─────────────────────────────────────────────────

@slack_app.command("/ask-justin")
def handle_ask(ack, respond, command):
    ack()
    question = command.get("text", "").strip()
    if not question:
        respond("Usage: `/ask-justin <your question>`")
        return
    respond(f"_Thinking..._")
    try:
        answer = query(question)
        respond(answer)
    except Exception as e:
        logging.exception("Query failed")
        respond(f"Sorry, something went wrong: {e}")


# ── Slash command: /add-doc ────────────────────────────────────────────────────

@slack_app.command("/add-doc")
def handle_add_doc(ack, respond, command):
    ack()
    source = command.get("text", "").strip()
    if not source:
        respond("Usage: `/add-doc <url or local file path>`")
        return
    respond(f"Ingesting `{source}`… this may take a moment.")
    try:
        if source.startswith("http://") or source.startswith("https://"):
            ingest_url(source)
        else:
            ingest_file(source)
        respond(f"Done! `{source}` has been added to the brain.")
    except Exception as e:
        logging.exception("Ingest failed")
        respond(f"Error ingesting `{source}`: {e}")


# ── @mentions in channels ──────────────────────────────────────────────────────

@slack_app.event("app_mention")
def handle_mention(event, say):
    # Strip the @mention prefix
    text = event.get("text", "")
    words = text.split(None, 1)
    question = words[1].strip() if len(words) > 1 else ""
    if not question:
        say("Hey! Ask me anything about my work.")
        return
    say("_Thinking..._")
    try:
        answer = query(question)
        say(answer)
    except Exception as e:
        logging.exception("Query failed")
        say(f"Sorry, something went wrong: {e}")


# ── Direct messages ────────────────────────────────────────────────────────────

@slack_app.event("message")
def handle_dm(message, say):
    # Only respond to direct messages (not channel messages or bot messages)
    if message.get("channel_type") != "im":
        return
    if message.get("subtype"):  # ignore edited/deleted/bot messages
        return
    question = message.get("text", "").strip()
    if not question:
        return
    try:
        answer = query(question)
        say(answer)
    except Exception as e:
        logging.exception("Query failed")
        say(f"Sorry, something went wrong: {e}")


# ── Flask webhook endpoint ─────────────────────────────────────────────────────

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=PORT)
