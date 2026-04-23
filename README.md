# AI-Powered Recruitment & Automated Dispatch System

An end-to-end recruitment engine designed to parse complex resumes, rank candidates based on semantic relevance, and dispatch personalized, automated emails.

## 🚀 Key Features

### Task 1: Intelligent Resume Parser & Ranker
- **Context-Aware Parsing:** Uses a sliding-window heuristic to extract education and experience data from multi-line PDF structures.
- **NER Name Validation:** Leverages spaCy's Named Entity Recognition to distinguish candidate names from job titles and locations.
- **Multi-Signal Ranking:** A hybrid scoring algorithm combining semantic similarity (Sentence-Transformers) with experience-year weighting.
- **Skill Normalization:** Maps varied technical terminology (e.g., "py" → "Python") to a standardized internal map.

### Task 2: Async Dynamic Email Engine
- **High Concurrency:** Implements `asyncio.Semaphore` to process and dispatch batches of emails concurrently without sequential blocking.
- **Jinja2 Templating:** Ensures proper personalization without placeholder leakage.
- **Reliability & Retries:** 3-tier retry mechanism with exponential backoff.
- **Persistent Logging:** Tracks `pending`, `sent`, and `failed` statuses in JSON logs.

## 🛠️ Technical Stack
- **Language:** Python 3.10+
- **Parsing:** `pdfplumber`, `re`, `spaCy`
- **Ranking:** `sentence-transformers`, `scikit-learn`
- **Async/Email:** `asyncio`, 

## 📦 Installation & Setup

1. Clone the repository:
    ```bash
    git clone <your-repo-link>
    cd recruitment-system
    ```

2. Install Python Dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Download NLP Models:
    The parser requires the spaCy English model for Named Entity Recognition:
    ```bash
    python -m spacy download en_core_web_sm
    ```

## 📈 Usage

1. Run Resume Ranking (Task 1):
    Parses PDFs in `data/resumes/`, calculates experience, and outputs a ranked list of candidates.
    ```bash
    python src/ranker.py
    ```

2. Run Automated Email Dispatcher (Task 2):
    Processes batch user data, injects it into the Jinja2 template, and dispatches emails concurrently.
    ```bash
    python src/email_service.py
    ```

## 🏗️ System Evolution

### V1: Initial Implementation (`src/email_service.py`)
* Designed for rapid deployment to meet project milestones.
* Uses asynchronous semaphores for basic concurrency.

### V2: Production-Ready Refactor (`src/email_system.py` & `src/templates.py`)
* **Queue-Based Architecture:** Implements an `asyncio.Queue` with multiple worker consumers to decouple data ingestion from processing.
* **Template Validation:** A dedicated `TemplateManager` uses Regex to auto-discover placeholders and validate user data before queuing.
* **Resilient Lifecycle:** Advanced retry logic with exponential backoff and real-time incremental logging to ensure no data loss during system interruptions.
