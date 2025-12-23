import json

with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r') as f:
    data = json.load(f)

id_to_idx = {}
for idx, p in enumerate(data):
    if 'original_id' in p:
        id_to_idx[p['original_id']] = idx

solutions = {}

# Problem 1959: Snail Pattern
solutions['1959'] = [
    {
        "language": "python",
        "code": """m, n = map(int, input().split())

# Count turns and final position for snail pattern
# Starting from top-left, going right first

# Simulate with bounds
turns = 0
x, y = 1, 1  # current position (1-indexed)

# Direction: 0=right, 1=down, 2=left, 3=up
dx = [0, 1, 0, -1]
dy = [1, 0, -1, 0]

top, bottom, left, right = 1, m, 1, n
direction = 0
cells_visited = 1

while cells_visited < m * n:
    # Move in current direction until boundary
    if direction == 0:  # right
        steps = right - y
        if steps > 0:
            y += steps
            cells_visited += steps
            if cells_visited >= m * n:
                break
        top += 1
        turns += 1
    elif direction == 1:  # down
        steps = bottom - x
        if steps > 0:
            x += steps
            cells_visited += steps
            if cells_visited >= m * n:
                break
        right -= 1
        turns += 1
    elif direction == 2:  # left
        steps = y - left
        if steps > 0:
            y -= steps
            cells_visited += steps
            if cells_visited >= m * n:
                break
        bottom -= 1
        turns += 1
    else:  # up
        steps = x - top
        if steps > 0:
            x -= steps
            cells_visited += steps
            if cells_visited >= m * n:
                break
        left += 1
        turns += 1

    direction = (direction + 1) % 4

print(turns)
print(x, y)
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long m = sc.nextLong();
        long n = sc.nextLong();

        int turns = 0;
        long x = 1, y = 1;

        long top = 1, bottom = m, left = 1, right = n;
        int direction = 0;
        long cellsVisited = 1;

        while (cellsVisited < m * n) {
            long steps;
            if (direction == 0) {
                steps = right - y;
                if (steps > 0) {
                    y += steps;
                    cellsVisited += steps;
                    if (cellsVisited >= m * n) break;
                }
                top++;
                turns++;
            } else if (direction == 1) {
                steps = bottom - x;
                if (steps > 0) {
                    x += steps;
                    cellsVisited += steps;
                    if (cellsVisited >= m * n) break;
                }
                right--;
                turns++;
            } else if (direction == 2) {
                steps = y - left;
                if (steps > 0) {
                    y -= steps;
                    cellsVisited += steps;
                    if (cellsVisited >= m * n) break;
                }
                bottom--;
                turns++;
            } else {
                steps = x - top;
                if (steps > 0) {
                    x -= steps;
                    cellsVisited += steps;
                    if (cellsVisited >= m * n) break;
                }
                left++;
                turns++;
            }
            direction = (direction + 1) % 4;
        }

        System.out.println(turns);
        System.out.println(x + " " + y);
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long m, n;
    cin >> m >> n;

    int turns = 0;
    long long x = 1, y = 1;

    long long top = 1, bottom = m, left = 1, right = n;
    int direction = 0;
    long long cellsVisited = 1;

    while (cellsVisited < m * n) {
        long long steps;
        if (direction == 0) {
            steps = right - y;
            if (steps > 0) {
                y += steps;
                cellsVisited += steps;
                if (cellsVisited >= m * n) break;
            }
            top++;
            turns++;
        } else if (direction == 1) {
            steps = bottom - x;
            if (steps > 0) {
                x += steps;
                cellsVisited += steps;
                if (cellsVisited >= m * n) break;
            }
            right--;
            turns++;
        } else if (direction == 2) {
            steps = y - left;
            if (steps > 0) {
                y -= steps;
                cellsVisited += steps;
                if (cellsVisited >= m * n) break;
            }
            bottom--;
            turns++;
        } else {
            steps = x - top;
            if (steps > 0) {
                x -= steps;
                cellsVisited += steps;
                if (cellsVisited >= m * n) break;
            }
            left++;
            turns++;
        }
        direction = (direction + 1) % 4;
    }

    cout << turns << "\\n" << x << " " << y << "\\n";
    return 0;
}
"""
    }
]

