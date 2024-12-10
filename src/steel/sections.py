from ..core.section import ThinWalledSection, SectionProperties
from dataclasses import dataclass
from abc import abstractmethod, ABC
from typing import Protocol, Tuple


class SteelSection(ABC):
    """鋼構造断面の抽象基底クラス"""
    
    @property
    @abstractmethod
    def area(self) -> float:
        """断面積"""
        pass

    @property
    @abstractmethod
    def centroid(self) -> Tuple[float, float]:
        """重心位置 (x, y)"""
        pass

    @property
    @abstractmethod
    def moment_of_inertia_strong(self) -> float:
        """強軸断面二次モーメント"""
        pass

    @property
    @abstractmethod
    def moment_of_inertia_weak(self) -> float:
        """弱軸断面二次モーメント"""
        pass

    @property
    @abstractmethod
    def section_modulus_strong(self) -> float:
        """強軸断面係数"""
        pass

    @property
    @abstractmethod
    def section_modulus_weak(self) -> float:
        """弱軸断面係数"""
        pass

    @property
    @abstractmethod
    def torsion_constant(self) -> float:
        """ねじり定数"""
        pass

    @property
    @abstractmethod
    def warping_constant(self) -> float:
        """そり定数"""
        pass

@dataclass
class SteelSectionProperties(SectionProperties):
    """鋼材断面特有の性能値"""
    plastic_moment_x: float
    plastic_moment_y: float
    warping_constant: float
    shear_center_x: float
    shear_center_y: float

class LippedChannelSection(SteelSection):
    """リップ付き溝形鋼の具体的な実装"""
    def __init__(self, h: float, b: float, d: float, 
                 t_w: float, t_f: float, t_l: float):
        self.h = h
        self.b = b
        self.d = d
        self.t_w = t_w
        self.t_f = t_f
        self.t_l = t_l
        self._validate_dimensions()

    @property
    def area(self) -> float:
        """断面積"""
        return (self.h * self.t_w + 
                2 * self.b * self.t_f + 
                2 * self.d * self.t_l)

    @property
    def centroid(self) -> Tuple[float, float]:
        """重心位置 (x, y)"""
        x_c = (2 * self.b * self.t_f * self.b/2 + 
               2 * self.d * self.t_l * (self.b + self.d/2)) / self.area
        y_c = self.h / 2  # 上下対称
        return (x_c, y_c)

    @property
    def moment_of_inertia_strong(self) -> float:
        """強軸断面二次モーメント (Ix)"""
        # ウェブの寄与
        I_web = self.t_w * self.h**3 / 12
        
        # フランジの寄与
        I_flange = 2 * (self.t_f * self.b**3 / 12 + 
                        self.b * self.t_f * (self.b/2)**2)
        
        # リップの寄与
        I_lip = 2 * (self.t_l * self.d**3 / 12 + 
                     self.d * self.t_l * (self.b + self.d/2)**2)
        
        return I_web + I_flange + I_lip

    @property
    def moment_of_inertia_weak(self) -> float:
        """弱軸断面二次モーメント (Iy)"""
        # ウェブの寄与
        I_web = self.h * self.t_w**3 / 12
        
        # フランジの寄与
        I_flange = 2 * self.b * self.t_f * (self.h/2)**2
        
        # リップの寄与
        I_lip = 2 * self.d * self.t_l * (self.h/2)**2
        
        return I_web + I_flange + I_lip

    @property
    def section_modulus_strong(self) -> float:
        """強軸断面係数"""
        return self.moment_of_inertia_strong / (self.h/2)

    @property
    def section_modulus_weak(self) -> float:
        """弱軸断面係数"""
        x_c = self.centroid[0]
        return self.moment_of_inertia_weak / x_c

    @property
    def torsion_constant(self) -> float:
        """ねじり定数 (J)"""
        # 薄肉断面の近似式
        return (self.h * self.t_w**3 + 
                2 * self.b * self.t_f**3 + 
                2 * self.d * self.t_l**3) / 3

    @property
    def warping_constant(self) -> float:
        """そり定数 (Cw)"""
        # 近似式
        return (self.moment_of_inertia_weak * self.h**2 / 4) * \
               (1 - (3 * self.b) / (2 * self.h))

    @property
    def shear_center(self) -> Tuple[float, float]:
        """せん断中心位置 (x, y)"""
        # リップの影響を考慮した修正係数
        k = 1 + (self.d/self.b)**2 * (self.t_l/self.t_f)
        
        x_s = self.b * (self.h**2 * self.t_w + 
                        4 * self.b * self.t_f * self.h * k) / \
              (4 * self.moment_of_inertia_weak)
        y_s = self.h / 2  # 上下対称
        
        return (x_s, y_s)
    
    def calculate_properties(self) -> SteelSectionProperties:
        """断面性能を計算して返す"""
        return SteelSectionProperties(
            moment_of_inertia_x=self.moment_of_inertia_strong,
            moment_of_inertia_y=self.moment_of_inertia_weak,
            torsional_constant=self.torsion_constant,
            plastic_moment_x=self.section_modulus_strong * 1.5,  # 簡易的な計算
            plastic_moment_y=self.section_modulus_weak * 1.5,    # 簡易的な計算
            warping_constant=self.warping_constant,
            shear_center_x=self.shear_center[0],
            shear_center_y=self.shear_center[1]
        )
    
    def _validate_dimensions(self):
        """寸法の妥当性検証"""
        if self.h <= 0 or self.b <= 0 or self.d <= 0:
            raise ValueError("寸法は正の値である必要があります")
        if self.t_w <= 0 or self.t_f <= 0 or self.t_l <= 0:
            raise ValueError("板厚は正の値である必要があります")


class HSection(ThinWalledSection):
    """H形鋼の具体的な実装"""
    pass


class BoxSection(ThinWalledSection):
    """箱形断面の具体的な実装"""
    pass
