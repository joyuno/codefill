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

# Problem 1950: Map label placement
solutions['1950'] = [
    {"language": "python", "code": """import sys
input = sys.stdin.readline

n = int(input())
cities = []
for _ in range(n):
    x, y = map(int, input().split())
    cities.append((x, y))

def can_place(size):
    # Label is width=3*size, height=size, placed at lower-right of city
    # Check if all labels don't overlap with each other and other cities
    for i in range(n):
        x1, y1 = cities[i]
        # Label i: [x1, x1+3*size] x [y1-size, y1]
        for j in range(i + 1, n):
            x2, y2 = cities[j]
            # Check if labels overlap
            # Label j: [x2, x2+3*size] x [y2-size, y2]
            if not (x1 + 3*size <= x2 or x2 + 3*size <= x1 or y1 - size >= y2 or y2 - size >= y1):
                return False
    return True

lo, hi = 0.0, 1e8
for _ in range(100):
    mid = (lo + hi) / 2
    if can_place(mid):
        lo = mid
    else:
        hi = mid

print(f"{lo:.2f}")
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    static int n;
    static int[][] cities;

    static boolean canPlace(double size) {
        for (int i = 0; i < n; i++) {
            double x1 = cities[i][0], y1 = cities[i][1];
            for (int j = i + 1; j < n; j++) {
                double x2 = cities[j][0], y2 = cities[j][1];
                if (!(x1 + 3*size <= x2 || x2 + 3*size <= x1 || y1 - size >= y2 || y2 - size >= y1))
                    return false;
            }
        }
        return true;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        n = Integer.parseInt(br.readLine().trim());
        cities = new int[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            cities[i][0] = Integer.parseInt(st.nextToken());
            cities[i][1] = Integer.parseInt(st.nextToken());
        }

        double lo = 0, hi = 1e8;
        for (int i = 0; i < 100; i++) {
            double mid = (lo + hi) / 2;
            if (canPlace(mid)) lo = mid;
            else hi = mid;
        }
        System.out.printf("%.2f%n", lo);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
#include <iomanip>
using namespace std;

int n;
int cities[101][2];

bool canPlace(double size) {
    for (int i = 0; i < n; i++) {
        double x1 = cities[i][0], y1 = cities[i][1];
        for (int j = i + 1; j < n; j++) {
            double x2 = cities[j][0], y2 = cities[j][1];
            if (!(x1 + 3*size <= x2 || x2 + 3*size <= x1 || y1 - size >= y2 || y2 - size >= y1))
                return false;
        }
    }
    return true;
}

int main() {
    cin >> n;
    for (int i = 0; i < n; i++) cin >> cities[i][0] >> cities[i][1];

    double lo = 0, hi = 1e8;
    for (int i = 0; i < 100; i++) {
        double mid = (lo + hi) / 2;
        if (canPlace(mid)) lo = mid;
        else hi = mid;
    }
    cout << fixed << setprecision(2) << lo << endl;
    return 0;
}"""}
]

# Problem 1951: Digit count to N
solutions['1951'] = [
    {"language": "python", "code": """n = int(input())
MOD = 1234567

def count_digits(n):
    if n <= 0:
        return 0
    result = 0
    digits = 1
    start = 1
    while start <= n:
        end = start * 10 - 1
        if end > n:
            end = n
        result = (result + (end - start + 1) * digits) % MOD
        digits += 1
        start *= 10
    return result

print(count_digits(n))
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        long n = Long.parseLong(br.readLine().trim());
        long MOD = 1234567;

        long result = 0;
        int digits = 1;
        long start = 1;
        while (start <= n) {
            long end = start * 10 - 1;
            if (end > n) end = n;
            result = (result + (end - start + 1) % MOD * digits % MOD) % MOD;
            digits++;
            start *= 10;
        }
        System.out.println(result);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
using namespace std;

int main() {
    long long n;
    cin >> n;
    long long MOD = 1234567;

    long long result = 0;
    int digits = 1;
    long long start = 1;
    while (start <= n) {
        long long end = start * 10 - 1;
        if (end > n) end = n;
        result = (result + (end - start + 1) % MOD * digits % MOD) % MOD;
        digits++;
        start *= 10;
    }
    cout << result << endl;
    return 0;
}"""}
]

