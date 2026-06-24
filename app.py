"""
CRF Auto-Bookmarker — Desktop Application
Built with CustomTkinter for a modern dark-mode UI.
Process first, then choose where to save.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from bookmarker import process_crf_bytes


# === APP CONFIGURATION ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class CRFBookmarkerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("CRF Auto-Bookmarker")
        self.geometry("750x620")
        self.minsize(650, 550)
        self.resizable(True, True)

        # Variables
        self.input_path = ctk.StringVar(value="")
        self.clip_height = ctk.DoubleVar(value=140)
        self.is_processing = False
        self.output_bytes = None  # Stores processed PDF bytes
        self.input_filename = ""  # Original filename for suggested save name

        # Build UI
        self._create_widgets()

    def _create_widgets(self):
        """Build the entire UI layout."""

        # === HEADER ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header_frame,
            text="📑 CRF Auto-Bookmarker",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Generate hierarchical bookmarks for CRF PDFs automatically",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        ).pack(anchor="w", pady=(2, 0))

        # === INPUT FILE SECTION ===
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=20, pady=(10, 5))

        ctk.CTkLabel(
            input_frame,
            text="📂 Input PDF (without bookmarks)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        input_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=15, pady=(0, 10))

        self.input_entry = ctk.CTkEntry(
            input_row,
            textvariable=self.input_path,
            placeholder_text="Select your CRF PDF file...",
            width=500
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            input_row,
            text="Browse",
            width=100,
            command=self._browse_input
        ).pack(side="right")

        # === SETTINGS ===
        settings_frame = ctk.CTkFrame(self)
        settings_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            settings_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        slider_row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        slider_row.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            slider_row,
            text="Header scan height (points):",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 10))

        self.clip_slider = ctk.CTkSlider(
            slider_row,
            from_=100,
            to=250,
            number_of_steps=15,
            variable=self.clip_height,
            width=200
        )
        self.clip_slider.pack(side="left", padx=(0, 10))

        self.clip_label = ctk.CTkLabel(
            slider_row,
            text="140",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=40
        )
        self.clip_label.pack(side="left")
        self.clip_slider.configure(command=self._update_clip_label)

        # === BUTTONS ROW ===
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        # Process Button
        self.process_btn = ctk.CTkButton(
            btn_frame,
            text="🚀 Generate Bookmarks",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            command=self._start_processing
        )
        self.process_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Download Button (initially disabled)
        self.download_btn = ctk.CTkButton(
            btn_frame,
            text="⬇️ Save As...",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color="#2196F3",
            hover_color="#1976D2",
            state="disabled",
            command=self._save_output
        )
        self.download_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # === PROGRESS BAR ===
        self.progress_bar = ctk.CTkProgressBar(self, height=8)
        self.progress_bar.pack(fill="x", padx=20, pady=(5, 5))
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.progress_label.pack(pady=(0, 5))

        # === RESULTS SECTION ===
        self.results_frame = ctk.CTkFrame(self)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        self.results_text = ctk.CTkTextbox(
            self.results_frame,
            font=ctk.CTkFont(size=12, family="Consolas"),
            height=150
        )
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.results_text.insert("1.0", "Results will appear here after processing...")
        self.results_text.configure(state="disabled")

    # === EVENT HANDLERS ===

    def _browse_input(self):
        """Open file dialog to select input PDF."""
        file_path = filedialog.askopenfilename(
            title="Select CRF PDF",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file_path:
            self.input_path.set(file_path)
            self.input_filename = os.path.basename(file_path)
            # Reset state when new file is selected
            self.output_bytes = None
            self.download_btn.configure(state="disabled")
            self.progress_bar.set(0)
            self.progress_label.configure(text="Ready", text_color="gray")

    def _update_clip_label(self, value):
        """Update the clip height label when slider moves."""
        self.clip_label.configure(text=str(int(float(value))))

    def _start_processing(self):
        """Validate inputs and start processing in a background thread."""
        input_file = self.input_path.get().strip()

        # Validation
        if not input_file:
            messagebox.showwarning("Missing Input", "Please select an input PDF file.")
            return
        if not os.path.exists(input_file):
            messagebox.showerror("File Not Found", f"Input file not found:\n{input_file}")
            return

        # Disable buttons during processing
        self.is_processing = True
        self.process_btn.configure(state="disabled", text="⏳ Processing...")
        self.download_btn.configure(state="disabled")
        self.output_bytes = None
        self.progress_bar.set(0)
        self.progress_label.configure(text="Starting...", text_color="white")

        # Clear results
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", "Processing...\n")
        self.results_text.configure(state="disabled")

        # Run in background thread to keep UI responsive
        thread = threading.Thread(
            target=self._run_processing,
            args=(input_file,),
            daemon=True
        )
        thread.start()

    def _run_processing(self, input_file: str):
        """Background processing thread."""

        def progress_callback(current, total):
            progress = current / total
            self.after(0, lambda: self.progress_bar.set(progress))
            self.after(0, lambda: self.progress_label.configure(
                text=f"Processing page {current} of {total}..."
            ))

        # Read input file as bytes
        with open(input_file, "rb") as f:
            input_bytes = f.read()

        # Run the bookmarking engine
        result = process_crf_bytes(
            input_bytes=input_bytes,
            clip_height=self.clip_height.get(),
            progress_callback=progress_callback
        )

        # Update UI on main thread
        self.after(0, lambda: self._show_results(result))

    def _show_results(self, result):
        """Display results in the UI after processing completes."""
        self.is_processing = False
        self.process_btn.configure(state="normal", text="🚀 Generate Bookmarks")
        self.progress_bar.set(1.0 if result.success else 0)

        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")

        if result.success:
            # Store output bytes for download
            self.output_bytes = result.output_bytes
            self.download_btn.configure(state="normal")

            self.progress_label.configure(text="✅ Complete! Click 'Save As...' to download.", text_color="#4CAF50")

            output = []
            output.append("=" * 55)
            output.append("  ✅ BOOKMARKING COMPLETE!")
            output.append("=" * 55)
            output.append("")
            output.append(f"  📄 Total Pages:            {result.total_pages}")
            output.append(f"  📁 Folders (Parents):      {result.parent_count}")
            output.append(f"  📋 Forms (Children):       {result.child_count}")
            output.append(f"  📝 Total Bookmarks:        {result.total_bookmarks}")
            output.append(f"  ⚠️  Pages Skipped:          {result.pages_skipped}")
            output.append("")
            output.append("  👉 Click 'Save As...' to choose where to save the file.")
            output.append("")
            output.append("-" * 55)
            output.append(f"  📁 Unique Folders ({len(result.unique_folders)}):")
            for folder in result.unique_folders:
                output.append(f"     • {folder}")
            output.append("")
            output.append(f"  📋 Unique Forms ({len(result.unique_forms)}):")
            for form in result.unique_forms:
                output.append(f"     • {form}")

            self.results_text.insert("1.0", "\n".join(output))

        else:
            self.progress_label.configure(text="❌ Failed", text_color="#FF5555")
            self.download_btn.configure(state="disabled")

            output = []
            output.append("=" * 55)
            output.append("  ❌ BOOKMARKING FAILED")
            output.append("=" * 55)
            output.append("")
            output.append(f"  Error: {result.error_message}")
            output.append("")
            output.append(f"  Pages scanned: {result.total_pages}")
            output.append(f"  Pages skipped: {result.pages_skipped}")
            output.append("")
            output.append("  💡 Tips:")
            output.append("     • Try increasing the Header scan height slider")
            output.append("     • Ensure the PDF has Folder/Form headers")
            output.append("     • Check if the PDF is corrupted")

            self.results_text.insert("1.0", "\n".join(output))
            messagebox.showerror("Error", result.error_message)

        self.results_text.configure(state="disabled")

    def _save_output(self):
        """Open Save As dialog and write the bookmarked PDF."""
        if not self.output_bytes:
            messagebox.showwarning("No Output", "No processed file available. Run bookmarking first.")
            return

        # Suggest filename based on input
        name, ext = os.path.splitext(self.input_filename)
        suggested_name = f"{name}_Bookmarked{ext}"

        file_path = filedialog.asksaveasfilename(
            title="Save Bookmarked PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=suggested_name
        )

        if file_path:
            try:
                with open(file_path, "wb") as f:
                    f.write(self.output_bytes)
                messagebox.showinfo(
                    "Saved!",
                    f"✅ Bookmarked PDF saved successfully!\n\n💾 {file_path}"
                )
                self.progress_label.configure(
                    text=f"💾 Saved to: {os.path.basename(file_path)}",
                    text_color="#4CAF50"
                )
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")


# === RUN THE APP ===
if __name__ == "__main__":
    app = CRFBookmarkerApp()
    app.mainloop()