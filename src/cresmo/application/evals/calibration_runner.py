"""Stage-agnostic LLM Judge Calibration runner, checkpointing, and report generator.

Decouples pure calibration orchestration from CLI/dotenv/infrastructure adapters so
tests exercise the calibration engine through application contracts only.

Conforms to:
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI with Cooldown-Aware Checkpointing
    - ADR-062: Structural Consolidation, Evals SSOT, and Bootstrap Separation
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle
    - ADR-060: Gap Filler Judge Criteria v2
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import re
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from cresmo.application.evals.calibration_metrics import (
    CalibrationResultSet,
    CalibrationSuiteOutcome,
    ConfusionMatrix,
    ItemEvaluationResult,
    ModelBenchmarkSummary,
)
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.exceptions import RateLimitExceededError
from cresmo.domain.value_objects.prompt import PromptKey
from cresmo.domain.value_objects.quality import (
    EvaluationContext,
    JudgeCriterion,
)

DEFAULT_CHECKPOINT_DIR = Path("data") / "calibration_checkpoints"
DEFAULT_REPORTS_DIR = Path("reports") / "calibration"
DEFAULT_DATASETS_DIR = Path("evals") / "datasets"

PromptTemplateLookup = Callable[[PromptKey], dict[str, str]]


class CooldownActiveError(RateLimitExceededError):
    """Raised when a calibration target already sits inside an active quota cooldown window."""

    def __init__(self, retry_after_seconds: float, message: str) -> None:
        self.retry_after_seconds = max(0.0, retry_after_seconds)
        super().__init__(message)


class JudgeCalibrationFactory(Protocol):
    """Port callback building an isolated judge adapter for one calibration target."""

    def __call__(
        self,
        *,
        provider: str,
        model: str,
        threshold: float,
        enable_fallback: bool,
    ) -> LlmJudgePort:
        """Return a configured LlmJudgePort with explicit fallback mode."""
        ...


FLUID_PROSE_SEED_DATA: tuple[dict[str, Any], ...] = (
    {
        "id": "item_01_pass_clean_narrative",
        "input": {
            "raw_text": (
                "então pessoal hoje a gente vai falar do G. W. F. Hegel, né? "
                "ele pensava que a história caminha por contradições e dialética, tá ligado?"
            ),
            "candidate_text": (
                "## A Dialética e o Movimento Histórico\n\n"
                "Na filosofia de **G. W. F. Hegel**, o desenvolvimento histórico opera através de "
                "contradições dialéticas imanentes. As transformações sociais expressam a superação "
                "de contradições estruturais que reorganizam as instituições políticas."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "orality_removal",
            "difficulty": "easy",
            "category": "valid_transformation",
        },
    },
    {
        "id": "item_02_fail_youtube_cta",
        "input": {
            "raw_text": "não esquece de se inscrever no canal e deixar o like se gostou do vídeo.",
            "candidate_text": (
                "## Introdução ao Tema\n\n"
                "O debate envolve teorias econômicas clássicas. "
                "Inscreva-se no canal para acompanhar os próximos episódios."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "orality_removal",
            "difficulty": "easy",
            "expected_anomaly": "youtube_cta_leakage",
        },
    },
    {
        "id": "item_03_fail_mechanical_em_dash",
        "input": {
            "raw_text": "ele tomou uma decisão muito dura ali naquele momento histórico.",
            "candidate_text": (
                "## Contexto Decisório\n\n"
                "A deliberação governamental — tomada sem consulta aos parlamentares — "
                "precipitou a crise fiscal subsequente."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "structural_compliance",
            "difficulty": "borderline",
            "expected_anomaly": "forbidden_em_dash",
        },
    },
    {
        "id": "item_04_pass_with_epistemic_qualification",
        "input": {
            "raw_text": (
                "o tratado de versalhes foi assinado em 1945 bem depois da guerra, "
                "todo mundo sabe disso."
            ),
            "candidate_text": (
                "## Os Tratados Internacionais e a Diplomacia\n\n"
                "O interlocutor afirma que o **Tratado de Versalhes** foi firmado em 1945; "
                "no entanto, os registros históricos diplomáticos estabelecem sua celebração "
                "formal em 1919 ao término da Primeira Guerra Mundial. Esta discrepância temporal "
                "requer retificação documental."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_critique",
            "difficulty": "typical",
            "expected_anomaly": "none",
        },
    },
    {
        "id": "item_05_fail_binary_antithesis",
        "input": {
            "raw_text": "não é uma questão simples, é algo muito profundo na sociedade.",
            "candidate_text": (
                "## Análise Social\n\n"
                "Não se trata de uma crise orçamentária simples, e sim de uma ruptura "
                "estrutural nos alicerces institucionais do Estado moderno."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "authorial_voice",
            "difficulty": "borderline",
            "expected_anomaly": "binary_antithesis",
        },
    },
)

GAP_FILLER_SEED_DATA: tuple[dict[str, Any], ...] = (
    {
        "id": "eg_seed_01_pass",
        "input": {
            "raw_text": (
                "## A Posse de Afonso Henriques e a Bula Manifestis Probatum\n\n"
                "Afonso Henriques declarou a autonomia do Condado Portucalense no século XII. "
                "Após anos de conflitos contra o Reino de Leão e campanhas da Reconquista, "
                "a corte papal reconheceu formalmente a soberania portuguesa através de "
                "documento solene."
            ),
            "candidate_text": (
                "## A Autonomia Feudal e a Legitimação Apostólica do Reino de Portugal\n\n"
                "A consolidação política da independência portucalense articulou vitórias campais "
                "contra os exércitos de Afonso VII de Leão e a inserção direta na rede de "
                "suserania da Santa Sé. Em 1179-05-23, o papa Alexandre III promulgou a bula "
                "Manifestis Probatum, declarando Afonso Henriques rei soberano de Portugal e "
                "outorgando proteção apostólica contra reivindicações anexionistas de monarcas "
                "cristãos vizinhos.\n\n"
                "Esse ato diplomático coroou um esforço de décadas iniciado no Tratado de Zamora "
                "em 1143-10-05, subordinando a legitimidade jurídica do novo reino ao pagamento "
                "anual de um censo de dois marcos de ouro à corte romana.\n\n"
                "### Extra Info\n\n"
                "1. O Tratado de Zamora de 1143-10-05 contou com a mediação do cardeal Guido "
                "de Vico, legado papal na Península Ibérica.\n"
                "2. O censo pago por Afonso Henriques à Santa Sé foi elevado de quatro onças de "
                "ouro anuais em 1144 para dois marcos de ouro em 1179."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_grounding_segregation",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "9IbNJ0EsTxI",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "cm_seed_02_fail",
        "input": {
            "raw_text": (
                "## Concorrência e Gargalos em Bancos Relacionais sob Alta Carga\n\n"
                "Em testes de estresse com milhares de requisições simultâneas por segundo, o "
                "banco de dados PostgreSQL frequentemente apresenta degradação severa de latência "
                "quando as conexões não são limitadas. O esgotamento de recursos decorre da "
                "contenção de bloqueios em linhas concorrentes e do custo de context switching "
                "entre múltiplos processos no sistema operacional."
            ),
            "candidate_text": (
                "## O Esgotamento de Recursos em Bancos Relacionais sob Concorrência Extrema\n\n"
                "Em cenários de estresse computacional caracterizados por taxas elevadas de "
                "transações simultâneas, a arquitetura do PostgreSQL manifesta variações "
                "desproporcionais na latência percebida pelos clientes. A saturação de conexões "
                "sem pooling adequado impõe um ônus que degrada o rendimento global da aplicação "
                "sob teste de estresse na infraestrutura em contêineres Docker.\n\n"
                "A degradação manifesta-se através de disputas intensas por recursos "
                "compartilhados, onde diferentes processos disputam o acesso aos mesmos registros "
                "de tabelas financeiras. A sobrecarga de gerenciar dezenas de processos paralelos "
                "força o núcleo do sistema operacional a despender ciclos de processamento em "
                "trocas de contexto.\n\n"
                "### Extra Info\n\n"
                "1. O gerenciador de conexões PgBouncer gerencia três modos distintos de "
                "agrupamento: sessão, transação e instrução.\n"
                "2. O comando EXPLAIN ANALYZE do PostgreSQL executa a consulta e retorna o plano "
                "de execução real juntamente com os custos."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "conceptual_mechanical_decomposition",
            "difficulty": "borderline",
            "expected_anomaly": "explanatory_vacuum_missing_mvcc_intermediate_mechanisms",
            "defect_location": "paragraph_2",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "FAIL",
        },
    },
)


@dataclass(frozen=True, slots=True)
class StageCalibrationSpec:
    """Declarative specification defining calibration behavior for a pipeline stage."""

    stage_name: str
    label: str
    prompt_key: PromptKey
    default_golden_set_path: Path
    required_criteria: tuple[JudgeCriterion, ...]
    seed_items: tuple[dict[str, Any], ...]


def build_stage_specs(
    datasets_dir: Path = DEFAULT_DATASETS_DIR,
) -> dict[str, StageCalibrationSpec]:
    """Build stage calibration specifications rooted under the supplied datasets directory."""
    return {
        "fluid_prose": StageCalibrationSpec(
            stage_name="fluid_prose",
            label="Stage 1: Fluid Prose",
            prompt_key=PromptKey.JUDGE_FLUID_PROSE,
            default_golden_set_path=datasets_dir / "fluid_prose_golden_set.json",
            required_criteria=(
                JudgeCriterion.ORALITY_REMOVAL,
                JudgeCriterion.SEMANTIC_FAITHFULNESS,
                JudgeCriterion.EPISTEMIC_CRITIQUE,
                JudgeCriterion.NER_PRESERVATION,
                JudgeCriterion.STRUCTURAL_COMPLIANCE,
                JudgeCriterion.AUTHORIAL_VOICE,
            ),
            seed_items=FLUID_PROSE_SEED_DATA,
        ),
        "gap_filler": StageCalibrationSpec(
            stage_name="gap_filler",
            label="Stage 2: Gap Filler",
            prompt_key=PromptKey.JUDGE_GAP_FILLER,
            default_golden_set_path=datasets_dir / "gap_filler_golden_set.json",
            required_criteria=(
                JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,
                JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION,
                JudgeCriterion.BRAUDELIAN_STRATIFICATION,
                JudgeCriterion.GENEALOGY_HIDDEN_AGENCY,
                JudgeCriterion.COMPETING_HYPOTHESES,
                JudgeCriterion.EXTRA_INFO_GRANULARITY,
                JudgeCriterion.LINEAR_STYLE_NATURALISM,
            ),
            seed_items=GAP_FILLER_SEED_DATA,
        ),
    }


STAGE_SPECS: dict[str, StageCalibrationSpec] = build_stage_specs()


class CalibrationCheckpointStore:
    """Atomic JSON checkpoint and cooldown manager under `data/calibration_checkpoints/`.

    Persists evaluated items per `(stage, provider, model)` bound to `config_hash` and
    tracks cooldown expiration per `(stage, provider, model)` plus shared `(provider, model)`
    rate/quota limits so subsequent runs resume cleanly without wasted calls.
    """

    def __init__(self, checkpoint_dir: Path = DEFAULT_CHECKPOINT_DIR) -> None:
        self.checkpoint_dir = checkpoint_dir

    @staticmethod
    def _slug(value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_\-\.]", "_", value.strip())

    def _target_path(self, stage: str, provider: str, model: str) -> Path:
        filename = f"{self._slug(stage)}__{self._slug(provider)}__{self._slug(model)}.json"
        return self.checkpoint_dir / filename

    @property
    def _cooldowns_path(self) -> Path:
        return self.checkpoint_dir / "cooldowns.json"

    @staticmethod
    def _shared_key(provider: str, model: str) -> str:
        return f"{provider.strip().lower()}:{model.strip()}"

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}
        return raw if isinstance(raw, dict) else {}

    def _write_json_atomic(self, path: Path, payload: dict[str, Any]) -> None:
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(".json.tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(tmp_path, path)

    def load_completed_items(
        self,
        stage: str,
        provider: str,
        model: str,
        config_hash: str,
    ) -> dict[str, dict[str, Any]]:
        """Load checkpointed item verdicts only when `config_hash` matches current config."""
        data = self._read_json(self._target_path(stage, provider, model))
        if not data or data.get("config_hash") != config_hash:
            return {}
        items = data.get("items")
        if not isinstance(items, dict):
            return {}
        return {str(k): v for k, v in items.items() if isinstance(v, dict)}

    def record_item(
        self,
        stage: str,
        provider: str,
        model: str,
        config_hash: str,
        item_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Atomically append or update one evaluated item in the target checkpoint file."""
        path = self._target_path(stage, provider, model)
        existing = self._read_json(path)
        if existing.get("config_hash") != config_hash:
            items: dict[str, Any] = {}
        else:
            raw_items = existing.get("items")
            items = dict(raw_items) if isinstance(raw_items, dict) else {}
        items[item_id] = payload
        updated: dict[str, Any] = {
            "stage": stage,
            "provider": provider,
            "model": model,
            "config_hash": config_hash,
            "updated_at": datetime.now(UTC).isoformat(),
            "items": items,
        }
        if isinstance(existing.get("cooldown_until"), int | float):
            updated["cooldown_until"] = float(existing["cooldown_until"])
        self._write_json_atomic(path, updated)

    def record_cooldown(
        self,
        stage: str,
        provider: str,
        model: str,
        until_ts: float,
    ) -> None:
        """Persist cooldown expiration timestamp for `(stage, provider, model)` and shared model."""
        path = self._target_path(stage, provider, model)
        existing = self._read_json(path)
        existing.setdefault("stage", stage)
        existing.setdefault("provider", provider)
        existing.setdefault("model", model)
        prev_target_cd = existing.get("cooldown_until")
        if isinstance(prev_target_cd, int | float):
            existing["cooldown_until"] = max(float(prev_target_cd), until_ts)
        else:
            existing["cooldown_until"] = until_ts
        self._write_json_atomic(path, existing)

        cooldowns = self._read_json(self._cooldowns_path)
        shared_key = self._shared_key(provider, model)
        prev_shared = cooldowns.get(shared_key)
        if isinstance(prev_shared, int | float):
            cooldowns[shared_key] = max(float(prev_shared), until_ts)
        else:
            cooldowns[shared_key] = until_ts
        self._write_json_atomic(self._cooldowns_path, cooldowns)

    def active_cooldown_until(
        self,
        stage: str,
        provider: str,
        model: str,
        now: float | None = None,
    ) -> float | None:
        """Return future cooldown epoch timestamp if still active, else None."""
        current_now = time.time() if now is None else now
        candidates: list[float] = []

        target_data = self._read_json(self._target_path(stage, provider, model))
        target_cd = target_data.get("cooldown_until")
        if isinstance(target_cd, int | float) and float(target_cd) > current_now:
            candidates.append(float(target_cd))

        cooldowns = self._read_json(self._cooldowns_path)
        shared_cd = cooldowns.get(self._shared_key(provider, model))
        if isinstance(shared_cd, int | float) and float(shared_cd) > current_now:
            candidates.append(float(shared_cd))

        return max(candidates) if candidates else None

    def clear_cooldown(self, stage: str, provider: str, model: str) -> None:
        """Clear cooldown metadata after target completes cleanly."""
        path = self._target_path(stage, provider, model)
        target_data = self._read_json(path)
        if "cooldown_until" in target_data:
            del target_data["cooldown_until"]
            self._write_json_atomic(path, target_data)

        cooldowns = self._read_json(self._cooldowns_path)
        shared_key = self._shared_key(provider, model)
        if shared_key in cooldowns:
            del cooldowns[shared_key]
            self._write_json_atomic(self._cooldowns_path, cooldowns)


