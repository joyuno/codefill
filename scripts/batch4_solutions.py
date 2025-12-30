import json

# 배치 4 솔루션: 인덱스 1067, 1085, 1088, 1093, 1103, 1108, 1114, 1122, 1124, 1130
# 문제 ID: 1069, 1034, 2624, 1029, 3860, 2258, 19940, 2957, 10836, 15711

solutions = {
    # 1069 - 집으로 (기하학, 케이스 분석)
    "1069": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
import math
input = sys.stdin.readline

# 입력: X, Y, D, T
X, Y, D, T = map(int, input().split())

# 원점까지의 거리
dist = math.sqrt(X * X + Y * Y)

# 경우 1: 순수하게 걷기
ans = dist

# 경우 2: 점프만 사용 (정확히 n번 점프로 도달 가능한 경우)
# 점프 한 번으로 D만큼 이동, 시간은 T
if dist >= D:
    # 점프 횟수
    n = int(dist / D)
    # n번 점프 후 남은 거리는 걸어감
    remain = dist - n * D
    ans = min(ans, n * T + remain)
    # n+1번 점프하고 되돌아 걷기
    back = (n + 1) * D - dist
    ans = min(ans, (n + 1) * T + back)
else:
    # 거리가 D보다 작은 경우
    # 점프 한 번 후 되돌아 걷기
    ans = min(ans, T + (D - dist))
    # 점프 두 번으로 정확히 도달 (삼각형 형성)
    ans = min(ans, 2 * T)

print(ans)
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        
        int X = Integer.parseInt(st.nextToken());
        int Y = Integer.parseInt(st.nextToken());
        int D = Integer.parseInt(st.nextToken());
        int T = Integer.parseInt(st.nextToken());
        
        // 원점까지의 거리
        double dist = Math.sqrt((double)X * X + (double)Y * Y);
        
        // 경우 1: 순수하게 걷기
        double ans = dist;
        
        if (dist >= D) {
            // 점프 횟수
            int n = (int)(dist / D);
            // n번 점프 후 남은 거리는 걸어감
            double remain = dist - (double)n * D;
            ans = Math.min(ans, (double)n * T + remain);
            // n+1번 점프하고 되돌아 걷기
            double back = (double)(n + 1) * D - dist;
            ans = Math.min(ans, (double)(n + 1) * T + back);
        } else {
            // 거리가 D보다 작은 경우
            // 점프 한 번 후 되돌아 걷기
            ans = Math.min(ans, (double)T + (D - dist));
            // 점프 두 번으로 정확히 도달 (삼각형 형성)
            ans = Math.min(ans, 2.0 * T);
        }
        
        System.out.println(ans);
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <cmath>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int X, Y, D, T;
    cin >> X >> Y >> D >> T;
    
    // 원점까지의 거리
    double dist = sqrt((double)X * X + (double)Y * Y);
    
    // 경우 1: 순수하게 걷기
    double ans = dist;
    
    if (dist >= D) {
        // 점프 횟수
        int n = (int)(dist / D);
        // n번 점프 후 남은 거리는 걸어감
        double remain = dist - (double)n * D;
        ans = min(ans, (double)n * T + remain);
        // n+1번 점프하고 되돌아 걷기
        double back = (double)(n + 1) * D - dist;
        ans = min(ans, (double)(n + 1) * T + back);
    } else {
        // 거리가 D보다 작은 경우
        // 점프 한 번 후 되돌아 걷기
        ans = min(ans, (double)T + (D - dist));
        // 점프 두 번으로 정확히 도달 (삼각형 형성)
        ans = min(ans, 2.0 * T);
    }
    
    cout.precision(15);
    cout << fixed << ans << endl;
    
    return 0;
}
'''
            }
        ]
    },
    
    # 1034 - 램프 (브루트포스)
    "1034": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from collections import Counter
input = sys.stdin.readline

# 입력
N, M = map(int, input().split())
rows = []
for _ in range(N):
    rows.append(input().strip())
K = int(input())

# 같은 패턴의 행을 그룹화
counter = Counter(rows)

ans = 0
for row, count in counter.items():
    # 해당 행에서 꺼져있는 램프(0) 개수
    zeros = row.count('0')
    
    # K번 눌러서 모든 램프를 켤 수 있는 조건:
    # 1. 0의 개수가 K 이하
    # 2. K와 0의 개수의 홀짝이 같아야 함 (남은 횟수로 같은 열 토글)
    if zeros <= K and (K - zeros) % 2 == 0:
        ans = max(ans, count)

print(ans)
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        
        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());
        
        String[] rows = new String[N];
        for (int i = 0; i < N; i++) {
            rows[i] = br.readLine().trim();
        }
        int K = Integer.parseInt(br.readLine().trim());
        
        // 같은 패턴의 행을 그룹화
        Map<String, Integer> counter = new HashMap<>();
        for (String row : rows) {
            counter.put(row, counter.getOrDefault(row, 0) + 1);
        }
        
        int ans = 0;
        for (Map.Entry<String, Integer> entry : counter.entrySet()) {
            String row = entry.getKey();
            int count = entry.getValue();
            
            // 해당 행에서 꺼져있는 램프(0) 개수
            int zeros = 0;
            for (char c : row.toCharArray()) {
                if (c == '0') zeros++;
            }
            
            // K번 눌러서 모든 램프를 켤 수 있는 조건
            if (zeros <= K && (K - zeros) % 2 == 0) {
                ans = Math.max(ans, count);
            }
        }
        
        System.out.println(ans);
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <map>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int N, M;
    cin >> N >> M;
    
    map<string, int> counter;
    for (int i = 0; i < N; i++) {
        string row;
        cin >> row;
        counter[row]++;
    }
    
    int K;
    cin >> K;
    
    int ans = 0;
    for (auto& p : counter) {
        string row = p.first;
        int count = p.second;
        
        // 해당 행에서 꺼져있는 램프(0) 개수
        int zeros = 0;
        for (char c : row) {
            if (c == '0') zeros++;
        }
        
        // K번 눌러서 모든 램프를 켤 수 있는 조건
        if (zeros <= K && (K - zeros) % 2 == 0) {
            ans = max(ans, count);
        }
    }
    
    cout << ans << endl;
    
    return 0;
}
'''
            }
        ]
    },
    
    # 2624 - 동전 바꿔주기 (DP)
    "2624": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

