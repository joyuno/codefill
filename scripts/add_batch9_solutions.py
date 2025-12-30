#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배치 9: 문제 81-90 솔루션 추가"""

import json

# 새로운 솔루션들
new_solutions = {
    "9358": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 수열 접기 게임
import sys
input = sys.stdin.readline

def solve():
    T = int(input())

    for t in range(1, T + 1):
        N = int(input())
        seq = list(map(int, input().split()))

        # 수열을 계속 접기
        while len(seq) > 2:
            new_seq = []
            n = len(seq)
            for i in range((n + 1) // 2):
                if i == n - 1 - i:
                    new_seq.append(seq[i] * 2)
                else:
                    new_seq.append(seq[i] + seq[n - 1 - i])
            seq = new_seq

        if seq[0] > seq[1]:
            print(f"Case #{t}: Alice")
        else:
            print(f"Case #{t}: Bob")

solve()
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

    int T;
    cin >> T;

    for (int t = 1; t <= T; t++) {
        int N;
        cin >> N;

        vector<long long> seq(N);
        for (int i = 0; i < N; i++) {
            cin >> seq[i];
        }

        while (seq.size() > 2) {
            vector<long long> newSeq;
            int n = seq.size();
            for (int i = 0; i < (n + 1) / 2; i++) {
                if (i == n - 1 - i) {
                    newSeq.push_back(seq[i] * 2);
                } else {
                    newSeq.push_back(seq[i] + seq[n - 1 - i]);
                }
            }
            seq = newSeq;
        }

        if (seq[0] > seq[1]) {
            cout << "Case #" << t << ": Alice" << "\\n";
        } else {
            cout << "Case #" << t << ": Bob" << "\\n";
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
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int T = Integer.parseInt(br.readLine().trim());

        for (int t = 1; t <= T; t++) {
            int N = Integer.parseInt(br.readLine().trim());
            StringTokenizer st = new StringTokenizer(br.readLine());

            List<Long> seq = new ArrayList<>();
            for (int i = 0; i < N; i++) {
                seq.add(Long.parseLong(st.nextToken()));
            }

            while (seq.size() > 2) {
                List<Long> newSeq = new ArrayList<>();
                int n = seq.size();
                for (int i = 0; i < (n + 1) / 2; i++) {
                    if (i == n - 1 - i) {
                        newSeq.add(seq.get(i) * 2);
                    } else {
                        newSeq.add(seq.get(i) + seq.get(n - 1 - i));
                    }
                }
                seq = newSeq;
            }

            if (seq.get(0) > seq.get(1)) {
                System.out.println("Case #" + t + ": Alice");
            } else {
                System.out.println("Case #" + t + ": Bob");
            }
        }
    }
}
'''
            }
        ]
    },
    "4900": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 7 세그먼트 디스플레이 덧셈
import sys
input = sys.stdin.readline

# 숫자 -> 코드 매핑
digit_to_code = {
    0: '063', 1: '010', 2: '093', 3: '079', 4: '106',
    5: '103', 6: '119', 7: '011', 8: '127', 9: '111'
}

# 코드 -> 숫자 매핑
code_to_digit = {v: k for k, v in digit_to_code.items()}

def decode(s):
    """코드를 숫자로 변환"""
    result = 0
    for i in range(0, len(s), 3):
        code = s[i:i+3]
        result = result * 10 + code_to_digit[code]
    return result

def encode(n):
    """숫자를 코드로 변환"""
    if n == 0:
        return '063'
    result = ''
    digits = []
    while n > 0:
        digits.append(n % 10)
        n //= 10
    for d in reversed(digits):
        result += digit_to_code[d]
    return result

def solve():
    while True:
        line = input().strip()
        if line == 'BYE':
            break

        # A+B= 파싱
        parts = line[:-1].split('+')  # 마지막 '=' 제거
        A = parts[0]
        B = parts[1]

        a = decode(A)
        b = decode(B)
        c = a + b
        C = encode(c)

        print(f"{A}+{B}={C}")

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <map>
using namespace std;

map<int, string> digitToCode = {
    {0, "063"}, {1, "010"}, {2, "093"}, {3, "079"}, {4, "106"},
    {5, "103"}, {6, "119"}, {7, "011"}, {8, "127"}, {9, "111"}
};

map<string, int> codeToDigit = {
    {"063", 0}, {"010", 1}, {"093", 2}, {"079", 3}, {"106", 4},
    {"103", 5}, {"119", 6}, {"011", 7}, {"127", 8}, {"111", 9}
};

long long decode(const string& s) {
    long long result = 0;
    for (int i = 0; i < s.length(); i += 3) {
        string code = s.substr(i, 3);
        result = result * 10 + codeToDigit[code];
    }
    return result;
}

string encode(long long n) {
    if (n == 0) return "063";
    string result;
    while (n > 0) {
        result = digitToCode[n % 10] + result;
        n /= 10;
    }
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string line;
    while (getline(cin, line)) {
        if (line == "BYE") break;

        // A+B= 파싱
        int plusPos = line.find('+');
        int eqPos = line.find('=');

        string A = line.substr(0, plusPos);
        string B = line.substr(plusPos + 1, eqPos - plusPos - 1);

        long long a = decode(A);
        long long b = decode(B);
        long long c = a + b;
        string C = encode(c);

        cout << A << "+" << B << "=" << C << "\\n";
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
    static Map<Integer, String> digitToCode = new HashMap<>();
    static Map<String, Integer> codeToDigit = new HashMap<>();

    static {
        digitToCode.put(0, "063"); digitToCode.put(1, "010");
        digitToCode.put(2, "093"); digitToCode.put(3, "079");
        digitToCode.put(4, "106"); digitToCode.put(5, "103");
        digitToCode.put(6, "119"); digitToCode.put(7, "011");
        digitToCode.put(8, "127"); digitToCode.put(9, "111");

        for (Map.Entry<Integer, String> e : digitToCode.entrySet()) {
            codeToDigit.put(e.getValue(), e.getKey());
        }
    }

    static long decode(String s) {
        long result = 0;
        for (int i = 0; i < s.length(); i += 3) {
            String code = s.substring(i, i + 3);
            result = result * 10 + codeToDigit.get(code);
        }
        return result;
    }

    static String encode(long n) {
        if (n == 0) return "063";
        StringBuilder result = new StringBuilder();
        while (n > 0) {
            result.insert(0, digitToCode.get((int)(n % 10)));
            n /= 10;
        }
        return result.toString();
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        String line;
        while ((line = br.readLine()) != null) {
            if (line.equals("BYE")) break;

            int plusPos = line.indexOf('+');
            int eqPos = line.indexOf('=');

            String A = line.substring(0, plusPos);
            String B = line.substring(plusPos + 1, eqPos);

            long a = decode(A);
            long b = decode(B);
            long c = a + b;
            String C = encode(c);

            sb.append(A).append("+").append(B).append("=").append(C).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "7507": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 올림픽 경기 최대 관람 - 그리디 (종료 시간 기준 정렬)
import sys
input = sys.stdin.readline

def solve():
    n = int(input())

    for scenario in range(1, n + 1):
        m = int(input())
        games = []
        for _ in range(m):
            d, s, e = map(int, input().split())
            games.append((d, s, e))

        # 날짜, 종료 시간 기준 정렬
        games.sort(key=lambda x: (x[0], x[2]))

        count = 0
        last_end = -1
        last_day = -1

        for d, s, e in games:
            if d != last_day:
                # 새로운 날
                count += 1
                last_day = d
                last_end = e
            elif s >= last_end:
                # 같은 날, 시작 시간이 마지막 종료 시간 이후
                count += 1
                last_end = e

        print(f"Scenario #{scenario}:")
        print(count)
        if scenario < n:
            print()

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

    int n;
    cin >> n;

    for (int scenario = 1; scenario <= n; scenario++) {
        int m;
        cin >> m;

        vector<tuple<int, int, int>> games(m);
        for (int i = 0; i < m; i++) {
            int d, s, e;
            cin >> d >> s >> e;
            games[i] = {d, e, s};  // 날짜, 종료, 시작
        }

        sort(games.begin(), games.end());

        int count = 0;
        int lastEnd = -1;
        int lastDay = -1;

        for (auto& [d, e, s] : games) {
            if (d != lastDay) {
                count++;
                lastDay = d;
                lastEnd = e;
            } else if (s >= lastEnd) {
                count++;
                lastEnd = e;
            }
        }

        cout << "Scenario #" << scenario << ":\\n";
        cout << count << "\\n";
        if (scenario < n) cout << "\\n";
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

        int n = Integer.parseInt(br.readLine().trim());

        for (int scenario = 1; scenario <= n; scenario++) {
            int m = Integer.parseInt(br.readLine().trim());

            int[][] games = new int[m][3];
            for (int i = 0; i < m; i++) {
                StringTokenizer st = new StringTokenizer(br.readLine());
                games[i][0] = Integer.parseInt(st.nextToken());  // day
                games[i][1] = Integer.parseInt(st.nextToken());  // start
                games[i][2] = Integer.parseInt(st.nextToken());  // end
            }

            // 날짜, 종료 시간 기준 정렬
            Arrays.sort(games, (a, b) -> {
                if (a[0] != b[0]) return a[0] - b[0];
                return a[2] - b[2];
            });

            int count = 0;
            int lastEnd = -1;
            int lastDay = -1;

            for (int[] g : games) {
                int d = g[0], s = g[1], e = g[2];
                if (d != lastDay) {
                    count++;
                    lastDay = d;
                    lastEnd = e;
                } else if (s >= lastEnd) {
                    count++;
                    lastEnd = e;
                }
            }

            sb.append("Scenario #").append(scenario).append(":\\n");
            sb.append(count).append("\\n");
            if (scenario < n) sb.append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "11387": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 전투력 계산 - 무기 교환 시 전투력 비교
import sys
input = sys.stdin.readline

def calc_power(atk, strength, crit_rate, crit_dmg, atk_speed):
    crit = min(crit_rate, 1.0)
    power = atk * (1 + strength / 100) * ((1 - crit) + crit * crit_dmg) * (1 + atk_speed)
    return power

def solve():
    # 크리 스탯
    kri = list(map(int, input().split()))
    # 파부 스탯
    pabu = list(map(int, input().split()))
    # 크리 무기
    kri_weapon = list(map(int, input().split()))
    # 파부 무기
    pabu_weapon = list(map(int, input().split()))

    # 현재 전투력
    kri_power = calc_power(kri[0], kri[1], kri[2]/100, kri[3]/100, kri[4]/100)
    pabu_power = calc_power(pabu[0], pabu[1], pabu[2]/100, pabu[3]/100, pabu[4]/100)

    # 크리가 파부 무기로 교체
    kri_new = [kri[i] - kri_weapon[i] + pabu_weapon[i] for i in range(5)]
    kri_new_power = calc_power(kri_new[0], kri_new[1], kri_new[2]/100, kri_new[3]/100, kri_new[4]/100)

    # 파부가 크리 무기로 교체
    pabu_new = [pabu[i] - pabu_weapon[i] + kri_weapon[i] for i in range(5)]
    pabu_new_power = calc_power(pabu_new[0], pabu_new[1], pabu_new[2]/100, pabu_new[3]/100, pabu_new[4]/100)

    # 결과
    def compare(old, new):
        if new > old + 1e-9:
            return '+'
        elif new < old - 1e-9:
            return '-'
        else:
            return '0'

    print(compare(kri_power, kri_new_power))
    print(compare(pabu_power, pabu_new_power))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
#include <cmath>
using namespace std;

double calcPower(double atk, double str, double critRate, double critDmg, double atkSpd) {
    double crit = min(critRate, 1.0);
    return atk * (1 + str / 100) * ((1 - crit) + crit * critDmg) * (1 + atkSpd);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    double kri[5], pabu[5], kriW[5], pabuW[5];

    for (int i = 0; i < 5; i++) cin >> kri[i];
    for (int i = 0; i < 5; i++) cin >> pabu[i];
    for (int i = 0; i < 5; i++) cin >> kriW[i];
    for (int i = 0; i < 5; i++) cin >> pabuW[i];

    double kriPower = calcPower(kri[0], kri[1], kri[2]/100, kri[3]/100, kri[4]/100);
    double pabuPower = calcPower(pabu[0], pabu[1], pabu[2]/100, pabu[3]/100, pabu[4]/100);

    double kriNew[5], pabuNew[5];
    for (int i = 0; i < 5; i++) {
        kriNew[i] = kri[i] - kriW[i] + pabuW[i];
        pabuNew[i] = pabu[i] - pabuW[i] + kriW[i];
    }

    double kriNewPower = calcPower(kriNew[0], kriNew[1], kriNew[2]/100, kriNew[3]/100, kriNew[4]/100);
    double pabuNewPower = calcPower(pabuNew[0], pabuNew[1], pabuNew[2]/100, pabuNew[3]/100, pabuNew[4]/100);

    auto compare = [](double old_p, double new_p) {
        if (new_p > old_p + 1e-9) return '+';
        if (new_p < old_p - 1e-9) return '-';
        return '0';
    };

    cout << compare(kriPower, kriNewPower) << "\\n";
    cout << compare(pabuPower, pabuNewPower) << "\\n";

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    static double calcPower(double atk, double str, double critRate, double critDmg, double atkSpd) {
        double crit = Math.min(critRate, 1.0);
        return atk * (1 + str / 100) * ((1 - crit) + crit * critDmg) * (1 + atkSpd);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        double[] kri = new double[5];
        double[] pabu = new double[5];
        double[] kriW = new double[5];
        double[] pabuW = new double[5];

        for (int i = 0; i < 5; i++) kri[i] = sc.nextDouble();
        for (int i = 0; i < 5; i++) pabu[i] = sc.nextDouble();
        for (int i = 0; i < 5; i++) kriW[i] = sc.nextDouble();
        for (int i = 0; i < 5; i++) pabuW[i] = sc.nextDouble();

        double kriPower = calcPower(kri[0], kri[1], kri[2]/100, kri[3]/100, kri[4]/100);
        double pabuPower = calcPower(pabu[0], pabu[1], pabu[2]/100, pabu[3]/100, pabu[4]/100);

        double[] kriNew = new double[5];
        double[] pabuNew = new double[5];
        for (int i = 0; i < 5; i++) {
            kriNew[i] = kri[i] - kriW[i] + pabuW[i];
            pabuNew[i] = pabu[i] - pabuW[i] + kriW[i];
        }

        double kriNewPower = calcPower(kriNew[0], kriNew[1], kriNew[2]/100, kriNew[3]/100, kriNew[4]/100);
        double pabuNewPower = calcPower(pabuNew[0], pabuNew[1], pabuNew[2]/100, pabuNew[3]/100, pabuNew[4]/100);

        System.out.println(compare(kriPower, kriNewPower));
        System.out.println(compare(pabuPower, pabuNewPower));
    }

    static char compare(double oldP, double newP) {
        if (newP > oldP + 1e-9) return '+';
        if (newP < oldP - 1e-9) return '-';
        return '0';
    }
}
'''
            }
        ]
    },
    "32247": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 파리 탈출 - 끈끈이주걱 피하기
