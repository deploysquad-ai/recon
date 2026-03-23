"""Gemini embedding-based semantic linking for recon-core.

Provides embed_nodes() and find_similar() to propose wikilinks by cosine similarity.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path

from .errors import MissingAPIKeyError, EmbeddingError, EmbeddingCacheMissingError

_CACHE_FILENAME = ".graph/embeddings.json"


def _import_genai():
    try:
        import google.generativeai as genai
        return genai
    except ImportError:
        raise ImportError(
            "Embedding requires the 'embed' extra: "
            "pip install 'deploysquad-recon-core[embed]'"
        )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _embedding_text(node_data: dict) -> str:
    """Build the text string used for embedding a node.

    Format: "{type}: {name}. {description_text}"

    - project nodes: description_text = description frontmatter field (or "" if absent)
    - user-story nodes: description_text = first non-empty line of body
    - all other types: description_text = ""
    """
    fm = node_data.get("frontmatter", {})
    node_type = fm.get("type", "")
    name = fm.get("name", "")

    if node_type == "project":
        description_text = fm.get("description", "")
    elif node_type == "user-story":
        body = node_data.get("body", "") or ""
        description_text = ""
        for line in body.splitlines():
            stripped = line.strip()
            if stripped:
                description_text = stripped
                break
    else:
        description_text = ""

    return f"{node_type}: {name}. {description_text}"


def _content_hash(text: str) -> str:
    """SHA-256 of text, truncated to 8 hex chars."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Standard cosine similarity. Returns 0.0 if either norm is zero."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _cache_key(relative_path: str, text: str) -> str:
    """Build cache key from relative path and content hash."""
    return f"{relative_path}:{_content_hash(text)}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def embed_nodes(project_dir: Path, api_key: str | None = None) -> dict:
    """Embed all nodes in the vault using Gemini text-embedding-004.

    Args:
        project_dir: Root directory of the project vault.
        api_key: Gemini API key. Falls back to GEMINI_API_KEY env var.

    Returns:
        {"embedded": N, "cached": N, "skipped": N}

    Raises:
        MissingAPIKeyError: No API key available.
        EmbeddingError: API failure during embedding (cache NOT written).
    """
    genai = _import_genai()

    # Resolve API key
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise MissingAPIKeyError(
            "GEMINI_API_KEY not set and no api_key argument provided."
        )

    # Import directly from submodules to avoid circular imports via __init__.py
    from deploysquad_recon_core import list_nodes, get_node

    # Configure Gemini
    genai.configure(api_key=key)

    project_dir = Path(project_dir)
    cache_path = project_dir / _CACHE_FILENAME
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing cache
    existing_cache: dict[str, list[float]] = {}
    if cache_path.exists():
        try:
            existing_cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing_cache = {}

    nodes = list_nodes(project_dir)

    embedded = 0
    cached = 0
    skipped = 0

    # Collect new embeddings in memory (all-or-nothing)
    new_entries: dict[str, list[float]] = {}

    for node_info in nodes:
        file_path = node_info["file_path"]
        relative_path = str(file_path.relative_to(project_dir))

        try:
            node_data = get_node(file_path)
        except Exception:
            skipped += 1
            continue

        fm = node_data.get("frontmatter", {})
        if not fm.get("name"):
            skipped += 1
            continue

        text = _embedding_text(node_data)
        key_str = _cache_key(relative_path, text)

        if key_str in existing_cache:
            cached += 1
            continue

        # Need to embed — call API
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
            )
            vector = result["embedding"]
        except Exception as exc:
            raise EmbeddingError(
                f"API failure while embedding '{relative_path}': {exc}"
            ) from exc

        new_entries[key_str] = vector
        embedded += 1

    # All-or-nothing write: merge new entries into existing cache and write
    merged_cache = {**existing_cache, **new_entries}
    cache_path.write_text(
        json.dumps(merged_cache, indent=None), encoding="utf-8"
    )

    return {"embedded": embedded, "cached": cached, "skipped": skipped}


