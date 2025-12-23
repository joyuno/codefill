import json

with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r') as f:
    data = json.load(f)

id_to_idx = {}
for idx, p in enumerate(data):
    if 'original_id' in p:
        id_to_idx[p['original_id']] = idx

solutions = {}

# Problem 1960: Matrix Reconstruction from Row/Col Sums (Greedy)
solutions['1960'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

n = int(input())
rows = list(map(int, input().split()))
cols = list(map(int, input().split()))

# Check if sum matches
if sum(rows) != sum(cols):
    print(-1)
else:
    # Greedy: assign 1s from left to right
    matrix = [[0] * n for _ in range(n)]

    # Create list of (count, index) for rows and cols
    row_list = [[rows[i], i] for i in range(n)]
    col_list = [[cols[j], j] for j in range(n)]

    for _ in range(sum(rows)):
        # Sort by remaining count (descending)
        row_list.sort(key=lambda x: -x[0])
        col_list.sort(key=lambda x: -x[0])

        # Find row and col with most remaining
        ri = row_list[0][1]
        ci = col_list[0][1]

        matrix[ri][ci] = 1
        row_list[0][0] -= 1
        col_list[0][0] -= 1

    # Verify
    valid = True
    for i in range(n):
        if sum(matrix[i]) != rows[i]:
            valid = False
            break
    for j in range(n):
        if sum(matrix[i][j] for i in range(n)) != cols[j]:
            valid = False
            break

    if valid:
        print(1)
        for row in matrix:
            print(''.join(map(str, row)))
    else:
        print(-1)
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
        int[] rows = new int[n];
        int rowSum = 0;
        for (int i = 0; i < n; i++) {
            rows[i] = Integer.parseInt(st.nextToken());
            rowSum += rows[i];
        }

        st = new StringTokenizer(br.readLine());
        int[] cols = new int[n];
        int colSum = 0;
        for (int j = 0; j < n; j++) {
            cols[j] = Integer.parseInt(st.nextToken());
            colSum += cols[j];
        }

        if (rowSum != colSum) {
            System.out.println(-1);
            return;
        }

        int[][] matrix = new int[n][n];
        int[][] rowList = new int[n][2];
        int[][] colList = new int[n][2];

        for (int i = 0; i < n; i++) {
            rowList[i][0] = rows[i];
            rowList[i][1] = i;
            colList[i][0] = cols[i];
            colList[i][1] = i;
        }

        for (int k = 0; k < rowSum; k++) {
            Arrays.sort(rowList, (a, b) -> b[0] - a[0]);
            Arrays.sort(colList, (a, b) -> b[0] - a[0]);

            int ri = rowList[0][1];
            int ci = colList[0][1];

            matrix[ri][ci] = 1;
            rowList[0][0]--;
            colList[0][0]--;
        }

        System.out.println(1);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                sb.append(matrix[i][j]);
            }
            sb.append("\\n");
        }
        System.out.print(sb);
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <algorithm>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> rows(n), cols(n);
    int rowSum = 0, colSum = 0;

    for (int i = 0; i < n; i++) {
        cin >> rows[i];
        rowSum += rows[i];
    }
    for (int j = 0; j < n; j++) {
        cin >> cols[j];
        colSum += cols[j];
    }

    if (rowSum != colSum) {
        cout << -1 << endl;
        return 0;
    }

    vector<vector<int>> matrix(n, vector<int>(n, 0));
    vector<pair<int, int>> rowList(n), colList(n);

    for (int i = 0; i < n; i++) {
        rowList[i] = {rows[i], i};
        colList[i] = {cols[i], i};
    }

    for (int k = 0; k < rowSum; k++) {
        sort(rowList.begin(), rowList.end(), greater<pair<int,int>>());
        sort(colList.begin(), colList.end(), greater<pair<int,int>>());

        int ri = rowList[0].second;
        int ci = colList[0].second;

        matrix[ri][ci] = 1;
        rowList[0].first--;
        colList[0].first--;
    }

    cout << 1 << endl;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cout << matrix[i][j];
        }
        cout << "\\n";
    }

    return 0;
}
"""
    }
]

# Problem 1970: Toasting (DP on circle with brackets)
solutions['1970'] = [
    {
        "language": "python",
        "code": """import sys
from collections import defaultdict
sys.setrecursionlimit(10000)
input = sys.stdin.readline

n = int(input())
brands = list(map(int, input().split()))

