#!/usr/bin/env python3
"""
20개 Medium 문제 솔루션 추가 스크립트 (offset 70-90)
문제 ID: 1680, 28138, 2817, 2597, 1951, 26595, 21737, 11278, 1639, 27932,
        25793, 10424, 31460, 27165, 15979, 14911, 3005, 16951, 28066, 28086
"""
import json

# 파일 읽기
with open('data/baekjoon/baek_medium.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 20개 문제에 대한 솔루션
new_solutions = {
    "1680": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 쓰레기 수거 문제 - 뒤에서부터 그리디
t = int(input())
for _ in range(t):
    w, n = map(int, input().split())
    bins = []
    for _ in range(n):
        x, c = map(int, input().split())
        bins.append((x, c))

    total_dist = 0
    current_load = 0
    farthest = 0

    # 뒤에서부터 처리
    for i in range(n - 1, -1, -1):
        x, c = bins[i]
        while c > 0:
            if current_load == 0:
                farthest = x
            take = min(c, w - current_load)
            current_load += take
            c -= take
            if current_load == w:
                total_dist += 2 * farthest
                current_load = 0

    if current_load > 0:
        total_dist += 2 * farthest

    print(total_dist)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 쓰레기 수거 - 뒤에서부터 그리디
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());
        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int w = Integer.parseInt(st.nextToken());
            int n = Integer.parseInt(st.nextToken());

            int[][] bins = new int[n][2];
            for (int i = 0; i < n; i++) {
                st = new StringTokenizer(br.readLine());
                bins[i][0] = Integer.parseInt(st.nextToken());
                bins[i][1] = Integer.parseInt(st.nextToken());
            }

            long totalDist = 0;
            int currentLoad = 0, farthest = 0;

            for (int i = n - 1; i >= 0; i--) {
                int x = bins[i][0], c = bins[i][1];
                while (c > 0) {
                    if (currentLoad == 0) farthest = x;
                    int take = Math.min(c, w - currentLoad);
                    currentLoad += take;
                    c -= take;
                    if (currentLoad == w) {
                        totalDist += 2L * farthest;
                        currentLoad = 0;
                    }
                }
            }
            if (currentLoad > 0) totalDist += 2L * farthest;
            sb.append(totalDist).append("\\n");
        }
        System.out.print(sb);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
using namespace std;

// 쓰레기 수거 - 뒤에서부터 그리디
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int w, n;
        cin >> w >> n;

        vector<pair<int, int>> bins(n);
        for (int i = 0; i < n; i++) {
            cin >> bins[i].first >> bins[i].second;
        }

        long long totalDist = 0;
        int currentLoad = 0, farthest = 0;

        for (int i = n - 1; i >= 0; i--) {
            int x = bins[i].first, c = bins[i].second;
            while (c > 0) {
                if (currentLoad == 0) farthest = x;
                int take = min(c, w - currentLoad);
                currentLoad += take;
                c -= take;
                if (currentLoad == w) {
                    totalDist += 2LL * farthest;
                    currentLoad = 0;
                }
            }
        }
        if (currentLoad > 0) totalDist += 2LL * farthest;
        cout << totalDist << "\\n";
    }
    return 0;
}
"""
            }
        ]
    },
    "28138": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 재밌는 나머지 연산 - 약수 찾기
a, b = map(int, input().split())

# a % x = b 이면 (a - b) % x = 0, x > b
diff = a - b
count = 0

i = 1
while i * i <= diff:
    if diff % i == 0:
        if i > b:
            count += 1
        if i != diff // i and diff // i > b:
            count += 1
    i += 1

print(count)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 재밌는 나머지 연산 - 약수 찾기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long a = Long.parseLong(st.nextToken());
        long b = Long.parseLong(st.nextToken());

        long diff = a - b;
        long count = 0;

        for (long i = 1; i * i <= diff; i++) {
            if (diff % i == 0) {
                if (i > b) count++;
                if (i != diff / i && diff / i > b) count++;
            }
        }
        System.out.println(count);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
using namespace std;

// 재밌는 나머지 연산 - 약수 찾기
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long a, b;
    cin >> a >> b;

    long long diff = a - b;
    long long count = 0;

    for (long long i = 1; i * i <= diff; i++) {
        if (diff % i == 0) {
            if (i > b) count++;
            if (i != diff / i && diff / i > b) count++;
        }
    }
    cout << count << endl;
    return 0;
}
"""
            }
        ]
    },
    "2817": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# ALPS식 투표 - 돈트 방식
x = int(input())
n = int(input())

candidates = []
for _ in range(n):
    parts = input().split()
    name = parts[0]
    votes = int(parts[1])
    if votes * 20 >= x:  # 5% 이상
        candidates.append([name, votes])

scores = []
for name, votes in candidates:
    for div in range(1, 15):
        scores.append((votes / div, name))

scores.sort(reverse=True)

result = {}
for name, _ in candidates:
    result[name] = 0

for i in range(14):
    if i < len(scores):
        result[scores[i][1]] += 1

for name in sorted(result.keys()):
    print(f"{name} {result[name]}")
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// ALPS식 투표 - 돈트 방식
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int x = Integer.parseInt(br.readLine().trim());
        int n = Integer.parseInt(br.readLine().trim());

        Map<String, Integer> votes = new TreeMap<>();
        List<double[]> scores = new ArrayList<>();
        List<String> names = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String name = st.nextToken();
            int vote = Integer.parseInt(st.nextToken());

            if (vote * 20 >= x) {
                votes.put(name, vote);
                names.add(name);
                for (int div = 1; div <= 14; div++) {
                    scores.add(new double[]{(double) vote / div, names.size() - 1});
                }
            }
        }

        scores.sort((a, b) -> Double.compare(b[0], a[0]));

        Map<String, Integer> result = new TreeMap<>();
        for (String name : names) result.put(name, 0);

        for (int i = 0; i < Math.min(14, scores.size()); i++) {
            String name = names.get((int) scores.get(i)[1]);
            result.put(name, result.get(name) + 1);
        }

        for (String name : result.keySet()) {
            System.out.println(name + " " + result.get(name));
        }
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
using namespace std;

