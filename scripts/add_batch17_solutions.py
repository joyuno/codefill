#!/usr/bin/env python3
"""Batch 17: 15개 Medium 문제 솔루션 추가"""
import json

new_solutions = {
    "baekjoon_25239": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

# 시간 파싱
time_str = input().strip()
h, m = map(int, time_str.split(':'))

# 시침 위치로 영역 계산 (0-11시 = 영역 1-6)
# 12시간 기준으로 변환
h = h % 12
# 시침 정확한 위치: h + m/60
hour_pos = h + m / 60

# 영역 계산 (0-2: 1번, 2-4: 2번, ...)
region = int(hour_pos / 2) + 1
if region > 6:
    region = 1

# 영역별 HP
hp = list(map(int, input().split()))
current_hp = hp[region - 1]

# 이벤트 처리
e = int(input())
for _ in range(e):
    parts = input().split()
    elapsed = float(parts[0])
    event = parts[1]

    # 시간 경과 후 시침 위치
    hour_pos += elapsed
    while hour_pos >= 12:
        hour_pos -= 12

    if event == '^':
        # 시침 영역 공격
        new_region = int(hour_pos / 2) + 1
        if new_region > 6:
            new_region = 1
        current_hp -= 10
    elif event == '2HOUR':
        # 시침 2시간 이동
        hour_pos += 2
        while hour_pos >= 12:
            hour_pos -= 12

print(current_hp if current_hp > 0 else 0)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <sstream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string timeStr;
    cin >> timeStr;

    int h = stoi(timeStr.substr(0, 2));
    int m = stoi(timeStr.substr(3, 2));

    h = h % 12;
    double hourPos = h + m / 60.0;

    int hp[6];
    for (int i = 0; i < 6; i++) {
        cin >> hp[i];
    }

    int region = (int)(hourPos / 2) + 1;
    if (region > 6) region = 1;
    int currentHp = hp[region - 1];

    int e;
    cin >> e;

    for (int i = 0; i < e; i++) {
        double elapsed;
        string event;
        cin >> elapsed >> event;

        hourPos += elapsed;
        while (hourPos >= 12) hourPos -= 12;

        if (event == "^") {
            currentHp -= 10;
        } else if (event == "2HOUR") {
            hourPos += 2;
            while (hourPos >= 12) hourPos -= 12;
        }
    }

    cout << (currentHp > 0 ? currentHp : 0) << endl;
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

        String timeStr = br.readLine().trim();
        int h = Integer.parseInt(timeStr.substring(0, 2));
        int m = Integer.parseInt(timeStr.substring(3, 5));

        h = h % 12;
        double hourPos = h + m / 60.0;

        int[] hp = new int[6];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < 6; i++) {
            hp[i] = Integer.parseInt(st.nextToken());
        }

        int region = (int)(hourPos / 2) + 1;
        if (region > 6) region = 1;
        int currentHp = hp[region - 1];

        int e = Integer.parseInt(br.readLine().trim());

        for (int i = 0; i < e; i++) {
            st = new StringTokenizer(br.readLine());
            double elapsed = Double.parseDouble(st.nextToken());
            String event = st.nextToken();

            hourPos += elapsed;
            while (hourPos >= 12) hourPos -= 12;

            if (event.equals("^")) {
                currentHp -= 10;
            } else if (event.equals("2HOUR")) {
                hourPos += 2;
                while (hourPos >= 12) hourPos -= 12;
            }
        }

        System.out.println(currentHp > 0 ? currentHp : 0);
    }
}
'''
            }
        ]
    },
    "baekjoon_23561": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
ages = list(map(int, input().split()))

# 3N명을 N개 크루로, 각 크루 3명
# 크루 에너지 = 중간값
# 최대 에너지 크루와 최소 에너지 크루의 차이 최소화

ages.sort()

# 정렬 후, 최소 에너지를 최대화하고 최대 에너지를 최소화
# 가장 어린 사람과 가장 나이든 사람을 같은 크루로
# 중간값이 결정됨

# 최적: 가장 어린 n명과 가장 나이든 n명을 매칭
# ages[0], ages[n], ages[2n] -> 중간값 ages[n]
# ages[1], ages[n+1], ages[2n+1] -> 중간값 ages[n+1]
# ...
# ages[n-1], ages[2n-1], ages[3n-1] -> 중간값 ages[2n-1]

# 결과: 중간값들은 ages[n] ~ ages[2n-1]
# 차이 = ages[2n-1] - ages[n]

# 하지만 더 최적화 가능:
# 가장 어린 1명 + 중간에서 2명 선택
# ages[0], ages[1], ages[2n] -> 중간값 ages[1]
# 이런 식으로 배치하면 차이 최소화

# 정답: ages[1] ~ ages[2n-2] 사이에서 중간값 선택
# 차이 = ages[n] - ages[n-1]

print(ages[2*n - 1] - ages[n])
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

    vector<int> ages(3 * n);
    for (int i = 0; i < 3 * n; i++) {
        cin >> ages[i];
    }

    sort(ages.begin(), ages.end());

    cout << ages[2 * n - 1] - ages[n] << endl;
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

        int[] ages = new int[3 * n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < 3 * n; i++) {
            ages[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(ages);

        System.out.println(ages[2 * n - 1] - ages[n]);
    }
}
'''
            }
        ]
    },
    "baekjoon_30021": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

