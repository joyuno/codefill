#!/usr/bin/env python3
"""배치 23: 기본 알고리즘 medium 문제 솔루션 추가"""

import json

new_solutions = {
    "baekjoon_1904": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 01타일 - DP (피보나치)
import sys
input = sys.stdin.readline

n = int(input())
MOD = 15746

# dp[i] = 길이 i인 2진 수열의 개수
# 1로 끝나는 경우: dp[i-1]
# 00으로 끝나는 경우: dp[i-2]
# 피보나치와 동일
if n == 1:
    print(1)
else:
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2

    for i in range(3, n + 1):
        dp[i] = (dp[i-1] + dp[i-2]) % MOD

    print(dp[n])
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

const int MOD = 15746;

int main() {
    int n;
    cin >> n;

    int dp[1000001];
    dp[1] = 1;
    dp[2] = 2;

    for (int i = 3; i <= n; i++) {
        dp[i] = (dp[i-1] + dp[i-2]) % MOD;
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
        int MOD = 15746;

        int[] dp = new int[n + 1];
        dp[1] = 1;
        if (n >= 2) dp[2] = 2;

        for (int i = 3; i <= n; i++) {
            dp[i] = (dp[i-1] + dp[i-2]) % MOD;
        }

        System.out.println(dp[n]);
    }
}
'''
            }
        ]
    },
    "baekjoon_1427": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 소트인사이드 - 내림차순 정렬
n = input()
print(''.join(sorted(n, reverse=True)))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
#include <string>
using namespace std;

int main() {
    string n;
    cin >> n;

    sort(n.begin(), n.end(), greater<char>());

    cout << n << endl;

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
        String n = sc.next();

        char[] chars = n.toCharArray();
        Arrays.sort(chars);

        StringBuilder sb = new StringBuilder(new String(chars));
        System.out.println(sb.reverse());
    }
}
'''
            }
        ]
    },
    "baekjoon_1325": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 효율적인 해킹 - BFS
import sys
from collections import deque
input = sys.stdin.readline

n, m = map(int, input().split())

# 역방향 그래프 (A가 B를 신뢰하면 B->A로 간선)
graph = [[] for _ in range(n + 1)]
for _ in range(m):
    a, b = map(int, input().split())
    graph[b].append(a)

def bfs(start):
    visited = [False] * (n + 1)
    visited[start] = True
    queue = deque([start])
    count = 1

    while queue:
        cur = queue.popleft()
        for next_node in graph[cur]:
            if not visited[next_node]:
                visited[next_node] = True
                count += 1
                queue.append(next_node)

    return count

# 모든 컴퓨터에서 해킹 가능한 컴퓨터 수 계산
counts = [0] + [bfs(i) for i in range(1, n + 1)]
max_count = max(counts)

result = [i for i in range(1, n + 1) if counts[i] == max_count]
print(' '.join(map(str, result)))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <queue>
#include <cstring>
using namespace std;

int n, m;
vector<int> graph[10001];
bool visited[10001];

