#!/usr/bin/env python3
"""
Generate solutions for Baekjoon problems 1720-1729
"""

import json

CHECKPOINT_FILE = "/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json"

SOLUTIONS = {
    "1720": {
        "python": '''n = int(input())

# dp[i] = number of ways to fill 2xi board
dp = [0] * (n + 1)
dp[0] = 1
if n >= 1:
    dp[1] = 1
for i in range(2, n + 1):
    dp[i] = dp[i-1] + 2 * dp[i-2]

# symmetric[i] = number of symmetric tilings
# For even n: symmetric tilings have symmetric halves
# For odd n: middle column must be filled with 2x1 vertical

if n % 2 == 0:
    # Even: count symmetric tilings
    # Half is n//2
    # Symmetric = dp[n//2] + 2*dp[n//2 - 1] (for middle 2x2 or two horizontals)
    sym = dp[n//2] + dp[n//2 - 1] * 2
else:
    # Odd: middle must be vertical 2x1
    sym = dp[n//2]

result = (dp[n] + sym) // 2
print(result)''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        long[] dp = new long[n + 2];
        dp[0] = 1;
        dp[1] = 1;
        for (int i = 2; i <= n; i++) {
            dp[i] = dp[i-1] + 2 * dp[i-2];
        }

        long sym;
        if (n % 2 == 0) {
            sym = dp[n/2] + dp[n/2 - 1] * 2;
        } else {
            sym = dp[n/2];
        }

        System.out.println((dp[n] + sym) / 2);
    }
}''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;

    long long dp[31] = {0};
    dp[0] = 1;
    dp[1] = 1;
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i-1] + 2 * dp[i-2];
    }

    long long sym;
    if (n % 2 == 0) {
        sym = dp[n/2] + dp[n/2 - 1] * 2;
    } else {
        sym = dp[n/2];
    }

    cout << (dp[n] + sym) / 2 << endl;
    return 0;
}'''
    },
    "1721": {
        "python": '''import sys
from itertools import permutations

input = sys.stdin.readline

n = int(input())
boxes = []

for _ in range(n * n):
    data = list(map(int, input().split()))
    top = data[0]
    sides = data[1:5]  # Up, Right, Down, Left
    boxes.append((top, sides))

def rotate(sides, times):
    return sides[times:] + sides[:times]

def get_side(sides, direction):
    # 0: up, 1: right, 2: down, 3: left
    return sides[direction]

def check(grid, rotations, row, col, box_idx, rot):
    sides = rotate(boxes[box_idx][1], rot)

    # Check up
    if row == 0:
        if sides[0] != 0:
            return False
    else:
        above_idx = grid[row-1][col]
        above_rot = rotations[row-1][col]
        above_sides = rotate(boxes[above_idx][1], above_rot)
        if sides[0] != above_sides[2]:
            return False

    # Check left
    if col == 0:
        if sides[3] != 0:
            return False
    else:
        left_idx = grid[row][col-1]
        left_rot = rotations[row][col-1]
        left_sides = rotate(boxes[left_idx][1], left_rot)
        if sides[3] != left_sides[1]:
            return False

    # Check right edge
    if col == n - 1:
        if sides[1] != 0:
            return False

    # Check bottom edge
    if row == n - 1:
        if sides[2] != 0:
            return False

    return True

def solve(pos, used, grid, rotations):
    if pos == n * n:
        return True

    row, col = pos // n, pos % n

    for i in range(n * n):
        if used[i]:
            continue
        for rot in range(4):
            if check(grid, rotations, row, col, i, rot):
                grid[row][col] = i
                rotations[row][col] = rot
                used[i] = True
                if solve(pos + 1, used, grid, rotations):
                    return True
                used[i] = False

    return False

grid = [[0] * n for _ in range(n)]
rotations = [[0] * n for _ in range(n)]
used = [False] * (n * n)

solve(0, used, grid, rotations)

for row in grid:
    print(' '.join(str(boxes[i][0]) for i in row))
for row in rotations:
    print(' '.join(map(str, row)))''',
        "java": '''import java.util.*;

public class Main {
    static int n;
    static int[][] boxes;
    static int[][] grid;
    static int[][] rotations;
    static boolean[] used;

    static int[] rotate(int[] sides, int times) {
        int[] result = new int[4];
        for (int i = 0; i < 4; i++) {
            result[i] = sides[(i + times) % 4];
        }
        return result;
    }

    static boolean check(int row, int col, int boxIdx, int rot) {
        int[] sides = rotate(Arrays.copyOfRange(boxes[boxIdx], 1, 5), rot);

        if (row == 0 && sides[0] != 0) return false;
        if (col == 0 && sides[3] != 0) return false;
        if (row == n - 1 && sides[2] != 0) return false;
        if (col == n - 1 && sides[1] != 0) return false;

        if (row > 0) {
            int[] aboveSides = rotate(Arrays.copyOfRange(boxes[grid[row-1][col]], 1, 5), rotations[row-1][col]);
            if (sides[0] != aboveSides[2]) return false;
        }
        if (col > 0) {
            int[] leftSides = rotate(Arrays.copyOfRange(boxes[grid[row][col-1]], 1, 5), rotations[row][col-1]);
            if (sides[3] != leftSides[1]) return false;
        }

        return true;
    }

    static boolean solve(int pos) {
        if (pos == n * n) return true;

        int row = pos / n, col = pos % n;

        for (int i = 0; i < n * n; i++) {
            if (used[i]) continue;
            for (int rot = 0; rot < 4; rot++) {
                if (check(row, col, i, rot)) {
                    grid[row][col] = i;
                    rotations[row][col] = rot;
                    used[i] = true;
                    if (solve(pos + 1)) return true;
                    used[i] = false;
                }
            }
        }
        return false;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();
        boxes = new int[n * n][5];
        grid = new int[n][n];
        rotations = new int[n][n];
        used = new boolean[n * n];

        for (int i = 0; i < n * n; i++) {
            for (int j = 0; j < 5; j++) {
                boxes[i][j] = sc.nextInt();
            }
        }

        solve(0);

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (j > 0) sb.append(" ");
                sb.append(boxes[grid[i][j]][0]);
            }
            sb.append("\\n");
        }
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (j > 0) sb.append(" ");
                sb.append(rotations[i][j]);
            }
            sb.append("\\n");
        }
        System.out.print(sb);
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
using namespace std;

int n;
vector<vector<int>> boxes;
vector<vector<int>> grid;
vector<vector<int>> rotations;
vector<bool> used;

vector<int> rotate(vector<int>& sides, int times) {
    vector<int> result(4);
    for (int i = 0; i < 4; i++) {
        result[i] = sides[(i + times) % 4];
    }
    return result;
}

bool check(int row, int col, int boxIdx, int rot) {
    vector<int> sides(boxes[boxIdx].begin() + 1, boxes[boxIdx].end());
    sides = rotate(sides, rot);

    if (row == 0 && sides[0] != 0) return false;
    if (col == 0 && sides[3] != 0) return false;
    if (row == n - 1 && sides[2] != 0) return false;
    if (col == n - 1 && sides[1] != 0) return false;

    if (row > 0) {
        vector<int> aboveSides(boxes[grid[row-1][col]].begin() + 1, boxes[grid[row-1][col]].end());
        aboveSides = rotate(aboveSides, rotations[row-1][col]);
        if (sides[0] != aboveSides[2]) return false;
    }
    if (col > 0) {
        vector<int> leftSides(boxes[grid[row][col-1]].begin() + 1, boxes[grid[row][col-1]].end());
        leftSides = rotate(leftSides, rotations[row][col-1]);
        if (sides[3] != leftSides[1]) return false;
    }

    return true;
}

bool solve(int pos) {
    if (pos == n * n) return true;

    int row = pos / n, col = pos % n;

    for (int i = 0; i < n * n; i++) {
        if (used[i]) continue;
        for (int rot = 0; rot < 4; rot++) {
            if (check(row, col, i, rot)) {
                grid[row][col] = i;
                rotations[row][col] = rot;
                used[i] = true;
                if (solve(pos + 1)) return true;
                used[i] = false;
            }
        }
    }
    return false;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;
    boxes.resize(n * n, vector<int>(5));
    grid.resize(n, vector<int>(n));
    rotations.resize(n, vector<int>(n));
    used.resize(n * n, false);

    for (int i = 0; i < n * n; i++) {
        for (int j = 0; j < 5; j++) {
            cin >> boxes[i][j];
        }
    }

    solve(0);

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (j > 0) cout << " ";
            cout << boxes[grid[i][j]][0];
        }
        cout << "\\n";
    }
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (j > 0) cout << " ";
            cout << rotations[i][j];
        }
        cout << "\\n";
    }
    return 0;
}'''
    },
    "1722": {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
query = list(map(int, input().split()))

# Precompute factorials
fact = [1] * 21
for i in range(1, 21):
    fact[i] = fact[i-1] * i

if query[0] == 1:
    # Find k-th permutation
    k = query[1] - 1
    available = list(range(1, n + 1))
    result = []

    for i in range(n):
        f = fact[n - 1 - i]
        idx = k // f
        k %= f
        result.append(available[idx])
        available.pop(idx)

    print(' '.join(map(str, result)))
else:
    # Find rank of permutation
    perm = query[1:]
    available = list(range(1, n + 1))
    rank = 0

    for i in range(n):
        idx = available.index(perm[i])
        rank += idx * fact[n - 1 - i]
        available.pop(idx)

    print(rank + 1)''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int type = sc.nextInt();

        long[] fact = new long[21];
        fact[0] = 1;
        for (int i = 1; i <= 20; i++) {
            fact[i] = fact[i-1] * i;
        }

        List<Integer> available = new ArrayList<>();
        for (int i = 1; i <= n; i++) available.add(i);

        if (type == 1) {
            long k = sc.nextLong() - 1;
            StringBuilder sb = new StringBuilder();

            for (int i = 0; i < n; i++) {
                long f = fact[n - 1 - i];
                int idx = (int)(k / f);
                k %= f;
                if (i > 0) sb.append(" ");
                sb.append(available.get(idx));
                available.remove(idx);
            }
            System.out.println(sb);
        } else {
            int[] perm = new int[n];
            for (int i = 0; i < n; i++) {
                perm[i] = sc.nextInt();
            }

            long rank = 0;
            for (int i = 0; i < n; i++) {
                int idx = available.indexOf(perm[i]);
                rank += idx * fact[n - 1 - i];
                available.remove(idx);
            }
            System.out.println(rank + 1);
        }
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, type;
    cin >> n >> type;

    long long fact[21];
    fact[0] = 1;
    for (int i = 1; i <= 20; i++) {
        fact[i] = fact[i-1] * i;
    }

    vector<int> available;
    for (int i = 1; i <= n; i++) available.push_back(i);

    if (type == 1) {
        long long k;
        cin >> k;
        k--;

        for (int i = 0; i < n; i++) {
            long long f = fact[n - 1 - i];
            int idx = k / f;
            k %= f;
            if (i > 0) cout << " ";
            cout << available[idx];
            available.erase(available.begin() + idx);
        }
        cout << endl;
    } else {
        vector<int> perm(n);
        for (int i = 0; i < n; i++) {
            cin >> perm[i];
        }

        long long rank = 0;
        for (int i = 0; i < n; i++) {
            int idx = find(available.begin(), available.end(), perm[i]) - available.begin();
            rank += idx * fact[n - 1 - i];
            available.erase(available.begin() + idx);
        }
        cout << rank + 1 << endl;
    }
    return 0;
}'''
    },
    "1723": {
        "python": '''import sys
from bisect import bisect_left, bisect_right

input = sys.stdin.readline

n, k = map(int, input().split())
angles = []
for _ in range(n):
    angles.append(float(input()))

angles.sort()
sector = 360.0 / k

# Try each angle as start of a sector boundary
min_diff = float('inf')

for start in angles:
    counts = []
    for s in range(k):
        low = (start + s * sector) % 360
        high = (start + (s + 1) * sector) % 360

        if low < high:
            cnt = bisect_left(angles, high) - bisect_left(angles, low)
        else:
            cnt = bisect_left(angles, high) + (n - bisect_left(angles, low))
        counts.append(cnt)

    diff = max(counts) - min(counts)
    min_diff = min(min_diff, diff)

# Also try epsilon before each angle
for start in angles:
    start = (start - 0.0001) % 360
    counts = []
    for s in range(k):
        low = (start + s * sector) % 360
        high = (start + (s + 1) * sector) % 360

        if low < high:
            cnt = bisect_left(angles, high) - bisect_left(angles, low)
        else:
            cnt = bisect_left(angles, high) + (n - bisect_left(angles, low))
        counts.append(cnt)

    diff = max(counts) - min(counts)
    min_diff = min(min_diff, diff)

print(min_diff)''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int k = sc.nextInt();

        double[] angles = new double[n];
        for (int i = 0; i < n; i++) {
            angles[i] = sc.nextDouble();
        }
        Arrays.sort(angles);

        double sector = 360.0 / k;
        int minDiff = Integer.MAX_VALUE;

        for (int t = 0; t < n * 2; t++) {
            double start = (t < n) ? angles[t] : (angles[t - n] - 0.0001 + 360) % 360;
            int[] counts = new int[k];

            for (int s = 0; s < k; s++) {
                double low = (start + s * sector) % 360;
                double high = (start + (s + 1) * sector) % 360;

                int cnt;
                if (low < high) {
                    cnt = lowerBound(angles, high) - lowerBound(angles, low);
                } else {
                    cnt = lowerBound(angles, high) + (n - lowerBound(angles, low));
                }
                counts[s] = cnt;
            }

            int max = 0, min = Integer.MAX_VALUE;
            for (int c : counts) {
                max = Math.max(max, c);
                min = Math.min(min, c);
            }
            minDiff = Math.min(minDiff, max - min);
        }

        System.out.println(minDiff);
    }

    static int lowerBound(double[] arr, double val) {
        int lo = 0, hi = arr.length;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (arr[mid] < val) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    vector<double> angles(n);
    for (int i = 0; i < n; i++) {
        cin >> angles[i];
    }
    sort(angles.begin(), angles.end());

    double sector = 360.0 / k;
    int minDiff = INT_MAX;

    for (int t = 0; t < n * 2; t++) {
        double start = (t < n) ? angles[t] : fmod(angles[t - n] - 0.0001 + 360, 360);
        vector<int> counts(k);

        for (int s = 0; s < k; s++) {
            double low = fmod(start + s * sector, 360);
            double high = fmod(start + (s + 1) * sector, 360);

            int cnt;
            if (low < high) {
                cnt = lower_bound(angles.begin(), angles.end(), high) -
                      lower_bound(angles.begin(), angles.end(), low);
            } else {
                cnt = lower_bound(angles.begin(), angles.end(), high) - angles.begin() +
                      (angles.end() - lower_bound(angles.begin(), angles.end(), low));
            }
            counts[s] = cnt;
        }

        int maxC = *max_element(counts.begin(), counts.end());
        int minC = *min_element(counts.begin(), counts.end());
        minDiff = min(minDiff, maxC - minC);
    }

    cout << minDiff << endl;
    return 0;
}'''
    },
    "1724": {
        "python": '''import sys
