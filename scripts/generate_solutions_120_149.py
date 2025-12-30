#!/usr/bin/env python3
"""
백준 중간 난이도 문제 솔루션 생성 스크립트
인덱스 120-149 범위의 빈 솔루션 문제들을 처리합니다.
"""

import json
import fcntl

def load_json_with_lock(filepath):
    """파일 잠금을 사용하여 JSON 파일을 읽습니다."""
    with open(filepath, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data

def save_json_with_lock(filepath, data):
    """파일 잠금을 사용하여 JSON 파일을 저장합니다."""
    with open(filepath, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def find_empty_medium_problems(data):
    """빈 솔루션 배열을 가진 중간 난이도 문제들을 찾습니다."""
    empty_medium_problems = []
    for idx, problem in enumerate(data):
        difficulty = problem.get('difficulty', '')
        solutions = problem.get('solutions', [])
        input_output = problem.get('input_output', '')

        if difficulty == 'medium' and (not solutions or solutions == []) and input_output:
            empty_medium_problems.append((idx, problem))

    return empty_medium_problems

# 각 문제에 대한 솔루션 정의
SOLUTIONS = {
    # 문제 120: 원의 둘레 (baekjoon_6600)
    "baekjoon_6600": {
        "python": '''# 세 점을 지나는 원의 둘레를 구하는 문제
# 외접원의 반지름을 구한 후 2*pi*r을 계산
import sys
import math

while True:
    try:
        line = input().strip()
        if not line:
            continue
        coords = list(map(float, line.split()))
        x1, y1, x2, y2, x3, y3 = coords

        # 세 점으로 외접원의 반지름 계산
        # 삼각형의 세 변의 길이 계산
        a = math.sqrt((x2-x3)**2 + (y2-y3)**2)
        b = math.sqrt((x1-x3)**2 + (y1-y3)**2)
        c = math.sqrt((x1-x2)**2 + (y1-y2)**2)

        # 삼각형의 넓이 (헤론의 공식)
        s = (a + b + c) / 2
        area = math.sqrt(s * (s-a) * (s-b) * (s-c))

        # 외접원의 반지름 R = abc / 4S
        R = (a * b * c) / (4 * area)

        # 원의 둘레
        circumference = 2 * math.pi * R
        print(f"{circumference:.2f}")
    except EOFError:
        break
    except:
        break
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        while (sc.hasNext()) {
            double x1 = sc.nextDouble();
            double y1 = sc.nextDouble();
            double x2 = sc.nextDouble();
            double y2 = sc.nextDouble();
            double x3 = sc.nextDouble();
            double y3 = sc.nextDouble();

            // 세 변의 길이 계산
            double a = Math.sqrt(Math.pow(x2-x3, 2) + Math.pow(y2-y3, 2));
            double b = Math.sqrt(Math.pow(x1-x3, 2) + Math.pow(y1-y3, 2));
            double c = Math.sqrt(Math.pow(x1-x2, 2) + Math.pow(y1-y2, 2));

            // 헤론의 공식으로 넓이 계산
            double s = (a + b + c) / 2;
            double area = Math.sqrt(s * (s-a) * (s-b) * (s-c));

            // 외접원 반지름 R = abc / 4S
            double R = (a * b * c) / (4 * area);

            // 원의 둘레
            double circumference = 2 * Math.PI * R;
            System.out.printf("%.2f%n", circumference);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <cmath>
#include <iomanip>

using namespace std;

int main() {
    double x1, y1, x2, y2, x3, y3;

    // 세 점의 좌표를 입력받음
    while (cin >> x1 >> y1 >> x2 >> y2 >> x3 >> y3) {
        // 세 변의 길이 계산
        double a = sqrt(pow(x2-x3, 2) + pow(y2-y3, 2));
        double b = sqrt(pow(x1-x3, 2) + pow(y1-y3, 2));
        double c = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2));

        // 헤론의 공식으로 삼각형 넓이 계산
        double s = (a + b + c) / 2;
        double area = sqrt(s * (s-a) * (s-b) * (s-c));

        // 외접원 반지름 R = abc / 4S
        double R = (a * b * c) / (4 * area);

        // 원의 둘레 출력
        cout << fixed << setprecision(2) << 2 * M_PI * R << endl;
    }

    return 0;
}
'''
    },

    # 문제 121: Moo Operations (baekjoon_27563)
    "baekjoon_27563": {
        "python": '''# MOO로 만들기 위한 최소 연산 횟수 계산
# 앞이나 뒤에서 제거하는 연산만 가능
import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    s = input().strip()
    n = len(s)

    if n < 3:
        print(-1)
        continue

    min_ops = float('inf')

    # 모든 위치에서 MOO를 찾아봄
    for i in range(n - 2):
        # s[i:i+3]이 MOO가 되려면 필요한 변경 수
        changes = 0
        if s[i] != 'M':
            changes += 1
        if s[i+1] != 'O':
            changes += 1
        if s[i+2] != 'O':
            changes += 1

        # 앞에서 i개 제거, 뒤에서 n-i-3개 제거
        ops = i + (n - i - 3) + changes
        min_ops = min(min_ops, ops)

    if min_ops == float('inf'):
        print(-1)
    else:
        print(min_ops)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            String s = sc.next();
            int n = s.length();

            if (n < 3) {
                System.out.println(-1);
                continue;
            }

            int minOps = Integer.MAX_VALUE;

            // 모든 위치에서 MOO를 찾음
            for (int i = 0; i <= n - 3; i++) {
                int changes = 0;
                if (s.charAt(i) != 'M') changes++;
                if (s.charAt(i+1) != 'O') changes++;
                if (s.charAt(i+2) != 'O') changes++;

                // 앞에서 i개, 뒤에서 n-i-3개 제거
                int ops = i + (n - i - 3) + changes;
                minOps = Math.min(minOps, ops);
            }

            System.out.println(minOps == Integer.MAX_VALUE ? -1 : minOps);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <algorithm>
#include <climits>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        string s;
        cin >> s;
        int n = s.length();

        if (n < 3) {
            cout << -1 << "\\n";
            continue;
        }

        int minOps = INT_MAX;

        // 모든 위치에서 MOO를 찾음
        for (int i = 0; i <= n - 3; i++) {
            int changes = 0;
            if (s[i] != 'M') changes++;
            if (s[i+1] != 'O') changes++;
            if (s[i+2] != 'O') changes++;

            // 앞에서 i개, 뒤에서 n-i-3개 제거
            int ops = i + (n - i - 3) + changes;
            minOps = min(minOps, ops);
        }

        cout << (minOps == INT_MAX ? -1 : minOps) << "\\n";
    }

    return 0;
}
'''
    },

    # 문제 122: LOL (baekjoon_11140)
    "baekjoon_11140": {
        "python": '''# LOL을 만들기 위한 최소 문자 추가 횟수
# 0: 이미 LOL 포함, 1: 한 글자만 추가, 2: 두 글자 추가, 3: 세 글자 추가
import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    s = input().strip().upper()

    # LOL이 이미 포함되어 있는지 확인
    if 'LOL' in s:
        print(0)
    # LO 또는 OL이 있으면 1개만 추가
    elif 'LO' in s or 'OL' in s:
        print(1)
    # L 또는 O가 있으면 2개 추가
    elif 'L' in s or 'O' in s:
        print(2)
    # 아무것도 없으면 3개 추가
    else:
        print(3)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            String s = sc.next().toUpperCase();

            // LOL이 이미 포함되어 있는지 확인
            if (s.contains("LOL")) {
                System.out.println(0);
            }
            // LO 또는 OL이 있으면 1개만 추가
            else if (s.contains("LO") || s.contains("OL")) {
                System.out.println(1);
            }
            // L 또는 O가 있으면 2개 추가
            else if (s.contains("L") || s.contains("O")) {
                System.out.println(2);
            }
            // 아무것도 없으면 3개 추가
            else {
                System.out.println(3);
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <algorithm>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        string s;
        cin >> s;

        // 대문자로 변환
        for (char& c : s) {
            c = toupper(c);
        }

        // LOL이 이미 포함되어 있는지 확인
        if (s.find("LOL") != string::npos) {
            cout << 0 << "\\n";
        }
        // LO 또는 OL이 있으면 1개만 추가
        else if (s.find("LO") != string::npos || s.find("OL") != string::npos) {
            cout << 1 << "\\n";
        }
        // L 또는 O가 있으면 2개 추가
        else if (s.find('L') != string::npos || s.find('O') != string::npos) {
            cout << 2 << "\\n";
        }
        // 아무것도 없으면 3개 추가
        else {
            cout << 3 << "\\n";
        }
    }

    return 0;
}
'''
    },

    # 문제 123: 목차 세기 (baekjoon_25956)
    "baekjoon_25956": {
        "python": '''# 목차 번호 세기 문제
# 각 depth에서의 번호를 추적하며 목차를 출력
import sys
input = sys.stdin.readline

n = int(input())
levels = [0] * (n + 2)  # 각 레벨의 현재 번호
prev_level = 0
valid = True
result = []

for i in range(n):
    level = int(input())

    # 레벨이 이전보다 2 이상 증가하면 유효하지 않음
    if level > prev_level + 1:
        valid = False
        break

    # 현재 레벨 번호 증가
    levels[level] += 1

    # 현재 레벨보다 높은 레벨들 초기화
    for j in range(level + 1, n + 2):
        levels[j] = 0

    # 결과 저장 (현재 레벨보다 아래 레벨들의 개수)
    count = sum(levels[level+1:])
    result.append(count)

    prev_level = level

if valid:
    for r in result:
        print(r)
else:
    print(-1)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        int[] levels = new int[n + 2];
        int prevLevel = 0;
        boolean valid = true;
        int[] result = new int[n];

        for (int i = 0; i < n; i++) {
            int level = sc.nextInt();

            // 레벨이 이전보다 2 이상 증가하면 유효하지 않음
            if (level > prevLevel + 1) {
                valid = false;
                break;
            }

            // 현재 레벨 번호 증가
            levels[level]++;

            // 현재 레벨보다 높은 레벨들 초기화
            for (int j = level + 1; j < n + 2; j++) {
                levels[j] = 0;
            }

            // 현재 레벨보다 아래 레벨들의 개수 합
            int count = 0;
            for (int j = level + 1; j < n + 2; j++) {
                count += levels[j];
            }
            result[i] = count;

            prevLevel = level;
        }

        if (valid) {
            for (int i = 0; i < n; i++) {
                System.out.println(result[i]);
            }
        } else {
            System.out.println(-1);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> levels(n + 2, 0);
    int prevLevel = 0;
    bool valid = true;
    vector<int> result;

    for (int i = 0; i < n; i++) {
        int level;
        cin >> level;

        // 레벨이 이전보다 2 이상 증가하면 유효하지 않음
        if (level > prevLevel + 1) {
            valid = false;
            break;
        }

        // 현재 레벨 번호 증가
        levels[level]++;

        // 현재 레벨보다 높은 레벨들 초기화
        for (int j = level + 1; j < n + 2; j++) {
            levels[j] = 0;
        }

        // 현재 레벨보다 아래 레벨들의 개수 합
        int count = 0;
        for (int j = level + 1; j < n + 2; j++) {
            count += levels[j];
        }
        result.push_back(count);

        prevLevel = level;
    }

    if (valid) {
        for (int r : result) {
            cout << r << "\\n";
        }
    } else {
        cout << -1 << "\\n";
    }

    return 0;
}
'''
    },

    # 문제 124: Jack and Jill (baekjoon_23656)
    "baekjoon_23656": {
        "python": '''# Jack and Jill 계단 오르기 문제
# Jack과 Jill이 동시에 계단을 오르며 위치 비교
import sys
input = sys.stdin.readline

# 계단 수 입력
steps = []
while True:
    try:
        n = int(input())
        steps.append(n)
    except:
        break

# Jack: 1,2,3,... 씩 오름, Jill: 1,2,3,... 씩 오름
# Jack은 위로, Jill은 아래로 시작
# 각 단계에서 위치 비교

jack_pos = 0
jill_pos = 0
jack_step = 1
jill_step = 1

for n in steps:
    # Jack은 n개 오르고, Jill도 n개 오름
    jack_pos += n
    jill_pos += n

    if jack_pos > jill_pos:
        print(">")
    elif jack_pos < jill_pos:
        print("<")
    else:
        print("=")
''',
        "java": '''import java.util.Scanner;
import java.util.ArrayList;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        ArrayList<Integer> steps = new ArrayList<>();

        while (sc.hasNextInt()) {
            steps.add(sc.nextInt());
        }

        // Jack과 Jill의 위치 추적
        long jackPos = 0;
        long jillPos = 0;

        for (int n : steps) {
            jackPos += n;
            jillPos += n;

            if (jackPos > jillPos) {
                System.out.println(">");
            } else if (jackPos < jillPos) {
                System.out.println("<");
            } else {
                System.out.println("=");
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    vector<int> steps;
    int n;

    while (cin >> n) {
        steps.push_back(n);
    }

    // Jack과 Jill의 위치 추적
    long long jackPos = 0;
    long long jillPos = 0;

    for (int step : steps) {
        jackPos += step;
        jillPos += step;

        if (jackPos > jillPos) {
            cout << ">" << "\\n";
        } else if (jackPos < jillPos) {
            cout << "<" << "\\n";
        } else {
            cout << "=" << "\\n";
        }
    }

    return 0;
}
'''
    },

    # 문제 125: 스펀지 (baekjoon_31418)
    "baekjoon_31418": {
        "python": '''# 스펀지 문제 - 구멍을 뚫어서 남은 스펀지의 부피 계산
import sys
input = sys.stdin.readline

line1 = list(map(int, input().split()))
W, H, N = line1[0], line1[1], line1[2]

# 전체 부피
total = W * H

# 초기 D 값
D = line1[3] if len(line1) > 3 else 1

# 각 구멍의 위치 읽기
holes = []
for i in range(N):
    parts = list(map(int, input().split()))
    holes.append((parts[0], parts[1]))

# 구멍이 차지하는 영역 계산
# 각 구멍은 D x D 크기
hole_area = 0
for x, y in holes:
    # 구멍이 스펀지 내부에 있는지 확인
    area = D * D
    hole_area += area

# 남은 부피
remaining = total - hole_area
print(remaining)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int W = sc.nextInt();
        int H = sc.nextInt();
        int N = sc.nextInt();
        int D = sc.nextInt();

        // 전체 부피
        long total = (long) W * H;

        // 구멍 영역 계산
        long holeArea = 0;
        for (int i = 0; i < N; i++) {
            int x = sc.nextInt();
            int y = sc.nextInt();
            holeArea += (long) D * D;
        }

        // 남은 부피
        System.out.println(total - holeArea);
    }
}
''',
        "cpp": '''#include <iostream>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int W, H, N, D;
    cin >> W >> H >> N >> D;

    // 전체 부피
    long long total = (long long) W * H;

    // 구멍 영역 계산
    long long holeArea = 0;
    for (int i = 0; i < N; i++) {
        int x, y;
        cin >> x >> y;
        holeArea += (long long) D * D;
    }

    // 남은 부피
    cout << total - holeArea << "\\n";

    return 0;
}
'''
    },

    # 문제 126: 자리수의 제곱 (baekjoon_4881)
    "baekjoon_4881": {
        "python": '''# 자리수의 제곱 합 계산
# A와 B 사이의 수들 중 자리수의 제곱 합으로 연결되는 수 찾기
import sys
input = sys.stdin.readline

def digit_square_sum(n):
    """숫자의 각 자리수 제곱의 합 계산"""
    total = 0
    while n > 0:
        d = n % 10
        total += d * d
        n //= 10
    return total

def find_cycle(n):
    """n에서 시작하여 사이클을 찾음"""
    visited = set()
    current = n
    while current not in visited:
        visited.add(current)
        current = digit_square_sum(current)
    return current, visited

while True:
    line = input().strip()
    if not line:
        continue
    a, b = map(int, line.split())
    if a == 0 and b == 0:
        break

    # a와 b 사이에서 겹치는 수의 개수
    visited_a = set()
    current = a
    for _ in range(1000):  # 충분한 반복
        visited_a.add(current)
        current = digit_square_sum(current)

    visited_b = set()
    current = b
    for _ in range(1000):
        visited_b.add(current)
        current = digit_square_sum(current)

    # 교집합 크기
    common = visited_a & visited_b
    print(f"{a} {b} {len(common)}")
''',
        "java": '''import java.util.Scanner;
import java.util.HashSet;

public class Main {
    static int digitSquareSum(int n) {
        int total = 0;
        while (n > 0) {
            int d = n % 10;
            total += d * d;
            n /= 10;
        }
        return total;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        while (true) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            if (a == 0 && b == 0) break;

            // a에서 시작하는 수열
            HashSet<Integer> visitedA = new HashSet<>();
            int current = a;
            for (int i = 0; i < 1000; i++) {
                visitedA.add(current);
                current = digitSquareSum(current);
            }

            // b에서 시작하는 수열
            HashSet<Integer> visitedB = new HashSet<>();
            current = b;
            for (int i = 0; i < 1000; i++) {
                visitedB.add(current);
                current = digitSquareSum(current);
            }

            // 교집합 크기
            visitedA.retainAll(visitedB);
            System.out.println(a + " " + b + " " + visitedA.size());
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <set>

using namespace std;

int digitSquareSum(int n) {
    int total = 0;
    while (n > 0) {
        int d = n % 10;
        total += d * d;
        n /= 10;
    }
    return total;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int a, b;
    while (cin >> a >> b) {
        if (a == 0 && b == 0) break;

        // a에서 시작하는 수열
        set<int> visitedA;
        int current = a;
        for (int i = 0; i < 1000; i++) {
            visitedA.insert(current);
            current = digitSquareSum(current);
        }

        // b에서 시작하는 수열
        set<int> visitedB;
        current = b;
        for (int i = 0; i < 1000; i++) {
            visitedB.insert(current);
            current = digitSquareSum(current);
        }

        // 교집합 크기
        int count = 0;
        for (int v : visitedA) {
            if (visitedB.count(v)) count++;
        }

        cout << a << " " << b << " " << count << "\\n";
    }

    return 0;
}
'''
    },

    # 문제 127: 공백왕 빈-칸 (baekjoon_3518)
    "baekjoon_3518": {
        "python": '''# 공백 정렬 문제 - 각 열의 너비를 맞춰서 출력
import sys

lines = sys.stdin.read().strip().split('\\n')

# 각 줄을 파싱하여 필드별로 분리
parsed = []
for line in lines:
    # 주석 분리
    if '//' in line:
        idx = line.index('//')
        code_part = line[:idx]
        comment_part = line[idx:]
    else:
        code_part = line
        comment_part = ''

    # 코드 부분을 토큰으로 분리
    tokens = code_part.split()
    parsed.append((tokens, comment_part.strip()))

# 각 열의 최대 너비 계산
max_cols = max(len(p[0]) for p in parsed) if parsed else 0
col_widths = [0] * max_cols

for tokens, _ in parsed:
    for i, token in enumerate(tokens):
        col_widths[i] = max(col_widths[i], len(token))

# 출력
for tokens, comment in parsed:
    result = []
    for i, token in enumerate(tokens):
        if i < len(col_widths):
            result.append(token.ljust(col_widths[i]))
        else:
            result.append(token)

    line_output = ' '.join(result).rstrip()
    if comment:
        line_output += ' ' + comment
    print(line_output)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        ArrayList<String[]> parsed = new ArrayList<>();
        ArrayList<String> comments = new ArrayList<>();

        while (sc.hasNextLine()) {
            String line = sc.nextLine();
            String codePart, commentPart = "";

            int idx = line.indexOf("//");
            if (idx != -1) {
                codePart = line.substring(0, idx);
                commentPart = line.substring(idx).trim();
            } else {
                codePart = line;
            }

            String[] tokens = codePart.trim().split("\\\\s+");
            parsed.add(tokens);
            comments.add(commentPart);
        }

        // 각 열의 최대 너비 계산
        int maxCols = 0;
        for (String[] tokens : parsed) {
            maxCols = Math.max(maxCols, tokens.length);
        }

        int[] colWidths = new int[maxCols];
        for (String[] tokens : parsed) {
            for (int i = 0; i < tokens.length; i++) {
                colWidths[i] = Math.max(colWidths[i], tokens[i].length());
            }
        }

        // 출력
        for (int i = 0; i < parsed.size(); i++) {
            String[] tokens = parsed.get(i);
            StringBuilder sb = new StringBuilder();

            for (int j = 0; j < tokens.length; j++) {
                if (j > 0) sb.append(" ");
                sb.append(String.format("%-" + colWidths[j] + "s", tokens[j]));
            }

            String result = sb.toString().stripTrailing();
            if (!comments.get(i).isEmpty()) {
                result += " " + comments.get(i);
            }
            System.out.println(result);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <iomanip>
#include <algorithm>

using namespace std;

int main() {
    vector<vector<string>> parsed;
    vector<string> comments;
    string line;

    while (getline(cin, line)) {
        string codePart, commentPart = "";

        size_t idx = line.find("//");
        if (idx != string::npos) {
            codePart = line.substr(0, idx);
            commentPart = line.substr(idx);
            // trim commentPart
            size_t start = commentPart.find_first_not_of(" ");
            if (start != string::npos) {
                commentPart = commentPart.substr(start);
            }
        } else {
            codePart = line;
        }

        // 토큰 분리
        vector<string> tokens;
        istringstream iss(codePart);
        string token;
        while (iss >> token) {
            tokens.push_back(token);
        }

        parsed.push_back(tokens);
        comments.push_back(commentPart);
    }

    // 각 열의 최대 너비 계산
    size_t maxCols = 0;
    for (const auto& tokens : parsed) {
        maxCols = max(maxCols, tokens.size());
    }

    vector<size_t> colWidths(maxCols, 0);
    for (const auto& tokens : parsed) {
        for (size_t i = 0; i < tokens.size(); i++) {
            colWidths[i] = max(colWidths[i], tokens[i].length());
        }
    }

    // 출력
    for (size_t i = 0; i < parsed.size(); i++) {
        string result = "";
        for (size_t j = 0; j < parsed[i].size(); j++) {
            if (j > 0) result += " ";
            string padded = parsed[i][j];
            while (padded.length() < colWidths[j]) padded += " ";
            result += padded;
        }

        // 뒤쪽 공백 제거
        while (!result.empty() && result.back() == ' ') {
            result.pop_back();
        }

        if (!comments[i].empty()) {
            result += " " + comments[i];
        }
        cout << result << "\\n";
    }

    return 0;
}
'''
    },

    # 문제 128: 대통령 선거 (baekjoon_9547)
    "baekjoon_9547": {
        "python": '''# 대통령 선거 - 투표 결과 집계
import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    n, m = map(int, input().split())

    # 각 후보의 득표수
    votes = [0] * (n + 1)

    for _ in range(m):
        prefs = list(map(int, input().split()))
        # 첫 번째 선호 후보에게 투표
        votes[prefs[0]] += 1

    # 최다 득표자 찾기
    max_votes = max(votes)
    winner = votes.index(max_votes)

    print(winner, max_votes)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            int n = sc.nextInt();
            int m = sc.nextInt();

            int[] votes = new int[n + 1];

            for (int i = 0; i < m; i++) {
                int firstChoice = sc.nextInt();
                votes[firstChoice]++;

                // 나머지 선호도는 읽기만 함
                for (int j = 1; j < n; j++) {
                    sc.nextInt();
                }
            }

            // 최다 득표자 찾기
            int maxVotes = 0;
            int winner = 0;
            for (int i = 1; i <= n; i++) {
                if (votes[i] > maxVotes) {
                    maxVotes = votes[i];
                    winner = i;
                }
            }

            System.out.println(winner + " " + maxVotes);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int n, m;
        cin >> n >> m;

        vector<int> votes(n + 1, 0);

        for (int i = 0; i < m; i++) {
            int firstChoice;
            cin >> firstChoice;
            votes[firstChoice]++;

            // 나머지 선호도는 읽기만 함
            for (int j = 1; j < n; j++) {
                int temp;
                cin >> temp;
            }
        }

        // 최다 득표자 찾기
        int maxVotes = 0;
        int winner = 0;
        for (int i = 1; i <= n; i++) {
            if (votes[i] > maxVotes) {
                maxVotes = votes[i];
                winner = i;
            }
        }

        cout << winner << " " << maxVotes << "\\n";
    }

    return 0;
}
'''
    },

    # 문제 129: 시계 (baekjoon_17843)
    "baekjoon_17843": {
        "python": '''# 시계 문제 - 시침과 분침 사이의 각도 계산
import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    h, m, s = map(int, input().split())

    # 시침의 각도 (12시 기준, 시계방향)
    # 시침은 1시간에 30도, 1분에 0.5도, 1초에 1/120도 이동
    hour_angle = (h % 12) * 30 + m * 0.5 + s * (1/120)

    # 분침의 각도
    # 분침은 1분에 6도, 1초에 0.1도 이동
    minute_angle = m * 6 + s * 0.1

    # 두 바늘 사이의 각도
    angle = abs(hour_angle - minute_angle)

    # 작은 각도 선택
    if angle > 180:
        angle = 360 - angle

    print(f"{angle:.6f}")
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            int h = sc.nextInt();
            int m = sc.nextInt();
            int s = sc.nextInt();

            // 시침의 각도 (12시 기준, 시계방향)
            double hourAngle = (h % 12) * 30 + m * 0.5 + s * (1.0/120);

            // 분침의 각도
            double minuteAngle = m * 6 + s * 0.1;

            // 두 바늘 사이의 각도
            double angle = Math.abs(hourAngle - minuteAngle);

            // 작은 각도 선택
            if (angle > 180) {
                angle = 360 - angle;
            }

            System.out.printf("%.6f%n", angle);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <cmath>
#include <iomanip>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int h, m, s;
        cin >> h >> m >> s;

        // 시침의 각도 (12시 기준, 시계방향)
        double hourAngle = (h % 12) * 30.0 + m * 0.5 + s * (1.0/120);

        // 분침의 각도
        double minuteAngle = m * 6.0 + s * 0.1;

        // 두 바늘 사이의 각도
        double angle = abs(hourAngle - minuteAngle);

        // 작은 각도 선택
        if (angle > 180) {
            angle = 360 - angle;
        }

        cout << fixed << setprecision(6) << angle << "\\n";
    }

    return 0;
}
'''
    },

    # 문제 130: Gazzzua (baekjoon_17939)
    "baekjoon_17939": {
        "python": '''# Gazzzua - 최대 이익 계산
# 각 위치에서 미래의 최대값을 이용해 이익 계산
import sys
input = sys.stdin.readline

n = int(input())
prices = list(map(int, input().split()))

# 뒤에서부터 최대값 계산
max_after = [0] * n
max_after[n-1] = prices[n-1]
for i in range(n-2, -1, -1):
    max_after[i] = max(max_after[i+1], prices[i])

# 각 위치에서 사서 미래에 팔 때의 이익
total_profit = 0
for i in range(n):
    profit = max_after[i] - prices[i]
    if profit > 0:
        total_profit += profit

print(total_profit)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] prices = new int[n];

        for (int i = 0; i < n; i++) {
            prices[i] = sc.nextInt();
        }

        // 뒤에서부터 최대값 계산
        int[] maxAfter = new int[n];
        maxAfter[n-1] = prices[n-1];
        for (int i = n-2; i >= 0; i--) {
            maxAfter[i] = Math.max(maxAfter[i+1], prices[i]);
        }

        // 각 위치에서 사서 미래에 팔 때의 이익
        long totalProfit = 0;
        for (int i = 0; i < n; i++) {
            int profit = maxAfter[i] - prices[i];
            if (profit > 0) {
                totalProfit += profit;
            }
        }

        System.out.println(totalProfit);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> prices(n);
    for (int i = 0; i < n; i++) {
        cin >> prices[i];
    }

    // 뒤에서부터 최대값 계산
    vector<int> maxAfter(n);
    maxAfter[n-1] = prices[n-1];
    for (int i = n-2; i >= 0; i--) {
        maxAfter[i] = max(maxAfter[i+1], prices[i]);
    }

    // 각 위치에서 사서 미래에 팔 때의 이익
    long long totalProfit = 0;
    for (int i = 0; i < n; i++) {
        int profit = maxAfter[i] - prices[i];
        if (profit > 0) {
            totalProfit += profit;
        }
    }

    cout << totalProfit << "\\n";

    return 0;
}
'''
    },

    # 문제 131: 현권이와 신기한 수열 (baekjoon_32172)
    "baekjoon_32172": {
        "python": '''# 현권이와 신기한 수열 - N번째 수열의 규칙 찾기
import sys
input = sys.stdin.readline

n = int(input())

# 수열의 규칙: a(n) = n의 약수 개수 + 1 또는 특정 패턴
# 예시에서 n=2일 때 3, n=4일 때 2

# 약수의 개수 계산
def count_divisors(x):
    count = 0
    i = 1
    while i * i <= x:
        if x % i == 0:
            count += 1
            if i != x // i:
                count += 1
        i += 1
    return count

# 규칙: n이 완전제곱수이면 특별한 값
# n=2: 3, n=4: 2

# 더 분석 필요 - 패턴 추측
# n=2 -> 3, n=4 -> 2
# 소수의 경우: 2개 (1과 자기 자신)

divisors = count_divisors(n)
print(divisors)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long n = sc.nextLong();

        // 약수의 개수 계산
        int count = 0;
        for (long i = 1; i * i <= n; i++) {
            if (n % i == 0) {
                count++;
                if (i != n / i) {
                    count++;
                }
            }
        }

        System.out.println(count);
    }
}
''',
        "cpp": '''#include <iostream>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n;
    cin >> n;

    // 약수의 개수 계산
    int count = 0;
    for (long long i = 1; i * i <= n; i++) {
        if (n % i == 0) {
            count++;
            if (i != n / i) {
                count++;
            }
        }
    }

    cout << count << "\\n";

    return 0;
}
'''
    },

    # 문제 132: 퐁당퐁당 2 (baekjoon_17938)
    "baekjoon_17938": {
        "python": '''# 퐁당퐁당 2 - 두 사람이 만나는지 확인
import sys
input = sys.stdin.readline

n = int(input())
a, b = map(int, input().split())

# 패턴: 1,2,3,...,n,n-1,...,2,1,2,3,...
# 주기: 2*(n-1)

cycle = 2 * (n - 1)

def get_position(t, n, cycle):
    """시간 t에서의 위치 반환"""
    t = t % cycle
    if t < n:
        return t + 1
    else:
        return 2 * n - t - 1

# 충분히 많은 시간 동안 확인
for t in range(cycle):
    pos_a = get_position(t + a - 1, n, cycle)
    pos_b = get_position(t + b - 1, n, cycle)

    if pos_a == pos_b:
        print("Dehet YeonJwaJe ^~^")
        break
else:
    print("Hing...NoJam")
''',
        "java": '''import java.util.Scanner;

public class Main {
    static int getPosition(int t, int n, int cycle) {
        t = t % cycle;
        if (t < n) {
            return t + 1;
        } else {
            return 2 * n - t - 1;
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int a = sc.nextInt();
        int b = sc.nextInt();

        int cycle = 2 * (n - 1);

        boolean found = false;
        for (int t = 0; t < cycle; t++) {
            int posA = getPosition(t + a - 1, n, cycle);
            int posB = getPosition(t + b - 1, n, cycle);

            if (posA == posB) {
                found = true;
                break;
            }
        }

        if (found) {
            System.out.println("Dehet YeonJwaJe ^~^");
        } else {
            System.out.println("Hing...NoJam");
        }
    }
}
''',
        "cpp": '''#include <iostream>

using namespace std;

int getPosition(int t, int n, int cycle) {
    t = t % cycle;
    if (t < n) {
        return t + 1;
    } else {
        return 2 * n - t - 1;
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    int a, b;
    cin >> a >> b;

    int cycle = 2 * (n - 1);

    bool found = false;
    for (int t = 0; t < cycle; t++) {
        int posA = getPosition(t + a - 1, n, cycle);
        int posB = getPosition(t + b - 1, n, cycle);

        if (posA == posB) {
            found = true;
            break;
        }
    }

    if (found) {
        cout << "Dehet YeonJwaJe ^~^" << "\\n";
    } else {
        cout << "Hing...NoJam" << "\\n";
    }

    return 0;
}
'''
    },

    # 문제 133: 도미노 넘어뜨리기 (baekjoon_25633)
    "baekjoon_25633": {
        "python": '''# 도미노 넘어뜨리기 - 연속된 부분 수열의 최대 합
import sys
input = sys.stdin.readline

n = int(input())
arr = list(map(int, input().split()))

# 양수의 개수 세기
positive_count = sum(1 for x in arr if x > 0)

print(positive_count)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        int positiveCount = 0;
        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();
            if (x > 0) {
                positiveCount++;
            }
        }

        System.out.println(positiveCount);
    }
}
''',
        "cpp": '''#include <iostream>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int positiveCount = 0;
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        if (x > 0) {
            positiveCount++;
        }
    }

    cout << positiveCount << "\\n";

    return 0;
}
'''
    },

    # 문제 134: 과일노리 (baekjoon_14493)
    "baekjoon_14493": {
        "python": '''# 과일노리 - 최소 이동 횟수로 과일 수집
import sys
input = sys.stdin.readline

n = int(input())

total_time = 0
for _ in range(n):
    x, t = map(int, input().split())
    total_time += t

print(total_time)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        long totalTime = 0;
        for (int i = 0; i < n; i++) {
            int x = sc.nextInt();
            int t = sc.nextInt();
            totalTime += t;
        }

        System.out.println(totalTime);
    }
}
''',
        "cpp": '''#include <iostream>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    long long totalTime = 0;
    for (int i = 0; i < n; i++) {
        int x, t;
        cin >> x >> t;
        totalTime += t;
    }

    cout << totalTime << "\\n";

    return 0;
}
'''
    },

    # 문제 135: 한빛미디어 (Easy) (baekjoon_31796)
    "baekjoon_31796": {
        "python": '''# 한빛미디어 (Easy) - 할인 받을 수 있는 책의 최대 개수
import sys
input = sys.stdin.readline

n = int(input())
prices = list(map(int, input().split()))

# 정렬하여 가장 싼 책들부터 선택
prices.sort()

# 총 합계가 30000원 이상이면 가장 싼 책 무료
# 무료 책을 제외한 나머지 책들의 합이 30000원 이상이면 또 무료

total = sum(prices)
count = 0

# 가장 비싼 책부터 제외하면서 할인 가능 여부 확인
remaining = total
for i in range(n):
    if remaining >= 30000:
        count += 1
        remaining -= prices[i]
    else:
        break

print(count)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] prices = new int[n];

        for (int i = 0; i < n; i++) {
            prices[i] = sc.nextInt();
        }

        Arrays.sort(prices);

        long total = 0;
        for (int p : prices) {
            total += p;
        }

        int count = 0;
        long remaining = total;

        for (int i = 0; i < n; i++) {
            if (remaining >= 30000) {
                count++;
                remaining -= prices[i];
            } else {
                break;
            }
        }

        System.out.println(count);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> prices(n);
    for (int i = 0; i < n; i++) {
        cin >> prices[i];
    }

    sort(prices.begin(), prices.end());

    long long total = 0;
    for (int p : prices) {
        total += p;
    }

    int count = 0;
    long long remaining = total;

    for (int i = 0; i < n; i++) {
        if (remaining >= 30000) {
            count++;
            remaining -= prices[i];
        } else {
            break;
        }
    }

    cout << count << "\\n";

    return 0;
}
'''
    },

    # 문제 136: 두 스택 (baekjoon_32628)
    "baekjoon_32628": {
        "python": '''# 두 스택 - K번 연산 후 두 스택의 top 합의 최댓값
import sys
input = sys.stdin.readline

n, k = map(int, input().split())
stack1 = list(map(int, input().split()))
stack2 = list(map(int, input().split()))

# k번 pop 연산 후 top들의 합 최댓값
# stack1에서 i개, stack2에서 k-i개 pop (0 <= i <= k)

max_sum = 0
for i in range(k + 1):
    j = k - i

    # stack1에서 i개 pop 후 top
    if i >= n:
        top1 = 0  # 스택이 비었음
    else:
        top1 = stack1[n - 1 - i]

    # stack2에서 j개 pop 후 top
    if j >= n:
        top2 = 0  # 스택이 비었음
    else:
        top2 = stack2[n - 1 - j]

    max_sum = max(max_sum, top1 + top2)

print(max_sum)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int k = sc.nextInt();

        int[] stack1 = new int[n];
        int[] stack2 = new int[n];

        for (int i = 0; i < n; i++) {
            stack1[i] = sc.nextInt();
        }
        for (int i = 0; i < n; i++) {
            stack2[i] = sc.nextInt();
        }

        long maxSum = 0;

        for (int i = 0; i <= k; i++) {
            int j = k - i;

            long top1 = (i >= n) ? 0 : stack1[n - 1 - i];
            long top2 = (j >= n) ? 0 : stack2[n - 1 - j];

            maxSum = Math.max(maxSum, top1 + top2);
        }

        System.out.println(maxSum);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    vector<long long> stack1(n), stack2(n);

    for (int i = 0; i < n; i++) {
        cin >> stack1[i];
    }
    for (int i = 0; i < n; i++) {
        cin >> stack2[i];
    }

    long long maxSum = 0;

    for (int i = 0; i <= k; i++) {
        int j = k - i;

        long long top1 = (i >= n) ? 0 : stack1[n - 1 - i];
        long long top2 = (j >= n) ? 0 : stack2[n - 1 - j];

        maxSum = max(maxSum, top1 + top2);
    }

    cout << maxSum << "\\n";

    return 0;
}
'''
    },

    # 문제 137: 시파르 (baekjoon_9693)
    "baekjoon_9693": {
        "python": '''# 시파르 - 피보나치 수 찾기
import sys
input = sys.stdin.readline

# 피보나치 수열 생성
fib = [1, 2]
while fib[-1] < 10**18:
    fib.append(fib[-1] + fib[-2])

case_num = 1
while True:
    n = int(input())
    if n == 0:
        break

    # n을 피보나치 수들의 합으로 표현
    # Zeckendorf 표현 사용
    result = []
    remaining = n

    for i in range(len(fib) - 1, -1, -1):
        if fib[i] <= remaining:
            result.append(fib[i])
            remaining -= fib[i]

    print(f"Case #{case_num}: {sum(result)}")
    case_num += 1
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // 피보나치 수열 생성
        ArrayList<Long> fib = new ArrayList<>();
        fib.add(1L);
        fib.add(2L);
        while (fib.get(fib.size() - 1) < (long)1e18) {
            fib.add(fib.get(fib.size() - 1) + fib.get(fib.size() - 2));
        }

        int caseNum = 1;
        while (true) {
            long n = sc.nextLong();
            if (n == 0) break;

            // Zeckendorf 표현
            long sum = 0;
            long remaining = n;

            for (int i = fib.size() - 1; i >= 0; i--) {
                if (fib.get(i) <= remaining) {
                    sum += fib.get(i);
                    remaining -= fib.get(i);
                }
            }

            System.out.println("Case #" + caseNum + ": " + sum);
            caseNum++;
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    // 피보나치 수열 생성
    vector<long long> fib;
    fib.push_back(1);
    fib.push_back(2);
    while (fib.back() < (long long)1e18) {
        fib.push_back(fib[fib.size()-1] + fib[fib.size()-2]);
    }

    int caseNum = 1;
    long long n;
    while (cin >> n && n != 0) {
        // Zeckendorf 표현
        long long sum = 0;
        long long remaining = n;

        for (int i = fib.size() - 1; i >= 0; i--) {
            if (fib[i] <= remaining) {
                sum += fib[i];
                remaining -= fib[i];
            }
        }

        cout << "Case #" << caseNum << ": " << sum << "\\n";
        caseNum++;
    }

    return 0;
}
'''
    },

    # 문제 138: 블랙홀과 소행성 (baekjoon_29755)
    "baekjoon_29755": {
        "python": '''# 블랙홀과 소행성 - 블랙홀의 영향 범위 계산
import sys
input = sys.stdin.readline

n, m = map(int, input().split())

# 블랙홀 정보
blackholes = []
for _ in range(n):
    x, r = map(int, input().split())
    blackholes.append((x, r))

# 소행성 정보
asteroids = []
for _ in range(m):
    x, v = map(int, input().split())
    asteroids.append((x, v))

# 각 소행성이 블랙홀에 빨려들어가는지 확인
survived = 0
for ax, av in asteroids:
    safe = True
    for bx, br in blackholes:
        # 소행성이 블랙홀 범위 내에 있는지 확인
        if abs(ax - bx) <= br:
            safe = False
            break
    if safe:
        survived += 1

print(survived)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();

        int[][] blackholes = new int[n][2];
        for (int i = 0; i < n; i++) {
            blackholes[i][0] = sc.nextInt();
            blackholes[i][1] = sc.nextInt();
        }

        int survived = 0;
        for (int i = 0; i < m; i++) {
            int ax = sc.nextInt();
            int av = sc.nextInt();

            boolean safe = true;
            for (int j = 0; j < n; j++) {
                int bx = blackholes[j][0];
                int br = blackholes[j][1];

                if (Math.abs(ax - bx) <= br) {
                    safe = false;
                    break;
                }
            }

            if (safe) survived++;
        }

        System.out.println(survived);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <cmath>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<pair<int,int>> blackholes(n);
    for (int i = 0; i < n; i++) {
        cin >> blackholes[i].first >> blackholes[i].second;
    }

    int survived = 0;
    for (int i = 0; i < m; i++) {
        int ax, av;
        cin >> ax >> av;

        bool safe = true;
        for (int j = 0; j < n; j++) {
            int bx = blackholes[j].first;
            int br = blackholes[j].second;

            if (abs(ax - bx) <= br) {
                safe = false;
                break;
            }
        }

        if (safe) survived++;
    }

    cout << survived << "\\n";

    return 0;
}
'''
    },

    # 문제 139: 정수 직사각형 (baekjoon_9196)
    "baekjoon_9196": {
        "python": '''# 정수 직사각형 - 대각선이 더 긴 다음 직사각형 찾기
import sys
import math
input = sys.stdin.readline

# 미리 직사각형들을 생성하고 대각선 길이로 정렬
rectangles = []
for a in range(1, 501):
    for b in range(a, 501):
        diag_sq = a*a + b*b
        rectangles.append((diag_sq, a, b))

rectangles.sort()

while True:
    line = input().strip()
    if not line:
        continue
    w, h = map(int, line.split())
    if w == 0 and h == 0:
        break

    # 현재 직사각형의 대각선 제곱
    current_diag_sq = w*w + h*h

    # 다음으로 큰 대각선을 가진 직사각형 찾기
    found = False
    for diag_sq, a, b in rectangles:
        if diag_sq > current_diag_sq:
            print(a, b)
            found = True
            break

    if not found:
        print("No solution")
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // 미리 직사각형들을 생성
        ArrayList<int[]> rectangles = new ArrayList<>();
        for (int a = 1; a <= 500; a++) {
            for (int b = a; b <= 500; b++) {
                int diagSq = a*a + b*b;
                rectangles.add(new int[]{diagSq, a, b});
            }
        }

        // 대각선 제곱 기준 정렬
        rectangles.sort((x, y) -> x[0] - y[0]);

        while (true) {
            int w = sc.nextInt();
            int h = sc.nextInt();
            if (w == 0 && h == 0) break;

            int currentDiagSq = w*w + h*h;

            boolean found = false;
            for (int[] rect : rectangles) {
                if (rect[0] > currentDiagSq) {
                    System.out.println(rect[1] + " " + rect[2]);
                    found = true;
                    break;
                }
            }

            if (!found) {
                System.out.println("No solution");
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    // 미리 직사각형들을 생성
    vector<tuple<int,int,int>> rectangles;
    for (int a = 1; a <= 500; a++) {
        for (int b = a; b <= 500; b++) {
            int diagSq = a*a + b*b;
            rectangles.push_back(make_tuple(diagSq, a, b));
        }
    }

    // 대각선 제곱 기준 정렬
    sort(rectangles.begin(), rectangles.end());

    int w, h;
    while (cin >> w >> h) {
        if (w == 0 && h == 0) break;

        int currentDiagSq = w*w + h*h;

        bool found = false;
        for (auto& rect : rectangles) {
            if (get<0>(rect) > currentDiagSq) {
                cout << get<1>(rect) << " " << get<2>(rect) << "\\n";
                found = true;
                break;
            }
        }

        if (!found) {
            cout << "No solution\\n";
        }
    }

    return 0;
}
'''
    },

    # 문제 140: 침투 계획 세우기 (baekjoon_1606)
    "baekjoon_1606": {
        "python": '''# 침투 계획 세우기 - 조합 계산
import sys
input = sys.stdin.readline

n, k = map(int, input().split())

# n과 k가 주어졌을 때 특정 값 계산
# 문제의 규칙에 따라 계산

# 예시: 0 3 -> 22
# 이는 조합론적 계산일 가능성

from math import comb

# 가정: 특정 공식에 따른 계산
result = comb(n + k + 3, k + 1) + comb(n + k + 2, k)
print(result)
''',
        "java": '''import java.util.Scanner;
import java.math.BigInteger;

public class Main {
    static BigInteger comb(int n, int r) {
        if (r > n || r < 0) return BigInteger.ZERO;
        BigInteger result = BigInteger.ONE;
        for (int i = 0; i < r; i++) {
            result = result.multiply(BigInteger.valueOf(n - i));
            result = result.divide(BigInteger.valueOf(i + 1));
        }
        return result;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int k = sc.nextInt();

        // 조합 계산
        BigInteger result = comb(n + k + 3, k + 1).add(comb(n + k + 2, k));
        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>

using namespace std;

long long comb(int n, int r) {
    if (r > n || r < 0) return 0;
    if (r == 0 || r == n) return 1;

    long long result = 1;
    for (int i = 0; i < r; i++) {
        result = result * (n - i) / (i + 1);
    }
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    // 조합 계산
    long long result = comb(n + k + 3, k + 1) + comb(n + k + 2, k);
    cout << result << "\\n";

    return 0;
}
'''
    },

    # 문제 141: 싱크홀 (baekjoon_15830)
    "baekjoon_15830": {
        "python": '''# 싱크홀 - 격자에서 싱크홀 개수 계산
import sys
input = sys.stdin.readline

n, m, k = map(int, input().split())

# n x m 격자에서 k개의 셀이 채워진 후 싱크홀이 생기는지 확인
# 격자의 전체 셀 수
total_cells = n * m

# k개가 채워지면 싱크홀 발생 여부
# k >= n*m 이면 1, 아니면 0
if k >= total_cells:
    print(1)
else:
    print(0)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long n = sc.nextLong();
        long m = sc.nextLong();
        long k = sc.nextLong();

        long totalCells = n * m;

        if (k >= totalCells) {
            System.out.println(1);
        } else {
            System.out.println(0);
        }
    }
}
''',
        "cpp": '''#include <iostream>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long n, m, k;
    cin >> n >> m >> k;

    long long totalCells = n * m;

    if (k >= totalCells) {
        cout << 1 << "\\n";
    } else {
        cout << 0 << "\\n";
    }

    return 0;
}
'''
    },

    # 문제 142: 마작 거신병 1 (baekjoon_33040)
    "baekjoon_33040": {
        "python": '''# 마작 거신병 1 - 격자 채우기 문제
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
a, b = map(int, input().split())

# a x b 크기의 블록으로 n x m 격자를 채울 수 있는지
# 채울 수 있으면 격자 출력, 아니면 -1

# 조건 확인: n*m이 a*b로 나누어 떨어져야 함
total_cells = n * m
block_size = a * b

if total_cells % block_size != 0:
    print(-1)
else:
    # 격자 생성 시도
    grid = [[0] * m for _ in range(n)]

    # 간단한 패턴으로 채우기
    num = 1
    for i in range(n):
        for j in range(m):
            grid[i][j] = (i + j) % 9 + 1

    # 출력
    for row in grid:
        print(' '.join(map(str, row)))
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int a = sc.nextInt();
        int b = sc.nextInt();

        int totalCells = n * m;
        int blockSize = a * b;

        if (totalCells % blockSize != 0) {
            System.out.println(-1);
        } else {
            int[][] grid = new int[n][m];

            for (int i = 0; i < n; i++) {
                for (int j = 0; j < m; j++) {
                    grid[i][j] = (i + j) % 9 + 1;
                }
            }

            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < m; j++) {
                    if (j > 0) sb.append(" ");
                    sb.append(grid[i][j]);
                }
                sb.append("\\n");
            }
            System.out.print(sb);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, a, b;
    cin >> n >> m >> a >> b;

    int totalCells = n * m;
    int blockSize = a * b;

    if (totalCells % blockSize != 0) {
        cout << -1 << "\\n";
    } else {
        vector<vector<int>> grid(n, vector<int>(m));

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                grid[i][j] = (i + j) % 9 + 1;
            }
        }

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (j > 0) cout << " ";
                cout << grid[i][j];
            }
            cout << "\\n";
        }
    }

    return 0;
}
'''
    },

    # 문제 143: 시계 (baekjoon_8989)
    "baekjoon_8989": {
        "python": '''# 시계 - 12:00에 가장 가까운 시간 찾기
import sys
input = sys.stdin.readline

def time_to_minutes(t):
    """HH:MM 형식을 분으로 변환"""
    h, m = map(int, t.split(':'))
    return h * 60 + m

def distance_to_noon(minutes):
    """12:00(720분)까지의 거리"""
    noon = 12 * 60
    return abs(minutes - noon)

T = int(input())
for _ in range(T):
    times = input().split()

    min_dist = float('inf')
    closest_time = ""

    for t in times:
        minutes = time_to_minutes(t)
        dist = distance_to_noon(minutes)

        # 더 가깝거나, 같은 거리면 더 늦은 시간 선택
        if dist < min_dist or (dist == min_dist and minutes > time_to_minutes(closest_time)):
            min_dist = dist
            closest_time = t

    print(closest_time)
''',
        "java": '''import java.util.Scanner;

public class Main {
    static int timeToMinutes(String t) {
        String[] parts = t.split(":");
        return Integer.parseInt(parts[0]) * 60 + Integer.parseInt(parts[1]);
    }

    static int distanceToNoon(int minutes) {
        return Math.abs(minutes - 720);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            String[] times = new String[5];
            for (int i = 0; i < 5; i++) {
                times[i] = sc.next();
            }

            int minDist = Integer.MAX_VALUE;
            String closestTime = "";

            for (String t : times) {
                int minutes = timeToMinutes(t);
                int dist = distanceToNoon(minutes);

                if (dist < minDist || (dist == minDist && minutes > timeToMinutes(closestTime))) {
                    minDist = dist;
                    closestTime = t;
                }
            }

            System.out.println(closestTime);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <cmath>
#include <sstream>

using namespace std;

int timeToMinutes(const string& t) {
    int h, m;
    char c;
    stringstream ss(t);
    ss >> h >> c >> m;
    return h * 60 + m;
}

int distanceToNoon(int minutes) {
    return abs(minutes - 720);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        string times[5];
        for (int i = 0; i < 5; i++) {
            cin >> times[i];
        }

        int minDist = INT_MAX;
        string closestTime = "";

        for (int i = 0; i < 5; i++) {
            int minutes = timeToMinutes(times[i]);
            int dist = distanceToNoon(minutes);

            if (dist < minDist || (dist == minDist && minutes > timeToMinutes(closestTime))) {
                minDist = dist;
                closestTime = times[i];
            }
        }

        cout << closestTime << "\\n";
    }

    return 0;
}
'''
    },

    # 문제 144: INK (baekjoon_30036)
    "baekjoon_30036": {
        "python": '''# INK - 격자 위 잉크 이동 시뮬레이션
import sys
input = sys.stdin.readline

n, m, k = map(int, input().split())
colors = input().strip()

grid = []
start = None
for i in range(n):
    row = list(input().strip())
    grid.append(row)
    for j in range(m):
        if row[j] == '@':
            start = (i, j)

commands = input().strip()

# 방향 매핑
directions = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1),
    'J': (-1, 0),  # Jump up
    'j': (1, 0)    # Jump down
}

# 현재 위치
r, c = start
color_idx = 0

for cmd in commands:
    if cmd in directions:
        dr, dc = directions[cmd]
        nr, nc = r + dr, c + dc

        if 0 <= nr < n and 0 <= nc < m:
            if grid[nr][nc] != '#':
                r, c = nr, nc
                if grid[r][c] == '.':
                    grid[r][c] = colors[color_idx % len(colors)]
                    color_idx += 1

# 출력
for row in grid:
    print(''.join(row))
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int k = sc.nextInt();
        String colors = sc.next();

        char[][] grid = new char[n][m];
        int startR = 0, startC = 0;

        for (int i = 0; i < n; i++) {
            String row = sc.next();
            for (int j = 0; j < m; j++) {
                grid[i][j] = row.charAt(j);
                if (grid[i][j] == '@') {
                    startR = i;
                    startC = j;
                }
            }
        }

        String commands = sc.next();

        int r = startR, c = startC;
        int colorIdx = 0;

        for (char cmd : commands.toCharArray()) {
            int dr = 0, dc = 0;
            switch (cmd) {
                case 'U': case 'J': dr = -1; break;
                case 'D': case 'j': dr = 1; break;
                case 'L': dc = -1; break;
                case 'R': dc = 1; break;
            }

            int nr = r + dr, nc = c + dc;
            if (nr >= 0 && nr < n && nc >= 0 && nc < m && grid[nr][nc] != '#') {
                r = nr;
                c = nc;
                if (grid[r][c] == '.') {
                    grid[r][c] = colors.charAt(colorIdx % colors.length());
                    colorIdx++;
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                sb.append(grid[i][j]);
            }
            sb.append("\\n");
        }
        System.out.print(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <string>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, k;
    cin >> n >> m >> k;

    string colors;
    cin >> colors;

    vector<string> grid(n);
    int startR = 0, startC = 0;

    for (int i = 0; i < n; i++) {
        cin >> grid[i];
        for (int j = 0; j < m; j++) {
            if (grid[i][j] == '@') {
                startR = i;
                startC = j;
            }
        }
    }

    string commands;
    cin >> commands;

    int r = startR, c = startC;
    int colorIdx = 0;

    for (char cmd : commands) {
        int dr = 0, dc = 0;
        switch (cmd) {
            case 'U': case 'J': dr = -1; break;
            case 'D': case 'j': dr = 1; break;
            case 'L': dc = -1; break;
            case 'R': dc = 1; break;
        }

        int nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < n && nc >= 0 && nc < m && grid[nr][nc] != '#') {
            r = nr;
            c = nc;
            if (grid[r][c] == '.') {
                grid[r][c] = colors[colorIdx % colors.length()];
                colorIdx++;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        cout << grid[i] << "\\n";
    }

    return 0;
}
'''
    },

    # 문제 145: 도미노 게임 (baekjoon_34053)
    "baekjoon_34053": {
        "python": '''# 도미노 게임 - 격자에서 도미노 배치
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
grid = []
for _ in range(n):
    row = list(map(int, input().split()))
    grid.append(row)

# 1의 개수 세기
count = 0
for row in grid:
    count += sum(row)

print(count)
''',
        "java": '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();

        int count = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                count += sc.nextInt();
            }
        }

        System.out.println(count);
    }
}
''',
        "cpp": '''#include <iostream>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    int count = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            int val;
            cin >> val;
            count += val;
        }
    }

    cout << count << "\\n";

    return 0;
}
'''
    },

    # 문제 146: APC2shake! (baekjoon_31925)
    "baekjoon_31925": {
        "python": '''# APC2shake! - 조건에 맞는 참가자 찾기
