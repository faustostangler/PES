"""Hexagonal Application Port for Directed Reflection Critique Synthesis (ADR-031)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from cresmo.domain.value_objects.quality import JudgeEvaluation


class CritiqueSynthesizerPort(ABC):
    """Port defining contract for converting structured JudgeEvaluation into directed natural language critique."""

    @abstractmethod
    def synthesize(
        self,
        evaluation: JudgeEvaluation,
        stage_name: str,
        *,
        trace_id: str | None = None,
    ) -> str:
        """Synthesize structured verdict criteria failures into concise imperative instructions.

        Args:
            evaluation: The failed JudgeEvaluation containing criteria scores and reasoning.
            stage_name: Unique stage identifier (e.g. 'fluid_prose').
            trace_id: Optional distributed trace identifier.

        Returns:
            Concise, directed natural language critique to inject into reflection prompt.
        """
