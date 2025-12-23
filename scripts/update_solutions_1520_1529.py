#!/usr/bin/env python3
import json

# Read the checkpoint file
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Solutions for problems 1520-1529
solutions_data = {
    "1520": [
        {
            "language": "python",
            "code": """import sys
sys.setrecursionlimit(500 * 500 + 10)
input = sys.stdin.readline

m, n = map(int, input().split())
grid = []
for _ in range(m):
    grid.append(list(map(int, input().split())))

dp = [[-1] * n for _ in range(m)]

dx = [0, 0, 1, -1]
dy = [1, -1, 0, 0]

def dfs(x, y):
    if x == m - 1 and y == n - 1:
        return 1
    if dp[x][y] != -1:
        return dp[x][y]

    dp[x][y] = 0
    for i in range(4):
        nx, ny = x + dx[i], y + dy[i]
        if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] < grid[x][y]:
            dp[x][y] += dfs(nx, ny)

    return dp[x][y]

print(dfs(0, 0))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static int m, n;
    static int[][] grid, dp;
    static int[] dx = {0, 0, 1, -1};
    static int[] dy = {1, -1, 0, 0};

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        m = Integer.parseInt(st.nextToken());
        n = Integer.parseInt(st.nextToken());

        grid = new int[m][n];
        dp = new int[m][n];

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                grid[i][j] = Integer.parseInt(st.nextToken());
                dp[i][j] = -1;
            }
        }

        System.out.println(dfs(0, 0));
    }

    static int dfs(int x, int y) {
        if (x == m - 1 && y == n - 1) return 1;
        if (dp[x][y] != -1) return dp[x][y];

        dp[x][y] = 0;
        for (int i = 0; i < 4; i++) {
            int nx = x + dx[i], ny = y + dy[i];
            if (nx >= 0 && nx < m && ny >= 0 && ny < n && grid[nx][ny] < grid[x][y]) {
                dp[x][y] += dfs(nx, ny);
            }
        }

        return dp[x][y];
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <cstring>
using namespace std;

int m, n;
int grid[501][501];
int dp[501][501];
int dx[] = {0, 0, 1, -1};
int dy[] = {1, -1, 0, 0};

int dfs(int x, int y) {
    if (x == m - 1 && y == n - 1) return 1;
    if (dp[x][y] != -1) return dp[x][y];

    dp[x][y] = 0;
    for (int i = 0; i < 4; i++) {
        int nx = x + dx[i], ny = y + dy[i];
        if (nx >= 0 && nx < m && ny >= 0 && ny < n && grid[nx][ny] < grid[x][y]) {
            dp[x][y] += dfs(nx, ny);
        }
    }

    return dp[x][y];
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> m >> n;

    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            cin >> grid[i][j];
        }
    }

    memset(dp, -1, sizeof(dp));
    cout << dfs(0, 0) << endl;

    return 0;
}"""
        }
    ],
    "1521": [
        {
            "language": "python",
            "code": """import sys
from functools import lru_cache

n = int(input())
perm = tuple(map(int, input().split()))

@lru_cache(maxsize=None)
def expected(p):
    p = list(p)
    if p == sorted(p):
        return 0.0

    inversions = []
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            if p[i] > p[j]:
                inversions.append((i, j))

    if not inversions:
        return 0.0

    total = 0.0
    for i, j in inversions:
        new_p = p[:]
        new_p[i], new_p[j] = new_p[j], new_p[i]
        total += 1 + expected(tuple(new_p))

    return total / len(inversions)

print(expected(perm))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static Map<String, Double> memo = new HashMap<>();

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] perm = new int[n];
        for (int i = 0; i < n; i++) {
            perm[i] = sc.nextInt();
        }

        System.out.println(expected(perm));
    }

    static String toKey(int[] p) {
        StringBuilder sb = new StringBuilder();
        for (int x : p) sb.append(x).append(",");
        return sb.toString();
    }

    static boolean isSorted(int[] p) {
        for (int i = 0; i < p.length - 1; i++) {
            if (p[i] > p[i + 1]) return false;
        }
        return true;
    }

    static double expected(int[] p) {
        if (isSorted(p)) return 0.0;

        String key = toKey(p);
        if (memo.containsKey(key)) return memo.get(key);

        List<int[]> inversions = new ArrayList<>();
        for (int i = 0; i < p.length; i++) {
            for (int j = i + 1; j < p.length; j++) {
                if (p[i] > p[j]) {
                    inversions.add(new int[]{i, j});
                }
            }
        }

        if (inversions.isEmpty()) return 0.0;

        double total = 0.0;
        for (int[] inv : inversions) {
            int[] newP = p.clone();
            int temp = newP[inv[0]];
            newP[inv[0]] = newP[inv[1]];
            newP[inv[1]] = temp;
            total += 1 + expected(newP);
        }

        double result = total / inversions.size();
        memo.put(key, result);
        return result;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
using namespace std;

map<vector<int>, double> memo;

bool isSorted(vector<int>& p) {
    for (int i = 0; i < p.size() - 1; i++) {
        if (p[i] > p[i + 1]) return false;
    }
    return true;
}

double expected(vector<int> p) {
    if (isSorted(p)) return 0.0;

    if (memo.count(p)) return memo[p];

    vector<pair<int, int>> inversions;
    for (int i = 0; i < p.size(); i++) {
        for (int j = i + 1; j < p.size(); j++) {
            if (p[i] > p[j]) {
                inversions.push_back({i, j});
            }
        }
    }

    if (inversions.empty()) return 0.0;

    double total = 0.0;
    for (auto& inv : inversions) {
        vector<int> newP = p;
        swap(newP[inv.first], newP[inv.second]);
        total += 1 + expected(newP);
    }

    double result = total / inversions.size();
    memo[p] = result;
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> perm(n);
    for (int i = 0; i < n; i++) {
        cin >> perm[i];
    }

    cout.precision(15);
    cout << fixed << expected(perm) << endl;

    return 0;
}"""
        }
    ],
    "1522": [
        {
            "language": "python",
            "code": """s = input().strip()
n = len(s)
a_count = s.count('a')

if a_count == 0 or a_count == n:
    print(0)
else:
    min_swaps = n
    for i in range(n):
        # Window starting at i with length a_count
        b_count = 0
        for j in range(a_count):
            if s[(i + j) % n] == 'b':
                b_count += 1
        min_swaps = min(min_swaps, b_count)

    print(min_swaps)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine().trim();
        int n = s.length();

        int aCount = 0;
        for (char c : s.toCharArray()) {
            if (c == 'a') aCount++;
        }

        if (aCount == 0 || aCount == n) {
            System.out.println(0);
            return;
        }

        int minSwaps = n;
        for (int i = 0; i < n; i++) {
            int bCount = 0;
            for (int j = 0; j < aCount; j++) {
                if (s.charAt((i + j) % n) == 'b') {
                    bCount++;
                }
            }
            minSwaps = Math.min(minSwaps, bCount);
        }

        System.out.println(minSwaps);
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

    int aCount = 0;
    for (char c : s) {
        if (c == 'a') aCount++;
    }

    if (aCount == 0 || aCount == n) {
        cout << 0 << endl;
        return 0;
    }

    int minSwaps = n;
    for (int i = 0; i < n; i++) {
        int bCount = 0;
        for (int j = 0; j < aCount; j++) {
            if (s[(i + j) % n] == 'b') {
                bCount++;
            }
        }
        minSwaps = min(minSwaps, bCount);
    }

    cout << minSwaps << endl;

    return 0;
}"""
        }
    ],
    "1523": [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

n, m = map(int, input().split())
a = []
b = []
for _ in range(n):
    x, y = map(int, input().split())
    a.append((x, y))
for _ in range(m):
    x, y = map(int, input().split())
    b.append((x, y))

a.sort()
b.sort()

i = j = 0
result = []

while i < n and j < m:
    if a[i] < b[j]:
        result.append(('A', a[i][0], a[i][1]))
        i += 1
    else:
        result.append(('B', b[j][0], b[j][1]))
        j += 1

while i < n:
    result.append(('A', a[i][0], a[i][1]))
    i += 1

while j < m:
    result.append(('B', b[j][0], b[j][1]))
    j += 1

for item in result:
    print(item[0], item[1], item[2])"""
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

        int[][] a = new int[n][2];
        int[][] b = new int[m][2];

        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            a[i][0] = Integer.parseInt(st.nextToken());
            a[i][1] = Integer.parseInt(st.nextToken());
        }

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            b[i][0] = Integer.parseInt(st.nextToken());
            b[i][1] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(a, (x, y) -> x[0] != y[0] ? x[0] - y[0] : x[1] - y[1]);
        Arrays.sort(b, (x, y) -> x[0] != y[0] ? x[0] - y[0] : x[1] - y[1]);

        StringBuilder sb = new StringBuilder();
        int i = 0, j = 0;

        while (i < n && j < m) {
            if (a[i][0] < b[j][0] || (a[i][0] == b[j][0] && a[i][1] < b[j][1])) {
                sb.append("A ").append(a[i][0]).append(" ").append(a[i][1]).append("\\n");
                i++;
            } else {
                sb.append("B ").append(b[j][0]).append(" ").append(b[j][1]).append("\\n");
                j++;
            }
        }

        while (i < n) {
            sb.append("A ").append(a[i][0]).append(" ").append(a[i][1]).append("\\n");
            i++;
        }

        while (j < m) {
            sb.append("B ").append(b[j][0]).append(" ").append(b[j][1]).append("\\n");
            j++;
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

    int n, m;
    cin >> n >> m;

    vector<pair<int, int>> a(n), b(m);

    for (int i = 0; i < n; i++) {
        cin >> a[i].first >> a[i].second;
    }

    for (int i = 0; i < m; i++) {
        cin >> b[i].first >> b[i].second;
    }

    sort(a.begin(), a.end());
    sort(b.begin(), b.end());

    int i = 0, j = 0;

    while (i < n && j < m) {
        if (a[i] < b[j]) {
            cout << "A " << a[i].first << " " << a[i].second << "\\n";
            i++;
        } else {
            cout << "B " << b[j].first << " " << b[j].second << "\\n";
            j++;
        }
    }

    while (i < n) {
        cout << "A " << a[i].first << " " << a[i].second << "\\n";
        i++;
    }

    while (j < m) {
        cout << "B " << b[j].first << " " << b[j].second << "\\n";
        j++;
    }

    return 0;
}"""
        }
    ],
    "1524": [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    input()  # empty line
    n, m = map(int, input().split())
    a = list(map(int, input().split()))
    b = list(map(int, input().split()))

    a.sort(reverse=True)
    b.sort(reverse=True)

    i = j = 0
    while i < n and j < m:
        if a[i] >= b[j]:
            j += 1
        else:
            i += 1

    if j == m:
        print('A')
    elif i == n:
        print('B')
    else:
        print('C')"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());
        StringBuilder sb = new StringBuilder();

        while (t-- > 0) {
            br.readLine();  // empty line
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int m = Integer.parseInt(st.nextToken());

            Integer[] a = new Integer[n];
            Integer[] b = new Integer[m];

            st = new StringTokenizer(br.readLine());
            for (int i = 0; i < n; i++) {
                a[i] = Integer.parseInt(st.nextToken());
            }

            st = new StringTokenizer(br.readLine());
            for (int i = 0; i < m; i++) {
                b[i] = Integer.parseInt(st.nextToken());
            }

            Arrays.sort(a, Collections.reverseOrder());
            Arrays.sort(b, Collections.reverseOrder());

            int i = 0, j = 0;
            while (i < n && j < m) {
                if (a[i] >= b[j]) {
                    j++;
                } else {
                    i++;
                }
            }

            if (j == m) {
                sb.append("A\\n");
            } else if (i == n) {
                sb.append("B\\n");
            } else {
                sb.append("C\\n");
            }
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

    int t;
    cin >> t;

    while (t--) {
        int n, m;
        cin >> n >> m;

        vector<int> a(n), b(m);

        for (int i = 0; i < n; i++) cin >> a[i];
        for (int i = 0; i < m; i++) cin >> b[i];

        sort(a.begin(), a.end(), greater<int>());
        sort(b.begin(), b.end(), greater<int>());

        int i = 0, j = 0;
        while (i < n && j < m) {
            if (a[i] >= b[j]) {
                j++;
            } else {
                i++;
            }
        }

        if (j == m) {
            cout << "A\\n";
        } else if (i == n) {
            cout << "B\\n";
        } else {
            cout << "C\\n";
        }
    }

    return 0;
}"""
        }
    ],
    "1525": [
        {
            "language": "python",
            "code": """from collections import deque

grid = []
for _ in range(3):
    row = list(map(int, input().split()))
    grid.extend(row)

start = ''.join(str(x) for x in grid)
target = '123456780'

if start == target:
    print(0)
else:
    # BFS
    moves = {
        0: [1, 3],
        1: [0, 2, 4],
        2: [1, 5],
        3: [0, 4, 6],
        4: [1, 3, 5, 7],
        5: [2, 4, 8],
        6: [3, 7],
        7: [4, 6, 8],
        8: [5, 7]
    }

    visited = {start: 0}
    queue = deque([start])

    while queue:
        state = queue.popleft()

        if state == target:
            print(visited[state])
            break

        zero_pos = state.index('0')
        for next_pos in moves[zero_pos]:
            state_list = list(state)
            state_list[zero_pos], state_list[next_pos] = state_list[next_pos], state_list[zero_pos]
            new_state = ''.join(state_list)

            if new_state not in visited:
                visited[new_state] = visited[state] + 1
                queue.append(new_state)
    else:
        print(-1)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                sb.append(sc.nextInt());
            }
        }

        String start = sb.toString();
        String target = "123456780";

        if (start.equals(target)) {
            System.out.println(0);
            return;
        }

        int[][] moves = {
            {1, 3},
            {0, 2, 4},
            {1, 5},
            {0, 4, 6},
            {1, 3, 5, 7},
            {2, 4, 8},
            {3, 7},
            {4, 6, 8},
            {5, 7}
        };

        Map<String, Integer> visited = new HashMap<>();
        Queue<String> queue = new LinkedList<>();

        visited.put(start, 0);
        queue.offer(start);

        while (!queue.isEmpty()) {
            String state = queue.poll();

            if (state.equals(target)) {
                System.out.println(visited.get(state));
                return;
            }

            int zeroPos = state.indexOf('0');
            for (int nextPos : moves[zeroPos]) {
                char[] chars = state.toCharArray();
                char temp = chars[zeroPos];
                chars[zeroPos] = chars[nextPos];
                chars[nextPos] = temp;
                String newState = new String(chars);

                if (!visited.containsKey(newState)) {
                    visited.put(newState, visited.get(state) + 1);
                    queue.offer(newState);
                }
            }
        }

        System.out.println(-1);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <queue>
