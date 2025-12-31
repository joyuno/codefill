#!/usr/bin/env python3
"""
배치 8: 인덱스 [1334, 1335, 1340, 1345, 1350, 1357, 1368, 1371, 1375, 1378]에 대한 솔루션 생성
"""
import json

# 솔루션 정의
solutions = {
    # Index 1334: 버스 노선 (baekjoon_10165)
    "1334": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    # N: 버스 정류소 개수, M: 버스 노선 수
    N = int(input())
    M = int(input())

    routes = []
    for i in range(M):
        a, b = map(int, input().split())
        if a <= b:
            # 일반 구간 [a, b]
            routes.append((a, b, i + 1, 0))
        else:
            # 순환 구간 [a, b+N] (0을 넘어가는 경우)
            routes.append((a, b + N, i + 1, 1))

    # 시작점 기준 오름차순, 끝점 기준 내림차순 정렬
    routes.sort(key=lambda x: (x[0], -x[1]))

    removed = set()

    # 일반 구간 처리 (순환하지 않는 구간)
    max_end = -1
    for a, b, idx, is_wrap in routes:
        if is_wrap == 0:  # 순환하지 않는 구간만
            if b <= max_end:
                removed.add(idx)
            else:
                max_end = b

    # 순환 구간 처리
    wrap_routes = [(a, b, idx) for a, b, idx, is_wrap in routes if is_wrap == 1]
    if wrap_routes:
        # 순환 구간 중 가장 큰 범위를 찾음
        max_wrap_end = max(r[1] for r in wrap_routes)

        # 순환 구간끼리 비교
        max_end = -1
        for a, b, idx in wrap_routes:
            if b <= max_end:
                removed.add(idx)
            else:
                max_end = b

        # 순환 구간이 일반 구간을 포함하는지 확인
        for a, b, idx, is_wrap in routes:
            if is_wrap == 0:  # 일반 구간
                for wa, wb, widx in wrap_routes:
                    if widx not in removed:
                        # 순환 구간 [wa, wb]가 일반 구간 [a, b]를 포함하는지
                        if a >= wa or b <= wb - N:
                            removed.add(idx)
                            break

    # 결과 출력
    result = [i for i in range(1, M + 1) if i not in removed]
    print(' '.join(map(str, result)))

solve()
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());
        int M = Integer.parseInt(br.readLine().trim());

        // 노선 정보: {시작, 끝, 인덱스, 순환여부}
        int[][] routes = new int[M][4];
        for (int i = 0; i < M; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            if (a <= b) {
                routes[i] = new int[]{a, b, i + 1, 0};
            } else {
                routes[i] = new int[]{a, b + N, i + 1, 1};
            }
        }

        // 시작점 오름차순, 끝점 내림차순 정렬
        Arrays.sort(routes, (x, y) -> {
            if (x[0] != y[0]) return x[0] - y[0];
            return y[1] - x[1];
        });

        Set<Integer> removed = new HashSet<>();

        // 일반 구간 처리
        int maxEnd = -1;
        for (int[] route : routes) {
            if (route[3] == 0) {
                if (route[1] <= maxEnd) {
                    removed.add(route[2]);
                } else {
                    maxEnd = route[1];
                }
            }
        }

        // 순환 구간 수집
        List<int[]> wrapRoutes = new ArrayList<>();
        for (int[] route : routes) {
            if (route[3] == 1) {
                wrapRoutes.add(route);
            }
        }

        if (!wrapRoutes.isEmpty()) {
            // 순환 구간끼리 비교
            maxEnd = -1;
            for (int[] wr : wrapRoutes) {
                if (wr[1] <= maxEnd) {
                    removed.add(wr[2]);
                } else {
                    maxEnd = wr[1];
                }
            }

            // 순환 구간이 일반 구간을 포함하는지 확인
            for (int[] route : routes) {
                if (route[3] == 0 && !removed.contains(route[2])) {
                    for (int[] wr : wrapRoutes) {
                        if (!removed.contains(wr[2])) {
                            if (route[0] >= wr[0] || route[1] <= wr[1] - N) {
                                removed.add(route[2]);
                                break;
                            }
                        }
                    }
                }
            }
        }

        // 결과 출력
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= M; i++) {
            if (!removed.contains(i)) {
                if (sb.length() > 0) sb.append(" ");
                sb.append(i);
            }
        }
        System.out.println(sb);
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long N;
    int M;
    cin >> N >> M;

    // 노선 정보: {시작, 끝, 인덱스, 순환여부}
    vector<tuple<long long, long long, int, int>> routes(M);

    for (int i = 0; i < M; i++) {
        long long a, b;
        cin >> a >> b;
        if (a <= b) {
            routes[i] = {a, b, i + 1, 0};
        } else {
            routes[i] = {a, b + N, i + 1, 1};
        }
    }

    // 시작점 오름차순, 끝점 내림차순 정렬
    sort(routes.begin(), routes.end(), [](const auto& x, const auto& y) {
        if (get<0>(x) != get<0>(y)) return get<0>(x) < get<0>(y);
        return get<1>(x) > get<1>(y);
    });

    set<int> removed;

    // 일반 구간 처리
    long long maxEnd = -1;
    for (auto& [a, b, idx, wrap] : routes) {
        if (wrap == 0) {
            if (b <= maxEnd) {
                removed.insert(idx);
            } else {
                maxEnd = b;
            }
        }
    }

    // 순환 구간 수집
    vector<tuple<long long, long long, int>> wrapRoutes;
    for (auto& [a, b, idx, wrap] : routes) {
        if (wrap == 1) {
            wrapRoutes.push_back({a, b, idx});
        }
    }

    if (!wrapRoutes.empty()) {
        // 순환 구간끼리 비교
        maxEnd = -1;
        for (auto& [a, b, idx] : wrapRoutes) {
            if (b <= maxEnd) {
                removed.insert(idx);
            } else {
                maxEnd = b;
            }
        }

        // 순환 구간이 일반 구간을 포함하는지 확인
        for (auto& [a, b, idx, wrap] : routes) {
            if (wrap == 0 && removed.find(idx) == removed.end()) {
                for (auto& [wa, wb, widx] : wrapRoutes) {
                    if (removed.find(widx) == removed.end()) {
                        if (a >= wa || b <= wb - N) {
                            removed.insert(idx);
                            break;
                        }
                    }
                }
            }
        }
    }

    // 결과 출력
    bool first = true;
    for (int i = 1; i <= M; i++) {
        if (removed.find(i) == removed.end()) {
            if (!first) cout << " ";
            cout << i;
            first = false;
        }
    }
    cout << "\\n";

    return 0;
}
'''
            }
        ]
    },

    # Index 1335: 모래성 (baekjoon_10711)
    "1335": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from collections import deque
input = sys.stdin.readline

def solve():
    H, W = map(int, input().split())
    grid = []
    for _ in range(H):
        grid.append(list(input().strip()))

    # 8방향 이동
    dx = [-1, -1, -1, 0, 0, 1, 1, 1]
    dy = [-1, 0, 1, -1, 1, -1, 0, 1]

    # 초기 상태에서 무너질 모래성을 큐에 추가
    queue = deque()

    # 각 모래성 주변의 빈 칸 수 계산
    empty_count = [[0] * W for _ in range(H)]

    for i in range(H):
        for j in range(W):
            if grid[i][j] != '.':
                count = 0
                for d in range(8):
                    ni, nj = i + dx[d], j + dy[d]
                    if 0 <= ni < H and 0 <= nj < W:
                        if grid[ni][nj] == '.':
                            count += 1
                    else:
                        count += 1  # 범위 밖은 빈 칸으로 취급
                empty_count[i][j] = count

                # 튼튼함보다 빈 칸이 많거나 같으면 무너짐
                if count >= int(grid[i][j]):
                    queue.append((i, j, 1))  # 1번째 파도에 무너짐
                    grid[i][j] = '.'  # 무너진 것으로 표시

    max_wave = 0

    while queue:
        x, y, wave = queue.popleft()
        max_wave = max(max_wave, wave)

        # 주변 모래성 확인
        for d in range(8):
            nx, ny = x + dx[d], y + dy[d]
            if 0 <= nx < H and 0 <= ny < W and grid[nx][ny] != '.':
                empty_count[nx][ny] += 1
                if empty_count[nx][ny] >= int(grid[nx][ny]):
                    queue.append((nx, ny, wave + 1))
                    grid[nx][ny] = '.'

    print(max_wave)

solve()
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int[] dx = {-1, -1, -1, 0, 0, 1, 1, 1};
    static int[] dy = {-1, 0, 1, -1, 1, -1, 0, 1};

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int H = Integer.parseInt(st.nextToken());
        int W = Integer.parseInt(st.nextToken());

        char[][] grid = new char[H][W];
        for (int i = 0; i < H; i++) {
            grid[i] = br.readLine().toCharArray();
        }

        // 각 모래성 주변의 빈 칸 수
        int[][] emptyCount = new int[H][W];
        Queue<int[]> queue = new LinkedList<>();

        for (int i = 0; i < H; i++) {
            for (int j = 0; j < W; j++) {
                if (grid[i][j] != '.') {
                    int count = 0;
                    for (int d = 0; d < 8; d++) {
                        int ni = i + dx[d];
                        int nj = j + dy[d];
                        if (ni >= 0 && ni < H && nj >= 0 && nj < W) {
                            if (grid[ni][nj] == '.') count++;
                        } else {
                            count++;
                        }
                    }
                    emptyCount[i][j] = count;

                    // 튼튼함보다 빈 칸이 많거나 같으면 무너짐
                    if (count >= grid[i][j] - '0') {
                        queue.offer(new int[]{i, j, 1});
                        grid[i][j] = '.';
                    }
                }
            }
        }

        int maxWave = 0;

        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            int x = cur[0], y = cur[1], wave = cur[2];
            maxWave = Math.max(maxWave, wave);

            for (int d = 0; d < 8; d++) {
                int nx = x + dx[d];
                int ny = y + dy[d];
                if (nx >= 0 && nx < H && ny >= 0 && ny < W && grid[nx][ny] != '.') {
                    emptyCount[nx][ny]++;
                    if (emptyCount[nx][ny] >= grid[nx][ny] - '0') {
                        queue.offer(new int[]{nx, ny, wave + 1});
                        grid[nx][ny] = '.';
                    }
                }
            }
        }

        System.out.println(maxWave);
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <queue>
#include <cstring>
using namespace std;

int dx[] = {-1, -1, -1, 0, 0, 1, 1, 1};
int dy[] = {-1, 0, 1, -1, 1, -1, 0, 1};

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int H, W;
    cin >> H >> W;

    char grid[1001][1001];
    int emptyCount[1001][1001];
    memset(emptyCount, 0, sizeof(emptyCount));

    for (int i = 0; i < H; i++) {
        cin >> grid[i];
    }

    // 무너질 모래성을 큐에 추가
    queue<tuple<int, int, int>> q;

    for (int i = 0; i < H; i++) {
        for (int j = 0; j < W; j++) {
            if (grid[i][j] != '.') {
                int count = 0;
                for (int d = 0; d < 8; d++) {
                    int ni = i + dx[d];
                    int nj = j + dy[d];
                    if (ni >= 0 && ni < H && nj >= 0 && nj < W) {
                        if (grid[ni][nj] == '.') count++;
                    } else {
                        count++;
                    }
                }
                emptyCount[i][j] = count;

                if (count >= grid[i][j] - '0') {
                    q.push({i, j, 1});
                    grid[i][j] = '.';
                }
            }
        }
    }

    int maxWave = 0;

    while (!q.empty()) {
        auto [x, y, wave] = q.front();
        q.pop();
        maxWave = max(maxWave, wave);

        for (int d = 0; d < 8; d++) {
            int nx = x + dx[d];
            int ny = y + dy[d];
            if (nx >= 0 && nx < H && ny >= 0 && ny < W && grid[nx][ny] != '.') {
                emptyCount[nx][ny]++;
                if (emptyCount[nx][ny] >= grid[nx][ny] - '0') {
                    q.push({nx, ny, wave + 1});
                    grid[nx][ny] = '.';
                }
            }
        }
    }

    cout << maxWave << "\\n";

    return 0;
}
'''
            }
        ]
    },

    # Index 1340: 로고 (baekjoon_3108)
    "1340": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline
sys.setrecursionlimit(10000)

def find(parent, x):
    if parent[x] != x:
        parent[x] = find(parent, parent[x])
    return parent[x]

def union(parent, rank, a, b):
    a = find(parent, a)
    b = find(parent, b)
    if a != b:
        if rank[a] < rank[b]:
            a, b = b, a
        parent[b] = a
        if rank[a] == rank[b]:
            rank[a] += 1

def intersect(r1, r2):
    # 두 직사각형이 교차하거나 한 변을 공유하는지 확인
    x1, y1, x2, y2 = r1
    x3, y3, x4, y4 = r2

    # 완전히 분리된 경우
    if x2 < x3 or x4 < x1 or y2 < y3 or y4 < y1:
        return False

    # 하나가 다른 하나 안에 완전히 포함된 경우
    if x1 < x3 and x4 < x2 and y1 < y3 and y4 < y2:
        return False
    if x3 < x1 and x2 < x4 and y3 < y1 and y2 < y4:
        return False

    return True

def solve():
    N = int(input())
    rects = []
    for _ in range(N):
        x1, y1, x2, y2 = map(int, input().split())
        rects.append((x1, y1, x2, y2))

    # 원점 (0,0)에 대한 직사각형 추가 (거북이 시작점)
    # 시작점도 하나의 직사각형으로 취급 (크기 0)
    rects.append((0, 0, 0, 0))

    n = len(rects)
    parent = list(range(n))
    rank = [0] * n

    # 교차하는 직사각형들을 같은 집합으로 합침
    for i in range(n):
        for j in range(i + 1, n):
            if intersect(rects[i], rects[j]):
                union(parent, rank, i, j)

    # 서로 다른 연결 요소의 개수
    components = len(set(find(parent, i) for i in range(n)))

    # PU 명령 횟수 = 연결 요소 개수 - 1
    print(components - 1)

