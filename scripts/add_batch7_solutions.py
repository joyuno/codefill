#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배치 7: 문제 61-70 솔루션 추가"""

import json

# 새로운 솔루션들
new_solutions = {
    "20949": {
        "solutions": [
            {
                "language": "python",
                "code": '''# PPI 계산 후 정렬 - 77인치 모니터
import math
import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    monitors = []

    for i in range(1, N + 1):
        W, H = map(int, input().split())
        # PPI = sqrt(W^2 + H^2) / D, D = 77 (고정)
        # 비교를 위해 sqrt(W^2 + H^2)만 계산 (D가 같으므로)
        ppi_sq = W * W + H * H  # PPI^2 * D^2에 비례
        monitors.append((ppi_sq, i))

    # PPI 내림차순, 번호 오름차순
    monitors.sort(key=lambda x: (-x[0], x[1]))

    for _, idx in monitors:
        print(idx)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    vector<pair<long long, int>> monitors;

    for (int i = 1; i <= N; i++) {
        long long W, H;
        cin >> W >> H;
        long long ppiSq = W * W + H * H;
        monitors.push_back({ppiSq, i});
    }

    // PPI 내림차순, 번호 오름차순
    sort(monitors.begin(), monitors.end(), [](auto& a, auto& b) {
        if (a.first != b.first) return a.first > b.first;
        return a.second < b.second;
    });

    for (auto& m : monitors) {
        cout << m.second << "\\n";
    }

    return 0;
}
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

        long[][] monitors = new long[N][2];  // [ppiSq, index]

        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long W = Long.parseLong(st.nextToken());
            long H = Long.parseLong(st.nextToken());
            monitors[i][0] = W * W + H * H;
            monitors[i][1] = i + 1;
        }

        // PPI 내림차순, 번호 오름차순
        Arrays.sort(monitors, (a, b) -> {
            if (a[0] != b[0]) return Long.compare(b[0], a[0]);
            return Long.compare(a[1], b[1]);
        });

        StringBuilder sb = new StringBuilder();
        for (long[] m : monitors) {
            sb.append(m[1]).append("\\n");
        }
        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "28446": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 볼링공 관리 - 무게로 사물함 번호 찾기
import sys
input = sys.stdin.readline

def solve():
    M = int(input())
    weight_to_locker = {}
    results = []

    for _ in range(M):
        query = list(map(int, input().split()))
        if query[0] == 1:
            x, w = query[1], query[2]
            weight_to_locker[w] = x
        else:  # query[0] == 2
            w = query[1]
            results.append(weight_to_locker[w])

    print('\\n'.join(map(str, results)))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <unordered_map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int M;
    cin >> M;

    unordered_map<long long, int> weightToLocker;

    while (M--) {
        int op;
        cin >> op;

        if (op == 1) {
            int x;
            long long w;
            cin >> x >> w;
            weightToLocker[w] = x;
        } else {
            long long w;
            cin >> w;
            cout << weightToLocker[w] << "\\n";
        }
    }

    return 0;
}
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

        int M = Integer.parseInt(br.readLine().trim());
        Map<Long, Integer> weightToLocker = new HashMap<>();

        while (M-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int op = Integer.parseInt(st.nextToken());

            if (op == 1) {
                int x = Integer.parseInt(st.nextToken());
                long w = Long.parseLong(st.nextToken());
                weightToLocker.put(w, x);
            } else {
                long w = Long.parseLong(st.nextToken());
                sb.append(weightToLocker.get(w)).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "29719": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 불침번 경우의 수 - 브실이가 1번 이상 들어가는 경우
# 전체 경우의 수 M^N - 브실이가 없는 경우 (M-1)^N
import sys
input = sys.stdin.readline

MOD = 1000000007

def solve():
    N, M = map(int, input().split())

    # 전체 경우의 수: M^N
    # 브실이가 없는 경우: (M-1)^N
    total = pow(M, N, MOD)
    without_me = pow(M - 1, N, MOD)

    result = (total - without_me + MOD) % MOD
    print(result)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

const long long MOD = 1000000007;

long long power(long long base, long long exp, long long mod) {
    long long result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) result = result * base % mod;
        base = base * base % mod;
        exp >>= 1;
    }
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long N, M;
    cin >> N >> M;

    long long total = power(M, N, MOD);
    long long withoutMe = power(M - 1, N, MOD);

    long long result = (total - withoutMe + MOD) % MOD;
    cout << result << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    static final long MOD = 1000000007;

    static long power(long base, long exp, long mod) {
        long result = 1;
        base %= mod;
        while (exp > 0) {
            if ((exp & 1) == 1) result = result * base % mod;
            base = base * base % mod;
            exp >>= 1;
        }
        return result;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long N = sc.nextLong();
        long M = sc.nextLong();

        long total = power(M, N, MOD);
        long withoutMe = power(M - 1, N, MOD);

        long result = (total - withoutMe + MOD) % MOD;
        System.out.println(result);
    }
}
'''
            }
        ]
    },
    "27849": {
        "solutions": [
            {
                "language": "python",
                "code": '''# Bessie의 건초더미 먹기 - 시뮬레이션
import sys
input = sys.stdin.readline

def solve():
    line = input().split()
    N, T = int(line[0]), int(line[1])

    deliveries = []
    for _ in range(N):
        d, b = map(int, input().split())
        deliveries.append((d, b))

    total_eaten = 0
    hay = 0
    prev_day = 0

    for d, b in deliveries:
        # prev_day+1 ~ d-1 동안 먹기
        days_to_eat = d - 1 - prev_day
        eaten = min(hay, days_to_eat)
        total_eaten += eaten
        hay -= eaten

        # d일 아침에 배달
        hay += b

        # d일에 먹기
        if hay > 0:
            total_eaten += 1
            hay -= 1

        prev_day = d

    # 마지막 배달 이후 T일까지 먹기
    if prev_day < T:
        days_to_eat = T - prev_day
        eaten = min(hay, days_to_eat)
        total_eaten += eaten

    print(total_eaten)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long N, T;
    cin >> N >> T;

    vector<pair<long long, long long>> deliveries(N);
    for (int i = 0; i < N; i++) {
        cin >> deliveries[i].first >> deliveries[i].second;
    }

    long long totalEaten = 0;
    long long hay = 0;
    long long prevDay = 0;

    for (auto& [d, b] : deliveries) {
        // prevDay+1 ~ d-1 동안 먹기
        long long daysToEat = d - 1 - prevDay;
        long long eaten = min(hay, daysToEat);
        totalEaten += eaten;
        hay -= eaten;

        // d일 아침에 배달
        hay += b;

        // d일에 먹기
        if (hay > 0) {
            totalEaten++;
            hay--;
        }

        prevDay = d;
    }

    // 마지막 배달 이후 T일까지
    if (prevDay < T) {
        long long daysToEat = T - prevDay;
        long long eaten = min(hay, daysToEat);
        totalEaten += eaten;
    }

    cout << totalEaten << endl;

    return 0;
}
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
        long T = Long.parseLong(st.nextToken());

        long[][] deliveries = new long[N][2];
        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            deliveries[i][0] = Long.parseLong(st.nextToken());
            deliveries[i][1] = Long.parseLong(st.nextToken());
        }

        long totalEaten = 0;
        long hay = 0;
        long prevDay = 0;

        for (int i = 0; i < N; i++) {
            long d = deliveries[i][0];
            long b = deliveries[i][1];

            long daysToEat = d - 1 - prevDay;
            long eaten = Math.min(hay, daysToEat);
            totalEaten += eaten;
            hay -= eaten;

            hay += b;

            if (hay > 0) {
                totalEaten++;
                hay--;
            }

            prevDay = d;
        }

        if (prevDay < T) {
            long daysToEat = T - prevDay;
            long eaten = Math.min(hay, daysToEat);
            totalEaten += eaten;
        }

        System.out.println(totalEaten);
    }
}
'''
            }
        ]
    },
    "27966": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 트리의 모든 정점 쌍 거리 합 최소화
# 스타 그래프 (한 정점에서 다른 모든 정점으로 연결)가 최적
# 거리 합 = (N-1) * 1 + (N-1) * (N-2) / 2 * 2 = (N-1) + (N-1)(N-2) = (N-1)(N-1) = (N-1)^2
# 실제: 1에서 다른 모든 정점까지 거리 1: N-1 개
# 나머지 쌍들 (N-1)C2 개, 각 거리 2
# 총합 = (N-1) + 2 * (N-1)(N-2)/2 = (N-1) + (N-1)(N-2) = (N-1)(1 + N - 2) = (N-1)^2

def solve():
    N = int(input())

    # 최소 거리 합 = (N-1)^2
    min_sum = (N - 1) * (N - 1)
    print(min_sum)

    # 스타 그래프: 1번 정점을 중심으로
    for i in range(2, N + 1):
        print(1, i)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long N;
    cin >> N;

    // 최소 거리 합 = (N-1)^2
    cout << (N - 1) * (N - 1) << "\\n";

    // 스타 그래프: 1번 정점을 중심으로
    for (int i = 2; i <= N; i++) {
        cout << 1 << " " << i << "\\n";
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long N = sc.nextLong();

        // 최소 거리 합 = (N-1)^2
        System.out.println((N - 1) * (N - 1));

        // 스타 그래프
        StringBuilder sb = new StringBuilder();
        for (int i = 2; i <= N; i++) {
            sb.append(1).append(" ").append(i).append("\\n");
        }
        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "17028": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 소 정렬 - 맨 앞 소를 k칸 뒤로 보내기
import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    p = list(map(int, input().split()))

    moves = 0

    # p[0]이 주목받는 소
    # 목표: [1, 2, 3, ..., N]
    # 소 1이 맨 앞으로 올 때까지 반복

    while p[0] != 1:
        # 현재 맨 앞 소의 목표 위치 찾기
        cow = p[0]
        target_pos = cow - 1  # 0-indexed에서 소 cow가 있어야 할 위치

        if target_pos == 0:
            # 이미 올바른 위치
            break

        # cow를 target_pos로 이동
        # k = target_pos (k칸 뒤로)
        k = target_pos
        moves += k

        # p[0]을 p[k]로 이동
        temp = p[0]
        for i in range(k):
            p[i] = p[i + 1]
        p[k] = temp

    print(moves)

solve()
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

    int N;
    cin >> N;

    vector<int> p(N);
    for (int i = 0; i < N; i++) {
        cin >> p[i];
    }

    int moves = 0;

    while (p[0] != 1) {
        int cow = p[0];
        int targetPos = cow - 1;

        if (targetPos == 0) break;

        int k = targetPos;
        moves += k;

        int temp = p[0];
        for (int i = 0; i < k; i++) {
            p[i] = p[i + 1];
        }
        p[k] = temp;
    }

    cout << moves << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        int[] p = new int[N];
        for (int i = 0; i < N; i++) {
            p[i] = sc.nextInt();
        }

        int moves = 0;

        while (p[0] != 1) {
            int cow = p[0];
            int targetPos = cow - 1;

            if (targetPos == 0) break;

            int k = targetPos;
            moves += k;

            int temp = p[0];
            for (int i = 0; i < k; i++) {
                p[i] = p[i + 1];
            }
            p[k] = temp;
        }

        System.out.println(moves);
    }
}
'''
            }
        ]
    },
    "13270": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 피보나치 치킨 세트 - 최소/최대 치킨 수
# 세트: (2,1), (3,2), (5,3), (8,5), (13,8), ...
# 사람:닭 비율이 높을수록 닭이 적게 옴
# 최소: 2인 1닭만 사용 -> N/2 (N이 짝수일 때)
# 최대: 3인 2닭만 사용 -> N/3 * 2 (N이 3의 배수일 때)

def solve():
    N = int(input())

    # 2인 1닭, 3인 2닭만 조합
    # 2a + 3b = N (a >= 0, b >= 0)
    # 치킨 수 = a + 2b

    min_chicken = float('inf')
    max_chicken = 0

    # a = (N - 3b) / 2
    for b in range(N // 3 + 1):
        remaining = N - 3 * b
        if remaining >= 0 and remaining % 2 == 0:
            a = remaining // 2
            chicken = a + 2 * b
            min_chicken = min(min_chicken, chicken)
            max_chicken = max(max_chicken, chicken)

    print(min_chicken, max_chicken)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    int minChicken = INT_MAX;
    int maxChicken = 0;

    // 2a + 3b = N
    for (int b = 0; b <= N / 3; b++) {
        int remaining = N - 3 * b;
        if (remaining >= 0 && remaining % 2 == 0) {
            int a = remaining / 2;
            int chicken = a + 2 * b;
            minChicken = min(minChicken, chicken);
            maxChicken = max(maxChicken, chicken);
        }
    }

    cout << minChicken << " " << maxChicken << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        int minChicken = Integer.MAX_VALUE;
        int maxChicken = 0;

        // 2a + 3b = N
        for (int b = 0; b <= N / 3; b++) {
            int remaining = N - 3 * b;
            if (remaining >= 0 && remaining % 2 == 0) {
                int a = remaining / 2;
                int chicken = a + 2 * b;
                minChicken = Math.min(minChicken, chicken);
                maxChicken = Math.max(maxChicken, chicken);
            }
        }

        System.out.println(minChicken + " " + maxChicken);
    }
}
'''
            }
        ]
    },
    "2223": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 금화 모으기 - 몬스터 피하면서 최대 금화 수집
