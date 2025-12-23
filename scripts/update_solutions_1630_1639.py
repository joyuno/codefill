#!/usr/bin/env python3
"""
Script to update solutions for problems 1630-1639 in checkpoint JSON file.
"""

import json

def load_checkpoint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_checkpoint(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_solutions_1630_1639():
    """Return solutions for problems 1630-1639"""
    solutions = {}

    # Problem 1630: LCM of 1 to N (Number Theory)
    solutions["1630"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

def sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

MOD = 987654321

N = int(input())
primes = sieve(N)

result = 1
for p in primes:
    # Find the highest power of p <= N
    power = p
    while power * p <= N:
        power *= p
    result = (result * power) % MOD

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

        long MOD = 987654321L;

        boolean[] isPrime = new boolean[N + 1];
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;

        for (int i = 2; i * i <= N; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j <= N; j += i) {
                    isPrime[j] = false;
                }
            }
        }

        long result = 1;
        for (int p = 2; p <= N; p++) {
            if (isPrime[p]) {
                long power = p;
                while (power * p <= N) {
                    power *= p;
                }
                result = (result * power) % MOD;
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
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    long long MOD = 987654321LL;

    vector<bool> isPrime(N + 1, true);
    isPrime[0] = isPrime[1] = false;

    for (int i = 2; i * i <= N; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j <= N; j += i) {
                isPrime[j] = false;
            }
        }
    }

    long long result = 1;
    for (int p = 2; p <= N; p++) {
        if (isPrime[p]) {
            long long power = p;
            while (power * p <= N) {
                power *= p;
            }
            result = (result * power) % MOD;
        }
    }

    cout << result << endl;

    return 0;
}"""
        }
    ]

    # Problem 1631: Hanoi Tower State (Recursion/Math)
    solutions["1631"] = [
        {
            "language": "python",
            "code": """import sys
sys.setrecursionlimit(100000)
input = sys.stdin.readline

def target_to_moves(target, n, src, dst, aux):
    \"\"\"Calculate minimum moves to reach target state from all disks on src\"\"\"
    if n == 0:
        return 0

    # Where should disk n be?
    disk_pos = target[n - 1]

    if disk_pos == src:
        # Disk n stays at src, just move smaller disks to proper places
        return target_to_moves(target, n - 1, src, dst, aux)
    elif disk_pos == dst:
        # Need to move n-1 disks to aux, then disk n to dst
        return (1 << (n - 1)) + target_to_moves(target, n - 1, aux, dst, src)
    else:  # disk_pos == aux
        # Need to move n-1 disks to dst, then disk n to aux
        return (1 << (n - 1)) + target_to_moves(target, n - 1, dst, aux, src)

def state_at_move(m, n, src, dst, aux, result):
    \"\"\"Find state after m moves when moving n disks from src to dst\"\"\"
    if n == 0:
        return

    # Total moves to move n disks = 2^n - 1
    # First 2^(n-1) - 1 moves: move n-1 disks from src to aux
    # Move 2^(n-1): move disk n from src to dst
    # Last 2^(n-1) - 1 moves: move n-1 disks from aux to dst

    half = 1 << (n - 1)

    if m < half:
        # Still in first phase
        result[n - 1] = src
        state_at_move(m, n - 1, src, aux, dst, result)
    elif m == half:
        # Just moved disk n
        result[n - 1] = dst
        state_at_move(half - 1, n - 1, src, aux, dst, result)
    else:
        # In second phase
        result[n - 1] = dst
        state_at_move(m - half, n - 1, aux, dst, src, result)

line = input().split()
N, M = int(line[0]), int(line[1])
target_str = input().strip()

target = []
for c in target_str:
    target.append(c)

# Calculate minimum moves to reach target from initial state (all on A)
min_moves = target_to_moves(target, N, 'A', 'C', 'B')

# Now find state after M moves
result = ['A'] * N
state_at_move(M, N, 'A', 'C', 'B', result)