int bfs(int start) {
    memset(visited, false, sizeof(visited));
    visited[start] = true;
    queue<int> q;
    q.push(start);
    int count = 1;

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

    return count;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> m;

    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        graph[b].push_back(a);
    }

    vector<int> counts(n + 1);
    int maxCount = 0;

    for (int i = 1; i <= n; i++) {
        counts[i] = bfs(i);
        maxCount = max(maxCount, counts[i]);
    }

    for (int i = 1; i <= n; i++) {
        if (counts[i] == maxCount) {
            cout << i << " ";
        }
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
    static int n, m;
    static ArrayList<Integer>[] graph;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        StringTokenizer st = new StringTokenizer(br.readLine());
        n = Integer.parseInt(st.nextToken());
        m = Integer.parseInt(st.nextToken());

        graph = new ArrayList[n + 1];
        for (int i = 1; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            graph[b].add(a);
        }

        int[] counts = new int[n + 1];
        int maxCount = 0;

        for (int i = 1; i <= n; i++) {
            counts[i] = bfs(i);
            maxCount = Math.max(maxCount, counts[i]);
        }

        for (int i = 1; i <= n; i++) {
            if (counts[i] == maxCount) {
                sb.append(i).append(" ");
            }
        }

        System.out.println(sb);
    }

    static int bfs(int start) {
        boolean[] visited = new boolean[n + 1];
        visited[start] = true;
        Queue<Integer> queue = new LinkedList<>();
        queue.add(start);
        int count = 1;

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

        return count;
    }
}
'''
            }
        ]
    },
    "baekjoon_7568": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 덩치 - 브루트포스
import sys
input = sys.stdin.readline

n = int(input())
people = [tuple(map(int, input().split())) for _ in range(n)]

result = []
for i in range(n):
    rank = 1
    for j in range(n):
        if i != j:
            # j가 i보다 덩치가 더 크면
            if people[j][0] > people[i][0] and people[j][1] > people[i][1]:
                rank += 1
    result.append(rank)

print(' '.join(map(str, result)))
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

    int n;
    cin >> n;

    vector<pair<int, int>> people(n);
    for (int i = 0; i < n; i++) {
        cin >> people[i].first >> people[i].second;
    }

    for (int i = 0; i < n; i++) {
        int rank = 1;
        for (int j = 0; j < n; j++) {
            if (i != j) {
                if (people[j].first > people[i].first &&
                    people[j].second > people[i].second) {
                    rank++;
                }
            }
        }
        cout << rank;
        if (i < n - 1) cout << " ";
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
        int[][] people = new int[n][2];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            people[i][0] = Integer.parseInt(st.nextToken());
            people[i][1] = Integer.parseInt(st.nextToken());
        }

        for (int i = 0; i < n; i++) {
            int rank = 1;
            for (int j = 0; j < n; j++) {
                if (i != j) {
                    if (people[j][0] > people[i][0] && people[j][1] > people[i][1]) {
                        rank++;
                    }
                }
            }
            sb.append(rank);
            if (i < n - 1) sb.append(" ");
        }

        System.out.println(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_14889": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 스타트와 링크 - 백트래킹
import sys
input = sys.stdin.readline

n = int(input())
s = [list(map(int, input().split())) for _ in range(n)]

min_diff = float('inf')

def backtrack(idx, team):
    global min_diff

    if len(team) == n // 2:
        other = [i for i in range(n) if i not in team]

        team_score = sum(s[i][j] + s[j][i] for i in team for j in team if i < j)
        other_score = sum(s[i][j] + s[j][i] for i in other for j in other if i < j)

        min_diff = min(min_diff, abs(team_score - other_score))
        return

    for i in range(idx, n):
        team.append(i)
        backtrack(i + 1, team)
        team.pop()

backtrack(0, [])
print(min_diff)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
using namespace std;

int n;
int s[20][20];
int minDiff = 1e9;
vector<int> team;

void backtrack(int idx) {
    if (team.size() == n / 2) {
        vector<int> other;
        for (int i = 0; i < n; i++) {
            if (find(team.begin(), team.end(), i) == team.end()) {
                other.push_back(i);
            }
        }

        int teamScore = 0, otherScore = 0;
        for (int i = 0; i < n / 2; i++) {
            for (int j = 0; j < n / 2; j++) {
                teamScore += s[team[i]][team[j]];
                otherScore += s[other[i]][other[j]];
            }
        }

        minDiff = min(minDiff, abs(teamScore - otherScore));
        return;
    }

    for (int i = idx; i < n; i++) {
        team.push_back(i);
        backtrack(i + 1);
        team.pop_back();
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cin >> s[i][j];
        }
    }

    backtrack(0);

    cout << minDiff << endl;

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
    static int[][] s;
    static int minDiff = Integer.MAX_VALUE;
    static boolean[] selected;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        n = Integer.parseInt(br.readLine());
        s = new int[n][n];
        selected = new boolean[n];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                s[i][j] = Integer.parseInt(st.nextToken());
            }
        }

        backtrack(0, 0);

        System.out.println(minDiff);
    }

    static void backtrack(int idx, int count) {
        if (count == n / 2) {
            int teamScore = 0, otherScore = 0;

            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (selected[i] && selected[j]) {
                        teamScore += s[i][j];
                    } else if (!selected[i] && !selected[j]) {
                        otherScore += s[i][j];
                    }
                }
            }

            minDiff = Math.min(minDiff, Math.abs(teamScore - otherScore));
            return;
        }

        for (int i = idx; i < n; i++) {
            selected[i] = true;
            backtrack(i + 1, count + 1);
            selected[i] = false;
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_4948": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 베르트랑 공준 - 에라토스테네스의 체
import sys
input = sys.stdin.readline

MAX = 123456 * 2 + 1

# 에라토스테네스의 체
is_prime = [True] * MAX
is_prime[0] = is_prime[1] = False

for i in range(2, int(MAX ** 0.5) + 1):
    if is_prime[i]:
        for j in range(i * i, MAX, i):
            is_prime[j] = False

while True:
    n = int(input())
    if n == 0:
        break

    count = sum(1 for i in range(n + 1, 2 * n + 1) if is_prime[i])
    print(count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

const int MAX = 246913;
bool isPrime[MAX];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    // 에라토스테네스의 체
    fill(isPrime, isPrime + MAX, true);
    isPrime[0] = isPrime[1] = false;

    for (int i = 2; i * i < MAX; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j < MAX; j += i) {
                isPrime[j] = false;
            }
        }
    }

    int n;
    while (cin >> n && n != 0) {
        int count = 0;
        for (int i = n + 1; i <= 2 * n; i++) {
            if (isPrime[i]) count++;
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

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int MAX = 246913;
        boolean[] isPrime = new boolean[MAX];
        java.util.Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;

        for (int i = 2; i * i < MAX; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j < MAX; j += i) {
                    isPrime[j] = false;
                }
            }
        }

        int n;
        while ((n = Integer.parseInt(br.readLine())) != 0) {
            int count = 0;
            for (int i = n + 1; i <= 2 * n; i++) {
                if (isPrime[i]) count++;
            }
            sb.append(count).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_14501": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 퇴사 - DP
import sys
input = sys.stdin.readline

n = int(input())
t = []
p = []

for _ in range(n):
    ti, pi = map(int, input().split())
    t.append(ti)
    p.append(pi)

# dp[i] = i일부터 마지막 날까지 얻을 수 있는 최대 수익
dp = [0] * (n + 1)

for i in range(n - 1, -1, -1):
    # 상담 완료 가능한 경우
    if i + t[i] <= n:
        # 상담하는 경우 vs 안 하는 경우
        dp[i] = max(dp[i + 1], p[i] + dp[i + t[i]])
    else:
        dp[i] = dp[i + 1]

print(dp[0])
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

    int t[15], p[15];
    int dp[16] = {0};

    for (int i = 0; i < n; i++) {
        cin >> t[i] >> p[i];
    }

    for (int i = n - 1; i >= 0; i--) {
        if (i + t[i] <= n) {
            dp[i] = max(dp[i + 1], p[i] + dp[i + t[i]]);
        } else {
            dp[i] = dp[i + 1];
        }
    }

    cout << dp[0] << endl;

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
        int[] t = new int[n];
        int[] p = new int[n];
        int[] dp = new int[n + 1];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            t[i] = Integer.parseInt(st.nextToken());
            p[i] = Integer.parseInt(st.nextToken());
        }

        for (int i = n - 1; i >= 0; i--) {
            if (i + t[i] <= n) {
                dp[i] = Math.max(dp[i + 1], p[i] + dp[i + t[i]]);
            } else {
                dp[i] = dp[i + 1];
            }
        }

        System.out.println(dp[0]);
    }
}
'''
            }
        ]
    },
    "baekjoon_1932": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 정수 삼각형 - DP
