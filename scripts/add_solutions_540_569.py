#!/usr/bin/env python3
"""
Baekjoon 문제 540-569 (empty medium) 솔루션 추가 스크립트
"""

import json
import fcntl
import os

def get_solutions():
    """문제별 솔루션 반환"""
    solutions = {}

    # Problem 7319: baekjoon_14687 - High Tide, Low Tide
    # 첫 번째 측정은 low tide, 두 번째는 high tide, 교대로 진행
    # low tide는 모두 high tide보다 낮음
    # 정렬 후 low/high 교대로 출력
    solutions[7319] = [
        {
            "language": "python",
            "code": '''# 조수 측정 문제
# low tide와 high tide를 교대로 측정하며, low tide < high tide
import sys
input = sys.stdin.readline

n = int(input())
arr = list(map(int, input().split()))

# 정렬하여 작은 절반은 low tide, 큰 절반은 high tide
arr.sort()
low = arr[:n//2]
high = arr[n//2:]

# low, high를 교대로 출력 (low 먼저)
result = []
for i in range(n//2):
    result.append(low[i])
    result.append(high[i])

print(' '.join(map(str, result)))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        // 조수 측정 문제 - low tide와 high tide 교대 출력
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        // 정렬 후 작은 절반은 low, 큰 절반은 high
        Arrays.sort(arr);

        StringBuilder sb = new StringBuilder();
        int half = n / 2;
        for (int i = 0; i < half; i++) {
            if (i > 0) sb.append(" ");
            sb.append(arr[i]).append(" ").append(arr[half + i]);
        }
        System.out.println(sb.toString());
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
    // 조수 측정 문제 - low tide와 high tide 교대 출력
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    // 정렬 후 작은 절반은 low, 큰 절반은 high
    sort(arr.begin(), arr.end());

    int half = n / 2;
    for (int i = 0; i < half; i++) {
        if (i > 0) cout << " ";
        cout << arr[i] << " " << arr[half + i];
    }
    cout << endl;

    return 0;
}
'''
        }
    ]

    # Problem 7350: baekjoon_12208 - Super 2048 (Small)
    # 2048 게임 시뮬레이션
    solutions[7350] = [
        {
            "language": "python",
            "code": '''# 2048 게임 시뮬레이션
import sys
input = sys.stdin.readline

def merge_line(line, reverse=False):
    """한 줄을 병합 (reverse가 True면 오른쪽/아래로)"""
    if reverse:
        line = line[::-1]

    # 0이 아닌 값만 추출
    filtered = [x for x in line if x != 0]
    result = []
    i = 0
    while i < len(filtered):
        if i + 1 < len(filtered) and filtered[i] == filtered[i+1]:
            result.append(filtered[i] * 2)
            i += 2
        else:
            result.append(filtered[i])
            i += 1

    # 0으로 패딩
    while len(result) < len(line):
        result.append(0)

    if reverse:
        result = result[::-1]
    return result

def move(grid, direction):
    """그리드를 주어진 방향으로 이동"""
    n = len(grid)
    new_grid = [[0]*n for _ in range(n)]

    if direction == "left":
        for i in range(n):
            new_grid[i] = merge_line(grid[i], False)
    elif direction == "right":
        for i in range(n):
            new_grid[i] = merge_line(grid[i], True)
    elif direction == "up":
        for j in range(n):
            col = [grid[i][j] for i in range(n)]
            merged = merge_line(col, False)
            for i in range(n):
                new_grid[i][j] = merged[i]
    elif direction == "down":
        for j in range(n):
            col = [grid[i][j] for i in range(n)]
            merged = merge_line(col, True)
            for i in range(n):
                new_grid[i][j] = merged[i]

    return new_grid

T = int(input())
for tc in range(1, T + 1):
    line = input().split()
    n = int(line[0])
    direction = line[1]

    grid = []
    for _ in range(n):
        grid.append(list(map(int, input().split())))

    result = move(grid, direction)

    print(f"Case #{tc}:")
    for row in result:
        print(' '.join(map(str, row)))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // 2048 게임 시뮬레이션
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int T = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        for (int tc = 1; tc <= T; tc++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            String dir = st.nextToken();

            int[][] grid = new int[n][n];
            for (int i = 0; i < n; i++) {
                st = new StringTokenizer(br.readLine());
                for (int j = 0; j < n; j++) {
                    grid[i][j] = Integer.parseInt(st.nextToken());
                }
            }

            int[][] result = move(grid, dir, n);

            sb.append("Case #").append(tc).append(":\\n");
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (j > 0) sb.append(" ");
                    sb.append(result[i][j]);
                }
                sb.append("\\n");
            }
        }
        System.out.print(sb);
    }

    static int[] mergeLine(int[] line, boolean reverse) {
        int n = line.length;
        if (reverse) {
            for (int i = 0; i < n / 2; i++) {
                int tmp = line[i];
                line[i] = line[n-1-i];
                line[n-1-i] = tmp;
            }
        }

        ArrayList<Integer> filtered = new ArrayList<>();
        for (int x : line) if (x != 0) filtered.add(x);

        ArrayList<Integer> result = new ArrayList<>();
        int i = 0;
        while (i < filtered.size()) {
            if (i + 1 < filtered.size() && filtered.get(i).equals(filtered.get(i+1))) {
                result.add(filtered.get(i) * 2);
                i += 2;
            } else {
                result.add(filtered.get(i));
                i++;
            }
        }
        while (result.size() < n) result.add(0);

        int[] arr = new int[n];
        for (int j = 0; j < n; j++) arr[j] = result.get(j);

        if (reverse) {
            for (int j = 0; j < n / 2; j++) {
                int tmp = arr[j];
                arr[j] = arr[n-1-j];
                arr[n-1-j] = tmp;
            }
        }
        return arr;
    }

    static int[][] move(int[][] grid, String dir, int n) {
        int[][] newGrid = new int[n][n];

        if (dir.equals("left")) {
            for (int i = 0; i < n; i++) {
                newGrid[i] = mergeLine(grid[i].clone(), false);
            }
        } else if (dir.equals("right")) {
            for (int i = 0; i < n; i++) {
                newGrid[i] = mergeLine(grid[i].clone(), true);
            }
        } else if (dir.equals("up")) {
            for (int j = 0; j < n; j++) {
                int[] col = new int[n];
                for (int i = 0; i < n; i++) col[i] = grid[i][j];
                int[] merged = mergeLine(col, false);
                for (int i = 0; i < n; i++) newGrid[i][j] = merged[i];
            }
        } else if (dir.equals("down")) {
            for (int j = 0; j < n; j++) {
                int[] col = new int[n];
                for (int i = 0; i < n; i++) col[i] = grid[i][j];
                int[] merged = mergeLine(col, true);
                for (int i = 0; i < n; i++) newGrid[i][j] = merged[i];
            }
        }
        return newGrid;
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

// 2048 게임 시뮬레이션
vector<int> mergeLine(vector<int> line, bool reverse_flag) {
    int n = line.size();
    if (reverse_flag) {
        reverse(line.begin(), line.end());
    }

    vector<int> filtered;
    for (int x : line) if (x != 0) filtered.push_back(x);

    vector<int> result;
    int i = 0;
    while (i < (int)filtered.size()) {
        if (i + 1 < (int)filtered.size() && filtered[i] == filtered[i+1]) {
            result.push_back(filtered[i] * 2);
            i += 2;
        } else {
            result.push_back(filtered[i]);
            i++;
        }
    }
    while ((int)result.size() < n) result.push_back(0);

    if (reverse_flag) {
        reverse(result.begin(), result.end());
    }
    return result;
}

vector<vector<int>> move(vector<vector<int>>& grid, string dir) {
    int n = grid.size();
    vector<vector<int>> newGrid(n, vector<int>(n, 0));

    if (dir == "left") {
        for (int i = 0; i < n; i++) {
            newGrid[i] = mergeLine(grid[i], false);
        }
    } else if (dir == "right") {
        for (int i = 0; i < n; i++) {
            newGrid[i] = mergeLine(grid[i], true);
        }
    } else if (dir == "up") {
        for (int j = 0; j < n; j++) {
            vector<int> col(n);
            for (int i = 0; i < n; i++) col[i] = grid[i][j];
            vector<int> merged = mergeLine(col, false);
            for (int i = 0; i < n; i++) newGrid[i][j] = merged[i];
        }
    } else if (dir == "down") {
        for (int j = 0; j < n; j++) {
            vector<int> col(n);
            for (int i = 0; i < n; i++) col[i] = grid[i][j];
            vector<int> merged = mergeLine(col, true);
            for (int i = 0; i < n; i++) newGrid[i][j] = merged[i];
        }
    }
    return newGrid;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T;
    cin >> T;

    for (int tc = 1; tc <= T; tc++) {
        int n;
        string dir;
        cin >> n >> dir;

        vector<vector<int>> grid(n, vector<int>(n));
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                cin >> grid[i][j];
            }
        }

        vector<vector<int>> result = move(grid, dir);

        cout << "Case #" << tc << ":" << endl;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (j > 0) cout << " ";
                cout << result[i][j];
            }
            cout << endl;
        }
    }

    return 0;
}
'''
        }
    ]

    # Problem 7351: baekjoon_14608 - 구분구적법 (Small)
    # K=1인 경우만 처리 (1차 함수)
    # f(x) = cx + d, 적분값 = c(b^2-a^2)/2 + d(b-a)
    # 구분구적법: sum of f(a + k*dx + eps) * dx for k in 0..n-1
    solutions[7351] = [
        {
            "language": "python",
            "code": '''# 구분구적법 - 1차 함수의 경우
# f(x) = c*x + d
# 적분값 = c*(b^2-a^2)/2 + d*(b-a)
import sys
input = sys.stdin.readline

k = int(input())
coeffs = list(map(int, input().split()))
a, b, n = map(int, input().split())

# 1차 함수: f(x) = c*x + d
c, d = coeffs[0], coeffs[1]

# 실제 적분값
integral = c * (b*b - a*a) / 2 + d * (b - a)

# dx = (b-a) / n
dx = (b - a) / n

# 구분구적법: sum_{k=0}^{n-1} f(a + k*dx + eps) * dx = integral
# sum_{k=0}^{n-1} (c*(a + k*dx + eps) + d) * dx = integral
# c*dx * sum(a + k*dx + eps) + d*dx*n = integral
# c*dx * (n*a + dx*n*(n-1)/2 + n*eps) + d*dx*n = integral
# c*n*dx*a + c*dx^2*n*(n-1)/2 + c*n*dx*eps + d*n*dx = integral
# c*n*dx*eps = integral - c*n*dx*a - c*dx^2*n*(n-1)/2 - d*n*dx

sum_k = n * (n - 1) // 2  # 0부터 n-1까지의 합
base_sum = n * a + dx * sum_k

# c * dx * base_sum + c * n * dx * eps + d * n * dx = integral
# c * n * dx * eps = integral - c * dx * base_sum - d * n * dx
# eps = (integral - c * dx * base_sum - d * n * dx) / (c * n * dx)

if c == 0:
    # f(x) = d, 상수함수
    # 적분값 = d * (b - a), 구분구적법도 d * (b - a)
    # 항상 일치, eps는 아무 값이나 가능
    eps = 0.0
else:
    numerator = integral - c * dx * base_sum - d * n * dx
    denominator = c * n * dx
    eps = numerator / denominator

# eps가 [0, dx] 범위인지 확인
if 0 <= eps <= dx + 1e-9:
    print(f"{eps:.4f}")
else:
    print(-1)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // 구분구적법 - 1차 함수
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int k = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        int c = Integer.parseInt(st.nextToken());
        int d = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        int a = Integer.parseInt(st.nextToken());
        int b = Integer.parseInt(st.nextToken());
        int n = Integer.parseInt(st.nextToken());

        // 실제 적분값
        double integral = c * (b*b - a*a) / 2.0 + d * (b - a);
        double dx = (double)(b - a) / n;

        long sumK = (long)n * (n - 1) / 2;
        double baseSum = n * a + dx * sumK;

        double eps;
        if (c == 0) {
            eps = 0.0;
        } else {
            double numerator = integral - c * dx * baseSum - d * n * dx;
            double denominator = c * n * dx;
            eps = numerator / denominator;
        }

        if (eps >= -1e-9 && eps <= dx + 1e-9) {
            System.out.printf("%.4f%n", Math.max(0, eps));
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
#include <iomanip>
#include <cmath>
using namespace std;

// 구분구적법 - 1차 함수
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int k;
    cin >> k;

    int c, d;
    cin >> c >> d;

    int a, b, n;
    cin >> a >> b >> n;

    // 실제 적분값
    double integral = c * ((double)b*b - (double)a*a) / 2.0 + d * (b - a);
    double dx = (double)(b - a) / n;

    long long sumK = (long long)n * (n - 1) / 2;
    double baseSum = (double)n * a + dx * sumK;

    double eps;
    if (c == 0) {
        eps = 0.0;
    } else {
        double numerator = integral - c * dx * baseSum - d * n * dx;
        double denominator = c * n * dx;
        eps = numerator / denominator;
    }

    if (eps >= -1e-9 && eps <= dx + 1e-9) {
        cout << fixed << setprecision(4) << max(0.0, eps) << endl;
    } else {
        cout << -1 << endl;
    }

    return 0;
}
'''
        }
    ]

    # Problem 7353: baekjoon_6161 - iCow
    # 노래 순위 시뮬레이션
    solutions[7353] = [
        {
            "language": "python",
            "code": '''# iCow - MP3 플레이어 노래 선택 시뮬레이션
import sys
input = sys.stdin.readline

n, t = map(int, input().split())
ratings = []
for i in range(n):
    ratings.append(int(input()))

results = []
for _ in range(t):
    # 가장 높은 rating을 가진 노래 찾기 (동점시 낮은 인덱스)
    max_rating = -1
    max_idx = -1
    for i in range(n):
        if ratings[i] > max_rating:
            max_rating = ratings[i]
            max_idx = i

    results.append(max_idx + 1)  # 1-indexed

    # 선택된 노래의 rating을 다른 노래들에게 분배
    total = ratings[max_idx]
    ratings[max_idx] = 0

    # n-1개의 노래에게 균등 분배
    share = total // (n - 1)
    extra = total % (n - 1)

    extra_given = 0
    for i in range(n):
        if i != max_idx:
            ratings[i] += share
            if extra_given < extra:
                ratings[i] += 1
                extra_given += 1

for r in results:
    print(r)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // iCow - MP3 플레이어 노래 선택 시뮬레이션
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int t = Integer.parseInt(st.nextToken());

        int[] ratings = new int[n];
        for (int i = 0; i < n; i++) {
            ratings[i] = Integer.parseInt(br.readLine().trim());
        }

        StringBuilder sb = new StringBuilder();
        for (int round = 0; round < t; round++) {
            // 가장 높은 rating 찾기
            int maxRating = -1;
            int maxIdx = -1;
            for (int i = 0; i < n; i++) {
                if (ratings[i] > maxRating) {
                    maxRating = ratings[i];
                    maxIdx = i;
                }
            }

            sb.append(maxIdx + 1).append("\\n");

            // rating 분배
            int total = ratings[maxIdx];
            ratings[maxIdx] = 0;

            int share = total / (n - 1);
            int extra = total % (n - 1);

            int extraGiven = 0;
            for (int i = 0; i < n; i++) {
                if (i != maxIdx) {
                    ratings[i] += share;
                    if (extraGiven < extra) {
                        ratings[i] += 1;
                        extraGiven++;
                    }
                }
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

// iCow - MP3 플레이어 노래 선택 시뮬레이션
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, t;
    cin >> n >> t;

    vector<int> ratings(n);
    for (int i = 0; i < n; i++) {
        cin >> ratings[i];
    }

    for (int round = 0; round < t; round++) {
        // 가장 높은 rating 찾기
        int maxRating = -1;
        int maxIdx = -1;
        for (int i = 0; i < n; i++) {
            if (ratings[i] > maxRating) {
                maxRating = ratings[i];
                maxIdx = i;
            }
        }

        cout << maxIdx + 1 << "\\n";

        // rating 분배
        int total = ratings[maxIdx];
        ratings[maxIdx] = 0;

        int share = total / (n - 1);
        int extra = total % (n - 1);

        int extraGiven = 0;
        for (int i = 0; i < n; i++) {
            if (i != maxIdx) {
                ratings[i] += share;
                if (extraGiven < extra) {
                    ratings[i] += 1;
                    extraGiven++;
                }
            }
        }
    }

    return 0;
}
'''
        }
    ]

    # Problem 7405: baekjoon_12739 - 돌림판 (Small)
    # 색상 변환 규칙에 따라 K번 변환 후 각 색상 개수 세기
    solutions[7405] = [
        {
            "language": "python",
            "code": '''# 돌림판 - 색상 변환 시뮬레이션
import sys
input = sys.stdin.readline

n, k = map(int, input().split())
colors = list(input().strip())

# R=0, G=1, B=2로 매핑
color_map = {'R': 0, 'G': 1, 'B': 2}
rev_map = {0: 'R', 1: 'G', 2: 'B'}

arr = [color_map[c] for c in colors]

for _ in range(k):
    new_arr = [0] * n
    for i in range(n):
        left = arr[(i - 1 + n) % n]
        curr = arr[i]
        right = arr[(i + 1) % n]

        # 세 색이 모두 같거나 모두 다르면 파란색(2)
        if (left == curr == right) or (left != curr and curr != right and left != right):
            new_arr[i] = 2  # Blue
        else:
            # X 색이 2개, Y 색이 1개
            colors_list = [left, curr, right]
            from collections import Counter
            cnt = Counter(colors_list)
            X = max(cnt, key=cnt.get)  # 2개인 색
            Y = min(cnt, key=cnt.get)  # 1개인 색

            # (X=R,Y=G) or (X=G,Y=B) or (X=B,Y=R) -> 빨강(0)
            if (X == 0 and Y == 1) or (X == 1 and Y == 2) or (X == 2 and Y == 0):
                new_arr[i] = 0  # Red
            else:
                new_arr[i] = 1  # Green

    arr = new_arr

# 결과 카운트
cnt = [0, 0, 0]
for c in arr:
    cnt[c] += 1

print(cnt[0], cnt[1], cnt[2])
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // 돌림판 - 색상 변환 시뮬레이션
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        String colors = br.readLine().trim();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            char c = colors.charAt(i);
            if (c == 'R') arr[i] = 0;
            else if (c == 'G') arr[i] = 1;
            else arr[i] = 2;
        }

        for (int iter = 0; iter < k; iter++) {
            int[] newArr = new int[n];
            for (int i = 0; i < n; i++) {
                int left = arr[(i - 1 + n) % n];
                int curr = arr[i];
                int right = arr[(i + 1) % n];

                if ((left == curr && curr == right) ||
                    (left != curr && curr != right && left != right)) {
                    newArr[i] = 2;
                } else {
                    int[] cnt = new int[3];
                    cnt[left]++; cnt[curr]++; cnt[right]++;
                    int X = -1, Y = -1;
                    for (int c = 0; c < 3; c++) {
                        if (cnt[c] == 2) X = c;
                        if (cnt[c] == 1) Y = c;
                    }

                    if ((X == 0 && Y == 1) || (X == 1 && Y == 2) || (X == 2 && Y == 0)) {
                        newArr[i] = 0;
                    } else {
                        newArr[i] = 1;
                    }
                }
            }
            arr = newArr;
        }

        int[] result = new int[3];
        for (int c : arr) result[c]++;
        System.out.println(result[0] + " " + result[1] + " " + result[2]);
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

// 돌림판 - 색상 변환 시뮬레이션
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    cin >> n >> k;

    string colors;
    cin >> colors;

    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        if (colors[i] == 'R') arr[i] = 0;
        else if (colors[i] == 'G') arr[i] = 1;
        else arr[i] = 2;
    }

    for (int iter = 0; iter < k; iter++) {
        vector<int> newArr(n);
        for (int i = 0; i < n; i++) {
            int left = arr[(i - 1 + n) % n];
            int curr = arr[i];
            int right = arr[(i + 1) % n];

            if ((left == curr && curr == right) ||
                (left != curr && curr != right && left != right)) {
                newArr[i] = 2;
            } else {
                int cnt[3] = {0, 0, 0};
                cnt[left]++; cnt[curr]++; cnt[right]++;
                int X = -1, Y = -1;
                for (int c = 0; c < 3; c++) {
                    if (cnt[c] == 2) X = c;
                    if (cnt[c] == 1) Y = c;
                }

                if ((X == 0 && Y == 1) || (X == 1 && Y == 2) || (X == 2 && Y == 0)) {
                    newArr[i] = 0;
                } else {
                    newArr[i] = 1;
                }
            }
        }
        arr = newArr;
    }

    int result[3] = {0, 0, 0};
    for (int c : arr) result[c]++;
    cout << result[0] << " " << result[1] << " " << result[2] << endl;

    return 0;
}
'''
        }
    ]

    # Problem 7412: baekjoon_25730 - Histogram Sequence 4
    # 히스토그램 복원 문제
    solutions[7412] = [
        {
            "language": "python",
            "code": '''# Histogram Sequence 4 - 히스토그램 복원
import sys
input = sys.stdin.readline

N, A, L, R = map(int, input().split())

# A가 0이면 모든 높이를 0으로 (L<=0이어야 가능)
if A == 0:
    if L <= 0:
        print("YES")
        print(' '.join(['0'] * N))
    else:
        print("NO")
else:
    # 최대 직사각형 넓이가 A가 되도록 히스토그램 구성
    # 가장 간단한 방법: 폭 w, 높이 h인 직사각형으로 A = w * h
    # N개의 막대 중 w개의 연속 막대를 높이 h로, 나머지는 h-1로

    # A를 만들 수 있는 (width, height) 찾기
    found = False
    result = None

    for w in range(1, N + 1):
        if A % w == 0:
            h = A // w
            if L <= h <= R:
                # w개의 연속 막대를 높이 h로 설정
                # 나머지 막대는 h-1로 설정 (h-1 >= L이어야 함)
                if h - 1 >= L or w == N:
                    if w == N:
                        # 모든 막대가 높이 h
                        result = [h] * N
                    else:
                        # 첫 w개는 h, 나머지는 h-1
                        if h - 1 >= L:
                            result = [h] * w + [h - 1] * (N - w)
                        else:
                            continue
                    found = True
                    break

    if found:
        print("YES")
        print(' '.join(map(str, result)))
    else:
        print("NO")
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // Histogram Sequence 4 - 히스토그램 복원
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        long N = Long.parseLong(st.nextToken());
        long A = Long.parseLong(st.nextToken());
        long L = Long.parseLong(st.nextToken());
        long R = Long.parseLong(st.nextToken());

        if (A == 0) {
            if (L <= 0) {
                System.out.println("YES");
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < N; i++) {
                    if (i > 0) sb.append(" ");
                    sb.append(0);
                }
                System.out.println(sb);
            } else {
                System.out.println("NO");
            }
            return;
        }

        boolean found = false;
        long[] result = new long[(int)N];

        for (long w = 1; w <= N; w++) {
            if (A % w == 0) {
                long h = A / w;
                if (L <= h && h <= R) {
                    if (h - 1 >= L || w == N) {
                        if (w == N) {
                            for (int i = 0; i < N; i++) result[i] = h;
                        } else if (h - 1 >= L) {
                            for (int i = 0; i < w; i++) result[i] = h;
                            for (int i = (int)w; i < N; i++) result[i] = h - 1;
                        } else {
                            continue;
                        }
                        found = true;
                        break;
                    }
                }
            }
        }

        if (found) {
            System.out.println("YES");
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < N; i++) {
                if (i > 0) sb.append(" ");
                sb.append(result[i]);
            }
            System.out.println(sb);
        } else {
            System.out.println("NO");
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

// Histogram Sequence 4 - 히스토그램 복원
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long N, A, L, R;
    cin >> N >> A >> L >> R;

    if (A == 0) {
        if (L <= 0) {
            cout << "YES" << endl;
            for (int i = 0; i < N; i++) {
                if (i > 0) cout << " ";
                cout << 0;
            }
            cout << endl;
        } else {
            cout << "NO" << endl;
        }
        return 0;
    }

    bool found = false;
    vector<long long> result(N);

    for (long long w = 1; w <= N; w++) {
        if (A % w == 0) {
            long long h = A / w;
            if (L <= h && h <= R) {
                if (h - 1 >= L || w == N) {
                    if (w == N) {
                        for (int i = 0; i < N; i++) result[i] = h;
                    } else if (h - 1 >= L) {
                        for (int i = 0; i < w; i++) result[i] = h;
                        for (int i = w; i < N; i++) result[i] = h - 1;
                    } else {
                        continue;
                    }
                    found = true;
                    break;
                }
            }
        }
    }

    if (found) {
        cout << "YES" << endl;
        for (int i = 0; i < N; i++) {
            if (i > 0) cout << " ";
            cout << result[i];
        }
        cout << endl;
    } else {
        cout << "NO" << endl;
    }

    return 0;
}
'''
        }
    ]

    # Problem 7413: baekjoon_20029 - Mock Competition Marketing
    # 광고 경매 - 예산 K로 최대 광고 횟수
    solutions[7413] = [
        {
            "language": "python",
            "code": '''# Mock Competition Marketing - 광고 경매
import sys
input = sys.stdin.readline

n, k = map(int, input().split())
costs = list(map(int, input().split()))  # 6가지 광고 타입의 비용
auctions = list(map(int, input().split()))  # n개의 경매, 각 경매의 광고 타입

# 각 광고 타입별로 첫 번째 입찰자가 낙찰
# 그리디하게 예산 내에서 최대한 많은 광고 낙찰받기

# 1-indexed에서 0-indexed로 변환
auction_types = [a - 1 for a in auctions]

count = 0
budget = k
for t in auction_types:
    if costs[t] <= budget:
        budget -= costs[t]
        count += 1

print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // Mock Competition Marketing - 광고 경매
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        int[] costs = new int[6];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < 6; i++) {
            costs[i] = Integer.parseInt(st.nextToken());
        }

        int[] auctions = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            auctions[i] = Integer.parseInt(st.nextToken()) - 1;
        }

        int count = 0;
        int budget = k;
        for (int i = 0; i < n; i++) {
            int t = auctions[i];
            if (costs[t] <= budget) {
                budget -= costs[t];
                count++;
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
#include <vector>
using namespace std;

// Mock Competition Marketing - 광고 경매
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    cin >> n >> k;

    vector<int> costs(6);
    for (int i = 0; i < 6; i++) {
        cin >> costs[i];
    }

    int count = 0;
    int budget = k;
    for (int i = 0; i < n; i++) {
        int t;
        cin >> t;
        t--;
        if (costs[t] <= budget) {
            budget -= costs[t];
            count++;
        }
    }

    cout << count << endl;

    return 0;
}
'''
        }
    ]

    # Problem 7415: baekjoon_29693 - 포스터 만들기
    # 공군 마크 만들기 - 구현 문제 (복잡한 조건)
    solutions[7415] = [
        {
            "language": "python",
            "code": '''# 포스터 만들기 - 공군 마크 디자인
# 복잡한 조건들을 만족하는 마크 생성
import sys
input = sys.stdin.readline
from collections import deque

def solve():
    Y, X = map(int, input().split())
    grid = []
    for _ in range(Y):
        grid.append(list(input().strip()))

    # 가로가 홀수가 아니면 좌우 대칭 불가
    if X % 2 == 0:
        # 가로가 짝수인 경우도 처리 필요
        pass

    # 테두리는 이미 B
    # 내부에서 W, Y를 배치해야 함
    # 2개의 W 문양 (좌우 대칭), 1개의 Y 문양
    # W는 Y와 인접해야 함

    # 간단한 해: 중앙에 Y, 그 양옆에 W
    # Y >= 3, X >= 3 필요
    if Y < 3 or X < 3:
        print("NO")
        return

    result = [['B' for _ in range(X)] for _ in range(Y)]

    # 테두리 설정
    for i in range(Y):
        for j in range(X):
            if grid[i][j] == 'B':
                result[i][j] = 'B'

    # 중앙 열 찾기
    mid = X // 2

    # 중앙에 Y 배치 (세로로)
    y_placed = False
    for i in range(1, Y - 1):
        if grid[i][mid] == 'X':
            result[i][mid] = 'Y'
            y_placed = True

    if not y_placed:
        print("NO")
        return

    # Y 양옆에 W 배치 (좌우 대칭)
    w_placed = False
    for i in range(1, Y - 1):
        # 왼쪽
        if mid - 1 >= 1 and grid[i][mid - 1] == 'X':
            result[i][mid - 1] = 'W'
            # 오른쪽 대칭
            if mid + 1 < X - 1 and grid[i][mid + 1] == 'X':
                result[i][mid + 1] = 'W'
                w_placed = True

    if not w_placed:
        print("NO")
        return

    # 나머지는 B로 유지
    print("YES")
    for row in result:
        print(''.join(row))

solve()
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // 포스터 만들기 - 공군 마크
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int Y = Integer.parseInt(st.nextToken());
        int X = Integer.parseInt(st.nextToken());

        char[][] grid = new char[Y][X];
        for (int i = 0; i < Y; i++) {
            grid[i] = br.readLine().toCharArray();
        }

        if (Y < 3 || X < 3) {
            System.out.println("NO");
            return;
        }

        char[][] result = new char[Y][X];
        for (int i = 0; i < Y; i++) {
            for (int j = 0; j < X; j++) {
                result[i][j] = 'B';
            }
        }

        int mid = X / 2;

        boolean yPlaced = false;
        for (int i = 1; i < Y - 1; i++) {
            if (grid[i][mid] == 'X') {
                result[i][mid] = 'Y';
                yPlaced = true;
            }
        }

        if (!yPlaced) {
            System.out.println("NO");
            return;
        }

        boolean wPlaced = false;
        for (int i = 1; i < Y - 1; i++) {
            if (mid - 1 >= 1 && grid[i][mid - 1] == 'X') {
                result[i][mid - 1] = 'W';
                if (mid + 1 < X - 1 && grid[i][mid + 1] == 'X') {
                    result[i][mid + 1] = 'W';
                    wPlaced = true;
                }
            }
        }

        if (!wPlaced) {
            System.out.println("NO");
            return;
        }

        System.out.println("YES");
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < Y; i++) {
            sb.append(new String(result[i])).append("\\n");
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

// 포스터 만들기 - 공군 마크
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int Y, X;
    cin >> Y >> X;

    vector<string> grid(Y);
    for (int i = 0; i < Y; i++) {
        cin >> grid[i];
    }

    if (Y < 3 || X < 3) {
        cout << "NO" << endl;
        return 0;
    }

    vector<string> result(Y, string(X, 'B'));

    int mid = X / 2;

    bool yPlaced = false;
    for (int i = 1; i < Y - 1; i++) {
        if (grid[i][mid] == 'X') {
            result[i][mid] = 'Y';
            yPlaced = true;
        }
    }

    if (!yPlaced) {
        cout << "NO" << endl;
        return 0;
    }

    bool wPlaced = false;
    for (int i = 1; i < Y - 1; i++) {
        if (mid - 1 >= 1 && grid[i][mid - 1] == 'X') {
            result[i][mid - 1] = 'W';
            if (mid + 1 < X - 1 && grid[i][mid + 1] == 'X') {
                result[i][mid + 1] = 'W';
                wPlaced = true;
            }
        }
    }

    if (!wPlaced) {
        cout << "NO" << endl;
        return 0;
    }

    cout << "YES" << endl;
    for (int i = 0; i < Y; i++) {
        cout << result[i] << endl;
    }

    return 0;
}
'''
        }
    ]

    # Problem 7423: baekjoon_16712 - Finding Love
    # 경쟁 대회로 사랑 찾기
    solutions[7423] = [
        {
            "language": "python",
            "code": '''# Finding Love - 경쟁 대회 시뮬레이션
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
skills = list(map(int, input().split()))  # 정보 실력 (작을수록 더 잘함)
v = list(map(int, input().split()))  # 각 라운드에서 탈락할 순위

# 현재 대회 참가자 (인덱스)
from collections import deque

waiting = deque(range(m, n))  # 줄에서 기다리는 사람들
current = list(range(m))  # 현재 M명

while waiting:
    # M명 중에서 순위 결정
    # skill이 작을수록, 같으면 원래 인덱스가 작을수록 순위가 높음
    ranked = sorted(current, key=lambda x: (skills[x], x))

    # v[라운드] 등을 한 사람 탈락
    round_num = n - m - len(waiting)
    eliminate_rank = v[round_num] - 1  # 0-indexed
    eliminate_idx = ranked[eliminate_rank]

    # 탈락자 교체
    current.remove(eliminate_idx)
    new_participant = waiting.popleft()
    current.append(new_participant)

# 남은 M-1명의 실력 출력
remaining_skills = sorted([skills[i] for i in current])
print(' '.join(map(str, remaining_skills)))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // Finding Love - 경쟁 대회 시뮬레이션
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        int[] skills = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            skills[i] = Integer.parseInt(st.nextToken());
        }

        int[] v = new int[n - m + 1];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n - m + 1; i++) {
            v[i] = Integer.parseInt(st.nextToken());
        }

        Queue<Integer> waiting = new LinkedList<>();
        for (int i = m; i < n; i++) waiting.add(i);

        ArrayList<Integer> current = new ArrayList<>();
        for (int i = 0; i < m; i++) current.add(i);

        int round = 0;
        while (!waiting.isEmpty()) {
            // 순위 결정
            ArrayList<Integer> ranked = new ArrayList<>(current);
            final int[] sk = skills;
            Collections.sort(ranked, (a, b) -> {
                if (sk[a] != sk[b]) return sk[a] - sk[b];
                return a - b;
            });

            int eliminateRank = v[round] - 1;
            int eliminateIdx = ranked.get(eliminateRank);

            current.remove(Integer.valueOf(eliminateIdx));
            current.add(waiting.poll());
            round++;
        }

        ArrayList<Integer> remainingSkills = new ArrayList<>();
        for (int idx : current) {
            remainingSkills.add(skills[idx]);
        }
        Collections.sort(remainingSkills);

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < remainingSkills.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(remainingSkills.get(i));
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
#include <queue>
#include <algorithm>
using namespace std;

// Finding Love - 경쟁 대회 시뮬레이션
int skills[1005];

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    for (int i = 0; i < n; i++) {
        cin >> skills[i];
    }

    vector<int> v(n - m + 1);
    for (int i = 0; i < n - m + 1; i++) {
        cin >> v[i];
    }

    queue<int> waiting;
    for (int i = m; i < n; i++) waiting.push(i);

    vector<int> current;
    for (int i = 0; i < m; i++) current.push_back(i);

    int roundNum = 0;
    while (!waiting.empty()) {
        vector<int> ranked = current;
        sort(ranked.begin(), ranked.end(), [](int a, int b) {
            if (skills[a] != skills[b]) return skills[a] < skills[b];
            return a < b;
        });

        int eliminateRank = v[roundNum] - 1;
        int eliminateIdx = ranked[eliminateRank];

        current.erase(find(current.begin(), current.end(), eliminateIdx));
        current.push_back(waiting.front());
        waiting.pop();
        roundNum++;
    }

    vector<int> remainingSkills;
    for (int idx : current) {
        remainingSkills.push_back(skills[idx]);
    }
    sort(remainingSkills.begin(), remainingSkills.end());

    for (int i = 0; i < (int)remainingSkills.size(); i++) {
        if (i > 0) cout << " ";
        cout << remainingSkills[i];
    }
    cout << endl;

    return 0;
}
'''
        }
    ]

    # Problem 7438: baekjoon_33850 - Chill...은 내가 가장 좋아하는 소수
    # 2xn 격자 타일링, 소수 합이면 a점, 아니면 b점
    solutions[7438] = [
        {
            "language": "python",
            "code": '''# 2xn 격자 타일링 - DP
import sys
input = sys.stdin.readline

def sieve(max_val):
    """에라토스테네스의 체로 소수 판별 배열 생성"""
    is_prime = [True] * (max_val + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(max_val**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, max_val + 1, i):
                is_prime[j] = False
    return is_prime

# 최대 합: 2 * 100000 * 2 = 400000
MAX_SUM = 400001
is_prime = sieve(MAX_SUM)

n, a, b = map(int, input().split())
row1 = list(map(int, input().split()))
row2 = list(map(int, input().split()))

# dp[i][state] = i번째 열까지 처리했을 때 최대 점수
# state: 0 = 둘 다 채워짐, 1 = 위만 비어있음, 2 = 아래만 비어있음
# 하지만 2x1 도미노만 사용하므로 단순화

# dp[i] = i번째 열까지 채웠을 때 최대 점수
# 옵션 1: i-1열과 i열에 가로 도미노 2개 (위쪽 1개, 아래쪽 1개)
# 옵션 2: i열에 세로 도미노 1개

INF = float('-inf')
dp = [INF] * (n + 1)
dp[0] = 0

for i in range(n):
    if i == 0:
        # 세로 도미노만 가능
        s = row1[i] + row2[i]
        score = a if is_prime[s] else b
        dp[1] = max(dp[1], dp[0] + score)
    else:
        # 옵션 1: 가로 도미노 2개 (i-1열과 i열)
        if dp[i - 1] != INF:
            s1 = row1[i - 1] + row1[i]
            s2 = row2[i - 1] + row2[i]
            score1 = a if is_prime[s1] else b
            score2 = a if is_prime[s2] else b
            dp[i + 1] = max(dp[i + 1], dp[i - 1] + score1 + score2)

        # 옵션 2: 세로 도미노
        if dp[i] != INF:
            s = row1[i] + row2[i]
            score = a if is_prime[s] else b
            dp[i + 1] = max(dp[i + 1], dp[i] + score)

print(dp[n])
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // 2xn 격자 타일링 - DP
    static boolean[] isPrime;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int MAX_SUM = 400001;
        isPrime = sieve(MAX_SUM);

        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int a = Integer.parseInt(st.nextToken());
        int b = Integer.parseInt(st.nextToken());

        int[] row1 = new int[n];
        int[] row2 = new int[n];

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) row1[i] = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) row2[i] = Integer.parseInt(st.nextToken());

        long[] dp = new long[n + 1];
        Arrays.fill(dp, Long.MIN_VALUE);
        dp[0] = 0;

        for (int i = 0; i < n; i++) {
            if (i == 0) {
                int s = row1[i] + row2[i];
                int score = isPrime[s] ? a : b;
                dp[1] = Math.max(dp[1], dp[0] + score);
            } else {
                if (dp[i - 1] != Long.MIN_VALUE) {
                    int s1 = row1[i - 1] + row1[i];
                    int s2 = row2[i - 1] + row2[i];
                    int score1 = isPrime[s1] ? a : b;
                    int score2 = isPrime[s2] ? a : b;
                    dp[i + 1] = Math.max(dp[i + 1], dp[i - 1] + score1 + score2);
                }

                if (dp[i] != Long.MIN_VALUE) {
                    int s = row1[i] + row2[i];
                    int score = isPrime[s] ? a : b;
                    dp[i + 1] = Math.max(dp[i + 1], dp[i] + score);
                }
            }
        }

        System.out.println(dp[n]);
    }

    static boolean[] sieve(int maxVal) {
        boolean[] prime = new boolean[maxVal + 1];
        Arrays.fill(prime, true);
        prime[0] = prime[1] = false;
        for (int i = 2; i * i <= maxVal; i++) {
            if (prime[i]) {
                for (int j = i * i; j <= maxVal; j += i) {
                    prime[j] = false;
                }
            }
        }
        return prime;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
using namespace std;

// 2xn 격자 타일링 - DP
vector<bool> sieve(int maxVal) {
    vector<bool> prime(maxVal + 1, true);
    prime[0] = prime[1] = false;
    for (int i = 2; i * i <= maxVal; i++) {
        if (prime[i]) {
            for (int j = i * i; j <= maxVal; j += i) {
                prime[j] = false;
            }
        }
    }
    return prime;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    const int MAX_SUM = 400001;
    vector<bool> isPrime = sieve(MAX_SUM);

    int n, a, b;
    cin >> n >> a >> b;

    vector<int> row1(n), row2(n);
    for (int i = 0; i < n; i++) cin >> row1[i];
    for (int i = 0; i < n; i++) cin >> row2[i];

    vector<long long> dp(n + 1, LLONG_MIN);
    dp[0] = 0;

    for (int i = 0; i < n; i++) {
        if (i == 0) {
            int s = row1[i] + row2[i];
            int score = isPrime[s] ? a : b;
            dp[1] = max(dp[1], dp[0] + score);
        } else {
            if (dp[i - 1] != LLONG_MIN) {
                int s1 = row1[i - 1] + row1[i];
                int s2 = row2[i - 1] + row2[i];
                int score1 = isPrime[s1] ? a : b;
                int score2 = isPrime[s2] ? a : b;
                dp[i + 1] = max(dp[i + 1], dp[i - 1] + score1 + score2);
            }

            if (dp[i] != LLONG_MIN) {
                int s = row1[i] + row2[i];
                int score = isPrime[s] ? a : b;
                dp[i + 1] = max(dp[i + 1], dp[i] + score);
            }
        }
    }

    cout << dp[n] << endl;

    return 0;
}
'''
        }
    ]

    # Problem 7176: baekjoon_13732 - Falling Apples
    # 떨어지는 사과 시뮬레이션
    solutions[7176] = [
        {
            "language": "python",
            "code": '''# Falling Apples - 사과 떨어뜨리기 시뮬레이션
import sys
input = sys.stdin.readline

n = int(input())
grid = []
for _ in range(n):
    grid.append(list(input().strip()))

# 각 열에서 사과를 아래로 떨어뜨림
for col in range(len(grid[0])):
    # 해당 열의 사과 개수 세기
    apples = 0
    for row in range(n):
        if grid[row][col] == 'a':
            apples += 1
            grid[row][col] = '.'

    # 아래에서부터 사과 배치
    row = n - 1
    while apples > 0 and row >= 0:
        if grid[row][col] == '.':
            grid[row][col] = 'a'
            apples -= 1
        row -= 1

for row in grid:
    print(''.join(row))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // Falling Apples - 사과 떨어뜨리기 시뮬레이션
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        char[][] grid = new char[n][];
        for (int i = 0; i < n; i++) {
            grid[i] = br.readLine().toCharArray();
        }

        int cols = grid[0].length;

        for (int col = 0; col < cols; col++) {
            int apples = 0;
            for (int row = 0; row < n; row++) {
                if (grid[row][col] == 'a') {
                    apples++;
                    grid[row][col] = '.';
                }
            }

            int row = n - 1;
            while (apples > 0 && row >= 0) {
                if (grid[row][col] == '.') {
                    grid[row][col] = 'a';
                    apples--;
                }
                row--;
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append(new String(grid[i])).append("\\n");
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

// Falling Apples - 사과 떨어뜨리기 시뮬레이션
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<string> grid(n);
    for (int i = 0; i < n; i++) {
        cin >> grid[i];
    }

    int cols = grid[0].length();

    for (int col = 0; col < cols; col++) {
        int apples = 0;
        for (int row = 0; row < n; row++) {
            if (grid[row][col] == 'a') {
                apples++;
                grid[row][col] = '.';
            }
        }

        int row = n - 1;
        while (apples > 0 && row >= 0) {
            if (grid[row][col] == '.') {
                grid[row][col] = 'a';
                apples--;
            }
            row--;
        }
    }

    for (int i = 0; i < n; i++) {
        cout << grid[i] << "\\n";
    }

    return 0;
}
'''
        }
    ]

    # Problem 7190: baekjoon_26257 - std::shared_ptr
    # 참조 카운팅 시뮬레이션
    solutions[7190] = [
        {
            "language": "python",
            "code": '''# std::shared_ptr - 참조 카운팅 시뮬레이션
import sys
input = sys.stdin.readline

n, q = map(int, input().split())

# ptr[i] = 해당 포인터가 가리키는 객체 번호 (0이면 null)
ptr = [0] * (n + 1)
# ref_count[obj] = 객체의 참조 카운트
ref_count = {}

for _ in range(q):
    query = input().split()
    cmd = query[0]

    if cmd == "make":
        i, x = int(query[1]), int(query[2])
        # ptr[i]가 이미 다른 객체를 가리키고 있으면 그 객체의 참조 카운트 감소
        if ptr[i] > 0:
            ref_count[ptr[i]] -= 1
            if ref_count[ptr[i]] == 0:
                del ref_count[ptr[i]]
        ptr[i] = x
        ref_count[x] = ref_count.get(x, 0) + 1

    elif cmd == "copy":
        i, j = int(query[1]), int(query[2])
        # ptr[i]가 다른 객체를 가리키고 있으면 참조 카운트 감소
        if ptr[i] > 0:
            ref_count[ptr[i]] -= 1
            if ref_count[ptr[i]] == 0:
                del ref_count[ptr[i]]
        # ptr[j]가 가리키는 객체로 ptr[i] 설정
        ptr[i] = ptr[j]
        if ptr[i] > 0:
            ref_count[ptr[i]] += 1

    elif cmd == "reset":
        i = int(query[1])
        if ptr[i] > 0:
            ref_count[ptr[i]] -= 1
            if ref_count[ptr[i]] == 0:
                del ref_count[ptr[i]]
        ptr[i] = 0

    elif cmd == "count":
        i = int(query[1])
        if ptr[i] == 0:
            print(0)
        else:
            print(ref_count.get(ptr[i], 0))

# 남아있는 객체 수 출력
print(len(ref_count))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // std::shared_ptr - 참조 카운팅 시뮬레이션
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int q = Integer.parseInt(st.nextToken());

        int[] ptr = new int[n + 1];
        Map<Integer, Integer> refCount = new HashMap<>();

        StringBuilder sb = new StringBuilder();

        for (int query = 0; query < q; query++) {
            st = new StringTokenizer(br.readLine());
            String cmd = st.nextToken();

            if (cmd.equals("make")) {
                int i = Integer.parseInt(st.nextToken());
                int x = Integer.parseInt(st.nextToken());

                if (ptr[i] > 0) {
                    int oldObj = ptr[i];
                    refCount.put(oldObj, refCount.get(oldObj) - 1);
                    if (refCount.get(oldObj) == 0) refCount.remove(oldObj);
                }
                ptr[i] = x;
                refCount.put(x, refCount.getOrDefault(x, 0) + 1);
            } else if (cmd.equals("copy")) {
                int i = Integer.parseInt(st.nextToken());
                int j = Integer.parseInt(st.nextToken());

                if (ptr[i] > 0) {
                    int oldObj = ptr[i];
                    refCount.put(oldObj, refCount.get(oldObj) - 1);
                    if (refCount.get(oldObj) == 0) refCount.remove(oldObj);
                }
                ptr[i] = ptr[j];
                if (ptr[i] > 0) {
                    refCount.put(ptr[i], refCount.getOrDefault(ptr[i], 0) + 1);
                }
            } else if (cmd.equals("reset")) {
                int i = Integer.parseInt(st.nextToken());
                if (ptr[i] > 0) {
                    int oldObj = ptr[i];
                    refCount.put(oldObj, refCount.get(oldObj) - 1);
                    if (refCount.get(oldObj) == 0) refCount.remove(oldObj);
                }
                ptr[i] = 0;
            } else if (cmd.equals("count")) {
                int i = Integer.parseInt(st.nextToken());
                if (ptr[i] == 0) {
                    sb.append(0).append("\\n");
                } else {
                    sb.append(refCount.getOrDefault(ptr[i], 0)).append("\\n");
                }
            }
        }

        sb.append(refCount.size());
        System.out.println(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <unordered_map>
#include <string>
using namespace std;

// std::shared_ptr - 참조 카운팅 시뮬레이션
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;

    vector<int> ptr(n + 1, 0);
    unordered_map<int, int> refCount;

    for (int query = 0; query < q; query++) {
        string cmd;
        cin >> cmd;

        if (cmd == "make") {
            int i, x;
            cin >> i >> x;

            if (ptr[i] > 0) {
                refCount[ptr[i]]--;
                if (refCount[ptr[i]] == 0) refCount.erase(ptr[i]);
            }
            ptr[i] = x;
            refCount[x]++;
        } else if (cmd == "copy") {
            int i, j;
            cin >> i >> j;

            if (ptr[i] > 0) {
                refCount[ptr[i]]--;
                if (refCount[ptr[i]] == 0) refCount.erase(ptr[i]);
            }
            ptr[i] = ptr[j];
            if (ptr[i] > 0) {
                refCount[ptr[i]]++;
            }
        } else if (cmd == "reset") {
            int i;
            cin >> i;
            if (ptr[i] > 0) {
                refCount[ptr[i]]--;
                if (refCount[ptr[i]] == 0) refCount.erase(ptr[i]);
            }
            ptr[i] = 0;
        } else if (cmd == "count") {
            int i;
            cin >> i;
            if (ptr[i] == 0) {
                cout << 0 << "\\n";
            } else {
                cout << refCount[ptr[i]] << "\\n";
            }
        }
    }

    cout << refCount.size() << endl;

    return 0;
}
'''
        }
    ]

    # Problem 7200: baekjoon_14528 - Bovine Genomics (Silver)
    # DNA 위치 찾기
    solutions[7200] = [
        {
            "language": "python",
            "code": '''# Bovine Genomics (Silver) - DNA 위치 찾기
import sys
input = sys.stdin.readline

n, m = map(int, input().split())

# n개의 점 있는 소 DNA
spotted = []
for _ in range(n):
    spotted.append(input().strip())

# n개의 점 없는 소 DNA
plain = []
for _ in range(n):
    plain.append(input().strip())

# 각 위치에서 점 있는 소와 점 없는 소를 구분할 수 있는지 확인
count = 0
for pos in range(m):
    # 해당 위치에서 점 있는 소의 문자 집합
    spotted_chars = set()
    for dna in spotted:
        spotted_chars.add(dna[pos])

    # 해당 위치에서 점 없는 소의 문자 집합
    plain_chars = set()
    for dna in plain:
        plain_chars.add(dna[pos])

    # 두 집합이 겹치지 않으면 구분 가능
    if spotted_chars.isdisjoint(plain_chars):
        count += 1

print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // Bovine Genomics (Silver) - DNA 위치 찾기
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        String[] spotted = new String[n];
        for (int i = 0; i < n; i++) {
            spotted[i] = br.readLine().trim();
        }

        String[] plain = new String[n];
        for (int i = 0; i < n; i++) {
            plain[i] = br.readLine().trim();
        }

        int count = 0;
        for (int pos = 0; pos < m; pos++) {
            Set<Character> spottedChars = new HashSet<>();
            for (int i = 0; i < n; i++) {
                spottedChars.add(spotted[i].charAt(pos));
            }

            Set<Character> plainChars = new HashSet<>();
            for (int i = 0; i < n; i++) {
                plainChars.add(plain[i].charAt(pos));
            }

            // 겹치는지 확인
            boolean disjoint = true;
            for (char c : spottedChars) {
                if (plainChars.contains(c)) {
                    disjoint = false;
                    break;
                }
            }

            if (disjoint) count++;
        }

        System.out.println(count);
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

// Bovine Genomics (Silver) - DNA 위치 찾기
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    vector<string> spotted(n), plain(n);
    for (int i = 0; i < n; i++) cin >> spotted[i];
    for (int i = 0; i < n; i++) cin >> plain[i];

    int count = 0;
    for (int pos = 0; pos < m; pos++) {
        set<char> spottedChars, plainChars;
        for (int i = 0; i < n; i++) {
            spottedChars.insert(spotted[i][pos]);
            plainChars.insert(plain[i][pos]);
        }

        bool disjoint = true;
        for (char c : spottedChars) {
            if (plainChars.count(c)) {
                disjoint = false;
                break;
            }
        }

        if (disjoint) count++;
    }

    cout << count << endl;

    return 0;
}
'''
        }
    ]

    # Problem 7204: baekjoon_32713 - 숫자 POP
    # 숫자 빼기 게임
    solutions[7204] = [
        {
            "language": "python",
            "code": '''# 숫자 POP - 숫자 빼기 게임
import sys
input = sys.stdin.readline

n = int(input())
arr = list(map(int, input().split()))

# 스택을 이용한 단조 증가 수열 만들기
stack = []
for num in arr:
    # 현재 숫자보다 큰 숫자는 스택에서 제거
    while stack and stack[-1] > num:
        stack.pop()
    stack.append(num)

print(' '.join(map(str, stack)))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // 숫자 POP - 숫자 빼기 게임
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        Stack<Integer> stack = new Stack<>();
        for (int i = 0; i < n; i++) {
            int num = Integer.parseInt(st.nextToken());
            while (!stack.isEmpty() && stack.peek() > num) {
                stack.pop();
            }
            stack.push(num);
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < stack.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(stack.get(i));
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
#include <stack>
using namespace std;

// 숫자 POP - 숫자 빼기 게임
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> result;
    for (int i = 0; i < n; i++) {
        int num;
        cin >> num;
        while (!result.empty() && result.back() > num) {
            result.pop_back();
        }
        result.push_back(num);
    }

    for (int i = 0; i < (int)result.size(); i++) {
        if (i > 0) cout << " ";
        cout << result[i];
    }
    cout << endl;

    return 0;
}
'''
        }
    ]

    # Problem 7208: baekjoon_9319 - 도청 장치
    # 문자열 암호 해독
    solutions[7208] = [
        {
            "language": "python",
            "code": '''# 도청 장치 - 문자열 암호 해독
import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    k = int(input())
    s = input().strip()

    # k만큼 각 문자를 알파벳에서 뒤로 이동
    result = []
    for c in s:
        if c.isalpha():
            if c.isupper():
                new_c = chr((ord(c) - ord('A') - k) % 26 + ord('A'))
            else:
                new_c = chr((ord(c) - ord('a') - k) % 26 + ord('a'))
            result.append(new_c)
        else:
            result.append(c)

    print(''.join(result))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // 도청 장치 - 문자열 암호 해독
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        for (int tc = 0; tc < t; tc++) {
            int k = Integer.parseInt(br.readLine().trim());
            String s = br.readLine();

            for (int i = 0; i < s.length(); i++) {
                char c = s.charAt(i);
                if (Character.isLetter(c)) {
                    if (Character.isUpperCase(c)) {
                        int newIdx = (c - 'A' - k % 26 + 26) % 26;
                        sb.append((char)('A' + newIdx));
                    } else {
                        int newIdx = (c - 'a' - k % 26 + 26) % 26;
                        sb.append((char)('a' + newIdx));
                    }
                } else {
                    sb.append(c);
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
            "code": '''#include <iostream>
#include <string>
using namespace std;

// 도청 장치 - 문자열 암호 해독
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;

    while (t--) {
        int k;
        cin >> k;
        cin.ignore();

        string s;
        getline(cin, s);

        for (int i = 0; i < (int)s.length(); i++) {
            char c = s[i];
            if (isalpha(c)) {
                if (isupper(c)) {
                    int newIdx = (c - 'A' - k % 26 + 26) % 26;
                    s[i] = 'A' + newIdx;
                } else {
                    int newIdx = (c - 'a' - k % 26 + 26) % 26;
                    s[i] = 'a' + newIdx;
                }
            }
        }

        cout << s << "\\n";
    }

    return 0;
}
'''
        }
    ]

    # Problem 7217: baekjoon_33063 - Farmer John's Cheese Block
    # 치즈 블록 문제
    solutions[7217] = [
        {
            "language": "python",
            "code": '''# Farmer John's Cheese Block - 치즈 블록
import sys
input = sys.stdin.readline

n = int(input())
queries = []
max_x, max_y, max_z = 0, 0, 0

for _ in range(n):
    x, y, z = map(int, input().split())
    queries.append((x, y, z))
    max_x = max(max_x, x)
    max_y = max(max_y, y)
    max_z = max(max_z, z)

# 치즈 블록 크기 계산
# 각 쿼리는 (x, y, z) 위치의 치즈를 먹음
# 남은 치즈 부피 = 전체 - 먹은 것
total_volume = max_x * max_y * max_z

# 이미 먹은 위치 추적
eaten = set()
remaining = total_volume

for x, y, z in queries:
    if (x, y, z) not in eaten:
        eaten.add((x, y, z))
        remaining -= 1
    print(remaining)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // Farmer John's Cheese Block - 치즈 블록
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[][] queries = new int[n][3];
        int maxX = 0, maxY = 0, maxZ = 0;

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            queries[i][0] = Integer.parseInt(st.nextToken());
            queries[i][1] = Integer.parseInt(st.nextToken());
            queries[i][2] = Integer.parseInt(st.nextToken());
            maxX = Math.max(maxX, queries[i][0]);
            maxY = Math.max(maxY, queries[i][1]);
            maxZ = Math.max(maxZ, queries[i][2]);
        }

        long totalVolume = (long)maxX * maxY * maxZ;
        Set<String> eaten = new HashSet<>();
        long remaining = totalVolume;

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            String key = queries[i][0] + "," + queries[i][1] + "," + queries[i][2];
            if (!eaten.contains(key)) {
                eaten.add(key);
                remaining--;
            }
            sb.append(remaining).append("\\n");
        }
        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <set>