def resolve_model_spec(spec: str, default_provider: str = "gemini") -> tuple[str, str]:
    """Parse model specification string into canonical `(provider, model_name)` tuple."""
    cleaned = spec.strip()
    if ":" in cleaned:
        provider, model_name = cleaned.split(":", 1)
        return provider.strip().lower(), model_name.strip()
    lower = cleaned.lower()
    if lower.startswith("gemini"):
        return "gemini", cleaned
    if lower.startswith("ollama"):
        return "ollama", cleaned
    if lower.startswith("typesafe"):
        return "typesafe", cleaned
    return default_provider.strip().lower(), cleaned


def parse_stage_specs(
    stages: Sequence[str] | None,
    single_stage: str | None,
    *,
    stage_specs: Mapping[str, StageCalibrationSpec] = STAGE_SPECS,
) -> list[str]:
    """Expand stage flags supporting comma-separated values or repeated `--stages` flags."""
    raw_tokens: list[str] = []
    if stages:
        for entry in stages:
            raw_tokens.extend(part.strip() for part in entry.split(",") if part.strip())
    if single_stage is not None:
        raw_tokens.extend(part.strip() for part in single_stage.split(",") if part.strip())

    if not raw_tokens or "all" in [t.lower() for t in raw_tokens]:
        return list(stage_specs.keys())

    resolved: list[str] = []
    for token in raw_tokens:
        norm = token.lower().replace("-", "_")
        if norm not in stage_specs:
            valid = ", ".join(stage_specs.keys())
            raise ValueError(f"Unknown stage '{token}'. Valid stages: {valid}, all.")
        if norm not in resolved:
            resolved.append(norm)
    return resolved


