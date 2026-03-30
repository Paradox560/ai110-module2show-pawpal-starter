import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
DATA_FILE = "data.json"


def _save():
    """Persist current owner state to disk."""
    if st.session_state.owner:
        st.session_state.owner.save_to_json(DATA_FILE)


if "owner" not in st.session_state:
    loaded = Owner.load_from_json(DATA_FILE)
    st.session_state.owner = loaded
    st.session_state.pets = {p.name: p for p in loaded.pets} if loaded else {}

# ---------------------------------------------------------------------------
# Owner + pet setup
# ---------------------------------------------------------------------------
st.subheader("Owner & Pet Setup")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Daily time available (minutes)", min_value=10, max_value=480, value=90, step=10)
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    breed = st.text_input("Breed", value="Labrador")
    age = st.number_input("Pet age", min_value=0, max_value=30, value=3)

if st.button("Save Owner & Pet"):
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    pet = Pet(name=pet_name, breed=breed, age=int(age))
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pets = {pet_name: pet}
    _save()
    st.success(f"Saved! Owner: {owner_name} | Pet: {pet_name} ({breed}, age {age}) | {available_minutes} min/day")

st.divider()

# ---------------------------------------------------------------------------
# Add tasks
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

if st.session_state.owner is None:
    st.info("Save an owner and pet above before adding tasks.")
else:
    pet_options = list(st.session_state.pets.keys())
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        selected_pet = st.selectbox("Assign to pet", pet_options)
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        category = st.selectbox("Category", ["walk", "feeding", "medication", "grooming", "enrichment", "hygiene"])
    with col3:
        priority = st.slider("Priority (1 = low, 5 = high)", min_value=1, max_value=5, value=3)
        preferred_time = st.selectbox("Preferred time", ["morning", "afternoon", "evening", "anytime"])
        exact_time = st.text_input("Exact time (HH:MM, optional)", value="", placeholder="e.g. 08:00")

    if st.button("Add Task"):
        pet = st.session_state.pets[selected_pet]
        task = Task(
            name=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
            preferred_time=preferred_time,
            frequency=frequency,
            time=exact_time.strip() if exact_time.strip() else None,
        )
        pet.add_task(task)
        _save()
        st.success(f"Added '{task_title}' to {selected_pet}.")

    # Show current tasks sorted by priority then time of day
    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        scheduler = Scheduler(st.session_state.owner)
        sorted_tasks = scheduler.sort_by_priority_then_time(all_tasks)
        st.markdown("**Current tasks (priority → time of day):**")
        rows = [
            {
                "Priority": f"{t.priority_emoji} {t.priority_label}",
                "Pet": t.pet_name or "—",
                "Task": t.name,
                "Time": (t.time if t.time else t.preferred_time),
                "Duration (min)": t.duration_minutes,
                "Category": t.category,
                "Frequency": t.frequency,
                "Done": "✓" if t.completed else "",
            }
            for t in sorted_tasks
        ]
        st.table(rows)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------
st.subheader("Generate Daily Schedule")

if st.session_state.owner is None:
    st.info("Set up an owner and add tasks first.")
else:
    if st.button("Generate Schedule"):
        owner = st.session_state.owner
        if not owner.get_all_tasks():
            st.warning("No tasks to schedule. Add some tasks above.")
        else:
            scheduler = Scheduler(owner)

            # ── Conflict warnings ────────────────────────────────
            conflicts = scheduler.detect_conflicts()
            if conflicts:
                st.markdown("**⚠️ Scheduling Conflicts Detected**")
                for msg in conflicts:
                    st.warning(msg)

            # ── Generate and display plan ────────────────────────
            plan = scheduler.generate_plan()
            if not plan:
                st.warning("No tasks fit within the available time.")
            else:
                st.success(f"Schedule ready — {sum(t.duration_minutes for t in plan)} of {owner.available_minutes} minutes used.")

                # Sort plan by priority then time of day for display
                sorted_plan = scheduler.sort_by_priority_then_time(plan)
                plan_rows = [
                    {
                        "Priority": f"{t.priority_emoji} {t.priority_label}",
                        "Pet": t.pet_name or "—",
                        "Task": t.name,
                        "Time": (t.time if t.time else t.preferred_time),
                        "Duration (min)": t.duration_minutes,
                        "Frequency": t.frequency,
                    }
                    for t in sorted_plan
                ]
                st.table(plan_rows)

                # Skipped tasks
                skipped = [t for t in owner.get_all_tasks() if t not in plan and not t.completed]
                if skipped:
                    st.markdown("**Skipped (insufficient time):**")
                    for t in skipped:
                        st.caption(f"– {t.name} ({t.duration_minutes} min, priority {t.priority})")

                # ── Mark tasks complete ──────────────────────────
                st.markdown("**Mark tasks complete:**")
                for task in sorted_plan:
                    pet = owner.get_pet(task.pet_name)
                    checkbox_key = f"done_{task.name}_{task.pet_name}"
                    if not task.completed:
                        if st.checkbox(f"{task.name} — {task.pet_name} ({task.duration_minutes} min)", key=checkbox_key):
                            next_task = scheduler.mark_task_complete(task, pet)
                            _save()
                            if next_task:
                                st.info(f"'{task.name}' marked done. Next occurrence scheduled for {next_task.due_date}.")
                            else:
                                st.info(f"'{task.name}' marked complete.")
                    else:
                        st.success(f"✓ {task.name} — {task.pet_name} (complete)")

st.divider()

# ---------------------------------------------------------------------------
# Filter view
# ---------------------------------------------------------------------------
st.subheader("Filter Tasks")

if st.session_state.owner is None:
    st.info("Set up an owner and add tasks first.")
else:
    owner = st.session_state.owner
    scheduler = Scheduler(owner)

    col1, col2 = st.columns(2)
    with col1:
        filter_status = st.selectbox("Completion status", ["All", "Pending", "Completed"])
    with col2:
        pet_filter_options = ["All"] + list(st.session_state.pets.keys())
        filter_pet = st.selectbox("Pet", pet_filter_options)

    completed_arg = None
    if filter_status == "Pending":
        completed_arg = False
    elif filter_status == "Completed":
        completed_arg = True

    pet_arg = None if filter_pet == "All" else filter_pet

    filtered = scheduler.filter_tasks(completed=completed_arg, pet_name=pet_arg)
    filtered_sorted = scheduler.sort_by_priority_then_time(filtered)

    if filtered_sorted:
        rows = [
            {
                "Priority": f"{t.priority_emoji} {t.priority_label}",
                "Pet": t.pet_name or "—",
                "Task": t.name,
                "Time": (t.time if t.time else t.preferred_time),
                "Duration (min)": t.duration_minutes,
                "Frequency": t.frequency,
                "Done": "✓" if t.completed else "",
            }
            for t in filtered_sorted
        ]
        st.table(rows)
    else:
        st.info("No tasks match the selected filters.")
