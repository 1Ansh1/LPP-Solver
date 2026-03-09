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

        self.step_btn = ctk.CTkButton(self.sidebar, text="Step-by-Step", fg_color="transparent", border_width=2)
        self.step_btn.grid(row=2, column=0, padx=20, pady=10)

        # --- MAIN CONTENT AREA ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.label = ctk.CTkLabel(self.main_frame, text="Input your Constraints here:", font=ctk.CTkFont(size=16))
        self.label.pack(pady=20)

    def solve_event(self):
        print("Solving...")

if __name__ == "__main__":
    app = LPPSolverApp()
    app.mainloop()