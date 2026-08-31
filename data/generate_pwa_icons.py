import os
import sys

def create_fallback_png(filename, size):
    # Minimal 1x1 transparent PNG data, we will try to make it the requested size but it's hard without zlib
    # For a real implementation, Pillow is needed. This is a very basic fallback that creates a fake PNG or tiny PNG.
    # We'll just write a minimal valid 1x1 transparent PNG. Browser will stretch it.
    minimal_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    with open(filename, 'wb') as f:
        f.write(minimal_png)
    print(f"Fallback created: {filename}")

def generate_icon(size, filename):
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create image with dark blue background
        img = Image.new('RGB', (size, size), color='#1e3a8a')
        draw = ImageDraw.Draw(img)
        
        # Try to draw a golden book/letter representation (simple rectangle for now)
        margin = size // 4
        draw.rectangle([margin, margin, size - margin, size - margin], outline='#fbbf24', width=size//20)
        
        # Save icon
        img.save(filename)
        print(f"Generated: {filename}")
    except ImportError:
        print("Pillow not found, using fallback...")
        create_fallback_png(filename, size)

def main():
    target_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.streamlit', 'static')
    os.makedirs(target_dir, exist_ok=True)
    
    generate_icon(192, os.path.join(target_dir, 'icon-192.png'))
    generate_icon(512, os.path.join(target_dir, 'icon-512.png'))
    print("PWA icons generation complete.")

if __name__ == '__main__':
    main()
