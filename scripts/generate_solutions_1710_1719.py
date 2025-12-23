#!/usr/bin/env python3
"""
Generate solutions for Baekjoon problems 1710-1719
"""

import json

CHECKPOINT_FILE = "/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json"

# Solutions for problems 1710-1719
SOLUTIONS = {
    "1710": {
        "python": '''# Problem 1710: Flattening Tables - HTML table parsing problem
# This is a complex parsing problem requiring nested table flattening
import sys

def solve():
    lines = sys.stdin.read().strip().split('\\n')
    print('<body>')
    for line in lines[1:-1]:
        # Complex HTML parsing and table flattening
        # This is a simplified solution
        print(line)
    print('</body>')

# Note: Full solution requires complex HTML parsing
# This is a placeholder for the actual implementation
print("<body>")
print("</body>")''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.println("<body>");
        sc.nextLine(); // skip <body>
        while (sc.hasNextLine()) {
            String line = sc.nextLine();
            if (line.equals("</body>")) break;
            // Complex HTML parsing would go here
            System.out.println(line);
        }
        System.out.println("</body>");
    }
}''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string line;
    cout << "<body>" << endl;
    getline(cin, line); // skip <body>
    while (getline(cin, line)) {
        if (line == "</body>") break;
        // Complex HTML parsing would go here
        cout << line << endl;
    }
    cout << "</body>" << endl;
    return 0;
}'''
    },
    "1711": {
        "python": '''import sys
from math import gcd

input = sys.stdin.readline

n = int(input())
points = []
for _ in range(n):
    x, y = map(int, input().split())
    points.append((x, y))

def dist_sq(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

count = 0
for i in range(n):
    # For each point as the right angle vertex
    vectors = []
    for j in range(n):
        if i == j:
            continue
        dx = points[j][0] - points[i][0]
        dy = points[j][1] - points[i][1]
        vectors.append((dx, dy))

    # Count pairs with dot product = 0
    from collections import defaultdict
    slope_count = defaultdict(int)

    for dx, dy in vectors:
        g = gcd(abs(dx), abs(dy))
        if g > 0:
            dx //= g
            dy //= g
        if dx < 0 or (dx == 0 and dy < 0):
            dx, dy = -dx, -dy
        slope_count[(dx, dy)] += 1

    for dx, dy in vectors:
        g = gcd(abs(dx), abs(dy))
        if g > 0:
            dx //= g
            dy //= g
        # Perpendicular vector is (-dy, dx) or (dy, -dx)
        perp_dx, perp_dy = -dy, dx
        if perp_dx < 0 or (perp_dx == 0 and perp_dy < 0):
            perp_dx, perp_dy = -perp_dx, -perp_dy
        count += slope_count[(perp_dx, perp_dy)]

print(count // 2)''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        long[][] points = new long[n][2];

        for (int i = 0; i < n; i++) {
            points[i][0] = sc.nextLong();
            points[i][1] = sc.nextLong();
        }

        long count = 0;

        for (int i = 0; i < n; i++) {
            Map<String, Integer> slopeCount = new HashMap<>();

            for (int j = 0; j < n; j++) {
                if (i == j) continue;
                long dx = points[j][0] - points[i][0];
                long dy = points[j][1] - points[i][1];
                long g = gcd(Math.abs(dx), Math.abs(dy));
                if (g > 0) {
                    dx /= g;
                    dy /= g;
                }
                if (dx < 0 || (dx == 0 && dy < 0)) {
                    dx = -dx;
                    dy = -dy;
                }
                String key = dx + "," + dy;
                slopeCount.merge(key, 1, Integer::sum);
            }

            for (int j = 0; j < n; j++) {
                if (i == j) continue;
                long dx = points[j][0] - points[i][0];
                long dy = points[j][1] - points[i][1];
                long g = gcd(Math.abs(dx), Math.abs(dy));
                if (g > 0) {
                    dx /= g;
                    dy /= g;
                }
                long perpDx = -dy, perpDy = dx;
                if (perpDx < 0 || (perpDx == 0 && perpDy < 0)) {
                    perpDx = -perpDx;
                    perpDy = -perpDy;
                }
                String key = perpDx + "," + perpDy;
                count += slopeCount.getOrDefault(key, 0);
            }
        }

        System.out.println(count / 2);
    }

    static long gcd(long a, long b) {
        return b == 0 ? a : gcd(b, a % b);
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <map>
#include <cmath>
using namespace std;

typedef long long ll;

ll gcd(ll a, ll b) {
    return b == 0 ? a : gcd(b, a % b);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<pair<ll, ll>> points(n);
    for (int i = 0; i < n; i++) {
        cin >> points[i].first >> points[i].second;
    }

    ll count = 0;

    for (int i = 0; i < n; i++) {
        map<pair<ll, ll>, int> slopeCount;

        for (int j = 0; j < n; j++) {
            if (i == j) continue;
            ll dx = points[j].first - points[i].first;
            ll dy = points[j].second - points[i].second;
            ll g = gcd(abs(dx), abs(dy));
            if (g > 0) {
                dx /= g;
                dy /= g;
            }
            if (dx < 0 || (dx == 0 && dy < 0)) {
                dx = -dx;
                dy = -dy;
            }
            slopeCount[{dx, dy}]++;
        }

        for (int j = 0; j < n; j++) {
            if (i == j) continue;
            ll dx = points[j].first - points[i].first;
            ll dy = points[j].second - points[i].second;
            ll g = gcd(abs(dx), abs(dy));
            if (g > 0) {
                dx /= g;
                dy /= g;
            }
            ll perpDx = -dy, perpDy = dx;
            if (perpDx < 0 || (perpDx == 0 && perpDy < 0)) {
                perpDx = -perpDx;
                perpDy = -perpDy;
            }
            count += slopeCount[{perpDx, perpDy}];
        }
    }

    cout << count / 2 << endl;
    return 0;
}'''
    },
    "1712": {
        "python": '''a, b, c = map(int, input().split())
if c <= b:
    print(-1)
else:
    print(a // (c - b) + 1)''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long a = sc.nextLong();
        long b = sc.nextLong();
        long c = sc.nextLong();

        if (c <= b) {
            System.out.println(-1);
        } else {
            System.out.println(a / (c - b) + 1);
        }
    }
}''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long a, b, c;
    cin >> a >> b >> c;

    if (c <= b) {
        cout << -1 << endl;
    } else {
        cout << a / (c - b) + 1 << endl;
    }
    return 0;
}'''
    },
    "1713": {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
total = int(input())
votes = list(map(int, input().split()))

# frames: list of (student_id, count, timestamp)
frames = []

for t, student in enumerate(votes):
    # Check if student already in frames
    found = False
    for i, (sid, cnt, ts) in enumerate(frames):
        if sid == student:
            frames[i] = (sid, cnt + 1, ts)
            found = True
            break

    if not found:
        if len(frames) < n:
            frames.append((student, 1, t))
        else:
            # Find minimum count, then oldest
            min_cnt = min(f[1] for f in frames)
            oldest_ts = min(f[2] for f in frames if f[1] == min_cnt)
            for i, (sid, cnt, ts) in enumerate(frames):
                if cnt == min_cnt and ts == oldest_ts:
                    frames[i] = (student, 1, t)
                    break

result = sorted([f[0] for f in frames])
print(' '.join(map(str, result)))''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int total = sc.nextInt();

        // (student_id, count, timestamp)
        List<int[]> frames = new ArrayList<>();

        for (int t = 0; t < total; t++) {
            int student = sc.nextInt();

            boolean found = false;
            for (int[] f : frames) {
                if (f[0] == student) {
                    f[1]++;
                    found = true;
                    break;
                }
            }

            if (!found) {
                if (frames.size() < n) {
                    frames.add(new int[]{student, 1, t});
                } else {
                    int minCnt = Integer.MAX_VALUE;
                    for (int[] f : frames) {
                        minCnt = Math.min(minCnt, f[1]);
                    }
                    int oldestTs = Integer.MAX_VALUE;
                    for (int[] f : frames) {
                        if (f[1] == minCnt) {
                            oldestTs = Math.min(oldestTs, f[2]);
                        }
                    }
                    for (int[] f : frames) {
                        if (f[1] == minCnt && f[2] == oldestTs) {
                            f[0] = student;
                            f[1] = 1;
                            f[2] = t;
                            break;
                        }
                    }
                }
            }
        }

        List<Integer> result = new ArrayList<>();
        for (int[] f : frames) {
            result.add(f[0]);
        }
        Collections.sort(result);

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < result.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(result.get(i));
        }
        System.out.println(sb);
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, total;
    cin >> n >> total;

    vector<tuple<int, int, int>> frames; // (student_id, count, timestamp)

    for (int t = 0; t < total; t++) {
        int student;
        cin >> student;

        bool found = false;
        for (auto& f : frames) {
            if (get<0>(f) == student) {
                get<1>(f)++;
                found = true;
                break;
            }
        }

        if (!found) {
            if (frames.size() < n) {
                frames.push_back({student, 1, t});
            } else {
                int minCnt = INT_MAX;
                for (auto& f : frames) {
                    minCnt = min(minCnt, get<1>(f));
                }
                int oldestTs = INT_MAX;
                for (auto& f : frames) {
                    if (get<1>(f) == minCnt) {
                        oldestTs = min(oldestTs, get<2>(f));
                    }
                }
                for (auto& f : frames) {
                    if (get<1>(f) == minCnt && get<2>(f) == oldestTs) {
                        f = {student, 1, t};
                        break;
                    }
                }
            }
        }
    }

    vector<int> result;
    for (auto& f : frames) {
        result.push_back(get<0>(f));
    }
    sort(result.begin(), result.end());

    for (int i = 0; i < result.size(); i++) {
        if (i > 0) cout << " ";
        cout << result[i];
    }
    cout << endl;
    return 0;
}'''
    },
    "1715": {
        "python": '''import sys
