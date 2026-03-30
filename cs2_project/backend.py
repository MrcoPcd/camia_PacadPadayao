from flask import Flask, render_template, request, redirect
import time

app = Flask(__name__)

# -----------------
# DATA STORAGE
# -----------------
tasks = []

# -----------------
# POMODORO SETTINGS
# -----------------
timer_end_time = None
timer_mode = "focus"

FOCUS_TIME = 25 * 60
BREAK_TIME = 5 * 60

# -----------------
# HOME PAGE
# -----------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------
# ADD TASK
# -----------------
@app.route("/add_task", methods=["POST"])
def add_task():
    task = request.form["task"]
    tasks.append({"task": task, "done": False})
    return redirect("/")

# -----------------
# VIEW TASKS
# -----------------
@app.route("/tasks")
def view_tasks():
    output = "<h2>Tasks</h2>"

    for i, task in enumerate(tasks):
        status = "Done" if task["done"] else "Not Done"
        output += f"{i}. {task['task']} - {status} <a href='/complete/{i}'>[Complete]</a><br>"

    output += "<br><a href='/'>Back to Home</a>"
    return output

# -----------------
# COMPLETE TASK
# -----------------
@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    if task_id < len(tasks):
        tasks[task_id]["done"] = True
        return redirect("/tasks")
    return "Task not found"

# -----------------
# PROGRESS TRACKER
# -----------------
@app.route("/progress")
def progress():
    if len(tasks) == 0:
        return "No tasks yet.<br><br><a href='/'>Back Home</a>"

    completed = sum(1 for task in tasks if task["done"])
    total = len(tasks)
    percent = (completed / total) * 100

    return f"""
    <h2>Progress Tracker</h2>
    Completed Tasks: {completed}<br>
    Total Tasks: {total}<br>
    Progress: {percent:.1f}% complete<br><br>
    <a href="/">Back Home</a>
    """

# -----------------
# START TIMER
# -----------------
@app.route("/start_timer")
def start_timer():
    global timer_end_time, timer_mode
    timer_mode = "focus"
    timer_end_time = time.time() + FOCUS_TIME
    return "Timer started!<br><br><a href='/'>Back Home</a>"

# -----------------
# TIMER API (JSON)
# -----------------
@app.route("/timer")
def timer_status():
    global timer_end_time, timer_mode

    if timer_end_time is None:
        return {"time": "00:00", "mode": "Not started"}

    remaining = int(timer_end_time - time.time())

    # AUTO SWITCH
    if remaining <= 0:
        if timer_mode == "focus":
            timer_mode = "break"
            timer_end_time = time.time() + BREAK_TIME
        else:
            timer_mode = "focus"
            timer_end_time = time.time() + FOCUS_TIME

        remaining = int(timer_end_time - time.time())

    minutes = remaining // 60
    seconds = remaining % 60

    return {
        "time": f"{minutes:02d}:{seconds:02d}",
        "mode": timer_mode
    }

# -----------------
# RUN SERVER
# -----------------
if __name__ == "__main__":
    app.run(debug=True)