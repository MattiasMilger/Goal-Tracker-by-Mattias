import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel
from datetime import datetime

class Goal:
    def __init__(self, title, description, recurrence="One-time"):
        self.title = title
        self.description = description
        self.recurrence = recurrence
        self.tasks = []  # List to store tasks (up to 20)

class GoalTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Goal Tracker")
        
        self.active_goals = []
        
        # Display current date and day
        self.current_date_label = tk.Label(root, text=self.get_current_date_and_day(), font=("Arial", 12))
        self.current_date_label.pack(pady=5)
        
        # UI Elements
        self.create_goal_button = tk.Button(root, text="Create Goal", command=self.create_goal)
        self.create_goal_button.pack(pady=10)
        
        self.goals_listbox = tk.Listbox(root, width=50)
        self.goals_listbox.pack(pady=10)
        self.goals_listbox.bind('<<ListboxSelect>>', self.show_goal_details)

        self.edit_button = tk.Button(root, text="Edit Goal", command=self.edit_goal, state=tk.DISABLED)
        self.edit_button.pack(pady=5)

        self.delete_button = tk.Button(root, text="Delete Goal", command=self.delete_goal, state=tk.DISABLED)
        self.delete_button.pack(pady=5)

    def get_current_date_and_day(self):
        """Fetch and return the current date and day of the week as a string."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        day_str = now.strftime("%A")  # Full weekday name
        return f"Today's Date: {date_str} ({day_str})"

    def create_goal(self):
        recurrence = self.choose_recurrence()
        if not recurrence:
            return
        
        title = simpledialog.askstring("Goal Title", "Enter the title of the goal:")
        if not title:
            return
        
        description = simpledialog.askstring("Goal Description", "Enter the description of the goal:")
        if description is None:
            return

        new_goal = Goal(title, description, recurrence)
        self.active_goals.append(new_goal)
        
        self.update_goals_list()

    def choose_recurrence(self):
        """Opens a dialog to choose recurrence using buttons."""
        recurrence_window = Toplevel(self.root)
        recurrence_window.title("Choose Recurrence")
        
        recurrence_choice = tk.StringVar()
        recurrence_choice.set("")  # Default to empty choice
        
        def set_recurrence(choice):
            recurrence_choice.set(choice)
            recurrence_window.destroy()

        tk.Label(recurrence_window, text="Choose Recurrence", font=("Arial", 12)).pack(pady=10)
        tk.Button(recurrence_window, text="One-time", command=lambda: set_recurrence("One-time")).pack(fill=tk.X)
        tk.Button(recurrence_window, text="Weekly", command=lambda: set_recurrence("Weekly")).pack(fill=tk.X)
        tk.Button(recurrence_window, text="Monthly", command=lambda: set_recurrence("Monthly")).pack(fill=tk.X)
        tk.Button(recurrence_window, text="Yearly", command=lambda: set_recurrence("Yearly")).pack(fill=tk.X)
        
        self.root.wait_window(recurrence_window)
        return recurrence_choice.get()

    def update_goals_list(self):
        self.goals_listbox.delete(0, tk.END)
        for goal in self.active_goals:
            self.goals_listbox.insert(tk.END, f"{goal.title} ({goal.recurrence})")
        self.edit_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)

    def show_goal_details(self, event):
        selected_index = self.goals_listbox.curselection()
        if not selected_index:
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            return
        
        self.selected_goal_index = selected_index[0]
        self.selected_goal = self.active_goals[self.selected_goal_index]
        self.edit_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)

    def edit_goal(self):
        title = simpledialog.askstring("Edit Goal Title", "Enter the new title:", initialvalue=self.selected_goal.title)
        if title:
            self.selected_goal.title = title
        
        description = simpledialog.askstring("Edit Goal Description", "Enter the new description:", initialvalue=self.selected_goal.description)
        if description is not None:
            self.selected_goal.description = description

        recurrence = self.choose_recurrence()
        if recurrence:
            self.selected_goal.recurrence = recurrence

        self.manage_tasks(self.selected_goal)

        self.update_goals_list()

    def manage_tasks(self, goal):
        task_window = Toplevel(self.root)
        task_window.title(f"Manage Tasks for '{goal.title}'")

        def update_task_listbox():
            tasks_listbox.delete(0, tk.END)
            for task in goal.tasks:
                tasks_listbox.insert(tk.END, task)

        def add_task():
            if len(goal.tasks) >= 20:
                messagebox.showerror("Error", "Maximum of 20 tasks allowed.")
                return
            task_desc = simpledialog.askstring("Add Task", "Enter task description:")
            if task_desc:
                goal.tasks.append(task_desc)
                update_task_listbox()

        def edit_task():
            selected_task_index = tasks_listbox.curselection()
            if not selected_task_index:
                return
            task_desc = simpledialog.askstring("Edit Task", "Edit task description:", initialvalue=goal.tasks[selected_task_index[0]])
            if task_desc is not None:
                goal.tasks[selected_task_index[0]] = task_desc
                update_task_listbox()

        def remove_task():
            selected_task_index = tasks_listbox.curselection()
            if not selected_task_index:
                return
            confirm = messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?")
            if confirm:
                del goal.tasks[selected_task_index[0]]
                update_task_listbox()

        tasks_listbox = tk.Listbox(task_window, width=40)
        tasks_listbox.pack(pady=10)

        tk.Button(task_window, text="Add Task", command=add_task).pack(fill=tk.X)
        tk.Button(task_window, text="Edit Task", command=edit_task).pack(fill=tk.X)
        tk.Button(task_window, text="Remove Task", command=remove_task).pack(fill=tk.X)

        update_task_listbox()

    def delete_goal(self):
        if self.selected_goal_index is not None:
            confirm = messagebox.askyesno("Delete Goal", f"Are you sure you want to delete '{self.selected_goal.title}'?")
            if confirm:
                del self.active_goals[self.selected_goal_index]
                self.update_goals_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = GoalTrackerApp(root)
    root.mainloop()
