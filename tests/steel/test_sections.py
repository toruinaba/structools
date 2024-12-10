import pytest
from src.steel.sections import LippedChannelSection, SteelSectionProperties

def test_lipped_channel_section_initialization():
    """リップ付き溝形鋼の初期化テスト"""
    section = LippedChannelSection(h=200, b=75, d=20, 
                                 t_w=2.3, t_f=2.3, t_l=2.3)
    assert section.h == 200
    assert section.b == 75
    assert section.d == 20
    assert section.t_w == 2.3
    assert section.t_f == 2.3
    assert section.t_l == 2.3

def test_lipped_channel_section_area():
    """リップ付き溝形鋼の断面積計算テスト"""
    section = LippedChannelSection(h=200, b=75, d=20, 
                                 t_w=2.3, t_f=2.3, t_l=2.3)
    # 断面積 = t * (h + 2b + 2d)
    expected_area = 2.3 * (200 + 2*75 + 2*20)
    assert abs(section.area - expected_area) < 0.01

def test_lipped_channel_section_centroid():
    """リップ付き溝形鋼の図心位置計算テスト"""
    section = LippedChannelSection(h=200, b=75, d=20, 
                                 t_w=2.3, t_f=2.3, t_l=2.3)
    x, y = section.centroid
    # y方向の図心は高さの中央
    assert abs(y - 100) < 0.01
    # x方向の図心は非対称なため、0より大きい値となる
    assert x > 0

def test_lipped_channel_section_properties():
    """リップ付き溝形鋼の断面特性計算テスト"""
    section = LippedChannelSection(h=200, b=75, d=20, 
                                 t_w=2.3, t_f=2.3, t_l=2.3)
    props = section.calculate_properties()
    assert isinstance(props, SteelSectionProperties)
    assert props.area > 0
    assert props.moment_of_inertia_strong > 0
    assert props.moment_of_inertia_weak > 0
    assert props.torsion_constant > 0

def test_invalid_dimensions():
    """不正な寸法に対するバリデーションテスト"""
    with pytest.raises(ValueError):
        LippedChannelSection(h=-200, b=75, d=20, t_w=2.3, t_f=2.3, t_l=2.3)
    
    with pytest.raises(ValueError):
        LippedChannelSection(h=200, b=-75, d=20, t_w=2.3, t_f=2.3, t_l=2.3)
    
    with pytest.raises(ValueError):
        LippedChannelSection(h=200, b=75, d=-20, t_w=2.3, t_f=2.3, t_l=2.3)
    
    with pytest.raises(ValueError):
        LippedChannelSection(h=200, b=75, d=20, t_w=-2.3, t_f=-2.3, t_l=-2.3)
