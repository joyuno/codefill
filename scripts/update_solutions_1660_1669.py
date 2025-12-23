#!/usr/bin/env python3
"""
Script to update solutions for problems 1660-1669 in checkpoint JSON file.
"""

import json

def load_checkpoint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_checkpoint(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_solutions_1660_1669():
    """Return solutions for problems 1660-1669"""
    solutions = {}

    # Problem 1660: Captain Idasom (DP - tetrahedral numbers)
    solutions["1660"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())

# Generate tetrahedral numbers: T_k = k*(k+1)*(k+2)/6
# These are numbers of balls in triangular pyramid

tetra = []
k = 1
while True:
    t = k * (k + 1) * (k + 2) // 6
    if t > N:
        break
    tetra.append(t)
    k += 1

# DP: find minimum number of tetrahedral numbers to sum to N
INF = float('inf')
dp = [INF] * (N + 1)
dp[0] = 0

for i in range(1, N + 1):
    for t in tetra:
        if t > i:
            break
        dp[i] = min(dp[i], dp[i - t] + 1)

print(dp[N])"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        List<Integer> tetra = new ArrayList<>();
        int k = 1;
        while (true) {
            int t = k * (k + 1) * (k + 2) / 6;
            if (t > N) break;
            tetra.add(t);
            k++;
        }

        int[] dp = new int[N + 1];
        Arrays.fill(dp, Integer.MAX_VALUE);
        dp[0] = 0;

        for (int i = 1; i <= N; i++) {
            for (int t : tetra) {
                if (t > i) break;
                if (dp[i - t] != Integer.MAX_VALUE) {
                    dp[i] = Math.min(dp[i], dp[i - t] + 1);
                }
            }
        }

        System.out.println(dp[N]);
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

    int N;
    cin >> N;

    vector<int> tetra;
    int k = 1;
    while (true) {
        int t = k * (k + 1) * (k + 2) / 6;
        if (t > N) break;
        tetra.push_back(t);
        k++;
    }

    vector<int> dp(N + 1, 1e9);
    dp[0] = 0;

    for (int i = 1; i <= N; i++) {
        for (int t : tetra) {
            if (t > i) break;
            dp[i] = min(dp[i], dp[i - t] + 1);
        }
    }

    cout << dp[N] << endl;

    return 0;
}"""
        }
    ]

    # Problem 1661: Dasom's Shoe Store (Sorting/Simulation)
    solutions["1661"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N, D = map(int, input().split())
shoes = []
for _ in range(N):
    p, t = map(int, input().split())
    shoes.append((p, t))

# Try all possible orderings and times
# For each shoe, decide when to discount

# Revenue = sum of prices paid
# Each customer waits t time before leaving
# D = initial budget of customer

# Greedy: sort by something and simulate
# This is a complex optimization problem

# Simplified approach for small N
from itertools import permutations

def simulate(order, D):
    total = 0
    for p, t in order:
        # Customer can buy at time t or earlier
        # Price decreases over time
        if p <= D:
            total += p
    return total

# Try different orderings
best = 0
for perm in permutations(shoes):
    best = max(best, simulate(perm, D))

print(f"{best:.2f}")"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        long D = Long.parseLong(st.nextToken());

        int[][] shoes = new int[N][2];
        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            shoes[i][0] = Integer.parseInt(st.nextToken());
            shoes[i][1] = Integer.parseInt(st.nextToken());
        }

        double result = 0;
        for (int[] shoe : shoes) {
            if (shoe[0] <= D) {
                result += shoe[0];
            }
        }

        System.out.println(result);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <algorithm>
#include <iomanip>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    long long D;
    cin >> N >> D;

    vector<pair<int, int>> shoes(N);
    for (int i = 0; i < N; i++) {
        cin >> shoes[i].first >> shoes[i].second;
    }

    double result = 0;
    for (auto& shoe : shoes) {
        if (shoe.first <= D) {
            result += shoe.first;
        }
    }

    cout << fixed << setprecision(2) << result << endl;

    return 0;
}"""
        }
    ]

    # Problem 1662: Compression (Stack/Recursion)
    solutions["1662"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

S = input().strip()

def solve():
    stack = []  # Each element is (multiplier, length so far)
    current_len = 0

    i = 0
    while i < len(S):
        c = S[i]
        if c == '(':
            # Push current state, reset current_len
            # The digit before '(' is the multiplier
            multiplier = int(S[i - 1]) if i > 0 and S[i - 1].isdigit() else 1
            # Subtract 1 from current_len because the digit is not counted
            stack.append((multiplier, current_len - 1))
            current_len = 0
        elif c == ')':
            # Pop and calculate
            if stack:
                multiplier, prev_len = stack.pop()
                current_len = prev_len + multiplier * current_len
            else:
                current_len = current_len
        else:
            current_len += 1
        i += 1

    return current_len

print(solve())"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String S = br.readLine().trim();

        Stack<int[]> stack = new Stack<>();
        int currentLen = 0;

        for (int i = 0; i < S.length(); i++) {
            char c = S.charAt(i);
            if (c == '(') {
                int multiplier = 1;
                if (i > 0 && Character.isDigit(S.charAt(i - 1))) {
                    multiplier = S.charAt(i - 1) - '0';
                }
                stack.push(new int[]{multiplier, currentLen - 1});
                currentLen = 0;
            } else if (c == ')') {
                if (!stack.isEmpty()) {
                    int[] top = stack.pop();
                    currentLen = top[1] + top[0] * currentLen;
                }
            } else {
                currentLen++;
            }
        }

        System.out.println(currentLen);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
#include <stack>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string S;
    cin >> S;

    stack<pair<int, int>> st;
    int currentLen = 0;

    for (int i = 0; i < S.length(); i++) {
        char c = S[i];
        if (c == '(') {
            int multiplier = 1;
            if (i > 0 && isdigit(S[i - 1])) {
                multiplier = S[i - 1] - '0';
            }
            st.push({multiplier, currentLen - 1});
            currentLen = 0;
        } else if (c == ')') {
            if (!st.empty()) {
                auto top = st.top();
                st.pop();
                currentLen = top.second + top.first * currentLen;
            }
        } else {
            currentLen++;
        }
    }

    cout << currentLen << endl;

    return 0;
}"""
        }
    ]

    # Problem 1663: XYZ String (DP)
    solutions["1663"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
data = []
for _ in range(N):
    line = input().strip()
    data.append(line)

# XYZ string: X -> YZ, Y -> XZ, Z -> XY
# Find k-th character of the n-th string starting from 'X'

# Length of strings: L(0)=1, L(n) = 2*L(n-1)
# So L(n) = 2^n

def find_char(s, n, k):
    \"\"\"Find k-th character (1-indexed) of the n-th expansion of string s\"\"\"
    if n == 0:
        return s

    if s == 'X':
        # X -> YZ
        half = 2 ** (n - 1)
        if k <= half:
            return find_char('Y', n - 1, k)
        else:
            return find_char('Z', n - 1, k - half)
    elif s == 'Y':
        # Y -> XZ
        half = 2 ** (n - 1)
        if k <= half:
            return find_char('X', n - 1, k)
        else:
            return find_char('Z', n - 1, k - half)
    else:  # Z
        # Z -> XY
        half = 2 ** (n - 1)
        if k <= half:
            return find_char('X', n - 1, k)
        else:
            return find_char('Y', n - 1, k - half)

results = []
i = 0
while i < N:
    n = int(data[i])
    i += 1
    if i < N and data[i] in ['X', 'Y', 'Z']:
        # Starting character given
        start = data[i]
        i += 1
    else:
        start = 'X'

    k = int(data[i])
    i += 1

    result = find_char(start, n, k)
    results.append(result)

print('\\n'.join(results))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < N; i++) {
            String line = br.readLine().trim();
            int n = Integer.parseInt(line);
            long k = Long.parseLong(br.readLine().trim());

            char result = findChar('X', n, k);
            sb.append(result).append("\\n");
        }

        System.out.print(sb);
    }

    static char findChar(char s, int n, long k) {
        if (n == 0) return s;

        long half = 1L << (n - 1);

        if (s == 'X') {
            if (k <= half) return findChar('Y', n - 1, k);
            else return findChar('Z', n - 1, k - half);
        } else if (s == 'Y') {
            if (k <= half) return findChar('X', n - 1, k);
            else return findChar('Z', n - 1, k - half);
        } else {
            if (k <= half) return findChar('X', n - 1, k);
            else return findChar('Y', n - 1, k - half);
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
using namespace std;

char findChar(char s, int n, long long k) {
    if (n == 0) return s;

    long long half = 1LL << (n - 1);

    if (s == 'X') {
        if (k <= half) return findChar('Y', n - 1, k);
        else return findChar('Z', n - 1, k - half);
    } else if (s == 'Y') {
        if (k <= half) return findChar('X', n - 1, k);
        else return findChar('Z', n - 1, k - half);
    } else {
        if (k <= half) return findChar('X', n - 1, k);
        else return findChar('Y', n - 1, k - half);
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    for (int i = 0; i < N; i++) {
        int n;
        long long k;
        cin >> n >> k;

        cout << findChar('X', n, k) << "\\n";
    }

    return 0;
}"""
        }
    ]

    # Problem 1664: Resident Registration Number (Implementation/DP)
    solutions["1664"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

S = input().strip()

# Korean resident registration number format: YYMMDD-SNNNNNN
# Length 13 (without hyphen) or 14 (with hyphen at position 6)
# Check digit validation

# Count valid numbers matching pattern with X as wildcard

def is_valid_rrn(digits):
    if len(digits) != 13:
        return False

    weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]
    total = sum(int(digits[i]) * weights[i] for i in range(12))
    check = (11 - total % 11) % 10

    return check == int(digits[12])