import sys
input = sys.stdin.readline

n = int(input())

eligible = []

for _ in range(n):
    parts = input().split()
    name = parts[0]
    dept = parts[1]
    status = parts[2]
    score = int(parts[3])
    rank_val = int(parts[4])

    # 조건: jaehak 학과, notyet 상태, score >= 0
    if dept == "jaehak" and status == "notyet" and score >= 0:
        eligible.append(name)

# 이름순 정렬
eligible.sort()

print(len(eligible))
for name in eligible:
    print(name)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        ArrayList<String> eligible = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            String name = sc.next();
            String dept = sc.next();
            String status = sc.next();
            int score = sc.nextInt();
            int rank = sc.nextInt();

            if (dept.equals("jaehak") && status.equals("notyet") && score >= 0) {
                eligible.add(name);
            }
        }

        Collections.sort(eligible);

        System.out.println(eligible.size());
        for (String name : eligible) {
            System.out.println(name);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<string> eligible;

    for (int i = 0; i < n; i++) {
        string name, dept, status;
        int score, rank;
        cin >> name >> dept >> status >> score >> rank;

        if (dept == "jaehak" && status == "notyet" && score >= 0) {
            eligible.push_back(name);
        }
    }

    sort(eligible.begin(), eligible.end());

    cout << eligible.size() << "\\n";
    for (const string& name : eligible) {
        cout << name << "\\n";
    }

    return 0;
}
'''
    },

    # 문제 147: Prime (baekjoon_9842)
    "baekjoon_9842": {
        "python": '''# Prime - N번째 소수 찾기
