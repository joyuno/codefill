#!/usr/bin/env python3
"""배치 22: 기본 알고리즘 medium 문제 솔루션 추가"""

import json

new_solutions = {
    "baekjoon_1764": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 듣보잡 - 교집합
import sys
input = sys.stdin.readline

n, m = map(int, input().split())

never_heard = set(input().strip() for _ in range(n))
never_seen = set(input().strip() for _ in range(m))

# 듣도 보도 못한 사람 = 교집합
result = sorted(never_heard & never_seen)

print(len(result))
for name in result:
    print(name)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <set>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    set<string> neverHeard;
    for (int i = 0; i < n; i++) {
        string name;
        cin >> name;
        neverHeard.insert(name);
    }

    vector<string> result;
    for (int i = 0; i < m; i++) {
        string name;
        cin >> name;
        if (neverHeard.count(name)) {
            result.push_back(name);
        }
    }

    sort(result.begin(), result.end());

    cout << result.size() << "\\n";
    for (const string& name : result) {
        cout << name << "\\n";
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

        Set<String> neverHeard = new HashSet<>();
        for (int i = 0; i < n; i++) {
            neverHeard.add(br.readLine());
        }

        List<String> result = new ArrayList<>();
        for (int i = 0; i < m; i++) {
            String name = br.readLine();
            if (neverHeard.contains(name)) {
                result.add(name);
            }
        }

        Collections.sort(result);

        sb.append(result.size()).append("\\n");
        for (String name : result) {
            sb.append(name).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_10815": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 숫자 카드 - 집합
import sys
input = sys.stdin.readline

n = int(input())
cards = set(map(int, input().split()))
m = int(input())
queries = list(map(int, input().split()))

print(' '.join('1' if q in cards else '0' for q in queries))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    set<int> cards;
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        cards.insert(x);
    }

    int m;
    cin >> m;

    for (int i = 0; i < m; i++) {
        int x;
        cin >> x;
        cout << (cards.count(x) ? 1 : 0);
        if (i < m - 1) cout << " ";
    }
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
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine());
        Set<Integer> cards = new HashSet<>();

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            cards.add(Integer.parseInt(st.nextToken()));
        }

        int m = Integer.parseInt(br.readLine());
        st = new StringTokenizer(br.readLine());

        for (int i = 0; i < m; i++) {
            int x = Integer.parseInt(st.nextToken());
            sb.append(cards.contains(x) ? 1 : 0);
            if (i < m - 1) sb.append(" ");
        }

        System.out.println(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_1193": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 분수찾기 - 대각선 규칙
x = int(input())

# n번째 대각선에는 n개의 분수가 있음
# 1~n번째 대각선까지 총 n(n+1)/2개의 분수
diagonal = 1
total = 0

while total + diagonal < x:
    total += diagonal
    diagonal += 1

# diagonal번째 대각선에서 몇 번째인지
pos = x - total

if diagonal % 2 == 1:
    # 홀수 대각선: 아래에서 위로 (분자 감소, 분모 증가)
    numerator = diagonal - pos + 1
    denominator = pos
else:
    # 짝수 대각선: 위에서 아래로 (분자 증가, 분모 감소)
    numerator = pos
    denominator = diagonal - pos + 1

print(f"{numerator}/{denominator}")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    int x;
    cin >> x;

    int diagonal = 1;
    int total = 0;

    while (total + diagonal < x) {
        total += diagonal;
        diagonal++;
    }

    int pos = x - total;
    int numerator, denominator;

    if (diagonal % 2 == 1) {
        numerator = diagonal - pos + 1;
        denominator = pos;
    } else {
        numerator = pos;
        denominator = diagonal - pos + 1;
    }

    cout << numerator << "/" << denominator << endl;

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
        int x = sc.nextInt();

        int diagonal = 1;
        int total = 0;

        while (total + diagonal < x) {
            total += diagonal;
            diagonal++;
        }

        int pos = x - total;
        int numerator, denominator;

        if (diagonal % 2 == 1) {
            numerator = diagonal - pos + 1;
            denominator = pos;
        } else {
            numerator = pos;
            denominator = diagonal - pos + 1;
        }

        System.out.println(numerator + "/" + denominator);
    }
}
'''
            }
        ]
    },
    "baekjoon_15649": {
        "solutions": [
            {
                "language": "python",
                "code": '''# N과 M (1) - 백트래킹
