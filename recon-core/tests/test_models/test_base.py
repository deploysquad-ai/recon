"""Tests for base model, Wikilink type, and status enums."""
import pytest
from pydantic import ValidationError

from deploysquad_recon_core.models.base import BaseNode, FullStatus, NoCompleteStatus, Wikilink


class TestWikilink:
    def test_valid_wikilink(self):
        """[[Type - Name]] format is accepted."""
        from pydantic import TypeAdapter
        ta = TypeAdapter(Wikilink)
        result = ta.validate_python("[[Project - My App]]")
        assert result == "[[Project - My App]]"

    def test_rejects_no_brackets(self):
        from pydantic import TypeAdapter
        ta = TypeAdapter(Wikilink)
        with pytest.raises(ValidationError):
            ta.validate_python("Project - My App")

    def test_rejects_missing_separator(self):
        from pydantic import TypeAdapter
        ta = TypeAdapter(Wikilink)
        with pytest.raises(ValidationError):
            ta.validate_python("[[ProjectMyApp]]")

    def test_multi_word_type(self):
        from pydantic import TypeAdapter
        ta = TypeAdapter(Wikilink)
        result = ta.validate_python("[[User Story - Login Flow]]")
        assert result == "[[User Story - Login Flow]]"


class TestFullStatus:
    def test_all_values(self):
        for s in ["draft", "active", "complete", "archived"]:
            assert FullStatus(s) == s

    def test_rejects_invalid(self):
        with pytest.raises(ValueError):
            FullStatus("deleted")


class TestNoCompleteStatus:
    def test_rejects_complete(self):
        with pytest.raises(ValueError):
            NoCompleteStatus("complete")

    def test_accepts_draft(self):
        assert NoCompleteStatus("draft") == "draft"

    def test_accepts_active(self):
        assert NoCompleteStatus("active") == "active"

    def test_accepts_archived(self):
        assert NoCompleteStatus("archived") == "archived"


class TestBaseNode:
    def test_valid_base_node(self):
        node = BaseNode(type="project", name="My App", status="draft")
        assert node.name == "My App"
        assert node.schema_version == 1

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            BaseNode(type="project", name="", status="draft")

    def test_schema_version_defaults_to_1(self):
        node = BaseNode(type="project", name="X", status="draft")
        assert node.schema_version == 1

    def test_tags_defaults_to_empty_list(self):
        node = BaseNode(type="project", name="X", status="draft")
        assert node.tags == []

    def test_tags_accepts_list(self):
        node = BaseNode(type="project", name="X", status="draft", tags=["project/my-app", "custom"])
        assert node.tags == ["project/my-app", "custom"]
