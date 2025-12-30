#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
10개의 중간 난이도 문제에 대한 솔루션 추가 스크립트
빈 solutions 배열을 가진 문제에만 솔루션을 추가합니다.
"""

import json
import fcntl
import os

JSON_PATH = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

# 솔루션 정의
SOLUTIONS = {
    # 문제 16112: 5차 전직 (그리디, 정렬)
    "baekjoon_16112": [
        {
            "language": "python",
            "code": '''# 백준 16112: 5차 전직
# 그리디 + 정렬 문제
# 경험치가 큰 퀘스트를 나중에 처리하면 더 많은 아케인스톤에 경험치가 쌓임
import sys
input = sys.stdin.readline

n, k = map(int, input().split())
a = list(map(int, input().split()))

# 경험치를 오름차순으로 정렬
a.sort()

# 각 퀘스트를 처리할 때, 이전에 획득한 아케인스톤 중 최대 k개가 활성화됨
# i번째 퀘스트를 처리할 때 min(i, k)개의 아케인스톤이 활성화 상태
total = 0
for i in range(n):
    # i번째 퀘스트를 처리할 때 활성화된 아케인스톤 개수
    active_stones = min(i, k)
    total += a[i] * active_stones

print(total)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 16112: 5차 전직
// 그리디 + 정렬 문제
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        long[] a = new long[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            a[i] = Long.parseLong(st.nextToken());
        }

        // 경험치를 오름차순으로 정렬
        Arrays.sort(a);

        // 각 퀘스트를 처리할 때 활성화된 아케인스톤 개수만큼 경험치 추가
        long total = 0;
        for (int i = 0; i < n; i++) {
            // i번째 퀘스트를 처리할 때 활성화된 아케인스톤 개수
            int activeStones = Math.min(i, k);
            total += a[i] * activeStones;
        }

        System.out.println(total);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 16112: 5차 전직
// 그리디 + 정렬 문제
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    cin >> n >> k;

    vector<long long> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    // 경험치를 오름차순으로 정렬
    sort(a.begin(), a.end());

    // 각 퀘스트를 처리할 때 활성화된 아케인스톤 개수만큼 경험치 추가
    long long total = 0;
    for (int i = 0; i < n; i++) {
        // i번째 퀘스트를 처리할 때 활성화된 아케인스톤 개수
        int activeStones = min(i, k);
        total += a[i] * activeStones;
    }

    cout << total << "\\n";
    return 0;
}
'''
        }
    ],

    # 문제 17479: 정식당 (구현, 해시셋)
    "baekjoon_17479": [
        {
            "language": "python",
            "code": '''# 백준 17479: 정식당
# 구현 + 해시셋 문제
import sys
input = sys.stdin.readline

A, B, C = map(int, input().split())

# 메뉴 저장
normal_menu = {}  # 일반메뉴: {이름: 가격}
special_menu = {}  # 특별메뉴: {이름: 가격}
service_menu = set()  # 서비스메뉴: 이름만 저장

# 일반메뉴 입력
for _ in range(A):
    parts = input().split()
    name, price = parts[0], int(parts[1])
    normal_menu[name] = price

# 특별메뉴 입력
for _ in range(B):
    parts = input().split()
    name, price = parts[0], int(parts[1])
    special_menu[name] = price

# 서비스메뉴 입력
for _ in range(C):
    name = input().strip()
    service_menu.add(name)

# 주문 처리
N = int(input())
normal_total = 0  # 일반메뉴 주문 총액
special_total = 0  # 특별메뉴 주문 총액
service_count = 0  # 서비스메뉴 주문 개수
valid = True

for _ in range(N):
    order = input().strip()

    if order in normal_menu:
        normal_total += normal_menu[order]
    elif order in special_menu:
        special_total += special_menu[order]
    elif order in service_menu:
        service_count += 1
    # 메뉴에 있는 음식만 주문한다고 했으므로 else 케이스 없음

# 주문 검증
# 1. 특별메뉴는 일반메뉴 20000원 이상 주문해야 함
if special_total > 0 and normal_total < 20000:
    valid = False

# 2. 서비스메뉴는 일반+특별메뉴 50000원 이상 주문해야 함
if service_count > 0 and (normal_total + special_total) < 50000:
    valid = False

# 3. 서비스메뉴는 단 하나만 주문 가능
if service_count > 1:
    valid = False

print("Okay" if valid else "No")
'''
        },
        {
            "language": "java",
            "code": '''// 백준 17479: 정식당
// 구현 + 해시셋 문제
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int A = Integer.parseInt(st.nextToken());
        int B = Integer.parseInt(st.nextToken());
        int C = Integer.parseInt(st.nextToken());

        // 메뉴 저장
        Map<String, Integer> normalMenu = new HashMap<>();
        Map<String, Integer> specialMenu = new HashMap<>();
        Set<String> serviceMenu = new HashSet<>();

        // 일반메뉴 입력
        for (int i = 0; i < A; i++) {
            st = new StringTokenizer(br.readLine());
            String name = st.nextToken();
            int price = Integer.parseInt(st.nextToken());
            normalMenu.put(name, price);
        }

        // 특별메뉴 입력
        for (int i = 0; i < B; i++) {
            st = new StringTokenizer(br.readLine());
            String name = st.nextToken();
            int price = Integer.parseInt(st.nextToken());
            specialMenu.put(name, price);
        }

        // 서비스메뉴 입력
        for (int i = 0; i < C; i++) {
            serviceMenu.add(br.readLine().trim());
        }

        // 주문 처리
        int N = Integer.parseInt(br.readLine());
        long normalTotal = 0;
        long specialTotal = 0;
        int serviceCount = 0;

        for (int i = 0; i < N; i++) {
            String order = br.readLine().trim();

            if (normalMenu.containsKey(order)) {
                normalTotal += normalMenu.get(order);
            } else if (specialMenu.containsKey(order)) {
                specialTotal += specialMenu.get(order);
            } else if (serviceMenu.contains(order)) {
                serviceCount++;
            }
        }

        // 주문 검증
        boolean valid = true;

        // 특별메뉴는 일반메뉴 20000원 이상 주문해야 함
        if (specialTotal > 0 && normalTotal < 20000) {
            valid = false;
        }

        // 서비스메뉴는 일반+특별메뉴 50000원 이상 주문해야 함
        if (serviceCount > 0 && (normalTotal + specialTotal) < 50000) {
            valid = false;
        }

        // 서비스메뉴는 단 하나만 주문 가능
        if (serviceCount > 1) {
            valid = false;
        }

        System.out.println(valid ? "Okay" : "No");
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 17479: 정식당
// 구현 + 해시셋 문제
#include <iostream>
#include <string>
#include <unordered_map>
#include <unordered_set>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int A, B, C;
    cin >> A >> B >> C;

    // 메뉴 저장
    unordered_map<string, int> normalMenu;
    unordered_map<string, int> specialMenu;
    unordered_set<string> serviceMenu;

    // 일반메뉴 입력
    for (int i = 0; i < A; i++) {
        string name;
        int price;
        cin >> name >> price;
        normalMenu[name] = price;
    }

    // 특별메뉴 입력
    for (int i = 0; i < B; i++) {
        string name;
        int price;
        cin >> name >> price;
        specialMenu[name] = price;
    }

    // 서비스메뉴 입력
    for (int i = 0; i < C; i++) {
        string name;
        cin >> name;
        serviceMenu.insert(name);
    }

    // 주문 처리
    int N;
    cin >> N;
    long long normalTotal = 0;
    long long specialTotal = 0;
    int serviceCount = 0;

    for (int i = 0; i < N; i++) {
        string order;
        cin >> order;

        if (normalMenu.count(order)) {
            normalTotal += normalMenu[order];
        } else if (specialMenu.count(order)) {
            specialTotal += specialMenu[order];
        } else if (serviceMenu.count(order)) {
            serviceCount++;
        }
    }

    // 주문 검증
    bool valid = true;

    // 특별메뉴는 일반메뉴 20000원 이상 주문해야 함
    if (specialTotal > 0 && normalTotal < 20000) {
        valid = false;
    }

    // 서비스메뉴는 일반+특별메뉴 50000원 이상 주문해야 함
    if (serviceCount > 0 && (normalTotal + specialTotal) < 50000) {
        valid = false;
    }

    // 서비스메뉴는 단 하나만 주문 가능
    if (serviceCount > 1) {
        valid = false;
    }

    cout << (valid ? "Okay" : "No") << "\\n";
    return 0;
}
'''
        }
    ],

    # 문제 19699: 소-난다! (조합 + 소수 판정)
    "baekjoon_19699": [
        {
            "language": "python",
            "code": '''# 백준 19699: 소-난다!
# 조합 + 소수 판정 문제
from itertools import combinations

def is_prime(n):
    """소수 판정 함수"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

