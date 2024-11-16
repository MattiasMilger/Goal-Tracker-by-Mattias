import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel
from datetime import datetime


class Goal:
    def __init__(self, title, description, recurrence="One-time"):
        self.title = title
        self.description = description
        self.recurrence = recurrence
        self.tasks = []  # List of (task, completed) tuples
        self.is_complete = False

    def toggle_task_completion(self, task_index):
        """Toggle the completion status of a task."""
        task, completed = self.tasks[task_index]
        self.tasks[task_index] = (task, not completed)
        self.update_completion_status()

    def update_completion_status(self):
        """Mark the goal as complete if all tasks are completed."""
        self.is_complete = all(completed for _, completed in self.tasks)


class GoalTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Goal Tracker")

        self.active_goals = []

        # Display current date and day
        self.current_date_label = tk.Label(root, text=self.get_current_date_and_day(), font=("Arial", 12))
        self.current_date_label.pack(pady=5)

        # Completion counter
        self.completion_counter_label = tk.Label(root, text="0/0 goals completed", font=("Arial", 12))
        self.completion_counter_label.pack(pady=5)

        # UI Elements
        self.create_goal_button = tk.Button(root, text="Create Goal", command=self.create_goal)
        self.create_goal_button.pack(pady=10)

        self.goals_listbox = tk.Listbox(root, width=50)
        self.goals_listbox.pack(pady=10)
        self.goals_listbox.bind('<Double-1>', self.double_click_edit_goal)
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
        self.update_completion_counter()
        self.manage_goal(new_goal)  # Automatically move to the manage goal UI

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
            status = "[✓]" if goal.is_complete else "[ ]"
            self.goals_listbox.insert(tk.END, f"{status} {goal.title} ({goal.recurrence})")
        self.edit_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)

    def update_completion_counter(self):
        completed_goals = sum(goal.is_complete for goal in self.active_goals)
        total_goals = len(self.active_goals)
        self.completion_counter_label.config(text=f"{completed_goals}/{total_goals} goals completed")

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
        self.manage_goal(self.selected_goal)

    def double_click_edit_goal(self, event):
        selected_index = self.goals_listbox.curselection()
        if not selected_index:
            return
        self.selected_goal_index = selected_index[0]
        self.selected_goal = self.active_goals[self.selected_goal_index]
        self.manage_goal(self.selected_goal)

    def manage_goal(self, goal):
        goal_window = Toplevel(self.root)
        goal_window.title("Manage Goal")

        def update_task_listbox():
            tasks_listbox.delete(0, tk.END)
            for task, completed in goal.tasks:
                status = "[✓]" if completed else "[ ]"
                tasks_listbox.insert(tk.END, f"{status} {task}")

        def add_task():
            if len(goal.tasks) >= 20:
                messagebox.showerror("Error", "Maximum of 20 tasks allowed.")
                return
            task_desc = simpledialog.askstring("Add Task", "Enter task description:")
            if task_desc:
                goal.tasks.append((task_desc, False))
                goal.update_completion_status()
                update_task_listbox()
                self.update_goals_list()
                self.update_completion_counter()

        def edit_task():
            selected_task_index = tasks_listbox.curselection()
            if not selected_task_index:
                return
            task_desc = simpledialog.askstring("Edit Task", "Edit task description:", initialvalue=goal.tasks[selected_task_index[0]][0])
            if task_desc is not None:
                goal.tasks[selected_task_index[0]] = (task_desc, goal.tasks[selected_task_index[0]][1])
                update_task_listbox()
                self.update_goals_list()
                self.update_completion_counter()

        def remove_task():
            selected_task_index = tasks_listbox.curselection()
            if not selected_task_index:
                return
            confirm = messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?")
            if confirm:
                del goal.tasks[selected_task_index[0]]
                goal.update_completion_status()
                update_task_listbox()
                self.update_goals_list()
                self.update_completion_counter()

        def toggle_task_completion(event=None):
            selected_task_index = tasks_listbox.curselection()
            if not selected_task_index:
                return
            goal.toggle_task_completion(selected_task_index[0])
            update_task_listbox()
            self.update_goals_list()
            self.update_completion_counter()

        def save_changes():
            updated_title = title_entry.get()
            updated_description = description_text.get("1.0", tk.END).strip()
            if updated_title:
                goal.title = updated_title
            goal.description = updated_description
            self.update_goals_list()
            self.update_completion_counter()
            goal_window.destroy()

        # Goal Title UI
        tk.Label(goal_window, text="Goal Title:", font=("Arial", 12)).pack(pady=5)
        title_entry = tk.Entry(goal_window, width=50)
        title_entry.insert(0, goal.title)
        title_entry.pack(pady=5)

        # Goal Description UI
        tk.Label(goal_window, text="Goal Description:", font=("Arial", 12)).pack(pady=5)
        description_text = tk.Text(goal_window, width=50, height=5)
        description_text.insert("1.0", goal.description)
        description_text.pack(pady=5)

        # Task List UI
        tasks_listbox = tk.Listbox(goal_window, width=40)
        tasks_listbox.pack(pady=10)
        tasks_listbox.bind('<Double-1>', toggle_task_completion)

        tk.Button(goal_window, text="Add Task", command=add_task).pack(fill=tk.X)
        tk.Button(goal_window, text="Edit Task", command=edit_task).pack(fill=tk.X)
        tk.Button(goal_window, text="Remove Task", command=remove_task).pack(fill=tk.X)

        # Save Button
        tk.Button(goal_window, text="Save Changes", command=save_changes).pack(pady=10)

        update_task_listbox()

    def delete_goal(self):
        confirm = messagebox.askyesno("Delete Goal", "Are you sure you want to delete this goal?")
        if confirm:
            del self.active_goals[self.selected_goal_index]
            self.update_goals_list()
            self.update_completion_counter()


if __name__ == "__main__":
    root = tk.Tk()
    app = GoalTrackerApp(root)
    root.mainloop()