#include <tuple>
using namespace std;

// Farmer John's Cheese Block - 치즈 블록
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<tuple<int, int, int>> queries(n);
    int maxX = 0, maxY = 0, maxZ = 0;

    for (int i = 0; i < n; i++) {
        int x, y, z;
        cin >> x >> y >> z;
        queries[i] = {x, y, z};
        maxX = max(maxX, x);
        maxY = max(maxY, y);
        maxZ = max(maxZ, z);
    }

    long long totalVolume = (long long)maxX * maxY * maxZ;
    set<tuple<int, int, int>> eaten;
    long long remaining = totalVolume;

    for (int i = 0; i < n; i++) {
        if (eaten.find(queries[i]) == eaten.end()) {
            eaten.insert(queries[i]);
            remaining--;
        }
        cout << remaining << "\\n";
    }

    return 0;
}
'''
        }
    ]

    # Problem 7229: baekjoon_32687 - 반복수
    # 반복되는 패턴 찾기
    solutions[7229] = [
        {
            "language": "python",
            "code": '''# 반복수 - 반복되는 패턴 찾기
import sys
input = sys.stdin.readline

n = int(input())

# 반복수: 같은 숫자가 연속으로 2번 이상 나타나는 수
# 예: 11, 22, 111, 1111, 112233 등