# 입력
T = int(input())  # 지폐 금액
k = int(input())  # 동전 종류 수

coins = []
for _ in range(k):
    p, n = map(int, input().split())
    coins.append((p, n))

# DP: dp[i] = 금액 i를 만드는 방법의 수
dp = [0] * (T + 1)
dp[0] = 1  # 0원을 만드는 방법은 1가지 (아무것도 안 씀)

# 각 동전에 대해 처리
for p, n in coins:
    # 역순으로 순회하면서 갱신 (같은 동전 중복 사용 방지를 위해 새 배열 사용)
    new_dp = dp[:]
    for cnt in range(1, n + 1):  # 동전을 1~n개 사용
        for amount in range(cnt * p, T + 1):
            new_dp[amount] += dp[amount - cnt * p]
    dp = new_dp

print(dp[T])
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        int T = Integer.parseInt(br.readLine().trim());
        int k = Integer.parseInt(br.readLine().trim());
        
        int[][] coins = new int[k][2];
        for (int i = 0; i < k; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            coins[i][0] = Integer.parseInt(st.nextToken());
            coins[i][1] = Integer.parseInt(st.nextToken());
        }
        
        // DP: dp[i] = 금액 i를 만드는 방법의 수
        int[] dp = new int[T + 1];
        dp[0] = 1;
        
        // 각 동전에 대해 처리
        for (int i = 0; i < k; i++) {
            int p = coins[i][0];
            int n = coins[i][1];
            
            int[] newDp = dp.clone();
            for (int cnt = 1; cnt <= n; cnt++) {
                for (int amount = cnt * p; amount <= T; amount++) {
                    newDp[amount] += dp[amount - cnt * p];
                }
            }
            dp = newDp;
        }
        
        System.out.println(dp[T]);
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int T, k;
    cin >> T >> k;
    
    vector<pair<int, int>> coins(k);
    for (int i = 0; i < k; i++) {
        cin >> coins[i].first >> coins[i].second;
    }
    
    // DP: dp[i] = 금액 i를 만드는 방법의 수
    vector<int> dp(T + 1, 0);
    dp[0] = 1;
    
    // 각 동전에 대해 처리
    for (int i = 0; i < k; i++) {
        int p = coins[i].first;
        int n = coins[i].second;
        
        vector<int> newDp = dp;
        for (int cnt = 1; cnt <= n; cnt++) {
            for (int amount = cnt * p; amount <= T; amount++) {
                newDp[amount] += dp[amount - cnt * p];
            }
        }
        dp = newDp;
    }
    
    cout << dp[T] << endl;
    
    return 0;
}
'''
            }
        ]
    },
    
    # 1029 - 그림 교환 (비트마스킹 DP)
    "1029": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

N = int(input())
price = []
for i in range(N):
    price.append(input().strip())

# dp[visited][cur][last_price] = 가능 여부
# visited: 방문한 사람들의 비트마스크
# cur: 현재 그림을 가진 사람
# last_price: 마지막으로 거래된 가격 (0-9)

# 메모이제이션
memo = {}

def dfs(cur, visited, last_price):
    # 현재 상태에서 최대 몇 명이 그림을 소유할 수 있는지
    key = (cur, visited, last_price)
    if key in memo:
        return memo[key]
    
    result = 0
    for nxt in range(N):
        if visited & (1 << nxt):  # 이미 소유한 적 있음
            continue
        nxt_price = int(price[cur][nxt])
        if nxt_price >= last_price:  # 더 비싸게 팔 수 있음
            result = max(result, 1 + dfs(nxt, visited | (1 << nxt), nxt_price))
    
    memo[key] = result
    return result

# 1번 아티스트(인덱스 0)가 처음 가격 0으로 그림을 가지고 시작
ans = 1 + dfs(0, 1, 0)
print(ans)
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int N;
    static int[][] price;
    static int[][][] dp;
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        N = Integer.parseInt(br.readLine().trim());
        price = new int[N][N];
        
        for (int i = 0; i < N; i++) {
            String line = br.readLine().trim();
            for (int j = 0; j < N; j++) {
                price[i][j] = line.charAt(j) - '0';
            }
        }
        
        // dp[visited][cur][last_price]
        dp = new int[1 << N][N][10];
        for (int[][] arr2d : dp) {
            for (int[] arr1d : arr2d) {
                Arrays.fill(arr1d, -1);
            }
        }
        
        // 1번 아티스트(인덱스 0)가 처음 가격 0으로 시작
        int ans = 1 + dfs(0, 1, 0);
        System.out.println(ans);
    }
    
    static int dfs(int cur, int visited, int lastPrice) {
        if (dp[visited][cur][lastPrice] != -1) {
            return dp[visited][cur][lastPrice];
        }
        
        int result = 0;
        for (int nxt = 0; nxt < N; nxt++) {
            if ((visited & (1 << nxt)) != 0) continue;
            int nxtPrice = price[cur][nxt];
            if (nxtPrice >= lastPrice) {
                result = Math.max(result, 1 + dfs(nxt, visited | (1 << nxt), nxtPrice));
            }
        }
        
        dp[visited][cur][lastPrice] = result;
        return result;
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <cstring>
#include <algorithm>
using namespace std;

int N;
int price[15][15];
int dp[1 << 15][15][10];

int dfs(int cur, int visited, int lastPrice) {
    if (dp[visited][cur][lastPrice] != -1) {
        return dp[visited][cur][lastPrice];
    }
    
    int result = 0;
    for (int nxt = 0; nxt < N; nxt++) {
        if (visited & (1 << nxt)) continue;
        int nxtPrice = price[cur][nxt];
        if (nxtPrice >= lastPrice) {
            result = max(result, 1 + dfs(nxt, visited | (1 << nxt), nxtPrice));
        }
    }
    
    dp[visited][cur][lastPrice] = result;
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    cin >> N;
    
    for (int i = 0; i < N; i++) {
        string line;
        cin >> line;
        for (int j = 0; j < N; j++) {
            price[i][j] = line[j] - '0';
        }
    }
    
    memset(dp, -1, sizeof(dp));
    
    // 1번 아티스트(인덱스 0)가 처음 가격 0으로 시작
    int ans = 1 + dfs(0, 1, 0);
    cout << ans << endl;
    
    return 0;
}
'''
            }
        ]
    },
    
    # 3860 - 할로윈 묘지 (벨만-포드)
    "3860": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from collections import defaultdict
