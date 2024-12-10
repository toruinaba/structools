from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, Dict, Any


# 断面の基本プロトコル
class section_protocol(Protocol):
    @property
    def area(self) -> float:
        """断面積"""
        ...

    @property
    def centroid(self) -> tuple[float, float]:
        """重心位置"""
        ...


# 断面の抽象基底クラス
class base_section(ABC):
    """全ての断面に共通する基本機能を定義"""
    
    @abstractmethod
    def calculate_properties(self) -> Dict[str, Any]:
        """断面性能の計算"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """断面の妥当性検証"""
        pass


# 基本的な断面形状の抽象クラス
class rectangular_section(base_section):
    """矩形断面の基本クラス"""
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    
    @property
    def area(self) -> float:
        return self.width * self.height


class circular_section(base_section):
    """円形断面の基本クラス"""
    def __init__(self, diameter: float):
        self.diameter = diameter


# 薄肉断面の基底クラス
class thin_walled_section(base_section):
    """薄肉断面に共通する機能を定義"""
    
    @abstractmethod
    def calculate_warping_constant(self) -> float:
        """そり定数の計算"""
        pass
    
    @abstractmethod
    def calculate_shear_center(self) -> tuple[float, float]:
        """せん断中心の計算"""
        pass


# 断面性能の基本データクラス
@dataclass
class section_properties:
    """断面性能を保持するデータクラス"""
    area: float
    moment_of_inertia_x: float
    moment_of_inertia_y: float
    torsional_constant: float
