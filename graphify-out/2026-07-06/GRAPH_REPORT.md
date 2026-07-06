# Graph Report - C:\git\content-plant  (2026-07-06)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 454 nodes · 1419 edges · 35 communities (23 shown, 12 thin omitted)
- Extraction: 63% EXTRACTED · 37% INFERRED · 0% AMBIGUOUS · INFERRED: 520 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f05c4e5d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Brand Configuration Loader|Brand Configuration Loader]]
- [[_COMMUNITY_Status Enum Definitions|Status Enum Definitions]]
- [[_COMMUNITY_TikTok Video Collector|TikTok Video Collector]]
- [[_COMMUNITY_Carousel Slide Assembly|Carousel Slide Assembly]]
- [[_COMMUNITY_Video Pipeline Assembly|Video Pipeline Assembly]]
- [[_COMMUNITY_System Module Names|System Module Names]]
- [[_COMMUNITY_Report Generation Utilities|Report Generation Utilities]]
- [[_COMMUNITY_Social Media Post Types|Social Media Post Types]]
- [[_COMMUNITY_Video Data Parser|Video Data Parser]]
- [[_COMMUNITY_Status Transition Utilities|Status Transition Utilities]]
- [[_COMMUNITY_Status Transition Tests|Status Transition Tests]]
- [[_COMMUNITY_TikTok Viral Screening Config|TikTok Viral Screening Config]]
- [[_COMMUNITY_System Specification Docs|System Specification Docs]]
- [[_COMMUNITY_Package Configuration|Package Configuration]]
- [[_COMMUNITY_Asset Validation Module|Asset Validation Module]]
- [[_COMMUNITY_Documentation Index and Specs|Documentation Index and Specs]]
- [[_COMMUNITY_Content Package Builder|Content Package Builder]]
- [[_COMMUNITY_Hyperframes JSON Schema|Hyperframes JSON Schema]]
- [[_COMMUNITY_Opencode Plugin Config|Opencode Plugin Config]]
- [[_COMMUNITY_Opencode Plugin Dependencies|Opencode Plugin Dependencies]]
- [[_COMMUNITY_Service Layer Tests|Service Layer Tests]]
- [[_COMMUNITY_Content Plant Tests|Content Plant Tests]]
- [[_COMMUNITY_SaaS Vision Document|SaaS Vision Document]]
- [[_COMMUNITY_Nura Lens Composition|Nura Lens Composition]]
- [[_COMMUNITY_Hyperframes Scripts Reqs|Hyperframes Scripts Reqs]]
- [[_COMMUNITY_Trend Radar Requirements|Trend Radar Requirements]]
- [[_COMMUNITY_Brief Parser Prompt|Brief Parser Prompt]]
- [[_COMMUNITY_Video Scenario Prompt|Video Scenario Prompt]]
- [[_COMMUNITY_Video Assembler Requirements|Video Assembler Requirements]]

## God Nodes (most connected - your core abstractions)
1. `BaseModel` - 41 edges
2. `ContentItemStatus` - 37 edges
3. `PublicationStatus` - 37 edges
4. `RenderJobStatus` - 36 edges
5. `IdeaStatus` - 36 edges
6. `ScenarioStatus` - 36 edges
7. `ExportPackageStatus` - 36 edges
8. `MetricSnapshotStatus` - 36 edges
9. `ProjectStatus` - 33 edges
10. `BrandProfileStatus` - 33 edges

## Surprising Connections (you probably didn't know these)
- `CarouselSlideBrief` --inherits--> `BaseModel`  [EXTRACTED]
  video-assembler/src/schemas/brief.py → core/domain/models.py
- `ContentBrief` --inherits--> `BaseModel`  [EXTRACTED]
  video-assembler/src/schemas/brief.py → core/domain/models.py
- `SceneBrief` --inherits--> `BaseModel`  [EXTRACTED]
  video-assembler/src/schemas/brief.py → core/domain/models.py
- `StockInsertion` --inherits--> `BaseModel`  [EXTRACTED]
  video-assembler/src/schemas/brief.py → core/domain/models.py
- `BrandConfig` --inherits--> `BaseModel`  [EXTRACTED]
  video-assembler/src/schemas/carousel.py → core/domain/models.py

