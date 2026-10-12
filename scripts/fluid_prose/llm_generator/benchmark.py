#!/usr/bin/env python3
"""Benchmark and Evaluation Harness for Fluid Prose Generator Models.

Executes and measures candidate LLM generators (Gemini cloud API, Ollama local models)
against raw spoken transcripts, submitting generated fluid prose to the calibrated
canonical LLM Judge (Gemini 3.5 Flash Lite) across all 6 canonical criteria.

Each evaluated model writes its own independent, comprehensive report file
to disk (scripts/fluid_prose/llm_generator_{model}.txt) with zero unified tables,
preserving full traceability of candidate prose, statistical quality gates,
criterion-by-criterion compliance matrices, and per-sample judge evaluations.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - ADR-030: Stage Quality Gate & Evaluator-Retry Fabric
    - SPEC-015: Fluid Prose Quality Gates and Calibration Framework
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Ensure project root and src are in sys.path
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
for path in (str(SRC_DIR), str(REPO_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from cresmo.application.ports import LLMTransformationPort, PromptProviderPort
from cresmo.domain.value_objects.prompt import PromptKey
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
)
from cresmo.infrastructure.adapters.gemini_adapter import GeminiLLMAdapter
from cresmo.infrastructure.adapters.ollama_llm_adapter import OllamaLLMAdapter
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.factories.adapter_factory import build_prompt_provider
from cresmo.presentation.factories.judge_factory import build_llm_judge_adapter

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("benchmark_generators")

CANONICAL_CRITERIA: tuple[JudgeCriterion, ...] = (
    JudgeCriterion.ORALITY_REMOVAL,
    JudgeCriterion.SEMANTIC_FAITHFULNESS,
    JudgeCriterion.EPISTEMIC_CRITIQUE,
    JudgeCriterion.NER_PRESERVATION,
    JudgeCriterion.STRUCTURAL_COMPLIANCE,
    JudgeCriterion.AUTHORIAL_VOICE,
)

ALL_BENCHMARK_MODELS: list[str] = [
    "gemini:gemini-3.5-flash",
    "gemini:gemini-2.5-flash",
    "ollama:qwen2.5:latest",
    "ollama:gemma4:latest",
    "ollama:deepseek-r1:7b",
    "ollama:llama3:latest",
]


@dataclass(frozen=True)
class BenchmarkSample:
    """Raw transcript sample used as generator benchmark input."""

    sample_id: str
    channel_name: str
    content_title: str
    file_name: str
    raw_text: str
    criterion_focus: str = "general"
    expected_verdict: str | None = None


@dataclass
class SampleEvaluationResult:
    """Evaluation outcome for a single sample and model."""

    sample: BenchmarkSample
    candidate_text: str
    generation_latency_seconds: float
    judge_latency_seconds: float
    evaluation: JudgeEvaluation
    error: str | None = None


@dataclass
class CriterionStats:
    """Statistical summary for a single canonical criterion."""

    criterion_name: str
    total_evaluations: int
    passed_count: int
    failed_count: int
    pass_rate: float
    mean_score: float
    min_score: float
    max_score: float
    stdev_score: float


@dataclass
class ModelBenchmarkSummary:
    """Aggregated benchmark statistics and quality gates for a specific model."""

    provider: str
    model_name: str
    total_samples: int
    successful_runs: int
    passed_runs: int
    failed_runs: int
    pass_rate: float
    defect_rate: float
    mean_overall_score: float
    median_overall_score: float
    stdev_overall_score: float
    min_overall_score: float
    max_overall_score: float
    mean_generation_latency: float
    p50_generation_latency: float
    p95_generation_latency: float
    mean_judge_latency: float
    p50_judge_latency: float
    p95_judge_latency: float
    criteria_stats: dict[str, CriterionStats]
    sample_results: list[SampleEvaluationResult]


def parse_raw_transcript_file(file_path: Path) -> BenchmarkSample:
    """Extract metadata and speech body from a raw transcript markdown file."""
    content = file_path.read_text(encoding="utf-8")
    channel_name = file_path.parent.name if file_path.parent.name != "raw" else "YouTube"
    content_title = file_path.stem
    file_name = file_path.name

    raw_text = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter_raw = parts[1]
            raw_text = parts[2].strip()

            for line in frontmatter_raw.splitlines():
                line = line.strip()
                if line.startswith("channel_name:"):
                    channel_name = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("video_title:"):
                    content_title = line.split(":", 1)[1].strip().strip('"\'')

    return BenchmarkSample(
        sample_id=file_path.stem,
        channel_name=channel_name,
        content_title=content_title,
        file_name=file_name,
        raw_text=raw_text,
    )


def load_benchmark_samples(
    input_path: Path | None = None,
    limit: int | None = None,
) -> list[BenchmarkSample]:
    """Discover and load benchmark samples from files, directories, or golden set fallback."""
    samples: list[BenchmarkSample] = []

    # Case 1: Explicit file provided
    if input_path is not None and input_path.is_file():
        if input_path.suffix.lower() == ".json":
            data = json.loads(input_path.read_text(encoding="utf-8"))
            for item in data:
                raw_text = item.get("input", {}).get("raw_text") or item.get("raw_text", "")
                meta = item.get("metadata", {})
                expected = item.get("expected_output", {}).get("verdict")
                samples.append(
                    BenchmarkSample(
                        sample_id=item.get("id", f"sample_{len(samples) + 1}"),
                        channel_name=meta.get("channel_name", "Curated Corpus"),
                        content_title=meta.get("title", meta.get("video_id", item.get("id"))),
                        file_name=f"{item.get('id')}.txt",
                        raw_text=raw_text,
                        criterion_focus=meta.get("criterion", "general"),
                        expected_verdict=expected,
                    )
                )
        else:
            samples.append(parse_raw_transcript_file(input_path))

    # Case 2: Directory provided (or default current llm_generator/samples folder)
    target_dir = (
        input_path
        if (input_path is not None and input_path.is_dir())
        else (Path(__file__).resolve().parent / "samples")
    )
    if not samples and target_dir.exists():
        found_files = sorted(list(target_dir.rglob("*.md")) + list(target_dir.rglob("*.txt")))
        for f in found_files:
            if f.name in {"cookies.txt", "playlist.txt", "playlist-priority.txt", "index.txt"}:
                continue
            try:
                sample = parse_raw_transcript_file(f)
                if len(sample.raw_text.strip()) > 80:
                    samples.append(sample)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Skipping unparseable transcript '%s': %s", f, exc)

    # Case 3: Fallback to Golden Set items if data/raw has fewer than 2 transcripts
    if len(samples) < 2:
        golden_path = REPO_ROOT / "data" / "golden_sets" / "fluid_prose_golden_set.json"
        if golden_path.exists():
            data = json.loads(golden_path.read_text(encoding="utf-8"))
            seen_texts: set[str] = set()
            for item in data:
                raw = item.get("input", {}).get("raw_text", "").strip()
                if raw and raw not in seen_texts:
                    seen_texts.add(raw)
                    meta = item.get("metadata", {})
                    samples.append(
                        BenchmarkSample(
                            sample_id=item.get("id", f"golden_{len(samples) + 1}"),
                            channel_name=meta.get("channel_name", "Golden Set"),
                            content_title=meta.get("video_id", "Golden Transcript"),
                            file_name=f"{item.get('id')}.txt",
                            raw_text=raw,
                            criterion_focus=meta.get("criterion", "general"),
                            expected_verdict=item.get("expected_output", {}).get("verdict"),
                        )
                    )

    if limit is not None and limit > 0:
        samples = samples[:limit]

    return samples


def build_generator_adapter(
    provider: str,
    model_name: str,
    settings: CresmoSettings,
    temperature: float = 0.2,
) -> LLMTransformationPort:
    """Instantiate candidate generator LLM adapter."""
    prov = provider.lower().strip()
    if prov == "gemini":
        api_key = settings.gemini_api_key.get_secret_value()
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is required to test Gemini models. Set it in .env or environment."
            )
        return GeminiLLMAdapter(
            api_key=api_key,
            model_name=model_name,
            default_temperature=temperature,
        )

    if prov == "ollama":
        return OllamaLLMAdapter(
            base_url=settings.ollama_base_url,
            model=model_name,
            timeout_seconds=settings.ollama_timeout_seconds,
            default_temperature=temperature,
            num_predict=settings.ollama_num_predict,
            keep_alive=settings.ollama_keep_alive,
        )

    raise ValueError(
        f"Unsupported generator provider: '{provider}'. Supported: 'gemini', 'ollama'."
    )


def resolve_model_spec(spec: str) -> tuple[str, str]:
    """Parse 'provider:model' or auto-detect provider from model name."""
    spec = spec.strip()
    if ":" in spec:
        prefix, remainder = spec.split(":", 1)
        if prefix.lower() in {"gemini", "ollama"}:
            return prefix.lower(), remainder

    # Auto-detection heuristic
    if spec.lower().startswith("gemini"):
        return "gemini", spec

    return "ollama", spec


def sanitize_filename(provider: str, model_name: str) -> str:
    """Convert model name or tag to clean, readable filename string."""
    clean_model = model_name
    if clean_model.startswith(f"{provider}:"):
        clean_model = clean_model[len(provider) + 1 :]
    clean_model = clean_model.replace(":", "_").replace("/", "_")
    clean_model = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", clean_model)
    return f"{provider}_{clean_model}" if not clean_model.startswith(provider) else clean_model


def calculate_percentile(data: list[float], percentile: float) -> float:
    """Calculate arbitrary percentile from list of floats."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = int(len(sorted_data) * (percentile / 100.0))
    idx = min(idx, len(sorted_data) - 1)
    return sorted_data[idx]


