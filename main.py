import customtkinter as ctk
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
        },
    }

class RTORecoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
    
        # ---------------- Window ----------------
        self.title("RTO Reconciliation Tool")
        self.geometry("1000x600")

        self.df = None

        # Root grid
        self.grid_columnconfigure(0, weight=1)

        # ================= LOAD FILE FRAME =================
        load_frame = ctk.CTkFrame(self)
        load_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        load_frame.grid_columnconfigure(0, weight=1)
        
        heading_font = ctk.CTkFont("Calibri", 20, "bold")
        btn_font = ctk.CTkFont("Calibri", 16, "bold")
        label_font = ctk.CTkFont("Calibri", 16)
        message_font = ctk.CTkFont("Calibri", 16)

        # Simulated LabelFrame title
        ctk.CTkLabel(
            load_frame,
            text="Load File",
            font=heading_font
        ).grid(row=0, column=0, sticky="w",padx=15, pady=(5, 15))

        ctk.CTkButton(
            load_frame,
            text="Load File",
            width=200,
            font=btn_font,
            command=self.upload_file
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(0,10))

        self.status_label = ctk.CTkLabel(
            load_frame,
            text="No file selected",
            font=label_font,
            text_color="gray"
        )
        self.status_label.grid(row=1, column=1, padx=15, sticky="w")

        # ================= WORKBOOK INFO FRAME =================
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        info_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            info_frame,
            text="Workbook Info",
            font=heading_font
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(5, 15))

        self.selected_sheet = ctk.StringVar()

        ctk.CTkLabel(info_frame, text="Sheet:", font=label_font).grid(row=1, column=0,padx=15, sticky="w")

        self.sheet_dropdown = ctk.CTkComboBox(
            info_frame,
            values=[],
            variable=self.selected_sheet,
            height=30,
            width=250,
            state="readonly",
            command=self.on_sheet_change
        )
        self.sheet_dropdown.grid(row=2, column=0, sticky="w",padx=15, pady=(5, 5))
        # self.sheet_dropdown.bind("<<ComboboxSelected>>",self.on_sheet_change)

        self.rows_var = ctk.StringVar(value="Number of Rows: -")
        self.cols_var = ctk.StringVar(value="Number of Columns: -")

        ctk.CTkLabel(info_frame, textvariable=self.rows_var, font=label_font).grid(row=1, column=1, sticky="w",pady=(2,0))
        ctk.CTkLabel(info_frame, textvariable=self.cols_var, font=label_font).grid(row=2, column=1, sticky="w",pady=(2,0))

        ctk.CTkLabel(info_frame, text="Headers:",font=label_font).grid(row=3, column=0, sticky="w", padx=15, pady=(10, 2))

        self.headers_text = ctk.CTkTextbox(info_frame, height=80,font=message_font)
        self.headers_text.grid(row=4, column=0, columnspan=2, sticky="ew", padx=15, pady=(0,10))
        self.headers_text.configure(state="disabled")

        # ================= DEALERSHIP FRAME =================
        dealer_frame = ctk.CTkFrame(self)
        dealer_frame.grid(row=2, column=0, sticky="nw", padx=20, pady=10)

        ctk.CTkLabel(
            dealer_frame,
            text="Select Dealership",
            font=heading_font
        ).grid(row=0, column=0, sticky="n", padx=10, pady=(5, 5))

        self.selected_dealer = ctk.StringVar()

        ctk.CTkRadioButton(dealer_frame, text="BR Hyundai", variable=self.selected_dealer, value="BR",font=label_font).grid(row=1, column=0, sticky="w",padx=10)
        ctk.CTkRadioButton(dealer_frame, text="SAS Hyundai", variable=self.selected_dealer, value="SAS",font=label_font).grid(row=2, column=0, sticky="w",padx=10)
        ctk.CTkRadioButton(dealer_frame, text="JSV Hyundai", variable=self.selected_dealer, value="JSV",font=label_font).grid(row=3, column=0, sticky="w",padx=10,pady=(0,10))

        self.grid_columnconfigure(0,weight=0)  # Dealership selector
        self.grid_columnconfigure(1,weight=1)  # Message box
        self.grid_columnconfigure(2,weight=0)  # Actions

        # ================= MESSAGES FRAME =================
        message_frame = ctk.CTkFrame(self)
        message_frame.grid(
            row=2,
            column=1,
            sticky="nsew",
            padx=10,
            pady=10
        )
        message_frame.grid_columnconfigure(0, weight=1)
        message_frame.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            message_frame,
            text="Messages",
            font=heading_font
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(5,10))

        self.message_box = ctk.CTkTextbox(
            message_frame,
            height=140,         # similar visual weight to Headers
            wrap="word",
            font=message_font
            
        )
        self.message_box.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )
        self.message_box.configure(state="disabled")
        # ================= ACTIONS FRAME =================
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(
            row=2,
            column=2,
            sticky="n",
            padx=(10, 20),
            pady=10
        )

        ctk.CTkLabel(
            action_frame,
            text="Actions",
            font=heading_font
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 8))
        
        # ctk.CTkButton(
        #     action_frame,
        #     text="Process Data",
        #     width=160,
        #     font=button_font,
        #     command=self.process_data
        # ).grid(row=1, column=0, padx=10, pady=(0, 8))

        ctk.CTkButton(
            action_frame,
            text="Get RTO Reco",
            width=160,
            fg_color="green",
            font=btn_font,
            hover_color="#0f8a0f",
            command=self.get_rto_reco
        ).grid(row=1, column=0, padx=10, pady=(0, 10))

    # ---- Utility functions for UI ----
    def clear_messages(self):
        self.message_box.configure(state="normal")
        self.message_box.delete("1.0", "end")
        self.message_box.configure(state="disabled")


    def show_message(self, text: str):
        self.message_box.configure(state="normal")
        self.message_box.insert("end", text + "\n")
        self.message_box.configure(state="disabled")
        self.message_box.see("end")

    def get_rto_reco(self):
        if not hasattr(self,"file_path") or not self.file_path:
            self.show_message("Please load an Excel file first.")
            return
        dealership = self.selected_dealer.get()
        if not dealership:
            self.show_message('Please select a dealership.')
            return
        
        self.clear_messages()
        self.show_message("Starting Reconciliation pipeline...")

        # Run in background so UI does not freeze
        threading.Thread(
            target = self._run_pipeline_safe,
            daemon = True
        ).start()

    def _run_pipeline_safe(self):
        result = run_reconciliation_pipeline(
            input_file_path=self.file_path,
            dealership=self.selected_dealer.get(),
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



    def upload_file(self):
        # pass
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if not file_path:
            return
        self.file_path=file_path
        self.status_label.configure(
            text=f"Loaded: {os.path.basename(file_path)}",
            text_color='green'
        )
        # Load workbook ONCE
        self.sheets = pd.read_excel(self.file_path,sheet_name=None)
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

        self.headers_text.configure(state="normal",text_color="green")
        self.headers_text.delete("1.0", "end")
        self.headers_text.insert("end",headers)
        self.headers_text.configure(state="disabled")

        #Schema inspection
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
        self.show_message(f"🔍 Inspecting schema for sheet: {sheet_name}")

        raw_headers = list(df.columns)
        stripped_headers = [h.strip() for h in raw_headers]

        # 1️⃣ Leading / trailing whitespace
        whitespace_issues = [
            h for h, s in zip(raw_headers, stripped_headers) if h != s
        ]
        if whitespace_issues:
            self.show_message(
                "⚠ Headers with leading/trailing spaces:\n  - "
                + "\n  - ".join(whitespace_issues)
            )

        # 2️⃣ Case mismatches
        case_issues = [
            h for h in raw_headers
            if h.strip().lower() != h.strip()
        ]
        if case_issues:
            self.show_message(
                "⚠ Headers with inconsistent casing:\n  - "
                + "\n  - ".join(case_issues)
            )

        # 3️⃣ Expected schema check (if known)
        expected = EXPECTED_SCHEMAS.get(sheet_name)
        if expected:
            normalized_actual = {h.strip() for h in raw_headers}
            missing = expected - normalized_actual
            extra = normalized_actual - expected

            if missing:
                self.show_message(
                    "⚠ Missing expected columns:\n  - "
                    + "\n  - ".join(missing)
                )

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
