import pathlib
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
        leaked_key = "[REDACTED_NEWS_API_KEY_PREFIX]" + "[REDACTED_NEWS_API_KEY_SUFFIX]"
        offenders = []

        for path in iter_public_text_files():
            if leaked_key in path.read_text(encoding="utf-8", errors="ignore"):
                offenders.append(path.relative_to(REPO_ROOT).as_posix())

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

    def test_readme_contains_origin_story_and_no_bullshit_positioning(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("before dedicated coding assistants", readme)
        self.assertIn("Data provenance", readme)
        self.assertIn("Not financial advice", readme)


if __name__ == "__main__":
    unittest.main()
