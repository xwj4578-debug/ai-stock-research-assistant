from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def _secid(code: str) -> str | None:
    if not code.isdigit() or len(code) != 6:
        return None
    market = "1" if code.startswith(("6", "9")) else "0"
    return f"{market}.{code}"


def _sina_symbol(code: str) -> str | None:
    if not code.isdigit() or len(code) != 6:
        return None
    market = "sh" if code.startswith(("6", "9")) else "sz"
    return f"{market}{code}"


def _scaled(value: Any, scale: float = 100) -> float | None:
    if value in (None, "-", ""):
        return None
    try:
        return round(float(value) / scale, 2)
    except (TypeError, ValueError):
        return None


def _market_cap_yi(value: Any) -> float | None:
    if value in (None, "-", ""):
        return None
    try:
        return round(float(value) / 100_000_000, 1)
    except (TypeError, ValueError):
        return None


def _get_json(url: str, timeout: float) -> dict[str, Any] | None:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*",
            "Referer": "https://quote.eastmoney.com/",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        pass

    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        return None
    try:
        completed = subprocess.run(
            [
                curl,
                "-L",
                "-s",
                "--max-time",
                str(max(2, int(timeout))),
                "-H",
                "User-Agent: Mozilla/5.0",
                "-H",
                "Referer: https://quote.eastmoney.com/",
                url,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout + 1,
        )
        if completed.stdout.strip():
            return json.loads(completed.stdout)
    except Exception:
        return None
    return None


def _fetch_sina_quote(code: str, timeout: float) -> dict[str, Any] | None:
    symbol = _sina_symbol(code)
    if not symbol:
        return None
    request = Request(
        f"https://hq.sinajs.cn/list={symbol}",
        headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            text = response.read().decode("gbk", errors="ignore")
    except Exception:
        return None
    if '="' not in text:
        return None
    body = text.split('="', 1)[1].rsplit('"', 1)[0]
    parts = body.split(",")
    if len(parts) < 32 or not parts[0]:
        return None
    prev_close = _scaled(parts[2], 1)
    current = _scaled(parts[3], 1)
    if not current:
        current = _scaled(parts[1], 1)
    change_pct = round((current / prev_close - 1) * 100, 2) if current is not None and prev_close else None
    updated_at = f"{parts[30]} {parts[31]}" if len(parts) > 31 and parts[30] and parts[31] else datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "code": code,
        "name": parts[0],
        "price": current,
        "market_cap": None,
        "pe": None,
        "pb": None,
        "change_pct": change_pct,
        "source": "新浪财经公开行情接口",
        "updated_at": updated_at,
    }


def fetch_live_quote(code: str, timeout: float = 5) -> dict[str, Any] | None:
    secid = _secid(code)
    if not secid:
        return None

    params = urlencode(
        {
            "secid": secid,
            "fields": "f43,f57,f58,f116,f162,f167,f170",
        }
    )
    payload = _get_json(f"https://push2.eastmoney.com/api/qt/stock/get?{params}", timeout=timeout)
    if not payload:
        return _fetch_sina_quote(code, timeout)

    data = payload.get("data")
    if not data:
        return None

    quote = {
        "code": data.get("f57") or code,
        "name": data.get("f58"),
        "price": _scaled(data.get("f43")),
        "market_cap": _market_cap_yi(data.get("f116")),
        "pe": _scaled(data.get("f162")),
        "pb": _scaled(data.get("f167")),
        "change_pct": _scaled(data.get("f170")),
        "source": "东方财富公开行情接口",
        "updated_at": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"),
    }
    if all(quote[key] is None for key in ("price", "market_cap", "pe", "pb", "change_pct")):
        return _fetch_sina_quote(code, timeout)
    return quote
