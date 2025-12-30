#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배치 8: 문제 71-80 솔루션 추가"""

import json

# 새로운 솔루션들
new_solutions = {
    "32981": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 찐 Even Number 개수 - N자리 수 중 {0,2,4,6,8}로만 이루어진 수
# N자리: 첫 자리는 2,4,6,8 (4가지), 나머지는 0,2,4,6,8 (5가지)
# 답 = 4 * 5^(N-1)
import sys
input = sys.stdin.readline

MOD = 10**9 + 7

def solve():
    Q = int(input())
    results = []

    for _ in range(Q):
        N = int(input())
        # 4 * 5^(N-1)
        result = 4 * pow(5, N - 1, MOD) % MOD
        results.append(result)

    print('\\n'.join(map(str, results)))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
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

    int Q;
    cin >> Q;

    while (Q--) {
        long long N;
        cin >> N;
        // 4 * 5^(N-1)
        long long result = 4 * power(5, N - 1, MOD) % MOD;
        cout << result << "\\n";
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
        StringBuilder sb = new StringBuilder();

        int Q = Integer.parseInt(br.readLine().trim());

        while (Q-- > 0) {
            long N = Long.parseLong(br.readLine().trim());
            long result = 4 * power(5, N - 1, MOD) % MOD;
            sb.append(result).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "25594": {
        "solutions": [
            {
                "language": "python",
                "code": '''# HG 표준음성기호 해독
import sys
input = sys.stdin.readline

# HG 표준음성기호 매핑
hg_map = {
    'aespa': 'a', 'baekjoon': 'b', 'cau': 'c', 'debug': 'd', 'edge': 'e',
    'firefox': 'f', 'golang': 'g', 'haegang': 'h', 'iu': 'i', 'java': 'j',
    'kotlin': 'k', 'lol': 'l', 'mips': 'm', 'null': 'n', 'os': 'o',
    'python': 'p', 'query': 'q', 'roka': 'r', 'solvedac': 's', 'tod': 't',
    'unix': 'u', 'virus': 'v', 'whale': 'w', 'xcode': 'x', 'yahoo': 'y',
    'zebra': 'z'
}

def solve():
    S = input().strip()

    # DP로 해독 가능한지 확인
    n = len(S)
    dp = [False] * (n + 1)
    dp[0] = True
    parent = [-1] * (n + 1)

    for i in range(n):
        if not dp[i]:
            continue
        for word in hg_map:
            if S[i:i+len(word)] == word:
                dp[i + len(word)] = True
                parent[i + len(word)] = i

    if not dp[n]:
        print("ERROR!")
        return

    # 역추적
    result = []
    pos = n
    while pos > 0:
        prev = parent[pos]
        word = S[prev:pos]
        result.append(hg_map[word])
        pos = prev

    result.reverse()
    print("It's HG!")
    print(''.join(result))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <vector>
#include <map>
using namespace std;

map<string, char> hgMap = {
    {"aespa", 'a'}, {"baekjoon", 'b'}, {"cau", 'c'}, {"debug", 'd'}, {"edge", 'e'},
    {"firefox", 'f'}, {"golang", 'g'}, {"haegang", 'h'}, {"iu", 'i'}, {"java", 'j'},
    {"kotlin", 'k'}, {"lol", 'l'}, {"mips", 'm'}, {"null", 'n'}, {"os", 'o'},
    {"python", 'p'}, {"query", 'q'}, {"roka", 'r'}, {"solvedac", 's'}, {"tod", 't'},
    {"unix", 'u'}, {"virus", 'v'}, {"whale", 'w'}, {"xcode", 'x'}, {"yahoo", 'y'},
    {"zebra", 'z'}
};

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string S;
    cin >> S;

    int n = S.length();
    vector<bool> dp(n + 1, false);
    vector<int> parent(n + 1, -1);
    dp[0] = true;

    for (int i = 0; i < n; i++) {
        if (!dp[i]) continue;
        for (auto& [word, ch] : hgMap) {
            int len = word.length();
            if (i + len <= n && S.substr(i, len) == word) {
                dp[i + len] = true;
                parent[i + len] = i;
            }
        }
    }

    if (!dp[n]) {
        cout << "ERROR!" << endl;
        return 0;
    }

    string result;
    int pos = n;
    while (pos > 0) {
        int prev = parent[pos];
        string word = S.substr(prev, pos - prev);
        result = hgMap[word] + result;
        pos = prev;
    }

    cout << "It's HG!" << endl;
    cout << result << endl;

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static Map<String, Character> hgMap = new HashMap<>();

    static {
        hgMap.put("aespa", 'a'); hgMap.put("baekjoon", 'b'); hgMap.put("cau", 'c');
        hgMap.put("debug", 'd'); hgMap.put("edge", 'e'); hgMap.put("firefox", 'f');
        hgMap.put("golang", 'g'); hgMap.put("haegang", 'h'); hgMap.put("iu", 'i');
        hgMap.put("java", 'j'); hgMap.put("kotlin", 'k'); hgMap.put("lol", 'l');
        hgMap.put("mips", 'm'); hgMap.put("null", 'n'); hgMap.put("os", 'o');
        hgMap.put("python", 'p'); hgMap.put("query", 'q'); hgMap.put("roka", 'r');
        hgMap.put("solvedac", 's'); hgMap.put("tod", 't'); hgMap.put("unix", 'u');
        hgMap.put("virus", 'v'); hgMap.put("whale", 'w'); hgMap.put("xcode", 'x');
        hgMap.put("yahoo", 'y'); hgMap.put("zebra", 'z');
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String S = br.readLine();

        int n = S.length();
        boolean[] dp = new boolean[n + 1];
        int[] parent = new int[n + 1];
        Arrays.fill(parent, -1);
        dp[0] = true;

        for (int i = 0; i < n; i++) {
            if (!dp[i]) continue;
            for (String word : hgMap.keySet()) {
                int len = word.length();
                if (i + len <= n && S.substring(i, i + len).equals(word)) {
                    dp[i + len] = true;
                    parent[i + len] = i;
                }
            }
        }

        if (!dp[n]) {
            System.out.println("ERROR!");
            return;
        }

        StringBuilder result = new StringBuilder();
        int pos = n;
        while (pos > 0) {
            int prev = parent[pos];
            String word = S.substring(prev, pos);
            result.insert(0, hgMap.get(word));
            pos = prev;
        }

        System.out.println("It's HG!");
        System.out.println(result);
    }
}
'''
            }
        ]
    },
    "28419": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 홀수/짝수 위치 합 같게 만들기
# 연산: 인접한 3개 위치를 각각 +1
import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    A = list(map(int, input().split()))

    # 홀수 위치 합 (1-indexed 홀수 = 0-indexed 짝수)
    odd_sum = sum(A[i] for i in range(0, N, 2))  # 1, 3, 5, ...
    even_sum = sum(A[i] for i in range(1, N, 2))  # 2, 4, 6, ...

    diff = odd_sum - even_sum

    # 연산 (i, i+1, i+2)를 할 때:
    # i가 0-indexed 짝수 (1-indexed 홀수)면: odd +2, even +1 -> diff +1
    # i가 0-indexed 홀수 (1-indexed 짝수)면: odd +1, even +2 -> diff -1

    # N이 홀수면: 0-indexed 짝수 시작점 = ceil((N-2)/2) 개
    # N이 짝수면: 0-indexed 짝수 시작점 = (N-2)/2 개

    # diff를 0으로 만들어야 함
    # diff > 0: diff -1 연산 (0-indexed 홀수 시작) 사용
    # diff < 0: diff +1 연산 (0-indexed 짝수 시작) 사용

    # N-2개의 연산 시작점 가능 (0 ~ N-3)
    # 0-indexed 짝수: 0, 2, 4, ... -> diff +1
    # 0-indexed 홀수: 1, 3, 5, ... -> diff -1

    # 0-indexed 홀수 시작점 개수
    cnt_minus = len([i for i in range(1, N-2+1, 2)])  # diff -1 연산
    cnt_plus = len([i for i in range(0, N-2+1, 2)])   # diff +1 연산

    if diff == 0:
        print(0)
    elif diff > 0:
        # diff -1 연산 diff번 필요
        if cnt_minus == 0:
            print(-1)
        else:
            print(diff)
    else:  # diff < 0
        # diff +1 연산 -diff번 필요
        if cnt_plus == 0:
            print(-1)
        else:
            print(-diff)

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

    int N;
    cin >> N;

    long long oddSum = 0, evenSum = 0;
    for (int i = 0; i < N; i++) {
        long long a;
        cin >> a;
        if (i % 2 == 0) oddSum += a;
        else evenSum += a;
    }

    long long diff = oddSum - evenSum;

    // 0-indexed 홀수 시작점 개수 (diff -1)
    int cntMinus = 0;
    for (int i = 1; i <= N - 3; i += 2) cntMinus++;

    // 0-indexed 짝수 시작점 개수 (diff +1)
    int cntPlus = 0;
    for (int i = 0; i <= N - 3; i += 2) cntPlus++;

    if (diff == 0) {
        cout << 0 << endl;
    } else if (diff > 0) {
        if (cntMinus == 0) cout << -1 << endl;
        else cout << diff << endl;
    } else {
        if (cntPlus == 0) cout << -1 << endl;
        else cout << -diff << endl;
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
        long oddSum = 0, evenSum = 0;
        for (int i = 0; i < N; i++) {
            long a = Long.parseLong(st.nextToken());
            if (i % 2 == 0) oddSum += a;
            else evenSum += a;
        }

        long diff = oddSum - evenSum;

        int cntMinus = 0;
        for (int i = 1; i <= N - 3; i += 2) cntMinus++;

        int cntPlus = 0;
        for (int i = 0; i <= N - 3; i += 2) cntPlus++;

        if (diff == 0) {
            System.out.println(0);
        } else if (diff > 0) {
            if (cntMinus == 0) System.out.println(-1);
            else System.out.println(diff);
        } else {
            if (cntPlus == 0) System.out.println(-1);
            else System.out.println(-diff);
        }
    }
}
'''
            }
        ]
    },
    "30020": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 치즈버거 만들기 - 패티 A개, 치즈 B개
# 패티 = 치즈 + 버거 수
# A = B + K (K: 버거 수)
# 조건: K <= B (각 버거에 최소 치즈 1개)

def solve():
    A, B = map(int, input().split())

    # K = A - B (버거 수)
    K = A - B

    if K <= 0 or K > B:
        print("NO")
        return

    print("YES")
    print(K)

    # 남은 패티와 치즈 분배
    remaining_patties = A - K  # 기본 1개씩 사용 후 남은 패티
    remaining_cheese = B - K   # 기본 1개씩 사용 후 남은 치즈

    # 모든 버거에 기본 "aba" (패티2, 치즈1)
    # 추가: 패티-치즈 쌍을 균등하게 분배

    for i in range(K):
        # 남은 것을 하나씩 추가
        extra_pairs = 0
        if remaining_patties > 0 and remaining_cheese > 0:
            extra_pairs = min(remaining_patties, remaining_cheese)
            extra_pairs = min(extra_pairs, remaining_patties // (K - i) if K - i > 0 else 0)

        # 단순히: 각 버거에 가능한 만큼 추가
        add = min(remaining_patties, remaining_cheese)
        add = add // (K - i) if K - i > 0 else 0

        remaining_patties -= add
        remaining_cheese -= add

        burger = "ab" * (add + 1) + "a"
        print(burger)

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

    int A, B;
    cin >> A >> B;

    int K = A - B;

    if (K <= 0 || K > B) {
        cout << "NO" << endl;
        return 0;
    }

    cout << "YES" << endl;
    cout << K << endl;

    int remP = A - K;
    int remC = B - K;

    for (int i = 0; i < K; i++) {
        int add = 0;
        if (K - i > 0) {
            add = min(remP, remC) / (K - i);
        }
        remP -= add;
        remC -= add;

        string burger = "";
        for (int j = 0; j < add + 1; j++) {
            burger += "ab";
        }
        burger += "a";
        cout << burger << "\\n";
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
        int A = sc.nextInt();
        int B = sc.nextInt();

        int K = A - B;

        if (K <= 0 || K > B) {
            System.out.println("NO");
            return;
        }

        System.out.println("YES");
        System.out.println(K);

        int remP = A - K;
        int remC = B - K;

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < K; i++) {
            int add = 0;
            if (K - i > 0) {
                add = Math.min(remP, remC) / (K - i);
            }
            remP -= add;
            remC -= add;

            StringBuilder burger = new StringBuilder();
            for (int j = 0; j < add + 1; j++) {
                burger.append("ab");
            }
            burger.append("a");
            sb.append(burger).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "1491": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 나선 끝점 찾기 - M x N 궁전
def solve():
    N, M = map(int, input().split())

    # 나선 시뮬레이션
    # 방향: 동(0), 북(1), 서(2), 남(3)
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]

    x, y = 0, 0
    direction = 0

    left, right = 0, N - 1
    bottom, top = 0, M - 1

    last_x, last_y = 0, 0

    while left <= right and bottom <= top:
        if direction == 0:  # 동쪽
            for i in range(left, right + 1):
                last_x, last_y = i, bottom
            bottom += 1
        elif direction == 1:  # 북쪽
            for i in range(bottom, top + 1):
                last_x, last_y = right, i
            right -= 1
        elif direction == 2:  # 서쪽
            for i in range(right, left - 1, -1):
                last_x, last_y = i, top
            top -= 1
        else:  # 남쪽
            for i in range(top, bottom - 1, -1):
                last_x, last_y = left, i
            left += 1

        direction = (direction + 1) % 4

    print(last_x, last_y)

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

    int N, M;
    cin >> N >> M;

    int left = 0, right = N - 1;
    int bottom = 0, top = M - 1;
    int direction = 0;

    int lastX = 0, lastY = 0;

    while (left <= right && bottom <= top) {
        if (direction == 0) {
            for (int i = left; i <= right; i++) {
                lastX = i; lastY = bottom;
            }
            bottom++;
        } else if (direction == 1) {
            for (int i = bottom; i <= top; i++) {
                lastX = right; lastY = i;
            }
            right--;
        } else if (direction == 2) {
            for (int i = right; i >= left; i--) {
                lastX = i; lastY = top;
            }
            top--;
        } else {
            for (int i = top; i >= bottom; i--) {
                lastX = left; lastY = i;
            }
            left++;
        }

        direction = (direction + 1) % 4;
    }

    cout << lastX << " " << lastY << endl;

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
        int M = sc.nextInt();

        int left = 0, right = N - 1;
        int bottom = 0, top = M - 1;
        int direction = 0;

        int lastX = 0, lastY = 0;

        while (left <= right && bottom <= top) {
            if (direction == 0) {
                for (int i = left; i <= right; i++) {
                    lastX = i; lastY = bottom;
                }
                bottom++;
            } else if (direction == 1) {
                for (int i = bottom; i <= top; i++) {
                    lastX = right; lastY = i;
                }
                right--;
            } else if (direction == 2) {
                for (int i = right; i >= left; i--) {
                    lastX = i; lastY = top;
                }
                top--;
            } else {
                for (int i = top; i >= bottom; i--) {
                    lastX = left; lastY = i;
                }
                left++;
            }

            direction = (direction + 1) % 4;
        }

        System.out.println(lastX + " " + lastY);
    }
}
'''
            }
        ]
    },
    "30803": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 수도꼭지 관리 - 열린 수도꼭지들의 물 합계