# Problem 1952: Snail corner count
solutions['1952'] = [
    {"language": "python", "code": """m, n = map(int, input().split())
# Count how many times the snail turns
# It fills an m x n grid in a spiral

if m == 1 or n == 1:
    print(0)
else:
    turns = 0
    while m > 0 and n > 0:
        if m == 1:
            turns += 0
            break
        if n == 1:
            turns += 0
            break
        turns += 2  # Two turns for each layer
        m -= 2
        n -= 2
    # Adjust for the last incomplete turns
    print(2 * (min((m + 1) // 2, (n + 1) // 2) + min(m // 2, n // 2)) - 1 if min(m, n) >= 1 else 0)
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int m = Integer.parseInt(st.nextToken());
        int n = Integer.parseInt(st.nextToken());

        if (m == 1 || n == 1) {
            System.out.println(0);
        } else {
            int turns = (Math.min(m, n) - 1) * 2 + (Math.max(m, n) > Math.min(m, n) ? 1 : 0);
            System.out.println(Math.max(0, turns));
        }
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    int m, n;
    cin >> m >> n;

    if (m == 1 || n == 1) {
        cout << 0 << endl;
    } else {
        int turns = (min(m, n) - 1) * 2 + (max(m, n) > min(m, n) ? 1 : 0);
        cout << max(0, turns) << endl;
    }
    return 0;
}"""}
]

# Problem 1953: Team division (bipartite)
solutions['1953'] = [
    {"language": "python", "code": """import sys
from collections import deque
input = sys.stdin.readline

n = int(input())
dislike = [[] for _ in range(n + 1)]

for i in range(1, n + 1):
    line = list(map(int, input().split()))
    cnt = line[0]
    for j in range(1, cnt + 1):
        dislike[i].append(line[j])

color = [0] * (n + 1)
team1, team2 = [], []

for start in range(1, n + 1):
    if color[start] == 0:
        queue = deque([start])
        color[start] = 1
        while queue:
            node = queue.popleft()
            for neighbor in dislike[node]:
                if color[neighbor] == 0:
                    color[neighbor] = 3 - color[node]
                    queue.append(neighbor)

for i in range(1, n + 1):
    if color[i] == 1:
        team1.append(i)
    else:
        team2.append(i)

print(len(team1))
print(' '.join(map(str, team1)))
print(len(team2))
print(' '.join(map(str, team2)))
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        List<List<Integer>> dislike = new ArrayList<>();
        for (int i = 0; i <= n; i++) dislike.add(new ArrayList<>());

        for (int i = 1; i <= n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int cnt = Integer.parseInt(st.nextToken());
            for (int j = 0; j < cnt; j++) {
                dislike.get(i).add(Integer.parseInt(st.nextToken()));
            }
        }

        int[] color = new int[n + 1];
        for (int start = 1; start <= n; start++) {
            if (color[start] == 0) {
                Queue<Integer> queue = new LinkedList<>();
                queue.offer(start);
                color[start] = 1;
                while (!queue.isEmpty()) {
                    int node = queue.poll();
                    for (int neighbor : dislike.get(node)) {
                        if (color[neighbor] == 0) {
                            color[neighbor] = 3 - color[node];
                            queue.offer(neighbor);
                        }
                    }
                }
            }
        }

        List<Integer> team1 = new ArrayList<>(), team2 = new ArrayList<>();
        for (int i = 1; i <= n; i++) {
            if (color[i] == 1) team1.add(i);
            else team2.add(i);
        }

        StringBuilder sb = new StringBuilder();
        sb.append(team1.size()).append("\\n");
        for (int i = 0; i < team1.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(team1.get(i));
        }
        sb.append("\\n").append(team2.size()).append("\\n");
        for (int i = 0; i < team2.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(team2.get(i));
        }
        System.out.println(sb);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
#include <vector>
#include <queue>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<vector<int>> dislike(n + 1);
    for (int i = 1; i <= n; i++) {
        int cnt;
        cin >> cnt;
        for (int j = 0; j < cnt; j++) {
            int x;
            cin >> x;
            dislike[i].push_back(x);
        }
    }

    vector<int> color(n + 1, 0);
    for (int start = 1; start <= n; start++) {
        if (color[start] == 0) {
            queue<int> q;
            q.push(start);
            color[start] = 1;
            while (!q.empty()) {
                int node = q.front(); q.pop();
                for (int neighbor : dislike[node]) {
                    if (color[neighbor] == 0) {
                        color[neighbor] = 3 - color[node];
                        q.push(neighbor);
                    }
                }
            }
        }
    }

    vector<int> team1, team2;
    for (int i = 1; i <= n; i++) {
        if (color[i] == 1) team1.push_back(i);
        else team2.push_back(i);
    }

    cout << team1.size() << "\\n";
    for (int i = 0; i < team1.size(); i++) {
        if (i > 0) cout << " ";
        cout << team1[i];
    }
    cout << "\\n" << team2.size() << "\\n";
    for (int i = 0; i < team2.size(); i++) {
        if (i > 0) cout << " ";
        cout << team2[i];
    }
    cout << "\\n";
    return 0;
}"""}
]