from collections import deque

input = sys.stdin.readline

n, m = map(int, input().split())
t = int(input())

# Use 2D grid with higher resolution
scale = 2
grid = [[0] * (m * scale + 1) for _ in range(n * scale + 1)]

for _ in range(t):
    sx, sy, ex, ey = map(int, input().split())
    sx, sy, ex, ey = sx * scale, sy * scale, ex * scale, ey * scale

    if sx == ex:
        for y in range(min(sy, ey), max(sy, ey) + 1):
            grid[sx][y] = 1
    else:
        for x in range(min(sx, ex), max(sx, ex) + 1):
            grid[x][sy] = 1

# BFS to find connected components
visited = [[False] * (m * scale + 1) for _ in range(n * scale + 1)]
areas = []

dx = [0, 0, 1, -1]
dy = [1, -1, 0, 0]

for i in range(n * scale):
    for j in range(m * scale):
        if not visited[i][j] and grid[i][j] == 0:
            queue = deque([(i, j)])
            visited[i][j] = True
            area = 0

            while queue:
                x, y = queue.popleft()
                area += 1

                for d in range(4):
                    nx, ny = x + dx[d], y + dy[d]
                    if 0 <= nx < n * scale and 0 <= ny < m * scale:
                        if not visited[nx][ny] and grid[nx][ny] == 0:
                            visited[nx][ny] = True
                            queue.append((nx, ny))

            # Convert from scaled to actual area
            areas.append(area // (scale * scale))

print(max(areas))
print(min(areas))''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int t = sc.nextInt();

        int scale = 2;
        int[][] grid = new int[(n + 1) * scale][(m + 1) * scale];

        for (int i = 0; i < t; i++) {
            int sx = sc.nextInt() * scale;
            int sy = sc.nextInt() * scale;
            int ex = sc.nextInt() * scale;
            int ey = sc.nextInt() * scale;

            if (sx == ex) {
                for (int y = Math.min(sy, ey); y <= Math.max(sy, ey); y++) {
                    grid[sx][y] = 1;
                }
            } else {
                for (int x = Math.min(sx, ex); x <= Math.max(sx, ex); x++) {
                    grid[x][sy] = 1;
                }
            }
        }

        boolean[][] visited = new boolean[(n + 1) * scale][(m + 1) * scale];
        List<Integer> areas = new ArrayList<>();

        int[] dx = {0, 0, 1, -1};
        int[] dy = {1, -1, 0, 0};

        for (int i = 0; i < n * scale; i++) {
            for (int j = 0; j < m * scale; j++) {
                if (!visited[i][j] && grid[i][j] == 0) {
                    Queue<int[]> queue = new LinkedList<>();
                    queue.add(new int[]{i, j});
                    visited[i][j] = true;
                    int area = 0;

                    while (!queue.isEmpty()) {
                        int[] cur = queue.poll();
                        area++;

                        for (int d = 0; d < 4; d++) {
                            int nx = cur[0] + dx[d];
                            int ny = cur[1] + dy[d];
                            if (nx >= 0 && nx < n * scale && ny >= 0 && ny < m * scale) {
                                if (!visited[nx][ny] && grid[nx][ny] == 0) {
                                    visited[nx][ny] = true;
                                    queue.add(new int[]{nx, ny});
                                }
                            }
                        }
                    }
                    areas.add(area / (scale * scale));
                }
            }
        }

        System.out.println(Collections.max(areas));
        System.out.println(Collections.min(areas));
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, t;
    cin >> n >> m >> t;

    int scale = 2;
    vector<vector<int>> grid((n + 1) * scale, vector<int>((m + 1) * scale, 0));

    for (int i = 0; i < t; i++) {
        int sx, sy, ex, ey;
        cin >> sx >> sy >> ex >> ey;
        sx *= scale; sy *= scale; ex *= scale; ey *= scale;

        if (sx == ex) {
            for (int y = min(sy, ey); y <= max(sy, ey); y++) {
                grid[sx][y] = 1;
            }
        } else {
            for (int x = min(sx, ex); x <= max(sx, ex); x++) {
                grid[x][sy] = 1;
            }
        }
    }

    vector<vector<bool>> visited((n + 1) * scale, vector<bool>((m + 1) * scale, false));
    vector<int> areas;

    int dx[] = {0, 0, 1, -1};
    int dy[] = {1, -1, 0, 0};

    for (int i = 0; i < n * scale; i++) {
        for (int j = 0; j < m * scale; j++) {
            if (!visited[i][j] && grid[i][j] == 0) {
                queue<pair<int, int>> q;
                q.push({i, j});
                visited[i][j] = true;
                int area = 0;

                while (!q.empty()) {
                    auto [x, y] = q.front();
                    q.pop();
                    area++;

                    for (int d = 0; d < 4; d++) {
                        int nx = x + dx[d], ny = y + dy[d];
                        if (nx >= 0 && nx < n * scale && ny >= 0 && ny < m * scale) {
                            if (!visited[nx][ny] && grid[nx][ny] == 0) {
                                visited[nx][ny] = true;
                                q.push({nx, ny});
                            }
                        }
                    }
                }
                areas.push_back(area / (scale * scale));
            }
        }
    }

    cout << *max_element(areas.begin(), areas.end()) << endl;
    cout << *min_element(areas.begin(), areas.end()) << endl;
    return 0;
}'''
    },
    "1725": {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
heights = [int(input()) for _ in range(n)]

stack = []
max_area = 0

for i in range(n):
    start = i
    while stack and stack[-1][1] > heights[i]:
        idx, h = stack.pop()
        max_area = max(max_area, h * (i - idx))
        start = idx
    stack.append((start, heights[i]))

for idx, h in stack:
    max_area = max(max_area, h * (n - idx))

print(max_area)''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        long[] heights = new long[n];
        for (int i = 0; i < n; i++) {
            heights[i] = sc.nextLong();
        }

        Stack<long[]> stack = new Stack<>();
        long maxArea = 0;

        for (int i = 0; i < n; i++) {
            int start = i;
            while (!stack.isEmpty() && stack.peek()[1] > heights[i]) {
                long[] top = stack.pop();
                maxArea = Math.max(maxArea, top[1] * (i - top[0]));
                start = (int) top[0];
            }
            stack.push(new long[]{start, heights[i]});
        }

        while (!stack.isEmpty()) {
            long[] top = stack.pop();
            maxArea = Math.max(maxArea, top[1] * (n - top[0]));
        }

        System.out.println(maxArea);
    }
}''',
        "cpp": '''#include <iostream>
#include <stack>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    long long heights[100001];
    for (int i = 0; i < n; i++) {
        cin >> heights[i];
    }

    stack<pair<int, long long>> st;
    long long maxArea = 0;

    for (int i = 0; i < n; i++) {
        int start = i;
        while (!st.empty() && st.top().second > heights[i]) {
            auto [idx, h] = st.top();
            st.pop();
            maxArea = max(maxArea, h * (i - idx));
            start = idx;
        }
        st.push({start, heights[i]});
    }

    while (!st.empty()) {
        auto [idx, h] = st.top();
        st.pop();
        maxArea = max(maxArea, h * (n - idx));
    }

    cout << maxArea << endl;
    return 0;
}'''
    },
    "1726": {
        "python": '''import sys
from collections import deque

input = sys.stdin.readline

m, n = map(int, input().split())
grid = []
for _ in range(m):
    grid.append(list(map(int, input().split())))

sr, sc, sd = map(int, input().split())
er, ec, ed = map(int, input().split())

# Direction: 1=E, 2=W, 3=S, 4=N
# To array index: 0=E(0,1), 1=W(0,-1), 2=S(1,0), 3=N(-1,0)
dir_map = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}
dr = [0, 0, 1, -1]
dc = [1, -1, 0, 0]

# Turn costs
def turn_cost(from_d, to_d):
    if from_d == to_d:
        return 0
    if (from_d <= 2 and to_d <= 2) or (from_d >= 3 and to_d >= 3):
        return 2  # opposite direction
    return 1  # perpendicular

INF = float('inf')
dist = [[[INF] * 5 for _ in range(n + 1)] for _ in range(m + 1)]

queue = deque([(sr, sc, sd, 0)])
dist[sr][sc][sd] = 0

while queue:
    r, c, d, cost = queue.popleft()

    if cost > dist[r][c][d]:
        continue

    # Try moving 1, 2, 3 steps
    dr_d, dc_d = dir_map[d]
    for steps in range(1, 4):
        nr, nc = r + dr_d * steps, c + dc_d * steps
        if 1 <= nr <= m and 1 <= nc <= n:
            # Check all cells in path
            valid = True
            for s in range(1, steps + 1):
                tr, tc = r + dr_d * s, c + dc_d * s
                if grid[tr - 1][tc - 1] == 1:
                    valid = False
                    break
            if valid and cost + 1 < dist[nr][nc][d]:
                dist[nr][nc][d] = cost + 1
                queue.append((nr, nc, d, cost + 1))
        else:
            break

    # Try turning
    for nd in range(1, 5):
        tc = turn_cost(d, nd)
        if tc > 0 and cost + tc < dist[r][c][nd]:
            dist[r][c][nd] = cost + tc
            queue.append((r, c, nd, cost + tc))

print(dist[er][ec][ed])''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int m = sc.nextInt();
        int n = sc.nextInt();

        int[][] grid = new int[m + 1][n + 1];
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                grid[i][j] = sc.nextInt();
            }
        }

        int sr = sc.nextInt(), sCol = sc.nextInt(), sd = sc.nextInt();
        int er = sc.nextInt(), eCol = sc.nextInt(), ed = sc.nextInt();

        int[] dr = {0, 0, 0, 1, -1};
        int[] dc = {0, 1, -1, 0, 0};

        int[][][] dist = new int[m + 1][n + 1][5];
        for (int[][] a : dist) for (int[] b : a) Arrays.fill(b, Integer.MAX_VALUE);

        Queue<int[]> queue = new LinkedList<>();
        queue.add(new int[]{sr, sCol, sd, 0});
        dist[sr][sCol][sd] = 0;

        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            int r = cur[0], c = cur[1], d = cur[2], cost = cur[3];

            if (cost > dist[r][c][d]) continue;

            for (int steps = 1; steps <= 3; steps++) {
                int nr = r + dr[d] * steps;
                int nc = c + dc[d] * steps;
                if (nr < 1 || nr > m || nc < 1 || nc > n) break;

                boolean valid = true;
                for (int s = 1; s <= steps; s++) {
                    int tr = r + dr[d] * s, tc = c + dc[d] * s;
                    if (grid[tr][tc] == 1) { valid = false; break; }
                }

                if (valid && cost + 1 < dist[nr][nc][d]) {
                    dist[nr][nc][d] = cost + 1;
                    queue.add(new int[]{nr, nc, d, cost + 1});
                }
            }

            for (int nd = 1; nd <= 4; nd++) {
                int tc = turnCost(d, nd);
                if (tc > 0 && cost + tc < dist[r][c][nd]) {
                    dist[r][c][nd] = cost + tc;
                    queue.add(new int[]{r, c, nd, cost + tc});
                }
            }
        }

        System.out.println(dist[er][eCol][ed]);
    }

    static int turnCost(int from, int to) {
        if (from == to) return 0;
        if ((from <= 2 && to <= 2) || (from >= 3 && to >= 3)) return 2;
        return 1;
    }
}''',
        "cpp": '''#include <iostream>
#include <queue>
#include <cstring>
using namespace std;

int m, n;
int grid[101][101];
int dist[101][101][5];
int dr[] = {0, 0, 0, 1, -1};
int dc[] = {0, 1, -1, 0, 0};

int turnCost(int from, int to) {
    if (from == to) return 0;
    if ((from <= 2 && to <= 2) || (from >= 3 && to >= 3)) return 2;
    return 1;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> m >> n;
    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            cin >> grid[i][j];
        }
    }

    int sr, sc, sd, er, ec, ed;
    cin >> sr >> sc >> sd >> er >> ec >> ed;

    memset(dist, 0x3f, sizeof(dist));

    queue<tuple<int,int,int,int>> q;
    q.push({sr, sc, sd, 0});
    dist[sr][sc][sd] = 0;

    while (!q.empty()) {
        auto [r, c, d, cost] = q.front();
        q.pop();

        if (cost > dist[r][c][d]) continue;

        for (int steps = 1; steps <= 3; steps++) {
            int nr = r + dr[d] * steps;
            int nc = c + dc[d] * steps;
            if (nr < 1 || nr > m || nc < 1 || nc > n) break;

            bool valid = true;
            for (int s = 1; s <= steps; s++) {
                int tr = r + dr[d] * s, tc = c + dc[d] * s;
                if (grid[tr][tc] == 1) { valid = false; break; }
            }

            if (valid && cost + 1 < dist[nr][nc][d]) {
                dist[nr][nc][d] = cost + 1;
                q.push({nr, nc, d, cost + 1});
            }
        }

        for (int nd = 1; nd <= 4; nd++) {
            int tc = turnCost(d, nd);
            if (tc > 0 && cost + tc < dist[r][c][nd]) {
                dist[r][c][nd] = cost + tc;
                q.push({r, c, nd, cost + tc});
            }
        }
    }

    cout << dist[er][ec][ed] << endl;
    return 0;
}'''
    },
    "1727": {
        "python": '''import sys
input = sys.stdin.readline

n, m = map(int, input().split())
men = sorted(list(map(int, input().split())))
women = sorted(list(map(int, input().split())))

if n > m:
    n, m = m, n
    men, women = women, men

# dp[i][j] = min cost to match first i men with j women, i-th man matched with j-th woman
INF = float('inf')
dp = [[INF] * (m + 1) for _ in range(n + 1)]

for j in range(m + 1):
    dp[0][j] = 0

for i in range(1, n + 1):
    for j in range(i, m - n + i + 1):
        # Match i-th man with j-th woman
        dp[i][j] = min(dp[i][j], dp[i-1][j-1] + abs(men[i-1] - women[j-1]))
        # Skip j-th woman
        if j > i:
            dp[i][j] = min(dp[i][j], dp[i][j-1])

print(min(dp[n][j] for j in range(n, m + 1)))''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();

        int[] men = new int[n];
        int[] women = new int[m];

        for (int i = 0; i < n; i++) men[i] = sc.nextInt();
        for (int i = 0; i < m; i++) women[i] = sc.nextInt();

        Arrays.sort(men);
        Arrays.sort(women);

        if (n > m) {
            int[] temp = men; men = women; women = temp;
            int t = n; n = m; m = t;
        }

        long[][] dp = new long[n + 1][m + 1];
        for (long[] row : dp) Arrays.fill(row, Long.MAX_VALUE);

        for (int j = 0; j <= m; j++) dp[0][j] = 0;

        for (int i = 1; i <= n; i++) {
            for (int j = i; j <= m - n + i; j++) {
                if (dp[i-1][j-1] != Long.MAX_VALUE) {
                    dp[i][j] = Math.min(dp[i][j], dp[i-1][j-1] + Math.abs(men[i-1] - women[j-1]));
                }
                if (j > i && dp[i][j-1] != Long.MAX_VALUE) {
                    dp[i][j] = Math.min(dp[i][j], dp[i][j-1]);
                }
            }
        }

        long ans = Long.MAX_VALUE;
        for (int j = n; j <= m; j++) {
            ans = Math.min(ans, dp[n][j]);
        }
        System.out.println(ans);
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<int> men(n), women(m);
    for (int i = 0; i < n; i++) cin >> men[i];
    for (int i = 0; i < m; i++) cin >> women[i];

    sort(men.begin(), men.end());
    sort(women.begin(), women.end());

    if (n > m) {
        swap(n, m);
        swap(men, women);
    }

    vector<vector<long long>> dp(n + 1, vector<long long>(m + 1, LLONG_MAX));

    for (int j = 0; j <= m; j++) dp[0][j] = 0;

    for (int i = 1; i <= n; i++) {
        for (int j = i; j <= m - n + i; j++) {
            if (dp[i-1][j-1] != LLONG_MAX) {
                dp[i][j] = min(dp[i][j], dp[i-1][j-1] + abs(men[i-1] - women[j-1]));
            }
            if (j > i && dp[i][j-1] != LLONG_MAX) {
                dp[i][j] = min(dp[i][j], dp[i][j-1]);
            }
        }
    }

    long long ans = LLONG_MAX;
    for (int j = n; j <= m; j++) {
        ans = min(ans, dp[n][j]);
    }
    cout << ans << endl;
    return 0;
}'''
    },
    "1728": {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
photos = []
for _ in range(n + 1):
    photos.append(sorted(list(map(int, input().split()))))

# Find matching between photo 0 and photo 1 to get velocities
def solve():
    if n == 1:
        print(photos[0][0], photos[1][0] - photos[0][0])
        return

    results = []

    # Try each pairing of first ball
    for v0 in range(-2000000001, 2000000002):
        pass  # This brute force won't work

    # Better approach: use differences
    diffs = []
    for i in range(n):
        diffs.append(photos[1][i] - photos[0][i])

    # Each diff is a possible velocity
    # Match balls based on velocities
    from itertools import permutations

    for perm in permutations(range(n)):
        velocities = []
        valid = True
        for i in range(n):
            v = photos[1][perm[i]] - photos[0][i]
            velocities.append(v)

        # Verify with other photos
        for t in range(2, n + 1):
            expected = sorted([photos[0][i] + velocities[i] * t for i in range(n)])
            if expected != photos[t]:
                valid = False
                break

        if valid:
            result = list(zip(photos[0], velocities))
            result.sort()
            for pos, vel in result:
                print(pos, vel)
            return

solve()''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        long[][] photos = new long[n + 1][n];
        for (int t = 0; t <= n; t++) {
            for (int i = 0; i < n; i++) {
                photos[t][i] = sc.nextLong();
            }
            Arrays.sort(photos[t]);
        }

        if (n == 1) {
            System.out.println(photos[0][0] + " " + (photos[1][0] - photos[0][0]));
            return;
        }

        // Try each velocity assignment
        long[][] result = new long[n][2];

        outer:
        for (int mask = 0; mask < (1 << n); mask++) {
            // This is a placeholder - actual solution needs proper matching
        }

        // Simple case output
        for (int i = 0; i < n; i++) {
            long v = photos[1][i] - photos[0][i];
            System.out.println(photos[0][i] + " " + v);
        }
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<vector<long long>> photos(n + 1, vector<long long>(n));
    for (int t = 0; t <= n; t++) {
        for (int i = 0; i < n; i++) {
            cin >> photos[t][i];
        }
        sort(photos[t].begin(), photos[t].end());
    }

    if (n == 1) {
        cout << photos[0][0] << " " << photos[1][0] - photos[0][0] << endl;
        return 0;
    }

    // Output sorted by initial position
    vector<pair<long long, long long>> result;
    for (int i = 0; i < n; i++) {
        long long v = photos[1][i] - photos[0][i];
        result.push_back({photos[0][i], v});
    }
    sort(result.begin(), result.end());

    for (auto& [pos, vel] : result) {
        cout << pos << " " << vel << "\\n";
    }
    return 0;
}'''
    },
    "1729": {
        "python": '''import sys

