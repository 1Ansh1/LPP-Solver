import numpy as np

class SimplexSolver:
    def __init__(self, c, A, b):
        self.c = c  # Objective coefficients
        self.A = A  # Constraint matrix
        self.b = b  # RHS values
        self.m, self.n = A.shape
        
        # Build the Initial Tableau
        # [ A | I | b ]
        # [ -c| 0 | 0 ]
        self.tableau = np.zeros((self.m + 1, self.n + self.m + 1))
        self.tableau[:self.m, :self.n] = self.A
        self.tableau[:self.m, self.n:self.n + self.m] = np.eye(self.m)
        self.tableau[:self.m, -1] = self.b
        self.tableau[-1, :self.n] = -self.c

    def solve(self):
        """Standard Simplex iteration loop."""
        while np.any(self.tableau[-1, :-1] < 0):
            # 1. Identify Pivot Column (Entering Variable)
            pivot_col = np.argmin(self.tableau[-1, :-1])
            
            # 2. Identify Pivot Row (Leaving Variable) using Ratio Test
            ratios = self.tableau[:-1, -1] / self.tableau[:-1, pivot_col]
            # Replace non-positive ratios with infinity to ignore them
            ratios[self.tableau[:-1, pivot_col] <= 0] = np.inf
            
            if np.all(ratios == np.inf):
                return "Unbounded", None
            
            pivot_row = np.argmin(ratios)
            
            # 3. Perform Pivoting (Row Operations)
            self._pivot(pivot_row, pivot_col)
            
        # 4. Extract Results
        results = self._extract_results()
        return "Optimal", results

    def _pivot(self, row, col):
        """Row operations to clear the pivot column."""
        self.tableau[row] /= self.tableau[row, col]
        for r in range(self.tableau.shape[0]):
            if r != row:
                self.tableau[r] -= self.tableau[r, col] * self.tableau[row]

    def _extract_results(self):
        var_values = np.zeros(self.n)
        for j in range(self.n):
            column = self.tableau[:-1, j]
            if np.sum(column == 1) == 1 and np.sum(column == 0) == self.m - 1:
                row_idx = np.where(column == 1)[0][0]
                var_values[j] = self.tableau[row_idx, -1]
        
        max_z = self.tableau[-1, -1]
        
        # --- NEW: Extract Shadow Prices ---
        # Shadow prices are in the Z-row under the slack variable columns
        # Slack columns start after the decision variables (index n)
        shadow_prices = self.tableau[-1, self.n : self.n + self.m]
        
        return {
            "vars": var_values, 
            "max_z": max_z, 
            "tableau": self.tableau,
            "shadow_prices": shadow_prices # <--- Added this
        }