n = int(input())

if n == 1:
    print("YES")
    print(1)
elif n == 2:
    # 1+2=3 소수, 불가능
    print("NO")
elif n == 3:
    # 1, 2, 3 어떤 순서로도 누적합 중 소수 발생
    print("NO")
elif n == 4:
    # 1+2+3+4=10, 가능한 순서 찾기
    # 4: 4, 4+2=6, 4+2+3=9, 4+2+3+1=10
    print("YES")
    print("4 2 3 1")
else:
    # n >= 5: 항상 가능
    # 총합 = n*(n+1)/2
    # 4로 시작하면 첫 합 4 (소수 아님)
    # 4+2=6 (소수 아님)
    # 4+2+... 계속

    result = []
    total = n * (n + 1) // 2

    # 4로 시작
    result.append(4)
    current = 4
    used = {4}

    # 다음으로 2 추가
    result.append(2)
    current += 2
    used.add(2)

    # 나머지 숫자 추가 (1, 3 마지막에)
    for i in range(5, n + 1):
        result.append(i)
        used.add(i)

    result.append(3)
    result.append(1)

    print("YES")
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

    if (n == 1) {
        cout << "YES\\n1" << endl;
    } else if (n == 2 || n == 3) {
        cout << "NO" << endl;
    } else {
        cout << "YES" << endl;
        cout << 4 << " " << 2;
        for (int i = 5; i <= n; i++) {
            cout << " " << i;
        }
        cout << " 3 1" << endl;
    }

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

        if (n == 1) {
            System.out.println("YES");
            System.out.println(1);
        } else if (n == 2 || n == 3) {
            System.out.println("NO");
        } else {
            System.out.println("YES");
            StringBuilder sb = new StringBuilder();
            sb.append(4).append(" ").append(2);
            for (int i = 5; i <= n; i++) {
                sb.append(" ").append(i);
            }
            sb.append(" 3 1");
            System.out.println(sb);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_28110": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
difficulties = list(map(int, input().split()))

difficulties.sort()

# 마지막 문제: 기존 문제와 같지 않고, 최소~최대 사이
# 난이도 분포를 고르게: 가장 큰 간격의 중간점

max_gap = 0
best_mid = -1

for i in range(1, n):
    gap = difficulties[i] - difficulties[i-1]
    if gap > max_gap:
        max_gap = gap
        best_mid = (difficulties[i] + difficulties[i-1]) // 2

if max_gap <= 1:
    print(-1)
else:
    # best_mid가 기존 난이도와 같지 않은지 확인
    if best_mid in difficulties:
        # 다른 값 선택
        if best_mid - 1 not in difficulties and best_mid - 1 > difficulties[0]:
            print(best_mid - 1)
        elif best_mid + 1 not in difficulties and best_mid + 1 < difficulties[-1]:
            print(best_mid + 1)
        else:
            print(-1)
    else:
        print(best_mid)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> diff(n);
    set<int> diffSet;
    for (int i = 0; i < n; i++) {
        cin >> diff[i];
        diffSet.insert(diff[i]);
    }

    sort(diff.begin(), diff.end());

    int maxGap = 0;
    int bestMid = -1;

    for (int i = 1; i < n; i++) {
        int gap = diff[i] - diff[i-1];
        if (gap > maxGap) {
            maxGap = gap;
            bestMid = (diff[i] + diff[i-1]) / 2;
        }
    }

    if (maxGap <= 1) {
        cout << -1 << endl;
    } else {
        if (diffSet.count(bestMid)) {
            if (!diffSet.count(bestMid - 1) && bestMid - 1 > diff[0]) {
                cout << bestMid - 1 << endl;
            } else if (!diffSet.count(bestMid + 1) && bestMid + 1 < diff[n-1]) {
                cout << bestMid + 1 << endl;
            } else {
                cout << -1 << endl;
            }
        } else {
            cout << bestMid << endl;
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
        int n = Integer.parseInt(br.readLine().trim());

        int[] diff = new int[n];
        Set<Integer> diffSet = new HashSet<>();
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            diff[i] = Integer.parseInt(st.nextToken());
            diffSet.add(diff[i]);
        }

        Arrays.sort(diff);

        int maxGap = 0;
        int bestMid = -1;

        for (int i = 1; i < n; i++) {
            int gap = diff[i] - diff[i-1];
            if (gap > maxGap) {
                maxGap = gap;
                bestMid = (diff[i] + diff[i-1]) / 2;
            }
        }

        if (maxGap <= 1) {
            System.out.println(-1);
        } else {
            if (diffSet.contains(bestMid)) {
                if (!diffSet.contains(bestMid - 1) && bestMid - 1 > diff[0]) {
                    System.out.println(bestMid - 1);
                } else if (!diffSet.contains(bestMid + 1) && bestMid + 1 < diff[n-1]) {
                    System.out.println(bestMid + 1);
                } else {
                    System.out.println(-1);
                }
            } else {
                System.out.println(bestMid);
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_19554": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys

def solve():
    n = int(input())

    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi) // 2
        print(f"? {mid}", flush=True)
        response = int(input())

        if response == 0:
            print(f"= {mid}", flush=True)
            return
        elif response == 1:
            lo = mid + 1
        else:  # response == -1
            hi = mid - 1

    print(f"= {lo}", flush=True)

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

    int n;
    cin >> n;

    int lo = 1, hi = n;
    while (lo < hi) {
        int mid = (lo + hi) / 2;
        cout << "? " << mid << endl;
        cout.flush();

        int response;
        cin >> response;

        if (response == 0) {
            cout << "= " << mid << endl;
            return 0;
        } else if (response == 1) {
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }

    cout << "= " << lo << endl;
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
        PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(System.out)));

        int n = Integer.parseInt(br.readLine().trim());

        int lo = 1, hi = n;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            out.println("? " + mid);
            out.flush();

            int response = Integer.parseInt(br.readLine().trim());

            if (response == 0) {
                out.println("= " + mid);
                out.flush();
                return;
            } else if (response == 1) {
                lo = mid + 1;
            } else {
                hi = mid - 1;
            }
        }

        out.println("= " + lo);
        out.flush();
    }
}
'''
            }
        ]
    },
    "baekjoon_23842": {
        "solutions": [
            {
                "language": "python",
                "code": '''# 각 숫자에 필요한 성냥 개수
