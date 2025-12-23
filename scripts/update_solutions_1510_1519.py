#!/usr/bin/env python3
import json

# Read the checkpoint file
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Solutions for problems 1510-1519
solutions_data = {
    "1510": [
        {
            "language": "python",
            "code": """n, m = map(int, input().split())
n += 1
m += 1

count = 0

# For each possible pair of equal-length sides
# Consider isosceles triangles where two sides have equal length
# We need to find triangles on grid points

for dx in range(m):
    for dy in range(n):
        if dx == 0 and dy == 0:
            continue

        # Length squared of the equal sides
        len_sq = dx * dx + dy * dy

        # For perpendicular bisector approach
        # Base vertices at (0,0) and (2*dx, 2*dy) - apex on perpendicular bisector
        # Or use rotation: rotate (dx, dy) by 90 degrees to get (-dy, dx)

        # Count triangles with apex at various positions
        # The two equal sides go from apex to two base vertices

        # Method: for each pair of points A, B that could be the base
        # find all apex points C such that |AC| = |BC|

        # Perpendicular direction to (dx, dy) is (-dy, dx)
        for k in range(-max(n, m), max(n, m) + 1):
            if k == 0:
                continue

            # Apex offset from midpoint: k * (-dy, dx) / 2 won't give integer coords
            # Need different approach
            pass

# Simpler brute force for small grids
count = 0
points = [(i, j) for i in range(m) for j in range(n)]

for i in range(len(points)):
    for j in range(i + 1, len(points)):
        for k in range(j + 1, len(points)):
            x1, y1 = points[i]
            x2, y2 = points[j]
            x3, y3 = points[k]

            # Check if they form a valid triangle (not collinear)
            area2 = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
            if area2 == 0:
                continue

            # Calculate squared distances
            d12 = (x2 - x1) ** 2 + (y2 - y1) ** 2
            d23 = (x3 - x2) ** 2 + (y3 - y2) ** 2
            d13 = (x3 - x1) ** 2 + (y3 - y1) ** 2

            # Check if isosceles (at least two sides equal)
            if d12 == d23 or d23 == d13 or d12 == d13:
                count += 1

print(count)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt() + 1;
        int m = sc.nextInt() + 1;

        long count = 0;

        for (int x1 = 0; x1 < m; x1++) {
            for (int y1 = 0; y1 < n; y1++) {
                for (int x2 = 0; x2 < m; x2++) {
                    for (int y2 = 0; y2 < n; y2++) {
                        if (x1 == x2 && y1 == y2) continue;
                        if (x1 > x2 || (x1 == x2 && y1 > y2)) continue;

                        for (int x3 = 0; x3 < m; x3++) {
                            for (int y3 = 0; y3 < n; y3++) {
                                if ((x1 == x3 && y1 == y3) || (x2 == x3 && y2 == y3)) continue;
                                if (x2 > x3 || (x2 == x3 && y2 > y3)) continue;

                                // Check collinearity
                                int area2 = Math.abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1));
                                if (area2 == 0) continue;

                                // Check distances
                                int d12 = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
                                int d23 = (x3 - x2) * (x3 - x2) + (y3 - y2) * (y3 - y2);
                                int d13 = (x3 - x1) * (x3 - x1) + (y3 - y1) * (y3 - y1);

                                if (d12 == d23 || d23 == d13 || d12 == d13) {
                                    count++;
                                }
                            }
                        }
                    }
                }
            }
        }

        System.out.println(count);
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

    int n, m;
    cin >> n >> m;
    n++; m++;

    long long count = 0;

    for (int x1 = 0; x1 < m; x1++) {
        for (int y1 = 0; y1 < n; y1++) {
            for (int x2 = x1; x2 < m; x2++) {
                for (int y2 = (x2 == x1 ? y1 + 1 : 0); y2 < n; y2++) {
                    for (int x3 = x2; x3 < m; x3++) {
                        for (int y3 = (x3 == x2 ? y2 + 1 : 0); y3 < n; y3++) {
                            // Check collinearity
                            int area2 = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1));
                            if (area2 == 0) continue;

                            // Check distances
                            int d12 = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
                            int d23 = (x3 - x2) * (x3 - x2) + (y3 - y2) * (y3 - y2);
                            int d13 = (x3 - x1) * (x3 - x1) + (y3 - y1) * (y3 - y1);

                            if (d12 == d23 || d23 == d13 || d12 == d13) {
                                count++;
                            }
                        }
                    }
                }
            }
        }
    }

    cout << count << endl;

    return 0;
}"""
        }
    ],
    "1511": [
        {
            "language": "python",
            "code": """cards = list(map(int, input().split()))

# Total cards
total = sum(cards)

if total == 0:
    print(0)
elif cards[0] == total:
    # Only 0s
    print(0)
else:
    # Greedy approach: place digits from 9 to 0
    # Alternating to avoid consecutive same digits
    # Maximize the number by placing larger digits first

    result = []

    # We need to handle the constraint that no two adjacent digits are same
    # and the number can't start with 0

    # Find if it's possible
    max_count = max(cards)
    if max_count > (total + 1) // 2:
        # Impossible - one digit appears too many times
        print(0)
    else:
        # Greedy: always try to place the largest possible digit
        # that is different from the last placed digit
        remaining = cards[:]
        last = -1

        while sum(remaining) > 0:
            placed = False
            for d in range(9, -1, -1):
                if remaining[d] > 0 and d != last:
                    # Check if we can still complete the number after placing d
                    remaining[d] -= 1

                    # Verify: the remaining most frequent digit shouldn't exceed
                    # half of remaining total (rounded up)
                    new_total = sum(remaining)
                    new_max = max(remaining)

                    if new_total == 0 or new_max <= (new_total + 1) // 2:
                        if len(result) == 0 and d == 0 and new_total > 0:
                            # Can't start with 0 if there are more digits
                            remaining[d] += 1
                            continue
                        result.append(str(d))
                        last = d
                        placed = True
                        break
                    else:
                        remaining[d] += 1

            if not placed:
                # Try any valid digit
                for d in range(9, -1, -1):
                    if remaining[d] > 0 and d != last:
                        result.append(str(d))
                        remaining[d] -= 1
                        last = d
                        placed = True
                        break

                if not placed:
                    break

        if sum(remaining) == 0:
            print(''.join(result))
        else:
            print(0)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int[] cards = new int[10];
        for (int i = 0; i < 10; i++) {
            cards[i] = sc.nextInt();
        }

        int total = 0;
        for (int c : cards) total += c;

        if (total == 0) {
            System.out.println(0);
            return;
        }

        if (cards[0] == total) {
            System.out.println(0);
            return;
        }

        int maxCount = 0;
        for (int c : cards) maxCount = Math.max(maxCount, c);

        if (maxCount > (total + 1) / 2) {
            System.out.println(0);
            return;
        }

        StringBuilder result = new StringBuilder();
        int[] remaining = cards.clone();
        int last = -1;

        while (true) {
            int sum = 0;
            for (int r : remaining) sum += r;
            if (sum == 0) break;

            boolean placed = false;
            for (int d = 9; d >= 0; d--) {
                if (remaining[d] > 0 && d != last) {
                    remaining[d]--;

                    int newTotal = 0;
                    int newMax = 0;
                    for (int r : remaining) {
                        newTotal += r;
                        newMax = Math.max(newMax, r);
                    }

                    if (newTotal == 0 || newMax <= (newTotal + 1) / 2) {
                        if (result.length() == 0 && d == 0 && newTotal > 0) {
                            remaining[d]++;
                            continue;
                        }
                        result.append(d);
                        last = d;
                        placed = true;
                        break;
                    } else {
                        remaining[d]++;
                    }
                }
            }

            if (!placed) break;
        }

        int finalSum = 0;
        for (int r : remaining) finalSum += r;

        if (finalSum == 0) {
            System.out.println(result.toString());
        } else {
            System.out.println(0);
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int cards[10];
    int total = 0;
    for (int i = 0; i < 10; i++) {
        cin >> cards[i];
        total += cards[i];
    }

    if (total == 0) {
        cout << 0 << endl;
        return 0;
    }

    if (cards[0] == total) {
        cout << 0 << endl;
        return 0;
    }

    int maxCount = *max_element(cards, cards + 10);

    if (maxCount > (total + 1) / 2) {
        cout << 0 << endl;
        return 0;
    }

    string result = "";
    int remaining[10];
    copy(cards, cards + 10, remaining);
    int last = -1;

    while (true) {
        int sum = 0;
        for (int i = 0; i < 10; i++) sum += remaining[i];
        if (sum == 0) break;

        bool placed = false;
        for (int d = 9; d >= 0; d--) {
            if (remaining[d] > 0 && d != last) {
                remaining[d]--;

                int newTotal = 0, newMax = 0;
                for (int i = 0; i < 10; i++) {
                    newTotal += remaining[i];
                    newMax = max(newMax, remaining[i]);
                }

                if (newTotal == 0 || newMax <= (newTotal + 1) / 2) {
                    if (result.empty() && d == 0 && newTotal > 0) {
                        remaining[d]++;
                        continue;
                    }
                    result += ('0' + d);
                    last = d;
                    placed = true;
                    break;
                } else {
                    remaining[d]++;
                }
            }
        }

        if (!placed) break;
    }

    int finalSum = 0;
    for (int i = 0; i < 10; i++) finalSum += remaining[i];

    if (finalSum == 0) {
        cout << result << endl;
    } else {
        cout << 0 << endl;
    }

    return 0;
}"""
        }
    ],
    "1512": [
        {
            "language": "python",
            "code": """m = int(input())
s = input().strip()
n = len(s)

min_changes = n  # worst case: change every character

for p in range(1, m + 1):
    # For period p, count changes needed
    changes = 0
    for i in range(p):
        # Count characters at positions i, i+p, i+2p, ...
        count = {'A': 0, 'C': 0, 'G': 0, 'T': 0}
        total = 0
        for j in range(i, n, p):
            count[s[j]] += 1
            total += 1
        # Keep the most frequent, change others
        max_count = max(count.values())
        changes += total - max_count

    min_changes = min(min_changes, changes)

print(min_changes)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int m = sc.nextInt();
        sc.nextLine();
        String s = sc.nextLine().trim();
        int n = s.length();

        int minChanges = n;

        for (int p = 1; p <= m; p++) {
            int changes = 0;
            for (int i = 0; i < p; i++) {
                int[] count = new int[4]; // A, C, G, T
                int total = 0;
                for (int j = i; j < n; j += p) {
                    char c = s.charAt(j);
                    if (c == 'A') count[0]++;
                    else if (c == 'C') count[1]++;
                    else if (c == 'G') count[2]++;
                    else count[3]++;
                    total++;
                }
                int maxCount = Math.max(Math.max(count[0], count[1]), Math.max(count[2], count[3]));
                changes += total - maxCount;
            }
            minChanges = Math.min(minChanges, changes);
        }

        System.out.println(minChanges);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int m;
    string s;
    cin >> m >> s;
    int n = s.length();

    int minChanges = n;

    for (int p = 1; p <= m; p++) {
        int changes = 0;
        for (int i = 0; i < p; i++) {
            int count[4] = {0}; // A, C, G, T
            int total = 0;
            for (int j = i; j < n; j += p) {
                char c = s[j];
                if (c == 'A') count[0]++;
                else if (c == 'C') count[1]++;
                else if (c == 'G') count[2]++;
                else count[3]++;
                total++;
            }
            int maxCount = max({count[0], count[1], count[2], count[3]});
            changes += total - maxCount;
        }
        minChanges = min(minChanges, changes);
    }

    cout << minChanges << endl;

    return 0;
}"""
        }
    ],
    "1513": [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

MOD = 1000007

line = input().split()
n, m, c = int(line[0]), int(line[1]), int(line[2])

# arcade[r][c] = arcade number at position (r, c), or 0 if none
arcade = [[0] * (m + 1) for _ in range(n + 1)]
for i in range(1, c + 1):
    r, col = map(int, input().split())
    arcade[r][col] = i

# dp[r][c][k][last] = number of ways to reach (r, c) visiting exactly k arcades
# with last visited arcade being 'last'
# This is too memory intensive, so we optimize

# dp[r][c][k] = number of ways to reach (r, c) visiting exactly k arcades
# where visits are in increasing order of arcade number

# Actually we need: dp[i][j][k][l] = ways to reach (i,j) having visited k arcades
# with the last visited arcade being l

# Simplified: dp[i][j][k] where we track the count, and ensure order by the traversal

dp = [[[[0] * (c + 1) for _ in range(c + 1)] for _ in range(m + 1)] for _ in range(n + 1)]
# dp[i][j][k][last] = ways to reach (i,j) with k arcades visited, last arcade = last

if arcade[1][1] > 0:
    dp[1][1][1][arcade[1][1]] = 1
else:
    dp[1][1][0][0] = 1

for i in range(1, n + 1):
    for j in range(1, m + 1):
        if i == 1 and j == 1:
            continue

        curr_arcade = arcade[i][j]

        for k in range(c + 1):
            for last in range(c + 1):
                # From (i-1, j)
                if i > 1:
                    if curr_arcade > 0:
                        if curr_arcade > last:
                            dp[i][j][k][curr_arcade] = (dp[i][j][k][curr_arcade] + dp[i-1][j][k-1][last]) % MOD
                    else:
                        dp[i][j][k][last] = (dp[i][j][k][last] + dp[i-1][j][k][last]) % MOD

                # From (i, j-1)
                if j > 1:
                    if curr_arcade > 0:
                        if curr_arcade > last:
                            dp[i][j][k][curr_arcade] = (dp[i][j][k][curr_arcade] + dp[i][j-1][k-1][last]) % MOD
                    else:
                        dp[i][j][k][last] = (dp[i][j][k][last] + dp[i][j-1][k][last]) % MOD

# Sum up results
result = []
for k in range(c + 1):
    total = 0
    for last in range(c + 1):
        total = (total + dp[n][m][k][last]) % MOD
    result.append(str(total))

print(' '.join(result))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static final int MOD = 1000007;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt(), m = sc.nextInt(), c = sc.nextInt();

        int[][] arcade = new int[n + 1][m + 1];
        for (int i = 1; i <= c; i++) {
            int r = sc.nextInt(), col = sc.nextInt();
            arcade[r][col] = i;
        }

        // dp[i][j][k][last]
        int[][][][] dp = new int[n + 1][m + 1][c + 1][c + 1];

        if (arcade[1][1] > 0) {
            dp[1][1][1][arcade[1][1]] = 1;
        } else {
            dp[1][1][0][0] = 1;
        }

        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= m; j++) {
                if (i == 1 && j == 1) continue;

                int curr = arcade[i][j];

                for (int k = 0; k <= c; k++) {
                    for (int last = 0; last <= c; last++) {
                        if (i > 1) {
                            if (curr > 0 && k > 0 && curr > last) {
                                dp[i][j][k][curr] = (dp[i][j][k][curr] + dp[i-1][j][k-1][last]) % MOD;
                            } else if (curr == 0) {
                                dp[i][j][k][last] = (dp[i][j][k][last] + dp[i-1][j][k][last]) % MOD;
                            }
                        }
                        if (j > 1) {
                            if (curr > 0 && k > 0 && curr > last) {
                                dp[i][j][k][curr] = (dp[i][j][k][curr] + dp[i][j-1][k-1][last]) % MOD;
                            } else if (curr == 0) {
                                dp[i][j][k][last] = (dp[i][j][k][last] + dp[i][j-1][k][last]) % MOD;
                            }
                        }
                    }
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int k = 0; k <= c; k++) {
            long total = 0;
            for (int last = 0; last <= c; last++) {
                total = (total + dp[n][m][k][last]) % MOD;
            }
            sb.append(total);
            if (k < c) sb.append(" ");
        }
        System.out.println(sb);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
using namespace std;

const int MOD = 1000007;

int arcade[51][51];
int dp[51][51][51][51];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, c;
    cin >> n >> m >> c;

    for (int i = 1; i <= c; i++) {
        int r, col;
        cin >> r >> col;
        arcade[r][col] = i;
    }

    if (arcade[1][1] > 0) {
        dp[1][1][1][arcade[1][1]] = 1;
    } else {
        dp[1][1][0][0] = 1;
    }

    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= m; j++) {
            if (i == 1 && j == 1) continue;

            int curr = arcade[i][j];

            for (int k = 0; k <= c; k++) {
                for (int last = 0; last <= c; last++) {
                    if (i > 1) {
                        if (curr > 0 && k > 0 && curr > last) {
                            dp[i][j][k][curr] = (dp[i][j][k][curr] + dp[i-1][j][k-1][last]) % MOD;
                        } else if (curr == 0) {
                            dp[i][j][k][last] = (dp[i][j][k][last] + dp[i-1][j][k][last]) % MOD;
                        }
                    }
                    if (j > 1) {
                        if (curr > 0 && k > 0 && curr > last) {
                            dp[i][j][k][curr] = (dp[i][j][k][curr] + dp[i][j-1][k-1][last]) % MOD;
                        } else if (curr == 0) {
                            dp[i][j][k][last] = (dp[i][j][k][last] + dp[i][j-1][k][last]) % MOD;
                        }
                    }
                }
            }
        }
    }

    for (int k = 0; k <= c; k++) {
        long long total = 0;
        for (int last = 0; last <= c; last++) {
            total = (total + dp[n][m][k][last]) % MOD;
        }
        cout << total;
        if (k < c) cout << " ";
    }
    cout << endl;

    return 0;
}"""
        }
    ],
    "1514": [
        {
            "language": "python",
            "code": """import sys
