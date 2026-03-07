from flask import Flask

app = Flask(__name__)

# -----------------
# DATA STORAGE
# -----------------
tasks = []

timer_running = False


# -----------------
# HOME PAGE
# -----------------
@app.route("/")
def home():
    return """
    <h1>Study Productivity Tool</h1>

    <h2>To-Do List</h2>
    <p>Add task: /add/yourtask</p>
    <p>View tasks: /tasks</p>
    <p>Complete task: /complete/tasknumber</p>

    <h2>Pomodoro Timer</h2>
    <p>Start timer: /start_timer</p>
    <p>Check timer: /timer</p>

    <h2>Progress Tracker</h2>
    <p>View progress: /progress</p>
    """


# -----------------
# ADD TASK
# -----------------
@app.route("/add/<task>")
def add_task(task):
    tasks.append({"task": task, "done": False})
    return f"Task '{task}' added!"


# -----------------
# VIEW TASKS
# -----------------
@app.route("/tasks")
def view_tasks():
    output = "<h2>Tasks</h2>"

    for i, task in enumerate(tasks):
        status = "Done" if task["done"] else "Not Done"
        output += f"{i}. {task['task']} - {status}<br>"

    return output


# -----------------
# COMPLETE TASK
# -----------------
@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    if task_id < len(tasks):
        tasks[task_id]["done"] = True
        return "Task completed!"
    else:
        return "Task not found"


# -----------------
# PROGRESS TRACKER
# -----------------
@app.route("/progress")
def progress():
    if len(tasks) == 0:
        return "No tasks yet."

    completed = sum(1 for task in tasks if task["done"])
    total = len(tasks)

    percent = (completed / total) * 100

    return f"""
    <h2>Progress Tracker</h2>
    Completed Tasks: {completed}<br>
    Total Tasks: {total}<br>
    Progress: {percent:.1f}% complete
    """


# -----------------
# START TIMER
# -----------------
@app.route("/start_timer")
def start_timer():
    global timer_running
    timer_running = True
    return "Pomodoro timer started! (25 minutes)"


# -----------------
# TIMER STATUS
# -----------------
@app.route("/timer")
def timer_status():
    if timer_running:
        return "Timer is running"
    else:
        return "Timer is not running"


# -----------------
# RUN SERVER
# -----------------
if __name__ == "__main__":
    app.run(debug=True)