input = sys.stdin.readline
INF = float('inf')

def solve():
    while True:
        line = input().split()
        W, H = int(line[0]), int(line[1])
        
        if W == 0 and H == 0:
            break
        
        G = int(input())
        graves = set()
        for _ in range(G):
            x, y = map(int, input().split())
            graves.add((x, y))
        
        E = int(input())
        holes = {}  # (x1, y1) -> (x2, y2, t)
        for _ in range(E):
            x1, y1, x2, y2, t = map(int, input().split())
            holes[(x1, y1)] = (x2, y2, t)
        
        # 정점 번호 매핑
        def idx(x, y):
            return y * W + x
        
        # 간선 생성
        edges = []
        dx = [1, 0, -1, 0]
        dy = [0, 1, 0, -1]
        
        for x in range(W):
            for y in range(H):
                if (x, y) in graves:
                    continue
                if (x, y) == (W - 1, H - 1):  # 출구는 나가는 간선 없음
                    continue
                
                if (x, y) in holes:
                    # 귀신 구멍
                    x2, y2, t = holes[(x, y)]
                    edges.append((idx(x, y), idx(x2, y2), t))
                else:
                    # 일반 이동
                    for d in range(4):
                        nx, ny = x + dx[d], y + dy[d]
                        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in graves:
                            edges.append((idx(x, y), idx(nx, ny), 1))
        
        V = W * H
        dist = [INF] * V
        dist[0] = 0
        
        # 벨만-포드 알고리즘
        for i in range(V):
            updated = False
            for u, v, w in edges:
                if dist[u] != INF and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    updated = True
                    if i == V - 1:
                        # 음수 사이클 존재 - 출구에 영향 있는지 확인
                        # 한 번 더 돌려서 출구까지 영향 확인
                        pass
            if not updated:
                break
        
        # 음수 사이클 검사 (출구에 영향 주는지)
        has_negative_cycle = False
        for _ in range(V):
            for u, v, w in edges:
                if dist[u] != INF and dist[u] + w < dist[v]:
                    dist[v] = -INF
                    has_negative_cycle = True
        
        target = idx(W - 1, H - 1)
        if dist[target] == -INF:
            print("Never")
        elif dist[target] == INF:
            print("Impossible")
        else:
            print(dist[target])

