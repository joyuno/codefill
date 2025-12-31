#!/usr/bin/env python3
"""
41-60번째 빈 솔루션 medium 문제들에 대한 솔루션 추가 스크립트
"""

import json
import fcntl
import os

# 파일 경로
FILE_PATH = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

# 솔루션 정의
SOLUTIONS = {
    # 인덱스 3655: 셔틀런 (13268)
    3655: [
        {
            "language": "python",
            "code": '''# 셔틀런 문제
# 시작점에서 각 콘까지 왕복하는 거리를 계산하여 쓰러진 구간 찾기

d = int(input())

# 한 세트에서 각 콘까지의 왕복 거리
# 1번 콘: 5m 왕복 = 10m
# 2번 콘: 10m 왕복 = 20m
# 3번 콘: 15m 왕복 = 30m
# 4번 콘: 20m 왕복 = 40m
# 한 세트 총 거리: 10 + 20 + 30 + 40 = 100m

# 한 세트 내에서 구간별 누적 거리
# 시작->콘1: 5m, 콘1->시작: 10m
# 시작->콘2: 20m, 콘2->시작: 30m (누적)
# 시작->콘3: 45m, 콘3->시작: 60m (누적)
# 시작->콘4: 80m, 콘4->시작: 100m (누적)

# 한 세트 내 위치로 변환
d_in_set = d % 100
if d_in_set == 0:
    d_in_set = 100

# 구간 판별
# 구간 0: 시작점 (0m 위치)
# 구간 1: 0 < x <= 5 (시작->콘1)
# 구간 2: 5 < x <= 10 (콘1->시작) 또는 10 < x <= 15 (시작->콘2의 첫번째 5m) ...
# 더 정확히: 각 구간의 범위를 계산

# 구간별 누적 거리 경계
# 구간1: 1~5 (시작->콘1)
# 구간2: 6~10 (콘1->시작)
# 구간3: 11~20 (시작->콘2)
# 구간4: 21~30 (콘2->시작)
# 구간5: 31~45 (시작->콘3)
# 구간6: 46~60 (콘3->시작)
# 구간7: 61~80 (시작->콘4)
# 구간8: 81~100 (콘4->시작, 끝나면 다시 0)

boundaries = [0, 5, 10, 20, 30, 45, 60, 80, 100]
zone = 0
for i in range(1, len(boundaries)):
    if boundaries[i-1] < d_in_set <= boundaries[i]:
        zone = i
        break

print(zone)
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int d;
    cin >> d;

    // 한 세트 내 위치로 변환 (한 세트 = 100m)
    int d_in_set = d % 100;
    if (d_in_set == 0) d_in_set = 100;

    // 구간별 누적 거리 경계
    // 구간1: 1~5, 구간2: 6~10, 구간3: 11~20, 구간4: 21~30
    // 구간5: 31~45, 구간6: 46~60, 구간7: 61~80, 구간8: 81~100
    int boundaries[] = {0, 5, 10, 20, 30, 45, 60, 80, 100};

    int zone = 0;
    for (int i = 1; i <= 8; i++) {
        if (boundaries[i-1] < d_in_set && d_in_set <= boundaries[i]) {
            zone = i;
            break;
        }
    }

    cout << zone << endl;

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int d = sc.nextInt();

        // 한 세트 내 위치로 변환 (한 세트 = 100m)
        int dInSet = d % 100;
        if (dInSet == 0) dInSet = 100;

        // 구간별 누적 거리 경계
        int[] boundaries = {0, 5, 10, 20, 30, 45, 60, 80, 100};

        int zone = 0;
        for (int i = 1; i <= 8; i++) {
            if (boundaries[i-1] < dInSet && dInSet <= boundaries[i]) {
                zone = i;
                break;
            }
        }

        System.out.println(zone);
    }
}
'''
        }
    ],

    # 인덱스 3658: 알래스카 (4159)
    3658: [
        {
            "language": "python",
            "code": '''# 알래스카 문제
# 충전소 간 거리가 200km 이하면 도달 가능

import sys
input = sys.stdin.readline

while True:
    n = int(input())
    if n == 0:
        break

    # 충전소 위치 입력
    stations = []
    for _ in range(n):
        stations.append(int(input()))

    # 시작점 0과 끝점 1422 추가 후 정렬
    stations.append(0)
    stations.append(1422)
    stations.sort()

    # 인접 충전소 간 거리가 모두 200km 이하인지 확인
    possible = True
    for i in range(1, len(stations)):
        if stations[i] - stations[i-1] > 200:
            possible = False
            break

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
        vector<int> stations;
        stations.push_back(0);      // 시작점
        stations.push_back(1422);   // 끝점

        for (int i = 0; i < n; i++) {
            int pos;
            cin >> pos;
            stations.push_back(pos);
        }

        sort(stations.begin(), stations.end());

        bool possible = true;
        for (int i = 1; i < stations.size(); i++) {
            if (stations[i] - stations[i-1] > 200) {
                possible = false;
                break;
            }
        }

        cout << (possible ? "POSSIBLE" : "IMPOSSIBLE") << "\\n";
    }

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        while (true) {
            int n = Integer.parseInt(br.readLine().trim());
            if (n == 0) break;

            List<Integer> stations = new ArrayList<>();
            stations.add(0);      // 시작점
            stations.add(1422);   // 끝점

            for (int i = 0; i < n; i++) {
                stations.add(Integer.parseInt(br.readLine().trim()));
            }

            Collections.sort(stations);

            boolean possible = true;
            for (int i = 1; i < stations.size(); i++) {
                if (stations.get(i) - stations.get(i-1) > 200) {
                    possible = false;
                    break;
                }
            }

            sb.append(possible ? "POSSIBLE" : "IMPOSSIBLE").append("\\n");
        }

        System.out.print(sb);
    }
}
'''
        }
    ],

    # 인덱스 3663: 서로소 쌍 (13412)
    3663: [
        {
            "language": "python",
            "code": '''# 서로소 쌍 문제
# n = a*b이고 gcd(a,b) = 1인 쌍의 개수 = 2^(n의 서로 다른 소인수 개수)

import sys
input = sys.stdin.readline

def count_distinct_prime_factors(n):
    """n의 서로 다른 소인수 개수 반환"""
    count = 0
    d = 2
    while d * d <= n:
        if n % d == 0:
            count += 1
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        count += 1
    return count

T = int(input())
for _ in range(T):
    n = int(input())
    k = count_distinct_prime_factors(n)
    # 서로소인 쌍 (a, b)의 개수 = 2^k
    print(1 << k)
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

// n의 서로 다른 소인수 개수 반환
int countDistinctPrimeFactors(long long n) {
    int count = 0;
    for (long long d = 2; d * d <= n; d++) {
        if (n % d == 0) {
            count++;
            while (n % d == 0) {
                n /= d;
            }
        }
    }
    if (n > 1) count++;
    return count;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        long long n;
        cin >> n;
        int k = countDistinctPrimeFactors(n);
        // 서로소인 쌍의 개수 = 2^k
        cout << (1 << k) << "\\n";
    }

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    // n의 서로 다른 소인수 개수 반환
    static int countDistinctPrimeFactors(long n) {
        int count = 0;
        for (long d = 2; d * d <= n; d++) {
            if (n % d == 0) {
                count++;
                while (n % d == 0) {
                    n /= d;
                }
            }
        }
        if (n > 1) count++;
        return count;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            long n = Long.parseLong(br.readLine().trim());
            int k = countDistinctPrimeFactors(n);
            // 서로소인 쌍의 개수 = 2^k
            sb.append(1 << k).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
        }
    ],

    # 인덱스 3670: 카드놀이 (3231)
    3670: [
        {
            "language": "python",
            "code": '''# 카드놀이 문제
# 카드를 정렬하기 위해 필요한 최소 패스 횟수
# = 가장 긴 증가하는 부분 수열의 길이를 N에서 빼기

import sys
input = sys.stdin.readline

n = int(input())
cards = []
for _ in range(n):
    cards.append(int(input()))

# 가장 긴 연속 증가 부분 수열 (1,2,3,... 형태) 찾기
# 1부터 시작하여 연속으로 올바른 순서인 카드 개수
longest = 0
current = 0

for i in range(n):
    # cards[i]가 current+1이면 연속
    if cards[i] == current + 1:
        current += 1
        longest = max(longest, current)
    elif cards[i] == 1:
        current = 1
        longest = max(longest, current)

# 필요한 패스 횟수 = 전체 카드 수 - 이미 정렬된 연속 카드 수
print(n - longest)
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

    int cards[n];
    for (int i = 0; i < n; i++) {
        cin >> cards[i];
    }

    // 가장 긴 연속 증가 부분 수열 찾기
    int longest = 0;
    int current = 0;

    for (int i = 0; i < n; i++) {
        if (cards[i] == current + 1) {
            current++;
            longest = max(longest, current);
        } else if (cards[i] == 1) {
            current = 1;
            longest = max(longest, current);
        }
    }

    // 필요한 패스 횟수
    cout << n - longest << endl;

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        int[] cards = new int[n];

        for (int i = 0; i < n; i++) {
            cards[i] = Integer.parseInt(br.readLine().trim());
        }

        // 가장 긴 연속 증가 부분 수열 찾기
        int longest = 0;
        int current = 0;

        for (int i = 0; i < n; i++) {
            if (cards[i] == current + 1) {
                current++;
                longest = Math.max(longest, current);
            } else if (cards[i] == 1) {
                current = 1;
                longest = Math.max(longest, current);
            }
        }

        // 필요한 패스 횟수
        System.out.println(n - longest);
    }
}
'''
        }
    ],

    # 인덱스 3674: exceed or not (15707)
    3674: [
        {
            "language": "python",
            "code": '''# exceed or not 문제
# A*B + C가 오버플로우(9 * 10^18 초과)인지 확인

import sys
input = sys.stdin.readline

A, B, C = map(int, input().split())

LIMIT = 9 * 10**18

# A*B 계산 시 오버플로우 체크
if A == 0 or B == 0:
    result = C
    if result > LIMIT:
        print("overflow")
    else:
        print(result)
else:
    # A*B가 LIMIT보다 큰지 확인
    if A > LIMIT // B:
        print("overflow")
    else:
        product = A * B
        result = product + C
        if result > LIMIT:
            print("overflow")
        else:
            print(result)
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    unsigned long long A, B, C;
    cin >> A >> B >> C;

    const unsigned long long LIMIT = 9000000000000000000ULL;

    // A*B 계산 시 오버플로우 체크
    if (A == 0 || B == 0) {
        if (C > LIMIT) {
            cout << "overflow" << endl;
        } else {
            cout << C << endl;
        }
    } else {
        // A*B가 LIMIT보다 큰지 확인
        if (A > LIMIT / B) {
            cout << "overflow" << endl;
        } else {
            unsigned long long product = A * B;
            // product + C 오버플로우 체크
            if (product > LIMIT - C) {
                cout << "overflow" << endl;
            } else {
                cout << product + C << endl;
            }
        }
    }

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.math.BigInteger;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        BigInteger A = new BigInteger(sc.next());
        BigInteger B = new BigInteger(sc.next());
        BigInteger C = new BigInteger(sc.next());

        BigInteger LIMIT = new BigInteger("9000000000000000000");

        BigInteger result = A.multiply(B).add(C);

        if (result.compareTo(LIMIT) > 0) {
            System.out.println("overflow");
        } else {
            System.out.println(result);
        }
    }
}
'''
        }
    ],

    # 인덱스 3676: 200% Mixed Juice! (25312)
    3676: [
        {
            "language": "python",
            "code": '''# 200% Mixed Juice! 문제