from functools import lru_cache

n = int(input())
current = input().strip()
target = input().strip()

# Calculate the difference at each position (mod 10)
diff = [(int(target[i]) - int(current[i])) % 10 for i in range(n)]

# dp[i][d1][d2] = minimum moves to solve positions 0..i-1
# where position i needs additional d1 turns and position i+1 needs additional d2 turns
# (due to previous multi-disc operations)

INF = float('inf')

# Precompute cost to rotate a single disc by amount d
def single_cost(d):
    d = d % 10
    if d == 0:
        return 0
    return (d + 2) // 3  # ceil(d / 3)

# Cost table for rotating 1, 2, or 3 adjacent discs
# cost[amount] = number of operations for one disc
# For multi-disc: we rotate all by same amount in one operation

@lru_cache(maxsize=None)
def solve(i, carry1, carry2):
    if i == n:
        if carry1 == 0 and carry2 == 0:
            return 0
        return INF

    need = (diff[i] + carry1) % 10

    min_cost = INF

    # Try all possible rotations at position i (affecting i, i+1, i+2)
    for rot1 in range(10):  # rotation for single disc at i
        for rot2 in range(10):  # rotation for discs i and i+1
            for rot3 in range(10):  # rotation for discs i, i+1, i+2
                total_at_i = (rot1 + rot2 + rot3) % 10
                if total_at_i != need:
                    continue

                # Calculate cost
                cost = single_cost(rot1) + single_cost(rot2) + single_cost(rot3)

                new_carry1 = (carry2 + rot2 + rot3) % 10
                new_carry2 = rot3

                future = solve(i + 1, new_carry1, new_carry2)
                if future != INF:
                    min_cost = min(min_cost, cost + future)

    return min_cost

