#!/usr/bin/env python3
"""
Generate solutions for Baekjoon problems 1740-1749
"""

import json

CHECKPOINT_FILE = "/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json"

SOLUTIONS = {
    "1740": {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())

# N-th number that can be represented as sum of distinct powers of 3
# This is equivalent to converting N to binary and then interpreting
# each bit as whether to include that power of 3

result = 0
power = 1
while n > 0:
    if n & 1:
        result += power
    power *= 3
    n >>= 1

print(result)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long n = sc.nextLong();

        long result = 0;
        long power = 1;
        while (n > 0) {
            if ((n & 1) == 1) {
                result += power;
            }
            power *= 3;
            n >>= 1;
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n;
    cin >> n;

    long long result = 0;
    long long power = 1;
    while (n > 0) {
        if (n & 1) {
            result += power;
        }
        power *= 3;
        n >>= 1;
    }

    cout << result << endl;
    return 0;
}
'''
    },
    "1741": {
        "python": '''import sys
from collections import defaultdict
input = sys.stdin.readline

def solve():
    n, m = map(int, input().split())

    # Build complement graph - edges represent students who DON'T know each other
    knows = defaultdict(set)
    for _ in range(m):
        a, b = map(int, input().split())
        knows[a].add(b)
        knows[b].add(a)

    # Find cliques in complement graph = independent sets in original graph
    # This is equivalent to finding connected components in complement graph
    # where each component forms a valid class

    # Use BFS/DFS on complement graph
    # Two students can be in same class only if they know each other
    # So we need to partition into groups where everyone in group knows everyone else (clique)

    # Actually, the problem asks for maximum partition where
    # students in different classes must know each other
    # This means students in same class can NOT know each other (or can)

    # Re-reading: "Different class students must know each other"
    # So within same class, no restriction
    # But across classes, all pairs must know each other

    # This means we need to find partition where the induced graph between classes is complete
    # Each class is an independent set in the complement graph

    # We need to find connected components in complement graph
    all_students = set(range(1, n + 1))

    visited = [False] * (n + 1)
    components = []

    for start in range(1, n + 1):
        if visited[start]:
            continue

        # BFS in complement graph
        component = []
        remaining = set(range(1, n + 1))
        remaining.discard(start)

        queue = [start]
        visited[start] = True
        component.append(start)

        while queue:
            u = queue.pop(0)
            # Find all unvisited nodes NOT connected to u (complement edges)
            new_remaining = set()
            for v in remaining:
                if v not in knows[u]:  # Not connected in original = connected in complement
                    if not visited[v]:
                        visited[v] = True
                        component.append(v)
                        queue.append(v)
                else:
                    new_remaining.add(v)
            remaining = new_remaining

        components.append(len(component))

    components.sort()
    print(len(components))
    print(' '.join(map(str, components)))

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();

        Set<Integer>[] knows = new HashSet[n + 1];
        for (int i = 0; i <= n; i++) {
            knows[i] = new HashSet<>();
        }

        for (int i = 0; i < m; i++) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            knows[a].add(b);
            knows[b].add(a);
        }

        boolean[] visited = new boolean[n + 1];
        List<Integer> components = new ArrayList<>();

        for (int start = 1; start <= n; start++) {
            if (visited[start]) continue;

            List<Integer> component = new ArrayList<>();
            Set<Integer> remaining = new HashSet<>();
            for (int i = 1; i <= n; i++) {
                if (i != start) remaining.add(i);
            }

            Queue<Integer> queue = new LinkedList<>();
            queue.add(start);
            visited[start] = true;
            component.add(start);

            while (!queue.isEmpty()) {
                int u = queue.poll();
                Set<Integer> newRemaining = new HashSet<>();
                for (int v : remaining) {
                    if (!knows[u].contains(v)) {
                        if (!visited[v]) {
                            visited[v] = true;
                            component.add(v);
                            queue.add(v);
                        }
                    } else {
                        newRemaining.add(v);
                    }
                }
                remaining = newRemaining;
            }

            components.add(component.size());
        }

        Collections.sort(components);
        System.out.println(components.size());
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < components.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(components.get(i));
        }
        System.out.println(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <set>
#include <queue>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<set<int>> knows(n + 1);

    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        knows[a].insert(b);
        knows[b].insert(a);
    }

    vector<bool> visited(n + 1, false);
    vector<int> components;

    for (int start = 1; start <= n; start++) {
        if (visited[start]) continue;

        vector<int> component;
        set<int> remaining;
        for (int i = 1; i <= n; i++) {
            if (i != start) remaining.insert(i);
        }

        queue<int> q;
        q.push(start);
        visited[start] = true;
        component.push_back(start);

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            set<int> newRemaining;
            for (int v : remaining) {
                if (knows[u].find(v) == knows[u].end()) {
                    if (!visited[v]) {
                        visited[v] = true;
                        component.push_back(v);
                        q.push(v);
                    }
                } else {
                    newRemaining.insert(v);
                }
            }
            remaining = newRemaining;
        }

        components.push_back(component.size());
    }

    sort(components.begin(), components.end());
    cout << components.size() << "\\n";
    for (int i = 0; i < components.size(); i++) {
        if (i > 0) cout << " ";
        cout << components[i];
    }
    cout << "\\n";
    return 0;
}
'''
    },
    "1742": {
        "python": '''import sys