# Problem 1956: Minimum cycle (Floyd-Warshall)
solutions['1956'] = [
    {"language": "python", "code": """import sys
input = sys.stdin.readline
INF = float('inf')

V, E = map(int, input().split())
dist = [[INF] * (V + 1) for _ in range(V + 1)]

for _ in range(E):
    a, b, c = map(int, input().split())
    dist[a][b] = min(dist[a][b], c)

for k in range(1, V + 1):
    for i in range(1, V + 1):
        for j in range(1, V + 1):
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

ans = INF
for i in range(1, V + 1):
    ans = min(ans, dist[i][i])

print(-1 if ans == INF else ans)
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int V = Integer.parseInt(st.nextToken());
        int E = Integer.parseInt(st.nextToken());

        int INF = 100000000;
        int[][] dist = new int[V + 1][V + 1];
        for (int[] row : dist) Arrays.fill(row, INF);

        for (int i = 0; i < E; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            int c = Integer.parseInt(st.nextToken());
            dist[a][b] = Math.min(dist[a][b], c);
        }

        for (int k = 1; k <= V; k++) {
            for (int i = 1; i <= V; i++) {
                for (int j = 1; j <= V; j++) {
                    dist[i][j] = Math.min(dist[i][j], dist[i][k] + dist[k][j]);
                }
            }
        }

        int ans = INF;
        for (int i = 1; i <= V; i++) {
            ans = Math.min(ans, dist[i][i]);
        }
        System.out.println(ans == INF ? -1 : ans);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
#include <algorithm>
using namespace std;

int dist[401][401];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int V, E;
    cin >> V >> E;

    int INF = 100000000;
    for (int i = 1; i <= V; i++)
        for (int j = 1; j <= V; j++)
            dist[i][j] = INF;

    for (int i = 0; i < E; i++) {
        int a, b, c;
        cin >> a >> b >> c;
        dist[a][b] = min(dist[a][b], c);
    }

    for (int k = 1; k <= V; k++)
        for (int i = 1; i <= V; i++)
            for (int j = 1; j <= V; j++)
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);

    int ans = INF;
    for (int i = 1; i <= V; i++)
        ans = min(ans, dist[i][i]);

    cout << (ans == INF ? -1 : ans) << endl;
    return 0;
}"""}
]

# Problem 1958: LCS of 3 strings
solutions['1958'] = [
    {"language": "python", "code": """a = input().strip()
b = input().strip()
c = input().strip()

la, lb, lc = len(a), len(b), len(c)
dp = [[[0] * (lc + 1) for _ in range(lb + 1)] for _ in range(la + 1)]

for i in range(1, la + 1):
    for j in range(1, lb + 1):
        for k in range(1, lc + 1):
            if a[i-1] == b[j-1] == c[k-1]:
                dp[i][j][k] = dp[i-1][j-1][k-1] + 1
            else:
                dp[i][j][k] = max(dp[i-1][j][k], dp[i][j-1][k], dp[i][j][k-1])

print(dp[la][lb][lc])
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String a = br.readLine().trim();
        String b = br.readLine().trim();
        String c = br.readLine().trim();

        int la = a.length(), lb = b.length(), lc = c.length();
        int[][][] dp = new int[la + 1][lb + 1][lc + 1];

        for (int i = 1; i <= la; i++) {
            for (int j = 1; j <= lb; j++) {
                for (int k = 1; k <= lc; k++) {
                    if (a.charAt(i-1) == b.charAt(j-1) && b.charAt(j-1) == c.charAt(k-1)) {
                        dp[i][j][k] = dp[i-1][j-1][k-1] + 1;
                    } else {
                        dp[i][j][k] = Math.max(Math.max(dp[i-1][j][k], dp[i][j-1][k]), dp[i][j][k-1]);
                    }
                }
            }
        }
        System.out.println(dp[la][lb][lc]);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int dp[101][101][101];

int main() {
    string a, b, c;
    cin >> a >> b >> c;

    int la = a.length(), lb = b.length(), lc = c.length();

    for (int i = 1; i <= la; i++) {
        for (int j = 1; j <= lb; j++) {
            for (int k = 1; k <= lc; k++) {
                if (a[i-1] == b[j-1] && b[j-1] == c[k-1]) {
                    dp[i][j][k] = dp[i-1][j-1][k-1] + 1;
                } else {
                    dp[i][j][k] = max({dp[i-1][j][k], dp[i][j-1][k], dp[i][j][k-1]});
                }
            }
        }
    }
    cout << dp[la][lb][lc] << endl;
    return 0;
}"""}
]