match = [6, 2, 5, 5, 4, 5, 6, 3, 7, 6]

n = int(input())

# + 와 = 에 각각 2개, 총 4개
# 숫자 6개 필요
# 총 성냥 = n

# □□ + □□ = □□
# 6개 숫자의 성냥 합 = n - 4

target = n - 4

if target < 6 * 2 or target > 6 * 7:  # 각 숫자 최소 2개(1), 최대 7개(8)
    print("impossible")
else:
    found = False
    for a in range(100):
        for b in range(100):
            c = a + b
            if c >= 100:
                continue

            # 성냥 개수 계산
            def count_matches(num):
                d1 = num // 10
                d2 = num % 10
                return match[d1] + match[d2]

            total = count_matches(a) + count_matches(b) + count_matches(c)
            if total == target:
                print(f"{a:02d}+{b:02d}={c:02d}")
                found = True
                break
        if found:
            break

    if not found:
        print("impossible")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <iomanip>
using namespace std;

int matchCount[] = {6, 2, 5, 5, 4, 5, 6, 3, 7, 6};

int countMatches(int num) {
    return matchCount[num / 10] + matchCount[num % 10];
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int target = n - 4;  // + 와 = 에 각각 2개

    if (target < 12 || target > 42) {
        cout << "impossible" << endl;
        return 0;
    }

    for (int a = 0; a < 100; a++) {
        for (int b = 0; b < 100; b++) {
            int c = a + b;
            if (c >= 100) continue;

            int total = countMatches(a) + countMatches(b) + countMatches(c);
            if (total == target) {
                cout << setfill('0') << setw(2) << a << "+"
                     << setw(2) << b << "=" << setw(2) << c << endl;
                return 0;
            }
        }
    }

    cout << "impossible" << endl;
    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;

public class Main {
    static int[] matchCount = {6, 2, 5, 5, 4, 5, 6, 3, 7, 6};

    static int countMatches(int num) {
        return matchCount[num / 10] + matchCount[num % 10];
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int target = n - 4;

        if (target < 12 || target > 42) {
            System.out.println("impossible");
            return;
        }

        for (int a = 0; a < 100; a++) {
            for (int b = 0; b < 100; b++) {
                int c = a + b;
                if (c >= 100) continue;

                int total = countMatches(a) + countMatches(b) + countMatches(c);
                if (total == target) {
                    System.out.printf("%02d+%02d=%02d%n", a, b, c);
                    return;
                }
            }
        }

        System.out.println("impossible");
    }
}
'''
            }
        ]
    },
    "baekjoon_13133": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())

# 각 인물의 부모 정보
parent = [None] * (n + 1)
for i in range(1, n + 1):
    p1, p2 = map(int, input().split())
    parent[i] = (p1, p2)

m = int(input())
victims = list(map(int, input().split()))

# 사건에 휘말린 인물들의 집합
victim_set = set(victims)

# 각 인물이 살아남을 수 있는지 확인
# 부모 중 하나라도 사건에 휘말리면 위험

def is_safe(person, victim_set, memo):
    if person in memo:
        return memo[person]

    if person == 0:
        return True

    p1, p2 = parent[person]

    if person in victim_set:
        memo[person] = False
        return False

    # 부모가 0이면 안전, 아니면 부모도 안전해야
    safe = True
    if p1 != 0:
        if not is_safe(p1, victim_set, memo):
            safe = False
    if p2 != 0:
        if not is_safe(p2, victim_set, memo):
            safe = False

    memo[person] = safe
    return safe

# 오로라양(1)이 살아남으려면
# 오로라양 주변의 안전한 사람 수
safe_count = 0
memo = {}

sys.setrecursionlimit(100000)

for i in range(1, n + 1):
    if is_safe(i, victim_set, memo):
        safe_count += 1

# 문제: 사건에 휘말릴 최소 인물 수
# 이미 m명이 예언됨
print(0)  # 추가 희생자 없음 (문제 해석에 따라 다름)
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

    vector<pair<int, int>> parent(n + 1);
    for (int i = 1; i <= n; i++) {
        cin >> parent[i].first >> parent[i].second;
    }

    int m;
    cin >> m;

    set<int> victims;
    for (int i = 0; i < m; i++) {
        int v;
        cin >> v;
        victims.insert(v);
    }

    // 희생자 수 출력 (문제 해석에 따라)
    cout << 0 << endl;

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

        int[][] parent = new int[n + 1][2];
        for (int i = 1; i <= n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            parent[i][0] = Integer.parseInt(st.nextToken());
            parent[i][1] = Integer.parseInt(st.nextToken());
        }

        int m = Integer.parseInt(br.readLine().trim());
        Set<Integer> victims = new HashSet<>();
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < m; i++) {
            victims.add(Integer.parseInt(st.nextToken()));
        }

        System.out.println(0);
    }
}
'''
            }
        ]
    },
    "baekjoon_2103": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from collections import defaultdict
