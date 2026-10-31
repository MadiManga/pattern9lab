from dataclasses import dataclass
from itertools import count

# ==========================================
# STATE PATTERN
# ==========================================

class TaskState:
    name = "Unknown"

    def complete(self, task):
        raise ValueError(
            f"Cannot complete a task in the {self.name} state."
        )

    def reopen(self, task):
        raise ValueError(
            f"Cannot reopen a task in the {self.name} state."
        )


class PendingState(TaskState):
    name = "Pending"

    def complete(self, task):
        task.state = CompletedState()


class CompletedState(TaskState):
    name = "Completed"

    def reopen(self, task):
        task.state = PendingState()


# ==========================================
# MEMENTO PATTERN
# ==========================================

@dataclass
class TaskMemento:

    title: str
    state_name: str


# ==========================================
# TASK MODEL
# ==========================================

@dataclass
class Task:

    id: int
    title: str
    state: TaskState

    @property
    def status(self):

        return self.state.name

    def save(self):
        return TaskMemento(
            title=self.title,
            state_name=self.status,
        )

    def restore(self, memento: TaskMemento):
        self.title = memento.title

        if memento.state_name == "Pending":
            self.state = PendingState()

        elif memento.state_name == "Completed":
            self.state = CompletedState()

        else:
            raise ValueError("Unknown task state in memento.")


# ==========================================
# OBSERVER PATTERN
# ==========================================

class Observer:
    def update(self, message: str):
        raise NotImplementedError


class NotificationObserver(Observer):
    def __init__(self):
        self.messages = []

    def update(self, message: str):
        self.messages.append(message)


# ==========================================
# TASK MANAGER
# ==========================================

class TaskManager:
    def __init__(self):
        self.tasks = []
        self._ids = count(1)
        self._observers = []
        self._history = {}

    # Observer subscription

    def subscribe(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, message: str):
        for observer in list(self._observers):
            observer.update(message)

    # Task operations

    def add_task(self, title: str):
        title = title.strip()

        if not title:
            raise ValueError("Task title is required.")

        if len(title) > 100:
            raise ValueError(
                "Task title must be 100 characters or fewer."
            )

        task = Task(
            id=next(self._ids),
            title=title,
            state=PendingState(),
        )

        self.tasks.append(task)
        self._history[task.id] = []

        self.notify(
            f'Task #{task.id} "{task.title}" was created.'
        )

        return task

    def find_task(self, task_id: int):
        return next(
            (
                task
                for task in self.tasks
                if task.id == task_id
            ),
            None,
        )

    # Memento: save before changing the task

    def _save_before_change(self, task):
        self._history.setdefault(task.id, []).append(
            task.save()
        )

    # State: complete a pending task

    def complete_task(self, task_id: int):
        task = self.find_task(task_id)

        if task is None:
            raise ValueError("Task not found.")

        if task.status != "Pending":
            raise ValueError(
                "Only pending tasks can be completed."
            )

        self._save_before_change(task)
        task.state.complete(task)

        self.notify(
            f'Task #{task.id} "{task.title}" was completed.'
        )

        return task

    # State: reopen a completed task

    def reopen_task(self, task_id: int):
        task = self.find_task(task_id)

        if task is None:
            raise ValueError("Task not found.")

        if task.status != "Completed":
            raise ValueError(
                "Only completed tasks can be reopened."
            )

        self._save_before_change(task)
        task.state.reopen(task)

        self.notify(
            f'Task #{task.id} "{task.title}" was reopened.'
        )

        return task

    # Memento: restore the last saved state

    def undo(self, task_id: int):
        task = self.find_task(task_id)

        if task is None:
            raise ValueError("Task not found.")

        history = self._history.get(task_id, [])

        if not history:
            raise ValueError(
                "There is no previous state to restore."
            )

        memento = history.pop()
        task.restore(memento)

        self.notify(
            f"Task #{task.id} was restored to {task.status}."
        )

        return task


# ==========================================
# STRATEGY PATTERN
# ==========================================

class SortStrategy:
    def sort(self, tasks):
        raise NotImplementedError


class SortById(SortStrategy):
    def sort(self, tasks):
        return sorted(
            tasks,
            key=lambda task: task.id,
        )


class SortByTitle(SortStrategy):
    def sort(self, tasks):
        return sorted(
            tasks,
            key=lambda task: task.title.casefold(),
        )


class SortByStatus(SortStrategy):
    def sort(self, tasks):
        return sorted(
            tasks,
            key=lambda task: (
                task.status != "Pending",
                task.id,
            ),
        )


class TaskSorter:
    STRATEGIES = {
        "id": SortById(),
        "title": SortByTitle(),
        "status": SortByStatus(),
    }

    @classmethod
    def sort(cls, tasks, strategy_name="id"):

        strategy = cls.STRATEGIES.get(
            strategy_name,
            cls.STRATEGIES["id"],
        )

        return strategy.sort(tasks)
