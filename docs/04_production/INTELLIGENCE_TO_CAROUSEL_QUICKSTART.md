# Intelligence to Carousel Quickstart

## Scope

This is a local, deterministic acceptance of the bounded LOOPRA vertical
slice from Content Intelligence through a QA-verified Instagram carousel.
It proves the existing service contracts; it does not introduce a workflow
engine or a second renderer.

## Run the acceptance

From the repository root:

```powershell
python scripts/run_intelligence_to_carousel_acceptance.py --workdir .tmp/intelligence-carousel-acceptance --keep-output --json
```

`--help` is side-effect-free. With no `--workdir`, the runner uses a temporary
directory and removes it after success unless `--keep-output` is passed.

Requirements: the established local Python environment and Pillow. The slice
uses no network access, credentials, LLM, FFmpeg, social API, or external
connector.

## Actual chain

```text
MarketSignal → TrendPattern → ContentOpportunity (approved) → Idea (approved)
→ explicit ScenarioTextBlock input → Scenario (needs_review, then approved)
→ ProductionBrief (validated) → RenderJob → carousel PNG → carousel QA
→ OutputFile records → RenderJob (rendered)
```

The runner uses `ContentIntelligenceService`, `IdeaService`,
`ScenarioService`, `ScenarioToCarouselBriefService`, and
`ProductionPipelineService`. The latter invokes the existing Pillow carousel
renderer and its QA before `OutputFile` records are registered.

## Expected output

The JSON result contains all entity IDs, lifecycle statuses, output records,
PNG dimensions, byte sizes, SHA-256 values, traceability booleans and checks.
The rendered files are under:

```text
<workdir>/storage/intelligence_carousel_acceptance/renders/<render_job_id>/carousel/
```

The fixture produces five 1080x1350 PNGs: a cover plus four explicit content
blocks (`body`, `quote`, `list`, `cta`). The blocks are supplied out of order
and are stored deterministically by `order`; their Cyrillic text is not
generated or rewritten.

## Current limits

- Carousel `ScenarioTextBlock` values are explicit planning input; there is no
  automatic text or AI generation.
- Trend Radar is not integrated; the MarketSignal is a local fixture.
- Opportunity, Idea and Scenario approval remain explicit actions.
- Only Instagram carousel is supported by this handoff.
- No publishing, analytics collection, Learning Memory, runtime agent, or
  orchestrator is implemented.
