#!/usr/bin/env python3
import json

# Load the checkpoint file
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r') as f:
    data = json.load(f)

# Solutions for problems 2080-2089
solutions = {
    2080: {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
segments = []
for _ in range(n):
    a, b = map(int, input().split())
    if a > b:
        a, b = b, a
    segments.append((a, b))

# Sort by start, then by end
segments.sort()

# Count overlapping pairs using sweep line
# Two segments overlap if their intersection has positive length
count = 0
events = []
for i, (a, b) in enumerate(segments):
    events.append((a, 0, i))  # start
    events.append((b, 1, i))  # end

events.sort()

from sortedcontainers import SortedList
active = SortedList()
result = 0

for pos, typ, idx in events:
    if typ == 0:  # start
        # Count overlaps with segments that started before and haven't ended
        a, b = segments[idx]
        # All active segments overlap with this one if they have common interior
        for end in active:
            if end > a:
                result += 1
        active.add(b)
    else:  # end
        active.remove(segments[idx][1])

print(result)
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());

        int[][] segments = new int[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            if (a > b) { int t = a; a = b; b = t; }
            segments[i][0] = a;
            segments[i][1] = b;
        }

        Arrays.sort(segments, (x, y) -> x[0] != y[0] ? x[0] - y[0] : x[1] - y[1]);

        long count = 0;
        TreeMap<Integer, Integer> active = new TreeMap<>();

        List<int[]> events = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            events.add(new int[]{segments[i][0], 0, i});
            events.add(new int[]{segments[i][1], 1, i});
        }
        events.sort((a, b) -> a[0] != b[0] ? a[0] - b[0] : a[1] - b[1]);

        for (int[] e : events) {
            int pos = e[0], type = e[1], idx = e[2];
            if (type == 0) {
                int start = segments[idx][0];
                for (int end : active.tailMap(start, false).keySet()) {
                    count += active.get(end);
                }
                active.merge(segments[idx][1], 1, Integer::sum);
            } else {
                int end = segments[idx][1];
                if (active.get(end) == 1) active.remove(end);
                else active.merge(end, -1, Integer::sum);
            }
        }

        System.out.println(count);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<pair<int,int>> segments(n);
    vector<tuple<int,int,int>> events;

    for (int i = 0; i < n; i++) {
        int a, b;
        cin >> a >> b;
        if (a > b) swap(a, b);
        segments[i] = {a, b};
        events.push_back({a, 0, i});
        events.push_back({b, 1, i});
    }

    sort(events.begin(), events.end());

    long long count = 0;
    map<int, int> active;

    for (auto& [pos, type, idx] : events) {
        if (type == 0) {
            int start = segments[idx].first;
            auto it = active.upper_bound(start);
            while (it != active.end()) {
                count += it->second;
                it++;
            }
            active[segments[idx].second]++;
        } else {
            int end = segments[idx].second;
            if (--active[end] == 0) active.erase(end);
        }
    }

    cout << count << endl;
    return 0;
}
'''
    },
    2081: {
        "python": '''import sys
input = sys.stdin.readline

n, m = map(int, input().split())
# Build graph of weight comparisons
# If a < b, then a's weight is less than b's weight
graph = [[] for _ in range(n + 1)]
reverse_graph = [[] for _ in range(n + 1)]

for _ in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)
    reverse_graph[b].append(a)

# For each node, count how many are heavier (reachable in graph)
# and how many are lighter (reachable in reverse_graph)
def count_reachable(start, adj):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for neighbor in adj[node]:
            if neighbor not in visited:
                stack.append(neighbor)
    return len(visited) - 1

