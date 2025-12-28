#!/usr/bin/env python3
import json

# 새로운 10개 문제 솔루션
new_solutions = {
    "14919": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 구간 개수 m 입력
m = int(input())
# 실수 배열 입력
nums = list(map(float, input().split()))

# 각 구간의 개수를 저장할 배열
count = [0] * m
# 구간 길이
L = 1.0 / m

# 각 실수가 어느 구간에 속하는지 계산
for num in nums:
    # 구간 인덱스 계산 (0-indexed)
    idx = int(num / L)
    # 정확히 1인 경우 마지막 구간에 포함
    if idx >= m:
        idx = m - 1
    count[idx] += 1

# 결과 출력
print(' '.join(map(str, count)))
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int m = Integer.parseInt(br.readLine().trim());
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

int main() {
    ios_base::sync_with_stdio(false);
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
        ]
    },
    "20937": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 떡의 개수 입력
n = int(input())
# 각 떡의 둘레 입력
perimeters = list(map(int, input().split()))

# 둘레별 떡 개수를 세기 (같은 둘레의 떡은 한 그릇에 담을 수 없음)
count = {}
for p in perimeters:
    count[p] = count.get(p, 0) + 1

# 가장 많이 겹치는 둘레의 개수가 필요한 그릇 수
result = max(count.values())
print(result)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        Map<Integer, Integer> count = new HashMap<>();
        for (int i = 0; i < n; i++) {
            int p = Integer.parseInt(st.nextToken());
            count.put(p, count.getOrDefault(p, 0) + 1);
        }
        int result = 0;
        for (int cnt : count.values()) {
            result = Math.max(result, cnt);
        }
        System.out.println(result);
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

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    int n;
    cin >> n;
    map<int, int> count;
    for (int i = 0; i < n; i++) {
        int p;
        cin >> p;
        count[p]++;
    }
    int result = 0;
    for (auto& pair : count) {
        result = max(result, pair.second);
    }
    cout << result << endl;
    return 0;
}
"""
            }
        ]
    },
    "2232": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 지뢰 개수 입력
n = int(input())
# 각 지뢰의 충격 강도
p = [int(input()) for _ in range(n)]

# 극대값(양쪽보다 큰 값)인 지뢰를 찾기
for i in range(n):
    left_ok = (i == 0) or (p[i] >= p[i-1])
    right_ok = (i == n-1) or (p[i] >= p[i+1])
    if left_ok and right_ok:
        if i > 0 and p[i] == p[i-1]:
            continue
        print(i + 1)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();
        int n = Integer.parseInt(br.readLine().trim());
        int[] p = new int[n];
        for (int i = 0; i < n; i++) {
            p[i] = Integer.parseInt(br.readLine().trim());
        }
        for (int i = 0; i < n; i++) {
            boolean leftOk = (i == 0) || (p[i] >= p[i-1]);
            boolean rightOk = (i == n-1) || (p[i] >= p[i+1]);
            if (leftOk && rightOk) {
                if (i > 0 && p[i] == p[i-1]) continue;
                sb.append(i + 1).append("\\n");
            }
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
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    int n;
    cin >> n;
    vector<int> p(n);
    for (int i = 0; i < n; i++) {
        cin >> p[i];
    }
    for (int i = 0; i < n; i++) {
        bool leftOk = (i == 0) || (p[i] >= p[i-1]);
        bool rightOk = (i == n-1) || (p[i] >= p[i+1]);
        if (leftOk && rightOk) {
            if (i > 0 && p[i] == p[i-1]) continue;
            cout << i + 1 << "\\n";
        }
    }
    return 0;
}
"""
            }
        ]
    },
    "1980": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

# 타워버거 n분, 불고기버거 m분, 총 t분
n, m, t = map(int, input().split())

# 콜라 마시는 시간을 최소화하면서 햄버거를 최대한 많이 먹기
min_cola = t + 1
max_burgers = 0