# N개의 주스 중 L리터를 최소 비용으로 구매

import sys
from math import gcd
input = sys.stdin.readline

N, L = map(int, input().split())

# (가격/용량) 비율로 정렬하기 위해 (가격, 용량) 저장
juices = []
for _ in range(N):
    v, c = map(int, input().split())  # 용량, 가격
    juices.append((c, v))  # (가격, 용량)

# 리터당 가격 기준 정렬 (c/v 오름차순)
juices.sort(key=lambda x: x[0] / x[1])

total_cost = 0
remaining = L

for cost, volume in juices:
    if remaining <= 0:
        break

    # 이 주스로 채울 양
    use = min(remaining, volume)
    total_cost += cost * use
    remaining -= use

# 기약분수로 출력
# total_cost / L
g = gcd(total_cost, L)
numerator = total_cost // g
denominator = L // g

if denominator == 1:
    print(numerator)
else:
    print(f"{numerator}/{denominator}")
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

    long long N, L;
    cin >> N >> L;

    vector<pair<long long, long long>> juices(N);  // (가격, 용량)

    for (int i = 0; i < N; i++) {
        long long v, c;
        cin >> v >> c;  // 용량, 가격
        juices[i] = {c, v};
    }

    // 리터당 가격 기준 정렬
    sort(juices.begin(), juices.end(), [](const auto& a, const auto& b) {
        return a.first * b.second < b.first * a.second;
    });

    long long totalCost = 0;
    long long remaining = L;

    for (auto& [cost, volume] : juices) {
        if (remaining <= 0) break;

        long long use = min(remaining, volume);
        totalCost += cost * use;
        remaining -= use;
    }

    // 기약분수로 출력
    long long g = gcd(totalCost, L);
    long long numerator = totalCost / g;
    long long denominator = L / g;

    if (denominator == 1) {
        cout << numerator << endl;
    } else {
        cout << numerator << "/" << denominator << endl;
    }

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

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

        int N = Integer.parseInt(st.nextToken());
        long L = Long.parseLong(st.nextToken());

        long[][] juices = new long[N][2];  // [가격, 용량]

        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            long v = Long.parseLong(st.nextToken());  // 용량
            long c = Long.parseLong(st.nextToken());  // 가격
            juices[i][0] = c;
            juices[i][1] = v;
        }

        // 리터당 가격 기준 정렬
        Arrays.sort(juices, (a, b) -> Long.compare(a[0] * b[1], b[0] * a[1]));

        long totalCost = 0;
        long remaining = L;

        for (int i = 0; i < N && remaining > 0; i++) {
            long cost = juices[i][0];
            long volume = juices[i][1];

            long use = Math.min(remaining, volume);
            totalCost += cost * use;
            remaining -= use;
        }

        // 기약분수로 출력
        long g = gcd(totalCost, L);
        long numerator = totalCost / g;
        long denominator = L / g;

        if (denominator == 1) {
            System.out.println(numerator);
        } else {
            System.out.println(numerator + "/" + denominator);
        }
    }
}
'''
        }
    ],

    # 인덱스 3683: 악마 게임 (16677)
    3683: [
        {
            "language": "python",
            "code": '''# 악마 게임 문제
