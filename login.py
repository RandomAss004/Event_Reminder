import json
import os
import customtkinter as ctk
from tkinter import messagebox
import subprocess


USERS_FILE = "users.json"


LANG_DICT = {
    "English": {
        "title": "Login",
        "username": "Username:",
        "password": "Password:",
        "password_confirm": "Confirm Password:",
        "login": "Login",
        "register": "Register",
        "login_success": "Welcome {username}!",
        "login_fail": "Invalid credentials",
        "login_warn": "Enter all fields",
        "register_success": "Registration successful!",
        "register_fail": "Username already exists",
        "password_mismatch": "Passwords do not match!",
        "language": "Language",
    },
    "Hindi": {
        "title": "लॉगिन",
        "username": "उपयोगकर्ता नाम:",
        "password": "पासवर्ड:",
        "password_confirm": "पासवर्ड पुष्टि करें:",
        "login": "लॉगिन",
        "register": "रजिस्टर करें",
        "login_success": "स्वागत है {username}!",
        "login_fail": "गलत प्रमाण-पत्र",
        "login_warn": "सभी फ़ील्ड भरें",
        "register_success": "रजिस्ट्रेशन सफल!",
        "register_fail": "यह नाम पहले से मौजूद है",
        "password_mismatch": "पासवर्ड मेल नहीं खाते!",
        "language": "भाषा",
    },
    "Marathi": {
        "title": "लॉगिन",
        "username": "वापरकर्ता नाव:",
        "password": "पासवर्ड:",
        "password_confirm": "पासवर्ड पडताळा:",
        "login": "लॉगिन",
        "register": "नोंदणी करा",
        "login_success": "{username} यांचे स्वागत आहे!",
        "login_fail": "अवैध माहिती",
        "login_warn": "सर्व फील्ड भरा",
        "register_success": "नोंदणी यशस्वी!",
        "register_fail": "हे नाव आधीपासूनच अस्तित्वात आहे",
        "password_mismatch": "पासवर्ड जुळत नाही!",
        "language": "भाषा",
    }
}


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


def update_labels(*args):
    lang = lang_var.get()
    t = LANG_DICT[lang]
    root.title(t["title"])
    username_label.configure(text=t["username"])
    password_label.configure(text=t["password"])
    confirm_password_label.configure(text=t["password_confirm"])
    login_button.configure(text=t["login"])
    register_button.configure(text=t["register"])
    language_label.configure(text=t["language"] + ":")


def login():
    lang = lang_var.get()
    t = LANG_DICT[lang]
    username = username_var.get().strip()
    password = password_var.get().strip()

    if not username or not password:
        messagebox.showwarning(t["title"], t["login_warn"])
        return

    users = load_users()
    if username in users and users[username] == password:
        messagebox.showinfo(t["title"], t["login_success"].format(username=username))
        root.destroy()
        subprocess.Popen(["python", "reminder.py", username])
    else:
        messagebox.showerror(t["title"], t["login_fail"])


def register():
    lang = lang_var.get()
    t = LANG_DICT[lang]
    username = username_var.get().strip()
    password = password_var.get().strip()
    confirm_password = confirm_password_var.get().strip()

    if not username or not password or not confirm_password:
        messagebox.showwarning(t["title"], t["login_warn"])
        return

    if password != confirm_password:
        messagebox.showerror(t["title"], t["password_mismatch"])
        return

    users = load_users()
    if username in users:
        messagebox.showerror(t["title"], t["register_fail"])
        return

    # The following lines must be inside the function!
    users[username] = password
    save_users(users)
    messagebox.showinfo(t["title"], t["register_success"])

    # Clear input fields after registration
    username_var.set("")
    password_var.set("")
    confirm_password_var.set("")


# Setup UI
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("360x420")  # Increased height for all widgets
root.resizable(False, False)

lang_var = ctk.StringVar(value="English")
username_var = ctk.StringVar()
password_var = ctk.StringVar()
confirm_password_var = ctk.StringVar()

frame = ctk.CTkFrame(root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

language_label = ctk.CTkLabel(frame, text=LANG_DICT["English"]["language"] + ":")
language_label.pack(pady=(8, 0))
lang_menu = ctk.CTkOptionMenu(frame, values=list(LANG_DICT.keys()), variable=lang_var)
lang_menu.pack(pady=(0, 12))

username_label = ctk.CTkLabel(frame, text=LANG_DICT["English"]["username"])
username_label.pack(pady=(4, 0))
username_entry = ctk.CTkEntry(frame, textvariable=username_var)
username_entry.pack(pady=(0, 8))

password_label = ctk.CTkLabel(frame, text=LANG_DICT["English"]["password"])
password_label.pack(pady=(4, 0))
password_entry = ctk.CTkEntry(frame, textvariable=password_var, show="*")
password_entry.pack(pady=(0, 8))

confirm_password_label = ctk.CTkLabel(frame, text=LANG_DICT["English"]["password_confirm"])
confirm_password_label.pack(pady=(4, 0))
confirm_password_entry = ctk.CTkEntry(frame, textvariable=confirm_password_var, show="*")
confirm_password_entry.pack(pady=(0, 12))

login_button = ctk.CTkButton(frame, text=LANG_DICT["English"]["login"], command=login)
login_button.pack(pady=(5, 3))
register_button = ctk.CTkButton(frame, text=LANG_DICT["English"]["register"], command=register)
register_button.pack(pady=(0, 3))

lang_var.trace("w", update_labels)

root.title(LANG_DICT["English"]["title"])
root.mainloop()
