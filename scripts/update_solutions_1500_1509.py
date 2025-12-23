#!/usr/bin/env python3
import json

# Read the checkpoint file
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Solutions for problems 1500-1509
solutions_data = {
    "1500": [
        {
            "language": "python",
            "code": """s, k = map(int, input().split())
q, r = divmod(s, k)
result = (q ** (k - r)) * ((q + 1) ** r)
print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long s = sc.nextLong();
        long k = sc.nextLong();
        long q = s / k;
        long r = s % k;
        long result = 1;
        for (int i = 0; i < k - r; i++) {
            result *= q;
        }
        for (int i = 0; i < r; i++) {
            result *= (q + 1);
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
    long long s, k;
    cin >> s >> k;
    long long q = s / k;
    long long r = s % k;
    long long result = 1;
    for (int i = 0; i < k - r; i++) {
        result *= q;
    }
    for (int i = 0; i < r; i++) {
        result *= (q + 1);
    }
    cout << result << endl;
    return 0;
}"""
        }
    ],
    "1501": [
        {
            "language": "python",
            "code": """from collections import defaultdict

def get_key(word):
    if len(word) <= 2:
        return word
    return word[0] + ''.join(sorted(word[1:-1])) + word[-1]

n = int(input())
dictionary = defaultdict(int)
for _ in range(n):
    word = input().strip()
    key = get_key(word)
    dictionary[key] += 1

m = int(input())
for _ in range(m):
    sentence = input().strip()
    if not sentence:
        print(0)
        continue
    words = sentence.split()
    result = 1
    for word in words:
        key = get_key(word)
        count = dictionary.get(key, 0)
        result *= count
    print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static String getKey(String word) {
        if (word.length() <= 2) return word;
        char[] middle = word.substring(1, word.length() - 1).toCharArray();
        Arrays.sort(middle);
        return word.charAt(0) + new String(middle) + word.charAt(word.length() - 1);
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        Map<String, Integer> dict = new HashMap<>();

        int n = Integer.parseInt(br.readLine().trim());
        for (int i = 0; i < n; i++) {
            String word = br.readLine().trim();
            String key = getKey(word);
            dict.put(key, dict.getOrDefault(key, 0) + 1);
        }

        int m = Integer.parseInt(br.readLine().trim());
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < m; i++) {
            String line = br.readLine();
            if (line == null || line.trim().isEmpty()) {
                sb.append(0).append("\\n");
                continue;
            }
            String[] words = line.trim().split(" ");
            long result = 1;
            for (String word : words) {
                if (word.isEmpty()) continue;
                String key = getKey(word);
                int count = dict.getOrDefault(key, 0);
                result *= count;
            }
            sb.append(result).append("\\n");
        }
        System.out.print(sb);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <map>
#include <sstream>
#include <algorithm>
using namespace std;

string getKey(const string& word) {
    if (word.length() <= 2) return word;
    string middle = word.substr(1, word.length() - 2);
    sort(middle.begin(), middle.end());
    return word[0] + middle + word[word.length() - 1];
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    map<string, int> dict;
    int n;
    cin >> n;
    cin.ignore();

    for (int i = 0; i < n; i++) {
        string word;
        getline(cin, word);
        string key = getKey(word);
        dict[key]++;
    }

    int m;
    cin >> m;
    cin.ignore();

    for (int i = 0; i < m; i++) {
        string line;
        getline(cin, line);
        if (line.empty()) {
            cout << 0 << "\\n";
            continue;
        }

        istringstream iss(line);
        string word;
        long long result = 1;
        while (iss >> word) {
            string key = getKey(word);
            result *= dict[key];
        }
        cout << result << "\\n";
    }

    return 0;
}"""
        }
    ],
    "1502": [
        {
            "language": "python",
            "code": """import sys
sys.setrecursionlimit(100000)

def solve():
    T = int(input())

    for _ in range(T):
        m, n = map(int, input().split())
        i1, j1 = map(int, input().split())
        i2, j2 = map(int, input().split())

        # Check parity - if both positions have same color on checkerboard, impossible
        if (i1 + j1) % 2 == (i2 + j2) % 2:
            print(-1)
            continue

        visited = [[False] * (n + 1) for _ in range(m + 1)]
        path = []
        found = [False]

        dx = [0, 0, 1, -1]
        dy = [1, -1, 0, 0]

        def dfs(x, y, cnt):
            if found[0]:
                return
            if cnt == m * n:
                if x == i2 and y == j2:
                    found[0] = True
                return

            for d in range(4):
                nx, ny = x + dx[d], y + dy[d]
                if 1 <= nx <= m and 1 <= ny <= n and not visited[nx][ny]:
                    visited[nx][ny] = True
                    path.append((nx, ny))
                    dfs(nx, ny, cnt + 1)
                    if found[0]:
                        return
                    path.pop()
                    visited[nx][ny] = False

        visited[i1][j1] = True
        path.append((i1, j1))
        dfs(i1, j1, 1)

        if found[0]:
            print(1)
            for x, y in path:
                print(x, y)
        else:
            print(-1)

solve()"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static int m, n;
    static boolean[][] visited;
    static List<int[]> path;
    static boolean found;
    static int[] dx = {0, 0, 1, -1};
    static int[] dy = {1, -1, 0, 0};
    static int targetX, targetY;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();
        StringBuilder sb = new StringBuilder();

        while (T-- > 0) {
            m = sc.nextInt();
            n = sc.nextInt();
            int i1 = sc.nextInt(), j1 = sc.nextInt();
            int i2 = sc.nextInt(), j2 = sc.nextInt();
            targetX = i2;
            targetY = j2;

            if ((i1 + j1) % 2 == (i2 + j2) % 2) {
                sb.append(-1).append("\\n");
                continue;
            }

            visited = new boolean[m + 1][n + 1];
            path = new ArrayList<>();
            found = false;

            visited[i1][j1] = true;
            path.add(new int[]{i1, j1});
            dfs(i1, j1, 1);

            if (found) {
                sb.append(1).append("\\n");
                for (int[] p : path) {
                    sb.append(p[0]).append(" ").append(p[1]).append("\\n");
                }
            } else {
                sb.append(-1).append("\\n");
            }
        }
        System.out.print(sb);
    }

    static void dfs(int x, int y, int cnt) {
        if (found) return;
        if (cnt == m * n) {
            if (x == targetX && y == targetY) found = true;
            return;
        }

        for (int d = 0; d < 4; d++) {
            int nx = x + dx[d], ny = y + dy[d];
            if (nx >= 1 && nx <= m && ny >= 1 && ny <= n && !visited[nx][ny]) {
                visited[nx][ny] = true;
                path.add(new int[]{nx, ny});
                dfs(nx, ny, cnt + 1);
                if (found) return;
                path.remove(path.size() - 1);
                visited[nx][ny] = false;
            }
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
using namespace std;

int m, n;
bool visited[9][9];
vector<pair<int,int>> path;
bool found;
int dx[] = {0, 0, 1, -1};
int dy[] = {1, -1, 0, 0};
int targetX, targetY;

void dfs(int x, int y, int cnt) {
    if (found) return;
    if (cnt == m * n) {
        if (x == targetX && y == targetY) found = true;
        return;
    }

    for (int d = 0; d < 4; d++) {
        int nx = x + dx[d], ny = y + dy[d];
        if (nx >= 1 && nx <= m && ny >= 1 && ny <= n && !visited[nx][ny]) {
            visited[nx][ny] = true;
            path.push_back({nx, ny});
            dfs(nx, ny, cnt + 1);
            if (found) return;
            path.pop_back();
            visited[nx][ny] = false;
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        cin >> m >> n;
        int i1, j1, i2, j2;
        cin >> i1 >> j1 >> i2 >> j2;
        targetX = i2;
        targetY = j2;

        if ((i1 + j1) % 2 == (i2 + j2) % 2) {
            cout << -1 << "\\n";
            continue;
        }

        for (int i = 0; i <= m; i++)
            for (int j = 0; j <= n; j++)
                visited[i][j] = false;
        path.clear();
        found = false;

        visited[i1][j1] = true;
        path.push_back({i1, j1});
        dfs(i1, j1, 1);

        if (found) {
            cout << 1 << "\\n";
            for (auto& p : path) {
                cout << p.first << " " << p.second << "\\n";
            }
        } else {
            cout << -1 << "\\n";
        }
    }

    return 0;
}"""
        }
    ],
    "1503": [
        {
            "language": "python",
            "code": """line = input().split()
n = int(line[0])
m = int(line[1])

excluded = set()
if m > 0:
    excluded = set(map(int, input().split()))

min_diff = float('inf')

# Maximum value we need to consider: since N <= 1000 and we need xyz >= something close to N
# If x, y, z are all 1, xyz = 1. We need to search smartly.
# Since N <= 1000, and we want |N - xyz|, we should search x, y, z up to about 1000

for x in range(1, 1001):
    if x in excluded:
        continue
    if x > n + min_diff:
        break
    for y in range(x, 1001):
        if y in excluded:
            continue
        if x * y > n + min_diff:
            break
        for z in range(y, 1001):
            if z in excluded:
                continue
            product = x * y * z
            diff = abs(n - product)
            if diff < min_diff:
                min_diff = diff
            if product > n + min_diff:
                break

print(min_diff)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();

        Set<Integer> excluded = new HashSet<>();
        for (int i = 0; i < m; i++) {
            excluded.add(sc.nextInt());
        }

        long minDiff = Long.MAX_VALUE;

        for (int x = 1; x <= 1000; x++) {
            if (excluded.contains(x)) continue;
            if (x > n + minDiff) break;

            for (int y = x; y <= 1000; y++) {
                if (excluded.contains(y)) continue;
                if ((long)x * y > n + minDiff) break;

                for (int z = y; z <= 1000; z++) {
                    if (excluded.contains(z)) continue;
                    long product = (long)x * y * z;
                    long diff = Math.abs(n - product);
                    if (diff < minDiff) {
                        minDiff = diff;
                    }
                    if (product > n + minDiff) break;
                }
            }
        }

        System.out.println(minDiff);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <set>
#include <cmath>
using namespace std;

int main() {
    int n, m;
    cin >> n >> m;

    set<int> excluded;
    for (int i = 0; i < m; i++) {
        int x;
        cin >> x;
        excluded.insert(x);
    }

    long long minDiff = LLONG_MAX;

    for (int x = 1; x <= 1000; x++) {
        if (excluded.count(x)) continue;
        if (x > n + minDiff) break;

        for (int y = x; y <= 1000; y++) {
            if (excluded.count(y)) continue;
            if ((long long)x * y > n + minDiff) break;

            for (int z = y; z <= 1000; z++) {
                if (excluded.count(z)) continue;
                long long product = (long long)x * y * z;
                long long diff = abs(n - product);
                if (diff < minDiff) {
                    minDiff = diff;
                }
                if (product > n + minDiff) break;
            }
        }
    }

    cout << minDiff << endl;
    return 0;
}"""
        }
    ],
    "1504": [
        {
            "language": "python",
            "code": """import heapq
import sys
input = sys.stdin.readline

def dijkstra(start, graph, n):
    dist = [float('inf')] * (n + 1)
    dist[start] = 0
    heap = [(0, start)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))

    return dist

n, e = map(int, input().split())
graph = [[] for _ in range(n + 1)]

for _ in range(e):
    a, b, c = map(int, input().split())
    graph[a].append((b, c))
    graph[b].append((a, c))

v1, v2 = map(int, input().split())

dist1 = dijkstra(1, graph, n)
distV1 = dijkstra(v1, graph, n)
distV2 = dijkstra(v2, graph, n)

# Path 1: 1 -> v1 -> v2 -> n
# Path 2: 1 -> v2 -> v1 -> n
path1 = dist1[v1] + distV1[v2] + distV2[n]
path2 = dist1[v2] + distV2[v1] + distV1[n]

result = min(path1, path2)

if result >= float('inf'):
    print(-1)
else:
    print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

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
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            int c = Integer.parseInt(st.nextToken());
            graph[a].add(new int[]{b, c});
            graph[b].add(new int[]{a, c});
        }

        st = new StringTokenizer(br.readLine());
        int v1 = Integer.parseInt(st.nextToken());
        int v2 = Integer.parseInt(st.nextToken());

        long[] dist1 = dijkstra(1);
        long[] distV1 = dijkstra(v1);
        long[] distV2 = dijkstra(v2);

        long path1 = dist1[v1] + distV1[v2] + distV2[n];
        long path2 = dist1[v2] + distV2[v1] + distV1[n];

        long result = Math.min(path1, path2);

        if (result >= 200000001) {
            System.out.println(-1);
        } else {
            System.out.println(result);
        }
    }

    static long[] dijkstra(int start) {
        long[] dist = new long[n + 1];
        Arrays.fill(dist, 200000001);
        dist[start] = 0;

        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        pq.offer(new long[]{0, start});

        while (!pq.isEmpty()) {
            long[] curr = pq.poll();
            long d = curr[0];
            int u = (int)curr[1];

            if (d > dist[u]) continue;

            for (int[] edge : graph[u]) {
                int v = edge[0];
                int w = edge[1];
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                    pq.offer(new long[]{dist[v], v});
                }
            }
        }

        return dist;
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

typedef pair<long long, int> pli;
const long long INF = 200000001;

int n, e;
vector<pair<int, int>> graph[801];

vector<long long> dijkstra(int start) {
    vector<long long> dist(n + 1, INF);
    dist[start] = 0;
    priority_queue<pli, vector<pli>, greater<pli>> pq;
    pq.push({0, start});

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

    return dist;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> e;

    for (int i = 0; i < e; i++) {
        int a, b, c;
        cin >> a >> b >> c;
        graph[a].push_back({b, c});
        graph[b].push_back({a, c});
    }

    int v1, v2;
    cin >> v1 >> v2;

    vector<long long> dist1 = dijkstra(1);
    vector<long long> distV1 = dijkstra(v1);
    vector<long long> distV2 = dijkstra(v2);

    long long path1 = dist1[v1] + distV1[v2] + distV2[n];
    long long path2 = dist1[v2] + distV2[v1] + distV1[n];

    long long result = min(path1, path2);

    if (result >= INF) {
        cout << -1 << endl;
    } else {
        cout << result << endl;
    }

    return 0;
}"""
        }
    ],
    "1505": [
        {
            "language": "python",
            "code": """import sys

def solve():
    line = input().split()
    n, m = int(line[0]), int(line[1])

    board = []
    for _ in range(n):
        row = input().strip()
        board.append([1 if c == '*' else 0 for c in row])

    target = [[1] * m for _ in range(n)]

    dx = [-1, -1, -1, 0, 0, 0, 1, 1, 1]
    dy = [-1, 0, 1, -1, 0, 1, -1, 0, 1]

    def toggle(grid, x, y):
        for i in range(9):
            nx, ny = x + dx[i], y + dy[i]
            if 0 <= nx < n and 0 <= ny < m:
                grid[nx][ny] ^= 1

    def check(first_row_mask):
        grid = [row[:] for row in board]
        cnt = 0

        for j in range(m):
            if (first_row_mask >> j) & 1:
                toggle(grid, 0, j)
                cnt += 1

        for i in range(1, n):
            for j in range(m):
                if grid[i-1][j] != target[i-1][j]:
                    toggle(grid, i, j)
                    cnt += 1

        if grid == target:
            return cnt
        return -1

    min_cnt = float('inf')

    for mask in range(1 << m):
        result = check(mask)
        if result != -1 and result < min_cnt:
            min_cnt = result

    if min_cnt == float('inf'):
        print(-1)
    else:
        print(min_cnt)

solve()"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static int n, m;
    static int[] dx = {-1, -1, -1, 0, 0, 0, 1, 1, 1};
    static int[] dy = {-1, 0, 1, -1, 0, 1, -1, 0, 1};

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();
        m = sc.nextInt();
        sc.nextLine();

        int[][] board = new int[n][m];
        for (int i = 0; i < n; i++) {
            String line = sc.nextLine();
            for (int j = 0; j < m; j++) {
                board[i][j] = line.charAt(j) == '*' ? 1 : 0;
            }
        }

        int minCnt = Integer.MAX_VALUE;

        for (int mask = 0; mask < (1 << m); mask++) {
            int result = check(board, mask);
            if (result != -1 && result < minCnt) {
                minCnt = result;
            }
        }

        System.out.println(minCnt == Integer.MAX_VALUE ? -1 : minCnt);
    }

    static void toggle(int[][] grid, int x, int y) {
        for (int i = 0; i < 9; i++) {
            int nx = x + dx[i], ny = y + dy[i];
            if (nx >= 0 && nx < n && ny >= 0 && ny < m) {
                grid[nx][ny] ^= 1;
            }
        }
    }

    static int check(int[][] board, int firstRowMask) {
        int[][] grid = new int[n][m];
        for (int i = 0; i < n; i++) {
            grid[i] = board[i].clone();
        }

        int cnt = 0;

        for (int j = 0; j < m; j++) {
            if (((firstRowMask >> j) & 1) == 1) {
                toggle(grid, 0, j);
                cnt++;
            }
        }

        for (int i = 1; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (grid[i-1][j] != 1) {
                    toggle(grid, i, j);
                    cnt++;
                }
            }
        }

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (grid[i][j] != 1) return -1;
            }
        }

        return cnt;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <climits>
using namespace std;

int n, m;
int dx[] = {-1, -1, -1, 0, 0, 0, 1, 1, 1};
int dy[] = {-1, 0, 1, -1, 0, 1, -1, 0, 1};

void toggle(vector<vector<int>>& grid, int x, int y) {
    for (int i = 0; i < 9; i++) {
        int nx = x + dx[i], ny = y + dy[i];
        if (nx >= 0 && nx < n && ny >= 0 && ny < m) {
            grid[nx][ny] ^= 1;
        }
    }
}

int check(vector<vector<int>>& board, int firstRowMask) {
    vector<vector<int>> grid = board;
    int cnt = 0;

    for (int j = 0; j < m; j++) {
        if ((firstRowMask >> j) & 1) {
            toggle(grid, 0, j);
            cnt++;
        }
    }

    for (int i = 1; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (grid[i-1][j] != 1) {
                toggle(grid, i, j);
                cnt++;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (grid[i][j] != 1) return -1;
        }
    }

    return cnt;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> m;
    vector<vector<int>> board(n, vector<int>(m));

    for (int i = 0; i < n; i++) {
        string line;
        cin >> line;
        for (int j = 0; j < m; j++) {
            board[i][j] = (line[j] == '*') ? 1 : 0;
        }
    }

    int minCnt = INT_MAX;

    for (int mask = 0; mask < (1 << m); mask++) {
        int result = check(board, mask);
        if (result != -1 && result < minCnt) {
            minCnt = result;
        }
    }

    cout << (minCnt == INT_MAX ? -1 : minCnt) << endl;

    return 0;
}"""
        }
    ],
    "1506": [
        {
            "language": "python",
            "code": """import sys
sys.setrecursionlimit(200)

def solve():
    n = int(input())
    costs = list(map(int, input().split()))

    graph = [[] for _ in range(n)]
    for i in range(n):
        row = input().strip()
        for j in range(n):
            if row[j] == '1':
                graph[i].append(j)

    # Tarjan's algorithm for SCC
    idx = [0]
    stack = []
    on_stack = [False] * n
    index = [-1] * n
    lowlink = [-1] * n
    scc_id = [-1] * n
    scc_count = [0]

    def strongconnect(v):
        index[v] = idx[0]
        lowlink[v] = idx[0]
        idx[0] += 1
        stack.append(v)
        on_stack[v] = True

        for w in graph[v]:
            if index[w] == -1:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack[w]:
                lowlink[v] = min(lowlink[v], index[w])

        if lowlink[v] == index[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc_id[w] = scc_count[0]
                scc.append(w)
                if w == v:
                    break
            scc_count[0] += 1

    for v in range(n):
        if index[v] == -1:
            strongconnect(v)

    # Find minimum cost for each SCC
    scc_min_cost = [float('inf')] * scc_count[0]
    for v in range(n):
        scc_min_cost[scc_id[v]] = min(scc_min_cost[scc_id[v]], costs[v])

    print(sum(scc_min_cost))

solve()"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static int n;
    static List<Integer>[] graph;
    static int idx = 0;
    static int[] index, lowlink, sccId;
    static boolean[] onStack;
    static Stack<Integer> stack;
    static int sccCount = 0;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();

        int[] costs = new int[n];
        for (int i = 0; i < n; i++) {
            costs[i] = sc.nextInt();
        }
        sc.nextLine();

        graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < n; i++) {
            String row = sc.nextLine();
            for (int j = 0; j < n; j++) {
                if (row.charAt(j) == '1') {
                    graph[i].add(j);
                }
            }
        }

        index = new int[n];
        lowlink = new int[n];
        sccId = new int[n];
        onStack = new boolean[n];
        Arrays.fill(index, -1);
        stack = new Stack<>();

        for (int v = 0; v < n; v++) {
            if (index[v] == -1) {
                strongconnect(v);
            }
        }

        int[] sccMinCost = new int[sccCount];
        Arrays.fill(sccMinCost, Integer.MAX_VALUE);

        for (int v = 0; v < n; v++) {
            sccMinCost[sccId[v]] = Math.min(sccMinCost[sccId[v]], costs[v]);
        }

        long total = 0;
        for (int cost : sccMinCost) {
            total += cost;
        }

        System.out.println(total);
    }

    static void strongconnect(int v) {
        index[v] = idx;
        lowlink[v] = idx;
        idx++;
        stack.push(v);
        onStack[v] = true;

        for (int w : graph[v]) {
            if (index[w] == -1) {
                strongconnect(w);
                lowlink[v] = Math.min(lowlink[v], lowlink[w]);
            } else if (onStack[w]) {
                lowlink[v] = Math.min(lowlink[v], index[w]);
            }
        }

        if (lowlink[v] == index[v]) {
            while (true) {
                int w = stack.pop();
                onStack[w] = false;
                sccId[w] = sccCount;
                if (w == v) break;
            }
            sccCount++;
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
using namespace std;

int n;
vector<int> graph[101];
int idx_counter = 0;
int index_arr[101], lowlink[101], sccId[101];
bool onStack[101];
stack<int> st;
int sccCount = 0;

void strongconnect(int v) {
    index_arr[v] = idx_counter;
    lowlink[v] = idx_counter;
    idx_counter++;
    st.push(v);
    onStack[v] = true;

    for (int w : graph[v]) {
        if (index_arr[w] == -1) {
            strongconnect(w);
            lowlink[v] = min(lowlink[v], lowlink[w]);
        } else if (onStack[w]) {
            lowlink[v] = min(lowlink[v], index_arr[w]);
        }
    }

    if (lowlink[v] == index_arr[v]) {
        while (true) {
            int w = st.top();
            st.pop();
            onStack[w] = false;
            sccId[w] = sccCount;
            if (w == v) break;
        }
        sccCount++;
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;

    int costs[101];
    for (int i = 0; i < n; i++) {
        cin >> costs[i];
    }

    for (int i = 0; i < n; i++) {
        string row;
        cin >> row;
        for (int j = 0; j < n; j++) {
            if (row[j] == '1') {
                graph[i].push_back(j);
            }
        }
    }

    fill(index_arr, index_arr + n, -1);
    fill(onStack, onStack + n, false);

    for (int v = 0; v < n; v++) {
        if (index_arr[v] == -1) {
            strongconnect(v);
        }
    }

    int sccMinCost[101];
    fill(sccMinCost, sccMinCost + sccCount, INT_MAX);

    for (int v = 0; v < n; v++) {
        sccMinCost[sccId[v]] = min(sccMinCost[sccId[v]], costs[v]);
    }

    long long total = 0;
    for (int i = 0; i < sccCount; i++) {
        total += sccMinCost[i];
    }

    cout << total << endl;

    return 0;
}"""
        }
    ],
    "1507": [
        {
            "language": "python",
            "code": """n = int(input())
dist = []
for _ in range(n):
    dist.append(list(map(int, input().split())))

# Check if the given distances are valid
# and find which edges are necessary
necessary = [[True] * n for _ in range(n)]

for k in range(n):
    for i in range(n):
        for j in range(n):
            if i != j and i != k and j != k:
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    print(-1)
                    exit()
                if dist[i][j] == dist[i][k] + dist[k][j]:
                    necessary[i][j] = False

total = 0
for i in range(n):
    for j in range(i + 1, n):
        if necessary[i][j]:
            total += dist[i][j]

print(total)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        int[][] dist = new int[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                dist[i][j] = sc.nextInt();
            }
        }

        boolean[][] necessary = new boolean[n][n];
        for (int i = 0; i < n; i++) {
            Arrays.fill(necessary[i], true);
        }

        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (i != j && i != k && j != k) {
                        if (dist[i][j] > dist[i][k] + dist[k][j]) {
                            System.out.println(-1);
                            return;
                        }
                        if (dist[i][j] == dist[i][k] + dist[k][j]) {
                            necessary[i][j] = false;
                        }
                    }
                }
            }
        }

        int total = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (necessary[i][j]) {
                    total += dist[i][j];
                }
            }
        }

        System.out.println(total);
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

    int n;
    cin >> n;

    int dist[21][21];
    bool necessary[21][21];

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cin >> dist[i][j];
            necessary[i][j] = true;
        }
    }

    for (int k = 0; k < n; k++) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (i != j && i != k && j != k) {
                    if (dist[i][j] > dist[i][k] + dist[k][j]) {
                        cout << -1 << endl;
                        return 0;
                    }
                    if (dist[i][j] == dist[i][k] + dist[k][j]) {
                        necessary[i][j] = false;
                    }
                }
            }
        }
    }

    int total = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (necessary[i][j]) {
                total += dist[i][j];
            }
        }
    }

    cout << total << endl;

    return 0;
}"""
        }
    ],
    "1508": [
        {
            "language": "python",
            "code": """def can_place(positions, m, min_dist):
    count = 1
    last = positions[0]
    for i in range(1, len(positions)):
        if positions[i] - last >= min_dist:
            count += 1
            last = positions[i]
    return count >= m

def find_placement(positions, m, min_dist):
    result = ['0'] * len(positions)
    count = 1
    last = 0
    result[0] = '1'

    for i in range(1, len(positions)):
        if positions[i] - positions[last] >= min_dist:
            count += 1
            result[i] = '1'
            last = i

    return result, count

n, m, k = map(int, input().split())
positions = list(map(int, input().split()))

# Binary search for maximum minimum distance
left, right = 0, positions[-1] - positions[0]
answer_dist = 0

while left <= right:
    mid = (left + right) // 2
    if can_place(positions, m, mid):
        answer_dist = mid
        left = mid + 1
    else:
        right = mid - 1

# Find lexicographically largest placement
# Try placing from the end
result = ['0'] * k
placed = 0
last_pos = float('inf')

for i in range(k - 1, -1, -1):
    remaining = i + 1
    need = m - placed

    if remaining < need:
        continue

    if last_pos - positions[i] >= answer_dist or placed == 0:
        if remaining == need or can_place_remaining(positions, i, need, answer_dist):
            result[i] = '1'
            last_pos = positions[i]
            placed += 1

    if placed == m:
        break

def can_place_remaining(positions, end_idx, need, min_dist):
    count = 0
    last = -float('inf')
    for i in range(end_idx + 1):
        if positions[i] - last >= min_dist:
            count += 1
            last = positions[i]
    return count >= need

# Re-solve with correct approach
result = ['0'] * k
for i in range(k - 1, -1, -1):
    result[i] = '1'
    temp = [j for j in range(k) if result[j] == '1']

    valid = True
    if len(temp) > m:
        valid = False
    else:
        # Check if we can still place remaining judges
        remaining_spots = i
        remaining_judges = m - len(temp)

        if remaining_judges > remaining_spots:
            valid = False
        else:
            # Check minimum distance
            for x in range(len(temp) - 1):
                if positions[temp[x + 1]] - positions[temp[x]] < answer_dist:
                    valid = False
                    break

            if valid and remaining_judges > 0:
                # Check if remaining judges can be placed
                test_positions = [positions[j] for j in temp]
                # Try to add remaining_judges before position i
                cnt = 0
                last = -float('inf')
                for j in range(i):
                    if result[j] == '0' and positions[j] - last >= answer_dist:
                        if len(temp) == 0 or positions[j] + answer_dist <= positions[temp[0]]:
                            cnt += 1
                            last = positions[j]
                if cnt < remaining_judges:
                    valid = False

    if not valid:
        result[i] = '0'

print(''.join(result))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static int[] positions;
    static int k, m;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        m = sc.nextInt();
        k = sc.nextInt();

        positions = new int[k];
        for (int i = 0; i < k; i++) {
            positions[i] = sc.nextInt();
        }

        int left = 0, right = positions[k-1] - positions[0];
        int answerDist = 0;

        while (left <= right) {
            int mid = (left + right) / 2;
            if (canPlace(mid)) {
                answerDist = mid;
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        StringBuilder result = new StringBuilder();
        int placed = 0;
        int lastPos = -1000001;

        for (int i = 0; i < k; i++) {
            if (positions[i] - lastPos >= answerDist) {
                int remaining = k - i - 1;
                int need = m - placed - 1;

                if (canPlaceRemaining(i + 1, positions[i], need, answerDist)) {
                    result.append('1');
                    lastPos = positions[i];
                    placed++;
                } else {
                    result.append('0');
                }
            } else {
                result.append('0');
            }

            if (placed == m) {
                while (result.length() < k) {
                    result.append('0');
                }
                break;
            }
        }

        System.out.println(result.toString());
    }

    static boolean canPlace(int minDist) {
        int count = 1;
        int last = positions[0];
        for (int i = 1; i < k; i++) {
            if (positions[i] - last >= minDist) {
                count++;
                last = positions[i];
            }
        }
        return count >= m;
    }

    static boolean canPlaceRemaining(int start, int lastPos, int need, int minDist) {
        if (need <= 0) return true;
        int count = 0;
        int last = lastPos;
        for (int i = start; i < k; i++) {
            if (positions[i] - last >= minDist) {
                count++;
                last = positions[i];
            }
        }
        return count >= need;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <string>
using namespace std;

int positions[51];
int k, m;

bool canPlace(int minDist) {
    int count = 1;
    int last = positions[0];
    for (int i = 1; i < k; i++) {
        if (positions[i] - last >= minDist) {
            count++;
            last = positions[i];
        }
    }
    return count >= m;
}

bool canPlaceRemaining(int start, int lastPos, int need, int minDist) {
    if (need <= 0) return true;
    int count = 0;
    int last = lastPos;
    for (int i = start; i < k; i++) {
        if (positions[i] - last >= minDist) {
            count++;
            last = positions[i];
        }
    }
    return count >= need;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n >> m >> k;

    for (int i = 0; i < k; i++) {
        cin >> positions[i];
    }

    int left = 0, right = positions[k-1] - positions[0];
    int answerDist = 0;

    while (left <= right) {
        int mid = (left + right) / 2;
        if (canPlace(mid)) {
            answerDist = mid;
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    string result = "";
    int placed = 0;
    int lastPos = -1000001;

    for (int i = 0; i < k; i++) {
        if (positions[i] - lastPos >= answerDist) {
            int need = m - placed - 1;

            if (canPlaceRemaining(i + 1, positions[i], need, answerDist)) {
                result += '1';
                lastPos = positions[i];
                placed++;
            } else {
                result += '0';
            }
        } else {
            result += '0';
        }

        if (placed == m) {
            while (result.length() < k) {
                result += '0';
            }
            break;
        }
    }

    cout << result << endl;

    return 0;
}"""
        }
    ],
    "1509": [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

s = input().strip()
n = len(s)

# is_palindrome[i][j] = True if s[i:j+1] is a palindrome
is_palindrome = [[False] * n for _ in range(n)]

for i in range(n):
    is_palindrome[i][i] = True

for i in range(n - 1):
    if s[i] == s[i + 1]:
        is_palindrome[i][i + 1] = True

for length in range(3, n + 1):
    for i in range(n - length + 1):
        j = i + length - 1
        if s[i] == s[j] and is_palindrome[i + 1][j - 1]:
            is_palindrome[i][j] = True

# dp[i] = minimum number of palindrome partitions for s[0:i]
dp = [float('inf')] * (n + 1)
dp[0] = 0

for i in range(1, n + 1):
    for j in range(i):
        if is_palindrome[j][i - 1]:
            dp[i] = min(dp[i], dp[j] + 1)

print(dp[n])"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine().trim();
        int n = s.length();

        boolean[][] isPalindrome = new boolean[n][n];

        for (int i = 0; i < n; i++) {
            isPalindrome[i][i] = true;
        }

        for (int i = 0; i < n - 1; i++) {
            if (s.charAt(i) == s.charAt(i + 1)) {
                isPalindrome[i][i + 1] = true;
            }
        }

        for (int len = 3; len <= n; len++) {
            for (int i = 0; i <= n - len; i++) {
                int j = i + len - 1;
                if (s.charAt(i) == s.charAt(j) && isPalindrome[i + 1][j - 1]) {
                    isPalindrome[i][j] = true;
                }
            }
        }

        int[] dp = new int[n + 1];
        Arrays.fill(dp, Integer.MAX_VALUE);
        dp[0] = 0;

        for (int i = 1; i <= n; i++) {
            for (int j = 0; j < i; j++) {
                if (isPalindrome[j][i - 1]) {
                    dp[i] = Math.min(dp[i], dp[j] + 1);
                }
            }
        }

        System.out.println(dp[n]);
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

    string s;
    cin >> s;
    int n = s.length();

    bool isPalindrome[2501][2501] = {false};

    for (int i = 0; i < n; i++) {
        isPalindrome[i][i] = true;
    }

    for (int i = 0; i < n - 1; i++) {
        if (s[i] == s[i + 1]) {
            isPalindrome[i][i + 1] = true;
        }
    }

    for (int len = 3; len <= n; len++) {
        for (int i = 0; i <= n - len; i++) {
            int j = i + len - 1;
            if (s[i] == s[j] && isPalindrome[i + 1][j - 1]) {
                isPalindrome[i][j] = true;
            }
        }
    }

    int dp[2501];
    fill(dp, dp + n + 1, 2501);
    dp[0] = 0;

    for (int i = 1; i <= n; i++) {
        for (int j = 0; j < i; j++) {
            if (isPalindrome[j][i - 1]) {
                dp[i] = min(dp[i], dp[j] + 1);
            }
        }
    }

    cout << dp[n] << endl;

    return 0;
}"""
        }
    ]
}

# Update the JSON data
for problem in data:
    original_id = problem.get("original_id", "")
    if original_id in solutions_data:
        problem["solutions"] = solutions_data[original_id]

# Write back to the file
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated solutions for problems 1500-1509")
