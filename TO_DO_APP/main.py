import tkinter as tk
from tkinter import messagebox
import os

FILE_NAME = "tasks.txt"

# ---------------------- FUNCTIONS ----------------------

def load_tasks():
    try:
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r") as file:
                tasks = file.readlines()
                for task in tasks:
                    task = task.strip()
                    if task:
                        listbox.insert(tk.END, task)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load tasks: {e}")

def save_tasks():
    try:
        tasks = listbox.get(0, tk.END)
        with open(FILE_NAME, "w") as file:
            for task in tasks:
                file.write(task + "\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save tasks: {e}")

def add_task():
    task = entry.get().strip()
    if task:
        listbox.insert(tk.END, task)
        entry.delete(0, tk.END)
        save_tasks()
    else:
        messagebox.showwarning("Warning", "Enter a task!")

def delete_task():
    try:
        selected = listbox.curselection()[0]
        listbox.delete(selected)
        save_tasks()
    except:
        messagebox.showwarning("Warning", "Select a task to delete!")

def mark_done():
    try:
        selected = listbox.curselection()[0]
        task = listbox.get(selected)
        if not task.startswith("✔ "):
            listbox.delete(selected)
            listbox.insert(tk.END, "✔ " + task)
            save_tasks()
    except:
        messagebox.showwarning("Warning", "Select a task!")

def unmark_done():
    try:
        selected = listbox.curselection()[0]
        task = listbox.get(selected)
        if task.startswith("✔ "):
            listbox.delete(selected)
            listbox.insert(selected, task[2:])
            save_tasks()
    except:
        messagebox.showwarning("Warning", "Select a task!")

def update_task():
    try:
        selected = listbox.curselection()[0]
        new_task = entry.get().strip()
        if new_task:
            listbox.delete(selected)
            listbox.insert(selected, new_task)
            entry.delete(0, tk.END)
            save_tasks()
        else:
            messagebox.showwarning("Warning", "Enter a task!")
    except:
        messagebox.showwarning("Warning", "Select a task to update!")

def delete_all():
    if listbox.get(0, tk.END) != () and messagebox.askyesno("Confirm", "Are you sure you want to delete all tasks?"):
        listbox.delete(0, tk.END)
        save_tasks()
    else:
        messagebox.showinfo("Info", "You don't have any tasks to delete!")

# ---------------------- UI ----------------------

root = tk.Tk()
root.title("To-Do List App")
root.geometry("400x500")
root.config(bg="#2c3e50")

title = tk.Label(root, text="My To-Do List", font=("Arial", 18, "bold"), bg="#2c3e50", fg="white")
title.pack(pady=10)

entry = tk.Entry(root, font=("Arial", 14))
entry.pack(pady=10, padx=10, fill=tk.X)

frame = tk.Frame(root)
frame.pack()

add_btn = tk.Button(frame, text="Add Task", width=10, command=add_task)
add_btn.grid(row=0, column=0, padx=5, pady=5)

delete_btn = tk.Button(frame, text="Delete Task", width=10, command=delete_task)
delete_btn.grid(row=0, column=1, padx=5, pady=5)

done_btn = tk.Button(frame, text="Mark Done", width=10, command=mark_done)
done_btn.grid(row=0, column=2, padx=5, pady=5)

delete_all_btn = tk.Button(frame, text="Delete All", width=10, command=delete_all)
delete_all_btn.grid(row=0, column=3, padx=5, pady=5)

unmark_btn = tk.Button(frame, text="Unmark Done", width=10, command=unmark_done)
unmark_btn.grid(row=1, column=0, padx=5, pady=5)

update_btn = tk.Button(frame, text="Update Task", width=10, command=update_task)
update_btn.grid(row=1, column=1, padx=5, pady=5)

frame_list = tk.Frame(root)
frame_list.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame_list)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(frame_list, font=("Arial", 14), selectbackground="#16a085", yscrollcommand=scrollbar.set)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar.config(command=listbox.yview)

# Load saved tasks
load_tasks()

root.mainloop()