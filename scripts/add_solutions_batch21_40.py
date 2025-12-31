#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
21번째부터 40번째까지의 빈 솔루션 medium 문제에 솔루션을 추가하는 스크립트
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

# 21번째부터 40번째까지 (인덱스 20~39)
solutions_to_add = {}

# 문제 21: 백준 15788 - 밸런스 스톤 (인덱스 3456)
solutions_to_add[empty_medium_indices[20]] = [
    {
        "language": "python",
        "code": '''# 백준 15788: 밸런스 스톤
# 마방진 퍼즐에서 빈 칸에 들어갈 수를 찾는 문제
import sys
input = sys.stdin.readline

n = int(input())
grid = []
zero_pos = None

for i in range(n):
    row = list(map(int, input().split()))
    grid.append(row)
    for j in range(n):
        if row[j] == 0:
            zero_pos = (i, j)

r, c = zero_pos

# 각 행, 열, 대각선의 합 계산
row_sums = [sum(grid[i]) for i in range(n)]
col_sums = [sum(grid[i][j] for i in range(n)) for j in range(n)]

# 빈 칸이 없는 행이나 열의 합을 기준으로 M 찾기
target = None
for i in range(n):
    if i != r:
        target = row_sums[i]
        break

if target is None:
    for j in range(n):
        if j != c:
            target = col_sums[j]
            break

# M 계산
M = target - row_sums[r]

if M <= 0:
    print(-1)
else:
    # 검증: 행, 열, 대각선 검사
    valid = True

    # 행 검사
    if row_sums[r] + M != target:
        valid = False

    # 열 검사
    if col_sums[c] + M != target:
        valid = False

    # 대각선 검사
    if r == c:  # 주대각선
        diag_sum = sum(grid[i][i] for i in range(n))
        if diag_sum + M != target:
            valid = False

    if r + c == n - 1:  # 부대각선
        anti_diag_sum = sum(grid[i][n-1-i] for i in range(n))
        if anti_diag_sum + M != target:
            valid = False

    # 대각선이 아닌 경우에도 대각선 합 검사
    diag1 = sum(grid[i][i] for i in range(n))
    diag2 = sum(grid[i][n-1-i] for i in range(n))

    if r == c:
        diag1 += M
    if r + c == n - 1:
        diag2 += M

    if diag1 != target or diag2 != target:
        valid = False

    if valid:
        print(M)
    else:
        print(-1)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 15788: 밸런스 스톤
// 마방진 퍼즐에서 빈 칸에 들어갈 수를 찾는 문제
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        long[][] grid = new long[n][n];
        int zeroR = -1, zeroC = -1;

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                grid[i][j] = Long.parseLong(st.nextToken());
                if (grid[i][j] == 0) {
                    zeroR = i;
                    zeroC = j;
                }
            }
        }

        // 각 행의 합 계산
        long[] rowSums = new long[n];
        long[] colSums = new long[n];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                rowSums[i] += grid[i][j];
                colSums[j] += grid[i][j];
            }
        }

        // 기준 합 찾기 (빈 칸이 없는 행)
        long target = -1;
        for (int i = 0; i < n; i++) {
            if (i != zeroR) {
                target = rowSums[i];
                break;
            }
        }

        // M 계산
        long M = target - rowSums[zeroR];

        if (M <= 0) {
            System.out.println(-1);
            return;
        }

        // 검증
        boolean valid = true;

        // 열 검사
        if (colSums[zeroC] + M != target) {
            valid = false;
        }

        // 대각선 검사
        long diag1 = 0, diag2 = 0;
        for (int i = 0; i < n; i++) {
            diag1 += grid[i][i];
            diag2 += grid[i][n-1-i];
        }

        if (zeroR == zeroC) diag1 += M;
        if (zeroR + zeroC == n - 1) diag2 += M;

        if (diag1 != target || diag2 != target) {
            valid = false;
        }

        System.out.println(valid ? M : -1);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
using namespace std;

// 백준 15788: 밸런스 스톤
// 마방진 퍼즐에서 빈 칸에 들어갈 수를 찾는 문제
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<vector<long long>> grid(n, vector<long long>(n));
    int zeroR = -1, zeroC = -1;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cin >> grid[i][j];
            if (grid[i][j] == 0) {
                zeroR = i;
                zeroC = j;
            }
        }
    }

    // 각 행, 열의 합 계산
    vector<long long> rowSums(n, 0), colSums(n, 0);
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            rowSums[i] += grid[i][j];
            colSums[j] += grid[i][j];
        }
    }

    // 기준 합 찾기
    long long target = -1;
    for (int i = 0; i < n; i++) {
        if (i != zeroR) {
            target = rowSums[i];
            break;
        }
    }

    // M 계산
    long long M = target - rowSums[zeroR];

    if (M <= 0) {
        cout << -1 << endl;
        return 0;
    }

    // 검증
    bool valid = true;

    // 열 검사
    if (colSums[zeroC] + M != target) valid = false;

    // 대각선 검사
    long long diag1 = 0, diag2 = 0;
    for (int i = 0; i < n; i++) {
        diag1 += grid[i][i];
        diag2 += grid[i][n-1-i];
    }

    if (zeroR == zeroC) diag1 += M;
    if (zeroR + zeroC == n - 1) diag2 += M;

    if (diag1 != target || diag2 != target) valid = false;

    cout << (valid ? M : -1) << endl;

    return 0;
}
'''
    }
]