// ALPS식 투표 - 돈트 방식
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int x, n;
    cin >> x >> n;

    map<string, int> result;
    vector<pair<double, string>> scores;

    for (int i = 0; i < n; i++) {
        string name;
        int vote;
        cin >> name >> vote;

        if (vote * 20 >= x) {
            result[name] = 0;
            for (int div = 1; div <= 14; div++) {
                scores.push_back({(double)vote / div, name});
            }
        }
    }

    sort(scores.begin(), scores.end(), [](auto& a, auto& b) {
        return a.first > b.first;
    });

    for (int i = 0; i < min(14, (int)scores.size()); i++) {
        result[scores[i].second]++;
    }

    for (auto& p : result) {
        cout << p.first << " " << p.second << "\\n";
    }
    return 0;
}
"""
            }
        ]
    },
    "2597": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 줄자접기 - 시뮬레이션
left, right = 0.0, 100.0

for _ in range(3):
    p = float(input())
    mid = (left + right) / 2

    if p <= mid:
        right = p + (p - left)
    else:
        left = p - (right - p)

print(f"{right - left:.1f}")
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;

// 줄자접기 - 시뮬레이션
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        double left = 0.0, right = 100.0;

        for (int i = 0; i < 3; i++) {
            double p = Double.parseDouble(br.readLine().trim());
            double mid = (left + right) / 2;

            if (p <= mid) right = p + (p - left);
            else left = p - (right - p);
        }
        System.out.printf("%.1f%n", right - left);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <iomanip>
using namespace std;

// 줄자접기 - 시뮬레이션
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    double left = 0.0, right = 100.0;

    for (int i = 0; i < 3; i++) {
        double p;
        cin >> p;
        double mid = (left + right) / 2;

        if (p <= mid) right = p + (p - left);
        else left = p - (right - p);
    }
    cout << fixed << setprecision(1) << right - left << endl;
    return 0;
}
"""
            }
        ]
    },
    "1951": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 활자 - 순환소수 순환마디 길이
a, b = map(int, input().split())

if a % b == 0:
    print(0)
else:
    seen = {}
    remainder = a % b
    pos = 0

    while remainder != 0 and remainder not in seen:
        seen[remainder] = pos
        remainder *= 10
        remainder = remainder % b
        pos += 1

    if remainder == 0:
        print(0)
    else:
        print(pos - seen[remainder])
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 활자 - 순환소수 순환마디 길이
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long a = Long.parseLong(st.nextToken());
        long b = Long.parseLong(st.nextToken());

        if (a % b == 0) {
            System.out.println(0);
            return;
        }

        Map<Long, Integer> seen = new HashMap<>();
        long remainder = a % b;
        int pos = 0;

        while (remainder != 0 && !seen.containsKey(remainder)) {
            seen.put(remainder, pos);
            remainder *= 10;
            remainder = remainder % b;
            pos++;
        }

        System.out.println(remainder == 0 ? 0 : pos - seen.get(remainder));
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <map>
using namespace std;

// 활자 - 순환소수 순환마디 길이
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long a, b;
    cin >> a >> b;

    if (a % b == 0) {
        cout << 0 << endl;
        return 0;
    }

    map<long long, int> seen;
    long long remainder = a % b;
    int pos = 0;

    while (remainder != 0 && seen.find(remainder) == seen.end()) {
        seen[remainder] = pos;
        remainder *= 10;
        remainder = remainder % b;
        pos++;
    }

    cout << (remainder == 0 ? 0 : pos - seen[remainder]) << endl;
    return 0;
}
"""
            }
        ]
    },
    "26595": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 전투의 신 - DP
n = int(input())
enemies = []
for _ in range(n):
    a, b = map(int, input().split())
    enemies.append((a, b))

# dp[j] = 연속 j마리 처치 중일 때 최대 점수
dp = {0: 0}

for i in range(n):
    a, b = enemies[i]
    new_dp = {}

    for j, score in dp.items():
        # 현재 적을 처치하지 않음
        if 0 not in new_dp or new_dp[0] < score:
            new_dp[0] = score

        # 현재 적을 처치함
        new_streak = j + 1
        bonus = new_streak * b
        new_score = score + a + bonus
        if new_streak not in new_dp or new_dp[new_streak] < new_score:
            new_dp[new_streak] = new_score

    dp = new_dp

print(max(dp.values()))
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 전투의 신 - DP
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[][] enemies = new int[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            enemies[i][0] = Integer.parseInt(st.nextToken());
            enemies[i][1] = Integer.parseInt(st.nextToken());
        }

        long[] dp = new long[n + 2];
        Arrays.fill(dp, Long.MIN_VALUE);
        dp[0] = 0;

        for (int i = 0; i < n; i++) {
            int a = enemies[i][0], b = enemies[i][1];
            long[] newDp = new long[n + 2];
            Arrays.fill(newDp, Long.MIN_VALUE);

            for (int j = 0; j <= i + 1; j++) {
                if (dp[j] == Long.MIN_VALUE) continue;
                newDp[0] = Math.max(newDp[0], dp[j]);
                int ns = j + 1;
                newDp[ns] = Math.max(newDp[ns], dp[j] + a + (long)ns * b);
            }
            dp = newDp;
        }

        long ans = 0;
        for (int j = 0; j <= n; j++) {
            if (dp[j] != Long.MIN_VALUE) ans = Math.max(ans, dp[j]);
        }
        System.out.println(ans);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
using namespace std;

// 전투의 신 - DP
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<pair<long long, long long>> enemies(n);
    for (int i = 0; i < n; i++) {
        cin >> enemies[i].first >> enemies[i].second;
    }

    vector<long long> dp(n + 2, LLONG_MIN);
    dp[0] = 0;

    for (int i = 0; i < n; i++) {
        long long a = enemies[i].first, b = enemies[i].second;
        vector<long long> newDp(n + 2, LLONG_MIN);

        for (int j = 0; j <= i + 1; j++) {
            if (dp[j] == LLONG_MIN) continue;
            newDp[0] = max(newDp[0], dp[j]);
            int ns = j + 1;
            newDp[ns] = max(newDp[ns], dp[j] + a + (long long)ns * b);
        }
        dp = newDp;
    }

    long long ans = 0;
    for (int j = 0; j <= n; j++) {
        if (dp[j] != LLONG_MIN) ans = max(ans, dp[j]);
    }
    cout << ans << endl;
    return 0;
}
"""
            }
        ]
    },
    "21737": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# SMUPC 계산기 - 파싱