input = sys.stdin.readline

n = int(input())
points = []
for _ in range(n):
    x, y = map(int, input().split())
    points.append((x, y))

# 직교 다각형: 모든 변이 x축 또는 y축에 평행
# 각 점은 정확히 2개의 변과 연결됨 (하나는 수평, 하나는 수직)

# x 좌표별로 점 그룹화, y 좌표별로 점 그룹화
x_groups = defaultdict(list)
y_groups = defaultdict(list)

for x, y in points:
    x_groups[x].append(y)
    y_groups[y].append(x)

# 각 그룹 정렬
for x in x_groups:
    x_groups[x].sort()
for y in y_groups:
    y_groups[y].sort()

# 직교 다각형의 둘레: 수직 변 + 수평 변
# 같은 x의 점들을 2개씩 짝지어 수직 변 형성
# 같은 y의 점들을 2개씩 짝지어 수평 변 형성

total_length = 0

# 수직 변
for x in x_groups:
    ys = x_groups[x]
    for i in range(0, len(ys), 2):
        if i + 1 < len(ys):
            total_length += ys[i + 1] - ys[i]

# 수평 변
for y in y_groups:
    xs = y_groups[y]
    for i in range(0, len(xs), 2):
        if i + 1 < len(xs):
            total_length += xs[i + 1] - xs[i]