from collections import defaultdict, deque
input = sys.stdin.readline

MOD = 1000003

def solve():
    n = int(input())
    m = int(input())

    # wins[a] = set of b such that a beats b
    wins = defaultdict(set)

    for _ in range(m):
        a, b = map(int, input().split())
        wins[a].add(b)

    # Build transitive closure
    for k in range(1, n + 1):
        for i in range(1, n + 1):
            if k in wins[i]:
                for j in wins[k]:
                    wins[i].add(j)

    # Check for contradiction: if a beats b and b beats a
    for i in range(1, n + 1):
        if i in wins[i]:
            print(0)
            return

    for i in range(1, n + 1):
        for j in wins[i]:
            if i in wins[j]:
                print(0)
                return

    # Count topological orderings
    # dp[mask] = number of ways to arrange cars in mask
    # But n can be up to 30, so we can't use bitmask

    # Use DP on the DAG
    # dp[i][S] = number of ways to place first i cars, where S is the set of placed cars

    # For small m, we can use inclusion-exclusion or count directly
    # Actually, we need to count linear extensions of the partial order

    # For n up to 30, we need efficient algorithm
    # Use DP with topological considerations

    # in_degree[i] = number of constraints where i must come after someone
    in_degree = [0] * (n + 1)
    for i in range(1, n + 1):
        for j in wins[i]:
            in_degree[j] += 1

    # Actually, let's use a different approach
    # The number of linear extensions can be computed with DP

    # Simple approach for small graphs:
    # Count permutations that respect the partial order

    # For this problem, since m <= 15, we can use the formula
    # Result = n! / product of (1 + number of descendants) for each chain

    # Let's use memoization with tuple of remaining elements
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def count_orderings(remaining):
        if not remaining:
            return 1

        result = 0
        remaining_set = set(remaining)

        for car in remaining:
            # Check if car can be placed first (no car in remaining beats it)
            can_place = True
            for other in remaining:
                if other != car and car in wins[other]:
                    can_place = False
                    break

            if can_place:
                new_remaining = tuple(c for c in remaining if c != car)
                result = (result + count_orderings(new_remaining)) % MOD

        return result

    result = count_orderings(tuple(range(1, n + 1)))
    print(result)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    static int MOD = 1000003;
    static Set<Integer>[] wins;
    static int n;
    static Map<Long, Long> memo = new HashMap<>();

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();
        int m = sc.nextInt();

        wins = new HashSet[n + 1];
        for (int i = 0; i <= n; i++) {
            wins[i] = new HashSet<>();
        }

        for (int i = 0; i < m; i++) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            wins[a].add(b);
        }

        // Build transitive closure
        for (int k = 1; k <= n; k++) {
            for (int i = 1; i <= n; i++) {
                if (wins[i].contains(k)) {
                    for (int j : wins[k]) {
                        wins[i].add(j);
                    }
                }
            }
        }

        // Check for contradiction
        for (int i = 1; i <= n; i++) {
            if (wins[i].contains(i)) {
                System.out.println(0);
                return;
            }
            for (int j : wins[i]) {
                if (wins[j].contains(i)) {
                    System.out.println(0);
                    return;
                }
            }
        }

        long mask = (1L << n) - 1;
        System.out.println(countOrderings(mask));
    }

    static long countOrderings(long remaining) {
        if (remaining == 0) return 1;
        if (memo.containsKey(remaining)) return memo.get(remaining);

        long result = 0;
        for (int car = 1; car <= n; car++) {
            if ((remaining & (1L << (car - 1))) == 0) continue;

            boolean canPlace = true;
            for (int other = 1; other <= n; other++) {
                if (other != car && (remaining & (1L << (other - 1))) != 0) {
                    if (wins[other].contains(car)) {
                        canPlace = false;
                        break;
                    }
                }
            }

            if (canPlace) {
                long newRemaining = remaining ^ (1L << (car - 1));
                result = (result + countOrderings(newRemaining)) % MOD;
            }
        }

        memo.put(remaining, result);
        return result;
    }
}
''',
        "cpp": '''#include <iostream>
#include <set>
#include <map>
using namespace std;

const int MOD = 1000003;
set<int> wins[31];
int n;
map<long long, long long> memo;