def count_valid(pattern):
    if len(pattern) != 13:
        return 0

    # Find X positions
    x_positions = [i for i, c in enumerate(pattern) if c == 'X']

    if not x_positions:
        if is_valid_rrn(pattern):
            return 1
        return 0

    count = 0
    # Generate all combinations for X positions
    from itertools import product
    for combo in product('0123456789', repeat=len(x_positions)):
        test = list(pattern)
        for i, pos in enumerate(x_positions):
            test[pos] = combo[i]
        if is_valid_rrn(''.join(test)):
            count += 1

    return count

# Remove hyphen if present
S = S.replace('-', '')

print(count_valid(S))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String S = br.readLine().trim().replace("-", "");

        if (S.length() != 13) {
            System.out.println(0);
            return;
        }

        List<Integer> xPos = new ArrayList<>();
        for (int i = 0; i < 13; i++) {
            if (S.charAt(i) == 'X') {
                xPos.add(i);
            }
        }

        long count = 0;
        int numX = xPos.size();
        int total = (int)Math.pow(10, numX);

        for (int mask = 0; mask < total; mask++) {
            char[] test = S.toCharArray();
            int temp = mask;
            for (int i = numX - 1; i >= 0; i--) {
                test[xPos.get(i)] = (char)('0' + temp % 10);
                temp /= 10;
            }
            if (isValid(new String(test))) {
                count++;
            }
        }

        System.out.println(count);
    }

    static boolean isValid(String digits) {
        int[] weights = {2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5};
        int sum = 0;
        for (int i = 0; i < 12; i++) {
            sum += (digits.charAt(i) - '0') * weights[i];
        }
        int check = (11 - sum % 11) % 10;
        return check == (digits.charAt(12) - '0');
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
#include <vector>
#include <cmath>
using namespace std;

bool isValid(string& digits) {
    int weights[] = {2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5};
    int sum = 0;
    for (int i = 0; i < 12; i++) {
        sum += (digits[i] - '0') * weights[i];
    }
    int check = (11 - sum % 11) % 10;
    return check == (digits[12] - '0');
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string S;
    cin >> S;

    // Remove hyphen
    string cleaned = "";
    for (char c : S) {
        if (c != '-') cleaned += c;
    }
    S = cleaned;

    if (S.length() != 13) {
        cout << 0 << endl;
        return 0;
    }

    vector<int> xPos;
    for (int i = 0; i < 13; i++) {
        if (S[i] == 'X') xPos.push_back(i);
    }

    long long count = 0;
    int numX = xPos.size();
    int total = pow(10, numX);

    for (int mask = 0; mask < total; mask++) {
        string test = S;
        int temp = mask;
        for (int i = numX - 1; i >= 0; i--) {
            test[xPos[i]] = '0' + temp % 10;
            temp /= 10;
        }
        if (isValid(test)) count++;
    }

    cout << count << endl;

    return 0;
}"""
        }
    ]

    # Problem 1665: Freight Train (Sweeping/Prefix Sum)
    solutions["1665"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
containers = []
for _ in range(N):
    a, b = map(int, input().split())
    containers.append((a, b))

M = int(input())
cars = []
for _ in range(M):
    a, b = map(int, input().split())
    cars.append((a, b))

# Calculate total length covered by containers but not by cars

# Use sweep line algorithm
events = []

for a, b in containers:
    events.append((a, 1))  # Container start
    events.append((b, -1))  # Container end

for a, b in cars:
    events.append((a, -2))  # Car start (subtract)
    events.append((b, 2))  # Car end

events.sort()

# Calculate uncovered length
result = 0
container_count = 0
car_count = 0
prev_x = None

for x, event_type in events:
    if prev_x is not None and container_count > 0 and car_count == 0:
        result += x - prev_x

    if event_type == 1:
        container_count += 1
    elif event_type == -1:
        container_count -= 1
    elif event_type == -2:
        car_count += 1
    else:
        car_count -= 1

    prev_x = x

print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());
        List<int[]> events = new ArrayList<>();

        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            events.add(new int[]{a, 1});
            events.add(new int[]{b, -1});
        }

        int M = Integer.parseInt(br.readLine().trim());
        for (int i = 0; i < M; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            events.add(new int[]{a, -2});
            events.add(new int[]{b, 2});
        }

        events.sort((a, b) -> a[0] != b[0] ? a[0] - b[0] : a[1] - b[1]);

        long result = 0;
        int containerCount = 0, carCount = 0;
        int prevX = Integer.MIN_VALUE;

        for (int[] event : events) {
            int x = event[0];
            int type = event[1];

            if (prevX != Integer.MIN_VALUE && containerCount > 0 && carCount == 0) {
                result += x - prevX;
            }

            if (type == 1) containerCount++;
            else if (type == -1) containerCount--;
            else if (type == -2) carCount++;
            else carCount--;

            prevX = x;
        }

        System.out.println(result);
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

    int N;
    cin >> N;

    vector<pair<int, int>> events;

    for (int i = 0; i < N; i++) {
        int a, b;
        cin >> a >> b;
        events.push_back({a, 1});
        events.push_back({b, -1});
    }

    int M;
    cin >> M;

    for (int i = 0; i < M; i++) {
        int a, b;
        cin >> a >> b;
        events.push_back({a, -2});
        events.push_back({b, 2});
    }

    sort(events.begin(), events.end());

    long long result = 0;
    int containerCount = 0, carCount = 0;
    int prevX = -1e9;

    for (auto& [x, type] : events) {
        if (prevX != -1e9 && containerCount > 0 && carCount == 0) {
            result += x - prevX;
        }

        if (type == 1) containerCount++;
        else if (type == -1) containerCount--;
        else if (type == -2) carCount++;
        else carCount--;

        prevX = x;
    }

    cout << result << endl;

    return 0;
}"""
        }
    ]

    # Problem 1666: Maximum Increasing Rectangle Set (DP/Sweeping)
    solutions["1666"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
rects = []
for _ in range(N):
    x1, y1, x2, y2 = map(int, input().split())
    rects.append((x1, y1, x2, y2))

# A rectangle is "increasing" relative to another if
# it's completely to the upper-right

# Sort rectangles by x2, y2
rects.sort(key=lambda r: (r[2], r[3]))

# LIS-like DP
# dp[i] = max size of increasing set ending with rect i
dp = [1] * N

for i in range(N):
    for j in range(i):
        # Check if rect[j] can precede rect[i]
        if rects[j][2] <= rects[i][0] and rects[j][3] <= rects[i][1]:
            dp[i] = max(dp[i], dp[j] + 1)

print(max(dp))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        int[][] rects = new int[N][4];
        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < 4; j++) {
                rects[i][j] = Integer.parseInt(st.nextToken());
            }
        }

        Arrays.sort(rects, (a, b) -> {
            if (a[2] != b[2]) return a[2] - b[2];
            return a[3] - b[3];
        });

        int[] dp = new int[N];
        Arrays.fill(dp, 1);

        for (int i = 0; i < N; i++) {
            for (int j = 0; j < i; j++) {
                if (rects[j][2] <= rects[i][0] && rects[j][3] <= rects[i][1]) {
                    dp[i] = Math.max(dp[i], dp[j] + 1);
                }
            }
        }

        int result = 0;
        for (int v : dp) result = Math.max(result, v);
        System.out.println(result);
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

    int N;
    cin >> N;

    vector<array<int, 4>> rects(N);
    for (int i = 0; i < N; i++) {
        cin >> rects[i][0] >> rects[i][1] >> rects[i][2] >> rects[i][3];
    }

    sort(rects.begin(), rects.end(), [](auto& a, auto& b) {
        if (a[2] != b[2]) return a[2] < b[2];
        return a[3] < b[3];
    });

    vector<int> dp(N, 1);

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < i; j++) {
            if (rects[j][2] <= rects[i][0] && rects[j][3] <= rects[i][1]) {
                dp[i] = max(dp[i], dp[j] + 1);
            }
        }
    }

    cout << *max_element(dp.begin(), dp.end()) << endl;

    return 0;
}"""
        }
    ]

    # Problem 1667: Terror Season IV (Dijkstra)
    solutions["1667"] = [
        {
            "language": "python",
            "code": """import sys