solve()
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int[] parent, rank_;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        int[][] rects = new int[N + 1][4];
        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            rects[i][0] = Integer.parseInt(st.nextToken());
            rects[i][1] = Integer.parseInt(st.nextToken());
            rects[i][2] = Integer.parseInt(st.nextToken());
            rects[i][3] = Integer.parseInt(st.nextToken());
        }
        // 원점 직사각형 추가
        rects[N] = new int[]{0, 0, 0, 0};

        int n = N + 1;
        parent = new int[n];
        rank_ = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            rank_[i] = 0;
        }

        // 교차하는 직사각형들을 같은 집합으로 합침
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (intersect(rects[i], rects[j])) {
                    union(i, j);
                }
            }
        }

        // 서로 다른 연결 요소의 개수
        Set<Integer> components = new HashSet<>();
        for (int i = 0; i < n; i++) {
            components.add(find(i));
        }

        // PU 명령 횟수 = 연결 요소 개수 - 1
        System.out.println(components.size() - 1);
    }

    static int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]);
        }
        return parent[x];
    }

    static void union(int a, int b) {
        a = find(a);
        b = find(b);
        if (a != b) {
            if (rank_[a] < rank_[b]) {
                int temp = a; a = b; b = temp;
            }
            parent[b] = a;
            if (rank_[a] == rank_[b]) {
                rank_[a]++;
            }
        }
    }

    static boolean intersect(int[] r1, int[] r2) {
        int x1 = r1[0], y1 = r1[1], x2 = r1[2], y2 = r1[3];
        int x3 = r2[0], y3 = r2[1], x4 = r2[2], y4 = r2[3];

        // 완전히 분리된 경우
        if (x2 < x3 || x4 < x1 || y2 < y3 || y4 < y1) {
            return false;
        }

        // 하나가 다른 하나 안에 완전히 포함된 경우
        if (x1 < x3 && x4 < x2 && y1 < y3 && y4 < y2) {
            return false;
        }
        if (x3 < x1 && x2 < x4 && y3 < y1 && y2 < y4) {
            return false;
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
#include <set>
using namespace std;

int parent[1001], rank_[1001];

int find(int x) {
    if (parent[x] != x) {
        parent[x] = find(parent[x]);
    }
    return parent[x];
}

void unite(int a, int b) {
    a = find(a);
    b = find(b);
    if (a != b) {
        if (rank_[a] < rank_[b]) swap(a, b);
        parent[b] = a;
        if (rank_[a] == rank_[b]) rank_[a]++;
    }
}

bool intersect(int* r1, int* r2) {
    int x1 = r1[0], y1 = r1[1], x2 = r1[2], y2 = r1[3];
    int x3 = r2[0], y3 = r2[1], x4 = r2[2], y4 = r2[3];

    // 완전히 분리된 경우
    if (x2 < x3 || x4 < x1 || y2 < y3 || y4 < y1) {
        return false;
    }

    // 하나가 다른 하나 안에 완전히 포함된 경우
    if (x1 < x3 && x4 < x2 && y1 < y3 && y4 < y2) {
        return false;
    }
    if (x3 < x1 && x2 < x4 && y3 < y1 && y2 < y4) {
        return false;
    }

    return true;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    int rects[1001][4];
    for (int i = 0; i < N; i++) {
        cin >> rects[i][0] >> rects[i][1] >> rects[i][2] >> rects[i][3];
    }
    // 원점 직사각형 추가
    rects[N][0] = rects[N][1] = rects[N][2] = rects[N][3] = 0;

    int n = N + 1;
    for (int i = 0; i < n; i++) {
        parent[i] = i;
        rank_[i] = 0;
    }

    // 교차하는 직사각형들을 같은 집합으로 합침
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (intersect(rects[i], rects[j])) {
                unite(i, j);
            }
        }
    }

    // 서로 다른 연결 요소의 개수
    set<int> components;
    for (int i = 0; i < n; i++) {
        components.insert(find(i));
    }

    // PU 명령 횟수 = 연결 요소 개수 - 1
    cout << components.size() - 1 << "\\n";

    return 0;
}
'''
            }
        ]
    },

    # Index 1345: 돌 게임 8 (baekjoon_9662)
    "1345": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    M = int(input())
    K = int(input())
    moves = list(map(int, input().split()))

    # Sprague-Grundy 값 계산
    # 상근이가 지는 경우 = 창영이가 이기는 경우 = SG값이 0인 경우

    # 충분히 큰 범위에서 SG값 계산하여 주기 찾기
    max_check = max(moves) * 100 + 1000
    sg = [0] * max_check

    for i in range(1, max_check):
        reachable = set()
        for m in moves:
            if i >= m:
                reachable.add(sg[i - m])
        # mex 계산
        mex = 0
        while mex in reachable:
            mex += 1
        sg[i] = mex

    # 패턴에서 주기 찾기 (SG값이 0인 위치)
    # 충분히 먼 위치에서 주기 시작
    start = max(moves) * 50

    # 주기 길이 찾기
    period = 0
    for p in range(1, max_check - start):
        found = True
        for i in range(100):  # 충분한 검증
            if start + i < max_check and start + p + i < max_check:
                if sg[start + i] != sg[start + p + i]:
                    found = False
                    break
        if found:
            period = p
            break

    # 주기 내에서 SG값이 0인 개수
    zero_in_period = sum(1 for i in range(start, start + period) if sg[i] == 0)

    if M <= start + period:
        # 직접 계산
        result = sum(1 for i in range(1, M + 1) if sg[i] == 0)
    else:
        # 주기 사용
        # [1, start) 구간의 0 개수
        count_before = sum(1 for i in range(1, start) if sg[i] == 0)

        # [start, M] 구간 계산
        remaining = M - start + 1
        full_periods = remaining // period
        partial = remaining % period

        count_period = full_periods * zero_in_period
        count_partial = sum(1 for i in range(start, start + partial) if sg[i] == 0)

        result = count_before + count_period + count_partial

    print(result)

solve()
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        long M = Long.parseLong(br.readLine().trim());
        int K = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] moves = new int[K];
        int maxMove = 0;
        for (int i = 0; i < K; i++) {
            moves[i] = Integer.parseInt(st.nextToken());
            maxMove = Math.max(maxMove, moves[i]);
        }

        // SG값 계산
        int maxCheck = maxMove * 100 + 1000;
        int[] sg = new int[maxCheck];

        for (int i = 1; i < maxCheck; i++) {
            Set<Integer> reachable = new HashSet<>();
            for (int m : moves) {
                if (i >= m) {
                    reachable.add(sg[i - m]);
                }
            }
            // mex 계산
            int mex = 0;
            while (reachable.contains(mex)) mex++;
            sg[i] = mex;
        }

        // 주기 찾기
        int start = maxMove * 50;
        int period = 0;

        outer:
        for (int p = 1; p < maxCheck - start; p++) {
            for (int i = 0; i < 100; i++) {
                if (start + i < maxCheck && start + p + i < maxCheck) {
                    if (sg[start + i] != sg[start + p + i]) {
                        continue outer;
                    }
                }
            }
            period = p;
            break;
        }

        // 주기 내 0 개수
        long zeroInPeriod = 0;
        for (int i = start; i < start + period; i++) {
            if (sg[i] == 0) zeroInPeriod++;
        }

        long result;
        if (M <= start + period) {
            result = 0;
            for (int i = 1; i <= M; i++) {
                if (sg[i] == 0) result++;
            }
        } else {
            // [1, start) 구간
            long countBefore = 0;
            for (int i = 1; i < start; i++) {
                if (sg[i] == 0) countBefore++;
            }

            // [start, M] 구간
            long remaining = M - start + 1;
            long fullPeriods = remaining / period;
            long partial = remaining % period;

            long countPeriod = fullPeriods * zeroInPeriod;
            long countPartial = 0;
            for (int i = start; i < start + partial; i++) {
                if (sg[i] == 0) countPartial++;
            }

            result = countBefore + countPeriod + countPartial;
        }

        System.out.println(result);
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long M;
    int K;
    cin >> M >> K;

    vector<int> moves(K);
    int maxMove = 0;
    for (int i = 0; i < K; i++) {
        cin >> moves[i];
        maxMove = max(maxMove, moves[i]);
    }

    // SG값 계산
    int maxCheck = maxMove * 100 + 1000;
    vector<int> sg(maxCheck, 0);

    for (int i = 1; i < maxCheck; i++) {
        set<int> reachable;
        for (int m : moves) {
            if (i >= m) {
                reachable.insert(sg[i - m]);
            }
        }
        // mex 계산
        int mex = 0;
        while (reachable.count(mex)) mex++;
        sg[i] = mex;
    }

    // 주기 찾기
    int start = maxMove * 50;
    int period = 0;

    for (int p = 1; p < maxCheck - start; p++) {
        bool found = true;
        for (int i = 0; i < 100; i++) {
            if (start + i < maxCheck && start + p + i < maxCheck) {
                if (sg[start + i] != sg[start + p + i]) {
                    found = false;
                    break;
                }
            }
        }
        if (found) {
            period = p;
            break;
        }
    }

    // 주기 내 0 개수
    long long zeroInPeriod = 0;
    for (int i = start; i < start + period; i++) {
        if (sg[i] == 0) zeroInPeriod++;
    }

    long long result;
    if (M <= start + period) {
        result = 0;
        for (int i = 1; i <= M; i++) {
            if (sg[i] == 0) result++;
        }
    } else {
        // [1, start) 구간
        long long countBefore = 0;
        for (int i = 1; i < start; i++) {
            if (sg[i] == 0) countBefore++;
        }

        // [start, M] 구간
        long long remaining = M - start + 1;
        long long fullPeriods = remaining / period;
        long long partial = remaining % period;

        long long countPeriod = fullPeriods * zeroInPeriod;
        long long countPartial = 0;
        for (int i = start; i < start + (int)partial; i++) {
            if (sg[i] == 0) countPartial++;
        }

        result = countBefore + countPeriod + countPartial;
    }

    cout << result << "\\n";

    return 0;
}
'''
            }
        ]
    },

    # Index 1350: 합 (baekjoon_1081)
    "1350": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def digit_sum(n):
    """0부터 n까지의 모든 수의 각 자릿수 합"""
    if n < 0:
        return 0
    if n == 0:
        return 0

    s = str(n)
    length = len(s)
    result = 0
    prefix = 0

    for i, c in enumerate(s):
        d = int(c)
        remaining = length - i - 1

        # 현재 자릿수보다 작은 숫자들의 기여
        # prefix * d * 10^remaining
        result += prefix * d * (10 ** remaining)

        # 0 ~ (d-1) 까지의 숫자가 현재 자리에 올 때
        # 각 숫자 k가 기여: k * 10^remaining
        # 합: (0+1+...+(d-1)) * 10^remaining = d*(d-1)/2 * 10^remaining
        result += d * (d - 1) // 2 * (10 ** remaining)

        # 뒤 자릿수들의 기여
        # d개의 블록, 각 블록은 10^remaining 개
        # 각 블록에서 한 자릿수의 합: 45 * remaining * 10^(remaining-1)
        if remaining > 0:
            result += d * 45 * remaining * (10 ** (remaining - 1))

        prefix += d

    # 마지막으로 모든 자릿수의 합 추가
    result += prefix

    return result