N, M = map(int, input().split())
weights = list(map(int, input().split()))

# M마리 소를 선택하는 모든 조합에서 몸무게 합이 소수인 경우 찾기
prime_sums = set()
for comb in combinations(weights, M):
    total = sum(comb)
    if is_prime(total):
        prime_sums.add(total)

# 결과 출력
if prime_sums:
    print(' '.join(map(str, sorted(prime_sums))))
else:
    print(-1)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 19699: 소-난다!
// 조합 + 소수 판정 문제
import java.io.*;
import java.util.*;

public class Main {
    static int N, M;
    static int[] weights;
    static Set<Integer> primeSums = new TreeSet<>();

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        N = Integer.parseInt(st.nextToken());
        M = Integer.parseInt(st.nextToken());

        weights = new int[N];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            weights[i] = Integer.parseInt(st.nextToken());
        }

        // 조합 생성
        combination(0, 0, 0);

        // 결과 출력
        if (primeSums.isEmpty()) {
            System.out.println(-1);
        } else {
            StringBuilder sb = new StringBuilder();
            for (int sum : primeSums) {
                sb.append(sum).append(" ");
            }
            System.out.println(sb.toString().trim());
        }
    }

    // 조합 생성 함수
    static void combination(int start, int count, int sum) {
        if (count == M) {
            if (isPrime(sum)) {
                primeSums.add(sum);
            }
            return;
        }

        for (int i = start; i < N; i++) {
            combination(i + 1, count + 1, sum + weights[i]);
        }
    }

    // 소수 판정 함수
    static boolean isPrime(int n) {
        if (n < 2) return false;
        if (n == 2) return true;
        if (n % 2 == 0) return false;
        for (int i = 3; i * i <= n; i += 2) {
            if (n % i == 0) return false;
        }
        return true;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 19699: 소-난다!
// 조합 + 소수 판정 문제
#include <iostream>
#include <vector>
#include <set>
#include <cmath>
using namespace std;

int N, M;
vector<int> weights;
set<int> primeSums;

// 소수 판정 함수
bool isPrime(int n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    for (int i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return false;
    }
    return true;
}

// 조합 생성 함수
void combination(int start, int count, int sum) {
    if (count == M) {
        if (isPrime(sum)) {
            primeSums.insert(sum);
        }
        return;
    }

    for (int i = start; i < N; i++) {
        combination(i + 1, count + 1, sum + weights[i]);
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> N >> M;
    weights.resize(N);
    for (int i = 0; i < N; i++) {
        cin >> weights[i];
    }

    // 조합 생성
    combination(0, 0, 0);

    // 결과 출력
    if (primeSums.empty()) {
        cout << -1 << "\\n";
    } else {
        bool first = true;
        for (int sum : primeSums) {
            if (!first) cout << " ";
            cout << sum;
            first = false;
        }
        cout << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # 문제 28217: 두 정삼각형 (구현)
    "baekjoon_28217": [
        {
            "language": "python",
            "code": '''# 백준 28217: 두 정삼각형
# 구현 문제 - 정삼각형 회전/대칭
import sys
input = sys.stdin.readline

def read_triangle(n):
    """정삼각형 읽기"""
    triangle = []
    for i in range(1, n + 1):
        row = list(map(int, input().split()))
        triangle.append(row)
    return triangle

def rotate_cw(tri, n):
    """시계방향 120도 회전"""
    new_tri = []
    for i in range(1, n + 1):
        row = []
        for j in range(i):
            # 새 위치 계산
            row.append(tri[n - 1 - j][n - i])
        new_tri.append(row)
    return new_tri

def reflect(tri, n):
    """좌우 대칭"""
    new_tri = []
    for i in range(n):
        new_tri.append(tri[i][::-1])
    return new_tri

def count_diff(a, b, n):
    """두 정삼각형의 차이 계산"""
    diff = 0
    for i in range(n):
        for j in range(i + 1):
            if a[i][j] != b[i][j]:
                diff += 1
    return diff

n = int(input())
A = read_triangle(n)
B = read_triangle(n)

min_diff = float('inf')

# 원본과 대칭
current = A
for _ in range(2):  # 원본, 대칭
    for _ in range(3):  # 0도, 120도, 240도 회전
        diff = count_diff(current, B, n)
        min_diff = min(min_diff, diff)
        current = rotate_cw(current, n)
    current = reflect(A, n)

print(min_diff)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 28217: 두 정삼각형
// 구현 문제 - 정삼각형 회전/대칭
import java.io.*;
import java.util.*;

public class Main {
    static int n;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        n = Integer.parseInt(br.readLine().trim());

        int[][] A = readTriangle(br);
        int[][] B = readTriangle(br);

        int minDiff = Integer.MAX_VALUE;

        // 원본과 대칭에서 각각 3번 회전
        int[][] current = copyTriangle(A);
        for (int flip = 0; flip < 2; flip++) {
            for (int rot = 0; rot < 3; rot++) {
                int diff = countDiff(current, B);
                minDiff = Math.min(minDiff, diff);
                current = rotateCW(current);
            }
            current = reflect(A);
        }

        System.out.println(minDiff);
    }

    static int[][] readTriangle(BufferedReader br) throws IOException {
        int[][] tri = new int[n][];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            tri[i] = new int[i + 1];
            for (int j = 0; j <= i; j++) {
                tri[i][j] = Integer.parseInt(st.nextToken());
            }
        }
        return tri;
    }

    static int[][] copyTriangle(int[][] tri) {
        int[][] copy = new int[n][];
        for (int i = 0; i < n; i++) {
            copy[i] = tri[i].clone();
        }
        return copy;
    }

    static int[][] rotateCW(int[][] tri) {
        int[][] newTri = new int[n][];
        for (int i = 0; i < n; i++) {
            newTri[i] = new int[i + 1];
            for (int j = 0; j <= i; j++) {
                newTri[i][j] = tri[n - 1 - j][n - 1 - i];
            }
        }
        return newTri;
    }

    static int[][] reflect(int[][] tri) {
        int[][] newTri = new int[n][];
        for (int i = 0; i < n; i++) {
            newTri[i] = new int[i + 1];
            for (int j = 0; j <= i; j++) {
                newTri[i][j] = tri[i][i - j];
            }
        }
        return newTri;
    }

    static int countDiff(int[][] a, int[][] b) {
        int diff = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j <= i; j++) {
                if (a[i][j] != b[i][j]) diff++;
            }
        }
        return diff;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 28217: 두 정삼각형
// 구현 문제 - 정삼각형 회전/대칭
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int n;

vector<vector<int>> readTriangle() {
    vector<vector<int>> tri(n);
    for (int i = 0; i < n; i++) {
        tri[i].resize(i + 1);
        for (int j = 0; j <= i; j++) {
            cin >> tri[i][j];
        }
    }
    return tri;
}

vector<vector<int>> rotateCW(const vector<vector<int>>& tri) {
    vector<vector<int>> newTri(n);
    for (int i = 0; i < n; i++) {
        newTri[i].resize(i + 1);
        for (int j = 0; j <= i; j++) {
            newTri[i][j] = tri[n - 1 - j][n - 1 - i];
        }
    }
    return newTri;
}

vector<vector<int>> reflect(const vector<vector<int>>& tri) {
    vector<vector<int>> newTri(n);
    for (int i = 0; i < n; i++) {
        newTri[i].resize(i + 1);
        for (int j = 0; j <= i; j++) {
            newTri[i][j] = tri[i][i - j];
        }
    }
    return newTri;
}

int countDiff(const vector<vector<int>>& a, const vector<vector<int>>& b) {
    int diff = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j <= i; j++) {
            if (a[i][j] != b[i][j]) diff++;
        }
    }
    return diff;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n;
    vector<vector<int>> A = readTriangle();
    vector<vector<int>> B = readTriangle();

    int minDiff = 1e9;

    // 원본과 대칭에서 각각 3번 회전
    vector<vector<int>> current = A;
    for (int flip = 0; flip < 2; flip++) {
        for (int rot = 0; rot < 3; rot++) {
            int diff = countDiff(current, B);
            minDiff = min(minDiff, diff);
            current = rotateCW(current);
        }
        current = reflect(A);
    }

    cout << minDiff << "\\n";
    return 0;
}
'''
        }
    ],

    # 문제 31964: 반품 회수 (그리디)
    "baekjoon_31964": [
        {
            "language": "python",
            "code": '''# 백준 31964: 반품 회수
# 그리디 문제 - 가장 먼 집까지 갔다가 돌아오는 시간 + 대기 시간 고려
import sys
input = sys.stdin.readline

n = int(input())
X = list(map(int, input().split()))  # 각 집의 위치
T = list(map(int, input().split()))  # 각 집이 물건을 내놓는 시각

# 가장 먼 집의 위치
max_x = max(X)

# 트럭이 가장 먼 집까지 갔다가 돌아오는 기본 시간
base_time = 2 * max_x

# 각 집에서 물건을 회수할 수 있는 최소 시간 계산
# 트럭이 위치 x에 도착하는 시간은 x (왕복 경로 중 가는 길)
# 또는 2*max_x - x (돌아오는 길)
max_wait = 0
for i in range(n):
    x, t = X[i], T[i]
    # 가는 길에 회수하려면 시간 x에 도착, t까지 기다려야 함
    # 돌아오는 길에 회수하려면 시간 2*max_x - x에 도착
    # 어느 경로든 물건이 나와 있어야 함

    # 가는 길에 도착하는 시간: x
    # 물건이 나오는 시간: t
    # 가는 길에 회수하려면 x >= t 이거나, 기다려야 함
    if x < t:
        # 가는 길에 도착했을 때 물건이 안 나옴
        # t까지 기다렸다가 다시 출발해야 하므로 추가 시간 필요
        wait = t - x
        max_wait = max(max_wait, wait)

print(base_time + max_wait)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 31964: 반품 회수
// 그리디 문제
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        long[] X = new long[n];
        for (int i = 0; i < n; i++) {
            X[i] = Long.parseLong(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        long[] T = new long[n];
        for (int i = 0; i < n; i++) {
            T[i] = Long.parseLong(st.nextToken());
        }

        // 가장 먼 집의 위치
        long maxX = 0;
        for (int i = 0; i < n; i++) {
            maxX = Math.max(maxX, X[i]);
        }

        // 기본 왕복 시간
        long baseTime = 2 * maxX;

        // 추가 대기 시간 계산
        long maxWait = 0;
        for (int i = 0; i < n; i++) {
            long x = X[i], t = T[i];
            if (x < t) {
                // 가는 길에 도착했을 때 물건이 안 나옴
                long wait = t - x;
                maxWait = Math.max(maxWait, wait);
            }
        }

        System.out.println(baseTime + maxWait);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 31964: 반품 회수
// 그리디 문제
#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    long long X[n], T[n];
    for (int i = 0; i < n; i++) {
        cin >> X[i];
    }
    for (int i = 0; i < n; i++) {
        cin >> T[i];
    }

    // 가장 먼 집의 위치
    long long maxX = 0;
    for (int i = 0; i < n; i++) {
        maxX = max(maxX, X[i]);
    }

    // 기본 왕복 시간
    long long baseTime = 2 * maxX;

    // 추가 대기 시간 계산
    long long maxWait = 0;
    for (int i = 0; i < n; i++) {
        long long x = X[i], t = T[i];
        if (x < t) {
            // 가는 길에 도착했을 때 물건이 안 나옴
            long long wait = t - x;
            maxWait = max(maxWait, wait);
        }
    }

    cout << baseTime + maxWait << "\\n";
    return 0;
}
'''
        }
    ],

    # 문제 9291: 스도쿠 채점 (구현)
    "baekjoon_9291": [
        {
            "language": "python",
            "code": '''# 백준 9291: 스도쿠 채점
# 구현 문제 - 스도쿠 유효성 검사
import sys
input = sys.stdin.readline

def is_valid_sudoku(grid):
    """스도쿠가 유효한지 검사"""
    # 각 행 검사
    for row in grid:
        if len(set(row)) != 9:
            return False

    # 각 열 검사
    for col in range(9):
        column = [grid[row][col] for row in range(9)]
        if len(set(column)) != 9:
            return False

    # 각 3x3 박스 검사
    for box_row in range(3):
        for box_col in range(3):
            box = []
            for i in range(3):
                for j in range(3):
                    box.append(grid[box_row * 3 + i][box_col * 3 + j])
            if len(set(box)) != 9:
                return False

    return True

T = int(input())
for case in range(1, T + 1):
    grid = []
    for _ in range(9):
        row = list(map(int, input().split()))
        grid.append(row)

    # 테스트 케이스 사이 빈 줄 처리
    if case < T:
        try:
            input()  # 빈 줄 읽기
        except:
            pass

    result = "CORRECT" if is_valid_sudoku(grid) else "INCORRECT"
    print(f"Case {case}: {result}")
'''
        },
        {
            "language": "java",
            "code": '''// 백준 9291: 스도쿠 채점
// 구현 문제 - 스도쿠 유효성 검사
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        for (int tc = 1; tc <= T; tc++) {
            int[][] grid = new int[9][9];

            for (int i = 0; i < 9; i++) {
                StringTokenizer st = new StringTokenizer(br.readLine());
                for (int j = 0; j < 9; j++) {
                    grid[i][j] = Integer.parseInt(st.nextToken());
                }
            }

            // 테스트 케이스 사이 빈 줄 처리
            if (tc < T) {
                br.readLine();
            }

            boolean valid = isValidSudoku(grid);
            sb.append("Case ").append(tc).append(": ");
            sb.append(valid ? "CORRECT" : "INCORRECT").append("\\n");
        }

        System.out.print(sb);
    }

    static boolean isValidSudoku(int[][] grid) {
        // 각 행 검사
        for (int i = 0; i < 9; i++) {
            Set<Integer> set = new HashSet<>();
            for (int j = 0; j < 9; j++) {
                set.add(grid[i][j]);
            }
            if (set.size() != 9) return false;
        }

        // 각 열 검사
        for (int j = 0; j < 9; j++) {
            Set<Integer> set = new HashSet<>();
            for (int i = 0; i < 9; i++) {
                set.add(grid[i][j]);
            }
            if (set.size() != 9) return false;
        }

        // 각 3x3 박스 검사
        for (int boxRow = 0; boxRow < 3; boxRow++) {
            for (int boxCol = 0; boxCol < 3; boxCol++) {
                Set<Integer> set = new HashSet<>();
                for (int i = 0; i < 3; i++) {
                    for (int j = 0; j < 3; j++) {
                        set.add(grid[boxRow * 3 + i][boxCol * 3 + j]);
                    }
                }
                if (set.size() != 9) return false;
            }
        }

        return true;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 9291: 스도쿠 채점
// 구현 문제 - 스도쿠 유효성 검사
#include <iostream>
#include <set>
#include <string>
using namespace std;

int grid[9][9];

bool isValidSudoku() {
    // 각 행 검사
    for (int i = 0; i < 9; i++) {
        set<int> s;
        for (int j = 0; j < 9; j++) {
            s.insert(grid[i][j]);
        }
        if (s.size() != 9) return false;
    }

    // 각 열 검사
    for (int j = 0; j < 9; j++) {
        set<int> s;
        for (int i = 0; i < 9; i++) {
            s.insert(grid[i][j]);
        }
        if (s.size() != 9) return false;
    }

    // 각 3x3 박스 검사
    for (int boxRow = 0; boxRow < 3; boxRow++) {
        for (int boxCol = 0; boxCol < 3; boxCol++) {
            set<int> s;
            for (int i = 0; i < 3; i++) {
                for (int j = 0; j < 3; j++) {
                    s.insert(grid[boxRow * 3 + i][boxCol * 3 + j]);
                }
            }
            if (s.size() != 9) return false;
        }
    }

    return true;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T;
    cin >> T;

    for (int tc = 1; tc <= T; tc++) {
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                cin >> grid[i][j];
            }
        }

        bool valid = isValidSudoku();
        cout << "Case " << tc << ": " << (valid ? "CORRECT" : "INCORRECT") << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # 문제 9421: 소수상근수 (에라토스테네스의 체 + 상근수 판정)
    "baekjoon_9421": [
        {
            "language": "python",
            "code": '''# 백준 9421: 소수상근수
# 에라토스테네스의 체 + 상근수 판정
import sys

def sieve(n):
    """에라토스테네스의 체로 소수 찾기"""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

def is_happy(n):
    """상근수(행복수) 판정"""
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))
    return n == 1

n = int(input())

# 소수 찾기
primes = sieve(n)

# 소수상근수 찾기
result = [p for p in primes if is_happy(p)]

# 출력
for num in result:
    print(num)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 9421: 소수상근수
// 에라토스테네스의 체 + 상근수 판정
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine().trim());

        // 에라토스테네스의 체
        boolean[] isPrime = new boolean[n + 1];
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;

        for (int i = 2; i * i <= n; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j <= n; j += i) {
                    isPrime[j] = false;
                }
            }
        }

        // 소수상근수 찾기
        for (int i = 2; i <= n; i++) {
            if (isPrime[i] && isHappy(i)) {
                sb.append(i).append("\\n");
            }
        }

        System.out.print(sb);
    }

    // 상근수(행복수) 판정
    static boolean isHappy(int num) {
        Set<Integer> seen = new HashSet<>();
        while (num != 1 && !seen.contains(num)) {
            seen.add(num);
            int sum = 0;
            while (num > 0) {
                int d = num % 10;
                sum += d * d;
                num /= 10;
            }
            num = sum;
        }
        return num == 1;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 9421: 소수상근수
// 에라토스테네스의 체 + 상근수 판정
#include <iostream>
#include <vector>
#include <set>
using namespace std;

// 상근수(행복수) 판정
bool isHappy(int num) {
    set<int> seen;
    while (num != 1 && seen.find(num) == seen.end()) {
        seen.insert(num);
        int sum = 0;
        while (num > 0) {
            int d = num % 10;
            sum += d * d;
            num /= 10;
        }
        num = sum;
    }
    return num == 1;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    // 에라토스테네스의 체
    vector<bool> isPrime(n + 1, true);
    isPrime[0] = isPrime[1] = false;

    for (int i = 2; i * i <= n; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j <= n; j += i) {
                isPrime[j] = false;
            }
        }
    }

    // 소수상근수 출력
    for (int i = 2; i <= n; i++) {
        if (isPrime[i] && isHappy(i)) {
            cout << i << "\\n";
        }
    }

    return 0;
}
'''
        }
    ],

    # 문제 30445: 행복 점수 (문자열, 구현)
    "baekjoon_30445": [
        {
            "language": "python",
            "code": '''# 백준 30445: 행복 점수
