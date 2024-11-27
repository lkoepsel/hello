import unittest
import os
import tempfile
from hello_server_v2 import app, init_db

class TestHelloServer(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Initialize the test database
        with app.app_context():
            init_db()

    def tearDown(self):
        # Close and remove the temporary database
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_get_route(self):
        # Test the GET route
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!doctype html>', response.data.lower())

    def test_valid_post(self):
        # Test posting valid data
        test_text = "Hello, World!"
        response = self.client.post('/', data={'text': test_text})
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'Data received successfully')

        # Verify data appears in GET response
        response = self.client.get('/')
        self.assertIn(bytes(test_text, 'utf-8'), response.data)

    def test_empty_post(self):
        # Test posting empty data
        response = self.client.post('/', data={'text': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Text cannot be empty', response.data.decode())

    def test_long_post(self):
        # Test posting text that exceeds maximum length
        long_text = 'a' * 1001  # Create text longer than 1000 characters
        response = self.client.post('/', data={'text': long_text})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Text too long', response.data.decode())

    def test_multiple_posts(self):
        # Test multiple POST requests
        test_texts = ["First message", "Second message", "Third message"]
        
        # Send multiple messages
        for text in test_texts:
            response = self.client.post('/', data={'text': text})
            self.assertEqual(response.status_code, 200)

        # Verify all messages appear in GET response
        response = self.client.get('/')
        for text in test_texts:
            self.assertIn(bytes(text, 'utf-8'), response.data)

    def test_missing_text_field(self):
        # Test POST request without 'text' field
        response = self.client.post('/', data={})
        self.assertEqual(response.status_code, 400)

    def test_whitespace_only_text(self):
        # Test posting whitespace-only text
        response = self.client.post('/', data={'text': '   '})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Text cannot be empty', response.data.decode())

if __name__ == '__main__':
    unittest.main()
