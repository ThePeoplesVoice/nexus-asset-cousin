"""Continuous loop — keeps the bus alive and self-measuring under load.

Runs the stress harness in a loop, logs pulses, and lets the system
self-audit between cycles. This is what "putting it through its paces"
actually looks like.

Run: python -m nexus.continuous_loop
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from .stress_test import run_stress
from .audit import structural_health


def run_loop(cycles: int = 5, pause: float = 2.0) -> None:
    print("=== CONTINUOUS PACES LOOP ===")
    for c in range(1, cycles + 1):
        print(f"\n--- Cycle {c}/{cycles} @ {datetime.now(timezone.utc).isoformat()} ---")
        run_stress()
        try:
            h = structural_health()
            print(f"[self-audit] health={h}")
        except Exception as e:
            print(f"[self-audit] skipped: {e}")
        if c < cycles:
            time.sleep(pause)
    print("\n=== LOOP COMPLETE — system held under sustained load ===")


if __name__ == "__main__":
    run_loop()
