// File: scripts/setup-db.ts

import { pool } from '../lib/auth';

async function setupDatabase() {
    const client = await pool.connect();
    try {
      console.log('Connected to the database.');
  
      const tableExists = await client.query(`
        SELECT EXISTS (
          SELECT FROM information_schema.tables 
          WHERE table_schema = 'public'
          AND table_name = 'upload_documents'
        );
      `);
  
      if (!tableExists.rows[0].exists) {
        await client.query(`
          CREATE TABLE upload_documents (
            id SERIAL PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
          );
        `);
        console.log('Table upload_documents created successfully.');
      } else {
        console.log('Table upload_documents already exists. Proceeding to update.');
  
        await client.query(`
          DO $$ 
          BEGIN 
            BEGIN
              ALTER TABLE upload_documents ADD COLUMN file_name VARCHAR(255) NOT NULL DEFAULT '';
            EXCEPTION
              WHEN duplicate_column THEN RAISE NOTICE 'column file_name already exists in upload_documents.';
            END;
            
            BEGIN
              ALTER TABLE upload_documents ADD COLUMN file_path VARCHAR(255) NOT NULL DEFAULT '';
            EXCEPTION
              WHEN duplicate_column THEN RAISE NOTICE 'column file_path already exists in upload_documents.';
            END;
            
            BEGIN
              ALTER TABLE upload_documents ADD COLUMN uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
            EXCEPTION
              WHEN duplicate_column THEN RAISE NOTICE 'column uploaded_at already exists in upload_documents.';
            END;
          END $$;
        `);
        console.log('Table upload_documents updated successfully.');
      }
    } catch (error) {
      console.error('Error setting up database:', error);
    } finally {
      client.release();
      console.log('Database connection released.');
    }
  }
  
  setupDatabase().then(() => {
    console.log('Database setup completed.');
    process.exit(0);
  }).catch((error) => {
    console.error('Database setup failed:', error);
    process.exit(1);
  });