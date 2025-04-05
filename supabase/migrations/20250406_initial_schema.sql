-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Characters table
CREATE TABLE IF NOT EXISTS characters (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  config JSONB DEFAULT '{}'::jsonb, -- For future custom configurations
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Memories table
CREATE TABLE IF NOT EXISTS memories (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
  /* 
   * memory_type defines the hierarchical memory structure:
   * - 'daily_raw': Raw daily conversation and task records
   * - 'daily_summary': Summary of a single day's memories
   * - 'level_10': Summary of approximately 10 daily_summary memories (~10 days)
   * - 'level_100': Summary of approximately 10 level_10 memories (~100 days)
   * - 'level_1000': Summary of approximately 10 level_100 memories (~1000 days)
   * - 'level_archive': Very long-term consolidated memories beyond 1000 days
   */
  memory_type TEXT NOT NULL,
  start_day INTEGER NOT NULL,
  end_day INTEGER NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  -- Add indexes for common query patterns
  CONSTRAINT memories_start_end_check CHECK (start_day <= end_day)
);

-- Create index on character_id and memory_type for faster lookups
CREATE INDEX idx_memories_character_memory_type ON memories(character_id, memory_type);
-- Create index on user_id for user-based queries
CREATE INDEX idx_memories_user_id ON memories(user_id);
-- Create index on date range for time-based queries
CREATE INDEX idx_memories_date_range ON memories(start_day, end_day);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
  device_id TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  -- Create a unique constraint to ensure only one active session per device and character
  CONSTRAINT unique_active_device_character UNIQUE (device_id, character_id)
);

-- Create index on user_id for user-based queries
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
-- Create index on active sessions for quick filtering
CREATE INDEX idx_sessions_active ON sessions(is_active) WHERE (is_active = TRUE);

-- Add RLS (Row Level Security) policies
ALTER TABLE characters ENABLE ROW LEVEL SECURITY;
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Create policies for characters table
CREATE POLICY "Users can view their own characters" 
  ON characters FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own characters" 
  ON characters FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own characters" 
  ON characters FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own characters" 
  ON characters FOR DELETE 
  USING (auth.uid() = user_id);

-- Create policies for memories table
CREATE POLICY "Users can view their own memories" 
  ON memories FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own memories" 
  ON memories FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own memories" 
  ON memories FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own memories" 
  ON memories FOR DELETE 
  USING (auth.uid() = user_id);

-- Create policies for sessions table
CREATE POLICY "Users can view their own sessions" 
  ON sessions FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own sessions" 
  ON sessions FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own sessions" 
  ON sessions FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own sessions" 
  ON sessions FOR DELETE 
  USING (auth.uid() = user_id);
