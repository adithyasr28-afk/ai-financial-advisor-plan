import math
import pytest

from backend.backtesting.engine import (
    run_backtest,
    sma,
    rsi,
    signals_sma_crossover,
    STRATEGIES,
)


def test_buy_hold_matches_simple_total_return():
    closes = [100.0, 110.0, 121.0, 133.1]  # +10% each day
    result = run_backtest(closes, "buy_hold")
    expected_total_return = (closes[-1] / closes[0] - 1) * 100
    assert result.total_return_pct == pytest.approx(expected_total_return, rel=1e-9)
    assert result.trades == 0
    assert result.max_drawdown_pct == pytest.approx(0.0, abs=1e-9)


def test_buy_hold_flat_price_series_has_zero_return_and_sharpe():
    closes = [100.0] * 10
    result = run_backtest(closes, "buy_hold")
    assert result.total_return_pct == pytest.approx(0.0, abs=1e-9)
    assert result.sharpe_ratio == 0.0
    assert result.max_drawdown_pct == pytest.approx(0.0, abs=1e-9)


def test_max_drawdown_detects_a_real_drop():
    # up to 120, down to 90, recover to 100
    closes = [100.0, 110.0, 120.0, 105.0, 90.0, 100.0]
    result = run_backtest(closes, "buy_hold")
    expected_dd = (90.0 / 120.0 - 1) * 100
    assert result.max_drawdown_pct == pytest.approx(expected_dd, rel=1e-9)


def test_signal_is_lagged_by_one_day_to_avoid_lookahead():
    # SMA crossover should hold *yesterday's* signal today. We verify this by
    # manually recomputing equity using the same lag rule and the same
    # (default) strategy parameters run_backtest actually uses internally.
    closes = [100 + i * 0.3 + 5 * math.sin(i / 3) for i in range(120)]
    signals = signals_sma_crossover(closes)  # defaults: fast=20, slow=50 - must match STRATEGIES["sma_crossover"]
    result = run_backtest(closes, "sma_crossover")
    daily_returns = [0.0] + [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]
    equity = [100.0]
    for i in range(1, len(closes)):
        position = signals[i - 1]
        equity.append(equity[-1] * (1 + daily_returns[i] * position))
    assert result.equity_curve == pytest.approx(equity, rel=1e-9)


def test_unknown_strategy_raises():
    with pytest.raises(ValueError):
        run_backtest([100.0, 101.0], "not_a_real_strategy")


def test_too_few_points_raises():
    with pytest.raises(ValueError):
        run_backtest([100.0], "buy_hold")


def test_sma_helper_returns_none_until_window_filled():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = sma(values, window=3)
    assert result[:2] == [None, None]
    assert result[2] == pytest.approx((1 + 2 + 3) / 3)
    assert result[4] == pytest.approx((3 + 4 + 5) / 3)


def test_rsi_is_100_when_no_losses_in_window():
    values = [100.0 + i for i in range(20)]  # strictly increasing
    result = rsi(values, period=14)
    assert result[14] == pytest.approx(100.0)


def test_all_strategies_produce_a_result_on_realistic_length_series():
    # 252 trading days, mildly noisy upward drift - representative of what
    # a real ~1y Yahoo Finance pull would look like.
    closes = [100.0]
    for i in range(1, 252):
        closes.append(closes[-1] * (1 + 0.0005 * math.sin(i / 5) + 0.0002))
    for name in STRATEGIES:
        result = run_backtest(closes, name)
        assert isinstance(result.total_return_pct, float)
        assert len(result.equity_curve) == len(closes)
        assert result.trades >= 0
        assert 0.0 <= result.win_rate_pct <= 100.0