# 주어진 단어로 시작하고 점수가 666 이상인 닉네임 찾기

import sys
input = sys.stdin.readline

word = input().strip()
n = int(input())

result = None
min_score = float('inf')

for _ in range(n):
    line = input().strip().split()
    nickname = line[0]
    score = int(line[1])

    # 닉네임이 word로 시작하는지 확인
    if nickname.startswith(word) and score >= 666:
        if score < min_score:
            min_score = score
            result = nickname

if result:
    print(result)
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

    string word;
    cin >> word;

    int n;
    cin >> n;

    string result = "";
    int minScore = 1e9;

    for (int i = 0; i < n; i++) {
        string nickname;
        int score;
        cin >> nickname >> score;

        // 닉네임이 word로 시작하는지 확인
        if (nickname.length() >= word.length() &&
            nickname.substr(0, word.length()) == word &&
            score >= 666) {
            if (score < minScore) {
                minScore = score;
                result = nickname;
            }
        }
    }

    if (result != "") {
        cout << result << endl;
    } else {
        cout << "No Jam" << endl;
    }

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        String word = br.readLine().trim();
        int n = Integer.parseInt(br.readLine().trim());

        String result = null;
        int minScore = Integer.MAX_VALUE;

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            String nickname = st.nextToken();
            int score = Integer.parseInt(st.nextToken());

            // 닉네임이 word로 시작하는지 확인
            if (nickname.startsWith(word) && score >= 666) {
                if (score < minScore) {
                    minScore = score;
                    result = nickname;
                }
            }
        }

        if (result != null) {
            System.out.println(result);
        } else {
            System.out.println("No Jam");
        }
    }
}
'''
        }
    ],

    # 인덱스 3690: 건공문자열 (30823)
    3690: [
        {
            "language": "python",
            "code": '''# 건공문자열 문제
# N개의 문자열을 K만큼 회전

import sys
input = sys.stdin.readline

N, K = map(int, input().split())
s = input().strip()

# K만큼 왼쪽으로 회전
K = K % N
result = s[K:] + s[:K]

print(result)
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

    int N, K;
    cin >> N >> K;

    string s;
    cin >> s;

    // K만큼 왼쪽으로 회전
    K = K % N;
    string result = s.substr(K) + s.substr(0, K);

    cout << result << endl;

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        String s = br.readLine().trim();

        // K만큼 왼쪽으로 회전
        K = K % N;
        String result = s.substring(K) + s.substring(0, K);

        System.out.println(result);
    }
}
'''
        }
    ],

    # 인덱스 3694: Social Distancing II (18881)
    3694: [
        {
            "language": "python",
            "code": '''# Social Distancing II 문제
# 감염된 소가 처음에 몇 마리였는지 최소값 구하기

import sys
input = sys.stdin.readline

N = int(input())

cows = []
for _ in range(N):
    x, s = map(int, input().split())
    cows.append((x, s))

