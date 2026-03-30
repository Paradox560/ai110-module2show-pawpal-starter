# PawPal+ Project Reflection

## 1. System Design

**Three core user actions:**

1. **Add a pet and owner info** — The user enters their name, daily time available, and preferences, then registers their pet (name, breed, age, special needs).
2. **Add and edit care tasks** — The user creates tasks like walks, feeding, or medication, each with a duration and priority level.
3. **Generate a daily plan** — The user requests a scheduled plan; the system fits tasks into available time slots ranked by priority and explains the reasoning.

**Mermaid.js Class Diagram:**

```mermaid
classDiagram
    class Owner {
        +str name
        +int available_minutes
        +list preferences
        +Pet pet
        +add_pet(pet: Pet)
        +get_available_time() int
    }

    class Pet {
        +str name
        +str breed
        +int age
        +list special_needs
        +list tasks
        +add_task(task: Task)
        +get_tasks() list
    }

    class Task {
        +str name
        +int duration_minutes
        +int priority
        +str category
        +str preferred_time
        +get_priority_score() int
        +is_schedulable(available: int) bool
    }

    class Scheduler {
        +Owner owner
        +list tasks
        +int total_minutes
        +generate_plan() list
        +filter_by_time(minutes: int) list
        +sort_by_priority(tasks: list) list
        +explain_plan(plan: list) str
    }

    Owner "1" --> "1" Pet : owns
    Pet "1" --> "*" Task : has
    Scheduler "1" --> "1" Owner : uses
    Scheduler "1" --> "*" Task : schedules
```

**a. Initial design**

The system is built around four classes:

- **Task** — the atomic unit of the app. It holds a task's name, duration, priority (1–5), category (walk/feeding/medication/etc.), and a preferred time of day. It knows whether it fits in a given time window (`is_schedulable`) and can report its priority score.
- **Pet** — stores the pet's profile (name, breed, age, special needs) and owns the list of associated `Task` objects. It is responsible for managing task membership.
- **Owner** — stores the owner's name, total daily minutes available, and personal preferences. It holds a reference to one `Pet` and exposes the available time for the scheduler to consume.
- **Scheduler** — the core logic class. It takes an `Owner` (and by extension the pet's tasks), filters tasks that fit within available time, sorts by priority, builds the final daily plan, and generates a plain-English explanation of its choices.

The relationship chain is: `Owner` → `Pet` → `Task`s, with `Scheduler` orchestrating the plan generation using `Owner` as its entry point.

**b. Design changes**

Yes — one change was made after reviewing the design for bottlenecks.

**Change:** The `Scheduler` originally held its own `tasks` list as an attribute, separate from `Pet.tasks`. This would create a sync problem: tasks added to the `Pet` after the `Scheduler` was constructed would not be visible to the plan generator.

**Fix:** Removed the duplicate `tasks` attribute from `Scheduler`. Instead, `generate_plan` (and related methods) will source tasks directly from `owner.pet.get_tasks()` at call time. This ensures the scheduler always works from the current state of the pet's task list without requiring manual re-syncing.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
