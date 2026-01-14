"""
title: Gemini Thinking Summary
description: Summarize Gemini reasoning stream and emit status updates.
author: GrayXu
author_url: https://github.com/GrayXu
funding_url: https://github.com/GrayXu/OpenWebUI-Funcs
"""

import asyncio
import contextvars
import re
from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Optional, Callable, Awaitable


class Filter:
    @dataclass
    class _StreamState:
        reasoning_buffer: str = ""
        scan_pos: int = 0
        last_summary: str = ""
        event_emitter: Optional[Callable[[dict], Awaitable[None]]] = None
        finished_emitted: bool = False
        in_reasoning: bool = False

    class Valves(BaseModel):
        priority: int = Field(default=100, description="priority")

    def __init__(self):
        self.valves = self.Valves()
        self._bold_line_re = re.compile(r"\*\*(.+?)\*\*")
        self._state_ctx = contextvars.ContextVar(
            "gemini_think_summary_state", default=None
        )

    async def inlet(
        self, body: dict, __event_emitter__, __user__: Optional[dict] = None
    ) -> dict:
        self._state_ctx.set(
            self._StreamState(
                reasoning_buffer="",
                scan_pos=0,
                last_summary="",
                event_emitter=__event_emitter__,
                finished_emitted=False,
                in_reasoning=False,
            )
        )
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

    def _extract_new_summary(self, state: _StreamState) -> Optional[str]:
        if state.scan_pos >= len(state.reasoning_buffer):
            return None

        segment = state.reasoning_buffer[state.scan_pos :]
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

        state.scan_pos += consumed

        if newest and newest != state.last_summary:
            state.last_summary = newest
            return newest

        return None

    async def outlet(
        self, body: dict, __event_emitter__, __user__: Optional[dict] = None
    ) -> dict:
        # No-op in outlet; this filter only monitors streaming reasoning content.
        return body

    def _emit_status(
        self, state: _StreamState, summary: str, finished: bool = False
    ) -> None:
        if not state.event_emitter:
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
            asyncio.create_task(state.event_emitter(payload))
        except RuntimeError:
            return

    def stream(self, event: dict) -> dict:
        state = self._state_ctx.get()
        if state is None:
            state = self._StreamState()
        reasoning_chunk = self._collect_reasoning_chunk(event)
        if not reasoning_chunk:
            if state.in_reasoning and not state.finished_emitted:
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
                    self._emit_status(state, "😎 Thinking Finished", finished=True)
                    state.finished_emitted = True
            return event

        state.reasoning_buffer += reasoning_chunk
        state.in_reasoning = True
        summary = self._extract_new_summary(state)
        if summary:
            self._emit_status(state, summary)
        return event
