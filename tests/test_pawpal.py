"""
Tests for PawPal+ core logic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    """Verify that calling mark_complete() sets the task's completed flag to True."""
    task = Task(name="Morning Walk", duration_minutes=30, priority=5, category="walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Verify that adding a task to a Pet increases its task count by one."""
    pet = Pet(name="Buddy", breed="Labrador", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(name="Feeding", duration_minutes=10, priority=4, category="feeding"))
    assert len(pet.get_tasks()) == 1


def test_sort_by_time_chronological_order():
    """Verify tasks are returned in chronological order: morning → afternoon → evening → anytime."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Luna", breed="Beagle", age=2)
    owner.add_pet(pet)

    pet.add_task(Task(name="Evening Stroll", duration_minutes=20, priority=3, category="walk", preferred_time="evening"))
    pet.add_task(Task(name="Anytime Brush", duration_minutes=10, priority=2, category="grooming", preferred_time="anytime"))
    pet.add_task(Task(name="Morning Feed", duration_minutes=10, priority=5, category="feeding", preferred_time="morning"))
    pet.add_task(Task(name="Afternoon Meds", duration_minutes=5, priority=4, category="medication", preferred_time="afternoon"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time(owner.get_all_tasks())
    time_slots = [t.preferred_time for t in sorted_tasks]

    assert time_slots == ["morning", "afternoon", "evening", "anytime"]


def test_sort_by_time_priority_tiebreaker():
    """Within the same time slot, tasks should be ordered by priority descending."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Luna", breed="Beagle", age=2)
    owner.add_pet(pet)

    pet.add_task(Task(name="Low Priority Morning", duration_minutes=10, priority=1, category="grooming", preferred_time="morning"))
    pet.add_task(Task(name="High Priority Morning", duration_minutes=10, priority=5, category="feeding", preferred_time="morning"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time(owner.get_all_tasks())

    assert sorted_tasks[0].name == "High Priority Morning"
    assert sorted_tasks[1].name == "Low Priority Morning"


def test_daily_recurrence_creates_next_day_task():
    """Marking a daily task complete should create a new task scheduled for the following day."""
    today = date.today()
    owner = Owner(name="Sam", available_minutes=60)
    pet = Pet(name="Rex", breed="Poodle", age=4)
    owner.add_pet(pet)

    daily_task = Task(
        name="Daily Walk",
        duration_minutes=30,
        priority=4,
        category="walk",
        frequency="daily",
        due_date=today,
    )
    pet.add_task(daily_task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(daily_task, pet)

    assert daily_task.completed is True
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.name == "Daily Walk"
    assert next_task in pet.get_tasks()


def test_weekly_recurrence_creates_next_week_task():
    """Marking a weekly task complete should create a new task scheduled for the following week."""
    today = date.today()
    owner = Owner(name="Sam", available_minutes=60)
    pet = Pet(name="Rex", breed="Poodle", age=4)
    owner.add_pet(pet)

    weekly_task = Task(
        name="Weekly Bath",
        duration_minutes=45,
        priority=3,
        category="grooming",
        frequency="weekly",
        due_date=today,
    )
    pet.add_task(weekly_task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(weekly_task, pet)

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_once_task_returns_no_next_task():
    """Marking a one-time task complete should return None (no recurrence)."""
    owner = Owner(name="Sam", available_minutes=60)
    pet = Pet(name="Rex", breed="Poodle", age=4)
    owner.add_pet(pet)

    once_task = Task(name="Vet Visit", duration_minutes=60, priority=5, category="medical", frequency="once")
    pet.add_task(once_task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(once_task, pet)

    assert next_task is None


def test_detect_conflicts_flags_duplicate_times():
    """Verify that the Scheduler returns a warning when two tasks share the same time string."""
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Mochi", breed="Shiba Inu", age=1)
    owner.add_pet(pet)

    pet.add_task(Task(name="Morning Walk", duration_minutes=30, priority=5, category="walk", time="08:00"))
    pet.add_task(Task(name="Morning Feed", duration_minutes=10, priority=4, category="feeding", time="08:00"))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Morning Walk" in warnings[0] or "Morning Feed" in warnings[0]


def test_detect_conflicts_no_false_positives():
    """Verify that tasks at distinct times produce no conflict warnings."""
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Mochi", breed="Shiba Inu", age=1)
    owner.add_pet(pet)

    pet.add_task(Task(name="Morning Walk", duration_minutes=30, priority=5, category="walk", time="08:00"))
    pet.add_task(Task(name="Afternoon Feed", duration_minutes=10, priority=4, category="feeding", time="12:00"))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert warnings == []


def test_detect_conflicts_ignores_completed_tasks():
    """Completed tasks should not be considered in conflict detection."""
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Mochi", breed="Shiba Inu", age=1)
    owner.add_pet(pet)

    task1 = Task(name="Morning Walk", duration_minutes=30, priority=5, category="walk", time="08:00")
    task2 = Task(name="Morning Feed", duration_minutes=10, priority=4, category="feeding", time="08:00")
    task1.completed = True  # already done — should be excluded from conflict check
    pet.add_task(task1)
    pet.add_task(task2)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert warnings == []
