import customtkinter as ctk

# Set the look and feel
ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

class LPPSolverApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LPP Solver Pro - Minor Project")
        self.geometry("1100x600")

        # Create Grid System (1 row, 2 columns)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="LPP SOLVER", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.solve_btn = ctk.CTkButton(self.sidebar, text="Solve Problem", command=self.solve_event)
        self.solve_btn.grid(row=1, column=0, padx=20, pady=10)

        # --- INPUT CONTROLS ---
        self.var_label = ctk.CTkLabel(self.sidebar, text="Number of Variables:")
        self.var_label.grid(row=3, column=0, padx=20, pady=(20, 0))
        
        self.var_entry = ctk.CTkEntry(self.sidebar, width=60)
        self.var_entry.insert(0, "2") # Default 2 variables
        self.var_entry.grid(row=4, column=0, padx=20, pady=5)

        self.con_label = ctk.CTkLabel(self.sidebar, text="Number of Constraints:")
        self.con_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        
        self.con_entry = ctk.CTkEntry(self.sidebar, width=60)
        self.con_entry.insert(0, "2") # Default 2 constraints
        self.con_entry.grid(row=6, column=0, padx=20, pady=5)

        self.generate_btn = ctk.CTkButton(self.sidebar, text="Update Grid", command=self.create_input_grid)
        self.generate_btn.grid(row=7, column=0, padx=20, pady=20)
        
        # Keep track of our entry widgets in a list
        self.entries = []

        self.step_btn = ctk.CTkButton(self.sidebar, text="Step-by-Step", fg_color="transparent", border_width=2)
        self.step_btn.grid(row=2, column=0, padx=20, pady=10)

        # --- MAIN CONTENT AREA ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.label = ctk.CTkLabel(self.main_frame, text="Input your Constraints here:", font=ctk.CTkFont(size=16))
        self.label.pack(pady=20)

    def solve_event(self):
        print("Solving...")
    
    def create_input_grid(self):
        # 1. Clear existing grid
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # 2. Get dimensions
        try:
            num_vars = int(self.var_entry.get())
            num_cons = int(self.con_entry.get())
        except ValueError:
            return # Handle empty/invalid input

        self.entries = [] # Reset entries list

        # 3. Create Header (e.g., x1, x2, RHS)
        for j in range(num_vars):
            lbl = ctk.CTkLabel(self.main_frame, text=f"x{j+1}", font=("Arial", 12, "bold"))
            lbl.grid(row=0, column=j, padx=5, pady=5)
        ctk.CTkLabel(self.main_frame, text="RHS", font=("Arial", 12, "bold")).grid(row=0, column=num_vars, padx=5, pady=5)

        # 4. Create Input Rows
        for i in range(num_cons):
            row_entries = []
            for j in range(num_vars + 1): # +1 for the RHS column
                entry = ctk.CTkEntry(self.main_frame, width=60)
                entry.grid(row=i+1, column=j, padx=2, pady=2)
                row_entries.append(entry)
            self.entries.append(row_entries)
            
        # 5. Add Objective Function Row at the bottom
        obj_label = ctk.CTkLabel(self.main_frame, text="Maximize Z =", font=("Arial", 14, "bold"))
        obj_label.grid(row=num_cons+2, column=0, columnspan=2, pady=(20, 0))
        
        self.obj_entries = []
        for j in range(num_vars):
            entry = ctk.CTkEntry(self.main_frame, width=60, fg_color="#2b2b2b", border_color="#1f6aa5")
            entry.grid(row=num_cons+3, column=j, padx=2, pady=5)
            self.obj_entries.append(entry)

if __name__ == "__main__":
    app = LPPSolverApp()
    app.mainloop()