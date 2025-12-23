#!/usr/bin/env python3
"""
Generate solutions for Baekjoon problems 1700-1799
"""

import json
import re

CHECKPOINT_FILE = "/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json"

# Solutions for problems 1700-1709
SOLUTIONS = {
    "1700": {
        "python": '''import sys
input = sys.stdin.readline

n, k = map(int, input().split())
order = list(map(int, input().split()))

plugged = []
count = 0

for i in range(k):
    device = order[i]
    if device in plugged:
        continue
    if len(plugged) < n:
        plugged.append(device)
    else:
        # Find which device to unplug
        # Unplug the one that will be used latest or not at all
        latest_idx = -1
        to_remove = 0
        for p in plugged:
            if p not in order[i+1:]:
                to_remove = p
                break
            else:
                idx = order[i+1:].index(p)
                if idx > latest_idx:
                    latest_idx = idx
                    to_remove = p
        plugged.remove(to_remove)
        plugged.append(device)
        count += 1

print(count)''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int k = sc.nextInt();
        int[] order = new int[k];
        for (int i = 0; i < k; i++) {
            order[i] = sc.nextInt();
        }

        ArrayList<Integer> plugged = new ArrayList<>();
        int count = 0;

        for (int i = 0; i < k; i++) {
            int device = order[i];
            if (plugged.contains(device)) continue;

            if (plugged.size() < n) {
                plugged.add(device);
            } else {
                int latestIdx = -1;
                int toRemove = plugged.get(0);

                for (int p : plugged) {
                    int nextUse = -1;
                    for (int j = i + 1; j < k; j++) {
                        if (order[j] == p) {
                            nextUse = j;
                            break;
                        }
                    }
                    if (nextUse == -1) {
                        toRemove = p;
                        break;
                    }
                    if (nextUse > latestIdx) {
                        latestIdx = nextUse;
                        toRemove = p;
                    }
                }
                plugged.remove(Integer.valueOf(toRemove));
                plugged.add(device);
                count++;
            }
        }
        System.out.println(count);
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    vector<int> order(k);
    for (int i = 0; i < k; i++) {
        cin >> order[i];
    }

    vector<int> plugged;
    int count = 0;

    for (int i = 0; i < k; i++) {
        int device = order[i];
        if (find(plugged.begin(), plugged.end(), device) != plugged.end()) {
            continue;
        }

        if (plugged.size() < n) {
            plugged.push_back(device);
        } else {
            int latestIdx = -1;
            int toRemove = 0;

            for (int p : plugged) {
                int nextUse = -1;
                for (int j = i + 1; j < k; j++) {
                    if (order[j] == p) {
                        nextUse = j;
                        break;
                    }
                }
                if (nextUse == -1) {
                    toRemove = p;
                    break;
                }
                if (nextUse > latestIdx) {
                    latestIdx = nextUse;
                    toRemove = p;
                }
            }
            plugged.erase(find(plugged.begin(), plugged.end(), toRemove));
            plugged.push_back(device);
            count++;
        }
    }
    cout << count << endl;
    return 0;
}'''
    },
    "1701": {
        "python": '''import sys
input = sys.stdin.readline

def compute_lps(s):
    n = len(s)
    lps = [0] * n
    length = 0
    i = 1
    max_len = 0
    while i < n:
        if s[i] == s[length]:
            length += 1
            lps[i] = length
            max_len = max(max_len, length)
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return max_len

s = input().strip()
result = 0
for i in range(len(s)):
    result = max(result, compute_lps(s[i:]))
print(result)''',
        "java": '''import java.util.*;

public class Main {
    public static int computeLPS(String s) {
        int n = s.length();
        int[] lps = new int[n];
        int length = 0;
        int i = 1;
        int maxLen = 0;

        while (i < n) {
            if (s.charAt(i) == s.charAt(length)) {
                length++;
                lps[i] = length;
                maxLen = Math.max(maxLen, length);
                i++;
            } else {
                if (length != 0) {
                    length = lps[length - 1];
                } else {
                    lps[i] = 0;
                    i++;
                }
            }
        }
        return maxLen;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        int result = 0;

        for (int i = 0; i < s.length(); i++) {
            result = Math.max(result, computeLPS(s.substring(i)));
        }
        System.out.println(result);
    }
}''',
        "cpp": '''#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int computeLPS(const string& s) {
    int n = s.length();
    if (n == 0) return 0;

    int* lps = new int[n]();
    int length = 0;
    int i = 1;
    int maxLen = 0;

    while (i < n) {
        if (s[i] == s[length]) {
            length++;
            lps[i] = length;
            maxLen = max(maxLen, length);
            i++;
        } else {
            if (length != 0) {
                length = lps[length - 1];
            } else {
                lps[i] = 0;
                i++;
            }
        }
    }
    delete[] lps;
    return maxLen;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    cin >> s;

    int result = 0;
    for (int i = 0; i < s.length(); i++) {
        result = max(result, computeLPS(s.substr(i)));
    }
    cout << result << endl;
    return 0;
}'''
    },
    "1702": {
        "python": '''import sys
from collections import defaultdict
import heapq

input = sys.stdin.readline

def solve():
    n, m, s, e = map(int, input().split())
    graph = defaultdict(list)

    for _ in range(m):
        p, r, c, t = map(int, input().split())
        graph[p].append((r, c, t))
        graph[r].append((p, c, t))

    # dp[node] = set of (cost, time) pairs that are Pareto optimal
    INF = float('inf')
    dist = defaultdict(lambda: [])

    # (cost, time, node)
    pq = [(0, 0, s)]

    while pq:
        cost, time, node = heapq.heappop(pq)

        # Check if dominated
        dominated = False
        for c2, t2 in dist[node]:
            if c2 <= cost and t2 <= time:
                dominated = True
                break
        if dominated:
            continue

        # Remove dominated entries and add new one
        new_list = [(c2, t2) for c2, t2 in dist[node] if not (cost <= c2 and time <= t2)]
        new_list.append((cost, time))
        dist[node] = new_list

        for next_node, c, t in graph[node]:
            new_cost = cost + c
            new_time = time + t

            # Check if new state is dominated
            dominated = False
            for c2, t2 in dist[next_node]:
                if c2 <= new_cost and t2 <= new_time:
                    dominated = True
                    break
            if not dominated:
                heapq.heappush(pq, (new_cost, new_time, next_node))

    # Filter Pareto optimal solutions at destination
    result = []
    for c, t in dist[e]:
        dominated = False
        for c2, t2 in dist[e]:
            if (c2 < c and t2 <= t) or (c2 <= c and t2 < t):
                dominated = True
                break
        if not dominated:
            result.append((c, t))

    # Remove duplicates
    result = list(set(result))
    print(len(result))

solve()''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int s = sc.nextInt();
        int e = sc.nextInt();

        List<int[]>[] graph = new ArrayList[n + 1];
        for (int i = 0; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < m; i++) {
            int p = sc.nextInt();
            int r = sc.nextInt();
            int c = sc.nextInt();
            int t = sc.nextInt();
            graph[p].add(new int[]{r, c, t});
            graph[r].add(new int[]{p, c, t});
        }

        List<int[]>[] dist = new ArrayList[n + 1];
        for (int i = 0; i <= n; i++) {
            dist[i] = new ArrayList<>();
        }

        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> {
            if (a[0] != b[0]) return a[0] - b[0];
            return a[1] - b[1];
        });
        pq.add(new int[]{0, 0, s});

        while (!pq.isEmpty()) {
            int[] curr = pq.poll();
            int cost = curr[0], time = curr[1], node = curr[2];

            boolean dominated = false;
            for (int[] pair : dist[node]) {
                if (pair[0] <= cost && pair[1] <= time) {
                    dominated = true;
                    break;
                }
            }
            if (dominated) continue;

            List<int[]> newList = new ArrayList<>();
            for (int[] pair : dist[node]) {
                if (!(cost <= pair[0] && time <= pair[1])) {
                    newList.add(pair);
                }
            }
            newList.add(new int[]{cost, time});
            dist[node] = newList;

            for (int[] edge : graph[node]) {
                int next = edge[0], c = edge[1], t = edge[2];
                int newCost = cost + c;
                int newTime = time + t;

                boolean dom = false;
                for (int[] pair : dist[next]) {
                    if (pair[0] <= newCost && pair[1] <= newTime) {
                        dom = true;
                        break;
                    }
                }
                if (!dom) {
                    pq.add(new int[]{newCost, newTime, next});
                }
            }
        }

        Set<String> result = new HashSet<>();
        for (int[] pair : dist[e]) {
            boolean dom = false;
            for (int[] other : dist[e]) {
                if ((other[0] < pair[0] && other[1] <= pair[1]) ||
                    (other[0] <= pair[0] && other[1] < pair[1])) {
                    dom = true;
                    break;
                }
            }
            if (!dom) {
                result.add(pair[0] + "," + pair[1]);
            }
        }
        System.out.println(result.size());
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <queue>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, s, e;
    cin >> n >> m >> s >> e;

    vector<vector<tuple<int,int,int>>> graph(n + 1);

    for (int i = 0; i < m; i++) {
        int p, r, c, t;
        cin >> p >> r >> c >> t;
        graph[p].push_back({r, c, t});
        graph[r].push_back({p, c, t});
    }

    vector<vector<pair<int,int>>> dist(n + 1);

    priority_queue<tuple<int,int,int>, vector<tuple<int,int,int>>, greater<>> pq;
    pq.push({0, 0, s});

    while (!pq.empty()) {
        auto [cost, time, node] = pq.top();
        pq.pop();

        bool dominated = false;
        for (auto& [c2, t2] : dist[node]) {
            if (c2 <= cost && t2 <= time) {
                dominated = true;
                break;
            }
        }
        if (dominated) continue;

        vector<pair<int,int>> newList;
        for (auto& [c2, t2] : dist[node]) {
            if (!(cost <= c2 && time <= t2)) {
                newList.push_back({c2, t2});
            }
        }
        newList.push_back({cost, time});
        dist[node] = newList;

        for (auto& [next, c, t] : graph[node]) {
            int newCost = cost + c;
            int newTime = time + t;

            bool dom = false;
            for (auto& [c2, t2] : dist[next]) {
                if (c2 <= newCost && t2 <= newTime) {
                    dom = true;
                    break;
                }
            }
            if (!dom) {
                pq.push({newCost, newTime, next});
            }
        }
    }

    set<pair<int,int>> result;
    for (auto& [c, t] : dist[e]) {
        bool dom = false;
        for (auto& [c2, t2] : dist[e]) {
            if ((c2 < c && t2 <= t) || (c2 <= c && t2 < t)) {
                dom = true;
                break;
            }
        }
        if (!dom) {
            result.insert({c, t});
        }
    }
    cout << result.size() << endl;
    return 0;
}'''
    },
    "1703": {
        "python": '''import sys
input = sys.stdin.readline

while True:
    line = input().split()
    a = int(line[0])
    if a == 0:
        break

    leaves = 1
    idx = 1
    for level in range(a):
        split_factor = int(line[idx])
        pruned = int(line[idx + 1])
        idx += 2
        leaves = leaves * split_factor - pruned

    print(leaves)''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        while (true) {
            int a = sc.nextInt();
            if (a == 0) break;

            long leaves = 1;
            for (int level = 0; level < a; level++) {
                int splitFactor = sc.nextInt();
                int pruned = sc.nextInt();
                leaves = leaves * splitFactor - pruned;
            }
            System.out.println(leaves);
        }
    }
}''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int a;
    while (cin >> a && a != 0) {
        long long leaves = 1;
        for (int level = 0; level < a; level++) {
            int splitFactor, pruned;
            cin >> splitFactor >> pruned;
            leaves = leaves * splitFactor - pruned;
        }
        cout << leaves << endl;
    }
    return 0;
}'''
    },
    "1704": {
        "python": '''import sys
input = sys.stdin.readline

def solve():
    m, n = map(int, input().split())
    grid = []
    for _ in range(m):
        grid.append(list(map(int, input().split())))

    dx = [0, 0, 1, -1, 0]
    dy = [1, -1, 0, 0, 0]

    def flip(g, i, j):
        for k in range(5):
            ni, nj = i + dx[k], j + dy[k]
            if 0 <= ni < m and 0 <= nj < n:
                g[ni][nj] ^= 1

    def try_solve(first_row_mask):
        g = [row[:] for row in grid]
        result = [[0] * n for _ in range(m)]

        # Apply first row mask
        for j in range(n):
            if (first_row_mask >> j) & 1:
                flip(g, 0, j)
                result[0][j] = 1

        # For each subsequent row, flip to turn off previous row
        for i in range(1, m):
            for j in range(n):
                if g[i-1][j] == 1:
                    flip(g, i, j)
                    result[i][j] = 1

        # Check if last row is all zeros
        if all(g[m-1][j] == 0 for j in range(n)):
            return result
        return None

    best = None
    for mask in range(1 << n):
        result = try_solve(mask)
        if result is not None:
            if best is None:
                best = result
            else:
                # Compare lexicographically
                for i in range(m):
                    for j in range(n):
                        if result[i][j] < best[i][j]:
                            best = result
                            break
                        elif result[i][j] > best[i][j]:
                            break
                    else:
                        continue
                    break

    if best is None:
        print("IMPOSSIBLE")
    else:
        for row in best:
            print(' '.join(map(str, row)))

solve()''',
        "java": '''import java.util.*;

public class Main {
    static int m, n;
    static int[] dx = {0, 0, 1, -1, 0};
    static int[] dy = {1, -1, 0, 0, 0};

    static void flip(int[][] g, int i, int j) {
        for (int k = 0; k < 5; k++) {
            int ni = i + dx[k], nj = j + dy[k];
            if (ni >= 0 && ni < m && nj >= 0 && nj < n) {
                g[ni][nj] ^= 1;
            }
        }
    }

    static int[][] trySolve(int[][] grid, int mask) {
        int[][] g = new int[m][n];
        for (int i = 0; i < m; i++) {
            g[i] = grid[i].clone();
        }
        int[][] result = new int[m][n];

        for (int j = 0; j < n; j++) {
            if (((mask >> j) & 1) == 1) {
                flip(g, 0, j);
                result[0][j] = 1;
            }
        }

        for (int i = 1; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (g[i-1][j] == 1) {
                    flip(g, i, j);
                    result[i][j] = 1;
                }
            }
        }

        for (int j = 0; j < n; j++) {
            if (g[m-1][j] != 0) return null;
        }
        return result;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        m = sc.nextInt();
        n = sc.nextInt();
        int[][] grid = new int[m][n];

        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                grid[i][j] = sc.nextInt();
            }
        }

        int[][] best = null;
        for (int mask = 0; mask < (1 << n); mask++) {
            int[][] result = trySolve(grid, mask);
            if (result != null) {
                if (best == null) {
                    best = result;
                } else {
                    outer:
                    for (int i = 0; i < m; i++) {
                        for (int j = 0; j < n; j++) {
                            if (result[i][j] < best[i][j]) {
                                best = result;
                                break outer;
                            } else if (result[i][j] > best[i][j]) {
                                break outer;
                            }
                        }
                    }
                }
            }
        }

        if (best == null) {
            System.out.println("IMPOSSIBLE");
        } else {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < m; i++) {
                for (int j = 0; j < n; j++) {
                    if (j > 0) sb.append(" ");
                    sb.append(best[i][j]);
                }
                sb.append("\\n");
            }
            System.out.print(sb);
        }
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
using namespace std;

int m, n;
int dx[] = {0, 0, 1, -1, 0};
int dy[] = {1, -1, 0, 0, 0};

void flip(vector<vector<int>>& g, int i, int j) {
    for (int k = 0; k < 5; k++) {
        int ni = i + dx[k], nj = j + dy[k];
        if (ni >= 0 && ni < m && nj >= 0 && nj < n) {
            g[ni][nj] ^= 1;
        }
    }
}

vector<vector<int>> trySolve(vector<vector<int>>& grid, int mask) {
    vector<vector<int>> g = grid;
    vector<vector<int>> result(m, vector<int>(n, 0));

    for (int j = 0; j < n; j++) {
        if ((mask >> j) & 1) {
            flip(g, 0, j);
            result[0][j] = 1;
        }
    }

    for (int i = 1; i < m; i++) {
        for (int j = 0; j < n; j++) {
            if (g[i-1][j] == 1) {
                flip(g, i, j);
                result[i][j] = 1;
            }
        }
    }

    for (int j = 0; j < n; j++) {
        if (g[m-1][j] != 0) return {};
    }
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> m >> n;
    vector<vector<int>> grid(m, vector<int>(n));

    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            cin >> grid[i][j];
        }
    }

    vector<vector<int>> best;
    for (int mask = 0; mask < (1 << n); mask++) {
        vector<vector<int>> result = trySolve(grid, mask);
        if (!result.empty()) {
            if (best.empty()) {
                best = result;
            } else {
                for (int i = 0; i < m; i++) {
                    bool updated = false;
                    for (int j = 0; j < n; j++) {
                        if (result[i][j] < best[i][j]) {
                            best = result;
                            updated = true;
                            break;
                        } else if (result[i][j] > best[i][j]) {
                            updated = true;
                            break;
                        }
                    }
                    if (updated) break;
                }
            }
        }
    }

    if (best.empty()) {
        cout << "IMPOSSIBLE" << endl;
    } else {
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (j > 0) cout << " ";
                cout << best[i][j];
            }
            cout << "\\n";
        }
    }
    return 0;
}'''
    },
    "1705": {
        "python": '''import sys
from collections import deque

input = sys.stdin.readline

def solve():
    n = int(input())
    A = [0] * (n + 1)
    B = [0] * (n + 1)

    for i in range(1, n + 1):
        a, b = map(int, input().split())
        A[i] = a
        B[i] = b

    # BFS to find sequence
    # State: frozenset of all possible positions
    initial = frozenset(range(1, n + 1))
    target = frozenset([1])

    queue = deque([(initial, "")])
    visited = {initial}

    while queue:
        state, seq = queue.popleft()

        if state == target:
            print(seq)
            return

        if len(seq) >= 10000:
            continue

        # Try 'A'
        next_a = frozenset(A[i] for i in state)
        if next_a not in visited:
            visited.add(next_a)
            queue.append((next_a, seq + "A"))

        # Try 'B'
        next_b = frozenset(B[i] for i in state)
        if next_b not in visited:
            visited.add(next_b)
            queue.append((next_b, seq + "B"))

solve()''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] A = new int[n + 1];
        int[] B = new int[n + 1];

        for (int i = 1; i <= n; i++) {
            A[i] = sc.nextInt();
            B[i] = sc.nextInt();
        }

        Set<Integer> initial = new HashSet<>();
        for (int i = 1; i <= n; i++) initial.add(i);

        Set<Integer> target = new HashSet<>();
        target.add(1);

        Queue<Object[]> queue = new LinkedList<>();
        queue.add(new Object[]{initial, ""});
        Set<Set<Integer>> visited = new HashSet<>();
        visited.add(initial);

        while (!queue.isEmpty()) {
            Object[] curr = queue.poll();
            Set<Integer> state = (Set<Integer>) curr[0];
            String seq = (String) curr[1];

            if (state.equals(target)) {
                System.out.println(seq);
                return;
            }

            if (seq.length() >= 10000) continue;

            Set<Integer> nextA = new HashSet<>();
            for (int i : state) nextA.add(A[i]);
            if (!visited.contains(nextA)) {
                visited.add(nextA);
                queue.add(new Object[]{nextA, seq + "A"});
            }

            Set<Integer> nextB = new HashSet<>();
            for (int i : state) nextB.add(B[i]);
            if (!visited.contains(nextB)) {
                visited.add(nextB);
                queue.add(new Object[]{nextB, seq + "B"});
            }
        }
    }
}''',
        "cpp": '''#include <iostream>
#include <set>
#include <queue>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> A(n + 1), B(n + 1);
    for (int i = 1; i <= n; i++) {
        cin >> A[i] >> B[i];
    }

    set<int> initial, target;
    for (int i = 1; i <= n; i++) initial.insert(i);
    target.insert(1);

    queue<pair<set<int>, string>> q;
    q.push({initial, ""});
    map<set<int>, bool> visited;
    visited[initial] = true;

    while (!q.empty()) {
        auto [state, seq] = q.front();
        q.pop();

        if (state == target) {
            cout << seq << endl;
            return 0;
        }

        if (seq.length() >= 10000) continue;

        set<int> nextA, nextB;
        for (int i : state) {
            nextA.insert(A[i]);
            nextB.insert(B[i]);
        }

        if (visited.find(nextA) == visited.end()) {
            visited[nextA] = true;
            q.push({nextA, seq + "A"});
        }

        if (visited.find(nextB) == visited.end()) {
            visited[nextB] = true;
            q.push({nextB, seq + "B"});
        }
    }
    return 0;
}'''
    },
    "1706": {
        "python": '''import sys
input = sys.stdin.readline

r, c = map(int, input().split())
grid = []
for _ in range(r):
    grid.append(input().strip())

words = []

# Horizontal words
for i in range(r):
    word = ""
    for j in range(c):
        if grid[i][j] == '#':
            if len(word) >= 2:
                words.append(word)
            word = ""
        else:
            word += grid[i][j]
    if len(word) >= 2:
        words.append(word)

# Vertical words
for j in range(c):
    word = ""
    for i in range(r):
        if grid[i][j] == '#':
            if len(word) >= 2:
                words.append(word)
            word = ""
        else:
            word += grid[i][j]
    if len(word) >= 2:
        words.append(word)

words.sort()
print(words[0])''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int r = sc.nextInt();
        int c = sc.nextInt();
        sc.nextLine();

        String[] grid = new String[r];
        for (int i = 0; i < r; i++) {
            grid[i] = sc.nextLine();
        }

        List<String> words = new ArrayList<>();

        // Horizontal
        for (int i = 0; i < r; i++) {
            StringBuilder word = new StringBuilder();
            for (int j = 0; j < c; j++) {
                if (grid[i].charAt(j) == '#') {
                    if (word.length() >= 2) {
                        words.add(word.toString());
                    }
                    word = new StringBuilder();
                } else {
                    word.append(grid[i].charAt(j));
                }
            }
            if (word.length() >= 2) {
                words.add(word.toString());
            }
        }

        // Vertical
        for (int j = 0; j < c; j++) {
            StringBuilder word = new StringBuilder();
            for (int i = 0; i < r; i++) {
                if (grid[i].charAt(j) == '#') {
                    if (word.length() >= 2) {
                        words.add(word.toString());
                    }
                    word = new StringBuilder();
                } else {
                    word.append(grid[i].charAt(j));
                }
            }
            if (word.length() >= 2) {
                words.add(word.toString());
            }
        }

        Collections.sort(words);
        System.out.println(words.get(0));
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int r, c;
    cin >> r >> c;

    vector<string> grid(r);
    for (int i = 0; i < r; i++) {
        cin >> grid[i];
    }

    vector<string> words;

    // Horizontal
    for (int i = 0; i < r; i++) {
        string word = "";
        for (int j = 0; j < c; j++) {
            if (grid[i][j] == '#') {
                if (word.length() >= 2) {
                    words.push_back(word);
                }
                word = "";
            } else {
                word += grid[i][j];
            }
        }
        if (word.length() >= 2) {
            words.push_back(word);
        }
    }

    // Vertical
    for (int j = 0; j < c; j++) {
        string word = "";
        for (int i = 0; i < r; i++) {
            if (grid[i][j] == '#') {
                if (word.length() >= 2) {
                    words.push_back(word);
                }
                word = "";
            } else {
                word += grid[i][j];
            }
        }
        if (word.length() >= 2) {
            words.push_back(word);
        }
    }

    sort(words.begin(), words.end());
    cout << words[0] << endl;
    return 0;
}'''
    },
    "1707": {
        "python": '''import sys
from collections import deque
input = sys.stdin.readline
sys.setrecursionlimit(100000)

def solve():
    k = int(input())
    for _ in range(k):
        v, e = map(int, input().split())
        graph = [[] for _ in range(v + 1)]

        for _ in range(e):
            a, b = map(int, input().split())
            graph[a].append(b)
            graph[b].append(a)

        color = [0] * (v + 1)
        is_bipartite = True

        for start in range(1, v + 1):
            if color[start] != 0:
                continue

            queue = deque([start])
            color[start] = 1

            while queue and is_bipartite:
                node = queue.popleft()
                for neighbor in graph[node]:
                    if color[neighbor] == 0:
                        color[neighbor] = -color[node]
                        queue.append(neighbor)
                    elif color[neighbor] == color[node]:
                        is_bipartite = False
                        break

        print("YES" if is_bipartite else "NO")

solve()''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int k = sc.nextInt();

        StringBuilder sb = new StringBuilder();
        while (k-- > 0) {
            int v = sc.nextInt();
            int e = sc.nextInt();

            List<Integer>[] graph = new ArrayList[v + 1];
            for (int i = 0; i <= v; i++) {
                graph[i] = new ArrayList<>();
            }

            for (int i = 0; i < e; i++) {
                int a = sc.nextInt();
                int b = sc.nextInt();
                graph[a].add(b);
                graph[b].add(a);
            }

            int[] color = new int[v + 1];
            boolean isBipartite = true;

            for (int start = 1; start <= v && isBipartite; start++) {
                if (color[start] != 0) continue;

                Queue<Integer> queue = new LinkedList<>();
                queue.add(start);
                color[start] = 1;

                while (!queue.isEmpty() && isBipartite) {
                    int node = queue.poll();
                    for (int neighbor : graph[node]) {
                        if (color[neighbor] == 0) {
                            color[neighbor] = -color[node];
                            queue.add(neighbor);
                        } else if (color[neighbor] == color[node]) {
                            isBipartite = false;
                            break;
                        }
                    }
                }
            }
            sb.append(isBipartite ? "YES" : "NO").append("\\n");
        }
        System.out.print(sb);
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <queue>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int k;
    cin >> k;

    while (k--) {
        int v, e;
        cin >> v >> e;

        vector<vector<int>> graph(v + 1);
        for (int i = 0; i < e; i++) {
            int a, b;
            cin >> a >> b;
            graph[a].push_back(b);
            graph[b].push_back(a);
        }

        vector<int> color(v + 1, 0);
        bool isBipartite = true;

        for (int start = 1; start <= v && isBipartite; start++) {
            if (color[start] != 0) continue;

            queue<int> q;
            q.push(start);
            color[start] = 1;

            while (!q.empty() && isBipartite) {
                int node = q.front();
                q.pop();

                for (int neighbor : graph[node]) {
                    if (color[neighbor] == 0) {
                        color[neighbor] = -color[node];
                        q.push(neighbor);
                    } else if (color[neighbor] == color[node]) {
                        isBipartite = false;
                        break;
                    }
                }
            }
        }
        cout << (isBipartite ? "YES" : "NO") << "\\n";
    }
    return 0;
}'''
    },
    "1708": {
        "python": '''import sys
input = sys.stdin.readline

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def convex_hull(points):
    points = sorted(set(points))
    if len(points) <= 1:
        return points

    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]

n = int(input())
points = []
for _ in range(n):
    x, y = map(int, input().split())
    points.append((x, y))

hull = convex_hull(points)
print(len(hull))''',
        "java": '''import java.util.*;

public class Main {
    static long cross(long[] o, long[] a, long[] b) {
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        long[][] points = new long[n][2];
        for (int i = 0; i < n; i++) {
            points[i][0] = sc.nextLong();
            points[i][1] = sc.nextLong();
        }

        Arrays.sort(points, (a, b) -> {
            if (a[0] != b[0]) return Long.compare(a[0], b[0]);
            return Long.compare(a[1], b[1]);
        });

        // Remove duplicates
        List<long[]> unique = new ArrayList<>();
        for (long[] p : points) {
            if (unique.isEmpty() || unique.get(unique.size()-1)[0] != p[0] || unique.get(unique.size()-1)[1] != p[1]) {
                unique.add(p);
            }
        }

        if (unique.size() <= 1) {
            System.out.println(unique.size());
            return;
        }

        // Build lower hull
        List<long[]> lower = new ArrayList<>();
        for (long[] p : unique) {
            while (lower.size() >= 2 && cross(lower.get(lower.size()-2), lower.get(lower.size()-1), p) <= 0) {
                lower.remove(lower.size() - 1);
            }
            lower.add(p);
        }

        // Build upper hull
        List<long[]> upper = new ArrayList<>();
        for (int i = unique.size() - 1; i >= 0; i--) {
            long[] p = unique.get(i);
            while (upper.size() >= 2 && cross(upper.get(upper.size()-2), upper.get(upper.size()-1), p) <= 0) {
                upper.remove(upper.size() - 1);
            }
            upper.add(p);
        }

        System.out.println(lower.size() - 1 + upper.size() - 1);
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

typedef long long ll;
typedef pair<ll, ll> pll;

ll cross(pll o, pll a, pll b) {
    return (a.first - o.first) * (b.second - o.second) - (a.second - o.second) * (b.first - o.first);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<pll> points(n);
    for (int i = 0; i < n; i++) {
        cin >> points[i].first >> points[i].second;
    }

    sort(points.begin(), points.end());
    points.erase(unique(points.begin(), points.end()), points.end());

    if (points.size() <= 1) {
        cout << points.size() << endl;
        return 0;
    }

    // Build lower hull
    vector<pll> lower;
    for (auto& p : points) {
        while (lower.size() >= 2 && cross(lower[lower.size()-2], lower[lower.size()-1], p) <= 0) {
            lower.pop_back();
        }
        lower.push_back(p);
    }

    // Build upper hull
    vector<pll> upper;
    for (int i = points.size() - 1; i >= 0; i--) {
        while (upper.size() >= 2 && cross(upper[upper.size()-2], upper[upper.size()-1], points[i]) <= 0) {
            upper.pop_back();
        }
        upper.push_back(points[i]);
    }

    cout << lower.size() - 1 + upper.size() - 1 << endl;
    return 0;
}'''
    },
    "1709": {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
r = n // 2

count = 0
prev_y = 0

for x in range(r):
    # Find max y such that x^2 + y^2 <= r^2
    y = prev_y
    while (x + 1) ** 2 + (y + 1) ** 2 <= r * r:
        y += 1

    # Count tiles at this x column
    count += prev_y - y
    prev_y = y

# Multiply by 4 for all quadrants
count *= 4

# Add tiles on axes (x=r/2 and y=r/2 lines)
# For each axis, the circle passes through tiles
axis_count = 0
y = 0
while y < r:
    if y * y < r * r and (y + 1) * (y + 1) > r * r:
        axis_count += 1
    elif y * y <= r * r:
        y_sq = r * r - y * y
        if y_sq > 0:
            axis_count += 1
    y += 1

# Actually, let me recalculate properly
# A tile at position (i,j) (0-indexed from center) is touched by circle
# if the circle passes through it

n = int(input()) if False else n
r = n // 2

count = 0
prev_y = r

for x in range(r):
    # Find the y value where circle exits this column
    y = prev_y
    while y > 0 and x * x + y * y > r * r:
        y -= 1
    while y < r and (x + 1) ** 2 + (y + 1) ** 2 <= r * r:
        y += 1

    # The circle passes through tiles from y to prev_y at column x
    if prev_y > y:
        count += prev_y - y
    count += 1  # The tile where circle enters/exits
    prev_y = y

print(count * 4)''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long n = sc.nextLong();
        long r = n / 2;

        long count = 0;
        long prevY = r;

        for (long x = 0; x < r; x++) {
            // Find y where x^2 + y^2 = r^2
            long y = prevY;
            while (y > 0 && x * x + y * y > r * r) {
                y--;
            }

            // Count tiles in this column that circle passes through
            count += prevY - y;
            prevY = y;
        }

        System.out.println(count * 4);
    }
}''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n;
    cin >> n;
    long long r = n / 2;

    long long count = 0;
    long long prevY = r;

    for (long long x = 0; x < r; x++) {
        long long y = prevY;
        while (y > 0 && x * x + y * y > r * r) {
            y--;
        }

        count += prevY - y;
        prevY = y;
    }

    cout << count * 4 << endl;
    return 0;
}'''
    }
}

def main():
    print("Loading checkpoint file...")
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total problems: {len(data)}")

    # Find problems in range 1700-1709
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

    # Save back
    print("Saving checkpoint file...")
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Done!")

if __name__ == "__main__":
    main()
