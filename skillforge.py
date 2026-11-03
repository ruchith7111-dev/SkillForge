"""Backward-compatible entry point for the SkillForge application."""

from skillforge_app.cli import ask, menu, show
from skillforge_app.config import DEFAULT_SETTINGS, FIELDS
from skillforge_app.skills import (
    add_skill,
    delete_skill,
    export_csv,
    export_pdf,
    filter_rows,
    find,
    level_for,
    rows,
    set_settings,
    summary,
    track_skill,
    update_skill,
)
from skillforge_app.store import load, save

__all__ = [
    "DEFAULT_SETTINGS",
    "FIELDS",
    "add_skill",
    "ask",
    "delete_skill",
    "export_csv",
    "export_pdf",
    "filter_rows",
    "find",
    "level_for",
    "load",
    "menu",
    "rows",
    "save",
    "set_settings",
    "show",
    "summary",
    "track_skill",
    "update_skill",
]
if __name__ == "__main__":
    menu()