n = int(input())
s = input().strip()

nums = []
ops = []
cur = ''

for c in s:
    if c in 'CSMD':
        if cur:
            nums.append(int(cur))
        cur = ''
        ops.append(c)
    else:
        cur += c

if cur:
    nums.append(int(cur))

result = nums[0]
results = []

for i, op in enumerate(ops):
    if op == 'C':
        results.append(result)
    elif op == 'S':
        result -= nums[i + 1]
    elif op == 'M':
        result *= nums[i + 1]
    elif op == 'D':
        if nums[i + 1] == 0:
            continue
        if result < 0:
            result = -(-result // nums[i + 1])
        else:
            result = result // nums[i + 1]

if not results:
    print("NO OUTPUT")
else:
    print(' '.join(map(str, results)))
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// SMUPC 계산기 - 파싱
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        String s = br.readLine().trim();

        List<Long> nums = new ArrayList<>();
        List<Character> ops = new ArrayList<>();
        StringBuilder cur = new StringBuilder();

        for (char c : s.toCharArray()) {
            if (c == 'C' || c == 'S' || c == 'M' || c == 'D') {
                if (cur.length() > 0) {
                    nums.add(Long.parseLong(cur.toString()));
                    cur = new StringBuilder();
                }
                ops.add(c);
            } else {
                cur.append(c);
            }
        }
        if (cur.length() > 0) nums.add(Long.parseLong(cur.toString()));

        long result = nums.get(0);
        List<Long> results = new ArrayList<>();

        for (int i = 0; i < ops.size(); i++) {
            char op = ops.get(i);
            if (op == 'C') results.add(result);
            else if (op == 'S') result -= nums.get(i + 1);
            else if (op == 'M') result *= nums.get(i + 1);
            else if (op == 'D') {
                if (nums.get(i + 1) == 0) continue;
                if (result < 0) result = -((-result) / nums.get(i + 1));
                else result = result / nums.get(i + 1);
            }
        }

        if (results.isEmpty()) System.out.println("NO OUTPUT");
        else {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < results.size(); i++) {
                if (i > 0) sb.append(" ");
                sb.append(results.get(i));
            }
            System.out.println(sb);
        }
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
#include <string>
using namespace std;