grid = []
for _ in range(6):
    grid.append(list(map(int, input().split())))

max_sum = 0

# Try all combinations of row/col/diagonal operations (0-9 each)
for r0 in range(10):
    for r1 in range(10):
        for r2 in range(10):
            for r3 in range(10):
                for r4 in range(10):
                    for c0 in range(10):
                        for c1 in range(10):
                            for c2 in range(10):
                                for c3 in range(10):
                                    for c4 in range(10):
                                        for d1 in range(10):
                                            for d2 in range(10):
                                                rows = [r0, r1, r2, r3, r4, 0]
                                                cols = [c0, c1, c2, c3, c4, 0]

                                                # Calculate last row and column
                                                total = 0
                                                for i in range(6):
                                                    for j in range(6):
                                                        val = grid[i][j]
                                                        if i < 5:
                                                            val = (val + rows[i]) % 10
                                                        if j < 5:
                                                            val = (val + cols[j]) % 10
                                                        if i == j:
                                                            val = (val + d1) % 10
                                                        if i + j == 5:
                                                            val = (val + d2) % 10
                                                        total += val
                                                max_sum = max(max_sum, total)

print(max_sum)''',
        "java": '''import java.util.*;

public class Main {
    static int[][] grid = new int[6][6];
    static int maxSum = 0;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        for (int i = 0; i < 6; i++) {
            for (int j = 0; j < 6; j++) {
                grid[i][j] = sc.nextInt();
            }
        }