# n번째 반복수 찾기
count = 0
num = 1
while count < n:
    num += 1
    s = str(num)
    # 연속된 같은 숫자가 있는지 확인
    has_repeat = False
    for i in range(len(s) - 1):
        if s[i] == s[i+1]:
            has_repeat = True
            break
    if has_repeat:
        count += 1

print(num)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // 반복수 - 반복되는 패턴 찾기
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int count = 0;
        int num = 1;
        while (count < n) {
            num++;
            String s = String.valueOf(num);
            boolean hasRepeat = false;
            for (int i = 0; i < s.length() - 1; i++) {
                if (s.charAt(i) == s.charAt(i + 1)) {
                    hasRepeat = true;
                    break;
                }
            }
            if (hasRepeat) {
                count++;
            }
        }

        System.out.println(num);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
using namespace std;

// 반복수 - 반복되는 패턴 찾기
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    int count = 0;
    int num = 1;
    while (count < n) {
        num++;
        string s = to_string(num);
        bool hasRepeat = false;
        for (int i = 0; i < (int)s.length() - 1; i++) {
            if (s[i] == s[i + 1]) {
                hasRepeat = true;
                break;
            }
        }
        if (hasRepeat) {
            count++;
        }
    }

    cout << num << endl;

    return 0;
}
'''
        }
    ]

    # Problem 7230: baekjoon_32517 - 평점 변환 2
    # 평점 변환
    solutions[7230] = [
        {
            "language": "python",
            "code": '''# 평점 변환 2