def run_benchmark_for_model(
    provider: str,
    model_name: str,
    samples: list[BenchmarkSample],
    settings: CresmoSettings,
    prompt_provider: PromptProviderPort,
    judge_adapter: Any,
    temperature: float = 0.2,
    pacing_seconds: float = 1.0,
) -> ModelBenchmarkSummary:
    """Execute generator transformations and judge evaluations for a single model."""
    generator = build_generator_adapter(
        provider=provider,
        model_name=model_name,
        settings=settings,
        temperature=temperature,
    )

    results: list[SampleEvaluationResult] = []
    print(f"\n{'=' * 75}")
    print(f"🚀 INICIANDO BENCHMARK DO GERADOR: [{provider.upper()}] {model_name}")
    print(f"📊 Total de Amostras: {len(samples)} | Temperatura: {temperature}")
    print(f"{'=' * 75}")

    for idx, sample in enumerate(samples, start=1):
        chat_prompt = prompt_provider.get_prompt(
            PromptKey.FLUID_PROSE,
            channel_name=sample.channel_name,
            file_name=sample.file_name,
            raw_text=sample.raw_text,
            language=settings.language,
        )

        t_gen_start = time.perf_counter()
        candidate_text = ""
        gen_error: str | None = None
        try:
            candidate_text = generator.transform(prompt=chat_prompt, temperature=temperature)
        except Exception as exc:  # noqa: BLE001
            gen_error = f"Generator Error: {exc}"
            logger.error("Falha na geração da amostra '%s': %s", sample.sample_id, exc)

        t_gen_end = time.perf_counter()
        gen_latency = t_gen_end - t_gen_start

        t_judge_start = time.perf_counter()
        eval_result: JudgeEvaluation
        if gen_error or not candidate_text.strip():
            eval_result = JudgeEvaluation(
                target_stage="fluid_prose",
                passed=False,
                overall_score=0.0,
                criteria_scores=tuple(
                    CriterionScore(
                        criterion=c,
                        score=0.0,
                        passed=False,
                        reasoning=f"Geração abortada ou vazia: {gen_error}",
                    )
                    for c in CANONICAL_CRITERIA
                ),
                provider="gemini_judge",
                latency_ms=0.0,
            )
            judge_latency = 0.0
        else:
            context = EvaluationContext(
                stage_name="fluid_prose",
                raw_text=sample.raw_text,
                candidate_text=candidate_text,
                required_criteria=CANONICAL_CRITERIA,
            )
            eval_result = judge_adapter.evaluate(context)
            t_judge_end = time.perf_counter()
            judge_latency = t_judge_end - t_judge_start

        status_str = "✓ PASS" if eval_result.passed else "✗ FAIL"
        score_str = f"{eval_result.overall_score:.2f}"
        print(
            f"[{idx:02d}/{len(samples):02d}] Amostra: {sample.sample_id:<25} | "
            f"Gen: {gen_latency:5.1f}s | Judge: {judge_latency:4.1f}s | "
            f"Nota: {score_str} ({status_str})"
        )

        results.append(
            SampleEvaluationResult(
                sample=sample,
                candidate_text=candidate_text,
                generation_latency_seconds=gen_latency,
                judge_latency_seconds=judge_latency,
                evaluation=eval_result,
                error=gen_error,
            )
        )

        if pacing_seconds > 0:
            time.sleep(pacing_seconds)

    # Statistical Aggregation
    total_samples = len(results)
    successful_runs = sum(1 for r in results if r.error is None and r.candidate_text.strip())
    passed_runs = sum(1 for r in results if r.evaluation.passed)
    failed_runs = total_samples - passed_runs
    pass_rate = (passed_runs / total_samples * 100.0) if total_samples > 0 else 0.0
    defect_rate = (failed_runs / total_samples * 100.0) if total_samples > 0 else 0.0

    overall_scores = [r.evaluation.overall_score for r in results]
    gen_latencies = [r.generation_latency_seconds for r in results]
    judge_latencies = [r.judge_latency_seconds for r in results]

    mean_overall = statistics.mean(overall_scores) if overall_scores else 0.0
    median_overall = statistics.median(overall_scores) if overall_scores else 0.0
    stdev_overall = statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0.0
    min_overall = min(overall_scores) if overall_scores else 0.0
    max_overall = max(overall_scores) if overall_scores else 0.0

    mean_gen_lat = statistics.mean(gen_latencies) if gen_latencies else 0.0
    p50_gen_lat = calculate_percentile(gen_latencies, 50.0)
    p95_gen_lat = calculate_percentile(gen_latencies, 95.0)

    mean_judge_lat = statistics.mean(judge_latencies) if judge_latencies else 0.0
    p50_judge_lat = calculate_percentile(judge_latencies, 50.0)
    p95_judge_lat = calculate_percentile(judge_latencies, 95.0)

    # Per-Criterion Breakdown
    criteria_stats: dict[str, CriterionStats] = {}
    for crit in CANONICAL_CRITERIA:
        crit_scores = [
            cs.score for r in results for cs in r.evaluation.criteria_scores if cs.criterion == crit
        ]
        crit_passes = sum(
            1 for r in results for cs in r.evaluation.criteria_scores if cs.criterion == crit and cs.passed
        )
        total_crit = len(crit_scores)
        crit_fails = total_crit - crit_passes
        crit_pass_rate = (crit_passes / total_crit * 100.0) if total_crit > 0 else 0.0
        crit_mean = statistics.mean(crit_scores) if crit_scores else 0.0
        crit_min = min(crit_scores) if crit_scores else 0.0
        crit_max = max(crit_scores) if crit_scores else 0.0
        crit_stdev = statistics.stdev(crit_scores) if len(crit_scores) > 1 else 0.0

        criteria_stats[crit.value] = CriterionStats(
            criterion_name=crit.value,
            total_evaluations=total_crit,
            passed_count=crit_passes,
            failed_count=crit_fails,
            pass_rate=crit_pass_rate,
            mean_score=crit_mean,
            min_score=crit_min,
            max_score=crit_max,
            stdev_score=crit_stdev,
        )

    return ModelBenchmarkSummary(
        provider=provider,
        model_name=model_name,
        total_samples=total_samples,
        successful_runs=successful_runs,
        passed_runs=passed_runs,
        failed_runs=failed_runs,
        pass_rate=pass_rate,
        defect_rate=defect_rate,
        mean_overall_score=mean_overall,
        median_overall_score=median_overall,
        stdev_overall_score=stdev_overall,
        min_overall_score=min_overall,
        max_overall_score=max_overall,
        mean_generation_latency=mean_gen_lat,
        p50_generation_latency=p50_gen_lat,
        p95_generation_latency=p95_gen_lat,
        mean_judge_latency=mean_judge_lat,
        p50_judge_latency=p50_judge_lat,
        p95_judge_latency=p95_judge_lat,
        criteria_stats=criteria_stats,
        sample_results=results,
    )


