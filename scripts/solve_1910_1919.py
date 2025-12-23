import json

# Load the checkpoint file
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r') as f:
    data = json.load(f)

# Create a mapping from original_id to index
id_to_idx = {}
for idx, p in enumerate(data):
    if 'original_id' in p:
        id_to_idx[p['original_id']] = idx

solutions = {}

# Problem 1910: Stone grouping (graph problem)
solutions['1910'] = [
    {
        "language": "python",
        "code": """import sys
from itertools import combinations
input = sys.stdin.readline

n = int(input())
adj = [[] for _ in range(n + 1)]

for i in range(1, n + 1):
    line = list(map(int, input().split()))
    L = line[0]
    for j in range(1, L + 1):
        adj[i].append(line[j])

# Try all possible subsets and check validity
best_count = 0
best_set = []

for mask in range(1, 1 << n):
    group = []
    for i in range(n):
        if mask & (1 << i):
            group.append(i + 1)

    # Check if valid: for each node in group, count of same-group neighbors is even
    valid = True
    for node in group:
        cnt = 0
        for neighbor in adj[node]:
            if neighbor in group:
                cnt += 1
        if cnt % 2 != 0:
            valid = False
            break

    if valid and len(group) > best_count:
        best_count = len(group)
        best_set = group

print(best_count)
print(' '.join(map(str, best_set)))
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i <= n; i++) adj.add(new ArrayList<>());

        for (int i = 1; i <= n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int L = Integer.parseInt(st.nextToken());
            for (int j = 0; j < L; j++) {
                adj.get(i).add(Integer.parseInt(st.nextToken()));
            }
        }

        int bestCount = 0;
        List<Integer> bestSet = new ArrayList<>();

        for (int mask = 1; mask < (1 << n); mask++) {
            List<Integer> group = new ArrayList<>();
            for (int i = 0; i < n; i++) {
                if ((mask & (1 << i)) != 0) {
                    group.add(i + 1);
                }
            }

            Set<Integer> groupSet = new HashSet<>(group);
            boolean valid = true;
            for (int node : group) {
                int cnt = 0;
                for (int neighbor : adj.get(node)) {
                    if (groupSet.contains(neighbor)) cnt++;
                }
                if (cnt % 2 != 0) {
                    valid = false;
                    break;
                }
            }

            if (valid && group.size() > bestCount) {
                bestCount = group.size();
                bestSet = new ArrayList<>(group);
            }
        }

        System.out.println(bestCount);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < bestSet.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(bestSet.get(i));
        }
        System.out.println(sb);
    }
}"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <vector>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<vector<int>> adj(n + 1);
    for (int i = 1; i <= n; i++) {
        int L;
        cin >> L;
        for (int j = 0; j < L; j++) {
            int x;
            cin >> x;
            adj[i].push_back(x);
        }
    }

    int bestCount = 0;
    vector<int> bestSet;

    for (int mask = 1; mask < (1 << n); mask++) {
        vector<int> group;
        for (int i = 0; i < n; i++) {
            if (mask & (1 << i)) {
                group.push_back(i + 1);
            }
        }

        set<int> groupSet(group.begin(), group.end());
        bool valid = true;
        for (int node : group) {
            int cnt = 0;
            for (int neighbor : adj[node]) {
                if (groupSet.count(neighbor)) cnt++;
            }
            if (cnt % 2 != 0) {
                valid = false;
                break;
            }
        }

        if (valid && (int)group.size() > bestCount) {
            bestCount = group.size();
            bestSet = group;
        }
    }

    cout << bestCount << "\\n";
    for (int i = 0; i < (int)bestSet.size(); i++) {
        if (i > 0) cout << " ";
        cout << bestSet[i];
    }
    cout << "\\n";

    return 0;
}"""
    }
]

