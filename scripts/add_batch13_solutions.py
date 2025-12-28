#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배치 13: Medium 문제 솔루션 추가"""

import json

new_solutions = {
    "baekjoon_15464": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    perm = list(map(int, input().split()))
    ids = list(map(int, input().split()))

    # perm[i]는 i+1번 소가 이동할 위치
    # 결과 배열에서 perm[i]-1 위치에 ids[i] 배치
    result = [0] * N
    for i in range(N):
        result[perm[i] - 1] = ids[i]

    for x in result:
        print(x)

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

    int N;
    cin >> N;

    vector<int> perm(N), ids(N);
    for (int i = 0; i < N; i++) cin >> perm[i];
    for (int i = 0; i < N; i++) cin >> ids[i];

    vector<int> result(N);
    for (int i = 0; i < N; i++) {
        result[perm[i] - 1] = ids[i];
    }

    for (int x : result) {
        cout << x << "\\n";
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
        int[] perm = new int[N];
        for (int i = 0; i < N; i++) perm[i] = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        int[] ids = new int[N];
        for (int i = 0; i < N; i++) ids[i] = Integer.parseInt(st.nextToken());

        int[] result = new int[N];
        for (int i = 0; i < N; i++) {
            result[perm[i] - 1] = ids[i];
        }

        StringBuilder sb = new StringBuilder();
        for (int x : result) {
            sb.append(x).append("\\n");
        }
        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_25710": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def digit_sum(n):
    s = 0
    while n > 0:
        s += n % 10
        n //= 10
    return s

def solve():
    N = int(input())
    a = list(map(int, input().split()))

    max_score = 0
    for i in range(N):
        for j in range(i + 1, N):
            product = a[i] * a[j]
            score = digit_sum(product)
            max_score = max(max_score, score)

    print(max_score)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
using namespace std;

int digitSum(long long n) {
    int s = 0;
    while (n > 0) {
        s += n % 10;
        n /= 10;
    }
    return s;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    vector<int> a(N);
    for (int i = 0; i < N; i++) cin >> a[i];

    int maxScore = 0;
    for (int i = 0; i < N; i++) {
        for (int j = i + 1; j < N; j++) {
            long long product = (long long)a[i] * a[j];
            int score = digitSum(product);
            maxScore = max(maxScore, score);
        }
    }

    cout << maxScore << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int digitSum(long n) {
        int s = 0;
        while (n > 0) {
            s += n % 10;
            n /= 10;
        }
        return s;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] a = new int[N];
        for (int i = 0; i < N; i++) a[i] = Integer.parseInt(st.nextToken());

        int maxScore = 0;
        for (int i = 0; i < N; i++) {
            for (int j = i + 1; j < N; j++) {
                long product = (long) a[i] * a[j];
                int score = digitSum(product);
                maxScore = Math.max(maxScore, score);
            }
        }

        System.out.println(maxScore);
    }
}
'''
            }
        ]
    },
    "baekjoon_16464": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    T = int(input())

    for _ in range(T):
        N = int(input())

        # N이 연속된 양의 정수의 합으로 표현 가능한지
        # 연속된 k개의 합: k*a + k*(k-1)/2 = N
        # k*a = N - k*(k-1)/2
        # a = (N - k*(k-1)/2) / k

        can = False
        k = 2
        while k * (k - 1) // 2 < N:
            remainder = N - k * (k - 1) // 2
            if remainder % k == 0 and remainder // k > 0:
                can = True
                break
            k += 1

        if can:
            print("Gazua")
        else:
            print("GoHanGang")

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
        long long N;
        cin >> N;

        bool can = false;
        for (long long k = 2; k * (k - 1) / 2 < N; k++) {
            long long remainder = N - k * (k - 1) / 2;
            if (remainder % k == 0 && remainder / k > 0) {
                can = true;
                break;
            }
        }

        cout << (can ? "Gazua" : "GoHanGang") << "\\n";
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
        int T = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        while (T-- > 0) {
            long N = Long.parseLong(br.readLine().trim());

            boolean can = false;
            for (long k = 2; k * (k - 1) / 2 < N; k++) {
                long remainder = N - k * (k - 1) / 2;
                if (remainder % k == 0 && remainder / k > 0) {
                    can = true;
                    break;
                }
            }

            sb.append(can ? "Gazua" : "GoHanGang").append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_20117": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    a = list(map(int, input().split()))

    # 묶음의 가격 = 묶음 내 최고 품질 * 묶음 크기
    # 최대 수익을 위해: 가장 높은 품질을 최대한 많이 활용

    a.sort(reverse=True)

    total = 0
    for i in range(N):
        # i번째 높은 품질의 호반우
        # 짝 지을 수 있으면 2배, 아니면 1배
        if i < N - i - 1:
            # 아직 짝이 남아있음
            total += a[i] * 2
        elif i == N - i - 1:
            # 홀수 개일 때 가운데 원소
            total += a[i]
        # i > N - i - 1이면 이미 짝이 된 것들이므로 더하지 않음

    print(total)

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

    vector<int> a(N);
    for (int i = 0; i < N; i++) cin >> a[i];

    sort(a.begin(), a.end(), greater<int>());

    long long total = 0;
    for (int i = 0; i < N; i++) {
        if (i < N - i - 1) {
            total += a[i] * 2;
        } else if (i == N - i - 1) {
            total += a[i];
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
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        Integer[] a = new Integer[N];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) a[i] = Integer.parseInt(st.nextToken());

        Arrays.sort(a, Collections.reverseOrder());

        long total = 0;
        for (int i = 0; i < N; i++) {
            if (i < N - i - 1) {
                total += a[i] * 2;
            } else if (i == N - i - 1) {
                total += a[i];
            }
        }

        System.out.println(total);
    }
}
'''
            }
        ]
    },
    "baekjoon_10469": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    board = []
    for _ in range(8):
        board.append(input().strip())

    queens = []
    for i in range(8):
        for j in range(8):
            if board[i][j] == '*':
                queens.append((i, j))

    # 8개 여왕이 있어야 함
    if len(queens) != 8:
        print("invalid")
        return

    # 각 행, 열, 대각선에 여왕이 하나씩
    rows = set()
    cols = set()
    diag1 = set()  # i - j
    diag2 = set()  # i + j

    for r, c in queens:
        if r in rows or c in cols or (r - c) in diag1 or (r + c) in diag2:
            print("invalid")
            return
        rows.add(r)
        cols.add(c)
        diag1.add(r - c)
        diag2.add(r + c)

    print("valid")

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    vector<pair<int,int>> queens;

    for (int i = 0; i < 8; i++) {
        string line;
        cin >> line;
        for (int j = 0; j < 8; j++) {
            if (line[j] == '*') {
                queens.push_back({i, j});
            }
        }
    }

    if (queens.size() != 8) {
        cout << "invalid" << endl;
        return 0;
    }

    set<int> rows, cols, diag1, diag2;

    for (auto& [r, c] : queens) {
        if (rows.count(r) || cols.count(c) || diag1.count(r-c) || diag2.count(r+c)) {
            cout << "invalid" << endl;
            return 0;
        }
        rows.insert(r);
        cols.insert(c);
        diag1.insert(r - c);
        diag2.insert(r + c);
    }

    cout << "valid" << endl;

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

        List<int[]> queens = new ArrayList<>();

        for (int i = 0; i < 8; i++) {
            String line = br.readLine();
            for (int j = 0; j < 8; j++) {
                if (line.charAt(j) == '*') {
                    queens.add(new int[]{i, j});
                }
            }
        }

        if (queens.size() != 8) {
            System.out.println("invalid");
            return;
        }

        Set<Integer> rows = new HashSet<>();
        Set<Integer> cols = new HashSet<>();
        Set<Integer> diag1 = new HashSet<>();
        Set<Integer> diag2 = new HashSet<>();

        for (int[] q : queens) {
            int r = q[0], c = q[1];
            if (rows.contains(r) || cols.contains(c) || diag1.contains(r-c) || diag2.contains(r+c)) {
                System.out.println("invalid");
                return;
            }
            rows.add(r);
            cols.add(c);
            diag1.add(r - c);
            diag2.add(r + c);
        }

        System.out.println("valid");
    }
}
'''
            }
        ]
    },
    "baekjoon_6463": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def last_nonzero_digit(n):
    if n < 2:
        return 1

    # 마지막 0이 아닌 숫자를 구함
    # 2의 개수와 5의 개수를 세고, 나머지 곱의 마지막 자릿수 계산

    result = 1
    twos = 0

    for i in range(2, n + 1):
        x = i
        while x % 2 == 0:
            twos += 1
            x //= 2
        while x % 5 == 0:
            twos -= 1
            x //= 5
        result = (result * (x % 10)) % 10

    # 남은 2들 곱하기
    for _ in range(twos):
        result = (result * 2) % 10

    return result

try:
    while True:
        n = int(input())
        result = last_nonzero_digit(n)
        print(f"{n:5d} -> {result}")
except:
    pass
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <iomanip>
using namespace std;

int lastNonzeroDigit(int n) {
    if (n < 2) return 1;

    int result = 1;
    int twos = 0;

    for (int i = 2; i <= n; i++) {
        int x = i;
        while (x % 2 == 0) {
            twos++;
            x /= 2;
        }
        while (x % 5 == 0) {
            twos--;
            x /= 5;
        }
        result = (result * (x % 10)) % 10;
    }

    for (int i = 0; i < twos; i++) {
        result = (result * 2) % 10;
    }

    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    while (cin >> n) {
        int result = lastNonzeroDigit(n);
        cout << setw(5) << n << " -> " << result << "\\n";
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;

public class Main {
    static int lastNonzeroDigit(int n) {
        if (n < 2) return 1;

        int result = 1;
        int twos = 0;

        for (int i = 2; i <= n; i++) {
            int x = i;
            while (x % 2 == 0) {
                twos++;
                x /= 2;
            }
            while (x % 5 == 0) {
                twos--;
                x /= 5;
            }
            result = (result * (x % 10)) % 10;
        }

        for (int i = 0; i < twos; i++) {
            result = (result * 2) % 10;
        }

        return result;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        String line;
        while ((line = br.readLine()) != null && !line.isEmpty()) {
            int n = Integer.parseInt(line.trim());
            int result = lastNonzeroDigit(n);
            sb.append(String.format("%5d -> %d%n", n, result));
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_5043": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
import math
input = sys.stdin.readline

def solve():
    N, b = map(int, input().split())

    # N개 파일을 b비트로 압축 가능한지
    # 서로 다른 N개 파일을 구분하려면 최소 ceil(log2(N)) 비트 필요
    # 2^b >= N이면 가능

    if N == 0:
        print("yes")
        return

    if N == 1:
        # 1개 파일은 0비트로도 가능
        print("yes")
        return

    # 2^b >= N인지 확인
    if b >= math.log2(N):
        print("yes")
    else:
        print("no")

solve()
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

    long long N, b;
    cin >> N >> b;

    if (N <= 1) {
        cout << "yes" << endl;
        return 0;
    }

    // 2^b >= N
    // b >= log2(N)
    double logN = log2((double)N);

    if ((double)b >= logN) {
        cout << "yes" << endl;
    } else {
        cout << "no" << endl;
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
        long b = Long.parseLong(st.nextToken());

        if (N <= 1) {
            System.out.println("yes");
            return;
        }

        double logN = Math.log(N) / Math.log(2);

        if ((double)b >= logN) {
            System.out.println("yes");
        } else {
            System.out.println("no");
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_17253": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    x = int(input())

    # x를 3진법으로 표현했을 때 각 자릿수가 0 또는 1만 있으면 삼삼함
    # 3의 거듭제곱은 한 번씩만 사용 가능

    if x == 0:
        print("NO")
        return

    while x > 0:
        if x % 3 > 1:
            print("NO")
            return
        x //= 3

    print("YES")

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

    long long x;
    cin >> x;

    if (x == 0) {
        cout << "NO" << endl;
        return 0;
    }

    while (x > 0) {
        if (x % 3 > 1) {
            cout << "NO" << endl;
            return 0;
        }
        x /= 3;
    }

    cout << "YES" << endl;

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
        long x = Long.parseLong(br.readLine().trim());

        if (x == 0) {
            System.out.println("NO");
            return;
        }

        while (x > 0) {
            if (x % 3 > 1) {
                System.out.println("NO");
                return;
            }
            x /= 3;
        }

        System.out.println("YES");
    }
}
'''
            }
        ]
    },
    "baekjoon_15885": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    a, b = map(int, input().split())

    # 시계가 a + b*t 속도로 움직임 (a: 초기위치?, b: 속도?)
    # 하루에 실제 시계와 몇 번 맞는지

    # 실제 시계와 고장난 시계의 속도 차이
    # 고장난 시계 속도 = a + b (분당 이동량)
    # 실제 시계 속도 = 1

    # 하루 = 1440분
    # 차이 속도 = |b - 1| (b가 분당 이동량이라면)
    # 만나는 횟수 = |b - 1| * 2 (12시간에 한 바퀴)

    # 문제 해석: a=초기위치 오프셋, b=속도 배율
    # b=1이면 항상 맞음 -> 무한대
    # b=0이면 멈춤 -> 하루에 2번
    # b=-1이면 거꾸로 -> 하루에 4번

    if b == 1:
        # 항상 맞음 (같은 속도)
        print("infinity")
        return

    # 상대 속도 = |1 - b|
    # 하루 = 2바퀴 (12시간 시계 기준)
    # 만나는 횟수 = 상대 속도 * 2

    relative = abs(1 - b)
    count = relative * 2

    print(count)

