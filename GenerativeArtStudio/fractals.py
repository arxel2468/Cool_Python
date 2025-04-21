# fractals.py

import numpy as np
from PIL import Image
import multiprocessing
from numba import njit, prange

@njit(parallel=True)
def compute_mandelbrot(width, height, zoom, max_iter, center):
    image = np.zeros((height, width, 3), dtype=np.uint8)
    x_center, y_center = center
    x_width = 1.5
    y_height = 1.5 * height / width

    for y in prange(height):
        for x in prange(width):
            a = x_center + (x - width / 2) * x_width / (0.5 * zoom * width)
            b = y_center + (y - height / 2) * y_height / (0.5 * zoom * height)
            c = complex(a, b)
            z = 0j
            n = 0

            while (z.real * z.real + z.imag * z.imag) <= 4 and n < max_iter:
                z = z * z + c
                n += 1

            hue = int(255 * n / max_iter)
            saturation = 255
            value = 255 if n < max_iter else 0
            image[y, x] = (hue, saturation, value)
    return image

def mandelbrot(width, height, zoom, max_iter, center=(0, 0)):
    image_array = compute_mandelbrot(width, height, zoom, max_iter, center)
    img = Image.fromarray(image_array, 'HSV').convert('RGB')
    return img

@njit(parallel=True)
def compute_julia(width, height, zoom, max_iter, c_complex, center):
    image = np.zeros((height, width, 3), dtype=np.uint8)
    x_center, y_center = center
    x_width = 1.5
    y_height = 1.5 * height / width

    for y in prange(height):
        for x in prange(width):
            a = x_center + (x - width / 2) * x_width / (0.5 * zoom * width)
            b = y_center + (y - height / 2) * y_height / (0.5 * zoom * height)
            z = complex(a, b)
            n = 0

            while (z.real * z.real + z.imag * z.imag) <= 4 and n < max_iter:
                z = z * z + c_complex
                n += 1

            hue = int(255 * n / max_iter)
            saturation = 255
            value = 255 if n < max_iter else 0
            image[y, x] = (hue, saturation, value)
    return image

def julia(width, height, zoom, max_iter, c_complex, center=(0, 0)):
    image_array = compute_julia(width, height, zoom, max_iter, c_complex, center)
    img = Image.fromarray(image_array, 'HSV').convert('RGB')
    return img
