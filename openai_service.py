#!/usr/bin/env python3
"""
OpenAI GPT-4 Content Generation Service
Fallback service for LinkedIn content generation when Gemini is unavailable
"""

import os
import json
from typing import Dict, Optional
from openai import OpenAI

class OpenAIService:
    """Service for generating LinkedIn content using OpenAI GPT-4"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.model = "gpt-4.1-mini"  # Using the available model
    
    def generate_linkedin_content(self, trend_data: Dict) -> Optional[Dict]:
        """
        Generate professional LinkedIn content from trend data.
        
        Args:
            trend_data: Dictionary containing trend information
                - title: Trend title
                - summary: Trend summary
                - emotionalAngle: Emotional angle (optional)
                - origin: Source of the trend (optional)
        
        Returns:
            Dictionary with LinkedIn content or None if generation fails
        """
        try:
            title = trend_data.get("title", "")
            summary = trend_data.get("summary", "")
            emotional_angle = trend_data.get("emotionalAngle", "Informative")
            
            # Create a comprehensive prompt for LinkedIn content
            prompt = f"""You are a professional LinkedIn content creator specializing in engaging, viral posts.

Generate a professional LinkedIn post about this trending topic:

**Topic:** {title}

**Context:** {summary}

**Emotional Angle:** {emotional_angle}

**Requirements:**
1. Write a compelling LinkedIn post (200-300 words)
2. Start with a hook that grabs attention
3. Include relevant insights and takeaways
4. Use professional but conversational tone
5. Add 5-7 relevant hashtags at the end
6. Make it engaging and shareable
7. Focus on value for the reader

**Format your response as JSON:**
{{
    "hook": "Opening sentence that grabs attention",
    "content": "Main body of the LinkedIn post (2-3 paragraphs)",
    "cta": "Call to action or closing thought",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3", "hashtag4", "hashtag5"],
    "image_prompt": "Detailed description for an image that would accompany this post"
}}

Generate the content now:"""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional LinkedIn content strategist who creates viral, engaging posts. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract the response
            content_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                # Remove markdown code blocks if present
                if content_text.startswith("```json"):
                    content_text = content_text.replace("```json", "").replace("```", "").strip()
                elif content_text.startswith("```"):
                    content_text = content_text.replace("```", "").strip()
                
                content_data = json.loads(content_text)
                
                # Ensure all required fields are present
                if not all(key in content_data for key in ["hook", "content", "cta", "hashtags"]):
                    raise ValueError("Missing required fields in response")
                
                # Add source information
                content_data["source"] = "OpenAI GPT-4"
                
                print(f"✅ OpenAI content generated successfully")
                return content_data
                
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured content from text
                print("⚠️  JSON parsing failed, creating structured content from text")
                return {
                    "hook": title,
                    "content": content_text[:500],
                    "cta": "What are your thoughts on this?",
                    "hashtags": ["#LinkedIn", "#Business", "#Innovation", "#Trends", "#Morocco"],
                    "image_prompt": f"Professional image about {title}",
                    "source": "OpenAI GPT-4 (fallback)"
                }
        
        except Exception as e:
            print(f"❌ OpenAI Content Generation Error: {e}")
            return None
    
    def research_custom_topic(self, topic: str) -> Optional[Dict]:
        """
        Research a custom topic and generate insights.
        
        Args:
            topic: The topic to research
        
        Returns:
            Dictionary with research results or None if generation fails
        """
        try:
            prompt = f"""Analyze this topic and provide professional insights for a LinkedIn post:

**Topic:** {topic}

**Provide:**
1. A clear, professional title for this topic
2. Key insights and relevance (why this matters)
3. Current trends or developments
4. Practical takeaways

**Format your response as JSON:**
{{
    "topic": "Clear, professional title",
    "relevance": "Why this topic matters and current trends (2-3 sentences)",
    "insights": "Key insights and takeaways (2-3 sentences)"
}}

Generate the analysis now:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional business analyst. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content_text.startswith("```json"):
                content_text = content_text.replace("```json", "").replace("```", "").strip()
            elif content_text.startswith("```"):
                content_text = content_text.replace("```", "").strip()
            
            research_data = json.loads(content_text)
            research_data["source"] = "OpenAI GPT-4"
            
            print(f"✅ OpenAI research completed successfully")
            return research_data
            
        except Exception as e:
            print(f"❌ OpenAI Research Error: {e}")
            return None


if __name__ == "__main__":
    # Test the OpenAI service
    print("🧪 Testing OpenAI Content Generation Service...\n")
    
    service = OpenAIService()
    
    # Test 1: Generate LinkedIn content
    print("Test 1: Generate LinkedIn content")
    test_trend = {
        "title": "Morocco's Digital Transformation in 2025",
        "summary": "Morocco is leading Africa's digital revolution with innovative startups and government initiatives",
        "emotionalAngle": "Inspiring"
    }
    
    content = service.generate_linkedin_content(test_trend)
    if content:
        print(f"✅ Content generated!")
        print(f"Hook: {content.get('hook', 'N/A')[:100]}...")
        print(f"Hashtags: {', '.join(content.get('hashtags', []))}")
    else:
        print("❌ Content generation failed")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Research custom topic
    print("Test 2: Research custom topic")
    research = service.research_custom_topic("Artificial Intelligence in Healthcare")
    if research:
        print(f"✅ Research completed!")
        print(f"Topic: {research.get('topic', 'N/A')}")
        print(f"Relevance: {research.get('relevance', 'N/A')[:100]}...")
    else:
        print("❌ Research failed")
