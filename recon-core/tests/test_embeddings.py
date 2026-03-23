"""Tests for Gemini embedding-based semantic linking."""
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from deploysquad_recon_core.errors import (
    MissingAPIKeyError,
    EmbeddingError,
    EmbeddingCacheMissingError,
    ReconCoreError,
)
from deploysquad_recon_core.embeddings import _embedding_text, _content_hash, _cosine_similarity


FAKE_EMBEDDING = [0.1, 0.2, 0.3]


@pytest.fixture
def vault_dir(tmp_path):
    """Minimal vault with one project node and one goal node."""
    import deploysquad_recon_core as rc
    proj_dir = tmp_path / "test-project"
    proj_dir.mkdir()
    rc.create_node("project", {"name": "Test Project", "description": "A productivity app that helps users manage their daily tasks", "status": "draft"}, proj_dir)
    rc.create_node(
        "goal",
        {
            "name": "Fast Login",
            "status": "draft",
            "belongs_to": "[[Project - Test Project]]",
        },
        proj_dir,
    )
    return proj_dir


# ---------------------------------------------------------------------------
# TestErrorTypes
# ---------------------------------------------------------------------------

class TestErrorTypes:
    def test_missing_api_key_error_is_recon_core_error(self):
        err = MissingAPIKeyError("no key")
        assert isinstance(err, ReconCoreError)

    def test_embedding_error_is_recon_core_error(self):
        err = EmbeddingError("api failed")
        assert isinstance(err, ReconCoreError)

    def test_embedding_cache_missing_error_is_recon_core_error(self):
        err = EmbeddingCacheMissingError("cache missing")
        assert isinstance(err, ReconCoreError)


# ---------------------------------------------------------------------------
# TestEmbeddingText
# ---------------------------------------------------------------------------

class TestEmbeddingText:
    def test_project_node_uses_description_field(self):
        node_data = {
            "frontmatter": {"type": "project", "name": "MyProject", "description": "A great project"},
            "body": "",
        }
        text = _embedding_text(node_data)
        assert text == "project: MyProject. A great project"

    def test_project_node_missing_description_uses_empty(self):
        node_data = {
            "frontmatter": {"type": "project", "name": "MyProject"},
            "body": "",
        }
        text = _embedding_text(node_data)
        assert text == "project: MyProject. "

    def test_user_story_uses_first_nonempty_body_line(self):
        node_data = {
            "frontmatter": {"type": "user-story", "name": "Login Flow"},
            "body": "\n\nAs a user I want to log in\nSo that I can access my account",
        }
        text = _embedding_text(node_data)
        assert text == "user-story: Login Flow. As a user I want to log in"

    def test_user_story_empty_body_uses_empty_string(self):
        node_data = {
            "frontmatter": {"type": "user-story", "name": "Empty Story"},
            "body": "",
        }
        text = _embedding_text(node_data)
        assert text == "user-story: Empty Story. "

    def test_other_type_uses_empty_description(self):
        node_data = {
            "frontmatter": {"type": "feature", "name": "Login", "description": "Should be ignored"},
            "body": "Some body text",
        }
        text = _embedding_text(node_data)
        assert text == "feature: Login. "

    def test_module_type_uses_empty_description(self):
        node_data = {
            "frontmatter": {"type": "module", "name": "Auth"},
            "body": "Module body",
        }
        text = _embedding_text(node_data)
        assert text == "module: Auth. "


# ---------------------------------------------------------------------------
# TestContentHash
# ---------------------------------------------------------------------------

class TestContentHash:
    def test_returns_8_hex_chars(self):
        h = _content_hash("hello world")
        assert len(h) == 8
        assert all(c in "0123456789abcdef" for c in h)

    def test_deterministic(self):
        assert _content_hash("same text") == _content_hash("same text")

    def test_different_text_different_hash(self):
        assert _content_hash("text a") != _content_hash("text b")


# ---------------------------------------------------------------------------
# TestCosineSimilarity
# ---------------------------------------------------------------------------

class TestCosineSimilarity:
    def test_identical_vectors_return_1(self):
        v = [1.0, 0.0, 0.0]
        assert abs(_cosine_similarity(v, v) - 1.0) < 1e-6

    def test_orthogonal_vectors_return_0(self):
        assert abs(_cosine_similarity([1.0, 0.0], [0.0, 1.0])) < 1e-6

    def test_zero_vector_returns_0(self):
        assert _cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0

    def test_typical_similarity(self):
        a = [1.0, 2.0, 3.0]
        b = [1.0, 2.0, 3.0]
        assert abs(_cosine_similarity(a, b) - 1.0) < 1e-6