def find_similar(
    node_path: Path,
    project_dir: Path,
    top_k: int = 5,
    threshold: float = 0.75,
) -> list[tuple[Path, float]]:
    """Find semantically similar nodes using cached Gemini embeddings.

    Args:
        node_path: Absolute path to the source node.
        project_dir: Root directory of the project vault.
        top_k: Maximum results to return.
        threshold: Minimum cosine similarity score.

    Returns:
        [(absolute_path, score), ...] sorted descending, max top_k, all >= threshold.
        Excludes the source node itself and nodes already in its outbound wikilinks.

    Raises:
        EmbeddingCacheMissingError: Cache does not exist — run embed_nodes first.
    """
    project_dir = Path(project_dir)
    node_path = Path(node_path)
    cache_path = project_dir / _CACHE_FILENAME

    if not cache_path.exists():
        raise EmbeddingCacheMissingError(
            f"No embeddings cache found at {cache_path}. Run embed_nodes() first."
        )

    cache: dict[str, list[float]] = json.loads(cache_path.read_text(encoding="utf-8"))

    # Import directly from submodules to avoid circular imports via __init__.py
    from deploysquad_recon_core import get_node
    from .vault.paths import get_type_display_name

    # Get source node data
    source_node = get_node(node_path)
    source_text = _embedding_text(source_node)
    source_rel = str(node_path.relative_to(project_dir))
    source_key = _cache_key(source_rel, source_text)

    # Get source embedding
    source_vector = cache.get(source_key)
    if source_vector is None:
        # Try to find any key with matching path prefix
        for k, v in cache.items():
            if k.startswith(source_rel + ":"):
                source_vector = v
                break

    if source_vector is None:
        # Source node not yet embedded — return empty list without error.
        # Call embed_nodes() to populate the cache first.
        return []

    # Collect all wikilinks from source frontmatter (all fields)
    source_fm = source_node.get("frontmatter", {})
    existing_wikilinks: set[str] = set()
    _wikilink_re = re.compile(r"\[\[([^\]]+)\]\]")
    for field_value in source_fm.values():
        if isinstance(field_value, str):
            for match in _wikilink_re.finditer(field_value):
                existing_wikilinks.add(f"[[{match.group(1)}]]")
        elif isinstance(field_value, list):
            for item in field_value:
                if isinstance(item, str):
                    for match in _wikilink_re.finditer(item):
                        existing_wikilinks.add(f"[[{match.group(1)}]]")

    results: list[tuple[Path, float]] = []

    for cache_key_str, vector in cache.items():
        # Extract relative path from cache key (format: "rel/path.md:8charhash")
        # The relative path is everything before the last ":xxxxxxxx" (8-char hex hash)
        # Use rsplit with maxsplit=1 since the hash portion is always ":8hexchars" at end
        colon_idx = cache_key_str.rfind(":")
        if colon_idx == -1:
            continue
        candidate_rel = cache_key_str[:colon_idx]
        candidate_abs = project_dir / candidate_rel

        # Exclude source itself
        if candidate_rel == source_rel:
            continue

        # Compute similarity
        score = _cosine_similarity(source_vector, vector)
        if score < threshold:
            continue

        # Check if already linked: build expected wikilink for candidate
        # Parse filename to get type and name
        filename = candidate_abs.name
        stem = filename[:-3] if filename.endswith(".md") else filename
        if " - " in stem:
            display, cand_name = stem.split(" - ", 1)
            # Derive type from display name
            from .vault.paths import _DISPLAY_TO_TYPE
            cand_type = _DISPLAY_TO_TYPE.get(display)
            if cand_type:
                display_name = get_type_display_name(cand_type)
                wikilink_str = f"[[{display_name} - {cand_name}]]"
                if wikilink_str in existing_wikilinks:
                    continue

        if candidate_abs.exists():
            results.append((candidate_abs, score))

    # Sort descending by score and limit to top_k
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]