# Problem 1963: Prime path (BFS)
solutions['1963'] = [
    {"language": "python", "code": """import sys
from collections import deque
input = sys.stdin.readline

def sieve(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return is_prime

is_prime = sieve(9999)

def bfs(start, end):
    if start == end:
        return 0
    visited = [False] * 10000
    queue = deque([(start, 0)])
    visited[start] = True

    while queue:
        num, dist = queue.popleft()
        s = str(num).zfill(4)

        for i in range(4):
            for d in '0123456789':
                if i == 0 and d == '0':
                    continue
                new_s = s[:i] + d + s[i+1:]
                new_num = int(new_s)
                if new_num == end:
                    return dist + 1
                if is_prime[new_num] and not visited[new_num]:
                    visited[new_num] = True
                    queue.append((new_num, dist + 1))
    return -1

t = int(input())
for _ in range(t):
    a, b = map(int, input().split())
    result = bfs(a, b)
    print(result if result != -1 else "Impossible")
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    static boolean[] isPrime = new boolean[10000];

    static void sieve() {
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;
        for (int i = 2; i * i < 10000; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j < 10000; j += i) {
                    isPrime[j] = false;
                }
            }
        }
    }

    static int bfs(int start, int end) {
        if (start == end) return 0;
        boolean[] visited = new boolean[10000];
        Queue<int[]> queue = new LinkedList<>();
        queue.offer(new int[]{start, 0});
        visited[start] = true;

        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            int num = cur[0], dist = cur[1];
            String s = String.format("%04d", num);

            for (int i = 0; i < 4; i++) {
                for (char d = '0'; d <= '9'; d++) {
                    if (i == 0 && d == '0') continue;
                    String newS = s.substring(0, i) + d + s.substring(i + 1);
                    int newNum = Integer.parseInt(newS);
                    if (newNum == end) return dist + 1;
                    if (isPrime[newNum] && !visited[newNum]) {
                        visited[newNum] = true;
                        queue.offer(new int[]{newNum, dist + 1});
                    }
                }
            }
        }
        return -1;
    }

    public static void main(String[] args) throws IOException {
        sieve();
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());
        StringBuilder sb = new StringBuilder();
        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            int result = bfs(a, b);
            sb.append(result == -1 ? "Impossible" : result).append("\\n");
        }
        System.out.print(sb);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
#include <queue>
#include <cstring>
using namespace std;

bool isPrime[10000];

void sieve() {
    memset(isPrime, true, sizeof(isPrime));
    isPrime[0] = isPrime[1] = false;
    for (int i = 2; i * i < 10000; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j < 10000; j += i) {
                isPrime[j] = false;
            }
        }
    }
}

int bfs(int start, int end) {
    if (start == end) return 0;
    bool visited[10000] = {false};
    queue<pair<int,int>> q;
    q.push({start, 0});
    visited[start] = true;

    while (!q.empty()) {
        auto [num, dist] = q.front(); q.pop();

        for (int i = 0; i < 4; i++) {
            for (char d = '0'; d <= '9'; d++) {
                if (i == 0 && d == '0') continue;
                int newNum = num;
                int digit = d - '0';
                int pos = 1;
                for (int j = 0; j < 3 - i; j++) pos *= 10;
                newNum = (num / (pos * 10)) * (pos * 10) + digit * pos + (num % pos);

                if (newNum == end) return dist + 1;
                if (isPrime[newNum] && !visited[newNum]) {
                    visited[newNum] = true;
                    q.push({newNum, dist + 1});
                }
            }
        }
    }
    return -1;
}

int main() {
    sieve();
    int t;
    cin >> t;
    while (t--) {
        int a, b;
        cin >> a >> b;
        int result = bfs(a, b);
        if (result == -1) cout << "Impossible" << "\\n";
        else cout << result << "\\n";
    }
    return 0;
}"""}
]