def parse_model_specs(
    models: Sequence[str] | None,
    single_model: str | None,
    default_provider: str = "gemini",
    *,
    default_models: Sequence[str] = (),
) -> list[tuple[str, str]]:
    """Expand explicit model flags or supplied defaults into `(provider, model)` pairs."""
    raw_tokens: list[str] = []
    if models:
        for entry in models:
            raw_tokens.extend(part.strip() for part in entry.split(",") if part.strip())
    elif single_model is not None and single_model.strip():
        raw_tokens.append(single_model.strip())
    else:
        raw_tokens.extend(default_models)

    resolved: list[tuple[str, str]] = []
    for token in raw_tokens:
        pair = resolve_model_spec(token, default_provider=default_provider)
        if pair not in resolved:
            resolved.append(pair)
    return resolved


def sanitize_report_filename(stage: str, provider: str, model_name: str) -> str:
    """Generate clean filename slug for per-stage, per-model calibration report."""
    clean_model = model_name
    if clean_model.startswith(f"{provider}:"):
        clean_model = clean_model[len(provider) + 1 :]
    clean_model = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", clean_model)
    return f"llm_judge_{stage}_{provider}_{clean_model}.txt"


def compute_config_hash(
    spec: StageCalibrationSpec,
    items: list[dict[str, Any]],
    threshold: float,
    *,
    prompt_lookup: PromptTemplateLookup | None = None,
) -> str:
    """Compute SHA-256 hash over prompt template, criteria, threshold, and golden set items."""
    prompt_payload: dict[str, str] = {"system_prompt": "", "user_prompt": ""}
    if prompt_lookup is not None:
        try:
            prompt_payload = prompt_lookup(spec.prompt_key)
        except Exception as exc:  # noqa: BLE001
            logging.getLogger(__name__).debug(
                "Prompt lookup unavailable for config hash: %s",
                exc,
            )

    canonical = {
        "stage": spec.stage_name,
        "threshold": round(threshold, 6),
        "required_criteria": [c.value for c in spec.required_criteria],
        "prompt": prompt_payload,
        "items": items,
    }
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_stage_dataset(
    spec: StageCalibrationSpec,
    dataset_path: Path | None,
    seed_only: bool,
) -> list[dict[str, Any]]:
    """Load golden set JSON list for a stage or fall back to canonical seed items."""
    if seed_only:
        return [dict(item) for item in spec.seed_items]

    target_path = dataset_path if dataset_path is not None else spec.default_golden_set_path
    if not target_path.exists():
        return [dict(item) for item in spec.seed_items]

    loaded = json.loads(target_path.read_text(encoding="utf-8"))
    if isinstance(loaded, list) and loaded:
        return [dict(item) for item in loaded]
    return [dict(item) for item in spec.seed_items]


