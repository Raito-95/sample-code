import tkinter as tk
from tkinter import messagebox, simpledialog

from Applications.AlgorithmsLab.GradeSystem import GradeSystemDriver


class GradeSystemGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Grade System GUI")
        self.driver = GradeSystemDriver()
        self.driver.load_data()

        self.display = tk.Text(master, width=60, height=20)
        self.display.pack(padx=10, pady=10)

        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Show All", command=self.show_all).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Add", command=self.add_record).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_record).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save", command=self.save_data).pack(side=tk.LEFT, padx=5)

        self.show_all()

    def show_all(self):
        self.display.delete("1.0", tk.END)
        for student_no, subjects in self.driver.grade_system.student_grade.items():
            items = " ".join(f"{sub} {score}" for sub, score in subjects.items())
            self.display.insert(tk.END, f"{student_no}: {items}\n")

    def add_record(self):
        student_data = simpledialog.askstring(
            "Add Record",
            "Enter student ID and subject/score pairs (e.g., '97531 DS 80 DM 80'):",
        )
        if student_data:
            self.driver.grade_system.insert_grade(student_data)
            self.show_all()
            messagebox.showinfo("Success", "Record added.")

    def delete_record(self):
        student_no = simpledialog.askstring("Delete Record", "Enter student ID:")
        if student_no:
            self.driver.grade_system.delete_grade(student_no)
            self.show_all()
            messagebox.showinfo("Success", "Record deleted.")

    def save_data(self):
        self.driver.save_data()
        messagebox.showinfo("Saved", f"Data saved to {self.driver.file_path}")


def main():
    root = tk.Tk()
    app = GradeSystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