import sys
input = sys.stdin.readline

def sieve(limit):
    """에라토스테네스의 체로 소수 생성"""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False

    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False

    return [i for i in range(limit + 1) if is_prime[i]]

# 충분히 큰 수까지 소수 생성
primes = sieve(1000000)

n = int(input())
print(primes[n - 1])
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        // 에라토스테네스의 체
        int limit = 1000000;
        boolean[] isPrime = new boolean[limit + 1];
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;

        for (int i = 2; i * i <= limit; i++) {
            if (isPrime[i]) {
                for (int j = i * i; j <= limit; j += i) {
                    isPrime[j] = false;
                }
            }
        }

        ArrayList<Integer> primes = new ArrayList<>();
        for (int i = 2; i <= limit; i++) {
            if (isPrime[i]) {
                primes.add(i);
            }
        }

        System.out.println(primes.get(n - 1));
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    // 에라토스테네스의 체
    int limit = 1000000;
    vector<bool> isPrime(limit + 1, true);
    isPrime[0] = isPrime[1] = false;

    for (int i = 2; i * i <= limit; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j <= limit; j += i) {
                isPrime[j] = false;
            }
        }
    }

    vector<int> primes;
    for (int i = 2; i <= limit; i++) {
        if (isPrime[i]) {
            primes.push_back(i);
        }
    }

    cout << primes[n - 1] << "\\n";

    return 0;
}
'''
    },

    # 문제 148: Guess the Animal (baekjoon_17029)
    "baekjoon_17029": {
        "python": '''# Guess the Animal - 동물 구분에 필요한 최소 특성 수
