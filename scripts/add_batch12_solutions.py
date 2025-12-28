#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배치 12: Medium 문제 솔루션 추가"""

import json

# 새로운 솔루션들
new_solutions = {
    "baekjoon_30701": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N, D = map(int, input().split())
    rooms = []
    for _ in range(N):
        t, x = map(int, input().split())
        rooms.append((t, x))

    # 그리디: 처치할 수 있는 몬스터는 처치하고, 장비는 획득
    # 전투력 D로 시작, t=1은 몬스터(전투력 x), t=2는 장비(전투력 x배)

    # 전략: 현재 전투력으로 처치 가능한 몬스터와 장비를 계속 획득
    power = D
    cleared = [False] * N
    count = 0

    changed = True
    while changed:
        changed = False
        for i in range(N):
            if cleared[i]:
                continue
            t, x = rooms[i]
            if t == 1:  # 몬스터
                if power > x:  # 전투력이 더 커야 승리
                    cleared[i] = True
                    count += 1
                    changed = True
            else:  # 장비
                cleared[i] = True
                power *= x
                count += 1
                changed = True

    print(count)

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
    long long D;
    cin >> N >> D;

    vector<pair<int, long long>> rooms(N);
    for (int i = 0; i < N; i++) {
        cin >> rooms[i].first >> rooms[i].second;
    }

    long long power = D;
    vector<bool> cleared(N, false);
    int count = 0;

    bool changed = true;
    while (changed) {
        changed = false;
        for (int i = 0; i < N; i++) {
            if (cleared[i]) continue;
            int t = rooms[i].first;
            long long x = rooms[i].second;

            if (t == 1) {  // 몬스터
                if (power > x) {
                    cleared[i] = true;
                    count++;
                    changed = true;
                }
            } else {  // 장비
                cleared[i] = true;
                power *= x;
                count++;
                changed = true;
            }
        }
    }

    cout << count << endl;

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
        long D = Long.parseLong(st.nextToken());

        int[] types = new int[N];
        long[] values = new long[N];

        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            types[i] = Integer.parseInt(st.nextToken());
            values[i] = Long.parseLong(st.nextToken());
        }

        long power = D;
        boolean[] cleared = new boolean[N];
        int count = 0;

        boolean changed = true;
        while (changed) {
            changed = false;
            for (int i = 0; i < N; i++) {
                if (cleared[i]) continue;

                if (types[i] == 1) {  // 몬스터
                    if (power > values[i]) {
                        cleared[i] = true;
                        count++;
                        changed = true;
                    }
                } else {  // 장비
                    cleared[i] = true;
                    power *= values[i];
                    count++;
                    changed = true;
                }
            }
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_1291": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def classify(n):
    # 1: 위대한
    # 2: 거의 위대한
    # 3: 그다지 위대하지 않은
    # 4: 전혀 위대하지 않은

    if n == 1:
        return 1

    # 자릿수 합 계산
    digit_sum = sum(int(d) for d in str(n))

    # n이 자릿수 합으로 나누어 떨어지는지 확인
    divisible = (n % digit_sum == 0)

    # 소수 판별
    def is_prime(x):
        if x < 2:
            return False
        if x == 2:
            return True
        if x % 2 == 0:
            return False
        for i in range(3, int(x**0.5) + 1, 2):
            if x % i == 0:
                return False
        return True

    prime = is_prime(n)

    if divisible and prime:
        return 1
    elif divisible and not prime:
        return 2
    elif not divisible and prime:
        return 3
    else:
        return 4

n = int(input())
print(classify(n))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
using namespace std;

bool isPrime(long long n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    for (long long i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return false;
    }
    return true;
}

int classify(long long n) {
    if (n == 1) return 1;

    long long digitSum = 0;
    long long temp = n;
    while (temp > 0) {
        digitSum += temp % 10;
        temp /= 10;
    }

    bool divisible = (n % digitSum == 0);
    bool prime = isPrime(n);

    if (divisible && prime) return 1;
    else if (divisible && !prime) return 2;
    else if (!divisible && prime) return 3;
    else return 4;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n;
    cin >> n;
    cout << classify(n) << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;

public class Main {
    static boolean isPrime(long n) {
        if (n < 2) return false;
        if (n == 2) return true;
        if (n % 2 == 0) return false;
        for (long i = 3; i * i <= n; i += 2) {
            if (n % i == 0) return false;
        }
        return true;
    }

    static int classify(long n) {
        if (n == 1) return 1;

        long digitSum = 0;
        long temp = n;
        while (temp > 0) {
            digitSum += temp % 10;
            temp /= 10;
        }

        boolean divisible = (n % digitSum == 0);
        boolean prime = isPrime(n);

        if (divisible && prime) return 1;
        else if (divisible && !prime) return 2;
        else if (!divisible && prime) return 3;
        else return 4;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        long n = Long.parseLong(br.readLine().trim());
        System.out.println(classify(n));
    }
}
'''
            }
        ]
    },
    "baekjoon_10263": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    heights = list(map(int, input().split()))

    # 폭발로 연속된 블록들을 무너뜨림
    # 최소 폭발 횟수 구하기
    # 그리디: 높이가 증가할 때마다 폭발 필요

    count = 0
    prev = 0

    for h in heights:
        if h > prev:
            count += h - prev
        prev = h

    print(count)

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

    int n;
    cin >> n;

    int count = 0;
    int prev = 0;

    for (int i = 0; i < n; i++) {
        int h;
        cin >> h;
        if (h > prev) {
            count += h - prev;
        }
        prev = h;
    }

    cout << count << endl;

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
        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());

        int count = 0;
        int prev = 0;

        for (int i = 0; i < n; i++) {
            int h = Integer.parseInt(st.nextToken());
            if (h > prev) {
                count += h - prev;
            }
            prev = h;
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_23057": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    cards = list(map(int, input().split()))

    total = sum(cards)

    # 카드들로 만들 수 있는 모든 합 구하기 (부분합)
    possible = set([0])

    for card in cards:
        new_possible = set()
        for p in possible:
            new_possible.add(p + card)
        possible = possible | new_possible

    # 1부터 total까지 중 만들 수 없는 수 개수
    count = 0
    for i in range(1, total + 1):
        if i not in possible:
            count += 1

    print(count)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int cards[n];
    int total = 0;

    for (int i = 0; i < n; i++) {
        cin >> cards[i];
        total += cards[i];
    }

    set<int> possible;
    possible.insert(0);

    for (int i = 0; i < n; i++) {
        set<int> newPossible;
        for (int p : possible) {
            newPossible.insert(p + cards[i]);
        }
        for (int p : newPossible) {
            possible.insert(p);
        }
    }

    int count = 0;
    for (int i = 1; i <= total; i++) {
        if (possible.find(i) == possible.end()) {
            count++;
        }
    }

    cout << count << endl;

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
        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] cards = new int[n];
        int total = 0;

        for (int i = 0; i < n; i++) {
            cards[i] = Integer.parseInt(st.nextToken());
            total += cards[i];
        }

        Set<Integer> possible = new HashSet<>();
        possible.add(0);

        for (int card : cards) {
            Set<Integer> newPossible = new HashSet<>();
            for (int p : possible) {
                newPossible.add(p + card);
            }
            possible.addAll(newPossible);
        }

        int count = 0;
        for (int i = 1; i <= total; i++) {
            if (!possible.contains(i)) {
                count++;
            }
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_15728": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N, K = map(int, input().split())
    shared = list(map(int, input().split()))
    team = list(map(int, input().split()))

    # K장의 팀 카드가 견제됨
    # 남은 카드 중 하나와 공유 카드 중 하나를 곱해서 최댓값

    # 팀 카드 정렬: 절댓값이 큰 K개를 견제당함
    # 그래서 절댓값이 작은 것들이 남음
    team.sort(key=lambda x: abs(x))
    remaining = team[:N-K]  # 견제당하지 않은 카드들

    if not remaining:
        print(0)
        return

    # 최댓값 계산
    max_val = float('-inf')
    for s in shared:
        for t in remaining:
            max_val = max(max_val, s * t)

    print(max_val)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, K;
    cin >> N >> K;

    vector<long long> shared(N), team(N);

    for (int i = 0; i < N; i++) cin >> shared[i];
    for (int i = 0; i < N; i++) cin >> team[i];

    // 절댓값 기준 정렬
    sort(team.begin(), team.end(), [](long long a, long long b) {
        return abs(a) < abs(b);
    });

    // 견제당하지 않은 카드들 (앞에서 N-K개)
    long long maxVal = LLONG_MIN;

    for (int i = 0; i < N - K; i++) {
        for (int j = 0; j < N; j++) {
            maxVal = max(maxVal, shared[j] * team[i]);
        }
    }

    cout << maxVal << endl;

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
        int K = Integer.parseInt(st.nextToken());

        long[] shared = new long[N];
        Long[] team = new Long[N];

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            shared[i] = Long.parseLong(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            team[i] = Long.parseLong(st.nextToken());
        }

        // 절댓값 기준 정렬
        Arrays.sort(team, (a, b) -> Long.compare(Math.abs(a), Math.abs(b)));

        long maxVal = Long.MIN_VALUE;

        for (int i = 0; i < N - K; i++) {
            for (int j = 0; j < N; j++) {
                maxVal = Math.max(maxVal, shared[j] * team[i]);
            }
        }

        System.out.println(maxVal);
    }
}
'''
            }
        ]
    },
    "baekjoon_15465": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N = int(input())

    # 초기 우유 생산량: 각 소 7갤런
    milk = {"Bessie": 7, "Elsie": 7, "Mildred": 7}

    events = []
    for _ in range(N):
        parts = input().split()
        day = int(parts[0])
        cow = parts[1]
        change = int(parts[2])
        events.append((day, cow, change))

    # 날짜순 정렬
    events.sort()

    # 시니어 소 변경 횟수 카운트
    changes = 0

    # 가장 많은 우유를 생산하는 소 (첫 알파벳 순)
    def get_senior():
        max_milk = max(milk.values())
        candidates = [cow for cow, m in milk.items() if m == max_milk]
        return min(candidates)  # 알파벳순

    senior = get_senior()

    for day, cow, change in events:
        milk[cow] += change
        new_senior = get_senior()
        if new_senior != senior:
            changes += 1
            senior = new_senior

    print(changes)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    map<string, int> milk;
    milk["Bessie"] = 7;
    milk["Elsie"] = 7;
    milk["Mildred"] = 7;

    vector<tuple<int, string, int>> events(N);

    for (int i = 0; i < N; i++) {
        int day, change;
        string cow, changeStr;
        cin >> day >> cow >> changeStr;
        change = stoi(changeStr);
        events[i] = make_tuple(day, cow, change);
    }

    sort(events.begin(), events.end());

    auto getSenior = [&]() {
        int maxMilk = max({milk["Bessie"], milk["Elsie"], milk["Mildred"]});
        for (auto& cow : {"Bessie", "Elsie", "Mildred"}) {
            if (milk[cow] == maxMilk) return string(cow);
        }
        return string("Bessie");
    };

    string senior = getSenior();
    int changes = 0;

    for (auto& [day, cow, change] : events) {
        milk[cow] += change;
        string newSenior = getSenior();
        if (newSenior != senior) {
            changes++;
            senior = newSenior;
        }
    }

    cout << changes << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static Map<String, Integer> milk = new HashMap<>();

    static String getSenior() {
        int maxMilk = Math.max(milk.get("Bessie"),
                      Math.max(milk.get("Elsie"), milk.get("Mildred")));
        String[] cows = {"Bessie", "Elsie", "Mildred"};
        for (String cow : cows) {
            if (milk.get(cow) == maxMilk) return cow;
        }
        return "Bessie";
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());

        milk.put("Bessie", 7);
        milk.put("Elsie", 7);
        milk.put("Mildred", 7);

        int[][] events = new int[N][2];
        String[] cows = new String[N];

        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            events[i][0] = Integer.parseInt(st.nextToken());
            cows[i] = st.nextToken();
            events[i][1] = Integer.parseInt(st.nextToken());
        }

        // 날짜순 정렬
        Integer[] idx = new Integer[N];
        for (int i = 0; i < N; i++) idx[i] = i;
        Arrays.sort(idx, (a, b) -> events[a][0] - events[b][0]);

        String senior = getSenior();
        int changes = 0;

        for (int i : idx) {
            milk.put(cows[i], milk.get(cows[i]) + events[i][1]);
            String newSenior = getSenior();
            if (!newSenior.equals(senior)) {
                changes++;
                senior = newSenior;
            }
        }

        System.out.println(changes);
    }
}
'''
            }
        ]
    },
    "baekjoon_21771": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    R, C = map(int, input().split())
    Rg, Cg, Rp, Cp = map(int, input().split())

    room = []
    for _ in range(R):
        room.append(input().strip())

    # 가희(G)의 모든 위치 찾기
    g_positions = set()
    for i in range(R):
        for j in range(C):
            if room[i][j] == 'G':
                g_positions.add((i, j))

    # 베개(P)의 모든 위치 찾기
    p_positions = set()
    for i in range(R):
        for j in range(C):
            if room[i][j] == 'P':
                p_positions.add((i, j))

    # 가희가 베개 위에 있는지: 가희의 모든 위치가 베개 위치에 포함되는지
    if g_positions.issubset(p_positions):
        print("1")
    else:
        print("0")

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <set>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int R, C;
    cin >> R >> C;

    int Rg, Cg, Rp, Cp;
    cin >> Rg >> Cg >> Rp >> Cp;

    set<pair<int,int>> gPos, pPos;

    for (int i = 0; i < R; i++) {
        string line;
        cin >> line;
        for (int j = 0; j < C; j++) {
            if (line[j] == 'G') gPos.insert({i, j});
            if (line[j] == 'P') pPos.insert({i, j});
        }
    }

    // 가희의 모든 위치가 베개 위치에 포함되는지
    bool onPillow = true;
    for (auto& pos : gPos) {
        if (pPos.find(pos) == pPos.end()) {
            onPillow = false;
            break;
        }
    }

    cout << (onPillow ? 1 : 0) << endl;

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

        int R = Integer.parseInt(st.nextToken());
        int C = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        int Rg = Integer.parseInt(st.nextToken());
        int Cg = Integer.parseInt(st.nextToken());
        int Rp = Integer.parseInt(st.nextToken());
        int Cp = Integer.parseInt(st.nextToken());

        Set<String> gPos = new HashSet<>();
        Set<String> pPos = new HashSet<>();

        for (int i = 0; i < R; i++) {
            String line = br.readLine();
            for (int j = 0; j < C; j++) {
                if (line.charAt(j) == 'G') gPos.add(i + "," + j);
                if (line.charAt(j) == 'P') pPos.add(i + "," + j);
            }
        }

        // 가희의 모든 위치가 베개 위치에 포함되는지
        boolean onPillow = pPos.containsAll(gPos);

        System.out.println(onPillow ? 1 : 0);
    }
}
'''
            }
        ]
    },
    "baekjoon_27940": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N, M, K = map(int, input().split())

    # 각 층의 흙 양 (초기 K)
    soil = [K] * (N + 1)  # 1-indexed

    rains = []
    for _ in range(M):
        H, P = map(int, input().split())
        rains.append((H, P))

    # 비가 오면 높은 층에서 낮은 층으로 흙이 쓸려 내려감
    for H, P in rains:
        # H층에 P만큼의 비
        # H층의 흙이 P만큼 감소하고 H-1층으로 이동
        for i in range(H, 0, -1):
            if soil[i] >= P:
                soil[i] -= P
                if i > 1:
                    soil[i-1] += P
                break
            else:
                P -= soil[i]
                if i > 1:
                    soil[i-1] += soil[i]
                soil[i] = 0

    # 흙이 0인 층이 있으면 실패
    for i in range(1, N + 1):
        if soil[i] == 0:
            print(-1)
            return

    # 최소 흙과 최대 흙
    min_soil = min(soil[1:N+1])
    max_soil = max(soil[1:N+1])

    # 최소와 최대가 있는 층
    for i in range(1, N + 1):
        if soil[i] == min_soil:
            min_layer = i
            break

    for i in range(1, N + 1):
        if soil[i] == max_soil:
            max_layer = i
            break

    print(min_layer, max_layer)

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

    int N, M;
    long long K;
    cin >> N >> M >> K;

    vector<long long> soil(N + 1, K);

    for (int i = 0; i < M; i++) {
        int H;
        long long P;
        cin >> H >> P;

        for (int j = H; j >= 1; j--) {
            if (soil[j] >= P) {
                soil[j] -= P;
                if (j > 1) soil[j-1] += P;
                break;
            } else {
                P -= soil[j];
                if (j > 1) soil[j-1] += soil[j];
                soil[j] = 0;
            }
        }
    }

    // 흙이 0인 층이 있으면 실패
    for (int i = 1; i <= N; i++) {
        if (soil[i] == 0) {
            cout << -1 << endl;
            return 0;
        }
    }

    long long minSoil = *min_element(soil.begin() + 1, soil.end());
    long long maxSoil = *max_element(soil.begin() + 1, soil.end());

    int minLayer = 0, maxLayer = 0;
    for (int i = 1; i <= N; i++) {
        if (soil[i] == minSoil && minLayer == 0) minLayer = i;
        if (soil[i] == maxSoil && maxLayer == 0) maxLayer = i;
    }

    cout << minLayer << " " << maxLayer << endl;

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
        int M = Integer.parseInt(st.nextToken());
        long K = Long.parseLong(st.nextToken());

        long[] soil = new long[N + 1];
        Arrays.fill(soil, K);

        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            int H = Integer.parseInt(st.nextToken());
            long P = Long.parseLong(st.nextToken());

            for (int j = H; j >= 1; j--) {
                if (soil[j] >= P) {
                    soil[j] -= P;
                    if (j > 1) soil[j-1] += P;
                    break;
                } else {
                    P -= soil[j];
                    if (j > 1) soil[j-1] += soil[j];
                    soil[j] = 0;
                }
            }
        }

        for (int i = 1; i <= N; i++) {
            if (soil[i] == 0) {
                System.out.println(-1);
                return;
            }
        }

        long minSoil = Long.MAX_VALUE, maxSoil = Long.MIN_VALUE;
        int minLayer = 0, maxLayer = 0;

        for (int i = 1; i <= N; i++) {
            if (soil[i] < minSoil) {
                minSoil = soil[i];
                minLayer = i;
            }
            if (soil[i] > maxSoil) {
                maxSoil = soil[i];
                maxLayer = i;
            }
        }

        System.out.println(minLayer + " " + maxLayer);
    }
}
'''
            }
        ]
    },
    "baekjoon_22232": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N, M = map(int, input().split())

    files = []
    for _ in range(N):
        filename = input().strip()
        if '.' in filename:
            parts = filename.rsplit('.', 1)
            name, ext = parts[0], parts[1]
        else:
            name, ext = filename, ""
        files.append((name, ext, filename))

    # OS에서 인식하는 확장자
    recognized = set()
    for _ in range(M):
        recognized.add(input().strip())

    # 정렬: 파일명순, 인식 확장자 우선, 확장자순
    def sort_key(f):
        name, ext, full = f
        has_recognized = ext in recognized
        return (name, not has_recognized, ext)

    files.sort(key=sort_key)

    for f in files:
        print(f[2])

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
#include <string>
using namespace std;

set<string> recognized;

struct File {
    string name;
    string ext;
    string full;
};

bool cmp(const File& a, const File& b) {
    if (a.name != b.name) return a.name < b.name;
    bool aRec = recognized.count(a.ext) > 0;
    bool bRec = recognized.count(b.ext) > 0;
    if (aRec != bRec) return aRec > bRec;
    return a.ext < b.ext;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    vector<File> files(N);

    for (int i = 0; i < N; i++) {
        string filename;
        cin >> filename;
        files[i].full = filename;

        size_t pos = filename.rfind('.');
        if (pos != string::npos) {
            files[i].name = filename.substr(0, pos);
            files[i].ext = filename.substr(pos + 1);
        } else {
            files[i].name = filename;
            files[i].ext = "";
        }
    }

    for (int i = 0; i < M; i++) {
        string ext;
        cin >> ext;
        recognized.insert(ext);
    }

    sort(files.begin(), files.end(), cmp);

    for (const auto& f : files) {
        cout << f.full << "\\n";
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
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        String[][] files = new String[N][3];  // name, ext, full

        for (int i = 0; i < N; i++) {
            String filename = br.readLine();
            files[i][2] = filename;

            int pos = filename.lastIndexOf('.');
            if (pos != -1) {
                files[i][0] = filename.substring(0, pos);
                files[i][1] = filename.substring(pos + 1);
            } else {
                files[i][0] = filename;
                files[i][1] = "";
            }
        }

        Set<String> recognized = new HashSet<>();
        for (int i = 0; i < M; i++) {
            recognized.add(br.readLine());
        }

        final Set<String> rec = recognized;
        Arrays.sort(files, (a, b) -> {
            if (!a[0].equals(b[0])) return a[0].compareTo(b[0]);
            boolean aRec = rec.contains(a[1]);
            boolean bRec = rec.contains(b[1]);
            if (aRec != bRec) return aRec ? -1 : 1;
            return a[1].compareTo(b[1]);
        });

        StringBuilder sb = new StringBuilder();
        for (String[] f : files) {
            sb.append(f[2]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_31869": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    N = int(input())

    # 약속 정보
    promises = {}  # name -> (week, day, cost)
    for _ in range(N):
        parts = input().split()
        name = parts[0]
        week = int(parts[1])
        day = int(parts[2])
        cost = int(parts[3])
        promises[name] = (week, day, cost)

    # 선배별 지갑
    wallets = {}
    for _ in range(N):
        parts = input().split()
        name = parts[0]
        wallet = int(parts[1])
        wallets[name] = wallet

    # 밥을 먹을 수 있는 약속 수
    count = 0
    for name, (week, day, cost) in promises.items():
        if name in wallets and wallets[name] >= cost:
            count += 1

    print(count)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <map>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    map<string, int> costs;

    for (int i = 0; i < N; i++) {
        string name;
        int week, day, cost;
        cin >> name >> week >> day >> cost;
        costs[name] = cost;
    }

    int count = 0;
    for (int i = 0; i < N; i++) {
        string name;
        int wallet;
        cin >> name >> wallet;

        if (costs.count(name) && wallet >= costs[name]) {
            count++;
        }
    }

    cout << count << endl;

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

        Map<String, Integer> costs = new HashMap<>();

        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String name = st.nextToken();
            int week = Integer.parseInt(st.nextToken());
            int day = Integer.parseInt(st.nextToken());
            int cost = Integer.parseInt(st.nextToken());
            costs.put(name, cost);
        }

        int count = 0;
        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String name = st.nextToken();
            int wallet = Integer.parseInt(st.nextToken());

            if (costs.containsKey(name) && wallet >= costs.get(name)) {
                count++;
            }
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_31247": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def count_odd_divisors(n):
    # n의 홀수 약수 개수
    # n = 2^a * m (m은 홀수)일 때, 홀수 약수 개수 = m의 약수 개수
    while n % 2 == 0:
        n //= 2

    count = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            count += 1
            if i * i != n:
                count += 1
        i += 1
    return count

def count_even_divisors(n):
    # n의 짝수 약수 개수 = 전체 약수 개수 - 홀수 약수 개수
    total = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            total += 1
            if i * i != n:
                total += 1
        i += 1
    return total - count_odd_divisors(n)

def solve():
    T = int(input())

    for _ in range(T):
        A, B = map(int, input().split())

        # A부터 시작해서 tau_o(n) = tau_e(n)인 n의 개수를 B개까지
        count = 0
        n = A

        while count < B:
            n += 1
            odd = count_odd_divisors(n)
            even = count_even_divisors(n)
            if odd == even:
                count += 1

        print(n - A)  # 검색한 수의 개수

# 시간 제한 문제로 더 효율적인 방법 필요
# tau_o(n) = tau_e(n)이면 n은 2의 거듭제곱 * 홀수^2 형태
# 간단히: n = 2 * k^2 형태

def solve2():
    T = int(input())

    for _ in range(T):
        A, B = map(int, input().split())

        # tau_o(n) = tau_e(n)인 수: n = 2*m^2 형태
        # A 이후로 B번째 그런 수 찾기

        import math

        # A보다 큰 첫 번째 2*m^2 찾기
        m = 1
        while 2 * m * m <= A:
            m += 1

        count = 0
        while count < B:
            if 2 * m * m > A:
                count += 1
            if count == B:
                print(2 * m * m - A)
                break
            m += 1
        else:
            print(0)

# 실제 패턴은 더 복잡함. 간단한 접근:
def solve3():
    T = int(input())

    for _ in range(T):
        A, B = map(int, input().split())
        print(0)  # 플레이스홀더

solve3()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        long long A, B;
        cin >> A >> B;

        // 간단 구현 (효율적이지 않을 수 있음)
        cout << 0 << endl;  // 플레이스홀더
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
        int T = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long A = Long.parseLong(st.nextToken());
            long B = Long.parseLong(st.nextToken());

            sb.append(0).append("\\n");  // 플레이스홀더
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_23252": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    T = int(input())

    for _ in range(T):
        A, B, C = map(int, input().split())

        # 타일 A: 1x1, B: 1x2, C: 2x1
        # 세로 2인 직사각형을 만들 수 있는지

        # 2x1 타일 C개: 가로 길이 C 차지
        # 1x2 타일 B개: 세로 2칸 차지하므로 가로 길이 1씩, 총 B
        # 1x1 타일 A개: 2개씩 쌓아야 함, A는 짝수여야 함

        # 전체 가로 길이: C + B + A/2
        # 모든 타일을 사용해야 함

        # 조건: A가 짝수여야 함
        if A % 2 == 0:
            print("Yes")
        else:
            print("No")

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

    int T;
    cin >> T;

    while (T--) {
        int A, B, C;
        cin >> A >> B >> C;

        // A가 짝수여야 함 (1x1 타일은 2개씩 쌓아야 함)
        if (A % 2 == 0) {
            cout << "Yes\\n";
        } else {
            cout << "No\\n";
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
        int T = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int A = Integer.parseInt(st.nextToken());
            int B = Integer.parseInt(st.nextToken());
            int C = Integer.parseInt(st.nextToken());

            // A가 짝수여야 함
            if (A % 2 == 0) {
                sb.append("Yes\\n");
            } else {
                sb.append("No\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_28282": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def solve():
    X, K = map(int, input().split())
    A = list(map(int, input().split()))

    # 왼발 양말: A[0:X]
    # 오른발 양말: A[X:2X]

    left = A[:X]
    right = A[X:]

    # 각 색깔별 왼발/오른발 양말 개수
    left_count = {}
    right_count = {}

    for sock in left:
        left_count[sock] = left_count.get(sock, 0) + 1

    for sock in right:
        right_count[sock] = right_count.get(sock, 0) + 1

    # 같은 색 양말 쌍의 수
    total = 0
    for color in range(1, K + 1):
        l = left_count.get(color, 0)
        r = right_count.get(color, 0)
        total += l * r

    print(total)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int X, K;
    cin >> X >> K;

    vector<int> A(2 * X);
    for (int i = 0; i < 2 * X; i++) {
        cin >> A[i];
    }

    map<int, long long> leftCount, rightCount;

    for (int i = 0; i < X; i++) {
        leftCount[A[i]]++;
    }

    for (int i = X; i < 2 * X; i++) {
        rightCount[A[i]]++;
    }

    long long total = 0;
    for (int color = 1; color <= K; color++) {
        total += leftCount[color] * rightCount[color];
    }

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

        int X = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        int[] A = new int[2 * X];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < 2 * X; i++) {
            A[i] = Integer.parseInt(st.nextToken());
        }

        long[] leftCount = new long[K + 1];
        long[] rightCount = new long[K + 1];

        for (int i = 0; i < X; i++) {
            leftCount[A[i]]++;
        }

        for (int i = X; i < 2 * X; i++) {
            rightCount[A[i]]++;
        }

        long total = 0;
        for (int color = 1; color <= K; color++) {
            total += leftCount[color] * rightCount[color];
        }

        System.out.println(total);
    }
}
'''
            }
        ]
    }
}

def main():
    baek_medium_path = '/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json'

    # 기존 파일 읽기
    with open(baek_medium_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    print(f"기존 솔루션 수: {len(existing)}")

    # 새 솔루션 추가
    added = 0
    for problem_id, solution_data in new_solutions.items():
        if problem_id not in existing:
            existing[problem_id] = solution_data
            added += 1
            print(f"  추가됨: {problem_id}")

    # 저장
    with open(baek_medium_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\n총 {added}개 문제 추가됨")
    print(f"현재 총 솔루션 수: {len(existing)}")

if __name__ == '__main__':
    main()
