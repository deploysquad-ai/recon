"""Tests for graph index builder."""
import json
from pathlib import Path

from deploysquad_recon_core.index import build_index, write_index, read_index


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "sample_vault" / "my-project"


class TestBuildIndex:
    def test_returns_all_nodes(self):
        index = build_index(FIXTURE_DIR)
        assert len(index["nodes"]) == 10

    def test_schema_version(self):
        index = build_index(FIXTURE_DIR)
        assert index["schema_version"] == 1

    def test_has_built_at(self):
        index = build_index(FIXTURE_DIR)
        assert "built_at" in index

    def test_project_name(self):
        index = build_index(FIXTURE_DIR)
        assert index["project"] == "My Project"

    def test_feature_node_entry(self):
        index = build_index(FIXTURE_DIR)
        feature_key = "features/Feature - JWT Login.md"
        assert feature_key in index["nodes"]
        node = index["nodes"][feature_key]
        assert node["type"] == "feature"
        assert node["name"] == "JWT Login"
        assert node["status"] == "draft"

    def test_feature_edges(self):
        index = build_index(FIXTURE_DIR)
        feature = index["nodes"]["features/Feature - JWT Login.md"]
        assert "[[User Story - Login]]" in feature["edges"].get("implements", [])
        assert "[[Module - Auth]]" in feature["edges"].get("belongs_to", [])

    def test_project_at_root(self):
        index = build_index(FIXTURE_DIR)
        assert "Project - My Project.md" in index["nodes"]

    def test_deterministic_keys(self):
        """Index should be sorted for deterministic output."""
        index = build_index(FIXTURE_DIR)
        keys = list(index["nodes"].keys())
        assert keys == sorted(keys)


class TestWriteAndReadIndex:
    def test_round_trip(self, tmp_path):
        index = build_index(FIXTURE_DIR)
        write_index(index, tmp_path)
        loaded = read_index(tmp_path)
        assert loaded["project"] == "My Project"
        assert len(loaded["nodes"]) == 10

    def test_creates_graph_dir(self, tmp_path):
        index = build_index(FIXTURE_DIR)
        write_index(index, tmp_path)
        assert (tmp_path / ".graph" / "index.json").exists()

    def test_valid_json(self, tmp_path):
        index = build_index(FIXTURE_DIR)
        path = write_index(index, tmp_path)
        # Should be parseable JSON
        json.loads(path.read_text())
