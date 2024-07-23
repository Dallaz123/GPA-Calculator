import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

class ImprovedGPACalculator:
    def __init__(self, master):
        self.master = master
        self.master.title("GPA Calculator")
        self.master.geometry("800x600")
        self.master.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TEntry", fieldbackground="white")
        self.style.configure("Treeview", rowheight=25, fieldbackground="white")
        self.style.map("TButton", background=[("active", "#45a049")])

        self.semesters = {f"Semester {i}": [] for i in range(1, 9)}
        self.current_semester = "Semester 1"

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Semester tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.semester_frames = {}
        for semester in self.semesters.keys():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=semester)
            self.semester_frames[semester] = frame
            self.create_semester_widgets(frame, semester)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Data management
        data_frame = ttk.Frame(main_frame)
        data_frame.pack(fill=tk.X, pady=10)

        ttk.Button(data_frame, text="Save Data", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(data_frame, text="Load Data", command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(data_frame, text="Calculate Overall GPA", command=self.calculate_overall_gpa).pack(side=tk.RIGHT, padx=5)

        self.overall_gpa_label = ttk.Label(main_frame, text="Overall GPA: ")
        self.overall_gpa_label.pack(pady=10)

    def create_semester_widgets(self, frame, semester):
        # Course entry
        course_frame = ttk.LabelFrame(frame, text="Add Course", padding="10")
        course_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10, padx=10)

        ttk.Label(course_frame, text="Course Name:").grid(row=0, column=0, padx=5, pady=5)
        course_entry = ttk.Entry(course_frame)
        course_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(course_frame, text="Credit Hours:").grid(row=1, column=0, padx=5, pady=5)
        credit_entry = ttk.Entry(course_frame)
        credit_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(course_frame, text="Grade:").grid(row=2, column=0, padx=5, pady=5)
        grade_combobox = ttk.Combobox(course_frame, values=['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F'])
        grade_combobox.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(course_frame, text="Add Course", command=lambda: self.add_course(semester, course_entry, credit_entry, grade_combobox)).grid(row=3, column=0, columnspan=2, pady=10)

        # Course list
        course_list = ttk.Treeview(frame, columns=('Course', 'Credits', 'Grade'), show='headings')
        course_list.heading('Course', text='Course')
        course_list.heading('Credits', text='Credits')
        course_list.heading('Grade', text='Grade')
        course_list.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        # GPA calculation
        gpa_frame = ttk.LabelFrame(frame, text="Semester GPA", padding="10")
        gpa_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10, padx=10)

        ttk.Button(gpa_frame, text="Calculate GPA", command=lambda: self.calculate_semester_gpa(semester)).grid(row=0, column=0, pady=10)

        semester_gpa_label = ttk.Label(gpa_frame, text="Semester GPA: ")
        semester_gpa_label.grid(row=1, column=0, pady=5)

        # Store references
        self.semester_frames[semester] = {
            'course_entry': course_entry,
            'credit_entry': credit_entry,
            'grade_combobox': grade_combobox,
            'course_list': course_list,
            'semester_gpa_label': semester_gpa_label
        }

    def on_tab_change(self, event):
        self.current_semester = self.notebook.tab(self.notebook.select(), "text")
        self.update_course_list(self.current_semester)

    def add_course(self, semester, course_entry, credit_entry, grade_combobox):
        course = course_entry.get()
        credits = credit_entry.get()
        grade = grade_combobox.get()

        if not course or not credits or not grade:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            credits = float(credits)
            if credits <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Credit hours must be a positive number")
            return

        self.semesters[semester].append((course, credits, grade))
        self.update_course_list(semester)

        # Clear entries
        course_entry.delete(0, 'end')
        credit_entry.delete(0, 'end')
        grade_combobox.set('')

    def update_course_list(self, semester):
        course_list = self.semester_frames[semester]['course_list']
        course_list.delete(*course_list.get_children())
        for course in self.semesters[semester]:
            course_list.insert('', 'end', values=course)

    def calculate_semester_gpa(self, semester):
        grade_points = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0
        }

        total_credits = 0
        total_grade_points = 0

        for course in self.semesters[semester]:
            _, credits, grade = course
            total_credits += credits
            total_grade_points += credits * grade_points[grade]

        if total_credits > 0:
            semester_gpa = total_grade_points / total_credits
            self.semester_frames[semester]['semester_gpa_label'].config(text=f"Semester GPA: {semester_gpa:.2f}")
        else:
            self.semester_frames[semester]['semester_gpa_label'].config(text="Semester GPA: N/A")

    def calculate_overall_gpa(self):
        grade_points = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0
        }

        total_credits = 0
        total_grade_points = 0

        for semester in self.semesters.values():
            for course in semester:
                _, credits, grade = course
                total_credits += credits
                total_grade_points += credits * grade_points[grade]

        if total_credits > 0:
            overall_gpa = total_grade_points / total_credits
            self.overall_gpa_label.config(text=f"Overall GPA: {overall_gpa:.2f}")
        else:
            self.overall_gpa_label.config(text="Overall GPA: N/A")

    def save_data(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json")
        if filename:
            with open(filename, 'w') as f:
                json.dump(self.semesters, f)
            messagebox.showinfo("Success", "Data saved successfully.")

    def load_data(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, 'r') as f:
                self.semesters = json.load(f)
            self.update_all_course_lists()
            messagebox.showinfo("Success", "Data loaded successfully.")

    def update_all_course_lists(self):
        for semester in self.semesters.keys():
            self.update_course_list(semester)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImprovedGPACalculator(root)
    root.mainloop()