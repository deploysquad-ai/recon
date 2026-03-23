"""Custom exception hierarchy for recon-core."""


class ReconCoreError(Exception):
    """Base exception for recon-core."""


class ValidationError(ReconCoreError):
    """Node data fails schema validation."""


class NodeNotFoundError(ReconCoreError):
    """Referenced node file does not exist."""


class BrokenLinkError(ReconCoreError):
    """Wikilink target does not exist in the vault."""


class DuplicateNodeError(ReconCoreError):
    """A node file already exists at the target path."""


class MissingAPIKeyError(ReconCoreError):
    """GEMINI_API_KEY not set and no api_key argument provided."""


class EmbeddingError(ReconCoreError):
    """Network or API failure during embedding."""


class EmbeddingCacheMissingError(ReconCoreError):
    """find_similar called before embed_nodes has run."""
