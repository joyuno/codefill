#!/usr/bin/env python3
import json

# Load the data
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r') as f:
    data = json.load(f)

# Solutions for problems 2000-2009

solutions_batch = {
    2000: {  # 책장제작 - DP problem to minimize bookshelf size
        "python": '''import sys
from itertools import permutations

def solve():
    n = int(input())
    books = []
    for _ in range(n):
        h, t = map(int, input().split())
        books.append((h, t))

    min_size = float('inf')

    for mask1 in range(1, (1 << n) - 1):
        for mask2 in range(1, (1 << n)):
            if mask1 & mask2:
                continue
            mask3 = ((1 << n) - 1) ^ mask1 ^ mask2
            if mask3 == 0:
                continue

            s1 = [books[i] for i in range(n) if mask1 & (1 << i)]
            s2 = [books[i] for i in range(n) if mask2 & (1 << i)]
            s3 = [books[i] for i in range(n) if mask3 & (1 << i)]

            h1 = max(b[0] for b in s1)
            h2 = max(b[0] for b in s2)
            h3 = max(b[0] for b in s3)

            t1 = sum(b[1] for b in s1)
            t2 = sum(b[1] for b in s2)
            t3 = sum(b[1] for b in s3)

            size = (h1 + h2 + h3) * max(t1, t2, t3)
            min_size = min(min_size, size)

    print(min_size)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[][] books = new int[n][2];
        for (int i = 0; i < n; i++) {
            books[i][0] = sc.nextInt();
            books[i][1] = sc.nextInt();
        }

        long minSize = Long.MAX_VALUE;

        for (int mask1 = 1; mask1 < (1 << n) - 1; mask1++) {
            for (int mask2 = 1; mask2 < (1 << n); mask2++) {
                if ((mask1 & mask2) != 0) continue;
                int mask3 = ((1 << n) - 1) ^ mask1 ^ mask2;
                if (mask3 == 0) continue;

                int h1 = 0, h2 = 0, h3 = 0;
                int t1 = 0, t2 = 0, t3 = 0;

                for (int i = 0; i < n; i++) {
                    if ((mask1 & (1 << i)) != 0) {
                        h1 = Math.max(h1, books[i][0]);
                        t1 += books[i][1];
                    } else if ((mask2 & (1 << i)) != 0) {
                        h2 = Math.max(h2, books[i][0]);
                        t2 += books[i][1];
                    } else {
                        h3 = Math.max(h3, books[i][0]);
                        t3 += books[i][1];
                    }
                }

                long size = (long)(h1 + h2 + h3) * Math.max(t1, Math.max(t2, t3));
                minSize = Math.min(minSize, size);
            }
        }

        System.out.println(minSize);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    vector<pair<int,int>> books(n);
    for (int i = 0; i < n; i++) {
        cin >> books[i].first >> books[i].second;
    }

    long long minSize = LLONG_MAX;

    for (int mask1 = 1; mask1 < (1 << n) - 1; mask1++) {
        for (int mask2 = 1; mask2 < (1 << n); mask2++) {
            if (mask1 & mask2) continue;
            int mask3 = ((1 << n) - 1) ^ mask1 ^ mask2;
            if (mask3 == 0) continue;

            int h1 = 0, h2 = 0, h3 = 0;
            int t1 = 0, t2 = 0, t3 = 0;

            for (int i = 0; i < n; i++) {
                if (mask1 & (1 << i)) {
                    h1 = max(h1, books[i].first);
                    t1 += books[i].second;
                } else if (mask2 & (1 << i)) {
                    h2 = max(h2, books[i].first);
                    t2 += books[i].second;
                } else {
                    h3 = max(h3, books[i].first);
                    t3 += books[i].second;
                }
            }

            long long size = (long long)(h1 + h2 + h3) * max({t1, t2, t3});
            minSize = min(minSize, size);
        }
    }

    cout << minSize << endl;
    return 0;
}
'''
    },
    2001: {  # 보석 줍기 - BFS with bitmask
        "python": '''import sys
from collections import deque
input = sys.stdin.readline

def main():
    data = input().split()
    n, m, k = int(data[0]), int(data[1]), int(data[2])

    jewel_at = [-1] * (n + 1)
    for i in range(k):
        pos = int(input())
        jewel_at[pos] = i

    graph = [[] for _ in range(n + 1)]
    for _ in range(m):
        line = input().split()
        a, b, w = int(line[0]), int(line[1]), int(line[2])
        graph[a].append((b, w))
        graph[b].append((a, w))

    visited = [[False] * (1 << k) for _ in range(n + 1)]
    q = deque()
    q.append((1, 0))
    visited[1][0] = True

    ans = 0

    while q:
        node, mask = q.popleft()

        if node == 1:
            ans = max(ans, bin(mask).count('1'))

        new_mask = mask
        if jewel_at[node] >= 0:
            new_mask = mask | (1 << jewel_at[node])

        if new_mask != mask and not visited[node][new_mask]:
            visited[node][new_mask] = True
            q.append((node, new_mask))

        cnt = bin(new_mask).count('1')

        for next_node, weight in graph[node]:
            if cnt <= weight and not visited[next_node][new_mask]:
                visited[next_node][new_mask] = True
                q.append((next_node, new_mask))

    print(ans)

main()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int k = sc.nextInt();

        int[] jewelAt = new int[n + 1];
        Arrays.fill(jewelAt, -1);
        for (int i = 0; i < k; i++) {
            int pos = sc.nextInt();
            jewelAt[pos] = i;
        }

        List<int[]>[] graph = new ArrayList[n + 1];
        for (int i = 0; i <= n; i++) graph[i] = new ArrayList<>();

        for (int i = 0; i < m; i++) {
            int a = sc.nextInt(), b = sc.nextInt(), w = sc.nextInt();
            graph[a].add(new int[]{b, w});
            graph[b].add(new int[]{a, w});
        }

        boolean[][] visited = new boolean[n + 1][1 << k];
        Queue<int[]> q = new LinkedList<>();
        q.offer(new int[]{1, 0});
        visited[1][0] = true;

        int ans = 0;

        while (!q.isEmpty()) {
            int[] cur = q.poll();
            int node = cur[0], mask = cur[1];

            if (node == 1) {
                ans = Math.max(ans, Integer.bitCount(mask));
            }

            int newMask = mask;
            if (jewelAt[node] >= 0) {
                newMask = mask | (1 << jewelAt[node]);
            }

            if (newMask != mask && !visited[node][newMask]) {
                visited[node][newMask] = true;
                q.offer(new int[]{node, newMask});
            }

            int cnt = Integer.bitCount(newMask);

            for (int[] edge : graph[node]) {
                int next = edge[0], weight = edge[1];
                if (cnt <= weight && !visited[next][newMask]) {
                    visited[next][newMask] = true;
                    q.offer(new int[]{next, newMask});
                }
            }
        }

        System.out.println(ans);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <queue>
#include <cstring>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, k;
    cin >> n >> m >> k;

    vector<int> jewelAt(n + 1, -1);
    for (int i = 0; i < k; i++) {
        int pos;
        cin >> pos;
        jewelAt[pos] = i;
    }

    vector<vector<pair<int,int>>> graph(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b, w;
        cin >> a >> b >> w;
        graph[a].push_back({b, w});
        graph[b].push_back({a, w});
    }

    vector<vector<bool>> visited(n + 1, vector<bool>(1 << k, false));
    queue<pair<int,int>> q;
    q.push({1, 0});
    visited[1][0] = true;

    int ans = 0;

    while (!q.empty()) {
        auto [node, mask] = q.front();
        q.pop();

        if (node == 1) {
            ans = max(ans, __builtin_popcount(mask));
        }

        int newMask = mask;
        if (jewelAt[node] >= 0) {
            newMask = mask | (1 << jewelAt[node]);
        }

        if (newMask != mask && !visited[node][newMask]) {
            visited[node][newMask] = true;
            q.push({node, newMask});
        }

        int cnt = __builtin_popcount(newMask);

        for (auto& [next, weight] : graph[node]) {
            if (cnt <= weight && !visited[next][newMask]) {
                visited[next][newMask] = true;
                q.push({next, newMask});
            }
        }
    }

    cout << ans << endl;
    return 0;
}
'''
    },
    2002: {  # 추월
        "python": '''n = int(input())
enter = {}
for i in range(n):
    car = input().strip()
    enter[car] = i

exit_order = []
for i in range(n):
    car = input().strip()
    exit_order.append(enter[car])

count = 0
for i in range(n):
    for j in range(i + 1, n):
        if exit_order[i] > exit_order[j]:
            count += 1
            break

print(count)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = Integer.parseInt(sc.nextLine());

        Map<String, Integer> enter = new HashMap<>();
        for (int i = 0; i < n; i++) {
            String car = sc.nextLine();
            enter.put(car, i);
        }

        int[] exitOrder = new int[n];
        for (int i = 0; i < n; i++) {
            String car = sc.nextLine();
            exitOrder[i] = enter.get(car);
        }

        int count = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (exitOrder[i] > exitOrder[j]) {
                    count++;
                    break;
                }
            }
        }

        System.out.println(count);
    }
}
''',
        "cpp": '''#include <iostream>
#include <map>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    map<string, int> enter;
    for (int i = 0; i < n; i++) {
        string car;
        cin >> car;
        enter[car] = i;
    }

    int exitOrder[1001];
    for (int i = 0; i < n; i++) {
        string car;
        cin >> car;
        exitOrder[i] = enter[car];
    }

    int count = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (exitOrder[i] > exitOrder[j]) {
                count++;
                break;
            }
        }
    }

    cout << count << endl;
    return 0;
}
'''
    },
    2003: {  # 수들의 합 2 - Two pointers
        "python": '''n, m = map(int, input().split())
a = list(map(int, input().split()))

count = 0
left = 0
current_sum = 0

for right in range(n):
    current_sum += a[right]

    while current_sum > m and left <= right:
        current_sum -= a[left]
        left += 1

    if current_sum == m:
        count += 1

print(count)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        int count = 0;
        int left = 0;
        long currentSum = 0;

        for (int right = 0; right < n; right++) {
            currentSum += a[right];

            while (currentSum > m && left <= right) {
                currentSum -= a[left];
                left++;
            }

            if (currentSum == m) {
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

    int n, m;
    cin >> n >> m;
    int a[10001];
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    int count = 0;
    int left = 0;
    long long currentSum = 0;

    for (int right = 0; right < n; right++) {
        currentSum += a[right];

        while (currentSum > m && left <= right) {
            currentSum -= a[left];
            left++;
        }

        if (currentSum == m) {
            count++;
        }
    }

    cout << count << endl;
    return 0;
}
'''
    },
    2004: {  # 조합 0의 개수
        "python": '''def count_factor(n, p):
    count = 0
    power = p
    while power <= n:
        count += n // power
        power *= p
    return count

n, m = map(int, input().split())

twos = count_factor(n, 2) - count_factor(m, 2) - count_factor(n - m, 2)
fives = count_factor(n, 5) - count_factor(m, 5) - count_factor(n - m, 5)

print(min(twos, fives))
''',
        "java": '''import java.util.*;

public class Main {
    static long countFactor(long n, long p) {
        long count = 0;
        long power = p;
        while (power <= n) {
            count += n / power;
            power *= p;
        }
        return count;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long n = sc.nextLong();
        long m = sc.nextLong();

        long twos = countFactor(n, 2) - countFactor(m, 2) - countFactor(n - m, 2);
        long fives = countFactor(n, 5) - countFactor(m, 5) - countFactor(n - m, 5);

        System.out.println(Math.min(twos, fives));
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
using namespace std;

long long countFactor(long long n, long long p) {
    long long count = 0;
    long long power = p;
    while (power <= n) {
        count += n / power;
        power *= p;
    }
    return count;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n, m;
    cin >> n >> m;

    long long twos = countFactor(n, 2) - countFactor(m, 2) - countFactor(n - m, 2);
    long long fives = countFactor(n, 5) - countFactor(m, 5) - countFactor(n - m, 5);

    cout << min(twos, fives) << endl;
    return 0;
}
'''
    },
    2005: {  # 사발 - 기하학적 문제
        "python": '''from itertools import permutations

def solve():
    n = int(input())
    bowls = []
    for _ in range(n):
        h, r, R = map(int, input().split())
        bowls.append((h, r, R))

    min_height = float('inf')

    for perm in permutations(range(n)):
        height = bowls[perm[0]][0]
        for i in range(1, n):
            prev_idx = perm[i-1]
            curr_idx = perm[i]
            h_prev, r_prev, R_prev = bowls[prev_idx]
            h_curr, r_curr, R_curr = bowls[curr_idx]

            if r_curr <= r_prev:
                height += h_curr
            elif r_curr >= R_prev:
                height += h_curr
            else:
                x = h_prev * (r_curr - r_prev) / (R_prev - r_prev)
                height += h_curr - x

        min_height = min(min_height, height)

    print(int(min_height))

solve()
''',
        "java": '''import java.util.*;

public class Main {
    static int[][] bowls;
    static int n;
    static double minHeight;
    static boolean[] used;
    static int[] order;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();
        bowls = new int[n][3];
        for (int i = 0; i < n; i++) {
            bowls[i][0] = sc.nextInt();
            bowls[i][1] = sc.nextInt();
            bowls[i][2] = sc.nextInt();
        }

        minHeight = Double.MAX_VALUE;
        used = new boolean[n];
        order = new int[n];

        permute(0);

        System.out.println((int) minHeight);
    }

    static void permute(int depth) {
        if (depth == n) {
            double height = calcHeight();
            minHeight = Math.min(minHeight, height);
            return;
        }

        for (int i = 0; i < n; i++) {
            if (!used[i]) {
                used[i] = true;
                order[depth] = i;
                permute(depth + 1);
                used[i] = false;
            }
        }
    }

    static double calcHeight() {
        double height = bowls[order[0]][0];
        for (int i = 1; i < n; i++) {
            int prev = order[i - 1];
            int curr = order[i];
            double hPrev = bowls[prev][0], rPrev = bowls[prev][1], RPrev = bowls[prev][2];
            double hCurr = bowls[curr][0], rCurr = bowls[curr][1], RCurr = bowls[curr][2];

            if (rCurr <= rPrev) {
                height += hCurr;
            } else if (rCurr >= RPrev) {
                height += hCurr;
            } else {
                double x = hPrev * (rCurr - rPrev) / (RPrev - rPrev);
                height += hCurr - x;
            }
        }
        return height;
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
#include <cmath>
using namespace std;

int n;
vector<tuple<int,int,int>> bowls;

double calcHeight(vector<int>& order) {
    double height = get<0>(bowls[order[0]]);
    for (int i = 1; i < n; i++) {
        int prev = order[i-1], curr = order[i];
        double hPrev = get<0>(bowls[prev]), rPrev = get<1>(bowls[prev]), RPrev = get<2>(bowls[prev]);
        double hCurr = get<0>(bowls[curr]), rCurr = get<1>(bowls[curr]);

        if (rCurr <= rPrev) {
            height += hCurr;
        } else if (rCurr >= RPrev) {
            height += hCurr;
        } else {
            double x = hPrev * (rCurr - rPrev) / (RPrev - rPrev);
            height += hCurr - x;
        }
    }
    return height;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;
    bowls.resize(n);
    for (int i = 0; i < n; i++) {
        int h, r, R;
        cin >> h >> r >> R;
        bowls[i] = {h, r, R};
    }

    vector<int> order(n);
    for (int i = 0; i < n; i++) order[i] = i;

    double minHeight = 1e18;
    do {
        minHeight = min(minHeight, calcHeight(order));
    } while (next_permutation(order.begin(), order.end()));

    cout << (long long)minHeight << endl;
    return 0;
}
'''
    },
    2006: {  # Chemistry 101
        "python": '''import sys
import re
from collections import defaultdict

def parse_side(s):
    elements = defaultdict(int)
    molecules = re.split(r'\\+', s)
    for mol in molecules:
        mol = mol.strip()
        if not mol:
            continue
        match = re.match(r'^(\\d*)', mol)
        coef = int(match.group(1)) if match.group(1) else 1
        mol = mol[len(match.group(0)):]

        i = 0
        while i < len(mol):
            if mol[i].isupper():
                elem = mol[i]
                i += 1
                while i < len(mol) and mol[i].islower():
                    elem += mol[i]
                    i += 1
                count_str = ""
                while i < len(mol) and mol[i].isdigit():
                    count_str += mol[i]
                    i += 1
                count = int(count_str) if count_str else 1
                elements[elem] += coef * count
            else:
                i += 1
    return elements

eq_num = 0
for line in sys.stdin:
    line = line.strip()
    if line == '#':
        break
    eq_num += 1

    line = line.replace(' ', '')

    parts = line.split('=')
    left = parse_side(parts[0])
    right = parse_side(parts[1])

    all_elements = set(left.keys()) | set(right.keys())
    destroyed = {}
    created = {}

    for elem in all_elements:
        diff = right[elem] - left[elem]
        if diff < 0:
            destroyed[elem] = -diff
        elif diff > 0:
            created[elem] = diff

    print(f"Equation {eq_num} is {'balanced' if not destroyed and not created else 'unbalanced'}.")
    for elem in sorted(destroyed.keys()):
        cnt = destroyed[elem]
        print(f"You have destroyed {cnt} atom{'s' if cnt > 1 else ''} of {elem}.")
    for elem in sorted(created.keys()):
        cnt = created[elem]
        print(f"You have created {cnt} atom{'s' if cnt > 1 else ''} of {elem}.")
    print()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int eqNum = 0;

        while (sc.hasNextLine()) {
            String line = sc.nextLine().trim();
            if (line.equals("#")) break;
            eqNum++;

            line = line.replace(" ", "");
            String[] parts = line.split("=");

            Map<String, Integer> left = parseSide(parts[0]);
            Map<String, Integer> right = parseSide(parts[1]);

            Set<String> allElements = new TreeSet<>();
            allElements.addAll(left.keySet());
            allElements.addAll(right.keySet());

            Map<String, Integer> destroyed = new TreeMap<>();
            Map<String, Integer> created = new TreeMap<>();

            for (String elem : allElements) {
                int lc = left.getOrDefault(elem, 0);
                int rc = right.getOrDefault(elem, 0);
                int diff = rc - lc;
                if (diff < 0) destroyed.put(elem, -diff);
                else if (diff > 0) created.put(elem, diff);
            }

            System.out.println("Equation " + eqNum + " is " +
                (destroyed.isEmpty() && created.isEmpty() ? "balanced" : "unbalanced") + ".");

            for (Map.Entry<String, Integer> e : destroyed.entrySet()) {
                int cnt = e.getValue();
                System.out.println("You have destroyed " + cnt + " atom" +
                    (cnt > 1 ? "s" : "") + " of " + e.getKey() + ".");
            }
            for (Map.Entry<String, Integer> e : created.entrySet()) {
                int cnt = e.getValue();
                System.out.println("You have created " + cnt + " atom" +
                    (cnt > 1 ? "s" : "") + " of " + e.getKey() + ".");
            }
            System.out.println();
        }
    }

    static Map<String, Integer> parseSide(String s) {
        Map<String, Integer> elements = new HashMap<>();
        String[] molecules = s.split("\\\\+");

        for (String mol : molecules) {
            mol = mol.trim();
            if (mol.isEmpty()) continue;

            int i = 0;
            int coef = 0;
            while (i < mol.length() && Character.isDigit(mol.charAt(i))) {
                coef = coef * 10 + (mol.charAt(i) - '0');
                i++;
            }
            if (coef == 0) coef = 1;

            while (i < mol.length()) {
                if (Character.isUpperCase(mol.charAt(i))) {
                    StringBuilder elem = new StringBuilder();
                    elem.append(mol.charAt(i++));
                    while (i < mol.length() && Character.isLowerCase(mol.charAt(i))) {
                        elem.append(mol.charAt(i++));
                    }
                    int count = 0;
                    while (i < mol.length() && Character.isDigit(mol.charAt(i))) {
                        count = count * 10 + (mol.charAt(i) - '0');
                        i++;
                    }
                    if (count == 0) count = 1;
                    elements.merge(elem.toString(), coef * count, Integer::sum);
                } else {
                    i++;
                }
            }
        }
        return elements;
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <map>
#include <sstream>
#include <cctype>
#include <algorithm>
using namespace std;

map<string, int> parseSide(const string& s) {
    map<string, int> elements;
    string mol;
    stringstream ss(s);

    while (getline(ss, mol, '+')) {
        while (!mol.empty() && mol[0] == ' ') mol = mol.substr(1);
        while (!mol.empty() && mol.back() == ' ') mol.pop_back();
        if (mol.empty()) continue;

        int i = 0;
        int coef = 0;
        while (i < (int)mol.size() && isdigit(mol[i])) {
            coef = coef * 10 + (mol[i] - '0');
            i++;
        }
        if (coef == 0) coef = 1;

        while (i < (int)mol.size()) {
            if (isupper(mol[i])) {
                string elem;
                elem += mol[i++];
                while (i < (int)mol.size() && islower(mol[i])) {
                    elem += mol[i++];
                }
                int count = 0;
                while (i < (int)mol.size() && isdigit(mol[i])) {
                    count = count * 10 + (mol[i] - '0');
                    i++;
                }
                if (count == 0) count = 1;
                elements[elem] += coef * count;
            } else {
                i++;
            }
        }
    }
    return elements;
}

int main() {
    int eqNum = 0;
    string line;

    while (getline(cin, line)) {
        if (line == "#") break;
        eqNum++;

        line.erase(remove(line.begin(), line.end(), ' '), line.end());
        if (!line.empty() && line.back() == '\\r') line.pop_back();

        size_t eqPos = line.find('=');
        string leftStr = line.substr(0, eqPos);
        string rightStr = line.substr(eqPos + 1);

        auto left = parseSide(leftStr);
        auto right = parseSide(rightStr);

        map<string, int> destroyed, created;

        for (auto& p : left) {
            int diff = right[p.first] - p.second;
            if (diff < 0) destroyed[p.first] = -diff;
        }
        for (auto& p : right) {
            int diff = p.second - left[p.first];
            if (diff > 0) created[p.first] = diff;
        }

        cout << "Equation " << eqNum << " is "
             << (destroyed.empty() && created.empty() ? "balanced" : "unbalanced") << "." << endl;

        for (auto& p : destroyed) {
            cout << "You have destroyed " << p.second << " atom"
                 << (p.second > 1 ? "s" : "") << " of " << p.first << "." << endl;
        }
        for (auto& p : created) {
            cout << "You have created " << p.second << " atom"
                 << (p.second > 1 ? "s" : "") << " of " << p.first << "." << endl;
        }
        cout << endl;
    }
    return 0;
}
'''
    },
    2007: {  # 수들의 합 3
        "python": '''from collections import Counter

def solve():
    n = int(input())
    sums = list(map(int, input().split()))
    sums.sort()

    if n == 2:
        s = sums[0]
        print(0, s)
        return

    for k in range(2, len(sums)):
        total = sums[0] + sums[1] + sums[k]
        if total % 2 != 0:
            continue

        s = total // 2
        a0 = s - sums[k]
        a1 = s - sums[1]
        a2 = s - sums[0]

        if a0 > a1 or a1 > a2:
            continue

        result = [a0, a1, a2]
        remaining = Counter(sums)

        valid = True
        for i in range(3):
            for j in range(i + 1, 3):
                pair_sum = result[i] + result[j]
                if remaining[pair_sum] > 0:
                    remaining[pair_sum] -= 1
                else:
                    valid = False
                    break
            if not valid:
                break

        if not valid:
            continue

        for _ in range(n - 3):
            min_sum = min(s for s, c in remaining.items() if c > 0)
            next_elem = min_sum - result[0]

            if next_elem < result[-1]:
                valid = False
                break

            for existing in result:
                pair_sum = existing + next_elem
                if remaining[pair_sum] > 0:
                    remaining[pair_sum] -= 1
                else:
                    valid = False
                    break

            if not valid:
                break

            result.append(next_elem)

        if valid and all(c == 0 for c in remaining.values()):
            print(' '.join(map(str, result)))
            return

    print("Impossible")

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = n * (n - 1) / 2;
        long[] sums = new long[m];
        for (int i = 0; i < m; i++) {
            sums[i] = sc.nextLong();
        }
        Arrays.sort(sums);

        if (n == 2) {
            System.out.println("0 " + sums[0]);
            return;
        }

        for (int k = 2; k < m; k++) {
            long total = sums[0] + sums[1] + sums[k];
            if (total % 2 != 0) continue;

            long s = total / 2;
            long a0 = s - sums[k];
            long a1 = s - sums[1];
            long a2 = s - sums[0];

            if (a0 > a1 || a1 > a2) continue;

            List<Long> result = new ArrayList<>();
            result.add(a0);
            result.add(a1);
            result.add(a2);

            Map<Long, Integer> remaining = new TreeMap<>();
            for (long sum : sums) {
                remaining.merge(sum, 1, Integer::sum);
            }

            boolean valid = true;
            for (int i = 0; i < 3 && valid; i++) {
                for (int j = i + 1; j < 3 && valid; j++) {
                    long pairSum = result.get(i) + result.get(j);
                    if (remaining.getOrDefault(pairSum, 0) > 0) {
                        remaining.merge(pairSum, -1, Integer::sum);
                    } else {
                        valid = false;
                    }
                }
            }

            if (!valid) continue;

            for (int cnt = 3; cnt < n && valid; cnt++) {
                long minSum = Long.MAX_VALUE;
                for (Map.Entry<Long, Integer> e : remaining.entrySet()) {
                    if (e.getValue() > 0) {
                        minSum = e.getKey();
                        break;
                    }
                }
                if (minSum == Long.MAX_VALUE) {
                    valid = false;
                    break;
                }

                long nextElem = minSum - result.get(0);
                if (nextElem < result.get(result.size() - 1)) {
                    valid = false;
                    break;
                }

                for (Long existing : result) {
                    long pairSum = existing + nextElem;
                    if (remaining.getOrDefault(pairSum, 0) > 0) {
                        remaining.merge(pairSum, -1, Integer::sum);
                    } else {
                        valid = false;
                        break;
                    }
                }

                if (valid) result.add(nextElem);
            }

            if (valid) {
                boolean allZero = true;
                for (int c : remaining.values()) {
                    if (c != 0) {
                        allZero = false;
                        break;
                    }
                }
                if (allZero) {
                    StringBuilder sb = new StringBuilder();
                    for (int i = 0; i < result.size(); i++) {
                        if (i > 0) sb.append(" ");
                        sb.append(result.get(i));
                    }
                    System.out.println(sb);
                    return;
                }
            }
        }

        System.out.println("Impossible");
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
    int m = n * (n - 1) / 2;
    vector<long long> sums(m);
    for (int i = 0; i < m; i++) {
        cin >> sums[i];
    }
    sort(sums.begin(), sums.end());

    if (n == 2) {
        cout << "0 " << sums[0] << endl;
        return 0;
    }

    for (int k = 2; k < m; k++) {
        long long total = sums[0] + sums[1] + sums[k];
        if (total % 2 != 0) continue;

        long long s = total / 2;
        long long a0 = s - sums[k];
        long long a1 = s - sums[1];
        long long a2 = s - sums[0];

        if (a0 > a1 || a1 > a2) continue;

        vector<long long> result = {a0, a1, a2};
        map<long long, int> remaining;
        for (auto& sum : sums) remaining[sum]++;

        bool valid = true;
        for (int i = 0; i < 3 && valid; i++) {
            for (int j = i + 1; j < 3 && valid; j++) {
                long long pairSum = result[i] + result[j];
                if (remaining[pairSum] > 0) {
                    remaining[pairSum]--;
                } else {
                    valid = false;
                }
            }
        }

        if (!valid) continue;

        for (int cnt = 3; cnt < n && valid; cnt++) {
            long long minSum = LLONG_MAX;
            for (auto& p : remaining) {
                if (p.second > 0) {
                    minSum = p.first;
                    break;
                }
            }
            if (minSum == LLONG_MAX) {
                valid = false;
                break;
            }

            long long nextElem = minSum - result[0];
            if (nextElem < result.back()) {
                valid = false;
                break;
            }

            for (auto& existing : result) {
                long long pairSum = existing + nextElem;
                if (remaining[pairSum] > 0) {
                    remaining[pairSum]--;
                } else {
                    valid = false;
                    break;
                }
            }

            if (valid) result.push_back(nextElem);
        }

        if (valid) {
            bool allZero = true;
            for (auto& p : remaining) {
                if (p.second != 0) {
                    allZero = false;
                    break;
                }
            }
            if (allZero) {
                for (int i = 0; i < (int)result.size(); i++) {
                    if (i > 0) cout << " ";
                    cout << result[i];
                }
                cout << endl;
                return 0;
            }
        }
    }

    cout << "Impossible" << endl;
    return 0;
}
'''
    },
    2008: {  # 사다리 게임 - DP
        "python": '''import sys
input = sys.stdin.readline

def solve():
    line = input().split()
    n, m = int(line[0]), int(line[1])
    line = input().split()
    a, b, x, y = int(line[0]), int(line[1]), int(line[2]), int(line[3])

    rungs = []
    for _ in range(m):
        r = int(input())
        rungs.append(r)

    INF = float('inf')
    dp = [[INF] * (n + 1) for _ in range(m + 1)]
    dp[0][a] = 0

    for i in range(m):
        r = rungs[i]
        for j in range(1, n + 1):
            if dp[i][j] == INF:
                continue

            new_pos = j
            if j == r:
                new_pos = r + 1
            elif j == r + 1:
                new_pos = r
            dp[i + 1][new_pos] = min(dp[i + 1][new_pos], dp[i][j])

            dp[i + 1][j] = min(dp[i + 1][j], dp[i][j] + x)

    min_cost = INF
    for j in range(1, n + 1):
        if dp[m][j] == INF:
            continue
        dist = abs(j - b)
        min_cost = min(min_cost, dp[m][j] + dist * y)

    print(min_cost)

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int a = sc.nextInt();
        int b = sc.nextInt();
        int x = sc.nextInt();
        int y = sc.nextInt();

        int[] rungs = new int[m];
        for (int i = 0; i < m; i++) {
            rungs[i] = sc.nextInt();
        }

        int INF = 1000000000;
        int[][] dp = new int[m + 1][n + 1];
        for (int[] row : dp) Arrays.fill(row, INF);
        dp[0][a] = 0;

        for (int i = 0; i < m; i++) {
            int r = rungs[i];
            for (int j = 1; j <= n; j++) {
                if (dp[i][j] == INF) continue;

                int newPos = j;
                if (j == r) newPos = r + 1;
                else if (j == r + 1) newPos = r;
                dp[i + 1][newPos] = Math.min(dp[i + 1][newPos], dp[i][j]);

                dp[i + 1][j] = Math.min(dp[i + 1][j], dp[i][j] + x);
            }
        }

        int minCost = INF;
        for (int j = 1; j <= n; j++) {
            if (dp[m][j] == INF) continue;
            int dist = Math.abs(j - b);
            minCost = Math.min(minCost, dp[m][j] + dist * y);
        }

        System.out.println(minCost);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, a, b, x, y;
    cin >> n >> m >> a >> b >> x >> y;

    vector<int> rungs(m);
    for (int i = 0; i < m; i++) {
        cin >> rungs[i];
    }

    const int INF = 1e9;
    vector<vector<int>> dp(m + 1, vector<int>(n + 1, INF));
    dp[0][a] = 0;

    for (int i = 0; i < m; i++) {
        int r = rungs[i];
        for (int j = 1; j <= n; j++) {
            if (dp[i][j] == INF) continue;

            int newPos = j;
            if (j == r) newPos = r + 1;
            else if (j == r + 1) newPos = r;
            dp[i + 1][newPos] = min(dp[i + 1][newPos], dp[i][j]);

            dp[i + 1][j] = min(dp[i + 1][j], dp[i][j] + x);
        }
    }

    int minCost = INF;
    for (int j = 1; j <= n; j++) {
        if (dp[m][j] == INF) continue;
        int dist = abs(j - b);
        minCost = min(minCost, dp[m][j] + dist * y);
    }

    cout << minCost << endl;
    return 0;
}
'''
    },
    2009: {  # Minecraft - 3D grid projection
        "python": '''import sys
input = sys.stdin.readline

def solve():
    n = int(input())

    H = []
    for _ in range(n):
        H.append(input().strip())

    R = []
    for _ in range(n):
        R.append(input().strip())

    C = []
    for _ in range(n):
        C.append(input().strip())

    M = [[[0]*n for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            for k in range(n):
                if H[j][k] == '1' and R[i][k] == '1' and C[i][j] == '1':
                    M[i][j][k] = 1

    for j in range(n):
        for k in range(n):
            has_block = any(M[i][j][k] for i in range(n))
            if (H[j][k] == '1') != has_block:
                print("NO")
                return

    for i in range(n):
        for k in range(n):
            has_block = any(M[i][j][k] for j in range(n))
            if (R[i][k] == '1') != has_block:
                print("NO")
                return

    for i in range(n):
        for j in range(n):
            has_block = any(M[i][j][k] for k in range(n))
            if (C[i][j] == '1') != has_block:
                print("NO")
                return

    print("YES")
    for i in range(n):
        for j in range(n):
            print(''.join(str(M[i][j][k]) for k in range(n)))

solve()
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        sc.nextLine();

        char[][] H = new char[n][n];
        char[][] R = new char[n][n];
        char[][] C = new char[n][n];

        for (int i = 0; i < n; i++) H[i] = sc.nextLine().toCharArray();
        for (int i = 0; i < n; i++) R[i] = sc.nextLine().toCharArray();
        for (int i = 0; i < n; i++) C[i] = sc.nextLine().toCharArray();

        int[][][] M = new int[n][n][n];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                for (int k = 0; k < n; k++) {
                    if (H[j][k] == '1' && R[i][k] == '1' && C[i][j] == '1') {
                        M[i][j][k] = 1;
                    }
                }
            }
        }

        for (int j = 0; j < n; j++) {
            for (int k = 0; k < n; k++) {
                boolean hasBlock = false;
                for (int i = 0; i < n; i++) if (M[i][j][k] == 1) hasBlock = true;
                if ((H[j][k] == '1') != hasBlock) {
                    System.out.println("NO");
                    return;
                }
            }
        }

        for (int i = 0; i < n; i++) {
            for (int k = 0; k < n; k++) {
                boolean hasBlock = false;
                for (int j = 0; j < n; j++) if (M[i][j][k] == 1) hasBlock = true;
                if ((R[i][k] == '1') != hasBlock) {
                    System.out.println("NO");
                    return;
                }
            }
        }

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                boolean hasBlock = false;
                for (int k = 0; k < n; k++) if (M[i][j][k] == 1) hasBlock = true;
                if ((C[i][j] == '1') != hasBlock) {
                    System.out.println("NO");
                    return;
                }
            }
        }

        System.out.println("YES");
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                StringBuilder sb = new StringBuilder();
                for (int k = 0; k < n; k++) sb.append(M[i][j][k]);
                System.out.println(sb);
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    string H[55], R[55], C[55];
    for (int i = 0; i < n; i++) cin >> H[i];
    for (int i = 0; i < n; i++) cin >> R[i];
    for (int i = 0; i < n; i++) cin >> C[i];

    int M[55][55][55] = {0};

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            for (int k = 0; k < n; k++) {
                if (H[j][k] == '1' && R[i][k] == '1' && C[i][j] == '1') {
                    M[i][j][k] = 1;
                }
            }
        }
    }

    for (int j = 0; j < n; j++) {
        for (int k = 0; k < n; k++) {
            bool hasBlock = false;
            for (int i = 0; i < n; i++) if (M[i][j][k]) hasBlock = true;
            if ((H[j][k] == '1') != hasBlock) {
                cout << "NO" << endl;
                return 0;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        for (int k = 0; k < n; k++) {
            bool hasBlock = false;
            for (int j = 0; j < n; j++) if (M[i][j][k]) hasBlock = true;
            if ((R[i][k] == '1') != hasBlock) {
                cout << "NO" << endl;
                return 0;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            bool hasBlock = false;
            for (int k = 0; k < n; k++) if (M[i][j][k]) hasBlock = true;
            if ((C[i][j] == '1') != hasBlock) {
                cout << "NO" << endl;
                return 0;
            }
        }
    }

    cout << "YES" << endl;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            for (int k = 0; k < n; k++) cout << M[i][j][k];
            cout << endl;
        }
    }
    return 0;
}
'''
    }
}

# Update the data
for i in range(990, 1000):
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

print("Batch 1 (2000-2009) completed!")
