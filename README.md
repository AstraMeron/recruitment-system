# AI-Powered Recruitment & Automated Dispatch System

An end-to-end recruitment engine designed to parse complex resumes, rank candidates based on semantic relevance, and dispatch personalized, high-concurrency automated emails.

## 🚀 Key Features

### Task 1: Intelligent Resume Parser & Ranker
* **Context-Aware Parsing:** Uses a sliding-window heuristic to extract education and experience data from multi-line PDF structures.
* **NER Name Validation:** Leverages spaCy's Named Entity Recognition to distinguish candidate names from job titles and locations.
* **Multi-Signal Ranking:** A hybrid scoring algorithm combining semantic similarity (Sentence-Transformers) with experience-year weighting.
* **Skill Normalization:** Maps varied technical terminology (e.g., "py" -> "Python") to a standardized internal map.

### Task 2: Async Dynamic Email Engine
* **High Concurrency:** Implements `asyncio.Semaphore` to process and dispatch batches of emails concurrently without sequential blocking.
* **Jinja2 Templating:** A professional-grade templating layer to prevent "placeholder leakage" and ensure 1:1 personalization.
* **Reliability & Retries:** Features a 3-tier retry mechanism with exponential backoff for handling SMTP timeouts and network blips.
* **Persistent Logging:** Generates a structured JSON lifecycle log (`email_dispatch_log.json`) tracking `pending`, `sent`, and `failed` statuses.

## 🛠️ Technical Stack
* **Language:** Python 3.10+
* **Parsing:** `pdfplumber`, `re` (Regex), `spaCy` (NLP)
* **Ranking:** `sentence-transformers`, `scikit-learn`
* **Async/Email:** `asyncio`, `Jinja2`

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-link>
   cd recruitment-system
  ```bash

2. Install Python Dependencies
pip install -r requirements.txt
3. Download NLP Models
The parser requires the spaCy English model for Named Entity Recognition:
python -m spacy download en_core_web_sm
📈 Usage
1. Run Resume Ranking (Task 1)
Parses PDFs in data/resumes/, calculates experience, and outputs a ranked list of candidates based on semantic relevance.
python src/ranker.py
2. Run Automated Email Dispatcher (Task 2)
Processes batch user data, injects it into the Jinja2 template, and dispatches emails concurrently with built-in retry logic.
python src/email_service.py
This is as clean as it gets — exactly what GitHub expects. Copy → paste → done.   