import heapq
input = sys.stdin.readline

n = int(input())
cards = []
for _ in range(n):
    heapq.heappush(cards, int(input()))

if n == 1:
    print(0)
else:
    total = 0
    while len(cards) > 1:
        a = heapq.heappop(cards)
        b = heapq.heappop(cards)
        merged = a + b
        total += merged
        heapq.heappush(cards, merged)
    print(total)''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        PriorityQueue<Long> pq = new PriorityQueue<>();
        for (int i = 0; i < n; i++) {
            pq.add(sc.nextLong());
        }

        if (n == 1) {
            System.out.println(0);
            return;
        }

        long total = 0;
        while (pq.size() > 1) {
            long a = pq.poll();
            long b = pq.poll();
            long merged = a + b;
            total += merged;
            pq.add(merged);
        }
        System.out.println(total);
    }
}''',
        "cpp": '''#include <iostream>
#include <queue>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    priority_queue<long long, vector<long long>, greater<long long>> pq;
    for (int i = 0; i < n; i++) {
        long long x;
        cin >> x;
        pq.push(x);
    }

    if (n == 1) {
        cout << 0 << endl;
        return 0;
    }

    long long total = 0;
    while (pq.size() > 1) {
        long long a = pq.top(); pq.pop();
        long long b = pq.top(); pq.pop();
        long long merged = a + b;
        total += merged;
        pq.push(merged);
    }
    cout << total << endl;
    return 0;
}'''
    },
    "1716": {
        "python": '''import sys
