import numpy as np

class SimplexSolver:
    def __init__(self, c, A, b, constraint_types):
        self.c = c
        self.A = A
        self.b = b
        self.constraint_types = constraint_types
        
        self.m, self.n = A.shape
        
       # Step 1: Count slack and artificial variables
        self.num_slack = 0
        self.num_artificial = 0

        for t in constraint_types:
            if t == "<=":
                self.num_slack += 1
            elif t == ">=":
                self.num_slack += 1
                self.num_artificial += 1
            elif t == "=":
                self.num_artificial += 1

        # Step 2: Total columns
        total_cols = self.n + self.num_slack + self.num_artificial + 1  # +1 for RHS

        # Step 3: Initialize tableau
        self.tableau = np.zeros((self.m + 1, total_cols))

        # Step 4: Fill rows
        slack_idx = self.n
        artificial_idx = self.n + self.num_slack

        self.artificial_cols = []

        for i in range(self.m):
            # Original variables
            self.tableau[i, :self.n] = self.A[i]

            if constraint_types[i] == "<=":
                self.tableau[i, slack_idx] = 1
                slack_idx += 1

            elif constraint_types[i] == ">=":
                self.tableau[i, slack_idx] = -1
                slack_idx += 1

                self.tableau[i, artificial_idx] = 1
                self.artificial_cols.append(artificial_idx)
                artificial_idx += 1

            elif constraint_types[i] == "=":
                self.tableau[i, artificial_idx] = 1
                self.artificial_cols.append(artificial_idx)
                artificial_idx += 1

            # RHS
            self.tableau[i, -1] = self.b[i]

        # Step 5: Phase 1 objective (minimize artificial variables)
        for col in self.artificial_cols:
            self.tableau[-1, col] = 1

        # Step 6: Make tableau consistent
        for i in range(self.m):
            if constraint_types[i] in [">=", "="]:
                self.tableau[-1] -= self.tableau[i]
        
        
        print("Artificial columns:", self.artificial_cols)
        print("Tableau shape:", self.tableau.shape)
        print("Initial Phase 1 Tableau:\n", self.tableau)


    def _simplex(self):
        while True:
            z_row = self.tableau[-1, :-1]
            
            neg_indices = np.where(z_row < -1e-8)[0]
            if len(neg_indices) == 0:
                break
            
            pivot_col = None
            
            for col_idx in neg_indices:
                col = self.tableau[:-1, col_idx]
                rhs = self.tableau[:-1, -1]
                
                with np.errstate(divide='ignore'):
                    ratios = np.where(col > 1e-8, rhs / col, np.inf)
                
                if not np.all(ratios == np.inf):
                    pivot_col = col_idx
                    break
            
            # 🔴 CRITICAL: no valid pivot → stop
            if pivot_col is None:
                break
            
            col = self.tableau[:-1, pivot_col]
            rhs = self.tableau[:-1, -1]
            
            with np.errstate(divide='ignore'):
                ratios = np.where(col > 1e-8, rhs / col, np.inf)
            
            pivot_row = np.argmin(ratios)
            
            self._pivot(pivot_row, pivot_col)
        
        return "Optimal"

    def solve(self):
        # -------- Phase 1 --------
        self._simplex()
        
        if abs(self.tableau[-1, -1]) > 1e-5:
            return "Infeasible", None
        
        # -------- Remove artificial variables --------
        self._remove_artificial()
        
        self._restore_basis()
        # -------- Phase 2 setup --------
        self._set_original_objective()
        
        print("After Phase 2 setup:\n", self.tableau)
        
        # -------- Phase 2 solve --------

        
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
        
        # ✅ Correct Z computation
        max_z = np.dot(self.c, var_values)
        
        shadow_prices = -self.tableau[-1, self.n : self.n + self.m]
        
        return {
            "vars": var_values,
            "max_z": max_z,
            "tableau": self.tableau,
            "shadow_prices": shadow_prices
        }
    

    def _remove_artificial(self):
        self.tableau = np.delete(self.tableau, self.artificial_cols, axis=1)
    
    def _set_original_objective(self):
        # Step 1: Reset Z-row
        self.tableau[-1, :] = 0
        
        # Step 2: Set original objective
        self.tableau[-1, :self.n] = -self.c
        
        # Step 3: Adjust Z-row using ALL basic variables
        for i in range(self.m):
            row = self.tableau[i, :-1]
            
            # find basic column
            if np.count_nonzero(row == 1) == 1 and np.count_nonzero(row == 0) == len(row) - 1:
                basic_col = np.where(row == 1)[0][0]
                
                # if this basic variable is an original variable
                if basic_col < self.n:
                    self.tableau[-1] += self.c[basic_col] * self.tableau[i]

    def _fix_basis(self):
        rows, cols = self.tableau.shape
        
        for i in range(self.m):
            row = self.tableau[i, :-1]
            
            # check if row already has a basic variable
            if np.count_nonzero(row == 1) == 1 and np.count_nonzero(row == 0) == len(row) - 1:
                continue
            
            # otherwise, find a pivot column
            for j in range(self.n):  # prefer original variables
                if abs(self.tableau[i, j]) > 1e-5:
                    self._pivot(i, j)
                    break

    def _restore_basis(self):
        for i in range(self.m):
            for j in range(self.tableau.shape[1] - 1):
                col = self.tableau[:, j]
                
                # check if column can be a basis column
                if np.count_nonzero(col[:-1] == 1) == 1 and np.count_nonzero(col[:-1] == 0) == self.m - 1:
                    row_idx = np.where(col[:-1] == 1)[0][0]
                    
                    if row_idx == i:
                        # make pivot exactly 1
                        if abs(self.tableau[i, j] - 1) > 1e-8:
                            self.tableau[i] /= self.tableau[i, j]
                        
                        # eliminate column from others
                        for r in range(self.m + 1):
                            if r != i:
                                self.tableau[r] -= self.tableau[r, j] * self.tableau[i]
                        
                        break