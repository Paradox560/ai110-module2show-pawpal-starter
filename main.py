"""
PawPal+ — Terminal testing ground.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # --- Setup owner ---
    owner = Owner(name="Alex", available_minutes=90)

    # --- Setup pets ---
    buddy = Pet(name="Buddy", breed="Labrador", age=3)
    luna = Pet(name="Luna", breed="Persian Cat", age=5, special_needs=["joint supplement"])

    owner.add_pet(buddy)
    owner.add_pet(luna)

    # --- Add tasks to Buddy ---
    buddy.add_task(Task("Morning Walk",      duration_minutes=30, priority=5, category="walk",      preferred_time="morning"))
    buddy.add_task(Task("Breakfast Feeding", duration_minutes=10, priority=5, category="feeding",   preferred_time="morning"))
    buddy.add_task(Task("Evening Walk",      duration_minutes=30, priority=4, category="walk",      preferred_time="evening"))
    buddy.add_task(Task("Grooming Session",  duration_minutes=20, priority=2, category="grooming",  preferred_time="anytime"))

    # --- Add tasks to Luna ---
    luna.add_task(Task("Breakfast Feeding",  duration_minutes=10, priority=5, category="feeding",   preferred_time="morning"))
    luna.add_task(Task("Joint Supplement",   duration_minutes=5,  priority=5, category="medication",preferred_time="morning"))
    luna.add_task(Task("Playtime",           duration_minutes=15, priority=3, category="enrichment",preferred_time="evening"))
    luna.add_task(Task("Litter Box Clean",   duration_minutes=10, priority=4, category="hygiene",   preferred_time="anytime"))

    # --- Generate plan ---
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    # --- Print Today's Schedule ---
    print("=" * 50)
    print("        🐾  PawPal+ — Today's Schedule  🐾")
    print("=" * 50)
    print()
    print(scheduler.explain_plan(plan))
    print()
    print("=" * 50)
    print(f"Pets: {', '.join(p.name for p in owner.pets)}")
    print(f"Total tasks across all pets: {len(owner.get_all_tasks())}")
    print(f"Tasks scheduled today: {len(plan)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