def solve():
    line = input().split()
    L, U = int(line[0]), int(line[1])

    if L == 0:
        print(digit_sum(U))
    else:
        print(digit_sum(U) - digit_sum(L - 1))

solve()
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
        long L = Long.parseLong(st.nextToken());
        long U = Long.parseLong(st.nextToken());

        if (L == 0) {
            System.out.println(digitSum(U));
        } else {
            System.out.println(digitSum(U) - digitSum(L - 1));
        }
    }

    static long digitSum(long n) {
        if (n <= 0) return 0;

        String s = Long.toString(n);
        int length = s.length();
        long result = 0;
        long prefix = 0;

        for (int i = 0; i < length; i++) {
            int d = s.charAt(i) - '0';
            int remaining = length - i - 1;
            long power = pow10(remaining);

            // 이전 자릿수들의 기여
            result += prefix * d * power;

            // 0 ~ (d-1) 까지의 숫자가 현재 자리에 올 때
            result += (long)d * (d - 1) / 2 * power;

            // 뒤 자릿수들의 기여
            if (remaining > 0) {
                result += (long)d * 45 * remaining * pow10(remaining - 1);
            }

            prefix += d;
        }

        result += prefix;

        return result;
    }

    static long pow10(int n) {
        long result = 1;
        for (int i = 0; i < n; i++) {
            result *= 10;
        }
        return result;
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
using namespace std;

long long pow10(int n) {
    long long result = 1;
    for (int i = 0; i < n; i++) {
        result *= 10;
    }
    return result;
}

long long digitSum(long long n) {
    if (n <= 0) return 0;

    string s = to_string(n);
    int length = s.length();
    long long result = 0;
    long long prefix = 0;

    for (int i = 0; i < length; i++) {
        int d = s[i] - '0';
        int remaining = length - i - 1;
        long long power = pow10(remaining);

        // 이전 자릿수들의 기여
        result += prefix * d * power;

        // 0 ~ (d-1) 까지의 숫자가 현재 자리에 올 때
        result += (long long)d * (d - 1) / 2 * power;

        // 뒤 자릿수들의 기여
        if (remaining > 0) {
            result += (long long)d * 45 * remaining * pow10(remaining - 1);
        }

        prefix += d;
    }

    result += prefix;

    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long L, U;
    cin >> L >> U;

    if (L == 0) {
        cout << digitSum(U) << "\\n";
    } else {
        cout << digitSum(U) - digitSum(L - 1) << "\\n";
    }

    return 0;
}
'''
            }
        ]
    },

    # Index 1357: 트리 색칠하기 (baekjoon_1693)
    "1357": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from collections import defaultdict
sys.setrecursionlimit(200000)
input = sys.stdin.readline

def solve():
    n = int(input())

    if n == 1:
        print(1)
        return

    # 인접 리스트 구성
    adj = defaultdict(list)
    for _ in range(n - 1):
        a, b = map(int, input().split())
        adj[a].append(b)
        adj[b].append(a)

    # 필요한 색상 수는 log2(n) + 1 정도면 충분
    import math
    max_color = int(math.log2(n)) + 2

    INF = float('inf')

    # dp[node][color] = node를 color로 칠했을 때 서브트리의 최소 비용
    dp = [[INF] * (max_color + 1) for _ in range(n + 1)]

    visited = [False] * (n + 1)

    def dfs(node):
        visited[node] = True
        children = []
        for next_node in adj[node]:
            if not visited[next_node]:
                children.append(next_node)
                dfs(next_node)

        if not children:
            # 리프 노드
            for c in range(1, max_color + 1):
                dp[node][c] = c
        else:
            # 내부 노드
            for c in range(1, max_color + 1):
                total = c  # 현재 노드 색상 비용
                for child in children:
                    # 자식은 현재 노드와 다른 색상이어야 함
                    min_child = INF
                    for cc in range(1, max_color + 1):
                        if cc != c:
                            min_child = min(min_child, dp[child][cc])
                    total += min_child
                dp[node][c] = total

    dfs(1)

    print(min(dp[1][c] for c in range(1, max_color + 1)))

solve()
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static List<List<Integer>> adj;
    static int[][] dp;
    static boolean[] visited;
    static int maxColor;
    static final int INF = 1_000_000_000;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        if (n == 1) {
            System.out.println(1);
            return;
        }

        adj = new ArrayList<>();
        for (int i = 0; i <= n; i++) {
            adj.add(new ArrayList<>());
        }

        for (int i = 0; i < n - 1; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            adj.get(a).add(b);
            adj.get(b).add(a);
        }

        maxColor = (int)(Math.log(n) / Math.log(2)) + 2;
        dp = new int[n + 1][maxColor + 1];
        visited = new boolean[n + 1];

        for (int i = 0; i <= n; i++) {
            Arrays.fill(dp[i], INF);
        }

        // 스택 기반 DFS (재귀 깊이 제한 회피)
        dfs(n, 1);

        int ans = INF;
        for (int c = 1; c <= maxColor; c++) {
            ans = Math.min(ans, dp[1][c]);
        }
        System.out.println(ans);
    }

    static void dfs(int n, int start) {
        // 후위 순회를 위해 스택 사용
        int[] parent = new int[n + 1];
        List<Integer>[] children = new ArrayList[n + 1];
        for (int i = 0; i <= n; i++) {
            children[i] = new ArrayList<>();
        }

        // BFS로 트리 구조 파악
        Queue<Integer> queue = new LinkedList<>();
        queue.offer(start);
        visited[start] = true;
        parent[start] = -1;
        List<Integer> order = new ArrayList<>();

        while (!queue.isEmpty()) {
            int node = queue.poll();
            order.add(node);
            for (int next : adj.get(node)) {
                if (!visited[next]) {
                    visited[next] = true;
                    parent[next] = node;
                    children[node].add(next);
                    queue.offer(next);
                }
            }
        }

        // 역순으로 처리 (후위 순회 효과)
        for (int i = order.size() - 1; i >= 0; i--) {
            int node = order.get(i);

            if (children[node].isEmpty()) {
                // 리프 노드
                for (int c = 1; c <= maxColor; c++) {
                    dp[node][c] = c;
                }
            } else {
                // 내부 노드
                for (int c = 1; c <= maxColor; c++) {
                    int total = c;
                    for (int child : children[node]) {
                        int minChild = INF;
                        for (int cc = 1; cc <= maxColor; cc++) {
                            if (cc != c) {
                                minChild = Math.min(minChild, dp[child][cc]);
                            }
                        }
                        total += minChild;
                    }
                    dp[node][c] = total;
                }
            }
        }
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <queue>
#include <cmath>
#include <algorithm>
#include <cstring>
using namespace std;

const int INF = 1e9;
int maxColor;
vector<int> adj[100001];
int dp[100001][20];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    if (n == 1) {
        cout << 1 << "\\n";
        return 0;
    }

    for (int i = 0; i < n - 1; i++) {
        int a, b;
        cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    maxColor = (int)(log2(n)) + 2;

    // 초기화
    for (int i = 0; i <= n; i++) {
        for (int j = 0; j <= maxColor; j++) {
            dp[i][j] = INF;
        }
    }

    // BFS로 트리 구조 파악 후 후위 순회
    vector<int> parent(n + 1, -1);
    vector<vector<int>> children(n + 1);
    vector<bool> visited(n + 1, false);
    vector<int> order;

    queue<int> q;
    q.push(1);
    visited[1] = true;

    while (!q.empty()) {
        int node = q.front();
        q.pop();
        order.push_back(node);

        for (int next : adj[node]) {
            if (!visited[next]) {
                visited[next] = true;
                parent[next] = node;
                children[node].push_back(next);
                q.push(next);
            }
        }
    }

    // 역순 처리
    for (int i = order.size() - 1; i >= 0; i--) {
        int node = order[i];

        if (children[node].empty()) {
            // 리프 노드
            for (int c = 1; c <= maxColor; c++) {
                dp[node][c] = c;
            }
        } else {
            // 내부 노드
            for (int c = 1; c <= maxColor; c++) {
                int total = c;
                for (int child : children[node]) {
                    int minChild = INF;
                    for (int cc = 1; cc <= maxColor; cc++) {
                        if (cc != c) {
                            minChild = min(minChild, dp[child][cc]);
                        }
                    }
                    total += minChild;
                }
                dp[node][c] = total;
            }
        }
    }

    int ans = INF;
    for (int c = 1; c <= maxColor; c++) {
        ans = min(ans, dp[1][c]);
    }
    cout << ans << "\\n";

    return 0;
}
'''
            }
        ]
    },

    # Index 1368: 합 (baekjoon_1132)
    "1368": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    numbers = []
    for _ in range(N):
        numbers.append(input().strip())

    # 각 알파벳의 가중치 계산
    weight = {}
    for c in 'ABCDEFGHIJ':
        weight[c] = 0

    # 0으로 시작할 수 없는 알파벳 표시
    cannot_be_zero = set()

    for num in numbers:
        if len(num) > 1:
            cannot_be_zero.add(num[0])

        # 각 자릿수별 가중치 계산
        for i, c in enumerate(num):
            weight[c] += 10 ** (len(num) - i - 1)

    # 사용된 알파벳만 추출
    used = set()
    for num in numbers:
        for c in num:
            used.add(c)

    used = list(used)

    # 가중치 기준 내림차순 정렬
    used.sort(key=lambda x: -weight[x])

    # 9부터 시작해서 할당
    result = 0
    digit = 9

    assigned = {}
    for c in used:
        assigned[c] = digit
        digit -= 1

    # 0으로 시작할 수 없는 알파벳 확인
    # 만약 0이 할당된 알파벳이 0으로 시작할 수 없다면,
    # 0으로 시작할 수 있는 알파벳 중 가장 가중치가 작은 것과 교환
    zero_char = None
    for c, d in assigned.items():
        if d == 0:
            zero_char = c
            break

    if zero_char and zero_char in cannot_be_zero:
        # 0으로 시작할 수 있는 알파벳 중 가장 가중치가 작은 것 찾기
        candidates = [c for c in used if c not in cannot_be_zero]
        if candidates:
            # 가장 가중치가 작은 알파벳과 교환
            min_weight_char = min(candidates, key=lambda x: weight[x])
            assigned[zero_char], assigned[min_weight_char] = assigned[min_weight_char], assigned[zero_char]

    # 결과 계산
    for num in numbers:
        value = 0
        for c in num:
            value = value * 10 + assigned[c]
        result += value

    print(result)

