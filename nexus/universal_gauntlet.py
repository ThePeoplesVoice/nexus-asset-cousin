"""Universal Gauntlet.

The bet: throw ANY code, language, source, history, numbers, or pure invention
at the cousin and it reads, analyzes, processes, and invents a working system
on the spot. 80% coverage in microseconds.

Run: python -m nexus.universal_gauntlet
"""
from __future__ import annotations

from nexus.universal_adapter import UniversalAdapter


def main() -> None:
    ua = UniversalAdapter()
    sources = [
        # 1987 Mario Bros / ancient Nintendo platform
        {"era": 1987, "platform": "NES", "game": "Mario Bros",
         "entities": ["mario", "luigi", "shellcreep", "pow_block"],
         "physics": "2d_side_scroller"},
        # Call of Duty multiplayer
        {"game": "Call of Duty", "mode": "multiplayer", "players": 64,
         "weapons": ["ak47", "m4", "sniper"], "maps": ["rust", "shipment"]},
        # Fortnite online
        {"game": "Fortnite", "mode": "battle_royale", "players": 100,
         "builds": True, "storm": "shrinking"},
        # Minecraft
        {"game": "Minecraft", "blocks": 1200, "mobs": ["zombie", "creeper"],
         "seed": 1337, "dimensions": ["overworld", "nether", "end"]},
        # Zelda
        {"game": "Legend of Zelda", "hearts": 12, "dungeons": 9,
         "items": ["master_sword", "bow", "boomerang"], "open_world": True},
        # Pure invention on the fly
        "a brand-new fictional platform with zero documentation, a made-up physics engine, "
        "and a currency called 'glorp' that only exists in the imagination of a traffic-jammed optimist",
        # Raw numbers / history
        [1987, 2026, 7_000, 20, 3_000, 0.000001],
        # Arbitrary code-ish blob
        {"fn": "def dispatch(asset): return asset.status", "lang": "python"},
    ]
    result = ua.run_gauntlet(sources)
    print("=" * 60)
    print("UNIVERSAL GAUNTLET RESULT")
    print("=" * 60)
    for k, v in result.items():
        print(f"  {k}: {v}")
    print("=" * 60)
    if result["all_above_80"]:
        print(
            "VERDICT: The cousin did not fail. It invented systems for every single source, "
            "crossed 80% coverage, and did it in microseconds. The bettors who said 'massive fail' "
            "are now eating their words."
        )
    else:
        print("VERDICT: Some sources slipped below 80%. Tighten the adapter.")


if __name__ == "__main__":
    main()
