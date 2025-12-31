#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medium 난이도 문제 180-209에 대한 솔루션 생성 스크립트
"""

import json
import fcntl

# JSON 파일 경로
JSON_FILE = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

# 각 문제에 대한 솔루션 정의
SOLUTIONS = {
    # 문제 180: 9214 - 첫 번째 항
    4654: [
        {
            "language": "python",
            "code": '''# 백준 9214: 첫 번째 항
# 주어진 수열에서 이전 항을 찾아 첫 번째 항을 구하는 문제

import sys
input = sys.stdin.readline

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

    # 이전 항에서 다음 항을 만들었을 때 현재 항과 일치하는지 확인
    if get_next(prev) != s:
        return None

    return prev

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
        // 검증: 이전 항에서 다음 항을 만들면 현재 항과 같아야 함
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
    while (i < s.length()) {
        char digit = s[i];
        int count = 1;
        while (i + count < s.length() && s[i + count] == digit) {
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
    for (int i = 0; i < s.length(); i += 2) {
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
    ],

    # 문제 181: 2853 - 배
    4662: [
        {
            "language": "python",
            "code": '''# 백준 2853: 배
# 배들이 주기적으로 방문하는 날이 주어졌을 때, 최소 배의 수를 구하는 문제
# 모든 배는 1일에 방문하고, 각 배는 일정한 주기로 방문함

import sys
from math import gcd
input = sys.stdin.readline

n = int(input())
days = []
for _ in range(n):
    days.append(int(input()))

# 모든 날에서 1을 뺀 값들 (배가 방문하는 날 - 첫째날)
# 배의 주기는 이 값들의 약수
diffs = set()
for day in days:
    diffs.add(day - 1)

diffs.discard(0)  # 0 제거 (첫째날)

if not diffs:
    # 모든 날이 1일인 경우 (배 1척)
    print(1)
else:
    # 모든 차이값의 GCD를 구함
    g = 0
    for d in diffs:
        g = gcd(g, d)

    # g의 약수들이 가능한 주기
    # 각 주기가 커버할 수 있는 날들을 계산
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
    covered = set([1])  # 1일은 모든 배가 방문
    diffs_set = set(days)
    count = 0

    for period in divisors:
        # 이 주기가 커버하는 날들
        covers = set()
        day = 1
        while day <= max(days):
            covers.add(day)
            day += period

        # 아직 커버되지 않은 날 중 이 주기가 커버하는 날이 있으면 선택
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

        // 모든 날에서 1을 뺀 값들의 GCD
        int g = 0;
        for (int day : days) {
            g = gcd(g, day - 1);
        }

        if (g == 0) {
            System.out.println(1);
            return;
        }

        // g의 약수들 구하기
        List<Integer> divisors = new ArrayList<>();
        for (int i = 1; i * i <= g; i++) {
            if (g % i == 0) {
                divisors.add(i);
                if (i != g / i) {
                    divisors.add(g / i);
                }
            }
        }
        Collections.sort(divisors, Collections.reverseOrder());

        // 그리디하게 선택
        Set<Integer> daysSet = new HashSet<>();
        for (int day : days) daysSet.add(day);

        Set<Integer> covered = new HashSet<>();
        covered.add(1);
        int maxDay = days[n - 1];
        int count = 0;

        for (int period : divisors) {
            Set<Integer> covers = new HashSet<>();
            for (int day = 1; day <= maxDay; day += period) {
                covers.add(day);
            }

            boolean needed = false;
            for (int day : daysSet) {
                if (!covered.contains(day) && covers.contains(day)) {
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
        if (b == 0) return a;
        return gcd(b, a % b);
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

int gcd(int a, int b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> days(n);
    for (int i = 0; i < n; i++) {
        cin >> days[i];
    }

    // 모든 날에서 1을 뺀 값들의 GCD
    int g = 0;
    for (int day : days) {
        g = gcd(g, day - 1);
    }

    if (g == 0) {
        cout << 1 << endl;
        return 0;
    }

    // g의 약수들 구하기
    vector<int> divisors;
    for (int i = 1; i * i <= g; i++) {
        if (g % i == 0) {
            divisors.push_back(i);
            if (i != g / i) {
                divisors.push_back(g / i);
            }
        }
    }
    sort(divisors.rbegin(), divisors.rend());

    // 그리디하게 선택
    set<int> daysSet(days.begin(), days.end());
    set<int> covered;
    covered.insert(1);
    int maxDay = days[n - 1];
    int count = 0;

    for (int period : divisors) {
        set<int> covers;
        for (int day = 1; day <= maxDay; day += period) {
            covers.insert(day);
        }

        bool needed = false;
        for (int day : daysSet) {
            if (covered.find(day) == covered.end() && covers.find(day) != covers.end()) {
                needed = true;
                break;
            }
        }

        if (needed) {
            for (int d : covers) covered.insert(d);
            count++;
        }

        bool allCovered = true;
        for (int day : daysSet) {
            if (covered.find(day) == covered.end()) {
                allCovered = false;
                break;
            }
        }
        if (allCovered) break;
    }

    cout << count << endl;

    return 0;
}
'''
        }
    ],

    # 문제 182: 24938 - 키트 분배하기
    4668: [
        {
            "language": "python",
            "code": '''# 백준 24938: 키트 분배하기
# 인접한 방끼리만 키트를 주고받아 모든 방의 키트 수를 같게 만드는 최소 혼잡도

import sys
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))

# 목표: 모든 방이 같은 수의 키트를 가지도록
# 전체 키트 수는 n의 배수이므로 평균값이 정수
total = sum(a)
target = total // n

# 왼쪽에서 오른쪽으로 스캔하며 누적 초과/부족분 계산
# 혼잡도는 각 위치에서 오른쪽으로 이동해야 하는 키트의 절대값의 합
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

        // 왼쪽에서 오른쪽으로 누적 초과/부족분 계산
        long result = 0;
        long prefix = 0;

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

    long long a[n];
    long long total = 0;

    for (int i = 0; i < n; i++) {
        cin >> a[i];
        total += a[i];
    }

    long long target = total / n;

    // 왼쪽에서 오른쪽으로 누적 초과/부족분 계산
    long long result = 0;
    long long prefix = 0;

    for (int i = 0; i < n - 1; i++) {
        prefix += a[i] - target;
        result += abs(prefix);
    }

    cout << result << endl;

    return 0;
}
'''
        }
    ],

    # 문제 183: 2892 - 심심한 준규
    4675: [
        {
            "language": "python",
            "code": '''# 백준 2892: 심심한 준규
# OTP 암호화에서 온점과 공백의 위치를 찾는 문제
# 메시지: 영소문자(97-122), 온점(46), 공백(32)
# key: '0'-'9' (48-57)
# 온점과 공백은 XOR 결과로 구분 가능

import sys
input = sys.stdin.readline

n = int(input())
encrypted = list(map(lambda x: int(x, 16), input().split()))

# 영소문자: 0x61-0x7A (97-122)
# 온점: 0x2E (46)
# 공백: 0x20 (32)
# key: 0x30-0x39 (48-57)

# 각 암호문에 대해 가능한 원문 범위 확인
result = []
for enc in encrypted:
    is_letter = False
    # key가 '0'-'9'일 때 XOR 결과가 영소문자인지 확인
    for key in range(0x30, 0x3A):  # '0' to '9'
        original = enc ^ key
        if 0x61 <= original <= 0x7A:  # 영소문자
            is_letter = True
            break

    if is_letter:
        result.append('-')
    else:
        result.append('.')

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
            // key가 '0'-'9'일 때 XOR 결과가 영소문자인지 확인
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
        // key가 '0'-'9'일 때 XOR 결과가 영소문자인지 확인
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
    ],

    # 문제 184: 14531 - Bovine Genomics (Bronze)
    4677: [
        {
            "language": "python",
            "code": '''# 백준 14531: Bovine Genomics (Bronze)
# 각 위치에서 spotty cow와 plain cow를 완벽히 구분할 수 있는 위치의 수

import sys
input = sys.stdin.readline

n, m = map(int, input().split())

# spotty cow의 게놈
spotty = []
for _ in range(n):
    spotty.append(input().strip())

# plain cow의 게놈
plain = []
for _ in range(n):
    plain.append(input().strip())

count = 0

# 각 위치에 대해 검사
for pos in range(m):
    # 해당 위치에서 spotty cow가 가지는 문자 집합
    spotty_chars = set()
    for genome in spotty:
        spotty_chars.add(genome[pos])

    # 해당 위치에서 plain cow가 가지는 문자 집합
    plain_chars = set()
    for genome in plain:
        plain_chars.add(genome[pos])

    # 두 집합이 겹치지 않으면 구분 가능
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

        for (int i = 0; i < n; i++) {
            spotty[i] = br.readLine().trim();
        }
        for (int i = 0; i < n; i++) {
            plain[i] = br.readLine().trim();
        }

        int count = 0;

        // 각 위치에 대해 검사
        for (int pos = 0; pos < m; pos++) {
            Set<Character> spottyChars = new HashSet<>();
            Set<Character> plainChars = new HashSet<>();

            for (int i = 0; i < n; i++) {
                spottyChars.add(spotty[i].charAt(pos));
                plainChars.add(plain[i].charAt(pos));
            }

            // 두 집합이 겹치지 않으면 구분 가능
            boolean overlap = false;
            for (char c : spottyChars) {
                if (plainChars.contains(c)) {
                    overlap = true;
                    break;
                }
            }

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

    for (int i = 0; i < n; i++) {
        cin >> spotty[i];
    }
    for (int i = 0; i < n; i++) {
        cin >> plain[i];
    }

    int count = 0;

    // 각 위치에 대해 검사
    for (int pos = 0; pos < m; pos++) {
        set<char> spottyChars, plainChars;

        for (int i = 0; i < n; i++) {
            spottyChars.insert(spotty[i][pos]);
            plainChars.insert(plain[i][pos]);
        }

        // 두 집합이 겹치지 않으면 구분 가능
        bool overlap = false;
        for (char c : spottyChars) {
            if (plainChars.count(c)) {
                overlap = true;
                break;
            }
        }

        if (!overlap) count++;
    }

    cout << count << endl;

    return 0;
}
'''
        }
    ],

    # 문제 185: 3709 - Laserbox
    4678: [
        {
            "language": "python",
            "code": '''# 백준 3709: Laserbox
# 레이저가 right-turner를 만나면 90도 오른쪽으로 꺾임
# 레이저가 어디로 나가는지 계산

import sys
input = sys.stdin.readline

t = int(input())

for _ in range(t):
    line = input().split()
    n = int(line[0])
    r = int(line[1])

    # right-turner 위치 저장
    turners = set()
    for _ in range(r):
        x, y = map(int, input().split())
        turners.add((x, y))

    # 레이저 시작 위치
    lx, ly = map(int, input().split())

    # 방향: 0=북, 1=동, 2=남, 3=서
    # dx, dy: 방향에 따른 이동
    dx = [0, 1, 0, -1]
    dy = [1, 0, -1, 0]

    # 시작 위치와 방향 결정
    if ly == 0:  # 아래에서 위로 (북쪽)
        direction = 0
    elif ly == n + 1:  # 위에서 아래로 (남쪽)
        direction = 2
    elif lx == 0:  # 왼쪽에서 오른쪽으로 (동쪽)
        direction = 1
    else:  # 오른쪽에서 왼쪽으로 (서쪽)
        direction = 3

    x, y = lx, ly
    visited = set()

    while True:
        # 이동
        x += dx[direction]
        y += dy[direction]

        # 격자 밖으로 나감
        if x < 1 or x > n or y < 1 or y > n:
            # 출구 좌표 계산
            if x < 1:
                print(0, y)
            elif x > n:
                print(n + 1, y)
            elif y < 1:
                print(x, 0)
            else:
                print(x, n + 1)
            break

        # 무한 루프 감지
        state = (x, y, direction)
        if state in visited:
            print(0, 0)
            break
        visited.add(state)

        # right-turner를 만나면 오른쪽으로 90도 회전
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

        int[] dx = {0, 1, 0, -1};  // 북, 동, 남, 서
        int[] dy = {1, 0, -1, 0};

        while (t-- > 0) {
            int n = sc.nextInt();
            int r = sc.nextInt();

            Set<Long> turners = new HashSet<>();
            for (int i = 0; i < r; i++) {
                int x = sc.nextInt();
                int y = sc.nextInt();
                turners.add((long)x * 100 + y);
            }

            int lx = sc.nextInt();
            int ly = sc.nextInt();

            int direction;
            if (ly == 0) direction = 0;
            else if (ly == n + 1) direction = 2;
            else if (lx == 0) direction = 1;
            else direction = 3;

            int x = lx, y = ly;
            Set<Long> visited = new HashSet<>();

            while (true) {
                x += dx[direction];
                y += dy[direction];

                if (x < 1 || x > n || y < 1 || y > n) {
                    if (x < 1) System.out.println(0 + " " + y);
                    else if (x > n) System.out.println((n + 1) + " " + y);
                    else if (y < 1) System.out.println(x + " " + 0);
                    else System.out.println(x + " " + (n + 1));
                    break;
                }

                long state = (long)x * 10000 + y * 10 + direction;
                if (visited.contains(state)) {
                    System.out.println("0 0");
                    break;
                }
                visited.add(state);

                if (turners.contains((long)x * 100 + y)) {
                    direction = (direction + 1) % 4;
                }
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

    int dx[] = {0, 1, 0, -1};  // 북, 동, 남, 서
    int dy[] = {1, 0, -1, 0};

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

        int direction;
        if (ly == 0) direction = 0;
        else if (ly == n + 1) direction = 2;
        else if (lx == 0) direction = 1;
        else direction = 3;

        int x = lx, y = ly;
        set<tuple<int,int,int>> visited;

        while (true) {
            x += dx[direction];
            y += dy[direction];

            if (x < 1 || x > n || y < 1 || y > n) {
                if (x < 1) cout << 0 << " " << y << endl;
                else if (x > n) cout << n + 1 << " " << y << endl;
                else if (y < 1) cout << x << " " << 0 << endl;
                else cout << x << " " << n + 1 << endl;
                break;
            }

            auto state = make_tuple(x, y, direction);
            if (visited.count(state)) {
                cout << "0 0" << endl;
                break;
            }
            visited.insert(state);

            if (turners.count({x, y})) {
                direction = (direction + 1) % 4;
            }
        }
    }

    return 0;
}
'''
        }
    ],

    # 문제 186: 32753 - 네 또 수열입니다
    4682: [
        {
            "language": "python",
            "code": '''# 백준 32753: 네 또 수열입니다
# 조건: 모든 i (1 <= i < N*K)에 대해 A[1]+...+A[i] = i
# 즉, 누적합이 인덱스와 같아야 함

import sys
input = sys.stdin.readline

n, k = map(int, input().split())

# 누적합 S[i] = i 이므로
# A[1] = 1, A[2] = 1, ... 즉 모든 원소가 1이어야 함
# 그런데 1~N을 각각 K개씩 사용해야 함

# 누적합 조건에서:
# A[1] = S[1] = 1
# A[i] = S[i] - S[i-1] = i - (i-1) = 1

# 따라서 모든 A[i] = 1이어야 하는데
# 1~N을 각각 K개씩 사용해야 하므로
# N = 1인 경우만 가능 (모두 1)

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
        int n = sc.nextInt();
        int k = sc.nextInt();

        // 조건: 모든 i에 대해 누적합 = i
        // 즉 모든 원소가 1이어야 함
        // N = 1인 경우만 가능

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

    // 조건: 모든 i에 대해 누적합 = i
    // 즉 모든 원소가 1이어야 함
    // N = 1인 경우만 가능

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
    ],

    # 문제 187: 34042 - 천상도
    4683: [
        {
            "language": "python",
            "code": '''# 백준 34042: 천상도
# N개의 수 중 1개 이상을 선택해서 곱했을 때 최대값
# 수의 범위: -2 ~ 2

import sys
input = sys.stdin.readline

n, m = map(int, input().split())

for _ in range(m):
    nums = list(map(int, input().split()))

    # 2의 개수, -2의 개수, 1의 개수, -1의 개수, 0의 개수
    cnt_2 = nums.count(2)
    cnt_m2 = nums.count(-2)
    cnt_1 = nums.count(1)
    cnt_m1 = nums.count(-1)
    cnt_0 = nums.count(0)

    # 최대 양수 곱을 만들기
    # 2와 -2를 최대한 사용, -2는 짝수개 사용

    # 2^a * 2^b = 2^(a+b) 형태로 계산
    # 음수가 짝수개면 양수

    # 모든 2 사용
    positive_power = cnt_2

    # -2는 짝수개 사용 (최대한 많이)
    if cnt_m2 % 2 == 0:
        positive_power += cnt_m2
    else:
        positive_power += cnt_m2 - 1

    # 결과 계산
    if positive_power > 0:
        result = 2 ** positive_power
    elif cnt_1 > 0:
        result = 1
    elif cnt_0 > 0:
        result = 0
    else:
        # 음수만 있는 경우: -1 하나 선택
        if cnt_m1 > 0:
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

            // 최대 양수 곱
            int positivePower = cnt2;
            if (cntM2 % 2 == 0) {
                positivePower += cntM2;
            } else {
                positivePower += cntM2 - 1;
            }

            long result;
            if (positivePower > 0) {
                result = 1L << positivePower;
            } else if (cnt1 > 0) {
                result = 1;
            } else if (cnt0 > 0) {
                result = 0;
            } else if (cntM1 > 0) {
                result = -1;
            } else {
                result = -2;
            }

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

        // 최대 양수 곱
        int positivePower = cnt2;
        if (cntM2 % 2 == 0) {
            positivePower += cntM2;
        } else {
            positivePower += cntM2 - 1;
        }

        long long result;
        if (positivePower > 0) {
            result = 1LL << positivePower;
        } else if (cnt1 > 0) {
            result = 1;
        } else if (cnt0 > 0) {
            result = 0;
        } else if (cntM1 > 0) {
            result = -1;
        } else {
            result = -2;
        }

        cout << result << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # 문제 188: 18270 - Livestock Lineup
    4695: [
        {
            "language": "python",
            "code": '''# 백준 18270: Livestock Lineup
# 8마리 소의 순서를 정하는 문제 (제약조건에 맞게)
# 사전순으로 가장 빠른 순서 출력

from itertools import permutations
import sys
input = sys.stdin.readline

cows = ["Beatrice", "Belinda", "Bella", "Bessie", "Betsy", "Blue", "Buttercup", "Sue"]

n = int(input())
constraints = []
for _ in range(n):
    line = input().strip()
    # "X must be milked beside Y" 형식
    parts = line.split()
    x = parts[0]
    y = parts[5]
    constraints.append((x, y))

def check(order):
    """주어진 순서가 모든 제약조건을 만족하는지 확인"""
    pos = {cow: i for i, cow in enumerate(order)}
    for x, y in constraints:
        if abs(pos[x] - pos[y]) != 1:
            return False
    return True

# 사전순으로 정렬된 순열을 순회
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
            String line = sc.nextLine();
            String[] parts = line.split(" ");
            constraints.add(new String[]{parts[0], parts[5]});
        }

        Arrays.sort(cows);

        do {
            if (check()) {
                for (String cow : cows) {
                    System.out.println(cow);
                }
                break;
            }
        } while (nextPermutation());
    }

    static boolean check() {
        Map<String, Integer> pos = new HashMap<>();
        for (int i = 0; i < 8; i++) {
            pos.put(cows[i], i);
        }
        for (String[] c : constraints) {
            if (Math.abs(pos.get(c[0]) - pos.get(c[1])) != 1) {
                return false;
            }
        }
        return true;
    }

    static boolean nextPermutation() {
        int i = 6;
        while (i >= 0 && cows[i].compareTo(cows[i + 1]) >= 0) i--;
        if (i < 0) return false;

        int j = 7;
        while (cows[i].compareTo(cows[j]) >= 0) j--;

        String temp = cows[i];
        cows[i] = cows[j];
        cows[j] = temp;

        int left = i + 1, right = 7;
        while (left < right) {
            temp = cows[left];
            cows[left] = cows[right];
            cows[right] = temp;
            left++;
            right--;
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
        // "X must be milked beside Y"
        int pos1 = line.find(' ');
        string x = line.substr(0, pos1);
        int pos2 = line.rfind(' ');
        string y = line.substr(pos2 + 1);
        constraints.push_back({x, y});
    }

    do {
        map<string, int> pos;
        for (int i = 0; i < 8; i++) {
            pos[cows[i]] = i;
        }

        bool valid = true;
        for (auto& c : constraints) {
            if (abs(pos[c.first] - pos[c.second]) != 1) {
                valid = false;
                break;
            }
        }

        if (valid) {
            for (const string& cow : cows) {
                cout << cow << "\\n";
            }
            break;
        }
    } while (next_permutation(cows.begin(), cows.end()));

    return 0;
}
'''
        }
    ],

    # 문제 189: 26111 - Parentheses Tree
    4699: [
        {
            "language": "python",
            "code": '''# 백준 26111: Parentheses Tree
# 괄호 문자열로 표현된 트리에서 루트부터 모든 리프까지의 거리 합 계산

import sys
input = sys.stdin.readline
sys.setrecursionlimit(10**7)

s = input().strip()

# 현재 깊이와 거리 합
total_distance = 0
depth = 0
i = 0

while i < len(s):
    if s[i] == '(':
        depth += 1
        # 다음 문자가 ')'이면 리프 노드
        if i + 1 < len(s) and s[i + 1] == ')':
            total_distance += depth
            i += 2  # "()" 건너뛰기
        else:
            i += 1
    else:  # ')'
        depth -= 1
        i += 1

print(total_distance)
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

        long totalDistance = 0;
        int depth = 0;
        int i = 0;

        while (i < s.length()) {
            if (s.charAt(i) == '(') {
                depth++;
                // 다음 문자가 ')'이면 리프 노드
                if (i + 1 < s.length() && s.charAt(i + 1) == ')') {
                    totalDistance += depth;
                    i += 2;
                } else {
                    i++;
                }
            } else {
                depth--;
                i++;
            }
        }

        System.out.println(totalDistance);
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

    long long totalDistance = 0;
    int depth = 0;
    int i = 0;

    while (i < s.length()) {
        if (s[i] == '(') {
            depth++;
            // 다음 문자가 ')'이면 리프 노드
            if (i + 1 < s.length() && s[i + 1] == ')') {
                totalDistance += depth;
                i += 2;
            } else {
                i++;
            }
        } else {
            depth--;
            i++;
        }
    }

    cout << totalDistance << endl;

    return 0;
}
'''
        }
    ],

    # 문제 190: 21868 - 미적분학 입문하기
    4712: [
        {
            "language": "python",
            "code": '''# 백준 21868: 미적분학 입문하기
# f(x) = ax + b에서 lim(x->x0) f(x) = L = a*x0 + b
# |f(x) - L| < epsilon을 만족하는 delta의 최댓값

import sys
from math import gcd
input = sys.stdin.readline

# epsilon = p/q
p, q = map(int, input().split())

# f(x) = ax + b
a, b = map(int, input().split())

# x0
x0 = int(input())

# L = a * x0 + b
L = a * x0 + b

# |f(x) - L| = |ax + b - (a*x0 + b)| = |a(x - x0)| = |a| * |x - x0|
# |a| * |x - x0| < epsilon
# |x - x0| < epsilon / |a|

# 만약 a = 0이면, f(x) = b이고 |f(x) - L| = 0 < epsilon이 항상 성립
# 따라서 delta의 최댓값은 존재하지 않음

print(L)

if a == 0:
    print("0 0")
else:
    # delta = epsilon / |a| = (p/q) / |a| = p / (q * |a|)
    num = p
    den = q * abs(a)

    # 기약분수로 만들기
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

        long p = sc.nextLong();
        long q = sc.nextLong();
        long a = sc.nextLong();
        long b = sc.nextLong();
        long x0 = sc.nextLong();

        long L = a * x0 + b;
        System.out.println(L);

        if (a == 0) {
            System.out.println("0 0");
        } else {
            long num = p;
            long den = q * Math.abs(a);

            long g = gcd(num, den);
            num /= g;
            den /= g;

            if (num <= 100000000L && den <= 100000000L) {
                System.out.println(num + " " + den);
            } else {
                System.out.println("0 0");
            }
        }
    }

    static long gcd(long a, long b) {
        if (b == 0) return a;
        return gcd(b, a % b);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

long long gcd(long long a, long long b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long p, q, a, b, x0;
    cin >> p >> q >> a >> b >> x0;

    long long L = a * x0 + b;
    cout << L << endl;

    if (a == 0) {
        cout << "0 0" << endl;
    } else {
        long long num = p;
        long long den = q * (a < 0 ? -a : a);

        long long g = gcd(num, den);
        num /= g;
        den /= g;

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
    ],
}

def main():
    # JSON 파일 읽기
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        problems = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # medium 난이도이면서 solutions가 비어있고 input_output이 있는 문제 찾기
    empty_medium_indices = []
    for i, problem in enumerate(problems):
        difficulty = problem.get('difficulty', '')
        solutions = problem.get('solutions', [])
        input_output = problem.get('input_output', '')

        if difficulty == 'medium' and (not solutions or len(solutions) == 0) and input_output:
            empty_medium_indices.append(i)

    print(f"총 빈 medium 문제 수: {len(empty_medium_indices)}")

    # 인덱스 180-209에 해당하는 문제들 처리
    updated_count = 0
    for list_idx in range(180, 190):  # 먼저 180-189만 처리
        if list_idx >= len(empty_medium_indices):
            break

        original_idx = empty_medium_indices[list_idx]
        problem = problems[original_idx]

        if original_idx in SOLUTIONS:
            problems[original_idx]['solutions'] = SOLUTIONS[original_idx]
            updated_count += 1
            print(f"문제 {list_idx} (원본 인덱스 {original_idx}) 솔루션 추가: {problem.get('name')}")

    # 파일에 저장
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(problems, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\n총 {updated_count}개의 문제에 솔루션 추가 완료")

if __name__ == "__main__":
    main()
