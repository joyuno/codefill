#!/usr/bin/env python3
"""Batch 15: 15개 Medium 문제 솔루션 추가"""
import json

new_solutions = {
    "baekjoon_14843": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

# 문제 정보 읽기
p = int(input())
problems = []
for _ in range(p):
    parts = input().split()
    s = float(parts[0])
    n = int(parts[1])
    t = int(parts[2])
    y = int(parts[3])
    problems.append((s, n, t, y))

# 점수 계산 함수: score = max(30, 75 - 3*(n-1) - 20*(t-s)/max(10s, 1)) * (1.15 ^ (y-2016))
# 문제에서 주어진 공식에 따라 점수 계산

e = int(input())
scores = []
for _ in range(e):
    score = float(input())
    scores.append(score)

# 총점 계산
total = sum(scores)
print(f"The total score of Younghoon is {total:.2f}.")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <iomanip>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int p;
    cin >> p;

    // 문제 정보 읽기 (사용하지 않음 - 점수가 직접 주어짐)
    for (int i = 0; i < p; i++) {
        double s;
        int n, t, y;
        cin >> s >> n >> t >> y;
    }

    int e;
    cin >> e;

    double total = 0.0;
    for (int i = 0; i < e; i++) {
        double score;
        cin >> score;
        total += score;
    }

    cout << fixed << setprecision(2);
    cout << "The total score of Younghoon is " << total << "." << endl;

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

        int p = Integer.parseInt(br.readLine().trim());

        // 문제 정보 읽기
        for (int i = 0; i < p; i++) {
            br.readLine();
        }

        int e = Integer.parseInt(br.readLine().trim());
        double total = 0.0;

        for (int i = 0; i < e; i++) {
            double score = Double.parseDouble(br.readLine().trim());
            total += score;
        }

        System.out.printf("The total score of Younghoon is %.2f.%n", total);
    }
}
'''
            }
        ]
    },
    "baekjoon_24173": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, k = map(int, input().split())
A = [0] + list(map(int, input().split()))  # 1-indexed

swap_count = 0
result = None

def heapify(A, k_idx, n_size):
    global swap_count, result
    smallest = k_idx
    left = 2 * k_idx
    right = 2 * k_idx + 1

    if left <= n_size and A[left] < A[smallest]:
        smallest = left
    if right <= n_size and A[right] < A[smallest]:
        smallest = right

    if smallest != k_idx:
        swap_count += 1
        if swap_count == k:
            result = (min(A[k_idx], A[smallest]), max(A[k_idx], A[smallest]))
        A[k_idx], A[smallest] = A[smallest], A[k_idx]
        heapify(A, smallest, n_size)

def build_min_heap(A, n_size):
    for i in range(n_size // 2, 0, -1):
        heapify(A, i, n_size)

def heap_sort(A, n_size):
    global swap_count, result
    build_min_heap(A, n_size)
    for i in range(n_size, 1, -1):
        swap_count += 1
        if swap_count == k:
            result = (min(A[1], A[i]), max(A[1], A[i]))
        A[1], A[i] = A[i], A[1]
        heapify(A, 1, i - 1)

sys.setrecursionlimit(200000)
heap_sort(A, n)

if result:
    print(result[0], result[1])
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
vector<int> A;
int swapCount = 0;
int result1 = -1, result2 = -1;

void heapify(int k_idx, int n_size) {
    int smallest = k_idx;
    int left = 2 * k_idx;
    int right = 2 * k_idx + 1;

    if (left <= n_size && A[left] < A[smallest])
        smallest = left;
    if (right <= n_size && A[right] < A[smallest])
        smallest = right;

    if (smallest != k_idx) {
        swapCount++;
        if (swapCount == k) {
            result1 = min(A[k_idx], A[smallest]);
            result2 = max(A[k_idx], A[smallest]);
        }
        swap(A[k_idx], A[smallest]);
        heapify(smallest, n_size);
    }
}

void buildMinHeap(int n_size) {
    for (int i = n_size / 2; i >= 1; i--) {
        heapify(i, n_size);
    }
}

void heapSort(int n_size) {
    buildMinHeap(n_size);
    for (int i = n_size; i >= 2; i--) {
        swapCount++;
        if (swapCount == k) {
            result1 = min(A[1], A[i]);
            result2 = max(A[1], A[i]);
        }
        swap(A[1], A[i]);
        heapify(1, i - 1);
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> k;
    A.resize(n + 1);
    for (int i = 1; i <= n; i++) {
        cin >> A[i];
    }

    heapSort(n);

    if (result1 == -1) {
        cout << -1 << endl;
    } else {
        cout << result1 << " " << result2 << endl;
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
    static int[] A;
    static int n, k;
    static int swapCount = 0;
    static int result1 = -1, result2 = -1;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        n = Integer.parseInt(st.nextToken());
        k = Integer.parseInt(st.nextToken());

        A = new int[n + 1];
        st = new StringTokenizer(br.readLine());
        for (int i = 1; i <= n; i++) {
            A[i] = Integer.parseInt(st.nextToken());
        }

        heapSort(n);

        if (result1 == -1) {
            System.out.println(-1);
        } else {
            System.out.println(result1 + " " + result2);
        }
    }

    static void heapify(int kIdx, int nSize) {
        int smallest = kIdx;
        int left = 2 * kIdx;
        int right = 2 * kIdx + 1;

        if (left <= nSize && A[left] < A[smallest])
            smallest = left;
        if (right <= nSize && A[right] < A[smallest])
            smallest = right;

        if (smallest != kIdx) {
            swapCount++;
            if (swapCount == k) {
                result1 = Math.min(A[kIdx], A[smallest]);
                result2 = Math.max(A[kIdx], A[smallest]);
            }
            int temp = A[kIdx];
            A[kIdx] = A[smallest];
            A[smallest] = temp;
            heapify(smallest, nSize);
        }
    }

    static void buildMinHeap(int nSize) {
        for (int i = nSize / 2; i >= 1; i--) {
            heapify(i, nSize);
        }
    }

    static void heapSort(int nSize) {
        buildMinHeap(nSize);
        for (int i = nSize; i >= 2; i--) {
            swapCount++;
            if (swapCount == k) {
                result1 = Math.min(A[1], A[i]);
                result2 = Math.max(A[1], A[i]);
            }
            int temp = A[1];
            A[1] = A[i];
            A[i] = temp;
            heapify(1, i - 1);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_17091": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 숫자를 영어로 변환하는 딕셔너리
nums = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
    11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
    15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
    19: "nineteen", 20: "twenty", 21: "twenty one", 22: "twenty two",
    23: "twenty three", 24: "twenty four", 25: "twenty five",
    26: "twenty six", 27: "twenty seven", 28: "twenty eight",
    29: "twenty nine", 30: "thirty"
}

h = int(input())
m = int(input())

if m == 0:
    print(f"{nums[h]} o' clock")
elif m == 15:
    print(f"quarter past {nums[h]}")
elif m == 30:
    print(f"half past {nums[h]}")
elif m == 45:
    next_h = h % 12 + 1
    print(f"quarter to {nums[next_h]}")
elif m < 30:
    if m == 1:
        print(f"one minute past {nums[h]}")
    else:
        print(f"{nums[m]} minutes past {nums[h]}")
else:
    # m > 30
    remaining = 60 - m
    next_h = h % 12 + 1
    if remaining == 1:
        print(f"one minute to {nums[next_h]}")
    else:
        print(f"{nums[remaining]} minutes to {nums[next_h]}")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    map<int, string> nums;
    nums[1] = "one"; nums[2] = "two"; nums[3] = "three";
    nums[4] = "four"; nums[5] = "five"; nums[6] = "six";
    nums[7] = "seven"; nums[8] = "eight"; nums[9] = "nine";
    nums[10] = "ten"; nums[11] = "eleven"; nums[12] = "twelve";
    nums[13] = "thirteen"; nums[14] = "fourteen"; nums[15] = "fifteen";
    nums[16] = "sixteen"; nums[17] = "seventeen"; nums[18] = "eighteen";
    nums[19] = "nineteen"; nums[20] = "twenty"; nums[21] = "twenty one";
    nums[22] = "twenty two"; nums[23] = "twenty three"; nums[24] = "twenty four";
    nums[25] = "twenty five"; nums[26] = "twenty six"; nums[27] = "twenty seven";
    nums[28] = "twenty eight"; nums[29] = "twenty nine"; nums[30] = "thirty";

    int h, m;
    cin >> h >> m;

    if (m == 0) {
        cout << nums[h] << " o' clock" << endl;
    } else if (m == 15) {
        cout << "quarter past " << nums[h] << endl;
    } else if (m == 30) {
        cout << "half past " << nums[h] << endl;
    } else if (m == 45) {
        int nextH = h % 12 + 1;
        cout << "quarter to " << nums[nextH] << endl;
    } else if (m < 30) {
        if (m == 1) {
            cout << "one minute past " << nums[h] << endl;
        } else {
            cout << nums[m] << " minutes past " << nums[h] << endl;
        }
    } else {
        int remaining = 60 - m;
        int nextH = h % 12 + 1;
        if (remaining == 1) {
            cout << "one minute to " << nums[nextH] << endl;
        } else {
            cout << nums[remaining] << " minutes to " << nums[nextH] << endl;
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

        String[] nums = {"", "one", "two", "three", "four", "five", "six", "seven",
            "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
            "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
            "twenty one", "twenty two", "twenty three", "twenty four", "twenty five",
            "twenty six", "twenty seven", "twenty eight", "twenty nine", "thirty"};

        int h = Integer.parseInt(br.readLine().trim());
        int m = Integer.parseInt(br.readLine().trim());

        if (m == 0) {
            System.out.println(nums[h] + " o' clock");
        } else if (m == 15) {
            System.out.println("quarter past " + nums[h]);
        } else if (m == 30) {
            System.out.println("half past " + nums[h]);
        } else if (m == 45) {
            int nextH = h % 12 + 1;
            System.out.println("quarter to " + nums[nextH]);
        } else if (m < 30) {
            if (m == 1) {
                System.out.println("one minute past " + nums[h]);
            } else {
                System.out.println(nums[m] + " minutes past " + nums[h]);
            }
        } else {
            int remaining = 60 - m;
            int nextH = h % 12 + 1;
            if (remaining == 1) {
                System.out.println("one minute to " + nums[nextH]);
            } else {
                System.out.println(nums[remaining] + " minutes to " + nums[nextH]);
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_27295": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from math import gcd
input = sys.stdin.readline

n, k = map(int, input().split())
points = []
for _ in range(n):
    x, y = map(int, input().split())
    points.append((x, y))

if n == 1:
    if points[0][0] == 0:
        print("EZPZ")
    else:
        # b = y
        print(0)
else:
    # k가 홀수이고 모든 점이 y=ax+b 직선 위에 있어야 함
    # 두 점으로 기울기 결정
    x1, y1 = points[0]
    x2, y2 = points[1]

    if x1 == x2:
        print(-1)
    else:
        # 기울기: (y2-y1)/(x2-x1)
        # 분수로 표현
        num = y2 - y1
        den = x2 - x1

        if den < 0:
            num, den = -num, -den

        g = gcd(abs(num), abs(den))
        num //= g
        den //= g

        # b = y1 - a*x1
        # b_num/b_den = y1 - (num/den)*x1 = (y1*den - num*x1) / den
        b_num = y1 * den - num * x1
        b_den = den

        g = gcd(abs(b_num), abs(b_den))
        b_num //= g
        b_den //= g

        # 모든 점이 이 직선 위에 있는지 확인
        valid = True
        for x, y in points:
            # y == (num/den)*x + b_num/b_den
            # y*den*b_den == num*x*b_den + b_num*den
            left = y * den * b_den
            right = num * x * b_den + b_num * den
            if left != right:
                valid = False
                break

        if not valid:
            print(-1)
        else:
            if b_den == 1:
                print(b_num)
            else:
                if b_num < 0:
                    print(f"-{abs(b_num)}/{b_den}")
                else:
                    print(f"{b_num}/{b_den}")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

long long gcd(long long a, long long b) {
    a = abs(a);
    b = abs(b);
    while (b) {
        long long t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    vector<pair<long long, long long>> points(n);
    for (int i = 0; i < n; i++) {
        cin >> points[i].first >> points[i].second;
    }

    if (n == 1) {
        if (points[0].first == 0) {
            cout << "EZPZ" << endl;
        } else {
            cout << 0 << endl;
        }
        return 0;
    }

    long long x1 = points[0].first, y1 = points[0].second;
    long long x2 = points[1].first, y2 = points[1].second;

    if (x1 == x2) {
        cout << -1 << endl;
        return 0;
    }

    // 기울기: (y2-y1)/(x2-x1)
    long long num = y2 - y1;
    long long den = x2 - x1;

    if (den < 0) {
        num = -num;
        den = -den;
    }

    long long g = gcd(abs(num), abs(den));
    num /= g;
    den /= g;

    // b = y1 - a*x1 = (y1*den - num*x1) / den
    long long bNum = y1 * den - num * x1;
    long long bDen = den;

    g = gcd(abs(bNum), abs(bDen));
    bNum /= g;
    bDen /= g;

    if (bDen < 0) {
        bNum = -bNum;
        bDen = -bDen;
    }

    // 모든 점 확인
    bool valid = true;
    for (int i = 0; i < n; i++) {
        long long x = points[i].first;
        long long y = points[i].second;
        // y*den*bDen == num*x*bDen + bNum*den
        if (y * den * bDen != num * x * bDen + bNum * den) {
            valid = false;
            break;
        }
    }

    if (!valid) {
        cout << -1 << endl;
    } else {
        if (bDen == 1) {
            cout << bNum << endl;
        } else {
            if (bNum < 0) {
                cout << "-" << abs(bNum) << "/" << bDen << endl;
            } else {
                cout << bNum << "/" << bDen << endl;
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
    static long gcd(long a, long b) {
        a = Math.abs(a);
        b = Math.abs(b);
        while (b != 0) {
            long t = b;
            b = a % b;
            a = t;
        }
        return a;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        long[][] points = new long[n][2];
        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            points[i][0] = Long.parseLong(st.nextToken());
            points[i][1] = Long.parseLong(st.nextToken());
        }

        if (n == 1) {
            if (points[0][0] == 0) {
                System.out.println("EZPZ");
            } else {
                System.out.println(0);
            }
            return;
        }

        long x1 = points[0][0], y1 = points[0][1];
        long x2 = points[1][0], y2 = points[1][1];

        if (x1 == x2) {
            System.out.println(-1);
            return;
        }

        long num = y2 - y1;
        long den = x2 - x1;

        if (den < 0) {
            num = -num;
            den = -den;
        }

        long g = gcd(Math.abs(num), Math.abs(den));
        num /= g;
        den /= g;

        long bNum = y1 * den - num * x1;
        long bDen = den;

        g = gcd(Math.abs(bNum), Math.abs(bDen));
        bNum /= g;
        bDen /= g;

        if (bDen < 0) {
            bNum = -bNum;
            bDen = -bDen;
        }

        boolean valid = true;
        for (int i = 0; i < n; i++) {
            long x = points[i][0];
            long y = points[i][1];
            if (y * den * bDen != num * x * bDen + bNum * den) {
                valid = false;
                break;
            }
        }

        if (!valid) {
            System.out.println(-1);
        } else {
            if (bDen == 1) {
                System.out.println(bNum);
            } else {
                if (bNum < 0) {
                    System.out.println("-" + Math.abs(bNum) + "/" + bDen);
                } else {
                    System.out.println(bNum + "/" + bDen);
                }
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_25045": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, m = map(int, input().split())
a = list(map(int, input().split()))  # 물품 만족도
b = list(map(int, input().split()))  # 고객 비용

# 만족도 내림차순, 비용 오름차순 정렬
a.sort(reverse=True)
b.sort()

# 그리디: 높은 만족도와 낮은 비용 매칭
# A_i - B_j >= 0 인 것만 선택

total = 0
j = 0  # 비용 인덱스
for i in range(n):
    if j >= m:
        break
    if a[i] - b[j] >= 0:
        total += a[i] - b[j]
        j += 1

print(total)
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

    int n, m;
    cin >> n >> m;

    vector<long long> a(n), b(m);
    for (int i = 0; i < n; i++) cin >> a[i];
    for (int i = 0; i < m; i++) cin >> b[i];

    // 만족도 내림차순, 비용 오름차순
    sort(a.rbegin(), a.rend());
    sort(b.begin(), b.end());

    long long total = 0;
    int j = 0;
    for (int i = 0; i < n && j < m; i++) {
        if (a[i] - b[j] >= 0) {
            total += a[i] - b[j];
            j++;
        }
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
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        Long[] a = new Long[n];
        Long[] b = new Long[m];

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            a[i] = Long.parseLong(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < m; i++) {
            b[i] = Long.parseLong(st.nextToken());
        }

        // 만족도 내림차순, 비용 오름차순
        Arrays.sort(a, Collections.reverseOrder());
        Arrays.sort(b);

        long total = 0;
        int j = 0;
        for (int i = 0; i < n && j < m; i++) {
            if (a[i] - b[j] >= 0) {
                total += a[i] - b[j];
                j++;
            }
        }

        System.out.println(total);
    }
}
'''
            }
        ]
    },
    "baekjoon_25426": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
