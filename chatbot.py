# chatbot.py

import os
from dotenv import load_dotenv
from openai import OpenAI

from tools.geo_tools import tool_schema          # the distance tool
from src.agent.agent import ReActAgent               # the ReAct agent


load_dotenv()

# ── Minimal LLMProvider wrapper so agent.py can stay framework-agnostic ───────

class LLMProvider:
    def __init__(self, client: OpenAI, model: str):
        self.client     = client
        self.model_name = model

    def generate(self, history: list, system_prompt: str = "") -> str:
        """Send full message history to OpenAI and return the reply text."""
        system_msg = [{"role": "system", "content": system_prompt}] if system_prompt else []
        response   = self.client.chat.completions.create(
            model    = self.model_name,
            messages = system_msg + history,
        )
        return response.choices[0].message.content


# ── Minimal logger stub (replaces src.telemetry.logger if not installed) ──────

class _SimpleLogger:
    def log_event(self, event: str, data: dict):
        print(f"[LOG] {event}: {data}")

# Monkey-patch the logger import used inside agent.py
import src.telemetry.logger as _log_module  # noqa: E402
_log_module.logger = _SimpleLogger()


# ── Bootstrap ─────────────────────────────────────────────────────────────────

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm           = LLMProvider(openai_client, model="gpt-4o")
tools         = [tool_schema]               # add more tools to this list
agent         = ReActAgent(llm, tools, max_steps=6)


# ── Chat loop ─────────────────────────────────────────────────────────────────

print("Chatbot ready (with geo-distance tool). Type 'exit' to quit.\n")

messages = []  # plain conversation history for non-agent turns (optional)

while True:
    try:
        user_input = input("You: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        break

    if not user_input:
        continue

    if user_input.lower() in {"exit", "quit"}:
        print("Goodbye!")
        break

    # Every message goes through the ReAct agent
    # The agent decides on its own whether to call a tool or answer directly
    agent.history = []                      # reset per conversation turn
    reply = agent.run(user_input)
    print(f"Bot: {reply}\n")
