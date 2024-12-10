from ..core.section import SectionProperties
from dataclasses import dataclass
from abc import abstractmethod, ABC
from typing import Tuple, Any


class PositiveFloat:
    """正の浮動小数点数を保証するデータ記述子
    
    :param name: パラメータの名前（エラーメッセージ用）
    :param doc: プロパティのドキュメント文字列
    """
    def __init__(self, name: str, doc: str | None = None):
        self.name = name
        self.private_name = f"_{name}"
        if doc is not None:
            self.__doc__ = doc

    def __get__(self, obj: Any, objtype: Any = None) -> float:
        if obj is None:
            return self
        return getattr(obj, self.private_name)

    def __set__(self, obj: Any, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name}は数値である必要があります")
        if value <= 0:
            raise ValueError(f"{self.name}は正の値である必要があります")
        setattr(obj, self.private_name, float(value))


class SteelSection(ABC):
    """鋼構造断面の抽象基底クラス
    
    全ての鋼構造断面に共通する基本的な断面性能を定義する抽象基底クラス。
    各具体的な断面形状クラスはこのクラスを継承して実装する。
    """
    
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
    """リップ付き溝形鋼の具体的な実装
    
    :param h: ウェブ高さ [mm]
    :param b: フランジ幅 [mm]
    :param d: リップ長さ [mm]
    :param t_w: ウェブ厚 [mm]
    :param t_f: フランジ厚 [mm]
    :param t_l: リップ厚 [mm]
    
    :raises ValueError: 寸法や板厚が0以下の場合
    :raises TypeError: 数値以外が指定された場合
    """
    # 寸法のバリデーション付きプロパティ
    h = PositiveFloat("ウェブ高さ", "ウェブ高さ [mm]")
    b = PositiveFloat("フランジ幅", "フランジ幅 [mm]")
    d = PositiveFloat("リップ長さ", "リップ長さ [mm]")
    t_w = PositiveFloat("ウェブ厚", "ウェブ厚 [mm]")
    t_f = PositiveFloat("フランジ厚", "フランジ厚 [mm]")
    t_l = PositiveFloat("リップ厚", "リップ厚 [mm]")

    def __init__(self, h: float, b: float, d: float, 
                 t_w: float, t_f: float, t_l: float):
        self.h = h
        self.b = b
        self.d = d
        self.t_w = t_w
        self.t_f = t_f
        self.t_l = t_l

    @property
    def area(self) -> float:
        """断面積を計算する

        :return: 断面積 [mm2]
        """
        # 各部材の面積
        web_area = self.h * self.t_w
        flange_area = 2 * self.b * self.t_f
        lip_area = 2 * self.d * self.t_l
        
        # 板厚の重なり部分の面積
        web_flange_overlap = 2 * self.t_w * self.t_f  # ウェブとフランジの重なり
        flange_lip_overlap = 2 * self.t_f * self.t_l   # フランジとリップの重なり
        
        return (web_area + 
                flange_area + 
                lip_area - 
                web_flange_overlap - 
                flange_lip_overlap)

    @property
    def centroid(self) -> Tuple[float, float]:
        """重心位置を計算する

        :return: 重心座標 (x, y) [mm]
        """
        x_c = (2 * self.b * self.t_f * self.b/2 + 
               2 * self.d * self.t_l * (self.b + self.d/2)) / self.area
        y_c = self.h / 2  # 上下対称
        return (x_c, y_c)

    @property
    def moment_of_inertia_strong_web(self) -> float:
        """強軸断面二次モーメントのウェブ寄与分
        
        :return: ウェブ部分の強軸周りの断面二次モーメント [mm4]
        """
        return self.t_w * self.h**3 / 12

    @property
    def moment_of_inertia_strong_flange(self) -> float:
        """強軸断面二次モーメントのフランジ寄与分
        
        :return: フランジ部分の強軸周りの断面二次モーメント [mm4]
        """
        return 2 * (self.t_f * self.b**3 / 12 + 
                   self.b * self.t_f * (self.b/2)**2)

    @property
    def moment_of_inertia_strong_lip(self) -> float:
        """強軸断面二次モーメントのリップ寄与分
        
        :return: リップ部分の強軸周りの断面二次モーメント [mm4]
        """
        return 2 * (self.t_l * self.d**3 / 12 + 
                   self.d * self.t_l * (self.b + self.d/2)**2)

    @property
    def moment_of_inertia_strong(self) -> float:
        """強軸まわりの断面二次モーメントを計算する

        :return: 強軸断面二次モーメント Ix [mm4]
        """
        return (self.moment_of_inertia_strong_web + 
                self.moment_of_inertia_strong_flange + 
                self.moment_of_inertia_strong_lip)

    @property
    def moment_of_inertia_weak_web(self) -> float:
        """弱軸断面二次モーメントのウェブ寄与分
        
        :return: ウェブ部分の弱軸周りの断面二次モーメント [mm4]
        """
        return self.h * self.t_w**3 / 12

    @property
    def moment_of_inertia_weak_flange(self) -> float:
        """弱軸断面二次モーメントのフランジ寄与分
        
        :return: フランジ部分の弱軸周りの断面二次モーメント [mm4]
        """
        return 2 * self.b * self.t_f * (self.h/2)**2

    @property
    def moment_of_inertia_weak_lip(self) -> float:
        """弱軸断面二次モーメントのリップ寄与分
        
        :return: リップ部分の弱軸周りの断面二次モーメント [mm4]
        """
        return 2 * self.d * self.t_l * (self.h/2)**2

    @property
    def moment_of_inertia_weak(self) -> float:
        """弱軸まわりの断面二次モーメントを計算する

        :return: 弱軸断面二次モーメント Iy [mm4]
        """
        return (self.moment_of_inertia_weak_web + 
                self.moment_of_inertia_weak_flange + 
                self.moment_of_inertia_weak_lip)

    @property
    def section_modulus_strong(self) -> float:
        """強軸まわりの断面係数を計算する

        :return: 強軸断面係数 Zx [mm3]
        """
        return self.moment_of_inertia_strong / (self.h/2)

    @property
    def section_modulus_weak(self) -> float:
        """弱軸まわりの断面係数を計算する

        :return: 弱軸断面係数 Zy [mm3]
        """
        x_c = self.centroid[0]
        return self.moment_of_inertia_weak / x_c

    @property
    def torsion_constant(self) -> float:
        """ねじり定数を計算する

        :return: ねじり定数 J [mm4]
        """
        # 薄肉断面の近似式
        return (self.h * self.t_w**3 + 
                2 * self.b * self.t_f**3 + 
                2 * self.d * self.t_l**3) / 3

    @property
    def warping_constant(self) -> float:
        """そり定数を計算する

        :return: そり定数 Cw [mm6]
        """
        # 近似式
        return (self.moment_of_inertia_weak * self.h**2 / 4) * \
               (1 - (3 * self.b) / (2 * self.h))

    @property
    def shear_center(self) -> Tuple[float, float]:
        """せん断中心位置を計算する

        :return: せん断中心座標 (x, y) [mm]
        """
        # リップの影響を考慮した修正係数
        k = 1 + (self.d/self.b)**2 * (self.t_l/self.t_f)
        
        x_s = self.b * (self.h**2 * self.t_w + 
                        4 * self.b * self.t_f * self.h * k) / \
              (4 * self.moment_of_inertia_weak)
        y_s = self.h / 2  # 上下対称
        
        return (x_s, y_s)
    
    def calculate_properties(self) -> SteelSectionProperties:
        """断面性能を計算して返す
        
        :return: 計算された全ての断面性能を含むSteelSectionPropertiesオブジェクト
        """
        return SteelSectionProperties(
            area=self.area,
            moment_of_inertia_x=self.moment_of_inertia_strong,
            moment_of_inertia_y=self.moment_of_inertia_weak,
            torsional_constant=self.torsion_constant,
            plastic_moment_x=self.section_modulus_strong * 1.5,  # 簡易的な計算
            plastic_moment_y=self.section_modulus_weak * 1.5,    # 簡易的な計算
            warping_constant=self.warping_constant,
            shear_center_x=self.shear_center[0],
            shear_center_y=self.shear_center[1]
        )
    
    @property
    def web_width_thickness_ratio(self) -> float:
        """ウェブの幅厚比
        
        :return: ウェブの幅厚比 (h/t_w) [-]
        """
        return self.h / self.t_w

    @property
    def flange_width_thickness_ratio(self) -> float:
        """フランジの幅厚比
        
        :return: フランジの幅厚比 (b/t_f) [-]
        """
        return self.b / self.t_f

    @property
    def lip_width_thickness_ratio(self) -> float:
        """リップの幅厚比
        
        :return: リップの幅厚比 (d/t_l) [-]
        """
        return self.d / self.t_l



