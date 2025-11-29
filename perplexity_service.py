#!/usr/bin/env python3
"""
Perplexity API Service for Morocco Trend Discovery
"""

import requests
import json
from typing import List, Dict
from config import Config

class PerplexityService:
    """Service for discovering Morocco trends using Perplexity AI"""
    
    def __init__(self):
        self.api_url = Config.PERPLEXITY_API_URL
        self.model = "sonar"  # Updated to current Perplexity model name
        self.api_key = Config.get_perplexity_token()
    
    def discover_morocco_trends(self) -> List[Dict]:
        """
        Discover trending topics in Morocco
        Returns a list of trend dictionaries with title, summary, and emotional angle
        """
        
        prompt = """You are a trend analyst. Discover the top 10 trending topics right now:
- 5 GLOBAL major events (worldwide significance)
- 5 MOROCCAN major events (specific to Morocco)

For each trend, provide:
1. Title (concise, professional)
2. Summary (2-3 sentences explaining why it matters)
3. Emotional Angle (one word: Inspiring, Concerning, Exciting, Informative, etc.)
4. Origin (Global or Morocco)

Format your response as a JSON array with this structure:
[
  {
    "title": "Event Title",
    "summary": "Brief explanation of the event and its significance.",
    "emotionalAngle": "Inspiring",
    "origin": "Global"
  }
]

Focus on:
- Recent news (last 24-48 hours)
- Professional/business relevance
- Topics suitable for LinkedIn discussion
- Events with social or economic impact

Return ONLY the JSON array, no additional text."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional trend analyst specializing in Morocco and global events. Provide accurate, timely information in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            if not self.api_key:
                print("Warning: Perplexity API key not configured")
                return self._get_fallback_trends()
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Extract JSON from response (sometimes wrapped in markdown)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            trends = json.loads(content)
            
            # Validate and clean trends
            valid_trends = []
            for trend in trends:
                if all(key in trend for key in ['title', 'summary', 'emotionalAngle', 'origin']):
                    valid_trends.append(trend)
            
            return valid_trends
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Perplexity API Error: {e}")
            return self._get_fallback_trends()
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            return self._get_fallback_trends()
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return self._get_fallback_trends()
    
    def research_custom_topic(self, topic: str) -> Dict:
        """
        Research a custom topic and return structured information
        """
        
        prompt = f"""Research this topic: "{topic}"

Provide a comprehensive analysis suitable for a LinkedIn post:
1. Key insights (3-4 bullet points)
2. Why it matters professionally
3. Moroccan perspective (if relevant)
4. Suggested discussion angle

Format as JSON:
{{
  "topic": "{topic}",
  "insights": ["insight 1", "insight 2", "insight 3"],
  "relevance": "Why this matters professionally",
  "moroccan_angle": "Moroccan perspective or 'N/A'",
  "discussion_angle": "Suggested approach for LinkedIn post"
}}