# Problem 1911: Cover puddles with planks (greedy)
solutions['1911'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

N, L = map(int, input().split())
puddles = []
for _ in range(N):
    s, e = map(int, input().split())
    puddles.append((s, e))

puddles.sort()

count = 0
covered = 0

for s, e in puddles:
    if covered < s:
        covered = s
    if covered < e:
        # Need planks to cover from covered to e
        need = (e - covered + L - 1) // L
        count += need
        covered += need * L

print(count)
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int N = Integer.parseInt(st.nextToken());
        int L = Integer.parseInt(st.nextToken());

        int[][] puddles = new int[N][2];
        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            puddles[i][0] = Integer.parseInt(st.nextToken());
            puddles[i][1] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(puddles, (a, b) -> a[0] - b[0]);

        int count = 0;
        long covered = 0;

        for (int[] p : puddles) {
            int s = p[0], e = p[1];
            if (covered < s) covered = s;
            if (covered < e) {
                int need = (int)((e - covered + L - 1) / L);
                count += need;
                covered += (long)need * L;
            }
        }

        System.out.println(count);
    }
}"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, L;
    cin >> N >> L;

    vector<pair<int, int>> puddles(N);
    for (int i = 0; i < N; i++) {
        cin >> puddles[i].first >> puddles[i].second;
    }

    sort(puddles.begin(), puddles.end());

    int count = 0;
    long long covered = 0;

    for (auto& p : puddles) {
        int s = p.first, e = p.second;
        if (covered < s) covered = s;
        if (covered < e) {
            int need = (e - covered + L - 1) / L;
            count += need;
            covered += (long long)need * L;
        }
    }

    cout << count << endl;

    return 0;
}"""
    }
]

# Problem 1912: Maximum subarray sum (Kadane's algorithm)
solutions['1912'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

n = int(input())
arr = list(map(int, input().split()))

max_sum = arr[0]
current_sum = arr[0]

for i in range(1, n):
    current_sum = max(arr[i], current_sum + arr[i])
    max_sum = max(max_sum, current_sum)

print(max_sum)
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        int maxSum = arr[0];
        int currentSum = arr[0];

        for (int i = 1; i < n; i++) {
            currentSum = Math.max(arr[i], currentSum + arr[i]);
            maxSum = Math.max(maxSum, currentSum);
        }

        System.out.println(maxSum);
    }
}"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int arr[100001];
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    int maxSum = arr[0];
    int currentSum = arr[0];

    for (int i = 1; i < n; i++) {
        currentSum = max(arr[i], currentSum + arr[i]);
        maxSum = max(maxSum, currentSum);
    }

    cout << maxSum << endl;

    return 0;
}"""
    }
]

# Problem 1913: Snail number spiral
solutions['1913'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

n = int(input())
target = int(input())

grid = [[0] * n for _ in range(n)]

# Start from center
mid = n // 2
x, y = mid, mid
grid[x][y] = 1

num = 2
# Direction: up, right, down, left
dx = [-1, 0, 1, 0]
dy = [0, 1, 0, -1]

step = 1
d = 0  # Start moving up

target_pos = (mid + 1, mid + 1) if target == 1 else None

while num <= n * n:
    for _ in range(2):  # Each step size is used twice
        for _ in range(step):
            if num > n * n:
                break
            x += dx[d]
            y += dy[d]
            grid[x][y] = num
            if num == target:
                target_pos = (x + 1, y + 1)
            num += 1
        d = (d + 1) % 4
    step += 1

for row in grid:
    print(' '.join(map(str, row)))
print(target_pos[0], target_pos[1])
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        int target = Integer.parseInt(br.readLine().trim());

        int[][] grid = new int[n][n];
        int mid = n / 2;
        int x = mid, y = mid;
        grid[x][y] = 1;

        int num = 2;
        int[] dx = {-1, 0, 1, 0};
        int[] dy = {0, 1, 0, -1};

        int step = 1;
        int d = 0;

        int tx = mid, ty = mid;
        if (target == 1) {
            tx = mid;
            ty = mid;
        }

        while (num <= n * n) {
            for (int t = 0; t < 2; t++) {
                for (int s = 0; s < step && num <= n * n; s++) {
                    x += dx[d];
                    y += dy[d];
                    grid[x][y] = num;
                    if (num == target) {
                        tx = x;
                        ty = y;
                    }
                    num++;
                }
                d = (d + 1) % 4;
            }
            step++;
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (j > 0) sb.append(" ");
                sb.append(grid[i][j]);
            }
            sb.append("\\n");
        }
        sb.append((tx + 1) + " " + (ty + 1));
        System.out.println(sb);
    }
}"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
using namespace std;

