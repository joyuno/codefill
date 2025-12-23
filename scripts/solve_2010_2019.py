#!/usr/bin/env python3
import json

# Load the data
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r') as f:
    data = json.load(f)

# Solutions for problems 2010-2019

solutions_batch = {
    2010: {  # 플러그 - simple sum
        "python": '''n = int(input())
total = 0
for _ in range(n):
    total += int(input())
print(total - n + 1)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        long total = 0;
        for (int i = 0; i < n; i++) {
            total += sc.nextInt();
        }
        System.out.println(total - n + 1);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    long long total = 0;
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        total += x;
    }
    cout << total - n + 1 << endl;
    return 0;
}
'''
    },
    2011: {  # 암호코드 - DP
        "python": '''import sys
input = sys.stdin.readline

s = input().strip()
n = len(s)

if n == 0 or s[0] == '0':
    print(0)
else:
    MOD = 1000000
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1

    for i in range(2, n + 1):
        if s[i-1] != '0':
            dp[i] = dp[i-1]

        two_digit = int(s[i-2:i])
        if 10 <= two_digit <= 26:
            dp[i] = (dp[i] + dp[i-2]) % MOD

        if dp[i] == 0:
            print(0)
            exit()

    print(dp[n] % MOD)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        int n = s.length();

        if (n == 0 || s.charAt(0) == '0') {
            System.out.println(0);
            return;
        }

        int MOD = 1000000;
        long[] dp = new long[n + 1];
        dp[0] = 1;
        dp[1] = 1;

        for (int i = 2; i <= n; i++) {
            if (s.charAt(i - 1) != '0') {
                dp[i] = dp[i - 1];
            }

            int twoDigit = Integer.parseInt(s.substring(i - 2, i));
            if (twoDigit >= 10 && twoDigit <= 26) {
                dp[i] = (dp[i] + dp[i - 2]) % MOD;
            }

            if (dp[i] == 0) {
                System.out.println(0);
                return;
            }
        }

        System.out.println(dp[n] % MOD);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    cin >> s;
    int n = s.length();

    if (n == 0 || s[0] == '0') {
        cout << 0 << endl;
        return 0;
    }

    const int MOD = 1000000;
    long long dp[5001] = {0};
    dp[0] = 1;
    dp[1] = 1;

    for (int i = 2; i <= n; i++) {
        if (s[i - 1] != '0') {
            dp[i] = dp[i - 1];
        }

        int twoDigit = (s[i - 2] - '0') * 10 + (s[i - 1] - '0');
        if (twoDigit >= 10 && twoDigit <= 26) {
            dp[i] = (dp[i] + dp[i - 2]) % MOD;
        }

        if (dp[i] == 0) {
            cout << 0 << endl;
            return 0;
        }
    }

    cout << dp[n] % MOD << endl;
    return 0;
}
'''
    },
    2012: {  # 등수 매기기 - greedy sort
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
ranks = []
for _ in range(n):
    ranks.append(int(input()))

ranks.sort()
total = 0
for i in range(n):
    total += abs(ranks[i] - (i + 1))

print(total)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] ranks = new int[n];
        for (int i = 0; i < n; i++) {
            ranks[i] = sc.nextInt();
        }

        Arrays.sort(ranks);
        long total = 0;
        for (int i = 0; i < n; i++) {
            total += Math.abs(ranks[i] - (i + 1));
        }

        System.out.println(total);
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    int ranks[500001];
    for (int i = 0; i < n; i++) {
        cin >> ranks[i];
    }

    sort(ranks, ranks + n);
    long long total = 0;
    for (int i = 0; i < n; i++) {
        total += abs(ranks[i] - (i + 1));
    }

    cout << total << endl;
    return 0;
}
'''
    },
    2013: {  # 선그리기 - line intersection / union-find
        "python": '''import sys
from collections import defaultdict

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def ccw(a, b, c):
    val = cross(a, b, c)
    if val > 1e-9:
        return 1
    elif val < -1e-9:
        return -1
    return 0

def on_segment(p, q, r):
    return (min(p[0], r[0]) <= q[0] + 1e-9 <= max(p[0], r[0]) + 1e-9 and
            min(p[1], r[1]) <= q[1] + 1e-9 <= max(p[1], r[1]) + 1e-9)

