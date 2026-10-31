# Smart Task Manager

Laboratory Work 9 - Behavioral Design Patterns (Memento, Observer, State, Strategy) in a Flask web app.

## Run

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. Tasks and history are stored in memory and reset when the server restarts.

## Files

- `task_patterns.py` - State, Memento, Observer and Strategy patterns plus `TaskManager`
- `app.py` - Flask routes
- `templates/index.html`, `static/style.css` - user interface