import sys
input = sys.stdin.readline

n = int(input())
triangle = [list(map(int, input().split())) for _ in range(n)]

# 아래에서 위로 DP
for i in range(n - 2, -1, -1):
    for j in range(i + 1):
        triangle[i][j] += max(triangle[i+1][j], triangle[i+1][j+1])

print(triangle[0][0])
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

    int triangle[500][500];

    for (int i = 0; i < n; i++) {
        for (int j = 0; j <= i; j++) {
            cin >> triangle[i][j];
        }
    }

    // 아래에서 위로 DP
    for (int i = n - 2; i >= 0; i--) {
        for (int j = 0; j <= i; j++) {
            triangle[i][j] += max(triangle[i+1][j], triangle[i+1][j+1]);
        }
    }

    cout << triangle[0][0] << endl;

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
        int[][] triangle = new int[n][n];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j <= i; j++) {
                triangle[i][j] = Integer.parseInt(st.nextToken());
            }
        }

        // 아래에서 위로 DP
        for (int i = n - 2; i >= 0; i--) {
            for (int j = 0; j <= i; j++) {
                triangle[i][j] += Math.max(triangle[i+1][j], triangle[i+1][j+1]);
            }
        }

        System.out.println(triangle[0][0]);
    }
}
'''
            }
        ]
    },
    "baekjoon_11725": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 트리의 부모 찾기 - BFS
import sys
from collections import deque
input = sys.stdin.readline

n = int(input())
graph = [[] for _ in range(n + 1)]

for _ in range(n - 1):
    a, b = map(int, input().split())
    graph[a].append(b)
    graph[b].append(a)

parent = [0] * (n + 1)
visited = [False] * (n + 1)

# BFS from root (1)
queue = deque([1])
visited[1] = True

while queue:
    cur = queue.popleft()
    for next_node in graph[cur]:
        if not visited[next_node]:
            visited[next_node] = True
            parent[next_node] = cur
            queue.append(next_node)

for i in range(2, n + 1):
    print(parent[i])
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

    int n;
    cin >> n;

    vector<int> graph[100001];
    int parent[100001] = {0};
    bool visited[100001] = {false};

    for (int i = 0; i < n - 1; i++) {
        int a, b;
        cin >> a >> b;
        graph[a].push_back(b);
        graph[b].push_back(a);
    }

    // BFS from root (1)
    queue<int> q;
    q.push(1);
    visited[1] = true;

    while (!q.empty()) {
        int cur = q.front();
        q.pop();

        for (int next : graph[cur]) {
            if (!visited[next]) {
                visited[next] = true;
                parent[next] = cur;
                q.push(next);
            }
        }
    }

    for (int i = 2; i <= n; i++) {
        cout << parent[i] << "\\n";
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
        ArrayList<Integer>[] graph = new ArrayList[n + 1];
        int[] parent = new int[n + 1];
        boolean[] visited = new boolean[n + 1];

        for (int i = 1; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < n - 1; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            graph[a].add(b);
            graph[b].add(a);
        }

        // BFS from root (1)
        Queue<Integer> queue = new LinkedList<>();
        queue.add(1);
        visited[1] = true;

        while (!queue.isEmpty()) {
            int cur = queue.poll();
            for (int next : graph[cur]) {
                if (!visited[next]) {
                    visited[next] = true;
                    parent[next] = cur;
                    queue.add(next);
                }
            }
        }

        for (int i = 2; i <= n; i++) {
            sb.append(parent[i]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_2193": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 이친수 - DP
n = int(input())

# dp[i][j] = 길이가 i이고 마지막 숫자가 j인 이친수의 개수
# 이친수는 1로 시작, 11 불가
if n == 1:
    print(1)
else:
    dp = [[0, 0] for _ in range(n + 1)]
    dp[1][1] = 1  # 1로 시작

    for i in range(2, n + 1):
        dp[i][0] = dp[i-1][0] + dp[i-1][1]  # 0은 앞이 0이든 1이든 가능
        dp[i][1] = dp[i-1][0]  # 1은 앞이 0이어야만 함

    print(dp[n][0] + dp[n][1])
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;

    // 피보나치와 동일
    long long dp[91];
    dp[1] = 1;
    dp[2] = 1;

    for (int i = 3; i <= n; i++) {
        dp[i] = dp[i-1] + dp[i-2];
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

        // 피보나치와 동일
        long[] dp = new long[n + 1];
        dp[1] = 1;
        if (n >= 2) dp[2] = 1;

        for (int i = 3; i <= n; i++) {
            dp[i] = dp[i-1] + dp[i-2];
        }

        System.out.println(dp[n]);
    }
}
'''
            }
        ]
    },
    "baekjoon_1927": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 최소 힙 - heapq
