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

## Cost

Using GPT-4o-mini:
- ~$0.15 per 1M input tokens
- ~$0.60 per 1M output tokens
- **Approximately $0.0002 per job extraction**

## Deployment

This app can be deployed on:
- [Render](https://render.com) - Free tier available
- [Railway](https://railway.app)
- Any platform supporting Python/Flask

For production, use gunicorn:

```bash
gunicorn app:app --bind 0.0.0.0:8050
```

## License

MIT

## Author

[Wes Porter](https://geoalchemist.com)
