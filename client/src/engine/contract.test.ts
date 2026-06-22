import { describe, expect, it } from "vitest";

import { isSupportedSchemaVersion, SUPPORTED_SCHEMA_VERSION } from "./contract";

describe("schema-version contract", () => {
  it("accepts the supported version", () => {
    expect(isSupportedSchemaVersion(SUPPORTED_SCHEMA_VERSION)).toBe(true);
  });

  it("rejects any other version", () => {
    expect(isSupportedSchemaVersion("0")).toBe(false);
    expect(isSupportedSchemaVersion("2")).toBe(false);
  });
});
