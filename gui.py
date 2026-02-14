import tkinter as tk
from tkinter import filedialog
from threading import Thread
from tkinter import ttk
from scraper import scrape_ozon, stop_scraping


root = tk.Tk()
root.title("Ozon Scraper")
root.geometry("1400x800")
bg = "lightgrey"

left_frame = tk.Frame(root, bg=bg)
left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

label_logs = tk.Label(
    left_frame,
    text="Logs",
    bg=bg,
    font=("Arial", 22, "bold")  
)
label_logs.pack()

line = tk.Canvas(left_frame, height=2, bg="black", highlightthickness=0)
line.pack(fill="x")

log_text = tk.Text(
    left_frame,
    bg=bg,
    borderwidth=0,
    highlightthickness=0,
    font=("Arial", 14)  
)
log_text.pack(fill="both", expand=True, padx=5, pady=5)


right_frame = tk.Frame(root, bg=bg, width=450)
right_frame.pack(side="right", fill="y", padx=5, pady=5)
right_frame.pack_propagate(False)

label_settings = tk.Label(
    right_frame,
    text="Settings",
    bg=bg,
    font=("Arial", 22, "bold")
)
label_settings.pack()

line2 = tk.Canvas(right_frame, height=2, bg="black", highlightthickness=0)
line2.pack(fill="x", pady=15)

tk.Label(right_frame, text="Query:", bg=bg, font=("Arial", 16)).pack(pady=(5,0))
query_entry = tk.Entry(right_frame, width=35, font=("Arial", 14))
query_entry.pack(pady=10)


tk.Label(right_frame, text="Count:", bg=bg, font=("Arial", 16)).pack()
count_entry = tk.Entry(right_frame, width=35, font=("Arial", 14))
count_entry.insert(0, "10")
count_entry.pack(pady=10)


save_path = ""

def choose_path():
    global save_path
    path = filedialog.askdirectory()
    if path:
        save_path = path
        path_label.config(text=path)

tk.Button(
    right_frame,
    text="Choose folder",
    width=30,
    height=2,
    font=("Arial", 14),
    command=choose_path
).pack(pady=10)

path_label = tk.Label(right_frame, text="", bg=bg, font=("Arial", 14))
path_label.pack(pady=(0,15))


def log(msg):
    log_text.insert(tk.END, msg + "\n")
    log_text.see(tk.END)

def start():
    global stop_scraping
    stop_scraping = False  

    query = query_entry.get()
    count = int(count_entry.get())
    selected_format = format_var.get()  


    Thread(
        target=scrape_ozon,
        args=(query, count, save_path, log, selected_format)
    ).start()



tk.Button(
    right_frame,
    text="START",
    width=30,
    height=2,
    font=("Arial", 14, "bold"),
    command=start
).pack(pady=20)


tk.Label(right_frame, text="Формат сохранения:", bg=bg, font=("Arial", 16)).pack(pady=(10,0))

format_var = tk.StringVar(value="json") 

format_dropdown = ttk.Combobox(
    right_frame,
    textvariable=format_var,
    values=["json", "csv", "xlsx"],
    font=("Arial", 14),
    state="readonly",
    width=10
)
format_dropdown.pack(pady=(0,15))

tk.Button(
    right_frame,
    text="STOP",
    width=30,
    height=2,
    font=("Arial", 14, "bold"),
    fg="red",
    command=stop_scraping
).pack(pady=10)


  



def main():
    root.mainloop()