solve()
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

    long long a, b;
    cin >> a >> b;

    if (b == 1) {
        cout << "infinity" << endl;
        return 0;
    }

    long long relative = abs(1 - b);
    long long count = relative * 2;

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
        StringTokenizer st = new StringTokenizer(br.readLine());

        long a = Long.parseLong(st.nextToken());
        long b = Long.parseLong(st.nextToken());

        if (b == 1) {
            System.out.println("infinity");
            return;
        }

        long relative = Math.abs(1 - b);
        long count = relative * 2;

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_31563": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N, Q = map(int, input().split())
    A = list(map(int, input().split()))

    offset = 0  # 회전 오프셋

    results = []
    for _ in range(Q):
        query = list(map(int, input().split()))

        if query[0] == 1:
            # 오른쪽으로 k만큼 회전
            k = query[1]
            offset = (offset + k) % N
        elif query[0] == 2:
            # i번째 원소 출력 (1-indexed)
            i = query[1]
            # 회전 후 i번째 위치의 원래 인덱스
            original_idx = (i - 1 - offset + N) % N
            results.append(A[original_idx])
        else:  # query[0] == 3
            # i부터 j까지 합
            i, j = query[1], query[2]
            total = 0
            for idx in range(i, j + 1):
                original_idx = (idx - 1 - offset + N) % N
                total += A[original_idx]
            results.append(total)

    for r in results:
        print(r)

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

    int N, Q;
    cin >> N >> Q;

    vector<long long> A(N);
    for (int i = 0; i < N; i++) cin >> A[i];

    int offset = 0;

    while (Q--) {
        int type;
        cin >> type;

        if (type == 1) {
            int k;
            cin >> k;
            offset = (offset + k) % N;
        } else if (type == 2) {
            int i;
            cin >> i;
            int originalIdx = ((i - 1 - offset) % N + N) % N;
            cout << A[originalIdx] << "\\n";
        } else {
            int i, j;
            cin >> i >> j;
            long long total = 0;
            for (int idx = i; idx <= j; idx++) {
                int originalIdx = ((idx - 1 - offset) % N + N) % N;
                total += A[originalIdx];
            }
            cout << total << "\\n";
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
        int Q = Integer.parseInt(st.nextToken());

        long[] A = new long[N];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) A[i] = Long.parseLong(st.nextToken());

        int offset = 0;
        StringBuilder sb = new StringBuilder();

        for (int q = 0; q < Q; q++) {
            st = new StringTokenizer(br.readLine());
            int type = Integer.parseInt(st.nextToken());

            if (type == 1) {
                int k = Integer.parseInt(st.nextToken());
                offset = (offset + k) % N;
            } else if (type == 2) {
                int i = Integer.parseInt(st.nextToken());
                int originalIdx = ((i - 1 - offset) % N + N) % N;
                sb.append(A[originalIdx]).append("\\n");
            } else {
                int i = Integer.parseInt(st.nextToken());
                int j = Integer.parseInt(st.nextToken());
                long total = 0;
                for (int idx = i; idx <= j; idx++) {
                    int originalIdx = ((idx - 1 - offset) % N + N) % N;
                    total += A[originalIdx];
                }
                sb.append(total).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_26152": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    A = list(map(int, input().split()))  # 상단
    B = list(map(int, input().split()))  # 하단
    Q = int(input())
    heights = list(map(int, input().split()))

    # 각 쿼리에 대해 h 높이로 시작해서 몇 개 장애물 통과 가능?
    for h in heights:
        count = 0
        current_h = h
        for i in range(N):
            # 장애물 통과 가능: B[i] < current_h < A[i]
            if B[i] < current_h < A[i]:
                count += 1
            else:
                break
        print(count)

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

    int N;
    cin >> N;

    vector<int> A(N), B(N);
    for (int i = 0; i < N; i++) cin >> A[i];
    for (int i = 0; i < N; i++) cin >> B[i];

    int Q;
    cin >> Q;

    while (Q--) {
        int h;
        cin >> h;

        int count = 0;
        for (int i = 0; i < N; i++) {
            if (B[i] < h && h < A[i]) {
                count++;
            } else {
                break;
            }
        }

        cout << count << "\\n";
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

        int[] A = new int[N];
        int[] B = new int[N];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) A[i] = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) B[i] = Integer.parseInt(st.nextToken());

        int Q = Integer.parseInt(br.readLine().trim());
        st = new StringTokenizer(br.readLine());

        StringBuilder sb = new StringBuilder();
        for (int q = 0; q < Q; q++) {
            int h = Integer.parseInt(st.nextToken());

            int count = 0;
            for (int i = 0; i < N; i++) {
                if (B[i] < h && h < A[i]) {
                    count++;
                } else {
                    break;
                }
            }

            sb.append(count).append("\\n");
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

    with open(baek_medium_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    print(f"기존 솔루션 수: {len(existing)}")

    added = 0
    for problem_id, solution_data in new_solutions.items():
        if problem_id not in existing:
            existing[problem_id] = solution_data
            added += 1
            print(f"  추가됨: {problem_id}")

    with open(baek_medium_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\n총 {added}개 문제 추가됨")
    print(f"현재 총 솔루션 수: {len(existing)}")

if __name__ == '__main__':
    main()
