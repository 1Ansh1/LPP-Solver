import numpy as np

class SimplexSolver:
    def __init__(self, c, A, b, constraint_types):
        self.c = c
        self.A = A
        self.b = b
        self.constraint_types = constraint_types
        self.steps = []
        self.m, self.n = A.shape
        
      
        self.num_slack = 0
        self.num_artificial = 0
    
        for i in range(self.m):
            if self.b[i] < 0:
                self.b[i] *= -1
                self.A[i] *= -1  

                if self.constraint_types[i] == "<=":
                    self.constraint_types[i] = ">="
                elif self.constraint_types[i] == ">=":
                    self.constraint_types[i] = "<="

        for t in self.constraint_types:
            if t == "<=":
                self.num_slack += 1
            elif t == ">=":
                self.num_slack += 1
                self.num_artificial += 1
            elif t == "=":
                self.num_artificial += 1

    
        total_cols = self.n + self.num_slack + self.num_artificial + 1  # +1 for RHS

    
        self.tableau = np.zeros((self.m + 1, total_cols))

   
        slack_idx = self.n
        artificial_idx = self.n + self.num_slack

        self.artificial_cols = []

        for i in range(self.m):
    
            self.tableau[i, :self.n] = self.A[i]

            if self.constraint_types[i] == "<=":
                self.tableau[i, slack_idx] = 1
                slack_idx += 1

            elif self.constraint_types[i] == ">=":
                self.tableau[i, slack_idx] = -1
                slack_idx += 1

                self.tableau[i, artificial_idx] = 1
                self.artificial_cols.append(artificial_idx)
                artificial_idx += 1

            elif self.constraint_types[i] == "=":
                self.tableau[i, artificial_idx] = 1
                self.artificial_cols.append(artificial_idx)
                artificial_idx += 1

    
            self.tableau[i, -1] = self.b[i]
     
            if self.tableau[i, -1] < 0:
                self.tableau[i, :] *= -1


   
        for col in self.artificial_cols:
            self.tableau[-1, col] = 1

  
        for i in range(self.m):
            if self.constraint_types[i] in [">=", "="]:
                self.tableau[-1] -= self.tableau[i]
        
        
        self._record_step(phase="Phase 1 - Initial")
        print("Artificial columns:", self.artificial_cols)
        print("Tableau shape:", self.tableau.shape)
        print("Initial Phase 1 Tableau:\n", self.tableau)

    def _record_step(self, pivot_row=None, pivot_col=None, phase=""):
        self.steps.append({
            "tableau": self.tableau.copy(),
            "pivot_row": pivot_row,
            "pivot_col": pivot_col,
            "phase": phase
    })
    def _simplex(self):
        while True:
            z_row = self.tableau[-1, :-1]
            
            neg_indices = np.where(z_row < -1e-8)[0]
            if len(neg_indices) == 0:
                break
            
       
            pivot_col = np.argmin(z_row)

   
            col = self.tableau[:-1, pivot_col]
            rhs = self.tableau[:-1, -1]

       
            if np.all(col <= 1e-8):
                return "Unbounded"

   
            with np.errstate(divide='ignore'):
                ratios = np.where(col > 1e-8, rhs / col, np.inf)

            pivot_row = np.argmin(ratios)
            
            col = self.tableau[:-1, pivot_col]
            rhs = self.tableau[:-1, -1]
            if np.all(col <= 1e-8):
                return "Unbounded"

            with np.errstate(divide='ignore'):
                ratios = np.where(col > 1e-8, rhs / col, np.inf)
            
            pivot_row = np.argmin(ratios)
            
            self._pivot(pivot_row, pivot_col)
        
        return "Optimal"

    def solve(self):
  
        self.current_phase = "Phase 1"
        status = self._simplex()
        if status == "Unbounded":
            return "Unbounded", None,self.steps
        
        if abs(self.tableau[-1, -1]) > 1e-5:
            return "Infeasible", None,self.steps
        
     
        self._remove_artificial()
        
        self._restore_basis()
       
  
        self.current_phase = "Phase 2"
        self._record_step(phase="Phase 2 - Start")       
        self._set_original_objective()

        print("After Phase 2 setup:\n", self.tableau)

   
        if len(self.artificial_cols) == 0:
            status = self._simplex()
            if status == "Unbounded":
                return "Unbounded", None,self.steps
        else:
      
            z_row = self.tableau[-1, :-1]
            if np.any(z_row < -1e-8):
                status = self._simplex()
            if status == "Unbounded":
                return "Unbounded", None,self.steps
        
    

        
        results = self._extract_results()
        
        return "Optimal", results,self.steps
        

    def _pivot(self, row, col):
        self.tableau[row] /= self.tableau[row, col]
        for r in range(self.tableau.shape[0]):
            if r != row:
                self.tableau[r] -= self.tableau[r, col] * self.tableau[row]

        self._record_step(pivot_row=row, pivot_col=col, phase=self.current_phase)

    def _extract_results(self):
        var_values = np.zeros(self.n)
        
        for j in range(self.n):
            column = self.tableau[:-1, j]
            if np.sum(column == 1) == 1 and np.sum(column == 0) == self.m - 1:
                row_idx = np.where(column == 1)[0][0]
                var_values[j] = self.tableau[row_idx, -1]
        
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
    
        self.tableau[-1, :] = 0
        
  
        self.tableau[-1, :self.n] = -self.c
        
      
        for i in range(self.m):
            row = self.tableau[i, :-1]
            
      
            if np.count_nonzero(row == 1) == 1 and np.count_nonzero(row == 0) == len(row) - 1:
                basic_col = np.where(row == 1)[0][0]
                
            
                if basic_col < self.n:
                    self.tableau[-1] += self.c[basic_col] * self.tableau[i]

    def _fix_basis(self):
        rows, cols = self.tableau.shape
        
        for i in range(self.m):
            row = self.tableau[i, :-1]
            
        
            if np.count_nonzero(row == 1) == 1 and np.count_nonzero(row == 0) == len(row) - 1:
                continue
            
         
            for j in range(self.n):  
                if abs(self.tableau[i, j]) > 1e-5:
                    self._pivot(i, j)
                    break

    def _restore_basis(self):
        for i in range(self.m):
            for j in range(self.tableau.shape[1] - 1):
                col = self.tableau[:, j]
                
          
                if np.count_nonzero(col[:-1] == 1) == 1 and np.count_nonzero(col[:-1] == 0) == self.m - 1:
                    row_idx = np.where(col[:-1] == 1)[0][0]
                    
                    if row_idx == i:
                
                        if abs(self.tableau[i, j] - 1) > 1e-8:
                            self.tableau[i] /= self.tableau[i, j]
                        
               
                        for r in range(self.m + 1):
                            if r != i:
                                self.tableau[r] -= self.tableau[r, j] * self.tableau[i]
                        
                        break