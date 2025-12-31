#!/usr/bin/env python3
"""
Script to add solutions to 10 medium difficulty Baekjoon problems with empty solutions.
Uses fcntl.LOCK_EX for safe file writing.
"""

import json
import fcntl

# File path
JSON_PATH = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

# Problem indices with empty solutions (medium difficulty)
PROBLEM_INDICES = [2469, 2473, 2481, 2486, 2490, 2491, 2499, 2530, 2533, 2547]

# Solutions for each problem
SOLUTIONS = {
    # Problem 1: baekjoon_11564 - 점프왕 최준민
    2469: [
        {
            "language": "python",
            "code": """# 백준 11564: 점프왕 최준민
# 0에서 시작해서 k씩 점프하여 [a, b] 구간의 초콜릿을 최대로 얻는 문제
# k의 배수인 좌표만 방문 가능하므로 [a, b] 구간 내 k의 배수 개수를 구하면 됨

import sys
input = sys.stdin.readline

k, a, b = map(int, input().split())

# a 이상의 첫 번째 k의 배수 찾기
if a % k == 0:
    first = a
elif a > 0:
    first = ((a // k) + 1) * k
else:
    first = (a // k) * k

# b 이하의 마지막 k의 배수 찾기
if b % k == 0:
    last = b
elif b > 0:
    last = (b // k) * k
else:
    last = ((b // k) - 1) * k if b % k != 0 else b

# k의 배수 개수 계산
if first > b or last < a:
    print(0)
else:
    count = (last - first) // k + 1
    print(count)
"""
        },
        {
            "language": "java",
            "code": """import java.util.Scanner;

// 백준 11564: 점프왕 최준민
// k의 배수만 방문 가능하므로 [a, b] 구간 내 k의 배수 개수를 계산
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long k = sc.nextLong();
        long a = sc.nextLong();
        long b = sc.nextLong();

        // a 이상의 첫 번째 k의 배수
        long first;
        if (a % k == 0) {
            first = a;
        } else if (a > 0) {
            first = ((a / k) + 1) * k;
        } else {
            first = (a / k) * k;
        }

        // b 이하의 마지막 k의 배수
        long last;
        if (b % k == 0) {
            last = b;
        } else if (b > 0) {
            last = (b / k) * k;
        } else {
            last = ((b / k) - 1) * k;
        }

        // k의 배수 개수 출력
        if (first > b || last < a) {
            System.out.println(0);
        } else {
            System.out.println((last - first) / k + 1);
        }
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
using namespace std;

// 백준 11564: 점프왕 최준민
// k의 배수만 방문 가능하므로 [a, b] 구간 내 k의 배수 개수를 계산
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    long long k, a, b;
    cin >> k >> a >> b;

    // a 이상의 첫 번째 k의 배수
    long long first;
    if (a % k == 0) {
        first = a;
    } else if (a > 0) {
        first = ((a / k) + 1) * k;
    } else {
        first = (a / k) * k;
    }

    // b 이하의 마지막 k의 배수
    long long last;
    if (b % k == 0) {
        last = b;
    } else if (b > 0) {
        last = (b / k) * k;
    } else {
        last = ((b / k) - 1) * k;
    }

    // k의 배수 개수 출력
    if (first > b || last < a) {
        cout << 0 << endl;
    } else {
        cout << (last - first) / k + 1 << endl;
    }

    return 0;
}
"""
        }
    ],

    # Problem 2: baekjoon_31926 - 밤양갱
    2473: [
        {
            "language": "python",
            "code": """# 백준 31926: 밤양갱
# daldidalgo를 N번, daldidan을 1번 출력해야 함
# daldidalgo (10자), daldidan (8자)
# 복사-붙여넣기를 활용하여 최소 시간 계산

import sys
input = sys.stdin.readline

n = int(input())

# daldidalgo 입력: 10초
# 이후 복사로 2배씩 늘릴 수 있음
# N개를 만들려면 ceil(log2(N))번 복사
# 마지막 daldidan 변환: 1초

if n == 1:
    print(10 + 1)  # N=1일 때
else:
    # N >= 2일 때
    copy_count = 0
    current = 1
    while current < n:
        current *= 2
        copy_count += 1
    # 10 (daldidalgo 입력) + copy_count (복사 횟수) + 1 (daldidan 변환)
    print(10 + copy_count + 1)
"""
        },
        {
            "language": "java",
            "code": """import java.util.Scanner;

// 백준 31926: 밤양갱
// daldidalgo N번 + daldidan 1번을 최소 시간에 입력
// daldidalgo 입력(10초) + log2(N)번 복사 + daldidan 변환(1초)
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long n = sc.nextLong();

        // daldidalgo 입력: 10초
        int result = 10;

        // N개까지 복사 (2배씩 증가)
        long current = 1;
        while (current < n) {
            current *= 2;
            result++;
        }

        // 마지막 daldidan 변환: 1초
        result++;

        System.out.println(result);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <cmath>
using namespace std;

// 백준 31926: 밤양갱
// daldidalgo N번 + daldidan 1번을 최소 시간에 입력
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    long long n;
    cin >> n;

    // daldidalgo 입력: 10초
    int result = 10;

    // N개까지 복사 (2배씩 증가)
    long long current = 1;
    while (current < n) {
        current *= 2;
        result++;
    }

    // 마지막 daldidan 변환: 1초
    result++;

    cout << result << endl;

    return 0;
}
"""
        }
    ],

    # Problem 3: baekjoon_20003 - 거스름돈이 싫어요
    2481: [
        {
            "language": "python",
            "code": """# 백준 20003: 거스름돈이 싫어요
# 모든 아이템 가격을 딱 떨어지게 나눌 수 있는 최대 코인 단위 = GCD
# 분수들의 GCD = 분자들의 GCD / 분모들의 LCM

import sys
from math import gcd
from functools import reduce

input = sys.stdin.readline

def lcm(a, b):
    return a * b // gcd(a, b)

n = int(input())
fractions = []
for _ in range(n):
    a, b = map(int, input().split())
    # 기약분수로 변환
    g = gcd(a, b)
    fractions.append((a // g, b // g))

# 분자들의 GCD
numerator_gcd = reduce(gcd, [f[0] for f in fractions])

# 분모들의 LCM
denominator_lcm = reduce(lcm, [f[1] for f in fractions])

# 결과를 기약분수로 출력
result_gcd = gcd(numerator_gcd, denominator_lcm)
print(numerator_gcd // result_gcd, denominator_lcm // result_gcd)
"""
        },
        {
            "language": "java",
            "code": """import java.util.Scanner;

// 백준 20003: 거스름돈이 싫어요
// 분수들의 GCD = 분자들의 GCD / 분모들의 LCM
public class Main {
    static long gcd(long a, long b) {
        while (b != 0) {
            long t = b;
            b = a % b;
            a = t;
        }
        return a;
    }

    static long lcm(long a, long b) {
        return a / gcd(a, b) * b;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        long numGcd = 0;  // 분자들의 GCD
        long denLcm = 1;  // 분모들의 LCM

        for (int i = 0; i < n; i++) {
            long a = sc.nextLong();
            long b = sc.nextLong();

            // 기약분수로 변환
            long g = gcd(a, b);
            a /= g;
            b /= g;

            // GCD와 LCM 계산
            if (numGcd == 0) {
                numGcd = a;
            } else {
                numGcd = gcd(numGcd, a);
            }
            denLcm = lcm(denLcm, b);
        }

        // 결과를 기약분수로 출력
        long g = gcd(numGcd, denLcm);
        System.out.println(numGcd / g + " " + denLcm / g);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <algorithm>
using namespace std;

// 백준 20003: 거스름돈이 싫어요
// 분수들의 GCD = 분자들의 GCD / 분모들의 LCM

long long gcd(long long a, long long b) {
    while (b != 0) {
        long long t = b;
        b = a % b;
        a = t;
    }
    return a;
}

long long lcm(long long a, long long b) {
    return a / gcd(a, b) * b;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    long long numGcd = 0;  // 분자들의 GCD
    long long denLcm = 1;  // 분모들의 LCM

    for (int i = 0; i < n; i++) {
        long long a, b;
        cin >> a >> b;

        // 기약분수로 변환
        long long g = gcd(a, b);
        a /= g;
        b /= g;

        // GCD와 LCM 계산
        if (numGcd == 0) {
            numGcd = a;
        } else {
            numGcd = gcd(numGcd, a);
        }
        denLcm = lcm(denLcm, b);
    }

    // 결과를 기약분수로 출력
    long long g = gcd(numGcd, denLcm);
    cout << numGcd / g << " " << denLcm / g << endl;

    return 0;
}
"""
        }
    ],

    # Problem 4: baekjoon_18243 - Small World Network
    2486: [
        {
            "language": "python",
            "code": """# 백준 18243: Small World Network
# 모든 정점 쌍의 최단 거리가 6 이하인지 확인
# 플로이드-워셜 알고리즘 사용

import sys
input = sys.stdin.readline

INF = float('inf')

n, k = map(int, input().split())

# 거리 배열 초기화
dist = [[INF] * (n + 1) for _ in range(n + 1)]
for i in range(n + 1):
    dist[i][i] = 0

# 간선 입력
for _ in range(k):
    a, b = map(int, input().split())
    dist[a][b] = 1
    dist[b][a] = 1

# 플로이드-워셜 알고리즘
for mid in range(1, n + 1):
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if dist[i][mid] + dist[mid][j] < dist[i][j]:
                dist[i][j] = dist[i][mid] + dist[mid][j]

# 모든 정점 쌍의 거리가 6 이하인지 확인
small_world = True
for i in range(1, n + 1):
    for j in range(1, n + 1):
        if dist[i][j] > 6:
            small_world = False
            break
    if not small_world:
        break

print("Small World!" if small_world else "Big World!")
"""
        },
        {
            "language": "java",
            "code": """import java.util.Scanner;

// 백준 18243: Small World Network
// 플로이드-워셜로 모든 정점 쌍의 최단 거리가 6 이하인지 확인
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int k = sc.nextInt();

        int INF = 1000000;
        int[][] dist = new int[n + 1][n + 1];

        // 초기화
        for (int i = 0; i <= n; i++) {
            for (int j = 0; j <= n; j++) {
                if (i == j) dist[i][j] = 0;
                else dist[i][j] = INF;
            }
        }

        // 간선 입력
        for (int i = 0; i < k; i++) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            dist[a][b] = 1;
            dist[b][a] = 1;
        }

        // 플로이드-워셜
        for (int mid = 1; mid <= n; mid++) {
            for (int i = 1; i <= n; i++) {
                for (int j = 1; j <= n; j++) {
                    if (dist[i][mid] + dist[mid][j] < dist[i][j]) {
                        dist[i][j] = dist[i][mid] + dist[mid][j];
                    }
                }
            }
        }

        // 6단계 이하인지 확인
        boolean smallWorld = true;
        for (int i = 1; i <= n && smallWorld; i++) {
            for (int j = 1; j <= n && smallWorld; j++) {
                if (dist[i][j] > 6) {
                    smallWorld = false;
                }
            }
        }

        System.out.println(smallWorld ? "Small World!" : "Big World!");
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <algorithm>
using namespace std;

// 백준 18243: Small World Network
// 플로이드-워셜로 모든 정점 쌍의 최단 거리가 6 이하인지 확인

const int INF = 1000000;
int dist[101][101];

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    // 초기화
    for (int i = 0; i <= n; i++) {
        for (int j = 0; j <= n; j++) {
            if (i == j) dist[i][j] = 0;
            else dist[i][j] = INF;
        }
    }

    // 간선 입력
    for (int i = 0; i < k; i++) {
        int a, b;
        cin >> a >> b;
        dist[a][b] = 1;
        dist[b][a] = 1;
    }

    // 플로이드-워셜
    for (int mid = 1; mid <= n; mid++) {
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++) {
                dist[i][j] = min(dist[i][j], dist[i][mid] + dist[mid][j]);
            }
        }
    }

    // 6단계 이하인지 확인
    bool smallWorld = true;
    for (int i = 1; i <= n && smallWorld; i++) {
        for (int j = 1; j <= n && smallWorld; j++) {
            if (dist[i][j] > 6) {
                smallWorld = false;
            }
        }
    }

    cout << (smallWorld ? "Small World!" : "Big World!") << endl;

    return 0;
}
"""
        }
    ],

    # Problem 5: baekjoon_23758 - 중앙값 제거
    2490: [
        {
            "language": "python",
            "code": """# 백준 23758: 중앙값 제거
# 중앙값을 2로 나누는 연산을 0이 나올 때까지 반복
# 중앙값 = 정렬 후 (N+1)//2 번째 원소
# 힙을 사용하여 효율적으로 중앙값 관리

import sys
import heapq

input = sys.stdin.readline

n = int(input())
arr = list(map(int, input().split()))

# 최대힙 (작은 쪽 절반) - 음수로 저장
# 최소힙 (큰 쪽 절반)
max_heap = []  # 작은 쪽 (중앙값 포함)
min_heap = []  # 큰 쪽

# 초기화: 정렬 후 분배
arr.sort()
mid_idx = (n + 1) // 2 - 1

for i in range(mid_idx + 1):
    heapq.heappush(max_heap, -arr[i])
for i in range(mid_idx + 1, n):
    heapq.heappush(min_heap, arr[i])

count = 0

while True:
    # 중앙값은 max_heap의 top
    median = -max_heap[0]
    if median == 0:
        break

    # 중앙값을 2로 나눔
    heapq.heapreplace(max_heap, -(median // 2))
    count += 1

    # 힙 균형 맞추기: max_heap의 top이 min_heap의 top보다 크면 교환
    if min_heap and -max_heap[0] > min_heap[0]:
        max_val = -heapq.heappop(max_heap)
        min_val = heapq.heappop(min_heap)
        heapq.heappush(max_heap, -min_val)
        heapq.heappush(min_heap, max_val)

print(count)
"""
        },
        {
            "language": "java",
            "code": """import java.io.*;
import java.util.*;

// 백준 23758: 중앙값 제거
// 힙을 사용하여 중앙값을 효율적으로 관리
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());

        StringTokenizer st = new StringTokenizer(br.readLine());
        long[] arr = new long[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Long.parseLong(st.nextToken());
        }

        Arrays.sort(arr);

        // 최대힙 (작은 쪽), 최소힙 (큰 쪽)
        PriorityQueue<Long> maxHeap = new PriorityQueue<>(Collections.reverseOrder());
        PriorityQueue<Long> minHeap = new PriorityQueue<>();

        int midIdx = (n + 1) / 2 - 1;
        for (int i = 0; i <= midIdx; i++) {
            maxHeap.add(arr[i]);
        }
        for (int i = midIdx + 1; i < n; i++) {
            minHeap.add(arr[i]);
        }

        long count = 0;

        while (true) {
            long median = maxHeap.peek();
            if (median == 0) break;

            maxHeap.poll();
            maxHeap.add(median / 2);
            count++;

            // 균형 맞추기
            if (!minHeap.isEmpty() && maxHeap.peek() > minHeap.peek()) {
                long maxVal = maxHeap.poll();
                long minVal = minHeap.poll();
                maxHeap.add(minVal);
                minHeap.add(maxVal);
            }
        }

        System.out.println(count);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <queue>
#include <algorithm>
#include <vector>
using namespace std;

// 백준 23758: 중앙값 제거
// 힙을 사용하여 중앙값을 효율적으로 관리

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<long long> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    sort(arr.begin(), arr.end());

    // 최대힙 (작은 쪽), 최소힙 (큰 쪽)
    priority_queue<long long> maxHeap;
    priority_queue<long long, vector<long long>, greater<long long>> minHeap;

    int midIdx = (n + 1) / 2 - 1;
    for (int i = 0; i <= midIdx; i++) {
        maxHeap.push(arr[i]);
    }
    for (int i = midIdx + 1; i < n; i++) {
        minHeap.push(arr[i]);
    }

    long long count = 0;

    while (true) {
        long long median = maxHeap.top();
        if (median == 0) break;

        maxHeap.pop();
        maxHeap.push(median / 2);
        count++;

        // 균형 맞추기
        if (!minHeap.empty() && maxHeap.top() > minHeap.top()) {
            long long maxVal = maxHeap.top(); maxHeap.pop();
            long long minVal = minHeap.top(); minHeap.pop();
            maxHeap.push(minVal);
            minHeap.push(maxVal);
        }
    }

    cout << count << endl;

    return 0;
}
"""
        }
    ],

    # Problem 6: baekjoon_27111 - 출입 기록
    2491: [
        {
            "language": "python",
            "code": """# 백준 27111: 출입 기록
# 출입 기록의 일관성을 확인하고 누락된 기록 수를 계산
# 들어온 기록 없이 나간 경우, 나간 기록 없이 들어온 경우 등을 체크

import sys
input = sys.stdin.readline

n = int(input())

# 현재 부대 내에 있는 사람들 (1이면 안에 있음)
inside = {}
missing = 0

for _ in range(n):
    a, b = map(int, input().split())

    if b == 1:  # 들어옴
        if a in inside and inside[a] == 1:
            # 이미 안에 있는데 또 들어옴 -> 나간 기록 누락
            missing += 1
        inside[a] = 1
    else:  # 나감
        if a not in inside or inside[a] == 0:
            # 안에 없는데 나감 -> 들어온 기록 누락
            missing += 1
        inside[a] = 0

# 마지막에 안에 남아있는 사람들 -> 나간 기록 누락
for person, status in inside.items():
    if status == 1:
        missing += 1

print(missing)
"""
        },
        {
            "language": "java",
            "code": """import java.io.*;
import java.util.*;

// 백준 27111: 출입 기록
// 출입 기록의 누락 횟수를 계산
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());

        // 현재 부대 내에 있는 사람들
        Map<Integer, Integer> inside = new HashMap<>();
        int missing = 0;

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());

            if (b == 1) {  // 들어옴
                if (inside.getOrDefault(a, 0) == 1) {
                    // 이미 안에 있는데 또 들어옴
                    missing++;
                }
                inside.put(a, 1);
            } else {  // 나감
                if (inside.getOrDefault(a, 0) == 0) {
                    // 안에 없는데 나감
                    missing++;
                }
                inside.put(a, 0);
            }
        }

        // 마지막에 안에 남아있는 사람들
        for (int status : inside.values()) {
            if (status == 1) {
                missing++;
            }
        }

        System.out.println(missing);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <map>
using namespace std;

// 백준 27111: 출입 기록
// 출입 기록의 누락 횟수를 계산

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    map<int, int> inside;
    int missing = 0;

    for (int i = 0; i < n; i++) {
        int a, b;
        cin >> a >> b;

        if (b == 1) {  // 들어옴
            if (inside[a] == 1) {
                // 이미 안에 있는데 또 들어옴
                missing++;
            }
            inside[a] = 1;
        } else {  // 나감
            if (inside[a] == 0) {
                // 안에 없는데 나감
                missing++;
            }
            inside[a] = 0;
        }
    }

    // 마지막에 안에 남아있는 사람들
    for (auto& p : inside) {
        if (p.second == 1) {
            missing++;
        }
    }

    cout << missing << endl;

    return 0;
}
"""
        }
    ],

    # Problem 7: baekjoon_14919 - 분포표 만들기
    2499: [
        {
            "language": "python",
            "code": """# 백준 14919: 분포표 만들기
# [0, 1) 구간을 m개로 나누고 각 구간에 포함되는 실수 개수 세기

import sys
input = sys.stdin.readline

m = int(input())
numbers = list(map(float, input().split()))

# 각 구간에 포함되는 개수
count = [0] * m
L = 1.0 / m

for num in numbers:
    # 해당 실수가 속하는 구간 번호 (0-indexed)
    idx = int(num / L)
    # 경계값 처리 (num이 정확히 1인 경우는 없지만 안전하게)
    if idx >= m:
        idx = m - 1
    count[idx] += 1

print(' '.join(map(str, count)))
"""
        },
        {
            "language": "java",
            "code": """import java.io.*;
import java.util.*;

// 백준 14919: 분포표 만들기
// [0, 1) 구간을 m개로 나누고 각 구간에 포함되는 실수 개수 세기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int m = Integer.parseInt(br.readLine());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] count = new int[m];
        double L = 1.0 / m;

        while (st.hasMoreTokens()) {
            double num = Double.parseDouble(st.nextToken());
            int idx = (int)(num / L);
            if (idx >= m) idx = m - 1;
            count[idx]++;
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < m; i++) {
            if (i > 0) sb.append(" ");
            sb.append(count[i]);
        }
        System.out.println(sb);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
using namespace std;

// 백준 14919: 분포표 만들기
// [0, 1) 구간을 m개로 나누고 각 구간에 포함되는 실수 개수 세기

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int m;
    cin >> m;

    vector<int> count(m, 0);
    double L = 1.0 / m;

    double num;
    while (cin >> num) {
        int idx = (int)(num / L);
        if (idx >= m) idx = m - 1;
        count[idx]++;
    }

    for (int i = 0; i < m; i++) {
        if (i > 0) cout << " ";
        cout << count[i];
    }
    cout << endl;

    return 0;
}
"""
        }
    ],

    # Problem 8: baekjoon_20937 - 떡국
    2530: [
        {
            "language": "python",
            "code": """# 백준 20937: 떡국
# 떡국 그릇을 최소 탑 개수로 쌓기
# 같은 크기의 그릇은 같은 탑에 쌓을 수 없음
# 따라서 가장 많이 등장하는 크기의 개수가 최소 탑 개수

import sys
from collections import Counter

input = sys.stdin.readline

n = int(input())
bowls = list(map(int, input().split()))

# 각 크기별 개수 세기
count = Counter(bowls)

# 가장 많이 등장하는 크기의 개수가 답
print(max(count.values()))
"""
        },
        {
            "language": "java",
            "code": """import java.io.*;
import java.util.*;

// 백준 20937: 떡국
// 같은 크기의 그릇은 같은 탑에 쌓을 수 없으므로
// 가장 많이 등장하는 크기의 개수가 최소 탑 개수
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());

        StringTokenizer st = new StringTokenizer(br.readLine());
        Map<Integer, Integer> count = new HashMap<>();

        for (int i = 0; i < n; i++) {
            int bowl = Integer.parseInt(st.nextToken());
            count.put(bowl, count.getOrDefault(bowl, 0) + 1);
        }

        int maxCount = 0;
        for (int c : count.values()) {
            maxCount = Math.max(maxCount, c);
        }

        System.out.println(maxCount);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <map>
#include <algorithm>
using namespace std;

// 백준 20937: 떡국
// 같은 크기의 그릇은 같은 탑에 쌓을 수 없으므로
// 가장 많이 등장하는 크기의 개수가 최소 탑 개수

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    map<int, int> count;
    for (int i = 0; i < n; i++) {
        int bowl;
        cin >> bowl;
        count[bowl]++;
    }

    int maxCount = 0;
    for (auto& p : count) {
        maxCount = max(maxCount, p.second);
    }

    cout << maxCount << endl;

    return 0;
}
"""
        }
    ],

    # Problem 9: baekjoon_2232 - 지뢰
    2533: [
        {
            "language": "python",
            "code": """# 백준 2232: 지뢰
# 연쇄 폭발을 고려하여 최소 개수의 지뢰를 직접 터트려야 함
# 가장 큰 충격 강도를 가진 지뢰부터 터트리면 됨
# 그리디: 충격 강도가 큰 지뢰부터 확인하며 아직 안 터진 지뢰만 직접 터트림

import sys
from collections import deque

input = sys.stdin.readline

n = int(input())
power = [int(input()) for _ in range(n)]

# 터진 지뢰 체크
exploded = [False] * n

# (충격 강도, 인덱스) 쌍으로 정렬 (내림차순)
indexed = sorted(enumerate(power), key=lambda x: -x[1])

result = []

def explode(idx):
    # idx 지뢰가 터지면 연쇄 폭발 처리
    queue = deque([idx])
    while queue:
        cur = queue.popleft()
        if exploded[cur]:
            continue
        exploded[cur] = True
        cur_power = power[cur]

        # 왼쪽 지뢰 확인
        if cur > 0 and not exploded[cur - 1] and power[cur - 1] < cur_power:
            queue.append(cur - 1)

        # 오른쪽 지뢰 확인
        if cur < n - 1 and not exploded[cur + 1] and power[cur + 1] < cur_power:
            queue.append(cur + 1)

for idx, p in indexed:
    if not exploded[idx]:
        result.append(idx + 1)  # 1-indexed
        explode(idx)

# 오름차순 정렬 후 출력
result.sort()
for r in result:
    print(r)
"""
        },
        {
            "language": "java",
            "code": """import java.io.*;
import java.util.*;

// 백준 2232: 지뢰
// 가장 큰 충격 강도를 가진 지뢰부터 터트려서 연쇄 폭발 유도
public class Main {
    static int n;
    static int[] power;
    static boolean[] exploded;

    static void explode(int idx) {
        Queue<Integer> queue = new LinkedList<>();
        queue.add(idx);

        while (!queue.isEmpty()) {
            int cur = queue.poll();
            if (exploded[cur]) continue;
            exploded[cur] = true;
            int curPower = power[cur];

            // 왼쪽 지뢰
            if (cur > 0 && !exploded[cur - 1] && power[cur - 1] < curPower) {
                queue.add(cur - 1);
            }

            // 오른쪽 지뢰
            if (cur < n - 1 && !exploded[cur + 1] && power[cur + 1] < curPower) {
                queue.add(cur + 1);
            }
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        n = Integer.parseInt(br.readLine());

        power = new int[n];
        exploded = new boolean[n];
        int[][] indexed = new int[n][2];

        for (int i = 0; i < n; i++) {
            power[i] = Integer.parseInt(br.readLine());
            indexed[i][0] = i;
            indexed[i][1] = power[i];
        }

        // 충격 강도 내림차순 정렬
        Arrays.sort(indexed, (a, b) -> b[1] - a[1]);

        List<Integer> result = new ArrayList<>();

        for (int[] item : indexed) {
            int idx = item[0];
            if (!exploded[idx]) {
                result.add(idx + 1);  // 1-indexed
                explode(idx);
            }
        }

        // 오름차순 정렬 후 출력
        Collections.sort(result);
        StringBuilder sb = new StringBuilder();
        for (int r : result) {
            sb.append(r).append("\\n");
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
#include <queue>
using namespace std;

// 백준 2232: 지뢰
// 가장 큰 충격 강도를 가진 지뢰부터 터트려서 연쇄 폭발 유도

int n;
vector<int> power;
vector<bool> exploded;

void explode(int idx) {
    queue<int> q;
    q.push(idx);

    while (!q.empty()) {
        int cur = q.front(); q.pop();
        if (exploded[cur]) continue;
        exploded[cur] = true;
        int curPower = power[cur];

        // 왼쪽 지뢰
        if (cur > 0 && !exploded[cur - 1] && power[cur - 1] < curPower) {
            q.push(cur - 1);
        }

        // 오른쪽 지뢰
        if (cur < n - 1 && !exploded[cur + 1] && power[cur + 1] < curPower) {
            q.push(cur + 1);
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n;
    power.resize(n);
    exploded.resize(n, false);

    vector<pair<int, int>> indexed(n);  // (충격 강도, 인덱스)

    for (int i = 0; i < n; i++) {
        cin >> power[i];
        indexed[i] = {power[i], i};
    }

    // 충격 강도 내림차순 정렬
    sort(indexed.begin(), indexed.end(), greater<pair<int, int>>());

    vector<int> result;

    for (auto& item : indexed) {
        int idx = item.second;
        if (!exploded[idx]) {
            result.push_back(idx + 1);  // 1-indexed
            explode(idx);
        }
    }

    // 오름차순 정렬 후 출력
    sort(result.begin(), result.end());
    for (int r : result) {
        cout << r << "\\n";
    }

    return 0;
}
"""
        }
    ],

    # Problem 10: baekjoon_1980 - 햄버거 사랑
    2547: [
        {
            "language": "python",
            "code": """# 백준 1980: 햄버거 사랑
# 타워버거(n분), 불고기버거(m분)를 t분 동안 먹기
# 목표: 1) 콜라 마시는 시간 최소화 2) 햄버거 최대로 먹기
# n*i + m*j <= t 를 만족하며 콜라 시간(t - n*i - m*j) 최소화

import sys
input = sys.stdin.readline

n, m, t = map(int, input().split())

min_coke = t  # 콜라 마시는 최소 시간
max_burger = 0  # 햄버거 최대 개수

# 타워버거 개수 i를 0부터 t//n까지 시도
for i in range(t // n + 1):
    remaining = t - n * i
    # 불고기버거는 남은 시간에서 최대로
    j = remaining // m
    coke = remaining - m * j
    total_burger = i + j

    if coke < min_coke or (coke == min_coke and total_burger > max_burger):
        min_coke = coke
        max_burger = total_burger

print(max_burger, min_coke)
"""
        },
        {
            "language": "java",
            "code": """import java.util.Scanner;

// 백준 1980: 햄버거 사랑
// 콜라 마시는 시간 최소화, 햄버거 최대로 먹기
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();  // 타워버거 시간
        int m = sc.nextInt();  // 불고기버거 시간
        int t = sc.nextInt();  // 총 시간

        int minCoke = t;
        int maxBurger = 0;

        // 타워버거 개수 i를 0부터 t/n까지 시도
        for (int i = 0; i <= t / n; i++) {
            int remaining = t - n * i;
            int j = remaining / m;  // 불고기버거 최대 개수
            int coke = remaining - m * j;
            int totalBurger = i + j;

            if (coke < minCoke || (coke == minCoke && totalBurger > maxBurger)) {
                minCoke = coke;
                maxBurger = totalBurger;
            }
        }

        System.out.println(maxBurger + " " + minCoke);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
using namespace std;

// 백준 1980: 햄버거 사랑
// 콜라 마시는 시간 최소화, 햄버거 최대로 먹기

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, t;  // 타워버거 시간, 불고기버거 시간, 총 시간
    cin >> n >> m >> t;

    int minCoke = t;
    int maxBurger = 0;

    // 타워버거 개수 i를 0부터 t/n까지 시도
    for (int i = 0; i <= t / n; i++) {
        int remaining = t - n * i;
        int j = remaining / m;  // 불고기버거 최대 개수
        int coke = remaining - m * j;
        int totalBurger = i + j;

        if (coke < minCoke || (coke == minCoke && totalBurger > maxBurger)) {
            minCoke = coke;
            maxBurger = totalBurger;
        }
    }

    cout << maxBurger << " " << minCoke << endl;

    return 0;
}
"""
        }
    ]
}

def main():
    # Read JSON file
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # Update solutions for each problem
    updated_count = 0
    for idx, solutions in SOLUTIONS.items():
        if data[idx]['solutions'] == []:
            data[idx]['solutions'] = solutions
            updated_count += 1
            print(f"Updated: {data[idx]['id']} - {data[idx].get('name', 'N/A')}")
        else:
            print(f"Skipped (already has solutions): {data[idx]['id']}")

    # Write back to JSON file with exclusive lock
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\nTotal updated: {updated_count} problems")

if __name__ == '__main__':
    main()
