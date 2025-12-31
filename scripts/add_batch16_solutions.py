#!/usr/bin/env python3
"""Batch 16: 15개 Medium 문제 솔루션 추가"""
import json

new_solutions = {
    "baekjoon_18881": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
cows = []
for _ in range(n):
    x, s = map(int, input().split())
    cows.append((x, s))

# 위치순 정렬
cows.sort()

# 감염된 소들 사이의 최소 거리 구하기
infected = [c for c in cows if c[1] == 1]
if len(infected) <= 1:
    print(1 if len(infected) == 1 else 0)
else:
    min_dist = float('inf')
    for i in range(1, len(infected)):
        dist = infected[i][0] - infected[i-1][0]
        min_dist = min(min_dist, dist)

    # 감염되지 않은 소가 사이에 있으면 별도 감염원
    # 최소 거리보다 더 큰 간격으로 떨어진 감염된 소 그룹 수
    count = 1
    for i in range(1, len(infected)):
        dist = infected[i][0] - infected[i-1][0]
        if dist > min_dist:
            count += 1

    print(count)
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

    vector<pair<int, int>> cows(n);
    for (int i = 0; i < n; i++) {
        cin >> cows[i].first >> cows[i].second;
    }

    sort(cows.begin(), cows.end());

    vector<int> infected;
    for (int i = 0; i < n; i++) {
        if (cows[i].second == 1) {
            infected.push_back(cows[i].first);
        }
    }

    if (infected.size() <= 1) {
        cout << (infected.size() == 1 ? 1 : 0) << endl;
        return 0;
    }

    int minDist = INT_MAX;
    for (int i = 1; i < (int)infected.size(); i++) {
        minDist = min(minDist, infected[i] - infected[i-1]);
    }

    int count = 1;
    for (int i = 1; i < (int)infected.size(); i++) {
        if (infected[i] - infected[i-1] > minDist) {
            count++;
        }
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

        int[][] cows = new int[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            cows[i][0] = Integer.parseInt(st.nextToken());
            cows[i][1] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(cows, (a, b) -> a[0] - b[0]);

        List<Integer> infected = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            if (cows[i][1] == 1) {
                infected.add(cows[i][0]);
            }
        }

        if (infected.size() <= 1) {
            System.out.println(infected.size() == 1 ? 1 : 0);
            return;
        }

        int minDist = Integer.MAX_VALUE;
        for (int i = 1; i < infected.size(); i++) {
            minDist = Math.min(minDist, infected.get(i) - infected.get(i-1));
        }

        int count = 1;
        for (int i = 1; i < infected.size(); i++) {
            if (infected.get(i) - infected.get(i-1) > minDist) {
                count++;
            }
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_28298": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from collections import Counter
input = sys.stdin.readline

n, m, k = map(int, input().split())
grid = []
for _ in range(n):
    grid.append(input().strip())

# K x K 타일 내 각 위치별로 가장 많은 색상 찾기
# (i % k, j % k) 위치에서 가장 많이 나오는 색상 선택

position_counts = [[Counter() for _ in range(k)] for _ in range(k)]

for i in range(n):
    for j in range(m):
        pi, pj = i % k, j % k
        position_counts[pi][pj][grid[i][j]] += 1

# 각 위치별 최적 색상 선택
best_color = [['' for _ in range(k)] for _ in range(k)]
changes = 0

for i in range(k):
    for j in range(k):
        if position_counts[i][j]:
            most_common = position_counts[i][j].most_common(1)[0]
            best_color[i][j] = most_common[0]
            total = sum(position_counts[i][j].values())
            changes += total - most_common[1]
        else:
            best_color[i][j] = 'A'

print(changes)

# 결과 그리드 생성
result = []
for i in range(n):
    row = ""
    for j in range(m):
        row += best_color[i % k][j % k]
    result.append(row)

for row in result:
    print(row)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <map>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, k;
    cin >> n >> m >> k;

    vector<string> grid(n);
    for (int i = 0; i < n; i++) {
        cin >> grid[i];
    }

    // 각 위치별 색상 카운트
    vector<vector<map<char, int>>> counts(k, vector<map<char, int>>(k));

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            counts[i % k][j % k][grid[i][j]]++;
        }
    }

    // 각 위치별 최적 색상 선택
    vector<vector<char>> best(k, vector<char>(k, 'A'));
    int changes = 0;

    for (int i = 0; i < k; i++) {
        for (int j = 0; j < k; j++) {
            int total = 0;
            int maxCount = 0;
            char bestChar = 'A';
            for (auto& p : counts[i][j]) {
                total += p.second;
                if (p.second > maxCount) {
                    maxCount = p.second;
                    bestChar = p.first;
                }
            }
            best[i][j] = bestChar;
            changes += total - maxCount;
        }
    }

    cout << changes << "\\n";

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            cout << best[i % k][j % k];
        }
        cout << "\\n";
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
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        String[] grid = new String[n];
        for (int i = 0; i < n; i++) {
            grid[i] = br.readLine();
        }

        // 각 위치별 색상 카운트
        int[][][] counts = new int[k][k][26];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                counts[i % k][j % k][grid[i].charAt(j) - 'A']++;
            }
        }

        char[][] best = new char[k][k];
        int changes = 0;

        for (int i = 0; i < k; i++) {
            for (int j = 0; j < k; j++) {
                int total = 0;
                int maxCount = 0;
                char bestChar = 'A';
                for (int c = 0; c < 26; c++) {
                    total += counts[i][j][c];
                    if (counts[i][j][c] > maxCount) {
                        maxCount = counts[i][j][c];
                        bestChar = (char)('A' + c);
                    }
                }
                best[i][j] = bestChar;
                changes += total - maxCount;
            }
        }

        StringBuilder sb = new StringBuilder();
        sb.append(changes).append("\\n");

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                sb.append(best[i % k][j % k]);
            }
            sb.append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_27527": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, l = map(int, input().split())
