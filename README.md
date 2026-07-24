# Page Pulse

## Overview

**Page Pulse** is a webpage auditing utility designed to analyze the metadata, SEO posture, and response latency of any public website. A user enters a URL on the Page Pulse dashboard, and the tool evaluates and presents performance indicators, tag hygiene, and content metrics.

The application is built with Django REST Framework and uses Requests and BeautifulSoup4 to fetch and analyze the target webpage. The frontend is served through Django, allowing the complete application to be accessed from a single URL.

---

## Features

- **HTTP Status Code Auditor**: Reports the HTTP status code returned by the remote server.
- **Latency Tracker**: Measures the response time required to fetch the target webpage.
- **Title & Description Extractor**: Extracts and validates the `<title>` and `<meta name="description">` tags.
- **Header Structure Audit**: Counts `<h1>` elements present on the webpage.
- **Image Accessibility Check**: Identifies `<img>` elements with missing or empty `alt` attributes.
- **Clean Content Word Counter**: Calculates visible word count while excluding scripts, stylesheets, and other non-content elements.
- **Robust Exception Shielding**: Handles invalid URLs, network failures, timeouts, and non-HTML responses without exposing server-side tracebacks to users.
- **Single-URL Application**: Django serves both the frontend dashboard and REST API from the same deployed application.

---

## Tech Stack

- **Backend**: Django, Django REST Framework (DRF)
- **Web Fetching & Parsing**: Requests, BeautifulSoup4
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (Fetch API)
- **Testing**: Django TestCase, unittest.mock
- **Production Server**: Gunicorn
- **Deployment**: Render

---

## Architecture

```text
                 Page Pulse Dashboard
                    HTML/CSS/JS
                         │
                         │ POST /api/audit/
                         ▼
              Django REST Framework
                    API View
                         │
                         ▼
                URL Fetching Service
                     Requests
                         │
                         ▼
                 HTML Parser Service
                  BeautifulSoup4
                         │
                         ▼
                  Extract Audit Data
                         │
                         ▼
                JSON API Response
                         │
                         ▼
              Frontend DOM Rendering
                         │
                         ▼
                  Audit Report
```

The application follows a separation-of-concerns approach:

- **Views** handle HTTP requests, input validation, and API responses.
- **Services** handle external webpage fetching, response timing, timeouts, and network errors.
- **Parsers** handle HTML analysis and extract audit metrics using BeautifulSoup4.
- **Frontend** displays the audit results and handles user interaction.

---

## Project Structure

```text
page-pulse/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   └── auditor/
│       ├── parsers.py         # BeautifulSoup HTML parsing logic
│       ├── services.py        # URL fetching and response timing logic
│       ├── views.py           # API views and request handling
│       ├── urls.py            # API route configuration
│       ├── tests.py           # Automated test cases
│       └── apps.py
│
├── frontend/
│   ├── index.html             # Dashboard interface
│   ├── style.css              # Custom styling
│   └── script.js              # API communication and UI logic
│
├── README.md
└── .gitignore
```

---

## Local Setup Instructions

### Prerequisites

- Python 3.10+
- Git

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd page-pulse
```

### 2. Navigate to the Backend

```bash
cd backend
```

### 3. Create and Activate a Virtual Environment

#### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

### 7. Open the Application

Open the following URL in your browser:

```text
http://127.0.0.1:8000/
```

The Django application serves both the Page Pulse frontend and the REST API. No separate frontend development server is required.

---

## API Contract

### POST `/api/audit/`

Analyzes a public webpage and returns audit metrics.

### Request Payload

```json
{
    "url": "https://example.com"
}
```

### Success Response

**HTTP Status: `200 OK`**

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

### Client Validation Error

**HTTP Status: `400 Bad Request`**

```json
{
    "error": "Invalid URL. Please provide a valid HTTP or HTTPS URL."
}
```

### Target Non-HTML Error

**HTTP Status: `422 Unprocessable Entity`**

```json
{
    "error": "The provided URL does not return an HTML document."
}
```

### Target Gateway Timeout Error

**HTTP Status: `504 Gateway Timeout`**

```json
{
    "error": "The request timed out while trying to reach the URL."
}
```

---

## Error Handling

The application handles common failure scenarios gracefully:

1. **Invalid URLs**  
   Validates that the provided URL uses a valid HTTP or HTTPS scheme before processing the request.

2. **Timeouts**  
   Applies a request timeout to prevent slow or unresponsive websites from blocking the application indefinitely.

3. **Network Failures**  
   Handles DNS resolution failures, connection errors, and server disconnections with structured client-facing error responses.

4. **Non-HTML Responses**  
   Checks the target response content type and rejects resources that do not return HTML content.

5. **Exception Shielding**  
   Prevents internal Python tracebacks and sensitive server-side details from being exposed to users.

---

## Testing

Automated tests are implemented using Django's testing framework and Python's `unittest.mock`.

To run the test suite, navigate to the `backend/` directory and execute:

```bash
python manage.py test auditor
```

The tests cover the application's audit functionality and error-handling scenarios.

---

## Design Decisions

### 1. Separation of Concerns

The application separates API views, webpage fetching, and HTML parsing into different modules.

- `views.py` handles HTTP requests and responses.
- `services.py` handles external webpage fetching and network operations.
- `parsers.py` handles BeautifulSoup-based HTML parsing.

This separation keeps the application modular, reusable, and easier to test.

### 2. Robust Exception Handling

External webpages can fail due to invalid URLs, DNS errors, timeouts, or unexpected response types. These failures are mapped to structured API responses instead of exposing internal server tracebacks.

This improves reliability and provides a safer user experience.

### 3. Single-URL Application Architecture

The frontend and backend are served through the same Django application. This simplifies deployment and allows users to access the complete Page Pulse application through a single URL.

### 4. Production Configuration

The application uses Gunicorn as the production WSGI server and is deployed as a Django Web Service on Render.

---

## Deployment

The Page Pulse application is deployed on Render using Django and Gunicorn.

### Production Server

Gunicorn is used to serve the Django application in production:

```bash
gunicorn config.wsgi:application
```

### Live Application

**Page Pulse Live Application:**

https://page-plus-61vy.onrender.com/

The deployed application serves the Page Pulse frontend and Django REST API through a single URL.

---

## Future Improvements

1. **Asynchronous Scraping (Celery + Redis)**  
   Move webpage auditing to background workers to prevent long-running scraping operations from blocking Django request workers when handling multiple concurrent requests.

2. **Audit History Database**  
   Store audit reports in a database so users can view and compare previous audit results over time.

3. **Deep SEO Checks**  
   Add additional checks for broken links, page speed metrics, canonical tags, Open Graph metadata, structured data, and schema markup.

4. **Batch URL Auditing**  
   Allow users to submit and audit multiple URLs in a single operation.

5. **Improved Monitoring and Observability**  
   Add application logging and monitoring to track errors, response times, and service health in production.