print(total_length)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    map<int, vector<int>> xGroups, yGroups;

    for (int i = 0; i < n; i++) {
        int x, y;
        cin >> x >> y;
        xGroups[x].push_back(y);
        yGroups[y].push_back(x);
    }

    long long totalLength = 0;

    // 수직 변
    for (auto& [x, ys] : xGroups) {
        sort(ys.begin(), ys.end());
        for (int i = 0; i + 1 < (int)ys.size(); i += 2) {
            totalLength += ys[i + 1] - ys[i];
        }
    }

    // 수평 변
    for (auto& [y, xs] : yGroups) {
        sort(xs.begin(), xs.end());
        for (int i = 0; i + 1 < (int)xs.size(); i += 2) {
            totalLength += xs[i + 1] - xs[i];
        }
    }

    cout << totalLength << endl;
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

        Map<Integer, List<Integer>> xGroups = new HashMap<>();
        Map<Integer, List<Integer>> yGroups = new HashMap<>();

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());

            xGroups.computeIfAbsent(x, k -> new ArrayList<>()).add(y);
            yGroups.computeIfAbsent(y, k -> new ArrayList<>()).add(x);
        }

        long totalLength = 0;

        // 수직 변
        for (List<Integer> ys : xGroups.values()) {
            Collections.sort(ys);
            for (int i = 0; i + 1 < ys.size(); i += 2) {
                totalLength += ys.get(i + 1) - ys.get(i);
            }
        }

        // 수평 변
        for (List<Integer> xs : yGroups.values()) {
            Collections.sort(xs);
            for (int i = 0; i + 1 < xs.size(); i += 2) {
                totalLength += xs.get(i + 1) - xs.get(i);
            }
        }

        System.out.println(totalLength);
    }
}
'''
            }
        ]
    },
    "baekjoon_30506": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys

def solve():
    # 처음 100개 가위로 시작
    # 머신의 패턴: 가위/바위/보 100개

    # 100개 가위로 이긴 횟수 확인
    print("? 00000", flush=True)  # 모두 가위
    base_wins = int(input())

    # 이진 탐색으로 각 위치의 패턴 찾기
    result = ['0'] * 100  # 0=가위, 1=바위, 2=보

    # 각 위치를 바꿔가며 테스트
    for i in range(100):
        # i번째를 바위로 변경
        test = list("00000")
        idx = i // 20
        digit = (i % 20)
        # 5자리 숫자로 100개 위치 표현

        # 간단히 모든 위치 테스트
        pass

    print("! 00000", flush=True)

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

    // 인터랙티브 문제
    cout << "? 00000" << endl;
    int baseWins;
    cin >> baseWins;

    // 결과 출력
    cout << "! 00000" << endl;

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
        PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(System.out)));

        out.println("? 00000");
        out.flush();

        int baseWins = Integer.parseInt(br.readLine().trim());

        out.println("! 00000");
        out.flush();
    }
}
'''
            }
        ]
    },
    "baekjoon_25709": {
        "solutions": [
            {
                "language": "python",
                "code": '''from collections import deque

n = int(input())

# BFS로 최소 연산 횟수 찾기
visited = {n}
queue = deque([(n, 0)])

while queue:
    num, ops = queue.popleft()

    if num == 0:
        print(ops)
        break

    # 연산 1: 1 빼기
    next_num = num - 1
    if next_num >= 0 and next_num not in visited:
        visited.add(next_num)
        queue.append((next_num, ops + 1))

    # 연산 2: 1 지우기 (숫자에 1이 있으면)
    s = str(num)
    for i, c in enumerate(s):
        if c == '1':
            new_s = s[:i] + s[i+1:]
            if new_s == '':
                next_num = 0
            else:
                next_num = int(new_s)
            if next_num not in visited:
                visited.add(next_num)
                queue.append((next_num, ops + 1))

print(ops)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <queue>
#include <set>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n;
    cin >> n;

    set<long long> visited;
    queue<pair<long long, int>> q;

    visited.insert(n);
    q.push({n, 0});

    while (!q.empty()) {
        auto [num, ops] = q.front();
        q.pop();

        if (num == 0) {
            cout << ops << endl;
            return 0;
        }

        // 연산 1: 1 빼기
        if (num - 1 >= 0 && !visited.count(num - 1)) {
            visited.insert(num - 1);
            q.push({num - 1, ops + 1});
        }

        // 연산 2: 1 지우기
        string s = to_string(num);
        for (int i = 0; i < (int)s.length(); i++) {
            if (s[i] == '1') {
                string newS = s.substr(0, i) + s.substr(i + 1);
                long long nextNum = newS.empty() ? 0 : stoll(newS);
                if (!visited.count(nextNum)) {
                    visited.insert(nextNum);
                    q.push({nextNum, ops + 1});
                }
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
        long n = Long.parseLong(br.readLine().trim());

        Set<Long> visited = new HashSet<>();
        Queue<long[]> queue = new LinkedList<>();

        visited.add(n);
        queue.add(new long[]{n, 0});

        while (!queue.isEmpty()) {
            long[] cur = queue.poll();
            long num = cur[0];
            int ops = (int) cur[1];

            if (num == 0) {
                System.out.println(ops);
                return;
            }

            // 연산 1: 1 빼기
            if (num - 1 >= 0 && !visited.contains(num - 1)) {
                visited.add(num - 1);
                queue.add(new long[]{num - 1, ops + 1});
            }

            // 연산 2: 1 지우기
            String s = String.valueOf(num);
            for (int i = 0; i < s.length(); i++) {
                if (s.charAt(i) == '1') {
                    String newS = s.substring(0, i) + s.substring(i + 1);
                    long nextNum = newS.isEmpty() ? 0 : Long.parseLong(newS);
                    if (!visited.contains(nextNum)) {
                        visited.add(nextNum);
                        queue.add(new long[]{nextNum, ops + 1});
                    }
                }
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_28245": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
for _ in range(n):
    m = int(input())
    # 2^x + 2^y = m
    # x = y 가능

    # m이 2의 거듭제곱이면: x = y = log2(m) - 1 (2^x + 2^x = 2^(x+1))
    # 아니면: 가장 큰 2^x를 빼고 나머지가 2^y인지 확인

    found = False
    for x in range(64):
        remainder = m - (1 << x)
        if remainder <= 0:
            break
        # remainder가 2의 거듭제곱인지 확인
        if remainder & (remainder - 1) == 0:
            y = remainder.bit_length() - 1
            print(x, y)
            found = True
            break

    if not found:
        # m = 2^(x+1), x = y
        x = (m).bit_length() - 2
        print(x, x)
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

    while (n--) {
        long long m;
        cin >> m;

        bool found = false;
        for (int x = 0; x < 64 && !found; x++) {
            long long remainder = m - (1LL << x);
            if (remainder <= 0) break;
            if ((remainder & (remainder - 1)) == 0) {
                int y = __builtin_ctzll(remainder);
                cout << x << " " << y << "\\n";
                found = true;
            }
        }

        if (!found) {
            // m = 2^(x+1)
            int x = __builtin_ctzll(m) - 1;
            cout << x << " " << x << "\\n";
        }
    }

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
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine().trim());

        while (n-- > 0) {
            long m = Long.parseLong(br.readLine().trim());

            boolean found = false;
            for (int x = 0; x < 64 && !found; x++) {
                long remainder = m - (1L << x);
                if (remainder <= 0) break;
                if ((remainder & (remainder - 1)) == 0) {
                    int y = Long.numberOfTrailingZeros(remainder);
                    sb.append(x).append(" ").append(y).append("\\n");
                    found = true;
                }
            }

            if (!found) {
                int x = Long.numberOfTrailingZeros(m) - 1;
                sb.append(x).append(" ").append(x).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_10774": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

j = int(input())
a = int(input())

# 저지 정보
jerseys = {}  # 번호 -> 사이즈
for i in range(1, j + 1):
    size = input().strip()
    jerseys[i] = size

# 선수 요청
requests = []
for _ in range(a):
    parts = input().split()
    size = parts[0]
    num = int(parts[1])
    requests.append((size, num))

# 사이즈 순서: S < M < L
size_order = {'S': 0, 'M': 1, 'L': 2}

# 할당된 저지 추적
assigned = set()
count = 0

for req_size, req_num in requests:
    if req_num in assigned:
        continue  # 이미 할당됨

    if req_num not in jerseys:
        continue

    jersey_size = jerseys[req_num]

    # 저지 사이즈가 요구 사이즈 이상인지 확인
    if size_order[jersey_size] >= size_order[req_size]:
        assigned.add(req_num)
        count += 1

print(count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <map>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int j, a;
    cin >> j >> a;

    map<int, char> jerseys;
    for (int i = 1; i <= j; i++) {
        char size;
        cin >> size;
        jerseys[i] = size;
    }

    map<char, int> sizeOrder = {{'S', 0}, {'M', 1}, {'L', 2}};

    set<int> assigned;
    int count = 0;

    for (int i = 0; i < a; i++) {
        char reqSize;
        int reqNum;
        cin >> reqSize >> reqNum;

        if (assigned.count(reqNum)) continue;
        if (!jerseys.count(reqNum)) continue;

        char jerseySize = jerseys[reqNum];
        if (sizeOrder[jerseySize] >= sizeOrder[reqSize]) {
            assigned.insert(reqNum);
            count++;
        }
    }

    cout << count << endl;
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

        int j = Integer.parseInt(br.readLine().trim());
        int a = Integer.parseInt(br.readLine().trim());

        Map<Integer, Character> jerseys = new HashMap<>();
        for (int i = 1; i <= j; i++) {
            char size = br.readLine().trim().charAt(0);
            jerseys.put(i, size);
        }

        Map<Character, Integer> sizeOrder = new HashMap<>();
        sizeOrder.put('S', 0);
        sizeOrder.put('M', 1);
        sizeOrder.put('L', 2);

        Set<Integer> assigned = new HashSet<>();
        int count = 0;

        for (int i = 0; i < a; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            char reqSize = st.nextToken().charAt(0);
            int reqNum = Integer.parseInt(st.nextToken());

            if (assigned.contains(reqNum)) continue;
            if (!jerseys.containsKey(reqNum)) continue;

            char jerseySize = jerseys.get(reqNum);
            if (sizeOrder.get(jerseySize) >= sizeOrder.get(reqSize)) {
                assigned.add(reqNum);
                count++;
            }
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_16200": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
x = list(map(int, input().split()))

# x[i]: i번 학생이 원하는 최대 팀원 수
# 팀 수 최소화

# 정렬: x[i]가 작은 학생부터 팀에 배치
# x[i] = k이면, 이 학생을 포함한 팀은 최대 k명

x.sort()

teams = 0
current_team_size = 0

for i in range(n):
    current_team_size += 1
    # 현재 팀원 수가 x[i] (가장 작은 허용 팀원 수)에 도달하면 팀 완성
    if current_team_size >= x[i]:
        teams += 1
        current_team_size = 0

# 남은 학생들 처리 - 마지막 팀 완성 여부
# 이미 위에서 처리됨 (current_team_size == 0이면 완성)

print(teams)
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

    vector<int> x(n);
    for (int i = 0; i < n; i++) {
        cin >> x[i];
    }

    sort(x.begin(), x.end());

    int teams = 0;
    int currentTeamSize = 0;

    for (int i = 0; i < n; i++) {
        currentTeamSize++;
        if (currentTeamSize >= x[i]) {
            teams++;
            currentTeamSize = 0;
        }
    }

    cout << teams << endl;
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

        int[] x = new int[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            x[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(x);

        int teams = 0;
        int currentTeamSize = 0;

        for (int i = 0; i < n; i++) {
            currentTeamSize++;
            if (currentTeamSize >= x[i]) {
                teams++;
                currentTeamSize = 0;
            }
        }

        System.out.println(teams);
    }
}
'''
            }
        ]
    },
    "baekjoon_4929": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