# Problem 1964: Pentagon points
solutions['1964'] = [
    {"language": "python", "code": """n = int(input())
MOD = 45678

# n-th pentagon number formula: n(3n-1)/2
# For stage n: 5 + 7 + 10 + ... pattern
# After analysis: formula is (3n^2 + n + 2) / 2 = (3n^2 + n + 2) // 2

# Stage 1: 5 points
# Stage 2: 5 + 7 = 12
# Stage 3: 5 + 7 + 10 = 22

# Formula: 5 + sum of (3 + 4*i) for i from 1 to n-1
# = 5 + 3(n-1) + 4*(1+2+...+(n-1))
# = 5 + 3n - 3 + 4*(n-1)*n/2
# = 5 + 3n - 3 + 2n(n-1)
# = 5 + 3n - 3 + 2n^2 - 2n
# = 2n^2 + n + 2

result = ((3 * n * n + n + 2) // 2) % MOD
print(result)
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        long n = Long.parseLong(br.readLine().trim());
        long MOD = 45678;
        long result = ((3 * n % MOD * n % MOD + n + 2) % MOD * 22840 % MOD) % MOD;
        // 22840 is modular inverse of 2 mod 45678
        System.out.println(result);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
using namespace std;

int main() {
    long long n;
    cin >> n;
    long long MOD = 45678;
    // (3n^2 + n + 2) / 2 mod 45678
    long long result = ((3 * n % MOD * n % MOD + n + 2) % MOD * 22840 % MOD) % MOD;
    cout << result << endl;
    return 0;
}"""}
]

# Problem 1965: LIS (box stacking)
solutions['1965'] = [
    {"language": "python", "code": """n = int(input())
arr = list(map(int, input().split()))

dp = [1] * n
for i in range(1, n):
    for j in range(i):
        if arr[j] < arr[i]:
            dp[i] = max(dp[i], dp[j] + 1)

print(max(dp))
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = Integer.parseInt(st.nextToken());

        int[] dp = new int[n];
        Arrays.fill(dp, 1);
        for (int i = 1; i < n; i++) {
            for (int j = 0; j < i; j++) {
                if (arr[j] < arr[i]) dp[i] = Math.max(dp[i], dp[j] + 1);
            }
        }

        int max = 0;
        for (int x : dp) max = Math.max(max, x);
        System.out.println(max);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    int n;
    cin >> n;
    int arr[1001], dp[1001];
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
        dp[i] = 1;
    }

    for (int i = 1; i < n; i++) {
        for (int j = 0; j < i; j++) {
            if (arr[j] < arr[i]) dp[i] = max(dp[i], dp[j] + 1);
        }
    }

    cout << *max_element(dp, dp + n) << endl;
    return 0;
}"""}
]

# Problem 1966: Printer queue
solutions['1966'] = [
    {"language": "python", "code": """import sys
from collections import deque
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n, m = map(int, input().split())
    priorities = list(map(int, input().split()))

    queue = deque((i, p) for i, p in enumerate(priorities))
    count = 0

    while queue:
        idx, priority = queue.popleft()
        if any(p > priority for _, p in queue):
            queue.append((idx, priority))
        else:
            count += 1
            if idx == m:
                print(count)
                break
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());
        StringBuilder sb = new StringBuilder();

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int m = Integer.parseInt(st.nextToken());

            st = new StringTokenizer(br.readLine());
            Queue<int[]> queue = new LinkedList<>();
            for (int i = 0; i < n; i++) {
                queue.offer(new int[]{i, Integer.parseInt(st.nextToken())});
            }

            int count = 0;
            while (!queue.isEmpty()) {
                int[] cur = queue.poll();
                boolean hasHigher = false;
                for (int[] item : queue) {
                    if (item[1] > cur[1]) { hasHigher = true; break; }
                }
                if (hasHigher) {
                    queue.offer(cur);
                } else {
                    count++;
                    if (cur[0] == m) {
                        sb.append(count).append("\\n");
                        break;
                    }
                }
            }
        }
        System.out.print(sb);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
#include <queue>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int n, m;
        cin >> n >> m;

        queue<pair<int,int>> q;
        priority_queue<int> pq;

        for (int i = 0; i < n; i++) {
            int p;
            cin >> p;
            q.push({i, p});
            pq.push(p);
        }

        int count = 0;
        while (!q.empty()) {
            auto [idx, priority] = q.front();
            q.pop();
            if (priority < pq.top()) {
                q.push({idx, priority});
            } else {
                pq.pop();
                count++;
                if (idx == m) {
                    cout << count << "\\n";
                    break;
                }
            }
        }
    }
    return 0;
}"""}
]