solve()
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static final long INF = Long.MAX_VALUE / 2;
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();
        
        while (true) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int W = Integer.parseInt(st.nextToken());
            int H = Integer.parseInt(st.nextToken());
            
            if (W == 0 && H == 0) break;
            
            int G = Integer.parseInt(br.readLine().trim());
            Set<Integer> graves = new HashSet<>();
            for (int i = 0; i < G; i++) {
                st = new StringTokenizer(br.readLine());
                int x = Integer.parseInt(st.nextToken());
                int y = Integer.parseInt(st.nextToken());
                graves.add(y * W + x);
            }
            
            int E = Integer.parseInt(br.readLine().trim());
            Map<Integer, int[]> holes = new HashMap<>();
            for (int i = 0; i < E; i++) {
                st = new StringTokenizer(br.readLine());
                int x1 = Integer.parseInt(st.nextToken());
                int y1 = Integer.parseInt(st.nextToken());
                int x2 = Integer.parseInt(st.nextToken());
                int y2 = Integer.parseInt(st.nextToken());
                int t = Integer.parseInt(st.nextToken());
                holes.put(y1 * W + x1, new int[]{y2 * W + x2, t});
            }
            
            // 간선 생성
            List<int[]> edges = new ArrayList<>();
            int[] dx = {1, 0, -1, 0};
            int[] dy = {0, 1, 0, -1};
            
            for (int x = 0; x < W; x++) {
                for (int y = 0; y < H; y++) {
                    int u = y * W + x;
                    if (graves.contains(u)) continue;
                    if (x == W - 1 && y == H - 1) continue;
                    
                    if (holes.containsKey(u)) {
                        int[] hole = holes.get(u);
                        edges.add(new int[]{u, hole[0], hole[1]});
                    } else {
                        for (int d = 0; d < 4; d++) {
                            int nx = x + dx[d];
                            int ny = y + dy[d];
                            if (nx >= 0 && nx < W && ny >= 0 && ny < H) {
                                int v = ny * W + nx;
                                if (!graves.contains(v)) {
                                    edges.add(new int[]{u, v, 1});
                                }
                            }
                        }
                    }
                }
            }
            
            int V = W * H;
            long[] dist = new long[V];
            Arrays.fill(dist, INF);
            dist[0] = 0;
            
            // 벨만-포드
            for (int i = 0; i < V; i++) {
                for (int[] edge : edges) {
                    int u = edge[0], v = edge[1], w = edge[2];
                    if (dist[u] != INF && dist[u] + w < dist[v]) {
                        dist[v] = dist[u] + w;
                    }
                }
            }
            
            // 음수 사이클 검사
            for (int i = 0; i < V; i++) {
                for (int[] edge : edges) {
                    int u = edge[0], v = edge[1], w = edge[2];
                    if (dist[u] != INF && dist[u] + w < dist[v]) {
                        dist[v] = -INF;
                    }
                }
            }
            
            int target = (H - 1) * W + (W - 1);
            if (dist[target] == -INF) {
                sb.append("Never\\n");
            } else if (dist[target] == INF) {
                sb.append("Impossible\\n");
            } else {
                sb.append(dist[target]).append("\\n");
            }
        }
        
        System.out.print(sb);
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <set>
#include <map>
#include <climits>
using namespace std;

