"""Behavioral tests of coverage accounting, not model review accuracy."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/reviewlens/scripts/check_coverage.py'
spec = importlib.util.spec_from_file_location('coverage_check', SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def fixture():
    return {
        'catalog': [{'id': 'behavior', 'source': 'general.md: Behavior'}],
        'performance_paths': [],
        'plan': [{'id': 'behavior-api', 'item': 'behavior', 'scope': 'api -> consumer',
                  'requirement': 'preserve empty result', 'pass': 'General',
                  'applicable': True, 'intended_extent': 'handler and sole registered consumer'}],
        'records': [{'id': 'behavior-api', 'status': 'inspected',
                     'examined_scope': ['api.py:handler -> consumer.py:read; registry.py registrations'],
                     'unexamined_scope': [], 'evidence': 'consumer handles empty result without fallback',
                     'result': 'No defect found in the specified path', 'reason': '',
                     'stop_reason': 'Traced to the sole registered observable consumer',
                     'execution': {'status': 'not_run', 'detail': 'Source inspection only; test execution optional'}}],
        'review_status': 'complete',
    }


class CoverageAccountingTest(unittest.TestCase):
    def test_complete_source_review_does_not_require_test_execution(self):
        self.assertEqual(checker.validate(fixture()), 'complete')

    def test_missing_record_and_unplanned_record_are_invalid(self):
        for missing in (True, False):
            data = fixture()
            if missing:
                data['records'] = []
            else:
                data['records'].append(dict(data['records'][0], id='extra'))
            with self.subTest(missing=missing), self.assertRaises(checker.Invalid):
                checker.validate(data)

    def test_duplicate_record_is_invalid(self):
        data = fixture()
        data['records'].append(copy.deepcopy(data['records'][0]))
        with self.assertRaises(checker.Invalid):
            checker.validate(data)

    def test_catalog_item_cannot_disappear_from_plan(self):
        data = fixture()
        data['catalog'].append({'id': 'error-chain', 'source': 'general.md: Error chaining'})
        with self.assertRaises(checker.Invalid):
            checker.validate(data)

    def test_partial_requires_reason_remaining_scope_and_partial_summary(self):
        data = fixture()
        record = data['records'][0]
        record.update(status='partial', unexamined_scope=['consumer.py:read'],
                      reason='Consumer source unavailable')
        with self.assertRaises(checker.Invalid):
            checker.validate(data)
        data['review_status'] = 'partial'
        self.assertEqual(checker.validate(data), 'partial')
        record['reason'] = ''
        with self.assertRaises(checker.Invalid):
            checker.validate(data)

    def test_no_candidates_is_valid_validator_exclusion(self):
        data = fixture()
        data['plan'][0]['applicable'] = False
        data['records'][0].update(status='not applicable', examined_scope=[],
                                 reason='No candidates requiring validation',
                                 evidence='Discovery candidate list is empty')
        self.assertEqual(checker.validate(data), 'complete')
        data['records'][0]['reason'] = ''
        with self.assertRaises(checker.Invalid):
            checker.validate(data)

    def test_inspection_requires_extent_and_cannot_hide_remaining_work(self):
        for field, value in [('examined_scope', []), ('unexamined_scope', ['other consumer']),
                             ('evidence', ''), ('stop_reason', '')]:
            data = fixture()
            data['records'][0][field] = value
            with self.subTest(field=field), self.assertRaises(checker.Invalid):
                checker.validate(data)

    def test_performance_paths_cannot_be_grouped(self):
        data = fixture()
        data['performance_paths'] = ['parser', 'evaluator']
        template = data['plan'][0]
        evidence = data['records'][0]
        for i in range(1, 9):
            item = f'P{i}'
            data['catalog'].append({'id': item, 'source': f'performance.md:{item}'})
            data['plan'].append(dict(template, id=item, item=item, scope='parser + evaluator'))
            data['records'].append(dict(evidence, id=item, cost_evidence={
                'base': 'One setup per request', 'target': 'One setup per request',
                'workload': 'Ten inputs', 'workload_source': 'Fixture contract',
                'safety_reuse': 'Request-local inputs'}))
        with self.assertRaisesRegex(checker.Invalid, 'performance scope missing|parser: missing P1'):
            checker.validate(data)
        data['performance_paths'].append('parser + evaluator')
        with self.assertRaisesRegex(checker.Invalid, 'parser: missing P1'):
            checker.validate(data)
        data['performance_paths'].remove('parser + evaluator')
        data['plan'] = data['plan'][:1]
        data['records'] = data['records'][:1]
        for path in data['performance_paths']:
            for i in range(1, 9):
                item = f'P{i}'
                data['plan'].append(dict(template, id=f'{path}-{item}', item=item, scope=path))
                data['records'].append(dict(evidence, id=f'{path}-{item}', cost_evidence={
                    'base': f'{path} baseline: one setup per request',
                    'target': f'{path} target: one setup per request',
                    'workload': 'One request with ten inputs',
                    'workload_source': 'Fixture contract',
                    'safety_reuse': 'Request-local immutable inputs'}))
        self.assertEqual(checker.validate(data), 'complete')
        del data['records'][-1]['cost_evidence']['workload_source']
        with self.assertRaises(checker.Invalid):
            checker.validate(data)

    def test_cli_exit_codes(self):
        complete = fixture()
        partial = fixture()
        partial['records'][0].update(status='not inspected', examined_scope=[],
                                     unexamined_scope=['api -> consumer'], reason='Source unavailable')
        partial['review_status'] = 'partial'
        for payload, code in [(json.dumps(complete), 0), (json.dumps(partial), 2), ('{', 1)]:
            with self.subTest(code=code):
                result = subprocess.run([sys.executable, str(SCRIPT)], input=payload,
                                        text=True, capture_output=True)
                self.assertEqual(result.returncode, code, result.stderr)


if __name__ == '__main__':
    unittest.main()
