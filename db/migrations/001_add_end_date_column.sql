-- Migration: Add end_date column to todos table
-- Version: 001
-- Description: Add end_date column to support todo item deadlines
-- Date: 2025-01-08

-- Add end_date column to todos table
ALTER TABLE todos 
ADD COLUMN end_date TIMESTAMP WITH TIME ZONE;

-- Add comment to the new column
COMMENT ON COLUMN todos.end_date IS '完了予定日';

-- Create index for end_date column (already exists in model, but adding for completeness)
CREATE INDEX IF NOT EXISTS idx_todos_end_date ON todos(end_date);

-- Create composite index for incomplete tasks with end_date (already exists in model)
CREATE INDEX IF NOT EXISTS idx_todos_incomplete_end_date ON todos(completed, end_date);

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 001: Successfully added end_date column to todos table';
END $$;