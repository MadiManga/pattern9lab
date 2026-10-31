from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from task_patterns import (
    NotificationObserver,
    TaskManager,
    TaskSorter,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "classroom-demo-key"

# Create the task manager and observer.

manager = TaskManager()
notification_observer = NotificationObserver()

manager.subscribe(notification_observer)

# Add sample tasks.

manager.add_task("Prepare laboratory materials")
manager.add_task("Study design patterns")
manager.add_task("Complete programming exercises")


@app.get("/")
def index():

    sort_by = request.args.get("sort", "id")

    tasks = TaskSorter.sort(
        manager.tasks,
        sort_by,
    )

    # Display the most recent notifications first.
    notifications = list(
        reversed(notification_observer.messages[-10:])
    )

    return render_template(
        "index.html",
        tasks=tasks,
        notifications=notifications,
        sort_by=sort_by,
    )


@app.post("/add")
def add_task():

    title = request.form.get("title", "")

    try:
        manager.add_task(title)
        flash("Task created successfully.", "success")

    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for("index"))


@app.post("/complete/<int:task_id>")
def complete_task(task_id):

    try:
        manager.complete_task(task_id)
        flash("Task completed successfully.", "success")

    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for("index"))


@app.post("/reopen/<int:task_id>")
def reopen_task(task_id):

    try:
        manager.reopen_task(task_id)
        flash("Task reopened successfully.", "success")

    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for("index"))


@app.post("/undo/<int:task_id>")
def undo_task(task_id):

    try:
        manager.undo(task_id)
        flash("Previous task state restored.", "success")

    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
