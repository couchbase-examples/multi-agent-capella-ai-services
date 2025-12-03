# 🎬 Seinfeld Script Generator

A multi-agent AI system that generates authentic Seinfeld episode scripts using CrewAI and [Couchbase Capella AI Services](https://docs.couchbase.com/ai/get-started/intro.html).

## Overview

This project uses 5 specialized AI agents working together to create Seinfeld scripts that capture the show's unique comedic style:

| Agent | Role | Description |
|-------|------|-------------|
| 🎯 **Theme Analyzer** | Comedy Consultant | Breaks down themes into Seinfeld-worthy comedic elements |
| 📝 **Plot Architect** | Episode Designer | Creates A/B/C plot threads that converge hilariously |
| 🎭 **Character Voice Specialist** | Voice Expert | Ensures characters sound authentic |
| ✍️ **Dialogue Writer** | Scene Writer | Crafts sharp, witty dialogue with perfect timing |
| ✅ **Quality Reviewer** | Editor | Polishes scripts for maximum "Seinfeldness" |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Input                              │
│                    "Theme for episode"                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestrator (CrewAI)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│    Couchbase  │    │   Capella AI  │    │   Agents      │
│   (Scripts +  │◄──►│ (Embeddings   │◄──►│ (5 Specialists│
│   Embeddings) │    │  + LLM)       │    │   with RAG)   │
└───────────────┘    └───────────────┘    └───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Generated Seinfeld Script                    │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **RAG-Enhanced Generation**: Uses actual Seinfeld scripts stored in Couchbase for reference
- **Vector Search**: Semantic search finds similar dialogues and scenes
- **Multi-Agent Collaboration**: Each agent specializes in a different aspect of scriptwriting
- **Character Authenticity**: Agents reference actual character dialogue patterns
- **Plot Structure**: Creates classic Seinfeld A/B/C plot threads that converge

## Prerequisites

- Python 3.10+
- Couchbase Capella cluster running Couchbase 8.0
- Couchbase Capella AI Services including hosting an Embedding and a Large Language Model

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd multi-agent-capella-ai-services
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   # Capella AI Services
   CAPELLA_AI_ENDPOINT="https://xxxx.ai.cloud.couchbase.com/v1"
   
   # LLM Configuration
   LLM_API_KEY="cbsk-v1-xxx"
   LLM_MODEL_NAME="mistralai/mistral-7b-instruct-v0.3"
   
   # Embedding Configuration
   EMBEDDING_API_KEY="cbsk-v1-xxx"
   EMBEDDING_MODEL_NAME="nvidia/llama-3.2-nv-embedqa-1b-v2"
   
   # Couchbase Connection
   CB_CONNECTION_STRING=couchbases://cb.xxx.cloud.couchbase.com
   CB_USERNAME=Administrator
   CB_PASSWORD=Password
   CB_BUCKET=seinfeld
   CB_SCOPE=episodes
   CB_COLLECTION=scripts
   ```

## Usage

### Using the CLI Command

After installation, use the `seinfeld` command:

```bash
# Generate a script with a theme
seinfeld "Jerry gets a smart speaker that mishears everything"

# Interactive mode (prompts for theme)
seinfeld --interactive

# Specify output file
seinfeld "Your theme" -o my_script.md

# Verbose mode
seinfeld "Your theme" -v
```

### Using Python Module

```bash
# Run as a Python module
python -m seinfeld_script_generator.main "Jerry gets a smart speaker"

# Interactive mode
python -m seinfeld_script_generator.main --interactive
```

### Using Python API

```python
from seinfeld_script_generator.crew import run_crew

# Generate a script
theme = "George discovers he's been pronouncing his own name wrong his entire life"
script = run_crew(theme)
print(script)
```

### Example Themes

Here are some theme ideas to try:

- "Jerry's new girlfriend only communicates through voice memos"
- "George pretends to be a marine biologist on a dating app"
- "Elaine's boss makes everyone use a productivity app that tracks bathroom breaks"
- "Kramer starts a business selling 'authentic New York air' to tourists"
- "The gang gets stuck in an escape room and can't agree on anything"

## Project Structure

```
multi-agent-capella-ai-services/
├── pyproject.toml              # Project configuration & dependencies
├── README.md                   # This file
├── TUTORIAL.md                 # Comprehensive tutorial
├── .env                        # Environment variables (create this)
├── src/
│   └── seinfeld_script_generator/
│       ├── __init__.py
│       ├── main.py             # CLI entry point
│       ├── crew.py             # CrewAI orchestration
│       ├── config/
│       │   ├── agents.yaml     # Agent definitions
│       │   └── tasks.yaml      # Task definitions
│       └── tools/
│           ├── __init__.py
│           └── couchbase_rag.py  # Couchbase RAG tool
└── output/                     # Generated scripts
```

## Couchbase Setup

To use RAG with actual Seinfeld scripts:

1. **Create a bucket** (e.g., `seinfeld`) in your Couchbase Capella cluster

2. **Create a scope and collection** for the scripts (e.g., `episodes.scripts`)

3. **Load Seinfeld scripts** from this [public dataset](https://www.kaggle.com/datasets/thec03u5/seinfeld-chronicles) with this document structure:
   ```json
   {
      "Character": "JERRY",
      "Dialogue": "What's the deal with airline peanuts?",
      "Season": 3,
      "EpisodeNo": 15
   }
   ```

4. **Deploy models** using [Capella Model Services](https://docs.couchbase.com/ai/build/model-service/model-service.html) for generating embeddings and a LLM for orchestrating the agents

5. **Vectorize the data** using the [Vectorization Workflow](https://docs.couchbase.com/ai/build/vectorization-service/vectorize-structured-data-capella.html) to create embeddings and a vector search index

## How It Works

### 1. Theme Analysis
The Theme Analyzer agent receives your theme and:
- Searches Couchbase for similar episode themes
- Identifies comedic angles for each character
- Finds the "nothing" that can be blown out of proportion

### 2. Plot Design
The Plot Architect creates:
- **A-Plot**: Main storyline (usually Jerry or ensemble)
- **B-Plot**: Secondary storyline (often George or Elaine)
- **C-Plot**: Tertiary storyline (usually Kramer's scheme)
- Convergence points where plots intersect

### 3. Character Voices
The Character Voice Specialist:
- Retrieves actual character dialogue from Couchbase
- Defines speech patterns and mannerisms for this episode
- Plans running gags and catchphrases

### 4. Script Writing
The Dialogue Writer:
- Writes scene-by-scene dialogue
- Uses RAG to match the style of similar scenes
- Includes stage directions and timing cues

### 5. Quality Review
The Quality Reviewer:
- Compares against actual Seinfeld scripts
- Checks character authenticity
- Polishes for comedic timing

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- Seinfeld™ is a trademark of Castle Rock Entertainment
- This is a fan project for educational purposes
