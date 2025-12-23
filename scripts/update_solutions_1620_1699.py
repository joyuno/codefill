#!/usr/bin/env python3
"""
Script to update solutions for problems 1620-1699 in checkpoint JSON file.
"""

import json

def load_checkpoint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_checkpoint(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_solutions_1620_1629():
    """Return solutions for problems 1620-1629"""
    solutions = {}

    # Problem 1620: Pokemon Master (HashMap)
    solutions["1620"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N, M = map(int, input().split())

name_to_num = {}
num_to_name = {}

for i in range(1, N + 1):
    name = input().strip()
    name_to_num[name] = i
    num_to_name[i] = name

result = []
for _ in range(M):
    query = input().strip()
    if query.isdigit():
        result.append(num_to_name[int(query)])
    else:
        result.append(str(name_to_num[query]))

print('\\n'.join(result))"""
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

        Map<String, Integer> nameToNum = new HashMap<>();
        String[] numToName = new String[N + 1];

        for (int i = 1; i <= N; i++) {
            String name = br.readLine().trim();
            nameToNum.put(name, i);
            numToName[i] = name;
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < M; i++) {
            String query = br.readLine().trim();
            if (Character.isDigit(query.charAt(0))) {
                sb.append(numToName[Integer.parseInt(query)]).append("\\n");
            } else {
                sb.append(nameToNum.get(query)).append("\\n");
            }
        }
        System.out.print(sb);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <map>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    map<string, int> nameToNum;
    string numToName[100001];

    for (int i = 1; i <= N; i++) {
        string name;
        cin >> name;
        nameToNum[name] = i;
        numToName[i] = name;
    }

    for (int i = 0; i < M; i++) {
        string query;
        cin >> query;
        if (isdigit(query[0])) {
            cout << numToName[stoi(query)] << "\\n";
        } else {
            cout << nameToNum[query] << "\\n";
        }
    }

    return 0;
}"""
        }
    ]

    # Problem 1621: Josam Mosa (DP with trace)
    solutions["1621"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N = int(input())
K, C = map(int, input().split())
weights = list(map(int, input().split()))

# dp[i] = (min_time, min_k_uses, last_used_k_positions)
# Simplified: dp[i] = minimum time to carry bananas 0..i-1

INF = float('inf')
dp = [INF] * (N + 1)
parent = [-1] * (N + 1)  # -1: single, else: start of K group
dp[0] = 0

for i in range(N):
    # Option 1: carry banana i individually
    if dp[i] + weights[i] < dp[i + 1]:
        dp[i + 1] = dp[i] + weights[i]
        parent[i + 1] = -1

    # Option 2: carry K bananas starting at i
    if i + K <= N:
        if dp[i] + C < dp[i + K]:
            dp[i + K] = dp[i] + C
            parent[i + K] = i  # Mark as group starting at i

# Backtrack to find K-group positions
k_positions = []
pos = N
while pos > 0:
    if parent[pos] >= 0:
        k_positions.append(parent[pos] + 1)  # 1-indexed
        pos = parent[pos]
    else:
        pos -= 1

k_positions.sort()

print(dp[N])
print(len(k_positions))
if k_positions:
    print(' '.join(map(str, k_positions)))
else:
    print()"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        int K = Integer.parseInt(st.nextToken());
        int C = Integer.parseInt(st.nextToken());

        int[] weights = new int[N];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            weights[i] = Integer.parseInt(st.nextToken());
        }

        long[] dp = new long[N + 1];
        int[] parent = new int[N + 1];
        Arrays.fill(dp, Long.MAX_VALUE);
        Arrays.fill(parent, -1);
        dp[0] = 0;

        for (int i = 0; i < N; i++) {
            if (dp[i] + weights[i] < dp[i + 1]) {
                dp[i + 1] = dp[i] + weights[i];
                parent[i + 1] = -1;
            }

            if (i + K <= N && dp[i] + C < dp[i + K]) {
                dp[i + K] = dp[i] + C;
                parent[i + K] = i;
            }
        }

        List<Integer> kPositions = new ArrayList<>();
        int pos = N;
        while (pos > 0) {
            if (parent[pos] >= 0) {
                kPositions.add(parent[pos] + 1);
                pos = parent[pos];
            } else {
                pos--;
            }
        }

        Collections.sort(kPositions);

        StringBuilder sb = new StringBuilder();
        sb.append(dp[N]).append("\\n");
        sb.append(kPositions.size()).append("\\n");
        for (int i = 0; i < kPositions.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(kPositions.get(i));
        }
        System.out.println(sb);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;
    int K, C;
    cin >> K >> C;

    vector<int> weights(N);
    for (int i = 0; i < N; i++) {
        cin >> weights[i];
    }

    vector<long long> dp(N + 1, LLONG_MAX);
    vector<int> parent(N + 1, -1);
    dp[0] = 0;

    for (int i = 0; i < N; i++) {
        if (dp[i] + weights[i] < dp[i + 1]) {
            dp[i + 1] = dp[i] + weights[i];
            parent[i + 1] = -1;
        }

        if (i + K <= N && dp[i] + C < dp[i + K]) {
            dp[i + K] = dp[i] + C;
            parent[i + K] = i;
        }
    }

    vector<int> kPositions;
    int pos = N;
    while (pos > 0) {
        if (parent[pos] >= 0) {
            kPositions.push_back(parent[pos] + 1);
            pos = parent[pos];
        } else {
            pos--;
        }
    }

    sort(kPositions.begin(), kPositions.end());

    cout << dp[N] << "\\n";
    cout << kPositions.size() << "\\n";
    for (int i = 0; i < kPositions.size(); i++) {
        if (i > 0) cout << " ";
        cout << kPositions[i];
    }
    cout << endl;

    return 0;
}"""
        }
    ]

    # Problem 1622: Common Permutation
    solutions["1622"] = [
        {
            "language": "python",
            "code": """import sys

