#!/usr/bin/env python3
"""배치 19: 기본 알고리즘 medium 문제 솔루션 추가"""

import json

new_solutions = {
    "baekjoon_2751": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 수 정렬하기 2 - 빠른 정렬
import sys
input = sys.stdin.readline

n = int(input())
arr = [int(input()) for _ in range(n)]
arr.sort()

# 출력 최적화
print('\\n'.join(map(str, arr)))
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

    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    sort(arr.begin(), arr.end());

    for (int i = 0; i < n; i++) {
        cout << arr[i] << '\\n';
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
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(br.readLine());
        }

        Arrays.sort(arr);

        for (int i = 0; i < n; i++) {
            sb.append(arr[i]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_2839": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 설탕 배달 - 그리디/DP
n = int(input())

result = -1

# 5kg 봉지를 최대한 많이 사용
for five in range(n // 5, -1, -1):
    remainder = n - 5 * five
    if remainder % 3 == 0:
        result = five + remainder // 3
        break

print(result)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;

    int result = -1;

    // 5kg 봉지를 최대한 많이 사용
    for (int five = n / 5; five >= 0; five--) {
        int remainder = n - 5 * five;
        if (remainder % 3 == 0) {
            result = five + remainder / 3;
            break;
        }
    }

    cout << result << endl;

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

        int result = -1;

        // 5kg 봉지를 최대한 많이 사용
        for (int five = n / 5; five >= 0; five--) {
            int remainder = n - 5 * five;
            if (remainder % 3 == 0) {
                result = five + remainder / 3;
                break;
            }
        }

        System.out.println(result);
    }
}
'''
            }
        ]
    },
    "baekjoon_1463": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 1로 만들기 - DP
n = int(input())

# dp[i] = i를 1로 만드는 최소 연산 횟수
dp = [0] * (n + 1)

for i in range(2, n + 1):
    dp[i] = dp[i - 1] + 1  # 1을 빼는 경우
    if i % 2 == 0:
        dp[i] = min(dp[i], dp[i // 2] + 1)
    if i % 3 == 0:
        dp[i] = min(dp[i], dp[i // 3] + 1)

print(dp[n])
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int dp[1000001];

int main() {
    int n;
    cin >> n;

    dp[1] = 0;

    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i - 1] + 1;  // 1을 빼는 경우
        if (i % 2 == 0) {
            dp[i] = min(dp[i], dp[i / 2] + 1);
        }
        if (i % 3 == 0) {
            dp[i] = min(dp[i], dp[i / 3] + 1);
        }
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

        for (int i = 2; i <= n; i++) {
            dp[i] = dp[i - 1] + 1;  // 1을 빼는 경우
            if (i % 2 == 0) {
                dp[i] = Math.min(dp[i], dp[i / 2] + 1);
            }
            if (i % 3 == 0) {
                dp[i] = Math.min(dp[i], dp[i / 3] + 1);
            }
        }

        System.out.println(dp[n]);
    }
}
'''
            }
        ]
    },
    "baekjoon_1260": {
        "solutions": [
            {
                "language": "python",
                "code": '''# DFS와 BFS
import sys
from collections import deque
input = sys.stdin.readline

def dfs(v, visited, graph, result):
    visited[v] = True
    result.append(v)
    for next_v in sorted(graph[v]):
        if not visited[next_v]:
            dfs(next_v, visited, graph, result)

def bfs(v, graph, n):
    visited = [False] * (n + 1)
    result = []
    queue = deque([v])
    visited[v] = True

    while queue:
        cur = queue.popleft()
        result.append(cur)
        for next_v in sorted(graph[cur]):
            if not visited[next_v]:
                visited[next_v] = True
                queue.append(next_v)

    return result

n, m, v = map(int, input().split())

graph = [[] for _ in range(n + 1)]
for _ in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)
    graph[b].append(a)

# DFS
visited = [False] * (n + 1)
dfs_result = []
dfs(v, visited, graph, dfs_result)
print(' '.join(map(str, dfs_result)))

# BFS
bfs_result = bfs(v, graph, n)
print(' '.join(map(str, bfs_result)))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <queue>
#include <cstring>
using namespace std;

int n, m, v;
vector<int> graph[1001];
bool visited[1001];

void dfs(int cur) {
    visited[cur] = true;
    cout << cur << " ";

    for (int next : graph[cur]) {
        if (!visited[next]) {
            dfs(next);
        }
    }
}

void bfs(int start) {
    queue<int> q;
    q.push(start);
    visited[start] = true;

    while (!q.empty()) {
        int cur = q.front();
        q.pop();
        cout << cur << " ";

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

    cin >> n >> m >> v;

    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        graph[a].push_back(b);
        graph[b].push_back(a);
    }

    // 정렬 (작은 번호 먼저 방문)
    for (int i = 1; i <= n; i++) {
        sort(graph[i].begin(), graph[i].end());
    }

    // DFS
    memset(visited, false, sizeof(visited));
    dfs(v);
    cout << "\\n";

    // BFS
    memset(visited, false, sizeof(visited));
    bfs(v);
    cout << "\\n";

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
    static StringBuilder sb = new StringBuilder();

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());
        int v = Integer.parseInt(st.nextToken());

        graph = new ArrayList[n + 1];
        for (int i = 1; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            graph[a].add(b);
            graph[b].add(a);
        }

        // 정렬
        for (int i = 1; i <= n; i++) {
            Collections.sort(graph[i]);
        }

        // DFS
        visited = new boolean[n + 1];
        dfs(v);
        sb.append("\\n");

        // BFS
        visited = new boolean[n + 1];
        bfs(v);

        System.out.println(sb);
    }

    static void dfs(int cur) {
        visited[cur] = true;
        sb.append(cur).append(" ");

        for (int next : graph[cur]) {
            if (!visited[next]) {
                dfs(next);
            }
        }
    }

    static void bfs(int start) {
        Queue<Integer> queue = new LinkedList<>();
        queue.add(start);
        visited[start] = true;

        while (!queue.isEmpty()) {
            int cur = queue.poll();
            sb.append(cur).append(" ");

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
    "baekjoon_1920": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 수 찾기 - 이분 탐색 또는 집합
import sys
input = sys.stdin.readline

n = int(input())
a = set(map(int, input().split()))
m = int(input())
queries = list(map(int, input().split()))

for q in queries:
    print(1 if q in a else 0)
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

    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    sort(a.begin(), a.end());

    int m;
    cin >> m;

    for (int i = 0; i < m; i++) {
        int x;
        cin >> x;

        // 이분 탐색
        if (binary_search(a.begin(), a.end(), x)) {
            cout << 1 << "\\n";
        } else {
            cout << 0 << "\\n";
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
        StringTokenizer st = new StringTokenizer(br.readLine());

        HashSet<Integer> set = new HashSet<>();
        for (int i = 0; i < n; i++) {
            set.add(Integer.parseInt(st.nextToken()));
        }

        int m = Integer.parseInt(br.readLine());
        st = new StringTokenizer(br.readLine());

        for (int i = 0; i < m; i++) {
            int x = Integer.parseInt(st.nextToken());
            sb.append(set.contains(x) ? 1 : 0).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_1929": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 소수 구하기 - 에라토스테네스의 체
import sys

m, n = map(int, input().split())

# 에라토스테네스의 체
is_prime = [True] * (n + 1)
is_prime[0] = is_prime[1] = False

for i in range(2, int(n ** 0.5) + 1):
    if is_prime[i]:
        for j in range(i * i, n + 1, i):
            is_prime[j] = False

result = []
for i in range(m, n + 1):
    if is_prime[i]:
        result.append(str(i))

print('\\n'.join(result))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int m, n;
    cin >> m >> n;

    // 에라토스테네스의 체
    vector<bool> is_prime(n + 1, true);
    is_prime[0] = is_prime[1] = false;

    for (int i = 2; i * i <= n; i++) {
        if (is_prime[i]) {
            for (int j = i * i; j <= n; j += i) {
                is_prime[j] = false;
            }
        }
    }

    for (int i = m; i <= n; i++) {
        if (is_prime[i]) {
            cout << i << "\\n";
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
        int m = Integer.parseInt(st.nextToken());
        int n = Integer.parseInt(st.nextToken());

        // 에라토스테네스의 체
        boolean[] isPrime = new boolean[n + 1];
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;

        for (int i = 2; i * i <= n; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j <= n; j += i) {
                    isPrime[j] = false;
                }
            }
        }

        for (int i = m; i <= n; i++) {
            if (isPrime[i]) {
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
    "baekjoon_10828": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 스택 구현
import sys
input = sys.stdin.readline

n = int(input())
stack = []
result = []

for _ in range(n):
    cmd = input().split()

    if cmd[0] == 'push':
        stack.append(int(cmd[1]))
    elif cmd[0] == 'pop':
        result.append(stack.pop() if stack else -1)
    elif cmd[0] == 'size':
        result.append(len(stack))
    elif cmd[0] == 'empty':
        result.append(0 if stack else 1)
    elif cmd[0] == 'top':
        result.append(stack[-1] if stack else -1)

print('\\n'.join(map(str, result)))
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

    int n;
    cin >> n;

    stack<int> st;

    for (int i = 0; i < n; i++) {
        string cmd;
        cin >> cmd;

        if (cmd == "push") {
            int x;
            cin >> x;
            st.push(x);
        } else if (cmd == "pop") {
            if (st.empty()) {
                cout << -1 << "\\n";
            } else {
                cout << st.top() << "\\n";
                st.pop();
            }
        } else if (cmd == "size") {
            cout << st.size() << "\\n";
        } else if (cmd == "empty") {
            cout << (st.empty() ? 1 : 0) << "\\n";
        } else if (cmd == "top") {
            if (st.empty()) {
                cout << -1 << "\\n";
            } else {
                cout << st.top() << "\\n";
            }
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
        Stack<Integer> stack = new Stack<>();

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String cmd = st.nextToken();

            if (cmd.equals("push")) {
                int x = Integer.parseInt(st.nextToken());
                stack.push(x);
            } else if (cmd.equals("pop")) {
                sb.append(stack.isEmpty() ? -1 : stack.pop()).append("\\n");
            } else if (cmd.equals("size")) {
                sb.append(stack.size()).append("\\n");
            } else if (cmd.equals("empty")) {
                sb.append(stack.isEmpty() ? 1 : 0).append("\\n");
            } else if (cmd.equals("top")) {
                sb.append(stack.isEmpty() ? -1 : stack.peek()).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_1697": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 숨바꼭질 - BFS
from collections import deque

n, k = map(int, input().split())

if n >= k:
    print(n - k)
else:
    MAX = 100001
    visited = [-1] * MAX
    visited[n] = 0

    queue = deque([n])

    while queue:
        cur = queue.popleft()

        if cur == k:
            print(visited[cur])
            break

        for next_pos in [cur - 1, cur + 1, cur * 2]:
            if 0 <= next_pos < MAX and visited[next_pos] == -1:
                visited[next_pos] = visited[cur] + 1
                queue.append(next_pos)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <queue>
using namespace std;

const int MAX = 100001;
int visited[MAX];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    if (n >= k) {
        cout << n - k << endl;
        return 0;
    }

    fill(visited, visited + MAX, -1);
    visited[n] = 0;

    queue<int> q;
    q.push(n);

    while (!q.empty()) {
        int cur = q.front();
        q.pop();

        if (cur == k) {
            cout << visited[cur] << endl;
            break;
        }

        int next_positions[] = {cur - 1, cur + 1, cur * 2};
        for (int next_pos : next_positions) {
            if (next_pos >= 0 && next_pos < MAX && visited[next_pos] == -1) {
                visited[next_pos] = visited[cur] + 1;
                q.push(next_pos);
            }
        }
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
        int n = sc.nextInt();
        int k = sc.nextInt();

        if (n >= k) {
            System.out.println(n - k);
            return;
        }

        final int MAX = 100001;
        int[] visited = new int[MAX];
        Arrays.fill(visited, -1);
        visited[n] = 0;

        Queue<Integer> queue = new LinkedList<>();
        queue.add(n);

        while (!queue.isEmpty()) {
            int cur = queue.poll();

            if (cur == k) {
                System.out.println(visited[cur]);
                break;
            }

            int[] nextPositions = {cur - 1, cur + 1, cur * 2};
            for (int nextPos : nextPositions) {
                if (nextPos >= 0 && nextPos < MAX && visited[nextPos] == -1) {
                    visited[nextPos] = visited[cur] + 1;
                    queue.add(nextPos);
                }
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_1654": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 랜선 자르기 - 이분 탐색
import sys
input = sys.stdin.readline

k, n = map(int, input().split())
cables = [int(input()) for _ in range(k)]

left, right = 1, max(cables)
result = 0

while left <= right:
    mid = (left + right) // 2

    # mid 길이로 자를 때 만들 수 있는 랜선 개수
    count = sum(c // mid for c in cables)

    if count >= n:
        result = mid
        left = mid + 1
    else:
        right = mid - 1

print(result)
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

    int k, n;
    cin >> k >> n;

    long long cables[10000];
    long long maxLen = 0;

    for (int i = 0; i < k; i++) {
        cin >> cables[i];
        maxLen = max(maxLen, cables[i]);
    }

    long long left = 1, right = maxLen;
    long long result = 0;

    while (left <= right) {
        long long mid = (left + right) / 2;

        // mid 길이로 자를 때 만들 수 있는 랜선 개수
        long long count = 0;
        for (int i = 0; i < k; i++) {
            count += cables[i] / mid;
        }

        if (count >= n) {
            result = mid;
            left = mid + 1;
        } else {
            right = mid - 1;
        }
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
        StringTokenizer st = new StringTokenizer(br.readLine());

        int k = Integer.parseInt(st.nextToken());
        int n = Integer.parseInt(st.nextToken());

        long[] cables = new long[k];
        long maxLen = 0;

        for (int i = 0; i < k; i++) {
            cables[i] = Long.parseLong(br.readLine());
            maxLen = Math.max(maxLen, cables[i]);
        }

        long left = 1, right = maxLen;
        long result = 0;

        while (left <= right) {
            long mid = (left + right) / 2;

            // mid 길이로 자를 때 만들 수 있는 랜선 개수
            long count = 0;
            for (int i = 0; i < k; i++) {
                count += cables[i] / mid;
            }

            if (count >= n) {
                result = mid;
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        System.out.println(result);
    }
}
'''
            }
        ]
    },
    "baekjoon_9012": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 괄호 - 스택
