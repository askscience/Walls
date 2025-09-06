from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional


@dataclass
class Bookmark:
    name: str
    url: str


class BookmarksManager:
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".walls_browser_bookmarks.json"
        self.bookmarks: List[Bookmark] = []
        self.load()

    def load(self):
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text())
                self.bookmarks = [Bookmark(**b) for b in data]
            except Exception:
                self.bookmarks = []

    def save(self):
        try:
            self.storage_path.write_text(json.dumps([asdict(b) for b in self.bookmarks], indent=2))
        except Exception:
            pass

    def add(self, name: str, url: str):
        self.bookmarks.append(Bookmark(name=name, url=url))
        self.save()

    def list(self) -> List[Bookmark]:
        return list(self.bookmarks)