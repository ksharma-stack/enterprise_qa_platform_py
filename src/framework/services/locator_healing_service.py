"""
Locator Healing Service (MCP-compatible)

- Accepts intent + DOM snapshot
- Delegates to LLM
- NEVER mutates locator contracts
"""

from __future__ import annotations


class LocatorHealingService:
    """Locator healing service via Azure openai"""

    def __init__(self, ai_adapter):
        self._ai = ai_adapter

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

Return JSON list of selector candidates with confidence scores.
""",
            },
        ]

        raw = self._ai.complete(prompt)

        # Parsing intentionally isolated
        return self._parse_response(raw)

    def _parse_response(self, raw: str) -> list[dict]:
        """
        MCP-safe parsing layer (can evolve independently).
        """
        import json

        return json.loads(raw)


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