#include <map>
#include <string>
using namespace std;

int moves[9][4] = {
    {1, 3, -1, -1},
    {0, 2, 4, -1},
    {1, 5, -1, -1},
    {0, 4, 6, -1},
    {1, 3, 5, 7},
    {2, 4, 8, -1},
    {3, 7, -1, -1},
    {4, 6, 8, -1},
    {5, 7, -1, -1}
};

int moveCnt[9] = {2, 3, 2, 3, 4, 3, 2, 3, 2};

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string start = "";
    for (int i = 0; i < 9; i++) {
        int x;
        cin >> x;
        start += ('0' + x);
    }

    string target = "123456780";

    if (start == target) {
        cout << 0 << endl;
        return 0;
    }

    map<string, int> visited;
    queue<string> q;

    visited[start] = 0;
    q.push(start);

    while (!q.empty()) {
        string state = q.front();
        q.pop();

        if (state == target) {
            cout << visited[state] << endl;
            return 0;
        }

        int zeroPos = state.find('0');
        for (int i = 0; i < moveCnt[zeroPos]; i++) {
            int nextPos = moves[zeroPos][i];
            string newState = state;
            swap(newState[zeroPos], newState[nextPos]);

            if (visited.find(newState) == visited.end()) {
                visited[newState] = visited[state] + 1;
                q.push(newState);
            }
        }
    }

    cout << -1 << endl;

    return 0;
}"""
        }
    ],
    "1526": [
        {
            "language": "python",
            "code": """n = int(input())

