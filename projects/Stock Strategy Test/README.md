# Stock & Options Strategy Lab

A private, beginner-friendly app for testing shares and options together on one page. Search for a U.S. stock or ETF, then add its **Shares**, **Long call**, **Protective put**, or **Cash-secured short put** as a separate allocation row. The same ticker can be used in more than one way, each with its own percentage. A cash allocation and one-click balancing controls make it easy to bring the portfolio to exactly 100%. Results are compared with investing the same starting money entirely in SPY and QQQ.

The app is an educational simulator, not investment advice. Historical results do not predict future performance.

## What the app does

- Searches valid U.S. stock and ETF names instead of accepting arbitrary ticker text.
- Adds a search result as shares, a long call, a protective put, or a cash-secured short put without changing pages.
- Tests one or more holdings and instruments over a chosen date range.
- Keeps every entered allocation fixed while the user edits other holdings, with visible under/over-allocation guidance.
- Can proportionally normalize the current mix to exactly 100% or put only the unallocated remainder into cash.
- Models an optional cash allocation that earns no interest.
- Supports buy-and-hold, monthly, quarterly, and annual rebalancing.
- Shows the strategy, SPY, and QQQ on one chart from the same starting value.
- Reports ending value, total return, annualized return, and maximum temporary loss.
- Includes deterministic demo prices so the complete workflow works without an account.
- Makes **Free automatic** the default: real share history plus an exact-first SPY/QQQ option hierarchy with no paid option-data plan required.
- Uses retained historical closing bid/ask first, a locally calibrated surface second, and clearly labeled extrapolation for older periods. Every result reports the percentage from each source.
- Prevents look-ahead by using only share returns, Cboe volatility observations, Treasury rates, and dividends dated on or before each simulated day.
- Derives the model-sensitivity band from locally measured model-versus-quote residuals instead of presenting one estimate as certain.
- Uses beginner-friendly call and put duration controls, with liquidity rules in an Advanced section.
- Keeps Tiingo Starter price rows in memory only during a run. A user-owned CSV can be imported for durable local reuse; exact Market Data records remain in their licensed vault.
- Offers 5-, 10-, and 15-year shortcuts for free Tiingo share history.
- Can combine multiple verified-beta option sleeves selected and priced locally from Market Data historical chains and quotes.
- Runs independent provider reads concurrently and keeps long tests in a polled background job instead of holding one browser request open.

The interface is intentionally chart-first: all strategy and data controls occupy the left rail while the performance comparison occupies the larger right side. There is no separate options page.

## Adding shares or options

Open `http://127.0.0.1:8790`, type a company name or ticker in **Search stocks & ETFs**, and choose the desired position on the matching result. For example, SPY shares, SPY calls, SPY protective puts, and QQQ calls can coexist as independently weighted rows. Every option row has its own expandable expiration, replacement, and strike controls. The guided defaults target approximately 540-day calls and 45-day protective puts.

Demo mode needs no account. Free automatic mode needs either a free Tiingo token or complete daily CSV files owned by the user, and models options locally. Exact recent mode uses Tiingo for share history and Market Data for historical option chains and individual contract quotes. It requests only the option contracts needed by the strategy and reuses locally cached exact-option data.

Market Data's free/trial access currently supports 24-hour-delayed option data and one year of history. The page shows the most recently reported credit balance before a real test begins. Missing contracts, illiquid quotes, and degraded valuations remain visible in the result.

Robinhood is not used as an application data source. Its official Trading MCP has current equity and option tools, but the same connection also exposes order tools and does not advertise historical option-price tools. The app therefore does not request brokerage access for a data-only research task.

## Run locally

Python 3.11+ is recommended.

```bash
cd "projects/Stock Strategy Test"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py --host 127.0.0.1 --port 8790
```

Open `http://127.0.0.1:8790`.

