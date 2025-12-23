#!/usr/bin/env python3
"""
Generate solutions for Baekjoon problems 1730-1739
"""

import json

CHECKPOINT_FILE = "/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json"

SOLUTIONS = {
    "1730": {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
moves = input().strip()

# Grid: 0 = none, 1 = horizontal, 2 = vertical, 3 = both
grid = [[0] * n for _ in range(n)]

r, c = 0, 0
dr = {'U': -1, 'D': 1, 'L': 0, 'R': 0}
dc = {'U': 0, 'D': 0, 'L': -1, 'R': 1}

for move in moves:
    nr = r + dr[move]
    nc = c + dc[move]
    if 0 <= nr < n and 0 <= nc < n:
        if move in 'UD':
            grid[r][c] |= 2
            grid[nr][nc] |= 2
        else:
            grid[r][c] |= 1
            grid[nr][nc] |= 1
        r, c = nr, nc

result = []
for i in range(n):
    row = ""
    for j in range(n):
        if grid[i][j] == 0:
            row += '.'
        elif grid[i][j] == 1:
            row += '-'
        elif grid[i][j] == 2:
            row += '|'
        else:
            row += '+'
    result.append(row)
print('\\n'.join(result))
''',
        "java": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        String moves = br.readLine().trim();

        int[][] grid = new int[n][n];
        int r = 0, c = 0;

        for (char move : moves.toCharArray()) {
            int nr = r, nc = c;
            if (move == 'U') nr--;
            else if (move == 'D') nr++;
            else if (move == 'L') nc--;
            else if (move == 'R') nc++;

            if (nr >= 0 && nr < n && nc >= 0 && nc < n) {
                if (move == 'U' || move == 'D') {
                    grid[r][c] |= 2;
                    grid[nr][nc] |= 2;
                } else {
                    grid[r][c] |= 1;
                    grid[nr][nc] |= 1;
                }
                r = nr;
                c = nc;
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == 0) sb.append('.');
                else if (grid[i][j] == 1) sb.append('-');
                else if (grid[i][j] == 2) sb.append('|');
                else sb.append('+');
            }
            sb.append("\\n");
        }
        System.out.print(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    string moves;
    cin >> n >> moves;

    int grid[10][10] = {0};
    int r = 0, c = 0;

    for (char move : moves) {
        int nr = r, nc = c;
        if (move == 'U') nr--;
        else if (move == 'D') nr++;
        else if (move == 'L') nc--;
        else if (move == 'R') nc++;

        if (nr >= 0 && nr < n && nc >= 0 && nc < n) {
            if (move == 'U' || move == 'D') {
                grid[r][c] |= 2;
                grid[nr][nc] |= 2;
            } else {
                grid[r][c] |= 1;
                grid[nr][nc] |= 1;
            }
            r = nr;
            c = nc;
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (grid[i][j] == 0) cout << '.';
            else if (grid[i][j] == 1) cout << '-';
            else if (grid[i][j] == 2) cout << '|';
            else cout << '+';
        }
        cout << "\\n";
    }
    return 0;
}
'''
    },
    "1731": {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
arr = [int(input()) for _ in range(n)]

# Check if arithmetic sequence
d = arr[1] - arr[0]
is_arithmetic = all(arr[i] - arr[i-1] == d for i in range(2, n))

if is_arithmetic:
    print(arr[-1] + d)
else:
    # Geometric sequence
    r = arr[1] // arr[0]
    print(arr[-1] * r)
''',
        "java": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        long[] arr = new long[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Long.parseLong(br.readLine().trim());
        }

        long d = arr[1] - arr[0];
        boolean isArithmetic = true;
        for (int i = 2; i < n; i++) {
            if (arr[i] - arr[i-1] != d) {
                isArithmetic = false;
                break;
            }
        }

        if (isArithmetic) {
            System.out.println(arr[n-1] + d);
        } else {
            long r = arr[1] / arr[0];
            System.out.println(arr[n-1] * r);
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    long long arr[50];
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    long long d = arr[1] - arr[0];
    bool isArithmetic = true;
    for (int i = 2; i < n; i++) {
        if (arr[i] - arr[i-1] != d) {
            isArithmetic = false;
            break;
        }
    }

    if (isArithmetic) {
        cout << arr[n-1] + d << endl;
    } else {
        long long r = arr[1] / arr[0];
        cout << arr[n-1] * r << endl;
    }
    return 0;
}
'''
    },
    "1732": {
        "python": '''import sys
from math import gcd, atan2
input = sys.stdin.readline

n = int(input())
buildings = []
for _ in range(n):
    x, y, z = map(int, input().split())
    buildings.append((x, y, z))

# Group buildings by direction from origin (using reduced fraction)
from collections import defaultdict
directions = defaultdict(list)

for x, y, z in buildings:
    g = gcd(abs(x), y) if y != 0 else abs(x)
    if g == 0:
        g = 1
    dx = x // g if g != 0 else x
    dy = y // g if g != 0 else y
    if dy < 0 or (dy == 0 and dx < 0):
        dx, dy = -dx, -dy
    directions[(dx, dy)].append((x, y, z))

blocked = set()

for key, group in directions.items():
    # Sort by distance from origin (closer first means smaller y, if y same then smaller |x|)
    # Actually need to sort by distance
    group.sort(key=lambda p: p[0]**2 + p[1]**2)

    max_height = 0
    for x, y, z in group:
        if z <= max_height:
            blocked.add((x, y))
        max_height = max(max_height, z)

result = sorted(blocked, key=lambda p: (p[0], p[1]))
for x, y in result:
    print(x, y)
''',
        "java": '''import java.io.*;
import java.util.*;

public class Main {
    static int gcd(int a, int b) {
        if (b == 0) return a;
        return gcd(b, a % b);
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        Map<Long, List<int[]>> directions = new HashMap<>();

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());
            int z = Integer.parseInt(st.nextToken());

            int g = gcd(Math.abs(x), Math.abs(y));
            if (g == 0) g = 1;
            int dx = x / g;
            int dy = y / g;
            if (dy < 0 || (dy == 0 && dx < 0)) {
                dx = -dx;
                dy = -dy;
            }

            long key = (long)(dx + 200001) * 400002 + (dy + 200001);
            directions.computeIfAbsent(key, k -> new ArrayList<>()).add(new int[]{x, y, z});
        }

        List<int[]> blocked = new ArrayList<>();

        for (List<int[]> group : directions.values()) {
            group.sort((a, b) -> {
                long da = (long)a[0] * a[0] + (long)a[1] * a[1];
                long db = (long)b[0] * b[0] + (long)b[1] * b[1];
                return Long.compare(da, db);
            });

            int maxHeight = 0;
            for (int[] p : group) {
                if (p[2] <= maxHeight) {
                    blocked.add(new int[]{p[0], p[1]});
                }
                maxHeight = Math.max(maxHeight, p[2]);
            }
        }

        blocked.sort((a, b) -> {
            if (a[0] != b[0]) return Integer.compare(a[0], b[0]);
            return Integer.compare(a[1], b[1]);
        });

        StringBuilder sb = new StringBuilder();
        for (int[] p : blocked) {
            sb.append(p[0]).append(" ").append(p[1]).append("\\n");
        }
        System.out.print(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
#include <cmath>
using namespace std;

int gcd(int a, int b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    map<pair<int,int>, vector<tuple<int,int,int>>> directions;

    for (int i = 0; i < n; i++) {
        int x, y, z;
        cin >> x >> y >> z;

        int g = gcd(abs(x), abs(y));
        if (g == 0) g = 1;
        int dx = x / g;
        int dy = y / g;
        if (dy < 0 || (dy == 0 && dx < 0)) {
            dx = -dx;
            dy = -dy;
        }

        directions[{dx, dy}].push_back({x, y, z});
    }

    vector<pair<int,int>> blocked;

    for (auto& [key, group] : directions) {
        sort(group.begin(), group.end(), [](const auto& a, const auto& b) {
            long long da = (long long)get<0>(a) * get<0>(a) + (long long)get<1>(a) * get<1>(a);
            long long db = (long long)get<0>(b) * get<0>(b) + (long long)get<1>(b) * get<1>(b);
            return da < db;
        });

        int maxHeight = 0;
        for (auto& [x, y, z] : group) {
            if (z <= maxHeight) {
                blocked.push_back({x, y});
            }
            maxHeight = max(maxHeight, z);
        }
    }

    sort(blocked.begin(), blocked.end());

    for (auto& [x, y] : blocked) {
        cout << x << " " << y << "\\n";
    }
    return 0;
}
'''
    },
    "1733": {
        "python": '''import sys
from collections import defaultdict
sys.setrecursionlimit(2000100)
input = sys.stdin.readline

def solve():
    n = int(input())
    shirts = []
    for i in range(n):
        a, b = map(int, input().split())
        shirts.append((a, b))

    # Build graph: each number is a node, each shirt connects two numbers
    graph = defaultdict(list)
    for i, (a, b) in enumerate(shirts):
        graph[a].append((b, i))
        graph[b].append((a, i))

    result = [0] * n
    used = [False] * 1000001
    shirt_assigned = [False] * n

    # For each connected component, try to assign
    visited_nodes = set()

    def dfs(node, parent_shirt):
        stack = [(node, parent_shirt, False)]
        while stack:
            node, parent_shirt, processed = stack.pop()
            if processed:
                continue
            if node in visited_nodes:
                continue
            visited_nodes.add(node)

            for neighbor, shirt_idx in graph[node]:
                if shirt_assigned[shirt_idx]:
                    continue
                a, b = shirts[shirt_idx]
                # Try to assign this shirt
                if not used[a]:
                    result[shirt_idx] = a
                    used[a] = True
                    shirt_assigned[shirt_idx] = True
                elif not used[b]:
                    result[shirt_idx] = b
                    used[b] = True
                    shirt_assigned[shirt_idx] = True
                else:
                    print(-1)
                    return False

                if neighbor not in visited_nodes:
                    stack.append((neighbor, shirt_idx, False))
        return True

    for i, (a, b) in enumerate(shirts):
        if a not in visited_nodes:
            if not dfs(a, -1):
                return
        if b not in visited_nodes:
            if not dfs(b, -1):
                return

    for i in range(n):
        if not shirt_assigned[i]:
            a, b = shirts[i]
            if not used[a]:
                result[i] = a
                used[a] = True
            elif not used[b]:
                result[i] = b
                used[b] = True
            else:
                print(-1)
                return

    for r in result:
        print(r)

solve()
''',
        "java": '''import java.io.*;
import java.util.*;

public class Main {
    static int[] result;
    static boolean[] used;
    static boolean[] shirtAssigned;
    static int[][] shirts;
    static List<int[]>[] graph;
    static boolean[] visitedNodes;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        shirts = new int[n][2];
        graph = new ArrayList[1000001];
        for (int i = 0; i <= 1000000; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            shirts[i][0] = a;
            shirts[i][1] = b;
            graph[a].add(new int[]{b, i});
            graph[b].add(new int[]{a, i});
        }

        result = new int[n];
        used = new boolean[1000001];
        shirtAssigned = new boolean[n];
        visitedNodes = new boolean[1000001];

        for (int i = 0; i < n; i++) {
            int a = shirts[i][0];
            int b = shirts[i][1];
            if (!visitedNodes[a]) {
                if (!dfs(a)) {
                    System.out.println(-1);
                    return;
                }
            }
            if (!visitedNodes[b]) {
                if (!dfs(b)) {
                    System.out.println(-1);
                    return;
                }
            }
        }

        for (int i = 0; i < n; i++) {
            if (!shirtAssigned[i]) {
                int a = shirts[i][0];
                int b = shirts[i][1];
                if (!used[a]) {
                    result[i] = a;
                    used[a] = true;
                } else if (!used[b]) {
                    result[i] = b;
                    used[b] = true;
                } else {
                    System.out.println(-1);
                    return;
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append(result[i]).append("\\n");
        }
        System.out.print(sb);
    }

    static boolean dfs(int start) {
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(start);

        while (!stack.isEmpty()) {
            int node = stack.pop();
            if (visitedNodes[node]) continue;
            visitedNodes[node] = true;

            for (int[] edge : graph[node]) {
                int neighbor = edge[0];
                int shirtIdx = edge[1];

                if (shirtAssigned[shirtIdx]) continue;

                int a = shirts[shirtIdx][0];
                int b = shirts[shirtIdx][1];

                if (!used[a]) {
                    result[shirtIdx] = a;
                    used[a] = true;
                    shirtAssigned[shirtIdx] = true;
                } else if (!used[b]) {
                    result[shirtIdx] = b;
                    used[b] = true;
                    shirtAssigned[shirtIdx] = true;
                } else {
                    return false;
                }

                if (!visitedNodes[neighbor]) {
                    stack.push(neighbor);
                }
            }
        }
        return true;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <stack>
using namespace std;

int result[1000001];
bool used[1000001];
bool shirtAssigned[1000001];
int shirts[1000001][2];
vector<pair<int,int>> graph[1000001];
bool visitedNodes[1000001];

bool dfs(int start) {
    stack<int> st;
    st.push(start);

    while (!st.empty()) {
        int node = st.top();
        st.pop();

        if (visitedNodes[node]) continue;
        visitedNodes[node] = true;

        for (auto& edge : graph[node]) {
            int neighbor = edge.first;
            int shirtIdx = edge.second;

            if (shirtAssigned[shirtIdx]) continue;

            int a = shirts[shirtIdx][0];
            int b = shirts[shirtIdx][1];

            if (!used[a]) {
                result[shirtIdx] = a;
                used[a] = true;
                shirtAssigned[shirtIdx] = true;
            } else if (!used[b]) {
                result[shirtIdx] = b;
                used[b] = true;
                shirtAssigned[shirtIdx] = true;
            } else {
                return false;
            }

            if (!visitedNodes[neighbor]) {
                st.push(neighbor);
            }
        }
    }
    return true;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    for (int i = 0; i < n; i++) {
        int a, b;
        cin >> a >> b;
        shirts[i][0] = a;
        shirts[i][1] = b;
        graph[a].push_back({b, i});
        graph[b].push_back({a, i});
    }

    for (int i = 0; i < n; i++) {
        int a = shirts[i][0];
        int b = shirts[i][1];
        if (!visitedNodes[a]) {
            if (!dfs(a)) {
                cout << -1 << endl;
                return 0;
            }
        }
        if (!visitedNodes[b]) {
            if (!dfs(b)) {
                cout << -1 << endl;
                return 0;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        if (!shirtAssigned[i]) {
            int a = shirts[i][0];
            int b = shirts[i][1];
            if (!used[a]) {
                result[i] = a;
                used[a] = true;
            } else if (!used[b]) {
                result[i] = b;
                used[b] = true;
            } else {
                cout << -1 << endl;
                return 0;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        cout << result[i] << "\\n";
    }
    return 0;
}
'''
    },
    "1734": {
        "python": '''import sys
from collections import defaultdict, deque
sys.setrecursionlimit(200010)
input = sys.stdin.readline

def solve():
    line = input().split()
    n, e = int(line[0]), int(line[1])

    graph = defaultdict(list)
    edges = []
    for _ in range(e):
        u, v = map(int, input().split())
        graph[u].append((v, len(edges)))
        graph[v].append((u, len(edges)))
        edges.append((u, v))

    q = int(input())
    queries = []
    for _ in range(q):
        parts = list(map(int, input().split()))
        queries.append(parts)

    # Build spanning tree using BFS
    parent = [-1] * (n + 1)
    parent_edge = [-1] * (n + 1)
    depth = [0] * (n + 1)
    visited = [False] * (n + 1)

    queue = deque([1])
    visited[1] = True

    while queue:
        u = queue.popleft()
        for v, eid in graph[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                parent_edge[v] = eid
                depth[v] = depth[u] + 1
                queue.append(v)

    # Simple LCA
    def lca(u, v):
        while depth[u] > depth[v]:
            u = parent[u]
        while depth[v] > depth[u]:
            v = parent[v]
        while u != v:
            u = parent[u]
            v = parent[v]
        return u

    # Check connectivity using BFS with excluded edge/node
    def can_reach_exclude_edge(a, b, g1, g2):
        # Find edge index
        edge_to_remove = None
        for v, eid in graph[g1]:
            if v == g2:
                edge_to_remove = eid
                break

        visited = [False] * (n + 1)
        queue = deque([a])
        visited[a] = True

        while queue:
            u = queue.popleft()
            if u == b:
                return True
            for v, eid in graph[u]:
                if not visited[v] and eid != edge_to_remove:
                    visited[v] = True
                    queue.append(v)
        return False

    def can_reach_exclude_node(a, b, c):
        if a == c or b == c:
            return False

        visited = [False] * (n + 1)
        visited[c] = True
        queue = deque([a])
        visited[a] = True

        while queue:
            u = queue.popleft()
            if u == b:
                return True
            for v, eid in graph[u]:
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)
        return False

    results = []
    for query in queries:
        if query[0] == 1:
            a, b, g1, g2 = query[1], query[2], query[3], query[4]
            if can_reach_exclude_edge(a, b, g1, g2):
                results.append("yes")
            else:
                results.append("no")
        else:
            a, b, c = query[1], query[2], query[3]
            if can_reach_exclude_node(a, b, c):
                results.append("yes")
            else:
                results.append("no")

    print('\\n'.join(results))

solve()
''',
        "java": '''import java.io.*;
import java.util.*;

public class Main {
    static List<int[]>[] graph;
    static int n;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        n = Integer.parseInt(st.nextToken());
        int e = Integer.parseInt(st.nextToken());

        graph = new ArrayList[n + 1];
        for (int i = 0; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < e; i++) {
            st = new StringTokenizer(br.readLine());
            int u = Integer.parseInt(st.nextToken());
            int v = Integer.parseInt(st.nextToken());
            graph[u].add(new int[]{v, i});
            graph[v].add(new int[]{u, i});
        }

        int q = Integer.parseInt(br.readLine().trim());
        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < q; i++) {
            st = new StringTokenizer(br.readLine());
            int type = Integer.parseInt(st.nextToken());

            if (type == 1) {
                int a = Integer.parseInt(st.nextToken());
                int b = Integer.parseInt(st.nextToken());
                int g1 = Integer.parseInt(st.nextToken());
                int g2 = Integer.parseInt(st.nextToken());

                if (canReachExcludeEdge(a, b, g1, g2)) {
                    sb.append("yes\\n");
                } else {
                    sb.append("no\\n");
                }
            } else {
                int a = Integer.parseInt(st.nextToken());
                int b = Integer.parseInt(st.nextToken());
                int c = Integer.parseInt(st.nextToken());

                if (canReachExcludeNode(a, b, c)) {
                    sb.append("yes\\n");
                } else {
                    sb.append("no\\n");
                }
            }
        }
        System.out.print(sb);
    }

    static boolean canReachExcludeEdge(int a, int b, int g1, int g2) {
        int edgeToRemove = -1;
        for (int[] edge : graph[g1]) {
            if (edge[0] == g2) {
                edgeToRemove = edge[1];
                break;
            }
        }

        boolean[] visited = new boolean[n + 1];
        Deque<Integer> queue = new ArrayDeque<>();
        queue.add(a);
        visited[a] = true;

        while (!queue.isEmpty()) {
            int u = queue.poll();
            if (u == b) return true;

            for (int[] edge : graph[u]) {
                if (!visited[edge[0]] && edge[1] != edgeToRemove) {
                    visited[edge[0]] = true;
                    queue.add(edge[0]);
                }
            }
        }
        return false;
    }

    static boolean canReachExcludeNode(int a, int b, int c) {
        if (a == c || b == c) return false;

        boolean[] visited = new boolean[n + 1];
        visited[c] = true;
        Deque<Integer> queue = new ArrayDeque<>();
        queue.add(a);
        visited[a] = true;

        while (!queue.isEmpty()) {
            int u = queue.poll();
            if (u == b) return true;

            for (int[] edge : graph[u]) {
                if (!visited[edge[0]]) {
                    visited[edge[0]] = true;
                    queue.add(edge[0]);
                }
            }
        }
        return false;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <queue>
using namespace std;

vector<pair<int,int>> graph[100001];
int n;

bool canReachExcludeEdge(int a, int b, int g1, int g2) {
    int edgeToRemove = -1;
    for (auto& e : graph[g1]) {
        if (e.first == g2) {
            edgeToRemove = e.second;
            break;
        }
    }

    vector<bool> visited(n + 1, false);
    queue<int> q;
    q.push(a);
    visited[a] = true;

    while (!q.empty()) {
        int u = q.front();
        q.pop();
        if (u == b) return true;

        for (auto& e : graph[u]) {
            if (!visited[e.first] && e.second != edgeToRemove) {
                visited[e.first] = true;
                q.push(e.first);
            }
        }
    }
    return false;
}

bool canReachExcludeNode(int a, int b, int c) {
    if (a == c || b == c) return false;

    vector<bool> visited(n + 1, false);
    visited[c] = true;
    queue<int> q;
    q.push(a);
    visited[a] = true;

    while (!q.empty()) {
        int u = q.front();
        q.pop();
        if (u == b) return true;

        for (auto& e : graph[u]) {
            if (!visited[e.first]) {
                visited[e.first] = true;
                q.push(e.first);
            }
        }
    }
    return false;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int e;
    cin >> n >> e;

    for (int i = 0; i < e; i++) {
        int u, v;
        cin >> u >> v;
        graph[u].push_back({v, i});
        graph[v].push_back({u, i});
    }

    int q;
    cin >> q;

    while (q--) {
        int type;
        cin >> type;

        if (type == 1) {
            int a, b, g1, g2;
            cin >> a >> b >> g1 >> g2;
            cout << (canReachExcludeEdge(a, b, g1, g2) ? "yes" : "no") << "\\n";
        } else {
            int a, b, c;
            cin >> a >> b >> c;
            cout << (canReachExcludeNode(a, b, c) ? "yes" : "no") << "\\n";
        }
    }
    return 0;
}
'''
    },
    "1735": {
        "python": '''import sys
from math import gcd
input = sys.stdin.readline

a1, b1 = map(int, input().split())
a2, b2 = map(int, input().split())

# a1/b1 + a2/b2 = (a1*b2 + a2*b1) / (b1*b2)
numerator = a1 * b2 + a2 * b1
denominator = b1 * b2

g = gcd(numerator, denominator)
print(numerator // g, denominator // g)
''',
        "java": '''import java.io.*;
import java.util.*;

public class Main {
    static long gcd(long a, long b) {
        if (b == 0) return a;
        return gcd(b, a % b);
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        long a1 = Long.parseLong(st.nextToken());
        long b1 = Long.parseLong(st.nextToken());

        st = new StringTokenizer(br.readLine());
        long a2 = Long.parseLong(st.nextToken());
        long b2 = Long.parseLong(st.nextToken());

        long numerator = a1 * b2 + a2 * b1;
        long denominator = b1 * b2;

        long g = gcd(numerator, denominator);
        System.out.println((numerator / g) + " " + (denominator / g));
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

long long gcd(long long a, long long b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long a1, b1, a2, b2;
    cin >> a1 >> b1 >> a2 >> b2;

    long long numerator = a1 * b2 + a2 * b1;
    long long denominator = b1 * b2;

    long long g = gcd(numerator, denominator);
    cout << numerator / g << " " << denominator / g << endl;
    return 0;
}
'''
    },
    "1736": {
        "python": '''import sys
input = sys.stdin.readline

n, m = map(int, input().split())
grid = []
trash = []

for i in range(n):
    row = list(map(int, input().split()))
    grid.append(row)
    for j in range(m):
        if row[j] == 1:
            trash.append((i, j))

# Sort trash by row, then column
trash.sort()

# Greedy: assign robots to cover trash
# Robot path covers points with increasing row and column
# This is equivalent to finding minimum path cover in DAG
# Which equals n - maximum matching

# Build bipartite graph: trash i can reach trash j if i.row <= j.row and i.col <= j.col and i != j
from collections import defaultdict

k = len(trash)
if k == 0:
    print(0)
else:
    # Left side: trash points, Right side: trash points
    # Edge from i to j if trash[i] can reach trash[j] (i before j in path)
    adj = defaultdict(list)
    for i in range(k):
        for j in range(k):
            if i != j and trash[i][0] <= trash[j][0] and trash[i][1] <= trash[j][1]:
                if trash[i][0] < trash[j][0] or trash[i][1] < trash[j][1]:
                    adj[i].append(j)

    # Maximum bipartite matching using Hungarian algorithm
    match_r = [-1] * k

    def dfs(u, visited):
        for v in adj[u]:
            if visited[v]:
                continue
            visited[v] = True
            if match_r[v] == -1 or dfs(match_r[v], visited):
                match_r[v] = u
                return True
        return False

    matching = 0
    for i in range(k):
        visited = [False] * k
        if dfs(i, visited):
            matching += 1

    print(k - matching)
''',
        "java": '''import java.io.*;
import java.util.*;

public class Main {
    static List<Integer>[] adj;
    static int[] matchR;
    static int k;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        List<int[]> trash = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < m; j++) {
                if (Integer.parseInt(st.nextToken()) == 1) {
                    trash.add(new int[]{i, j});
                }
            }
        }

        k = trash.size();
        if (k == 0) {
            System.out.println(0);
            return;
        }

        trash.sort((a, b) -> a[0] != b[0] ? a[0] - b[0] : a[1] - b[1]);

        adj = new ArrayList[k];
        for (int i = 0; i < k; i++) {
            adj[i] = new ArrayList<>();
        }

        for (int i = 0; i < k; i++) {
            for (int j = 0; j < k; j++) {
                if (i != j && trash.get(i)[0] <= trash.get(j)[0] && trash.get(i)[1] <= trash.get(j)[1]) {
                    if (trash.get(i)[0] < trash.get(j)[0] || trash.get(i)[1] < trash.get(j)[1]) {
                        adj[i].add(j);
                    }
                }
            }
        }

        matchR = new int[k];
        Arrays.fill(matchR, -1);

        int matching = 0;
        for (int i = 0; i < k; i++) {
            boolean[] visited = new boolean[k];
            if (dfs(i, visited)) {
                matching++;
            }
        }

        System.out.println(k - matching);
    }

    static boolean dfs(int u, boolean[] visited) {
        for (int v : adj[u]) {
            if (visited[v]) continue;
            visited[v] = true;
            if (matchR[v] == -1 || dfs(matchR[v], visited)) {
                matchR[v] = u;
                return true;
            }
        }
        return false;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

vector<int> adj[10001];
int matchR[10001];
bool visited[10001];
int k;

bool dfs(int u) {
    for (int v : adj[u]) {
        if (visited[v]) continue;
        visited[v] = true;
        if (matchR[v] == -1 || dfs(matchR[v])) {
            matchR[v] = u;
            return true;
        }
    }
    return false;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<pair<int,int>> trash;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            int x;
            cin >> x;
            if (x == 1) {
                trash.push_back({i, j});
            }
        }
    }

    k = trash.size();
    if (k == 0) {
        cout << 0 << endl;
        return 0;
    }

    sort(trash.begin(), trash.end());

    for (int i = 0; i < k; i++) {
        for (int j = 0; j < k; j++) {
            if (i != j && trash[i].first <= trash[j].first && trash[i].second <= trash[j].second) {
                if (trash[i].first < trash[j].first || trash[i].second < trash[j].second) {
                    adj[i].push_back(j);
                }
            }
        }
    }

    fill(matchR, matchR + k, -1);

    int matching = 0;
    for (int i = 0; i < k; i++) {
        fill(visited, visited + k, false);
        if (dfs(i)) {
            matching++;
        }
    }

    cout << k - matching << endl;
    return 0;
}
'''
    },
    "1737": {
        "python": '''import sys
from math import pi
sys.setrecursionlimit(100000)

MOD = 10**18

memo = {}

def P(n):
    if n <= pi:
        return 1
    if n in memo:
        return memo[n]

    result = (P(n - 1) + P(n - pi)) % MOD
    memo[n] = result
    return result

n = int(input())
print(P(n))
''',
        "java": '''import java.io.*;
import java.util.*;

public class Main {
    static final long MOD = 1000000000000000000L;
    static final double PI = Math.PI;
    static Map<Double, Long> memo = new HashMap<>();

    static long P(double n) {
        if (n <= PI) return 1;
        if (memo.containsKey(n)) return memo.get(n);

        long result = (P(n - 1) + P(n - PI)) % MOD;
        memo.put(n, result);
        return result;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        System.out.println(P(n));
    }
}
''',
        "cpp": '''#include <iostream>
#include <map>
#include <cmath>
using namespace std;

const long long MOD = 1000000000000000000LL;
const double PI = acos(-1.0);
map<double, long long> memo;

long long P(double n) {
    if (n <= PI) return 1;
    if (memo.count(n)) return memo[n];

    long long result = (P(n - 1) + P(n - PI)) % MOD;
    memo[n] = result;
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    cout << P(n) << endl;
    return 0;
}
'''
    },
    "1738": {
        "python": '''import sys
from collections import deque
input = sys.stdin.readline

INF = float('inf')

def solve():
    n, m = map(int, input().split())

    edges = []
    graph = [[] for _ in range(n + 1)]
    reverse_graph = [[] for _ in range(n + 1)]

    for _ in range(m):
        u, v, w = map(int, input().split())
        edges.append((u, v, w))
        graph[u].append((v, w))
        reverse_graph[v].append(u)

    # Check if n is reachable from 1
    visited = [False] * (n + 1)
    queue = deque([1])
    visited[1] = True
    while queue:
        u = queue.popleft()
        for v, w in graph[u]:
            if not visited[v]:
                visited[v] = True
                queue.append(v)

    if not visited[n]:
        print(-1)
        return

    # Check which nodes can reach n
    can_reach_n = [False] * (n + 1)
    queue = deque([n])
    can_reach_n[n] = True
    while queue:
        u = queue.popleft()
        for v in reverse_graph[u]:
            if not can_reach_n[v]:
                can_reach_n[v] = True
                queue.append(v)

    # Bellman-Ford for longest path (negate weights)
    dist = [-INF] * (n + 1)
    parent = [-1] * (n + 1)
    dist[1] = 0

    for i in range(n - 1):
        for u, v, w in edges:
            if can_reach_n[u] and can_reach_n[v]:
                if dist[u] != -INF and dist[u] + w > dist[v]:
                    dist[v] = dist[u] + w
                    parent[v] = u

    # Check for positive cycle on path to n
    for u, v, w in edges:
        if can_reach_n[u] and can_reach_n[v]:
            if dist[u] != -INF and dist[u] + w > dist[v]:
                # Positive cycle detected - check if it's on path to n
                print(-1)
                return

    # Reconstruct path
    if dist[n] == -INF:
        print(-1)
        return

    path = []
    curr = n
    while curr != -1:
        path.append(curr)
        curr = parent[curr]

    path.reverse()
    print(' '.join(map(str, path)))

solve()
''',
        "java": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        int[][] edges = new int[m][3];
        List<int[]>[] graph = new ArrayList[n + 1];
        List<Integer>[] reverseGraph = new ArrayList[n + 1];

        for (int i = 0; i <= n; i++) {
            graph[i] = new ArrayList<>();
            reverseGraph[i] = new ArrayList<>();
        }

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            int u = Integer.parseInt(st.nextToken());
            int v = Integer.parseInt(st.nextToken());
            int w = Integer.parseInt(st.nextToken());
            edges[i] = new int[]{u, v, w};
            graph[u].add(new int[]{v, w});
            reverseGraph[v].add(u);
        }

        // Check reachability from 1
        boolean[] visited = new boolean[n + 1];
        Deque<Integer> queue = new ArrayDeque<>();
        queue.add(1);
        visited[1] = true;
        while (!queue.isEmpty()) {
            int u = queue.poll();
            for (int[] e : graph[u]) {
                if (!visited[e[0]]) {
                    visited[e[0]] = true;
                    queue.add(e[0]);
                }
            }
        }

        if (!visited[n]) {
            System.out.println(-1);
            return;
        }

        // Check which nodes can reach n
        boolean[] canReachN = new boolean[n + 1];
        queue.add(n);
        canReachN[n] = true;
        while (!queue.isEmpty()) {
            int u = queue.poll();
            for (int v : reverseGraph[u]) {
                if (!canReachN[v]) {
                    canReachN[v] = true;
                    queue.add(v);
                }
            }
        }

        long INF = Long.MIN_VALUE;
        long[] dist = new long[n + 1];
        int[] parent = new int[n + 1];
        Arrays.fill(dist, INF);
        Arrays.fill(parent, -1);
        dist[1] = 0;

        for (int i = 0; i < n - 1; i++) {
            for (int[] e : edges) {
                int u = e[0], v = e[1], w = e[2];
                if (canReachN[u] && canReachN[v]) {
                    if (dist[u] != INF && dist[u] + w > dist[v]) {
                        dist[v] = dist[u] + w;
                        parent[v] = u;
                    }
                }
            }
        }

        for (int[] e : edges) {
            int u = e[0], v = e[1], w = e[2];
            if (canReachN[u] && canReachN[v]) {
                if (dist[u] != INF && dist[u] + w > dist[v]) {
                    System.out.println(-1);
                    return;
                }
            }
        }

        if (dist[n] == INF) {
            System.out.println(-1);
            return;
        }

        List<Integer> path = new ArrayList<>();
        int curr = n;
        while (curr != -1) {
            path.add(curr);
            curr = parent[curr];
        }

        Collections.reverse(path);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < path.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(path.get(i));
        }
        System.out.println(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

const long long INF = -1e18;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<tuple<int,int,int>> edges(m);
    vector<vector<pair<int,int>>> graph(n + 1);
    vector<vector<int>> reverseGraph(n + 1);

    for (int i = 0; i < m; i++) {
        int u, v, w;
        cin >> u >> v >> w;
        edges[i] = {u, v, w};
        graph[u].push_back({v, w});
        reverseGraph[v].push_back(u);
    }

    // Check reachability from 1
    vector<bool> visited(n + 1, false);
    queue<int> q;
    q.push(1);
    visited[1] = true;
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        for (auto& [v, w] : graph[u]) {
            if (!visited[v]) {
                visited[v] = true;
                q.push(v);
            }
        }
    }

    if (!visited[n]) {
        cout << -1 << endl;
        return 0;
    }

    // Check which nodes can reach n
    vector<bool> canReachN(n + 1, false);
    q.push(n);
    canReachN[n] = true;
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        for (int v : reverseGraph[u]) {
            if (!canReachN[v]) {
                canReachN[v] = true;
                q.push(v);
            }
        }
    }

    vector<long long> dist(n + 1, INF);
    vector<int> parent(n + 1, -1);
    dist[1] = 0;

    for (int i = 0; i < n - 1; i++) {
        for (auto& [u, v, w] : edges) {
            if (canReachN[u] && canReachN[v]) {
                if (dist[u] != INF && dist[u] + w > dist[v]) {
                    dist[v] = dist[u] + w;
                    parent[v] = u;
                }
            }
        }
    }

    for (auto& [u, v, w] : edges) {
        if (canReachN[u] && canReachN[v]) {
            if (dist[u] != INF && dist[u] + w > dist[v]) {
                cout << -1 << endl;
                return 0;
            }
        }
    }

    if (dist[n] == INF) {
        cout << -1 << endl;
        return 0;
    }

    vector<int> path;
    int curr = n;
    while (curr != -1) {
        path.push_back(curr);
        curr = parent[curr];
    }

    reverse(path.begin(), path.end());
    for (int i = 0; i < path.size(); i++) {
        if (i > 0) cout << " ";
        cout << path[i];
    }
    cout << endl;
    return 0;
}
'''
    },
    "1739": {
        "python": '''import sys