# Problem 1972: D-pairs (Surprising String)
solutions['1972'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

while True:
    s = input().strip()
    if s == '*':
        break

    n = len(s)
    surprising = True

    for d in range(n - 1):
        pairs = set()
        for i in range(n - d - 1):
            pair = s[i] + s[i + d + 1]
            if pair in pairs:
                surprising = False
                break
            pairs.add(pair)
        if not surprising:
            break

    if surprising:
        print(f"{s} is surprising.")
    else:
        print(f"{s} is NOT surprising.")
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s;

        while (!(s = br.readLine().trim()).equals("*")) {
            int n = s.length();
            boolean surprising = true;

            outer:
            for (int d = 0; d < n - 1; d++) {
                Set<String> pairs = new HashSet<>();
                for (int i = 0; i < n - d - 1; i++) {
                    String pair = "" + s.charAt(i) + s.charAt(i + d + 1);
                    if (pairs.contains(pair)) {
                        surprising = false;
                        break outer;
                    }
                    pairs.add(pair);
                }
            }

            if (surprising) {
                System.out.println(s + " is surprising.");
            } else {
                System.out.println(s + " is NOT surprising.");
            }
        }
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <set>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    while (cin >> s && s != "*") {
        int n = s.length();
        bool surprising = true;

        for (int d = 0; d < n - 1 && surprising; d++) {
            set<string> pairs;
            for (int i = 0; i < n - d - 1; i++) {
                string pair = "";
                pair += s[i];
                pair += s[i + d + 1];
                if (pairs.count(pair)) {
                    surprising = false;
                    break;
                }
                pairs.insert(pair);
            }
        }

        if (surprising) {
            cout << s << " is surprising." << endl;
        } else {
            cout << s << " is NOT surprising." << endl;
        }
    }

    return 0;
}
"""
    }
]

# Problem 1975: Sum of trailing zeros
solutions['1975'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

def count_trailing_zeros(n, b):
    # Count trailing zeros when n is written in base b
    # This equals the number of times b divides n
    count = 0
    while n % b == 0:
        count += 1
        n //= b
    return count

def solve(n):
    # Sum of f(n, b) for b from 2 to infinity
    # f(n, b) = number of trailing zeros in base b = largest k such that b^k divides n

    # For each divisor d of n, count how many bases b have b^k = d for some k >= 1
    # Actually, sum over all b: max k such that b^k | n

    # Equivalently, for each prime factor p of n with exponent e:
    # contribution is sum over b from 2 to n: floor(e_p(b) / something)...

    # Let's think differently: for each b, f(n,b) = min over primes p of floor(v_p(n) / v_p(b))
    # where v_p is the p-adic valuation

    # Simpler: f(n, b) is the largest k such that b^k | n
    # For b > n, f(n, b) = 0 (since b^1 > n can't divide n unless n = 0)

    # So we sum from b = 2 to n
    # But this is O(n) which is too slow for large n

    # For each k >= 1, count how many b have b^k | n but b^(k+1) does not divide n
    # This is equivalent to: b^k | n and either b^(k+1) > n or b^(k+1) does not divide n

    # Actually, let's count: for each divisor d of n (d > 1), add 1 for each k such that d = b^k for some b
    # i.e., for each divisor d > 1, count how many ways d = b^k with k >= 1

    # So answer = sum over d | n, d > 1: number of (b, k) with b^k = d and k >= 1
    # = sum over d | n, d > 1: 1 (if d = b^1 for b = d, always possible)
    # + 1 if d is a perfect square (d = b^2)
    # + 1 if d is a perfect cube, etc.

    # So for each divisor d > 1 of n, we add the number of k >= 1 such that d^(1/k) is an integer

    if n == 1:
        return 0

    # Get all divisors of n
    divisors = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            if i > 1:
                divisors.append(i)
            if i != n // i and n // i > 1:
                divisors.append(n // i)
        i += 1

    total = 0
    for d in divisors:
        # Count k >= 1 such that d^(1/k) is integer
        k = 1
        while True:
            root = round(d ** (1/k))
            if root < 2:
                break
            if root ** k == d:
                total += 1
            k += 1

    return total

t = int(input())
for _ in range(t):
    n = int(input())
    print(solve(n))
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            long n = Long.parseLong(br.readLine().trim());
            System.out.println(solve(n));
        }
    }

    static long solve(long n) {
        if (n == 1) return 0;

        ArrayList<Long> divisors = new ArrayList<>();
        for (long i = 1; i * i <= n; i++) {
            if (n % i == 0) {
                if (i > 1) divisors.add(i);
                if (i != n / i && n / i > 1) divisors.add(n / i);
            }
        }

        long total = 0;
        for (long d : divisors) {
            for (int k = 1; ; k++) {
                long root = (long) Math.round(Math.pow(d, 1.0 / k));
                if (root < 2) break;
                long power = 1;
                for (int j = 0; j < k; j++) power *= root;
                if (power == d) total++;
                // Also check root-1 and root+1 due to floating point
                if (root > 2) {
                    power = 1;
                    for (int j = 0; j < k; j++) power *= (root - 1);
                    if (power == d) total++;
                }
                power = 1;
                for (int j = 0; j < k; j++) power *= (root + 1);
                if (power == d) total++;
            }
        }

        return total;
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

long long solve(long long n) {
    if (n == 1) return 0;

    vector<long long> divisors;
    for (long long i = 1; i * i <= n; i++) {
        if (n % i == 0) {
            if (i > 1) divisors.push_back(i);
            if (i != n / i && n / i > 1) divisors.push_back(n / i);
        }
    }

    long long total = 0;
    for (long long d : divisors) {
        for (int k = 1; ; k++) {
            long long root = round(pow(d, 1.0 / k));
            if (root < 2) break;

            auto check = [&](long long r) {
                if (r < 2) return;
                long long power = 1;
                for (int j = 0; j < k; j++) {
                    power *= r;
                    if (power > d) return;
                }
                if (power == d) total++;
            };

            check(root);
            if (root > 2) check(root - 1);
            check(root + 1);
        }
    }

    return total;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        long long n;
        cin >> n;
        cout << solve(n) << "\\n";
    }

    return 0;
}
"""
    }
]