# 위치 기준 정렬
cows.sort()

# 감염된 소들 사이의 최소 거리 찾기
min_sick_dist = float('inf')
prev_sick_pos = None

for x, s in cows:
    if s == 1:  # 감염된 소
        if prev_sick_pos is not None:
            min_sick_dist = min(min_sick_dist, x - prev_sick_pos)
        prev_sick_pos = x

# 감염된 소가 1마리 이하면 1 출력
sick_count = sum(1 for _, s in cows if s == 1)
if sick_count <= 1:
    print(sick_count)
else:
    # 연속된 감염 그룹 세기
    # 감염된 소들 사이 거리가 min_sick_dist 이하면 같은 그룹
    groups = 0
    prev_sick_pos = None

    for x, s in cows:
        if s == 1:
            if prev_sick_pos is None or x - prev_sick_pos > min_sick_dist:
                groups += 1
            prev_sick_pos = x

    print(groups)
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

    vector<pair<int, int>> cows(N);

    for (int i = 0; i < N; i++) {
        cin >> cows[i].first >> cows[i].second;
    }

    // 위치 기준 정렬
    sort(cows.begin(), cows.end());

    // 감염된 소들 사이의 최소 거리 찾기
    int minSickDist = 1e9;
    int prevSickPos = -1e9;
    int sickCount = 0;

    for (auto& [x, s] : cows) {
        if (s == 1) {
            sickCount++;
            if (prevSickPos > -1e9) {
                minSickDist = min(minSickDist, x - prevSickPos);
            }
            prevSickPos = x;
        }
    }

    if (sickCount <= 1) {
        cout << sickCount << endl;
    } else {
        // 연속된 감염 그룹 세기
        int groups = 0;
        prevSickPos = -1e9;

        for (auto& [x, s] : cows) {
            if (s == 1) {
                if (prevSickPos < -1e9 + 1 || x - prevSickPos > minSickDist) {
                    groups++;
                }
                prevSickPos = x;
            }
        }

        cout << groups << endl;
    }

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());

        int[][] cows = new int[N][2];

        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            cows[i][0] = Integer.parseInt(st.nextToken());
            cows[i][1] = Integer.parseInt(st.nextToken());
        }

        // 위치 기준 정렬
        Arrays.sort(cows, (a, b) -> a[0] - b[0]);

        // 감염된 소들 사이의 최소 거리 찾기
        int minSickDist = Integer.MAX_VALUE;
        int prevSickPos = Integer.MIN_VALUE;
        int sickCount = 0;

        for (int i = 0; i < N; i++) {
            if (cows[i][1] == 1) {
                sickCount++;
                if (prevSickPos > Integer.MIN_VALUE) {
                    minSickDist = Math.min(minSickDist, cows[i][0] - prevSickPos);
                }
                prevSickPos = cows[i][0];
            }
        }

        if (sickCount <= 1) {
            System.out.println(sickCount);
        } else {
            // 연속된 감염 그룹 세기
            int groups = 0;
            prevSickPos = Integer.MIN_VALUE;

            for (int i = 0; i < N; i++) {
                if (cows[i][1] == 1) {
                    if (prevSickPos == Integer.MIN_VALUE || cows[i][0] - prevSickPos > minSickDist) {
                        groups++;
                    }
                    prevSickPos = cows[i][0];
                }
            }

            System.out.println(groups);
        }
    }
}
'''
        }
    ],

    # 인덱스 3746: 더 흔한 타일 색칠 문제 (28298)
    3746: [
        {
            "language": "python",
            "code": '''# 더 흔한 타일 색칠 문제
# K*K 패턴을 반복하여 최소 변경으로 타일 색칠

import sys
from collections import Counter
input = sys.stdin.readline

N, M, K = map(int, input().split())

grid = []
for _ in range(N):
    grid.append(input().strip())

# 각 (i%K, j%K) 위치별로 가장 많이 나오는 문자 찾기
pattern_counts = [[Counter() for _ in range(K)] for _ in range(K)]

for i in range(N):
    for j in range(M):
        pattern_counts[i % K][j % K][grid[i][j]] += 1

# 각 패턴 위치에서 가장 많이 나오는 문자 선택
pattern = [['' for _ in range(K)] for _ in range(K)]
total_changes = 0

for i in range(K):
    for j in range(K):
        if pattern_counts[i][j]:
            most_common = pattern_counts[i][j].most_common(1)[0]
            pattern[i][j] = most_common[0]
            # 변경 횟수 = 전체 개수 - 가장 많은 문자 개수
            total_in_pos = sum(pattern_counts[i][j].values())
            total_changes += total_in_pos - most_common[1]
        else:
            pattern[i][j] = 'A'

print(total_changes)