sys.setrecursionlimit(100000)
input = sys.stdin.readline

def solve():
    t = int(input())

    for _ in range(t):
        n, m, k = map(int, input().split())

        # 2-SAT problem
        # For each horizontal road segment and vertical road segment, we have a direction variable
        # Horizontal roads: indexed 0 to N*M-1 (for each row, M-1 segments = N*(M-1) total)
        # But simpler: for road i (horizontal), variable i means direction right (true) or left (false)

        # Actually, let's use interval-based approach
        # For horizontal road at row r: direction is either left or right
        # For vertical road at column c: direction is either up or down

        # We need to check if we can assign directions such that each bus can travel
        # Let's use simple simulation approach for small cases

        buses = []
        for _ in range(k):
            a, b, c, d = map(int, input().split())
            buses.append((a, b, c, d))

        # For 2-SAT:
        # Variable for horizontal road h: h can go right (true) or left (false)
        # Variable for vertical road v: v can go down (true) or up (false)

        # Each bus (a,b) -> (c,d) needs a path using at most one horizontal and one vertical road
        # If a == c: only use horizontal road between min(b,d) and max(b,d) on row a
        # If b == d: only use vertical road between min(a,c) and max(a,c) on column b
        # Otherwise: can go horizontal then vertical, or vertical then horizontal

        # This is a 2-SAT problem where:
        # - If bus must use horizontal road from b to d on row a:
        #   - If b < d: road segment on row a from b to d-1 must go right
        #   - If b > d: road segment on row a from d to b-1 must go left

        # For simplicity, let's use implication graph
        # Variable indexing: horizontal road (r, c) -> (r, c+1) is var r*(M-1) + c
        # Vertical road (r, c) -> (r+1, c) is var N*(M-1) + r*(M) + c (wait, need to think)

        # Actually for this problem, let's simplify:
        # We have N horizontal roads (rows 1 to N), each has direction
        # We have M vertical roads (columns 1 to M), each has direction

        # For bus (a,b) -> (c,d):
        # Path option 1: go on row a from b to d, then on column d from a to c
        # Path option 2: go on column b from a to c, then on row c from b to d

        # For path 1: row a direction must match sign(d-b), col d direction must match sign(c-a)
        # For path 2: col b direction must match sign(c-a), row c direction must match sign(d-b)

        # 2-SAT: at least one of the two paths must be valid

        # Variable i for row i: True = right, False = left
        # Variable n+j for col j: True = down, False = up

        def var(is_row, idx, direction):
            # direction: for row, True=right, False=left
            #            for col, True=down, False=up
            base = idx if is_row else n + idx
            return 2 * base + (1 if direction else 0)

        def neg(v):
            return v ^ 1

        num_vars = 2 * (n + m)
        adj = [[] for _ in range(num_vars)]
        radj = [[] for _ in range(num_vars)]

        def add_or(a, b):
            # (a OR b) = (NOT a -> b) AND (NOT b -> a)
            adj[neg(a)].append(b)
            adj[neg(b)].append(a)
            radj[b].append(neg(a))
            radj[a].append(neg(b))

        def add_must(a):
            # Must be a: (NOT a -> a), which means if NOT a then contradiction
            adj[neg(a)].append(a)
            radj[a].append(neg(a))

        valid = True

        for a, b, c, d in buses:
            if a == c and b == d:
                continue

            # Path 1: row a (b->d), col d (a->c)
            # Path 2: col b (a->c), row c (b->d)

            options = []

            if a == c:
                # Only horizontal movement on row a
                if b < d:
                    add_must(var(True, a, True))  # row a must go right
                else:
                    add_must(var(True, a, False))  # row a must go left
            elif b == d:
                # Only vertical movement on col b
                if a < c:
                    add_must(var(False, b, True))  # col b must go down
                else:
                    add_must(var(False, b, False))  # col b must go up
            else:
                # Two options
                # Path 1: row a needs direction sign(d-b), col d needs direction sign(c-a)
                row_a_dir = d > b  # True = right
                col_d_dir = c > a  # True = down

                # Path 2: col b needs direction sign(c-a), row c needs direction sign(d-b)
                col_b_dir = c > a  # True = down
                row_c_dir = d > b  # True = right

                # At least one path must work
                # Path 1 works if: row[a] == row_a_dir AND col[d] == col_d_dir
                # Path 2 works if: col[b] == col_b_dir AND row[c] == row_c_dir

                p1_row = var(True, a, row_a_dir)
                p1_col = var(False, d, col_d_dir)
                p2_col = var(False, b, col_b_dir)
                p2_row = var(True, c, row_c_dir)

                # (p1_row AND p1_col) OR (p2_col AND p2_row)
                # NOT(p1_row) OR NOT(p1_col) -> (p2_col AND p2_row)
                # NOT(p2_col) OR NOT(p2_row) -> (p1_row AND p1_col)

                # If NOT p1_row -> must use path 2
                adj[neg(p1_row)].append(p2_col)
                adj[neg(p1_row)].append(p2_row)
                radj[p2_col].append(neg(p1_row))
                radj[p2_row].append(neg(p1_row))

                # If NOT p1_col -> must use path 2
                adj[neg(p1_col)].append(p2_col)
                adj[neg(p1_col)].append(p2_row)
                radj[p2_col].append(neg(p1_col))
                radj[p2_row].append(neg(p1_col))

                # If NOT p2_col -> must use path 1
                adj[neg(p2_col)].append(p1_row)
                adj[neg(p2_col)].append(p1_col)
                radj[p1_row].append(neg(p2_col))
                radj[p1_col].append(neg(p2_col))

                # If NOT p2_row -> must use path 1
                adj[neg(p2_row)].append(p1_row)
                adj[neg(p2_row)].append(p1_col)
                radj[p1_row].append(neg(p2_row))
                radj[p1_col].append(neg(p2_row))

        # SCC-based 2-SAT
        order = []
        visited = [False] * num_vars

        def dfs1(u):
            stack = [(u, False)]
            while stack:
                node, done = stack.pop()
                if done:
                    order.append(node)
                    continue
                if visited[node]:
                    continue
                visited[node] = True
                stack.append((node, True))
                for v in adj[node]:
                    if not visited[v]:
                        stack.append((v, False))

        for i in range(num_vars):
            if not visited[i]:
                dfs1(i)

        scc_id = [-1] * num_vars
        scc_num = 0

        def dfs2(u, sid):
            stack = [u]
            while stack:
                node = stack.pop()
                if scc_id[node] != -1:
                    continue
                scc_id[node] = sid
                for v in radj[node]:
                    if scc_id[v] == -1:
                        stack.append(v)

        for u in reversed(order):
            if scc_id[u] == -1:
                dfs2(u, scc_num)
                scc_num += 1

        # Check satisfiability
        for i in range(n + m):
            if scc_id[2*i] == scc_id[2*i + 1]:
                valid = False
                break

        print("Yes" if valid else "No")

