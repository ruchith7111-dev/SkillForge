# SkillForge – Personal Skill Growth Tracker

Console app (Python 3.10+) to add skills, log practice hours, auto-derive levels,
filter, summarise and export progress. Data persists in a JSON file.

## Run

    python skillforge.py

Optional PDF export: `pip install -r requirements.txt`

## Test

    PYTHONPATH=. python -m unittest discover -s tests -v

## Layout

    skillforge.py        compatibility entry point
    skillforge_app/      core package: config, storage, logic, CLI, exporters
    tests/               unit tests (stdlib unittest)
    skillforge_data.json created on first save in the working directory

## Rules

- Level = 1 + hours // hours_per_level, capped at max_level (Settings, default 10 h / level, max 5).
- Achieved = level >= target.
- Settings cannot set max level below any existing target.
