#!/usr/bin/env python3
"""
Generate solutions for 10 medium difficulty Baekjoon problems with empty solutions.
"""

import json
import fcntl
import os

def get_solutions():
    """Return solutions for the 10 medium problems."""

    solutions = {}

    # Problem 24040: 예쁜 케이크 (Pretty Cake)
    # 조건: 케이크 둘레가 3의 배수여야 함 (빨/초/흰 반복)
    # 둘레 = 2*(a+b) where a*b = N, 높이=1
    # 2*(a+b)가 3의 배수 => a+b가 3의 배수
    solutions["baekjoon_24040"] = [
        {
            "language": "python",
            "code": '''# 백준 24040: 예쁜 케이크
# N = a * b (a, b는 양의 정수)
# 둘레 = 2*(a+b)가 3의 배수여야 함
# 즉, (a+b)가 3의 배수여야 함
import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    N = int(input())
    found = False
    # N의 약수 쌍 (a, b)를 찾아 a+b가 3의 배수인지 확인
    i = 1
    while i * i <= N:
        if N % i == 0:
            a = i
            b = N // i
            if (a + b) % 3 == 0:
                found = True
                break
        i += 1
    print("TAK" if found else "NIE")
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 24040: 예쁜 케이크
// N = a * b (a, b는 양의 정수)
// 둘레 = 2*(a+b)가 3의 배수여야 함
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine());
        while (T-- > 0) {
            long N = Long.parseLong(br.readLine());
            boolean found = false;

            // N의 약수 쌍 (a, b)를 찾아 a+b가 3의 배수인지 확인
            for (long i = 1; i * i <= N; i++) {
                if (N % i == 0) {
                    long a = i;
                    long b = N / i;
                    if ((a + b) % 3 == 0) {
                        found = true;
                        break;
                    }
                }
            }
            sb.append(found ? "TAK" : "NIE").append("\\n");
        }
        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

// 백준 24040: 예쁜 케이크
// N = a * b (a, b는 양의 정수)
// 둘레 = 2*(a+b)가 3의 배수여야 함
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        long long N;
        cin >> N;
        bool found = false;

        // N의 약수 쌍 (a, b)를 찾아 a+b가 3의 배수인지 확인
        for (long long i = 1; i * i <= N; i++) {
            if (N % i == 0) {
                long long a = i;
                long long b = N / i;
                if ((a + b) % 3 == 0) {
                    found = true;
                    break;
                }
            }
        }
        cout << (found ? "TAK" : "NIE") << "\\n";
    }

    return 0;
}
'''
        }
    ]

    # Problem 2790: F7
    # 마지막 레이싱 점수: 1등=N점, 2등=N-1점, ..., 꼴등=1점
    # 각 드라이버가 우승 가능한지 확인
    solutions["baekjoon_2790"] = [
        {
            "language": "python",
            "code": '''# 백준 2790: F7
# 마지막 레이싱에서 1등=N점, 꼴등=1점
# 각 드라이버가 우승 가능한지 확인
import sys
input = sys.stdin.readline

N = int(input())
scores = []
for _ in range(N):
    scores.append(int(input()))

# 점수 내림차순 정렬
scores.sort(reverse=True)

count = 0
for i in range(N):
    # i번째 드라이버가 1등(N점)을 받고, 현재 1등이 꼴등(i+1점)을 받는 경우
    # i번째 드라이버 최대 점수: scores[i] + N
    # 현재 1등 최소 점수: scores[0] + (i + 1)
    if scores[i] + N >= scores[0] + (i + 1):
        count += 1
    else:
        break

print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 2790: F7
// 마지막 레이싱에서 1등=N점, 꼴등=1점
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine());
        int[] scores = new int[N];

        for (int i = 0; i < N; i++) {
            scores[i] = Integer.parseInt(br.readLine());
        }

        // 점수 내림차순 정렬
        Arrays.sort(scores);
        for (int i = 0; i < N / 2; i++) {
            int temp = scores[i];
            scores[i] = scores[N - 1 - i];
            scores[N - 1 - i] = temp;
        }

        int count = 0;
        for (int i = 0; i < N; i++) {
            // i번째 드라이버가 1등(N점), 현재 1등이 (i+1)점을 받는 경우
            if (scores[i] + N >= scores[0] + (i + 1)) {
                count++;
            } else {
                break;
            }
        }

        System.out.println(count);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <algorithm>
#include <vector>
using namespace std;

// 백준 2790: F7
// 마지막 레이싱에서 1등=N점, 꼴등=1점
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    vector<int> scores(N);
    for (int i = 0; i < N; i++) {
        cin >> scores[i];
    }

    // 점수 내림차순 정렬
    sort(scores.begin(), scores.end(), greater<int>());

    int count = 0;
    for (int i = 0; i < N; i++) {
        // i번째 드라이버가 1등(N점), 현재 1등이 (i+1)점을 받는 경우
        if (scores[i] + N >= scores[0] + (i + 1)) {
            count++;
        } else {
            break;
        }
    }

    cout << count << "\\n";

    return 0;
}
'''
        }
    ]

    # Problem 1835: 카드
    # 역으로 시뮬레이션하여 원래 카드 순서 찾기
    solutions["baekjoon_1835"] = [
        {
            "language": "python",
            "code": '''# 백준 1835: 카드
# 역으로 시뮬레이션하여 원래 카드 순서 찾기
from collections import deque

N = int(input())
dq = deque()

# N부터 1까지 역순으로 카드를 놓으면서 역연산 수행
for i in range(N, 0, -1):
    # 카드 i를 앞에 놓음
    dq.appendleft(i)
    # i번 역연산: 뒤에서 앞으로 i번 이동
    for _ in range(i):
        dq.appendleft(dq.pop())

print(*dq)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 1835: 카드
// 역으로 시뮬레이션하여 원래 카드 순서 찾기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int N = Integer.parseInt(br.readLine());
        ArrayDeque<Integer> dq = new ArrayDeque<>();

        // N부터 1까지 역순으로 카드를 놓으면서 역연산 수행
        for (int i = N; i >= 1; i--) {
            // 카드 i를 앞에 놓음
            dq.addFirst(i);
            // i번 역연산: 뒤에서 앞으로 i번 이동
            for (int j = 0; j < i; j++) {
                dq.addFirst(dq.pollLast());
            }
        }

        for (int card : dq) {
            sb.append(card).append(" ");
        }
        System.out.println(sb.toString().trim());
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <deque>
using namespace std;

// 백준 1835: 카드
// 역으로 시뮬레이션하여 원래 카드 순서 찾기
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    deque<int> dq;

    // N부터 1까지 역순으로 카드를 놓으면서 역연산 수행
    for (int i = N; i >= 1; i--) {
        // 카드 i를 앞에 놓음
        dq.push_front(i);
        // i번 역연산: 뒤에서 앞으로 i번 이동
        for (int j = 0; j < i; j++) {
            dq.push_front(dq.back());
            dq.pop_back();
        }
    }

    for (int i = 0; i < N; i++) {
        cout << dq[i];
        if (i < N - 1) cout << " ";
    }
    cout << "\\n";

    return 0;
}
'''
        }
    ]

    # Problem 2865: 나는 위대한 슈퍼스타K
    # 각 참가자의 최고 점수만 고려하여 상위 K명 선택
    solutions["baekjoon_2865"] = [
        {
            "language": "python",
            "code": '''# 백준 2865: 나는 위대한 슈퍼스타K
# 각 참가자의 최고 점수만 고려하여 상위 K명 선택
import sys
input = sys.stdin.readline

N, M, K = map(int, input().split())

# 각 참가자별 최고 점수 저장
max_scores = [0.0] * (N + 1)

for _ in range(M):
    line = input().split()
    for j in range(0, len(line), 2):
        idx = int(line[j])
        score = float(line[j + 1])
        max_scores[idx] = max(max_scores[idx], score)

# 최고 점수 기준 내림차순 정렬 후 상위 K명 합계
max_scores.sort(reverse=True)
result = sum(max_scores[:K])

# 소수점 첫째 자리까지 출력
print(f"{result:.1f}")
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 2865: 나는 위대한 슈퍼스타K
// 각 참가자의 최고 점수만 고려하여 상위 K명 선택
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        // 각 참가자별 최고 점수 저장
        double[] maxScores = new double[N + 1];

        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            while (st.hasMoreTokens()) {
                int idx = Integer.parseInt(st.nextToken());
                double score = Double.parseDouble(st.nextToken());
                maxScores[idx] = Math.max(maxScores[idx], score);
            }
        }

        // 최고 점수 기준 내림차순 정렬
        Double[] scores = new Double[N];
        for (int i = 1; i <= N; i++) {
            scores[i - 1] = maxScores[i];
        }
        Arrays.sort(scores, Collections.reverseOrder());

        // 상위 K명 합계
        double result = 0;
        for (int i = 0; i < K; i++) {
            result += scores[i];
        }

        System.out.printf("%.1f%n", result);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <algorithm>
#include <vector>
#include <iomanip>
using namespace std;

// 백준 2865: 나는 위대한 슈퍼스타K
// 각 참가자의 최고 점수만 고려하여 상위 K명 선택
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M, K;
    cin >> N >> M >> K;

    // 각 참가자별 최고 점수 저장
    vector<double> maxScores(N + 1, 0.0);

    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            int idx;
            double score;
            cin >> idx >> score;
            maxScores[idx] = max(maxScores[idx], score);
        }
    }

    // 최고 점수 기준 내림차순 정렬
    vector<double> scores(maxScores.begin() + 1, maxScores.end());
    sort(scores.begin(), scores.end(), greater<double>());

    // 상위 K명 합계
    double result = 0;
    for (int i = 0; i < K; i++) {
        result += scores[i];
    }

    cout << fixed << setprecision(1) << result << "\\n";

    return 0;
}
'''
        }
    ]

    # Problem 2168: 타일 위의 대각선
    # 대각선이 지나는 타일 수 = x + y - gcd(x, y)
    solutions["baekjoon_2168"] = [
        {
            "language": "python",
            "code": '''# 백준 2168: 타일 위의 대각선
# 대각선이 지나는 타일 수 = x + y - gcd(x, y)
import math

x, y = map(int, input().split())
print(x + y - math.gcd(x, y))
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 2168: 타일 위의 대각선
// 대각선이 지나는 타일 수 = x + y - gcd(x, y)
public class Main {
    public static long gcd(long a, long b) {
        while (b != 0) {
            long temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long x = Long.parseLong(st.nextToken());
        long y = Long.parseLong(st.nextToken());

        System.out.println(x + y - gcd(x, y));
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

// 백준 2168: 타일 위의 대각선
// 대각선이 지나는 타일 수 = x + y - gcd(x, y)
long long gcd(long long a, long long b) {
    while (b != 0) {
        long long temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    long long x, y;
    cin >> x >> y;

    cout << x + y - gcd(x, y) << "\\n";

    return 0;
}
'''
        }
    ]

    # Problem 14653: 너의 이름은
    # Q번째 메시지 전에 활동한 사람과 읽지 않은 수를 비교
    solutions["baekjoon_14653"] = [
        {
            "language": "python",
            "code": '''# 백준 14653: 너의 이름은
# Q번째 메시지를 읽지 않은 사람 찾기
import sys
input = sys.stdin.readline

N, K, Q = map(int, input().split())

messages = []
for _ in range(K):
    line = input().split()
    unread = int(line[0])
    sender = line[1]
    messages.append((unread, sender))

# Q번째 메시지 이후에 활동한 사람들 (메시지를 보내거나)
active_after_Q = set()
for i in range(Q, K):
    active_after_Q.add(messages[i][1])

# Q번째 메시지의 읽지 않은 수
unread_Q = messages[Q - 1][0]

# 모든 사람 집합
all_people = set(chr(ord('A') + i) for i in range(N))

# Q번째 메시지 발신자는 당연히 읽음 처리
sender_Q = messages[Q - 1][1]

# Q번째 메시지 이후 활동한 사람들은 Q번째 메시지를 읽은 것
# 읽지 않은 사람 = 전체 - Q번째 이후 활동한 사람 - Q번째 발신자
candidates = all_people - active_after_Q - {sender_Q}

# 읽지 않은 사람 수가 unread_Q와 같아야 함
if len(candidates) == unread_Q:
    result = sorted(candidates)
    print(' '.join(result))
else:
    print(-1)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 14653: 너의 이름은
// Q번째 메시지를 읽지 않은 사람 찾기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());
        int Q = Integer.parseInt(st.nextToken());

        int[] unread = new int[K];
        char[] sender = new char[K];

        for (int i = 0; i < K; i++) {
            st = new StringTokenizer(br.readLine());
            unread[i] = Integer.parseInt(st.nextToken());
            sender[i] = st.nextToken().charAt(0);
        }

        // Q번째 메시지 이후에 활동한 사람들
        Set<Character> activeAfterQ = new HashSet<>();
        for (int i = Q; i < K; i++) {
            activeAfterQ.add(sender[i]);
        }

        // Q번째 메시지의 읽지 않은 수
        int unreadQ = unread[Q - 1];
        char senderQ = sender[Q - 1];

        // 읽지 않은 사람 후보
        List<Character> candidates = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            char person = (char)('A' + i);
            if (person != senderQ && !activeAfterQ.contains(person)) {
                candidates.add(person);
            }
        }

        if (candidates.size() == unreadQ) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < candidates.size(); i++) {
                sb.append(candidates.get(i));
                if (i < candidates.size() - 1) sb.append(" ");
            }
            System.out.println(sb);
        } else {
            System.out.println(-1);
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <set>
#include <vector>
using namespace std;

// 백준 14653: 너의 이름은
// Q번째 메시지를 읽지 않은 사람 찾기
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int N, K, Q;
    cin >> N >> K >> Q;

    vector<int> unread(K);
    vector<char> sender(K);

    for (int i = 0; i < K; i++) {
        cin >> unread[i] >> sender[i];
    }

    // Q번째 메시지 이후에 활동한 사람들
    set<char> activeAfterQ;
    for (int i = Q; i < K; i++) {
        activeAfterQ.insert(sender[i]);
    }

    // Q번째 메시지의 읽지 않은 수
    int unreadQ = unread[Q - 1];
    char senderQ = sender[Q - 1];

    // 읽지 않은 사람 후보
    vector<char> candidates;
    for (int i = 0; i < N; i++) {
        char person = 'A' + i;
        if (person != senderQ && activeAfterQ.find(person) == activeAfterQ.end()) {
            candidates.push_back(person);
        }
    }

    if ((int)candidates.size() == unreadQ) {
        for (int i = 0; i < (int)candidates.size(); i++) {
            cout << candidates[i];
            if (i < (int)candidates.size() - 1) cout << " ";
        }
        cout << "\\n";
    } else {
        cout << -1 << "\\n";
    }

    return 0;
}
'''
        }
    ]

    # Problem 12755: 수면 장애
    # N번째 숫자 찾기 (1부터 이어붙인 숫자열)
    solutions["baekjoon_12755"] = [
        {
            "language": "python",
            "code": '''# 백준 12755: 수면 장애
# N번째 숫자 찾기 (1부터 이어붙인 숫자열에서)
N = int(input())

# 각 자릿수별 숫자 개수와 총 자릿수
# 1자리: 1-9 (9개, 9자리)
# 2자리: 10-99 (90개, 180자리)
# k자리: 9*10^(k-1)개, k*9*10^(k-1)자리

digit = 1  # 현재 자릿수
count = 9  # 해당 자릿수 숫자 개수
start = 1  # 해당 자릿수 시작 숫자

while N > digit * count:
    N -= digit * count
    digit += 1
    count *= 10
    start *= 10

# N번째 숫자가 속한 숫자 찾기
# (N-1) // digit : 시작 숫자로부터 몇 번째 숫자인지
# (N-1) % digit : 해당 숫자에서 몇 번째 자리인지
num = start + (N - 1) // digit
idx = (N - 1) % digit

print(str(num)[idx])
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;

// 백준 12755: 수면 장애
// N번째 숫자 찾기 (1부터 이어붙인 숫자열에서)
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        long N = Long.parseLong(br.readLine());

        // 각 자릿수별 숫자 개수와 총 자릿수
        int digit = 1;
        long count = 9;
        long start = 1;

        while (N > digit * count) {
            N -= digit * count;
            digit++;
            count *= 10;
            start *= 10;
        }

        // N번째 숫자가 속한 숫자 찾기
        long num = start + (N - 1) / digit;
        int idx = (int)((N - 1) % digit);

        System.out.println(String.valueOf(num).charAt(idx));
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
using namespace std;

// 백준 12755: 수면 장애
// N번째 숫자 찾기 (1부터 이어붙인 숫자열에서)
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    long long N;
    cin >> N;

    // 각 자릿수별 숫자 개수와 총 자릿수
    int digit = 1;
    long long count = 9;
    long long start = 1;

    while (N > digit * count) {
        N -= digit * count;
        digit++;
        count *= 10;
        start *= 10;
    }

    // N번째 숫자가 속한 숫자 찾기
    long long num = start + (N - 1) / digit;
    int idx = (N - 1) % digit;

    cout << to_string(num)[idx] << "\\n";

    return 0;
}
'''
        }
    ]

    # Problem 14754: Pizza Boxes
    # 각 행과 열의 최대값을 제외한 나머지 박스 제거 가능
    solutions["baekjoon_14754"] = [
        {
            "language": "python",
            "code": '''# 백준 14754: Pizza Boxes
# 각 행과 열의 최대값을 제외한 나머지 박스 제거 가능
import sys
input = sys.stdin.readline

R, C = map(int, input().split())
grid = []
for _ in range(R):
    grid.append(list(map(int, input().split())))

# 각 행의 최대값과 각 열의 최대값 찾기
row_max = [max(row) for row in grid]
col_max = [max(grid[i][j] for i in range(R)) for j in range(C)]

# 전체 합
total = sum(sum(row) for row in grid)

# 제거할 수 없는 박스들의 합 (각 행/열의 최대값 위치)
# 최대값인 위치는 유지해야 함
keep = 0
for i in range(R):
    for j in range(C):
        if grid[i][j] == row_max[i] or grid[i][j] == col_max[j]:
            keep += grid[i][j]

print(total - keep)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 14754: Pizza Boxes
// 각 행과 열의 최대값을 제외한 나머지 박스 제거 가능
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int R = Integer.parseInt(st.nextToken());
        int C = Integer.parseInt(st.nextToken());

        int[][] grid = new int[R][C];
        int[] rowMax = new int[R];
        int[] colMax = new int[C];

        for (int i = 0; i < R; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < C; j++) {
                grid[i][j] = Integer.parseInt(st.nextToken());
                rowMax[i] = Math.max(rowMax[i], grid[i][j]);
                colMax[j] = Math.max(colMax[j], grid[i][j]);
            }
        }

        long total = 0;
        long keep = 0;

        for (int i = 0; i < R; i++) {
            for (int j = 0; j < C; j++) {
                total += grid[i][j];
                if (grid[i][j] == rowMax[i] || grid[i][j] == colMax[j]) {
                    keep += grid[i][j];
                }
            }
        }

        System.out.println(total - keep);
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

// 백준 14754: Pizza Boxes
// 각 행과 열의 최대값을 제외한 나머지 박스 제거 가능
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int R, C;
    cin >> R >> C;

    vector<vector<int>> grid(R, vector<int>(C));
    vector<int> rowMax(R, 0);
    vector<int> colMax(C, 0);

    for (int i = 0; i < R; i++) {
        for (int j = 0; j < C; j++) {
            cin >> grid[i][j];
            rowMax[i] = max(rowMax[i], grid[i][j]);
            colMax[j] = max(colMax[j], grid[i][j]);
        }
    }

    long long total = 0;
    long long keep = 0;

    for (int i = 0; i < R; i++) {
        for (int j = 0; j < C; j++) {
            total += grid[i][j];
            if (grid[i][j] == rowMax[i] || grid[i][j] == colMax[j]) {
                keep += grid[i][j];
            }
        }
    }

    cout << total - keep << "\\n";

    return 0;
}
'''
        }
    ]

    # Problem 4335: 숫자 맞추기
    # 올리가 외친 수와 스탠의 답변이 모순인지 확인
    solutions["baekjoon_4335"] = [
        {
            "language": "python",
            "code": '''# 백준 4335: 숫자 맞추기
# 스탠이 거짓말을 했는지 확인
import sys
input = sys.stdin.readline

while True:
    line = input().strip()
    if line == "0":
        break

    guess = int(line)
    response = input().strip()

    low = 1   # 가능한 최소값
    high = 10 # 가능한 최대값
    honest = True

    while True:
        if response == "right on":
            if guess < low or guess > high:
                honest = False
            break
        elif response == "too high":
            if guess <= low:
                honest = False
                # 이후 입력 모두 소진
                while True:
                    line = input().strip()
                    if line == "0":
                        break
                    guess = int(line)
                    response = input().strip()
                    if response == "right on":
                        break
                break
            high = guess - 1
        elif response == "too low":
            if guess >= high:
                honest = False
                while True:
                    line = input().strip()
                    if line == "0":
                        break
                    guess = int(line)
                    response = input().strip()
                    if response == "right on":
                        break
                break
            low = guess + 1

        line = input().strip()
        if line == "0":
            break
        guess = int(line)
        response = input().strip()

    if honest:
        print("Stan may be honest")
    else:
        print("Stan is dishonest")
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;

// 백준 4335: 숫자 맞추기
// 스탠이 거짓말을 했는지 확인
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        while (true) {
            String line = br.readLine().trim();
            if (line.equals("0")) break;

            int guess = Integer.parseInt(line);
            String response = br.readLine().trim();

            int low = 1;
            int high = 10;
            boolean honest = true;

            while (true) {
                if (response.equals("right on")) {
                    if (guess < low || guess > high) {
                        honest = false;
                    }
                    break;
                } else if (response.equals("too high")) {
                    if (guess <= low) {
                        honest = false;
                        while (true) {
                            line = br.readLine().trim();
                            if (line.equals("0")) break;
                            response = br.readLine().trim();
                            if (response.equals("right on")) break;
                        }
                        break;
                    }
                    high = guess - 1;
                } else if (response.equals("too low")) {
                    if (guess >= high) {
                        honest = false;
                        while (true) {
                            line = br.readLine().trim();
                            if (line.equals("0")) break;
                            response = br.readLine().trim();
                            if (response.equals("right on")) break;
                        }
                        break;
                    }
                    low = guess + 1;
                }

                line = br.readLine().trim();
                if (line.equals("0")) break;
                guess = Integer.parseInt(line);
                response = br.readLine().trim();
            }

            sb.append(honest ? "Stan may be honest" : "Stan is dishonest").append("\\n");
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

// 백준 4335: 숫자 맞추기
// 스탠이 거짓말을 했는지 확인
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int guess;
    while (cin >> guess && guess != 0) {
        cin.ignore();
        string response;
        getline(cin, response);

        int low = 1;
        int high = 10;
        bool honest = true;

        while (true) {
            if (response == "right on") {
                if (guess < low || guess > high) {
                    honest = false;
                }
                break;
            } else if (response == "too high") {
                if (guess <= low) {
                    honest = false;
                    while (cin >> guess && guess != 0) {
                        cin.ignore();
                        getline(cin, response);
                        if (response == "right on") break;
                    }
                    break;
                }
                high = guess - 1;
            } else if (response == "too low") {
                if (guess >= high) {
                    honest = false;
                    while (cin >> guess && guess != 0) {
                        cin.ignore();
                        getline(cin, response);
                        if (response == "right on") break;
                    }
                    break;
                }
                low = guess + 1;
            }

            cin >> guess;
            if (guess == 0) break;
            cin.ignore();
            getline(cin, response);
        }

        cout << (honest ? "Stan may be honest" : "Stan is dishonest") << "\\n";
    }

    return 0;
}
'''
        }
    ]

    # Problem 22941: RPG 마스터 오명진
    # 용사가 마왕을 이길 수 있는지 시뮬레이션
    solutions["baekjoon_22941"] = [
        {
            "language": "python",
            "code": '''# 백준 22941: RPG 마스터 오명진
# 용사가 마왕을 이길 수 있는지 확인
import sys
input = sys.stdin.readline

hero_hp, hero_atk, boss_hp, boss_atk = map(int, input().split())
P, S = map(int, input().split())

# 용사가 마왕을 잡는데 필요한 턴 수
# 마왕 체력이 P 이하가 되면 S만큼 회복

# 스킬을 발동시키지 않고 잡는 경우
turns_no_skill = (boss_hp + hero_atk - 1) // hero_atk

# 스킬을 발동시키는 경우
# 마왕 체력을 1~P 사이로 만들고 그 다음 턴에 잡아야 함
# 스킬 발동 후 마왕 체력: boss_hp - k*hero_atk + S (1 <= boss_hp - k*hero_atk <= P)
# 조건: boss_hp - P <= k*hero_atk <= boss_hp - 1
# k = ceil((boss_hp - P) / hero_atk) ~ floor((boss_hp - 1) / hero_atk)

# 스킬 발동 후 한 번에 잡으려면
# boss_hp - k*hero_atk + S <= hero_atk (스킬 발동 후 남은 체력이 한 방에 죽음)
# 이 경우 총 턴 수 = k + 1

turns_with_skill = float('inf')
if P < boss_hp:
    # k*hero_atk가 boss_hp - P 이상, boss_hp - 1 이하여야 스킬 발동
    k_min = (boss_hp - P + hero_atk - 1) // hero_atk
    k_max = (boss_hp - 1) // hero_atk

    if k_min <= k_max:
        # 스킬 발동 후 체력 = boss_hp - k*hero_atk + S
        # 한 방에 잡으려면 이 값이 hero_atk 이하
        # 가장 유리한 건 k_max (체력을 최대한 깎고 스킬 발동)
        remaining = boss_hp - k_max * hero_atk + S
        if remaining <= hero_atk:
            turns_with_skill = k_max + 1
        else:
            # 스킬 발동 후 추가 턴 필요
            turns_with_skill = k_max + 1 + (remaining - hero_atk + hero_atk - 1) // hero_atk

hero_turns = min(turns_no_skill, turns_with_skill)

# 용사가 버틸 수 있는 턴 수 (용사가 공격 후 마왕이 공격하므로)
# 용사가 hero_turns번 공격하는 동안 마왕은 hero_turns - 1번 공격
boss_attacks = hero_turns - 1
hero_damage = boss_attacks * boss_atk

if hero_hp > hero_damage:
    print("Victory!")
else:
    print("gg")
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 22941: RPG 마스터 오명진
// 용사가 마왕을 이길 수 있는지 확인
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long heroHp = Long.parseLong(st.nextToken());
        long heroAtk = Long.parseLong(st.nextToken());
        long bossHp = Long.parseLong(st.nextToken());
        long bossAtk = Long.parseLong(st.nextToken());

        st = new StringTokenizer(br.readLine());
        long P = Long.parseLong(st.nextToken());
        long S = Long.parseLong(st.nextToken());

        // 스킬을 발동시키지 않고 잡는 경우
        long turnsNoSkill = (bossHp + heroAtk - 1) / heroAtk;

        // 스킬을 발동시키는 경우
        long turnsWithSkill = Long.MAX_VALUE;
        if (P < bossHp) {
            long kMin = (bossHp - P + heroAtk - 1) / heroAtk;
            long kMax = (bossHp - 1) / heroAtk;

            if (kMin <= kMax) {
                long remaining = bossHp - kMax * heroAtk + S;
                if (remaining <= heroAtk) {
                    turnsWithSkill = kMax + 1;
                } else {
                    turnsWithSkill = kMax + 1 + (remaining - heroAtk + heroAtk - 1) / heroAtk;
                }
            }
        }

        long heroTurns = Math.min(turnsNoSkill, turnsWithSkill);
        long bossAttacks = heroTurns - 1;
        long heroDamage = bossAttacks * bossAtk;

        if (heroHp > heroDamage) {
            System.out.println("Victory!");
        } else {
            System.out.println("gg");
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <algorithm>
using namespace std;

// 백준 22941: RPG 마스터 오명진
// 용사가 마왕을 이길 수 있는지 확인
int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    long long heroHp, heroAtk, bossHp, bossAtk;
    cin >> heroHp >> heroAtk >> bossHp >> bossAtk;

    long long P, S;
    cin >> P >> S;

    // 스킬을 발동시키지 않고 잡는 경우
    long long turnsNoSkill = (bossHp + heroAtk - 1) / heroAtk;

    // 스킬을 발동시키는 경우
    long long turnsWithSkill = 1e18;
    if (P < bossHp) {
        long long kMin = (bossHp - P + heroAtk - 1) / heroAtk;
        long long kMax = (bossHp - 1) / heroAtk;

        if (kMin <= kMax) {
            long long remaining = bossHp - kMax * heroAtk + S;
            if (remaining <= heroAtk) {
                turnsWithSkill = kMax + 1;
            } else {
                turnsWithSkill = kMax + 1 + (remaining - heroAtk + heroAtk - 1) / heroAtk;
            }
        }
    }

    long long heroTurns = min(turnsNoSkill, turnsWithSkill);
    long long bossAttacks = heroTurns - 1;
    long long heroDamage = bossAttacks * bossAtk;

    if (heroHp > heroDamage) {
        cout << "Victory!" << "\\n";
    } else {
        cout << "gg" << "\\n";
    }

    return 0;
}
'''
        }
    ]

    return solutions


def main():
    file_path = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

    # Read the JSON file with file locking
    with open(file_path, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # Get solutions
    solutions = get_solutions()

    # Problem indices (pre-computed)
    problem_indices = {
        "baekjoon_24040": 2224,
        "baekjoon_2790": 2225,
        "baekjoon_1835": 2244,
        "baekjoon_2865": 2252,
        "baekjoon_2168": 2258,
        "baekjoon_14653": 2263,
        "baekjoon_12755": 2264,
        "baekjoon_14754": 2272,
        "baekjoon_4335": 2284,
        "baekjoon_22941": 2289
    }

    # Update solutions
    updated_count = 0
    for problem_id, idx in problem_indices.items():
        if data[idx]['solutions'] == []:
            if problem_id in solutions:
                data[idx]['solutions'] = solutions[problem_id]
                updated_count += 1
                print(f"Updated: {problem_id} at index {idx}")
            else:
                print(f"Warning: No solution found for {problem_id}")
        else:
            print(f"Skipped (already has solutions): {problem_id}")

    # Write back with exclusive lock
    with open(file_path, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\nTotal updated: {updated_count} problems")


if __name__ == "__main__":
    main()