print(solve(0, 0, 0))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static int n;
    static int[] diff;
    static int[][][] memo;
    static final int INF = 1000000;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();
        String current = sc.next();
        String target = sc.next();

        diff = new int[n];
        for (int i = 0; i < n; i++) {
            diff[i] = ((target.charAt(i) - current.charAt(i)) % 10 + 10) % 10;
        }

        memo = new int[n + 1][10][10];
        for (int[][] arr2 : memo) {
            for (int[] arr1 : arr2) {
                Arrays.fill(arr1, -1);
            }
        }

        System.out.println(solve(0, 0, 0));
    }

    static int singleCost(int d) {
        d = d % 10;
        if (d == 0) return 0;
        return (d + 2) / 3;
    }

    static int solve(int i, int carry1, int carry2) {
        if (i == n) {
            return (carry1 == 0 && carry2 == 0) ? 0 : INF;
        }

        if (memo[i][carry1][carry2] != -1) {
            return memo[i][carry1][carry2];
        }

        int need = (diff[i] + carry1) % 10;
        int minCost = INF;

        for (int rot1 = 0; rot1 < 10; rot1++) {
            for (int rot2 = 0; rot2 < 10; rot2++) {
                for (int rot3 = 0; rot3 < 10; rot3++) {
                    int totalAtI = (rot1 + rot2 + rot3) % 10;
                    if (totalAtI != need) continue;

                    int cost = singleCost(rot1) + singleCost(rot2) + singleCost(rot3);
                    int newCarry1 = (carry2 + rot2 + rot3) % 10;
                    int newCarry2 = rot3;

                    int future = solve(i + 1, newCarry1, newCarry2);
                    if (future != INF) {
                        minCost = Math.min(minCost, cost + future);
                    }
                }
            }
        }

        memo[i][carry1][carry2] = minCost;
        return minCost;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
#include <cstring>
#include <algorithm>
using namespace std;

int n;
int diff[101];
int memo[101][10][10];
const int INF = 1000000;

int singleCost(int d) {
    d = d % 10;
    if (d == 0) return 0;
    return (d + 2) / 3;
}

int solve(int i, int carry1, int carry2) {
    if (i == n) {
        return (carry1 == 0 && carry2 == 0) ? 0 : INF;
    }

    if (memo[i][carry1][carry2] != -1) {
        return memo[i][carry1][carry2];
    }

    int need = (diff[i] + carry1) % 10;
    int minCost = INF;

    for (int rot1 = 0; rot1 < 10; rot1++) {
        for (int rot2 = 0; rot2 < 10; rot2++) {
            for (int rot3 = 0; rot3 < 10; rot3++) {
                int totalAtI = (rot1 + rot2 + rot3) % 10;
                if (totalAtI != need) continue;

                int cost = singleCost(rot1) + singleCost(rot2) + singleCost(rot3);
                int newCarry1 = (carry2 + rot2 + rot3) % 10;
                int newCarry2 = rot3;

                int future = solve(i + 1, newCarry1, newCarry2);
                if (future != INF) {
                    minCost = min(minCost, cost + future);
                }
            }
        }
    }

    return memo[i][carry1][carry2] = minCost;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string current, target;
    cin >> n >> current >> target;

    for (int i = 0; i < n; i++) {
        diff[i] = ((target[i] - current[i]) % 10 + 10) % 10;
    }

    memset(memo, -1, sizeof(memo));

    cout << solve(0, 0, 0) << endl;

    return 0;
}"""
        }
    ],
    "1515": [
        {
            "language": "python",
            "code": """s = input().strip()
idx = 0
n = 1

while idx < len(s):
    num_str = str(n)
    for c in num_str:
        if idx < len(s) and s[idx] == c:
            idx += 1
    n += 1

print(n - 1)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine().trim();

        int idx = 0;
        int n = 1;

        while (idx < s.length()) {
            String numStr = String.valueOf(n);
            for (int i = 0; i < numStr.length() && idx < s.length(); i++) {
                if (s.charAt(idx) == numStr.charAt(i)) {
                    idx++;
                }
            }
            n++;
        }

        System.out.println(n - 1);
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

    string s;
    cin >> s;

    int idx = 0;
    int n = 1;

    while (idx < s.length()) {
        string numStr = to_string(n);
        for (char c : numStr) {
            if (idx < s.length() && s[idx] == c) {
                idx++;
            }
        }
        n++;
    }

    cout << n - 1 << endl;

    return 0;
}"""
        }
    ],
    "1516": [
        {
            "language": "python",
            "code": """from collections import deque
