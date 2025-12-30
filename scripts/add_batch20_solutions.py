#!/usr/bin/env python3
"""배치 20: 기본 알고리즘 medium 문제 솔루션 추가"""

import json

new_solutions = {
    "baekjoon_2579": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 계단 오르기 - DP
import sys
input = sys.stdin.readline

n = int(input())
stairs = [0] + [int(input()) for _ in range(n)]

if n == 1:
    print(stairs[1])
elif n == 2:
    print(stairs[1] + stairs[2])
else:
    # dp[i] = i번째 계단에 도달했을 때 최대 점수
    dp = [0] * (n + 1)
    dp[1] = stairs[1]
    dp[2] = stairs[1] + stairs[2]

    for i in range(3, n + 1):
        # i-2에서 2칸 점프 또는 i-3에서 1칸씩 2번 점프 후 마지막 1칸 점프
        dp[i] = max(dp[i-2] + stairs[i], dp[i-3] + stairs[i-1] + stairs[i])

    print(dp[n])
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int stairs[301] = {0};
    int dp[301] = {0};

    for (int i = 1; i <= n; i++) {
        cin >> stairs[i];
    }

    if (n == 1) {
        cout << stairs[1] << endl;
    } else if (n == 2) {
        cout << stairs[1] + stairs[2] << endl;
    } else {
        dp[1] = stairs[1];
        dp[2] = stairs[1] + stairs[2];

        for (int i = 3; i <= n; i++) {
            dp[i] = max(dp[i-2] + stairs[i], dp[i-3] + stairs[i-1] + stairs[i]);
        }

        cout << dp[n] << endl;
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine());
        int[] stairs = new int[n + 1];
        int[] dp = new int[n + 1];

        for (int i = 1; i <= n; i++) {
            stairs[i] = Integer.parseInt(br.readLine());
        }

        if (n == 1) {
            System.out.println(stairs[1]);
        } else if (n == 2) {
            System.out.println(stairs[1] + stairs[2]);
        } else {
            dp[1] = stairs[1];
            dp[2] = stairs[1] + stairs[2];

            for (int i = 3; i <= n; i++) {
                dp[i] = Math.max(dp[i-2] + stairs[i], dp[i-3] + stairs[i-1] + stairs[i]);
            }

            System.out.println(dp[n]);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_1012": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 유기농 배추 - DFS/BFS로 연결 요소 개수 세기
import sys
from collections import deque
sys.setrecursionlimit(10000)
input = sys.stdin.readline

def bfs(x, y, field, visited, m, n):
    queue = deque([(x, y)])
    visited[x][y] = True
    dx = [0, 0, 1, -1]
    dy = [1, -1, 0, 0]

    while queue:
        cx, cy = queue.popleft()
        for i in range(4):
            nx, ny = cx + dx[i], cy + dy[i]
            if 0 <= nx < m and 0 <= ny < n:
                if field[nx][ny] == 1 and not visited[nx][ny]:
                    visited[nx][ny] = True
                    queue.append((nx, ny))

t = int(input())
for _ in range(t):
    m, n, k = map(int, input().split())
    field = [[0] * n for _ in range(m)]
    visited = [[False] * n for _ in range(m)]

    for _ in range(k):
        x, y = map(int, input().split())
        field[x][y] = 1

    count = 0
    for i in range(m):
        for j in range(n):
            if field[i][j] == 1 and not visited[i][j]:
                bfs(i, j, field, visited, m, n)
                count += 1

    print(count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <cstring>
#include <queue>
using namespace std;

int m, n, k;
int field[50][50];
bool visited[50][50];
int dx[] = {0, 0, 1, -1};
int dy[] = {1, -1, 0, 0};

void bfs(int x, int y) {
    queue<pair<int, int>> q;
    q.push({x, y});
    visited[x][y] = true;

    while (!q.empty()) {
        int cx = q.front().first;
        int cy = q.front().second;
        q.pop();

        for (int i = 0; i < 4; i++) {
            int nx = cx + dx[i];
            int ny = cy + dy[i];

            if (nx >= 0 && nx < m && ny >= 0 && ny < n) {
                if (field[nx][ny] == 1 && !visited[nx][ny]) {
                    visited[nx][ny] = true;
                    q.push({nx, ny});
                }
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
        cin >> m >> n >> k;

        memset(field, 0, sizeof(field));
        memset(visited, false, sizeof(visited));

        for (int i = 0; i < k; i++) {
            int x, y;
            cin >> x >> y;
            field[x][y] = 1;
        }

        int count = 0;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (field[i][j] == 1 && !visited[i][j]) {
                    bfs(i, j);
                    count++;
                }
            }
        }

        cout << count << "\\n";
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int m, n;
    static int[][] field;
    static boolean[][] visited;
    static int[] dx = {0, 0, 1, -1};
    static int[] dy = {1, -1, 0, 0};

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            m = Integer.parseInt(st.nextToken());
            n = Integer.parseInt(st.nextToken());
            int k = Integer.parseInt(st.nextToken());

            field = new int[m][n];
            visited = new boolean[m][n];

            for (int i = 0; i < k; i++) {
                st = new StringTokenizer(br.readLine());
                int x = Integer.parseInt(st.nextToken());
                int y = Integer.parseInt(st.nextToken());
                field[x][y] = 1;
            }

            int count = 0;
            for (int i = 0; i < m; i++) {
                for (int j = 0; j < n; j++) {
                    if (field[i][j] == 1 && !visited[i][j]) {
                        bfs(i, j);
                        count++;
                    }
                }
            }

            sb.append(count).append("\\n");
        }

        System.out.print(sb);
    }

    static void bfs(int x, int y) {
        Queue<int[]> queue = new LinkedList<>();
        queue.add(new int[]{x, y});
        visited[x][y] = true;

        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            int cx = cur[0], cy = cur[1];

            for (int i = 0; i < 4; i++) {
                int nx = cx + dx[i];
                int ny = cy + dy[i];

                if (nx >= 0 && nx < m && ny >= 0 && ny < n) {
                    if (field[nx][ny] == 1 && !visited[nx][ny]) {
                        visited[nx][ny] = true;
                        queue.add(new int[]{nx, ny});
                    }
                }
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_2606": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 바이러스 - DFS/BFS
import sys
from collections import deque
input = sys.stdin.readline

n = int(input())
m = int(input())

graph = [[] for _ in range(n + 1)]
for _ in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)
    graph[b].append(a)

# BFS로 1번과 연결된 컴퓨터 수 세기
visited = [False] * (n + 1)
queue = deque([1])
visited[1] = True
count = 0

while queue:
    cur = queue.popleft()
    for next_node in graph[cur]:
        if not visited[next_node]:
            visited[next_node] = True
            count += 1
            queue.append(next_node)

print(count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <queue>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<int> graph[101];
    bool visited[101] = {false};

    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        graph[a].push_back(b);
        graph[b].push_back(a);
    }

    // BFS
    queue<int> q;
    q.push(1);
    visited[1] = true;
    int count = 0;

    while (!q.empty()) {
        int cur = q.front();
        q.pop();

        for (int next : graph[cur]) {
            if (!visited[next]) {
                visited[next] = true;
                count++;
                q.push(next);
            }
        }
    }

    cout << count << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine());
        int m = Integer.parseInt(br.readLine());

        ArrayList<Integer>[] graph = new ArrayList[n + 1];
        for (int i = 1; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < m; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            graph[a].add(b);
            graph[b].add(a);
        }

        // BFS
        boolean[] visited = new boolean[n + 1];
        Queue<Integer> queue = new LinkedList<>();
        queue.add(1);
        visited[1] = true;
        int count = 0;

        while (!queue.isEmpty()) {
            int cur = queue.poll();

            for (int next : graph[cur]) {
                if (!visited[next]) {
                    visited[next] = true;
                    count++;
                    queue.add(next);
                }
            }
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_2667": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 단지번호붙이기 - DFS/BFS
import sys
from collections import deque
input = sys.stdin.readline

n = int(input())
grid = [input().strip() for _ in range(n)]

visited = [[False] * n for _ in range(n)]
dx = [0, 0, 1, -1]
dy = [1, -1, 0, 0]

def bfs(x, y):
    queue = deque([(x, y)])
    visited[x][y] = True
    count = 1

    while queue:
        cx, cy = queue.popleft()
        for i in range(4):
            nx, ny = cx + dx[i], cy + dy[i]
            if 0 <= nx < n and 0 <= ny < n:
                if grid[nx][ny] == '1' and not visited[nx][ny]:
                    visited[nx][ny] = True
                    count += 1
                    queue.append((nx, ny))

    return count

complexes = []
for i in range(n):
    for j in range(n):
        if grid[i][j] == '1' and not visited[i][j]:
            complexes.append(bfs(i, j))

complexes.sort()
print(len(complexes))
for c in complexes:
    print(c)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <string>
using namespace std;

int n;
string grid[25];
bool visited[25][25];
int dx[] = {0, 0, 1, -1};
int dy[] = {1, -1, 0, 0};

int bfs(int x, int y) {
    queue<pair<int, int>> q;
    q.push({x, y});
    visited[x][y] = true;
    int count = 1;

    while (!q.empty()) {
        int cx = q.front().first;
        int cy = q.front().second;
        q.pop();

        for (int i = 0; i < 4; i++) {
            int nx = cx + dx[i];
            int ny = cy + dy[i];

            if (nx >= 0 && nx < n && ny >= 0 && ny < n) {
                if (grid[nx][ny] == '1' && !visited[nx][ny]) {
                    visited[nx][ny] = true;
                    count++;
                    q.push({nx, ny});
                }
            }
        }
    }

    return count;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;

    for (int i = 0; i < n; i++) {
        cin >> grid[i];
    }

    vector<int> complexes;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (grid[i][j] == '1' && !visited[i][j]) {
                complexes.push_back(bfs(i, j));
            }
        }
    }

    sort(complexes.begin(), complexes.end());

    cout << complexes.size() << "\\n";
    for (int c : complexes) {
        cout << c << "\\n";
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int n;
    static String[] grid;
    static boolean[][] visited;
    static int[] dx = {0, 0, 1, -1};
    static int[] dy = {1, -1, 0, 0};

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        n = Integer.parseInt(br.readLine());
        grid = new String[n];
        visited = new boolean[n][n];

        for (int i = 0; i < n; i++) {
            grid[i] = br.readLine();
        }

        ArrayList<Integer> complexes = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i].charAt(j) == '1' && !visited[i][j]) {
                    complexes.add(bfs(i, j));
                }
            }
        }

        Collections.sort(complexes);

        sb.append(complexes.size()).append("\\n");
        for (int c : complexes) {
            sb.append(c).append("\\n");
        }

        System.out.print(sb);
    }

    static int bfs(int x, int y) {
        Queue<int[]> queue = new LinkedList<>();
        queue.add(new int[]{x, y});
        visited[x][y] = true;
        int count = 1;

        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            int cx = cur[0], cy = cur[1];

            for (int i = 0; i < 4; i++) {
                int nx = cx + dx[i];
                int ny = cy + dy[i];

                if (nx >= 0 && nx < n && ny >= 0 && ny < n) {
                    if (grid[nx].charAt(ny) == '1' && !visited[nx][ny]) {
                        visited[nx][ny] = true;
                        count++;
                        queue.add(new int[]{nx, ny});
                    }
                }
            }
        }

        return count;
    }
}
'''
            }
        ]
    },
    "baekjoon_2941": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 크로아티아 알파벳
s = input()

# 크로아티아 알파벳 목록 (긴 것부터 체크)
croatian = ['dz=', 'c=', 'c-', 'd-', 'lj', 'nj', 's=', 'z=']

for c in croatian:
    s = s.replace(c, '#')

print(len(s))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    string s;
    cin >> s;

    string croatian[] = {"dz=", "c=", "c-", "d-", "lj", "nj", "s=", "z="};

    for (const string& c : croatian) {
        size_t pos;
        while ((pos = s.find(c)) != string::npos) {
            s.replace(pos, c.length(), "#");
        }
    }

    cout << s.length() << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.next();

        String[] croatian = {"dz=", "c=", "c-", "d-", "lj", "nj", "s=", "z="};

        for (String c : croatian) {
            s = s.replace(c, "#");
        }

        System.out.println(s.length());
    }
}
'''
            }
        ]
    },
    "baekjoon_11726": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 2xn 타일링 - DP (피보나치)