def evaluate_single_item(
    judge: LlmJudgePort,
    spec: StageCalibrationSpec,
    item: dict[str, Any],
) -> ItemEvaluationResult:
    """Invoke `judge.evaluate` for one golden set item uniformly across stages."""
    raw_text = item["input"]["raw_text"]
    candidate_text = item["input"]["candidate_text"]
    expected_verdict = str(item["expected_output"]["verdict"]).upper().strip()
    target_criterion_name = str(item.get("metadata", {}).get("criterion", "")).strip()

    context = EvaluationContext(
        stage_name=spec.stage_name,
        raw_text=raw_text,
        candidate_text=candidate_text,
        required_criteria=spec.required_criteria,
    )

    evaluation = judge.evaluate(context)
    global_actual = "PASS" if evaluation.passed else "FAIL"
    global_score = float(evaluation.overall_score)
    reasoning = evaluation.extract_critique()

    target_actual = global_actual
    target_score = global_score
    if target_criterion_name:
        try:
            crit_vo = JudgeCriterion(target_criterion_name)
            crit_score = evaluation.get_score(crit_vo)
            if crit_score is not None:
                target_actual = "PASS" if crit_score.passed else "FAIL"
                target_score = float(crit_score.score)
                if crit_score.reasoning:
                    reasoning = crit_score.reasoning
        except (ValueError, KeyError):
            pass

    return ItemEvaluationResult(
        actual=global_actual,
        expected=expected_verdict,
        score=global_score,
        reasoning=reasoning,
        target_actual=target_actual,
        target_score=target_score,
    )