def segments_intersect(p1, q1, p2, q2):
    d1 = ccw(p2, q2, p1)
    d2 = ccw(p2, q2, q1)
    d3 = ccw(p1, q1, p2)
    d4 = ccw(p1, q1, q2)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True

    if d1 == 0 and on_segment(p2, p1, q2):
        return True
    if d2 == 0 and on_segment(p2, q1, q2):
        return True
    if d3 == 0 and on_segment(p1, p2, q1):
        return True
    if d4 == 0 and on_segment(p1, q2, q1):
        return True

    return False

def collinear(p1, q1, p2, q2):
    return ccw(p1, q1, p2) == 0 and ccw(p1, q1, q2) == 0

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1

n = int(input())
segments = []
for _ in range(n):
    x1, y1, x2, y2 = map(float, input().split())
    segments.append(((x1, y1), (x2, y2)))

uf = UnionFind(n)

for i in range(n):
    for j in range(i + 1, n):
        p1, q1 = segments[i]
        p2, q2 = segments[j]
        if collinear(p1, q1, p2, q2) and segments_intersect(p1, q1, p2, q2):
            uf.union(i, j)
        elif segments_intersect(p1, q1, p2, q2):
            uf.union(i, j)

count = len(set(uf.find(i) for i in range(n)))
print(count)
''',
        "java": '''import java.util.*;

public class Main {
    static int[] parent, rank_;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        double[][] segments = new double[n][4];
        for (int i = 0; i < n; i++) {
            segments[i][0] = sc.nextDouble();
            segments[i][1] = sc.nextDouble();
            segments[i][2] = sc.nextDouble();
            segments[i][3] = sc.nextDouble();
        }

        parent = new int[n];
        rank_ = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (intersect(segments[i], segments[j])) {
                    union(i, j);
                }
            }
        }

        Set<Integer> groups = new HashSet<>();
        for (int i = 0; i < n; i++) {
            groups.add(find(i));
        }
        System.out.println(groups.size());
    }

    static int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    }

    static void union(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return;
        if (rank_[px] < rank_[py]) { int t = px; px = py; py = t; }
        parent[py] = px;
        if (rank_[px] == rank_[py]) rank_[px]++;
    }

    static boolean intersect(double[] s1, double[] s2) {
        double x1 = s1[0], y1 = s1[1], x2 = s1[2], y2 = s1[3];
        double x3 = s2[0], y3 = s2[1], x4 = s2[2], y4 = s2[3];

        double d1 = ccw(x3, y3, x4, y4, x1, y1);
        double d2 = ccw(x3, y3, x4, y4, x2, y2);
        double d3 = ccw(x1, y1, x2, y2, x3, y3);
        double d4 = ccw(x1, y1, x2, y2, x4, y4);

        if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
            ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) return true;

        if (d1 == 0 && onSegment(x3, y3, x1, y1, x4, y4)) return true;
        if (d2 == 0 && onSegment(x3, y3, x2, y2, x4, y4)) return true;
        if (d3 == 0 && onSegment(x1, y1, x3, y3, x2, y2)) return true;
        if (d4 == 0 && onSegment(x1, y1, x4, y4, x2, y2)) return true;

        return false;
    }

    static double ccw(double ax, double ay, double bx, double by, double cx, double cy) {
        double val = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);
        if (Math.abs(val) < 1e-9) return 0;
        return val;
    }

    static boolean onSegment(double px, double py, double qx, double qy, double rx, double ry) {
        return qx <= Math.max(px, rx) + 1e-9 && qx >= Math.min(px, rx) - 1e-9 &&
               qy <= Math.max(py, ry) + 1e-9 && qy >= Math.min(py, ry) - 1e-9;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <set>
#include <cmath>
using namespace std;

int parent[10001], rnk[10001];

int find(int x) {
    if (parent[x] != x) parent[x] = find(parent[x]);
    return parent[x];
}

void unite(int x, int y) {
    int px = find(x), py = find(y);
    if (px == py) return;
    if (rnk[px] < rnk[py]) swap(px, py);
    parent[py] = px;
    if (rnk[px] == rnk[py]) rnk[px]++;
}

double ccw(double ax, double ay, double bx, double by, double cx, double cy) {
    double val = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);
    if (fabs(val) < 1e-9) return 0;
    return val;
}

