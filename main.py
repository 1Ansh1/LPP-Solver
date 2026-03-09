import customtkinter as ctk
import numpy as np
from solver_engine import SimplexSolver
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

        # In __init__, update the button command:
        self.step_btn.configure(command=self.view_steps_event)

    

        # --- MAIN CONTENT AREA ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.label = ctk.CTkLabel(self.main_frame, text="Input your Constraints here:", font=ctk.CTkFont(size=16))
        self.label.pack(pady=20)
        # --- RESULTS AREA (Initially Hidden or Empty) ---
        self.results_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1e1e1e")
        self.results_frame.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="nsew")
        
        # Labels for display
        self.res_title = ctk.CTkLabel(self.results_frame, text="OPTIMIZATION RESULTS", font=ctk.CTkFont(size=14, weight="bold"))
        self.res_title.pack(pady=10)

        self.z_label = ctk.CTkLabel(self.results_frame, text="Max Z = --", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2ecc71")
        self.z_label.pack(pady=5)

        self.vars_label = ctk.CTkLabel(self.results_frame, text="Variables: --", font=ctk.CTkFont(size=14))
        self.vars_label.pack(pady=10)

    def view_steps_event(self):
        c, A, b = self.get_user_data()
        if c is None: return
        
        solver = SimplexSolver(c, A, b)
        status, results = solver.solve()
        
        if status == "Optimal":
            # Pass the full results dictionary now
            self.show_tableau_popup(results)

    def solve_event(self):
        # 1. Harvest Data
        c, A, b = self.get_user_data()
        if c is None: return 
        
        # 2. Run Solver
        solver = SimplexSolver(c, A, b)
        status, results = solver.solve()
        
        # 3. Update the GUI Results
        if status == "Optimal":
            # Format the Max Z to 2 decimal places
            self.z_label.configure(text=f"Max Z = {results['max_z']:.2f}")
            
            # Format Variables nicely: x1 = 2.00, x2 = 6.00
            var_strings = [f"x{i+1} = {val:.2f}" for i, val in enumerate(results['vars'])]
            self.vars_label.configure(text=" | ".join(var_strings))
            
            # Highlight the frame to show success
            self.results_frame.configure(border_width=2, border_color="#2ecc71")
        else:
            self.z_label.configure(text="No Optimal Solution", text_color="#e74c3c")
            self.vars_label.configure(text=f"Status: {status}")
            self.results_frame.configure(border_width=2, border_color="#e74c3c")
    
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

    def get_user_data(self):
        try:
            # 1. Get Objective Function Coefficients
            # Example: [3, 5] for 3x1 + 5x2
            obj_coeffs = [float(e.get()) for e in self.obj_entries]
            
            # 2. Get Constraint Matrix (A) and RHS values (b)
            matrix_A = []
            rhs_b = []
            
            for row in self.entries:
                # All entries except the last one in the row are coefficients
                coeffs = [float(e.get()) for e in row[:-1]]
                matrix_A.append(coeffs)
                
                # The last entry in each row is the RHS (Right Hand Side)
                rhs_b.append(float(row[-1].get()))
                
            return np.array(obj_coeffs), np.array(matrix_A), np.array(rhs_b)
            
        except ValueError:
            # This triggers if a box is empty or contains a letter
            print("Error: Please enter valid numbers in all boxes.")
            return None, None, None
        

    def show_tableau_popup(self, results):
        tableau = results['tableau']
        rows, cols = tableau.shape
        num_vars = len(results['vars'])
        num_slacks = rows - 1 # Each constraint has a slack

        popup = ctk.CTkToplevel(self)
        popup.title("Final Simplex Tableau")
        popup.geometry("850x500")
        popup.attributes("-topmost", True)

        # Main Header
        title = ctk.CTkLabel(popup, text="OPTIMAL SIMPLEX TABLEAU", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(popup, width=800, height=400)
        scroll_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # 1. GENERATE HEADERS (x1, x2... s1, s2... RHS)
        headers = [f"x{i+1}" for i in range(num_vars)] + \
                  [f"s{i+1}" for i in range(num_slacks)] + \
                  ["RHS"]
        
        # Empty corner label
        ctk.CTkLabel(scroll_frame, text="Basis", font=("Arial", 12, "bold"), text_color="#3498db").grid(row=0, column=0, padx=10, pady=5)

        for j, h in enumerate(headers):
            lbl = ctk.CTkLabel(scroll_frame, text=h, font=("Arial", 12, "bold"), text_color="#3498db")
            lbl.grid(row=0, column=j+1, padx=10, pady=5)

        # 2. GENERATE ROWS
        for i in range(rows):
            # Row Label (Basic Variable or Z)
            row_name = f"Row {i+1}" if i < rows-1 else "Z-Row"
            ctk.CTkLabel(scroll_frame, text=row_name, font=("Arial", 11, "italic")).grid(row=i+1, column=0, padx=10, pady=5)

            for j in range(cols):
                val = f"{tableau[i, j]:.2f}"
                
                # Logic for cell styling
                is_z_row = (i == rows - 1)
                is_rhs_col = (j == cols - 1)
                
                # Default style
                text_col = "white"
                bg_col = "transparent"
                
                if is_z_row:
                    text_col = "#2ecc71" # Green for the final objective row
                if is_rhs_col:
                    bg_col = "#2c3e50" # Darker background for RHS
                
                cell = ctk.CTkLabel(scroll_frame, text=val, text_color=text_col, 
                                   fg_color=bg_col, corner_radius=4, width=70)
                cell.grid(row=i+1, column=j+1, padx=5, pady=5)  

if __name__ == "__main__":
    app = LPPSolverApp()
    app.mainloop()