import sys
input = sys.stdin.readline

t = int(input())

for _ in range(t):
    s = input().strip()
    count = 0
    valid = True

    for c in s:
        if c == '(':
            count += 1
        else:
            count -= 1
            if count < 0:
                valid = False
                break

    if valid and count == 0:
        print("YES")
    else:
        print("NO")
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

    int t;
    cin >> t;

    while (t--) {
        string s;
        cin >> s;

        int count = 0;
        bool valid = true;

        for (char c : s) {
            if (c == '(') {
                count++;
            } else {
                count--;
                if (count < 0) {
                    valid = false;
                    break;
                }
            }
        }

        if (valid && count == 0) {
            cout << "YES\\n";
        } else {
            cout << "NO\\n";
        }
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
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine());

        while (t-- > 0) {
            String s = br.readLine();
            int count = 0;
            boolean valid = true;

            for (char c : s.toCharArray()) {
                if (c == '(') {
                    count++;
                } else {
                    count--;
                    if (count < 0) {
                        valid = false;
                        break;
                    }
                }
            }

            if (valid && count == 0) {
                sb.append("YES\\n");
            } else {
                sb.append("NO\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_1003": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 피보나치 함수 - DP
import sys
input = sys.stdin.readline

# 미리 계산
# fib(n) 호출 시 0 출력 횟수 = fib(n-1)의 0 출력 횟수 + fib(n-2)의 0 출력 횟수
# fib(0): 0 1번, 1 0번
# fib(1): 0 0번, 1 1번

MAX = 41
zero = [0] * MAX
one = [0] * MAX
zero[0], one[0] = 1, 0
zero[1], one[1] = 0, 1

for i in range(2, MAX):
    zero[i] = zero[i-1] + zero[i-2]
    one[i] = one[i-1] + one[i-2]

t = int(input())
for _ in range(t):
    n = int(input())
    print(zero[n], one[n])
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int zero[41], one[41];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    // 미리 계산
    zero[0] = 1; one[0] = 0;
    zero[1] = 0; one[1] = 1;

    for (int i = 2; i <= 40; i++) {
        zero[i] = zero[i-1] + zero[i-2];
        one[i] = one[i-1] + one[i-2];
    }

    int t;
    cin >> t;

    while (t--) {
        int n;
        cin >> n;
        cout << zero[n] << " " << one[n] << "\\n";
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
        StringBuilder sb = new StringBuilder();

        // 미리 계산
        int[] zero = new int[41];
        int[] one = new int[41];
        zero[0] = 1; one[0] = 0;
        zero[1] = 0; one[1] = 1;

        for (int i = 2; i <= 40; i++) {
            zero[i] = zero[i-1] + zero[i-2];
            one[i] = one[i-1] + one[i-2];
        }

        int t = Integer.parseInt(br.readLine());

        while (t-- > 0) {
            int n = Integer.parseInt(br.readLine());
            sb.append(zero[n]).append(" ").append(one[n]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_2805": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 나무 자르기 - 이분 탐색
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
trees = list(map(int, input().split()))

left, right = 0, max(trees)
result = 0

while left <= right:
    mid = (left + right) // 2

    # 높이 mid로 잘랐을 때 얻는 나무 양
    total = sum(max(0, t - mid) for t in trees)

    if total >= m:
        result = mid
        left = mid + 1
    else:
        right = mid - 1

print(result)
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

    int n, m;
    cin >> n >> m;

    int trees[1000000];
    int maxHeight = 0;

    for (int i = 0; i < n; i++) {
        cin >> trees[i];
        maxHeight = max(maxHeight, trees[i]);
    }

    long long left = 0, right = maxHeight;
    long long result = 0;

    while (left <= right) {
        long long mid = (left + right) / 2;

        // 높이 mid로 잘랐을 때 얻는 나무 양
        long long total = 0;
        for (int i = 0; i < n; i++) {
            if (trees[i] > mid) {
                total += trees[i] - mid;
            }
        }

        if (total >= m) {
            result = mid;
            left = mid + 1;
        } else {
            right = mid - 1;
        }
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
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        int[] trees = new int[n];
        int maxHeight = 0;

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            trees[i] = Integer.parseInt(st.nextToken());
            maxHeight = Math.max(maxHeight, trees[i]);
        }

        long left = 0, right = maxHeight;
        long result = 0;

        while (left <= right) {
            long mid = (left + right) / 2;

            // 높이 mid로 잘랐을 때 얻는 나무 양
            long total = 0;
            for (int i = 0; i < n; i++) {
                if (trees[i] > mid) {
                    total += trees[i] - mid;
                }
            }

            if (total >= m) {
                result = mid;
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        System.out.println(result);
    }
}
'''
            }
        ]
    },
    "baekjoon_2178": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 미로 탐색 - BFS
from collections import deque
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
maze = [input().strip() for _ in range(n)]

# BFS
dist = [[-1] * m for _ in range(n)]
dist[0][0] = 1

queue = deque([(0, 0)])
dx = [0, 0, 1, -1]
dy = [1, -1, 0, 0]

while queue:
    x, y = queue.popleft()

    for i in range(4):
        nx, ny = x + dx[i], y + dy[i]

        if 0 <= nx < n and 0 <= ny < m:
            if maze[nx][ny] == '1' and dist[nx][ny] == -1:
                dist[nx][ny] = dist[x][y] + 1
                queue.append((nx, ny))

print(dist[n-1][m-1])
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <queue>
#include <string>
using namespace std;

int n, m;
string maze[100];
int dist[100][100];
int dx[] = {0, 0, 1, -1};
int dy[] = {1, -1, 0, 0};

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> m;

    for (int i = 0; i < n; i++) {
        cin >> maze[i];
        for (int j = 0; j < m; j++) {
            dist[i][j] = -1;
        }
    }

    // BFS
    queue<pair<int, int>> q;
    q.push({0, 0});
    dist[0][0] = 1;

    while (!q.empty()) {
        int x = q.front().first;
        int y = q.front().second;
        q.pop();

        for (int i = 0; i < 4; i++) {
            int nx = x + dx[i];
            int ny = y + dy[i];

            if (nx >= 0 && nx < n && ny >= 0 && ny < m) {
                if (maze[nx][ny] == '1' && dist[nx][ny] == -1) {
                    dist[nx][ny] = dist[x][y] + 1;
                    q.push({nx, ny});
                }
            }
        }
    }

    cout << dist[n-1][m-1] << endl;

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

        String[] maze = new String[n];
        int[][] dist = new int[n][m];

        for (int i = 0; i < n; i++) {
            maze[i] = br.readLine();
            Arrays.fill(dist[i], -1);
        }

        // BFS
        int[] dx = {0, 0, 1, -1};
        int[] dy = {1, -1, 0, 0};

        Queue<int[]> queue = new LinkedList<>();
        queue.add(new int[]{0, 0});
        dist[0][0] = 1;

        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            int x = cur[0], y = cur[1];

            for (int i = 0; i < 4; i++) {
                int nx = x + dx[i];
                int ny = y + dy[i];

                if (nx >= 0 && nx < n && ny >= 0 && ny < m) {
                    if (maze[nx].charAt(ny) == '1' && dist[nx][ny] == -1) {
                        dist[nx][ny] = dist[x][y] + 1;
                        queue.add(new int[]{nx, ny});
                    }
                }
            }
        }

        System.out.println(dist[n-1][m-1]);
    }
}
'''
            }
        ]
    },
    "baekjoon_1002": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 터렛 - 두 원의 교점 개수
import math

t = int(input())

for _ in range(t):
    x1, y1, r1, x2, y2, r2 = map(int, input().split())

    # 두 원의 중심 사이 거리
    d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    # 동심원인 경우
    if d == 0:
        if r1 == r2:
            print(-1)  # 무한개
        else:
            print(0)  # 교점 없음
    # 외접 또는 내접
    elif d == r1 + r2 or d == abs(r1 - r2):
        print(1)
    # 두 점에서 만남
    elif abs(r1 - r2) < d < r1 + r2:
        print(2)
    # 만나지 않음
    else:
        print(0)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        double x1, y1, r1, x2, y2, r2;
        cin >> x1 >> y1 >> r1 >> x2 >> y2 >> r2;

        // 두 원의 중심 사이 거리
        double d = sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));

        // 동심원인 경우
        if (d == 0) {
            if (r1 == r2) {
                cout << -1 << "\\n";  // 무한개
            } else {
                cout << 0 << "\\n";  // 교점 없음
            }
        }
        // 외접 또는 내접
        else if (d == r1 + r2 || d == abs(r1 - r2)) {
            cout << 1 << "\\n";
        }
        // 두 점에서 만남
        else if (abs(r1 - r2) < d && d < r1 + r2) {
            cout << 2 << "\\n";
        }
        // 만나지 않음
        else {
            cout << 0 << "\\n";
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

        int t = Integer.parseInt(br.readLine());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            double x1 = Double.parseDouble(st.nextToken());
            double y1 = Double.parseDouble(st.nextToken());
            double r1 = Double.parseDouble(st.nextToken());
            double x2 = Double.parseDouble(st.nextToken());
            double y2 = Double.parseDouble(st.nextToken());
            double r2 = Double.parseDouble(st.nextToken());

            // 두 원의 중심 사이 거리
            double d = Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));

            // 동심원인 경우
            if (d == 0) {
                if (r1 == r2) {
                    sb.append(-1).append("\\n");  // 무한개
                } else {
                    sb.append(0).append("\\n");  // 교점 없음
                }
            }
            // 외접 또는 내접
            else if (d == r1 + r2 || d == Math.abs(r1 - r2)) {
                sb.append(1).append("\\n");
            }
            // 두 점에서 만남
            else if (Math.abs(r1 - r2) < d && d < r1 + r2) {
                sb.append(2).append("\\n");
            }
            // 만나지 않음
            else {
                sb.append(0).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_1181": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 단어 정렬
import sys
input = sys.stdin.readline

n = int(input())
words = set()

for _ in range(n):
    words.add(input().strip())

# 길이 순, 같으면 사전 순
sorted_words = sorted(words, key=lambda x: (len(x), x))

print('\\n'.join(sorted_words))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
#include <vector>
#include <set>
#include <string>
using namespace std;

bool compare(const string& a, const string& b) {
    if (a.length() != b.length()) {
        return a.length() < b.length();
    }
    return a < b;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    set<string> wordSet;

    for (int i = 0; i < n; i++) {
        string word;
        cin >> word;
        wordSet.insert(word);
    }

    vector<string> words(wordSet.begin(), wordSet.end());
    sort(words.begin(), words.end(), compare);

    for (const string& word : words) {
        cout << word << "\\n";
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

        Set<String> wordSet = new HashSet<>();

        for (int i = 0; i < n; i++) {
            wordSet.add(br.readLine());
        }

        List<String> words = new ArrayList<>(wordSet);

        // 길이 순, 같으면 사전 순
        Collections.sort(words, (a, b) -> {
            if (a.length() != b.length()) {
                return a.length() - b.length();
            }
            return a.compareTo(b);
        });

        for (String word : words) {
            sb.append(word).append("\\n");
        }

        System.out.print(sb);
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