def format_model_report(summary: ModelBenchmarkSummary) -> str:
    """Format exhaustive, self-contained report text with quality gates and full statistics."""
    lines: list[str] = [
        "=" * 90,
        f"RELATÓRIO DE BENCHMARK INDIVIDUAL - GERADOR FLUID PROSE: {summary.model_name}",
        "=" * 90,
        f"Data/Hora de Execução:   {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Provedor do Modelo:      {summary.provider.upper()}",
        f"Modelo Gerador Avaliado: {summary.model_name}",
        "Juiz de Avaliação:       Gemini 3.5 Flash Lite Calibrado (Prompt: cresmo-llm-judge)",
        "Threshold de Aprovação:  >= 0.8000 (ADR-039 Canonical Stage Quality Gate)",
        "",
        "=" * 90,
        "1. TABELA DE MÉTRICAS EXECUTIVAS E PRODUCTION QUALITY GATES",
        "=" * 90,
        f"{'Métrica Avaliada':<34} | {'Valor Observado':<16} | {'Meta / Threshold Canônico':<32}",
        "-" * 90,
        f"{'Total de Amostras Avaliadas':<34} | {summary.total_samples:<16} | {'N/A':<32}",
        f"{'Gerações Concluídas com Sucesso':<34} | {summary.successful_runs:<16} | {'100% de Completude':<32}",
        f"{'Aprovações Globais (Pass)':<34} | {summary.passed_runs:<16} | {'N/A':<32}",
        f"{'Reprovações Globais (Fail)':<34} | {summary.failed_runs:<16} | {'0 (Zero Defeitos)':<32}",
        f"{'Taxa de Aprovação (Pass Rate)':<34} | {summary.pass_rate:5.1f}%{'':<10} | {'>= 80.0% (Recomendado >= 90%)':<32}",
        f"{'Taxa de Defeito (Defect Rate)':<34} | {summary.defect_rate:5.1f}%{'':<10} | {'<= 10.0% (Shadow Mode Target)':<32}",
        f"{'Score Médio Geral (Overall Mean)':<34} | {summary.mean_overall_score:6.4f}{'':<10} | {'>= 0.8000':<32}",
        f"{'Mediana do Score Geral (Median)':<34} | {summary.median_overall_score:6.4f}{'':<10} | {'>= 0.8000':<32}",
        f"{'Desvio Padrão do Score (StDev)':<34} | {summary.stdev_overall_score:6.4f}{'':<10} | {'Baixa variância (< 0.15)':<32}",
        f"{'Score Mínimo Observado (Min)':<34} | {summary.min_overall_score:6.4f}{'':<10} | {'>= 0.7000 (Sem colapsos)':<32}",
        f"{'Score Máximo Observado (Max)':<34} | {summary.max_overall_score:6.4f}{'':<10} | {'1.0000':<32}",
        "-" * 90,
        f"{'Latência Média de Geração (Mean)':<34} | {summary.mean_generation_latency:5.2f}s{'':<10} | {'Throughput de Ingestão':<32}",
        f"{'Latência de Geração P50 (Mediana)':<34} | {summary.p50_generation_latency:5.2f}s{'':<10} | {'Operação Típica':<32}",
        f"{'Latência de Geração P95 (Tail)':<34} | {summary.p95_generation_latency:5.2f}s{'':<10} | {'Limite de Timeout':<32}",
        f"{'Latência Média do Juiz (Mean)':<34} | {summary.mean_judge_latency:5.2f}s{'':<10} | {'<= 6.00s (SLO ADR-039)':<32}",
        f"{'Latência do Juiz P95 (Tail)':<34} | {summary.p95_judge_latency:5.2f}s{'':<10} | {'<= 6.00s (SLO ADR-039)':<32}",
        "=" * 90,
        "",
        "=" * 90,
        "2. MATRIZ DE CONFORMIDADE E BREAKDOWN POR CRITÉRIO CANÔNICO",
        "=" * 90,
        f"{'Critério Canônico':<24} | {'Total':<5} | {'Pass':<5} | {'Fail':<5} | {'Pass Rate':<9} | {'Score Méd':<9} | {'Min':<6} | {'StDev':<6} | {'Status'}",
        "-" * 90,
    ]

    for crit_name, cs in summary.criteria_stats.items():
        status_flag = "[✓ PASS]" if cs.pass_rate >= 80.0 else "[✗ FAIL]"
        lines.append(
            f"{crit_name:<24} | {cs.total_evaluations:<5} | {cs.passed_count:<5} | "
            f"{cs.failed_count:<5} | {cs.pass_rate:6.1f}%   | {cs.mean_score:8.4f}  | "
            f"{cs.min_score:5.2f}  | {cs.stdev_score:5.2f}  | {status_flag}"
        )

    lines.extend([
        "=" * 90,
        "",
        "=" * 90,
        "3. DETALHAMENTO ITEM A ITEM (TRANSCRIÇÃO, PROSA GERADA E VEREDITO DO JUIZ)",
        "=" * 90,
        "",
    ])

    for idx, r in enumerate(summary.sample_results, start=1):
        status_tag = "APROVADO [PASS]" if r.evaluation.passed else "REPROVADO [FAIL]"
        lines.extend([
            "-" * 90,
            f"AMOSTRA #{idx:02d} | ID: {r.sample.sample_id} | Foco: {r.sample.criterion_focus}",
            f"Canal: {r.sample.channel_name} | Título: {r.sample.content_title}",
            f"Veredito do Juiz: {status_tag} | Overall Score: {r.evaluation.overall_score:.4f}",
            f"Tempo Geração: {r.generation_latency_seconds:.2f}s | Tempo Avaliação: {r.judge_latency_seconds:.2f}s",
            "-" * 90,
            "",
            "--- [ENTRADA: TRANSCRIÇÃO BRUTA (RAW TEXT)] ---",
            r.sample.raw_text.strip(),
            "",
            "--- [SAÍDA: PROSA FLUIDA GERADA PELO MODELO (CANDIDATE TEXT)] ---",
            r.candidate_text.strip() if r.candidate_text.strip() else "[GERAÇÃO VAZIA OU FALHOU]",
            "",
            "--- [AVALIAÇÃO DETALHADA DO JUIZ POR CRITÉRIO] ---",
        ])

        for score in r.evaluation.criteria_scores:
            c_status = "PASS" if score.passed else "FAIL"
            lines.append(
                f"  [{c_status}] {score.criterion.value} (Nota: {score.score:.2f}):\n"
                f"         Justificativa: {score.reasoning}"
            )
            if score.improvement_suggestion:
                lines.append(f"         Sugestão:      {score.improvement_suggestion}")

        if r.error:
            lines.extend(["", f"  [ERRO DO GERADOR]: {r.error}"])

        lines.extend(["", ""])

    lines.extend([
        "=" * 90,
        "FIM DO RELATÓRIO DO MODELO",
        "=" * 90,
    ])

    return "\n".join(lines)


