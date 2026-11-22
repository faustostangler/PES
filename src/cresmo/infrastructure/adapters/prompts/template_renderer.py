"""Single compiled Mustache `{{variable}}` template rendering engine.

Conforms to:
    - ADR-052: Langfuse Chat-Native Prompt Catalog & Local JSON Fallback
    - ADR-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
    - SPEC-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
"""

from __future__ import annotations

import re
from collections.abc import Mapping

_MUSTACHE_TAG_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_\-]+)\s*\}\}")


class TemplateRenderer:
    """Render double-brace Mustache `{{variable}}` placeholders while preserving literal JSON."""

    def render(self, template: str, variables: Mapping[str, str]) -> str:
        """Substitute matched `{{key}}` tags with values, leaving unmatched tags untouched.

        Args:
            template: Raw template string containing Mustache ``{{var}}`` tags.
            variables: Mapping of variable names to string replacement values.

        Returns:
            Rendered string with matched placeholders replaced and literal JSON braces intact.
        """
        if not template or not variables:
            return template

        def _replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key in variables:
                return variables[key]
            return match.group(0)

        return _MUSTACHE_TAG_RE.sub(_replace, template)
