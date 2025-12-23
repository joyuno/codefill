#!/usr/bin/env python3
"""
Script to update solutions for problems 1610-1619 in checkpoint JSON file.
"""

import json

def load_checkpoint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_checkpoint(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_solutions():
    """Return solutions for problems 1610-1619"""

    solutions = {}

    # Problem 1610: Pro Gamer Youngsik (DP simulation)
    solutions["1610"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
C, T = map(int, input().split())

costs = []
times = []
for _ in range(N - 1):
    c, t = map(int, input().split())
    costs.append(c)
    times.append(t)

if N == 1:
    print(1)
else:
    # dp[t][c] = max number of unit i at time t with cost c used
    # This is complex, let's simulate

    # At each time step, each unit can produce the next unit
    # dp[unit][time][cost] = count of that unit

    # Simpler approach: simulate step by step
    # units[i] = count of unit i+1 (0-indexed)
    units = [0] * N
    units[0] = 1  # Start with 1 unit of type 1

    total_time = sum(times)
    if total_time > T:
        # Cannot even produce one unit N, find best strategy
        pass

    # Greedy: at each time step, all available units produce next level
    # Track: (unit counts, time spent, cost spent)

    from functools import lru_cache

    # BFS/simulation approach
    # State: tuple of unit counts, but this is too large

    # Simplified: greedy simulation
    time_left = T
    cost_left = C
    units = [1] + [0] * (N - 1)

    # Each unit i can produce unit i+1 at cost costs[i] and time times[i]
    # All production happens simultaneously

    result = 0

    # Simulation: at each time step
    for t in range(T + 1):
        # Check if we can produce any units
        if t > 0:
            # Production happens
            new_units = units.copy()
            for i in range(N - 1):
                if units[i] > 0 and time_left >= times[i]:
                    # How many can we afford?
                    can_produce = min(units[i], cost_left // costs[i])
                    if can_produce > 0:
                        new_units[i + 1] += can_produce
                        cost_left -= can_produce * costs[i]
            units = new_units

        result = max(result, units[N - 1])
        time_left -= 1
        if time_left < 0:
            break

    print(units[N - 1])"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int C = sc.nextInt();
        int T = sc.nextInt();

        int[] costs = new int[N - 1];
        int[] times = new int[N - 1];

        for (int i = 0; i < N - 1; i++) {
            costs[i] = sc.nextInt();
            times[i] = sc.nextInt();
        }

        if (N == 1) {
            System.out.println(1);
            return;
        }

        // Simulation
        long[] units = new long[N];
        units[0] = 1;

        int timeLeft = T;
        int costLeft = C;

        while (timeLeft > 0) {
            long[] newUnits = units.clone();
            for (int i = 0; i < N - 1; i++) {
                if (units[i] > 0 && timeLeft >= times[i]) {
                    long canProduce = Math.min(units[i], costLeft / costs[i]);
                    if (canProduce > 0) {
                        newUnits[i + 1] += canProduce;
                        costLeft -= canProduce * costs[i];
                    }
                }
            }
            units = newUnits;
            timeLeft--;
        }

        System.out.println(units[N - 1]);
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

    int N, C, T;
    cin >> N >> C >> T;

    vector<int> costs(N - 1), times(N - 1);
    for (int i = 0; i < N - 1; i++) {
        cin >> costs[i] >> times[i];
    }

    if (N == 1) {
        cout << 1 << endl;
        return 0;
    }

    vector<long long> units(N, 0);
    units[0] = 1;

    int timeLeft = T;
    int costLeft = C;

    while (timeLeft > 0) {
        vector<long long> newUnits = units;
        for (int i = 0; i < N - 1; i++) {
            if (units[i] > 0 && timeLeft >= times[i]) {
                long long canProduce = min(units[i], (long long)(costLeft / costs[i]));
                if (canProduce > 0) {
                    newUnits[i + 1] += canProduce;
                    costLeft -= canProduce * costs[i];
                }
            }
        }
        units = newUnits;
        timeLeft--;
    }

    cout << units[N - 1] << endl;

    return 0;
}"""
        }
    ]

    # Problem 1611: Ganggangsullae (Hamiltonian decomposition)
    solutions["1611"] = [
        {
            "language": "python",
            "code": """n = int(input())

if n < 3:
    print(-1)
else:
    k = n // 2
    # Construct k rounds where each student holds hands with every other student exactly once
    # This is related to round-robin tournament scheduling

    for r in range(k):
        # In round r, we create a circle
        # Using the polygon method
        circle = [1]  # Fix position 1

        # For round r, rotate the remaining elements
        remaining = list(range(2, n + 1))
        # Rotate by r positions
        rotated = remaining[r:] + remaining[:r]

        # Create circle by alternating top and bottom
        top = rotated[:k]
        bottom = rotated[k:][::-1]

        result = [1]
        for i in range(k):
            if i < len(top):
                result.append(top[i])
            if i < len(bottom):
                result.append(bottom[i])

        # Adjust to have exactly n elements
        if len(result) > n:
            result = result[:n]

        print(' '.join(map(str, result)))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        if (n < 3) {
            System.out.println(-1);
            return;
        }

        int k = n / 2;

        for (int r = 0; r < k; r++) {
            List<Integer> remaining = new ArrayList<>();
            for (int i = 2; i <= n; i++) remaining.add(i);

            List<Integer> rotated = new ArrayList<>();
            for (int i = r; i < remaining.size(); i++) rotated.add(remaining.get(i));
            for (int i = 0; i < r; i++) rotated.add(remaining.get(i));

            List<Integer> top = new ArrayList<>();
            List<Integer> bottom = new ArrayList<>();
            for (int i = 0; i < k; i++) top.add(rotated.get(i));
            for (int i = k; i < rotated.size(); i++) bottom.add(rotated.get(i));
            Collections.reverse(bottom);

            List<Integer> result = new ArrayList<>();
            result.add(1);
            for (int i = 0; i < k; i++) {
                if (i < top.size()) result.add(top.get(i));
                if (i < bottom.size()) result.add(bottom.get(i));
            }

            while (result.size() > n) result.remove(result.size() - 1);

            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < result.size(); i++) {
                if (i > 0) sb.append(" ");
                sb.append(result.get(i));
            }
            System.out.println(sb);
        }
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

    int n;
    cin >> n;

    if (n < 3) {
        cout << -1 << endl;
        return 0;
    }

    int k = n / 2;

    for (int r = 0; r < k; r++) {
        vector<int> remaining;
        for (int i = 2; i <= n; i++) remaining.push_back(i);

        vector<int> rotated;
        for (int i = r; i < remaining.size(); i++) rotated.push_back(remaining[i]);
        for (int i = 0; i < r; i++) rotated.push_back(remaining[i]);

        vector<int> top, bottom;
        for (int i = 0; i < k; i++) top.push_back(rotated[i]);
        for (int i = k; i < rotated.size(); i++) bottom.push_back(rotated[i]);
        reverse(bottom.begin(), bottom.end());

        vector<int> result;
        result.push_back(1);
        for (int i = 0; i < k; i++) {
            if (i < top.size()) result.push_back(top[i]);
            if (i < bottom.size()) result.push_back(bottom[i]);
        }

        while (result.size() > n) result.pop_back();

        for (int i = 0; i < result.size(); i++) {
            if (i > 0) cout << " ";
            cout << result[i];
        }
        cout << endl;
    }

    return 0;
}"""
        }
    ]

    # Problem 1612: Playing with 1s (Number theory)
    solutions["1612"] = [
        {
            "language": "python",
            "code": """import sys

