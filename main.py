# import customtkinter as ctk
# from customtkinter import CTk
# from tkinter import filedialog, messagebox, ttk
# import pandas as pd
# import os

# class RTORecoApp(ctk.CTk):
#     def __init__(self, root):
#         self.root = root
#         self.root.title("RTO Reconciliation Tool")
#         self.root.geometry("1000x600")

#         self.df = None

#         # Root grid config
#         self.root.grid_rowconfigure(0, weight=0)
#         self.root.grid_columnconfigure(0, weight=1)


#         # --- File loader ---
#         load_frame = ctk.LabelFrame(
#             root,
#             text="Load File",
#             padx=15,
#             pady=10
#         )
#         load_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

#         # Make it expand across window width
#         load_frame.grid_columnconfigure(0, weight=1)

#         upload_btn = tk.Button(
#             load_frame,
#             text="Load File",
#             width=20,
#             command=self.upload_file
#         )
#         upload_btn.grid(
#             row=0,
#             column=0,
#             sticky="w"
#         )
#         self.status_label = tk.Label(
#             load_frame,
#             text="No file selected",
#             fg="gray"
#         )
#         self.status_label.grid(row=0, column=1, pady=5)

#         # --- Workbook Info ----
#         info_frame = tk.LabelFrame(self.root, text="Workbook Info", padx=15, pady=10)
#         info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

#         # Make frame stretch horizontally
#         info_frame.grid_columnconfigure(0, weight=1)
#         info_frame.grid_columnconfigure(1, weight=1)

#         tk.Label(info_frame, text="Sheet: ", anchor="w").grid(row=0, column=0, sticky="w")

#         self.selected_sheet = tk.StringVar()

#         self.sheet_dropdown = ttk.Combobox(
#             info_frame, 
#             textvariable=self.selected_sheet,
#             state="readonly",
#             width=30
#         )
#         self.sheet_dropdown.grid(row=1, column=0, sticky="w", pady=(5,10))

#         self.rows_var = tk.StringVar(value="Rows: -")
#         self.cols_var = tk.StringVar(value="Columns: -")

#         tk.Label(
#             info_frame,
#             textvariable=self.rows_var,
#             anchor="w"
#         ).grid(row=0, column=0, sticky="w", padx=(40,0))

#         tk.Label(
#             info_frame,
#             textvariable=self.cols_var,
#             anchor="w"
#         ).grid(row=0, column=1, sticky="w", padx=(40,0))

#         tk.Label(info_frame, text="Headers: ", anchor="w").grid(row=2, column=0, sticky="w", pady=(10,2))

#         self.headers_text = tk.Text(info_frame, height=4, wrap="word")
#         self.headers_text.grid(row=3, column=0, columnspan=2, sticky="ew")
#         self.headers_text.config(state="disabled")

#         # -- Dealership Selection --- 

#         dealer_frame = tk.LabelFrame(self.root, text="Select Dealership", padx=15, pady=10)
#         dealer_frame.grid(row=2,column=0,sticky="w",padx=20, pady=10)
#         # Fix width behaviour(important)
#         dealer_frame.grid_columnconfigure(0, weight=0)

#         self.selected_dealer = tk.StringVar(value="")

#         tk.Radiobutton(dealer_frame,text="BR Hyundai", variable=self.selected_dealer,value="BR").grid(row=0,column=0,sticky="w")
#         tk.Radiobutton(dealer_frame,text="SAS Hyundai", variable=self.selected_dealer,value="SAS").grid(row=1,column=0,sticky="w")
#         tk.Radiobutton(dealer_frame,text="JSV Hyundai", variable=self.selected_dealer,value="JSV").grid(row=2,column=0,sticky="w")

#         # # ---------------- LEFT PANEL ----------------
#         # left_frame = tk.Frame(main_frame)
#         # left_frame.grid(row=1, column=0, sticky="nw")

