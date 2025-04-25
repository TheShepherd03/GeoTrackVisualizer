#!/usr/bin/env python3
"""
Convert SVG icon to PNG and ICO formats for application use.
"""
import os
import cairosvg
from PIL import Image

# Create icons directory if it doesn't exist
os.makedirs('icons', exist_ok=True)

# Convert SVG to PNG in various sizes
sizes = [16, 32, 48, 64, 128, 256]
png_files = []

for size in sizes:
    output_file = f'icons/app_icon_{size}.png'
    cairosvg.svg2png(
        url='icons/app_icon.svg',
        write_to=output_file,
        output_width=size,
        output_height=size
    )
    png_files.append(output_file)
    print(f"Created {output_file}")

# Create ICO file with multiple sizes
ico_output = 'icons/app_icon.ico'
images = [Image.open(png_file) for png_file in png_files]
images[0].save(
    ico_output,
    format='ICO',
    sizes=[(size, size) for size in sizes],
    append_images=images[1:]
)
print(f"Created {ico_output}")

# Create a 512x512 PNG for high-resolution displays
cairosvg.svg2png(
    url='icons/app_icon.svg',
    write_to='icons/app_icon.png',
    output_width=512,
    output_height=512
)
print("Created icons/app_icon.png (512x512)")

print("Icon conversion complete!")
