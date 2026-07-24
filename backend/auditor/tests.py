from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
import requests

class PagePulseAPITests(APITestCase):
    
    def setUp(self):
        self.audit_url = reverse('audit')
        
    @patch('auditor.services.requests.get')
    def test_happy_path(self, mock_get):
        """
        Happy path: Ensure a valid HTML page returns correct metrics.
        """
        # Mock responses structure
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html; charset=utf-8'}
        mock_response.text = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>My Test Page</title>
            <meta name="description" content="This is a test webpage meta description.">
        </head>
        <body>
            <h1>Main Title Header</h1>
            <p>Here is some visible text with several words to audit.</p>
            <img src="pic1.jpg" alt="A nice picture">
            <img src="pic2.jpg"> <!-- missing alt -->
            <img src="pic3.jpg" alt=""> <!-- empty alt -->
        </body>
        </html>
        """
        
        data = {"url": "https://happy-path.example.com"}
        response = self.client.post(self.audit_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["url"], "https://happy-path.example.com")
        self.assertEqual(response.data["status_code"], 200)
        self.assertGreaterEqual(response.data["response_time"], 0.0)
        self.assertEqual(response.data["title"], "My Test Page")
        self.assertEqual(response.data["meta_description"], "This is a test webpage meta description.")
        self.assertEqual(response.data["h1_count"], 1)
        self.assertEqual(response.data["images_missing_alt"], 2)  # One missing, one empty alt
        self.assertEqual(response.data["word_count"], 16)  # Title (3 words) + H1 (3 words) + Paragraph (10 words) = 16 words.


    def test_invalid_url_missing(self):
        """
        Verify missing url returns Bad Request.
        """
        response = self.client.post(self.audit_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Invalid URL. Please provide a valid HTTP or HTTPS URL.")

    def test_invalid_url_malformed(self):
        """
        Verify malformed/missing scheme url returns Bad Request.
        """
        # No http/https scheme
        response = self.client.post(self.audit_url, {"url": "example.com"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid URL. Please provide a valid HTTP or HTTPS URL.")
        
        # Empty string
        response = self.client.post(self.audit_url, {"url": "   "}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid URL. Please provide a valid HTTP or HTTPS URL.")

        # Completely invalid domain
        response = self.client.post(self.audit_url, {"url": "http://invalid_domain#$#@.com"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid URL. Please provide a valid HTTP or HTTPS URL.")

    @patch('auditor.services.requests.get')
    def test_timeout_error(self, mock_get):
        """
        Mock a request timeout and verify Gateway Timeout (504) is returned.
        """
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out.")
        
        data = {"url": "https://timeout.example.com"}
        response = self.client.post(self.audit_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)
        self.assertEqual(response.data["error"], "The request timed out while trying to reach the URL.")

    @patch('auditor.services.requests.get')
    def test_connection_error(self, mock_get):
        """
        Mock a connection failure and verify Bad Request (400) is returned.
        """
        mock_get.side_effect = requests.exceptions.ConnectionError("DNS lookup failed.")
        
        data = {"url": "https://nonexistent-dns-domain.xyz"}
        response = self.client.post(self.audit_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Connection failed or DNS error occurred. Verify the URL is correct.")

    @patch('auditor.services.requests.get')
    def test_non_html_response(self, mock_get):
        """
        Verify returning non-HTML Content-Type (like application/json) throws Unprocessable Entity (422).
        """
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.text = '{"name": "test"}'
        
        data = {"url": "https://api.example.com/data.json"}
        response = self.client.post(self.audit_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["error"], "The provided URL does not return an HTML document.")

    @patch('auditor.services.requests.get')
    def test_missing_elements(self, mock_get):
        """
        Ensure pages missing standard tags (<title>, <meta description>) return "Not available".
        """
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = """
        <html>
        <body>
            <p>Only body text without title or description meta tag.</p>
        </body>
        </html>
        """
        
        data = {"url": "https://no-tags.example.com"}
        response = self.client.post(self.audit_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Not available")
        self.assertEqual(response.data["meta_description"], "Not available")
        self.assertEqual(response.data["h1_count"], 0)
        self.assertEqual(response.data["images_missing_alt"], 0)
        self.assertEqual(response.data["word_count"], 9) # "Only body text without title or description meta tag" -> 9 words.
