import tkinter as tk
from tkinter import filedialog, ttk
from threading import Thread
from Scraping.ozon_scraper import OzonScraper



class OzonScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ozon Scraper")
        self.root.geometry("1400x800")
        self.bg = "lightgrey"
        self.save_path = ""
        self.scraper = None

        self.create_widgets()

    def create_widgets(self):

        left_frame = tk.Frame(self.root, bg=self.bg)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        tk.Label(left_frame, text="Logs", bg=self.bg, font=("Arial", 22, "bold")).pack()
        tk.Canvas(left_frame, height=2, bg="black", highlightthickness=0).pack(fill="x")
        self.log_text = tk.Text(left_frame, bg=self.bg, borderwidth=0, highlightthickness=0, font=("Arial", 14))
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        right_frame = tk.Frame(self.root, bg=self.bg, width=450)
        right_frame.pack(side="right", fill="y", padx=5, pady=5)
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="Settings", bg=self.bg, font=("Arial", 22, "bold")).pack()
        tk.Canvas(right_frame, height=2, bg="black", highlightthickness=0).pack(fill="x", pady=15)

        tk.Label(right_frame, text="Query:", bg=self.bg, font=("Arial", 16)).pack(pady=(5,0))
        self.query_entry = tk.Entry(right_frame, width=35, font=("Arial", 14))
        self.query_entry.pack(pady=10)

        tk.Label(right_frame, text="Count:", bg=self.bg, font=("Arial", 16)).pack()
        self.count_entry = tk.Entry(right_frame, width=35, font=("Arial", 14))
        self.count_entry.insert(0, "10")
        self.count_entry.pack(pady=10)

        tk.Button(right_frame, text="Choose folder", width=30, height=2, font=("Arial", 14), command=self.choose_path).pack(pady=10)
        self.path_label = tk.Label(right_frame, text="", bg=self.bg, font=("Arial", 14))
        self.path_label.pack(pady=(0,15))

        tk.Label(right_frame, text="Формат сохранения:", bg=self.bg, font=("Arial", 16)).pack(pady=(10,0))
        self.format_var = tk.StringVar(value="json")
        ttk.Combobox(right_frame, textvariable=self.format_var, values=["json", "csv", "xlsx"], font=("Arial", 14), state="readonly", width=10).pack(pady=(0,15))

        tk.Button(right_frame, text="START", width=30, height=2, font=("Arial", 14, "bold"), command=self.start_scraping).pack(pady=20)
        tk.Button(right_frame, text="STOP", width=30, height=2, font=("Arial", 14, "bold"), fg="red", command=self.stop_scraping).pack(pady=10)

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def choose_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path = path
            self.path_label.config(text=path)

    def start_scraping(self):
        query = self.query_entry.get()
        count = int(self.count_entry.get())
        file_format = self.format_var.get()
        if not self.save_path:
            self.log("Выберите папку для сохранения данных")
            return
        self.scraper = OzonScraper(query, count, self.save_path, log_callback=self.log, file_format=file_format)
        Thread(target=self.scraper.scrape).start()

    def stop_scraping(self):
        if self.scraper:
            self.scraper.stop_scraping()
            self.log("Стоп команда отправлена...")