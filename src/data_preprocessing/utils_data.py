from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional
import math

DEFAULT_COLMAP = {
    "rv_id": "rv_id",
    "hv_id": "hv_id",
    "msg_rcv_time": "msg_rcv_time",
    "hv_pos_x": "hv_pos_x",
    "hv_pos_y": "hv_pos_y",
    "hv_speed": "hv_speed",
    "hv_heading": "hv_heading",
    "rv_pos_x": "rv_pos_x",
    "rv_pos_y": "rv_pos_y",
    "rv_speed": "rv_speed",
    "rv_heading": "rv_heading",
    "target_id": "target_id",
    "eebl_warn": "eebl_warn",
    "ima_warn": "ima_warn",
    "attack_type": "attack_type",
}

def _safe_get(row: Any, key: str, default: Any = None) -> Any:
    try:
        v = row[key]
        # Convert numpy scalars to python
        try:
            import numpy as np
            if isinstance(v, (np.generic,)):
                return v.item()
        except Exception:
            pass
        return v
    except Exception:
        return default

def row_to_text(row: Any, colmap: Dict[str, str] = DEFAULT_COLMAP) -> str:
    """Convert one MisbehaviorX row into a natural-language prompt input.

    This matches the style used in the project report and the prompt templates.
    If a column is missing, the field will fall back to '?'.
    """
    def g(name: str, default: Any = "?") -> Any:
        return _safe_get(row, colmap.get(name, name), default)

    # numeric formatting with fallbacks
    def fnum(x: Any, fmt: str) -> str:
        try:
            if x is None:
                return "?"
            if isinstance(x, str) and x.strip() == "":
                return "?"
            return format(float(x), fmt)
        except Exception:
            return "?"

    return (
        f"Receiver vehicle {g('rv_id')} received a message from vehicle {g('hv_id')} "
        f"at time {fnum(g('msg_rcv_time'), '.3f')} s.\n"
        f"Sender (hv) position: ({fnum(g('hv_pos_x'), '.1f')}, {fnum(g('hv_pos_y'), '.1f')}), "
        f"speed: {fnum(g('hv_speed'), '.1f')} m/s, heading: {fnum(g('hv_heading'), '.1f')} deg.\n"
        f"Receiver (rv) position: ({fnum(g('rv_pos_x'), '.1f')}, {fnum(g('rv_pos_y'), '.1f')}), "
        f"speed: {fnum(g('rv_speed'), '.1f')} m/s, heading: {fnum(g('rv_heading'), '.1f')} deg.\n"
        f"Target id: {g('target_id')}, EEBL warning: {g('eebl_warn')}, IMA warning: {g('ima_warn')}."
    )

def label_from_attack_type(attack_type: Optional[str]) -> str:
    """Binary label used in this project: attacker vs genuine."""
    if attack_type is None:
        return "unknown"
    at = str(attack_type).strip().lower()
    if at == "genuine":
        return "genuine"
    # everything else treated as attacker (as in the report's binary setting)
    return "attacker"
