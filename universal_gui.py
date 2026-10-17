from __future__ import annotations

import os
import queue
import threading
import tkinter as tk

from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from universal_merge import inspect_sources, merge_files


# =====================================
# PURPLE THEME
# =====================================

BG = "#1C0D29"
CARD = "#30183F"
FIELD = "#452553"
PURPLE = "#A936C1"
WHITE = "#FFFFFF"
MUTED = "#D3ACDF"


class App:

    def __init__(self, root):
        self.root = root

        root.title("Excel Merger Pro v3.3 | MERGE Files")
        root.geometry("1160x735")
        root.minsize(1000, 670)
        root.configure(bg=BG)

        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()

        self.status = tk.StringVar(
            value="Ready to merge"
        )

        self.stats = [
            tk.StringVar(value="--")
            for _ in range(3)
        ]

        self.source_columns = {}
        self.mappings = {}
        self.column_flags = {}
        self.column_order = []

        self.events = queue.Queue()
        self.busy = False

        self.build()

        root.after(
            120,
            self.poll_events
        )

    # =====================================
    # REUSABLE UI ELEMENTS
    # =====================================

    def label(
        self,
        parent,
        text,
        size=12,
        bold=False,
        color=WHITE
    ):
        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=color,
            font=(
                "Segoe UI",
                size,
                "bold" if bold else "normal"
            )
        )

    def button(
        self,
        parent,
        text,
        command,
        color=PURPLE
    ):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=WHITE,
            activebackground="#C65CE0",
            activeforeground=WHITE,
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=8
        )

    # =====================================
    # MAIN WINDOW DESIGN
    # =====================================

    def build(self):

        self.label(
            self.root,
            "EXCEL MERGER  PRO",
            28,
            True
        ).pack(pady=(18, 0))

        self.label(
            self.root,
            "CSV & XLSX File Merger  |  "
            "Column Mapping  |  Automated Excel Reports",
            12,
            color=MUTED
        ).pack(pady=(0, 15))

        paths = tk.Frame(
            self.root,
            bg=BG
        )

        paths.pack(
            fill="x",
            padx=38
        )

        fields = [
            (
                0,
                "INPUT FOLDER",
                self.input_folder
            ),
            (
                1,
                "OUTPUT FOLDER",
                self.output_folder
            )
        ]

        for col, title, variable in fields:

            block = tk.Frame(
                paths,
                bg=CARD,
                padx=12,
                pady=12
            )

            block.grid(
                row=0,
                column=col,
                padx=8,
                sticky="ew"
            )

            paths.grid_columnconfigure(
                col,
                weight=1
            )

            self.label(
                block,
                title,
                12,
                True
            ).pack(anchor="w")

            line = tk.Frame(
                block,
                bg=CARD
            )

            line.pack(
                fill="x",
                pady=(7, 0)
            )

            entry = tk.Entry(
                line,
                textvariable=variable,
                bg=FIELD,
                fg=WHITE,
                insertbackground=WHITE,
                font=("Segoe UI", 12),
                relief="flat"
            )

            entry.pack(
                side="left",
                fill="x",
                expand=True,
                ipady=9
            )

            self.button(
                line,
                "Browse",
                lambda v=variable: self.browse(v)
            ).pack(
                side="right",
                padx=(8, 0)
            )

        # =================================
        # ACTION BUTTONS
        # =================================

        tools = tk.Frame(
            self.root,
            bg=BG
        )

        tools.pack(pady=(14, 8))

        self.button(
            tools,
            "1  INSPECT & MAP COLUMNS",
            self.inspect
        ).pack(
            side="left",
            padx=8
        )

        self.merge_btn = self.button(
            tools,
            "2  START MERGE",
            self.start
        )

        self.merge_btn.pack(
            side="left",
            padx=8
        )

        self.button(
            tools,
            "OPEN REPORT",
            self.open_report,
            color="#593468"
        ).pack(
            side="left",
            padx=8
        )

        self.label(
            self.root,
            "Column mapping: choose an output name "
            "for each input column.",
            11,
            color=MUTED
        ).pack()

        # =================================
        # SCROLLABLE MAPPING PANEL
        # =================================

        body = tk.Frame(
            self.root,
            bg=CARD
        )

        body.pack(
            fill="both",
            expand=True,
            padx=46,
            pady=10
        )

        self.canvas = tk.Canvas(
            body,
            bg=CARD,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            body,
            orient="vertical",
            command=self.canvas.yview
        )

        self.inner = tk.Frame(
            self.canvas,
            bg=CARD
        )

        self.inner.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0),
            window=self.inner,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.label(
            self.inner,
            "Choose folders, then click "
            "INSPECT & MAP COLUMNS.",
            12,
            color=MUTED
        ).pack(
            padx=18,
            pady=20
        )

        # =================================
        # FOOTER AND STATISTICS
        # =================================

        footer = tk.Frame(
            self.root,
            bg=BG
        )

        footer.pack(
            fill="x",
            padx=54,
            pady=(0, 12)
        )

        self.label(
            footer,
            "Status:",
            11,
            True
        ).pack(side="left")

        tk.Label(
            footer,
            textvariable=self.status,
            bg=BG,
            fg="#E6B5F3",
            font=("Segoe UI", 11)
        ).pack(
            side="left",
            padx=8
        )

        stat_fields = [
            ("Files", self.stats[0]),
            ("Clean Rows", self.stats[1]),
            ("Excluded", self.stats[2])
        ]

        for title, variable in stat_fields:

            section = tk.Frame(
                footer,
                bg=CARD,
                padx=15,
                pady=7
            )

            section.pack(
                side="right",
                padx=5
            )

            tk.Label(
                section,
                textvariable=variable,
                bg=CARD,
                fg=WHITE,
                font=("Segoe UI", 16, "bold")
            ).pack()

            self.label(
                section,
                title,
                10,
                color=MUTED
            ).pack()

    # =====================================
    # FOLDER SELECTION
    # =====================================

    def browse(self, variable):

        path = filedialog.askdirectory()

        if not path:
            return

        variable.set(path)

        if variable is self.input_folder:
            self.source_columns = {}
            self.mappings = {}
            self.column_flags = {}
            self.column_order = []
            for child in self.inner.winfo_children():
                child.destroy()

            self.label(
                self.inner,
                "Input folder changed. Click INSPECT & MAP COLUMNS.",
                12,
                color=MUTED
            ).pack(padx=18, pady=20)
            self.status.set(
                "Input changed. Inspect columns again."
            )

    # =====================================
    # INSPECT AND MAP COLUMNS
    # =====================================

    def inspect(self):

        if self.busy:
            return

        try:
            self.source_columns = inspect_sources(
                Path(self.input_folder.get())
            )

            if not self.source_columns:
                raise ValueError(
                    "No CSV or XLSX files found"
                )

        except Exception as error:
            messagebox.showerror(
                "Inspection failed",
                str(error)
            )
            return

        for child in self.inner.winfo_children():
            child.destroy()

        self.mappings = {}
        self.column_flags = {}
        self.column_order = []

        row = tk.Frame(
            self.inner,
            bg=CARD
        )

        row.pack(
            fill="x",
            padx=12,
            pady=5
        )

        self.label(
            row,
            "OUTPUT COLUMNS",
            12,
            True
        ).pack(side="left")

        self.label(
            row,
            "Select, deselect, and reorder columns.",
            10,
            color=MUTED
        ).pack(
            side="left",
            padx=12
        )

        self.order_box = tk.Listbox(
            self.inner,
            selectmode="browse",
            height=5,
            bg=FIELD,
            fg=WHITE,
            selectbackground=PURPLE,
            font=("Segoe UI", 12),
            relief="flat"
        )

        self.order_box.pack(
            fill="x",
            padx=18,
            pady=4
        )

        order_actions = tk.Frame(
            self.inner,
            bg=CARD
        )

        order_actions.pack(
            anchor="e",
            padx=18
        )

        self.button(
            order_actions,
            "Up ↑",
            lambda: self.move_order(-1),
            color="#593468"
        ).pack(
            side="left",
            padx=3
        )

        self.button(
            order_actions,
            "Down ↓",
            lambda: self.move_order(1),
            color="#593468"
        ).pack(
            side="left",
            padx=3
        )

        self.output_chooser = tk.Frame(
            self.inner,
            bg=CARD
        )

        self.output_chooser.pack(
            fill="x",
            padx=18,
            pady=(7, 15)
        )

        for filename, columns in self.source_columns.items():

            self.label(
                self.inner,
                filename,
                13,
                True,
                color="#E6B5F3"
            ).pack(
                anchor="w",
                padx=18,
                pady=(10, 2)
            )

            self.mappings[filename] = {}

            for column in columns:

                line = tk.Frame(
                    self.inner,
                    bg=CARD
                )

                line.pack(
                    fill="x",
                    padx=22,
                    pady=2
                )

                tk.Label(
                    line,
                    text=column,
                    bg=CARD,
                    fg=WHITE,
                    font=("Segoe UI", 11),
                    width=28,
                    anchor="w"
                ).pack(side="left")

                self.label(
                    line,
                    "→",
                    12,
                    color=MUTED
                ).pack(
                    side="left",
                    padx=5
                )

                variable = tk.StringVar(
                    value=column
                )

                tk.Entry(
                    line,
                    textvariable=variable,
                    bg=FIELD,
                    fg=WHITE,
                    insertbackground=WHITE,
                    font=("Segoe UI", 11),
                    relief="flat",
                    width=28
                ).pack(
                    side="left",
                    ipady=5
                )

                self.mappings[filename][column] = variable

        self.button(
            self.inner,
            "REFRESH OUTPUT COLUMN CHOICES",
            self.refresh_output_columns
        ).pack(pady=10)

        self.refresh_output_columns()

        self.status.set(
            f"Inspected {len(self.source_columns)} files."
        )

    # =====================================
    # OUTPUT COLUMN CHOICES
    # =====================================

    def refresh_output_columns(self):

        old_flags = {
            name: variable.get()
            for name, variable in self.column_flags.items()
        }

        names = list(
            dict.fromkeys(
                variable.get().strip()
                for mappings in self.mappings.values()
                for variable in mappings.values()
            )
        )

        names = [
            name for name in names
            if name and name != "Source File"
        ]

        names.append("Source File")

        self.column_order = [
            name for name in self.column_order
            if name in names
        ] + [
            name for name in names
            if name not in self.column_order
        ]

        for child in self.output_chooser.winfo_children():
            child.destroy()

        self.column_flags = {}

        for name in names:

            variable = tk.BooleanVar(
                value=old_flags.get(name, True)
            )

            self.column_flags[name] = variable

            tk.Checkbutton(
                self.output_chooser,
                text=name,
                variable=variable,
                bg=CARD,
                fg=WHITE,
                selectcolor=FIELD,
                activebackground=CARD,
                activeforeground=WHITE,
                font=("Segoe UI", 11)
            ).pack(
                side="left",
                padx=8
            )

        self.redraw_order()

    # =====================================
    # REORDER COLUMNS
    # =====================================

    def redraw_order(self):

        self.order_box.delete(
            0,
            "end"
        )

        for name in self.column_order:
            self.order_box.insert(
                "end",
                name
            )

    def move_order(self, delta):

        selection = self.order_box.curselection()

        if not selection:
            return

        index = selection[0]
        new_index = index + delta

        if 0 <= new_index < len(self.column_order):

            self.column_order[index], \
            self.column_order[new_index] = (
                self.column_order[new_index],
                self.column_order[index]
            )

            self.redraw_order()

            self.order_box.selection_set(
                new_index
            )

    # =====================================
    # START MERGING
    # =====================================

    def start(self):

        if self.busy:
            return

        source = Path(
            self.input_folder.get()
        )

        output = Path(
            self.output_folder.get()
        )

        if not source.is_dir() or not output.is_dir():
            messagebox.showerror(
                "Missing folder",
                "Choose valid input and output folders."
            )
            return

        if not self.source_columns:
            messagebox.showwarning(
                "Inspect first",
                "Click INSPECT & MAP COLUMNS first."
            )
            return

        mapping = {
            filename: {
                column: variable.get().strip()
                for column, variable in column_map.items()
            }
            for filename, column_map in self.mappings.items()
        }

        current_names = list(
            dict.fromkeys(
                name
                for columns in mapping.values()
                for name in columns.values()
            )
        )

        current_names.append("Source File")

        if set(current_names) != set(self.column_order):
            messagebox.showwarning(
                "Refresh",
                "Mappings changed. Refresh output columns."
            )
            return

        selected = [
            name
            for name in self.column_order
            if self.column_flags[name].get()
        ]

        if not selected:
            messagebox.showwarning(
                "No columns",
                "Select at least one output column."
            )
            return

        self.busy = True

        self.merge_btn.configure(
            state="disabled"
        )

        self.status.set("Starting...")

        for stat in self.stats:
            stat.set("--")

        threading.Thread(
            target=self.worker,
            args=(
                str(source),
                str(output),
                mapping,
                selected
            ),
            daemon=True
        ).start()

    # =====================================
    # BACKGROUND PROCESSING
    # =====================================

    def worker(
        self,
        source,
        output,
        mapping,
        selected
    ):

        try:
            result = merge_files(
                source,
                output,
                mapping=mapping,
                selected=selected,
                progress=lambda message: self.events.put(
                    ("progress", message)
                )
            )

            self.events.put(
                ("success", result)
            )

        except Exception as error:
            self.events.put(
                ("error", str(error))
            )

    # =====================================
    # UPDATE GUI FROM WORKER
    # =====================================

    def poll_events(self):

        try:
            while True:

                kind, payload = self.events.get_nowait()

                if kind == "progress":
                    self.status.set(payload)

                elif kind == "success":

                    self.busy = False

                    self.merge_btn.configure(
                        state="normal"
                    )

                    self.stats[0].set(
                        f"{payload['files']:,}"
                    )

                    self.stats[1].set(
                        f"{payload['clean_rows']:,}"
                    )

                    self.stats[2].set(
                        f"{payload['excluded_rows']:,}"
                    )

                    self.status.set(
                    "Merge completed successfully!"
                    )

                    messagebox.showinfo(
                        "Success",
                        "Excel report created:\n"
                        f"{payload['report']}"
                    )

                elif kind == "error":

                    self.busy = False

                    self.merge_btn.configure(
                        state="normal"
                    )

                    self.status.set(
                        "Merge failed"
                    )

                    messagebox.showerror(
                        "Merge failed",
                        payload
                    )

        except queue.Empty:
            pass

        self.root.after(
            120,
            self.poll_events
        )

    # =====================================
    # OPEN EXCEL REPORT
    # =====================================

    def open_report(self):

        report = (
            Path(self.output_folder.get())
            / "Universal_Merged.xlsx"
        )

        if not report.is_file():
            messagebox.showwarning(
                "Not found",
                "No report in the selected output folder."
            )
            return

        try:
            os.startfile(str(report))

        except OSError as error:
            messagebox.showerror(
                "Open report",
                str(error)
            )


# =====================================
# RUN APPLICATION
# =====================================

if __name__ == "__main__":

    window = tk.Tk()

    App(window)

    window.mainloop()