try:
    while True:
        a = input().strip()
        b = input().strip()

        # Count characters in both strings
        count_a = [0] * 26
        count_b = [0] * 26

        for c in a:
            count_a[ord(c) - ord('a')] += 1
        for c in b:
            count_b[ord(c) - ord('a')] += 1

        # Take minimum of each character
        result = []
        for i in range(26):
            result.append(chr(ord('a') + i) * min(count_a[i], count_b[i]))

        print(''.join(result))
except EOFError:
    pass"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        while (sc.hasNextLine()) {
            String a = sc.nextLine().trim();
            if (!sc.hasNextLine()) break;
            String b = sc.nextLine().trim();

            int[] countA = new int[26];
            int[] countB = new int[26];

            for (char c : a.toCharArray()) {
                countA[c - 'a']++;
            }
            for (char c : b.toCharArray()) {
                countB[c - 'a']++;
            }

            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 26; i++) {
                int cnt = Math.min(countA[i], countB[i]);
                for (int j = 0; j < cnt; j++) {
                    sb.append((char)('a' + i));
                }
            }
            System.out.println(sb);
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

    string a, b;
    while (getline(cin, a) && getline(cin, b)) {
        int countA[26] = {0};
        int countB[26] = {0};

        for (char c : a) {
            countA[c - 'a']++;
        }
        for (char c : b) {
            countB[c - 'a']++;
        }

        string result = "";
        for (int i = 0; i < 26; i++) {
            int cnt = min(countA[i], countB[i]);
            for (int j = 0; j < cnt; j++) {
                result += ('a' + i);
            }
        }
        cout << result << "\\n";
    }

    return 0;
}"""
        }
    ]

    # Problem 1623: Party Planning (Tree DP with traceback)
    solutions["1623"] = [
        {
            "language": "python",
            "code": """import sys
from collections import defaultdict
sys.setrecursionlimit(300000)
input = sys.stdin.readline

N = int(input())
values = [0] + list(map(int, input().split()))
parents = [0, 0] + list(map(int, input().split()))

children = defaultdict(list)
for i in range(2, N + 1):
    children[parents[i]].append(i)

# dp[v][0] = max value when v is not selected
# dp[v][1] = max value when v is selected
dp = [[0, 0] for _ in range(N + 1)]
choice = [[[], []] for _ in range(N + 1)]

def dfs(v):
    dp[v][1] = values[v]

    for c in children[v]:
        dfs(c)
        dp[v][0] += max(dp[c][0], dp[c][1])
        dp[v][1] += dp[c][0]

dfs(1)

# Traceback
def trace(v, selected):
    result = []
    if selected:
        result.append(v)
        for c in children[v]:
            result.extend(trace(c, False))
    else:
        for c in children[v]:
            if dp[c][1] > dp[c][0]:
                result.extend(trace(c, True))
            else:
                result.extend(trace(c, False))
    return result

# Case 1: Boss attends
result1 = trace(1, True)
result1.sort()

# Case 2: Boss doesn't attend
result2 = trace(1, False)
result2.sort()