# 문자열 처리 문제
# HAPPY에 있는 글자: H, A, P, Y (행복한 글자)
# SAD에 있는 글자: S, A, D (우울한 글자)

message = input().strip()

happy_chars = set('HAPPY')  # H, A, P, Y
sad_chars = set('SAD')  # S, A, D

ph = 0  # 행복 점수
pg = 0  # 우울 점수

for c in message:
    upper_c = c.upper()
    if upper_c in happy_chars:
        ph += 1
    if upper_c in sad_chars:
        pg += 1

# 행복 지수 계산
if ph == 0 and pg == 0:
    h = 0.5
else:
    h = ph / (ph + pg)

# 백분율로 변환하여 출력 (소수점 둘째 자리까지)
print(f"{h * 100:.2f}")
'''
        },
        {
            "language": "java",
            "code": '''// 백준 30445: 행복 점수
// 문자열 처리 문제
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String message = br.readLine();

        Set<Character> happyChars = new HashSet<>(Arrays.asList('H', 'A', 'P', 'Y'));
        Set<Character> sadChars = new HashSet<>(Arrays.asList('S', 'A', 'D'));

        int ph = 0;  // 행복 점수
        int pg = 0;  // 우울 점수

        for (char c : message.toCharArray()) {
            char upperC = Character.toUpperCase(c);
            if (happyChars.contains(upperC)) {
                ph++;
            }
            if (sadChars.contains(upperC)) {
                pg++;
            }
        }

        // 행복 지수 계산
        double h;
        if (ph == 0 && pg == 0) {
            h = 0.5;
        } else {
            h = (double) ph / (ph + pg);
        }

        // 백분율로 변환하여 출력
        System.out.printf("%.2f%n", h * 100);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 30445: 행복 점수