# ---------------------------------------------------------------------------
# TestEmbedNodes
# ---------------------------------------------------------------------------

class TestEmbedNodes:
    def _make_mock_genai(self, embedding=None):
        """Build a mock google.generativeai module."""
        if embedding is None:
            embedding = FAKE_EMBEDDING
        mock_genai = MagicMock()
        mock_genai.embed_content.return_value = {"embedding": embedding}
        return mock_genai

    def test_raises_missing_api_key_when_no_key(self, vault_dir):
        from deploysquad_recon_core.embeddings import embed_nodes
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GEMINI_API_KEY", None)
            with pytest.raises(MissingAPIKeyError):
                embed_nodes(vault_dir)

    def test_accepts_api_key_arg(self, vault_dir):
        from deploysquad_recon_core.embeddings import embed_nodes
        mock_genai = self._make_mock_genai()
        with patch("deploysquad_recon_core.embeddings._import_genai", return_value=mock_genai):
            result = embed_nodes(vault_dir, api_key="test-key")
        mock_genai.configure.assert_called_once_with(api_key="test-key")
        assert "embedded" in result

    def test_accepts_env_var_key(self, vault_dir):
        from deploysquad_recon_core.embeddings import embed_nodes
        mock_genai = self._make_mock_genai()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "env-key"}):
            with patch("deploysquad_recon_core.embeddings._import_genai", return_value=mock_genai):
                result = embed_nodes(vault_dir, api_key=None)
        mock_genai.configure.assert_called_once_with(api_key="env-key")
        assert "embedded" in result

    def test_writes_cache_file_on_success(self, vault_dir):
        from deploysquad_recon_core.embeddings import embed_nodes
        mock_genai = self._make_mock_genai()
        with patch("deploysquad_recon_core.embeddings._import_genai", return_value=mock_genai):
            embed_nodes(vault_dir, api_key="test-key")
        cache_path = vault_dir / ".graph" / "embeddings.json"
        assert cache_path.exists()
        cache = json.loads(cache_path.read_text())
        assert len(cache) > 0

    def test_returns_embedded_and_cached_counts(self, vault_dir):
        from deploysquad_recon_core.embeddings import embed_nodes
        mock_genai = self._make_mock_genai()
        with patch("deploysquad_recon_core.embeddings._import_genai", return_value=mock_genai):
            result1 = embed_nodes(vault_dir, api_key="test-key")
        assert result1["embedded"] > 0
        assert result1["cached"] == 0

        # Second call — all should be cached
        with patch("deploysquad_recon_core.embeddings._import_genai", return_value=mock_genai):
            result2 = embed_nodes(vault_dir, api_key="test-key")
        assert result2["embedded"] == 0
        assert result2["cached"] == result1["embedded"]

    def test_does_not_write_cache_on_api_failure(self, vault_dir):
        from deploysquad_recon_core.embeddings import embed_nodes
        mock_genai = MagicMock()
        mock_genai.embed_content.side_effect = RuntimeError("API down")
        cache_path = vault_dir / ".graph" / "embeddings.json"
        with patch("deploysquad_recon_core.embeddings._import_genai", return_value=mock_genai):
            with pytest.raises(EmbeddingError):
                embed_nodes(vault_dir, api_key="test-key")
        assert not cache_path.exists()


# ---------------------------------------------------------------------------
# TestFindSimilar
# ---------------------------------------------------------------------------