print(''.join(result))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static char[] result;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        long M = Long.parseLong(st.nextToken());
        String target = br.readLine().trim();

        result = new char[N];
        Arrays.fill(result, 'A');

        stateAtMove(M, N, 'A', 'C', 'B');

        System.out.println(new String(result));
    }

    static void stateAtMove(long m, int n, char src, char dst, char aux) {
        if (n == 0) return;

        long half = 1L << (n - 1);

        if (m < half) {
            result[n - 1] = src;
            stateAtMove(m, n - 1, src, aux, dst);
        } else if (m == half) {
            result[n - 1] = dst;
            stateAtMove(half - 1, n - 1, src, aux, dst);
        } else {
            result[n - 1] = dst;
            stateAtMove(m - half, n - 1, aux, dst, src);
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
using namespace std;

string result;

void stateAtMove(long long m, int n, char src, char dst, char aux) {
    if (n == 0) return;

    long long half = 1LL << (n - 1);

    if (m < half) {
        result[n - 1] = src;
        stateAtMove(m, n - 1, src, aux, dst);
    } else if (m == half) {
        result[n - 1] = dst;
        stateAtMove(half - 1, n - 1, src, aux, dst);
    } else {
        result[n - 1] = dst;
        stateAtMove(m - half, n - 1, aux, dst, src);
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    long long M;
    cin >> N >> M;

    string target;
    cin >> target;

    result = string(N, 'A');
    stateAtMove(M, N, 'A', 'C', 'B');

    cout << result << endl;

    return 0;
}"""
        }
    ]

    # Problem 1632: Line Fighter (Median of lines)
    solutions["1632"] = [
        {
            "language": "python",
            "code": """import sys
from fractions import Fraction
input = sys.stdin.readline

def get_median_at_x(lines, x):
    values = sorted([a * x + b for a, b in lines])
    return values[len(values) // 2]

line = input().split()
N, K = int(line[0]), int(line[1])

lines = []
for _ in range(N):
    a, b = map(int, input().split())
    lines.append((a, b))

# Find all x where median changes (intersection points)
events = set()
for i in range(N):
    for j in range(i + 1, N):
        a1, b1 = lines[i]
        a2, b2 = lines[j]
        if a1 != a2:
            x = Fraction(b2 - b1, a1 - a2)
            events.add(x)

events = sorted(events)

# Binary search for where median = K starts and ends
def count_less_equal(lines, x, k):
    return sum(1 for a, b in lines if a * x + b <= k)

# Find leftmost x where median >= K
# Find rightmost x where median <= K

# Check at -inf and +inf
# At x -> -inf, lines with largest a dominate (lowest value)
# At x -> +inf, lines with smallest a dominate (highest value)

# Sort lines by slope
sorted_by_slope = sorted(lines, key=lambda p: p[0])

# At x -> -inf: median is the (N//2 + 1)-th line when sorted by value at -inf
# Value at -inf is dominated by slope: lower slope = higher value

# At x -> +inf: median is the (N//2 + 1)-th line
# Value at +inf is dominated by slope: higher slope = higher value

# We need to find interval where g(x) = K

# Simple approach: check at critical points and find interval
critical = sorted(set(events))

def median_at(x):
    vals = sorted([a * x + b for a, b in lines])
    return vals[N // 2]

# Check at boundaries
eps = Fraction(1, 1000000)

result_start = None
result_end = None

# Check if median ever equals K
found = False

# Check at each interval
prev_x = None
for x in critical:
    mid = median_at(x)
    if mid == K:
        found = True
        if result_start is None:
            result_start = x
        result_end = x

    if prev_x is not None:
        mid_x = (prev_x + x) / 2
        mid_val = median_at(mid_x)
        if mid_val == K:
            found = True
            if result_start is None:
                result_start = prev_x
            result_end = x
    prev_x = x

# Check at -inf and +inf
if not found or result_start is None:
    # Check if constant
    slopes = [a for a, b in lines]
    if all(s == 0 for s in slopes):
        values = sorted([b for a, b in lines])
        if values[N // 2] == K:
            print("-inf +inf")
        else:
            print("impossible")
    else:
        print("impossible")
else:
    start_str = f"{float(result_start):.3f}" if result_start is not None else "-inf"
    end_str = f"{float(result_end):.3f}" if result_end is not None else "+inf"
    print(f"{start_str} {end_str}")"""
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
        int K = Integer.parseInt(st.nextToken());

        int[][] lines = new int[N][2];
        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            lines[i][0] = Integer.parseInt(st.nextToken());
            lines[i][1] = Integer.parseInt(st.nextToken());
        }

        // Find intersection points
        TreeSet<Double> events = new TreeSet<>();
        for (int i = 0; i < N; i++) {
            for (int j = i + 1; j < N; j++) {
                int a1 = lines[i][0], b1 = lines[i][1];
                int a2 = lines[j][0], b2 = lines[j][1];
                if (a1 != a2) {
                    double x = (double)(b2 - b1) / (a1 - a2);
                    events.add(x);
                }
            }
        }

        Double startX = null, endX = null;

        for (double x : events) {
            double[] vals = new double[N];
            for (int i = 0; i < N; i++) {
                vals[i] = lines[i][0] * x + lines[i][1];
            }
            Arrays.sort(vals);
            if (Math.abs(vals[N / 2] - K) < 1e-9) {
                if (startX == null) startX = x;
                endX = x;
            }
        }

        if (startX == null) {
            System.out.println("impossible");
        } else {
            System.out.printf("%.3f %.3f%n", startX, endX);
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
#include <cmath>
#include <iomanip>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, K;
    cin >> N >> K;

    vector<pair<int, int>> lines(N);
    for (int i = 0; i < N; i++) {
        cin >> lines[i].first >> lines[i].second;
    }

    set<double> events;
    for (int i = 0; i < N; i++) {
        for (int j = i + 1; j < N; j++) {
            int a1 = lines[i].first, b1 = lines[i].second;
            int a2 = lines[j].first, b2 = lines[j].second;
            if (a1 != a2) {
                double x = (double)(b2 - b1) / (a1 - a2);
                events.insert(x);
            }
        }
    }

    double startX = -1e18, endX = -1e18;
    bool found = false;

    for (double x : events) {
        vector<double> vals(N);
        for (int i = 0; i < N; i++) {
            vals[i] = lines[i].first * x + lines[i].second;
        }
        sort(vals.begin(), vals.end());
        if (abs(vals[N / 2] - K) < 1e-9) {
            if (!found) {
                startX = x;
                found = true;
            }
            endX = x;
        }
    }

    if (!found) {
        cout << "impossible" << endl;
    } else {
        cout << fixed << setprecision(3) << startX << " " << endX << endl;
    }

    return 0;
}"""
        }
    ]

    # Problem 1633: Best Team (DP)
    solutions["1633"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

players = []
try:
    while True:
        line = input().strip()
        if not line:
            break
        w, b = map(int, line.split())
        players.append((w, b))
except:
    pass

n = len(players)

# dp[i][j][k] = max score using first i players, j white, k black
# Too much memory, use 2D rolling
# dp[j][k] = max score with j white players and k black players

dp = [[-1] * 16 for _ in range(16)]
dp[0][0] = 0

for i in range(n):
    w, b = players[i]
    # Go backwards to avoid using same player twice
    new_dp = [row[:] for row in dp]

    for j in range(16):
        for k in range(16):
            if dp[j][k] < 0:
                continue

            # Don't pick this player
            # Already in new_dp

            # Pick as white player
            if j < 15:
                new_dp[j + 1][k] = max(new_dp[j + 1][k], dp[j][k] + w)

            # Pick as black player
            if k < 15:
                new_dp[j][k + 1] = max(new_dp[j][k + 1], dp[j][k] + b)

    dp = new_dp

print(dp[15][15])"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        List<int[]> players = new ArrayList<>();

        String line;
        while ((line = br.readLine()) != null && !line.isEmpty()) {
            StringTokenizer st = new StringTokenizer(line);
            int w = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            players.add(new int[]{w, b});
        }

        int n = players.size();

        int[][] dp = new int[16][16];
        for (int[] row : dp) Arrays.fill(row, -1);
        dp[0][0] = 0;

        for (int i = 0; i < n; i++) {
            int w = players.get(i)[0];
            int b = players.get(i)[1];

            int[][] newDp = new int[16][16];
            for (int j = 0; j < 16; j++) {
                newDp[j] = dp[j].clone();
            }

            for (int j = 0; j < 16; j++) {
                for (int k = 0; k < 16; k++) {
                    if (dp[j][k] < 0) continue;

                    if (j < 15) {
                        newDp[j + 1][k] = Math.max(newDp[j + 1][k], dp[j][k] + w);
                    }
                    if (k < 15) {
                        newDp[j][k + 1] = Math.max(newDp[j][k + 1], dp[j][k] + b);
                    }
                }
            }

            dp = newDp;
        }

        System.out.println(dp[15][15]);
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

    vector<pair<int, int>> players;
    int w, b;
    while (cin >> w >> b) {
        players.push_back({w, b});
    }

    int n = players.size();

    vector<vector<int>> dp(16, vector<int>(16, -1));
    dp[0][0] = 0;

    for (int i = 0; i < n; i++) {
        int pw = players[i].first;
        int pb = players[i].second;

        vector<vector<int>> newDp = dp;

        for (int j = 0; j < 16; j++) {
            for (int k = 0; k < 16; k++) {
                if (dp[j][k] < 0) continue;

                if (j < 15) {
                    newDp[j + 1][k] = max(newDp[j + 1][k], dp[j][k] + pw);
                }
                if (k < 15) {
                    newDp[j][k + 1] = max(newDp[j][k + 1], dp[j][k] + pb);
                }
            }
        }

        dp = newDp;
    }

    cout << dp[15][15] << endl;

    return 0;
}"""
        }
    ]

    # Problem 1634: Complete Binary Tree (Tree Isomorphism)
    solutions["1634"] = [
        {
            "language": "python",
            "code": """import sys
sys.setrecursionlimit(100000)
input = sys.stdin.readline

def solve(t1, t2, start1, end1, start2, end2):
    if start1 > end1:
        return 0
    if start1 == end1:
        return 1 if t1[start1] == t2[start2] else 0

    mid1 = (start1 + end1) // 2
    mid2 = (start2 + end2) // 2

    # Try matching left-left and right-right
    left_left = solve(t1, t2, start1, mid1, start2, mid2)
    right_right = solve(t1, t2, mid1 + 1, end1, mid2 + 1, end2)
    option1 = left_left + right_right

    # Try matching left-right and right-left (swap)
    left_right = solve(t1, t2, start1, mid1, mid2 + 1, end2)
    right_left = solve(t1, t2, mid1 + 1, end1, start2, mid2)
    option2 = left_right + right_left

    return max(option1, option2)

k = int(input())
t1 = list(map(int, input().split()))
t2 = list(map(int, input().split()))

n = len(t1)
result = solve(t1, t2, 0, n - 1, 0, n - 1)
print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static int[] t1, t2;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int k = Integer.parseInt(br.readLine().trim());

        StringTokenizer st1 = new StringTokenizer(br.readLine());
        StringTokenizer st2 = new StringTokenizer(br.readLine());

        int n = 1 << (k - 1);
        t1 = new int[n];
        t2 = new int[n];

        for (int i = 0; i < n; i++) {
            t1[i] = Integer.parseInt(st1.nextToken());
        }
        for (int i = 0; i < n; i++) {
            t2[i] = Integer.parseInt(st2.nextToken());
        }

        System.out.println(solve(0, n - 1, 0, n - 1));
    }

    static int solve(int s1, int e1, int s2, int e2) {
        if (s1 > e1) return 0;
        if (s1 == e1) return t1[s1] == t2[s2] ? 1 : 0;

        int m1 = (s1 + e1) / 2;
        int m2 = (s2 + e2) / 2;

        int leftLeft = solve(s1, m1, s2, m2);
        int rightRight = solve(m1 + 1, e1, m2 + 1, e2);
        int option1 = leftLeft + rightRight;

        int leftRight = solve(s1, m1, m2 + 1, e2);
        int rightLeft = solve(m1 + 1, e1, s2, m2);
        int option2 = leftRight + rightLeft;

        return Math.max(option1, option2);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

vector<int> t1, t2;

int solve(int s1, int e1, int s2, int e2) {
    if (s1 > e1) return 0;
    if (s1 == e1) return t1[s1] == t2[s2] ? 1 : 0;

    int m1 = (s1 + e1) / 2;
    int m2 = (s2 + e2) / 2;

    int leftLeft = solve(s1, m1, s2, m2);
    int rightRight = solve(m1 + 1, e1, m2 + 1, e2);
    int option1 = leftLeft + rightRight;

    int leftRight = solve(s1, m1, m2 + 1, e2);
    int rightLeft = solve(m1 + 1, e1, s2, m2);
    int option2 = leftRight + rightLeft;

    return max(option1, option2);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int k;
    cin >> k;

    int n = 1 << (k - 1);
    t1.resize(n);
    t2.resize(n);

    for (int i = 0; i < n; i++) cin >> t1[i];
    for (int i = 0; i < n; i++) cin >> t2[i];

    cout << solve(0, n - 1, 0, n - 1) << endl;

    return 0;
}"""
        }
    ]

    # Problem 1635: 1 or -1 (Constructive)
    solutions["1635"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N, M = map(int, input().split())

sequences = []
for _ in range(M):
    seq = list(map(int, input().split()))
    sequences.append(seq)

# For product to have sum 0, we need N/2 ones and N/2 negative ones
# Create base patterns that can be reused

# Strategy: Create N different b sequences based on position patterns
# For a_i, find which b_j makes product sum to 0

# Simple approach: for each a_i, construct b_i directly
# Need product to have N/2 ones and N/2 negative ones

def make_b(a):
    n = len(a)
    # We want a[i] * b[i] to have sum 0
    # So we need N/2 positions where a[i] * b[i] = 1
    # and N/2 positions where a[i] * b[i] = -1

    b = [0] * n

    # Count +1s and -1s in a
    # If a[i] = 1, b[i] = 1 gives product 1, b[i] = -1 gives product -1
    # If a[i] = -1, b[i] = 1 gives product -1, b[i] = -1 gives product 1

    ones_needed = n // 2
    neg_ones_needed = n // 2

    for i in range(n):
        if ones_needed > 0 and (neg_ones_needed == 0 or i % 2 == 0):
            # Want product = 1
            if a[i] == 1:
                b[i] = 1
            else:
                b[i] = -1
            ones_needed -= 1
        else:
            # Want product = -1
            if a[i] == 1:
                b[i] = -1
            else:
                b[i] = 1
            neg_ones_needed -= 1

    return b

# Actually, use a smarter approach
# Create a fixed set of N base b sequences
# b_k has pattern: positions 0..k-1 are one type, positions k..N-1 are another

base_b = []
for k in range(N):
    b = [1] * N
    # Set first k positions to have alternating influence
    half = N // 2
    for i in range(half):
        b[i] = 1
    for i in range(half, N):
        b[i] = -1
    base_b.append(b)

# For each a, find a b from base that works, or construct one
results = []
for seq in sequences:
    # Count what we need
    n = len(seq)
    half = n // 2

    # Construct b such that exactly half of products are 1
    b = [0] * n
    pos_count = 0
    neg_count = 0

    for i in range(n):
        if pos_count < half:
            # Make product positive
            b[i] = seq[i]  # a[i] * a[i] = 1
            pos_count += 1
        else:
            # Make product negative
            b[i] = -seq[i]  # a[i] * (-a[i]) = -1
            neg_count += 1

    results.append(b)

for b in results:
    print(' '.join(map(str, b)))"""
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

        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            int[] a = new int[N];
            for (int j = 0; j < N; j++) {
                a[j] = Integer.parseInt(st.nextToken());
            }

            int[] b = new int[N];
            int half = N / 2;

            for (int j = 0; j < N; j++) {
                if (j < half) {
                    b[j] = a[j];  // product = 1
                } else {
                    b[j] = -a[j];  // product = -1
                }
            }

            for (int j = 0; j < N; j++) {
                if (j > 0) sb.append(" ");
                sb.append(b[j]);
            }
            sb.append("\\n");
        }

        System.out.print(sb);
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

    int N, M;
    cin >> N >> M;

    for (int i = 0; i < M; i++) {
        vector<int> a(N);
        for (int j = 0; j < N; j++) {
            cin >> a[j];
        }

        int half = N / 2;

        for (int j = 0; j < N; j++) {
            int b;
            if (j < half) {
                b = a[j];  // product = 1
            } else {
                b = -a[j];  // product = -1
            }

            if (j > 0) cout << " ";
            cout << b;
        }
        cout << "\\n";
    }

    return 0;
}"""
        }
    ]

    # Problem 1636: Pringles (Greedy)
    solutions["1636"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
ranges = []
for _ in range(N):
    s, e = map(int, input().split())
    ranges.append((s, e))

# Greedy: keep track of current value, minimize total change
# For each range, move current value to closest point in range

total_cost = 0
results = []

# Start with any value in first range
current = ranges[0][0]
results.append(current)

for i in range(1, N):
    s, e = ranges[i]

    if current < s:
        total_cost += s - current
        current = s
    elif current > e:
        total_cost += current - e
        current = e
    # else current is already in range

    results.append(current)

print(total_cost)
for r in results:
    print(r)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        int[][] ranges = new int[N][2];
        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            ranges[i][0] = Integer.parseInt(st.nextToken());
            ranges[i][1] = Integer.parseInt(st.nextToken());
        }

        long totalCost = 0;
        int[] results = new int[N];

        int current = ranges[0][0];
        results[0] = current;

        for (int i = 1; i < N; i++) {
            int s = ranges[i][0];
            int e = ranges[i][1];

            if (current < s) {
                totalCost += s - current;
                current = s;
            } else if (current > e) {
                totalCost += current - e;
                current = e;
            }

            results[i] = current;
        }

        StringBuilder sb = new StringBuilder();
        sb.append(totalCost).append("\\n");
        for (int r : results) {
            sb.append(r).append("\\n");
        }
        System.out.print(sb);
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

    vector<pair<int, int>> ranges(N);
    for (int i = 0; i < N; i++) {
        cin >> ranges[i].first >> ranges[i].second;
    }

    long long totalCost = 0;
    vector<int> results(N);

    int current = ranges[0].first;
    results[0] = current;

    for (int i = 1; i < N; i++) {
        int s = ranges[i].first;
        int e = ranges[i].second;

        if (current < s) {
            totalCost += s - current;
            current = s;
        } else if (current > e) {
            totalCost += current - e;
            current = e;
        }

        results[i] = current;
    }

    cout << totalCost << "\\n";
    for (int r : results) {
        cout << r << "\\n";
    }

    return 0;
}"""
        }
    ]

    # Problem 1637: Sharp Eyes (Binary Search + Parity)
    solutions["1637"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
sequences = []
for _ in range(N):
    A, C, B = map(int, input().split())
    sequences.append((A, C, B))

def count_leq(x):
    \"\"\"Count numbers <= x in the pile\"\"\"
    total = 0
    for A, C, B in sequences:
        if x < A:
            continue
        # Numbers: A, A+B, A+2B, ..., A+kB where A+kB <= min(C, x)
        limit = min(C, x)
        if limit >= A:
            total += (limit - A) // B + 1
    return total

# Binary search for the smallest x where count_leq(x) is odd
# and count_leq(x-1) is even

left, right = 1, 2147483647

# First check if there's any odd count
if count_leq(right) % 2 == 0:
    print("NOTHING")
else:
    while left < right:
        mid = (left + right) // 2
        if count_leq(mid) % 2 == 1:
            right = mid
        else:
            left = mid + 1

    # Count how many times 'left' appears
    cnt = count_leq(left) - count_leq(left - 1)
    print(left, cnt)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static long[][] sequences;
    static int N;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        N = Integer.parseInt(br.readLine().trim());

        sequences = new long[N][3];
        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            sequences[i][0] = Long.parseLong(st.nextToken());  // A
            sequences[i][1] = Long.parseLong(st.nextToken());  // C
            sequences[i][2] = Long.parseLong(st.nextToken());  // B
        }

        if (countLeq(2147483647L) % 2 == 0) {
            System.out.println("NOTHING");
        } else {
            long left = 1, right = 2147483647L;

            while (left < right) {
                long mid = (left + right) / 2;
                if (countLeq(mid) % 2 == 1) {
                    right = mid;
                } else {
                    left = mid + 1;
                }
            }

            long cnt = countLeq(left) - countLeq(left - 1);
            System.out.println(left + " " + cnt);
        }
    }

    static long countLeq(long x) {
        long total = 0;
        for (int i = 0; i < N; i++) {
            long A = sequences[i][0];
            long C = sequences[i][1];
            long B = sequences[i][2];

            if (x < A) continue;
            long limit = Math.min(C, x);
            if (limit >= A) {
                total += (limit - A) / B + 1;
            }
        }
        return total;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
using namespace std;

int N;
vector<long long> A, C, B;

long long countLeq(long long x) {
    long long total = 0;
    for (int i = 0; i < N; i++) {
        if (x < A[i]) continue;
        long long limit = min(C[i], x);
        if (limit >= A[i]) {
            total += (limit - A[i]) / B[i] + 1;
        }
    }
    return total;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> N;

    A.resize(N);
    C.resize(N);
    B.resize(N);

    for (int i = 0; i < N; i++) {
        cin >> A[i] >> C[i] >> B[i];
    }

    if (countLeq(2147483647LL) % 2 == 0) {
        cout << "NOTHING" << endl;
    } else {
        long long left = 1, right = 2147483647LL;

        while (left < right) {
            long long mid = (left + right) / 2;
            if (countLeq(mid) % 2 == 1) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }

        long long cnt = countLeq(left) - countLeq(left - 1);
        cout << left << " " << cnt << endl;
    }

    return 0;
}"""
        }
    ]

    # Problem 1638: Convex Hull (DP)
    solutions["1638"] = [
        {
            "language": "python",
            "code": """import sys
from math import gcd
input = sys.stdin.readline

M, N = map(int, input().split())

# Maximum vertices on convex hull in M x N rectangle
# Using Farey sequence approach

# Count coprime pairs (a, b) where 0 <= a <= M, 0 <= b <= N
# Each such pair represents a direction vector

# The maximum number of vertices is the number of distinct slopes
# plus corner adjustments

def count_coprimes(m, n):
    # Count pairs (a, b) with gcd(a, b) = 1, 1 <= a <= m, 1 <= b <= n
    count = 0
    for a in range(1, m + 1):
        for b in range(1, n + 1):
            if gcd(a, b) == 1:
                count += 1
    return count

# The answer is 2 * (coprime pairs with a <= M and b <= N) + 4 (for axes directions)
# But we need to be more careful

# Actually, for convex hull with integer points in [0, M] x [0, N]
# Maximum vertices = 2 + 2 * |{(a,b): 1<=a<=M, 1<=b<=N, gcd(a,b)=1}|

coprimes = count_coprimes(M, N)
result = 2 + 2 * coprimes

print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int M = Integer.parseInt(st.nextToken());
        int N = Integer.parseInt(st.nextToken());

        int coprimes = 0;
        for (int a = 1; a <= M; a++) {
            for (int b = 1; b <= N; b++) {
                if (gcd(a, b) == 1) {
                    coprimes++;
                }
            }
        }

        int result = 2 + 2 * coprimes;
        System.out.println(result);
    }

    static int gcd(int a, int b) {
        while (b != 0) {
            int t = b;
            b = a % b;
            a = t;
        }
        return a;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <algorithm>
using namespace std;

int gcd(int a, int b) {
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int M, N;
    cin >> M >> N;

    int coprimes = 0;
    for (int a = 1; a <= M; a++) {
        for (int b = 1; b <= N; b++) {
            if (gcd(a, b) == 1) {
                coprimes++;
            }
        }
    }

    int result = 2 + 2 * coprimes;
    cout << result << endl;

    return 0;
}"""
        }
    ]

    # Problem 1639: Lucky Ticket (Bruteforce)
    solutions["1639"] = [
        {
            "language": "python",
            "code": """S = input().strip()
n = len(S)

# Find longest even-length substring where left half sum = right half sum
result = 0

for length in range(2, n + 1, 2):
    half = length // 2
    found = False
    for start in range(n - length + 1):
        left_sum = sum(int(S[start + i]) for i in range(half))
        right_sum = sum(int(S[start + half + i]) for i in range(half))
        if left_sum == right_sum:
            result = length
            found = True
            break
    if not found and result > 0:
        break

print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String S = sc.nextLine().trim();
        int n = S.length();

        int result = 0;

        for (int length = n - (n % 2); length >= 2; length -= 2) {
            int half = length / 2;
            boolean found = false;

            for (int start = 0; start <= n - length; start++) {
                int leftSum = 0, rightSum = 0;
                for (int i = 0; i < half; i++) {
                    leftSum += S.charAt(start + i) - '0';
                    rightSum += S.charAt(start + half + i) - '0';
                }
                if (leftSum == rightSum) {
                    result = length;
                    found = true;
                    break;
                }
            }

            if (found) break;
        }

        System.out.println(result);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string S;
    cin >> S;
    int n = S.length();

    int result = 0;

    for (int length = n - (n % 2); length >= 2; length -= 2) {
        int half = length / 2;
        bool found = false;

        for (int start = 0; start <= n - length; start++) {
            int leftSum = 0, rightSum = 0;
            for (int i = 0; i < half; i++) {
                leftSum += S[start + i] - '0';
                rightSum += S[start + half + i] - '0';
            }
            if (leftSum == rightSum) {
                result = length;
                found = true;
                break;
            }
        }

        if (found) break;
    }

    cout << result << endl;

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
    solutions = get_solutions_1630_1639()

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