import sys
input = sys.stdin.readline

def solve():
    N, M = map(int, input().split())

    # 각 x 위치별 제약 조건
    # 아래에서: y > h (y는 h 초과)
    # 위에서: y < h (y는 h 미만)
    lower = {}  # x -> 최소 y (이보다 커야 함)
    upper = {}  # x -> 최대 y (이보다 작아야 함)

    for _ in range(M):
        c, x, h = map(int, input().split())
        if c == 0:  # 아래에서
            if x not in lower or h > lower[x]:
                lower[x] = h
        else:  # 위에서
            if x not in upper or h < upper[x]:
                upper[x] = h

    # 시뮬레이션
    # y좌표 범위를 추적
    # 각 이동에서 a >= -1 (y + a로 이동)
    # y는 정수, 시작점 y=0, 끝점 y=0

    # DP: 각 x에서 가능한 y 범위
    # y_min, y_max 추적

    y_min, y_max = 0, 0

    for x in range(1, N):
        # 이전 위치 x-1에서 x로 이동
        # a >= -1 선택, y' = y + a
        # 새 y 범위: [y_min - 1, infinity) but y_max가 무한대는 아님

        # x 위치의 제약
        lo = lower.get(x, float('-inf'))  # y > lo
        hi = upper.get(x, float('inf'))   # y < hi

        # 새 y 범위
        new_y_min = y_min - 1  # a = -1일 때 최소
        new_y_max = float('inf')  # a는 얼마든지 클 수 있음

        # 제약 적용
        new_y_min = max(new_y_min, lo + 1)  # y > lo
        new_y_max = min(new_y_max, hi - 1)  # y < hi

        if new_y_min > new_y_max:
            print("adios")
            return

        y_min = new_y_min
        y_max = new_y_max

    # 마지막 이동: x=N-1 -> x=N, y must be 0
    # y + a = 0, a = -y
    # a >= -1이므로 -y >= -1, y <= 1
    # y는 y_min ~ y_max 범위
    if y_min <= 0 and y_max >= 0:
        print("stay")
    elif y_min <= 1:
        print("stay")
    else:
        print("adios")

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <map>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long N, M;
    cin >> N >> M;

    map<long long, long long> lower, upper;

    for (int i = 0; i < M; i++) {
        int c;
        long long x, h;
        cin >> c >> x >> h;
        if (c == 0) {
            if (lower.find(x) == lower.end() || h > lower[x]) {
                lower[x] = h;
            }
        } else {
            if (upper.find(x) == upper.end() || h < upper[x]) {
                upper[x] = h;
            }
        }
    }

    long long yMin = 0, yMax = 0;

    for (long long x = 1; x < N; x++) {
        long long newYMin = yMin - 1;
        long long newYMax = LLONG_MAX;

        if (lower.find(x) != lower.end()) {
            newYMin = max(newYMin, lower[x] + 1);
        }
        if (upper.find(x) != upper.end()) {
            newYMax = min(newYMax, upper[x] - 1);
        }

        if (newYMin > newYMax) {
            cout << "adios" << endl;
            return 0;
        }

        yMin = newYMin;
        yMax = newYMax;
    }

    if (yMin <= 1) {
        cout << "stay" << endl;
    } else {
        cout << "adios" << endl;
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
        StringTokenizer st = new StringTokenizer(br.readLine());

        long N = Long.parseLong(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        Map<Long, Long> lower = new HashMap<>();
        Map<Long, Long> upper = new HashMap<>();

        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            int c = Integer.parseInt(st.nextToken());
            long x = Long.parseLong(st.nextToken());
            long h = Long.parseLong(st.nextToken());

            if (c == 0) {
                lower.merge(x, h, Math::max);
            } else {
                upper.merge(x, h, Math::min);
            }
        }

        long yMin = 0, yMax = 0;

        for (long x = 1; x < N; x++) {
            long newYMin = yMin - 1;
            long newYMax = Long.MAX_VALUE;

            if (lower.containsKey(x)) {
                newYMin = Math.max(newYMin, lower.get(x) + 1);
            }
            if (upper.containsKey(x)) {
                newYMax = Math.min(newYMax, upper.get(x) - 1);
            }

            if (newYMin > newYMax) {
                System.out.println("adios");
                return;
            }

            yMin = newYMin;
            yMax = newYMax;
        }

        if (yMin <= 1) {
            System.out.println("stay");
        } else {
            System.out.println("adios");
        }
    }
}
'''
            }
        ]
    },
    "25287": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 순열 비감소로 만들기 - i를 N-i+1로 바꿀 수 있음
import sys
input = sys.stdin.readline

def solve():
    T = int(input())

    for _ in range(T):
        N = int(input())
        perm = list(map(int, input().split()))

        # 각 위치에서 min(i, N-i+1)과 max(i, N-i+1) 중 선택
        # 비감소 수열이 되도록

        prev = 0
        possible = True

        for i in range(N):
            val = perm[i]
            other = N - val + 1

            small = min(val, other)
            big = max(val, other)

            # prev 이상인 값 중 가장 작은 것 선택
            if small >= prev:
                prev = small
            elif big >= prev:
                prev = big
            else:
                possible = False
                break

        print("YES" if possible else "NO")

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
        int N;
        cin >> N;

        int prev = 0;
        bool possible = true;

        for (int i = 0; i < N; i++) {
            int val;
            cin >> val;
            int other = N - val + 1;

            int small = min(val, other);
            int big = max(val, other);

            if (small >= prev) {
                prev = small;
            } else if (big >= prev) {
                prev = big;
            } else {
                possible = false;
            }
        }

        cout << (possible ? "YES" : "NO") << "\\n";
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
            int N = Integer.parseInt(br.readLine().trim());
            StringTokenizer st = new StringTokenizer(br.readLine());

            int prev = 0;
            boolean possible = true;

            for (int i = 0; i < N; i++) {
                int val = Integer.parseInt(st.nextToken());
                int other = N - val + 1;

                int small = Math.min(val, other);
                int big = Math.max(val, other);

                if (small >= prev) {
                    prev = small;
                } else if (big >= prev) {
                    prev = big;
                } else {
                    possible = false;
                }
            }

            sb.append(possible ? "YES" : "NO").append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "17251": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 힘 겨루기 - 최대값 위치로 승자 결정
import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    strengths = list(map(int, input().split()))

    max_val = max(strengths)

    # 최대값의 첫 위치와 마지막 위치
    first_max = strengths.index(max_val)
    last_max = N - 1 - strengths[::-1].index(max_val)

    # 홍팀: 기준선 왼쪽 (인덱스 0 ~ i)
    # 청팀: 기준선 오른쪽 (인덱스 i+1 ~ N-1)
    # 기준선: i와 i+1 사이 (i = 0 ~ N-2)

    # 홍팀이 이기려면: 최대값이 왼쪽에만 있어야 함
    # 청팀이 이기려면: 최대값이 오른쪽에만 있어야 함

    # first_max가 왼쪽에 있는 경우: 기준선 >= first_max
    # last_max가 오른쪽에 있는 경우: 기준선 < last_max

    # 홍팀 승리: 기준선이 last_max 이상 (마지막 최대값도 왼쪽에 포함)
    red_wins = N - 1 - last_max  # 기준선 = last_max, ..., N-2

    # 청팀 승리: 기준선이 first_max 미만 (첫 최대값도 오른쪽에 포함)
    blue_wins = first_max  # 기준선 = 0, ..., first_max-1

    if red_wins > blue_wins:
        print('R')
    elif blue_wins > red_wins:
        print('B')
    else:
        print('X')

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

    vector<int> strengths(N);
    for (int i = 0; i < N; i++) {
        cin >> strengths[i];
    }

    int maxVal = *max_element(strengths.begin(), strengths.end());

    int firstMax = -1, lastMax = -1;
    for (int i = 0; i < N; i++) {
        if (strengths[i] == maxVal) {
            if (firstMax == -1) firstMax = i;
            lastMax = i;
        }
    }

    int redWins = N - 1 - lastMax;
    int blueWins = firstMax;

    if (redWins > blueWins) {
        cout << "R" << endl;
    } else if (blueWins > redWins) {
        cout << "B" << endl;
    } else {
        cout << "X" << endl;
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
        int N = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] strengths = new int[N];
        int maxVal = 0;

        for (int i = 0; i < N; i++) {
            strengths[i] = Integer.parseInt(st.nextToken());
            maxVal = Math.max(maxVal, strengths[i]);
        }

        int firstMax = -1, lastMax = -1;
        for (int i = 0; i < N; i++) {
            if (strengths[i] == maxVal) {
                if (firstMax == -1) firstMax = i;
                lastMax = i;
            }
        }

        int redWins = N - 1 - lastMax;
        int blueWins = firstMax;

        if (redWins > blueWins) {
            System.out.println("R");
        } else if (blueWins > redWins) {
            System.out.println("B");
        } else {
            System.out.println("X");
        }
    }
}
'''
            }
        ]
    },
    "11978": {
        "solutions": [
            {
                "language": "python",
                "code": '''# FJ 잔디 깎기 - 다시 자라기 전에 깎은 칸 수
import sys
input = sys.stdin.readline

def solve():
    line = input().split()
    X = int(line[0])  # 다시 자라는 시간

    directions = []
    for _ in range(6):
        parts = input().split()
        d = parts[0]
        steps = int(parts[1])
        directions.append((d, steps))

    # 방향 매핑
    dx = {'N': 0, 'S': 0, 'E': 1, 'W': -1}
    dy = {'N': 1, 'S': -1, 'E': 0, 'W': 0}

    # 모든 칸과 방문 시간 기록
    visited = {}  # (x, y) -> 첫 방문 시간
    x, y, t = 0, 0, 0

    visited[(x, y)] = t

    for d, steps in directions:
        for _ in range(steps):
            t += 1
            x += dx[d]
            y += dy[d]
            if (x, y) not in visited:
                visited[(x, y)] = t

    # 최종 시간
    T = t

    # 다시 자라지 않은 칸 수
    # 시간 T에서, 칸 (x, y)가 다시 자라지 않으려면
    # visited[(x, y)] + X > T
    count = 0
    for (px, py), first_t in visited.items():
        if first_t + X > T:
            count += 1

    print(count)

solve()
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

    int X;
    cin >> X;

    map<pair<int, int>, int> visited;

    int x = 0, y = 0, t = 0;
    visited[{x, y}] = t;

    for (int i = 0; i < 6; i++) {
        char d;
        int steps;
        cin >> d >> steps;

        int dx = 0, dy = 0;
        if (d == 'N') dy = 1;
        else if (d == 'S') dy = -1;
        else if (d == 'E') dx = 1;
        else if (d == 'W') dx = -1;

        for (int j = 0; j < steps; j++) {
            t++;
            x += dx;
            y += dy;
            if (visited.find({x, y}) == visited.end()) {
                visited[{x, y}] = t;
            }
        }
    }

    int T = t;
    int count = 0;
    for (auto& [pos, firstT] : visited) {
        if (firstT + X > T) count++;
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
        int X = Integer.parseInt(br.readLine().trim());

        Map<Long, Integer> visited = new HashMap<>();

        int x = 0, y = 0, t = 0;
        visited.put(key(x, y), t);

        for (int i = 0; i < 6; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            char d = st.nextToken().charAt(0);
            int steps = Integer.parseInt(st.nextToken());

            int dx = 0, dy = 0;
            if (d == 'N') dy = 1;
            else if (d == 'S') dy = -1;
            else if (d == 'E') dx = 1;
            else if (d == 'W') dx = -1;

            for (int j = 0; j < steps; j++) {
                t++;
                x += dx;
                y += dy;
                long k = key(x, y);
                if (!visited.containsKey(k)) {
                    visited.put(k, t);
                }
            }
        }

        int T = t;
        int count = 0;
        for (int firstT : visited.values()) {
            if (firstT + X > T) count++;
        }

        System.out.println(count);
    }

    static long key(int x, int y) {
        return ((long)x << 20) + y;
    }
}
'''
            }
        ]
    },
    "27972": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 피아노 연주 수열 - N의 최솟값 찾기