import sys
input = sys.stdin.readline

def solve():
    line = input().split()
    t, x, m = int(line[0]), int(line[1]), int(line[2])

    monsters = []
    for _ in range(m):
        d, s = map(int, input().split())
        monsters.append((d, s))

    if m == 0:
        # 몬스터가 없으면 모든 시간 금화 수집
        print(t * x)
        return

    # 가장 빨리 도착하는 몬스터 기준
    # d/s 단위 시간 후 도착
    min_arrival = float('inf')
    for d, s in monsters:
        arrival = d // s  # 몬스터가 도착하는 시간
        min_arrival = min(min_arrival, arrival)

    # 연속으로 min_arrival - 1 시간 금화 수집 가능
    # 그 후 1 시간 쉬면 몬스터 원위치

    # 패턴: (min_arrival - 1) 수집 + 1 휴식
    if min_arrival <= 1:
        # 수집 불가
        print(0)
        return

    collect_time = min_arrival - 1
    cycle = collect_time + 1

    # t 시간 동안
    full_cycles = t // cycle
    remaining = t % cycle

    # 남은 시간에서 수집 가능한 시간
    extra_collect = min(remaining, collect_time)

    total = (full_cycles * collect_time + extra_collect) * x
    print(total)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long t, x, m;
    cin >> t >> x >> m;

    if (m == 0) {
        cout << t * x << endl;
        return 0;
    }

    long long minArrival = LLONG_MAX;
    for (int i = 0; i < m; i++) {
        long long d, s;
        cin >> d >> s;
        minArrival = min(minArrival, d / s);
    }

    if (minArrival <= 1) {
        cout << 0 << endl;
        return 0;
    }

    long long collectTime = minArrival - 1;
    long long cycle = collectTime + 1;

    long long fullCycles = t / cycle;
    long long remaining = t % cycle;
    long long extraCollect = min(remaining, collectTime);

    long long total = (fullCycles * collectTime + extraCollect) * x;
    cout << total << endl;

    return 0;
}
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

        long t = Long.parseLong(st.nextToken());
        long x = Long.parseLong(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        if (m == 0) {
            System.out.println(t * x);
            return;
        }

        long minArrival = Long.MAX_VALUE;
        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            long d = Long.parseLong(st.nextToken());
            long s = Long.parseLong(st.nextToken());
            minArrival = Math.min(minArrival, d / s);
        }

        if (minArrival <= 1) {
            System.out.println(0);
            return;
        }

        long collectTime = minArrival - 1;
        long cycle = collectTime + 1;

        long fullCycles = t / cycle;
        long remaining = t % cycle;
        long extraCollect = Math.min(remaining, collectTime);

        long total = (fullCycles * collectTime + extraCollect) * x;
        System.out.println(total);
    }
}
'''
            }
        ]
    },
    "25344": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 행성 정렬 주기 - LCM 계산
import math
import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    T = list(map(int, input().split()))

    # 모든 T의 LCM
    result = T[0]
    for i in range(1, len(T)):
        result = result * T[i] // math.gcd(result, T[i])

    print(result)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
using namespace std;

long long gcd(long long a, long long b) {
    while (b) {
        a %= b;
        swap(a, b);
    }
    return a;
}

long long lcm(long long a, long long b) {
    return a / gcd(a, b) * b;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    long long result = 1;
    for (int i = 0; i < N - 2; i++) {
        long long T;
        cin >> T;
        result = lcm(result, T);
    }

    cout << result << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    static long gcd(long a, long b) {
        while (b != 0) {
            long temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    static long lcm(long a, long b) {
        return a / gcd(a, b) * b;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        long result = 1;
        for (int i = 0; i < N - 2; i++) {
            long T = sc.nextLong();
            result = lcm(result, T);
        }

        System.out.println(result);
    }
}
'''
            }
        ]
    },
    "17359": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 전구 묶음 배치 - 상태 변경 횟수 최소화
