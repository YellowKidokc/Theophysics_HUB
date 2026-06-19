"""Headless tests for the backend core (no PySide6 / no network required).

Run from the repo root:

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import logging
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_core"))

from action_registry import ActionRegistry  # noqa: E402
from clipboard_store import ClipboardStore  # noqa: E402
from config_loader import ConfigLoader  # noqa: E402
from hotkey_manager import HotkeyManager  # noqa: E402
from models import LinkRecord, PromptRecord  # noqa: E402
from prompt_engine import PromptEngine  # noqa: E402
from registry import Registry  # noqa: E402
from tts import TTSError, TTSProvider  # noqa: E402


class ConfigLoaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ConfigLoader(ROOT)

    def test_core_config_files_load(self) -> None:
        self.assertEqual(self.config.app_config()["app_name"], "Stratum")
        self.assertTrue(self.config.actions_config())
        self.assertIn("dashboard", self.config.panels())
        self.assertEqual(self.config.clipboard_config()["slots"], 75)

    def test_optional_files_return_lists(self) -> None:
        self.assertIsInstance(self.config.prompts_config(), list)
        self.assertIsInstance(self.config.links_config(), list)
        self.assertIsInstance(self.config.hotkeys_config(), list)


class ActionRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        # Attach a NullHandler so the expected failure log doesn't spill the
        # last-resort traceback to stderr during the test run.
        logging.getLogger("theophysics.actions").addHandler(logging.NullHandler())
        self.registry = ActionRegistry(ROOT)

    def test_lists_configured_actions(self) -> None:
        ids = {record.id for record in self.registry.list_actions()}
        self.assertIn("clean_dictation", ids)
        self.assertIn("rewrite_coherent_openai", ids)

    def test_runs_pure_action(self) -> None:
        result = self.registry.run(
            "clean_dictation",
            {"selection": "um this  is i a test", "clipboard": ""},
        )
        self.assertTrue(result.ok)
        self.assertIn("I", result.output)
        self.assertNotIn("um", result.output.lower().split())

    def test_unknown_action_fails_cleanly(self) -> None:
        result = self.registry.run("does_not_exist", {})
        self.assertFalse(result.ok)
        self.assertIsNotNone(result.error)


class ClipboardStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "slots.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_set_get_clear_and_persist(self) -> None:
        store = ClipboardStore(self.path, slot_count=5)
        store.set(2, "hello world")
        self.assertEqual(store.get(2).text, "hello world")
        self.assertTrue(store.get(2).timestamp)

        # Reload from disk to confirm persistence.
        reloaded = ClipboardStore(self.path, slot_count=5)
        self.assertEqual(reloaded.get(2).text, "hello world")

        reloaded.clear(2)
        self.assertTrue(reloaded.get(2).is_empty)

    def test_first_empty_and_bounds(self) -> None:
        store = ClipboardStore(self.path, slot_count=3)
        store.set(0, "a")
        self.assertEqual(store.first_empty_index(), 1)
        with self.assertRaises(IndexError):
            store.get(99)


class RegistryAndPromptTests(unittest.TestCase):
    def test_registry_loads_typed_content(self) -> None:
        state = Registry(ROOT).load()
        self.assertTrue(all(isinstance(p, PromptRecord) for p in state.prompts))
        self.assertTrue(all(isinstance(link, LinkRecord) for link in state.links))

    def test_prompt_engine_renders(self) -> None:
        engine = PromptEngine([PromptRecord(name="echo", content="X: {text}")])
        self.assertEqual(engine.render("echo", "hi"), "X: hi")
        with self.assertRaises(KeyError):
            engine.get("missing")

    def test_hotkey_bindings_map_to_commands(self) -> None:
        bindings = HotkeyManager(ROOT).bindings()
        self.assertEqual(bindings.get("Ctrl+Alt+C"), "gui clipboard")
        self.assertEqual(bindings.get("Ctrl+Space"), "rewrite")


class ModelValidationTests(unittest.TestCase):
    def test_prompt_requires_fields(self) -> None:
        with self.assertRaises(ValueError):
            PromptRecord.from_config({"name": "", "content": "x"})

    def test_link_requires_fields(self) -> None:
        with self.assertRaises(ValueError):
            LinkRecord.from_config({"label": "x"})


class TTSTests(unittest.TestCase):
    def test_empty_text_raises(self) -> None:
        with self.assertRaises(TTSError):
            TTSProvider().speak("   ")

    @unittest.skipIf(sys.platform.startswith("win"), "non-Windows behavior only")
    def test_unsupported_platform_raises(self) -> None:
        provider = TTSProvider()
        self.assertFalse(provider.is_supported())
        with self.assertRaises(TTSError):
            provider.speak("hello")


if __name__ == "__main__":
    unittest.main()
