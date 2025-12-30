#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배치 10: 문제 91-100 솔루션 추가"""

import json

# 새로운 솔루션들
new_solutions = {
    "9872": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 소 그룹 등장 횟수 - 가장 많이 등장한 그룹
import sys
from collections import defaultdict
input = sys.stdin.readline

def solve():
    N = int(input())
    groups = defaultdict(int)

    for _ in range(N):
        cows = input().split()
        cows.sort()  # 정렬하여 같은 그룹으로 취급
        key = tuple(cows)
        groups[key] += 1

    print(max(groups.values()))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <map>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    map<vector<string>, int> groups;

    for (int i = 0; i < N; i++) {
        vector<string> cows(3);
        cin >> cows[0] >> cows[1] >> cows[2];
        sort(cows.begin(), cows.end());
        groups[cows]++;
    }

    int maxCount = 0;
    for (auto& [key, count] : groups) {
        maxCount = max(maxCount, count);
    }

    cout << maxCount << endl;

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

        Map<String, Integer> groups = new HashMap<>();

        for (int i = 0; i < N; i++) {
            String[] cows = br.readLine().split(" ");
            Arrays.sort(cows);
            String key = String.join(",", cows);
            groups.put(key, groups.getOrDefault(key, 0) + 1);
        }

        int maxCount = 0;
        for (int count : groups.values()) {
            maxCount = Math.max(maxCount, count);
        }

        System.out.println(maxCount);
    }
}
'''
            }
        ]
    },
    "33049": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 마작 테이블 배치 - 3인/4인 마작
import sys
input = sys.stdin.readline

def solve():
    P3, P4, P0 = map(int, input().split())

    # P3명은 3인 마작만, P4명은 4인 마작만, P0명은 둘 다 가능
    # 3인 마작 테이블: T3개, 4인 마작 테이블: T4개
    # 3*T3 >= P3, 4*T4 >= P4
    # 3*T3 + 4*T4 = P3 + P4 + P0

    total = P3 + P4 + P0

    # T3를 최소화하면서 가능한 배치 찾기
    # T3 = ceil(P3 / 3), 남은 사람을 4인 테이블에

    for T3 in range((P3 + 2) // 3, total // 3 + 1):
        # T3개의 3인 테이블에 3*T3명
        # 남은 사람: total - 3*T3
        remaining = total - 3 * T3
        if remaining < 0:
            continue
        if remaining % 4 != 0:
            continue

        T4 = remaining // 4

        # P4명이 4인 테이블에 모두 들어가야 함
        if 4 * T4 < P4:
            continue

        # P3명이 3인 테이블에 모두 들어가야 함
        if 3 * T3 < P3:
            continue

        # 추가 확인: 3인 테이블에 P0에서 채울 수 있어야 함
        need_for_3 = 3 * T3 - P3
        need_for_4 = 4 * T4 - P4
        if need_for_3 + need_for_4 <= P0:
            print(T3, T4)
            return

    print(-1)

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

    int P3, P4, P0;
    cin >> P3 >> P4 >> P0;

    int total = P3 + P4 + P0;

    for (int T3 = (P3 + 2) / 3; T3 <= total / 3 + 1; T3++) {
        int remaining = total - 3 * T3;
        if (remaining < 0) continue;
        if (remaining % 4 != 0) continue;

        int T4 = remaining / 4;

        if (4 * T4 < P4) continue;
        if (3 * T3 < P3) continue;

        int needFor3 = 3 * T3 - P3;
        int needFor4 = 4 * T4 - P4;
        if (needFor3 + needFor4 <= P0) {
            cout << T3 << " " << T4 << endl;
            return 0;
        }
    }

    cout << -1 << endl;
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
        int P3 = sc.nextInt();
        int P4 = sc.nextInt();
        int P0 = sc.nextInt();

        int total = P3 + P4 + P0;

        for (int T3 = (P3 + 2) / 3; T3 <= total / 3 + 1; T3++) {
            int remaining = total - 3 * T3;
            if (remaining < 0) continue;
            if (remaining % 4 != 0) continue;

            int T4 = remaining / 4;

            if (4 * T4 < P4) continue;
            if (3 * T3 < P3) continue;

            int needFor3 = 3 * T3 - P3;
            int needFor4 = 4 * T4 - P4;
            if (needFor3 + needFor4 <= P0) {
                System.out.println(T3 + " " + T4);
                return;
            }
        }

        System.out.println(-1);
    }
}
'''
            }
        ]
    },
    "4411": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 여행 비용 정산 - 최소 교환 금액
