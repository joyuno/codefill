-- =====================================================
-- credit_history 테이블 RLS 및 권한 설정
-- =====================================================

-- RLS 활성화
ALTER TABLE credit_history ENABLE ROW LEVEL SECURITY;

-- 정책: 사용자는 자신의 내역만 조회 가능
CREATE POLICY "Users can view their own credit history" ON credit_history
    FOR SELECT USING (auth.uid() = user_id);

-- 정책: 사용자는 직접 INSERT 불가 (함수를 통해서만)
-- service_role만 INSERT 가능
CREATE POLICY "Service role can insert credit history" ON credit_history
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- 정책: service_role은 모든 작업 가능
CREATE POLICY "Service role can manage credit history" ON credit_history
    FOR ALL USING (auth.role() = 'service_role');

-- 테이블 권한
GRANT SELECT ON credit_history TO authenticated;
GRANT ALL ON credit_history TO service_role;

-- 코멘트
COMMENT ON TABLE credit_history IS '크레딧 사용/충전 내역';
COMMENT ON COLUMN credit_history.type IS '유형: use(사용), charge(충전), bonus(보너스), refund(환불)';
COMMENT ON COLUMN credit_history.amount IS '변동량 (양수: 충전/보너스/환불, 음수: 사용)';
COMMENT ON COLUMN credit_history.balance IS '변경 후 잔액';
