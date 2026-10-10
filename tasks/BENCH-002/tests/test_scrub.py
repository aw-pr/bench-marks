"""
test_scrub.py — unit tests for scripts/scrub.py

Run from the repo root:
    python3 -m pytest tasks/BENCH-002/tests/ -v

Or from the bench-marks repo root:
    python3 -m pytest tasks/BENCH-002/tests/test_scrub.py -v
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Allow import of scrub.py from the scripts directory.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import scrub  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures: sample summary content representing each provider
# ---------------------------------------------------------------------------

SAMPLE_GEMINI_SUMMARY = """\
---
provider: gemini
topic: 'AI regulation in financial services'
date: 2026-05-19
from: 2023
to: 2026
lanes: [financial, frontier, academic, vc, blogs, tech]
depth: deep
brief_title: 'AI Regulation Test'
brief_file: '/private/path/to/prompts/brief.md'
model_lane: gemini-2.5-flash
model_synthesis: gemini-2.5-pro
tags: [research-sweep, gemini, ai-regulation]
---
### Overview

The EU AI Act and UK regulatory divergence are the defining issues. Gemini-sourced analysis
confirms that OpenAI, Anthropic and Google DeepMind all face GPAI obligations.

### Key Findings

The FCA Mills Review is a significant development. Regulatory pressure from the Treasury Committee
has increased.