# 결과 그리드 출력
for i in range(N):
    row = ""
    for j in range(M):
        row += pattern[i % K][j % K]
    print(row)
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

    int N, M, K;
    cin >> N >> M >> K;

    string grid[N];
    for (int i = 0; i < N; i++) {
        cin >> grid[i];
    }

    // 각 (i%K, j%K) 위치별로 문자 카운트
    map<char, int> patternCounts[K][K];

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            patternCounts[i % K][j % K][grid[i][j]]++;
        }
    }

    // 각 패턴 위치에서 가장 많이 나오는 문자 선택
    char pattern[K][K];
    int totalChanges = 0;

    for (int i = 0; i < K; i++) {
        for (int j = 0; j < K; j++) {
            char bestChar = 'A';
            int maxCount = 0;
            int totalInPos = 0;

            for (auto& [ch, cnt] : patternCounts[i][j]) {
                totalInPos += cnt;
                if (cnt > maxCount) {
                    maxCount = cnt;
                    bestChar = ch;
                }
            }

            pattern[i][j] = bestChar;
            totalChanges += totalInPos - maxCount;
        }
    }

    cout << totalChanges << "\\n";

    // 결과 그리드 출력
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            cout << pattern[i % K][j % K];
        }
        cout << "\\n";
    }

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        String[] grid = new String[N];
        for (int i = 0; i < N; i++) {
            grid[i] = br.readLine();
        }

        // 각 (i%K, j%K) 위치별로 문자 카운트
        Map<Character, Integer>[][] patternCounts = new HashMap[K][K];
        for (int i = 0; i < K; i++) {
            for (int j = 0; j < K; j++) {
                patternCounts[i][j] = new HashMap<>();
            }
        }

        for (int i = 0; i < N; i++) {
            for (int j = 0; j < M; j++) {
                char c = grid[i].charAt(j);
                patternCounts[i % K][j % K].merge(c, 1, Integer::sum);
            }
        }

        // 각 패턴 위치에서 가장 많이 나오는 문자 선택
        char[][] pattern = new char[K][K];
        int totalChanges = 0;

        for (int i = 0; i < K; i++) {
            for (int j = 0; j < K; j++) {
                char bestChar = 'A';
                int maxCount = 0;
                int totalInPos = 0;

                for (Map.Entry<Character, Integer> e : patternCounts[i][j].entrySet()) {
                    totalInPos += e.getValue();
                    if (e.getValue() > maxCount) {
                        maxCount = e.getValue();
                        bestChar = e.getKey();
                    }
                }

                pattern[i][j] = bestChar;
                totalChanges += totalInPos - maxCount;
            }
        }

        StringBuilder sb = new StringBuilder();
        sb.append(totalChanges).append("\\n");

        // 결과 그리드 출력
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < M; j++) {
                sb.append(pattern[i % K][j % K]);
            }
            sb.append("\\n");
        }

        System.out.print(sb);
    }
}
'''
        }
    ],

    # 인덱스 3747: 배너 걸기 (27527)
    3747: [
        {
            "language": "python",
            "code": '''# 배너 걸기 문제
# 연속된 K개의 기둥에서 최소 높이가 H 이상인지 확인

import sys
from collections import deque
input = sys.stdin.readline

N, K = map(int, input().split())
heights = list(map(int, input().split()))

# 슬라이딩 윈도우로 K개의 연속 구간에서 최소값 >= K인지 확인
# 최소값 >= K면 "YES"

# 슬라이딩 윈도우 최소값 (모노토닉 덱 사용)
dq = deque()  # (인덱스, 값)

for i in range(N):
    # 현재 원소보다 큰 원소들 제거 (최소값 유지)
    while dq and dq[-1][1] >= heights[i]:
        dq.pop()

    dq.append((i, heights[i]))

    # 윈도우 범위를 벗어난 원소 제거
    while dq[0][0] <= i - K:
        dq.popleft()

    # K개가 채워졌을 때
    if i >= K - 1:
        if dq[0][1] >= K:
            print("YES")
            sys.exit()

print("NO")
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <deque>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, K;
    cin >> N >> K;

    int heights[N];
    for (int i = 0; i < N; i++) {
        cin >> heights[i];
    }

    // 슬라이딩 윈도우 최소값 (모노토닉 덱)
    deque<pair<int, int>> dq;  // (인덱스, 값)

    for (int i = 0; i < N; i++) {
        // 현재 원소보다 큰 원소들 제거
        while (!dq.empty() && dq.back().second >= heights[i]) {
            dq.pop_back();
        }

        dq.push_back({i, heights[i]});

        // 윈도우 범위를 벗어난 원소 제거
        while (dq.front().first <= i - K) {
            dq.pop_front();
        }

        // K개가 채워졌을 때
        if (i >= K - 1) {
            if (dq.front().second >= K) {
                cout << "YES" << endl;
                return 0;
            }
        }
    }

    cout << "NO" << endl;
    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        int[] heights = new int[N];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            heights[i] = Integer.parseInt(st.nextToken());
        }

        // 슬라이딩 윈도우 최소값 (모노토닉 덱)
        Deque<int[]> dq = new ArrayDeque<>();  // {인덱스, 값}

        for (int i = 0; i < N; i++) {
            // 현재 원소보다 큰 원소들 제거
            while (!dq.isEmpty() && dq.peekLast()[1] >= heights[i]) {
                dq.pollLast();
            }

            dq.addLast(new int[]{i, heights[i]});

            // 윈도우 범위를 벗어난 원소 제거
            while (dq.peekFirst()[0] <= i - K) {
                dq.pollFirst();
            }

            // K개가 채워졌을 때
            if (i >= K - 1) {
                if (dq.peekFirst()[1] >= K) {
                    System.out.println("YES");
                    return;
                }
            }
        }

        System.out.println("NO");
    }
}
'''
        }
    ],

    # 인덱스 3769: 푸른 MEX의 아내 (28250)
    3769: [
        {
            "language": "python",
            "code": '''# 이브, 프시케 그리고 푸른 MEX의 아내 문제
# 모든 부분 구간의 MEX 합 구하기

import sys
input = sys.stdin.readline

N = int(input())
arr = list(map(int, input().split()))

# 모든 부분 구간 [l, r]에 대해 MEX 계산
total = 0

for l in range(N):
    # l부터 시작하는 구간에서 각 숫자의 존재 여부
    present = [False] * (N + 2)
    mex = 0

    for r in range(l, N):
        present[arr[r]] = True

        # MEX 업데이트
        while present[mex]:
            mex += 1

        total += mex

print(total)
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

    vector<int> arr(N);
    for (int i = 0; i < N; i++) {
        cin >> arr[i];
    }

    // 모든 부분 구간의 MEX 합
    long long total = 0;

    for (int l = 0; l < N; l++) {
        vector<bool> present(N + 2, false);
        int mex = 0;

        for (int r = l; r < N; r++) {
            present[arr[r]] = true;

            // MEX 업데이트
            while (present[mex]) {
                mex++;
            }

            total += mex;
        }
    }

    cout << total << endl;

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());
        int[] arr = new int[N];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        // 모든 부분 구간의 MEX 합
        long total = 0;

        for (int l = 0; l < N; l++) {
            boolean[] present = new boolean[N + 2];
            int mex = 0;

            for (int r = l; r < N; r++) {
                present[arr[r]] = true;

                // MEX 업데이트
                while (present[mex]) {
                    mex++;
                }

                total += mex;
            }
        }

        System.out.println(total);
    }
}
'''
        }
    ],

    # 인덱스 3773: 평면 분할 (18187)
    3773: [
        {
            "language": "python",
            "code": '''# 평면 분할 문제
