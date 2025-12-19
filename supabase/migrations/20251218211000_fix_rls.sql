-- Fix RLS permissions for service role access

-- Grant permissions to authenticated and service_role
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;

-- Grant specific permissions
GRANT INSERT, UPDATE ON users TO authenticated;
GRANT INSERT, UPDATE ON user_stats TO authenticated;
GRANT INSERT, UPDATE ON user_preferences TO authenticated;
GRANT INSERT ON attempts TO authenticated;
GRANT INSERT ON hint_logs TO authenticated;
GRANT INSERT, UPDATE ON daily_activity TO authenticated;

-- Allow anon to view public tables
GRANT SELECT ON codes TO anon;
GRANT SELECT ON problems TO anon;
GRANT SELECT ON badges TO anon;
GRANT SELECT ON plans TO anon;

-- Fix service role policies - service_role bypasses RLS by default
-- but we need to make sure the policies don't block it

-- Drop existing service_role policies that might be conflicting
DROP POLICY IF EXISTS "Service role can manage users" ON users;
DROP POLICY IF EXISTS "Service role can manage user_stats" ON user_stats;
DROP POLICY IF EXISTS "Service role can manage user_preferences" ON user_preferences;
DROP POLICY IF EXISTS "Service role can manage attempts" ON attempts;
DROP POLICY IF EXISTS "Service role can manage hint_logs" ON hint_logs;
DROP POLICY IF EXISTS "Service role can manage daily_activity" ON daily_activity;
DROP POLICY IF EXISTS "Service role can manage user_badges" ON user_badges;
DROP POLICY IF EXISTS "Service role can manage subscriptions" ON subscriptions;
DROP POLICY IF EXISTS "Service role can manage codes" ON codes;
DROP POLICY IF EXISTS "Service role can manage problems" ON problems;
DROP POLICY IF EXISTS "Service role can manage badges" ON badges;
DROP POLICY IF EXISTS "Service role can manage plans" ON plans;

-- For public tables, allow everyone to select
DROP POLICY IF EXISTS "Anyone can view codes" ON codes;
DROP POLICY IF EXISTS "Anyone can view problems" ON problems;
DROP POLICY IF EXISTS "Anyone can view badges" ON badges;
DROP POLICY IF EXISTS "Anyone can view plans" ON plans;

CREATE POLICY "Public read codes" ON codes FOR SELECT USING (true);
CREATE POLICY "Public read problems" ON problems FOR SELECT USING (true);
CREATE POLICY "Public read badges" ON badges FOR SELECT USING (true);
CREATE POLICY "Public read plans" ON plans FOR SELECT USING (true);
