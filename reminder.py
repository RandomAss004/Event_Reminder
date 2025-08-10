import customtkinter as ctk
import json
import os
import threading
import time
from datetime import datetime, timedelta
import pyttsx3
import pywhatkit
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

FILE = "events.json"
editing_index = -1

# -------------------- Data Handling -------------------- #
def load_data():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as f:
                data = json.load(f)
                for e in data:
                    e.setdefault("done", False)
                    e.setdefault("phone", "")
                    e.setdefault("time", "")
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_data():
    try:
        with open(FILE, "w") as f:
            json.dump(events, f, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")

# -------------------- Speech & Messaging -------------------- #
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Text-to-speech Error: {e}")

def send_whatsapp_message(phone, message):
    try:
        now = datetime.now()
        send_time = now + timedelta(minutes=1)
        pywhatkit.sendwhatmsg(phone, message, send_time.hour, send_time.minute)
    except Exception as e:
        print(f"WhatsApp Error: {e}")

# -------------------- Event Functions -------------------- #
def add_or_update_event():
    global editing_index
    name = name_var.get().strip()
    date_str = date_var.get().strip()
    time_str = time_var.get().strip()
    phone = phone_var.get().strip()
    if not name or not date_str or not time_str:
        popup_message("Please enter event name, date, and time.")
        return
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        popup_message("Date must be YYYY-MM-DD and time must be HH:MM.")
        return
    event_data = {
        "name": name,
        "date": date_str,
        "time": time_str,
        "phone": phone,
        "done": False
    }
    if editing_index >= 0:
        events[editing_index].update(event_data)
        editing_index = -1
    else:
        events.append(event_data)
    save_data()
    clear_inputs()
    refresh_event_table()
    add_update_btn.configure(text="Add Event ➕")

def delete_event(idx):
    if ctk.CTkMessagebox(title="Delete Event", message="Are you sure?", icon="warning", option_1="Yes", option_2="No").get()=="Yes":
        events.pop(idx)
        save_data()
        refresh_event_table()

def mark_done(idx):
    events[idx]["done"] = True
    save_data()
    refresh_event_table()

def edit_event(idx):
    global editing_index
    editing_index = idx
    e = events[idx]
    name_var.set(e["name"])
    date_var.set(e["date"])
    time_var.set(e["time"])
    phone_var.set(e["phone"])
    add_update_btn.configure(text="Save Changes ✏️")

def clear_inputs():
    global editing_index
    name_var.set("")
    date_var.set("")
    time_var.set("")
    phone_var.set("")
    editing_index = -1
    add_update_btn.configure(text="Add Event ➕")

def refresh_event_table():
    # Destroy previous rows
    for row in table_frame.winfo_children():
        row.destroy()
    # Table headings
    headings = ["Event Name", "Date", "Time", "Phone", "Status", "Action"]
    for i, h in enumerate(headings):
        ctk.CTkLabel(table_frame, text=h, font=("Helvetica", 13, "bold"), width=105, height=25).grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
    # Table rows
    for idx, e in enumerate(events):
        for j, col in enumerate([e["name"], e["date"], e["time"], e["phone"], "✔" if e.get("done", False) else ""]):
            ctk.CTkLabel(table_frame, text=col, width=105).grid(row=idx+1, column=j, padx=1, pady=1, sticky="nsew")
        # Action buttons
        action_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        ctk.CTkButton(action_frame, text="Mark", width=50, command=lambda idx=idx: mark_done(idx)).pack(side="left", padx=1)
        ctk.CTkButton(action_frame, text="Edit", width=50, command=lambda idx=idx: edit_event(idx)).pack(side="left", padx=1)
        ctk.CTkButton(action_frame, text="Delete", width=55, fg_color="#FF5A5A", command=lambda idx=idx: delete_event(idx)).pack(side="left", padx=1)
        action_frame.grid(row=idx+1, column=5, pady=1, sticky="nsew")

def popup_message(msg):
    box = ctk.CTkMessagebox(title="Event Reminder", message=msg)
    box.get()

# -------------------- Background Reminder Checker -------------------- #
def reminder_checker():
    while True:
        now = datetime.now()
        for e in events:
            if not e.get("done", False):
                try:
                    event_datetime_str = f"{e['date']} {e['time']}"
                    event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")
                    if now <= event_datetime < now + timedelta(minutes=1):
                        speak(f"Reminder: {e['name']} is now.")
                        if e.get("phone"):
                            send_whatsapp_message(e["phone"], f"Reminder: {e['name']} is now scheduled.")
                        e["done"] = True
                        save_data()
                        root.after(0, refresh_event_table)
                except (ValueError, KeyError):
                    continue
        time.sleep(30)

# -------------------- Graph -------------------- #
def calculate_daily_stats():
    daily_stats = {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0,
                   'Fri': 0, 'Sat': 0, 'Sun': 0}
    now = datetime.now().date()
    start_of_week = now - timedelta(days=now.weekday())
    for e in events:
        try:
            event_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
            if e["done"] and start_of_week <= event_date < start_of_week + timedelta(days=7):
                day_of_week = event_date.strftime('%a')
                if day_of_week in daily_stats:
                    daily_stats[day_of_week] += 1
        except (ValueError, TypeError):
            continue
    return daily_stats

def update_weekly_stats_graph():
    daily_stats = calculate_daily_stats()
    days = list(daily_stats.keys())
    counts = list(daily_stats.values())
    graph_window = ctk.CTkToplevel(root)
    graph_window.title("Weekly Completion Graph")
    graph_window.geometry("650x400")
    fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
    ax.bar(days, counts, color='teal')
    ax.set_title('Completed Events per Day (Current Week)')
    ax.set_xlabel('Day of the Week')
    ax.set_ylabel('Events Completed')
    ax.set_ylim(0, max(counts)+1 if counts else 1)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.get_tk_widget().pack(pady=10, padx=10, fill='both', expand=True)
    canvas.draw()

def show_overview_page():
    overview_window = ctk.CTkToplevel(root)
    overview_window.title("Event Overview")
    overview_window.geometry("400x300")
    total_events = len(events)
    completed_events = sum(1 for e in events if e.get("done", False))
    pending_events = total_events - completed_events
    stats = [("Total Events", total_events), ("Completed Events", completed_events), ("Pending Events", pending_events)]
    title_label = ctk.CTkLabel(overview_window, text="Event Statistics", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=(20, 10))
    for stat, val in stats:
        row = ctk.CTkFrame(overview_window)
        ctk.CTkLabel(row, text=stat, width=180, anchor="w").pack(side="left", padx=6)
        ctk.CTkLabel(row, text=str(val), width=100).pack(side="right", padx=6)
        row.pack(fill="x", padx=20, pady=3)

def show_about():
    info = (
        "Event Reminder App\n"
        "Contributors:\n"
        "1. Shriven Muley\n"
        "2. Atul Bawaskar\n"
        "3. Om Singh\n"
        "4. Aryan Gharat\n"
        "5. Rohan Sarkate\n"
        "6. Umar Patel\n"
        "Version 1.8"
    )
    about_win = ctk.CTkToplevel(root)
    about_win.title("About")
    about_win.geometry("320x280")
    about_label = ctk.CTkLabel(about_win, text=info, justify="left", font=("Helvetica", 13))
    about_label.pack(pady=20, padx=20)
    ctk.CTkButton(about_win, text="OK", command=about_win.destroy).pack(pady=10)

# -------------------- UI Setup -------------------- #
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.title("Event Reminder")
root.geometry("820x700")
root.resizable(True, True)
name_var = ctk.StringVar()
date_var = ctk.StringVar()
time_var = ctk.StringVar()
phone_var = ctk.StringVar()
events = load_data()

ctk.CTkLabel(root, text="EVENT REMINDER", font=("Helvetica", 18, "bold")).pack(pady=(10, 5))
input_frame = ctk.CTkFrame(root)
input_frame.pack(pady=10, padx=10, fill='x')
ctk.CTkLabel(input_frame, text="Event Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
ctk.CTkEntry(input_frame, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
ctk.CTkLabel(input_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5, sticky='w')
ctk.CTkEntry(input_frame, textvariable=date_var).grid(row=0, column=3, padx=5, pady=5, sticky='ew')
ctk.CTkLabel(input_frame, text="Time (HH:MM):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
ctk.CTkEntry(input_frame, textvariable=time_var).grid(row=1, column=1, padx=5, pady=5, sticky='ew')
ctk.CTkLabel(input_frame, text="Phone (+CountryCodeNumber):").grid(row=1, column=2, padx=5, pady=5, sticky='w')
ctk.CTkEntry(input_frame, textvariable=phone_var).grid(row=1, column=3, padx=5, pady=5, sticky='ew')

add_update_btn = ctk.CTkButton(input_frame, text="Add Event ➕", command=add_or_update_event)
add_update_btn.grid(row=2, column=0, columnspan=4, pady=10, sticky='ew')

# CustomTkinter Table Replacement
table_frame = ctk.CTkScrollableFrame(root, height=340)  # Use scrollable frame for table
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Button Panel
btn_frame = ctk.CTkFrame(root)
btn_frame.pack(pady=5, padx=10)
ctk.CTkButton(btn_frame, text="View Graph", command=update_weekly_stats_graph).pack(side='left', padx=5)
ctk.CTkButton(btn_frame, text="Overview Page", command=show_overview_page).pack(side='left', padx=5)
ctk.CTkButton(btn_frame, text="Clear Inputs", command=clear_inputs).pack(side='left', padx=5)
ctk.CTkButton(btn_frame, text="About", command=show_about).pack(side='left', padx=5)

def menu_exit():
    root.destroy()

# Start reminder thread and initial table render
threading.Thread(target=reminder_checker, daemon=True).start()
refresh_event_table()
root.mainloop()
