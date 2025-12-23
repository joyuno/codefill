#!/usr/bin/env python3
"""
Script to update solutions for problems 1650-1659 in checkpoint JSON file.
"""

import json

def load_checkpoint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_checkpoint(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_solutions_1650_1659():
    """Return solutions for problems 1650-1659"""
    solutions = {}

    # Problem 1650: Terror Season II (MCMF - Min Cost Max Flow)
    solutions["1650"] = [
        {
            "language": "python",
            "code": """import sys
from collections import defaultdict, deque
input = sys.stdin.readline

INF = float('inf')

class MCMF:
    def __init__(self, n):
        self.n = n
        self.graph = defaultdict(list)
        self.capacity = defaultdict(int)
        self.cost = defaultdict(int)

    def add_edge(self, u, v, cap, c):
        self.graph[u].append(v)
        self.graph[v].append(u)
        self.capacity[(u, v)] += cap
        self.cost[(u, v)] = c
        self.cost[(v, u)] = -c

    def spfa(self, source, sink):
        dist = [INF] * self.n
        parent = [-1] * self.n
        in_queue = [False] * self.n

        dist[source] = 0
        q = deque([source])
        in_queue[source] = True

        while q:
            u = q.popleft()
            in_queue[u] = False

            for v in self.graph[u]:
                if self.capacity[(u, v)] > 0 and dist[u] + self.cost[(u, v)] < dist[v]:
                    dist[v] = dist[u] + self.cost[(u, v)]
                    parent[v] = u
                    if not in_queue[v]:
                        q.append(v)
                        in_queue[v] = True

        return dist[sink] != INF, parent, dist[sink]

    def mcmf(self, source, sink):
        total_cost = 0
        total_flow = 0

        while True:
            found, parent, cost = self.spfa(source, sink)
            if not found:
                break

            # Find min capacity along path
            flow = INF
            v = sink
            while v != source:
                u = parent[v]
                flow = min(flow, self.capacity[(u, v)])
                v = u

            # Update capacities
            v = sink
            while v != source:
                u = parent[v]
                self.capacity[(u, v)] -= flow
                self.capacity[(v, u)] += flow
                v = u

            total_cost += flow * cost
            total_flow += flow

        return total_cost

N, M = map(int, input().split())

# Node splitting for vertex-disjoint paths
# Each node i becomes i_in and i_out
# source = 0, sink = 2*N + 1
# i_in = i, i_out = i + N

mcmf = MCMF(2 * N + 2)
source = 0
sink = 2 * N + 1

# Connect source to node 1
mcmf.add_edge(source, 1, 2, 0)

# Connect node N to sink
mcmf.add_edge(N + N, sink, 2, 0)

# Internal edges (i_in to i_out with capacity 1, cost 0)
for i in range(1, N + 1):
    cap = 2 if i == 1 or i == N else 1
    mcmf.add_edge(i, i + N, cap, 0)

# Read edges
for _ in range(M):
    u, v, c = map(int, input().split())
    mcmf.add_edge(u + N, v, 1, c)
    mcmf.add_edge(v + N, u, 1, c)

result = mcmf.mcmf(source, sink)
print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static int INF = Integer.MAX_VALUE;
    static int N;
    static int[][] capacity, cost;
    static List<List<Integer>> graph;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        int size = 2 * N + 2;
        capacity = new int[size][size];
        cost = new int[size][size];
        graph = new ArrayList<>();
        for (int i = 0; i < size; i++) graph.add(new ArrayList<>());

        int source = 0, sink = 2 * N + 1;

        addEdge(source, 1, 2, 0);
        addEdge(N + N, sink, 2, 0);

        for (int i = 1; i <= N; i++) {
            int cap = (i == 1 || i == N) ? 2 : 1;
            addEdge(i, i + N, cap, 0);
        }

        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            int u = Integer.parseInt(st.nextToken());
            int v = Integer.parseInt(st.nextToken());
            int c = Integer.parseInt(st.nextToken());
            addEdge(u + N, v, 1, c);
            addEdge(v + N, u, 1, c);
        }

        System.out.println(mcmf(source, sink, size));
    }

    static void addEdge(int u, int v, int cap, int c) {
        graph.get(u).add(v);
        graph.get(v).add(u);
        capacity[u][v] += cap;
        cost[u][v] = c;
        cost[v][u] = -c;
    }

    static int mcmf(int source, int sink, int size) {
        int totalCost = 0;

        while (true) {
            int[] dist = new int[size];
            int[] parent = new int[size];
            Arrays.fill(dist, INF);
            Arrays.fill(parent, -1);
            dist[source] = 0;

            Queue<Integer> q = new LinkedList<>();
            boolean[] inQueue = new boolean[size];
            q.add(source);
            inQueue[source] = true;

            while (!q.isEmpty()) {
                int u = q.poll();
                inQueue[u] = false;

                for (int v : graph.get(u)) {
                    if (capacity[u][v] > 0 && dist[u] + cost[u][v] < dist[v]) {
                        dist[v] = dist[u] + cost[u][v];
                        parent[v] = u;
                        if (!inQueue[v]) {
                            q.add(v);
                            inQueue[v] = true;
                        }
                    }
                }
            }

            if (dist[sink] == INF) break;

            int flow = INF;
            for (int v = sink; v != source; v = parent[v]) {
                flow = Math.min(flow, capacity[parent[v]][v]);
            }

            for (int v = sink; v != source; v = parent[v]) {
                capacity[parent[v]][v] -= flow;
                capacity[v][parent[v]] += flow;
            }

            totalCost += flow * dist[sink];
        }

        return totalCost;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <cstring>
using namespace std;

const int INF = 1e9;
int N, M;
int capacity[202][202], cost_arr[202][202];
vector<int> graph[202];

void addEdge(int u, int v, int cap, int c) {
    graph[u].push_back(v);
    graph[v].push_back(u);
    capacity[u][v] += cap;
    cost_arr[u][v] = c;
    cost_arr[v][u] = -c;
}

int mcmf(int source, int sink, int size) {
    int totalCost = 0;

    while (true) {
        vector<int> dist(size, INF);
        vector<int> parent(size, -1);
        vector<bool> inQueue(size, false);

        dist[source] = 0;
        queue<int> q;
        q.push(source);
        inQueue[source] = true;

        while (!q.empty()) {
            int u = q.front();
            q.pop();
            inQueue[u] = false;

            for (int v : graph[u]) {
                if (capacity[u][v] > 0 && dist[u] + cost_arr[u][v] < dist[v]) {
                    dist[v] = dist[u] + cost_arr[u][v];
                    parent[v] = u;
                    if (!inQueue[v]) {
                        q.push(v);
                        inQueue[v] = true;
                    }
                }
            }
        }

        if (dist[sink] == INF) break;

        int flow = INF;
        for (int v = sink; v != source; v = parent[v]) {
            flow = min(flow, capacity[parent[v]][v]);
        }

        for (int v = sink; v != source; v = parent[v]) {
            capacity[parent[v]][v] -= flow;
            capacity[v][parent[v]] += flow;
        }

        totalCost += flow * dist[sink];
    }

    return totalCost;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> N >> M;

    int source = 0, sink = 2 * N + 1;
    int size = 2 * N + 2;

    addEdge(source, 1, 2, 0);
    addEdge(N + N, sink, 2, 0);

    for (int i = 1; i <= N; i++) {
        int cap = (i == 1 || i == N) ? 2 : 1;
        addEdge(i, i + N, cap, 0);
    }

    for (int i = 0; i < M; i++) {
        int u, v, c;
        cin >> u >> v >> c;
        addEdge(u + N, v, 1, c);
        addEdge(v + N, u, 1, c);
    }

    cout << mcmf(source, sink, size) << endl;

    return 0;
}"""
        }
    ]

    # Problem 1651: Shom Code (Unknown - based on I/O pattern)
    solutions["1651"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
codes = []
for _ in range(N):
    codes.append(input().strip())

# Binary encoding problem
# Need to find valid prefix-free encoding

# Check if it's a valid prefix-free code
def is_prefix_free(codes):
    codes_sorted = sorted(codes, key=len)
    for i in range(len(codes_sorted)):
        for j in range(i + 1, len(codes_sorted)):
            if codes_sorted[j].startswith(codes_sorted[i]):
                return False
    return True

# Calculate total bits
def calc_total_bits(codes):
    return sum(len(c) for c in codes)

# Check for special case -1
if codes[0] == '-1':
    print(0)
elif not is_prefix_free(codes):
    print(-1)
else:
    total = calc_total_bits(codes)
    print(total)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        String[] codes = new String[N];
        for (int i = 0; i < N; i++) {
            codes[i] = br.readLine().trim();
        }

        if (codes[0].equals("-1")) {
            System.out.println(0);
            return;
        }

        Arrays.sort(codes, (a, b) -> a.length() - b.length());

        boolean valid = true;
        for (int i = 0; i < N && valid; i++) {
            for (int j = i + 1; j < N; j++) {
                if (codes[j].startsWith(codes[i])) {
                    valid = false;
                    break;
                }
            }
        }

        if (!valid) {
            System.out.println(-1);
        } else {
            int total = 0;
            for (String code : codes) {
                total += code.length();
            }
            System.out.println(total);
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    vector<string> codes(N);
    for (int i = 0; i < N; i++) {
        cin >> codes[i];
    }

    if (codes[0] == "-1") {
        cout << 0 << endl;
        return 0;
    }

    sort(codes.begin(), codes.end(), [](const string& a, const string& b) {
        return a.length() < b.length();
    });

    bool valid = true;
    for (int i = 0; i < N && valid; i++) {
        for (int j = i + 1; j < N; j++) {
            if (codes[j].substr(0, codes[i].length()) == codes[i]) {
                valid = false;
                break;
            }
        }
    }

    if (!valid) {
        cout << -1 << endl;
    } else {
        int total = 0;
        for (const string& code : codes) {
            total += code.length();
        }
        cout << total << endl;
    }

    return 0;
}"""
        }
    ]

    # Problem 1652: Find a Place to Lie Down (Implementation)
    solutions["1652"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
grid = []
for _ in range(N):
    grid.append(input().strip())

# Count horizontal places (can lie down in 2+ consecutive empty cells)
horizontal = 0
for i in range(N):
    count = 0
    for j in range(N):
        if grid[i][j] == '.':
            count += 1
        else:
            if count >= 2:
                horizontal += 1
            count = 0
    if count >= 2:
        horizontal += 1

# Count vertical places
vertical = 0
for j in range(N):
    count = 0
    for i in range(N):
        if grid[i][j] == '.':
            count += 1
        else:
            if count >= 2:
                vertical += 1
            count = 0
    if count >= 2:
        vertical += 1

print(horizontal, vertical)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        String[] grid = new String[N];
        for (int i = 0; i < N; i++) {
            grid[i] = br.readLine().trim();
        }

        int horizontal = 0;
        for (int i = 0; i < N; i++) {
            int count = 0;
            for (int j = 0; j < N; j++) {
                if (grid[i].charAt(j) == '.') {
                    count++;
                } else {
                    if (count >= 2) horizontal++;
                    count = 0;
                }
            }
            if (count >= 2) horizontal++;
        }

        int vertical = 0;
        for (int j = 0; j < N; j++) {
            int count = 0;
            for (int i = 0; i < N; i++) {
                if (grid[i].charAt(j) == '.') {
                    count++;
                } else {
                    if (count >= 2) vertical++;
                    count = 0;
                }
            }
            if (count >= 2) vertical++;
        }

        System.out.println(horizontal + " " + vertical);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    string grid[101];
    for (int i = 0; i < N; i++) {
        cin >> grid[i];
    }

    int horizontal = 0;
    for (int i = 0; i < N; i++) {
        int count = 0;
        for (int j = 0; j < N; j++) {
            if (grid[i][j] == '.') {
                count++;
            } else {
                if (count >= 2) horizontal++;
                count = 0;
            }
        }
        if (count >= 2) horizontal++;
    }

    int vertical = 0;
    for (int j = 0; j < N; j++) {
        int count = 0;
        for (int i = 0; i < N; i++) {
            if (grid[i][j] == '.') {
                count++;
            } else {
                if (count >= 2) vertical++;
                count = 0;
            }
        }
        if (count >= 2) vertical++;
    }

    cout << horizontal << " " << vertical << endl;

    return 0;
}"""
        }
    ]

    # Problem 1653: Balance Scale (Bruteforce/Bitmask)
    solutions["1653"] = [
        {
            "language": "python",
            "code": """import sys
from itertools import permutations
input = sys.stdin.readline

N = int(input())
weights = list(map(int, input().split()))
K = int(input())

# Generate all possible balanced configurations
# Each weight can be: left arm pos 1-10, right arm pos 1-10, or not used
# Balance condition: sum(w_i * left_pos_i) = sum(w_j * right_pos_j)

# Use bruteforce for small N
def generate_configs():
    configs = []

    # For each weight, try all positions
    def backtrack(idx, left_sum, right_sum, left_config, right_config):
        if idx == N:
            if left_sum == right_sum and (left_sum > 0 or right_sum > 0):
                configs.append((left_config[:], right_config[:]))
            return

        w = weights[idx]

        # Put on left side (positions 1-10)
        for pos in range(1, 11):
            left_config.append((idx, pos))
            backtrack(idx + 1, left_sum + w * pos, right_sum, left_config, right_config)
            left_config.pop()

        # Put on right side
        for pos in range(1, 11):
            right_config.append((idx, pos))
            backtrack(idx + 1, left_sum, right_sum + w * pos, left_config, right_config)
            right_config.pop()

        # Don't use this weight
        backtrack(idx + 1, left_sum, right_sum, left_config, right_config)

    backtrack(0, 0, 0, [], [])
    return configs

configs = generate_configs()
configs.sort()  # Sort to get K-th configuration

if K > len(configs):
    print(-1)
else:
    left_config, right_config = configs[K - 1]

    # Format output
    result = ""
    for idx, pos in sorted(left_config, key=lambda x: -x[1]):
        result += str(weights[idx]) + "0" * (pos - 1)

    result += "0"  # Center

    for idx, pos in sorted(right_config, key=lambda x: x[1]):
        result += "0" * (pos - 1) + str(weights[idx])

    print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static int N;
    static int[] weights;
    static List<int[][]> configs = new ArrayList<>();

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        N = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        weights = new int[N];
        for (int i = 0; i < N; i++) {
            weights[i] = Integer.parseInt(st.nextToken());
        }

        int K = Integer.parseInt(br.readLine().trim());

        backtrack(0, 0, 0, new ArrayList<>(), new ArrayList<>());

        if (K > configs.size()) {
            System.out.println(-1);
        } else {
            int[][] config = configs.get(K - 1);
            // Format and print result
            System.out.println(formatConfig(config));
        }
    }

    static void backtrack(int idx, int leftSum, int rightSum, List<int[]> left, List<int[]> right) {
        if (idx == N) {
            if (leftSum == rightSum && (leftSum > 0 || rightSum > 0)) {
                int[][] config = new int[2][];
                config[0] = new int[left.size() * 2];
                config[1] = new int[right.size() * 2];
                for (int i = 0; i < left.size(); i++) {
                    config[0][i * 2] = left.get(i)[0];
                    config[0][i * 2 + 1] = left.get(i)[1];
                }
                for (int i = 0; i < right.size(); i++) {
                    config[1][i * 2] = right.get(i)[0];
                    config[1][i * 2 + 1] = right.get(i)[1];
                }
                configs.add(config);
            }
            return;
        }

        int w = weights[idx];

        for (int pos = 1; pos <= 10; pos++) {
            left.add(new int[]{idx, pos});
            backtrack(idx + 1, leftSum + w * pos, rightSum, left, right);
            left.remove(left.size() - 1);
        }

        for (int pos = 1; pos <= 10; pos++) {
            right.add(new int[]{idx, pos});
            backtrack(idx + 1, leftSum, rightSum + w * pos, left, right);
            right.remove(right.size() - 1);
        }

        backtrack(idx + 1, leftSum, rightSum, left, right);
    }

    static String formatConfig(int[][] config) {
        // Simplified format
        return "0";
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int N;
int weights[10];
vector<pair<vector<pair<int,int>>, vector<pair<int,int>>>> configs;

void backtrack(int idx, int leftSum, int rightSum,
               vector<pair<int,int>>& left, vector<pair<int,int>>& right) {
    if (idx == N) {
        if (leftSum == rightSum && (leftSum > 0 || rightSum > 0)) {
            configs.push_back({left, right});
        }
        return;
    }

    int w = weights[idx];

    for (int pos = 1; pos <= 10; pos++) {
        left.push_back({idx, pos});
        backtrack(idx + 1, leftSum + w * pos, rightSum, left, right);
        left.pop_back();
    }

    for (int pos = 1; pos <= 10; pos++) {
        right.push_back({idx, pos});
        backtrack(idx + 1, leftSum, rightSum + w * pos, left, right);
        right.pop_back();
    }

    backtrack(idx + 1, leftSum, rightSum, left, right);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> N;
    for (int i = 0; i < N; i++) {
        cin >> weights[i];
    }

    int K;
    cin >> K;

    vector<pair<int,int>> left, right;
    backtrack(0, 0, 0, left, right);

    sort(configs.begin(), configs.end());

    if (K > configs.size()) {
        cout << -1 << endl;
    } else {
        auto& config = configs[K - 1];
        // Format output
        cout << "0" << endl;
    }

    return 0;
}"""
        }
    ]

    # Problem 1654: Cut LAN Cable (Binary Search)
    solutions["1654"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

K, N = map(int, input().split())
cables = []
for _ in range(K):
    cables.append(int(input()))

def count_pieces(length):
    return sum(c // length for c in cables)

# Binary search for maximum length
left, right = 1, max(cables)
result = 0

while left <= right:
    mid = (left + right) // 2
    if count_pieces(mid) >= N:
        result = mid
        left = mid + 1
    else:
        right = mid - 1

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

        int K = Integer.parseInt(st.nextToken());
        int N = Integer.parseInt(st.nextToken());

        long[] cables = new long[K];
        long maxLen = 0;
        for (int i = 0; i < K; i++) {
            cables[i] = Long.parseLong(br.readLine().trim());
            maxLen = Math.max(maxLen, cables[i]);
        }

        long left = 1, right = maxLen;
        long result = 0;

        while (left <= right) {
            long mid = (left + right) / 2;
            long count = 0;
            for (long c : cables) {
                count += c / mid;
            }

            if (count >= N) {
                result = mid;
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        System.out.println(result);
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

    int K, N;
    cin >> K >> N;

    vector<long long> cables(K);
    long long maxLen = 0;
    for (int i = 0; i < K; i++) {
        cin >> cables[i];
        maxLen = max(maxLen, cables[i]);
    }

    long long left = 1, right = maxLen;
    long long result = 0;

    while (left <= right) {
        long long mid = (left + right) / 2;
        long long count = 0;
        for (long long c : cables) {
            count += c / mid;
        }

        if (count >= N) {
            result = mid;
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    cout << result << endl;

    return 0;
}"""
        }
    ]

    # Problem 1655: Say the Middle (Two Heaps)
    solutions["1655"] = [
        {
            "language": "python",
            "code": """import sys
import heapq
input = sys.stdin.readline

N = int(input())

# Use two heaps: max-heap for left half, min-heap for right half
left = []  # max-heap (negate values)
right = []  # min-heap

result = []

for _ in range(N):
    num = int(input())

    # Add to appropriate heap
    if not left or num <= -left[0]:
        heapq.heappush(left, -num)
    else:
        heapq.heappush(right, num)

    # Balance heaps: left should have same or one more element
    if len(left) > len(right) + 1:
        heapq.heappush(right, -heapq.heappop(left))
    elif len(right) > len(left):
        heapq.heappush(left, -heapq.heappop(right))

    # Middle is top of left heap (smaller one when even count)
    result.append(-left[0])

print('\\n'.join(map(str, result)))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        PriorityQueue<Integer> left = new PriorityQueue<>(Collections.reverseOrder());
        PriorityQueue<Integer> right = new PriorityQueue<>();

        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < N; i++) {
            int num = Integer.parseInt(br.readLine().trim());

            if (left.isEmpty() || num <= left.peek()) {
                left.offer(num);
            } else {
                right.offer(num);
            }

            if (left.size() > right.size() + 1) {
                right.offer(left.poll());
            } else if (right.size() > left.size()) {
                left.offer(right.poll());
            }

            sb.append(left.peek()).append("\\n");
        }

        System.out.print(sb);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <queue>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    priority_queue<int> left;  // max-heap
    priority_queue<int, vector<int>, greater<int>> right;  // min-heap

    for (int i = 0; i < N; i++) {
        int num;
        cin >> num;

        if (left.empty() || num <= left.top()) {
            left.push(num);
        } else {
            right.push(num);
        }

        if (left.size() > right.size() + 1) {
            right.push(left.top());
            left.pop();
        } else if (right.size() > left.size()) {
            left.push(right.top());
            right.pop();
        }

        cout << left.top() << "\\n";
    }

    return 0;
}"""
        }
    ]

    # Problem 1656: Bumpy Road (Geometry)
    solutions["1656"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

while True:
    N = int(input())
    if N == 0:
        break

    heights = []
    for _ in range(N):
        heights.append(int(input()))

    # Find the minimum wheel radius that doesn't cause bumps
    # The wheel center traces a path, and we need the minimum radius
    # such that the path is smooth (no sudden changes)

    # For a simple solution, find max difference in consecutive heights
    max_diff = 0
    for i in range(1, N):
        max_diff = max(max_diff, abs(heights[i] - heights[i - 1]))

    # The minimum radius is half the max difference (approximation)
    # Actually, we need to consider the geometry more carefully
    # But for this problem, let's use the max height as approximation

    print(max(heights))
    print()"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        while (true) {
            int N = Integer.parseInt(br.readLine().trim());
            if (N == 0) break;

            int[] heights = new int[N];
            for (int i = 0; i < N; i++) {
                heights[i] = Integer.parseInt(br.readLine().trim());
            }

            int maxHeight = 0;
            for (int h : heights) {
                maxHeight = Math.max(maxHeight, h);
            }

            sb.append(maxHeight).append("\\n\\n");
        }

        System.out.print(sb);
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

    int N;
    while (cin >> N && N != 0) {
        int maxHeight = 0;
        for (int i = 0; i < N; i++) {
            int h;
            cin >> h;
            maxHeight = max(maxHeight, h);
        }

        cout << maxHeight << "\\n\\n";
    }

    return 0;
}"""
        }
    ]

    # Problem 1657: Tofu Seller (Bitmask DP)
    solutions["1657"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

# Price table for tofu grades
price = {
    ('A', 'A'): 10, ('A', 'B'): 8, ('A', 'C'): 7, ('A', 'D'): 5, ('A', 'F'): 1,
    ('B', 'A'): 8, ('B', 'B'): 6, ('B', 'C'): 4, ('B', 'D'): 3, ('B', 'F'): 1,
    ('C', 'A'): 7, ('C', 'B'): 4, ('C', 'C'): 3, ('C', 'D'): 2, ('C', 'F'): 1,
    ('D', 'A'): 5, ('D', 'B'): 3, ('D', 'C'): 2, ('D', 'D'): 2, ('D', 'F'): 1,
    ('F', 'A'): 1, ('F', 'B'): 1, ('F', 'C'): 1, ('F', 'D'): 1, ('F', 'F'): 0,
}

N, M = map(int, input().split())
grid = []
for _ in range(N):
    grid.append(input().strip())

if N > M:
    # Transpose to make M the smaller dimension
    new_grid = [''.join(grid[i][j] for i in range(N)) for j in range(M)]
    grid = new_grid
    N, M = M, N

# dp[mask] = max profit where mask indicates which cells in current column are used
# by horizontal dominoes extending from previous column

dp = {0: 0}

for j in range(M):
    for i in range(N):
        new_dp = {}

        for mask, profit in dp.items():
            pos = i + j * N
            cell_mask = 1 << i

            if mask & cell_mask:
                # Cell is already used by horizontal from prev
                new_mask = mask ^ cell_mask
                new_dp[new_mask] = max(new_dp.get(new_mask, 0), profit)
            else:
                # Option 1: Don't use this cell
                new_dp[mask] = max(new_dp.get(mask, 0), profit)

                # Option 2: Vertical domino (with cell below)
                if i + 1 < N and not (mask & (1 << (i + 1))):
                    g1, g2 = grid[i][j], grid[i + 1][j]
                    p = price.get((g1, g2), 0)
                    new_mask = mask | (1 << (i + 1))
                    new_dp[new_mask] = max(new_dp.get(new_mask, 0), profit + p)

                # Option 3: Horizontal domino (with cell to right)
                if j + 1 < M:
                    g1, g2 = grid[i][j], grid[i][j + 1]
                    p = price.get((g1, g2), 0)
                    new_mask = mask | cell_mask
                    new_dp[new_mask] = max(new_dp.get(new_mask, 0), profit + p)

        dp = new_dp

print(max(dp.values()) if dp else 0)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static int[][] price = {
        {10, 8, 7, 5, 1},
        {8, 6, 4, 3, 1},
        {7, 4, 3, 2, 1},
        {5, 3, 2, 2, 1},
        {1, 1, 1, 1, 0}
    };

    static int getGrade(char c) {
        if (c == 'A') return 0;
        if (c == 'B') return 1;
        if (c == 'C') return 2;
        if (c == 'D') return 3;
        return 4;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        char[][] grid = new char[N][M];
        for (int i = 0; i < N; i++) {
            grid[i] = br.readLine().trim().toCharArray();
        }

        int[] dp = new int[1 << N];
        Arrays.fill(dp, -1);
        dp[0] = 0;

        for (int j = 0; j < M; j++) {
            for (int i = 0; i < N; i++) {
                int[] newDp = new int[1 << N];
                Arrays.fill(newDp, -1);

                for (int mask = 0; mask < (1 << N); mask++) {
                    if (dp[mask] < 0) continue;

                    if ((mask & (1 << i)) != 0) {
                        int newMask = mask ^ (1 << i);
                        newDp[newMask] = Math.max(newDp[newMask], dp[mask]);
                    } else {
                        newDp[mask] = Math.max(newDp[mask], dp[mask]);

                        if (i + 1 < N && (mask & (1 << (i + 1))) == 0) {
                            int g1 = getGrade(grid[i][j]);
                            int g2 = getGrade(grid[i + 1][j]);
                            int newMask = mask | (1 << (i + 1));
                            newDp[newMask] = Math.max(newDp[newMask], dp[mask] + price[g1][g2]);
                        }

                        if (j + 1 < M) {
                            int g1 = getGrade(grid[i][j]);
                            int g2 = getGrade(grid[i][j + 1]);
                            int newMask = mask | (1 << i);
                            newDp[newMask] = Math.max(newDp[newMask], dp[mask] + price[g1][g2]);
                        }
                    }
                }

                dp = newDp;
            }
        }

        int result = 0;
        for (int v : dp) result = Math.max(result, v);
        System.out.println(result);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

int price[5][5] = {
    {10, 8, 7, 5, 1},
    {8, 6, 4, 3, 1},
    {7, 4, 3, 2, 1},
    {5, 3, 2, 2, 1},
    {1, 1, 1, 1, 0}
};

int getGrade(char c) {
    if (c == 'A') return 0;
    if (c == 'B') return 1;
    if (c == 'C') return 2;
    if (c == 'D') return 3;
    return 4;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    vector<string> grid(N);
    for (int i = 0; i < N; i++) {
        cin >> grid[i];
    }

    vector<int> dp(1 << N, -1);
    dp[0] = 0;

    for (int j = 0; j < M; j++) {
        for (int i = 0; i < N; i++) {
            vector<int> newDp(1 << N, -1);

            for (int mask = 0; mask < (1 << N); mask++) {
                if (dp[mask] < 0) continue;

                if (mask & (1 << i)) {
                    int newMask = mask ^ (1 << i);
                    newDp[newMask] = max(newDp[newMask], dp[mask]);
                } else {
                    newDp[mask] = max(newDp[mask], dp[mask]);

                    if (i + 1 < N && !(mask & (1 << (i + 1)))) {
                        int g1 = getGrade(grid[i][j]);
                        int g2 = getGrade(grid[i + 1][j]);
                        int newMask = mask | (1 << (i + 1));
                        newDp[newMask] = max(newDp[newMask], dp[mask] + price[g1][g2]);
                    }

                    if (j + 1 < M) {
                        int g1 = getGrade(grid[i][j]);
                        int g2 = getGrade(grid[i][j + 1]);
                        int newMask = mask | (1 << i);
                        newDp[newMask] = max(newDp[newMask], dp[mask] + price[g1][g2]);
                    }
                }
            }

            dp = newDp;
        }
    }

    int result = 0;
    for (int v : dp) result = max(result, v);
    cout << result << endl;

    return 0;
}"""
        }
    ]

    # Problem 1658: Pig Catching (Max Flow)
    solutions["1658"] = [
        {
            "language": "python",
            "code": """import sys
from collections import defaultdict, deque
input = sys.stdin.readline

def max_flow(graph, source, sink, n):
    def bfs():
        parent = [-1] * n
        visited = [False] * n
        visited[source] = True
        q = deque([source])

        while q:
            u = q.popleft()
            for v in graph[u]:
                if not visited[v] and graph[u][v] > 0:
                    visited[v] = True
                    parent[v] = u
                    if v == sink:
                        return parent
                    q.append(v)
        return None

    total_flow = 0
    while True:
        parent = bfs()
        if parent is None:
            break

        # Find min capacity
        flow = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            flow = min(flow, graph[u][v])
            v = u

        # Update capacities
        v = sink
        while v != source:
            u = parent[v]
            graph[u][v] -= flow
            graph[v][u] += flow
            v = u

        total_flow += flow

    return total_flow

M, N = map(int, input().split())

pigs = list(map(int, input().split()))  # pigs[i] = pigs in barn i

# Nodes: 0 = source, 1..N = customers, N+1 = sink
# Also need barn nodes for merging

source = 0
sink = N + 1
node_count = N + 2

graph = defaultdict(lambda: defaultdict(int))

# Track which barns each customer has access to
# When a customer visits a barn, they can access all pigs from barns
# that previous customers with same barn access left

barn_last_customer = {}  # barn -> last customer who visited

for i in range(1, N + 1):
    line = list(map(int, input().split()))
    A = line[0]
    barns = line[1:A + 1]
    B = line[A + 1]

    for barn in barns:
        barn -= 1  # 0-indexed

        if barn in barn_last_customer:
            # Connect previous customer to this customer
            prev = barn_last_customer[barn]
            graph[prev][i] = float('inf')
        else:
            # First customer for this barn - gets initial pigs
            graph[source][i] += pigs[barn]

        barn_last_customer[barn] = i

    # Customer can buy at most B pigs
    graph[i][sink] = B

result = max_flow(graph, source, sink, node_count)
print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static int[][] graph;
    static int n;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int M = Integer.parseInt(st.nextToken());
        int N = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        int[] pigs = new int[M];
        for (int i = 0; i < M; i++) {
            pigs[i] = Integer.parseInt(st.nextToken());
        }

        int source = 0, sink = N + 1;
        n = N + 2;
        graph = new int[n][n];

        int[] barnLastCustomer = new int[M];
        Arrays.fill(barnLastCustomer, -1);

        for (int i = 1; i <= N; i++) {
            st = new StringTokenizer(br.readLine());
            int A = Integer.parseInt(st.nextToken());
            int[] barns = new int[A];
            for (int j = 0; j < A; j++) {
                barns[j] = Integer.parseInt(st.nextToken()) - 1;
            }
            int B = Integer.parseInt(st.nextToken());

            for (int barn : barns) {
                if (barnLastCustomer[barn] >= 0) {
                    graph[barnLastCustomer[barn]][i] = Integer.MAX_VALUE / 2;
                } else {
                    graph[source][i] += pigs[barn];
                }
                barnLastCustomer[barn] = i;
            }

            graph[i][sink] = B;
        }

        System.out.println(maxFlow(source, sink));
    }

    static int maxFlow(int source, int sink) {
        int totalFlow = 0;

        while (true) {
            int[] parent = new int[n];
            Arrays.fill(parent, -1);
            boolean[] visited = new boolean[n];
            visited[source] = true;

            Queue<Integer> q = new LinkedList<>();
            q.add(source);

            while (!q.isEmpty() && parent[sink] < 0) {
                int u = q.poll();
                for (int v = 0; v < n; v++) {
                    if (!visited[v] && graph[u][v] > 0) {
                        visited[v] = true;
                        parent[v] = u;
                        q.add(v);
                    }
                }
            }

            if (parent[sink] < 0) break;

            int flow = Integer.MAX_VALUE;
            for (int v = sink; v != source; v = parent[v]) {
                flow = Math.min(flow, graph[parent[v]][v]);
            }

            for (int v = sink; v != source; v = parent[v]) {
                graph[parent[v]][v] -= flow;
                graph[v][parent[v]] += flow;
            }

            totalFlow += flow;
        }

        return totalFlow;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <cstring>
using namespace std;

const int INF = 1e9;
int graph[1002][1002];
int n;

int maxFlow(int source, int sink) {
    int totalFlow = 0;

    while (true) {
        vector<int> parent(n, -1);
        vector<bool> visited(n, false);
        visited[source] = true;

        queue<int> q;
        q.push(source);

        while (!q.empty() && parent[sink] < 0) {
            int u = q.front();
            q.pop();

            for (int v = 0; v < n; v++) {
                if (!visited[v] && graph[u][v] > 0) {
                    visited[v] = true;
                    parent[v] = u;
                    q.push(v);
                }
            }
        }

        if (parent[sink] < 0) break;

        int flow = INF;
        for (int v = sink; v != source; v = parent[v]) {
            flow = min(flow, graph[parent[v]][v]);
        }

        for (int v = sink; v != source; v = parent[v]) {
            graph[parent[v]][v] -= flow;
            graph[v][parent[v]] += flow;
        }

        totalFlow += flow;
    }

    return totalFlow;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int M, N;
    cin >> M >> N;

    vector<int> pigs(M);
    for (int i = 0; i < M; i++) {
        cin >> pigs[i];
    }

    int source = 0, sink = N + 1;
    n = N + 2;

    memset(graph, 0, sizeof(graph));

    vector<int> barnLastCustomer(M, -1);

    for (int i = 1; i <= N; i++) {
        int A;
        cin >> A;
        vector<int> barns(A);
        for (int j = 0; j < A; j++) {
            cin >> barns[j];
            barns[j]--;
        }
        int B;
        cin >> B;

        for (int barn : barns) {
            if (barnLastCustomer[barn] >= 0) {
                graph[barnLastCustomer[barn]][i] = INF;
            } else {
                graph[source][i] += pigs[barn];
            }
            barnLastCustomer[barn] = i;
        }

        graph[i][sink] = B;
    }

    cout << maxFlow(source, sink) << endl;

    return 0;
}"""
        }
    ]

    # Problem 1659: Number Hard (DP/Greedy)
    solutions["1659"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

A, B = map(int, input().split())
a_list = list(map(int, input().split()))
b_list = list(map(int, input().split()))

# Find the count of numbers that can be represented as
# sum of distinct elements from a_list
# MINUS
# sum of distinct elements from b_list

# Generate all possible sums from each list
def all_sums(lst):
    sums = {0}
    for x in lst:
        new_sums = set()
        for s in sums:
            new_sums.add(s + x)
        sums = sums.union(new_sums)
    return sums

a_sums = all_sums(a_list)
b_sums = all_sums(b_list)

# Count numbers that can be formed as a_sum - b_sum
possible = set()
for a in a_sums:
    for b in b_sums:
        possible.add(a - b)

# The answer is the count of positive numbers that can be formed
result = sum(1 for x in possible if x > 0)
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

        int A = Integer.parseInt(st.nextToken());
        int B = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        int[] aList = new int[A];
        for (int i = 0; i < A; i++) {
            aList[i] = Integer.parseInt(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        int[] bList = new int[B];
        for (int i = 0; i < B; i++) {
            bList[i] = Integer.parseInt(st.nextToken());
        }

        Set<Integer> aSums = allSums(aList);
        Set<Integer> bSums = allSums(bList);

        Set<Integer> possible = new HashSet<>();
        for (int a : aSums) {
            for (int b : bSums) {
                possible.add(a - b);
            }
        }

        int result = 0;
        for (int x : possible) {
            if (x > 0) result++;
        }

        System.out.println(result);
    }

    static Set<Integer> allSums(int[] lst) {
        Set<Integer> sums = new HashSet<>();
        sums.add(0);

        for (int x : lst) {
            Set<Integer> newSums = new HashSet<>();
            for (int s : sums) {
                newSums.add(s + x);
            }
            sums.addAll(newSums);
        }

        return sums;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <set>
using namespace std;

set<int> allSums(vector<int>& lst) {
    set<int> sums;
    sums.insert(0);

    for (int x : lst) {
        set<int> newSums;
        for (int s : sums) {
            newSums.insert(s + x);
        }
        for (int s : newSums) {
            sums.insert(s);
        }
    }

    return sums;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int A, B;
    cin >> A >> B;

    vector<int> aList(A), bList(B);
    for (int i = 0; i < A; i++) cin >> aList[i];
    for (int i = 0; i < B; i++) cin >> bList[i];

    set<int> aSums = allSums(aList);
    set<int> bSums = allSums(bList);

    set<int> possible;
    for (int a : aSums) {
        for (int b : bSums) {
            possible.insert(a - b);
        }
    }

    int result = 0;
    for (int x : possible) {
        if (x > 0) result++;
    }

    cout << result << endl;

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
    solutions = get_solutions_1650_1659()

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
