-- =====================================================
-- Add onboarding columns to users table
-- =====================================================

-- Add onboarding-related columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS current_status VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS learning_goal VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS experience_level VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS strong_algorithms TEXT[];
ALTER TABLE users ADD COLUMN IF NOT EXISTS solved_ac_id VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS desired_job VARCHAR(20);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS users_current_status_idx ON users(current_status);
CREATE INDEX IF NOT EXISTS users_experience_level_idx ON users(experience_level);
