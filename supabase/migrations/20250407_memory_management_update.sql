ALTER TABLE characters ADD COLUMN IF NOT EXISTS is_sleeping BOOLEAN DEFAULT FALSE;

ALTER TABLE characters ADD COLUMN IF NOT EXISTS last_memory_processing_date TIMESTAMPTZ;

ALTER TABLE memories ADD COLUMN IF NOT EXISTS is_processed BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_memories_character_type_processed ON memories(character_id, memory_type, is_processed);

ALTER TABLE characters ENABLE ROW LEVEL SECURITY;
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
