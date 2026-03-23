"""Tests for wikilink parsing and resolution."""
from pathlib import Path

import pytest

from deploysquad_recon_core.links import (
    parse_wikilink,
    extract_wikilinks,
    resolve_link,
    resolve_all_links,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "sample_vault" / "my-project"


class TestParseWikilink:
    def test_valid_feature(self):
        assert parse_wikilink("[[Feature - JWT Login]]") == ("feature", "JWT Login")

    def test_valid_user_story(self):
        assert parse_wikilink("[[User Story - Login]]") == ("user-story", "Login")

    def test_valid_project(self):
        assert parse_wikilink("[[Project - My App]]") == ("project", "My App")

    def test_not_a_link(self):
        assert parse_wikilink("not a link") is None

    def test_unknown_type(self):
        assert parse_wikilink("[[Unknown - Foo]]") is None

    def test_no_separator(self):
        assert parse_wikilink("[[Feature]]") is None


class TestExtractWikilinks:
    def test_from_string(self):
        result = extract_wikilinks("[[Feature - X]]")
        assert result == ["[[Feature - X]]"]

    def test_from_list(self):
        result = extract_wikilinks(["[[Feature - X]]", "[[Module - Y]]"])
        assert set(result) == {"[[Feature - X]]", "[[Module - Y]]"}

    def test_from_dict(self):
        result = extract_wikilinks({
            "belongs_to": "[[Project - X]]",
            "implements": ["[[User Story - Y]]"],
        })
        assert "[[Project - X]]" in result
        assert "[[User Story - Y]]" in result

    def test_plain_string(self):
        assert extract_wikilinks("just text") == []

    def test_nested(self):
        data = {"a": {"b": ["[[Feature - X]]"]}}
        result = extract_wikilinks(data)
        assert result == ["[[Feature - X]]"]


class TestResolveLink:
    def test_existing_feature(self):
        result = resolve_link("[[Feature - JWT Login]]", FIXTURE_DIR)
        assert result is not None
        assert result.exists()

    def test_existing_project(self):
        result = resolve_link("[[Project - My Project]]", FIXTURE_DIR)
        assert result is not None

    def test_nonexistent(self):
        result = resolve_link("[[Feature - Nonexistent]]", FIXTURE_DIR)
        assert result is None

    def test_invalid_link(self):
        result = resolve_link("not a link", FIXTURE_DIR)
        assert result is None


class TestResolveAllLinks:
    def test_fixture_vault_no_broken_links(self):
        result = resolve_all_links(FIXTURE_DIR)
        assert len(result["broken"]) == 0
        assert len(result["valid"]) > 0

    def test_broken_link_detected(self, tmp_path):
        # Create a feature that references a nonexistent user story
        import frontmatter
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        post = frontmatter.Post("", type="feature", schema_version=1,
                                name="Bad", status="draft",
                                belongs_to="[[Module - Missing]]",
                                implements=["[[User Story - Missing]]"])
        (features_dir / "Feature - Bad.md").write_text(frontmatter.dumps(post))

        result = resolve_all_links(tmp_path)
        assert len(result["broken"]) >= 2  # Module and User Story are missing

    def test_result_includes_source_path(self):
        result = resolve_all_links(FIXTURE_DIR)
        for lr in result["valid"]:
            assert lr.source_path.exists()
            assert lr.wikilink.startswith("[[")
