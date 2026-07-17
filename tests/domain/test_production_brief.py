from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.domain import (
    ProductionBrief,
    ProductionBriefStatus,
    ProductionScene,
    ProductionAudio,
    ProductionOutput,
    ProductionSlide,
    ProductionQA,
    ProductionSubtitles,
    ProductionBrand,
    ContentFormat,
    PublishingPlatform,
    InvalidStatusTransitionError,
    PRODUCTION_BRIEF_STATUS_TRANSITIONS,
)
from core.domain.models import utc_now


def test_production_brief_creation() -> None:
    brief = ProductionBrief(
        production_brief_id="brief_minimal_001",
        workspace_id="internal",
        project_id="nura",
        scenario_id="scenario_abc",
    )
    assert brief.production_brief_id == "brief_minimal_001"
    assert brief.workspace_id == "internal"
    assert brief.project_id == "nura"
    assert brief.scenario_id == "scenario_abc"
    assert brief.content_format == ContentFormat.TEXT_SOCIAL_POST
    assert brief.production_variant == ""
    assert brief.target_platforms == []
    assert brief.scenes == []
    assert isinstance(brief.audio, ProductionAudio)
    assert isinstance(brief.subtitles, ProductionSubtitles)
    assert isinstance(brief.output, ProductionOutput)
    assert isinstance(brief.brand, ProductionBrand)
    assert brief.slides == []
    assert isinstance(brief.qa, ProductionQA)
    assert brief.status == ProductionBriefStatus.DRAFT


def test_production_brief_creation_full_narrative() -> None:
    brief = ProductionBrief(
        production_brief_id="brief_test_001",
        workspace_id="internal",
        project_id="nura",
        scenario_id="scenario_abc",
        content_format=ContentFormat.SHORT_VERTICAL_VIDEO,
        production_variant="static_images_narrative",
        target_platforms=[PublishingPlatform.TIKTOK, PublishingPlatform.INSTAGRAM],
        scenes=[
            ProductionScene(index=0, purpose="hook", image_source="img_01.png", duration_sec=3.0, narration_text="Test hook"),
            ProductionScene(index=1, purpose="main", image_source="img_02.png", duration_sec=5.0, narration_text="Test body"),
            ProductionScene(index=2, purpose="main", image_source="img_03.png", duration_sec=4.0, narration_text="Test value"),
            ProductionScene(index=3, purpose="cta", image_source="img_04.png", duration_sec=3.0, narration_text="Test CTA"),
        ],
        audio=ProductionAudio(voiceover_path="vo.wav", music_path="bg.mp3", music_volume=0.15, ducking_enabled=True),
        subtitles=ProductionSubtitles(enabled=True, mode="manual", font_path="font.ttf", font_size=50),
        output=ProductionOutput(aspect_ratio="9:16", resolution_width=1080, resolution_height=1920, fps=24, generate_srt=True, generate_cover=True),
        qa=ProductionQA(check_resolution=True, check_duration=True, check_audio=True, check_subtitles=True),
    )
    assert brief.production_brief_id == "brief_test_001"
    assert brief.content_format == ContentFormat.SHORT_VERTICAL_VIDEO
    assert brief.production_variant == "static_images_narrative"
    assert brief.target_platforms == [PublishingPlatform.TIKTOK, PublishingPlatform.INSTAGRAM]
    assert len(brief.scenes) == 4
    assert brief.scenes[0].purpose == "hook"
    assert brief.scenes[0].narration_text == "Test hook"
    assert brief.scenes[3].purpose == "cta"
    assert brief.audio.voiceover_path == "vo.wav"
    assert brief.audio.music_volume == 0.15
    assert brief.audio.ducking_enabled is True
    assert brief.subtitles.enabled is True
    assert brief.subtitles.font_size == 50
    assert brief.output.aspect_ratio == "9:16"
    assert brief.output.resolution_width == 1080
    assert brief.output.resolution_height == 1920
    assert brief.output.generate_srt is True
    assert brief.output.generate_cover is True
    assert brief.qa.check_resolution is True
    assert brief.qa.check_duration is True
    assert brief.qa.check_audio is True
    assert brief.qa.check_subtitles is True