import sys
input = sys.stdin.readline

def solve():
    while True:
        n = int(input())
        if n == 0:
            break

        expenses = []
        for _ in range(n):
            expenses.append(float(input().strip()))

        total = sum(expenses)
        avg = total / n

        # 각 사람이 내야 할 금액과 실제 낸 금액의 차이
        diffs = [exp - avg for exp in expenses]

        # 센트 단위로 처리
        # 내야 할 사람 (diff < 0), 받아야 할 사람 (diff > 0)
        give = sum(-d for d in diffs if d < 0)

        # 정산 금액 (센트 오차 고려)
        print(f"${give:.2f}")

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    while (cin >> n && n != 0) {
        vector<double> expenses(n);
        double total = 0;

        for (int i = 0; i < n; i++) {
            cin >> expenses[i];
            total += expenses[i];
        }

        double avg = total / n;

        double give = 0;
        for (int i = 0; i < n; i++) {
            double diff = expenses[i] - avg;
            if (diff < 0) {
                give += -diff;
            }
        }

        // 센트 단위로 반올림
        give = floor(give * 100 + 0.5) / 100;

        cout << fixed << setprecision(2) << "$" << give << "\\n";
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

        while (true) {
            int n = Integer.parseInt(br.readLine().trim());
            if (n == 0) break;

            double[] expenses = new double[n];
            double total = 0;

            for (int i = 0; i < n; i++) {
                expenses[i] = Double.parseDouble(br.readLine().trim());
                total += expenses[i];
            }

            double avg = total / n;

            double give = 0;
            for (int i = 0; i < n; i++) {
                double diff = expenses[i] - avg;
                if (diff < 0) {
                    give += -diff;
                }
            }

            // 센트 단위로 반올림
            give = Math.floor(give * 100 + 0.5) / 100;

            sb.append(String.format("$%.2f%n", give));
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "33560": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 수상한 어릿광대 - 주사위 게임 시뮬레이션
import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    dice = list(map(int, input().split()))

    rewards = [0, 0, 0, 0]  # 보상 1, 2, 3, 4

    i = 0
    while i < N:
        # 새 게임 시작
        score = 0
        time_elapsed = 0
        score_per_turn = 1
        time_per_turn = 4

        while i < N and time_elapsed <= 240:
            d = dice[i]

            # 효과 적용
            if d == 1:
                # 게임 종료
                if 35 <= score < 65:
                    rewards[0] += 1
                elif 65 <= score < 95:
                    rewards[1] += 1
                elif 95 <= score < 125:
                    rewards[2] += 1
                elif score >= 125:
                    rewards[3] += 1
                i += 1
                break
            elif d == 2:
                if score_per_turn > 1:
                    score_per_turn //= 2
                else:
                    time_per_turn += 2
            elif d == 3:
                pass
            elif d == 4:
                time_elapsed += 56
            elif d == 5:
                if time_per_turn > 1:
                    time_per_turn -= 1
            elif d == 6:
                if score_per_turn < 32:
                    score_per_turn *= 2

            # 점수 획득 및 시간 흐름
            score += score_per_turn
            time_elapsed += time_per_turn
            i += 1

    for r in rewards:
        print(r)

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

    vector<int> dice(N);
    for (int i = 0; i < N; i++) {
        cin >> dice[i];
    }

    int rewards[4] = {0, 0, 0, 0};

    int i = 0;
    while (i < N) {
        int score = 0;
        int timeElapsed = 0;
        int scorePerTurn = 1;
        int timePerTurn = 4;

        while (i < N && timeElapsed <= 240) {
            int d = dice[i];

            if (d == 1) {
                if (35 <= score && score < 65) rewards[0]++;
                else if (65 <= score && score < 95) rewards[1]++;
                else if (95 <= score && score < 125) rewards[2]++;
                else if (score >= 125) rewards[3]++;
                i++;
                break;
            } else if (d == 2) {
                if (scorePerTurn > 1) scorePerTurn /= 2;
                else timePerTurn += 2;
            } else if (d == 4) {
                timeElapsed += 56;
            } else if (d == 5) {
                if (timePerTurn > 1) timePerTurn--;
            } else if (d == 6) {
                if (scorePerTurn < 32) scorePerTurn *= 2;
            }

            score += scorePerTurn;
            timeElapsed += timePerTurn;
            i++;
        }
    }

    for (int i = 0; i < 4; i++) {
        cout << rewards[i] << "\\n";
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

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] dice = new int[N];
        for (int i = 0; i < N; i++) {
            dice[i] = Integer.parseInt(st.nextToken());
        }

        int[] rewards = new int[4];

        int i = 0;
        while (i < N) {
            int score = 0;
            int timeElapsed = 0;
            int scorePerTurn = 1;
            int timePerTurn = 4;

            while (i < N && timeElapsed <= 240) {
                int d = dice[i];

                if (d == 1) {
                    if (35 <= score && score < 65) rewards[0]++;
                    else if (65 <= score && score < 95) rewards[1]++;
                    else if (95 <= score && score < 125) rewards[2]++;
                    else if (score >= 125) rewards[3]++;
                    i++;
                    break;
                } else if (d == 2) {
                    if (scorePerTurn > 1) scorePerTurn /= 2;
                    else timePerTurn += 2;
                } else if (d == 4) {
                    timeElapsed += 56;
                } else if (d == 5) {
                    if (timePerTurn > 1) timePerTurn--;
                } else if (d == 6) {
                    if (scorePerTurn < 32) scorePerTurn *= 2;
                }

                score += scorePerTurn;
                timeElapsed += timePerTurn;
                i++;
            }
        }

        for (int r : rewards) {
            System.out.println(r);
        }
    }
}
'''
            }
        ]
    },
    "18787": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 소 변환 - 최소 연산 횟수
import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    A = input().strip()
    B = input().strip()

    # 각 위치에서 H와 G의 차이
    countA = {'H': 0, 'G': 0}
    countB = {'H': 0, 'G': 0}

    for c in A:
        countA[c] += 1
    for c in B:
        countB[c] += 1

    # H와 G 개수가 다르면 불가능? 아니, 변환 가능
    # 실제로는 위치 차이를 세면 됨

    diff = 0
    for i in range(N):
        if A[i] != B[i]:
            diff += 1

    # 한 번의 변환으로 H->G 또는 G->H
    # diff / 2번의 교환이 필요
    print(diff // 2)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    string A, B;
    cin >> N >> A >> B;

    int diff = 0;
    for (int i = 0; i < N; i++) {
        if (A[i] != B[i]) diff++;
    }

    cout << diff / 2 << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine().trim());
        String A = br.readLine().trim();
        String B = br.readLine().trim();

        int diff = 0;
        for (int i = 0; i < N; i++) {
            if (A.charAt(i) != B.charAt(i)) diff++;
        }

        System.out.println(diff / 2);
    }
}
'''
            }
        ]
    },
    "27970": {
        "solutions": [
            {
                "language": "python",
                "code": '''# O를 X로 바꾸기 - 이진수로 해석
import sys
input = sys.stdin.readline

MOD = 10**9 + 7

def solve():
    s = input().strip()
    n = len(s)

    # O를 1, X를 0으로 해석하여 이진수로 변환
    # 이진수 값이 연산 횟수

    result = 0
    for i, c in enumerate(s):
        if c == 'O':
            # 오른쪽에서 i번째 비트가 1
            pos = n - 1 - i
            result = (result + pow(2, pos, MOD)) % MOD

    print(result)

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
using namespace std;

const long long MOD = 1e9 + 7;

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

    string s;
    cin >> s;
    int n = s.length();

    long long result = 0;
    for (int i = 0; i < n; i++) {
        if (s[i] == 'O') {
            int pos = n - 1 - i;
            result = (result + power(2, pos, MOD)) % MOD;
        }
    }

    cout << result << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;

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

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine().trim();
        int n = s.length();

        long result = 0;
        for (int i = 0; i < n; i++) {
            if (s.charAt(i) == 'O') {
                int pos = n - 1 - i;
                result = (result + power(2, pos, MOD)) % MOD;
            }
        }

        System.out.println(result);
    }
}
'''
            }
        ]
    },
    "14842": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 사다리 나무 길이 계산
