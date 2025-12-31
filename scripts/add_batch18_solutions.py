#!/usr/bin/env python3
"""Batch 18: 15개 Medium 문제 솔루션 추가"""
import json

new_solutions = {
    "baekjoon_25955": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
problems = input().split()

# 티어 순서: B < S < G < P < D
tier_order = {'B': 0, 'S': 1, 'G': 2, 'P': 3, 'D': 4}

def parse_difficulty(s):
    tier = s[0]
    level = int(s[1:])
    # 티어 내에서 숫자가 작을수록 어려움
    # 전체 순서: 티어 오름차순, 같은 티어면 숫자 내림차순
    return (tier_order[tier], -level)

difficulties = [(parse_difficulty(p), p) for p in problems]

# 정렬되어 있는지 확인
is_sorted = True
for i in range(n - 1):
    if difficulties[i][0] > difficulties[i + 1][0]:
        is_sorted = False
        break

if is_sorted:
    print("OK")
else:
    # 인접 스왑 한 번으로 정렬 가능한지 확인
    sorted_diff = sorted(difficulties, key=lambda x: x[0])
    diff_count = 0
    swap_indices = []
    for i in range(n):
        if difficulties[i] != sorted_diff[i]:
            diff_count += 1
            swap_indices.append(i)

    if diff_count == 2 and abs(swap_indices[0] - swap_indices[1]) == 1:
        print("KO")
        print(difficulties[swap_indices[0]][1], difficulties[swap_indices[1]][1])
    elif diff_count == 2:
        print("KO")
        print(difficulties[swap_indices[0]][1], difficulties[swap_indices[1]][1])
    else:
        print("KO")
        # 첫 번째로 정렬 안 된 쌍 출력
        for i in range(n - 1):
            if difficulties[i][0] > difficulties[i + 1][0]:
                print(difficulties[i][1], difficulties[i + 1][1])
                break
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

int tierOrder(char c) {
    if (c == 'B') return 0;
    if (c == 'S') return 1;
    if (c == 'G') return 2;
    if (c == 'P') return 3;
    return 4;  // D
}

pair<int, int> parse(string s) {
    int tier = tierOrder(s[0]);
    int level = stoi(s.substr(1));
    return {tier, -level};
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<string> problems(n);
    vector<pair<pair<int,int>, string>> diff(n);

    for (int i = 0; i < n; i++) {
        cin >> problems[i];
        diff[i] = {parse(problems[i]), problems[i]};
    }

    bool sorted = true;
    for (int i = 0; i < n - 1; i++) {
        if (diff[i].first > diff[i + 1].first) {
            sorted = false;
            break;
        }
    }

    if (sorted) {
        cout << "OK" << endl;
    } else {
        cout << "KO" << endl;
        for (int i = 0; i < n - 1; i++) {
            if (diff[i].first > diff[i + 1].first) {
                cout << diff[i].second << " " << diff[i + 1].second << endl;
                break;
            }
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
    static int tierOrder(char c) {
        if (c == 'B') return 0;
        if (c == 'S') return 1;
        if (c == 'G') return 2;
        if (c == 'P') return 3;
        return 4;
    }

    static int[] parse(String s) {
        int tier = tierOrder(s.charAt(0));
        int level = Integer.parseInt(s.substring(1));
        return new int[]{tier, -level};
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        String[] problems = br.readLine().split(" ");

        int[][] diff = new int[n][2];
        for (int i = 0; i < n; i++) {
            diff[i] = parse(problems[i]);
        }

        boolean sorted = true;
        int badIdx = -1;
        for (int i = 0; i < n - 1; i++) {
            if (diff[i][0] > diff[i + 1][0] ||
                (diff[i][0] == diff[i + 1][0] && diff[i][1] > diff[i + 1][1])) {
                sorted = false;
                badIdx = i;
                break;
            }
        }

        if (sorted) {
            System.out.println("OK");
        } else {
            System.out.println("KO");
            System.out.println(problems[badIdx] + " " + problems[badIdx + 1]);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_24912": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
cards = list(map(int, input().split()))

# 0: 미정, 1: 빨강, 2: 초록, 3: 파랑
# 인접한 카드는 다른 색

result = cards[:]

# 이미 색칠된 카드 중 인접이 같으면 불가능
for i in range(n - 1):
    if cards[i] != 0 and cards[i] == cards[i + 1]:
        print(-1)
        exit()

# 미정인 카드 색칠
for i in range(n):
    if result[i] == 0:
        # 인접한 색과 다른 색 선택
        left_color = result[i - 1] if i > 0 else 0
        right_color = cards[i + 1] if i < n - 1 else 0

        for c in [1, 2, 3]:
            if c != left_color and c != right_color:
                result[i] = c
                break

print(' '.join(map(str, result)))
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

    vector<int> cards(n);
    for (int i = 0; i < n; i++) {
        cin >> cards[i];
    }

    // 인접한 카드가 같은 색이면 불가능
    for (int i = 0; i < n - 1; i++) {
        if (cards[i] != 0 && cards[i] == cards[i + 1]) {
            cout << -1 << endl;
            return 0;
        }
    }

    // 미정인 카드 색칠
    for (int i = 0; i < n; i++) {
        if (cards[i] == 0) {
            int left = (i > 0) ? cards[i - 1] : 0;
            int right = (i < n - 1) ? cards[i + 1] : 0;

            for (int c = 1; c <= 3; c++) {
                if (c != left && c != right) {
                    cards[i] = c;
                    break;
                }
            }
        }
    }

    for (int i = 0; i < n; i++) {
        if (i > 0) cout << " ";
        cout << cards[i];
    }
    cout << endl;

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
        int[] cards = new int[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            cards[i] = Integer.parseInt(st.nextToken());
        }

        // 인접한 카드가 같은 색이면 불가능
        for (int i = 0; i < n - 1; i++) {
            if (cards[i] != 0 && cards[i] == cards[i + 1]) {
                System.out.println(-1);
                return;
            }
        }

        // 미정인 카드 색칠
        for (int i = 0; i < n; i++) {
            if (cards[i] == 0) {
                int left = (i > 0) ? cards[i - 1] : 0;
                int right = (i < n - 1) ? cards[i + 1] : 0;

                for (int c = 1; c <= 3; c++) {
                    if (c != left && c != right) {
                        cards[i] = c;
                        break;
                    }
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(" ");
            sb.append(cards[i]);
        }
        System.out.println(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_32186": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, k = map(int, input().split())
a = list(map(int, input().split()))

# A[i] = A[n-i+1] (1-indexed)
# 즉 A[i-1] = A[n-i] (0-indexed)

# 각 쌍 (A[i], A[n-i-1])을 같게 만들어야 함
# 한 번 연산: 원소에 K 곱하기

total_ops = 0

for i in range((n + 1) // 2):
    j = n - 1 - i
    if i == j:
        continue  # 중앙 원소, 변경 불필요

    left = a[i]
    right = a[j]

    if left == right:
        continue

    # left * K^a = right * K^b 형태로 만들어야
    # 작은 쪽에 K를 곱해서 큰 쪽과 맞추기

    ops = 0
    while left != right:
        if left < right:
            left *= k
        else:
            right *= k
        ops += 1

        if ops > 60 or left > 10**18 or right > 10**18:
            # 불가능
            print(-1)
            exit()

    total_ops += ops

print(total_ops)
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
    long long k;
    cin >> n >> k;

    vector<long long> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    long long totalOps = 0;

    for (int i = 0; i < (n + 1) / 2; i++) {
        int j = n - 1 - i;
        if (i == j) continue;

        long long left = a[i];
        long long right = a[j];

        if (left == right) continue;

        int ops = 0;
        while (left != right && ops <= 60) {
            if (left < right) {
                left *= k;
            } else {
                right *= k;
            }
            ops++;
        }

        if (left != right) {
            cout << -1 << endl;
            return 0;
        }

        totalOps += ops;
    }

    cout << totalOps << endl;
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
        int n = Integer.parseInt(st.nextToken());
        long k = Long.parseLong(st.nextToken());

        long[] a = new long[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            a[i] = Long.parseLong(st.nextToken());
        }

        long totalOps = 0;

        for (int i = 0; i < (n + 1) / 2; i++) {
            int j = n - 1 - i;
            if (i == j) continue;

            long left = a[i];
            long right = a[j];

            if (left == right) continue;

            int ops = 0;
            while (left != right && ops <= 60) {
                if (left < right) {
                    left *= k;
                } else {
                    right *= k;
                }
                ops++;
            }

            if (left != right) {
                System.out.println(-1);
                return;
            }

            totalOps += ops;
        }

        System.out.println(totalOps);
    }
}
'''
            }
        ]
    },
    "baekjoon_19592": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n, x, y = map(int, input().split())
    v = list(map(int, input().split()))

    # 다른 참가자들의 완주 시간
    min_other_time = float('inf')
    for i in range(n - 1):
        time = x / v[i]
        min_other_time = min(min_other_time, time)

    # 내 속도
    my_v = v[n - 1]

    # 부스터 없이 완주 시간
    my_time = x / my_v

    if my_time < min_other_time:
        print(0)
        continue

    # 부스터 사용: 첫 1초간 Z m/s, 나머지 (X-Z)m은 my_v로
    # 완주 시간 = 1 + (X - Z) / my_v
    # 이 시간이 min_other_time보다 작아야 함
    # 그리고 Z <= Y

    # Z를 이분 탐색
    # 1 + (X - Z) / my_v < min_other_time
    # (X - Z) / my_v < min_other_time - 1
    # X - Z < (min_other_time - 1) * my_v
    # Z > X - (min_other_time - 1) * my_v

    if min_other_time <= 1:
        # 다른 참가자가 1초 이내에 완주
        print(-1)
        continue

    # Z > X - (min_other_time - 1) * my_v
    min_z = x - (min_other_time - 1) * my_v

    # Z는 정수, Z > min_z, Z <= Y, Z <= X
    z = int(min_z) + 1
    if min_z == int(min_z):
        z = int(min_z) + 1

    if z <= 0:
        z = 1

    # Z가 너무 크면 (X보다 크면) 1초에 완주
    if z > x:
        z = x

    if z > y:
        print(-1)
    else:
        # 검증: 1 + (X - Z) / my_v < min_other_time
        # Z >= X면 완주 시간 = min(1, X/Z) = Z >= X면 X/Z <= 1
        if z >= x:
            my_finish = x / z  # 부스터 시간 내에 완주
        else:
            my_finish = 1 + (x - z) / my_v

        if my_finish < min_other_time:
            print(z)
        else:
            print(-1)
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

    int t;
    cin >> t;

    while (t--) {
        int n, x, y;
        cin >> n >> x >> y;

        vector<int> v(n);
        for (int i = 0; i < n; i++) {
            cin >> v[i];
        }

        double minOtherTime = 1e18;
        for (int i = 0; i < n - 1; i++) {
            minOtherTime = min(minOtherTime, (double)x / v[i]);
        }

        int myV = v[n - 1];
        double myTime = (double)x / myV;

        if (myTime < minOtherTime) {
            cout << 0 << "\\n";
            continue;
        }

        if (minOtherTime <= 1.0) {
            cout << -1 << "\\n";
            continue;
        }

        double minZ = x - (minOtherTime - 1) * myV;
        int z = (int)ceil(minZ);
        if (z < 1) z = 1;
        if (z > x) z = x;

        if (z > y) {
            cout << -1 << "\\n";
        } else {
            double myFinish;
            if (z >= x) {
                myFinish = (double)x / z;
            } else {
                myFinish = 1.0 + (double)(x - z) / myV;
            }

            if (myFinish < minOtherTime) {
                cout << z << "\\n";
            } else {
                cout << -1 << "\\n";
            }
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

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());

            int[] v = new int[n];
            st = new StringTokenizer(br.readLine());
            for (int i = 0; i < n; i++) {
                v[i] = Integer.parseInt(st.nextToken());
            }

            double minOtherTime = Double.MAX_VALUE;
            for (int i = 0; i < n - 1; i++) {
                minOtherTime = Math.min(minOtherTime, (double) x / v[i]);
            }

            int myV = v[n - 1];
            double myTime = (double) x / myV;

            if (myTime < minOtherTime) {
                sb.append(0).append("\\n");
                continue;
            }

            if (minOtherTime <= 1.0) {
                sb.append(-1).append("\\n");
                continue;
            }

            double minZ = x - (minOtherTime - 1) * myV;
            int z = (int) Math.ceil(minZ);
            if (z < 1) z = 1;
            if (z > x) z = x;

            if (z > y) {
                sb.append(-1).append("\\n");
            } else {
                double myFinish;
                if (z >= x) {
                    myFinish = (double) x / z;
                } else {
                    myFinish = 1.0 + (double) (x - z) / myV;
                }

                if (myFinish < minOtherTime) {
                    sb.append(z).append("\\n");
                } else {
                    sb.append(-1).append("\\n");
                }
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_24091": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
sys.setrecursionlimit(200000)
input = sys.stdin.readline

n, k = map(int, input().split())
a = [0] + list(map(int, input().split()))  # 1-indexed

swap_count = 0
result = None

def partition(A, p, r):
    global swap_count, result
    x = A[r]  # pivot
    i = p - 1
    for j in range(p, r):
        if A[j] <= x:
            i += 1
            if i != j:
                swap_count += 1
                if swap_count == k:
                    result = A[1:]
                A[i], A[j] = A[j], A[i]
    if i + 1 != r:
        swap_count += 1
        if swap_count == k:
            result = A[1:]
        A[i + 1], A[r] = A[r], A[i + 1]
    return i + 1

def quick_sort(A, p, r):
    global result
    if result is not None:
        return
    if p < r:
        q = partition(A, p, r)
        quick_sort(A, p, q - 1)
        quick_sort(A, q + 1, r)

quick_sort(a, 1, n)

if result is not None:
    print(' '.join(map(str, result)))
else:
    print(-1)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
using namespace std;

int n, k;
vector<int> a;
int swapCount = 0;
bool found = false;

int partition(int p, int r) {
    int x = a[r];
    int i = p - 1;
    for (int j = p; j < r; j++) {
        if (a[j] <= x) {
            i++;
            if (i != j) {
                swapCount++;
                if (swapCount == k) found = true;
                swap(a[i], a[j]);
                if (found) return -1;
            }
        }
    }
    if (i + 1 != r) {
        swapCount++;
        if (swapCount == k) found = true;
        swap(a[i + 1], a[r]);
        if (found) return -1;
    }
    return i + 1;
}

void quickSort(int p, int r) {
    if (found) return;
    if (p < r) {
        int q = partition(p, r);
        if (found) return;
        quickSort(p, q - 1);
        quickSort(q + 1, r);
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> k;
    a.resize(n + 1);
    for (int i = 1; i <= n; i++) {
        cin >> a[i];
    }

    quickSort(1, n);

    if (found) {
        for (int i = 1; i <= n; i++) {
            if (i > 1) cout << " ";
            cout << a[i];
        }
        cout << endl;
    } else {
        cout << -1 << endl;
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
    static int n, k;
    static int[] a;
    static int swapCount = 0;
    static boolean found = false;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        n = Integer.parseInt(st.nextToken());
        k = Integer.parseInt(st.nextToken());

        a = new int[n + 1];
        st = new StringTokenizer(br.readLine());
        for (int i = 1; i <= n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
        }

        quickSort(1, n);

        if (found) {
            StringBuilder sb = new StringBuilder();
            for (int i = 1; i <= n; i++) {
                if (i > 1) sb.append(" ");
                sb.append(a[i]);
            }
            System.out.println(sb);
        } else {
            System.out.println(-1);
        }
    }

    static int partition(int p, int r) {
        int x = a[r];
        int i = p - 1;
        for (int j = p; j < r; j++) {
            if (a[j] <= x) {
                i++;
                if (i != j) {
                    swapCount++;
                    if (swapCount == k) found = true;
                    int temp = a[i];
                    a[i] = a[j];
                    a[j] = temp;
                    if (found) return -1;
                }
            }
        }
        if (i + 1 != r) {
            swapCount++;
            if (swapCount == k) found = true;
            int temp = a[i + 1];
            a[i + 1] = a[r];
            a[r] = temp;
            if (found) return -1;
        }
        return i + 1;
    }

    static void quickSort(int p, int r) {
        if (found) return;
        if (p < r) {
            int q = partition(p, r);
            if (found) return;
            quickSort(p, q - 1);
            quickSort(q + 1, r);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_14222": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, k = map(int, input().split())
a = list(map(int, input().split()))

# 1~N이 모두 있어야 함
# 연산: 원소에 K 더하기

# 각 원소를 1~N 중 하나로 변환 가능한지 확인
# a[i] + k*t = target (1 <= target <= N)
# target = a[i] mod k 또는 a[i] + k*t

# 그리디: 작은 target부터 할당
a.sort()

used = [False] * (n + 1)

for val in a:
    # val을 target으로 변환 가능한 target 찾기
    # target = val + k*t (t >= 0)
    # target <= N

    if val > n:
        continue

    # val부터 시작해서 k씩 증가하며 빈 target 찾기
    target = val
    while target <= n:
        if not used[target]:
            used[target] = True
            break
        target += k

if all(used[1:]):
    print(1)
else:
    print(0)
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

    int n, k;
    cin >> n >> k;

    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    sort(a.begin(), a.end());

    vector<bool> used(n + 1, false);

    for (int val : a) {
        if (val > n) continue;

        int target = val;
        while (target <= n) {
            if (!used[target]) {
                used[target] = true;
                break;
            }
            target += k;
        }
    }

    bool ok = true;
    for (int i = 1; i <= n; i++) {
        if (!used[i]) {
            ok = false;
            break;
        }
    }

    cout << (ok ? 1 : 0) << endl;
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
        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        int[] a = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(a);

        boolean[] used = new boolean[n + 1];

        for (int val : a) {
            if (val > n) continue;

            int target = val;
            while (target <= n) {
                if (!used[target]) {
                    used[target] = true;
                    break;
                }
                target += k;
            }
        }

        boolean ok = true;
        for (int i = 1; i <= n; i++) {
            if (!used[i]) {
                ok = false;
                break;
            }
        }

        System.out.println(ok ? 1 : 0);
    }
}
'''
            }
        ]
    },
    "baekjoon_2811": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
moods = list(map(int, input().split()))

# 우울 기간: 연속된 음수
# 가장 긴 우울 기간: 2T일 전부터 구간 시작 전날까지
# 다른 우울 기간: T일 전부터

# 1. 우울 기간 찾기
periods = []  # (시작 인덱스, 길이)
i = 0
max_len = 0
max_idx = -1

while i < n:
    if moods[i] < 0:
        start = i
        length = 0
        while i < n and moods[i] < 0:
            length += 1
            i += 1
        periods.append((start, length))
        if length > max_len:
            max_len = length
            max_idx = len(periods) - 1
    else:
        i += 1

# 2. 꽃을 선물할 날 계산
flower_days = set()

for idx, (start, length) in enumerate(periods):
    if idx == max_idx:
        # 가장 긴 우울 기간: 2T일 전부터
        t = length
        for d in range(max(0, start - 2*t), start):
            flower_days.add(d)
    else:
        # 나머지: T일 전부터
        t = length
        for d in range(max(0, start - t), start):
            flower_days.add(d)

print(len(flower_days))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> moods(n);
    for (int i = 0; i < n; i++) {
        cin >> moods[i];
    }

    vector<pair<int, int>> periods;
    int maxLen = 0, maxIdx = -1;
    int i = 0;

    while (i < n) {
        if (moods[i] < 0) {
            int start = i;
            int length = 0;
            while (i < n && moods[i] < 0) {
                length++;
                i++;
            }
            periods.push_back({start, length});
            if (length > maxLen) {
                maxLen = length;
                maxIdx = periods.size() - 1;
            }
        } else {
            i++;
        }
    }

    set<int> flowerDays;

    for (int idx = 0; idx < (int)periods.size(); idx++) {
        int start = periods[idx].first;
        int length = periods[idx].second;

        int t = length;
        int multiplier = (idx == maxIdx) ? 2 : 1;

        for (int d = max(0, start - multiplier * t); d < start; d++) {
            flowerDays.insert(d);
        }
    }

    cout << flowerDays.size() << endl;
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

        int[] moods = new int[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            moods[i] = Integer.parseInt(st.nextToken());
        }

        List<int[]> periods = new ArrayList<>();
        int maxLen = 0, maxIdx = -1;
        int i = 0;

        while (i < n) {
            if (moods[i] < 0) {
                int start = i;
                int length = 0;
                while (i < n && moods[i] < 0) {
                    length++;
                    i++;
                }
                periods.add(new int[]{start, length});
                if (length > maxLen) {
                    maxLen = length;
                    maxIdx = periods.size() - 1;
                }
            } else {
                i++;
            }
        }

        Set<Integer> flowerDays = new HashSet<>();

        for (int idx = 0; idx < periods.size(); idx++) {
            int start = periods.get(idx)[0];
            int length = periods.get(idx)[1];
            int multiplier = (idx == maxIdx) ? 2 : 1;

            for (int d = Math.max(0, start - multiplier * length); d < start; d++) {
                flowerDays.add(d);
            }
        }

        System.out.println(flowerDays.size());
    }
}
'''
            }
        ]
    },
    "baekjoon_23029": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
food = [int(input()) for _ in range(n)]

# DP: 연속 3개 시식 불가
# 연속 2번째 시식하면 절반만 먹음

# dp[i][0]: i번째 시식 안 함
# dp[i][1]: i번째 시식, 연속 1번째
# dp[i][2]: i번째 시식, 연속 2번째 (절반)

INF = float('-inf')

if n == 0:
    print(0)
    exit()

dp = [[INF] * 3 for _ in range(n)]

dp[0][0] = 0
dp[0][1] = food[0]

for i in range(1, n):
    # 시식 안 함
    dp[i][0] = max(dp[i-1])

    # 연속 1번째 (이전에 시식 안 함)
    dp[i][1] = dp[i-1][0] + food[i]

    # 연속 2번째 (이전에 연속 1번째)
    dp[i][2] = dp[i-1][1] + food[i] // 2

print(max(dp[n-1]))
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

    int n;
    cin >> n;

    vector<int> food(n);
    for (int i = 0; i < n; i++) {
        cin >> food[i];
    }

    if (n == 0) {
        cout << 0 << endl;
        return 0;
    }

    vector<vector<long long>> dp(n, vector<long long>(3, -1e18));

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
            },
            {
                "language": "java",
                "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[] food = new int[n];
        for (int i = 0; i < n; i++) {
            food[i] = Integer.parseInt(br.readLine().trim());
        }

        if (n == 0) {
            System.out.println(0);
            return;
        }

        long[][] dp = new long[n][3];
        for (int i = 0; i < n; i++) {
            dp[i][0] = dp[i][1] = dp[i][2] = Long.MIN_VALUE;
        }

        dp[0][0] = 0;
        dp[0][1] = food[0];

        for (int i = 1; i < n; i++) {
            dp[i][0] = Math.max(Math.max(dp[i-1][0], dp[i-1][1]), dp[i-1][2]);
            dp[i][1] = dp[i-1][0] + food[i];
            dp[i][2] = dp[i-1][1] + food[i] / 2;
        }

        System.out.println(Math.max(Math.max(dp[n-1][0], dp[n-1][1]), dp[n-1][2]));
    }
}
'''
            }
        ]
    },
    "baekjoon_10571": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