solve()
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        String[] numbers = new String[N];
        for (int i = 0; i < N; i++) {
            numbers[i] = br.readLine().trim();
        }

        // 각 알파벳의 가중치 계산
        long[] weight = new long[26];
        boolean[] cannotBeZero = new boolean[26];
        boolean[] used = new boolean[26];

        for (String num : numbers) {
            if (num.length() > 1) {
                cannotBeZero[num.charAt(0) - 'A'] = true;
            }

            long power = 1;
            for (int i = num.length() - 1; i >= 0; i--) {
                int idx = num.charAt(i) - 'A';
                weight[idx] += power;
                used[idx] = true;
                power *= 10;
            }
        }

        // 사용된 알파벳 수집 및 정렬
        List<Integer> usedChars = new ArrayList<>();
        for (int i = 0; i < 26; i++) {
            if (used[i]) {
                usedChars.add(i);
            }
        }

        usedChars.sort((a, b) -> Long.compare(weight[b], weight[a]));

        // 9부터 할당
        int[] assigned = new int[26];
        int digit = 9;
        for (int c : usedChars) {
            assigned[c] = digit--;
        }

        // 0이 할당된 알파벳이 0으로 시작할 수 없는 경우 교환
        int zeroChar = -1;
        for (int c : usedChars) {
            if (assigned[c] == 0) {
                zeroChar = c;
                break;
            }
        }

        if (zeroChar != -1 && cannotBeZero[zeroChar]) {
            // 0으로 시작할 수 있는 알파벳 중 가장 가중치가 작은 것 찾기
            int minWeightChar = -1;
            long minWeight = Long.MAX_VALUE;
            for (int c : usedChars) {
                if (!cannotBeZero[c] && weight[c] < minWeight) {
                    minWeight = weight[c];
                    minWeightChar = c;
                }
            }
            if (minWeightChar != -1) {
                int temp = assigned[zeroChar];
                assigned[zeroChar] = assigned[minWeightChar];
                assigned[minWeightChar] = temp;
            }
        }

        // 결과 계산
        long result = 0;
        for (String num : numbers) {
            long value = 0;
            for (char c : num.toCharArray()) {
                value = value * 10 + assigned[c - 'A'];
            }
            result += value;
        }

        System.out.println(result);
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    vector<string> numbers(N);
    for (int i = 0; i < N; i++) {
        cin >> numbers[i];
    }

    // 각 알파벳의 가중치 계산
    long long weight[26] = {0};
    bool cannotBeZero[26] = {false};
    bool used[26] = {false};

    for (const string& num : numbers) {
        if (num.length() > 1) {
            cannotBeZero[num[0] - 'A'] = true;
        }

        long long power = 1;
        for (int i = num.length() - 1; i >= 0; i--) {
            int idx = num[i] - 'A';
            weight[idx] += power;
            used[idx] = true;
            power *= 10;
        }
    }

    // 사용된 알파벳 수집 및 정렬
    vector<int> usedChars;
    for (int i = 0; i < 26; i++) {
        if (used[i]) {
            usedChars.push_back(i);
        }
    }

    sort(usedChars.begin(), usedChars.end(), [&](int a, int b) {
        return weight[a] > weight[b];
    });

    // 9부터 할당
    int assigned[26];
    int digit = 9;
    for (int c : usedChars) {
        assigned[c] = digit--;
    }

    // 0이 할당된 알파벳이 0으로 시작할 수 없는 경우 교환
    int zeroChar = -1;
    for (int c : usedChars) {
        if (assigned[c] == 0) {
            zeroChar = c;
            break;
        }
    }

    if (zeroChar != -1 && cannotBeZero[zeroChar]) {
        // 0으로 시작할 수 있는 알파벳 중 가장 가중치가 작은 것 찾기
        int minWeightChar = -1;
        long long minWeight = 1e18;
        for (int c : usedChars) {
            if (!cannotBeZero[c] && weight[c] < minWeight) {
                minWeight = weight[c];
                minWeightChar = c;
            }
        }
        if (minWeightChar != -1) {
            swap(assigned[zeroChar], assigned[minWeightChar]);
        }
    }

    // 결과 계산
    long long result = 0;
    for (const string& num : numbers) {
        long long value = 0;
        for (char c : num) {
            value = value * 10 + assigned[c - 'A'];
        }
        result += value;
    }

    cout << result << "\\n";

    return 0;
}
'''
            }
        ]
    },

    # Index 1371: 삼차 방정식 풀기 (baekjoon_9735)
    "1371": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve_cubic(A, B, C, D):
    """삼차 방정식 Ax^3 + Bx^2 + Cx + D = 0의 실수 해 찾기"""
    solutions = []

    # 정수 해 찾기 (유리근 정리 활용)
    # D의 약수를 확인
    if D == 0:
        int_root = 0
    else:
        int_root = None
        # D의 약수 중에서 해 찾기
        for x in range(-abs(D), abs(D) + 1):
            if x == 0:
                continue
            if D % x == 0:
                val = A * x * x * x + B * x * x + C * x + D
                if val == 0:
                    int_root = x
                    break

        if int_root is None:
            # 범위를 넓혀서 검색
            for x in range(-1000001, 1000001):
                val = A * x * x * x + B * x * x + C * x + D
                if val == 0:
                    int_root = x
                    break

    if int_root is None:
        return []

    # (x - int_root)로 나누기
    # Ax^3 + Bx^2 + Cx + D = (x - r)(ax^2 + bx + c)
    # a = A, b = B + A*r, c = C + r*(B + A*r) = C + Br + Ar^2
    a = A
    b = B + A * int_root
    c = C + int_root * b

    solutions.append(int_root)

    # 이차 방정식 ax^2 + bx + c = 0 풀기
    if a != 0:
        discriminant = b * b - 4 * a * c
        if discriminant >= 0:
            import math
            sqrt_d = math.sqrt(discriminant)
            x1 = (-b + sqrt_d) / (2 * a)
            x2 = (-b - sqrt_d) / (2 * a)

            if abs(x1 - x2) > 1e-9:
                solutions.append(x1)
                solutions.append(x2)
            else:
                solutions.append(x1)
    elif b != 0:
        solutions.append(-c / b)

    # 중복 제거 및 정렬
    unique = []
    solutions.sort()
    for s in solutions:
        if not unique or abs(s - unique[-1]) > 1e-9:
            unique.append(s)

    return unique

def main():
    N = int(input())
    for _ in range(N):
        A, B, C, D = map(int, input().split())
        roots = solve_cubic(A, B, C, D)
        print(' '.join(f'{r:.4f}' for r in roots))

main()
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

        for (int t = 0; t < N; t++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long A = Long.parseLong(st.nextToken());
            long B = Long.parseLong(st.nextToken());
            long C = Long.parseLong(st.nextToken());
            long D = Long.parseLong(st.nextToken());

            List<Double> roots = solveCubic(A, B, C, D);

            for (int i = 0; i < roots.size(); i++) {
                if (i > 0) sb.append(" ");
                sb.append(String.format("%.4f", roots.get(i)));
            }
            sb.append("\\n");
        }

        System.out.print(sb);
    }

    static List<Double> solveCubic(long A, long B, long C, long D) {
        List<Double> solutions = new ArrayList<>();

        // 정수 해 찾기
        Long intRoot = null;
        for (long x = -1000001; x <= 1000001; x++) {
            long val = A * x * x * x + B * x * x + C * x + D;
            if (val == 0) {
                intRoot = x;
                break;
            }
        }

        if (intRoot == null) {
            return solutions;
        }

        solutions.add((double) intRoot);

        // 조립제법으로 이차방정식 계수 구하기
        double a = A;
        double b = B + A * intRoot;
        double c = C + intRoot * b;

        // 이차방정식 풀기
        if (Math.abs(a) > 1e-10) {
            double discriminant = b * b - 4 * a * c;
            if (discriminant >= 0) {
                double sqrtD = Math.sqrt(discriminant);
                double x1 = (-b + sqrtD) / (2 * a);
                double x2 = (-b - sqrtD) / (2 * a);

                if (Math.abs(x1 - x2) > 1e-9) {
                    solutions.add(x1);
                    solutions.add(x2);
                } else {
                    solutions.add(x1);
                }
            }
        } else if (Math.abs(b) > 1e-10) {
            solutions.add(-c / b);
        }

        // 정렬 및 중복 제거
        Collections.sort(solutions);
        List<Double> unique = new ArrayList<>();
        for (double s : solutions) {
            if (unique.isEmpty() || Math.abs(s - unique.get(unique.size() - 1)) > 1e-9) {
                unique.add(s);
            }
        }

        return unique;
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <iomanip>
using namespace std;

vector<double> solveCubic(long long A, long long B, long long C, long long D) {
    vector<double> solutions;

    // 정수 해 찾기
    long long intRoot = 0;
    bool found = false;

    for (long long x = -1000001; x <= 1000001; x++) {
        long long val = A * x * x * x + B * x * x + C * x + D;
        if (val == 0) {
            intRoot = x;
            found = true;
            break;
        }
    }

    if (!found) return solutions;

    solutions.push_back((double)intRoot);

    // 조립제법으로 이차방정식 계수 구하기
    double a = A;
    double b = B + A * intRoot;
    double c = C + intRoot * b;

    // 이차방정식 풀기
    if (fabs(a) > 1e-10) {
        double discriminant = b * b - 4 * a * c;
        if (discriminant >= 0) {
            double sqrtD = sqrt(discriminant);
            double x1 = (-b + sqrtD) / (2 * a);
            double x2 = (-b - sqrtD) / (2 * a);

            if (fabs(x1 - x2) > 1e-9) {
                solutions.push_back(x1);
                solutions.push_back(x2);
            } else {
                solutions.push_back(x1);
            }
        }
    } else if (fabs(b) > 1e-10) {
        solutions.push_back(-c / b);
    }

    // 정렬 및 중복 제거
    sort(solutions.begin(), solutions.end());
    vector<double> unique;
    for (double s : solutions) {
        if (unique.empty() || fabs(s - unique.back()) > 1e-9) {
            unique.push_back(s);
        }
    }

    return unique;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    cout << fixed << setprecision(4);

    int N;
    cin >> N;

    while (N--) {
        long long A, B, C, D;
        cin >> A >> B >> C >> D;

        vector<double> roots = solveCubic(A, B, C, D);

        for (int i = 0; i < roots.size(); i++) {
            if (i > 0) cout << " ";
            cout << roots[i];
        }
        cout << "\\n";
    }

    return 0;
}
'''
            }
        ]
    },

    # Index 1375: 분단의 슬픔 (baekjoon_13161) - 최소 컷 문제
    "1375": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from collections import deque