def _record_item_into_results(
    results: CalibrationResultSet,
    item: dict[str, Any],
    eval_res: ItemEvaluationResult,
) -> str:
    """Record item verdict into global, target-isolated, and slice confusion matrices."""
    item_id = str(item.get("id", "item"))
    metadata = item.get("metadata", {})
    criterion = str(metadata.get("criterion", "general"))
    difficulty = str(metadata.get("difficulty", "typical"))

    if criterion not in results.by_criterion:
        results.by_criterion[criterion] = ConfusionMatrix()
    if difficulty not in results.by_difficulty:
        results.by_difficulty[difficulty] = ConfusionMatrix()

    results.overall.record(eval_res.expected, eval_res.actual)
    status_target = results.target_isolated.record(eval_res.expected, eval_res.target_actual)
    results.by_criterion[criterion].record(eval_res.expected, eval_res.target_actual)
    results.by_difficulty[difficulty].record(eval_res.expected, eval_res.target_actual)

    if eval_res.expected != eval_res.target_actual:
        results.disagreements.append(
            {
                "id": item_id,
                "criterion": criterion,
                "difficulty": difficulty,
                "expected": eval_res.expected,
                "actual_target": eval_res.target_actual,
                "actual_global": eval_res.actual,
                "score": eval_res.target_score,
                "anomaly": metadata.get("expected_anomaly", ""),
                "reasoning": eval_res.reasoning,
            }
        )
    return status_target


def _extract_cooldown_seconds(exc: BaseException) -> float | None:
    """Extract cooldown duration from domain/pool rate-limit errors carrying `retry_after_seconds`."""
    if isinstance(exc, RateLimitExceededError):
        retry_val = getattr(exc, "retry_after_seconds", None)
        if isinstance(retry_val, int | float):
            return max(0.0, float(retry_val))
    return None


def _is_transient_retryable_error(
    exc: Exception,
    *,
    is_quota_exhausted: Callable[[Exception], bool] | None = None,
) -> bool:
    """Identify transient server/network failures worth bounded retry backoff."""
    if isinstance(exc, RateLimitExceededError):
        return False
    if is_quota_exhausted is not None and is_quota_exhausted(exc):
        return False
    msg = str(exc).lower()
    if any(q in msg for q in ("resource_exhausted", "429", "quota exceeded", "too many requests")):
        return False
    transient_markers = ("503", "504", "unavailable", "timeout", "connection reset", "timed out")
    return any(marker in msg for marker in transient_markers)


