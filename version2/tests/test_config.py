"""
Tests for infra/config.py — environment loading, validation, and merging.
"""
import os
import pytest
from unittest.mock import patch
from infra.config import UIConfig, LimitsConfig, load_settings, get_app_env, _deep_merge


# ── get_app_env ────────────────────────────────────────────────────────────

def test_get_app_env_dev():
    with patch.dict(os.environ, {"APP_ENV": "dev"}):
        assert get_app_env() == "dev"


def test_get_app_env_prod():
    with patch.dict(os.environ, {"APP_ENV": "prod"}):
        assert get_app_env() == "prod"


def test_get_app_env_invalid():
    with patch.dict(os.environ, {"APP_ENV": "staging"}):
        with pytest.raises(ValueError, match="APP_ENV must be"):
            get_app_env()


def test_get_app_env_defaults_to_dev():
    env = {k: v for k, v in os.environ.items() if k != "APP_ENV"}
    with patch.dict(os.environ, env, clear=True):
        assert get_app_env() == "dev"


# ── UIConfig validators ────────────────────────────────────────────────────

def test_uiconfig_valid_hex_colors():
    cfg = UIConfig(background_color="#ffffff", accent_color="#14b8a6")
    assert cfg.background_color == "#ffffff"


def test_uiconfig_short_hex_valid():
    cfg = UIConfig(background_color="#fff")
    assert cfg.background_color == "#fff"


def test_uiconfig_invalid_color_raises():
    with pytest.raises(Exception, match="Invalid color"):
        UIConfig(background_color="red")


def test_uiconfig_css_injection_rejected():
    with pytest.raises(Exception):
        UIConfig(background_color="#fff; } body { display:none; } /*")


def test_uiconfig_font_size_in_range():
    cfg = UIConfig(body_font_size_rem=1.5)
    assert cfg.body_font_size_rem == 1.5


def test_uiconfig_font_size_too_small_raises():
    with pytest.raises(Exception, match="out of range"):
        UIConfig(body_font_size_rem=0.1)


def test_uiconfig_font_size_too_large_raises():
    with pytest.raises(Exception, match="out of range"):
        UIConfig(body_font_size_rem=10.0)


def test_uiconfig_logo_size_valid():
    cfg = UIConfig(logo_size_px=64)
    assert cfg.logo_size_px == 64


def test_uiconfig_logo_size_out_of_range_raises():
    with pytest.raises(Exception, match="out of range"):
        UIConfig(logo_size_px=512)


# ── LimitsConfig validators ────────────────────────────────────────────────

def test_limitsconfig_valid():
    cfg = LimitsConfig(max_resume_chars=30000, max_upload_mb=3)
    assert cfg.max_resume_chars == 30000


def test_limitsconfig_chars_too_low_raises():
    with pytest.raises(Exception):
        LimitsConfig(max_resume_chars=100)


def test_limitsconfig_mb_too_high_raises():
    with pytest.raises(Exception):
        LimitsConfig(max_upload_mb=100)


# ── _deep_merge ────────────────────────────────────────────────────────────

def test_deep_merge_override_wins():
    base = {"a": 1, "b": {"x": 10, "y": 20}}
    override = {"b": {"x": 99}}
    result = _deep_merge(base, override)
    assert result["b"]["x"] == 99
    assert result["b"]["y"] == 20   # untouched


def test_deep_merge_adds_new_keys():
    base = {"a": 1}
    override = {"b": 2}
    result = _deep_merge(base, override)
    assert result == {"a": 1, "b": 2}


def test_deep_merge_does_not_mutate_base():
    base = {"a": {"x": 1}}
    override = {"a": {"x": 99}}
    _deep_merge(base, override)
    assert base["a"]["x"] == 1   # original unchanged
