#!/usr/bin/env python3
"""배치 24: 기본 알고리즘 medium 문제 솔루션 추가"""

import json

new_solutions = {
    "baekjoon_11651": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 좌표 정렬하기 2 - y좌표 기준 정렬
import sys
input = sys.stdin.readline

n = int(input())
points = [tuple(map(int, input().split())) for _ in range(n)]

# y좌표 순, 같으면 x좌표 순
points.sort(key=lambda p: (p[1], p[0]))

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

    // y좌표 순, 같으면 x좌표 순
    sort(points.begin(), points.end(), [](auto& a, auto& b) {
        if (a.second != b.second) return a.second < b.second;
        return a.first < b.first;
    });

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

        // y좌표 순, 같으면 x좌표 순
        Arrays.sort(points, (a, b) -> {
            if (a[1] != b[1]) return a[1] - b[1];
            return a[0] - b[0];
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
    "baekjoon_11660": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 구간 합 구하기 5 - 2D 누적 합
import sys
input = sys.stdin.readline

n, m = map(int, input().split())

# 2D 누적 합 배열
prefix = [[0] * (n + 1) for _ in range(n + 1)]

for i in range(1, n + 1):
    row = list(map(int, input().split()))
    for j in range(1, n + 1):
        prefix[i][j] = row[j-1] + prefix[i-1][j] + prefix[i][j-1] - prefix[i-1][j-1]

result = []
for _ in range(m):
    x1, y1, x2, y2 = map(int, input().split())
    # (x1, y1) ~ (x2, y2) 구간 합
    ans = prefix[x2][y2] - prefix[x1-1][y2] - prefix[x2][y1-1] + prefix[x1-1][y1-1]
    result.append(ans)

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

    long long prefix[1025][1025] = {0};

    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= n; j++) {
            int x;
            cin >> x;
            prefix[i][j] = x + prefix[i-1][j] + prefix[i][j-1] - prefix[i-1][j-1];
        }
    }

    while (m--) {
        int x1, y1, x2, y2;
        cin >> x1 >> y1 >> x2 >> y2;
        long long ans = prefix[x2][y2] - prefix[x1-1][y2] - prefix[x2][y1-1] + prefix[x1-1][y1-1];
        cout << ans << "\\n";
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

        long[][] prefix = new long[n + 1][n + 1];

        for (int i = 1; i <= n; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 1; j <= n; j++) {
                int x = Integer.parseInt(st.nextToken());
                prefix[i][j] = x + prefix[i-1][j] + prefix[i][j-1] - prefix[i-1][j-1];
            }
        }

        while (m-- > 0) {
            st = new StringTokenizer(br.readLine());
            int x1 = Integer.parseInt(st.nextToken());
            int y1 = Integer.parseInt(st.nextToken());
            int x2 = Integer.parseInt(st.nextToken());
            int y2 = Integer.parseInt(st.nextToken());

            long ans = prefix[x2][y2] - prefix[x1-1][y2] - prefix[x2][y1-1] + prefix[x1-1][y1-1];
            sb.append(ans).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_6588": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 골드바흐의 추측 - 에라토스테네스의 체
import sys
input = sys.stdin.readline

MAX = 1000001

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

    found = False
    for a in range(3, n // 2 + 1, 2):  # 홀수 소수만
        if is_prime[a] and is_prime[n - a]:
            print(f"{n} = {a} + {n - a}")
            found = True
            break

    if not found:
        print("Goldbach's conjecture is wrong.")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

const int MAX = 1000001;
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
        bool found = false;
        for (int a = 3; a <= n / 2; a += 2) {
            if (isPrime[a] && isPrime[n - a]) {
                cout << n << " = " << a << " + " << n - a << "\\n";
                found = true;
                break;
            }
        }
        if (!found) {
            cout << "Goldbach's conjecture is wrong.\\n";
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

        int MAX = 1000001;
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
            boolean found = false;
            for (int a = 3; a <= n / 2; a += 2) {
                if (isPrime[a] && isPrime[n - a]) {
                    sb.append(n).append(" = ").append(a).append(" + ").append(n - a).append("\\n");
                    found = true;
                    break;
                }
            }
            if (!found) {
                sb.append("Goldbach's conjecture is wrong.\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_11279": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 최대 힙 - heapq (음수 활용)
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
            result.append(-heapq.heappop(heap))
        else:
            result.append(0)
    else:
        heapq.heappush(heap, -x)

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

    priority_queue<int> pq;  // 최대 힙

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
        PriorityQueue<Integer> pq = new PriorityQueue<>(Collections.reverseOrder());  // 최대 힙

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
    "baekjoon_25206": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 너의 평점은 - 평점 계산
grade_points = {
    'A+': 4.5, 'A0': 4.0, 'B+': 3.5, 'B0': 3.0,
    'C+': 2.5, 'C0': 2.0, 'D+': 1.5, 'D0': 1.0, 'F': 0.0
}

total_credits = 0
total_points = 0

for _ in range(20):
    parts = input().split()
    credit = float(parts[1])
    grade = parts[2]

    if grade == 'P':  # Pass/Fail 과목 제외
        continue

    total_credits += credit
    total_points += credit * grade_points[grade]

if total_credits == 0:
    print(0.0)
else:
    print(total_points / total_credits)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    map<string, double> gradePoints = {
        {"A+", 4.5}, {"A0", 4.0}, {"B+", 3.5}, {"B0", 3.0},
        {"C+", 2.5}, {"C0", 2.0}, {"D+", 1.5}, {"D0", 1.0}, {"F", 0.0}
    };

    double totalCredits = 0;
    double totalPoints = 0;

    for (int i = 0; i < 20; i++) {
        string name, grade;
        double credit;
        cin >> name >> credit >> grade;

        if (grade == "P") continue;

        totalCredits += credit;
        totalPoints += credit * gradePoints[grade];
    }

    if (totalCredits == 0) {
        cout << 0.0 << endl;
    } else {
        cout << fixed;
        cout.precision(6);
        cout << totalPoints / totalCredits << endl;
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

        Map<String, Double> gradePoints = new HashMap<>();
        gradePoints.put("A+", 4.5);
        gradePoints.put("A0", 4.0);
        gradePoints.put("B+", 3.5);
        gradePoints.put("B0", 3.0);
        gradePoints.put("C+", 2.5);
        gradePoints.put("C0", 2.0);
        gradePoints.put("D+", 1.5);
        gradePoints.put("D0", 1.0);
        gradePoints.put("F", 0.0);

        double totalCredits = 0;
        double totalPoints = 0;

        for (int i = 0; i < 20; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String name = st.nextToken();
            double credit = Double.parseDouble(st.nextToken());
            String grade = st.nextToken();

            if (grade.equals("P")) continue;

            totalCredits += credit;
            totalPoints += credit * gradePoints.get(grade);
        }

        if (totalCredits == 0) {
            System.out.println(0.0);
        } else {
            System.out.println(totalPoints / totalCredits);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_10866": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 덱 구현
import sys
from collections import deque
input = sys.stdin.readline

n = int(input())
dq = deque()
result = []

for _ in range(n):
    cmd = input().split()

    if cmd[0] == 'push_front':
        dq.appendleft(int(cmd[1]))
    elif cmd[0] == 'push_back':
        dq.append(int(cmd[1]))
    elif cmd[0] == 'pop_front':
        result.append(dq.popleft() if dq else -1)
    elif cmd[0] == 'pop_back':
        result.append(dq.pop() if dq else -1)
    elif cmd[0] == 'size':
        result.append(len(dq))
    elif cmd[0] == 'empty':
        result.append(0 if dq else 1)
    elif cmd[0] == 'front':
        result.append(dq[0] if dq else -1)
    elif cmd[0] == 'back':
        result.append(dq[-1] if dq else -1)

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

        if (cmd == "push_front") {
            int x;
            cin >> x;
            dq.push_front(x);
        } else if (cmd == "push_back") {
            int x;
            cin >> x;
            dq.push_back(x);
        } else if (cmd == "pop_front") {
            if (dq.empty()) {
                cout << -1 << "\\n";
            } else {
                cout << dq.front() << "\\n";
                dq.pop_front();
            }
        } else if (cmd == "pop_back") {
            if (dq.empty()) {
                cout << -1 << "\\n";
            } else {
                cout << dq.back() << "\\n";
                dq.pop_back();
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
        Deque<Integer> dq = new ArrayDeque<>();

        while (n-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String cmd = st.nextToken();

            if (cmd.equals("push_front")) {
                dq.addFirst(Integer.parseInt(st.nextToken()));
            } else if (cmd.equals("push_back")) {
                dq.addLast(Integer.parseInt(st.nextToken()));
            } else if (cmd.equals("pop_front")) {
                sb.append(dq.isEmpty() ? -1 : dq.pollFirst()).append("\\n");
            } else if (cmd.equals("pop_back")) {
                sb.append(dq.isEmpty() ? -1 : dq.pollLast()).append("\\n");
            } else if (cmd.equals("size")) {
                sb.append(dq.size()).append("\\n");
            } else if (cmd.equals("empty")) {
                sb.append(dq.isEmpty() ? 1 : 0).append("\\n");
            } else if (cmd.equals("front")) {
                sb.append(dq.isEmpty() ? -1 : dq.peekFirst()).append("\\n");
            } else if (cmd.equals("back")) {
                sb.append(dq.isEmpty() ? -1 : dq.peekLast()).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_2563": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 색종이 - 2D 배열
paper = [[False] * 100 for _ in range(100)]

n = int(input())
for _ in range(n):
    x, y = map(int, input().split())
    for i in range(x, x + 10):
        for j in range(y, y + 10):
            paper[i][j] = True

# 검은 영역 넓이 계산
area = sum(sum(row) for row in paper)
print(area)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    bool paper[100][100] = {false};

    int n;
    cin >> n;

    while (n--) {
        int x, y;
        cin >> x >> y;
        for (int i = x; i < x + 10; i++) {
            for (int j = y; j < y + 10; j++) {
                paper[i][j] = true;
            }
        }
    }

    int area = 0;
    for (int i = 0; i < 100; i++) {
        for (int j = 0; j < 100; j++) {
            if (paper[i][j]) area++;
        }
    }

    cout << area << endl;

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

        boolean[][] paper = new boolean[100][100];

        int n = Integer.parseInt(br.readLine());

        for (int k = 0; k < n; k++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());

            for (int i = x; i < x + 10; i++) {
                for (int j = y; j < y + 10; j++) {
                    paper[i][j] = true;
                }
            }
        }

        int area = 0;
        for (int i = 0; i < 100; i++) {
            for (int j = 0; j < 100; j++) {
                if (paper[i][j]) area++;
            }
        }

        System.out.println(area);
    }
}
'''
            }
        ]
    },
    "baekjoon_1966": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 프린터 큐 - 시뮬레이션
from collections import deque
import sys
input = sys.stdin.readline

t = int(input())

for _ in range(t):
    n, m = map(int, input().split())
    priorities = list(map(int, input().split()))

    queue = deque([(i, priorities[i]) for i in range(n)])
    order = 0

    while queue:
        cur = queue.popleft()
        # 더 높은 우선순위가 있는지 확인
        if any(p > cur[1] for _, p in queue):
            queue.append(cur)
        else:
            order += 1
            if cur[0] == m:
                print(order)
                break
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <queue>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int n, m;
        cin >> n >> m;

        queue<pair<int, int>> q;  // (인덱스, 우선순위)
        priority_queue<int> pq;   // 최대 우선순위

        for (int i = 0; i < n; i++) {
            int p;
            cin >> p;
            q.push({i, p});
            pq.push(p);
        }

        int order = 0;

        while (!q.empty()) {
            auto cur = q.front();
            q.pop();

            if (cur.second < pq.top()) {
                q.push(cur);
            } else {
                pq.pop();
                order++;
                if (cur.first == m) {
                    cout << order << "\\n";
                    break;
                }
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

        int t = Integer.parseInt(br.readLine());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int m = Integer.parseInt(st.nextToken());

            Queue<int[]> queue = new LinkedList<>();
            PriorityQueue<Integer> pq = new PriorityQueue<>(Collections.reverseOrder());

            st = new StringTokenizer(br.readLine());
            for (int i = 0; i < n; i++) {
                int p = Integer.parseInt(st.nextToken());
                queue.add(new int[]{i, p});
                pq.add(p);
            }

            int order = 0;

            while (!queue.isEmpty()) {
                int[] cur = queue.poll();

                if (cur[1] < pq.peek()) {
                    queue.add(cur);
                } else {
                    pq.poll();
                    order++;
                    if (cur[0] == m) {
                        sb.append(order).append("\\n");
                        break;
                    }
                }
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_11727": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 2xn 타일링 2 - DP
n = int(input())
MOD = 10007

# dp[i] = dp[i-1] + 2 * dp[i-2]
# (1x2 하나 또는 2x1 두 개 또는 2x2 하나)
if n == 1:
    print(1)
else:
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 3

    for i in range(3, n + 1):
        dp[i] = (dp[i-1] + 2 * dp[i-2]) % MOD

    print(dp[n])
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

const int MOD = 10007;

int main() {
    int n;
    cin >> n;

    int dp[1001];
    dp[1] = 1;
    dp[2] = 3;

    for (int i = 3; i <= n; i++) {
        dp[i] = (dp[i-1] + 2 * dp[i-2]) % MOD;
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
        int MOD = 10007;

        int[] dp = new int[n + 1];
        dp[1] = 1;
        if (n >= 2) dp[2] = 3;

        for (int i = 3; i <= n; i++) {
            dp[i] = (dp[i-1] + 2 * dp[i-2]) % MOD;
        }

        System.out.println(dp[n]);
    }
}
'''
            }
        ]
    },
    "baekjoon_1244": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 스위치 켜고 끄기
import sys
input = sys.stdin.readline

n = int(input())
switches = [0] + list(map(int, input().split()))
m = int(input())

for _ in range(m):
    gender, num = map(int, input().split())

    if gender == 1:  # 남학생: 배수 스위치 토글
        for i in range(num, n + 1, num):
            switches[i] = 1 - switches[i]
    else:  # 여학생: 대칭 구간 토글
        left, right = num, num
        while left > 1 and right < n and switches[left - 1] == switches[right + 1]:
            left -= 1
            right += 1
        for i in range(left, right + 1):
            switches[i] = 1 - switches[i]

# 20개씩 출력
for i in range(1, n + 1):
    print(switches[i], end=' ')
    if i % 20 == 0:
        print()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int switches[101];
    for (int i = 1; i <= n; i++) {
        cin >> switches[i];
    }

    int m;
    cin >> m;

    while (m--) {
        int gender, num;
        cin >> gender >> num;

        if (gender == 1) {  // 남학생
            for (int i = num; i <= n; i += num) {
                switches[i] = 1 - switches[i];
            }
        } else {  // 여학생
            int left = num, right = num;
            while (left > 1 && right < n && switches[left - 1] == switches[right + 1]) {
                left--;
                right++;
            }
            for (int i = left; i <= right; i++) {
                switches[i] = 1 - switches[i];
            }
        }
    }

    for (int i = 1; i <= n; i++) {
        cout << switches[i];
        if (i % 20 == 0 || i == n) {
            cout << "\\n";
        } else {
            cout << " ";
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
        int[] switches = new int[n + 1];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 1; i <= n; i++) {
            switches[i] = Integer.parseInt(st.nextToken());
        }

        int m = Integer.parseInt(br.readLine());

        while (m-- > 0) {
            st = new StringTokenizer(br.readLine());
            int gender = Integer.parseInt(st.nextToken());
            int num = Integer.parseInt(st.nextToken());

            if (gender == 1) {  // 남학생
                for (int i = num; i <= n; i += num) {
                    switches[i] = 1 - switches[i];
                }
            } else {  // 여학생
                int left = num, right = num;
                while (left > 1 && right < n && switches[left - 1] == switches[right + 1]) {
                    left--;
                    right++;
                }
                for (int i = left; i <= right; i++) {
                    switches[i] = 1 - switches[i];
                }
            }
        }

        for (int i = 1; i <= n; i++) {
            sb.append(switches[i]);
            if (i % 20 == 0 || i == n) {
                sb.append("\\n");
            } else {
                sb.append(" ");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_9020": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 골드바흐의 추측 - 두 소수 차이가 가장 작은 것
import sys
input = sys.stdin.readline

MAX = 10001

# 에라토스테네스의 체
is_prime = [True] * MAX
is_prime[0] = is_prime[1] = False

for i in range(2, int(MAX ** 0.5) + 1):
    if is_prime[i]:
        for j in range(i * i, MAX, i):
            is_prime[j] = False

t = int(input())
for _ in range(t):
    n = int(input())

    # 두 소수 차이가 가장 작은 쌍 찾기
    for a in range(n // 2, 1, -1):
        if is_prime[a] and is_prime[n - a]:
            print(a, n - a)
            break
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

const int MAX = 10001;
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

    int t;
    cin >> t;

    while (t--) {
        int n;
        cin >> n;

        for (int a = n / 2; a >= 2; a--) {
            if (isPrime[a] && isPrime[n - a]) {
                cout << a << " " << n - a << "\\n";
                break;
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

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int MAX = 10001;
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

        int t = Integer.parseInt(br.readLine());

        while (t-- > 0) {
            int n = Integer.parseInt(br.readLine());

            for (int a = n / 2; a >= 2; a--) {
                if (isPrime[a] && isPrime[n - a]) {
                    sb.append(a).append(" ").append(n - a).append("\\n");
                    break;
                }
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_9465": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 스티커 - DP
import sys
input = sys.stdin.readline

t = int(input())

for _ in range(t):
    n = int(input())
    stickers = [list(map(int, input().split())) for _ in range(2)]

    if n == 1:
        print(max(stickers[0][0], stickers[1][0]))
        continue

    # dp[i][j] = j열까지 고려했을 때 최대 점수 (i: 0=위, 1=아래, 2=안뗌)
    dp = [[0] * n for _ in range(2)]
    dp[0][0] = stickers[0][0]
    dp[1][0] = stickers[1][0]

    for j in range(1, n):
        dp[0][j] = max(dp[1][j-1], dp[1][j-2] if j >= 2 else 0, dp[0][j-2] if j >= 2 else 0) + stickers[0][j]
        dp[1][j] = max(dp[0][j-1], dp[0][j-2] if j >= 2 else 0, dp[1][j-2] if j >= 2 else 0) + stickers[1][j]

    print(max(dp[0][n-1], dp[1][n-1]))
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

    int t;
    cin >> t;

    while (t--) {
        int n;
        cin >> n;

        int stickers[2][100001];
        int dp[2][100001];

        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < n; j++) {
                cin >> stickers[i][j];
            }
        }

        dp[0][0] = stickers[0][0];
        dp[1][0] = stickers[1][0];

        if (n >= 2) {
            dp[0][1] = dp[1][0] + stickers[0][1];
            dp[1][1] = dp[0][0] + stickers[1][1];
        }

        for (int j = 2; j < n; j++) {
            dp[0][j] = max(dp[1][j-1], dp[1][j-2]) + stickers[0][j];
            dp[1][j] = max(dp[0][j-1], dp[0][j-2]) + stickers[1][j];
        }

        cout << max(dp[0][n-1], dp[1][n-1]) << "\\n";
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
            int n = Integer.parseInt(br.readLine());

            int[][] stickers = new int[2][n];
            int[][] dp = new int[2][n];

            for (int i = 0; i < 2; i++) {
                StringTokenizer st = new StringTokenizer(br.readLine());
                for (int j = 0; j < n; j++) {
                    stickers[i][j] = Integer.parseInt(st.nextToken());
                }
            }

            dp[0][0] = stickers[0][0];
            dp[1][0] = stickers[1][0];

            if (n >= 2) {
                dp[0][1] = dp[1][0] + stickers[0][1];
                dp[1][1] = dp[0][0] + stickers[1][1];
            }

            for (int j = 2; j < n; j++) {
                dp[0][j] = Math.max(dp[1][j-1], dp[1][j-2]) + stickers[0][j];
                dp[1][j] = Math.max(dp[0][j-1], dp[0][j-2]) + stickers[1][j];
            }

            sb.append(Math.max(dp[0][n-1], dp[1][n-1])).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_15651": {
        "solutions": [
            {
                "language": "python",
                "code": '''# N과 M (3) - 중복 허용 수열
import sys

def backtrack(arr, n, m):
    if len(arr) == m:
        print(' '.join(map(str, arr)))
        return

    for i in range(1, n + 1):
        arr.append(i)
        backtrack(arr, n, m)
        arr.pop()

n, m = map(int, input().split())
backtrack([], n, m)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
using namespace std;

int n, m;
vector<int> arr;

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
        arr.push_back(i);
        backtrack();
        arr.pop_back();
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
    static StringBuilder sb = new StringBuilder();

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        n = Integer.parseInt(st.nextToken());
        m = Integer.parseInt(st.nextToken());

        arr = new int[m];

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
            arr[depth] = i;
            backtrack(depth + 1);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_3273": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 두 수의 합 - 투 포인터
import sys
input = sys.stdin.readline

n = int(input())
arr = list(map(int, input().split()))
x = int(input())

arr.sort()

left, right = 0, n - 1
count = 0

while left < right:
    total = arr[left] + arr[right]
    if total == x:
        count += 1
        left += 1
        right -= 1
    elif total < x:
        left += 1
    else:
        right -= 1

print(count)
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

    int arr[100000];
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    int x;
    cin >> x;

    sort(arr, arr + n);

    int left = 0, right = n - 1;
    int count = 0;

    while (left < right) {
        int total = arr[left] + arr[right];
        if (total == x) {
            count++;
            left++;
            right--;
        } else if (total < x) {
            left++;
        } else {
            right--;
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
        int[] arr = new int[n];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        int x = Integer.parseInt(br.readLine());

        Arrays.sort(arr);

        int left = 0, right = n - 1;
        int count = 0;

        while (left < right) {
            int total = arr[left] + arr[right];
            if (total == x) {
                count++;
                left++;
                right--;
            } else if (total < x) {
                left++;
            } else {
                right--;
            }
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_18111": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 마인크래프트 - 브루트포스
import sys
input = sys.stdin.readline

n, m, b = map(int, input().split())
ground = []
for _ in range(n):
    ground.extend(map(int, input().split()))

min_height = min(ground)
max_height = max(ground)

min_time = float('inf')
result_height = 0

for h in range(min_height, max_height + 1):
    remove = 0
    add = 0

    for block in ground:
        if block > h:
            remove += block - h
        else:
            add += h - block

    # 블록이 충분한지 확인
    if b + remove >= add:
        time = 2 * remove + add
        if time < min_time or (time == min_time and h > result_height):
            min_time = time
            result_height = h

print(min_time, result_height)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, b;
    cin >> n >> m >> b;

    vector<int> ground(n * m);
    int minH = 256, maxH = 0;

    for (int i = 0; i < n * m; i++) {
        cin >> ground[i];
        minH = min(minH, ground[i]);
        maxH = max(maxH, ground[i]);
    }

    int minTime = 1e9;
    int resultHeight = 0;

    for (int h = minH; h <= maxH; h++) {
        int remove = 0, add = 0;

        for (int block : ground) {
            if (block > h) {
                remove += block - h;
            } else {
                add += h - block;
            }
        }

        if (b + remove >= add) {
            int time = 2 * remove + add;
            if (time < minTime || (time == minTime && h > resultHeight)) {
                minTime = time;
                resultHeight = h;
            }
        }
    }

    cout << minTime << " " << resultHeight << endl;

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
        int b = Integer.parseInt(st.nextToken());

        int[] ground = new int[n * m];
        int minH = 256, maxH = 0;
        int idx = 0;

        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < m; j++) {
                ground[idx] = Integer.parseInt(st.nextToken());
                minH = Math.min(minH, ground[idx]);
                maxH = Math.max(maxH, ground[idx]);
                idx++;
            }
        }

        int minTime = Integer.MAX_VALUE;
        int resultHeight = 0;

        for (int h = minH; h <= maxH; h++) {
            int remove = 0, add = 0;

            for (int block : ground) {
                if (block > h) {
                    remove += block - h;
                } else {
                    add += h - block;
                }
            }

            if (b + remove >= add) {
                int time = 2 * remove + add;
                if (time < minTime || (time == minTime && h > resultHeight)) {
                    minTime = time;
                    resultHeight = h;
                }
            }
        }

        System.out.println(minTime + " " + resultHeight);
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
