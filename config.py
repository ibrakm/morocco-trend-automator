#!/usr/bin/env python3
"""
Configuration for Morocco Trend Automator Bot
Uses environment variables for API keys
"""

import os

# Configuration class
class Config:
    """Configuration with environment variables"""
    
    @staticmethod
    def get_telegram_token():
        return os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    @staticmethod
    def get_perplexity_token():
        return os.getenv('PERPLEXITY_API_KEY', '')
    
    @staticmethod
    def get_gemini_token():
        return os.getenv('GEMINI_API_KEY', '')
    
    @staticmethod
    def get_linkedin_token():
        return os.getenv('LINKEDIN_ACCESS_TOKEN', '')
    
    @staticmethod
    def get_linkedin_urn():
        return os.getenv('LINKEDIN_URN', '')
    
    # API Endpoints
    PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
    PERPLEXITY_MODEL = "llama-3.1-sonar-small-128k-online"
    
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    GEMINI_TEXT_MODEL = "gemini-2.0-flash-exp"
    GEMINI_IMAGE_MODEL = "imagen-3.0-generate-001"
    
    LINKEDIN_API_URL = "https://api.linkedin.com/v2"
    
    # Bot Settings
    BOT_USERNAME = "@becool11"
    POLLING_TIMEOUT = 30
    
    # Image Settings
    IMAGE_WIDTH = 1200
    IMAGE_HEIGHT = 630
    LOGO_SIZE = (150, 150)