// 문자열 처리 문제
#include <iostream>
#include <string>
#include <set>
#include <iomanip>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string message;
    getline(cin, message);

    set<char> happyChars = {'H', 'A', 'P', 'Y'};
    set<char> sadChars = {'S', 'A', 'D'};

    int ph = 0;  // 행복 점수
    int pg = 0;  // 우울 점수

    for (char c : message) {
        char upperC = toupper(c);
        if (happyChars.count(upperC)) {
            ph++;
        }
        if (sadChars.count(upperC)) {
            pg++;
        }
    }

    // 행복 지수 계산
    double h;
    if (ph == 0 && pg == 0) {
        h = 0.5;
    } else {
        h = (double) ph / (ph + pg);
    }

    // 백분율로 변환하여 출력
    cout << fixed << setprecision(2) << h * 100 << "\\n";
    return 0;
}
'''
        }
    ],

    # 문제 31287: 장난감 강아지 (시뮬레이션)
    "baekjoon_31287": [
        {
            "language": "python",
            "code": '''# 백준 31287: 장난감 강아지
# 시뮬레이션 문제
# S를 K번 반복한 문자열 T를 따라 이동하며 원점 재방문 확인
import sys
input = sys.stdin.readline

N, K = map(int, input().split())
S = input().strip()