for i in range(t // n + 1):
    remaining = t - n * i
    j = remaining // m
    cola_time = remaining - m * j
    total_burgers = i + j

    if cola_time < min_cola or (cola_time == min_cola and total_burgers > max_burgers):
        min_cola = cola_time
        max_burgers = total_burgers

print(max_burgers, min_cola)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());
        int t = Integer.parseInt(st.nextToken());

        int minCola = t + 1;
        int maxBurgers = 0;

        for (int i = 0; i <= t / n; i++) {
            int remaining = t - n * i;
            int j = remaining / m;
            int colaTime = remaining - m * j;
            int totalBurgers = i + j;

            if (colaTime < minCola || (colaTime == minCola && totalBurgers > maxBurgers)) {
                minCola = colaTime;
                maxBurgers = totalBurgers;
            }
        }
        System.out.println(maxBurgers + " " + minCola);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    int n, m, t;
    cin >> n >> m >> t;

    int minCola = t + 1;
    int maxBurgers = 0;

    for (int i = 0; i <= t / n; i++) {
        int remaining = t - n * i;
        int j = remaining / m;
        int colaTime = remaining - m * j;
        int totalBurgers = i + j;

        if (colaTime < minCola || (colaTime == minCola && totalBurgers > maxBurgers)) {
            minCola = colaTime;
            maxBurgers = totalBurgers;
        }
    }
    cout << maxBurgers << " " << minCola << endl;
    return 0;
}
"""
            }
        ]
    },
    "27162": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
from collections import Counter

input = sys.stdin.readline

# 이미 선택한 족보 (Y: 선택함, N: 선택 안함)
used = input().strip()
# 고정된 주사위 3개
fixed = list(map(int, input().split()))

max_score = 0

for d1 in range(1, 7):
    for d2 in range(1, 7):
        dice = fixed + [d1, d2]
        count = Counter(dice)
        total = sum(dice)

        scores = [0] * 12

        # Ones ~ Sixes
        for i in range(6):
            scores[i] = count[i + 1] * (i + 1)

        # Four of a Kind
        if any(c >= 4 for c in count.values()):
            scores[6] = total

        # Full House
        vals = sorted(count.values())
        if vals == [2, 3] or vals == [5]:
            scores[7] = total

        # Little Straight
        if all(i in count for i in [1, 2, 3, 4, 5]):
            scores[8] = 30

        # Big Straight
        if all(i in count for i in [2, 3, 4, 5, 6]):
            scores[9] = 30

        # Yacht
        if any(c >= 5 for c in count.values()):
            scores[10] = 50

        # Choice
        scores[11] = total

        for i in range(12):
            if used[i] == 'N':
                max_score = max(max_score, scores[i])

print(max_score)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String used = br.readLine().trim();
        StringTokenizer st = new StringTokenizer(br.readLine());
        int[] fixed = new int[3];
        for (int i = 0; i < 3; i++) {
            fixed[i] = Integer.parseInt(st.nextToken());
        }

        int maxScore = 0;

        for (int d1 = 1; d1 <= 6; d1++) {
            for (int d2 = 1; d2 <= 6; d2++) {
                int[] dice = {fixed[0], fixed[1], fixed[2], d1, d2};
                int[] count = new int[7];
                int total = 0;
                for (int d : dice) {
                    count[d]++;
                    total += d;
                }

                int[] scores = new int[12];
                for (int i = 0; i < 6; i++) {
                    scores[i] = count[i + 1] * (i + 1);
                }

                for (int c : count) {
                    if (c >= 4) { scores[6] = total; break; }
                }

                boolean hasThree = false, hasTwo = false, hasFive = false;
                for (int c : count) {
                    if (c == 3) hasThree = true;
                    if (c == 2) hasTwo = true;
                    if (c == 5) hasFive = true;
                }
                if ((hasThree && hasTwo) || hasFive) scores[7] = total;

                if (count[1] >= 1 && count[2] >= 1 && count[3] >= 1 && count[4] >= 1 && count[5] >= 1) scores[8] = 30;
                if (count[2] >= 1 && count[3] >= 1 && count[4] >= 1 && count[5] >= 1 && count[6] >= 1) scores[9] = 30;

                for (int c : count) {
                    if (c >= 5) { scores[10] = 50; break; }
                }

                scores[11] = total;

                for (int i = 0; i < 12; i++) {
                    if (used.charAt(i) == 'N') {
                        maxScore = Math.max(maxScore, scores[i]);
                    }
                }
            }
        }
        System.out.println(maxScore);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string used;
    cin >> used;
    int fixed[3];
    for (int i = 0; i < 3; i++) cin >> fixed[i];

    int maxScore = 0;

    for (int d1 = 1; d1 <= 6; d1++) {
        for (int d2 = 1; d2 <= 6; d2++) {
            int dice[5] = {fixed[0], fixed[1], fixed[2], d1, d2};
            int count[7] = {0};
            int total = 0;
            for (int d : dice) { count[d]++; total += d; }

            int scores[12] = {0};
            for (int i = 0; i < 6; i++) scores[i] = count[i + 1] * (i + 1);

            for (int i = 1; i <= 6; i++) if (count[i] >= 4) { scores[6] = total; break; }

            bool hasThree = false, hasTwo = false, hasFive = false;
            for (int i = 1; i <= 6; i++) {
                if (count[i] == 3) hasThree = true;
                if (count[i] == 2) hasTwo = true;
                if (count[i] == 5) hasFive = true;
            }
            if ((hasThree && hasTwo) || hasFive) scores[7] = total;

            if (count[1] >= 1 && count[2] >= 1 && count[3] >= 1 && count[4] >= 1 && count[5] >= 1) scores[8] = 30;
            if (count[2] >= 1 && count[3] >= 1 && count[4] >= 1 && count[5] >= 1 && count[6] >= 1) scores[9] = 30;

            for (int i = 1; i <= 6; i++) if (count[i] >= 5) { scores[10] = 50; break; }

            scores[11] = total;

            for (int i = 0; i < 12; i++) {
                if (used[i] == 'N') maxScore = max(maxScore, scores[i]);
            }
        }
    }
    cout << maxScore << endl;
    return 0;
}
"""
            }
        ]
    },
    "27931": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