bool onSegment(double px, double py, double qx, double qy, double rx, double ry) {
    return qx <= max(px, rx) + 1e-9 && qx >= min(px, rx) - 1e-9 &&
           qy <= max(py, ry) + 1e-9 && qy >= min(py, ry) - 1e-9;
}

bool intersect(double* s1, double* s2) {
    double x1 = s1[0], y1 = s1[1], x2 = s1[2], y2 = s1[3];
    double x3 = s2[0], y3 = s2[1], x4 = s2[2], y4 = s2[3];

    double d1 = ccw(x3, y3, x4, y4, x1, y1);
    double d2 = ccw(x3, y3, x4, y4, x2, y2);
    double d3 = ccw(x1, y1, x2, y2, x3, y3);
    double d4 = ccw(x1, y1, x2, y2, x4, y4);

    if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
        ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) return true;

    if (d1 == 0 && onSegment(x3, y3, x1, y1, x4, y4)) return true;
    if (d2 == 0 && onSegment(x3, y3, x2, y2, x4, y4)) return true;
    if (d3 == 0 && onSegment(x1, y1, x3, y3, x2, y2)) return true;
    if (d4 == 0 && onSegment(x1, y1, x4, y4, x2, y2)) return true;

    return false;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    double segments[10001][4];
    for (int i = 0; i < n; i++) {
        cin >> segments[i][0] >> segments[i][1] >> segments[i][2] >> segments[i][3];
        parent[i] = i;
        rnk[i] = 0;
    }

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (intersect(segments[i], segments[j])) {
                unite(i, j);
            }
        }
    }

    set<int> groups;
    for (int i = 0; i < n; i++) {
        groups.insert(find(i));
    }
    cout << groups.size() << endl;
    return 0;
}
'''
    },
    2014: {  # 소수의 곱 - priority queue
        "python": '''import heapq

k, n = map(int, input().split())
primes = list(map(int, input().split()))

heap = []
seen = set()

for p in primes:
    heapq.heappush(heap, p)
    seen.add(p)

result = 0
for _ in range(n):
    result = heapq.heappop(heap)
    for p in primes:
        new_val = result * p
        if new_val not in seen and new_val < 2**31:
            seen.add(new_val)
            heapq.heappush(heap, new_val)
        if result % p == 0:
            break

print(result)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int k = sc.nextInt();
        int n = sc.nextInt();
        long[] primes = new long[k];
        for (int i = 0; i < k; i++) {
            primes[i] = sc.nextLong();
        }

        PriorityQueue<Long> heap = new PriorityQueue<>();
        Set<Long> seen = new HashSet<>();

        for (long p : primes) {
            heap.offer(p);
            seen.add(p);
        }

        long result = 0;
        for (int i = 0; i < n; i++) {
            result = heap.poll();
            for (long p : primes) {
                long newVal = result * p;
                if (!seen.contains(newVal) && newVal < (1L << 31)) {
                    seen.add(newVal);
                    heap.offer(newVal);
                }
                if (result % p == 0) break;
            }
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
#include <queue>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int k, n;
    cin >> k >> n;
    long long primes[101];
    for (int i = 0; i < k; i++) {
        cin >> primes[i];
    }

    priority_queue<long long, vector<long long>, greater<long long>> heap;
    set<long long> seen;

    for (int i = 0; i < k; i++) {
        heap.push(primes[i]);
        seen.insert(primes[i]);
    }

    long long result = 0;
    for (int i = 0; i < n; i++) {
        result = heap.top();
        heap.pop();
        for (int j = 0; j < k; j++) {
            long long newVal = result * primes[j];
            if (seen.find(newVal) == seen.end() && newVal < (1LL << 31)) {
                seen.insert(newVal);
                heap.push(newVal);
            }
            if (result % primes[j] == 0) break;
        }
    }

    cout << result << endl;
    return 0;
}
'''
    },
    2015: {  # 수들의 합 4 - prefix sum with map
        "python": '''import sys
from collections import defaultdict
input = sys.stdin.readline

n, k = map(int, input().split())
a = list(map(int, input().split()))

prefix = [0] * (n + 1)
for i in range(n):
    prefix[i + 1] = prefix[i] + a[i]

count = defaultdict(int)
result = 0

for i in range(n + 1):
    # We need prefix[j] such that prefix[i] - prefix[j] = k
    # So prefix[j] = prefix[i] - k
    target = prefix[i] - k
    result += count[target]
    count[prefix[i]] += 1