Run checks:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
.venv/bin/python -m py_compile app.py stock_strategy_lab/*.py
node --check static/app.js
```

## Free real data with Tiingo

Tiingo's free personal plan currently advertises more than 50 years of end-of-day history, 50 requests per hour, and 1,000 requests per day for internal use.

1. Create a free Tiingo account and copy the API token from its token page.
2. Leave **Price source** on the default **Free automatic**.
3. Expand **Free share-data settings**, paste the token, and click **Save token**.
4. Search for holdings, add shares or options, and run the test. A Market Data token is optional; without one, option values are explicitly labeled unvalidated estimates.

The token is saved in the ignored local `data/tiingo_token` file with owner-only permissions. The browser can see only whether a token is configured, never the token itself. Tiingo price responses are held only in process memory and cleared when the run ends; they are not written into the vault or a saved run. A summary-only result is retained, and rerunning reconstructs its chart.

To keep reusable history that you are entitled to retain, open the same panel and import a daily CSV for each required symbol. The importer accepts `Date`, `Close`, and `Adjusted Close`; `Dividends` and `Stock Splits` improve option modeling. SPY and QQQ are always required because they are the benchmarks.

Tiingo is used instead of Yahoo Finance because Yahoo does not provide a supported public historical-price API for this app. Yahoo's website still provides manual CSV downloads, but its unofficial chart endpoint can throttle automated requests.

## Verified beta options

The **Verified beta options** source is an independent-sleeve model calculated entirely inside this app. Tiingo supplies adjusted share prices and benchmarks. Market Data supplies the historical option chain used to select each contract and the exact bid/ask history used to price it on every held trading session.

1. Connect both Tiingo and Market Data.
2. Choose dates inside the verified Market Data window or previously retained local quote coverage.
3. Add one or more positive **Call** or **Put** rows. They may use different tickers.
4. Add any desired share rows and cash, then make the total 100%.
5. Expand **Expiration, roll & strike** under each option row to give that position its own settings.
6. Choose **Verified beta options**. The app switches portfolio rebalancing to buy-and-hold; every option still rolls at its own selected threshold.
7. Run the comparison. Independent option rows run concurrently and are combined with shares and cash into one strategy line.

Every option row receives its requested percentage of starting money and is calculated as an independent sleeve. Money does not move between sleeves after the start, although option replacement still occurs inside each sleeve. No OnclickMedia schedule, option price, or portfolio total is used. The app applies the selected expiration, roll, strike, delta, open-interest, monthly-expiration, and spread rules directly to Market Data chains. It rejects a missing contract history or a missing required daily bid/ask instead of carrying or inventing a price. Purchases use the ask, daily values and sales use the bid, contracts are whole lots, and the locally calculated cash balance is authoritative.

ATM, percentage, fixed-dollar, and delta strike rules use the same audited local selector as the regular Real Historical Prices engine. Each chain snapshot and contract series receives a SHA-256 audit checksum in the result. Verified coverage grows as exact Market Data chain and contract histories are retained locally. A date outside both the provider window and retained coverage is refused rather than approximated.

## Modeling assumptions

- Uses adjusted closes for share and benchmark total returns, while using raw contemporaneous closes for option strikes and intrinsic value.
- Fractional shares are allowed. Share trades have no taxes or commissions in v1.
- A rebalance restores the target weights at that day's adjusted close.
- Free automatic checks the local vault for exact SPY/QQQ closing bid/ask first. Within the provider's rolling window it may save only a missing selected chain/contract while preserving the 30-credit reserve. Older gaps use a calibrated or explicitly uncalibrated model; no substitution is silent.
- The calibrated model fits SPY and QQQ independently with constrained eSSVI total variance, put/call forward inference, historical Cboe VIX/VXN observations, U.S. Treasury rates, trailing cash dividends, and evidence-based bid/ask behavior.
- Deep in-the-money contracts use an adaptive 128–1,024-step American lattice with convergence testing. Other daily marks use the faster continuation value with the same intrinsic and no-arbitrage bounds. A genuinely worthless option may have a zero bid.
- The result includes lower/higher reruns based on the locally measured model-versus-quote residual. This is a sensitivity range, not a statistical confidence interval.
- Options use whole contracts. Long options are bought at ask and sold or valued at bid. Cash-secured short puts open at bid, close or are valued at ask, and reserve `strike × contract multiplier` as collateral.
- A long option can be liquidated at the better of its historical bid or realizable exercise value after share slippage. Deep in-the-money short puts also receive rational-assignment and unassigned comparisons when the paths differ.
- Every option leg rolls independently. A 45-day put roll can restore portfolio targets without replacing a still-valid 540-day call.
- The default Robinhood stock/ETF option fee estimate is $0.04 per contract per side; minor sell-only SEC and FINRA fees are not modeled.
- Long options can lose their entire premium. Cash-secured short puts can lose much of their reserved collateral.
- A missing option leg receives one independent retry after five trading sessions. Other positions remain untouched, and a still-missing allocation stays in cash until the next scheduled rebalance.
- Historical chain membership is cached separately from each selected contract's quote history, so repeated runs select the same contracts without additional provider calls.
- The comparison begins on the first trading date with a usable price for every holding, SPY, and QQQ.
- A symbol is added only after the user chooses a provider search result.

## Local data boundary

Runtime state defaults to the ignored `data/` directory. Tokens, imported user-owned prices, official Cboe/Treasury reference files, licensed Market Data records, saved state, and logs stay on this computer and must not be committed. Tiingo Starter rows are transient and never stored in that vault.

## Improve option accuracy

The subtle **Improve option accuracy** panel is beside the data settings. It is limited to SPY/QQQ, strikes from 50%–150% of spot, 365–730-day calls, and 30–60-day puts.

- **Save next calibration batch** collects the oldest missing weekly SPY/QQQ anchor first, in expiration-sized requests. It never starts another request once the reported balance reaches the 30-credit reserve.
- **Check measured accuracy** runs the held-out grid: both symbols; long calls, long puts, and cash-secured short puts; five strike buckets; three expiration buckets; plus the default mixed portfolio.
- **Validated within 1%** appears only if every evidence cell is present, every runnable held-out portfolio finishes within 1% of exact closing bid/ask, and assignment uncertainty stays within 1%.
- A period older than the retained calibration library is labeled **Extrapolated historical estimate**. The app never treats five or ten years of modeled history as reconstructed historical option quotes.