import sys
input = sys.stdin.readline

def solve():
    W, H, N = map(int, input().split())

    # 세로를 N등분
    # 각 뼈대의 길이는 W * |1 - 2*i/N| (i = 0, 1, ..., N)
    # i=0과 i=N은 제외 (양끝)

    total = 0.0
    for i in range(1, N):
        ratio = abs(1.0 - 2.0 * i / N)
        length = W * ratio
        total += length

    # 두 개의 사다리
    total *= 2

    print(f"{total:.6f}")

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <iomanip>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    double W, H;
    long long N;
    cin >> W >> H >> N;

    double total = 0.0;
    for (long long i = 1; i < N; i++) {
        double ratio = abs(1.0 - 2.0 * i / N);
        double length = W * ratio;
        total += length;
    }

    total *= 2;

    cout << fixed << setprecision(6) << total << endl;

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
        double W = sc.nextDouble();
        double H = sc.nextDouble();
        long N = sc.nextLong();

        double total = 0.0;
        for (long i = 1; i < N; i++) {
            double ratio = Math.abs(1.0 - 2.0 * i / N);
            double length = W * ratio;
            total += length;
        }

        total *= 2;

        System.out.printf("%.6f%n", total);
    }
}
'''
            }
        ]
    },
    "3061": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 사다리 게임 - 역순열로 만드는 최소 스왑 (버블 정렬 교환 횟수)
import sys
input = sys.stdin.readline

def solve():
    T = int(input())

    for _ in range(T):
        N = int(input())
        arr = list(map(int, input().split()))

        # 버블 정렬 교환 횟수 = 역순 쌍의 개수 (inversion count)
        count = 0
        for i in range(N):
            for j in range(i + 1, N):
                if arr[i] > arr[j]:
                    count += 1

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

    int T;
    cin >> T;

    while (T--) {
        int N;
        cin >> N;

        vector<int> arr(N);
        for (int i = 0; i < N; i++) {
            cin >> arr[i];
        }

        long long count = 0;
        for (int i = 0; i < N; i++) {
            for (int j = i + 1; j < N; j++) {
                if (arr[i] > arr[j]) count++;
            }
        }

        cout << count << "\\n";
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

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            int N = Integer.parseInt(br.readLine().trim());
            StringTokenizer st = new StringTokenizer(br.readLine());

            int[] arr = new int[N];
            for (int i = 0; i < N; i++) {
                arr[i] = Integer.parseInt(st.nextToken());
            }

            long count = 0;
            for (int i = 0; i < N; i++) {
                for (int j = i + 1; j < N; j++) {
                    if (arr[i] > arr[j]) count++;
                }
            }

            sb.append(count).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "15594": {
        "solutions": [
            {
                "language": "python",
                "code": '''# Bessie가 끼어든 위치 찾아 스왑 횟수 계산
