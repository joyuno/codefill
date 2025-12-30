#!/usr/bin/env python3
"""
백준 문제에 대한 솔루션을 생성하고 추가하는 스크립트
Medium 난이도 문제 중 솔루션이 비어있는 문제 10개를 처리합니다.
"""

import json
import fcntl
import os

# 파일 경로
FILE_PATH = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

# 각 문제에 대한 솔루션 정의
SOLUTIONS = {
    # Problem 1: baekjoon_11947 - 이런 반전이
    "baekjoon_11947": [
        {
            "language": "python",
            "code": '''# 백준 11947 - 이런 반전이
# n의 반전 F(n): 각 자리수 a를 (9-a)로 바꾼 것
# 사랑스러움: n * F(n)의 최댓값 찾기
import sys
input = sys.stdin.readline

def reverse_num(n):
    """숫자 n의 반전을 계산"""
    result = 0
    multiplier = 1
    while n > 0:
        digit = n % 10
        result += (9 - digit) * multiplier
        multiplier *= 10
        n //= 10
    return result

def max_loveliness(N):
    """1부터 N까지의 수 중 최대 사랑스러움을 찾음"""
    # 자릿수별로 최댓값 후보 탐색
    # 사랑스러움 n * (9...9 - n)이 최대가 되려면
    # n이 대략 절반 근처일 때 최댓값
    max_val = 0

    # N의 자릿수
    str_n = str(N)
    digits = len(str_n)

    # 각 자릿수에서 후보 탐색
    for d in range(1, digits + 1):
        if d < digits:
            # d자리 수 중 최댓값은 약 절반 지점
            upper = 10 ** d - 1
            # 5로 시작하는 수가 좋은 후보
            candidates = []
            half = (10 ** (d - 1) + upper) // 2
            for offset in range(-10, 11):
                cand = half + offset
                if 1 <= cand <= upper:
                    candidates.append(cand)
            # 4..4, 5..5 형태도 후보
            candidates.append(int('4' * d))
            candidates.append(int('5' * d))
            for c in candidates:
                r = reverse_num(c)
                max_val = max(max_val, c * r)
        else:
            # N 자릿수
            # N 이하의 수 중에서 탐색
            candidates = []
            # 절반 근처
            half = (10 ** (d - 1) + N) // 2
            for offset in range(-100, 101):
                cand = half + offset
                if 1 <= cand <= N:
                    candidates.append(cand)
            # 4..4, 5..5 형태
            four_str = '4' * d
            five_str = '5' * d
            if int(four_str) <= N:
                candidates.append(int(four_str))
            if int(five_str) <= N:
                candidates.append(int(five_str))
            # N 자체도 후보
            candidates.append(N)
            # N-1자리 최댓값
            if d > 1:
                candidates.append(10 ** (d - 1) - 1)

            for c in candidates:
                if 1 <= c <= N:
                    r = reverse_num(c)
                    max_val = max(max_val, c * r)

    return max_val

T = int(input())
for _ in range(T):
    N = int(input())
    print(max_loveliness(N))
'''
        },
        {
            "language": "java",
            "code": '''// 백준 11947 - 이런 반전이
// n의 반전 F(n): 각 자리수 a를 (9-a)로 바꾼 것
// 사랑스러움: n * F(n)의 최댓값 찾기
import java.io.*;
import java.math.BigInteger;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());

        while (T-- > 0) {
            String nStr = br.readLine().trim();
            BigInteger N = new BigInteger(nStr);
            sb.append(maxLoveliness(N)).append("\\n");
        }

        System.out.print(sb);
    }

    // 숫자의 반전 계산
    static BigInteger reverseNum(BigInteger n) {
        String s = n.toString();
        StringBuilder sb = new StringBuilder();
        for (char c : s.toCharArray()) {
            sb.append((char)('9' - c + '0'));
        }
        String result = sb.toString().replaceFirst("^0+", "");
        return result.isEmpty() ? BigInteger.ZERO : new BigInteger(result);
    }

    // 1부터 N까지의 수 중 최대 사랑스러움
    static BigInteger maxLoveliness(BigInteger N) {
        BigInteger maxVal = BigInteger.ZERO;
        int digits = N.toString().length();

        for (int d = 1; d <= digits; d++) {
            BigInteger upper = BigInteger.TEN.pow(d).subtract(BigInteger.ONE);
            BigInteger lower = d == 1 ? BigInteger.ONE : BigInteger.TEN.pow(d - 1);
            BigInteger limit = d < digits ? upper : N;

            // 절반 근처 후보들
            BigInteger half = lower.add(limit).divide(BigInteger.valueOf(2));

            for (int offset = -100; offset <= 100; offset++) {
                BigInteger cand = half.add(BigInteger.valueOf(offset));
                if (cand.compareTo(BigInteger.ONE) >= 0 && cand.compareTo(limit) <= 0) {
                    BigInteger rev = reverseNum(cand);
                    BigInteger love = cand.multiply(rev);
                    if (love.compareTo(maxVal) > 0) {
                        maxVal = love;
                    }
                }
            }

            // 4...4, 5...5 형태
            String fourStr = "4".repeat(d);
            String fiveStr = "5".repeat(d);
            BigInteger four = new BigInteger(fourStr);
            BigInteger five = new BigInteger(fiveStr);

            if (four.compareTo(limit) <= 0) {
                BigInteger rev = reverseNum(four);
                maxVal = maxVal.max(four.multiply(rev));
            }
            if (five.compareTo(limit) <= 0) {
                BigInteger rev = reverseNum(five);
                maxVal = maxVal.max(five.multiply(rev));
            }
        }

        return maxVal;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 11947 - 이런 반전이
// n의 반전 F(n): 각 자리수 a를 (9-a)로 바꾼 것
// 사랑스러움: n * F(n)의 최댓값 찾기
#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

// 숫자의 반전 계산
long long reverseNum(long long n) {
    long long result = 0;
    long long multiplier = 1;
    while (n > 0) {
        int digit = n % 10;
        result += (9 - digit) * multiplier;
        multiplier *= 10;
        n /= 10;
    }
    return result;
}

// 1부터 N까지의 수 중 최대 사랑스러움
long long maxLoveliness(long long N) {
    long long maxVal = 0;

    // N의 자릿수
    string strN = to_string(N);
    int digits = strN.length();

    for (int d = 1; d <= digits; d++) {
        long long upper = 1;
        for (int i = 0; i < d; i++) upper *= 10;
        upper--;

        long long lower = (d == 1) ? 1 : (upper / 9 + 1);
        long long limit = (d < digits) ? upper : N;

        // 절반 근처 후보들
        long long half = (lower + limit) / 2;

        for (int offset = -100; offset <= 100; offset++) {
            long long cand = half + offset;
            if (cand >= 1 && cand <= limit) {
                long long rev = reverseNum(cand);
                maxVal = max(maxVal, cand * rev);
            }
        }

        // 4...4, 5...5 형태
        long long four = 0, five = 0;
        for (int i = 0; i < d; i++) {
            four = four * 10 + 4;
            five = five * 10 + 5;
        }

        if (four <= limit) {
            long long rev = reverseNum(four);
            maxVal = max(maxVal, four * rev);
        }
        if (five <= limit) {
            long long rev = reverseNum(five);
            maxVal = max(maxVal, five * rev);
        }
    }

    return maxVal;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T;
    cin >> T;

    while (T--) {
        long long N;
        cin >> N;
        cout << maxLoveliness(N) << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # Problem 2: baekjoon_14468 - 소가 길을 건너간 이유 2
    "baekjoon_14468": [
        {
            "language": "python",
            "code": '''# 백준 14468 - 소가 길을 건너간 이유 2
# 원형 길에서 경로가 교차하는 소 쌍의 개수 세기
import sys
input = sys.stdin.readline

s = input().strip()

# 각 소의 두 위치 저장
positions = {}
for i, c in enumerate(s):
    if c not in positions:
        positions[c] = []
    positions[c].append(i)

count = 0
cows = list(positions.keys())

# 모든 소 쌍에 대해 경로가 교차하는지 확인
for i in range(len(cows)):
    for j in range(i + 1, len(cows)):
        a1, a2 = positions[cows[i]]
        b1, b2 = positions[cows[j]]

        # 경로가 교차하는 경우: 한 소의 한 위치만 다른 소의 두 위치 사이에 있음
        # a1 < b1 < a2 < b2 또는 b1 < a1 < b2 < a2 형태
        if a1 < b1 < a2 < b2:
            count += 1
        elif b1 < a1 < b2 < a2:
            count += 1

print(count)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 14468 - 소가 길을 건너간 이유 2
// 원형 길에서 경로가 교차하는 소 쌍의 개수 세기
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine().trim();

        // 각 소의 두 위치 저장
        int[][] positions = new int[26][2];
        int[] idx = new int[26];

        for (int i = 0; i < s.length(); i++) {
            int c = s.charAt(i) - 'A';
            positions[c][idx[c]++] = i;
        }

        int count = 0;

        // 모든 소 쌍에 대해 경로가 교차하는지 확인
        for (int i = 0; i < 26; i++) {
            for (int j = i + 1; j < 26; j++) {
                int a1 = positions[i][0], a2 = positions[i][1];
                int b1 = positions[j][0], b2 = positions[j][1];

                // 경로가 교차하는 경우
                if (a1 < b1 && b1 < a2 && a2 < b2) {
                    count++;
                } else if (b1 < a1 && a1 < b2 && b2 < a2) {
                    count++;
                }
            }
        }

        System.out.println(count);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 14468 - 소가 길을 건너간 이유 2
// 원형 길에서 경로가 교차하는 소 쌍의 개수 세기
#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s;
    cin >> s;

    // 각 소의 두 위치 저장
    vector<pair<int, int>> positions(26, {-1, -1});

    for (int i = 0; i < (int)s.length(); i++) {
        int c = s[i] - 'A';
        if (positions[c].first == -1) {
            positions[c].first = i;
        } else {
            positions[c].second = i;
        }
    }

    int count = 0;

    // 모든 소 쌍에 대해 경로가 교차하는지 확인
    for (int i = 0; i < 26; i++) {
        for (int j = i + 1; j < 26; j++) {
            int a1 = positions[i].first, a2 = positions[i].second;
            int b1 = positions[j].first, b2 = positions[j].second;

            // 경로가 교차하는 경우
            if (a1 < b1 && b1 < a2 && a2 < b2) {
                count++;
            } else if (b1 < a1 && a1 < b2 && b2 < a2) {
                count++;
            }
        }
    }

    cout << count << endl;

    return 0;
}
'''
        }
    ],

    # Problem 3: baekjoon_27919 - UDPC 파티
    "baekjoon_27919": [
        {
            "language": "python",
            "code": '''# 백준 27919 - UDPC 파티
# U와 C, D와 P가 서로 바뀔 수 있음
# 각 마스코트가 선정될 수 있는지 확인
import sys
input = sys.stdin.readline

v = input().strip()

# U+C 그룹과 D+P 그룹의 개수
uc = v.count('U') + v.count('C')
dp = v.count('D') + v.count('P')

result = []

# 윤이(U)가 선정될 수 있는지: U가 최대가 될 수 있어야 함
# U는 uc개까지 가능, D는 dp개까지, P는 dp개까지
# U > D and U > P
# 최선의 경우: U = uc, D = 0, P = 0
# U가 이기려면 uc > 0 (적어도 1표는 있어야 함)
# D와 P 중 하나가 dp표를 다 가져갈 수 있으므로
# uc > dp이면 U가 이길 수 있음
if uc > dp:
    result.append('U')

# 달구(D)가 선정될 수 있는지
# D는 dp개까지 가능, U는 uc개까지, P는 0개까지 가능
# 최선: D = dp, U = 0, P = 0
# dp > uc이면 D가 이길 수 있음
if dp > uc:
    result.append('D')

# 포닉스(P)가 선정될 수 있는지
# P는 dp개까지 가능, U는 uc개까지, D는 0개까지 가능
# dp > uc이면 P가 이길 수 있음
if dp > uc:
    result.append('P')

if result:
    print(''.join(result))
else:
    print('C')
'''
        },
        {
            "language": "java",
            "code": '''// 백준 27919 - UDPC 파티
// U와 C, D와 P가 서로 바뀔 수 있음
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String v = br.readLine().trim();

        // U+C 그룹과 D+P 그룹의 개수
        int uc = 0, dp = 0;
        for (char c : v.toCharArray()) {
            if (c == 'U' || c == 'C') uc++;
            else if (c == 'D' || c == 'P') dp++;
        }

        StringBuilder result = new StringBuilder();

        // 윤이(U)가 선정될 수 있는지
        if (uc > dp) {
            result.append('U');
        }

        // 달구(D)가 선정될 수 있는지
        if (dp > uc) {
            result.append('D');
        }

        // 포닉스(P)가 선정될 수 있는지
        if (dp > uc) {
            result.append('P');
        }

        if (result.length() > 0) {
            System.out.println(result);
        } else {
            System.out.println('C');
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 27919 - UDPC 파티
// U와 C, D와 P가 서로 바뀔 수 있음
#include <iostream>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string v;
    cin >> v;

    // U+C 그룹과 D+P 그룹의 개수
    int uc = 0, dp = 0;
    for (char c : v) {
        if (c == 'U' || c == 'C') uc++;
        else if (c == 'D' || c == 'P') dp++;
    }

    string result = "";

    // 윤이(U)가 선정될 수 있는지
    if (uc > dp) {
        result += 'U';
    }

    // 달구(D)가 선정될 수 있는지
    if (dp > uc) {
        result += 'D';
    }

    // 포닉스(P)가 선정될 수 있는지
    if (dp > uc) {
        result += 'P';
    }

    if (!result.empty()) {
        cout << result << endl;
    } else {
        cout << 'C' << endl;
    }

    return 0;
}
'''
        }
    ],

    # Problem 4: baekjoon_31797 - 아~파트 아파트
    "baekjoon_31797": [
        {
            "language": "python",
            "code": '''# 백준 31797 - 아~파트 아파트
# 술게임에서 N층을 쌓는 사람 찾기
import sys
input = sys.stdin.readline

N, M = map(int, input().split())

# 각 참가자의 손 높이를 저장
hands = []
for i in range(1, M + 1):
    h1, h2 = map(int, input().split())
    hands.append((h1, i))  # (높이, 참가자 번호)
    hands.append((h2, i))

# 높이 순으로 정렬 (낮은 순)
hands.sort()

# N번째 손을 쌓는 참가자 찾기
# 가장 아래 손부터 순서대로 위로 쌓임
print(hands[N - 1][1])
'''
        },
        {
            "language": "java",
            "code": '''// 백준 31797 - 아~파트 아파트
// 술게임에서 N층을 쌓는 사람 찾기
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        // 각 참가자의 손 높이를 저장
        int[][] hands = new int[2 * M][2];
        int idx = 0;

        for (int i = 1; i <= M; i++) {
            st = new StringTokenizer(br.readLine());
            int h1 = Integer.parseInt(st.nextToken());
            int h2 = Integer.parseInt(st.nextToken());
            hands[idx][0] = h1;
            hands[idx][1] = i;
            idx++;
            hands[idx][0] = h2;
            hands[idx][1] = i;
            idx++;
        }

        // 높이 순으로 정렬
        Arrays.sort(hands, (a, b) -> a[0] - b[0]);

        // N번째 손을 쌓는 참가자 찾기
        System.out.println(hands[N - 1][1]);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 31797 - 아~파트 아파트
// 술게임에서 N층을 쌓는 사람 찾기
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, M;
    cin >> N >> M;

    // 각 참가자의 손 높이를 저장
    vector<pair<int, int>> hands;

    for (int i = 1; i <= M; i++) {
        int h1, h2;
        cin >> h1 >> h2;
        hands.push_back({h1, i});
        hands.push_back({h2, i});
    }

    // 높이 순으로 정렬
    sort(hands.begin(), hands.end());

    // N번째 손을 쌓는 참가자 찾기
    cout << hands[N - 1].second << endl;

    return 0;
}
'''
        }
    ],

    # Problem 5: baekjoon_1972 - 놀라운 문자열
    "baekjoon_1972": [
        {
            "language": "python",
            "code": '''# 백준 1972 - 놀라운 문자열
# 모든 D에 대해 D-쌍이 모두 다른 문자열인지 확인
import sys
input = sys.stdin.readline

while True:
    s = input().strip()
    if s == '*':
        break

    n = len(s)
    is_surprising = True

    # 0-쌍부터 (n-2)-쌍까지 확인
    for d in range(n - 1):
        pairs = set()
        for i in range(n - d - 1):
            pair = s[i] + s[i + d + 1]
            if pair in pairs:
                is_surprising = False
                break
            pairs.add(pair)
        if not is_surprising:
            break

    if is_surprising:
        print(f"{s} is surprising.")
    else:
        print(f"{s} is NOT surprising.")
'''
        },
        {
            "language": "java",
            "code": '''// 백준 1972 - 놀라운 문자열
// 모든 D에 대해 D-쌍이 모두 다른 문자열인지 확인
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        while (true) {
            String s = br.readLine().trim();
            if (s.equals("*")) break;

            int n = s.length();
            boolean isSurprising = true;

            // 0-쌍부터 (n-2)-쌍까지 확인
            outer:
            for (int d = 0; d < n - 1; d++) {
                Set<String> pairs = new HashSet<>();
                for (int i = 0; i < n - d - 1; i++) {
                    String pair = "" + s.charAt(i) + s.charAt(i + d + 1);
                    if (pairs.contains(pair)) {
                        isSurprising = false;
                        break outer;
                    }
                    pairs.add(pair);
                }
            }

            if (isSurprising) {
                sb.append(s).append(" is surprising.\\n");
            } else {
                sb.append(s).append(" is NOT surprising.\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 1972 - 놀라운 문자열
// 모든 D에 대해 D-쌍이 모두 다른 문자열인지 확인
#include <iostream>
#include <string>
#include <set>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s;
    while (cin >> s && s != "*") {
        int n = s.length();
        bool isSurprising = true;

        // 0-쌍부터 (n-2)-쌍까지 확인
        for (int d = 0; d < n - 1 && isSurprising; d++) {
            set<string> pairs;
            for (int i = 0; i < n - d - 1; i++) {
                string pair = "";
                pair += s[i];
                pair += s[i + d + 1];
                if (pairs.count(pair)) {
                    isSurprising = false;
                    break;
                }
                pairs.insert(pair);
            }
        }

        if (isSurprising) {
            cout << s << " is surprising." << endl;
        } else {
            cout << s << " is NOT surprising." << endl;
        }
    }

    return 0;
}
'''
        }
    ],

    # Problem 6: baekjoon_15889 - 호 안에 수류탄이야!!
    "baekjoon_15889": [
        {
            "language": "python",
            "code": '''# 백준 15889 - 호 안에 수류탄이야!!
# 수류탄이 마지막 전우에게 도달할 수 있는지 확인
import sys
input = sys.stdin.readline

N = int(input())
positions = list(map(int, input().split()))

if N == 1:
    # 혼자면 이미 마지막 전우
    print("권병장님, 중대장님이 찾으십니다")
else:
    ranges = list(map(int, input().split()))

    # 현재 도달 가능한 최대 거리
    max_reach = positions[0] + ranges[0]

    for i in range(1, N - 1):
        if positions[i] <= max_reach:
            # i번째 전우에게 도달 가능하면 그 전우도 던질 수 있음
            max_reach = max(max_reach, positions[i] + ranges[i])

    # 마지막 전우에게 도달 가능한지 확인
    if max_reach >= positions[N - 1]:
        print("권병장님, 중대장님이 찾으십니다")
    else:
        print("엄마 나 전역 늦어질 것 같아")
'''
        },
        {
            "language": "java",
            "code": '''// 백준 15889 - 호 안에 수류탄이야!!
// 수류탄이 마지막 전우에게 도달할 수 있는지 확인
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] positions = new int[N];
        for (int i = 0; i < N; i++) {
            positions[i] = Integer.parseInt(st.nextToken());
        }

        if (N == 1) {
            System.out.println("권병장님, 중대장님이 찾으십니다");
            return;
        }

        st = new StringTokenizer(br.readLine());
        int[] ranges = new int[N - 1];
        for (int i = 0; i < N - 1; i++) {
            ranges[i] = Integer.parseInt(st.nextToken());
        }

        // 현재 도달 가능한 최대 거리
        long maxReach = positions[0] + ranges[0];

        for (int i = 1; i < N - 1; i++) {
            if (positions[i] <= maxReach) {
                maxReach = Math.max(maxReach, (long)positions[i] + ranges[i]);
            }
        }

        // 마지막 전우에게 도달 가능한지 확인
        if (maxReach >= positions[N - 1]) {
            System.out.println("권병장님, 중대장님이 찾으십니다");
        } else {
            System.out.println("엄마 나 전역 늦어질 것 같아");
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 15889 - 호 안에 수류탄이야!!
// 수류탄이 마지막 전우에게 도달할 수 있는지 확인
#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;

    vector<long long> positions(N);
    for (int i = 0; i < N; i++) {
        cin >> positions[i];
    }

    if (N == 1) {
        cout << "권병장님, 중대장님이 찾으십니다" << endl;
        return 0;
    }

    vector<long long> ranges(N - 1);
    for (int i = 0; i < N - 1; i++) {
        cin >> ranges[i];
    }

    // 현재 도달 가능한 최대 거리
    long long maxReach = positions[0] + ranges[0];

    for (int i = 1; i < N - 1; i++) {
        if (positions[i] <= maxReach) {
            maxReach = max(maxReach, positions[i] + ranges[i]);
        }
    }

    // 마지막 전우에게 도달 가능한지 확인
    if (maxReach >= positions[N - 1]) {
        cout << "권병장님, 중대장님이 찾으십니다" << endl;
    } else {
        cout << "엄마 나 전역 늦어질 것 같아" << endl;
    }

    return 0;
}
'''
        }
    ],

    # Problem 7: baekjoon_4446 - ROT13
    "baekjoon_4446": [
        {
            "language": "python",
            "code": '''# 백준 4446 - ROT13
# 모음과 자음을 각각 순환시켜 변환
import sys
input = sys.stdin.readline

# 모음: a i y e o u (6개, 3칸 이동)
vowels = "aiyeou"
# 자음: b k x z n h d c w g p v j q t s r l m f (20개, 10칸 이동)
consonants = "bkxznhdcwgpvjqtsrlmf"

def decode(c):
    """ROT13을 영어로 변환"""
    lower_c = c.lower()

    if lower_c in vowels:
        idx = vowels.index(lower_c)
        # 3칸 뒤로 이동 (역변환)
        new_idx = (idx - 3) % 6
        new_char = vowels[new_idx]
    elif lower_c in consonants:
        idx = consonants.index(lower_c)
        # 10칸 뒤로 이동 (역변환)
        new_idx = (idx - 10) % 20
        new_char = consonants[new_idx]
    else:
        return c

    # 대소문자 유지
    return new_char.upper() if c.isupper() else new_char

while True:
    try:
        line = input()
        if not line:
            break
        line = line.rstrip('\\n')
        result = ''.join(decode(c) for c in line)
        print(result)
    except:
        break
'''
        },
        {
            "language": "java",
            "code": '''// 백준 4446 - ROT13
// 모음과 자음을 각각 순환시켜 변환
import java.io.*;

public class Main {
    static String vowels = "aiyeou";
    static String consonants = "bkxznhdcwgpvjqtsrlmf";

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        String line;
        while ((line = br.readLine()) != null) {
            StringBuilder result = new StringBuilder();
            for (char c : line.toCharArray()) {
                result.append(decode(c));
            }
            sb.append(result).append("\\n");
        }

        System.out.print(sb);
    }

    static char decode(char c) {
        char lowerC = Character.toLowerCase(c);
        int vowelIdx = vowels.indexOf(lowerC);
        int consonantIdx = consonants.indexOf(lowerC);

        char newChar;
        if (vowelIdx != -1) {
            // 모음: 3칸 뒤로 이동
            int newIdx = (vowelIdx - 3 + 6) % 6;
            newChar = vowels.charAt(newIdx);
        } else if (consonantIdx != -1) {
            // 자음: 10칸 뒤로 이동
            int newIdx = (consonantIdx - 10 + 20) % 20;
            newChar = consonants.charAt(newIdx);
        } else {
            return c;
        }

        return Character.isUpperCase(c) ? Character.toUpperCase(newChar) : newChar;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 4446 - ROT13
// 모음과 자음을 각각 순환시켜 변환
#include <iostream>
#include <string>
using namespace std;

string vowels = "aiyeou";
string consonants = "bkxznhdcwgpvjqtsrlmf";

char decode(char c) {
    char lowerC = tolower(c);

    size_t vowelIdx = vowels.find(lowerC);
    size_t consonantIdx = consonants.find(lowerC);

    char newChar;
    if (vowelIdx != string::npos) {
        // 모음: 3칸 뒤로 이동
        int newIdx = (vowelIdx - 3 + 6) % 6;
        newChar = vowels[newIdx];
    } else if (consonantIdx != string::npos) {
        // 자음: 10칸 뒤로 이동
        int newIdx = (consonantIdx - 10 + 20) % 20;
        newChar = consonants[newIdx];
    } else {
        return c;
    }

    return isupper(c) ? toupper(newChar) : newChar;
}

int main() {
    string line;
    while (getline(cin, line)) {
        string result = "";
        for (char c : line) {
            result += decode(c);
        }
        cout << result << endl;
    }

    return 0;
}
'''
        }
    ],

    # Problem 8: baekjoon_14584 - 암호 해독
    "baekjoon_14584": [
        {
            "language": "python",
            "code": '''# 백준 14584 - 암호 해독
# 카이사르 암호 해독 - 사전 단어가 포함되는 shift 찾기
import sys
input = sys.stdin.readline

cipher = input().strip()
n = int(input())
words = [input().strip() for _ in range(n)]

def shift_text(text, k):
    """텍스트를 k칸 뒤로 이동"""
    result = ""
    for c in text:
        new_c = chr((ord(c) - ord('a') + k) % 26 + ord('a'))
        result += new_c
    return result

# 모든 shift 값에 대해 시도
for k in range(26):
    decoded = shift_text(cipher, k)

    # 사전 단어가 포함되는지 확인
    for word in words:
        if word in decoded:
            print(decoded)
            exit()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 14584 - 암호 해독
// 카이사르 암호 해독 - 사전 단어가 포함되는 shift 찾기
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        String cipher = br.readLine().trim();
        int n = Integer.parseInt(br.readLine().trim());
        String[] words = new String[n];
        for (int i = 0; i < n; i++) {
            words[i] = br.readLine().trim();
        }

        // 모든 shift 값에 대해 시도
        for (int k = 0; k < 26; k++) {
            String decoded = shiftText(cipher, k);

            // 사전 단어가 포함되는지 확인
            for (String word : words) {
                if (decoded.contains(word)) {
                    System.out.println(decoded);
                    return;
                }
            }
        }
    }

    static String shiftText(String text, int k) {
        StringBuilder sb = new StringBuilder();
        for (char c : text.toCharArray()) {
            char newC = (char)((c - 'a' + k) % 26 + 'a');
            sb.append(newC);
        }
        return sb.toString();
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 14584 - 암호 해독
// 카이사르 암호 해독 - 사전 단어가 포함되는 shift 찾기
#include <iostream>
#include <string>
#include <vector>
using namespace std;

string shiftText(const string& text, int k) {
    string result = "";
    for (char c : text) {
        char newC = (c - 'a' + k) % 26 + 'a';
        result += newC;
    }
    return result;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string cipher;
    cin >> cipher;

    int n;
    cin >> n;

    vector<string> words(n);
    for (int i = 0; i < n; i++) {
        cin >> words[i];
    }

    // 모든 shift 값에 대해 시도
    for (int k = 0; k < 26; k++) {
        string decoded = shiftText(cipher, k);

        // 사전 단어가 포함되는지 확인
        for (const string& word : words) {
            if (decoded.find(word) != string::npos) {
                cout << decoded << endl;
                return 0;
            }
        }
    }

    return 0;
}
'''
        }
    ],

    # Problem 9: baekjoon_5883 - 아이폰 9S
    "baekjoon_5883": [
        {
            "language": "python",
            "code": '''# 백준 5883 - 아이폰 9S
# 특정 용량을 제거했을 때 가장 긴 연속 구간 찾기
import sys
input = sys.stdin.readline

N = int(input())
B = [int(input()) for _ in range(N)]

# 모든 용량의 집합
capacities = set(B)

max_len = 0

# 각 용량을 제거했을 때 가장 긴 연속 구간 계산
for remove in capacities:
    # remove 용량을 제외한 리스트
    current_len = 0
    current_val = None

    for b in B:
        if b == remove:
            continue

        if b == current_val:
            current_len += 1
        else:
            current_val = b
            current_len = 1

        max_len = max(max_len, current_len)

print(max_len)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 5883 - 아이폰 9S
// 특정 용량을 제거했을 때 가장 긴 연속 구간 찾기
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());
        int[] B = new int[N];
        Set<Integer> capacities = new HashSet<>();

        for (int i = 0; i < N; i++) {
            B[i] = Integer.parseInt(br.readLine().trim());
            capacities.add(B[i]);
        }

        int maxLen = 0;

        // 각 용량을 제거했을 때 가장 긴 연속 구간 계산
        for (int remove : capacities) {
            int currentLen = 0;
            int currentVal = -1;

            for (int b : B) {
                if (b == remove) continue;

                if (b == currentVal) {
                    currentLen++;
                } else {
                    currentVal = b;
                    currentLen = 1;
                }

                maxLen = Math.max(maxLen, currentLen);
            }
        }

        System.out.println(maxLen);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 5883 - 아이폰 9S
// 특정 용량을 제거했을 때 가장 긴 연속 구간 찾기
#include <iostream>
#include <vector>
#include <set>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;

    vector<int> B(N);
    set<int> capacities;

    for (int i = 0; i < N; i++) {
        cin >> B[i];
        capacities.insert(B[i]);
    }

    int maxLen = 0;

    // 각 용량을 제거했을 때 가장 긴 연속 구간 계산
    for (int remove : capacities) {
        int currentLen = 0;
        int currentVal = -1;

        for (int b : B) {
            if (b == remove) continue;

            if (b == currentVal) {
                currentLen++;
            } else {
                currentVal = b;
                currentLen = 1;
            }

            maxLen = max(maxLen, currentLen);
        }
    }

    cout << maxLen << endl;

    return 0;
}
'''
        }
    ],

    # Problem 10: baekjoon_1560 - 비숍
    "baekjoon_1560": [
        {
            "language": "python",
            "code": '''# 백준 1560 - 비숍
# N*N 체스판에 서로 공격하지 않는 최대 비숍 수
# 비숍은 대각선으로 이동하므로
# 흰 칸과 검은 칸에 독립적으로 배치 가능
# N=1: 1개, N>=2: 2*(N-1)개

N = int(input())

if N == 1:
    print(1)
else:
    # 각 대각선에 최대 1개씩 배치 가능
    # 왼쪽 위에서 오른쪽 아래 대각선: 2*N-1개
    # 하지만 흰 칸과 검은 칸이 분리되어 있음
    # 흰 칸 대각선 수: N개 (N이 짝수), N개 (N이 홀수)
    # 검은 칸 대각선 수: N-1개 (N이 짝수), N-1개 (N이 홀수)
    # 최대 비숍 수: N + (N-1) - 1 = 2*N - 2
    # 단, 가장자리 대각선은 1칸짜리이므로 고려 필요
    print(2 * N - 2)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 1560 - 비숍
// N*N 체스판에 서로 공격하지 않는 최대 비숍 수
import java.io.*;
import java.math.BigInteger;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        BigInteger N = new BigInteger(br.readLine().trim());

        if (N.equals(BigInteger.ONE)) {
            System.out.println(1);
        } else {
            // 최대 비숍 수: 2*N - 2
            BigInteger result = N.multiply(BigInteger.valueOf(2)).subtract(BigInteger.valueOf(2));
            System.out.println(result);
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 1560 - 비숍
// N*N 체스판에 서로 공격하지 않는 최대 비숍 수
// N이 70자리까지 가능하므로 문자열 연산 필요
#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

// 큰 수 더하기
string addBigInt(string a, string b) {
    string result = "";
    int carry = 0;
    int i = a.length() - 1;
    int j = b.length() - 1;

    while (i >= 0 || j >= 0 || carry) {
        int sum = carry;
        if (i >= 0) sum += a[i--] - '0';
        if (j >= 0) sum += b[j--] - '0';
        result += (char)(sum % 10 + '0');
        carry = sum / 10;
    }

    reverse(result.begin(), result.end());
    return result;
}

// 큰 수 빼기 (a > b 가정)
string subBigInt(string a, string b) {
    string result = "";
    int borrow = 0;
    int i = a.length() - 1;
    int j = b.length() - 1;

    while (i >= 0) {
        int diff = (a[i--] - '0') - borrow;
        if (j >= 0) diff -= (b[j--] - '0');
        if (diff < 0) {
            diff += 10;
            borrow = 1;
        } else {
            borrow = 0;
        }
        result += (char)(diff + '0');
    }

    // 앞의 0 제거
    while (result.length() > 1 && result.back() == '0') {
        result.pop_back();
    }

    reverse(result.begin(), result.end());
    return result;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string N;
    cin >> N;

    if (N == "1") {
        cout << 1 << endl;
    } else {
        // 최대 비숍 수: 2*N - 2
        string twoN = addBigInt(N, N);
        string result = subBigInt(twoN, "2");
        cout << result << endl;
    }

    return 0;
}
'''
        }
    ]
}

def main():
    # JSON 파일 읽기
    print("JSON 파일 읽는 중...")
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"전체 문제 수: {len(data)}")

    # 업데이트할 문제 찾기 및 업데이트
    updated_count = 0
    updated_ids = []

    for problem in data:
        problem_id = problem.get('id')
        if problem_id in SOLUTIONS:
            current_solutions = problem.get('solutions')
            # 솔루션이 비어있는 경우에만 업데이트
            if current_solutions is None or current_solutions == []:
                problem['solutions'] = SOLUTIONS[problem_id]
                updated_count += 1
                updated_ids.append(problem_id)
                print(f"  업데이트: {problem_id}")
            else:
                print(f"  건너뜀 (이미 솔루션 있음): {problem_id}")

    # 파일 쓰기 (파일 잠금 사용)
    print("\nJSON 파일 저장 중...")
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\n완료!")
    print(f"업데이트된 문제 수: {updated_count}")
    print(f"업데이트된 문제 ID: {updated_ids}")

    # 검증
    print("\n검증 중...")
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        verify_data = json.load(f)

    for problem in verify_data:
        if problem.get('id') in updated_ids:
            sols = problem.get('solutions', [])
            print(f"  {problem.get('id')}: {len(sols)}개 솔루션")

if __name__ == "__main__":
    main()