## Import Cycles
- 1-file cycle: `core/domain/models.py -> core/domain/models.py`
- 1-file cycle: `core/domain/transitions.py -> core/domain/transitions.py`
- 2-file cycle: `core/domain/enums.py -> core/domain/transitions.py -> core/domain/enums.py`

## Hyperedges (group relationships)
- **Brand Profile Usage in Platform Modules** — docs_brand_system_spec_brand_profile, docs_brand_system_spec_scenario_studio, docs_brand_system_spec_visual_prompt_generation, docs_brand_system_spec_production_engine, docs_brand_system_spec_publishing_hub, docs_brand_system_spec_qa_and_review, docs_brand_system_spec_analytics [EXTRACTED 1.00]
- **Core Content Formats** — docs_content_formats_overview_dialog_miniseries, docs_content_formats_overview_atmospheric_video, docs_content_formats_overview_dialog_carousel, docs_content_formats_overview_explainer_carousel, docs_content_formats_overview_text_social_post, docs_content_formats_overview_pinterest_pin [EXTRACTED 1.00]
- **Core Data Model Entities** — docs_data_model_brand_profile, docs_data_model_project, docs_data_model_cta, docs_data_model_scenario, docs_data_model_content_format, docs_data_model_render_job, docs_data_model_content_item, docs_data_model_export_package, docs_data_model_publication, docs_data_model_metric_snapshot [EXTRACTED 1.00]
- **Content Formats in Content Plant** — docs_format_pinterest_pins_pinterest_pin, docs_format_text_social_posts_text_social_post, docs_idea_bank_spec_idea, docs_production_engine_spec_production_engine [EXTRACTED 1.00]
- **Production Pipeline Modules** — docs_idea_bank_spec_idea, docs_production_engine_spec_production_engine, docs_pipelines_spec_pipeline, docs_integrations_spec_integration [EXTRACTED 1.00]
- **MVP Core Content Production Loop** — docs_mvp_scope_mvp, docs_format_text_social_posts_text_social_post, docs_format_pinterest_pins_pinterest_pin, docs_idea_bank_spec_idea, docs_production_engine_spec_production_engine, docs_pipelines_spec_pipeline [EXTRACTED 1.00]
- **Core Content Plant Modules** — docs_publishing_hub_spec, docs_qa_and_review, docs_scenario_studio_spec, docs_system_architecture, docs_workspace_and_project_model [EXTRACTED 1.00]
- **Content Plant User Interface Modules** — docs_web_ui_spec, docs_user_workflows, docs_publishing_hub_spec [EXTRACTED 1.00]
- **Trend Radar Integration with Content Plant** — docs_trend_radar_spec, docs_qa_and_review, docs_scenario_studio_spec, docs_publishing_hub_spec [EXTRACTED 1.00]
- **Nura TikTok Viral Screening Radar Project** — trend_radar_readme, trend_radar_docs_radar_guide, trend_radar_docs_scoring_logic, trend_radar_config_competitors, trend_radar_config_hashtags, trend_radar_config_keywords, trend_radar_config_rotational, trend_radar_rotational_keys, trend_radar_start_commands, trend_radar_prompts_pattern_analysis_ru [EXTRACTED 1.00]

## Communities (35 total, 12 thin omitted)

### Community 0 - "Brand Configuration Loader"
Cohesion: 0.07
Nodes (35): BrandProfile, BrandProfileStatus, Any, Path, Path, Project, ProjectConfig, AssetsConfig (+27 more)

### Community 1 - "Status Enum Definitions"
Cohesion: 0.34
Nodes (49): ContentItemStatus, Any, datetime, BrandProfileStatus, ContentFormat, ContentItemStatus, DomainModule, ExportPackageStatus (+41 more)

### Community 2 - "TikTok Video Collector"
Cohesion: 0.06
Nodes (31): analyze_top_videos(), analyze_video(), load_prompt(), TikTokCollector, send_digest(), async_random_sleep(), extract_video_id(), get_config() (+23 more)

### Community 3 - "Carousel Slide Assembly"
Cohesion: 0.10
Nodes (36): BaseModel, CarouselSlideBrief, SceneBrief, StockInsertion, BrandConfig, CarouselConfig, CarouselSettings, CarouselSlide (+28 more)

### Community 4 - "Video Pipeline Assembly"
Cohesion: 0.15
Nodes (16): BaseSettings, ContentBrief, _load_prompt(), _load_trend_data(), _match_local_stock(), _match_local_stock_to_scene(), _sanitize_name(), Settings (+8 more)

