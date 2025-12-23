import json

with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r') as f:
    data = json.load(f)

id_to_idx = {}
for idx, p in enumerate(data):
    if 'original_id' in p:
        id_to_idx[p['original_id']] = idx

solutions = {}

# Problem 1969: DNA - Hamming Distance
solutions['1969'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

n, m = map(int, input().split())
dna = [input().strip() for _ in range(n)]

result = []
total_dist = 0

for i in range(m):
    cnt = {'A': 0, 'C': 0, 'G': 0, 'T': 0}
    for j in range(n):
        cnt[dna[j][i]] += 1

    best_char = 'A'
    best_cnt = cnt['A']
    for c in ['C', 'G', 'T']:
        if cnt[c] > best_cnt:
            best_cnt = cnt[c]
            best_char = c

    result.append(best_char)
    total_dist += n - best_cnt

print(''.join(result))
print(total_dist)
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
        int m = Integer.parseInt(st.nextToken());

        String[] dna = new String[n];
        for (int i = 0; i < n; i++) {
            dna[i] = br.readLine();
        }

        StringBuilder result = new StringBuilder();
        int totalDist = 0;
        char[] order = {'A', 'C', 'G', 'T'};

        for (int i = 0; i < m; i++) {
            int[] cnt = new int[4];
            for (int j = 0; j < n; j++) {
                char c = dna[j].charAt(i);
                if (c == 'A') cnt[0]++;
                else if (c == 'C') cnt[1]++;
                else if (c == 'G') cnt[2]++;
                else cnt[3]++;
            }

            int maxCnt = 0;
            char bestChar = 'A';
            for (int k = 0; k < 4; k++) {
                if (cnt[k] > maxCnt) {
                    maxCnt = cnt[k];
                    bestChar = order[k];
                }
            }

            result.append(bestChar);
            totalDist += n - maxCnt;
        }

        System.out.println(result);
        System.out.println(totalDist);
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    string dna[1000];
    for (int i = 0; i < n; i++) {
        cin >> dna[i];
    }

    string result = "";
    int totalDist = 0;
    char order[] = {'A', 'C', 'G', 'T'};

    for (int i = 0; i < m; i++) {
        int cnt[4] = {0};
        for (int j = 0; j < n; j++) {
            char c = dna[j][i];
            if (c == 'A') cnt[0]++;
            else if (c == 'C') cnt[1]++;
            else if (c == 'G') cnt[2]++;
            else cnt[3]++;
        }

        int maxCnt = 0;
        char bestChar = 'A';
        for (int k = 0; k < 4; k++) {
            if (cnt[k] > maxCnt) {
                maxCnt = cnt[k];
                bestChar = order[k];
            }
        }

        result += bestChar;
        totalDist += n - maxCnt;
    }

    cout << result << "\\n" << totalDist << "\\n";
    return 0;
}
"""
    }
]

# Problem 1977: Perfect Square Sum
solutions['1977'] = [
    {
        "language": "python",
        "code": """import math

m = int(input())
n = int(input())

squares = []
i = 1
while i * i <= n:
    if i * i >= m:
        squares.append(i * i)
    i += 1

if not squares:
    print(-1)
else:
    print(sum(squares))
    print(min(squares))
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int m = sc.nextInt();
        int n = sc.nextInt();

        ArrayList<Integer> squares = new ArrayList<>();
        int i = 1;
        while (i * i <= n) {
            if (i * i >= m) {
                squares.add(i * i);
            }
            i++;
        }

        if (squares.isEmpty()) {
            System.out.println(-1);
        } else {
            int sum = 0;
            int min = Integer.MAX_VALUE;
            for (int sq : squares) {
                sum += sq;
                min = Math.min(min, sq);
            }
            System.out.println(sum);
            System.out.println(min);
        }
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <vector>
#include <climits>
using namespace std;