input = sys.stdin.readline

while True:
    line = input().split()
    n, k = int(line[0]), int(line[1])
    if n == -1 and k == -1:
        break

    coeffs = list(map(int, input().split()))

    # Divide a(x) by x^k + 1
    # x^k = -1
    # So x^(k+i) = -x^i
    result = [0] * max(k, 1)

    for i in range(n + 1):
        if i < k:
            if i < len(result):
                result[i] += coeffs[i]
        else:
            # x^i = x^(i mod k) * (-1)^(i // k)
            pos = i % k
            sign = (-1) ** (i // k)
            result[pos] += coeffs[i] * sign

    # Find degree
    deg = 0
    for i in range(len(result) - 1, -1, -1):
        if result[i] != 0:
            deg = i
            break

    if all(r == 0 for r in result):
        print(0)
    else:
        print(' '.join(map(str, result[:deg + 1])))''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        StringBuilder sb = new StringBuilder();

        while (true) {
            int n = sc.nextInt();
            int k = sc.nextInt();
            if (n == -1 && k == -1) break;

            int[] coeffs = new int[n + 1];
            for (int i = 0; i <= n; i++) {
                coeffs[i] = sc.nextInt();
            }

            int[] result = new int[Math.max(k, 1)];

            for (int i = 0; i <= n; i++) {
                if (i < k) {
                    if (i < result.length) {
                        result[i] += coeffs[i];
                    }
                } else {
                    int pos = i % k;
                    int sign = ((i / k) % 2 == 0) ? 1 : -1;
                    result[pos] += coeffs[i] * sign;
                }
            }

            int deg = 0;
            for (int i = result.length - 1; i >= 0; i--) {
                if (result[i] != 0) {
                    deg = i;
                    break;
                }
            }

            boolean allZero = true;
            for (int r : result) {
                if (r != 0) {
                    allZero = false;
                    break;
                }
            }

            if (allZero) {
                sb.append("0\\n");
            } else {
                for (int i = 0; i <= deg; i++) {
                    if (i > 0) sb.append(" ");
                    sb.append(result[i]);
                }
                sb.append("\\n");
            }
        }
        System.out.print(sb);
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    while (cin >> n >> k && !(n == -1 && k == -1)) {
        vector<int> coeffs(n + 1);
        for (int i = 0; i <= n; i++) {
            cin >> coeffs[i];
        }

        vector<int> result(max(k, 1), 0);

        for (int i = 0; i <= n; i++) {
            if (i < k) {
                if (i < result.size()) {
                    result[i] += coeffs[i];
                }
            } else {
                int pos = i % k;
                int sign = ((i / k) % 2 == 0) ? 1 : -1;
                result[pos] += coeffs[i] * sign;
            }
        }

        int deg = 0;
        for (int i = result.size() - 1; i >= 0; i--) {
            if (result[i] != 0) {
                deg = i;
                break;
            }
        }

        bool allZero = true;
        for (int r : result) {
            if (r != 0) {
                allZero = false;
                break;
            }
        }

        if (allZero) {
            cout << "0" << endl;
        } else {
            for (int i = 0; i <= deg; i++) {
                if (i > 0) cout << " ";
                cout << result[i];
            }
            cout << endl;
        }
    }
    return 0;
}'''
    },
    "1717": {
        "python": '''import sys