int grid[1000][1000];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, target;
    cin >> n >> target;

    int mid = n / 2;
    int x = mid, y = mid;
    grid[x][y] = 1;

    int num = 2;
    int dx[] = {-1, 0, 1, 0};
    int dy[] = {0, 1, 0, -1};

    int step = 1;
    int d = 0;

    int tx = mid, ty = mid;

    while (num <= n * n) {
        for (int t = 0; t < 2; t++) {
            for (int s = 0; s < step && num <= n * n; s++) {
                x += dx[d];
                y += dy[d];
                grid[x][y] = num;
                if (num == target) {
                    tx = x;
                    ty = y;
                }
                num++;
            }
            d = (d + 1) % 4;
        }
        step++;
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (j > 0) cout << " ";
            cout << grid[i][j];
        }
        cout << "\\n";
    }
    cout << (tx + 1) << " " << (ty + 1) << "\\n";

    return 0;
}"""
    }
]

# Problem 1914: Tower of Hanoi (with big integers)
solutions['1914'] = [
    {
        "language": "python",
        "code": """import sys
sys.setrecursionlimit(1000000)

def hanoi(n, src, dst, aux, moves):
    if n == 1:
        moves.append((src, dst))
        return
    hanoi(n - 1, src, aux, dst, moves)
    moves.append((src, dst))
    hanoi(n - 1, aux, dst, src, moves)

n = int(input())

# 2^n - 1 can be very large
print(pow(2, n) - 1)

if n <= 20:
    moves = []
    hanoi(n, 1, 3, 2, moves)
    for src, dst in moves:
        print(src, dst)
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;
import java.io.*;
import java.math.BigInteger;

public class Main {
    static StringBuilder sb = new StringBuilder();

    static void hanoi(int n, int src, int dst, int aux) {
        if (n == 1) {
            sb.append(src + " " + dst + "\\n");
            return;
        }
        hanoi(n - 1, src, aux, dst);
        sb.append(src + " " + dst + "\\n");
        hanoi(n - 1, aux, dst, src);
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        BigInteger moves = BigInteger.valueOf(2).pow(n).subtract(BigInteger.ONE);
        System.out.println(moves);

        if (n <= 20) {
            hanoi(n, 1, 3, 2);
            System.out.print(sb);
        }
    }
}"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <string>
using namespace std;

string multiply(string num, int x) {
    int carry = 0;
    for (int i = num.size() - 1; i >= 0; i--) {
        int prod = (num[i] - '0') * x + carry;
        num[i] = (prod % 10) + '0';
        carry = prod / 10;
    }
    while (carry) {
        num = char(carry % 10 + '0') + num;
        carry /= 10;
    }
    return num;
}

string subtract(string num, int x) {
    int i = num.size() - 1;
    num[i] -= x;
    while (i > 0 && num[i] < '0') {
        num[i] += 10;
        num[i-1]--;
        i--;
    }
    int start = 0;
    while (start < num.size() - 1 && num[start] == '0') start++;
    return num.substr(start);
}

string power2(int n) {
    string result = "1";
    for (int i = 0; i < n; i++) {
        result = multiply(result, 2);
    }
    return result;
}

