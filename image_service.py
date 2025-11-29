#!/usr/bin/env python3
"""
Image Compositing Service for LinkedIn Posts
Creates professional images with background, text overlay, and logo
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64
from typing import Optional, Tuple
from config import Config

class ImageService:
    """Service for creating and compositing images for LinkedIn posts"""
    
    def __init__(self):
        self.width = Config.IMAGE_WIDTH
        self.height = Config.IMAGE_HEIGHT
        self.logo_size = Config.LOGO_SIZE
    
    def create_gradient_background(self, colors: Tuple[str, str] = ("#1a5f3f", "#2d8659")) -> Image.Image:
        """
        Create a gradient background image
        Default colors: Morocco green shades
        """
        img = Image.new('RGB', (self.width, self.height), colors[0])
        draw = ImageDraw.Draw(img)
        
        # Create vertical gradient
        for y in range(self.height):
            # Interpolate between two colors
            ratio = y / self.height
            r1, g1, b1 = self._hex_to_rgb(colors[0])
            r2, g2, b2 = self._hex_to_rgb(colors[1])
            
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return img
    
    def add_text_overlay(self, img: Image.Image, title: str, subtitle: Optional[str] = None) -> Image.Image:
        """
        Add text overlay to image
        """
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add semi-transparent overlay for better text readability
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([(0, self.height//3), (self.width, 2*self.height//3)], 
                              fill=(0, 0, 0, 100))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # Draw title (centered)
        title_lines = self._wrap_text(title, title_font, self.width - 100)
        y_offset = self.height // 2 - (len(title_lines) * 70) // 2
        
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            
            # Draw text shadow
            draw.text((x+2, y_offset+2), line, font=title_font, fill=(0, 0, 0, 128))
            # Draw main text
            draw.text((x, y_offset), line, font=title_font, fill=(255, 255, 255))
            y_offset += 70
        
        # Draw subtitle if provided
        if subtitle:
            subtitle_lines = self._wrap_text(subtitle, subtitle_font, self.width - 100)
            y_offset += 20
            for line in subtitle_lines:
                bbox = draw.textbbox((0, 0), line, font=subtitle_font)
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                draw.text((x, y_offset), line, font=subtitle_font, fill=(200, 200, 200))
                y_offset += 40
        
        return img
    
    def add_morocco_flag_accent(self, img: Image.Image) -> Image.Image:
        """
        Add Morocco flag colors as accent
        """
        draw = ImageDraw.Draw(img)
        
        # Morocco flag colors: Red (#C1272D) and Green (#006233)
        accent_height = 10
        
        # Red stripe at top
        draw.rectangle([(0, 0), (self.width, accent_height)], fill='#C1272D')
        
        # Green stripe at bottom
        draw.rectangle([(0, self.height - accent_height), (self.width, self.height)], 
                      fill='#006233')
        
        return img
    
    def add_logo(self, img: Image.Image, logo_path: Optional[str] = None) -> Image.Image:
        """
        Add logo to image (bottom right corner)
        If no logo provided, add a text watermark
        """
        if logo_path:
            try:
                logo = Image.open(logo_path)
                logo = logo.resize(self.logo_size, Image.Resampling.LANCZOS)
                
                # Position: bottom right with margin
                position = (self.width - self.logo_size[0] - 30, 
                           self.height - self.logo_size[1] - 30)
                
                # Paste logo (handle transparency)
                if logo.mode == 'RGBA':
                    img.paste(logo, position, logo)
                else:
                    img.paste(logo, position)
            except Exception as e:
                print(f"⚠️  Could not load logo: {e}")
                # Fallback to text watermark
                self._add_text_watermark(img)
        else:
            self._add_text_watermark(img)
        
        return img
    
    def _add_text_watermark(self, img: Image.Image):
        """Add text watermark instead of logo"""
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        text = "Morocco Trends"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        position = (self.width - text_width - 30, self.height - 40)
        
        # Draw with semi-transparent background
        draw.rectangle([(position[0]-10, position[1]-5), 
                       (position[0]+text_width+10, position[1]+25)],
                      fill=(0, 0, 0, 128))
        draw.text(position, text, font=font, fill=(255, 255, 255))
    
    def create_post_image(self, title: str, subtitle: Optional[str] = None, 
                         logo_path: Optional[str] = None,
                         background_image: Optional[str] = None) -> Image.Image:
        """
        Create complete LinkedIn post image
        """
        # Create or load background
        if background_image:
            try:
                img = Image.open(background_image)
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                # Apply slight blur for better text overlay
                img = img.filter(ImageFilter.GaussianBlur(radius=2))
            except Exception as e:
                print(f"⚠️  Could not load background: {e}, using gradient")
                img = self.create_gradient_background()
        else:
            img = self.create_gradient_background()
        
        # Add text overlay
        img = self.add_text_overlay(img, title, subtitle)
        
        # Add Morocco flag accent
        img = self.add_morocco_flag_accent(img)
        
        # Add logo or watermark
        img = self.add_logo(img, logo_path)
        
        return img
    
    def image_to_bytes(self, img: Image.Image, format: str = 'PNG') -> bytes:
        """Convert PIL Image to bytes"""
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=format, quality=95)
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()
    
    def image_to_base64(self, img: Image.Image, format: str = 'PNG') -> str:
        """Convert PIL Image to base64 string"""
        img_bytes = self.image_to_bytes(img, format)
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def save_image(self, img: Image.Image, path: str):
        """Save image to file"""
        img.save(path, quality=95)
        print(f"✅ Image saved: {path}")
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

if __name__ == "__main__":
    # Test the service
    print("🧪 Testing Image Service...\n")
    service = ImageService()
    
    print("🎨 Creating test image...")
    img = service.create_post_image(
        title="Morocco's Digital Transformation",
        subtitle="Leading Africa's Tech Revolution"
    )
    
    output_path = "/home/ubuntu/morocco-bot/test_image.png"
    service.save_image(img, output_path)
    
    print(f"\n✅ Test image created: {output_path}")
    print(f"📐 Dimensions: {img.size[0]}x{img.size[1]}")
