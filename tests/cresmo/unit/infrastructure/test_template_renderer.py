"""Hermetic unit tests for single compiled Mustache TemplateRenderer (ADR-071)."""

from __future__ import annotations

from cresmo.infrastructure.adapters.prompts.template_renderer import TemplateRenderer


class TestTemplateRenderer:
    """Unit tests verifying Mustache substitution, JSON brace safety, and unmatched preservation."""

    def test_render_replaces_mustache_tags_and_preserves_literal_json(self) -> None:
        renderer = TemplateRenderer()
        template = (
            'System for {{language}}: return JSON {"title": "example", "count": 1}. '
            "Keep {{unmatched_tag}} intact and accept {{ spaced_key }}."
        )
        rendered = renderer.render(
            template,
            {"language": "English", "spaced_key": "OK"},
        )
        assert '{"title": "example", "count": 1}' in rendered
        assert "System for English:" in rendered
        assert "accept OK." in rendered
        assert "{{unmatched_tag}}" in rendered

    def test_render_handles_empty_template_and_hyphenated_skill_names(self) -> None:
        renderer = TemplateRenderer()
        assert renderer.render("", {"a": "b"}) == ""
        assert renderer.render("Keep {{a}}", {}) == "Keep {{a}}"
        assert (
            renderer.render("Rule: {{cresmo-style-guide}}", {"cresmo-style-guide": "CLEAN"})
            == "Rule: CLEAN"
        )
