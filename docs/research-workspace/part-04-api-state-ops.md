# Research Workspace Part 4

## API Contract

Primary aggregation endpoint:

```http
GET /api/v1/workspace
GET /api/v1/workspace?module=hotSectors
```

Response includes:

- `marketPulse`
- `dailyBrief`
- `researchQueue`
- `hotSectors`
- `watchlist`
- `riskAlerts`
- `moduleStates`
- `requestId`

Watchlist:

```http
GET /api/v1/watchlist?page=1&page_size=20&q=&risk=&sort=score
POST /api/v1/watchlist
DELETE /api/v1/watchlist/{id}
```

Queue:

```http
POST /api/v1/research-queue/{id}/{action}
```

Telemetry:

```http
POST /api/v1/telemetry
```

## State Machine

Workspace states:

- `Loading`
- `Ready`
- `Refreshing`
- `Empty`
- `Error`
- `Retry`

Each module keeps its own state so one failed refresh does not wipe the page.

## Error Recovery

- Network timeout: show retry.
- AI failure: keep the last successful non-AI modules.
- Empty data: show empty state.
- Auth failure in future versions: redirect to login.

## Performance Targets

- First load under 2 seconds when cache is warm.
- Module refresh under 300 ms when cache is warm.
- AI summary under 5 seconds.
- Watchlist design should support 1000+ stocks.

## Security Rules

- Future production APIs should use JWT, HTTPS, authorization checks, and operation logs.
- AI output must not promise returns, invent facts, or issue direct buy/sell instructions.