# 방향 매핑
dx = {'U': 0, 'D': 0, 'L': -1, 'R': 1}
dy = {'U': 1, 'D': -1, 'L': 0, 'R': 0}

# S를 한 번 실행했을 때의 좌표 변화량
total_dx = sum(dx[c] for c in S)
total_dy = sum(dy[c] for c in S)

# S를 한 번 실행하면서 원점 방문 확인
x, y = 0, 0
visited_first = False
for c in S:
    x += dx[c]
    y += dy[c]
    if x == 0 and y == 0:
        visited_first = True
        break

if visited_first:
    print("YES")
elif total_dx == 0 and total_dy == 0:
    # S를 한 번 실행하면 원점으로 돌아옴
    # 따라서 K >= 2이면 S를 2번 실행해도 원점 방문 가능
    print("YES")
else:
    # S를 두 번 실행하면서 원점 방문 확인 (K >= 2인 경우)
    if K >= 2:
        # 두 번째 S 실행
        for c in S:
            x += dx[c]
            y += dy[c]
            if x == 0 and y == 0:
                visited_first = True
                break

    if visited_first:
        print("YES")
    else:
        print("NO")
'''
        },
        {
            "language": "java",
            "code": '''// 백준 31287: 장난감 강아지
// 시뮬레이션 문제
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());
        String S = br.readLine().trim();

        // S를 한 번 실행하면서 원점 방문 확인
        int x = 0, y = 0;
        boolean visited = false;

        for (char c : S.toCharArray()) {
            if (c == 'U') y++;
            else if (c == 'D') y--;
            else if (c == 'L') x--;
            else if (c == 'R') x++;

            if (x == 0 && y == 0) {
                visited = true;
                break;
            }
        }

        if (visited) {
            System.out.println("YES");
            return;
        }

        // S를 한 번 실행 후 위치
        int totalDx = x;
        int totalDy = y;

        if (totalDx == 0 && totalDy == 0) {
            // S를 한 번 실행하면 원점으로 돌아옴
            System.out.println("YES");
            return;
        }

        // S를 두 번째 실행하면서 원점 방문 확인
        if (K >= 2) {
            for (char c : S.toCharArray()) {
                if (c == 'U') y++;
                else if (c == 'D') y--;
                else if (c == 'L') x--;
                else if (c == 'R') x++;

                if (x == 0 && y == 0) {
                    visited = true;
                    break;
                }
            }
        }

        System.out.println(visited ? "YES" : "NO");
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 31287: 장난감 강아지
// 시뮬레이션 문제
#include <iostream>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, K;
    string S;
    cin >> N >> K >> S;

    // S를 한 번 실행하면서 원점 방문 확인
    int x = 0, y = 0;
    bool visited = false;

    for (char c : S) {
        if (c == 'U') y++;
        else if (c == 'D') y--;
        else if (c == 'L') x--;
        else if (c == 'R') x++;

        if (x == 0 && y == 0) {
            visited = true;
            break;
        }
    }

    if (visited) {
        cout << "YES\\n";
        return 0;
    }

    // S를 한 번 실행 후 위치
    int totalDx = x;
    int totalDy = y;

    if (totalDx == 0 && totalDy == 0) {
        // S를 한 번 실행하면 원점으로 돌아옴
        cout << "YES\\n";
        return 0;
    }

    // S를 두 번째 실행하면서 원점 방문 확인
    if (K >= 2) {
        for (char c : S) {
            if (c == 'U') y++;
            else if (c == 'D') y--;
            else if (c == 'L') x--;
            else if (c == 'R') x++;

            if (x == 0 && y == 0) {
                visited = true;
                break;
            }
        }
    }

    cout << (visited ? "YES" : "NO") << "\\n";
    return 0;
}
'''
        }
    ],

    # 문제 22351: 수학은 체육과목 입니다 3 (문자열, 브루트포스)
    "baekjoon_22351": [
        {
            "language": "python",
            "code": '''# 백준 22351: 수학은 체육과목 입니다 3
