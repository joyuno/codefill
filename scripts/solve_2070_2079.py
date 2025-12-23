#!/usr/bin/env python3
import json

# Load the checkpoint file
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r') as f:
    data = json.load(f)

# Solutions for problems 2070-2079
solutions = {
    2070: {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))

# Check if the sequence is a necklace (all rotations >= original)
is_necklace = True
for i in range(1, n):
    rotated = a[i:] + a[:i]
    if rotated < a:
        is_necklace = False
        break

print("Yes" if is_necklace else "No")
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());
        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] a = new int[n];
        for (int i = 0; i < n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
        }

        boolean isNecklace = true;
        for (int r = 1; r < n && isNecklace; r++) {
            for (int i = 0; i < n; i++) {
                int orig = a[i];
                int rot = a[(i + r) % n];
                if (rot < orig) {
                    isNecklace = false;
                    break;
                } else if (rot > orig) {
                    break;
                }
            }
        }

        System.out.println(isNecklace ? "Yes" : "No");
    }
}
''',
        "cpp": '''#include <iostream>
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

    bool isNecklace = true;
    for (int r = 1; r < n && isNecklace; r++) {
        for (int i = 0; i < n; i++) {
            int orig = a[i];
            int rot = a[(i + r) % n];
            if (rot < orig) {
                isNecklace = false;
                break;
            } else if (rot > orig) {
                break;
            }
        }
    }

    cout << (isNecklace ? "Yes" : "No") << endl;
    return 0;
}
'''
    },
    2071: {
        "python": '''import sys
from collections import deque
input = sys.stdin.readline

def bfs(grid, start, color, visited):
    n = len(grid)
    m = len(grid[0])
    q = deque([start])
    visited[start[0]][start[1]] = True
    area = 0

    while q:
        r, c = q.popleft()
        area += 1
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m and not visited[nr][nc]:
                if grid[nr][nc] == color:
                    visited[nr][nc] = True
                    q.append((nr, nc))

    return area

n, m = map(int, input().split())
grid = []
for _ in range(n):
    row = list(map(int, input().split()))
    grid.append(row)

visited = [[False] * m for _ in range(n)]
territories = {1: 0, 2: 0}

for i in range(n):
    for j in range(m):
        if not visited[i][j] and grid[i][j] in [1, 2]:
            color = grid[i][j]
            area = bfs(grid, (i, j), color, visited)
            territories[color] += area

print(territories[1], territories[2])
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    static int n, m;
    static int[][] grid;
    static boolean[][] visited;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        n = Integer.parseInt(st.nextToken());
        m = Integer.parseInt(st.nextToken());

        grid = new int[n][m];
        visited = new boolean[n][m];

        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < m; j++) {
                grid[i][j] = Integer.parseInt(st.nextToken());
            }
        }

        int black = 0, white = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (!visited[i][j] && grid[i][j] > 0) {
                    int area = bfs(i, j, grid[i][j]);
                    if (grid[i][j] == 1) black += area;
                    else white += area;
                }
            }
        }

        System.out.println(black + " " + white);
    }

    static int bfs(int r, int c, int color) {
        Queue<int[]> q = new LinkedList<>();
        q.add(new int[]{r, c});
        visited[r][c] = true;
        int area = 0;
        int[] dr = {0, 0, 1, -1};
        int[] dc = {1, -1, 0, 0};

        while (!q.isEmpty()) {
            int[] cur = q.poll();
            area++;
            for (int d = 0; d < 4; d++) {
                int nr = cur[0] + dr[d];
                int nc = cur[1] + dc[d];
                if (nr >= 0 && nr < n && nc >= 0 && nc < m && !visited[nr][nc] && grid[nr][nc] == color) {
                    visited[nr][nc] = true;
                    q.add(new int[]{nr, nc});
                }
            }
        }
        return area;
    }
}
''',
        "cpp": '''#include <iostream>
#include <queue>
#include <vector>
using namespace std;

int n, m;
vector<vector<int>> grid;
vector<vector<bool>> visited;
int dr[] = {0, 0, 1, -1};
int dc[] = {1, -1, 0, 0};

