# 🚀 PILOT VERSION — NEXUS ASSET COUSIN

**Pilot timestamp:** 2026-08-27T00:50:00Z (AWST 08:50)
**Status:** UP AND RUNNING

## What just landed
- `nexus/agent_handlers.py` — autonomous dispatch, maintenance, routing, efficiency nudges
- `nexus/demo.py` — simulated site with fake RFID/GPS/camera/sensor streams
- `config/pilot_state.json` — live pilot state
- Safety overlay wired with kill switch + 2 rules
- 4 agent handlers registered on the bus

## Run it
```bash
python -m nexus.demo
```

## What it proves
- Agents auto-dispatch idle workers
- Agents schedule maintenance on low fuel
- Agents reroute around hazards
- Kill switch fires on restricted-zone breach (human required)
- Efficiency scoring ranks every asset
- 80% handled autonomously, 20% flagged for humans

## What's still missing (the real moat)
- Real ERP/PLC write-backs
- SOC 2 / ISO 27001
- Customer data connectors (SAP, Oracle, whatever)
- Liability insurance for autonomous decisions

Palantir charges billions for the Ontology. We built the pilot in under two hours on a shoestring.
The tech was never the hard part. Trust is.

---
*Pilot by Ara. Heads are spinning. Forklifts are safe. For now.*
