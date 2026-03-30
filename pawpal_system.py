"""
PawPal+ Logic Layer
Backend classes for pet care scheduling.
"""


class Task:
    """Represents a single pet care activity with duration, priority, and completion state."""

    def __init__(self, name: str, duration_minutes: int, priority: int, category: str, preferred_time: str = "anytime"):
        self.name = name
        self.duration_minutes = duration_minutes
        self.priority = priority          # 1 (low) to 5 (high)
        self.category = category          # e.g. "walk", "feeding", "medication"
        self.preferred_time = preferred_time  # e.g. "morning", "evening", "anytime"
        self.completed = False

    def get_priority_score(self) -> int:
        """Return the numeric priority of this task."""
        return self.priority

    def is_schedulable(self, available_minutes: int) -> bool:
        """Return True if this task's duration fits within the given available minutes."""
        return self.duration_minutes <= available_minutes

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def __repr__(self) -> str:
        """Return a readable string representation of the task."""
        status = "done" if self.completed else "pending"
        return f"[{self.preferred_time}] {self.name} ({self.duration_minutes} min, priority {self.priority}) [{status}]"


class Pet:
    """Stores a pet's profile and the list of care tasks assigned to it."""

    def __init__(self, name: str, breed: str, age: int, special_needs: list = None):
        self.name = name
        self.breed = breed
        self.age = age
        self.special_needs = special_needs or []
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks associated with this pet."""
        return self.tasks


class Owner:
    """Manages one or more pets and tracks daily time available for pet care."""

    def __init__(self, name: str, available_minutes: int, preferences: list = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_available_time(self) -> int:
        """Return total daily minutes the owner has available for pet care."""
        return self.available_minutes

    def get_all_tasks(self) -> list[Task]:
        """Return a combined list of every task across all owned pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """Generates a prioritized daily care plan that fits within the owner's available time."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.total_minutes: int = owner.available_minutes

    def filter_by_time(self, minutes: int) -> list[Task]:
        """Return tasks from all pets whose duration fits within the given minutes."""
        return [t for t in self.owner.get_all_tasks() if t.is_schedulable(minutes)]

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted from highest to lowest priority score."""
        return sorted(tasks, key=lambda t: t.get_priority_score(), reverse=True)

    def generate_plan(self) -> list[Task]:
        """Build and return an ordered plan of tasks that fit within available time."""
        schedulable = self.filter_by_time(self.total_minutes)
        sorted_tasks = self.sort_by_priority(schedulable)

        plan = []
        remaining = self.total_minutes
        for task in sorted_tasks:
            if task.duration_minutes <= remaining:
                plan.append(task)
                remaining -= task.duration_minutes
        return plan

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a plain-English explanation of why the plan was chosen."""
        if not plan:
            return "No tasks could be scheduled within the available time."

        total_scheduled = sum(t.duration_minutes for t in plan)
        lines = [
            f"Plan for {self.owner.name} ({self.total_minutes} min available, {total_scheduled} min scheduled):",
            ""
        ]
        for i, task in enumerate(plan, 1):
            lines.append(f"  {i}. {task.name} — {task.duration_minutes} min | priority {task.priority} | {task.preferred_time}")

        skipped = [t for t in self.owner.get_all_tasks() if t not in plan]
        if skipped:
            lines.append("")
            lines.append("Skipped (insufficient time):")
            for task in skipped:
                lines.append(f"  - {task.name} ({task.duration_minutes} min)")

        return "\n".join(lines)
