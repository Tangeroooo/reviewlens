import unittest
from api import status_rows
from queue_selection import retry_ids

class RetryPolicyTests(unittest.TestCase):
    def test_status_and_selection(self):
        jobs = [
            {"id": "a", "state": "failed", "attempts": 0},
            {"id": "b", "state": "failed", "attempts": 3},
            {"id": "c", "state": "running", "attempts": 0},
            {"id": "d", "state": "done", "attempts": 0},
            {"id": "e", "state": "failed", "attempts": 2},
        ]
        self.assertEqual(status_rows(jobs, 3), [
            {"id": "a", "retryable": True}, {"id": "b", "retryable": False},
            {"id": "c", "retryable": False}, {"id": "d", "retryable": False},
            {"id": "e", "retryable": True},
        ])
        self.assertEqual(retry_ids(jobs, 3), ["a", "e"])

    def test_empty(self):
        self.assertEqual(status_rows([], 3), [])
        self.assertEqual(retry_ids([], 3), [])

    def test_disabled_retry(self):
        jobs = [{"id": "a", "state": "failed", "attempts": 0}]
        self.assertEqual(status_rows(jobs, 0), [{"id": "a", "retryable": False}])
        self.assertEqual(retry_ids(jobs, 0), [])
