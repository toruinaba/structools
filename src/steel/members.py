from dataclasses import dataclass
from typing import List, Optional, Any
from .sections import steel_section

@dataclass
class beam_member:
    """梁部材クラス"""
    
    section: steel_section
    length: float
    supports: List[float]
    load_cases: Optional[List[Any]] = None
    
    def __post_init__(self):
        self.validate_geometry()
        self.calculate_internal_forces()
    
    def calculate_capacity(self) -> dict:
        """耐力計算"""
        return {
            'moment': self.moment_capacity(),
            'shear': self.shear_capacity(),
            'buckling': self.buckling_capacity()
        }
    
    def check_safety(self) -> dict:
        """安全性照査"""
        capacities = self.calculate_capacity()
        demands = self.calculate_demands()
        return {k: demands[k]/v for k, v in capacities.items()}