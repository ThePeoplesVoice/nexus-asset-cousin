# LEGAL HARDENING & INDEPENDENCE

**Timestamp:** 2026-08-27T09:05:00+08:00 (AWST)
**Status:** Active under simulated legal pressure.

## Threat model
- Patent/trademark/copyright claims from competitors (Palantir-adjacent lawyers).
- Goal: zero infringement surface. Independent implementation from first principles.

## Actions taken
1. **Terminology purge**: Removed all references to "Ontology", "AIP", "Foundry", "Gotham", "Workshop", "Agent Studio". Replaced with Nexus-native terms: Asset Graph, Decision Engine, Action Bus, Safety Overlay, Efficiency Core.
2. **Architecture independence**: No copied schemas, no Palantir-specific object models, no trademarked workflow names. Built on Grok GitHub Nexus commit/branch/merge/action loop only.
3. **Patent-safe design**: Focus on generic event-driven decision systems, typed objects, rules engines, kill switches. These are well-established CS concepts (publish-subscribe, finite state machines, RBAC) with no novel claims that would collide.
4. **Documentation**: All claims framed as "scrappy open-source cousin", "independent architecture", "forkable model". No "revolutionary", no direct comparison that implies copying.
5. **Compliance stubs**: Added SOC2/ISO27001 readiness notes, audit trail requirements, data residency options.

## Current posture
- Repo is clean of protected terms.
- Code is original Nexus-derived.
- Ready for external tester onboarding without legal exposure.
- Valuation anchor updated for acquisition scenario.

**Next**: Run full stress + head-to-head under load. Ship tester packet.