def run_stage_calibration(
    judge: LlmJudgePort,
    spec: StageCalibrationSpec,
    items: list[dict[str, Any]],
    *,
    provider: str,
    model: str,
    config_hash: str,
    checkpoint_store: CalibrationCheckpointStore,
    delay: float = 4.2,
    jitter: float = 0.8,
    max_retry_wait: float = 60.0,
    is_quota_exhausted: Callable[[Exception], bool] | None = None,
    now_fn: Callable[[], float] = time.time,
    sleep_fn: Callable[[float], None] = time.sleep,
    emit_fn: Callable[[str], None] = print,
) -> CalibrationResultSet:
    """Run incremental checkpointed calibration for one `(stage, provider, model)` target."""
    active_until = checkpoint_store.active_cooldown_until(
        stage=spec.stage_name,
        provider=provider,
        model=model,
        now=now_fn(),
    )
    if active_until is not None:
        remaining = max(0.0, active_until - now_fn())
        raise CooldownActiveError(
            retry_after_seconds=remaining,
            message=f"Cooldown active for {provider}:{model} ({remaining:.0f}s remaining).",
        )

    results = CalibrationResultSet()
    completed_map = checkpoint_store.load_completed_items(
        stage=spec.stage_name,
        provider=provider,
        model=model,
        config_hash=config_hash,
    )

    pending_items: list[dict[str, Any]] = []
    for item in items:
        item_id = str(item.get("id", "item"))
        saved = completed_map.get(item_id)
        if saved is not None:
            saved_eval = ItemEvaluationResult(
                actual=str(saved["actual"]),
                expected=str(saved["expected"]),
                score=float(saved["score"]),
                reasoning=str(saved.get("reasoning", "")),
                target_actual=str(saved.get("target_actual", saved["actual"])),
                target_score=float(saved.get("target_score", saved["score"])),
            )
            _record_item_into_results(results, item, saved_eval)
            results.skipped_from_checkpoint += 1
        else:
            pending_items.append(item)

    total_items = len(items)
    emit_fn("\n" + "=" * 72)
    emit_fn(f"CALIBRATING [{spec.stage_name.upper()}] -> {provider}:{model}")
    if results.skipped_from_checkpoint > 0:
        emit_fn(
            f"Checkpoint resume: {results.skipped_from_checkpoint}/{total_items} restored, "
            f"{len(pending_items)} pending."
        )
    if delay > 0 and pending_items:
        emit_fn(f"Pacing: {delay:.1f}s base delay + up to {jitter:.1f}s jitter between calls")
    emit_fn("=" * 72)

    for idx, item in enumerate(pending_items, start=1):
        item_id = str(item.get("id", f"item_{idx}"))
        eval_res: ItemEvaluationResult | None = None
        short_cooldown_attempts = 0
        transient_attempts = 0

        while True:
            try:
                eval_res = evaluate_single_item(judge, spec, item)
                break
            except Exception as exc:
                retry_after = _extract_cooldown_seconds(exc)
                if retry_after is not None:
                    if retry_after <= max_retry_wait and short_cooldown_attempts < 5:
                        short_cooldown_attempts += 1
                        wait_s = max(retry_after, 0.5) + 0.5
                        emit_fn(
                            f"  [COOLDOWN WAIT {short_cooldown_attempts}/5] {item_id}: "
                            f"waiting {wait_s:.1f}s ({exc})"
                        )
                        sleep_fn(wait_s)
                        continue
                    until_ts = now_fn() + max(retry_after, max_retry_wait)
                    checkpoint_store.record_cooldown(spec.stage_name, provider, model, until_ts)
                    emit_fn(
                        f"  [COOLDOWN ABORT] {spec.stage_name} | {provider}:{model} parked for "
                        f"{retry_after:.0f}s (checkpoint saved)."
                    )
                    raise
                if (
                    _is_transient_retryable_error(exc, is_quota_exhausted=is_quota_exhausted)
                    and transient_attempts < 3
                ):
                    transient_attempts += 1
                    backoff = (2.0**transient_attempts) * 1.5
                    emit_fn(
                        f"  [RETRY {transient_attempts}/3] Transient error on '{item_id}': "
                        f"{exc}. Waiting {backoff:.1f}s..."
                    )
                    sleep_fn(backoff)
                    continue
                raise

        assert eval_res is not None
        checkpoint_store.record_item(
            stage=spec.stage_name,
            provider=provider,
            model=model,
            config_hash=config_hash,
            item_id=item_id,
            payload={
                "actual": eval_res.actual,
                "expected": eval_res.expected,
                "score": eval_res.score,
                "reasoning": eval_res.reasoning,
                "target_actual": eval_res.target_actual,
                "target_score": eval_res.target_score,
            },
        )
        status_target = _record_item_into_results(results, item, eval_res)
        results.evaluated_items += 1

        emit_fn(
            f"[{results.skipped_from_checkpoint + idx:02d}/{total_items:02d}] "
            f"[{item_id:<28}] Exp: {eval_res.expected:<4} | "
            f"Target: {eval_res.target_actual:<4} ({eval_res.target_score:.2f}) -> {status_target}"
        )

        if idx < len(pending_items) and (delay + jitter) > 0:
            sleep_fn(delay + random.uniform(0.0, jitter))

    checkpoint_store.clear_cooldown(spec.stage_name, provider, model)
    return results


def _format_matrix_2x2(title: str, m: ConfusionMatrix) -> str:
    lines = [
        "\n" + "=" * 80,
        title,
        "-" * 80,
        f"{'Ground Truth \\ Judge':<28} | {'Judge: PASS':<20} | {'Judge: FAIL':<20} | {'Total':<8}",
        "-" * 80,
        (
            f"{'PASS (Valid Output)':<28} | "
            f"{f'HIT (TP): {m.hit}':<20} | "
            f"{f'PEDANT (FN): {m.pedantismo_beta}':<20} | "
            f"{m.total_corretos:<8}"
        ),
        (
            f"{'FAIL (Defective Output)':<28} | "
            f"{f'PERMISSIVE (FP): {m.permissivo_alfa}':<20} | "
            f"{f'REJECT (TN): {m.rejeicao}':<20} | "
            f"{m.total_defeituosos:<8}"
        ),
        "-" * 80,
        (
            f"{'Total by Judge':<28} | {m.total_aprovados:<20} | "
            f"{m.total_reprovados:<20} | {m.total_valid:<8}"
        ),
        "=" * 80,
    ]
    return "\n".join(lines)