input = sys.stdin.readline

def solve():
    N = int(input())
    camps = list(map(int, input().split()))

    # 노드 번호: 0 = source, 1~N = 사람, N+1 = sink
    source = 0
    sink = N + 1

    # 인접 리스트와 용량 배열
    INF = float('inf')
    graph = [[] for _ in range(N + 2)]
    capacity = [[0] * (N + 2) for _ in range(N + 2)]

    # 진영 연결
    for i in range(N):
        if camps[i] == 1:  # A진영 (source와 연결)
            graph[source].append(i + 1)
            graph[i + 1].append(source)
            capacity[source][i + 1] = INF
        elif camps[i] == 2:  # B진영 (sink와 연결)
            graph[i + 1].append(sink)
            graph[sink].append(i + 1)
            capacity[i + 1][sink] = INF

    # 슬픔 가중치
    for i in range(N):
        weights = list(map(int, input().split()))
        for j in range(N):
            if i != j and weights[j] > 0:
                graph[i + 1].append(j + 1)
                capacity[i + 1][j + 1] += weights[j]

    # 최대 유량 (Dinic 알고리즘)
    def bfs():
        level = [-1] * (N + 2)
        level[source] = 0
        q = deque([source])
        while q:
            u = q.popleft()
            for v in graph[u]:
                if level[v] == -1 and capacity[u][v] > 0:
                    level[v] = level[u] + 1
                    q.append(v)
        return level[sink] != -1, level

    def dfs(u, pushed, level, iter_):
        if u == sink:
            return pushed
        while iter_[u] < len(graph[u]):
            v = graph[u][iter_[u]]
            if level[v] == level[u] + 1 and capacity[u][v] > 0:
                d = dfs(v, min(pushed, capacity[u][v]), level, iter_)
                if d > 0:
                    capacity[u][v] -= d
                    capacity[v][u] += d
                    return d
            iter_[u] += 1
        return 0

    max_flow = 0
    while True:
        found, level = bfs()
        if not found:
            break
        iter_ = [0] * (N + 2)
        while True:
            f = dfs(source, INF, level, iter_)
            if f == 0:
                break
            max_flow += f

    # 최소 컷 찾기 (source에서 도달 가능한 정점)
    visited = [False] * (N + 2)
    q = deque([source])
    visited[source] = True
    while q:
        u = q.popleft()
        for v in graph[u]:
            if not visited[v] and capacity[u][v] > 0:
                visited[v] = True
                q.append(v)

    # A진영: source에서 도달 가능
    # B진영: source에서 도달 불가능
    A_group = [i for i in range(1, N + 1) if visited[i]]
    B_group = [i for i in range(1, N + 1) if not visited[i]]

    print(max_flow)
    print(' '.join(map(str, A_group)) if A_group else '')
    print(' '.join(map(str, B_group)) if B_group else '')

