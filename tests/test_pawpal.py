"""
Tests for PawPal+ core logic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
