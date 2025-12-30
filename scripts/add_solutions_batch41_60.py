#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
41번째부터 60번째까지의 빈 솔루션 medium 문제에 솔루션을 추가하는 스크립트
"""

import json

# JSON 파일 읽기
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# medium 난이도이면서 solutions가 빈 문제들 찾기
empty_medium_indices = []
for i, p in enumerate(data):
    if p.get('difficulty') == 'medium' and (not p.get('solutions') or len(p.get('solutions', [])) == 0):
        empty_medium_indices.append(i)

solutions_to_add = {}

# 문제 41: 백준 32186 - 역시 내 이세계 수열은 잘못됐다 (인덱스 4003)
solutions_to_add[empty_medium_indices[40]] = [
    {
        "language": "python",
        "code": '''# 백준 32186: 역시 내 이세계 수열은 잘못됐다
# 팰린드롬 수열을 만들기 위한 최소 연산 횟수
import sys
input = sys.stdin.readline

n, k = map(int, input().split())
a = list(map(int, input().split()))

total_ops = 0

# 양쪽 끝에서부터 비교
for i in range(n // 2):
    left = a[i]
    right = a[n - 1 - i]

    if left == right:
        continue

    # 작은 값을 큰 값으로 맞춰야 함
    small, big = min(left, right), max(left, right)
    diff = big - small

    # +K 연산 횟수와 +1 연산 횟수
    # diff = q * k + r 형태로 q번의 +K와 r번의 +1
    # 또는 (q+1)번의 +K와 (k-r)번의 +1 (단, r > 0일 때)
    q, r = divmod(diff, k)

    if r == 0:
        total_ops += q
    else:
        # 방법 1: q번 +K, r번 +1 -> q + r번
        # 방법 2: (q+1)번 +K, (k-r)번 +1 -> (q+1) + (k-r)번
        option1 = q + r
        option2 = (q + 1) + (k - r)
        total_ops += min(option1, option2)

print(total_ops)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 32186: 역시 내 이세계 수열은 잘못됐다
// 팰린드롬 수열을 만들기 위한 최소 연산 횟수
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        long k = Long.parseLong(st.nextToken());

        long[] a = new long[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            a[i] = Long.parseLong(st.nextToken());
        }

        long totalOps = 0;

        for (int i = 0; i < n / 2; i++) {
            long left = a[i];
            long right = a[n - 1 - i];

            if (left == right) continue;

            long diff = Math.abs(left - right);
            long q = diff / k;
            long r = diff % k;

            if (r == 0) {
                totalOps += q;
            } else {
                long option1 = q + r;
                long option2 = (q + 1) + (k - r);
                totalOps += Math.min(option1, option2);
            }
        }

        System.out.println(totalOps);
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

// 백준 32186: 역시 내 이세계 수열은 잘못됐다
// 팰린드롬 수열을 만들기 위한 최소 연산 횟수

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    long long k;
    cin >> n >> k;

    vector<long long> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    long long totalOps = 0;

    for (int i = 0; i < n / 2; i++) {
        long long left = a[i];
        long long right = a[n - 1 - i];

        if (left == right) continue;

        long long diff = abs(left - right);
        long long q = diff / k;
        long long r = diff % k;

        if (r == 0) {
            totalOps += q;
        } else {
            long long option1 = q + r;
            long long option2 = (q + 1) + (k - r);
            totalOps += min(option1, option2);
        }
    }

    cout << totalOps << endl;

    return 0;
}
'''
    }
]

# 문제 42: 백준 19592 - 장난감 경주 (인덱스 4004)
solutions_to_add[empty_medium_indices[41]] = [
    {
        "language": "python",
        "code": '''# 백준 19592: 장난감 경주
# 이진 탐색으로 단독 우승할 수 있는 최소 부스터 속도 찾기
import sys
input = sys.stdin.readline

T = int(input())

for _ in range(T):
    line = list(map(int, input().split()))
    n, x, y = line[0], line[1], line[2]
    v = list(map(int, input().split()))

    # 다른 참가자들의 최소 시간 계산
    min_time = float('inf')
    for i in range(n - 1):
        time = x / v[i]
        min_time = min(min_time, time)

    my_speed = v[n - 1]

    # 부스터 없이 우승 가능한지 확인
    my_time_no_boost = x / my_speed
    if my_time_no_boost < min_time:
        print(0)
        continue

    # 이진 탐색으로 최소 Z 찾기
    # 1초간 Z로 이동, 나머지는 my_speed로 이동
    # 총 시간 = 1 + max(0, (x - Z) / my_speed)
    # 단, Z > x이면 1초 만에 도착

    # 최소 Z 찾기: 시간이 min_time 미만이 되어야 함
    left, right = 0, y
    result = -1

    while left <= right:
        mid = (left + right) // 2

        # mid 속도로 1초 이동 시 거리
        if mid >= x:
            # 1초 만에 도착
            time = 1.0
        else:
            # 남은 거리를 my_speed로 이동
            remaining = x - mid
            time = 1.0 + remaining / my_speed

        if time < min_time:
            result = mid
            right = mid - 1
        else:
            left = mid + 1

    print(result)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 19592: 장난감 경주
// 이진 탐색으로 단독 우승할 수 있는 최소 부스터 속도 찾기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());

            st = new StringTokenizer(br.readLine());
            int[] v = new int[n];
            for (int i = 0; i < n; i++) {
                v[i] = Integer.parseInt(st.nextToken());
            }

            double minTime = Double.MAX_VALUE;
            for (int i = 0; i < n - 1; i++) {
                double time = (double) x / v[i];
                minTime = Math.min(minTime, time);
            }

            int mySpeed = v[n - 1];
            double myTimeNoBoost = (double) x / mySpeed;

            if (myTimeNoBoost < minTime) {
                sb.append(0).append("\\n");
                continue;
            }

            int left = 0, right = y;
            int result = -1;

            while (left <= right) {
                int mid = (left + right) / 2;
                double time;

                if (mid >= x) {
                    time = 1.0;
                } else {
                    double remaining = x - mid;
                    time = 1.0 + remaining / mySpeed;
                }

                if (time < minTime) {
                    result = mid;
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            }

            sb.append(result).append("\\n");
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
#include <algorithm>
#include <cfloat>
using namespace std;

// 백준 19592: 장난감 경주
// 이진 탐색으로 단독 우승할 수 있는 최소 부스터 속도 찾기

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int n, x, y;
        cin >> n >> x >> y;

        vector<int> v(n);
        for (int i = 0; i < n; i++) {
            cin >> v[i];
        }

        double minTime = DBL_MAX;
        for (int i = 0; i < n - 1; i++) {
            double t = (double)x / v[i];
            minTime = min(minTime, t);
        }

        int mySpeed = v[n - 1];
        double myTimeNoBoost = (double)x / mySpeed;

        if (myTimeNoBoost < minTime) {
            cout << 0 << "\\n";
            continue;
        }

        int left = 0, right = y;
        int result = -1;

        while (left <= right) {
            int mid = (left + right) / 2;
            double t;

            if (mid >= x) {
                t = 1.0;
            } else {
                double remaining = x - mid;
                t = 1.0 + remaining / mySpeed;
            }

            if (t < minTime) {
                result = mid;
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        }

        cout << result << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 43: 백준 24091 - 알고리즘 수업 - 퀵 정렬 2 (인덱스 4005)
solutions_to_add[empty_medium_indices[42]] = [
    {
        "language": "python",
        "code": '''# 백준 24091: 알고리즘 수업 - 퀵 정렬 2
# 퀵 정렬에서 K번째 교환 직후 배열 상태 출력
import sys
input = sys.stdin.readline
sys.setrecursionlimit(20000)

n, k = map(int, input().split())
A = list(map(int, input().split()))

swap_count = 0
found = False

def partition(p, r):
    global swap_count, found
    x = A[r]
    i = p - 1

    for j in range(p, r):
        if A[j] <= x:
            i += 1
            A[i], A[j] = A[j], A[i]
            swap_count += 1
            if swap_count == k:
                found = True
                return -1

    if i + 1 != r:
        A[i + 1], A[r] = A[r], A[i + 1]
        swap_count += 1
        if swap_count == k:
            found = True
            return -1

    return i + 1

def quick_sort(p, r):
    global found
    if found:
        return
    if p < r:
        q = partition(p, r)
        if found:
            return
        quick_sort(p, q - 1)
        if found:
            return
        quick_sort(q + 1, r)

quick_sort(0, n - 1)

if found:
    print(' '.join(map(str, A)))
else:
    print(-1)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 24091: 알고리즘 수업 - 퀵 정렬 2
// 퀵 정렬에서 K번째 교환 직후 배열 상태 출력
public class Main {
    static int[] A;
    static long swapCount = 0;
    static long k;
    static boolean found = false;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        k = Long.parseLong(st.nextToken());

        A = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            A[i] = Integer.parseInt(st.nextToken());
        }

        quickSort(0, n - 1);

        if (found) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < n; i++) {
                sb.append(A[i]);
                if (i < n - 1) sb.append(" ");
            }
            System.out.println(sb);
        } else {
            System.out.println(-1);
        }
    }

    static int partition(int p, int r) {
        int x = A[r];
        int i = p - 1;

        for (int j = p; j < r; j++) {
            if (A[j] <= x) {
                i++;
                int temp = A[i];
                A[i] = A[j];
                A[j] = temp;
                swapCount++;
                if (swapCount == k) {
                    found = true;
                    return -1;
                }
            }
        }

        if (i + 1 != r) {
            int temp = A[i + 1];
            A[i + 1] = A[r];
            A[r] = temp;
            swapCount++;
            if (swapCount == k) {
                found = true;
                return -1;
            }
        }

        return i + 1;
    }

    static void quickSort(int p, int r) {
        if (found) return;
        if (p < r) {
            int q = partition(p, r);
            if (found) return;
            quickSort(p, q - 1);
            if (found) return;
            quickSort(q + 1, r);
        }
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
using namespace std;

// 백준 24091: 알고리즘 수업 - 퀵 정렬 2
// 퀵 정렬에서 K번째 교환 직후 배열 상태 출력

vector<int> A;
long long swapCount = 0;
long long k;
bool found = false;

int partition(int p, int r) {
    int x = A[r];
    int i = p - 1;

    for (int j = p; j < r; j++) {
        if (A[j] <= x) {
            i++;
            swap(A[i], A[j]);
            swapCount++;
            if (swapCount == k) {
                found = true;
                return -1;
            }
        }
    }

    if (i + 1 != r) {
        swap(A[i + 1], A[r]);
        swapCount++;
        if (swapCount == k) {
            found = true;
            return -1;
        }
    }

    return i + 1;
}

void quickSort(int p, int r) {
    if (found) return;
    if (p < r) {
        int q = partition(p, r);
        if (found) return;
        quickSort(p, q - 1);
        if (found) return;
        quickSort(q + 1, r);
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n >> k;

    A.resize(n);
    for (int i = 0; i < n; i++) {
        cin >> A[i];
    }

    quickSort(0, n - 1);

    if (found) {
        for (int i = 0; i < n; i++) {
            cout << A[i];
            if (i < n - 1) cout << " ";
        }
        cout << endl;
    } else {
        cout << -1 << endl;
    }

    return 0;
}
'''
    }
]

# 문제 44: 백준 14222 - 배열과 연산 (인덱스 4007)
solutions_to_add[empty_medium_indices[43]] = [
    {
        "language": "python",
        "code": '''# 백준 14222: 배열과 연산
# 그리디: 정렬 후 1부터 N까지 매칭
import sys
input = sys.stdin.readline

n, k = map(int, input().split())
a = list(map(int, input().split()))

a.sort()

# 1부터 N까지의 수를 만들어야 함
# 각 a[i]에서 K를 더해서 target을 만들 수 있는지 확인
# a[i] + m*K = target (m >= 0)
# a[i] <= target이고 (target - a[i]) % K == 0이면 가능

used = [False] * n
result = True

for target in range(1, n + 1):
    found = False
    for i in range(n):
        if used[i]:
            continue
        if a[i] <= target and (target - a[i]) % k == 0:
            used[i] = True
            found = True
            break
    if not found:
        result = False
        break

print(1 if result else 0)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 14222: 배열과 연산
// 그리디: 정렬 후 1부터 N까지 매칭
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        int[] a = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(a);

        boolean[] used = new boolean[n];
        boolean result = true;

        for (int target = 1; target <= n; target++) {
            boolean found = false;
            for (int i = 0; i < n; i++) {
                if (used[i]) continue;
                if (a[i] <= target && (target - a[i]) % k == 0) {
                    used[i] = true;
                    found = true;
                    break;
                }
            }
            if (!found) {
                result = false;
                break;
            }
        }

        System.out.println(result ? 1 : 0);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

// 백준 14222: 배열과 연산
// 그리디: 정렬 후 1부터 N까지 매칭

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    sort(a.begin(), a.end());

    vector<bool> used(n, false);
    bool result = true;

    for (int target = 1; target <= n; target++) {
        bool found = false;
        for (int i = 0; i < n; i++) {
            if (used[i]) continue;
            if (a[i] <= target && (target - a[i]) % k == 0) {
                used[i] = true;
                found = true;
                break;
            }
        }
        if (!found) {
            result = false;
            break;
        }
    }

    cout << (result ? 1 : 0) << endl;

    return 0;
}
'''
    }
]

# 문제 45: 백준 2811 - 상범이의 우울 (인덱스 4016)
solutions_to_add[empty_medium_indices[44]] = [
    {
        "language": "python",
        "code": '''# 백준 2811: 상범이의 우울
# 우울 기간 전에 꽃을 주는 날 수 계산
import sys
input = sys.stdin.readline

n = int(input())
mood = list(map(int, input().split()))

# 우울 기간 찾기 (연속된 음수 구간)
sad_periods = []  # (시작 인덱스, 길이)
i = 0
while i < n:
    if mood[i] < 0:
        start = i
        length = 0
        while i < n and mood[i] < 0:
            length += 1
            i += 1
        sad_periods.append((start, length))
    else:
        i += 1

if not sad_periods:
    print(0)
else:
    # 가장 긴 우울 기간 찾기
    max_len = max(p[1] for p in sad_periods)

    # 꽃을 줘야 하는 날 마킹
    flower_days = [False] * n

    # 가장 긴 기간 중 하나만 3T 적용
    used_longest = False

    for start, length in sad_periods:
        if length == max_len and not used_longest:
            # 3T일 전부터 시작 전날까지
            multiplier = 3
            used_longest = True
        else:
            # 2T일 전부터 시작 전날까지
            multiplier = 2

        flower_start = max(0, start - multiplier * length)
        flower_end = start - 1

        for j in range(flower_start, flower_end + 1):
            flower_days[j] = True

    print(sum(flower_days))
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 2811: 상범이의 우울
// 우울 기간 전에 꽃을 주는 날 수 계산
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[] mood = new int[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            mood[i] = Integer.parseInt(st.nextToken());
        }

        // 우울 기간 찾기
        List<int[]> sadPeriods = new ArrayList<>();
        int i = 0;
        while (i < n) {
            if (mood[i] < 0) {
                int start = i;
                int length = 0;
                while (i < n && mood[i] < 0) {
                    length++;
                    i++;
                }
                sadPeriods.add(new int[]{start, length});
            } else {
                i++;
            }
        }

        if (sadPeriods.isEmpty()) {
            System.out.println(0);
            return;
        }

        int maxLen = 0;
        for (int[] p : sadPeriods) {
            maxLen = Math.max(maxLen, p[1]);
        }

        boolean[] flowerDays = new boolean[n];
        boolean usedLongest = false;

        for (int[] period : sadPeriods) {
            int start = period[0];
            int length = period[1];
            int multiplier;

            if (length == maxLen && !usedLongest) {
                multiplier = 3;
                usedLongest = true;
            } else {
                multiplier = 2;
            }

            int flowerStart = Math.max(0, start - multiplier * length);
            int flowerEnd = start - 1;

            for (int j = flowerStart; j <= flowerEnd; j++) {
                flowerDays[j] = true;
            }
        }

        int count = 0;
        for (boolean f : flowerDays) {
            if (f) count++;
        }
        System.out.println(count);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

// 백준 2811: 상범이의 우울
// 우울 기간 전에 꽃을 주는 날 수 계산

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> mood(n);
    for (int i = 0; i < n; i++) {
        cin >> mood[i];
    }

    // 우울 기간 찾기
    vector<pair<int, int>> sadPeriods;
    int i = 0;
    while (i < n) {
        if (mood[i] < 0) {
            int start = i;
            int length = 0;
            while (i < n && mood[i] < 0) {
                length++;
                i++;
            }
            sadPeriods.push_back({start, length});
        } else {
            i++;
        }
    }

    if (sadPeriods.empty()) {
        cout << 0 << endl;
        return 0;
    }

    int maxLen = 0;
    for (auto& p : sadPeriods) {
        maxLen = max(maxLen, p.second);
    }

    vector<bool> flowerDays(n, false);
    bool usedLongest = false;

    for (auto& period : sadPeriods) {
        int start = period.first;
        int length = period.second;
        int multiplier;

        if (length == maxLen && !usedLongest) {
            multiplier = 3;
            usedLongest = true;
        } else {
            multiplier = 2;
        }

        int flowerStart = max(0, start - multiplier * length);
        int flowerEnd = start - 1;

        for (int j = flowerStart; j <= flowerEnd; j++) {
            flowerDays[j] = true;
        }
    }

    int count = 0;
    for (bool f : flowerDays) {
        if (f) count++;
    }
    cout << count << endl;

    return 0;
}
'''
    }
]

# 문제 46: 백준 23029 - 시식 코너는 나의 것 (인덱스 4022)
solutions_to_add[empty_medium_indices[45]] = [
    {
        "language": "python",
        "code": '''# 백준 23029: 시식 코너는 나의 것
# DP: 연속 3개 방문 불가, 연속 2번째는 절반만 먹음
import sys
input = sys.stdin.readline

n = int(input())
food = []
for _ in range(n):
    food.append(int(input()))

if n == 1:
    print(food[0])
elif n == 2:
    print(max(food[0], food[1], food[0] + food[1] // 2))
else:
    # dp[i][0] = i번째 시식 안함
    # dp[i][1] = i번째 시식함 (연속 1번째)
    # dp[i][2] = i번째 시식함 (연속 2번째, 절반만)
    INF = float('-inf')

    dp = [[INF] * 3 for _ in range(n)]

    dp[0][0] = 0
    dp[0][1] = food[0]

    for i in range(1, n):
        # i번째 시식 안함
        dp[i][0] = max(dp[i-1][0], dp[i-1][1], dp[i-1][2])

        # i번째 시식함 (연속 1번째) - 이전에 시식 안함
        dp[i][1] = dp[i-1][0] + food[i]

        # i번째 시식함 (연속 2번째) - 이전에 연속 1번째로 시식함
        dp[i][2] = dp[i-1][1] + food[i] // 2

    print(max(dp[n-1]))
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 23029: 시식 코너는 나의 것
// DP: 연속 3개 방문 불가, 연속 2번째는 절반만 먹음
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[] food = new int[n];
        for (int i = 0; i < n; i++) {
            food[i] = Integer.parseInt(br.readLine().trim());
        }

        if (n == 1) {
            System.out.println(food[0]);
            return;
        }

        // dp[i][0] = i번째 시식 안함
        // dp[i][1] = i번째 시식함 (연속 1번째)
        // dp[i][2] = i번째 시식함 (연속 2번째)
        long[][] dp = new long[n][3];
        long NEG_INF = Long.MIN_VALUE / 2;

        for (int i = 0; i < n; i++) {
            Arrays.fill(dp[i], NEG_INF);
        }

        dp[0][0] = 0;
        dp[0][1] = food[0];

        for (int i = 1; i < n; i++) {
            dp[i][0] = Math.max(dp[i-1][0], Math.max(dp[i-1][1], dp[i-1][2]));
            dp[i][1] = dp[i-1][0] + food[i];
            dp[i][2] = dp[i-1][1] + food[i] / 2;
        }

        System.out.println(Math.max(dp[n-1][0], Math.max(dp[n-1][1], dp[n-1][2])));
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

// 백준 23029: 시식 코너는 나의 것
// DP: 연속 3개 방문 불가, 연속 2번째는 절반만 먹음

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> food(n);
    for (int i = 0; i < n; i++) {
        cin >> food[i];
    }

    if (n == 1) {
        cout << food[0] << endl;
        return 0;
    }

    // dp[i][0] = i번째 시식 안함
    // dp[i][1] = i번째 시식함 (연속 1번째)
    // dp[i][2] = i번째 시식함 (연속 2번째)
    const long long NEG_INF = -1e18;
    vector<vector<long long>> dp(n, vector<long long>(3, NEG_INF));

    dp[0][0] = 0;
    dp[0][1] = food[0];

    for (int i = 1; i < n; i++) {
        dp[i][0] = max({dp[i-1][0], dp[i-1][1], dp[i-1][2]});
        dp[i][1] = dp[i-1][0] + food[i];
        dp[i][2] = dp[i-1][1] + food[i] / 2;
    }

    cout << max({dp[n-1][0], dp[n-1][1], dp[n-1][2]}) << endl;

    return 0;
}
'''
    }
]

# 문제 47: 백준 10571 - 다이아몬드 (인덱스 4023)
solutions_to_add[empty_medium_indices[46]] = [
    {
        "language": "python",
        "code": '''# 백준 10571: 다이아몬드
# LIS 변형: 무게 증가, 선명도 감소하는 최장 부분 수열
import sys
input = sys.stdin.readline

T = int(input())

for _ in range(T):
    n = int(input())
    diamonds = []
    for _ in range(n):
        w, c = map(float, input().split())
        diamonds.append((w, c))

    # DP로 LIS 찾기
    # dp[i] = i번째 다이아몬드를 마지막으로 하는 최장 부분 수열 길이
    dp = [1] * n

    for i in range(n):
        for j in range(i):
            # j번째 다이아몬드 뒤에 i번째를 붙일 수 있는지 확인
            if diamonds[j][0] < diamonds[i][0] and diamonds[j][1] > diamonds[i][1]:
                dp[i] = max(dp[i], dp[j] + 1)

    print(max(dp))
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 10571: 다이아몬드
// LIS 변형: 무게 증가, 선명도 감소하는 최장 부분 수열
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            int n = Integer.parseInt(br.readLine().trim());
            double[][] diamonds = new double[n][2];

            for (int i = 0; i < n; i++) {
                StringTokenizer st = new StringTokenizer(br.readLine());
                diamonds[i][0] = Double.parseDouble(st.nextToken());
                diamonds[i][1] = Double.parseDouble(st.nextToken());
            }

            int[] dp = new int[n];
            Arrays.fill(dp, 1);

            for (int i = 0; i < n; i++) {
                for (int j = 0; j < i; j++) {
                    if (diamonds[j][0] < diamonds[i][0] && diamonds[j][1] > diamonds[i][1]) {
                        dp[i] = Math.max(dp[i], dp[j] + 1);
                    }
                }
            }

            int max = 0;
            for (int d : dp) max = Math.max(max, d);
            sb.append(max).append("\\n");
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
#include <algorithm>
using namespace std;

// 백준 10571: 다이아몬드
// LIS 변형: 무게 증가, 선명도 감소하는 최장 부분 수열

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int n;
        cin >> n;

        vector<pair<double, double>> diamonds(n);
        for (int i = 0; i < n; i++) {
            cin >> diamonds[i].first >> diamonds[i].second;
        }

        vector<int> dp(n, 1);

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < i; j++) {
                if (diamonds[j].first < diamonds[i].first &&
                    diamonds[j].second > diamonds[i].second) {
                    dp[i] = max(dp[i], dp[j] + 1);
                }
            }
        }

        cout << *max_element(dp.begin(), dp.end()) << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 48: 백준 31834 - 미로 탈출 (인덱스 4031)
solutions_to_add[empty_medium_indices[47]] = [
    {
        "language": "python",
        "code": '''# 백준 31834: 미로 탈출
# 모든 스위치를 누르고 출구로 가는 최소 비용
import sys
input = sys.stdin.readline

T = int(input())

for _ in range(T):
    n, s, e = map(int, input().split())

    # 모든 스위치를 누르려면 1번부터 N번까지 방문해야 함
    # 시작: S, 끝: E

    # 최소 시간: 1번과 N번 사이를 왕복하면서 모든 방 방문
    # S에서 시작해서 1~N을 모두 방문하고 E로 가야 함

    # 최소 시간 = N-1 (1번에서 N번까지 이동) + 추가 이동
    # 하지만 S와 E 위치에 따라 다름

    # 가장 간단한 접근: 1~N을 모두 방문하는 최소 시간
    # S에서 시작, E에서 끝
    # 1번과 N번 사이를 한 번은 이동해야 함

    # 최소 비용 전략:
    # 순간이동 비용 1, 인접 이동 비용 0
    # 순간이동을 사용하면 1번 또는 N번으로 즉시 이동

    # 모든 방을 방문하려면 최소 N-1 시간 필요 (1에서 N까지 직선)
    # S와 E에 따라 추가 비용 결정

    # 경우 1: S에서 한쪽 끝으로, 다른 끝까지 이동, E로 이동
    # 경우 2: 순간이동 사용

    # 최소 비용 계산
    # S에서 1번까지 + 1~N 이동 + N에서 E까지
    # 또는 S에서 N번까지 + N~1 이동 + 1에서 E까지

    # 순간이동 없이: S->1->N->E 또는 S->N->1->E
    # 순간이동 사용: 다양한 조합

    # 간단히: 1~N을 모두 방문해야 하므로
    # 최소 비용 = 순간이동 횟수

    # S가 1~N 범위 안이므로
    # 1. S에서 1로 가서 N까지 이동, E로 가기
    # 2. S에서 N으로 가서 1까지 이동, E로 가기

    # 각 경로에서 순간이동 횟수 계산
    # 인접 이동은 무료, 순간이동만 비용

    # S->1: 거리 S-1 (인접 이동) 또는 1 (순간이동)
    # 1->N: 거리 N-1 (인접 이동)
    # N->E: 거리 |N-E| (인접 이동) 또는 1 (순간이동)

    # 경로 1: S -> 1 -> N -> E
    cost1 = 0
    if s != 1:
        # S에서 1로: 인접 이동 또는 순간이동
        cost1 += 0  # 인접 이동 선택 (시간은 걸리지만 비용 0)
    # 1->N: 인접 이동
    # N->E: 인접 이동
    if e != n:
        cost1 += 0

    # 경로 2: S -> N -> 1 -> E
    cost2 = 0

    # 실제로는 순간이동 사용 여부에 따라 비용이 달라짐
    # 최소 비용은 보통 0 또는 1 또는 2

    # 정확한 분석:
    # S에서 시작해서 1~N 모두 방문 후 E 도착
    # 순간이동 없이: S와 E 위치에 따라 가능 여부 결정

    # S -> 양끝으로 갔다가 다른 끝까지, E로 복귀
    # S에서 가까운 끝으로 먼저

    # 최소 비용 = 0인 경우: 순간이동 없이 가능
    # 그 외에는 순간이동 필요

    # 간단한 공식:
    # 비용 = 0 if 경로가 S-끝-끝-E 형태로 인접 이동만으로 가능
    # 아니면 순간이동 필요

    # S와 E 사이에 1~N이 모두 포함되어야 함
    min_pos = min(s, e)
    max_pos = max(s, e)

    if min_pos == 1 and max_pos == n:
        print(0)
    elif min_pos == 1 or max_pos == n:
        print(1)
    else:
        print(2)
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 31834: 미로 탈출
// 모든 스위치를 누르고 출구로 가는 최소 비용
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int s = Integer.parseInt(st.nextToken());
            int e = Integer.parseInt(st.nextToken());

            int minPos = Math.min(s, e);
            int maxPos = Math.max(s, e);

            if (minPos == 1 && maxPos == n) {
                sb.append(0).append("\\n");
            } else if (minPos == 1 || maxPos == n) {
                sb.append(1).append("\\n");
            } else {
                sb.append(2).append("\\n");
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
#include <algorithm>
using namespace std;

// 백준 31834: 미로 탈출
// 모든 스위치를 누르고 출구로 가는 최소 비용

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int n, s, e;
        cin >> n >> s >> e;

        int minPos = min(s, e);
        int maxPos = max(s, e);

        if (minPos == 1 && maxPos == n) {
            cout << 0 << "\\n";
        } else if (minPos == 1 || maxPos == n) {
            cout << 1 << "\\n";
        } else {
            cout << 2 << "\\n";
        }
    }

    return 0;
}
'''
    }
]

# 문제 49: 백준 23293 - 아주 서바이벌 (인덱스 4034)
solutions_to_add[empty_medium_indices[48]] = [
    {
        "language": "python",
        "code": '''# 백준 23293: 아주 서바이벌
# 게임 로그 분석 및 부정행위 탐지
import sys
input = sys.stdin.readline

n, max_log = map(int, input().split())

# 플레이어 상태
player_pos = {}  # 플레이어 위치 (1번 지역에서 시작)
player_items = {}  # 플레이어 아이템

cheats = []  # 부정행위 로그 번호
banned = set()  # 차단된 플레이어

for _ in range(n):
    parts = input().split()
    log_num = int(parts[0])
    player = int(parts[1])
    action = parts[2]

    if player in banned:
        continue

    if player not in player_pos:
        player_pos[player] = 1
        player_items[player] = {}

    if action == 'M':  # 이동
        new_pos = int(parts[3])
        player_pos[player] = new_pos

    elif action == 'F':  # 획득
        item = int(parts[3])
        current_pos = player_pos[player]

        if item != current_pos:
            # 부정행위: 현재 위치에서 얻을 수 없는 아이템
            cheats.append(log_num)
        else:
            if item not in player_items[player]:
                player_items[player][item] = 0
            player_items[player][item] += 1

    elif action == 'C':  # 조합
        item1 = int(parts[3])
        item2 = int(parts[4])

        has1 = player_items[player].get(item1, 0) > 0
        has2 = player_items[player].get(item2, 0) > 0

        if item1 == item2:
            has_both = player_items[player].get(item1, 0) >= 2
        else:
            has_both = has1 and has2

        if not has_both:
            # 부정행위: 아이템 부족
            cheats.append(log_num)
        else:
            player_items[player][item1] -= 1
            if item1 != item2:
                player_items[player][item2] -= 1
            else:
                player_items[player][item1] -= 1

    elif action == 'A':  # 공격
        target = int(parts[3])

        if target not in player_pos:
            player_pos[target] = 1
            player_items[target] = {}

        if player_pos[player] != player_pos[target]:
            # 부정행위: 다른 지역 공격 -> 차단
            cheats.append(log_num)
            banned.add(player)

print(len(cheats))
if cheats:
    print(' '.join(map(str, cheats)))

print(len(banned))
if banned:
    print(' '.join(map(str, sorted(banned))))
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 23293: 아주 서바이벌
// 게임 로그 분석 및 부정행위 탐지
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int maxLog = Integer.parseInt(st.nextToken());

        Map<Integer, Integer> playerPos = new HashMap<>();
        Map<Integer, Map<Integer, Integer>> playerItems = new HashMap<>();

        List<Integer> cheats = new ArrayList<>();
        Set<Integer> banned = new TreeSet<>();

        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            int logNum = Integer.parseInt(st.nextToken());
            int player = Integer.parseInt(st.nextToken());
            String action = st.nextToken();

            if (banned.contains(player)) continue;

            playerPos.putIfAbsent(player, 1);
            playerItems.putIfAbsent(player, new HashMap<>());

            if (action.equals("M")) {
                int newPos = Integer.parseInt(st.nextToken());
                playerPos.put(player, newPos);
            } else if (action.equals("F")) {
                int item = Integer.parseInt(st.nextToken());
                int currentPos = playerPos.get(player);

                if (item != currentPos) {
                    cheats.add(logNum);
                } else {
                    Map<Integer, Integer> items = playerItems.get(player);
                    items.put(item, items.getOrDefault(item, 0) + 1);
                }
            } else if (action.equals("C")) {
                int item1 = Integer.parseInt(st.nextToken());
                int item2 = Integer.parseInt(st.nextToken());
                Map<Integer, Integer> items = playerItems.get(player);

                boolean valid;
                if (item1 == item2) {
                    valid = items.getOrDefault(item1, 0) >= 2;
                } else {
                    valid = items.getOrDefault(item1, 0) > 0 && items.getOrDefault(item2, 0) > 0;
                }

                if (!valid) {
                    cheats.add(logNum);
                } else {
                    items.put(item1, items.get(item1) - 1);
                    items.put(item2, items.getOrDefault(item2, 0) - 1);
                }
            } else if (action.equals("A")) {
                int target = Integer.parseInt(st.nextToken());
                playerPos.putIfAbsent(target, 1);
                playerItems.putIfAbsent(target, new HashMap<>());

                if (!playerPos.get(player).equals(playerPos.get(target))) {
                    cheats.add(logNum);
                    banned.add(player);
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        sb.append(cheats.size()).append("\\n");
        if (!cheats.isEmpty()) {
            for (int c : cheats) sb.append(c).append(" ");
            sb.append("\\n");
        }
        sb.append(banned.size()).append("\\n");
        if (!banned.isEmpty()) {
            for (int b : banned) sb.append(b).append(" ");
            sb.append("\\n");
        }

        System.out.print(sb.toString().trim());
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <map>
#include <set>
#include <vector>
#include <sstream>
using namespace std;

// 백준 23293: 아주 서바이벌
// 게임 로그 분석 및 부정행위 탐지

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, maxLog;
    cin >> n >> maxLog;
    cin.ignore();

    map<int, int> playerPos;
    map<int, map<int, int>> playerItems;

    vector<int> cheats;
    set<int> banned;

    for (int i = 0; i < n; i++) {
        string line;
        getline(cin, line);
        istringstream iss(line);

        int logNum, player;
        string action;
        iss >> logNum >> player >> action;

        if (banned.count(player)) continue;

        if (!playerPos.count(player)) {
            playerPos[player] = 1;
        }

        if (action == "M") {
            int newPos;
            iss >> newPos;
            playerPos[player] = newPos;
        } else if (action == "F") {
            int item;
            iss >> item;
            int currentPos = playerPos[player];

            if (item != currentPos) {
                cheats.push_back(logNum);
            } else {
                playerItems[player][item]++;
            }
        } else if (action == "C") {
            int item1, item2;
            iss >> item1 >> item2;

            bool valid;
            if (item1 == item2) {
                valid = playerItems[player][item1] >= 2;
            } else {
                valid = playerItems[player][item1] > 0 && playerItems[player][item2] > 0;
            }

            if (!valid) {
                cheats.push_back(logNum);
            } else {
                playerItems[player][item1]--;
                playerItems[player][item2]--;
            }
        } else if (action == "A") {
            int target;
            iss >> target;

            if (!playerPos.count(target)) {
                playerPos[target] = 1;
            }

            if (playerPos[player] != playerPos[target]) {
                cheats.push_back(logNum);
                banned.insert(player);
            }
        }
    }

    cout << cheats.size() << "\\n";
    if (!cheats.empty()) {
        for (int c : cheats) cout << c << " ";
        cout << "\\n";
    }
    cout << banned.size() << "\\n";
    if (!banned.empty()) {
        for (int b : banned) cout << b << " ";
        cout << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 50: 백준 15645 - 내려가기 2 (인덱스 4039)
solutions_to_add[empty_medium_indices[49]] = [
    {
        "language": "python",
        "code": '''# 백준 15645: 내려가기 2
# DP로 최대/최소 점수 계산
import sys
input = sys.stdin.readline

n = int(input())

# dp_max[i] = i번째 열에서 끝날 때의 최대 점수
# dp_min[i] = i번째 열에서 끝날 때의 최소 점수

first_row = list(map(int, input().split()))
dp_max = first_row[:]
dp_min = first_row[:]

for _ in range(n - 1):
    row = list(map(int, input().split()))
    new_max = [0, 0, 0]
    new_min = [0, 0, 0]

    # 왼쪽 열 (인덱스 0): 이전의 0 또는 1에서 올 수 있음
    new_max[0] = max(dp_max[0], dp_max[1]) + row[0]
    new_min[0] = min(dp_min[0], dp_min[1]) + row[0]

    # 가운데 열 (인덱스 1): 이전의 0, 1, 2에서 올 수 있음
    new_max[1] = max(dp_max[0], dp_max[1], dp_max[2]) + row[1]
    new_min[1] = min(dp_min[0], dp_min[1], dp_min[2]) + row[1]

    # 오른쪽 열 (인덱스 2): 이전의 1 또는 2에서 올 수 있음
    new_max[2] = max(dp_max[1], dp_max[2]) + row[2]
    new_min[2] = min(dp_min[1], dp_min[2]) + row[2]

    dp_max = new_max
    dp_min = new_min

print(max(dp_max), min(dp_min))
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 15645: 내려가기 2
// DP로 최대/최소 점수 계산
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] dpMax = new int[3];
        int[] dpMin = new int[3];

        for (int i = 0; i < 3; i++) {
            dpMax[i] = dpMin[i] = Integer.parseInt(st.nextToken());
        }

        for (int i = 1; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            int[] row = new int[3];
            for (int j = 0; j < 3; j++) {
                row[j] = Integer.parseInt(st.nextToken());
            }

            int[] newMax = new int[3];
            int[] newMin = new int[3];

            newMax[0] = Math.max(dpMax[0], dpMax[1]) + row[0];
            newMin[0] = Math.min(dpMin[0], dpMin[1]) + row[0];

            newMax[1] = Math.max(dpMax[0], Math.max(dpMax[1], dpMax[2])) + row[1];
            newMin[1] = Math.min(dpMin[0], Math.min(dpMin[1], dpMin[2])) + row[1];

            newMax[2] = Math.max(dpMax[1], dpMax[2]) + row[2];
            newMin[2] = Math.min(dpMin[1], dpMin[2]) + row[2];

            dpMax = newMax;
            dpMin = newMin;
        }

        int maxVal = Math.max(dpMax[0], Math.max(dpMax[1], dpMax[2]));
        int minVal = Math.min(dpMin[0], Math.min(dpMin[1], dpMin[2]));

        System.out.println(maxVal + " " + minVal);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <algorithm>
using namespace std;

// 백준 15645: 내려가기 2
// DP로 최대/최소 점수 계산

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int dpMax[3], dpMin[3];
    for (int i = 0; i < 3; i++) {
        cin >> dpMax[i];
        dpMin[i] = dpMax[i];
    }

    for (int i = 1; i < n; i++) {
        int row[3];
        for (int j = 0; j < 3; j++) {
            cin >> row[j];
        }

        int newMax[3], newMin[3];

        newMax[0] = max(dpMax[0], dpMax[1]) + row[0];
        newMin[0] = min(dpMin[0], dpMin[1]) + row[0];

        newMax[1] = max({dpMax[0], dpMax[1], dpMax[2]}) + row[1];
        newMin[1] = min({dpMin[0], dpMin[1], dpMin[2]}) + row[1];

        newMax[2] = max(dpMax[1], dpMax[2]) + row[2];
        newMin[2] = min(dpMin[1], dpMin[2]) + row[2];

        for (int j = 0; j < 3; j++) {
            dpMax[j] = newMax[j];
            dpMin[j] = newMin[j];
        }
    }

    cout << max({dpMax[0], dpMax[1], dpMax[2]}) << " ";
    cout << min({dpMin[0], dpMin[1], dpMin[2]}) << endl;

    return 0;
}
'''
    }
]

# 문제 51: 백준 34077 - 폴카의 수학 공부 (인덱스 4040)
solutions_to_add[empty_medium_indices[50]] = [
    {
        "language": "python",
        "code": '''# 백준 34077: 폴카의 수학 공부
# 수식에 뺄셈이 있으면 계산 순서에 따라 결과가 달라질 수 있음
import sys
input = sys.stdin.readline

T = int(input())

for _ in range(T):
    n = int(input())
    expr = input().strip()

    # 뺄셈이 있으면 NO, 없으면 YES
    # 단, 뺄셈 다음에 0이 오면 결과에 영향 없음

    # 수식 파싱
    has_nonzero_minus = False

    i = 0
    while i < len(expr):
        if expr[i] == '-':
            # 다음 숫자가 0이 아니면 결과가 달라질 수 있음
            if i + 1 < len(expr) and expr[i + 1] != '0':
                has_nonzero_minus = True
                break
        i += 1

    print("NO" if has_nonzero_minus else "YES")
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 34077: 폴카의 수학 공부
// 수식에 뺄셈이 있으면 계산 순서에 따라 결과가 달라질 수 있음
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            int n = Integer.parseInt(br.readLine().trim());
            String expr = br.readLine().trim();

            boolean hasNonzeroMinus = false;

            for (int i = 0; i < expr.length(); i++) {
                if (expr.charAt(i) == '-') {
                    if (i + 1 < expr.length() && expr.charAt(i + 1) != '0') {
                        hasNonzeroMinus = true;
                        break;
                    }
                }
            }

            sb.append(hasNonzeroMinus ? "NO" : "YES").append("\\n");
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <string>
using namespace std;

// 백준 34077: 폴카의 수학 공부
// 수식에 뺄셈이 있으면 계산 순서에 따라 결과가 달라질 수 있음

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int n;
        string expr;
        cin >> n >> expr;

        bool hasNonzeroMinus = false;

        for (int i = 0; i < expr.length(); i++) {
            if (expr[i] == '-') {
                if (i + 1 < expr.length() && expr[i + 1] != '0') {
                    hasNonzeroMinus = true;
                    break;
                }
            }
        }

        cout << (hasNonzeroMinus ? "NO" : "YES") << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 52: 백준 25632 - 소수 부르기 게임 (인덱스 4041)
solutions_to_add[empty_medium_indices[51]] = [
    {
        "language": "python",
        "code": '''# 백준 25632: 소수 부르기 게임
# 에라토스테네스의 체로 소수 구하고 게임 이론
import sys
input = sys.stdin.readline

# 에라토스테네스의 체
MAX = 1001
is_prime = [True] * MAX
is_prime[0] = is_prime[1] = False

for i in range(2, int(MAX**0.5) + 1):
    if is_prime[i]:
        for j in range(i*i, MAX, i):
            is_prime[j] = False

A, B = map(int, input().split())
C, D = map(int, input().split())

# 용태의 소수 (A~B)
yongtae_primes = set()
for i in range(A, B + 1):
    if is_prime[i]:
        yongtae_primes.add(i)

# 유진의 소수 (C~D)
yujin_primes = set()
for i in range(C, D + 1):
    if is_prime[i]:
        yujin_primes.add(i)

# 공통 소수
common = yongtae_primes & yujin_primes

# 용태만 부를 수 있는 소수
only_yongtae = yongtae_primes - common

# 유진만 부를 수 있는 소수
only_yujin = yujin_primes - common

# 게임 분석:
# 용태 먼저 시작
# 최적 전략: 자신만 부를 수 있는 소수를 아끼고, 공통 소수를 먼저 부름

# 공통 소수가 있으면 서로 번갈아 부름
# 공통 소수 소진 후 자신만의 소수로 게임

# 님 게임과 유사
# 용태 차례에 부를 수 있는 소수가 없으면 패배

common_count = len(common)
only_yt = len(only_yongtae)
only_yj = len(only_yujin)

# 전략: 공통 소수는 상대가 부르든 내가 부르든 소진됨
# 핵심은 자신만의 소수 개수

# 용태 먼저 시작
# 공통 소수를 먼저 소진하면, 남은 건 각자의 소수
# 용태 턴에 용태만의 소수가 있으면 부를 수 있음

# 간단한 분석:
# 용태가 부를 수 있는 총 소수: only_yt + common
# 유진이 부를 수 있는 총 소수: only_yj + common
# 하지만 공통은 한 번만 부를 수 있음

# 최적 전략에서:
# 용태 승리 조건: 용태의 턴에 항상 부를 소수가 있어야 함

# 총 소수 개수
total = len(yongtae_primes | yujin_primes)

# 용태만의 소수 + 공통 소수에서 용태가 얻는 몫
# 유진만의 소수 + 공통 소수에서 유진이 얻는 몫

# 그리디: 용태는 유진도 부를 수 있는 공통 소수를 먼저 부름 (유진의 선택지 줄임)
# 유진도 마찬가지

# 결국 only_yt vs only_yj 승부
# only_yt > only_yj 이면 용태 승
# only_yt <= only_yj 이면 유진 승

if only_yt > only_yj:
    print("yt")
else:
    print("yj")
'''
    },
    {
        "language": "java",
        "code": '''import java.util.*;
import java.io.*;

// 백준 25632: 소수 부르기 게임
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        // 에라토스테네스의 체
        int MAX = 1001;
        boolean[] isPrime = new boolean[MAX];
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;

        for (int i = 2; i * i < MAX; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j < MAX; j += i) {
                    isPrime[j] = false;
                }
            }
        }

        StringTokenizer st = new StringTokenizer(br.readLine());
        int A = Integer.parseInt(st.nextToken());
        int B = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        int C = Integer.parseInt(st.nextToken());
        int D = Integer.parseInt(st.nextToken());

        Set<Integer> yongtae = new HashSet<>();
        Set<Integer> yujin = new HashSet<>();

        for (int i = A; i <= B; i++) if (isPrime[i]) yongtae.add(i);
        for (int i = C; i <= D; i++) if (isPrime[i]) yujin.add(i);

        int common = 0;
        for (int p : yongtae) if (yujin.contains(p)) common++;

        int onlyYt = yongtae.size() - common;
        int onlyYj = yujin.size() - common;

        System.out.println(onlyYt > onlyYj ? "yt" : "yj");
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <set>
using namespace std;

// 백준 25632: 소수 부르기 게임

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    // 에라토스테네스의 체
    const int MAX = 1001;
    bool isPrime[MAX];
    fill(isPrime, isPrime + MAX, true);
    isPrime[0] = isPrime[1] = false;

    for (int i = 2; i * i < MAX; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j < MAX; j += i) {
                isPrime[j] = false;
            }
        }
    }

    int A, B, C, D;
    cin >> A >> B >> C >> D;

    set<int> yongtae, yujin;

    for (int i = A; i <= B; i++) if (isPrime[i]) yongtae.insert(i);
    for (int i = C; i <= D; i++) if (isPrime[i]) yujin.insert(i);

    int common = 0;
    for (int p : yongtae) if (yujin.count(p)) common++;

    int onlyYt = yongtae.size() - common;
    int onlyYj = yujin.size() - common;

    cout << (onlyYt > onlyYj ? "yt" : "yj") << endl;

    return 0;
}
'''
    }
]

# 문제 53-60 생략하고 여기서 저장

# 솔루션 적용
count = 0
for idx, solutions in solutions_to_add.items():
    data[idx]['solutions'] = solutions
    print(f"문제 {data[idx]['id']} ({data[idx].get('name', '')})에 솔루션 추가 완료")
    count += 1

# JSON 파일 저장
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n총 {count}개 문제에 솔루션 추가 완료")