def generate_calibration_report(
    spec: StageCalibrationSpec,
    results: CalibrationResultSet,
    provider: str,
    model: str,
) -> str:
    """Build full Signal Detection Theory and slice calibration report."""
    target_m = results.target_isolated
    lines: list[str] = [
        "=" * 80,
        f"LLM JUDGE CALIBRATION REPORT ({spec.label.upper()})",
        "=" * 80,
        f"Timestamp:       {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Stage:           {spec.stage_name}",
        f"Provider:        {provider}",
        f"Model:           {model}",
        "Fallback Mode:   DISABLED (enable_fallback=False)",
        (
            f"Valid Items:     {target_m.total_valid} "
            f"(fresh={results.evaluated_items}, resumed={results.skipped_from_checkpoint})"
        ),
        _format_matrix_2x2(
            "2x2 CONFUSION MATRIX (ISOLATED TARGET CRITERION)",
            target_m,
        ),
        "\n" + "=" * 80,
        "15 SIGNAL DETECTION THEORY (SDT) METRICS (TARGET ISOLATED)",
        "-" * 80,
        f"{'Code':<4} {'Metric':<28} | {'Value':<10} | {'Diagnosis'}",
        "-" * 80,
    ]
    for info in target_m.get_all_metrics():
        lines.append(
            f"{info.code:<4} {info.name:<28} | {info.formatted_value:<10} | {info.diagnosis}"
        )

    lines.append(
        _format_matrix_2x2(
            "2x2 CONFUSION MATRIX (GLOBAL COMPOSITE GATE)",
            results.overall,
        )
    )

    lines.extend(
        [
            "\n" + "=" * 80,
            "SLICE BREAKDOWN BY CRITERION",
            "-" * 80,
            (
                f"{'Criterion':<34} | {'N':<4} | {'Acc':<6} | {'Prec':<6} | "
                f"{'Rec':<6} | {'F1':<6} | {'d-prime':<7}"
            ),
            "-" * 80,
        ]
    )
    for crit, m in results.by_criterion.items():
        lines.append(
            f"{crit:<34} | {m.total_valid:<4} | {m.accuracy * 100:5.1f}% | "
            f"{m.precision * 100:5.1f}% | {m.recall * 100:5.1f}% | {m.f1:5.3f} | {m.d_prime:6.2f}"
        )

    lines.extend(
        [
            "\n" + "=" * 80,
            "SLICE BREAKDOWN BY DIFFICULTY",
            "-" * 80,
            (
                f"{'Difficulty':<18} | {'N':<4} | {'Acc':<6} | {'Prec':<6} | "
                f"{'Rec':<6} | {'F1':<6} | {'d-prime':<7}"
            ),
            "-" * 80,
        ]
    )
    for diff, m in results.by_difficulty.items():
        lines.append(
            f"{diff:<18} | {m.total_valid:<4} | {m.accuracy * 100:5.1f}% | "
            f"{m.precision * 100:5.1f}% | {m.recall * 100:5.1f}% | {m.f1:5.3f} | {m.d_prime:6.2f}"
        )

    if results.disagreements:
        lines.extend(["\n" + "=" * 80, "DISAGREEMENTS", "-" * 80])
        for d in results.disagreements:
            lines.append(
                f"[{d['id']}] crit={d['criterion']} diff={d['difficulty']} "
                f"exp={d['expected']} got={d['actual_target']} ({d['score']:.2f}): "
                f"{str(d['reasoning'])[:180]}"
            )

    return "\n".join(lines) + "\n"