result = 0

def find_max(num):
    global result
    if num > n:
        return
    result = max(result, num)
    find_max(num * 10 + 4)
    find_max(num * 10 + 7)

find_max(4)
find_max(7)

print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static int n;
    static int result = 0;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();

        findMax(4);
        findMax(7);

        System.out.println(result);
    }

    static void findMax(long num) {
        if (num > n) return;
        result = (int)Math.max(result, num);
        findMax(num * 10 + 4);
        findMax(num * 10 + 7);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
using namespace std;

int n;
int result = 0;

void findMax(long long num) {
    if (num > n) return;
    result = max(result, (int)num);
    findMax(num * 10 + 4);
    findMax(num * 10 + 7);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;

    findMax(4);
    findMax(7);

    cout << result << endl;

    return 0;
}"""
        }
    ],
    "1527": [
        {
            "language": "python",
            "code": """a, b = map(int, input().split())

result = 0
candidates = []

def generate(num):
    if num > b:
        return
    if num >= a:
        candidates.append(num)
    generate(num * 10 + 4)
    generate(num * 10 + 7)

generate(4)
generate(7)

print(len(candidates))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static long a, b;
    static int count = 0;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        a = sc.nextLong();
        b = sc.nextLong();

        generate(4);
        generate(7);

        System.out.println(count);
    }

    static void generate(long num) {
        if (num > b) return;
        if (num >= a) count++;
        generate(num * 10 + 4);
        generate(num * 10 + 7);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
using namespace std;

long long a, b;
int cnt = 0;

void generate(long long num) {
    if (num > b) return;
    if (num >= a) cnt++;
    generate(num * 10 + 4);
    generate(num * 10 + 7);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> a >> b;

    generate(4);
    generate(7);

    cout << cnt << endl;

    return 0;
}"""
        }
    ],
    "1528": [
        {
            "language": "python",
            "code": """import sys
from collections import defaultdict
input = sys.stdin.readline

def solve():
    n = int(input())
    seqs = []
    for _ in range(n):
        seq = list(map(int, input().split()))
        seqs.append(seq[1:])

    # Use BFS to find if we can reach target sum
    target = sum(seqs[0])
    for seq in seqs:
        if sum(seq) != target:
            print(-1)
            return

    # Try to match sequences using greedy + backtracking
    # State: current index for each sequence
    from collections import deque

    start = tuple([0] * n)
    queue = deque([start])
    visited = {start: []}

    while queue:
        state = queue.popleft()
        path = visited[state]

        # Check if all sequences are complete
        if all(state[i] == len(seqs[i]) for i in range(n)):
            print(len(path))
            for x in path:
                print(x)
            return

        # Find all possible next values
        candidates = set()
        for i in range(n):
            if state[i] < len(seqs[i]):
                candidates.add(seqs[i][state[i]])

        for val in candidates:
            # Check if this value can be the next for all sequences
            new_state = list(state)
            valid = True
            for i in range(n):
                if state[i] < len(seqs[i]):
                    if seqs[i][state[i]] == val:
                        new_state[i] += 1
                    else:
                        # Check if this sequence can skip to val
                        found = False
                        for j in range(state[i], len(seqs[i])):
                            if seqs[i][j] == val:
                                new_state[i] = j + 1
                                found = True
                                break
                        if not found:
                            valid = False
                            break

            if valid:
                new_state = tuple(new_state)
                if new_state not in visited:
                    visited[new_state] = path + [val]
                    queue.append(new_state)

    print(-1)

solve()"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        int[][] seqs = new int[n][];
        for (int i = 0; i < n; i++) {
            int len = sc.nextInt();
            seqs[i] = new int[len];
            for (int j = 0; j < len; j++) {
                seqs[i][j] = sc.nextInt();
            }
        }

        int target = 0;
        for (int x : seqs[0]) target += x;

        for (int i = 1; i < n; i++) {
            int sum = 0;
            for (int x : seqs[i]) sum += x;
            if (sum != target) {
                System.out.println(-1);
                return;
            }
        }

        // BFS
        Map<String, List<Integer>> visited = new HashMap<>();
        Queue<int[]> queue = new LinkedList<>();

        int[] start = new int[n];
        queue.offer(start);
        visited.put(Arrays.toString(start), new ArrayList<>());

        while (!queue.isEmpty()) {
            int[] state = queue.poll();
            List<Integer> path = visited.get(Arrays.toString(state));

            boolean allDone = true;
            for (int i = 0; i < n; i++) {
                if (state[i] < seqs[i].length) {
                    allDone = false;
                    break;
                }
            }

            if (allDone) {
                System.out.println(path.size());
                for (int x : path) {
                    System.out.println(x);
                }
                return;
            }

            Set<Integer> candidates = new HashSet<>();
            for (int i = 0; i < n; i++) {
                if (state[i] < seqs[i].length) {
                    candidates.add(seqs[i][state[i]]);
                }
            }

            for (int val : candidates) {
                int[] newState = state.clone();
                boolean valid = true;

                for (int i = 0; i < n; i++) {
                    if (state[i] < seqs[i].length) {
                        boolean found = false;
                        for (int j = state[i]; j < seqs[i].length; j++) {
                            if (seqs[i][j] == val) {
                                newState[i] = j + 1;
                                found = true;
                                break;
                            }
                        }
                        if (!found) {
                            valid = false;
                            break;
                        }
                    }
                }

                if (valid) {
                    String key = Arrays.toString(newState);
                    if (!visited.containsKey(key)) {
                        List<Integer> newPath = new ArrayList<>(path);
                        newPath.add(val);
                        visited.put(key, newPath);
                        queue.offer(newState);
                    }
                }
            }
        }

        System.out.println(-1);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <queue>
#include <map>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<vector<int>> seqs(n);
    for (int i = 0; i < n; i++) {
        int len;
        cin >> len;
        seqs[i].resize(len);
        for (int j = 0; j < len; j++) {
            cin >> seqs[i][j];
        }
    }

    int target = 0;
    for (int x : seqs[0]) target += x;

    for (int i = 1; i < n; i++) {
        int sum = 0;
        for (int x : seqs[i]) sum += x;
        if (sum != target) {
            cout << -1 << endl;
            return 0;
        }
    }

    map<vector<int>, vector<int>> visited;
    queue<vector<int>> q;

    vector<int> start(n, 0);
    q.push(start);
    visited[start] = {};

    while (!q.empty()) {
        vector<int> state = q.front();
        q.pop();
        vector<int> path = visited[state];

        bool allDone = true;
        for (int i = 0; i < n; i++) {
            if (state[i] < seqs[i].size()) {
                allDone = false;
                break;
            }
        }

        if (allDone) {
            cout << path.size() << endl;
            for (int x : path) {
                cout << x << endl;
            }
            return 0;
        }

        set<int> candidates;
        for (int i = 0; i < n; i++) {
            if (state[i] < seqs[i].size()) {
                candidates.insert(seqs[i][state[i]]);
            }
        }

        for (int val : candidates) {
            vector<int> newState = state;
            bool valid = true;

            for (int i = 0; i < n; i++) {
                if (state[i] < seqs[i].size()) {
                    bool found = false;
                    for (int j = state[i]; j < seqs[i].size(); j++) {
                        if (seqs[i][j] == val) {
                            newState[i] = j + 1;
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                        valid = false;
                        break;
                    }
                }
            }

            if (valid && visited.find(newState) == visited.end()) {
                vector<int> newPath = path;
                newPath.push_back(val);
                visited[newState] = newPath;
                q.push(newState);
            }
        }
    }

    cout << -1 << endl;

    return 0;
}"""
        }
    ],
    "1529": [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

n = int(input())
cows = []
for _ in range(n):
    s, e, p = map(int, input().split())
    cows.append((s, e, p))

# Greedy: always pick the cow with highest priority that can be milked
# Simulate minute by minute

# Since N is small, we can use simulation
result = [0] * n
time = 1

while True:
    # Find which cows can be milked at current time
    available = []
    for i in range(n):
        s, e, p = cows[i]
        if s <= time <= e:
            available.append((p, i))

    if not available:
        # No cow available, find next available cow
        next_time = float('inf')
        for i in range(n):
            s, e, p = cows[i]
            if s > time:
                next_time = min(next_time, s)
        if next_time == float('inf'):
            break
        time = next_time
    else:
        # Milk the cow with highest priority
        available.sort(reverse=True)
        _, cow_idx = available[0]
        result[cow_idx] += 1

        # Update the cow's end time (milked one unit)
        s, e, p = cows[cow_idx]
        cows[cow_idx] = (time + 1, e, p)

        time += 1

for r in result:
    print(r)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        int[] s = new int[n];
        int[] e = new int[n];
        int[] p = new int[n];

        for (int i = 0; i < n; i++) {
            s[i] = sc.nextInt();
            e[i] = sc.nextInt();
            p[i] = sc.nextInt();
        }

        int[] result = new int[n];
        int time = 1;

        while (true) {
            int bestCow = -1;
            int bestPriority = -1;

            for (int i = 0; i < n; i++) {
                if (s[i] <= time && time <= e[i]) {
                    if (p[i] > bestPriority) {
                        bestPriority = p[i];
                        bestCow = i;
                    }
                }
            }

            if (bestCow == -1) {
                int nextTime = Integer.MAX_VALUE;
                for (int i = 0; i < n; i++) {
                    if (s[i] > time) {
                        nextTime = Math.min(nextTime, s[i]);
                    }
                }
                if (nextTime == Integer.MAX_VALUE) break;
                time = nextTime;
            } else {
                result[bestCow]++;
                s[bestCow] = time + 1;
                time++;
            }
        }

        for (int r : result) {
            System.out.println(r);
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> s(n), e(n), p(n);
    for (int i = 0; i < n; i++) {
        cin >> s[i] >> e[i] >> p[i];
    }

    vector<int> result(n, 0);
    int time = 1;

    while (true) {
        int bestCow = -1;
        int bestPriority = -1;

        for (int i = 0; i < n; i++) {
            if (s[i] <= time && time <= e[i]) {
                if (p[i] > bestPriority) {
                    bestPriority = p[i];
                    bestCow = i;
                }
            }
        }

        if (bestCow == -1) {
            int nextTime = INT_MAX;
            for (int i = 0; i < n; i++) {
                if (s[i] > time) {
                    nextTime = min(nextTime, s[i]);
                }
            }
            if (nextTime == INT_MAX) break;
            time = nextTime;
        } else {
            result[bestCow]++;
            s[bestCow] = time + 1;
            time++;
        }
    }

    for (int r : result) {
        cout << r << "\\n";
    }

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

print("Updated solutions for problems 1520-1529")
