#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배치 6: 문제 51-60 솔루션 추가"""

import json

# 새로운 솔루션들
new_solutions = {
    "30046": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 홍진수 - H, J, S에 1-9 중복 없이 대입하여 p < q < r 만족하는지 확인
from itertools import permutations

def solve():
    n = int(input())
    P = input().strip()
    Q = input().strip()
    R = input().strip()

    # 1-9에서 3개를 선택하여 H, J, S에 대입
    for perm in permutations(range(1, 10), 3):
        mapping = {'H': perm[0], 'J': perm[1], 'S': perm[2]}

        # 각 문자열을 숫자로 변환
        p = int(''.join(str(mapping[c]) for c in P))
        q = int(''.join(str(mapping[c]) for c in Q))
        r = int(''.join(str(mapping[c]) for c in R))

        if p < q < r:
            print("HJS! HJS! HJS!")
            return

    print("Hmm...")

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    string P, Q, R;
    cin >> n >> P >> Q >> R;

    // 1-9에서 H, J, S에 대입할 값 선택
    int digits[] = {1, 2, 3, 4, 5, 6, 7, 8, 9};

    do {
        int H = digits[0], J = digits[1], S = digits[2];

        // 비교: 숫자로 변환하지 않고 자릿수별로 비교
        // p < q 확인
        bool p_less_q = false, p_eq_q = true;
        for (int i = 0; i < n && p_eq_q; i++) {
            int pv = (P[i] == 'H' ? H : (P[i] == 'J' ? J : S));
            int qv = (Q[i] == 'H' ? H : (Q[i] == 'J' ? J : S));
            if (pv < qv) { p_less_q = true; p_eq_q = false; }
            else if (pv > qv) { p_eq_q = false; }
        }
        if (!p_less_q) continue;

        // q < r 확인
        bool q_less_r = false, q_eq_r = true;
        for (int i = 0; i < n && q_eq_r; i++) {
            int qv = (Q[i] == 'H' ? H : (Q[i] == 'J' ? J : S));
            int rv = (R[i] == 'H' ? H : (R[i] == 'J' ? J : S));
            if (qv < rv) { q_less_r = true; q_eq_r = false; }
            else if (qv > rv) { q_eq_r = false; }
        }
        if (q_less_r) {
            cout << "HJS! HJS! HJS!" << endl;
            return 0;
        }
    } while (next_permutation(digits, digits + 9));

    cout << "Hmm..." << endl;
    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    static int n;
    static String P, Q, R;
    static boolean found = false;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();
        P = sc.next();
        Q = sc.next();
        R = sc.next();

        // 1-9 중 3개 선택하여 순열 생성
        int[] digits = {1, 2, 3, 4, 5, 6, 7, 8, 9};
        permute(digits, 0);

        if (!found) {
            System.out.println("Hmm...");
        }
    }

    static void permute(int[] arr, int k) {
        if (found) return;
        if (k == 3) {
            check(arr[0], arr[1], arr[2]);
            return;
        }
        for (int i = k; i < 9; i++) {
            swap(arr, i, k);
            permute(arr, k + 1);
            swap(arr, i, k);
        }
    }

    static void swap(int[] arr, int i, int j) {
        int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }

    static void check(int H, int J, int S) {
        // p < q 비교
        for (int i = 0; i < n; i++) {
            int pv = val(P.charAt(i), H, J, S);
            int qv = val(Q.charAt(i), H, J, S);
            if (pv < qv) break;
            if (pv > qv) return;
        }
        // q < r 비교
        for (int i = 0; i < n; i++) {
            int qv = val(Q.charAt(i), H, J, S);
            int rv = val(R.charAt(i), H, J, S);
            if (qv < rv) {
                System.out.println("HJS! HJS! HJS!");
                found = true;
                return;
            }
            if (qv > rv) return;
        }
    }

    static int val(char c, int H, int J, int S) {
        if (c == 'H') return H;
        if (c == 'J') return J;
        return S;
    }
}
'''
            }
        ]
    },
    "25487": {
        "solutions": [
            {
                "language": "python",
                "code": '''# (x mod y) = (y mod z) = (z mod x) 조건 만족하는 쌍 개수
