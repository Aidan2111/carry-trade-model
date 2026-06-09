import hashlib
import json
import pathlib
import re
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".tsx",
    ".ts",
    ".json",
    ".template",
    ".example",
    ".txt",
}
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "build",
    "dist",
    "__pycache__",
}


def iter_public_text_files():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if EXCLUDED_PARTS.intersection(path.parts):
            continue
        if path.suffix in TEXT_SUFFIXES:
            yield path


class PublicReadinessTests(unittest.TestCase):
    def test_no_hardcoded_newsapi_key_is_present(self):
        leaked_key_sha256 = (
            "37dc8f765f17593933431a0e0921379473c44cfb2328816cc28464d9c2a1f8a9"
        )
        offenders = []

        for path in iter_public_text_files():
            content = path.read_text(encoding="utf-8", errors="ignore")
            for token in re.findall(r"\b[a-fA-F0-9]{32}\b", content):
                token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
                if token_hash == leaked_key_sha256:
                    offenders.append(path.relative_to(REPO_ROOT).as_posix())
                    break

        self.assertEqual(offenders, [], f"Hardcoded NewsAPI key found in {offenders}")

    def test_dashboard_fetches_api_data_instead_of_static_mock_data(self):
        dashboard = (REPO_ROOT / "frontend/src/components/Dashboard.tsx").read_text(
            encoding="utf-8"
        )

        self.assertIn("ApiService.getDashboardData", dashboard)
        self.assertNotIn("const mockData", dashboard)

    def test_public_env_example_exists_and_documents_optional_keys(self):
        env_example = REPO_ROOT / ".env.example"

        self.assertTrue(env_example.exists(), ".env.example should exist for public setup")
        content = env_example.read_text(encoding="utf-8")
        self.assertIn("NEWS_API_KEY=", content)
        self.assertIn("FRED_API_KEY=", content)

        env_template = (REPO_ROOT / ".env.template").read_text(encoding="utf-8")
        self.assertNotIn("your_", env_template)

    def test_readme_contains_origin_story_and_no_bullshit_positioning(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("before dedicated coding assistants", readme)
        self.assertIn("Data provenance", readme)
        self.assertIn("Not financial advice", readme)

    def test_readme_explains_free_and_paid_data_source_paths(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Free/no-key data", readme)
        self.assertIn("Optional free API keys", readme)
        self.assertIn("Paid or premium data", readme)
        self.assertIn("Higher-quality data usually comes from paid providers", readme)

    def test_frontend_dev_server_docs_match_vite_script(self):
        package = json.loads((REPO_ROOT / "frontend/package.json").read_text(encoding="utf-8"))
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        dashboard_readme = (REPO_ROOT / "README_DASHBOARD.md").read_text(encoding="utf-8")

        self.assertIn("--host 127.0.0.1", package["scripts"]["start"])
        self.assertIn("--port 5173", package["scripts"]["start"])
        self.assertIn("http://127.0.0.1:5173", readme)
        self.assertIn("http://127.0.0.1:5173", dashboard_readme)

    def test_canonical_api_uses_local_safe_defaults(self):
        api = (REPO_ROOT / "api_server_real_data.py").read_text(encoding="utf-8")

        self.assertIn("ENABLE_MODEL_UPDATE_ENDPOINT", api)
        self.assertIn("FLASK_HOST", api)
        self.assertIn("127.0.0.1", api)
        self.assertIn("CORS_ORIGINS", api)
        self.assertNotIn("CORS(app)  # Enable CORS for all routes", api)
        self.assertNotIn("app.run(host='0.0.0.0'", api)

    def test_legacy_api_servers_delegate_to_canonical_real_data_api(self):
        for filename in ("api_server.py", "api_server_live.py"):
            content = (REPO_ROOT / filename).read_text(encoding="utf-8")
            self.assertIn("from api_server_real_data import app", content)
            self.assertNotIn("np.random", content)
            self.assertNotIn("debug=True", content)
            self.assertNotIn("CORS(app)", content)

    def test_public_entrypoints_do_not_create_synthetic_live_market_data(self):
        checked_files = (
            "api_server_real_data.py",
            "api_server.py",
            "api_server_live.py",
            "dashboard_integration.py",
            "enhanced_scraper_simple.py",
            "enhanced_auto_scraper.py",
            "real_time_data_engine.py",
            "run_live_model.py",
            "carry_model.py",
            "carry_model_live_logged.py",
            "carry_model_live_with_fx_keyed.py",
        )
        forbidden = (
            "Return mock data",
            "Default values if no log exists",
            "simulated",
            "random walk",
            "np.random",
            "np.random.normal(12.5",
            "np.random.uniform(0.6",
        )

        offenders = []
        for filename in checked_files:
            content = (REPO_ROOT / filename).read_text(encoding="utf-8")
            for marker in forbidden:
                if marker in content:
                    offenders.append(f"{filename}: {marker}")

        self.assertEqual(offenders, [], f"Synthetic public entrypoint data found: {offenders}")

    def test_model_update_paths_do_not_run_legacy_synthetic_scripts(self):
        integration = (REPO_ROOT / "dashboard_integration.py").read_text(encoding="utf-8")
        self.assertNotIn("carry_model_live_logged.py", integration)
        self.assertNotIn("subprocess.run", integration)

        live_runner = (REPO_ROOT / "run_live_model.py").read_text(encoding="utf-8")
        self.assertNotIn("np.random", live_runner)
        self.assertNotIn("placeholder", live_runner.lower())
        self.assertNotIn("benchmark_return", live_runner)

    def test_frontend_empty_states_do_not_imply_background_analysis(self):
        checked_files = (
            "frontend/src/components/ModelPredictionsCard.tsx",
            "frontend/src/components/NewsCard.tsx",
            "frontend/src/components/SentimentCard.tsx",
        )
        forbidden = (
            "Training AI models",
            "Generating predictions",
            "Loading market news",
            "Scanning financial headlines",
            "Analyzing market sentiment",
            "Processing news feeds",
        )

        offenders = []
        for filename in checked_files:
            content = (REPO_ROOT / filename).read_text(encoding="utf-8")
            for marker in forbidden:
                if marker in content:
                    offenders.append(f"{filename}: {marker}")

        self.assertEqual(offenders, [], f"Misleading frontend empty states: {offenders}")

    def test_premium_api_clients_do_not_send_keys_over_plain_http(self):
        client = (REPO_ROOT / "production_api_client.py").read_text(encoding="utf-8")

        self.assertIn("https://data.fixer.io/api/latest", client)
        self.assertNotIn("http://data.fixer.io/api/latest", client)

    def test_live_trading_demo_is_paper_only_by_default(self):
        trading_demo = (REPO_ROOT / "live_trading_deployment.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("PaperTradingResearchBot", trading_demo)
        self.assertIn("ENABLE_LIVE_TRADING", trading_demo)
        self.assertNotIn("Production-ready live trading bot", trading_demo)
        self.assertNotIn("Ready-to-run script for live trading deployment", trading_demo)


if __name__ == "__main__":
    unittest.main()