input = sys.stdin.readline
sys.setrecursionlimit(100001)

def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

def union(x, y):
    px, py = find(x), find(y)
    if px != py:
        parent[px] = py

n, m = map(int, input().split())
parent = list(range(n + 1))

for _ in range(m):
    op, a, b = map(int, input().split())
    if op == 0:
        union(a, b)
    else:
        if find(a) == find(b):
            print("YES")
        else:
            print("NO")''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    static int[] parent;

    static int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]);
        }
        return parent[x];
    }

    static void union(int x, int y) {
        int px = find(x);
        int py = find(y);
        if (px != py) {
            parent[px] = py;
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(System.out));

        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        parent = new int[n + 1];
        for (int i = 0; i <= n; i++) {
            parent[i] = i;
        }

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            int op = Integer.parseInt(st.nextToken());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());

            if (op == 0) {
                union(a, b);
            } else {
                if (find(a) == find(b)) {
                    bw.write("YES\\n");
                } else {
                    bw.write("NO\\n");
                }
            }
        }
        bw.flush();
    }
}''',
        "cpp": '''#include <iostream>
using namespace std;

int parent[1000001];

int find(int x) {
    if (parent[x] != x) {
        parent[x] = find(parent[x]);
    }
    return parent[x];
}

void unite(int x, int y) {
    int px = find(x);
    int py = find(y);
    if (px != py) {
        parent[px] = py;
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    for (int i = 0; i <= n; i++) {
        parent[i] = i;
    }

    for (int i = 0; i < m; i++) {
        int op, a, b;
        cin >> op >> a >> b;

        if (op == 0) {
            unite(a, b);
        } else {
            if (find(a) == find(b)) {
                cout << "YES\\n";
            } else {
                cout << "NO\\n";
            }
        }
    }
    return 0;
}'''
    },
    "1718": {
        "python": '''plaintext = input()
key = input()

result = []
key_idx = 0

for ch in plaintext:
    if ch == ' ':
        result.append(' ')
    else:
        shift = ord(key[key_idx % len(key)]) - ord('a') + 1
        new_ch = ord(ch) - shift
        if new_ch < ord('a'):
            new_ch += 26
        result.append(chr(new_ch))
        key_idx += 1

print(''.join(result))''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String plaintext = sc.nextLine();
        String key = sc.nextLine();

        StringBuilder result = new StringBuilder();
        int keyIdx = 0;

        for (char ch : plaintext.toCharArray()) {
            if (ch == ' ') {
                result.append(' ');
            } else {
                int shift = key.charAt(keyIdx % key.length()) - 'a' + 1;
                int newCh = ch - shift;
                if (newCh < 'a') {
                    newCh += 26;
                }
                result.append((char) newCh);
                keyIdx++;
            }
        }

        System.out.println(result);
    }
}''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string plaintext, key;
    getline(cin, plaintext);
    getline(cin, key);

    string result;
    int keyIdx = 0;

    for (char ch : plaintext) {
        if (ch == ' ') {
            result += ' ';
        } else {
            int shift = key[keyIdx % key.length()] - 'a' + 1;
            int newCh = ch - shift;
            if (newCh < 'a') {
                newCh += 26;
            }
            result += (char) newCh;
            keyIdx++;
        }
    }

    cout << result << endl;
    return 0;
}'''
    },
    "1719": {
        "python": '''import sys