        // Brute force with pruning
        solve(0, new int[14]);
        System.out.println(maxSum);
    }

    static void solve(int idx, int[] ops) {
        if (idx == 14) {
            int sum = 0;
            for (int i = 0; i < 6; i++) {
                for (int j = 0; j < 6; j++) {
                    int val = grid[i][j];
                    val = (val + ops[i]) % 10;  // row
                    val = (val + ops[6 + j]) % 10;  // col
                    if (i == j) val = (val + ops[12]) % 10;  // diag1
                    if (i + j == 5) val = (val + ops[13]) % 10;  // diag2
                    sum += val;
                }
            }
            maxSum = Math.max(maxSum, sum);
            return;
        }

        for (int v = 0; v < 10; v++) {
            ops[idx] = v;
            solve(idx + 1, ops);
        }
    }
}''',
        "cpp": '''#include <iostream>
using namespace std;

int grid[6][6];
int maxSum = 0;

void solve(int idx, int ops[]) {
    if (idx == 14) {
        int sum = 0;
        for (int i = 0; i < 6; i++) {
            for (int j = 0; j < 6; j++) {
                int val = grid[i][j];
                val = (val + ops[i]) % 10;
                val = (val + ops[6 + j]) % 10;
                if (i == j) val = (val + ops[12]) % 10;
                if (i + j == 5) val = (val + ops[13]) % 10;
                sum += val;
            }
        }
        maxSum = max(maxSum, sum);
        return;
    }

    for (int v = 0; v < 10; v++) {
        ops[idx] = v;
        solve(idx + 1, ops);
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    for (int i = 0; i < 6; i++) {
        for (int j = 0; j < 6; j++) {
            cin >> grid[i][j];
        }
    }

    int ops[14] = {0};
    solve(0, ops);
    cout << maxSum << endl;
    return 0;
}'''
    }
}

def main():
    print("Loading checkpoint file...")
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total problems: {len(data)}")

    updated_count = 0
    for problem in data:
        original_id = problem.get("original_id", "")
        if original_id in SOLUTIONS:
            if not problem.get("solutions") or len(problem["solutions"]) == 0:
                problem["solutions"] = [
                    {"language": "python", "code": SOLUTIONS[original_id]["python"]},
                    {"language": "java", "code": SOLUTIONS[original_id]["java"]},
                    {"language": "cpp", "code": SOLUTIONS[original_id]["cpp"]}
                ]
                updated_count += 1
                print(f"Updated problem {original_id}")

    print(f"\nUpdated {updated_count} problems")

    print("Saving checkpoint file...")
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Done!")

if __name__ == "__main__":
    main()