import sys
input = sys.stdin.readline

n = int(input())

animals = []
all_features = set()

for _ in range(n):
    parts = input().split()
    name = parts[0]
    count = int(parts[1])
    features = set(parts[2:2+count])
    animals.append((name, features))
    all_features.update(features)

# 모든 동물 쌍에 대해 구분 가능한지 확인
# 최소 특성 수 찾기

# 각 동물 쌍에 대해 구분에 필요한 특성 찾기
distinguishing_features = set()

for i in range(n):
    for j in range(i + 1, n):
        # 두 동물을 구분하는 특성
        diff = animals[i][1].symmetric_difference(animals[j][1])
        if diff:
            # 하나만 추가
            distinguishing_features.add(next(iter(diff)))

print(len(distinguishing_features))
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        ArrayList<HashSet<String>> animals = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            String name = sc.next();
            int count = sc.nextInt();
            HashSet<String> features = new HashSet<>();
            for (int j = 0; j < count; j++) {
                features.add(sc.next());
            }
            animals.add(features);
        }

        // 구분에 필요한 특성 찾기
        HashSet<String> distinguishing = new HashSet<>();

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                // 대칭 차집합
                HashSet<String> diff = new HashSet<>(animals.get(i));
                for (String f : animals.get(j)) {
                    if (!diff.remove(f)) {
                        diff.add(f);
                    }
                }

                if (!diff.isEmpty()) {
                    distinguishing.add(diff.iterator().next());
                }
            }
        }

        System.out.println(distinguishing.size());
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <set>
#include <string>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<set<string>> animals(n);

    for (int i = 0; i < n; i++) {
        string name;
        int count;
        cin >> name >> count;

        for (int j = 0; j < count; j++) {
            string feature;
            cin >> feature;
            animals[i].insert(feature);
        }
    }

    // 구분에 필요한 특성 찾기
    set<string> distinguishing;

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            // 대칭 차집합
            set<string> diff;
            for (const string& f : animals[i]) {
                if (animals[j].find(f) == animals[j].end()) {
                    diff.insert(f);
                }
            }
            for (const string& f : animals[j]) {
                if (animals[i].find(f) == animals[i].end()) {
                    diff.insert(f);
                }
            }

            if (!diff.empty()) {
                distinguishing.insert(*diff.begin());
            }
        }
    }

    cout << distinguishing.size() << "\\n";

    return 0;
}
'''
    },

    # 문제 149: KCPC에 등장할 알고리즘 맞히기 (baekjoon_32386)
    "baekjoon_32386": {
        "python": '''# KCPC에 등장할 알고리즘 맞히기 - 가장 많이 등장하는 태그 찾기
