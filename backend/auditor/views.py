import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import (
    fetch_and_measure_webpage,
    AuditorTimeoutError,
    AuditorConnectionError,
    AuditorNonHtmlError,
    AuditorRequestError
)
from .parsers import parse_html_report

class AuditView(APIView):
    """
    API View to handle webpage auditing.
    POST /api/audit/
    """
    def post(self, request, *args, **kwargs):
        url = request.data.get('url')
        
        # 1. Check if URL is missing or empty
        if not url:
            return Response(
                {"error": "Invalid URL. Please provide a valid HTTP or HTTPS URL."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        url = str(url).strip()
        if not url:
            return Response(
                {"error": "Invalid URL. Please provide a valid HTTP or HTTPS URL."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Check if URL lacks http:// or https://
        if not (url.startswith('http://') or url.startswith('https://')):
            return Response(
                {"error": "Invalid URL. Please provide a valid HTTP or HTTPS URL."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Perform DRF/Django URL validation
        validator = URLValidator(schemes=['http', 'https'])
        try:
            validator(url)
        except ValidationError:
            return Response(
                {"error": "Invalid URL. Please provide a valid HTTP or HTTPS URL."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Fetch the page, parse, and handle failures gracefully
        try:
            html_content, response_time, status_code = fetch_and_measure_webpage(url)
            metrics = parse_html_report(html_content)
            
            # Formulate final successful response payload
            payload = {
                "url": url,
                "status_code": status_code,
                "response_time": response_time,
                "title": metrics["title"],
                "meta_description": metrics["meta_description"],
                "h1_count": metrics["h1_count"],
                "images_missing_alt": metrics["images_missing_alt"],
                "word_count": metrics["word_count"]
            }
            return Response(payload, status=status.HTTP_200_OK)

        except AuditorTimeoutError as e:
            return Response(
                {"error": "The request timed out while trying to reach the URL."},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except AuditorNonHtmlError as e:
            return Response(
                {"error": "The provided URL does not return an HTML document."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except AuditorConnectionError as e:
            return Response(
                {"error": "Connection failed or DNS error occurred. Verify the URL is correct."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except AuditorRequestError as e:
            # Shield internal details/traceback while passing a friendly error message
            return Response(
                {"error": f"Failed to fetch webpage: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Fail-safe catch-all
            return Response(
                {"error": "An unexpected error occurred while parsing the webpage."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def serve_frontend_index(request):
    """
    Serves the index.html from the frontend folder at GET /
    """
    frontend_dir = os.path.join(settings.BASE_DIR.parent, 'frontend')
    file_path = os.path.join(frontend_dir, 'index.html')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='text/html')
    raise Http404("index.html not found")


def serve_frontend_static(request, filename):
    """
    Serves static files (style.css, script.js) from the frontend folder at root paths.
    """
    # Protect against directory traversal
    filename = os.path.basename(filename)
    frontend_dir = os.path.join(settings.BASE_DIR.parent, 'frontend')
    file_path = os.path.join(frontend_dir, filename)
    if os.path.exists(file_path):
        content_type = 'text/plain'
        if filename.endswith('.css'):
            content_type = 'text/css'
        elif filename.endswith('.js'):
            content_type = 'application/javascript'
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    raise Http404(f"{filename} not found")
