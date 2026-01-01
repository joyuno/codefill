-- =====================================================
-- solved.ac Integration Table
-- =====================================================

-- solved.ac 프로필 정보를 저장하는 테이블
CREATE TABLE IF NOT EXISTS solved_ac_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- solved.ac 기본 정보
    handle VARCHAR(50) NOT NULL,  -- 백준 아이디
    bio TEXT,
    profile_image_url TEXT,

    -- 레벨/티어 정보
    tier INTEGER DEFAULT 0,  -- 0: Unrated, 1-5: Bronze, 6-10: Silver, etc.
    rating INTEGER DEFAULT 0,
    class INTEGER DEFAULT 0,
    class_decoration VARCHAR(20),  -- none, silver, gold

    -- 문제 풀이 통계
    solved_count INTEGER DEFAULT 0,
    exp BIGINT DEFAULT 0,

    -- 랭킹 정보
    rank INTEGER,

    -- 스트릭 정보
    max_streak INTEGER DEFAULT 0,

    -- 기타 정보
    organizations JSONB,  -- 소속 정보

    -- 동기화 정보
    last_synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS solved_ac_profiles_user_idx ON solved_ac_profiles(user_id);
CREATE INDEX IF NOT EXISTS solved_ac_profiles_handle_idx ON solved_ac_profiles(handle);
CREATE INDEX IF NOT EXISTS solved_ac_profiles_tier_idx ON solved_ac_profiles(tier);
CREATE INDEX IF NOT EXISTS solved_ac_profiles_rating_idx ON solved_ac_profiles(rating);

-- 권한 부여 (GRANT)
GRANT ALL ON solved_ac_profiles TO postgres;
GRANT ALL ON solved_ac_profiles TO service_role;
GRANT SELECT ON solved_ac_profiles TO authenticated;
GRANT SELECT ON solved_ac_profiles TO anon;

-- RLS 활성화
ALTER TABLE solved_ac_profiles ENABLE ROW LEVEL SECURITY;

-- Service Role 전용 정책 (기존 테이블들과 동일한 패턴)
CREATE POLICY "Service role can manage solved_ac_profiles" ON solved_ac_profiles
    FOR ALL USING (auth.role() = 'service_role');

-- 공개 읽기 정책 (다른 사용자 프로필 조회 허용)
CREATE POLICY "Anyone can view solved_ac_profiles" ON solved_ac_profiles
    FOR SELECT USING (true);

-- updated_at 자동 업데이트 트리거
CREATE TRIGGER update_solved_ac_profiles_updated_at BEFORE UPDATE ON solved_ac_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
