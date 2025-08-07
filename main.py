import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import tkinter.font as tkFont
import json, os, time, threading
from datetime import datetime
import pyttsx3
import pywhatkit

FILE = "events.json"

# -------------------- Data Handling -------------------- #
def load_data():
    if os.path.exists(FILE):
        data = json.load(open(FILE))
        for e in data:
            e.setdefault("done", False)
            e.setdefault("phone", "")
            e.setdefault("time", "")
            e.setdefault("description", "")
        return data
    return []

def save_data():
    json.dump(events, open(FILE, "w"))

# -------------------- Speech -------------------- #
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# -------------------- WhatsApp -------------------- #
def send_whatsapp_message(phone, event):
    try:
        now = datetime.now()
        send_hour = now.hour
        send_minute = now.minute + 1
        
        # Beautiful formatted message
        message = (
            f"📌 Event Reminder\n"
            f"📅 Date: {event['date']}\n"
            f"🕒 Time: {event['time']}\n"
            f"📍 Event: {event['name']}\n"
            f"📝 Notes: {event['description']}"
        )
        
        pywhatkit.sendwhatmsg(phone, message, send_hour, send_minute)
    except Exception as e:
        print("WhatsApp Error:", e)


# -------------------- Event Functions -------------------- #
def add_event():
    global edit_index
    name = name_var.get().strip()
    date_str = date_var.get_date().strftime("%Y-%m-%d")
    time_str = time_var.get().strip()
    phone = phone_var.get().strip()
    desc = desc_var.get().strip()

    if not name or not date_str or not time_str:
        messagebox.showwarning("Input", "Please fill in Event Name, Date, and Time.")
        return

    if edit_index == -1:
        events.append({
            "name": name,
            "date": date_str,
            "time": time_str,
            "phone": phone,
            "description": desc,
            "done": False
        })
    else:
        events[edit_index].update({
            "name": name,
            "date": date_str,
            "time": time_str,
            "phone": phone,
            "description": desc
        })
        edit_index = -1
        add_btn.configure(text="Add Event")

    save_data()
    clear_inputs()
    refresh()

def delete_event():
    selected = tree.selection()
    if selected:
        idx = int(selected[0])
        events.pop(idx)
        save_data()
        refresh()

def mark_done():
    selected = tree.selection()
    if selected:
        idx = int(selected[0])
        events[idx]["done"] = True
        save_data()
        refresh()

def edit_event():
    global edit_index
    selected = tree.selection()
    if selected:
        idx = int(selected[0])
        e = events[idx]
        name_var.set(e["name"])
        date_var.set_date(datetime.strptime(e["date"], "%Y-%m-%d"))
        time_var.set(e["time"])
        phone_var.set(e["phone"])
        desc_var.set(e["description"])
        edit_index = idx
        add_btn.configure(text="Save Changes")

def clear_inputs():
    name_var.set("")
    time_var.set("")
    phone_var.set("")
    desc_var.set("")
    date_var.set_date(datetime.now())

# -------------------- Search & Filter -------------------- #
def filter_events(*args):
    search_text = search_var.get().lower()
    tree.delete(*tree.get_children())
    for i, e in enumerate(events):
        if (search_text in e["name"].lower() or
            search_text in e["description"].lower() or
            search_text in e["date"]):
            tree.insert("", "end", iid=i, values=(
                e["name"], e["date"], e["time"], e["phone"], e["description"],
                "✔" if e["done"] else ""
            ))
    auto_resize_columns()

# -------------------- Auto Column Resize -------------------- #
def auto_resize_columns():
    for col in tree["columns"]:
        tree.column(col, width=tkFont.Font().measure(col.title()) + 20)

# -------------------- Refresh -------------------- #
def refresh():
    filter_events()

# -------------------- Background Reminder Checker -------------------- #
def reminder_checker():
    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")

        for e in events:
            if e["date"] == today_str and e["time"] == current_time and not e["done"]:
                speak(f"Reminder: {e['name']} is now.")
                if e["phone"]:
                    send_whatsapp_message(e["phone"], e)

                e["done"] = True
                save_data()
                refresh()

        time.sleep(30)

# -------------------- UI -------------------- #
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Event Reminder")
root.geometry("900x600")

events = load_data()

edit_index = -1  # -1 means adding, >=0 means editing

# Variables
name_var = tk.StringVar()
time_var = tk.StringVar()
phone_var = tk.StringVar()
desc_var = tk.StringVar()
search_var = tk.StringVar()

search_var.trace("w", filter_events)

# Input Frame
input_frame = ctk.CTkFrame(root)
input_frame.pack(pady=10, padx=10, fill="x")

ctk.CTkLabel(input_frame, text="Event Name:").grid(row=0, column=0, padx=5, pady=5)
ctk.CTkEntry(input_frame, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)

ctk.CTkLabel(input_frame, text="Date:").grid(row=0, column=2, padx=5, pady=5)
date_var = DateEntry(input_frame, date_pattern="yyyy-mm-dd")
date_var.grid(row=0, column=3, padx=5, pady=5)

ctk.CTkLabel(input_frame, text="Time (HH:MM):").grid(row=1, column=0, padx=5, pady=5)
ctk.CTkEntry(input_frame, textvariable=time_var).grid(row=1, column=1, padx=5, pady=5)

ctk.CTkLabel(input_frame, text="Phone (+CountryCodeNumber):").grid(row=1, column=2, padx=5, pady=5)
ctk.CTkEntry(input_frame, textvariable=phone_var).grid(row=1, column=3, padx=5, pady=5)

ctk.CTkLabel(input_frame, text="Description:").grid(row=2, column=0, padx=5, pady=5)
ctk.CTkEntry(input_frame, textvariable=desc_var, width=400).grid(row=2, column=1, columnspan=3, padx=5, pady=5)

# Buttons
btn_frame = ctk.CTkFrame(root)
btn_frame.pack(pady=5)

add_btn = ctk.CTkButton(btn_frame, text="Add Event", command=add_event)
add_btn.grid(row=0, column=0, padx=5)
ctk.CTkButton(btn_frame, text="Edit Event", command=edit_event).grid(row=0, column=1, padx=5)
ctk.CTkButton(btn_frame, text="Mark Done", command=mark_done).grid(row=0, column=2, padx=5)
ctk.CTkButton(btn_frame, text="Delete Event", command=delete_event).grid(row=0, column=3, padx=5)

# Search
search_frame = ctk.CTkFrame(root)
search_frame.pack(pady=5, fill="x")
ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
ctk.CTkEntry(search_frame, textvariable=search_var).pack(side="left", fill="x", expand=True, padx=5)

# Treeview
tree_frame = ctk.CTkFrame(root)
tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

columns = ("Event", "Date", "Time", "Phone", "Description", "Done")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack(fill="both", expand=True)

refresh()

# Start reminder thread
threading.Thread(target=reminder_checker, daemon=True).start()

root.mainloop()
