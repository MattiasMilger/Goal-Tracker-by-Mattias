import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
from datetime import datetime, timedelta

# Constants
MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT = 600, 740

# Colors and Theme
BACKGROUND_COLOR = "#2b2b2b"
TEXT_COLOR = "#ffffff"
ENTRY_COLOR = "#4a4a4a"
BUTTON_COLOR = "#3a3a3a"

class GoalTracker:
    DATA_FILE = "goals_with_tasks.json"

    def __init__(self, root):
        # Tkinter setup
        self.root = root
        self.root.title("Goal Tracker")
        root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        root.configure(bg=BACKGROUND_COLOR)

        self.goals = self.load_goals()
        self.reset_goals()

        self.selected_goal = None

        # Frame for goal management
        self.goal_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
        self.goal_frame.pack(pady=10)

        # Entry fields
        tk.Label(self.goal_frame, text="Goal Title:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(self.goal_frame, width=30, bg=ENTRY_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)                                 
        self.title_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.goal_frame, text="Description:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, sticky="w")
        self.description_entry = tk.Entry(self.goal_frame, width=30, bg=ENTRY_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.description_entry.grid(row=1, column=1, padx=5)

        # Goal category dropdown
        tk.Label(self.goal_frame, text="Category:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).grid(row=2, column=0, sticky="w")
        self.category_var = tk.StringVar(value="Weekly")
        self.category_dropdown = tk.OptionMenu(self.goal_frame, self.category_var, "Daily", "Weekly", "Monthly", "One-Time")
        self.category_dropdown.grid(row=2, column=1, sticky="w")
        # Customize the main button
        self.category_dropdown.config(bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=ENTRY_COLOR, activeforeground=TEXT_COLOR)

        # Access the menu of the OptionMenu
        menu = self.category_dropdown["menu"]

        # Customize the dropdown menu colors
        menu.config(bg=BACKGROUND_COLOR, fg=TEXT_COLOR, activebackground=ENTRY_COLOR, activeforeground=TEXT_COLOR)

        # Buttons for managing goals
        self.goal_button_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
        self.goal_button_frame.pack(pady=5)
        
        #Button for adding goal
        self.add_button = tk.Button(self.goal_button_frame, text="Add Goal", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=self.add_goal)
        self.add_button.pack(side="left", padx=5)

        self.edit_button = tk.Button(self.goal_button_frame, text="Edit Goal", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=self.edit_goal)
        self.edit_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(self.goal_button_frame, text="Delete Goal", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=self.delete_goal)
        self.delete_button.pack(side="left", padx=5)

        self.toggle_goal_button = tk.Button(self.goal_button_frame, text="Toggle Goal Completion", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=self.toggle_goal_completion)
        self.toggle_goal_button.pack(side="left", padx=5)

        self.edit_times_completed_button = tk.Button(self.goal_button_frame, text="Edit Times Completed", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=self.edit_times_completed)
        self.edit_times_completed_button.pack(side="left", padx=5)

        # Listboxes
        tk.Label(root, text="Incomplete Goals:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor="w", padx=10)
        self.goals_listbox = tk.Listbox(root, width=80, height=10, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.goals_listbox.pack(pady=5)

        tk.Label(root, text="Completed Goals:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor="w", padx=10)
        self.complete_goals_listbox = tk.Listbox(root, width=80, height=10, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.complete_goals_listbox.pack(pady=5)

        # Task List and controls
        tk.Label(root, text="Tasks for Selected Goal:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR                                                                                                                                                                                                                                                                                                                                ).pack(anchor="w", padx=10)
        self.tasks_listbox = tk.Listbox(root, width=80, height=5, bg=ENTRY_COLOR, fg=TEXT_COLOR)
        self.tasks_listbox.pack(pady=5)

        task_button_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
        task_button_frame.pack(pady=5)

        self.add_task_button = tk.Button(task_button_frame, text="Add Task", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=self.add_task)
        self.add_task_button.pack(side="left", padx=5)

        self.edit_task_button = tk.Button(task_button_frame, text="Edit Task", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=self.edit_task)
        self.edit_task_button.pack(side="left", padx=5)

        self.delete_task_button = tk.Button(task_button_frame, text="Delete Task", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=self.delete_task)
        self.delete_task_button.pack(side="left", padx=5)

        self.toggle_task_button = tk.Button(task_button_frame, text="Toggle Task Completion", bg=BUTTON_COLOR, fg=TEXT_COLOR, command=self.toggle_task_completion)
        self.toggle_task_button.pack(side="left", padx=5)

        tk.Label(text="", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(padx=10)

        tk.Button(text="Exit", command=root.quit, width=15, bg=BUTTON_COLOR, fg=TEXT_COLOR).pack()

        tk.Label(text="", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(padx=10)

        # Bind listbox selection to refresh tasks
        self.goals_listbox.bind("<<ListboxSelect>>", self.refresh_tasks)
        self.complete_goals_listbox.bind("<<ListboxSelect>>", self.refresh_tasks)

        # Refresh UI
        self.refresh_goals()

    def reset_goals(self):
        current_date = datetime.now()
        for goal in self.goals:
            reset_needed = False
            if goal["category"] == "Daily":
                last_reset_date = datetime.strptime(goal.get("last_reset_date", "1970-01-01"), "%Y-%m-%d")
                if current_date - last_reset_date >= timedelta(days=1):
                    reset_needed = True
            if goal["category"] == "Weekly":
                last_reset_date = datetime.strptime(goal.get("last_reset_date", "1970-01-01"), "%Y-%m-%d")
                if current_date - last_reset_date >= timedelta(days=7):
                    reset_needed = True
            elif goal["category"] == "Monthly":
                last_reset_date = datetime.strptime(goal.get("last_reset_date", "1970-01-01"), "%Y-%m-%d")
                if current_date.month != last_reset_date.month or current_date.year != last_reset_date.year:
                    reset_needed = True

            if reset_needed:
                goal["completed"] = False
                goal["tasks"] = [{"title": task["title"], "completed": False} for task in goal["tasks"]]
                goal["times_completed"] += 1
                goal["last_reset_date"] = current_date.strftime("%Y-%m-%d")

        self.save_goals()

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
            "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
        })
        self.save_goals()
        self.refresh_goals()
        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

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

    def edit_times_completed(self):
        if not self.selected_goal:
            messagebox.showerror("Error", "Please select a goal to edit times completed.")
        # Open a dialog to ask for a number
        number = simpledialog.askfloat("Change Times Completed", "Enter a number:")
        number = int(number) if number.is_integer() else number
        self.selected_goal["times_completed"] = number
        self.save_goals()
        self.refresh_goals()

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
            formatted_goal = f"{goal['title']} | {goal['description']} | ({goal['category']}) | (Completed {goal['times_completed']})"
            listbox = self.complete_goals_listbox if goal["completed"] else self.goals_listbox
            listbox.insert(tk.END, formatted_goal)

    def get_goal_from_index(self, listbox, index):
        title = listbox.get(index).split(" | ")[0]
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
    root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    app = GoalTracker(root)
    root.mainloop()
