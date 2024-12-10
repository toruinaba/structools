import pytest
from src.steel.sections import LippedChannelSection, SteelSectionProperties

class TestLippedChannelSection:
    """リップ付き溝形鋼のテストクラス"""

    @pytest.fixture
    def section(self):
        """テストで使用する標準的なリップ付き溝形鋼断面"""
        return LippedChannelSection(h=200, b=75, d=20, 
                                  t_w=2.3, t_f=2.3, t_l=2.3)

    def test_initialization(self, section):
        """リップ付き溝形鋼の初期化テスト"""
        assert section.h == 200
        assert section.b == 75
        assert section.d == 20
        assert section.t_w == 2.3
        assert section.t_f == 2.3
        assert section.t_l == 2.3

    def test_area(self, section):
        """リップ付き溝形鋼の断面積計算テスト"""
        # 断面積 = t * (h + 2b + 2d)
        expected_area = 2.3 * (200 + 2*75 + 2*20)
        assert abs(section.area - expected_area) < 0.01

    def test_centroid(self, section):
        """リップ付き溝形鋼の図心位置計算テスト"""
        x, y = section.centroid
        # y方向の図心は高さの中央
        assert abs(y - 100) < 0.01
        # x方向の図心は非対称なため、0より大きい値となる
        assert x > 0

    def test_section_properties(self, section):
        """リップ付き溝形鋼の断面特性計算テスト"""
        props = section.calculate_properties()
        assert isinstance(props, SteelSectionProperties)
        assert props.area > 0
        assert props.moment_of_inertia_x > 0
        assert props.moment_of_inertia_y > 0
        assert props.torsional_constant > 0

    def test_invalid_dimensions(self):
        """不正な寸法に対するバリデーションテスト"""
        with pytest.raises(ValueError):
            LippedChannelSection(h=-200, b=75, d=20, t_w=2.3, t_f=2.3, t_l=2.3)
        
        with pytest.raises(ValueError):
            LippedChannelSection(h=200, b=-75, d=20, t_w=2.3, t_f=2.3, t_l=2.3)
        
        with pytest.raises(ValueError):
            LippedChannelSection(h=200, b=75, d=-20, t_w=2.3, t_f=2.3, t_l=2.3)
        
        with pytest.raises(ValueError):
            LippedChannelSection(h=200, b=75, d=20, t_w=-2.3, t_f=-2.3, t_l=-2.3)