int main() {
    int m, n;
    cin >> m >> n;

    vector<int> squares;
    int i = 1;
    while (i * i <= n) {
        if (i * i >= m) {
            squares.push_back(i * i);
        }
        i++;
    }

    if (squares.empty()) {
        cout << -1 << endl;
    } else {
        int sum = 0;
        int minVal = INT_MAX;
        for (int sq : squares) {
            sum += sq;
            if (sq < minVal) minVal = sq;
        }
        cout << sum << endl;
        cout << minVal << endl;
    }

    return 0;
}
"""
    }
]

# Problem 1979: n-dramatic number
solutions['1979'] = [
    {
        "language": "python",
        "code": """n, k = map(int, input().split())

# Find smallest n-dramatic number ending with k
# If we multiply by n and get a cyclic right shift
# Example: 102564 * 4 = 410256

def solve(n, k):
    # The number ends with k
    # When multiplied by n, it becomes a right cyclic shift
    # So the result starts with k

    # Try building the number digit by digit from right
    # Start with k, simulate multiplication

    seen = set()
    digits = [k]
    carry = 0

    while True:
        last = digits[-1]
        # last * n + carry should give us the next digit and new carry
        # But we need to find what digit d gives us: d * n + carry ends with digits[0] initially

        # Actually, let's think differently
        # Number = d_m d_{m-1} ... d_1 d_0 where d_0 = k
        # Number * n = d_0 d_m d_{m-1} ... d_1 (right shift)

        # So if Number = X, then X * n = k * 10^m + X // 10
        # X * n - X/10 = k * 10^m
        # X * (n - 1/10) = k * 10^m
        # X * (10n - 1) / 10 = k * 10^m
        # X * (10n - 1) = k * 10^(m+1)

        # Let's just simulate
        break

    # Better approach: simulate the multiplication
    # Build number backwards
    digits = []
    current = k
    carry = 0

    for _ in range(10000):  # max iterations
        prod = current * n + carry
        next_digit = prod % 10
        carry = prod // 10
        digits.append(current)

        if next_digit == k and carry == 0 and len(digits) > 1:
            # Check if this forms a valid number
            num_str = ''.join(str(d) for d in reversed(digits))
            if num_str[0] != '0':
                return num_str

        current = next_digit

        state = (current, carry)
        if state in seen:
            break
        seen.add(state)

    return "0"

print(solve(n, k))
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int k = sc.nextInt();

        // Simulate building the number
        ArrayList<Integer> digits = new ArrayList<>();
        Set<Long> seen = new HashSet<>();

        int current = k;
        int carry = 0;

        for (int i = 0; i < 1000000; i++) {
            int prod = current * n + carry;
            int nextDigit = prod % 10;
            carry = prod / 10;
            digits.add(current);

            if (nextDigit == k && carry == 0 && digits.size() > 1) {
                StringBuilder sb = new StringBuilder();
                for (int j = digits.size() - 1; j >= 0; j--) {
                    sb.append(digits.get(j));
                }
                String numStr = sb.toString();
                if (numStr.charAt(0) != '0') {
                    System.out.println(numStr);
                    return;
                }
            }

            current = nextDigit;
            long state = (long)current * 100 + carry;
            if (seen.contains(state)) break;
            seen.add(state);
        }

        System.out.println(0);
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <vector>
#include <set>
#include <string>
using namespace std;

int main() {
    int n, k;
    cin >> n >> k;

    vector<int> digits;
    set<pair<int,int>> seen;

    int current = k;
    int carry = 0;

    for (int i = 0; i < 1000000; i++) {
        int prod = current * n + carry;
        int nextDigit = prod % 10;
        carry = prod / 10;
        digits.push_back(current);

        if (nextDigit == k && carry == 0 && digits.size() > 1) {
            string numStr = "";
            for (int j = digits.size() - 1; j >= 0; j--) {
                numStr += ('0' + digits[j]);
            }
            if (numStr[0] != '0') {
                cout << numStr << endl;
                return 0;
            }
        }

        current = nextDigit;
        if (seen.count({current, carry})) break;
        seen.insert({current, carry});
    }

    cout << 0 << endl;
    return 0;
}
"""
    }
]

# Problem 1980: Hamburger eating
solutions['1980'] = [
    {
        "language": "python",
        "code": """n, m, t = map(int, input().split())