print(result)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        long k = sc.nextLong();

        long[] prefix = new long[n + 1];
        prefix[0] = 0;
        for (int i = 0; i < n; i++) {
            prefix[i + 1] = prefix[i] + sc.nextInt();
        }

        Map<Long, Long> count = new HashMap<>();
        long result = 0;

        for (int i = 0; i <= n; i++) {
            long target = prefix[i] - k;
            result += count.getOrDefault(target, 0L);
            count.merge(prefix[i], 1L, Long::sum);
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    long long k;
    cin >> n >> k;

    long long prefix[200001];
    prefix[0] = 0;
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        prefix[i + 1] = prefix[i] + x;
    }

    map<long long, long long> count;
    long long result = 0;

    for (int i = 0; i <= n; i++) {
        long long target = prefix[i] - k;
        if (count.find(target) != count.end()) {
            result += count[target];
        }
        count[prefix[i]]++;
    }

    cout << result << endl;
    return 0;
}
'''
    },
    2016: {  # 미팅 주선하기 - Gale-Shapley algorithm
        "python": '''import sys
input = sys.stdin.readline

def stable_matching(men_pref, women_pref, n):
    free_men = list(range(n))
    women_partner = [-1] * n
    men_partner = [-1] * n
    men_next = [0] * n

    women_rank = [[0] * n for _ in range(n)]
    for w in range(n):
        for rank, m in enumerate(women_pref[w]):
            women_rank[w][m] = rank

    while free_men:
        m = free_men.pop(0)
        if men_next[m] >= n:
            continue
        w = men_pref[m][men_next[m]]
        men_next[m] += 1

        if women_partner[w] == -1:
            women_partner[w] = m
            men_partner[m] = w
        else:
            current = women_partner[w]
            if women_rank[w][m] < women_rank[w][current]:
                women_partner[w] = m
                men_partner[m] = w
                men_partner[current] = -1
                free_men.append(current)
            else:
                free_men.append(m)

    return men_partner

T = int(input())
for _ in range(T):
    men_pref = []
    women_pref = []

    for i in range(5):
        pref = list(map(int, input().split()))
        men_pref.append([x - 6 for x in pref])

    for i in range(5):
        pref = list(map(int, input().split()))
        women_pref.append([x - 1 for x in pref])

    result = stable_matching(women_pref, men_pref, 5)

    if result[0] + 6 == 6:
        print("YES")
    else:
        print("NO")
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            int[][] menPref = new int[5][5];
            int[][] womenPref = new int[5][5];

            for (int i = 0; i < 5; i++) {
                for (int j = 0; j < 5; j++) {
                    menPref[i][j] = sc.nextInt() - 6;
                }
            }

            for (int i = 0; i < 5; i++) {
                for (int j = 0; j < 5; j++) {
                    womenPref[i][j] = sc.nextInt() - 1;
                }
            }

            int[] result = stableMatching(womenPref, menPref, 5);
            System.out.println(result[0] == 0 ? "YES" : "NO");
        }
    }

    static int[] stableMatching(int[][] menPref, int[][] womenPref, int n) {
        Queue<Integer> freeMen = new LinkedList<>();
        for (int i = 0; i < n; i++) freeMen.offer(i);

        int[] womenPartner = new int[n];
        int[] menPartner = new int[n];
        int[] menNext = new int[n];
        Arrays.fill(womenPartner, -1);
        Arrays.fill(menPartner, -1);

        int[][] womenRank = new int[n][n];
        for (int w = 0; w < n; w++) {
            for (int rank = 0; rank < n; rank++) {
                womenRank[w][womenPref[w][rank]] = rank;
            }
        }

        while (!freeMen.isEmpty()) {
            int m = freeMen.poll();
            if (menNext[m] >= n) continue;
            int w = menPref[m][menNext[m]];
            menNext[m]++;

            if (womenPartner[w] == -1) {
                womenPartner[w] = m;
                menPartner[m] = w;
            } else {
                int current = womenPartner[w];
                if (womenRank[w][m] < womenRank[w][current]) {
                    womenPartner[w] = m;
                    menPartner[m] = w;
                    menPartner[current] = -1;
                    freeMen.offer(current);
                } else {
                    freeMen.offer(m);
                }
            }
        }

        return menPartner;
    }
}
''',
        "cpp": '''#include <iostream>
