import pathlib
import subprocess
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


class RepositoryStructureTests(unittest.TestCase):
    def test_importable_code_is_grouped_by_responsibility_under_src(self):
        expected_package_paths = [
            "src/carry_trade/api/app.py",
            "src/carry_trade/api/data_provider.py",
            "src/carry_trade/api/routes.py",
            "src/carry_trade/api/server.py",
            "src/carry_trade/api/service.py",
            "src/carry_trade/dashboard/integration.py",
            "src/carry_trade/data/sources/news_client.py",
            "src/carry_trade/data/collectors/enhanced_scraper_simple.py",
            "src/carry_trade/data/providers/production_api_client.py",
            "src/carry_trade/data/runtime/real_time_data_engine.py",
            "src/carry_trade/modeling/experiments/improved_ensemble_model.py",
            "src/carry_trade/modeling/runners/run_live_model.py",
            "src/carry_trade/trading/live_trading_deployment.py",
        ]

        missing = [
            path
            for path in expected_package_paths
            if not (REPO_ROOT / path).exists()
        ]

        self.assertEqual(missing, [])

    def test_root_python_files_are_only_compatibility_entrypoints(self):
        allowed_root_files = {
            "api_server.py",
            "api_server_live.py",
            "api_server_real_data.py",
            "carry_model.py",
            "carry_model_live_logged.py",
            "carry_model_live_with_fx_keyed.py",
            "enhanced_scraper_simple.py",
            "improved_ensemble_model.py",
            "run_live_model.py",
        }
        root_python_files = {path.name for path in REPO_ROOT.glob("*.py")}

        self.assertEqual(root_python_files - allowed_root_files, set())

    def test_root_markdown_files_are_limited_to_the_primary_readme(self):
        root_markdown_files = {path.name for path in REPO_ROOT.glob("*.md")}

        self.assertEqual(root_markdown_files, {"README.md"})

    def test_repository_structure_doc_captures_current_layout(self):
        structure_doc = REPO_ROOT / "docs/architecture/repository-structure.md"

        self.assertTrue(structure_doc.exists())
        content = structure_doc.read_text(encoding="utf-8").lower()

        self.assertIn("microsoft learn", content)
        self.assertIn("well-architected framework", content)
        self.assertIn("src/carry_trade", content)
        self.assertIn("data/collectors", content)
        self.assertIn("modeling/experiments", content)
        self.assertIn("scripts/system_evaluation.py", content)
        self.assertIn("docs/process/branching-strategy.md", content)
        self.assertIn("root compatibility entrypoints", content)

    def test_runtime_data_ignore_rule_does_not_hide_source_packages(self):
        package_markers = [
            "src/carry_trade/data/__init__.py",
            "src/carry_trade/data/collectors/__init__.py",
            "src/carry_trade/data/providers/__init__.py",
            "src/carry_trade/data/runtime/__init__.py",
            "src/carry_trade/data/sources/__init__.py",
        ]

        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-v", *package_markers],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1, result.stdout)

    def test_branching_strategy_doc_matches_microsoft_guidance(self):
        strategy_doc = REPO_ROOT / "docs/process/branching-strategy.md"

        self.assertTrue(strategy_doc.exists())
        content = strategy_doc.read_text(encoding="utf-8").lower()

        self.assertIn("learn.microsoft.com/en-us/azure/devops/repos/git/git-branching-guidance", content)
        self.assertIn("well-architected", content)
        self.assertIn("main", content)
        self.assertIn("feature/", content)
        self.assertIn("hotfix/", content)
        self.assertIn("release/", content)
        self.assertIn("pull request", content)
        self.assertIn("quality gate", content)
        self.assertIn("scripts/system_evaluation.py", content)

    def test_pull_request_template_documents_review_and_verification_gates(self):
        template = REPO_ROOT / ".github/pull_request_template.md"

        self.assertTrue(template.exists())
        content = template.read_text(encoding="utf-8").lower()

        self.assertIn("summary", content)
        self.assertIn("testing", content)
        self.assertIn("risk", content)
        self.assertIn("docs updated", content)
        self.assertIn("scripts/system_evaluation.py", content)


if __name__ == "__main__":
    unittest.main()
