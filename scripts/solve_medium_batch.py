#!/usr/bin/env python3
"""
Medium problems batch solver for Baekjoon problems.
Generates solutions for 10 medium problems with empty solutions.
"""

import json
import fcntl
import os

FILE_PATH = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

# 문제별 솔루션 정의
SOLUTIONS = {
    # 문제 1: baekjoon_30969 - 진주로 가자! (Hard)
    # 진주로 가는 교통편의 요금과 그보다 비싼 교통편의 개수를 구하는 문제
    "baekjoon_30969": [
        {
            "language": "python",
            "code": '''# 백준 30969 - 진주로 가자! (Hard)
# 진주로 가는 요금과 그보다 비싼 교통편의 개수를 구하는 문제

import sys
input = sys.stdin.readline

n = int(input())
jinju_price = 0
prices = []

for _ in range(n):
    line = input().split()
    dest = line[0]
    price = int(line[1])

    if dest == "jinju":
        jinju_price = price
    prices.append(price)

# 진주보다 비싼 교통편 개수 계산
count = sum(1 for p in prices if p > jinju_price)

print(jinju_price)
print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 30969 - 진주로 가자! (Hard)
// 진주로 가는 요금과 그보다 비싼 교통편의 개수를 구하는 문제
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());

        int jinjuPrice = 0;
        int[] prices = new int[n];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String dest = st.nextToken();
            int price = Integer.parseInt(st.nextToken());

            if (dest.equals("jinju")) {
                jinjuPrice = price;
            }
            prices[i] = price;
        }

        // 진주보다 비싼 교통편 개수 계산
        int count = 0;
        for (int p : prices) {
            if (p > jinjuPrice) count++;
        }

        System.out.println(jinjuPrice);
        System.out.println(count);
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

// 백준 30969 - 진주로 가자! (Hard)
// 진주로 가는 요금과 그보다 비싼 교통편의 개수를 구하는 문제

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    int jinjuPrice = 0;
    vector<int> prices(n);

    for (int i = 0; i < n; i++) {
        string dest;
        int price;
        cin >> dest >> price;

        if (dest == "jinju") {
            jinjuPrice = price;
        }
        prices[i] = price;
    }

    // 진주보다 비싼 교통편 개수 계산
    int count = 0;
    for (int p : prices) {
        if (p > jinjuPrice) count++;
    }

    cout << jinjuPrice << "\\n" << count << "\\n";
    return 0;
}
'''
        }
    ],

    # 문제 2: baekjoon_24498 - blobnom
    # 탑의 최대 높이를 구하는 문제 (중간 탑에 양쪽에서 블롭을 모을 수 있음)
    "baekjoon_24498": [
        {
            "language": "python",
            "code": '''# 백준 24498 - blobnom
# 중간 탑을 선택하여 양쪽 탑에서 블롭을 모아 최대 높이를 만드는 문제
# 핵심: 중간 탑 i를 선택하면 min(A[i-1], A[i+1])번 연산 가능
# 따라서 최대 높이 = max(A[i] + min(A[i-1], A[i+1])) for i in [1, n-2]

import sys
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))

if n == 1:
    # 탑이 1개면 그 높이가 최대
    print(a[0])
elif n == 2:
    # 탑이 2개면 둘 중 큰 값이 최대 (중간 탑이 없으므로 연산 불가)
    print(max(a))
else:
    # 각 중간 탑에서 가능한 최대 높이 계산
    max_height = max(a)  # 연산을 하지 않는 경우도 고려
    for i in range(1, n - 1):
        # i번 탑을 선택하면 min(a[i-1], a[i+1])번 연산 가능
        height = a[i] + min(a[i-1], a[i+1])
        max_height = max(max_height, height)
    print(max_height)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 24498 - blobnom
// 중간 탑을 선택하여 양쪽 탑에서 블롭을 모아 최대 높이를 만드는 문제
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] a = new int[n];
        for (int i = 0; i < n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
        }

        if (n == 1) {
            // 탑이 1개면 그 높이가 최대
            System.out.println(a[0]);
        } else if (n == 2) {
            // 탑이 2개면 둘 중 큰 값이 최대
            System.out.println(Math.max(a[0], a[1]));
        } else {
            // 각 중간 탑에서 가능한 최대 높이 계산
            int maxHeight = 0;
            for (int i = 0; i < n; i++) {
                maxHeight = Math.max(maxHeight, a[i]);
            }

            for (int i = 1; i < n - 1; i++) {
                // i번 탑을 선택하면 min(a[i-1], a[i+1])번 연산 가능
                int height = a[i] + Math.min(a[i-1], a[i+1]);
                maxHeight = Math.max(maxHeight, height);
            }
            System.out.println(maxHeight);
        }
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

// 백준 24498 - blobnom
// 중간 탑을 선택하여 양쪽 탑에서 블롭을 모아 최대 높이를 만드는 문제

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    if (n == 1) {
        // 탑이 1개면 그 높이가 최대
        cout << a[0] << "\\n";
    } else if (n == 2) {
        // 탑이 2개면 둘 중 큰 값이 최대
        cout << max(a[0], a[1]) << "\\n";
    } else {
        // 각 중간 탑에서 가능한 최대 높이 계산
        int maxHeight = *max_element(a.begin(), a.end());

        for (int i = 1; i < n - 1; i++) {
            // i번 탑을 선택하면 min(a[i-1], a[i+1])번 연산 가능
            int height = a[i] + min(a[i-1], a[i+1]);
            maxHeight = max(maxHeight, height);
        }
        cout << maxHeight << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # 문제 3: baekjoon_5376 - 소수를 분수로
    # 순환소수를 분수로 변환하는 문제
    "baekjoon_5376": [
        {
            "language": "python",
            "code": '''# 백준 5376 - 소수를 분수로
# 순환소수를 분수로 변환하는 문제
# 예: 0.166... = 0.1(6) = (16-1)/90 = 15/90 = 1/6

import sys
from math import gcd
input = sys.stdin.readline

def solve(s):
    # "0." 제거
    s = s[2:]

    # 괄호가 있는지 확인
    if '(' in s:
        # 비순환 부분과 순환 부분 분리
        idx = s.index('(')
        non_repeat = s[:idx]  # 비순환 부분
        repeat = s[idx+1:-1]  # 순환 부분 (괄호 제거)

        # 비순환 부분 길이와 순환 부분 길이
        non_len = len(non_repeat)
        rep_len = len(repeat)

        # 분모: 9를 rep_len개, 0을 non_len개
        denom = int('9' * rep_len + '0' * non_len)

        # 분자: (비순환+순환) - 비순환
        if non_repeat == '':
            numer = int(repeat)
        else:
            numer = int(non_repeat + repeat) - int(non_repeat)
    else:
        # 유한소수
        non_repeat = s
        numer = int(non_repeat) if non_repeat else 0
        denom = 10 ** len(non_repeat)

    # 기약분수로 변환
    g = gcd(numer, denom)
    numer //= g
    denom //= g

    return f"{numer}/{denom}"

t = int(input())
for _ in range(t):
    s = input().strip()
    print(solve(s))
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 5376 - 소수를 분수로
// 순환소수를 분수로 변환하는 문제
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine());
        StringBuilder sb = new StringBuilder();

        while (t-- > 0) {
            String s = br.readLine().substring(2); // "0." 제거

            long numer, denom;

            if (s.contains("(")) {
                // 순환소수
                int idx = s.indexOf('(');
                String nonRepeat = s.substring(0, idx);
                String repeat = s.substring(idx + 1, s.length() - 1);

                int nonLen = nonRepeat.length();
                int repLen = repeat.length();

                // 분모: 9를 repLen개, 0을 nonLen개
                StringBuilder denomStr = new StringBuilder();
                for (int i = 0; i < repLen; i++) denomStr.append('9');
                for (int i = 0; i < nonLen; i++) denomStr.append('0');
                denom = Long.parseLong(denomStr.toString());

                // 분자: (비순환+순환) - 비순환
                if (nonRepeat.isEmpty()) {
                    numer = Long.parseLong(repeat);
                } else {
                    numer = Long.parseLong(nonRepeat + repeat) - Long.parseLong(nonRepeat);
                }
            } else {
                // 유한소수
                numer = Long.parseLong(s);
                denom = (long) Math.pow(10, s.length());
            }

            // 기약분수로 변환
            long g = gcd(numer, denom);
            numer /= g;
            denom /= g;

            sb.append(numer).append("/").append(denom).append("\\n");
        }
        System.out.print(sb);
    }

    static long gcd(long a, long b) {
        return b == 0 ? a : gcd(b, a % b);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
#include <cmath>
using namespace std;

// 백준 5376 - 소수를 분수로
// 순환소수를 분수로 변환하는 문제

long long gcd(long long a, long long b) {
    return b == 0 ? a : gcd(b, a % b);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;

    while (t--) {
        string s;
        cin >> s;
        s = s.substr(2); // "0." 제거

        long long numer, denom;

        size_t idx = s.find('(');
        if (idx != string::npos) {
            // 순환소수
            string nonRepeat = s.substr(0, idx);
            string repeat = s.substr(idx + 1, s.length() - idx - 2);

            int nonLen = nonRepeat.length();
            int repLen = repeat.length();

            // 분모: 9를 repLen개, 0을 nonLen개
            string denomStr = "";
            for (int i = 0; i < repLen; i++) denomStr += '9';
            for (int i = 0; i < nonLen; i++) denomStr += '0';
            denom = stoll(denomStr);

            // 분자: (비순환+순환) - 비순환
            if (nonRepeat.empty()) {
                numer = stoll(repeat);
            } else {
                numer = stoll(nonRepeat + repeat) - stoll(nonRepeat);
            }
        } else {
            // 유한소수
            numer = stoll(s);
            denom = (long long)pow(10, s.length());
        }

        // 기약분수로 변환
        long long g = gcd(numer, denom);
        numer /= g;
        denom /= g;

        cout << numer << "/" << denom << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # 문제 4: baekjoon_15739 - 매직스퀘어
    # n*n 행렬이 마방진인지 확인하는 문제
    "baekjoon_15739": [
        {
            "language": "python",
            "code": '''# 백준 15739 - 매직스퀘어
# n*n 행렬이 마방진인지 확인하는 문제
# 조건 1: 1부터 n*n까지의 수가 중복 없이 모두 존재
# 조건 2: 모든 행, 열, 대각선의 합이 n*(n^2+1)/2

import sys
input = sys.stdin.readline

n = int(input())
matrix = []
for _ in range(n):
    row = list(map(int, input().split()))
    matrix.append(row)

# 목표 합 계산
target = n * (n * n + 1) // 2

# 1부터 n*n까지 모두 존재하는지 확인
all_nums = set()
for row in matrix:
    for num in row:
        all_nums.add(num)

if all_nums != set(range(1, n * n + 1)):
    print("FALSE")
else:
    is_magic = True

    # 각 행의 합 확인
    for row in matrix:
        if sum(row) != target:
            is_magic = False
            break

    # 각 열의 합 확인
    if is_magic:
        for j in range(n):
            col_sum = sum(matrix[i][j] for i in range(n))
            if col_sum != target:
                is_magic = False
                break

    # 주대각선 합 확인
    if is_magic:
        diag1 = sum(matrix[i][i] for i in range(n))
        if diag1 != target:
            is_magic = False

    # 부대각선 합 확인
    if is_magic:
        diag2 = sum(matrix[i][n - 1 - i] for i in range(n))
        if diag2 != target:
            is_magic = False

    print("TRUE" if is_magic else "FALSE")
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 15739 - 매직스퀘어
// n*n 행렬이 마방진인지 확인하는 문제
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());

        int[][] matrix = new int[n][n];
        Set<Integer> nums = new HashSet<>();

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                matrix[i][j] = Integer.parseInt(st.nextToken());
                nums.add(matrix[i][j]);
            }
        }

        // 목표 합 계산
        int target = n * (n * n + 1) / 2;

        // 1부터 n*n까지 모두 존재하는지 확인
        boolean valid = nums.size() == n * n;
        if (valid) {
            for (int i = 1; i <= n * n; i++) {
                if (!nums.contains(i)) {
                    valid = false;
                    break;
                }
            }
        }

        if (!valid) {
            System.out.println("FALSE");
            return;
        }

        // 각 행의 합 확인
        for (int i = 0; i < n && valid; i++) {
            int sum = 0;
            for (int j = 0; j < n; j++) sum += matrix[i][j];
            if (sum != target) valid = false;
        }

        // 각 열의 합 확인
        for (int j = 0; j < n && valid; j++) {
            int sum = 0;
            for (int i = 0; i < n; i++) sum += matrix[i][j];
            if (sum != target) valid = false;
        }

        // 대각선 합 확인
        if (valid) {
            int diag1 = 0, diag2 = 0;
            for (int i = 0; i < n; i++) {
                diag1 += matrix[i][i];
                diag2 += matrix[i][n - 1 - i];
            }
            if (diag1 != target || diag2 != target) valid = false;
        }

        System.out.println(valid ? "TRUE" : "FALSE");
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
#include <set>
using namespace std;

// 백준 15739 - 매직스퀘어
// n*n 행렬이 마방진인지 확인하는 문제

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<vector<int>> matrix(n, vector<int>(n));
    set<int> nums;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cin >> matrix[i][j];
            nums.insert(matrix[i][j]);
        }
    }

    // 목표 합 계산
    int target = n * (n * n + 1) / 2;

    // 1부터 n*n까지 모두 존재하는지 확인
    bool valid = (nums.size() == n * n);
    if (valid) {
        for (int i = 1; i <= n * n; i++) {
            if (nums.find(i) == nums.end()) {
                valid = false;
                break;
            }
        }
    }

    if (!valid) {
        cout << "FALSE\\n";
        return 0;
    }

    // 각 행의 합 확인
    for (int i = 0; i < n && valid; i++) {
        int sum = 0;
        for (int j = 0; j < n; j++) sum += matrix[i][j];
        if (sum != target) valid = false;
    }

    // 각 열의 합 확인
    for (int j = 0; j < n && valid; j++) {
        int sum = 0;
        for (int i = 0; i < n; i++) sum += matrix[i][j];
        if (sum != target) valid = false;
    }

    // 대각선 합 확인
    if (valid) {
        int diag1 = 0, diag2 = 0;
        for (int i = 0; i < n; i++) {
            diag1 += matrix[i][i];
            diag2 += matrix[i][n - 1 - i];
        }
        if (diag1 != target || diag2 != target) valid = false;
    }

    cout << (valid ? "TRUE" : "FALSE") << "\\n";
    return 0;
}
'''
        }
    ],

    # 문제 5: baekjoon_17499 - 수열과 시프트 쿼리
    # 수열에 대해 더하기와 시프트 연산을 수행하는 문제
    "baekjoon_17499": [
        {
            "language": "python",
            "code": '''# 백준 17499 - 수열과 시프트 쿼리
# 수열에 대해 더하기와 시프트 연산을 수행하는 문제
# 핵심: 시프트는 실제로 수행하지 않고 offset만 관리

import sys
input = sys.stdin.readline

n, q = map(int, input().split())
a = list(map(int, input().split()))

offset = 0  # 현재 시프트 오프셋 (양수: 오른쪽, 음수: 왼쪽)

for _ in range(q):
    query = list(map(int, input().split()))

    if query[0] == 1:
        # a[i]에 x를 더함
        i, x = query[1], query[2]
        # 현재 오프셋을 고려한 실제 인덱스 계산
        real_idx = (i - 1 - offset) % n
        a[real_idx] += x
    elif query[0] == 2:
        # 오른쪽으로 s칸 시프트
        s = query[1]
        offset = (offset + s) % n
    else:
        # 왼쪽으로 s칸 시프트
        s = query[1]
        offset = (offset - s) % n

# 최종 결과 출력 (오프셋 적용)
result = []
for i in range(n):
    real_idx = (i - offset) % n
    result.append(a[real_idx])

print(*result)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 17499 - 수열과 시프트 쿼리
// 수열에 대해 더하기와 시프트 연산을 수행하는 문제
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int q = Integer.parseInt(st.nextToken());

        long[] a = new long[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            a[i] = Long.parseLong(st.nextToken());
        }

        int offset = 0; // 현재 시프트 오프셋

        for (int i = 0; i < q; i++) {
            st = new StringTokenizer(br.readLine());
            int type = Integer.parseInt(st.nextToken());

            if (type == 1) {
                int idx = Integer.parseInt(st.nextToken());
                long x = Long.parseLong(st.nextToken());
                // 현재 오프셋을 고려한 실제 인덱스 계산
                int realIdx = ((idx - 1 - offset) % n + n) % n;
                a[realIdx] += x;
            } else if (type == 2) {
                int s = Integer.parseInt(st.nextToken());
                offset = (offset + s) % n;
            } else {
                int s = Integer.parseInt(st.nextToken());
                offset = ((offset - s) % n + n) % n;
            }
        }

        // 최종 결과 출력 (오프셋 적용)
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            int realIdx = ((i - offset) % n + n) % n;
            sb.append(a[realIdx]);
            if (i < n - 1) sb.append(" ");
        }
        System.out.println(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
using namespace std;

// 백준 17499 - 수열과 시프트 쿼리
// 수열에 대해 더하기와 시프트 연산을 수행하는 문제

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;

    vector<long long> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    int offset = 0; // 현재 시프트 오프셋

    for (int i = 0; i < q; i++) {
        int type;
        cin >> type;

        if (type == 1) {
            int idx;
            long long x;
            cin >> idx >> x;
            // 현재 오프셋을 고려한 실제 인덱스 계산
            int realIdx = ((idx - 1 - offset) % n + n) % n;
            a[realIdx] += x;
        } else if (type == 2) {
            int s;
            cin >> s;
            offset = (offset + s) % n;
        } else {
            int s;
            cin >> s;
            offset = ((offset - s) % n + n) % n;
        }
    }

    // 최종 결과 출력 (오프셋 적용)
    for (int i = 0; i < n; i++) {
        int realIdx = ((i - offset) % n + n) % n;
        cout << a[realIdx];
        if (i < n - 1) cout << " ";
    }
    cout << "\\n";

    return 0;
}
'''
        }
    ],

    # 문제 6: baekjoon_11277 - 2-SAT - 1
    # 2-SAT 문제가 만족 가능한지 판별하는 문제
    "baekjoon_11277": [
        {
            "language": "python",
            "code": '''# 백준 11277 - 2-SAT - 1
# 2-SAT 문제가 만족 가능한지 판별하는 문제
# SCC(강한 연결 요소)를 이용하여 해결

import sys
from collections import defaultdict
sys.setrecursionlimit(100000)
input = sys.stdin.readline

def solve():
    n, m = map(int, input().split())

    # 그래프 구성: 변수 i는 양수, ~i는 음수로 표현
    # 노드 번호: i > 0이면 i, i < 0이면 n - i
    def node(x):
        if x > 0:
            return x
        else:
            return n - x

    def neg(x):
        if x <= n:
            return x + n
        else:
            return x - n

    graph = defaultdict(list)
    reverse_graph = defaultdict(list)

    for _ in range(m):
        a, b = map(int, input().split())
        # (a ∨ b) ≡ (¬a → b) ∧ (¬b → a)
        u = node(-a)
        v = node(b)
        graph[u].append(v)
        reverse_graph[v].append(u)

        u = node(-b)
        v = node(a)
        graph[u].append(v)
        reverse_graph[v].append(u)

    # 코사라주 알고리즘으로 SCC 찾기
    visited = [False] * (2 * n + 1)
    order = []

    def dfs1(v):
        visited[v] = True
        for u in graph[v]:
            if not visited[u]:
                dfs1(u)
        order.append(v)

    for i in range(1, 2 * n + 1):
        if not visited[i]:
            dfs1(i)

    scc_id = [0] * (2 * n + 1)
    scc_count = 0

    def dfs2(v, scc):
        scc_id[v] = scc
        for u in reverse_graph[v]:
            if scc_id[u] == 0:
                dfs2(u, scc)

    for v in reversed(order):
        if scc_id[v] == 0:
            scc_count += 1
            dfs2(v, scc_count)

    # x와 ~x가 같은 SCC에 있으면 불가능
    for i in range(1, n + 1):
        if scc_id[i] == scc_id[i + n]:
            print(0)
            return

    print(1)

solve()
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 11277 - 2-SAT - 1
// 2-SAT 문제가 만족 가능한지 판별하는 문제
public class Main {
    static ArrayList<Integer>[] graph, reverseGraph;
    static boolean[] visited;
    static int[] sccId;
    static Stack<Integer> order;
    static int n;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        graph = new ArrayList[2 * n + 1];
        reverseGraph = new ArrayList[2 * n + 1];
        for (int i = 0; i <= 2 * n; i++) {
            graph[i] = new ArrayList<>();
            reverseGraph[i] = new ArrayList<>();
        }

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());

            // (a ∨ b) ≡ (¬a → b) ∧ (¬b → a)
            int u = node(-a);
            int v = node(b);
            graph[u].add(v);
            reverseGraph[v].add(u);

            u = node(-b);
            v = node(a);
            graph[u].add(v);
            reverseGraph[v].add(u);
        }

        // 코사라주 알고리즘
        visited = new boolean[2 * n + 1];
        order = new Stack<>();

        for (int i = 1; i <= 2 * n; i++) {
            if (!visited[i]) dfs1(i);
        }

        sccId = new int[2 * n + 1];
        int sccCount = 0;

        while (!order.isEmpty()) {
            int v = order.pop();
            if (sccId[v] == 0) {
                sccCount++;
                dfs2(v, sccCount);
            }
        }

        // x와 ~x가 같은 SCC에 있으면 불가능
        for (int i = 1; i <= n; i++) {
            if (sccId[i] == sccId[i + n]) {
                System.out.println(0);
                return;
            }
        }
        System.out.println(1);
    }

    static int node(int x) {
        return x > 0 ? x : n - x;
    }

    static void dfs1(int v) {
        visited[v] = true;
        for (int u : graph[v]) {
            if (!visited[u]) dfs1(u);
        }
        order.push(v);
    }

    static void dfs2(int v, int scc) {
        sccId[v] = scc;
        for (int u : reverseGraph[v]) {
            if (sccId[u] == 0) dfs2(u, scc);
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
#include <stack>
using namespace std;

// 백준 11277 - 2-SAT - 1
// 2-SAT 문제가 만족 가능한지 판별하는 문제

int n, m;
vector<int> graph[20001], reverseGraph[20001];
bool visited[20001];
int sccId[20001];
stack<int> order;

int node(int x) {
    return x > 0 ? x : n - x;
}

void dfs1(int v) {
    visited[v] = true;
    for (int u : graph[v]) {
        if (!visited[u]) dfs1(u);
    }
    order.push(v);
}

void dfs2(int v, int scc) {
    sccId[v] = scc;
    for (int u : reverseGraph[v]) {
        if (sccId[u] == 0) dfs2(u, scc);
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m;

    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;

        // (a ∨ b) ≡ (¬a → b) ∧ (¬b → a)
        int u = node(-a);
        int v = node(b);
        graph[u].push_back(v);
        reverseGraph[v].push_back(u);

        u = node(-b);
        v = node(a);
        graph[u].push_back(v);
        reverseGraph[v].push_back(u);
    }

    // 코사라주 알고리즘
    for (int i = 1; i <= 2 * n; i++) {
        if (!visited[i]) dfs1(i);
    }

    int sccCount = 0;
    while (!order.empty()) {
        int v = order.top();
        order.pop();
        if (sccId[v] == 0) {
            sccCount++;
            dfs2(v, sccCount);
        }
    }

    // x와 ~x가 같은 SCC에 있으면 불가능
    for (int i = 1; i <= n; i++) {
        if (sccId[i] == sccId[i + n]) {
            cout << 0 << "\\n";
            return 0;
        }
    }
    cout << 1 << "\\n";

    return 0;
}
'''
        }
    ],

    # 문제 7: baekjoon_2090 - 조화평균
    # N개 수의 조화평균을 분수로 출력하는 문제
    "baekjoon_2090": [
        {
            "language": "python",
            "code": '''# 백준 2090 - 조화평균
# N개 수의 조화평균을 구하는 문제
# 조화평균 = 1 / (1/A[1] + 1/A[2] + ... + 1/A[N])
# 가장 짧은 표현, 사전순으로 앞서는 것 출력

from math import gcd
from functools import reduce

def lcm(a, b):
    return a * b // gcd(a, b)

n = int(input())
a = list(map(int, input().split()))

# 분모들의 LCM 계산 (모든 수를 통분하기 위해)
common = reduce(lcm, a)

# 1/a[i]들의 합 계산: sum(common/a[i]) / common
numer_sum = sum(common // x for x in a)

# 조화평균 = 1 / (numer_sum / common) = common / numer_sum
# 분자: common, 분모: numer_sum
numer = common
denom = numer_sum

# 기약분수로 변환
g = gcd(numer, denom)
numer //= g
denom //= g

# 결과가 정수인 경우도 고려
if denom == 1:
    # 정수 출력과 분수 출력 중 짧은 것 선택
    int_str = str(numer)
    frac_str = f"{numer}/1"
    # 길이가 같으면 사전순으로 앞서는 것
    if len(int_str) < len(frac_str):
        print(int_str)
    elif len(int_str) > len(frac_str):
        print(frac_str)
    else:
        print(min(int_str, frac_str))
else:
    print(f"{numer}/{denom}")
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 2090 - 조화평균
// N개 수의 조화평균을 구하는 문제
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());
        StringTokenizer st = new StringTokenizer(br.readLine());

        long[] a = new long[n];
        for (int i = 0; i < n; i++) {
            a[i] = Long.parseLong(st.nextToken());
        }

        // 분모들의 LCM 계산
        long common = a[0];
        for (int i = 1; i < n; i++) {
            common = lcm(common, a[i]);
        }

        // 1/a[i]들의 합 계산
        long numerSum = 0;
        for (int i = 0; i < n; i++) {
            numerSum += common / a[i];
        }

        // 조화평균 = common / numerSum
        long numer = common;
        long denom = numerSum;

        // 기약분수로 변환
        long g = gcd(numer, denom);
        numer /= g;
        denom /= g;

        // 결과 출력
        if (denom == 1) {
            String intStr = String.valueOf(numer);
            String fracStr = numer + "/1";
            if (intStr.length() < fracStr.length()) {
                System.out.println(intStr);
            } else if (intStr.length() > fracStr.length()) {
                System.out.println(fracStr);
            } else {
                System.out.println(intStr.compareTo(fracStr) < 0 ? intStr : fracStr);
            }
        } else {
            System.out.println(numer + "/" + denom);
        }
    }

    static long gcd(long a, long b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    static long lcm(long a, long b) {
        return a / gcd(a, b) * b;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
#include <string>
#include <numeric>
using namespace std;

// 백준 2090 - 조화평균
// N개 수의 조화평균을 구하는 문제

long long gcd(long long a, long long b) {
    return b == 0 ? a : gcd(b, a % b);
}

long long lcm(long long a, long long b) {
    return a / gcd(a, b) * b;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<long long> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    // 분모들의 LCM 계산
    long long common = a[0];
    for (int i = 1; i < n; i++) {
        common = lcm(common, a[i]);
    }

    // 1/a[i]들의 합 계산
    long long numerSum = 0;
    for (int i = 0; i < n; i++) {
        numerSum += common / a[i];
    }

    // 조화평균 = common / numerSum
    long long numer = common;
    long long denom = numerSum;

    // 기약분수로 변환
    long long g = gcd(numer, denom);
    numer /= g;
    denom /= g;

    // 결과 출력
    if (denom == 1) {
        string intStr = to_string(numer);
        string fracStr = to_string(numer) + "/1";
        if (intStr.length() < fracStr.length()) {
            cout << intStr << "\\n";
        } else if (intStr.length() > fracStr.length()) {
            cout << fracStr << "\\n";
        } else {
            cout << (intStr < fracStr ? intStr : fracStr) << "\\n";
        }
    } else {
        cout << numer << "/" << denom << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # 문제 8: baekjoon_25375 - 아주 간단한 문제
    # gcd(x, y) = a이고 x + y = b인 자연수 쌍 존재 여부
    "baekjoon_25375": [
        {
            "language": "python",
            "code": '''# 백준 25375 - 아주 간단한 문제
# gcd(x, y) = a이고 x + y = b인 자연수 쌍 (x, y) 존재 여부
# 조건: b가 a의 배수이고, b/a >= 2이며, b/a가 홀수가 아닐 때 (즉, b/a가 2 이상의 짝수)
# 또는 b/a가 3 이상의 홀수일 때도 가능

import sys
input = sys.stdin.readline

q = int(input())
for _ in range(q):
    a, b = map(int, input().split())

    # b가 a의 배수가 아니면 불가능
    if b % a != 0:
        print(0)
        continue

    k = b // a  # x/a + y/a = k (여기서 gcd(x/a, y/a) = 1이어야 함)

    # k >= 2이고 k가 2가 아닌 짝수면 불가능 (gcd가 2 이상이 됨)
    # k = 2이면 x = y = a인데 gcd(a, a) = a이므로 가능
    # k >= 3이면 서로소인 두 수로 분해 가능

    if k < 2:
        print(0)
    else:
        print(1)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 25375 - 아주 간단한 문제
// gcd(x, y) = a이고 x + y = b인 자연수 쌍 존재 여부
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int q = Integer.parseInt(br.readLine());
        StringBuilder sb = new StringBuilder();

        while (q-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long a = Long.parseLong(st.nextToken());
            long b = Long.parseLong(st.nextToken());

            // b가 a의 배수가 아니면 불가능
            if (b % a != 0) {
                sb.append(0).append("\\n");
                continue;
            }

            long k = b / a;

            // k >= 2이면 가능
            if (k < 2) {
                sb.append(0).append("\\n");
            } else {
                sb.append(1).append("\\n");
            }
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

// 백준 25375 - 아주 간단한 문제
// gcd(x, y) = a이고 x + y = b인 자연수 쌍 존재 여부

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int q;
    cin >> q;

    while (q--) {
        long long a, b;
        cin >> a >> b;

        // b가 a의 배수가 아니면 불가능
        if (b % a != 0) {
            cout << 0 << "\\n";
            continue;
        }

        long long k = b / a;

        // k >= 2이면 가능
        if (k < 2) {
            cout << 0 << "\\n";
        } else {
            cout << 1 << "\\n";
        }
    }

    return 0;
}
'''
        }
    ],

    # 문제 9: baekjoon_29197 - 아침 태권도
    # 원점에서 볼 수 있는 학생 수를 구하는 문제
    "baekjoon_29197": [
        {
            "language": "python",
            "code": '''# 백준 29197 - 아침 태권도
# 원점에서 다른 학생에게 가려지지 않는 학생 수를 구하는 문제
# 같은 기울기(방향)에 있는 학생들 중 가장 가까운 학생만 보임

import sys
from math import gcd
input = sys.stdin.readline

n = int(input())
positions = []
for _ in range(n):
    x, y = map(int, input().split())
    positions.append((x, y))

# 각 방향별로 가장 가까운 거리 저장
directions = {}

for x, y in positions:
    # 방향 벡터를 기약 형태로 변환
    g = gcd(abs(x), abs(y))
    dx, dy = x // g, y // g

    # 거리(맨해튼 거리 또는 원점으로부터의 거리)
    dist = abs(x) + abs(y)  # 비교용으로 맨해튼 거리 사용

    if (dx, dy) not in directions:
        directions[(dx, dy)] = dist
    else:
        directions[(dx, dy)] = min(directions[(dx, dy)], dist)

# 각 방향에서 가장 가까운 학생만 카운트 (방향 수가 답)
print(len(directions))
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 29197 - 아침 태권도
// 원점에서 다른 학생에게 가려지지 않는 학생 수를 구하는 문제
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());

        // 각 방향별로 가장 가까운 거리 저장
        Map<Long, Integer> directions = new HashMap<>();

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());

            // 방향 벡터를 기약 형태로 변환
            int g = gcd(Math.abs(x), Math.abs(y));
            int dx = x / g;
            int dy = y / g;

            // 방향을 하나의 키로 변환 (dx * 2000001 + dy)
            long key = (long)(dx + 1000000) * 2000001 + (dy + 1000000);

            // 거리 계산 (맨해튼 거리)
            int dist = Math.abs(x) + Math.abs(y);

            if (!directions.containsKey(key)) {
                directions.put(key, dist);
            } else {
                directions.put(key, Math.min(directions.get(key), dist));
            }
        }

        System.out.println(directions.size());
    }

    static int gcd(int a, int b) {
        return b == 0 ? a : gcd(b, a % b);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <map>
#include <cmath>
using namespace std;

// 백준 29197 - 아침 태권도
// 원점에서 다른 학생에게 가려지지 않는 학생 수를 구하는 문제

int gcd(int a, int b) {
    return b == 0 ? a : gcd(b, a % b);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    // 각 방향별로 가장 가까운 거리 저장
    map<pair<int, int>, int> directions;

    for (int i = 0; i < n; i++) {
        int x, y;
        cin >> x >> y;

        // 방향 벡터를 기약 형태로 변환
        int g = gcd(abs(x), abs(y));
        int dx = x / g;
        int dy = y / g;

        // 거리 계산 (맨해튼 거리)
        int dist = abs(x) + abs(y);

        auto key = make_pair(dx, dy);
        if (directions.find(key) == directions.end()) {
            directions[key] = dist;
        } else {
            directions[key] = min(directions[key], dist);
        }
    }

    cout << directions.size() << "\\n";

    return 0;
}
'''
        }
    ],

    # 문제 10: baekjoon_15996 - 팩토리얼 나누기
    # N!을 A^k로 나눌 때 나머지가 0이 되는 최대 k 구하기
    "baekjoon_15996": [
        {
            "language": "python",
            "code": '''# 백준 15996 - 팩토리얼 나누기
# N!을 A^k로 나눌 때 나머지가 0이 되는 최대 k 구하기
# 르장드르 공식: N!에서 소수 p의 지수 = floor(N/p) + floor(N/p^2) + ...

import sys
input = sys.stdin.readline

n, a = map(int, input().split())

# 르장드르 공식 적용
k = 0
power = a
while power <= n:
    k += n // power
    power *= a

print(k)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 15996 - 팩토리얼 나누기
// N!을 A^k로 나눌 때 나머지가 0이 되는 최대 k 구하기
// 르장드르 공식 사용
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long n = Long.parseLong(st.nextToken());
        long a = Long.parseLong(st.nextToken());

        // 르장드르 공식 적용
        long k = 0;
        long power = a;
        while (power <= n) {
            k += n / power;
            power *= a;
        }

        System.out.println(k);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

// 백준 15996 - 팩토리얼 나누기
// N!을 A^k로 나눌 때 나머지가 0이 되는 최대 k 구하기
// 르장드르 공식 사용

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long n, a;
    cin >> n >> a;

    // 르장드르 공식 적용
    long long k = 0;
    long long power = a;
    while (power <= n) {
        k += n / power;
        power *= a;
    }

    cout << k << "\\n";

    return 0;
}
'''
        }
    ]
}

def main():
    # JSON 파일 읽기
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # 문제별 인덱스 매핑
    problem_indices = {
        "baekjoon_30969": 2346,
        "baekjoon_24498": 2348,
        "baekjoon_5376": 2349,
        "baekjoon_15739": 2393,
        "baekjoon_17499": 2400,
        "baekjoon_11277": 2408,
        "baekjoon_2090": 2418,
        "baekjoon_25375": 2441,
        "baekjoon_29197": 2449,
        "baekjoon_15996": 2464
    }

    updated_count = 0

    for problem_id, solutions in SOLUTIONS.items():
        idx = problem_indices.get(problem_id)
        if idx is not None and idx < len(data):
            # 기존 솔루션이 비어있는지 확인
            if not data[idx].get('solutions') or len(data[idx].get('solutions', [])) == 0:
                data[idx]['solutions'] = solutions
                updated_count += 1
                print(f"Updated: {problem_id} at index {idx}")
            else:
                print(f"Skipped (already has solutions): {problem_id}")

    # JSON 파일에 저장 (fcntl 잠금 사용)
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\nTotal updated: {updated_count} problems")

    # 남은 빈 솔루션 개수 확인
    empty_count = sum(1 for p in data if not p.get('solutions') or len(p.get('solutions', [])) == 0)
    print(f"Remaining empty solutions: {empty_count}")

if __name__ == "__main__":
    main()