const long long INF = LLONG_MAX / 2;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int W, H;
    while (cin >> W >> H) {
        if (W == 0 && H == 0) break;
        
        int G;
        cin >> G;
        set<int> graves;
        for (int i = 0; i < G; i++) {
            int x, y;
            cin >> x >> y;
            graves.insert(y * W + x);
        }
        
        int E;
        cin >> E;
        map<int, pair<int, int>> holes;
        for (int i = 0; i < E; i++) {
            int x1, y1, x2, y2, t;
            cin >> x1 >> y1 >> x2 >> y2 >> t;
            holes[y1 * W + x1] = {y2 * W + x2, t};
        }
        
        // 간선 생성
        vector<tuple<int, int, int>> edges;
        int dx[] = {1, 0, -1, 0};
        int dy[] = {0, 1, 0, -1};
        
        for (int x = 0; x < W; x++) {
            for (int y = 0; y < H; y++) {
                int u = y * W + x;
                if (graves.count(u)) continue;
                if (x == W - 1 && y == H - 1) continue;
                
                if (holes.count(u)) {
                    auto [v, t] = holes[u];
                    edges.push_back({u, v, t});
                } else {
                    for (int d = 0; d < 4; d++) {
                        int nx = x + dx[d];
                        int ny = y + dy[d];
                        if (nx >= 0 && nx < W && ny >= 0 && ny < H) {
                            int v = ny * W + nx;
                            if (!graves.count(v)) {
                                edges.push_back({u, v, 1});
                            }
                        }
                    }
                }
            }
        }
        
        int V = W * H;
        vector<long long> dist(V, INF);
        dist[0] = 0;
        
        // 벨만-포드
        for (int i = 0; i < V; i++) {
            for (auto& [u, v, w] : edges) {
                if (dist[u] != INF && dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                }
            }
        }
        
        // 음수 사이클 검사
        for (int i = 0; i < V; i++) {
            for (auto& [u, v, w] : edges) {
                if (dist[u] != INF && dist[u] + w < dist[v]) {
                    dist[v] = -INF;
                }
            }
        }
        
        int target = (H - 1) * W + (W - 1);
        if (dist[target] == -INF) {
            cout << "Never" << endl;
        } else if (dist[target] == INF) {
            cout << "Impossible" << endl;
        } else {
            cout << dist[target] << endl;
        }
    }
    
    return 0;
}
'''
            }
        ]
    },
    
    # 2258 - 정육점 (그리디, 정렬)
    "2258": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

N, M = map(int, input().split())
meat = []
for _ in range(N):
    w, p = map(int, input().split())
    meat.append((p, w))

# 가격 오름차순, 같은 가격이면 무게 내림차순 정렬
meat.sort(key=lambda x: (x[0], -x[1]))

ans = float('inf')
total_weight = 0
total_price = 0
prev_price = -1

for price, weight in meat:
    if price == prev_price:
        # 같은 가격이면 가격 누적
        total_price += price
    else:
        # 다른 가격이면 해당 가격만 지불 (이전 것들은 공짜)
        total_price = price
    
    total_weight += weight
    prev_price = price
    
    if total_weight >= M:
        ans = min(ans, total_price)

if ans == float('inf'):
    print(-1)
else:
    print(ans)
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        
        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());
        
        int[][] meat = new int[N][2];
        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            meat[i][1] = Integer.parseInt(st.nextToken()); // weight
            meat[i][0] = Integer.parseInt(st.nextToken()); // price
        }
        
        // 가격 오름차순, 같은 가격이면 무게 내림차순 정렬
        Arrays.sort(meat, (a, b) -> {
            if (a[0] != b[0]) return a[0] - b[0];
            return b[1] - a[1];
        });
        
        long ans = Long.MAX_VALUE;
        long totalWeight = 0;
        long totalPrice = 0;
        int prevPrice = -1;
        
        for (int[] m : meat) {
            int price = m[0];
            int weight = m[1];
            
            if (price == prevPrice) {
                totalPrice += price;
            } else {
                totalPrice = price;
            }
            
            totalWeight += weight;
            prevPrice = price;
            
            if (totalWeight >= M) {
                ans = Math.min(ans, totalPrice);
            }
        }
        
        if (ans == Long.MAX_VALUE) {
            System.out.println(-1);
        } else {
            System.out.println(ans);
        }
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int N, M;
    cin >> N >> M;
    
    vector<pair<int, int>> meat(N); // (price, weight)
    for (int i = 0; i < N; i++) {
        int w, p;
        cin >> w >> p;
        meat[i] = {p, w};
    }
    
    // 가격 오름차순, 같은 가격이면 무게 내림차순 정렬
    sort(meat.begin(), meat.end(), [](auto& a, auto& b) {
        if (a.first != b.first) return a.first < b.first;
        return a.second > b.second;
    });
    
    long long ans = LLONG_MAX;
    long long totalWeight = 0;
    long long totalPrice = 0;
    int prevPrice = -1;
    
    for (auto& m : meat) {
        int price = m.first;
        int weight = m.second;
        
        if (price == prevPrice) {
            totalPrice += price;
        } else {
            totalPrice = price;
        }
        
        totalWeight += weight;
        prevPrice = price;
        
        if (totalWeight >= M) {
            ans = min(ans, totalPrice);
        }
    }
    
    if (ans == LLONG_MAX) {
        cout << -1 << endl;
    } else {
        cout << ans << endl;
    }
    
    return 0;
}
'''
            }
        ]
    },
    
    # 19940 - 피자 오븐 (그리디)
    "19940": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    N = int(input())
    
    # 60분 버튼 횟수
    addh = N // 60
    remain = N % 60
    
    # 40분 이상이면 60분 한 번 더 누르고 -10분으로 조절하는 게 유리할 수 있음
    # 사전순으로 ADDH가 작은 것이 우선
    
    results = []
    
    # 경우 1: addh번의 ADDH 사용
    if addh >= 0:
        r = remain
        addt = r // 10
        r2 = r % 10
        
        # r2를 처리: +1로 가거나 +10 -1로 가거나
        if r2 <= 5:
            addo = r2
            mino = 0
            mint = 0
        else:
            addt += 1
            mint = 0
            addo = 0
            mino = 10 - r2
        
        results.append((addh, addt, mint, addo, mino))
    
    # 경우 2: (addh + 1)번의 ADDH 사용하고 -10분으로 조절
    if addh >= 0:
        r = 60 - remain  # 60 - remain = 60에서 빼야 할 양
        mint2 = r // 10
        r2 = r % 10
        
        if r2 <= 5:
            mino2 = r2
            addo2 = 0
            addt2 = 0
        else:
            mint2 += 1
            addo2 = 0
            mino2 = 0
            addo2 = 10 - r2
        
        results.append((addh + 1, 0, mint2, addo2, mino2))
    
    # 버튼 총 횟수가 최소인 것 중 사전순으로 가장 작은 것 선택
    best = None
    best_count = float('inf')
    
    for res in results:
        cnt = sum(res)
        if cnt < best_count or (cnt == best_count and res < best):
            best_count = cnt
            best = res
    
    print(*best)
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();
        
        int T = Integer.parseInt(br.readLine().trim());
        
        while (T-- > 0) {
            int N = Integer.parseInt(br.readLine().trim());
            
            int addh = N / 60;
            int remain = N % 60;
            
            int[] best = null;
            int bestCount = Integer.MAX_VALUE;
            
            // 경우 1: addh번의 ADDH 사용
            {
                int r = remain;
                int addt = r / 10;
                int r2 = r % 10;
                int mint, addo, mino;
                
                if (r2 <= 5) {
                    addo = r2;
                    mino = 0;
                    mint = 0;
                } else {
                    addt++;
                    mint = 0;
                    addo = 0;
                    mino = 10 - r2;
                }
                
                int[] res = {addh, addt, mint, addo, mino};
                int cnt = addh + addt + mint + addo + mino;
                
                if (cnt < bestCount || (cnt == bestCount && compare(res, best) < 0)) {
                    bestCount = cnt;
                    best = res;
                }
            }
            
            // 경우 2: (addh + 1)번의 ADDH 사용
            {
                int r = 60 - remain;
                int mint2 = r / 10;
                int r2 = r % 10;
                int addo2, mino2, addt2 = 0;
                
                if (r2 <= 5) {
                    mino2 = r2;
                    addo2 = 0;
                } else {
                    mint2++;
                    mino2 = 0;
                    addo2 = 10 - r2;
                }
                
                int[] res = {addh + 1, addt2, mint2, addo2, mino2};
                int cnt = (addh + 1) + addt2 + mint2 + addo2 + mino2;
                
                if (cnt < bestCount || (cnt == bestCount && compare(res, best) < 0)) {
                    bestCount = cnt;
                    best = res;
                }
            }
            
            for (int i = 0; i < 5; i++) {
                sb.append(best[i]);
                if (i < 4) sb.append(" ");
            }
            sb.append("\\n");
        }
        
        System.out.print(sb);
    }
    
    static int compare(int[] a, int[] b) {
        if (b == null) return -1;
        for (int i = 0; i < 5; i++) {
            if (a[i] != b[i]) return a[i] - b[i];
        }
        return 0;
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int T;
    cin >> T;
    
    while (T--) {
        int N;
        cin >> N;
        
        int addh = N / 60;
        int remain = N % 60;
        
        vector<int> best;
        int bestCount = INT_MAX;
        
        // 경우 1: addh번의 ADDH 사용
        {
            int r = remain;
            int addt = r / 10;
            int r2 = r % 10;
            int mint, addo, mino;
            
            if (r2 <= 5) {
                addo = r2;
                mino = 0;
                mint = 0;
            } else {
                addt++;
                mint = 0;
                addo = 0;
                mino = 10 - r2;
            }
            
            vector<int> res = {addh, addt, mint, addo, mino};
            int cnt = addh + addt + mint + addo + mino;
            
            if (cnt < bestCount || (cnt == bestCount && res < best)) {
                bestCount = cnt;
                best = res;
            }
        }
        
        // 경우 2: (addh + 1)번의 ADDH 사용
        {
            int r = 60 - remain;
            int mint2 = r / 10;
            int r2 = r % 10;
            int addo2, mino2, addt2 = 0;
            
            if (r2 <= 5) {
                mino2 = r2;
                addo2 = 0;
            } else {
                mint2++;
                mino2 = 0;
                addo2 = 10 - r2;
            }
            
            vector<int> res = {addh + 1, addt2, mint2, addo2, mino2};
            int cnt = (addh + 1) + addt2 + mint2 + addo2 + mino2;
            
            if (cnt < bestCount || (cnt == bestCount && res < best)) {
                bestCount = cnt;
                best = res;
            }
        }
        
        for (int i = 0; i < 5; i++) {
            cout << best[i];
            if (i < 4) cout << " ";
        }
        cout << "\\n";
    }
    
    return 0;
}
'''
            }
        ]
    },
    
    # 2957 - 이진 탐색 트리 (Map/Set 활용)
    "2957": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from bisect import bisect_left, insort
input = sys.stdin.readline

N = int(input())

# 삽입된 값과 그 깊이를 저장
# sortedlist: 정렬된 삽입 값들
# depth: 각 값의 깊이
sorted_vals = []
depth = {}

total = 0
result = []

for _ in range(N):
    x = int(input())
    
    if not sorted_vals:
        # 첫 번째 노드는 루트
        depth[x] = 0
    else:
        # x가 삽입될 위치 찾기
        pos = bisect_left(sorted_vals, x)
        
        # x보다 작은 값 중 가장 큰 값과, x보다 큰 값 중 가장 작은 값 찾기
        d = 0
        if pos > 0:
            # x보다 작은 값 중 가장 큰 값
            smaller = sorted_vals[pos - 1]
            d = max(d, depth[smaller] + 1)
        if pos < len(sorted_vals):
            # x보다 큰 값 중 가장 작은 값
            larger = sorted_vals[pos]
            d = max(d, depth[larger] + 1)
        
        depth[x] = d
        total += d
    
    insort(sorted_vals, x)
    result.append(total)

print('\\n'.join(map(str, result)))
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();
        
        int N = Integer.parseInt(br.readLine().trim());
        
        // TreeMap: 값 -> 깊이
        TreeMap<Integer, Integer> tree = new TreeMap<>();
        
        long total = 0;
        
        for (int i = 0; i < N; i++) {
            int x = Integer.parseInt(br.readLine().trim());
            
            if (tree.isEmpty()) {
                tree.put(x, 0);
            } else {
                int d = 0;
                
                // x보다 작은 값 중 가장 큰 값
                Integer lower = tree.lowerKey(x);
                if (lower != null) {
                    d = Math.max(d, tree.get(lower) + 1);
                }
                
                // x보다 큰 값 중 가장 작은 값
                Integer higher = tree.higherKey(x);
                if (higher != null) {
                    d = Math.max(d, tree.get(higher) + 1);
                }
                
                tree.put(x, d);
                total += d;
            }
            
            sb.append(total).append("\\n");
        }
        
        System.out.print(sb);
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int N;
    cin >> N;
    
    // map: 값 -> 깊이
    map<int, int> tree;
    
    long long total = 0;
    
    for (int i = 0; i < N; i++) {
        int x;
        cin >> x;
        
        if (tree.empty()) {
            tree[x] = 0;
        } else {
            int d = 0;
            
            auto it = tree.lower_bound(x);
            
            // x보다 큰 값 중 가장 작은 값
            if (it != tree.end()) {
                d = max(d, it->second + 1);
            }
            
            // x보다 작은 값 중 가장 큰 값
            if (it != tree.begin()) {
                --it;
                d = max(d, it->second + 1);
            }
            
            tree[x] = d;
            total += d;
        }
        
        cout << total << "\\n";
    }
    
    return 0;
}
'''
            }
        ]
    },
    
    # 10836 - 여왕벌 (시뮬레이션 최적화)
    "10836": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