// SMUPC 계산기 - 파싱
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    string s;
    cin >> n >> s;

    vector<long long> nums;
    vector<char> ops;
    string cur = "";

    for (char c : s) {
        if (c == 'C' || c == 'S' || c == 'M' || c == 'D') {
            if (!cur.empty()) {
                nums.push_back(stoll(cur));
                cur = "";
            }
            ops.push_back(c);
        } else {
            cur += c;
        }
    }
    if (!cur.empty()) nums.push_back(stoll(cur));

    long long result = nums[0];
    vector<long long> results;

    for (int i = 0; i < ops.size(); i++) {
        char op = ops[i];
        if (op == 'C') results.push_back(result);
        else if (op == 'S') result -= nums[i + 1];
        else if (op == 'M') result *= nums[i + 1];
        else if (op == 'D') {
            if (nums[i + 1] == 0) continue;
            if (result < 0) result = -((-result) / nums[i + 1]);
            else result = result / nums[i + 1];
        }
    }

    if (results.empty()) cout << "NO OUTPUT" << endl;
    else {
        for (int i = 0; i < results.size(); i++) {
            if (i > 0) cout << " ";
            cout << results[i];
        }
        cout << endl;
    }
    return 0;
}
"""
            }
        ]
    },
    "11278": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
from collections import defaultdict
input = sys.stdin.readline
sys.setrecursionlimit(200000)

# 2-SAT - 2: SCC 기반 해결
def solve():
    n, m = map(int, input().split())

    graph = defaultdict(list)
    reverse_graph = defaultdict(list)

    def var_to_node(x):
        return 2 * x if x > 0 else 2 * (-x) + 1

    def neg_node(node):
        return node ^ 1

    for _ in range(m):
        a, b = map(int, input().split())
        na, nb = var_to_node(a), var_to_node(b)
        graph[neg_node(na)].append(nb)
        graph[neg_node(nb)].append(na)
        reverse_graph[nb].append(neg_node(na))
        reverse_graph[na].append(neg_node(nb))

    visited = [False] * (2 * n + 2)
    order = []

    def dfs1(v):
        stack = [(v, False)]
        while stack:
            node, processed = stack.pop()
            if processed:
                order.append(node)
                continue
            if visited[node]:
                continue
            visited[node] = True
            stack.append((node, True))
            for nxt in graph[node]:
                if not visited[nxt]:
                    stack.append((nxt, False))

    for i in range(2, 2 * n + 2):
        if not visited[i]:
            dfs1(i)

    scc_id = [-1] * (2 * n + 2)
    scc_count = 0

    def dfs2(v, scc):
        stack = [v]
        while stack:
            node = stack.pop()
            if scc_id[node] != -1:
                continue
            scc_id[node] = scc
            for nxt in reverse_graph[node]:
                if scc_id[nxt] == -1:
                    stack.append(nxt)

    for v in reversed(order):
        if scc_id[v] == -1:
            dfs2(v, scc_count)
            scc_count += 1

    result = [0] * (n + 1)
    for i in range(1, n + 1):
        pos, neg = 2 * i, 2 * i + 1
        if scc_id[pos] == scc_id[neg]:
            print(0)
            return
        result[i] = 1 if scc_id[pos] > scc_id[neg] else 0

    print(1)
    print(' '.join(map(str, result[1:])))

solve()
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 2-SAT - 2: SCC 기반 해결
public class Main {
    static List<Integer>[] graph, reverseGraph;
    static boolean[] visited;
    static int[] sccId;
    static List<Integer> order;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        int size = 2 * n + 2;
        graph = new ArrayList[size];
        reverseGraph = new ArrayList[size];
        for (int i = 0; i < size; i++) {
            graph[i] = new ArrayList<>();
            reverseGraph[i] = new ArrayList<>();
        }

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            int na = varToNode(a), nb = varToNode(b);
            graph[neg(na)].add(nb);
            graph[neg(nb)].add(na);
            reverseGraph[nb].add(neg(na));
            reverseGraph[na].add(neg(nb));
        }

        visited = new boolean[size];
        order = new ArrayList<>();
        for (int i = 2; i < size; i++) if (!visited[i]) dfs1(i);

        sccId = new int[size];
        Arrays.fill(sccId, -1);
        int sccCount = 0;
        for (int i = order.size() - 1; i >= 0; i--) {
            int v = order.get(i);
            if (sccId[v] == -1) dfs2(v, sccCount++);
        }

        StringBuilder sb = new StringBuilder();
        int[] result = new int[n + 1];
        boolean possible = true;

        for (int i = 1; i <= n; i++) {
            if (sccId[2 * i] == sccId[2 * i + 1]) { possible = false; break; }
            result[i] = sccId[2 * i] > sccId[2 * i + 1] ? 1 : 0;
        }

        if (!possible) System.out.println(0);
        else {
            sb.append(1).append("\\n");
            for (int i = 1; i <= n; i++) { if (i > 1) sb.append(" "); sb.append(result[i]); }
            System.out.println(sb);
        }
    }

    static int varToNode(int x) { return x > 0 ? 2 * x : 2 * (-x) + 1; }
    static int neg(int node) { return node ^ 1; }

    static void dfs1(int v) {
        Deque<int[]> stack = new ArrayDeque<>();
        stack.push(new int[]{v, 0});
        while (!stack.isEmpty()) {
            int[] cur = stack.peek();
            int node = cur[0];
            if (!visited[node]) visited[node] = true;
            boolean found = false;
            while (cur[1] < graph[node].size()) {
                int next = graph[node].get(cur[1]++);
                if (!visited[next]) { stack.push(new int[]{next, 0}); found = true; break; }
            }
            if (!found) { order.add(node); stack.pop(); }
        }
    }

    static void dfs2(int v, int scc) {
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(v);
        while (!stack.isEmpty()) {
            int node = stack.pop();
            if (sccId[node] != -1) continue;
            sccId[node] = scc;
            for (int next : reverseGraph[node]) if (sccId[next] == -1) stack.push(next);
        }
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
using namespace std;

// 2-SAT - 2: SCC 기반 해결
vector<int> graph[200002], reverseGraph[200002];
bool visited[200002];
int sccId[200002];
vector<int> order;

int varToNode(int x) { return x > 0 ? 2 * x : 2 * (-x) + 1; }
int neg(int node) { return node ^ 1; }

void dfs1(int start) {
    stack<pair<int, int>> st;
    st.push({start, 0});
    while (!st.empty()) {
        int node = st.top().first;
        int& idx = st.top().second;
        if (!visited[node]) visited[node] = true;
        bool found = false;
        while (idx < graph[node].size()) {
            int next = graph[node][idx++];
            if (!visited[next]) { st.push({next, 0}); found = true; break; }
        }
        if (!found) { order.push_back(node); st.pop(); }
    }
}

void dfs2(int start, int scc) {
    stack<int> st;
    st.push(start);
    while (!st.empty()) {
        int node = st.top(); st.pop();
        if (sccId[node] != -1) continue;
        sccId[node] = scc;
        for (int next : reverseGraph[node]) if (sccId[next] == -1) st.push(next);
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        int na = varToNode(a), nb = varToNode(b);
        graph[neg(na)].push_back(nb);
        graph[neg(nb)].push_back(na);
        reverseGraph[nb].push_back(neg(na));
        reverseGraph[na].push_back(neg(nb));
    }

    fill(visited, visited + 2 * n + 2, false);
    fill(sccId, sccId + 2 * n + 2, -1);

    for (int i = 2; i < 2 * n + 2; i++) if (!visited[i]) dfs1(i);

    int sccCount = 0;
    for (int i = order.size() - 1; i >= 0; i--) {
        int v = order[i];
        if (sccId[v] == -1) dfs2(v, sccCount++);
    }

    vector<int> result(n + 1);
    bool possible = true;

    for (int i = 1; i <= n; i++) {
        if (sccId[2 * i] == sccId[2 * i + 1]) { possible = false; break; }
        result[i] = sccId[2 * i] > sccId[2 * i + 1] ? 1 : 0;
    }

    if (!possible) cout << 0 << endl;
    else {
        cout << 1 << endl;
        for (int i = 1; i <= n; i++) { if (i > 1) cout << " "; cout << result[i]; }
        cout << endl;
    }
    return 0;
}
"""
            }
        ]
    },
    "1639": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 행운의 티켓 - 누적합
s = input().strip()
n = len(s)

if n == 0:
    print(0)