import sys
input = sys.stdin.readline

def solve():
    M = int(input())
    p = list(map(int, input().split()))

    # 연속 증가/감소 구간의 최대 길이 찾기
    max_len = 1
    current_len = 1

    for i in range(1, M):
        if p[i] > p[i-1]:
            current_len += 1
        elif p[i] < p[i-1]:
            current_len += 1
        else:
            # 같으면 길이 유지
            pass

        # 방향 전환 시 리셋
        if i >= 1:
            if p[i] > p[i-1]:
                if i < M - 1 and p[i] >= p[i+1]:
                    pass  # 계속
                max_len = max(max_len, current_len)
            elif p[i] < p[i-1]:
                max_len = max(max_len, current_len)

    # 재계산: 연속 증가 또는 감소 구간의 최대 길이
    max_inc = 1
    max_dec = 1
    inc_len = 1
    dec_len = 1

    for i in range(1, M):
        if p[i] > p[i-1]:
            inc_len += 1
            dec_len = 1
        elif p[i] < p[i-1]:
            dec_len += 1
            inc_len = 1
        else:
            # 같으면 둘 다 유지
            pass

        max_inc = max(max_inc, inc_len)
        max_dec = max(max_dec, dec_len)

    print(max(max_inc, max_dec))

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

    int M;
    cin >> M;

    int prev, curr;
    cin >> prev;

    int maxInc = 1, maxDec = 1;
    int incLen = 1, decLen = 1;

    for (int i = 1; i < M; i++) {
        cin >> curr;

        if (curr > prev) {
            incLen++;
            decLen = 1;
        } else if (curr < prev) {
            decLen++;
            incLen = 1;
        }
        // 같으면 둘 다 유지

        maxInc = max(maxInc, incLen);
        maxDec = max(maxDec, decLen);

        prev = curr;
    }

    cout << max(maxInc, maxDec) << endl;

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
        int M = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int prev = Integer.parseInt(st.nextToken());

        int maxInc = 1, maxDec = 1;
        int incLen = 1, decLen = 1;

        for (int i = 1; i < M; i++) {
            int curr = Integer.parseInt(st.nextToken());

            if (curr > prev) {
                incLen++;
                decLen = 1;
            } else if (curr < prev) {
                decLen++;
                incLen = 1;
            }

            maxInc = Math.max(maxInc, incLen);
            maxDec = Math.max(maxDec, decLen);

            prev = curr;
        }

        System.out.println(Math.max(maxInc, maxDec));
    }
}
'''
            }
        ]
    },
    "30677": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 별가루 만들기 - 시뮬레이션
import sys
input = sys.stdin.readline

def solve():
    line = input().split()
    N, K, C, R = int(line[0]), int(line[1]), int(line[2]), int(line[3])

    base = list(map(int, input().split()))
    s = list(map(int, input().split()))
    p = list(map(int, input().split()))

    plan = []
    for _ in range(N):
        plan.append(int(input()))

    # 시뮬레이션
    fatigue = 0
    combo = 0
    skill = [0] * K  # 각 마법 숙련도
    total_stardust = 0

    for day in range(N):
        magic = plan[day]

        if magic == 0:
            # 휴식
            fatigue = max(0, fatigue - R)
            combo = 0
        else:
            idx = magic - 1

            # 피로도 체크
            if fatigue + p[idx] > 100:
                print(-1)
                return

            # 별가루 계산
            delta = int(base[idx] * (1 + combo * C / 100) * (1 + skill[idx] * s[idx] / 100))
            total_stardust += delta

            # 상태 업데이트
            fatigue += p[idx]
            combo += 1
            skill[idx] += 1

    print(total_stardust)

solve()
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

    int N, K, C, R;
    cin >> N >> K >> C >> R;

    vector<long long> base(K), s(K), p(K);
    for (int i = 0; i < K; i++) cin >> base[i];
    for (int i = 0; i < K; i++) cin >> s[i];
    for (int i = 0; i < K; i++) cin >> p[i];

    vector<int> plan(N);
    for (int i = 0; i < N; i++) cin >> plan[i];

    long long fatigue = 0, combo = 0;
    vector<long long> skill(K, 0);
    long long totalStardust = 0;

    for (int day = 0; day < N; day++) {
        int magic = plan[day];

        if (magic == 0) {
            fatigue = max(0LL, fatigue - R);
            combo = 0;
        } else {
            int idx = magic - 1;

            if (fatigue + p[idx] > 100) {
                cout << -1 << endl;
                return 0;
            }

            long long delta = (long long)(base[idx] * (1.0 + combo * C / 100.0) * (1.0 + skill[idx] * s[idx] / 100.0));
            totalStardust += delta;

            fatigue += p[idx];
            combo++;
            skill[idx]++;
        }
    }

    cout << totalStardust << endl;

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
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());
        int C = Integer.parseInt(st.nextToken());
        int R = Integer.parseInt(st.nextToken());

        long[] base = new long[K];
        long[] s = new long[K];
        long[] p = new long[K];

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < K; i++) base[i] = Long.parseLong(st.nextToken());

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < K; i++) s[i] = Long.parseLong(st.nextToken());

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < K; i++) p[i] = Long.parseLong(st.nextToken());

        int[] plan = new int[N];
        for (int i = 0; i < N; i++) {
            plan[i] = Integer.parseInt(br.readLine().trim());
        }

        long fatigue = 0, combo = 0;
        long[] skill = new long[K];
        long totalStardust = 0;

        for (int day = 0; day < N; day++) {
            int magic = plan[day];

            if (magic == 0) {
                fatigue = Math.max(0, fatigue - R);
                combo = 0;
            } else {
                int idx = magic - 1;

                if (fatigue + p[idx] > 100) {
                    System.out.println(-1);
                    return;
                }

                long delta = (long)(base[idx] * (1.0 + combo * C / 100.0) * (1.0 + skill[idx] * s[idx] / 100.0));
                totalStardust += delta;

                fatigue += p[idx];
                combo++;
                skill[idx]++;
            }
        }

        System.out.println(totalStardust);
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
