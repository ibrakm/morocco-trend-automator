# Morocco Trend Automator - Telegram Bot

A professional Telegram bot that discovers trending topics, generates LinkedIn content with AI, and publishes directly to LinkedIn.

## Features

- 🔍 Discovers trending topics (global + Morocco-specific)
- 🤖 Generates professional LinkedIn content using AI
- 🎨 Creates beautiful images with 5 templates and 8 color schemes
- 📤 Publishes directly to LinkedIn
- 🔄 3-tier fallback system: Gemini → OpenAI → Perplexity

## Deployment to Railway.app

### Prerequisites
- Railway.app account
- GitHub account

### Environment Variables Required

Set these in Railway.app dashboard:

```
OPENAI_API_KEY=your_openai_api_key_here
```

All other API keys (Gemini, Perplexity, LinkedIn) are encrypted in the config.py file.

### Deployment Steps

1. Push this code to GitHub
2. Connect your GitHub repository to Railway.app
3. Add the OPENAI_API_KEY environment variable
4. Deploy!

The bot will start automatically and run 24/7.

## Bot Commands

- `/start` - Start the bot and see available commands
- `/scan` - Scan for trending topics
- `/topic <your topic>` - Generate content for a custom topic
- `/preview` - Preview generated content
- `/publish` - Publish to LinkedIn
- `/reset` - Reset session

## Bot Details

- **Bot Username**: @Newlinkedinv1bot
- **Bot Token**: Encrypted in config.py

## Support

For issues or questions, contact the bot owner.