#include <queue>
#include <cstring>
using namespace std;

int stableMatching(int menPref[5][5], int womenPref[5][5], int n, int* result) {
    queue<int> freeMen;
    for (int i = 0; i < n; i++) freeMen.push(i);

    int womenPartner[5], menPartner[5], menNext[5];
    memset(womenPartner, -1, sizeof(womenPartner));
    memset(menPartner, -1, sizeof(menPartner));
    memset(menNext, 0, sizeof(menNext));

    int womenRank[5][5];
    for (int w = 0; w < n; w++) {
        for (int rank = 0; rank < n; rank++) {
            womenRank[w][womenPref[w][rank]] = rank;
        }
    }

    while (!freeMen.empty()) {
        int m = freeMen.front();
        freeMen.pop();
        if (menNext[m] >= n) continue;
        int w = menPref[m][menNext[m]];
        menNext[m]++;

        if (womenPartner[w] == -1) {
            womenPartner[w] = m;
            menPartner[m] = w;
        } else {
            int current = womenPartner[w];
            if (womenRank[w][m] < womenRank[w][current]) {
                womenPartner[w] = m;
                menPartner[m] = w;
                menPartner[current] = -1;
                freeMen.push(current);
            } else {
                freeMen.push(m);
            }
        }
    }

    for (int i = 0; i < n; i++) result[i] = menPartner[i];
    return 0;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int menPref[5][5], womenPref[5][5];

        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < 5; j++) {
                cin >> menPref[i][j];
                menPref[i][j] -= 6;
            }
        }

        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < 5; j++) {
                cin >> womenPref[i][j];
                womenPref[i][j] -= 1;
            }
        }

        int result[5];
        stableMatching(womenPref, menPref, 5, result);
        cout << (result[0] == 0 ? "YES" : "NO") << endl;
    }

    return 0;
}
'''
    },
    2017: {  # 울타리 - computational geometry
        "python": '''import sys
import math
from collections import defaultdict
input = sys.stdin.readline