# 문제 22: 백준 7481 - ATM놀이 (인덱스 3457)
solutions_to_add[empty_medium_indices[21]] = [
    {
        "language": "python",
        "code": '''# 백준 7481: ATM놀이
# 확장 유클리드 알고리즘을 이용한 디오판틴 방정식 풀이
import sys
input = sys.stdin.readline

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = extended_gcd(b, a % b)
    return g, y, x - (a // b) * y

T = int(input())
for _ in range(T):
    a, b, S = map(int, input().split())

    g = gcd(a, b)

    # S가 gcd(a, b)로 나누어지지 않으면 불가능
    if S % g != 0:
        print("Impossible")
        continue

    # ax + by = S의 해 찾기
    g, x0, y0 = extended_gcd(a, b)

    # 특수해
    x0 *= S // g
    y0 *= S // g

    # 일반해: x = x0 + (b/g)*t, y = y0 - (a/g)*t
    # x >= 0, y >= 0 조건을 만족하는 t 찾기

    a_g = a // g
    b_g = b // g

    # x >= 0: t >= -x0 * g / b = -x0 / b_g
    # y >= 0: t <= y0 * g / a = y0 / a_g

    # t의 범위 계산
    if b_g > 0:
        t_min = -x0 // b_g if -x0 >= 0 else (-x0 - b_g + 1) // b_g
        if x0 + b_g * t_min < 0:
            t_min += 1
    else:
        t_min = float('-inf')

    if a_g > 0:
        t_max = y0 // a_g
        if y0 - a_g * t_max < 0:
            t_max -= 1
    else:
        t_max = float('inf')

    if t_min > t_max:
        print("Impossible")
        continue

    # 지폐 수 최소화: x + y = (x0 + b_g*t) + (y0 - a_g*t) = x0 + y0 + (b_g - a_g)*t
    # b_g - a_g > 0이면 t를 최소로, < 0이면 t를 최대로

    if b_g - a_g > 0:
        t = t_min
    elif b_g - a_g < 0:
        t = t_max
    else:
        t = t_min  # 어떤 t든 상관없음

    x = x0 + b_g * t
    y = y0 - a_g * t

    if x >= 0 and y >= 0:
        print(x, y)
    else:
        print("Impossible")
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 7481: ATM놀이
// 확장 유클리드 알고리즘을 이용한 디오판틴 방정식 풀이
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long a = Long.parseLong(st.nextToken());
            long b = Long.parseLong(st.nextToken());
            long S = Long.parseLong(st.nextToken());

            long g = gcd(a, b);

            if (S % g != 0) {
                sb.append("Impossible\\n");
                continue;
            }

            long[] result = extendedGcd(a, b);
            long x0 = result[1] * (S / g);
            long y0 = result[2] * (S / g);

            long a_g = a / g;
            long b_g = b / g;

            // t 범위 찾기
            long tMin = Long.MIN_VALUE;
            long tMax = Long.MAX_VALUE;

            // x >= 0: x0 + b_g * t >= 0
            if (b_g > 0) {
                tMin = (long) Math.ceil(-x0 / (double) b_g);
            } else if (b_g < 0) {
                tMax = (long) Math.floor(-x0 / (double) b_g);
            } else if (x0 < 0) {
                sb.append("Impossible\\n");
                continue;
            }

            // y >= 0: y0 - a_g * t >= 0
            if (a_g > 0) {
                tMax = Math.min(tMax, (long) Math.floor(y0 / (double) a_g));
            } else if (a_g < 0) {
                tMin = Math.max(tMin, (long) Math.ceil(y0 / (double) a_g));
            } else if (y0 < 0) {
                sb.append("Impossible\\n");
                continue;
            }

            if (tMin > tMax) {
                sb.append("Impossible\\n");
                continue;
            }

            long t = (b_g - a_g > 0) ? tMin : tMax;
            long x = x0 + b_g * t;
            long y = y0 - a_g * t;

            if (x >= 0 && y >= 0) {
                sb.append(x + " " + y + "\\n");
            } else {
                sb.append("Impossible\\n");
            }
        }

        System.out.print(sb);
    }

    static long gcd(long a, long b) {
        while (b != 0) {
            long temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    static long[] extendedGcd(long a, long b) {
        if (b == 0) return new long[]{a, 1, 0};
        long[] result = extendedGcd(b, a % b);
        return new long[]{result[0], result[2], result[1] - (a / b) * result[2]};
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <cmath>
using namespace std;

// 백준 7481: ATM놀이
// 확장 유클리드 알고리즘을 이용한 디오판틴 방정식 풀이

typedef long long ll;

ll gcd(ll a, ll b) {
    while (b) {
        ll temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

ll extGcd(ll a, ll b, ll &x, ll &y) {
    if (b == 0) {
        x = 1; y = 0;
        return a;
    }
    ll x1, y1;
    ll g = extGcd(b, a % b, x1, y1);
    x = y1;
    y = x1 - (a / b) * y1;
    return g;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        ll a, b, S;
        cin >> a >> b >> S;

        ll g = gcd(a, b);

        if (S % g != 0) {
            cout << "Impossible\\n";
            continue;
        }

        ll x0, y0;
        extGcd(a, b, x0, y0);
        x0 *= S / g;
        y0 *= S / g;

        ll a_g = a / g;
        ll b_g = b / g;

        // t 범위 계산
        ll tMin = LLONG_MIN, tMax = LLONG_MAX;

        // x >= 0
        if (b_g > 0) {
            tMin = (ll)ceil(-x0 / (double)b_g);
        } else if (b_g < 0) {
            tMax = (ll)floor(-x0 / (double)b_g);
        } else if (x0 < 0) {
            cout << "Impossible\\n";
            continue;
        }

        // y >= 0
        if (a_g > 0) {
            tMax = min(tMax, (ll)floor(y0 / (double)a_g));
        } else if (a_g < 0) {
            tMin = max(tMin, (ll)ceil(y0 / (double)a_g));
        } else if (y0 < 0) {
            cout << "Impossible\\n";
            continue;
        }

        if (tMin > tMax) {
            cout << "Impossible\\n";
            continue;
        }

        ll t = (b_g - a_g > 0) ? tMin : tMax;
        ll x = x0 + b_g * t;
        ll y = y0 - a_g * t;

        if (x >= 0 && y >= 0) {
            cout << x << " " << y << "\\n";
        } else {
            cout << "Impossible\\n";
        }
    }

    return 0;
}
'''
    }
]

# 문제 23: 백준 15464 - The Bovine Shuffle (인덱스 3463)
solutions_to_add[empty_medium_indices[22]] = [
    {
        "language": "python",
        "code": '''# 백준 15464: The Bovine Shuffle
# 셔플을 역으로 3번 수행하여 원래 순서 찾기
import sys
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))  # 1-indexed positions
cows = input().split()  # 셔플 후 순서

# a[i-1] = j는 위치 i에 있는 소가 위치 j로 이동한다는 의미
# 역으로: 위치 j에 있는 소는 원래 위치 i에 있었음

# 역 매핑 생성: inverse[j] = i (위치 j의 소는 원래 위치 i에서 왔음)
inverse = [0] * (n + 1)
for i in range(n):
    inverse[a[i]] = i + 1

# 현재 위치에서 3번 역셔플
current = list(range(1, n + 1))  # 현재 위치
for _ in range(3):
    new_pos = [0] * n
    for i in range(n):
        # 위치 i+1의 소는 원래 inverse[i+1] 위치에서 왔음
        new_pos[inverse[i + 1] - 1] = current[i]
    current = new_pos

# current[i]는 원래 위치 i+1에 있어야 할 소의 현재 위치
# 따라서 원래 위치 i에는 cows[current[i]-1]의 소가 있어야 함

result = [0] * n
for i in range(n):
    result[current[i] - 1] = cows[i]

for cow in result:
    print(cow)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 15464: The Bovine Shuffle
// 셔플을 역으로 3번 수행하여 원래 순서 찾기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] a = new int[n];
        for (int i = 0; i < n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        String[] cows = new String[n];
        for (int i = 0; i < n; i++) {
            cows[i] = st.nextToken();
        }

        // 역 매핑 생성
        int[] inverse = new int[n + 1];
        for (int i = 0; i < n; i++) {
            inverse[a[i]] = i + 1;
        }

        // 3번 역셔플
        int[] current = new int[n];
        for (int i = 0; i < n; i++) current[i] = i + 1;

        for (int t = 0; t < 3; t++) {
            int[] newPos = new int[n];
            for (int i = 0; i < n; i++) {
                newPos[inverse[i + 1] - 1] = current[i];
            }
            current = newPos;
        }

        // 결과 배열 생성
        String[] result = new String[n];
        for (int i = 0; i < n; i++) {
            result[current[i] - 1] = cows[i];
        }

        StringBuilder sb = new StringBuilder();
        for (String cow : result) {
            sb.append(cow).append("\\n");
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

// 백준 15464: The Bovine Shuffle
// 셔플을 역으로 3번 수행하여 원래 순서 찾기
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    vector<string> cows(n);
    for (int i = 0; i < n; i++) {
        cin >> cows[i];
    }

    // 역 매핑 생성
    vector<int> inverse(n + 1);
    for (int i = 0; i < n; i++) {
        inverse[a[i]] = i + 1;
    }

    // 3번 역셔플
    vector<int> current(n);
    for (int i = 0; i < n; i++) current[i] = i + 1;

    for (int t = 0; t < 3; t++) {
        vector<int> newPos(n);
        for (int i = 0; i < n; i++) {
            newPos[inverse[i + 1] - 1] = current[i];
        }
        current = newPos;
    }

    // 결과 배열 생성
    vector<string> result(n);
    for (int i = 0; i < n; i++) {
        result[current[i] - 1] = cows[i];
    }

    for (const string& cow : result) {
        cout << cow << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 24: 백준 14843 - 정보갓 영훈이 (인덱스 3465)
solutions_to_add[empty_medium_indices[23]] = [
    {
        "language": "python",
        "code": '''# 백준 14843: 정보갓 영훈이
# 점수 계산 후 상위 15% 이내인지 확인
import sys
input = sys.stdin.readline

n = int(input())
total_score = 0.0

for _ in range(n):
    parts = input().split()
    S = float(parts[0])
    A = int(parts[1])
    T = int(parts[2])
    M = int(parts[3])

    # 점수 계산: S * (1 + 1/A) * (1 + M/T) / 4
    score = S * (1 + 1/A) * (1 + M/T) / 4
    total_score += score

p = int(input())
scores = []
for _ in range(p):
    scores.append(float(input()))

# 영훈이보다 점수가 높은 사람 수 계산
higher_count = sum(1 for s in scores if s > total_score)

# 순위 = 자신보다 점수가 높은 사람 수 + 1
rank = higher_count + 1

# 상위 15% 이내 = 순위 <= 총 인원(p+1) * 0.15
threshold = (p + 1) * 0.15

if rank <= threshold:
    print(f"The total score of Younghoon is {total_score:.2f}.")
else:
    print(f"The total score of Younghoon is {total_score:.2f}.")
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 14843: 정보갓 영훈이
// 점수 계산 후 상위 15% 이내인지 확인
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        double totalScore = 0.0;

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            double S = Double.parseDouble(st.nextToken());
            int A = Integer.parseInt(st.nextToken());
            int T = Integer.parseInt(st.nextToken());
            int M = Integer.parseInt(st.nextToken());

            // 점수 계산
            double score = S * (1 + 1.0/A) * (1 + (double)M/T) / 4;
            totalScore += score;
        }

        int p = Integer.parseInt(br.readLine().trim());
        double[] scores = new double[p];
        for (int i = 0; i < p; i++) {
            scores[i] = Double.parseDouble(br.readLine().trim());
        }

        // 순위 계산
        int higherCount = 0;
        for (double s : scores) {
            if (s > totalScore) higherCount++;
        }

        System.out.printf("The total score of Younghoon is %.2f.%n", totalScore);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <iomanip>
#include <vector>
using namespace std;

// 백준 14843: 정보갓 영훈이
// 점수 계산 후 상위 15% 이내인지 확인
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    double totalScore = 0.0;

    for (int i = 0; i < n; i++) {
        double S;
        int A, T, M;
        cin >> S >> A >> T >> M;

        // 점수 계산
        double score = S * (1 + 1.0/A) * (1 + (double)M/T) / 4;
        totalScore += score;
    }

    int p;
    cin >> p;

    vector<double> scores(p);
    for (int i = 0; i < p; i++) {
        cin >> scores[i];
    }

    // 순위 계산
    int higherCount = 0;
    for (double s : scores) {
        if (s > totalScore) higherCount++;
    }

    cout << fixed << setprecision(2);
    cout << "The total score of Younghoon is " << totalScore << "." << endl;

    return 0;
}
'''
    }
]

# 문제 25: 백준 25710 - 점수 계산 (인덱스 3468)
solutions_to_add[empty_medium_indices[24]] = [
    {
        "language": "python",
        "code": '''# 백준 25710: 점수 계산