#         # upload_btn = tk.Button(
#         #     left_frame,
#         #     text="Upload Excel File",
#         #     width=25,
#         #     command=self.upload_file
#         # )
#         # upload_btn.grid(row=0, column=0, pady=5)

#         # self.status_label = tk.Label(
#         #     left_frame,
#         #     text="No file selected",
#         #     fg="gray"
#         # )
#         # self.status_label.grid(row=1, column=0, pady=5)

#         # process_btn = tk.Button(
#         #     left_frame,
#         #     text="Process Data",
#         #     width=25,
#         #     command=self.process_data
#         # )
#         # process_btn.grid(row=2, column=0, pady=5)

#         # save_btn = tk.Button(
#         #     left_frame,
#         #     text="Download Processed File",
#         #     width=25,
#         #     command=self.save_file
#         # )
#         # save_btn.grid(row=3, column=0, pady=5)

#         # # ---------------- RIGHT PANEL (INFO) ----------------
#         # right_frame = tk.LabelFrame(
#         #     main_frame,
#         #     text="File Info",
#         #     padx=10,
#         #     pady=10
#         # )
#         # right_frame.grid(row=1, column=1, sticky="ne", padx=(20, 0))

#         # self.rows_var = tk.StringVar(value="Rows: -")
#         # self.cols_var = tk.StringVar(value="Columns: -")
#         # self.headers_var = tk.StringVar(value="Headers: -")

#         # tk.Label(right_frame, textvariable=self.rows_var, anchor="w").grid(row=0, column=0, sticky="w", pady=2)
#         # tk.Label(right_frame, textvariable=self.cols_var, anchor="w").grid(row=1, column=0, sticky="w", pady=2)

#         # tk.Label(right_frame, text="Headers:", anchor="w").grid(row=2, column=0, sticky="w", pady=(10, 2))

#         # self.headers_text = tk.Text(
#         #     right_frame,
#         #     width=30,
#         #     height=6,
#         #     wrap="word"
#         # )
#         # self.headers_text.grid(row=3, column=0)

#         # self.headers_text.config(state="disabled")

#     # ---------------- LOGIC ----------------
#     def upload_file(self):
#         # pass
#         file_path = filedialog.askopenfilename(
#             filetypes=[("Excel Files", "*.xlsx *.xls")]
#         )

#         if file_path:
#             self.df = pd.read_excel(file_path)

#             # Update status
#             self.status_label.config(
#                 text=f"Loaded: {os.path.basename(file_path)}",
#                 fg="green"
#             )

#             # Update info panel
#             self.rows_var.set(f"Rows: {self.df.shape[0]}")
#             self.cols_var.set(f"Columns: {self.df.shape[1]}")

#             headers = ", ".join(self.df.columns.astype(str))

#             self.headers_text.config(state="normal")
#             self.headers_text.delete("1.0", tk.END)
#             self.headers_text.insert(tk.END, headers)
#             self.headers_text.config(state="disabled")

#     def update_filename(self):
#         pass
#     # def process_data(self):
#     #     if self.df is None:
#     #         messagebox.showerror("Error", "Please upload an Excel file first")
#     #         return

#     #     self.df = self.df.drop_duplicates()
#     #     self.df = self.df.fillna("N/A")
#     #     self.df["Processed"] = "Yes"

#     #     messagebox.showinfo("Success", "Data processed successfully!")

#     # def save_file(self):
#     #     if self.df is None:
#     #         messagebox.showerror("Error", "No processed data to save")
#     #         return

#     #     save_path = filedialog.asksaveasfilename(
#     #         defaultextension=".xlsx",
#     #         filetypes=[("Excel Files", "*.xlsx")]
#     #     )

#     #     if save_path:
#     #         self.df.to_excel(save_path, index=False)
#     #         messagebox.showinfo("Saved", "Processed file saved successfully!")