# Find max burgers with min cola time
# Try all combinations of tower burgers and bulgogi burgers

best_count = 0
best_cola = t

for tower in range(t // n + 1):
    remaining = t - tower * n
    bulgogi = remaining // m
    total = tower + bulgogi
    cola_time = t - tower * n - bulgogi * m

    if cola_time < best_cola or (cola_time == best_cola and total > best_count):
        best_cola = cola_time
        best_count = total

print(best_count, best_cola)
"""
    },
    {
        "language": "java",
        "code": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int t = sc.nextInt();

        int bestCount = 0;
        int bestCola = t;

        for (int tower = 0; tower <= t / n; tower++) {
            int remaining = t - tower * n;
            int bulgogi = remaining / m;
            int total = tower + bulgogi;
            int colaTime = t - tower * n - bulgogi * m;

            if (colaTime < bestCola || (colaTime == bestCola && total > bestCount)) {
                bestCola = colaTime;
                bestCount = total;
            }
        }

        System.out.println(bestCount + " " + bestCola);
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
using namespace std;

int main() {
    int n, m, t;
    cin >> n >> m >> t;

    int bestCount = 0;
    int bestCola = t;

    for (int tower = 0; tower <= t / n; tower++) {
        int remaining = t - tower * n;
        int bulgogi = remaining / m;
        int total = tower + bulgogi;
        int colaTime = t - tower * n - bulgogi * m;

        if (colaTime < bestCola || (colaTime == bestCola && total > bestCount)) {
            bestCola = colaTime;
            bestCount = total;
        }
    }

    cout << bestCount << " " << bestCola << endl;
    return 0;
}
"""
    }
]