M, N = map(int, input().split())

# 왼쪽 열과 위쪽 행의 성장값 누적
# 2*M-1 칸: 왼쪽 열(아래서 위로) + 위쪽 행(왼쪽에서 오른쪽)
growth = [0] * (2 * M - 1)

for _ in range(N):
    counts = list(map(int, input().split()))
    # counts[0]: 0 성장 개수, counts[1]: 1 성장 개수, counts[2]: 2 성장 개수
    
    idx = 0
    for g in range(3):
        for _ in range(counts[g]):
            growth[idx] += g
            idx += 1

# 결과 출력
# 첫 번째 행: 위쪽 행 값들 (인덱스 M-1 ~ 2*M-2)
# 나머지 행: 왼쪽 열 값 + 위쪽 행 값들의 최댓값
result = []

for i in range(M):
    row = []
    for j in range(M):
        if i == 0:
            # 첫 번째 행
            row.append(1 + growth[M - 1 + j])
        elif j == 0:
            # 첫 번째 열
            row.append(1 + growth[M - 1 - i])
        else:
            # 나머지 칸: 위쪽 행의 값과 동일 (왼쪽, 왼쪽위, 위 중 최댓값 = 위)
            row.append(1 + growth[M - 1 + j])
    result.append(' '.join(map(str, row)))