def main() -> int:
    """CLI Entrypoint for generator benchmark execution."""
    parser = argparse.ArgumentParser(
        description="Benchmark and evaluate candidate generator LLMs for Fluid Prose against canonical judge."
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=ALL_BENCHMARK_MODELS,
        help=(
            "List of model identifiers to test sequentially (default: all canonical models - "
            "'gemini:gemini-3.5-flash' 'gemini:gemini-2.5-flash' 'ollama:qwen2.5:latest' "
            "'ollama:gemma4:latest' 'ollama:deepseek-r1:7b' 'ollama:llama3:latest' or 'all')"
        ),
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to specific transcript file or directory of raw transcripts (default: scripts/fluid_prose/llm_generator/samples).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of transcript samples to evaluate per model.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "scripts" / "fluid_prose",
        help="Directory to save individual model report files (default: scripts/fluid_prose).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature for generator models (default: 0.2).",
    )
    parser.add_argument(
        "--pacing",
        type=float,
        default=1.0,
        help="Inter-request sleep delay in seconds to respect rate limits (default: 1.0).",
    )

    args = parser.parse_args()
    settings = CresmoSettings()
    settings.ensure_directories()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Propagate Langfuse environment variables to silence client initialization warnings
    if settings.langfuse_public_key:
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
    if settings.langfuse_secret_key.get_secret_value():
        os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key.get_secret_value()
    if settings.langfuse_host:
        os.environ["LANGFUSE_HOST"] = settings.langfuse_host

    # 1. Resolve Target Models
    raw_models = args.models
    if "all" in [m.lower() for m in raw_models]:
        raw_models = list(ALL_BENCHMARK_MODELS)

    # 2. Load Samples
    samples = load_benchmark_samples(input_path=args.input, limit=args.limit)
    if not samples:
        logger.error("Nenhuma amostra de transcrição encontrada para benchmark!")
        return 1

    print(f"📦 Amostras carregadas para o benchmark: {len(samples)}")
    for i, s in enumerate(samples, 1):
        print(f"   {i:2d}. [{s.sample_id}] {s.content_title} ({len(s.raw_text)} caracteres)")

    print(f"\n🎯 Modelos agendados para avaliação ({len(raw_models)}):")
    for i, m in enumerate(raw_models, 1):
        print(f"   {i}. {m}")
    print()

    # 3. Instantiate Prompt Provider & Calibrated Judge Adapter
    prompt_provider = build_prompt_provider(settings=settings)
    judge_adapter = build_llm_judge_adapter(settings=settings, prompt_provider=prompt_provider)

    # 4. Iterate Over Models
    for spec in raw_models:
        provider, model_name = resolve_model_spec(spec)
        filename_slug = sanitize_filename(provider, model_name)
        output_file = args.output_dir / f"llm_generator_{filename_slug}.txt"

        try:
            summary = run_benchmark_for_model(
                provider=provider,
                model_name=model_name,
                samples=samples,
                settings=settings,
                prompt_provider=prompt_provider,
                judge_adapter=judge_adapter,
                temperature=args.temperature,
                pacing_seconds=args.pacing,
            )

            report_text = format_model_report(summary)
            output_file.write_text(report_text, encoding="utf-8")

            print("\n💾 Relatório individual salvo com sucesso em:")
            print(f"   👉 {output_file}")
            print(
                f"   [Resultado: {summary.passed_runs}/{summary.total_samples} aprovados "
                f"({summary.pass_rate:.1f}%) | Defeito: {summary.defect_rate:.1f}% | "
                f"Score Médio: {summary.mean_overall_score:.4f}]\n"
            )

        except Exception as exc:  # noqa: BLE001
            logger.error("Erro ao executar benchmark para o modelo '%s': %s", spec, exc)

    print("🏁 Todos os benchmarks solicitados foram concluídos!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
