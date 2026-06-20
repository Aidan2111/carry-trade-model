import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))


class SystemEvaluationTests(unittest.TestCase):
    def test_system_evaluation_reports_api_contract_and_update_gate(self):
        from scripts.system_evaluation import run_system_evaluation

        report = run_system_evaluation()

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["checks"]["health"]["status_code"], 200)
        self.assertEqual(report["checks"]["dashboard"]["status_code"], 200)
        self.assertEqual(report["checks"]["model_update_disabled"]["status_code"], 403)
        self.assertEqual(report["checks"]["dashboard"]["data_source"], "REAL_DATA")
        self.assertEqual(report["checks"]["dashboard"]["prediction_key_style"], "camelCase")
        self.assertEqual(report["checks"]["dashboard"]["signal_key_style"], "camelCase")


if __name__ == "__main__":
    unittest.main()
