import tkinter as tk
from tkinter import messagebox
import json
import os

FILE_NAME = "tasks.json"

# ---------------------- FUNCTIONS ----------------------

def load_tasks():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as file:
            tasks = json.load(file)
            for task in tasks:
                listbox.insert(tk.END, task)

def save_tasks():
    tasks = listbox.get(0, tk.END)
    with open(FILE_NAME, "w") as file:
        json.dump(list(tasks), file)

def add_task():
    task = entry.get()
    if task != "":
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
        listbox.delete(selected)
        listbox.insert(tk.END, "✔ " + task)
        save_tasks()
    except:
        messagebox.showwarning("Warning", "Select a task!")

def delete_all():
    if listbox.get(0, tk.END) != () and messagebox.askyesno("Confirm", "Are you sure you want to delete all tasks?"):
        listbox.delete(0, tk.END)
        save_tasks()
    else:
        messagebox.showinfo("Warning", "You don't have any tasks to delete!")

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

add_btn = tk.Button(frame, text="Add Task", width=12, command=add_task)
add_btn.grid(row=0, column=0, padx=5, pady=5)

delete_btn = tk.Button(frame, text="Delete Task", width=12, command=delete_task)
delete_btn.grid(row=0, column=1, padx=5, pady=5)

done_btn = tk.Button(frame, text="Mark Done", width=12, command=mark_done)
done_btn.grid(row=0, column=2, padx=5, pady=5)

delete_all_btn = tk.Button(frame, text="Delete All", width=12, command=delete_all)
delete_all_btn.grid(row=0, column=3, padx=5, pady=5)

listbox = tk.Listbox(root, font=("Arial", 14), selectbackground="#16a085")
listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Load saved tasks
load_tasks()

root.mainloop()