for i in range(1, n + 1):
    heavier = count_reachable(i, graph)
    lighter = count_reachable(i, reverse_graph)
    print(lighter + 1, heavier + lighter + 1)
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    static List<Integer>[] graph, reverseGraph;
    static int n;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        graph = new ArrayList[n + 1];
        reverseGraph = new ArrayList[n + 1];
        for (int i = 0; i <= n; i++) {
            graph[i] = new ArrayList<>();
            reverseGraph[i] = new ArrayList<>();
        }

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            graph[a].add(b);
            reverseGraph[b].add(a);
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= n; i++) {
            int heavier = countReachable(i, graph);
            int lighter = countReachable(i, reverseGraph);
            sb.append((lighter + 1) + " " + (heavier + lighter + 1) + "\n");
        }
        System.out.print(sb);
    }

    static int countReachable(int start, List<Integer>[] adj) {
        boolean[] visited = new boolean[n + 1];
        Stack<Integer> stack = new Stack<>();
        stack.push(start);
        int count = 0;

        while (!stack.isEmpty()) {
            int node = stack.pop();
            if (visited[node]) continue;
            visited[node] = true;
            count++;
            for (int next : adj[node]) {
                if (!visited[next]) stack.push(next);
            }
        }
        return count - 1;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <stack>
using namespace std;

int n;
vector<int> graph[1001], reverseGraph[1001];

int countReachable(int start, vector<int> adj[]) {
    vector<bool> visited(n + 1, false);
    stack<int> st;
    st.push(start);
    int count = 0;

    while (!st.empty()) {
        int node = st.top();
        st.pop();
        if (visited[node]) continue;
        visited[node] = true;
        count++;
        for (int next : adj[node]) {
            if (!visited[next]) st.push(next);
        }
    }
    return count - 1;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int m;
    cin >> n >> m;

    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        graph[a].push_back(b);
        reverseGraph[b].push_back(a);
    }

    for (int i = 1; i <= n; i++) {
        int heavier = countReachable(i, graph);
        int lighter = countReachable(i, reverseGraph);
        cout << lighter + 1 << " " << heavier + lighter + 1 << "\n";
    }

    return 0;
}
'''
    },
    2082: {
        "python": '''import sys
input = sys.stdin.readline

# Digital clock pattern
# Each digit is represented as a 5x3 grid of # and .
patterns = {
    0: ["###", "#.#", "#.#", "#.#", "###"],
    1: ["..#", "..#", "..#", "..#", "..#"],
    2: ["###", "..#", "###", "#..", "###"],
    3: ["###", "..#", "###", "..#", "###"],
    4: ["#.#", "#.#", "###", "..#", "..#"],
    5: ["###", "#..", "###", "..#", "###"],
    6: ["###", "#..", "###", "#.#", "###"],
    7: ["###", "..#", "..#", "..#", "..#"],
    8: ["###", "#.#", "###", "#.#", "###"],
    9: ["###", "#.#", "###", "..#", "###"]
}

# Read the broken display
display = []
for _ in range(5):
    display.append(input().strip())

def matches(digit, col):
    for row in range(5):
        for c in range(3):
            if display[row][col + c] == '#' and patterns[digit][row][c] != '#':
                return False
    return True

def find_possible(col):
    possible = []
    for d in range(10):
        if matches(d, col):
            possible.append(d)
    return possible

# Columns for each digit: 0, 4, 9, 13 (with : at column 7-8)
h1 = find_possible(0)
h2 = find_possible(4)
m1 = find_possible(10)
m2 = find_possible(14)

result = None
for d1 in h1:
    for d2 in h2:
        hour = d1 * 10 + d2
        if hour > 23:
            continue
        for d3 in m1:
            for d4 in m2:
                minute = d3 * 10 + d4
                if minute > 59:
                    continue
                if result is None:
                    result = f"{d1}{d2}:{d3}{d4}"
                else:
                    print("-1")
                    exit()