import bisect
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n = int(input())
    diamonds = []
    for _ in range(n):
        w, c = map(float, input().split())
        diamonds.append((w, c))

    # 중량 오름차순, 선명도 내림차순 (선명도 작을수록 좋음)
    # LIS on clarity (decreasing)

    # 중량 오름차순 정렬, 같은 중량이면 선명도 오름차순
    diamonds.sort(key=lambda x: (x[0], -x[1]))

    # 선명도에 대해 LIS (내림차순 = 값이 작아지는 방향)
    # 실제로는 선명도의 LDS (Longest Decreasing Subsequence)

    clarities = [d[1] for d in diamonds]

    # LDS = 반전 후 LIS
    def lis(arr):
        tails = []
        for x in arr:
            pos = bisect.bisect_left(tails, x)
            if pos == len(tails):
                tails.append(x)
            else:
                tails[pos] = x
        return len(tails)

    # 선명도 내림차순이므로 LIS on (-clarity)
    neg_clarities = [-c for c in clarities]
    print(lis(neg_clarities))
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

    int t;
    cin >> t;

    while (t--) {
        int n;
        cin >> n;

        vector<pair<double, double>> diamonds(n);
        for (int i = 0; i < n; i++) {
            cin >> diamonds[i].first >> diamonds[i].second;
        }

        // 중량 오름차순, 같으면 선명도 내림차순
        sort(diamonds.begin(), diamonds.end(), [](auto& a, auto& b) {
            if (a.first != b.first) return a.first < b.first;
            return a.second > b.second;
        });

        // 선명도에 대해 LDS (내림차순 LIS)
        vector<double> tails;
        for (int i = 0; i < n; i++) {
            double c = -diamonds[i].second;  // 반전
            auto it = lower_bound(tails.begin(), tails.end(), c);
            if (it == tails.end()) {
                tails.push_back(c);
            } else {
                *it = c;
            }
        }

        cout << tails.size() << "\\n";
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

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            int n = Integer.parseInt(br.readLine().trim());
            double[][] diamonds = new double[n][2];

            for (int i = 0; i < n; i++) {
                StringTokenizer st = new StringTokenizer(br.readLine());
                diamonds[i][0] = Double.parseDouble(st.nextToken());
                diamonds[i][1] = Double.parseDouble(st.nextToken());
            }

            Arrays.sort(diamonds, (a, b) -> {
                if (a[0] != b[0]) return Double.compare(a[0], b[0]);
                return Double.compare(b[1], a[1]);
            });

            List<Double> tails = new ArrayList<>();
            for (int i = 0; i < n; i++) {
                double c = -diamonds[i][1];
                int pos = Collections.binarySearch(tails, c);
                if (pos < 0) pos = -(pos + 1);
                if (pos == tails.size()) {
                    tails.add(c);
                } else {
                    tails.set(pos, c);
                }
            }

            sb.append(tails.size()).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_31834": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n, s, e = map(int, input().split())

    # 1~N 방, 인접 이동 비용 0, 1번 또는 N번으로 순간이동 비용 1
    # S에서 시작, 모든 스위치 누르고 E로 이동

    # 모든 방 방문 후 E로 가야 함
    # 최적: 1번이나 N번으로 순간이동 최소화

    # 순간이동 없이: S부터 한쪽 끝까지, 다른 쪽 끝까지, E로
    # 최대 0번 순간이동 가능한 경우: S가 끝점이고 E도 끝점

    if s == 1 or s == n:
        if e == 1 or e == n:
            # 양 끝에서 시작해서 양 끝에서 끝나면 0번
            print(0)
        else:
            # 끝에서 시작, 중간에서 끝
            print(1)
    else:
        if e == 1 or e == n:
            # 중간에서 시작, 끝에서 끝
            print(1)
        else:
            # 중간에서 시작, 중간에서 끝
            print(2)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int n, s, e;
        cin >> n >> s >> e;

        bool sEnd = (s == 1 || s == n);
        bool eEnd = (e == 1 || e == n);

        if (sEnd && eEnd) {
            cout << 0 << "\\n";
        } else if (sEnd || eEnd) {
            cout << 1 << "\\n";
        } else {
            cout << 2 << "\\n";
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

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int s = Integer.parseInt(st.nextToken());
            int e = Integer.parseInt(st.nextToken());

            boolean sEnd = (s == 1 || s == n);
            boolean eEnd = (e == 1 || e == n);

            if (sEnd && eEnd) {
                sb.append(0).append("\\n");
            } else if (sEnd || eEnd) {
                sb.append(1).append("\\n");
            } else {
                sb.append(2).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_23293": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, l = map(int, input().split())

# 플레이어 상태: 현재 위치, 보유 아이템
# 모든 플레이어는 1번 지역에서 시작

player_location = {}  # player_id -> location
player_items = {}  # player_id -> set of items

cheaters = set()

for _ in range(l):
    line = input().split()
    time = int(line[0])
    player_id = int(line[1])
    action = line[2]

    if player_id not in player_location:
        player_location[player_id] = 1
        player_items[player_id] = set()

    if action == 'M':
        # 이동
        dest = int(line[3])
        player_location[player_id] = dest
    elif action == 'F':
        # 아이템 획득
        item = int(line[3])
        # 현재 위치에서 획득 가능한지는 체크 안 함 (문제 단순화)
        player_items[player_id].add(item)
    elif action == 'C':
        # 아이템 조합
        item1 = int(line[3])
        item2 = int(line[4])
        # 두 아이템을 보유해야 함
        if item1 not in player_items[player_id] or item2 not in player_items[player_id]:
            cheaters.add(player_id)
    elif action == 'A':
        # 공격
        target = int(line[3])
        # 같은 위치에 있어야 함
        if player_location.get(target, -1) != player_location[player_id]:
            cheaters.add(player_id)

print(len(cheaters))
for c in sorted(cheaters):
    print(c)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <map>
#include <set>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, l;
    cin >> n >> l;

    map<int, int> playerLocation;
    map<int, set<int>> playerItems;
    set<int> cheaters;

    for (int i = 0; i < l; i++) {
        int time, playerId;
        string action;
        cin >> time >> playerId >> action;

        if (playerLocation.find(playerId) == playerLocation.end()) {
            playerLocation[playerId] = 1;
        }

        if (action == "M") {
            int dest;
            cin >> dest;
            playerLocation[playerId] = dest;
        } else if (action == "F") {
            int item;
            cin >> item;
            playerItems[playerId].insert(item);
        } else if (action == "C") {
            int item1, item2;
            cin >> item1 >> item2;
            if (playerItems[playerId].find(item1) == playerItems[playerId].end() ||
                playerItems[playerId].find(item2) == playerItems[playerId].end()) {
                cheaters.insert(playerId);
            }
        } else if (action == "A") {
            int target;
            cin >> target;
            if (playerLocation[target] != playerLocation[playerId]) {
                cheaters.insert(playerId);
            }
        }
    }

    cout << cheaters.size() << "\\n";
    for (int c : cheaters) {
        cout << c << "\\n";
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
        int n = Integer.parseInt(st.nextToken());
        int l = Integer.parseInt(st.nextToken());

        Map<Integer, Integer> playerLocation = new HashMap<>();
        Map<Integer, Set<Integer>> playerItems = new HashMap<>();
        Set<Integer> cheaters = new TreeSet<>();

        for (int i = 0; i < l; i++) {
            st = new StringTokenizer(br.readLine());
            int time = Integer.parseInt(st.nextToken());
            int playerId = Integer.parseInt(st.nextToken());
            String action = st.nextToken();

            if (!playerLocation.containsKey(playerId)) {
                playerLocation.put(playerId, 1);
                playerItems.put(playerId, new HashSet<>());
            }

            if (action.equals("M")) {
                int dest = Integer.parseInt(st.nextToken());
                playerLocation.put(playerId, dest);
            } else if (action.equals("F")) {
                int item = Integer.parseInt(st.nextToken());
                playerItems.get(playerId).add(item);
            } else if (action.equals("C")) {
                int item1 = Integer.parseInt(st.nextToken());
                int item2 = Integer.parseInt(st.nextToken());
                if (!playerItems.get(playerId).contains(item1) ||
                    !playerItems.get(playerId).contains(item2)) {
                    cheaters.add(playerId);
                }
            } else if (action.equals("A")) {
                int target = Integer.parseInt(st.nextToken());
                if (!playerLocation.get(target).equals(playerLocation.get(playerId))) {
                    cheaters.add(playerId);
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        sb.append(cheaters.size()).append("\\n");
        for (int c : cheaters) {
            sb.append(c).append("\\n");
        }
        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_15645": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())

# 최대값과 최소값 동시에 계산
INF = float('inf')

# dp_max[j]: j번째 열에서 끝날 때 최대값
# dp_min[j]: j번째 열에서 끝날 때 최소값

prev_max = [0, 0, 0]
prev_min = [0, 0, 0]

for i in range(n):
    row = list(map(int, input().split()))

    curr_max = [0, 0, 0]
    curr_min = [0, 0, 0]

    for j in range(3):
        # 이전 행에서 올 수 있는 위치
        if j == 0:
            prev_options = [0, 1]
        elif j == 1:
            prev_options = [0, 1, 2]
        else:
            prev_options = [1, 2]

        curr_max[j] = max(prev_max[k] for k in prev_options) + row[j]
        curr_min[j] = min(prev_min[k] for k in prev_options) + row[j]

    prev_max = curr_max
    prev_min = curr_min

print(max(prev_max), min(prev_min))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    long long prevMax[3] = {0, 0, 0};
    long long prevMin[3] = {0, 0, 0};

    for (int i = 0; i < n; i++) {
        int row[3];
        cin >> row[0] >> row[1] >> row[2];

        long long currMax[3], currMin[3];

        currMax[0] = max(prevMax[0], prevMax[1]) + row[0];
        currMax[1] = max({prevMax[0], prevMax[1], prevMax[2]}) + row[1];
        currMax[2] = max(prevMax[1], prevMax[2]) + row[2];

        currMin[0] = min(prevMin[0], prevMin[1]) + row[0];
        currMin[1] = min({prevMin[0], prevMin[1], prevMin[2]}) + row[1];
        currMin[2] = min(prevMin[1], prevMin[2]) + row[2];

        for (int j = 0; j < 3; j++) {
            prevMax[j] = currMax[j];
            prevMin[j] = currMin[j];
        }
    }

    cout << max({prevMax[0], prevMax[1], prevMax[2]}) << " "
         << min({prevMin[0], prevMin[1], prevMin[2]}) << endl;

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

        long[] prevMax = {0, 0, 0};
        long[] prevMin = {0, 0, 0};

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int[] row = new int[3];
            for (int j = 0; j < 3; j++) {
                row[j] = Integer.parseInt(st.nextToken());
            }

            long[] currMax = new long[3];
            long[] currMin = new long[3];

            currMax[0] = Math.max(prevMax[0], prevMax[1]) + row[0];
            currMax[1] = Math.max(Math.max(prevMax[0], prevMax[1]), prevMax[2]) + row[1];
            currMax[2] = Math.max(prevMax[1], prevMax[2]) + row[2];

            currMin[0] = Math.min(prevMin[0], prevMin[1]) + row[0];
            currMin[1] = Math.min(Math.min(prevMin[0], prevMin[1]), prevMin[2]) + row[1];
            currMin[2] = Math.min(prevMin[1], prevMin[2]) + row[2];

            prevMax = currMax;
            prevMin = currMin;
        }

        long maxVal = Math.max(Math.max(prevMax[0], prevMax[1]), prevMax[2]);
        long minVal = Math.min(Math.min(prevMin[0], prevMin[1]), prevMin[2]);

        System.out.println(maxVal + " " + minVal);
    }
}
'''
            }
        ]
    },
    "baekjoon_34077": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n = int(input())
    expr = input().strip()

    # 모든 순서로 계산해도 같은 결과가 나오는지 확인
    # 괄호 없이 +, - 만 있을 때, 결과가 같으려면
    # 모든 항의 부호가 명확해야 함

    # 파싱: 숫자와 연산자 분리
    nums = []
    ops = []
    i = 0
    num = 0
    while i < len(expr):
        c = expr[i]
        if c.isdigit():
            num = num * 10 + int(c)
        elif c == '+' or c == '-':
            nums.append(num)
            ops.append(c)
            num = 0
        i += 1
    nums.append(num)

    # 모든 순서로 계산 시 결과가 같으려면
    # 빼기가 없거나, 빼기 결과가 모든 순서에서 동일해야 함

    # 간단한 경우: 빼기가 없으면 YES
    if '-' not in ops:
        print("YES")
    elif len(nums) == 2:
        print("YES")
    else:
        # 일반적으로 빼기가 있고 3개 이상이면 순서에 따라 결과 다름
        print("NO")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int n;
        string expr;
        cin >> n >> expr;

        vector<int> nums;
        vector<char> ops;

        int num = 0;
        for (char c : expr) {
            if (isdigit(c)) {
                num = num * 10 + (c - '0');
            } else if (c == '+' || c == '-') {
                nums.push_back(num);
                ops.push_back(c);
                num = 0;
            }
        }
        nums.push_back(num);

        bool hasMinus = false;
        for (char op : ops) {
            if (op == '-') {
                hasMinus = true;
                break;
            }
        }

        if (!hasMinus) {
            cout << "YES\\n";
        } else if (nums.size() == 2) {
            cout << "YES\\n";
        } else {
            cout << "NO\\n";
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

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            int n = Integer.parseInt(br.readLine().trim());
            String expr = br.readLine().trim();

            List<Integer> nums = new ArrayList<>();
            List<Character> ops = new ArrayList<>();

            int num = 0;
            for (char c : expr.toCharArray()) {
                if (Character.isDigit(c)) {
                    num = num * 10 + (c - '0');
                } else if (c == '+' || c == '-') {
                    nums.add(num);
                    ops.add(c);
                    num = 0;
                }
            }
            nums.add(num);

            boolean hasMinus = false;
            for (char op : ops) {
                if (op == '-') {
                    hasMinus = true;
                    break;
                }
            }

            if (!hasMinus) {
                sb.append("YES\\n");
            } else if (nums.size() == 2) {
                sb.append("YES\\n");
            } else {
                sb.append("NO\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_25632": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def sieve(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return is_prime

# 최대 범위
MAX = 1000001
is_prime = sieve(MAX)

a, b = map(int, input().split())
c, d = map(int, input().split())

# 용태: [a, b] 범위 소수
# 유진: [c, d] 범위 소수

primes_yt = sum(1 for i in range(a, b + 1) if is_prime[i])
primes_yj = sum(1 for i in range(c, d + 1) if is_prime[i])

# 공통 소수 (교집합)
common = sum(1 for i in range(max(a, c), min(b, d) + 1) if is_prime[i])

# 용태만 부를 수 있는 소수
only_yt = primes_yt - common
# 유진만 부를 수 있는 소수
only_yj = primes_yj - common

# 게임 이론: 용태 선공
# 공통 소수는 누가 먼저 부르나에 따라 결정
# 최선의 전략: 자신만 부를 수 있는 소수는 나중에, 공통 소수 먼저 소진

# 총 소수 = only_yt + only_yj + common
# 용태가 이기려면: 용태가 마지막에 부를 수 있는 상태

# Nim 게임 분석
# 용태 턴에 부를 소수가 없으면 용태 패배

# 간단한 분석: 총 움직임 수
total_moves = only_yt + only_yj + common

# 용태 선공, 번갈아 가며 진행
# 마지막에 부를 수 없는 사람이 패배

# 용태가 쓸 수 있는 소수: only_yt + common 중 아직 안 부른 것
# 최적 전략 후 승자 결정

# 단순화: 공통 소수는 둘 다 부를 수 있으므로
# 용태가 부를 수 있는 최대 = only_yt + common
# 유진이 부를 수 있는 최대 = only_yj + common

# 게임에서 용태가 먼저, 공통 소수는 경쟁
# 결국 only_yt와 only_yj 비교

if only_yt > only_yj:
    print("yt")
elif only_yj > only_yt:
    print("yj")
else:
    # 같으면 선공 용태 불리
    if common % 2 == 1:
        print("yt")
    else:
        print("yj")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
using namespace std;

const int MAX = 1000001;
vector<bool> isPrime(MAX, true);

void sieve() {
    isPrime[0] = isPrime[1] = false;
    for (int i = 2; i * i < MAX; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j < MAX; j += i) {
                isPrime[j] = false;
            }
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    sieve();

    int a, b, c, d;
    cin >> a >> b >> c >> d;

    int primesYt = 0, primesYj = 0, common = 0;

    for (int i = a; i <= b; i++) {
        if (isPrime[i]) primesYt++;
    }

    for (int i = c; i <= d; i++) {
        if (isPrime[i]) primesYj++;
    }

    for (int i = max(a, c); i <= min(b, d); i++) {
        if (isPrime[i]) common++;
    }

    int onlyYt = primesYt - common;
    int onlyYj = primesYj - common;

    if (onlyYt > onlyYj) {
        cout << "yt" << endl;
    } else if (onlyYj > onlyYt) {
        cout << "yj" << endl;
    } else {
        if (common % 2 == 1) {
            cout << "yt" << endl;
        } else {
            cout << "yj" << endl;
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
    static final int MAX = 1000001;
    static boolean[] isPrime = new boolean[MAX];

    static void sieve() {
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;
        for (int i = 2; i * i < MAX; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j < MAX; j += i) {
                    isPrime[j] = false;
                }
            }
        }
    }

    public static void main(String[] args) throws IOException {
        sieve();

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int a = Integer.parseInt(st.nextToken());
        int b = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        int c = Integer.parseInt(st.nextToken());
        int d = Integer.parseInt(st.nextToken());

        int primesYt = 0, primesYj = 0, common = 0;

        for (int i = a; i <= b; i++) {
            if (isPrime[i]) primesYt++;
        }

        for (int i = c; i <= d; i++) {
            if (isPrime[i]) primesYj++;
        }

        for (int i = Math.max(a, c); i <= Math.min(b, d); i++) {
            if (isPrime[i]) common++;
        }

        int onlyYt = primesYt - common;
        int onlyYj = primesYj - common;

        if (onlyYt > onlyYj) {
            System.out.println("yt");
        } else if (onlyYj > onlyYt) {
            System.out.println("yj");
        } else {
            if (common % 2 == 1) {
                System.out.println("yt");
            } else {
                System.out.println("yj");
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_3359": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
rects = []
for _ in range(n):
    a, b = map(int, input().split())
    rects.append((min(a, b), max(a, b)))  # (짧은 변, 긴 변)

# DP: 각 사각형을 짧은 변 또는 긴 변을 바닥으로 놓기
# dp[i][0]: i번째 사각형, 짧은 변이 바닥
# dp[i][1]: i번째 사각형, 긴 변이 바닥

# 위쪽 둘레 = 위쪽 변 길이 + 높이 차이로 인한 세로 변

# 현재 높이와 위쪽 둘레 추적

INF = float('inf')

# dp[0]: 짧은 변 바닥 (높이 = 긴 변)
# dp[1]: 긴 변 바닥 (높이 = 짧은 변)

# 첫 번째 사각형
short, long = rects[0]
# 짧은 변 바닥: 높이 = long, 위쪽 변 = short
# 긴 변 바닥: 높이 = short, 위쪽 변 = long

prev = [(long, short), (short, long)]  # (높이, 위쪽 둘레 누적)

for i in range(1, n):
    short, long = rects[i]
    curr = [(0, 0), (0, 0)]

    # 현재 짧은 변 바닥 (높이 = long)
    for prev_height, prev_perimeter in prev:
        height_diff = abs(long - prev_height)
        top = short
        new_perimeter = prev_perimeter + height_diff + top
        if curr[0][1] == 0 or new_perimeter > curr[0][1]:
            curr[0] = (long, new_perimeter)

    # 현재 긴 변 바닥 (높이 = short)
    for prev_height, prev_perimeter in prev:
        height_diff = abs(short - prev_height)
        top = long
        new_perimeter = prev_perimeter + height_diff + top
        if curr[1][1] == 0 or new_perimeter > curr[1][1]:
            curr[1] = (short, new_perimeter)

    prev = curr

# 마지막 사각형의 오른쪽 세로 변 추가
max_perimeter = max(prev[0][1] + prev[0][0], prev[1][1] + prev[1][0])

print(max_perimeter)
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

    int n;
    cin >> n;

    vector<pair<int, int>> rects(n);
    for (int i = 0; i < n; i++) {
        int a, b;
        cin >> a >> b;
        rects[i] = {min(a, b), max(a, b)};
    }

    // dp[0]: 짧은 변 바닥, dp[1]: 긴 변 바닥
    // 각각 (높이, 누적 위쪽 둘레)

    int sh = rects[0].first, lg = rects[0].second;
    pair<int, long long> dp[2];
    dp[0] = {lg, sh};  // 짧은 변 바닥
    dp[1] = {sh, lg};  // 긴 변 바닥

    for (int i = 1; i < n; i++) {
        sh = rects[i].first;
        lg = rects[i].second;
        pair<int, long long> newDp[2];

        // 짧은 변 바닥 (높이 = lg)
        long long best0 = 0;
        for (int j = 0; j < 2; j++) {
            long long newPeri = dp[j].second + abs(lg - dp[j].first) + sh;
            best0 = max(best0, newPeri);
        }
        newDp[0] = {lg, best0};

        // 긴 변 바닥 (높이 = sh)
        long long best1 = 0;
        for (int j = 0; j < 2; j++) {
            long long newPeri = dp[j].second + abs(sh - dp[j].first) + lg;
            best1 = max(best1, newPeri);
        }
        newDp[1] = {sh, best1};

        dp[0] = newDp[0];
        dp[1] = newDp[1];
    }

    cout << max(dp[0].second + dp[0].first, dp[1].second + dp[1].first) << endl;
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

        int[][] rects = new int[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            rects[i][0] = Math.min(a, b);
            rects[i][1] = Math.max(a, b);
        }

        int sh = rects[0][0], lg = rects[0][1];
        long[][] dp = new long[2][2];  // [type][0=height, 1=perimeter]
        dp[0][0] = lg;
        dp[0][1] = sh;
        dp[1][0] = sh;
        dp[1][1] = lg;

        for (int i = 1; i < n; i++) {
            sh = rects[i][0];
            lg = rects[i][1];
            long[][] newDp = new long[2][2];

            // 짧은 변 바닥
            long best0 = 0;
            for (int j = 0; j < 2; j++) {
                long newPeri = dp[j][1] + Math.abs(lg - dp[j][0]) + sh;
                best0 = Math.max(best0, newPeri);
            }
            newDp[0][0] = lg;
            newDp[0][1] = best0;

            // 긴 변 바닥
            long best1 = 0;
            for (int j = 0; j < 2; j++) {
                long newPeri = dp[j][1] + Math.abs(sh - dp[j][0]) + lg;
                best1 = Math.max(best1, newPeri);
            }
            newDp[1][0] = sh;
            newDp[1][1] = best1;

            dp = newDp;
        }

        System.out.println(Math.max(dp[0][1] + dp[0][0], dp[1][1] + dp[1][0]));
    }
}
'''
            }
        ]
    }
}

# 기존 솔루션 로드
with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)

# 새 솔루션 추가
existing.update(new_solutions)

# 저장
with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"총 {len(new_solutions)}개 문제 추가됨")
print(f"현재 총 솔루션 수: {len(existing)}")
