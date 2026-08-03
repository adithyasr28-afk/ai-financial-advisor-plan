
## Hallucination Rate
- **Samples**: 20
- **Average Hallucination Rate**: 5.77%
- **Details**:
  - Query: `latest news for Apple` | Agents: ['news_intelligence'] | Evidence: 5 | Valid: 5 | Rate: 0.00%
  - Query: `AAPL comprehensive report` | Agents: ['news_intelligence', 'financial_statement', 'valuation', 'risk', 'technical_analysis', 'portfolio', 'macro_economy', 'report_writer'] | Evidence: 26 | Valid: 24 | Rate: 7.69%
  - Query: `Apple revenue 2025` | Agents: ['financial_statement'] | Evidence: 3 | Valid: 3 | Rate: 0.00%
  - Query: `IBM valuation` | Agents: ['valuation'] | Evidence: 1 | Valid: 1 | Rate: 0.00%
  - Query: `portfolio risk assessment` | Agents: ['risk', 'portfolio'] | Evidence: 2 | Valid: 1 | Rate: 50.00%
  - Query: `AAPL technical analysis trend` | Agents: ['technical_analysis'] | Evidence: 1 | Valid: 1 | Rate: 0.00%
  - Query: `my portfolio holdings` | Agents: ['portfolio'] | Evidence: 1 | Valid: 1 | Rate: 0.00%
  - Query: `current GDP macro economy` | Agents: ['macro_economy'] | Evidence: 1 | Valid: 1 | Rate: 0.00%
  - Query: `Apple stock news` | Agents: ['news_intelligence'] | Evidence: 5 | Valid: 5 | Rate: 0.00%
  - Query: `financial statement analysis` | Agents: ['financial_statement'] | Evidence: 3 | Valid: 3 | Rate: 0.00%
  - Query: `latest news for Apple` | Agents: ['news_intelligence'] | Evidence: 5 | Valid: 5 | Rate: 0.00%
  - Query: `AAPL comprehensive report` | Agents: ['news_intelligence', 'financial_statement', 'valuation', 'risk', 'technical_analysis', 'portfolio', 'macro_economy', 'report_writer'] | Evidence: 26 | Valid: 24 | Rate: 7.69%
  - Query: `Apple revenue 2025` | Agents: ['financial_statement'] | Evidence: 3 | Valid: 3 | Rate: 0.00%
  - Query: `IBM valuation` | Agents: ['valuation'] | Evidence: 1 | Valid: 1 | Rate: 0.00%
  - Query: `portfolio risk assessment` | Agents: ['risk', 'portfolio'] | Evidence: 2 | Valid: 1 | Rate: 50.00%
  - Query: `AAPL technical analysis trend` | Agents: ['technical_analysis'] | Evidence: 1 | Valid: 1 | Rate: 0.00%
  - Query: `my portfolio holdings` | Agents: ['portfolio'] | Evidence: 1 | Valid: 1 | Rate: 0.00%
  - Query: `current GDP macro economy` | Agents: ['macro_economy'] | Evidence: 1 | Valid: 1 | Rate: 0.00%
  - Query: `Apple stock news` | Agents: ['news_intelligence'] | Evidence: 5 | Valid: 5 | Rate: 0.00%
  - Query: `financial statement analysis` | Agents: ['financial_statement'] | Evidence: 3 | Valid: 3 | Rate: 0.00%

## Retrieval Precision@k
- **Top-K**: 3
- **Samples**: 5
- **Average Precision@3**: 100.00%
- **Details**:
  - Query: `Apple net sales 2025` | Expected: apple_2025_10k.htm | Retrieved: ['apple_2025_10k.htm', 'apple_2025_10k.htm', 'apple_2025_10k.htm'] | hit
  - Query: `Apple revenue 2024` | Expected: apple_2024_10k.htm | Retrieved: ['apple_2024_10k.htm', 'apple_2024_10k.htm', 'apple_2023_10k.htm'] | hit
  - Query: `Apple cash flow 2023` | Expected: apple_2023_10k.htm | Retrieved: ['apple_2023_10k.htm', 'apple_2023_10k.htm', 'apple_2023_10k.htm'] | hit
  - Query: `Apple total assets` | Expected: apple_2025_10k.htm | Retrieved: ['apple_2025_10k.htm', 'apple_2024_10k.htm', 'apple_2023_10k.htm'] | hit
  - Query: `Apple research and development expenses` | Expected: apple_2025_10k.htm | Retrieved: ['apple_2023_10k.htm', 'apple_2023_10k.htm', 'apple_2025_10k.htm'] | hit

## Latency
- **Runs**: 10
- **Mean**: 30.76 ms
- **Median**: 15.66 ms
- **Std Dev**: 46.8 ms
- **Min**: 0.66 ms
- **Max**: 153.48 ms

## Token Cost (Estimated)
- **Model**: gpt-4o-mini (estimated)
- **Pricing**: Input $0.15/1M, Output $0.6/1M
- **Samples**: 5
- **Average Tokens**: 1550
- **Average Cost**: $0.000929
- **Details**:
  - Query: `latest news for Apple` | Agents: 1 | Tokens: 912 (in:4/out:908) | Cost: $0.000545
  - Query: `AAPL comprehensive report` | Agents: 8 | Tokens: 5242 (in:4/out:5238) | Cost: $0.003143
  - Query: `Apple revenue 2025` | Agents: 1 | Tokens: 738 (in:5/out:733) | Cost: $0.000441
  - Query: `IBM valuation` | Agents: 1 | Tokens: 262 (in:2/out:260) | Cost: $0.000156
  - Query: `portfolio risk assessment` | Agents: 2 | Tokens: 598 (in:3/out:595) | Cost: $0.000357

## Forecast Accuracy
- **Status**: insufficient_data
- **Message**: Not enough data points for window

## Agent Agreement
- **Queries Tested**: 10
- **With Stances**: 7
- **Agreements**: 5
- **Disagreements**: 2
- **Agreement Rate**: 71.4%
- **Stance Distribution**: {"bullish": 2, "neutral": 2, "hold": 3, "uptrend": 2, "insufficient_data": 3, "conflict": 1}
- **Details**:
  - Query: `latest news for Apple` | Stances: [<Stance.BULLISH: 'bullish'>] | agree
  - Query: `AAPL comprehensive report` | Stances: [<Stance.BULLISH: 'bullish'>, <Stance.NEUTRAL: 'neutral'>, <Stance.HOLD: 'hold'>, <Stance.UPTREND: 'uptrend'>, <Stance.INSUFFICIENT_DATA: 'insufficient_data'>, <Stance.CONFLICT: 'conflict'>] | disagree
  - Query: `Apple revenue 2025` | Stances: [] | no_stance
  - Query: `IBM valuation` | Stances: [<Stance.NEUTRAL: 'neutral'>] | agree
  - Query: `portfolio risk assessment` | Stances: [<Stance.HOLD: 'hold'>, <Stance.INSUFFICIENT_DATA: 'insufficient_data'>] | disagree
  - Query: `AAPL technical analysis trend` | Stances: [<Stance.UPTREND: 'uptrend'>] | agree
  - Query: `my portfolio holdings` | Stances: [<Stance.INSUFFICIENT_DATA: 'insufficient_data'>] | agree
  - Query: `current GDP macro economy` | Stances: [] | no_stance
  - Query: `tech sector outlook` | Stances: [] | no_stance
  - Query: `market risk today` | Stances: [<Stance.HOLD: 'hold'>] | agree