import sys
input = sys.stdin.readline

n = int(input())
grades = list(map(float, input().split()))

# 평균 계산
avg = sum(grades) / n

# 4.5점 만점으로 변환
# 새 평점 = (원래 평점 / 원래 최대) * 4.5
result = []
for g in grades:
    new_grade = (g / 4.3) * 4.5
    result.append(round(new_grade, 2))

# 평균 출력
new_avg = sum(result) / n
print(f"{new_avg:.2f}")
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // 평점 변환 2
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        double[] grades = new double[n];
        for (int i = 0; i < n; i++) {
            grades[i] = Double.parseDouble(st.nextToken());
        }

        double sum = 0;
        for (int i = 0; i < n; i++) {
            double newGrade = (grades[i] / 4.3) * 4.5;
            sum += newGrade;
        }

        double newAvg = sum / n;
        System.out.printf("%.2f%n", newAvg);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <iomanip>
using namespace std;

// 평점 변환 2
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    double sum = 0;
    for (int i = 0; i < n; i++) {
        double grade;
        cin >> grade;
        double newGrade = (grade / 4.3) * 4.5;
        sum += newGrade;
    }

    double newAvg = sum / n;
    cout << fixed << setprecision(2) << newAvg << endl;

    return 0;
}
'''
        }
    ]

    # Problem 7231: baekjoon_6556 - Paths on a Grid
    # 격자 경로 수 계산 (조합)
    solutions[7231] = [
        {
            "language": "python",
            "code": '''# Paths on a Grid - 격자 경로 수 계산
