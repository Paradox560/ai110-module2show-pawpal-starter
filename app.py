import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state init — runs once per session; survives reruns (step 2)
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

if "pets" not in st.session_state:
    st.session_state.pets = {}   # name -> Pet

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
    st.success(f"Saved! Owner: {owner_name} | Pet: {pet_name} ({breed}, age {age}) | {available_minutes} min/day")

st.divider()

# ---------------------------------------------------------------------------
# Add tasks (step 3 — calls Pet.add_task with real Task objects)
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
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        category = st.selectbox("Category", ["walk", "feeding", "medication", "grooming", "enrichment", "hygiene"])
    with col3:
        priority = st.slider("Priority (1 = low, 5 = high)", min_value=1, max_value=5, value=3)
        preferred_time = st.selectbox("Preferred time", ["morning", "afternoon", "evening", "anytime"])

    if st.button("Add Task"):
        pet = st.session_state.pets[selected_pet]
        task = Task(
            name=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
            preferred_time=preferred_time,
        )
        pet.add_task(task)
        st.success(f"Added '{task_title}' to {selected_pet}.")

    # Show current tasks for all pets
    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.markdown("**Current tasks:**")
        rows = [
            {
                "Pet": next(p.name for p in st.session_state.owner.pets if task in p.tasks),
                "Task": t.name,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Category": t.category,
                "Time": t.preferred_time,
            }
            for t in all_tasks
            for task in [t]  # alias
        ]
        st.table(rows)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Generate schedule (step 3 — calls Scheduler.generate_plan + explain_plan)
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
            plan = scheduler.generate_plan()
            explanation = scheduler.explain_plan(plan)

            st.success("Schedule generated!")
            st.text(explanation)

            if plan:
                st.markdown("**Mark tasks complete:**")
                for task in plan:
                    if st.checkbox(f"{task.name} ({task.duration_minutes} min)", key=task.name):
                        task.mark_complete()