# n개의 직선이 평면을 최대 몇 개의 영역으로 나누는지
# 공식: 1 + n + n*(n-1)/2 = 1 + n*(n+1)/2

n = int(input())

# n개의 직선이 일반 위치(어떤 세 직선도 한 점에서 만나지 않고, 평행한 직선이 없음)일 때
# 최대 영역 개수 = 1 + n + C(n,2) = 1 + n + n*(n-1)/2
result = 1 + n + n * (n - 1) // 2
print(result)
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n;
    cin >> n;

    // n개의 직선이 평면을 나누는 최대 영역 개수
    // = 1 + n + n*(n-1)/2
    long long result = 1 + n + n * (n - 1) / 2;

    cout << result << endl;

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
        long n = sc.nextLong();

        // n개의 직선이 평면을 나누는 최대 영역 개수
        // = 1 + n + n*(n-1)/2
        long result = 1 + n + n * (n - 1) / 2;

        System.out.println(result);
    }
}
'''
        }
    ],

    # 인덱스 3782: 오리와 박수치는 춘배 (30404)
    3782: [
        {
            "language": "python",
            "code": '''# 오리와 박수치는 춘배 문제
# N개의 시각 중 K초 간격으로 박수치는 횟수

import sys
input = sys.stdin.readline

N, K = map(int, input().split())
times = list(map(int, input().split()))

# 각 시각에 박수를 칠 수 있으면 카운트
# 첫 번째는 항상 박수
claps = 1
last_clap = times[0]

for i in range(1, N):
    if times[i] - last_clap >= K:
        claps += 1
        last_clap = times[i]

print(claps)
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, K;
    cin >> N >> K;

    int times[N];
    for (int i = 0; i < N; i++) {
        cin >> times[i];
    }

    // 첫 번째는 항상 박수
    int claps = 1;
    int lastClap = times[0];

    for (int i = 1; i < N; i++) {
        if (times[i] - lastClap >= K) {
            claps++;
            lastClap = times[i];
        }
    }

    cout << claps << endl;

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        int[] times = new int[N];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            times[i] = Integer.parseInt(st.nextToken());
        }

        // 첫 번째는 항상 박수
        int claps = 1;
        int lastClap = times[0];

        for (int i = 1; i < N; i++) {
            if (times[i] - lastClap >= K) {
                claps++;
                lastClap = times[i];
            }
        }

        System.out.println(claps);
    }
}
'''
        }
    ],

    # 인덱스 3783: 다중 일차 함수 (26258)
    3783: [
        {
            "language": "python",
            "code": '''# 다중 일차 함수 문제
# 꺾은선 그래프의 기울기 구하기

import sys
input = sys.stdin.readline

N = int(input())

points = []
for _ in range(N):
    x, y = map(int, input().split())
    points.append((x, y))

Q = int(input())