def test_production_brief_creation_carousel() -> None:
    brief = ProductionBrief(
        production_brief_id="brief_test_002",
        workspace_id="internal",
        project_id="nura",
        scenario_id="scenario_xyz",
        content_format=ContentFormat.INSTAGRAM_CAROUSEL,
        production_variant="educational_carousel",
        target_platforms=[PublishingPlatform.INSTAGRAM],
        output=ProductionOutput(aspect_ratio="4:5", resolution_width=1080, resolution_height=1350, slide_count=7),
        slides=[
            ProductionSlide(slide_number=1, template="cover", heading="Test cover"),
            ProductionSlide(slide_number=2, template="quote", heading="Slide 2"),
            ProductionSlide(slide_number=3, template="list", heading="Slide 3"),
            ProductionSlide(slide_number=4, template="text_image", heading="Slide 4"),
            ProductionSlide(slide_number=5, template="quote", heading="Slide 5"),
            ProductionSlide(slide_number=6, template="list", heading="Slide 6"),
            ProductionSlide(slide_number=7, template="cta", heading="CTA", cta="Click here"),
        ],
        brand=ProductionBrand(colors_primary="#D97A32", colors_accent="#8C6A3B"),
        qa=ProductionQA(check_slide_count=True),
    )
    assert brief.production_brief_id == "brief_test_002"
    assert brief.content_format == ContentFormat.INSTAGRAM_CAROUSEL
    assert brief.production_variant == "educational_carousel"
    assert brief.target_platforms == [PublishingPlatform.INSTAGRAM]
    assert len(brief.slides) == 7
    assert brief.slides[0].slide_number == 1
    assert brief.slides[0].heading == "Test cover"
    assert brief.slides[6].slide_number == 7
    assert brief.slides[6].cta == "Click here"
    assert brief.brand.colors_primary == "#D97A32"
    assert brief.brand.colors_accent == "#8C6A3B"
    assert brief.qa.check_slide_count is True
    assert brief.output.slide_count == 7


def test_production_brief_missing_required_fields() -> None:
    with pytest.raises(ValidationError):
        ProductionBrief(
            production_brief_id="",
            workspace_id="internal",
            project_id="nura",
            scenario_id="scenario_abc",
        )


def test_production_brief_invalid_content_format() -> None:
    with pytest.raises(ValidationError):
        ProductionBrief(
            production_brief_id="brief_invalid_fmt",
            workspace_id="internal",
            project_id="nura",
            scenario_id="scenario_abc",
            content_format="invalid_format",
        )


def test_production_brief_status_transitions_valid() -> None:
    brief = ProductionBrief(
        production_brief_id="brief_status_001",
        workspace_id="internal",
        project_id="nura",
        scenario_id="scenario_abc",
    )
    assert brief.status == ProductionBriefStatus.DRAFT

    validated = brief.transition_to(ProductionBriefStatus.VALIDATED)
    assert validated.status == ProductionBriefStatus.VALIDATED

    approved = validated.transition_to(ProductionBriefStatus.APPROVED)
    assert approved.status == ProductionBriefStatus.APPROVED

    in_progress = approved.transition_to(ProductionBriefStatus.IN_PROGRESS)
    assert in_progress.status == ProductionBriefStatus.IN_PROGRESS

    completed = in_progress.transition_to(ProductionBriefStatus.COMPLETED)
    assert completed.status == ProductionBriefStatus.COMPLETED

    archived = completed.transition_to(ProductionBriefStatus.ARCHIVED)
    assert archived.status == ProductionBriefStatus.ARCHIVED


def test_production_brief_status_transitions_invalid() -> None:
    brief = ProductionBrief(
        production_brief_id="brief_status_002",
        workspace_id="internal",
        project_id="nura",
        scenario_id="scenario_abc",
    )
    with pytest.raises(InvalidStatusTransitionError):
        brief.transition_to(ProductionBriefStatus.COMPLETED)


def test_production_scene_validation() -> None:
    with pytest.raises(ValidationError):
        ProductionScene(
            index=-1,
            purpose="invalid",
            image_source="test.png",
        )


def test_production_slide_validation() -> None:
    with pytest.raises(ValidationError):
        ProductionSlide(slide_number=0, heading="Invalid slide")

    with pytest.raises(ValidationError):
        ProductionSlide(slide_number=11, heading="Invalid slide")


def test_production_audio_validation() -> None:
    with pytest.raises(ValidationError):
        ProductionAudio(music_volume=1.5)

    with pytest.raises(ValidationError):
        ProductionAudio(music_volume=-0.1)