class HSection(SteelSection):
    """H形鋼の具体的な実装
    
    :param h: 断面せい [mm]
    :param b: フランジ幅 [mm]
    :param t_w: ウェブ厚 [mm]
    :param t_f: フランジ厚 [mm]
    
    :raises ValueError: 寸法や板厚が0以下の場合
    :raises TypeError: 数値以外が指定された場合
    """
    # 寸法のバリデーション付きプロパティ
    h = PositiveFloat("断面せい", "断面せい [mm]")
    b = PositiveFloat("フランジ幅", "フランジ幅 [mm]")
    t_w = PositiveFloat("ウェブ厚", "ウェブ厚 [mm]")
    t_f = PositiveFloat("フランジ厚", "フランジ厚 [mm]")

    def __init__(self, h: float, b: float, t_w: float, t_f: float):
        self.h = h
        self.b = b
        self.t_w = t_w
        self.t_f = t_f

    @property
    def web_area(self) -> float:
        """ウェブ部分の断面積を計算する

        :return: ウェブの断面積 [mm2]
        """
        return (self.h - 2 * self.t_f) * self.t_w

    @property
    def flange_area(self) -> float:
        """フランジ部分の断面積を計算する

        :return: フランジの断面積 [mm2]（上下フランジの合計）
        """
        return 2 * self.b * self.t_f

    @property
    def area(self) -> float:
        """断面積を計算する

        :return: 断面積 [mm2]
        """
        return self.web_area + self.flange_area

    @property
    def centroid(self) -> Tuple[float, float]:
        """重心位置を計算する

        :return: 重心座標 (x, y) [mm]
        """
        # H形鋼は対称断面のため、重心は断面の中心
        return (self.b/2, self.h/2)

    @property
    def moment_of_inertia_strong(self) -> float:
        """強軸まわりの断面二次モーメントを計算する

        :return: 強軸断面二次モーメント Ix [mm4]
        """
        # ウェブの寄与
        web_i = self.t_w * (self.h - 2*self.t_f)**3 / 12
        # フランジの寄与（平行軸の定理を使用）
        d = (self.h - self.t_f) / 2  # 重心からフランジ重心までの距離
        flange_i = 2 * (self.b * self.t_f**3 / 12 + self.b * self.t_f * d**2)
        return web_i + flange_i

    @property
    def moment_of_inertia_weak(self) -> float:
        """弱軸まわりの断面二次モーメントを計算する

        :return: 弱軸断面二次モーメント Iy [mm4]
        """
        # ウェブの寄与
        web_i = (self.h - 2*self.t_f) * self.t_w**3 / 12
        # フランジの寄与
        flange_i = 2 * (self.t_f * self.b**3 / 12)
        return web_i + flange_i

    @property
    def section_modulus_strong(self) -> float:
        """強軸まわりの断面係数を計算する

        :return: 強軸断面係数 Zx [mm3]
        """
        return self.moment_of_inertia_strong / (self.h/2)

    @property
    def section_modulus_weak(self) -> float:
        """弱軸まわりの断面係数を計算する

        :return: 弱軸断面係数 Zy [mm3]
        """
        return self.moment_of_inertia_weak / (self.b/2)

    @property
    def torsion_constant(self) -> float:
        """ねじり定数を計算する

        :return: ねじり定数 J [mm4]
        """
        # 薄肉断面の近似式
        return ((self.h - 2*self.t_f) * self.t_w**3 + 
                2 * self.b * self.t_f**3) / 3

    @property
    def warping_constant(self) -> float:
        """そり定数を計算する

        :return: そり定数 Cw [mm6]
        """
        # H形鋼のそり定数の計算式
        h_f = self.h - self.t_f  # フランジ重心間距離
        return self.t_f * self.b**3 * h_f**2 / 24

    def calculate_properties(self) -> SteelSectionProperties:
        """断面性能を計算して返す
        
        :return: 計算された全ての断面性能を含むSteelSectionPropertiesオブジェクト
        """
        return SteelSectionProperties(
            area=self.area,
            moment_of_inertia_x=self.moment_of_inertia_strong,
            moment_of_inertia_y=self.moment_of_inertia_weak,
            torsional_constant=self.torsion_constant,
            plastic_moment_x=self.section_modulus_strong * 1.5,  # 簡易的な計算
            plastic_moment_y=self.section_modulus_weak * 1.5,    # 簡易的な計算
            warping_constant=self.warping_constant,
            shear_center_x=self.b/2,  # 対称断面のため重心と一致
            shear_center_y=self.h/2    # 対称断面のため重心と一致
        )

    @property
    def web_width_thickness_ratio(self) -> float:
        """ウェブの幅厚比
        
        :return: ウェブの幅厚比 ((h-2t_f)/t_w) [-]
        """
        return (self.h - 2*self.t_f) / self.t_w

    @property
    def flange_width_thickness_ratio(self) -> float:
        """フランジの幅厚比
        
        :return: フランジの幅厚比 (b/2t_f) [-]
        """
        return (self.b/2) / self.t_f

    def check_width_thickness_ratios(self, steel_grade: str = "SN400") -> dict:
        """幅厚比の制限値との比較を行う
        
        :param steel_grade: 鋼材の強度区分 (デフォルト: "SN400")
        :return: 各部材の幅厚比と制限値の比較結果
        
        使用例:
            >>> section = HSection(400, 200, 8, 13)
            >>> result = section.check_width_thickness_ratios("SN400")
            >>> print(result)
            {
                'web': {'ratio': 46.15, 'limit': 72, 'status': 'OK'},
                'flange': {'ratio': 7.69, 'limit': 12, 'status': 'OK'}
            }
        """
        # 鋼材強度に応じた制限値（JIS G 3136に基づく）
        limits = {
            "SN400": {"web": 72, "flange": 12},
            "SN490": {"web": 67, "flange": 11},
            "SM490": {"web": 67, "flange": 11},
            "SM520": {"web": 60, "flange": 10}
        }
        
        if steel_grade not in limits:
            raise ValueError(f"未対応の鋼材グレード: {steel_grade}")
        
        web_ratio = self.web_width_thickness_ratio
        flange_ratio = self.flange_width_thickness_ratio
        
        return {
            "web": {
                "ratio": round(web_ratio, 2),
                "limit": limits[steel_grade]["web"],
                "status": "OK" if web_ratio <= limits[steel_grade]["web"] else "NG"
            },
            "flange": {
                "ratio": round(flange_ratio, 2),
                "limit": limits[steel_grade]["flange"],
                "status": "OK" if flange_ratio <= limits[steel_grade]["flange"] else "NG"
            }
        }


class BoxSection(SteelSection):
    """箱形断面の具体的な実装"""
    pass