solve()
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int N;
    static List<Integer>[] graph;
    static int[][] capacity;
    static int source, sink;
    static final int INF = 1_000_000_000;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        N = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] camps = new int[N];
        for (int i = 0; i < N; i++) {
            camps[i] = Integer.parseInt(st.nextToken());
        }

        source = 0;
        sink = N + 1;

        graph = new ArrayList[N + 2];
        capacity = new int[N + 2][N + 2];
        for (int i = 0; i < N + 2; i++) {
            graph[i] = new ArrayList<>();
        }

        // 진영 연결
        for (int i = 0; i < N; i++) {
            if (camps[i] == 1) {
                graph[source].add(i + 1);
                graph[i + 1].add(source);
                capacity[source][i + 1] = INF;
            } else if (camps[i] == 2) {
                graph[i + 1].add(sink);
                graph[sink].add(i + 1);
                capacity[i + 1][sink] = INF;
            }
        }

        // 슬픔 가중치
        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < N; j++) {
                int w = Integer.parseInt(st.nextToken());
                if (i != j && w > 0) {
                    if (capacity[i + 1][j + 1] == 0) {
                        graph[i + 1].add(j + 1);
                    }
                    capacity[i + 1][j + 1] += w;
                }
            }
        }

        // Dinic 알고리즘
        long maxFlow = 0;
        int[] level = new int[N + 2];
        int[] iter = new int[N + 2];

        while (bfs(level)) {
            Arrays.fill(iter, 0);
            int f;
            while ((f = dfs(source, INF, level, iter)) > 0) {
                maxFlow += f;
            }
        }

        // 최소 컷 찾기
        boolean[] visited = new boolean[N + 2];
        Queue<Integer> q = new LinkedList<>();
        q.offer(source);
        visited[source] = true;
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : graph[u]) {
                if (!visited[v] && capacity[u][v] > 0) {
                    visited[v] = true;
                    q.offer(v);
                }
            }
        }

        StringBuilder sbA = new StringBuilder();
        StringBuilder sbB = new StringBuilder();
        for (int i = 1; i <= N; i++) {
            if (visited[i]) {
                if (sbA.length() > 0) sbA.append(" ");
                sbA.append(i);
            } else {
                if (sbB.length() > 0) sbB.append(" ");
                sbB.append(i);
            }
        }

        System.out.println(maxFlow);
        System.out.println(sbA);
        System.out.println(sbB);
    }

    static boolean bfs(int[] level) {
        Arrays.fill(level, -1);
        level[source] = 0;
        Queue<Integer> q = new LinkedList<>();
        q.offer(source);
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : graph[u]) {
                if (level[v] == -1 && capacity[u][v] > 0) {
                    level[v] = level[u] + 1;
                    q.offer(v);
                }
            }
        }
        return level[sink] != -1;
    }

    static int dfs(int u, int pushed, int[] level, int[] iter) {
        if (u == sink) return pushed;
        for (; iter[u] < graph[u].size(); iter[u]++) {
            int v = graph[u].get(iter[u]);
            if (level[v] == level[u] + 1 && capacity[u][v] > 0) {
                int d = dfs(v, Math.min(pushed, capacity[u][v]), level, iter);
                if (d > 0) {
                    capacity[u][v] -= d;
                    capacity[v][u] += d;
                    return d;
                }
            }
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
#include <queue>
#include <cstring>
using namespace std;

const int INF = 1e9;
int N;
vector<int> graph[502];
int capacity[502][502];
int source, sink;

bool bfs(int level[]) {
    memset(level, -1, sizeof(int) * (N + 2));
    level[source] = 0;
    queue<int> q;
    q.push(source);
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        for (int v : graph[u]) {
            if (level[v] == -1 && capacity[u][v] > 0) {
                level[v] = level[u] + 1;
                q.push(v);
            }
        }
    }
    return level[sink] != -1;
}

int dfs(int u, int pushed, int level[], int iter[]) {
    if (u == sink) return pushed;
    for (; iter[u] < graph[u].size(); iter[u]++) {
        int v = graph[u][iter[u]];
        if (level[v] == level[u] + 1 && capacity[u][v] > 0) {
            int d = dfs(v, min(pushed, capacity[u][v]), level, iter);
            if (d > 0) {
                capacity[u][v] -= d;
                capacity[v][u] += d;
                return d;
            }
        }
    }
    return 0;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> N;

    vector<int> camps(N);
    for (int i = 0; i < N; i++) {
        cin >> camps[i];
    }

    source = 0;
    sink = N + 1;

    memset(capacity, 0, sizeof(capacity));

    // 진영 연결
    for (int i = 0; i < N; i++) {
        if (camps[i] == 1) {
            graph[source].push_back(i + 1);
            graph[i + 1].push_back(source);
            capacity[source][i + 1] = INF;
        } else if (camps[i] == 2) {
            graph[i + 1].push_back(sink);
            graph[sink].push_back(i + 1);
            capacity[i + 1][sink] = INF;
        }
    }

    // 슬픔 가중치
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            int w;
            cin >> w;
            if (i != j && w > 0) {
                if (capacity[i + 1][j + 1] == 0) {
                    graph[i + 1].push_back(j + 1);
                }
                capacity[i + 1][j + 1] += w;
            }
        }
    }

    // Dinic
    long long maxFlow = 0;
    int level[502], iter[502];

    while (bfs(level)) {
        memset(iter, 0, sizeof(iter));
        int f;
        while ((f = dfs(source, INF, level, iter)) > 0) {
            maxFlow += f;
        }
    }

    // 최소 컷 찾기
    bool visited[502] = {false};
    queue<int> q;
    q.push(source);
    visited[source] = true;
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        for (int v : graph[u]) {
            if (!visited[v] && capacity[u][v] > 0) {
                visited[v] = true;
                q.push(v);
            }
        }
    }

    cout << maxFlow << "\\n";

    bool firstA = true, firstB = true;
    for (int i = 1; i <= N; i++) {
        if (visited[i]) {
            if (!firstA) cout << " ";
            cout << i;
            firstA = false;
        }
    }
    cout << "\\n";

    for (int i = 1; i <= N; i++) {
        if (!visited[i]) {
            if (!firstB) cout << " ";
            cout << i;
            firstB = false;
        }
    }
    cout << "\\n";

    return 0;
}
'''
            }
        ]
    },

    # Index 1378: 전봇대 (baekjoon_8986) - 삼분 탐색
    "1378": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    x = list(map(int, input().split()))

    if N == 1:
        print(0)
        return

    # 삼분 탐색으로 최적의 간격 d 찾기
    # d의 범위: 1 ~ x[N-1]

    def calc_cost(d):
        """간격이 d일 때 총 이동 거리"""
        total = 0
        for i in range(N):
            target = i * d  # i번째 전봇대의 목표 위치
            total += abs(x[i] - target)
        return total

    left = 0
    right = x[N - 1]

    # 삼분 탐색
    while right - left > 2:
        m1 = left + (right - left) // 3
        m2 = right - (right - left) // 3

        if calc_cost(m1) > calc_cost(m2):
            left = m1
        else:
            right = m2

    # 남은 범위에서 최솟값 찾기
    min_cost = float('inf')
    for d in range(left, right + 1):
        min_cost = min(min_cost, calc_cost(d))

    print(min_cost)

solve()
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int N;
    static long[] x;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        N = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        x = new long[N];
        for (int i = 0; i < N; i++) {
            x[i] = Long.parseLong(st.nextToken());
        }

        if (N == 1) {
            System.out.println(0);
            return;
        }

        // 삼분 탐색
        long left = 0;
        long right = x[N - 1];

        while (right - left > 2) {
            long m1 = left + (right - left) / 3;
            long m2 = right - (right - left) / 3;

            if (calcCost(m1) > calcCost(m2)) {
                left = m1;
            } else {
                right = m2;
            }
        }

        // 남은 범위에서 최솟값 찾기
        long minCost = Long.MAX_VALUE;
        for (long d = left; d <= right; d++) {
            minCost = Math.min(minCost, calcCost(d));
        }

        System.out.println(minCost);
    }

    static long calcCost(long d) {
        long total = 0;
        for (int i = 0; i < N; i++) {
            long target = (long)i * d;
            total += Math.abs(x[i] - target);
        }
        return total;
    }
}
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

int N;
vector<long long> x;

long long calcCost(long long d) {
    long long total = 0;
    for (int i = 0; i < N; i++) {
        long long target = (long long)i * d;
        total += abs(x[i] - target);
    }
    return total;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> N;
    x.resize(N);
    for (int i = 0; i < N; i++) {
        cin >> x[i];
    }

    if (N == 1) {
        cout << 0 << "\\n";
        return 0;
    }

    // 삼분 탐색
    long long left = 0;
    long long right = x[N - 1];

    while (right - left > 2) {
        long long m1 = left + (right - left) / 3;
        long long m2 = right - (right - left) / 3;

        if (calcCost(m1) > calcCost(m2)) {
            left = m1;
        } else {
            right = m2;
        }
    }

    // 남은 범위에서 최솟값 찾기
    long long minCost = 1e18;
    for (long long d = left; d <= right; d++) {
        minCost = min(minCost, calcCost(d));
    }

    cout << minCost << "\\n";

    return 0;
}
'''
            }
        ]
    }
}

# baek_medium.json에 추가
def main():
    with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'r') as f:
        data = json.load(f)

    # 새 솔루션 추가
    for idx, sol_data in solutions.items():
        data[idx] = sol_data

    with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Added {len(solutions)} solutions to baek_medium.json")
    print(f"Total entries in baek_medium.json: {len(data)}")

if __name__ == "__main__":
    main()
