/**
 * Client for the KidQuest content server. The fetch implementation is injectable
 * so the URL/parsing logic is unit-testable without a browser or a live server.
 */
import { RawDailyLevel } from "../engine/level/LevelLoader";

export interface TodayResponse {
  profile_id: string;
  date: string;
  stale: boolean;
  level: RawDailyLevel;
}

export interface FetchResponse {
  ok: boolean;
  status: number;
  json: () => Promise<unknown>;
}

export type FetchLike = (url: string) => Promise<FetchResponse>;

export function contentUrl(baseUrl: string, profileId: string): string {
  return `${baseUrl.replace(/\/$/, "")}/content/today/${encodeURIComponent(profileId)}`;
}

export async function fetchTodayLevel(
  baseUrl: string,
  profileId: string,
  fetchImpl: FetchLike,
): Promise<TodayResponse> {
  const res = await fetchImpl(contentUrl(baseUrl, profileId));
  if (!res.ok) {
    throw new Error(`content fetch failed for ${profileId}: HTTP ${res.status}`);
  }
  return (await res.json()) as TodayResponse;
}