import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    heights = []
    for _ in range(N):
        heights.append(int(input()))

    # 정렬된 상태에서 Bessie가 끼어듦
    # 최소 스왑 = Bessie가 끼어든 위치와 원래 있어야 할 위치의 차이

    # 현재 위치에서 Bessie 찾기
    # Bessie는 정렬 순서를 깨는 위치에 있음

    # 끼어든 위치 찾기
    insert_pos = -1
    for i in range(1, N):
        if heights[i] < heights[i-1]:
            insert_pos = i
            break

    if insert_pos == -1:
        # 이미 정렬됨
        print(0)
        return

    # Bessie의 값
    bessie = heights[insert_pos]

    # 원래 있어야 할 위치 찾기
    original_pos = -1
    for i in range(N):
        if i == insert_pos:
            continue
        # Bessie가 들어갈 위치
        if i < insert_pos:
            if heights[i] > bessie:
                original_pos = i
                break
        else:
            if heights[i] >= bessie:
                original_pos = i
                break
    if original_pos == -1:
        original_pos = N - 1 if insert_pos < N - 1 else 0

    # 실제로는 왼쪽에서 끼어들었는지 오른쪽에서 끼어들었는지 확인
    # 스왑 횟수 = |insert_pos - original_pos|
    print(abs(insert_pos - original_pos))

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

    vector<int> heights(N);
    for (int i = 0; i < N; i++) {
        cin >> heights[i];
    }

    // 정렬된 위치와 비교
    vector<int> sorted = heights;
    sort(sorted.begin(), sorted.end());

    // 다른 위치 찾기
    int start = -1, end = -1;
    for (int i = 0; i < N; i++) {
        if (heights[i] != sorted[i]) {
            if (start == -1) start = i;
            end = i;
        }
    }

    if (start == -1) {
        cout << 0 << endl;
    } else {
        cout << end - start << endl;
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

        int[] heights = new int[N];
        int[] sorted = new int[N];
        for (int i = 0; i < N; i++) {
            heights[i] = Integer.parseInt(br.readLine().trim());
            sorted[i] = heights[i];
        }

        Arrays.sort(sorted);

        int start = -1, end = -1;
        for (int i = 0; i < N; i++) {
            if (heights[i] != sorted[i]) {
                if (start == -1) start = i;
                end = i;
            }
        }

        if (start == -1) {
            System.out.println(0);
        } else {
            System.out.println(end - start);
        }
    }
}
'''
            }
        ]
    },
    "21236": {
        "solutions": [
            {
                "language": "python",
                "code": '''# Comfortable Cows - 정확히 3개의 인접 소