# Problem 1967: Tree diameter
solutions['1967'] = [
    {"language": "python", "code": """import sys
from collections import deque
sys.setrecursionlimit(100001)
input = sys.stdin.readline

n = int(input())
if n == 1:
    print(0)
else:
    adj = [[] for _ in range(n + 1)]
    for _ in range(n - 1):
        p, c, w = map(int, input().split())
        adj[p].append((c, w))
        adj[c].append((p, w))

    def bfs(start):
        dist = [-1] * (n + 1)
        dist[start] = 0
        queue = deque([start])
        farthest = start
        max_dist = 0
        while queue:
            node = queue.popleft()
            for neighbor, weight in adj[node]:
                if dist[neighbor] == -1:
                    dist[neighbor] = dist[node] + weight
                    queue.append(neighbor)
                    if dist[neighbor] > max_dist:
                        max_dist = dist[neighbor]
                        farthest = neighbor
        return farthest, max_dist

    farthest1, _ = bfs(1)
    _, diameter = bfs(farthest1)
    print(diameter)
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    static List<List<int[]>> adj;
    static int n;

    static int[] bfs(int start) {
        int[] dist = new int[n + 1];
        Arrays.fill(dist, -1);
        dist[start] = 0;
        Queue<Integer> queue = new LinkedList<>();
        queue.offer(start);
        int farthest = start, maxDist = 0;
        while (!queue.isEmpty()) {
            int node = queue.poll();
            for (int[] edge : adj.get(node)) {
                int neighbor = edge[0], weight = edge[1];
                if (dist[neighbor] == -1) {
                    dist[neighbor] = dist[node] + weight;
                    queue.offer(neighbor);
                    if (dist[neighbor] > maxDist) {
                        maxDist = dist[neighbor];
                        farthest = neighbor;
                    }
                }
            }
        }
        return new int[]{farthest, maxDist};
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        n = Integer.parseInt(br.readLine().trim());
        if (n == 1) { System.out.println(0); return; }

        adj = new ArrayList<>();
        for (int i = 0; i <= n; i++) adj.add(new ArrayList<>());

        for (int i = 0; i < n - 1; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int p = Integer.parseInt(st.nextToken());
            int c = Integer.parseInt(st.nextToken());
            int w = Integer.parseInt(st.nextToken());
            adj.get(p).add(new int[]{c, w});
            adj.get(c).add(new int[]{p, w});
        }

        int[] result1 = bfs(1);
        int[] result2 = bfs(result1[0]);
        System.out.println(result2[1]);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
#include <vector>
#include <queue>
#include <cstring>
using namespace std;

int n;
vector<pair<int,int>> adj[10001];

pair<int,int> bfs(int start) {
    int dist[10001];
    memset(dist, -1, sizeof(dist));
    dist[start] = 0;
    queue<int> q;
    q.push(start);
    int farthest = start, maxDist = 0;
    while (!q.empty()) {
        int node = q.front(); q.pop();
        for (auto& [neighbor, weight] : adj[node]) {
            if (dist[neighbor] == -1) {
                dist[neighbor] = dist[node] + weight;
                q.push(neighbor);
                if (dist[neighbor] > maxDist) {
                    maxDist = dist[neighbor];
                    farthest = neighbor;
                }
            }
        }
    }
    return {farthest, maxDist};
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;
    if (n == 1) { cout << 0 << endl; return 0; }

    for (int i = 0; i < n - 1; i++) {
        int p, c, w;
        cin >> p >> c >> w;
        adj[p].push_back({c, w});
        adj[c].push_back({p, w});
    }

    auto [farthest1, _] = bfs(1);
    auto [_, diameter] = bfs(farthest1);
    cout << diameter << endl;
    return 0;
}"""}
]