# Problem 1983: Number Box (DP matching)
solutions['1983'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

n = int(input())
top = list(map(int, input().split()))
bottom = list(map(int, input().split()))

# DP: dp[i][j] = max value when top row used up to position i, bottom row used up to position j
# Actually we need to handle zeros which mean empty positions

# Remove zeros and track indices
top_vals = [(i, v) for i, v in enumerate(top) if v != 0]
bottom_vals = [(i, v) for i, v in enumerate(bottom) if v != 0]

# We can place items in columns, and each column can have at most 1 from top and 1 from bottom
# Items must maintain relative order

# dp[i][j] = max sum when we've placed first i items from top and first j items from bottom
INF = float('inf')
m1, m2 = len(top_vals), len(bottom_vals)

# dp[i][j] = max product sum
dp = [[-INF] * (m2 + 1) for _ in range(m1 + 1)]
dp[0][0] = 0

for i in range(m1 + 1):
    for j in range(m2 + 1):
        if dp[i][j] == -INF:
            continue

        # Option 1: Place next top item alone (skip in bottom or empty)
        if i < m1:
            dp[i+1][j] = max(dp[i+1][j], dp[i][j])

        # Option 2: Place next bottom item alone
        if j < m2:
            dp[i][j+1] = max(dp[i][j+1], dp[i][j])

        # Option 3: Place both together in same column (multiply)
        if i < m1 and j < m2:
            product = top_vals[i][1] * bottom_vals[j][1]
            dp[i+1][j+1] = max(dp[i+1][j+1], dp[i][j] + product)

print(dp[m1][m2])
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] top = new int[n];
        for (int i = 0; i < n; i++) top[i] = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        int[] bottom = new int[n];
        for (int i = 0; i < n; i++) bottom[i] = Integer.parseInt(st.nextToken());

        ArrayList<Integer> topVals = new ArrayList<>();
        ArrayList<Integer> bottomVals = new ArrayList<>();

        for (int v : top) if (v != 0) topVals.add(v);
        for (int v : bottom) if (v != 0) bottomVals.add(v);

        int m1 = topVals.size(), m2 = bottomVals.size();
        long INF = Long.MIN_VALUE / 2;
        long[][] dp = new long[m1 + 1][m2 + 1];

        for (long[] row : dp) Arrays.fill(row, INF);
        dp[0][0] = 0;

        for (int i = 0; i <= m1; i++) {
            for (int j = 0; j <= m2; j++) {
                if (dp[i][j] == INF) continue;

                if (i < m1)
                    dp[i+1][j] = Math.max(dp[i+1][j], dp[i][j]);

                if (j < m2)
                    dp[i][j+1] = Math.max(dp[i][j+1], dp[i][j]);

                if (i < m1 && j < m2) {
                    long product = (long) topVals.get(i) * bottomVals.get(j);
                    dp[i+1][j+1] = Math.max(dp[i+1][j+1], dp[i][j] + product);
                }
            }
        }

        System.out.println(dp[m1][m2]);
    }
}
"""
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

    int n;
    cin >> n;

    vector<int> topVals, bottomVals;

    for (int i = 0; i < n; i++) {
        int v; cin >> v;
        if (v != 0) topVals.push_back(v);
    }

    for (int i = 0; i < n; i++) {
        int v; cin >> v;
        if (v != 0) bottomVals.push_back(v);
    }

    int m1 = topVals.size(), m2 = bottomVals.size();
    long long INF = -1e18;
    vector<vector<long long>> dp(m1 + 1, vector<long long>(m2 + 1, INF));
    dp[0][0] = 0;

    for (int i = 0; i <= m1; i++) {
        for (int j = 0; j <= m2; j++) {
            if (dp[i][j] == INF) continue;

            if (i < m1)
                dp[i+1][j] = max(dp[i+1][j], dp[i][j]);

            if (j < m2)
                dp[i][j+1] = max(dp[i][j+1], dp[i][j]);

            if (i < m1 && j < m2) {
                long long product = (long long) topVals[i] * bottomVals[j];
                dp[i+1][j+1] = max(dp[i+1][j+1], dp[i][j] + product);
            }
        }
    }

    cout << dp[m1][m2] << endl;
    return 0;
}
"""
    }
]