# 문자열 브루트포스 문제
# A부터 B까지 이어 붙인 문자열이 입력과 일치하는지 확인

S = input().strip()

def check(a, b):
    """a부터 b까지 이어붙인 문자열이 S와 일치하는지 확인"""
    result = ''.join(str(i) for i in range(a, b + 1))
    return result == S

# A는 1~999, B는 A~999
result = None
for a in range(1, 1000):
    # a로 시작하는 문자열인지 먼저 확인
    if not S.startswith(str(a)):
        continue

    # a부터 시작해서 b까지 이어붙여보기
    current = str(a)
    b = a
    while len(current) < len(S) and b < 999:
        b += 1
        current += str(b)

    if current == S:
        if result is None or a < result[0]:
            result = (a, b)

if result:
    print(result[0], result[1])
'''
        },
        {
            "language": "java",
            "code": '''// 백준 22351: 수학은 체육과목 입니다 3
// 문자열 브루트포스 문제
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String S = br.readLine().trim();

        int resultA = -1, resultB = -1;

        // A는 1~999
        for (int a = 1; a <= 999; a++) {
            String aStr = String.valueOf(a);

            // S가 a로 시작하는지 확인
            if (!S.startsWith(aStr)) {
                continue;
            }

            // a부터 시작해서 b까지 이어붙여보기
            StringBuilder current = new StringBuilder(aStr);
            int b = a;

            while (current.length() < S.length() && b < 999) {
                b++;
                current.append(b);
            }

            if (current.toString().equals(S)) {
                if (resultA == -1 || a < resultA) {
                    resultA = a;
                    resultB = b;
                }
            }
        }

        System.out.println(resultA + " " + resultB);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 22351: 수학은 체육과목 입니다 3
