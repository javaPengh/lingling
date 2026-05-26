import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { DatabaseSync } from "node:sqlite";

let database: DatabaseSync | null = null;

const serverDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const rootDir = resolve(serverDir, "..");
const schemaPath = resolve(serverDir, "db", "schema.sql");
const databasePath = resolve(rootDir, "lingling.db");

export function getDatabase(): DatabaseSync {
  if (!database) {
    database = new DatabaseSync(databasePath);
    database.exec("PRAGMA foreign_keys = ON;");
    database.exec(readFileSync(schemaPath, "utf8"));
  }

  return database;
}
