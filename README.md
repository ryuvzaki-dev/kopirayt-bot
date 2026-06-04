# 🤖 Kopirayt Bot — O'rnatish Qo'llanmasi

## Kerakli narsalar
1. Telegram Bot Token (@BotFather dan)
2. Anthropic API Key (claude.ai/api)
3. Railway.app akkaunt (bepul)

## Railway.app ga joylash (bepul hosting)

### 1-qadam: GitHub ga yuklash
- github.com ga kiring
- "New repository" → nom bering → "Create"
- Barcha fayllarni yuklang

### 2-qadam: Railway ga ulash
- railway.app ga kiring (GitHub bilan login)
- "New Project" → "Deploy from GitHub"
- Repositoriyangizni tanlang

### 3-qadam: Environment Variables
Railway dashboard → Variables bo'limiga qo'shing:

```
BOT_TOKEN = 8492694051:AAEG_t1uMtam...  (sizning tokeningiz)
ANTHROPIC_API_KEY = sk-ant-...           (Anthropic kaliti)
ALLOWED_USER_ID = 123456789             (sizning Telegram ID)
```

### Telegram ID ni qanday bilish?
@userinfobot ga yozing → u sizning ID ingizni beradi

### Anthropic API Key qayerdan?
console.anthropic.com → API Keys → Create Key

## Bot buyruqlari
- ✍️ Kopirayt yozish — yangi kopirayt yaratish
- ➕ Andoza qo'shish — namuna saqlash
- 📋 Andozalarni ko'rish — barcha namunalar
- 🗑 Andoza o'chirish — bitta o'chirish
- 🧹 Hammasini tozalash — barchasini o'chirish
