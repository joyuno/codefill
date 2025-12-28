#!/usr/bin/env python3
"""
백준 문제 솔루션 생성 및 업데이트 스크립트 (Part 3)
나머지 문제들에 대한 솔루션
"""

import json

# 추가 솔루션 정의
SOLUTIONS_PART3 = {
    # 2546: 경제학과 정원영
    "2546": {
        "python": '''# 백준 2546: 경제학과 정원영
# C언어 평균보다 낮고 경제학 평균보다 높은 학생 수

import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    input()  # 빈 줄
    N, M = map(int, input().split())
    iqs = list(map(int, input().split()))

    c_iqs = iqs[:N]
    e_iqs = iqs[N:]

    c_avg = sum(c_iqs) / N
    e_avg = sum(e_iqs) / M

    count = 0
    for iq in c_iqs:
        # C언어 평균보다 낮고 경제학 평균보다 높으면 두 평균 모두 올라감
        if iq < c_avg and iq > e_avg:
            count += 1

    print(count)
''',
        "java": '''import java.util.*;

// 백준 2546: 경제학과 정원영
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        for (int t = 0; t < T; t++) {
            int N = sc.nextInt();
            int M = sc.nextInt();

            long[] cIQs = new long[N];
            long[] eIQs = new long[M];
            long cSum = 0, eSum = 0;

            for (int i = 0; i < N; i++) {
                cIQs[i] = sc.nextLong();
                cSum += cIQs[i];
            }
            for (int i = 0; i < M; i++) {
                eIQs[i] = sc.nextLong();
                eSum += eIQs[i];
            }

            double cAvg = (double) cSum / N;
            double eAvg = (double) eSum / M;

            int count = 0;
            for (int i = 0; i < N; i++) {
                if (cIQs[i] < cAvg && cIQs[i] > eAvg) {
                    count++;
                }
            }

            System.out.println(count);
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 2546: 경제학과 정원영
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int N, M;
        cin >> N >> M;

        long long cIQs[200001], eIQs[200001];
        long long cSum = 0, eSum = 0;

        for (int i = 0; i < N; i++) {
            cin >> cIQs[i];
            cSum += cIQs[i];
        }
        for (int i = 0; i < M; i++) {
            cin >> eIQs[i];
            eSum += eIQs[i];
        }

        double cAvg = (double) cSum / N;
        double eAvg = (double) eSum / M;

        int count = 0;
        for (int i = 0; i < N; i++) {
            if (cIQs[i] < cAvg && cIQs[i] > eAvg) {
                count++;
            }
        }

        cout << count << "\\n";
    }

    return 0;
}
'''
    },

    # 30019: 강의실 예약 시스템
    "30019": {
        "python": '''# 백준 30019: 강의실 예약 시스템
# 예약이 겹치지 않으면 수락

import sys
input = sys.stdin.readline

N, M = map(int, input().split())

# 각 강의실별 예약 현황
rooms = [[] for _ in range(N + 1)]

for _ in range(M):
    k, s, e = map(int, input().split())

    # 기존 예약과 겹치는지 확인
    conflict = False
    for rs, re in rooms[k]:
        if not (e <= rs or s >= re):  # 겹침
            conflict = True
            break

    if conflict:
        print("NO")
    else:
        print("YES")
        rooms[k].append((s, e))
''',
        "java": '''import java.util.*;

// 백준 30019: 강의실 예약 시스템
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int M = sc.nextInt();

        List<int[]>[] rooms = new ArrayList[N + 1];
        for (int i = 0; i <= N; i++) {
            rooms[i] = new ArrayList<>();
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < M; i++) {
            int k = sc.nextInt();
            int s = sc.nextInt();
            int e = sc.nextInt();

            boolean conflict = false;
            for (int[] res : rooms[k]) {
                if (!(e <= res[0] || s >= res[1])) {
                    conflict = true;
                    break;
                }
            }

            if (conflict) {
                sb.append("NO\\n");
            } else {
                sb.append("YES\\n");
                rooms[k].add(new int[]{s, e});
            }
        }

        System.out.print(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
using namespace std;

// 백준 30019: 강의실 예약 시스템
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    vector<pair<int, int>> rooms[N + 1];

    for (int i = 0; i < M; i++) {
        int k, s, e;
        cin >> k >> s >> e;

        bool conflict = false;
        for (auto& res : rooms[k]) {
            if (!(e <= res.first || s >= res.second)) {
                conflict = true;
                break;
            }
        }

        if (conflict) {
            cout << "NO\\n";
        } else {
            cout << "YES\\n";
            rooms[k].push_back({s, e});
        }
    }

    return 0;
}
'''
    },

    # 17946: 피자는 나눌 수록 커지잖아요
    "17946": {
        "python": '''# 백준 17946: 피자는 나눌 수록 커지잖아요
# k번 칼질하면 k+1조각, 윤희에게 1+2+...+k = k(k+1)/2 조각
# 예찬이가 먹는 조각 = k+1 - k(k+1)/2 = (k+1)(1 - k/2)
# k=1일 때 가장 많이 먹음 (조각 2개 - 1개 = 1개)

T = int(input())
for _ in range(T):
    K = int(input())
    # 칼질 1번: 2조각, 윤희 1조각, 예찬 1조각
    print(1)
''',
        "java": '''import java.util.Scanner;

// 백준 17946: 피자는 나눌 수록 커지잖아요
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        for (int t = 0; t < T; t++) {
            int K = sc.nextInt();
            // 칼질 1번이 항상 최적
            System.out.println(1);
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 17946: 피자는 나눌 수록 커지잖아요
int main() {
    int T;
    cin >> T;

    while (T--) {
        int K;
        cin >> K;
        // 칼질 1번이 항상 최적
        cout << 1 << "\\n";
    }

    return 0;
}
'''
    },

    # 11580: Footprint
    "11580": {
        "python": '''# 백준 11580: Footprint
# 동서남북 이동 후 방문한 좌표 개수

N = int(input())
S = input().strip()

visited = set()
x, y = 0, 0
visited.add((x, y))

for c in S:
    if c == 'N':
        y += 1
    elif c == 'S':
        y -= 1
    elif c == 'E':
        x += 1
    elif c == 'W':
        x -= 1
    visited.add((x, y))

print(len(visited))
''',
        "java": '''import java.util.*;

// 백준 11580: Footprint
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        String S = sc.next();

        Set<String> visited = new HashSet<>();
        int x = 0, y = 0;
        visited.add(x + "," + y);

        for (char c : S.toCharArray()) {
            if (c == 'N') y++;
            else if (c == 'S') y--;
            else if (c == 'E') x++;
            else if (c == 'W') x--;
            visited.add(x + "," + y);
        }

        System.out.println(visited.size());
    }
}
''',
        "cpp": '''#include <iostream>
#include <set>
#include <string>
using namespace std;

// 백준 11580: Footprint
int main() {
    int N;
    string S;
    cin >> N >> S;

    set<pair<int, int>> visited;
    int x = 0, y = 0;
    visited.insert({x, y});

    for (char c : S) {
        if (c == 'N') y++;
        else if (c == 'S') y--;
        else if (c == 'E') x++;
        else if (c == 'W') x--;
        visited.insert({x, y});
    }

    cout << visited.size() << endl;

    return 0;
}
'''
    },

    # 18229: 내가 살게, 아냐 내가 살게
    "18229": {
        "python": '''# 백준 18229: 내가 살게, 아냐 내가 살게
# 처음으로 K 이상 손을 뻗은 사람 찾기

N, M, K = map(int, input().split())
A = []
for _ in range(N):
    A.append(list(map(int, input().split())))

# 각 사람의 현재 뻗은 손 길이
reach = [0] * N

for j in range(M):
    for i in range(N):
        reach[i] += A[i][j]
        if reach[i] >= K:
            print(i + 1, j + 1)
            exit()
''',
        "java": '''import java.util.Scanner;

// 백준 18229: 내가 살게, 아냐 내가 살게
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int M = sc.nextInt();
        int K = sc.nextInt();

        int[][] A = new int[N][M];
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < M; j++) {
                A[i][j] = sc.nextInt();
            }
        }

        int[] reach = new int[N];

        for (int j = 0; j < M; j++) {
            for (int i = 0; i < N; i++) {
                reach[i] += A[i][j];
                if (reach[i] >= K) {
                    System.out.println((i + 1) + " " + (j + 1));
                    return;
                }
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 18229: 내가 살게, 아냐 내가 살게
int main() {
    int N, M, K;
    cin >> N >> M >> K;

    int A[100][100];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            cin >> A[i][j];
        }
    }

    int reach[100] = {0};

    for (int j = 0; j < M; j++) {
        for (int i = 0; i < N; i++) {
            reach[i] += A[i][j];
            if (reach[i] >= K) {
                cout << i + 1 << " " << j + 1 << endl;
                return 0;
            }
        }
    }

    return 0;
}
'''
    },

    # 3724: 표
    "3724": {
        "python": '''# 백준 3724: 표
# 각 열의 곱이 가장 큰 열 번호 찾기
# 곱이 클 수 있으므로 로그 합으로 비교

import math

T = int(input())
for _ in range(T):
    M, N = map(int, input().split())

    # 각 열의 곱의 부호와 절대값 로그
    log_sum = [0] * M
    sign = [1] * M
    zero = [False] * M

    for _ in range(N):
        row = list(map(int, input().split()))
        for j in range(M):
            if row[j] == 0:
                zero[j] = True
            elif row[j] < 0:
                sign[j] *= -1
                log_sum[j] += math.log(abs(row[j]))
            else:
                log_sum[j] += math.log(row[j])

    # 가장 큰 열 찾기 (같으면 번호가 큰 것)
    best_col = -1
    best_val = None

    for j in range(M):
        if zero[j]:
            val = (0, 0)  # 0
        elif sign[j] < 0:
            val = (-1, log_sum[j])  # 음수
        else:
            val = (1, log_sum[j])  # 양수

        if best_val is None or val > best_val or (val == best_val):
            best_val = val
            best_col = j

    print(best_col + 1)
''',
        "java": '''import java.util.*;

// 백준 3724: 표
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        for (int t = 0; t < T; t++) {
            int M = sc.nextInt();
            int N = sc.nextInt();

            double[] logSum = new double[M];
            int[] sign = new int[M];
            boolean[] zero = new boolean[M];
            Arrays.fill(sign, 1);

            for (int i = 0; i < N; i++) {
                for (int j = 0; j < M; j++) {
                    long val = sc.nextLong();
                    if (val == 0) {
                        zero[j] = true;
                    } else if (val < 0) {
                        sign[j] *= -1;
                        logSum[j] += Math.log(Math.abs(val));
                    } else {
                        logSum[j] += Math.log(val);
                    }
                }
            }

            int bestCol = 0;
            for (int j = 1; j < M; j++) {
                int cmp = compare(zero, sign, logSum, j, bestCol);
                if (cmp > 0 || cmp == 0) {
                    bestCol = j;
                }
            }

            System.out.println(bestCol + 1);
        }
    }

    static int compare(boolean[] zero, int[] sign, double[] logSum, int a, int b) {
        int sA = zero[a] ? 0 : sign[a];
        int sB = zero[b] ? 0 : sign[b];

        if (sA != sB) return sA - sB;
        if (sA == 0) return 0;
        if (sA > 0) return Double.compare(logSum[a], logSum[b]);
        return Double.compare(logSum[b], logSum[a]);
    }
}
''',
        "cpp": '''#include <iostream>
#include <cmath>
#include <vector>
using namespace std;

// 백준 3724: 표
int main() {
    int T;
    cin >> T;

    while (T--) {
        int M, N;
        cin >> M >> N;

        vector<double> logSum(M, 0);
        vector<int> sign(M, 1);
        vector<bool> zero(M, false);

        for (int i = 0; i < N; i++) {
            for (int j = 0; j < M; j++) {
                long long val;
                cin >> val;
                if (val == 0) {
                    zero[j] = true;
                } else if (val < 0) {
                    sign[j] *= -1;
                    logSum[j] += log(abs(val));
                } else {
                    logSum[j] += log(val);
                }
            }
        }

        int bestCol = 0;
        for (int j = 1; j < M; j++) {
            int sA = zero[j] ? 0 : sign[j];
            int sB = zero[bestCol] ? 0 : sign[bestCol];

            if (sA > sB) {
                bestCol = j;
            } else if (sA == sB) {
                if (sA == 0 || (sA > 0 && logSum[j] >= logSum[bestCol])
                    || (sA < 0 && logSum[j] <= logSum[bestCol])) {
                    bestCol = j;
                }
            }
        }

        cout << bestCol + 1 << "\\n";
    }

    return 0;
}
'''
    },

    # 18130: 여름나기
    "18130": {
        "python": '''# 백준 18130: 여름나기
# 집까지 T시간, 손 선풍기 비용 최소화

N, T = map(int, input().split())

best_idx = -1
best_cost = float('inf')

for i in range(N):
    P, K, C = map(int, input().split())

    # K시간마다 비용 추가
    # T시간까지 추가 비용 = C*(1 + 2 + ... + floor((T-1)/K))
    # = C * m * (m+1) / 2 where m = (T-1) // K
    m = (T - 1) // K if K > 0 else 0
    extra_cost = C * m * (m + 1) // 2
    total = P + extra_cost

    if total < best_cost:
        best_cost = total
        best_idx = i + 1

print(best_idx, best_cost)
''',
        "java": '''import java.util.Scanner;

// 백준 18130: 여름나기
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        long T = sc.nextLong();

        int bestIdx = -1;
        long bestCost = Long.MAX_VALUE;

        for (int i = 0; i < N; i++) {
            long P = sc.nextLong();
            long K = sc.nextLong();
            long C = sc.nextLong();

            long m = (T - 1) / K;
            long extraCost = C * m * (m + 1) / 2;
            long total = P + extraCost;

            if (total < bestCost) {
                bestCost = total;
                bestIdx = i + 1;
            }
        }

        System.out.println(bestIdx + " " + bestCost);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 18130: 여름나기
int main() {
    int N;
    long long T;
    cin >> N >> T;

    int bestIdx = -1;
    long long bestCost = 1e18;

    for (int i = 0; i < N; i++) {
        long long P, K, C;
        cin >> P >> K >> C;

        long long m = (T - 1) / K;
        long long extraCost = C * m * (m + 1) / 2;
        long long total = P + extraCost;

        if (total < bestCost) {
            bestCost = total;
            bestIdx = i + 1;
        }
    }

    cout << bestIdx << " " << bestCost << endl;

    return 0;
}
'''
    },

    # 19563: 개구리 1
    "19563": {
        "python": '''# 백준 19563: 개구리 1
# 원점에서 c번 점프 후 (a, b)에 도달 가능한지

a, b, c = map(int, input().split())

# 최소 필요 점프: |a| + |b|
# c번 점프로 가능하려면 c >= |a| + |b|
# 그리고 (c - (|a| + |b|))가 짝수여야 함 (왕복 이동)

min_jumps = abs(a) + abs(b)

if c >= min_jumps and (c - min_jumps) % 2 == 0:
    print("YES")
else:
    print("NO")
''',
        "java": '''import java.util.Scanner;

// 백준 19563: 개구리 1
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long a = sc.nextLong();
        long b = sc.nextLong();
        long c = sc.nextLong();

        long minJumps = Math.abs(a) + Math.abs(b);

        if (c >= minJumps && (c - minJumps) % 2 == 0) {
            System.out.println("YES");
        } else {
            System.out.println("NO");
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <cmath>
using namespace std;

// 백준 19563: 개구리 1
int main() {
    long long a, b, c;
    cin >> a >> b >> c;

    long long minJumps = abs(a) + abs(b);

    if (c >= minJumps && (c - minJumps) % 2 == 0) {
        cout << "YES" << endl;
    } else {
        cout << "NO" << endl;
    }

    return 0;
}
'''
    },

    # 20651: Daisy Chains
    "20651": {
        "python": '''# 백준 20651: Daisy Chains
# (i, j) 쌍 중 평균 꽃잎 수를 가진 꽃이 있는 쌍의 개수

N = int(input())
petals = list(map(int, input().split()))

count = 0

for i in range(N):
    for j in range(i, N):
        # i부터 j까지의 꽃들
        total = sum(petals[i:j+1])
        length = j - i + 1
        avg = total / length

        # 평균과 같은 꽃잎을 가진 꽃이 있는지
        if avg in petals[i:j+1]:
            count += 1

print(count)
''',
        "java": '''import java.util.Scanner;

// 백준 20651: Daisy Chains
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] petals = new int[N];
        for (int i = 0; i < N; i++) {
            petals[i] = sc.nextInt();
        }

        int count = 0;

        for (int i = 0; i < N; i++) {
            int total = 0;
            for (int j = i; j < N; j++) {
                total += petals[j];
                int length = j - i + 1;

                // 평균이 정수인지 확인
                if (total % length == 0) {
                    int avg = total / length;
                    for (int k = i; k <= j; k++) {
                        if (petals[k] == avg) {
                            count++;
                            break;
                        }
                    }
                }
            }
        }

        System.out.println(count);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 20651: Daisy Chains
int main() {
    int N;
    cin >> N;
    int petals[100];
    for (int i = 0; i < N; i++) {
        cin >> petals[i];
    }

    int count = 0;

    for (int i = 0; i < N; i++) {
        int total = 0;
        for (int j = i; j < N; j++) {
            total += petals[j];
            int length = j - i + 1;

            if (total % length == 0) {
                int avg = total / length;
                for (int k = i; k <= j; k++) {
                    if (petals[k] == avg) {
                        count++;
                        break;
                    }
                }
            }
        }
    }

    cout << count << endl;

    return 0;
}
'''
    },

    # 31408: 당직 근무표
    "31408": {
        "python": '''# 백준 31408: 당직 근무표
# 이틀 연속 같은 사람이 당직을 서지 않도록 할 수 있는지

from collections import Counter

N = int(input())
schedule = list(map(int, input().split()))

# 가장 많이 등장하는 병사의 횟수
counts = Counter(schedule)
max_count = max(counts.values())

# 가장 많이 등장하는 병사가 (N+1)//2 이하면 가능
if max_count <= (N + 1) // 2:
    print("YES")
else:
    print("NO")
''',
        "java": '''import java.util.*;

// 백준 31408: 당직 근무표
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        Map<Integer, Integer> counts = new HashMap<>();
        for (int i = 0; i < N; i++) {
            int a = sc.nextInt();
            counts.put(a, counts.getOrDefault(a, 0) + 1);
        }

        int maxCount = Collections.max(counts.values());

        if (maxCount <= (N + 1) / 2) {
            System.out.println("YES");
        } else {
            System.out.println("NO");
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <map>
using namespace std;

// 백준 31408: 당직 근무표
int main() {
    int N;
    cin >> N;

    map<int, int> counts;
    for (int i = 0; i < N; i++) {
        int a;
        cin >> a;
        counts[a]++;
    }

    int maxCount = 0;
    for (auto& p : counts) {
        maxCount = max(maxCount, p.second);
    }

    if (maxCount <= (N + 1) / 2) {
        cout << "YES" << endl;
    } else {
        cout << "NO" << endl;
    }

    return 0;
}
'''
    },

    # 25643: 문자열 탑 쌓기
    "25643": {
        "python": '''# 백준 25643: 문자열 탑 쌓기
# 문자열을 겹쳐서 쌓을 수 있는지 확인

def can_stack(s1, s2):
    # s1 위에 s2를 쌓을 수 있는지
    # 겹치는 부분이 동일해야 함
    M = len(s1)
    for overlap in range(1, M):
        if s1[-overlap:] == s2[:overlap]:
            return True
    return False

N, M = map(int, input().split())
strings = []
for _ in range(N):
    strings.append(input().strip())

# 순서대로 쌓을 수 있는지
can_build = True
for i in range(N - 1):
    if not can_stack(strings[i], strings[i + 1]):
        can_build = False
        break

print(1 if can_build else 0)
''',
        "java": '''import java.util.*;

// 백준 25643: 문자열 탑 쌓기
public class Main {
    static boolean canStack(String s1, String s2) {
        int M = s1.length();
        for (int overlap = 1; overlap < M; overlap++) {
            if (s1.substring(M - overlap).equals(s2.substring(0, overlap))) {
                return true;
            }
        }
        return false;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int M = sc.nextInt();

        String[] strings = new String[N];
        for (int i = 0; i < N; i++) {
            strings[i] = sc.next();
        }

        boolean canBuild = true;
        for (int i = 0; i < N - 1; i++) {
            if (!canStack(strings[i], strings[i + 1])) {
                canBuild = false;
                break;
            }
        }

        System.out.println(canBuild ? 1 : 0);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

// 백준 25643: 문자열 탑 쌓기
bool canStack(const string& s1, const string& s2) {
    int M = s1.length();
    for (int overlap = 1; overlap < M; overlap++) {
        if (s1.substr(M - overlap) == s2.substr(0, overlap)) {
            return true;
        }
    }
    return false;
}

int main() {
    int N, M;
    cin >> N >> M;

    string strings[100];
    for (int i = 0; i < N; i++) {
        cin >> strings[i];
    }

    bool canBuild = true;
    for (int i = 0; i < N - 1; i++) {
        if (!canStack(strings[i], strings[i + 1])) {
            canBuild = false;
            break;
        }
    }

    cout << (canBuild ? 1 : 0) << endl;

    return 0;
}
'''
    },

    # 17283: I am Groot
    "17283": {
        "python": '''# 백준 17283: I am Groot
# 나뭇가지 길이의 합 (중심줄기 제외)

L = int(input())
R = int(input())

total = 0
length = L * R // 100  # 첫 번째 가지 길이
branches = 2  # 첫 번째 가지 개수

while length > 5:
    total += length * branches
    branches *= 2
    length = length * R // 100

print(total)
''',
        "java": '''import java.util.Scanner;

// 백준 17283: I am Groot
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int L = sc.nextInt();
        int R = sc.nextInt();

        long total = 0;
        int length = L * R / 100;
        int branches = 2;

        while (length > 5) {
            total += (long) length * branches;
            branches *= 2;
            length = length * R / 100;
        }

        System.out.println(total);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 17283: I am Groot
int main() {
    int L, R;
    cin >> L >> R;

    long long total = 0;
    int length = L * R / 100;
    long long branches = 2;

    while (length > 5) {
        total += length * branches;
        branches *= 2;
        length = length * R / 100;
    }

    cout << total << endl;

    return 0;
}
'''
    },

    # 14174: Block Game
    "14174": {
        "python": '''# 백준 14174: Block Game
# 각 알파벳이 최소 몇 개 필요한지

N = int(input())

# 각 알파벳의 최대 필요 개수
max_count = [0] * 26

for _ in range(N):
    words = input().split()
    # 두 단어 중 각 알파벳이 더 많이 필요한 쪽
    count = [0] * 26
    for word in words:
        word_count = [0] * 26
        for c in word:
            word_count[ord(c) - ord('a')] += 1
        for i in range(26):
            count[i] = max(count[i], word_count[i])

    for i in range(26):
        max_count[i] = max(max_count[i], count[i])

# 모든 보드에 대해 필요한 최대 개수
for i in range(26):
    for c in max_count:
        pass

# 결과 출력
for c in max_count:
    print(c)
''',
        "java": '''import java.util.*;

// 백준 14174: Block Game
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        sc.nextLine();

        int[] maxCount = new int[26];

        for (int b = 0; b < N; b++) {
            String[] words = sc.nextLine().split(" ");
            int[] boardMax = new int[26];

            for (String word : words) {
                int[] wordCount = new int[26];
                for (char c : word.toCharArray()) {
                    wordCount[c - 'a']++;
                }
                for (int i = 0; i < 26; i++) {
                    boardMax[i] = Math.max(boardMax[i], wordCount[i]);
                }
            }

            for (int i = 0; i < 26; i++) {
                maxCount[i] += boardMax[i];
            }
        }

        for (int i = 0; i < 26; i++) {
            System.out.println(maxCount[i]);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <sstream>
#include <algorithm>
using namespace std;

// 백준 14174: Block Game
int main() {
    int N;
    cin >> N;
    cin.ignore();

    int maxCount[26] = {0};

    for (int b = 0; b < N; b++) {
        string line;
        getline(cin, line);
        stringstream ss(line);
        string word;

        int boardMax[26] = {0};

        while (ss >> word) {
            int wordCount[26] = {0};
            for (char c : word) {
                wordCount[c - 'a']++;
            }
            for (int i = 0; i < 26; i++) {
                boardMax[i] = max(boardMax[i], wordCount[i]);
            }
        }

        for (int i = 0; i < 26; i++) {
            maxCount[i] += boardMax[i];
        }
    }

    for (int i = 0; i < 26; i++) {
        cout << maxCount[i] << "\\n";
    }

    return 0;
}
'''
    },

    # 27445: Gorani Command
    "27445": {
        "python": '''# 백준 27445: Gorani Command
# 거리 정보로 위치 찾기

N, M = map(int, input().split())
distances = []
for i in range(N):
    distances.append(list(map(int, input().split())))

# 각 위치에서의 거리를 계산하여 일치하는 위치 찾기
for r in range(N):
    for c in range(M):
        match = True
        for i in range(N):
            expected_dist = abs(r - i)
            if distances[i][c] != expected_dist:
                match = False
                break
        if match:
            print(r + 1, c + 1)
            exit()
''',
        "java": '''import java.util.*;

// 백준 27445: Gorani Command
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int M = sc.nextInt();

        int[][] dist = new int[N][M];
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < M; j++) {
                dist[i][j] = sc.nextInt();
            }
        }

        for (int r = 0; r < N; r++) {
            for (int c = 0; c < M; c++) {
                boolean match = true;
                for (int i = 0; i < N; i++) {
                    if (dist[i][c] != Math.abs(r - i)) {
                        match = false;
                        break;
                    }
                }
                if (match) {
                    System.out.println((r + 1) + " " + (c + 1));
                    return;
                }
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <cmath>
using namespace std;

// 백준 27445: Gorani Command
int main() {
    int N, M;
    cin >> N >> M;

    int dist[100][100];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            cin >> dist[i][j];
        }
    }

    for (int r = 0; r < N; r++) {
        for (int c = 0; c < M; c++) {
            bool match = true;
            for (int i = 0; i < N; i++) {
                if (dist[i][c] != abs(r - i)) {
                    match = false;
                    break;
                }
            }
            if (match) {
                cout << r + 1 << " " << c + 1 << endl;
                return 0;
            }
        }
    }

    return 0;
}
'''
    },

    # 28115: 등차수열의 합
    "28115": {
        "python": '''# 백준 28115: 등차수열의 합
# A = B + C, B와 C가 등차수열이 되도록

N = int(input())
A = list(map(int, input().split()))

if N <= 2:
    # N이 2 이하면 항상 가능
    print("YES")
    B = [0] * N
    C = A[:]
    print(' '.join(map(str, B)))
    print(' '.join(map(str, C)))
else:
    # B: 0, d, 2d, 3d, ... (등차수열)
    # C = A - B 도 등차수열이어야 함
    # C: A[0]-0, A[1]-d, A[2]-2d, ...
    # C가 등차수열이려면: (A[1]-d) - (A[0]) = (A[2]-2d) - (A[1]-d)
    # A[1] - d - A[0] = A[2] - 2d - A[1] + d
    # A[1] - A[0] - d = A[2] - A[1] - d
    # A[1] - A[0] = A[2] - A[1]
    # 즉, A가 등차수열이면 가능

    # A가 등차수열인지 확인
    diff = A[1] - A[0]
    is_arithmetic = True
    for i in range(2, N):
        if A[i] - A[i-1] != diff:
            is_arithmetic = False
            break

    if is_arithmetic:
        print("YES")
        # B = 0, 0, 0, ... (공차 0)
        # C = A
        print(' '.join(['0'] * N))
        print(' '.join(map(str, A)))
    else:
        # 다른 방법 시도
        # B[i] = i, C[i] = A[i] - i
        # B는 등차수열 (공차 1)
        # C가 등차수열이려면: (A[1]-1) - (A[0]-0) = (A[2]-2) - (A[1]-1)
        # A[1] - A[0] - 1 = A[2] - A[1] - 1 -> A[1]-A[0] = A[2]-A[1]

        # 일반적인 접근: B와 C의 공차를 d_B, d_C라 하면
        # A[i] = B[i] + C[i] = (B[0] + i*d_B) + (C[0] + i*d_C)
        # A[i] = (B[0]+C[0]) + i*(d_B + d_C)
        # A[0] = B[0] + C[0], A[1] - A[0] = d_B + d_C, A[2] - A[1] = d_B + d_C, ...
        # 즉 A가 등차수열이어야 함

        print("NO")
''',
        "java": '''import java.util.*;

// 백준 28115: 등차수열의 합
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] A = new int[N];
        for (int i = 0; i < N; i++) {
            A[i] = sc.nextInt();
        }

        if (N <= 2) {
            System.out.println("YES");
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < N; i++) sb.append("0 ");
            System.out.println(sb.toString().trim());
            sb = new StringBuilder();
            for (int i = 0; i < N; i++) sb.append(A[i] + " ");
            System.out.println(sb.toString().trim());
        } else {
            int diff = A[1] - A[0];
            boolean isArithmetic = true;
            for (int i = 2; i < N; i++) {
                if (A[i] - A[i-1] != diff) {
                    isArithmetic = false;
                    break;
                }
            }

            if (isArithmetic) {
                System.out.println("YES");
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < N; i++) sb.append("0 ");
                System.out.println(sb.toString().trim());
                sb = new StringBuilder();
                for (int i = 0; i < N; i++) sb.append(A[i] + " ");
                System.out.println(sb.toString().trim());
            } else {
                System.out.println("NO");
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 28115: 등차수열의 합
int main() {
    int N;
    cin >> N;
    int A[100];
    for (int i = 0; i < N; i++) {
        cin >> A[i];
    }

    if (N <= 2) {
        cout << "YES" << endl;
        for (int i = 0; i < N; i++) cout << "0 ";
        cout << endl;
        for (int i = 0; i < N; i++) cout << A[i] << " ";
        cout << endl;
    } else {
        int diff = A[1] - A[0];
        bool isArithmetic = true;
        for (int i = 2; i < N; i++) {
            if (A[i] - A[i-1] != diff) {
                isArithmetic = false;
                break;
            }
        }

        if (isArithmetic) {
            cout << "YES" << endl;
            for (int i = 0; i < N; i++) cout << "0 ";
            cout << endl;
            for (int i = 0; i < N; i++) cout << A[i] << " ";
            cout << endl;
        } else {
            cout << "NO" << endl;
        }
    }

    return 0;
}
'''
    },
}


def main():
    # JSON 파일 읽기
    filepath = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 솔루션이 비어있고 difficulty가 easy인 문제들 찾기
    empty_easy_indices = []
    for i, prob in enumerate(data):
        if prob.get('solutions') == [] and prob.get('difficulty') == 'easy':
            empty_easy_indices.append(i)

    print(f"Total empty easy problems before update: {len(empty_easy_indices)}")

    # 솔루션 추가
    updated_count = 0
    for idx in empty_easy_indices:
        prob = data[idx]
        original_id = prob.get('original_id')

        if original_id in SOLUTIONS_PART3:
            sol = SOLUTIONS_PART3[original_id]
            data[idx]['solutions'] = [
                {"language": "python", "code": sol["python"]},
                {"language": "java", "code": sol["java"]},
                {"language": "cpp", "code": sol["cpp"]}
            ]
            updated_count += 1
            print(f"Updated: {original_id} - {prob.get('name')}")

    # 파일 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nTotal updated in this batch: {updated_count}")

    # 최종 카운트
    remaining = 0
    for prob in data:
        if prob.get('solutions') == [] and prob.get('difficulty') == 'easy':
            remaining += 1
    print(f"Remaining empty easy problems: {remaining}")


if __name__ == '__main__':
    main()