# Problem 1981: Array Max-Min Difference (BFS + Binary Search)
solutions['1981'] = [
    {
        "language": "python",
        "code": """import sys
from collections import deque
input = sys.stdin.readline

n = int(input())
board = []
for _ in range(n):
    board.append(list(map(int, input().split())))

min_val = min(min(row) for row in board)
max_val = max(max(row) for row in board)

dx = [0, 0, 1, -1]
dy = [1, -1, 0, 0]

def can_reach(lo, hi):
    if not (lo <= board[0][0] <= hi) or not (lo <= board[n-1][n-1] <= hi):
        return False

    visited = [[False] * n for _ in range(n)]
    queue = deque([(0, 0)])
    visited[0][0] = True

    while queue:
        x, y = queue.popleft()
        if x == n - 1 and y == n - 1:
            return True

        for i in range(4):
            nx, ny = x + dx[i], y + dy[i]
            if 0 <= nx < n and 0 <= ny < n and not visited[nx][ny]:
                if lo <= board[nx][ny] <= hi:
                    visited[nx][ny] = True
                    queue.append((nx, ny))

    return False

ans = max_val - min_val
for lo in range(min_val, max_val + 1):
    for hi in range(lo, max_val + 1):
        if hi - lo >= ans:
            break
        if can_reach(lo, hi):
            ans = hi - lo
            break

print(ans)
"""
    },
    {
        "language": "java",
        "code": """import java.io.*;
import java.util.*;

public class Main {
    static int n;
    static int[][] board;
    static int[] dx = {0, 0, 1, -1};
    static int[] dy = {1, -1, 0, 0};

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        n = Integer.parseInt(br.readLine().trim());
        board = new int[n][n];

        int minVal = 201, maxVal = -1;
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                board[i][j] = Integer.parseInt(st.nextToken());
                minVal = Math.min(minVal, board[i][j]);
                maxVal = Math.max(maxVal, board[i][j]);
            }
        }

        int ans = maxVal - minVal;
        for (int lo = minVal; lo <= maxVal; lo++) {
            for (int hi = lo; hi <= maxVal; hi++) {
                if (hi - lo >= ans) break;
                if (canReach(lo, hi)) {
                    ans = hi - lo;
                    break;
                }
            }
        }

        System.out.println(ans);
    }

    static boolean canReach(int lo, int hi) {
        if (board[0][0] < lo || board[0][0] > hi) return false;
        if (board[n-1][n-1] < lo || board[n-1][n-1] > hi) return false;

        boolean[][] visited = new boolean[n][n];
        Queue<int[]> queue = new LinkedList<>();
        queue.add(new int[]{0, 0});
        visited[0][0] = true;

        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            if (cur[0] == n - 1 && cur[1] == n - 1) return true;

            for (int i = 0; i < 4; i++) {
                int nx = cur[0] + dx[i];
                int ny = cur[1] + dy[i];
                if (nx >= 0 && nx < n && ny >= 0 && ny < n && !visited[nx][ny]) {
                    if (board[nx][ny] >= lo && board[nx][ny] <= hi) {
                        visited[nx][ny] = true;
                        queue.add(new int[]{nx, ny});
                    }
                }
            }
        }
        return false;
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
#include <queue>
#include <cstring>
using namespace std;

int n;
int board[101][101];
bool visited[101][101];
int dx[] = {0, 0, 1, -1};
int dy[] = {1, -1, 0, 0};

bool canReach(int lo, int hi) {
    if (board[0][0] < lo || board[0][0] > hi) return false;
    if (board[n-1][n-1] < lo || board[n-1][n-1] > hi) return false;

    memset(visited, false, sizeof(visited));
    queue<pair<int,int>> q;
    q.push({0, 0});
    visited[0][0] = true;

    while (!q.empty()) {
        auto [x, y] = q.front();
        q.pop();

        if (x == n - 1 && y == n - 1) return true;

        for (int i = 0; i < 4; i++) {
            int nx = x + dx[i];
            int ny = y + dy[i];
            if (nx >= 0 && nx < n && ny >= 0 && ny < n && !visited[nx][ny]) {
                if (board[nx][ny] >= lo && board[nx][ny] <= hi) {
                    visited[nx][ny] = true;
                    q.push({nx, ny});
                }
            }
        }
    }
    return false;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;
    int minVal = 201, maxVal = -1;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cin >> board[i][j];
            minVal = min(minVal, board[i][j]);
            maxVal = max(maxVal, board[i][j]);
        }
    }

    int ans = maxVal - minVal;
    for (int lo = minVal; lo <= maxVal; lo++) {
        for (int hi = lo; hi <= maxVal; hi++) {
            if (hi - lo >= ans) break;
            if (canReach(lo, hi)) {
                ans = hi - lo;
                break;
            }
        }
    }

    cout << ans << endl;
    return 0;
}
"""
    }
]

