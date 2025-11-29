#!/usr/bin/env python3
"""
Google Gemini API Service for Content Generation
"""

import google.generativeai as genai
import requests
import json
import base64
from typing import Dict, Optional
from config import Config

class GeminiService:
    """Service for generating LinkedIn content and images using Google Gemini"""
    
    def __init__(self):
        self.api_key = Config.get_gemini_token()
        genai.configure(api_key=self.api_key)
        # Use gemini-2.5-flash (stable and available)
        self.text_model = genai.GenerativeModel('gemini-2.5-flash')
        self.image_api_url = f"{Config.GEMINI_API_URL}/{Config.GEMINI_IMAGE_MODEL}:predict"
    
    def generate_linkedin_content(self, trend_data: Dict) -> Dict:
        """
        Generate LinkedIn post content based on trend data
        Returns: {
            'post_text': str,
            'hashtags': list,
            'image_prompt': str,
            'call_to_action': str
        }
        """
        
        prompt = f"""You are a professional LinkedIn content creator specializing in Morocco-focused posts.

Create an engaging LinkedIn post about this topic:

**Title:** {trend_data.get('title', 'Topic')}
**Summary:** {trend_data.get('summary', 'No summary provided')}
**Emotional Angle:** {trend_data.get('emotionalAngle', 'Professional')}
**Origin:** {trend_data.get('origin', 'General')}

Requirements:
1. Write a compelling LinkedIn post (200-300 words)
2. Professional tone but engaging and conversational
3. Include relevant insights and analysis
4. Add a Moroccan perspective if relevant
5. End with a thought-provoking question or call-to-action
6. Suggest 5-7 relevant hashtags
7. Create a detailed image prompt for AI image generation (describe a professional, eye-catching visual)

Format your response as JSON:
{{
  "post_text": "The main post content here...",
  "hashtags": ["Morocco", "Business", "Innovation", "Leadership", "Growth"],
  "image_prompt": "Professional business scene showing...",
  "call_to_action": "What are your thoughts on this?"
}}

Return ONLY the JSON, no additional text."""

        try:
            response = self.text_model.generate_content(prompt)
            content = response.text
            
            # Extract JSON from response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            generated = json.loads(content)
            
            # Validate required fields
            required_fields = ['post_text', 'hashtags', 'image_prompt', 'call_to_action']
            for field in required_fields:
                if field not in generated:
                    generated[field] = self._get_default_field(field)
            
            return generated
            
        except Exception as e:
            print(f"❌ Gemini Content Generation Error: {e}")
            raise
    
    def generate_image_from_prompt(self, prompt: str) -> Optional['Image.Image']:
        """
        Generate an image using Imagen 3 via REST API
        Returns: PIL Image or None
        """
        from PIL import Image
        import io
        
        # Enhance the prompt for professional LinkedIn images
        enhanced_prompt = f"""Professional LinkedIn post image: {prompt}. Modern, clean, professional style. High quality. Balanced composition. Professional color palette. Inspiring and engaging."""

        try:
            print(f"🎨 Generating AI image: {prompt[:50]}...")
            
            # Use Imagen 3 REST API
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT/locations/us-central1/publishers/google/models/imagen-3.0-generate-001:predict"
            
            # For now, use a simpler approach: Generate with Gemini text-to-image via the SDK
            # Note: Imagen requires Google Cloud project setup
            # As a workaround, we'll use a placeholder and fall back to gradient
            
            print("⚠️  Imagen 3 requires Google Cloud project setup")
            print("🔄 Using enhanced gradient background instead")
            return None
            
        except Exception as e:
            print(f"❌ Image Generation Error: {e}")
            print("⚠️  Falling back to gradient background")
            return None
    
    def research_custom_topic(self, topic: str) -> Dict:
        """
        Research and generate content for a custom topic
        """
        
        prompt = f"""You are a professional content researcher and LinkedIn ghostwriter.

Research and create content about: "{topic}"

Provide:
1. Key insights and analysis
2. Why this matters professionally
3. Moroccan perspective (if relevant)
4. LinkedIn post content (200-300 words)
5. Relevant hashtags
6. Image prompt for visual content
7. Call-to-action

Format as JSON:
{{
  "topic": "{topic}",
  "insights": ["Key insight 1", "Key insight 2", "Key insight 3"],
  "relevance": "Why this matters professionally",
  "moroccan_angle": "Moroccan perspective or 'N/A'",
  "post_text": "Full LinkedIn post content...",
  "hashtags": ["Hashtag1", "Hashtag2", "Hashtag3"],
  "image_prompt": "Description for image generation",
  "call_to_action": "Engaging question or CTA"
}}

Return ONLY the JSON."""

        try:
            response = self.text_model.generate_content(prompt)
            content = response.text
            
            # Extract JSON
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            research = json.loads(content)
            return research
            
        except Exception as e:
            print(f"❌ Custom Topic Research Error: {e}")
            raise
    
    def _get_default_field(self, field: str) -> any:
        """Get default value for missing field"""
        defaults = {
            'post_text': "Exciting developments in Morocco's business landscape!",
            'hashtags': ["Morocco", "Business", "Innovation", "Leadership"],
            'image_prompt': "Modern Moroccan business scene with professionals collaborating",
            'call_to_action': "What are your thoughts on this?"
        }
        return defaults.get(field, "")
    
    def _get_fallback_content(self, trend_data: Dict) -> Dict:
        """Fallback content if API fails"""
        title = trend_data.get('title', 'Topic')
        summary = trend_data.get('summary', '')
        
        return {
            'post_text': f"""🌟 {title}

{summary}

This development represents a significant opportunity for professionals and businesses in Morocco and beyond. As we navigate these changes, it's important to stay informed and adapt our strategies accordingly.

What's your perspective on this trend? How do you see it impacting your industry?

#Morocco #Business #Innovation #Leadership #Growth #ProfessionalDevelopment""",
            'hashtags': ["Morocco", "Business", "Innovation", "Leadership", "Growth", "ProfessionalDevelopment"],
            'image_prompt': f"Professional business scene related to {title}, modern Moroccan setting, inspiring and professional",
            'call_to_action': "Share your thoughts in the comments!"
        }
    
    def format_content_message(self, content: Dict) -> str:
        """Format generated content into a nice Telegram message"""
        
        message = "✨ **LinkedIn Content Generated!**\n\n"
        message += "📝 **Post Content:**\n"
        
        # Handle both Gemini format (post_text) and OpenAI format (hook + content + cta)
        if 'post_text' in content:
            message += f"{content['post_text']}\n\n"
        elif 'hook' in content and 'content' in content:
            # OpenAI/Perplexity format
            message += f"{content['hook']}\n\n"
            message += f"{content['content']}\n\n"
            if 'cta' in content:
                message += f"{content['cta']}\n\n"
        else:
            message += "Content generated successfully\n\n"
        
        message += "🏷️ **Hashtags:**\n"
        hashtags = ' '.join([f"#{tag}" for tag in content.get('hashtags', [])])
        message += f"{hashtags}\n\n"
        
        message += "🎨 **Image Concept:**\n"
        message += f"_{content.get('image_prompt', 'Professional LinkedIn image')}_\n\n"
        
        message += "💬 **Call-to-Action:**\n"
        cta = content.get('call_to_action') or content.get('cta', 'Share your thoughts!')
        message += f"{cta}\n\n"
        
        message += "📤 **Next Steps:**\n"
        message += "• Review and edit if needed\n"
        message += "• Use `/publish` to post to LinkedIn\n"
        message += "• Or use `/scan` to explore more trends"
        
        return message

if __name__ == "__main__":
    # Test the service
    print("🧪 Testing Gemini Service...\n")
    service = GeminiService()
    
    # Test trend data
    test_trend = {
        "title": "Morocco's Digital Transformation Accelerates",
        "summary": "Morocco is rapidly advancing its digital infrastructure with new tech hubs and startup funding initiatives.",
        "emotionalAngle": "Inspiring",
        "origin": "Morocco"
    }
    
    print("📊 Generating LinkedIn content...")
    content = service.generate_linkedin_content(test_trend)
    
    print("\n✅ Content Generated:\n")
    print("="*60)
    print(service.format_content_message(content))
    print("="*60)
