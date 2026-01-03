"""
title: Gemini Thinking Summary
description: Summarize Gemini reasoning stream and emit status updates.
author: GrayXu
author_url: https://github.com/GrayXu
funding_url: https://github.com/GrayXu/OpenWebUI-Funcs
"""

import asyncio
import re
from pydantic import BaseModel, Field
from typing import Optional


class Filter:
    class Valves(BaseModel):
        priority: int = Field(default=100, description="priority")

    def __init__(self):
        self.valves = self.Valves()
        self._reasoning_buffer = ""
        self._scan_pos = 0
        self._last_summary = ""
        self._bold_line_re = re.compile(r"\*\*(.+?)\*\*")
        self._event_emitter = None
        self._finished_emitted = False
        self._in_reasoning = False

    async def inlet(
        self, body: dict, __event_emitter__, __user__: Optional[dict] = None
    ) -> dict:
        self._event_emitter = __event_emitter__
        self._finished_emitted = False
        self._in_reasoning = False
        return body

    def _collect_reasoning_chunk(self, event: dict) -> str:
        chunk = ""
        for choice in event.get("choices", []):
            delta = choice.get("delta") or {}
            if delta.get("reasoning_content"):
                chunk += delta["reasoning_content"]
            message = choice.get("message") or {}
            if message.get("reasoning_content"):
                chunk += message["reasoning_content"]
        return chunk

    def _extract_new_summary(self) -> Optional[str]:
        if self._scan_pos >= len(self._reasoning_buffer):
            return None

        segment = self._reasoning_buffer[self._scan_pos :]
        lines = segment.splitlines(keepends=True)
        if not lines:
            return None

        consumed = 0
        newest = None

        for line in lines:
            if not line.endswith(("\n", "\r")):
                break
            consumed += len(line)
            stripped = line.strip()
            match = self._bold_line_re.fullmatch(stripped)
            if match:
                newest = match.group(1).strip()

        self._scan_pos += consumed

        if newest and newest != self._last_summary:
            self._last_summary = newest
            return newest

        return None

    async def outlet(
        self, body: dict, __event_emitter__, __user__: Optional[dict] = None
    ) -> dict:
        # No-op in outlet; this filter only monitors streaming reasoning content.
        return body

    def _emit_status(self, summary: str, finished: bool = False) -> None:
        if not self._event_emitter:
            return
        description = summary if finished else f"🤔 {summary}..."
        payload = {
            "type": "status",
            "data": {
                "description": description,
                "done": True,
                "hidden": False,
            },
        }
        try:
            asyncio.create_task(self._event_emitter(payload))
        except RuntimeError:
            return

    def stream(self, event: dict) -> dict:
        reasoning_chunk = self._collect_reasoning_chunk(event)
        if not reasoning_chunk:
            if self._in_reasoning and not self._finished_emitted:
                has_content = False
                for choice in event.get("choices", []):
                    delta = choice.get("delta") or {}
                    if delta.get("content"):
                        has_content = True
                        break
                    message = choice.get("message") or {}
                    if message.get("content"):
                        has_content = True
                        break
                if has_content:
                    self._emit_status("😎 Thinking Finished", finished=True)
                    self._finished_emitted = True
            return event

        self._reasoning_buffer += reasoning_chunk
        self._in_reasoning = True
        summary = self._extract_new_summary()
        if summary:
            self._emit_status(summary)
        return event
