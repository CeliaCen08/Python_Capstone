import tkinter as tk
import time
import threading
import random
import mysql.connector as con


def get_db_connection():
    cnx = con.connect(user='root', password='Abc2463762@',
                      host='localhost', database='typing_speed')
    return cnx


def setup_database():
    cnx = get_db_connection()
    cursor = cnx.cursor()

    # Create table if it does not exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS scores (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        score DECIMAL(10, 2) NOT NULL)''')

    cnx.commit()
    cnx.close()


class TypeSpeedGUI:
    def __init__(self):
        setup_database()
        self.root = tk.Tk()
        self.root.title("Typing Speed Application")
        self.root.geometry("800x600")

        self.texts = open("text.txt", "r").read().split("\n")

        self.frame = tk.Frame(self.root)

        self.sample_label = tk.Label(self.frame, text=random.choice(self.texts), font=("Helvetica", 18))
        self.sample_label.grid(row=0, column=0, columnspan=2, padx=5, pady=10)

        self.input_entry = tk.Entry(self.frame, width=40, font=("Helvetica", 24))
        self.input_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        self.input_entry.bind("<KeyRelease>", self.start)

        self.WPM = tk.StringVar()

        self.speed_label = tk.Label(self.frame, text="Speed: \n0.00 CPS\n0.00 CPM\n0.00 WPS\n0.00 WPM",
                                    font=("Helvetica", 24))
        self.speed_label.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        self.reset_button = tk.Button(self.frame, text="Reset", font=("Helvetica", 24), command=self.reset)
        self.reset_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        self.show_scores_button = tk.Button(self.frame, text="Show Scores", font=("Helvetica", 24),
                                            command=self.show_scores)
        self.show_scores_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

        self.frame.pack(expand=True)
        self.counter = 0
        self.running = False

        self.root.mainloop()

    def show_scores(self):
        try:
            cnx = get_db_connection()
            cursor = cnx.cursor()

            cursor.execute("SELECT * FROM scores ORDER BY score DESC")
            scores = cursor.fetchall()

            scores_window = tk.Toplevel(self.root)
            scores_window.title("Scores")

            scores_text = "\n".join([f"{score[1]}: {score[2]}" for score in scores])
            tk.Label(scores_window, text=scores_text).pack(pady=20)

            cnx.close()
        except Exception as e:
            print(f"An error occurred: {e}")

    def check_completion(self):
        if self.input_entry.get() == self.sample_label.cget('text'):
            self.input_entry.config(fg="green")
            self.end_test()

    def end_test(self):
        self.running = False

    def start(self, event):
        if not self.running:
            if not event.keycode in [16, 17, 18]:  # Check for control, shift, alt keys
                self.running = True
                t = threading.Thread(target=self.time_thread)
                t.start()
        if not self.sample_label.cget('text').startswith(self.input_entry.get()):
            self.input_entry.config(fg="red")
        else:
            self.input_entry.config(fg="black")

        self.check_completion()

    def time_thread(self):
        while self.running:
            time.sleep(0.1)
            self.counter += 0.1
            cps = len(self.input_entry.get()) / self.counter
            cpm = cps * 60
            wps = len(self.input_entry.get().split(" ")) / self.counter
            wpm = wps * 60
            self.speed_label.config(text=f"Speed: \n{cps:.2f} CPS\n{cpm:.2f} CPM\n{wps:.2f} WPS\n{wpm:.2f} WPM")
            self.WPM.set("{:.2f}".format(wpm))

    def reset(self):
        self.running = False
        self.counter = 0
        self.speed_label.config(text="Speed: \n0.00 CPS\n0.00 CPM\n0.00 WPS\n0.00 WPM")
        self.sample_label.config(text=random.choice(self.texts))
        self.input_entry.delete(0, tk.END)

        name_dialog = tk.Toplevel(self.root)
        name_dialog.title("Enter Name")
        name_label = tk.Label(name_dialog, text="Please enter your name:")
        name_label.pack()
        self.name_entry = tk.Entry(name_dialog)
        self.name_entry.pack()
        submit_button = tk.Button(name_dialog, text="Submit", command=self.submit_name)
        submit_button.pack()

    def submit_name(self):
        try:
            cnx = get_db_connection()
            cursor = cnx.cursor()

            cursor.execute("INSERT INTO scores (name, score) VALUES (%s, %s)", (self.name_entry.get(),
                                                                                self.WPM.get()))

            cnx.commit()
            cnx.close()
        except Exception as e:
            print(f"An error occurred while saving score: {e}")


TypeSpeedGUI()