for _ in range(Q):
    t = float(input())

    # t가 어느 구간에 있는지 이진 탐색
    # 구간 [points[i].x, points[i+1].x)에 있으면 기울기 계산

    left, right = 0, N - 2
    result_slope = 0

    while left <= right:
        mid = (left + right) // 2

        if points[mid][0] <= t < points[mid + 1][0]:
            # 기울기 계산
            dx = points[mid + 1][0] - points[mid][0]
            dy = points[mid + 1][1] - points[mid][1]
            if dy > 0:
                result_slope = 1
            elif dy < 0:
                result_slope = -1
            else:
                result_slope = 0
            break
        elif t < points[mid][0]:
            right = mid - 1
        else:
            left = mid + 1

    print(result_slope)
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

    vector<pair<double, double>> points(N);
    for (int i = 0; i < N; i++) {
        cin >> points[i].first >> points[i].second;
    }

    int Q;
    cin >> Q;

    while (Q--) {
        double t;
        cin >> t;

        // 이진 탐색으로 구간 찾기
        int left = 0, right = N - 2;
        int resultSlope = 0;

        while (left <= right) {
            int mid = (left + right) / 2;

            if (points[mid].first <= t && t < points[mid + 1].first) {
                double dy = points[mid + 1].second - points[mid].second;
                if (dy > 0) resultSlope = 1;
                else if (dy < 0) resultSlope = -1;
                else resultSlope = 0;
                break;
            } else if (t < points[mid].first) {
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        }

        cout << resultSlope << "\\n";
    }

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int N = Integer.parseInt(br.readLine().trim());

        double[][] points = new double[N][2];
        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            points[i][0] = Double.parseDouble(st.nextToken());
            points[i][1] = Double.parseDouble(st.nextToken());
        }

        int Q = Integer.parseInt(br.readLine().trim());

        while (Q-- > 0) {
            double t = Double.parseDouble(br.readLine().trim());

            // 이진 탐색으로 구간 찾기
            int left = 0, right = N - 2;
            int resultSlope = 0;

            while (left <= right) {
                int mid = (left + right) / 2;

                if (points[mid][0] <= t && t < points[mid + 1][0]) {
                    double dy = points[mid + 1][1] - points[mid][1];
                    if (dy > 0) resultSlope = 1;
                    else if (dy < 0) resultSlope = -1;
                    else resultSlope = 0;
                    break;
                } else if (t < points[mid][0]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            }

            sb.append(resultSlope).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
        }
    ],

    # 인덱스 3785: 배스킨라빈스 (25179)
    3785: [
        {
            "language": "python",
            "code": '''# 배스킨라빈스~N~귀엽고~깜찍하게~ 문제
# 게임 이론: (N-1) % (M+1) != 0이면 선공 승리

import sys
input = sys.stdin.readline

N, M = map(int, input().split())

# N개의 숫자를 부를 때, 한 번에 1~M개 부를 수 있음
# N을 부르면 지는 게임
# (N-1) % (M+1) == 0이면 후공 승리, 아니면 선공 승리

if (N - 1) % (M + 1) != 0:
    print("Can win")
else:
    print("Can't win")
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long N, M;
    cin >> N >> M;

    // (N-1) % (M+1) != 0이면 선공 승리
    if ((N - 1) % (M + 1) != 0) {
        cout << "Can win" << endl;
    } else {
        cout << "Can't win" << endl;
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
        long M = sc.nextLong();

        // (N-1) % (M+1) != 0이면 선공 승리
        if ((N - 1) % (M + 1) != 0) {
            System.out.println("Can win");
        } else {
            System.out.println("Can't win");
        }
    }
}
'''
        }
    ],

    # 인덱스 3793: 이삿짐센터 (16237)
    3793: [
        {
            "language": "python",
            "code": '''# 이삿짐센터 문제
# 무게 1~5kg의 물건을 5kg 상자에 담기

import sys
input = sys.stdin.readline

a, b, c, d, e = map(int, input().split())

# 5kg 물건: 각각 1개의 상자 필요
boxes = e

# 4kg 물건: 각각 1개의 상자, 남는 1kg에 1kg 물건
boxes += d
a = max(0, a - d)  # 4kg 상자의 빈 공간에 1kg 채움

# 3kg 물건: 2개씩 묶으면 6kg -> 상자 1개에 1개씩
# 3kg 하나에 2kg 하나, 또는 3kg 하나에 1kg 두 개
# 3+2 = 5, 3+1+1 = 5

# 3kg 물건 처리
boxes += c
# 남는 공간 2kg * c개
space_for_2 = c  # 각 3kg 상자에 2kg 공간
used_2 = min(b, space_for_2)
b -= used_2
space_for_1 = (c - used_2) * 2 + used_2 * 0  # 2kg 넣으면 1kg 공간 없음
# 다시 계산: 3kg 상자에 2kg 안 넣은 경우 2kg 공간 남음
# 3kg 상자에 2kg 넣은 경우 공간 없음
remaining_space = (c - used_2) * 2  # 2kg 안 넣은 상자들의 남은 공간
a = max(0, a - remaining_space)

# 2kg 물건: 2개씩 묶으면 4kg, 1kg 공간 남음
# 2+2+1 = 5
boxes += (b + 2) // 3
leftover_2 = b % 3
if leftover_2 == 1:
    # 2kg 1개 남음, 1kg 3개 필요
    if a >= 3:
        a -= 3
    else:
        a = 0
        boxes += 1
elif leftover_2 == 2:
    # 2kg 2개 = 4kg, 1kg 1개 필요
    if a >= 1:
        a -= 1
        boxes += 1
    else:
        boxes += 1

# 1kg 물건: 5개씩 묶음
boxes += (a + 4) // 5

print(boxes)
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

    int a, b, c, d, e;
    cin >> a >> b >> c >> d >> e;

    int boxes = 0;

    // 5kg 물건
    boxes += e;

    // 4kg 물건 (+ 1kg)
    boxes += d;
    a = max(0, a - d);

    // 3kg 물건
    boxes += c;
    int space2 = c;  // 2kg 공간
    int used2 = min(b, space2);
    b -= used2;
    int space1 = (c - used2) * 2;  // 남은 1kg 공간
    a = max(0, a - space1);

    // 2kg 물건 (3개씩 묶으면 6kg, 2상자에 3개)
    // 2+2+1 패턴 활용
    boxes += b / 3;
    int left2 = b % 3;

    if (left2 == 1) {
        // 2kg 1개, 1kg 3개 필요
        boxes += 1;
        a = max(0, a - 3);
    } else if (left2 == 2) {
        // 2kg 2개, 1kg 1개 필요
        boxes += 1;
        a = max(0, a - 1);
    }

    // 1kg 물건
    boxes += (a + 4) / 5;

    cout << boxes << endl;

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
        int a = sc.nextInt();
        int b = sc.nextInt();
        int c = sc.nextInt();
        int d = sc.nextInt();
        int e = sc.nextInt();

        int boxes = 0;

        // 5kg 물건
        boxes += e;

        // 4kg 물건 (+ 1kg)
        boxes += d;
        a = Math.max(0, a - d);

        // 3kg 물건
        boxes += c;
        int space2 = c;
        int used2 = Math.min(b, space2);
        b -= used2;
        int space1 = (c - used2) * 2;
        a = Math.max(0, a - space1);

        // 2kg 물건
        boxes += b / 3;
        int left2 = b % 3;

        if (left2 == 1) {
            boxes += 1;
            a = Math.max(0, a - 3);
        } else if (left2 == 2) {
            boxes += 1;
            a = Math.max(0, a - 1);
        }

        // 1kg 물건
        boxes += (a + 4) / 5;

        System.out.println(boxes);
    }
}
'''
        }
    ],

    # 인덱스 3799: 컴포트 (3258)
    3799: [
        {
            "language": "python",
            "code": '''# 컴포트 문제
# N칸 원형 트랙에서 K만큼 점프하며 B까지 도달 (함정 피하면서)

import sys
input = sys.stdin.readline

line = input().split()
N, B, K = int(line[0]), int(line[1]), int(line[2])

traps = set()
if K > 0:
    trap_list = list(map(int, input().split()))
    traps = set(trap_list)

# 점프 크기 D를 1부터 N-1까지 시도
for D in range(1, N):
    pos = 1  # 시작 위치
    visited = set()
    possible = True

    while pos not in visited:
        if pos == B:
            print(D)
            sys.exit()
        if pos in traps:
            possible = False
            break

        visited.add(pos)
        pos = (pos - 1 + D) % N + 1  # 1-indexed 원형 이동

    if not possible:
        continue

print(-1)  # 불가능한 경우
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

    int N, B, K;
    cin >> N >> B >> K;

    set<int> traps;
    for (int i = 0; i < K; i++) {
        int t;
        cin >> t;
        traps.insert(t);
    }

    // 점프 크기 D를 1부터 N-1까지 시도
    for (int D = 1; D < N; D++) {
        int pos = 1;  // 시작 위치
        set<int> visited;
        bool possible = true;

        while (visited.find(pos) == visited.end()) {
            if (pos == B) {
                cout << D << endl;
                return 0;
            }
            if (traps.find(pos) != traps.end()) {
                possible = false;
                break;
            }

            visited.insert(pos);
            pos = (pos - 1 + D) % N + 1;  // 1-indexed 원형 이동
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
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int B = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        Set<Integer> traps = new HashSet<>();
        if (K > 0) {
            st = new StringTokenizer(br.readLine());
            for (int i = 0; i < K; i++) {
                traps.add(Integer.parseInt(st.nextToken()));
            }
        }

        // 점프 크기 D를 1부터 N-1까지 시도
        for (int D = 1; D < N; D++) {
            int pos = 1;  // 시작 위치
            Set<Integer> visited = new HashSet<>();
            boolean possible = true;

            while (!visited.contains(pos)) {
                if (pos == B) {
                    System.out.println(D);
                    return;
                }
                if (traps.contains(pos)) {
                    possible = false;
                    break;
                }

                visited.add(pos);
                pos = (pos - 1 + D) % N + 1;  // 1-indexed 원형 이동
            }
        }

        System.out.println(-1);
    }
}
'''
        }
    ],

    # 인덱스 3806: 도미노 무너트리기 (25972)
    3806: [
        {
            "language": "python",
            "code": '''# 도미노 무너트리기 문제
# 각 도미노가 넘어지면 오른쪽으로 길이만큼 영향

import sys
input = sys.stdin.readline

N = int(input())

dominoes = []
for _ in range(N):
    x, l = map(int, input().split())
    dominoes.append((x, l))

# 위치 순으로 정렬
dominoes.sort()

# 그리디: 현재 도달 가능한 최대 위치
count = 0
max_reach = 0

for x, l in dominoes:
    if x > max_reach:
        # 새로 밀어야 함
        count += 1
        max_reach = x + l
    else:
        # 이미 도달 가능, 범위 확장
        max_reach = max(max_reach, x + l)

print(count)
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

    vector<pair<int, int>> dominoes(N);
    for (int i = 0; i < N; i++) {
        cin >> dominoes[i].first >> dominoes[i].second;
    }

    // 위치 순으로 정렬
    sort(dominoes.begin(), dominoes.end());

    // 그리디
    int count = 0;
    int maxReach = 0;

    for (auto& [x, l] : dominoes) {
        if (x > maxReach) {
            count++;
            maxReach = x + l;
        } else {
            maxReach = max(maxReach, x + l);
        }
    }

    cout << count << endl;

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());

        int[][] dominoes = new int[N][2];
        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            dominoes[i][0] = Integer.parseInt(st.nextToken());
            dominoes[i][1] = Integer.parseInt(st.nextToken());
        }

        // 위치 순으로 정렬
        Arrays.sort(dominoes, (a, b) -> a[0] - b[0]);

        // 그리디
        int count = 0;
        int maxReach = 0;

        for (int i = 0; i < N; i++) {
            int x = dominoes[i][0];
            int l = dominoes[i][1];

            if (x > maxReach) {
                count++;
                maxReach = x + l;
            } else {
                maxReach = Math.max(maxReach, x + l);
            }
        }

        System.out.println(count);
    }
}
'''
        }
    ],

    # 인덱스 3857: 비 오는 날 (31066)
    3857: [
        {
            "language": "python",
            "code": '''# 비 오는 날 문제
# 빗물이 D만큼 내리고, 배수구가 E만큼 배수, S에 도달하면 대피

import sys
input = sys.stdin.readline

T = int(input())

for _ in range(T):
    S, D, E = map(int, input().split())

    if D <= E:
        # 물이 차지 않음
        print(-1)
    else:
        # 매 시간 (D - E)만큼 물이 참
        # S 이상 차는 데 걸리는 시간
        net_increase = D - E
        # ceil(S / net_increase)
        time = (S + net_increase - 1) // net_increase
        print(time)
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
        long long S, D, E;
        cin >> S >> D >> E;

        if (D <= E) {
            // 물이 차지 않음
            cout << -1 << "\\n";
        } else {
            // 매 시간 (D - E)만큼 물이 참
            long long netIncrease = D - E;
            // ceil(S / netIncrease)
            long long time = (S + netIncrease - 1) / netIncrease;
            cout << time << "\\n";
        }
    }

    return 0;
}
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long S = Long.parseLong(st.nextToken());
            long D = Long.parseLong(st.nextToken());
            long E = Long.parseLong(st.nextToken());

            if (D <= E) {
                // 물이 차지 않음
                sb.append(-1).append("\\n");
            } else {
                // 매 시간 (D - E)만큼 물이 참
                long netIncrease = D - E;
                // ceil(S / netIncrease)
                long time = (S + netIncrease - 1) / netIncrease;
                sb.append(time).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
        }
    ]
}


def main():
    """솔루션 추가 및 파일 저장"""

    # 파일 읽기 (락 사용)
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # 솔루션 추가
    updated_count = 0
    for idx, solutions in SOLUTIONS.items():
        if idx < len(data):
            data[idx]['solutions'] = solutions
            updated_count += 1
            print(f"인덱스 {idx} ({data[idx].get('name', 'Unknown')}) 솔루션 추가 완료")

    # 파일 쓰기 (락 사용)
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\n총 {updated_count}개 문제의 솔루션이 추가되었습니다.")


if __name__ == '__main__':
    main()
