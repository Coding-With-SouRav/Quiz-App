import configparser
import ctypes
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
import os
from faker import Faker
import requests
import html
import socket
import shelve

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("YourAppID.UniqueName")


def resource_path(relative_path):
    """ Get absolute path to resources for both dev and PyInstaller """

    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")
    full_path = os.path.join(base_path, relative_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Resource not found: {full_path}")
    return full_path


class QuizApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Game")
        self.root.geometry("600x700")

        try:
            root.iconbitmap(resource_path(r"icons/icon.ico"))

        except Exception as e:
            print("Icon load error:", e)
            
        # self.storage_path = os.path.join(os.path.expanduser("~"), ".quiz_config")

        self.quiz_storage_path = os.path.join(os.path.expanduser("~"), ".quiz_app_config")
        os.makedirs(self.quiz_storage_path, exist_ok=True)

        if sys.platform == "win32":
            try:
                ctypes.windll.kernel32.SetFileAttributesW(self.quiz_storage_path, 2)
            except:
                pass

        self.config_file = os.path.join(self.quiz_storage_path, "config.ini")

        self.current_theme = self.load_theme()
        self.themes = {
            "light": {"bg": "#f0f0f0", "fg": "black", "button": "#e0e0e0", "accent": "#717771"},
            "dark": {"bg": "#2d2d2d", "fg": "white", "button": "#3d3d3d", "accent": "#2196F3"},
            "blue": {"bg": "#e6f2ff", "fg": "black", "button": "#cce5ff", "accent": "#007bff"},
            "green": {"bg": "#e6ffe6", "fg": "black", "button": "#ccffcc", "accent": "#28a745"},
            "purple": {"bg": "#f0e6ff", "fg": "black", "button": "#e0ccff", "accent": "#6f42c1"}
        }
        self.questions = {
            "Easy": self.generate_easy_questions(100),
            "Medium": self.generate_medium_questions(100),
            "Hard": self.generate_hard_questions(100),
            "Googly": self.generate_googly_questions(100)
        }
        self.score = 0
        self.current_question_index = 0
        self.selected_difficulty = None
        self.questions_used = []
        self.normal_count_since_googly = 0
        self.question_history = []
        self.main_frame = tk.Frame(root)
        self.quiz_frame = tk.Frame(root)
        self.load_window_geometry()
        self.create_widgets()
        self.apply_theme(self.current_theme)
        self.show_main_screen()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_theme(self):
        """Load theme from JSON storage"""
        theme_file = os.path.join(self.quiz_storage_path, "theme.json")
        if os.path.exists(theme_file):
            try:
                with open(theme_file, 'r') as f:
                    data = json.load(f)
                    return data.get("theme", "light")
            except Exception as e:
                print(f"Error loading theme: {e}")
        return "light"

    def save_theme(self):
        """Save current theme to JSON storage"""
        theme_file = os.path.join(self.quiz_storage_path, "theme.json")
        try:
            with open(theme_file, 'w') as f:
                json.dump({"theme": self.current_theme}, f)
        except Exception as e:
            print(f"Error saving theme: {e}")

    def is_internet_available(self):
        """Check if internet connection is available"""

        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True

        except OSError:
            return False

    def get_internet_question(self, difficulty):
        """Fetch question from OpenTDB API"""
        difficulty_map = {
            "Easy": "Easy",
            "Medium": "Medium",
            "Hard": "Hard"
        }

        try:
            url = f"https://opentdb.com/api.php?amount=1&difficulty={difficulty_map.get(difficulty, 'Medium')}&type=multiple"
            response = requests.get(url, timeout=5)
            data = response.json()

            if data["response_code"] == 0:
                question = data["results"][0]
                q_text = html.unescape(question["question"])
                correct = html.unescape(question["correct_answer"])
                options = [html.unescape(opt) for opt in question["incorrect_answers"]]
                options.append(correct)
                random.shuffle(options)
                return {
                    "question": q_text,
                    "options": options,
                    "answer": correct
                }

        except Exception as e:
            print(f"Error fetching internet question: {e}")
        return None

    def generate_easy_questions(self, count):
        fake = Faker()
        questions = []
        for i in range(count):
            templates = [
                (f"What is the largest city in {fake.country()}?",
                [fake.city() for _ in range(4)],
                random.randint(0, 3)),
                (f"What is {random.randint(5, 20)} + {random.randint(5, 20)}?",
                [str(random.randint(10, 30)) for _ in range(3)] +
                [str(random.randint(5, 20) + random.randint(5, 20))],
                -1),
                (f"Which planet is known as the {fake.word()} planet?",
                [fake.word().capitalize() for _ in range(4)],
                random.randint(0, 3)),
                (f"What color is a {fake.word()}?",
                [fake.color_name() for _ in range(4)],
                random.randint(0, 3)),
                (f"How many sides does a {fake.word()} have?",
                [str(random.randint(3, 10)) for _ in range(4)],
                random.randint(0, 3))
            ]
            template = random.choice(templates)
            question = template[0]
            options = template[1]
            answer_idx = template[2]

            if answer_idx == -1:
                answer = options[-1]
            else:
                answer = options[answer_idx]
            questions.append({
                "question": question,
                "options": options,
                "answer": answer
            })
        return questions

    def generate_medium_questions(self, count):
        fake = Faker()
        questions = []
        for i in range(count):
            templates = [
                (f"Who wrote '{fake.catch_phrase()}'?",
                 [fake.name() for _ in range(4)],
                 random.randint(0, 3)),
                (f"What is the chemical symbol for {fake.word().capitalize()}?",
                 [fake.word()[:2].upper() for _ in range(4)],
                 random.randint(0, 3)),
                (f"In what year was {fake.company()} founded?",
                 [str(random.randint(1800, 2023)) for _ in range(4)],
                 random.randint(0, 3)),
                (f"What is the largest {fake.word()} in the world?",
                 [fake.word().capitalize() for _ in range(4)],
                 random.randint(0, 3)),
                (f"How many elements are in the periodic table?",
                 [str(random.randint(50, 200)) for _ in range(4)],
                 random.randint(0, 3))
            ]
            template = random.choice(templates)
            question = template[0]
            options = template[1]
            answer = options[template[2]]
            questions.append({
                "question": question,
                "options": options,
                "answer": answer
            })
        return questions

    def generate_hard_questions(self, count):
        fake = Faker()
        questions = []
        for i in range(count):
            templates = [
                (f"What is the derivative of x^{random.randint(2, 5)}?",
                 [f"{random.randint(1, 5)}x^{random.randint(1, 4)}" for _ in range(3)] +
                 [f"{random.randint(2, 5)}x^{random.randint(1, 4)}"],
                 -1),
                (f"Who developed the theory of {fake.word()}?",
                 [fake.name() for _ in range(4)],
                 random.randint(0, 3)),
                (f"What is the atomic number of {fake.word().capitalize()}?",
                 [str(random.randint(1, 100)) for _ in range(4)],
                 random.randint(0, 3)),
                (f"In quantum physics, what does {fake.word().upper()} stand for?",
                 [fake.word() for _ in range(4)],
                 random.randint(0, 3)),
                (f"What is the {fake.word()} constant approximately equal to?",
                 [str(round(random.uniform(1.0, 10.0), 4)) for _ in range(4)],
                 random.randint(0, 3))
            ]
            template = random.choice(templates)
            question = template[0]
            options = template[1]
            answer_idx = template[2]

            if answer_idx == -1:
                answer = options[-1]
            else:
                answer = options[answer_idx]
            questions.append({
                "question": question,
                "options": options,
                "answer": answer
            })
        return questions

    def generate_googly_questions(self, count):
        fake = Faker()
        questions = []
        for i in range(count):
            templates = [
                (f"If a {fake.word()} is traveling at {random.randint(10, 100)} mph, how long to travel {random.randint(100, 500)} miles?",
                 [f"{random.uniform(1, 10):.2f} hours" for _ in range(3)] +
                 [f"{random.randint(100, 500)/random.randint(10, 100):.2f} hours"],
                 -1),
                (f"What is the next number: {random.randint(1, 10)}, {random.randint(11, 20)}, {random.randint(21, 30)}, __?",
                 [str(random.randint(31, 50)) for _ in range(4)],
                 random.randint(0, 3)),
                (f"Which word doesn't belong: {fake.word()}, {fake.word()}, {fake.word()}, {fake.word()}?",
                 [fake.word() for _ in range(4)],
                 random.randint(0, 3)),
                (f"Solve: ({random.randint(1, 10)} + {random.randint(1, 10)}) × {random.randint(1, 10)}",
                 [str(random.randint(10, 100)) for _ in range(3)] +
                 [str((random.randint(1, 10) + random.randint(1, 10)) * random.randint(1, 10))],
                 -1),
                (f"What is the {fake.word()} of {fake.word()} in {fake.country()}?",
                 [fake.word().capitalize() for _ in range(4)],
                 random.randint(0, 3))
            ]
            template = random.choice(templates)
            question = template[0]
            options = template[1]
            answer_idx = template[2]

            if answer_idx == -1:
                answer = options[-1]
            else:
                answer = options[answer_idx]
            questions.append({
                "question": question,
                "options": options,
                "answer": answer
            })
        return questions

    def create_widgets(self):
        self.title_label = tk.Label(
            self.main_frame,
            text="Quiz Game",
            font=("Arial", 24, "bold")
        )
        self.difficulty_label = tk.Label(
            self.main_frame,
            text="Select Difficulty:",
            font=("Arial", 14)
        )
        self.difficulty_var = tk.StringVar()
        self.difficulty_combobox = ttk.Combobox(
            self.main_frame,
            textvariable=self.difficulty_var,
            values=["Easy", "Medium", "Hard"],
            state="readonly",
            width=15,
            font=("Arial", 12)
        )
        self.difficulty_combobox.set("Easy")
        self.start_button = tk.Button(
            self.main_frame,
            text="Start Quiz",
            command=self.start_quiz,
            font=("Arial", 14),
            padx=20,
            pady=10
        )
        self.theme_button = tk.Button(
            self.main_frame,
            text="Theme",
            font=("Arial", 10),
            width=8,
            command=self.show_theme_menu
        )
        self.create_theme_menu()
        self.score_label = tk.Label(
            self.quiz_frame,
            text=f"Score: {self.score}",
            font=("Arial", 16, "bold"),
            anchor="e"
        )
        self.round_label = tk.Label(
            self.quiz_frame,
            text="",
            font=("Arial", 12),
            anchor="w"
        )
        self.question_label = tk.Label(
            self.quiz_frame,
            text="",
            wraplength=550,
            font=("Arial", 16),
            pady=20
        )
        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.quiz_frame,
                text="",
                command=lambda idx=i: self.check_answer(idx),
                font=("Arial", 12),
                width=40,
                anchor="w",
                pady=10
            )
            self.option_buttons.append(btn)
        self.nav_frame = tk.Frame(self.quiz_frame)
        self.prev_button = tk.Button(
            self.nav_frame,
            text="◀ Previous",
            command=self.prev_question,
            font=("Arial", 12),
            state=tk.DISABLED
        )
        self.next_button = tk.Button(
            self.nav_frame,
            text="Next ▶",
            command=self.next_question,
            font=("Arial", 12),
            state=tk.DISABLED
        )
        self.home_button = tk.Button(
            self.quiz_frame,
            text="Home",
            command=self.show_main_screen,
            font=("Arial", 12)
        )

    def create_theme_menu(self):
        self.theme_menu = tk.Menu(self.root, tearoff=0)
        for theme_name in self.themes:
            self.theme_menu.add_command(
                label=theme_name.capitalize(),
                command=lambda t=theme_name: self.apply_theme(t)
            )

    def show_theme_menu(self):
        """Show the theme selection menu"""
        self.theme_menu.post(
            self.theme_button.winfo_rootx(),
            self.theme_button.winfo_rooty() + self.theme_button.winfo_height()
        )

    def apply_theme(self, theme_name):
        """Apply a color theme to the application"""
        self.current_theme = theme_name
        self.save_theme()
        theme = self.themes[theme_name]
        self.root.config(bg=theme["bg"])
        self.main_frame.config(bg=theme["bg"])
        self.title_label.config(bg=theme["bg"], fg=theme["fg"])
        self.difficulty_label.config(bg=theme["bg"], fg=theme["fg"])
        self.start_button.config(
            bg=theme["accent"],
            fg="white",
            activebackground=theme["accent"],
            activeforeground="white"
        )
        self.quiz_frame.config(bg=theme["bg"])
        self.score_label.config(bg=theme["bg"], fg=theme["fg"])
        self.round_label.config(bg=theme["bg"], fg=theme["fg"])
        self.question_label.config(bg=theme["button"], fg=theme["fg"])
        for btn in self.option_buttons:
            btn.config(
                bg=theme["button"],
                fg=theme["fg"],
                activebackground=theme["button"],
                activeforeground=theme["fg"]
            )
        self.prev_button.config(
            bg=theme["accent"],
            fg="white",
            activebackground=theme["accent"],
            activeforeground="white"
        )
        self.next_button.config(
            bg=theme["accent"],
            fg="white",
            activebackground=theme["accent"],
            activeforeground="white"
        )
        self.home_button.config(
            bg=theme["accent"],
            fg="white",
            activebackground=theme["accent"],
            activeforeground="white"
        )
        self.theme_button.config(
            bg=theme["accent"],
            fg="white",
            activebackground=theme["accent"],
            activeforeground="white"
        )
        self.nav_frame.config(bg=theme["bg"])

    def show_main_screen(self):
        self.quiz_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        self.theme_button.place(relx=0.95, rely=0.05, anchor=tk.NE)
        self.title_label.pack(pady=20)
        self.difficulty_label.pack(pady=10)
        self.difficulty_combobox.pack(pady=5)
        self.start_button.pack(pady=30)

    def start_quiz(self):
        self.selected_difficulty = self.difficulty_var.get()
        self.score = 0
        self.current_question_index = 0
        self.questions_used = []
        self.normal_count_since_googly = 0
        self.question_history = []
        self.main_frame.pack_forget()
        self.quiz_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        self.update_score()
        self.show_question()

    def show_question(self):

        if self.current_question_index < len(self.question_history):
            history_item = self.question_history[self.current_question_index]
            question_data = history_item["data"]
            is_googly_round = history_item["is_googly"]
            user_answer_index = history_item.get("user_answer")
            options = history_item["displayed_options"]
            self.question_label.config(text=question_data["question"])
            for i in range(4):
                self.option_buttons[i].config(
                    text=f"{chr(65+i)}. {options[i]}",
                    bg="SystemButtonFace",
                    fg="black",
                    state=tk.DISABLED
                )

                if options[i] == question_data["answer"]:
                    self.option_buttons[i].config(bg="#4CAF50", fg="white")

                if user_answer_index == i and options[i] != question_data["answer"]:
                    self.option_buttons[i].config(bg="#F44336", fg="white")

            if is_googly_round:
                self.round_label.config(text="GOOGLY ROUND! (Double Points)", fg="red")
            else:
                self.round_label.config(text=f"Normal Round ({self.normal_count_since_googly}/5 to next Googly)", fg="black")
            self.next_button.config(state=tk.NORMAL)
        else:
            is_googly_round = self.normal_count_since_googly == 5

            if is_googly_round and not self.questions["Googly"]:
                is_googly_round = False
                self.normal_count_since_googly = 0
            question_data = None

            if not is_googly_round and self.is_internet_available():
                question_data = self.get_internet_question(self.selected_difficulty)

            if question_data is None:
                source = "Googly" if is_googly_round else self.selected_difficulty
                available_questions = [
                    q for q in self.questions[source]

                    if q not in self.questions_used
                ]

                if not available_questions:
                    self.questions_used = []
                    available_questions = self.questions[source].copy()
                question_data = random.choice(available_questions)
                self.questions_used.append(question_data)
            displayed_options = question_data["options"].copy()
            random.shuffle(displayed_options)
            self.question_history.append({
                "data": question_data,
                "is_googly": is_googly_round,
                "displayed_options": displayed_options,
                "user_answer": None
            })

            if is_googly_round:
                self.normal_count_since_googly = 0
                self.round_label.config(text="GOOGLY ROUND! (Double Points)", fg="red")
            else:
                self.normal_count_since_googly += 1
                self.round_label.config(text=f"Normal Round ({self.normal_count_since_googly}/5 to next Googly)", fg="black")
            self.question_label.config(text=question_data["question"])
            for i in range(4):
                self.option_buttons[i].config(
                    text=f"{chr(65+i)}. {displayed_options[i]}",
                    bg="SystemButtonFace",
                    fg="black",
                    state=tk.NORMAL
                )
            self.next_button.config(state=tk.DISABLED)
        self.update_score()
        self.prev_button.config(state=tk.NORMAL if self.current_question_index > 0 else tk.DISABLED)
        self.score_label.pack(fill=tk.X, pady=5)
        self.round_label.pack(fill=tk.X, pady=5)
        self.question_label.pack(fill=tk.X, pady=20)
        for btn in self.option_buttons:
            btn.pack(fill=tk.X, pady=5)
        self.nav_frame.pack(fill=tk.X, pady=10)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button.pack(side=tk.RIGHT, padx=5)
        self.home_button.pack(side=tk.BOTTOM, pady=10)

    def check_answer(self, option_idx):
        selected_text = self.option_buttons[option_idx].cget("text")[3:]
        question_data = self.question_history[self.current_question_index]["data"]
        correct_answer = question_data["answer"]
        self.question_history[self.current_question_index]["user_answer"] = option_idx
        for btn in self.option_buttons:
            btn.config(state=tk.DISABLED)
        for i in range(4):
            option_text = self.option_buttons[i].cget("text")[3:]

            if option_text == correct_answer:
                self.option_buttons[i].config(bg="#4CAF50", fg="white")

        if selected_text == correct_answer:
            points = 2 if self.question_history[self.current_question_index]["is_googly"] else 1
            self.score += points
            self.update_score()
        else:
            self.option_buttons[option_idx].config(bg="#F44336", fg="white")
        self.next_button.config(state=tk.NORMAL)

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score} | Question: {self.current_question_index+1}")

    def next_question(self):
        self.current_question_index += 1
        self.show_question()

    def prev_question(self):

        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.show_question()

    def save_window_geometry(self):
        """Save window geometry and last transaction type"""
        config = configparser.ConfigParser()
        
        # Geometry section
        config["Geometry"] = {
            "size": self.root.geometry(),
            "state": self.root.state()
        }

        # config_file = 'config.ini'
        
        with open(self.config_file, "w") as f:
            config.write(f)

    def load_window_geometry(self):
        if os.path.exists(self.config_file):
            config = configparser.ConfigParser()
            config.read(self.config_file)
            if "Geometry" in config:
                geometry = config["Geometry"].get("size", "")
                state = config["Geometry"].get("state", "normal")
                if geometry:
                    self.root.geometry(geometry)
                    self.root.update_idletasks()
                    self.root.update()
                if state == "zoomed":
                    self.root.state("zoomed")  # Restore maximized state
                elif state == "iconic":
                    self.root.iconify()

    def on_close(self):
        """Handler for window close event"""
        self.save_window_geometry()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