# Problem 1988: Nap Time (DP)
solutions['1988'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

n, b = map(int, input().split())
rest = [int(input()) for _ in range(n)]

# DP: dp[i][j][started] = max rest when considering interval i, using j intervals, started = whether sleeping in interval i
# First interval of each sleep segment doesn't count

INF = float('-inf')

# dp[j][0] = not sleeping at interval i
# dp[j][1] = sleeping at interval i (and was sleeping at i-1)
# dp[j][2] = just started sleeping at interval i

dp = [[INF, INF, INF] for _ in range(b + 1)]
dp[0][0] = 0

for i in range(n):
    ndp = [[INF, INF, INF] for _ in range(b + 1)]

    for j in range(b + 1):
        # Not sleeping now
        if dp[j][0] != INF:
            ndp[j][0] = max(ndp[j][0], dp[j][0])
        if dp[j][1] != INF:
            ndp[j][0] = max(ndp[j][0], dp[j][1])
        if dp[j][2] != INF:
            ndp[j][0] = max(ndp[j][0], dp[j][2])

        # Just started sleeping (no rest gained)
        if j + 1 <= b:
            if dp[j][0] != INF:
                ndp[j + 1][2] = max(ndp[j + 1][2], dp[j][0])

        # Continue sleeping (rest gained)
        if j + 1 <= b:
            if dp[j][1] != INF:
                ndp[j + 1][1] = max(ndp[j + 1][1], dp[j][1] + rest[i])
            if dp[j][2] != INF:
                ndp[j + 1][1] = max(ndp[j + 1][1], dp[j][2] + rest[i])

    dp = ndp

print(max(max(row) for row in dp))
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int b = Integer.parseInt(st.nextToken());

        int[] rest = new int[n];
        for (int i = 0; i < n; i++) {
            rest[i] = Integer.parseInt(br.readLine().trim());
        }

        long INF = Long.MIN_VALUE / 2;
        long[][] dp = new long[b + 1][3];
        for (long[] row : dp) Arrays.fill(row, INF);
        dp[0][0] = 0;

        for (int i = 0; i < n; i++) {
            long[][] ndp = new long[b + 1][3];
            for (long[] row : ndp) Arrays.fill(row, INF);

            for (int j = 0; j <= b; j++) {
                // Not sleeping
                for (int k = 0; k < 3; k++) {
                    if (dp[j][k] != INF) {
                        ndp[j][0] = Math.max(ndp[j][0], dp[j][k]);
                    }
                }

                // Just started
                if (j + 1 <= b && dp[j][0] != INF) {
                    ndp[j + 1][2] = Math.max(ndp[j + 1][2], dp[j][0]);
                }

                // Continue sleeping
                if (j + 1 <= b) {
                    if (dp[j][1] != INF)
                        ndp[j + 1][1] = Math.max(ndp[j + 1][1], dp[j][1] + rest[i]);
                    if (dp[j][2] != INF)
                        ndp[j + 1][1] = Math.max(ndp[j + 1][1], dp[j][2] + rest[i]);
                }
            }

            dp = ndp;
        }

        long ans = 0;
        for (int j = 0; j <= b; j++) {
            for (int k = 0; k < 3; k++) {
                ans = Math.max(ans, dp[j][k]);
            }
        }

        System.out.println(ans);
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <algorithm>
#include <cstring>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, b;
    cin >> n >> b;

    int rest[n];
    for (int i = 0; i < n; i++) cin >> rest[i];

    long long INF = -1e18;
    long long dp[b + 1][3];

    for (int j = 0; j <= b; j++)
        for (int k = 0; k < 3; k++)
            dp[j][k] = INF;

    dp[0][0] = 0;

    for (int i = 0; i < n; i++) {
        long long ndp[b + 1][3];
        for (int j = 0; j <= b; j++)
            for (int k = 0; k < 3; k++)
                ndp[j][k] = INF;

        for (int j = 0; j <= b; j++) {
            for (int k = 0; k < 3; k++) {
                if (dp[j][k] != INF) {
                    ndp[j][0] = max(ndp[j][0], dp[j][k]);
                }
            }

            if (j + 1 <= b && dp[j][0] != INF) {
                ndp[j + 1][2] = max(ndp[j + 1][2], dp[j][0]);
            }

            if (j + 1 <= b) {
                if (dp[j][1] != INF)
                    ndp[j + 1][1] = max(ndp[j + 1][1], dp[j][1] + rest[i]);
                if (dp[j][2] != INF)
                    ndp[j + 1][1] = max(ndp[j + 1][1], dp[j][2] + rest[i]);
            }
        }

        memcpy(dp, ndp, sizeof(dp));
    }

    long long ans = 0;
    for (int j = 0; j <= b; j++)
        for (int k = 0; k < 3; k++)
            ans = max(ans, dp[j][k]);

    cout << ans << endl;
    return 0;
}
"""
    }
]

# Problem 1989: Array Subarray Score (Stack based)
solutions['1989'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))

# For each element, find the range where it's the minimum
# Use monotonic stack

# left[i] = first index j < i where a[j] < a[i], or -1
# right[i] = first index j > i where a[j] < a[i], or n

left = [-1] * n
right = [n] * n

stack = []
for i in range(n):
    while stack and a[stack[-1]] >= a[i]:
        stack.pop()
    if stack:
        left[i] = stack[-1]
    stack.append(i)

stack = []
for i in range(n - 1, -1, -1):
    while stack and a[stack[-1]] >= a[i]:
        stack.pop()
    if stack:
        right[i] = stack[-1]
    stack.append(i)

# Prefix sum
prefix = [0] * (n + 1)
for i in range(n):
    prefix[i + 1] = prefix[i] + a[i]

ans = 0
best_i, best_j = 0, 0

for i in range(n):
    # Element a[i] is minimum in range (left[i], right[i])
    # For subarray [l, r] where left[i] < l <= i and i <= r < right[i]
    # Score = sum(l, r) * a[i]
    # We want to maximize sum, so extend as far as possible

    l = left[i] + 1
    r = right[i] - 1

    total = prefix[r + 1] - prefix[l]
    score = total * a[i]

    if score > ans:
        ans = score
        best_i, best_j = l + 1, r + 1

print(ans)
print(best_i, best_j)
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        long[] a = new long[n];
        for (int i = 0; i < n; i++) a[i] = Long.parseLong(st.nextToken());

        int[] left = new int[n];
        int[] right = new int[n];
        Arrays.fill(left, -1);
        Arrays.fill(right, n);

        Deque<Integer> stack = new ArrayDeque<>();
        for (int i = 0; i < n; i++) {
            while (!stack.isEmpty() && a[stack.peek()] >= a[i]) stack.pop();
            if (!stack.isEmpty()) left[i] = stack.peek();
            stack.push(i);
        }

        stack.clear();
        for (int i = n - 1; i >= 0; i--) {
            while (!stack.isEmpty() && a[stack.peek()] >= a[i]) stack.pop();
            if (!stack.isEmpty()) right[i] = stack.peek();
            stack.push(i);
        }

        long[] prefix = new long[n + 1];
        for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + a[i];

        long ans = 0;
        int bestI = 0, bestJ = 0;

        for (int i = 0; i < n; i++) {
            int l = left[i] + 1;
            int r = right[i] - 1;
            long total = prefix[r + 1] - prefix[l];
            long score = total * a[i];

            if (score > ans) {
                ans = score;
                bestI = l + 1;
                bestJ = r + 1;
            }
        }

        System.out.println(ans);
        System.out.println(bestI + " " + bestJ);
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <stack>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    long long a[n];
    for (int i = 0; i < n; i++) cin >> a[i];

    int left[n], right[n];
    fill(left, left + n, -1);
    fill(right, right + n, n);

    stack<int> st;
    for (int i = 0; i < n; i++) {
        while (!st.empty() && a[st.top()] >= a[i]) st.pop();
        if (!st.empty()) left[i] = st.top();
        st.push(i);
    }

    while (!st.empty()) st.pop();
    for (int i = n - 1; i >= 0; i--) {
        while (!st.empty() && a[st.top()] >= a[i]) st.pop();
        if (!st.empty()) right[i] = st.top();
        st.push(i);
    }

    long long prefix[n + 1];
    prefix[0] = 0;
    for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + a[i];

    long long ans = 0;
    int bestI = 0, bestJ = 0;

    for (int i = 0; i < n; i++) {
        int l = left[i] + 1;
        int r = right[i] - 1;
        long long total = prefix[r + 1] - prefix[l];
        long long score = total * a[i];

        if (score > ans) {
            ans = score;
            bestI = l + 1;
            bestJ = r + 1;
        }
    }

    cout << ans << "\\n" << bestI << " " << bestJ << "\\n";
    return 0;
}
"""
    }
]

