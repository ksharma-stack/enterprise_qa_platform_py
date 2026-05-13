"""
Locator Healing Service (MCP-compatible), AI service responsible for self-healing decisions.

- Accepts intent + constraints + DOM snapshot
- Delegates to LLM
- NEVER mutates locator contracts
- Returns STRICT JSON string
"""

from __future__ import annotations

from src.framework.adapters.ai_client import OpenAIClient

AI_SERVICE = None


def set_ai_service(service):
    """set ai_service"""
    global AI_SERVICE
    AI_SERVICE = service


def get_ai_service():
    """get ai_service"""
    return AI_SERVICE


class AiService:
    """Locator healing service via Azure openai"""

    def __init__(self, ai_client: OpenAIClient):
        self.ai_client = ai_client

    def suggest_selectors(
        self, intent: dict, dom_snapshot: str, constraints: dict
    ) -> list[dict]:
        """
        Returns candidate selectors with confidence.
        """

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are an accessibility-first test automation expert. "
                    "Suggest robust selectors without modifying existing contracts."
                    "Return the response as VALID JSON ONLY."
                    "Do not include markdown, code fences, backticks, comments, explanations, or any extra text."
                    "Do not wrap the JSON in quotes."
                    "Output must start with `{` and end with `}`."
                    "If you cannot comply, return an empty JSON object `{}`."
                ),
            },
            {
                "role": "user",
                "content": f"""
                Intent:
                {intent}

                Constraints:
                {constraints}

                DOM Snapshot:
                {dom_snapshot}

                Respond with STRICT JSON only using schema:
                {{
                "action": "heal | abort | retry",
                "confidence": float,
                "locator": {{
                    "strategy": "role | css | xpath",
                    "value": "string"
                }}
                }}


                """,
            },
        ]
        # Return JSON list of selector candidates with confidence scores.
        raw = self.ai_client.complete(prompt)

        # Parsing intentionally isolated
        return self._parse_response(raw)

    def _parse_response(self, raw: str) -> list[dict]:
        """
        MCP-safe parsing layer (can evolve independently).
        """
        import json

        return json.loads(raw)

    # def heal_locator(self, dom_snapshot: str, intent: str) -> str:
    #     """
    #     Use AI to suggest a new locator based on the DOM snapshot and intent.
    #     """
    #     return self.ai_client.suggest_locator(dom_snapshot, intent)


# class SelfHealingEngine:
#     def attempt_heal(self, contract, dom_snapshot):
#         prompt = render_prompt(contract, dom_snapshot)

#         suggestion = self.ai_client.suggest_locator(prompt)

#         if suggestion["confidence"] < config.healing_threshold:
#             raise HealingRejected("Low confidence")

#         return suggestion

#     def require_approval(old, new):
#         if config.mode == "manual":
#             raise HealingPendingApproval(old, new)

#         if config.mode == "auto":
#             return True

#     def apply_patch(locator_file, key, suggestion):
#         data = load_yaml(locator_file)

#         data[key][suggestion["strategy"]] = suggestion["value"]

#         data["_healing_meta"] = {
#             "updated_by": "azure-openai",
#             "confidence": suggestion["confidence"],
#             "timestamp": utc_now(),
#         }

#         save_yaml(locator_file, data)