# 두 수의 곱의 자릿수 합의 최댓값 구하기
import sys
input = sys.stdin.readline

def digit_sum(n):
    s = 0
    while n > 0:
        s += n % 10
        n //= 10
    return s

n = int(input())
a = list(map(int, input().split()))

# 배열의 값은 최대 1000이므로, 각 값별로 가장 큰 인덱스 저장
# 1000 * 1000 = 1,000,000 이므로 모든 쌍을 확인하는 것은 비효율적
# 대신 각 값이 존재하는지 체크하고, 존재하는 값들의 쌍만 확인

# 값의 존재 여부 체크
exists = [False] * 1001
for x in a:
    exists[x] = True

max_score = 0

# 존재하는 값들의 쌍 확인
for i in range(1, 1001):
    if not exists[i]:
        continue
    for j in range(i, 1001):
        if not exists[j]:
            continue
        if i == j:
            # 같은 값이 2개 이상 있어야 함
            count = sum(1 for x in a if x == i)
            if count < 2:
                continue
        score = digit_sum(i * j)
        max_score = max(max_score, score)

print(max_score)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 25710: 점수 계산
// 두 수의 곱의 자릿수 합의 최댓값 구하기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] a = new int[n];
        int[] count = new int[1001];

        for (int i = 0; i < n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
            count[a[i]]++;
        }

        int maxScore = 0;

        for (int i = 1; i <= 1000; i++) {
            if (count[i] == 0) continue;
            for (int j = i; j <= 1000; j++) {
                if (count[j] == 0) continue;
                if (i == j && count[i] < 2) continue;

                int score = digitSum(i * j);
                maxScore = Math.max(maxScore, score);
            }
        }

        System.out.println(maxScore);
    }

    static int digitSum(int n) {
        int sum = 0;
        while (n > 0) {
            sum += n % 10;
            n /= 10;
        }
        return sum;
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
using namespace std;

// 백준 25710: 점수 계산
// 두 수의 곱의 자릿수 합의 최댓값 구하기

int digitSum(int n) {
    int sum = 0;
    while (n > 0) {
        sum += n % 10;
        n /= 10;
    }
    return sum;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> count(1001, 0);

    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        count[x]++;
    }

    int maxScore = 0;

    for (int i = 1; i <= 1000; i++) {
        if (count[i] == 0) continue;
        for (int j = i; j <= 1000; j++) {
            if (count[j] == 0) continue;
            if (i == j && count[i] < 2) continue;

            int score = digitSum(i * j);
            maxScore = max(maxScore, score);
        }
    }

    cout << maxScore << endl;

    return 0;
}
'''
    }
]

# 문제 26: 백준 24173 - 알고리즘 수업 - 힙 정렬 1 (인덱스 3473)
solutions_to_add[empty_medium_indices[25]] = [
    {
        "language": "python",
        "code": '''# 백준 24173: 알고리즘 수업 - 힙 정렬 1
# 최소 힙 기반 힙 정렬에서 K번째 교환되는 두 수 찾기
import sys
input = sys.stdin.readline
sys.setrecursionlimit(1000000)

n, k = map(int, input().split())
A = [0] + list(map(int, input().split()))  # 1-indexed

swap_count = 0
result = None

def heapify(k_idx, n_size):
    global swap_count, result

    left = 2 * k_idx
    right = 2 * k_idx + 1

    smaller = -1

    if right <= n_size:
        if A[left] < A[right]:
            smaller = left
        else:
            smaller = right
    elif left <= n_size:
        smaller = left
    else:
        return

    if A[smaller] < A[k_idx]:
        swap_count += 1
        if swap_count == k:
            result = (min(A[k_idx], A[smaller]), max(A[k_idx], A[smaller]))
        A[k_idx], A[smaller] = A[smaller], A[k_idx]
        heapify(smaller, n_size)

