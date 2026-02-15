-- Database initialization script for Todo API Backend
-- This script runs when the PostgreSQL container starts for the first time

-- Create additional extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Set database encoding and collation for Japanese text support
ALTER DATABASE todoapp SET client_encoding TO 'UTF8';
ALTER DATABASE todoapp SET lc_collate TO 'C';
ALTER DATABASE todoapp SET lc_ctype TO 'en_US.utf8';

-- Create indexes for better performance (these will be created by SQLAlchemy as well)
-- But we can add additional performance indexes here if needed

-- Set default timezone
SET timezone = 'UTC';

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Grant necessary permissions to the application user
GRANT CONNECT ON DATABASE todoapp TO todouser;
GRANT USAGE ON SCHEMA public TO todouser;
GRANT CREATE ON SCHEMA public TO todouser;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Todo API Backend database initialized successfully';
END $$;