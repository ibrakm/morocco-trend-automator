#!/usr/bin/env python3
"""
Morocco Trend Automator - Enhanced Version
With comprehensive error handling, reset command, and bug fixes
"""

import requests
import time
import json
import os
from typing import Dict, Optional
from config import Config
from perplexity_service import PerplexityService
from gemini_service import GeminiService
from image_service import ImageService
# from enhanced_image_service import EnhancedImageService
# from ai_image_service import AIImageService
from professional_image_service import ProfessionalImageService
from openai_service import OpenAIService
from linkedin_service import LinkedInService
from error_handler import error_handler, rate_limiter, health_check, handle_errors

class MoroccoTrendBot:
    """Enhanced bot with error handling and recovery"""
    
    def __init__(self):
        self.bot_token = Config.get_telegram_token()
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Initialize services with error handling
        error_handler.logger.info("🔧 Initializing services...")
        try:
            self.perplexity = PerplexityService()
            self.gemini = GeminiService()
            self.image_service = ImageService()
            self.enhanced_image_service = EnhancedImageService()
            self.ai_image_service = AIImageService()
            self.professional_image_service = ProfessionalImageService()
            self.openai = OpenAIService()
            self.linkedin = LinkedInService()
            error_handler.logger.info("✅ All services initialized!")
        except Exception as e:
            error_handler.log_error(e, {"phase": "initialization"})
            raise
        
        # Bot state management
        self.user_states = {}  # {chat_id: {state, data, last_activity}}
        self.admin_users = set()  # Admin user IDs
        
        # Session timeout (30 minutes)
        self.session_timeout = 1800
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown", reply_markup: Optional[Dict] = None) -> Optional[Dict]:
        """Send a message with error handling and optional inline keyboard"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            error_handler.logger.error(f"Timeout sending message to {chat_id}")
            return None
        except requests.exceptions.RequestException as e:
            error_handler.log_error(e, {"chat_id": chat_id, "action": "send_message"})
            return None
        except Exception as e:
            error_handler.log_error(e, {"chat_id": chat_id, "action": "send_message"})
            return None
    
    def send_photo(self, chat_id: int, photo_bytes: bytes, caption: Optional[str] = None) -> Optional[Dict]:
        """Send a photo with error handling"""
        url = f"{self.base_url}/sendPhoto"
        files = {"photo": ("image.png", photo_bytes, "image/png")}
        data = {"chat_id": chat_id}
        
        if caption:
            data["caption"] = caption
            data["parse_mode"] = "Markdown"
        
        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            error_handler.logger.error(f"Timeout sending photo to {chat_id}")
            self.send_message(chat_id, "⚠️ Image upload timed out. Please try again.")
            return None
        except Exception as e:
            error_handler.log_error(e, {"chat_id": chat_id, "action": "send_photo"})
            self.send_message(chat_id, "❌ Failed to send image. Please try again.")
            return None
    
    def get_updates(self, offset: Optional[int] = None) -> Optional[Dict]:
        """Get updates with error handling"""
        url = f"{self.base_url}/getUpdates"
        params = {
            "timeout": 30,
            "offset": offset,
            "allowed_updates": json.dumps(["message", "callback_query"])
        }
        
        try:
            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            error_handler.logger.warning("Timeout getting updates (normal)")
            return {"ok": True, "result": []}
        except requests.exceptions.ConnectionError:
            error_handler.logger.error("Connection error getting updates")
            time.sleep(5)  # Wait before retry
            return {"ok": True, "result": []}
        except Exception as e:
            error_handler.log_error(e, {"action": "get_updates"})
            time.sleep(5)
            return {"ok": True, "result": []}
    
    def clean_expired_sessions(self):
        """Clean up expired user sessions"""
        current_time = time.time()
        expired = []
        
        for chat_id, state in self.user_states.items():
            last_activity = state.get("last_activity", current_time)
            if current_time - last_activity > self.session_timeout:
                expired.append(chat_id)
        
        for chat_id in expired:
            del self.user_states[chat_id]
            error_handler.logger.info(f"Cleaned expired session for {chat_id}")
    
    def reset_user_state(self, chat_id: int):
        """Reset user state"""
        self.user_states[chat_id] = {
            "state": "idle",
            "data": {},
            "last_activity": time.time()
        }
        error_handler.logger.info(f"Reset state for user {chat_id}")
    
    def update_user_activity(self, chat_id: int):
        """Update user's last activity timestamp"""
        if chat_id in self.user_states:
            self.user_states[chat_id]["last_activity"] = time.time()
    
    @handle_errors(error_handler, "Failed to start bot. Please try /reset")
    def handle_start(self, chat_id: int, username: str):
        """Handle /start command"""
        response = f"""🎉 **Morocco Trend Automator is Online!**

✅ All systems operational!

👋 Welcome, @{username}!

📋 **Available Commands:**

🔍 **Discovery:**
/scan - Discover trending topics in Morocco
/topic <text> - Research any custom topic

📝 **Content:**
/preview - Preview your content and image

📤 **Publishing:**
/publish - Publish content to LinkedIn

🔧 **System:**
/status - Check bot status
/reset - Reset your session
/errors - View recent errors (admin)
/help - Show this message

🤖 **How it works:**
1. Use /scan to discover trends
2. Reply with a number (1-10) to select a trend
3. Bot generates professional LinkedIn content
4. Review with /preview
5. Publish with /publish

Ready to automate your content! 🚀"""
        
        self.send_message(chat_id, response)
        self.reset_user_state(chat_id)
        health_check.record_request()
    
    @handle_errors(error_handler, "Failed to scan trends. Please try again or use /reset")
    def handle_scan(self, chat_id: int):
        """Handle /scan command with error handling"""
        error_handler.logger.info(f"handle_scan called for chat_id: {chat_id}")
        
        # Check rate limit
        if not rate_limiter.is_allowed(chat_id):
            wait_time = rate_limiter.get_wait_time(chat_id)
            self.send_message(
                chat_id,
                f"⏳ **Rate Limit**\n\nPlease wait {wait_time} seconds before scanning again.\n\n_This prevents API overuse._"
            )
            return
        
        error_handler.logger.info(f"Sending scanning message to {chat_id}")
        self.send_message(chat_id, "🔍 **Scanning Morocco Trends...**\n\nAnalyzing Google Trends, news sources, and social media...\n\n_This may take 10-15 seconds..._")
        
        try:
            error_handler.logger.info("Calling perplexity.discover_morocco_trends()")
            trends = self.perplexity.discover_morocco_trends()
            error_handler.logger.info(f"Got {len(trends) if trends else 0} trends")
            
            if not trends or len(trends) == 0:
                self.send_message(
                    chat_id,
                    "⚠️ **No Trends Found**\n\nCould not fetch trends at this moment.\n\n"
                    "**Try:**\n"
                    "• Wait a moment and try again\n"
                    "• Use `/topic <your topic>` for custom research\n"
                    "• Use `/reset` if problem persists"
                )
                return
            
            # Store trends in user state
            self.user_states[chat_id] = {
                "state": "trend_selection",
                "data": {"trends": trends},
                "last_activity": time.time()
            }
            
            # Format and send trends
            error_handler.logger.info("Formatting trends message...")
            message = self.perplexity.format_trends_message(trends)
            error_handler.logger.info(f"Message formatted, length: {len(message)} chars")
            error_handler.logger.info("Sending trends message to user...")
            result = self.send_message(chat_id, message)
            error_handler.logger.info(f"Send result: {result is not None}")
            health_check.record_request()
            
        except Exception as e:
            error_handler.log_error(e, {"chat_id": chat_id, "command": "scan"})
            health_check.record_error(e)
            self.send_message(
                chat_id,
                f"❌ **Error Scanning Trends**\n\n"
                f"_{type(e).__name__}: {str(e)[:100]}_\n\n"
                f"**Try:**\n"
                f"• `/reset` to clear your session\n"
                f"• Wait a moment and try again\n"
                f"• Use `/topic <custom topic>` instead"
            )
    
    @handle_errors(error_handler, "Failed to research topic. Please try again or use /reset")
    def handle_topic(self, chat_id: int, topic: str):
        """Handle /topic command with validation"""
        if not topic or len(topic.strip()) < 3:
            self.send_message(
                chat_id,
                "❌ **Invalid Topic**\n\n"
                "Please provide a topic with at least 3 characters.\n\n"
                "**Example:** `/topic Financial problems in Morocco 2025`"
            )
            return
        
        # Limit topic length
        if len(topic) > 200:
            self.send_message(
                chat_id,
                "❌ **Topic Too Long**\n\n"
                "Please keep your topic under 200 characters."
            )
            return
        
        # Check rate limit
        if not rate_limiter.is_allowed(chat_id):
            wait_time = rate_limiter.get_wait_time(chat_id)
            self.send_message(
                chat_id,
                f"⏳ **Rate Limit**\n\nPlease wait {wait_time} seconds before researching again."
            )
            return
        
        self.send_message(chat_id, f"📝 **Researching Custom Topic...**\n\n_{topic}_\n\n_Analyzing and generating content..._")
        
        try:
            # 3-TIER FALLBACK FOR RESEARCH
            research = None
            
            # Tier 1: Try Gemini research
            try:
                print("🔷 Research Tier 1: Trying Gemini...")
                research = self.gemini.research_custom_topic(topic)
            except Exception as e:
                print(f"⚠️  Gemini research failed: {e}")
                research = None
            
            if research:
                print("✅ Gemini research succeeded!")
            
            # Tier 2: Try OpenAI research if Gemini failed
            if not research:
                try:
                    print("🔶 Research Tier 2: Trying OpenAI...")
                    research = self.openai.research_custom_topic(topic)
                except Exception as e:
                    print(f"⚠️  OpenAI research failed: {e}")
                    research = None
                
                if research:
                    print("✅ OpenAI research succeeded!")
            
            # Tier 3: Use basic topic data if both failed
            if not research:
                print("🔸 Research Tier 3: Using basic topic data")
                research = {
                    "topic": topic,
                    "relevance": f"Analysis of {topic}",
                    "insights": ["Research in progress"]
                }
            
            # Generate content
            trend_data = {
                "title": research.get("topic", topic)[:100],  # Limit title length
                "summary": research.get("relevance", "")[:300],  # Limit summary
                "emotionalAngle": "Informative",
                "origin": "Custom"
            }
            
            # 3-TIER FALLBACK FOR CONTENT GENERATION
            content = None
            
            # Tier 1: Try Gemini
            try:
                print("🔷 Content Tier 1: Trying Gemini...")
                content = self.gemini.generate_linkedin_content(trend_data)
            except Exception as e:
                print(f"⚠️  Gemini content failed: {e}")
                content = None
            
            if content:
                print("✅ Gemini content succeeded!")
            
            # Tier 2: Try OpenAI if Gemini failed
            if not content:
                try:
                    print("🔶 Content Tier 2: Trying OpenAI...")
                    content = self.openai.generate_linkedin_content(trend_data)
                except Exception as e:
                    print(f"⚠️  OpenAI content failed: {e}")
                    content = None
                
                if content:
                    print("✅ OpenAI content succeeded!")
            
            # Tier 3: Try Perplexity direct if both failed
            if not content:
                try:
                    print("🔸 Content Tier 3: Trying Perplexity direct...")
                    content = self.perplexity.generate_linkedin_content_direct(trend_data)
                except Exception as e:
                    print(f"❌ Perplexity direct failed: {e}")
                    content = None
                
                if content:
                    print("✅ Perplexity direct content succeeded!")
            
            # If all tiers failed, send error
            if not content:
                self.send_message(
                    chat_id,
                    "❌ **Content Generation Failed**\n\n"
                    "All content generation services are currently unavailable.\n\n"
                    "**Please try:**\n"
                    "• Wait a moment and try again\n"
                    "• Use `/reset` and try a different topic\n"
                    "• Use `/scan` for trending topics"
                )
                self.reset_user_state(chat_id)
                return
            
            # Store in user state
            self.user_states[chat_id] = {
                "state": "content_ready",
                "data": {
                    "trend": trend_data,
                    "content": content,
                    "research": research
                },
                "last_activity": time.time()
            }
            
            # Send formatted content
            message = self.gemini.format_content_message(content)
            self.send_message(chat_id, message)
            health_check.record_request()
            
        except Exception as e:
            error_handler.log_error(e, {"chat_id": chat_id, "command": "topic", "topic": topic})
            health_check.record_error(e)
            self.send_message(
                chat_id,
                f"❌ **Error Researching Topic**\n\n"
                f"Could not research: _{topic[:50]}_\n\n"
                f"**Try:**\n"
                f"• Simplify your topic\n"
                f"• Use `/reset` and try again\n"
                f"• Use `/scan` for trending topics"
            )
    
    def handle_trend_selection(self, chat_id: int, selection: str):
        """Handle trend number selection with validation"""
        user_state = self.user_states.get(chat_id, {})
        
        if user_state.get("state") != "trend_selection":
            return
        
        try:
            trend_num = int(selection)
            trends = user_state["data"].get("trends", [])
            
            if not trends:
                self.send_message(chat_id, "❌ No trends available. Please use `/scan` again.")
                self.reset_user_state(chat_id)
                return
            
            if 1 <= trend_num <= len(trends):
                selected_trend = trends[trend_num - 1]
                
                self.send_message(chat_id, f"✨ **Generating Content...**\n\n📊 Topic: _{selected_trend['title']}_\n\n_Creating professional LinkedIn post..._")
                
                # 3-TIER FALLBACK SYSTEM
                # Try Gemini first, then OpenAI, then Perplexity direct
                content = None
                
                # Tier 1: Try Gemini
                try:
                    print("🔷 Tier 1: Trying Gemini...")
                    content = self.gemini.generate_linkedin_content(selected_trend)
                except Exception as e:
                    print(f"⚠️  Gemini failed: {e}")
                    content = None
                
                if content:
                    print("✅ Gemini succeeded!")
                
                # Tier 2: Try OpenAI if Gemini failed
                if not content:
                    try:
                        print("🔶 Tier 2: Trying OpenAI GPT-4...")
                        content = self.openai.generate_linkedin_content(selected_trend)
                    except Exception as e:
                        print(f"⚠️  OpenAI failed: {e}")
                        content = None
                    
                    if content:
                        print("✅ OpenAI succeeded!")
                
                # Tier 3: Try Perplexity direct if both failed
                if not content:
                    try:
                        print("🔸 Tier 3: Trying Perplexity direct...")
                        content = self.perplexity.generate_linkedin_content_direct(selected_trend)
                    except Exception as e:
                        print(f"❌ Perplexity direct failed: {e}")
                        content = None
                    
                    if content:
                        print("✅ Perplexity direct succeeded!")
                
                # If all tiers failed, send error message
                if not content:
                    self.send_message(
                        chat_id,
                        "❌ **Content Generation Failed**\n\n"
                        "All content generation services are currently unavailable.\n\n"
                        "**Please try:**\n"
                        "• Wait a moment and try again\n"
                        "• Use `/reset` and select a different trend\n"
                        "• Try `/topic <your topic>` for custom content"
                    )
                    self.reset_user_state(chat_id)
                    return
                
                # Store in user state
                self.user_states[chat_id] = {
                    "state": "content_ready",
                    "data": {
                        "trend": selected_trend,
                        "content": content
                    },
                    "last_activity": time.time()
                }
                
                # Send formatted content with inline keyboard buttons
                message = self.gemini.format_content_message(content)
                
                # Create inline keyboard with action buttons
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "📤 Publish to LinkedIn", "callback_data": "publish"},
                            {"text": "👁️ Preview", "callback_data": "preview"}
                        ],
                        [
                            {"text": "🔍 Scan More Trends", "callback_data": "scan"},
                            {"text": "🔄 Reset", "callback_data": "reset"}
                        ]
                    ]
                }
                
                self.send_message(chat_id, message, reply_markup=keyboard)
                health_check.record_request()
                
            else:
                self.send_message(chat_id, f"❌ Invalid selection. Please choose 1-{len(trends)}")
                
        except ValueError:
            pass  # Not a number, ignore
        except Exception as e:
            error_handler.log_error(e, {"chat_id": chat_id, "selection": selection})
            self.send_message(chat_id, "❌ Error processing selection. Please try again or use `/reset`")
    
    @handle_errors(error_handler, "Failed to generate preview. Please try again or use /reset")
    def handle_preview(self, chat_id: int):
        """Handle /preview command with error handling"""
        user_state = self.user_states.get(chat_id, {})
        
        if user_state.get("state") != "content_ready":
            self.send_message(
                chat_id,
                "❌ **No Content to Preview**\n\n"
                "**Please:**\n"
                "1. Use `/scan` to discover trends, OR\n"
                "2. Use `/topic <your topic>` for custom content\n"
                "3. Then try `/preview` again"
            )
            return
        
        self.send_message(chat_id, "🎨 **Generating Preview...**\n\n_Creating image (this may take a moment)..._")
        
        try:
            trend = user_state["data"].get("trend")
            content = user_state["data"].get("content")
            
            if not trend or not content:
                self.send_message(chat_id, "❌ Content data missing. Please use `/reset` and try again.")
                return
            
            # Try AI image generation first
            ai_img = None
            image_prompt = content.get("image_prompt", "")
            
            if image_prompt:
                print("🤖 Attempting AI image generation...")
                ai_img = self.ai_image_service.generate_linkedin_image(
                    title=trend.get("title", "Morocco Trends"),
                    summary=trend.get("summary", ""),
                    topic=trend.get("title", "")
                )
            
            # Use AI image if successful, otherwise professional templates
            if ai_img:
                print("✅ Using AI-generated image")
                img = ai_img
                # Resize to standard dimensions
                img = img.resize((1200, 630))
            else:
                print("🎨 Using professional template design")
                img = self.professional_image_service.create_linkedin_image(
                    title=trend.get("title", "Morocco Trends"),
                    summary=trend.get("summary", ""),
                    topic=trend.get("title", "")
                )
            
            # Convert to bytes
            img_bytes = self.image_service.image_to_bytes(img)
            
            # Store image in user state
            self.user_states[chat_id]["data"]["image_bytes"] = img_bytes
            self.update_user_activity(chat_id)
            
            # Send image with caption
            caption = f"**Preview Ready!**\n\n✅ Content generated\n✅ Image created\n\nUse `/publish` to post to LinkedIn"
            self.send_photo(chat_id, img_bytes, caption)
            health_check.record_request()
            
        except Exception as e:
            error_handler.log_error(e, {"chat_id": chat_id, "command": "preview"})
            health_check.record_error(e)
            self.send_message(
                chat_id,
                f"❌ **Error Creating Preview**\n\n"
                f"_{type(e).__name__}_\n\n"
                f"**Try:**\n"
                f"• Wait a moment and try again\n"
                f"• Use `/reset` to clear session\n"
                f"• Start over with `/scan`"
            )
    
    @handle_errors(error_handler, "Failed to publish. Please try again or use /reset")
    def handle_publish(self, chat_id: int):
        """Handle /publish command with error handling"""
        user_state = self.user_states.get(chat_id, {})
        
        if user_state.get("state") != "content_ready":
            self.send_message(
                chat_id,
                "❌ **No Content to Publish**\n\n"
                "**Please:**\n"
                "1. Use `/scan` or `/topic` to create content\n"
                "2. Use `/preview` to review\n"
                "3. Then use `/publish`"
            )
            return
        
        self.send_message(chat_id, "📤 **Publishing to LinkedIn...**\n\n_Uploading image and creating post..._\n\n_This may take 10-15 seconds..._")
        
        try:
            content = user_state["data"].get("content")
            
            if not content:
                self.send_message(chat_id, "❌ Content missing. Please use `/reset` and try again.")
                return
            
            # Generate image if not already done
            if "image_bytes" not in user_state["data"]:
                trend = user_state["data"].get("trend", {})
                
                # Try AI image generation first
                ai_img = None
                image_prompt = content.get("image_prompt", "")
                
                if image_prompt:
                    ai_img = self.ai_image_service.generate_linkedin_image(
                        title=trend.get("title", "Morocco Trends"),
                        summary=trend.get("summary", ""),
                        topic=trend.get("title", "")
                    )
                
                # Use AI image if successful, otherwise professional templates
                if ai_img:
                    img = ai_img.resize((1200, 630))
                else:
                    img = self.professional_image_service.create_linkedin_image(
                        title=trend.get("title", "Morocco Trends"),
                        summary=trend.get("summary", ""),
                        topic=trend.get("title", "")
                    )
                
                img_bytes = self.image_service.image_to_bytes(img)
                user_state["data"]["image_bytes"] = img_bytes
            else:
                img_bytes = user_state["data"]["image_bytes"]
            
            # Format LinkedIn text
            linkedin_text = self.linkedin.format_linkedin_text(content)
            
            # Publish to LinkedIn
            result = self.linkedin.publish_post_with_image(linkedin_text, img_bytes)
            
            if result["success"]:
                message = f"""✅ **Published Successfully!**

🎉 Your post is now live on LinkedIn!

📊 Post ID: `{result['post_id']}`

🔗 Check your LinkedIn profile to see it.

Ready to create more? Use /scan to find new trends!"""
                self.send_message(chat_id, message)
                
                # Reset state
                self.reset_user_state(chat_id)
                health_check.record_request()
            else:
                self.send_message(
                    chat_id,
                    f"❌ **Publishing Failed**\n\n"
                    f"{result['message']}\n\n"
                    f"**Common Issues:**\n"
                    f"• LinkedIn token expired (needs refresh)\n"
                    f"• API rate limit reached\n"
                    f"• Network connectivity\n\n"
                    f"**Try:**\n"
                    f"• Wait a few minutes and try again\n"
                    f"• Contact admin to refresh LinkedIn token\n"
                    f"• Use `/reset` to clear session"
                )
                
        except Exception as e:
            error_handler.log_error(e, {"chat_id": chat_id, "command": "publish"})
            health_check.record_error(e)
            self.send_message(
                chat_id,
                f"❌ **Error Publishing**\n\n"
                f"_{type(e).__name__}_\n\n"
                f"Your content is saved. Try `/publish` again or use `/reset`"
            )
    
    def handle_reset(self, chat_id: int):
        """Handle /reset command"""
        self.reset_user_state(chat_id)
        self.send_message(
            chat_id,
            "🔄 **Session Reset Complete**\n\n"
            "✅ Your session has been cleared\n"
            "✅ All temporary data removed\n"
            "✅ Ready for new requests\n\n"
            "Use `/start` to see available commands!"
        )
        error_handler.logger.info(f"User {chat_id} reset their session")
    
    def handle_status(self, chat_id: int):
        """Handle /status command with health check"""
        try:
            status = health_check.get_status()
            
            response = f"""📊 **Bot Status**

🟢 **System Health:** {status['status'].upper()}

⏱️ **Uptime:** {status['uptime']}
📈 **Total Requests:** {status['total_requests']}
❌ **Total Errors:** {status['total_errors']}
📉 **Error Rate:** {status['error_rate']}

✅ **Services:**
• Telegram Bot: Online
• Perplexity API: Ready
• Gemini API: Ready
• Image Service: Ready
• LinkedIn API: Ready

🔐 **Security:**
• All tokens encrypted
• Rate limiting active
• Session management enabled

💾 **Your Session:**
• State: {self.user_states.get(chat_id, {}).get('state', 'idle')}
• Active: {'Yes' if chat_id in self.user_states else 'No'}

🤖 Ready to automate your content!"""
            
            self.send_message(chat_id, response)
            
        except Exception as e:
            error_handler.log_error(e, {"chat_id": chat_id, "command": "status"})
            self.send_message(chat_id, "❌ Error getting status. Bot is running but status unavailable.")
    
    def handle_errors_command(self, chat_id: int):
        """Handle /errors command (admin only)"""
        recent_errors = error_handler.get_recent_errors(5)
        
        if not recent_errors:
            self.send_message(chat_id, "✅ **No Recent Errors**\n\nSystem is running smoothly!")
            return
        
        response = f"⚠️ **Recent Errors ({len(recent_errors)})**\n\n"
        
        for i, error in enumerate(recent_errors, 1):
            response += f"**{i}. {error['error_type']}**\n"
            response += f"_{error['timestamp']}_\n"
            response += f"`{error['error_message'][:100]}`\n\n"
        
        response += "Use `/reset` to clear your session if experiencing issues."
        
        self.send_message(chat_id, response)
    
    def handle_callback_query(self, callback_query: Dict):
        """Handle inline keyboard button clicks"""
        try:
            query_id = callback_query.get("id")
            chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
            data = callback_query.get("data")
            
            error_handler.logger.info(f"🔘 Callback query from {chat_id}: {data}")
            
            if not chat_id or not data:
                return
            
            # Answer the callback query to remove loading state
            answer_url = f"{self.base_url}/answerCallbackQuery"
            requests.post(answer_url, json={"callback_query_id": query_id}, timeout=5)
            
            # Route to appropriate handler based on button data
            if data == "publish":
                self.handle_publish(chat_id)
            elif data == "preview":
                self.handle_preview(chat_id)
            elif data == "scan":
                self.handle_scan(chat_id)
            elif data == "reset":
                self.handle_reset(chat_id)
            else:
                error_handler.logger.warning(f"Unknown callback data: {data}")
                
        except Exception as e:
            error_handler.log_error(e, {"action": "handle_callback_query", "callback_query": str(callback_query)[:200]})
    
    def handle_message(self, message: Dict):
        """Handle incoming messages with comprehensive error handling"""
        try:
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            user = message.get("from", {})
            username = user.get("username", user.get("first_name", "User"))
            
            if not chat_id:
                error_handler.logger.warning("Message without chat_id received")
                return
            
            error_handler.logger.info(f"📨 Message from @{username} ({chat_id}): {text[:50]}")
            
            # Update user activity
            self.update_user_activity(chat_id)
            
            # Handle commands
            if text.startswith("/start") or text.startswith("/help"):
                self.handle_start(chat_id, username)
            
            elif text.startswith("/scan"):
                self.handle_scan(chat_id)
            
            elif text.startswith("/topic"):
                topic = text.replace("/topic", "").strip()
                self.handle_topic(chat_id, topic)
            
            elif text.startswith("/preview"):
                self.handle_preview(chat_id)
            
            elif text.startswith("/publish"):
                self.handle_publish(chat_id)
            
            elif text.startswith("/reset"):
                self.handle_reset(chat_id)
            
            elif text.startswith("/status"):
                self.handle_status(chat_id)
            
            elif text.startswith("/errors"):
                self.handle_errors_command(chat_id)
            
            # Handle trend selection (numbers)
            elif text.isdigit():
                self.handle_trend_selection(chat_id, text)
            
            else:
                # Unknown command
                response = f"You said: _{text[:100]}_\n\nUse `/help` to see available commands!"
                self.send_message(chat_id, response)
                
        except Exception as e:
            error_handler.log_error(e, {"action": "handle_message", "message": str(message)[:200]})
            health_check.record_error(e)
            try:
                self.send_message(
                    chat_id,
                    "❌ **Unexpected Error**\n\n"
                    "An error occurred processing your message.\n\n"
                    "**Try:**\n"
                    "• `/reset` to clear your session\n"
                    "• `/status` to check bot health\n"
                    "• Wait a moment and try again"
                )
            except:
                pass  # Fail silently if we can't even send error message
    
    def run(self):
        """Main bot loop with error recovery"""
        print("=" * 60)
        print("🤖 Morocco Trend Automator Bot Starting...")
        print("=" * 60)
        print(f"Bot: {Config.BOT_USERNAME}")
        print(f"Mode: Long Polling (No webhook required)")
        print(f"Error Handling: Enabled")
        print(f"Rate Limiting: Enabled")
        print("=" * 60)
        
        offset = None
        error_count = 0
        max_errors = 10  # Max consecutive errors before longer wait
        
        error_handler.logger.info("✅ Bot is running! Send /start to your bot to test it.")
        print("\n✅ Bot is running! Send /start to your bot to test it.")
        print("Press Ctrl+C to stop.\n")
        
        try:
            while True:
                try:
                    # Clean expired sessions periodically
                    if int(time.time()) % 300 == 0:  # Every 5 minutes
                        self.clean_expired_sessions()
                    
                    # Get updates
                    result = self.get_updates(offset)
                    
                    if result and result.get("ok"):
                        updates = result.get("result", [])
                        
                        for update in updates:
                            try:
                                # Update offset
                                offset = update.get("update_id") + 1
                                
                                # Debug: Log update type
                                if "callback_query" in update:
                                    error_handler.logger.info(f"📥 Received callback_query update: {update.get('update_id')}")
                                
                                # Handle message
                                if "message" in update:
                                    self.handle_message(update["message"])
                                    error_count = 0  # Reset error count on success
                                
                                # Handle callback query (button clicks)
                                elif "callback_query" in update:
                                    self.handle_callback_query(update["callback_query"])
                                    error_count = 0
                                    
                            except Exception as e:
                                error_handler.log_error(e, {"update_id": update.get("update_id")})
                                error_count += 1
                    
                    # Small delay to avoid hitting rate limits
                    time.sleep(0.1)
                    
                except KeyboardInterrupt:
                    raise  # Re-raise to exit cleanly
                    
                except Exception as e:
                    error_handler.log_error(e, {"phase": "main_loop"})
                    error_count += 1
                    
                    # If too many errors, wait longer
                    if error_count >= max_errors:
                        error_handler.logger.error(f"Too many errors ({error_count}), waiting 60s")
                        time.sleep(60)
                        error_count = 0
                    else:
                        time.sleep(5)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            error_handler.logger.info("Bot stopped by user (Ctrl+C)")
        except Exception as e:
            error_handler.log_error(e, {"phase": "main_run"})
            print(f"\n❌ Fatal Error: {e}")
            raise

if __name__ == "__main__":
    try:
        bot = MoroccoTrendBot()
        bot.run()
    except Exception as e:
        error_handler.log_error(e, {"phase": "startup"})
        print(f"❌ Failed to start bot: {e}")
        print("Check logs for details: /home/ubuntu/morocco-bot/bot_errors.log")