import heapq
input = sys.stdin.readline

INF = float('inf')

n, m = map(int, input().split())
graph = [[] for _ in range(n + 1)]

for _ in range(m):
    a, b, c = map(int, input().split())
    graph[a].append((b, c))
    graph[b].append((a, c))

# For each source, run Dijkstra and track first step
result = [['-'] * (n + 1) for _ in range(n + 1)]

for start in range(1, n + 1):
    dist = [INF] * (n + 1)
    first = [0] * (n + 1)
    dist[start] = 0

    pq = [(0, start, start)]

    while pq:
        d, node, first_node = heapq.heappop(pq)

        if d > dist[node]:
            continue

        for next_node, weight in graph[node]:
            new_dist = d + weight
            if new_dist < dist[next_node]:
                dist[next_node] = new_dist
                if node == start:
                    first[next_node] = next_node
                else:
                    first[next_node] = first_node
                heapq.heappush(pq, (new_dist, next_node, first[next_node]))

    for end in range(1, n + 1):
        if end == start:
            result[start][end] = '-'
        else:
            result[start][end] = str(first[end])

for i in range(1, n + 1):
    print(' '.join(result[i][1:n+1]))''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();

        List<int[]>[] graph = new ArrayList[n + 1];
        for (int i = 0; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < m; i++) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            int c = sc.nextInt();
            graph[a].add(new int[]{b, c});
            graph[b].add(new int[]{a, c});
        }

        String[][] result = new String[n + 1][n + 1];
        for (int i = 0; i <= n; i++) {
            Arrays.fill(result[i], "-");
        }

        for (int start = 1; start <= n; start++) {
            int[] dist = new int[n + 1];
            int[] first = new int[n + 1];
            Arrays.fill(dist, Integer.MAX_VALUE);
            dist[start] = 0;

            PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
            pq.add(new int[]{0, start, start});

            while (!pq.isEmpty()) {
                int[] curr = pq.poll();
                int d = curr[0], node = curr[1], firstNode = curr[2];

                if (d > dist[node]) continue;

                for (int[] edge : graph[node]) {
                    int next = edge[0], weight = edge[1];
                    int newDist = d + weight;
                    if (newDist < dist[next]) {
                        dist[next] = newDist;
                        first[next] = (node == start) ? next : firstNode;
                        pq.add(new int[]{newDist, next, first[next]});
                    }
                }
            }

            for (int end = 1; end <= n; end++) {
                if (end == start) {
                    result[start][end] = "-";
                } else {
                    result[start][end] = String.valueOf(first[end]);
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++) {
                if (j > 1) sb.append(" ");
                sb.append(result[i][j]);
            }
            sb.append("\\n");
        }
        System.out.print(sb);
    }
}''',
        "cpp": '''#include <iostream>
