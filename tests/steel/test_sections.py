import pytest
from src.steel.sections import LippedChannelSection, SteelSectionProperties, HSection

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
        # 各部材の面積
        web_area = 200 * 2.3
        flange_area = 2 * 75 * 2.3
        lip_area = 2 * 20 * 2.3
        # 重なり部分を差し引く
        overlap_area = 2 * 2.3 * 2.3  # ウェブとフランジの重なり
        overlap_area += 2 * 2.3 * 2.3  # フランジとリップの重なり
        expected_area = web_area + flange_area + lip_area - overlap_area
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

    def test_moment_of_inertia_strong_components(self, section):
        """強軸断面二次モーメントの各成分テスト"""
        # 各成分が正の値
        assert section.moment_of_inertia_strong_web > 0
        assert section.moment_of_inertia_strong_flange > 0
        assert section.moment_of_inertia_strong_lip > 0
        
        # 合計が全体の値と一致
        total = (section.moment_of_inertia_strong_web + 
                section.moment_of_inertia_strong_flange + 
                section.moment_of_inertia_strong_lip)
        assert abs(total - section.moment_of_inertia_strong) < 0.01

    def test_moment_of_inertia_weak_components(self, section):
        """弱軸断面二次モーメントの各成分テスト"""
        # 各成分が正の値
        assert section.moment_of_inertia_weak_web > 0
        assert section.moment_of_inertia_weak_flange > 0
        assert section.moment_of_inertia_weak_lip > 0
        
        # 合計が全体の値と一致
        total = (section.moment_of_inertia_weak_web + 
                section.moment_of_inertia_weak_flange + 
                section.moment_of_inertia_weak_lip)
        assert abs(total - section.moment_of_inertia_weak) < 0.01

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

    def test_width_thickness_ratios(self, section):
        """幅厚比の計算テスト"""
        # 期待値の計算
        expected_web_ratio = 200 / 2.3
        expected_flange_ratio = 75 / 2.3
        expected_lip_ratio = 20 / 2.3

        # 計算値と期待値の比較
        assert abs(section.web_width_thickness_ratio - expected_web_ratio) < 0.01
        assert abs(section.flange_width_thickness_ratio - expected_flange_ratio) < 0.01
        assert abs(section.lip_width_thickness_ratio - expected_lip_ratio) < 0.01


class TestHSection:
    """H形鋼のテストクラス"""

    @pytest.fixture
    def section(self):
        """テストで使用する標準的なH形鋼断面"""
        return HSection(h=400, b=200, t_w=8, t_f=13)

    def test_initialization(self, section):
        """H形鋼の初期化テスト"""
        assert section.h == 400
        assert section.b == 200
        assert section.t_w == 8
        assert section.t_f == 13

    def test_invalid_dimensions(self):
        """不正な寸法でのエラー処理テスト"""
        with pytest.raises(ValueError):
            HSection(-400, 200, 8, 13)  # 負の値
        with pytest.raises(ValueError):
            HSection(400, 0, 8, 13)     # ゼロ値
        with pytest.raises(TypeError):
            HSection("400", 200, 8, 13)  # 文字列

    def test_area_calculations(self, section):
        """断面積計算のテスト"""
        # 個別の面積
        expected_web_area = (400 - 2*13) * 8
        expected_flange_area = 2 * 200 * 13
        
        assert section.web_area == pytest.approx(expected_web_area)
        assert section.flange_area == pytest.approx(expected_flange_area)
        
        # 全体の面積
        expected_total_area = expected_web_area + expected_flange_area
        assert section.area == pytest.approx(expected_total_area)

    def test_moment_of_inertia(self, section):
        """断面二次モーメントのテスト"""
        # 強軸
        Ix = section.moment_of_inertia_strong
        assert Ix > 0
        assert isinstance(Ix, float)
        
        # 弱軸
        Iy = section.moment_of_inertia_weak
        assert Iy > 0
        assert isinstance(Iy, float)
        assert Ix > Iy  # 強軸の方が大きいことを確認

    def test_section_modulus(self, section):
        """断面係数のテスト"""
        # 強軸
        Zx = section.section_modulus_strong
        assert Zx == pytest.approx(section.moment_of_inertia_strong / (section.h/2))
        
        # 弱軸
        Zy = section.section_modulus_weak
        assert Zy == pytest.approx(section.moment_of_inertia_weak / (section.b/2))

    def test_width_thickness_ratios(self, section):
        """幅厚比のテスト"""
        expected_web_ratio = (400 - 2*13) / 8
        expected_flange_ratio = (200/2) / 13
        
        assert section.web_width_thickness_ratio == pytest.approx(expected_web_ratio)
        assert section.flange_width_thickness_ratio == pytest.approx(expected_flange_ratio)

    def test_width_thickness_check(self, section):
        """幅厚比制限値チェックのテスト"""
        # SN400での確認
        result = section.check_width_thickness_ratios("SN400")
        assert "web" in result
        assert "flange" in result
        assert all(key in result["web"] for key in ["ratio", "limit", "status"])
        assert all(key in result["flange"] for key in ["ratio", "limit", "status"])
        
        # 未対応の鋼材グレード
        with pytest.raises(ValueError):
            section.check_width_thickness_ratios("INVALID")

    def test_calculate_properties(self, section):
        """断面性能計算メソッドのテスト"""
        props = section.calculate_properties()
        
        assert isinstance(props, SteelSectionProperties)
        assert props.area == pytest.approx(section.area)
        assert props.moment_of_inertia_x == pytest.approx(section.moment_of_inertia_strong)
        assert props.moment_of_inertia_y == pytest.approx(section.moment_of_inertia_weak)
        assert props.torsional_constant == pytest.approx(section.torsion_constant)
        assert props.warping_constant == pytest.approx(section.warping_constant)

    def test_centroid(self, section):
        """重心位置のテスト"""
        x, y = section.centroid
        
        # H形鋼は対称断面なので、重心は幾何学的中心
        assert x == pytest.approx(section.b/2)
        assert y == pytest.approx(section.h/2)