else:
    digits = [int(c) for c in s]
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + digits[i]

    max_len = 0
    for half in range(1, n // 2 + 1):
        length = 2 * half
        for start in range(n - length + 1):
            mid = start + half
            end = start + length
            if prefix[mid] - prefix[start] == prefix[end] - prefix[mid]:
                max_len = length
                break

    print(max_len)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;

// 행운의 티켓 - 누적합
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();

        if (s == null || s.isEmpty()) {
            System.out.println(0);
            return;
        }

        int n = s.length();
        int[] prefix = new int[n + 1];
        for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + (s.charAt(i) - '0');

        int maxLen = 0;
        for (int half = 1; half <= n / 2; half++) {
            int length = 2 * half;
            for (int start = 0; start <= n - length; start++) {
                int mid = start + half, end = start + length;
                if (prefix[mid] - prefix[start] == prefix[end] - prefix[mid]) {
                    maxLen = length;
                    break;
                }
            }
        }
        System.out.println(maxLen);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <string>
#include <vector>
using namespace std;

// 행운의 티켓 - 누적합
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    cin >> s;

    int n = s.length();
    if (n == 0) { cout << 0 << endl; return 0; }

    vector<int> prefix(n + 1, 0);
    for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + (s[i] - '0');

    int maxLen = 0;
    for (int half = 1; half <= n / 2; half++) {
        int length = 2 * half;
        for (int start = 0; start <= n - length; start++) {
            int mid = start + half, end = start + length;
            if (prefix[mid] - prefix[start] == prefix[end] - prefix[mid]) {
                maxLen = length;
                break;
            }
        }
    }
    cout << maxLen << endl;
    return 0;
}
"""
            }
        ]
    },
    "27932": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 어깨동무 - 이분 탐색
n, k = map(int, input().split())
heights = list(map(int, input().split()))

def can_achieve(diff):
    remove = 0
    for i in range(n - 1):
        if abs(heights[i] - heights[i + 1]) > diff:
            remove += 1
    return remove <= k

left, right = 0, 10**9
answer = right

while left <= right:
    mid = (left + right) // 2
    if can_achieve(mid):
        answer = mid
        right = mid - 1
    else:
        left = mid + 1

print(answer)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 어깨동무 - 이분 탐색
public class Main {
    static int n, k;
    static int[] heights;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        n = Integer.parseInt(st.nextToken());
        k = Integer.parseInt(st.nextToken());
        heights = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) heights[i] = Integer.parseInt(st.nextToken());

        long left = 0, right = 1_000_000_000L, answer = right;
        while (left <= right) {
            long mid = (left + right) / 2;
            if (canAchieve(mid)) { answer = mid; right = mid - 1; }
            else left = mid + 1;
        }
        System.out.println(answer);
    }

    static boolean canAchieve(long diff) {
        int remove = 0;
        for (int i = 0; i < n - 1; i++)
            if (Math.abs(heights[i] - heights[i + 1]) > diff) remove++;
        return remove <= k;
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

// 어깨동무 - 이분 탐색
int n, k;
vector<int> heights;

bool canAchieve(long long diff) {
    int remove = 0;
    for (int i = 0; i < n - 1; i++)
        if (abs(heights[i] - heights[i + 1]) > diff) remove++;
    return remove <= k;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> k;
    heights.resize(n);
    for (int i = 0; i < n; i++) cin >> heights[i];

    long long left = 0, right = 1000000000LL, answer = right;
    while (left <= right) {
        long long mid = (left + right) / 2;
        if (canAchieve(mid)) { answer = mid; right = mid - 1; }
        else left = mid + 1;
    }
    cout << answer << endl;
    return 0;
}
"""
            }
        ]
    },
    "25793": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
from math import gcd
input = sys.stdin.readline

# 초콜릿 피라미드 - 수학
n = int(input())
total = n * (n + 1) // 2

if total % 2 == 1:
    print("0/1")
else:
    half = total // 2
    count = 0
    for cut in range(1, n):
        left = cut * (cut + 1) // 2
        if left == half:
            count += 1

    if count == 0:
        print("0/1")
    else:
        total_cuts = n - 1
        g = gcd(count, total_cuts)
        print(f"{count // g}/{total_cuts // g}")
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;

// 초콜릿 피라미드 - 수학
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        long total = (long) n * (n + 1) / 2;
        if (total % 2 == 1) { System.out.println("0/1"); return; }

        long half = total / 2;
        int count = 0;
        for (int cut = 1; cut < n; cut++) {
            long left = (long) cut * (cut + 1) / 2;
            if (left == half) count++;
        }

        if (count == 0) System.out.println("0/1");
        else {
            int totalCuts = n - 1;
            int g = gcd(count, totalCuts);
            System.out.println((count / g) + "/" + (totalCuts / g));
        }
    }

    static int gcd(int a, int b) { return b == 0 ? a : gcd(b, a % b); }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <algorithm>
using namespace std;

// 초콜릿 피라미드 - 수학
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    long long total = (long long) n * (n + 1) / 2;
    if (total % 2 == 1) { cout << "0/1" << endl; return 0; }

    long long half = total / 2;
    int count = 0;
    for (int cut = 1; cut < n; cut++) {
        long long left = (long long) cut * (cut + 1) / 2;
        if (left == half) count++;
    }

    if (count == 0) cout << "0/1" << endl;
    else {
        int totalCuts = n - 1;
        int g = __gcd(count, totalCuts);
        cout << (count / g) << "/" << (totalCuts / g) << endl;
    }
    return 0;
}
"""
            }
        ]
    },
    "10424": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 알고리즘 기말고사 - 순위 계산
n = int(input())
students = []

for i in range(n):
    parts = input().split()
    name = parts[0]
    scores = list(map(int, parts[1:]))
    total = sum(scores)
    students.append((total, name))

students.sort(key=lambda x: (-x[0], x[1]))

ranks = []
for i, (total, name) in enumerate(students):
    if i == 0 or total != students[i-1][0]:
        rank = i + 1
    ranks.append(rank)

for i, (total, name) in enumerate(students):
    print(f"{ranks[i]} {name} {total}")
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 알고리즘 기말고사 - 순위 계산
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        List<int[]> students = new ArrayList<>();
        String[] names = new String[n];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            names[i] = st.nextToken();
            int total = 0;
            while (st.hasMoreTokens()) total += Integer.parseInt(st.nextToken());
            students.add(new int[]{total, i});
        }

        students.sort((a, b) -> {
            if (a[0] != b[0]) return b[0] - a[0];
            return names[a[1]].compareTo(names[b[1]]);
        });

        StringBuilder sb = new StringBuilder();
        int rank = 1;
        for (int i = 0; i < n; i++) {
            if (i > 0 && students.get(i)[0] != students.get(i-1)[0]) rank = i + 1;
            int idx = students.get(i)[1];
            sb.append(rank).append(" ").append(names[idx]).append(" ").append(students.get(i)[0]).append("\\n");
        }
        System.out.print(sb);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
#include <algorithm>
#include <sstream>
using namespace std;

// 알고리즘 기말고사 - 순위 계산
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    cin.ignore();

    vector<pair<int, string>> students;

    for (int i = 0; i < n; i++) {
        string line;
        getline(cin, line);
        istringstream iss(line);
        string name;
        iss >> name;
        int total = 0, score;
        while (iss >> score) total += score;
        students.push_back({total, name});
    }

    sort(students.begin(), students.end(), [](auto& a, auto& b) {
        if (a.first != b.first) return a.first > b.first;
        return a.second < b.second;
    });

    int rank = 1;
    for (int i = 0; i < n; i++) {
        if (i > 0 && students[i].first != students[i-1].first) rank = i + 1;
        cout << rank << " " << students[i].second << " " << students[i].first << "\\n";
    }
    return 0;
}
"""
            }
        ]
    },
    "31460": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 초콜릿과 11과 팰린드롬