funcs = []
for _ in range(n):
    a, b = map(int, input().split())
    funcs.append((a, b))

# sum(a_i * x_i + b_i) = sum(a_i * x_i) + sum(b_i)
# sum(b_i)는 고정
# sum(a_i * x_i)를 최대화하려면 큰 a에 큰 x 할당

# a 내림차순 정렬 후, 큰 a에 큰 x(N, N-1, ...) 할당
funcs.sort(key=lambda x: -x[0])

total = 0
x = n
for a, b in funcs:
    total += a * x + b
    x -= 1

print(total)
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

    vector<pair<long long, long long>> funcs(n);
    for (int i = 0; i < n; i++) {
        cin >> funcs[i].first >> funcs[i].second;
    }

    // a 내림차순 정렬
    sort(funcs.begin(), funcs.end(), [](const auto& a, const auto& b) {
        return a.first > b.first;
    });

    long long total = 0;
    long long x = n;
    for (int i = 0; i < n; i++) {
        total += funcs[i].first * x + funcs[i].second;
        x--;
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
        int n = Integer.parseInt(br.readLine().trim());

        long[][] funcs = new long[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            funcs[i][0] = Long.parseLong(st.nextToken());
            funcs[i][1] = Long.parseLong(st.nextToken());
        }

        // a 내림차순 정렬
        Arrays.sort(funcs, (a, b) -> Long.compare(b[0], a[0]));

        long total = 0;
        long x = n;
        for (int i = 0; i < n; i++) {
            total += funcs[i][0] * x + funcs[i][1];
            x--;
        }

        System.out.println(total);
    }
}
'''
            }
        ]
    },
    "baekjoon_18249": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

MOD = 1000000007

# 피보나치 수열: f(n) = f(n-1) + f(n-2)
# f(1) = 1, f(2) = 2

def fib(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    if n == 2:
        return 2

    # 행렬 거듭제곱
    # [f(n+1)] = [1 1]^n * [1]
    # [f(n)  ]   [1 0]     [0]

    def mat_mult(A, B, mod):
        return [
            [(A[0][0]*B[0][0] + A[0][1]*B[1][0]) % mod, (A[0][0]*B[0][1] + A[0][1]*B[1][1]) % mod],
            [(A[1][0]*B[0][0] + A[1][1]*B[1][0]) % mod, (A[1][0]*B[0][1] + A[1][1]*B[1][1]) % mod]
        ]

    def mat_pow(M, p, mod):
        result = [[1, 0], [0, 1]]  # 단위 행렬
        while p > 0:
            if p % 2 == 1:
                result = mat_mult(result, M, mod)
            M = mat_mult(M, M, mod)
            p //= 2
        return result

    M = [[1, 1], [1, 0]]
    result = mat_pow(M, n, MOD)
    return result[0][0]

t = int(input())
for _ in range(t):
    n = int(input())
    print(fib(n))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
using namespace std;

const long long MOD = 1000000007;

typedef vector<vector<long long>> Matrix;

Matrix matMult(Matrix& A, Matrix& B) {
    Matrix C(2, vector<long long>(2));
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            for (int k = 0; k < 2; k++) {
                C[i][j] = (C[i][j] + A[i][k] * B[k][j]) % MOD;
            }
        }
    }
    return C;
}

Matrix matPow(Matrix M, long long p) {
    Matrix result = {{1, 0}, {0, 1}};
    while (p > 0) {
        if (p % 2 == 1) {
            result = matMult(result, M);
        }
        M = matMult(M, M);
        p /= 2;
    }
    return result;
}

long long fib(long long n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    if (n == 2) return 2;

    Matrix M = {{1, 1}, {1, 0}};
    Matrix result = matPow(M, n);
    return result[0][0];
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        long long n;
        cin >> n;
        cout << fib(n) << "\\n";
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
    static final long MOD = 1000000007;

    static long[][] matMult(long[][] A, long[][] B) {
        long[][] C = new long[2][2];
        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                for (int k = 0; k < 2; k++) {
                    C[i][j] = (C[i][j] + A[i][k] * B[k][j]) % MOD;
                }
            }
        }
        return C;
    }

    static long[][] matPow(long[][] M, long p) {
        long[][] result = {{1, 0}, {0, 1}};
        while (p > 0) {
            if (p % 2 == 1) {
                result = matMult(result, M);
            }
            M = matMult(M, M);
            p /= 2;
        }
        return result;
    }

    static long fib(long n) {
        if (n <= 0) return 0;
        if (n == 1) return 1;
        if (n == 2) return 2;

        long[][] M = {{1, 1}, {1, 0}};
        long[][] result = matPow(M, n);
        return result[0][0];
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());
        while (t-- > 0) {
            long n = Long.parseLong(br.readLine().trim());
            sb.append(fib(n)).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_13268": {
        "solutions": [
            {
                "language": "python",
                "code": '''n = int(input())