void hanoi(int n, int src, int dst, int aux) {
    if (n == 1) {
        cout << src << " " << dst << "\\n";
        return;
    }
    hanoi(n - 1, src, aux, dst);
    cout << src << " " << dst << "\\n";
    hanoi(n - 1, aux, dst, src);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    string moves = subtract(power2(n), 1);
    cout << moves << "\\n";

    if (n <= 20) {
        hanoi(n, 1, 3, 2);
    }

    return 0;
}"""
    }
]

# Problem 1915: Largest square in matrix (DP)
solutions['1915'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

n, m = map(int, input().split())
grid = []
for _ in range(n):
    line = input().strip()
    grid.append([int(c) for c in line])

if n == 0 or m == 0:
    print(0)
else:
    dp = [[0] * m for _ in range(n)]
    max_side = 0

    for i in range(n):
        for j in range(m):
            if grid[i][j] == 1:
                if i == 0 or j == 0:
                    dp[i][j] = 1
                else:
                    dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
                max_side = max(max_side, dp[i][j])

    print(max_side * max_side)
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        int[][] grid = new int[n][m];
        for (int i = 0; i < n; i++) {
            String line = br.readLine();
            for (int j = 0; j < m; j++) {
                grid[i][j] = line.charAt(j) - '0';
            }
        }

        int[][] dp = new int[n][m];
        int maxSide = 0;

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (grid[i][j] == 1) {
                    if (i == 0 || j == 0) {
                        dp[i][j] = 1;
                    } else {
                        dp[i][j] = Math.min(Math.min(dp[i-1][j], dp[i][j-1]), dp[i-1][j-1]) + 1;
                    }
                    maxSide = Math.max(maxSide, dp[i][j]);
                }
            }
        }

        System.out.println(maxSide * maxSide);
    }
}"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <algorithm>
#include <string>
using namespace std;

int grid[1001][1001];
int dp[1001][1001];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    for (int i = 0; i < n; i++) {
        string line;
        cin >> line;
        for (int j = 0; j < m; j++) {
            grid[i][j] = line[j] - '0';
        }
    }

    int maxSide = 0;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (grid[i][j] == 1) {
                if (i == 0 || j == 0) {
                    dp[i][j] = 1;
                } else {
                    dp[i][j] = min({dp[i-1][j], dp[i][j-1], dp[i-1][j-1]}) + 1;
                }
                maxSide = max(maxSide, dp[i][j]);
            }
        }
    }

    cout << maxSide * maxSide << endl;

    return 0;
}"""
    }
]

# Problem 1916: Dijkstra's algorithm
solutions['1916'] = [
    {
        "language": "python",
        "code": """import sys
import heapq
input = sys.stdin.readline

N = int(input())
M = int(input())

graph = [[] for _ in range(N + 1)]
for _ in range(M):
    u, v, w = map(int, input().split())
    graph[u].append((v, w))

A, B = map(int, input().split())

# Dijkstra
dist = [float('inf')] * (N + 1)
dist[A] = 0
pq = [(0, A)]

while pq:
    d, u = heapq.heappop(pq)
    if d > dist[u]:
        continue
    for v, w in graph[u]:
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
            heapq.heappush(pq, (dist[v], v))

print(dist[B])
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());
        int M = Integer.parseInt(br.readLine().trim());

        List<List<int[]>> graph = new ArrayList<>();
        for (int i = 0; i <= N; i++) graph.add(new ArrayList<>());

        for (int i = 0; i < M; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int u = Integer.parseInt(st.nextToken());
            int v = Integer.parseInt(st.nextToken());
            int w = Integer.parseInt(st.nextToken());
            graph.get(u).add(new int[]{v, w});
        }

        StringTokenizer st = new StringTokenizer(br.readLine());
        int A = Integer.parseInt(st.nextToken());
        int B = Integer.parseInt(st.nextToken());

        int[] dist = new int[N + 1];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[A] = 0;

        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
        pq.offer(new int[]{0, A});

        while (!pq.isEmpty()) {
            int[] cur = pq.poll();
            int d = cur[0], u = cur[1];
            if (d > dist[u]) continue;
            for (int[] edge : graph.get(u)) {
                int v = edge[0], w = edge[1];
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                    pq.offer(new int[]{dist[v], v});
                }
            }
        }

        System.out.println(dist[B]);
    }
}"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

typedef pair<int, int> pii;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    vector<vector<pii>> graph(N + 1);
    for (int i = 0; i < M; i++) {
        int u, v, w;
        cin >> u >> v >> w;
        graph[u].push_back({v, w});
    }

    int A, B;
    cin >> A >> B;

    vector<int> dist(N + 1, 1e9);
    dist[A] = 0;

    priority_queue<pii, vector<pii>, greater<pii>> pq;
    pq.push({0, A});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;
        for (auto [v, w] : graph[u]) {
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});
            }
        }
    }

    cout << dist[B] << endl;

    return 0;
}"""
    }
]

