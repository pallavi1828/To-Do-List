from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

# -------- Task & ToDoList classes --------
class Task:
    def __init__(self, title, priority):
        self.title = title
        self.priority = priority
        self.completed = False
        self.date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.next = None

class ToDoList:
    def __init__(self):
        self.head = None
        self.history = []

    def add_task(self, title, priority):
        new_task = Task(title, priority)
        if not self.head or priority < self.head.priority:
            new_task.next = self.head
            self.head = new_task
        else:
            current = self.head
            while current.next and current.next.priority <= priority:
                current = current.next
            new_task.next = current.next
            current.next = new_task
        return f"✅ Task '{title}' added with priority {priority}."

    def display_tasks(self):
        if not self.head:
            return "🗒️ No tasks available."
        tasks_list = []
        current = self.head
        while current:
            status = "✅ Completed" if current.completed else "⏳ Pending"
            tasks_list.append(f"🔹 {current.title} | Priority: {current.priority} | Status: {status} | Added on: {current.date_added}")
            current = current.next
        return "\n".join(tasks_list)

    def mark_complete(self, title):
        current = self.head
        while current:
            if current.title == title:
                current.completed = True
                self.history.append((title, "completed", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                return f"✅ Task '{title}' marked as complete."
            current = current.next
        return f"⚠️ Task '{title}' not found."

    def delete_task(self, title):
        if not self.head:
            return "⚠️ No tasks to delete."

        if self.head.title == title:
            self.history.append((title, "deleted", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.head = self.head.next
            return f"🗑️ Task '{title}' deleted."

        current = self.head
        while current.next:
            if current.next.title == title:
                self.history.append((title, "deleted", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                current.next = current.next.next
                return f"🗑️ Task '{title}' deleted."
            current = current.next

        return f"⚠️ Task '{title}' not found."

    def show_history(self):
        if not self.history:
            return "📭 No task history yet."
        history_log = []
        for title, action, timestamp in self.history:
            emoji = "🗑️" if action == "deleted" else "✅"
            history_log.append(f"{emoji} {action.capitalize()} task '{title}' on {timestamp}")
        return "\n".join(history_log)

# -------- Flask App Setup --------
app = Flask(__name__)
CORS(app)
todo_list = ToDoList()

# -------- Routes --------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json["message"].lower()

    if "add task" in user_message:
        parts = user_message.split(":")
        if len(parts) == 3:
            title = parts[1].strip()
            try:
                priority = int(parts[2].strip())
                return jsonify({"reply": todo_list.add_task(title, priority)})
            except ValueError:
                return jsonify({"reply": "❌ Invalid priority. Please enter a number."})
        else:
            return jsonify({"reply": "✍️ Use format: 'Add task: Task Name: Priority (1-5)'"})

    elif "view tasks" in user_message or "show tasks" in user_message:
        return jsonify({"reply": todo_list.display_tasks()})

    elif "mark complete" in user_message:
        title = user_message.replace("mark complete ", "").strip()
        return jsonify({"reply": todo_list.mark_complete(title)})

    elif "delete task" in user_message:
        title = user_message.replace("delete task ", "").strip()
        return jsonify({"reply": todo_list.delete_task(title)})

    elif "history" in user_message or "show history" in user_message:
        return jsonify({"reply": todo_list.show_history()})

    elif "hello" in user_message:
        return jsonify({"reply": "👋 Hello! I’m your To-Do Bot. Try commands like:\n- Add task: Task: Priority\n- View tasks\n- Mark complete task\n- Delete task\n- Show history"})

    elif "bye" in user_message:
        return jsonify({"reply": "👋 Goodbye! Stay productive!"})

    else:
        return jsonify({"reply": "❓ I didn’t understand that. Try:\n- Add task: Homework: 1\n- View tasks\n- Delete task Homework\n- Show history"})

# -------- Run App --------
if __name__ == '__main__':
    app.run(debug=True)
