#!/usr/bin/env python3
"""
Professional Image Service - Advanced Template System
Creates stunning, varied professional images for LinkedIn posts
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import random
import math
from typing import Optional, Tuple, List

class ProfessionalImageService:
    """Service for creating professional, template-based images"""
    
    def __init__(self, width=1200, height=630):
        self.width = width
        self.height = height
        
        # Professional color schemes
        self.color_schemes = {
            'tech_blue': {
                'primary': '#1e40af', 'secondary': '#3b82f6', 'accent': '#60a5fa',
                'text': '#ffffff', 'overlay': '#1e3a8a'
            },
            'business_green': {
                'primary': '#065f46', 'secondary': '#059669', 'accent': '#10b981',
                'text': '#ffffff', 'overlay': '#064e3b'
            },
            'innovation_purple': {
                'primary': '#6b21a8', 'secondary': '#9333ea', 'accent': '#c084fc',
                'text': '#ffffff', 'overlay': '#581c87'
            },
            'morocco_red': {
                'primary': '#991b1b', 'secondary': '#dc2626', 'accent': '#ef4444',
                'text': '#ffffff', 'overlay': '#7f1d1d'
            },
            'modern_orange': {
                'primary': '#c2410c', 'secondary': '#ea580c', 'accent': '#fb923c',
                'text': '#ffffff', 'overlay': '#9a3412'
            },
            'professional_navy': {
                'primary': '#1e3a8a', 'secondary': '#2563eb', 'accent': '#3b82f6',
                'text': '#ffffff', 'overlay': '#1e293b'
            },
            'creative_teal': {
                'primary': '#0f766e', 'secondary': '#14b8a6', 'accent': '#5eead4',
                'text': '#ffffff', 'overlay': '#134e4a'
            },
            'elegant_gold': {
                'primary': '#92400e', 'secondary': '#d97706', 'accent': '#fbbf24',
                'text': '#ffffff', 'overlay': '#78350f'
            }
        }
        
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get a font with fallback"""
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except:
            try:
                return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size)
            except:
                return ImageFont.load_default()
    
    def select_scheme(self, topic: str = "") -> dict:
        """Select color scheme based on topic"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['tech', 'digital', 'ai', 'software', 'data', 'cyber']):
            scheme_name = 'tech_blue'
        elif any(word in topic_lower for word in ['business', 'economy', 'market', 'finance', 'trade']):
            scheme_name = 'business_green'
        elif any(word in topic_lower for word in ['morocco', 'maroc', 'maghreb', 'rabat', 'casablanca']):
            scheme_name = 'morocco_red'
        elif any(word in topic_lower for word in ['innovation', 'startup', 'entrepreneur', 'creative']):
            scheme_name = 'innovation_purple'
        elif any(word in topic_lower for word in ['energy', 'power', 'solar', 'renewable']):
            scheme_name = 'modern_orange'
        elif any(word in topic_lower for word in ['design', 'art', 'creative', 'media']):
            scheme_name = 'creative_teal'
        elif any(word in topic_lower for word in ['luxury', 'premium', 'exclusive', 'elite']):
            scheme_name = 'elegant_gold'
        else:
            scheme_name = 'professional_navy'
        
        return self.color_schemes[scheme_name]
    
    def template_modern_gradient(self, title: str, subtitle: str, scheme: dict) -> Image.Image:
        """Template 1: Modern diagonal gradient with geometric elements"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Create diagonal gradient
        primary_rgb = self._hex_to_rgb(scheme['primary'])
        secondary_rgb = self._hex_to_rgb(scheme['secondary'])
        accent_rgb = self._hex_to_rgb(scheme['accent'])
        
        for y in range(self.height):
            for x in range(self.width):
                ratio = (x + y) / (self.width + self.height)
                if ratio < 0.5:
                    r = int(primary_rgb[0] + (secondary_rgb[0] - primary_rgb[0]) * ratio * 2)
                    g = int(primary_rgb[1] + (secondary_rgb[1] - primary_rgb[1]) * ratio * 2)
                    b = int(primary_rgb[2] + (secondary_rgb[2] - primary_rgb[2]) * ratio * 2)
                else:
                    local_ratio = (ratio - 0.5) * 2
                    r = int(secondary_rgb[0] + (accent_rgb[0] - secondary_rgb[0]) * local_ratio)
                    g = int(secondary_rgb[1] + (accent_rgb[1] - secondary_rgb[1]) * local_ratio)
                    b = int(secondary_rgb[2] + (accent_rgb[2] - secondary_rgb[2]) * local_ratio)
                draw.point((x, y), fill=(r, g, b))
        
        # Add geometric circles
        overlay_color = self._hex_to_rgb(scheme['overlay']) + (30,)
        draw.ellipse([self.width - 300, -100, self.width + 100, 300], fill=overlay_color)
        draw.ellipse([-150, self.height - 250, 250, self.height + 150], fill=overlay_color)
        
        # Add text
        self._add_centered_text(draw, title, subtitle, scheme['text'])
        
        return img
    
    def template_split_design(self, title: str, subtitle: str, scheme: dict) -> Image.Image:
        """Template 2: Split screen design with solid colors"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Split background
        primary_rgb = self._hex_to_rgb(scheme['primary'])
        secondary_rgb = self._hex_to_rgb(scheme['secondary'])
        
        # Left side - primary color
        draw.rectangle([0, 0, self.width // 2, self.height], fill=primary_rgb)
        
        # Right side - secondary color
        draw.rectangle([self.width // 2, 0, self.width, self.height], fill=secondary_rgb)
        
        # Add diagonal accent stripe
        accent_rgb = self._hex_to_rgb(scheme['accent'])
        points = [
            (self.width // 2 - 50, 0),
            (self.width // 2 + 50, 0),
            (self.width // 2 + 150, self.height),
            (self.width // 2 + 50, self.height)
        ]
        draw.polygon(points, fill=accent_rgb)
        
        # Add text
        self._add_centered_text(draw, title, subtitle, scheme['text'])
        
        return img
    
    def template_geometric_pattern(self, title: str, subtitle: str, scheme: dict) -> Image.Image:
        """Template 3: Geometric pattern background"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Base gradient
        primary_rgb = self._hex_to_rgb(scheme['primary'])
        secondary_rgb = self._hex_to_rgb(scheme['secondary'])
        
        for y in range(self.height):
            ratio = y / self.height
            r = int(primary_rgb[0] + (secondary_rgb[0] - primary_rgb[0]) * ratio)
            g = int(primary_rgb[1] + (secondary_rgb[1] - primary_rgb[1]) * ratio)
            b = int(primary_rgb[2] + (secondary_rgb[2] - primary_rgb[2]) * ratio)
            draw.rectangle([0, y, self.width, y + 1], fill=(r, g, b))
        
        # Add geometric pattern
        accent_rgb = self._hex_to_rgb(scheme['accent']) + (40,)
        overlay_rgb = self._hex_to_rgb(scheme['overlay']) + (50,)
        
        # Circles pattern
        for i in range(0, self.width + 200, 200):
            for j in range(0, self.height + 200, 200):
                draw.ellipse([i - 80, j - 80, i + 80, j + 80], outline=accent_rgb, width=3)
                draw.ellipse([i - 50, j - 50, i + 50, j + 50], fill=overlay_rgb)
        
        # Add text
        self._add_centered_text(draw, title, subtitle, scheme['text'])
        
        return img
    
    def template_minimalist(self, title: str, subtitle: str, scheme: dict) -> Image.Image:
        """Template 4: Minimalist design with accent bar"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Solid background
        primary_rgb = self._hex_to_rgb(scheme['primary'])
        draw.rectangle([0, 0, self.width, self.height], fill=primary_rgb)
        
        # Accent bar on left
        accent_rgb = self._hex_to_rgb(scheme['accent'])
        draw.rectangle([0, 0, 20, self.height], fill=accent_rgb)
        
        # Subtle geometric elements
        overlay_rgb = self._hex_to_rgb(scheme['overlay']) + (30,)
        draw.rectangle([self.width - 300, 0, self.width, 300], fill=overlay_rgb)
        draw.ellipse([self.width - 200, self.height - 200, self.width + 50, self.height + 50], fill=overlay_rgb)
        
        # Add text
        self._add_centered_text(draw, title, subtitle, scheme['text'])
        
        return img
    
    def template_radial_burst(self, title: str, subtitle: str, scheme: dict) -> Image.Image:
        """Template 5: Radial gradient burst from corner"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Radial gradient from top-right corner
        primary_rgb = self._hex_to_rgb(scheme['primary'])
        accent_rgb = self._hex_to_rgb(scheme['accent'])
        
        center_x, center_y = self.width, 0
        max_distance = math.sqrt(self.width**2 + self.height**2)
        
        for y in range(self.height):
            for x in range(self.width):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                ratio = min(distance / max_distance, 1.0)
                
                r = int(accent_rgb[0] + (primary_rgb[0] - accent_rgb[0]) * ratio)
                g = int(accent_rgb[1] + (primary_rgb[1] - accent_rgb[1]) * ratio)
                b = int(accent_rgb[2] + (primary_rgb[2] - accent_rgb[2]) * ratio)
                draw.point((x, y), fill=(r, g, b))
        
        # Add decorative lines
        secondary_rgb = self._hex_to_rgb(scheme['secondary']) + (60,)
        for i in range(5):
            y_pos = 100 + i * 100
            draw.line([(0, y_pos), (400, y_pos)], fill=secondary_rgb, width=3)
        
        # Add text
        self._add_centered_text(draw, title, subtitle, scheme['text'])
        
        return img
    
    def _add_centered_text(self, draw: ImageDraw.Draw, title: str, subtitle: str, text_color: str):
        """Add centered text with background overlay"""
        text_rgb = self._hex_to_rgb(text_color)
        
        # Create semi-transparent overlay for text
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Dark overlay box
        box_margin = 80
        overlay_draw.rectangle(
            [box_margin, self.height // 2 - 120, self.width - box_margin, self.height // 2 + 120],
            fill=(0, 0, 0, 120)
        )
        
        # Convert overlay to RGB and composite
        img_with_overlay = Image.alpha_composite(
            Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0)),
            overlay
        ).convert('RGB')
        
        # Paste overlay onto main image
        base_img = Image.new('RGB', (self.width, self.height))
        base_img.paste(draw._image)
        base_img.paste(img_with_overlay, (0, 0), img_with_overlay.convert('RGBA'))
        draw._image = base_img
        
        # Add title
        title_font = self._get_font(70)
        title_wrapped = self._wrap_text(title, title_font, self.width - 200)
        
        y_offset = self.height // 2 - 60
        for line in title_wrapped:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y_offset), line, fill=text_rgb, font=title_font)
            y_offset += 80
        
        # Add subtitle if provided
        if subtitle:
            subtitle_font = self._get_font(32)
            subtitle_wrapped = self._wrap_text(subtitle, subtitle_font, self.width - 200)
            
            y_offset += 20
            for line in subtitle_wrapped[:2]:  # Max 2 lines for subtitle
                bbox = draw.textbbox((0, 0), line, font=subtitle_font)
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                draw.text((x, y_offset), line, fill=text_rgb, font=subtitle_font)
                y_offset += 40
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def create_linkedin_image(self, title: str, summary: str = "", topic: str = "") -> Image.Image:
        """Create a professional LinkedIn image with random template"""
        # Select color scheme
        scheme = self.select_scheme(topic or title)
        
        # Select random template
        templates = [
            self.template_modern_gradient,
            self.template_split_design,
            self.template_geometric_pattern,
            self.template_minimalist,
            self.template_radial_burst
        ]
        
        template_func = random.choice(templates)
        
        # Create image
        img = template_func(title, summary[:100] if summary else "", scheme)
        
        # Add Morocco flag accent if Morocco-related
        if any(word in (topic + title).lower() for word in ['morocco', 'maroc', 'maghreb']):
            self._add_morocco_accent(img)
        
        return img
    
    def _add_morocco_accent(self, img: Image.Image):
        """Add subtle Morocco flag accent bars"""
        draw = ImageDraw.Draw(img)
        
        # Red bar (top)
        draw.rectangle([0, 0, self.width, 8], fill='#c1272d')
        
        # Green bar (bottom)
        draw.rectangle([0, self.height - 8, self.width, self.height], fill='#006233')


if __name__ == "__main__":
    # Test the professional image service
    print("🧪 Testing Professional Image Service...\n")
    
    service = ProfessionalImageService()
    
    test_cases = [
        {
            'title': "Morocco's Digital Transformation",
            'summary': "Leading Africa's tech revolution",
            'topic': "technology morocco"
        },
        {
            'title': "The Future of AI in Business",
            'summary': "How artificial intelligence is reshaping industries",
            'topic': "technology ai"
        },
        {
            'title': "Sustainable Energy Solutions",
            'summary': "Renewable power for a greener future",
            'topic': "energy innovation"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"🎨 Test {i}: {test['title']}")
        img = service.create_linkedin_image(
            title=test['title'],
            summary=test['summary'],
            topic=test['topic']
        )
        
        output_path = f"/home/ubuntu/morocco-bot/test_professional_{i}.png"
        img.save(output_path, quality=95)
        print(f"✅ Image created: {output_path}")
        print(f"📐 Dimensions: {img.size[0]}x{img.size[1]}\n")
    
    print("✅ All tests completed!")
