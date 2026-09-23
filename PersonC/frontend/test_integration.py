"""Focused integration tests for the Person C end-to-end contract."""

import io
import unittest
from unittest.mock import patch

from api_client import analyze_crop, demo_diagnosis, normalize_response


class IntegrationTests(unittest.TestCase):
    def test_demo_covers_all_confidence_paths(self):
        self.assertEqual(demo_diagnosis("brown spots").status, "high")
        self.assertEqual(demo_diagnosis("mixed symptoms, not sure").status, "borderline")
        self.assertEqual(demo_diagnosis("severe wilting").status, "low")

    def test_normalizes_person_b_response(self):
        result = normalize_response(
            {
                "diagnosis": "Leaf spot",
                "image_confidence": 86,
                "recommendation": "Remove affected leaves.",
            }
        )
        self.assertEqual(result.disease, "Leaf spot")
        self.assertEqual(result.confidence, 0.86)
        self.assertEqual(result.status, "high")

    @patch("api_client.settings")
    @patch("api_client.requests.post")
    def test_sends_image_and_farmer_context_to_backend(self, post, mocked_settings):
        mocked_settings.backend_url = "https://example.test/analyze"
        mocked_settings.request_timeout_seconds = 5
        response = post.return_value
        response.json.return_value = {"disease": "Blight", "confidence": 0.9}
        response.raise_for_status.return_value = None

        result = analyze_crop(
            io.BytesIO(b"image"),
            "Tomato",
            "Leaf",
            "Brown spots",
        )

        self.assertEqual(result.disease, "Blight")
        _, kwargs = post.call_args
        self.assertEqual(kwargs["data"]["crop_name"], "Tomato")
        self.assertEqual(kwargs["data"]["plant_part"], "Leaf")
        self.assertEqual(kwargs["data"]["symptoms"], "Brown spots")
        self.assertIn("image", kwargs["files"])


if __name__ == "__main__":
    unittest.main()
