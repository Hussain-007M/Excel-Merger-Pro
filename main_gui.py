import tkinter as tk


def open_merge():
    from universal_gui import App

    window = tk.Toplevel(root)
    App(window)


def open_join():
    from join_gui import open_join_window

    open_join_window(root)


root = tk.Tk()
root.title("Excel Merger Pro v3.3")
root.geometry("560x460")
root.minsize(560, 460)
root.configure(bg="#1C0D29")


tk.Label(
    root,
    text="EXCEL MERGER PRO",
    font=("Segoe UI", 22, "bold"),
    fg="white",
    bg="#1C0D29"
).pack(pady=35)


tk.Button(
    root,
    text="MERGE FILES",
    command=open_merge,
    bg="#A936C1",
    fg="white",
    font=("Segoe UI", 15, "bold"),
    width=22,
    pady=12
).pack(pady=10)


tk.Label(
    root,
    text="Combine CSV & Excel files into one report",
    font=("Segoe UI", 10),
    fg="#D3ACDF",
    bg="#1C0D29"
).pack()


tk.Button(
    root,
    text="JOIN TABLES",
    command=open_join,
    bg="#A936C1",
    fg="white",
    font=("Segoe UI", 15, "bold"),
    width=22,
    pady=12
).pack(pady=10)


tk.Label(
    root,
    text="Connect two tables using matching columns",
    font=("Segoe UI", 10),
    fg="#D3ACDF",
    bg="#1C0D29"
).pack()


root.mainloop()
