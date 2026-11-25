# Design direction — Project 05 · Northeast Brazil Green Data Centre Site Selection

## Series identity
Project 05 of the Daniel Santos Infrastructure Analytics Series. Projects 01–04 establish the energy-system analysis language; Project 05 applies the same evidence-first discipline to a site-selection workflow.

## Audience
Recruiters, data-centre/infrastructure professionals, energy analysts and technically curious readers. The interface supports:
1. a two-minute executive scan;
2. interactive exploration of scenarios and candidates;
3. a detailed methodology / source review.

## Single job
Show where public evidence justifies deeper data-centre diligence in Northeast Brazil — without implying that municipality-level screening proves utility headroom, industrial water, route-diverse fibre or parcel feasibility.

## Visual system
- Background: `#06111A`
- Surface: `#0A1722`
- Elevated surface: `#0E2030`
- Text: `#F1F7FB`
- Muted: `#97AABD`
- Screening / pass accent: `#4FE0B5`
- Infrastructure / map accent: `#66BFFF`
- Conditional / unresolved: `#F2B85D`
- Risk: `#EF7569`
- Rule: `#213748`

## Signature
The memorable element is the **site dossier**: each priority municipality reads like an infrastructure-screening file rather than a generic card. Dossiers combine core evidence, climate-risk signals, public infrastructure context and unresolved external gates.

The hero uses a **decision funnel** (1,794 → 190 → 11 → 5) because those numbers encode the real analytical process rather than decoration.

## Information architecture
Overview → Five site dossiers → Scenario map → Tier-A robustness → Evidence → Method → Sources → Series navigation.

Detailed material remains available, but the page reveals complexity progressively instead of front-loading every methodology detail.

## Interaction contract
- Core conclusions remain readable without interacting with the map.
- Site dossier tabs are keyboard-operable buttons.
- “Show on map” links the selected dossier to its geography.
- Risk bars use text values and labels; color is never the only signal.
- Map rankings remain scenario-specific and do not overwrite the Step-16 diligence queue.
- Motion is minimal and respects `prefers-reduced-motion`.
- Mobile reading order prioritizes decision context before charts/tables.

## Guardrails
The UI must never visually imply:
- transmission proximity = available MW;
- Q95 = water permission or firm industrial supply;
- provider count = route diversity;
- municipality CNUC screen = parcel legality;
- a five-site diligence queue = investment approval.
