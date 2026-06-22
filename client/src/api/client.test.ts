import { describe, expect, it } from "vitest";

import { FetchResponse, contentUrl, fetchTodayLevel } from "./client";

describe("content API client", () => {
  it("builds the today-content URL", () => {
    expect(contentUrl("http://srv:8000/", "youth_10yo")).toBe(
      "http://srv:8000/content/today/youth_10yo",
    );
  });

  it("returns the parsed body on success", async () => {
    const body = { profile_id: "p", date: "2026-06-22", stale: false, level: { schema_version: "1" } };
    const fake = async (): Promise<FetchResponse> => ({ ok: true, status: 200, json: async () => body });
    const res = await fetchTodayLevel("http://srv", "p", fake);
    expect(res.date).toBe("2026-06-22");
    expect(res.level.schema_version).toBe("1");
  });

  it("throws on a non-ok response", async () => {
    const fake = async (): Promise<FetchResponse> => ({ ok: false, status: 404, json: async () => ({}) });
    await expect(fetchTodayLevel("http://srv", "p", fake)).rejects.toThrow(/HTTP 404/);
  });
});
