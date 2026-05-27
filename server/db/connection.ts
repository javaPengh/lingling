import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { DatabaseSync } from "node:sqlite";

let database: DatabaseSync | null = null;

const serverDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const rootDir = resolve(serverDir, "..");
const schemaPath = resolve(serverDir, "db", "schema.sql");
const databasePath = resolve(rootDir, "lingling.db");

export function createDatabaseConnection(path = databasePath): DatabaseSync {
  const connection = new DatabaseSync(path);
  connection.exec("PRAGMA foreign_keys = ON;");
  connection.exec(readFileSync(schemaPath, "utf8"));

  return connection;
}

export function getDatabase(): DatabaseSync {
  if (!database) {
    database = createDatabaseConnection();
  }

  return database;
}
