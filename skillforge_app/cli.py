from .skills import add_skill, delete_skill, export_pdf, filter_rows, set_settings, summary, track_skill, update_skill


def ask(prompt, cast=str, default=None):
    raw = input(f"{prompt}: ").strip()
    return default if not raw and default is not None else cast(raw)


def show(items):
    if not items:
        return print("No skills.")
    print(f"{'Name':<20}{'Category':<16}{'Level':<8}{'Target':<8}{'Hours':<9}Status")
    for row in items:
        status = "achieved" if row["achieved"] else "in progress"
        print(
            f"{row['name'][:19]:<20}{row['category'][:15]:<16}{row['level']:<8}"
            f"{row['target']:<8}{row['hours']:<9}{status}"
        )


def cmd_add(data):
    add_skill(data, ask("Name"), ask(f"Target level (1-{data['settings']['max_level']})", int), ask("Category", default="General"))
    print("Skill added.")


def cmd_update(data):
    name, category = ask("Skill name"), input("New category (blank = keep): ").strip() or None
    target = input("New target (blank = keep): ").strip()
    update_skill(data, name, category, int(target) if target else None)
    print("Skill updated.")


def cmd_filter(data):
    category = input("Category (blank = all): ").strip() or None
    choice = ask("1) All  2) Achieved  3) In progress", int)
    show(filter_rows(data, category, {1: None, 2: True, 3: False}.get(choice)))


def cmd_settings(data):
    set_settings(data, ask("Hours per level", float), ask("Max level", int))
    print("Settings updated.")


def cmd_summary(data):
    for key, value in summary(data).items():
        print(f"{key}: {value}")


def cmd_export_csv(data):
    from .skills import export_csv

    print("Saved", export_csv(data))


def cmd_export_pdf(data):
    print("Saved", export_pdf(data))


ACTIONS = {
    "1": ("Add skill", cmd_add),
    "2": ("Update skill", cmd_update),
    "3": ("Delete skill", lambda d: (delete_skill(d, ask("Skill name")), print("Skill deleted."))),
    "4": ("Track practice", lambda d: (track_skill(d, ask("Skill name"), ask("Hours practised", float)), print("Hours logged."))),
    "5": ("Filter skills", cmd_filter),
    "6": ("Summary", cmd_summary),
    "7": ("Export CSV", cmd_export_csv),
    "8": ("Export PDF", cmd_export_pdf),
    "9": ("Settings", cmd_settings),
}


def menu():
    from .store import load, save

    data = load()
    while True:
        print("\n=== SkillForge ===")
        for key, (label, _) in ACTIONS.items():
            print(f"{key}. {label}")
        print("0. Exit")
        try:
            choice = input("Choose: ").strip()
            if choice == "0":
                break
            if choice not in ACTIONS:
                print("Invalid option.")
                continue
            ACTIONS[choice][1](data)
            save(data)
        except (ValueError, OSError) as err:
            print(f"Error: {err}")
        except (EOFError, KeyboardInterrupt):
            break
    save(data)
    print("Data saved. Bye.")