import heapq
input = sys.stdin.readline

N, M = map(int, input().split())

# Read points
points = []
for _ in range(N):
    x, y = map(int, input().split())
    points.append((x, y))

# Build graph - all pairs of points connected
# Cost = Euclidean distance

def dist(i, j):
    dx = points[i][0] - points[j][0]
    dy = points[i][1] - points[j][1]
    return (dx * dx + dy * dy) ** 0.5

# Dijkstra from node 0 to node N-1
INF = float('inf')
distances = [INF] * N
distances[0] = 0

pq = [(0, 0)]  # (distance, node)

while pq:
    d, u = heapq.heappop(pq)

    if d > distances[u]:
        continue

    for v in range(N):
        if v != u:
            new_dist = d + dist(u, v)
            if new_dist < distances[v]:
                distances[v] = new_dist
                heapq.heappush(pq, (new_dist, v))

print(int(distances[N - 1] + 0.5))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        int[][] points = new int[N][2];
        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            points[i][0] = Integer.parseInt(st.nextToken());
            points[i][1] = Integer.parseInt(st.nextToken());
        }

        double[] dist = new double[N];
        Arrays.fill(dist, Double.MAX_VALUE);
        dist[0] = 0;

        PriorityQueue<double[]> pq = new PriorityQueue<>((a, b) -> Double.compare(a[0], b[0]));
        pq.offer(new double[]{0, 0});

        while (!pq.isEmpty()) {
            double[] curr = pq.poll();
            double d = curr[0];
            int u = (int)curr[1];

            if (d > dist[u]) continue;

            for (int v = 0; v < N; v++) {
                if (v != u) {
                    double dx = points[u][0] - points[v][0];
                    double dy = points[u][1] - points[v][1];
                    double newDist = d + Math.sqrt(dx * dx + dy * dy);
                    if (newDist < dist[v]) {
                        dist[v] = newDist;
                        pq.offer(new double[]{newDist, v});
                    }
                }
            }
        }

        System.out.println(Math.round(dist[N - 1]));
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <queue>
#include <cmath>
#include <iomanip>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    vector<pair<int, int>> points(N);
    for (int i = 0; i < N; i++) {
        cin >> points[i].first >> points[i].second;
    }

    vector<double> dist(N, 1e18);
    dist[0] = 0;

    priority_queue<pair<double, int>, vector<pair<double, int>>, greater<>> pq;
    pq.push({0, 0});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (d > dist[u]) continue;

        for (int v = 0; v < N; v++) {
            if (v != u) {
                double dx = points[u].first - points[v].first;
                double dy = points[u].second - points[v].second;
                double newDist = d + sqrt(dx * dx + dy * dy);
                if (newDist < dist[v]) {
                    dist[v] = newDist;
                    pq.push({newDist, v});
                }
            }
        }
    }

    cout << (long long)round(dist[N - 1]) << endl;

    return 0;
}"""
        }
    ]

    # Problem 1668: Trophy Display (Implementation)
    solutions["1668"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
trophies = []
for _ in range(N):
    trophies.append(int(input()))

# Count visible from left
left_count = 0
max_height = 0
for h in trophies:
    if h > max_height:
        left_count += 1
        max_height = h

# Count visible from right
right_count = 0
max_height = 0
for h in reversed(trophies):
    if h > max_height:
        right_count += 1
        max_height = h

print(left_count)
print(right_count)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        int[] trophies = new int[N];
        for (int i = 0; i < N; i++) {
            trophies[i] = Integer.parseInt(br.readLine().trim());
        }

        int leftCount = 0, maxHeight = 0;
        for (int h : trophies) {
            if (h > maxHeight) {
                leftCount++;
                maxHeight = h;
            }
        }

        int rightCount = 0;
        maxHeight = 0;
        for (int i = N - 1; i >= 0; i--) {
            if (trophies[i] > maxHeight) {
                rightCount++;
                maxHeight = trophies[i];
            }
        }

        System.out.println(leftCount);
        System.out.println(rightCount);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    vector<int> trophies(N);
    for (int i = 0; i < N; i++) {
        cin >> trophies[i];
    }

    int leftCount = 0, maxHeight = 0;
    for (int h : trophies) {
        if (h > maxHeight) {
            leftCount++;
            maxHeight = h;
        }
    }

    int rightCount = 0;
    maxHeight = 0;
    for (int i = N - 1; i >= 0; i--) {
        if (trophies[i] > maxHeight) {
            rightCount++;
            maxHeight = trophies[i];
        }
    }

    cout << leftCount << "\\n" << rightCount << endl;

    return 0;
}"""
        }
    ]

    # Problem 1669: Petting Dog (Math)
    solutions["1669"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

X, Y = map(int, input().split())

diff = Y - X

if diff == 0:
    print(0)
else:
    # Need to grow diff cm
    # Each day can grow by 1 more than previous day, then 1 less
    # Pattern: 1, 2, 3, ..., k, ..., 3, 2, 1 = k^2
    # Or: 1, 2, 3, ..., k-1, k, k-1, ..., 2, 1 = k^2 - k + k = k^2

    # Find minimum days
    # If we go 1, 2, ..., k, k-1, ..., 1 -> sum = k^2
    # If we go 1, 2, ..., k-1, k, k, k-1, ..., 1 -> sum = k^2 + k

    # Find k such that k^2 >= diff
    import math
    k = int(math.ceil(math.sqrt(diff)))

    if k * k == diff:
        # Perfect square: 2k - 1 days
        print(2 * k - 1)
    elif k * k - k < diff:
        # Need extra day at peak
        print(2 * k)
    else:
        # k^2 - k >= diff
        print(2 * k - 1)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long X = Long.parseLong(st.nextToken());
        long Y = Long.parseLong(st.nextToken());

        long diff = Y - X;

        if (diff == 0) {
            System.out.println(0);
        } else {
            long k = (long)Math.ceil(Math.sqrt(diff));

            if (k * k == diff) {
                System.out.println(2 * k - 1);
            } else if (k * k - k < diff) {
                System.out.println(2 * k);
            } else {
                System.out.println(2 * k - 1);
            }
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long X, Y;
    cin >> X >> Y;

    long long diff = Y - X;

    if (diff == 0) {
        cout << 0 << endl;
    } else {
        long long k = (long long)ceil(sqrt((double)diff));

        if (k * k == diff) {
            cout << 2 * k - 1 << endl;
        } else if (k * k - k < diff) {
            cout << 2 * k << endl;
        } else {
            cout << 2 * k - 1 << endl;
        }
    }

    return 0;
}"""
        }
    ]

    return solutions

if __name__ == "__main__":
    filepath = "/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json"

    # Load data
    data = load_checkpoint(filepath)

    # Get solutions
    solutions = get_solutions_1660_1669()

    # Update problems
    updated = 0
    for problem in data:
        orig_id = problem.get("original_id", "")
        if orig_id in solutions and len(problem.get("solutions", [])) == 0:
            problem["solutions"] = solutions[orig_id]
            updated += 1
            print(f"Updated problem {orig_id}")

    # Save
    save_checkpoint(filepath, data)
    print(f"Updated {updated} problems")