n = int(input())
points = list(map(int, input().split()))

# 홀수, 짝수 좌표 분리
odd = sorted([p for p in points if p % 2 == 1])
even = sorted([p for p in points if p % 2 == 0])

# 짝수 거리: 같은 패리티끼리
min_even = -1
for arr in [odd, even]:
    for i in range(len(arr) - 1):
        dist = arr[i + 1] - arr[i]
        if min_even == -1 or dist < min_even:
            min_even = dist

# 홀수 거리: 다른 패리티끼리
min_odd = -1
if odd and even:
    i, j = 0, 0
    while i < len(odd) and j < len(even):
        dist = abs(odd[i] - even[j])
        if min_odd == -1 or dist < min_odd:
            min_odd = dist
        if odd[i] < even[j]:
            i += 1
        else:
            j += 1

print(min_even, min_odd)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        List<Long> odd = new ArrayList<>();
        List<Long> even = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            long p = Long.parseLong(st.nextToken());
            if (p % 2 == 0) even.add(p);
            else odd.add(p);
        }

        Collections.sort(odd);
        Collections.sort(even);

        long minEven = -1;
        for (int i = 0; i < odd.size() - 1; i++) {
            long dist = odd.get(i + 1) - odd.get(i);
            if (minEven == -1 || dist < minEven) minEven = dist;
        }
        for (int i = 0; i < even.size() - 1; i++) {
            long dist = even.get(i + 1) - even.get(i);
            if (minEven == -1 || dist < minEven) minEven = dist;
        }

        long minOdd = -1;
        if (!odd.isEmpty() && !even.isEmpty()) {
            int i = 0, j = 0;
            while (i < odd.size() && j < even.size()) {
                long dist = Math.abs(odd.get(i) - even.get(j));
                if (minOdd == -1 || dist < minOdd) minOdd = dist;
                if (odd.get(i) < even.get(j)) i++;
                else j++;
            }
        }

        System.out.println(minEven + " " + minOdd);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    vector<long long> odd, even;
    for (int i = 0; i < n; i++) {
        long long p;
        cin >> p;
        if (p % 2 == 0) even.push_back(p);
        else odd.push_back(p);
    }

    sort(odd.begin(), odd.end());
    sort(even.begin(), even.end());

    long long minEven = -1;
    for (int i = 0; i < (int)odd.size() - 1; i++) {
        long long dist = odd[i + 1] - odd[i];
        if (minEven == -1 || dist < minEven) minEven = dist;
    }
    for (int i = 0; i < (int)even.size() - 1; i++) {
        long long dist = even[i + 1] - even[i];
        if (minEven == -1 || dist < minEven) minEven = dist;
    }

    long long minOdd = -1;
    if (!odd.empty() && !even.empty()) {
        int i = 0, j = 0;
        while (i < (int)odd.size() && j < (int)even.size()) {
            long long dist = abs(odd[i] - even[j]);
            if (minOdd == -1 || dist < minOdd) minOdd = dist;
            if (odd[i] < even[j]) i++;
            else j++;
        }
    }

    cout << minEven << " " << minOdd << endl;
    return 0;
}
"""
            }
        ]
    },
    "6324": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

n = int(input())

for i in range(1, n + 1):
    url = input().strip()

    # 프로토콜
    protocol_end = url.index('://')
    protocol = url[:protocol_end]
    rest = url[protocol_end + 3:]

    # 호스트
    host_end = len(rest)
    for j, c in enumerate(rest):
        if c == '/' or c == ':':
            host_end = j
            break
    host = rest[:host_end]
    rest = rest[host_end:]

    # 포트
    port = "<default>"
    if rest.startswith(':'):
        port_end = rest.find('/')
        if port_end == -1:
            port = rest[1:]
            rest = ""
        else:
            port = rest[1:port_end]
            rest = rest[port_end:]

    # 경로
    path = "<default>"
    if rest.startswith('/'):
        rest = rest[1:]
        if rest:
            path = rest

    print(f"URL #{i}")
    print(f"Protocol = {protocol}")
    print(f"Host     = {host}")
    print(f"Port     = {port}")
    print(f"Path     = {path}")

    if i < n:
        print()
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine().trim());

        for (int i = 1; i <= n; i++) {
            String url = br.readLine().trim();

            int protocolEnd = url.indexOf("://");
            String protocol = url.substring(0, protocolEnd);
            String rest = url.substring(protocolEnd + 3);

            int hostEnd = rest.length();
            for (int j = 0; j < rest.length(); j++) {
                char c = rest.charAt(j);
                if (c == '/' || c == ':') {
                    hostEnd = j;
                    break;
                }
            }
            String host = rest.substring(0, hostEnd);
            rest = rest.substring(hostEnd);

            String port = "<default>";
            if (rest.startsWith(":")) {
                int portEnd = rest.indexOf('/');
                if (portEnd == -1) {
                    port = rest.substring(1);
                    rest = "";
                } else {
                    port = rest.substring(1, portEnd);
                    rest = rest.substring(portEnd);
                }
            }

            String path = "<default>";
            if (rest.startsWith("/")) {
                rest = rest.substring(1);
                if (!rest.isEmpty()) path = rest;
            }

            sb.append("URL #").append(i).append("\\n");
            sb.append("Protocol = ").append(protocol).append("\\n");
            sb.append("Host     = ").append(host).append("\\n");
            sb.append("Port     = ").append(port).append("\\n");
            sb.append("Path     = ").append(path).append("\\n");

            if (i < n) sb.append("\\n");
        }
        System.out.print(sb);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    cin.ignore();

    for (int i = 1; i <= n; i++) {
        string url;
        getline(cin, url);

        size_t protocolEnd = url.find("://");
        string protocol = url.substr(0, protocolEnd);
        string rest = url.substr(protocolEnd + 3);

        size_t hostEnd = rest.length();
        for (size_t j = 0; j < rest.length(); j++) {
            if (rest[j] == '/' || rest[j] == ':') {
                hostEnd = j;
                break;
            }
        }
        string host = rest.substr(0, hostEnd);
        rest = rest.substr(hostEnd);

        string port = "<default>";
        if (!rest.empty() && rest[0] == ':') {
            size_t portEnd = rest.find('/');
            if (portEnd == string::npos) {
                port = rest.substr(1);
                rest = "";
            } else {
                port = rest.substr(1, portEnd - 1);
                rest = rest.substr(portEnd);
            }
        }

        string path = "<default>";
        if (!rest.empty() && rest[0] == '/') {
            rest = rest.substr(1);
            if (!rest.empty()) path = rest;
        }

        cout << "URL #" << i << "\\n";
        cout << "Protocol = " << protocol << "\\n";
        cout << "Host     = " << host << "\\n";
        cout << "Port     = " << port << "\\n";
        cout << "Path     = " << path << "\\n";

        if (i < n) cout << "\\n";
    }
    return 0;
}
"""
            }
        ]
    },
    "17124": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