heights = list(map(int, input().split()))

# 연속 l개의 높이가 모두 같아야 배너 설치 가능
# 슬라이딩 윈도우로 연속 l개 확인

for i in range(n - l + 1):
    # heights[i:i+l]이 모두 같은지 확인
    all_same = True
    for j in range(i + 1, i + l):
        if heights[j] != heights[i]:
            all_same = False
            break
    if all_same:
        print("YES")
        exit()

print("NO")
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

    int n, l;
    cin >> n >> l;

    vector<int> heights(n);
    for (int i = 0; i < n; i++) {
        cin >> heights[i];
    }

    for (int i = 0; i <= n - l; i++) {
        bool allSame = true;
        for (int j = i + 1; j < i + l; j++) {
            if (heights[j] != heights[i]) {
                allSame = false;
                break;
            }
        }
        if (allSame) {
            cout << "YES" << endl;
            return 0;
        }
    }

    cout << "NO" << endl;
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
        int n = Integer.parseInt(st.nextToken());
        int l = Integer.parseInt(st.nextToken());

        int[] heights = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            heights[i] = Integer.parseInt(st.nextToken());
        }

        for (int i = 0; i <= n - l; i++) {
            boolean allSame = true;
            for (int j = i + 1; j < i + l; j++) {
                if (heights[j] != heights[i]) {
                    allSame = false;
                    break;
                }
            }
            if (allSame) {
                System.out.println("YES");
                return;
            }
        }

        System.out.println("NO");
    }
}
'''
            }
        ]
    },
    "baekjoon_28250": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from collections import Counter
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))

# mex({a_i, a_j}) 계산
# 0: 0 없으면 0, 0 있고 1 없으면 1, 둘 다 있으면 2, ...

cnt = Counter(a)

total = 0

# 모든 쌍에 대해 mex 계산
# mex({x, y}):
# - x != y: 0이 없으면 0, 1이 없으면 1, 2가 없으면 2 (단, x, y가 아닌 값 중)
# - x == y: 0이 없으면 0, 1이 없으면 1, ...

# 최적화: mex 값별로 기여도 계산
# mex = 0: x != 0 and y != 0
# mex = 1: (x == 0 or y == 0) and x != 1 and y != 1
# mex = 2: {x, y} includes 0 and 1, but not 2
# ...

# 단순 O(n^2) 접근
for i in range(n):
    for j in range(i + 1, n):
        s = {a[i], a[j]}
        mex = 0
        while mex in s:
            mex += 1
        total += mex

print(total)
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

    int n;
    cin >> n;

    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    long long total = 0;

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            set<int> s = {a[i], a[j]};
            int mex = 0;
            while (s.count(mex)) {
                mex++;
            }
            total += mex;
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
        int n = Integer.parseInt(br.readLine().trim());

        int[] a = new int[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
        }

        long total = 0;

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                Set<Integer> s = new HashSet<>();
                s.add(a[i]);
                s.add(a[j]);
                int mex = 0;
                while (s.contains(mex)) {
                    mex++;
                }
                total += mex;
            }
        }

        System.out.println(total);
    }
}
'''
            }
        ]
    },
    "baekjoon_18187": {
        "solutions": [
            {
                "language": "python",
                "code": '''n = int(input())

# 기울기가 -1, 0, 1인 직선만 사용 가능
# 최대 영역 수 = 1 + sum(i for i in 1..n) (모든 직선이 다른 직선과 교차)
# 하지만 같은 기울기끼리는 교차 안 함

# 세 그룹으로 나누기: 기울기 -1, 0, 1
# 각 그룹에서 a, b, c개 사용
# 영역 수 = 1 + (a + b + c) + ab + bc + ca

# n개를 세 그룹으로 나눠 ab + bc + ca 최대화
# a + b + c = n, a*b + b*c + c*a 최대화

# 최적: n을 3으로 나눠 균등 배분
if n == 0:
    print(1)
elif n == 1:
    print(2)
elif n == 2:
    print(4)
else:
    a = n // 3
    b = n // 3
    c = n // 3
    remainder = n % 3
    if remainder == 1:
        a += 1
    elif remainder == 2:
        a += 1
        b += 1

    regions = 1 + (a + b + c) + a*b + b*c + c*a
    print(regions)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n;
    cin >> n;

    if (n == 0) {
        cout << 1 << endl;
    } else if (n == 1) {
        cout << 2 << endl;
    } else if (n == 2) {
        cout << 4 << endl;
    } else {
        long long a = n / 3;
        long long b = n / 3;
        long long c = n / 3;
        long long remainder = n % 3;
        if (remainder == 1) {
            a++;
        } else if (remainder == 2) {
            a++;
            b++;
        }

        long long regions = 1 + (a + b + c) + a*b + b*c + c*a;
        cout << regions << endl;
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
        long n = Long.parseLong(br.readLine().trim());

        if (n == 0) {
            System.out.println(1);
        } else if (n == 1) {
            System.out.println(2);
        } else if (n == 2) {
            System.out.println(4);
        } else {
            long a = n / 3;
            long b = n / 3;
            long c = n / 3;
            long remainder = n % 3;
            if (remainder == 1) {
                a++;
            } else if (remainder == 2) {
                a++;
                b++;
            }

            long regions = 1 + (a + b + c) + a*b + b*c + c*a;
            System.out.println(regions);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_30404": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, k = map(int, input().split())
times = list(map(int, input().split()))

# 그리디: 가능한 한 늦게 박수치기
claps = 0
last_clap = -float('inf')

for t in times:
    # t부터 t+k 사이에 박수 쳐야 함
    if last_clap < t:
        # 새로 박수 쳐야 함, 가능한 늦게: t+k
        last_clap = t + k
        claps += 1
    # else: 이전 박수가 아직 유효

print(claps)
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

    int n, k;
    cin >> n >> k;

    vector<int> times(n);
    for (int i = 0; i < n; i++) {
        cin >> times[i];
    }

    int claps = 0;
    int lastClap = -1000000000;

    for (int i = 0; i < n; i++) {
        if (lastClap < times[i]) {
            lastClap = times[i] + k;
            claps++;
        }
    }

    cout << claps << endl;
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
        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        int[] times = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            times[i] = Integer.parseInt(st.nextToken());
        }

        int claps = 0;
        int lastClap = Integer.MIN_VALUE;

        for (int i = 0; i < n; i++) {
            if (lastClap < times[i]) {
                lastClap = times[i] + k;
                claps++;
            }
        }

        System.out.println(claps);
    }
}
'''
            }
        ]
    },
    "baekjoon_26258": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
