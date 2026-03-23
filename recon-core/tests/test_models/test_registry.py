"""Tests for model registry and schema export."""
import pytest

from deploysquad_recon_core.models import NODE_TYPE_MAP, get_model_for_type
from deploysquad_recon_core.schemas import export_schemas, export_schema


class TestRegistry:
    def test_all_10_types_registered(self):
        assert len(NODE_TYPE_MAP) == 10
        assert set(NODE_TYPE_MAP.keys()) == {
            "project", "goal", "version", "persona", "constraint",
            "module", "decision", "user-story", "epic", "feature"
        }

    def test_get_model_for_type_feature(self):
        model = get_model_for_type("feature")
        assert model.__name__ == "FeatureNode"

    def test_get_model_for_type_user_story(self):
        model = get_model_for_type("user-story")
        assert model.__name__ == "UserStoryNode"

    def test_get_model_for_unknown_type(self):
        with pytest.raises(KeyError):
            get_model_for_type("unknown")


class TestSchemaExport:
    def test_export_schemas_returns_all(self):
        schemas = export_schemas()
        assert len(schemas) == 10
        assert "properties" in schemas["project"]

    def test_export_single_schema(self):
        schema = export_schema("feature")
        assert "implements" in schema["properties"]

    def test_export_schema_has_required(self):
        schema = export_schema("project")
        assert "required" in schema

    def test_export_schema_unknown_type(self):
        with pytest.raises(KeyError):
            export_schema("unknown")