# DP on circular array - find max non-crossing pairs with same brand
# dp[i][j] = max pairs in range [i, j]

memo = {}

def dp(i, j):
    if i >= j:
        return 0
    if (i, j) in memo:
        return memo[(i, j)]

    # Option 1: don't pair person i
    res = dp(i + 1, j)

    # Option 2: pair person i with some person k where brands match and we can split
    for k in range(i + 1, j + 1):
        if brands[i] == brands[k]:
            # Pair (i, k), then solve (i+1, k-1) and (k+1, j)
            res = max(res, 1 + dp(i + 1, k - 1) + dp(k + 1, j))

    memo[(i, j)] = res
    return res

print(dp(0, n - 1))
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    static int[] brands;
    static int[][] dp;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        brands = new int[n];
        for (int i = 0; i < n; i++) {
            brands[i] = Integer.parseInt(st.nextToken());
        }

        dp = new int[n][n];
        for (int[] row : dp) Arrays.fill(row, -1);

        System.out.println(solve(0, n - 1));
    }

    static int solve(int i, int j) {
        if (i >= j) return 0;
        if (dp[i][j] != -1) return dp[i][j];

        int res = solve(i + 1, j);

        for (int k = i + 1; k <= j; k++) {
            if (brands[i] == brands[k]) {
                res = Math.max(res, 1 + solve(i + 1, k - 1) + solve(k + 1, j));
            }
        }

        return dp[i][j] = res;
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <cstring>
using namespace std;

int n;
int brands[1001];
int dp[1001][1001];

int solve(int i, int j) {
    if (i >= j) return 0;
    if (dp[i][j] != -1) return dp[i][j];

    int res = solve(i + 1, j);

    for (int k = i + 1; k <= j; k++) {
        if (brands[i] == brands[k]) {
            res = max(res, 1 + solve(i + 1, k - 1) + solve(k + 1, j));
        }
    }

    return dp[i][j] = res;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;
    for (int i = 0; i < n; i++) {
        cin >> brands[i];
    }

    memset(dp, -1, sizeof(dp));
    cout << solve(0, n - 1) << endl;

    return 0;
}
"""
    }
]

# Problem 1974: Jump Championship (LIS variant)
solutions['1974'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n = int(input())
    trophies = list(map(int, input().split()))

    # Find longest increasing subsequence and track path
    # dp[i] = (length, path) of LIS ending at i

    dp = [(1, [i]) for i in range(n)]

    for i in range(1, n):
        for j in range(i):
            if trophies[j] < trophies[i]:
                if dp[j][0] + 1 > dp[i][0]:
                    dp[i] = (dp[j][0] + 1, dp[j][1] + [i])

    best = max(dp, key=lambda x: x[0])
    print(best[0])
    print(' '.join(str(i + 1) for i in best[1]))
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());
        while (t-- > 0) {
            int n = Integer.parseInt(br.readLine().trim());
            StringTokenizer st = new StringTokenizer(br.readLine());
            int[] trophies = new int[n];
            for (int i = 0; i < n; i++) {
                trophies[i] = Integer.parseInt(st.nextToken());
            }

            int[] dp = new int[n];
            int[] parent = new int[n];
            Arrays.fill(dp, 1);
            Arrays.fill(parent, -1);

            int maxLen = 1, maxIdx = 0;
            for (int i = 1; i < n; i++) {
                for (int j = 0; j < i; j++) {
                    if (trophies[j] < trophies[i] && dp[j] + 1 > dp[i]) {
                        dp[i] = dp[j] + 1;
                        parent[i] = j;
                    }
                }
                if (dp[i] > maxLen) {
                    maxLen = dp[i];
                    maxIdx = i;
                }
            }

            ArrayList<Integer> path = new ArrayList<>();
            int idx = maxIdx;
            while (idx != -1) {
                path.add(idx + 1);
                idx = parent[idx];
            }
            Collections.reverse(path);

            sb.append(maxLen).append("\\n");
            for (int i = 0; i < path.size(); i++) {
                if (i > 0) sb.append(" ");
                sb.append(path.get(i));
            }
            sb.append("\\n");
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
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int n;
        cin >> n;

        vector<int> trophies(n);
        for (int i = 0; i < n; i++) {
            cin >> trophies[i];
        }

        vector<int> dp(n, 1), parent(n, -1);

        int maxLen = 1, maxIdx = 0;
        for (int i = 1; i < n; i++) {
            for (int j = 0; j < i; j++) {
                if (trophies[j] < trophies[i] && dp[j] + 1 > dp[i]) {
                    dp[i] = dp[j] + 1;
                    parent[i] = j;
                }
            }
            if (dp[i] > maxLen) {
                maxLen = dp[i];
                maxIdx = i;
            }
        }

        vector<int> path;
        int idx = maxIdx;
        while (idx != -1) {
            path.push_back(idx + 1);
            idx = parent[idx];
        }
        reverse(path.begin(), path.end());

        cout << maxLen << "\\n";
        for (int i = 0; i < path.size(); i++) {
            if (i > 0) cout << " ";
            cout << path[i];
        }
        cout << "\\n";
    }

    return 0;
}
"""
    }
]