solve()
''',
        "java": '''import java.io.*;
import java.util.*;

public class Main {
    static List<Integer>[] adj, radj;
    static boolean[] visited;
    static int[] sccId;
    static List<Integer> order;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());
        StringBuilder sb = new StringBuilder();

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int m = Integer.parseInt(st.nextToken());
            int k = Integer.parseInt(st.nextToken());

            int numVars = 2 * (n + m);
            adj = new ArrayList[numVars];
            radj = new ArrayList[numVars];
            for (int i = 0; i < numVars; i++) {
                adj[i] = new ArrayList<>();
                radj[i] = new ArrayList<>();
            }

            boolean valid = true;

            for (int i = 0; i < k; i++) {
                st = new StringTokenizer(br.readLine());
                int a = Integer.parseInt(st.nextToken());
                int b = Integer.parseInt(st.nextToken());
                int c = Integer.parseInt(st.nextToken());
                int d = Integer.parseInt(st.nextToken());

                if (a == c && b == d) continue;

                if (a == c) {
                    int v = var(true, a, b < d, n);
                    addMust(v);
                } else if (b == d) {
                    int v = var(false, b, a < c, n);
                    addMust(v);
                } else {
                    int p1Row = var(true, a, d > b, n);
                    int p1Col = var(false, d, c > a, n);
                    int p2Col = var(false, b, c > a, n);
                    int p2Row = var(true, c, d > b, n);

                    addEdge(neg(p1Row), p2Col);
                    addEdge(neg(p1Row), p2Row);
                    addEdge(neg(p1Col), p2Col);
                    addEdge(neg(p1Col), p2Row);
                    addEdge(neg(p2Col), p1Row);
                    addEdge(neg(p2Col), p1Col);
                    addEdge(neg(p2Row), p1Row);
                    addEdge(neg(p2Row), p1Col);
                }
            }

            visited = new boolean[numVars];
            order = new ArrayList<>();

            for (int i = 0; i < numVars; i++) {
                if (!visited[i]) dfs1(i);
            }

            sccId = new int[numVars];
            Arrays.fill(sccId, -1);
            int sccNum = 0;

            for (int i = numVars - 1; i >= 0; i--) {
                int u = order.get(i);
                if (sccId[u] == -1) {
                    dfs2(u, sccNum++);
                }
            }

            for (int i = 0; i < n + m; i++) {
                if (sccId[2*i] == sccId[2*i + 1]) {
                    valid = false;
                    break;
                }
            }

            sb.append(valid ? "Yes" : "No").append("\\n");
        }
        System.out.print(sb);
    }

    static int var(boolean isRow, int idx, boolean dir, int n) {
        int base = isRow ? idx : n + idx;
        return 2 * base + (dir ? 1 : 0);
    }

    static int neg(int v) {
        return v ^ 1;
    }

    static void addEdge(int u, int v) {
        adj[u].add(v);
        radj[v].add(u);
    }

    static void addMust(int a) {
        addEdge(neg(a), a);
    }

    static void dfs1(int u) {
        Deque<int[]> stack = new ArrayDeque<>();
        stack.push(new int[]{u, 0});

        while (!stack.isEmpty()) {
            int[] cur = stack.peek();
            int node = cur[0];

            if (!visited[node]) {
                visited[node] = true;
            }

            boolean found = false;
            while (cur[1] < adj[node].size()) {
                int v = adj[node].get(cur[1]++);
                if (!visited[v]) {
                    stack.push(new int[]{v, 0});
                    found = true;
                    break;
                }
            }

            if (!found) {
                stack.pop();
                order.add(node);
            }
        }
    }

    static void dfs2(int start, int sid) {
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(start);

        while (!stack.isEmpty()) {
            int u = stack.pop();
            if (sccId[u] != -1) continue;
            sccId[u] = sid;

            for (int v : radj[u]) {
                if (sccId[v] == -1) {
                    stack.push(v);
                }
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
using namespace std;

vector<int> adj[4002], radj[4002];
bool visited[4002];
int sccId[4002];
vector<int> order;
int numVars;

int var(bool isRow, int idx, bool dir, int n) {
    int base = isRow ? idx : n + idx;
    return 2 * base + (dir ? 1 : 0);
}

int neg(int v) {
    return v ^ 1;
}

void addEdge(int u, int v) {
    adj[u].push_back(v);
    radj[v].push_back(u);
}

void addMust(int a) {
    addEdge(neg(a), a);
}

void dfs1(int start) {
    stack<pair<int,int>> st;
    st.push({start, 0});

    while (!st.empty()) {
        int node = st.top().first;
        int& idx = st.top().second;

        if (!visited[node]) {
            visited[node] = true;
        }

        bool found = false;
        while (idx < adj[node].size()) {
            int v = adj[node][idx++];
            if (!visited[v]) {
                st.push({v, 0});
                found = true;
                break;
            }
        }

        if (!found) {
            st.pop();
            order.push_back(node);
        }
    }
}

void dfs2(int start, int sid) {
    stack<int> st;
    st.push(start);

    while (!st.empty()) {
        int u = st.top();
        st.pop();
        if (sccId[u] != -1) continue;
        sccId[u] = sid;

        for (int v : radj[u]) {
            if (sccId[v] == -1) {
                st.push(v);
            }
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int n, m, k;
        cin >> n >> m >> k;

        numVars = 2 * (n + m);
        for (int i = 0; i < numVars; i++) {
            adj[i].clear();
            radj[i].clear();
            visited[i] = false;
            sccId[i] = -1;
        }
        order.clear();

        for (int i = 0; i < k; i++) {
            int a, b, c, d;
            cin >> a >> b >> c >> d;

            if (a == c && b == d) continue;

            if (a == c) {
                addMust(var(true, a, b < d, n));
            } else if (b == d) {
                addMust(var(false, b, a < c, n));
            } else {
                int p1Row = var(true, a, d > b, n);
                int p1Col = var(false, d, c > a, n);
                int p2Col = var(false, b, c > a, n);
                int p2Row = var(true, c, d > b, n);

                addEdge(neg(p1Row), p2Col);
                addEdge(neg(p1Row), p2Row);
                addEdge(neg(p1Col), p2Col);
                addEdge(neg(p1Col), p2Row);
                addEdge(neg(p2Col), p1Row);
                addEdge(neg(p2Col), p1Col);
                addEdge(neg(p2Row), p1Row);
                addEdge(neg(p2Row), p1Col);
            }
        }

        for (int i = 0; i < numVars; i++) {
            if (!visited[i]) dfs1(i);
        }

        int sccNum = 0;
        for (int i = numVars - 1; i >= 0; i--) {
            int u = order[i];
            if (sccId[u] == -1) {
                dfs2(u, sccNum++);
            }
        }

        bool valid = true;
        for (int i = 0; i < n + m; i++) {
            if (sccId[2*i] == sccId[2*i + 1]) {
                valid = false;
                break;
            }
        }

        cout << (valid ? "Yes" : "No") << "\\n";
    }
    return 0;
}
'''
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
            solutions = []
            for lang in ["python", "java", "cpp"]:
                if lang in SOLUTIONS[original_id]:
                    solutions.append({
                        "language": lang,
                        "code": SOLUTIONS[original_id][lang]
                    })
            problem["solutions"] = solutions
            updated_count += 1
            print(f"Updated problem {original_id}")

    print(f"\nUpdated {updated_count} problems")
    print("Saving checkpoint file...")

    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Done!")

if __name__ == "__main__":
    main()
