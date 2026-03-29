"""
PawPal+ Logic Layer
Backend classes for pet care scheduling.
"""


class Task:
    """Represents a single pet care task (walk, feeding, medication, etc.)."""

    def __init__(self, name: str, duration_minutes: int, priority: int, category: str, preferred_time: str = "anytime"):
        self.name = name
        self.duration_minutes = duration_minutes
        self.priority = priority          # 1 (low) to 5 (high)
        self.category = category          # e.g. "walk", "feeding", "medication"
        self.preferred_time = preferred_time  # e.g. "morning", "evening", "anytime"

    def get_priority_score(self) -> int:
        """Return the numeric priority of this task."""
        pass

    def is_schedulable(self, available_minutes: int) -> bool:
        """Return True if this task fits within the given available time."""
        pass


class Pet:
    """Represents the pet being cared for."""

    def __init__(self, name: str, breed: str, age: int, special_needs: list = None):
        self.name = name
        self.breed = breed
        self.age = age
        self.special_needs = special_needs or []
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        pass

    def get_tasks(self) -> list[Task]:
        """Return all tasks associated with this pet."""
        pass


class Owner:
    """Represents the pet owner with their availability and preferences."""

    def __init__(self, name: str, available_minutes: int, preferences: list = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or []
        self.pet: Pet = None

    def add_pet(self, pet: Pet) -> None:
        """Register a pet for this owner."""
        pass

    def get_available_time(self) -> int:
        """Return total daily minutes the owner has available for pet care."""
        pass


class Scheduler:
    """Generates a daily care plan based on owner availability and task priorities."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: list[Task] = []
        self.total_minutes: int = owner.available_minutes

    def generate_plan(self) -> list[Task]:
        """Build and return an ordered list of tasks that fit within available time."""
        pass

    def filter_by_time(self, minutes: int) -> list[Task]:
        """Return only tasks whose duration fits within the given minutes."""
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted from highest to lowest priority."""
        pass

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a human-readable explanation of why the plan was chosen."""
        pass
