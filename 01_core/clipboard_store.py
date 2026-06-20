"""Persistent multi-slot clipboard model (no UI).

The hub keeps a fixed grid of clipboard slots (75 by default) so users can park
and recall snippets. This module owns the data and persistence only; rendering
and hotkeys live in the UI and AHK layers respectively.

Persistence is a single JSON document written atomically. The store is small
and human-scale, so a flat JSON file keeps it inspectable and avoids pulling a
database into the desktop app prematurely.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import tempfile
from pathlib import Path

from models import ClipboardSlot

DEFAULT_SLOT_COUNT = 75


class ClipboardStore:
    """Fixed-size, file-backed collection of :class:`ClipboardSlot` records."""

    def __init__(self, store_path: Path, slot_count: int = DEFAULT_SLOT_COUNT):
        if slot_count <= 0:
            raise ValueError("slot_count must be positive")
        self.store_path = store_path
        self.slot_count = slot_count
        self._slots: list[ClipboardSlot] = [ClipboardSlot(index=i) for i in range(slot_count)]
        self.load()

    @classmethod
    def from_config(cls, root: Path, clipboard_cfg: dict) -> "ClipboardStore":
        slot_count = int(clipboard_cfg.get("slots", DEFAULT_SLOT_COUNT))
        store_rel = str(clipboard_cfg.get("store_file", "05_logs/clipboard_slots.json"))
        return cls(root / store_rel, slot_count=slot_count)

    # -- access -------------------------------------------------------------
    def slots(self) -> list[ClipboardSlot]:
        return list(self._slots)

    def get(self, index: int) -> ClipboardSlot:
        self._check_index(index)
        return self._slots[index]

    # -- mutation -----------------------------------------------------------
    def set(self, index: int, text: str) -> ClipboardSlot:
        """Store ``text`` in a slot, stamping the current UTC time, and persist."""
        self._check_index(index)
        slot = ClipboardSlot(index=index, text=text, timestamp=_now_iso())
        self._slots[index] = slot
        self.save()
        return slot

    def clear(self, index: int) -> None:
        self._check_index(index)
        self._slots[index] = ClipboardSlot(index=index)
        self.save()

    def first_empty_index(self) -> int | None:
        for slot in self._slots:
            if slot.is_empty:
                return slot.index
        return None

    def ranked_slots(self) -> list[dict[str, object]]:
        """Return non-empty slots ranked by lightweight learned-preference signals.

        Ranking is intentionally deterministic and available from day one: a
        Markov-style keyword/content score dominates at first, while timestamp
        recency acts as a tie-breaker. The result shape is API-friendly so a
        future SQLite preference/River model can add scores without changing
        callers.
        """
        ranked = []
        for slot in self._slots:
            if slot.is_empty:
                continue
            markov_score = _markov_keyword_score(slot.text)
            recency_score = _timestamp_score(slot.timestamp)
            preference_score = 0.0
            river_score = 0.0
            total_score = (0.7 * markov_score) + (0.2 * recency_score) + (0.1 * preference_score) + river_score
            ranked.append(
                {
                    "index": slot.index,
                    "text": slot.text,
                    "timestamp": slot.timestamp,
                    "preview": slot.preview(),
                    "score": round(total_score, 4),
                    "scores": {
                        "markov": round(markov_score, 4),
                        "preference": preference_score,
                        "river": river_score,
                        "recency": round(recency_score, 4),
                    },
                }
            )
        return sorted(ranked, key=lambda item: (item["score"], item["timestamp"]), reverse=True)

    # -- persistence --------------------------------------------------------
    def load(self) -> None:
        if not self.store_path.exists():
            return
        try:
            raw = json.loads(self.store_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # A corrupt store should not brick the app; start from empty slots.
            return
        for item in raw.get("slots", []):
            index = item.get("index")
            if isinstance(index, int) and 0 <= index < self.slot_count:
                self._slots[index] = ClipboardSlot(
                    index=index,
                    text=str(item.get("text", "")),
                    timestamp=str(item.get("timestamp", "")),
                )

    def save(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "slot_count": self.slot_count,
            "slots": [
                {"index": s.index, "text": s.text, "timestamp": s.timestamp}
                for s in self._slots
                if not s.is_empty
            ],
        }
        _atomic_write(self.store_path, json.dumps(payload, ensure_ascii=False, indent=2))

    def _check_index(self, index: int) -> None:
        if not 0 <= index < self.slot_count:
            raise IndexError(f"Slot index out of range: {index} (0..{self.slot_count - 1})")


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _atomic_write(path: Path, text: str) -> None:
    """Write via a temp file + replace so a crash can't truncate the store."""
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


def _markov_keyword_score(text: str) -> float:
    """Cheap day-one relevance score based on repeated tokens and action words."""
    words = [word.strip(".,;:!?()[]{}\"'’“”").lower() for word in text.split()]
    words = [word for word in words if len(word) > 2]
    if not words:
        return 0.0
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    repeated = sum(count - 1 for count in counts.values() if count > 1)
    action_terms = {"todo", "fix", "build", "ship", "test", "prompt", "api", "clip", "rewrite"}
    action_hits = sum(1 for word in words if word in action_terms)
    return min(1.0, (repeated / max(len(words), 1)) + (action_hits * 0.08) + min(len(words), 200) / 1000)


def _timestamp_score(timestamp: str) -> float:
    if not timestamp:
        return 0.0
    try:
        when = dt.datetime.fromisoformat(timestamp)
        if when.tzinfo is None:
            when = when.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return 0.0
    age_hours = max((dt.datetime.now(dt.timezone.utc) - when).total_seconds() / 3600, 0)
    return max(0.0, 1.0 - min(age_hours / (24 * 30), 1.0))