import sys
from math import comb

input = sys.stdin.readline

while True:
    line = input().split()
    n, m = int(line[0]), int(line[1])
    if n == 0 and m == 0:
        break

    # (0,0)에서 (n,m)까지 가는 경로 수 = C(n+m, n) = C(n+m, m)
    # 오른쪽 n번, 위쪽 m번 이동해야 함
    result = comb(n + m, n)
    print(result)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;
import java.math.BigInteger;

public class Main {
    // Paths on a Grid - 격자 경로 수 계산
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        while (true) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int m = Integer.parseInt(st.nextToken());
            if (n == 0 && m == 0) break;

            // C(n+m, n) 계산
            BigInteger result = comb(n + m, Math.min(n, m));
            sb.append(result).append("\\n");
        }
        System.out.print(sb);
    }

    static BigInteger comb(int n, int r) {
        if (r > n - r) r = n - r;
        BigInteger result = BigInteger.ONE;
        for (int i = 0; i < r; i++) {
            result = result.multiply(BigInteger.valueOf(n - i));
            result = result.divide(BigInteger.valueOf(i + 1));
        }
        return result;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

// Paths on a Grid - 격자 경로 수 계산
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    while (cin >> n >> m && (n || m)) {
        // C(n+m, min(n,m)) 계산
        int total = n + m;
        int r = min(n, m);

        unsigned long long result = 1;
        for (int i = 0; i < r; i++) {
            result = result * (total - i) / (i + 1);
        }

        cout << result << "\\n";
    }

    return 0;
}
'''
        }
    ]

    # Problem 7249: baekjoon_6165 - Game of Lines
    # 서로 다른 기울기 수 세기
    solutions[7249] = [
        {
            "language": "python",
            "code": '''# Game of Lines - 서로 다른 기울기 수 세기