from bisect import bisect_left

input = sys.stdin.readline

t = int(input())

for _ in range(t):
    n, m = map(int, input().split())
    A = list(map(int, input().split()))
    B = sorted(map(int, input().split()))

    total = 0
    for a in A:
        idx = bisect_left(B, a)
        candidates = []
        if idx > 0:
            candidates.append(B[idx - 1])
        if idx < m:
            candidates.append(B[idx])
        closest = min(candidates, key=lambda x: (abs(x - a), x))
        total += closest

    print(total)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int m = Integer.parseInt(st.nextToken());

            int[] A = new int[n];
            st = new StringTokenizer(br.readLine());
            for (int i = 0; i < n; i++) A[i] = Integer.parseInt(st.nextToken());

            int[] B = new int[m];
            st = new StringTokenizer(br.readLine());
            for (int i = 0; i < m; i++) B[i] = Integer.parseInt(st.nextToken());
            Arrays.sort(B);

            long total = 0;
            for (int a : A) {
                int idx = Arrays.binarySearch(B, a);
                if (idx < 0) idx = -(idx + 1);

                int closest;
                if (idx == 0) closest = B[0];
                else if (idx == m) closest = B[m - 1];
                else {
                    int left = B[idx - 1];
                    int right = B[idx];
                    closest = (a - left <= right - a) ? left : right;
                }
                total += closest;
            }
            sb.append(total).append("\\n");
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
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int n, m;
        cin >> n >> m;

        vector<int> A(n), B(m);
        for (int i = 0; i < n; i++) cin >> A[i];
        for (int i = 0; i < m; i++) cin >> B[i];
        sort(B.begin(), B.end());

        long long total = 0;
        for (int a : A) {
            int idx = lower_bound(B.begin(), B.end(), a) - B.begin();

            int closest;
            if (idx == 0) closest = B[0];
            else if (idx == m) closest = B[m - 1];
            else {
                int left = B[idx - 1];
                int right = B[idx];
                closest = (a - left <= right - a) ? left : right;
            }
            total += closest;
        }
        cout << total << "\\n";
    }
    return 0;
}
"""
            }
        ]
    },
    "19948": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

poem = input().strip()
space_limit = int(input())
alpha_limits = list(map(int, input().split()))

space_count = 0
alpha_count = [0] * 26
title_chars = []

prev_space = True
for c in poem:
    if c == ' ':
        space_count += 1
        prev_space = True
    else:
        upper_c = c.upper()
        idx = ord(upper_c) - ord('A')
        alpha_count[idx] += 1
        if prev_space:
            title_chars.append(upper_c)
        prev_space = False

for c in title_chars:
    idx = ord(c) - ord('A')
    alpha_count[idx] += 1

if space_count > space_limit:
    print(-1)
else:
    possible = True
    for i in range(26):
        if alpha_count[i] > alpha_limits[i]:
            possible = False
            break

    if possible:
        print(''.join(title_chars))
    else:
        print(-1)
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        String poem = br.readLine();
        int spaceLimit = Integer.parseInt(br.readLine().trim());
        int[] alphaLimits = new int[26];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < 26; i++) alphaLimits[i] = Integer.parseInt(st.nextToken());

        int spaceCount = 0;
        int[] alphaCount = new int[26];
        StringBuilder title = new StringBuilder();

        boolean prevSpace = true;
        for (int i = 0; i < poem.length(); i++) {
            char c = poem.charAt(i);
            if (c == ' ') {
                spaceCount++;
                prevSpace = true;
            } else {
                char upperC = Character.toUpperCase(c);
                int idx = upperC - 'A';
                alphaCount[idx]++;
                if (prevSpace) title.append(upperC);
                prevSpace = false;
            }
        }

        for (int i = 0; i < title.length(); i++) {
            int idx = title.charAt(i) - 'A';
            alphaCount[idx]++;
        }

        if (spaceCount > spaceLimit) {
            System.out.println(-1);
            return;
        }

        for (int i = 0; i < 26; i++) {
            if (alphaCount[i] > alphaLimits[i]) {
                System.out.println(-1);
                return;
            }
        }
        System.out.println(title);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <string>
#include <cctype>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string poem;
    getline(cin, poem);

    int spaceLimit;
    cin >> spaceLimit;

    int alphaLimits[26];
    for (int i = 0; i < 26; i++) cin >> alphaLimits[i];

    int spaceCount = 0;
    int alphaCount[26] = {0};
    string title = "";

    bool prevSpace = true;
    for (char c : poem) {
        if (c == ' ') {
            spaceCount++;
            prevSpace = true;
        } else {
            char upperC = toupper(c);
            int idx = upperC - 'A';
            alphaCount[idx]++;
            if (prevSpace) title += upperC;
            prevSpace = false;
        }
    }

    for (char c : title) {
        int idx = c - 'A';
        alphaCount[idx]++;
    }

    if (spaceCount > spaceLimit) {
        cout << -1 << endl;
        return 0;
    }

    for (int i = 0; i < 26; i++) {
        if (alphaCount[i] > alphaLimits[i]) {
            cout << -1 << endl;
            return 0;
        }
    }
    cout << title << endl;
    return 0;
}
"""
            }
        ]
    },
    "11507": {
        "solutions": [
            {
                "language": "python",
                "code": """import sys
input = sys.stdin.readline

cards = input().strip()

# 모양별 카드 존재 여부
suits = {'P': [False] * 14, 'K': [False] * 14, 'H': [False] * 14, 'T': [False] * 14}

error = False

i = 0
while i < len(cards):
    suit = cards[i]
    num = int(cards[i+1:i+3])

    if suits[suit][num]:
        error = True
        break
    suits[suit][num] = True
    i += 3

if error:
    print("GRESKA")
else:
    result = []
    for suit in ['P', 'K', 'H', 'T']:
        count = sum(1 for j in range(1, 14) if not suits[suit][j])
        result.append(count)
    print(' '.join(map(str, result)))
"""
            },
            {
                "language": "java",
                "code": """import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String cards = br.readLine().trim();

        boolean[][] suits = new boolean[4][14];
        boolean error = false;

        for (int i = 0; i < cards.length(); i += 3) {
            int suitIdx = getSuitIdx(cards.charAt(i));
            int num = Integer.parseInt(cards.substring(i + 1, i + 3));

            if (suits[suitIdx][num]) {
                error = true;
                break;
            }
            suits[suitIdx][num] = true;
        }

        if (error) {
            System.out.println("GRESKA");
        } else {
            StringBuilder sb = new StringBuilder();
            for (int s = 0; s < 4; s++) {
                int count = 0;
                for (int j = 1; j <= 13; j++) {
                    if (!suits[s][j]) count++;
                }
                if (s > 0) sb.append(" ");
                sb.append(count);
            }
            System.out.println(sb);
        }
    }

    static int getSuitIdx(char c) {
        if (c == 'P') return 0;
        if (c == 'K') return 1;
        if (c == 'H') return 2;
        return 3;
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """#include <iostream>
#include <string>
using namespace std;

int getSuitIdx(char c) {
    if (c == 'P') return 0;
    if (c == 'K') return 1;
    if (c == 'H') return 2;
    return 3;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string cards;
    cin >> cards;

    bool suits[4][14] = {false};
    bool error = false;

    for (int i = 0; i < (int)cards.length(); i += 3) {
        int suitIdx = getSuitIdx(cards[i]);
        int num = stoi(cards.substr(i + 1, 2));

        if (suits[suitIdx][num]) {
            error = true;
            break;
        }
        suits[suitIdx][num] = true;
    }

    if (error) {
        cout << "GRESKA" << endl;
    } else {
        for (int s = 0; s < 4; s++) {
            int count = 0;
            for (int j = 1; j <= 13; j++) {
                if (!suits[s][j]) count++;
            }
            if (s > 0) cout << " ";
            cout << count;
        }
        cout << endl;
    }
    return 0;
}
"""
            }
        ]
    }
}

if __name__ == "__main__":
    # Read existing file
    with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'r') as f:
        data = json.load(f)

    # Add new solutions
    data.update(new_solutions)

    # Save
    with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Added {len(new_solutions)} new solutions")
    print("New problem IDs:", list(new_solutions.keys()))
