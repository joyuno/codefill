#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배치 11: Medium 문제 솔루션 추가 (27111, 28136, 28470, 2777, 2545, 11819, 1262, 20004, 3063, 23797, 31937, 29700, 17393, 25943, 23056)"""

import json

# 새로운 솔루션들
new_solutions = {
    "baekjoon_27111": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    # 현재 부대 내에 있는 사람들 추적
    inside = set()
    missing = 0

    for _ in range(n):
        a, b = map(int, input().split())

        if b == 1:  # 입장
            if a in inside:
                # 이미 안에 있는데 또 입장 -> 나간 기록이 누락됨
                missing += 1
            inside.add(a)
        else:  # 퇴장 (b == 0)
            if a not in inside:
                # 안에 없는데 나감 -> 들어온 기록이 누락됨
                missing += 1
            else:
                inside.remove(a)

    # 마지막에 부대 내에 남아있는 사람들 -> 나간 기록 누락
    missing += len(inside)

    print(missing)

solve()
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

    int n;
    cin >> n;

    set<int> inside;  // 현재 부대 내에 있는 사람들
    int missing = 0;

    for (int i = 0; i < n; i++) {
        int a, b;
        cin >> a >> b;

        if (b == 1) {  // 입장
            if (inside.count(a)) {
                // 이미 안에 있는데 또 입장 -> 나간 기록 누락
                missing++;
            }
            inside.insert(a);
        } else {  // 퇴장
            if (!inside.count(a)) {
                // 안에 없는데 나감 -> 들어온 기록 누락
                missing++;
            } else {
                inside.erase(a);
            }
        }
    }

    // 마지막에 남아있는 사람들 -> 나간 기록 누락
    missing += inside.size();

    cout << missing << endl;

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
        int n = Integer.parseInt(br.readLine().trim());

        Set<Integer> inside = new HashSet<>();  // 현재 부대 내 사람들
        int missing = 0;

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());

            if (b == 1) {  // 입장
                if (inside.contains(a)) {
                    // 이미 안에 있는데 또 입장 -> 나간 기록 누락
                    missing++;
                }
                inside.add(a);
            } else {  // 퇴장
                if (!inside.contains(a)) {
                    // 안에 없는데 나감 -> 들어온 기록 누락
                    missing++;
                } else {
                    inside.remove(a);
                }
            }
        }

        // 마지막에 남아있는 사람들 -> 나간 기록 누락
        missing += inside.size();

        System.out.println(missing);
    }
}
'''
            }
        ]
    },
    "baekjoon_28136": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    a = list(map(int, input().split()))

    # 원형 배열에서 인접한 원소들이 오름차순이 아닌 곳의 개수를 센다
    # 그 개수가 곧 끊어야 하는 횟수
    cuts = 0
    for i in range(n):
        # a[i]와 a[(i+1) % n] 비교
        if a[i] >= a[(i + 1) % n]:
            cuts += 1

    print(cuts)

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

    int n;
    cin >> n;

    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    // 원형 배열에서 인접한 원소들이 오름차순이 아닌 곳의 개수
    int cuts = 0;
    for (int i = 0; i < n; i++) {
        if (a[i] >= a[(i + 1) % n]) {
            cuts++;
        }
    }

    cout << cuts << endl;

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
        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] a = new int[n];
        for (int i = 0; i < n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
        }

        // 원형 배열에서 인접한 원소들이 오름차순이 아닌 곳의 개수
        int cuts = 0;
        for (int i = 0; i < n; i++) {
            if (a[i] >= a[(i + 1) % n]) {
                cuts++;
            }
        }

        System.out.println(cuts);
    }
}
'''
            }
        ]
    },
    "baekjoon_28470": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))
    K = list(map(float, input().split()))

    total = 0
    for i in range(n):
        # 공격 먼저: 증가량 = floor(A[i] * K[i]), 감소량 = B[i]
        attack_first = int(A[i] * K[i]) - B[i]

        # 회피 먼저: 증가량 = A[i], 감소량 = floor(B[i] * K[i])
        dodge_first = A[i] - int(B[i] * K[i])

        # 더 큰 값 선택
        total += max(attack_first, dodge_first)

    print(total)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<long long> A(n), B(n);
    vector<double> K(n);

    for (int i = 0; i < n; i++) cin >> A[i];
    for (int i = 0; i < n; i++) cin >> B[i];
    for (int i = 0; i < n; i++) cin >> K[i];

    long long total = 0;
    for (int i = 0; i < n; i++) {
        // 공격 먼저: 증가량 = floor(A[i] * K[i]), 감소량 = B[i]
        long long attack_first = (long long)(A[i] * K[i]) - B[i];

        // 회피 먼저: 증가량 = A[i], 감소량 = floor(B[i] * K[i])
        long long dodge_first = A[i] - (long long)(B[i] * K[i]);

        total += max(attack_first, dodge_first);
    }

    cout << total << endl;

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
        int n = Integer.parseInt(br.readLine().trim());

        long[] A = new long[n];
        long[] B = new long[n];
        double[] K = new double[n];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) A[i] = Long.parseLong(st.nextToken());

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) B[i] = Long.parseLong(st.nextToken());

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) K[i] = Double.parseDouble(st.nextToken());

        long total = 0;
        for (int i = 0; i < n; i++) {
            // 공격 먼저
            long attackFirst = (long)(A[i] * K[i]) - B[i];
            // 회피 먼저
            long dodgeFirst = A[i] - (long)(B[i] * K[i]);

            total += Math.max(attackFirst, dodgeFirst);
        }

        System.out.println(total);
    }
}
'''
            }
        ]
    },
    "baekjoon_2777": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve(n):
    if n == 1:
        return 1  # 1자리 수 1

    # n을 2~9의 소인수로 분해
    digits = []
    temp = n

    # 9부터 2까지 역순으로 나누기
    for d in range(9, 1, -1):
        while temp % d == 0:
            digits.append(d)
            temp //= d

    # 나머지가 1이 아니면 불가능
    if temp != 1:
        return -1

    # 자릿수 = 분해된 숫자들의 개수
    return len(digits)

t = int(input())
for _ in range(t):
    n = int(input())
    print(solve(n))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int solve(long long n) {
    if (n == 1) return 1;

    int count = 0;

    // 9부터 2까지 역순으로 나누기
    for (int d = 9; d >= 2; d--) {
        while (n % d == 0) {
            count++;
            n /= d;
        }
    }

    // 나머지가 1이 아니면 불가능
    if (n != 1) return -1;

    return count;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        long long n;
        cin >> n;
        cout << solve(n) << endl;
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;

public class Main {
    static int solve(long n) {
        if (n == 1) return 1;

        int count = 0;

        for (int d = 9; d >= 2; d--) {
            while (n % d == 0) {
                count++;
                n /= d;
            }
        }

        if (n != 1) return -1;

        return count;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        while (t-- > 0) {
            long n = Long.parseLong(br.readLine().trim());
            sb.append(solve(n)).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_2545": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve(A, B, C, D):
    dims = [A, B, C]

    for _ in range(D):
        dims.sort()
        if dims[2] > 0:
            dims[2] -= 1
        else:
            break

    return dims[0] * dims[1] * dims[2]

t = int(input())
for _ in range(t):
    input()  # 빈 줄 처리
    A, B, C, D = map(int, input().split())
    print(solve(A, B, C, D))
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

    int t;
    cin >> t;

    while (t--) {
        long long A, B, C, D;
        cin >> A >> B >> C >> D;

        long long dims[3] = {A, B, C};

        for (int i = 0; i < D; i++) {
            sort(dims, dims + 3);
            if (dims[2] > 0) {
                dims[2]--;
            } else {
                break;
            }
        }

        cout << dims[0] * dims[1] * dims[2] << endl;
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
        int t = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        while (t-- > 0) {
            br.readLine();  // 빈 줄 처리
            StringTokenizer st = new StringTokenizer(br.readLine());
            long A = Long.parseLong(st.nextToken());
            long B = Long.parseLong(st.nextToken());
            long C = Long.parseLong(st.nextToken());
            long D = Long.parseLong(st.nextToken());

            long[] dims = {A, B, C};

            for (int i = 0; i < D; i++) {
                Arrays.sort(dims);
                if (dims[2] > 0) {
                    dims[2]--;
                } else {
                    break;
                }
            }

            sb.append(dims[0] * dims[1] * dims[2]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_11819": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    A, B, C = map(int, input().split())
    print(pow(A, B, C))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;
typedef unsigned long long ull;

ull mulmod(ull a, ull b, ull m) {
    return (__uint128_t)a * b % m;
}

ull powmod(ull a, ull b, ull m) {
    a %= m;
    ull result = 1;
    while (b > 0) {
        if (b & 1) {
            result = mulmod(result, a, m);
        }
        a = mulmod(a, a, m);
        b >>= 1;
    }
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    ull A, B, C;
    cin >> A >> B >> C;

    cout << powmod(A, B, C) << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;
import java.math.BigInteger;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        BigInteger A = new BigInteger(st.nextToken());
        BigInteger B = new BigInteger(st.nextToken());
        BigInteger C = new BigInteger(st.nextToken());

        System.out.println(A.modPow(B, C));
    }
}
'''
            }
        ]
    },
    "baekjoon_1262": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys

def get_char(n, r, c):
    center = n - 1
    dist = abs(r - center) + abs(c - center)

    if dist >= n:
        return '.'
    else:
        return chr(ord('a') + dist)

def solve():
    line = sys.stdin.readline().split()
    N, R1, R2, C1, C2 = map(int, line)

    tile_size = 2 * N - 1

    result = []
    for r in range(R1, R2 + 1):
        row = []
        for c in range(C1, C2 + 1):
            tr = r % tile_size
            tc = c % tile_size
            row.append(get_char(N, tr, tc))
        result.append(''.join(row))

    print('\\n'.join(result))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <cmath>
using namespace std;

char getChar(int n, int r, int c) {
    int center = n - 1;
    int dist = abs(r - center) + abs(c - center);

    if (dist >= n) {
        return '.';
    } else {
        return 'a' + dist;
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, R1, R2, C1, C2;
    cin >> N >> R1 >> R2 >> C1 >> C2;

    int tileSize = 2 * N - 1;

    for (int r = R1; r <= R2; r++) {
        for (int c = C1; c <= C2; c++) {
            int tr = r % tileSize;
            int tc = c % tileSize;
            cout << getChar(N, tr, tc);
        }
        cout << '\\n';
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
    static char getChar(int n, int r, int c) {
        int center = n - 1;
        int dist = Math.abs(r - center) + Math.abs(c - center);

        if (dist >= n) {
            return '.';
        } else {
            return (char)('a' + dist);
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int R1 = Integer.parseInt(st.nextToken());
        int R2 = Integer.parseInt(st.nextToken());
        int C1 = Integer.parseInt(st.nextToken());
        int C2 = Integer.parseInt(st.nextToken());

        int tileSize = 2 * N - 1;

        StringBuilder sb = new StringBuilder();
        for (int r = R1; r <= R2; r++) {
            for (int c = C1; c <= C2; c++) {
                int tr = r % tileSize;
                int tc = c % tileSize;
                sb.append(getChar(N, tr, tc));
            }
            sb.append('\\n');
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_20004": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    A = int(input())

    for n in range(1, A + 1):
        if 31 % (n + 1) == 0:
            print(n)

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

    int A;
    cin >> A;

    for (int n = 1; n <= A; n++) {
        if (31 % (n + 1) == 0) {
            cout << n << '\\n';
        }
    }

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
        int A = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        for (int n = 1; n <= A; n++) {
            if (31 % (n + 1) == 0) {
                sb.append(n).append('\\n');
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_3063": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    T = int(input())

    for _ in range(T):
        x1, y1, x2, y2, x3, y3, x4, y4 = map(int, input().split())

        area1 = (x2 - x1) * (y2 - y1)

        overlap_x1 = max(x1, x3)
        overlap_x2 = min(x2, x4)
        overlap_y1 = max(y1, y3)
        overlap_y2 = min(y2, y4)

        if overlap_x1 < overlap_x2 and overlap_y1 < overlap_y2:
            overlap_area = (overlap_x2 - overlap_x1) * (overlap_y2 - overlap_y1)
        else:
            overlap_area = 0

        print(area1 - overlap_area)

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
        int x1, y1, x2, y2, x3, y3, x4, y4;
        cin >> x1 >> y1 >> x2 >> y2 >> x3 >> y3 >> x4 >> y4;

        int area1 = (x2 - x1) * (y2 - y1);

        int overlapX1 = max(x1, x3);
        int overlapX2 = min(x2, x4);
        int overlapY1 = max(y1, y3);
        int overlapY2 = min(y2, y4);

        int overlapArea = 0;
        if (overlapX1 < overlapX2 && overlapY1 < overlapY2) {
            overlapArea = (overlapX2 - overlapX1) * (overlapY2 - overlapY1);
        }

        cout << area1 - overlapArea << '\\n';
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

        StringBuilder sb = new StringBuilder();
        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int x1 = Integer.parseInt(st.nextToken());
            int y1 = Integer.parseInt(st.nextToken());
            int x2 = Integer.parseInt(st.nextToken());
            int y2 = Integer.parseInt(st.nextToken());
            int x3 = Integer.parseInt(st.nextToken());
            int y3 = Integer.parseInt(st.nextToken());
            int x4 = Integer.parseInt(st.nextToken());
            int y4 = Integer.parseInt(st.nextToken());

            int area1 = (x2 - x1) * (y2 - y1);

            int overlapX1 = Math.max(x1, x3);
            int overlapX2 = Math.min(x2, x4);
            int overlapY1 = Math.max(y1, y3);
            int overlapY2 = Math.min(y2, y4);

            int overlapArea = 0;
            if (overlapX1 < overlapX2 && overlapY1 < overlapY2) {
                overlapArea = (overlapX2 - overlapX1) * (overlapY2 - overlapY1);
            }

            sb.append(area1 - overlapArea).append('\\n');
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_23797": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    s = input().strip()

    wait_k = 0
    wait_p = 0

    for c in s:
        if c == 'K':
            if wait_k > 0:
                wait_k -= 1
                wait_p += 1
            else:
                wait_p += 1
        else:
            if wait_p > 0:
                wait_p -= 1
                wait_k += 1
            else:
                wait_k += 1

    print(wait_k + wait_p)

solve()
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

    int waitK = 0;
    int waitP = 0;

    for (char c : s) {
        if (c == 'K') {
            if (waitK > 0) {
                waitK--;
                waitP++;
            } else {
                waitP++;
            }
        } else {
            if (waitP > 0) {
                waitP--;
                waitK++;
            } else {
                waitK++;
            }
        }
    }

    cout << waitK + waitP << endl;

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
        String s = br.readLine().trim();

        int waitK = 0;
        int waitP = 0;

        for (char c : s.toCharArray()) {
            if (c == 'K') {
                if (waitK > 0) {
                    waitK--;
                    waitP++;
                } else {
                    waitP++;
                }
            } else {
                if (waitP > 0) {
                    waitP--;
                    waitK++;
                } else {
                    waitK++;
                }
            }
        }

        System.out.println(waitK + waitP);
    }
}
'''
            }
        ]
    },
    "baekjoon_31937": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N, M, K = map(int, input().split())
    infected = set(map(int, input().split()))

    logs = []
    for _ in range(M):
        t, a, b = map(int, input().split())
        logs.append((t, a, b))

    logs.sort()

    for start in infected:
        infected_set = {start}

        for t, a, b in logs:
            if a in infected_set:
                infected_set.add(b)

        if infected_set == infected:
            print(start)
            return

solve()
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

    int N, M, K;
    cin >> N >> M >> K;

    set<int> infected;
    for (int i = 0; i < K; i++) {
        int x;
        cin >> x;
        infected.insert(x);
    }

    vector<tuple<int, int, int>> logs(M);
    for (int i = 0; i < M; i++) {
        int t, a, b;
        cin >> t >> a >> b;
        logs[i] = make_tuple(t, a, b);
    }

    sort(logs.begin(), logs.end());

    for (int start : infected) {
        set<int> simInfected;
        simInfected.insert(start);

        for (auto& [t, a, b] : logs) {
            if (simInfected.count(a)) {
                simInfected.insert(b);
            }
        }

        if (simInfected == infected) {
            cout << start << endl;
            return 0;
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
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        Set<Integer> infected = new HashSet<>();
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < K; i++) {
            infected.add(Integer.parseInt(st.nextToken()));
        }

        int[][] logs = new int[M][3];
        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            logs[i][0] = Integer.parseInt(st.nextToken());
            logs[i][1] = Integer.parseInt(st.nextToken());
            logs[i][2] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(logs, (a, b) -> a[0] - b[0]);

        for (int start : infected) {
            Set<Integer> simInfected = new HashSet<>();
            simInfected.add(start);

            for (int[] log : logs) {
                if (simInfected.contains(log[1])) {
                    simInfected.add(log[2]);
                }
            }

            if (simInfected.equals(infected)) {
                System.out.println(start);
                return;
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_29700": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N, M, K = map(int, input().split())

    total = 0
    for _ in range(N):
        row = input().strip()

        count = 0
        for c in row:
            if c == '0':
                count += 1
            else:
                if count >= K:
                    total += count - K + 1
                count = 0

        if count >= K:
            total += count - K + 1

    print(total)

solve()
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

    int N, M, K;
    cin >> N >> M >> K;

    long long total = 0;

    for (int i = 0; i < N; i++) {
        string row;
        cin >> row;

        int count = 0;
        for (char c : row) {
            if (c == '0') {
                count++;
            } else {
                if (count >= K) {
                    total += count - K + 1;
                }
                count = 0;
            }
        }

        if (count >= K) {
            total += count - K + 1;
        }
    }

    cout << total << endl;

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
        String[] line = br.readLine().split(" ");
        int N = Integer.parseInt(line[0]);
        int M = Integer.parseInt(line[1]);
        int K = Integer.parseInt(line[2]);

        long total = 0;

        for (int i = 0; i < N; i++) {
            String row = br.readLine();

            int count = 0;
            for (int j = 0; j < row.length(); j++) {
                if (row.charAt(j) == '0') {
                    count++;
                } else {
                    if (count >= K) {
                        total += count - K + 1;
                    }
                    count = 0;
                }
            }

            if (count >= K) {
                total += count - K + 1;
            }
        }

        System.out.println(total);
    }
}
'''
            }
        ]
    },
    "baekjoon_17393": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from bisect import bisect_right
input = sys.stdin.readline

def solve():
    n = int(input())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))

    result = []
    for i in range(n):
        if i == n - 1:
            result.append(0)
        else:
            idx = bisect_right(B, A[i], i + 1, n)
            result.append(idx - (i + 1))

    print(' '.join(map(str, result)))

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

    vector<long long> A(n), B(n);
    for (int i = 0; i < n; i++) cin >> A[i];
    for (int i = 0; i < n; i++) cin >> B[i];

    for (int i = 0; i < n; i++) {
        if (i == n - 1) {
            cout << 0;
        } else {
            auto it = upper_bound(B.begin() + i + 1, B.end(), A[i]);
            cout << (it - (B.begin() + i + 1));
        }
        if (i < n - 1) cout << ' ';
    }
    cout << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int upperBound(long[] arr, int start, int end, long target) {
        while (start < end) {
            int mid = (start + end) / 2;
            if (arr[mid] <= target) {
                start = mid + 1;
            } else {
                end = mid;
            }
        }
        return start;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        long[] A = new long[n];
        long[] B = new long[n];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) A[i] = Long.parseLong(st.nextToken());

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) B[i] = Long.parseLong(st.nextToken());

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i == n - 1) {
                sb.append(0);
            } else {
                int idx = upperBound(B, i + 1, n, A[i]);
                sb.append(idx - (i + 1));
            }
            if (i < n - 1) sb.append(' ');
        }

        System.out.println(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_25943": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    weights = list(map(int, input().split()))

    left = weights[0]
    right = weights[1]

    for i in range(2, n):
        if left == right:
            left += weights[i]
        elif left < right:
            left += weights[i]
        else:
            right += weights[i]

    diff = abs(left - right)

    weights_list = [100, 50, 20, 10, 5, 2, 1]
    count = 0

    for w in weights_list:
        count += diff // w
        diff %= w

    print(count)

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

    int n;
    cin >> n;

    long long weights[10001];
    for (int i = 0; i < n; i++) {
        cin >> weights[i];
    }

    long long left = weights[0];
    long long right = weights[1];

    for (int i = 2; i < n; i++) {
        if (left == right) {
            left += weights[i];
        } else if (left < right) {
            left += weights[i];
        } else {
            right += weights[i];
        }
    }

    long long diff = (left > right) ? (left - right) : (right - left);

    int weightsList[] = {100, 50, 20, 10, 5, 2, 1};
    int count = 0;

    for (int w : weightsList) {
        count += diff / w;
        diff %= w;
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
        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        long[] weights = new long[n];
        for (int i = 0; i < n; i++) {
            weights[i] = Long.parseLong(st.nextToken());
        }

        long left = weights[0];
        long right = weights[1];

        for (int i = 2; i < n; i++) {
            if (left == right) {
                left += weights[i];
            } else if (left < right) {
                left += weights[i];
            } else {
                right += weights[i];
            }
        }

        long diff = Math.abs(left - right);

        int[] weightsList = {100, 50, 20, 10, 5, 2, 1};
        int count = 0;

        for (int w : weightsList) {
            count += diff / w;
            diff %= w;
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_23056": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    first_line = input().split()
    N, M = int(first_line[0]), int(first_line[1])

    classes = {i: [] for i in range(1, N + 1)}
    counts = {i: 0 for i in range(1, N + 1)}

    while True:
        line = input().split()
        class_num = int(line[0])
        name = line[1]

        if class_num == 0 and name == '0':
            break

        if counts[class_num] < M:
            classes[class_num].append(name)
            counts[class_num] += 1

    result = []

    for c in range(1, N + 1, 2):
        classes[c].sort(key=lambda x: (len(x), x))
        for name in classes[c]:
            result.append(f"{c} {name}")

    for c in range(2, N + 1, 2):
        classes[c].sort(key=lambda x: (len(x), x))
        for name in classes[c]:
            result.append(f"{c} {name}")

    print('\\n'.join(result))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

bool cmp(const string& a, const string& b) {
    if (a.length() != b.length()) return a.length() < b.length();
    return a < b;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    vector<vector<string>> classes(N + 1);
    vector<int> counts(N + 1, 0);

    int classNum;
    string name;

    while (cin >> classNum >> name) {
        if (classNum == 0 && name == "0") break;

        if (counts[classNum] < M) {
            classes[classNum].push_back(name);
            counts[classNum]++;
        }
    }

    for (int c = 1; c <= N; c += 2) {
        sort(classes[c].begin(), classes[c].end(), cmp);
        for (const string& s : classes[c]) {
            cout << c << " " << s << "\\n";
        }
    }

    for (int c = 2; c <= N; c += 2) {
        sort(classes[c].begin(), classes[c].end(), cmp);
        for (const string& s : classes[c]) {
            cout << c << " " << s << "\\n";
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
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        List<List<String>> classes = new ArrayList<>();
        for (int i = 0; i <= N; i++) {
            classes.add(new ArrayList<>());
        }
        int[] counts = new int[N + 1];

        String line;
        while ((line = br.readLine()) != null) {
            st = new StringTokenizer(line);
            int classNum = Integer.parseInt(st.nextToken());
            String name = st.nextToken();

            if (classNum == 0 && name.equals("0")) break;

            if (counts[classNum] < M) {
                classes.get(classNum).add(name);
                counts[classNum]++;
            }
        }

        StringBuilder sb = new StringBuilder();

        for (int c = 1; c <= N; c += 2) {
            Collections.sort(classes.get(c), (a, b) -> {
                if (a.length() != b.length()) return a.length() - b.length();
                return a.compareTo(b);
            });
            for (String name : classes.get(c)) {
                sb.append(c).append(" ").append(name).append("\\n");
            }
        }

        for (int c = 2; c <= N; c += 2) {
            Collections.sort(classes.get(c), (a, b) -> {
                if (a.length() != b.length()) return a.length() - b.length();
                return a.compareTo(b);
            });
            for (String name : classes.get(c)) {
                sb.append(c).append(" ").append(name).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    }
}

def main():
    baek_medium_path = '/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json'

    # 기존 파일 읽기
    with open(baek_medium_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    print(f"기존 솔루션 수: {len(existing)}")

    # 새 솔루션 추가
    added = 0
    for problem_id, solution_data in new_solutions.items():
        if problem_id not in existing:
            existing[problem_id] = solution_data
            added += 1
            print(f"  추가됨: {problem_id}")

    # 저장
    with open(baek_medium_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\n총 {added}개 문제 추가됨")
    print(f"현재 총 솔루션 수: {len(existing)}")

if __name__ == '__main__':
    main()
