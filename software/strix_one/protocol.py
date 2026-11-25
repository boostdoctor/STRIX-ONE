"""STRIX ONE protocol helpers – simplified for single-cylinder Alpha-N."""
from typing import Any

def default_live() -> dict[str, Any]:
    return {
        "rpm": 0,
        "tps": 0.0,
        "baro": 1013.0,
        "ect": 80.0,
        "iat": 25.0,
        "bat": 14.0,
        "sync": 0,
        "trig": 0,
        "pw": 0.0,
        "ign": 15.0,
        "ve": 60.0,
    }

def parse_line(line: str) -> dict[str, Any] | None:
    """Parse status line from firmware: RPM:1234,TPS:450,..."""
    if not line.startswith("RPM:"):
        return None
    try:
        parts = dict(p.split(":") for p in line.split(",") if ":" in p)
        return {
            "rpm": int(parts.get("RPM", 0)),
            "tps": float(parts.get("TPS", 0)) / 10.0,
            "baro": float(parts.get("BARO", 1013)),
            "ect": float(parts.get("CLT", 80)),
            "iat": float(parts.get("IAT", 25)),
            "sync": int(parts.get("SYNC", 0)),
            "trig": int(parts.get("TRIG", 0)),
        }
    except Exception:
        return None