# Problem 1917: Cube net validation
solutions['1917'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

# All 11 valid cube net patterns (normalized)
def get_normalized(cells):
    min_r = min(c[0] for c in cells)
    min_c = min(c[1] for c in cells)
    normalized = tuple(sorted((r - min_r, c - min_c) for r, c in cells))
    return normalized

# Generate all valid cube nets
valid_nets = set()

# The 11 basic patterns
patterns = [
    [(0,0),(0,1),(0,2),(0,3),(1,1),(2,1)],  # Cross
    [(0,0),(0,1),(0,2),(1,2),(1,3),(2,2)],
    [(0,0),(0,1),(1,1),(1,2),(2,1),(2,2)],
    [(0,0),(1,0),(1,1),(1,2),(1,3),(2,0)],
    [(0,0),(1,0),(1,1),(1,2),(2,1),(2,2)],
    [(0,0),(1,0),(1,1),(1,2),(2,2),(2,3)],
    [(0,0),(1,0),(1,1),(2,1),(2,2),(3,2)],
    [(0,0),(0,1),(1,1),(1,2),(1,3),(2,1)],
    [(0,0),(0,1),(1,1),(1,2),(2,2),(2,3)],
    [(0,1),(1,0),(1,1),(1,2),(2,1),(2,2)],
    [(0,1),(1,0),(1,1),(1,2),(2,0),(2,1)],
]

def rotate90(cells):
    return [(c, -r) for r, c in cells]

def flip(cells):
    return [(-r, c) for r, c in cells]

for pattern in patterns:
    cells = pattern
    for _ in range(4):
        valid_nets.add(get_normalized(cells))
        valid_nets.add(get_normalized(flip(cells)))
        cells = rotate90(cells)

results = []
for _ in range(3):
    grid = []
    for i in range(6):
        row = list(map(int, input().split()))
        grid.append(row)

    cells = []
    for i in range(6):
        for j in range(6):
            if grid[i][j] == 1:
                cells.append((i, j))

    if len(cells) != 6:
        results.append("no")
    else:
        normalized = get_normalized(cells)
        if normalized in valid_nets:
            results.append("yes")
        else:
            results.append("no")

for r in results:
    print(r)
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;
import java.io.*;

public class Main {
    static Set<String> validNets = new HashSet<>();

    static String normalize(int[][] cells) {
        int minR = Integer.MAX_VALUE, minC = Integer.MAX_VALUE;
        for (int[] c : cells) {
            minR = Math.min(minR, c[0]);
            minC = Math.min(minC, c[1]);
        }
        int[][] norm = new int[6][2];
        for (int i = 0; i < 6; i++) {
            norm[i][0] = cells[i][0] - minR;
            norm[i][1] = cells[i][1] - minC;
        }
        Arrays.sort(norm, (a, b) -> a[0] != b[0] ? a[0] - b[0] : a[1] - b[1]);
        StringBuilder sb = new StringBuilder();
        for (int[] c : norm) sb.append(c[0] + "," + c[1] + ";");
        return sb.toString();
    }

    static int[][] rotate90(int[][] cells) {
        int[][] result = new int[6][2];
        for (int i = 0; i < 6; i++) {
            result[i][0] = cells[i][1];
            result[i][1] = -cells[i][0];
        }
        return result;
    }

    static int[][] flip(int[][] cells) {
        int[][] result = new int[6][2];
        for (int i = 0; i < 6; i++) {
            result[i][0] = -cells[i][0];
            result[i][1] = cells[i][1];
        }
        return result;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int[][][] patterns = {
            {{0,0},{0,1},{0,2},{0,3},{1,1},{2,1}},
            {{0,0},{0,1},{0,2},{1,2},{1,3},{2,2}},
            {{0,0},{0,1},{1,1},{1,2},{2,1},{2,2}},
            {{0,0},{1,0},{1,1},{1,2},{1,3},{2,0}},
            {{0,0},{1,0},{1,1},{1,2},{2,1},{2,2}},
            {{0,0},{1,0},{1,1},{1,2},{2,2},{2,3}},
            {{0,0},{1,0},{1,1},{2,1},{2,2},{3,2}},
            {{0,0},{0,1},{1,1},{1,2},{1,3},{2,1}},
            {{0,0},{0,1},{1,1},{1,2},{2,2},{2,3}},
            {{0,1},{1,0},{1,1},{1,2},{2,1},{2,2}},
            {{0,1},{1,0},{1,1},{1,2},{2,0},{2,1}}
        };

        for (int[][] pattern : patterns) {
            int[][] cells = pattern.clone();
            for (int r = 0; r < 4; r++) {
                validNets.add(normalize(cells));
                validNets.add(normalize(flip(cells)));
                cells = rotate90(cells);
            }
        }

        StringBuilder result = new StringBuilder();
        for (int t = 0; t < 3; t++) {
            int[][] grid = new int[6][6];
            List<int[]> cellList = new ArrayList<>();
            for (int i = 0; i < 6; i++) {
                StringTokenizer st = new StringTokenizer(br.readLine());
                for (int j = 0; j < 6; j++) {
                    grid[i][j] = Integer.parseInt(st.nextToken());
                    if (grid[i][j] == 1) cellList.add(new int[]{i, j});
                }
            }

            if (cellList.size() != 6) {
                result.append("no\\n");
            } else {
                int[][] cells = cellList.toArray(new int[6][2]);
                if (validNets.contains(normalize(cells))) {
                    result.append("yes\\n");
                } else {
                    result.append("no\\n");
                }
            }
        }
        System.out.print(result);
    }
}"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <set>
#include <vector>
#include <algorithm>
using namespace std;

set<string> validNets;

string normalize(vector<pair<int,int>> cells) {
    int minR = 1e9, minC = 1e9;
    for (auto& c : cells) {
        minR = min(minR, c.first);
        minC = min(minC, c.second);
    }
    for (auto& c : cells) {
        c.first -= minR;
        c.second -= minC;
    }
    sort(cells.begin(), cells.end());
    string s;
    for (auto& c : cells) {
        s += to_string(c.first) + "," + to_string(c.second) + ";";
    }
    return s;
}

vector<pair<int,int>> rotate90(vector<pair<int,int>> cells) {
    for (auto& c : cells) {
        int r = c.first, col = c.second;
        c.first = col;
        c.second = -r;
    }
    return cells;
}

vector<pair<int,int>> flip(vector<pair<int,int>> cells) {
    for (auto& c : cells) {
        c.first = -c.first;
    }
    return cells;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    vector<vector<pair<int,int>>> patterns = {
        {{0,0},{0,1},{0,2},{0,3},{1,1},{2,1}},
        {{0,0},{0,1},{0,2},{1,2},{1,3},{2,2}},
        {{0,0},{0,1},{1,1},{1,2},{2,1},{2,2}},
        {{0,0},{1,0},{1,1},{1,2},{1,3},{2,0}},
        {{0,0},{1,0},{1,1},{1,2},{2,1},{2,2}},
        {{0,0},{1,0},{1,1},{1,2},{2,2},{2,3}},
        {{0,0},{1,0},{1,1},{2,1},{2,2},{3,2}},
        {{0,0},{0,1},{1,1},{1,2},{1,3},{2,1}},
        {{0,0},{0,1},{1,1},{1,2},{2,2},{2,3}},
        {{0,1},{1,0},{1,1},{1,2},{2,1},{2,2}},
        {{0,1},{1,0},{1,1},{1,2},{2,0},{2,1}}
    };

    for (auto& pattern : patterns) {
        auto cells = pattern;
        for (int r = 0; r < 4; r++) {
            validNets.insert(normalize(cells));
            validNets.insert(normalize(flip(cells)));
            cells = rotate90(cells);
        }
    }

    for (int t = 0; t < 3; t++) {
        vector<pair<int,int>> cells;
        for (int i = 0; i < 6; i++) {
            for (int j = 0; j < 6; j++) {
                int x;
                cin >> x;
                if (x == 1) cells.push_back({i, j});
            }
        }

        if (cells.size() != 6) {
            cout << "no\\n";
        } else if (validNets.count(normalize(cells))) {
            cout << "yes\\n";
        } else {
            cout << "no\\n";
        }
    }

    return 0;
}"""
    }
]

# Problem 1918: Infix to Postfix
solutions['1918'] = [
    {
        "language": "python",
        "code": """import sys

def infix_to_postfix(expr):
    result = []
    stack = []
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

    for c in expr:
        if c.isalpha():
            result.append(c)
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                result.append(stack.pop())
            stack.pop()  # Remove '('
        else:  # operator
            while stack and stack[-1] != '(' and precedence.get(stack[-1], 0) >= precedence[c]:
                result.append(stack.pop())
            stack.append(c)

    while stack:
        result.append(stack.pop())

    return ''.join(result)

expr = input().strip()
print(infix_to_postfix(expr))
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String expr = br.readLine().trim();

        StringBuilder result = new StringBuilder();
        Stack<Character> stack = new Stack<>();

        Map<Character, Integer> precedence = new HashMap<>();
        precedence.put('+', 1);
        precedence.put('-', 1);
        precedence.put('*', 2);
        precedence.put('/', 2);

        for (char c : expr.toCharArray()) {
            if (Character.isLetter(c)) {
                result.append(c);
            } else if (c == '(') {
                stack.push(c);
            } else if (c == ')') {
                while (!stack.isEmpty() && stack.peek() != '(') {
                    result.append(stack.pop());
                }
                stack.pop();
            } else {
                while (!stack.isEmpty() && stack.peek() != '(' &&
                       precedence.getOrDefault(stack.peek(), 0) >= precedence.get(c)) {
                    result.append(stack.pop());
                }
                stack.push(c);
            }
        }

        while (!stack.isEmpty()) {
            result.append(stack.pop());
        }

        System.out.println(result);
    }
}"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <stack>
#include <string>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string expr;
    cin >> expr;

    string result;
    stack<char> st;

    map<char, int> precedence;
    precedence['+'] = 1;
    precedence['-'] = 1;
    precedence['*'] = 2;
    precedence['/'] = 2;

    for (char c : expr) {
        if (isalpha(c)) {
            result += c;
        } else if (c == '(') {
            st.push(c);
        } else if (c == ')') {
            while (!st.empty() && st.top() != '(') {
                result += st.top();
                st.pop();
            }
            st.pop();
        } else {
            while (!st.empty() && st.top() != '(' && precedence[st.top()] >= precedence[c]) {
                result += st.top();
                st.pop();
            }
            st.push(c);
        }
    }

    while (!st.empty()) {
        result += st.top();
        st.pop();
    }

    cout << result << endl;

    return 0;
}"""
    }
]

# Problem 1919: Anagram difference
solutions['1919'] = [
    {
        "language": "python",
        "code": """s1 = input().strip()