print(dp[1][1], dp[1][0])
print(' '.join(map(str, result1)), -1)
print(' '.join(map(str, result2)), -1)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static List<List<Integer>> children;
    static int[] values;
    static long[][] dp;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        values = new int[N + 1];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 1; i <= N; i++) {
            values[i] = Integer.parseInt(st.nextToken());
        }

        children = new ArrayList<>();
        for (int i = 0; i <= N; i++) {
            children.add(new ArrayList<>());
        }

        if (N > 1) {
            st = new StringTokenizer(br.readLine());
            for (int i = 2; i <= N; i++) {
                int parent = Integer.parseInt(st.nextToken());
                children.get(parent).add(i);
            }
        }

        dp = new long[N + 1][2];
        dfs(1);

        List<Integer> result1 = new ArrayList<>();
        List<Integer> result2 = new ArrayList<>();
        trace(1, true, result1);
        trace(1, false, result2);

        Collections.sort(result1);
        Collections.sort(result2);

        StringBuilder sb = new StringBuilder();
        sb.append(dp[1][1]).append(" ").append(dp[1][0]).append("\\n");

        for (int x : result1) sb.append(x).append(" ");
        sb.append("-1\\n");

        for (int x : result2) sb.append(x).append(" ");
        sb.append("-1");

        System.out.println(sb);
    }

    static void dfs(int v) {
        dp[v][1] = values[v];
        dp[v][0] = 0;

        for (int c : children.get(v)) {
            dfs(c);
            dp[v][0] += Math.max(dp[c][0], dp[c][1]);
            dp[v][1] += dp[c][0];
        }
    }

    static void trace(int v, boolean selected, List<Integer> result) {
        if (selected) {
            result.add(v);
            for (int c : children.get(v)) {
                trace(c, false, result);
            }
        } else {
            for (int c : children.get(v)) {
                if (dp[c][1] > dp[c][0]) {
                    trace(c, true, result);
                } else {
                    trace(c, false, result);
                }
            }
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

vector<vector<int>> children;
vector<int> values;
vector<vector<long long>> dp;

void dfs(int v) {
    dp[v][1] = values[v];
    dp[v][0] = 0;

    for (int c : children[v]) {
        dfs(c);
        dp[v][0] += max(dp[c][0], dp[c][1]);
        dp[v][1] += dp[c][0];
    }
}

void trace(int v, bool selected, vector<int>& result) {
    if (selected) {
        result.push_back(v);
        for (int c : children[v]) {
            trace(c, false, result);
        }
    } else {
        for (int c : children[v]) {
            if (dp[c][1] > dp[c][0]) {
                trace(c, true, result);
            } else {
                trace(c, false, result);
            }
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    values.resize(N + 1);
    for (int i = 1; i <= N; i++) {
        cin >> values[i];
    }

    children.resize(N + 1);
    for (int i = 2; i <= N; i++) {
        int parent;
        cin >> parent;
        children[parent].push_back(i);
    }

    dp.resize(N + 1, vector<long long>(2, 0));
    dfs(1);

    vector<int> result1, result2;
    trace(1, true, result1);
    trace(1, false, result2);

    sort(result1.begin(), result1.end());
    sort(result2.begin(), result2.end());

    cout << dp[1][1] << " " << dp[1][0] << "\\n";

    for (int x : result1) cout << x << " ";
    cout << "-1\\n";

    for (int x : result2) cout << x << " ";
    cout << "-1" << endl;

    return 0;
}"""
        }
    ]

    # Problem 1624: Data File (Binary search / Prefix sum)
    solutions["1624"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

N, M = map(int, input().split())
files = []
for _ in range(N):
    files.append(int(input()))

# Sort files by size
files.sort()

# Prefix sum
prefix = [0] * (N + 1)
for i in range(N):
    prefix[i + 1] = prefix[i] + files[i]

result = []
for _ in range(M):
    capacity = int(input())

    # Binary search for largest index where prefix[i] <= capacity
    left, right = 0, N
    while left < right:
        mid = (left + right + 1) // 2
        if prefix[mid] <= capacity:
            left = mid
        else:
            right = mid - 1

    result.append(left)

print('\\n'.join(map(str, result)))"""
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

        int[] files = new int[N];
        for (int i = 0; i < N; i++) {
            files[i] = Integer.parseInt(br.readLine().trim());
        }

        Arrays.sort(files);

        long[] prefix = new long[N + 1];
        for (int i = 0; i < N; i++) {
            prefix[i + 1] = prefix[i] + files[i];
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < M; i++) {
            long capacity = Long.parseLong(br.readLine().trim());

            int left = 0, right = N;
            while (left < right) {
                int mid = (left + right + 1) / 2;
                if (prefix[mid] <= capacity) {
                    left = mid;
                } else {
                    right = mid - 1;
                }
            }
            sb.append(left).append("\\n");
        }
        System.out.print(sb);
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

    int N, M;
    cin >> N >> M;

    vector<int> files(N);
    for (int i = 0; i < N; i++) {
        cin >> files[i];
    }

    sort(files.begin(), files.end());

    vector<long long> prefix(N + 1, 0);
    for (int i = 0; i < N; i++) {
        prefix[i + 1] = prefix[i] + files[i];
    }

    for (int i = 0; i < M; i++) {
        long long capacity;
        cin >> capacity;

        int left = 0, right = N;
        while (left < right) {
            int mid = (left + right + 1) / 2;
            if (prefix[mid] <= capacity) {
                left = mid;
            } else {
                right = mid - 1;
            }
        }
        cout << left << "\\n";
    }

    return 0;
}"""
        }
    ]

    # Problem 1625: Typing (DP on 2D matrix)
    solutions["1625"] = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

S = input().strip()
T = input().strip()

n, m = len(S), len(T)

# dp[i][j] = min cost to match S[:i] with T[:j]
INF = float('inf')
dp = [[INF] * (m + 1) for _ in range(n + 1)]

# Costs
ADD_COST = 1  # Insert character into S
DEL_COST = 1  # Delete character from S
CHANGE_COST = 1  # Change character in S

dp[0][0] = 0

# Initialize: deleting all from S
for i in range(1, n + 1):
    dp[i][0] = dp[i-1][0] + DEL_COST

# Initialize: adding all to empty S
for j in range(1, m + 1):
    dp[0][j] = dp[0][j-1] + ADD_COST

for i in range(1, n + 1):
    for j in range(1, m + 1):
        # Delete S[i-1]
        dp[i][j] = min(dp[i][j], dp[i-1][j] + DEL_COST)

        # Insert T[j-1] into S
        dp[i][j] = min(dp[i][j], dp[i][j-1] + ADD_COST)

        # Match or change
        if S[i-1] == T[j-1]:
            dp[i][j] = min(dp[i][j], dp[i-1][j-1])
        else:
            dp[i][j] = min(dp[i][j], dp[i-1][j-1] + CHANGE_COST)

print(dp[n][m])"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String S = sc.nextLine().trim();
        String T = sc.nextLine().trim();

        int n = S.length(), m = T.length();
        int[][] dp = new int[n + 1][m + 1];

        for (int i = 0; i <= n; i++) dp[i][0] = i;
        for (int j = 0; j <= m; j++) dp[0][j] = j;

        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= m; j++) {
                dp[i][j] = dp[i-1][j] + 1;  // Delete
                dp[i][j] = Math.min(dp[i][j], dp[i][j-1] + 1);  // Insert

                if (S.charAt(i-1) == T.charAt(j-1)) {
                    dp[i][j] = Math.min(dp[i][j], dp[i-1][j-1]);
                } else {
                    dp[i][j] = Math.min(dp[i][j], dp[i-1][j-1] + 1);
                }
            }
        }

        System.out.println(dp[n][m]);
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string S, T;
    cin >> S >> T;

    int n = S.length(), m = T.length();
    vector<vector<int>> dp(n + 1, vector<int>(m + 1, 0));

    for (int i = 0; i <= n; i++) dp[i][0] = i;
    for (int j = 0; j <= m; j++) dp[0][j] = j;

    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= m; j++) {
            dp[i][j] = dp[i-1][j] + 1;
            dp[i][j] = min(dp[i][j], dp[i][j-1] + 1);

            if (S[i-1] == T[j-1]) {
                dp[i][j] = min(dp[i][j], dp[i-1][j-1]);
            } else {
                dp[i][j] = min(dp[i][j], dp[i-1][j-1] + 1);
            }
        }
    }

    cout << dp[n][m] << endl;

    return 0;
}"""
        }
    ]

    # Problem 1626: Two Circles
    solutions["1626"] = [
        {
            "language": "python",
            "code": """import sys
import math
input = sys.stdin.readline

x1, y1, r1 = map(int, input().split())
x2, y2, r2 = map(int, input().split())

d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Check if circles intersect
if d > r1 + r2:  # Too far apart
    print(-1)
elif d < abs(r1 - r2):  # One inside the other
    print(-1)
elif d == 0 and r1 == r2:  # Same circle
    print(-1)
else:
    # Common external tangent length
    # L = sqrt(d^2 - (r1 - r2)^2) for external tangent
    # L = sqrt(d^2 - (r1 + r2)^2) for internal tangent

    if d >= r1 + r2:
        # External tangent
        ext = math.sqrt(d * d - (r1 - r2) ** 2) if d >= abs(r1 - r2) else 0
        # Internal tangent
        int_tan = math.sqrt(d * d - (r1 + r2) ** 2) if d >= r1 + r2 else 0
        print(f"{ext:.5f}")
    elif d >= abs(r1 - r2):
        # Only external tangent
        ext = math.sqrt(d * d - (r1 - r2) ** 2)
        print(f"{ext:.5f}")
    else:
        print(-1)"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        double x1 = sc.nextDouble(), y1 = sc.nextDouble(), r1 = sc.nextDouble();
        double x2 = sc.nextDouble(), y2 = sc.nextDouble(), r2 = sc.nextDouble();

        double d = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));

        if (d > r1 + r2 || d < Math.abs(r1 - r2)) {
            System.out.println(-1);
        } else if (d == 0 && r1 == r2) {
            System.out.println(-1);
        } else {
            double ext = Math.sqrt(d * d - Math.pow(r1 - r2, 2));
            System.out.printf("%.5f%n", ext);
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <cmath>
#include <iomanip>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    double x1, y1, r1, x2, y2, r2;
    cin >> x1 >> y1 >> r1 >> x2 >> y2 >> r2;

    double d = sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2));

    if (d > r1 + r2 || d < abs(r1 - r2)) {
        cout << -1 << endl;
    } else if (d == 0 && r1 == r2) {
        cout << -1 << endl;
    } else {
        double ext = sqrt(d * d - pow(r1 - r2, 2));
        cout << fixed << setprecision(5) << ext << endl;
    }

    return 0;
}"""
        }
    ]

    # Problem 1627: Quadratic Equation
    solutions["1627"] = [
        {
            "language": "python",
            "code": """import math

a, b, c = map(int, input().split())

# ax^2 + bx + c = 0
# x = (-b +/- sqrt(b^2 - 4ac)) / 2a

discriminant = b * b - 4 * a * c

if discriminant < 0:
    print("NO")
else:
    sqrt_d = math.sqrt(discriminant)
    x1 = (-b + sqrt_d) / (2 * a)
    x2 = (-b - sqrt_d) / (2 * a)

    if x1 > x2:
        x1, x2 = x2, x1

    if discriminant == 0:
        print(f"{x1:.6f}")
    else:
        print(f"{x1:.6f}")
        print(f"{x2:.6f}")"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        double a = sc.nextDouble();
        double b = sc.nextDouble();
        double c = sc.nextDouble();

        double discriminant = b * b - 4 * a * c;

        if (discriminant < 0) {
            System.out.println("NO");
        } else {
            double sqrtD = Math.sqrt(discriminant);
            double x1 = (-b + sqrtD) / (2 * a);
            double x2 = (-b - sqrtD) / (2 * a);

            if (x1 > x2) {
                double temp = x1;
                x1 = x2;
                x2 = temp;
            }

            if (discriminant == 0) {
                System.out.printf("%.6f%n", x1);
            } else {
                System.out.printf("%.6f%n", x1);
                System.out.printf("%.6f%n", x2);
            }
        }
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <cmath>
#include <iomanip>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    double a, b, c;
    cin >> a >> b >> c;

    double discriminant = b * b - 4 * a * c;

    if (discriminant < 0) {
        cout << "NO" << endl;
    } else {
        double sqrtD = sqrt(discriminant);
        double x1 = (-b + sqrtD) / (2 * a);
        double x2 = (-b - sqrtD) / (2 * a);

        if (x1 > x2) swap(x1, x2);

        cout << fixed << setprecision(6);
        if (discriminant == 0) {
            cout << x1 << endl;
        } else {
            cout << x1 << endl;
            cout << x2 << endl;
        }
    }

    return 0;
}"""
        }
    ]

    # Problem 1628: Subset sum (Meet in the Middle)
    solutions["1628"] = [
        {
            "language": "python",
            "code": """import sys
from collections import defaultdict
input = sys.stdin.readline

N, S = map(int, input().split())
arr = list(map(int, input().split()))

# Meet in the middle
half = N // 2
left = arr[:half]
right = arr[half:]

def get_sums(lst):
    sums = defaultdict(int)
    n = len(lst)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += lst[i]
        sums[s] += 1
    return sums

left_sums = get_sums(left)
right_sums = get_sums(right)

count = 0

# Count pairs where left_sum + right_sum = S
for ls, lc in left_sums.items():
    if S - ls in right_sums:
        count += lc * right_sums[S - ls]

# Add single subsets from left that equal S
if S in left_sums:
    count += left_sums[S]

# Add single subsets from right that equal S (already counted above)
# Actually we need to handle empty subset case

# Subtract empty subset case if S == 0
# The above counts include empty+empty = 0

print(count)"""
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
        long S = Long.parseLong(st.nextToken());

        long[] arr = new long[N];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            arr[i] = Long.parseLong(st.nextToken());
        }

        int half = N / 2;
        long[] left = new long[half];
        long[] right = new long[N - half];

        for (int i = 0; i < half; i++) left[i] = arr[i];
        for (int i = half; i < N; i++) right[i - half] = arr[i];

        Map<Long, Long> leftSums = getSums(left);
        Map<Long, Long> rightSums = getSums(right);

        long count = 0;

        for (Map.Entry<Long, Long> entry : leftSums.entrySet()) {
            long ls = entry.getKey();
            long lc = entry.getValue();
            if (rightSums.containsKey(S - ls)) {
                count += lc * rightSums.get(S - ls);
            }
        }

        if (leftSums.containsKey(S)) {
            count += leftSums.get(S);
        }

        System.out.println(count);
    }

    static Map<Long, Long> getSums(long[] lst) {
        Map<Long, Long> sums = new HashMap<>();
        int n = lst.length;
        for (int mask = 0; mask < (1 << n); mask++) {
            long s = 0;
            for (int i = 0; i < n; i++) {
                if ((mask & (1 << i)) != 0) {
                    s += lst[i];
                }
            }
            sums.put(s, sums.getOrDefault(s, 0L) + 1);
        }
        return sums;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <map>
using namespace std;

map<long long, long long> getSums(vector<long long>& lst) {
    map<long long, long long> sums;
    int n = lst.size();
    for (int mask = 0; mask < (1 << n); mask++) {
        long long s = 0;
        for (int i = 0; i < n; i++) {
            if (mask & (1 << i)) {
                s += lst[i];
            }
        }
        sums[s]++;
    }
    return sums;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    long long S;
    cin >> N >> S;

    vector<long long> arr(N);
    for (int i = 0; i < N; i++) {
        cin >> arr[i];
    }

    int half = N / 2;
    vector<long long> left(arr.begin(), arr.begin() + half);
    vector<long long> right(arr.begin() + half, arr.end());

    auto leftSums = getSums(left);
    auto rightSums = getSums(right);

    long long count = 0;

    for (auto& [ls, lc] : leftSums) {
        if (rightSums.count(S - ls)) {
            count += lc * rightSums[S - ls];
        }
    }

    if (leftSums.count(S)) {
        count += leftSums[S];
    }

    cout << count << endl;

    return 0;
}"""
        }
    ]

    # Problem 1629: Modular Exponentiation
    solutions["1629"] = [
        {
            "language": "python",
            "code": """A, B, C = map(int, input().split())

def power(a, b, c):
    if b == 0:
        return 1
    if b == 1:
        return a % c

    half = power(a, b // 2, c)
    result = (half * half) % c

    if b % 2 == 1:
        result = (result * a) % c

    return result

print(power(A, B, C))"""
        },
        {
            "language": "java",
            "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long A = sc.nextLong();
        long B = sc.nextLong();
        long C = sc.nextLong();

        System.out.println(power(A, B, C));
    }

    static long power(long a, long b, long c) {
        if (b == 0) return 1;
        if (b == 1) return a % c;

        long half = power(a, b / 2, c);
        long result = (half * half) % c;

        if (b % 2 == 1) {
            result = (result * a) % c;
        }

        return result;
    }
}"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
using namespace std;

long long power(long long a, long long b, long long c) {
    if (b == 0) return 1;
    if (b == 1) return a % c;

    long long half = power(a, b / 2, c);
    long long result = (half * half) % c;

    if (b % 2 == 1) {
        result = (result * a) % c;
    }

    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long A, B, C;
    cin >> A >> B >> C;

    cout << power(A, B, C) << endl;

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
    solutions = get_solutions_1620_1629()

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