Return ONLY the JSON, no additional text."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional research analyst. Provide accurate, insightful information in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        try:
            if not self.api_key:
                print("Warning: Perplexity API key not configured")
                return self._get_fallback_trends()
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Extract JSON from response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            research = json.loads(content)
            return research
            
        except Exception as e:
            print(f"❌ Research Error: {e}")
            raise
    
    def generate_linkedin_content_direct(self, trend_data: Dict) -> Dict:
        """
        Generate LinkedIn content directly using Perplexity (fallback option)
        This is used when both Gemini and OpenAI fail
        """
        
        title = trend_data.get("title", "")
        summary = trend_data.get("summary", "")
        emotional_angle = trend_data.get("emotionalAngle", "Informative")
        
        prompt = f"""You are a professional LinkedIn content creator. Create an engaging LinkedIn post about this topic:

**Topic:** {title}

**Context:** {summary}

**Emotional Angle:** {emotional_angle}

**Requirements:**
1. Write a compelling LinkedIn post (200-300 words)
2. Start with an attention-grabbing hook
3. Include valuable insights and takeaways
4. Use professional but conversational tone
5. Add 5-7 relevant hashtags
6. Make it shareable and engaging
7. Focus on providing value to readers

**Format your response as JSON:**
{{
    "hook": "Opening sentence that grabs attention",
    "content": "Main body of the LinkedIn post (2-3 paragraphs)",
    "cta": "Call to action or closing thought",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3", "hashtag4", "hashtag5"],
    "image_prompt": "Detailed description for an image that would accompany this post"
}}

Generate the LinkedIn post now:"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional LinkedIn content strategist who creates viral, engaging posts. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Extract JSON from response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            linkedin_content = json.loads(content)
            linkedin_content["source"] = "Perplexity Direct"
            
            print(f"✅ Perplexity direct content generated successfully")
            return linkedin_content
            
        except Exception as e:
            print(f"❌ Perplexity Direct Content Generation Error: {e}")
            raise
    
    def _get_fallback_trends(self) -> List[Dict]:
        """Fallback trends if API fails"""
        return [
            {
                "title": "AI Revolution in Business",
                "summary": "Artificial intelligence continues to transform industries worldwide, with new applications emerging daily.",
                "emotionalAngle": "Exciting",
                "origin": "Global"
            },
            {
                "title": "Morocco's Digital Transformation",
                "summary": "Morocco accelerates its digital economy initiatives with new tech hubs and startup funding.",
                "emotionalAngle": "Inspiring",
                "origin": "Morocco"
            },
            {
                "title": "Sustainable Development Goals",
                "summary": "Global focus on sustainability drives innovation in renewable energy and green technology.",
                "emotionalAngle": "Informative",
                "origin": "Global"
            },
            {
                "title": "Moroccan Tourism Recovery",
                "summary": "Morocco's tourism sector shows strong recovery with record visitor numbers this year.",
                "emotionalAngle": "Positive",
                "origin": "Morocco"
            },
            {
                "title": "Remote Work Evolution",
                "summary": "The future of work continues to evolve with hybrid models becoming the new standard.",
                "emotionalAngle": "Informative",
                "origin": "Global"
            }
        ]

    def format_trends_message(self, trends: List[Dict]) -> str:
        """Format trends into a nice Telegram message"""
        
        global_trends = [t for t in trends if t['origin'] == 'Global']
        morocco_trends = [t for t in trends if t['origin'] == 'Morocco']
        
        message = "🔍 **Morocco Trend Scanner Results**\n\n"
        
        if global_trends:
            message += "🌍 **Global Major Events:**\n\n"
            for i, trend in enumerate(global_trends[:5], 1):
                message += f"**{i}. {trend['title']}**\n"
                message += f"_{trend['summary']}_\n"
                message += f"💭 {trend['emotionalAngle']}\n\n"
        
        if morocco_trends:
            message += "🇲🇦 **Moroccan Major Events:**\n\n"
            for i, trend in enumerate(morocco_trends[:5], 1):
                message += f"**{i+5}. {trend['title']}**\n"
                message += f"_{trend['summary']}_\n"
                message += f"💭 {trend['emotionalAngle']}\n\n"
        
        message += "📝 **To create content about a trend:**\n"
        message += "Reply with the number (1-10) or use:\n"
        message += "`/topic Your custom topic here`"
        
        return message

if __name__ == "__main__":
    # Test the service
    print("🧪 Testing Perplexity Service...\n")
    service = PerplexityService()
    
    print("📊 Discovering Morocco trends...")
    trends = service.discover_morocco_trends()
    
    print(f"\n✅ Found {len(trends)} trends:\n")
    for i, trend in enumerate(trends, 1):
        print(f"{i}. {trend['title']} ({trend['origin']})")
    
    print("\n" + "="*60)
    print("\n📱 Formatted message:")
    print("="*60)
    print(service.format_trends_message(trends))