long long countOrderings(long long remaining) {
    if (remaining == 0) return 1;
    if (memo.count(remaining)) return memo[remaining];

    long long result = 0;
    for (int car = 1; car <= n; car++) {
        if ((remaining & (1LL << (car - 1))) == 0) continue;

        bool canPlace = true;
        for (int other = 1; other <= n; other++) {
            if (other != car && (remaining & (1LL << (other - 1))) != 0) {
                if (wins[other].count(car)) {
                    canPlace = false;
                    break;
                }
            }
        }

        if (canPlace) {
            long long newRemaining = remaining ^ (1LL << (car - 1));
            result = (result + countOrderings(newRemaining)) % MOD;
        }
    }

    memo[remaining] = result;
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int m;
    cin >> n >> m;

    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        wins[a].insert(b);
    }

    // Build transitive closure
    for (int k = 1; k <= n; k++) {
        for (int i = 1; i <= n; i++) {
            if (wins[i].count(k)) {
                for (int j : wins[k]) {
                    wins[i].insert(j);
                }
            }
        }
    }

    // Check for contradiction
    for (int i = 1; i <= n; i++) {
        if (wins[i].count(i)) {
            cout << 0 << endl;
            return 0;
        }
        for (int j : wins[i]) {
            if (wins[j].count(i)) {
                cout << 0 << endl;
                return 0;
            }
        }
    }

    long long mask = (1LL << n) - 1;
    cout << countOrderings(mask) << endl;
    return 0;
}
'''
    },
    "1743": {
        "python": '''import sys
from collections import deque
input = sys.stdin.readline

def solve():
    n, m, k = map(int, input().split())
    grid = [[0] * (m + 1) for _ in range(n + 1)]

    for _ in range(k):
        r, c = map(int, input().split())
        grid[r][c] = 1

    visited = [[False] * (m + 1) for _ in range(n + 1)]
    dr = [0, 0, 1, -1]
    dc = [1, -1, 0, 0]

    max_size = 0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if grid[i][j] == 1 and not visited[i][j]:
                # BFS
                queue = deque([(i, j)])
                visited[i][j] = True
                size = 0

                while queue:
                    r, c = queue.popleft()
                    size += 1

                    for d in range(4):
                        nr, nc = r + dr[d], c + dc[d]
                        if 1 <= nr <= n and 1 <= nc <= m:
                            if grid[nr][nc] == 1 and not visited[nr][nc]:
                                visited[nr][nc] = True
                                queue.append((nr, nc))

                max_size = max(max_size, size)

    print(max_size)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int k = sc.nextInt();

        int[][] grid = new int[n + 1][m + 1];
        boolean[][] visited = new boolean[n + 1][m + 1];

        for (int i = 0; i < k; i++) {
            int r = sc.nextInt();
            int c = sc.nextInt();
            grid[r][c] = 1;
        }

        int[] dr = {0, 0, 1, -1};
        int[] dc = {1, -1, 0, 0};

        int maxSize = 0;

        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= m; j++) {
                if (grid[i][j] == 1 && !visited[i][j]) {
                    Queue<int[]> queue = new LinkedList<>();
                    queue.add(new int[]{i, j});
                    visited[i][j] = true;
                    int size = 0;

                    while (!queue.isEmpty()) {
                        int[] curr = queue.poll();
                        size++;

                        for (int d = 0; d < 4; d++) {
                            int nr = curr[0] + dr[d];
                            int nc = curr[1] + dc[d];
                            if (nr >= 1 && nr <= n && nc >= 1 && nc <= m) {
                                if (grid[nr][nc] == 1 && !visited[nr][nc]) {
                                    visited[nr][nc] = true;
                                    queue.add(new int[]{nr, nc});
                                }
                            }
                        }
                    }

                    maxSize = Math.max(maxSize, size);
                }
            }
        }

        System.out.println(maxSize);
    }
}
''',
        "cpp": '''#include <iostream>
