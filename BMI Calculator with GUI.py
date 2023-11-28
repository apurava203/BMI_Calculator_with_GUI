import tkinter as tk
from tkinter import messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# SQLite database setup
conn = sqlite3.connect('bmi_data.db')
c = conn.cursor()
c.execute('''
          CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT,
              weight REAL,
              height REAL,
              bmi REAL,
              date TEXT
          )
          ''')
conn.commit()

class BMIApp:
    def __init__(self, master):
        self.master = master
        self.master.title("BMI Calculator")

        self.name_var = tk.StringVar()
        self.weight_var = tk.DoubleVar()
        self.height_var = tk.DoubleVar()

        tk.Label(master, text="Name:").grid(row=0, column=0, sticky="e")
        tk.Entry(master, textvariable=self.name_var).grid(row=0, column=1)
        tk.Label(master, text="Weight (kg):").grid(row=1, column=0, sticky="e")
        tk.Entry(master, textvariable=self.weight_var).grid(row=1, column=1)
        tk.Label(master, text="Height (m):").grid(row=2, column=0, sticky="e")
        tk.Entry(master, textvariable=self.height_var).grid(row=2, column=1)

        tk.Button(master, text="Calculate BMI", command=self.calculate_bmi).grid(row=3, column=0, columnspan=2)
        tk.Button(master, text="Plot BMI Trends", command=self.plot_bmi_trends).grid(row=4, column=0, columnspan=2)

    def calculate_bmi(self):
        try:
            name = self.name_var.get()
            weight = self.weight_var.get()
            height = self.height_var.get()

            if not name:
                name = "Unknown"

            if weight <= 0 or height <= 0:
                raise ValueError("Weight and height must be positive numbers.")

            bmi = weight / (height ** 2)
            bmi = round(bmi, 2)

            category = self.get_bmi_category(bmi)

            messagebox.showinfo("BMI Result", f"Name: {name}\nBMI: {bmi}\nCategory: {category}")

            self.save_to_database(name, weight, height, bmi)
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 24.9:
            return "Normal Weight"
        elif 25 <= bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"

    def save_to_database(self, name, weight, height, bmi):
        date = "current_date"  # Replace with the actual date
        c.execute('''
                  INSERT INTO users (name, weight, height, bmi, date)
                  VALUES (?, ?, ?, ?, ?)
                  ''', (name, weight, height, bmi, date))
        conn.commit()

    def plot_bmi_trends(self):
        c.execute('SELECT date, bmi FROM users WHERE name = ?', (self.name_var.get(),))
        data = c.fetchall()

        if not data:
            messagebox.showinfo("Information", "No data available for plotting.")
            return

        dates, bmis = zip(*data)
        fig, ax = plt.subplots()
        ax.plot(dates, bmis, marker='o', linestyle='-')
        ax.set_title("BMI Trends")
        ax.set_xlabel("Date")
        ax.set_ylabel("BMI")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.master)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=5, column=0, columnspan=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = BMIApp(root)
    root.mainloop()

conn.close()