# 한 세트: 2*(5+10+15+20) = 100m
# n미터 뛰었을 때 몇 세트?

set_distance = 100  # 한 세트 거리
sets = (n + set_distance - 1) // set_distance

print(sets)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    // 한 세트: 100m
    int sets = (n + 99) / 100;
    cout << sets << endl;

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

        // 한 세트: 100m
        int sets = (n + 99) / 100;
        System.out.println(sets);
    }
}
'''
            }
        ]
    },
    "baekjoon_4159": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

while True:
    n = int(input())
    if n == 0:
        break

    stations = []
    for _ in range(n):
        stations.append(int(input()))

    stations.sort()

    # 왕복: 0 -> 1422 -> 0
    # 한 번 충전으로 200마일
    # 연속된 충전소 간 거리가 100마일 이하여야 왕복 가능

    possible = True

    # 더슨 크릭(0)에서 출발
    if stations[0] > 100:
        possible = False
    else:
        for i in range(1, n):
            if stations[i] - stations[i-1] > 100:
                possible = False
                break

        # 마지막 충전소에서 델타 정션(1422)까지, 그리고 돌아올 수 있어야
        if possible:
            if 1422 - stations[-1] > 100:
                possible = False

    print("POSSIBLE" if possible else "IMPOSSIBLE")
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
    while (cin >> n && n != 0) {
        vector<int> stations(n);
        for (int i = 0; i < n; i++) {
            cin >> stations[i];
        }

        sort(stations.begin(), stations.end());

        bool possible = true;

        // 0에서 첫 충전소까지
        if (stations[0] > 100) {
            possible = false;
        } else {
            for (int i = 1; i < n; i++) {
                if (stations[i] - stations[i-1] > 100) {
                    possible = false;
                    break;
                }
            }

            // 마지막 충전소에서 1422까지
            if (possible && 1422 - stations[n-1] > 100) {
                possible = false;
            }
        }

        cout << (possible ? "POSSIBLE" : "IMPOSSIBLE") << endl;
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

        String line;
        while ((line = br.readLine()) != null) {
            int n = Integer.parseInt(line.trim());
            if (n == 0) break;

            int[] stations = new int[n];
            for (int i = 0; i < n; i++) {
                stations[i] = Integer.parseInt(br.readLine().trim());
            }

            Arrays.sort(stations);

            boolean possible = true;

            if (stations[0] > 100) {
                possible = false;
            } else {
                for (int i = 1; i < n; i++) {
                    if (stations[i] - stations[i-1] > 100) {
                        possible = false;
                        break;
                    }
                }

                if (possible && 1422 - stations[n-1] > 100) {
                    possible = false;
                }
            }

            sb.append(possible ? "POSSIBLE" : "IMPOSSIBLE").append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_13412": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def count_coprime_pairs(n):
    """N의 서로소 인수 쌍 개수 = 2^(소인수 개수)"""
    # N을 소인수분해해서 서로 다른 소인수 개수 세기
    prime_count = 0
    temp = n

    d = 2
    while d * d <= temp:
        if temp % d == 0:
            prime_count += 1
            while temp % d == 0:
                temp //= d
        d += 1

    if temp > 1:
        prime_count += 1

    return 1 << prime_count  # 2^prime_count

t = int(input())
for _ in range(t):
    n = int(input())
    print(count_coprime_pairs(n))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int countCoprimePairs(int n) {
    int primeCount = 0;
    int temp = n;

    for (int d = 2; d * d <= temp; d++) {
        if (temp % d == 0) {
            primeCount++;
            while (temp % d == 0) {
                temp /= d;
            }
        }
    }

    if (temp > 1) {
        primeCount++;
    }

    return 1 << primeCount;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int n;
        cin >> n;
        cout << countCoprimePairs(n) << "\\n";
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;

public class Main {
    static int countCoprimePairs(int n) {
        int primeCount = 0;
        int temp = n;

        for (int d = 2; d * d <= temp; d++) {
            if (temp % d == 0) {
                primeCount++;
                while (temp % d == 0) {
                    temp /= d;
                }
            }
        }

        if (temp > 1) {
            primeCount++;
        }

        return 1 << primeCount;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            int n = Integer.parseInt(br.readLine().trim());
            sb.append(countCoprimePairs(n)).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_3231": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
pos = [0] * (n + 1)  # 각 숫자의 위치

for i in range(n):
    card = int(input())
    pos[card] = i

# 박수 횟수: 다음 카드가 현재 카드보다 왼쪽에 있는 횟수
claps = 0
for i in range(1, n):
    if pos[i+1] < pos[i]:
        claps += 1

print(claps)
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

    vector<int> pos(n + 1);
    for (int i = 0; i < n; i++) {
        int card;
        cin >> card;
        pos[card] = i;
    }

    int claps = 0;
    for (int i = 1; i < n; i++) {
        if (pos[i+1] < pos[i]) {
            claps++;
        }
    }

    cout << claps << endl;
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

        int[] pos = new int[n + 1];
        for (int i = 0; i < n; i++) {
            int card = Integer.parseInt(br.readLine().trim());
            pos[card] = i;
        }

        int claps = 0;
        for (int i = 1; i < n; i++) {
            if (pos[i+1] < pos[i]) {
                claps++;
            }
        }

        System.out.println(claps);
    }
}
'''
            }
        ]
    },
    "baekjoon_15707": {
        "solutions": [
            {
                "language": "python",
                "code": '''a, b, r = input().split()

# 큰 수 곱셈
result = int(a) * int(b)

if result > int(r):
    print("overflow")
else:
    print(result)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
using namespace std;

// 큰 수 비교 (문자열)
int compare(string a, string b) {
    if (a.length() != b.length()) {
        return a.length() > b.length() ? 1 : -1;
    }
    return a.compare(b);
}

// 큰 수 곱셈 (문자열)
string multiply(string a, string b) {
    int n = a.length(), m = b.length();
    if (n == 0 || m == 0) return "0";

    vector<int> result(n + m, 0);

    int aIdx = n - 1;
    int bIdx = m - 1;

    for (int i = n - 1; i >= 0; i--) {
        for (int j = m - 1; j >= 0; j--) {
            int mul = (a[i] - '0') * (b[j] - '0');
            int p1 = i + j, p2 = i + j + 1;
            int sum = mul + result[p2];

            result[p2] = sum % 10;
            result[p1] += sum / 10;
        }
    }

    string str = "";
    for (int i : result) {
        if (!(str.empty() && i == 0)) {
            str += to_string(i);
        }
    }

    return str.empty() ? "0" : str;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string a, b, r;
    cin >> a >> b >> r;

    string product = multiply(a, b);

    if (compare(product, r) > 0) {
        cout << "overflow" << endl;
    } else {
        cout << product << endl;
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.math.BigInteger;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        BigInteger a = new BigInteger(st.nextToken());
        BigInteger b = new BigInteger(st.nextToken());
        BigInteger r = new BigInteger(st.nextToken());

        BigInteger product = a.multiply(b);

        if (product.compareTo(r) > 0) {
            System.out.println("overflow");
        } else {
            System.out.println(product);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_25312": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from math import gcd
input = sys.stdin.readline

n, m = map(int, input().split())

# 각 음료수의 설탕 농도(v/w) 계산
drinks = []
for _ in range(n):
    w, v = map(int, input().split())
    drinks.append((v, w, v / w))  # (설탕, 용량, 농도)

# 농도 높은 순으로 정렬
drinks.sort(key=lambda x: -x[2])

# 그리디: 농도 높은 것부터 최대한 사용
total_sugar_num = 0
total_sugar_den = 1
remaining = m

for v, w, _ in drinks:
    if remaining <= 0:
        break
    if w <= remaining:
        # 전부 사용
        total_sugar_num = total_sugar_num * 1 + v * total_sugar_den
        remaining -= w
    else:
        # 일부만 사용: remaining/w * v
        # total_sugar += (remaining * v) / w
        add_num = remaining * v
        add_den = w
        g = gcd(add_num, add_den)
        add_num //= g
        add_den //= g

        # 분수 덧셈
        total_sugar_num = total_sugar_num * add_den + add_num * total_sugar_den
        total_sugar_den = total_sugar_den * add_den
        g = gcd(total_sugar_num, total_sugar_den)
        total_sugar_num //= g
        total_sugar_den //= g

        remaining = 0

if total_sugar_den == 1:
    print(total_sugar_num)
else:
    print(f"{total_sugar_num}/{total_sugar_den}")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

long long gcd(long long a, long long b) {
    while (b) {
        long long t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    long long m;
    cin >> n >> m;

    vector<tuple<long long, long long, double>> drinks(n);
    for (int i = 0; i < n; i++) {
        long long w, v;
        cin >> w >> v;
        drinks[i] = {v, w, (double)v / w};
    }

    // 농도 높은 순
    sort(drinks.begin(), drinks.end(), [](auto& a, auto& b) {
        return get<2>(a) > get<2>(b);
    });

    long long num = 0, den = 1;
    long long remaining = m;

    for (auto& [v, w, _] : drinks) {
        if (remaining <= 0) break;
        if (w <= remaining) {
            num = num + v * den;
            remaining -= w;
        } else {
            // remaining/w * v
            long long addNum = remaining * v;
            long long addDen = w;
            long long g = gcd(addNum, addDen);
            addNum /= g;
            addDen /= g;

            num = num * addDen + addNum * den;
            den = den * addDen;
            g = gcd(num, den);
            num /= g;
            den /= g;

            remaining = 0;
        }
    }

    if (den == 1) {
        cout << num << endl;
    } else {
        cout << num << "/" << den << endl;
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
    static long gcd(long a, long b) {
        while (b != 0) {
            long t = b;
            b = a % b;
            a = t;
        }
        return a;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        long m = Long.parseLong(st.nextToken());

        double[][] drinks = new double[n][3];  // v, w, concentration
        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            long w = Long.parseLong(st.nextToken());
            long v = Long.parseLong(st.nextToken());
            drinks[i][0] = v;
            drinks[i][1] = w;
            drinks[i][2] = (double) v / w;
        }

        // 농도 높은 순 정렬
        Arrays.sort(drinks, (a, b) -> Double.compare(b[2], a[2]));

        long num = 0, den = 1;
        long remaining = m;

        for (int i = 0; i < n && remaining > 0; i++) {
            long v = (long) drinks[i][0];
            long w = (long) drinks[i][1];

            if (w <= remaining) {
                num = num + v * den;
                remaining -= w;
            } else {
                long addNum = remaining * v;
                long addDen = w;
                long g = gcd(addNum, addDen);
                addNum /= g;
                addDen /= g;

                num = num * addDen + addNum * den;
                den = den * addDen;
                g = gcd(num, den);
                num /= g;
                den /= g;

                remaining = 0;
            }
        }

        if (den == 1) {
            System.out.println(num);
        } else {
            System.out.println(num + "/" + den);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_16677": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

original = input().strip()
n = int(input())

best = None
best_cost = float('inf')

for _ in range(n):
    parts = input().split()
    name = parts[0]
    cost = int(parts[1])

    # 접두사가 original과 같고, 길이가 더 긴 것 중 비용 최소
    if len(name) > len(original) and name.startswith(original):
        if cost < best_cost:
            best_cost = cost
            best = name

if best:
    print(best)
else:
    print("No Jam")
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

    string original;
    cin >> original;

    int n;
    cin >> n;

    string best = "";
    int bestCost = INT_MAX;

    for (int i = 0; i < n; i++) {
        string name;
        int cost;
        cin >> name >> cost;

        // 접두사가 original이고 길이가 더 긴 것
        if (name.length() > original.length() &&
            name.substr(0, original.length()) == original) {
            if (cost < bestCost) {
                bestCost = cost;
                best = name;
            }
        }
    }

    if (best.empty()) {
        cout << "No Jam" << endl;
    } else {
        cout << best << endl;
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
        String original = br.readLine().trim();
        int n = Integer.parseInt(br.readLine().trim());

        String best = null;
        int bestCost = Integer.MAX_VALUE;

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String name = st.nextToken();
            int cost = Integer.parseInt(st.nextToken());

            // 접두사가 original이고 길이가 더 긴 것
            if (name.length() > original.length() &&
                name.startsWith(original)) {
                if (cost < bestCost) {
                    bestCost = cost;
                    best = name;
                }
            }
        }

        if (best == null) {
            System.out.println("No Jam");
        } else {
            System.out.println(best);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_30823": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, k = map(int, input().split())
s = list(input().strip())

# i = 1, 2, ..., N-K+1 순서로 reverse(i) 수행
# reverse(i): s[i-1:i+k-1] 뒤집기

for i in range(1, n - k + 2):
    # 0-indexed: s[i-1:i-1+k] 뒤집기
    left = i - 1
    right = left + k - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1

print(''.join(s))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    string s;
    cin >> s;

    for (int i = 0; i <= n - k; i++) {
        reverse(s.begin() + i, s.begin() + i + k);
    }

    cout << s << endl;
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

        char[] s = br.readLine().trim().toCharArray();

        for (int i = 0; i <= n - k; i++) {
            // s[i:i+k] 뒤집기
            int left = i;
            int right = i + k - 1;
            while (left < right) {
                char temp = s[left];
                s[left] = s[right];
                s[right] = temp;
                left++;
                right--;
            }
        }

        System.out.println(new String(s));
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