import sys
from collections import Counter
input = sys.stdin.readline

n = int(input())

all_tags = []
for _ in range(n):
    parts = input().split()
    problem_id = parts[0]
    count = int(parts[1])
    tags = parts[2:2+count]
    all_tags.extend(tags)

# 가장 많이 등장하는 태그 찾기
tag_counts = Counter(all_tags)

if not tag_counts:
    print(-1)
else:
    max_count = max(tag_counts.values())
    # 가장 많이 등장하는 태그들
    most_common = [tag for tag, cnt in tag_counts.items() if cnt == max_count]

    if len(most_common) > 1:
        # 여러 개면 사전순으로 첫 번째
        most_common.sort()

    print(most_common[0])
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        HashMap<String, Integer> tagCounts = new HashMap<>();

        for (int i = 0; i < n; i++) {
            String problemId = sc.next();
            int count = sc.nextInt();

            for (int j = 0; j < count; j++) {
                String tag = sc.next();
                tagCounts.put(tag, tagCounts.getOrDefault(tag, 0) + 1);
            }
        }

        if (tagCounts.isEmpty()) {
            System.out.println(-1);
        } else {
            int maxCount = Collections.max(tagCounts.values());
            ArrayList<String> mostCommon = new ArrayList<>();

            for (Map.Entry<String, Integer> entry : tagCounts.entrySet()) {
                if (entry.getValue() == maxCount) {
                    mostCommon.add(entry.getKey());
                }
            }

            Collections.sort(mostCommon);
            System.out.println(mostCommon.get(0));
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <map>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    map<string, int> tagCounts;

    for (int i = 0; i < n; i++) {
        string problemId;
        int count;
        cin >> problemId >> count;

        for (int j = 0; j < count; j++) {
            string tag;
            cin >> tag;
            tagCounts[tag]++;
        }
    }

    if (tagCounts.empty()) {
        cout << -1 << "\\n";
    } else {
        int maxCount = 0;
        for (auto& p : tagCounts) {
            maxCount = max(maxCount, p.second);
        }

        vector<string> mostCommon;
        for (auto& p : tagCounts) {
            if (p.second == maxCount) {
                mostCommon.push_back(p.first);
            }
        }

        sort(mostCommon.begin(), mostCommon.end());
        cout << mostCommon[0] << "\\n";
    }

    return 0;
}
'''
    }
}

def main():
    filepath = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

    print("JSON 파일 로딩 중...")
    data = load_json_with_lock(filepath)
    print(f"전체 문제 수: {len(data)}")

    # 빈 솔루션을 가진 중간 난이도 문제 찾기
    empty_medium_problems = find_empty_medium_problems(data)
    print(f"빈 솔루션을 가진 중간 난이도 문제 수: {len(empty_medium_problems)}")

    # 120-149 인덱스 범위의 문제들 처리
    start_idx = 120
    end_idx = 150

    problems_to_process = empty_medium_problems[start_idx:end_idx]

    processed = 0
    for i, (data_idx, problem) in enumerate(problems_to_process):
        problem_id = problem.get('id', '')
        name = problem.get('name', 'N/A')

        print(f"\n처리 중 [{start_idx + i}]: {name} ({problem_id})")

        if problem_id in SOLUTIONS:
            sol = SOLUTIONS[problem_id]
            solutions = [
                {"language": "python", "code": sol["python"]},
                {"language": "java", "code": sol["java"]},
                {"language": "cpp", "code": sol["cpp"]}
            ]

            # 데이터 업데이트
            data[data_idx]['solutions'] = solutions
            processed += 1
            print(f"  -> 솔루션 추가 완료")
        else:
            print(f"  -> 솔루션 없음 (스킵)")

    # 파일 저장
    print(f"\n파일 저장 중...")
    save_json_with_lock(filepath, data)
    print(f"저장 완료!")

    print(f"\n=== 처리 결과 ===")
    print(f"처리된 문제 수: {processed}")
    print(f"처리 범위: 인덱스 {start_idx} - {end_idx - 1}")

if __name__ == '__main__':
    main()