s2 = input().strip()

cnt1 = [0] * 26
cnt2 = [0] * 26

for c in s1:
    cnt1[ord(c) - ord('a')] += 1
for c in s2:
    cnt2[ord(c) - ord('a')] += 1

diff = 0
for i in range(26):
    diff += abs(cnt1[i] - cnt2[i])

print(diff)
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s1 = br.readLine().trim();
        String s2 = br.readLine().trim();

        int[] cnt1 = new int[26];
        int[] cnt2 = new int[26];

        for (char c : s1.toCharArray()) {
            cnt1[c - 'a']++;
        }
        for (char c : s2.toCharArray()) {
            cnt2[c - 'a']++;
        }

        int diff = 0;
        for (int i = 0; i < 26; i++) {
            diff += Math.abs(cnt1[i] - cnt2[i]);
        }

        System.out.println(diff);
    }
}"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <string>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s1, s2;
    cin >> s1 >> s2;

    int cnt1[26] = {0};
    int cnt2[26] = {0};

    for (char c : s1) {
        cnt1[c - 'a']++;
    }
    for (char c : s2) {
        cnt2[c - 'a']++;
    }

    int diff = 0;
    for (int i = 0; i < 26; i++) {
        diff += abs(cnt1[i] - cnt2[i]);
    }

    cout << diff << endl;

    return 0;
}"""
    }
]

# Apply solutions to data
for oid, sol_list in solutions.items():
    if oid in id_to_idx:
        data[id_to_idx[oid]]['solutions'] = sol_list
        print(f"Applied solutions for problem {oid}")

# Save the updated data
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved checkpoint file with problems 1910-1919 solved")
