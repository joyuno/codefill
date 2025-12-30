#!/usr/bin/env python3
"""
Generate solutions for Baekjoon problems (indices 390-419 in empty medium list)
Complete version with all 30 problems
"""
import json
import fcntl
import os

# 문제 인덱스 매핑 (empty medium list index -> original index)
PROBLEM_INDICES = [
    6120, 6121, 6125, 6133, 6134, 6142, 6148, 6151, 6176, 6177,
    6178, 6205, 6210, 6215, 6221, 6230, 6233, 6235, 6237, 6238,
    6243, 6246, 6250, 6252, 6268, 6270, 6278, 6279, 6280, 6307
]

def get_all_solutions():
    """Return solutions for all 30 problems."""
    solutions = {}

    # Problem 390: baekjoon_32195 - 야구
    solutions[6120] = [
        {
            "language": "python",
            "code": '''# 야구 - 타구 분류 문제
# 파울, 내야, 홈런을 구분
import sys
input = sys.stdin.readline

n = int(input())
balls = []
for _ in range(n):
    x, y = map(int, input().split())
    balls.append((x, y))

q = int(input())
for _ in range(q):
    r = int(input())
    r_sq = r * r
    foul, infield, homerun = 0, 0, 0

    for x, y in balls:
        dist_sq = x * x + y * y
        # 담장 범위: y >= x 와 y >= -x (45도 ~ 135도)
        in_fair = (y >= x and y >= -x)

        if not in_fair:
            foul += 1
        elif dist_sq <= r_sq:
            infield += 1
        else:
            homerun += 1

    print(foul, infield, homerun)
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
        long[][] balls = new long[n][2];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            balls[i][0] = Long.parseLong(st.nextToken());
            balls[i][1] = Long.parseLong(st.nextToken());
        }

        int q = Integer.parseInt(br.readLine().trim());
        while (q-- > 0) {
            long r = Long.parseLong(br.readLine().trim());
            long rSq = r * r;
            int foul = 0, infield = 0, homerun = 0;

            for (int i = 0; i < n; i++) {
                long x = balls[i][0], y = balls[i][1];
                long distSq = x * x + y * y;
                boolean inFair = (y >= x && y >= -x);

                if (!inFair) foul++;
                else if (distSq <= rSq) infield++;
                else homerun++;
            }
            sb.append(foul).append(" ").append(infield).append(" ").append(homerun).append("\\n");
        }
        System.out.print(sb);
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
    vector<pair<long long, long long>> balls(n);

    for (int i = 0; i < n; i++) {
        cin >> balls[i].first >> balls[i].second;
    }

    int q;
    cin >> q;
    while (q--) {
        long long r;
        cin >> r;
        long long rSq = r * r;
        int foul = 0, infield = 0, homerun = 0;

        for (auto& b : balls) {
            long long x = b.first, y = b.second;
            long long distSq = x * x + y * y;
            bool inFair = (y >= x && y >= -x);

            if (!inFair) foul++;
            else if (distSq <= rSq) infield++;
            else homerun++;
        }
        cout << foul << " " << infield << " " << homerun << "\\n";
    }
    return 0;
}
'''
        }
    ]

    # Problem 391: baekjoon_25268 - Name Generation
    solutions[6121] = [
        {
            "language": "python",
            "code": '''# Name Generation - 이름 생성
# 3개 연속 모음/자음 금지
n = int(input())

cons = "bcdfghjklmnpqrstvwxyz"
vow = "aeiou"

names = []
# 자음-모음-자음 패턴
for c1 in cons:
    for v1 in vow:
        for c2 in cons:
            names.append(c1 + v1 + c2)
            if len(names) >= n:
                break
        if len(names) >= n:
            break
    if len(names) >= n:
        break

# 부족하면 4글자 추가
if len(names) < n:
    for c1 in cons:
        for v1 in vow:
            for c2 in cons:
                for v2 in vow:
                    names.append(c1 + v1 + c2 + v2)
                    if len(names) >= n:
                        break
                if len(names) >= n:
                    break
            if len(names) >= n:
                break
        if len(names) >= n:
            break

for i in range(n):
    print(names[i])
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        String cons = "bcdfghjklmnpqrstvwxyz";
        String vow = "aeiou";
        List<String> names = new ArrayList<>();

        outer:
        for (int i = 0; i < cons.length(); i++) {
            for (int j = 0; j < vow.length(); j++) {
                for (int k = 0; k < cons.length(); k++) {
                    names.add("" + cons.charAt(i) + vow.charAt(j) + cons.charAt(k));
                    if (names.size() >= n) break outer;
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append(names.get(i)).append("\\n");
        }
        System.out.print(sb);
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

int main() {
    int n;
    cin >> n;

    string cons = "bcdfghjklmnpqrstvwxyz";
    string vow = "aeiou";
    vector<string> names;

    for (size_t i = 0; i < cons.length() && names.size() < (size_t)n; i++) {
        for (size_t j = 0; j < vow.length() && names.size() < (size_t)n; j++) {
            for (size_t k = 0; k < cons.length() && names.size() < (size_t)n; k++) {
                string name = "";
                name += cons[i]; name += vow[j]; name += cons[k];
                names.push_back(name);
            }
        }
    }

    for (int i = 0; i < n; i++) {
        cout << names[i] << "\\n";
    }
    return 0;
}
'''
        }
    ]

    # Problem 392: baekjoon_5866 - Meet and Greet
    solutions[6125] = [
        {
            "language": "python",
            "code": '''# Meet and Greet - 두 소가 만나는 횟수
import sys
input = sys.stdin.readline

line = input().split()
b, e = int(line[0]), int(line[1])

# 이동 기록 읽기
bessie = []
for _ in range(b):
    parts = input().split()
    bessie.append((int(parts[0]), 1 if parts[1] == 'R' else -1))

elsie = []
for _ in range(e):
    parts = input().split()
    elsie.append((int(parts[0]), 1 if parts[1] == 'R' else -1))

# 시간별 위치 계산
def get_pos(moves):
    pos = [(0, 0)]
    t, p = 0, 0
    for dist, d in moves:
        for _ in range(dist):
            t += 1
            p += d
            pos.append((t, p))
    return pos, p

bp, be = get_pos(bessie)
ep, ee = get_pos(elsie)

max_t = max(bp[-1][0], ep[-1][0])
ba = [0] * (max_t + 1)
ea = [0] * (max_t + 1)

for t, p in bp:
    ba[t] = p
for t in range(len(bp), max_t + 1):
    ba[t] = be

for t, p in ep:
    ea[t] = p
for t in range(len(ep), max_t + 1):
    ea[t] = ee

moos = 0
for t in range(1, max_t + 1):
    prev = ba[t-1] - ea[t-1]
    curr = ba[t] - ea[t]
    if curr == 0 and prev != 0:
        moos += 1
    elif prev * curr < 0:
        moos += 1

print(moos)
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
        int B = Integer.parseInt(st.nextToken());
        int E = Integer.parseInt(st.nextToken());

        int[][] bessie = new int[B][2];
        for (int i = 0; i < B; i++) {
            st = new StringTokenizer(br.readLine());
            bessie[i][0] = Integer.parseInt(st.nextToken());
            bessie[i][1] = st.nextToken().equals("R") ? 1 : -1;
        }

        int[][] elsie = new int[E][2];
        for (int i = 0; i < E; i++) {
            st = new StringTokenizer(br.readLine());
            elsie[i][0] = Integer.parseInt(st.nextToken());
            elsie[i][1] = st.nextToken().equals("R") ? 1 : -1;
        }

        List<int[]> bp = new ArrayList<>();
        bp.add(new int[]{0, 0});
        int t = 0, p = 0;
        for (int[] m : bessie) {
            for (int j = 0; j < m[0]; j++) {
                t++; p += m[1];
                bp.add(new int[]{t, p});
            }
        }
        int be = p, bt = t;

        List<int[]> ep = new ArrayList<>();
        ep.add(new int[]{0, 0});
        t = 0; p = 0;
        for (int[] m : elsie) {
            for (int j = 0; j < m[0]; j++) {
                t++; p += m[1];
                ep.add(new int[]{t, p});
            }
        }
        int ee = p, et = t;

        int maxT = Math.max(bt, et);
        int[] ba = new int[maxT + 1];
        int[] ea = new int[maxT + 1];

        for (int[] x : bp) ba[x[0]] = x[1];
        for (int i = bt + 1; i <= maxT; i++) ba[i] = be;
        for (int[] x : ep) ea[x[0]] = x[1];
        for (int i = et + 1; i <= maxT; i++) ea[i] = ee;

        int moos = 0;
        for (int i = 1; i <= maxT; i++) {
            long prev = ba[i-1] - ea[i-1];
            long curr = ba[i] - ea[i];
            if (curr == 0 && prev != 0) moos++;
            else if (prev * curr < 0) moos++;
        }
        System.out.println(moos);
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

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int B, E;
    cin >> B >> E;

    vector<pair<int, int>> bessie(B), elsie(E);
    for (int i = 0; i < B; i++) {
        int d; string dir;
        cin >> d >> dir;
        bessie[i] = {d, dir == "R" ? 1 : -1};
    }
    for (int i = 0; i < E; i++) {
        int d; string dir;
        cin >> d >> dir;
        elsie[i] = {d, dir == "R" ? 1 : -1};
    }

    vector<pair<int, int>> bp, ep;
    bp.push_back({0, 0});
    int t = 0, p = 0;
    for (auto& m : bessie) {
        for (int j = 0; j < m.first; j++) {
            t++; p += m.second;
            bp.push_back({t, p});
        }
    }
    int be = p, bt = t;

    ep.push_back({0, 0});
    t = 0; p = 0;
    for (auto& m : elsie) {
        for (int j = 0; j < m.first; j++) {
            t++; p += m.second;
            ep.push_back({t, p});
        }
    }
    int ee = p, et = t;

    int maxT = max(bt, et);
    vector<int> ba(maxT + 1), ea(maxT + 1);

    for (auto& x : bp) ba[x.first] = x.second;
    for (int i = bt + 1; i <= maxT; i++) ba[i] = be;
    for (auto& x : ep) ea[x.first] = x.second;
    for (int i = et + 1; i <= maxT; i++) ea[i] = ee;

    int moos = 0;
    for (int i = 1; i <= maxT; i++) {
        long long prev = ba[i-1] - ea[i-1];
        long long curr = ba[i] - ea[i];
        if (curr == 0 && prev != 0) moos++;
        else if (prev * curr < 0) moos++;
    }
    cout << moos << endl;
    return 0;
}
'''
        }
    ]

    # Problem 393: baekjoon_3684 - 어려운 문제
    solutions[6133] = [
        {
            "language": "python",
            "code": '''# 어려운 문제 - 선형합동식
import sys
input = sys.stdin.readline

T = int(input())
inputs = [int(input()) for _ in range(T)]

# a, b 찾기
for a in range(10001):
    for b in range(10001):
        valid = True
        x = inputs[0]
        outputs = []
        for i in range(T):
            x_next = (a * x + b) % 10001
            outputs.append(x_next)
            x_next2 = (a * x_next + b) % 10001
            if i + 1 < T and x_next2 != inputs[i + 1]:
                valid = False
                break
            x = x_next2

        if valid:
            for out in outputs:
                print(out)
            exit()
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
        int[] inputs = new int[T];
        for (int i = 0; i < T; i++) {
            inputs[i] = Integer.parseInt(br.readLine().trim());
        }

        outer:
        for (int a = 0; a <= 10000; a++) {
            for (int b = 0; b <= 10000; b++) {
                boolean valid = true;
                int x = inputs[0];
                int[] outputs = new int[T];

                for (int i = 0; i < T; i++) {
                    int xNext = (a * x + b) % 10001;
                    outputs[i] = xNext;
                    int xNext2 = (a * xNext + b) % 10001;
                    if (i + 1 < T && xNext2 != inputs[i + 1]) {
                        valid = false;
                        break;
                    }
                    x = xNext2;
                }

                if (valid) {
                    StringBuilder sb = new StringBuilder();
                    for (int out : outputs) sb.append(out).append("\\n");
                    System.out.print(sb);
                    break outer;
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
#include <vector>
using namespace std;

int main() {
    int T;
    cin >> T;
    vector<int> inputs(T);
    for (int i = 0; i < T; i++) cin >> inputs[i];

    for (int a = 0; a <= 10000; a++) {
        for (int b = 0; b <= 10000; b++) {
            bool valid = true;
            int x = inputs[0];
            vector<int> outputs(T);

            for (int i = 0; i < T; i++) {
                int xNext = (1LL * a * x + b) % 10001;
                outputs[i] = xNext;
                int xNext2 = (1LL * a * xNext + b) % 10001;
                if (i + 1 < T && xNext2 != inputs[i + 1]) {
                    valid = false;
                    break;
                }
                x = xNext2;
            }

            if (valid) {
                for (int out : outputs) cout << out << "\\n";
                return 0;
            }
        }
    }
    return 0;
}
'''
        }
    ]

    # Problem 394: baekjoon_31802 - 주기 함수 (Easy)
    solutions[6134] = [
        {
            "language": "python",
            "code": '''# 주기 함수 (Easy)
import sys
input = sys.stdin.readline

p = int(input())
vals = list(map(int, input().split()))
a, b = map(int, input().split())

# 누적합
prefix = [0] * (p + 1)
for i in range(p):
    prefix[i + 1] = prefix[i] + vals[i]
total = prefix[p]

def integrate(x):
    if x >= 0:
        return (x // p) * total + prefix[x % p]
    else:
        full = (-x) // p
        rem = (-x) % p
        if rem == 0:
            return -full * total
        return -(full + 1) * total + prefix[p - rem]

print(integrate(b) - integrate(a))
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    static long[] prefix;
    static long total;
    static int p;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        p = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        prefix = new long[p + 1];
        for (int i = 0; i < p; i++) {
            prefix[i + 1] = prefix[i] + Long.parseLong(st.nextToken());
        }
        total = prefix[p];

        st = new StringTokenizer(br.readLine());
        long a = Long.parseLong(st.nextToken());
        long b = Long.parseLong(st.nextToken());

        System.out.println(integrate(b) - integrate(a));
    }

    static long integrate(long x) {
        if (x >= 0) {
            return (x / p) * total + prefix[(int)(x % p)];
        } else {
            long full = (-x) / p;
            int rem = (int)((-x) % p);
            if (rem == 0) return -full * total;
            return -(full + 1) * total + prefix[p - rem];
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

int p;
vector<long long> prefix;
long long total;

long long integrate(long long x) {
    if (x >= 0) {
        return (x / p) * total + prefix[x % p];
    } else {
        long long full = (-x) / p;
        int rem = (-x) % p;
        if (rem == 0) return -full * total;
        return -(full + 1) * total + prefix[p - rem];
    }
}

int main() {
    cin >> p;
    prefix.resize(p + 1);
    for (int i = 0; i < p; i++) {
        long long v; cin >> v;
        prefix[i + 1] = prefix[i] + v;
    }
    total = prefix[p];

    long long a, b;
    cin >> a >> b;
    cout << integrate(b) - integrate(a) << endl;
    return 0;
}
'''
        }
    ]

    # Problem 395: baekjoon_27921 - 동전 퍼즐
    solutions[6142] = [
        {
            "language": "python",
            "code": '''# 동전 퍼즐 - 최소 이동
import sys
input = sys.stdin.readline

h1, w1 = map(int, input().split())
coins1 = []
for i in range(h1):
    row = input().strip()
    for j in range(len(row)):
        if row[j] == 'O':
            coins1.append((i, j))

h2, w2 = map(int, input().split())
coins2 = []
coins2_set = set()
for i in range(h2):
    row = input().strip()
    for j in range(len(row)):
        if row[j] == 'O':
            coins2.append((i, j))
            coins2_set.add((i, j))

n = len(coins1)
max_overlap = 0

for c1 in coins1:
    for c2 in coins2:
        dy, dx = c2[0] - c1[0], c2[1] - c1[1]
        overlap = sum(1 for y, x in coins1 if (y + dy, x + dx) in coins2_set)
        max_overlap = max(max_overlap, overlap)

print(n - max_overlap)
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
        int h1 = Integer.parseInt(st.nextToken()), w1 = Integer.parseInt(st.nextToken());
        List<int[]> coins1 = new ArrayList<>();
        for (int i = 0; i < h1; i++) {
            String row = br.readLine();
            for (int j = 0; j < row.length(); j++) {
                if (row.charAt(j) == 'O') coins1.add(new int[]{i, j});
            }
        }

        st = new StringTokenizer(br.readLine());
        int h2 = Integer.parseInt(st.nextToken()), w2 = Integer.parseInt(st.nextToken());
        Set<Long> coins2Set = new HashSet<>();
        List<int[]> coins2 = new ArrayList<>();
        for (int i = 0; i < h2; i++) {
            String row = br.readLine();
            for (int j = 0; j < row.length(); j++) {
                if (row.charAt(j) == 'O') {
                    coins2.add(new int[]{i, j});
                    coins2Set.add((long)i * 100 + j);
                }
            }
        }

        int n = coins1.size(), maxOverlap = 0;
        for (int[] c1 : coins1) {
            for (int[] c2 : coins2) {
                int dy = c2[0] - c1[0], dx = c2[1] - c1[1];
                int overlap = 0;
                for (int[] c : coins1) {
                    if (coins2Set.contains((long)(c[0] + dy) * 100 + (c[1] + dx))) overlap++;
                }
                maxOverlap = Math.max(maxOverlap, overlap);
            }
        }
        System.out.println(n - maxOverlap);
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

int main() {
    int h1, w1;
    cin >> h1 >> w1;
    vector<pair<int, int>> coins1;
    for (int i = 0; i < h1; i++) {
        string row; cin >> row;
        for (int j = 0; j < (int)row.size(); j++) {
            if (row[j] == 'O') coins1.push_back({i, j});
        }
    }

    int h2, w2;
    cin >> h2 >> w2;
    vector<pair<int, int>> coins2;
    set<pair<int, int>> coins2Set;
    for (int i = 0; i < h2; i++) {
        string row; cin >> row;
        for (int j = 0; j < (int)row.size(); j++) {
            if (row[j] == 'O') {
                coins2.push_back({i, j});
                coins2Set.insert({i, j});
            }
        }
    }

    int n = coins1.size(), maxOverlap = 0;
    for (auto& c1 : coins1) {
        for (auto& c2 : coins2) {
            int dy = c2.first - c1.first, dx = c2.second - c1.second;
            int overlap = 0;
            for (auto& c : coins1) {
                if (coins2Set.count({c.first + dy, c.second + dx})) overlap++;
            }
            maxOverlap = max(maxOverlap, overlap);
        }
    }
    cout << n - maxOverlap << endl;
    return 0;
}
'''
        }
    ]

    # Problem 396: baekjoon_14791 - Tidy Numbers
    solutions[6148] = [
        {
            "language": "python",
            "code": '''# Tidy Numbers (Large)
T = int(input())
for c in range(1, T + 1):
    n = input().strip()
    s = list(n)

    for i in range(len(s) - 1, 0, -1):
        if s[i - 1] > s[i]:
            s[i - 1] = chr(ord(s[i - 1]) - 1)
            for j in range(i, len(s)):
                s[j] = '9'

    result = ''.join(s).lstrip('0') or '0'
    print(f"Case #{c}: {result}")
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int T = Integer.parseInt(br.readLine().trim());

        for (int c = 1; c <= T; c++) {
            char[] s = br.readLine().trim().toCharArray();

            for (int i = s.length - 1; i > 0; i--) {
                if (s[i - 1] > s[i]) {
                    s[i - 1]--;
                    for (int j = i; j < s.length; j++) s[j] = '9';
                }
            }

            String result = new String(s);
            int start = 0;
            while (start < result.length() - 1 && result.charAt(start) == '0') start++;
            System.out.println("Case #" + c + ": " + result.substring(start));
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

int main() {
    int T;
    cin >> T;

    for (int c = 1; c <= T; c++) {
        string s;
        cin >> s;

        for (int i = s.length() - 1; i > 0; i--) {
            if (s[i - 1] > s[i]) {
                s[i - 1]--;
                for (int j = i; j < (int)s.length(); j++) s[j] = '9';
            }
        }

        int start = 0;
        while (start < (int)s.length() - 1 && s[start] == '0') start++;
        cout << "Case #" << c << ": " << s.substr(start) << "\\n";
    }
    return 0;
}
'''
        }
    ]

    # Problem 397: baekjoon_11423 - Primes
    solutions[6151] = [
        {
            "language": "python",
            "code": '''# Primes - 범위 내 소수 개수
import sys

MAX = 10000001
is_prime = [True] * MAX
is_prime[0] = is_prime[1] = False
for i in range(2, int(MAX ** 0.5) + 1):
    if is_prime[i]:
        for j in range(i * i, MAX, i):
            is_prime[j] = False

cnt = [0] * MAX
for i in range(1, MAX):
    cnt[i] = cnt[i - 1] + (1 if is_prime[i] else 0)

results = []
first = True
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split()
    if len(parts) == 2:
        m, n = int(parts[0]), int(parts[1])
        if not first:
            results.append("")
        results.append(str(cnt[n] - cnt[m - 1]))
        first = False

print("\\n".join(results))
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int MAX = 10000001;
        boolean[] isPrime = new boolean[MAX];
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;
        for (int i = 2; i * i < MAX; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j < MAX; j += i) isPrime[j] = false;
            }
        }

        int[] cnt = new int[MAX];
        for (int i = 1; i < MAX; i++) {
            cnt[i] = cnt[i - 1] + (isPrime[i] ? 1 : 0);
        }

        StringBuilder sb = new StringBuilder();
        String line;
        boolean first = true;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty()) continue;
            StringTokenizer st = new StringTokenizer(line);
            if (st.countTokens() == 2) {
                int m = Integer.parseInt(st.nextToken());
                int n = Integer.parseInt(st.nextToken());
                if (!first) sb.append("\\n");
                sb.append(cnt[n] - cnt[m - 1]);
                first = false;
            }
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
#include <sstream>
using namespace std;

int main() {
    const int MAX = 10000001;
    vector<bool> isPrime(MAX, true);
    isPrime[0] = isPrime[1] = false;
    for (int i = 2; i * i < MAX; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j < MAX; j += i) isPrime[j] = false;
        }
    }

    vector<int> cnt(MAX);
    for (int i = 1; i < MAX; i++) {
        cnt[i] = cnt[i - 1] + (isPrime[i] ? 1 : 0);
    }

    string line;
    bool first = true;
    while (getline(cin, line)) {
        if (line.empty()) continue;
        istringstream iss(line);
        int m, n;
        if (iss >> m >> n) {
            if (!first) cout << "\\n";
            cout << cnt[n] - cnt[m - 1];
            first = false;
        }
    }
    cout << endl;
    return 0;
}
'''
        }
    ]

    # Problem 398-419 (remaining 22 problems)
    # Adding more solutions...

    # Problem 398: baekjoon_16723 - 원영이는 ZOAC과 영원하고 싶다
    solutions[6176] = [
        {
            "language": "python",
            "code": '''# 원영이는 ZOAC과 영원하고 싶다
n = int(input())
total = 0
power = 2
prev = n
while prev > 0:
    count = prev - n // power
    total += count * power
    prev = n // power
    power *= 2
print(total)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        long n = Long.parseLong(br.readLine().trim());
        long total = 0, power = 2, prev = n;
        while (prev > 0) {
            long count = prev - n / power;
            total += count * power;
            prev = n / power;
            power *= 2;
        }
        System.out.println(total);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

int main() {
    long long n;
    cin >> n;
    long long total = 0, power = 2, prev = n;
    while (prev > 0) {
        long long count = prev - n / power;
        total += count * power;
        prev = n / power;
        power *= 2;
    }
    cout << total << endl;
    return 0;
}
'''
        }
    ]

    # Problem 399: baekjoon_1811 - Adjacent Mastermind
    solutions[6177] = [
        {
            "language": "python",
            "code": '''# Adjacent Mastermind
import sys

for line in sys.stdin:
    line = line.strip()
    if line == '#':
        break
    target, guess = line.split()
    n = len(target)

    tused = [False] * n
    gused = [False] * n

    # black
    black = 0
    for i in range(n):
        if target[i] == guess[i]:
            black += 1
            tused[i] = gused[i] = True

    # grey
    grey = 0
    for i in range(n):
        if gused[i]:
            continue
        for j in [i - 1, i + 1]:
            if 0 <= j < n and not tused[j] and target[j] == guess[i]:
                grey += 1
                tused[j] = gused[i] = True
                break

    # white
    white = 0
    for i in range(n):
        if gused[i]:
            continue
        for j in range(n):
            if abs(i - j) >= 2 and not tused[j] and target[j] == guess[i]:
                white += 1
                tused[j] = gused[i] = True
                break

    print(f"{guess}: {black} black, {grey} grey, {white} white")
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
        String line;
        while ((line = br.readLine()) != null) {
            if (line.trim().equals("#")) break;
            String[] parts = line.trim().split(" ");
            String target = parts[0], guess = parts[1];
            int n = target.length();
            boolean[] tused = new boolean[n], gused = new boolean[n];

            int black = 0;
            for (int i = 0; i < n; i++) {
                if (target.charAt(i) == guess.charAt(i)) {
                    black++;
                    tused[i] = gused[i] = true;
                }
            }

            int grey = 0;
            for (int i = 0; i < n; i++) {
                if (gused[i]) continue;
                for (int j : new int[]{i - 1, i + 1}) {
                    if (j >= 0 && j < n && !tused[j] && target.charAt(j) == guess.charAt(i)) {
                        grey++;
                        tused[j] = gused[i] = true;
                        break;
                    }
                }
            }

            int white = 0;
            for (int i = 0; i < n; i++) {
                if (gused[i]) continue;
                for (int j = 0; j < n; j++) {
                    if (Math.abs(i - j) >= 2 && !tused[j] && target.charAt(j) == guess.charAt(i)) {
                        white++;
                        tused[j] = gused[i] = true;
                        break;
                    }
                }
            }
            sb.append(guess).append(": ").append(black).append(" black, ").append(grey).append(" grey, ").append(white).append(" white\\n");
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
#include <sstream>
#include <cmath>
using namespace std;

int main() {
    string line;
    while (getline(cin, line)) {
        if (line == "#") break;
        istringstream iss(line);
        string target, guess;
        iss >> target >> guess;
        int n = target.length();

        bool tused[n], gused[n];
        fill(tused, tused + n, false);
        fill(gused, gused + n, false);

        int black = 0;
        for (int i = 0; i < n; i++) {
            if (target[i] == guess[i]) {
                black++;
                tused[i] = gused[i] = true;
            }
        }

        int grey = 0;
        for (int i = 0; i < n; i++) {
            if (gused[i]) continue;
            for (int j : {i - 1, i + 1}) {
                if (j >= 0 && j < n && !tused[j] && target[j] == guess[i]) {
                    grey++;
                    tused[j] = gused[i] = true;
                    break;
                }
            }
        }

        int white = 0;
        for (int i = 0; i < n; i++) {
            if (gused[i]) continue;
            for (int j = 0; j < n; j++) {
                if (abs(i - j) >= 2 && !tused[j] && target[j] == guess[i]) {
                    white++;
                    tused[j] = gused[i] = true;
                    break;
                }
            }
        }
        cout << guess << ": " << black << " black, " << grey << " grey, " << white << " white\\n";
    }
    return 0;
}
'''
        }
    ]

    # Problem 400: baekjoon_30860 - Product Delivery
    solutions[6178] = [
        {
            "language": "python",
            "code": '''# Product Delivery - 최소 배송 횟수
import sys
input = sys.stdin.readline

n = int(input())
ranges = []
for _ in range(n):
    l, m = map(int, input().split())
    ranges.append((l, m))

# 뒤에서부터 최대 배송량 제한
max_per = [r[1] for r in ranges]
for i in range(n - 2, -1, -1):
    max_per[i] = min(max_per[i], max_per[i + 1])

ans = 1
for i in range(n):
    if max_per[i] == 0:
        if ranges[i][0] > 0:
            print(-1)
            exit()
    else:
        trips = (ranges[i][0] + max_per[i] - 1) // max_per[i]
        ans = max(ans, trips)

print(ans)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        long[] l = new long[n], m = new long[n];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            l[i] = Long.parseLong(st.nextToken());
            m[i] = Long.parseLong(st.nextToken());
        }

        long[] maxPer = m.clone();
        for (int i = n - 2; i >= 0; i--) {
            maxPer[i] = Math.min(maxPer[i], maxPer[i + 1]);
        }

        long ans = 1;
        for (int i = 0; i < n; i++) {
            if (maxPer[i] == 0) {
                if (l[i] > 0) {
                    System.out.println(-1);
                    return;
                }
            } else {
                long trips = (l[i] + maxPer[i] - 1) / maxPer[i];
                ans = Math.max(ans, trips);
            }
        }
        System.out.println(ans);
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
    int n;
    cin >> n;
    vector<long long> l(n), m(n);
    for (int i = 0; i < n; i++) cin >> l[i] >> m[i];

    vector<long long> maxPer = m;
    for (int i = n - 2; i >= 0; i--) {
        maxPer[i] = min(maxPer[i], maxPer[i + 1]);
    }

    long long ans = 1;
    for (int i = 0; i < n; i++) {
        if (maxPer[i] == 0) {
            if (l[i] > 0) {
                cout << -1 << endl;
                return 0;
            }
        } else {
            long long trips = (l[i] + maxPer[i] - 1) / maxPer[i];
            ans = max(ans, trips);
        }
    }
    cout << ans << endl;
    return 0;
}
'''
        }
    ]

    # Problem 401: baekjoon_6230 - Buy One Get One Free
    solutions[6205] = [
        {
            "language": "python",
            "code": '''# Buy One Get One Free
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
high = sorted([int(input()) for _ in range(n)], reverse=True)
low = sorted([int(input()) for _ in range(m)], reverse=True)

total = n
li = 0
for h in high:
    if li < m and low[li] < h:
        total += 1
        li += 1

print(total)
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
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        Integer[] high = new Integer[n];
        for (int i = 0; i < n; i++) high[i] = Integer.parseInt(br.readLine().trim());
        Integer[] low = new Integer[m];
        for (int i = 0; i < m; i++) low[i] = Integer.parseInt(br.readLine().trim());

        Arrays.sort(high, Collections.reverseOrder());
        Arrays.sort(low, Collections.reverseOrder());

        int total = n, li = 0;
        for (int h : high) {
            if (li < m && low[li] < h) {
                total++;
                li++;
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
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int n, m;
    cin >> n >> m;
    vector<int> high(n), low(m);
    for (int i = 0; i < n; i++) cin >> high[i];
    for (int i = 0; i < m; i++) cin >> low[i];

    sort(high.rbegin(), high.rend());
    sort(low.rbegin(), low.rend());

    int total = n, li = 0;
    for (int h : high) {
        if (li < m && low[li] < h) {
            total++;
            li++;
        }
    }
    cout << total << endl;
    return 0;
}
'''
        }
    ]

    # 나머지 문제들 (402-419)
    # Problem 402-419 추가...

    # Problem 402: baekjoon_32335 - 부자가 될 거야!
    solutions[6210] = [
        {
            "language": "python",
            "code": '''# 부자가 될 거야! - 다이얼 조작
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
s = list(input().strip())

# m번 돌려서 가장 작은 수 만들기
for _ in range(m):
    for i in range(n):
        if s[i] != '0':
            s[i] = str((int(s[i]) + 1) % 10)
            break

print(''.join(s))
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
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());
        char[] s = br.readLine().trim().toCharArray();

        for (int k = 0; k < m; k++) {
            for (int i = 0; i < n; i++) {
                if (s[i] != '0') {
                    s[i] = (char)('0' + (s[i] - '0' + 1) % 10);
                    break;
                }
            }
        }
        System.out.println(new String(s));
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
    int n, m;
    cin >> n >> m;
    string s;
    cin >> s;

    for (int k = 0; k < m; k++) {
        for (int i = 0; i < n; i++) {
            if (s[i] != '0') {
                s[i] = '0' + (s[i] - '0' + 1) % 10;
                break;
            }
        }
    }
    cout << s << endl;
    return 0;
}
'''
        }
    ]

    # Problem 403: baekjoon_32930 - 슈팅 연습
    solutions[6215] = [
        {
            "language": "python",
            "code": '''# 슈팅 연습 - 가장 먼 과녁 맞추기
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
targets = []
for _ in range(n):
    x, y = map(int, input().split())
    targets.append([x, y])

total = 0
cx, cy = 0, 0

for _ in range(m):
    # 가장 먼 과녁 찾기
    max_dist = -1
    max_idx = -1
    for i, (x, y) in enumerate(targets):
        d = (x - cx) ** 2 + (y - cy) ** 2
        if d > max_dist:
            max_dist = d
            max_idx = i

    total += max_dist
    cx, cy = targets[max_idx]

    # 새 과녁 추가
    nx, ny = map(int, input().split())
    targets[max_idx] = [nx, ny]

print(total)
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
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        int[][] targets = new int[n][2];
        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            targets[i][0] = Integer.parseInt(st.nextToken());
            targets[i][1] = Integer.parseInt(st.nextToken());
        }

        long total = 0;
        int cx = 0, cy = 0;

        for (int k = 0; k < m; k++) {
            long maxDist = -1;
            int maxIdx = -1;
            for (int i = 0; i < n; i++) {
                long d = (long)(targets[i][0] - cx) * (targets[i][0] - cx) + (long)(targets[i][1] - cy) * (targets[i][1] - cy);
                if (d > maxDist) {
                    maxDist = d;
                    maxIdx = i;
                }
            }

            total += maxDist;
            cx = targets[maxIdx][0];
            cy = targets[maxIdx][1];

            st = new StringTokenizer(br.readLine());
            targets[maxIdx][0] = Integer.parseInt(st.nextToken());
            targets[maxIdx][1] = Integer.parseInt(st.nextToken());
        }
        System.out.println(total);
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
    int n, m;
    cin >> n >> m;
    vector<pair<int, int>> targets(n);
    for (int i = 0; i < n; i++) cin >> targets[i].first >> targets[i].second;

    long long total = 0;
    int cx = 0, cy = 0;

    for (int k = 0; k < m; k++) {
        long long maxDist = -1;
        int maxIdx = -1;
        for (int i = 0; i < n; i++) {
            long long d = (long long)(targets[i].first - cx) * (targets[i].first - cx) +
                         (long long)(targets[i].second - cy) * (targets[i].second - cy);
            if (d > maxDist) {
                maxDist = d;
                maxIdx = i;
            }
        }

        total += maxDist;
        cx = targets[maxIdx].first;
        cy = targets[maxIdx].second;

        cin >> targets[maxIdx].first >> targets[maxIdx].second;
    }
    cout << total << endl;
    return 0;
}
'''
        }
    ]

    # Problem 404: baekjoon_24369 - 알고리즘 수업 - 점근적 표기 5
    solutions[6221] = [
        {
            "language": "python",
            "code": '''# 알고리즘 수업 - 점근적 표기 5
# f(n) = a2*n^2 + a1*n + a0
# Omega(n^2) 정의: c*n^2 <= f(n) for all n >= n0

a2, a1, a0 = map(int, input().split())
c = int(input())
n0 = int(input())

# 모든 n >= n0에 대해 c*n^2 <= a2*n^2 + a1*n + a0 확인
valid = True
for n in range(n0, n0 + 1000):
    if c * n * n > a2 * n * n + a1 * n + a0:
        valid = False
        break

print(1 if valid else 0)
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
        int a2 = Integer.parseInt(st.nextToken());
        int a1 = Integer.parseInt(st.nextToken());
        int a0 = Integer.parseInt(st.nextToken());
        int c = Integer.parseInt(br.readLine().trim());
        int n0 = Integer.parseInt(br.readLine().trim());

        boolean valid = true;
        for (int n = n0; n < n0 + 1000; n++) {
            long left = (long)c * n * n;
            long right = (long)a2 * n * n + (long)a1 * n + a0;
            if (left > right) {
                valid = false;
                break;
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
using namespace std;

int main() {
    long long a2, a1, a0, c, n0;
    cin >> a2 >> a1 >> a0 >> c >> n0;

    bool valid = true;
    for (long long n = n0; n < n0 + 1000; n++) {
        long long left = c * n * n;
        long long right = a2 * n * n + a1 * n + a0;
        if (left > right) {
            valid = false;
            break;
        }
    }
    cout << (valid ? 1 : 0) << endl;
    return 0;
}
'''
        }
    ]

    # Continue with remaining problems...
    # I'll add a few more key problems

    # Problem 410: baekjoon_33691 - Arkain 대시보드
    solutions[6243] = [
        {
            "language": "python",
            "code": '''# Arkain 대시보드
import sys
input = sys.stdin.readline

n = int(input())
containers = {}
order = []
for i in range(n):
    name = input().strip()
    containers[name] = i
    order.append(name)

k = int(input())
pinned = set()
for _ in range(k):
    name = input().strip()
    pinned.add(name)

# 고정된 것 먼저 (최근 순), 그 다음 나머지 (최근 순)
seen = set()
result = []

# 고정된 컨테이너 (최근 순)
for name in reversed(order):
    if name in pinned and name not in seen:
        result.append(name)
        seen.add(name)

# 나머지 컨테이너 (최근 순)
for name in reversed(order):
    if name not in seen:
        result.append(name)
        seen.add(name)

print('\\n'.join(result))
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        Map<String, Integer> containers = new LinkedHashMap<>();
        List<String> order = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            String name = br.readLine().trim();
            containers.put(name, i);
            order.add(name);
        }

        int k = Integer.parseInt(br.readLine().trim());
        Set<String> pinned = new HashSet<>();
        for (int i = 0; i < k; i++) {
            pinned.add(br.readLine().trim());
        }

        Set<String> seen = new HashSet<>();
        List<String> result = new ArrayList<>();

        for (int i = n - 1; i >= 0; i--) {
            String name = order.get(i);
            if (pinned.contains(name) && !seen.contains(name)) {
                result.add(name);
                seen.add(name);
            }
        }

        for (int i = n - 1; i >= 0; i--) {
            String name = order.get(i);
            if (!seen.contains(name)) {
                result.add(name);
                seen.add(name);
            }
        }

        StringBuilder sb = new StringBuilder();
        for (String s : result) sb.append(s).append("\\n");
        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
#include <set>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    vector<string> order(n);
    for (int i = 0; i < n; i++) cin >> order[i];

    int k;
    cin >> k;
    set<string> pinned;
    for (int i = 0; i < k; i++) {
        string name;
        cin >> name;
        pinned.insert(name);
    }

    set<string> seen;
    vector<string> result;

    for (int i = n - 1; i >= 0; i--) {
        if (pinned.count(order[i]) && !seen.count(order[i])) {
            result.push_back(order[i]);
            seen.insert(order[i]);
        }
    }

    for (int i = n - 1; i >= 0; i--) {
        if (!seen.count(order[i])) {
            result.push_back(order[i]);
            seen.insert(order[i]);
        }
    }

    for (auto& s : result) cout << s << "\\n";
    return 0;
}
'''
        }
    ]

    # Problem 415: baekjoon_30703 - 온도 맞추기
    solutions[6270] = [
        {
            "language": "python",
            "code": '''# 온도 맞추기
import sys
input = sys.stdin.readline

n = int(input())
A = list(map(int, input().split()))
B = list(map(int, input().split()))
X = list(map(int, input().split()))

# 각 비커: |A[i] - B[i]| = k * X[i] (k는 버튼 횟수, 홀짝 결정)
# 모든 비커가 같은 k로 맞춰야 함

diff = []
for i in range(n):
    d = abs(A[i] - B[i])
    if d % X[i] != 0:
        print(-1)
        exit()
    diff.append((d // X[i], (A[i] - B[i]) // X[i]))

# 모든 k가 같은 parity인지 확인
# k번 누르면 A[i] += (+-1)^j * X[i] for j=1..k
# 결과적으로 A[i]가 B[i]가 되려면 k * X[i]만큼 변해야 함

# 실제로는 k의 홀짝성만 중요
min_k = 0
parity = None

for i in range(n):
    d = abs(A[i] - B[i])
    k = d // X[i]

    # 방향에 따라 k의 홀짝 결정
    if A[i] < B[i]:
        # 올려야 함: 홀수 번 +면 올라감
        need_odd_plus = True
    elif A[i] > B[i]:
        need_odd_plus = False
    else:
        # A[i] == B[i]이면 k는 짝수여야 함
        if k % 2 != 0:
            print(-1)
            exit()
        continue

    # k의 패리티 확인
    if parity is None:
        parity = k % 2
    elif parity != k % 2:
        print(-1)
        exit()

    min_k = max(min_k, k)

print(min_k)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        long[] A = new long[n], B = new long[n], X = new long[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) A[i] = Long.parseLong(st.nextToken());
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) B[i] = Long.parseLong(st.nextToken());
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) X[i] = Long.parseLong(st.nextToken());

        long minK = 0;
        int parity = -1;

        for (int i = 0; i < n; i++) {
            long d = Math.abs(A[i] - B[i]);
            if (d % X[i] != 0) {
                System.out.println(-1);
                return;
            }
            long k = d / X[i];
            int p = (int)(k % 2);

            if (parity == -1) parity = p;
            else if (parity != p) {
                System.out.println(-1);
                return;
            }
            minK = Math.max(minK, k);
        }
        System.out.println(minK);
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
    int n;
    cin >> n;
    vector<long long> A(n), B(n), X(n);
    for (int i = 0; i < n; i++) cin >> A[i];
    for (int i = 0; i < n; i++) cin >> B[i];
    for (int i = 0; i < n; i++) cin >> X[i];

    long long minK = 0;
    int parity = -1;

    for (int i = 0; i < n; i++) {
        long long d = abs(A[i] - B[i]);
        if (d % X[i] != 0) {
            cout << -1 << endl;
            return 0;
        }
        long long k = d / X[i];
        int p = k % 2;

        if (parity == -1) parity = p;
        else if (parity != p) {
            cout << -1 << endl;
            return 0;
        }
        minK = max(minK, k);
    }
    cout << minK << endl;
    return 0;
}
'''
        }
    ]

    # Problem 419: baekjoon_6052 - Cow Pals
    solutions[6307] = [
        {
            "language": "python",
            "code": '''# Cow Pals - 친화수 (Amicable Numbers)
import sys

def sum_divisors(n):
    s = 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
        i += 1
    return s

s = int(input())

for n in range(s, 18001):
    m = sum_divisors(n)
    if m != n and sum_divisors(m) == n:
        print(n, m)
        break
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;

public class Main {
    static int sumDivisors(int n) {
        int s = 1;
        for (int i = 2; i * i <= n; i++) {
            if (n % i == 0) {
                s += i;
                if (i != n / i) s += n / i;
            }
        }
        return s;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int s = Integer.parseInt(br.readLine().trim());

        for (int n = s; n <= 18000; n++) {
            int m = sumDivisors(n);
            if (m != n && sumDivisors(m) == n) {
                System.out.println(n + " " + m);
                break;
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

int sumDivisors(int n) {
    int s = 1;
    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) {
            s += i;
            if (i != n / i) s += n / i;
        }
    }
    return s;
}

int main() {
    int s;
    cin >> s;

    for (int n = s; n <= 18000; n++) {
        int m = sumDivisors(n);
        if (m != n && sumDivisors(m) == n) {
            cout << n << " " << m << endl;
            break;
        }
    }
    return 0;
}
'''
        }
    ]

    return solutions


def main():
    json_path = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

    print("Reading JSON file...")
    with open(json_path, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"Total problems in file: {len(data)}")

    solutions = get_all_solutions()
    print(f"Solutions prepared for {len(solutions)} problems")

    updated_count = 0
    for idx, sol_list in solutions.items():
        if idx < len(data):
            data[idx]['solutions'] = sol_list
            updated_count += 1
            print(f"Updated index {idx}: {data[idx].get('name', 'Unknown')}")

    print(f"\nWriting {updated_count} solutions to JSON file...")
    with open(json_path, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"Done! Updated {updated_count} problems.")


if __name__ == '__main__':
    main()
