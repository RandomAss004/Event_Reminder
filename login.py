import json
import os
import tkinter as tk
from tkinter import messagebox
import subprocess

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        return json.load(open(USERS_FILE))
    return {}

def save_users(users):
    json.dump(users, open(USERS_FILE, "w"))

def login():
    username = username_var.get().strip()
    password = password_var.get().strip()

    if not username or not password:
        messagebox.showwarning("Login", "Enter both username & password")
        return

    users = load_users()
    if username in users and users[username] == password:
        messagebox.showinfo("Login", f"Welcome {username}!")
        root.destroy()
        subprocess.Popen(["python", "reminder.py", username])
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")

def register():
    username = username_var.get().strip()
    password = password_var.get().strip()

    if not username or not password:
        messagebox.showwarning("Register", "Enter both username & password")
        return

    users = load_users()
    if username in users:
        messagebox.showerror("Register Failed", "Username already exists")
        return

    users[username] = password
    save_users(users)
    messagebox.showinfo("Register", "Registration successful!")

root = tk.Tk()
root.title("Login")
root.geometry("300x200")

username_var = tk.StringVar()
password_var = tk.StringVar()

tk.Label(root, text="Username:").pack(pady=5)
tk.Entry(root, textvariable=username_var).pack(pady=5)

tk.Label(root, text="Password:").pack(pady=5)
tk.Entry(root, textvariable=password_var, show="*").pack(pady=5)

tk.Button(root, text="Login", command=login).pack(pady=5)
tk.Button(root, text="Register", command=register).pack(pady=5)

root.mainloop()
