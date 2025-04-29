import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import string
import sys
import time 

class TestCaseGeneratorApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Codeforces Test Case Generator")
        self.geometry("900x800")
        self.minsize(750, 650)

        self.style = ttk.Style(self)
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        elif 'alt' in available_themes:
             self.style.theme_use('alt')
        elif 'vista' in available_themes: # Good for Windows
             self.style.theme_use('vista')
        elif 'aqua' in available_themes: # Good for macOS
             self.style.theme_use('aqua')
        # Default theme as fallback

        # Define custom colors (adapt these for better themes)
        self.bg_color = self.style.lookup('TFrame', 'background') # Get theme background
        self.fg_color = self.style.lookup('TLabel', 'foreground') # Get theme foreground
        self.accent_color = "#0078D7" # A blue accent color
        self.accent_fg_color = "#FFFFFF" # White text on accent
        self.hover_color = "#005A9E" # Darker blue for hover
        self.pressed_color = "#003C6A" # Even darker for pressed
        self.disabled_bg_color = "#F0F0F0" # Lighter grey for disabled
        self.disabled_fg_color = "#A0A0A0" # Grey text for disabled
        self.status_success_color = "#107C10" # Green for success
        self.status_warning_color = "#D83B01" # Orange for warning
        self.status_info_color = self.fg_color # Default text color for info

        # --- Custom Styles ---
        self.style.configure('TLabelFrame', padding=10, borderwidth=1, relief="groove")
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TCheckbutton', padding=5)
        self.style.configure('TRadiobutton', padding=(0, 5), background=self.bg_color) # Match background
        self.style.configure('TEntry', padding=5)
        self.style.configure('TCombobox', padding=5)

        # Custom Button Style (Primary Action)
        self.style.configure('Accent.TButton',
                             font=('Segoe UI', 10, 'bold'), # Slightly more modern font if available
                             padding=(15, 8),
                             background=self.accent_color,
                             foreground=self.accent_fg_color,
                             borderwidth=1,
                             relief="raised") # Start raised
        self.style.map('Accent.TButton',
                       background=[('active', self.pressed_color), # Clicked state
                                   ('hover', self.hover_color),   # Hover state
                                   ('disabled', self.disabled_bg_color)],
                       foreground=[('disabled', self.disabled_fg_color)],
                       relief=[('pressed', 'sunken'), # Sunken when pressed
                               ('!pressed', 'raised')]) # Raised otherwise

        # Standard Button Style
        self.style.configure('Std.TButton',
                             font=('Segoe UI', 9),
                             padding=(10, 5),
                             borderwidth=1,
                             relief="raised")
        self.style.map('Std.TButton',
                        background=[('active', self.style.lookup('TButton', 'selectbackground')),
                                    ('hover', self.style.lookup('TButton', 'lightcolor'))], # Use theme's hover if possible
                        relief=[('pressed', 'sunken'),
                                ('!pressed', 'raised')])

        # --- Main Frame ---
        main_frame = ttk.Frame(self, padding="15") # Increased padding
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(0, weight=1, minsize=350) # Config column (flexible width)
        main_frame.grid_columnconfigure(1, weight=2) # Output column (takes more space)
        main_frame.grid_rowconfigure(0, weight=1)    # Allow row to expand vertically
        main_frame.grid_rowconfigure(1, weight=0)    # Status bar row (fixed height)

        # --- Configuration Frame (Left Side) with Scrollbar ---
        config_scroll_frame = ttk.Frame(main_frame, style='Card.TFrame', borderwidth=1, relief="solid") # Use a frame as a container
        config_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 5)) # Add padding around it
        config_scroll_frame.grid_rowconfigure(0, weight=1)
        config_scroll_frame.grid_columnconfigure(0, weight=1)

        config_canvas = tk.Canvas(config_scroll_frame, borderwidth=0, highlightthickness=0, background=self.bg_color) # Remove canvas border
        config_canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(config_scroll_frame, orient="vertical", command=config_canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        config_canvas.configure(yscrollcommand=scrollbar.set)

        self.config_frame_content = ttk.Frame(config_canvas, padding="15") # Padding inside the scrollable area
        self.config_frame_content.bind("<Configure>", lambda e: config_canvas.configure(scrollregion=config_canvas.bbox("all")))
        config_canvas.create_window((0, 0), window=self.config_frame_content, anchor="nw")

        # --- Configuration Widgets ---
        current_row = 0 # Use grid layout within config_frame_content for better control

        # --- Test Cases (t) ---
        t_frame = ttk.LabelFrame(self.config_frame_content, text="Test Cases (t)", padding=10)
        t_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        t_frame.grid_columnconfigure(1, weight=1) # Allow entry to expand if needed
        current_row += 1

        self.t_var = tk.BooleanVar()
        self.t_check = ttk.Checkbutton(t_frame, text="Multiple Test Cases (t)?", variable=self.t_var, command=self.toggle_t_entry)
        self.t_check.grid(row=0, column=0, sticky="w")
        self.t_label = ttk.Label(t_frame, text="Number of Cases (t):")
        self.t_entry = ttk.Entry(t_frame, width=10)
        self.t_entry.insert(0, "10")
        # Grid placement handled by toggle_t_entry

        self.toggle_t_entry() # Set initial state

        # --- Common Variables (n, m, k) ---
        vars_frame = ttk.LabelFrame(self.config_frame_content, text="Common Variables", padding=10)
        vars_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        current_row += 1

        self.vars_to_include = {}
        var_row = 0
        for var_name in ['n', 'm', 'k']:
            frame = ttk.Frame(vars_frame) # Use a simple frame for each var line
            frame.grid(row=var_row, column=0, sticky="ew", pady=3)
            var_row += 1

            bool_var = tk.BooleanVar(value=(var_name == 'n')) # Default n checked
            check = ttk.Checkbutton(frame, text=f"Include {var_name}?", variable=bool_var)
            check.pack(side=tk.LEFT, anchor=tk.W, padx=(0, 15)) # Add padding after checkbox

            min_label = ttk.Label(frame, text=f"{var_name} min:")
            min_label.pack(side=tk.LEFT)
            min_entry = ttk.Entry(frame, width=7)
            min_entry.insert(0, "1")
            min_entry.pack(side=tk.LEFT, padx=(2, 10)) # Padding between min/max

            max_label = ttk.Label(frame, text="max:")
            max_label.pack(side=tk.LEFT)
            max_entry = ttk.Entry(frame, width=7)
            max_entry.insert(0, "10")
            max_entry.pack(side=tk.LEFT, padx=2)
            self.vars_to_include[var_name] = (bool_var, min_entry, max_entry)

        # --- Input Structure ---
        structure_frame = ttk.LabelFrame(self.config_frame_content, text="Input Structure per Test Case", padding=10)
        structure_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        current_row += 1

        self.input_type = tk.StringVar(value="list_nums")
        input_options = [
            ("No specific structure (only n, m, k if selected)", "none"),
            ("List/Array of N numbers", "list_nums"),
            ("String of length N", "string_n"),
            ("Single String (no N)", "string_single"),
            ("N x M Matrix", "matrix"),
            ("Fixed Variables (e.g., x y z)", "fixed_vars")
        ]
        for text, value in input_options:
            ttk.Radiobutton(structure_frame, text=text, variable=self.input_type, value=value).pack(anchor=tk.W)

        # --- Constraints for Structures ---
        constraints_frame = ttk.LabelFrame(self.config_frame_content, text="Structure Constraints", padding=10)
        constraints_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        current_row += 1

        # Value Range (Numbers)
        num_range_frame = ttk.Frame(constraints_frame)
        num_range_frame.pack(fill=tk.X, pady=3)
        ttk.Label(num_range_frame, text="Value Range min:").pack(side=tk.LEFT, padx=(0, 2))
        self.num_min_entry = ttk.Entry(num_range_frame, width=9)
        self.num_min_entry.insert(0, "0")
        self.num_min_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(num_range_frame, text="max:").pack(side=tk.LEFT, padx=(0, 2))
        self.num_max_entry = ttk.Entry(num_range_frame, width=9)
        self.num_max_entry.insert(0, "100")
        self.num_max_entry.pack(side=tk.LEFT)

        # Character Set (Strings)
        char_set_frame = ttk.Frame(constraints_frame)
        char_set_frame.pack(fill=tk.X, pady=3)
        ttk.Label(char_set_frame, text="Char Set:").pack(side=tk.LEFT, padx=(0, 2))
        self.char_set_var = tk.StringVar(value="lowercase")
        char_combo = ttk.Combobox(char_set_frame, textvariable=self.char_set_var,
                                  values=["lowercase", "uppercase", "digits", "alphanumeric", "custom"],
                                  width=12, state="readonly")
        char_combo.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(char_set_frame, text="Custom:").pack(side=tk.LEFT, padx=(0, 2))
        self.custom_chars_entry = ttk.Entry(char_set_frame, width=15)
        self.custom_chars_entry.insert(0, "abc")
        self.custom_chars_entry.pack(side=tk.LEFT)

        # String Length (Single String)
        str_len_frame = ttk.Frame(constraints_frame)
        str_len_frame.pack(fill=tk.X, pady=3)
        ttk.Label(str_len_frame, text="Str Len min:").pack(side=tk.LEFT, padx=(0, 2))
        self.str_len_min_entry = ttk.Entry(str_len_frame, width=7)
        self.str_len_min_entry.insert(0, "1")
        self.str_len_min_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(str_len_frame, text="max:").pack(side=tk.LEFT, padx=(0, 2))
        self.str_len_max_entry = ttk.Entry(str_len_frame, width=7)
        self.str_len_max_entry.insert(0, "10")
        self.str_len_max_entry.pack(side=tk.LEFT)

        # Variable Names (Fixed Vars)
        fixed_vars_frame = ttk.Frame(constraints_frame)
        fixed_vars_frame.pack(fill=tk.X, pady=3)
        ttk.Label(fixed_vars_frame, text="Var Names (space-sep):").pack(side=tk.LEFT, padx=(0, 2))
        self.fixed_vars_entry = ttk.Entry(fixed_vars_frame, width=25)
        self.fixed_vars_entry.insert(0, "x y")
        self.fixed_vars_entry.pack(side=tk.LEFT)

        # --- Queries ---
        query_frame = ttk.LabelFrame(self.config_frame_content, text="Queries (Optional)", padding=10)
        query_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 10))
        current_row += 1

        self.q_var = tk.BooleanVar()
        self.q_check = ttk.Checkbutton(query_frame, text="Include Q queries after main input?", variable=self.q_var, command=self.toggle_q_entry)
        self.q_check.pack(anchor=tk.W)

        self.q_details_frame = ttk.Frame(query_frame, padding=(15, 5, 0, 0)) # Indent slightly

        # Q Range
        q_num_frame = ttk.Frame(self.q_details_frame)
        q_num_frame.pack(fill=tk.X, pady=3)
        ttk.Label(q_num_frame, text="Q min:").pack(side=tk.LEFT, padx=(0, 2))
        self.q_min_entry = ttk.Entry(q_num_frame, width=7)
        self.q_min_entry.insert(0, "1")
        self.q_min_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(q_num_frame, text="max:").pack(side=tk.LEFT, padx=(0, 2))
        self.q_max_entry = ttk.Entry(q_num_frame, width=7)
        self.q_max_entry.insert(0, "10")
        self.q_max_entry.pack(side=tk.LEFT)

        # Query Value Range
        q_format_frame = ttk.Frame(self.q_details_frame)
        q_format_frame.pack(fill=tk.X, pady=3)
        ttk.Label(q_format_frame, text="Query Vals min:").pack(side=tk.LEFT, padx=(0, 2))
        self.q_val_min_entry = ttk.Entry(q_format_frame, width=9)
        self.q_val_min_entry.insert(0, "1")
        self.q_val_min_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(q_format_frame, text="max:").pack(side=tk.LEFT, padx=(0, 2))
        self.q_val_max_entry = ttk.Entry(q_format_frame, width=9)
        self.q_val_max_entry.insert(0, "100")
        self.q_val_max_entry.pack(side=tk.LEFT)

        self.toggle_q_entry() # Set initial state

        # --- Generation Button ---
        # Place button in its own frame for centering/padding
        button_frame = ttk.Frame(self.config_frame_content)
        button_frame.grid(row=current_row, column=0, pady=(20, 10))
        button_frame.grid_columnconfigure(0, weight=1) # Center button
        current_row += 1

        self.generate_button = ttk.Button(button_frame, text="Generate Test Cases", command=self.generate_test_cases_async, style='Accent.TButton')
        self.generate_button.grid(row=0, column=0) # Center in frame

        # --- Output Frame (Right Side) ---
        output_outer_frame = ttk.Frame(main_frame) # Add an outer frame for padding
        output_outer_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0,5))
        output_outer_frame.grid_rowconfigure(0, weight=1)
        output_outer_frame.grid_columnconfigure(0, weight=1)

        output_frame = ttk.LabelFrame(output_outer_frame, text="Generated Output", padding=10)
        output_frame.grid(row=0, column=0, sticky="nsew")
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        # Text widget with scrollbars
        text_frame = ttk.Frame(output_frame) # Frame to contain text and scrollbar
        text_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        self.output_text = tk.Text(text_frame, wrap=tk.NONE, width=60, height=25,
                                   borderwidth=1, relief="solid", font=("Courier New", 9),
                                   undo=True, # Enable undo/redo
                                   background="#fdfdfd") # Slightly off-white background
        self.output_text.grid(row=0, column=0, sticky="nsew")

        text_yscroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.output_text.yview)
        text_yscroll.grid(row=0, column=1, sticky="ns")
        self.output_text['yscrollcommand'] = text_yscroll.set

        text_xscroll = ttk.Scrollbar(output_frame, orient="horizontal", command=self.output_text.xview)
        text_xscroll.grid(row=1, column=0, sticky="ew")
        self.output_text['xscrollcommand'] = text_xscroll.set

        # Save Button below text area
        self.save_button = ttk.Button(output_frame, text="Save to File...", command=self.save_to_file, style='Std.TButton')
        self.save_button.grid(row=2, column=0, pady=(10, 0)) # Add padding above

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        status_bar.grid(row=1, column=0, columnspan=2, sticky="sew", padx=0, pady=(5,0)) # Span both columns at the bottom

        # --- Event Bindings for Button Animations (Optional but nice) ---
        # We'll use the built-in ttk states (:hover, :active) configured in the style map
        # No extra bindings needed for the ttk button animations defined via style.map

        self.set_status("Ready. Configure and generate test cases.", "info")


    # --- Helper Methods ---
    def set_status(self, message, level="info"):
        """Updates the status bar with a message and appropriate color."""
        self.status_var.set(message)
        status_bar_widget = self.children['!frame'].children['!label'] # Find status bar widget
        color = self.status_info_color
        if level == "success":
            color = self.status_success_color
        elif level == "warning":
            color = self.status_warning_color
        elif level == "error": # Use messagebox for errors, but maybe color status too
            color = self.status_warning_color # Or a dedicated error color
        status_bar_widget.config(foreground=color)
        # Clear status after a delay
        if level != "info": # Keep 'Ready' message persistent
            self.after(5000, lambda: self.set_status("Ready.", "info") if self.status_var.get() == message else None)


    def toggle_t_entry(self):
        """Shows or hides the entry field for the number of test cases using grid."""
        if self.t_var.get():
            self.t_label.grid(row=0, column=1, sticky="w", padx=(10, 2))
            self.t_entry.grid(row=0, column=2, sticky="w")
        else:
            self.t_label.grid_forget()
            self.t_entry.grid_forget()


    def toggle_q_entry(self):
        """Shows or hides the frame containing query configuration options."""
        if self.q_var.get():
            self.q_details_frame.pack(fill=tk.X, pady=(5,0), anchor='w') # Ensure it packs correctly
        else:
            self.q_details_frame.pack_forget()

    def get_int(self, entry_widget, name, default=None):
        """Safely gets an integer from an Entry widget."""
        try:
            return int(entry_widget.get())
        except ValueError:
            messagebox.showerror("Input Error", f"Invalid integer value for '{name}'. Please enter a whole number.", parent=self)
            self.set_status(f"Error: Invalid integer for {name}", "error")
            return default

    def get_constrained_int(self, min_entry, max_entry, name):
        """Gets min/max from entries, validates, and returns a random int in range."""
        min_val = self.get_int(min_entry, f"{name}_min")
        max_val = self.get_int(max_entry, f"{name}_max")

        if min_val is None or max_val is None:
            return None

        if min_val > max_val:
             messagebox.showerror("Input Error", f"Min value ({min_val}) cannot be greater than Max value ({max_val}) for '{name}'.", parent=self)
             self.set_status(f"Error: Min > Max for {name}", "error")
             return None

        try:
            return random.randint(min_val, max_val)
        except ValueError as e:
            messagebox.showerror("Generation Error", f"Could not generate random integer for '{name}' with range {min_val}-{max_val}.\nError: {e}", parent=self)
            self.set_status(f"Error generating random int for {name}", "error")
            return None

    def get_char_pool(self):
        """Determines the character pool based on user selection."""
        set_type = self.char_set_var.get()
        pool = ""
        if set_type == "lowercase": pool = string.ascii_lowercase
        elif set_type == "uppercase": pool = string.ascii_uppercase
        elif set_type == "digits": pool = string.digits
        elif set_type == "alphanumeric": pool = string.ascii_letters + string.digits
        elif set_type == "custom":
            pool = self.custom_chars_entry.get()
            if not pool:
                messagebox.showerror("Input Error", "Custom character set cannot be empty.", parent=self)
                self.set_status("Error: Custom char set empty", "error")
                return None
        else:
             messagebox.showerror("Internal Error", f"Unknown character set type: {set_type}", parent=self)
             self.set_status("Internal Error: Unknown char set", "error")
             return None

        if not pool:
             messagebox.showerror("Input Error", "Character pool is empty. Cannot generate string.", parent=self)
             self.set_status("Error: Character pool empty", "error")
             return None

        return pool

    # --- Generation Logic (remains largely the same) ---
    def generate_single_case(self):
        """Generates the string output for a single test case."""
        # (This core logic is mostly unchanged, but added error checks setting status)
        lines = []
        vars_generated = {}

        # 1. Generate n, m, k
        first_line_parts = []
        for var_name in ['n', 'm', 'k']:
            is_included, min_entry, max_entry = self.vars_to_include[var_name]
            if is_included.get():
                val = self.get_constrained_int(min_entry, max_entry, var_name)
                if val is None: return None
                vars_generated[var_name] = val
                first_line_parts.append(str(val))
        if first_line_parts: lines.append(" ".join(first_line_parts))

        n = vars_generated.get('n')
        m = vars_generated.get('m')
        input_structure = self.input_type.get()

        # 2. Generate main structure
        num_min = self.get_int(self.num_min_entry, "Value Range Min")
        num_max = self.get_int(self.num_max_entry, "Value Range Max")
        if num_min is None or num_max is None: return None
        if num_min > num_max:
            messagebox.showerror("Input Error", f"Min value ({num_min}) cannot be greater than Max value ({num_max}) for 'Value Range'.", parent=self)
            self.set_status("Error: Min > Max for Value Range", "error")
            return None

        if input_structure == "list_nums":
            if n is None: messagebox.showerror("Config Error", "Cannot generate 'List of N numbers' because 'n' is not selected.", parent=self); self.set_status("Config Error: 'n' needed for list", "error"); return None
            if n < 0: messagebox.showerror("Config Error", f"Cannot generate list for negative N ({n}).", parent=self); self.set_status("Config Error: Negative N for list", "error"); return None
            nums = [str(random.randint(num_min, num_max)) for _ in range(n)]
            lines.append(" ".join(nums))
        elif input_structure == "string_n":
            if n is None: messagebox.showerror("Config Error", "Cannot generate 'String of length N' because 'n' is not selected.", parent=self); self.set_status("Config Error: 'n' needed for string", "error"); return None
            if n < 0: messagebox.showerror("Config Error", f"Cannot generate string for negative N ({n}).", parent=self); self.set_status("Config Error: Negative N for string", "error"); return None
            char_pool = self.get_char_pool();
            if char_pool is None: return None
            lines.append("".join(random.choices(char_pool, k=n)))
        elif input_structure == "string_single":
            str_len = self.get_constrained_int(self.str_len_min_entry, self.str_len_max_entry, "String Length")
            if str_len is None: return None
            if str_len < 0: messagebox.showerror("Config Error", f"Cannot generate string for negative length ({str_len}).", parent=self); self.set_status("Config Error: Negative string length", "error"); return None
            char_pool = self.get_char_pool();
            if char_pool is None: return None
            lines.append("".join(random.choices(char_pool, k=str_len)))
        elif input_structure == "matrix":
            if n is None or m is None: messagebox.showerror("Config Error", "Cannot generate 'N x M Matrix' because 'n' or 'm' is not selected.", parent=self); self.set_status("Config Error: 'n' and 'm' needed for matrix", "error"); return None
            if n < 0 or m < 0: messagebox.showerror("Config Error", f"Cannot generate matrix for negative N ({n}) or M ({m}).", parent=self); self.set_status("Config Error: Negative N/M for matrix", "error"); return None
            for _ in range(n):
                row = [str(random.randint(num_min, num_max)) for _ in range(m)]
                lines.append(" ".join(row))
        elif input_structure == "fixed_vars":
            var_names_str = self.fixed_vars_entry.get()
            if not var_names_str.strip(): messagebox.showerror("Input Error", "Variable names cannot be empty for 'Fixed Variables'.", parent=self); self.set_status("Input Error: Fixed var names empty", "error"); return None
            var_names = var_names_str.split()
            vals = [str(random.randint(num_min, num_max)) for _ in var_names]
            lines.append(" ".join(vals))

        # 3. Generate Queries
        if self.q_var.get():
            q_count = self.get_constrained_int(self.q_min_entry, self.q_max_entry, "Number of Queries (Q)")
            if q_count is None: return None
            if q_count < 0: messagebox.showerror("Config Error", f"Cannot generate negative number of queries ({q_count}).", parent=self); self.set_status("Config Error: Negative Q", "error"); return None

            q_val_min = self.get_int(self.q_val_min_entry, "Query Val Min")
            q_val_max = self.get_int(self.q_val_max_entry, "Query Val Max")
            if q_val_min is None or q_val_max is None: return None
            if q_val_min > q_val_max: messagebox.showerror("Input Error", f"Min value ({q_val_min}) cannot be greater than Max value ({q_val_max}) for 'Query Val Range'.", parent=self); self.set_status("Input Error: Min > Max for Query Vals", "error"); return None

            lines.append(str(q_count))
            for _ in range(q_count):
                q_line = f"{random.randint(q_val_min, q_val_max)} {random.randint(q_val_min, q_val_max)}"
                lines.append(q_line)

        return "\n".join(lines)

    def _perform_generation(self):
        """Internal method to run the generation logic."""
        output_content = []
        generation_successful = True # Flag to track success

        try:
            if self.t_var.get():
                num_test_cases = self.get_int(self.t_entry, "Number of Test Cases (t)")
                if num_test_cases is None: generation_successful = False
                if generation_successful and num_test_cases <= 0:
                    messagebox.showerror("Input Error", "Number of test cases 't' must be positive.", parent=self)
                    self.set_status("Error: 't' must be positive", "error")
                    generation_successful = False
                if generation_successful and num_test_cases > 10000:
                    # Use status bar for warnings
                    self.set_status("Warning: Generating a large number of test cases (> 10000)...", "warning")
                    self.update_idletasks() # Ensure message is shown

                if generation_successful:
                    output_content.append(str(num_test_cases))
                    for i in range(num_test_cases):
                        single_case_output = self.generate_single_case()
                        if single_case_output is None:
                            self.output_text.insert(tk.END, f"--- Error generating test case #{i+1}. Aborting. ---\n")
                            self.set_status(f"Error generating test case #{i+1}", "error")
                            generation_successful = False
                            break # Stop generation on the first error
                        output_content.append(single_case_output)
                        # Optional: Update status periodically for long generations
                        # if i % 100 == 0:
                        #    self.set_status(f"Generating case {i+1}/{num_test_cases}...", "info")
                        #    self.update_idletasks()
            else:
                # Single test case
                single_case_output = self.generate_single_case()
                if single_case_output is None:
                    self.output_text.insert(tk.END, "--- Error generating the test case. ---\n")
                    # Error message already shown by generate_single_case or helpers
                    generation_successful = False
                else:
                    output_content.append(single_case_output)

            # Display result if successful
            if generation_successful:
                self.output_text.delete('1.0', tk.END) # Clear previous output *only if successful*
                final_output = "\n".join(output_content)
                self.output_text.insert(tk.END, final_output)
                if final_output and not final_output.endswith('\n'):
                    self.output_text.insert(tk.END, "\n") # Ensure trailing newline
                self.set_status("Test cases generated successfully! Good luck!", "success")

        except Exception as e:
            # Catch unexpected errors during generation
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred during generation:\n{e}", parent=self)
            self.set_status(f"Unexpected generation error: {e}", "error")
            generation_successful = False

        finally:
            # Re-enable the button regardless of success or failure
            self.generate_button.config(state=tk.NORMAL, text="Generate Test Cases")


    def generate_test_cases_async(self):
        """
        Handles the button state change and calls the generation logic.
        Uses `after(1)` to allow the UI to update before potentially
        long-running generation starts.
        """
        self.output_text.delete('1.0', tk.END) # Clear output area immediately
        self.generate_button.config(state=tk.DISABLED, text="Generating...")
        self.set_status("Generating...", "info")
        self.update_idletasks() # Force UI update to show disabled state/text

        # Run the actual generation slightly delayed to let UI update
        self.after(10, self._perform_generation)


    def save_to_file(self):
        """Saves the content of the output text area to a user-selected file."""
        content = self.output_text.get('1.0', tk.END).rstrip()
        if not content:
            # Use status bar instead of messagebox for this warning
            self.set_status("Warning: Output area is empty. Nothing to save.", "warning")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Input Files", "*.in"), ("All Files", "*.*")],
            title="Save Test Cases As",
            parent=self
        )
        if not filepath:
            self.set_status("Save cancelled.", "info")
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                if not content.endswith('\n'):
                    f.write('\n')
            # Use status bar for success message
            self.set_status(f"Successfully saved to {filepath}. Good luck!", "success")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file:\n{e}", parent=self)
            self.set_status(f"Error saving file: {e}", "error")


if __name__ == "__main__":
    app = TestCaseGeneratorApp()
    app.mainloop()
