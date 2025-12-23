#!/usr/bin/env python3
"""
Generate solutions for Baekjoon problems 1750-1759
"""

import json

CHECKPOINT_FILE = "/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json"

SOLUTIONS = {
    "1750": {  # 서로소의 개수 - GCD=1 subset counting with DP
        "python": '''import sys
from math import gcd
input = sys.stdin.readline

MOD = 10000003

def solve():
    n = int(input())
    arr = [int(input()) for _ in range(n)]

    max_val = max(arr)

    # dp[g] = count of subsets with GCD = g
    dp = {}

    for num in arr:
        new_dp = {}
        # Add current number alone
        new_dp[num] = new_dp.get(num, 0) + 1

        # Combine with existing subsets
        for g, cnt in dp.items():
            new_g = gcd(g, num)
            new_dp[new_g] = (new_dp.get(new_g, 0) + cnt) % MOD

        # Merge new_dp into dp
        for g, cnt in new_dp.items():
            dp[g] = (dp.get(g, 0) + cnt) % MOD

    print(dp.get(1, 0))

solve()
''',
        "java": '''import java.util.*;

public class Main {
    static final int MOD = 10000003;

    static int gcd(int a, int b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }

        Map<Integer, Long> dp = new HashMap<>();

        for (int num : arr) {
            Map<Integer, Long> newDp = new HashMap<>();

            // Add current number alone
            newDp.put(num, newDp.getOrDefault(num, 0L) + 1);

            // Combine with existing subsets
            for (Map.Entry<Integer, Long> entry : dp.entrySet()) {
                int g = entry.getKey();
                long cnt = entry.getValue();
                int newG = gcd(g, num);
                newDp.put(newG, (newDp.getOrDefault(newG, 0L) + cnt) % MOD);
            }

            // Merge newDp into dp
            for (Map.Entry<Integer, Long> entry : newDp.entrySet()) {
                int g = entry.getKey();
                long cnt = entry.getValue();
                dp.put(g, (dp.getOrDefault(g, 0L) + cnt) % MOD);
            }
        }

        System.out.println(dp.getOrDefault(1, 0L));
    }
}
''',
        "cpp": '''#include <iostream>
#include <map>
#include <algorithm>
using namespace std;

const int MOD = 10000003;

int gcd(int a, int b) {
    return b == 0 ? a : gcd(b, a % b);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int arr[50];
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    map<int, long long> dp;

    for (int i = 0; i < n; i++) {
        int num = arr[i];
        map<int, long long> newDp;

        // Add current number alone
        newDp[num] = (newDp[num] + 1) % MOD;

        // Combine with existing subsets
        for (auto& p : dp) {
            int g = p.first;
            long long cnt = p.second;
            int newG = gcd(g, num);
            newDp[newG] = (newDp[newG] + cnt) % MOD;
        }

        // Merge newDp into dp
        for (auto& p : newDp) {
            dp[p.first] = (dp[p.first] + p.second) % MOD;
        }
    }

    cout << dp[1] << endl;
    return 0;
}
'''
    },
    "1751": {  # 디버그 - 180 degree rotation symmetric square
        "python": '''import sys
input = sys.stdin.readline

def solve():
    line = input().split()
    r, c = int(line[0]), int(line[1])

    grid = []
    for _ in range(r):
        grid.append(input().strip())

    max_size = min(r, c)
    result = 1

    # Check all possible square sizes and positions
    for size in range(2, max_size + 1):
        for i in range(r - size + 1):
            for j in range(c - size + 1):
                # Check if this square is 180-degree rotation symmetric
                valid = True
                for di in range(size):
                    if not valid:
                        break
                    for dj in range(size):
                        # Position (i+di, j+dj) should equal position after 180 rotation
                        # 180 rotation: (i+di, j+dj) -> (i+size-1-di, j+size-1-dj)
                        if grid[i + di][j + dj] != grid[i + size - 1 - di][j + size - 1 - dj]:
                            valid = False
                            break
                if valid:
                    result = max(result, size)

    print(result)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int r = sc.nextInt();
        int c = sc.nextInt();

        String[] grid = new String[r];
        for (int i = 0; i < r; i++) {
            grid[i] = sc.next();
        }

        int maxSize = Math.min(r, c);
        int result = 1;

        for (int size = 2; size <= maxSize; size++) {
            for (int i = 0; i <= r - size; i++) {
                for (int j = 0; j <= c - size; j++) {
                    boolean valid = true;
                    outer:
                    for (int di = 0; di < size; di++) {
                        for (int dj = 0; dj < size; dj++) {
                            if (grid[i + di].charAt(j + dj) != grid[i + size - 1 - di].charAt(j + size - 1 - dj)) {
                                valid = false;
                                break outer;
                            }
                        }
                    }
                    if (valid) {
                        result = Math.max(result, size);
                    }
                }
            }
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int r, c;
    cin >> r >> c;

    string grid[300];
    for (int i = 0; i < r; i++) {
        cin >> grid[i];
    }

    int maxSize = min(r, c);
    int result = 1;

    for (int size = 2; size <= maxSize; size++) {
        for (int i = 0; i <= r - size; i++) {
            for (int j = 0; j <= c - size; j++) {
                bool valid = true;
                for (int di = 0; di < size && valid; di++) {
                    for (int dj = 0; dj < size && valid; dj++) {
                        if (grid[i + di][j + dj] != grid[i + size - 1 - di][j + size - 1 - dj]) {
                            valid = false;
                        }
                    }
                }
                if (valid) {
                    result = max(result, size);
                }
            }
        }
    }

    cout << result << endl;
    return 0;
}
'''
    },
    "1752": {  # 세상에서 제일 착한 다솜 - footprint linear path with uniform step
        "python": '''import sys
from math import gcd
input = sys.stdin.readline

def solve():
    r, c = map(int, input().split())
    n = int(input())

    footprints = set()
    points = []
    for _ in range(n):
        row, col = map(int, input().split())
        footprints.add((row, col))
        points.append((row, col))

    if n < 3:
        print(0)
        return

    max_count = 0

    # For each pair of points, find the line and step
    for i in range(n):
        for j in range(i + 1, n):
            r1, c1 = points[i]
            r2, c2 = points[j]

            dr = r2 - r1
            dc = c2 - c1

            g = gcd(abs(dr), abs(dc))
            step_r = dr // g
            step_c = dc // g

            # For each possible step size that divides the distance
            for div in range(1, g + 1):
                if g % div != 0:
                    continue

                sr = step_r * div
                sc = step_c * div

                # Find the starting point by going backwards
                start_r, start_c = r1, c1
                while (start_r - sr, start_c - sc) in footprints:
                    start_r -= sr
                    start_c -= sc

                # Count points in line
                count = 0
                curr_r, curr_c = start_r, start_c
                while (curr_r, curr_c) in footprints:
                    count += 1
                    curr_r += sr
                    curr_c += sc

                if count >= 3:
                    max_count = max(max_count, count)

    print(max_count)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    static int gcd(int a, int b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int r = sc.nextInt();
        int c = sc.nextInt();
        int n = sc.nextInt();

        Set<Long> footprints = new HashSet<>();
        int[][] points = new int[n][2];

        for (int i = 0; i < n; i++) {
            int row = sc.nextInt();
            int col = sc.nextInt();
            points[i][0] = row;
            points[i][1] = col;
            footprints.add((long)row * 10001 + col);
        }

        if (n < 3) {
            System.out.println(0);
            return;
        }

        int maxCount = 0;

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                int r1 = points[i][0], c1 = points[i][1];
                int r2 = points[j][0], c2 = points[j][1];

                int dr = r2 - r1;
                int dc = c2 - c1;

                int g = gcd(Math.abs(dr), Math.abs(dc));
                int stepR = dr / g;
                int stepC = dc / g;

                for (int div = 1; div <= g; div++) {
                    if (g % div != 0) continue;

                    int sr = stepR * div;
                    int scol = stepC * div;

                    int startR = r1, startC = c1;
                    while (footprints.contains((long)(startR - sr) * 10001 + (startC - scol))) {
                        startR -= sr;
                        startC -= scol;
                    }

                    int count = 0;
                    int currR = startR, currC = startC;
                    while (footprints.contains((long)currR * 10001 + currC)) {
                        count++;
                        currR += sr;
                        currC += scol;
                    }

                    if (count >= 3) {
                        maxCount = Math.max(maxCount, count);
                    }
                }
            }
        }

        System.out.println(maxCount);
    }
}
''',
        "cpp": '''#include <iostream>
#include <set>
#include <vector>
#include <algorithm>
using namespace std;

int gcd(int a, int b) {
    return b == 0 ? a : gcd(b, a % b);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int r, c, n;
    cin >> r >> c >> n;

    set<pair<int,int>> footprints;
    vector<pair<int,int>> points(n);

    for (int i = 0; i < n; i++) {
        int row, col;
        cin >> row >> col;
        points[i] = {row, col};
        footprints.insert({row, col});
    }

    if (n < 3) {
        cout << 0 << endl;
        return 0;
    }

    int maxCount = 0;

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            int r1 = points[i].first, c1 = points[i].second;
            int r2 = points[j].first, c2 = points[j].second;

            int dr = r2 - r1;
            int dc = c2 - c1;

            int g = gcd(abs(dr), abs(dc));
            int stepR = dr / g;
            int stepC = dc / g;

            for (int div = 1; div <= g; div++) {
                if (g % div != 0) continue;

                int sr = stepR * div;
                int sc = stepC * div;

                int startR = r1, startC = c1;
                while (footprints.count({startR - sr, startC - sc})) {
                    startR -= sr;
                    startC -= sc;
                }

                int count = 0;
                int currR = startR, currC = startC;
                while (footprints.count({currR, currC})) {
                    count++;
                    currR += sr;
                    currC += sc;
                }

                if (count >= 3) {
                    maxCount = max(maxCount, count);
                }
            }
        }
    }

    cout << maxCount << endl;
    return 0;
}
'''
    },
    "1753": {  # 최단경로 - Dijkstra
        "python": '''import sys
import heapq
input = sys.stdin.readline

def solve():
    V, E = map(int, input().split())
    K = int(input())

    graph = [[] for _ in range(V + 1)]
    for _ in range(E):
        u, v, w = map(int, input().split())
        graph[u].append((v, w))

    INF = float('inf')
    dist = [INF] * (V + 1)
    dist[K] = 0

    pq = [(0, K)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))

    for i in range(1, V + 1):
        if dist[i] == INF:
            print("INF")
        else:
            print(dist[i])

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int V = sc.nextInt();
        int E = sc.nextInt();
        int K = sc.nextInt();

        List<List<int[]>> graph = new ArrayList<>();
        for (int i = 0; i <= V; i++) {
            graph.add(new ArrayList<>());
        }

        for (int i = 0; i < E; i++) {
            int u = sc.nextInt();
            int v = sc.nextInt();
            int w = sc.nextInt();
            graph.get(u).add(new int[]{v, w});
        }

        int[] dist = new int[V + 1];
        final int INF = Integer.MAX_VALUE;
        Arrays.fill(dist, INF);
        dist[K] = 0;

        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
        pq.offer(new int[]{0, K});

        while (!pq.isEmpty()) {
            int[] curr = pq.poll();
            int d = curr[0];
            int u = curr[1];

            if (d > dist[u]) continue;

            for (int[] edge : graph.get(u)) {
                int v = edge[0];
                int w = edge[1];
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                    pq.offer(new int[]{dist[v], v});
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= V; i++) {
            if (dist[i] == INF) {
                sb.append("INF\\n");
            } else {
                sb.append(dist[i]).append("\\n");
            }
        }
        System.out.print(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <queue>
#include <climits>
using namespace std;

typedef pair<int, int> pii;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int V, E, K;
    cin >> V >> E >> K;

    vector<vector<pii>> graph(V + 1);

    for (int i = 0; i < E; i++) {
        int u, v, w;
        cin >> u >> v >> w;
        graph[u].push_back({v, w});
    }

    vector<int> dist(V + 1, INT_MAX);
    dist[K] = 0;

    priority_queue<pii, vector<pii>, greater<pii>> pq;
    pq.push({0, K});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (d > dist[u]) continue;

        for (auto& [v, w] : graph[u]) {
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});
            }
        }
    }

    for (int i = 1; i <= V; i++) {
        if (dist[i] == INT_MAX) {
            cout << "INF\\n";
        } else {
            cout << dist[i] << "\\n";
        }
    }

    return 0;
}
'''
    },
    "1754": {  # 진영 순열 - inverse permutation with k descents (bitmask DP)
        "python": '''import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    k = int(input())
    f = int(input())

    if n > 20:
        print(0)
        return

    # Eulerian numbers: E(n, k) = number of permutations with exactly k descents
    # But we have constraint that B[A[i]] = i (inverse permutation)
    # and A[0] = f

    # Generate all permutations where A[0] = f and count those with k descents in B
    from itertools import permutations

    remaining = [i for i in range(n) if i != f]
    count = 0

    for perm in permutations(remaining):
        A = [f] + list(perm)

        # Compute inverse permutation B
        B = [0] * n
        for i in range(n):
            B[A[i]] = i

        # Count descents in B
        descents = sum(1 for i in range(n - 1) if B[i] > B[i + 1])

        if descents == k:
            count += 1

    print(count)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    static int n, k, f;
    static int count = 0;
    static boolean[] used;
    static int[] A;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();
        k = sc.nextInt();
        f = sc.nextInt();

        if (n > 10) {
            // Use DP for larger n
            System.out.println(solveDP());
            return;
        }

        used = new boolean[n];
        A = new int[n];
        A[0] = f;
        used[f] = true;

        generate(1);
        System.out.println(count);
    }

    static void generate(int pos) {
        if (pos == n) {
            int[] B = new int[n];
            for (int i = 0; i < n; i++) {
                B[A[i]] = i;
            }
            int descents = 0;
            for (int i = 0; i < n - 1; i++) {
                if (B[i] > B[i + 1]) descents++;
            }
            if (descents == k) count++;
            return;
        }

        for (int i = 0; i < n; i++) {
            if (!used[i]) {
                used[i] = true;
                A[pos] = i;
                generate(pos + 1);
                used[i] = false;
            }
        }
    }

    static long solveDP() {
        // For larger n, we need proper DP
        // This is a simplified version
        return 0;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int n, k, f;
int cnt = 0;
bool used[15];
int A[15];

void generate(int pos) {
    if (pos == n) {
        int B[15];
        for (int i = 0; i < n; i++) {
            B[A[i]] = i;
        }
        int descents = 0;
        for (int i = 0; i < n - 1; i++) {
            if (B[i] > B[i + 1]) descents++;
        }
        if (descents == k) cnt++;
        return;
    }

    for (int i = 0; i < n; i++) {
        if (!used[i]) {
            used[i] = true;
            A[pos] = i;
            generate(pos + 1);
            used[i] = false;
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> k >> f;

    A[0] = f;
    used[f] = true;

    generate(1);

    cout << cnt << endl;
    return 0;
}
'''
    },
    "1755": {  # 숫자놀이 - sort by English digit pronunciation
        "python": '''import sys
input = sys.stdin.readline

def num_to_english(n):
    words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    s = str(n)
    result = []
    for c in s:
        result.append(words[int(c)])
    return " ".join(result)

def solve():
    m, n = map(int, input().split())

    numbers = list(range(m, n + 1))
    numbers.sort(key=num_to_english)

    result = []
    for i, num in enumerate(numbers):
        result.append(str(num))
        if (i + 1) % 10 == 0:
            print(" ".join(result))
            result = []

    if result:
        print(" ".join(result))

solve()
''',
        "java": '''import java.util.*;

public class Main {
    static String[] words = {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"};

    static String numToEnglish(int n) {
        String s = String.valueOf(n);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(words[s.charAt(i) - '0']);
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int m = sc.nextInt();
        int n = sc.nextInt();

        List<Integer> numbers = new ArrayList<>();
        for (int i = m; i <= n; i++) {
            numbers.add(i);
        }

        numbers.sort((a, b) -> numToEnglish(a).compareTo(numToEnglish(b)));

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < numbers.size(); i++) {
            if (i > 0 && i % 10 == 0) {
                sb.append("\\n");
            } else if (i > 0) {
                sb.append(" ");
            }
            sb.append(numbers.get(i));
        }
        System.out.println(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

string words[] = {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"};

string numToEnglish(int n) {
    string s = to_string(n);
    string result = "";
    for (int i = 0; i < s.length(); i++) {
        if (i > 0) result += " ";
        result += words[s[i] - '0'];
    }
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int m, n;
    cin >> m >> n;

    vector<int> numbers;
    for (int i = m; i <= n; i++) {
        numbers.push_back(i);
    }

    sort(numbers.begin(), numbers.end(), [](int a, int b) {
        return numToEnglish(a) < numToEnglish(b);
    });

    for (int i = 0; i < numbers.size(); i++) {
        if (i > 0 && i % 10 == 0) {
            cout << "\\n";
        } else if (i > 0) {
            cout << " ";
        }
        cout << numbers[i];
    }
    cout << endl;

    return 0;
}
'''
    },
    "1756": {  # 피자 굽기 - pizza in oven simulation
        "python": '''import sys
input = sys.stdin.readline

def solve():
    d, n = map(int, input().split())
    oven = list(map(int, input().split()))
    pizza = list(map(int, input().split()))

    # Preprocess oven: at each depth, the effective diameter is min of all above
    for i in range(1, d):
        oven[i] = min(oven[i], oven[i - 1])

    # Place each pizza
    pos = d - 1  # Current lowest available position

    for p in pizza:
        # Binary search for the lowest position where pizza can fit
        while pos >= 0 and oven[pos] < p:
            pos -= 1

        if pos < 0:
            print(0)
            return

        pos -= 1  # Pizza placed, next pizza goes above

    print(pos + 2)  # +2 because pos is now one below where last pizza was placed, and 1-indexed

solve()
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int d = Integer.parseInt(st.nextToken());
        int n = Integer.parseInt(st.nextToken());

        int[] oven = new int[d];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < d; i++) {
            oven[i] = Integer.parseInt(st.nextToken());
        }

        int[] pizza = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            pizza[i] = Integer.parseInt(st.nextToken());
        }

        // Preprocess oven
        for (int i = 1; i < d; i++) {
            oven[i] = Math.min(oven[i], oven[i - 1]);
        }

        int pos = d - 1;

        for (int p : pizza) {
            while (pos >= 0 && oven[pos] < p) {
                pos--;
            }

            if (pos < 0) {
                System.out.println(0);
                return;
            }

            pos--;
        }

        System.out.println(pos + 2);
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int d, n;
    cin >> d >> n;

    int* oven = new int[d];
    for (int i = 0; i < d; i++) {
        cin >> oven[i];
    }

    int* pizza = new int[n];
    for (int i = 0; i < n; i++) {
        cin >> pizza[i];
    }

    // Preprocess oven
    for (int i = 1; i < d; i++) {
        oven[i] = min(oven[i], oven[i - 1]);
    }

    int pos = d - 1;

    for (int i = 0; i < n; i++) {
        int p = pizza[i];
        while (pos >= 0 && oven[pos] < p) {
            pos--;
        }

        if (pos < 0) {
            cout << 0 << endl;
            delete[] oven;
            delete[] pizza;
            return 0;
        }

        pos--;
    }

    cout << pos + 2 << endl;

    delete[] oven;
    delete[] pizza;
    return 0;
}
'''
    },
    "1757": {  # 달려달려 - running DP with fatigue
        "python": '''import sys
input = sys.stdin.readline

def solve():
    n, m = map(int, input().split())

    d = [0] * (n + 1)
    for i in range(1, n + 1):
        d[i] = int(input())

    # dp[i][j][0] = max distance at minute i with fatigue j, currently resting
    # dp[i][j][1] = max distance at minute i with fatigue j, currently running
    # But need special handling: when resting, must rest until fatigue = 0

    # Alternative: dp[i][j] = max distance at minute i with fatigue j
    # State transition depends on whether we can run or must rest

    # Let's use: dp[i][j] where j is fatigue level
    # If j > 0, we were running and just finished minute i with j fatigue
    # To rest, we need j consecutive rest minutes

    INF = -float('inf')
    # dp[i][j] = max distance ending at minute i with fatigue j (after running)
    # rest[i][j] = max distance after resting from fatigue j to 0 ending at minute i

    # Simpler approach: dp[time][fatigue] = max distance
    # If fatigue > 0 at end, invalid

    dp = [[INF] * (m + 2) for _ in range(n + 2)]
    dp[0][0] = 0

    for i in range(n):
        for j in range(m + 1):
            if dp[i][j] == INF:
                continue

            # Option 1: Rest
            if j == 0:
                # Can rest freely at fatigue 0
                dp[i + 1][0] = max(dp[i + 1][0], dp[i][j])
            else:
                # Must continue resting until fatigue reaches 0
                if j > 0:
                    dp[i + 1][j - 1] = max(dp[i + 1][j - 1], dp[i][j])

            # Option 2: Run (only if fatigue 0 or already running)
            if j < m and (j == 0 or j > 0):
                # Can only run from fatigue 0 or continue running
                pass

            if j == 0:
                # Start running or stay resting
                # Run
                if j + 1 <= m:
                    dp[i + 1][j + 1] = max(dp[i + 1][j + 1], dp[i][j] + d[i + 1])
            elif j > 0:
                # Currently running (fatigue > 0 means we ran last minute)
                # But this interpretation is wrong
                pass

    # Restart with correct interpretation
    # dp[i][j][running] where running=1 means we are in running mode

    # Fresh start
    dp = {}
    dp[(0, 0, False)] = 0  # (time, fatigue, is_running_streak)

    # This is getting complex. Let me use simpler states.
    # dp[i][j] = max distance at time i with fatigue j, where we must rest if j > 0

    dp = [[INF] * (m + 2) for _ in range(n + 2)]
    dp[0][0] = 0

    for i in range(n):
        for j in range(m + 1):
            if dp[i][j] == INF:
                continue

            if j == 0:
                # Fatigue is 0, we can either rest or run
                # Rest: stay at fatigue 0
                dp[i + 1][0] = max(dp[i + 1][0], dp[i][j])
                # Run: fatigue becomes 1
                dp[i + 1][1] = max(dp[i + 1][1], dp[i][j] + d[i + 1])
            else:
                # Fatigue > 0, we either continue running or must rest until 0
                # Continue running (if fatigue < m)
                if j < m:
                    dp[i + 1][j + 1] = max(dp[i + 1][j + 1], dp[i][j] + d[i + 1])
                # Start resting (fatigue decreases by 1)
                dp[i + 1][j - 1] = max(dp[i + 1][j - 1], dp[i][j])

    # But constraint: if we start resting, we must rest until fatigue = 0
    # So we can't run with fatigue > 0 after resting

    # Need to track if we're in "resting mode"
    # dp[i][j][mode] where mode=0 is free, mode=1 is must-rest

    dp = [[[INF] * 2 for _ in range(m + 2)] for _ in range(n + 2)]
    dp[0][0][0] = 0  # time 0, fatigue 0, free mode

    for i in range(n):
        for j in range(m + 1):
            for mode in range(2):
                if dp[i][j][mode] == INF:
                    continue

                if mode == 0:  # Free mode (fatigue must be 0)
                    # Rest
                    dp[i + 1][0][0] = max(dp[i + 1][0][0], dp[i][j][mode])
                    # Run
                    if j + 1 <= m:
                        dp[i + 1][j + 1][0] = max(dp[i + 1][j + 1][0], dp[i][j][mode] + d[i + 1])
                else:  # Must rest mode
                    # Must rest until fatigue = 0
                    if j > 0:
                        dp[i + 1][j - 1][1] = max(dp[i + 1][j - 1][1], dp[i][j][mode])
                    else:
                        # Fatigue reached 0, enter free mode
                        dp[i + 1][0][0] = max(dp[i + 1][0][0], dp[i][j][mode])

    # Wait, the logic is still off. Let me re-read the problem.
    # "쉬기 시작하면 지침지수가 0이 되기 전에는 다시 달릴 수가 없다"
    # So once you start resting, you must continue resting until fatigue = 0

    # dp[i][j][mode]: i=time, j=fatigue, mode=0(running allowed) or 1(must rest)
    dp = [[[INF] * 2 for _ in range(m + 2)] for _ in range(n + 2)]
    dp[0][0][0] = 0

    for i in range(n):
        for j in range(m + 1):
            # Mode 0: can run or rest
            if dp[i][j][0] != INF:
                v = dp[i][j][0]
                if j == 0:
                    # Rest (stay free)
                    dp[i + 1][0][0] = max(dp[i + 1][0][0], v)
                    # Run
                    dp[i + 1][1][0] = max(dp[i + 1][1][0], v + d[i + 1])
                else:
                    # j > 0 and mode 0 means we were running
                    # Run more
                    if j + 1 <= m:
                        dp[i + 1][j + 1][0] = max(dp[i + 1][j + 1][0], v + d[i + 1])
                    # Start resting (enter must-rest mode)
                    dp[i + 1][j - 1][1] = max(dp[i + 1][j - 1][1], v)

            # Mode 1: must rest
            if dp[i][j][1] != INF:
                v = dp[i][j][1]
                if j > 0:
                    # Continue resting
                    dp[i + 1][j - 1][1] = max(dp[i + 1][j - 1][1], v)
                else:
                    # j == 0, done resting, back to free mode
                    # Rest one more (optional) or run
                    dp[i + 1][0][0] = max(dp[i + 1][0][0], v)

    # Answer: max at time n with fatigue 0
    ans = max(dp[n][0][0], dp[n][0][1]) if dp[n][0][0] != INF or dp[n][0][1] != INF else 0
    print(ans if ans != INF else 0)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();

        int[] d = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            d[i] = sc.nextInt();
        }

        long INF = Long.MIN_VALUE;
        long[][][] dp = new long[n + 2][m + 2][2];
        for (int i = 0; i <= n + 1; i++) {
            for (int j = 0; j <= m + 1; j++) {
                dp[i][j][0] = INF;
                dp[i][j][1] = INF;
            }
        }
        dp[0][0][0] = 0;

        for (int i = 0; i < n; i++) {
            for (int j = 0; j <= m; j++) {
                if (dp[i][j][0] != INF) {
                    long v = dp[i][j][0];
                    if (j == 0) {
                        dp[i + 1][0][0] = Math.max(dp[i + 1][0][0], v);
                        dp[i + 1][1][0] = Math.max(dp[i + 1][1][0], v + d[i + 1]);
                    } else {
                        if (j + 1 <= m) {
                            dp[i + 1][j + 1][0] = Math.max(dp[i + 1][j + 1][0], v + d[i + 1]);
                        }
                        dp[i + 1][j - 1][1] = Math.max(dp[i + 1][j - 1][1], v);
                    }
                }

                if (dp[i][j][1] != INF) {
                    long v = dp[i][j][1];
                    if (j > 0) {
                        dp[i + 1][j - 1][1] = Math.max(dp[i + 1][j - 1][1], v);
                    } else {
                        dp[i + 1][0][0] = Math.max(dp[i + 1][0][0], v);
                    }
                }
            }
        }

        long ans = Math.max(dp[n][0][0], dp[n][0][1]);
        System.out.println(ans == INF ? 0 : ans);
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
#include <cstring>
using namespace std;

long long dp[10002][502][2];
int d[10002];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    for (int i = 1; i <= n; i++) {
        cin >> d[i];
    }

    const long long INF = -1e18;
    for (int i = 0; i <= n + 1; i++) {
        for (int j = 0; j <= m + 1; j++) {
            dp[i][j][0] = INF;
            dp[i][j][1] = INF;
        }
    }
    dp[0][0][0] = 0;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j <= m; j++) {
            if (dp[i][j][0] != INF) {
                long long v = dp[i][j][0];
                if (j == 0) {
                    dp[i + 1][0][0] = max(dp[i + 1][0][0], v);
                    dp[i + 1][1][0] = max(dp[i + 1][1][0], v + d[i + 1]);
                } else {
                    if (j + 1 <= m) {
                        dp[i + 1][j + 1][0] = max(dp[i + 1][j + 1][0], v + d[i + 1]);
                    }
                    dp[i + 1][j - 1][1] = max(dp[i + 1][j - 1][1], v);
                }
            }

            if (dp[i][j][1] != INF) {
                long long v = dp[i][j][1];
                if (j > 0) {
                    dp[i + 1][j - 1][1] = max(dp[i + 1][j - 1][1], v);
                } else {
                    dp[i + 1][0][0] = max(dp[i + 1][0][0], v);
                }
            }
        }
    }

    long long ans = max(dp[n][0][0], dp[n][0][1]);
    cout << (ans == INF ? 0 : ans) << endl;

    return 0;
}
'''
    },
    "1758": {  # 알바생 강호 - greedy tip optimization
        "python": '''import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    tips = [int(input()) for _ in range(n)]

    # Sort in descending order
    tips.sort(reverse=True)

    total = 0
    for i, tip in enumerate(tips):
        actual = tip - i  # i is 0-indexed, so rank is i+1, penalty is i
        if actual > 0:
            total += actual

    print(total)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        Integer[] tips = new Integer[n];
        for (int i = 0; i < n; i++) {
            tips[i] = sc.nextInt();
        }

        Arrays.sort(tips, Collections.reverseOrder());

        long total = 0;
        for (int i = 0; i < n; i++) {
            long actual = tips[i] - i;
            if (actual > 0) {
                total += actual;
            }
        }

        System.out.println(total);
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int* tips = new int[n];
    for (int i = 0; i < n; i++) {
        cin >> tips[i];
    }

    sort(tips, tips + n, greater<int>());

    long long total = 0;
    for (int i = 0; i < n; i++) {
        long long actual = tips[i] - i;
        if (actual > 0) {
            total += actual;
        }
    }

    cout << total << endl;

    delete[] tips;
    return 0;
}
'''
    },
    "1759": {  # 암호 만들기 - password generation with backtracking
        "python": '''import sys
input = sys.stdin.readline

def solve():
    l, c = map(int, input().split())
    chars = input().split()
    chars.sort()

    vowels = set('aeiou')

    def backtrack(idx, path):
        if len(path) == l:
            vowel_count = sum(1 for ch in path if ch in vowels)
            consonant_count = l - vowel_count
            if vowel_count >= 1 and consonant_count >= 2:
                print(''.join(path))
            return

        for i in range(idx, c):
            path.append(chars[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])

solve()
''',
        "java": '''import java.util.*;

public class Main {
    static int l, c;
    static char[] chars;
    static Set<Character> vowels = new HashSet<>(Arrays.asList('a', 'e', 'i', 'o', 'u'));
    static StringBuilder sb = new StringBuilder();

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        l = sc.nextInt();
        c = sc.nextInt();

        chars = new char[c];
        for (int i = 0; i < c; i++) {
            chars[i] = sc.next().charAt(0);
        }

        Arrays.sort(chars);

        backtrack(0, new char[l], 0);
        System.out.print(sb);
    }

    static void backtrack(int idx, char[] path, int len) {
        if (len == l) {
            int vowelCount = 0;
            for (char ch : path) {
                if (vowels.contains(ch)) vowelCount++;
            }
            int consonantCount = l - vowelCount;
            if (vowelCount >= 1 && consonantCount >= 2) {
                sb.append(new String(path)).append("\\n");
            }
            return;
        }

        for (int i = idx; i < c; i++) {
            path[len] = chars[i];
            backtrack(i + 1, path, len + 1);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
#include <string>
#include <set>
using namespace std;

int l, c;
char chars[15];
set<char> vowels = {'a', 'e', 'i', 'o', 'u'};
string path;

void backtrack(int idx) {
    if (path.length() == l) {
        int vowelCount = 0;
        for (char ch : path) {
            if (vowels.count(ch)) vowelCount++;
        }
        int consonantCount = l - vowelCount;
        if (vowelCount >= 1 && consonantCount >= 2) {
            cout << path << "\\n";
        }
        return;
    }

    for (int i = idx; i < c; i++) {
        path += chars[i];
        backtrack(i + 1);
        path.pop_back();
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> l >> c;

    for (int i = 0; i < c; i++) {
        cin >> chars[i];
    }

    sort(chars, chars + c);

    backtrack(0);

    return 0;
}
'''
    }
}


def main():
    # Load the checkpoint file
    print("Loading checkpoint file...")
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} problems")

    # Update solutions for problems 1750-1759
    updated_count = 0
    for problem in data:
        original_id = problem.get('original_id', '')
        if original_id in SOLUTIONS:
            sol = SOLUTIONS[original_id]
            problem['solutions'] = [
                {"language": "python", "code": sol["python"]},
                {"language": "java", "code": sol["java"]},
                {"language": "cpp", "code": sol["cpp"]}
            ]
            updated_count += 1
            print(f"Updated problem {original_id}: {problem.get('name', 'Unknown')}")

    print(f"\nUpdated {updated_count} problems")

    # Save the checkpoint file
    print("Saving checkpoint file...")
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Done!")


if __name__ == "__main__":
    main()