n = int(input())
s = input().strip()

max_len = 0

for center in range(n):
    # 홀수 길이 팰린드롬
    for r in range(min(center + 1, n - center)):
        left, right = center - r, center + r
        if s[left] != s[right]:
            break
        odd_sum = even_sum = 0
        for i, c in enumerate(s[left:right+1]):
            if i % 2 == 0:
                odd_sum += int(c)
            else:
                even_sum += int(c)
        if (odd_sum - even_sum) % 11 == 0:
            max_len = max(max_len, right - left + 1)

for center in range(n - 1):
    # 짝수 길이 팰린드롬
    for r in range(min(center + 1, n - center - 1)):
        left, right = center - r, center + 1 + r
        if s[left] != s[right]:
            break
        odd_sum = even_sum = 0
        for i, c in enumerate(s[left:right+1]):
            if i % 2 == 0:
                odd_sum += int(c)
            else:
                even_sum += int(c)
        if (odd_sum - even_sum) % 11 == 0:
            max_len = max(max_len, right - left + 1)

print(max_len)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;

// 초콜릿과 11과 팰린드롬
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        String s = br.readLine().trim();

        int maxLen = 0;

        for (int center = 0; center < n; center++) {
            for (int r = 0; r <= Math.min(center, n - center - 1); r++) {
                int left = center - r, right = center + r;
                if (s.charAt(left) != s.charAt(right)) break;
                int oddSum = 0, evenSum = 0;
                for (int i = left; i <= right; i++) {
                    int d = s.charAt(i) - '0';
                    if ((i - left) % 2 == 0) oddSum += d;
                    else evenSum += d;
                }
                if ((oddSum - evenSum) % 11 == 0) maxLen = Math.max(maxLen, right - left + 1);
            }
            for (int r = 0; r <= Math.min(center, n - center - 2); r++) {
                int left = center - r, right = center + 1 + r;
                if (s.charAt(left) != s.charAt(right)) break;
                int oddSum = 0, evenSum = 0;
                for (int i = left; i <= right; i++) {
                    int d = s.charAt(i) - '0';
                    if ((i - left) % 2 == 0) oddSum += d;
                    else evenSum += d;
                }
                if ((oddSum - evenSum) % 11 == 0) maxLen = Math.max(maxLen, right - left + 1);
            }
        }
        System.out.println(maxLen);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

// 초콜릿과 11과 팰린드롬
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    string s;
    cin >> n >> s;

    int maxLen = 0;

    for (int center = 0; center < n; center++) {
        for (int r = 0; r <= min(center, n - center - 1); r++) {
            int left = center - r, right = center + r;
            if (s[left] != s[right]) break;
            int oddSum = 0, evenSum = 0;
            for (int i = left; i <= right; i++) {
                int d = s[i] - '0';
                if ((i - left) % 2 == 0) oddSum += d;
                else evenSum += d;
            }
            if ((oddSum - evenSum) % 11 == 0) maxLen = max(maxLen, right - left + 1);
        }
        for (int r = 0; r <= min(center, n - center - 2); r++) {
            int left = center - r, right = center + 1 + r;
            if (s[left] != s[right]) break;
            int oddSum = 0, evenSum = 0;
            for (int i = left; i <= right; i++) {
                int d = s[i] - '0';
                if ((i - left) % 2 == 0) oddSum += d;
                else evenSum += d;
            }
            if ((oddSum - evenSum) % 11 == 0) maxLen = max(maxLen, right - left + 1);
        }
    }
    cout << maxLen << endl;
    return 0;
}
"""
            }
        ]
    },
    "27165": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 모든 곳을 안전하게 - 시뮬레이션
n, m = map(int, input().split())
visited = [[False] * m for _ in range(n)]
commands = input().strip()

x, y = 0, 0
visited[x][y] = True

dx = {'U': -1, 'D': 1, 'L': 0, 'R': 0}
dy = {'U': 0, 'D': 0, 'L': -1, 'R': 1}

for cmd in commands:
    nx, ny = x + dx[cmd], y + dy[cmd]
    if 0 <= nx < n and 0 <= ny < m:
        x, y = nx, ny
        visited[x][y] = True

print("YES" if all(visited[i][j] for i in range(n) for j in range(m)) else "NO")
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 모든 곳을 안전하게 - 시뮬레이션
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());
        boolean[][] visited = new boolean[n][m];
        String commands = br.readLine().trim();

        int x = 0, y = 0;
        visited[x][y] = true;

        for (char cmd : commands.toCharArray()) {
            int nx = x, ny = y;
            if (cmd == 'U') nx--;
            else if (cmd == 'D') nx++;
            else if (cmd == 'L') ny--;
            else if (cmd == 'R') ny++;

            if (nx >= 0 && nx < n && ny >= 0 && ny < m) {
                x = nx; y = ny;
                visited[x][y] = true;
            }
        }

        boolean allVisited = true;
        for (int i = 0; i < n && allVisited; i++)
            for (int j = 0; j < m && allVisited; j++)
                if (!visited[i][j]) allVisited = false;

        System.out.println(allVisited ? "YES" : "NO");
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
#include <string>
using namespace std;

// 모든 곳을 안전하게 - 시뮬레이션
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;
    vector<vector<bool>> visited(n, vector<bool>(m, false));
    string commands;
    cin >> commands;

    int x = 0, y = 0;
    visited[x][y] = true;

    for (char cmd : commands) {
        int nx = x, ny = y;
        if (cmd == 'U') nx--;
        else if (cmd == 'D') nx++;
        else if (cmd == 'L') ny--;
        else if (cmd == 'R') ny++;

        if (nx >= 0 && nx < n && ny >= 0 && ny < m) {
            x = nx; y = ny;
            visited[x][y] = true;
        }
    }

    bool allVisited = true;
    for (int i = 0; i < n && allVisited; i++)
        for (int j = 0; j < m && allVisited; j++)
            if (!visited[i][j]) allVisited = false;

    cout << (allVisited ? "YES" : "NO") << endl;
    return 0;
}
"""
            }
        ]
    },
    "15979": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
from math import gcd
input = sys.stdin.readline

