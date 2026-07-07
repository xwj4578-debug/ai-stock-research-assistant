# Research Workspace Part 2

## Scope

Part 2 adds the operational modules after the first workspace shell:

- Hot Sectors: sector heat, leader, trend core, fund flow, short AI summary, and sector detail entry.
- Watchlist: future possible trades, not simple favorites.
- AI Copilot: structured research partner output, not a generic chatbot.
- Module states: loading, empty, error, and independent retry.
- API draft: workspace aggregation, Copilot, chat, and watchlist mutation endpoints.

## Implemented Prototype Behavior

- Hot sector cards are clickable and open a sector detail panel.
- Sector detail shows members, leader ranking, fund flow, news placeholders, and an AI report summary.
- Watchlist cards show score, risk level, latest change summary, next action, and quick actions.
- Empty Watchlist shows a clear entry back to Research Queue.
- AI Copilot has quick actions and structured output: reason, leader, trend core, risk, next watch points.

## API

- `GET /api/workspace`
- `GET /api/workspace/copilot`
- `POST /api/workspace/chat`
- `POST /api/watchlist`
- `DELETE /api/watchlist/{id}`