# Problem 1985: Friends / Almost Friends
solutions['1985'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

def get_digits(n):
    return set(str(n))

def can_be_almost(s):
    # Check if we can apply one operation to make digits match another set
    # Operation: adjacent digits a,b -> (a-1, b+1) or (a+1, b-1)
    # Return all possible digit sets after one operation
    results = []
    s_list = list(s)
    n = len(s_list)

    for i in range(n - 1):
        # Try (a-1, b+1)
        a, b = int(s_list[i]), int(s_list[i + 1])
        if a > 0:  # a-1 >= 0
            if i == 0 and a - 1 == 0:
                pass  # leading zero not allowed
            else:
                new_s = s_list[:]
                new_s[i] = str(a - 1)
                new_s[i + 1] = str(b + 1) if b < 9 else str(b)
                if b < 9:
                    results.append(set(''.join(new_s)))

        # Try (a+1, b-1)
        if a < 9 and b > 0:
            new_s = s_list[:]
            new_s[i] = str(a + 1)
            new_s[i + 1] = str(b - 1)
            results.append(set(''.join(new_s)))

    return results

while True:
    line = input().strip()
    if not line:
        continue
    parts = line.split()
    a, b = parts[0], parts[1]

    digits_a = get_digits(a)
    digits_b = get_digits(b)

    if digits_a == digits_b:
        print("friends")
    else:
        # Check if one operation can make them friends
        is_almost = False

        # Try operations on a
        for new_digits in can_be_almost(a):
            if new_digits == digits_b:
                is_almost = True
                break

        # Try operations on b
        if not is_almost:
            for new_digits in can_be_almost(b):
                if new_digits == digits_a:
                    is_almost = True
                    break

        if is_almost:
            print("almost friends")
        else:
            print("nothing")
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line;

        while ((line = br.readLine()) != null && !line.isEmpty()) {
            String[] parts = line.split(" ");
            String a = parts[0], b = parts[1];

            Set<Character> digitsA = getDigits(a);
            Set<Character> digitsB = getDigits(b);

            if (digitsA.equals(digitsB)) {
                System.out.println("friends");
            } else {
                boolean isAlmost = false;

                for (Set<Character> newDigits : canBeAlmost(a)) {
                    if (newDigits.equals(digitsB)) {
                        isAlmost = true;
                        break;
                    }
                }

                if (!isAlmost) {
                    for (Set<Character> newDigits : canBeAlmost(b)) {
                        if (newDigits.equals(digitsA)) {
                            isAlmost = true;
                            break;
                        }
                    }
                }

                System.out.println(isAlmost ? "almost friends" : "nothing");
            }
        }
    }

    static Set<Character> getDigits(String s) {
        Set<Character> set = new HashSet<>();
        for (char c : s.toCharArray()) set.add(c);
        return set;
    }

    static List<Set<Character>> canBeAlmost(String s) {
        List<Set<Character>> results = new ArrayList<>();
        char[] arr = s.toCharArray();
        int n = arr.length;

        for (int i = 0; i < n - 1; i++) {
            int a = arr[i] - '0', b = arr[i + 1] - '0';

            if (a > 0 && b < 9) {
                if (!(i == 0 && a - 1 == 0)) {
                    char[] newArr = arr.clone();
                    newArr[i] = (char)('0' + a - 1);
                    newArr[i + 1] = (char)('0' + b + 1);
                    results.add(getDigits(new String(newArr)));
                }
            }

            if (a < 9 && b > 0) {
                char[] newArr = arr.clone();
                newArr[i] = (char)('0' + a + 1);
                newArr[i + 1] = (char)('0' + b - 1);
                results.add(getDigits(new String(newArr)));
            }
        }

        return results;
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <set>
#include <vector>
#include <string>
using namespace std;

set<char> getDigits(const string& s) {
    return set<char>(s.begin(), s.end());
}

vector<set<char>> canBeAlmost(const string& s) {
    vector<set<char>> results;
    int n = s.length();

    for (int i = 0; i < n - 1; i++) {
        int a = s[i] - '0', b = s[i + 1] - '0';

        if (a > 0 && b < 9) {
            if (!(i == 0 && a - 1 == 0)) {
                string newS = s;
                newS[i] = '0' + a - 1;
                newS[i + 1] = '0' + b + 1;
                results.push_back(getDigits(newS));
            }
        }

        if (a < 9 && b > 0) {
            string newS = s;
            newS[i] = '0' + a + 1;
            newS[i + 1] = '0' + b - 1;
            results.push_back(getDigits(newS));
        }
    }

    return results;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string a, b;
    while (cin >> a >> b) {
        set<char> digitsA = getDigits(a);
        set<char> digitsB = getDigits(b);

        if (digitsA == digitsB) {
            cout << "friends" << endl;
        } else {
            bool isAlmost = false;

            for (auto& newDigits : canBeAlmost(a)) {
                if (newDigits == digitsB) {
                    isAlmost = true;
                    break;
                }
            }

            if (!isAlmost) {
                for (auto& newDigits : canBeAlmost(b)) {
                    if (newDigits == digitsA) {
                        isAlmost = true;
                        break;
                    }
                }
            }

            cout << (isAlmost ? "almost friends" : "nothing") << endl;
        }
    }

    return 0;
}
"""
    }
]

# Problem 1996: Minesweeper (Complex variant)
solutions['1996'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

n = int(input())
board = []
for _ in range(n):
    board.append(list(input().strip()))

# Each cell either has mines (1-9) or a number (0-9)
# We need to find mine configuration

# This is a constraint satisfaction problem
# Use backtracking

result = [['0'] * n for _ in range(n)]

def get_neighbors(r, c):
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                neighbors.append((nr, nc))
    return neighbors

# Find cells with numbers (constraints)
# Find cells with dots (unknowns)

constraints = []
unknowns = set()

for i in range(n):
    for j in range(n):
        if board[i][j] == '.':
            unknowns.add((i, j))
        elif board[i][j].isdigit():
            constraints.append((i, j, int(board[i][j])))

# For simplicity, use greedy/heuristic approach
# Assign mines based on constraints

mines = [[0] * n for _ in range(n)]

def solve():
    # Simple constraint propagation
    changed = True
    while changed:
        changed = False
        for r, c, num in constraints:
            neighbors = get_neighbors(r, c)
            unknown_neighbors = [(nr, nc) for nr, nc in neighbors if (nr, nc) in unknowns]
            mine_count = sum(mines[nr][nc] for nr, nc in neighbors)

            remaining = num - mine_count
            if remaining == len(unknown_neighbors) and remaining > 0:
                # All unknowns must be mines
                for nr, nc in unknown_neighbors:
                    mines[nr][nc] = 1
                    unknowns.discard((nr, nc))
                    changed = True
            elif remaining == 0:
                # All unknowns are safe
                for nr, nc in unknown_neighbors:
                    unknowns.discard((nr, nc))
                    changed = True

solve()

# Build result
for i in range(n):
    for j in range(n):
        if board[i][j] == '.':
            if mines[i][j] > 0:
                result[i][j] = '*'
            else:
                # Count surrounding mines
                count = sum(mines[nr][nc] for nr, nc in get_neighbors(i, j))
                result[i][j] = str(count)
        else:
            # It's a constraint cell - show M if unsolvable or number
            count = sum(mines[nr][nc] for nr, nc in get_neighbors(i, j))
            if count > 9:
                result[i][j] = 'M'
            else:
                result[i][j] = str(count)

for row in result:
    print(''.join(row))
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    static int n;
    static char[][] board;
    static int[][] mines;
    static Set<Integer> unknowns = new HashSet<>();

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        n = Integer.parseInt(br.readLine().trim());
        board = new char[n][n];
        mines = new int[n][n];

        for (int i = 0; i < n; i++) {
            board[i] = br.readLine().toCharArray();
        }

        List<int[]> constraints = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (board[i][j] == '.') {
                    unknowns.add(i * n + j);
                } else if (Character.isDigit(board[i][j])) {
                    constraints.add(new int[]{i, j, board[i][j] - '0'});
                }
            }
        }

        boolean changed = true;
        while (changed) {
            changed = false;
            for (int[] con : constraints) {
                int r = con[0], c = con[1], num = con[2];
                List<int[]> neighbors = getNeighbors(r, c);
                List<Integer> unknownNeighbors = new ArrayList<>();
                int mineCount = 0;

                for (int[] nb : neighbors) {
                    int key = nb[0] * n + nb[1];
                    if (unknowns.contains(key)) {
                        unknownNeighbors.add(key);
                    }
                    mineCount += mines[nb[0]][nb[1]];
                }

                int remaining = num - mineCount;
                if (remaining == unknownNeighbors.size() && remaining > 0) {
                    for (int key : unknownNeighbors) {
                        mines[key / n][key % n] = 1;
                        unknowns.remove(key);
                        changed = true;
                    }
                } else if (remaining == 0) {
                    for (int key : unknownNeighbors) {
                        unknowns.remove(key);
                        changed = true;
                    }
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (board[i][j] == '.') {
                    if (mines[i][j] > 0) {
                        sb.append('*');
                    } else {
                        int count = 0;
                        for (int[] nb : getNeighbors(i, j)) {
                            count += mines[nb[0]][nb[1]];
                        }
                        sb.append(count);
                    }
                } else {
                    int count = 0;
                    for (int[] nb : getNeighbors(i, j)) {
                        count += mines[nb[0]][nb[1]];
                    }
                    sb.append(count > 9 ? 'M' : (char)('0' + count));
                }
            }
            sb.append("\\n");
        }
        System.out.print(sb);
    }

    static List<int[]> getNeighbors(int r, int c) {
        List<int[]> neighbors = new ArrayList<>();
        for (int dr = -1; dr <= 1; dr++) {
            for (int dc = -1; dc <= 1; dc++) {
                if (dr == 0 && dc == 0) continue;
                int nr = r + dr, nc = c + dc;
                if (nr >= 0 && nr < n && nc >= 0 && nc < n) {
                    neighbors.add(new int[]{nr, nc});
                }
            }
        }
        return neighbors;
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <vector>
#include <set>
using namespace std;

int n;
char board[500][500];
int mines[500][500];
set<int> unknowns;

vector<pair<int,int>> getNeighbors(int r, int c) {
    vector<pair<int,int>> neighbors;
    for (int dr = -1; dr <= 1; dr++) {
        for (int dc = -1; dc <= 1; dc++) {
            if (dr == 0 && dc == 0) continue;
            int nr = r + dr, nc = c + dc;
            if (nr >= 0 && nr < n && nc >= 0 && nc < n) {
                neighbors.push_back({nr, nc});
            }
        }
    }
    return neighbors;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;
    vector<tuple<int,int,int>> constraints;

    for (int i = 0; i < n; i++) {
        cin >> board[i];
        for (int j = 0; j < n; j++) {
            if (board[i][j] == '.') {
                unknowns.insert(i * n + j);
            } else if (isdigit(board[i][j])) {
                constraints.push_back({i, j, board[i][j] - '0'});
            }
        }
    }

    bool changed = true;
    while (changed) {
        changed = false;
        for (auto& [r, c, num] : constraints) {
            auto neighbors = getNeighbors(r, c);
            vector<int> unknownNeighbors;
            int mineCount = 0;

            for (auto& [nr, nc] : neighbors) {
                int key = nr * n + nc;
                if (unknowns.count(key)) {
                    unknownNeighbors.push_back(key);
                }
                mineCount += mines[nr][nc];
            }

            int remaining = num - mineCount;
            if (remaining == (int)unknownNeighbors.size() && remaining > 0) {
                for (int key : unknownNeighbors) {
                    mines[key / n][key % n] = 1;
                    unknowns.erase(key);
                    changed = true;
                }
            } else if (remaining == 0) {
                for (int key : unknownNeighbors) {
                    unknowns.erase(key);
                    changed = true;
                }
            }
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (board[i][j] == '.') {
                if (mines[i][j] > 0) {
                    cout << '*';
                } else {
                    int count = 0;
                    for (auto& [nr, nc] : getNeighbors(i, j)) {
                        count += mines[nr][nc];
                    }
                    cout << count;
                }
            } else {
                int count = 0;
                for (auto& [nr, nc] : getNeighbors(i, j)) {
                    count += mines[nr][nc];
                }
                cout << (count > 9 ? 'M' : (char)('0' + count));
            }
        }
        cout << "\\n";
    }

    return 0;
}
"""
    }
]