# x >= y >= z이면 x mod y = y mod z = z mod x = 0 (단, z mod x에서 z < x이므로 z)
# 사실 x >= y >= z일 때만 가능하고, 이 경우 모두 0이 되려면 x >= y >= z
import sys
input = sys.stdin.readline

def solve():
    T = int(input())
    results = []

    for _ in range(T):
        a, b, c = map(int, input().split())
        # x >= y >= z일 때, z mod x = z (z < x인 경우) 이므로 모두 0이 되려면 z = 0 불가
        # 실제로는 x >= y >= z이고 y가 x의 배수, z가 y의 배수, x가 z의 배수
        # 가장 간단한 경우: x = y = z
        # min(a, b, c)가 답
        results.append(min(a, b, c))

    print('\\n'.join(map(str, results)))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int a, b, c;
        cin >> a >> b >> c;
        // x = y = z인 경우만 조건 만족
        cout << min({a, b, c}) << '\\n';
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            int c = Integer.parseInt(st.nextToken());

            // x = y = z인 경우만 조건 만족
            sb.append(Math.min(a, Math.min(b, c))).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "26122": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 막대 자석 문자열: 앞 절반이 모두 N 또는 모두 S이고, N과 S 개수 동일
# 가장 긴 막대 자석 부분 문자열 찾기
import sys
input = sys.stdin.readline

def solve():
    k = int(input())
    s = input().strip()

    max_len = 0

    # 연속된 같은 문자의 구간을 찾기
    i = 0
    while i < k:
        # 현재 문자로 시작하는 연속 구간
        ch = s[i]
        j = i
        while j < k and s[j] == ch:
            j += 1
        first_len = j - i  # 첫 번째 문자의 연속 길이

        # 다음 문자의 연속 구간
        if j < k:
            ch2 = s[j]
            m = j
            while m < k and s[m] == ch2:
                m += 1
            second_len = m - j  # 두 번째 문자의 연속 길이

            # 막대 자석 문자열 길이 = 2 * min(first_len, second_len)
            max_len = max(max_len, 2 * min(first_len, second_len))

        i = j

    print(max_len)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int k;
    string s;
    cin >> k >> s;

    int maxLen = 0;
    int i = 0;

    while (i < k) {
        char ch = s[i];
        int j = i;
        while (j < k && s[j] == ch) j++;
        int firstLen = j - i;

        if (j < k) {
            char ch2 = s[j];
            int m = j;
            while (m < k && s[m] == ch2) m++;
            int secondLen = m - j;

            maxLen = max(maxLen, 2 * min(firstLen, secondLen));
        }

        i = j;
    }

    cout << maxLen << endl;
    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int k = Integer.parseInt(br.readLine().trim());
        String s = br.readLine().trim();

        int maxLen = 0;
        int i = 0;

        while (i < k) {
            char ch = s.charAt(i);
            int j = i;
            while (j < k && s.charAt(j) == ch) j++;
            int firstLen = j - i;

            if (j < k) {
                char ch2 = s.charAt(j);
                int m = j;
                while (m < k && s.charAt(m) == ch2) m++;
                int secondLen = m - j;

                maxLen = Math.max(maxLen, 2 * Math.min(firstLen, secondLen));
            }

            i = j;
        }

        System.out.println(maxLen);
    }
}
'''
            }
        ]
    },
    "28293": {
        "solutions": [
            {
                "language": "python",
                "code": '''# a^b의 자릿수 계산
# 자릿수 = floor(b * log10(a)) + 1
import math

a, b = map(int, input().split())
# log10(a^b) = b * log10(a)
digits = int(b * math.log10(a)) + 1
print(digits)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <cmath>
using namespace std;

