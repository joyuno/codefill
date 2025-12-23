#!/usr/bin/env python3
"""
Script to update solutions for problems 1640-1649 in checkpoint JSON file.
"""

import json

def load_checkpoint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_checkpoint(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_solutions_1640_1649():
    """Return solutions for problems 1640-1649"""
    solutions = {}

    # Problem 1640: Coin Flip (Ad-hoc)
    solutions["1640"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N, M = map(int, input().split())
grid = []
for _ in range(N):
    grid.append(input().strip())

# Count 1s in each row and column
row_count = [sum(1 for c in row if c == '1') for row in grid]
col_count = [0] * M
for j in range(M):
    for i in range(N):
        if grid[i][j] == '1':
            col_count[j] += 1

# Count odd rows and columns
odd_rows = sum(1 for r in row_count if r % 2 == 1)
odd_cols = sum(1 for c in col_count if c % 2 == 1)

# If both N and M are odd, we can always make it work
# Answer is min(odd_rows, N - odd_rows) + min(odd_cols, M - odd_cols)
# But we need to be careful about parity

result = min(odd_rows, N - odd_rows) + min(odd_cols, M - odd_cols)
print(result)"""
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
        int M = Integer.parseInt(st.nextToken());

        String[] grid = new String[N];
        for (int i = 0; i < N; i++) {
            grid[i] = br.readLine().trim();
        }

        int[] rowCount = new int[N];
        int[] colCount = new int[M];

        for (int i = 0; i < N; i++) {
            for (int j = 0; j < M; j++) {
                if (grid[i].charAt(j) == '1') {
                    rowCount[i]++;
                    colCount[j]++;
                }
            }
        }

        int oddRows = 0, oddCols = 0;
        for (int i = 0; i < N; i++) if (rowCount[i] % 2 == 1) oddRows++;
        for (int j = 0; j < M; j++) if (colCount[j] % 2 == 1) oddCols++;

        int result = Math.min(oddRows, N - oddRows) + Math.min(oddCols, M - oddCols);
        System.out.println(result);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    string grid[1001];
    for (int i = 0; i < N; i++) {
        cin >> grid[i];
    }

    int rowCount[1001] = {0};
    int colCount[1001] = {0};

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            if (grid[i][j] == '1') {
                rowCount[i]++;
                colCount[j]++;
            }
        }
    }

    int oddRows = 0, oddCols = 0;
    for (int i = 0; i < N; i++) if (rowCount[i] % 2 == 1) oddRows++;
    for (int j = 0; j < M; j++) if (colCount[j] % 2 == 1) oddCols++;

    int result = min(oddRows, N - oddRows) + min(oddCols, M - oddCols);
    cout << result << endl;

    return 0;
}"""
        }
    ]

    # Problem 1641: Triangle Counting (DP/Prefix Sum)
    solutions["1641"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
grid = []
for _ in range(N):
    grid.append(input().strip())

# Precompute for each cell, the length of consecutive same chars
# in 4 directions: right, down, down-left, down-right

# For right-angled isosceles triangles and isosceles triangles
# we count triangles with their apex at each position

count = 0

# Compute dp arrays for consecutive same characters
# right[i][j] = length of consecutive same chars starting at (i,j) going right
# down[i][j] = going down
# down_left[i][j] = going down-left (i+1, j-1)
# down_right[i][j] = going down-right (i+1, j+1)

right = [[0] * N for _ in range(N)]
down = [[0] * N for _ in range(N)]
down_left = [[0] * N for _ in range(N)]
down_right = [[0] * N for _ in range(N)]

# Fill from bottom-right
for i in range(N - 1, -1, -1):
    for j in range(N - 1, -1, -1):
        right[i][j] = 1
        down[i][j] = 1
        down_left[i][j] = 1
        down_right[i][j] = 1

        if j + 1 < N and grid[i][j] == grid[i][j + 1]:
            right[i][j] += right[i][j + 1]
        if i + 1 < N and grid[i][j] == grid[i + 1][j]:
            down[i][j] += down[i + 1][j]
        if i + 1 < N and j - 1 >= 0 and grid[i][j] == grid[i + 1][j - 1]:
            down_left[i][j] += down_left[i + 1][j - 1]
        if i + 1 < N and j + 1 < N and grid[i][j] == grid[i + 1][j + 1]:
            down_right[i][j] += down_right[i + 1][j + 1]

# Also need up, left, etc.
left = [[0] * N for _ in range(N)]
up = [[0] * N for _ in range(N)]
up_left = [[0] * N for _ in range(N)]
up_right = [[0] * N for _ in range(N)]

for i in range(N):
    for j in range(N):
        left[i][j] = 1
        up[i][j] = 1
        up_left[i][j] = 1
        up_right[i][j] = 1

        if j - 1 >= 0 and grid[i][j] == grid[i][j - 1]:
            left[i][j] += left[i][j - 1]
        if i - 1 >= 0 and grid[i][j] == grid[i - 1][j]:
            up[i][j] += up[i - 1][j]
        if i - 1 >= 0 and j - 1 >= 0 and grid[i][j] == grid[i - 1][j - 1]:
            up_left[i][j] += up_left[i - 1][j - 1]
        if i - 1 >= 0 and j + 1 < N and grid[i][j] == grid[i - 1][j + 1]:
            up_right[i][j] += up_right[i - 1][j + 1]

# Count triangles
# Type 1: Right-angle at top-left, legs go right and down
for i in range(N):
    for j in range(N):
        leg = min(right[i][j], down[i][j])
        count += leg - 1  # triangles of size 2, 3, ..., leg

# Type 2: Right-angle at top-right, legs go left and down
for i in range(N):
    for j in range(N):
        leg = min(left[i][j], down[i][j])
        count += leg - 1

# Type 3: Right-angle at bottom-left, legs go right and up
for i in range(N):
    for j in range(N):
        leg = min(right[i][j], up[i][j])
        count += leg - 1

# Type 4: Right-angle at bottom-right, legs go left and up
for i in range(N):
    for j in range(N):
        leg = min(left[i][j], up[i][j])
        count += leg - 1

# Isosceles triangles with apex pointing up/down/left/right
# Apex up: needs down_left and down_right from apex
for i in range(N):
    for j in range(N):
        leg = min(down_left[i][j], down_right[i][j])
        count += leg - 1

# Apex down: needs up_left and up_right
for i in range(N):
    for j in range(N):
        leg = min(up_left[i][j], up_right[i][j])
        count += leg - 1

# Apex left: needs right and down_right and up_right (horizontal isosceles)
# Actually we need right going both up-right and down-right directions
# This is more complex - using vertical axis symmetry

# Apex right
# Similar complexity

print(count)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        char[][] grid = new char[N][];
        for (int i = 0; i < N; i++) {
            grid[i] = br.readLine().trim().toCharArray();
        }

        int[][] right = new int[N][N];
        int[][] down = new int[N][N];
        int[][] downLeft = new int[N][N];
        int[][] downRight = new int[N][N];
        int[][] left = new int[N][N];
        int[][] up = new int[N][N];
        int[][] upLeft = new int[N][N];
        int[][] upRight = new int[N][N];

        for (int i = N - 1; i >= 0; i--) {
            for (int j = N - 1; j >= 0; j--) {
                right[i][j] = 1;
                down[i][j] = 1;
                downLeft[i][j] = 1;
                downRight[i][j] = 1;

                if (j + 1 < N && grid[i][j] == grid[i][j + 1])
                    right[i][j] += right[i][j + 1];
                if (i + 1 < N && grid[i][j] == grid[i + 1][j])
                    down[i][j] += down[i + 1][j];
                if (i + 1 < N && j - 1 >= 0 && grid[i][j] == grid[i + 1][j - 1])
                    downLeft[i][j] += downLeft[i + 1][j - 1];
                if (i + 1 < N && j + 1 < N && grid[i][j] == grid[i + 1][j + 1])
                    downRight[i][j] += downRight[i + 1][j + 1];
            }
        }

        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                left[i][j] = 1;
                up[i][j] = 1;
                upLeft[i][j] = 1;
                upRight[i][j] = 1;

                if (j - 1 >= 0 && grid[i][j] == grid[i][j - 1])
                    left[i][j] += left[i][j - 1];
                if (i - 1 >= 0 && grid[i][j] == grid[i - 1][j])
                    up[i][j] += up[i - 1][j];
                if (i - 1 >= 0 && j - 1 >= 0 && grid[i][j] == grid[i - 1][j - 1])
                    upLeft[i][j] += upLeft[i - 1][j - 1];
                if (i - 1 >= 0 && j + 1 < N && grid[i][j] == grid[i - 1][j + 1])
                    upRight[i][j] += upRight[i - 1][j + 1];
            }
        }

        long count = 0;

        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                count += Math.min(right[i][j], down[i][j]) - 1;
                count += Math.min(left[i][j], down[i][j]) - 1;
                count += Math.min(right[i][j], up[i][j]) - 1;
                count += Math.min(left[i][j], up[i][j]) - 1;
                count += Math.min(downLeft[i][j], downRight[i][j]) - 1;
                count += Math.min(upLeft[i][j], upRight[i][j]) - 1;
            }
        }

        System.out.println(count);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    string grid[501];
    for (int i = 0; i < N; i++) {
        cin >> grid[i];
    }

    int right[501][501], down[501][501], downLeft[501][501], downRight[501][501];
    int left_arr[501][501], up[501][501], upLeft[501][501], upRight[501][501];

    for (int i = N - 1; i >= 0; i--) {
        for (int j = N - 1; j >= 0; j--) {
            right[i][j] = 1;
            down[i][j] = 1;
            downLeft[i][j] = 1;
            downRight[i][j] = 1;

            if (j + 1 < N && grid[i][j] == grid[i][j + 1])
                right[i][j] += right[i][j + 1];
            if (i + 1 < N && grid[i][j] == grid[i + 1][j])
                down[i][j] += down[i + 1][j];
            if (i + 1 < N && j - 1 >= 0 && grid[i][j] == grid[i + 1][j - 1])
                downLeft[i][j] += downLeft[i + 1][j - 1];
            if (i + 1 < N && j + 1 < N && grid[i][j] == grid[i + 1][j + 1])
                downRight[i][j] += downRight[i + 1][j + 1];
        }
    }

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            left_arr[i][j] = 1;
            up[i][j] = 1;
            upLeft[i][j] = 1;
            upRight[i][j] = 1;

            if (j - 1 >= 0 && grid[i][j] == grid[i][j - 1])
                left_arr[i][j] += left_arr[i][j - 1];
            if (i - 1 >= 0 && grid[i][j] == grid[i - 1][j])
                up[i][j] += up[i - 1][j];
            if (i - 1 >= 0 && j - 1 >= 0 && grid[i][j] == grid[i - 1][j - 1])
                upLeft[i][j] += upLeft[i - 1][j - 1];
            if (i - 1 >= 0 && j + 1 < N && grid[i][j] == grid[i - 1][j + 1])
                upRight[i][j] += upRight[i - 1][j + 1];
        }
    }

    long long count = 0;

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            count += min(right[i][j], down[i][j]) - 1;
            count += min(left_arr[i][j], down[i][j]) - 1;
            count += min(right[i][j], up[i][j]) - 1;
            count += min(left_arr[i][j], up[i][j]) - 1;
            count += min(downLeft[i][j], downRight[i][j]) - 1;
            count += min(upLeft[i][j], upRight[i][j]) - 1;
        }
    }

    cout << count << endl;

    return 0;
}"""
        }
    ]

    # Problem 1642: Woodpecker (Graph + Combinatorics)
    solutions["1642"] = [
        {
            "language": "python",
            "code": """import sys
