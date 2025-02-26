# color_harmony.py

import random
import colorsys

def adjust_hue(hue, degrees):
    # Adjust hue by specified degrees, ensuring it stays within 0-1 range
    return (hue + degrees / 360.0) % 1.0

def generate_palette(harmony='analogous'):
    base_hue = random.random()
    saturation = 0.8
    value = 0.9
    palette = []

    if harmony.lower() == 'complementary':
        # Complementary colors are 180 degrees apart
        hues = [base_hue, adjust_hue(base_hue, 180)]
    elif harmony.lower() == 'triadic':
        # Triadic colors are 120 degrees apart
        hues = [adjust_hue(base_hue, i) for i in [0, 120, 240]]
    elif harmony.lower() == 'tetradic':
        # Tetradic colors are 90 degrees apart
        hues = [adjust_hue(base_hue, i) for i in [0, 90, 180, 270]]
    else:  # Analogous by default
        # Analogous colors within 30 degrees
        hues = [adjust_hue(base_hue, i) for i in [-30, -15, 0, 15, 30]]

    for hue in hues:
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        rgb = (int(r * 255), int(g * 255), int(b * 255))
        palette.append(rgb)

    return palette