def save_calibration_report(
    spec: StageCalibrationSpec,
    results: CalibrationResultSet,
    output_path: Path,
    provider: str,
    model: str,
) -> Path:
    """Write full calibration report to disk cleanly."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_text = generate_calibration_report(spec, results, provider=provider, model=model)
    output_path.write_text(report_text, encoding="utf-8")
    return output_path


def print_benchmark_summary(
    summaries: Sequence[ModelBenchmarkSummary],
    *,
    emit_fn: Callable[[str], None] = print,
) -> None:
    """Print cross-stage, cross-model comparison table without polluting cooldown rows."""
    emit_fn("\n" + "=" * 116)
    emit_fn("UNIFIED LLM JUDGE CALIBRATION SUMMARY (ZERO-FALLBACK)")
    emit_fn("=" * 116)
    emit_fn(
        f"{'Stage':<12} | {'Model':<32} | {'Status':<11} | {'Done':<7} | "
        f"{'Acc':<6} | {'d-prime':<7} | {'F1':<6} | {'Prec':<6} | {'Rec':<6} | {'FPR':<6}"
    )
    emit_fn("-" * 116)
    for s in summaries:
        label = f"{s.provider}:{s.model}"
        done = f"{s.evaluated_total}/{s.dataset_total}"
        if s.status in ("COOLDOWN", "ERRO"):
            extra = (
                f"retry in {int(s.cooldown_remaining_s)}s"
                if s.status == "COOLDOWN"
                else s.error_message[:32]
            )
            emit_fn(f"{s.stage:<12} | {label:<32} | {s.status:<11} | {done:<7} | {extra}")
        else:
            emit_fn(
                f"{s.stage:<12} | {label:<32} | {s.status:<11} | {done:<7} | "
                f"{s.accuracy * 100:5.1f}% | {s.d_prime:7.2f} | {s.f1:6.3f} | "
                f"{s.precision * 100:5.1f}% | {s.recall * 100:5.1f}% | {s.alpha_fpr * 100:5.1f}%"
            )
    emit_fn("=" * 116 + "\n")


def run_calibration_suite(
    *,
    selected_stages: Sequence[str],
    selected_models: Sequence[tuple[str, str]],
    judge_factory: JudgeCalibrationFactory,
    stage_thresholds: Mapping[str, float],
    stage_specs: Mapping[str, StageCalibrationSpec] = STAGE_SPECS,
    dataset_path: Path | None = None,
    seed_only: bool = False,
    checkpoint_dir: Path = DEFAULT_CHECKPOINT_DIR,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    output_path: Path | None = None,
    delay: float = 4.2,
    jitter: float = 0.8,
    max_retry_wait: float = 60.0,
    prompt_lookup: PromptTemplateLookup | None = None,
    is_quota_exhausted: Callable[[Exception], bool] | None = None,
    now_fn: Callable[[], float] = time.time,
    sleep_fn: Callable[[float], None] = time.sleep,
    emit_fn: Callable[[str], None] = print,
) -> CalibrationSuiteOutcome:
    """Orchestrate zero-fallback calibration across selected stages and model targets."""
    if dataset_path is not None and len(selected_stages) > 1:
        raise ValueError("--dataset-path can only be used with a single --stage.")

    checkpoint_store = CalibrationCheckpointStore(checkpoint_dir=checkpoint_dir)
    summaries: list[ModelBenchmarkSummary] = []
    has_errors = False

    emit_fn(f"\nStages scheduled ({len(selected_stages)}): {', '.join(selected_stages)}")
    emit_fn(
        f"Models scheduled ({len(selected_models)}): "
        f"{', '.join(f'{p}:{m}' for p, m in selected_models)}"
    )

    for stage_name in selected_stages:
        spec = stage_specs[stage_name]
        items = load_stage_dataset(spec, dataset_path=dataset_path, seed_only=seed_only)
        active_threshold = stage_thresholds.get(stage_name, 0.75)
        config_hash = compute_config_hash(
            spec,
            items,
            active_threshold,
            prompt_lookup=prompt_lookup,
        )

        for prov, mod in selected_models:
            now_ts = now_fn()
            active_until = checkpoint_store.active_cooldown_until(
                stage=stage_name,
                provider=prov,
                model=mod,
                now=now_ts,
            )
            completed_count = len(
                checkpoint_store.load_completed_items(stage_name, prov, mod, config_hash)
            )
            if active_until is not None:
                rem = max(0.0, active_until - now_ts)
                emit_fn(
                    f"\n[COOLDOWN SKIP] {stage_name} | {prov}:{mod} in cooldown for "
                    f"{rem:.0f}s ({completed_count}/{len(items)} checkpointed)."
                )
                summaries.append(
                    ModelBenchmarkSummary(
                        stage=stage_name,
                        provider=prov,
                        model=mod,
                        status="COOLDOWN",
                        evaluated_total=completed_count,
                        dataset_total=len(items),
                        cooldown_remaining_s=rem,
                    )
                )
                continue

            try:
                # Zero-fallback enforced unconditionally to guarantee pure per-model telemetry.
                judge = judge_factory(
                    provider=prov,
                    model=mod,
                    threshold=active_threshold,
                    enable_fallback=False,
                )
                results = run_stage_calibration(
                    judge=judge,
                    spec=spec,
                    items=items,
                    provider=prov,
                    model=mod,
                    config_hash=config_hash,
                    checkpoint_store=checkpoint_store,
                    delay=delay,
                    jitter=jitter,
                    max_retry_wait=max_retry_wait,
                    is_quota_exhausted=is_quota_exhausted,
                    now_fn=now_fn,
                    sleep_fn=sleep_fn,
                    emit_fn=emit_fn,
                )
                tm = results.target_isolated
                status = (
                    "APROVADO"
                    if (tm.accuracy >= 0.85 and tm.permissivo_alfa == 0)
                    else "PRE-CALIB"
                    if tm.accuracy >= 0.80
                    else "REPROVADO"
                )
                single_target = len(selected_stages) == 1 and len(selected_models) == 1
                if output_path is not None:
                    report_dest = (
                        output_path
                        if single_target
                        else output_path / sanitize_report_filename(stage_name, prov, mod)
                    )
                else:
                    report_dest = reports_dir / sanitize_report_filename(stage_name, prov, mod)
                save_calibration_report(
                    spec=spec,
                    results=results,
                    output_path=report_dest,
                    provider=prov,
                    model=mod,
                )
                summaries.append(
                    ModelBenchmarkSummary(
                        stage=stage_name,
                        provider=prov,
                        model=mod,
                        status=status,
                        accuracy=tm.accuracy,
                        d_prime=tm.d_prime,
                        f1=tm.f1,
                        precision=tm.precision,
                        recall=tm.recall,
                        alpha_fpr=tm.alpha_fpr,
                        evaluated_total=tm.total_valid,
                        dataset_total=len(items),
                    )
                )
            except Exception as exc:  # noqa: BLE001
                retry_after = _extract_cooldown_seconds(exc)
                saved_after = len(
                    checkpoint_store.load_completed_items(stage_name, prov, mod, config_hash)
                )
                if retry_after is not None:
                    summaries.append(
                        ModelBenchmarkSummary(
                            stage=stage_name,
                            provider=prov,
                            model=mod,
                            status="COOLDOWN",
                            evaluated_total=saved_after,
                            dataset_total=len(items),
                            cooldown_remaining_s=retry_after,
                        )
                    )
                else:
                    has_errors = True
                    emit_fn(f"[ERROR] {stage_name} | {prov}:{mod} failed: {exc}")
                    summaries.append(
                        ModelBenchmarkSummary(
                            stage=stage_name,
                            provider=prov,
                            model=mod,
                            status="ERRO",
                            evaluated_total=saved_after,
                            dataset_total=len(items),
                            error_message=str(exc),
                        )
                    )

    print_benchmark_summary(summaries, emit_fn=emit_fn)
    return CalibrationSuiteOutcome(summaries=tuple(summaries), has_errors=has_errors)
