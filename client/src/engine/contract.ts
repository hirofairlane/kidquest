/**
 * Binding between the pure engine and the shared content contract.
 *
 * The daily-level JSON schema declares `schema_version` as a constant. The engine
 * refuses to load content it does not understand. Keep this in sync with
 * `shared/schemas/daily_level.schema.json` (`schema_version.const`).
 */
export const SUPPORTED_SCHEMA_VERSION = "1";

/** True when the engine can load content authored against the given schema version. */
export function isSupportedSchemaVersion(version: string): boolean {
  return version === SUPPORTED_SCHEMA_VERSION;
}