### Community 5 - "System Module Names"
Cohesion: 0.09
Nodes (27): Analytics, Brand Profile, Production Engine, Publishing Hub, QA and Review, Scenario Studio, Visual Prompt Generation, Atmospheric Video Format (+19 more)

### Community 6 - "Report Generation Utilities"
Cohesion: 0.14
Nodes (22): Connection, _fmt(), generate_report(), _parse_carousel_block(), _parse_scenario_block(), save_ai_analyses(), save_carousel_texts(), save_report() (+14 more)

### Community 7 - "Social Media Post Types"
Cohesion: 0.18
Nodes (22): Carousel Repurpose Pin, Checklist Pin, Mini Guide Pin, Pinterest Pin, Quote Pin, Tip Pin, Video Pin, Caption Post (+14 more)

### Community 8 - "Video Data Parser"
Cohesion: 0.25
Nodes (16): extract_from_api_responses(), _extract_from_dom(), _extract_from_json(), _extract_links(), extract_playlists_from_api(), extract_video_data(), _extract_video_id(), _find_items() (+8 more)

### Community 9 - "Status Transition Utilities"
Cohesion: 0.47
Nodes (3): utc_now(), validated_model_copy(), validate_status_transition()

### Community 11 - "TikTok Viral Screening Config"
Cohesion: 0.31
Nodes (10): Competitors Config, Hashtags Config, Keywords Config, Rotational Config, Nura TikTok Viral Screening Radar Guide, Scoring Logic for Nura TikTok Viral Screening Radar, Pattern Analysis Prompt (Russian), Nura TikTok Viral Screening Radar README (+2 more)

### Community 12 - "System Specification Docs"
Cohesion: 0.56
Nodes (9): Publishing Hub Spec, QA and Review Spec, Scenario Studio Spec, System Architecture, Task Prompt Templates, Trend Radar Spec, User Workflows, Web UI Spec (+1 more)

### Community 13 - "Package Configuration"
Cohesion: 0.22
Nodes (8): name, private, scripts, check, dev, publish, render, type

### Community 14 - "Asset Validation Module"
Cohesion: 0.61
Nodes (8): AssetReport, _check_video_file(), format_asset_report(), validate_job_assets(), _validate_media_files(), _validate_overlay_sources(), _validate_scene_references(), Path

### Community 15 - "Documentation Index and Specs"
Cohesion: 0.39
Nodes (8): Content Plant Documentation Index, MVP Scope, Brand System Spec, Workspace and Project Model, NURA Project Profile, Agent Rules, Analytics and Optimization Spec, Asset Library Spec

### Community 16 - "Content Package Builder"
Cohesion: 0.54
Nodes (6): build_package(), _build_publish_notes(), ContentPackage, _extract_text_content(), _write_text(), Path

### Community 17 - "Hyperframes JSON Schema"
Cohesion: 0.29
Nodes (6): paths, assets, blocks, components, registry, $schema

## Knowledge Gaps
- **54 isolated node(s):** `$schema`, `registry`, `blocks`, `components`, `assets` (+49 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `datetime` connect `Status Enum Definitions` to `TikTok Video Collector`, `Carousel Slide Assembly`, `Report Generation Utilities`, `Status Transition Utilities`, `Status Transition Tests`?**
  _High betweenness centrality (0.237) - this node is a cross-community bridge._
- **Why does `BaseModel` connect `Carousel Slide Assembly` to `Brand Configuration Loader`, `Status Enum Definitions`, `Video Pipeline Assembly`, `Status Transition Utilities`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Why does `TikTokCollector` connect `TikTok Video Collector` to `Report Generation Utilities`?**
  _High betweenness centrality (0.143) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `BaseModel` (e.g. with `BrandProfileStatus` and `ContentFormat`) actually correct?**
  _`BaseModel` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `ContentItemStatus` (e.g. with `ContentItemStatus` and `Any`) actually correct?**
  _`ContentItemStatus` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `PublicationStatus` (e.g. with `ContentItemStatus` and `Any`) actually correct?**
  _`PublicationStatus` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `RenderJobStatus` (e.g. with `ContentItemStatus` and `Any`) actually correct?**
  _`RenderJobStatus` has 30 INFERRED edges - model-reasoned connections that need verification._