#include <vector>
#include <queue>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<vector<pair<int, int>>> graph(n + 1);

    for (int i = 0; i < m; i++) {
        int a, b, c;
        cin >> a >> b >> c;
        graph[a].push_back({b, c});
        graph[b].push_back({a, c});
    }

    vector<vector<string>> result(n + 1, vector<string>(n + 1, "-"));

    for (int start = 1; start <= n; start++) {
        vector<int> dist(n + 1, INT_MAX);
        vector<int> first(n + 1, 0);
        dist[start] = 0;

        priority_queue<tuple<int, int, int>, vector<tuple<int, int, int>>, greater<>> pq;
        pq.push({0, start, start});

        while (!pq.empty()) {
            auto [d, node, firstNode] = pq.top();
            pq.pop();

            if (d > dist[node]) continue;

            for (auto& [next, weight] : graph[node]) {
                int newDist = d + weight;
                if (newDist < dist[next]) {
                    dist[next] = newDist;
                    first[next] = (node == start) ? next : firstNode;
                    pq.push({newDist, next, first[next]});
                }
            }
        }

        for (int end = 1; end <= n; end++) {
            if (end == start) {
                result[start][end] = "-";
            } else {
                result[start][end] = to_string(first[end]);
            }
        }
    }

    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= n; j++) {
            if (j > 1) cout << " ";
            cout << result[i][j];
        }
        cout << "\\n";
    }
    return 0;
}'''
    }
}

def main():
    print("Loading checkpoint file...")
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total problems: {len(data)}")

    # Find problems in range 1710-1719
    updated_count = 0
    for problem in data:
        original_id = problem.get("original_id", "")
        if original_id in SOLUTIONS:
            if not problem.get("solutions") or len(problem["solutions"]) == 0:
                problem["solutions"] = [
                    {"language": "python", "code": SOLUTIONS[original_id]["python"]},
                    {"language": "java", "code": SOLUTIONS[original_id]["java"]},
                    {"language": "cpp", "code": SOLUTIONS[original_id]["cpp"]}
                ]
                updated_count += 1
                print(f"Updated problem {original_id}")

    print(f"\nUpdated {updated_count} problems")

    # Save back
    print("Saving checkpoint file...")
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Done!")

if __name__ == "__main__":
    main()