# Problem 1976: Trip planning (Union-Find)
solutions['1976'] = [
    {"language": "python", "code": """import sys
input = sys.stdin.readline

def find(parent, x):
    if parent[x] != x:
        parent[x] = find(parent, parent[x])
    return parent[x]

def union(parent, x, y):
    px, py = find(parent, x), find(parent, y)
    if px != py:
        parent[py] = px

n = int(input())
m = int(input())

parent = list(range(n + 1))

for i in range(1, n + 1):
    row = list(map(int, input().split()))
    for j in range(1, n + 1):
        if row[j - 1] == 1:
            union(parent, i, j)

plan = list(map(int, input().split()))

root = find(parent, plan[0])
possible = all(find(parent, city) == root for city in plan)

print("YES" if possible else "NO")
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    static int[] parent;

    static int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    }

    static void union(int x, int y) {
        int px = find(x), py = find(y);
        if (px != py) parent[py] = px;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        int m = Integer.parseInt(br.readLine().trim());

        parent = new int[n + 1];
        for (int i = 0; i <= n; i++) parent[i] = i;

        for (int i = 1; i <= n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 1; j <= n; j++) {
                if (Integer.parseInt(st.nextToken()) == 1) {
                    union(i, j);
                }
            }
        }

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] plan = new int[m];
        for (int i = 0; i < m; i++) plan[i] = Integer.parseInt(st.nextToken());

        int root = find(plan[0]);
        boolean possible = true;
        for (int city : plan) {
            if (find(city) != root) { possible = false; break; }
        }
        System.out.println(possible ? "YES" : "NO");
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
using namespace std;

int parent[201];

int find_p(int x) {
    if (parent[x] != x) parent[x] = find_p(parent[x]);
    return parent[x];
}

void unite(int x, int y) {
    int px = find_p(x), py = find_p(y);
    if (px != py) parent[py] = px;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    for (int i = 0; i <= n; i++) parent[i] = i;

    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= n; j++) {
            int x;
            cin >> x;
            if (x == 1) unite(i, j);
        }
    }

    int plan[1001];
    for (int i = 0; i < m; i++) cin >> plan[i];

    int root = find_p(plan[0]);
    bool possible = true;
    for (int i = 0; i < m; i++) {
        if (find_p(plan[i]) != root) { possible = false; break; }
    }
    cout << (possible ? "YES" : "NO") << endl;
    return 0;
}"""}
]

# Problem 1987: Alphabet path
solutions['1987'] = [
    {"language": "python", "code": """import sys
input = sys.stdin.readline

R, C = map(int, input().split())
board = [input().strip() for _ in range(R)]

dx = [0, 0, 1, -1]
dy = [1, -1, 0, 0]

max_len = 0

def dfs(x, y, visited, length):
    global max_len
    max_len = max(max_len, length)

    for i in range(4):
        nx, ny = x + dx[i], y + dy[i]
        if 0 <= nx < R and 0 <= ny < C:
            c = board[nx][ny]
            if c not in visited:
                visited.add(c)
                dfs(nx, ny, visited, length + 1)
                visited.remove(c)

visited = {board[0][0]}
dfs(0, 0, visited, 1)
print(max_len)
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    static int R, C, maxLen = 0;
    static char[][] board;
    static int[] dx = {0, 0, 1, -1};
    static int[] dy = {1, -1, 0, 0};

    static void dfs(int x, int y, int visited, int length) {
        maxLen = Math.max(maxLen, length);
        for (int i = 0; i < 4; i++) {
            int nx = x + dx[i], ny = y + dy[i];
            if (nx >= 0 && nx < R && ny >= 0 && ny < C) {
                int bit = 1 << (board[nx][ny] - 'A');
                if ((visited & bit) == 0) {
                    dfs(nx, ny, visited | bit, length + 1);
                }
            }
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        R = Integer.parseInt(st.nextToken());
        C = Integer.parseInt(st.nextToken());
        board = new char[R][C];
        for (int i = 0; i < R; i++) board[i] = br.readLine().toCharArray();

        int visited = 1 << (board[0][0] - 'A');
        dfs(0, 0, visited, 1);
        System.out.println(maxLen);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
using namespace std;

int R, C, maxLen = 0;
char board[21][21];
int dx[] = {0, 0, 1, -1};
int dy[] = {1, -1, 0, 0};

void dfs(int x, int y, int visited, int length) {
    maxLen = max(maxLen, length);
    for (int i = 0; i < 4; i++) {
        int nx = x + dx[i], ny = y + dy[i];
        if (nx >= 0 && nx < R && ny >= 0 && ny < C) {
            int bit = 1 << (board[nx][ny] - 'A');
            if (!(visited & bit)) {
                dfs(nx, ny, visited | bit, length + 1);
            }
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> R >> C;
    for (int i = 0; i < R; i++) cin >> board[i];

    int visited = 1 << (board[0][0] - 'A');
    dfs(0, 0, visited, 1);
    cout << maxLen << endl;
    return 0;
}"""}
]