# Problem 1986: Chess - Safe positions
solutions['1986'] = [
    {
        "language": "python",
        "code": """import sys
input = sys.stdin.readline

n, m = map(int, input().split())
board = [[0] * (m + 1) for _ in range(n + 1)]  # 0 = safe, 1 = attacked, 2 = piece

# Queen attacks
queen_line = list(map(int, input().split()))
num_queens = queen_line[0]
queens = []
for i in range(num_queens):
    r, c = queen_line[1 + 2*i], queen_line[2 + 2*i]
    queens.append((r, c))
    board[r][c] = 2

# Knight attacks
knight_line = list(map(int, input().split()))
num_knights = knight_line[0]
knights = []
for i in range(num_knights):
    r, c = knight_line[1 + 2*i], knight_line[2 + 2*i]
    knights.append((r, c))
    board[r][c] = 2

# Pawn blocks
pawn_line = list(map(int, input().split()))
num_pawns = pawn_line[0]
for i in range(num_pawns):
    r, c = pawn_line[1 + 2*i], pawn_line[2 + 2*i]
    board[r][c] = 2

# Mark queen attacks
directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
for qr, qc in queens:
    for dr, dc in directions:
        nr, nc = qr + dr, qc + dc
        while 1 <= nr <= n and 1 <= nc <= m:
            if board[nr][nc] == 2:  # blocked by piece
                break
            if board[nr][nc] == 0:
                board[nr][nc] = 1
            nr += dr
            nc += dc

# Mark knight attacks
knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
for kr, kc in knights:
    for dr, dc in knight_moves:
        nr, nc = kr + dr, kc + dc
        if 1 <= nr <= n and 1 <= nc <= m and board[nr][nc] == 0:
            board[nr][nc] = 1

# Count safe positions
safe = 0
for i in range(1, n + 1):
    for j in range(1, m + 1):
        if board[i][j] == 0:
            safe += 1

print(safe)
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
        int m = Integer.parseInt(st.nextToken());

        int[][] board = new int[n + 1][m + 1];

        // Queens
        st = new StringTokenizer(br.readLine());
        int numQueens = Integer.parseInt(st.nextToken());
        int[][] queens = new int[numQueens][2];
        for (int i = 0; i < numQueens; i++) {
            queens[i][0] = Integer.parseInt(st.nextToken());
            queens[i][1] = Integer.parseInt(st.nextToken());
            board[queens[i][0]][queens[i][1]] = 2;
        }

        // Knights
        st = new StringTokenizer(br.readLine());
        int numKnights = Integer.parseInt(st.nextToken());
        int[][] knights = new int[numKnights][2];
        for (int i = 0; i < numKnights; i++) {
            knights[i][0] = Integer.parseInt(st.nextToken());
            knights[i][1] = Integer.parseInt(st.nextToken());
            board[knights[i][0]][knights[i][1]] = 2;
        }

        // Pawns
        st = new StringTokenizer(br.readLine());
        int numPawns = Integer.parseInt(st.nextToken());
        for (int i = 0; i < numPawns; i++) {
            int r = Integer.parseInt(st.nextToken());
            int c = Integer.parseInt(st.nextToken());
            board[r][c] = 2;
        }

        // Queen attacks
        int[][] dirs = {{0,1},{0,-1},{1,0},{-1,0},{1,1},{1,-1},{-1,1},{-1,-1}};
        for (int[] q : queens) {
            for (int[] d : dirs) {
                int nr = q[0] + d[0], nc = q[1] + d[1];
                while (nr >= 1 && nr <= n && nc >= 1 && nc <= m) {
                    if (board[nr][nc] == 2) break;
                    if (board[nr][nc] == 0) board[nr][nc] = 1;
                    nr += d[0]; nc += d[1];
                }
            }
        }

        // Knight attacks
        int[][] kmoves = {{-2,-1},{-2,1},{-1,-2},{-1,2},{1,-2},{1,2},{2,-1},{2,1}};
        for (int[] k : knights) {
            for (int[] km : kmoves) {
                int nr = k[0] + km[0], nc = k[1] + km[1];
                if (nr >= 1 && nr <= n && nc >= 1 && nc <= m && board[nr][nc] == 0) {
                    board[nr][nc] = 1;
                }
            }
        }

        int safe = 0;
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= m; j++) {
                if (board[i][j] == 0) safe++;
            }
        }

        System.out.println(safe);
    }
}
"""
    },
    {
        "language": "cpp",
        "code": """#include <iostream>
using namespace std;

int board[1001][1001];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    int numQueens;
    cin >> numQueens;
    int queens[numQueens][2];
    for (int i = 0; i < numQueens; i++) {
        cin >> queens[i][0] >> queens[i][1];
        board[queens[i][0]][queens[i][1]] = 2;
    }

    int numKnights;
    cin >> numKnights;
    int knights[numKnights][2];
    for (int i = 0; i < numKnights; i++) {
        cin >> knights[i][0] >> knights[i][1];
        board[knights[i][0]][knights[i][1]] = 2;
    }

    int numPawns;
    cin >> numPawns;
    for (int i = 0; i < numPawns; i++) {
        int r, c;
        cin >> r >> c;
        board[r][c] = 2;
    }

    int dirs[8][2] = {{0,1},{0,-1},{1,0},{-1,0},{1,1},{1,-1},{-1,1},{-1,-1}};
    for (int i = 0; i < numQueens; i++) {
        for (auto& d : dirs) {
            int nr = queens[i][0] + d[0], nc = queens[i][1] + d[1];
            while (nr >= 1 && nr <= n && nc >= 1 && nc <= m) {
                if (board[nr][nc] == 2) break;
                if (board[nr][nc] == 0) board[nr][nc] = 1;
                nr += d[0]; nc += d[1];
            }
        }
    }

    int kmoves[8][2] = {{-2,-1},{-2,1},{-1,-2},{-1,2},{1,-2},{1,2},{2,-1},{2,1}};
    for (int i = 0; i < numKnights; i++) {
        for (auto& km : kmoves) {
            int nr = knights[i][0] + km[0], nc = knights[i][1] + km[1];
            if (nr >= 1 && nr <= n && nc >= 1 && nc <= m && board[nr][nc] == 0) {
                board[nr][nc] = 1;
            }
        }
    }

    int safe = 0;
    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= m; j++) {
            if (board[i][j] == 0) safe++;
        }
    }

    cout << safe << endl;
    return 0;
}
"""
    }
]

