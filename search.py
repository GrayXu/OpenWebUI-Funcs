"""
title: Web Search
description: Create a Filter action toggle button that maps to other search/thinking models.
author: GrayXu
author_url: https://github.com/GrayXu
funding_url: https://github.com/GrayXu/OpenWebUI-Funcs
"""

from pydantic import BaseModel, Field
from typing import Optional


class Filter:
    class Valves(BaseModel):
        priority: int = Field(default=100, description="priority")
        pass

    def __init__(self):
        self.valves = self.Valves()
        self.toggle = True
        # Model mapping based on README.md
        self.model_mapping = {
            "deepseek": {
                "base": "",
                "search": None,
                "think": "-thinking",
                "think_search": None,
                "suffix": True,
            },
            "gemini-2.5-flash": {
                "base": "gemini-2.5-flash",
                "search": "gemini-2.5-flash-search",
                "think": "gemini-2.5-flash-thinking",
                "think_search": "gemini-2.5-flash-search",
            },
            "gemini-2.5-pro": {
                "base": "gemini-2.5-pro",
                "search": "gemini-2.5-pro-search-show",
                "think": "gemini-2.5-pro-thinking",
                "think_search": "gemini-2.5-pro-search-show-thinking",
            },
            "gemini": {
                "base": "-preview",
                "search": "-search-show",
                "think": "-thinking",
                "think_search": "-search-show-thinking",
                "suffix": True,
            },
            "doubao-seed": {
                "base": "",
                "search": None,
                "think": "-thinking",
                "think_search": None,
                "suffix": True,
            },
            "claude": {
                "base": "",
                "search": None,
                "think": "-thinking",
                "think_search": None,
                "suffix": True,
            },
            "qwen": {
                "base": "",
                "search": None,
                "think": "-thinking",
                "think_search": None,
                "suffix": True,
            },
            "gpt": {
                "base": "gpt-5",
                "search": None,
                "think": "gpt-5-high",
                "think_search": None,
            }
        }
        self.icon = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHZpZXdCb3g9IjAgMCAyNCAyNCIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZT0iY3VycmVudENvbG9yIj4KICA8cGF0aCBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGQ9Ik0yMSAyMWwtNS4xOTctNS4xOTdtLjAwMS0uMDAxYTguNDE4IDguNDE4IDAgMSAwLTEuNDE1IDEuNDE0bDUuMTk2IDUuMTk2eiIgLz4KPC9zdmc+Cg=="""
        pass

    def detect_model_keyword(self, model_name: str) -> Optional[str]:
        """Detect which keyword the current model contains, preferring the longest match"""
        normalized_model = model_name.lower().replace("-", "").replace(".", "")
        best_match = None
        best_length = -1

        for keyword in self.model_mapping.keys():
            normalized_keyword = keyword.replace("-", "").replace(".", "")
            if normalized_keyword in normalized_model and len(normalized_keyword) > best_length:
                best_match = keyword
                best_length = len(normalized_keyword)

        return best_match

    def _apply_suffix(self, current_model: str, suffix: Optional[str]) -> str:
        """Append suffix when needed while preventing duplicates"""
        if not suffix:
            return current_model
        if current_model.endswith(suffix):
            return current_model
        return f"{current_model}{suffix}"

    async def inlet(
        self, body: dict, __event_emitter__, __user__: Optional[dict] = None
    ) -> dict:
        # Get filter IDs
        filter_ids = body.get("metadata", {}).get("filter_ids", [])
        has_search = "search" in filter_ids
        has_think = "think" in filter_ids

        # Detect current model keyword
        current_model = body.get("model", "")
        keyword = self.detect_model_keyword(current_model)

        if keyword and keyword in self.model_mapping:
            # Determine which variant to use
            if has_think and has_search:
                target_model = self.model_mapping[keyword]["think_search"]
            elif has_search:
                target_model = self.model_mapping[keyword]["search"]
            elif has_think:
                target_model = self.model_mapping[keyword]["think"]
            else:
                target_model = self.model_mapping[keyword]["base"]

            # Only update if target model is not None
            if target_model is not None:
                if self.model_mapping[keyword].get("suffix"):
                    body["model"] = self._apply_suffix(current_model, target_model)
                else:
                    body["model"] = target_model

        print("search.py----rewrite to "+body["model"])
        
        if not has_think and has_search:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "搜索网页中...",
                        "done": True,
                        "hidden": False,
                    },
                }
            )

        return body