int bfs(int r, int c, int color) {
    queue<pair<int,int>> q;
    q.push({r, c});
    visited[r][c] = true;
    int area = 0;

    while (!q.empty()) {
        auto [cr, cc] = q.front();
        q.pop();
        area++;
        for (int d = 0; d < 4; d++) {
            int nr = cr + dr[d];
            int nc = cc + dc[d];
            if (nr >= 0 && nr < n && nc >= 0 && nc < m && !visited[nr][nc] && grid[nr][nc] == color) {
                visited[nr][nc] = true;
                q.push({nr, nc});
            }
        }
    }
    return area;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> m;
    grid.resize(n, vector<int>(m));
    visited.resize(n, vector<bool>(m, false));

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            cin >> grid[i][j];
        }
    }

    int black = 0, white = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (!visited[i][j] && grid[i][j] > 0) {
                int area = bfs(i, j, grid[i][j]);
                if (grid[i][j] == 1) black += area;
                else white += area;
            }
        }
    }

    cout << black << " " << white << endl;
    return 0;
}
'''
    },
    2072: {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
board = [[0] * 19 for _ in range(19)]
turn = 1  # 1 = black, 2 = white

def check_win(x, y, color):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    for dx, dy in directions:
        count = 1
        # forward
        nx, ny = x + dx, y + dy
        while 0 <= nx < 19 and 0 <= ny < 19 and board[nx][ny] == color:
            count += 1
            nx += dx
            ny += dy
        # backward
        nx, ny = x - dx, y - dy
        while 0 <= nx < 19 and 0 <= ny < 19 and board[nx][ny] == color:
            count += 1
            nx -= dx
            ny -= dy

        if count == 5:
            return True
    return False

winner = 0
for i in range(n):
    x, y = map(int, input().split())
    x -= 1
    y -= 1

    if winner == 0:
        board[x][y] = turn
        if check_win(x, y, turn):
            winner = i + 1
        turn = 3 - turn

print(winner if winner > 0 else -1)
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    static int[][] board = new int[19][19];

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());
        int turn = 1;
        int winner = 0;

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int x = Integer.parseInt(st.nextToken()) - 1;
            int y = Integer.parseInt(st.nextToken()) - 1;

            if (winner == 0) {
                board[x][y] = turn;
                if (checkWin(x, y, turn)) {
                    winner = i + 1;
                }
                turn = 3 - turn;
            }
        }

        System.out.println(winner > 0 ? winner : -1);
    }

    static boolean checkWin(int x, int y, int color) {
        int[][] dirs = {{1, 0}, {0, 1}, {1, 1}, {1, -1}};

        for (int[] d : dirs) {
            int count = 1;
            int nx = x + d[0], ny = y + d[1];
            while (nx >= 0 && nx < 19 && ny >= 0 && ny < 19 && board[nx][ny] == color) {
                count++;
                nx += d[0];
                ny += d[1];
            }
            nx = x - d[0];
            ny = y - d[1];
            while (nx >= 0 && nx < 19 && ny >= 0 && ny < 19 && board[nx][ny] == color) {
                count++;
                nx -= d[0];
                ny -= d[1];
            }
            if (count == 5) return true;
        }
        return false;
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int board[19][19];

bool checkWin(int x, int y, int color) {
    int dx[] = {1, 0, 1, 1};
    int dy[] = {0, 1, 1, -1};

    for (int d = 0; d < 4; d++) {
        int count = 1;
        int nx = x + dx[d], ny = y + dy[d];
        while (nx >= 0 && nx < 19 && ny >= 0 && ny < 19 && board[nx][ny] == color) {
            count++;
            nx += dx[d];
            ny += dy[d];
        }
        nx = x - dx[d];
        ny = y - dy[d];
        while (nx >= 0 && nx < 19 && ny >= 0 && ny < 19 && board[nx][ny] == color) {
            count++;
            nx -= dx[d];
            ny -= dy[d];
        }
        if (count == 5) return true;
    }
    return false;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    int turn = 1;
    int winner = 0;

    for (int i = 0; i < n; i++) {
        int x, y;
        cin >> x >> y;
        x--; y--;

        if (winner == 0) {
            board[x][y] = turn;
            if (checkWin(x, y, turn)) {
                winner = i + 1;
            }
            turn = 3 - turn;
        }
    }

    cout << (winner > 0 ? winner : -1) << endl;
    return 0;
}
'''
    },
    2073: {
        "python": '''import sys
input = sys.stdin.readline

D, P = map(int, input().split())
# dp[i] = max capacity to reach distance i
dp = [0] * (D + 1)
dp[0] = float('inf')

for _ in range(P):
    L, C = map(int, input().split())
    for i in range(D, L - 1, -1):
        if dp[i - L] > 0:
            dp[i] = max(dp[i], min(dp[i - L], C))

print(dp[D])
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int D = Integer.parseInt(st.nextToken());
        int P = Integer.parseInt(st.nextToken());

        int[] dp = new int[D + 1];
        dp[0] = Integer.MAX_VALUE;

        for (int i = 0; i < P; i++) {
            st = new StringTokenizer(br.readLine());
            int L = Integer.parseInt(st.nextToken());
            int C = Integer.parseInt(st.nextToken());

            for (int j = D; j >= L; j--) {
                if (dp[j - L] > 0) {
                    dp[j] = Math.max(dp[j], Math.min(dp[j - L], C));
                }
            }
        }

        System.out.println(dp[D]);
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
using namespace std;

int dp[100001];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int D, P;
    cin >> D >> P;

    dp[0] = 1e9;

    for (int i = 0; i < P; i++) {
        int L, C;
        cin >> L >> C;

        for (int j = D; j >= L; j--) {
            if (dp[j - L] > 0) {
                dp[j] = max(dp[j], min(dp[j - L], C));
            }
        }
    }

    cout << dp[D] << endl;
    return 0;
}
'''
    },
    2074: {
        "python": '''import sys
from collections import deque
input = sys.stdin.readline

P = int(input())

# BFS to find minimum steps to compute x^P
# State: (a, b) where we have x^a and x^b in two variables
# We can do: a+a, a+b, b+a, b+b
visited = {}
q = deque([(1, 0, 0)])  # (larger, smaller, steps)
visited[(1, 0)] = 0

result = -1
while q:
    a, b, steps = q.popleft()

    if a == P or b == P:
        result = steps
        break

    # Generate next states
    next_states = [
        (a + a, a),
        (a + b, max(a, b)),
        (b + a, max(a, b)),
        (b + b, b)
    ]

    for na, nb in next_states:
        if na > P + P:
            continue
        key = (max(na, nb), min(na, nb))
        if key not in visited:
            visited[key] = steps + 1
            q.append((key[0], key[1], steps + 1))

print(result)
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int P = Integer.parseInt(br.readLine());

        Map<Long, Integer> visited = new HashMap<>();
        Queue<long[]> q = new LinkedList<>();
        q.add(new long[]{1, 0, 0});
        visited.put(1L * 20001 + 0, 0);

        int result = -1;
        while (!q.isEmpty()) {
            long[] cur = q.poll();
            int a = (int)cur[0], b = (int)cur[1], steps = (int)cur[2];

            if (a == P || b == P) {
                result = steps;
                break;
            }

            int[][] next = {{a+a, a}, {a+b, Math.max(a,b)}, {b+a, Math.max(a,b)}, {b+b, b}};

            for (int[] ns : next) {
                int na = ns[0], nb = ns[1];
                if (na > 2 * P) continue;
                int ma = Math.max(na, nb), mi = Math.min(na, nb);
                long key = (long)ma * 20001 + mi;
                if (!visited.containsKey(key)) {
                    visited.put(key, steps + 1);
                    q.add(new long[]{ma, mi, steps + 1});
                }
            }
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
#include <queue>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int P;
    cin >> P;

    map<pair<int,int>, int> visited;
    queue<tuple<int,int,int>> q;
    q.push({1, 0, 0});
    visited[{1, 0}] = 0;

    int result = -1;
    while (!q.empty()) {
        auto [a, b, steps] = q.front();
        q.pop();

        if (a == P || b == P) {
            result = steps;
            break;
        }

        vector<pair<int,int>> next = {{a+a, a}, {a+b, max(a,b)}, {b+a, max(a,b)}, {b+b, b}};

        for (auto [na, nb] : next) {
            if (na > 2 * P) continue;
            int ma = max(na, nb), mi = min(na, nb);
            if (visited.find({ma, mi}) == visited.end()) {
                visited[{ma, mi}] = steps + 1;
                q.push({ma, mi, steps + 1});
            }
        }
    }

    cout << result << endl;
    return 0;
}
'''
    },
    2075: {
        "python": '''import sys
import heapq
input = sys.stdin.readline

n = int(input())
heap = []

for _ in range(n):
    row = list(map(int, input().split()))
    for num in row:
        if len(heap) < n:
            heapq.heappush(heap, num)
        elif num > heap[0]:
            heapq.heapreplace(heap, num)

print(heap[0])
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());

        PriorityQueue<Integer> pq = new PriorityQueue<>();

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                int num = Integer.parseInt(st.nextToken());
                if (pq.size() < n) {
                    pq.add(num);
                } else if (num > pq.peek()) {
                    pq.poll();
                    pq.add(num);
                }
            }
        }

        System.out.println(pq.peek());
    }
}
''',
        "cpp": '''#include <iostream>
#include <queue>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    priority_queue<int, vector<int>, greater<int>> pq;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            int num;
            cin >> num;
            if (pq.size() < n) {
                pq.push(num);
            } else if (num > pq.top()) {
                pq.pop();
                pq.push(num);
            }
        }
    }

    cout << pq.top() << endl;
    return 0;
}
'''
    },
    2076: {
        "python": '''import sys
import math
input = sys.stdin.readline

n = int(input())
sum_x = 0
sum_y = 0

for _ in range(n):
    x, y = map(int, input().split())
    sum_x += x
    sum_y += y

magnitude = math.sqrt(sum_x * sum_x + sum_y * sum_y)
print(f"{magnitude:.2f}")
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());

        long sumX = 0, sumY = 0;
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());
            sumX += x;
            sumY += y;
        }

        double magnitude = Math.sqrt(sumX * sumX + sumY * sumY);
        System.out.printf("%.2f%n", magnitude);
    }
}
''',
        "cpp": '''#include <iostream>
#include <cmath>
#include <iomanip>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    long long sumX = 0, sumY = 0;
    for (int i = 0; i < n; i++) {
        int x, y;
        cin >> x >> y;
        sumX += x;
        sumY += y;
    }

    double magnitude = sqrt((double)sumX * sumX + (double)sumY * sumY);
    cout << fixed << setprecision(2) << magnitude << endl;
    return 0;
}
'''
    },
    2077: {
        "python": '''import sys
from collections import deque
input = sys.stdin.readline

n, m = map(int, input().split())
# BFS to find minimum mineral X needed to reach (n, m) from (1, 1)
# Each cell has cost of mineral X

grid = []
for i in range(n):
    row = list(map(int, input().split()))
    grid.append(row)

dist = [[float('inf')] * m for _ in range(n)]
dist[0][0] = grid[0][0]
dq = deque([(0, 0)])

while dq:
    r, c = dq.popleft()
    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < n and 0 <= nc < m:
            new_dist = dist[r][c] + grid[nr][nc]
            if new_dist < dist[nr][nc]:
                dist[nr][nc] = new_dist
                dq.append((nr, nc))

print(dist[n-1][m-1])
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        int[][] grid = new int[n][m];
        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < m; j++) {
                grid[i][j] = Integer.parseInt(st.nextToken());
            }
        }

        int[][] dist = new int[n][m];
        for (int[] row : dist) Arrays.fill(row, Integer.MAX_VALUE);
        dist[0][0] = grid[0][0];

        Deque<int[]> dq = new ArrayDeque<>();
        dq.add(new int[]{0, 0});
        int[] dr = {0, 0, 1, -1};
        int[] dc = {1, -1, 0, 0};

        while (!dq.isEmpty()) {
            int[] cur = dq.pollFirst();
            int r = cur[0], c = cur[1];
            for (int d = 0; d < 4; d++) {
                int nr = r + dr[d], nc = c + dc[d];
                if (nr >= 0 && nr < n && nc >= 0 && nc < m) {
                    int newDist = dist[r][c] + grid[nr][nc];
                    if (newDist < dist[nr][nc]) {
                        dist[nr][nc] = newDist;
                        dq.addLast(new int[]{nr, nc});
                    }
                }
            }
        }

        System.out.println(dist[n-1][m-1]);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <queue>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<vector<int>> grid(n, vector<int>(m));
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            cin >> grid[i][j];
        }
    }

    vector<vector<int>> dist(n, vector<int>(m, INT_MAX));
    dist[0][0] = grid[0][0];

    deque<pair<int,int>> dq;
    dq.push_back({0, 0});
    int dr[] = {0, 0, 1, -1};
    int dc[] = {1, -1, 0, 0};

    while (!dq.empty()) {
        auto [r, c] = dq.front();
        dq.pop_front();
        for (int d = 0; d < 4; d++) {
            int nr = r + dr[d], nc = c + dc[d];
            if (nr >= 0 && nr < n && nc >= 0 && nc < m) {
                int newDist = dist[r][c] + grid[nr][nc];
                if (newDist < dist[nr][nc]) {
                    dist[nr][nc] = newDist;
                    dq.push_back({nr, nc});
                }
            }
        }
    }

    cout << dist[n-1][m-1] << endl;
    return 0;
}
'''
    },
    2078: {
        "python": '''import sys
input = sys.stdin.readline

p, q = map(int, input().split())

left = 0
right = 0

while p != q:
    if p > q:
        left += 1
        p -= q
    else:
        right += 1
        q -= p

print(left, right)
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int p = Integer.parseInt(st.nextToken());
        int q = Integer.parseInt(st.nextToken());

        int left = 0, right = 0;

        while (p != q) {
            if (p > q) {
                left++;
                p -= q;
            } else {
                right++;
                q -= p;
            }
        }

        System.out.println(left + " " + right);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int p, q;
    cin >> p >> q;

    int left = 0, right = 0;

    while (p != q) {
        if (p > q) {
            left++;
            p -= q;
        } else {
            right++;
            q -= p;
        }
    }

    cout << left << " " << right << endl;
    return 0;
}
'''
    },
    2079: {
        "python": '''import sys
input = sys.stdin.readline

s = input().strip()
n = len(s)

# is_palin[i][j] = True if s[i:j+1] is palindrome
is_palin = [[False] * n for _ in range(n)]
for i in range(n):
    is_palin[i][i] = True
for i in range(n - 1):
    if s[i] == s[i + 1]:
        is_palin[i][i + 1] = True
for length in range(3, n + 1):
    for i in range(n - length + 1):
        j = i + length - 1
        if s[i] == s[j] and is_palin[i + 1][j - 1]:
            is_palin[i][j] = True

# dp[i] = minimum palindromes to partition s[0:i+1]
dp = [float('inf')] * n
for i in range(n):
    if is_palin[0][i]:
        dp[i] = 1
    else:
        for j in range(i):
            if is_palin[j + 1][i]:
                dp[i] = min(dp[i], dp[j] + 1)

print(dp[n - 1])
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        int n = s.length();

        boolean[][] isPalin = new boolean[n][n];
        for (int i = 0; i < n; i++) {
            isPalin[i][i] = true;
        }
        for (int i = 0; i < n - 1; i++) {
            if (s.charAt(i) == s.charAt(i + 1)) {
                isPalin[i][i + 1] = true;
            }
        }
        for (int len = 3; len <= n; len++) {
            for (int i = 0; i <= n - len; i++) {
                int j = i + len - 1;
                if (s.charAt(i) == s.charAt(j) && isPalin[i + 1][j - 1]) {
                    isPalin[i][j] = true;
                }
            }
        }

        int[] dp = new int[n];
        Arrays.fill(dp, Integer.MAX_VALUE);
        for (int i = 0; i < n; i++) {
            if (isPalin[0][i]) {
                dp[i] = 1;
            } else {
                for (int j = 0; j < i; j++) {
                    if (isPalin[j + 1][i]) {
                        dp[i] = Math.min(dp[i], dp[j] + 1);
                    }
                }
            }
        }

        System.out.println(dp[n - 1]);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <string>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    cin >> s;
    int n = s.length();

    vector<vector<bool>> isPalin(n, vector<bool>(n, false));
    for (int i = 0; i < n; i++) {
        isPalin[i][i] = true;
    }
    for (int i = 0; i < n - 1; i++) {
        if (s[i] == s[i + 1]) {
            isPalin[i][i + 1] = true;
        }
    }
    for (int len = 3; len <= n; len++) {
        for (int i = 0; i <= n - len; i++) {
            int j = i + len - 1;
            if (s[i] == s[j] && isPalin[i + 1][j - 1]) {
                isPalin[i][j] = true;
            }
        }
    }

    vector<int> dp(n, INT_MAX);
    for (int i = 0; i < n; i++) {
        if (isPalin[0][i]) {
            dp[i] = 1;
        } else {
            for (int j = 0; j < i; j++) {
                if (isPalin[j + 1][i]) {
                    dp[i] = min(dp[i], dp[j] + 1);
                }
            }
        }
    }

    cout << dp[n - 1] << endl;
    return 0;
}
'''
    }
}

# Update the problems
count = 0
for i, problem in enumerate(data):
    try:
        oid = int(problem.get('original_id', 0))
    except:
        continue

    if oid in solutions:
        if not problem.get('solutions') or len(problem.get('solutions', [])) == 0:
            problem['solutions'] = [
                {"language": "python", "code": solutions[oid]["python"]},
                {"language": "java", "code": solutions[oid]["java"]},
                {"language": "cpp", "code": solutions[oid]["cpp"]}
            ]
            count += 1
            print(f"Updated problem {oid}")

# Save the checkpoint file
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Batch 8 (2070-2079) completed! Updated {count} problems.")
