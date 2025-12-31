#!/usr/bin/env python3
"""
10개의 medium 난이도 문제에 대한 솔루션을 생성하는 스크립트
"""

import json
import fcntl

# 솔루션 정의
SOLUTIONS = {
    "baekjoon_27162": [
        {
            "language": "python",
            "code": '''# 백준 27162: Yacht Dice
# 야찌 다이스 게임에서 최대 점수를 계산하는 문제
import sys
input = sys.stdin.readline

# 12개의 족보 사용 가능 여부 (Y/N)
available = input().strip()

# 고정된 주사위 3개
fixed = list(map(int, input().split()))

def calculate_score(dice):
    """주어진 5개 주사위로 얻을 수 있는 점수 계산"""
    scores = []
    cnt = [0] * 7  # 각 숫자의 개수
    for d in dice:
        cnt[d] += 1

    # Ones ~ Sixes (인덱스 0~5)
    for i in range(1, 7):
        scores.append(cnt[i] * i)

    total = sum(dice)

    # Four of a Kind (인덱스 6): 같은 눈 4개 이상이면 그 4개의 합
    four_kind = 0
    for i in range(1, 7):
        if cnt[i] >= 4:
            four_kind = i * 4
    scores.append(four_kind)

    # Full House (인덱스 7): 정확히 두 종류, 하나가 3개 하나가 2개
    full_house = 0
    kinds = sum(1 for c in cnt if c > 0)
    if kinds == 2:
        has_three = any(c == 3 for c in cnt)
        has_two = any(c == 2 for c in cnt)
        if has_three and has_two:
            full_house = total
    scores.append(full_house)

    # Little Straight (인덱스 8): 1,2,3,4,5
    little = total if all(cnt[i] == 1 for i in range(1, 6)) else 0
    scores.append(little)

    # Big Straight (인덱스 9): 2,3,4,5,6
    big = total if all(cnt[i] == 1 for i in range(2, 7)) else 0
    scores.append(big)

    # Yacht (인덱스 10): 5개 모두 같은 눈
    yacht = 50 if any(c == 5 for c in cnt) else 0
    scores.append(yacht)

    # Choice (인덱스 11): 모든 주사위 합
    scores.append(total)

    return scores

max_score = 0

# 남은 2개 주사위의 모든 조합 시도
for d1 in range(1, 7):
    for d2 in range(1, 7):
        dice = fixed + [d1, d2]
        scores = calculate_score(dice)

        # 사용 가능한 족보 중 최대 점수 선택
        for i in range(12):
            if available[i] == 'Y':
                max_score = max(max_score, scores[i])

print(max_score)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String available = sc.nextLine();  // 12개 족보 사용 가능 여부
        int[] fixed = new int[3];
        for (int i = 0; i < 3; i++) {
            fixed[i] = sc.nextInt();
        }

        int maxScore = 0;

        // 남은 2개 주사위의 모든 조합 시도
        for (int d1 = 1; d1 <= 6; d1++) {
            for (int d2 = 1; d2 <= 6; d2++) {
                int[] dice = {fixed[0], fixed[1], fixed[2], d1, d2};
                int[] scores = calculateScore(dice);

                for (int i = 0; i < 12; i++) {
                    if (available.charAt(i) == 'Y') {
                        maxScore = Math.max(maxScore, scores[i]);
                    }
                }
            }
        }

        System.out.println(maxScore);
    }

    // 주어진 5개 주사위로 각 족보의 점수 계산
    static int[] calculateScore(int[] dice) {
        int[] scores = new int[12];
        int[] cnt = new int[7];
        int total = 0;

        for (int d : dice) {
            cnt[d]++;
            total += d;
        }

        // Ones ~ Sixes
        for (int i = 1; i <= 6; i++) {
            scores[i - 1] = cnt[i] * i;
        }

        // Four of a Kind
        for (int i = 1; i <= 6; i++) {
            if (cnt[i] >= 4) {
                scores[6] = i * 4;
            }
        }

        // Full House
        int kinds = 0;
        boolean hasThree = false, hasTwo = false;
        for (int c : cnt) {
            if (c > 0) kinds++;
            if (c == 3) hasThree = true;
            if (c == 2) hasTwo = true;
        }
        if (kinds == 2 && hasThree && hasTwo) {
            scores[7] = total;
        }

        // Little Straight (1,2,3,4,5)
        boolean little = true;
        for (int i = 1; i <= 5; i++) {
            if (cnt[i] != 1) little = false;
        }
        if (little) scores[8] = total;

        // Big Straight (2,3,4,5,6)
        boolean big = true;
        for (int i = 2; i <= 6; i++) {
            if (cnt[i] != 1) big = false;
        }
        if (big) scores[9] = total;

        // Yacht
        for (int c : cnt) {
            if (c == 5) scores[10] = 50;
        }

        // Choice
        scores[11] = total;

        return scores;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

// 주어진 5개 주사위로 각 족보의 점수 계산
void calculateScore(int dice[], int scores[]) {
    int cnt[7] = {0};
    int total = 0;

    for (int i = 0; i < 5; i++) {
        cnt[dice[i]]++;
        total += dice[i];
    }

    // Ones ~ Sixes (인덱스 0~5)
    for (int i = 1; i <= 6; i++) {
        scores[i - 1] = cnt[i] * i;
    }

    // Four of a Kind (인덱스 6)
    scores[6] = 0;
    for (int i = 1; i <= 6; i++) {
        if (cnt[i] >= 4) {
            scores[6] = i * 4;
        }
    }

    // Full House (인덱스 7)
    scores[7] = 0;
    int kinds = 0;
    bool hasThree = false, hasTwo = false;
    for (int i = 1; i <= 6; i++) {
        if (cnt[i] > 0) kinds++;
        if (cnt[i] == 3) hasThree = true;
        if (cnt[i] == 2) hasTwo = true;
    }
    if (kinds == 2 && hasThree && hasTwo) {
        scores[7] = total;
    }

    // Little Straight (인덱스 8): 1,2,3,4,5
    scores[8] = 0;
    bool little = true;
    for (int i = 1; i <= 5; i++) {
        if (cnt[i] != 1) little = false;
    }
    if (little) scores[8] = total;

    // Big Straight (인덱스 9): 2,3,4,5,6
    scores[9] = 0;
    bool big = true;
    for (int i = 2; i <= 6; i++) {
        if (cnt[i] != 1) big = false;
    }
    if (big) scores[9] = total;

    // Yacht (인덱스 10)
    scores[10] = 0;
    for (int i = 1; i <= 6; i++) {
        if (cnt[i] == 5) scores[10] = 50;
    }

    // Choice (인덱스 11)
    scores[11] = total;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    string available;
    cin >> available;

    int fixed[3];
    for (int i = 0; i < 3; i++) {
        cin >> fixed[i];
    }

    int maxScore = 0;

    // 남은 2개 주사위의 모든 조합 시도
    for (int d1 = 1; d1 <= 6; d1++) {
        for (int d2 = 1; d2 <= 6; d2++) {
            int dice[5] = {fixed[0], fixed[1], fixed[2], d1, d2};
            int scores[12];
            calculateScore(dice, scores);

            for (int i = 0; i < 12; i++) {
                if (available[i] == 'Y') {
                    maxScore = max(maxScore, scores[i]);
                }
            }
        }
    }

    cout << maxScore << endl;

    return 0;
}
'''
        }
    ],
    "baekjoon_27931": [
        {
            "language": "python",
            "code": '''# 백준 27931: Parity Constraint Closest Pair (Easy)
# 수직선상의 점들 중 짝수 거리 최소값과 홀수 거리 최소값을 구하는 문제
import sys
input = sys.stdin.readline

n = int(input())
points = list(map(int, input().split()))

# 정렬하여 인접한 점들 간의 거리만 확인
points.sort()

even_min = -1  # 짝수 거리 최소값
odd_min = -1   # 홀수 거리 최소값

for i in range(n - 1):
    diff = points[i + 1] - points[i]
    if diff % 2 == 0:  # 짝수 거리
        if even_min == -1 or diff < even_min:
            even_min = diff
    else:  # 홀수 거리
        if odd_min == -1 or diff < odd_min:
            odd_min = diff

print(even_min, odd_min)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] points = new int[n];

        for (int i = 0; i < n; i++) {
            points[i] = sc.nextInt();
        }

        // 정렬하여 인접한 점들 간의 거리만 확인
        Arrays.sort(points);

        int evenMin = -1;  // 짝수 거리 최소값
        int oddMin = -1;   // 홀수 거리 최소값

        for (int i = 0; i < n - 1; i++) {
            int diff = points[i + 1] - points[i];
            if (diff % 2 == 0) {  // 짝수 거리
                if (evenMin == -1 || diff < evenMin) {
                    evenMin = diff;
                }
            } else {  // 홀수 거리
                if (oddMin == -1 || diff < oddMin) {
                    oddMin = diff;
                }
            }
        }

        System.out.println(evenMin + " " + oddMin);
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

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> points(n);
    for (int i = 0; i < n; i++) {
        cin >> points[i];
    }

    // 정렬하여 인접한 점들 간의 거리만 확인
    sort(points.begin(), points.end());

    int evenMin = -1;  // 짝수 거리 최소값
    int oddMin = -1;   // 홀수 거리 최소값

    for (int i = 0; i < n - 1; i++) {
        int diff = points[i + 1] - points[i];
        if (diff % 2 == 0) {  // 짝수 거리
            if (evenMin == -1 || diff < evenMin) {
                evenMin = diff;
            }
        } else {  // 홀수 거리
            if (oddMin == -1 || diff < oddMin) {
                oddMin = diff;
            }
        }
    }

    cout << evenMin << " " << oddMin << endl;

    return 0;
}
'''
        }
    ],
    "baekjoon_6324": [
        {
            "language": "python",
            "code": '''# 백준 6324: URLs
# URL을 파싱하여 프로토콜, 호스트, 포트, 경로를 출력하는 문제
import sys
input = sys.stdin.readline

n = int(input())

for i in range(n):
    url = input().strip()

    # 프로토콜 추출 (://로 구분)
    protocol_end = url.find("://")
    protocol = url[:protocol_end]
    rest = url[protocol_end + 3:]

    # 경로 추출 (/로 구분)
    if '/' in rest:
        slash_idx = rest.find('/')
        host_port = rest[:slash_idx]
        path = rest[slash_idx + 1:]
    else:
        host_port = rest
        path = None

    # 호스트와 포트 추출 (:로 구분)
    if ':' in host_port:
        colon_idx = host_port.find(':')
        host = host_port[:colon_idx]
        port = host_port[colon_idx + 1:]
    else:
        host = host_port
        port = None

    # 출력
    print(f"URL #{i + 1}")
    print(f"Protocol = {protocol}")
    print(f"Host     = {host}")

    if port is not None:
        print(f"Port     = {port}")
    else:
        print("Port     = <default>")

    if path is not None:
        print(f"Path     = {path}")
    else:
        print("Path     = <none>")

    print()
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = Integer.parseInt(sc.nextLine());

        for (int i = 0; i < n; i++) {
            String url = sc.nextLine();

            // 프로토콜 추출
            int protocolEnd = url.indexOf("://");
            String protocol = url.substring(0, protocolEnd);
            String rest = url.substring(protocolEnd + 3);

            // 경로 추출
            String hostPort;
            String path = null;
            int slashIdx = rest.indexOf('/');
            if (slashIdx != -1) {
                hostPort = rest.substring(0, slashIdx);
                path = rest.substring(slashIdx + 1);
            } else {
                hostPort = rest;
            }

            // 호스트와 포트 추출
            String host;
            String port = null;
            int colonIdx = hostPort.indexOf(':');
            if (colonIdx != -1) {
                host = hostPort.substring(0, colonIdx);
                port = hostPort.substring(colonIdx + 1);
            } else {
                host = hostPort;
            }

            // 출력
            System.out.println("URL #" + (i + 1));
            System.out.println("Protocol = " + protocol);
            System.out.println("Host     = " + host);

            if (port != null) {
                System.out.println("Port     = " + port);
            } else {
                System.out.println("Port     = <default>");
            }

            if (path != null) {
                System.out.println("Path     = " + path);
            } else {
                System.out.println("Path     = <none>");
            }

            System.out.println();
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    cin.ignore();

    for (int i = 0; i < n; i++) {
        string url;
        getline(cin, url);

        // 프로토콜 추출
        size_t protocolEnd = url.find("://");
        string protocol = url.substr(0, protocolEnd);
        string rest = url.substr(protocolEnd + 3);

        // 경로 추출
        string hostPort;
        string path = "";
        bool hasPath = false;
        size_t slashIdx = rest.find('/');
        if (slashIdx != string::npos) {
            hostPort = rest.substr(0, slashIdx);
            path = rest.substr(slashIdx + 1);
            hasPath = true;
        } else {
            hostPort = rest;
        }

        // 호스트와 포트 추출
        string host;
        string port = "";
        bool hasPort = false;
        size_t colonIdx = hostPort.find(':');
        if (colonIdx != string::npos) {
            host = hostPort.substr(0, colonIdx);
            port = hostPort.substr(colonIdx + 1);
            hasPort = true;
        } else {
            host = hostPort;
        }

        // 출력
        cout << "URL #" << (i + 1) << "\\n";
        cout << "Protocol = " << protocol << "\\n";
        cout << "Host     = " << host << "\\n";

        if (hasPort) {
            cout << "Port     = " << port << "\\n";
        } else {
            cout << "Port     = <default>\\n";
        }

        if (hasPath) {
            cout << "Path     = " << path << "\\n";
        } else {
            cout << "Path     = <none>\\n";
        }

        cout << "\\n";
    }

    return 0;
}
'''
        }
    ],
    "baekjoon_17124": [
        {
            "language": "python",
            "code": '''# 백준 17124: 두 개의 배열
# 배열 A의 각 원소에 대해 배열 B에서 가장 가까운 값을 찾아 합을 구하는 문제
import sys
from bisect import bisect_left
input = sys.stdin.readline

T = int(input())

for _ in range(T):
    n, m = map(int, input().split())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))

    # B를 정렬하여 이분 탐색 사용
    B.sort()

    total = 0

    for a in A:
        # 이분 탐색으로 a와 가장 가까운 값 찾기
        idx = bisect_left(B, a)

        # 후보: B[idx-1]과 B[idx]
        candidates = []
        if idx > 0:
            candidates.append(B[idx - 1])
        if idx < m:
            candidates.append(B[idx])

        # 가장 가까운 값 선택 (거리가 같으면 작은 값)
        best = min(candidates, key=lambda x: (abs(x - a), x))
        total += best

    print(total)
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
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int m = Integer.parseInt(st.nextToken());

            int[] A = new int[n];
            int[] B = new int[m];

            st = new StringTokenizer(br.readLine());
            for (int i = 0; i < n; i++) {
                A[i] = Integer.parseInt(st.nextToken());
            }

            st = new StringTokenizer(br.readLine());
            for (int i = 0; i < m; i++) {
                B[i] = Integer.parseInt(st.nextToken());
            }

            // B를 정렬하여 이분 탐색 사용
            Arrays.sort(B);

            long total = 0;

            for (int a : A) {
                // 이분 탐색
                int idx = Arrays.binarySearch(B, a);
                if (idx < 0) {
                    idx = -(idx + 1);
                }

                // 후보들 중 가장 가까운 값 선택
                int best = -1;
                int minDiff = Integer.MAX_VALUE;

                if (idx > 0) {
                    int diff = Math.abs(B[idx - 1] - a);
                    if (diff < minDiff || (diff == minDiff && B[idx - 1] < best)) {
                        minDiff = diff;
                        best = B[idx - 1];
                    }
                }

                if (idx < m) {
                    int diff = Math.abs(B[idx] - a);
                    if (diff < minDiff || (diff == minDiff && B[idx] < best)) {
                        minDiff = diff;
                        best = B[idx];
                    }
                }

                total += best;
            }

            sb.append(total).append("\\n");
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
#include <cmath>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int n, m;
        cin >> n >> m;

        vector<int> A(n), B(m);

        for (int i = 0; i < n; i++) {
            cin >> A[i];
        }

        for (int i = 0; i < m; i++) {
            cin >> B[i];
        }

        // B를 정렬하여 이분 탐색 사용
        sort(B.begin(), B.end());

        long long total = 0;

        for (int a : A) {
            // 이분 탐색으로 a 이상인 첫 위치 찾기
            int idx = lower_bound(B.begin(), B.end(), a) - B.begin();

            // 후보들 중 가장 가까운 값 선택
            int best = -1;
            int minDiff = 2e9;

            if (idx > 0) {
                int diff = abs(B[idx - 1] - a);
                if (diff < minDiff || (diff == minDiff && B[idx - 1] < best)) {
                    minDiff = diff;
                    best = B[idx - 1];
                }
            }

            if (idx < m) {
                int diff = abs(B[idx] - a);
                if (diff < minDiff || (diff == minDiff && B[idx] < best)) {
                    minDiff = diff;
                    best = B[idx];
                }
            }

            total += best;
        }

        cout << total << "\\n";
    }

    return 0;
}
'''
        }
    ],
    "baekjoon_19948": [
        {
            "language": "python",
            "code": '''# 백준 19948: 음유시인 영재
# 시를 입력하고 제목을 만들 수 있는지 확인하는 문제
import sys
input = sys.stdin.readline

poem = input().strip()
space_limit = int(input())
key_limits = list(map(int, input().split()))  # A~Z 각각의 남은 횟수

# 시 입력에 필요한 키 사용량 계산
space_count = 0
key_count = [0] * 26  # A~Z 사용량

prev_char = None
for c in poem:
    if c == ' ':
        # 연속된 공백은 한 번만 카운트
        if prev_char != ' ':
            space_count += 1
    else:
        # 대소문자 모두 같은 키로 취급
        idx = ord(c.upper()) - ord('A')
        # 연속된 같은 문자는 한 번만 카운트
        if prev_char is None or prev_char.upper() != c.upper():
            key_count[idx] += 1
    prev_char = c

# 시 입력 가능 여부 확인
possible = True
if space_count > space_limit:
    possible = False
for i in range(26):
    if key_count[i] > key_limits[i]:
        possible = False

if not possible:
    print(-1)
else:
    # 남은 키 횟수 업데이트
    space_limit -= space_count
    for i in range(26):
        key_limits[i] -= key_count[i]

    # 제목 생성: 각 단어의 첫 글자를 대문자로
    words = poem.split()
    title = ""
    for word in words:
        title += word[0].upper()

    # 제목 입력에 필요한 키 사용량 계산
    title_key_count = [0] * 26
    prev_char = None
    for c in title:
        idx = ord(c) - ord('A')
        if prev_char != c:
            title_key_count[idx] += 1
        prev_char = c

    # 제목 입력 가능 여부 확인
    title_possible = True
    for i in range(26):
        if title_key_count[i] > key_limits[i]:
            title_possible = False

    if title_possible:
        print(title)
    else:
        print(-1)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String poem = sc.nextLine();
        int spaceLimit = sc.nextInt();
        int[] keyLimits = new int[26];
        for (int i = 0; i < 26; i++) {
            keyLimits[i] = sc.nextInt();
        }

        // 시 입력에 필요한 키 사용량 계산
        int spaceCount = 0;
        int[] keyCount = new int[26];

        Character prevChar = null;
        for (char c : poem.toCharArray()) {
            if (c == ' ') {
                if (prevChar == null || prevChar != ' ') {
                    spaceCount++;
                }
            } else {
                int idx = Character.toUpperCase(c) - 'A';
                if (prevChar == null || Character.toUpperCase(prevChar) != Character.toUpperCase(c)) {
                    keyCount[idx]++;
                }
            }
            prevChar = c;
        }

        // 시 입력 가능 여부 확인
        boolean possible = true;
        if (spaceCount > spaceLimit) {
            possible = false;
        }
        for (int i = 0; i < 26; i++) {
            if (keyCount[i] > keyLimits[i]) {
                possible = false;
            }
        }

        if (!possible) {
            System.out.println(-1);
            return;
        }

        // 남은 키 횟수 업데이트
        for (int i = 0; i < 26; i++) {
            keyLimits[i] -= keyCount[i];
        }

        // 제목 생성
        String[] words = poem.split(" +");
        StringBuilder title = new StringBuilder();
        for (String word : words) {
            if (word.length() > 0) {
                title.append(Character.toUpperCase(word.charAt(0)));
            }
        }

        // 제목 입력에 필요한 키 사용량 계산
        int[] titleKeyCount = new int[26];
        prevChar = null;
        for (char c : title.toString().toCharArray()) {
            int idx = c - 'A';
            if (prevChar == null || prevChar != c) {
                titleKeyCount[idx]++;
            }
            prevChar = c;
        }

        // 제목 입력 가능 여부 확인
        boolean titlePossible = true;
        for (int i = 0; i < 26; i++) {
            if (titleKeyCount[i] > keyLimits[i]) {
                titlePossible = false;
            }
        }

        if (titlePossible) {
            System.out.println(title);
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
#include <string>
#include <sstream>
#include <cctype>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    string poem;
    getline(cin, poem);

    int spaceLimit;
    cin >> spaceLimit;

    int keyLimits[26];
    for (int i = 0; i < 26; i++) {
        cin >> keyLimits[i];
    }

    // 시 입력에 필요한 키 사용량 계산
    int spaceCount = 0;
    int keyCount[26] = {0};

    char prevChar = '\\0';
    for (char c : poem) {
        if (c == ' ') {
            if (prevChar != ' ') {
                spaceCount++;
            }
        } else {
            int idx = toupper(c) - 'A';
            if (prevChar == '\\0' || toupper(prevChar) != toupper(c)) {
                keyCount[idx]++;
            }
        }
        prevChar = c;
    }

    // 시 입력 가능 여부 확인
    bool possible = true;
    if (spaceCount > spaceLimit) {
        possible = false;
    }
    for (int i = 0; i < 26; i++) {
        if (keyCount[i] > keyLimits[i]) {
            possible = false;
        }
    }

    if (!possible) {
        cout << -1 << endl;
        return 0;
    }

    // 남은 키 횟수 업데이트
    for (int i = 0; i < 26; i++) {
        keyLimits[i] -= keyCount[i];
    }

    // 제목 생성
    string title = "";
    istringstream iss(poem);
    string word;
    while (iss >> word) {
        title += toupper(word[0]);
    }

    // 제목 입력에 필요한 키 사용량 계산
    int titleKeyCount[26] = {0};
    prevChar = '\\0';
    for (char c : title) {
        int idx = c - 'A';
        if (prevChar != c) {
            titleKeyCount[idx]++;
        }
        prevChar = c;
    }

    // 제목 입력 가능 여부 확인
    bool titlePossible = true;
    for (int i = 0; i < 26; i++) {
        if (titleKeyCount[i] > keyLimits[i]) {
            titlePossible = false;
        }
    }

    if (titlePossible) {
        cout << title << endl;
    } else {
        cout << -1 << endl;
    }

    return 0;
}
'''
        }
    ],
    "baekjoon_11507": [
        {
            "language": "python",
            "code": '''# 백준 11507: 카드셋트
# 누락된 카드를 찾는 문제
import sys
input = sys.stdin.readline

s = input().strip()

# 각 무늬별로 1~13까지 카드가 있어야 함
# P: 스페이드, K: 클로버, H: 하트, T: 다이아몬드
cards = {'P': set(), 'K': set(), 'H': set(), 'T': set()}

# 카드 파싱 (3글자씩)
i = 0
error = False

while i < len(s):
    suit = s[i]  # 무늬
    num = int(s[i+1:i+3])  # 숫자 (01~13)

    # 중복 체크
    if num in cards[suit]:
        error = True
        break

    cards[suit].add(num)
    i += 3

if error:
    print("GRESKA")
else:
    # 각 무늬별로 남은 카드 수 계산
    result = []
    for suit in ['P', 'K', 'H', 'T']:
        result.append(13 - len(cards[suit]))
    print(' '.join(map(str, result)))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();

        // 각 무늬별로 카드 기록
        Set<Integer>[] cards = new HashSet[4];
        for (int i = 0; i < 4; i++) {
            cards[i] = new HashSet<>();
        }

        // P=0, K=1, H=2, T=3
        boolean error = false;

        for (int i = 0; i < s.length(); i += 3) {
            char suit = s.charAt(i);
            int num = Integer.parseInt(s.substring(i + 1, i + 3));

            int suitIdx = -1;
            if (suit == 'P') suitIdx = 0;
            else if (suit == 'K') suitIdx = 1;
            else if (suit == 'H') suitIdx = 2;
            else if (suit == 'T') suitIdx = 3;

            // 중복 체크
            if (cards[suitIdx].contains(num)) {
                error = true;
                break;
            }

            cards[suitIdx].add(num);
        }

        if (error) {
            System.out.println("GRESKA");
        } else {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 4; i++) {
                if (i > 0) sb.append(" ");
                sb.append(13 - cards[i].size());
            }
            System.out.println(sb);
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
#include <set>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    cin >> s;

    // 각 무늬별로 카드 기록
    set<int> cards[4];  // P=0, K=1, H=2, T=3

    bool error = false;

    for (int i = 0; i < s.length(); i += 3) {
        char suit = s[i];
        int num = stoi(s.substr(i + 1, 2));

        int suitIdx = -1;
        if (suit == 'P') suitIdx = 0;
        else if (suit == 'K') suitIdx = 1;
        else if (suit == 'H') suitIdx = 2;
        else if (suit == 'T') suitIdx = 3;

        // 중복 체크
        if (cards[suitIdx].count(num)) {
            error = true;
            break;
        }

        cards[suitIdx].insert(num);
    }

    if (error) {
        cout << "GRESKA" << endl;
    } else {
        for (int i = 0; i < 4; i++) {
            if (i > 0) cout << " ";
            cout << 13 - cards[i].size();
        }
        cout << endl;
    }

    return 0;
}
'''
        }
    ],
    "baekjoon_4821": [
        {
            "language": "python",
            "code": '''# 백준 4821: 페이지 세기
# 인쇄 범위에서 출력할 페이지 수를 구하는 문제
import sys
input = sys.stdin.readline

while True:
    total_pages = int(input())
    if total_pages == 0:
        break

    ranges = input().strip()

    # 출력할 페이지를 집합으로 관리
    pages = set()

    # 쉼표로 구분된 각 범위 처리
    for part in ranges.split(','):
        if '-' in part:
            # 범위 형식: low-high
            low, high = map(int, part.split('-'))
            # low > high면 출력 안 함
            if low <= high:
                # 문서 범위 내의 페이지만 추가
                for p in range(max(1, low), min(total_pages, high) + 1):
                    pages.add(p)
        else:
            # 단일 페이지
            p = int(part)
            if 1 <= p <= total_pages:
                pages.add(p)

    print(len(pages))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        while (true) {
            int totalPages = Integer.parseInt(sc.nextLine().trim());
            if (totalPages == 0) break;

            String ranges = sc.nextLine().trim();

            // 출력할 페이지를 집합으로 관리
            Set<Integer> pages = new HashSet<>();

            // 쉼표로 구분된 각 범위 처리
            for (String part : ranges.split(",")) {
                if (part.contains("-")) {
                    // 범위 형식: low-high
                    String[] nums = part.split("-");
                    int low = Integer.parseInt(nums[0]);
                    int high = Integer.parseInt(nums[1]);

                    if (low <= high) {
                        for (int p = Math.max(1, low); p <= Math.min(totalPages, high); p++) {
                            pages.add(p);
                        }
                    }
                } else {
                    // 단일 페이지
                    int p = Integer.parseInt(part);
                    if (p >= 1 && p <= totalPages) {
                        pages.add(p);
                    }
                }
            }

            System.out.println(pages.size());
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
#include <set>
#include <sstream>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int totalPages;
    while (cin >> totalPages && totalPages != 0) {
        string ranges;
        cin >> ranges;

        // 출력할 페이지를 집합으로 관리
        set<int> pages;

        // 쉼표로 구분된 각 범위 처리
        stringstream ss(ranges);
        string part;

        while (getline(ss, part, ',')) {
            size_t dashPos = part.find('-');
            if (dashPos != string::npos) {
                // 범위 형식: low-high
                int low = stoi(part.substr(0, dashPos));
                int high = stoi(part.substr(dashPos + 1));

                if (low <= high) {
                    for (int p = max(1, low); p <= min(totalPages, high); p++) {
                        pages.insert(p);
                    }
                }
            } else {
                // 단일 페이지
                int p = stoi(part);
                if (p >= 1 && p <= totalPages) {
                    pages.insert(p);
                }
            }
        }

        cout << pages.size() << "\\n";
    }

    return 0;
}
'''
        }
    ],
    "baekjoon_11946": [
        {
            "language": "python",
            "code": '''# 백준 11946: ACM-ICPC
# ACM-ICPC 등수 산정 문제
import sys
from collections import defaultdict
input = sys.stdin.readline

N, M, S = map(int, input().split())

# 각 팀의 정보: (팀번호: {문제번호: (제출시간, 틀린횟수)})
# 맞은 문제만 기록
teams = defaultdict(dict)  # teams[팀번호][문제번호] = (제출시간, 해당 문제의 틀린 제출 횟수)
wrong_count = defaultdict(lambda: defaultdict(int))  # wrong_count[팀번호][문제번호] = 틀린 횟수

for _ in range(S):
    line = input().split()
    time = int(line[0])
    problem = int(line[1])
    team = int(line[2])
    result = line[3]

    # 이미 맞은 문제는 무시
    if problem in teams[team]:
        continue

    if result == "AC":
        # 맞았을 때: 제출 시간과 이전 틀린 횟수 기록
        teams[team][problem] = (time, wrong_count[team][problem])
    else:
        # 틀렸을 때: 틀린 횟수 증가
        wrong_count[team][problem] += 1

# 각 팀의 최종 결과 계산
results = []
for team_num in range(1, N + 1):
    solved = len(teams[team_num])
    penalty = 0

    for problem, (time, wrong) in teams[team_num].items():
        penalty += time + wrong * 20

    results.append((team_num, solved, penalty))

# 정렬: 맞은 문제 수 내림차순, 페널티 오름차순, 팀 번호 오름차순
results.sort(key=lambda x: (-x[1], x[2], x[0]))

# 등수 매기기
rank = 1
for i, (team_num, solved, penalty) in enumerate(results):
    if i > 0:
        prev_solved, prev_penalty = results[i-1][1], results[i-1][2]
        if solved != prev_solved or penalty != prev_penalty:
            rank = i + 1
    print(rank, solved, penalty)
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

        int N = Integer.parseInt(st.nextToken());  // 팀 수
        int M = Integer.parseInt(st.nextToken());  // 문제 수
        int S = Integer.parseInt(st.nextToken());  // 제출 수

        // 각 팀의 맞은 문제: 제출 시간 기록
        Map<Integer, Map<Integer, Integer>> solvedTime = new HashMap<>();
        // 각 팀의 각 문제별 틀린 횟수
        Map<Integer, Map<Integer, Integer>> wrongCount = new HashMap<>();

        for (int i = 1; i <= N; i++) {
            solvedTime.put(i, new HashMap<>());
            wrongCount.put(i, new HashMap<>());
        }

        for (int i = 0; i < S; i++) {
            st = new StringTokenizer(br.readLine());
            int time = Integer.parseInt(st.nextToken());
            int problem = Integer.parseInt(st.nextToken());
            int team = Integer.parseInt(st.nextToken());
            String result = st.nextToken();

            // 이미 맞은 문제는 무시
            if (solvedTime.get(team).containsKey(problem)) {
                continue;
            }

            if (result.equals("AC")) {
                solvedTime.get(team).put(problem, time);
            } else {
                wrongCount.get(team).merge(problem, 1, Integer::sum);
            }
        }

        // 각 팀의 최종 결과 계산
        int[][] results = new int[N][3];  // [팀번호, 맞은수, 페널티]

        for (int team = 1; team <= N; team++) {
            int solved = solvedTime.get(team).size();
            int penalty = 0;

            for (Map.Entry<Integer, Integer> entry : solvedTime.get(team).entrySet()) {
                int problem = entry.getKey();
                int time = entry.getValue();
                int wrong = wrongCount.get(team).getOrDefault(problem, 0);
                penalty += time + wrong * 20;
            }

            results[team - 1] = new int[]{team, solved, penalty};
        }

        // 정렬
        Arrays.sort(results, (a, b) -> {
            if (a[1] != b[1]) return b[1] - a[1];  // 맞은 수 내림차순
            if (a[2] != b[2]) return a[2] - b[2];  // 페널티 오름차순
            return a[0] - b[0];  // 팀 번호 오름차순
        });

        // 등수 매기기 및 출력
        StringBuilder sb = new StringBuilder();
        int rank = 1;
        for (int i = 0; i < N; i++) {
            if (i > 0) {
                if (results[i][1] != results[i-1][1] || results[i][2] != results[i-1][2]) {
                    rank = i + 1;
                }
            }
            sb.append(rank).append(" ").append(results[i][1]).append(" ").append(results[i][2]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <map>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M, S;
    cin >> N >> M >> S;

    // 각 팀의 맞은 문제: 제출 시간
    map<int, map<int, int>> solvedTime;  // solvedTime[team][problem] = time
    // 각 팀의 각 문제별 틀린 횟수
    map<int, map<int, int>> wrongCount;  // wrongCount[team][problem] = count

    for (int i = 0; i < S; i++) {
        int time, problem, team;
        string result;
        cin >> time >> problem >> team >> result;

        // 이미 맞은 문제는 무시
        if (solvedTime[team].count(problem)) {
            continue;
        }

        if (result == "AC") {
            solvedTime[team][problem] = time;
        } else {
            wrongCount[team][problem]++;
        }
    }

    // 각 팀의 최종 결과 계산
    vector<tuple<int, int, int>> results;  // (팀번호, 맞은수, 페널티)

    for (int team = 1; team <= N; team++) {
        int solved = solvedTime[team].size();
        int penalty = 0;

        for (auto& p : solvedTime[team]) {
            int problem = p.first;
            int time = p.second;
            int wrong = wrongCount[team][problem];
            penalty += time + wrong * 20;
        }

        results.push_back({team, solved, penalty});
    }

    // 정렬: 맞은 수 내림차순, 페널티 오름차순, 팀 번호 오름차순
    sort(results.begin(), results.end(), [](auto& a, auto& b) {
        if (get<1>(a) != get<1>(b)) return get<1>(a) > get<1>(b);
        if (get<2>(a) != get<2>(b)) return get<2>(a) < get<2>(b);
        return get<0>(a) < get<0>(b);
    });

    // 등수 매기기 및 출력
    int rank = 1;
    for (int i = 0; i < N; i++) {
        if (i > 0) {
            if (get<1>(results[i]) != get<1>(results[i-1]) ||
                get<2>(results[i]) != get<2>(results[i-1])) {
                rank = i + 1;
            }
        }
        cout << rank << " " << get<1>(results[i]) << " " << get<2>(results[i]) << "\\n";
    }

    return 0;
}
'''
        }
    ],
    "baekjoon_9881": [
        {
            "language": "python",
            "code": '''# 백준 9881: Ski Course Design
# 언덕 높이를 조정하여 최대-최소 차이가 17 이하가 되도록 하는 최소 비용
import sys
input = sys.stdin.readline

n = int(input())
hills = [int(input()) for _ in range(n)]

min_cost = float('inf')

# 가능한 모든 범위 [low, low+17] 시도 (low: 0~83)
for low in range(84):
    high = low + 17
    cost = 0

    for h in hills:
        if h < low:
            # 높이를 low로 올려야 함
            cost += (low - h) ** 2
        elif h > high:
            # 높이를 high로 낮춰야 함
            cost += (h - high) ** 2

    min_cost = min(min_cost, cost)

print(min_cost)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] hills = new int[n];

        for (int i = 0; i < n; i++) {
            hills[i] = sc.nextInt();
        }

        int minCost = Integer.MAX_VALUE;

        // 가능한 모든 범위 [low, low+17] 시도
        for (int low = 0; low <= 83; low++) {
            int high = low + 17;
            int cost = 0;

            for (int h : hills) {
                if (h < low) {
                    cost += (low - h) * (low - h);
                } else if (h > high) {
                    cost += (h - high) * (h - high);
                }
            }

            minCost = Math.min(minCost, cost);
        }

        System.out.println(minCost);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int hills[1000];
    for (int i = 0; i < n; i++) {
        cin >> hills[i];
    }

    int minCost = 1e9;

    // 가능한 모든 범위 [low, low+17] 시도
    for (int low = 0; low <= 83; low++) {
        int high = low + 17;
        int cost = 0;

        for (int i = 0; i < n; i++) {
            int h = hills[i];
            if (h < low) {
                cost += (low - h) * (low - h);
            } else if (h > high) {
                cost += (h - high) * (h - high);
            }
        }

        minCost = min(minCost, cost);
    }

    cout << minCost << endl;

    return 0;
}
'''
        }
    ],
    "baekjoon_2641": [
        {
            "language": "python",
            "code": '''# 백준 2641: 다각형그리기
# 같은 다각형을 그리는 모양수열 찾기
import sys
input = sys.stdin.readline

n = int(input())
sample = list(map(int, input().split()))

m = int(input())

# 반대 방향 매핑: 1<->3, 2<->4
opposite = {1: 3, 3: 1, 2: 4, 4: 2}

def normalize(seq):
    """모양수열을 정규화하여 비교 가능한 형태로 변환"""
    # 모든 시작점에서의 순환 수열 생성
    rotations = []
    for i in range(len(seq)):
        rotations.append(tuple(seq[i:] + seq[:i]))
    return set(rotations)

def reverse_seq(seq):
    """역방향 수열 생성"""
    # 역순으로 하되 각 방향을 반대로
    return [opposite[x] for x in reversed(seq)]

# 표본 수열의 모든 회전 + 역방향 회전 저장
sample_normalized = normalize(sample)
sample_reverse = reverse_seq(sample)
sample_reverse_normalized = normalize(sample_reverse)

matches = []

for _ in range(m):
    seq = list(map(int, input().split()))

    # 정방향 비교
    if tuple(seq) in sample_normalized:
        matches.append(seq)
        continue

    # 역방향 비교
    if tuple(seq) in sample_reverse_normalized:
        matches.append(seq)

print(len(matches))
for seq in matches:
    print(' '.join(map(str, seq)))
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;

public class Main {
    static int[] opposite = {0, 3, 4, 1, 2};  // 1<->3, 2<->4

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] sample = new int[n];
        for (int i = 0; i < n; i++) {
            sample[i] = sc.nextInt();
        }

        int m = sc.nextInt();

        // 표본의 모든 회전 및 역방향 저장
        Set<String> validPatterns = new HashSet<>();

        // 정방향 모든 회전
        for (int i = 0; i < n; i++) {
            StringBuilder sb = new StringBuilder();
            for (int j = 0; j < n; j++) {
                sb.append(sample[(i + j) % n]).append(",");
            }
            validPatterns.add(sb.toString());
        }

        // 역방향 수열 생성
        int[] reversed = new int[n];
        for (int i = 0; i < n; i++) {
            reversed[i] = opposite[sample[n - 1 - i]];
        }

        // 역방향 모든 회전
        for (int i = 0; i < n; i++) {
            StringBuilder sb = new StringBuilder();
            for (int j = 0; j < n; j++) {
                sb.append(reversed[(i + j) % n]).append(",");
            }
            validPatterns.add(sb.toString());
        }

        List<int[]> matches = new ArrayList<>();

        for (int i = 0; i < m; i++) {
            int[] seq = new int[n];
            for (int j = 0; j < n; j++) {
                seq[j] = sc.nextInt();
            }

            StringBuilder sb = new StringBuilder();
            for (int x : seq) {
                sb.append(x).append(",");
            }

            if (validPatterns.contains(sb.toString())) {
                matches.add(seq);
            }
        }

        System.out.println(matches.size());
        for (int[] seq : matches) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < n; i++) {
                if (i > 0) sb.append(" ");
                sb.append(seq[i]);
            }
            System.out.println(sb);
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
#include <set>
#include <string>
using namespace std;

int opposite[] = {0, 3, 4, 1, 2};  // 1<->3, 2<->4

string toStr(vector<int>& v) {
    string s = "";
    for (int x : v) {
        s += to_string(x) + ",";
    }
    return s;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> sample(n);
    for (int i = 0; i < n; i++) {
        cin >> sample[i];
    }

    int m;
    cin >> m;

    // 표본의 모든 회전 및 역방향 저장
    set<string> validPatterns;

    // 정방향 모든 회전
    for (int i = 0; i < n; i++) {
        vector<int> rotated(n);
        for (int j = 0; j < n; j++) {
            rotated[j] = sample[(i + j) % n];
        }
        validPatterns.insert(toStr(rotated));
    }

    // 역방향 수열 생성
    vector<int> reversed(n);
    for (int i = 0; i < n; i++) {
        reversed[i] = opposite[sample[n - 1 - i]];
    }

    // 역방향 모든 회전
    for (int i = 0; i < n; i++) {
        vector<int> rotated(n);
        for (int j = 0; j < n; j++) {
            rotated[j] = reversed[(i + j) % n];
        }
        validPatterns.insert(toStr(rotated));
    }

    vector<vector<int>> matches;

    for (int i = 0; i < m; i++) {
        vector<int> seq(n);
        for (int j = 0; j < n; j++) {
            cin >> seq[j];
        }

        if (validPatterns.count(toStr(seq))) {
            matches.push_back(seq);
        }
    }

    cout << matches.size() << "\\n";
    for (auto& seq : matches) {
        for (int i = 0; i < n; i++) {
            if (i > 0) cout << " ";
            cout << seq[i];
        }
        cout << "\\n";
    }

    return 0;
}
'''
        }
    ],
    "baekjoon_3944": [
        {
            "language": "python",
            "code": '''# 백준 3944: 나머지 계산
# 10^N을 K로 나눈 나머지를 구하는 문제
import sys
input = sys.stdin.readline

T = int(input())

for _ in range(T):
    N, K = map(int, input().split())

    # 10^N mod K를 빠르게 계산 (거듭제곱)
    result = pow(10, N, K)
    print(result)
'''
        },
        {
            "language": "java",
            "code": '''import java.util.*;
import java.math.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            long N = sc.nextLong();
            long K = sc.nextLong();

            // 10^N mod K를 빠르게 계산
            BigInteger ten = BigInteger.TEN;
            BigInteger n = BigInteger.valueOf(N);
            BigInteger k = BigInteger.valueOf(K);

            BigInteger result = ten.modPow(n, k);
            System.out.println(result);
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

// 거듭제곱 모듈러 연산
long long power(long long base, long long exp, long long mod) {
    long long result = 1;
    base %= mod;

    while (exp > 0) {
        if (exp & 1) {
            result = result * base % mod;
        }
        exp >>= 1;
        base = base * base % mod;
    }

    return result;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        long long N, K;
        cin >> N >> K;

        // 10^N mod K 계산
        cout << power(10, N, K) << "\\n";
    }

    return 0;
}
'''
        }
    ],
    "baekjoon_22858": [
        {
            "language": "python",
            "code": '''# 백준 22858: 원상 복구 (small)
# 셔플을 K번 역으로 적용하여 원래 배열 복구
import sys
input = sys.stdin.readline

N, K = map(int, input().split())
S = list(map(int, input().split()))  # 셔플 후 결과
D = list(map(int, input().split()))  # 셔플 규칙

# D[i]는 i+1번 위치에 D[i]번 위치의 카드가 온다는 의미
# 즉, 셔플 후 result[i] = original[D[i]-1]

# 역으로 적용: original[D[i]-1] = result[i]
# 즉, 역셔플: result_before[D[i]-1] = result_after[i]

current = S[:]

for _ in range(K):
    before = [0] * N
    for i in range(N):
        before[D[i] - 1] = current[i]
    current = before

print(' '.join(map(str, current)))
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

        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        int[] S = new int[N];  // 셔플 후 결과
        int[] D = new int[N];  // 셔플 규칙

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            S[i] = Integer.parseInt(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            D[i] = Integer.parseInt(st.nextToken());
        }

        // 역셔플 K번 적용
        int[] current = S.clone();

        for (int k = 0; k < K; k++) {
            int[] before = new int[N];
            for (int i = 0; i < N; i++) {
                before[D[i] - 1] = current[i];
            }
            current = before;
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < N; i++) {
            if (i > 0) sb.append(" ");
            sb.append(current[i]);
        }
        System.out.println(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int N, K;
    cin >> N >> K;

    vector<int> S(N);  // 셔플 후 결과
    vector<int> D(N);  // 셔플 규칙

    for (int i = 0; i < N; i++) {
        cin >> S[i];
    }

    for (int i = 0; i < N; i++) {
        cin >> D[i];
    }

    // 역셔플 K번 적용
    vector<int> current = S;

    for (int k = 0; k < K; k++) {
        vector<int> before(N);
        for (int i = 0; i < N; i++) {
            before[D[i] - 1] = current[i];
        }
        current = before;
    }

    for (int i = 0; i < N; i++) {
        if (i > 0) cout << " ";
        cout << current[i];
    }
    cout << "\\n";

    return 0;
}
'''
        }
    ]
}

def main():
    file_path = "/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json"

    # 파일을 잠금 상태로 읽기
    with open(file_path, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        data = json.load(f)

    # 솔루션이 비어있는 문제에 솔루션 추가
    updated_count = 0

    for problem in data:
        problem_id = problem.get('id', '')

        # 솔루션이 비어있고, 우리가 솔루션을 가지고 있는 경우에만 업데이트
        if problem_id in SOLUTIONS:
            if not problem.get('solutions') or len(problem.get('solutions', [])) == 0:
                problem['solutions'] = SOLUTIONS[problem_id]
                updated_count += 1
                print(f"Updated: {problem_id}")

    # 파일에 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nTotal updated: {updated_count} problems")

if __name__ == "__main__":
    main()
