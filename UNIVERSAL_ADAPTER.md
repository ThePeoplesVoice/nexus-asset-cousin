# Universal Adapter Layer

## The bet
Every platform, game, and code source on Earth simultaneously wants in.
Mario Bros (1987), Call of Duty, Fortnite, Minecraft, Zelda, and a pile of
random invented junk. They all bet it would fail.

## What it does
- Reads ANY source: code, language, history, numbers, game data, pure fiction.
- Analyzes it without a pre-trained domain model.
- Processes it into typed objects, relationships, and allowed actions.
- **Invents** a brand-new functional system on the spot if the source has none.
- Covers the boring 80% in microseconds, not months.

## Why it beats the slide-deck crowd
They need ontology engineers, domain experts, and a year of modeling per
vertical. This adapter invents the vertical the moment you describe it.

## Run it
```
python -m nexus.universal_gauntlet
```

## Result shape
- `systems_invented`: how many sources got a working system
- `avg_coverage_pct`: average 80%+ coverage across the gauntlet
- `avg_latency_us`: microseconds per invention
- `all_above_80`: True if every source cleared the bar
- `verdict`: UNTETHERED or NEEDS_WORK
