# Page Pulse

## Overview
**Page Pulse** is a webpage auditing utility designed to analyze the metadata, SEO posture, and response latency of any public website. A user enters a URL on the frontend dashboard, and the tool evaluates and presents performance indicators, tag hygiene, and content metrics.

---

## Features
- **HTTP Status Code Auditor**: Reports status of the remote server.
- **Latency Tracker**: Measures precise page fetch response times.
- **Title & Description Extractor**: Validates `<title>` and `<meta name="description">` tags.
- **Header Structure Audit**: Counts `<h1>` element frequencies.
- **Image Accessibility Check**: Identifies `<img>` tags missing or containing empty `alt` attributes.
- **Clean Content word-counter**: Excludes scripts, stylesheets, and navigation templates to calculate visible word count.
- **Robust Exception Shielding**: Prevents Python tracebacks from leaking to the client interface.

---

## Tech Stack
- **Backend Framework**: Django + Django REST Framework (DRF)
- **Scraping & Parsing**: Requests, BeautifulSoup4
- **Frontend Engine**: HTML5, Vanilla CSS3 (Custom design system), Vanilla ES6 JavaScript (Fetch API)
- **Test Runner**: Django TestCase + Unittest Mock

---

## Architecture
```
   Frontend Dashboard (HTML/CSS/JS)
                 │
                 ▼  (HTTP POST /api/audit/)
     Django REST Framework API View
                 │
                 ▼  (Invoke Fetcher)
      URL Fetching Service (requests)
                 │
                 ▼  (Extract Metrics)
      HTML Parser Service (BeautifulSoup4)
                 │
                 ▼  (Formulate Response)
      Django API View (JSON payload)
                 │
                 ▼  (Render Cards)
   Frontend Results Render (DOM Updates)
```

---

## Project Structure
```
page-pulse/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   └── auditor/
│       ├── parsers.py         # BS4 HTML parsing rules
│       ├── services.py        # Fetching engine and timing logic
│       ├── views.py           # API views and payload validators
│       ├── urls.py            # App route map
│       ├── tests.py           # API and service unit test cases
│       └── apps.py
│
├── frontend/
│   ├── index.html             # Dashboard view structure
│   ├── style.css              # Custom styling
│   └── script.js              # Fetch connection and dynamic state actions
│
└── .gitignore
```

---

## Setup Instructions

### Backend Setup

1. **Create and Activate a Virtual Environment**:
   ```powershell
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Launch Server**:
   ```bash
   python manage.py runserver
   ```
   The backend API will run on `http://127.0.0.1:8000/`.

### Frontend Setup

Since the frontend is built using standard Vanilla Web components:
- Open `frontend/index.html` directly in any web browser, OR
- Serve it using a lightweight local web server:
  ```bash
  # Python 3 built-in server
  python -m http.server 8080 --directory frontend
  ```
  Then open `http://localhost:8080` in your web browser.

---

## API Contract

### POST `/api/audit/`

#### Request Payload
```json
{
    "url": "https://example.com"
}
```

#### Success Response (`200 OK`)
```json
{
    "url": "https://example.com",
    "status_code": 200,
    "response_time": 0.42,
    "title": "Example Domain",
    "meta_description": "Example description",
    "h1_count": 1,
    "images_missing_alt": 2,
    "word_count": 150
}
```

#### Client Validation Error (`400 Bad Request`)
```json
{
    "error": "Invalid URL. Please provide a valid HTTP or HTTPS URL."
}
```

#### Target Non-HTML Error (`422 Unprocessable Entity`)
```json
{
    "error": "The provided URL does not return an HTML document."
}
```

#### Target Gateway Timeout Error (`504 Gateway Timeout`)
```json
{
    "error": "The request timed out while trying to reach the URL."
}
```

---

## Error Handling
1. **Invalid URLs**: Validates scheme (`http://` or `https://`) and formats using Django's core `URLValidator`.
2. **Timeout**: Restricts requests to 10 seconds. Throws standard gateway error rather than keeping threads open.
3. **Network Failure**: Catches DNS resolution errors or server disconnects safely and displays clean client-facing feedback.
4. **Non-HTML responses**: Inspects response `Content-Type` header and rejects non-HTML payloads immediately.

---

## Testing
To run the automated Django test suite, run the following command in the `backend/` directory:
```bash
python manage.py test auditor
```

---

## Design Decisions

1. **Why Django REST Framework (DRF) was used**:
   Provides robust serialization, validation, standard HTTP error responses, and clean architectural abstractions for developing reliable Web APIs.
2. **Why parsing logic was separated from the API view**:
   Decoupling the BeautifulSoup parser (`parsers.py`) and remote page retriever (`services.py`) from the view handler (`views.py`) ensures modular, reusable, and unit-testable code that respects the single responsibility principle.
3. **Why timeout and error handling were implemented**:
   Ensures application reliability. Bad or slow URLs provided by users could crash threads or trigger server timeouts; wrapping external calls safeguards the backend and prevents Python stack trace leaks.

---

## Future Improvements
1. **Scraping Agent Rotation**: Implement rotating User-Agent strings and proxy rotators to avoid bot-detection blocking.
2. **Asynchronous Scraping (Celery + Redis)**: Hand off scraping execution to background workers for massive performance gains when auditing larger pages or multiple URLs in batches.
3. **Audit History DB Store**: Save report records in database to let users compare progress over time.
4. **Deep SEO Checks**: Add page speed metrics, link validation (checking for broken anchors), and schema markup audits.
