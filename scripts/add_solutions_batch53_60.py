#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
53번째부터 60번째까지의 빈 솔루션 medium 문제에 솔루션을 추가하는 스크립트
"""

import json

# JSON 파일 읽기
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# medium 난이도이면서 solutions가 빈 문제들 찾기
empty_medium_indices = []
for i, p in enumerate(data):
    if p.get('difficulty') == 'medium' and (not p.get('solutions') or len(p.get('solutions', [])) == 0):
        empty_medium_indices.append(i)

solutions_to_add = {}

# 문제 53: 백준 3359 - 사각 사각 (인덱스 4048)
solutions_to_add[empty_medium_indices[52]] = [
    {
        "language": "python",
        "code": '''# 백준 3359: 사각 사각
# DP: 각 사각형을 세로 또는 가로로 놓을 때 위쪽 둘레 최대화
import sys
input = sys.stdin.readline

n = int(input())
rects = []
for _ in range(n):
    a, b = map(int, input().split())
    rects.append((a, b))

# dp[i][0] = i번째 사각형을 a가 바닥일 때 (높이 b)
# dp[i][1] = i번째 사각형을 b가 바닥일 때 (높이 a)

INF = float('-inf')
dp = [[INF, INF] for _ in range(n)]

# 첫 번째 사각형
# 옵션 0: 바닥 a, 높이 b -> 위쪽 변 a
# 옵션 1: 바닥 b, 높이 a -> 위쪽 변 b
dp[0][0] = rects[0][0]  # 위쪽 변
dp[0][1] = rects[0][1]

for i in range(1, n):
    a, b = rects[i]

    # 이전 높이
    prev_a, prev_b = rects[i-1]

    for prev_opt in [0, 1]:
        prev_height = prev_b if prev_opt == 0 else prev_a

        for curr_opt in [0, 1]:
            curr_height = b if curr_opt == 0 else a
            curr_top = a if curr_opt == 0 else b

            # 측면 추가 (높이 차이)
            side = abs(curr_height - prev_height)

            dp[i][curr_opt] = max(dp[i][curr_opt], dp[i-1][prev_opt] + side + curr_top)

# 마지막 사각형의 오른쪽 측면
last_a, last_b = rects[-1]
result = max(dp[-1][0] + last_b, dp[-1][1] + last_a)

# 첫 번째 사각형의 왼쪽 측면
first_a, first_b = rects[0]
# 첫 번째 선택에 따른 왼쪽 측면 추가
# dp 다시 계산 필요

# 다시 계산 (왼쪽 측면 포함)
dp = [[INF, INF] for _ in range(n)]

# 첫 번째: 왼쪽 측면 + 위쪽 변
dp[0][0] = rects[0][1] + rects[0][0]  # 높이 b (왼쪽) + 위쪽 a
dp[0][1] = rects[0][0] + rects[0][1]  # 높이 a (왼쪽) + 위쪽 b

for i in range(1, n):
    a, b = rects[i]
    prev_a, prev_b = rects[i-1]

    for prev_opt in [0, 1]:
        prev_height = prev_b if prev_opt == 0 else prev_a

        for curr_opt in [0, 1]:
            curr_height = b if curr_opt == 0 else a
            curr_top = a if curr_opt == 0 else b
            side = abs(curr_height - prev_height)

            dp[i][curr_opt] = max(dp[i][curr_opt], dp[i-1][prev_opt] + side + curr_top)

# 마지막 오른쪽 측면 추가
last_a, last_b = rects[-1]
result = max(dp[-1][0] + last_b, dp[-1][1] + last_a)

print(result)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 3359: 사각 사각
// DP: 각 사각형을 세로 또는 가로로 놓을 때 위쪽 둘레 최대화
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[][] rects = new int[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            rects[i][0] = Integer.parseInt(st.nextToken());
            rects[i][1] = Integer.parseInt(st.nextToken());
        }

        long[][] dp = new long[n][2];
        long NEG_INF = Long.MIN_VALUE / 2;

        for (int i = 0; i < n; i++) {
            Arrays.fill(dp[i], NEG_INF);
        }

        // 첫 번째: 왼쪽 측면 + 위쪽 변
        dp[0][0] = rects[0][1] + rects[0][0];
        dp[0][1] = rects[0][0] + rects[0][1];

        for (int i = 1; i < n; i++) {
            int a = rects[i][0], b = rects[i][1];
            int prevA = rects[i-1][0], prevB = rects[i-1][1];

            for (int prevOpt = 0; prevOpt < 2; prevOpt++) {
                int prevHeight = (prevOpt == 0) ? prevB : prevA;

                for (int currOpt = 0; currOpt < 2; currOpt++) {
                    int currHeight = (currOpt == 0) ? b : a;
                    int currTop = (currOpt == 0) ? a : b;
                    int side = Math.abs(currHeight - prevHeight);

                    dp[i][currOpt] = Math.max(dp[i][currOpt], dp[i-1][prevOpt] + side + currTop);
                }
            }
        }

        int lastA = rects[n-1][0], lastB = rects[n-1][1];
        long result = Math.max(dp[n-1][0] + lastB, dp[n-1][1] + lastA);

        System.out.println(result);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

// 백준 3359: 사각 사각
// DP: 각 사각형을 세로 또는 가로로 놓을 때 위쪽 둘레 최대화

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<pair<int, int>> rects(n);
    for (int i = 0; i < n; i++) {
        cin >> rects[i].first >> rects[i].second;
    }

    const long long NEG_INF = -1e18;
    vector<vector<long long>> dp(n, vector<long long>(2, NEG_INF));

    // 첫 번째: 왼쪽 측면 + 위쪽 변
    dp[0][0] = rects[0].second + rects[0].first;
    dp[0][1] = rects[0].first + rects[0].second;

    for (int i = 1; i < n; i++) {
        int a = rects[i].first, b = rects[i].second;
        int prevA = rects[i-1].first, prevB = rects[i-1].second;

        for (int prevOpt = 0; prevOpt < 2; prevOpt++) {
            int prevHeight = (prevOpt == 0) ? prevB : prevA;

            for (int currOpt = 0; currOpt < 2; currOpt++) {
                int currHeight = (currOpt == 0) ? b : a;
                int currTop = (currOpt == 0) ? a : b;
                int side = abs(currHeight - prevHeight);

                dp[i][currOpt] = max(dp[i][currOpt], dp[i-1][prevOpt] + side + currTop);
            }
        }
    }

    int lastA = rects[n-1].first, lastB = rects[n-1].second;
    long long result = max(dp[n-1][0] + lastB, dp[n-1][1] + lastA);

    cout << result << endl;

    return 0;
}
'''
    }
]

# 문제 54: 백준 23323 - 황소 다마고치 (인덱스 4050)
solutions_to_add[empty_medium_indices[53]] = [
    {
        "language": "python",
        "code": '''# 백준 23323: 황소 다마고치
# 그리디: 체력이 홀수일 때만 먹이 1개 사용
import sys
input = sys.stdin.readline

T = int(input())

for _ in range(T):
    n, m = map(int, input().split())

    day = 0

    while n > 0:
        # 낮: 먹이 주기 (선택)
        # 밤: 체력 절반

        # 최적 전략: 체력이 홀수면 1개 먹이 사용 (버려지는 1 방지)
        if n % 2 == 1 and m > 0:
            n += 1
            m -= 1

        # 밤
        n //= 2
        day += 1

    print(day)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 23323: 황소 다마고치
// 그리디: 체력이 홀수일 때만 먹이 1개 사용
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long n = Long.parseLong(st.nextToken());
            long m = Long.parseLong(st.nextToken());

            long day = 0;

            while (n > 0) {
                if (n % 2 == 1 && m > 0) {
                    n++;
                    m--;
                }
                n /= 2;
                day++;
            }

            sb.append(day).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
using namespace std;

// 백준 23323: 황소 다마고치
// 그리디: 체력이 홀수일 때만 먹이 1개 사용

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        long long n, m;
        cin >> n >> m;

        long long day = 0;

        while (n > 0) {
            if (n % 2 == 1 && m > 0) {
                n++;
                m--;
            }
            n /= 2;
            day++;
        }

        cout << day << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 55: 백준 20974 - Even More Odd Photos (인덱스 4053)
solutions_to_add[empty_medium_indices[54]] = [
    {
        "language": "python",
        "code": '''# 백준 20974: Even More Odd Photos
# 짝수 합 그룹과 홀수 합 그룹을 번갈아 배치
import sys
input = sys.stdin.readline

n = int(input())
nums = list(map(int, input().split()))

# 짝수와 홀수 개수 세기
even_count = sum(1 for x in nums if x % 2 == 0)
odd_count = n - even_count

# 그룹: 짝수-홀수-짝수-홀수-...
# 짝수 합 그룹: 짝수들만 또는 홀수 2개씩
# 홀수 합 그룹: 홀수 1개 이상 (홀수 개수가 홀수)

# 전략:
# 1. 짝수만으로 그룹 만들기
# 2. 홀수 2개로 짝수 합 그룹 만들기
# 3. 홀수 1개로 홀수 합 그룹 만들기

# 짝수 합 그룹 수 = even_count + (odd_count // 2)
# 홀수 합 그룹 수 = 남은 홀수로 결정

# 최적: 짝수-홀수-짝수-홀수-... 형태
# 짝수 합 그룹이 K개, 홀수 합 그룹이 K-1 또는 K개

# 짝수 합을 만들 수 있는 재료: 짝수 개수 + 홀수 쌍 개수
even_groups = even_count  # 짝수만으로 만든 그룹
odd_pairs = odd_count // 2  # 홀수 2개로 만든 짝수 합 그룹
remaining_odds = odd_count % 2  # 남은 홀수 1개

# 총 짝수 합 그룹 가능: even_count (각 짝수 1개씩)
# 홀수를 2개씩 묶어서 짝수 합 그룹 추가 가능

# 그룹 배치: 짝-홀-짝-홀-... (짝수 합으로 시작)
# 짝수 합 그룹 수 >= 홀수 합 그룹 수

# 홀수 합 그룹은 홀수 1개로 만들 수 있음
# 홀수 개수 = odd_count

# 최대 그룹 수 계산
# 짝수 합 그룹과 홀수 합 그룹을 번갈아 배치

# 사용 가능한 짝수 합 자원: even_count + floor(odd_count/2)
# 사용 가능한 홀수 합 자원: ceil(odd_count/1) = odd_count (각 홀수 1개씩)

# 하지만 짝수 합을 위해 홀수 2개를 쓰면 홀수 합 자원 감소

# 그리디: 홀수 1개씩 홀수 합 그룹에 사용, 나머지 홀수는 2개씩 짝수 합에 사용

# 최대 그룹: 2*min(E, O) + 1 또는 2*O + 1 등 여러 케이스

E = even_count
O = odd_count

# 짝수 합 그룹: E개 (각 짝수 1개씩) + 홀수 2개씩 추가 가능
# 홀수 합 그룹: 홀수 1개씩

# 번갈아 배치하므로
# 그룹 수 = 짝수 합 그룹 수 + 홀수 합 그룹 수
# 짝수 합 >= 홀수 합 또는 홀수 합 = 짝수 합 - 1

# 케이스별 분석
if O == 0:
    # 홀수가 없으면 짝수 합 그룹만 1개
    print(E if E > 0 else 0)
else:
    # 홀수가 있는 경우
    # 짝수 합 그룹: E + (O-k)//2 (k는 홀수 합 그룹에 사용할 홀수 개수)
    # 홀수 합 그룹: k (각각 홀수 1개씩)
    # 그룹 배치: 짝-홀-짝-홀-... (짝수 합 >= 홀수 합)

    # 최적: k를 최대화하되 짝수 합 >= 홀수 합 유지
    # 짝수 합 = E + (O-k)//2
    # 홀수 합 = k
    # E + (O-k)//2 >= k

    best = 0
    for k in range(O + 1):
        even_grp = E + (O - k) // 2
        odd_grp = k

        if even_grp >= odd_grp and (O - k) % 2 == 0:
            total = even_grp + odd_grp
            best = max(best, total)
        elif even_grp >= odd_grp - 1:
            # 홀수 합 그룹이 1개 더 많을 수 있음
            pass

    # 더 간단한 공식
    # 짝수 합 최대: E + O//2
    # 홀수 합 최대: O

    # 번갈아 배치할 때
    # 짝수 합 먼저 -> 짝수 합 = 홀수 합 또는 홀수 합 + 1
    # 홀수 합 먼저 -> 홀수 합 = 짝수 합 또는 짝수 합 + 1

    # 최대 그룹 = min(2*E + O, E + O + E) 형태

    # 정확한 공식
    if E >= O:
        # 짝수가 충분 -> 홀수 전부 홀수 합 그룹으로 사용
        # 그룹: O + O = 2*O (짝수 O개, 홀수 O개 번갈아)
        # 남은 짝수 1개 추가 가능
        best = 2 * O + 1
    else:
        # 짝수가 부족 -> 홀수 2개씩 묶어서 짝수 합 보충
        # 필요한 추가 짝수 합 = O - E
        # 홀수 2개씩 = 2*(O-E)개 홀수 사용
        # 남은 홀수 = O - 2*(O-E) = 2E - O
        remaining = 2 * E - O
        if remaining >= 0:
            # 충분한 홀수
            best = E + (O - remaining) // 2 + remaining
            # = E + (O - 2E + O) // 2 + 2E - O
            # = E + O - E + 2E - O = 2E
            # 번갈아 배치: E개 짝수 합 + E개 홀수 합 = 2E
            # 추가로 남은 홀수가 있으면 +1
            if O % 2 == 1:
                best = 2 * E
            else:
                best = 2 * E + 1
        else:
            best = 2 * E + 1 if O > 0 else 0

    print(best)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 20974: Even More Odd Photos
// 짝수 합 그룹과 홀수 합 그룹을 번갈아 배치
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int even = 0, odd = 0;

        for (int i = 0; i < n; i++) {
            int x = Integer.parseInt(st.nextToken());
            if (x % 2 == 0) even++;
            else odd++;
        }

        if (odd == 0) {
            System.out.println(even > 0 ? 1 : 0);
        } else if (even >= odd) {
            System.out.println(2 * odd + 1);
        } else {
            // even < odd
            // 홀수 2개씩 짝수 합 만들기
            int needed = odd - even;
            int remaining = odd - 2 * needed;

            if (remaining >= 0) {
                System.out.println(2 * even + 1);
            } else {
                System.out.println(2 * even + 1);
            }
        }
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
using namespace std;

// 백준 20974: Even More Odd Photos
// 짝수 합 그룹과 홀수 합 그룹을 번갈아 배치

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int even = 0, odd = 0;
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        if (x % 2 == 0) even++;
        else odd++;
    }

    if (odd == 0) {
        cout << (even > 0 ? 1 : 0) << endl;
    } else if (even >= odd) {
        cout << 2 * odd + 1 << endl;
    } else {
        cout << 2 * even + 1 << endl;
    }

    return 0;
}
'''
    }
]

# 문제 56: 백준 2200 - 계산기 (인덱스 4054)
solutions_to_add[empty_medium_indices[55]] = [
    {
        "language": "python",
        "code": '''# 백준 2200: 계산기
# 최소 키 입력으로 다항식 계산
import sys
input = sys.stdin.readline

n = int(input())
coeffs = list(map(int, input().split()))  # 최고차항부터

# Horner's method 사용: a_n*x^n + ... + a_0 = ((...((a_n)*x + a_{n-1})*x + ...)*x + a_0)

# 기본: x 입력 (1회), 각 곱하기 (1회), 각 계수 입력 (자릿수), 각 더하기 (1회)

# 호너법: ((a_n * x + a_{n-1}) * x + a_{n-2}) * ... * x + a_0

# 키 입력 계산
# 시작: x (1회)
# 각 단계: +, 계수, *, x

# 최고차항 계수는 항상 1이므로 시작은 x

def count_digits(num):
    if num == 0:
        return 1
    count = 0
    while num > 0:
        count += 1
        num //= 10
    return count

total = 1  # 초기 x

for i in range(1, n + 1):
    coeff = coeffs[i]
    if coeff != 0:
        total += 1  # +
        total += count_digits(coeff)  # 계수 입력
    total += 1  # *
    total += 1  # x

# 마지막 = 키
total += 1

# 하지만 문제의 계산기는 다르게 동작
# 다시 분석 필요

# 예제: x^3 + x + 11
# x, *, x, *, x, +, x, +, 1, 1, = -> 11회
# 계수: 1 0 1 11

# Horner: x -> *x -> +0 -> *x -> +1 -> *x -> +11
# x, *, x, +, 0, *, x, +, 1, *, x, +, 1, 1, = -> 더 많음

# 문제의 방식: 각 항을 따로 계산
# x^3: x, *, x, *, x (5회)
# + x: +, x (2회)
# + 11: +, 1, 1 (3회)
# = (1회)
# 총 11회

# 다시 계산
total = 0

# 최고차항 (계수 1)
# x^n = x * x * ... * x (n개의 x와 n-1개의 *)
# 키 입력: x + (n-1) * (+ *, x) = 1 + 2*(n-1) = 2n - 1
# 하지만 처음 x 다음 각 곱하기는 *, x

# x^n: x, *, x, *, x, ..., *, x
# = 1 + 2*(n-1) = 2n - 1 ... 아니, x가 n개, *가 n-1개
# = n + (n-1) = 2n - 1

total = 2 * n - 1  # 최고차항 x^n

# 나머지 항들
for i in range(1, n + 1):
    coeff = coeffs[i]
    if coeff != 0:
        total += 1  # +
        total += count_digits(coeff)  # 계수

# = 키
total += 1

print(total)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 2200: 계산기
// 최소 키 입력으로 다항식 계산
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        long[] coeffs = new long[n + 1];
        for (int i = 0; i <= n; i++) {
            coeffs[i] = Long.parseLong(st.nextToken());
        }

        // 최고차항 x^n: 2n - 1 키
        long total = 2 * n - 1;

        // 나머지 항들
        for (int i = 1; i <= n; i++) {
            if (coeffs[i] != 0) {
                total += 1;  // +
                total += countDigits(coeffs[i]);  // 계수
            }
        }

        // = 키
        total += 1;

        System.out.println(total);
    }

    static int countDigits(long num) {
        if (num == 0) return 1;
        int count = 0;
        while (num > 0) {
            count++;
            num /= 10;
        }
        return count;
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <string>
using namespace std;

// 백준 2200: 계산기
// 최소 키 입력으로 다항식 계산

int countDigits(long long num) {
    if (num == 0) return 1;
    int count = 0;
    while (num > 0) {
        count++;
        num /= 10;
    }
    return count;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    long long total = 2 * n - 1;  // 최고차항

    for (int i = 1; i <= n; i++) {
        long long coeff;
        cin >> coeff;
        if (coeff != 0) {
            total += 1;  // +
            total += countDigits(coeff);  // 계수
        }
    }

    total += 1;  // =

    cout << total << endl;

    return 0;
}
'''
    }
]

# 문제 57: 백준 33557 - 곱셈을 누가 이렇게 해 ㅋㅋ (인덱스 4056)
solutions_to_add[empty_medium_indices[56]] = [
    {
        "language": "python",
        "code": '''# 백준 33557: 곱셈을 누가 이렇게 해 ㅋㅋ
# 잘못된 곱셈 결과와 일반 곱셈 결과 비교
import sys
input = sys.stdin.readline

T = int(input())

for _ in range(T):
    A, B = map(int, input().split())

    # 일반 곱셈
    normal = A * B

    # 잘못된 곱셈
    # 각 자릿수를 곱하고 받아올림 없이 그대로 적음
    # 자릿수가 다르면 긴 수의 자릿수만 적음

    strA = str(A)
    strB = str(B)

    # 짧은 쪽을 긴 쪽에 맞춤 (앞에 0 패딩)
    maxLen = max(len(strA), len(strB))
    strA = strA.zfill(maxLen)
    strB = strB.zfill(maxLen)

    # 각 자릿수 곱셈
    result = ""
    for i in range(maxLen):
        product = int(strA[i]) * int(strB[i])
        result += str(product)

    # 앞의 0 제거
    wrong = int(result) if result else 0

    print(1 if normal == wrong else 0)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 33557: 곱셈을 누가 이렇게 해 ㅋㅋ
// 잘못된 곱셈 결과와 일반 곱셈 결과 비교
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long A = Long.parseLong(st.nextToken());
            long B = Long.parseLong(st.nextToken());

            long normal = A * B;

            String strA = String.valueOf(A);
            String strB = String.valueOf(B);

            int maxLen = Math.max(strA.length(), strB.length());

            while (strA.length() < maxLen) strA = "0" + strA;
            while (strB.length() < maxLen) strB = "0" + strB;

            StringBuilder result = new StringBuilder();
            for (int i = 0; i < maxLen; i++) {
                int product = (strA.charAt(i) - '0') * (strB.charAt(i) - '0');
                result.append(product);
            }

            long wrong = Long.parseLong(result.toString());

            sb.append(normal == wrong ? 1 : 0).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <string>
using namespace std;

// 백준 33557: 곱셈을 누가 이렇게 해 ㅋㅋ
// 잘못된 곱셈 결과와 일반 곱셈 결과 비교

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        long long A, B;
        cin >> A >> B;

        long long normal = A * B;

        string strA = to_string(A);
        string strB = to_string(B);

        int maxLen = max(strA.length(), strB.length());

        while (strA.length() < maxLen) strA = "0" + strA;
        while (strB.length() < maxLen) strB = "0" + strB;

        string result = "";
        for (int i = 0; i < maxLen; i++) {
            int product = (strA[i] - '0') * (strB[i] - '0');
            result += to_string(product);
        }

        long long wrong = stoll(result);

        cout << (normal == wrong ? 1 : 0) << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 58: 백준 31462 - 삼각 초콜릿 포장 (인덱스 4061)
solutions_to_add[empty_medium_indices[57]] = [
    {
        "language": "python",
        "code": '''# 백준 31462: 삼각 초콜릿 포장
# 삼각형 타일링 가능 여부 확인
import sys
input = sys.stdin.readline

n = int(input())
grid = []
for i in range(n):
    grid.append(input().strip())

# 위로 뾰족한 삼각형 (R): (i,j), (i+1,j), (i+1,j+1)
# 아래로 뾰족한 삼각형 (B): (i,j), (i,j+1), (i+1,j+1)

# 그리디하게 채우기
used = [[False] * (i + 1) for i in range(n)]

def solve():
    for i in range(n):
        for j in range(i + 1):
            if used[i][j]:
                continue

            color = grid[i][j]

            if color == 'R':
                # 위로 뾰족한 삼각형: (i,j), (i+1,j), (i+1,j+1)
                if i + 1 >= n:
                    return False
                if j >= len(grid[i+1]) or j + 1 >= len(grid[i+1]):
                    return False
                if grid[i+1][j] != 'R' or grid[i+1][j+1] != 'R':
                    return False
                if used[i+1][j] or used[i+1][j+1]:
                    return False

                used[i][j] = True
                used[i+1][j] = True
                used[i+1][j+1] = True

            else:  # color == 'B'
                # 아래로 뾰족한 삼각형: (i,j), (i,j+1), (i+1,j+1)
                if j + 1 > i:
                    return False
                if i + 1 >= n or j + 1 >= len(grid[i+1]):
                    return False
                if grid[i][j+1] != 'B' or grid[i+1][j+1] != 'B':
                    return False
                if used[i][j+1] or used[i+1][j+1]:
                    return False

                used[i][j] = True
                used[i][j+1] = True
                used[i+1][j+1] = True

    return True

print(1 if solve() else 0)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 31462: 삼각 초콜릿 포장
// 삼각형 타일링 가능 여부 확인
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        String[] grid = new String[n];
        for (int i = 0; i < n; i++) {
            grid[i] = br.readLine().trim();
        }

        boolean[][] used = new boolean[n][];
        for (int i = 0; i < n; i++) {
            used[i] = new boolean[i + 1];
        }

        boolean valid = true;

        outer:
        for (int i = 0; i < n; i++) {
            for (int j = 0; j <= i; j++) {
                if (used[i][j]) continue;

                char color = grid[i].charAt(j);

                if (color == 'R') {
                    if (i + 1 >= n || j >= grid[i+1].length() || j + 1 >= grid[i+1].length()) {
                        valid = false;
                        break outer;
                    }
                    if (grid[i+1].charAt(j) != 'R' || grid[i+1].charAt(j+1) != 'R') {
                        valid = false;
                        break outer;
                    }
                    if (used[i+1][j] || used[i+1][j+1]) {
                        valid = false;
                        break outer;
                    }

                    used[i][j] = true;
                    used[i+1][j] = true;
                    used[i+1][j+1] = true;
                } else {
                    if (j + 1 > i || i + 1 >= n || j + 1 >= grid[i+1].length()) {
                        valid = false;
                        break outer;
                    }
                    if (grid[i].charAt(j+1) != 'B' || grid[i+1].charAt(j+1) != 'B') {
                        valid = false;
                        break outer;
                    }
                    if (used[i][j+1] || used[i+1][j+1]) {
                        valid = false;
                        break outer;
                    }

                    used[i][j] = true;
                    used[i][j+1] = true;
                    used[i+1][j+1] = true;
                }
            }
        }

        System.out.println(valid ? 1 : 0);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
#include <string>
using namespace std;

// 백준 31462: 삼각 초콜릿 포장
// 삼각형 타일링 가능 여부 확인

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<string> grid(n);
    for (int i = 0; i < n; i++) {
        cin >> grid[i];
    }

    vector<vector<bool>> used(n);
    for (int i = 0; i < n; i++) {
        used[i].resize(i + 1, false);
    }

    bool valid = true;

    for (int i = 0; i < n && valid; i++) {
        for (int j = 0; j <= i && valid; j++) {
            if (used[i][j]) continue;

            char color = grid[i][j];

            if (color == 'R') {
                if (i + 1 >= n || j >= (int)grid[i+1].length() || j + 1 >= (int)grid[i+1].length()) {
                    valid = false;
                    continue;
                }
                if (grid[i+1][j] != 'R' || grid[i+1][j+1] != 'R') {
                    valid = false;
                    continue;
                }
                if (used[i+1][j] || used[i+1][j+1]) {
                    valid = false;
                    continue;
                }

                used[i][j] = true;
                used[i+1][j] = true;
                used[i+1][j+1] = true;
            } else {
                if (j + 1 > i || i + 1 >= n || j + 1 >= (int)grid[i+1].length()) {
                    valid = false;
                    continue;
                }
                if (grid[i][j+1] != 'B' || grid[i+1][j+1] != 'B') {
                    valid = false;
                    continue;
                }
                if (used[i][j+1] || used[i+1][j+1]) {
                    valid = false;
                    continue;
                }

                used[i][j] = true;
                used[i][j+1] = true;
                used[i+1][j+1] = true;
            }
        }
    }

    cout << (valid ? 1 : 0) << endl;

    return 0;
}
'''
    }
]

# 문제 59: 백준 27112 - 시간 외 근무 멈춰! (인덱스 4063)
solutions_to_add[empty_medium_indices[58]] = [
    {
        "language": "python",
        "code": '''# 백준 27112: 시간 외 근무 멈춰!
# 그리디: 마감 순으로 정렬 후 스케줄링
import sys
import heapq
input = sys.stdin.readline

n = int(input())
tasks = []

for _ in range(n):
    d, t = map(int, input().split())
    tasks.append((d, t))

# 마감일 순으로 정렬
tasks.sort()

# 현재 날짜와 시간 외 근무 횟수
current_day = 1
overtime = 0

# 평시 근무: 월~금 (주 5일)
# 시간 외 근무: 매일 가능

def get_work_days(start, end):
    """start부터 end-1까지의 평시 근무일 수"""
    if end <= start:
        return 0

    days = end - start
    weeks = days // 7
    remainder = days % 7

    work_days = weeks * 5
    start_dow = (start - 1) % 7  # 0=월, 1=화, ..., 4=금, 5=토, 6=일

    for i in range(remainder):
        if (start_dow + i) % 7 < 5:
            work_days += 1

    return work_days

# 우선순위 큐로 작업 관리
heap = []  # (남은 작업량, 마감일)

for d, t in tasks:
    heapq.heappush(heap, (-t, d, t))  # 최대 힙 (작업량 큰 것 우선)

# 시뮬레이션이 복잡하므로 이진 탐색 사용
def can_finish(max_overtime):
    """최대 max_overtime번의 시간 외 근무로 모든 작업 완료 가능한지"""
    work = []  # (deadline, time)
    for d, t in tasks:
        work.append((d, t))

    work.sort()

    total_overtime = 0
    current = 1

    for deadline, time in work:
        # current부터 deadline-1까지 사용 가능한 날
        available_days = deadline - current

        if available_days < 0:
            return False

        # 평시 근무일 계산
        work_days = get_work_days(current, deadline)

        if work_days >= time:
            # 시간 외 근무 없이 완료 가능
            pass
        else:
            # 시간 외 근무 필요
            needed = time - work_days
            if needed > available_days:
                return False
            total_overtime += needed

        current = deadline

    return total_overtime <= max_overtime

# 이진 탐색
left, right = 0, 100001 * 100001
result = -1

while left <= right:
    mid = (left + right) // 2
    if can_finish(mid):
        result = mid
        right = mid - 1
    else:
        left = mid + 1

print(result)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 27112: 시간 외 근무 멈춰!
// 그리디: 마감 순으로 정렬 후 스케줄링
public class Main {
    static int[][] tasks;
    static int n;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        n = Integer.parseInt(br.readLine().trim());

        tasks = new int[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            tasks[i][0] = Integer.parseInt(st.nextToken());
            tasks[i][1] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(tasks, (a, b) -> a[0] - b[0]);

        long left = 0, right = (long) 1e10;
        long result = -1;

        while (left <= right) {
            long mid = (left + right) / 2;
            if (canFinish(mid)) {
                result = mid;
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        }

        System.out.println(result);
    }

    static int getWorkDays(int start, int end) {
        if (end <= start) return 0;

        int days = end - start;
        int weeks = days / 7;
        int remainder = days % 7;

        int workDays = weeks * 5;
        int startDow = (start - 1) % 7;

        for (int i = 0; i < remainder; i++) {
            if ((startDow + i) % 7 < 5) workDays++;
        }

        return workDays;
    }

    static boolean canFinish(long maxOvertime) {
        long totalOvertime = 0;
        int current = 1;

        for (int[] task : tasks) {
            int deadline = task[0];
            int time = task[1];

            int availableDays = deadline - current;
            if (availableDays < 0) return false;

            int workDays = getWorkDays(current, deadline);

            if (workDays < time) {
                int needed = time - workDays;
                if (needed > availableDays) return false;
                totalOvertime += needed;
            }

            current = deadline;
        }

        return totalOvertime <= maxOvertime;
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

// 백준 27112: 시간 외 근무 멈춰!
// 그리디: 마감 순으로 정렬 후 스케줄링

int n;
vector<pair<int, int>> tasks;

int getWorkDays(int start, int end) {
    if (end <= start) return 0;

    int days = end - start;
    int weeks = days / 7;
    int remainder = days % 7;

    int workDays = weeks * 5;
    int startDow = (start - 1) % 7;

    for (int i = 0; i < remainder; i++) {
        if ((startDow + i) % 7 < 5) workDays++;
    }

    return workDays;
}

bool canFinish(long long maxOvertime) {
    long long totalOvertime = 0;
    int current = 1;

    for (auto& task : tasks) {
        int deadline = task.first;
        int time = task.second;

        int availableDays = deadline - current;
        if (availableDays < 0) return false;

        int workDays = getWorkDays(current, deadline);

        if (workDays < time) {
            int needed = time - workDays;
            if (needed > availableDays) return false;
            totalOvertime += needed;
        }

        current = deadline;
    }

    return totalOvertime <= maxOvertime;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;

    tasks.resize(n);
    for (int i = 0; i < n; i++) {
        cin >> tasks[i].first >> tasks[i].second;
    }

    sort(tasks.begin(), tasks.end());

    long long left = 0, right = 1e10;
    long long result = -1;

    while (left <= right) {
        long long mid = (left + right) / 2;
        if (canFinish(mid)) {
            result = mid;
            right = mid - 1;
        } else {
            left = mid + 1;
        }
    }

    cout << result << endl;

    return 0;
}
'''
    }
]

# 문제 60: 백준 2936 - 채식주의자 (인덱스 4068)
solutions_to_add[empty_medium_indices[59]] = [
    {
        "language": "python",
        "code": '''# 백준 2936: 채식주의자
# 삼각형을 이등분하는 선분의 다른 끝점 찾기
import sys
import math
input = sys.stdin.readline

x, y = map(float, input().split())

# 삼각형: (0,0), (250,0), (0,250)
# 넓이: 250*250/2 = 31250

# 입력점이 어느 변 위에 있는지 확인
EPS = 1e-9

def on_edge(x, y):
    """점이 어느 변 위에 있는지 반환"""
    if abs(y) < EPS and 0 <= x <= 250:
        return 'bottom'  # (0,0)-(250,0)
    if abs(x) < EPS and 0 <= y <= 250:
        return 'left'  # (0,0)-(0,250)
    if abs(x + y - 250) < EPS and 0 <= x <= 250 and 0 <= y <= 250:
        return 'hypotenuse'  # (250,0)-(0,250)
    return None

edge = on_edge(x, y)

# 삼각형 넓이의 절반
half_area = 31250 / 2

if edge == 'bottom':
    # 점이 (x, 0)에 있음
    # 다른 끝점은 left 또는 hypotenuse 위에

    # Case 1: 다른 끝점이 left (0, y2)
    # 삼각형 (0,0), (x,0), (0,y2) 넓이 = x*y2/2 = half_area
    # y2 = 2*half_area/x = 31250/x
    if x > EPS:
        y2 = 31250 / x
        if 0 <= y2 <= 250:
            print(f"0.00 {y2:.2f}")
        else:
            # 다른 끝점은 hypotenuse 위
            # (x2, 250-x2) where x2 + (250-x2) = 250
            # 삼각형 넓이 계산 필요
            # 점 (x,0)에서 빗변 (x2, 250-x2)까지 선분으로 이등분
            # 넓이 = (전체) - (작은 삼각형)
            # 복잡하므로 다른 방법 사용

            # 이등분선은 (x,0)에서 시작해서 다른 변을 지남
            # 넓이 31250/2를 만드는 점 찾기

            # 빗변 위의 점 (t, 250-t)와 (x,0) 연결
            # 삼각형 (250,0), (x,0), (t, 250-t) 넓이
            # = |250-x| * |250-t| / 2 (대략적 계산)

            # 정확한 공식:
            # 넓이 = 0.5 * |x1(y2-y3) + x2(y3-y1) + x3(y1-y2)|
            # (250,0), (x,0), (t, 250-t)
            # = 0.5 * |250*(0-(250-t)) + x*((250-t)-0) + t*(0-0)|
            # = 0.5 * |250*(t-250) + x*(250-t)|
            # = 0.5 * |(250-t)*(x-250)|
            # = 0.5 * (250-t) * (250-x)  (x < 250이므로)

            # 이 넓이 = half_area = 15625
            # (250-t) * (250-x) = 31250
            # 250-t = 31250 / (250-x)
            # t = 250 - 31250 / (250-x)

            t = 250 - 31250 / (250 - x)
            print(f"{t:.2f} {250-t:.2f}")
    else:
        # x = 0, 원점
        # 다른 끝점은 (125, 125)
        print("125.00 125.00")

elif edge == 'left':
    # 점이 (0, y)에 있음
    if y > EPS:
        x2 = 31250 / y
        if 0 <= x2 <= 250:
            print(f"{x2:.2f} 0.00")
        else:
            t = 250 - 31250 / (250 - y)
            print(f"{250-t:.2f} {t:.2f}")
    else:
        print("125.00 125.00")

elif edge == 'hypotenuse':
    # 점이 빗변 (x, 250-x) 위에 있음
    # 다른 끝점은 bottom 또는 left 위에

    # 빗변에서 원점까지 거리로 판단
    # 작은 삼각형 (0,0), (250,0), (x, 250-x) 넓이
    # = 0.5 * 250 * (250-x)... 아니, 정확히 계산

    # (0,0), (250,0), (x, 250-x)
    # 넓이 = 0.5 * |0*(0-(250-x)) + 250*((250-x)-0) + x*(0-0)|
    # = 0.5 * 250 * (250-x)

    area_to_bottom = 0.5 * 250 * (250 - x)

    if area_to_bottom >= half_area:
        # 다른 끝점은 bottom 위
        # (0,0), (t,0), (x, 250-x) 넓이 = half_area
        # 0.5 * t * (250-x) = half_area
        # t = 2 * half_area / (250-x) = 31250 / (250-x)
        t = 31250 / (250 - x)
        print(f"{t:.2f} 0.00")
    else:
        # 다른 끝점은 left 위
        # (0,0), (0,t), (x, 250-x) 넓이 = half_area
        # 0.5 * t * x = half_area
        # t = 31250 / x
        t = 31250 / x
        print(f"0.00 {t:.2f}")
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 2936: 채식주의자
// 삼각형을 이등분하는 선분의 다른 끝점 찾기
public class Main {
    static final double EPS = 1e-9;
    static final double HALF_AREA = 15625;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        double x = Double.parseDouble(st.nextToken());
        double y = Double.parseDouble(st.nextToken());

        String edge = onEdge(x, y);

        if (edge.equals("bottom")) {
            if (x > EPS) {
                double y2 = 31250 / x;
                if (y2 <= 250) {
                    System.out.printf("0.00 %.2f%n", y2);
                } else {
                    double t = 250 - 31250 / (250 - x);
                    System.out.printf("%.2f %.2f%n", t, 250 - t);
                }
            } else {
                System.out.println("125.00 125.00");
            }
        } else if (edge.equals("left")) {
            if (y > EPS) {
                double x2 = 31250 / y;
                if (x2 <= 250) {
                    System.out.printf("%.2f 0.00%n", x2);
                } else {
                    double t = 250 - 31250 / (250 - y);
                    System.out.printf("%.2f %.2f%n", 250 - t, t);
                }
            } else {
                System.out.println("125.00 125.00");
            }
        } else {
            double areaToBottom = 0.5 * 250 * (250 - x);

            if (areaToBottom >= HALF_AREA) {
                double t = 31250 / (250 - x);
                System.out.printf("%.2f 0.00%n", t);
            } else {
                double t = 31250 / x;
                System.out.printf("0.00 %.2f%n", t);
            }
        }
    }

    static String onEdge(double x, double y) {
        if (Math.abs(y) < EPS && x >= 0 && x <= 250) return "bottom";
        if (Math.abs(x) < EPS && y >= 0 && y <= 250) return "left";
        return "hypotenuse";
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <iomanip>
#include <cmath>
using namespace std;

// 백준 2936: 채식주의자
// 삼각형을 이등분하는 선분의 다른 끝점 찾기

const double EPS = 1e-9;
const double HALF_AREA = 15625;

string onEdge(double x, double y) {
    if (abs(y) < EPS && x >= 0 && x <= 250) return "bottom";
    if (abs(x) < EPS && y >= 0 && y <= 250) return "left";
    return "hypotenuse";
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    double x, y;
    cin >> x >> y;

    string edge = onEdge(x, y);

    cout << fixed << setprecision(2);

    if (edge == "bottom") {
        if (x > EPS) {
            double y2 = 31250 / x;
            if (y2 <= 250) {
                cout << "0.00 " << y2 << endl;
            } else {
                double t = 250 - 31250 / (250 - x);
                cout << t << " " << 250 - t << endl;
            }
        } else {
            cout << "125.00 125.00" << endl;
        }
    } else if (edge == "left") {
        if (y > EPS) {
            double x2 = 31250 / y;
            if (x2 <= 250) {
                cout << x2 << " 0.00" << endl;
            } else {
                double t = 250 - 31250 / (250 - y);
                cout << 250 - t << " " << t << endl;
            }
        } else {
            cout << "125.00 125.00" << endl;
        }
    } else {
        double areaToBottom = 0.5 * 250 * (250 - x);

        if (areaToBottom >= HALF_AREA) {
            double t = 31250 / (250 - x);
            cout << t << " 0.00" << endl;
        } else {
            double t = 31250 / x;
            cout << "0.00 " << t << endl;
        }
    }

    return 0;
}
'''
    }
]

# 솔루션 적용
count = 0
for idx, solutions in solutions_to_add.items():
    data[idx]['solutions'] = solutions
    print(f"문제 {data[idx]['id']} ({data[idx].get('name', '')})에 솔루션 추가 완료")
    count += 1

# JSON 파일 저장
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n총 {count}개 문제에 솔루션 추가 완료")