# Problem 1999: Submatrix Query (2D RMQ or sliding window)
solutions['1999'] = [
    {
        "language": "python",
        "code": """import sys
from collections import deque
input = sys.stdin.readline

n, b, k = map(int, input().split())
matrix = []
for _ in range(n):
    matrix.append(list(map(int, input().split())))

# Precompute max and min for each BxB submatrix using sliding window

# First, compute row-wise min/max with window size b
row_max = [[0] * (n - b + 1) for _ in range(n)]
row_min = [[0] * (n - b + 1) for _ in range(n)]

for i in range(n):
    dq_max, dq_min = deque(), deque()
    for j in range(n):
        while dq_max and matrix[i][dq_max[-1]] <= matrix[i][j]:
            dq_max.pop()
        while dq_min and matrix[i][dq_min[-1]] >= matrix[i][j]:
            dq_min.pop()
        dq_max.append(j)
        dq_min.append(j)

        if j >= b - 1:
            while dq_max[0] <= j - b:
                dq_max.popleft()
            while dq_min[0] <= j - b:
                dq_min.popleft()
            row_max[i][j - b + 1] = matrix[i][dq_max[0]]
            row_min[i][j - b + 1] = matrix[i][dq_min[0]]

# Now compute column-wise min/max
cols = n - b + 1
sub_max = [[0] * cols for _ in range(n - b + 1)]
sub_min = [[0] * cols for _ in range(n - b + 1)]

for j in range(cols):
    dq_max, dq_min = deque(), deque()
    for i in range(n):
        while dq_max and row_max[dq_max[-1]][j] <= row_max[i][j]:
            dq_max.pop()
        while dq_min and row_min[dq_min[-1]][j] >= row_min[i][j]:
            dq_min.pop()
        dq_max.append(i)
        dq_min.append(i)

        if i >= b - 1:
            while dq_max[0] <= i - b:
                dq_max.popleft()
            while dq_min[0] <= i - b:
                dq_min.popleft()
            sub_max[i - b + 1][j] = row_max[dq_max[0]][j]
            sub_min[i - b + 1][j] = row_min[dq_min[0]][j]

results = []
for _ in range(k):
    i, j = map(int, input().split())
    i -= 1
    j -= 1
    results.append(sub_max[i][j] - sub_min[i][j])

print('\\n'.join(map(str, results)))
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        PrintWriter pw = new PrintWriter(new BufferedOutputStream(System.out));

        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int b = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        int[][] matrix = new int[n][n];
        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                matrix[i][j] = Integer.parseInt(st.nextToken());
            }
        }

        int cols = n - b + 1;
        int[][] rowMax = new int[n][cols];
        int[][] rowMin = new int[n][cols];

        for (int i = 0; i < n; i++) {
            Deque<Integer> dqMax = new ArrayDeque<>();
            Deque<Integer> dqMin = new ArrayDeque<>();
            for (int j = 0; j < n; j++) {
                while (!dqMax.isEmpty() && matrix[i][dqMax.peekLast()] <= matrix[i][j]) dqMax.pollLast();
                while (!dqMin.isEmpty() && matrix[i][dqMin.peekLast()] >= matrix[i][j]) dqMin.pollLast();
                dqMax.addLast(j);
                dqMin.addLast(j);

                if (j >= b - 1) {
                    while (dqMax.peekFirst() <= j - b) dqMax.pollFirst();
                    while (dqMin.peekFirst() <= j - b) dqMin.pollFirst();
                    rowMax[i][j - b + 1] = matrix[i][dqMax.peekFirst()];
                    rowMin[i][j - b + 1] = matrix[i][dqMin.peekFirst()];
                }
            }
        }

        int rows = n - b + 1;
        int[][] subMax = new int[rows][cols];
        int[][] subMin = new int[rows][cols];

        for (int j = 0; j < cols; j++) {
            Deque<Integer> dqMax = new ArrayDeque<>();
            Deque<Integer> dqMin = new ArrayDeque<>();
            for (int i = 0; i < n; i++) {
                while (!dqMax.isEmpty() && rowMax[dqMax.peekLast()][j] <= rowMax[i][j]) dqMax.pollLast();
                while (!dqMin.isEmpty() && rowMin[dqMin.peekLast()][j] >= rowMin[i][j]) dqMin.pollLast();
                dqMax.addLast(i);
                dqMin.addLast(i);

                if (i >= b - 1) {
                    while (dqMax.peekFirst() <= i - b) dqMax.pollFirst();
                    while (dqMin.peekFirst() <= i - b) dqMin.pollFirst();
                    subMax[i - b + 1][j] = rowMax[dqMax.peekFirst()][j];
                    subMin[i - b + 1][j] = rowMin[dqMin.peekFirst()][j];
                }
            }
        }

        for (int q = 0; q < k; q++) {
            st = new StringTokenizer(br.readLine());
            int i = Integer.parseInt(st.nextToken()) - 1;
            int j = Integer.parseInt(st.nextToken()) - 1;
            pw.println(subMax[i][j] - subMin[i][j]);
        }

        pw.close();
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <deque>
using namespace std;

int matrix[251][251];
int rowMax[251][251], rowMin[251][251];
int subMax[251][251], subMin[251][251];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, b, k;
    cin >> n >> b >> k;

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            cin >> matrix[i][j];

    int cols = n - b + 1;

    for (int i = 0; i < n; i++) {
        deque<int> dqMax, dqMin;
        for (int j = 0; j < n; j++) {
            while (!dqMax.empty() && matrix[i][dqMax.back()] <= matrix[i][j]) dqMax.pop_back();
            while (!dqMin.empty() && matrix[i][dqMin.back()] >= matrix[i][j]) dqMin.pop_back();
            dqMax.push_back(j);
            dqMin.push_back(j);

            if (j >= b - 1) {
                while (dqMax.front() <= j - b) dqMax.pop_front();
                while (dqMin.front() <= j - b) dqMin.pop_front();
                rowMax[i][j - b + 1] = matrix[i][dqMax.front()];
                rowMin[i][j - b + 1] = matrix[i][dqMin.front()];
            }
        }
    }

    for (int j = 0; j < cols; j++) {
        deque<int> dqMax, dqMin;
        for (int i = 0; i < n; i++) {
            while (!dqMax.empty() && rowMax[dqMax.back()][j] <= rowMax[i][j]) dqMax.pop_back();
            while (!dqMin.empty() && rowMin[dqMin.back()][j] >= rowMin[i][j]) dqMin.pop_back();
            dqMax.push_back(i);
            dqMin.push_back(i);

            if (i >= b - 1) {
                while (dqMax.front() <= i - b) dqMax.pop_front();
                while (dqMin.front() <= i - b) dqMin.pop_front();
                subMax[i - b + 1][j] = rowMax[dqMax.front()][j];
                subMin[i - b + 1][j] = rowMin[dqMin.front()][j];
            }
        }
    }

    for (int q = 0; q < k; q++) {
        int i, j;
        cin >> i >> j;
        i--; j--;
        cout << subMax[i][j] - subMin[i][j] << "\\n";
    }

    return 0;
}
"""
    }
]

# Apply solutions
for oid, sol_list in solutions.items():
    if oid in id_to_idx:
        data[id_to_idx[oid]]['solutions'] = sol_list
        print(f"Applied solutions for problem {oid}")

with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nSaved checkpoint file")
print(f"Total problems processed: {len(solutions)}")