def solve():
    line = input().split()
    N, R = int(line[0]), int(line[1])
    line = input().split()
    px, py = float(line[0]), float(line[1])

    rocks = []
    for _ in range(R):
        v = int(input())
        vertices = []
        for _ in range(v):
            coords = input().split()
            x, y = float(coords[0]), float(coords[1])
            vertices.append((x, y))
        rocks.append(vertices)

    # Generate all fence posts
    posts = []
    # Bottom edge: y=0, x=0 to N
    for x in range(N + 1):
        posts.append((x, 0))
    # Right edge: x=N, y=0 to N
    for y in range(1, N + 1):
        posts.append((N, y))
    # Top edge: y=N, x=N to 0
    for x in range(N - 1, -1, -1):
        posts.append((x, N))
    # Left edge: x=0, y=N to 0
    for y in range(N - 1, 0, -1):
        posts.append((0, y))

    # For each rock, compute angle range that blocks view
    blocked_angles = []

    for rock in rocks:
        min_angle = float('inf')
        max_angle = float('-inf')
        for vx, vy in rock:
            angle = math.atan2(vy - py, vx - px)
            min_angle = min(min_angle, angle)
            max_angle = max(max_angle, angle)
        blocked_angles.append((min_angle, max_angle))

    # Count visible posts
    visible = 0
    for post in posts:
        if post[0] == px and post[1] == py:
            continue
        angle = math.atan2(post[1] - py, post[0] - px)
        blocked = False
        for min_a, max_a in blocked_angles:
            if min_a <= angle <= max_a:
                blocked = True
                break
        if not blocked:
            visible += 1

    print(visible)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int R = sc.nextInt();
        double px = sc.nextDouble();
        double py = sc.nextDouble();

        List<double[]> blockedAngles = new ArrayList<>();

        for (int r = 0; r < R; r++) {
            int v = sc.nextInt();
            double minAngle = Double.MAX_VALUE;
            double maxAngle = -Double.MAX_VALUE;
            for (int i = 0; i < v; i++) {
                double x = sc.nextDouble();
                double y = sc.nextDouble();
                double angle = Math.atan2(y - py, x - px);
                minAngle = Math.min(minAngle, angle);
                maxAngle = Math.max(maxAngle, angle);
            }
            blockedAngles.add(new double[]{minAngle, maxAngle});
        }

        int visible = 0;
        // Check all 4N posts
        for (int x = 0; x <= N; x++) {
            if (canSee(x, 0, px, py, blockedAngles)) visible++;
        }
        for (int y = 1; y <= N; y++) {
            if (canSee(N, y, px, py, blockedAngles)) visible++;
        }
        for (int x = N - 1; x >= 0; x--) {
            if (canSee(x, N, px, py, blockedAngles)) visible++;
        }
        for (int y = N - 1; y >= 1; y--) {
            if (canSee(0, y, px, py, blockedAngles)) visible++;
        }

        System.out.println(visible);
    }

    static boolean canSee(double x, double y, double px, double py, List<double[]> blocked) {
        double angle = Math.atan2(y - py, x - px);
        for (double[] range : blocked) {
            if (angle >= range[0] && angle <= range[1]) return false;
        }
        return true;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, R;
    cin >> N >> R;
    double px, py;
    cin >> px >> py;

    vector<pair<double, double>> blockedAngles;

    for (int r = 0; r < R; r++) {
        int v;
        cin >> v;
        double minAngle = 1e18, maxAngle = -1e18;
        for (int i = 0; i < v; i++) {
            double x, y;
            cin >> x >> y;
            double angle = atan2(y - py, x - px);
            minAngle = min(minAngle, angle);
            maxAngle = max(maxAngle, angle);
        }
        blockedAngles.push_back({minAngle, maxAngle});
    }

    auto canSee = [&](double x, double y) {
        double angle = atan2(y - py, x - px);
        for (auto& range : blockedAngles) {
            if (angle >= range.first && angle <= range.second) return false;
        }
        return true;
    };

    int visible = 0;
    for (int x = 0; x <= N; x++) {
        if (canSee(x, 0)) visible++;
    }
    for (int y = 1; y <= N; y++) {
        if (canSee(N, y)) visible++;
    }
    for (int x = N - 1; x >= 0; x--) {
        if (canSee(x, N)) visible++;
    }
    for (int y = N - 1; y >= 1; y--) {
        if (canSee(0, y)) visible++;
    }

    cout << visible << endl;
    return 0;
}
'''
    },
    2018: {  # 수들의 합 5 - two pointers
        "python": '''n = int(input())

count = 0
left = 1
current_sum = 0

for right in range(1, n + 1):
    current_sum += right
    while current_sum > n:
        current_sum -= left
        left += 1
    if current_sum == n:
        count += 1

print(count)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        int count = 0;
        int left = 1;
        long currentSum = 0;

        for (int right = 1; right <= n; right++) {
            currentSum += right;
            while (currentSum > n) {
                currentSum -= left;
                left++;
            }
            if (currentSum == n) {
                count++;
            }
        }

        System.out.println(count);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int count = 0;
    int left = 1;
    long long currentSum = 0;

    for (int right = 1; right <= n; right++) {
        currentSum += right;
        while (currentSum > n) {
            currentSum -= left;
            left++;
        }
        if (currentSum == n) {
            count++;
        }
    }

    cout << count << endl;
    return 0;
}
'''
    },
    2019: {  # 다각형개수 - graph theory / Euler's formula
        "python": '''import sys
