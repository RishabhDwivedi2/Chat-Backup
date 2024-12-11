// File: src/lib/db.ts

import { Pool } from 'pg';

let pool: Pool | null = null;

if (!pool) {
  pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: parseInt(process.env.DB_PORT || '5432'),
  });
}

export { pool };