import json
import fcntl
import sys

# 솔루션 정의
solutions_data = {
    4073: {  # baekjoon_31416 - 가상 검증 기술
        "python": '''# 가상 검증 기술 - 두 연구원이 검증 업무를 분담하여 최소 시간 계산
import sys
input = sys.stdin.readline

Q = int(input())
for _ in range(Q):
    TA, TB, VA, VB = map(int, input().split())

    # 상혁이는 A만 가능, 도훈이는 A, B 모두 가능
    # 도훈이가 B를 모두 처리해야 함 (필수)
    time_B = TB * VB

    # 도훈이가 B를 처리하는 동안 상혁이가 A를 최대한 처리
    # 상혁이가 처리할 수 있는 A의 개수
    max_A_by_sanghyuk = time_B // TA

    # 상혁이가 처리한 후 남은 A의 개수
    remaining_A = max(0, VA - max_A_by_sanghyuk)

    # 두 가지 경우 고려:
    # 1. 상혁이가 time_B 동안 A를 처리하고, 도훈이가 남은 A를 처리
    # 2. 상혁이가 B보다 더 오래 A를 처리

    # 도훈이: B 모두 + 남은 A, 상혁이: 가능한 만큼 A
    # 최적: 이분탐색으로 최소 시간 찾기

    lo, hi = time_B, (VA * TA + VB * TB)
    ans = hi

    while lo <= hi:
        mid = (lo + hi) // 2
        # mid 시간 동안:
        # 상혁이가 처리할 수 있는 A 개수
        a_by_s = mid // TA
        # 도훈이가 처리해야 할 A 개수
        a_by_d = max(0, VA - a_by_s)
        # 도훈이 필요 시간: B 모두 + 남은 A
        time_d = TB * VB + TA * a_by_d

        if time_d <= mid:
            ans = mid
            hi = mid - 1
        else:
            lo = mid + 1

    print(ans)
''',
        "java": '''// 가상 검증 기술 - 두 연구원이 검증 업무를 분담하여 최소 시간 계산
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int Q = Integer.parseInt(br.readLine().trim());

        for (int q = 0; q < Q; q++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long TA = Long.parseLong(st.nextToken());
            long TB = Long.parseLong(st.nextToken());
            long VA = Long.parseLong(st.nextToken());
            long VB = Long.parseLong(st.nextToken());

            // 이분탐색으로 최소 시간 찾기
            long lo = TB * VB;  // 도훈이가 B만 처리하는 시간
            long hi = TA * VA + TB * VB;  // 도훈이 혼자 모두 처리하는 시간
            long ans = hi;

            while (lo <= hi) {
                long mid = (lo + hi) / 2;
                // mid 시간 동안 상혁이가 처리할 수 있는 A 개수
                long aByS = mid / TA;
                // 도훈이가 처리해야 할 A 개수
                long aByD = Math.max(0, VA - aByS);
                // 도훈이 필요 시간
                long timeD = TB * VB + TA * aByD;

                if (timeD <= mid) {
                    ans = mid;
                    hi = mid - 1;
                } else {
                    lo = mid + 1;
                }
            }

            sb.append(ans).append("\\n");
        }

        System.out.print(sb);
    }
}
''',
        "cpp": '''// 가상 검증 기술 - 두 연구원이 검증 업무를 분담하여 최소 시간 계산
#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int Q;
    cin >> Q;

    while (Q--) {
        long long TA, TB, VA, VB;
        cin >> TA >> TB >> VA >> VB;

        // 이분탐색으로 최소 시간 찾기
        long long lo = TB * VB;  // 도훈이가 B만 처리하는 시간
        long long hi = TA * VA + TB * VB;  // 도훈이 혼자 모두 처리하는 시간
        long long ans = hi;

        while (lo <= hi) {
            long long mid = (lo + hi) / 2;
            // mid 시간 동안 상혁이가 처리할 수 있는 A 개수
            long long aByS = mid / TA;
            // 도훈이가 처리해야 할 A 개수
            long long aByD = max(0LL, VA - aByS);
            // 도훈이 필요 시간
            long long timeD = TB * VB + TA * aByD;

            if (timeD <= mid) {
                ans = mid;
                hi = mid - 1;
            } else {
                lo = mid + 1;
            }
        }

        cout << ans << "\\n";
    }

    return 0;
}
'''
    },
    4074: {  # baekjoon_14231 - 박스 포장
        "python": '''# 박스 포장 - LIS(최장 증가 부분 수열) 문제
import sys
input = sys.stdin.readline

n = int(input())
A = list(map(int, input().split()))

# dp[i] = i번째 박스까지 고려했을 때 최대 포장 개수
dp = [1] * n

for i in range(1, n):
    for j in range(i):
        # 앞의 박스가 뒤의 박스보다 작아야 넣을 수 있음
        if A[j] < A[i]:
            dp[i] = max(dp[i], dp[j] + 1)

print(max(dp))
''',
        "java": '''// 박스 포장 - LIS(최장 증가 부분 수열) 문제
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] A = new int[n];
        for (int i = 0; i < n; i++) {
            A[i] = Integer.parseInt(st.nextToken());
        }

        // dp[i] = i번째 박스까지 고려했을 때 최대 포장 개수
        int[] dp = new int[n];
        Arrays.fill(dp, 1);

        int maxVal = 1;
        for (int i = 1; i < n; i++) {
            for (int j = 0; j < i; j++) {
                // 앞의 박스가 뒤의 박스보다 작아야 넣을 수 있음
                if (A[j] < A[i]) {
                    dp[i] = Math.max(dp[i], dp[j] + 1);
                }
            }
            maxVal = Math.max(maxVal, dp[i]);
        }

        System.out.println(maxVal);
    }
}
''',
        "cpp": '''// 박스 포장 - LIS(최장 증가 부분 수열) 문제
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> A(n);
    for (int i = 0; i < n; i++) {
        cin >> A[i];
    }

    // dp[i] = i번째 박스까지 고려했을 때 최대 포장 개수
    vector<int> dp(n, 1);

    int maxVal = 1;
    for (int i = 1; i < n; i++) {
        for (int j = 0; j < i; j++) {
            // 앞의 박스가 뒤의 박스보다 작아야 넣을 수 있음
            if (A[j] < A[i]) {
                dp[i] = max(dp[i], dp[j] + 1);
            }
        }
        maxVal = max(maxVal, dp[i]);
    }

    cout << maxVal << endl;

    return 0;
}
'''
    },
    4086: {  # baekjoon_17357 - 자동차가 차주 김표준의 편을 들면?
        "python": '''# 표준편차가 최대가 되는 구간의 시작 인덱스 찾기
import sys
input = sys.stdin.readline

n = int(input())
A = list(map(int, input().split()))

# 표준편차가 최대 = 분산이 최대
# 분산 = (sum(x^2)/n) - (sum(x)/n)^2

for k in range(1, n + 1):
    # 길이가 k인 모든 구간에 대해 분산 계산
    max_var = -1
    max_idx = 1

    for i in range(n - k + 1):
        # 구간 [i, i+k-1]
        segment = A[i:i+k]
        s = sum(segment)
        s2 = sum(x * x for x in segment)
        # 분산 = E[X^2] - E[X]^2
        var = s2 * k - s * s  # k로 나누기 전 값 비교 (순서 유지)

        if var > max_var:
            max_var = var
            max_idx = i + 1  # 1-indexed

    print(max_idx)
''',
        "java": '''// 표준편차가 최대가 되는 구간의 시작 인덱스 찾기
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        long[] A = new long[n];
        for (int i = 0; i < n; i++) {
            A[i] = Long.parseLong(st.nextToken());
        }

        // 표준편차가 최대 = 분산이 최대
        for (int k = 1; k <= n; k++) {
            long maxVar = -1;
            int maxIdx = 1;

            for (int i = 0; i <= n - k; i++) {
                // 구간 [i, i+k-1]
                long s = 0, s2 = 0;
                for (int j = i; j < i + k; j++) {
                    s += A[j];
                    s2 += A[j] * A[j];
                }
                // 분산 비교: k * s2 - s * s
                long var = (long) k * s2 - s * s;

                if (var > maxVar) {
                    maxVar = var;
                    maxIdx = i + 1;  // 1-indexed
                }
            }

            sb.append(maxIdx).append("\\n");
        }

        System.out.print(sb);
    }
}
''',
        "cpp": '''// 표준편차가 최대가 되는 구간의 시작 인덱스 찾기
#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<long long> A(n);
    for (int i = 0; i < n; i++) {
        cin >> A[i];
    }

    // 표준편차가 최대 = 분산이 최대
    for (int k = 1; k <= n; k++) {
        long long maxVar = -1;
        int maxIdx = 1;

        for (int i = 0; i <= n - k; i++) {
            // 구간 [i, i+k-1]
            long long s = 0, s2 = 0;
            for (int j = i; j < i + k; j++) {
                s += A[j];
                s2 += A[j] * A[j];
            }
            // 분산 비교: k * s2 - s * s
            long long var = (long long) k * s2 - s * s;

            if (var > maxVar) {
                maxVar = var;
                maxIdx = i + 1;  // 1-indexed
            }
        }

        cout << maxIdx << "\\n";
    }

    return 0;
}
'''
    },
    4087: {  # baekjoon_27922 - 현대모비스 입사 프로젝트
        "python": '''# 현대모비스 입사 프로젝트 - K개 강의 선택하여 두 역량 합 최대화
import sys
input = sys.stdin.readline

N, K = map(int, input().split())
lectures = []
for _ in range(N):
    a, b, c = map(int, input().split())
    lectures.append((a, b, c))

# 세 가지 조합: (a+b), (b+c), (a+c)
# 각 조합에서 상위 K개 선택
ans = 0

# a+b 기준
lectures_ab = sorted(lectures, key=lambda x: x[0] + x[1], reverse=True)
total = sum(lectures_ab[i][0] + lectures_ab[i][1] for i in range(K))
ans = max(ans, total)

# b+c 기준
lectures_bc = sorted(lectures, key=lambda x: x[1] + x[2], reverse=True)
total = sum(lectures_bc[i][1] + lectures_bc[i][2] for i in range(K))
ans = max(ans, total)

# a+c 기준
lectures_ac = sorted(lectures, key=lambda x: x[0] + x[2], reverse=True)
total = sum(lectures_ac[i][0] + lectures_ac[i][2] for i in range(K))
ans = max(ans, total)

print(ans)
''',
        "java": '''// 현대모비스 입사 프로젝트 - K개 강의 선택하여 두 역량 합 최대화
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        int[][] lectures = new int[N][3];
        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            lectures[i][0] = Integer.parseInt(st.nextToken());
            lectures[i][1] = Integer.parseInt(st.nextToken());
            lectures[i][2] = Integer.parseInt(st.nextToken());
        }

        long ans = 0;

        // a+b 기준 정렬
        Integer[] idx = new Integer[N];
        for (int i = 0; i < N; i++) idx[i] = i;

        // a+b 기준
        final int[][] lec = lectures;
        Arrays.sort(idx, (x, y) -> (lec[y][0] + lec[y][1]) - (lec[x][0] + lec[x][1]));
        long total = 0;
        for (int i = 0; i < K; i++) {
            total += lec[idx[i]][0] + lec[idx[i]][1];
        }
        ans = Math.max(ans, total);

        // b+c 기준
        Arrays.sort(idx, (x, y) -> (lec[y][1] + lec[y][2]) - (lec[x][1] + lec[x][2]));
        total = 0;
        for (int i = 0; i < K; i++) {
            total += lec[idx[i]][1] + lec[idx[i]][2];
        }
        ans = Math.max(ans, total);

        // a+c 기준
        Arrays.sort(idx, (x, y) -> (lec[y][0] + lec[y][2]) - (lec[x][0] + lec[x][2]));
        total = 0;
        for (int i = 0; i < K; i++) {
            total += lec[idx[i]][0] + lec[idx[i]][2];
        }
        ans = Math.max(ans, total);

        System.out.println(ans);
    }
}
''',
        "cpp": '''// 현대모비스 입사 프로젝트 - K개 강의 선택하여 두 역량 합 최대화
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, K;
    cin >> N >> K;

    vector<tuple<int, int, int>> lectures(N);
    for (int i = 0; i < N; i++) {
        int a, b, c;
        cin >> a >> b >> c;
        lectures[i] = {a, b, c};
    }

    long long ans = 0;

    // a+b 기준
    sort(lectures.begin(), lectures.end(), [](auto& x, auto& y) {
        return get<0>(x) + get<1>(x) > get<0>(y) + get<1>(y);
    });
    long long total = 0;
    for (int i = 0; i < K; i++) {
        total += get<0>(lectures[i]) + get<1>(lectures[i]);
    }
    ans = max(ans, total);

    // b+c 기준
    sort(lectures.begin(), lectures.end(), [](auto& x, auto& y) {
        return get<1>(x) + get<2>(x) > get<1>(y) + get<2>(y);
    });
    total = 0;
    for (int i = 0; i < K; i++) {
        total += get<1>(lectures[i]) + get<2>(lectures[i]);
    }
    ans = max(ans, total);

    // a+c 기준
    sort(lectures.begin(), lectures.end(), [](auto& x, auto& y) {
        return get<0>(x) + get<2>(x) > get<0>(y) + get<2>(y);
    });
    total = 0;
    for (int i = 0; i < K; i++) {
        total += get<0>(lectures[i]) + get<2>(lectures[i]);
    }
    ans = max(ans, total);

    cout << ans << endl;

    return 0;
}
'''
    },
    4092: {  # baekjoon_6487 - 두 직선의 교차 여부
        "python": '''# 두 직선의 교차 여부 - 직선 방정식 이용
import sys
input = sys.stdin.readline

def solve(x1, y1, x2, y2, x3, y3, x4, y4):
    # 직선 1: (x1,y1) - (x2,y2)
    # 직선 2: (x3,y3) - (x4,y4)

    # 방향 벡터
    dx1, dy1 = x2 - x1, y2 - y1
    dx2, dy2 = x4 - x3, y4 - y3

    # 외적 (평행 판정)
    cross = dx1 * dy2 - dy1 * dx2

    if cross == 0:
        # 평행: 같은 직선인지 확인
        # (x3-x1, y3-y1)이 (dx1, dy1)과 평행한지
        cross2 = (x3 - x1) * dy1 - (y3 - y1) * dx1
        if cross2 == 0:
            return "LINE"
        else:
            return "NONE"

    # 교점 계산: 매개변수 방정식
    # P1 + t * D1 = P3 + s * D2
    # x1 + t * dx1 = x3 + s * dx2
    # y1 + t * dy1 = y3 + s * dy2

    # t = ((x3-x1)*dy2 - (y3-y1)*dx2) / cross
    t = ((x3 - x1) * dy2 - (y3 - y1) * dx2) / cross

    x = x1 + t * dx1
    y = y1 + t * dy1

    return f"POINT {x:.2f} {y:.2f}"

N = int(input())
for _ in range(N):
    coords = list(map(int, input().split()))
    x1, y1, x2, y2, x3, y3, x4, y4 = coords
    print(solve(x1, y1, x2, y2, x3, y3, x4, y4))
''',
        "java": '''// 두 직선의 교차 여부 - 직선 방정식 이용
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int N = Integer.parseInt(br.readLine().trim());

        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            double x1 = Double.parseDouble(st.nextToken());
            double y1 = Double.parseDouble(st.nextToken());
            double x2 = Double.parseDouble(st.nextToken());
            double y2 = Double.parseDouble(st.nextToken());
            double x3 = Double.parseDouble(st.nextToken());
            double y3 = Double.parseDouble(st.nextToken());
            double x4 = Double.parseDouble(st.nextToken());
            double y4 = Double.parseDouble(st.nextToken());

            // 방향 벡터
            double dx1 = x2 - x1, dy1 = y2 - y1;
            double dx2 = x4 - x3, dy2 = y4 - y3;

            // 외적 (평행 판정)
            double cross = dx1 * dy2 - dy1 * dx2;

            if (Math.abs(cross) < 1e-9) {
                // 평행: 같은 직선인지 확인
                double cross2 = (x3 - x1) * dy1 - (y3 - y1) * dx1;
                if (Math.abs(cross2) < 1e-9) {
                    sb.append("LINE\\n");
                } else {
                    sb.append("NONE\\n");
                }
            } else {
                // 교점 계산
                double t = ((x3 - x1) * dy2 - (y3 - y1) * dx2) / cross;
                double x = x1 + t * dx1;
                double y = y1 + t * dy1;
                sb.append(String.format("POINT %.2f %.2f\\n", x, y));
            }
        }

        System.out.print(sb);
    }
}
''',
        "cpp": '''// 두 직선의 교차 여부 - 직선 방정식 이용
#include <iostream>
#include <cstdio>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    for (int i = 0; i < N; i++) {
        double x1, y1, x2, y2, x3, y3, x4, y4;
        cin >> x1 >> y1 >> x2 >> y2 >> x3 >> y3 >> x4 >> y4;

        // 방향 벡터
        double dx1 = x2 - x1, dy1 = y2 - y1;
        double dx2 = x4 - x3, dy2 = y4 - y3;

        // 외적 (평행 판정)
        double cross = dx1 * dy2 - dy1 * dx2;

        if (fabs(cross) < 1e-9) {
            // 평행: 같은 직선인지 확인
            double cross2 = (x3 - x1) * dy1 - (y3 - y1) * dx1;
            if (fabs(cross2) < 1e-9) {
                cout << "LINE\\n";
            } else {
                cout << "NONE\\n";
            }
        } else {
            // 교점 계산
            double t = ((x3 - x1) * dy2 - (y3 - y1) * dx2) / cross;
            double x = x1 + t * dx1;
            double y = y1 + t * dy1;
            printf("POINT %.2f %.2f\\n", x, y);
        }
    }

    return 0;
}
'''
    },
    4093: {  # baekjoon_29808 - 너의 수능 점수가 궁금해
        "python": '''# 너의 수능 점수가 궁금해 - 학번에서 수능 점수 역산
import sys
input = sys.stdin.readline

S = int(input())

# 학번 = 4763 * ((국어-영어 차이) * 508 or 108 + (수학-탐구 차이) * 212 or 305)
# S = 4763 * (val1 + val2)

if S % 4763 != 0:
    print(0)
else:
    target = S // 4763
    # target = diff1 * coef1 + diff2 * coef2
    # diff1 in [0, 200], coef1 in {508, 108}
    # diff2 in [0, 200], coef2 in {212, 305}

    results = []

    for coef1 in [508, 108]:
        for coef2 in [212, 305]:
            # diff1 * coef1 + diff2 * coef2 = target
            for diff1 in range(201):
                remainder = target - diff1 * coef1
                if remainder < 0:
                    break
                if remainder % coef2 == 0:
                    diff2 = remainder // coef2
                    if 0 <= diff2 <= 200:
                        results.append((diff1, diff2))

    # 중복 제거 및 정렬
    results = sorted(set(results))

    print(len(results))
    for d1, d2 in results:
        print(d1, d2)
''',
        "java": '''// 너의 수능 점수가 궁금해 - 학번에서 수능 점수 역산
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        long S = Long.parseLong(br.readLine().trim());

        // 학번 = 4763 * (val1 + val2)
        if (S % 4763 != 0) {
            System.out.println(0);
            return;
        }

        long target = S / 4763;
        TreeSet<String> results = new TreeSet<>();

        int[] coefs1 = {508, 108};
        int[] coefs2 = {212, 305};

        for (int coef1 : coefs1) {
            for (int coef2 : coefs2) {
                for (int diff1 = 0; diff1 <= 200; diff1++) {
                    long remainder = target - (long) diff1 * coef1;
                    if (remainder < 0) break;
                    if (remainder % coef2 == 0) {
                        long diff2 = remainder / coef2;
                        if (diff2 >= 0 && diff2 <= 200) {
                            // 정렬을 위한 키 생성
                            String key = String.format("%03d %03d", diff1, diff2);
                            results.add(key);
                        }
                    }
                }
            }
        }

        sb.append(results.size()).append("\\n");
        for (String r : results) {
            String[] parts = r.split(" ");
            sb.append(Integer.parseInt(parts[0])).append(" ").append(Integer.parseInt(parts[1])).append("\\n");
        }

        System.out.print(sb);
    }
}
''',
        "cpp": '''// 너의 수능 점수가 궁금해 - 학번에서 수능 점수 역산
#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long S;
    cin >> S;

    // 학번 = 4763 * (val1 + val2)
    if (S % 4763 != 0) {
        cout << 0 << endl;
        return 0;
    }

    long long target = S / 4763;
    set<pair<int, int>> results;

    int coefs1[] = {508, 108};
    int coefs2[] = {212, 305};

    for (int coef1 : coefs1) {
        for (int coef2 : coefs2) {
            for (int diff1 = 0; diff1 <= 200; diff1++) {
                long long remainder = target - (long long) diff1 * coef1;
                if (remainder < 0) break;
                if (remainder % coef2 == 0) {
                    long long diff2 = remainder / coef2;
                    if (diff2 >= 0 && diff2 <= 200) {
                        results.insert({diff1, (int)diff2});
                    }
                }
            }
        }
    }

    cout << results.size() << "\\n";
    for (auto& p : results) {
        cout << p.first << " " << p.second << "\\n";
    }

    return 0;
}
'''
    },
    4107: {  # baekjoon_21869 - Maximum Bishop
        "python": '''# Maximum Bishop - N x N 체스판에 최대 비숍 배치
import sys

n = int(input())

# 비숍은 대각선으로 이동하므로, 각 대각선에 최대 1개 배치
# N=1일 때: 1개
# N>=2일 때: 첫 행과 마지막 열에 배치하면 2*(N-1)개 가능하지만
# 실제로는 첫 행에 N개, 마지막 행에 N개 (겹치는 것 제외) = 2N - 2개
# 더 정확히: 2*N - 2 (N >= 2)

if n == 1:
    print(1)
    print(1, 1)
else:
    # 최대 개수: 2*N - 2
    print(2 * n - 2)
    # 첫 번째 행에 모두 배치
    for col in range(1, n + 1):
        print(1, col)
    # 마지막 행에 2~N-1 열에 배치 (1열과 N열은 첫 행과 대각선 충돌 가능하므로 제외)
    for col in range(2, n):
        print(n, col)
''',
        "java": '''// Maximum Bishop - N x N 체스판에 최대 비숍 배치
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine().trim());

        // 비숍은 대각선으로 이동
        // N=1일 때: 1개
        // N>=2일 때: 2*N - 2개

        if (n == 1) {
            sb.append(1).append("\\n");
            sb.append("1 1\\n");
        } else {
            // 최대 개수: 2*N - 2
            sb.append(2 * n - 2).append("\\n");
            // 첫 번째 행에 모두 배치
            for (int col = 1; col <= n; col++) {
                sb.append(1).append(" ").append(col).append("\\n");
            }
            // 마지막 행에 2~N-1 열에 배치
            for (int col = 2; col < n; col++) {
                sb.append(n).append(" ").append(col).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
''',
        "cpp": '''// Maximum Bishop - N x N 체스판에 최대 비숍 배치
#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    // 비숍은 대각선으로 이동
    // N=1일 때: 1개
    // N>=2일 때: 2*N - 2개

    if (n == 1) {
        cout << 1 << "\\n";
        cout << "1 1\\n";
    } else {
        // 최대 개수: 2*N - 2
        cout << 2 * n - 2 << "\\n";
        // 첫 번째 행에 모두 배치
        for (int col = 1; col <= n; col++) {
            cout << 1 << " " << col << "\\n";
        }
        // 마지막 행에 2~N-1 열에 배치
        for (int col = 2; col < n; col++) {
            cout << n << " " << col << "\\n";
        }
    }

    return 0;
}
'''
    },
    4110: {  # baekjoon_16969 - 차량 번호판 2
        "python": '''# 차량 번호판 2 - 연속 중복 불가 조건으로 가능한 번호판 개수
import sys
input = sys.stdin.readline

MOD = 1000000009

s = input().strip()
n = len(s)

# 첫 글자: c이면 26가지, d이면 10가지
if s[0] == 'c':
    result = 26
else:
    result = 10

# 이후 글자: 이전과 같은 종류면 (개수-1), 다른 종류면 그대로
for i in range(1, n):
    if s[i] == s[i-1]:
        # 연속 중복 불가
        if s[i] == 'c':
            result = (result * 25) % MOD
        else:
            result = (result * 9) % MOD
    else:
        # 다른 종류
        if s[i] == 'c':
            result = (result * 26) % MOD
        else:
            result = (result * 10) % MOD

print(result)
''',
        "java": '''// 차량 번호판 2 - 연속 중복 불가 조건으로 가능한 번호판 개수
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        final long MOD = 1000000009L;

        String s = br.readLine().trim();
        int n = s.length();

        // 첫 글자: c이면 26가지, d이면 10가지
        long result = (s.charAt(0) == 'c') ? 26 : 10;

        // 이후 글자
        for (int i = 1; i < n; i++) {
            if (s.charAt(i) == s.charAt(i-1)) {
                // 연속 중복 불가
                if (s.charAt(i) == 'c') {
                    result = (result * 25) % MOD;
                } else {
                    result = (result * 9) % MOD;
                }
            } else {
                // 다른 종류
                if (s.charAt(i) == 'c') {
                    result = (result * 26) % MOD;
                } else {
                    result = (result * 10) % MOD;
                }
            }
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''// 차량 번호판 2 - 연속 중복 불가 조건으로 가능한 번호판 개수
#include <iostream>
#include <string>
using namespace std;

const long long MOD = 1000000009;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    cin >> s;
    int n = s.length();

    // 첫 글자: c이면 26가지, d이면 10가지
    long long result = (s[0] == 'c') ? 26 : 10;

    // 이후 글자
    for (int i = 1; i < n; i++) {
        if (s[i] == s[i-1]) {
            // 연속 중복 불가
            if (s[i] == 'c') {
                result = (result * 25) % MOD;
            } else {
                result = (result * 9) % MOD;
            }
        } else {
            // 다른 종류
            if (s[i] == 'c') {
                result = (result * 26) % MOD;
            } else {
                result = (result * 10) % MOD;
            }
        }
    }

    cout << result << endl;

    return 0;
}
'''
    },
    4111: {  # baekjoon_26123 - 외계 침략자 윤이
        "python": '''# 외계 침략자 윤이 - D일 동안 가장 높은 빌딩에 레이저 발사
import sys
input = sys.stdin.readline

N, D = map(int, input().split())
heights = list(map(int, input().split()))

# 높이 내림차순 정렬
heights.sort(reverse=True)

# 누적 레이저 횟수 계산
# 높이가 h1 > h2 > h3 > ... 일 때
# h1인 빌딩이 1개면 h1 - h2일 동안 1개씩
# h2인 빌딩이 2개면 h2 - h3일 동안 2개씩...

total = 0
day = 0

for i in range(N):
    if day >= D:
        break

    # 현재 높이에서 다음 높이까지
    next_height = heights[i + 1] if i + 1 < N else 0
    days_needed = heights[i] - next_height
    days_used = min(days_needed, D - day)

    total += days_used * (i + 1)
    day += days_used

print(total)
''',
        "java": '''// 외계 침략자 윤이 - D일 동안 가장 높은 빌딩에 레이저 발사
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        long D = Long.parseLong(st.nextToken());

        long[] heights = new long[N];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            heights[i] = Long.parseLong(st.nextToken());
        }

        // 높이 내림차순 정렬
        Long[] h = new Long[N];
        for (int i = 0; i < N; i++) h[i] = heights[i];
        Arrays.sort(h, Collections.reverseOrder());

        long total = 0;
        long day = 0;

        for (int i = 0; i < N; i++) {
            if (day >= D) break;

            // 현재 높이에서 다음 높이까지
            long nextHeight = (i + 1 < N) ? h[i + 1] : 0;
            long daysNeeded = h[i] - nextHeight;
            long daysUsed = Math.min(daysNeeded, D - day);

            total += daysUsed * (i + 1);
            day += daysUsed;
        }

        System.out.println(total);
    }
}
''',
        "cpp": '''// 외계 침략자 윤이 - D일 동안 가장 높은 빌딩에 레이저 발사
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    long long D;
    cin >> N >> D;

    vector<long long> heights(N);
    for (int i = 0; i < N; i++) {
        cin >> heights[i];
    }

    // 높이 내림차순 정렬
    sort(heights.begin(), heights.end(), greater<long long>());

    long long total = 0;
    long long day = 0;

    for (int i = 0; i < N; i++) {
        if (day >= D) break;

        // 현재 높이에서 다음 높이까지
        long long nextHeight = (i + 1 < N) ? heights[i + 1] : 0;
        long long daysNeeded = heights[i] - nextHeight;
        long long daysUsed = min(daysNeeded, D - day);

        total += daysUsed * (i + 1);
        day += daysUsed;
    }

    cout << total << endl;

    return 0;
}
'''
    },
    4115: {  # baekjoon_24494 - Herdle
        "python": '''# Herdle - 3x3 그리드 맞추기 게임 (Wordle 유사)
import sys
input = sys.stdin.readline

# 추측 그리드 읽기
guess = []
for _ in range(3):
    guess.append(input().strip())

# 정답 그리드 읽기
answer = []
for _ in range(3):
    answer.append(input().strip())

# 초록색 (정확한 위치) 개수
green = 0
for i in range(3):
    for j in range(3):
        if guess[i][j] == answer[i][j]:
            green += 1

# 노란색 (다른 위치에 존재) 개수
# 각 문자별로 카운트
from collections import Counter

# 정답에서 초록이 아닌 문자들
answer_chars = Counter()
guess_chars = Counter()

for i in range(3):
    for j in range(3):
        if guess[i][j] != answer[i][j]:
            answer_chars[answer[i][j]] += 1
            guess_chars[guess[i][j]] += 1

# 노란색: 각 문자에 대해 min(guess 개수, answer 개수)
yellow = 0
for ch in guess_chars:
    yellow += min(guess_chars[ch], answer_chars[ch])

print(green)
print(yellow)
''',
        "java": '''// Herdle - 3x3 그리드 맞추기 게임 (Wordle 유사)
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        // 추측 그리드 읽기
        char[][] guess = new char[3][3];
        for (int i = 0; i < 3; i++) {
            String line = br.readLine().trim();
            for (int j = 0; j < 3; j++) {
                guess[i][j] = line.charAt(j);
            }
        }

        // 정답 그리드 읽기
        char[][] answer = new char[3][3];
        for (int i = 0; i < 3; i++) {
            String line = br.readLine().trim();
            for (int j = 0; j < 3; j++) {
                answer[i][j] = line.charAt(j);
            }
        }

        // 초록색 (정확한 위치) 개수
        int green = 0;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (guess[i][j] == answer[i][j]) {
                    green++;
                }
            }
        }

        // 노란색 계산을 위한 카운트
        int[] answerCount = new int[26];
        int[] guessCount = new int[26];

        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (guess[i][j] != answer[i][j]) {
                    answerCount[answer[i][j] - 'A']++;
                    guessCount[guess[i][j] - 'A']++;
                }
            }
        }

        // 노란색: 각 문자에 대해 min(guess, answer)
        int yellow = 0;
        for (int c = 0; c < 26; c++) {
            yellow += Math.min(guessCount[c], answerCount[c]);
        }

        System.out.println(green);
        System.out.println(yellow);
    }
}
''',
        "cpp": '''// Herdle - 3x3 그리드 맞추기 게임 (Wordle 유사)
#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    // 추측 그리드 읽기
    string guess[3];
    for (int i = 0; i < 3; i++) {
        cin >> guess[i];
    }

    // 정답 그리드 읽기
    string answer[3];
    for (int i = 0; i < 3; i++) {
        cin >> answer[i];
    }

    // 초록색 (정확한 위치) 개수
    int green = 0;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (guess[i][j] == answer[i][j]) {
                green++;
            }
        }
    }

    // 노란색 계산을 위한 카운트
    int answerCount[26] = {0};
    int guessCount[26] = {0};

    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (guess[i][j] != answer[i][j]) {
                answerCount[answer[i][j] - 'A']++;
                guessCount[guess[i][j] - 'A']++;
            }
        }
    }

    // 노란색: 각 문자에 대해 min(guess, answer)
    int yellow = 0;
    for (int c = 0; c < 26; c++) {
        yellow += min(guessCount[c], answerCount[c]);
    }

    cout << green << "\\n";
    cout << yellow << "\\n";

    return 0;
}
'''
    },
    4116: {  # baekjoon_25180 - 썸 팰린드롬
        "python": '''# 썸 팰린드롬 - 자릿수 합이 N인 팰린드롬의 최소 자릿수
import sys
input = sys.stdin.readline

N = int(input())

# 팰린드롬에서 자릿수 합을 N으로 만들기
# 홀수 자릿수 k: 가운데 숫자 + 양쪽 쌍 (k-1)/2개
# 각 쌍은 최대 18(9+9) 기여, 가운데는 최대 9
# 짝수 자릿수 k: 쌍 k/2개, 각 쌍은 최대 18

# 1자리: 1~9 가능
if N <= 9:
    print(1)
else:
    # 2자리 이상: 첫 자리는 1~9, 나머지는 0~9
    # 팰린드롬에서 합 N을 만드는 최소 자릿수

    # k자리 팰린드롬의 최대 합:
    # k 홀수: 9 + 18 * ((k-1)//2) = 9 + 9*(k-1) = 9*k
    # k 짝수: 18 * (k//2) = 9*k
    # 즉, k자리 팰린드롬의 최대 합은 9*k (첫 자리 0 불가 고려 안 함)

    # 최소 자릿수: ceil(N / 9)
    # 하지만 홀수면 가운데 하나만 있으므로 조금 다름

    # k자리에서 가능한 최대 합
    # k=1: 9
    # k=2: 9+9=18 (11~99 형태)
    # k=3: 9+9+9=27 (예: 999)
    # k=4: 9*4=36

    # 최소 k = ceil(N/9)
    # 단, k가 홀수면 실제 최대합 = 9 + 18*((k-1)//2) = 9*k
    # k가 짝수면 실제 최대합 = 18*(k//2) = 9*k

    # 결국 최소 k = ceil(N/9)
    k = (N + 8) // 9  # ceil(N/9)
    print(k)
''',
        "java": '''// 썸 팰린드롬 - 자릿수 합이 N인 팰린드롬의 최소 자릿수
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        long N = Long.parseLong(br.readLine().trim());

        // 팰린드롬에서 자릿수 합을 N으로 만들기
        // k자리 팰린드롬의 최대 합은 9*k
        // 최소 k = ceil(N/9)

        if (N <= 9) {
            System.out.println(1);
        } else {
            long k = (N + 8) / 9;  // ceil(N/9)
            System.out.println(k);
        }
    }
}
''',
        "cpp": '''// 썸 팰린드롬 - 자릿수 합이 N인 팰린드롬의 최소 자릿수
#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long N;
    cin >> N;

    // 팰린드롬에서 자릿수 합을 N으로 만들기
    // k자리 팰린드롬의 최대 합은 9*k
    // 최소 k = ceil(N/9)

    if (N <= 9) {
        cout << 1 << endl;
    } else {
        long long k = (N + 8) / 9;  // ceil(N/9)
        cout << k << endl;
    }

    return 0;
}
'''
    },
    4123: {  # baekjoon_31670 - 특별한 마법 공격
        "python": '''# 특별한 마법 공격 - 인접한 두 학생 중 한 명 이상 단죄 (최소 에너지)
import sys
input = sys.stdin.readline

N = int(input())
R = list(map(int, input().split()))

if N == 1:
    # 1명이면 무조건 단죄 (인접한 쌍이 없으므로 0?)
    # 문제: "모든 서로 인접한 두 학생 중 한 명 이상" -> 쌍이 없으면 조건 만족
    print(0)
else:
    # dp[i][0] = i번째 학생을 단죄하지 않은 경우의 최소 에너지
    # dp[i][1] = i번째 학생을 단죄한 경우의 최소 에너지

    # 인접한 두 학생 중 한 명 이상 -> i-1, i 중 적어도 하나 선택
    # 즉, dp[i][0]은 i-1을 반드시 선택해야 함

    INF = float('inf')
    dp = [[INF, INF] for _ in range(N)]

    # 초기화
    dp[0][0] = 0
    dp[0][1] = R[0]

    for i in range(1, N):
        # i를 선택하지 않음 -> i-1을 반드시 선택해야 함
        dp[i][0] = dp[i-1][1]

        # i를 선택함 -> i-1은 선택해도 안 해도 됨
        dp[i][1] = min(dp[i-1][0], dp[i-1][1]) + R[i]

    print(min(dp[N-1][0], dp[N-1][1]))
''',
        "java": '''// 특별한 마법 공격 - 인접한 두 학생 중 한 명 이상 단죄 (최소 에너지)
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());

        if (N == 1) {
            // 1명이면 인접한 쌍이 없으므로 조건 자동 만족
            System.out.println(0);
            return;
        }

        StringTokenizer st = new StringTokenizer(br.readLine());
        long[] R = new long[N];
        for (int i = 0; i < N; i++) {
            R[i] = Long.parseLong(st.nextToken());
        }

        // dp[i][0] = i번째 학생을 단죄하지 않은 경우의 최소 에너지
        // dp[i][1] = i번째 학생을 단죄한 경우의 최소 에너지
        long[][] dp = new long[N][2];

        dp[0][0] = 0;
        dp[0][1] = R[0];

        for (int i = 1; i < N; i++) {
            // i를 선택하지 않음 -> i-1을 반드시 선택해야 함
            dp[i][0] = dp[i-1][1];

            // i를 선택함 -> i-1은 선택해도 안 해도 됨
            dp[i][1] = Math.min(dp[i-1][0], dp[i-1][1]) + R[i];
        }

        System.out.println(Math.min(dp[N-1][0], dp[N-1][1]));
    }
}
''',
        "cpp": '''// 특별한 마법 공격 - 인접한 두 학생 중 한 명 이상 단죄 (최소 에너지)
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    if (N == 1) {
        // 1명이면 인접한 쌍이 없으므로 조건 자동 만족
        cout << 0 << endl;
        return 0;
    }

    vector<long long> R(N);
    for (int i = 0; i < N; i++) {
        cin >> R[i];
    }

    // dp[i][0] = i번째 학생을 단죄하지 않은 경우의 최소 에너지
    // dp[i][1] = i번째 학생을 단죄한 경우의 최소 에너지
    vector<vector<long long>> dp(N, vector<long long>(2));

    dp[0][0] = 0;
    dp[0][1] = R[0];

    for (int i = 1; i < N; i++) {
        // i를 선택하지 않음 -> i-1을 반드시 선택해야 함
        dp[i][0] = dp[i-1][1];

        // i를 선택함 -> i-1은 선택해도 안 해도 됨
        dp[i][1] = min(dp[i-1][0], dp[i-1][1]) + R[i];
    }

    cout << min(dp[N-1][0], dp[N-1][1]) << endl;

    return 0;
}
'''
    },
    4125: {  # baekjoon_28360 - 양동이 게임
        "python": '''# 양동이 게임 - 물 흐름 시뮬레이션 (DAG)
import sys
input = sys.stdin.readline

N, M = map(int, input().split())

# 그래프 구성
out_edges = [[] for _ in range(N + 1)]
for _ in range(M):
    v, w = map(int, input().split())
    out_edges[v].append(w)

# 각 양동이에 담긴 물의 양 계산
water = [0.0] * (N + 1)
water[1] = 100.0  # 1번 양동이에 100 부음

# 위상 정렬 순서로 처리 (번호가 작은 것이 위에 있음)
for v in range(1, N + 1):
    if water[v] > 0 and len(out_edges[v]) > 0:
        # 물을 균등하게 분배
        amount = water[v] / len(out_edges[v])
        for w in out_edges[v]:
            water[w] += amount
        water[v] = 0  # 다 흘러나감

# 최대 물의 양
max_water = max(water)
print(max_water)
''',
        "java": '''// 양동이 게임 - 물 흐름 시뮬레이션 (DAG)
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        // 그래프 구성
        List<List<Integer>> outEdges = new ArrayList<>();
        for (int i = 0; i <= N; i++) {
            outEdges.add(new ArrayList<>());
        }

        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            int v = Integer.parseInt(st.nextToken());
            int w = Integer.parseInt(st.nextToken());
            outEdges.get(v).add(w);
        }

        // 각 양동이에 담긴 물의 양 계산
        double[] water = new double[N + 1];
        water[1] = 100.0;  // 1번 양동이에 100 부음

        // 위상 정렬 순서로 처리 (번호가 작은 것이 위에 있음)
        for (int v = 1; v <= N; v++) {
            if (water[v] > 0 && outEdges.get(v).size() > 0) {
                // 물을 균등하게 분배
                double amount = water[v] / outEdges.get(v).size();
                for (int w : outEdges.get(v)) {
                    water[w] += amount;
                }
                water[v] = 0;  // 다 흘러나감
            }
        }

        // 최대 물의 양
        double maxWater = 0;
        for (int i = 1; i <= N; i++) {
            maxWater = Math.max(maxWater, water[i]);
        }

        System.out.println(maxWater);
    }
}
''',
        "cpp": '''// 양동이 게임 - 물 흐름 시뮬레이션 (DAG)
#include <iostream>
#include <vector>
#include <algorithm>
#include <iomanip>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    // 그래프 구성
    vector<vector<int>> outEdges(N + 1);

    for (int i = 0; i < M; i++) {
        int v, w;
        cin >> v >> w;
        outEdges[v].push_back(w);
    }

    // 각 양동이에 담긴 물의 양 계산
    vector<double> water(N + 1, 0.0);
    water[1] = 100.0;  // 1번 양동이에 100 부음

    // 위상 정렬 순서로 처리 (번호가 작은 것이 위에 있음)
    for (int v = 1; v <= N; v++) {
        if (water[v] > 0 && outEdges[v].size() > 0) {
            // 물을 균등하게 분배
            double amount = water[v] / outEdges[v].size();
            for (int w : outEdges[v]) {
                water[w] += amount;
            }
            water[v] = 0;  // 다 흘러나감
        }
    }

    // 최대 물의 양
    double maxWater = 0;
    for (int i = 1; i <= N; i++) {
        maxWater = max(maxWater, water[i]);
    }

    cout << fixed << setprecision(10) << maxWater << endl;

    return 0;
}
'''
    },
    4130: {  # baekjoon_17296 - But can you do it in 0.5x A presses?
        "python": '''# A버튼 최소 횟수 - 0.5는 누른 채로 시작하는 것
import sys
input = sys.stdin.readline

N = int(input())
stages = input().split()

# 각 스테이지 값을 실수로 변환
values = []
for s in stages:
    if '.' in s:
        values.append(float(s))
    else:
        values.append(float(s))

# x+0.5는 A버튼을 누른 채로 시작해서 x번 더 누르는 것
# 연속으로 0.5가 나오면 이전 스테이지에서 누르고 있던 걸 이어서 사용 가능

total = 0
holding = False  # 현재 A버튼을 누르고 있는지

for v in values:
    frac = v - int(v)  # 소수 부분

    if frac > 0.4:  # 0.5
        # A버튼을 누른 채로 시작해야 함
        if holding:
            # 이미 누르고 있으므로 int(v)번만 추가
            total += int(v)
        else:
            # 새로 눌러야 함 -> int(v) + 1번
            total += int(v) + 1
        holding = True  # 다음 스테이지도 누른 채로 시작할 수 있음
    else:
        # 정수 -> 그냥 v번
        total += int(v)
        holding = False  # 누르고 있을 필요 없음 (다음 스테이지 상태는 상관없음)
        # 단, 다음 스테이지가 0.5면 새로 눌러야 함

print(int(total))
''',
        "java": '''// A버튼 최소 횟수 - 0.5는 누른 채로 시작하는 것
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        double[] values = new double[N];
        for (int i = 0; i < N; i++) {
            values[i] = Double.parseDouble(st.nextToken());
        }

        // x+0.5는 A버튼을 누른 채로 시작해서 x번 더 누르는 것
        double total = 0;
        boolean holding = false;

        for (int i = 0; i < N; i++) {
            double v = values[i];
            double frac = v - (int) v;

            if (frac > 0.4) {  // 0.5
                if (holding) {
                    total += (int) v;
                } else {
                    total += (int) v + 1;
                }
                holding = true;
            } else {
                total += (int) v;
                holding = false;
            }
        }

        System.out.println((int) total);
    }
}
''',
        "cpp": '''// A버튼 최소 횟수 - 0.5는 누른 채로 시작하는 것
#include <iostream>
#include <string>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    // x+0.5는 A버튼을 누른 채로 시작해서 x번 더 누르는 것
    int total = 0;
    bool holding = false;

    for (int i = 0; i < N; i++) {
        double v;
        cin >> v;
        double frac = v - (int) v;

        if (frac > 0.4) {  // 0.5
            if (holding) {
                total += (int) v;
            } else {
                total += (int) v + 1;
            }
            holding = true;
        } else {
            total += (int) v;
            holding = false;
        }
    }

    cout << total << endl;

    return 0;
}
'''
    },
    4133: {  # baekjoon_4030 - 포켓볼
        "python": '''# 포켓볼 - 삼각수이면서 완전제곱수 + 1인 수 찾기
import sys
import math
input = sys.stdin.readline

def is_triangular(x):
    # x = n*(n+1)/2 -> n^2 + n - 2x = 0
    # n = (-1 + sqrt(1 + 8x)) / 2
    if x <= 0:
        return False
    d = 1 + 8 * x
    sqrt_d = int(math.isqrt(d))
    if sqrt_d * sqrt_d != d:
        return False
    if (sqrt_d - 1) % 2 != 0:
        return False
    return True

def is_perfect_square(x):
    if x < 0:
        return False
    sqrt_x = int(math.isqrt(x))
    return sqrt_x * sqrt_x == x

# 조건: x개를 삼각형, x+1개를 정사각형
# x = n*(n+1)/2 (삼각수)
# x+1 = m^2 (완전제곱수)

# 미리 계산: a < x+1 < b를 만족하는 개수
# x+1이 완전제곱수이면서 x = (x+1) - 1이 삼각수

# 범위 내에서 완전제곱수 찾고, 그 중 -1이 삼각수인 것

case_num = 0
while True:
    line = input().strip()
    if not line:
        continue
    a, b = map(int, line.split())
    if a == 0 and b == 0:
        break

    case_num += 1

    # a < x+1 < b -> x+1 in (a+1, b) = [a+1, b-1]
    # m^2 in [a+1, b-1]

    count = 0
    m_start = int(math.ceil(math.sqrt(a + 1)))
    m_end = int(math.floor(math.sqrt(b - 1)))

    for m in range(m_start, m_end + 1):
        x_plus_1 = m * m
        if a < x_plus_1 < b:
            x = x_plus_1 - 1
            if is_triangular(x):
                count += 1

    print(f"Case {case_num}: {count}")
''',
        "java": '''// 포켓볼 - 삼각수이면서 완전제곱수 + 1인 수 찾기
import java.io.*;
import java.util.*;

public class Main {
    static boolean isTriangular(long x) {
        if (x <= 0) return false;
        long d = 1 + 8 * x;
        long sqrtD = (long) Math.sqrt(d);
        // 정확한 제곱근 확인
        while (sqrtD * sqrtD < d) sqrtD++;
        while (sqrtD * sqrtD > d) sqrtD--;
        if (sqrtD * sqrtD != d) return false;
        if ((sqrtD - 1) % 2 != 0) return false;
        return true;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int caseNum = 0;
        String line;
        while ((line = br.readLine()) != null) {
            StringTokenizer st = new StringTokenizer(line);
            long a = Long.parseLong(st.nextToken());
            long b = Long.parseLong(st.nextToken());

            if (a == 0 && b == 0) break;

            caseNum++;

            int count = 0;
            long mStart = (long) Math.ceil(Math.sqrt(a + 1));
            long mEnd = (long) Math.floor(Math.sqrt(b - 1));

            for (long m = mStart; m <= mEnd; m++) {
                long xPlus1 = m * m;
                if (a < xPlus1 && xPlus1 < b) {
                    long x = xPlus1 - 1;
                    if (isTriangular(x)) {
                        count++;
                    }
                }
            }

            sb.append("Case ").append(caseNum).append(": ").append(count).append("\\n");
        }

        System.out.print(sb);
    }
}
''',
        "cpp": '''// 포켓볼 - 삼각수이면서 완전제곱수 + 1인 수 찾기
#include <iostream>
#include <cmath>
using namespace std;

bool isTriangular(long long x) {
    if (x <= 0) return false;
    long long d = 1 + 8 * x;
    long long sqrtD = (long long) sqrt((double) d);
    // 정확한 제곱근 확인
    while (sqrtD * sqrtD < d) sqrtD++;
    while (sqrtD * sqrtD > d) sqrtD--;
    if (sqrtD * sqrtD != d) return false;
    if ((sqrtD - 1) % 2 != 0) return false;
    return true;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long a, b;
    int caseNum = 0;

    while (cin >> a >> b) {
        if (a == 0 && b == 0) break;

        caseNum++;

        int count = 0;
        long long mStart = (long long) ceil(sqrt((double)(a + 1)));
        long long mEnd = (long long) floor(sqrt((double)(b - 1)));

        for (long long m = mStart; m <= mEnd; m++) {
            long long xPlus1 = m * m;
            if (a < xPlus1 && xPlus1 < b) {
                long long x = xPlus1 - 1;
                if (isTriangular(x)) {
                    count++;
                }
            }
        }

        cout << "Case " << caseNum << ": " << count << "\\n";
    }

    return 0;
}
'''
    },
    4141: {  # baekjoon_1862 - 미터계
        "python": '''# 미터계 - 4를 제외한 9진법
import sys
input = sys.stdin.readline

s = input().strip()

# 4가 없는 숫자 체계 = 9진법
# 0,1,2,3,5,6,7,8,9 -> 0,1,2,3,4,5,6,7,8 (9진법)
# 각 자릿수를 9진법으로 변환

# 미터계 숫자를 실제 거리로 변환
# 각 자릿수를 9진법 자릿수로 매핑
# 0->0, 1->1, 2->2, 3->3, 5->4, 6->5, 7->6, 8->7, 9->8

result = 0
for c in s:
    d = int(c)
    if d > 4:
        d -= 1  # 4 이후의 숫자는 1 감소
    result = result * 9 + d

print(result)
''',
        "java": '''// 미터계 - 4를 제외한 9진법
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        String s = br.readLine().trim();

        // 4가 없는 숫자 체계 = 9진법
        // 각 자릿수를 9진법 자릿수로 매핑

        long result = 0;
        for (int i = 0; i < s.length(); i++) {
            int d = s.charAt(i) - '0';
            if (d > 4) {
                d--;  // 4 이후의 숫자는 1 감소
            }
            result = result * 9 + d;
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''// 미터계 - 4를 제외한 9진법
#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    cin >> s;

    // 4가 없는 숫자 체계 = 9진법
    // 각 자릿수를 9진법 자릿수로 매핑

    long long result = 0;
    for (char c : s) {
        int d = c - '0';
        if (d > 4) {
            d--;  // 4 이후의 숫자는 1 감소
        }
        result = result * 9 + d;
    }

    cout << result << endl;

    return 0;
}
'''
    },
    4145: {  # baekjoon_10981 - HEADING TO WORLD FINALS
        "python": '''# HEADING TO WORLD FINALS - ICPC 순위 정렬 후 상위 K개 대학 팀 선택
import sys
input = sys.stdin.readline

N, K = map(int, input().split())

teams = []
for _ in range(N):
    parts = input().split()
    univ = parts[0]
    team_name = parts[1]
    solved = int(parts[2])
    penalty = int(parts[3])
    teams.append((univ, team_name, solved, penalty))

# 정렬: 푼 문제 수 내림차순, 페널티 오름차순
teams.sort(key=lambda x: (-x[2], x[3]))

# 상위 K개 대학 선택 (각 대학에서 가장 높은 순위 팀 1개만)
selected_univs = set()
result = []

for univ, team_name, solved, penalty in teams:
    if univ not in selected_univs:
        selected_univs.add(univ)
        result.append(team_name)
        if len(result) == K:
            break

for team_name in result:
    print(team_name)
''',
        "java": '''// HEADING TO WORLD FINALS - ICPC 순위 정렬 후 상위 K개 대학 팀 선택
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        List<String[]> teams = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            String univ = st.nextToken();
            String teamName = st.nextToken();
            String solved = st.nextToken();
            String penalty = st.nextToken();
            teams.add(new String[]{univ, teamName, solved, penalty});
        }

        // 정렬: 푼 문제 수 내림차순, 페널티 오름차순
        teams.sort((a, b) -> {
            int solvedA = Integer.parseInt(a[2]);
            int solvedB = Integer.parseInt(b[2]);
            if (solvedA != solvedB) return solvedB - solvedA;
            int penaltyA = Integer.parseInt(a[3]);
            int penaltyB = Integer.parseInt(b[3]);
            return penaltyA - penaltyB;
        });

        // 상위 K개 대학 선택
        Set<String> selectedUnivs = new HashSet<>();
        List<String> result = new ArrayList<>();

        for (String[] team : teams) {
            if (!selectedUnivs.contains(team[0])) {
                selectedUnivs.add(team[0]);
                result.add(team[1]);
                if (result.size() == K) break;
            }
        }

        StringBuilder sb = new StringBuilder();
        for (String teamName : result) {
            sb.append(teamName).append("\\n");
        }
        System.out.print(sb);
    }
}
''',
        "cpp": '''// HEADING TO WORLD FINALS - ICPC 순위 정렬 후 상위 K개 대학 팀 선택
#include <iostream>
#include <vector>
#include <algorithm>
#include <set>
using namespace std;

struct Team {
    string univ, teamName;
    int solved, penalty;
};

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, K;
    cin >> N >> K;

    vector<Team> teams(N);
    for (int i = 0; i < N; i++) {
        cin >> teams[i].univ >> teams[i].teamName >> teams[i].solved >> teams[i].penalty;
    }

    // 정렬: 푼 문제 수 내림차순, 페널티 오름차순
    sort(teams.begin(), teams.end(), [](const Team& a, const Team& b) {
        if (a.solved != b.solved) return a.solved > b.solved;
        return a.penalty < b.penalty;
    });

    // 상위 K개 대학 선택
    set<string> selectedUnivs;
    vector<string> result;

    for (const auto& team : teams) {
        if (selectedUnivs.find(team.univ) == selectedUnivs.end()) {
            selectedUnivs.insert(team.univ);
            result.push_back(team.teamName);
            if ((int)result.size() == K) break;
        }
    }

    for (const auto& teamName : result) {
        cout << teamName << "\\n";
    }

    return 0;
}
'''
    },
    4147: {  # baekjoon_27376 - 참살이길
        "python": '''# 참살이길 - 신호등 시뮬레이션
import sys
input = sys.stdin.readline

n, k = map(int, input().split())

signals = []
for _ in range(k):
    x, t, s = map(int, input().split())
    signals.append((x, t, s))

# 신호등을 위치순으로 정렬
signals.sort()

time = 0  # 현재 시간
pos = 0   # 현재 위치

for x, t, s in signals:
    # x까지 이동하는 데 걸리는 시간
    time += x - pos
    pos = x

    # 현재 시간에 신호등 상태 확인
    # s초 이후에 처음으로 초록불이 됨
    # 그 전에는 빨간불, 이후 t초간 초록, t초간 빨간 반복

    if time < s:
        # 아직 첫 초록불 전 -> 빨간불, s까지 대기
        time = s
    else:
        # s 이후: 주기 2*t
        elapsed = time - s
        cycle_pos = elapsed % (2 * t)

        if cycle_pos < t:
            # 초록불 -> 통과 가능
            pass
        else:
            # 빨간불 -> 다음 초록불까지 대기
            wait = 2 * t - cycle_pos
            time += wait

# 끝점까지 이동
time += n - pos

print(time)
''',
        "java": '''// 참살이길 - 신호등 시뮬레이션
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long n = Long.parseLong(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        long[][] signals = new long[k][3];
        for (int i = 0; i < k; i++) {
            st = new StringTokenizer(br.readLine());
            signals[i][0] = Long.parseLong(st.nextToken());  // x
            signals[i][1] = Long.parseLong(st.nextToken());  // t
            signals[i][2] = Long.parseLong(st.nextToken());  // s
        }

        // 신호등을 위치순으로 정렬
        Arrays.sort(signals, (a, b) -> Long.compare(a[0], b[0]));

        long time = 0;
        long pos = 0;

        for (int i = 0; i < k; i++) {
            long x = signals[i][0];
            long t = signals[i][1];
            long s = signals[i][2];

            // x까지 이동
            time += x - pos;
            pos = x;

            if (time < s) {
                // 아직 첫 초록불 전 -> 빨간불
                time = s;
            } else {
                // s 이후: 주기 2*t
                long elapsed = time - s;
                long cyclePos = elapsed % (2 * t);

                if (cyclePos < t) {
                    // 초록불 -> 통과 가능
                } else {
                    // 빨간불 -> 다음 초록불까지 대기
                    long wait = 2 * t - cyclePos;
                    time += wait;
                }
            }
        }

        // 끝점까지 이동
        time += n - pos;

        System.out.println(time);
    }
}
''',
        "cpp": '''// 참살이길 - 신호등 시뮬레이션
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n;
    int k;
    cin >> n >> k;

    vector<tuple<long long, long long, long long>> signals(k);
    for (int i = 0; i < k; i++) {
        long long x, t, s;
        cin >> x >> t >> s;
        signals[i] = {x, t, s};
    }

    // 신호등을 위치순으로 정렬
    sort(signals.begin(), signals.end());

    long long time = 0;
    long long pos = 0;

    for (int i = 0; i < k; i++) {
        long long x = get<0>(signals[i]);
        long long t = get<1>(signals[i]);
        long long s = get<2>(signals[i]);

        // x까지 이동
        time += x - pos;
        pos = x;

        if (time < s) {
            // 아직 첫 초록불 전 -> 빨간불
            time = s;
        } else {
            // s 이후: 주기 2*t
            long long elapsed = time - s;
            long long cyclePos = elapsed % (2 * t);

            if (cyclePos < t) {
                // 초록불 -> 통과 가능
            } else {
                // 빨간불 -> 다음 초록불까지 대기
                long long wait = 2 * t - cyclePos;
                time += wait;
            }
        }
    }

    // 끝점까지 이동
    time += n - pos;

    cout << time << endl;

    return 0;
}
'''
    },
    4157: {  # baekjoon_30923 - 크냑과 3D 프린터
        "python": '''# 크냑과 3D 프린터 - 3D 히스토그램 겉넓이 계산
import sys
input = sys.stdin.readline

N = int(input())
h = list(map(int, input().split()))

# 각 직육면체: 너비 1, 폭 1, 높이 h[i]
# 겉넓이 계산:
# - 위쪽 면: 모든 막대의 위쪽 = N * 1
# - 아래쪽 면: 모든 막대의 아래쪽 = N * 1
# - 앞/뒤 면: 각 막대마다 높이 * 1 * 2 = 2 * sum(h)
# - 좌/우 면: 인접한 막대 높이 차이

# 위/아래 면
top_bottom = 2 * N

# 앞/뒤 면
front_back = 2 * sum(h)

# 좌/우 면
# 첫 막대 왼쪽: h[0]
# 마지막 막대 오른쪽: h[N-1]
# 인접한 막대 사이: abs(h[i] - h[i-1])

left_right = h[0] + h[N-1]
for i in range(1, N):
    left_right += abs(h[i] - h[i-1])

total = top_bottom + front_back + left_right
print(total)
''',
        "java": '''// 크냑과 3D 프린터 - 3D 히스토그램 겉넓이 계산
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        long[] h = new long[N];
        for (int i = 0; i < N; i++) {
            h[i] = Long.parseLong(st.nextToken());
        }

        // 위/아래 면
        long topBottom = 2L * N;

        // 앞/뒤 면
        long frontBack = 0;
        for (int i = 0; i < N; i++) {
            frontBack += h[i];
        }
        frontBack *= 2;

        // 좌/우 면
        long leftRight = h[0] + h[N-1];
        for (int i = 1; i < N; i++) {
            leftRight += Math.abs(h[i] - h[i-1]);
        }

        long total = topBottom + frontBack + leftRight;
        System.out.println(total);
    }
}
''',
        "cpp": '''// 크냑과 3D 프린터 - 3D 히스토그램 겉넓이 계산
#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    vector<long long> h(N);
    for (int i = 0; i < N; i++) {
        cin >> h[i];
    }

    // 위/아래 면
    long long topBottom = 2LL * N;

    // 앞/뒤 면
    long long frontBack = 0;
    for (int i = 0; i < N; i++) {
        frontBack += h[i];
    }
    frontBack *= 2;

    // 좌/우 면
    long long leftRight = h[0] + h[N-1];
    for (int i = 1; i < N; i++) {
        leftRight += abs(h[i] - h[i-1]);
    }

    long long total = topBottom + frontBack + leftRight;
    cout << total << endl;

    return 0;
}
'''
    },
    4160: {  # baekjoon_33510 - 이상한 나누기
        "python": '''# 이상한 나누기 - 이진수에서 홀수 연산 횟수 계산
import sys
input = sys.stdin.readline

N = int(input())
X = input().strip()

# 이상한 나누기:
# 홀수: N = (N+1)/2
# 짝수: N = N/2

# 이진수에서 관찰:
# 짝수 (끝이 0): 오른쪽 시프트
# 홀수 (끝이 1): +1 후 오른쪽 시프트 = 끝의 1을 0으로 바꾸고 carry

# 홀수 연산 횟수 = 이진수에서 '1'의 개수? 아님
# 연속된 1들 처리 시 carry 발생

# 시뮬레이션:
# 1011 (11)
# 홀수: (11+1)/2 = 6 (110)
# 짝수: 6/2 = 3 (11)
# 홀수: (3+1)/2 = 2 (10)
# 짝수: 2/2 = 1 (1)

# 패턴: 연속된 1들의 그룹 개수를 세면 됨
# 예: 1011 -> 1그룹(1), 0, 1그룹(11) = 2개의 1그룹

# 더 정확히: carry를 고려해야 함
# 1111 -> +1 = 10000 -> 4번 시프트
# 홀수 연산: 1번만

# 결론: 연속된 1의 블록 개수 = 홀수 연산 횟수

# 이진수 문자열에서 '01' 또는 시작이 '1'인 블록 개수
count = 0
prev = '0'
for c in X:
    if c == '1' and prev == '0':
        count += 1
    prev = c

print(count)
''',
        "java": '''// 이상한 나누기 - 이진수에서 홀수 연산 횟수 계산
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());
        String X = br.readLine().trim();

        // 연속된 1의 블록 개수 = 홀수 연산 횟수
        int count = 0;
        char prev = '0';

        for (int i = 0; i < X.length(); i++) {
            char c = X.charAt(i);
            if (c == '1' && prev == '0') {
                count++;
            }
            prev = c;
        }

        System.out.println(count);
    }
}
''',
        "cpp": '''// 이상한 나누기 - 이진수에서 홀수 연산 횟수 계산
#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    string X;
    cin >> X;

    // 연속된 1의 블록 개수 = 홀수 연산 횟수
    int count = 0;
    char prev = '0';

    for (char c : X) {
        if (c == '1' && prev == '0') {
            count++;
        }
        prev = c;
    }

    cout << count << endl;

    return 0;
}
'''
    }
}

def main():
    filepath = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

    # 파일 열기 및 잠금
    with open(filepath, 'r+', encoding='utf-8') as f:
        # 배타적 잠금 획득
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

        try:
            # 데이터 읽기
            data = json.load(f)

            # 솔루션 추가
            for idx, sols in solutions_data.items():
                if idx < len(data):
                    solutions = []
                    for lang in ['python', 'java', 'cpp']:
                        if lang in sols:
                            solutions.append({
                                'language': lang,
                                'code': sols[lang]
                            })
                    data[idx]['solutions'] = solutions
                    print(f"Added solutions to index {idx}: {data[idx].get('id', 'unknown')}")

            # 파일 처음으로 이동하고 쓰기
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()

            print(f"\nSuccessfully updated {len(solutions_data)} problems")

        finally:
            # 잠금 해제
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

if __name__ == '__main__':
    main()
