#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medium 난이도 문제 200-209에 대한 솔루션 생성 스크립트
"""

import json
import fcntl

JSON_FILE = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

def main():
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        problems = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    empty_medium = []
    for i, problem in enumerate(problems):
        difficulty = problem.get('difficulty', '')
        solutions = problem.get('solutions', [])
        input_output = problem.get('input_output', '')

        if difficulty == 'medium' and (not solutions or len(solutions) == 0) and input_output:
            empty_medium.append({
                'original_index': i,
                'problem': problem
            })

    print(f"총 빈 medium 문제 수: {len(empty_medium)}")

    solutions_to_add = {}

    # 문제 200: 27724 - 팝핀 소다
    solutions_to_add[200] = [
        {
            "language": "python",
            "code": '''# 백준 27724: 팝핀 소다
# N명 중 토너먼트에서 최대 몇 번 승리할 수 있는지
# K는 탄산 내성, M은 이변의 수
import sys
import math
input = sys.stdin.readline

n, m, k = map(int, input().split())

# 이변 없이 이길 수 있는 횟수: k-1명보다 강하므로 log2(k)번
# 이변을 사용하면 더 강한 상대도 이길 수 있음

# 총 라운드 수
total_rounds = int(math.log2(n))

# 정상적으로 이길 수 있는 횟수: K보다 작은 사람과 만나면 이김
# 최대 log2(K) 라운드까지 정상 승리 가능

wins_without_upset = 0
remaining = k - 1  # K보다 약한 사람 수
for _ in range(total_rounds):
    if remaining > 0:
        wins_without_upset += 1
        remaining = remaining // 2
    else:
        break

# 이변을 사용하면 추가 라운드 승리 가능
# 각 라운드에서 이변 1번 사용 시 1라운드 추가 승리
total_wins = min(wins_without_upset + m, total_rounds)

print(total_wins)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int k = sc.nextInt();

        int totalRounds = (int)(Math.log(n) / Math.log(2));

        int winsWithoutUpset = 0;
        int remaining = k - 1;
        for (int i = 0; i < totalRounds; i++) {
            if (remaining > 0) {
                winsWithoutUpset++;
                remaining /= 2;
            } else {
                break;
            }
        }

        int totalWins = Math.min(winsWithoutUpset + m, totalRounds);
        System.out.println(totalWins);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, k;
    cin >> n >> m >> k;

    int totalRounds = (int)log2(n);

    int winsWithoutUpset = 0;
    int remaining = k - 1;
    for (int i = 0; i < totalRounds; i++) {
        if (remaining > 0) {
            winsWithoutUpset++;
            remaining /= 2;
        } else {
            break;
        }
    }

    int totalWins = min(winsWithoutUpset + m, totalRounds);
    cout << totalWins << endl;

    return 0;
}
'''
        }
    ]

    # 문제 201: 25329 - 학생별 통화 요금 계산
    solutions_to_add[201] = [
        {
            "language": "python",
            "code": '''# 백준 25329: 학생별 통화 요금 계산
import sys
from collections import defaultdict
input = sys.stdin.readline

n = int(input())
total_minutes = defaultdict(int)

for _ in range(n):
    parts = input().strip().split()
    time = parts[0]
    name = parts[1]

    h, m = map(int, time.split(':'))
    minutes = h * 60 + m
    total_minutes[name] += minutes

# 요금 계산
# 기본 시간: 100분, 기본 요금: 10원
# 단위 시간: 50분, 단위 요금: 3원

def calc_fee(minutes):
    if minutes <= 100:
        return 10
    else:
        extra = minutes - 100
        extra_units = (extra + 49) // 50  # 올림
        return 10 + extra_units * 3

result = []
for name, minutes in total_minutes.items():
    fee = calc_fee(minutes)
    result.append((name, fee))

# 요금 내림차순, 이름 오름차순
result.sort(key=lambda x: (-x[1], x[0]))

for name, fee in result:
    print(name, fee)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = Integer.parseInt(sc.nextLine());

        Map<String, Integer> totalMinutes = new HashMap<>();

        for (int i = 0; i < n; i++) {
            String[] parts = sc.nextLine().split(" ");
            String[] time = parts[0].split(":");
            int h = Integer.parseInt(time[0]);
            int m = Integer.parseInt(time[1]);
            int minutes = h * 60 + m;
            String name = parts[1];

            totalMinutes.put(name, totalMinutes.getOrDefault(name, 0) + minutes);
        }

        List<String[]> result = new ArrayList<>();
        for (Map.Entry<String, Integer> e : totalMinutes.entrySet()) {
            int fee = calcFee(e.getValue());
            result.add(new String[]{e.getKey(), String.valueOf(fee)});
        }

        result.sort((a, b) -> {
            int feeA = Integer.parseInt(a[1]);
            int feeB = Integer.parseInt(b[1]);
            if (feeA != feeB) return feeB - feeA;
            return a[0].compareTo(b[0]);
        });

        for (String[] r : result) {
            System.out.println(r[0] + " " + r[1]);
        }
    }

    static int calcFee(int minutes) {
        if (minutes <= 100) return 10;
        int extra = minutes - 100;
        int extraUnits = (extra + 49) / 50;
        return 10 + extraUnits * 3;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <map>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

int calcFee(int minutes) {
    if (minutes <= 100) return 10;
    int extra = minutes - 100;
    int extraUnits = (extra + 49) / 50;
    return 10 + extraUnits * 3;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    map<string, int> totalMinutes;

    for (int i = 0; i < n; i++) {
        string time, name;
        cin >> time >> name;

        int h = stoi(time.substr(0, 2));
        int m = stoi(time.substr(3, 2));
        int minutes = h * 60 + m;

        totalMinutes[name] += minutes;
    }

    vector<pair<string, int>> result;
    for (auto& p : totalMinutes) {
        int fee = calcFee(p.second);
        result.push_back({p.first, fee});
    }

    sort(result.begin(), result.end(), [](auto& a, auto& b) {
        if (a.second != b.second) return a.second > b.second;
        return a.first < b.first;
    });

    for (auto& r : result) {
        cout << r.first << " " << r.second << "\\n";
    }

    return 0;
}
'''
        }
    ]

    # 문제 202: 30786 - 홀수 찾아 삼만리
    solutions_to_add[202] = [
        {
            "language": "python",
            "code": '''# 백준 30786: 홀수 찾아 삼만리
# 모든 여행지를 방문하며 총 이동거리가 홀수가 되도록
import sys
input = sys.stdin.readline

n = int(input())
coords = []
for i in range(n):
    x, y = map(int, input().split())
    coords.append((x, y, i + 1))  # 1-indexed

# 두 점 사이 거리: |x1-x2| + |y1-y2|
# 거리의 홀짝은 (x1+y1) % 2 XOR (x2+y2) % 2로 결정

# 각 점을 짝수/홀수로 분류 (x+y의 홀짝)
even = []  # x+y가 짝수
odd = []   # x+y가 홀수

for x, y, idx in coords:
    if (x + y) % 2 == 0:
        even.append(idx)
    else:
        odd.append(idx)

# 총 이동거리가 홀수가 되려면
# 짝수->홀수 또는 홀수->짝수 이동이 홀수 번이어야 함

# n개 점을 모두 방문, n-1번 이동
# 홀/짝 변환 횟수가 홀수이면 총 거리가 홀수

# 방법: even을 모두 방문하고 odd를 모두 방문하면
# 변환 횟수 = 1 (짝수끼리 + 홀수끼리 = 0 + 1(전환) + 0)

if len(even) == 0 or len(odd) == 0:
    # 모든 점이 같은 종류: 항상 짝수 거리
    print("NO")
else:
    print("YES")
    # 짝수 점들 먼저, 그 다음 홀수 점들 (또는 반대)
    # 총 전환 횟수가 1번이면 홀수
    result = even + odd
    print(' '.join(map(str, result)))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        List<Integer> even = new ArrayList<>();
        List<Integer> odd = new ArrayList<>();

        for (int i = 1; i <= n; i++) {
            int x = sc.nextInt();
            int y = sc.nextInt();
            if ((x + y) % 2 == 0) even.add(i);
            else odd.add(i);
        }

        if (even.isEmpty() || odd.isEmpty()) {
            System.out.println("NO");
        } else {
            System.out.println("YES");
            StringBuilder sb = new StringBuilder();
            for (int i : even) sb.append(i).append(" ");
            for (int i : odd) sb.append(i).append(" ");
            System.out.println(sb.toString().trim());
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> even, odd;

    for (int i = 1; i <= n; i++) {
        int x, y;
        cin >> x >> y;
        if ((x + y) % 2 == 0) even.push_back(i);
        else odd.push_back(i);
    }

    if (even.empty() || odd.empty()) {
        cout << "NO" << endl;
    } else {
        cout << "YES" << endl;
        for (int i : even) cout << i << " ";
        for (int i : odd) cout << i << " ";
        cout << endl;
    }

    return 0;
}
'''
        }
    ]

    # 문제 203: 30047 - 함수 문자열
    solutions_to_add[203] = [
        {
            "language": "python",
            "code": '''# 백준 30047: 함수 문자열
# x는 0, g(S)는 S+1, f(S,T)는 min(S,T)
import sys
sys.setrecursionlimit(10**6)

s = input().strip()
idx = 0

def parse():
    global idx
    if idx >= len(s):
        return None

    c = s[idx]

    if c == 'x':
        idx += 1
        return 0
    elif c == 'g':
        idx += 1
        val = parse()
        if val is None:
            return None
        return val + 1
    elif c == 'f':
        idx += 1
        val1 = parse()
        if val1 is None:
            return None
        val2 = parse()
        if val2 is None:
            return None
        return min(val1, val2)
    else:
        return None

result = parse()

if result is None or idx != len(s):
    print(-1)
else:
    print(result)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    static String s;
    static int idx = 0;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        s = sc.nextLine();

        Integer result = parse();

        if (result == null || idx != s.length()) {
            System.out.println(-1);
        } else {
            System.out.println(result);
        }
    }

    static Integer parse() {
        if (idx >= s.length()) return null;

        char c = s.charAt(idx);

        if (c == 'x') {
            idx++;
            return 0;
        } else if (c == 'g') {
            idx++;
            Integer val = parse();
            if (val == null) return null;
            return val + 1;
        } else if (c == 'f') {
            idx++;
            Integer val1 = parse();
            if (val1 == null) return null;
            Integer val2 = parse();
            if (val2 == null) return null;
            return Math.min(val1, val2);
        } else {
            return null;
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
using namespace std;

string s;
int idx = 0;

int parse(bool& valid) {
    if (idx >= s.length()) {
        valid = false;
        return -1;
    }

    char c = s[idx];

    if (c == 'x') {
        idx++;
        return 0;
    } else if (c == 'g') {
        idx++;
        int val = parse(valid);
        if (!valid) return -1;
        return val + 1;
    } else if (c == 'f') {
        idx++;
        int val1 = parse(valid);
        if (!valid) return -1;
        int val2 = parse(valid);
        if (!valid) return -1;
        return min(val1, val2);
    } else {
        valid = false;
        return -1;
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> s;

    bool valid = true;
    int result = parse(valid);

    if (!valid || idx != s.length()) {
        cout << -1 << endl;
    } else {
        cout << result << endl;
    }

    return 0;
}
'''
        }
    ]

    # 문제 204: 10527 - Judging Troubles
    solutions_to_add[204] = [
        {
            "language": "python",
            "code": '''# 백준 10527: Judging Troubles
# 두 시스템에서 같은 결과가 최대 몇 개인지
from collections import Counter
import sys
input = sys.stdin.readline

n = int(input())

dom = []
for _ in range(n):
    dom.append(input().strip())

kat = []
for _ in range(n):
    kat.append(input().strip())

dom_count = Counter(dom)
kat_count = Counter(kat)

# 같은 결과의 최대 매칭
result = 0
for key in dom_count:
    if key in kat_count:
        result += min(dom_count[key], kat_count[key])

print(result)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        sc.nextLine();

        Map<String, Integer> dom = new HashMap<>();
        Map<String, Integer> kat = new HashMap<>();

        for (int i = 0; i < n; i++) {
            String s = sc.nextLine();
            dom.put(s, dom.getOrDefault(s, 0) + 1);
        }

        for (int i = 0; i < n; i++) {
            String s = sc.nextLine();
            kat.put(s, kat.getOrDefault(s, 0) + 1);
        }

        int result = 0;
        for (String key : dom.keySet()) {
            if (kat.containsKey(key)) {
                result += Math.min(dom.get(key), kat.get(key));
            }
        }

        System.out.println(result);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <map>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    map<string, int> dom, kat;

    for (int i = 0; i < n; i++) {
        string s;
        cin >> s;
        dom[s]++;
    }

    for (int i = 0; i < n; i++) {
        string s;
        cin >> s;
        kat[s]++;
    }

    int result = 0;
    for (auto& p : dom) {
        if (kat.count(p.first)) {
            result += min(p.second, kat[p.first]);
        }
    }

    cout << result << endl;

    return 0;
}
'''
        }
    ]

    # 문제 205: 14233 - 악덕 사장
    solutions_to_add[205] = [
        {
            "language": "python",
            "code": '''# 백준 14233: 악덕 사장
# 모든 일을 k시간씩 하면서 마감을 지키는 최대 k
import sys
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))

# 정렬 후 i번째 일을 i*k 시간에 끝내야 함
# a[i] >= i*k -> k <= a[i]/i (i는 1-indexed)

a.sort()

min_k = float('inf')
for i in range(n):
    k = a[i] // (i + 1)
    min_k = min(min_k, k)

print(min_k)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        long[] a = new long[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextLong();

        Arrays.sort(a);

        long minK = Long.MAX_VALUE;
        for (int i = 0; i < n; i++) {
            long k = a[i] / (i + 1);
            minK = Math.min(minK, k);
        }

        System.out.println(minK);
    }
}
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

    int n;
    cin >> n;

    long long a[n];
    for (int i = 0; i < n; i++) cin >> a[i];

    sort(a, a + n);

    long long minK = 1e18;
    for (int i = 0; i < n; i++) {
        long long k = a[i] / (i + 1);
        minK = min(minK, k);
    }

    cout << minK << endl;

    return 0;
}
'''
        }
    ]

    # 문제 206: 7774 - 콘센트
    solutions_to_add[206] = [
        {
            "language": "python",
            "code": '''# 백준 7774: 콘센트
# A 콘센트 1개로 시작, A->B 멀티탭과 B->A 멀티탭을 번갈아 사용
import sys
input = sys.stdin.readline

line = input().split()
n, m = int(line[0]), int(line[1])

a = []
b = []

if n > 0:
    a = list(map(int, input().split()))
if m > 0:
    b = list(map(int, input().split()))

# 내림차순 정렬 (큰 멀티탭 먼저 사용)
a.sort(reverse=True)
b.sort(reverse=True)

# 시뮬레이션
# A 콘센트 개수, B 콘센트 개수
a_count = 1
b_count = 0
a_idx = 0
b_idx = 0

while True:
    # A 콘센트에 A->B 멀티탭 꽂기
    # a_count개의 A 콘센트에 멀티탭 꽂음
    new_b = 0
    for _ in range(a_count):
        if a_idx < n:
            new_b += a[a_idx]
            a_idx += 1
    if new_b == 0:
        break
    b_count = new_b

    # B 콘센트에 B->A 멀티탭 꽂기
    new_a = 0
    for _ in range(b_count):
        if b_idx < m:
            new_a += b[b_idx]
            b_idx += 1
    if new_a == 0:
        break
    a_count = new_a

# 최종 A 콘센트 개수
print(a_count)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();

        Integer[] a = new Integer[n];
        Integer[] b = new Integer[m];

        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        for (int i = 0; i < m; i++) b[i] = sc.nextInt();

        Arrays.sort(a, Collections.reverseOrder());
        Arrays.sort(b, Collections.reverseOrder());

        long aCount = 1, bCount = 0;
        int aIdx = 0, bIdx = 0;

        while (true) {
            long newB = 0;
            for (long i = 0; i < aCount && aIdx < n; i++) {
                newB += a[aIdx++];
            }
            if (newB == 0) break;
            bCount = newB;

            long newA = 0;
            for (long i = 0; i < bCount && bIdx < m; i++) {
                newA += b[bIdx++];
            }
            if (newA == 0) break;
            aCount = newA;
        }

        System.out.println(aCount);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <algorithm>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<int> a(n), b(m);
    for (int i = 0; i < n; i++) cin >> a[i];
    for (int i = 0; i < m; i++) cin >> b[i];

    sort(a.rbegin(), a.rend());
    sort(b.rbegin(), b.rend());

    long long aCount = 1, bCount = 0;
    int aIdx = 0, bIdx = 0;

    while (true) {
        long long newB = 0;
        for (long long i = 0; i < aCount && aIdx < n; i++) {
            newB += a[aIdx++];
        }
        if (newB == 0) break;
        bCount = newB;

        long long newA = 0;
        for (long long i = 0; i < bCount && bIdx < m; i++) {
            newA += b[bIdx++];
        }
        if (newA == 0) break;
        aCount = newA;
    }

    cout << aCount << endl;

    return 0;
}
'''
        }
    ]

    # 문제 207: 10751 - COW
    solutions_to_add[207] = [
        {
            "language": "python",
            "code": '''# 백준 10751: COW
# COW가 부분 수열로 몇 번 등장하는지
import sys
input = sys.stdin.readline

n = int(input())
s = input().strip()

# dp로 계산
# c_count: C의 개수
# co_count: CO의 개수
# cow_count: COW의 개수

c_count = 0
co_count = 0
cow_count = 0

for ch in s:
    if ch == 'C':
        c_count += 1
    elif ch == 'O':
        co_count += c_count
    elif ch == 'W':
        cow_count += co_count

print(cow_count)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        String s = sc.next();

        long cCount = 0, coCount = 0, cowCount = 0;

        for (char ch : s.toCharArray()) {
            if (ch == 'C') cCount++;
            else if (ch == 'O') coCount += cCount;
            else if (ch == 'W') cowCount += coCount;
        }

        System.out.println(cowCount);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    string s;
    cin >> n >> s;

    long long cCount = 0, coCount = 0, cowCount = 0;

    for (char ch : s) {
        if (ch == 'C') cCount++;
        else if (ch == 'O') coCount += cCount;
        else if (ch == 'W') cowCount += coCount;
    }

    cout << cowCount << endl;

    return 0;
}
'''
        }
    ]

    # 문제 208: 32194 - 질문은 계속돼
    solutions_to_add[208] = [
        {
            "language": "python",
            "code": '''# 백준 32194: 질문은 계속돼
# 첫 번째 질문의 답은 "예"
# 이후 질문은 이전 답을 기반으로 결정
import sys
input = sys.stdin.readline

n = int(input())

# 각 질문의 답 저장 (1-indexed)
answers = [None] * (n + 2)
answers[1] = True  # 첫 번째 답은 "예"

for i in range(2, n + 2):
    parts = input().split()
    qtype = int(parts[0])
    x = int(parts[1])
    y = int(parts[2])

    if qtype == 1:
        # x~y 모두 "예"인가?
        all_yes = all(answers[j] for j in range(x, y + 1))
        answers[i] = all_yes
    else:
        # x~y 모두 "아니오"인가?
        all_no = all(not answers[j] for j in range(x, y + 1))
        answers[i] = all_no

    print("Yes" if answers[i] else "No")
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        boolean[] answers = new boolean[n + 2];
        answers[1] = true;

        StringBuilder sb = new StringBuilder();

        for (int i = 2; i <= n + 1; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int type = Integer.parseInt(st.nextToken());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());

            if (type == 1) {
                boolean allYes = true;
                for (int j = x; j <= y; j++) {
                    if (!answers[j]) { allYes = false; break; }
                }
                answers[i] = allYes;
            } else {
                boolean allNo = true;
                for (int j = x; j <= y; j++) {
                    if (answers[j]) { allNo = false; break; }
                }
                answers[i] = allNo;
            }

            sb.append(answers[i] ? "Yes" : "No").append("\\n");
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

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    bool answers[n + 2];
    answers[1] = true;

    for (int i = 2; i <= n + 1; i++) {
        int type, x, y;
        cin >> type >> x >> y;

        if (type == 1) {
            bool allYes = true;
            for (int j = x; j <= y; j++) {
                if (!answers[j]) { allYes = false; break; }
            }
            answers[i] = allYes;
        } else {
            bool allNo = true;
            for (int j = x; j <= y; j++) {
                if (answers[j]) { allNo = false; break; }
            }
            answers[i] = allNo;
        }

        cout << (answers[i] ? "Yes" : "No") << "\\n";
    }

    return 0;
}
'''
        }
    ]

    # 문제 209: 18882 - Cowntact Tracing
    solutions_to_add[209] = [
        {
            "language": "python",
            "code": '''# 백준 18882: Cowntact Tracing
# patient zero 후보 수, K의 최소/최대값
import sys
input = sys.stdin.readline

line = input().split()
n, t = int(line[0]), int(line[1])
infected = input().strip()

events = []
for _ in range(t):
    parts = input().split()
    time = int(parts[0])
    x = int(parts[1]) - 1
    y = int(parts[2]) - 1
    events.append((time, x, y))

events.sort()

def simulate(patient_zero, k):
    """patient_zero에서 시작해 k번 전파할 때 감염 상태"""
    inf = [False] * n
    inf[patient_zero] = True
    count = [0] * n  # 각 소의 악수 횟수

    for time, x, y in events:
        spread = False
        if inf[x] and count[x] < k:
            if not inf[y]:
                inf[y] = True
            count[x] += 1
            spread = True
        if inf[y] and count[y] < k:
            if not inf[x]:
                inf[x] = True
            count[y] += 1
            spread = True

    # 감염 상태 비교
    result = ''.join('1' if inf[i] else '0' for i in range(n))
    return result == infected

# patient zero 후보 찾기
candidates = []
for pz in range(n):
    if infected[pz] == '0':
        continue

    # 이 소가 patient zero일 때 가능한 K 범위 찾기
    min_k = None
    max_k = None

    for k in range(251):  # 충분히 큰 범위
        if simulate(pz, k):
            if min_k is None:
                min_k = k
            max_k = k

    if min_k is not None:
        candidates.append((pz, min_k, max_k))

# 결과 출력
num_pz = len(candidates)
overall_min_k = min(c[1] for c in candidates) if candidates else 0
overall_max_k = max(c[2] for c in candidates) if candidates else 0

if overall_max_k >= 250:
    print(num_pz, overall_min_k, "Infinity")
else:
    print(num_pz, overall_min_k, overall_max_k)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    static int n, t;
    static String infected;
    static int[][] events;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();
        t = sc.nextInt();
        infected = sc.next();

        events = new int[t][3];
        for (int i = 0; i < t; i++) {
            events[i][0] = sc.nextInt();
            events[i][1] = sc.nextInt() - 1;
            events[i][2] = sc.nextInt() - 1;
        }

        Arrays.sort(events, (a, b) -> a[0] - b[0]);

        List<int[]> candidates = new ArrayList<>();
        for (int pz = 0; pz < n; pz++) {
            if (infected.charAt(pz) == '0') continue;

            int minK = -1, maxK = -1;
            for (int k = 0; k <= 250; k++) {
                if (simulate(pz, k)) {
                    if (minK == -1) minK = k;
                    maxK = k;
                }
            }
            if (minK != -1) candidates.add(new int[]{pz, minK, maxK});
        }

        int numPz = candidates.size();
        int overallMinK = Integer.MAX_VALUE;
        int overallMaxK = 0;
        for (int[] c : candidates) {
            overallMinK = Math.min(overallMinK, c[1]);
            overallMaxK = Math.max(overallMaxK, c[2]);
        }

        if (overallMaxK >= 250) {
            System.out.println(numPz + " " + overallMinK + " Infinity");
        } else {
            System.out.println(numPz + " " + overallMinK + " " + overallMaxK);
        }
    }

    static boolean simulate(int patientZero, int k) {
        boolean[] inf = new boolean[n];
        inf[patientZero] = true;
        int[] count = new int[n];

        for (int[] e : events) {
            int x = e[1], y = e[2];
            if (inf[x] && count[x] < k) {
                inf[y] = true;
                count[x]++;
            }
            if (inf[y] && count[y] < k) {
                inf[x] = true;
                count[y]++;
            }
        }

        for (int i = 0; i < n; i++) {
            if ((infected.charAt(i) == '1') != inf[i]) return false;
        }
        return true;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

int n, t;
string infected;
vector<tuple<int,int,int>> events;

bool simulate(int pz, int k) {
    vector<bool> inf(n, false);
    inf[pz] = true;
    vector<int> cnt(n, 0);

    for (auto& e : events) {
        int x = get<1>(e), y = get<2>(e);
        if (inf[x] && cnt[x] < k) {
            inf[y] = true;
            cnt[x]++;
        }
        if (inf[y] && cnt[y] < k) {
            inf[x] = true;
            cnt[y]++;
        }
    }

    for (int i = 0; i < n; i++) {
        if ((infected[i] == '1') != inf[i]) return false;
    }
    return true;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> t >> infected;

    for (int i = 0; i < t; i++) {
        int ti, x, y;
        cin >> ti >> x >> y;
        events.push_back({ti, x-1, y-1});
    }

    sort(events.begin(), events.end());

    vector<tuple<int,int,int>> candidates;
    for (int pz = 0; pz < n; pz++) {
        if (infected[pz] == '0') continue;

        int minK = -1, maxK = -1;
        for (int k = 0; k <= 250; k++) {
            if (simulate(pz, k)) {
                if (minK == -1) minK = k;
                maxK = k;
            }
        }
        if (minK != -1) candidates.push_back({pz, minK, maxK});
    }

    int numPz = candidates.size();
    int overallMinK = 1e9, overallMaxK = 0;
    for (auto& c : candidates) {
        overallMinK = min(overallMinK, get<1>(c));
        overallMaxK = max(overallMaxK, get<2>(c));
    }

    if (overallMaxK >= 250) {
        cout << numPz << " " << overallMinK << " Infinity" << endl;
    } else {
        cout << numPz << " " << overallMinK << " " << overallMaxK << endl;
    }

    return 0;
}
'''
        }
    ]

    # 솔루션 적용
    updated_count = 0
    for list_idx in range(200, 210):
        if list_idx >= len(empty_medium):
            break

        original_idx = empty_medium[list_idx]['original_index']
        problem = problems[original_idx]

        if list_idx in solutions_to_add:
            problems[original_idx]['solutions'] = solutions_to_add[list_idx]
            updated_count += 1
            print(f"문제 {list_idx} (원본 인덱스 {original_idx}) 솔루션 추가: {problem.get('name')}")

    # 파일에 저장
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(problems, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\n총 {updated_count}개의 문제에 솔루션 추가 완료 (200-209)")

if __name__ == "__main__":
    main()