print(result if result else "-1")
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    static String[][] patterns = {
        {"###", "#.#", "#.#", "#.#", "###"},
        {"..#", "..#", "..#", "..#", "..#"},
        {"###", "..#", "###", "#..", "###"},
        {"###", "..#", "###", "..#", "###"},
        {"#.#", "#.#", "###", "..#", "..#"},
        {"###", "#..", "###", "..#", "###"},
        {"###", "#..", "###", "#.#", "###"},
        {"###", "..#", "..#", "..#", "..#"},
        {"###", "#.#", "###", "#.#", "###"},
        {"###", "#.#", "###", "..#", "###"}
    };

    static String[] display = new String[5];

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        for (int i = 0; i < 5; i++) {
            display[i] = br.readLine();
        }

        List<Integer> h1 = findPossible(0);
        List<Integer> h2 = findPossible(4);
        List<Integer> m1 = findPossible(10);
        List<Integer> m2 = findPossible(14);

        String result = null;
        for (int d1 : h1) {
            for (int d2 : h2) {
                int hour = d1 * 10 + d2;
                if (hour > 23) continue;
                for (int d3 : m1) {
                    for (int d4 : m2) {
                        int minute = d3 * 10 + d4;
                        if (minute > 59) continue;
                        if (result == null) {
                            result = String.format("%d%d:%d%d", d1, d2, d3, d4);
                        } else {
                            System.out.println(-1);
                            return;
                        }
                    }
                }
            }
        }

        System.out.println(result != null ? result : -1);
    }

    static boolean matches(int digit, int col) {
        for (int row = 0; row < 5; row++) {
            for (int c = 0; c < 3; c++) {
                if (display[row].charAt(col + c) == '#' && patterns[digit][row].charAt(c) != '#') {
                    return false;
                }
            }
        }
        return true;
    }

    static List<Integer> findPossible(int col) {
        List<Integer> possible = new ArrayList<>();
        for (int d = 0; d < 10; d++) {
            if (matches(d, col)) possible.add(d);
        }
        return possible;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <string>
using namespace std;

string patterns[10][5] = {
    {"###", "#.#", "#.#", "#.#", "###"},
    {"..#", "..#", "..#", "..#", "..#"},
    {"###", "..#", "###", "#..", "###"},
    {"###", "..#", "###", "..#", "###"},
    {"#.#", "#.#", "###", "..#", "..#"},
    {"###", "#..", "###", "..#", "###"},
    {"###", "#..", "###", "#.#", "###"},
    {"###", "..#", "..#", "..#", "..#"},
    {"###", "#.#", "###", "#.#", "###"},
    {"###", "#.#", "###", "..#", "###"}
};

string display[5];

bool matches(int digit, int col) {
    for (int row = 0; row < 5; row++) {
        for (int c = 0; c < 3; c++) {
            if (display[row][col + c] == '#' && patterns[digit][row][c] != '#') {
                return false;
            }
        }
    }
    return true;
}

vector<int> findPossible(int col) {
    vector<int> possible;
    for (int d = 0; d < 10; d++) {
        if (matches(d, col)) possible.push_back(d);
    }
    return possible;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    for (int i = 0; i < 5; i++) {
        cin >> display[i];
    }

    vector<int> h1 = findPossible(0);
    vector<int> h2 = findPossible(4);
    vector<int> m1 = findPossible(10);
    vector<int> m2 = findPossible(14);

    string result = "";
    int count = 0;

    for (int d1 : h1) {
        for (int d2 : h2) {
            int hour = d1 * 10 + d2;
            if (hour > 23) continue;
            for (int d3 : m1) {
                for (int d4 : m2) {
                    int minute = d3 * 10 + d4;
                    if (minute > 59) continue;
                    count++;
                    if (count == 1) {
                        result = to_string(d1) + to_string(d2) + ":" + to_string(d3) + to_string(d4);
                    }
                }
            }
        }
    }

    if (count == 1) cout << result << endl;
    else cout << -1 << endl;

    return 0;
}
'''
    },
    2083: {
        "python": '''import sys
input = sys.stdin.readline

while True:
    line = input().strip()
    if line == '#':
        break

    parts = line.split()
    name = parts[0]
    age = int(parts[1])
    weight = int(parts[2])

    if age > 17 or weight >= 80:
        print(f"{name} Senior")
    else:
        print(f"{name} Junior")
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        while (true) {
            String line = br.readLine();
            if (line.equals("#")) break;

            StringTokenizer st = new StringTokenizer(line);
            String name = st.nextToken();
            int age = Integer.parseInt(st.nextToken());
            int weight = Integer.parseInt(st.nextToken());

            if (age > 17 || weight >= 80) {
                sb.append(name + " Senior\n");
            } else {
                sb.append(name + " Junior\n");
            }
        }

        System.out.print(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string name;
    while (cin >> name) {
        if (name == "#") break;

        int age, weight;
        cin >> age >> weight;

        if (age > 17 || weight >= 80) {
            cout << name << " Senior\n";
        } else {
            cout << name << " Junior\n";
        }
    }

    return 0;
}
'''
    },
    2084: {
        "python": '''import sys
input = sys.stdin.readline

while True:
    line = input().strip()
    if not line:
        break

    parts = list(map(int, line.split()))
    if parts[0] == 0:
        break

    n, m = parts[0], parts[1]
    edges = []
    idx = 2
    for _ in range(m):
        a, b = parts[idx], parts[idx + 1]
        edges.append((a, b))
        idx += 2

    # Calculate degree sequence
    degree = [0] * (n + 1)
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1

    # Output degree sequence sorted
    deg_seq = sorted(degree[1:n+1], reverse=True)
    print(' '.join(map(str, deg_seq)))
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        String line;
        while ((line = br.readLine()) != null && !line.isEmpty()) {
            StringTokenizer st = new StringTokenizer(line);
            int n = Integer.parseInt(st.nextToken());
            if (n == 0) break;
            int m = Integer.parseInt(st.nextToken());

            int[] degree = new int[n + 1];
            for (int i = 0; i < m; i++) {
                int a = Integer.parseInt(st.nextToken());
                int b = Integer.parseInt(st.nextToken());
                degree[a]++;
                degree[b]++;
            }

            Integer[] degSeq = new Integer[n];
            for (int i = 0; i < n; i++) {
                degSeq[i] = degree[i + 1];
            }
            Arrays.sort(degSeq, Collections.reverseOrder());

            for (int i = 0; i < n; i++) {
                sb.append(degSeq[i]);
                if (i < n - 1) sb.append(" ");
            }
            sb.append("\n");
        }

        System.out.print(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    while (cin >> n && n != 0) {
        cin >> m;

        vector<int> degree(n + 1, 0);
        for (int i = 0; i < m; i++) {
            int a, b;
            cin >> a >> b;
            degree[a]++;
            degree[b]++;
        }

        vector<int> degSeq(degree.begin() + 1, degree.end());
        sort(degSeq.rbegin(), degSeq.rend());

        for (int i = 0; i < n; i++) {
            cout << degSeq[i];
            if (i < n - 1) cout << " ";
        }
        cout << "\n";
    }

    return 0;
}
'''
    },
    2085: {
        "python": '''import sys
input = sys.stdin.readline

A, B = map(int, input().split())
n = int(input())
nums = list(map(int, input().split()))

# Convert from base A to base 10, then to base B
value = 0
for num in nums:
    value = value * A + num

# Convert to base B
if value == 0:
    print(0)
else:
    result = []
    while value > 0:
        result.append(value % B)
        value //= B
    print(' '.join(map(str, result[::-1])))
''',
        "java": '''import java.util.*;
import java.io.*;
import java.math.BigInteger;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int A = Integer.parseInt(st.nextToken());
        int B = Integer.parseInt(st.nextToken());
        int n = Integer.parseInt(br.readLine());
        st = new StringTokenizer(br.readLine());

        BigInteger value = BigInteger.ZERO;
        BigInteger baseA = BigInteger.valueOf(A);

        for (int i = 0; i < n; i++) {
            int num = Integer.parseInt(st.nextToken());
            value = value.multiply(baseA).add(BigInteger.valueOf(num));
        }

        if (value.equals(BigInteger.ZERO)) {
            System.out.println(0);
        } else {
            BigInteger baseB = BigInteger.valueOf(B);
            List<String> result = new ArrayList<>();
            while (value.compareTo(BigInteger.ZERO) > 0) {
                result.add(value.mod(baseB).toString());
                value = value.divide(baseB);
            }
            Collections.reverse(result);
            System.out.println(String.join(" ", result));
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int A, B, n;
    cin >> A >> B >> n;

    vector<long long> nums(n);
    for (int i = 0; i < n; i++) {
        cin >> nums[i];
    }

    // Convert from base A to base 10
    // Using vector for big number
    vector<long long> value = {0};

    for (int i = 0; i < n; i++) {
        // Multiply by A
        long long carry = 0;
        for (int j = 0; j < value.size(); j++) {
            long long prod = value[j] * A + carry;
            value[j] = prod % 1000000000;
            carry = prod / 1000000000;
        }
        while (carry > 0) {
            value.push_back(carry % 1000000000);
            carry /= 1000000000;
        }

        // Add nums[i]
        carry = nums[i];
        for (int j = 0; j < value.size() && carry > 0; j++) {
            long long sum = value[j] + carry;
            value[j] = sum % 1000000000;
            carry = sum / 1000000000;
        }
        while (carry > 0) {
            value.push_back(carry % 1000000000);
            carry /= 1000000000;
        }
    }

    // Check if zero
    bool isZero = true;
    for (auto v : value) if (v != 0) isZero = false;

    if (isZero) {
        cout << 0 << endl;
        return 0;
    }

    // Convert to base B
    vector<long long> result;
    while (!isZero) {
        long long remainder = 0;
        for (int i = value.size() - 1; i >= 0; i--) {
            long long cur = value[i] + remainder * 1000000000;
            value[i] = cur / B;
            remainder = cur % B;
        }
        result.push_back(remainder);

        while (value.size() > 1 && value.back() == 0) {
            value.pop_back();
        }
        isZero = (value.size() == 1 && value[0] == 0);
    }

    reverse(result.begin(), result.end());
    for (int i = 0; i < result.size(); i++) {
        cout << result[i];
        if (i < result.size() - 1) cout << " ";
    }
    cout << endl;

    return 0;
}
'''
    },
    2086: {
        "python": '''import sys
input = sys.stdin.readline

MOD = 1000000000

def matrix_mult(A, B):
    return [
        [(A[0][0] * B[0][0] + A[0][1] * B[1][0]) % MOD, (A[0][0] * B[0][1] + A[0][1] * B[1][1]) % MOD],
        [(A[1][0] * B[0][0] + A[1][1] * B[1][0]) % MOD, (A[1][0] * B[0][1] + A[1][1] * B[1][1]) % MOD]
    ]

def matrix_pow(M, n):
    if n == 1:
        return M
    if n % 2 == 0:
        half = matrix_pow(M, n // 2)
        return matrix_mult(half, half)
    else:
        return matrix_mult(M, matrix_pow(M, n - 1))

def fib_sum(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    # F(1) + F(2) + ... + F(n) = F(n+2) - 1
    M = [[1, 1], [1, 0]]
    result = matrix_pow(M, n + 1)
    return (result[0][0] - 1) % MOD

a, b = map(int, input().split())

# Sum from a to b = Sum(1 to b) - Sum(1 to a-1)
result = (fib_sum(b) - fib_sum(a - 1) + MOD) % MOD
print(result)
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    static final long MOD = 1000000000;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        long a = Long.parseLong(st.nextToken());
        long b = Long.parseLong(st.nextToken());

        long result = (fibSum(b) - fibSum(a - 1) + MOD) % MOD;
        System.out.println(result);
    }

    static long fibSum(long n) {
        if (n <= 0) return 0;
        if (n == 1) return 1;
        long[][] M = {{1, 1}, {1, 0}};
        long[][] result = matrixPow(M, n + 1);
        return (result[0][0] - 1 + MOD) % MOD;
    }

    static long[][] matrixMult(long[][] A, long[][] B) {
        return new long[][] {
            {(A[0][0] * B[0][0] + A[0][1] * B[1][0]) % MOD, (A[0][0] * B[0][1] + A[0][1] * B[1][1]) % MOD},
            {(A[1][0] * B[0][0] + A[1][1] * B[1][0]) % MOD, (A[1][0] * B[0][1] + A[1][1] * B[1][1]) % MOD}
        };
    }

    static long[][] matrixPow(long[][] M, long n) {
        if (n == 1) return M;
        if (n % 2 == 0) {
            long[][] half = matrixPow(M, n / 2);
            return matrixMult(half, half);
        } else {
            return matrixMult(M, matrixPow(M, n - 1));
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
using namespace std;

const long long MOD = 1000000000;
typedef vector<vector<long long>> Matrix;

Matrix matrixMult(Matrix& A, Matrix& B) {
    Matrix C(2, vector<long long>(2));
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            for (int k = 0; k < 2; k++) {
                C[i][j] = (C[i][j] + A[i][k] * B[k][j]) % MOD;
            }
        }
    }
    return C;
}

Matrix matrixPow(Matrix M, long long n) {
    if (n == 1) return M;
    if (n % 2 == 0) {
        Matrix half = matrixPow(M, n / 2);
        return matrixMult(half, half);
    } else {
        Matrix sub = matrixPow(M, n - 1);
        return matrixMult(M, sub);
    }
}

long long fibSum(long long n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    Matrix M = {{1, 1}, {1, 0}};
    Matrix result = matrixPow(M, n + 1);
    return (result[0][0] - 1 + MOD) % MOD;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long a, b;
    cin >> a >> b;

    long long result = (fibSum(b) - fibSum(a - 1) + MOD) % MOD;
    cout << result << endl;

    return 0;
}
'''
    },
    2087: {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
nums = list(map(int, input().split()))
K = int(input())

# Find the n-bit binary password such that
# sum of (bit[i] * nums[i]) = K
# This is essentially finding a subset sum

# Try all 2^n combinations
found = False
for mask in range(1 << n):
    total = 0
    for i in range(n):
        if mask & (1 << (n - 1 - i)):
            total += nums[i]
    if total == K:
        result = ""
        for i in range(n):
            if mask & (1 << (n - 1 - i)):
                result += "1"
            else:
                result += "0"
        print(result)
        found = True
        break

if not found:
    print("NO")
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());
        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) {
            nums[i] = Integer.parseInt(st.nextToken());
        }
        int K = Integer.parseInt(br.readLine());

        boolean found = false;
        for (int mask = 0; mask < (1 << n) && !found; mask++) {
            int total = 0;
            for (int i = 0; i < n; i++) {
                if ((mask & (1 << (n - 1 - i))) != 0) {
                    total += nums[i];
                }
            }
            if (total == K) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < n; i++) {
                    if ((mask & (1 << (n - 1 - i))) != 0) {
                        sb.append("1");
                    } else {
                        sb.append("0");
                    }
                }
                System.out.println(sb);
                found = true;
            }
        }

        if (!found) {
            System.out.println("NO");
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    vector<int> nums(n);
    for (int i = 0; i < n; i++) {
        cin >> nums[i];
    }
    int K;
    cin >> K;

    bool found = false;
    for (int mask = 0; mask < (1 << n) && !found; mask++) {
        int total = 0;
        for (int i = 0; i < n; i++) {
            if (mask & (1 << (n - 1 - i))) {
                total += nums[i];
            }
        }
        if (total == K) {
            for (int i = 0; i < n; i++) {
                if (mask & (1 << (n - 1 - i))) {
                    cout << "1";
                } else {
                    cout << "0";
                }
            }
            cout << endl;
            found = true;
        }
    }

    if (!found) {
        cout << "NO" << endl;
    }

    return 0;
}
'''
    },
    2088: {
        "python": '''import sys
from collections import defaultdict
input = sys.stdin.readline

n = int(input())
tree = defaultdict(list)
parent = [0] * (n + 1)
labels = [''] * (n + 1)

for i in range(1, n + 1):
    parts = input().strip().split()
    labels[i] = parts[0]
    k = int(parts[1])
    for j in range(k):
        child = int(parts[2 + j])
        tree[i].append(child)
        parent[child] = i

# Find root
root = 0
for i in range(1, n + 1):
    if parent[i] == 0:
        root = i
        break

# DFS to find lexicographically smallest path
def dfs(node, path):
    path = path + labels[node]
    if not tree[node]:
        return path

    children_paths = []
    for child in tree[node]:
        children_paths.append(dfs(child, path))

    return min(children_paths)

result = dfs(root, "")
print(result)
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    static List<Integer>[] tree;
    static String[] labels;
    static int n;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        n = Integer.parseInt(br.readLine());

        tree = new ArrayList[n + 1];
        labels = new String[n + 1];
        int[] parent = new int[n + 1];

        for (int i = 0; i <= n; i++) {
            tree[i] = new ArrayList<>();
        }

        for (int i = 1; i <= n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            labels[i] = st.nextToken();
            int k = Integer.parseInt(st.nextToken());
            for (int j = 0; j < k; j++) {
                int child = Integer.parseInt(st.nextToken());
                tree[i].add(child);
                parent[child] = i;
            }
        }

        int root = 0;
        for (int i = 1; i <= n; i++) {
            if (parent[i] == 0) {
                root = i;
                break;
            }
        }

        System.out.println(dfs(root, ""));
    }

    static String dfs(int node, String path) {
        path = path + labels[node];
        if (tree[node].isEmpty()) {
            return path;
        }

        String minPath = null;
        for (int child : tree[node]) {
            String childPath = dfs(child, path);
            if (minPath == null || childPath.compareTo(minPath) < 0) {
                minPath = childPath;
            }
        }
        return minPath;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

int n;
vector<int> tree[10001];
string labels[10001];

string dfs(int node, string path) {
    path += labels[node];
    if (tree[node].empty()) {
        return path;
    }

    string minPath = "";
    for (int child : tree[node]) {
        string childPath = dfs(child, path);
        if (minPath.empty() || childPath < minPath) {
            minPath = childPath;
        }
    }
    return minPath;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;
    vector<int> parent(n + 1, 0);

    for (int i = 1; i <= n; i++) {
        int k;
        cin >> labels[i] >> k;
        for (int j = 0; j < k; j++) {
            int child;
            cin >> child;
            tree[i].push_back(child);
            parent[child] = i;
        }
    }

    int root = 0;
    for (int i = 1; i <= n; i++) {
        if (parent[i] == 0) {
            root = i;
            break;
        }
    }

    cout << dfs(root, "") << endl;
    return 0;
}
'''
    },
    2089: {
        "python": '''import sys
input = sys.stdin.readline

n = int(input())

if n == 0:
    print(0)
else:
    result = []
    while n != 0:
        remainder = n % (-2)
        n //= -2
        if remainder < 0:
            remainder += 2
            n += 1
        result.append(remainder)

    print(''.join(map(str, result[::-1])))
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());

        if (n == 0) {
            System.out.println(0);
            return;
        }

        StringBuilder result = new StringBuilder();
        while (n != 0) {
            int remainder = n % (-2);
            n /= -2;
            if (remainder < 0) {
                remainder += 2;
                n += 1;
            }
            result.append(remainder);
        }

        System.out.println(result.reverse());
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    if (n == 0) {
        cout << 0 << endl;
        return 0;
    }

    string result = "";
    while (n != 0) {
        int remainder = n % (-2);
        n /= -2;
        if (remainder < 0) {
            remainder += 2;
            n += 1;
        }
        result += to_string(remainder);
    }

    reverse(result.begin(), result.end());
    cout << result << endl;
    return 0;
}
'''
    }
}

# Update the problems
count = 0
for i, problem in enumerate(data):
    try:
        oid = int(problem.get('original_id', 0))
    except:
        continue

    if oid in solutions:
        if not problem.get('solutions') or len(problem.get('solutions', [])) == 0:
            problem['solutions'] = [
                {"language": "python", "code": solutions[oid]["python"]},
                {"language": "java", "code": solutions[oid]["java"]},
                {"language": "cpp", "code": solutions[oid]["cpp"]}
            ]
            count += 1
            print(f"Updated problem {oid}")

# Save the checkpoint file
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Batch 9 (2080-2089) completed! Updated {count} problems.")
