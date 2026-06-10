"""Model-theory validation tests for the improved carry trade model.

These tests check the statistical machinery rather than release hygiene:

1. The prediction target is genuinely forward-looking (no peeking at the past).
2. Time-series cross-validation reports roughly zero skill on pure noise,
   which would fail if features or folds leaked future information.
3. The pipeline recovers a deliberately planted signal, so a near-zero score
   on noise reflects honest validation rather than a broken model.

The tests swap the heavy stacking ensemble for a small Ridge-based ensemble
so the suite stays fast enough to run on every change.
"""

import pathlib
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from sklearn.linear_model import Ridge

from improved_ensemble_model import ImprovedCarryTradeModel


class FastCarryTradeModel(ImprovedCarryTradeModel):
    """Same pipeline, but with a tiny base-model set for fast tests."""

    def _build_base_models(self, n_estimators=100):
        return [
            ("ridge_a", Ridge(alpha=1.0)),
            ("ridge_b", Ridge(alpha=10.0)),
        ]


def make_market_frame(n_days=400, seed=7):
    """Build a merged data frame shaped like load_and_prepare_data output."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2022-01-01", periods=n_days, freq="D")

    usd = 36.0 * np.cumprod(1 + rng.normal(0, 0.004, n_days))
    eur = 39.0 * np.cumprod(1 + rng.normal(0, 0.005, n_days))

    frame = pd.DataFrame(
        {
            "date": dates,
            "USD_UAH": usd,
            "EUR_UAH": eur,
            "US_FedFunds": rng.uniform(4.0, 5.5, n_days),
            "EU_Rate": rng.uniform(2.5, 4.0, n_days),
            "UAH_Rate": rng.uniform(13.0, 18.0, n_days),
            "US_CPI": rng.uniform(2.0, 6.0, n_days),
            "US_InflationExpectations": rng.uniform(2.0, 4.0, n_days),
            "US_YieldCurve": rng.uniform(0.5, 3.0, n_days),
            "EU_ConsumerPrices": rng.uniform(1.5, 5.0, n_days),
            "sentiment_usd": rng.normal(0, 0.3, n_days),
            "sentiment_eur": rng.normal(0, 0.3, n_days),
            "sentiment_uah": rng.normal(-0.1, 0.3, n_days),
        }
    )
    return frame


class TargetConstructionTests(unittest.TestCase):
    def test_target_is_forward_seven_day_return(self):
        model = FastCarryTradeModel()
        data = model._enhanced_feature_engineering(make_market_frame())

        prices = data["USD_UAH"].to_numpy()
        targets = data["usd_return"].to_numpy()

        # usd_return at row t must equal the return realized from t to t+7.
        for t in (0, 50, 200, len(data) - 8):
            expected = prices[t + 7] / prices[t] - 1
            self.assertAlmostEqual(targets[t], expected, places=10)

        # The last 7 rows have no future price, so the target must be NaN
        # there instead of silently reusing past data.
        self.assertTrue(np.isnan(targets[-7:]).all())


class LeakageAndSignalRecoveryTests(unittest.TestCase):
    def _run_cv(self, data):
        model = FastCarryTradeModel()
        X, y_usd, y_eur, dates, _ = model.prepare_features_and_targets(data)
        results = model.time_series_split_validation(X, y_usd, y_eur, dates)
        return float(np.mean(results["usd_scores"]))

    def test_cv_folds_keep_purge_gap_between_train_and_validation(self):
        model = FastCarryTradeModel()
        data = model._enhanced_feature_engineering(make_market_frame(seed=11))
        X, y_usd, y_eur, dates, _ = model.prepare_features_and_targets(data)
        results = model.time_series_split_validation(X, y_usd, y_eur, dates)

        self.assertTrue(results["fold_dates"], "CV produced no folds")
        for fold in results["fold_dates"]:
            separation = (fold["val_start"] - fold["train_end"]).days
            # The 7-day forward target needs prices through train_end + 7, so
            # validation must start more than 7 days after training ends.
            self.assertGreater(
                separation,
                7,
                f"Fold {fold['fold']} validation starts {separation} day(s) "
                "after training ends; the 7-day purge gap is missing",
            )

    def test_cross_validation_reports_no_skill_on_pure_noise(self):
        model = FastCarryTradeModel()
        data = model._enhanced_feature_engineering(make_market_frame(seed=11))

        # Replace the target with noise that is independent of every feature.
        rng = np.random.default_rng(99)
        noise = rng.normal(0, 0.01, len(data))
        data["usd_return"] = noise
        data["eur_return"] = noise

        avg_r2 = self._run_cv(data)
        self.assertLess(
            avg_r2,
            0.05,
            "CV reported skill on a noise target; check for feature/target leakage",
        )

    def test_cross_validation_recovers_planted_signal(self):
        model = FastCarryTradeModel()
        data = model._enhanced_feature_engineering(make_market_frame(seed=23))

        # Plant a linear relationship between a carry feature and the target.
        rng = np.random.default_rng(99)
        signal = 0.002 * (data["interest_diff_usd"] - data["interest_diff_usd"].mean())
        data["usd_return"] = signal + rng.normal(0, 0.0005, len(data))
        data["eur_return"] = signal + rng.normal(0, 0.0005, len(data))

        avg_r2 = self._run_cv(data)
        self.assertGreater(
            avg_r2,
            0.5,
            "CV failed to recover a strong planted signal; pipeline may be broken",
        )


if __name__ == "__main__":
    unittest.main()