# Problem 1994: Arithmetic Sequence (LIS variant with DP)
solutions['1994'] = [
    {
        "language": "python",
        "code": """import sys
from collections import defaultdict
input = sys.stdin.readline

n = int(input())
nums = []
for _ in range(n):
    nums.append(int(input()))

nums.sort()

if n == 1:
    print(1)
elif n == 2:
    print(2)
else:
    # dp[i][d] = length of arithmetic sequence ending at index i with difference d
    # This is O(n^2) which might be tight but should work

    ans = 2

    # Use dictionary for each position
    dp = [defaultdict(lambda: 1) for _ in range(n)]

    for i in range(1, n):
        for j in range(i):
            d = nums[i] - nums[j]
            dp[i][d] = max(dp[i][d], dp[j][d] + 1)
            ans = max(ans, dp[i][d])

    print(ans)
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

        long[] nums = new long[n];
        for (int i = 0; i < n; i++) {
            nums[i] = Long.parseLong(br.readLine().trim());
        }

        Arrays.sort(nums);

        if (n == 1) {
            System.out.println(1);
            return;
        }
        if (n == 2) {
            System.out.println(2);
            return;
        }

        int ans = 2;
        HashMap<Long, Integer>[] dp = new HashMap[n];
        for (int i = 0; i < n; i++) {
            dp[i] = new HashMap<>();
        }

        for (int i = 1; i < n; i++) {
            for (int j = 0; j < i; j++) {
                long d = nums[i] - nums[j];
                int prev = dp[j].getOrDefault(d, 1);
                int curr = dp[i].getOrDefault(d, 1);
                dp[i].put(d, Math.max(curr, prev + 1));
                ans = Math.max(ans, dp[i].get(d));
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
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    long long nums[n];
    for (int i = 0; i < n; i++) {
        cin >> nums[i];
    }

    sort(nums, nums + n);

    if (n == 1) {
        cout << 1 << endl;
        return 0;
    }
    if (n == 2) {
        cout << 2 << endl;
        return 0;
    }

    int ans = 2;
    map<long long, int> dp[n];

    for (int i = 1; i < n; i++) {
        for (int j = 0; j < i; j++) {
            long long d = nums[i] - nums[j];
            int prev = dp[j].count(d) ? dp[j][d] : 1;
            int curr = dp[i].count(d) ? dp[i][d] : 1;
            dp[i][d] = max(curr, prev + 1);
            ans = max(ans, dp[i][d]);
        }
    }

    cout << ans << endl;
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
