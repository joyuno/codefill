#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medium 난이도 문제 180-209에 대한 솔루션 생성 스크립트
"""

import json
import fcntl

# JSON 파일 경로
JSON_FILE = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

def main():
    # JSON 파일 읽기
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        problems = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # medium 난이도이면서 solutions가 비어있고 input_output이 있는 문제 찾기
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
    print("\n인덱스 180-209의 문제들:")

    # 각 문제에 대한 솔루션 생성
    solutions_to_add = {}

    # 문제 180: 9214 - 첫 번째 항
    solutions_to_add[180] = [
        {
            "language": "python",
            "code": '''# 백준 9214: 첫 번째 항
# 주어진 수열에서 이전 항을 찾아 첫 번째 항을 구하는 문제

import sys
input = sys.stdin.readline

def get_next(s):
    """현재 항에서 다음 항을 만드는 함수"""
    if not s:
        return ""
    result = []
    i = 0
    while i < len(s):
        digit = s[i]
        count = 1
        while i + count < len(s) and s[i + count] == digit:
            count += 1
        result.append(str(count) + digit)
        i += count
    return ''.join(result)

def get_prev(s):
    """현재 항에서 이전 항을 찾는 함수"""
    if len(s) % 2 != 0:
        return None
    result = []
    i = 0
    while i < len(s):
        count = int(s[i])
        digit = s[i + 1]
        if count == 0:
            return None
        result.append(digit * count)
        i += 2
    prev = ''.join(result)
    # 검증: 이전 항에서 다음 항을 만들면 현재 항과 같아야 함
    if get_next(prev) != s:
        return None
    return prev

test_num = 0
while True:
    line = input().strip()
    if line == '0':
        break
    test_num += 1
    current = line

    # 자기 자신이 이전 항인 경우 체크 (22처럼)
    prev = get_prev(current)
    while prev is not None and prev != current:
        current = prev
        prev = get_prev(current)

    print(f"Test {test_num}: {current}")
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int testNum = 0;

        while (sc.hasNextLine()) {
            String line = sc.nextLine().trim();
            if (line.equals("0")) break;

            testNum++;
            String current = line;

            // 이전 항을 계속 찾아가기
            String prev = getPrev(current);
            while (prev != null && !prev.equals(current)) {
                current = prev;
                prev = getPrev(current);
            }

            System.out.println("Test " + testNum + ": " + current);
        }
    }

    // 다음 항 생성
    static String getNext(String s) {
        if (s.isEmpty()) return "";
        StringBuilder result = new StringBuilder();
        int i = 0;
        while (i < s.length()) {
            char digit = s.charAt(i);
            int count = 1;
            while (i + count < s.length() && s.charAt(i + count) == digit) {
                count++;
            }
            result.append(count).append(digit);
            i += count;
        }
        return result.toString();
    }

    // 이전 항 찾기
    static String getPrev(String s) {
        if (s.length() % 2 != 0) return null;
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < s.length(); i += 2) {
            int count = s.charAt(i) - '0';
            char digit = s.charAt(i + 1);
            if (count == 0) return null;
            for (int j = 0; j < count; j++) {
                result.append(digit);
            }
        }
        String prev = result.toString();
        // 검증
        if (!getNext(prev).equals(s)) return null;
        return prev;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
using namespace std;

// 다음 항 생성
string getNext(const string& s) {
    if (s.empty()) return "";
    string result;
    int i = 0;
    while (i < (int)s.length()) {
        char digit = s[i];
        int count = 1;
        while (i + count < (int)s.length() && s[i + count] == digit) {
            count++;
        }
        result += to_string(count) + digit;
        i += count;
    }
    return result;
}

// 이전 항 찾기
string getPrev(const string& s) {
    if (s.length() % 2 != 0) return "";
    string result;
    for (int i = 0; i < (int)s.length(); i += 2) {
        int count = s[i] - '0';
        char digit = s[i + 1];
        if (count == 0) return "";
        for (int j = 0; j < count; j++) {
            result += digit;
        }
    }
    // 검증
    if (getNext(result) != s) return "";
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string line;
    int testNum = 0;

    while (getline(cin, line)) {
        if (line == "0") break;
        testNum++;
        string current = line;

        string prev = getPrev(current);
        while (!prev.empty() && prev != current) {
            current = prev;
            prev = getPrev(current);
        }

        cout << "Test " << testNum << ": " << current << endl;
    }

    return 0;
}
'''
        }
    ]

    # 문제 181: 2853 - 배
    solutions_to_add[181] = [
        {
            "language": "python",
            "code": '''# 백준 2853: 배
# 배들이 주기적으로 방문하는 날이 주어졌을 때, 최소 배의 수를 구하는 문제
import sys
from math import gcd
input = sys.stdin.readline

n = int(input())
days = []
for _ in range(n):
    days.append(int(input()))

# 모든 날에서 1을 뺀 값들 (배가 방문하는 날 - 첫째날)
diffs = set()
for day in days:
    diffs.add(day - 1)
diffs.discard(0)

if not diffs:
    print(1)
else:
    # 모든 차이값의 GCD를 구함
    g = 0
    for d in diffs:
        g = gcd(g, d)

    # g의 약수들이 가능한 주기
    divisors = []
    i = 1
    while i * i <= g:
        if g % i == 0:
            divisors.append(i)
            if i != g // i:
                divisors.append(g // i)
        i += 1
    divisors.sort(reverse=True)

    # 그리디하게 가장 큰 주기부터 선택
    covered = set([1])
    diffs_set = set(days)
    count = 0

    for period in divisors:
        covers = set()
        day = 1
        while day <= max(days):
            covers.add(day)
            day += period

        uncovered = diffs_set - covered
        if uncovered & covers:
            covered |= covers
            count += 1

        if covered >= diffs_set:
            break

    print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] days = new int[n];
        for (int i = 0; i < n; i++) {
            days[i] = sc.nextInt();
        }

        int g = 0;
        for (int day : days) {
            g = gcd(g, day - 1);
        }

        if (g == 0) {
            System.out.println(1);
            return;
        }

        List<Integer> divisors = new ArrayList<>();
        for (int i = 1; i * i <= g; i++) {
            if (g % i == 0) {
                divisors.add(i);
                if (i != g / i) divisors.add(g / i);
            }
        }
        Collections.sort(divisors, Collections.reverseOrder());

        Set<Integer> daysSet = new HashSet<>();
        for (int d : days) daysSet.add(d);

        Set<Integer> covered = new HashSet<>();
        covered.add(1);
        int maxDay = days[n - 1];
        int count = 0;

        for (int period : divisors) {
            Set<Integer> covers = new HashSet<>();
            for (int day = 1; day <= maxDay; day += period) covers.add(day);

            boolean needed = false;
            for (int d : daysSet) {
                if (!covered.contains(d) && covers.contains(d)) {
                    needed = true;
                    break;
                }
            }

            if (needed) {
                covered.addAll(covers);
                count++;
            }

            if (covered.containsAll(daysSet)) break;
        }

        System.out.println(count);
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
#include <vector>
#include <set>
#include <algorithm>
using namespace std;

int gcd(int a, int b) { return b == 0 ? a : gcd(b, a % b); }

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    vector<int> days(n);
    for (int i = 0; i < n; i++) cin >> days[i];

    int g = 0;
    for (int d : days) g = gcd(g, d - 1);

    if (g == 0) {
        cout << 1 << endl;
        return 0;
    }

    vector<int> divisors;
    for (int i = 1; i * i <= g; i++) {
        if (g % i == 0) {
            divisors.push_back(i);
            if (i != g / i) divisors.push_back(g / i);
        }
    }
    sort(divisors.rbegin(), divisors.rend());

    set<int> daysSet(days.begin(), days.end());
    set<int> covered;
    covered.insert(1);
    int maxDay = days[n - 1], count = 0;

    for (int period : divisors) {
        set<int> covers;
        for (int d = 1; d <= maxDay; d += period) covers.insert(d);

        bool needed = false;
        for (int d : daysSet) {
            if (!covered.count(d) && covers.count(d)) { needed = true; break; }
        }

        if (needed) {
            for (int d : covers) covered.insert(d);
            count++;
        }

        bool all = true;
        for (int d : daysSet) if (!covered.count(d)) { all = false; break; }
        if (all) break;
    }

    cout << count << endl;
    return 0;
}
'''
        }
    ]

    # 문제 182: 24938 - 키트 분배하기
    solutions_to_add[182] = [
        {
            "language": "python",
            "code": '''# 백준 24938: 키트 분배하기
# 인접한 방끼리만 키트를 주고받아 모든 방의 키트 수를 같게 만드는 최소 혼잡도
import sys
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))

total = sum(a)
target = total // n

# 왼쪽에서 오른쪽으로 누적 초과/부족분 계산
result = 0
prefix = 0

for i in range(n - 1):
    prefix += a[i] - target
    result += abs(prefix)

print(result)
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
        StringTokenizer st = new StringTokenizer(br.readLine());

        long[] a = new long[n];
        long total = 0;
        for (int i = 0; i < n; i++) {
            a[i] = Long.parseLong(st.nextToken());
            total += a[i];
        }

        long target = total / n;
        long result = 0, prefix = 0;

        for (int i = 0; i < n - 1; i++) {
            prefix += a[i] - target;
            result += Math.abs(prefix);
        }

        System.out.println(result);
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

    int n;
    cin >> n;

    long long a[n], total = 0;
    for (int i = 0; i < n; i++) {
        cin >> a[i];
        total += a[i];
    }

    long long target = total / n;
    long long result = 0, prefix = 0;

    for (int i = 0; i < n - 1; i++) {
        prefix += a[i] - target;
        result += abs(prefix);
    }

    cout << result << endl;
    return 0;
}
'''
        }
    ]

    # 문제 183: 2892 - 심심한 준규
    solutions_to_add[183] = [
        {
            "language": "python",
            "code": '''# 백준 2892: 심심한 준규
# OTP 암호화에서 온점과 공백의 위치를 찾는 문제
import sys
input = sys.stdin.readline

n = int(input())
encrypted = list(map(lambda x: int(x, 16), input().split()))

result = []
for enc in encrypted:
    is_letter = False
    # key가 '0'-'9'일 때 XOR 결과가 영소문자인지 확인
    for key in range(0x30, 0x3A):
        original = enc ^ key
        if 0x61 <= original <= 0x7A:
            is_letter = True
            break
    result.append('-' if is_letter else '.')

print(''.join(result))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        StringBuilder result = new StringBuilder();
        for (int i = 0; i < n; i++) {
            int enc = Integer.parseInt(sc.next(), 16);
            boolean isLetter = false;
            for (int key = 0x30; key <= 0x39; key++) {
                int original = enc ^ key;
                if (original >= 0x61 && original <= 0x7A) {
                    isLetter = true;
                    break;
                }
            }
            result.append(isLetter ? '-' : '.');
        }
        System.out.println(result);
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
    cin >> n;

    string result;
    for (int i = 0; i < n; i++) {
        int enc;
        cin >> hex >> enc;

        bool isLetter = false;
        for (int key = 0x30; key <= 0x39; key++) {
            int original = enc ^ key;
            if (original >= 0x61 && original <= 0x7A) {
                isLetter = true;
                break;
            }
        }
        result += isLetter ? '-' : '.';
    }

    cout << result << endl;
    return 0;
}
'''
        }
    ]

    # 문제 184: 14531 - Bovine Genomics (Bronze)
    solutions_to_add[184] = [
        {
            "language": "python",
            "code": '''# 백준 14531: Bovine Genomics (Bronze)
# 각 위치에서 spotty cow와 plain cow를 완벽히 구분할 수 있는 위치의 수
import sys
input = sys.stdin.readline

n, m = map(int, input().split())

spotty = [input().strip() for _ in range(n)]
plain = [input().strip() for _ in range(n)]

count = 0
for pos in range(m):
    spotty_chars = set(g[pos] for g in spotty)
    plain_chars = set(g[pos] for g in plain)
    if len(spotty_chars & plain_chars) == 0:
        count += 1

print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        String[] spotty = new String[n];
        String[] plain = new String[n];

        for (int i = 0; i < n; i++) spotty[i] = br.readLine().trim();
        for (int i = 0; i < n; i++) plain[i] = br.readLine().trim();

        int count = 0;
        for (int pos = 0; pos < m; pos++) {
            Set<Character> sc = new HashSet<>(), pc = new HashSet<>();
            for (int i = 0; i < n; i++) {
                sc.add(spotty[i].charAt(pos));
                pc.add(plain[i].charAt(pos));
            }
            boolean overlap = false;
            for (char c : sc) if (pc.contains(c)) { overlap = true; break; }
            if (!overlap) count++;
        }

        System.out.println(count);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    string spotty[n], plain[n];
    for (int i = 0; i < n; i++) cin >> spotty[i];
    for (int i = 0; i < n; i++) cin >> plain[i];

    int count = 0;
    for (int pos = 0; pos < m; pos++) {
        set<char> sc, pc;
        for (int i = 0; i < n; i++) {
            sc.insert(spotty[i][pos]);
            pc.insert(plain[i][pos]);
        }
        bool overlap = false;
        for (char c : sc) if (pc.count(c)) { overlap = true; break; }
        if (!overlap) count++;
    }

    cout << count << endl;
    return 0;
}
'''
        }
    ]

    # 문제 185: 3709 - Laserbox
    solutions_to_add[185] = [
        {
            "language": "python",
            "code": '''# 백준 3709: Laserbox
# 레이저가 right-turner를 만나면 90도 오른쪽으로 꺾임
import sys
input = sys.stdin.readline

t = int(input())
dx = [0, 1, 0, -1]  # 북, 동, 남, 서
dy = [1, 0, -1, 0]

for _ in range(t):
    line = input().split()
    n, r = int(line[0]), int(line[1])

    turners = set()
    for _ in range(r):
        x, y = map(int, input().split())
        turners.add((x, y))

    lx, ly = map(int, input().split())

    if ly == 0: direction = 0
    elif ly == n + 1: direction = 2
    elif lx == 0: direction = 1
    else: direction = 3

    x, y = lx, ly
    visited = set()

    while True:
        x += dx[direction]
        y += dy[direction]

        if x < 1 or x > n or y < 1 or y > n:
            if x < 1: print(0, y)
            elif x > n: print(n + 1, y)
            elif y < 1: print(x, 0)
            else: print(x, n + 1)
            break

        state = (x, y, direction)
        if state in visited:
            print(0, 0)
            break
        visited.add(state)

        if (x, y) in turners:
            direction = (direction + 1) % 4
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int t = sc.nextInt();
        int[] dx = {0, 1, 0, -1}, dy = {1, 0, -1, 0};

        while (t-- > 0) {
            int n = sc.nextInt(), r = sc.nextInt();
            Set<Long> turners = new HashSet<>();
            for (int i = 0; i < r; i++) {
                int x = sc.nextInt(), y = sc.nextInt();
                turners.add((long)x * 100 + y);
            }

            int lx = sc.nextInt(), ly = sc.nextInt();
            int dir;
            if (ly == 0) dir = 0;
            else if (ly == n + 1) dir = 2;
            else if (lx == 0) dir = 1;
            else dir = 3;

            int x = lx, y = ly;
            Set<Long> visited = new HashSet<>();

            while (true) {
                x += dx[dir]; y += dy[dir];

                if (x < 1 || x > n || y < 1 || y > n) {
                    if (x < 1) System.out.println(0 + " " + y);
                    else if (x > n) System.out.println((n+1) + " " + y);
                    else if (y < 1) System.out.println(x + " " + 0);
                    else System.out.println(x + " " + (n+1));
                    break;
                }

                long state = (long)x * 10000 + y * 10 + dir;
                if (visited.contains(state)) { System.out.println("0 0"); break; }
                visited.add(state);

                if (turners.contains((long)x * 100 + y)) dir = (dir + 1) % 4;
            }
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;
    int dx[] = {0, 1, 0, -1}, dy[] = {1, 0, -1, 0};

    while (t--) {
        int n, r;
        cin >> n >> r;

        set<pair<int,int>> turners;
        for (int i = 0; i < r; i++) {
            int x, y;
            cin >> x >> y;
            turners.insert({x, y});
        }

        int lx, ly;
        cin >> lx >> ly;

        int dir;
        if (ly == 0) dir = 0;
        else if (ly == n + 1) dir = 2;
        else if (lx == 0) dir = 1;
        else dir = 3;

        int x = lx, y = ly;
        set<tuple<int,int,int>> visited;

        while (true) {
            x += dx[dir]; y += dy[dir];

            if (x < 1 || x > n || y < 1 || y > n) {
                if (x < 1) cout << 0 << " " << y << endl;
                else if (x > n) cout << n + 1 << " " << y << endl;
                else if (y < 1) cout << x << " " << 0 << endl;
                else cout << x << " " << n + 1 << endl;
                break;
            }

            auto state = make_tuple(x, y, dir);
            if (visited.count(state)) { cout << "0 0" << endl; break; }
            visited.insert(state);

            if (turners.count({x, y})) dir = (dir + 1) % 4;
        }
    }
    return 0;
}
'''
        }
    ]

    # 문제 186: 32753 - 네 또 수열입니다
    solutions_to_add[186] = [
        {
            "language": "python",
            "code": '''# 백준 32753: 네 또 수열입니다
# 조건: 모든 i (1 <= i < N*K)에 대해 A[1]+...+A[i] = i
import sys
input = sys.stdin.readline

n, k = map(int, input().split())

# 누적합 S[i] = i이므로 A[i] = 1 for all i
# 따라서 N = 1인 경우만 가능

if n == 1:
    print(' '.join(['1'] * k))
else:
    print(-1)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt(), k = sc.nextInt();

        if (n == 1) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < k; i++) {
                if (i > 0) sb.append(" ");
                sb.append(1);
            }
            System.out.println(sb);
        } else {
            System.out.println(-1);
        }
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

    int n, k;
    cin >> n >> k;

    if (n == 1) {
        for (int i = 0; i < k; i++) {
            if (i > 0) cout << " ";
            cout << 1;
        }
        cout << endl;
    } else {
        cout << -1 << endl;
    }
    return 0;
}
'''
        }
    ]

    # 문제 187: 34042 - 천상도
    solutions_to_add[187] = [
        {
            "language": "python",
            "code": '''# 백준 34042: 천상도
# N개의 수 중 1개 이상을 선택해서 곱했을 때 최대값
import sys
input = sys.stdin.readline

n, m = map(int, input().split())

for _ in range(m):
    nums = list(map(int, input().split()))

    cnt_2 = nums.count(2)
    cnt_m2 = nums.count(-2)
    cnt_1 = nums.count(1)
    cnt_m1 = nums.count(-1)
    cnt_0 = nums.count(0)

    # 최대 양수 곱
    positive_power = cnt_2
    if cnt_m2 % 2 == 0:
        positive_power += cnt_m2
    else:
        positive_power += cnt_m2 - 1

    if positive_power > 0:
        result = 2 ** positive_power
    elif cnt_1 > 0:
        result = 1
    elif cnt_0 > 0:
        result = 0
    elif cnt_m1 > 0:
        result = -1
    else:
        result = -2

    print(result)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        StringBuilder sb = new StringBuilder();
        for (int q = 0; q < m; q++) {
            st = new StringTokenizer(br.readLine());
            int cnt2 = 0, cntM2 = 0, cnt1 = 0, cntM1 = 0, cnt0 = 0;

            for (int i = 0; i < n; i++) {
                int x = Integer.parseInt(st.nextToken());
                if (x == 2) cnt2++;
                else if (x == -2) cntM2++;
                else if (x == 1) cnt1++;
                else if (x == -1) cntM1++;
                else cnt0++;
            }

            int posPower = cnt2 + (cntM2 % 2 == 0 ? cntM2 : cntM2 - 1);

            long result;
            if (posPower > 0) result = 1L << posPower;
            else if (cnt1 > 0) result = 1;
            else if (cnt0 > 0) result = 0;
            else if (cntM1 > 0) result = -1;
            else result = -2;

            sb.append(result).append("\\n");
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

    int n, m;
    cin >> n >> m;

    while (m--) {
        int cnt2 = 0, cntM2 = 0, cnt1 = 0, cntM1 = 0, cnt0 = 0;

        for (int i = 0; i < n; i++) {
            int x;
            cin >> x;
            if (x == 2) cnt2++;
            else if (x == -2) cntM2++;
            else if (x == 1) cnt1++;
            else if (x == -1) cntM1++;
            else cnt0++;
        }

        int posPower = cnt2 + (cntM2 % 2 == 0 ? cntM2 : cntM2 - 1);

        long long result;
        if (posPower > 0) result = 1LL << posPower;
        else if (cnt1 > 0) result = 1;
        else if (cnt0 > 0) result = 0;
        else if (cntM1 > 0) result = -1;
        else result = -2;

        cout << result << "\\n";
    }
    return 0;
}
'''
        }
    ]

    # 문제 188: 18270 - Livestock Lineup
    solutions_to_add[188] = [
        {
            "language": "python",
            "code": '''# 백준 18270: Livestock Lineup
# 8마리 소의 순서를 정하는 문제 (제약조건에 맞게)
from itertools import permutations
import sys
input = sys.stdin.readline

cows = ["Beatrice", "Belinda", "Bella", "Bessie", "Betsy", "Blue", "Buttercup", "Sue"]

n = int(input())
constraints = []
for _ in range(n):
    line = input().strip()
    parts = line.split()
    constraints.append((parts[0], parts[5]))

def check(order):
    pos = {cow: i for i, cow in enumerate(order)}
    for x, y in constraints:
        if abs(pos[x] - pos[y]) != 1:
            return False
    return True

for perm in permutations(sorted(cows)):
    if check(perm):
        for cow in perm:
            print(cow)
        break
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    static String[] cows = {"Beatrice", "Belinda", "Bella", "Bessie", "Betsy", "Blue", "Buttercup", "Sue"};
    static List<String[]> constraints = new ArrayList<>();

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = Integer.parseInt(sc.nextLine());

        for (int i = 0; i < n; i++) {
            String[] parts = sc.nextLine().split(" ");
            constraints.add(new String[]{parts[0], parts[5]});
        }

        Arrays.sort(cows);
        do {
            if (check()) {
                for (String cow : cows) System.out.println(cow);
                break;
            }
        } while (nextPerm());
    }

    static boolean check() {
        Map<String, Integer> pos = new HashMap<>();
        for (int i = 0; i < 8; i++) pos.put(cows[i], i);
        for (String[] c : constraints) {
            if (Math.abs(pos.get(c[0]) - pos.get(c[1])) != 1) return false;
        }
        return true;
    }

    static boolean nextPerm() {
        int i = 6;
        while (i >= 0 && cows[i].compareTo(cows[i+1]) >= 0) i--;
        if (i < 0) return false;
        int j = 7;
        while (cows[i].compareTo(cows[j]) >= 0) j--;
        String t = cows[i]; cows[i] = cows[j]; cows[j] = t;
        for (int l = i+1, r = 7; l < r; l++, r--) {
            t = cows[l]; cows[l] = cows[r]; cows[r] = t;
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
#include <map>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    vector<string> cows = {"Beatrice", "Belinda", "Bella", "Bessie", "Betsy", "Blue", "Buttercup", "Sue"};
    sort(cows.begin(), cows.end());

    int n;
    cin >> n;
    cin.ignore();

    vector<pair<string, string>> constraints;
    for (int i = 0; i < n; i++) {
        string line;
        getline(cin, line);
        int p1 = line.find(' ');
        string x = line.substr(0, p1);
        int p2 = line.rfind(' ');
        string y = line.substr(p2 + 1);
        constraints.push_back({x, y});
    }

    do {
        map<string, int> pos;
        for (int i = 0; i < 8; i++) pos[cows[i]] = i;

        bool valid = true;
        for (auto& c : constraints) {
            if (abs(pos[c.first] - pos[c.second]) != 1) { valid = false; break; }
        }

        if (valid) {
            for (auto& cow : cows) cout << cow << "\\n";
            break;
        }
    } while (next_permutation(cows.begin(), cows.end()));

    return 0;
}
'''
        }
    ]

    # 문제 189: 26111 - Parentheses Tree
    solutions_to_add[189] = [
        {
            "language": "python",
            "code": '''# 백준 26111: Parentheses Tree
# 괄호 문자열로 표현된 트리에서 루트부터 모든 리프까지의 거리 합
import sys
input = sys.stdin.readline

s = input().strip()

total = 0
depth = 0
i = 0

while i < len(s):
    if s[i] == '(':
        depth += 1
        if i + 1 < len(s) and s[i + 1] == ')':
            total += depth
            i += 2
        else:
            i += 1
    else:
        depth -= 1
        i += 1

print(total)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine().trim();

        long total = 0;
        int depth = 0, i = 0;

        while (i < s.length()) {
            if (s.charAt(i) == '(') {
                depth++;
                if (i + 1 < s.length() && s.charAt(i + 1) == ')') {
                    total += depth;
                    i += 2;
                } else {
                    i++;
                }
            } else {
                depth--;
                i++;
            }
        }

        System.out.println(total);
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

    string s;
    cin >> s;

    long long total = 0;
    int depth = 0, i = 0;

    while (i < (int)s.length()) {
        if (s[i] == '(') {
            depth++;
            if (i + 1 < (int)s.length() && s[i + 1] == ')') {
                total += depth;
                i += 2;
            } else {
                i++;
            }
        } else {
            depth--;
            i++;
        }
    }

    cout << total << endl;
    return 0;
}
'''
        }
    ]

    # 문제 190-199 솔루션 추가
    # 문제 190: 21868 - 미적분학 입문하기
    solutions_to_add[190] = [
        {
            "language": "python",
            "code": '''# 백준 21868: 미적분학 입문하기
import sys
from math import gcd
input = sys.stdin.readline

p, q = map(int, input().split())  # epsilon = p/q
a, b = map(int, input().split())  # f(x) = ax + b
x0 = int(input())

L = a * x0 + b
print(L)

if a == 0:
    print("0 0")
else:
    num = p
    den = q * abs(a)
    g = gcd(num, den)
    num //= g
    den //= g

    if num <= 10**8 and den <= 10**8:
        print(num, den)
    else:
        print("0 0")
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long p = sc.nextLong(), q = sc.nextLong();
        long a = sc.nextLong(), b = sc.nextLong();
        long x0 = sc.nextLong();

        System.out.println(a * x0 + b);

        if (a == 0) {
            System.out.println("0 0");
        } else {
            long num = p, den = q * Math.abs(a);
            long g = gcd(num, den);
            num /= g; den /= g;

            if (num <= 100000000L && den <= 100000000L) {
                System.out.println(num + " " + den);
            } else {
                System.out.println("0 0");
            }
        }
    }

    static long gcd(long a, long b) { return b == 0 ? a : gcd(b, a % b); }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

long long gcd(long long a, long long b) { return b == 0 ? a : gcd(b, a % b); }

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long p, q, a, b, x0;
    cin >> p >> q >> a >> b >> x0;

    cout << a * x0 + b << endl;

    if (a == 0) {
        cout << "0 0" << endl;
    } else {
        long long num = p, den = q * (a < 0 ? -a : a);
        long long g = gcd(num, den);
        num /= g; den /= g;

        if (num <= 100000000LL && den <= 100000000LL) {
            cout << num << " " << den << endl;
        } else {
            cout << "0 0" << endl;
        }
    }
    return 0;
}
'''
        }
    ]

    # 문제 191: 31845 - 카드 교환
    solutions_to_add[191] = [
        {
            "language": "python",
            "code": '''# 백준 31845: 카드 교환
# 양수 점수 카드만 최대한 많이 선택
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
a = list(map(int, input().split()))

# 양수인 점수들만 내림차순 정렬 후 최대 m개 선택
positive = sorted([x for x in a if x > 0], reverse=True)
result = sum(positive[:m])
print(result)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt(), m = sc.nextInt();

        List<Integer> positive = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();
            if (x > 0) positive.add(x);
        }

        Collections.sort(positive, Collections.reverseOrder());

        long result = 0;
        for (int i = 0; i < Math.min(m, positive.size()); i++) {
            result += positive.get(i);
        }

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
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<int> positive;
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        if (x > 0) positive.push_back(x);
    }

    sort(positive.rbegin(), positive.rend());

    long long result = 0;
    for (int i = 0; i < min(m, (int)positive.size()); i++) {
        result += positive[i];
    }

    cout << result << endl;
    return 0;
}
'''
        }
    ]

    # 문제 192: 15705 - 단어 찾기
    solutions_to_add[192] = [
        {
            "language": "python",
            "code": '''# 백준 15705: 단어 찾기
# 8방향으로 단어 찾기
import sys
input = sys.stdin.readline

s = input().strip()
n, m = map(int, input().split())
board = [input().strip() for _ in range(n)]

# 8방향
dx = [-1, -1, -1, 0, 0, 1, 1, 1]
dy = [-1, 0, 1, -1, 1, -1, 0, 1]

def check(x, y, d):
    for i, c in enumerate(s):
        nx, ny = x + dx[d] * i, y + dy[d] * i
        if nx < 0 or nx >= n or ny < 0 or ny >= m:
            return False
        if board[nx][ny] != c:
            return False
    return True

found = False
for i in range(n):
    for j in range(m):
        if board[i][j] == s[0]:
            for d in range(8):
                if check(i, j, d):
                    found = True
                    break
        if found:
            break
    if found:
        break

print(1 if found else 0)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    static int[] dx = {-1, -1, -1, 0, 0, 1, 1, 1};
    static int[] dy = {-1, 0, 1, -1, 1, -1, 0, 1};
    static int n, m;
    static String s;
    static String[] board;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        s = sc.nextLine();
        n = sc.nextInt(); m = sc.nextInt(); sc.nextLine();
        board = new String[n];
        for (int i = 0; i < n; i++) board[i] = sc.nextLine();

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (board[i].charAt(j) == s.charAt(0)) {
                    for (int d = 0; d < 8; d++) {
                        if (check(i, j, d)) {
                            System.out.println(1);
                            return;
                        }
                    }
                }
            }
        }
        System.out.println(0);
    }

    static boolean check(int x, int y, int d) {
        for (int i = 0; i < s.length(); i++) {
            int nx = x + dx[d] * i, ny = y + dy[d] * i;
            if (nx < 0 || nx >= n || ny < 0 || ny >= m) return false;
            if (board[nx].charAt(ny) != s.charAt(i)) return false;
        }
        return true;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
using namespace std;

int dx[] = {-1, -1, -1, 0, 0, 1, 1, 1};
int dy[] = {-1, 0, 1, -1, 1, -1, 0, 1};
int n, m;
string s, board[105];

bool check(int x, int y, int d) {
    for (int i = 0; i < (int)s.length(); i++) {
        int nx = x + dx[d] * i, ny = y + dy[d] * i;
        if (nx < 0 || nx >= n || ny < 0 || ny >= m) return false;
        if (board[nx][ny] != s[i]) return false;
    }
    return true;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> s >> n >> m;
    for (int i = 0; i < n; i++) cin >> board[i];

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (board[i][j] == s[0]) {
                for (int d = 0; d < 8; d++) {
                    if (check(i, j, d)) {
                        cout << 1 << endl;
                        return 0;
                    }
                }
            }
        }
    }
    cout << 0 << endl;
    return 0;
}
'''
        }
    ]

    # 문제 193: 17041 - Measuring Traffic
    solutions_to_add[193] = [
        {
            "language": "python",
            "code": '''# 백준 17041: Measuring Traffic
# 고속도로 교통량 측정
import sys
input = sys.stdin.readline

n = int(input())
sensors = []
for _ in range(n):
    parts = input().split()
    sensor_type = parts[0]
    low = int(parts[1])
    high = int(parts[2])
    sensors.append((sensor_type, low, high))

# 시작 교통량 범위
start_low, start_high = 0, 10**9

# 앞에서부터 역으로 계산
flow_low, flow_high = 0, 10**9
for i in range(n):
    sensor_type, low, high = sensors[i]
    if sensor_type == "none":
        flow_low = max(flow_low, low)
        flow_high = min(flow_high, high)
    elif sensor_type == "on":
        flow_low += low
        flow_high += high
    else:  # off
        flow_low -= high
        flow_high -= low
        flow_low = max(0, flow_low)

start_low, start_high = flow_low, flow_high

# 끝 교통량 범위
flow_low, flow_high = 0, 10**9
for i in range(n - 1, -1, -1):
    sensor_type, low, high = sensors[i]
    if sensor_type == "none":
        flow_low = max(flow_low, low)
        flow_high = min(flow_high, high)
    elif sensor_type == "on":
        flow_low -= high
        flow_high -= low
        flow_low = max(0, flow_low)
    else:  # off
        flow_low += low
        flow_high += high

end_low, end_high = flow_low, flow_high

print(start_low, start_high)
print(end_low, end_high)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        String[] types = new String[n];
        int[] lows = new int[n], highs = new int[n];

        for (int i = 0; i < n; i++) {
            types[i] = sc.next();
            lows[i] = sc.nextInt();
            highs[i] = sc.nextInt();
        }

        // 시작 교통량
        long flowL = 0, flowH = 1000000000;
        for (int i = 0; i < n; i++) {
            if (types[i].equals("none")) {
                flowL = Math.max(flowL, lows[i]);
                flowH = Math.min(flowH, highs[i]);
            } else if (types[i].equals("on")) {
                flowL += lows[i];
                flowH += highs[i];
            } else {
                flowL -= highs[i];
                flowH -= lows[i];
                flowL = Math.max(0, flowL);
            }
        }
        System.out.println(flowL + " " + flowH);

        // 끝 교통량
        flowL = 0; flowH = 1000000000;
        for (int i = n - 1; i >= 0; i--) {
            if (types[i].equals("none")) {
                flowL = Math.max(flowL, lows[i]);
                flowH = Math.min(flowH, highs[i]);
            } else if (types[i].equals("on")) {
                flowL -= highs[i];
                flowH -= lows[i];
                flowL = Math.max(0, flowL);
            } else {
                flowL += lows[i];
                flowH += highs[i];
            }
        }
        System.out.println(flowL + " " + flowH);
    }
}
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
    cin >> n;

    string types[n];
    long long lows[n], highs[n];

    for (int i = 0; i < n; i++) {
        cin >> types[i] >> lows[i] >> highs[i];
    }

    // 시작 교통량
    long long flowL = 0, flowH = 1e9;
    for (int i = 0; i < n; i++) {
        if (types[i] == "none") {
            flowL = max(flowL, lows[i]);
            flowH = min(flowH, highs[i]);
        } else if (types[i] == "on") {
            flowL += lows[i];
            flowH += highs[i];
        } else {
            flowL -= highs[i];
            flowH -= lows[i];
            flowL = max(0LL, flowL);
        }
    }
    cout << flowL << " " << flowH << "\\n";

    // 끝 교통량
    flowL = 0; flowH = 1e9;
    for (int i = n - 1; i >= 0; i--) {
        if (types[i] == "none") {
            flowL = max(flowL, lows[i]);
            flowH = min(flowH, highs[i]);
        } else if (types[i] == "on") {
            flowL -= highs[i];
            flowH -= lows[i];
            flowL = max(0LL, flowL);
        } else {
            flowL += lows[i];
            flowH += highs[i];
        }
    }
    cout << flowL << " " << flowH << "\\n";

    return 0;
}
'''
        }
    ]

    # 문제 194: 31924 - 현대모비스 특별상의 주인공은? 2
    solutions_to_add[194] = [
        {
            "language": "python",
            "code": '''# 백준 31924: 현대모비스 특별상의 주인공은? 2
# MOBIS를 8방향으로 찾기
import sys
input = sys.stdin.readline

n = int(input())
grid = [input().strip() for _ in range(n)]

dx = [-1, -1, -1, 0, 0, 1, 1, 1]
dy = [-1, 0, 1, -1, 1, -1, 0, 1]
target = "MOBIS"

count = 0
for i in range(n):
    for j in range(n):
        if grid[i][j] == 'M':
            for d in range(8):
                found = True
                for k in range(5):
                    ni, nj = i + dx[d] * k, j + dy[d] * k
                    if ni < 0 or ni >= n or nj < 0 or nj >= n:
                        found = False
                        break
                    if grid[ni][nj] != target[k]:
                        found = False
                        break
                if found:
                    count += 1

print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt(); sc.nextLine();
        String[] grid = new String[n];
        for (int i = 0; i < n; i++) grid[i] = sc.nextLine();

        int[] dx = {-1, -1, -1, 0, 0, 1, 1, 1};
        int[] dy = {-1, 0, 1, -1, 1, -1, 0, 1};
        String target = "MOBIS";

        int count = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i].charAt(j) == 'M') {
                    for (int d = 0; d < 8; d++) {
                        boolean found = true;
                        for (int k = 0; k < 5; k++) {
                            int ni = i + dx[d] * k, nj = j + dy[d] * k;
                            if (ni < 0 || ni >= n || nj < 0 || nj >= n || grid[ni].charAt(nj) != target.charAt(k)) {
                                found = false;
                                break;
                            }
                        }
                        if (found) count++;
                    }
                }
            }
        }
        System.out.println(count);
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
    cin >> n;
    string grid[n];
    for (int i = 0; i < n; i++) cin >> grid[i];

    int dx[] = {-1, -1, -1, 0, 0, 1, 1, 1};
    int dy[] = {-1, 0, 1, -1, 1, -1, 0, 1};
    string target = "MOBIS";

    int count = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (grid[i][j] == 'M') {
                for (int d = 0; d < 8; d++) {
                    bool found = true;
                    for (int k = 0; k < 5; k++) {
                        int ni = i + dx[d] * k, nj = j + dy[d] * k;
                        if (ni < 0 || ni >= n || nj < 0 || nj >= n || grid[ni][nj] != target[k]) {
                            found = false;
                            break;
                        }
                    }
                    if (found) count++;
                }
            }
        }
    }
    cout << count << endl;
    return 0;
}
'''
        }
    ]

    # 문제 195: 33573 - 대칭제곱수
    solutions_to_add[195] = [
        {
            "language": "python",
            "code": '''# 백준 33573: 대칭제곱수
# 제곱수이면서 뒤집어도 제곱수인지 확인
import sys
import math
input = sys.stdin.readline

def is_perfect_square(n):
    if n < 0:
        return False
    root = int(math.isqrt(n))
    return root * root == n

t = int(input())
for _ in range(t):
    n = int(input())

    # n이 제곱수인지 확인
    if not is_perfect_square(n):
        print("NO")
        continue

    # n을 뒤집기
    rev = int(str(n)[::-1])

    # 뒤집은 수도 제곱수인지 확인
    if is_perfect_square(rev):
        print("YES")
    else:
        print("NO")
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        while (t-- > 0) {
            long n = Long.parseLong(br.readLine().trim());

            if (!isPerfectSquare(n)) {
                sb.append("NO\\n");
                continue;
            }

            long rev = Long.parseLong(new StringBuilder(String.valueOf(n)).reverse().toString());

            if (isPerfectSquare(rev)) {
                sb.append("YES\\n");
            } else {
                sb.append("NO\\n");
            }
        }
        System.out.print(sb);
    }

    static boolean isPerfectSquare(long n) {
        if (n < 0) return false;
        long root = (long)Math.sqrt(n);
        if (root * root == n) return true;
        if ((root + 1) * (root + 1) == n) return true;
        return false;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
#include <algorithm>
#include <cmath>
using namespace std;

bool isPerfectSquare(long long n) {
    if (n < 0) return false;
    long long root = sqrt(n);
    if (root * root == n) return true;
    if ((root + 1) * (root + 1) == n) return true;
    return false;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        long long n;
        cin >> n;

        if (!isPerfectSquare(n)) {
            cout << "NO\\n";
            continue;
        }

        string s = to_string(n);
        reverse(s.begin(), s.end());
        long long rev = stoll(s);

        if (isPerfectSquare(rev)) {
            cout << "YES\\n";
        } else {
            cout << "NO\\n";
        }
    }

    return 0;
}
'''
        }
    ]

    # 문제 196: 26090 - 완전한 수열
    solutions_to_add[196] = [
        {
            "language": "python",
            "code": '''# 백준 26090: 완전한 수열
# 길이가 소수이고 합도 소수인 연속 부분 수열의 개수
import sys
input = sys.stdin.readline

def sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return is_prime

n = int(input())
a = list(map(int, input().split()))

# 에라토스테네스의 체
max_sum = n * 2000
is_prime = sieve(max(n, max_sum))

# 소수인 길이들
prime_lengths = [p for p in range(2, n + 1) if is_prime[p]]

# 누적합
prefix = [0] * (n + 1)
for i in range(n):
    prefix[i + 1] = prefix[i] + a[i]

count = 0
for length in prime_lengths:
    for i in range(n - length + 1):
        total = prefix[i + length] - prefix[i]
        if total > 1 and total <= max_sum and is_prime[total]:
            count += 1

print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();

        int maxSum = n * 2000;
        boolean[] isPrime = sieve(Math.max(n, maxSum));

        long[] prefix = new long[n + 1];
        for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + a[i];

        int count = 0;
        for (int len = 2; len <= n; len++) {
            if (!isPrime[len]) continue;
            for (int i = 0; i + len <= n; i++) {
                long sum = prefix[i + len] - prefix[i];
                if (sum > 1 && sum <= maxSum && isPrime[(int)sum]) count++;
            }
        }

        System.out.println(count);
    }

    static boolean[] sieve(int n) {
        boolean[] isPrime = new boolean[n + 1];
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;
        for (int i = 2; i * i <= n; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j <= n; j += i) isPrime[j] = false;
            }
        }
        return isPrime;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
using namespace std;

vector<bool> sieve(int n) {
    vector<bool> isPrime(n + 1, true);
    isPrime[0] = isPrime[1] = false;
    for (int i = 2; i * i <= n; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j <= n; j += i) isPrime[j] = false;
        }
    }
    return isPrime;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    vector<int> a(n);
    for (int i = 0; i < n; i++) cin >> a[i];

    int maxSum = n * 2000;
    vector<bool> isPrime = sieve(max(n, maxSum));

    vector<long long> prefix(n + 1);
    for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + a[i];

    int count = 0;
    for (int len = 2; len <= n; len++) {
        if (!isPrime[len]) continue;
        for (int i = 0; i + len <= n; i++) {
            long long sum = prefix[i + len] - prefix[i];
            if (sum > 1 && sum <= maxSum && isPrime[sum]) count++;
        }
    }

    cout << count << endl;
    return 0;
}
'''
        }
    ]

    # 나머지 문제들도 추가 (197-209)
    # 문제 197: 30427 - Reveals
    solutions_to_add[197] = [
        {
            "language": "python",
            "code": '''# 백준 30427: Reveals
# 케이크를 먹은 범인 찾기
import sys
input = sys.stdin.readline

# 첫 줄 (swi's cake is missing!)
input()

n = int(input())
people = []
for _ in range(n):
    people.append(input().strip())

m = int(input())
witnesses = set()
for _ in range(m):
    witnesses.add(input().strip())

# 규칙에 따라 범인 찾기

# 1. dongho가 집에 있으면 범인
if "dongho" in people:
    print("dongho")
    exit()

# 목격되지 않은 사람들
unseen = [p for p in people if p not in witnesses]

# 2. 목격되지 않은 사람이 한 명이면 범인
if len(unseen) == 1:
    print(unseen[0])
    exit()

# 3. 목격되지 않은 bumin이 있으면 범인
if "bumin" in unseen:
    print("bumin")
    exit()

# 4. 목격되지 않은 cake가 있으면 범인
if "cake" in unseen:
    print("cake")
    exit()

# 5. 목격되지 않은 lawyer가 있으면 범인
if "lawyer" in unseen:
    print("lawyer")
    exit()

# 6. 목격되지 않은 사람 중 사전순 가장 빠른 사람
unseen.sort()
print(unseen[0])
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        sc.nextLine(); // swi's cake is missing!

        int n = Integer.parseInt(sc.nextLine());
        Set<String> peopleSet = new HashSet<>();
        List<String> people = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            String p = sc.nextLine();
            people.add(p);
            peopleSet.add(p);
        }

        int m = Integer.parseInt(sc.nextLine());
        Set<String> witnesses = new HashSet<>();
        for (int i = 0; i < m; i++) {
            witnesses.add(sc.nextLine());
        }

        // 1. dongho
        if (peopleSet.contains("dongho")) {
            System.out.println("dongho");
            return;
        }

        List<String> unseen = new ArrayList<>();
        for (String p : people) {
            if (!witnesses.contains(p)) unseen.add(p);
        }

        // 2. 한 명
        if (unseen.size() == 1) {
            System.out.println(unseen.get(0));
            return;
        }

        Set<String> unseenSet = new HashSet<>(unseen);

        // 3. bumin
        if (unseenSet.contains("bumin")) {
            System.out.println("bumin");
            return;
        }

        // 4. cake
        if (unseenSet.contains("cake")) {
            System.out.println("cake");
            return;
        }

        // 5. lawyer
        if (unseenSet.contains("lawyer")) {
            System.out.println("lawyer");
            return;
        }

        // 6. 사전순
        Collections.sort(unseen);
        System.out.println(unseen.get(0));
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string line;
    getline(cin, line); // swi's cake is missing!

    int n;
    cin >> n;
    cin.ignore();

    vector<string> people(n);
    set<string> peopleSet;
    for (int i = 0; i < n; i++) {
        getline(cin, people[i]);
        peopleSet.insert(people[i]);
    }

    int m;
    cin >> m;
    cin.ignore();

    set<string> witnesses;
    for (int i = 0; i < m; i++) {
        getline(cin, line);
        witnesses.insert(line);
    }

    // 1. dongho
    if (peopleSet.count("dongho")) {
        cout << "dongho" << endl;
        return 0;
    }

    vector<string> unseen;
    for (auto& p : people) {
        if (!witnesses.count(p)) unseen.push_back(p);
    }

    // 2. 한 명
    if (unseen.size() == 1) {
        cout << unseen[0] << endl;
        return 0;
    }

    set<string> unseenSet(unseen.begin(), unseen.end());

    // 3. bumin
    if (unseenSet.count("bumin")) { cout << "bumin" << endl; return 0; }

    // 4. cake
    if (unseenSet.count("cake")) { cout << "cake" << endl; return 0; }

    // 5. lawyer
    if (unseenSet.count("lawyer")) { cout << "lawyer" << endl; return 0; }

    // 6. 사전순
    sort(unseen.begin(), unseen.end());
    cout << unseen[0] << endl;
    return 0;
}
'''
        }
    ]

    # 문제 198: 20493 - 세상은 하나의 손수건
    solutions_to_add[198] = [
        {
            "language": "python",
            "code": '''# 백준 20493: 세상은 하나의 손수건
# 좌표평면에서 방향 전환하며 이동
import sys
input = sys.stdin.readline

n, t = map(int, input().split())

# 방향: 0=동, 1=북, 2=서, 3=남
dx = [1, 0, -1, 0]
dy = [0, 1, 0, -1]

x, y = 0, 0
direction = 0  # 시작: x축 양방향 (동쪽)
prev_time = 0

for _ in range(n):
    parts = input().split()
    curr_time = int(parts[0])
    turn = parts[1]

    # prev_time ~ curr_time 동안 이동
    elapsed = curr_time - prev_time
    x += dx[direction] * elapsed
    y += dy[direction] * elapsed

    # 방향 전환
    if turn == "left":
        direction = (direction + 1) % 4
    else:  # right
        direction = (direction + 3) % 4

    prev_time = curr_time

# 마지막 구간
elapsed = t - prev_time
x += dx[direction] * elapsed
y += dy[direction] * elapsed

print(x, y)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        long t = sc.nextLong();

        int[] dx = {1, 0, -1, 0};
        int[] dy = {0, 1, 0, -1};

        long x = 0, y = 0;
        int dir = 0;
        long prev = 0;

        for (int i = 0; i < n; i++) {
            long curr = sc.nextLong();
            String turn = sc.next();

            long elapsed = curr - prev;
            x += dx[dir] * elapsed;
            y += dy[dir] * elapsed;

            if (turn.equals("left")) dir = (dir + 1) % 4;
            else dir = (dir + 3) % 4;

            prev = curr;
        }

        long elapsed = t - prev;
        x += dx[dir] * elapsed;
        y += dy[dir] * elapsed;

        System.out.println(x + " " + y);
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
    long long t;
    cin >> n >> t;

    int dx[] = {1, 0, -1, 0};
    int dy[] = {0, 1, 0, -1};

    long long x = 0, y = 0;
    int dir = 0;
    long long prev = 0;

    for (int i = 0; i < n; i++) {
        long long curr;
        string turn;
        cin >> curr >> turn;

        long long elapsed = curr - prev;
        x += dx[dir] * elapsed;
        y += dy[dir] * elapsed;

        if (turn == "left") dir = (dir + 1) % 4;
        else dir = (dir + 3) % 4;

        prev = curr;
    }

    long long elapsed = t - prev;
    x += dx[dir] * elapsed;
    y += dy[dir] * elapsed;

    cout << x << " " << y << endl;
    return 0;
}
'''
        }
    ]

    # 문제 199: 31785 - 시소 배열
    solutions_to_add[199] = [
        {
            "language": "python",
            "code": '''# 백준 31785: 시소 배열
import sys
input = sys.stdin.readline

q = int(input())
arr = []

for _ in range(q):
    query = input().split()
    if query[0] == '1':
        x = int(query[1])
        arr.append(x)
    else:  # query[0] == '2'
        n = len(arr)
        half = n // 2

        left_sum = sum(arr[:half])
        right_sum = sum(arr[half:])

        if left_sum <= right_sum:
            print(left_sum)
            arr = arr[half:]
        else:
            print(right_sum)
            arr = arr[:half]

# 최종 배열 출력
print(' '.join(map(str, arr)))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int q = Integer.parseInt(br.readLine().trim());

        List<Long> arr = new ArrayList<>();
        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < q; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int type = Integer.parseInt(st.nextToken());

            if (type == 1) {
                long x = Long.parseLong(st.nextToken());
                arr.add(x);
            } else {
                int n = arr.size();
                int half = n / 2;

                long leftSum = 0, rightSum = 0;
                for (int j = 0; j < half; j++) leftSum += arr.get(j);
                for (int j = half; j < n; j++) rightSum += arr.get(j);

                if (leftSum <= rightSum) {
                    sb.append(leftSum).append("\\n");
                    arr = new ArrayList<>(arr.subList(half, n));
                } else {
                    sb.append(rightSum).append("\\n");
                    arr = new ArrayList<>(arr.subList(0, half));
                }
            }
        }

        for (int i = 0; i < arr.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(arr.get(i));
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

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int q;
    cin >> q;

    vector<long long> arr;

    while (q--) {
        int type;
        cin >> type;

        if (type == 1) {
            long long x;
            cin >> x;
            arr.push_back(x);
        } else {
            int n = arr.size();
            int half = n / 2;

            long long leftSum = 0, rightSum = 0;
            for (int i = 0; i < half; i++) leftSum += arr[i];
            for (int i = half; i < n; i++) rightSum += arr[i];

            if (leftSum <= rightSum) {
                cout << leftSum << "\\n";
                arr = vector<long long>(arr.begin() + half, arr.end());
            } else {
                cout << rightSum << "\\n";
                arr = vector<long long>(arr.begin(), arr.begin() + half);
            }
        }
    }

    for (int i = 0; i < (int)arr.size(); i++) {
        if (i > 0) cout << " ";
        cout << arr[i];
    }
    cout << endl;

    return 0;
}
'''
        }
    ]

    # 문제 200-209도 추가
    # 문제 200: 16923 - 다음 다양한 단어
    solutions_to_add[200] = [
        {
            "language": "python",
            "code": '''# 백준 16923: 다음 다양한 단어
# 사전순으로 다음 다양한 단어 찾기
import sys

s = input().strip()
n = len(s)

# 현재 사용된 문자
used = set(s)

# 마지막 문자 뒤에 아직 사용되지 않은 가장 작은 문자 추가
for c in 'abcdefghijklmnopqrstuvwxyz':
    if c not in used:
        print(s + c)
        exit()

# 모든 문자가 사용된 경우, 마지막 문자부터 교체 시도
for i in range(n - 1, -1, -1):
    # i번째 문자보다 큰 문자 중 사용되지 않은 가장 작은 문자 찾기
    removed = s[i]
    # i번째 이후 문자들을 제거하면 사용 가능해지는 문자들
    available = set()
    for j in range(i, n):
        available.add(s[j])

    # i-1까지 사용된 문자
    used_before = set(s[:i])

    for c in 'abcdefghijklmnopqrstuvwxyz':
        if c > s[i] and (c not in used_before):
            # s[:i] + c가 답
            print(s[:i] + c)
            exit()

print(-1)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        int n = s.length();

        Set<Character> used = new HashSet<>();
        for (char c : s.toCharArray()) used.add(c);

        // 끝에 문자 추가
        for (char c = 'a'; c <= 'z'; c++) {
            if (!used.contains(c)) {
                System.out.println(s + c);
                return;
            }
        }

        // 마지막부터 교체
        for (int i = n - 1; i >= 0; i--) {
            Set<Character> usedBefore = new HashSet<>();
            for (int j = 0; j < i; j++) usedBefore.add(s.charAt(j));

            for (char c = (char)(s.charAt(i) + 1); c <= 'z'; c++) {
                if (!usedBefore.contains(c)) {
                    System.out.println(s.substring(0, i) + c);
                    return;
                }
            }
        }

        System.out.println(-1);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    cin >> s;
    int n = s.length();

    set<char> used(s.begin(), s.end());

    // 끝에 문자 추가
    for (char c = 'a'; c <= 'z'; c++) {
        if (used.find(c) == used.end()) {
            cout << s + c << endl;
            return 0;
        }
    }

    // 마지막부터 교체
    for (int i = n - 1; i >= 0; i--) {
        set<char> usedBefore(s.begin(), s.begin() + i);

        for (char c = s[i] + 1; c <= 'z'; c++) {
            if (usedBefore.find(c) == usedBefore.end()) {
                cout << s.substr(0, i) + c << endl;
                return 0;
            }
        }
    }

    cout << -1 << endl;
    return 0;
}
'''
        }
    ]

    # 문제 201-209 생략하고 나중에 추가
    # 인덱스 180-199까지 먼저 처리

    # 솔루션 적용
    updated_count = 0
    for list_idx in range(180, 200):  # 180-199
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

    print(f"\n총 {updated_count}개의 문제에 솔루션 추가 완료 (180-199)")

if __name__ == "__main__":
    main()