import bisect
input = sys.stdin.readline

n = int(input())
points = []
for _ in range(n):
    x, y = map(int, input().split())
    points.append((x, y))

# x 좌표 리스트 (이분 탐색용)
xs = [p[0] for p in points]

q = int(input())
results = []

for _ in range(q):
    k = float(input())

    # k가 어느 구간에 속하는지 찾기
    idx = bisect.bisect_right(xs, k)

    if idx == 0 or idx == n:
        # 범위 밖 (문제에서는 항상 범위 내로 주어질 것으로 가정)
        results.append(0)
    else:
        # [xs[idx-1], xs[idx]] 구간
        x1, y1 = points[idx - 1]
        x2, y2 = points[idx]

        if y2 > y1:
            results.append(1)  # 증가
        elif y2 < y1:
            results.append(-1)  # 감소
        else:
            results.append(0)  # 변화 없음

for r in results:
    print(r)
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

    vector<pair<double, double>> points(n);
    vector<double> xs(n);

    for (int i = 0; i < n; i++) {
        cin >> points[i].first >> points[i].second;
        xs[i] = points[i].first;
    }

    int q;
    cin >> q;

    while (q--) {
        double k;
        cin >> k;

        int idx = upper_bound(xs.begin(), xs.end(), k) - xs.begin();

        if (idx == 0 || idx == n) {
            cout << 0 << "\\n";
        } else {
            double y1 = points[idx - 1].second;
            double y2 = points[idx].second;

            if (y2 > y1) {
                cout << 1 << "\\n";
            } else if (y2 < y1) {
                cout << -1 << "\\n";
            } else {
                cout << 0 << "\\n";
            }
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
        int n = Integer.parseInt(br.readLine().trim());

        double[][] points = new double[n][2];
        double[] xs = new double[n];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            points[i][0] = Double.parseDouble(st.nextToken());
            points[i][1] = Double.parseDouble(st.nextToken());
            xs[i] = points[i][0];
        }

        int q = Integer.parseInt(br.readLine().trim());
        StringBuilder sb = new StringBuilder();

        while (q-- > 0) {
            double k = Double.parseDouble(br.readLine().trim());

            // 이분 탐색
            int idx = Arrays.binarySearch(xs, k);
            if (idx < 0) {
                idx = -(idx + 1);
            }

            if (idx == 0 || idx == n) {
                sb.append(0).append("\\n");
            } else {
                double y1 = points[idx - 1][1];
                double y2 = points[idx][1];

                if (y2 > y1) {
                    sb.append(1).append("\\n");
                } else if (y2 < y1) {
                    sb.append(-1).append("\\n");
                } else {
                    sb.append(0).append("\\n");
                }
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_25179": {
        "solutions": [
            {
                "language": "python",
                "code": '''n, m = map(int, input().split())

# 배스킨라빈스 N 게임: N을 부르면 패배
# 한 번에 1~M개 부를 수 있음
# N을 상대가 부르게 하려면
# (N-1) % (M+1) != 0이면 이길 수 있음

if (n - 1) % (m + 1) != 0:
    print("Can win")
else:
    print("Can't win")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n, m;
    cin >> n >> m;

    if ((n - 1) % (m + 1) != 0) {
        cout << "Can win" << endl;
    } else {
        cout << "Can't win" << endl;
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
        long n = Long.parseLong(st.nextToken());
        long m = Long.parseLong(st.nextToken());

        if ((n - 1) % (m + 1) != 0) {
            System.out.println("Can win");
        } else {
            System.out.println("Can't win");
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_16237": {
        "solutions": [
            {
                "language": "python",
                "code": '''a, b, c, d, e = map(int, input().split())

# 바구니당 최대 5kg
# 5kg: 각각 1개씩
baskets = e

# 4kg: 4+1 = 5 (1kg과 매칭)
baskets += d
a = max(0, a - d)

# 3kg: 3+2 = 5 또는 3+1+1 = 5
baskets += c
# 3kg 바구니에 2kg 넣기
pairs_3_2 = min(c, b)
b -= pairs_3_2
# 남은 3kg 바구니에 1kg 2개 넣기 (이미 2kg 안 넣은 바구니)
remaining_3 = c - pairs_3_2
fill_1 = min(remaining_3 * 2, a)
a -= fill_1

# 2kg: 2+2+1 = 5 또는 2+2 = 4 또는 2+1+1+1 = 5
# 2개씩 묶기
pairs_2 = b // 2
baskets += pairs_2
if b % 2 == 1:
    # 남은 2kg 1개
    baskets += 1
    # 2kg에 1kg 3개 넣을 수 있음
    a = max(0, a - 3)

# 1개씩 매칭된 2kg 바구니에 1kg 1개씩 넣기
a = max(0, a - pairs_2)

# 남은 1kg: 5개씩 묶기
baskets += (a + 4) // 5

print(baskets)
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

    int a, b, c, d, e;
    cin >> a >> b >> c >> d >> e;

    int baskets = e;

    // 4kg + 1kg
    baskets += d;
    a = max(0, a - d);

    // 3kg
    baskets += c;
    // 3kg + 2kg
    int pairs_3_2 = min(c, b);
    b -= pairs_3_2;
    // 남은 3kg에 1kg 2개씩
    int remaining_3 = c - pairs_3_2;
    int fill_1 = min(remaining_3 * 2, a);
    a -= fill_1;

    // 2kg
    int pairs_2 = b / 2;
    baskets += pairs_2;
    if (b % 2 == 1) {
        baskets += 1;
        a = max(0, a - 3);
    }
    a = max(0, a - pairs_2);

    // 1kg
    baskets += (a + 4) / 5;

    cout << baskets << endl;
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
        int a = Integer.parseInt(st.nextToken());
        int b = Integer.parseInt(st.nextToken());
        int c = Integer.parseInt(st.nextToken());
        int d = Integer.parseInt(st.nextToken());
        int e = Integer.parseInt(st.nextToken());

        int baskets = e;

        // 4kg + 1kg
        baskets += d;
        a = Math.max(0, a - d);

        // 3kg
        baskets += c;
        int pairs_3_2 = Math.min(c, b);
        b -= pairs_3_2;
        int remaining_3 = c - pairs_3_2;
        int fill_1 = Math.min(remaining_3 * 2, a);
        a -= fill_1;

        // 2kg
        int pairs_2 = b / 2;
        baskets += pairs_2;
        if (b % 2 == 1) {
            baskets += 1;
            a = Math.max(0, a - 3);
        }
        a = Math.max(0, a - pairs_2);

        // 1kg
        baskets += (a + 4) / 5;

        System.out.println(baskets);
    }
}
'''
            }
        ]
    },
    "baekjoon_3258": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, z, m = map(int, input().split())
obstacles = set()
if m > 0:
    obstacles = set(map(int, input().split()))

# K = 1부터 N-1까지 시도
for k in range(1, n):
    pos = 1
    visited = set()
    success = True

    while pos != z:
        if pos in visited:
            # 무한 루프
            success = False
            break
        visited.add(pos)

        pos = (pos - 1 + k) % n + 1  # 다음 위치

        if pos in obstacles:
            success = False
            break

    if success:
        print(k)
        break
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

    int n, z, m;
    cin >> n >> z >> m;

    set<int> obstacles;
    for (int i = 0; i < m; i++) {
        int o;
        cin >> o;
        obstacles.insert(o);
    }

    for (int k = 1; k < n; k++) {
        int pos = 1;
        set<int> visited;
        bool success = true;

        while (pos != z) {
            if (visited.count(pos)) {
                success = false;
                break;
            }
            visited.insert(pos);

            pos = (pos - 1 + k) % n + 1;

            if (obstacles.count(pos)) {
                success = false;
                break;
            }
        }

        if (success) {
            cout << k << endl;
            break;
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
        int n = Integer.parseInt(st.nextToken());
        int z = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        Set<Integer> obstacles = new HashSet<>();
        if (m > 0) {
            st = new StringTokenizer(br.readLine());
            for (int i = 0; i < m; i++) {
                obstacles.add(Integer.parseInt(st.nextToken()));
            }
        }

        for (int k = 1; k < n; k++) {
            int pos = 1;
            Set<Integer> visited = new HashSet<>();
            boolean success = true;

            while (pos != z) {
                if (visited.contains(pos)) {
                    success = false;
                    break;
                }
                visited.add(pos);

                pos = (pos - 1 + k) % n + 1;

                if (obstacles.contains(pos)) {
                    success = false;
                    break;
                }
            }

            if (success) {
                System.out.println(k);
                break;
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_25972": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
dominos = []
for _ in range(n):
    a, l = map(int, input().split())
    dominos.append((a, l))

# 위치순 정렬
dominos.sort()

# 각 도미노에서 시작해서 도달 가능한 최대 위치 계산
# 그리디: 현재 도달 가능한 최대 위치까지 모든 도미노 무너뜨림

count = 0
i = 0
while i < n:
    count += 1
    # 현재 도미노 무너뜨리기
    reach = dominos[i][0] + dominos[i][1]

    # 연쇄 반응
    while i + 1 < n and dominos[i + 1][0] <= reach:
        i += 1
        reach = max(reach, dominos[i][0] + dominos[i][1])

    i += 1

print(count)
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

    vector<pair<long long, long long>> dominos(n);
    for (int i = 0; i < n; i++) {
        cin >> dominos[i].first >> dominos[i].second;
    }

    sort(dominos.begin(), dominos.end());

    int count = 0;
    int i = 0;
    while (i < n) {
        count++;
        long long reach = dominos[i].first + dominos[i].second;

        while (i + 1 < n && dominos[i + 1].first <= reach) {
            i++;
            reach = max(reach, dominos[i].first + dominos[i].second);
        }

        i++;
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

        long[][] dominos = new long[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            dominos[i][0] = Long.parseLong(st.nextToken());
            dominos[i][1] = Long.parseLong(st.nextToken());
        }

        Arrays.sort(dominos, (a, b) -> Long.compare(a[0], b[0]));

        int count = 0;
        int i = 0;
        while (i < n) {
            count++;
            long reach = dominos[i][0] + dominos[i][1];

            while (i + 1 < n && dominos[i + 1][0] <= reach) {
                i++;
                reach = Math.max(reach, dominos[i][0] + dominos[i][1]);
            }

            i++;
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_31066": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n, m, k = map(int, input().split())

    # n명, m개 우산, 한 우산에 k명
    # 불가능: n > m * k (모든 우산 최대 사용해도 부족)
    if n > m * k:
        print(-1)
        continue

    # 가능한 경우 최소 시행 횟수
    # 한 번에 최대 m*k명 이동 가능
    # 최소 횟수 = ceil(n / (m * k)) 아님...

    # 생각: 모든 학생이 건너가야 함
    # 한 번에 m개 우산으로 최대 m*k명 이동
    # 우산을 다시 가져오려면 누군가가 돌아와야 함

    # 왕복 필요: 마지막을 제외하고 매번 1명 이상이 우산을 가지고 돌아와야
    # 최소 횟수 = 2*(건너가는 횟수 - 1) + 1

    if m >= n or k * m >= n:
        # 한 번에 모두 건너갈 수 있음
        print(1)
    else:
        # 여러 번 필요
        # 한 번에 m*k명 건너가고, 1명이 돌아옴
        # 실제로 m*k - 1명씩 건너감
        trips = 1
        remaining = n
        while remaining > m * k:
            remaining -= (m * k - 1)
            trips += 2  # 가기 + 돌아오기

        print(trips)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        long long n, m, k;
        cin >> n >> m >> k;

        if (n > m * k) {
            cout << -1 << "\\n";
            continue;
        }

        if (m * k >= n) {
            cout << 1 << "\\n";
        } else {
            long long trips = 1;
            long long remaining = n;
            while (remaining > m * k) {
                remaining -= (m * k - 1);
                trips += 2;
            }
            cout << trips << "\\n";
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
        int t = Integer.parseInt(br.readLine().trim());
        StringBuilder sb = new StringBuilder();

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long n = Long.parseLong(st.nextToken());
            long m = Long.parseLong(st.nextToken());
            long k = Long.parseLong(st.nextToken());

            if (n > m * k) {
                sb.append(-1).append("\\n");
                continue;
            }

            if (m * k >= n) {
                sb.append(1).append("\\n");
            } else {
                long trips = 1;
                long remaining = n;
                while (remaining > m * k) {
                    remaining -= (m * k - 1);
                    trips += 2;
                }
                sb.append(trips).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_14674": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, g = map(int, input().split())

games = []
for _ in range(n):
    i, c, s = map(int, input().split())
    # 만족도/비용 비율이 높은 순으로 선택
    games.append((i, c, s, s / c))

# 비율 높은 순, 비율 같으면 번호 낮은 순
games.sort(key=lambda x: (-x[3], x[0]))

# 상위 g개 선택
selected = []
for i in range(min(g, n)):
    selected.append(games[i][0])

selected.sort()
for idx in selected:
    print(idx)
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

    int n, g;
    cin >> n >> g;

    vector<tuple<double, int, int>> games;  // ratio, -id, id
    for (int i = 0; i < n; i++) {
        int id, c, s;
        cin >> id >> c >> s;
        double ratio = (double)s / c;
        games.push_back({-ratio, id, id});
    }

    sort(games.begin(), games.end());

    vector<int> selected;
    for (int i = 0; i < min(g, n); i++) {
        selected.push_back(get<2>(games[i]));
    }

    sort(selected.begin(), selected.end());

    for (int id : selected) {
        cout << id << "\\n";
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
        int n = Integer.parseInt(st.nextToken());
        int g = Integer.parseInt(st.nextToken());

        double[][] games = new double[n][3];  // id, cost, satisfaction
        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            games[i][0] = Integer.parseInt(st.nextToken());
            games[i][1] = Integer.parseInt(st.nextToken());
            games[i][2] = Integer.parseInt(st.nextToken());
        }

        // 비율 높은 순, 같으면 번호 낮은 순
        Arrays.sort(games, (a, b) -> {
            double ratioA = a[2] / a[1];
            double ratioB = b[2] / b[1];
            if (ratioA != ratioB) {
                return Double.compare(ratioB, ratioA);
            }
            return Double.compare(a[0], b[0]);
        });

        List<Integer> selected = new ArrayList<>();
        for (int i = 0; i < Math.min(g, n); i++) {
            selected.add((int) games[i][0]);
        }

        Collections.sort(selected);

        StringBuilder sb = new StringBuilder();
        for (int id : selected) {
            sb.append(id).append("\\n");
        }
        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_13274": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, k = map(int, input().split())
arr = list(map(int, input().split()))
arr.sort()

for _ in range(k):
    l, r, x = map(int, input().split())
    # 오름차순 정렬 상태에서 L~R 인덱스에 X 더하기
    for i in range(l - 1, r):
        arr[i] += x
    arr.sort()

print(' '.join(map(str, arr)))
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

    int n, k;
    cin >> n >> k;

    vector<long long> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    sort(arr.begin(), arr.end());

    for (int q = 0; q < k; q++) {
        int l, r;
        long long x;
        cin >> l >> r >> x;

        for (int i = l - 1; i < r; i++) {
            arr[i] += x;
        }
        sort(arr.begin(), arr.end());
    }

    for (int i = 0; i < n; i++) {
        if (i > 0) cout << " ";
        cout << arr[i];
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
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        long[] arr = new long[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr[i] = Long.parseLong(st.nextToken());
        }
        Arrays.sort(arr);

        for (int q = 0; q < k; q++) {
            st = new StringTokenizer(br.readLine());
            int l = Integer.parseInt(st.nextToken());
            int r = Integer.parseInt(st.nextToken());
            long x = Long.parseLong(st.nextToken());

            for (int i = l - 1; i < r; i++) {
                arr[i] += x;
            }
            Arrays.sort(arr);
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(" ");
            sb.append(arr[i]);
        }
        System.out.println(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_21557": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
heights = list(map(int, input().split()))

# N-2번 중간 폭죽 터뜨리기, 양 끝 2개 남김
# 각 터뜨림마다 양옆 높이 1씩 감소

# 최종: heights[0]과 heights[n-1]만 남음
# 중간 폭죽 터뜨리면 양옆 -1
# 0번째 옆에서 터뜨리면 heights[0] -= 1
# n-1번째 옆에서 터뜨리면 heights[n-1] -= 1

# 폭죽 i 터뜨리면:
# - i-1 위치에 폭죽 있으면 heights[i-1] -= 1
# - i+1 위치에 폭죽 있으면 heights[i+1] -= 1

# 모든 중간 폭죽을 터뜨리므로:
# heights[0]은 터뜨린 1번 폭죽에 의해 1 감소 (1번이 터뜨려지면)
# heights[n-1]은 터뜨린 n-2번 폭죽에 의해 1 감소

# 실제로 heights[0]과 heights[n-1]이 감소되는 횟수:
# heights[0]: 1번 폭죽이 터뜨려질 때 1 감소
# heights[n-1]: n-2번 폭죽이 터뜨려질 때 1 감소

# 중간 폭죽들은 순서대로 터뜨려지므로 연쇄적 감소
# 최종: heights[0] - (n-2), heights[n-1] - (n-2)

final_0 = heights[0] - (n - 2)
final_n = heights[n - 1] - (n - 2)

print(max(final_0, final_n))
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

    vector<long long> heights(n);
    for (int i = 0; i < n; i++) {
        cin >> heights[i];
    }

    long long final_0 = heights[0] - (n - 2);
    long long final_n = heights[n - 1] - (n - 2);

    cout << max(final_0, final_n) << endl;

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

        long[] heights = new long[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            heights[i] = Long.parseLong(st.nextToken());
        }

        long final_0 = heights[0] - (n - 2);
        long final_n = heights[n - 1] - (n - 2);

        System.out.println(Math.max(final_0, final_n));
    }
}
'''
            }
        ]
    }
}

# 기존 솔루션 로드
with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)

# 새 솔루션 추가
existing.update(new_solutions)

# 저장
with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"총 {len(new_solutions)}개 문제 추가됨")
print(f"현재 총 솔루션 수: {len(existing)}")