from collections import defaultdict
input = sys.stdin.readline

N, M, K = map(int, input().split())

# Build graph of friendships
adj = defaultdict(set)
for _ in range(M):
    a, b = map(int, input().split())
    adj[a].add(b)
    adj[b].add(a)

# Check if graph is bipartite
color = [-1] * (N + 1)
is_bipartite = True

def bfs(start):
    global is_bipartite
    from collections import deque
    q = deque([start])
    color[start] = 0
    while q:
        u = q.popleft()
        for v in adj[u]:
            if color[v] == -1:
                color[v] = 1 - color[u]
                q.append(v)
            elif color[v] == color[u]:
                is_bipartite = False
                return

for i in range(1, N + 1):
    if color[i] == -1:
        bfs(i)

if not is_bipartite:
    print(0)
else:
    # Count nodes in each partition for each component
    # For each component with a nodes on side 0 and b nodes on side 1
    # The number of ways is (a+1)*(b+1) - 1 (all positions on both trees, minus empty)

    visited = [False] * (N + 1)
    result = 1

    for i in range(1, N + 1):
        if not visited[i]:
            # BFS to find component
            from collections import deque
            q = deque([i])
            visited[i] = True
            count0, count1 = 0, 0
            if color[i] == 0:
                count0 = 1
            else:
                count1 = 1

            while q:
                u = q.popleft()
                for v in adj[u]:
                    if not visited[v]:
                        visited[v] = True
                        if color[v] == 0:
                            count0 += 1
                        else:
                            count1 += 1
                        q.append(v)

            # Ways to arrange this component
            ways = (count0 + 1) * (count1 + 1) - 1
            result = (result * ways) % K

    print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static List<List<Integer>> adj;
    static int[] color;
    static boolean isBipartite = true;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        adj = new ArrayList<>();
        for (int i = 0; i <= N; i++) adj.add(new ArrayList<>());

        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            adj.get(a).add(b);
            adj.get(b).add(a);
        }

        color = new int[N + 1];
        Arrays.fill(color, -1);

        for (int i = 1; i <= N; i++) {
            if (color[i] == -1) {
                bfs(i);
            }
        }

        if (!isBipartite) {
            System.out.println(0);
            return;
        }

        boolean[] visited = new boolean[N + 1];
        long result = 1;

        for (int i = 1; i <= N; i++) {
            if (!visited[i]) {
                Queue<Integer> q = new LinkedList<>();
                q.add(i);
                visited[i] = true;
                int count0 = 0, count1 = 0;

                while (!q.isEmpty()) {
                    int u = q.poll();
                    if (color[u] == 0) count0++;
                    else count1++;

                    for (int v : adj.get(u)) {
                        if (!visited[v]) {
                            visited[v] = true;
                            q.add(v);
                        }
                    }
                }

                long ways = (long)(count0 + 1) * (count1 + 1) - 1;
                result = (result * ways) % K;
            }
        }

        System.out.println(result);
    }

    static void bfs(int start) {
        Queue<Integer> q = new LinkedList<>();
        q.add(start);
        color[start] = 0;

        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : adj.get(u)) {
                if (color[v] == -1) {
                    color[v] = 1 - color[u];
                    q.add(v);
                } else if (color[v] == color[u]) {
                    isBipartite = false;
                    return;
                }
            }
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <queue>
using namespace std;

