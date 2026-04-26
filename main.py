import customtkinter as ctk
from PIL import Image
import shutil
from tkinter import filedialog
from backend.orchestrator.pipeline_runner import run_reconciliation_pipeline
import threading
import pandas as pd
import os

EXPECTED_SCHEMAS = {
    "Delivery Data": {
        "Delivery Date",
        "Customer Name",
        "Chassis Number",
        "VIN Number",
        "Showroom",
    },
    "RTO Data": {
        "Office Name",
        "Dealer Name",
        "Vehicle Registration Number",
        "Owner Name",
        "Chassis Number",
        "VIN Number",
    },
}
PRIMARY_COLOUR = "#16365C"
PRIMARY_COLOUR_HOVER = "#204A7D"
SECONDARY_COLOUR = "#EDE8D0"
SECONDARY_COLOUR_HOVER = "#F5F1DC"
ACCENT_COLOUR = "#FFC107"


class RTORecoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------------- Window ----------------
        self.title("Automobile RTO Reco")
        self.geometry("1000x600")
        # ------ Fonts ----
        heading_font = ctk.CTkFont("Calibri", 20, "bold")
        btn_font = ctk.CTkFont("Calibri", 16, "bold")
        label_font = ctk.CTkFont("Calibri", 16)
        message_font = ctk.CTkFont("Calibri", 16)

        self.df = None
        self.output_path = None

        # Root grid
        self.grid_columnconfigure(0, weight=1)
        # ===== Header Frame
        header_frame = ctk.CTkFrame(
            self, height=100, fg_color=PRIMARY_COLOUR, corner_radius=0
        )
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew")

        # Configure columns
        header_frame.grid_columnconfigure(0, weight=0)  # logo
        header_frame.grid_columnconfigure(1, weight=1)  # text (expand)
        header_frame.grid_columnconfigure(2, weight=0)  # text (expand)

        # --- Load image (IMPORTANT: keep reference)
        self.logo_img = ctk.CTkImage(Image.open("assets/logo.png"), size=(80, 80))

        # --- Logo on left
        logo_label = ctk.CTkLabel(header_frame, image=self.logo_img, text="")
        logo_label.grid(row=0, column=0, rowspan=3, padx=20, pady=10, sticky="w")

        # --- Text content (center-left)
        ctk.CTkLabel(
            header_frame,
            text="Automobile RTO Reconciliation",
            font=ctk.CTkFont("Calibri", 24, "bold"),
            text_color=SECONDARY_COLOUR,
        ).grid(row=0, column=1, sticky="w", pady=(10, 0))

        ctk.CTkLabel(
            header_frame,
            text="Asija and Associates LLP",
            font=ctk.CTkFont("Calibri", 16, "bold"),
            text_color=SECONDARY_COLOUR,
        ).grid(row=1, column=1, sticky="w", pady=(5, 0))

        ctk.CTkLabel(
            header_frame,
            text="Audit and Assurance Vertical",
            font=ctk.CTkFont("Calibri", 14, "bold"),
            text_color=SECONDARY_COLOUR,
        ).grid(row=2, column=1, sticky="w", pady=(0, 10))

        ctk.CTkButton(
            header_frame,
            text="Export Input Template",
            text_color=PRIMARY_COLOUR,
            font=btn_font,
            fg_color=SECONDARY_COLOUR,
            hover_color=SECONDARY_COLOUR_HOVER,
            command=self.download_template,
        ).grid(row=1, column=2, sticky="ew", padx=(0, 20))

        # ================= LOAD FILE FRAME =================
        load_frame = ctk.CTkFrame(self)
        load_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        load_frame.grid_columnconfigure(0, weight=1)

        # Simulated LabelFrame title
        ctk.CTkLabel(load_frame, text="Import File", font=heading_font).grid(
            row=0, column=0, sticky="w", padx=15, pady=(5, 15)
        )

        ctk.CTkButton(
            load_frame,
            text="Import File",
            width=200,
            font=btn_font,
            fg_color=PRIMARY_COLOUR,
            hover_color=PRIMARY_COLOUR_HOVER,
            command=self.upload_file,
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            load_frame, text="No file selected", font=label_font, text_color="gray"
        )
        self.status_label.grid(row=1, column=1, padx=15, sticky="w")

        # ================= WORKBOOK INFO FRAME =================
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        info_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(info_frame, text="Workbook Info", font=heading_font).grid(
            row=0, column=0, sticky="w", padx=15, pady=(5, 2)
        )

        self.selected_sheet = ctk.StringVar()

        ctk.CTkLabel(info_frame, text="Sheet:", font=label_font).grid(
            row=1, column=0, padx=15, sticky="w", pady=(0, 2)
        )

        self.sheet_dropdown = ctk.CTkComboBox(
            info_frame,
            values=[],
            variable=self.selected_sheet,
            height=30,
            width=250,
            state="readonly",
            command=self.on_sheet_change,
        )
        self.sheet_dropdown.grid(row=2, column=0, sticky="w", padx=15, pady=(5, 5))

        self.rows_var = ctk.StringVar(value="Number of Rows: -")
        self.cols_var = ctk.StringVar(value="Number of Columns: -")

        ctk.CTkLabel(info_frame, textvariable=self.rows_var, font=label_font).grid(
            row=1, column=1, sticky="w", pady=(2, 0)
        )
        ctk.CTkLabel(info_frame, textvariable=self.cols_var, font=label_font).grid(
            row=2, column=1, sticky="w", pady=(2, 0)
        )

        ctk.CTkLabel(info_frame, text="Headers:", font=label_font).grid(
            row=3, column=0, sticky="w", padx=15, pady=(0, 2)
        )

        self.headers_text = ctk.CTkTextbox(info_frame, height=50, font=message_font)
        self.headers_text.grid(
            row=4, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 10)
        )
        self.headers_text.configure(state="disabled")

        # ================= DEALERSHIP FRAME =================
        dealer_frame = ctk.CTkFrame(self)
        dealer_frame.grid(row=3, column=0, sticky="nw", padx=20, pady=10)

        ctk.CTkLabel(dealer_frame, text="Select Dealership", font=heading_font).grid(
            row=0, column=0, sticky="n", padx=10, pady=(5, 5)
        )

        self.selected_dealer = ctk.StringVar()

        ctk.CTkRadioButton(
            dealer_frame,
            text="BR Tata",
            variable=self.selected_dealer,
            value="BR",
            font=label_font,
            fg_color=PRIMARY_COLOUR_HOVER,
            hover_color=PRIMARY_COLOUR_HOVER,
        ).grid(row=1, column=0, sticky="w", padx=10)
        ctk.CTkRadioButton(
            dealer_frame,
            text="SRM Tata",
            variable=self.selected_dealer,
            value="SAS",
            fg_color=PRIMARY_COLOUR_HOVER,
            hover_color=PRIMARY_COLOUR_HOVER,
            font=label_font,
        ).grid(row=2, column=0, sticky="w", padx=10, pady=(0, 15))

        self.grid_columnconfigure(0, weight=0)  # Dealership selector
        self.grid_columnconfigure(1, weight=1)  # Message box
        self.grid_columnconfigure(2, weight=0)  # Actions

        # ================= MESSAGES FRAME =================
        message_frame = ctk.CTkFrame(self)
        message_frame.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)
        message_frame.grid_columnconfigure(0, weight=1)
        message_frame.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(message_frame, text="Messages", font=heading_font).grid(
            row=0, column=0, sticky="w", padx=10, pady=(5, 10)
        )

        self.message_box = ctk.CTkTextbox(
            message_frame,
            height=140,  # similar visual weight to Headers
            wrap="word",
            font=message_font,
        )
        self.message_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.message_box.configure(state="disabled")
        # ================= ACTIONS FRAME =================
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=3, column=2, sticky="n", padx=(10, 20), pady=10)

        ctk.CTkLabel(action_frame, text="Actions", font=heading_font).grid(
            row=0, column=0, sticky="w", padx=10, pady=(5, 8)
        )

        ctk.CTkButton(
            action_frame,
            text="Choose Output Location",
            width=180,
            text_color=PRIMARY_COLOUR,
            fg_color=SECONDARY_COLOUR,
            hover_color=SECONDARY_COLOUR_HOVER,
            font=btn_font,
            command=self.choose_output_dir,
        ).grid(row=1, column=0, padx=10, pady=(0, 8))

        ctk.CTkButton(
            action_frame,
            text="Get RTO Reco",
            width=180,
            fg_color=PRIMARY_COLOUR,
            hover_color=PRIMARY_COLOUR_HOVER,
            font=btn_font,
            command=self.get_rto_reco,
        ).grid(row=2, column=0, padx=10, pady=(0, 10))

    # ---- Utility functions for UI ----
    def clear_messages(self):
        self.message_box.configure(state="normal")
        self.message_box.delete("1.0", "end")
        self.message_box.configure(state="disabled")

    def download_template(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel file", "*.xlsx")],
            initialfile="rto_template.xlsx",
        )

        if not path:
            return

        # Get absolute path to template
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "assets", "template.xlsx")

        if not os.path.exists(template_path):
            print("Template not found:", template_path)
            return

        shutil.copy(template_path, path)

    def show_message(self, text: str):
        self.message_box.configure(state="normal")
        self.message_box.insert("end", text + "\n")
        self.message_box.configure(state="disabled")
        self.message_box.see("end")

    def get_rto_reco(self):
        if not hasattr(self, "file_path") or not self.file_path:
            self.show_message("Please load an Excel file first.")
            return
        dealership = self.selected_dealer.get()
        if not dealership:
            self.show_message("Please select a dealership.")
            return

        self.clear_messages()
        self.show_message("Starting Reconciliation pipeline...")

        # Run in background so UI does not freeze
        threading.Thread(target=self._run_pipeline_safe, daemon=True).start()

    def _run_pipeline_safe(self):
        result = run_reconciliation_pipeline(
            input_file_path=self.file_path,
            dealership=self.selected_dealer.get(),
            output_dir=self.output_path,
        )

        # UI updates must happen on main thread
        self.after(0, self._handle_pipeline_result, result)

    def _handle_pipeline_result(self, result: dict):
        for msg in result["messages"]:
            self.show_message(msg)

        if result["success"]:
            self.show_message(f"\n📄 Output file generated:\n{result['output_file']}")
        else:
            self.show_message("\n❌ Please fix the above issues and try again.")

    def choose_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path = directory
            self.show_message(f"📁 Output directory set to:\n{directory}")

    def upload_file(self):
        # pass
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if not file_path:
            return
        self.file_path = file_path
        self.status_label.configure(
            text=f"Loaded: {os.path.basename(file_path)}", text_color="green"
        )
        # Load workbook ONCE
        self.sheets = pd.read_excel(self.file_path, sheet_name=None)
        sheet_names = list(self.sheets.keys())

        # Populate combobox
        self.sheet_dropdown.configure(values=sheet_names)

        # Auto-select first sheet
        if sheet_names:
            self.selected_sheet.set(sheet_names[0])
            self.load_sheet(sheet_names[0])

    # ---- Workbook info methods ----
    def load_sheet(self, sheet_name):
        self.df = self.sheets[sheet_name]

        # Update info
        self.rows_var.set(f"Number of Rows: {self.df.shape[0]}")
        self.cols_var.set(f"Number of Columns: {self.df.shape[1]}")

        headers = ", ".join(self.df.columns.astype(str))

        self.headers_text.configure(state="normal", text_color="green")
        self.headers_text.delete("1.0", "end")
        self.headers_text.insert("end", headers)
        self.headers_text.configure(state="disabled")

        # Schema inspection
        self.inspect_headers(self.df, sheet_name)

    def on_sheet_change(self, event=None):
        sheet_name = self.selected_sheet.get()
        if sheet_name:
            self.load_sheet(sheet_name)

    def inspect_headers(self, df: pd.DataFrame, sheet_name: str):
        """
        Warn user about schema issues:
        - Leading/trailing spaces
        - Case mismatches
        - Missing expected columns
        """
        self.clear_messages()
        expected = EXPECTED_SCHEMAS.get(sheet_name)

        # If schema is not defined for this sheet, skip inspection
        if not expected:
            self.show_message(f"ℹ No expected schema defined for sheet: {sheet_name}")
            return

        self.show_message(f"Inspecting schema for sheet: {sheet_name}")

        raw_headers = list(df.columns)
        stripped_headers = [h.strip() for h in raw_headers]

        # Normalized lookup maps
        actual_normalized = {h.strip(): h for h in raw_headers}
        actual_lower = {h.strip().lower(): h for h in raw_headers}

        # Missing Expected columns
        missing = [
            col
            for col in expected
            if col not in actual_normalized and col.lower() not in actual_lower
        ]

        if missing:
            self.show_message(
                "⚠ Missing expected columns:\n  - " + "\n  - ".join(missing)
            )

        # Leading / trailing whitespace
        whitespace_issues = [
            actual_normalized[col]
            for col in expected
            if col in actual_normalized and actual_normalized[col] != col
        ]
        if whitespace_issues:
            self.show_message(
                "⚠ Headers with leading/trailing spaces:\n  - "
                + "\n  - ".join(whitespace_issues)
            )

        # Case mismatches
        case_issues = []
        for col in expected:
            actual = actual_lower.get(col.lower())
            if actual and actual.strip() != col:
                case_issues.append(actual)

        if case_issues:
            self.show_message(
                "⚠ Headers with inconsistent casing:\n  - " + "\n  - ".join(case_issues)
            )
        # Extra columns
        expected_lower = {c.lower() for c in expected}
        extra = [h for h in raw_headers if h.strip().lower() not in expected_lower]
        if extra:
            self.show_message(
                "ℹ Extra columns found (will be ignored later):\n  - "
                + "\n  - ".join(extra)
            )


if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    app = RTORecoApp()
    app.mainloop()