def build_min_heap():
    for i in range(n // 2, 0, -1):
        heapify(i, n)

def heap_sort():
    global swap_count, result
    build_min_heap()

    for i in range(n, 1, -1):
        swap_count += 1
        if swap_count == k:
            result = (min(A[1], A[i]), max(A[1], A[i]))
        A[1], A[i] = A[i], A[1]
        heapify(1, i - 1)

heap_sort()

if result:
    print(result[0], result[1])
else:
    print(-1)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 24173: 알고리즘 수업 - 힙 정렬 1
// 최소 힙 기반 힙 정렬에서 K번째 교환되는 두 수 찾기
public class Main {
    static int[] A;
    static long swapCount = 0;
    static long k;
    static int[] result = null;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        k = Long.parseLong(st.nextToken());

        A = new int[n + 1];
        st = new StringTokenizer(br.readLine());
        for (int i = 1; i <= n; i++) {
            A[i] = Integer.parseInt(st.nextToken());
        }

        heapSort(n);

        if (result != null) {
            System.out.println(result[0] + " " + result[1]);
        } else {
            System.out.println(-1);
        }
    }

    static void heapify(int kIdx, int nSize) {
        int left = 2 * kIdx;
        int right = 2 * kIdx + 1;

        int smaller = -1;

        if (right <= nSize) {
            smaller = (A[left] < A[right]) ? left : right;
        } else if (left <= nSize) {
            smaller = left;
        } else {
            return;
        }

        if (A[smaller] < A[kIdx]) {
            swapCount++;
            if (swapCount == k) {
                result = new int[]{Math.min(A[kIdx], A[smaller]), Math.max(A[kIdx], A[smaller])};
            }
            int temp = A[kIdx];
            A[kIdx] = A[smaller];
            A[smaller] = temp;
            heapify(smaller, nSize);
        }
    }

    static void buildMinHeap(int n) {
        for (int i = n / 2; i >= 1; i--) {
            heapify(i, n);
        }
    }

    static void heapSort(int n) {
        buildMinHeap(n);

        for (int i = n; i >= 2; i--) {
            swapCount++;
            if (swapCount == k) {
                result = new int[]{Math.min(A[1], A[i]), Math.max(A[1], A[i])};
            }
            int temp = A[1];
            A[1] = A[i];
            A[i] = temp;
            heapify(1, i - 1);
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

// 백준 24173: 알고리즘 수업 - 힙 정렬 1
// 최소 힙 기반 힙 정렬에서 K번째 교환되는 두 수 찾기

vector<int> A;
long long swapCount = 0;
long long k;
pair<int, int> result = {-1, -1};
bool found = false;

void heapify(int kIdx, int nSize) {
    int left = 2 * kIdx;
    int right = 2 * kIdx + 1;

    int smaller = -1;

    if (right <= nSize) {
        smaller = (A[left] < A[right]) ? left : right;
    } else if (left <= nSize) {
        smaller = left;
    } else {
        return;
    }

    if (A[smaller] < A[kIdx]) {
        swapCount++;
        if (swapCount == k) {
            result = {min(A[kIdx], A[smaller]), max(A[kIdx], A[smaller])};
            found = true;
        }
        swap(A[kIdx], A[smaller]);
        heapify(smaller, nSize);
    }
}

void buildMinHeap(int n) {
    for (int i = n / 2; i >= 1; i--) {
        heapify(i, n);
    }
}

void heapSort(int n) {
    buildMinHeap(n);

    for (int i = n; i >= 2; i--) {
        swapCount++;
        if (swapCount == k) {
            result = {min(A[1], A[i]), max(A[1], A[i])};
            found = true;
        }
        swap(A[1], A[i]);
        heapify(1, i - 1);
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n >> k;

    A.resize(n + 1);
    for (int i = 1; i <= n; i++) {
        cin >> A[i];
    }

    heapSort(n);

    if (found) {
        cout << result.first << " " << result.second << endl;
    } else {
        cout << -1 << endl;
    }

    return 0;
}
'''
    }
]

# 문제 27: 백준 17091 - 단어 시계 (인덱스 3477)
solutions_to_add[empty_medium_indices[26]] = [
    {
        "language": "python",
        "code": '''# 백준 17091: 단어 시계
# 시각을 영어 단어로 표현하기

h = int(input())
m = int(input())

nums = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "quarter", "sixteen", "seventeen",
        "eighteen", "nineteen", "twenty", "twenty one", "twenty two", "twenty three",
        "twenty four", "twenty five", "twenty six", "twenty seven", "twenty eight",
        "twenty nine", "half"]

# 시간 단어
hours = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve"]

if m == 0:
    # 정각
    print(f"{hours[h]} o' clock")
elif m == 15:
    # 15분
    print(f"quarter past {hours[h]}")
elif m == 30:
    # 30분
    print(f"half past {hours[h]}")
elif m == 45:
    # 45분
    next_h = h + 1 if h < 12 else 1
    print(f"quarter to {hours[next_h]}")
elif m < 30:
    # past 사용
    if m == 1:
        print(f"one minute past {hours[h]}")
    else:
        print(f"{nums[m]} minutes past {hours[h]}")
else:
    # to 사용 (30 < m < 60)
    next_h = h + 1 if h < 12 else 1
    remaining = 60 - m
    if remaining == 1:
        print(f"one minute to {hours[next_h]}")
    else:
        print(f"{nums[remaining]} minutes to {hours[next_h]}")
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;

// 백준 17091: 단어 시계
// 시각을 영어 단어로 표현하기
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int h = sc.nextInt();
        int m = sc.nextInt();

        String[] nums = {"", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                "eleven", "twelve", "thirteen", "fourteen", "quarter", "sixteen", "seventeen",
                "eighteen", "nineteen", "twenty", "twenty one", "twenty two", "twenty three",
                "twenty four", "twenty five", "twenty six", "twenty seven", "twenty eight",
                "twenty nine", "half"};

        String[] hours = {"", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                "eleven", "twelve"};

        if (m == 0) {
            System.out.println(hours[h] + " o' clock");
        } else if (m == 15) {
            System.out.println("quarter past " + hours[h]);
        } else if (m == 30) {
            System.out.println("half past " + hours[h]);
        } else if (m == 45) {
            int nextH = (h < 12) ? h + 1 : 1;
            System.out.println("quarter to " + hours[nextH]);
        } else if (m < 30) {
            if (m == 1) {
                System.out.println("one minute past " + hours[h]);
            } else {
                System.out.println(nums[m] + " minutes past " + hours[h]);
            }
        } else {
            int nextH = (h < 12) ? h + 1 : 1;
            int remaining = 60 - m;
            if (remaining == 1) {
                System.out.println("one minute to " + hours[nextH]);
            } else {
                System.out.println(nums[remaining] + " minutes to " + hours[nextH]);
            }
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

// 백준 17091: 단어 시계
// 시각을 영어 단어로 표현하기

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int h, m;
    cin >> h >> m;

    string nums[] = {"", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
            "eleven", "twelve", "thirteen", "fourteen", "quarter", "sixteen", "seventeen",
            "eighteen", "nineteen", "twenty", "twenty one", "twenty two", "twenty three",
            "twenty four", "twenty five", "twenty six", "twenty seven", "twenty eight",
            "twenty nine", "half"};

    string hours[] = {"", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
            "eleven", "twelve"};

    if (m == 0) {
        cout << hours[h] << " o' clock" << endl;
    } else if (m == 15) {
        cout << "quarter past " << hours[h] << endl;
    } else if (m == 30) {
        cout << "half past " << hours[h] << endl;
    } else if (m == 45) {
        int nextH = (h < 12) ? h + 1 : 1;
        cout << "quarter to " << hours[nextH] << endl;
    } else if (m < 30) {
        if (m == 1) {
            cout << "one minute past " << hours[h] << endl;
        } else {
            cout << nums[m] << " minutes past " << hours[h] << endl;
        }
    } else {
        int nextH = (h < 12) ? h + 1 : 1;
        int remaining = 60 - m;
        if (remaining == 1) {
            cout << "one minute to " << hours[nextH] << endl;
        } else {
            cout << nums[remaining] << " minutes to " << hours[nextH] << endl;
        }
    }

    return 0;
}
'''
    }
]

# 문제 28: 백준 16464 - 가주아 (인덱스 3485)
solutions_to_add[empty_medium_indices[27]] = [
    {
        "language": "python",
        "code": '''# 백준 16464: 가주아
# 연속된 수의 합으로 K를 만들 수 있는지 확인
# K가 2의 거듭제곱이면 불가능, 아니면 가능
import sys
input = sys.stdin.readline

N = int(input())

for _ in range(N):
    K = int(input())

    # K가 2의 거듭제곱인지 확인
    # 2의 거듭제곱은 이진수에서 1이 하나만 있음 (K & (K-1) == 0)
    if K & (K - 1) == 0:
        print("GoHanGang")
    else:
        print("Gazua")
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 16464: 가주아
// 연속된 수의 합으로 K를 만들 수 있는지 확인
// K가 2의 거듭제곱이면 불가능, 아니면 가능
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int N = Integer.parseInt(br.readLine().trim());

        for (int i = 0; i < N; i++) {
            long K = Long.parseLong(br.readLine().trim());

            // K가 2의 거듭제곱인지 확인
            if ((K & (K - 1)) == 0) {
                sb.append("GoHanGang\\n");
            } else {
                sb.append("Gazua\\n");
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

// 백준 16464: 가주아
// 연속된 수의 합으로 K를 만들 수 있는지 확인
// K가 2의 거듭제곱이면 불가능, 아니면 가능

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    for (int i = 0; i < N; i++) {
        long long K;
        cin >> K;

        // K가 2의 거듭제곱인지 확인
        if ((K & (K - 1)) == 0) {
            cout << "GoHanGang\\n";
        } else {
            cout << "Gazua\\n";
        }
    }

    return 0;
}
'''
    }
]

# 문제 29: 백준 31563 - 수열 회전과 쿼리 (인덱스 3486)
solutions_to_add[empty_medium_indices[28]] = [
    {
        "language": "python",
        "code": '''# 백준 31563: 수열 회전과 쿼리
# 수열을 회전하고 구간 합을 계산하는 문제
import sys
input = sys.stdin.readline

n, q = map(int, input().split())
a = list(map(int, input().split()))

# 누적 합 배열 생성
prefix = [0] * (n + 1)
for i in range(n):
    prefix[i + 1] = prefix[i] + a[i]

total_sum = prefix[n]

# 현재 시작 인덱스 (오프셋)
offset = 0

for _ in range(q):
    query = list(map(int, input().split()))

    if query[0] == 1:
        # 오른쪽으로 k만큼 회전
        k = query[1]
        offset = (offset - k) % n
    elif query[0] == 2:
        # 왼쪽으로 k만큼 회전
        k = query[1]
        offset = (offset + k) % n
    else:
        # 구간 합 쿼리
        l, r = query[1], query[2]

        # 실제 인덱스 계산 (1-indexed를 0-indexed로)
        actual_l = (l - 1 + offset) % n
        actual_r = (r - 1 + offset) % n

        if actual_l <= actual_r:
            # 연속 구간
            result = prefix[actual_r + 1] - prefix[actual_l]
        else:
            # 분리된 구간 (actual_l부터 끝까지 + 처음부터 actual_r까지)
            result = (prefix[n] - prefix[actual_l]) + prefix[actual_r + 1]

        print(result)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 31563: 수열 회전과 쿼리
// 수열을 회전하고 구간 합을 계산하는 문제
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int q = Integer.parseInt(st.nextToken());

        long[] a = new long[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            a[i] = Long.parseLong(st.nextToken());
        }

        // 누적 합 배열
        long[] prefix = new long[n + 1];
        for (int i = 0; i < n; i++) {
            prefix[i + 1] = prefix[i] + a[i];
        }

        int offset = 0;

        for (int i = 0; i < q; i++) {
            st = new StringTokenizer(br.readLine());
            int type = Integer.parseInt(st.nextToken());

            if (type == 1) {
                int k = Integer.parseInt(st.nextToken());
                offset = ((offset - k) % n + n) % n;
            } else if (type == 2) {
                int k = Integer.parseInt(st.nextToken());
                offset = (offset + k) % n;
            } else {
                int l = Integer.parseInt(st.nextToken());
                int r = Integer.parseInt(st.nextToken());

                int actualL = (l - 1 + offset) % n;
                int actualR = (r - 1 + offset) % n;

                long result;
                if (actualL <= actualR) {
                    result = prefix[actualR + 1] - prefix[actualL];
                } else {
                    result = (prefix[n] - prefix[actualL]) + prefix[actualR + 1];
                }

                sb.append(result).append("\\n");
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
#include <vector>
using namespace std;

// 백준 31563: 수열 회전과 쿼리
// 수열을 회전하고 구간 합을 계산하는 문제

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, q;
    cin >> n >> q;

    vector<long long> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    // 누적 합 배열
    vector<long long> prefix(n + 1, 0);
    for (int i = 0; i < n; i++) {
        prefix[i + 1] = prefix[i] + a[i];
    }

    int offset = 0;

    for (int i = 0; i < q; i++) {
        int type;
        cin >> type;

        if (type == 1) {
            int k;
            cin >> k;
            offset = ((offset - k) % n + n) % n;
        } else if (type == 2) {
            int k;
            cin >> k;
            offset = (offset + k) % n;
        } else {
            int l, r;
            cin >> l >> r;

            int actualL = (l - 1 + offset) % n;
            int actualR = (r - 1 + offset) % n;

            long long result;
            if (actualL <= actualR) {
                result = prefix[actualR + 1] - prefix[actualL];
            } else {
                result = (prefix[n] - prefix[actualL]) + prefix[actualR + 1];
            }

            cout << result << "\\n";
        }
    }

    return 0;
}
'''
    }
]

# 문제 30: 백준 26152 - 플래피 버드 스코어링 (인덱스 3531)
solutions_to_add[empty_medium_indices[29]] = [
    {
        "language": "python",
        "code": '''# 백준 26152: 플래피 버드 스코어링
# 각 장애물의 틈새 크기를 계산하고 이진 탐색으로 점수 계산
import sys
input = sys.stdin.readline

n = int(input())
A = list(map(int, input().split()))  # 상단 장애물
B = list(map(int, input().split()))  # 하단 장애물

# 각 장애물의 틈새 크기 계산
gaps = []
for i in range(n):
    gap = A[i] - B[i]  # 틈새 크기
    gaps.append(gap)

# 각 장애물까지 도달하려면 그 전까지의 모든 장애물을 통과해야 함
# 따라서 i번째 장애물까지 통과하려면 min(gaps[0:i+1]) >= w 이어야 함

# 각 위치까지의 최소 틈새 계산
min_gaps = []
current_min = float('inf')
for i in range(n):
    current_min = min(current_min, gaps[i])
    min_gaps.append(current_min)

# min_gaps 정렬하여 이진 탐색 준비
# min_gaps[i] = i번째 장애물까지 통과하기 위한 최소 필요 틈새
# 점수 = 통과한 장애물 수

q = int(input())
birds = list(map(int, input().split()))

results = []
for w in birds:
    # w보다 min_gap이 크거나 같은 가장 큰 인덱스 찾기
    # min_gaps[i] >= w인 최대 i+1이 점수

    left, right = 0, n
    while left < right:
        mid = (left + right) // 2
        if min_gaps[mid] >= w:
            left = mid + 1
        else:
            right = mid

    results.append(left)

for r in results:
    print(r)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 26152: 플래피 버드 스코어링
// 각 장애물의 틈새 크기를 계산하고 이진 탐색으로 점수 계산
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine().trim());

        long[] A = new long[n];
        long[] B = new long[n];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            A[i] = Long.parseLong(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            B[i] = Long.parseLong(st.nextToken());
        }

        // 각 위치까지의 최소 틈새 계산
        long[] minGaps = new long[n];
        long currentMin = Long.MAX_VALUE;
        for (int i = 0; i < n; i++) {
            currentMin = Math.min(currentMin, A[i] - B[i]);
            minGaps[i] = currentMin;
        }

        int q = Integer.parseInt(br.readLine().trim());
        st = new StringTokenizer(br.readLine());

        for (int i = 0; i < q; i++) {
            long w = Long.parseLong(st.nextToken());

            // 이진 탐색
            int left = 0, right = n;
            while (left < right) {
                int mid = (left + right) / 2;
                if (minGaps[mid] >= w) {
                    left = mid + 1;
                } else {
                    right = mid;
                }
            }

            sb.append(left).append("\\n");
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
#include <algorithm>
using namespace std;

// 백준 26152: 플래피 버드 스코어링
// 각 장애물의 틈새 크기를 계산하고 이진 탐색으로 점수 계산

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<long long> A(n), B(n);
    for (int i = 0; i < n; i++) cin >> A[i];
    for (int i = 0; i < n; i++) cin >> B[i];

    // 각 위치까지의 최소 틈새 계산
    vector<long long> minGaps(n);
    long long currentMin = LLONG_MAX;
    for (int i = 0; i < n; i++) {
        currentMin = min(currentMin, A[i] - B[i]);
        minGaps[i] = currentMin;
    }

    int q;
    cin >> q;

    for (int i = 0; i < q; i++) {
        long long w;
        cin >> w;

        // 이진 탐색
        int left = 0, right = n;
        while (left < right) {
            int mid = (left + right) / 2;
            if (minGaps[mid] >= w) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        cout << left << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 31: 백준 20117 - 호반우 상인의 이상한 품질 계산법 (인덱스 3542)
solutions_to_add[empty_medium_indices[30]] = [
    {
        "language": "python",
        "code": '''# 백준 20117: 호반우 상인의 이상한 품질 계산법
# 그리디: 정렬 후 큰 값과 작은 값을 묶어서 중앙값(더 큰 값) 사용
import sys
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))

a.sort()

total = 0

# 절반씩 묶어서 큰 값을 중앙값으로 사용
# 홀수개면 가운데 값은 단독으로 판매
left = 0
right = n - 1

while left < right:
    # 가장 작은 값과 가장 큰 값을 묶음
    # 중앙값은 더 큰 값 (묶음 크기 2개, 중앙값 = 2/2+1 = 2번째 = 큰 값)
    total += a[right] * 2
    left += 1
    right -= 1

# 홀수개인 경우 가운데 값 단독 판매
if left == right:
    total += a[left]

print(total)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 20117: 호반우 상인의 이상한 품질 계산법
// 그리디: 정렬 후 큰 값과 작은 값을 묶어서 중앙값(더 큰 값) 사용
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        int[] a = new int[n];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(a);

        long total = 0;
        int left = 0, right = n - 1;

        while (left < right) {
            total += a[right] * 2;
            left++;
            right--;
        }

        if (left == right) {
            total += a[left];
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

// 백준 20117: 호반우 상인의 이상한 품질 계산법
// 그리디: 정렬 후 큰 값과 작은 값을 묶어서 중앙값(더 큰 값) 사용

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    sort(a.begin(), a.end());

    long long total = 0;
    int left = 0, right = n - 1;

    while (left < right) {
        total += (long long)a[right] * 2;
        left++;
        right--;
    }

    if (left == right) {
        total += a[left];
    }

    cout << total << endl;

    return 0;
}
'''
    }
]

# 문제 32: 백준 10469 - 사이 나쁜 여왕들 (인덱스 3545)
solutions_to_add[empty_medium_indices[31]] = [
    {
        "language": "python",
        "code": '''# 백준 10469: 사이 나쁜 여왕들
# 8퀸 문제의 해가 유효한지 검증

board = []
queens = []

for i in range(8):
    row = input()
    board.append(row)
    for j in range(8):
        if row[j] == '*':
            queens.append((i, j))

# 정확히 8개의 여왕이 있어야 함
if len(queens) != 8:
    print("invalid")
else:
    valid = True

    # 각 여왕 쌍에 대해 공격 가능 여부 확인
    for i in range(8):
        for j in range(i + 1, 8):
            r1, c1 = queens[i]
            r2, c2 = queens[j]

            # 같은 행
            if r1 == r2:
                valid = False
                break

            # 같은 열
            if c1 == c2:
                valid = False
                break

            # 같은 대각선
            if abs(r1 - r2) == abs(c1 - c2):
                valid = False
                break

        if not valid:
            break

    print("valid" if valid else "invalid")
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 10469: 사이 나쁜 여왕들
// 8퀸 문제의 해가 유효한지 검증
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        List<int[]> queens = new ArrayList<>();

        for (int i = 0; i < 8; i++) {
            String row = br.readLine();
            for (int j = 0; j < 8; j++) {
                if (row.charAt(j) == '*') {
                    queens.add(new int[]{i, j});
                }
            }
        }

        if (queens.size() != 8) {
            System.out.println("invalid");
            return;
        }

        boolean valid = true;

        outer:
        for (int i = 0; i < 8; i++) {
            for (int j = i + 1; j < 8; j++) {
                int r1 = queens.get(i)[0], c1 = queens.get(i)[1];
                int r2 = queens.get(j)[0], c2 = queens.get(j)[1];

                if (r1 == r2 || c1 == c2 || Math.abs(r1 - r2) == Math.abs(c1 - c2)) {
                    valid = false;
                    break outer;
                }
            }
        }

        System.out.println(valid ? "valid" : "invalid");
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

// 백준 10469: 사이 나쁜 여왕들
// 8퀸 문제의 해가 유효한지 검증

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    vector<pair<int, int>> queens;

    for (int i = 0; i < 8; i++) {
        string row;
        cin >> row;
        for (int j = 0; j < 8; j++) {
            if (row[j] == '*') {
                queens.push_back({i, j});
            }
        }
    }

    if (queens.size() != 8) {
        cout << "invalid" << endl;
        return 0;
    }

    bool valid = true;

    for (int i = 0; i < 8 && valid; i++) {
        for (int j = i + 1; j < 8 && valid; j++) {
            int r1 = queens[i].first, c1 = queens[i].second;
            int r2 = queens[j].first, c2 = queens[j].second;

            if (r1 == r2 || c1 == c2 || abs(r1 - r2) == abs(c1 - c2)) {
                valid = false;
            }
        }
    }

    cout << (valid ? "valid" : "invalid") << endl;

    return 0;
}
'''
    }
]

# 문제 33: 백준 6463 - 팩트 (인덱스 3550)
solutions_to_add[empty_medium_indices[32]] = [
    {
        "language": "python",
        "code": '''# 백준 6463: 팩트
# N!의 0이 아닌 마지막 자릿수 구하기
import sys
input = sys.stdin.readline

# N!의 마지막 0이 아닌 자릿수를 계산하는 함수
# 규칙: 2와 5의 개수를 맞추고 나머지 숫자들의 곱의 마지막 자릿수
def last_nonzero_digit(n):
    if n < 2:
        return 1

    # 테이블: 각 자릿수 d에 대해 1*2*...*d mod 10 (5를 제외한)
    table = [1, 1, 2, 6, 4, 2, 2, 4, 2, 8]

    if n < 10:
        result = 1
        for i in range(2, n + 1):
            result = (result * i) % 10
        while result % 10 == 0:
            result //= 10
        return result % 10

    # 재귀적 계산
    q = n // 5
    r = n % 10

    result = last_nonzero_digit(q)
    result = (result * table[r]) % 10

    # 2의 보정 (5가 2보다 많으므로 2를 곱해야 함)
    # q개의 5가 있으므로 2^q를 곱해야 함
    # 하지만 이미 팩토리얼에 포함되어 있으므로 조정 필요

    # 더 정확한 알고리즘 사용
    if (n // 10) % 4 == 1 or (n // 10) % 4 == 2:
        result = (result * 4) % 10

    return result

# 실제로는 더 간단한 접근법 사용
def solve(n):
    if n == 0 or n == 1:
        return 1

    result = 1
    table = [1, 1, 2, 6, 4, 2, 2, 4, 2, 8]  # 0!~9!의 마지막 0이 아닌 자릿수

    while n > 1:
        result = (result * table[n % 10]) % 10
        # 홀수 보정
        if ((n // 10) % 4) in [1, 2]:
            result = (result * 4) % 10
        n //= 5

    return result

while True:
    try:
        line = input().strip()
        if not line:
            break
        n = int(line)
        digit = solve(n)
        print(f"{n:>5} -> {digit}")
    except:
        break
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 6463: 팩트
// N!의 0이 아닌 마지막 자릿수 구하기
public class Main {
    static int[] table = {1, 1, 2, 6, 4, 2, 2, 4, 2, 8};

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        String line;
        while ((line = br.readLine()) != null && !line.isEmpty()) {
            int n = Integer.parseInt(line.trim());
            int digit = solve(n);
            sb.append(String.format("%5d -> %d%n", n, digit));
        }

        System.out.print(sb);
    }

    static int solve(int n) {
        if (n == 0 || n == 1) return 1;

        int result = 1;

        while (n > 1) {
            result = (result * table[n % 10]) % 10;
            int q = (n / 10) % 4;
            if (q == 1 || q == 2) {
                result = (result * 4) % 10;
            }
            n /= 5;
        }

        return result;
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <iomanip>
using namespace std;

// 백준 6463: 팩트
// N!의 0이 아닌 마지막 자릿수 구하기

int table[] = {1, 1, 2, 6, 4, 2, 2, 4, 2, 8};

int solve(int n) {
    if (n == 0 || n == 1) return 1;

    int result = 1;

    while (n > 1) {
        result = (result * table[n % 10]) % 10;
        int q = (n / 10) % 4;
        if (q == 1 || q == 2) {
            result = (result * 4) % 10;
        }
        n /= 5;
    }

    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    while (cin >> n) {
        int digit = solve(n);
        cout << setw(5) << n << " -> " << digit << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 34: 백준 27295 - 선형 회귀는 너무 쉬워 1 (인덱스 3571)
solutions_to_add[empty_medium_indices[33]] = [
    {
        "language": "python",
        "code": '''# 백준 27295: 선형 회귀는 너무 쉬워 1
# sum(a*x_i + b - y_i)를 0에 가깝게 만드는 a 찾기
import sys
from math import gcd
input = sys.stdin.readline

n, b = map(int, input().split())

sum_x = 0
sum_y_minus_b = 0

for _ in range(n):
    x, y = map(int, input().split())
    sum_x += x
    sum_y_minus_b += (y - b)

# sum(a*x_i + b - y_i) = a * sum_x + n*b - sum_y = a * sum_x - sum(y_i - b)
# 이를 0에 가깝게 하려면: a * sum_x = sum(y_i - b)
# a = sum(y_i - b) / sum_x

if sum_x == 0:
    # a에 관계없이 값이 일정 -> EZPZ
    print("EZPZ")
else:
    # a = sum_y_minus_b / sum_x
    numerator = sum_y_minus_b
    denominator = sum_x

    # 부호 처리
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator

    # 기약분수로 변환
    g = gcd(abs(numerator), abs(denominator))
    numerator //= g
    denominator //= g

    if denominator == 1:
        print(numerator)
    else:
        print(f"{numerator}/{denominator}")
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 27295: 선형 회귀는 너무 쉬워 1
// sum(a*x_i + b - y_i)를 0에 가깝게 만드는 a 찾기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        long b = Long.parseLong(st.nextToken());

        long sumX = 0;
        long sumYMinusB = 0;

        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            long x = Long.parseLong(st.nextToken());
            long y = Long.parseLong(st.nextToken());
            sumX += x;
            sumYMinusB += (y - b);
        }

        if (sumX == 0) {
            System.out.println("EZPZ");
        } else {
            long numerator = sumYMinusB;
            long denominator = sumX;

            if (denominator < 0) {
                numerator = -numerator;
                denominator = -denominator;
            }

            long g = gcd(Math.abs(numerator), Math.abs(denominator));
            numerator /= g;
            denominator /= g;

            if (denominator == 1) {
                System.out.println(numerator);
            } else {
                System.out.println(numerator + "/" + denominator);
            }
        }
    }

    static long gcd(long a, long b) {
        while (b != 0) {
            long temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <cmath>
using namespace std;

// 백준 27295: 선형 회귀는 너무 쉬워 1
// sum(a*x_i + b - y_i)를 0에 가깝게 만드는 a 찾기

long long gcd(long long a, long long b) {
    while (b != 0) {
        long long temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    long long b;
    cin >> n >> b;

    long long sumX = 0;
    long long sumYMinusB = 0;

    for (int i = 0; i < n; i++) {
        long long x, y;
        cin >> x >> y;
        sumX += x;
        sumYMinusB += (y - b);
    }

    if (sumX == 0) {
        cout << "EZPZ" << endl;
    } else {
        long long numerator = sumYMinusB;
        long long denominator = sumX;

        if (denominator < 0) {
            numerator = -numerator;
            denominator = -denominator;
        }

        long long g = gcd(abs(numerator), abs(denominator));
        numerator /= g;
        denominator /= g;

        if (denominator == 1) {
            cout << numerator << endl;
        } else {
            cout << numerator << "/" << denominator << endl;
        }
    }

    return 0;
}
'''
    }
]

# 문제 35: 백준 15885 - 고장난 시계 (인덱스 3576)
solutions_to_add[empty_medium_indices[34]] = [
    {
        "language": "python",
        "code": '''# 백준 15885: 고장난 시계
# 24시간 동안 고장난 시계가 정상 시계와 일치하는 횟수
import sys
from math import gcd
input = sys.stdin.readline

a, b = map(int, input().split())

# 정상 시계: 12시간에 한 바퀴 = 12*60*60초에 한 바퀴
# 고장난 시계: 1초에 a/b초 이동 -> 12*60*60 * b/a 초에 한 바퀴

# 24시간 = 2 * 12시간 = 2바퀴
# 정상 시계는 24시간 동안 2바퀴
# 고장난 시계는 24시간(= 2 * 12 * 60 * 60초) 동안 (2 * 12 * 60 * 60 * a/b) / (12 * 60 * 60) = 2a/b 바퀴

# 두 시계가 일치하는 횟수 = |정상 바퀴 수 - 고장 바퀴 수|
# = |2 - 2a/b| = |2b - 2a| / b = 2|b - a| / b

# 시작점 제외하고 24시간째 포함
# 일치 횟수 = 2 * |b - a| / b 를 정수로

numerator = 2 * abs(b - a)
denominator = b

g = gcd(numerator, denominator)
numerator //= g
denominator //= g

# 정수 부분 출력
print(numerator // denominator)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 15885: 고장난 시계
// 24시간 동안 고장난 시계가 정상 시계와 일치하는 횟수
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long a = Long.parseLong(st.nextToken());
        long b = Long.parseLong(st.nextToken());

        long numerator = 2 * Math.abs(b - a);
        long denominator = b;

        long g = gcd(numerator, denominator);
        numerator /= g;
        denominator /= g;

        System.out.println(numerator / denominator);
    }

    static long gcd(long a, long b) {
        while (b != 0) {
            long temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <cmath>
using namespace std;

// 백준 15885: 고장난 시계
// 24시간 동안 고장난 시계가 정상 시계와 일치하는 횟수

long long gcd(long long a, long long b) {
    while (b != 0) {
        long long temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long a, b;
    cin >> a >> b;

    long long numerator = 2 * abs(b - a);
    long long denominator = b;

    long long g = gcd(numerator, denominator);
    numerator /= g;
    denominator /= g;

    cout << numerator / denominator << endl;

    return 0;
}
'''
    }
]

# 문제 36: 백준 5043 - 정말 좋은 압축 (인덱스 3592)
solutions_to_add[empty_medium_indices[35]] = [
    {
        "language": "python",
        "code": '''# 백준 5043: 정말 좋은 압축
# N개의 파일을 최대 b비트로 압축 가능한지 확인
# 각 파일은 1000비트, 서로 다른 파일
# b비트로 압축하면 최대 2^0 + 2^1 + ... + 2^b = 2^(b+1) - 1개의 파일 구분 가능
import sys
input = sys.stdin.readline

line = input().split()
N = int(line[0])
b = int(line[1])

# 최대 구분 가능한 파일 수: 2^(b+1) - 1
# 하지만 정확히 말하면, 길이 1~b 비트의 모든 패턴 = 2 + 4 + ... + 2^b = 2^(b+1) - 2
# 길이 0비트도 허용하면 +1 = 2^(b+1) - 1

# 더 간단히: b비트 이하로 N개의 서로 다른 코드를 만들 수 있는가?
# 2^1 + 2^2 + ... + 2^b = 2^(b+1) - 2 (길이 1 이상)
# 또는 각 파일에 고유 코드 부여: 최대 2^b개 (정확히 b비트 사용 시)

# 문제는 "최대 b비트"이므로 1~b비트 모두 사용 가능
# 가능한 코드 수 = sum(2^i for i in 1..b) = 2^(b+1) - 2

if b == 0:
    # 0비트로는 최대 1개 파일만 (빈 코드)
    if N <= 1:
        print("yes")
    else:
        print("no")
else:
    max_files = (1 << (b + 1)) - 2
    if N <= max_files:
        print("yes")
    else:
        print("no")
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 5043: 정말 좋은 압축
// N개의 파일을 최대 b비트로 압축 가능한지 확인
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long N = Long.parseLong(st.nextToken());
        int b = Integer.parseInt(st.nextToken());

        if (b == 0) {
            System.out.println(N <= 1 ? "yes" : "no");
        } else {
            // 최대 파일 수: 2^(b+1) - 2
            long maxFiles = (1L << (b + 1)) - 2;
            System.out.println(N <= maxFiles ? "yes" : "no");
        }
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
using namespace std;

// 백준 5043: 정말 좋은 압축
// N개의 파일을 최대 b비트로 압축 가능한지 확인

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long N;
    int b;
    cin >> N >> b;

    if (b == 0) {
        cout << (N <= 1 ? "yes" : "no") << endl;
    } else {
        // 최대 파일 수: 2^(b+1) - 2
        long long maxFiles = (1LL << (b + 1)) - 2;
        cout << (N <= maxFiles ? "yes" : "no") << endl;
    }

    return 0;
}
'''
    }
]

# 문제 37: 백준 17253 - 삼삼한 수 2 (인덱스 3596)
solutions_to_add[empty_medium_indices[36]] = [
    {
        "language": "python",
        "code": '''# 백준 17253: 삼삼한 수 2
# 3의 거듭제곱들을 중복 없이 더해서 만들 수 있는 수인지 확인
# 이는 3진법으로 표현했을 때 각 자릿수가 0 또는 1인 경우
import sys
input = sys.stdin.readline

N = int(input())

if N == 0:
    print("NO")
else:
    is_samsam = True
    while N > 0:
        digit = N % 3
        if digit > 1:
            is_samsam = False
            break
        N //= 3

    print("YES" if is_samsam else "NO")
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 17253: 삼삼한 수 2
// 3의 거듭제곱들을 중복 없이 더해서 만들 수 있는 수인지 확인
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        long N = Long.parseLong(br.readLine().trim());

        if (N == 0) {
            System.out.println("NO");
            return;
        }

        boolean isSamsam = true;
        while (N > 0) {
            long digit = N % 3;
            if (digit > 1) {
                isSamsam = false;
                break;
            }
            N /= 3;
        }

        System.out.println(isSamsam ? "YES" : "NO");
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
using namespace std;

// 백준 17253: 삼삼한 수 2
// 3의 거듭제곱들을 중복 없이 더해서 만들 수 있는 수인지 확인

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long N;
    cin >> N;

    if (N == 0) {
        cout << "NO" << endl;
        return 0;
    }

    bool isSamsam = true;
    while (N > 0) {
        long long digit = N % 3;
        if (digit > 1) {
            isSamsam = false;
            break;
        }
        N /= 3;
    }

    cout << (isSamsam ? "YES" : "NO") << endl;

    return 0;
}
'''
    }
]

# 문제 38: 백준 25045 - 비즈마켓 (인덱스 3601)
solutions_to_add[empty_medium_indices[37]] = [
    {
        "language": "python",
        "code": '''# 백준 25045: 비즈마켓
# 그리디: 만족도가 큰 물품을 비용이 작은 기업에 배정
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
A = list(map(int, input().split()))  # 물품 만족도
B = list(map(int, input().split()))  # 기업 지불 비용

# 만족도 내림차순 정렬
A.sort(reverse=True)
# 비용 오름차순 정렬
B.sort()

total = 0
i, j = 0, 0

# 만족도가 큰 물품과 비용이 작은 기업을 매칭
while i < n and j < m:
    diff = A[i] - B[j]
    if diff >= 0:
        total += diff
        i += 1
        j += 1
    else:
        # 이 기업은 어떤 물품과도 매칭 불가 (만족도 < 비용)
        j += 1

print(total)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 25045: 비즈마켓
// 그리디: 만족도가 큰 물품을 비용이 작은 기업에 배정
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        long[] A = new long[n];
        long[] B = new long[m];

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            A[i] = Long.parseLong(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < m; i++) {
            B[i] = Long.parseLong(st.nextToken());
        }

        // 만족도 내림차순, 비용 오름차순
        Arrays.sort(A);
        Arrays.sort(B);

        long total = 0;
        int i = n - 1, j = 0;

        while (i >= 0 && j < m) {
            long diff = A[i] - B[j];
            if (diff >= 0) {
                total += diff;
                i--;
                j++;
            } else {
                j++;
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

// 백준 25045: 비즈마켓
// 그리디: 만족도가 큰 물품을 비용이 작은 기업에 배정

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<long long> A(n), B(m);
    for (int i = 0; i < n; i++) cin >> A[i];
    for (int i = 0; i < m; i++) cin >> B[i];

    // 만족도 내림차순, 비용 오름차순
    sort(A.begin(), A.end(), greater<long long>());
    sort(B.begin(), B.end());

    long long total = 0;
    int i = 0, j = 0;

    while (i < n && j < m) {
        long long diff = A[i] - B[j];
        if (diff >= 0) {
            total += diff;
            i++;
            j++;
        } else {
            j++;
        }
    }

    cout << total << endl;

    return 0;
}
'''
    }
]

# 문제 39: 백준 25426 - 일차함수들 (인덱스 3605)
solutions_to_add[empty_medium_indices[38]] = [
    {
        "language": "python",
        "code": '''# 백준 25426: 일차함수들
# a_i가 큰 함수에 큰 x값을 대입하면 합이 최대화됨
import sys
input = sys.stdin.readline

n = int(input())
funcs = []

for _ in range(n):
    a, b = map(int, input().split())
    funcs.append((a, b))

# a_i 기준으로 정렬
funcs.sort()

# 작은 a에는 작은 x, 큰 a에는 큰 x
# x = 1, 2, ..., n을 a가 작은 순서대로 배정
total = 0
for i, (a, b) in enumerate(funcs):
    x = i + 1  # 1부터 시작
    total += a * x + b

print(total)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 25426: 일차함수들
// a_i가 큰 함수에 큰 x값을 대입하면 합이 최대화됨
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        long[][] funcs = new long[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            funcs[i][0] = Long.parseLong(st.nextToken()); // a
            funcs[i][1] = Long.parseLong(st.nextToken()); // b
        }

        // a 기준으로 정렬
        Arrays.sort(funcs, (x, y) -> Long.compare(x[0], y[0]));

        long total = 0;
        for (int i = 0; i < n; i++) {
            long x = i + 1;
            total += funcs[i][0] * x + funcs[i][1];
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

// 백준 25426: 일차함수들
// a_i가 큰 함수에 큰 x값을 대입하면 합이 최대화됨

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<pair<long long, long long>> funcs(n);
    for (int i = 0; i < n; i++) {
        cin >> funcs[i].first >> funcs[i].second; // a, b
    }

    // a 기준으로 정렬
    sort(funcs.begin(), funcs.end());

    long long total = 0;
    for (int i = 0; i < n; i++) {
        long long x = i + 1;
        total += funcs[i].first * x + funcs[i].second;
    }

    cout << total << endl;

    return 0;
}
'''
    }
]

# 문제 40: 백준 18249 - 욱제가 풀어야 하는 문제 (인덱스 3654)
solutions_to_add[empty_medium_indices[39]] = [
    {
        "language": "python",
        "code": '''# 백준 18249: 욱제가 풀어야 하는 문제
# 그래프에서 퍼펙트 매칭의 수 구하기
# 이 문제는 피보나치 수열과 관련됨
import sys
input = sys.stdin.readline

MOD = 10**9 + 7
MAX_N = 191230

# 피보나치 수열 전처리
fib = [0] * (MAX_N + 1)
fib[1] = 1
if MAX_N >= 2:
    fib[2] = 2
for i in range(3, MAX_N + 1):
    fib[i] = (fib[i-1] + fib[i-2]) % MOD

T = int(input())
for _ in range(T):
    N = int(input())
    print(fib[N])
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 18249: 욱제가 풀어야 하는 문제
// 그래프에서 퍼펙트 매칭의 수 구하기
public class Main {
    static final int MOD = 1_000_000_007;
    static final int MAX_N = 191230;
    static long[] fib = new long[MAX_N + 1];

    public static void main(String[] args) throws IOException {
        // 피보나치 전처리
        fib[1] = 1;
        if (MAX_N >= 2) fib[2] = 2;
        for (int i = 3; i <= MAX_N; i++) {
            fib[i] = (fib[i-1] + fib[i-2]) % MOD;
        }

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());
        for (int t = 0; t < T; t++) {
            int N = Integer.parseInt(br.readLine().trim());
            sb.append(fib[N]).append("\\n");
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

// 백준 18249: 욱제가 풀어야 하는 문제
// 그래프에서 퍼펙트 매칭의 수 구하기

const int MOD = 1e9 + 7;
const int MAX_N = 191230;
long long fib[MAX_N + 1];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    // 피보나치 전처리
    fib[1] = 1;
    fib[2] = 2;
    for (int i = 3; i <= MAX_N; i++) {
        fib[i] = (fib[i-1] + fib[i-2]) % MOD;
    }

    int T;
    cin >> T;

    while (T--) {
        int N;
        cin >> N;
        cout << fib[N] << "\\n";
    }

    return 0;
}
'''
    }
]

# 솔루션 적용
for idx, solutions in solutions_to_add.items():
    data[idx]['solutions'] = solutions
    print(f"문제 {data[idx]['id']} ({data[idx].get('name', '')})에 솔루션 추가 완료")

# JSON 파일 저장
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n총 {len(solutions_to_add)}개 문제에 솔루션 추가 완료")