# N이 작으므로 (N <= 10) 순열 탐색 가능
from itertools import permutations

def count_changes(s):
    """문자열에서 상태 변경 횟수 계산"""
    changes = 0
    for i in range(1, len(s)):
        if s[i] != s[i-1]:
            changes += 1
    return changes

def solve():
    N = int(input())
    bulbs = []
    for _ in range(N):
        bulbs.append(input().strip())

    if N == 1:
        print(count_changes(bulbs[0]))
        return

    min_changes = float('inf')

    # 모든 순열 탐색
    for perm in permutations(range(N)):
        combined = ''.join(bulbs[i] for i in perm)
        changes = count_changes(combined)
        min_changes = min(min_changes, changes)

    print(min_changes)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <climits>
using namespace std;

int countChanges(const string& s) {
    int changes = 0;
    for (int i = 1; i < s.length(); i++) {
        if (s[i] != s[i-1]) changes++;
    }
    return changes;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    vector<string> bulbs(N);
    for (int i = 0; i < N; i++) {
        cin >> bulbs[i];
    }

    vector<int> perm(N);
    for (int i = 0; i < N; i++) perm[i] = i;

    int minChanges = INT_MAX;

    do {
        string combined;
        for (int i : perm) {
            combined += bulbs[i];
        }
        minChanges = min(minChanges, countChanges(combined));
    } while (next_permutation(perm.begin(), perm.end()));

    cout << minChanges << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;

public class Main {
    static String[] bulbs;
    static int N;
    static int minChanges = Integer.MAX_VALUE;
    static boolean[] used;
    static int[] order;

    static int countChanges(String s) {
        int changes = 0;
        for (int i = 1; i < s.length(); i++) {
            if (s.charAt(i) != s.charAt(i-1)) changes++;
        }
        return changes;
    }

    static void permute(int depth) {
        if (depth == N) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < N; i++) {
                sb.append(bulbs[order[i]]);
            }
            minChanges = Math.min(minChanges, countChanges(sb.toString()));
            return;
        }

        for (int i = 0; i < N; i++) {
            if (!used[i]) {
                used[i] = true;
                order[depth] = i;
                permute(depth + 1);
                used[i] = false;
            }
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        N = sc.nextInt();

        bulbs = new String[N];
        for (int i = 0; i < N; i++) {
            bulbs[i] = sc.next();
        }

        used = new boolean[N];
        order = new int[N];
        permute(0);

        System.out.println(minChanges);
    }
}
'''
            }
        ]
    }
}

# 기존 파일 읽기
with open('data/baekjoon/baek_medium.json', 'r', encoding='utf-8') as f:
    medium_data = json.load(f)

print(f"기존 솔루션 수: {len(medium_data)}")

# 새 솔루션 추가
added = 0
for pid, data in new_solutions.items():
    if pid not in medium_data:
        medium_data[pid] = data
        added += 1
    else:
        print(f"이미 존재: {pid}")

# 파일 저장
with open('data/baekjoon/baek_medium.json', 'w', encoding='utf-8') as f:
    json.dump(medium_data, f, ensure_ascii=False, indent=2)

print(f"새로 추가된 솔루션: {added}개")
print(f"총 솔루션 수: {len(medium_data)}개")
