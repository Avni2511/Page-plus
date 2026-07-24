import time
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

class AuditorError(Exception):
    """Base exception class for the webpage auditor service."""
    pass

class AuditorTimeoutError(AuditorError):
    """Raised when the URL fetch request times out."""
    pass

class AuditorConnectionError(AuditorError):
    """Raised when a network connection error (e.g., DNS resolution failure) occurs."""
    pass

class AuditorNonHtmlError(AuditorError):
    """Raised when the target page is not an HTML document."""
    pass

class AuditorRequestError(AuditorError):
    """Raised when there is any other network or protocol failure."""
    pass

def fetch_and_measure_webpage(url, timeout=10):
    """
    Fetches the content of the target URL, measures response time, and ensures
    the response is an HTML document.

    Returns:
        tuple: (html_content, response_time_seconds, status_code)
    """
    # Custom headers to act as a friendly browser audit bot
    headers = {
        'User-Agent': 'PagePulseAuditor/1.0 (Web Audit Utility; SDE Internship Assignment)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }

    start_time = time.perf_counter()
    try:
        # We perform a GET request. We set verify=True by default, but fallback to ConnectionError if SSL fails.
        # Allow redirects so we reach the final destination page.
        response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        response_time = round(time.perf_counter() - start_time, 2)

        # Validate Content-Type header
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type.lower():
            raise AuditorNonHtmlError("The provided URL does not return an HTML document.")

        return response.text, response_time, response.status_code

    except Timeout:
        raise AuditorTimeoutError("The request timed out while trying to reach the URL.")
    except ConnectionError:
        raise AuditorConnectionError("Connection failed or DNS error occurred. Verify the URL is correct.")
    except AuditorNonHtmlError:
        raise
    except RequestException as e:
        raise AuditorRequestError(f"An unexpected request error occurred: {str(e)}")
