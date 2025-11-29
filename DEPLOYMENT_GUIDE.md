# Morocco Trend Automator - Deployment Guide

## 🎉 Bot Status: FIXED AND TESTED

The bot has been successfully fixed and tested. The 3-tier fallback system is now working correctly:
- ✅ Generates content relevant to user's topic (not generic Morocco business)
- ✅ Proper tier fallback: Gemini → OpenAI → Perplexity
- ✅ Successfully published to LinkedIn
- ✅ All bugs fixed

---

## 📦 What's Included

This package contains:
- `morocco_bot.py` - Main bot file (FIXED)
- `gemini_service.py` - Gemini AI service (FIXED exception handling)
- `openai_service.py` - OpenAI service
- `perplexity_service.py` - Perplexity service (FIXED exception handling)
- `linkedin_service.py` - LinkedIn integration
- `image_service.py` - Image generation
- `professional_image_service.py` - Professional image templates
- `error_handler.py` - Error handling
- `config.py` - Configuration (encrypted API keys)
- `.encryption_key` - Encryption key for API keys
- `requirements.txt` - Python dependencies
- `Procfile` - For Railway/Render deployment
- `runtime.txt` - Python version specification

---

## 🚀 Deployment Options (100% Free)

### Option 1: Railway.app (Recommended)
**Free Tier:** 500 hours/month (enough for 24/7 with sleep mode)

1. Create account at https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub account
4. Create a new repository and push this code
5. Select the repository in Railway
6. Add environment variable: `OPENAI_API_KEY=your_key_here`
7. Deploy!

### Option 2: Render.com
**Free Tier:** 750 hours/month

1. Create account at https://render.com
2. Click "New" → "Background Worker"
3. Connect GitHub repository
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python3 morocco_bot.py`
6. Add environment variable: `OPENAI_API_KEY=your_key_here`
7. Deploy!

### Option 3: Fly.io
**Free Tier:** 3 shared-cpu-1x VMs

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Run: `fly auth signup`
3. Run: `fly launch`
4. Follow prompts
5. Run: `fly secrets set OPENAI_API_KEY=your_key_here`
6. Run: `fly deploy`

### Option 4: PythonAnywhere
**Free Tier:** 1 always-on web app

1. Create account at https://www.pythonanywhere.com
2. Upload files via Files tab
3. Open Bash console
4. Run: `pip3 install --user -r requirements.txt`
5. Create a scheduled task to run `python3 morocco_bot.py`
6. Set to run every hour (keeps bot alive)

### Option 5: Heroku (Requires Credit Card for Verification)
**Free Tier:** 550-1000 dyno hours/month

1. Create account at https://heroku.com
2. Install Heroku CLI
3. Run: `heroku login`
4. Run: `heroku create morocco-trend-bot`
5. Run: `heroku config:set OPENAI_API_KEY=your_key_here`
6. Run: `git push heroku master`

---

## 🔑 Environment Variables

Only ONE environment variable is required:

```
OPENAI_API_KEY=your_openai_api_key_here
```

All other API keys (Gemini, Perplexity, LinkedIn, Telegram Bot Token) are already encrypted in `config.py`.

---

## 📝 How to Get API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)
4. Add $5-10 credit to your account

### If You Need to Update Other Keys

The following keys are already configured and encrypted:
- **Telegram Bot Token**: Already set for @Newlinkedinv1bot
- **Gemini API Key**: Already configured
- **Perplexity API Key**: Already configured  
- **LinkedIn Credentials**: Already configured

If you need to change any of these, you'll need to:
1. Update `config.py`
2. Re-encrypt using the `.encryption_key` file

---

## 🧪 Testing the Bot

After deployment:

1. Open Telegram and search for **@Newlinkedinv1bot**
2. Send `/start`
3. Send `/topic artificial intelligence in Morocco`
4. Wait for content generation
5. Send `/publish` to post to LinkedIn

Expected behavior:
- Bot generates relevant content about your topic
- Falls back through tiers if one fails (Gemini → OpenAI → Perplexity)
- Successfully publishes to LinkedIn

---

## 🐛 Troubleshooting

### Bot not responding
- Check if the deployment is running (check logs)
- Verify `OPENAI_API_KEY` environment variable is set
- Check if you have OpenAI API credits

### "Error Researching Topic"
- This means all 3 tiers failed
- Check your OpenAI API key and credits
- Gemini may be out of quota (this is normal, it falls back to OpenAI)

### LinkedIn publishing fails
- LinkedIn credentials may need to be refreshed
- Check error logs for details

### Bot generates generic Morocco content
- This bug has been FIXED in this version
- If you still see this, you may be running old code

---

## 📊 Monitoring

### Check Logs

**Railway:**
```
railway logs
```

**Render:**
Go to Dashboard → Your Service → Logs

**Fly.io:**
```
fly logs
```

**Heroku:**
```
heroku logs --tail
```

---

## 💰 Cost Estimates

### Free Tier Limits
- **Railway**: 500 hours/month free (bot sleeps when inactive)
- **Render**: 750 hours/month free
- **Fly.io**: 3 VMs free
- **PythonAnywhere**: 1 always-on app free

### API Costs (Pay-as-you-go)
- **OpenAI GPT-4**: ~$0.01-0.03 per request
- **Gemini**: Free tier available (15 requests/minute)
- **Perplexity**: Free tier available

**Estimated monthly cost**: $5-15 depending on usage

---

## 🔒 Security Notes

1. **Never commit `.encryption_key` to public repositories**
2. **Use environment variables** for sensitive data
3. **Rotate API keys** regularly
4. **Monitor usage** to detect unauthorized access

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review deployment logs
3. Verify all environment variables are set correctly

---

## ✅ Deployment Checklist

Before deploying:
- [ ] Choose a hosting platform
- [ ] Create account on chosen platform
- [ ] Get OpenAI API key
- [ ] Add credits to OpenAI account ($5-10 minimum)
- [ ] Upload/push code to platform
- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Start the deployment
- [ ] Test with `/start` command
- [ ] Test with `/topic` command
- [ ] Verify LinkedIn publishing works

---

## 🎯 Next Steps

1. Choose your preferred hosting platform from the options above
2. Follow the deployment steps for that platform
3. Set the `OPENAI_API_KEY` environment variable
4. Test the bot thoroughly
5. Monitor logs for any issues

**The bot is ready to deploy and will run 24/7 once hosted!**