import sys
input = sys.stdin.readline

def solve():
    N = int(input())

    cows = set()
    dx = [0, 0, 1, -1]
    dy = [1, -1, 0, 0]

    def count_adj(x, y):
        cnt = 0
        for i in range(4):
            nx, ny = x + dx[i], y + dy[i]
            if (nx, ny) in cows:
                cnt += 1
        return cnt

    def is_comfortable(x, y):
        return count_adj(x, y) == 3

    comfortable = 0
    results = []

    for _ in range(N):
        x, y = map(int, input().split())

        # 새 소 추가 전 인접 소들의 상태 확인
        affected = []
        for i in range(4):
            nx, ny = x + dx[i], y + dy[i]
            if (nx, ny) in cows:
                affected.append((nx, ny, is_comfortable(nx, ny)))

        # 새 소 추가
        cows.add((x, y))

        # 새 소가 comfortable인지
        if is_comfortable(x, y):
            comfortable += 1

        # 인접 소들의 상태 변화
        for nx, ny, was_comfortable in affected:
            now_comfortable = is_comfortable(nx, ny)
            if was_comfortable and not now_comfortable:
                comfortable -= 1
            elif not was_comfortable and now_comfortable:
                comfortable += 1

        results.append(comfortable)

    print('\\n'.join(map(str, results)))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <set>
using namespace std;

set<pair<int, int>> cows;
int dx[] = {0, 0, 1, -1};
int dy[] = {1, -1, 0, 0};

int countAdj(int x, int y) {
    int cnt = 0;
    for (int i = 0; i < 4; i++) {
        if (cows.count({x + dx[i], y + dy[i]})) cnt++;
    }
    return cnt;
}

bool isComfortable(int x, int y) {
    return countAdj(x, y) == 3;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    int comfortable = 0;

    for (int i = 0; i < N; i++) {
        int x, y;
        cin >> x >> y;

        // 인접 소들의 현재 상태
        int adj[4][3];  // nx, ny, was_comfortable
        int adjCount = 0;
        for (int j = 0; j < 4; j++) {
            int nx = x + dx[j], ny = y + dy[j];
            if (cows.count({nx, ny})) {
                adj[adjCount][0] = nx;
                adj[adjCount][1] = ny;
                adj[adjCount][2] = isComfortable(nx, ny);
                adjCount++;
            }
        }

        cows.insert({x, y});

        if (isComfortable(x, y)) comfortable++;

        for (int j = 0; j < adjCount; j++) {
            int nx = adj[j][0], ny = adj[j][1];
            bool wasComf = adj[j][2];
            bool nowComf = isComfortable(nx, ny);
            if (wasComf && !nowComf) comfortable--;
            else if (!wasComf && nowComf) comfortable++;
        }

        cout << comfortable << "\\n";
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
    static Set<Long> cows = new HashSet<>();
    static int[] dx = {0, 0, 1, -1};
    static int[] dy = {1, -1, 0, 0};

    static long key(int x, int y) {
        return ((long)x << 20) + y;
    }

    static int countAdj(int x, int y) {
        int cnt = 0;
        for (int i = 0; i < 4; i++) {
            if (cows.contains(key(x + dx[i], y + dy[i]))) cnt++;
        }
        return cnt;
    }

    static boolean isComfortable(int x, int y) {
        return countAdj(x, y) == 3;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int N = Integer.parseInt(br.readLine().trim());
        int comfortable = 0;

        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());

            List<int[]> affected = new ArrayList<>();
            for (int j = 0; j < 4; j++) {
                int nx = x + dx[j], ny = y + dy[j];
                if (cows.contains(key(nx, ny))) {
                    affected.add(new int[]{nx, ny, isComfortable(nx, ny) ? 1 : 0});
                }
            }

            cows.add(key(x, y));

            if (isComfortable(x, y)) comfortable++;

            for (int[] adj : affected) {
                boolean wasComf = adj[2] == 1;
                boolean nowComf = isComfortable(adj[0], adj[1]);
                if (wasComf && !nowComf) comfortable--;
                else if (!wasComf && nowComf) comfortable++;
            }

            sb.append(comfortable).append("\\n");
        }

        System.out.print(sb);
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