# Problem 1990: Prime palindromes
solutions['1990'] = [
    {"language": "python", "code": """import sys

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

def generate_palindromes(min_val, max_val):
    result = []
    # 1 digit
    for i in range(1, 10):
        if min_val <= i <= max_val:
            result.append(i)
    # 2 digits
    for i in range(1, 10):
        num = i * 11
        if min_val <= num <= max_val:
            result.append(num)
    # 3 digits
    for i in range(1, 10):
        for j in range(0, 10):
            num = i * 101 + j * 10
            if min_val <= num <= max_val:
                result.append(num)
    # 4 digits
    for i in range(1, 10):
        for j in range(0, 10):
            num = i * 1001 + j * 110
            if min_val <= num <= max_val:
                result.append(num)
    # 5 digits
    for i in range(1, 10):
        for j in range(0, 10):
            for k in range(0, 10):
                num = i * 10001 + j * 1010 + k * 100
                if min_val <= num <= max_val:
                    result.append(num)
    # 6 digits
    for i in range(1, 10):
        for j in range(0, 10):
            for k in range(0, 10):
                num = i * 100001 + j * 10010 + k * 1100
                if min_val <= num <= max_val:
                    result.append(num)
    # 7 digits
    for i in range(1, 10):
        for j in range(0, 10):
            for k in range(0, 10):
                for l in range(0, 10):
                    num = i * 1000001 + j * 100010 + k * 10100 + l * 1000
                    if min_val <= num <= max_val:
                        result.append(num)
    # 8 digits
    for i in range(1, 10):
        for j in range(0, 10):
            for k in range(0, 10):
                for l in range(0, 10):
                    num = i * 10000001 + j * 1000010 + k * 100100 + l * 11000
                    if min_val <= num <= max_val:
                        result.append(num)
    return sorted(result)

a, b = map(int, input().split())
palindromes = generate_palindromes(a, b)

for p in palindromes:
    if is_prime(p):
        print(p)

print(-1)
"""},
    {"language": "java", "code": """import java.util.*;
import java.io.*;

public class Main {
    static boolean isPrime(int n) {
        if (n < 2) return false;
        if (n == 2) return true;
        if (n % 2 == 0) return false;
        for (int i = 3; i * i <= n; i += 2) {
            if (n % i == 0) return false;
        }
        return true;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int a = Integer.parseInt(st.nextToken());
        int b = Integer.parseInt(st.nextToken());

        List<Integer> palindromes = new ArrayList<>();

        // Generate odd-length palindromes (even length > 11 are divisible by 11)
        for (int len = 1; len <= 7; len += 2) {
            int half = (len + 1) / 2;
            int start = (int)Math.pow(10, half - 1);
            int end = (int)Math.pow(10, half);
            for (int i = start; i < end; i++) {
                String s = String.valueOf(i);
                String rev = new StringBuilder(s.substring(0, half - 1)).reverse().toString();
                int num = Integer.parseInt(s + rev);
                if (num >= a && num <= b) palindromes.add(num);
            }
        }

        // Add single and double digit palindromes
        for (int i = 1; i <= 9; i++) {
            if (i >= a && i <= b) palindromes.add(i);
            int d = i * 11;
            if (d >= a && d <= b) palindromes.add(d);
        }

        Collections.sort(palindromes);
        StringBuilder sb = new StringBuilder();
        for (int p : palindromes) {
            if (isPrime(p)) sb.append(p).append("\\n");
        }
        sb.append(-1);
        System.out.println(sb);
    }
}"""},
    {"language": "cpp", "code": """#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

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
    int a, b;
    cin >> a >> b;

    vector<int> palindromes;

    // 1-digit
    for (int i = 1; i <= 9; i++) if (i >= a && i <= b) palindromes.push_back(i);
    // 2-digit
    for (int i = 1; i <= 9; i++) { int n = i * 11; if (n >= a && n <= b) palindromes.push_back(n); }
    // 3-digit
    for (int i = 1; i <= 9; i++) for (int j = 0; j <= 9; j++) { int n = i*101+j*10; if (n >= a && n <= b) palindromes.push_back(n); }
    // 5-digit
    for (int i = 1; i <= 9; i++) for (int j = 0; j <= 9; j++) for (int k = 0; k <= 9; k++) { int n = i*10001+j*1010+k*100; if (n >= a && n <= b) palindromes.push_back(n); }
    // 7-digit
    for (int i = 1; i <= 9; i++) for (int j = 0; j <= 9; j++) for (int k = 0; k <= 9; k++) for (int l = 0; l <= 9; l++) { int n = i*1000001+j*100010+k*10100+l*1000; if (n >= a && n <= b) palindromes.push_back(n); }

    sort(palindromes.begin(), palindromes.end());
    for (int p : palindromes) {
        if (isPrime(p)) cout << p << "\\n";
    }
    cout << -1 << endl;
    return 0;
}"""}
]

# Apply solutions to data
for oid, sol_list in solutions.items():
    if oid in id_to_idx:
        data[id_to_idx[oid]]['solutions'] = sol_list
        print(f"Applied solutions for problem {oid}")

# Save the updated data
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\\nSaved checkpoint file with remaining problems")
print(f"Total problems processed: {len(solutions)}")