# 스승님 찾기 - GCD
n = int(input())
values = [int(input()) for _ in range(n)]

if n == 1:
    print(1)
else:
    result = abs(values[1] - values[0])
    for i in range(2, n):
        result = gcd(result, abs(values[i] - values[i-1]))
    print(result)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;

// 스승님 찾기 - GCD
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        long[] values = new long[n];
        for (int i = 0; i < n; i++) values[i] = Long.parseLong(br.readLine().trim());

        if (n == 1) { System.out.println(1); return; }

        long result = Math.abs(values[1] - values[0]);
        for (int i = 2; i < n; i++) result = gcd(result, Math.abs(values[i] - values[i-1]));
        System.out.println(result);
    }

    static long gcd(long a, long b) { return b == 0 ? a : gcd(b, a % b); }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
using namespace std;

// 스승님 찾기 - GCD
long long gcd(long long a, long long b) { return b == 0 ? a : gcd(b, a % b); }

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    vector<long long> values(n);
    for (int i = 0; i < n; i++) cin >> values[i];

    if (n == 1) { cout << 1 << endl; return 0; }

    long long result = abs(values[1] - values[0]);
    for (int i = 2; i < n; i++) result = gcd(result, abs(values[i] - values[i-1]));
    cout << result << endl;
    return 0;
}
"""
            }
        ]
    },
    "14911": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 궁합 쌍 찾기
nums = list(map(int, input().split()))
target = int(input())

pairs = set()
n = len(nums)

for i in range(n):
    for j in range(i + 1, n):
        if nums[i] + nums[j] == target:
            pair = tuple(sorted([nums[i], nums[j]]))
            pairs.add(pair)

pairs = sorted(pairs)

if not pairs:
    print("0")
else:
    for p in pairs:
        print(p[0], p[1])
    print(len(pairs))
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 궁합 쌍 찾기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        List<Integer> nums = new ArrayList<>();
        while (st.hasMoreTokens()) nums.add(Integer.parseInt(st.nextToken()));
        int target = Integer.parseInt(br.readLine().trim());

        Set<String> pairSet = new TreeSet<>();
        List<int[]> pairs = new ArrayList<>();
        int n = nums.size();

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (nums.get(i) + nums.get(j) == target) {
                    int a = Math.min(nums.get(i), nums.get(j));
                    int b = Math.max(nums.get(i), nums.get(j));
                    String key = a + " " + b;
                    if (!pairSet.contains(key)) {
                        pairSet.add(key);
                        pairs.add(new int[]{a, b});
                    }
                }
            }
        }

        pairs.sort((x, y) -> x[0] != y[0] ? x[0] - y[0] : x[1] - y[1]);

        StringBuilder sb = new StringBuilder();
        if (pairs.isEmpty()) sb.append("0");
        else {
            for (int[] p : pairs) sb.append(p[0]).append(" ").append(p[1]).append("\\n");
            sb.append(pairs.size());
        }
        System.out.println(sb);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
#include <sstream>
using namespace std;

// 궁합 쌍 찾기
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string line;
    getline(cin, line);
    istringstream iss(line);
    vector<int> nums;
    int x;
    while (iss >> x) nums.push_back(x);

    int target;
    cin >> target;

    set<pair<int,int>> pairSet;
    int n = nums.size();

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (nums[i] + nums[j] == target) {
                int a = min(nums[i], nums[j]);
                int b = max(nums[i], nums[j]);
                pairSet.insert({a, b});
            }
        }
    }

    if (pairSet.empty()) cout << "0" << endl;
    else {
        for (auto& p : pairSet) cout << p.first << " " << p.second << "\\n";
        cout << pairSet.size() << endl;
    }
    return 0;
}
"""
            }
        ]
    },
    "3005": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 크로스워드 퍼즐 쳐다보기 - 문자열 추출
r, c = map(int, input().split())
grid = [input().strip() for _ in range(r)]

words = set()

for i in range(r):
    word = ""
    for j in range(c):
        if grid[i][j] != '#':
            word += grid[i][j]
        else:
            if len(word) >= 2:
                words.add(word)
            word = ""
    if len(word) >= 2:
        words.add(word)

for j in range(c):
    word = ""
    for i in range(r):
        if grid[i][j] != '#':
            word += grid[i][j]
        else:
            if len(word) >= 2:
                words.add(word)
            word = ""
    if len(word) >= 2:
        words.add(word)

print(min(words))
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 크로스워드 퍼즐 쳐다보기 - 문자열 추출
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int r = Integer.parseInt(st.nextToken());
        int c = Integer.parseInt(st.nextToken());

        char[][] grid = new char[r][c];
        for (int i = 0; i < r; i++) grid[i] = br.readLine().toCharArray();

        Set<String> words = new TreeSet<>();

        for (int i = 0; i < r; i++) {
            StringBuilder word = new StringBuilder();
            for (int j = 0; j < c; j++) {
                if (grid[i][j] != '#') word.append(grid[i][j]);
                else { if (word.length() >= 2) words.add(word.toString()); word = new StringBuilder(); }
            }
            if (word.length() >= 2) words.add(word.toString());
        }

        for (int j = 0; j < c; j++) {
            StringBuilder word = new StringBuilder();
            for (int i = 0; i < r; i++) {
                if (grid[i][j] != '#') word.append(grid[i][j]);
                else { if (word.length() >= 2) words.add(word.toString()); word = new StringBuilder(); }
            }
            if (word.length() >= 2) words.add(word.toString());
        }

        System.out.println(words.iterator().next());
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
#include <set>
#include <string>
using namespace std;

