# AI Location Extraction Demo

A demonstration of using GPT-4o-mini to extract structured location data from job posting text.

This project showcases how LLMs can replace manual data extraction tasks at a fraction of the cost (~$0.0002 per extraction).

![Demo](https://res.cloudinary.com/wessport/image/upload/v1768771124/ai-pipeline.png)

## Features

- Extract primary work location from unstructured job posting text
- Classify location granularity (street address → city → state → country)
- Interactive web demo with animated processing visualization
- Dark/light theme support

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/wessport/ai-loc-extraction-demo.git
cd ai-loc-extraction-demo
```

### 2. Set up environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API key

Copy the example environment file and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env` and add your key:

```
OPENAI_API_KEY=sk-your-key-here
```

### 4. Run the demo

```bash
python app.py
```

Open http://localhost:8050 in your browser.

## Project Structure

```
ai-loc-extraction-demo/
├── app.py                 # Flask web server
├── static/
│   ├── index.html         # Main UI
│   ├── style.css          # Dark/light theme styles
│   └── app.js             # Frontend logic & animations
├── utils/
│   └── llm_extractor.py   # OpenAI API wrapper
├── render.yaml            # Render deployment config
├── requirements.txt
├── .env.example
└── README.md
```

## How It Works

1. **Input**: Paste job posting text into the web interface
2. **Processing**: The text is sent to GPT-4o-mini with a structured extraction prompt
3. **Output**: Returns the most specific location found, along with:
   - Location granularity level
   - Confidence score
   - AI explanation of the extraction

---

## OpenAI API Setup

This demo uses the OpenAI API with GPT-4o-mini.

### Getting an API Key

1. Create an account at [platform.openai.com](https://platform.openai.com)
2. Navigate to [API Keys](https://platform.openai.com/api-keys)
3. Click "Create new secret key"
4. Select **Service account** type (recommended for apps)
5. Copy the key — you won't see it again

### Pricing

OpenAI API is pay-as-you-go. You'll need to add a payment method and purchase credits (minimum $5).

The good news: this demo is extremely cheap to run. **$5 covers ~25,000 extractions**.

### Cost Breakdown

| Component | Cost |
|-----------|------|
| Input tokens | $0.15 per 1M tokens |
| Output tokens | $0.60 per 1M tokens |
| **Per extraction** | **~$0.0002** |

### Setting Spending Limits

To prevent unexpected charges, set a monthly budget limit at [platform.openai.com/settings/organization/limits](https://platform.openai.com/settings/organization/limits).

For example, set a $5/month cap — the API will reject requests once you hit that limit.

---

## Deploying to Render (Free)

This repo includes a `render.yaml` for one-click deployment.

### Option 1: Blueprint Deploy

1. Go to [render.com](https://render.com) and sign in
2. Click **New** → **Blueprint**
3. Connect your GitHub account and select this repo
4. Render will auto-detect `render.yaml` and configure everything
5. Add your `OPENAI_API_KEY` in the environment variables
6. Click **Apply**

### Option 2: Manual Setup

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect your GitHub repo
3. Configure:

| Setting | Value |
|---------|-------|
| **Runtime** | Python |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| **Health Check Path** | `/api/health` |
| **Instance Type** | Free |

4. Add environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key

5. Click **Deploy**

### Free Tier Limitations

Render's free tier:
- Spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- 750 hours/month across all free services

---

## Alternative Deployment Options

### Railway

```bash
railway login
railway init
railway add --name OPENAI_API_KEY
railway up
```

### Local Production

```bash
gunicorn app:app --bind 0.0.0.0:8050
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8050"]
```

---

## License

MIT

## Author

[Wes Porter](https://geoalchemist.com)
