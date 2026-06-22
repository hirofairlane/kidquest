"""KidQuest server package.

Importable without side effects (no network, no filesystem writes, no process
spawning at import time) so it is safe to import under test. Behaviour gated by
the ``KIDQUEST_TESTING`` environment variable is added by later milestones.
"""

# Daily-level schema version this server understands. Kept in sync with
# shared/schemas/daily_level.schema.json (schema_version.const) and verified by tests.
SCHEMA_VERSION = "1"

__all__ = ["SCHEMA_VERSION"]
