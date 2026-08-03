"""
A small, dependency-free backtesting engine.

Design choices, stated up front because they materially affect the numbers:
- Long/flat only - no shorting, no leverage. Every strategy is either fully
  invested (position=1) or fully in cash (position=0) each day.
- No transaction costs or slippage modeled. Real trading would erode returns,
  especially for higher-frequency signals like RSI mean reversion.
- The signal computed from day i's close determines the position held on
  day i+1, not day i itself - using today's own close to decide whether to
  hold a position today is look-ahead bias, since that price isn't known
  until the market closes.
- Sharpe ratio assumes a 0% risk-free rate and annualizes with sqrt(252).
"""

from dataclasses import dataclass
import math


@dataclass
class BacktestMetrics:
    total_return_pct: float
    annualized_return_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float
    trades: int
    win_rate_pct: float
    equity_curve: list[float]


def sma(values: list[float], window: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    for i in range(len(values)):
        if i + 1 >= window:
            out[i] = sum(values[i + 1 - window : i + 1]) / window
    return out


def rsi(values: list[float], period: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    gains = [0.0] * len(values)
    losses = [0.0] * len(values)
    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        gains[i] = max(change, 0.0)
        losses[i] = max(-change, 0.0)
    for i in range(period, len(values)):
        avg_gain = sum(gains[i - period + 1 : i + 1]) / period
        avg_loss = sum(losses[i - period + 1 : i + 1]) / period
        if avg_loss == 0:
            out[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            out[i] = 100 - (100 / (1 + rs))
    return out


def ema(values: list[float], span: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    alpha = 2 / (span + 1)
    prev: float | None = None
    for i, v in enumerate(values):
        prev = v if prev is None else alpha * v + (1 - alpha) * prev
        out[i] = prev
    return out


def macd_line(
    values: list[float], fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[list[float | None], list[float | None]]:
    ema_fast = ema(values, fast)
    ema_slow = ema(values, slow)
    macd = [f - s for f, s in zip(ema_fast, ema_slow)]  # both are fully populated from index 0
    signal_line = ema(macd, signal)
    return macd, signal_line


def signals_buy_hold(closes: list[float]) -> list[int]:
    return [1] * len(closes)


def signals_sma_crossover(closes: list[float], fast: int = 20, slow: int = 50) -> list[int]:
    fast_ma = sma(closes, fast)
    slow_ma = sma(closes, slow)
    position = 0
    out = []
    for f, s in zip(fast_ma, slow_ma):
        if f is not None and s is not None:
            position = 1 if f > s else 0
        out.append(position)
    return out


def signals_rsi_mean_reversion(
    closes: list[float], period: int = 14, oversold: float = 30, overbought: float = 70
) -> list[int]:
    r = rsi(closes, period)
    position = 0
    out = []
    for value in r:
        if value is not None:
            if value < oversold:
                position = 1
            elif value > overbought:
                position = 0
        out.append(position)
    return out


def signals_macd(closes: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> list[int]:
    macd, signal_line = macd_line(closes, fast, slow, signal)
    position = 0
    out = []
    for m, s in zip(macd, signal_line):
        if m is not None and s is not None:
            position = 1 if m > s else 0
        out.append(position)
    return out


STRATEGIES = {
    "buy_hold": signals_buy_hold,
    "sma_crossover": signals_sma_crossover,
    "rsi_mean_reversion": signals_rsi_mean_reversion,
    "macd": signals_macd,
}


def run_backtest(closes: list[float], strategy: str) -> BacktestMetrics:
    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy}. Choose one of: {', '.join(STRATEGIES)}")
    if len(closes) < 2:
        raise ValueError("Need at least 2 price points to backtest")

    signals = STRATEGIES[strategy](closes)
    daily_returns = [0.0] + [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]

    equity = [100.0]
    strategy_returns: list[float] = []
    for i in range(1, len(closes)):
        position = signals[i - 1]  # yesterday's signal decides today's position
        ret = daily_returns[i] * position
        strategy_returns.append(ret)
        equity.append(equity[-1] * (1 + ret))

    trades = sum(1 for i in range(1, len(signals)) if signals[i] != signals[i - 1])

    # Bucket returns into discrete long trades to compute a win rate
    trade_returns: list[float] = []
    segment_start = 0
    current_position = signals[0]
    for i in range(1, len(signals)):
        if signals[i] != current_position:
            if current_position == 1:
                trade_returns.append(equity[i] / equity[segment_start] - 1)
            segment_start = i
            current_position = signals[i]
    if current_position == 1 and segment_start < len(equity) - 1:
        trade_returns.append(equity[-1] / equity[segment_start] - 1)

    win_rate = (sum(1 for r in trade_returns if r > 0) / len(trade_returns) * 100) if trade_returns else 0.0

    total_return = equity[-1] / equity[0] - 1
    years = len(closes) / 252
    annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else total_return

    peak = equity[0]
    max_dd = 0.0
    for value in equity:
        peak = max(peak, value)
        max_dd = min(max_dd, (value - peak) / peak)

    mean_ret = sum(strategy_returns) / len(strategy_returns) if strategy_returns else 0.0
    variance = (
        sum((r - mean_ret) ** 2 for r in strategy_returns) / len(strategy_returns) if strategy_returns else 0.0
    )
    std = math.sqrt(variance)
    sharpe = (mean_ret / std) * math.sqrt(252) if std > 0 else 0.0

    return BacktestMetrics(
        total_return_pct=total_return * 100,
        annualized_return_pct=annualized_return * 100,
        max_drawdown_pct=max_dd * 100,
        sharpe_ratio=sharpe,
        trades=trades,
        win_rate_pct=win_rate,
        equity_curve=equity,
    )
