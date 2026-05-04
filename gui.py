import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from agents.orchestrator import OrchestratorAgent
from config import RESUMES_DIR


class ResumeScreeningGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Resume Screening System")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
        
        # Styling
        self.root.configure(bg="#f0f0f0")
        self.style_config = {
            "bg": "#f0f0f0",
            "button_bg": "#1e40af",
            "button_fg": "white",
            "label_fg": "#1f2937",
            "input_bg": "white",
            "border_color": "#d1d5db"
        }
        
        # Variables
        self.role_file_path = tk.StringVar()
        self.resumes_dir_path = tk.StringVar(value=RESUMES_DIR)
        self.dry_run_mode = tk.BooleanVar(value=True)
        self.model_override = tk.StringVar(value="None")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Title
        title = tk.Label(
            self.root, 
            text="🤖 AI Resume Screening System", 
            font=("Arial", 18, "bold"),
            bg=self.style_config["bg"],
            fg=self.style_config["label_fg"]
        )
        title.pack(pady=15)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.style_config["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Role File Selection
        self._create_file_selector(
            main_frame, 
            "Job Role Description File:",
            self.role_file_path,
            select_type="file"
        )
        
        # Resumes Directory Selection
        self._create_file_selector(
            main_frame,
            "Resumes Directory:",
            self.resumes_dir_path,
            select_type="directory"
        )
        
        # Model Override
        self._create_model_selector(main_frame)
        
        # Dry Run Mode
        dry_run_frame = tk.Frame(main_frame, bg=self.style_config["bg"])
        dry_run_frame.pack(fill=tk.X, pady=10)
        
        dry_run_check = tk.Checkbutton(
            dry_run_frame,
            text="🔒 Dry Run Mode (Simulate without sending emails)",
            variable=self.dry_run_mode,
            font=("Arial", 10),
            bg=self.style_config["bg"],
            fg=self.style_config["label_fg"],
            activebackground=self.style_config["bg"],
            activeforeground=self.style_config["label_fg"]
        )
        dry_run_check.pack(anchor=tk.W)
        
        # Run Button
        button_frame = tk.Frame(main_frame, bg=self.style_config["bg"])
        button_frame.pack(fill=tk.X, pady=15)
        
        run_button = tk.Button(
            button_frame,
            text="🚀 Run Screening",
            command=self._run_screening,
            font=("Arial", 12, "bold"),
            bg=self.style_config["button_bg"],
            fg=self.style_config["button_fg"],
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        run_button.pack(fill=tk.X)
        
        # Output Area
        output_label = tk.Label(
            main_frame,
            text="📋 Output & Logs:",
            font=("Arial", 11, "bold"),
            bg=self.style_config["bg"],
            fg=self.style_config["label_fg"]
        )
        output_label.pack(anchor=tk.W, pady=(15, 5))
        
        self.output_text = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            width=70,
            bg=self.style_config["input_bg"],
            fg="#374151",
            font=("Courier New", 9),
            relief=tk.SUNKEN,
            bd=1
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial", 9),
            bg="#e5e7eb",
            fg="#6b7280",
            anchor=tk.W,
            padx=10,
            pady=5
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def _create_file_selector(self, parent, label_text, variable, select_type="file"):
        """Create a file/directory selector widget"""
        frame = tk.Frame(parent, bg=self.style_config["bg"])
        frame.pack(fill=tk.X, pady=10)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=("Arial", 10, "bold"),
            bg=self.style_config["bg"],
            fg=self.style_config["label_fg"]
        )
        label.pack(anchor=tk.W)
        
        input_frame = tk.Frame(frame, bg=self.style_config["bg"])
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        entry = tk.Entry(
            input_frame,
            textvariable=variable,
            font=("Arial", 9),
            bg=self.style_config["input_bg"],
            relief=tk.SUNKEN,
            bd=1
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        button_text = "📁 Browse" if select_type == "directory" else "📄 Browse"
        browse_button = tk.Button(
            input_frame,
            text=button_text,
            command=lambda: self._browse(variable, select_type),
            font=("Arial", 9),
            bg="#6366f1",
            fg="white",
            padx=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=1
        )
        browse_button.pack(side=tk.LEFT)
        
    def _create_model_selector(self, parent):
        """Create model override selector"""
        frame = tk.Frame(parent, bg=self.style_config["bg"])
        frame.pack(fill=tk.X, pady=10)
        
        label = tk.Label(
            frame,
            text="LLM Model Override (Optional):",
            font=("Arial", 10, "bold"),
            bg=self.style_config["bg"],
            fg=self.style_config["label_fg"]
        )
        label.pack(anchor=tk.W)
        
        model_frame = tk.Frame(frame, bg=self.style_config["bg"])
        model_frame.pack(fill=tk.X, pady=(5, 0))
        
        models = ["None", "llama2", "mistral", "neural-chat", "openhermes"]
        dropdown = tk.OptionMenu(
            model_frame,
            self.model_override,
            *models
        )
        dropdown.config(
            font=("Arial", 9),
            bg=self.style_config["input_bg"],
            relief=tk.SUNKEN,
            bd=1
        )
        dropdown.pack(anchor=tk.W)
        
    def _browse(self, variable, select_type):
        """Browse for file or directory"""
        if select_type == "file":
            filepath = filedialog.askopenfilename(
                title="Select Role Description File",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filepath:
                variable.set(filepath)
        else:
            dirpath = filedialog.askdirectory(title="Select Resumes Directory")
            if dirpath:
                variable.set(dirpath)
                
    def _validate_inputs(self):
        """Validate user inputs"""
        if not self.role_file_path.get():
            messagebox.showerror("Error", "Please select a role description file")
            return False
        
        if not Path(self.role_file_path.get()).exists():
            messagebox.showerror("Error", f"Role file not found: {self.role_file_path.get()}")
            return False
        
        if not self.resumes_dir_path.get():
            messagebox.showerror("Error", "Please select a resumes directory")
            return False
        
        if not Path(self.resumes_dir_path.get()).is_dir():
            messagebox.showerror("Error", f"Resumes directory not found: {self.resumes_dir_path.get()}")
            return False
        
        return True
        
    def _run_screening(self):
        """Run the screening process in a separate thread"""
        if not self._validate_inputs():
            return
        
        # Disable run button during execution
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.DISABLED)
        
        # Start screening in background thread
        thread = threading.Thread(target=self._screening_worker, daemon=True)
        thread.start()
        
    def _screening_worker(self):
        """Worker thread for running the screening"""
        try:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            
            self._log("🚀 Starting AI Resume Screening...\n")
            self._log(f"Role File: {self.role_file_path.get()}\n")
            self._log(f"Resumes Dir: {self.resumes_dir_path.get()}\n")
            self._log(f"Dry Run: {self.dry_run_mode.get()}\n")
            self._log(f"Model: {self.model_override.get()}\n")
            self._log("-" * 60 + "\n\n")
            
            self.status_var.set("Running screening...")
            self.root.update()
            
            # Get model override
            model = None if self.model_override.get() == "None" else self.model_override.get()
            
            # Run orchestrator
            orchestrator = OrchestratorAgent(model=model)
            orchestrator.run(
                role_file=Path(self.role_file_path.get()),
                resumes_path=Path(self.resumes_dir_path.get()),
                dry_run=self.dry_run_mode.get()
            )
            
            self._log("\n✅ Screening completed successfully!")
            self.status_var.set("✅ Completed successfully")
            messagebox.showinfo("Success", "Resume screening completed successfully!")
            
        except Exception as e:
            self._log(f"\n❌ Error: {str(e)}")
            self.status_var.set("❌ Error occurred")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            
        finally:
            # Re-enable run button
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Button):
                    widget.config(state=tk.NORMAL)
            self.output_text.config(state=tk.DISABLED)
            
    def _log(self, message):
        """Log message to output text area"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.root.update()


def main():
    root = tk.Tk()
    gui = ResumeScreeningGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