class TestFindSimilar:
    def _write_cache(self, vault_dir, entries: dict):
        """Write embeddings.json cache manually for tests."""
        graph_dir = vault_dir / ".graph"
        graph_dir.mkdir(exist_ok=True)
        cache_path = graph_dir / "embeddings.json"
        cache_path.write_text(json.dumps(entries))

    def _get_project_and_goal(self, vault_dir):
        import deploysquad_recon_core as rc
        nodes = rc.list_nodes(vault_dir)
        project_path = next(n["file_path"] for n in nodes if n["type"] == "project")
        goal_path = next(n["file_path"] for n in nodes if n["type"] == "goal")
        return project_path, goal_path

    def test_raises_when_no_cache(self, vault_dir):
        from deploysquad_recon_core.embeddings import find_similar
        project_path, _ = self._get_project_and_goal(vault_dir)
        with pytest.raises(EmbeddingCacheMissingError):
            find_similar(project_path, vault_dir)

    def test_returns_nodes_above_threshold(self, vault_dir):
        from deploysquad_recon_core.embeddings import embed_nodes, find_similar

        mock_genai = MagicMock()
        mock_genai.embed_content.return_value = {"embedding": [1.0, 0.0, 0.0]}
        with patch("deploysquad_recon_core.embeddings._import_genai", return_value=mock_genai):
            embed_nodes(vault_dir, api_key="test-key")

        project_path, _ = self._get_project_and_goal(vault_dir)

        results = find_similar(project_path, vault_dir, top_k=5, threshold=0.5)
        assert isinstance(results, list)
        for abs_path, score in results:
            assert isinstance(abs_path, Path)
            assert abs_path.is_absolute()
            assert score >= 0.5

    def test_excludes_nodes_below_threshold(self, vault_dir):
        from deploysquad_recon_core.embeddings import find_similar, _cache_key, _embedding_text
        import deploysquad_recon_core as rc

        project_path, goal_path = self._get_project_and_goal(vault_dir)

        # Write cache: project and goal with orthogonal vectors (similarity=0)
        proj_node = rc.get_node(project_path)
        goal_node = rc.get_node(goal_path)

        proj_rel = str(project_path.relative_to(vault_dir))
        goal_rel = str(goal_path.relative_to(vault_dir))

        cache = {
            _cache_key(proj_rel, _embedding_text(proj_node)): [1.0, 0.0, 0.0],
            _cache_key(goal_rel, _embedding_text(goal_node)): [0.0, 1.0, 0.0],
        }
        self._write_cache(vault_dir, cache)

        # With threshold=0.9, no result should appear (orthogonal = 0.0 similarity)
        results = find_similar(project_path, vault_dir, top_k=5, threshold=0.9)
        assert results == []

    def test_excludes_source_node_itself(self, vault_dir):
        from deploysquad_recon_core.embeddings import find_similar, _cache_key, _embedding_text
        import deploysquad_recon_core as rc

        project_path, goal_path = self._get_project_and_goal(vault_dir)

        proj_node = rc.get_node(project_path)
        goal_node = rc.get_node(goal_path)

        proj_rel = str(project_path.relative_to(vault_dir))
        goal_rel = str(goal_path.relative_to(vault_dir))

        # Both with identical high-similarity vectors
        cache = {
            _cache_key(proj_rel, _embedding_text(proj_node)): [1.0, 0.0, 0.0],
            _cache_key(goal_rel, _embedding_text(goal_node)): [1.0, 0.0, 0.0],
        }
        self._write_cache(vault_dir, cache)

        results = find_similar(project_path, vault_dir, top_k=5, threshold=0.0)
        result_paths = [str(p) for p, _ in results]
        assert str(project_path) not in result_paths

    def test_results_sorted_descending_by_score(self, vault_dir):
        from deploysquad_recon_core.embeddings import find_similar, _cache_key, _embedding_text
        import deploysquad_recon_core as rc

        project_path, goal_path = self._get_project_and_goal(vault_dir)

        proj_node = rc.get_node(project_path)
        goal_node = rc.get_node(goal_path)

        proj_rel = str(project_path.relative_to(vault_dir))
        goal_rel = str(goal_path.relative_to(vault_dir))

        # goal has moderate similarity to project
        cache = {
            _cache_key(proj_rel, _embedding_text(proj_node)): [1.0, 0.0, 0.0],
            _cache_key(goal_rel, _embedding_text(goal_node)): [0.8, 0.6, 0.0],
        }
        self._write_cache(vault_dir, cache)

        results = find_similar(project_path, vault_dir, top_k=5, threshold=0.0)
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)

    def test_excludes_already_linked_nodes(self, vault_dir):
        from deploysquad_recon_core.embeddings import find_similar, _cache_key, _embedding_text
        import deploysquad_recon_core as rc

        project_path, goal_path = self._get_project_and_goal(vault_dir)

        # Goal already has belongs_to pointing to Project - Test Project
        # Update goal with a related_to link to the project
        rc.update_node(goal_path, {"related_to": ["[[Project - Test Project]]"]})

        goal_node = rc.get_node(goal_path)
        proj_node = rc.get_node(project_path)

        proj_rel = str(project_path.relative_to(vault_dir))
        goal_rel = str(goal_path.relative_to(vault_dir))

        # Both with high similarity
        cache = {
            _cache_key(proj_rel, _embedding_text(proj_node)): [1.0, 0.0, 0.0],
            _cache_key(goal_rel, _embedding_text(goal_node)): [1.0, 0.0, 0.0],
        }
        self._write_cache(vault_dir, cache)

        # find_similar from goal — project is already linked (belongs_to + related_to) so should be excluded
        results = find_similar(goal_path, vault_dir, top_k=5, threshold=0.0)
        result_paths = [str(p) for p, _ in results]
        assert str(project_path) not in result_paths