# Problem 1998: QuadTree Black/White count
solutions['1998'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

n, m = map(int, input().split())
image = []
for _ in range(n):
    image.append(input().strip())

# Pad to power of 2
size = 1
while size < max(n, m):
    size *= 2

# Create padded image (white = 0)
grid = [[0] * size for _ in range(size)]
for i in range(n):
    for j in range(m):
        grid[i][j] = int(image[i][j])

def count_quadtree(r, c, sz):
    # Returns (white_nodes, black_nodes)
    if sz == 1:
        if grid[r][c] == 0:
            return (1, 0)
        else:
            return (0, 1)

    # Check if all same color
    first = grid[r][c]
    all_same = True
    for i in range(r, r + sz):
        for j in range(c, c + sz):
            if grid[i][j] != first:
                all_same = False
                break
        if not all_same:
            break

    if all_same:
        if first == 0:
            return (1, 0)
        else:
            return (0, 1)

    # Divide into 4 quadrants
    half = sz // 2
    w1, b1 = count_quadtree(r, c, half)
    w2, b2 = count_quadtree(r, c + half, half)
    w3, b3 = count_quadtree(r + half, c, half)
    w4, b4 = count_quadtree(r + half, c + half, half)

    return (w1 + w2 + w3 + w4, b1 + b2 + b3 + b4)

white, black = count_quadtree(0, 0, size)
print(white, black)
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    static int[][] grid;
    static int size;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        size = 1;
        while (size < Math.max(n, m)) size *= 2;

        grid = new int[size][size];
        for (int i = 0; i < n; i++) {
            String line = br.readLine();
            for (int j = 0; j < m; j++) {
                grid[i][j] = line.charAt(j) - '0';
            }
        }

        int[] result = countQuadtree(0, 0, size);
        System.out.println(result[0] + " " + result[1]);
    }

    static int[] countQuadtree(int r, int c, int sz) {
        if (sz == 1) {
            if (grid[r][c] == 0) return new int[]{1, 0};
            else return new int[]{0, 1};
        }

        int first = grid[r][c];
        boolean allSame = true;
        outer:
        for (int i = r; i < r + sz; i++) {
            for (int j = c; j < c + sz; j++) {
                if (grid[i][j] != first) {
                    allSame = false;
                    break outer;
                }
            }
        }

        if (allSame) {
            if (first == 0) return new int[]{1, 0};
            else return new int[]{0, 1};
        }

        int half = sz / 2;
        int[] r1 = countQuadtree(r, c, half);
        int[] r2 = countQuadtree(r, c + half, half);
        int[] r3 = countQuadtree(r + half, c, half);
        int[] r4 = countQuadtree(r + half, c + half, half);

        return new int[]{r1[0]+r2[0]+r3[0]+r4[0], r1[1]+r2[1]+r3[1]+r4[1]};
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <vector>
using namespace std;

int grid[1024][1024];
int size_;

pair<int,int> countQuadtree(int r, int c, int sz) {
    if (sz == 1) {
        if (grid[r][c] == 0) return {1, 0};
        else return {0, 1};
    }

    int first = grid[r][c];
    bool allSame = true;
    for (int i = r; i < r + sz && allSame; i++) {
        for (int j = c; j < c + sz && allSame; j++) {
            if (grid[i][j] != first) {
                allSame = false;
            }
        }
    }

    if (allSame) {
        if (first == 0) return {1, 0};
        else return {0, 1};
    }

    int half = sz / 2;
    auto r1 = countQuadtree(r, c, half);
    auto r2 = countQuadtree(r, c + half, half);
    auto r3 = countQuadtree(r + half, c, half);
    auto r4 = countQuadtree(r + half, c + half, half);

    return {r1.first+r2.first+r3.first+r4.first, r1.second+r2.second+r3.second+r4.second};
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    size_ = 1;
    while (size_ < max(n, m)) size_ *= 2;

    for (int i = 0; i < n; i++) {
        string line;
        cin >> line;
        for (int j = 0; j < m; j++) {
            grid[i][j] = line[j] - '0';
        }
    }

    auto result = countQuadtree(0, 0, size_);
    cout << result.first << " " << result.second << endl;

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
