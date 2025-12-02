import json

from django.test import override_settings
from django.urls import reverse

from debug_toolbar.store import get_store

from ..base import IntegrationTestCase


@override_settings(DEBUG=True)
class TimerExportTests(IntegrationTestCase):
    def _generate_request_id(self):
        response = self.client.get("/json_view/")
        self.assertEqual(response.status_code, 200)
        request_ids = list(get_store().request_ids())
        self.assertTrue(request_ids)
        return request_ids[0]

    def test_timer_export_success(self):
        request_id = self._generate_request_id()
        response = self.client.get(
            reverse("djdt:timer_export"), {"request_id": request_id}
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["schema"], "debug-toolbar.timer.v1")
        self.assertEqual(payload["meta"]["request_id"], request_id)
        self.assertIn("timing", payload)
        self.assertIn("wall_time_ms", payload["timing"])
        self.assertIn("browser_timing", payload)
        self.assertIn(request_id, response["Content-Disposition"])

    def test_timer_export_missing_request_id(self):
        response = self.client.get(reverse("djdt:timer_export"))
        self.assertEqual(response.status_code, 400)

    def test_timer_export_unknown_request_id(self):
        response = self.client.get(
            reverse("djdt:timer_export"), {"request_id": "not-found"}
        )
        self.assertEqual(response.status_code, 400)

    def test_timer_export_with_browser_timing_payload(self):
        request_id = self._generate_request_id()
        timing_payload = [
            {"name": "connect", "start_ms": 1, "duration_ms": 2},
            {"name": "domInteractive", "start_ms": 5},
        ]
        response = self.client.get(
            reverse("djdt:timer_export"),
            {"request_id": request_id, "browser_timing": json.dumps(timing_payload)},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["browser_timing"], timing_payload)
