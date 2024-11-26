import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
from datetime import datetime, timedelta


class GoalTracker:
    DATA_FILE = "goals_with_tasks.json"

    def __init__(self, root):
        self.root = root
        self.root.title("Goal Tracker")

        self.goals = self.load_goals()
        self.reset_weekly_goals()

        self.selected_goal = None

        # Frame for goal management
        self.goal_frame = tk.Frame(root)
        self.goal_frame.pack(pady=10)

        # Entry fields
        tk.Label(self.goal_frame, text="Goal Title:").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(self.goal_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.goal_frame, text="Description:").grid(row=1, column=0, sticky="w")
        self.description_entry = tk.Entry(self.goal_frame, width=30)
        self.description_entry.grid(row=1, column=1, padx=5)

        # Goal category dropdown
        tk.Label(self.goal_frame, text="Category:").grid(row=2, column=0, sticky="w")
        self.category_var = tk.StringVar(value="Weekly")
        self.category_dropdown = tk.OptionMenu(self.goal_frame, self.category_var, "Weekly", "Monthly", "One-Time")
        self.category_dropdown.grid(row=2, column=1, sticky="w")

        # Buttons for managing goals
        self.goal_button_frame = tk.Frame(root)
        self.goal_button_frame.pack(pady=5)

        self.add_button = tk.Button(self.goal_button_frame, text="Add Goal", command=self.add_goal)
        self.add_button.pack(side="left", padx=5)

        self.edit_button = tk.Button(self.goal_button_frame, text="Edit Goal", command=self.edit_goal)
        self.edit_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(self.goal_button_frame, text="Delete Goal", command=self.delete_goal)
        self.delete_button.pack(side="left", padx=5)

        self.toggle_goal_button = tk.Button(self.goal_button_frame, text="Toggle Goal Completion", command=self.toggle_goal_completion)
        self.toggle_goal_button.pack(side="left", padx=5)

        # Listboxes
        tk.Label(root, text="Incomplete Goals:").pack(anchor="w", padx=10)
        self.goals_listbox = tk.Listbox(root, width=80, height=10)
        self.goals_listbox.pack(pady=5)

        tk.Label(root, text="Completed Goals:").pack(anchor="w", padx=10)
        self.complete_goals_listbox = tk.Listbox(root, width=80, height=10)
        self.complete_goals_listbox.pack(pady=5)

        # Task List and controls
        tk.Label(root, text="Tasks for Selected Goal:").pack(anchor="w", padx=10)
        self.tasks_listbox = tk.Listbox(root, width=80, height=5)
        self.tasks_listbox.pack(pady=5)

        task_button_frame = tk.Frame(root)
        task_button_frame.pack(pady=5)

        self.add_task_button = tk.Button(task_button_frame, text="Add Task", command=self.add_task)
        self.add_task_button.pack(side="left", padx=5)

        self.edit_task_button = tk.Button(task_button_frame, text="Edit Task", command=self.edit_task)
        self.edit_task_button.pack(side="left", padx=5)

        self.delete_task_button = tk.Button(task_button_frame, text="Delete Task", command=self.delete_task)
        self.delete_task_button.pack(side="left", padx=5)

        self.toggle_task_button = tk.Button(task_button_frame, text="Toggle Task Completion", command=self.toggle_task_completion)
        self.toggle_task_button.pack(side="left", padx=5)

        # Bind listbox selection to refresh tasks
        self.goals_listbox.bind("<<ListboxSelect>>", self.refresh_tasks)
        self.complete_goals_listbox.bind("<<ListboxSelect>>", self.refresh_tasks)

        # Refresh UI
        self.refresh_goals()

    def add_goal(self):
        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()
        category = self.category_var.get()

        if not title:
            messagebox.showerror("Error", "Goal title cannot be empty.")
            return

        self.goals.append({
            "title": title,
            "description": description,
            "completed": False,
            "category": category,
            "times_completed": 0,
            "tasks": [],
        })
        self.save_goals()
        self.refresh_goals()
        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

    def reset_weekly_goals(self):
        current_date = datetime.now()
        for goal in self.goals:
            if goal["category"] == "Weekly" and goal["completed"]:
                last_completed_date = datetime.strptime(goal["date"], "%Y-%m-%d")
                if current_date - last_completed_date > timedelta(days=7):
                    goal["completed"] = False
                    goal["times_completed"] += 1
        self.save_goals()

    def edit_goal(self):
        if not self.selected_goal:
            messagebox.showerror("Error", "Please select a goal to edit.")
            return

        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()
        category = self.category_var.get()

        if title:
            self.selected_goal["title"] = title
        if description:
            self.selected_goal["description"] = description
        self.selected_goal["category"] = category

        self.save_goals()
        self.refresh_goals()
        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

    def delete_goal(self):
        if not self.selected_goal:
            messagebox.showerror("Error", "Please select a goal to delete.")
            return

        self.goals.remove(self.selected_goal)
        self.selected_goal = None

        self.save_goals()
        self.refresh_goals()
        self.tasks_listbox.delete(0, tk.END)

    def add_task(self):
        if not self.selected_goal:
            messagebox.showerror("Error", "Please select a goal to add a task to.")
            return

        task_title = simpledialog.askstring("Add Task", "Task Title:")
        if task_title:
            self.selected_goal["tasks"].append({"title": task_title, "completed": False})
            self.save_goals()
            self.refresh_tasks()

    def edit_task(self):
        if not self.selected_goal:
            messagebox.showerror("Error", "Please select a goal to edit a task.")
            return

        selected_task = self.tasks_listbox.curselection()
        if not selected_task:
            messagebox.showerror("Error", "Please select a task to edit.")
            return

        task = self.selected_goal["tasks"][selected_task[0]]
        new_title = simpledialog.askstring("Edit Task", "New Task Title:", initialvalue=task["title"])
        if new_title:
            task["title"] = new_title
            self.save_goals()
            self.refresh_tasks()

    def delete_task(self):
        if not self.selected_goal:
            messagebox.showerror("Error", "Please select a goal to delete a task from.")
            return

        selected_task = self.tasks_listbox.curselection()
        if not selected_task:
            messagebox.showerror("Error", "Please select a task to delete.")
            return

        del self.selected_goal["tasks"][selected_task[0]]
        self.save_goals()
        self.refresh_tasks()

    def toggle_task_completion(self):
        if not self.selected_goal:
            messagebox.showerror("Error", "Please select a goal and a task to toggle completion.")
            return

        selected_task = self.tasks_listbox.curselection()
        if not selected_task:
            messagebox.showerror("Error", "Please select a task to toggle completion.")
            return

        task = self.selected_goal["tasks"][selected_task[0]]
        task["completed"] = not task["completed"]

        self.save_goals()
        self.refresh_tasks()

    def toggle_goal_completion(self):
        if not self.selected_goal:
            messagebox.showerror("Error", "Please select a goal to toggle completion.")
            return

        self.selected_goal["completed"] = not self.selected_goal["completed"]
        self.save_goals()
        self.refresh_goals()

    def refresh_tasks(self, event=None):
        selected = self.goals_listbox.curselection() or self.complete_goals_listbox.curselection()
        if selected:
            listbox = self.goals_listbox if self.goals_listbox.curselection() else self.complete_goals_listbox
            index = selected[0]
            self.selected_goal = self.get_goal_from_index(listbox, index)

        if not self.selected_goal:
            return

        self.tasks_listbox.delete(0, tk.END)
        for task in self.selected_goal["tasks"]:
            task_status = "✔" if task["completed"] else "✘"
            self.tasks_listbox.insert(tk.END, f"{task_status} {task['title']}")

    def refresh_goals(self):
        self.goals_listbox.delete(0, tk.END)
        self.complete_goals_listbox.delete(0, tk.END)

        for goal in self.goals:
            listbox = self.complete_goals_listbox if goal["completed"] else self.goals_listbox
            listbox.insert(tk.END, f"{goal['title']} - {goal['category']}")

    def get_goal_from_index(self, listbox, index):
        title = listbox.get(index).split(" - ")[0]
        for goal in self.goals:
            if goal["title"] == title:
                return goal
        return None

    def save_goals(self):
        with open(self.DATA_FILE, "w") as file:
            json.dump(self.goals, file, indent=4)

    def load_goals(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "r") as file:
                return json.load(file)
        return []


if __name__ == "__main__":
    root = tk.Tk()
    app = GoalTracker(root)
    root.mainloop()