int main() {
    long long a, b;
    cin >> a >> b;

    // 자릿수 = floor(b * log10(a)) + 1
    long long digits = (long long)(b * log10((double)a)) + 1;
    cout << digits << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long a = sc.nextLong();
        long b = sc.nextLong();

        // 자릿수 = floor(b * log10(a)) + 1
        long digits = (long)(b * Math.log10(a)) + 1;
        System.out.println(digits);
    }
}
'''
            }
        ]
    },
    "23631": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 진심 좌우 반복 뛰기 - 정확히 N-1 m 뛴 후 위치와 방향
import sys
input = sys.stdin.readline

def solve():
    T = int(input())
    results = []

    for _ in range(T):
        N, K = map(int, input().split())
        target = N - 1  # 뛰어야 할 거리

        if target == 0:
            results.append("0 R")
            continue

        # i번째 이동: i*K m 이동
        # 누적 거리: K + 2K + 3K + ... + nK = K*n*(n+1)/2
        # K*n*(n+1)/2 >= target인 최소 n 찾기

        # 이진 탐색으로 n 찾기
        lo, hi = 1, 10**8
        while lo < hi:
            mid = (lo + hi) // 2
            total = K * mid * (mid + 1) // 2
            if total >= target:
                hi = mid
            else:
                lo = mid + 1

        n = lo
        # n-1번까지의 누적 거리
        prev_total = K * (n - 1) * n // 2 if n > 0 else 0
        remaining = target - prev_total  # n번째에서 더 가야 할 거리

        # n번째 이동 방향: 홀수면 오른쪽(+), 짝수면 왼쪽(-)
        # 위치 계산: 홀수 이동은 +, 짝수 이동은 -
        # 1번: +K, 2번: -2K, 3번: +3K, 4번: -4K, ...
        # n-1번까지의 위치
        pos = 0
        # 공식: 위치 = sum of (-1)^(i+1) * i * K for i in 1..n-1
        # 홀수 항: +, 짝수 항: -
        # n-1이 짝수면: 위치 = -(n-1)/2 * K
        # n-1이 홀수면: 위치 = ((n-1)+1)/2 * K = n/2 * K
        if n == 1:
            pos = 0
        else:
            m = n - 1
            if m % 2 == 0:
                pos = -(m // 2) * K
            else:
                pos = ((m + 1) // 2) * K

        # n번째 이동 방향
        if n % 2 == 1:  # 오른쪽
            pos += remaining
            # 전환점에 도달했으면 방향 전환
            if remaining == n * K:
                direction = "L"
            else:
                direction = "R"
        else:  # 왼쪽
            pos -= remaining
            if remaining == n * K:
                direction = "R"
            else:
                direction = "L"

        results.append(f"{pos} {direction}")

    print('\\n'.join(results))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        long long N, K;
        cin >> N >> K;
        long long target = N - 1;

        if (target == 0) {
            cout << "0 R\\n";
            continue;
        }

        // K*n*(n+1)/2 >= target인 최소 n
        long long lo = 1, hi = 200000000LL;
        while (lo < hi) {
            long long mid = (lo + hi) / 2;
            long long total = K * mid * (mid + 1) / 2;
            if (total >= target) hi = mid;
            else lo = mid + 1;
        }

        long long n = lo;
        long long prev_total = (n > 1) ? K * (n - 1) * n / 2 : 0;
        long long remaining = target - prev_total;

        // n-1번까지의 위치
        long long pos = 0;
        if (n > 1) {
            long long m = n - 1;
            if (m % 2 == 0) pos = -(m / 2) * K;
            else pos = ((m + 1) / 2) * K;
        }

        char direction;
        if (n % 2 == 1) {
            pos += remaining;
            direction = (remaining == n * K) ? 'L' : 'R';
        } else {
            pos -= remaining;
            direction = (remaining == n * K) ? 'R' : 'L';
        }

        cout << pos << " " << direction << "\\n";
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long N = Long.parseLong(st.nextToken());
            long K = Long.parseLong(st.nextToken());
            long target = N - 1;

            if (target == 0) {
                sb.append("0 R\\n");
                continue;
            }

            // 이진 탐색
            long lo = 1, hi = 200000000L;
            while (lo < hi) {
                long mid = (lo + hi) / 2;
                long total = K * mid * (mid + 1) / 2;
                if (total >= target) hi = mid;
                else lo = mid + 1;
            }

            long n = lo;
            long prevTotal = (n > 1) ? K * (n - 1) * n / 2 : 0;
            long remaining = target - prevTotal;

            long pos = 0;
            if (n > 1) {
                long m = n - 1;
                if (m % 2 == 0) pos = -(m / 2) * K;
                else pos = ((m + 1) / 2) * K;
            }

            char direction;
            if (n % 2 == 1) {
                pos += remaining;
                direction = (remaining == n * K) ? 'L' : 'R';
            } else {
                pos -= remaining;
                direction = (remaining == n * K) ? 'R' : 'L';
            }

            sb.append(pos).append(" ").append(direction).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "26083": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 유통기한 해석 - 세 가지 형식 중 유효한 것으로 해석해도 안전한지
import sys
input = sys.stdin.readline

def is_valid_date(y, m, d):
    """날짜가 유효한지 확인"""
    if m < 1 or m > 12:
        return False
    if d < 1:
        return False

    days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    year = 2000 + y
    # 윤년 확인
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        days_in_month[2] = 29

    return d <= days_in_month[m]

def to_days(y, m, d):
    """날짜를 일수로 변환 (비교용)"""
    return y * 10000 + m * 100 + d

def solve():
    Y, M, D = map(int, input().split())
    today = to_days(Y, M, D)

    N = int(input())
    results = []

    for _ in range(N):
        A, B, C = map(int, input().split())

        valid_dates = []

        # 연도/월/일 형식: A=년, B=월, C=일
        if is_valid_date(A, B, C):
            valid_dates.append(to_days(A, B, C))

        # 일/월/연도 형식: A=일, B=월, C=년
        if is_valid_date(C, B, A):
            valid_dates.append(to_days(C, B, A))

        # 월/일/연도 형식: A=월, B=일, C=년
        if is_valid_date(C, A, B):
            valid_dates.append(to_days(C, A, B))

        if not valid_dates:
            results.append("invalid")
        else:
            # 모든 유효한 해석에서 유통기한이 오늘 이후여야 안전
            if all(d >= today for d in valid_dates):
                results.append("safe")
            else:
                results.append("unsafe")

    print('\\n'.join(results))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
using namespace std;

int daysInMonth[13] = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

bool isLeap(int year) {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

bool isValid(int y, int m, int d) {
    if (m < 1 || m > 12 || d < 1) return false;
    int year = 2000 + y;
    int maxD = daysInMonth[m];
    if (m == 2 && isLeap(year)) maxD = 29;
    return d <= maxD;
}

int toDays(int y, int m, int d) {
    return y * 10000 + m * 100 + d;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int Y, M, D;
    cin >> Y >> M >> D;
    int today = toDays(Y, M, D);

    int N;
    cin >> N;

    while (N--) {
        int A, B, C;
        cin >> A >> B >> C;

        vector<int> valid;

        // 연도/월/일
        if (isValid(A, B, C)) valid.push_back(toDays(A, B, C));
        // 일/월/연도
        if (isValid(C, B, A)) valid.push_back(toDays(C, B, A));
        // 월/일/연도
        if (isValid(C, A, B)) valid.push_back(toDays(C, A, B));

        if (valid.empty()) {
            cout << "invalid\\n";
        } else {
            bool safe = true;
            for (int d : valid) {
                if (d < today) safe = false;
            }
            cout << (safe ? "safe" : "unsafe") << "\\n";
        }
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int[] daysInMonth = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

    static boolean isLeap(int year) {
        return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
    }

    static boolean isValid(int y, int m, int d) {
        if (m < 1 || m > 12 || d < 1) return false;
        int year = 2000 + y;
        int maxD = daysInMonth[m];
        if (m == 2 && isLeap(year)) maxD = 29;
        return d <= maxD;
    }

    static int toDays(int y, int m, int d) {
        return y * 10000 + m * 100 + d;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        StringTokenizer st = new StringTokenizer(br.readLine());
        int Y = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());
        int D = Integer.parseInt(st.nextToken());
        int today = toDays(Y, M, D);

        int N = Integer.parseInt(br.readLine().trim());

        while (N-- > 0) {
            st = new StringTokenizer(br.readLine());
            int A = Integer.parseInt(st.nextToken());
            int B = Integer.parseInt(st.nextToken());
            int C = Integer.parseInt(st.nextToken());

            List<Integer> valid = new ArrayList<>();

            if (isValid(A, B, C)) valid.add(toDays(A, B, C));
            if (isValid(C, B, A)) valid.add(toDays(C, B, A));
            if (isValid(C, A, B)) valid.add(toDays(C, A, B));

            if (valid.isEmpty()) {
                sb.append("invalid\\n");
            } else {
                boolean safe = true;
                for (int d : valid) {
                    if (d < today) safe = false;
                }
                sb.append(safe ? "safe" : "unsafe").append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "31848": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 도토리 분류기 - 구멍 크기 이상이면 떨어짐, 지나갈 때마다 크기 1 감소
import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    holes = list(map(int, input().split()))
    Q = int(input())
    acorns = list(map(int, input().split()))

    # 각 도토리에 대해 떨어지는 구멍 번호 찾기
    # 구멍 i를 지날 때 도토리 크기는 s - i (0-indexed)
    # s - i >= holes[i]이면 떨어짐
    # 즉, holes[i] + i <= s인 최소 i 찾기

    # 전처리: arr[i] = holes[i] + i (0-indexed에서 i는 지난 구멍 수)
    # 실제로 i번째 구멍(1-indexed)을 지날 때 크기는 s - (i-1)
    # s - (i-1) >= holes[i-1]이면 떨어짐
    # holes[i-1] <= s - i + 1
    # holes[i-1] + i - 1 <= s

    arr = [holes[i] + i for i in range(N)]

    # 각 도토리에 대해 arr[i] <= s인 최소 i 찾기
    # prefix min을 사용하여 이진탐색 가능하도록
    # arr의 prefix minimum 배열 생성
    prefix_min = [0] * N
    prefix_min[0] = arr[0]
    for i in range(1, N):
        prefix_min[i] = min(prefix_min[i-1], arr[i])

    results = []
    for s in acorns:
        # prefix_min[i] <= s인 최소 i 찾기
        lo, hi = 0, N - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if prefix_min[mid] <= s:
                hi = mid
            else:
                lo = mid + 1
        results.append(lo + 1)  # 1-indexed

    print(' '.join(map(str, results)))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    vector<long long> holes(N);
    for (int i = 0; i < N; i++) {
        cin >> holes[i];
    }

    // arr[i] = holes[i] + i
    vector<long long> arr(N);
    for (int i = 0; i < N; i++) {
        arr[i] = holes[i] + i;
    }

    // prefix minimum
    vector<long long> prefixMin(N);
    prefixMin[0] = arr[0];
    for (int i = 1; i < N; i++) {
        prefixMin[i] = min(prefixMin[i-1], arr[i]);
    }

    int Q;
    cin >> Q;

    while (Q--) {
        long long s;
        cin >> s;

        // prefixMin[i] <= s인 최소 i
        int lo = 0, hi = N - 1;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (prefixMin[mid] <= s) hi = mid;
            else lo = mid + 1;
        }

        cout << (lo + 1);
        if (Q > 0) cout << ' ';
    }
    cout << '\\n';

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int N = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        long[] holes = new long[N];
        for (int i = 0; i < N; i++) {
            holes[i] = Long.parseLong(st.nextToken());
        }

        // arr[i] = holes[i] + i
        long[] arr = new long[N];
        for (int i = 0; i < N; i++) {
            arr[i] = holes[i] + i;
        }

        // prefix minimum
        long[] prefixMin = new long[N];
        prefixMin[0] = arr[0];
        for (int i = 1; i < N; i++) {
            prefixMin[i] = Math.min(prefixMin[i-1], arr[i]);
        }

        int Q = Integer.parseInt(br.readLine().trim());
        st = new StringTokenizer(br.readLine());

        for (int q = 0; q < Q; q++) {
            long s = Long.parseLong(st.nextToken());

            int lo = 0, hi = N - 1;
            while (lo < hi) {
                int mid = (lo + hi) / 2;
                if (prefixMin[mid] <= s) hi = mid;
                else lo = mid + 1;
            }

            if (q > 0) sb.append(' ');
            sb.append(lo + 1);
        }
        sb.append('\\n');

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "26518": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 수열의 극한 - a_i = b*a_{i-1} + c*a_{i-2}
# 특성방정식: x^2 = bx + c => x^2 - bx - c = 0
# 큰 근이 극한값
import math

b, c, a1, a2 = map(int, input().split())

# x = (b + sqrt(b^2 + 4c)) / 2
discriminant = b * b + 4 * c
limit = (b + math.sqrt(discriminant)) / 2

print(f"{limit:.9f}")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <cmath>
#include <iomanip>
using namespace std;

int main() {
    long long b, c, a1, a2;
    cin >> b >> c >> a1 >> a2;

    // 특성방정식의 큰 근
    double discriminant = (double)b * b + 4.0 * c;
    double limit = (b + sqrt(discriminant)) / 2.0;

    cout << fixed << setprecision(9) << limit << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long b = sc.nextLong();
        long c = sc.nextLong();
        long a1 = sc.nextLong();
        long a2 = sc.nextLong();

        // 특성방정식의 큰 근
        double discriminant = (double)b * b + 4.0 * c;
        double limit = (b + Math.sqrt(discriminant)) / 2.0;

        System.out.printf("%.9f%n", limit);
    }
}
'''
            }
        ]
    },
    "27515": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 2의 거듭제곱 합치기 - 같은 값 두 개를 합쳐서 최대값 구하기
