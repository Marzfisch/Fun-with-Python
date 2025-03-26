import os
import json
import webbrowser
import platform
import threading
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from difflib import get_close_matches
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

TASKS_FILE = "tasks.json"


class AutomationAssistant:
    def __init__(self):
        self.tasks = self.load_tasks()

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r") as f:
                return json.load(f)
        return []

    def save_tasks(self):
        with open(TASKS_FILE, "w") as f:
            json.dump(self.tasks, f, indent=2, default=str)

    def add_task(self, task):
        self.tasks.append({"task": task, "deadline": None})
        self.save_tasks()

    def list_tasks(self):
        return self.tasks

    def set_deadline(self, task_name, date_str):
        deadline = date_parser.parse(date_str)
        task = self.find_task(task_name)
        if task:
            task["deadline"] = deadline.strftime("%Y-%m-%d")
            self.save_tasks()
            return True
        return False

    def find_task(self, name):
        names = [t["task"] for t in self.tasks]
        match = get_close_matches(name, names, n=1, cutoff=0.6)
        if match:
            return next(t for t in self.tasks if t["task"] == match[0])
        return None

    def check_reminders(self):
        today = datetime.now().date()
        due = []
        for t in self.tasks:
            if t["deadline"]:
                try:
                    deadline = datetime.strptime(t["deadline"], "%Y-%m-%d").date()
                    if deadline <= today:
                        due.append(t)
                except:
                    continue
        return due


class TaskApp(tk.Tk):
    def __init__(self, manager):
        super().__init__()
        self.title("Task Assistant")
        self.geometry("400x500")
        self.manager = manager

        self.task_list = tk.Listbox(self, font=("Arial", 12))
        self.task_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        add_btn = tk.Button(self, text="Add Task", command=self.add_task)
        add_btn.pack(fill=tk.X, padx=10)

        deadline_btn = tk.Button(self, text="Set Deadline", command=self.set_deadline)
        deadline_btn.pack(fill=tk.X, padx=10)

        search_btn = tk.Button(self, text="Search Web", command=self.search_web)
        search_btn.pack(fill=tk.X, padx=10)

        open_btn = tk.Button(self, text="Open App", command=self.open_app)
        open_btn.pack(fill=tk.X, padx=10)

        self.refresh_tasks()
        self.after(5000, self.check_reminders_periodically)

    def refresh_tasks(self):
        self.task_list.delete(0, tk.END)
        for t in self.manager.list_tasks():
            deadline = t["deadline"] or "No deadline"
            self.task_list.insert(tk.END, f"{t['task']} (Due: {deadline})")

    def add_task(self):
        task = simpledialog.askstring("Add Task", "What is the task?")
        if task:
            self.manager.add_task(task)
            self.refresh_tasks()

    def set_deadline(self):
        task_name = simpledialog.askstring("Task Name", "Enter task name (approximate):")
        deadline = simpledialog.askstring("Deadline", "Enter deadline (YYYY-MM-DD or natural language):")
        if task_name and deadline:
            success = self.manager.set_deadline(task_name, deadline)
            if success:
                messagebox.showinfo("Success", "Deadline set!")
                self.refresh_tasks()
            else:
                messagebox.showwarning("Not Found", "Task not found.")

    def search_web(self):
        query = simpledialog.askstring("Search Web", "What do you want to search?")
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")

    def open_app(self):
        app_name = simpledialog.askstring("Open App", "App to open (e.g., terminal, text editor):")
        if not app_name:
            return
        app_map = {
            "edge": "microsoft-edge",
            "browser": "firefox",
            "terminal": "gnome-terminal",
            "text editor": "gedit",
            "calculator": "gnome-calculator",
        }
        app_cmd = app_map.get(app_name.lower(), app_name)

        system = platform.system()
        try:
            if system == "Darwin":
                os.system(f"open -a '{app_cmd}'")
            elif system == "Windows":
                os.system(f"start {app_cmd}")
            else:
                os.system(f"{app_cmd} &")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open application: {e}")

    def check_reminders_periodically(self):
        due = self.manager.check_reminders()
        for t in due:
            messagebox.showwarning("Reminder", f"Task due: {t['task']} (by {t['deadline']})")
        self.after(60000, self.check_reminders_periodically)  # check every 60s


if __name__ == "__main__":
    manager = AutomationAssistant()
    app = TaskApp(manager)
    app.mainloop()
