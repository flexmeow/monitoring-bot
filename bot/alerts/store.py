import json
import os
import tempfile
from pathlib import Path

from web3 import Web3

from bot.alerts import backup


class Store:
    """Per-user address subscriptions.

    GitHub is the source of truth: state is pulled on startup and pushed by `flush()`
    on a schedule (~daily) — NOT on every change. Mutations during the day live in
    memory, so a restart reloads from GitHub and loses at most ~24h of changes. Without
    `github` config it falls back to a local JSON file at `path` (for local dev).

    The Telegram getUpdates offset is kept in memory only (never persisted).

    Persisted schema: {"users": {"<user_id>": {"chat_id": int, "addresses": ["0x..."]}}}
    """

    def __init__(self, path: str, github: dict | None = None):
        self._path = Path(path)
        self._github = github  # {"repo", "path", "branch", "token"} or None
        self._sha: str | None = None
        self._offset: int | None = None
        self._data = self._load()

    def _load(self) -> dict:
        if self._github:
            content, self._sha = backup.get_remote(
                self._github["repo"], self._github["path"], self._github["branch"], self._github["token"]
            )
        else:
            content = self._path.read_text() if self._path.exists() else None

        data = json.loads(content) if content else {}
        loaded = {"users": data.get("users", {})}
        self._last_text = json.dumps(loaded, indent=2)  # baseline so an unchanged flush is a no-op
        return loaded

    def flush(self) -> None:
        """Persist the current state to the source of truth. Call on a schedule."""
        text = json.dumps(self._data, indent=2)
        if text == self._last_text:
            return  # nothing changed since the last flush; skip the commit

        if self._github:
            self._sha = backup.put_remote(
                self._github["repo"], self._github["path"], self._github["branch"], self._github["token"], text, self._sha
            )
        else:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=self._path.parent, suffix=".tmp")
            with os.fdopen(fd, "w") as f:
                f.write(text)
            os.replace(tmp, self._path)  # atomic swap

        self._last_text = text

    # -------------------------------------------------------------------------
    # Reads
    # -------------------------------------------------------------------------

    def get_offset(self) -> int | None:
        return self._offset

    def list_addresses(self, user_id: int) -> list[str]:
        user = self._data["users"].get(str(user_id))
        return list(user["addresses"]) if user else []

    def watchers_of(self, address: str) -> list[int]:
        """Chat IDs of all users watching the given address."""
        address = Web3.to_checksum_address(address)
        return [u["chat_id"] for u in self._data["users"].values() if address in u["addresses"]]

    # -------------------------------------------------------------------------
    # Writes (in memory only — persisted to GitHub by flush())
    # -------------------------------------------------------------------------

    def set_offset(self, offset: int) -> None:
        self._offset = offset

    def ensure_user(self, user_id: int, chat_id: int) -> None:
        user = self._data["users"].setdefault(str(user_id), {"chat_id": chat_id, "addresses": []})
        user["chat_id"] = chat_id  # refresh in case it changed

    def add_address(self, user_id: int, chat_id: int, address: str, max_addresses: int) -> str:
        """Returns 'added', 'exists', or 'cap'."""
        user = self._data["users"].setdefault(str(user_id), {"chat_id": chat_id, "addresses": []})
        user["chat_id"] = chat_id
        if address in user["addresses"]:
            return "exists"
        if len(user["addresses"]) >= max_addresses:
            return "cap"
        user["addresses"].append(address)
        return "added"

    def remove_address(self, user_id: int, address: str) -> bool:
        user = self._data["users"].get(str(user_id))
        if not user or address not in user["addresses"]:
            return False
        user["addresses"].remove(address)
        return True