# if __name__ == "__main__":
#     ctk.set_appearance_mode("Light")
#     ctk.set_default_color_theme("blue")
#     app = RTORecoApp()
#     app.mainloop()
import customtkinter as ctk
from tkinter import filedialog, messagebox
from backend.orchestrator.pipeline_runner import run_reconciliation_pipeline
import threading
import pandas as pd
import os


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

        # Simulated LabelFrame title
        ctk.CTkLabel(
            load_frame,
            text="Load File",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, sticky="w",padx=15, pady=(0, 10))

        ctk.CTkButton(
            load_frame,
            text="Load File",
            width=160,
            command=self.upload_file
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(0,10))

        self.status_label = ctk.CTkLabel(
            load_frame,
            text="No file selected",
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
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(0, 10))

        self.selected_sheet = ctk.StringVar()

        ctk.CTkLabel(info_frame, text="Sheet:").grid(row=1, column=0,padx=15, sticky="w")

        self.sheet_dropdown = ctk.CTkComboBox(
            info_frame,
            values=[],
            variable=self.selected_sheet,
            width=250
        )
        self.sheet_dropdown.grid(row=2, column=0, sticky="w",padx=15, pady=(5, 10))

        self.rows_var = ctk.StringVar(value="Number of Rows: -")
        self.cols_var = ctk.StringVar(value="Number of Columns: -")

        ctk.CTkLabel(info_frame, textvariable=self.rows_var).grid(row=1, column=1, sticky="w",pady=(2,0))
        ctk.CTkLabel(info_frame, textvariable=self.cols_var).grid(row=2, column=1, sticky="w",pady=(2,0))

        ctk.CTkLabel(info_frame, text="Headers:").grid(row=3, column=0, sticky="w", padx=10, pady=(10, 2))

        self.headers_text = ctk.CTkTextbox(info_frame, height=80)
        self.headers_text.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=(0,10))
        self.headers_text.configure(state="disabled")

        # ================= DEALERSHIP FRAME =================
        dealer_frame = ctk.CTkFrame(self)
        dealer_frame.grid(row=2, column=0, sticky="w", padx=20, pady=10)

        ctk.CTkLabel(
            dealer_frame,
            text="Select Dealership",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(0, 10))

        self.selected_dealer = ctk.StringVar()

        ctk.CTkRadioButton(dealer_frame, text="BR Hyundai", variable=self.selected_dealer, value="BR").grid(row=1, column=0, sticky="w",padx=10)
        ctk.CTkRadioButton(dealer_frame, text="SAS Hyundai", variable=self.selected_dealer, value="SAS").grid(row=2, column=0, sticky="w",padx=10)
        ctk.CTkRadioButton(dealer_frame, text="JSV Hyundai", variable=self.selected_dealer, value="JSV").grid(row=3, column=0, sticky="w",padx=10,pady=(0,10))

        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=0)

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

        ctk.CTkLabel(
            message_frame,
            text="Messages",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 6))

        self.message_box = ctk.CTkTextbox(
            message_frame,
            height=90,          # similar visual weight to Headers
            wrap="word"
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
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 8))
        
        ctk.CTkButton(
            action_frame,
            text="Process Data",
            width=160,
            command=self.process_data
        ).grid(row=1, column=0, padx=10, pady=(0, 8))

        ctk.CTkButton(
            action_frame,
            text="Get RTO Reco",
            width=160,
            fg_color="green",
            hover_color="#0f8a0f",
            command=self.get_rto_reco
        ).grid(row=2, column=0, padx=10, pady=(0, 10))

    def clear_messages(self):
        self.message_box.configure(state="normal")
        self.message_box.delete("1.0", "end")
        self.message_box.configure(state="disabled")


    def show_message(self, text: str):
        self.message_box.configure(state="normal")
        self.message_box.insert("end", text + "\n")
        self.message_box.configure(state="disabled")
        self.message_box.see("end")
    
    def process_data(self):
        pass
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
        if file_path:
            self.file_path=file_path
            self.status_label.configure(
                text=f"Loaded: {os.path.basename(file_path)}",
                text_color='green'
            )

if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    app = RTORecoApp()
    app.mainloop()
