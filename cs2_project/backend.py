from flask import Flask, render_template, request, redirect
import time

app = Flask(__name__)

# -----------------
# DATA STORAGE
# -----------------
tasks = []
completed_tasks = []

# -----------------
# TIMER SETTINGS
# -----------------
timer_end_time = None
timer_mode = "focus"

timer_paused = False
timer_mode= "focus"

FOCUS_TIME = request.form.get("timer") * 60

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
    task = "Task"
    grade = request.form.get("grade", "Not Set")
    subject = request.form.get("subject", "General")
    category = request.form.get("category", "General")

    tasks.append({
    "task": task,
    "grade": grade,
    "subject": subject,
    "category": category,
    "done": False
})
    return redirect("/")

# -----------------
# VIEW TASKS
# -----------------
@app.route("/tasks")
def view_tasks():
    output = "<h2>Tasks</h2>"

    if tasks == []:
         output += "◎ None so far :D<br>"
    else:
        for i, task in enumerate(tasks):
            output += f"◎ (Grade {task['grade']}) [{task['subject']}] ({task['category']}) {task['task']} - Not Done <a href='/complete/{i}'>[Complete]</a> <a href='/delete/{i}'>[Delete]</a><br>"

    output += "<br><a href='/'>Back to Home</a>"
    return output

# -----------------
# COMPLETE TASK
# -----------------
@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    if task_id < len(tasks):
        tasks[task_id]["done"] = True
        completed_tasks.append(tasks[task_id])
        tasks.remove(tasks[task_id])
        return redirect("/tasks")
    return "Task not found"

# -----------------
# DELETE TASK
# -----------------
@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    tasks.remove(tasks[task_id])
    return redirect("/tasks")

# -----------------
# UNDO COMPLETION OF TASK
# -----------------
@app.route("/undo/<int:task_id>")
def undo_completion(task_id):
    completed_tasks[task_id]["done"] = False
    tasks.append(completed_tasks[task_id])
    completed_tasks.remove(completed_tasks[task_id])
    return redirect("/progress")

# -----------------
# PROGRESS TRACKER
# -----------------
@app.route("/progress")
def progress():
    if len(tasks) == 0 and len(completed_tasks) == 0:
        return "No tasks yet.<br><br><a href='/'>Back Home</a>"

    completed = len(completed_tasks)
    unfinished_tasks = len(tasks)
    total = len(tasks) + len(completed_tasks)
    percent = (completed / total) * 100
    completedtasks = ""

    if completed_tasks == []:
        completedtasks = "◎ None so far >:(<br>"
    else:
        for i, task in enumerate(completed_tasks):
            completedtasks += f"◎ (Grade {task['grade']}) [{task['subject']}] ({task['category']}) {task['task']} - Done <a href='/undo/{i}'>[Undo]</a>"

    return f"""
    <h2>Progress Tracker</h2>
    Tasks needed to be done: {unfinished_tasks}<br>
    Completed Tasks: {completed}<br>
    Total Tasks: {total}<br>
    Progress: {percent:.1f}% complete<br><br>

    Your Completed Tasks:<br>
    {completedtasks}<br>
    <a href="/">Back Home</a>
    """

# -----------------
# START TIMER
# -----------------
@app.route("/start_timer")
def start_timer():
    global timer_end_time, timer_mode, timer_paused

    timer_mode = "focus"
    timer_paused = False
    timer_end_time = time.time() + FOCUS_TIME

    return "Timer started"

# -----------------
# PAUSE TIMER
# -----------------
@app.route("/pause_timer")
def pause_timer():
    global timer_end_time, timer_paused, pause_remaining

    if timer_end_time:
        pause_remaining = int(timer_end_time - time.time())
        timer_paused = True

    return "Paused"

# -----------------
# RESUME TIMER
# -----------------
@app.route("/resume_timer")
def resume_timer():
    global timer_end_time, timer_paused, pause_remaining

    if timer_paused:
        timer_end_time = time.time() + pause_remaining
        timer_paused = False

    return "Resumed"

# -----------------
# RESET TIMER
# -----------------
@app.route("/reset_timer")
def reset_timer():
    global timer_end_time, timer_mode, timer_paused

    timer_mode = "focus"
    timer_paused = False
    timer_end_time = None

    return "Reset"


# -----------------
# TIMER API (JSON)
# -----------------
@app.route("/timer")
def timer_status():
    global timer_end_time, timer_mode

    if timer_end_time is None:
        return {"time": "00:00", "mode": "Not started"}

    if timer_paused:
        remaining = pause_remaining
    else:
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