print('\\n'.join(result))
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        
        int M = Integer.parseInt(st.nextToken());
        int N = Integer.parseInt(st.nextToken());
        
        // 왼쪽 열과 위쪽 행의 성장값 누적
        int[] growth = new int[2 * M - 1];
        
        for (int day = 0; day < N; day++) {
            st = new StringTokenizer(br.readLine());
            int[] counts = new int[3];
            for (int i = 0; i < 3; i++) {
                counts[i] = Integer.parseInt(st.nextToken());
            }
            
            int idx = 0;
            for (int g = 0; g < 3; g++) {
                for (int c = 0; c < counts[g]; c++) {
                    growth[idx++] += g;
                }
            }
        }
        
        // 결과 출력
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < M; i++) {
            for (int j = 0; j < M; j++) {
                if (j > 0) sb.append(" ");
                if (i == 0) {
                    sb.append(1 + growth[M - 1 + j]);
                } else if (j == 0) {
                    sb.append(1 + growth[M - 1 - i]);
                } else {
                    sb.append(1 + growth[M - 1 + j]);
                }
            }
            sb.append("\\n");
        }
        
        System.out.print(sb);
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int M, N;
    cin >> M >> N;
    
    // 왼쪽 열과 위쪽 행의 성장값 누적
    vector<int> growth(2 * M - 1, 0);
    
    for (int day = 0; day < N; day++) {
        int counts[3];
        for (int i = 0; i < 3; i++) {
            cin >> counts[i];
        }
        
        int idx = 0;
        for (int g = 0; g < 3; g++) {
            for (int c = 0; c < counts[g]; c++) {
                growth[idx++] += g;
            }
        }
    }
    
    // 결과 출력
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < M; j++) {
            if (j > 0) cout << " ";
            if (i == 0) {
                cout << 1 + growth[M - 1 + j];
            } else if (j == 0) {
                cout << 1 + growth[M - 1 - i];
            } else {
                cout << 1 + growth[M - 1 + j];
            }
        }
        cout << "\\n";
    }
    
    return 0;
}
'''
            }
        ]
    },
    
    # 15711 - 환상의 짝꿍 (소수 판별, 골드바흐 추측)
    "15711": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

# 에라토스테네스의 체로 소수 생성
# 합이 최대 2*10^12이므로, 소수 판별에는 sqrt(2*10^12) ≈ 1.4*10^6까지 필요
MAX = 2000001
is_prime = [True] * MAX
is_prime[0] = is_prime[1] = False

for i in range(2, int(MAX**0.5) + 1):
    if is_prime[i]:
        for j in range(i*i, MAX, i):
            is_prime[j] = False

# 소수 리스트
primes = [i for i in range(MAX) if is_prime[i]]

def check_prime(n):
    """n이 소수인지 판별 (밀러-라빈 또는 직접 판별)"""
    if n < MAX:
        return is_prime[n]
    # n이 큰 경우 직접 나눠봄
    if n % 2 == 0:
        return False
    for p in primes:
        if p * p > n:
            break
        if n % p == 0:
            return False
    return True

T = int(input())
results = []

for _ in range(T):
    A, B = map(int, input().split())
    S = A + B
    
    if S < 4:
        # 3 이하는 두 소수의 합으로 표현 불가
        results.append("NO")
    elif S % 2 == 0:
        # 짝수는 골드바흐 추측에 의해 항상 가능 (4 이상)
        results.append("YES")
    else:
        # 홀수인 경우: 2 + (S-2) 형태만 가능
        # S-2가 소수인지 확인
        if check_prime(S - 2):
            results.append("YES")
        else:
            results.append("NO")

print('\\n'.join(results))
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static final int MAX = 2000001;
    static boolean[] isPrime = new boolean[MAX];
    static int[] primes;
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();
        
        // 에라토스테네스의 체
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;
        
        for (int i = 2; i * i < MAX; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j < MAX; j += i) {
                    isPrime[j] = false;
                }
            }
        }
        
        // 소수 리스트
        List<Integer> primeList = new ArrayList<>();
        for (int i = 2; i < MAX; i++) {
            if (isPrime[i]) primeList.add(i);
        }
        primes = primeList.stream().mapToInt(i -> i).toArray();
        
        int T = Integer.parseInt(br.readLine().trim());
        
        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long A = Long.parseLong(st.nextToken());
            long B = Long.parseLong(st.nextToken());
            long S = A + B;
            
            if (S < 4) {
                sb.append("NO\\n");
            } else if (S % 2 == 0) {
                sb.append("YES\\n");
            } else {
                if (checkPrime(S - 2)) {
                    sb.append("YES\\n");
                } else {
                    sb.append("NO\\n");
                }
            }
        }
        
        System.out.print(sb);
    }
    
    static boolean checkPrime(long n) {
        if (n < MAX) {
            return isPrime[(int)n];
        }
        if (n % 2 == 0) return false;
        for (int p : primes) {
            if ((long)p * p > n) break;
            if (n % p == 0) return false;
        }
        return true;
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <cstring>
using namespace std;

const int MAX = 2000001;
bool isPrime[MAX];
vector<int> primes;

bool checkPrime(long long n) {
    if (n < MAX) {
        return isPrime[n];
    }
    if (n % 2 == 0) return false;
    for (int p : primes) {
        if ((long long)p * p > n) break;
        if (n % p == 0) return false;
    }
    return true;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    // 에라토스테네스의 체
    memset(isPrime, true, sizeof(isPrime));
    isPrime[0] = isPrime[1] = false;
    
    for (int i = 2; i * i < MAX; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j < MAX; j += i) {
                isPrime[j] = false;
            }
        }
    }
    
    // 소수 리스트
    for (int i = 2; i < MAX; i++) {
        if (isPrime[i]) primes.push_back(i);
    }
    
    int T;
    cin >> T;
    
    while (T--) {
        long long A, B;
        cin >> A >> B;
        long long S = A + B;
        
        if (S < 4) {
            cout << "NO\\n";
        } else if (S % 2 == 0) {
            cout << "YES\\n";
        } else {
            if (checkPrime(S - 2)) {
                cout << "YES\\n";
            } else {
                cout << "NO\\n";
            }
        }
    }
    
    return 0;
}
'''
            }
        ]
    }
}

# baek_medium.json에 추가
import json

with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'r') as f:
    data = json.load(f)

for problem_id, solution_data in solutions.items():
    data[problem_id] = solution_data

with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {len(solutions)} solutions to baek_medium.json")
print(f"Total problems in baek_medium.json: {len(data)}")
