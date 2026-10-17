import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from join_engine import join_tables, read_table


def open_join_window(parent):
    root = tk.Toplevel(parent)
    root.title("Excel Merger Pro | JOIN Tables")
    root.geometry("850x600")
    root.minsize(850, 600)
    root.configure(bg="#1C0D29")

    left_file = tk.StringVar(master=root)
    right_file = tk.StringVar(master=root)
    output_folder = tk.StringVar(master=root)
    join_type = tk.StringVar(master=root, value="left")
    readable_ids = tk.BooleanVar(master=root, value=False)
    left_key = tk.StringVar(master=root)
    right_key = tk.StringVar(master=root)

    
    def load_columns(file_path, combo, variable):
        combo["values"] = []
        variable.set("")

        try:
            df = read_table(file_path)
            columns = df.columns.tolist()

            combo["values"] = columns

            if columns:
                variable.set(columns[0])

        except Exception as error:
            messagebox.showerror(
                "Error reading columns",
                str(error),
                parent=root
            )

    def select_left():
        path = filedialog.askopenfilename(
            parent=root,
            filetypes=[("Data files", "*.csv *.xlsx")]
        )

        if path:
            left_file.set(path)
            load_columns(path, left_key_combo, left_key)

    def select_right():
        path = filedialog.askopenfilename(
            parent=root,
            filetypes=[("Data files", "*.csv *.xlsx")]
        )

        if path:
            right_file.set(path)
            load_columns(path, right_key_combo, right_key)

    def select_output():
        path = filedialog.askdirectory(parent=root)

        if path:
            output_folder.set(path)

    def run_join():
        if not all([
            left_file.get(),
            right_file.get(),
            output_folder.get()
        ]):
            messagebox.showwarning(
                "Missing information",
                "Select both files and an output folder.",
                parent=root
            )
            return

        if not left_key.get() or not right_key.get():
            messagebox.showwarning(
                "Missing JOIN columns",
                "Select a JOIN column for each file.",
                parent=root
            )
            return

        try:
            join_tables(
                left_file.get(),
                right_file.get(),
                output_folder.get(),
                join_type=join_type.get(),
                left_key=left_key.get(),
                right_key=right_key.get(),
                readable_ids=readable_ids.get() 
            )

            messagebox.showinfo(
                "Success",
                "JOIN completed successfully!",
                parent=root
            )

        except Exception as error:
            messagebox.showerror(
                "JOIN failed",
                str(error),
                parent=root
            )

    tk.Label(
        root,
        text="JOIN TABLES",
        bg="#1C0D29",
        fg="white",
        font=("Segoe UI", 24, "bold")
    ).pack(pady=24)

    def add_file_field(label, variable, command):
        frame = tk.Frame(root, bg="#1C0D29")
        frame.pack(fill="x", padx=35, pady=8)

        tk.Label(
            frame,
            text=label,
            bg="#1C0D29",
            fg="white",
            width=13,
            anchor="w"
        ).pack(side="left")

        tk.Entry(
            frame,
            textvariable=variable,
            font=("Segoe UI", 10)
        ).pack(side="left", fill="x", expand=True)

        tk.Button(
            frame,
            text="Browse",
            command=command
        ).pack(side="left", padx=8)

    add_file_field("Left File", left_file, select_left)
    add_file_field("Right File", right_file, select_right)
    add_file_field("Output Folder", output_folder, select_output)

    tk.Label(
        root,
        text="JOIN COLUMNS",
        bg="#1C0D29",
        fg="white",
        font=("Segoe UI", 12, "bold")
    ).pack(pady=(15, 5))

    left_key_combo = ttk.Combobox(
        root,
        textvariable=left_key,
        state="readonly",
        width=35
    )
    left_key_combo.pack(pady=5)

    right_key_combo = ttk.Combobox(
        root,
        textvariable=right_key,
        state="readonly",
        width=35
    )
    right_key_combo.pack(pady=5)

    tk.Label(
        root,
        text="JOIN Type",
        bg="#1C0D29",
        fg="white"
    ).pack(pady=(15, 5))

    ttk.Combobox(
        root,
        textvariable=join_type,
        values=["left", "inner"],
        state="readonly",
        width=20
    ).pack()

    tk.Checkbutton(
        root,
        text="Generate Readable IDs (ORD-0001 / CUS-0001)",
        variable=readable_ids,
        bg="#1C0D29",
        fg="white",
        selectcolor="#30183F",
        activebackground="#1C0D29",
        activeforeground="white",
        font=("Segoe UI", 11)
    ).pack(pady=10)
    
    tk.Button(
        root,
        text="START JOIN",
        command=run_join,
        bg="#A336C1",
        fg="white",
        font=("Segoe UI", 13, "bold"),
        padx=30,
        pady=12
    ).pack(pady=25)

