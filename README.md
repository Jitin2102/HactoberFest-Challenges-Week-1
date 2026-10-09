# 🌿 EcoQuest AI
### Touch less screen. Explore more Earth.

EcoQuest AI is a screen-light outdoor exploration companion. It turns everyday walks into small nature missions, encourages mindful observation, and lets users record what they discover.

## What works in this MVP

- Six ready-to-use outdoor missions with practical safety guidance
- Mission completion, points, and progress tracking
- Field journal for reflections and observations
- Optional local Gemma-powered mission generation and nature Q&A through Ollama
- Photo preview in the Nature Guide (image-based species identification is not implemented yet)
- Clean, responsive Streamlit interface

## Why open AI?

Gemma can run through a local Ollama runtime, so prompts and responses for its features can remain on the user's machine rather than being sent to a closed hosted LLM API. The ready-made mission library works without a model. Local inference requires compatible hardware, a downloaded model, and Ollama running; this is not a fully offline mobile app yet.

Open-weight models also make it possible to swap models, inspect behavior, and experiment with local inference. Model licenses and usage terms should be checked before redistribution or deployment.

## Stack

- Python + Streamlit
- Gemma via Ollama (optional local model)
- Streamlit session state for prototype progress

## Run locally

### 1. Create an environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the app

```bash
streamlit run app.py
```

### 3. Enable local Gemma (optional)

Install Ollama from its official website, then run:

```bash
ollama pull gemma3:1b
ollama serve
```

In another terminal, start EcoQuest with `streamlit run app.py`. Set `GEMMA_MODEL` in your environment or `.env` if you want to use a different compatible local model.

## Project structure

```text
EcoQuest_AI/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Roadmap

- [ ] Add robust image-based plant identification with a dedicated vision model
- [ ] Add voice input and speech output
- [ ] Add downloadable offline mission packs
- [ ] Add persistent storage and optional accounts
- [ ] Add weather-aware recommendations with clear permission controls
- [ ] Test outdoors and document real user feedback

## Safety and limitations

- AI responses are educational suggestions, not authoritative species identification.
- Never eat wild plants or handle unknown organisms based on an AI response.
- Stay on public paths, respect wildlife, and avoid traffic or unsafe areas.
- This MVP does not currently use live weather, maps, or GPS.
- User progress is session-only and may reset when the session ends.

## Challenge submission

Built for the Hacktoberfest Open-Source AI Challenge — Week 1: Touch Grass.

**Tagline:** Touch less screen. Explore more Earth.
