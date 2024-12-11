// File: src/lib/auth.ts

import { betterAuth } from "better-auth"
import pg from "pg";
import dotenv from 'dotenv';
dotenv.config();

const pool = new pg.Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: parseInt(process.env.DB_PORT || '5432'),
});

export const auth = betterAuth({
    database: pool,
    emailAndPassword: {
        enabled: true
    },
});

export const getUserCount = async () => {
    const client = await pool.connect();
    try {
        const result = await client.query('SELECT COUNT(*) FROM users');
        return result.rows[0].count;
    } finally {
        client.release();
    }
};

export { pool };