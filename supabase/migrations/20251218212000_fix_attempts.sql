-- Fix attempts table column sizes

-- Change submitted_answer from VARCHAR(10) to TEXT
ALTER TABLE attempts ALTER COLUMN submitted_answer TYPE TEXT;
