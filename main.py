"""
PawPal+ — Terminal testing ground.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def section(title: str) -> None:
    print()
    print("=" * 55)
    print(f"  {title}")
    print("=" * 55)


def main():
    # ── Setup owner ──────────────────────────────────────────
    owner = Owner(name="Alex", available_minutes=90)

    # ── Setup pets ───────────────────────────────────────────
    buddy = Pet(name="Buddy", breed="Labrador", age=3)
    luna = Pet(name="Luna", breed="Persian Cat", age=5, special_needs=["joint supplement"])

    owner.add_pet(buddy)
    owner.add_pet(luna)

    # ── Add tasks OUT OF ORDER (evening tasks added before morning) ──
    # Buddy's tasks
    buddy.add_task(Task("Evening Walk",      duration_minutes=30, priority=4, category="walk",       preferred_time="evening",  frequency="daily",  time="18:00"))
    buddy.add_task(Task("Morning Walk",      duration_minutes=30, priority=5, category="walk",       preferred_time="morning",  frequency="daily",  time="07:00"))
    buddy.add_task(Task("Breakfast Feeding", duration_minutes=10, priority=5, category="feeding",    preferred_time="morning",  frequency="daily",  time="07:30"))
    buddy.add_task(Task("Grooming Session",  duration_minutes=20, priority=2, category="grooming",   preferred_time="anytime"))

    # Luna's tasks
    luna.add_task(Task("Playtime",           duration_minutes=15, priority=3, category="enrichment", preferred_time="evening",  time="18:00"))  # same time as Buddy's Evening Walk!
    luna.add_task(Task("Breakfast Feeding",  duration_minutes=10, priority=5, category="feeding",    preferred_time="morning",  frequency="daily",  time="07:30"))  # same time as Buddy!
    luna.add_task(Task("Joint Supplement",   duration_minutes=5,  priority=5, category="medication", preferred_time="morning",  frequency="weekly", time="08:00"))
    luna.add_task(Task("Litter Box Clean",   duration_minutes=10, priority=4, category="hygiene",    preferred_time="anytime"))

    scheduler = Scheduler(owner)

    # ── 1. Today's plan (original priority-based) ────────────
    section("PawPal+  —  Today's Schedule")
    plan = scheduler.generate_plan()
    print(scheduler.explain_plan(plan))

    # ── 2. Sort all tasks by time of day ─────────────────────
    section("All Tasks Sorted by Time of Day")
    all_tasks = owner.get_all_tasks()
    sorted_by_time = scheduler.sort_by_time(all_tasks)
    for task in sorted_by_time:
        pet_label = f"[{task.pet_name}]" if task.pet_name else ""
        print(f"  {pet_label:8s} {task}")

    # ── 3. Filter by pet name ─────────────────────────────────
    section("Filter: Luna's Tasks Only")
    luna_tasks = scheduler.filter_tasks(pet_name="Luna")
    for task in luna_tasks:
        print(f"  {task}")

    # ── 4. Mark a daily task complete & auto-create next occurrence ──
    section("Recurring Task — Mark Complete & Auto-Schedule Next")
    morning_walk = buddy.tasks[1]  # "Morning Walk" (daily)
    print(f"  Before: {morning_walk}")
    next_walk = scheduler.mark_task_complete(morning_walk, buddy)
    print(f"  After:  {morning_walk}")
    if next_walk:
        print(f"  Next:   {next_walk}  (due {next_walk.due_date})")

    # ── 5. Filter pending vs completed ───────────────────────
    section("Filter: Pending Tasks (all pets)")
    pending = scheduler.filter_tasks(completed=False)
    for task in pending:
        print(f"  [{task.pet_name:5s}] {task}")

    section("Filter: Completed Tasks (all pets)")
    done = scheduler.filter_tasks(completed=True)
    for task in done:
        print(f"  [{task.pet_name:5s}] {task}")

    # ── 6. Conflict detection ─────────────────────────────────
    section("Conflict Detection")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No scheduling conflicts detected.")

    print()
    print("=" * 55)
    print(f"  Pets: {', '.join(p.name for p in owner.pets)}")
    print(f"  Total tasks: {len(owner.get_all_tasks())}  |  Scheduled today: {len(plan)}")
    print("=" * 55)


if __name__ == "__main__":
    main()
