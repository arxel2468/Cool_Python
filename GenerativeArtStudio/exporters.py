# exporters.py

import svgwrite

def export_to_svg(pygame_surface, filename):
    width, height = pygame_surface.get_size()
    dwg = svgwrite.Drawing(filename, size=(width, height))

    # Since we're working with raster data (pixels), we need to convert
    # the pixel data into vector graphics. This can be complex and may
    # not produce the desired result, but here is a simple example:

    # Get the pixel array
    pixels = pygame.surfarray.array3d(pygame_surface)
    pixels = pixels.transpose([1, 0, 2])  # Transpose to match image dimensions

    # Simplistic approach: Draw circles for non-white pixels (not efficient)
    for y in range(height):
        for x in range(width):
            color = pixels[y][x]
            if not (color == [255, 255, 255]).all():  # Skip white pixels
                color_hex = svgwrite.utils.rgb(color[0], color[1], color[2])
                dwg.add(dwg.rect(insert=(x, y), size=(1, 1), fill=color_hex))

    dwg.save()
    print(f"Artwork exported as SVG to {filename}")