import sys
input = sys.stdin.readline

def solve():
    N = int(input())
    A = list(map(int, input().split()))

    Q = int(input())

    # 초기 상태: 모든 수도꼭지 열림
    is_open = [True] * N
    total = sum(A)

    results = [total]

    for _ in range(Q):
        query = list(map(int, input().split()))
        if query[0] == 1:
            i, x = query[1] - 1, query[2]
            if is_open[i]:
                total -= A[i]
                total += x
            A[i] = x
        else:  # query[0] == 2
            i = query[1] - 1
            if is_open[i]:
                total -= A[i]
                is_open[i] = False
            else:
                total += A[i]
                is_open[i] = True

        results.append(total)

    print('\\n'.join(map(str, results)))

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

    vector<long long> A(N);
    vector<bool> isOpen(N, true);
    long long total = 0;

    for (int i = 0; i < N; i++) {
        cin >> A[i];
        total += A[i];
    }

    int Q;
    cin >> Q;

    cout << total << "\\n";

    while (Q--) {
        int op;
        cin >> op;

        if (op == 1) {
            int i;
            long long x;
            cin >> i >> x;
            i--;
            if (isOpen[i]) {
                total -= A[i];
                total += x;
            }
            A[i] = x;
        } else {
            int i;
            cin >> i;
            i--;
            if (isOpen[i]) {
                total -= A[i];
                isOpen[i] = false;
            } else {
                total += A[i];
                isOpen[i] = true;
            }
        }

        cout << total << "\\n";
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

        int N = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        long[] A = new long[N];
        boolean[] isOpen = new boolean[N];
        long total = 0;

        for (int i = 0; i < N; i++) {
            A[i] = Long.parseLong(st.nextToken());
            isOpen[i] = true;
            total += A[i];
        }

        int Q = Integer.parseInt(br.readLine().trim());
        sb.append(total).append("\\n");

        while (Q-- > 0) {
            st = new StringTokenizer(br.readLine());
            int op = Integer.parseInt(st.nextToken());

            if (op == 1) {
                int i = Integer.parseInt(st.nextToken()) - 1;
                long x = Long.parseLong(st.nextToken());
                if (isOpen[i]) {
                    total -= A[i];
                    total += x;
                }
                A[i] = x;
            } else {
                int i = Integer.parseInt(st.nextToken()) - 1;
                if (isOpen[i]) {
                    total -= A[i];
                    isOpen[i] = false;
                } else {
                    total += A[i];
                    isOpen[i] = true;
                }
            }

            sb.append(total).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "12348": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 분해합의 생성자 찾기 - N의 가장 작은 생성자
# M + M의 각 자릿수 합 = N
# M의 범위: N - 9*자릿수 ~ N-1

def solve():
    N = int(input())

    # 최대 자릿수: 19 (10^18)
    max_digits = 19

    # 탐색 범위
    start = max(1, N - 9 * max_digits)

    for M in range(start, N):
        digit_sum = sum(int(d) for d in str(M))
        if M + digit_sum == N:
            print(M)
            return

    print(0)

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

    long long N;
    cin >> N;

    int maxDigits = 19;
    long long start = max(1LL, N - 9 * maxDigits);

    for (long long M = start; M < N; M++) {
        long long temp = M;
        long long digitSum = 0;
        while (temp > 0) {
            digitSum += temp % 10;
            temp /= 10;
        }
        if (M + digitSum == N) {
            cout << M << endl;
            return 0;
        }
    }

    cout << 0 << endl;
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

        int maxDigits = 19;
        long start = Math.max(1L, N - 9 * maxDigits);

        for (long M = start; M < N; M++) {
            long temp = M;
            long digitSum = 0;
            while (temp > 0) {
                digitSum += temp % 10;
                temp /= 10;
            }
            if (M + digitSum == N) {
                System.out.println(M);
                return;
            }
        }

        System.out.println(0);
    }
}
'''
            }
        ]
    },
    "1569": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 정사각형으로 모든 점 가리기 - 변에 점이 놓여야 함
def solve():
    N = int(input())
    points = []
    for _ in range(N):
        x, y = map(int, input().split())
        points.append((x, y))

    if N == 1:
        print(0)
        return

    # 모든 점이 정사각형 변 위에 있어야 함
    # 정사각형은 x축, y축에 평행

    # 가능한 변의 길이 후보
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # 변의 길이는 적어도 max(max_x - min_x, max_y - min_y)
    side = max(max_x - min_x, max_y - min_y)

    # 확인: 모든 점이 변 위에 있는지
    # 정사각형: (min_x, min_y) ~ (min_x + side, min_y + side)
    # 점 (x, y)가 변 위: x == min_x or x == min_x + side or y == min_y or y == min_y + side

    def check(sx, sy, s):
        for x, y in points:
            on_edge = (x == sx or x == sx + s or y == sy or y == sy + s)
            inside = (sx <= x <= sx + s and sy <= y <= sy + s)
            if not (on_edge and inside):
                return False
        return True

    # 정사각형 위치 탐색
    for sx in [min_x, max_x - side]:
        for sy in [min_y, max_y - side]:
            if check(sx, sy, side):
                print(side)
                return

    print(-1)

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

    vector<int> xs(N), ys(N);
    for (int i = 0; i < N; i++) {
        cin >> xs[i] >> ys[i];
    }

    if (N == 1) {
        cout << 0 << endl;
        return 0;
    }

    int minX = *min_element(xs.begin(), xs.end());
    int maxX = *max_element(xs.begin(), xs.end());
    int minY = *min_element(ys.begin(), ys.end());
    int maxY = *max_element(ys.begin(), ys.end());

    int side = max(maxX - minX, maxY - minY);

    auto check = [&](int sx, int sy, int s) {
        for (int i = 0; i < N; i++) {
            int x = xs[i], y = ys[i];
            bool onEdge = (x == sx || x == sx + s || y == sy || y == sy + s);
            bool inside = (sx <= x && x <= sx + s && sy <= y && y <= sy + s);
            if (!(onEdge && inside)) return false;
        }
        return true;
    };

    vector<int> sxs = {minX, maxX - side};
    vector<int> sys = {minY, maxY - side};

    for (int sx : sxs) {
        for (int sy : sys) {
            if (check(sx, sy, side)) {
                cout << side << endl;
                return 0;
            }
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
        int N = sc.nextInt();

        int[] xs = new int[N];
        int[] ys = new int[N];

        for (int i = 0; i < N; i++) {
            xs[i] = sc.nextInt();
            ys[i] = sc.nextInt();
        }

        if (N == 1) {
            System.out.println(0);
            return;
        }

        int minX = Arrays.stream(xs).min().getAsInt();
        int maxX = Arrays.stream(xs).max().getAsInt();
        int minY = Arrays.stream(ys).min().getAsInt();
        int maxY = Arrays.stream(ys).max().getAsInt();

        int side = Math.max(maxX - minX, maxY - minY);

        int[] sxs = {minX, maxX - side};
        int[] sys = {minY, maxY - side};

        for (int sx : sxs) {
            for (int sy : sys) {
                boolean valid = true;
                for (int i = 0; i < N; i++) {
                    int x = xs[i], y = ys[i];
                    boolean onEdge = (x == sx || x == sx + side || y == sy || y == sy + side);
                    boolean inside = (sx <= x && x <= sx + side && sy <= y && y <= sy + side);
                    if (!(onEdge && inside)) {
                        valid = false;
                        break;
                    }
                }
                if (valid) {
                    System.out.println(side);
                    return;
                }
            }
        }

        System.out.println(-1);
    }
}
'''
            }
        ]
    },
    "9239": {
        "solutions": [
            {
                "language": "python",
                "code": '''# X를 곱하면 첫 자리를 맨 뒤로 보낸 수가 되는 수 찾기
from decimal import Decimal, getcontext
getcontext().prec = 50

def solve():
    X = Decimal(input().strip())

    results = []

    # n * X = 첫 자리를 맨 뒤로 보낸 수
    # n = d1 * 10^(k-1) + rest (k자리 수, 첫 자리 d1)
    # result = rest * 10 + d1

    for d1 in range(1, 10):  # 첫 자리
        for k in range(1, 9):  # 자릿수 (1 ~ 8)
            # n = d1 * 10^(k-1) + rest
            # n * X = rest * 10 + d1
            # (d1 * 10^(k-1) + rest) * X = rest * 10 + d1
            # d1 * 10^(k-1) * X + rest * X = rest * 10 + d1
            # rest * (X - 10) = d1 - d1 * 10^(k-1) * X
            # rest = d1 * (1 - 10^(k-1) * X) / (X - 10)

            power = Decimal(10) ** (k - 1)
            numerator = d1 * (1 - power * X)
            denominator = X - 10

            if denominator == 0:
                continue

            rest = numerator / denominator

            # rest는 0 이상 10^(k-1) 미만 정수
            if rest < 0 or rest >= power:
                continue

            rest_int = int(rest)
            if Decimal(rest_int) != rest:
                continue

            n = d1 * int(power) + rest_int
            expected = rest_int * 10 + d1

            # 검증
            if n * X == expected and n < 10**8:
                results.append(n)

    if results:
        results.sort()
        for r in results:
            print(r)
    else:
        print("No solution")

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <iomanip>
using namespace std;

int main() {
    double X;
    cin >> X;

    vector<long long> results;

    for (int d1 = 1; d1 <= 9; d1++) {
        for (int k = 1; k <= 8; k++) {
            long long power = 1;
            for (int i = 0; i < k - 1; i++) power *= 10;

            double numerator = d1 * (1.0 - power * X);
            double denominator = X - 10.0;

            if (abs(denominator) < 1e-10) continue;

            double rest_d = numerator / denominator;

            if (rest_d < -0.5 || rest_d >= power) continue;

            long long rest = (long long)round(rest_d);
            if (rest < 0 || rest >= power) continue;

            long long n = d1 * power + rest;
            long long expected = rest * 10 + d1;

            // 검증 (부동소수점 오차 고려)
            if (abs((double)n * X - expected) < 1e-6 && n < 100000000) {
                results.push_back(n);
            }
        }
    }

    if (results.empty()) {
        cout << "No solution" << endl;
    } else {
        sort(results.begin(), results.end());
        results.erase(unique(results.begin(), results.end()), results.end());
        for (long long r : results) {
            cout << r << endl;
        }
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.util.*;
import java.math.BigDecimal;
import java.math.RoundingMode;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        BigDecimal X = new BigDecimal(sc.next());

        Set<Long> resultSet = new TreeSet<>();

        for (int d1 = 1; d1 <= 9; d1++) {
            for (int k = 1; k <= 8; k++) {
                long power = 1;
                for (int i = 0; i < k - 1; i++) power *= 10;

                BigDecimal powerBD = new BigDecimal(power);
                BigDecimal d1BD = new BigDecimal(d1);

                BigDecimal numerator = d1BD.multiply(BigDecimal.ONE.subtract(powerBD.multiply(X)));
                BigDecimal denominator = X.subtract(new BigDecimal(10));

                if (denominator.compareTo(BigDecimal.ZERO) == 0) continue;

                BigDecimal restBD = numerator.divide(denominator, 10, RoundingMode.HALF_UP);

                if (restBD.compareTo(BigDecimal.ZERO) < 0 || restBD.compareTo(powerBD) >= 0) continue;

                long rest = restBD.setScale(0, RoundingMode.HALF_UP).longValue();
                if (rest < 0 || rest >= power) continue;

                long n = d1 * power + rest;
                long expected = rest * 10 + d1;

                BigDecimal nBD = new BigDecimal(n);
                BigDecimal product = nBD.multiply(X);
                BigDecimal expectedBD = new BigDecimal(expected);

                if (product.subtract(expectedBD).abs().compareTo(new BigDecimal("0.000001")) < 0 && n < 100000000) {
                    resultSet.add(n);
                }
            }
        }

        if (resultSet.isEmpty()) {
            System.out.println("No solution");
        } else {
            for (long r : resultSet) {
                System.out.println(r);
            }
        }
    }
}
'''
            }
        ]
    },
    "14600": {
        "solutions": [
            {
                "language": "python",
                "code": '''# ㄱ자 타일로 바닥 채우기 (2^K x 2^K)
def solve():
    K = int(input())
    x, y = map(int, input().split())

    size = 2 ** K
    grid = [[0] * size for _ in range(size)]

    # 배수구 위치 (1-indexed -> 0-indexed, y축 반전)
    drain_x = x - 1
    drain_y = size - y

    grid[drain_y][drain_x] = -1

    tile_num = [0]

    def fill(r, c, sz, dr, dc):
        """(r, c)에서 시작하는 sz x sz 영역을 채움. (dr, dc)는 이미 채워진 칸"""
        if sz == 1:
            return

        tile_num[0] += 1
        num = tile_num[0]

        half = sz // 2
        mid_r = r + half
        mid_c = c + half

        # 4개의 사분면 중 이미 채워진 칸 제외하고 중앙에 ㄱ자 타일 배치
        for (nr, nc) in [(r, c), (r, c + half), (r + half, c), (r + half, c + half)]:
            # 이 사분면에 이미 채워진 칸이 있는지 확인
            has_filled = False
            for rr in range(nr, nr + half):
                for cc in range(nc, nc + half):
                    if grid[rr][cc] != 0:
                        has_filled = True
                        break
                if has_filled:
                    break

            if not has_filled:
                # 중앙 근처에 타일 배치
                if nr == r and nc == c:
                    grid[mid_r - 1][mid_c - 1] = num
                elif nr == r and nc == c + half:
                    grid[mid_r - 1][mid_c] = num
                elif nr == r + half and nc == c:
                    grid[mid_r][mid_c - 1] = num
                else:
                    grid[mid_r][mid_c] = num

        # 재귀
        for (nr, nc) in [(r, c), (r, c + half), (r + half, c), (r + half, c + half)]:
            # 이 사분면의 채워진 칸 찾기
            filled_r, filled_c = -1, -1
            for rr in range(nr, nr + half):
                for cc in range(nc, nc + half):
                    if grid[rr][cc] != 0:
                        filled_r, filled_c = rr, cc
                        break
                if filled_r != -1:
                    break
            fill(nr, nc, half, filled_r, filled_c)

    fill(0, 0, size, drain_y, drain_x)

    for row in grid:
        print(' '.join(map(str, row)))

solve()
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
using namespace std;

int grid[4][4];
int tileNum = 0;

void fill(int r, int c, int sz, int dr, int dc) {
    if (sz == 1) return;

    tileNum++;
    int num = tileNum;
    int half = sz / 2;
    int midR = r + half;
    int midC = c + half;

    // 4개 사분면
    int sectors[4][2] = {{r, c}, {r, c + half}, {r + half, c}, {r + half, c + half}};

    for (int s = 0; s < 4; s++) {
        int nr = sectors[s][0], nc = sectors[s][1];
        bool hasFilled = false;
        for (int rr = nr; rr < nr + half && !hasFilled; rr++) {
            for (int cc = nc; cc < nc + half && !hasFilled; cc++) {
                if (grid[rr][cc] != 0) hasFilled = true;
            }
        }

        if (!hasFilled) {
            if (nr == r && nc == c) grid[midR - 1][midC - 1] = num;
            else if (nr == r && nc == c + half) grid[midR - 1][midC] = num;
            else if (nr == r + half && nc == c) grid[midR][midC - 1] = num;
            else grid[midR][midC] = num;
        }
    }

    for (int s = 0; s < 4; s++) {
        int nr = sectors[s][0], nc = sectors[s][1];
        int filledR = -1, filledC = -1;
        for (int rr = nr; rr < nr + half && filledR == -1; rr++) {
            for (int cc = nc; cc < nc + half && filledR == -1; cc++) {
                if (grid[rr][cc] != 0) {
                    filledR = rr; filledC = cc;
                }
            }
        }
        fill(nr, nc, half, filledR, filledC);
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int K;
    cin >> K;

    int x, y;
    cin >> x >> y;

    int size = 1 << K;

    int drainX = x - 1;
    int drainY = size - y;

    grid[drainY][drainX] = -1;

    fill(0, 0, size, drainY, drainX);

    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            if (j > 0) cout << " ";
            cout << grid[i][j];
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

public class Main {
    static int[][] grid;
    static int tileNum = 0;

    static void fill(int r, int c, int sz, int dr, int dc) {
        if (sz == 1) return;

        tileNum++;
        int num = tileNum;
        int half = sz / 2;
        int midR = r + half;
        int midC = c + half;

        int[][] sectors = {{r, c}, {r, c + half}, {r + half, c}, {r + half, c + half}};

        for (int[] sector : sectors) {
            int nr = sector[0], nc = sector[1];
            boolean hasFilled = false;
            outer:
            for (int rr = nr; rr < nr + half; rr++) {
                for (int cc = nc; cc < nc + half; cc++) {
                    if (grid[rr][cc] != 0) {
                        hasFilled = true;
                        break outer;
                    }
                }
            }

            if (!hasFilled) {
                if (nr == r && nc == c) grid[midR - 1][midC - 1] = num;
                else if (nr == r && nc == c + half) grid[midR - 1][midC] = num;
                else if (nr == r + half && nc == c) grid[midR][midC - 1] = num;
                else grid[midR][midC] = num;
            }
        }

        for (int[] sector : sectors) {
            int nr = sector[0], nc = sector[1];
            int filledR = -1, filledC = -1;
            outer:
            for (int rr = nr; rr < nr + half; rr++) {
                for (int cc = nc; cc < nc + half; cc++) {
                    if (grid[rr][cc] != 0) {
                        filledR = rr; filledC = cc;
                        break outer;
                    }
                }
            }
            fill(nr, nc, half, filledR, filledC);
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int K = sc.nextInt();
        int x = sc.nextInt();
        int y = sc.nextInt();

        int size = 1 << K;
        grid = new int[size][size];

        int drainX = x - 1;
        int drainY = size - y;
        grid[drainY][drainX] = -1;

        fill(0, 0, size, drainY, drainX);

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                if (j > 0) sb.append(" ");
                sb.append(grid[i][j]);
            }
            sb.append("\\n");
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