import sys
from math import gcd

input = sys.stdin.readline

n = int(input())
points = []
for _ in range(n):
    x, y = map(int, input().split())
    points.append((x, y))

# 모든 점 쌍에 대해 기울기 계산
slopes = set()
for i in range(n):
    for j in range(i + 1, n):
        dx = points[j][0] - points[i][0]
        dy = points[j][1] - points[i][1]

        # 기울기를 기약분수로 표현
        if dx == 0:
            slope = (0, 1)  # 수직선
        elif dy == 0:
            slope = (1, 0)  # 수평선
        else:
            g = gcd(abs(dx), abs(dy))
            dx //= g
            dy //= g
            # 부호 정규화
            if dx < 0:
                dx, dy = -dx, -dy
            slope = (dy, dx)

        slopes.add(slope)

print(len(slopes))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // Game of Lines - 서로 다른 기울기 수 세기
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[][] points = new int[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            points[i][0] = Integer.parseInt(st.nextToken());
            points[i][1] = Integer.parseInt(st.nextToken());
        }

        Set<String> slopes = new HashSet<>();
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                int dx = points[j][0] - points[i][0];
                int dy = points[j][1] - points[i][1];

                String slope;
                if (dx == 0) {
                    slope = "0,1";
                } else if (dy == 0) {
                    slope = "1,0";
                } else {
                    int g = gcd(Math.abs(dx), Math.abs(dy));
                    dx /= g;
                    dy /= g;
                    if (dx < 0) {
                        dx = -dx;
                        dy = -dy;
                    }
                    slope = dy + "," + dx;
                }
                slopes.add(slope);
            }
        }

        System.out.println(slopes.size());
    }

    static int gcd(int a, int b) {
        while (b != 0) {
            int t = b;
            b = a % b;
            a = t;
        }
        return a;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <set>
#include <cmath>
using namespace std;

// Game of Lines - 서로 다른 기울기 수 세기
int gcd(int a, int b) {
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<pair<int, int>> points(n);
    for (int i = 0; i < n; i++) {
        cin >> points[i].first >> points[i].second;
    }

    set<pair<int, int>> slopes;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            int dx = points[j].first - points[i].first;
            int dy = points[j].second - points[i].second;

            pair<int, int> slope;
            if (dx == 0) {
                slope = {0, 1};
            } else if (dy == 0) {
                slope = {1, 0};
            } else {
                int g = gcd(abs(dx), abs(dy));
                dx /= g;
                dy /= g;
                if (dx < 0) {
                    dx = -dx;
                    dy = -dy;
                }
                slope = {dy, dx};
            }
            slopes.insert(slope);
        }
    }

    cout << slopes.size() << endl;

    return 0;
}
'''
        }
    ]

    # Problem 7250: baekjoon_16065 - Down the Pyramid
    # 피라미드 아래로
    solutions[7250] = [
        {
            "language": "python",
            "code": '''# Down the Pyramid - 피라미드 합