import sys
from collections import defaultdict

input = sys.stdin.readline

def solve():
    Q = int(input())

    # count[k] = 2^k의 개수
    count = defaultdict(int)

    def get_max():
        # 최대값 계산: count를 정규화하고 가장 높은 비트 찾기
        # 2개 이상인 것들은 합쳐서 올림
        temp = defaultdict(int, count)
        max_k = max(temp.keys()) if temp else -1

        for k in range(max(max_k + 1, 63)):
            if temp[k] >= 2:
                carry = temp[k] // 2
                temp[k] %= 2
                temp[k + 1] += carry

        # 가장 높은 k 찾기
        for k in range(70, -1, -1):
            if temp[k] > 0:
                return 1 << k
        return 0

    results = []
    for _ in range(Q):
        query = input().split()
        op = query[0]
        x = int(query[1])

        if x == 0:
            # 0은 합치기에 영향 없음
            pass
        else:
            # x = 2^k
            k = x.bit_length() - 1
            if op == '+':
                count[k] += 1
            else:  # '-'
                count[k] -= 1
                if count[k] == 0:
                    del count[k]

        results.append(get_max())

    print('\\n'.join(map(str, results)))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <map>
using namespace std;

map<int, long long> cnt;

long long getMax() {
    map<int, long long> temp = cnt;

    for (auto& p : temp) {
        int k = p.first;
        while (temp[k] >= 2) {
            long long carry = temp[k] / 2;
            temp[k] %= 2;
            temp[k + 1] += carry;
            k++;
        }
    }

    for (int k = 70; k >= 0; k--) {
        if (temp[k] > 0) {
            return 1LL << k;
        }
    }
    return 0;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int Q;
    cin >> Q;

    while (Q--) {
        string op;
        long long x;
        cin >> op >> x;

        if (x > 0) {
            int k = 0;
            while ((1LL << k) < x) k++;

            if (op == "+") {
                cnt[k]++;
            } else {
                cnt[k]--;
                if (cnt[k] == 0) cnt.erase(k);
            }
        }

        cout << getMax() << "\\n";
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static TreeMap<Integer, Long> cnt = new TreeMap<>();

    static long getMax() {
        TreeMap<Integer, Long> temp = new TreeMap<>(cnt);

        for (int k = 0; k <= 70; k++) {
            if (temp.containsKey(k) && temp.get(k) >= 2) {
                long carry = temp.get(k) / 2;
                temp.put(k, temp.get(k) % 2);
                temp.put(k + 1, temp.getOrDefault(k + 1, 0L) + carry);
            }
        }

        for (int k = 70; k >= 0; k--) {
            if (temp.getOrDefault(k, 0L) > 0) {
                return 1L << k;
            }
        }
        return 0;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int Q = Integer.parseInt(br.readLine().trim());

        while (Q-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String op = st.nextToken();
            long x = Long.parseLong(st.nextToken());

            if (x > 0) {
                int k = 0;
                while ((1L << k) < x) k++;

                if (op.equals("+")) {
                    cnt.put(k, cnt.getOrDefault(k, 0L) + 1);
                } else {
                    cnt.put(k, cnt.get(k) - 1);
                    if (cnt.get(k) == 0) cnt.remove(k);
                }
            }

            sb.append(getMax()).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "19844": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 프랑스어 단어 세기
import sys
input = sys.stdin.readline

def solve():
    s = input().strip()

    # 띄어쓰기와 하이픈으로 분리
    words = []
    current = ""
    for c in s:
        if c == ' ' or c == '-':
            if current:
                words.append(current)
                current = ""
        else:
            current += c
    if current:
        words.append(current)

    # 각 단어에서 어포스트로피로 분리 가능한지 확인
    prefixes = {"c'", "j'", "n'", "m'", "t'", "s'", "l'", "d'", "qu'"}
    vowels = set("aeiouh")

    count = 0
    for word in words:
        if not word:
            continue

        # 어포스트로피 위치 찾기
        split_count = 1
        i = 0
        while i < len(word):
            found = False
            # 가능한 접두사 확인
            for prefix in ["c'", "j'", "n'", "m'", "t'", "s'", "l'", "d'", "qu'"]:
                if word[i:].startswith(prefix):
                    # 어포스트로피 뒤가 모음인지 확인
                    pos = i + len(prefix)
                    if pos < len(word) and word[pos] in vowels:
                        split_count += 1
                        i = pos
                        found = True
                        break
            if not found:
                i += 1

        count += split_count

    print(count)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <vector>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    getline(cin, s);

    // 띄어쓰기와 하이픈으로 분리
    vector<string> words;
    string current;
    for (char c : s) {
        if (c == ' ' || c == '-') {
            if (!current.empty()) {
                words.push_back(current);
                current.clear();
            }
        } else {
            current += c;
        }
    }
    if (!current.empty()) words.push_back(current);

    set<char> vowels = {'a', 'e', 'i', 'o', 'u', 'h'};
    vector<string> prefixes = {"c'", "j'", "n'", "m'", "t'", "s'", "l'", "d'", "qu'"};

    int count = 0;
    for (const string& word : words) {
        if (word.empty()) continue;

        int splitCount = 1;
        size_t i = 0;
        while (i < word.length()) {
            bool found = false;
            for (const string& prefix : prefixes) {
                if (word.substr(i, prefix.length()) == prefix) {
                    size_t pos = i + prefix.length();
                    if (pos < word.length() && vowels.count(word[pos])) {
                        splitCount++;
                        i = pos;
                        found = true;
                        break;
                    }
                }
            }
            if (!found) i++;
        }

        count += splitCount;
    }

    cout << count << endl;
    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();

        // 띄어쓰기와 하이픈으로 분리
        List<String> words = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        for (char c : s.toCharArray()) {
            if (c == ' ' || c == '-') {
                if (current.length() > 0) {
                    words.add(current.toString());
                    current = new StringBuilder();
                }
            } else {
                current.append(c);
            }
        }
        if (current.length() > 0) words.add(current.toString());

        Set<Character> vowels = new HashSet<>(Arrays.asList('a', 'e', 'i', 'o', 'u', 'h'));
        String[] prefixes = {"c'", "j'", "n'", "m'", "t'", "s'", "l'", "d'", "qu'"};

        int count = 0;
        for (String word : words) {
            if (word.isEmpty()) continue;

            int splitCount = 1;
            int i = 0;
            while (i < word.length()) {
                boolean found = false;
                for (String prefix : prefixes) {
                    if (word.substring(i).startsWith(prefix)) {
                        int pos = i + prefix.length();
                        if (pos < word.length() && vowels.contains(word.charAt(pos))) {
                            splitCount++;
                            i = pos;
                            found = true;
                            break;
                        }
                    }
                }
                if (!found) i++;
            }

            count += splitCount;
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    }
}

# 기존 파일 읽기
with open('data/baekjoon/baek_medium.json', 'r', encoding='utf-8') as f:
    medium_data = json.load(f)

print(f"기존 솔루션 수: {len(medium_data)}")

# 새 솔루션 추가
added = 0
for pid, data in new_solutions.items():
    if pid not in medium_data:
        medium_data[pid] = data
        added += 1
    else:
        print(f"이미 존재: {pid}")

# 파일 저장
with open('data/baekjoon/baek_medium.json', 'w', encoding='utf-8') as f:
    json.dump(medium_data, f, ensure_ascii=False, indent=2)

print(f"새로 추가된 솔루션: {added}개")
print(f"총 솔루션 수: {len(medium_data)}개")
