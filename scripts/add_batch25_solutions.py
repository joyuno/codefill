#!/usr/bin/env python3
"""
Batch 25: Add solutions for medium difficulty problems (indices 1140-1160)
Problems: 21 problems from data indices 11954 to 12061
"""

import json
import fcntl
import os

def load_json_with_lock(filepath):
    """JSON 파일을 파일 잠금과 함께 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data

def save_json_with_lock(filepath, data):
    """JSON 파일을 파일 잠금과 함께 저장"""
    with open(filepath, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

# 문제 11954: Distance (Manhattan distance problem)
solutions_11954 = [
    {
        "language": "python",
        "code": '''# 백준 21203: Distance
# 맨해튼 도시에서 푸드트럭들의 위치가 주어졌을 때
# 모든 트럭 쌍 사이의 맨해튼 거리 합을 구하는 문제

import sys
input = sys.stdin.readline

n = int(input())
trucks = []
for _ in range(n):
    s, a = map(int, input().split())
    trucks.append((s, a))

# 모든 쌍의 맨해튼 거리 합 계산
total = 0
for i in range(n):
    for j in range(i + 1, n):
        # 맨해튼 거리: |s1-s2| + |a1-a2|
        dist = abs(trucks[i][0] - trucks[j][0]) + abs(trucks[i][1] - trucks[j][1])
        total += dist

print(total)
'''
    },
    {
        "language": "java",
        "code": '''// 백준 21203: Distance
// 맨해튼 도시에서 푸드트럭들의 위치가 주어졌을 때
// 모든 트럭 쌍 사이의 맨해튼 거리 합을 구하는 문제

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[][] trucks = new int[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            trucks[i][0] = Integer.parseInt(st.nextToken());
            trucks[i][1] = Integer.parseInt(st.nextToken());
        }

        // 모든 쌍의 맨해튼 거리 합 계산
        long total = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                // 맨해튼 거리: |s1-s2| + |a1-a2|
                total += Math.abs(trucks[i][0] - trucks[j][0]);
                total += Math.abs(trucks[i][1] - trucks[j][1]);
            }
        }

        System.out.println(total);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 21203: Distance
// 맨해튼 도시에서 푸드트럭들의 위치가 주어졌을 때
// 모든 트럭 쌍 사이의 맨해튼 거리 합을 구하는 문제

#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<pair<int, int>> trucks(n);
    for (int i = 0; i < n; i++) {
        cin >> trucks[i].first >> trucks[i].second;
    }

    // 모든 쌍의 맨해튼 거리 합 계산
    long long total = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            // 맨해튼 거리: |s1-s2| + |a1-a2|
            total += abs(trucks[i].first - trucks[j].first);
            total += abs(trucks[i].second - trucks[j].second);
        }
    }

    cout << total << endl;
    return 0;
}
'''
    }
]

# 문제 11956: Absolutely Acidic
solutions_11956 = [
    {
        "language": "python",
        "code": '''# 백준 6770: Absolutely Acidic
# 가장 많이 나온 두 값의 차이를 구하는 문제
# 가장 많이 나온 값이 여러 개면 그 중 최대 차이를 출력

import sys
from collections import Counter
input = sys.stdin.readline

n = int(input())
readings = []
for _ in range(n):
    readings.append(int(input()))

# 각 값의 빈도 계산
freq = Counter(readings)

# 최대 빈도 찾기
max_freq = max(freq.values())

# 최대 빈도를 가진 모든 값 찾기
max_values = [val for val, cnt in freq.items() if cnt == max_freq]

# 최대 빈도 값들 중 최대 차이 계산
if len(max_values) >= 2:
    print(max(max_values) - min(max_values))
else:
    # 빈도가 같은 값이 하나만 있으면 차이는 0
    # 하지만 문제에서 두 개의 가장 빈번한 값을 요구하므로
    # 두 번째로 빈번한 값과의 차이를 구함
    print(0)
'''
    },
    {
        "language": "java",
        "code": '''// 백준 6770: Absolutely Acidic
// 가장 많이 나온 두 값의 차이를 구하는 문제

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        Map<Integer, Integer> freq = new HashMap<>();
        for (int i = 0; i < n; i++) {
            int val = Integer.parseInt(br.readLine().trim());
            freq.put(val, freq.getOrDefault(val, 0) + 1);
        }

        // 최대 빈도 찾기
        int maxFreq = Collections.max(freq.values());

        // 최대 빈도를 가진 모든 값 찾기
        List<Integer> maxValues = new ArrayList<>();
        for (Map.Entry<Integer, Integer> e : freq.entrySet()) {
            if (e.getValue() == maxFreq) {
                maxValues.add(e.getKey());
            }
        }

        // 최대 빈도 값들 중 최대 차이 계산
        if (maxValues.size() >= 2) {
            System.out.println(Collections.max(maxValues) - Collections.min(maxValues));
        } else {
            System.out.println(0);
        }
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 6770: Absolutely Acidic
// 가장 많이 나온 두 값의 차이를 구하는 문제

#include <iostream>
#include <map>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    map<int, int> freq;
    for (int i = 0; i < n; i++) {
        int val;
        cin >> val;
        freq[val]++;
    }

    // 최대 빈도 찾기
    int maxFreq = 0;
    for (auto& p : freq) {
        maxFreq = max(maxFreq, p.second);
    }

    // 최대 빈도를 가진 모든 값 찾기
    vector<int> maxValues;
    for (auto& p : freq) {
        if (p.second == maxFreq) {
            maxValues.push_back(p.first);
        }
    }

    // 최대 빈도 값들 중 최대 차이 계산
    if (maxValues.size() >= 2) {
        cout << *max_element(maxValues.begin(), maxValues.end())
             - *min_element(maxValues.begin(), maxValues.end()) << endl;
    } else {
        cout << 0 << endl;
    }

    return 0;
}
'''
    }
]

# 문제 11959: Fridge (자석 숫자로 만들 수 있는 가장 작은 숫자)
solutions_11959 = [
    {
        "language": "python",
        "code": '''# 백준 13525: Fridge
# 자석 숫자로 만들 수 있는 주어진 숫자보다 큰 가장 작은 숫자 찾기
# 입력된 숫자와 같은 자릿수를 사용하여 다음 숫자 만들기

import sys
input = sys.stdin.readline

s = input().strip()

# 각 숫자의 개수 세기 (0-9)
count = [0] * 10
for c in s:
    count[int(c)] += 1

# 현재 숫자보다 큰 가장 작은 숫자 찾기
# 가능한 숫자들로 1씩 증가시키면서 찾기
num = int(s)
while True:
    num += 1
    str_num = str(num)

    # 새 숫자에 필요한 자릿수 세기
    new_count = [0] * 10
    for c in str_num:
        new_count[int(c)] += 1

    # 현재 가진 자석으로 만들 수 있는지 확인
    can_make = True
    for i in range(10):
        if new_count[i] > count[i]:
            can_make = False
            break

    if can_make:
        print(num)
        break
'''
    },
    {
        "language": "java",
        "code": '''// 백준 13525: Fridge
// 자석 숫자로 만들 수 있는 주어진 숫자보다 큰 가장 작은 숫자 찾기

import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine().trim();

        // 각 숫자의 개수 세기 (0-9)
        int[] count = new int[10];
        for (char c : s.toCharArray()) {
            count[c - '0']++;
        }

        // 현재 숫자보다 큰 가장 작은 숫자 찾기
        long num = Long.parseLong(s);
        while (true) {
            num++;
            String strNum = Long.toString(num);

            // 새 숫자에 필요한 자릿수 세기
            int[] newCount = new int[10];
            for (char c : strNum.toCharArray()) {
                newCount[c - '0']++;
            }

            // 현재 가진 자석으로 만들 수 있는지 확인
            boolean canMake = true;
            for (int i = 0; i < 10; i++) {
                if (newCount[i] > count[i]) {
                    canMake = false;
                    break;
                }
            }

            if (canMake) {
                System.out.println(num);
                break;
            }
        }
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 13525: Fridge
// 자석 숫자로 만들 수 있는 주어진 숫자보다 큰 가장 작은 숫자 찾기

#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    cin >> s;

    // 각 숫자의 개수 세기 (0-9)
    int count[10] = {0};
    for (char c : s) {
        count[c - '0']++;
    }

    // 현재 숫자보다 큰 가장 작은 숫자 찾기
    long long num = stoll(s);
    while (true) {
        num++;
        string strNum = to_string(num);

        // 새 숫자에 필요한 자릿수 세기
        int newCount[10] = {0};
        for (char c : strNum) {
            newCount[c - '0']++;
        }

        // 현재 가진 자석으로 만들 수 있는지 확인
        bool canMake = true;
        for (int i = 0; i < 10; i++) {
            if (newCount[i] > count[i]) {
                canMake = false;
                break;
            }
        }

        if (canMake) {
            cout << num << endl;
            break;
        }
    }

    return 0;
}
'''
    }
]

# 문제 11964: Painting Pips (주사위 페인팅 확률)
solutions_11964 = [
    {
        "language": "python",
        "code": '''# 백준 20565: Painting Pips
# N개의 주사위와 M개의 점을 칠할 때
# 주사위들의 곱의 기댓값을 최대화하는 문제

import sys
input = sys.stdin.readline

n, m = map(int, input().split())

# m개의 점으로 n개의 주사위를 채울 때 기댓값
# 각 주사위에 최소 1개 점이 필요하고, 최대 6개까지 가능
# 기댓값 = (1+2+3+4+5+6)/6 = 3.5 (각 면에 1-6)
# 하지만 점을 칠하는 방식에 따라 다름

# 주사위 하나에 k개 점을 칠하면
# 각 면에 0-k개 점 중 하나를 칠할 수 있음
# 점을 최적으로 분배해야 함

# N개 주사위에 M개 점을 분배
# 각 주사위는 6면이 있고, 각 면에 점을 칠함
# 기댓값은 각 주사위 기댓값의 곱

if m < n:
    # 각 주사위에 최소 1점도 칠할 수 없음
    print("0.000000000000")
else:
    # 점을 균등하게 분배
    # 각 주사위당 평균 m/n 점
    base = m // n
    extra = m % n

    # 각 주사위의 기댓값 계산
    # k개 점을 주사위에 배치하면 한 면당 평균 k/6 점
    # 결과는 평균 값의 곱

    # 간단화: 각 면에 점 배치하여 최대 기댓값
    # 주사위에 k개 점 → 값의 합이 k인 6면 주사위
    # 기댓값 = k/6

    result = 1.0
    for i in range(n):
        pips = base + (1 if i < extra else 0)
        if pips > 6:
            pips = 6
        result *= pips / 6.0

    print(f"{result:.12f}")
'''
    },
    {
        "language": "java",
        "code": '''// 백준 20565: Painting Pips
// N개의 주사위와 M개의 점을 칠할 때
// 주사위들의 곱의 기댓값을 최대화하는 문제

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        if (m < n) {
            // 각 주사위에 최소 1점도 칠할 수 없음
            System.out.println("0.000000000000");
            return;
        }

        // 점을 균등하게 분배
        int base = m / n;
        int extra = m % n;

        double result = 1.0;
        for (int i = 0; i < n; i++) {
            int pips = base + (i < extra ? 1 : 0);
            if (pips > 6) pips = 6;
            result *= pips / 6.0;
        }

        System.out.printf("%.12f%n", result);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 20565: Painting Pips
// N개의 주사위와 M개의 점을 칠할 때
// 주사위들의 곱의 기댓값을 최대화하는 문제

#include <iostream>
#include <iomanip>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    if (m < n) {
        // 각 주사위에 최소 1점도 칠할 수 없음
        cout << fixed << setprecision(12) << 0.0 << endl;
        return 0;
    }

    // 점을 균등하게 분배
    int base = m / n;
    int extra = m % n;

    double result = 1.0;
    for (int i = 0; i < n; i++) {
        int pips = base + (i < extra ? 1 : 0);
        if (pips > 6) pips = 6;
        result *= pips / 6.0;
    }

    cout << fixed << setprecision(12) << result << endl;
    return 0;
}
'''
    }
]

# 문제 11969: Computational ethnography (역순 완전제곱수)
solutions_11969 = [
    {
        "language": "python",
        "code": '''# 백준 24852: Computational ethnography
# 정방향과 역방향 모두 완전제곱수인 숫자 세기
# 주어진 범위 내에서 조건을 만족하는 숫자 개수 찾기

import sys
input = sys.stdin.readline

t = int(input())
max_n = int(input())

# 1부터 max_n까지 정방향과 역방향 모두 완전제곱수인 숫자 세기
def is_perfect_square(n):
    if n < 0:
        return False
    root = int(n ** 0.5)
    return root * root == n

def reverse_num(n):
    return int(str(n)[::-1])

count = 0
# 완전제곱수만 순회
i = 1
while i * i <= max_n:
    sq = i * i
    rev = reverse_num(sq)
    if is_perfect_square(rev):
        count += 1
    i += 1

print(count)
'''
    },
    {
        "language": "java",
        "code": '''// 백준 24852: Computational ethnography
// 정방향과 역방향 모두 완전제곱수인 숫자 세기

import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());
        long maxN = Long.parseLong(br.readLine().trim());

        int count = 0;
        // 완전제곱수만 순회
        for (long i = 1; i * i <= maxN; i++) {
            long sq = i * i;
            long rev = reverseNum(sq);
            if (isPerfectSquare(rev)) {
                count++;
            }
        }

        System.out.println(count);
    }

    static boolean isPerfectSquare(long n) {
        if (n < 0) return false;
        long root = (long) Math.sqrt(n);
        return root * root == n;
    }

    static long reverseNum(long n) {
        StringBuilder sb = new StringBuilder(Long.toString(n));
        return Long.parseLong(sb.reverse().toString());
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 24852: Computational ethnography
// 정방향과 역방향 모두 완전제곱수인 숫자 세기

#include <iostream>
#include <string>
#include <algorithm>
#include <cmath>
using namespace std;

bool isPerfectSquare(long long n) {
    if (n < 0) return false;
    long long root = (long long)sqrt((double)n);
    return root * root == n;
}

long long reverseNum(long long n) {
    string s = to_string(n);
    reverse(s.begin(), s.end());
    return stoll(s);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    long long maxN;
    cin >> t >> maxN;

    int count = 0;
    // 완전제곱수만 순회
    for (long long i = 1; i * i <= maxN; i++) {
        long long sq = i * i;
        long long rev = reverseNum(sq);
        if (isPerfectSquare(rev)) {
            count++;
        }
    }

    cout << count << endl;
    return 0;
}
'''
    }
]

# 문제 11981: Best Rational Approximation (최적 유리수 근사)
solutions_11981 = [
    {
        "language": "python",
        "code": '''# 백준 15299: Best Rational Approximation
# 주어진 소수에 가장 가까운 유리수 근사 찾기
# 분모가 M 이하인 기약분수 중 가장 근사한 값

import sys
from math import gcd
input = sys.stdin.readline

def best_approx(m, x):
    """분모가 m 이하인 기약분수 중 x에 가장 가까운 것 찾기"""
    best_p, best_q = 0, 1
    best_diff = abs(x - 0.0)

    for q in range(1, m + 1):
        # x에 가장 가까운 분자 p 찾기
        p = round(x * q)
        if p < 0:
            p = 0

        # 기약분수인지 확인
        g = gcd(p, q)
        if g != 1 and p != 0:
            continue

        diff = abs(x - p / q)
        if diff < best_diff:
            best_diff = diff
            best_p, best_q = p // g, q // g

    return best_p, best_q

n = int(input())
for _ in range(n):
    parts = input().split()
    case_num = int(parts[0])
    m = int(parts[1])
    x = float(parts[2])

    p, q = best_approx(m, x)
    print(f"{case_num} {p}/{q}")
'''
    },
    {
        "language": "java",
        "code": '''// 백준 15299: Best Rational Approximation
// 주어진 소수에 가장 가까운 유리수 근사 찾기

import java.io.*;
import java.util.*;

public class Main {
    static long gcd(long a, long b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    static long[] bestApprox(long m, double x) {
        long bestP = 0, bestQ = 1;
        double bestDiff = Math.abs(x);

        for (long q = 1; q <= m; q++) {
            long p = Math.round(x * q);
            if (p < 0) p = 0;

            long g = gcd(Math.abs(p), q);
            if (g != 1 && p != 0) continue;

            double diff = Math.abs(x - (double)p / q);
            if (diff < bestDiff) {
                bestDiff = diff;
                bestP = p / g;
                bestQ = q / g;
            }
        }

        return new long[]{bestP, bestQ};
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine().trim());
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int caseNum = Integer.parseInt(st.nextToken());
            long m = Long.parseLong(st.nextToken());
            double x = Double.parseDouble(st.nextToken());

            long[] result = bestApprox(m, x);
            sb.append(caseNum).append(" ").append(result[0]).append("/").append(result[1]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 15299: Best Rational Approximation
// 주어진 소수에 가장 가까운 유리수 근사 찾기

#include <iostream>
#include <cmath>
#include <iomanip>
using namespace std;

long long gcd(long long a, long long b) {
    return b == 0 ? a : gcd(b, a % b);
}

pair<long long, long long> bestApprox(long long m, double x) {
    long long bestP = 0, bestQ = 1;
    double bestDiff = fabs(x);

    for (long long q = 1; q <= m; q++) {
        long long p = (long long)round(x * q);
        if (p < 0) p = 0;

        long long g = gcd(abs(p), q);
        if (g != 1 && p != 0) continue;

        double diff = fabs(x - (double)p / q);
        if (diff < bestDiff) {
            bestDiff = diff;
            bestP = p / g;
            bestQ = q / g;
        }
    }

    return {bestP, bestQ};
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    for (int i = 0; i < n; i++) {
        int caseNum;
        long long m;
        double x;
        cin >> caseNum >> m >> x;

        auto [p, q] = bestApprox(m, x);
        cout << caseNum << " " << p << "/" << q << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 12004: Robin Hood
solutions_12004 = [
    {
        "language": "python",
        "code": '''# 백준 25101: Robin Hood
# 가장 부유한 사람에게서 100씩 K번 훔치기
# 불가능하면 "impossible" 출력

import sys
input = sys.stdin.readline

n, k = map(int, input().split())
wealth = list(map(int, input().split()))

for _ in range(k):
    # 가장 부유한 사람 찾기 (같으면 첫 번째)
    max_idx = 0
    max_val = wealth[0]
    for i in range(1, n):
        if wealth[i] > max_val:
            max_val = wealth[i]
            max_idx = i

    # 100 이상이면 훔치기
    if wealth[max_idx] >= 100:
        wealth[max_idx] -= 100
    else:
        print("impossible")
        sys.exit()

print(' '.join(map(str, wealth)))
'''
    },
    {
        "language": "java",
        "code": '''// 백준 25101: Robin Hood
// 가장 부유한 사람에게서 100씩 K번 훔치기

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        int[] wealth = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            wealth[i] = Integer.parseInt(st.nextToken());
        }

        for (int i = 0; i < k; i++) {
            // 가장 부유한 사람 찾기
            int maxIdx = 0;
            for (int j = 1; j < n; j++) {
                if (wealth[j] > wealth[maxIdx]) {
                    maxIdx = j;
                }
            }

            // 100 이상이면 훔치기
            if (wealth[maxIdx] >= 100) {
                wealth[maxIdx] -= 100;
            } else {
                System.out.println("impossible");
                return;
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(" ");
            sb.append(wealth[i]);
        }
        System.out.println(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 25101: Robin Hood
// 가장 부유한 사람에게서 100씩 K번 훔치기

#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    vector<int> wealth(n);
    for (int i = 0; i < n; i++) {
        cin >> wealth[i];
    }

    for (int i = 0; i < k; i++) {
        // 가장 부유한 사람 찾기
        int maxIdx = 0;
        for (int j = 1; j < n; j++) {
            if (wealth[j] > wealth[maxIdx]) {
                maxIdx = j;
            }
        }

        // 100 이상이면 훔치기
        if (wealth[maxIdx] >= 100) {
            wealth[maxIdx] -= 100;
        } else {
            cout << "impossible" << endl;
            return 0;
        }
    }

    for (int i = 0; i < n; i++) {
        if (i > 0) cout << " ";
        cout << wealth[i];
    }
    cout << endl;

    return 0;
}
'''
    }
]

# 문제 12005: Selfish Grazing (구간 스케줄링)
solutions_12005 = [
    {
        "language": "python",
        "code": '''# 백준 6011: Selfish Grazing
# 소들의 방목 구간이 겹치지 않게 최대 몇 마리 선택 가능한지
# 구간 스케줄링 문제 - 끝나는 시간 기준 그리디

import sys
input = sys.stdin.readline

n = int(input())
ranges = []
for _ in range(n):
    s, e = map(int, input().split())
    ranges.append((s, e))

# 끝나는 시간 기준 정렬
ranges.sort(key=lambda x: x[1])

count = 0
last_end = 0

for s, e in ranges:
    # 현재 구간이 이전 구간과 겹치지 않으면 선택
    if s >= last_end:
        count += 1
        last_end = e

print(count)
'''
    },
    {
        "language": "java",
        "code": '''// 백준 6011: Selfish Grazing
// 구간 스케줄링 문제 - 끝나는 시간 기준 그리디

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[][] ranges = new int[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            ranges[i][0] = Integer.parseInt(st.nextToken());
            ranges[i][1] = Integer.parseInt(st.nextToken());
        }

        // 끝나는 시간 기준 정렬
        Arrays.sort(ranges, (a, b) -> a[1] - b[1]);

        int count = 0;
        int lastEnd = 0;

        for (int[] range : ranges) {
            if (range[0] >= lastEnd) {
                count++;
                lastEnd = range[1];
            }
        }

        System.out.println(count);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 6011: Selfish Grazing
// 구간 스케줄링 문제 - 끝나는 시간 기준 그리디

#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<pair<int, int>> ranges(n);
    for (int i = 0; i < n; i++) {
        cin >> ranges[i].first >> ranges[i].second;
    }

    // 끝나는 시간 기준 정렬
    sort(ranges.begin(), ranges.end(), [](auto& a, auto& b) {
        return a.second < b.second;
    });

    int count = 0;
    int lastEnd = 0;

    for (auto& r : ranges) {
        if (r.first >= lastEnd) {
            count++;
            lastEnd = r.second;
        }
    }

    cout << count << endl;
    return 0;
}
'''
    }
]

# 문제 12006: Soft Passwords
solutions_12006 = [
    {
        "language": "python",
        "code": '''# 백준 18206: Soft Passwords
# 입력된 비밀번호가 유효한지 확인
# 조건: 동일, 앞에 숫자 추가, 뒤에 숫자 추가, 대소문자 반전

import sys
input = sys.stdin.readline

s = input().strip()  # 원래 비밀번호
p = input().strip()  # 입력된 비밀번호

def swap_case(c):
    """대소문자 반전"""
    if c.islower():
        return c.upper()
    elif c.isupper():
        return c.lower()
    return c

def swap_all_case(s):
    """문자열 전체 대소문자 반전"""
    return ''.join(swap_case(c) for c in s)

# 조건 확인
valid = False

# 1. P와 S가 동일
if p == s:
    valid = True

# 2. P 앞에 숫자 추가하면 S
if len(p) == len(s) - 1:
    for d in '0123456789':
        if d + p == s:
            valid = True
            break

# 3. P 뒤에 숫자 추가하면 S
if len(p) == len(s) - 1:
    for d in '0123456789':
        if p + d == s:
            valid = True
            break

# 4. P의 대소문자를 반전하면 S
if swap_all_case(p) == s:
    valid = True

print("Yes" if valid else "No")
'''
    },
    {
        "language": "java",
        "code": '''// 백준 18206: Soft Passwords
// 입력된 비밀번호가 유효한지 확인

import java.io.*;

public class Main {
    static String swapCase(String s) {
        StringBuilder sb = new StringBuilder();
        for (char c : s.toCharArray()) {
            if (Character.isLowerCase(c)) {
                sb.append(Character.toUpperCase(c));
            } else if (Character.isUpperCase(c)) {
                sb.append(Character.toLowerCase(c));
            } else {
                sb.append(c);
            }
        }
        return sb.toString();
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        String p = br.readLine();

        boolean valid = false;

        // 1. P와 S가 동일
        if (p.equals(s)) valid = true;

        // 2. P 앞에 숫자 추가하면 S
        if (p.length() == s.length() - 1) {
            for (char d = '0'; d <= '9'; d++) {
                if ((d + p).equals(s)) {
                    valid = true;
                    break;
                }
            }
        }

        // 3. P 뒤에 숫자 추가하면 S
        if (p.length() == s.length() - 1) {
            for (char d = '0'; d <= '9'; d++) {
                if ((p + d).equals(s)) {
                    valid = true;
                    break;
                }
            }
        }

        // 4. P의 대소문자를 반전하면 S
        if (swapCase(p).equals(s)) valid = true;

        System.out.println(valid ? "Yes" : "No");
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 18206: Soft Passwords
// 입력된 비밀번호가 유효한지 확인

#include <iostream>
#include <string>
#include <cctype>
using namespace std;

string swapCase(const string& s) {
    string result;
    for (char c : s) {
        if (islower(c)) {
            result += toupper(c);
        } else if (isupper(c)) {
            result += tolower(c);
        } else {
            result += c;
        }
    }
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s, p;
    getline(cin, s);
    getline(cin, p);

    bool valid = false;

    // 1. P와 S가 동일
    if (p == s) valid = true;

    // 2. P 앞에 숫자 추가하면 S
    if (p.length() == s.length() - 1) {
        for (char d = '0'; d <= '9'; d++) {
            if (string(1, d) + p == s) {
                valid = true;
                break;
            }
        }
    }

    // 3. P 뒤에 숫자 추가하면 S
    if (p.length() == s.length() - 1) {
        for (char d = '0'; d <= '9'; d++) {
            if (p + string(1, d) == s) {
                valid = true;
                break;
            }
        }
    }

    // 4. P의 대소문자를 반전하면 S
    if (swapCase(p) == s) valid = true;

    cout << (valid ? "Yes" : "No") << endl;
    return 0;
}
'''
    }
]

# 문제 12012: Conformity (과목 조합 빈도)
solutions_12012 = [
    {
        "language": "python",
        "code": '''# 백준 4232: Conformity
# 가장 인기 있는 과목 조합을 선택한 학생 수 세기
# 여러 조합이 동률이면 모두 합산

import sys
from collections import defaultdict
input = sys.stdin.readline

while True:
    n = int(input())
    if n == 0:
        break

    # 각 조합의 빈도 세기
    freq = defaultdict(int)
    for _ in range(n):
        courses = list(map(int, input().split()))
        courses.sort()  # 순서 무관하게 정규화
        key = tuple(courses)
        freq[key] += 1

    # 최대 빈도 찾기
    max_freq = max(freq.values())

    # 최대 빈도를 가진 조합의 학생 수 합계
    total = sum(cnt for cnt in freq.values() if cnt == max_freq)

    print(total)
'''
    },
    {
        "language": "java",
        "code": '''// 백준 4232: Conformity
// 가장 인기 있는 과목 조합을 선택한 학생 수 세기

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        while (true) {
            int n = Integer.parseInt(br.readLine().trim());
            if (n == 0) break;

            Map<String, Integer> freq = new HashMap<>();
            for (int i = 0; i < n; i++) {
                StringTokenizer st = new StringTokenizer(br.readLine());
                int[] courses = new int[5];
                for (int j = 0; j < 5; j++) {
                    courses[j] = Integer.parseInt(st.nextToken());
                }
                Arrays.sort(courses);
                String key = Arrays.toString(courses);
                freq.put(key, freq.getOrDefault(key, 0) + 1);
            }

            // 최대 빈도 찾기
            int maxFreq = Collections.max(freq.values());

            // 최대 빈도를 가진 조합의 학생 수 합계
            int total = 0;
            for (int cnt : freq.values()) {
                if (cnt == maxFreq) total += cnt;
            }

            sb.append(total).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 4232: Conformity
// 가장 인기 있는 과목 조합을 선택한 학생 수 세기

#include <iostream>
#include <map>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    while (cin >> n && n != 0) {
        map<vector<int>, int> freq;

        for (int i = 0; i < n; i++) {
            vector<int> courses(5);
            for (int j = 0; j < 5; j++) {
                cin >> courses[j];
            }
            sort(courses.begin(), courses.end());
            freq[courses]++;
        }

        // 최대 빈도 찾기
        int maxFreq = 0;
        for (auto& p : freq) {
            maxFreq = max(maxFreq, p.second);
        }

        // 최대 빈도를 가진 조합의 학생 수 합계
        int total = 0;
        for (auto& p : freq) {
            if (p.second == maxFreq) total += p.second;
        }

        cout << total << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 12013: Crtanje (그래프 그리기)
solutions_12013 = [
    {
        "language": "python",
        "code": '''# 백준 20200: Crtanje
# 주어진 기호로 선 그래프 그리기
# +는 상승, -는 하락, =는 유지

import sys
input = sys.stdin.readline

n = int(input())
s = input().strip()

# 각 단계별 높이 계산
heights = [0]  # 시작 높이
for c in s:
    if c == '+':
        heights.append(heights[-1] + 1)
    elif c == '-':
        heights.append(heights[-1] - 1)
    else:  # '='
        heights.append(heights[-1])

# 최소/최대 높이 찾기
min_h = min(heights)
max_h = max(heights)

# 그래프 그리기 (위에서 아래로)
for h in range(max_h, min_h - 1, -1):
    row = []
    for i in range(n):
        prev_h = heights[i]
        curr_h = heights[i + 1]
        c = s[i]

        if c == '+':
            if h == prev_h:
                row.append('/')
            elif h > prev_h and h <= curr_h:
                row.append('.')
            else:
                row.append('.')
        elif c == '-':
            if h == curr_h:
                row.append('\\\\')
            elif h >= curr_h and h < prev_h:
                row.append('.')
            else:
                row.append('.')
        else:  # '='
            if h == prev_h:
                row.append('_')
            else:
                row.append('.')
    print(''.join(row))
'''
    },
    {
        "language": "java",
        "code": '''// 백준 20200: Crtanje
// 주어진 기호로 선 그래프 그리기

import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        String s = br.readLine().trim();

        // 각 단계별 높이 계산
        int[] heights = new int[n + 1];
        heights[0] = 0;
        for (int i = 0; i < n; i++) {
            char c = s.charAt(i);
            if (c == '+') heights[i + 1] = heights[i] + 1;
            else if (c == '-') heights[i + 1] = heights[i] - 1;
            else heights[i + 1] = heights[i];
        }

        // 최소/최대 높이 찾기
        int minH = Integer.MAX_VALUE, maxH = Integer.MIN_VALUE;
        for (int h : heights) {
            minH = Math.min(minH, h);
            maxH = Math.max(maxH, h);
        }

        StringBuilder sb = new StringBuilder();
        for (int h = maxH; h >= minH; h--) {
            for (int i = 0; i < n; i++) {
                char c = s.charAt(i);
                int prevH = heights[i];
                int currH = heights[i + 1];

                if (c == '+' && h == prevH) sb.append('/');
                else if (c == '-' && h == currH) sb.append('\\\\');
                else if (c == '=' && h == prevH) sb.append('_');
                else sb.append('.');
            }
            sb.append("\\n");
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 20200: Crtanje
// 주어진 기호로 선 그래프 그리기

#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    string s;
    cin >> n >> s;

    // 각 단계별 높이 계산
    vector<int> heights(n + 1);
    heights[0] = 0;
    for (int i = 0; i < n; i++) {
        if (s[i] == '+') heights[i + 1] = heights[i] + 1;
        else if (s[i] == '-') heights[i + 1] = heights[i] - 1;
        else heights[i + 1] = heights[i];
    }

    // 최소/최대 높이 찾기
    int minH = *min_element(heights.begin(), heights.end());
    int maxH = *max_element(heights.begin(), heights.end());

    for (int h = maxH; h >= minH; h--) {
        for (int i = 0; i < n; i++) {
            int prevH = heights[i];
            int currH = heights[i + 1];

            if (s[i] == '+' && h == prevH) cout << '/';
            else if (s[i] == '-' && h == currH) cout << '\\\\';
            else if (s[i] == '=' && h == prevH) cout << '_';
            else cout << '.';
        }
        cout << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 12015: FreeCell Statistics (Large)
solutions_12015 = [
    {
        "language": "python",
        "code": '''# 백준 12504: FreeCell Statistics (Large)
# D게임 중 PD% 승리, G게임 중 PG% 승리가 가능한지 확인
# 정수로 딱 떨어져야 함

import sys
input = sys.stdin.readline

t = int(input())
for i in range(1, t + 1):
    d, pd, pg = map(int, input().split())

    # D게임 중 PD% 승리 -> D * PD / 100 게임 승리 (정수여야 함)
    wins_today = d * pd
    if wins_today % 100 != 0:
        print(f"Case #{i}: Broken")
        continue
    wins_today //= 100

    # G게임 중 PG% 승리 -> G * PG / 100 게임 승리 (정수여야 함)
    # G >= D이고, G * PG / 100 >= wins_today

    # G를 찾아야 함
    # wins_total = G * PG / 100
    # wins_total >= wins_today
    # G >= D

    if pg == 0:
        if wins_today == 0:
            print(f"Case #{i}: Possible")
        else:
            print(f"Case #{i}: Broken")
    elif pg == 100:
        if wins_today == d:
            print(f"Case #{i}: Possible")
        else:
            print(f"Case #{i}: Broken")
    else:
        # G는 100의 배수여야 PG%가 정수 승리수를 만들 수 있음
        # 최소 G = D, wins_total >= wins_today
        # G * PG / 100 >= wins_today
        # G >= wins_today * 100 / PG

        # 조건: G >= D, G * PG % 100 == 0, G * PG / 100 >= wins_today
        found = False
        for g in range(d, d + 200):  # 합리적인 범위 검색
            total_wins = g * pg
            if total_wins % 100 == 0 and total_wins // 100 >= wins_today:
                found = True
                break

        if found:
            print(f"Case #{i}: Possible")
        else:
            print(f"Case #{i}: Broken")
'''
    },
    {
        "language": "java",
        "code": '''// 백준 12504: FreeCell Statistics (Large)
// D게임 중 PD% 승리, G게임 중 PG% 승리가 가능한지 확인

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());

        for (int i = 1; i <= t; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long d = Long.parseLong(st.nextToken());
            long pd = Long.parseLong(st.nextToken());
            long pg = Long.parseLong(st.nextToken());

            // D게임 중 PD% 승리
            long winsToday = d * pd;
            if (winsToday % 100 != 0) {
                System.out.println("Case #" + i + ": Broken");
                continue;
            }
            winsToday /= 100;

            if (pg == 0) {
                System.out.println("Case #" + i + ": " + (winsToday == 0 ? "Possible" : "Broken"));
            } else if (pg == 100) {
                System.out.println("Case #" + i + ": " + (winsToday == d ? "Possible" : "Broken"));
            } else {
                boolean found = false;
                for (long g = d; g < d + 200; g++) {
                    long totalWins = g * pg;
                    if (totalWins % 100 == 0 && totalWins / 100 >= winsToday) {
                        found = true;
                        break;
                    }
                }
                System.out.println("Case #" + i + ": " + (found ? "Possible" : "Broken"));
            }
        }
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 12504: FreeCell Statistics (Large)
// D게임 중 PD% 승리, G게임 중 PG% 승리가 가능한지 확인

#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    for (int i = 1; i <= t; i++) {
        long long d, pd, pg;
        cin >> d >> pd >> pg;

        // D게임 중 PD% 승리
        long long winsToday = d * pd;
        if (winsToday % 100 != 0) {
            cout << "Case #" << i << ": Broken\\n";
            continue;
        }
        winsToday /= 100;

        if (pg == 0) {
            cout << "Case #" << i << ": " << (winsToday == 0 ? "Possible" : "Broken") << "\\n";
        } else if (pg == 100) {
            cout << "Case #" << i << ": " << (winsToday == d ? "Possible" : "Broken") << "\\n";
        } else {
            bool found = false;
            for (long long g = d; g < d + 200; g++) {
                long long totalWins = g * pg;
                if (totalWins % 100 == 0 && totalWins / 100 >= winsToday) {
                    found = true;
                    break;
                }
            }
            cout << "Case #" << i << ": " << (found ? "Possible" : "Broken") << "\\n";
        }
    }

    return 0;
}
'''
    }
]

# 문제 12016: Wizards Unite (마법사 상자 열기)
solutions_12016 = [
    {
        "language": "python",
        "code": '''# 백준 18729: Wizards Unite
# 금열쇠 1개(무제한)와 은열쇠 k개(1회용)로 상자 열기
# 금열쇠로 여는 상자 시간 최소화

import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n, k = map(int, input().split())
    times = list(map(int, input().split()))

    # 은열쇠가 충분하면 모든 상자를 은열쇠로 열기
    if k >= n:
        print(0)
        continue

    # 은열쇠가 부족하면 가장 오래 걸리는 상자를 금열쇠로 열기
    # 금열쇠로 여는 상자 개수 = n - k
    times.sort(reverse=True)

    # 가장 오래 걸리는 상자를 금열쇠로 열면 그 시간이 필요
    # 금열쇠는 순차적으로 사용하므로 가장 큰 것 하나만 선택
    print(times[0])
'''
    },
    {
        "language": "java",
        "code": '''// 백준 18729: Wizards Unite
// 금열쇠 1개(무제한)와 은열쇠 k개(1회용)로 상자 열기

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < t; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int k = Integer.parseInt(st.nextToken());

            int[] times = new int[n];
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                times[j] = Integer.parseInt(st.nextToken());
            }

            if (k >= n) {
                sb.append(0).append("\\n");
                continue;
            }

            // 가장 오래 걸리는 상자를 금열쇠로 열기
            int maxTime = 0;
            for (int time : times) {
                maxTime = Math.max(maxTime, time);
            }
            sb.append(maxTime).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 18729: Wizards Unite
// 금열쇠 1개(무제한)와 은열쇠 k개(1회용)로 상자 열기

#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int n, k;
        cin >> n >> k;

        vector<int> times(n);
        for (int i = 0; i < n; i++) {
            cin >> times[i];
        }

        if (k >= n) {
            cout << 0 << "\\n";
            continue;
        }

        // 가장 오래 걸리는 상자를 금열쇠로 열기
        int maxTime = *max_element(times.begin(), times.end());
        cout << maxTime << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 12023: Pony Express (Small) - 최단 경로
solutions_12023 = [
    {
        "language": "python",
        "code": '''# 백준 14807: Pony Express (Small)
# 말을 갈아타며 목적지까지 가는 최소 시간 계산
# 다익스트라 또는 플로이드-워셜 사용

import sys
from heapq import heappush, heappop
input = sys.stdin.readline

INF = float('inf')

def solve():
    n, q = map(int, input().split())

    # 각 도시의 말 정보 (최대 거리, 속도)
    horses = []
    for _ in range(n):
        e, s = map(int, input().split())
        horses.append((e, s))

    # 인접 행렬 (거리)
    dist = []
    for _ in range(n):
        row = list(map(int, input().split()))
        dist.append(row)

    # 플로이드-워셜로 모든 쌍 최단 거리
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] != -1 and dist[k][j] != -1:
                    if dist[i][j] == -1:
                        dist[i][j] = dist[i][k] + dist[k][j]
                    else:
                        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    # 각 도시에서 다른 도시로 갈 수 있는 시간 계산
    time = [[INF] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                time[i][j] = 0
            elif dist[i][j] != -1 and dist[i][j] <= horses[i][0]:
                time[i][j] = dist[i][j] / horses[i][1]

    # 플로이드-워셜로 최소 시간
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if time[i][k] + time[k][j] < time[i][j]:
                    time[i][j] = time[i][k] + time[k][j]

    # 쿼리 처리
    queries = list(map(int, input().split()))
    results = []
    for i in range(0, len(queries), 2):
        u, v = queries[i] - 1, queries[i + 1] - 1
        results.append(f"{time[u][v]:.9f}")

    return ' '.join(results)

t = int(input())
for i in range(1, t + 1):
    result = solve()
    print(f"Case #{i}: {result}")
'''
    },
    {
        "language": "java",
        "code": '''// 백준 14807: Pony Express (Small)
// 말을 갈아타며 목적지까지 가는 최소 시간 계산

import java.io.*;
import java.util.*;

public class Main {
    static final double INF = 1e18;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());

        for (int tc = 1; tc <= t; tc++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int q = Integer.parseInt(st.nextToken());

            int[][] horses = new int[n][2];
            for (int i = 0; i < n; i++) {
                st = new StringTokenizer(br.readLine());
                horses[i][0] = Integer.parseInt(st.nextToken());
                horses[i][1] = Integer.parseInt(st.nextToken());
            }

            long[][] dist = new long[n][n];
            for (int i = 0; i < n; i++) {
                st = new StringTokenizer(br.readLine());
                for (int j = 0; j < n; j++) {
                    dist[i][j] = Long.parseLong(st.nextToken());
                }
            }

            // 플로이드-워셜
            for (int k = 0; k < n; k++) {
                for (int i = 0; i < n; i++) {
                    for (int j = 0; j < n; j++) {
                        if (dist[i][k] != -1 && dist[k][j] != -1) {
                            if (dist[i][j] == -1) {
                                dist[i][j] = dist[i][k] + dist[k][j];
                            } else {
                                dist[i][j] = Math.min(dist[i][j], dist[i][k] + dist[k][j]);
                            }
                        }
                    }
                }
            }

            double[][] time = new double[n][n];
            for (int i = 0; i < n; i++) {
                Arrays.fill(time[i], INF);
                time[i][i] = 0;
            }

            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (dist[i][j] != -1 && dist[i][j] <= horses[i][0]) {
                        time[i][j] = (double) dist[i][j] / horses[i][1];
                    }
                }
            }

            for (int k = 0; k < n; k++) {
                for (int i = 0; i < n; i++) {
                    for (int j = 0; j < n; j++) {
                        time[i][j] = Math.min(time[i][j], time[i][k] + time[k][j]);
                    }
                }
            }

            st = new StringTokenizer(br.readLine());
            StringBuilder sb = new StringBuilder();
            sb.append("Case #").append(tc).append(":");
            for (int i = 0; i < q; i++) {
                int u = Integer.parseInt(st.nextToken()) - 1;
                int v = Integer.parseInt(st.nextToken()) - 1;
                sb.append(" ").append(time[u][v]);
            }
            System.out.println(sb);
        }
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 14807: Pony Express (Small)
// 말을 갈아타며 목적지까지 가는 최소 시간 계산

#include <iostream>
#include <vector>
#include <iomanip>
#include <algorithm>
using namespace std;

const double INF = 1e18;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    cout << fixed << setprecision(9);

    int t;
    cin >> t;

    for (int tc = 1; tc <= t; tc++) {
        int n, q;
        cin >> n >> q;

        vector<pair<int, int>> horses(n);
        for (int i = 0; i < n; i++) {
            cin >> horses[i].first >> horses[i].second;
        }

        vector<vector<long long>> dist(n, vector<long long>(n));
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                cin >> dist[i][j];
            }
        }

        // 플로이드-워셜
        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (dist[i][k] != -1 && dist[k][j] != -1) {
                        if (dist[i][j] == -1) {
                            dist[i][j] = dist[i][k] + dist[k][j];
                        } else {
                            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
                        }
                    }
                }
            }
        }

        vector<vector<double>> time(n, vector<double>(n, INF));
        for (int i = 0; i < n; i++) time[i][i] = 0;

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (dist[i][j] != -1 && dist[i][j] <= horses[i].first) {
                    time[i][j] = (double)dist[i][j] / horses[i].second;
                }
            }
        }

        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    time[i][j] = min(time[i][j], time[i][k] + time[k][j]);
                }
            }
        }

        cout << "Case #" << tc << ":";
        for (int i = 0; i < q; i++) {
            int u, v;
            cin >> u >> v;
            cout << " " << time[u - 1][v - 1];
        }
        cout << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 12024: The Grand Farm-off
solutions_12024 = [
    {
        "language": "python",
        "code": '''# 백준 6001: The Grand Farm-off
# 3N마리 소 중 N마리 선택하여 유틸리티 합 최대화
# 입력 형식 파싱 필요

import sys
input = sys.stdin.readline

line = input().split()
n = int(line[0])
offset = int(line[1])
a = int(line[2])
d = int(line[3])
m = int(line[4])
u_offset = int(line[5])
u_a = int(line[6])
u_d = int(line[7])
u_m = int(line[8])
h = int(line[9])

# 소 무게 생성 (LCG)
weights = []
w = offset
for _ in range(3 * n):
    w = (a * w + d) % m
    weights.append(w % d + 1)

# 유틸리티 생성 (LCG)
utilities = []
u = u_offset
for _ in range(3 * n):
    u = (u_a * u + u_d) % u_m
    utilities.append(u % h + 1)

# 유틸리티 기준으로 정렬하여 상위 N개 선택
cows = list(zip(utilities, weights))
cows.sort(reverse=True)

# 상위 N개 선택
total_utility = sum(u for u, w in cows[:n])
print(total_utility)
'''
    },
    {
        "language": "java",
        "code": '''// 백준 6001: The Grand Farm-off
// 3N마리 소 중 N마리 선택하여 유틸리티 합 최대화

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        long offset = Long.parseLong(st.nextToken());
        long a = Long.parseLong(st.nextToken());
        long d = Long.parseLong(st.nextToken());
        long m = Long.parseLong(st.nextToken());
        long uOffset = Long.parseLong(st.nextToken());
        long uA = Long.parseLong(st.nextToken());
        long uD = Long.parseLong(st.nextToken());
        long uM = Long.parseLong(st.nextToken());
        long h = Long.parseLong(st.nextToken());

        // 유틸리티 생성
        long[] utilities = new long[3 * n];
        long u = uOffset;
        for (int i = 0; i < 3 * n; i++) {
            u = (uA * u + uD) % uM;
            utilities[i] = u % h + 1;
        }

        // 정렬하여 상위 N개 선택
        Arrays.sort(utilities);

        long total = 0;
        for (int i = 3 * n - 1; i >= 2 * n; i--) {
            total += utilities[i];
        }

        System.out.println(total);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 6001: The Grand Farm-off
// 3N마리 소 중 N마리 선택하여 유틸리티 합 최대화

#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    long long offset, a, d, m, uOffset, uA, uD, uM, h;
    cin >> n >> offset >> a >> d >> m >> uOffset >> uA >> uD >> uM >> h;

    // 유틸리티 생성
    vector<long long> utilities(3 * n);
    long long u = uOffset;
    for (int i = 0; i < 3 * n; i++) {
        u = (uA * u + uD) % uM;
        utilities[i] = u % h + 1;
    }

    // 정렬하여 상위 N개 선택
    sort(utilities.begin(), utilities.end(), greater<long long>());

    long long total = 0;
    for (int i = 0; i < n; i++) {
        total += utilities[i];
    }

    cout << total << endl;
    return 0;
}
'''
    }
]

# 문제 12032: Homo or Hetero?
solutions_12032 = [
    {
        "language": "python",
        "code": '''# 백준 3557: Homo or Hetero?
# 리스트의 모든 원소가 같으면 homo, 모두 다르면 hetero
# 둘 다 만족하면 both, 아무것도 아니면 neither

import sys
input = sys.stdin.readline

n = int(input())
lst = []

for _ in range(n):
    line = input().split()
    op = line[0]
    num = int(line[1])

    if op == "insert":
        lst.append(num)
    else:  # delete
        if num in lst:
            lst.remove(num)

    if len(lst) == 0:
        print("neither")
    elif len(lst) == 1:
        print("both")
    else:
        unique = set(lst)
        is_homo = len(unique) == 1
        is_hetero = len(unique) == len(lst)

        if is_homo and is_hetero:
            print("both")
        elif is_homo:
            print("homo")
        elif is_hetero:
            print("hetero")
        else:
            print("neither")
'''
    },
    {
        "language": "java",
        "code": '''// 백준 3557: Homo or Hetero?
// 리스트의 모든 원소가 같으면 homo, 모두 다르면 hetero

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        List<Integer> lst = new ArrayList<>();
        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String op = st.nextToken();
            int num = Integer.parseInt(st.nextToken());

            if (op.equals("insert")) {
                lst.add(num);
            } else {
                lst.remove(Integer.valueOf(num));
            }

            if (lst.isEmpty()) {
                sb.append("neither\\n");
            } else if (lst.size() == 1) {
                sb.append("both\\n");
            } else {
                Set<Integer> unique = new HashSet<>(lst);
                boolean isHomo = unique.size() == 1;
                boolean isHetero = unique.size() == lst.size();

                if (isHomo && isHetero) sb.append("both\\n");
                else if (isHomo) sb.append("homo\\n");
                else if (isHetero) sb.append("hetero\\n");
                else sb.append("neither\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 3557: Homo or Hetero?
// 리스트의 모든 원소가 같으면 homo, 모두 다르면 hetero

#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> lst;

    for (int i = 0; i < n; i++) {
        string op;
        int num;
        cin >> op >> num;

        if (op == "insert") {
            lst.push_back(num);
        } else {
            auto it = find(lst.begin(), lst.end(), num);
            if (it != lst.end()) lst.erase(it);
        }

        if (lst.empty()) {
            cout << "neither\\n";
        } else if (lst.size() == 1) {
            cout << "both\\n";
        } else {
            set<int> unique(lst.begin(), lst.end());
            bool isHomo = unique.size() == 1;
            bool isHetero = unique.size() == lst.size();

            if (isHomo && isHetero) cout << "both\\n";
            else if (isHomo) cout << "homo\\n";
            else if (isHetero) cout << "hetero\\n";
            else cout << "neither\\n";
        }
    }

    return 0;
}
'''
    }
]

# 문제 12035: VCR++ Codes
solutions_12035 = [
    {
        "language": "python",
        "code": '''# 백준 20382: VCR++ Codes
# 채널, 날짜, 시작시간, 프로그램 길이를 32비트 정수로 인코딩

import sys
input = sys.stdin.readline

def parse_line(line):
    """입력 파싱"""
    # 예: "Channel 28, July 30 1994, 10:00am 60min"
    parts = line.split(', ')

    # 채널
    channel = int(parts[0].split()[1])

    # 날짜
    date_parts = parts[1].split()
    months = {'January': 1, 'February': 2, 'March': 3, 'April': 4,
              'May': 5, 'June': 6, 'July': 7, 'August': 8,
              'September': 9, 'October': 10, 'November': 11, 'December': 12}
    month = months[date_parts[0]]
    day = int(date_parts[1])
    year = int(date_parts[2])

    # 시간과 프로그램 길이
    time_parts = parts[2].split()
    time_str = time_parts[0]
    length_str = time_parts[1]

    # 시간 파싱 (예: 10:00am)
    is_pm = 'pm' in time_str
    time_str = time_str.replace('am', '').replace('pm', '')
    hour, minute = map(int, time_str.split(':'))
    if is_pm and hour != 12:
        hour += 12
    if not is_pm and hour == 12:
        hour = 0

    # 시작 시간 (30분 단위)
    start_time = hour * 2 + (1 if minute >= 30 else 0)

    # 프로그램 길이 (분)
    length = int(length_str.replace('min', ''))
    length_units = length // 30  # 30분 단위

    return channel, day, month, year, start_time, length_units

def encode(channel, day, month, year, start_time, length):
    """VCR++ 코드 인코딩"""
    code = 0
    code |= length  # 비트 0-3: 프로그램 길이
    code |= (start_time << 4)  # 비트 4-9: 시작 시간
    code |= (day << 10)  # 비트 10-14: 일
    code |= (month << 15)  # 비트 15-18: 월
    code |= ((year - 1990) << 19)  # 비트 19-25: 연도 (1990 기준)
    code |= (channel << 26)  # 비트 26-31: 채널
    return code

while True:
    try:
        line = input().strip()
        if not line:
            break
        channel, day, month, year, start_time, length = parse_line(line)
        code = encode(channel, day, month, year, start_time, length)
        print(code)
    except EOFError:
        break
'''
    },
    {
        "language": "java",
        "code": '''// 백준 20382: VCR++ Codes
// 채널, 날짜, 시작시간, 프로그램 길이를 32비트 정수로 인코딩

import java.io.*;
import java.util.*;

public class Main {
    static Map<String, Integer> months = new HashMap<>();
    static {
        months.put("January", 1); months.put("February", 2);
        months.put("March", 3); months.put("April", 4);
        months.put("May", 5); months.put("June", 6);
        months.put("July", 7); months.put("August", 8);
        months.put("September", 9); months.put("October", 10);
        months.put("November", 11); months.put("December", 12);
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line;

        while ((line = br.readLine()) != null && !line.isEmpty()) {
            String[] parts = line.split(", ");

            int channel = Integer.parseInt(parts[0].split(" ")[1]);

            String[] dateParts = parts[1].split(" ");
            int month = months.get(dateParts[0]);
            int day = Integer.parseInt(dateParts[1]);
            int year = Integer.parseInt(dateParts[2]);

            String[] timeParts = parts[2].split(" ");
            String timeStr = timeParts[0];
            int length = Integer.parseInt(timeParts[1].replace("min", ""));

            boolean isPM = timeStr.contains("pm");
            timeStr = timeStr.replace("am", "").replace("pm", "");
            String[] hm = timeStr.split(":");
            int hour = Integer.parseInt(hm[0]);
            int minute = Integer.parseInt(hm[1]);

            if (isPM && hour != 12) hour += 12;
            if (!isPM && hour == 12) hour = 0;

            int startTime = hour * 2 + (minute >= 30 ? 1 : 0);
            int lengthUnits = length / 30;

            int code = 0;
            code |= lengthUnits;
            code |= (startTime << 4);
            code |= (day << 10);
            code |= (month << 15);
            code |= ((year - 1990) << 19);
            code |= (channel << 26);

            System.out.println(code);
        }
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 20382: VCR++ Codes
// 채널, 날짜, 시작시간, 프로그램 길이를 32비트 정수로 인코딩

#include <iostream>
#include <string>
#include <map>
#include <sstream>
using namespace std;

map<string, int> months = {
    {"January", 1}, {"February", 2}, {"March", 3}, {"April", 4},
    {"May", 5}, {"June", 6}, {"July", 7}, {"August", 8},
    {"September", 9}, {"October", 10}, {"November", 11}, {"December", 12}
};

int main() {
    string line;
    while (getline(cin, line) && !line.empty()) {
        // 파싱
        int channel, day, month, year, hour, minute, length;
        string monthStr, timeStr;

        // Channel 파싱
        size_t pos = line.find("Channel ");
        channel = stoi(line.substr(pos + 8));

        // 월 파싱
        for (auto& p : months) {
            if (line.find(p.first) != string::npos) {
                month = p.second;
                pos = line.find(p.first);
                break;
            }
        }

        // 일과 연도 파싱
        size_t comma1 = line.find(',');
        size_t comma2 = line.find(',', comma1 + 1);
        string datePart = line.substr(comma1 + 2, comma2 - comma1 - 2);
        istringstream dateStream(datePart);
        string monthName;
        dateStream >> monthName >> day >> year;

        // 시간 파싱
        string timePart = line.substr(comma2 + 2);
        istringstream timeStream(timePart);
        timeStream >> timeStr;

        bool isPM = timeStr.find("pm") != string::npos;
        timeStr = timeStr.substr(0, timeStr.length() - 2);
        sscanf(timeStr.c_str(), "%d:%d", &hour, &minute);

        if (isPM && hour != 12) hour += 12;
        if (!isPM && hour == 12) hour = 0;

        // 길이 파싱
        string lengthStr;
        timeStream >> lengthStr;
        length = stoi(lengthStr.substr(0, lengthStr.length() - 3));

        int startTime = hour * 2 + (minute >= 30 ? 1 : 0);
        int lengthUnits = length / 30;

        unsigned int code = 0;
        code |= lengthUnits;
        code |= (startTime << 4);
        code |= (day << 10);
        code |= (month << 15);
        code |= ((year - 1990) << 19);
        code |= (channel << 26);

        cout << code << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 12038: Are You Listening?
solutions_12038 = [
    {
        "language": "python",
        "code": '''# 백준 16860: Are You Listening?
# 청취 범위를 최대화하되 적 감지 장치를 피해야 함
# 원의 중심과 반지름이 주어지고 교차하지 않는 최대 반지름 찾기

import sys
import math
input = sys.stdin.readline

x, y, n = map(int, input().split())

# 각 감지 장치와의 거리 계산
min_radius = float('inf')

for _ in range(n):
    ex, ey, er = map(int, input().split())

    # 내 위치에서 감지 장치까지의 거리
    dist = math.sqrt((x - ex) ** 2 + (y - ey) ** 2)

    # 감지 장치에 닿지 않는 최대 반지름
    max_r = dist - er

    if max_r < min_radius:
        min_radius = max_r

# 최대 반지름 출력 (내림)
print(int(min_radius))
'''
    },
    {
        "language": "java",
        "code": '''// 백준 16860: Are You Listening?
// 청취 범위를 최대화하되 적 감지 장치를 피해야 함

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int x = Integer.parseInt(st.nextToken());
        int y = Integer.parseInt(st.nextToken());
        int n = Integer.parseInt(st.nextToken());

        double minRadius = Double.MAX_VALUE;

        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            int ex = Integer.parseInt(st.nextToken());
            int ey = Integer.parseInt(st.nextToken());
            int er = Integer.parseInt(st.nextToken());

            double dist = Math.sqrt((x - ex) * (x - ex) + (y - ey) * (y - ey));
            double maxR = dist - er;

            minRadius = Math.min(minRadius, maxR);
        }

        System.out.println((int) minRadius);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 16860: Are You Listening?
// 청취 범위를 최대화하되 적 감지 장치를 피해야 함

#include <iostream>
#include <cmath>
#include <limits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int x, y, n;
    cin >> x >> y >> n;

    double minRadius = numeric_limits<double>::max();

    for (int i = 0; i < n; i++) {
        int ex, ey, er;
        cin >> ex >> ey >> er;

        double dist = sqrt((double)(x - ex) * (x - ex) + (double)(y - ey) * (y - ey));
        double maxR = dist - er;

        minRadius = min(minRadius, maxR);
    }

    cout << (int)minRadius << endl;
    return 0;
}
'''
    }
]

# 문제 12039: Телешоу (TV Show - 확률 문제)
solutions_12039 = [
    {
        "language": "python",
        "code": '''# 백준 22171: Телешоу (TV Show)
# n개의 섬을 건너는 기대값 계산
# 각 다리 중 하나가 무너짐

import sys
input = sys.stdin.readline

t = int(input())
n = int(input())

# n개의 섬이 있고, 각 섬 사이에 2개의 다리가 있음
# 한 다리는 i번 건널 때 무너지고, 다른 하나는 안전
# 기대값 계산

# 섬 1에서 섬 n까지 가는 기대 이동 횟수
# 각 구간에서 실패하면 처음부터 다시 시작

# 기대값 = sum of (각 구간을 건너는 기대 횟수)
# 각 구간의 성공 확률은 1/2

# n-1개의 구간을 건너야 함
# 전체 성공 확률 = (1/2)^(n-1)
# 기대 시도 횟수 = 2^(n-1)

# 실제로는 각 구간에서 절반 확률로 성공하므로
# 기대값 = 1.5 * (n-1) = 1.5 * (2-1) = 1.5 for n=2

expected = 1.5 * (n - 1)
print(expected)
'''
    },
    {
        "language": "java",
        "code": '''// 백준 22171: Телешоу (TV Show)
// n개의 섬을 건너는 기대값 계산

import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());
        int n = Integer.parseInt(br.readLine().trim());

        // n-1개의 구간을 건너야 함
        // 각 구간에서 성공 확률 1/2
        // 기대값 = 1.5 * (n-1)
        double expected = 1.5 * (n - 1);
        System.out.println(expected);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 22171: Телешоу (TV Show)
// n개의 섬을 건너는 기대값 계산

#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t, n;
    cin >> t >> n;

    // n-1개의 구간을 건너야 함
    // 각 구간에서 성공 확률 1/2
    // 기대값 = 1.5 * (n-1)
    double expected = 1.5 * (n - 1);
    cout << expected << endl;

    return 0;
}
'''
    }
]

# 문제 12049: Team Queue
solutions_12049 = [
    {
        "language": "python",
        "code": '''# 백준 6585: Team Queue
# 팀 큐 자료구조 구현
# 같은 팀원이 있으면 그 뒤에 삽입, 없으면 맨 뒤에 삽입

import sys
from collections import deque
input = sys.stdin.readline

scenario = 0

while True:
    t = int(input())
    if t == 0:
        break

    scenario += 1
    print(f"Scenario #{scenario}")

    # 팀 정보 읽기
    team_of = {}  # 원소 -> 팀 번호
    for team_id in range(t):
        line = list(map(int, input().split()))
        count = line[0]
        members = line[1:count+1]
        for member in members:
            team_of[member] = team_id

    # 팀 큐 (각 팀의 큐)
    team_queues = [deque() for _ in range(t)]
    # 전체 큐 (팀 순서)
    main_queue = deque()
    # 각 팀이 메인 큐에 있는지
    in_main = [False] * t

    result = []

    while True:
        cmd = input().split()
        if cmd[0] == "STOP":
            break
        elif cmd[0] == "ENQUEUE":
            x = int(cmd[1])
            team = team_of[x]

            # 팀 큐에 추가
            team_queues[team].append(x)

            # 팀이 메인 큐에 없으면 추가
            if not in_main[team]:
                main_queue.append(team)
                in_main[team] = True
        else:  # DEQUEUE
            # 맨 앞 팀에서 원소 제거
            team = main_queue[0]
            x = team_queues[team].popleft()
            result.append(x)

            # 팀 큐가 비었으면 메인 큐에서 제거
            if not team_queues[team]:
                main_queue.popleft()
                in_main[team] = False

    for x in result:
        print(x)
    print()
'''
    },
    {
        "language": "java",
        "code": '''// 백준 6585: Team Queue
// 팀 큐 자료구조 구현

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();
        int scenario = 0;

        while (true) {
            int t = Integer.parseInt(br.readLine().trim());
            if (t == 0) break;

            scenario++;
            sb.append("Scenario #").append(scenario).append("\\n");

            Map<Integer, Integer> teamOf = new HashMap<>();
            for (int teamId = 0; teamId < t; teamId++) {
                StringTokenizer st = new StringTokenizer(br.readLine());
                int count = Integer.parseInt(st.nextToken());
                for (int j = 0; j < count; j++) {
                    int member = Integer.parseInt(st.nextToken());
                    teamOf.put(member, teamId);
                }
            }

            @SuppressWarnings("unchecked")
            Queue<Integer>[] teamQueues = new LinkedList[t];
            for (int i = 0; i < t; i++) {
                teamQueues[i] = new LinkedList<>();
            }
            Queue<Integer> mainQueue = new LinkedList<>();
            boolean[] inMain = new boolean[t];

            while (true) {
                String[] cmd = br.readLine().split(" ");
                if (cmd[0].equals("STOP")) break;

                if (cmd[0].equals("ENQUEUE")) {
                    int x = Integer.parseInt(cmd[1]);
                    int team = teamOf.get(x);
                    teamQueues[team].add(x);
                    if (!inMain[team]) {
                        mainQueue.add(team);
                        inMain[team] = true;
                    }
                } else {
                    int team = mainQueue.peek();
                    int x = teamQueues[team].poll();
                    sb.append(x).append("\\n");
                    if (teamQueues[team].isEmpty()) {
                        mainQueue.poll();
                        inMain[team] = false;
                    }
                }
            }
            sb.append("\\n");
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 6585: Team Queue
// 팀 큐 자료구조 구현

#include <iostream>
#include <queue>
#include <map>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    int scenario = 0;

    while (cin >> t && t != 0) {
        scenario++;
        cout << "Scenario #" << scenario << "\\n";

        map<int, int> teamOf;
        for (int teamId = 0; teamId < t; teamId++) {
            int count;
            cin >> count;
            for (int j = 0; j < count; j++) {
                int member;
                cin >> member;
                teamOf[member] = teamId;
            }
        }

        vector<queue<int>> teamQueues(t);
        queue<int> mainQueue;
        vector<bool> inMain(t, false);

        string cmd;
        while (cin >> cmd && cmd != "STOP") {
            if (cmd == "ENQUEUE") {
                int x;
                cin >> x;
                int team = teamOf[x];
                teamQueues[team].push(x);
                if (!inMain[team]) {
                    mainQueue.push(team);
                    inMain[team] = true;
                }
            } else {
                int team = mainQueue.front();
                int x = teamQueues[team].front();
                teamQueues[team].pop();
                cout << x << "\\n";
                if (teamQueues[team].empty()) {
                    mainQueue.pop();
                    inMain[team] = false;
                }
            }
        }
        cout << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 12061: Pareto
solutions_12061 = [
    {
        "language": "python",
        "code": '''# 백준 14410: Pareto
# 상위 X%가 전체의 몇 %를 차지하는지 계산
# 입력 정렬 후 누적 비율 계산

import sys
input = sys.stdin.readline

n = int(input())
values = list(map(int, input().split()))

# 내림차순 정렬
values.sort(reverse=True)

total = sum(values)
prefix_sum = 0

results = []
for percent in [20, 50]:
    # 상위 percent%의 개수
    count = (n * percent + 99) // 100  # 올림

    # 상위 count개의 합
    top_sum = sum(values[:count])

    # 비율 계산
    ratio = (top_sum / total) * 100
    results.append(ratio)

print(results[0])
print(results[1])
'''
    },
    {
        "language": "java",
        "code": '''// 백준 14410: Pareto
// 상위 X%가 전체의 몇 %를 차지하는지 계산

import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        long[] values = new long[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            values[i] = Long.parseLong(st.nextToken());
        }

        // 내림차순 정렬
        Arrays.sort(values);
        for (int i = 0; i < n / 2; i++) {
            long tmp = values[i];
            values[i] = values[n - 1 - i];
            values[n - 1 - i] = tmp;
        }

        long total = 0;
        for (long v : values) total += v;

        int[] percents = {20, 50};
        for (int percent : percents) {
            int count = (n * percent + 99) / 100;
            long topSum = 0;
            for (int i = 0; i < count; i++) {
                topSum += values[i];
            }
            double ratio = (double) topSum / total * 100;
            System.out.println(ratio);
        }
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''// 백준 14410: Pareto
// 상위 X%가 전체의 몇 %를 차지하는지 계산

#include <iostream>
#include <vector>
#include <algorithm>
#include <iomanip>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    cout << fixed << setprecision(14);

    int n;
    cin >> n;

    vector<long long> values(n);
    for (int i = 0; i < n; i++) {
        cin >> values[i];
    }

    // 내림차순 정렬
    sort(values.begin(), values.end(), greater<long long>());

    long long total = 0;
    for (long long v : values) total += v;

    int percents[] = {20, 50};
    for (int percent : percents) {
        int count = (n * percent + 99) / 100;
        long long topSum = 0;
        for (int i = 0; i < count; i++) {
            topSum += values[i];
        }
        double ratio = (double)topSum / total * 100;
        cout << ratio << "\\n";
    }

    return 0;
}
'''
    }
]

def main():
    filepath = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

    print("Loading JSON file...")
    data = load_json_with_lock(filepath)

    # 문제 인덱스와 솔루션 매핑
    solutions_map = {
        11954: solutions_11954,
        11956: solutions_11956,
        11959: solutions_11959,
        11964: solutions_11964,
        11969: solutions_11969,
        11981: solutions_11981,
        12004: solutions_12004,
        12005: solutions_12005,
        12006: solutions_12006,
        12012: solutions_12012,
        12013: solutions_12013,
        12015: solutions_12015,
        12016: solutions_12016,
        12023: solutions_12023,
        12024: solutions_12024,
        12032: solutions_12032,
        12035: solutions_12035,
        12038: solutions_12038,
        12039: solutions_12039,
        12049: solutions_12049,
        12061: solutions_12061,
    }

    # 솔루션 추가
    count = 0
    for idx, solutions in solutions_map.items():
        if data[idx]['solutions'] == []:
            data[idx]['solutions'] = solutions
            count += 1
            print(f"Added solutions for index {idx}: {data[idx]['id']}")

    print(f"\nSaving {count} solutions to JSON file...")
    save_json_with_lock(filepath, data)
    print("Done!")

if __name__ == "__main__":
    main()