import sys

def backtrack(arr, n, m, used):
    if len(arr) == m:
        print(' '.join(map(str, arr)))
        return

    for i in range(1, n + 1):
        if not used[i]:
            used[i] = True
            arr.append(i)
            backtrack(arr, n, m, used)
            arr.pop()
            used[i] = False

n, m = map(int, input().split())
used = [False] * (n + 1)
backtrack([], n, m, used)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
using namespace std;

int n, m;
vector<int> arr;
bool used[9];

void backtrack() {
    if (arr.size() == m) {
        for (int i = 0; i < m; i++) {
            cout << arr[i];
            if (i < m - 1) cout << " ";
        }
        cout << "\\n";
        return;
    }

    for (int i = 1; i <= n; i++) {
        if (!used[i]) {
            used[i] = true;
            arr.push_back(i);
            backtrack();
            arr.pop_back();
            used[i] = false;
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> m;
    backtrack();

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int n, m;
    static int[] arr;
    static boolean[] used;
    static StringBuilder sb = new StringBuilder();

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        n = Integer.parseInt(st.nextToken());
        m = Integer.parseInt(st.nextToken());

        arr = new int[m];
        used = new boolean[n + 1];

        backtrack(0);

        System.out.print(sb);
    }

    static void backtrack(int depth) {
        if (depth == m) {
            for (int i = 0; i < m; i++) {
                sb.append(arr[i]);
                if (i < m - 1) sb.append(" ");
            }
            sb.append("\\n");
            return;
        }

        for (int i = 1; i <= n; i++) {
            if (!used[i]) {
                used[i] = true;
                arr[depth] = i;
                backtrack(depth + 1);
                used[i] = false;
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_11399": {
        "solutions": [
            {
                "language": "python",
                "code": '''# ATM - 그리디 (최소 시간 먼저)
import sys
input = sys.stdin.readline

n = int(input())
times = list(map(int, input().split()))

times.sort()

# 누적 합의 합
total = 0
current = 0
for t in times:
    current += t
    total += current

print(total)
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

    int times[1000];
    for (int i = 0; i < n; i++) {
        cin >> times[i];
    }

    sort(times, times + n);

    int total = 0;
    int current = 0;
    for (int i = 0; i < n; i++) {
        current += times[i];
        total += current;
    }

    cout << total << endl;

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

        int[] times = new int[n];
        for (int i = 0; i < n; i++) {
            times[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(times);

        int total = 0;
        int current = 0;
        for (int i = 0; i < n; i++) {
            current += times[i];
            total += current;
        }

        System.out.println(total);
    }
}
'''
            }
        ]
    },
    "baekjoon_1158": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 요세푸스 문제 - 큐
from collections import deque

n, k = map(int, input().split())
queue = deque(range(1, n + 1))
result = []

while queue:
    for _ in range(k - 1):
        queue.append(queue.popleft())
    result.append(queue.popleft())

print('<' + ', '.join(map(str, result)) + '>')
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <queue>
using namespace std;

int main() {
    int n, k;
    cin >> n >> k;

    queue<int> q;
    for (int i = 1; i <= n; i++) {
        q.push(i);
    }

    cout << "<";
    while (!q.empty()) {
        for (int i = 0; i < k - 1; i++) {
            q.push(q.front());
            q.pop();
        }
        cout << q.front();
        q.pop();
        if (!q.empty()) cout << ", ";
    }
    cout << ">" << endl;

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

        Queue<Integer> queue = new LinkedList<>();
        for (int i = 1; i <= n; i++) {
            queue.add(i);
        }

        StringBuilder sb = new StringBuilder("<");
        while (!queue.isEmpty()) {
            for (int i = 0; i < k - 1; i++) {
                queue.add(queue.poll());
            }
            sb.append(queue.poll());
            if (!queue.isEmpty()) sb.append(", ");
        }
        sb.append(">");

        System.out.println(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_1149": {
        "solutions": [
            {
                "language": "python",
                "code": '''# RGB거리 - DP
import sys
input = sys.stdin.readline

n = int(input())
costs = [list(map(int, input().split())) for _ in range(n)]

# dp[i][j] = i번째 집을 j색으로 칠할 때 최소 비용
dp = [[0] * 3 for _ in range(n)]
dp[0] = costs[0][:]

for i in range(1, n):
    dp[i][0] = costs[i][0] + min(dp[i-1][1], dp[i-1][2])
    dp[i][1] = costs[i][1] + min(dp[i-1][0], dp[i-1][2])
    dp[i][2] = costs[i][2] + min(dp[i-1][0], dp[i-1][1])

print(min(dp[n-1]))
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

    int costs[1000][3];
    int dp[1000][3];

    for (int i = 0; i < n; i++) {
        cin >> costs[i][0] >> costs[i][1] >> costs[i][2];
    }

    dp[0][0] = costs[0][0];
    dp[0][1] = costs[0][1];
    dp[0][2] = costs[0][2];

    for (int i = 1; i < n; i++) {
        dp[i][0] = costs[i][0] + min(dp[i-1][1], dp[i-1][2]);
        dp[i][1] = costs[i][1] + min(dp[i-1][0], dp[i-1][2]);
        dp[i][2] = costs[i][2] + min(dp[i-1][0], dp[i-1][1]);
    }

    cout << min({dp[n-1][0], dp[n-1][1], dp[n-1][2]}) << endl;

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
        int[][] costs = new int[n][3];
        int[][] dp = new int[n][3];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            costs[i][0] = Integer.parseInt(st.nextToken());
            costs[i][1] = Integer.parseInt(st.nextToken());
            costs[i][2] = Integer.parseInt(st.nextToken());
        }

        dp[0][0] = costs[0][0];
        dp[0][1] = costs[0][1];
        dp[0][2] = costs[0][2];

        for (int i = 1; i < n; i++) {
            dp[i][0] = costs[i][0] + Math.min(dp[i-1][1], dp[i-1][2]);
            dp[i][1] = costs[i][1] + Math.min(dp[i-1][0], dp[i-1][2]);
            dp[i][2] = costs[i][2] + Math.min(dp[i-1][0], dp[i-1][1]);
        }

        System.out.println(Math.min(dp[n-1][0], Math.min(dp[n-1][1], dp[n-1][2])));
    }
}
'''
            }
        ]
    },
    "baekjoon_2468": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 안전 영역 - BFS
import sys
from collections import deque
input = sys.stdin.readline

n = int(input())
grid = [list(map(int, input().split())) for _ in range(n)]

def count_safe_areas(height):
    visited = [[False] * n for _ in range(n)]
    count = 0
    dx = [0, 0, 1, -1]
    dy = [1, -1, 0, 0]

    for i in range(n):
        for j in range(n):
            if grid[i][j] > height and not visited[i][j]:
                # BFS
                queue = deque([(i, j)])
                visited[i][j] = True

                while queue:
                    x, y = queue.popleft()
                    for d in range(4):
                        nx, ny = x + dx[d], y + dy[d]
                        if 0 <= nx < n and 0 <= ny < n:
                            if grid[nx][ny] > height and not visited[nx][ny]:
                                visited[nx][ny] = True
                                queue.append((nx, ny))

                count += 1

    return count

# 모든 높이에 대해 시도 (0 포함 - 비가 안 올 때)
max_height = max(max(row) for row in grid)
result = max(count_safe_areas(h) for h in range(max_height + 1))

print(result)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <queue>
#include <algorithm>
using namespace std;

int n;
int grid[100][100];
bool visited[100][100];
int dx[] = {0, 0, 1, -1};
int dy[] = {1, -1, 0, 0};

int countSafeAreas(int height) {
    fill(&visited[0][0], &visited[0][0] + 100 * 100, false);
    int count = 0;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (grid[i][j] > height && !visited[i][j]) {
                queue<pair<int, int>> q;
                q.push({i, j});
                visited[i][j] = true;

                while (!q.empty()) {
                    int x = q.front().first;
                    int y = q.front().second;
                    q.pop();

                    for (int d = 0; d < 4; d++) {
                        int nx = x + dx[d];
                        int ny = y + dy[d];

                        if (nx >= 0 && nx < n && ny >= 0 && ny < n) {
                            if (grid[nx][ny] > height && !visited[nx][ny]) {
                                visited[nx][ny] = true;
                                q.push({nx, ny});
                            }
                        }
                    }
                }

                count++;
            }
        }
    }

    return count;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;

    int maxHeight = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cin >> grid[i][j];
            maxHeight = max(maxHeight, grid[i][j]);
        }
    }

    int result = 0;
    for (int h = 0; h <= maxHeight; h++) {
        result = max(result, countSafeAreas(h));
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
    static int n;
    static int[][] grid;
    static boolean[][] visited;
    static int[] dx = {0, 0, 1, -1};
    static int[] dy = {1, -1, 0, 0};

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        n = Integer.parseInt(br.readLine());
        grid = new int[n][n];

        int maxHeight = 0;
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                grid[i][j] = Integer.parseInt(st.nextToken());
                maxHeight = Math.max(maxHeight, grid[i][j]);
            }
        }

        int result = 0;
        for (int h = 0; h <= maxHeight; h++) {
            result = Math.max(result, countSafeAreas(h));
        }

        System.out.println(result);
    }

    static int countSafeAreas(int height) {
        visited = new boolean[n][n];
        int count = 0;

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] > height && !visited[i][j]) {
                    bfs(i, j, height);
                    count++;
                }
            }
        }

        return count;
    }

    static void bfs(int si, int sj, int height) {
        Queue<int[]> queue = new LinkedList<>();
        queue.add(new int[]{si, sj});
        visited[si][sj] = true;

        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            int x = cur[0], y = cur[1];

            for (int d = 0; d < 4; d++) {
                int nx = x + dx[d];
                int ny = y + dy[d];

                if (nx >= 0 && nx < n && ny >= 0 && ny < n) {
                    if (grid[nx][ny] > height && !visited[nx][ny]) {
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
    "baekjoon_18258": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 큐 2 - deque 사용
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
#include <deque>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    deque<int> dq;

    while (n--) {
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

        while (n-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String cmd = st.nextToken();

            if (cmd.equals("push")) {
                queue.addLast(Integer.parseInt(st.nextToken()));
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
    "baekjoon_9461": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 파도반 수열 - DP
import sys
input = sys.stdin.readline

# P(n) = P(n-2) + P(n-3)
dp = [0] * 101
dp[1] = dp[2] = dp[3] = 1
dp[4] = dp[5] = 2

for i in range(6, 101):
    dp[i] = dp[i-2] + dp[i-3]

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
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long dp[101];
    dp[1] = dp[2] = dp[3] = 1;
    dp[4] = dp[5] = 2;

    for (int i = 6; i <= 100; i++) {
        dp[i] = dp[i-2] + dp[i-3];
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
                "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        long[] dp = new long[101];
        dp[1] = dp[2] = dp[3] = 1;
        dp[4] = dp[5] = 2;

        for (int i = 6; i <= 100; i++) {
            dp[i] = dp[i-2] + dp[i-3];
        }

        int t = Integer.parseInt(br.readLine());

        while (t-- > 0) {
            int n = Integer.parseInt(br.readLine());
            sb.append(dp[n]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_1010": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 다리 놓기 - 조합 (mCn)
import sys
from math import comb
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n, m = map(int, input().split())
    print(comb(m, n))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    // 조합 테이블 미리 계산
    long long dp[30][30] = {0};

    for (int i = 0; i < 30; i++) {
        dp[i][0] = 1;
        dp[i][i] = 1;
        for (int j = 1; j < i; j++) {
            dp[i][j] = dp[i-1][j-1] + dp[i-1][j];
        }
    }

    int t;
    cin >> t;

    while (t--) {
        int n, m;
        cin >> n >> m;
        cout << dp[m][n] << "\\n";
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

        // 조합 테이블 미리 계산
        long[][] dp = new long[30][30];

        for (int i = 0; i < 30; i++) {
            dp[i][0] = 1;
            dp[i][i] = 1;
            for (int j = 1; j < i; j++) {
                dp[i][j] = dp[i-1][j-1] + dp[i-1][j];
            }
        }

        int t = Integer.parseInt(br.readLine());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int m = Integer.parseInt(st.nextToken());
            sb.append(dp[m][n]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_18870": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 좌표 압축
import sys
input = sys.stdin.readline

n = int(input())
coords = list(map(int, input().split()))

# 정렬된 고유값에 인덱스 부여
sorted_unique = sorted(set(coords))
rank = {v: i for i, v in enumerate(sorted_unique)}

print(' '.join(str(rank[c]) for c in coords))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> coords(n);
    vector<int> sorted_coords(n);

    for (int i = 0; i < n; i++) {
        cin >> coords[i];
        sorted_coords[i] = coords[i];
    }

    sort(sorted_coords.begin(), sorted_coords.end());
    sorted_coords.erase(unique(sorted_coords.begin(), sorted_coords.end()), sorted_coords.end());

    map<int, int> rank;
    for (int i = 0; i < sorted_coords.size(); i++) {
        rank[sorted_coords[i]] = i;
    }

    for (int i = 0; i < n; i++) {
        cout << rank[coords[i]];
        if (i < n - 1) cout << " ";
    }
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
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] coords = new int[n];
        int[] sorted = new int[n];

        for (int i = 0; i < n; i++) {
            coords[i] = Integer.parseInt(st.nextToken());
            sorted[i] = coords[i];
        }

        Arrays.sort(sorted);

        Map<Integer, Integer> rank = new HashMap<>();
        int r = 0;
        for (int i = 0; i < n; i++) {
            if (!rank.containsKey(sorted[i])) {
                rank.put(sorted[i], r++);
            }
        }

        for (int i = 0; i < n; i++) {
            sb.append(rank.get(coords[i]));
            if (i < n - 1) sb.append(" ");
        }

        System.out.println(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_14888": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 연산자 끼워넣기 - 백트래킹
import sys
input = sys.stdin.readline

n = int(input())
nums = list(map(int, input().split()))
ops = list(map(int, input().split()))  # +, -, *, /

max_val = -1e9
min_val = 1e9

def backtrack(idx, result, ops):
    global max_val, min_val

    if idx == n:
        max_val = max(max_val, result)
        min_val = min(min_val, result)
        return

    for i in range(4):
        if ops[i] > 0:
            ops[i] -= 1
            if i == 0:
                backtrack(idx + 1, result + nums[idx], ops)
            elif i == 1:
                backtrack(idx + 1, result - nums[idx], ops)
            elif i == 2:
                backtrack(idx + 1, result * nums[idx], ops)
            else:
                # C++14 나눗셈: 0을 향해 버림
                if result < 0:
                    backtrack(idx + 1, -(-result // nums[idx]), ops)
                else:
                    backtrack(idx + 1, result // nums[idx], ops)
            ops[i] += 1

backtrack(1, nums[0], ops)
print(max_val)
print(min_val)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int n;
int nums[11];
int ops[4];
int maxVal = -1e9;
int minVal = 1e9;

void backtrack(int idx, int result) {
    if (idx == n) {
        maxVal = max(maxVal, result);
        minVal = min(minVal, result);
        return;
    }

    for (int i = 0; i < 4; i++) {
        if (ops[i] > 0) {
            ops[i]--;
            int next;
            if (i == 0) next = result + nums[idx];
            else if (i == 1) next = result - nums[idx];
            else if (i == 2) next = result * nums[idx];
            else next = result / nums[idx];
            backtrack(idx + 1, next);
            ops[i]++;
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;
    for (int i = 0; i < n; i++) {
        cin >> nums[i];
    }
    for (int i = 0; i < 4; i++) {
        cin >> ops[i];
    }

    backtrack(1, nums[0]);

    cout << maxVal << "\\n" << minVal << endl;

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
    static int[] nums;
    static int[] ops;
    static int maxVal = Integer.MIN_VALUE;
    static int minVal = Integer.MAX_VALUE;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        n = Integer.parseInt(br.readLine());
        nums = new int[n];
        ops = new int[4];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            nums[i] = Integer.parseInt(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < 4; i++) {
            ops[i] = Integer.parseInt(st.nextToken());
        }

        backtrack(1, nums[0]);

        System.out.println(maxVal);
        System.out.println(minVal);
    }

    static void backtrack(int idx, int result) {
        if (idx == n) {
            maxVal = Math.max(maxVal, result);
            minVal = Math.min(minVal, result);
            return;
        }

        for (int i = 0; i < 4; i++) {
            if (ops[i] > 0) {
                ops[i]--;
                int next;
                if (i == 0) next = result + nums[idx];
                else if (i == 1) next = result - nums[idx];
                else if (i == 2) next = result * nums[idx];
                else next = result / nums[idx];
                backtrack(idx + 1, next);
                ops[i]++;
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_10773": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 제로 - 스택
import sys
input = sys.stdin.readline

k = int(input())
stack = []

for _ in range(k):
    n = int(input())
    if n == 0:
        stack.pop()
    else:
        stack.append(n)

print(sum(stack))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <stack>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int k;
    cin >> k;

    stack<int> st;

    while (k--) {
        int n;
        cin >> n;
        if (n == 0) {
            st.pop();
        } else {
            st.push(n);
        }
    }

    long long sum = 0;
    while (!st.empty()) {
        sum += st.top();
        st.pop();
    }

    cout << sum << endl;

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

        int k = Integer.parseInt(br.readLine());
        Stack<Integer> stack = new Stack<>();

        while (k-- > 0) {
            int n = Integer.parseInt(br.readLine());
            if (n == 0) {
                stack.pop();
            } else {
                stack.push(n);
            }
        }

        long sum = 0;
        while (!stack.isEmpty()) {
            sum += stack.pop();
        }

        System.out.println(sum);
    }
}
'''
            }
        ]
    },
    "baekjoon_1436": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 영화감독 숌 - 브루트포스
n = int(input())

count = 0
num = 666

while True:
    if '666' in str(num):
        count += 1
        if count == n:
            print(num)
            break
    num += 1
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    int n;
    cin >> n;

    int count = 0;
    int num = 666;

    while (true) {
        if (to_string(num).find("666") != string::npos) {
            count++;
            if (count == n) {
                cout << num << endl;
                break;
            }
        }
        num++;
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

        int count = 0;
        int num = 666;

        while (true) {
            if (String.valueOf(num).contains("666")) {
                count++;
                if (count == n) {
                    System.out.println(num);
                    break;
                }
            }
            num++;
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
