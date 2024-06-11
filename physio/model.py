from __future__ import annotations
import math
from typing import Tuple, Optional
from .scenario import Scenario

class ModelUpdateState:
    def __init__(self, carbs : float, insulin : float): 
        self.carbs   = max(0, carbs)
        self.insulin = max(0, insulin)

    @staticmethod
    def zero() -> ModelUpdateState:
        return ModelUpdateState(0, 0)

class Model:
    def __init__(self, scenario : Scenario):
        self.scenario = scenario
        # Initial state
        self.Cg1 = 0
        self.Cg2 = 1
        self.Is  = 1
        self.Im  = 1
        self.I   = 1
        self.Gm  = 400
        self.G   = 1
        
        # Alpha values
        # Acquired from Duke et al. 2009 and tested
        self.alpha_1_c = 0.95
        self.alpha_2_c = 0.09167
        self.alpha_3_c = 250
        
        self.alpha_fi = 0.015
        self.alpha_ci = 0.033
        
        self.alpha_1_ind = 1.2
        
        self.alpha_1_dep = 0.0002
        self.alpha_2_dep = 90
        
        self.alpha_1_clr = 0.043
        self.g_renal_threshold = 0

        self.alpha_1_egp = -0.333
        self.alpha_2_egp = 45
        self.alpha_3_egp = 15

    def output_vector(self) -> Tuple[float, float, float, float, float, float, float]:
        return (
            self.Cg1, self.Cg2,
            self.Is, self.Im, self.I * 1000,
            self.Gm, self.G
        )
    
    def step(self, update_state : Optional[ModelUpdateState] = None) -> None:
        if update_state is None:
            update_state = ModelUpdateState.zero()
            
        # Carbs Consumption and Digestion
        Cg1 = self.Cg1 - self.alpha_1_c * self.Cg1 + update_state.carbs  
        Cg2 = self.Cg2 + self.alpha_1_c * self.Cg1 - self.alpha_2_c / (1 + 25 / self.Cg2) # TODO: magic number
        
        # Insulin Injection and Absorption
        Is = self.Is - self.alpha_fi * self.Is + update_state.insulin
        Im = self.Im + self.alpha_fi * self.Is - self.alpha_ci * self.Im
        
        # Absorption
        d_abs = self.alpha_3_c * self.alpha_2_c / (1 + 25 / self.Cg2)       # TODO: Magic Number
        
        # Insulin independent utilization
        d_ind = self.alpha_1_ind * math.sqrt(self.G)
        
        # Insulin dependent utilization
        d_dep = self.alpha_1_dep * self.I * (self.G + self.alpha_2_dep)
        
        # Renal clearance
        d_clr = (self.G > self.g_renal_threshold) * self.alpha_1_clr * (self.G - self.g_renal_threshold)
        
        # endogenous liver production
        d_egp =  self.alpha_1_egp * self.G + self.alpha_2_egp * math.exp(-self.I / self.alpha_3_egp)

        # Glucose compartment
        Gm = self.Gm + d_abs - d_ind - d_dep - d_clr + d_egp
        
        # Final two states
        
        G = self.Gm / (2.2 * self.scenario.body_mass)
        I = self.Im * self.scenario.insulin_sensitivity / (142 * self.scenario.body_mass)
        
        for value in (d_abs, d_ind, d_dep, d_clr, d_egp):
            print(f'{value:12.8f} | ', end='')
            
        self.Cg1 = Cg1
        self.Cg2 = Cg2
        self.Is  = Is
        self.Im  = Im
        self.Gm  = Gm
        self.G   = G
        self.I   = I