n = int(input())

# dp[i] = 2xi 직사각형을 채우는 방법의 수
# dp[i] = dp[i-1] + dp[i-2] (피보나치)
if n == 1:
    print(1)
else:
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2

    for i in range(3, n + 1):
        dp[i] = (dp[i-1] + dp[i-2]) % 10007

    print(dp[n])
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;

    int dp[1001];
    dp[1] = 1;
    dp[2] = 2;

    for (int i = 3; i <= n; i++) {
        dp[i] = (dp[i-1] + dp[i-2]) % 10007;
    }

    cout << dp[n] << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        int[] dp = new int[n + 1];
        dp[1] = 1;
        if (n >= 2) dp[2] = 2;

        for (int i = 3; i <= n; i++) {
            dp[i] = (dp[i-1] + dp[i-2]) % 10007;
        }

        System.out.println(dp[n]);
    }
}
'''
            }
        ]
    },
    "baekjoon_11053": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 가장 긴 증가하는 부분 수열 (LIS) - DP O(n^2)
import sys
input = sys.stdin.readline

n = int(input())
arr = list(map(int, input().split()))

# dp[i] = arr[i]를 마지막 원소로 하는 LIS의 길이
dp = [1] * n

for i in range(1, n):
    for j in range(i):
        if arr[j] < arr[i]:
            dp[i] = max(dp[i], dp[j] + 1)

print(max(dp))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int arr[1000], dp[1000];

    for (int i = 0; i < n; i++) {
        cin >> arr[i];
        dp[i] = 1;
    }

    for (int i = 1; i < n; i++) {
        for (int j = 0; j < i; j++) {
            if (arr[j] < arr[i]) {
                dp[i] = max(dp[i], dp[j] + 1);
            }
        }
    }

    cout << *max_element(dp, dp + n) << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] arr = new int[n];
        int[] dp = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
            dp[i] = 1;
        }

        for (int i = 1; i < n; i++) {
            for (int j = 0; j < i; j++) {
                if (arr[j] < arr[i]) {
                    dp[i] = Math.max(dp[i], dp[j] + 1);
                }
            }
        }

        int max = 0;
        for (int i = 0; i < n; i++) {
            max = Math.max(max, dp[i]);
        }

        System.out.println(max);
    }
}
'''
            }
        ]
    },
    "baekjoon_1316": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 그룹 단어 체커
