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

        # Buttons for adding, editing, and deleting
        self.add_button = tk.Button(self.goal_frame, text="Add Goal", command=self.add_goal)
        self.add_button.grid(row=3, column=0, pady=5)

        self.edit_button = tk.Button(self.goal_frame, text="Edit Goal", command=self.edit_goal)
        self.edit_button.grid(row=3, column=1, pady=5)

        self.delete_button = tk.Button(self.goal_frame, text="Delete Goal", command=self.delete_goal)
        self.delete_button.grid(row=3, column=2, pady=5)

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

        self.add_task_button = tk.Button(root, text="Add Task", command=self.add_task)
        self.add_task_button.pack(side="left", padx=5)

        self.mark_task_complete_button = tk.Button(root, text="Mark Task as Complete", command=self.mark_task_complete)
        self.mark_task_complete_button.pack(side="left", padx=5)

        # Mark as complete/incomplete buttons
        self.complete_button = tk.Button(root, text="Mark Goal as Complete", command=self.mark_as_complete)
        self.complete_button.pack(pady=5)

        self.incomplete_button = tk.Button(root, text="Mark Goal as Incomplete", command=self.mark_as_incomplete)
        self.incomplete_button.pack(pady=5)

        # Bind listbox selection to refresh tasks
        self.goals_listbox.bind("<<ListboxSelect>>", self.refresh_tasks)
        self.complete_goals_listbox.bind("<<ListboxSelect>>", self.refresh_tasks)

        # Refresh UI
        self.refresh_goals()

    def add_goal(self):
        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()
        category = self.category_var.get()
        date = datetime.now().strftime("%Y-%m-%d")

        if not title:
            messagebox.showerror("Error", "Goal title cannot be empty.")
            return

        self.goals.append({
            "title": title,
            "description": description,
            "completed": False,
            "category": category,
            "date": date,
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

    def mark_task_complete(self):
        if not self.selected_goal:
            messagebox.showerror("Error", "Please select a goal and a task to mark as complete.")
            return

        selected_task = self.tasks_listbox.curselection()
        if not selected_task:
            messagebox.showerror("Error", "Please select a task to mark as complete.")
            return

        task = self.selected_goal["tasks"][selected_task[0]]
        task["completed"] = True

        self.save_goals()
        self.refresh_tasks()

    def mark_as_complete(self):
        if not self.selected_goal:
            messagebox.showerror("Error", "Please select a goal to mark as complete.")
            return

        if not all(task["completed"] for task in self.selected_goal["tasks"]):
            messagebox.showerror("Error", "All tasks must be completed before marking the goal as complete.")
            return

        self.selected_goal["completed"] = True
        self.selected_goal["date"] = datetime.now().strftime("%Y-%m-%d")
        self.save_goals()
        self.refresh_goals()

    def mark_as_incomplete(self):
        if not self.selected_goal:
            messagebox.showerror("Error", "Please select a completed goal to mark as incomplete.")
            return

        self.selected_goal["completed"] = False
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
            goal_display = f"{goal['title']} - {goal['description']} ({goal['category']})"
            goal_display += f" [Date: {goal['date']}, Times Completed: {goal['times_completed']}]"

            if goal["completed"]:
                self.complete_goals_listbox.insert(tk.END, goal_display)
            else:
                self.goals_listbox.insert(tk.END, goal_display)

    def get_goal_from_index(self, listbox, index):
        title = listbox.get(index).split(" - ")[0]
        for goal in self.goals:
            if goal["title"] == title:
                return goal

    def load_goals(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "r") as file:
                return json.load(file)
        return []

    def save_goals(self):
        with open(self.DATA_FILE, "w") as file:
            json.dump(self.goals, file, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = GoalTracker(root)
    root.mainloop()
