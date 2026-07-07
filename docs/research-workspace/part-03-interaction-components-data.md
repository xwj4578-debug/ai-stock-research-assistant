# Research Workspace Part 3

## Interaction Flow

The intended daily path is:

1. Open Workspace.
2. Read Market Pulse.
3. Read AI Daily Brief.
4. Pick a Hot Sector.
5. Inspect sector detail.
6. Open a target stock report.
7. Add it to Watchlist.
8. Track changes.
9. Trigger buy-point review or abandon research.

Every module must answer: what should the user do next?

## Component Notes

- Market Pulse supports refresh and links into deeper market review.
- Research Queue is ranked by risk, buy-point signal, sector heat, and user preference.
- Queue cards support analyze, add to Watchlist, mark complete, and remove.
- Watchlist cards support pin, delete, reminder, completion, and report entry.
- AI Copilot keeps current sector and current stock context available for prompts.

## Data Draft

Tables planned for a persistent implementation:

- `workspace_snapshot`
- `research_queue`
- `watchlist`

The prototype uses live aggregation plus local browser storage for Watchlist actions.

## Prompt Draft

Workspace summary prompt output:

1. Market summary.
2. Hot sectors.
3. Risks.
4. Research suggestion.
5. Next research tasks.

Constraints: under 300 Chinese characters, no direct buy/sell recommendation, fact-based explanation.