n = int(input())
count = 0

for _ in range(n):
    word = input()
    is_group = True
    seen = set()
    prev = ''

    for c in word:
        if c != prev:
            if c in seen:
                is_group = False
                break
            seen.add(c)
        prev = c

    if is_group:
        count += 1

print(count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int count = 0;

    for (int i = 0; i < n; i++) {
        string word;
        cin >> word;

        bool isGroup = true;
        set<char> seen;
        char prev = '\\0';

        for (char c : word) {
            if (c != prev) {
                if (seen.find(c) != seen.end()) {
                    isGroup = false;
                    break;
                }
                seen.insert(c);
            }
            prev = c;
        }

        if (isGroup) count++;
    }

    cout << count << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine());
        int count = 0;

        for (int i = 0; i < n; i++) {
            String word = br.readLine();
            boolean isGroup = true;
            Set<Character> seen = new HashSet<>();
            char prev = '\\0';

            for (char c : word.toCharArray()) {
                if (c != prev) {
                    if (seen.contains(c)) {
                        isGroup = false;
                        break;
                    }
                    seen.add(c);
                }
                prev = c;
            }

            if (isGroup) count++;
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_1874": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 스택 수열
import sys
input = sys.stdin.readline

n = int(input())
sequence = [int(input()) for _ in range(n)]

stack = []
result = []
current = 1
possible = True

for num in sequence:
    while current <= num:
        stack.append(current)
        result.append('+')
        current += 1

    if stack[-1] == num:
        stack.pop()
        result.append('-')
    else:
        possible = False
        break

if possible:
    print('\\n'.join(result))
else:
    print('NO')
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <stack>
#include <vector>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    stack<int> st;
    vector<char> result;
    int current = 1;
    bool possible = true;

    for (int i = 0; i < n; i++) {
        int num;
        cin >> num;

        while (current <= num) {
            st.push(current);
            result.push_back('+');
            current++;
        }

        if (st.top() == num) {
            st.pop();
            result.push_back('-');
        } else {
            possible = false;
            break;
        }
    }

    if (possible) {
        for (char c : result) {
            cout << c << "\\n";
        }
    } else {
        cout << "NO" << endl;
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine());
        Stack<Integer> stack = new Stack<>();
        int current = 1;
        boolean possible = true;

        for (int i = 0; i < n; i++) {
            int num = Integer.parseInt(br.readLine());

            while (current <= num) {
                stack.push(current);
                sb.append("+\\n");
                current++;
            }

            if (stack.peek() == num) {
                stack.pop();
                sb.append("-\\n");
            } else {
                possible = false;
                break;
            }
        }

        if (possible) {
            System.out.print(sb);
        } else {
            System.out.println("NO");
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_2108": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 통계학
import sys
from collections import Counter
input = sys.stdin.readline

n = int(input())
nums = [int(input()) for _ in range(n)]

# 산술평균 (반올림)
mean = round(sum(nums) / n)

# 중앙값
nums.sort()
median = nums[n // 2]

# 최빈값 (여러 개면 두 번째로 작은 값)
counter = Counter(nums)
max_count = max(counter.values())
modes = sorted([k for k, v in counter.items() if v == max_count])
mode = modes[1] if len(modes) > 1 else modes[0]

# 범위
range_val = nums[-1] - nums[0]

print(mean)
print(median)
print(mode)
print(range_val)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> nums(n);
    long long sum = 0;
    map<int, int> counter;

    for (int i = 0; i < n; i++) {
        cin >> nums[i];
        sum += nums[i];
        counter[nums[i]]++;
    }

    sort(nums.begin(), nums.end());

    // 산술평균 (반올림)
    int mean = round((double)sum / n);

    // 중앙값
    int median = nums[n / 2];

    // 최빈값
    int maxCount = 0;
    for (auto& p : counter) {
        maxCount = max(maxCount, p.second);
    }

    vector<int> modes;
    for (auto& p : counter) {
        if (p.second == maxCount) {
            modes.push_back(p.first);
        }
    }

    int mode = modes.size() > 1 ? modes[1] : modes[0];

    // 범위
    int rangeVal = nums[n-1] - nums[0];

    cout << mean << "\\n";
    cout << median << "\\n";
    cout << mode << "\\n";
    cout << rangeVal << "\\n";

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine());
        int[] nums = new int[n];
        long sum = 0;
        Map<Integer, Integer> counter = new TreeMap<>();

        for (int i = 0; i < n; i++) {
            nums[i] = Integer.parseInt(br.readLine());
            sum += nums[i];
            counter.put(nums[i], counter.getOrDefault(nums[i], 0) + 1);
        }

        Arrays.sort(nums);

        // 산술평균
        int mean = (int) Math.round((double) sum / n);

        // 중앙값
        int median = nums[n / 2];

        // 최빈값
        int maxCount = Collections.max(counter.values());
        List<Integer> modes = new ArrayList<>();
        for (Map.Entry<Integer, Integer> e : counter.entrySet()) {
            if (e.getValue() == maxCount) {
                modes.add(e.getKey());
            }
        }
        int mode = modes.size() > 1 ? modes.get(1) : modes.get(0);

        // 범위
        int rangeVal = nums[n-1] - nums[0];

        sb.append(mean).append("\\n");
        sb.append(median).append("\\n");
        sb.append(mode).append("\\n");
        sb.append(rangeVal).append("\\n");

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_10816": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 숫자 카드 2 - Counter 사용
import sys
from collections import Counter
input = sys.stdin.readline

n = int(input())
cards = list(map(int, input().split()))
m = int(input())
queries = list(map(int, input().split()))

counter = Counter(cards)
result = [str(counter[q]) for q in queries]
print(' '.join(result))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    map<int, int> counter;
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        counter[x]++;
    }

    int m;
    cin >> m;

    for (int i = 0; i < m; i++) {
        int x;
        cin >> x;
        cout << counter[x];
        if (i < m - 1) cout << " ";
    }
    cout << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine());
        StringTokenizer st = new StringTokenizer(br.readLine());

        Map<Integer, Integer> counter = new HashMap<>();
        for (int i = 0; i < n; i++) {
            int x = Integer.parseInt(st.nextToken());
            counter.put(x, counter.getOrDefault(x, 0) + 1);
        }

        int m = Integer.parseInt(br.readLine());
        st = new StringTokenizer(br.readLine());

        for (int i = 0; i < m; i++) {
            int x = Integer.parseInt(st.nextToken());
            sb.append(counter.getOrDefault(x, 0));
            if (i < m - 1) sb.append(" ");
        }

        System.out.println(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_4673": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 셀프 넘버
def d(n):
    result = n
    while n > 0:
        result += n % 10
        n //= 10
    return result

# 생성자가 있는 수 체크
not_self = set()
for i in range(1, 10001):
    generated = d(i)
    if generated <= 10000:
        not_self.add(generated)

# 셀프 넘버 출력
for i in range(1, 10001):
    if i not in not_self:
        print(i)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int d(int n) {
    int result = n;
    while (n > 0) {
        result += n % 10;
        n /= 10;
    }
    return result;
}

int main() {
    bool notSelf[10001] = {false};

    for (int i = 1; i <= 10000; i++) {
        int generated = d(i);
        if (generated <= 10000) {
            notSelf[generated] = true;
        }
    }

    for (int i = 1; i <= 10000; i++) {
        if (!notSelf[i]) {
            cout << i << "\\n";
        }
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''public class Main {
    static int d(int n) {
        int result = n;
        while (n > 0) {
            result += n % 10;
            n /= 10;
        }
        return result;
    }

    public static void main(String[] args) {
        boolean[] notSelf = new boolean[10001];

        for (int i = 1; i <= 10000; i++) {
            int generated = d(i);
            if (generated <= 10000) {
                notSelf[generated] = true;
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= 10000; i++) {
            if (!notSelf[i]) {
                sb.append(i).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_10814": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 나이순 정렬 - 안정 정렬
import sys
input = sys.stdin.readline

n = int(input())
members = []

for i in range(n):
    line = input().split()
    age = int(line[0])
    name = line[1]
    members.append((age, i, name))

# 나이순, 같으면 가입순 (인덱스)
members.sort(key=lambda x: (x[0], x[1]))

for age, _, name in members:
    print(age, name)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

struct Member {
    int age;
    int index;
    string name;
};

bool compare(const Member& a, const Member& b) {
    if (a.age != b.age) return a.age < b.age;
    return a.index < b.index;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<Member> members(n);

    for (int i = 0; i < n; i++) {
        cin >> members[i].age >> members[i].name;
        members[i].index = i;
    }

    sort(members.begin(), members.end(), compare);

    for (const Member& m : members) {
        cout << m.age << " " << m.name << "\\n";
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine());

        int[][] members = new int[n][2];
        String[] names = new String[n];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            members[i][0] = Integer.parseInt(st.nextToken());
            members[i][1] = i;
            names[i] = st.nextToken();
        }

        // 나이순, 같으면 가입순 정렬
        Integer[] indices = new Integer[n];
        for (int i = 0; i < n; i++) indices[i] = i;

        Arrays.sort(indices, (a, b) -> {
            if (members[a][0] != members[b][0]) {
                return members[a][0] - members[b][0];
            }
            return members[a][1] - members[b][1];
        });

        for (int i : indices) {
            sb.append(members[i][0]).append(" ").append(names[i]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_4949": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 균형잡힌 세상 - 스택
import sys
input = sys.stdin.readline

while True:
    s = input().rstrip()
    if s == '.':
        break

    stack = []
    balanced = True

    for c in s:
        if c == '(' or c == '[':
            stack.append(c)
        elif c == ')':
            if not stack or stack[-1] != '(':
                balanced = False
                break
            stack.pop()
        elif c == ']':
            if not stack or stack[-1] != '[':
                balanced = False
                break
            stack.pop()

    if balanced and len(stack) == 0:
        print('yes')
    else:
        print('no')
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <stack>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    while (getline(cin, s)) {
        if (s == ".") break;

        stack<char> st;
        bool balanced = true;

        for (char c : s) {
            if (c == '(' || c == '[') {
                st.push(c);
            } else if (c == ')') {
                if (st.empty() || st.top() != '(') {
                    balanced = false;
                    break;
                }
                st.pop();
            } else if (c == ']') {
                if (st.empty() || st.top() != '[') {
                    balanced = false;
                    break;
                }
                st.pop();
            }
        }

        if (balanced && st.empty()) {
            cout << "yes\\n";
        } else {
            cout << "no\\n";
        }
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        String s;
        while (!(s = br.readLine()).equals(".")) {
            Stack<Character> stack = new Stack<>();
            boolean balanced = true;

            for (char c : s.toCharArray()) {
                if (c == '(' || c == '[') {
                    stack.push(c);
                } else if (c == ')') {
                    if (stack.isEmpty() || stack.peek() != '(') {
                        balanced = false;
                        break;
                    }
                    stack.pop();
                } else if (c == ']') {
                    if (stack.isEmpty() || stack.peek() != '[') {
                        balanced = false;
                        break;
                    }
                    stack.pop();
                }
            }

            if (balanced && stack.isEmpty()) {
                sb.append("yes\\n");
            } else {
                sb.append("no\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_11047": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 동전 0 - 그리디
import sys
input = sys.stdin.readline

n, k = map(int, input().split())
coins = [int(input()) for _ in range(n)]

# 큰 동전부터 사용
count = 0
for i in range(n - 1, -1, -1):
    if coins[i] <= k:
        count += k // coins[i]
        k %= coins[i]
    if k == 0:
        break

print(count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    int coins[10];
    for (int i = 0; i < n; i++) {
        cin >> coins[i];
    }

    int count = 0;
    for (int i = n - 1; i >= 0; i--) {
        if (coins[i] <= k) {
            count += k / coins[i];
            k %= coins[i];
        }
        if (k == 0) break;
    }

    cout << count << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        int[] coins = new int[n];
        for (int i = 0; i < n; i++) {
            coins[i] = Integer.parseInt(br.readLine());
        }

        int count = 0;
        for (int i = n - 1; i >= 0; i--) {
            if (coins[i] <= k) {
                count += k / coins[i];
                k %= coins[i];
            }
            if (k == 0) break;
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    }
}

# 기존 파일 로드 및 업데이트
with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)

existing.update(new_solutions)

with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"총 {len(new_solutions)}개 문제 추가됨")
print(f"현재 총 솔루션 수: {len(existing)}")
