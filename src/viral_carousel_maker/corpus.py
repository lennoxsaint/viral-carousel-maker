"""Local-only private corpus importer.

The importer stores derived counts and heuristics, never raw source posts.
"""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any

from .virality import count_words, detect_weak_hook_opener, find_trigger_words


CORPUS_DIR = Path.home() / ".viral-carousel-maker" / "corpus"
SUPPORTED_SUFFIXES = {".md", ".txt", ".json", ".jsonl", ".csv"}


def import_private_corpus(source: str | Path, local_only: bool = True) -> dict[str, Any]:
    if not local_only:
        raise ValueError("Private corpus imports must use --local-only.")
    source_path = Path(source).expanduser()
    if not source_path.exists():
        raise FileNotFoundError(f"Corpus source not found: {source_path}")
    texts = list(_iter_texts(source_path))
    summary = summarize_corpus_texts(texts)
    summary["source_name"] = source_path.name
    summary["imported_at"] = datetime.now(UTC).isoformat()
    out_path = _summary_path(source_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary["summary_path"] = str(out_path)
    return summary


def summarize_corpus_texts(texts: list[str]) -> dict[str, Any]:
    hook_lengths: Counter[str] = Counter()
    weak_openers: Counter[str] = Counter()
    trigger_hits: Counter[str] = Counter()
    question_hooks = 0
    numeric_hooks = 0
    compressed_hooks = 0
    total_words = 0

    for text in texts:
        hook = _first_content_line(text)
        words = count_words(hook)
        total_words += count_words(text)
        bucket = "1-7" if words <= 7 else "8-12" if words <= 12 else "13-18" if words <= 18 else "19+"
        hook_lengths[bucket] += 1
        opener = detect_weak_hook_opener(hook)
        if opener:
            weak_openers[opener] += 1
        for hit in find_trigger_words(hook):
            trigger_hits[hit] += 1
        if "?" in hook:
            question_hooks += 1
        if any(char.isdigit() for char in hook):
            numeric_hooks += 1
        if words <= 12:
            compressed_hooks += 1

    post_count = len(texts)
    return {
        "post_count": post_count,
        "raw_posts_stored": False,
        "avg_words_per_post": round(total_words / post_count, 2) if post_count else 0,
        "hook_length_buckets": hook_lengths.most_common(),
        "weak_opener_counts": weak_openers.most_common(),
        "trigger_word_counts": trigger_hits.most_common(),
        "question_hook_rate": round(question_hooks / post_count, 4) if post_count else 0,
        "numeric_hook_rate": round(numeric_hooks / post_count, 4) if post_count else 0,
        "compressed_hook_rate": round(compressed_hooks / post_count, 4) if post_count else 0,
        "derived_rules": _derive_rules(post_count, weak_openers, question_hooks, compressed_hooks),
    }


def _iter_texts(path: Path) -> list[str]:
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
    texts: list[str] = []
    for file_path in files:
        if file_path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        data = file_path.read_text(encoding="utf-8", errors="ignore")
        if file_path.suffix.lower() == ".jsonl":
            for line in data.splitlines():
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = _json_text(value)
                if text:
                    texts.append(text)
        elif file_path.suffix.lower() == ".json":
            try:
                value = json.loads(data)
            except json.JSONDecodeError:
                value = data
            if isinstance(value, list):
                texts.extend(text for item in value if (text := _json_text(item)))
            else:
                text = _json_text(value)
                if text:
                    texts.append(text)
        else:
            chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", data) if chunk.strip()]
            texts.extend(chunks or [data.strip()])
    return [text for text in texts if text.strip()]


def _json_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("text", "post", "content", "caption", "body"):
            if value.get(key):
                return str(value[key])
    return ""


def _first_content_line(text: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip().strip("#-• ")
        if cleaned:
            return cleaned
    return text.strip()[:160]


def _derive_rules(
    post_count: int,
    weak_openers: Counter[str],
    question_hooks: int,
    compressed_hooks: int,
) -> list[str]:
    if not post_count:
        return ["No usable posts found; import a richer corpus before deriving rules."]
    rules = []
    if compressed_hooks / post_count >= 0.5:
        rules.append("Imported winners skew short; keep hooks under 12 words by default.")
    if question_hooks / post_count < 0.2:
        rules.append("Questions are rare in this corpus; default hooks to statements.")
    if weak_openers:
        rules.append("Track weak how-to/list openers separately and avoid them unless search intent matters.")
    rules.append("Use these as private local priors, not public proof claims.")
    return rules


def _summary_path(source_path: Path) -> Path:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in source_path.name.lower()).strip("-")
    return CORPUS_DIR / f"{slug or 'corpus'}-summary.json"