import sys
import heapq
input = sys.stdin.readline

n = int(input())
heap = []
result = []

for _ in range(n):
    x = int(input())
    if x == 0:
        if heap:
            result.append(heapq.heappop(heap))
        else:
            result.append(0)
    else:
        heapq.heappush(heap, x)

print('\\n'.join(map(str, result)))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <queue>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    priority_queue<int, vector<int>, greater<int>> pq;  // 최소 힙

    while (n--) {
        int x;
        cin >> x;

        if (x == 0) {
            if (pq.empty()) {
                cout << 0 << "\\n";
            } else {
                cout << pq.top() << "\\n";
                pq.pop();
            }
        } else {
            pq.push(x);
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
        PriorityQueue<Integer> pq = new PriorityQueue<>();  // 최소 힙

        while (n-- > 0) {
            int x = Integer.parseInt(br.readLine());

            if (x == 0) {
                if (pq.isEmpty()) {
                    sb.append(0).append("\\n");
                } else {
                    sb.append(pq.poll()).append("\\n");
                }
            } else {
                pq.add(x);
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_1541": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 잃어버린 괄호 - 그리디
# 첫 번째 -가 나오면 그 이후의 모든 수는 빼야 최소
expr = input()

# - 기준으로 분리
parts = expr.split('-')

result = 0
for i, part in enumerate(parts):
    # 각 파트 내의 + 계산
    total = sum(map(int, part.split('+')))
    if i == 0:
        result += total
    else:
        result -= total

print(result)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <sstream>
using namespace std;

int main() {
    string expr;
    cin >> expr;

    int result = 0;
    bool minus = false;
    string num = "";

    for (int i = 0; i <= expr.length(); i++) {
        if (i == expr.length() || expr[i] == '+' || expr[i] == '-') {
            int val = stoi(num);
            if (minus) {
                result -= val;
            } else {
                result += val;
            }
            num = "";
            if (i < expr.length() && expr[i] == '-') {
                minus = true;
            }
        } else {
            num += expr[i];
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
        String expr = sc.next();

        String[] parts = expr.split("-");

        int result = 0;
        for (int i = 0; i < parts.length; i++) {
            String[] nums = parts[i].split("\\\\+");
            int total = 0;
            for (String num : nums) {
                total += Integer.parseInt(num);
            }
            if (i == 0) {
                result += total;
            } else {
                result -= total;
            }
        }

        System.out.println(result);
    }
}
'''
            }
        ]
    },
    "baekjoon_1182": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 부분수열의 합 - 비트마스킹/백트래킹
import sys
input = sys.stdin.readline

n, s = map(int, input().split())
nums = list(map(int, input().split()))

count = 0

# 비트마스킹으로 모든 부분집합 순회
for mask in range(1, 1 << n):  # 공집합 제외
    total = 0
    for i in range(n):
        if mask & (1 << i):
            total += nums[i]
    if total == s:
        count += 1

print(count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int n, s;
int nums[20];
int count_ans = 0;

void backtrack(int idx, int total) {
    if (idx == n) {
        if (total == s) count_ans++;
        return;
    }

    backtrack(idx + 1, total + nums[idx]);  // 포함
    backtrack(idx + 1, total);  // 미포함
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> s;
    for (int i = 0; i < n; i++) {
        cin >> nums[i];
    }

    backtrack(0, 0);

    // 공집합 제외
    if (s == 0) count_ans--;

    cout << count_ans << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int n, s;
    static int[] nums;
    static int count = 0;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        n = Integer.parseInt(st.nextToken());
        s = Integer.parseInt(st.nextToken());

        nums = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            nums[i] = Integer.parseInt(st.nextToken());
        }

        backtrack(0, 0);

        // 공집합 제외
        if (s == 0) count--;

        System.out.println(count);
    }

    static void backtrack(int idx, int total) {
        if (idx == n) {
            if (total == s) count++;
            return;
        }

        backtrack(idx + 1, total + nums[idx]);  // 포함
        backtrack(idx + 1, total);  // 미포함
    }
}
'''
            }
        ]
    },
    "baekjoon_1676": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 팩토리얼 0의 개수 - 5의 개수 세기
n = int(input())

# 뒤에서부터 0의 개수 = min(2의 개수, 5의 개수) = 5의 개수
# N! 에서 5의 배수, 25의 배수, 125의 배수... 세기
count = 0
power_of_5 = 5

while power_of_5 <= n:
    count += n // power_of_5
    power_of_5 *= 5

print(count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;

    int count = 0;
    int power = 5;

    while (power <= n) {
        count += n / power;
        power *= 5;
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
        int power = 5;

        while (power <= n) {
            count += n / power;
            power *= 5;
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_11866": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 요세푸스 문제 0 - 큐
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
