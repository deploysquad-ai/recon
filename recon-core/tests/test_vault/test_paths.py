"""Tests for vault path utilities."""
from pathlib import Path

from deploysquad_recon_core.vault.paths import (
    type_to_subfolder,
    node_filename,
    node_filepath,
    parse_filename,
    name_to_wikilink,
    project_slug,
    get_type_display_name,
    find_project_name,
    project_tag,
)


class TestTypeToSubfolder:
    def test_feature(self):
        assert type_to_subfolder("feature") == "features"

    def test_user_story(self):
        assert type_to_subfolder("user-story") == "user-stories"

    def test_project_is_root(self):
        assert type_to_subfolder("project") == ""

    def test_goal(self):
        assert type_to_subfolder("goal") == "goals"

    def test_persona(self):
        assert type_to_subfolder("persona") == "personas"

    def test_constraint(self):
        assert type_to_subfolder("constraint") == "constraints"

    def test_module(self):
        assert type_to_subfolder("module") == "modules"

    def test_decision(self):
        assert type_to_subfolder("decision") == "decisions"

    def test_epic(self):
        assert type_to_subfolder("epic") == "epics"

    def test_version(self):
        assert type_to_subfolder("version") == "versions"


class TestNodeFilename:
    def test_feature(self):
        assert node_filename("feature", "JWT Login") == "Feature - JWT Login.md"

    def test_user_story(self):
        assert node_filename("user-story", "Login Flow") == "User Story - Login Flow.md"

    def test_project(self):
        assert node_filename("project", "My App") == "Project - My App.md"


class TestNodeFilepath:
    def test_feature(self, tmp_path):
        result = node_filepath("feature", "JWT Login", tmp_path)
        assert result == tmp_path / "features" / "Feature - JWT Login.md"

    def test_project_at_root(self, tmp_path):
        result = node_filepath("project", "My App", tmp_path)
        assert result == tmp_path / "Project - My App.md"

    def test_user_story(self, tmp_path):
        result = node_filepath("user-story", "Login", tmp_path)
        assert result == tmp_path / "user-stories" / "User Story - Login.md"


class TestParseFilename:
    def test_feature(self):
        assert parse_filename("Feature - JWT Login.md") == ("feature", "JWT Login")

    def test_user_story(self):
        assert parse_filename("User Story - Login Flow.md") == ("user-story", "Login Flow")

    def test_project(self):
        assert parse_filename("Project - My App.md") == ("project", "My App")

    def test_invalid_returns_none(self):
        assert parse_filename("README.md") is None

    def test_no_md_extension_returns_none(self):
        assert parse_filename("Feature - JWT Login") is None


class TestNameToWikilink:
    def test_feature(self):
        assert name_to_wikilink("feature", "JWT Login") == "[[Feature - JWT Login]]"

    def test_user_story(self):
        assert name_to_wikilink("user-story", "Login") == "[[User Story - Login]]"


class TestProjectSlug:
    def test_simple(self):
        assert project_slug("My Cool Project") == "my-cool-project"

    def test_special_chars(self):
        assert project_slug("App (v2.0)") == "app-v2-0"

    def test_multiple_spaces(self):
        assert project_slug("My   Project") == "my-project"


class TestTypeDisplayName:
    def test_feature(self):
        assert get_type_display_name("feature") == "Feature"

    def test_user_story(self):
        assert get_type_display_name("user-story") == "User Story"


class TestFindProjectName:
    def test_finds_project_file(self, tmp_path):
        (tmp_path / "Project - Ideate.md").write_text(
            "---\ntype: project\nname: Ideate\nstatus: draft\nschema_version: 1\n---\n"
        )
        assert find_project_name(tmp_path) == "Ideate"

    def test_returns_none_when_no_project_file(self, tmp_path):
        assert find_project_name(tmp_path) is None

    def test_ignores_non_project_files(self, tmp_path):
        (tmp_path / "Feature - Login.md").write_text("")
        assert find_project_name(tmp_path) is None

    def test_multiword_project_name(self, tmp_path):
        (tmp_path / "Project - My Cool App.md").write_text(
            "---\ntype: project\nname: My Cool App\nstatus: draft\nschema_version: 1\n---\n"
        )
        assert find_project_name(tmp_path) == "My Cool App"


class TestProjectTag:
    def test_simple_name(self):
        assert project_tag("Ideate") == "project/ideate"

    def test_multiword_name(self):
        assert project_tag("My Cool Project") == "project/my-cool-project"

    def test_already_lowercase(self):
        assert project_tag("ideate") == "project/ideate"

    def test_spaces_become_hyphens(self):
        assert project_tag("Hello World") == "project/hello-world"