import sys
input = sys.stdin.readline

n = int(input())
time = [0] * (n + 1)
graph = [[] for _ in range(n + 1)]
indegree = [0] * (n + 1)

for i in range(1, n + 1):
    line = list(map(int, input().split()))
    time[i] = line[0]
    for j in range(1, len(line) - 1):
        prereq = line[j]
        graph[prereq].append(i)
        indegree[i] += 1

# Topological sort with DP
result = [0] * (n + 1)
queue = deque()

for i in range(1, n + 1):
    if indegree[i] == 0:
        queue.append(i)
        result[i] = time[i]

while queue:
    node = queue.popleft()
    for next_node in graph[node]:
        result[next_node] = max(result[next_node], result[node] + time[next_node])
        indegree[next_node] -= 1
        if indegree[next_node] == 0:
            queue.append(next_node)

for i in range(1, n + 1):
    print(result[i])"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[] time = new int[n + 1];
        List<Integer>[] graph = new ArrayList[n + 1];
        int[] indegree = new int[n + 1];

        for (int i = 0; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 1; i <= n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            time[i] = Integer.parseInt(st.nextToken());
            while (st.hasMoreTokens()) {
                int prereq = Integer.parseInt(st.nextToken());
                if (prereq == -1) break;
                graph[prereq].add(i);
                indegree[i]++;
            }
        }

        int[] result = new int[n + 1];
        Queue<Integer> queue = new LinkedList<>();

        for (int i = 1; i <= n; i++) {
            if (indegree[i] == 0) {
                queue.offer(i);
                result[i] = time[i];
            }
        }

        while (!queue.isEmpty()) {
            int node = queue.poll();
            for (int next : graph[node]) {
                result[next] = Math.max(result[next], result[node] + time[next]);
                indegree[next]--;
                if (indegree[next] == 0) {
                    queue.offer(next);
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= n; i++) {
            sb.append(result[i]).append("\\n");
        }
        System.out.print(sb);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <queue>
#include <sstream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    cin.ignore();

    vector<int> time(n + 1);
    vector<vector<int>> graph(n + 1);
    vector<int> indegree(n + 1, 0);

    for (int i = 1; i <= n; i++) {
        string line;
        getline(cin, line);
        istringstream iss(line);

        iss >> time[i];
        int prereq;
        while (iss >> prereq && prereq != -1) {
            graph[prereq].push_back(i);
            indegree[i]++;
        }
    }

    vector<int> result(n + 1, 0);
    queue<int> q;

    for (int i = 1; i <= n; i++) {
        if (indegree[i] == 0) {
            q.push(i);
            result[i] = time[i];
        }
    }

    while (!q.empty()) {
        int node = q.front();
        q.pop();

        for (int next : graph[node]) {
            result[next] = max(result[next], result[node] + time[next]);
            indegree[next]--;
            if (indegree[next] == 0) {
                q.push(next);
            }
        }
    }

    for (int i = 1; i <= n; i++) {
        cout << result[i] << "\\n";
    }

    return 0;
}"""
        }
    ],
    "1517": [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

def merge_sort(arr):
    if len(arr) <= 1:
        return arr, 0

    mid = len(arr) // 2
    left, left_inv = merge_sort(arr[:mid])
    right, right_inv = merge_sort(arr[mid:])

    merged = []
    inversions = left_inv + right_inv
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            inversions += len(left) - i
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])

    return merged, inversions

n = int(input())
arr = list(map(int, input().split()))
_, result = merge_sort(arr)
print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static long inversions = 0;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        long[] arr = new long[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr[i] = Long.parseLong(st.nextToken());
        }

        mergeSort(arr, 0, n - 1);
        System.out.println(inversions);
    }

    static void mergeSort(long[] arr, int left, int right) {
        if (left >= right) return;

        int mid = (left + right) / 2;
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }

    static void merge(long[] arr, int left, int mid, int right) {
        long[] temp = new long[right - left + 1];
        int i = left, j = mid + 1, k = 0;

        while (i <= mid && j <= right) {
            if (arr[i] <= arr[j]) {
                temp[k++] = arr[i++];
            } else {
                temp[k++] = arr[j++];
                inversions += mid - i + 1;
            }
        }

        while (i <= mid) temp[k++] = arr[i++];
        while (j <= right) temp[k++] = arr[j++];

        for (int l = 0; l < temp.length; l++) {
            arr[left + l] = temp[l];
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
using namespace std;

long long inversions = 0;

void merge(vector<long long>& arr, int left, int mid, int right) {
    vector<long long> temp(right - left + 1);
    int i = left, j = mid + 1, k = 0;

    while (i <= mid && j <= right) {
        if (arr[i] <= arr[j]) {
            temp[k++] = arr[i++];
        } else {
            temp[k++] = arr[j++];
            inversions += mid - i + 1;
        }
    }

    while (i <= mid) temp[k++] = arr[i++];
    while (j <= right) temp[k++] = arr[j++];

    for (int l = 0; l < temp.size(); l++) {
        arr[left + l] = temp[l];
    }
}

void mergeSort(vector<long long>& arr, int left, int right) {
    if (left >= right) return;

    int mid = (left + right) / 2;
    mergeSort(arr, left, mid);
    mergeSort(arr, mid + 1, right);
    merge(arr, left, mid, right);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<long long> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    mergeSort(arr, 0, n - 1);
    cout << inversions << endl;

    return 0;
}"""
        }
    ],
    "1518": [
        {
            "language": "python",
            "code": """import sys
sys.setrecursionlimit(10000)

def solve():
    grid = []
    for _ in range(5):
        row = list(map(int, input().split()))
        grid.append(row)

    # Find fixed positions
    fixed = {}
    for i in range(5):
        for j in range(5):
            if grid[i][j] != 0:
                fixed[i] = (j, grid[i][j])

    # Check constraints
    for i in range(5):
        if i in fixed:
            j, val = fixed[i]
            # val must fit at position j in row i
            # Row i can have values from some range
            # Position j means j values come before val in this row
            pass

    # Try to fill the grid using backtracking with bipartite matching
    used = [False] * 26
    result = [[0] * 5 for _ in range(5)]

    # For fixed values
    for i in range(5):
        if i in fixed:
            j, val = fixed[i]
            result[i][j] = val
            used[val] = True

    def can_complete(row, col, remaining):
        if row == 5:
            return True

        next_row, next_col = (row, col + 1) if col < 4 else (row + 1, 0)

        if result[row][col] != 0:
            return can_complete(next_row, next_col, remaining)

        for num in sorted(remaining):
            # Check row constraint: must be greater than previous
            if col > 0 and num <= result[row][col - 1]:
                continue
            # Check if valid
            valid = True
            if col < 4:
                # Check if remaining numbers can fill the rest of the row
                greater_count = sum(1 for x in remaining if x > num and x != num)
                if greater_count < 4 - col:
                    valid = False

            if valid:
                result[row][col] = num
                new_remaining = remaining - {num}
                if can_complete(next_row, next_col, new_remaining):
                    return True
                result[row][col] = 0

        return False

    all_nums = set(range(1, 26)) - set(v for j, v in fixed.values())

    if can_complete(0, 0, all_nums):
        for row in result:
            print(' '.join(map(str, row)))
    else:
        print(-1)

solve()"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static int[][] grid = new int[5][5];
    static int[][] result = new int[5][5];
    static boolean[] used = new boolean[26];

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < 5; j++) {
                grid[i][j] = sc.nextInt();
                result[i][j] = grid[i][j];
                if (grid[i][j] != 0) {
                    used[grid[i][j]] = true;
                }
            }
        }

        if (solve(0, 0)) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 5; i++) {
                for (int j = 0; j < 5; j++) {
                    sb.append(result[i][j]);
                    if (j < 4) sb.append(" ");
                }
                sb.append("\\n");
            }
            System.out.print(sb);
        } else {
            System.out.println(-1);
        }
    }

    static boolean solve(int row, int col) {
        if (row == 5) return true;

        int nextRow = col == 4 ? row + 1 : row;
        int nextCol = col == 4 ? 0 : col + 1;

        if (result[row][col] != 0) {
            if (col > 0 && result[row][col] <= result[row][col - 1]) {
                return false;
            }
            return solve(nextRow, nextCol);
        }

        int minVal = col > 0 ? result[row][col - 1] + 1 : 1;

        for (int num = minVal; num <= 25; num++) {
            if (used[num]) continue;

            // Check if we can fill remaining positions in row
            int remaining = 4 - col;
            int available = 0;
            for (int k = num + 1; k <= 25; k++) {
                if (!used[k]) available++;
            }
            if (available < remaining) continue;

            result[row][col] = num;
            used[num] = true;

            if (solve(nextRow, nextCol)) return true;

            result[row][col] = 0;
            used[num] = false;
        }

        return false;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
using namespace std;

int grid[5][5];
int result[5][5];
bool used[26];

bool solve(int row, int col) {
    if (row == 5) return true;

    int nextRow = (col == 4) ? row + 1 : row;
    int nextCol = (col == 4) ? 0 : col + 1;

    if (result[row][col] != 0) {
        if (col > 0 && result[row][col] <= result[row][col - 1]) {
            return false;
        }
        return solve(nextRow, nextCol);
    }

    int minVal = (col > 0) ? result[row][col - 1] + 1 : 1;

    for (int num = minVal; num <= 25; num++) {
        if (used[num]) continue;

        int remaining = 4 - col;
        int available = 0;
        for (int k = num + 1; k <= 25; k++) {
            if (!used[k]) available++;
        }
        if (available < remaining) continue;

        result[row][col] = num;
        used[num] = true;

        if (solve(nextRow, nextCol)) return true;

        result[row][col] = 0;
        used[num] = false;
    }

    return false;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) {
            cin >> grid[i][j];
            result[i][j] = grid[i][j];
            if (grid[i][j] != 0) {
                used[grid[i][j]] = true;
            }
        }
    }

    if (solve(0, 0)) {
        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < 5; j++) {
                cout << result[i][j];
                if (j < 4) cout << " ";
            }
            cout << "\\n";
        }
    } else {
        cout << -1 << "\\n";
    }

    return 0;
}"""
        }
    ],
    "1519": [
        {
            "language": "python",
            "code": """import sys
sys.setrecursionlimit(2000000)

n = int(input())

# Memoization for game state
memo = {}

def get_substrings(num):
    s = str(num)
    subs = set()
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if j - i < len(s):  # proper substring
                sub = s[i:j]
                if sub[0] != '0':  # no leading zeros
                    subs.add(int(sub))
    subs.discard(0)
    return subs

def can_win(num):
    if num in memo:
        return memo[num]

    subs = get_substrings(num)
    if not subs:
        memo[num] = False
        return False

    for sub in subs:
        new_num = num - sub
        if new_num >= 0 and not can_win(new_num):
            memo[num] = True
            return True

    memo[num] = False
    return False

# Find the smallest winning move
subs = get_substrings(n)
result = -1

for sub in sorted(subs):
    new_num = n - sub
    if new_num >= 0 and not can_win(new_num):
        result = sub
        break

print(result)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static Map<Integer, Boolean> memo = new HashMap<>();

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        List<Integer> subs = getSubstrings(n);
        Collections.sort(subs);

        int result = -1;
        for (int sub : subs) {
            int newNum = n - sub;
            if (newNum >= 0 && !canWin(newNum)) {
                result = sub;
                break;
            }
        }

        System.out.println(result);
    }

    static List<Integer> getSubstrings(int num) {
        String s = String.valueOf(num);
        Set<Integer> subs = new HashSet<>();

        for (int i = 0; i < s.length(); i++) {
            for (int j = i + 1; j <= s.length(); j++) {
                if (j - i < s.length()) {
                    String sub = s.substring(i, j);
                    if (sub.charAt(0) != '0') {
                        subs.add(Integer.parseInt(sub));
                    }
                }
            }
        }
        subs.remove(0);
        return new ArrayList<>(subs);
    }

    static boolean canWin(int num) {
        if (memo.containsKey(num)) {
            return memo.get(num);
        }

        List<Integer> subs = getSubstrings(num);
        if (subs.isEmpty()) {
            memo.put(num, false);
            return false;
        }

        for (int sub : subs) {
            int newNum = num - sub;
            if (newNum >= 0 && !canWin(newNum)) {
                memo.put(num, true);
                return true;
            }
        }

        memo.put(num, false);
        return false;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <set>
#include <map>
#include <algorithm>
using namespace std;

map<int, bool> memo;

vector<int> getSubstrings(int num) {
    string s = to_string(num);
    set<int> subs;

    for (int i = 0; i < s.length(); i++) {
        for (int j = i + 1; j <= s.length(); j++) {
            if (j - i < s.length()) {
                string sub = s.substr(i, j - i);
                if (sub[0] != '0') {
                    subs.insert(stoi(sub));
                }
            }
        }
    }
    subs.erase(0);
    return vector<int>(subs.begin(), subs.end());
}

bool canWin(int num) {
    if (memo.count(num)) {
        return memo[num];
    }

    vector<int> subs = getSubstrings(num);
    if (subs.empty()) {
        memo[num] = false;
        return false;
    }

    for (int sub : subs) {
        int newNum = num - sub;
        if (newNum >= 0 && !canWin(newNum)) {
            memo[num] = true;
            return true;
        }
    }

    memo[num] = false;
    return false;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> subs = getSubstrings(n);
    sort(subs.begin(), subs.end());

    int result = -1;
    for (int sub : subs) {
        int newNum = n - sub;
        if (newNum >= 0 && !canWin(newNum)) {
            result = sub;
            break;
        }
    }

    cout << result << endl;

    return 0;
}"""
        }
    ]
}

# Update the JSON data
for problem in data:
    original_id = problem.get("original_id", "")
    if original_id in solutions_data:
        problem["solutions"] = solutions_data[original_id]

# Write back to the file
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated solutions for problems 1510-1519")
