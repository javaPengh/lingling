import type { DatabaseSync } from "node:sqlite";
import { getDatabase } from "./connection.js";

export type Db = DatabaseSync;

export function dbOrDefault(db?: Db): Db {
  return db ?? getDatabase();
}

export function jsonText(value: unknown): string {
  return JSON.stringify(value);
}

export function nullableJsonText(value: unknown | null): string | null {
  return value === null ? null : JSON.stringify(value);
}

export function parseJson<T>(value: string | null, fallback: T): T {
  return value === null ? fallback : (JSON.parse(value) as T);
}

export function boolToInt(value: boolean | null): number | null {
  if (value === null) {
    return null;
  }

  return value ? 1 : 0;
}

export function intToBool(value: number | null): boolean | null {
  if (value === null) {
    return null;
  }

  return value === 1;
}