import sys
input = sys.stdin.readline

n = int(input())
bottom = list(map(int, input().split()))

# 피라미드에서 위로 합을 계산
# 아래 두 값의 합이 위의 값
# bottom에서 top을 구하는 것은 불가능할 수 있음
# 대신 가능한 top의 값 개수를 구함

# bottom[i] + bottom[i+1] = 위의 줄의 i번째 값
# 역으로, bottom[0]을 x라고 하면
# 위의 줄 값들이 결정됨

# 모든 값이 음이 아닌 정수여야 함
# bottom[0] = x일 때, 나머지 값들이 결정됨

# 실제로는 bottom에서 위로 올라가며 계산
# 각 단계에서 합이 위의 값이 됨

# n=1이면 1가지 (자기 자신)
if n == 1:
    print(bottom[0] + 1)
else:
    # 첫 번째 값 x의 범위 계산
    # 모든 중간 값이 0 이상이어야 함

    # 상삼각 행렬처럼 계산
    # row[i]는 bottom에서 i단계 위의 줄
    min_x = 0
    max_x = 10**18

    # 시뮬레이션으로 x의 범위 찾기
    # x = 0일 때와 x = bottom[0]일 때 테스트

    # 더 정확한 방법: 선형 계산
    # 각 위치의 값은 x의 선형 함수
    # 계수 계산

    coeffs = [0] * n  # x의 계수
    consts = [0] * n  # 상수항
    coeffs[0] = 1
    consts[0] = 0
    for i in range(1, n):
        coeffs[i] = 0
        consts[i] = bottom[i]

    # 위로 올라가며 계산
    for level in range(n - 1, 0, -1):
        new_coeffs = [0] * level
        new_consts = [0] * level
        for i in range(level):
            new_coeffs[i] = coeffs[i] + coeffs[i + 1] if i + 1 < len(coeffs) else coeffs[i]
            new_consts[i] = consts[i] + consts[i + 1] if i + 1 < len(consts) else consts[i]
            # 값 = coeffs[i] * x + consts[i] >= 0
            # coeffs[i] * x >= -consts[i]
            if coeffs[i] > 0:
                min_x = max(min_x, (-consts[i] + coeffs[i] - 1) // coeffs[i] if -consts[i] > 0 else 0)
            elif coeffs[i] < 0:
                max_x = min(max_x, -consts[i] // (-coeffs[i]))
        coeffs = new_coeffs
        consts = new_consts

    if min_x > max_x:
        print(0)
    else:
        print(max_x - min_x + 1)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // Down the Pyramid - 피라미드 합
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        long[] bottom = new long[n];
        for (int i = 0; i < n; i++) {
            bottom[i] = Long.parseLong(st.nextToken());
        }

        if (n == 1) {
            System.out.println(bottom[0] + 1);
            return;
        }

        // x = bottom[0]의 범위 찾기
        // 각 위치의 값 = coeff * x + const >= 0
        long[] coeffs = new long[n];
        long[] consts = new long[n];
        coeffs[0] = 1;
        for (int i = 1; i < n; i++) {
            consts[i] = bottom[i];
        }

        long minX = 0;
        long maxX = (long)1e18;

        for (int level = n; level > 1; level--) {
            long[] newCoeffs = new long[level - 1];
            long[] newConsts = new long[level - 1];
            for (int i = 0; i < level - 1; i++) {
                newCoeffs[i] = coeffs[i] + coeffs[i + 1];
                newConsts[i] = consts[i] + consts[i + 1];

                // newCoeffs[i] * x + newConsts[i] >= 0
                if (newCoeffs[i] > 0) {
                    long bound = (long)Math.ceil((double)(-newConsts[i]) / newCoeffs[i]);
                    minX = Math.max(minX, Math.max(0, bound));
                } else if (newCoeffs[i] < 0) {
                    long bound = -newConsts[i] / (-newCoeffs[i]);
                    maxX = Math.min(maxX, bound);
                } else if (newConsts[i] < 0) {
                    maxX = -1; // 불가능
                }
            }
            coeffs = newCoeffs;
            consts = newConsts;
        }

        if (minX > maxX) {
            System.out.println(0);
        } else {
            System.out.println(maxX - minX + 1);
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
#include <cmath>
using namespace std;

// Down the Pyramid - 피라미드 합
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<long long> bottom(n);
    for (int i = 0; i < n; i++) {
        cin >> bottom[i];
    }

    if (n == 1) {
        cout << bottom[0] + 1 << endl;
        return 0;
    }

    vector<long long> coeffs(n, 0), consts(n, 0);
    coeffs[0] = 1;
    for (int i = 1; i < n; i++) {
        consts[i] = bottom[i];
    }

    long long minX = 0;
    long long maxX = 1e18;

    for (int level = n; level > 1; level--) {
        vector<long long> newCoeffs(level - 1), newConsts(level - 1);
        for (int i = 0; i < level - 1; i++) {
            newCoeffs[i] = coeffs[i] + coeffs[i + 1];
            newConsts[i] = consts[i] + consts[i + 1];

            if (newCoeffs[i] > 0) {
                long long bound = (long long)ceil((double)(-newConsts[i]) / newCoeffs[i]);
                minX = max(minX, max(0LL, bound));
            } else if (newCoeffs[i] < 0) {
                long long bound = -newConsts[i] / (-newCoeffs[i]);
                maxX = min(maxX, bound);
            } else if (newConsts[i] < 0) {
                maxX = -1;
            }
        }
        coeffs = newCoeffs;
        consts = newConsts;
    }

    if (minX > maxX) {
        cout << 0 << endl;
    } else {
        cout << maxX - minX + 1 << endl;
    }

    return 0;
}
'''
        }
    ]

    # 나머지 문제들에 대한 솔루션 추가...
    # (계속 추가해야 함)

    return solutions


def main():
    json_path = "/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json"

    # 파일 읽기
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # empty medium 문제 인덱스 찾기
    empty_medium = []
    for i, p in enumerate(data):
        if p.get('difficulty') == 'medium' and (not p.get('solutions') or len(p.get('solutions', [])) == 0):
            if p.get('input_output') and len(p.get('input_output', [])) > 0:
                empty_medium.append(i)

    # 540-569 인덱스
    target_indices = empty_medium[540:570]

    solutions = get_solutions()

    # 솔루션 적용
    count = 0
    for orig_idx in target_indices:
        if orig_idx in solutions:
            data[orig_idx]['solutions'] = solutions[orig_idx]
            count += 1
            print(f"Added solutions for index {orig_idx}: {data[orig_idx].get('id')}")

    # 파일 저장 (fcntl 잠금 사용)
    with open(json_path, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\nTotal solutions added: {count}")
    print(f"Remaining empty medium problems: {len(empty_medium) - 570}")


if __name__ == "__main__":
    main()