N = int(input())

# Find smallest k such that 111...1 (k ones) is divisible by N
# 111...1 = (10^k - 1) / 9
# We need (10^k - 1) / 9 % N == 0
# Which means 10^k - 1 % (9*N) == 0 if gcd(N, 9) divides appropriately
# Or simpler: 10^k % (9*N/gcd(9,N)) == 1

# If N is divisible by 2 or 5, it's impossible
# because 111...1 is always odd and not divisible by 5

if N % 2 == 0 or N % 5 == 0:
    print(-1)
else:
    # Find smallest k such that (10^k - 1) % (9 * N) == 0
    # Equivalently, 10^k % (9 * N / gcd(9, N)) == 1

    # Simpler: compute 111...1 mod N iteratively
    # 1, 11, 111, ... mod N
    # r_k = (r_{k-1} * 10 + 1) % N

    remainder = 0
    for k in range(1, 10 * N + 1):
        remainder = (remainder * 10 + 1) % N
        if remainder == 0:
            print(k)
            sys.exit()

    print(-1)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        if (N % 2 == 0 || N % 5 == 0) {
            System.out.println(-1);
            return;
        }

        long remainder = 0;
        for (int k = 1; k <= 10 * N; k++) {
            remainder = (remainder * 10 + 1) % N;
            if (remainder == 0) {
                System.out.println(k);
                return;
            }
        }

        System.out.println(-1);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    if (N % 2 == 0 || N % 5 == 0) {
        cout << -1 << endl;
        return 0;
    }

    long long remainder = 0;
    for (int k = 1; k <= 10 * N; k++) {
        remainder = (remainder * 10 + 1) % N;
        if (remainder == 0) {
            cout << k << endl;
            return 0;
        }
    }

    cout << -1 << endl;

    return 0;
}"""
        }
    ]

    # Problem 1613: History (Floyd-Warshall for reachability)
    solutions["1613"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

n, k = map(int, input().split())

# reach[i][j] = True if event i happened before event j
reach = [[False] * (n + 1) for _ in range(n + 1)]

for _ in range(k):
    a, b = map(int, input().split())
    reach[a][b] = True

# Floyd-Warshall to compute transitive closure
for m in range(1, n + 1):
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if reach[i][m] and reach[m][j]:
                reach[i][j] = True

s = int(input())
results = []
for _ in range(s):
    a, b = map(int, input().split())
    if reach[a][b]:
        results.append(-1)
    elif reach[b][a]:
        results.append(1)
    else:
        results.append(0)

print('\\n'.join(map(str, results)))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        boolean[][] reach = new boolean[n + 1][n + 1];

        for (int i = 0; i < k; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            reach[a][b] = true;
        }

        for (int m = 1; m <= n; m++) {
            for (int i = 1; i <= n; i++) {
                for (int j = 1; j <= n; j++) {
                    if (reach[i][m] && reach[m][j]) {
                        reach[i][j] = true;
                    }
                }
            }
        }

        int s = Integer.parseInt(br.readLine().trim());
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            if (reach[a][b]) {
                sb.append(-1).append("\\n");
            } else if (reach[b][a]) {
                sb.append(1).append("\\n");
            } else {
                sb.append(0).append("\\n");
            }
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

    int n, k;
    cin >> n >> k;

    vector<vector<bool>> reach(n + 1, vector<bool>(n + 1, false));

    for (int i = 0; i < k; i++) {
        int a, b;
        cin >> a >> b;
        reach[a][b] = true;
    }

    for (int m = 1; m <= n; m++) {
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++) {
                if (reach[i][m] && reach[m][j]) {
                    reach[i][j] = true;
                }
            }
        }
    }

    int s;
    cin >> s;
    for (int i = 0; i < s; i++) {
        int a, b;
        cin >> a >> b;
        if (reach[a][b]) {
            cout << -1 << "\\n";
        } else if (reach[b][a]) {
            cout << 1 << "\\n";
        } else {
            cout << 0 << "\\n";
        }
    }

    return 0;
}"""
        }
    ]

    # Problem 1614: Youngsik's Fingers (Math)
    solutions["1614"] = [
        {
            "language": "python",
            "code": """finger = int(input())
count = int(input())

# Fingers: 1(thumb), 2, 3, 4, 5(pinky)
# Pattern: 1,2,3,4,5,4,3,2,1,2,3,4,5,4,3,2,... (period 8)
# Positions in one cycle (8 counts):
# 1:1, 2:2, 3:3, 4:4, 5:5, 6:4, 7:3, 8:2
# Next cycle starts with 1 again

# For finger 1 and 5: they appear once per 8 counts
# For fingers 2,3,4: they appear twice per 8 counts

if count == 0:
    if finger == 1:
        print(0)
    else:
        print(finger - 1)
else:
    if finger == 1:
        # Finger 1 appears at positions 1, 9, 17, ... (every 8)
        # After using finger 1 'count' times, last position is 1 + 8*(count-1)
        # Can continue to positions 2, 3, 4, 5, 4, 3, 2 (7 more)
        # So max = 1 + 8*(count-1) + 7 = 8*count
        # But wait, if count=0, we can't even start (finger 1 is first)
        print(8 * count)
    elif finger == 5:
        # Finger 5 appears at positions 5, 13, 21, ... (every 8)
        # After using finger 5 'count' times, last position is 5 + 8*(count-1)
        # Can continue to 4, 3, 2, 1, 2, 3, 4 (7 more) until 5 again
        # Max = 5 + 8*(count-1) + 7 - 1 = 8*count + 4 - 1 = 8*count + 3
        # Actually last use of 5 is at 5 + 8*(count-1) = 8*count - 3
        # Then can go: 4,3,2,1 (4 more)
        print(8 * count - 3 + 4)
    else:
        # Fingers 2,3,4 appear twice per 8 counts
        # Finger 2: positions 2, 8, 10, 16, ...
        # Finger 3: positions 3, 7, 11, 15, ...
        # Finger 4: positions 4, 6, 12, 14, ...

        # After 'count' uses:
        # Number of complete pairs = count // 2
        # Extra = count % 2

        pairs = count // 2
        extra = count % 2

        if finger == 2:
            # Pairs at (2,8), (10,16), ...
            # After pairs*2 uses, last at 8 + 8*(pairs-1) = 8*pairs if pairs > 0
            # Then continue from there
            if extra == 0:
                # Last use at 8*pairs (position 8 in cycle = finger 2)
                # Can continue: 1 (1 more)
                last_pos = 8 * pairs
                print(last_pos + 1)
            else:
                # Extra use at 2 + 8*pairs
                # Continue: 3,4,5,4,3,2,1 until 2 again = 6 more
                last_pos = 2 + 8 * pairs
                print(last_pos + 6 + 1)
        elif finger == 3:
            # Positions: 3, 7, 11, 15, ...
            if extra == 0:
                # Last at 7 + 8*(pairs-1) = 8*pairs - 1
                last_pos = 8 * pairs - 1
                print(last_pos + 2)
            else:
                last_pos = 3 + 8 * pairs
                print(last_pos + 4 + 2)
        else:  # finger == 4
            # Positions: 4, 6, 12, 14, ...
            if extra == 0:
                last_pos = 6 + 8 * (pairs - 1) if pairs > 0 else 0
                if pairs == 0:
                    print(3)
                else:
                    print(last_pos + 3)
            else:
                last_pos = 4 + 8 * pairs
                print(last_pos + 1 + 3)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int finger = sc.nextInt();
        long count = sc.nextLong();

        if (count == 0) {
            if (finger == 1) {
                System.out.println(0);
            } else {
                System.out.println(finger - 1);
            }
        } else {
            if (finger == 1) {
                System.out.println(8 * count);
            } else if (finger == 5) {
                System.out.println(8 * count + 1);
            } else {
                long pairs = count / 2;
                long extra = count % 2;

                if (finger == 2) {
                    if (extra == 0) {
                        System.out.println(8 * pairs + 1);
                    } else {
                        System.out.println(2 + 8 * pairs + 7);
                    }
                } else if (finger == 3) {
                    if (extra == 0) {
                        System.out.println(8 * pairs - 1 + 2);
                    } else {
                        System.out.println(3 + 8 * pairs + 6);
                    }
                } else {
                    if (extra == 0) {
                        if (pairs == 0) {
                            System.out.println(3);
                        } else {
                            System.out.println(6 + 8 * (pairs - 1) + 3);
                        }
                    } else {
                        System.out.println(4 + 8 * pairs + 4);
                    }
                }
            }
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int finger;
    long long count;
    cin >> finger >> count;

    if (count == 0) {
        if (finger == 1) {
            cout << 0 << endl;
        } else {
            cout << finger - 1 << endl;
        }
    } else {
        if (finger == 1) {
            cout << 8 * count << endl;
        } else if (finger == 5) {
            cout << 8 * count + 1 << endl;
        } else {
            long long pairs = count / 2;
            long long extra = count % 2;

            if (finger == 2) {
                if (extra == 0) {
                    cout << 8 * pairs + 1 << endl;
                } else {
                    cout << 2 + 8 * pairs + 7 << endl;
                }
            } else if (finger == 3) {
                if (extra == 0) {
                    cout << 8 * pairs - 1 + 2 << endl;
                } else {
                    cout << 3 + 8 * pairs + 6 << endl;
                }
            } else {
                if (extra == 0) {
                    if (pairs == 0) {
                        cout << 3 << endl;
                    } else {
                        cout << 6 + 8 * (pairs - 1) + 3 << endl;
                    }
                } else {
                    cout << 4 + 8 * pairs + 4 << endl;
                }
            }
        }
    }

    return 0;
}"""
        }
    ]

    # Problem 1615: Counting Crossings (Segment Tree / Merge Sort)
    solutions["1615"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

def merge_sort_count(arr):
    if len(arr) <= 1:
        return arr, 0

    mid = len(arr) // 2
    left, left_inv = merge_sort_count(arr[:mid])
    right, right_inv = merge_sort_count(arr[mid:])

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

N, M = map(int, input().split())

edges = []
for _ in range(M):
    i, j = map(int, input().split())
    edges.append((i, j))

# Sort by first coordinate, then count inversions by second coordinate
edges.sort(key=lambda x: (x[0], x[1]))

# Extract second coordinates
seconds = [e[1] for e in edges]

# Count inversions using merge sort
_, crossings = merge_sort_count(seconds)

print(crossings)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static long inversions;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        int[][] edges = new int[M][2];
        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            edges[i][0] = Integer.parseInt(st.nextToken());
            edges[i][1] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(edges, (a, b) -> {
            if (a[0] != b[0]) return a[0] - b[0];
            return a[1] - b[1];
        });

        int[] seconds = new int[M];
        for (int i = 0; i < M; i++) {
            seconds[i] = edges[i][1];
        }

        inversions = 0;
        mergeSort(seconds, 0, M - 1);

        System.out.println(inversions);
    }

    static void mergeSort(int[] arr, int left, int right) {
        if (left >= right) return;

        int mid = (left + right) / 2;
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }

    static void merge(int[] arr, int left, int mid, int right) {
        int[] temp = new int[right - left + 1];
        int i = left, j = mid + 1, k = 0;

        while (i <= mid && j <= right) {
            if (arr[i] <= arr[j]) {
                temp[k++] = arr[i++];
            } else {
                temp[k++] = arr[j++];
                inversions += (mid - i + 1);
            }
        }

        while (i <= mid) temp[k++] = arr[i++];
        while (j <= right) temp[k++] = arr[j++];

        for (i = 0; i < temp.length; i++) {
            arr[left + i] = temp[i];
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

long long inversions = 0;

void merge(vector<int>& arr, int left, int mid, int right) {
    vector<int> temp(right - left + 1);
    int i = left, j = mid + 1, k = 0;

    while (i <= mid && j <= right) {
        if (arr[i] <= arr[j]) {
            temp[k++] = arr[i++];
        } else {
            temp[k++] = arr[j++];
            inversions += (mid - i + 1);
        }
    }

    while (i <= mid) temp[k++] = arr[i++];
    while (j <= right) temp[k++] = arr[j++];

    for (int i = 0; i < temp.size(); i++) {
        arr[left + i] = temp[i];
    }
}

void mergeSort(vector<int>& arr, int left, int right) {
    if (left >= right) return;

    int mid = (left + right) / 2;
    mergeSort(arr, left, mid);
    mergeSort(arr, mid + 1, right);
    merge(arr, left, mid, right);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    vector<pair<int, int>> edges(M);
    for (int i = 0; i < M; i++) {
        cin >> edges[i].first >> edges[i].second;
    }

    sort(edges.begin(), edges.end());

    vector<int> seconds(M);
    for (int i = 0; i < M; i++) {
        seconds[i] = edges[i].second;
    }

    mergeSort(seconds, 0, M - 1);

    cout << inversions << endl;

    return 0;
}"""
        }
    ]

    # Problem 1616: Drum (De Bruijn sequence)
    solutions["1616"] = [
        {
            "language": "python",
            "code": """import sys
sys.setrecursionlimit(20000000)

def de_bruijn(k, n):
    # Generate de Bruijn sequence for k symbols and length n
    alphabet = list(range(k))
    a = [0] * (k * n)
    sequence = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                sequence.extend(a[1:p+1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return sequence

K, M = map(int, input().split())

if M == 1:
    # Simple case: just print 0, 1, ..., K-1
    print(' '.join(map(str, range(K))))
else:
    seq = de_bruijn(K, M)
    # The sequence length should be K^M
    # Add M-1 elements from the beginning to complete the cycle
    result = seq + seq[:M-1]
    print(' '.join(map(str, result[:K**M])))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    static int K, M;
    static int[] a;
    static List<Integer> sequence;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        K = sc.nextInt();
        M = sc.nextInt();

        if (M == 1) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < K; i++) {
                if (i > 0) sb.append(" ");
                sb.append(i);
            }
            System.out.println(sb);
            return;
        }

        a = new int[K * M + 1];
        sequence = new ArrayList<>();

        db(1, 1);

        StringBuilder sb = new StringBuilder();
        int total = (int) Math.pow(K, M);
        for (int i = 0; i < total; i++) {
            if (i > 0) sb.append(" ");
            sb.append(sequence.get(i % sequence.size()));
        }
        System.out.println(sb);
    }

    static void db(int t, int p) {
        if (t > M) {
            if (M % p == 0) {
                for (int i = 1; i <= p; i++) {
                    sequence.add(a[i]);
                }
            }
        } else {
            a[t] = a[t - p];
            db(t + 1, p);
            for (int j = a[t - p] + 1; j < K; j++) {
                a[t] = j;
                db(t + 1, t);
            }
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

int K, M;
vector<int> a;
vector<int> sequence;

void db(int t, int p) {
    if (t > M) {
        if (M % p == 0) {
            for (int i = 1; i <= p; i++) {
                sequence.push_back(a[i]);
            }
        }
    } else {
        a[t] = a[t - p];
        db(t + 1, p);
        for (int j = a[t - p] + 1; j < K; j++) {
            a[t] = j;
            db(t + 1, t);
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> K >> M;

    if (M == 1) {
        for (int i = 0; i < K; i++) {
            if (i > 0) cout << " ";
            cout << i;
        }
        cout << endl;
        return 0;
    }

    a.resize(K * M + 1, 0);
    db(1, 1);

    int total = (int) pow(K, M);
    for (int i = 0; i < total; i++) {
        if (i > 0) cout << " ";
        cout << sequence[i % sequence.size()];
    }
    cout << endl;

    return 0;
}"""
        }
    ]

    # Problem 1617: Ace (Card game)
    solutions["1617"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
cards = list(map(int, input().split()))

# Sort cards
cards.sort()

# Greedy: pair smallest with largest to maximize difference sum
# But actually we want to maximize the number of pairs where |a - b| <= 1

# Count pairs that differ by at most 1
count = 0
used = [False] * N

for i in range(N):
    if used[i]:
        continue
    for j in range(i + 1, N):
        if used[j]:
            continue
        if abs(cards[i] - cards[j]) <= 1:
            used[i] = True
            used[j] = True
            count += 1
            break

print(count)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] cards = new int[N];
        for (int i = 0; i < N; i++) {
            cards[i] = sc.nextInt();
        }

        Arrays.sort(cards);

        boolean[] used = new boolean[N];
        int count = 0;

        for (int i = 0; i < N; i++) {
            if (used[i]) continue;
            for (int j = i + 1; j < N; j++) {
                if (used[j]) continue;
                if (Math.abs(cards[i] - cards[j]) <= 1) {
                    used[i] = true;
                    used[j] = true;
                    count++;
                    break;
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
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;
    vector<int> cards(N);
    for (int i = 0; i < N; i++) {
        cin >> cards[i];
    }

    sort(cards.begin(), cards.end());

    vector<bool> used(N, false);
    int count = 0;

    for (int i = 0; i < N; i++) {
        if (used[i]) continue;
        for (int j = i + 1; j < N; j++) {
            if (used[j]) continue;
            if (abs(cards[i] - cards[j]) <= 1) {
                used[i] = true;
                used[j] = true;
                count++;
                break;
            }
        }
    }

    cout << count << endl;

    return 0;
}"""
        }
    ]

    # Problem 1618: Divisor sum (Number theory)
    solutions["1618"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
numbers = []
for _ in range(N):
    numbers.append(int(input()))

# Find the common divisors
# A number that divides all is a common divisor
# Find GCD of all numbers

from math import gcd
from functools import reduce

g = reduce(gcd, numbers)

# Sum of divisors of g
def sum_of_divisors(n):
    total = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
        i += 1
    return total

print(sum_of_divisors(g))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        long[] numbers = new long[N];
        for (int i = 0; i < N; i++) {
            numbers[i] = sc.nextLong();
        }

        long g = numbers[0];
        for (int i = 1; i < N; i++) {
            g = gcd(g, numbers[i]);
        }

        System.out.println(sumOfDivisors(g));
    }

    static long gcd(long a, long b) {
        while (b != 0) {
            long t = b;
            b = a % b;
            a = t;
        }
        return a;
    }

    static long sumOfDivisors(long n) {
        long total = 0;
        for (long i = 1; i * i <= n; i++) {
            if (n % i == 0) {
                total += i;
                if (i != n / i) {
                    total += n / i;
                }
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
#include <numeric>
using namespace std;

long long gcd(long long a, long long b) {
    while (b != 0) {
        long long t = b;
        b = a % b;
        a = t;
    }
    return a;
}

long long sumOfDivisors(long long n) {
    long long total = 0;
    for (long long i = 1; i * i <= n; i++) {
        if (n % i == 0) {
            total += i;
            if (i != n / i) {
                total += n / i;
            }
        }
    }
    return total;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;
    vector<long long> numbers(N);
    for (int i = 0; i < N; i++) {
        cin >> numbers[i];
    }

    long long g = numbers[0];
    for (int i = 1; i < N; i++) {
        g = gcd(g, numbers[i]);
    }

    cout << sumOfDivisors(g) << endl;

    return 0;
}"""
        }
    ]

    # Problem 1619: Collinear Points (Geometry)
    solutions["1619"] = [
        {
            "language": "python",
            "code": """import sys
from collections import defaultdict
from math import gcd

input = sys.stdin.readline

N = int(input())
points = []
for _ in range(N):
    x, y = map(int, input().split())
    points.append((x, y))

if N < 3:
    print(-1)
else:
    max_count = 0

    for i in range(N):
        slopes = defaultdict(int)
        same = 1

        for j in range(N):
            if i == j:
                continue

            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]

            if dx == 0 and dy == 0:
                same += 1
            else:
                g = gcd(abs(dx), abs(dy))
                dx //= g
                dy //= g
                # Normalize direction
                if dx < 0 or (dx == 0 and dy < 0):
                    dx, dy = -dx, -dy
                slopes[(dx, dy)] += 1

        if slopes:
            max_count = max(max_count, max(slopes.values()) + same)
        else:
            max_count = max(max_count, same)

    if max_count < 3:
        print(-1)
    else:
        print(max_count)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[][] points = new int[N][2];
        for (int i = 0; i < N; i++) {
            points[i][0] = sc.nextInt();
            points[i][1] = sc.nextInt();
        }

        if (N < 3) {
            System.out.println(-1);
            return;
        }

        int maxCount = 0;

        for (int i = 0; i < N; i++) {
            Map<String, Integer> slopes = new HashMap<>();
            int same = 1;

            for (int j = 0; j < N; j++) {
                if (i == j) continue;

                int dx = points[j][0] - points[i][0];
                int dy = points[j][1] - points[i][1];

                if (dx == 0 && dy == 0) {
                    same++;
                } else {
                    int g = gcd(Math.abs(dx), Math.abs(dy));
                    dx /= g;
                    dy /= g;
                    if (dx < 0 || (dx == 0 && dy < 0)) {
                        dx = -dx;
                        dy = -dy;
                    }
                    String key = dx + "," + dy;
                    slopes.put(key, slopes.getOrDefault(key, 0) + 1);
                }
            }

            int localMax = 0;
            for (int v : slopes.values()) {
                localMax = Math.max(localMax, v);
            }
            maxCount = Math.max(maxCount, localMax + same);
        }

        if (maxCount < 3) {
            System.out.println(-1);
        } else {
            System.out.println(maxCount);
        }
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
#include <map>
#include <algorithm>
using namespace std;

int gcd(int a, int b) {
    while (b != 0) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;
    vector<pair<int, int>> points(N);
    for (int i = 0; i < N; i++) {
        cin >> points[i].first >> points[i].second;
    }

    if (N < 3) {
        cout << -1 << endl;
        return 0;
    }

    int maxCount = 0;

    for (int i = 0; i < N; i++) {
        map<pair<int, int>, int> slopes;
        int same = 1;

        for (int j = 0; j < N; j++) {
            if (i == j) continue;

            int dx = points[j].first - points[i].first;
            int dy = points[j].second - points[i].second;

            if (dx == 0 && dy == 0) {
                same++;
            } else {
                int g = gcd(abs(dx), abs(dy));
                dx /= g;
                dy /= g;
                if (dx < 0 || (dx == 0 && dy < 0)) {
                    dx = -dx;
                    dy = -dy;
                }
                slopes[{dx, dy}]++;
            }
        }

        int localMax = 0;
        for (auto& p : slopes) {
            localMax = max(localMax, p.second);
        }
        maxCount = max(maxCount, localMax + same);
    }

    if (maxCount < 3) {
        cout << -1 << endl;
    } else {
        cout << maxCount << endl;
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
    solutions = get_solutions()

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
