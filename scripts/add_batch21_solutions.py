#!/usr/bin/env python3
"""배치 21: 기본 알고리즘 medium 문제 솔루션 추가"""

import json

new_solutions = {
    "baekjoon_11650": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 좌표 정렬하기
import sys
input = sys.stdin.readline

n = int(input())
points = [tuple(map(int, input().split())) for _ in range(n)]

# x좌표 순, 같으면 y좌표 순
points.sort()

for x, y in points:
    print(x, y)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<pair<int, int>> points(n);

    for (int i = 0; i < n; i++) {
        cin >> points[i].first >> points[i].second;
    }

    sort(points.begin(), points.end());

    for (auto& p : points) {
        cout << p.first << " " << p.second << "\\n";
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
        int[][] points = new int[n][2];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            points[i][0] = Integer.parseInt(st.nextToken());
            points[i][1] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(points, (a, b) -> {
            if (a[0] != b[0]) return a[0] - b[0];
            return a[1] - b[1];
        });

        for (int[] p : points) {
            sb.append(p[0]).append(" ").append(p[1]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_11724": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 연결 요소의 개수 - DFS/BFS
import sys
from collections import deque
sys.setrecursionlimit(10000)
input = sys.stdin.readline

n, m = map(int, input().split())

graph = [[] for _ in range(n + 1)]
for _ in range(m):
    u, v = map(int, input().split())
    graph[u].append(v)
    graph[v].append(u)

visited = [False] * (n + 1)

def bfs(start):
    queue = deque([start])
    visited[start] = True
    while queue:
        cur = queue.popleft()
        for next_node in graph[cur]:
            if not visited[next_node]:
                visited[next_node] = True
                queue.append(next_node)

count = 0
for i in range(1, n + 1):
    if not visited[i]:
        bfs(i)
        count += 1

print(count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <queue>
using namespace std;

int n, m;
vector<int> graph[1001];
bool visited[1001];

void bfs(int start) {
    queue<int> q;
    q.push(start);
    visited[start] = true;

    while (!q.empty()) {
        int cur = q.front();
        q.pop();

        for (int next : graph[cur]) {
            if (!visited[next]) {
                visited[next] = true;
                q.push(next);
            }
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> m;

    for (int i = 0; i < m; i++) {
        int u, v;
        cin >> u >> v;
        graph[u].push_back(v);
        graph[v].push_back(u);
    }

    int count = 0;
    for (int i = 1; i <= n; i++) {
        if (!visited[i]) {
            bfs(i);
            count++;
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
    static ArrayList<Integer>[] graph;
    static boolean[] visited;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        graph = new ArrayList[n + 1];
        visited = new boolean[n + 1];

        for (int i = 1; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            int u = Integer.parseInt(st.nextToken());
            int v = Integer.parseInt(st.nextToken());
            graph[u].add(v);
            graph[v].add(u);
        }

        int count = 0;
        for (int i = 1; i <= n; i++) {
            if (!visited[i]) {
                bfs(i);
                count++;
            }
        }

        System.out.println(count);
    }

    static void bfs(int start) {
        Queue<Integer> queue = new LinkedList<>();
        queue.add(start);
        visited[start] = true;

        while (!queue.isEmpty()) {
            int cur = queue.poll();

            for (int next : graph[cur]) {
                if (!visited[next]) {
                    visited[next] = true;
                    queue.add(next);
                }
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_10844": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 쉬운 계단 수 - DP
n = int(input())
MOD = 1000000000

# dp[i][j] = 길이가 i이고 마지막 숫자가 j인 계단 수의 개수
dp = [[0] * 10 for _ in range(n + 1)]

# 길이가 1인 경우 (0으로 시작 불가)
for j in range(1, 10):
    dp[1][j] = 1

for i in range(2, n + 1):
    for j in range(10):
        if j > 0:
            dp[i][j] += dp[i-1][j-1]
        if j < 9:
            dp[i][j] += dp[i-1][j+1]
        dp[i][j] %= MOD

print(sum(dp[n]) % MOD)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

const long long MOD = 1000000000;
long long dp[101][10];

int main() {
    int n;
    cin >> n;

    // 길이가 1인 경우 (0으로 시작 불가)
    for (int j = 1; j <= 9; j++) {
        dp[1][j] = 1;
    }

    for (int i = 2; i <= n; i++) {
        for (int j = 0; j <= 9; j++) {
            if (j > 0) dp[i][j] += dp[i-1][j-1];
            if (j < 9) dp[i][j] += dp[i-1][j+1];
            dp[i][j] %= MOD;
        }
    }

    long long result = 0;
    for (int j = 0; j <= 9; j++) {
        result += dp[n][j];
    }

    cout << result % MOD << endl;

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
        long MOD = 1000000000;

        long[][] dp = new long[n + 1][10];

        // 길이가 1인 경우 (0으로 시작 불가)
        for (int j = 1; j <= 9; j++) {
            dp[1][j] = 1;
        }

        for (int i = 2; i <= n; i++) {
            for (int j = 0; j <= 9; j++) {
                if (j > 0) dp[i][j] += dp[i-1][j-1];
                if (j < 9) dp[i][j] += dp[i-1][j+1];
                dp[i][j] %= MOD;
            }
        }

        long result = 0;
        for (int j = 0; j <= 9; j++) {
            result += dp[n][j];
        }

        System.out.println(result % MOD);
    }
}
'''
            }
        ]
    },
    "baekjoon_11659": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 구간 합 구하기 4 - 누적 합
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
nums = list(map(int, input().split()))

# 누적 합 배열
prefix = [0] * (n + 1)
for i in range(n):
    prefix[i + 1] = prefix[i] + nums[i]

result = []
for _ in range(m):
    i, j = map(int, input().split())
    result.append(prefix[j] - prefix[i - 1])

print('\\n'.join(map(str, result)))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    long long prefix[100001] = {0};

    for (int i = 1; i <= n; i++) {
        int x;
        cin >> x;
        prefix[i] = prefix[i-1] + x;
    }

    for (int q = 0; q < m; q++) {
        int i, j;
        cin >> i >> j;
        cout << prefix[j] - prefix[i-1] << "\\n";
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

        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        long[] prefix = new long[n + 1];
        st = new StringTokenizer(br.readLine());
        for (int i = 1; i <= n; i++) {
            prefix[i] = prefix[i-1] + Integer.parseInt(st.nextToken());
        }

        for (int q = 0; q < m; q++) {
            st = new StringTokenizer(br.readLine());
            int i = Integer.parseInt(st.nextToken());
            int j = Integer.parseInt(st.nextToken());
            sb.append(prefix[j] - prefix[i-1]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_2164": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 카드2 - 큐
from collections import deque

n = int(input())
queue = deque(range(1, n + 1))

while len(queue) > 1:
    queue.popleft()  # 맨 위 카드 버림
    queue.append(queue.popleft())  # 맨 위 카드를 맨 아래로

print(queue[0])
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <queue>
using namespace std;

int main() {
    int n;
    cin >> n;

    queue<int> q;
    for (int i = 1; i <= n; i++) {
        q.push(i);
    }

    while (q.size() > 1) {
        q.pop();  // 맨 위 카드 버림
        q.push(q.front());  // 맨 위 카드를 맨 아래로
        q.pop();
    }

    cout << q.front() << endl;

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

        Queue<Integer> queue = new LinkedList<>();
        for (int i = 1; i <= n; i++) {
            queue.add(i);
        }

        while (queue.size() > 1) {
            queue.poll();  // 맨 위 카드 버림
            queue.add(queue.poll());  // 맨 위 카드를 맨 아래로
        }

        System.out.println(queue.poll());
    }
}
'''
            }
        ]
    },
    "baekjoon_2156": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 포도주 시식 - DP
import sys
input = sys.stdin.readline

n = int(input())
wine = [0] + [int(input()) for _ in range(n)]

if n == 1:
    print(wine[1])
elif n == 2:
    print(wine[1] + wine[2])
else:
    # dp[i] = i번째 포도주까지 고려했을 때 최대 양
    dp = [0] * (n + 1)
    dp[1] = wine[1]
    dp[2] = wine[1] + wine[2]

    for i in range(3, n + 1):
        # 현재 안 마심, 현재만 마심 (전전꺼 마시고), OXO 패턴
        dp[i] = max(dp[i-1], dp[i-2] + wine[i], dp[i-3] + wine[i-1] + wine[i])

    print(dp[n])
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    int n;
    cin >> n;

    int wine[10001] = {0};
    int dp[10001] = {0};

    for (int i = 1; i <= n; i++) {
        cin >> wine[i];
    }

    if (n == 1) {
        cout << wine[1] << endl;
    } else if (n == 2) {
        cout << wine[1] + wine[2] << endl;
    } else {
        dp[1] = wine[1];
        dp[2] = wine[1] + wine[2];

        for (int i = 3; i <= n; i++) {
            dp[i] = max({dp[i-1], dp[i-2] + wine[i], dp[i-3] + wine[i-1] + wine[i]});
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
        int[] wine = new int[n + 1];
        int[] dp = new int[n + 1];

        for (int i = 1; i <= n; i++) {
            wine[i] = Integer.parseInt(br.readLine());
        }

        if (n == 1) {
            System.out.println(wine[1]);
        } else if (n == 2) {
            System.out.println(wine[1] + wine[2]);
        } else {
            dp[1] = wine[1];
            dp[2] = wine[1] + wine[2];

            for (int i = 3; i <= n; i++) {
                dp[i] = Math.max(dp[i-1], Math.max(dp[i-2] + wine[i], dp[i-3] + wine[i-1] + wine[i]));
            }

            System.out.println(dp[n]);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_1912": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 연속합 - DP (카데인 알고리즘)
import sys
input = sys.stdin.readline

n = int(input())
nums = list(map(int, input().split()))

# dp[i] = i번째 원소를 마지막으로 하는 연속합의 최대값
dp = [0] * n
dp[0] = nums[0]
max_sum = dp[0]

for i in range(1, n):
    dp[i] = max(nums[i], dp[i-1] + nums[i])
    max_sum = max(max_sum, dp[i])

print(max_sum)
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

    int nums[100000];
    for (int i = 0; i < n; i++) {
        cin >> nums[i];
    }

    int dp = nums[0];
    int maxSum = dp;

    for (int i = 1; i < n; i++) {
        dp = max(nums[i], dp + nums[i]);
        maxSum = max(maxSum, dp);
    }

    cout << maxSum << endl;

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

        int[] nums = new int[n];
        for (int i = 0; i < n; i++) {
            nums[i] = Integer.parseInt(st.nextToken());
        }

        int dp = nums[0];
        int maxSum = dp;

        for (int i = 1; i < n; i++) {
            dp = Math.max(nums[i], dp + nums[i]);
            maxSum = Math.max(maxSum, dp);
        }

        System.out.println(maxSum);
    }
}
'''
            }
        ]
    },
    "baekjoon_1629": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 곱셈 - 분할 정복을 이용한 거듭제곱
import sys
input = sys.stdin.readline

a, b, c = map(int, input().split())

# Python은 내장 pow가 모듈러 거듭제곱 지원
print(pow(a, b, c))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

// 분할 정복 거듭제곱
long long power(long long a, long long b, long long c) {
    if (b == 0) return 1;

    long long half = power(a, b / 2, c);
    half = (half * half) % c;

    if (b % 2 == 1) {
        half = (half * (a % c)) % c;
    }

    return half;
}

int main() {
    long long a, b, c;
    cin >> a >> b >> c;

    cout << power(a, b, c) << endl;

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
        long a = sc.nextLong();
        long b = sc.nextLong();
        long c = sc.nextLong();

        System.out.println(power(a, b, c));
    }

    // 분할 정복 거듭제곱
    static long power(long a, long b, long c) {
        if (b == 0) return 1;

        long half = power(a, b / 2, c);
        half = (half * half) % c;

        if (b % 2 == 1) {
            half = (half * (a % c)) % c;
        }

        return half;
    }
}
'''
            }
        ]
    },
    "baekjoon_10845": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 큐 구현
import sys
from collections import deque
input = sys.stdin.readline

n = int(input())
queue = deque()
result = []

for _ in range(n):
    cmd = input().split()

    if cmd[0] == 'push':
        queue.append(int(cmd[1]))
    elif cmd[0] == 'pop':
        result.append(queue.popleft() if queue else -1)
    elif cmd[0] == 'size':
        result.append(len(queue))
    elif cmd[0] == 'empty':
        result.append(0 if queue else 1)
    elif cmd[0] == 'front':
        result.append(queue[0] if queue else -1)
    elif cmd[0] == 'back':
        result.append(queue[-1] if queue else -1)

print('\\n'.join(map(str, result)))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <queue>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    deque<int> dq;

    for (int i = 0; i < n; i++) {
        string cmd;
        cin >> cmd;

        if (cmd == "push") {
            int x;
            cin >> x;
            dq.push_back(x);
        } else if (cmd == "pop") {
            if (dq.empty()) {
                cout << -1 << "\\n";
            } else {
                cout << dq.front() << "\\n";
                dq.pop_front();
            }
        } else if (cmd == "size") {
            cout << dq.size() << "\\n";
        } else if (cmd == "empty") {
            cout << (dq.empty() ? 1 : 0) << "\\n";
        } else if (cmd == "front") {
            cout << (dq.empty() ? -1 : dq.front()) << "\\n";
        } else if (cmd == "back") {
            cout << (dq.empty() ? -1 : dq.back()) << "\\n";
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

        int n = Integer.parseInt(br.readLine());
        Deque<Integer> queue = new ArrayDeque<>();

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String cmd = st.nextToken();

            if (cmd.equals("push")) {
                int x = Integer.parseInt(st.nextToken());
                queue.addLast(x);
            } else if (cmd.equals("pop")) {
                sb.append(queue.isEmpty() ? -1 : queue.pollFirst()).append("\\n");
            } else if (cmd.equals("size")) {
                sb.append(queue.size()).append("\\n");
            } else if (cmd.equals("empty")) {
                sb.append(queue.isEmpty() ? 1 : 0).append("\\n");
            } else if (cmd.equals("front")) {
                sb.append(queue.isEmpty() ? -1 : queue.peekFirst()).append("\\n");
            } else if (cmd.equals("back")) {
                sb.append(queue.isEmpty() ? -1 : queue.peekLast()).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_1018": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 체스판 다시 칠하기
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
board = [input().strip() for _ in range(n)]

# 두 가지 패턴
pattern1 = "WBWBWBWB"
pattern2 = "BWBWBWBW"

min_count = float('inf')

# 모든 8x8 영역 확인
for i in range(n - 7):
    for j in range(m - 7):
        count1 = 0  # W로 시작하는 패턴
        count2 = 0  # B로 시작하는 패턴

        for x in range(8):
            for y in range(8):
                if x % 2 == 0:
                    if board[i + x][j + y] != pattern1[y]:
                        count1 += 1
                    if board[i + x][j + y] != pattern2[y]:
                        count2 += 1
                else:
                    if board[i + x][j + y] != pattern2[y]:
                        count1 += 1
                    if board[i + x][j + y] != pattern1[y]:
                        count2 += 1

        min_count = min(min_count, count1, count2)

print(min_count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
#include <string>
using namespace std;

int main() {
    int n, m;
    cin >> n >> m;

    string board[50];
    for (int i = 0; i < n; i++) {
        cin >> board[i];
    }

    string pattern1 = "WBWBWBWB";
    string pattern2 = "BWBWBWBW";

    int minCount = 64;

    for (int i = 0; i <= n - 8; i++) {
        for (int j = 0; j <= m - 8; j++) {
            int count1 = 0, count2 = 0;

            for (int x = 0; x < 8; x++) {
                for (int y = 0; y < 8; y++) {
                    if (x % 2 == 0) {
                        if (board[i + x][j + y] != pattern1[y]) count1++;
                        if (board[i + x][j + y] != pattern2[y]) count2++;
                    } else {
                        if (board[i + x][j + y] != pattern2[y]) count1++;
                        if (board[i + x][j + y] != pattern1[y]) count2++;
                    }
                }
            }

            minCount = min({minCount, count1, count2});
        }
    }

    cout << minCount << endl;

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
        int m = Integer.parseInt(st.nextToken());

        String[] board = new String[n];
        for (int i = 0; i < n; i++) {
            board[i] = br.readLine();
        }

        String pattern1 = "WBWBWBWB";
        String pattern2 = "BWBWBWBW";

        int minCount = 64;

        for (int i = 0; i <= n - 8; i++) {
            for (int j = 0; j <= m - 8; j++) {
                int count1 = 0, count2 = 0;

                for (int x = 0; x < 8; x++) {
                    for (int y = 0; y < 8; y++) {
                        if (x % 2 == 0) {
                            if (board[i + x].charAt(j + y) != pattern1.charAt(y)) count1++;
                            if (board[i + x].charAt(j + y) != pattern2.charAt(y)) count2++;
                        } else {
                            if (board[i + x].charAt(j + y) != pattern2.charAt(y)) count1++;
                            if (board[i + x].charAt(j + y) != pattern1.charAt(y)) count2++;
                        }
                    }
                }

                minCount = Math.min(minCount, Math.min(count1, count2));
            }
        }

        System.out.println(minCount);
    }
}
'''
            }
        ]
    },
    "baekjoon_1065": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 한수
def is_hansu(n):
    if n < 100:
        return True
    digits = [int(d) for d in str(n)]
    diff = digits[1] - digits[0]
    for i in range(2, len(digits)):
        if digits[i] - digits[i-1] != diff:
            return False
    return True

n = int(input())
count = sum(1 for i in range(1, n + 1) if is_hansu(i))
print(count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

bool isHansu(int n) {
    if (n < 100) return true;

    int d1 = n / 100;
    int d2 = (n / 10) % 10;
    int d3 = n % 10;

    return (d2 - d1) == (d3 - d2);
}

int main() {
    int n;
    cin >> n;

    int count = 0;
    for (int i = 1; i <= n; i++) {
        if (isHansu(i)) count++;
    }

    cout << count << endl;

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

        int count = 0;
        for (int i = 1; i <= n; i++) {
            if (isHansu(i)) count++;
        }

        System.out.println(count);
    }

    static boolean isHansu(int n) {
        if (n < 100) return true;

        int d1 = n / 100;
        int d2 = (n / 10) % 10;
        int d3 = n % 10;

        return (d2 - d1) == (d3 - d2);
    }
}
'''
            }
        ]
    },
    "baekjoon_11723": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 집합 - 비트마스킹
import sys
input = sys.stdin.readline

m = int(input())
s = 0  # 비트마스크
result = []

for _ in range(m):
    cmd = input().split()

    if cmd[0] == 'add':
        x = int(cmd[1])
        s |= (1 << x)
    elif cmd[0] == 'remove':
        x = int(cmd[1])
        s &= ~(1 << x)
    elif cmd[0] == 'check':
        x = int(cmd[1])
        result.append(1 if s & (1 << x) else 0)
    elif cmd[0] == 'toggle':
        x = int(cmd[1])
        s ^= (1 << x)
    elif cmd[0] == 'all':
        s = (1 << 21) - 1
    elif cmd[0] == 'empty':
        s = 0

print('\\n'.join(map(str, result)))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int m;
    cin >> m;

    int s = 0;  // 비트마스크

    while (m--) {
        string cmd;
        cin >> cmd;

        if (cmd == "add") {
            int x;
            cin >> x;
            s |= (1 << x);
        } else if (cmd == "remove") {
            int x;
            cin >> x;
            s &= ~(1 << x);
        } else if (cmd == "check") {
            int x;
            cin >> x;
            cout << ((s & (1 << x)) ? 1 : 0) << "\\n";
        } else if (cmd == "toggle") {
            int x;
            cin >> x;
            s ^= (1 << x);
        } else if (cmd == "all") {
            s = (1 << 21) - 1;
        } else if (cmd == "empty") {
            s = 0;
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

        int m = Integer.parseInt(br.readLine());
        int s = 0;  // 비트마스크

        while (m-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String cmd = st.nextToken();

            if (cmd.equals("add")) {
                int x = Integer.parseInt(st.nextToken());
                s |= (1 << x);
            } else if (cmd.equals("remove")) {
                int x = Integer.parseInt(st.nextToken());
                s &= ~(1 << x);
            } else if (cmd.equals("check")) {
                int x = Integer.parseInt(st.nextToken());
                sb.append((s & (1 << x)) != 0 ? 1 : 0).append("\\n");
            } else if (cmd.equals("toggle")) {
                int x = Integer.parseInt(st.nextToken());
                s ^= (1 << x);
            } else if (cmd.equals("all")) {
                s = (1 << 21) - 1;
            } else if (cmd.equals("empty")) {
                s = 0;
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_1620": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 나는야 포켓몬 마스터 이다솜 - 해시맵
import sys
input = sys.stdin.readline

n, m = map(int, input().split())

name_to_num = {}
num_to_name = {}

for i in range(1, n + 1):
    name = input().strip()
    name_to_num[name] = i
    num_to_name[i] = name

result = []
for _ in range(m):
    query = input().strip()
    if query.isdigit():
        result.append(num_to_name[int(query)])
    else:
        result.append(str(name_to_num[query]))

print('\\n'.join(result))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <map>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    map<string, int> nameToNum;
    string numToName[100001];

    for (int i = 1; i <= n; i++) {
        string name;
        cin >> name;
        nameToNum[name] = i;
        numToName[i] = name;
    }

    for (int i = 0; i < m; i++) {
        string query;
        cin >> query;

        if (isdigit(query[0])) {
            cout << numToName[stoi(query)] << "\\n";
        } else {
            cout << nameToNum[query] << "\\n";
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

        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        Map<String, Integer> nameToNum = new HashMap<>();
        String[] numToName = new String[n + 1];

        for (int i = 1; i <= n; i++) {
            String name = br.readLine();
            nameToNum.put(name, i);
            numToName[i] = name;
        }

        for (int i = 0; i < m; i++) {
            String query = br.readLine();

            if (Character.isDigit(query.charAt(0))) {
                sb.append(numToName[Integer.parseInt(query)]).append("\\n");
            } else {
                sb.append(nameToNum.get(query)).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_1406": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 에디터 - 스택 두 개 사용
import sys
input = sys.stdin.readline

s = list(input().strip())
m = int(input())

# 커서 왼쪽 스택, 커서 오른쪽 스택
left = s
right = []

for _ in range(m):
    cmd = input().split()

    if cmd[0] == 'L':
        if left:
            right.append(left.pop())
    elif cmd[0] == 'D':
        if right:
            left.append(right.pop())
    elif cmd[0] == 'B':
        if left:
            left.pop()
    elif cmd[0] == 'P':
        left.append(cmd[1])

# 결과 출력
left.extend(reversed(right))
print(''.join(left))
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
    cin >> s;

    int m;
    cin >> m;

    // 커서 왼쪽, 오른쪽 스택
    stack<char> left, right;

    for (char c : s) {
        left.push(c);
    }

    while (m--) {
        char cmd;
        cin >> cmd;

        if (cmd == 'L') {
            if (!left.empty()) {
                right.push(left.top());
                left.pop();
            }
        } else if (cmd == 'D') {
            if (!right.empty()) {
                left.push(right.top());
                right.pop();
            }
        } else if (cmd == 'B') {
            if (!left.empty()) {
                left.pop();
            }
        } else if (cmd == 'P') {
            char c;
            cin >> c;
            left.push(c);
        }
    }

    // 결과 출력
    string result = "";
    while (!left.empty()) {
        result = left.top() + result;
        left.pop();
    }
    while (!right.empty()) {
        result += right.top();
        right.pop();
    }

    cout << result << endl;

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

        String s = br.readLine();
        int m = Integer.parseInt(br.readLine());

        // 커서 왼쪽, 오른쪽 스택
        Stack<Character> left = new Stack<>();
        Stack<Character> right = new Stack<>();

        for (char c : s.toCharArray()) {
            left.push(c);
        }

        while (m-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String cmd = st.nextToken();

            if (cmd.equals("L")) {
                if (!left.isEmpty()) {
                    right.push(left.pop());
                }
            } else if (cmd.equals("D")) {
                if (!right.isEmpty()) {
                    left.push(right.pop());
                }
            } else if (cmd.equals("B")) {
                if (!left.isEmpty()) {
                    left.pop();
                }
            } else if (cmd.equals("P")) {
                char c = st.nextToken().charAt(0);
                left.push(c);
            }
        }

        // 결과 출력
        while (!left.isEmpty()) {
            right.push(left.pop());
        }
        while (!right.isEmpty()) {
            sb.append(right.pop());
        }

        System.out.println(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_9095": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 1, 2, 3 더하기 - DP
import sys
input = sys.stdin.readline

# dp[i] = i를 1, 2, 3의 합으로 나타내는 방법의 수
dp = [0] * 12
dp[1] = 1
dp[2] = 2
dp[3] = 4

for i in range(4, 12):
    dp[i] = dp[i-1] + dp[i-2] + dp[i-3]

t = int(input())
for _ in range(t):
    n = int(input())
    print(dp[n])
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    // dp[i] = i를 1, 2, 3의 합으로 나타내는 방법의 수
    int dp[12];
    dp[1] = 1;
    dp[2] = 2;
    dp[3] = 4;

    for (int i = 4; i <= 11; i++) {
        dp[i] = dp[i-1] + dp[i-2] + dp[i-3];
    }

    int t;
    cin >> t;

    while (t--) {
        int n;
        cin >> n;
        cout << dp[n] << "\\n";
    }

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

        // dp[i] = i를 1, 2, 3의 합으로 나타내는 방법의 수
        int[] dp = new int[12];
        dp[1] = 1;
        dp[2] = 2;
        dp[3] = 4;

        for (int i = 4; i <= 11; i++) {
            dp[i] = dp[i-1] + dp[i-2] + dp[i-3];
        }

        int t = sc.nextInt();

        while (t-- > 0) {
            int n = sc.nextInt();
            System.out.println(dp[n]);
        }
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
