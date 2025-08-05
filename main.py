import tkinter as tk
from tkinter import ttk, messagebox
import json, os, time
from datetime import datetime
import threading
import pyttsx3
import pywhatkit

FILE = "events.json"

# -------------------- Data Handling -------------------- #
def load_data():
    if os.path.exists(FILE):
        data = json.load(open(FILE))
        for e in data:
            if "done" not in e:
                e["done"] = False
            if "phone" not in e:
                e["phone"] = ""
            if "time" not in e:
                e["time"] = ""
        return data
    return []

def save_data():
    json.dump(events, open(FILE, "w"))

# -------------------- Speech -------------------- #
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# -------------------- WhatsApp Sender -------------------- #
def send_whatsapp_message(phone, message):
    try:
        now = datetime.now()
        send_hour = now.hour
        send_minute = now.minute + 1  # PyWhatKit needs 1 min lead time
        pywhatkit.sendwhatmsg(phone, message, send_hour, send_minute)
    except Exception as e:
        print("WhatsApp Error:", e)

# -------------------- Event Functions -------------------- #
def add_event():
    name = name_var.get().strip()
    date = date_var.get().strip()
    time_str = time_var.get().strip()
    phone = phone_var.get().strip()
    
    if name and date and time_str:
        events.append({
            "name": name,
            "date": date,
            "time": time_str,
            "phone": phone,
            "done": False
        })
        save_data()
        refresh()
        name_var.set("")
        date_var.set("")
        time_var.set("")
        phone_var.set("")
    else:
        messagebox.showwarning("Input", "Enter event name, date, and time.")

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

def refresh():
    tree.delete(*tree.get_children())
    for i, e in enumerate(events):
        tree.insert("", "end", iid=i,
                    values=(e["name"], e["date"], e.get("time", ""), e.get("phone", ""), 
                            "✔" if e.get("done", False) else ""))

# -------------------- Background Reminder Checker -------------------- #
def reminder_checker():
    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        
        for e in events:
            if e["date"] == today_str and e.get("time") == current_time and not e.get("done", False):
                speak(f"Reminder: {e['name']} is now.")
                if e.get("phone"):
                    send_whatsapp_message(e["phone"], f"Reminder: {e['name']} is now scheduled.")
                e["done"] = True
                save_data()
                refresh()
        
        time.sleep(30)  # check every 30 seconds

# -------------------- UI -------------------- #
root = tk.Tk()
root.title("Event Reminder")
root.geometry("650x400")

# Variables
name_var = tk.StringVar()
date_var = tk.StringVar()
time_var = tk.StringVar()
phone_var = tk.StringVar()

events = load_data()

# Input Frame
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Event Name:").grid(row=0, column=0, padx=5, pady=5)
tk.Entry(frame, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5)
tk.Entry(frame, textvariable=date_var).grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame, text="Time (HH:MM):").grid(row=1, column=0, padx=5, pady=5)
tk.Entry(frame, textvariable=time_var).grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Phone (+CountryCodeNumber):").grid(row=1, column=2, padx=5, pady=5)
tk.Entry(frame, textvariable=phone_var).grid(row=1, column=3, padx=5, pady=5)

tk.Button(frame, text="Add Event", command=add_event).grid(row=2, column=0, columnspan=4, pady=5)

# Treeview
tree = ttk.Treeview(root, columns=("Event", "Date", "Time", "Phone", "Done"), show="headings")
tree.heading("Event", text="Event Name")
tree.heading("Date", text="Date")
tree.heading("Time", text="Time")
tree.heading("Phone", text="Phone")
tree.heading("Done", text="Done")
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Mark Done", command=mark_done).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Delete Event", command=delete_event).grid(row=0, column=1, padx=5)

refresh()

# Start reminder thread
threading.Thread(target=reminder_checker, daemon=True).start()

root.mainloop()