#include <queue>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, k;
    cin >> n >> m >> k;

    int grid[101][101] = {0};
    bool visited[101][101] = {false};

    for (int i = 0; i < k; i++) {
        int r, c;
        cin >> r >> c;
        grid[r][c] = 1;
    }

    int dr[] = {0, 0, 1, -1};
    int dc[] = {1, -1, 0, 0};

    int maxSize = 0;

    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= m; j++) {
            if (grid[i][j] == 1 && !visited[i][j]) {
                queue<pair<int,int>> q;
                q.push({i, j});
                visited[i][j] = true;
                int size = 0;

                while (!q.empty()) {
                    auto [r, c] = q.front();
                    q.pop();
                    size++;

                    for (int d = 0; d < 4; d++) {
                        int nr = r + dr[d];
                        int nc = c + dc[d];
                        if (nr >= 1 && nr <= n && nc >= 1 && nc <= m) {
                            if (grid[nr][nc] == 1 && !visited[nr][nc]) {
                                visited[nr][nc] = true;
                                q.push({nr, nc});
                            }
                        }
                    }
                }

                maxSize = max(maxSize, size);
            }
        }
    }

    cout << maxSize << endl;
    return 0;
}
'''
    },
    "1744": {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
nums = [int(input()) for _ in range(n)]

# Separate into positive (>1), ones, zero/negative
positive = sorted([x for x in nums if x > 1], reverse=True)
ones = [x for x in nums if x == 1]
non_positive = sorted([x for x in nums if x <= 0])

result = 0

# For positive numbers > 1, pair largest with second largest
i = 0
while i + 1 < len(positive):
    result += positive[i] * positive[i + 1]
    i += 2
if i < len(positive):
    result += positive[i]

# Add all ones (better to add than multiply)
result += len(ones)

# For non-positive, pair smallest (most negative) together
i = 0
while i + 1 < len(non_positive):
    result += non_positive[i] * non_positive[i + 1]
    i += 2
if i < len(non_positive):
    result += non_positive[i]

print(result)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        List<Integer> positive = new ArrayList<>();
        List<Integer> nonPositive = new ArrayList<>();
        int ones = 0;

        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();
            if (x > 1) positive.add(x);
            else if (x == 1) ones++;
            else nonPositive.add(x);
        }

        Collections.sort(positive, Collections.reverseOrder());
        Collections.sort(nonPositive);

        long result = 0;

        int i = 0;
        while (i + 1 < positive.size()) {
            result += (long) positive.get(i) * positive.get(i + 1);
            i += 2;
        }
        if (i < positive.size()) {
            result += positive.get(i);
        }

        result += ones;

        i = 0;
        while (i + 1 < nonPositive.size()) {
            result += (long) nonPositive.get(i) * nonPositive.get(i + 1);
            i += 2;
        }
        if (i < nonPositive.size()) {
            result += nonPositive.get(i);
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> positive;
    vector<int> nonPositive;
    int ones = 0;

    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        if (x > 1) positive.push_back(x);
        else if (x == 1) ones++;
        else nonPositive.push_back(x);
    }

    sort(positive.rbegin(), positive.rend());
    sort(nonPositive.begin(), nonPositive.end());

    long long result = 0;

    int i = 0;
    while (i + 1 < positive.size()) {
        result += (long long) positive[i] * positive[i + 1];
        i += 2;
    }
    if (i < positive.size()) {
        result += positive[i];
    }

    result += ones;

    i = 0;
    while (i + 1 < nonPositive.size()) {
        result += (long long) nonPositive[i] * nonPositive[i + 1];
        i += 2;
    }
    if (i < nonPositive.size()) {
        result += nonPositive[i];
    }

    cout << result << endl;
    return 0;
}
'''
    },
    "1745": {
        "python": '''import sys
from collections import defaultdict
input = sys.stdin.readline

INF = float('inf')

def solve():
    f, p = map(int, input().split())

    current = []
    capacity = []
    for _ in range(f):
        c, cap = map(int, input().split())
        current.append(c)
        capacity.append(cap)

    total_students = sum(current)
    total_capacity = sum(capacity)

    if total_students > total_capacity:
        print(-1)
        return

    edges = []
    graph = defaultdict(list)

    for _ in range(p):
        a, b, t = map(int, input().split())
        a -= 1
        b -= 1
        graph[a].append((b, t))
        graph[b].append((a, t))
        edges.append(t)

    edges = sorted(set(edges))

    # Floyd-Warshall to find all pairs shortest paths
    dist = [[INF] * f for _ in range(f)]
    for i in range(f):
        dist[i][i] = 0

    for u in range(f):
        for v, t in graph[u]:
            dist[u][v] = min(dist[u][v], t)

    for k in range(f):
        for i in range(f):
            for j in range(f):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Binary search on the answer
    def can_distribute(max_time):
        # Build flow network where edge exists if dist[i][j] <= max_time
        # Use simple greedy/flow approach

        # Simple bipartite matching approach
        # Source connects to rooms with excess students
        # Sink connects from rooms with capacity

        from collections import deque

        # Build flow graph
        # Node 0 = source
        # Nodes 1 to f = rooms (supply side)
        # Nodes f+1 to 2f = rooms (demand side)
        # Node 2f+1 = sink

        n = 2 * f + 2
        source = 0
        sink = 2 * f + 1

        cap = [[0] * n for _ in range(n)]

        for i in range(f):
            cap[source][i + 1] = current[i]
            cap[f + 1 + i][sink] = capacity[i]

        for i in range(f):
            for j in range(f):
                if dist[i][j] <= max_time:
                    cap[i + 1][f + 1 + j] = INF

        # Max flow using BFS
        def bfs():
            parent = [-1] * n
            visited = [False] * n
            queue = deque([source])
            visited[source] = True

            while queue:
                u = queue.popleft()
                for v in range(n):
                    if not visited[v] and cap[u][v] > 0:
                        visited[v] = True
                        parent[v] = u
                        if v == sink:
                            return parent
                        queue.append(v)
            return None

        max_flow = 0
        while True:
            parent = bfs()
            if parent is None:
                break

            # Find min capacity along path
            path_flow = INF
            v = sink
            while v != source:
                u = parent[v]
                path_flow = min(path_flow, cap[u][v])
                v = u

            # Update capacities
            v = sink
            while v != source:
                u = parent[v]
                cap[u][v] -= path_flow
                cap[v][u] += path_flow
                v = u

            max_flow += path_flow

        return max_flow >= total_students

    # Get all possible time values
    all_times = set([0])
    for i in range(f):
        for j in range(f):
            if dist[i][j] != INF:
                all_times.add(dist[i][j])

    all_times = sorted(all_times)

    # Binary search
    left, right = 0, len(all_times) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2
        if can_distribute(all_times[mid]):
            result = all_times[mid]
            right = mid - 1
        else:
            left = mid + 1

    print(result)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    static int f;
    static long[][] dist;
    static int[] current, capacity;
    static final long INF = Long.MAX_VALUE / 2;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        f = sc.nextInt();
        int p = sc.nextInt();

        current = new int[f];
        capacity = new int[f];
        int totalStudents = 0, totalCapacity = 0;

        for (int i = 0; i < f; i++) {
            current[i] = sc.nextInt();
            capacity[i] = sc.nextInt();
            totalStudents += current[i];
            totalCapacity += capacity[i];
        }

        if (totalStudents > totalCapacity) {
            System.out.println(-1);
            return;
        }

        dist = new long[f][f];
        for (int i = 0; i < f; i++) {
            Arrays.fill(dist[i], INF);
            dist[i][i] = 0;
        }

        Set<Long> allTimes = new TreeSet<>();
        allTimes.add(0L);

        for (int i = 0; i < p; i++) {
            int a = sc.nextInt() - 1;
            int b = sc.nextInt() - 1;
            long t = sc.nextLong();
            dist[a][b] = Math.min(dist[a][b], t);
            dist[b][a] = Math.min(dist[b][a], t);
        }

        for (int k = 0; k < f; k++) {
            for (int i = 0; i < f; i++) {
                for (int j = 0; j < f; j++) {
                    if (dist[i][k] + dist[k][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                    }
                }
            }
        }

        for (int i = 0; i < f; i++) {
            for (int j = 0; j < f; j++) {
                if (dist[i][j] != INF) {
                    allTimes.add(dist[i][j]);
                }
            }
        }

        Long[] times = allTimes.toArray(new Long[0]);
        int left = 0, right = times.length - 1;
        long result = -1;

        while (left <= right) {
            int mid = (left + right) / 2;
            if (canDistribute(times[mid], totalStudents)) {
                result = times[mid];
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        }

        System.out.println(result);
    }

    static boolean canDistribute(long maxTime, int totalStudents) {
        int n = 2 * f + 2;
        int source = 0, sink = 2 * f + 1;

        int[][] cap = new int[n][n];

        for (int i = 0; i < f; i++) {
            cap[source][i + 1] = current[i];
            cap[f + 1 + i][sink] = capacity[i];
        }

        for (int i = 0; i < f; i++) {
            for (int j = 0; j < f; j++) {
                if (dist[i][j] <= maxTime) {
                    cap[i + 1][f + 1 + j] = 1000000;
                }
            }
        }

        int maxFlow = 0;
        while (true) {
            int[] parent = new int[n];
            Arrays.fill(parent, -1);
            boolean[] visited = new boolean[n];
            Queue<Integer> queue = new LinkedList<>();
            queue.add(source);
            visited[source] = true;

            while (!queue.isEmpty() && parent[sink] == -1) {
                int u = queue.poll();
                for (int v = 0; v < n; v++) {
                    if (!visited[v] && cap[u][v] > 0) {
                        visited[v] = true;
                        parent[v] = u;
                        queue.add(v);
                    }
                }
            }

            if (parent[sink] == -1) break;

            int pathFlow = Integer.MAX_VALUE;
            for (int v = sink; v != source; v = parent[v]) {
                pathFlow = Math.min(pathFlow, cap[parent[v]][v]);
            }

            for (int v = sink; v != source; v = parent[v]) {
                cap[parent[v]][v] -= pathFlow;
                cap[v][parent[v]] += pathFlow;
            }

            maxFlow += pathFlow;
        }

        return maxFlow >= totalStudents;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <queue>
#include <set>
#include <algorithm>
#include <cstring>
using namespace std;

const long long INF = 1e18;
int f;
long long dist[201][201];
int current_[201], capacity_[201];

bool canDistribute(long long maxTime, int totalStudents) {
    int n = 2 * f + 2;
    int source = 0, sink = 2 * f + 1;

    vector<vector<int>> cap(n, vector<int>(n, 0));

    for (int i = 0; i < f; i++) {
        cap[source][i + 1] = current_[i];
        cap[f + 1 + i][sink] = capacity_[i];
    }

    for (int i = 0; i < f; i++) {
        for (int j = 0; j < f; j++) {
            if (dist[i][j] <= maxTime) {
                cap[i + 1][f + 1 + j] = 1000000;
            }
        }
    }

    int maxFlow = 0;
    while (true) {
        vector<int> parent(n, -1);
        vector<bool> visited(n, false);
        queue<int> q;
        q.push(source);
        visited[source] = true;

        while (!q.empty() && parent[sink] == -1) {
            int u = q.front();
            q.pop();
            for (int v = 0; v < n; v++) {
                if (!visited[v] && cap[u][v] > 0) {
                    visited[v] = true;
                    parent[v] = u;
                    q.push(v);
                }
            }
        }

        if (parent[sink] == -1) break;

        int pathFlow = INT_MAX;
        for (int v = sink; v != source; v = parent[v]) {
            pathFlow = min(pathFlow, cap[parent[v]][v]);
        }

        for (int v = sink; v != source; v = parent[v]) {
            cap[parent[v]][v] -= pathFlow;
            cap[v][parent[v]] += pathFlow;
        }

        maxFlow += pathFlow;
    }

    return maxFlow >= totalStudents;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int p;
    cin >> f >> p;

    int totalStudents = 0, totalCapacity = 0;
    for (int i = 0; i < f; i++) {
        cin >> current_[i] >> capacity_[i];
        totalStudents += current_[i];
        totalCapacity += capacity_[i];
    }

    if (totalStudents > totalCapacity) {
        cout << -1 << endl;
        return 0;
    }

    for (int i = 0; i < f; i++) {
        for (int j = 0; j < f; j++) {
            dist[i][j] = (i == j) ? 0 : INF;
        }
    }

    for (int i = 0; i < p; i++) {
        int a, b;
        long long t;
        cin >> a >> b >> t;
        a--; b--;
        dist[a][b] = min(dist[a][b], t);
        dist[b][a] = min(dist[b][a], t);
    }

    for (int k = 0; k < f; k++) {
        for (int i = 0; i < f; i++) {
            for (int j = 0; j < f; j++) {
                if (dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }

    set<long long> allTimes;
    allTimes.insert(0);
    for (int i = 0; i < f; i++) {
        for (int j = 0; j < f; j++) {
            if (dist[i][j] != INF) {
                allTimes.insert(dist[i][j]);
            }
        }
    }

    vector<long long> times(allTimes.begin(), allTimes.end());
    int left = 0, right = times.size() - 1;
    long long result = -1;

    while (left <= right) {
        int mid = (left + right) / 2;
        if (canDistribute(times[mid], totalStudents)) {
            result = times[mid];
            right = mid - 1;
        } else {
            left = mid + 1;
        }
    }

    cout << result << endl;
    return 0;
}
'''
    },
    "1746": {
        "python": '''import sys
input = sys.stdin.readline

INF = float('inf')

def solve():
    n, t, s, e = map(int, input().split())

    # Compress node numbers
    nodes = set()
    edges = []
    for _ in range(t):
        length, i1, i2 = map(int, input().split())
        nodes.add(i1)
        nodes.add(i2)
        edges.append((i1, i2, length))

    node_list = sorted(nodes)
    node_map = {v: i for i, v in enumerate(node_list)}
    num_nodes = len(node_list)

    s = node_map[s]
    e = node_map[e]

    # Build adjacency matrix
    adj = [[INF] * num_nodes for _ in range(num_nodes)]
    for i1, i2, length in edges:
        u, v = node_map[i1], node_map[i2]
        adj[u][v] = min(adj[u][v], length)
        adj[v][u] = min(adj[v][u], length)

    # Matrix multiplication for shortest paths with exactly k edges
    def mat_mult(A, B):
        n = len(A)
        C = [[INF] * n for _ in range(n)]
        for i in range(n):
            for k in range(n):
                if A[i][k] == INF:
                    continue
                for j in range(n):
                    if B[k][j] == INF:
                        continue
                    C[i][j] = min(C[i][j], A[i][k] + B[k][j])
        return C

    # Matrix exponentiation
    def mat_pow(M, p):
        n = len(M)
        result = [[INF] * n for _ in range(n)]
        for i in range(n):
            result[i][i] = 0

        base = [row[:] for row in M]

        while p > 0:
            if p & 1:
                result = mat_mult(result, base)
            base = mat_mult(base, base)
            p >>= 1

        return result

    result = mat_pow(adj, n)
    print(result[s][e])

solve()
''',
        "java": '''import java.util.*;

public class Main {
    static final long INF = (long) 1e18;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int t = sc.nextInt();
        int s = sc.nextInt();
        int e = sc.nextInt();

        Set<Integer> nodeSet = new TreeSet<>();
        int[][] edgesData = new int[t][3];

        for (int i = 0; i < t; i++) {
            int length = sc.nextInt();
            int i1 = sc.nextInt();
            int i2 = sc.nextInt();
            nodeSet.add(i1);
            nodeSet.add(i2);
            edgesData[i] = new int[]{i1, i2, length};
        }

        List<Integer> nodeList = new ArrayList<>(nodeSet);
        Map<Integer, Integer> nodeMap = new HashMap<>();
        for (int i = 0; i < nodeList.size(); i++) {
            nodeMap.put(nodeList.get(i), i);
        }

        int numNodes = nodeList.size();
        s = nodeMap.get(s);
        e = nodeMap.get(e);

        long[][] adj = new long[numNodes][numNodes];
        for (int i = 0; i < numNodes; i++) {
            Arrays.fill(adj[i], INF);
        }

        for (int[] edge : edgesData) {
            int u = nodeMap.get(edge[0]);
            int v = nodeMap.get(edge[1]);
            int len = edge[2];
            adj[u][v] = Math.min(adj[u][v], len);
            adj[v][u] = Math.min(adj[v][u], len);
        }

        long[][] result = matPow(adj, n, numNodes);
        System.out.println(result[s][e]);
    }

    static long[][] matMult(long[][] A, long[][] B, int n) {
        long[][] C = new long[n][n];
        for (int i = 0; i < n; i++) {
            Arrays.fill(C[i], INF);
        }

        for (int i = 0; i < n; i++) {
            for (int k = 0; k < n; k++) {
                if (A[i][k] == INF) continue;
                for (int j = 0; j < n; j++) {
                    if (B[k][j] == INF) continue;
                    C[i][j] = Math.min(C[i][j], A[i][k] + B[k][j]);
                }
            }
        }
        return C;
    }

    static long[][] matPow(long[][] M, int p, int n) {
        long[][] result = new long[n][n];
        for (int i = 0; i < n; i++) {
            Arrays.fill(result[i], INF);
            result[i][i] = 0;
        }

        long[][] base = new long[n][n];
        for (int i = 0; i < n; i++) {
            base[i] = M[i].clone();
        }

        while (p > 0) {
            if ((p & 1) == 1) {
                result = matMult(result, base, n);
            }
            base = matMult(base, base, n);
            p >>= 1;
        }

        return result;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
using namespace std;

const long long INF = 1e18;

vector<vector<long long>> matMult(vector<vector<long long>>& A, vector<vector<long long>>& B, int n) {
    vector<vector<long long>> C(n, vector<long long>(n, INF));

    for (int i = 0; i < n; i++) {
        for (int k = 0; k < n; k++) {
            if (A[i][k] == INF) continue;
            for (int j = 0; j < n; j++) {
                if (B[k][j] == INF) continue;
                C[i][j] = min(C[i][j], A[i][k] + B[k][j]);
            }
        }
    }
    return C;
}

vector<vector<long long>> matPow(vector<vector<long long>>& M, int p, int n) {
    vector<vector<long long>> result(n, vector<long long>(n, INF));
    for (int i = 0; i < n; i++) {
        result[i][i] = 0;
    }

    vector<vector<long long>> base = M;

    while (p > 0) {
        if (p & 1) {
            result = matMult(result, base, n);
        }
        base = matMult(base, base, n);
        p >>= 1;
    }

    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, t, s, e;
    cin >> n >> t >> s >> e;

    set<int> nodeSet;
    vector<tuple<int, int, int>> edges;

    for (int i = 0; i < t; i++) {
        int length, i1, i2;
        cin >> length >> i1 >> i2;
        nodeSet.insert(i1);
        nodeSet.insert(i2);
        edges.push_back({i1, i2, length});
    }

    vector<int> nodeList(nodeSet.begin(), nodeSet.end());
    map<int, int> nodeMap;
    for (int i = 0; i < nodeList.size(); i++) {
        nodeMap[nodeList[i]] = i;
    }

    int numNodes = nodeList.size();
    s = nodeMap[s];
    e = nodeMap[e];

    vector<vector<long long>> adj(numNodes, vector<long long>(numNodes, INF));

    for (auto& [i1, i2, length] : edges) {
        int u = nodeMap[i1];
        int v = nodeMap[i2];
        adj[u][v] = min(adj[u][v], (long long)length);
        adj[v][u] = min(adj[v][u], (long long)length);
    }

    auto result = matPow(adj, n, numNodes);
    cout << result[s][e] << endl;
    return 0;
}
'''
    },
    "1747": {
        "python": '''import sys
input = sys.stdin.readline

def is_palindrome(n):
    s = str(n)
    return s == s[::-1]

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

n = int(input())

# Start from n and find first palindrome prime
curr = n
while True:
    if is_palindrome(curr) and is_prime(curr):
        print(curr)
        break
    curr += 1
''',
        "java": '''import java.util.*;

public class Main {
    static boolean isPalindrome(int n) {
        String s = String.valueOf(n);
        int len = s.length();
        for (int i = 0; i < len / 2; i++) {
            if (s.charAt(i) != s.charAt(len - 1 - i)) {
                return false;
            }
        }
        return true;
    }

    static boolean isPrime(int n) {
        if (n < 2) return false;
        if (n == 2) return true;
        if (n % 2 == 0) return false;
        for (int i = 3; i * i <= n; i += 2) {
            if (n % i == 0) return false;
        }
        return true;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        int curr = n;
        while (true) {
            if (isPalindrome(curr) && isPrime(curr)) {
                System.out.println(curr);
                break;
            }
            curr++;
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

bool isPalindrome(int n) {
    string s = to_string(n);
    string rev = s;
    reverse(rev.begin(), rev.end());
    return s == rev;
}

bool isPrime(int n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    for (int i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return false;
    }
    return true;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int curr = n;
    while (true) {
        if (isPalindrome(curr) && isPrime(curr)) {
            cout << curr << endl;
            break;
        }
        curr++;
    }
    return 0;
}
'''
    },
    "1748": {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())