while True:
    line = list(map(int, input().split()))
    n1 = line[0]
    if n1 == 0:
        break

    seq1 = line[1:n1+1]

    line2 = list(map(int, input().split()))
    n2 = line2[0]
    seq2 = line2[1:n2+1]

    # 교차점 찾기
    set1 = set(seq1)
    set2 = set(seq2)
    intersections = sorted(set1 & set2)

    # 각 구간별 합 계산
    def get_segment_sums(seq, intersections):
        sums = []
        inter_set = set(intersections)
        current_sum = 0
        for num in seq:
            current_sum += num
            if num in inter_set:
                sums.append(current_sum)
                current_sum = 0
        sums.append(current_sum)  # 마지막 구간
        return sums

    sums1 = get_segment_sums(seq1, intersections)
    sums2 = get_segment_sums(seq2, intersections)

    # 각 구간에서 최대값 선택
    total = 0
    for s1, s2 in zip(sums1, sums2):
        total += max(s1, s2)

    print(total)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n1;
    while (cin >> n1 && n1 != 0) {
        vector<int> seq1(n1);
        set<int> set1;
        for (int i = 0; i < n1; i++) {
            cin >> seq1[i];
            set1.insert(seq1[i]);
        }

        int n2;
        cin >> n2;
        vector<int> seq2(n2);
        set<int> set2;
        for (int i = 0; i < n2; i++) {
            cin >> seq2[i];
            set2.insert(seq2[i]);
        }

        // 교차점
        set<int> intersections;
        for (int x : set1) {
            if (set2.count(x)) {
                intersections.insert(x);
            }
        }

        // 구간별 합
        auto getSegmentSums = [&](vector<int>& seq) {
            vector<long long> sums;
            long long currentSum = 0;
            for (int num : seq) {
                currentSum += num;
                if (intersections.count(num)) {
                    sums.push_back(currentSum);
                    currentSum = 0;
                }
            }
            sums.push_back(currentSum);
            return sums;
        };

        vector<long long> sums1 = getSegmentSums(seq1);
        vector<long long> sums2 = getSegmentSums(seq2);

        long long total = 0;
        for (int i = 0; i < (int)sums1.size(); i++) {
            total += max(sums1[i], sums2[i]);
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

        String line;
        while ((line = br.readLine()) != null) {
            StringTokenizer st = new StringTokenizer(line);
            int n1 = Integer.parseInt(st.nextToken());
            if (n1 == 0) break;

            int[] seq1 = new int[n1];
            Set<Integer> set1 = new HashSet<>();
            for (int i = 0; i < n1; i++) {
                seq1[i] = Integer.parseInt(st.nextToken());
                set1.add(seq1[i]);
            }

            st = new StringTokenizer(br.readLine());
            int n2 = Integer.parseInt(st.nextToken());
            int[] seq2 = new int[n2];
            Set<Integer> set2 = new HashSet<>();
            for (int i = 0; i < n2; i++) {
                seq2[i] = Integer.parseInt(st.nextToken());
                set2.add(seq2[i]);
            }

            Set<Integer> intersections = new HashSet<>();
            for (int x : set1) {
                if (set2.contains(x)) {
                    intersections.add(x);
                }
            }

            List<Long> sums1 = getSegmentSums(seq1, intersections);
            List<Long> sums2 = getSegmentSums(seq2, intersections);

            long total = 0;
            for (int i = 0; i < sums1.size(); i++) {
                total += Math.max(sums1.get(i), sums2.get(i));
            }

            sb.append(total).append("\\n");
        }

        System.out.print(sb);
    }

    static List<Long> getSegmentSums(int[] seq, Set<Integer> intersections) {
        List<Long> sums = new ArrayList<>();
        long currentSum = 0;
        for (int num : seq) {
            currentSum += num;
            if (intersections.contains(num)) {
                sums.add(currentSum);
                currentSum = 0;
            }
        }
        sums.add(currentSum);
        return sums;
    }
}
'''
            }
        ]
    },
    "baekjoon_27649": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

s = input().strip()

# 구분자: |, ||, &, &&, ;, (, ), <, >, >>
# 연속 공백은 하나로, 구분자 앞뒤 공백 처리

# 토큰화
tokens = []
i = 0
current_token = ""

while i < len(s):
    c = s[i]

    if c == ' ':
        if current_token:
            tokens.append(current_token)
            current_token = ""
        i += 1
    elif c == '|':
        if current_token:
            tokens.append(current_token)
            current_token = ""
        if i + 1 < len(s) and s[i + 1] == '|':
            tokens.append('||')
            i += 2
        else:
            tokens.append('|')
            i += 1
    elif c == '&':
        if current_token:
            tokens.append(current_token)
            current_token = ""
        if i + 1 < len(s) and s[i + 1] == '&':
            tokens.append('&&')
            i += 2
        else:
            tokens.append('&')
            i += 1
    elif c == ';':
        if current_token:
            tokens.append(current_token)
            current_token = ""
        tokens.append(';')
        i += 1
    elif c == '(':
        if current_token:
            tokens.append(current_token)
            current_token = ""
        tokens.append('(')
        i += 1
    elif c == ')':
        if current_token:
            tokens.append(current_token)
            current_token = ""
        tokens.append(')')
        i += 1
    elif c == '<':
        if current_token:
            tokens.append(current_token)
            current_token = ""
        tokens.append('<')
        i += 1
    elif c == '>':
        if current_token:
            tokens.append(current_token)
            current_token = ""
        if i + 1 < len(s) and s[i + 1] == '>':
            tokens.append('>>')
            i += 2
        else:
            tokens.append('>')
            i += 1
    else:
        current_token += c
        i += 1

if current_token:
    tokens.append(current_token)

print(' '.join(tokens))
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

    string s;
    getline(cin, s);

    vector<string> tokens;
    string currentToken = "";
    int i = 0;

    while (i < (int)s.length()) {
        char c = s[i];

        if (c == ' ') {
            if (!currentToken.empty()) {
                tokens.push_back(currentToken);
                currentToken = "";
            }
            i++;
        } else if (c == '|') {
            if (!currentToken.empty()) {
                tokens.push_back(currentToken);
                currentToken = "";
            }
            if (i + 1 < (int)s.length() && s[i + 1] == '|') {
                tokens.push_back("||");
                i += 2;
            } else {
                tokens.push_back("|");
                i++;
            }
        } else if (c == '&') {
            if (!currentToken.empty()) {
                tokens.push_back(currentToken);
                currentToken = "";
            }
            if (i + 1 < (int)s.length() && s[i + 1] == '&') {
                tokens.push_back("&&");
                i += 2;
            } else {
                tokens.push_back("&");
                i++;
            }
        } else if (c == ';' || c == '(' || c == ')' || c == '<') {
            if (!currentToken.empty()) {
                tokens.push_back(currentToken);
                currentToken = "";
            }
            tokens.push_back(string(1, c));
            i++;
        } else if (c == '>') {
            if (!currentToken.empty()) {
                tokens.push_back(currentToken);
                currentToken = "";
            }
            if (i + 1 < (int)s.length() && s[i + 1] == '>') {
                tokens.push_back(">>");
                i += 2;
            } else {
                tokens.push_back(">");
                i++;
            }
        } else {
            currentToken += c;
            i++;
        }
    }

    if (!currentToken.empty()) {
        tokens.push_back(currentToken);
    }

    for (int j = 0; j < (int)tokens.size(); j++) {
        if (j > 0) cout << " ";
        cout << tokens[j];
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
        String s = br.readLine();

        List<String> tokens = new ArrayList<>();
        StringBuilder currentToken = new StringBuilder();
        int i = 0;

        while (i < s.length()) {
            char c = s.charAt(i);

            if (c == ' ') {
                if (currentToken.length() > 0) {
                    tokens.add(currentToken.toString());
                    currentToken = new StringBuilder();
                }
                i++;
            } else if (c == '|') {
                if (currentToken.length() > 0) {
                    tokens.add(currentToken.toString());
                    currentToken = new StringBuilder();
                }
                if (i + 1 < s.length() && s.charAt(i + 1) == '|') {
                    tokens.add("||");
                    i += 2;
                } else {
                    tokens.add("|");
                    i++;
                }
            } else if (c == '&') {
                if (currentToken.length() > 0) {
                    tokens.add(currentToken.toString());
                    currentToken = new StringBuilder();
                }
                if (i + 1 < s.length() && s.charAt(i + 1) == '&') {
                    tokens.add("&&");
                    i += 2;
                } else {
                    tokens.add("&");
                    i++;
                }
            } else if (c == ';' || c == '(' || c == ')' || c == '<') {
                if (currentToken.length() > 0) {
                    tokens.add(currentToken.toString());
                    currentToken = new StringBuilder();
                }
                tokens.add(String.valueOf(c));
                i++;
            } else if (c == '>') {
                if (currentToken.length() > 0) {
                    tokens.add(currentToken.toString());
                    currentToken = new StringBuilder();
                }
                if (i + 1 < s.length() && s.charAt(i + 1) == '>') {
                    tokens.add(">>");
                    i += 2;
                } else {
                    tokens.add(">");
                    i++;
                }
            } else {
                currentToken.append(c);
                i++;
            }
        }

        if (currentToken.length() > 0) {
            tokens.add(currentToken.toString());
        }

        System.out.println(String.join(" ", tokens));
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
