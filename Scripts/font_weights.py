#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fantasque Sans Mono — Shared Weight Name → OS/2 Number Mapping.

Single source of truth for the weight name → OS/2 weight class mapping
(Spec §4.6). Previously duplicated across ``multi_weight_driver.py``
(``WEIGHT_CLASS``), ``generate_specimen.py`` (``_weight_number`` inline
dict) and ``_css_font_faces`` (inline dict) — DRY (PRN-001, REF-014).

This module is intentionally dependency-free (stdlib only).
"""

# OS/2 weight class per weight name (Spec §4.6, r6 Q-08).
WEIGHT_OS2_CLASS = {
    "Light": 300,
    "Regular": 400,
    "Medium": 500,
    "SemiBold": 600,
    "Bold": 700,
    "ExtraBold": 800,
}