// 크로스워드 퍼즐 쳐다보기 - 문자열 추출
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int r, c;
    cin >> r >> c;
    vector<string> grid(r);
    for (int i = 0; i < r; i++) cin >> grid[i];

    set<string> words;

    for (int i = 0; i < r; i++) {
        string word = "";
        for (int j = 0; j < c; j++) {
            if (grid[i][j] != '#') word += grid[i][j];
            else { if (word.length() >= 2) words.insert(word); word = ""; }
        }
        if (word.length() >= 2) words.insert(word);
    }

    for (int j = 0; j < c; j++) {
        string word = "";
        for (int i = 0; i < r; i++) {
            if (grid[i][j] != '#') word += grid[i][j];
            else { if (word.length() >= 2) words.insert(word); word = ""; }
        }
        if (word.length() >= 2) words.insert(word);
    }

    cout << *words.begin() << endl;
    return 0;
}
"""
            }
        ]
    },
    "16951": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 블록 놀이 - 등차수열
n, k = map(int, input().split())
blocks = list(map(int, input().split()))

max_keep = 0

for i in range(n):
    a = blocks[i] - i * k
    if a < 1:
        continue

    count = 0
    for j in range(n):
        expected = a + j * k
        if blocks[j] == expected:
            count += 1

    max_keep = max(max_keep, count)

print(n - max_keep)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 블록 놀이 - 등차수열
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());
        int[] blocks = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) blocks[i] = Integer.parseInt(st.nextToken());

        int maxKeep = 0;
        for (int i = 0; i < n; i++) {
            int a = blocks[i] - i * k;
            if (a < 1) continue;
            int count = 0;
            for (int j = 0; j < n; j++) {
                int expected = a + j * k;
                if (blocks[j] == expected) count++;
            }
            maxKeep = Math.max(maxKeep, count);
        }
        System.out.println(n - maxKeep);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
using namespace std;

// 블록 놀이 - 등차수열
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;
    vector<int> blocks(n);
    for (int i = 0; i < n; i++) cin >> blocks[i];

    int maxKeep = 0;
    for (int i = 0; i < n; i++) {
        int a = blocks[i] - i * k;
        if (a < 1) continue;
        int count = 0;
        for (int j = 0; j < n; j++) {
            int expected = a + j * k;
            if (blocks[j] == expected) count++;
        }
        maxKeep = max(maxKeep, count);
    }
    cout << n - maxKeep << endl;
    return 0;
}
"""
            }
        ]
    },
    "28066": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
from collections import deque
input = sys.stdin.readline

# 타노스는 요세푸스가 밉다 - 큐 시뮬레이션
n, k = map(int, input().split())
q = deque(range(1, n + 1))

while len(q) > 1:
    survivor = q.popleft()
    for _ in range(min(k - 1, len(q))):
        q.popleft()
    q.append(survivor)

print(q[0])
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

// 타노스는 요세푸스가 밉다 - 큐 시뮬레이션
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        Deque<Integer> q = new ArrayDeque<>();
        for (int i = 1; i <= n; i++) q.addLast(i);

        while (q.size() > 1) {
            int survivor = q.pollFirst();
            int toRemove = Math.min(k - 1, q.size());
            for (int i = 0; i < toRemove; i++) q.pollFirst();
            q.addLast(survivor);
        }
        System.out.println(q.peekFirst());
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <deque>
using namespace std;

// 타노스는 요세푸스가 밉다 - 큐 시뮬레이션
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    deque<int> q;
    for (int i = 1; i <= n; i++) q.push_back(i);

    while (q.size() > 1) {
        int survivor = q.front();
        q.pop_front();
        int toRemove = min(k - 1, (int)q.size());
        for (int i = 0; i < toRemove; i++) q.pop_front();
        q.push_back(survivor);
    }
    cout << q.front() << endl;
    return 0;
}
"""
            }
        ]
    },
    "28086": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 미소녀 컴퓨터 파루빗토 쨩 - 8진수 계산기
expr = input().strip()

op_pos = -1
op = ''
for i in range(1, len(expr)):
    if expr[i] in '+-*':
        op_pos = i
        op = expr[i]
        break

a = int(expr[:op_pos], 8)
b = int(expr[op_pos + 1:], 8)

if op == '+':
    result = a + b
elif op == '-':
    result = a - b
elif op == '*':
    result = a * b

if result == 0:
    print(0)
elif result > 0:
    print(oct(result)[2:])
else:
    print('-' + oct(-result)[2:])
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;

// 미소녀 컴퓨터 파루빗토 쨩 - 8진수 계산기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String expr = br.readLine().trim();

        int opPos = -1;
        char op = ' ';
        for (int i = 1; i < expr.length(); i++) {
            char c = expr.charAt(i);
            if (c == '+' || c == '-' || c == '*') {
                opPos = i;
                op = c;
                break;
            }
        }

        long a = Long.parseLong(expr.substring(0, opPos), 8);
        long b = Long.parseLong(expr.substring(opPos + 1), 8);

        long result = 0;
        if (op == '+') result = a + b;
        else if (op == '-') result = a - b;
        else if (op == '*') result = a * b;

        if (result == 0) System.out.println(0);
        else if (result > 0) System.out.println(Long.toOctalString(result));
        else System.out.println("-" + Long.toOctalString(-result));
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <string>
using namespace std;

// 미소녀 컴퓨터 파루빗토 쨩 - 8진수 계산기
long long octalToDecimal(const string& s) {
    long long result = 0;
    int start = 0;
    bool neg = false;
    if (s[0] == '-') { neg = true; start = 1; }
    for (int i = start; i < s.length(); i++)
        result = result * 8 + (s[i] - '0');
    return neg ? -result : result;
}

string decimalToOctal(long long n) {
    if (n == 0) return "0";
    bool neg = n < 0;
    if (neg) n = -n;
    string result = "";
    while (n > 0) { result = char('0' + n % 8) + result; n /= 8; }
    return neg ? "-" + result : result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string expr;
    cin >> expr;

    int opPos = -1;
    char op = ' ';
    for (int i = 1; i < expr.length(); i++) {
        if (expr[i] == '+' || expr[i] == '-' || expr[i] == '*') {
            opPos = i;
            op = expr[i];
            break;
        }
    }

    long long a = octalToDecimal(expr.substr(0, opPos));
    long long b = octalToDecimal(expr.substr(opPos + 1));

    long long result = 0;
    if (op == '+') result = a + b;
    else if (op == '-') result = a - b;
    else if (op == '*') result = a * b;

    cout << decimalToOctal(result) << endl;
    return 0;
}
"""
            }
        ]
    }
}

# 기존 데이터에 새 솔루션 추가
data.update(new_solutions)

# 파일 저장
with open('data/baekjoon/baek_medium.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Successfully updated baek_medium.json with {len(new_solutions)} new problems")
print(f"Total problems in file: {len(data)}")