// 문자열 브루트포스 문제
#include <iostream>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string S;
    cin >> S;

    int resultA = -1, resultB = -1;

    // A는 1~999
    for (int a = 1; a <= 999; a++) {
        string aStr = to_string(a);

        // S가 a로 시작하는지 확인
        if (S.substr(0, aStr.length()) != aStr) {
            continue;
        }

        // a부터 시작해서 b까지 이어붙여보기
        string current = aStr;
        int b = a;

        while (current.length() < S.length() && b < 999) {
            b++;
            current += to_string(b);
        }

        if (current == S) {
            if (resultA == -1 || a < resultA) {
                resultA = a;
                resultB = b;
            }
        }
    }

    cout << resultA << " " << resultB << "\\n";
    return 0;
}
'''
        }
    ],
}

def main():
    # JSON 파일 읽기 (파일 잠금 사용)
    with open(JSON_PATH, 'r+', encoding='utf-8') as f:
        # 배타적 파일 잠금 획득
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

        try:
            data = json.load(f)

            updated_count = 0
            for problem in data:
                problem_id = problem.get('id')

                # 빈 solutions 배열인 경우에만 처리
                if problem_id in SOLUTIONS:
                    if not problem.get('solutions') or len(problem.get('solutions', [])) == 0:
                        problem['solutions'] = SOLUTIONS[problem_id]
                        updated_count += 1
                        print(f"Updated: {problem_id}")
                    else:
                        print(f"Skipped (already has solutions): {problem_id}")

            # 파일 처음으로 이동하고 내용 덮어쓰기
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()

            print(f"\nTotal updated: {updated_count} problems")

        finally:
            # 파일 잠금 해제
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

if __name__ == '__main__':
    main()
