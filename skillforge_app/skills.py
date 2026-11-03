import csv
import math
from datetime import date

from .config import FIELDS
from .exporters import export_pdf as write_pdf


def _positive(value, what):
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{what} must be a positive number.")
    return value


def _normalize_name(name):
    return " ".join(str(name).split())


def _normalize_category(category):
    return str(category).strip() or "General"


def _target(data, target):
    if not 1 <= target <= data["settings"]["max_level"]:
        raise ValueError(f"Target must be between 1 and {data['settings']['max_level']}.")
    return target


def find(data, name):
    key = _normalize_name(name).lower()
    return next((skill for skill in data["skills"] if skill["name"].lower() == key), None)


def _get(data, name):
    skill = find(data, name)
    if skill is None:
        raise ValueError(f"Skill '{name}' not found.")
    return skill


def level_for(hours, settings):
    return min(1 + int(hours // settings["hours_per_level"]), settings["max_level"])


def rows(data):
    """Skills with derived level/achieved flag. Computed, never stored, never stale."""
    settings = data["settings"]
    result = []
    for skill in data["skills"]:
        level = level_for(skill["hours"], settings)
        result.append({**skill, "level": level, "achieved": level >= skill["target"]})
    return result


def add_skill(data, name, target, category="General"):
    name = _normalize_name(name)
    if not name:
        raise ValueError("Name cannot be empty.")
    if find(data, name):
        raise ValueError(f"Skill '{name}' already exists.")
    data["skills"].append(
        {
            "name": name,
            "category": _normalize_category(category),
            "target": _target(data, target),
            "hours": 0.0,
            "added": date.today().isoformat(),
        }
    )


def update_skill(data, name, category=None, target=None):
    skill = _get(data, name)
    if category and category.strip():
        skill["category"] = _normalize_category(category)
    if target is not None:
        skill["target"] = _target(data, target)


def delete_skill(data, name):
    data["skills"].remove(_get(data, name))


def track_skill(data, name, hours):
    skill = _get(data, name)
    skill["hours"] = round(skill["hours"] + _positive(hours, "Hours"), 2)


def set_settings(data, hours_per_level, max_level):
    max_level = int(max_level)
    if max_level < 1 or any(skill["target"] > max_level for skill in data["skills"]):
        raise ValueError("Max level must be >= 1 and >= every skill target.")
    data["settings"] = {
        "hours_per_level": _positive(hours_per_level, "Hours per level"),
        "max_level": max_level,
    }


def filter_rows(data, category=None, achieved=None):
    """achieved=True -> done only, False -> in progress only, None -> all."""
    category_key = category.strip().lower() if category else None
    return [
        row
        for row in rows(data)
        if (category_key is None or row["category"].lower() == category_key)
        and (achieved is None or row["achieved"] == achieved)
    ]


def summary(data):
    rows_list = rows(data)
    if not rows_list:
        return {
            "total": 0,
            "achieved": 0,
            "in_progress": 0,
            "avg_level": 0,
            "total_hours": 0.0,
            "categories": {},
        }

    total_level = 0
    total_hours = 0.0
    achieved = 0
    category_counts = {}
    for row in rows_list:
        total_level += row["level"]
        total_hours += row["hours"]
        achieved += int(row["achieved"])
        key = row["category"].lower()
        if key not in category_counts:
            category_counts[key] = {"label": row["category"], "count": 0}
        category_counts[key]["count"] += 1

    return {
        "total": len(rows_list),
        "achieved": achieved,
        "in_progress": len(rows_list) - achieved,
        "avg_level": round(total_level / len(rows_list), 2),
        "total_hours": round(total_hours, 2),
        "categories": {info["label"]: info["count"] for info in category_counts.values()},
    }


def export_csv(data, path="skillforge_export.csv"):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows(data))
    return path


def export_pdf(data, path="skillforge_report.pdf"):
    return write_pdf(rows(data), path)