result = 0
digits = 1
start = 1
end = 9

while start <= n:
    if n >= end:
        result += digits * (end - start + 1)
    else:
        result += digits * (n - start + 1)

    digits += 1
    start = end + 1
    end = end * 10 + 9

print(result)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long n = sc.nextLong();

        long result = 0;
        long digits = 1;
        long start = 1;
        long end = 9;

        while (start <= n) {
            if (n >= end) {
                result += digits * (end - start + 1);
            } else {
                result += digits * (n - start + 1);
            }

            digits++;
            start = end + 1;
            end = end * 10 + 9;
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n;
    cin >> n;

    long long result = 0;
    long long digits = 1;
    long long start = 1;
    long long end = 9;

    while (start <= n) {
        if (n >= end) {
            result += digits * (end - start + 1);
        } else {
            result += digits * (n - start + 1);
        }

        digits++;
        start = end + 1;
        end = end * 10 + 9;
    }

    cout << result << endl;
    return 0;
}
'''
    },
    "1749": {
        "python": '''import sys
input = sys.stdin.readline

def solve():
    n, m = map(int, input().split())
    matrix = []
    for _ in range(n):
        matrix.append(list(map(int, input().split())))

    # Compute prefix sums
    prefix = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            prefix[i][j] = matrix[i-1][j-1] + prefix[i-1][j] + prefix[i][j-1] - prefix[i-1][j-1]

    def get_sum(r1, c1, r2, c2):
        return prefix[r2][c2] - prefix[r1-1][c2] - prefix[r2][c1-1] + prefix[r1-1][c1-1]

    max_sum = float('-inf')

    for r1 in range(1, n + 1):
        for r2 in range(r1, n + 1):
            for c1 in range(1, m + 1):
                for c2 in range(c1, m + 1):
                    s = get_sum(r1, c1, r2, c2)
                    max_sum = max(max_sum, s)

    print(max_sum)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();

        int[][] matrix = new int[n][m];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                matrix[i][j] = sc.nextInt();
            }
        }

        int[][] prefix = new int[n + 1][m + 1];
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= m; j++) {
                prefix[i][j] = matrix[i-1][j-1] + prefix[i-1][j] + prefix[i][j-1] - prefix[i-1][j-1];
            }
        }

        int maxSum = Integer.MIN_VALUE;

        for (int r1 = 1; r1 <= n; r1++) {
            for (int r2 = r1; r2 <= n; r2++) {
                for (int c1 = 1; c1 <= m; c1++) {
                    for (int c2 = c1; c2 <= m; c2++) {
                        int s = prefix[r2][c2] - prefix[r1-1][c2] - prefix[r2][c1-1] + prefix[r1-1][c1-1];
                        maxSum = Math.max(maxSum, s);
                    }
                }
            }
        }

        System.out.println(maxSum);
    }
}
''',
        "cpp": '''#include <iostream>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    int matrix[200][200];
    int prefix[201][201] = {0};

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            cin >> matrix[i][j];
        }
    }

    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= m; j++) {
            prefix[i][j] = matrix[i-1][j-1] + prefix[i-1][j] + prefix[i][j-1] - prefix[i-1][j-1];
        }
    }

    int maxSum = INT_MIN;

    for (int r1 = 1; r1 <= n; r1++) {
        for (int r2 = r1; r2 <= n; r2++) {
            for (int c1 = 1; c1 <= m; c1++) {
                for (int c2 = c1; c2 <= m; c2++) {
                    int s = prefix[r2][c2] - prefix[r1-1][c2] - prefix[r2][c1-1] + prefix[r1-1][c1-1];
                    maxSum = max(maxSum, s);
                }
            }
        }
    }

    cout << maxSum << endl;
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
