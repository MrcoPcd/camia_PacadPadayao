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

# -----------------
# HOME PAGE
# -----------------
@app.route("/")
def home():
    return render_template("index.html", tasks=tasks)

# -----------------
# ADD TASK
# -----------------
@app.route("/add_task", methods=["POST"])
def add_task():
    grade = request.form.get("grade", "Not Set")
    subject = request.form.get("subject", "General")
    category = request.form.get("category", "General")
    timer_value = request.form.get("timer")

    duration = int(timer_value) * 60 if timer_value and timer_value != "None" else 0

    tasks.append({
        "task": "Task",
        "grade": grade,
        "subject": subject,
        "category": category,
        "done": False,
        "remaining_time": duration,
        "running": False,           
        "last_updated": None        
    })
    return redirect("/")


# -----------------
# COMPLETE TASK
# -----------------
@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    if task_id < len(tasks):
        tasks[task_id]["done"] = True
        completed_tasks.append(tasks[task_id])
        tasks.remove(tasks[task_id])
        return redirect("/")
    return "Task not found"

# -----------------
# DELETE TASK
# -----------------
@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    tasks.remove(tasks[task_id])
    return redirect("/")

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
# TIMER
# -----------------
@app.route("/timer/<int:task_id>/<action>")
def control_timer(task_id, action):
    if 0 <= task_id < len(tasks):
        task = tasks[task_id]
        if action == "start":
            task["running"] = True
            task["last_updated"] = time.time()
        elif action == "pause":
            # Update the remaining time one last time before stopping
            get_remaining_seconds(task) 
            task["running"] = False
        elif action == "stop":
            task["running"] = False
            task["remaining_time"] = 0
    return redirect("/")

def get_remaining_seconds(task):
    if task.get("running") and task["remaining_time"] > 0:
        now = time.time()
        elapsed = now - task["last_updated"]
        
        task["remaining_time"] = max(0, task["remaining_time"] - elapsed)
        
        task["last_updated"] = now
        
    return int(task["remaining_time"])


# -----------------
# TIMER API (JSON)
# -----------------
def calculate_remaining(task):
    """Calculates seconds left and updates the last_updated anchor."""
    if task.get("running") and task["remaining_time"] > 0:
        now = time.time()
        # If it was just started, initialize the anchor
        if task["last_updated"] is None:
            task["last_updated"] = now
            
        elapsed = now - task["last_updated"]
        task["remaining_time"] = max(0, task["remaining_time"] - elapsed)
        task["last_updated"] = now
        
    return int(task["remaining_time"])

@app.route("/get_task_timers")
def get_timers_api():
    """This is the ONLY function that should be named for the API route."""
    results = []
    for task in tasks:
        rem = calculate_remaining(task)
        minutes = rem // 60
        seconds = rem % 60
        results.append(f"{minutes:02d}:{seconds:02d}")
    
    # Flask needs us to return this as a JSON list for the JavaScript to read it
    from flask import jsonify
    return jsonify(results)

# -----------------
# RUN SERVER
# -----------------
if __name__ == "__main__":
    app.run(debug=True)