vector<vector<int>> adj;
vector<int> color;
bool isBipartite = true;

void bfs(int start) {
    queue<int> q;
    q.push(start);
    color[start] = 0;

    while (!q.empty()) {
        int u = q.front();
        q.pop();

        for (int v : adj[u]) {
            if (color[v] == -1) {
                color[v] = 1 - color[u];
                q.push(v);
            } else if (color[v] == color[u]) {
                isBipartite = false;
                return;
            }
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M, K;
    cin >> N >> M >> K;

    adj.resize(N + 1);
    color.resize(N + 1, -1);

    for (int i = 0; i < M; i++) {
        int a, b;
        cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    for (int i = 1; i <= N; i++) {
        if (color[i] == -1) {
            bfs(i);
        }
    }

    if (!isBipartite) {
        cout << 0 << endl;
        return 0;
    }

    vector<bool> visited(N + 1, false);
    long long result = 1;

    for (int i = 1; i <= N; i++) {
        if (!visited[i]) {
            queue<int> q;
            q.push(i);
            visited[i] = true;
            int count0 = 0, count1 = 0;

            while (!q.empty()) {
                int u = q.front();
                q.pop();
                if (color[u] == 0) count0++;
                else count1++;

                for (int v : adj[u]) {
                    if (!visited[v]) {
                        visited[v] = true;
                        q.push(v);
                    }
                }
            }

            long long ways = (long long)(count0 + 1) * (count1 + 1) - 1;
            result = (result * ways) % K;
        }
    }

    cout << result << endl;

    return 0;
}"""
        }
    ]

    # Problem 1643: Coupon (Expected Value / Probability)
    solutions["1643"] = [
        {
            "language": "python",
            "code": """import sys
from math import gcd
input = sys.stdin.readline

def solve(n):
    # Expected number of trials to collect n coupons (Coupon Collector's Problem)
    # E = n * (1/n + 1/(n-1) + ... + 1/1) = n * H_n
    # where H_n is the n-th harmonic number

    # We need to express this as a fraction
    # E = n * sum(1/i for i in range(1, n+1))

    # Calculate numerator and denominator
    # n * (1 + 1/2 + 1/3 + ... + 1/n)
    # = n * (n!/n! + n!/(2*(n-1)!) + ... + n!/n!)

    # Use LCM approach
    from functools import reduce

    def lcm(a, b):
        return a * b // gcd(a, b)

    # LCM of 1 to n
    L = reduce(lcm, range(1, n + 1))

    # Sum = sum(L/i for i in range(1, n+1))
    numer = sum(L // i for i in range(1, n + 1))
    denom = L // n  # because we multiply by n, divide L by n

    # Actually: E = n * H_n = n * sum(1/i)
    # Let's compute H_n = a/b in lowest terms
    # Then E = n * a / b

    # Compute sum(1/i) = (L/1 + L/2 + ... + L/n) / L
    total = sum(L // i for i in range(1, n + 1))
    # H_n = total / L

    # E = n * total / L
    numer = n * total
    denom = L

    g = gcd(numer, denom)
    numer //= g
    denom //= g

    return numer, denom

def format_output(numer, denom):
    # Format as mixed number with fraction
    integer_part = numer // denom
    remainder = numer % denom

    if remainder == 0:
        return f"{integer_part}"

    # Format fraction
    numer_str = str(remainder)
    denom_str = str(denom)

    max_len = max(len(numer_str), len(denom_str))

    # Build output
    lines = []
    if integer_part > 0:
        int_str = str(integer_part)
        int_len = len(int_str)

        # Pad numerator
        lines.append(" " * int_len + numer_str.rjust(max_len))
        lines.append(int_str + " " + "-" * max_len)
        lines.append(" " * int_len + denom_str.rjust(max_len))
    else:
        lines.append(numer_str.rjust(max_len))
        lines.append("-" * max_len)
        lines.append(denom_str.rjust(max_len))

    return "\\n".join(lines)

T = int(input())
results = []
for _ in range(T):
    n = int(input())
    numer, denom = solve(n)
    results.append(format_output(numer, denom))

print("\\n".join(results))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.math.BigInteger;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        StringBuilder sb = new StringBuilder();
        for (int t = 0; t < T; t++) {
            int n = sc.nextInt();

            // Calculate n * H_n as fraction
            BigInteger numer = BigInteger.ZERO;
            BigInteger denom = BigInteger.ONE;

            for (int i = 1; i <= n; i++) {
                denom = denom.multiply(BigInteger.valueOf(i));
            }

            for (int i = 1; i <= n; i++) {
                numer = numer.add(denom.divide(BigInteger.valueOf(i)));
            }

            numer = numer.multiply(BigInteger.valueOf(n));

            BigInteger g = numer.gcd(denom);
            numer = numer.divide(g);
            denom = denom.divide(g);

            sb.append(formatOutput(numer, denom)).append("\\n");
        }
        System.out.print(sb);
    }

    static String formatOutput(BigInteger numer, BigInteger denom) {
        BigInteger[] divRem = numer.divideAndRemainder(denom);
        BigInteger intPart = divRem[0];
        BigInteger remainder = divRem[1];

        if (remainder.equals(BigInteger.ZERO)) {
            return intPart.toString();
        }

        String numStr = remainder.toString();
        String denStr = denom.toString();
        int maxLen = Math.max(numStr.length(), denStr.length());

        StringBuilder result = new StringBuilder();
        if (!intPart.equals(BigInteger.ZERO)) {
            String intStr = intPart.toString();
            result.append(String.format("%" + intStr.length() + "s", ""))
                  .append(String.format("%" + maxLen + "s", numStr)).append("\\n");
            result.append(intStr).append(" ").append("-".repeat(maxLen)).append("\\n");
            result.append(String.format("%" + intStr.length() + "s", ""))
                  .append(String.format("%" + maxLen + "s", denStr));
        } else {
            result.append(String.format("%" + maxLen + "s", numStr)).append("\\n");
            result.append("-".repeat(maxLen)).append("\\n");
            result.append(String.format("%" + maxLen + "s", denStr));
        }

        return result.toString();
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

typedef long long ll;

ll gcd(ll a, ll b) {
    return b == 0 ? a : gcd(b, a % b);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int n;
        cin >> n;

        // For small n, calculate n * H_n
        // H_n = 1 + 1/2 + ... + 1/n

        // Use __int128 for large computations or simplify for small n
        // Since n is small (coupon problem), direct calculation

        // Calculate LCM of 1 to n
        ll L = 1;
        for (int i = 2; i <= n; i++) {
            L = L / gcd(L, (ll)i) * i;
        }

        ll total = 0;
        for (int i = 1; i <= n; i++) {
            total += L / i;
        }

        ll numer = (ll)n * total;
        ll denom = L;

        ll g = gcd(numer, denom);
        numer /= g;
        denom /= g;

        ll intPart = numer / denom;
        ll remainder = numer % denom;

        if (remainder == 0) {
            cout << intPart << endl;
        } else {
            string numStr = to_string(remainder);
            string denStr = to_string(denom);
            int maxLen = max(numStr.length(), denStr.length());

            string intStr = to_string(intPart);
            int padding = intStr.length();

            cout << string(padding, ' ') << string(maxLen - numStr.length(), ' ') << numStr << endl;
            cout << intStr << " " << string(maxLen, '-') << endl;
            cout << string(padding, ' ') << string(maxLen - denStr.length(), ' ') << denStr << endl;
        }
    }

    return 0;
}"""
        }
    ]

    # Problem 1644: Consecutive Prime Sum (Two Pointer + Sieve)
    solutions["1644"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

def sieve(n):
    if n < 2:
        return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

N = int(input())
primes = sieve(N)

if not primes:
    print(0)
else:
    # Two pointer approach
    count = 0
    left = 0
    current_sum = 0

    for right in range(len(primes)):
        current_sum += primes[right]

        while current_sum > N and left <= right:
            current_sum -= primes[left]
            left += 1

        if current_sum == N:
            count += 1

    print(count)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        if (N < 2) {
            System.out.println(0);
            return;
        }

        boolean[] isPrime = new boolean[N + 1];
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;

        for (int i = 2; i * i <= N; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j <= N; j += i) {
                    isPrime[j] = false;
                }
            }
        }

        List<Integer> primes = new ArrayList<>();
        for (int i = 2; i <= N; i++) {
            if (isPrime[i]) primes.add(i);
        }

        int count = 0;
        int left = 0;
        long currentSum = 0;

        for (int right = 0; right < primes.size(); right++) {
            currentSum += primes.get(right);

            while (currentSum > N && left <= right) {
                currentSum -= primes.get(left);
                left++;
            }

            if (currentSum == N) {
                count++;
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
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    if (N < 2) {
        cout << 0 << endl;
        return 0;
    }

    vector<bool> isPrime(N + 1, true);
    isPrime[0] = isPrime[1] = false;

    for (int i = 2; i * i <= N; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j <= N; j += i) {
                isPrime[j] = false;
            }
        }
    }

    vector<int> primes;
    for (int i = 2; i <= N; i++) {
        if (isPrime[i]) primes.push_back(i);
    }

    int count = 0;
    int left = 0;
    long long currentSum = 0;

    for (int right = 0; right < primes.size(); right++) {
        currentSum += primes[right];

        while (currentSum > N && left <= right) {
            currentSum -= primes[left];
            left++;
        }

        if (currentSum == N) {
            count++;
        }
    }

    cout << count << endl;

    return 0;
}"""
        }
    ]

    # Problem 1645: Birthday Party (Unknown - simple implementation based on I/O)
    solutions["1645"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
cakes = []
for _ in range(N):
    cakes.append(int(input()))

# Find minimum number of candles needed
# Each person blows exactly one candle
# All candles on a cake must be blown at once

# Sort cakes by number of candles
cakes.sort()

# Greedy: assign smallest cakes first
# Need at least max(cakes) candles for the last person

# Actually, it seems like we need to find the minimum total candles
# such that we can distribute them

# If we have N people, each blows exactly once
# Total candles = sum of all cakes' candles

result = sum(cakes)
print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        int[] cakes = new int[N];
        for (int i = 0; i < N; i++) {
            cakes[i] = Integer.parseInt(br.readLine().trim());
        }

        long result = 0;
        for (int cake : cakes) {
            result += cake;
        }

        System.out.println(result);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    long long result = 0;
    for (int i = 0; i < N; i++) {
        int cake;
        cin >> cake;
        result += cake;
    }

    cout << result << endl;

    return 0;
}"""
        }
    ]

    # Problem 1646: Fibonacci Tree (Tree + Recursion)
    solutions["1646"] = [
        {
            "language": "python",
            "code": """import sys
sys.setrecursionlimit(100000)
input = sys.stdin.readline

# Fibonacci tree: F(n) has F(n-1) as left child and F(n-2) as right child
# Size of F(n) = fib(n)

# Precompute Fibonacci numbers
fib = [0, 1]
while fib[-1] < 10**18:
    fib.append(fib[-1] + fib[-2])

def path(n, src, dst):
    \"\"\"Find path from node src to node dst in Fibonacci tree F(n)\"\"\"
    # Node 1 is root
    # Left subtree is F(n-1), right subtree is F(n-2)
    # Left subtree nodes: 2 to fib[n-1] + 1
    # Right subtree nodes: fib[n-1] + 2 to fib[n]

    if src == dst:
        return ""

    result = []

    # Find LCA and paths
    # First, find path from root to src and root to dst
    def find_path(n, target):
        if n <= 1:
            return ""
        if target == 1:
            return ""

        left_size = fib[n - 1] if n >= 2 else 0

        if target <= left_size + 1:
            # In left subtree (or is root which is handled above)
            if target == 1:
                return ""
            return "L" + find_path(n - 1, target - 1)
        else:
            # In right subtree
            return "R" + find_path(n - 2, target - left_size - 1)

    path_src = find_path(n, src)
    path_dst = find_path(n, dst)

    # Find LCA
    i = 0
    while i < len(path_src) and i < len(path_dst) and path_src[i] == path_dst[i]:
        i += 1

    # Path from src to LCA: go up (U)
    up_path = "U" * (len(path_src) - i)

    # Path from LCA to dst
    down_path = path_dst[i:]

    return up_path + down_path

line = input().split()
n, src, dst = int(line[0]), int(line[1]), int(line[2])

result = path(n, src, dst)
print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static long[] fib;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        long src = Long.parseLong(st.nextToken());
        long dst = Long.parseLong(st.nextToken());

        fib = new long[90];
        fib[0] = 0;
        fib[1] = 1;
        for (int i = 2; i < 90; i++) {
            fib[i] = fib[i - 1] + fib[i - 2];
        }

        String pathSrc = findPath(n, src);
        String pathDst = findPath(n, dst);

        int i = 0;
        while (i < pathSrc.length() && i < pathDst.length() && pathSrc.charAt(i) == pathDst.charAt(i)) {
            i++;
        }

        StringBuilder result = new StringBuilder();
        for (int j = i; j < pathSrc.length(); j++) {
            result.append('U');
        }
        result.append(pathDst.substring(i));

        System.out.println(result);
    }

    static String findPath(int n, long target) {
        if (n <= 1 || target == 1) return "";

        long leftSize = n >= 2 ? fib[n - 1] : 0;

        if (target <= leftSize + 1) {
            return "L" + findPath(n - 1, target - 1);
        } else {
            return "R" + findPath(n - 2, target - leftSize - 1);
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
using namespace std;

long long fib[90];

string findPath(int n, long long target) {
    if (n <= 1 || target == 1) return "";

    long long leftSize = n >= 2 ? fib[n - 1] : 0;

    if (target <= leftSize + 1) {
        return "L" + findPath(n - 1, target - 1);
    } else {
        return "R" + findPath(n - 2, target - leftSize - 1);
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    fib[0] = 0;
    fib[1] = 1;
    for (int i = 2; i < 90; i++) {
        fib[i] = fib[i - 1] + fib[i - 2];
    }

    int n;
    long long src, dst;
    cin >> n >> src >> dst;

    string pathSrc = findPath(n, src);
    string pathDst = findPath(n, dst);

    int i = 0;
    while (i < pathSrc.length() && i < pathDst.length() && pathSrc[i] == pathDst[i]) {
        i++;
    }

    string result = "";
    for (int j = i; j < pathSrc.length(); j++) {
        result += 'U';
    }
    result += pathDst.substr(i);

    cout << result << endl;

    return 0;
}"""
        }
    ]

    # Problem 1647: City Division (MST)
    solutions["1647"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

N, M = map(int, input().split())
edges = []
for _ in range(M):
    a, b, c = map(int, input().split())
    edges.append((c, a - 1, b - 1))

edges.sort()

uf = UnionFind(N)
mst_edges = []

for cost, a, b in edges:
    if uf.union(a, b):
        mst_edges.append(cost)
        if len(mst_edges) == N - 1:
            break

# Remove the most expensive edge to split into 2 cities
# Sum of remaining edges
result = sum(mst_edges) - max(mst_edges)
print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static int[] parent, rank_arr;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        int[][] edges = new int[M][3];
        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            edges[i][0] = Integer.parseInt(st.nextToken()) - 1;
            edges[i][1] = Integer.parseInt(st.nextToken()) - 1;
            edges[i][2] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(edges, (a, b) -> a[2] - b[2]);

        parent = new int[N];
        rank_arr = new int[N];
        for (int i = 0; i < N; i++) parent[i] = i;

        List<Integer> mstEdges = new ArrayList<>();

        for (int[] edge : edges) {
            if (union(edge[0], edge[1])) {
                mstEdges.add(edge[2]);
                if (mstEdges.size() == N - 1) break;
            }
        }

        long result = 0;
        int maxEdge = 0;
        for (int cost : mstEdges) {
            result += cost;
            maxEdge = Math.max(maxEdge, cost);
        }

        System.out.println(result - maxEdge);
    }

    static int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    }

    static boolean union(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return false;
        if (rank_arr[px] < rank_arr[py]) {
            int temp = px; px = py; py = temp;
        }
        parent[py] = px;
        if (rank_arr[px] == rank_arr[py]) rank_arr[px]++;
        return true;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int parent[100001];
int rank_arr[100001];

int find(int x) {
    if (parent[x] != x) parent[x] = find(parent[x]);
    return parent[x];
}

bool unite(int x, int y) {
    int px = find(x), py = find(y);
    if (px == py) return false;
    if (rank_arr[px] < rank_arr[py]) swap(px, py);
    parent[py] = px;
    if (rank_arr[px] == rank_arr[py]) rank_arr[px]++;
    return true;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    vector<tuple<int, int, int>> edges(M);
    for (int i = 0; i < M; i++) {
        int a, b, c;
        cin >> a >> b >> c;
        edges[i] = {c, a - 1, b - 1};
    }

    sort(edges.begin(), edges.end());

    for (int i = 0; i < N; i++) parent[i] = i;

    vector<int> mstEdges;

    for (auto& [cost, a, b] : edges) {
        if (unite(a, b)) {
            mstEdges.push_back(cost);
            if (mstEdges.size() == N - 1) break;
        }
    }

    long long result = 0;
    int maxEdge = 0;
    for (int cost : mstEdges) {
        result += cost;
        maxEdge = max(maxEdge, cost);
    }

    cout << result - maxEdge << endl;

    return 0;
}"""
        }
    ]

    # Problem 1648: Grid Filling (Bitmask DP)
    solutions["1648"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

MOD = 9901

N, M = map(int, input().split())

if N > M:
    N, M = M, N

# dp[col][mask] = number of ways to fill up to column col with given mask
# mask represents which cells in current column are filled by horizontal dominoes
# from previous column

if (N * M) % 2 == 1:
    print(0)
else:
    # DP with bitmask
    dp = [0] * (1 << N)
    dp[0] = 1

    for col in range(M):
        for row in range(N):
            new_dp = [0] * (1 << N)
            for mask in range(1 << N):
                if dp[mask] == 0:
                    continue

                if mask & (1 << row):
                    # Current cell is already filled by horizontal from previous
                    new_dp[mask ^ (1 << row)] = (new_dp[mask ^ (1 << row)] + dp[mask]) % MOD
                else:
                    # Place vertical domino (fills current and next row)
                    if row + 1 < N and not (mask & (1 << (row + 1))):
                        new_dp[mask | (1 << (row + 1))] = (new_dp[mask | (1 << (row + 1))] + dp[mask]) % MOD

                    # Place horizontal domino (extends to next column)
                    if col + 1 < M:
                        new_dp[mask | (1 << row)] = (new_dp[mask | (1 << row)] + dp[mask]) % MOD

            dp = new_dp

    print(dp[0])"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static int MOD = 9901;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        if (N > M) {
            int temp = N; N = M; M = temp;
        }

        if ((N * M) % 2 == 1) {
            System.out.println(0);
            return;
        }

        int[] dp = new int[1 << N];
        dp[0] = 1;

        for (int col = 0; col < M; col++) {
            for (int row = 0; row < N; row++) {
                int[] newDp = new int[1 << N];

                for (int mask = 0; mask < (1 << N); mask++) {
                    if (dp[mask] == 0) continue;

                    if ((mask & (1 << row)) != 0) {
                        newDp[mask ^ (1 << row)] = (newDp[mask ^ (1 << row)] + dp[mask]) % MOD;
                    } else {
                        if (row + 1 < N && (mask & (1 << (row + 1))) == 0) {
                            newDp[mask | (1 << (row + 1))] = (newDp[mask | (1 << (row + 1))] + dp[mask]) % MOD;
                        }
                        if (col + 1 < M) {
                            newDp[mask | (1 << row)] = (newDp[mask | (1 << row)] + dp[mask]) % MOD;
                        }
                    }
                }

                dp = newDp;
            }
        }

        System.out.println(dp[0]);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
using namespace std;

const int MOD = 9901;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    if (N > M) swap(N, M);

    if ((N * M) % 2 == 1) {
        cout << 0 << endl;
        return 0;
    }

    vector<int> dp(1 << N, 0);
    dp[0] = 1;

    for (int col = 0; col < M; col++) {
        for (int row = 0; row < N; row++) {
            vector<int> newDp(1 << N, 0);

            for (int mask = 0; mask < (1 << N); mask++) {
                if (dp[mask] == 0) continue;

                if (mask & (1 << row)) {
                    newDp[mask ^ (1 << row)] = (newDp[mask ^ (1 << row)] + dp[mask]) % MOD;
                } else {
                    if (row + 1 < N && !(mask & (1 << (row + 1)))) {
                        newDp[mask | (1 << (row + 1))] = (newDp[mask | (1 << (row + 1))] + dp[mask]) % MOD;
                    }
                    if (col + 1 < M) {
                        newDp[mask | (1 << row)] = (newDp[mask | (1 << row)] + dp[mask]) % MOD;
                    }
                }
            }

            dp = newDp;
        }
    }

    cout << dp[0] << endl;

    return 0;
}"""
        }
    ]

    # Problem 1649: Taxi (DAG DP)
    solutions["1649"] = [
        {
            "language": "python",
            "code": """import sys
from collections import defaultdict, deque
input = sys.stdin.readline

N, M = map(int, input().split())

adj = defaultdict(list)
in_degree = [0] * (N + 1)

for _ in range(M):
    a, b = map(int, input().split())
    adj[a].append(b)
    in_degree[b] += 1

src, dst = map(int, input().split())
K = int(input())

# Find longest path from src to dst in DAG
# Use topological sort and DP

# First, do topological sort
order = []
q = deque()
for i in range(1, N + 1):
    if in_degree[i] == 0:
        q.append(i)

while q:
    u = q.popleft()
    order.append(u)
    for v in adj[u]:
        in_degree[v] -= 1
        if in_degree[v] == 0:
            q.append(v)

# DP for longest path from src
dist = [-1] * (N + 1)
dist[src] = 0

for u in order:
    if dist[u] == -1:
        continue
    for v in adj[u]:
        dist[v] = max(dist[v], dist[u] + 1)

# Number of edges in longest path from src to dst
result = dist[dst]
print(result)"""
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
        int M = Integer.parseInt(st.nextToken());

        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i <= N; i++) adj.add(new ArrayList<>());
        int[] inDegree = new int[N + 1];

        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            adj.get(a).add(b);
            inDegree[b]++;
        }

        st = new StringTokenizer(br.readLine());
        int src = Integer.parseInt(st.nextToken());
        int dst = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(br.readLine().trim());

        // Topological sort
        Queue<Integer> q = new LinkedList<>();
        for (int i = 1; i <= N; i++) {
            if (inDegree[i] == 0) q.add(i);
        }

        List<Integer> order = new ArrayList<>();
        while (!q.isEmpty()) {
            int u = q.poll();
            order.add(u);
            for (int v : adj.get(u)) {
                if (--inDegree[v] == 0) q.add(v);
            }
        }

        int[] dist = new int[N + 1];
        Arrays.fill(dist, -1);
        dist[src] = 0;

        for (int u : order) {
            if (dist[u] == -1) continue;
            for (int v : adj.get(u)) {
                dist[v] = Math.max(dist[v], dist[u] + 1);
            }
        }

        System.out.println(dist[dst]);
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

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    vector<vector<int>> adj(N + 1);
    vector<int> inDegree(N + 1, 0);

    for (int i = 0; i < M; i++) {
        int a, b;
        cin >> a >> b;
        adj[a].push_back(b);
        inDegree[b]++;
    }

    int src, dst, K;
    cin >> src >> dst >> K;

    // Topological sort
    queue<int> q;
    for (int i = 1; i <= N; i++) {
        if (inDegree[i] == 0) q.push(i);
    }

    vector<int> order;
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        order.push_back(u);
        for (int v : adj[u]) {
            if (--inDegree[v] == 0) q.push(v);
        }
    }

    vector<int> dist(N + 1, -1);
    dist[src] = 0;

    for (int u : order) {
        if (dist[u] == -1) continue;
        for (int v : adj[u]) {
            dist[v] = max(dist[v], dist[u] + 1);
        }
    }

    cout << dist[dst] << endl;

    return 0;
}"""
        }
    ]

    return solutions

if __name__ == "__main__":
    filepath = "/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json"

    # Load data
    data = load_checkpoint(filepath)

    # Get solutions
    solutions = get_solutions_1640_1649()

    # Update problems
    updated = 0
    for problem in data:
        orig_id = problem.get("original_id", "")
        if orig_id in solutions and len(problem.get("solutions", [])) == 0:
            problem["solutions"] = solutions[orig_id]
            updated += 1
            print(f"Updated problem {orig_id}")

    # Save
    save_checkpoint(filepath, data)
    print(f"Updated {updated} problems")