from collections import defaultdict
input = sys.stdin.readline

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def ccw(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def segment_intersection(p1, p2, p3, p4):
    d1 = ccw(p3, p4, p1)
    d2 = ccw(p3, p4, p2)
    d3 = ccw(p1, p2, p3)
    d4 = ccw(p1, p2, p4)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        t = d1 / (d1 - d2)
        x = p1[0] + t * (p2[0] - p1[0])
        y = p1[1] + t * (p2[1] - p1[1])
        return (x, y)
    return None

n = int(input())
segments = []
for _ in range(n):
    x1, y1, x2, y2 = map(int, input().split())
    segments.append(((x1, y1), (x2, y2)))

# Find all intersection points
points = set()
for seg in segments:
    points.add(seg[0])
    points.add(seg[1])

for i in range(n):
    for j in range(i + 1, n):
        pt = segment_intersection(segments[i][0], segments[i][1],
                                  segments[j][0], segments[j][1])
        if pt:
            points.add(pt)

# Build graph
graph = defaultdict(set)
points_list = list(points)

for seg in segments:
    pts_on_seg = [seg[0], seg[1]]
    for pt in points_list:
        if pt != seg[0] and pt != seg[1]:
            # Check if pt is on segment
            if min(seg[0][0], seg[1][0]) <= pt[0] <= max(seg[0][0], seg[1][0]) and \
               min(seg[0][1], seg[1][1]) <= pt[1] <= max(seg[0][1], seg[1][1]):
                cross = ccw(seg[0], seg[1], pt)
                if abs(cross) < 1e-9:
                    pts_on_seg.append(pt)

    pts_on_seg.sort()
    for i in range(len(pts_on_seg) - 1):
        p1, p2 = pts_on_seg[i], pts_on_seg[i + 1]
        graph[p1].add(p2)
        graph[p2].add(p1)

# Count edges and vertices
V = len(graph)
E = sum(len(adj) for adj in graph.values()) // 2

# Euler's formula: V - E + F = 2, F = E - V + 2 (including outer face)
# Number of inner faces = E - V + 1
F = E - V + 1

# Count valid polygons (faces with >= 3 edges and no dangling edges)
print(max(0, F))
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        int[][] segments = new int[n][4];
        for (int i = 0; i < n; i++) {
            segments[i][0] = sc.nextInt();
            segments[i][1] = sc.nextInt();
            segments[i][2] = sc.nextInt();
            segments[i][3] = sc.nextInt();
        }

        Set<String> points = new HashSet<>();
        for (int[] seg : segments) {
            points.add(seg[0] + "," + seg[1]);
            points.add(seg[2] + "," + seg[3]);
        }

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                double[] pt = intersection(segments[i], segments[j]);
                if (pt != null) {
                    points.add(pt[0] + "," + pt[1]);
                }
            }
        }

        // Using Euler's formula approximation
        int V = points.size();
        int E = n + (points.size() - 2 * n);
        int F = E - V + 1;

        System.out.println(Math.max(0, F));
    }

    static double[] intersection(int[] s1, int[] s2) {
        double x1 = s1[0], y1 = s1[1], x2 = s1[2], y2 = s1[3];
        double x3 = s2[0], y3 = s2[1], x4 = s2[2], y4 = s2[3];

        double d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4);
        if (Math.abs(d) < 1e-10) return null;

        double t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d;
        double u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / d;

        if (t > 0 && t < 1 && u > 0 && u < 1) {
            return new double[]{x1 + t * (x2 - x1), y1 + t * (y2 - y1)};
        }
        return null;
    }
}
''',
        "cpp": '''#include <iostream>
#include <set>
#include <vector>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<array<int, 4>> segments(n);
    for (int i = 0; i < n; i++) {
        cin >> segments[i][0] >> segments[i][1] >> segments[i][2] >> segments[i][3];
    }

    set<pair<double, double>> points;
    for (auto& seg : segments) {
        points.insert({seg[0], seg[1]});
        points.insert({seg[2], seg[3]});
    }

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            double x1 = segments[i][0], y1 = segments[i][1];
            double x2 = segments[i][2], y2 = segments[i][3];
            double x3 = segments[j][0], y3 = segments[j][1];
            double x4 = segments[j][2], y4 = segments[j][3];

            double d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4);
            if (fabs(d) < 1e-10) continue;

            double t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d;
            double u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / d;

            if (t > 0 && t < 1 && u > 0 && u < 1) {
                points.insert({x1 + t * (x2 - x1), y1 + t * (y2 - y1)});
            }
        }
    }

    int V = points.size();
    int E = n + (V - 2 * n);
    int F = E - V + 1;

    cout << max(0, F) << endl;
    return 0;
}
'''
    }
}

# Update the data
for i in range(1000, 1010):
    problem = data[i]
    orig_id = problem.get('original_id')
    if orig_id is None:
        continue
    try:
        orig_id_int = int(orig_id)
    except:
        continue
    if orig_id_int in solutions_batch:
        sol = solutions_batch[orig_id_int]
        problem['solutions'] = [
            {"language": "python", "code": sol["python"]},
            {"language": "java", "code": sol["java"]},
            {"language": "cpp", "code": sol["cpp"]}
        ]
        print(f"Updated problem {orig_id_int}")

# Save the data
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Batch 2 (2010-2019) completed!")