Sources: [[sources-ai-regulation#^a1|Bank of England (2023)]] ([↗](https://www.bankofengland.co.uk/))

![[sources-ai-regulation]]
"""

SAMPLE_OPENAI_SUMMARY = """\
---
provider: openai
topic: 'AI regulation in financial services'
date: 2026-05-19
model_lane: gpt-5.4-mini
model_synthesis: gpt-5.5
tags: [research-sweep, openai, ai-regulation]
---
### Overview

OpenAI analysis of EU AI Act compliance. GPT-5 capabilities are subject to GPAI obligations.
Anthropic and Google DeepMind face similar requirements.

![[sources-ai-regulation]]
"""

SAMPLE_CLAUDE_SUMMARY = """\
---
provider: claude
topic: 'AI regulation in financial services'
date: 2026-05-19
model_lane: claude-haiku-4-5-20251001
model_synthesis: claude-opus-4-7
tags: [research-sweep, claude, ai-regulation]
---
### Overview

Claude synthesis of the regulatory landscape. Anthropic's own GPAI obligations are noted.

![[sources-ai-regulation]]
"""

SAMPLE_WITH_VERTEX_URL = """\
---
provider: gemini
date: 2026-05-19
---
Some text with a grounding URL: https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQabcdef1234567890 and more text.
"""


# ---------------------------------------------------------------------------
# Tests: frontmatter scrubbing
# ---------------------------------------------------------------------------

class TestFrontmatterScrub:
    def test_provider_field_removed(self):
        text, removed = scrub._scrub_frontmatter(SAMPLE_GEMINI_SUMMARY)
        assert "provider: gemini" not in text
        assert "provider" in removed

    def test_model_lane_removed(self):
        text, removed = scrub._scrub_frontmatter(SAMPLE_GEMINI_SUMMARY)
        assert "model_lane" not in text
        assert "model_lane" in removed

    def test_model_synthesis_removed(self):
        text, removed = scrub._scrub_frontmatter(SAMPLE_GEMINI_SUMMARY)
        assert "model_synthesis" not in text
        assert "model_synthesis" in removed

    def test_brief_file_removed(self):
        text, removed = scrub._scrub_frontmatter(SAMPLE_GEMINI_SUMMARY)
        assert "brief_file" not in text
        assert "brief_file" in removed

    def test_tags_removed(self):
        text, removed = scrub._scrub_frontmatter(SAMPLE_GEMINI_SUMMARY)
        assert "tags:" not in text
        assert "tags" in removed

    def test_safe_fields_preserved(self):
        text, _ = scrub._scrub_frontmatter(SAMPLE_GEMINI_SUMMARY)
        # topic, date, from, to, lanes, depth, brief_title should survive
        assert "topic:" in text
        assert "date:" in text
        assert "lanes:" in text
        assert "depth:" in text

    def test_openai_model_fields_removed(self):
        text, removed = scrub._scrub_frontmatter(SAMPLE_OPENAI_SUMMARY)
        assert "gpt-5.4-mini" not in text
        assert "gpt-5.5" not in text

    def test_claude_model_fields_removed(self):
        text, removed = scrub._scrub_frontmatter(SAMPLE_CLAUDE_SUMMARY)
        assert "claude-haiku" not in text
        assert "claude-opus" not in text

    def test_no_frontmatter_passthrough(self):
        plain = "No frontmatter here.\n\nJust body text."
        text, removed = scrub._scrub_frontmatter(plain)
        assert text == plain
        assert removed == {}


# ---------------------------------------------------------------------------
# Tests: provider name replacement
# ---------------------------------------------------------------------------

class TestProviderNameScrub:
    def test_gemini_name_replaced(self):
        text, replacements = scrub._scrub_provider_names("Gemini-sourced analysis")
        assert "Gemini" not in text
        assert scrub.REPLACEMENT in text
        assert any("Gemini" in r for r in replacements)

    def test_openai_name_replaced(self):
        text, replacements = scrub._scrub_provider_names("OpenAI analysis confirms GPT-5 capabilities.")
        assert "OpenAI" not in text

    def test_anthropic_name_replaced(self):
        text, replacements = scrub._scrub_provider_names("Anthropic's GPAI obligations are noted.")
        assert "Anthropic" not in text

    def test_google_deepmind_replaced(self):
        text, _ = scrub._scrub_provider_names("Google DeepMind released Gemini Deep Think.")
        assert "Google DeepMind" not in text

    def test_case_insensitive_replacement(self):
        text, _ = scrub._scrub_provider_names("GEMINI model capabilities")
        assert "GEMINI" not in text

    def test_non_provider_text_preserved(self):
        original = "The FCA Mills Review is a significant development."
        text, replacements = scrub._scrub_provider_names(original)
        assert text == original
        assert replacements == []

    def test_eu_ai_act_preserved(self):
        original = "The EU AI Act's GPAI obligations took effect in August 2025."
        text, _ = scrub._scrub_provider_names(original)
        assert "EU AI Act" in text
        assert "GPAI" in text


# ---------------------------------------------------------------------------
# Tests: structural pattern removal
# ---------------------------------------------------------------------------

class TestStructuralPatterns:
    def test_obsidian_transclusion_removed(self):
        text, removed = scrub._remove_structural_patterns("Some text.\n\n![[sources-ai-regulation]]\n")
        assert "![[sources-" not in text

    def test_vertex_redirect_url_removed(self):
        text, removed = scrub._remove_structural_patterns(SAMPLE_WITH_VERTEX_URL)
        assert "vertexaisearch.cloud.google.com" not in text

    def test_citation_wikilink_removed(self):
        citation = "Sources: [[sources-ai-regulation#^a1|Bank of England (2023)]] ([↗](https://www.bankofengland.co.uk/))"
        text, _ = scrub._remove_structural_patterns(citation)
        assert "[[sources-" not in text

    def test_plain_urls_preserved(self):
        plain = "See https://www.bankofengland.co.uk/ for details."
        text, _ = scrub._remove_structural_patterns(plain)
        assert "https://www.bankofengland.co.uk/" in text


# ---------------------------------------------------------------------------
# Tests: end-to-end scrub_file (no provider names survive)
# ---------------------------------------------------------------------------

class TestScrubFile:
    def _write_temp(self, content: str) -> str:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(content)
            return f.name

    def _cleanup(self, path: str):
        try:
            os.unlink(path)
        except OSError:
            pass

    def test_no_provider_names_in_gemini_output(self):
        path = self._write_temp(SAMPLE_GEMINI_SUMMARY)
        try:
            text, _ = scrub.scrub_file(path)
            # "gemini" may appear in topic/date-range context but not as a provider label
            # The tag was removed; model fields were removed. Check the specific provider markers:
            assert "provider: gemini" not in text
            assert "model_lane: gemini" not in text
            assert "tags:" not in text
        finally:
            self._cleanup(path)

    def test_no_provider_names_in_openai_output(self):
        path = self._write_temp(SAMPLE_OPENAI_SUMMARY)
        try:
            text, _ = scrub.scrub_file(path)
            assert "provider: openai" not in text
            assert "gpt-5.4-mini" not in text
            assert "gpt-5.5" not in text
        finally:
            self._cleanup(path)

    def test_no_provider_names_in_claude_output(self):
        path = self._write_temp(SAMPLE_CLAUDE_SUMMARY)
        try:
            text, _ = scrub.scrub_file(path)
            assert "provider: claude" not in text
            assert "claude-haiku" not in text
            assert "claude-opus" not in text
        finally:
            self._cleanup(path)

    def test_manifest_structure(self):
        path = self._write_temp(SAMPLE_GEMINI_SUMMARY)
        try:
            _, manifest = scrub.scrub_file(path)
            assert "frontmatter_fields_removed" in manifest
            assert "provider_name_replacements" in manifest
            assert "structural_blocks_removed_count" in manifest
        finally:
            self._cleanup(path)

    def test_body_content_preserved_after_scrub(self):
        """Key substantive content (regulatory instruments) must survive scrubbing."""
        path = self._write_temp(SAMPLE_GEMINI_SUMMARY)
        try:
            text, _ = scrub.scrub_file(path)
            assert "FCA Mills Review" in text
            assert "Treasury Committee" in text
            assert "GPAI" in text
        finally:
            self._cleanup(path)

    def test_no_vertex_urls_in_output(self):
        path = self._write_temp(SAMPLE_WITH_VERTEX_URL)
        try:
            text, _ = scrub.scrub_file(path)
            assert "vertexaisearch" not in text
        finally:
            self._cleanup(path)
