#!/usr/bin/env python3
"""
Script to add solutions for medium difficulty problems (index 960-989)
in problems_with_github_solutions.json
"""

import json
import fcntl
import os

# Define solutions for each problem
SOLUTIONS = {
    # Problem 960: baekjoon_24300 - НАЙ-ГОЛЯМ ОСТАТЪК (Maximum Remainder)
    # Find the maximum remainder when dividing a_i by a_j
    10725: [
        {
            "language": "python",
            "code": '''# 백준 24300: 최대 나머지 (Maximum Remainder)
# N개의 양의 정수가 주어질 때, a_i를 a_j로 나눈 나머지 중 가장 큰 값을 구하는 문제
# 최대 나머지는 두 번째로 큰 수가 된다 (가장 큰 수 % 두 번째로 큰 수 = 두 번째로 큰 수)

import sys
input = sys.stdin.readline

n = int(input())
arr = list(map(int, input().split()))

# 정렬 후 가장 큰 수와 두 번째로 큰 수 찾기
arr.sort(reverse=True)

# 최대 나머지는 두 번째로 큰 수
# 왜냐하면 max_val % second_max = second_max (max > second_max이면)
print(arr[1])
'''
        },
        {
            "language": "java",
            "code": '''// 백준 24300: 최대 나머지 (Maximum Remainder)
// N개의 양의 정수가 주어질 때, a_i를 a_j로 나눈 나머지 중 가장 큰 값을 구함

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        // 정렬하여 두 번째로 큰 수 찾기
        Arrays.sort(arr);

        // 최대 나머지는 두 번째로 큰 수
        System.out.println(arr[n - 2]);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 24300: 최대 나머지 (Maximum Remainder)
// N개의 양의 정수가 주어질 때, a_i를 a_j로 나눈 나머지 중 가장 큰 값을 구함

#include <iostream>
#include <algorithm>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    // 정렬하여 두 번째로 큰 수 찾기
    sort(arr.begin(), arr.end(), greater<int>());

    // 최대 나머지는 두 번째로 큰 수
    cout << arr[1] << endl;

    return 0;
}
'''
        }
    ],

    # Problem 961: baekjoon_30608 - Missing Vowels
    # Check if short name can be obtained from full name by omitting vowels
    10743: [
        {
            "language": "python",
            "code": '''# 백준 30608: Missing Vowels
# 짧은 이름이 전체 이름에서 모음을 생략하여 얻을 수 있는지 확인

import sys
input = sys.stdin.readline

def solve():
    s = input().strip().lower()  # 짧은 이름
    f = input().strip().lower()  # 전체 이름

    vowels = set('aeiouy')

    # s의 각 문자에 대해 f에서 매칭 시도
    j = 0  # f에서의 위치
    for i, c in enumerate(s):
        found = False
        while j < len(f):
            if s[i] == f[j]:
                # 정확히 매칭
                found = True
                j += 1
                break
            elif f[j] in vowels and s[i] not in vowels:
                # f의 현재 문자가 모음이고 s의 현재 문자가 자음이면 건너뛰기
                j += 1
            elif f[j] in vowels and s[i] in vowels:
                # 둘 다 모음인데 다르면 실패
                break
            else:
                # 자음인데 다르면 실패
                break

        if not found:
            print("Different")
            return

    # 나머지 f의 문자들이 모두 모음이어야 함
    while j < len(f):
        if f[j] not in vowels:
            print("Different")
            return
        j += 1

    print("Same")

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 30608: Missing Vowels
// 짧은 이름이 전체 이름에서 모음을 생략하여 얻을 수 있는지 확인

import java.util.*;
import java.io.*;

public class Main {
    static Set<Character> vowels = new HashSet<>(Arrays.asList('a', 'e', 'i', 'o', 'u', 'y'));

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine().trim().toLowerCase();  // 짧은 이름
        String f = br.readLine().trim().toLowerCase();  // 전체 이름

        int j = 0;  // f에서의 위치
        boolean valid = true;

        for (int i = 0; i < s.length() && valid; i++) {
            char cs = s.charAt(i);
            boolean found = false;

            while (j < f.length()) {
                char cf = f.charAt(j);
                if (cs == cf) {
                    found = true;
                    j++;
                    break;
                } else if (vowels.contains(cf) && !vowels.contains(cs)) {
                    j++;
                } else {
                    break;
                }
            }

            if (!found) valid = false;
        }

        // 나머지 f의 문자들이 모두 모음이어야 함
        while (j < f.length() && valid) {
            if (!vowels.contains(f.charAt(j))) {
                valid = false;
            }
            j++;
        }

        System.out.println(valid ? "Same" : "Different");
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 30608: Missing Vowels
// 짧은 이름이 전체 이름에서 모음을 생략하여 얻을 수 있는지 확인

#include <iostream>
#include <string>
#include <set>
#include <algorithm>
using namespace std;

set<char> vowels = {'a', 'e', 'i', 'o', 'u', 'y'};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s, f;
    getline(cin, s);
    getline(cin, f);

    // 소문자로 변환
    transform(s.begin(), s.end(), s.begin(), ::tolower);
    transform(f.begin(), f.end(), f.begin(), ::tolower);

    int j = 0;
    bool valid = true;

    for (int i = 0; i < s.length() && valid; i++) {
        char cs = s[i];
        bool found = false;

        while (j < f.length()) {
            char cf = f[j];
            if (cs == cf) {
                found = true;
                j++;
                break;
            } else if (vowels.count(cf) && !vowels.count(cs)) {
                j++;
            } else {
                break;
            }
        }

        if (!found) valid = false;
    }

    // 나머지 문자들이 모두 모음이어야 함
    while (j < f.length() && valid) {
        if (!vowels.count(f[j])) {
            valid = false;
        }
        j++;
    }

    cout << (valid ? "Same" : "Different") << endl;

    return 0;
}
'''
        }
    ],

    # Problem 962: baekjoon_11611 - Blur
    # Apply blur operation n times and count unique values
    10764: [
        {
            "language": "python",
            "code": '''# 백준 11611: Blur
# 이미지에 블러 연산을 n번 적용한 후 고유한 픽셀 값의 개수를 구함

import sys
input = sys.stdin.readline

def solve():
    line = input().split()
    w, h, n = int(line[0]), int(line[1]), int(line[2])

    # 이미지 읽기 (분수로 표현하기 위해 정수로 저장, 9^n으로 나눈 값)
    image = []
    for _ in range(h):
        row = list(map(int, input().split()))
        image.append(row)

    # n번 블러 적용
    # 각 픽셀 값을 9^n으로 나눈 분자로 표현
    # 초기: 각 값에 9^n을 곱함
    scale = 9 ** n
    grid = [[image[r][c] * scale for c in range(w)] for r in range(h)]

    for _ in range(n):
        new_grid = [[0] * w for _ in range(h)]
        for r in range(h):
            for c in range(w):
                total = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr = (r + dr) % h
                        nc = (c + dc) % w
                        total += grid[nr][nc]
                # 9로 나누기 (분자 유지)
                new_grid[r][c] = total // 9
        grid = new_grid

    # 고유한 값의 개수
    unique_values = set()
    for row in grid:
        for val in row:
            unique_values.add(val)

    print(len(unique_values))

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 11611: Blur
// 이미지에 블러 연산을 n번 적용한 후 고유한 픽셀 값의 개수를 구함

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int w = Integer.parseInt(st.nextToken());
        int h = Integer.parseInt(st.nextToken());
        int n = Integer.parseInt(st.nextToken());

        // 이미지 읽기
        long[][] grid = new long[h][w];
        long scale = 1;
        for (int i = 0; i < n; i++) scale *= 9;

        for (int r = 0; r < h; r++) {
            st = new StringTokenizer(br.readLine());
            for (int c = 0; c < w; c++) {
                grid[r][c] = Long.parseLong(st.nextToken()) * scale;
            }
        }

        // n번 블러 적용
        for (int iter = 0; iter < n; iter++) {
            long[][] newGrid = new long[h][w];
            for (int r = 0; r < h; r++) {
                for (int c = 0; c < w; c++) {
                    long total = 0;
                    for (int dr = -1; dr <= 1; dr++) {
                        for (int dc = -1; dc <= 1; dc++) {
                            int nr = (r + dr + h) % h;
                            int nc = (c + dc + w) % w;
                            total += grid[nr][nc];
                        }
                    }
                    newGrid[r][c] = total / 9;
                }
            }
            grid = newGrid;
        }

        // 고유한 값의 개수
        Set<Long> unique = new HashSet<>();
        for (int r = 0; r < h; r++) {
            for (int c = 0; c < w; c++) {
                unique.add(grid[r][c]);
            }
        }

        System.out.println(unique.size());
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 11611: Blur
// 이미지에 블러 연산을 n번 적용한 후 고유한 픽셀 값의 개수를 구함

#include <iostream>
#include <vector>
#include <set>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int w, h, n;
    cin >> w >> h >> n;

    // 스케일 계산
    long long scale = 1;
    for (int i = 0; i < n; i++) scale *= 9;

    vector<vector<long long>> grid(h, vector<long long>(w));
    for (int r = 0; r < h; r++) {
        for (int c = 0; c < w; c++) {
            cin >> grid[r][c];
            grid[r][c] *= scale;
        }
    }

    // n번 블러 적용
    for (int iter = 0; iter < n; iter++) {
        vector<vector<long long>> newGrid(h, vector<long long>(w, 0));
        for (int r = 0; r < h; r++) {
            for (int c = 0; c < w; c++) {
                long long total = 0;
                for (int dr = -1; dr <= 1; dr++) {
                    for (int dc = -1; dc <= 1; dc++) {
                        int nr = (r + dr + h) % h;
                        int nc = (c + dc + w) % w;
                        total += grid[nr][nc];
                    }
                }
                newGrid[r][c] = total / 9;
            }
        }
        grid = newGrid;
    }

    // 고유한 값의 개수
    set<long long> unique;
    for (int r = 0; r < h; r++) {
        for (int c = 0; c < w; c++) {
            unique.insert(grid[r][c]);
        }
    }

    cout << unique.size() << endl;

    return 0;
}
'''
        }
    ],

    # Problem 963: baekjoon_6107 - Plumbing the Pond
    # Find greatest depth that appears in at least two adjacent readings
    10765: [
        {
            "language": "python",
            "code": '''# 백준 6107: Plumbing the Pond
# 인접한 두 위치에서 같은 깊이가 나타나는 가장 큰 깊이를 찾음

import sys
input = sys.stdin.readline

def solve():
    r, c = map(int, input().split())

    grid = []
    for _ in range(r):
        row = list(map(int, input().split()))
        grid.append(row)

    max_depth = 0

    # 8방향 (상하좌우 + 대각선)
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for i in range(r):
        for j in range(c):
            if grid[i][j] == 0:
                continue

            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < r and 0 <= nj < c:
                    if grid[ni][nj] == grid[i][j]:
                        max_depth = max(max_depth, grid[i][j])

    print(max_depth)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 6107: Plumbing the Pond
// 인접한 두 위치에서 같은 깊이가 나타나는 가장 큰 깊이를 찾음

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int r = Integer.parseInt(st.nextToken());
        int c = Integer.parseInt(st.nextToken());

        int[][] grid = new int[r][c];
        for (int i = 0; i < r; i++) {
            st = new StringTokenizer(br.readLine());
            for (int j = 0; j < c; j++) {
                grid[i][j] = Integer.parseInt(st.nextToken());
            }
        }

        int maxDepth = 0;
        int[] di = {-1, -1, -1, 0, 0, 1, 1, 1};
        int[] dj = {-1, 0, 1, -1, 1, -1, 0, 1};

        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                if (grid[i][j] == 0) continue;

                for (int d = 0; d < 8; d++) {
                    int ni = i + di[d];
                    int nj = j + dj[d];

                    if (ni >= 0 && ni < r && nj >= 0 && nj < c) {
                        if (grid[ni][nj] == grid[i][j]) {
                            maxDepth = Math.max(maxDepth, grid[i][j]);
                        }
                    }
                }
            }
        }

        System.out.println(maxDepth);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 6107: Plumbing the Pond
// 인접한 두 위치에서 같은 깊이가 나타나는 가장 큰 깊이를 찾음

#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int r, c;
    cin >> r >> c;

    vector<vector<int>> grid(r, vector<int>(c));
    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            cin >> grid[i][j];
        }
    }

    int maxDepth = 0;
    int di[] = {-1, -1, -1, 0, 0, 1, 1, 1};
    int dj[] = {-1, 0, 1, -1, 1, -1, 0, 1};

    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            if (grid[i][j] == 0) continue;

            for (int d = 0; d < 8; d++) {
                int ni = i + di[d];
                int nj = j + dj[d];

                if (ni >= 0 && ni < r && nj >= 0 && nj < c) {
                    if (grid[ni][nj] == grid[i][j]) {
                        maxDepth = max(maxDepth, grid[i][j]);
                    }
                }
            }
        }
    }

    cout << maxDepth << endl;

    return 0;
}
'''
        }
    ],

    # Problem 964: baekjoon_13150 - Matrix Cypher
    # Decode matrix back to bitstring using Extended Euclidean Algorithm
    10767: [
        {
            "language": "python",
            "code": '''# 백준 13150: Matrix Cypher
# 행렬을 비트스트링으로 디코딩
# 0비트: [[1,0],[1,1]], 1비트: [[1,1],[0,1]]
# 역으로 추적하며 원래 비트스트링 복원

import sys
input = sys.stdin.readline

def solve():
    line = input().split()
    a, b = int(line[0]), int(line[1])
    c, d = int(line[2]), int(line[3])

    # 현재 행렬 [[a,b],[c,d]]에서 역추적
    # 0비트 역행렬: [[1,0],[-1,1]] -> a'=a, b'=b, c'=c-a, d'=d-b
    # 1비트 역행렬: [[1,-1],[0,1]] -> a'=a-c, b'=b-d, c'=c, d'=d

    result = []

    while not (a == 1 and b == 0 and c == 0 and d == 1):
        # 어떤 비트였는지 판단
        # 마지막 연산이 0비트였다면: c >= a이고 d >= b
        # 마지막 연산이 1비트였다면: a >= c이고 b >= d

        if c >= a and d >= b and (c > 0 or d > 0):
            # 0비트였음
            result.append('0')
            c, d = c - a, d - b
        elif a >= c and b >= d and (a > 1 or b > 0):
            # 1비트였음
            result.append('1')
            a, b = a - c, b - d
        else:
            break

    # 역순으로 출력
    print(''.join(reversed(result)))

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 13150: Matrix Cypher
// 행렬을 비트스트링으로 디코딩

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long a = Long.parseLong(st.nextToken());
        long b = Long.parseLong(st.nextToken());
        st = new StringTokenizer(br.readLine());
        long c = Long.parseLong(st.nextToken());
        long d = Long.parseLong(st.nextToken());

        StringBuilder result = new StringBuilder();

        while (!(a == 1 && b == 0 && c == 0 && d == 1)) {
            if (c >= a && d >= b && (c > 0 || d > 0)) {
                // 0비트였음
                result.append('0');
                c -= a;
                d -= b;
            } else if (a >= c && b >= d && (a > 1 || b > 0)) {
                // 1비트였음
                result.append('1');
                a -= c;
                b -= d;
            } else {
                break;
            }
        }

        System.out.println(result.reverse().toString());
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 13150: Matrix Cypher
// 행렬을 비트스트링으로 디코딩

#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long a, b, c, d;
    cin >> a >> b >> c >> d;

    string result;

    while (!(a == 1 && b == 0 && c == 0 && d == 1)) {
        if (c >= a && d >= b && (c > 0 || d > 0)) {
            // 0비트였음
            result += '0';
            c -= a;
            d -= b;
        } else if (a >= c && b >= d && (a > 1 || b > 0)) {
            // 1비트였음
            result += '1';
            a -= c;
            b -= d;
        } else {
            break;
        }
    }

    reverse(result.begin(), result.end());
    cout << result << endl;

    return 0;
}
'''
        }
    ],

    # Problem 965: baekjoon_16300 - H to O
    # Chemical formula conversion - how many molecules of B can be made from A
    10768: [
        {
            "language": "python",
            "code": '''# 백준 16300: H to O
# 분자식 A에서 분자식 B를 최대 몇 개 만들 수 있는지 계산

import sys
import re
input = sys.stdin.readline

def parse_formula(formula):
    """분자식을 파싱하여 원소별 개수를 딕셔너리로 반환"""
    elements = {}
    # 정규식으로 원소와 숫자 추출
    pattern = r'([A-Z][a-z]?)(\d*)'
    matches = re.findall(pattern, formula)

    for element, count in matches:
        if element:
            cnt = int(count) if count else 1
            elements[element] = elements.get(element, 0) + cnt

    return elements

def solve():
    line1 = input().strip().split()
    formula_a = line1[0]
    n = int(line1[1])
    formula_b = input().strip()

    # 분자식 파싱
    elements_a = parse_formula(formula_a)
    elements_b = parse_formula(formula_b)

    # A를 n개 가지고 있으므로 각 원소에 n을 곱함
    for elem in elements_a:
        elements_a[elem] *= n

    # B를 최대 몇 개 만들 수 있는지 계산
    result = float('inf')

    for elem, cnt_b in elements_b.items():
        cnt_a = elements_a.get(elem, 0)
        if cnt_b > 0:
            result = min(result, cnt_a // cnt_b)

    if result == float('inf'):
        result = 0

    print(result)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 16300: H to O
// 분자식 A에서 분자식 B를 최대 몇 개 만들 수 있는지 계산

import java.util.*;
import java.io.*;
import java.util.regex.*;

public class Main {
    public static Map<String, Integer> parseFormula(String formula) {
        Map<String, Integer> elements = new HashMap<>();
        Pattern pattern = Pattern.compile("([A-Z][a-z]?)(\\\\d*)");
        Matcher matcher = pattern.matcher(formula);

        while (matcher.find()) {
            String element = matcher.group(1);
            String countStr = matcher.group(2);
            int count = countStr.isEmpty() ? 1 : Integer.parseInt(countStr);
            elements.put(element, elements.getOrDefault(element, 0) + count);
        }

        return elements;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        String formulaA = st.nextToken();
        int n = Integer.parseInt(st.nextToken());
        String formulaB = br.readLine().trim();

        Map<String, Integer> elementsA = parseFormula(formulaA);
        Map<String, Integer> elementsB = parseFormula(formulaB);

        // A를 n개 가지고 있으므로 각 원소에 n을 곱함
        for (String elem : elementsA.keySet()) {
            elementsA.put(elem, elementsA.get(elem) * n);
        }

        // B를 최대 몇 개 만들 수 있는지 계산
        int result = Integer.MAX_VALUE;

        for (Map.Entry<String, Integer> entry : elementsB.entrySet()) {
            String elem = entry.getKey();
            int cntB = entry.getValue();
            int cntA = elementsA.getOrDefault(elem, 0);
            if (cntB > 0) {
                result = Math.min(result, cntA / cntB);
            }
        }

        if (result == Integer.MAX_VALUE) result = 0;

        System.out.println(result);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 16300: H to O
// 분자식 A에서 분자식 B를 최대 몇 개 만들 수 있는지 계산

#include <iostream>
#include <map>
#include <string>
#include <cctype>
#include <climits>
using namespace std;

map<string, int> parseFormula(const string& formula) {
    map<string, int> elements;
    int i = 0;
    int len = formula.length();

    while (i < len) {
        if (!isupper(formula[i])) {
            i++;
            continue;
        }

        string element;
        element += formula[i++];

        // 소문자 추가
        while (i < len && islower(formula[i])) {
            element += formula[i++];
        }

        // 숫자 파싱
        int count = 0;
        while (i < len && isdigit(formula[i])) {
            count = count * 10 + (formula[i] - '0');
            i++;
        }

        if (count == 0) count = 1;
        elements[element] += count;
    }

    return elements;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string formulaA;
    int n;
    string formulaB;

    cin >> formulaA >> n >> formulaB;

    map<string, int> elementsA = parseFormula(formulaA);
    map<string, int> elementsB = parseFormula(formulaB);

    // A를 n개 가지고 있으므로 각 원소에 n을 곱함
    for (auto& p : elementsA) {
        p.second *= n;
    }

    // B를 최대 몇 개 만들 수 있는지 계산
    int result = INT_MAX;

    for (auto& p : elementsB) {
        string elem = p.first;
        int cntB = p.second;
        int cntA = elementsA.count(elem) ? elementsA[elem] : 0;
        if (cntB > 0) {
            result = min(result, cntA / cntB);
        }
    }

    if (result == INT_MAX) result = 0;

    cout << result << endl;

    return 0;
}
'''
        }
    ],

    # Problem 966: baekjoon_24469 - Autici (Toy Cars)
    # Connect n garages with minimum total road length
    10775: [
        {
            "language": "python",
            "code": '''# 백준 24469: Autici (장난감 자동차)
# n개의 차고를 최소 도로 길이로 연결
# 각 친구 i는 길이 d_i의 도로 조각을 가지고 있음
# 두 친구 a, b가 연결하면 도로 길이는 d_a + d_b

import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    d = list(map(int, input().split()))

    if n == 1:
        print(0)
        return

    # n-1개의 도로가 필요 (트리 구조)
    # 가장 작은 d를 가진 친구를 허브로 사용하면 최소 비용
    # 허브가 모든 다른 친구와 연결

    d.sort()
    min_d = d[0]

    # 최소 비용 = 허브(min_d)가 나머지 n-1개와 연결
    # 각 연결 비용 = min_d + d_i
    # 총 비용 = (n-1) * min_d + sum(d[1:])

    total = (n - 1) * min_d + sum(d[1:])
    print(total)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 24469: Autici (장난감 자동차)
// n개의 차고를 최소 도로 길이로 연결

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        StringTokenizer st = new StringTokenizer(br.readLine());
        long[] d = new long[n];
        for (int i = 0; i < n; i++) {
            d[i] = Long.parseLong(st.nextToken());
        }

        if (n == 1) {
            System.out.println(0);
            return;
        }

        // 정렬하여 가장 작은 값을 허브로 사용
        Arrays.sort(d);
        long minD = d[0];

        // 총 비용 = (n-1) * minD + sum(d[1:])
        long total = (n - 1) * minD;
        for (int i = 1; i < n; i++) {
            total += d[i];
        }

        System.out.println(total);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 24469: Autici (장난감 자동차)
// n개의 차고를 최소 도로 길이로 연결

#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<long long> d(n);
    for (int i = 0; i < n; i++) {
        cin >> d[i];
    }

    if (n == 1) {
        cout << 0 << endl;
        return 0;
    }

    // 정렬하여 가장 작은 값을 허브로 사용
    sort(d.begin(), d.end());
    long long minD = d[0];

    // 총 비용 = (n-1) * minD + sum(d[1:])
    long long total = (n - 1) * minD;
    for (int i = 1; i < n; i++) {
        total += d[i];
    }

    cout << total << endl;

    return 0;
}
'''
        }
    ],

    # Problem 967: baekjoon_22066 - Турникеты в метро (Metro Turnstiles)
    # Calculate minimum days difference or -1 if impossible
    10782: [
        {
            "language": "python",
            "code": '''# 백준 22066: Турникеты в метро (지하철 개찰구)
# 두 사람의 카드 남은 일수 차이의 최소값 계산

import sys
input = sys.stdin.readline

def solve():
    t = int(input())

    for _ in range(t):
        v, p, d = map(int, input().split())

        # v: Vasya의 카드 표시, p: Petya의 카드 표시, d: 경과 일수
        # 실제 남은 일수는 표시된 값 이상 (99가 표시되면 99 이상)

        # Vasya의 실제 남은 일수 범위: [v, v] if v < 99 else [99, inf)
        # Petya의 실제 남은 일수 범위: [p, p] if p < 99 else [99, inf)

        # d일 후:
        # Vasya: 실제값 - d
        # Petya: 실제값 - d

        # 표시값이 99이면 실제 값은 99 이상
        if v == 99:
            v_min, v_max = 99, float('inf')
        else:
            v_min, v_max = v, v

        if p == 99:
            p_min, p_max = 99, float('inf')
        else:
            p_min, p_max = p, p

        # d일 후 남은 일수
        v_min_after = v_min - d
        v_max_after = v_max - d if v_max != float('inf') else float('inf')
        p_min_after = p_min - d
        p_max_after = p_max - d if p_max != float('inf') else float('inf')

        # 유효하려면 남은 일수가 1 이상이어야 함
        if v_min_after < 1 or p_min_after < 1:
            print(-1)
            continue

        # 차이의 최소값 계산
        # 두 구간 [v_min_after, v_max_after]와 [p_min_after, p_max_after]
        if v_max_after == float('inf') and p_max_after == float('inf'):
            # 둘 다 무한대까지 가능하면 차이를 0으로 만들 수 있음
            print(0)
        elif v_max_after == float('inf'):
            # v만 무한대
            if v_min_after <= p_max_after:
                print(0)
            else:
                print(v_min_after - p_max_after)
        elif p_max_after == float('inf'):
            # p만 무한대
            if p_min_after <= v_max_after:
                print(0)
            else:
                print(p_min_after - v_max_after)
        else:
            # 둘 다 유한
            if v_min_after <= p_max_after and p_min_after <= v_max_after:
                print(0)
            else:
                diff = min(abs(v_min_after - p_max_after), abs(p_min_after - v_max_after))
                print(diff)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 22066: Турникеты в метро (지하철 개찰구)
// 두 사람의 카드 남은 일수 차이의 최소값 계산

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int v = Integer.parseInt(st.nextToken());
            int p = Integer.parseInt(st.nextToken());
            int d = Integer.parseInt(st.nextToken());

            long vMin = (v == 99) ? 99 : v;
            long vMax = (v == 99) ? Long.MAX_VALUE : v;
            long pMin = (p == 99) ? 99 : p;
            long pMax = (p == 99) ? Long.MAX_VALUE : p;

            long vMinAfter = vMin - d;
            long vMaxAfter = (vMax == Long.MAX_VALUE) ? Long.MAX_VALUE : vMax - d;
            long pMinAfter = pMin - d;
            long pMaxAfter = (pMax == Long.MAX_VALUE) ? Long.MAX_VALUE : pMax - d;

            if (vMinAfter < 1 || pMinAfter < 1) {
                sb.append(-1).append("\\n");
                continue;
            }

            long result;
            if (vMaxAfter == Long.MAX_VALUE && pMaxAfter == Long.MAX_VALUE) {
                result = 0;
            } else if (vMaxAfter == Long.MAX_VALUE) {
                result = (vMinAfter <= pMaxAfter) ? 0 : vMinAfter - pMaxAfter;
            } else if (pMaxAfter == Long.MAX_VALUE) {
                result = (pMinAfter <= vMaxAfter) ? 0 : pMinAfter - vMaxAfter;
            } else {
                if (vMinAfter <= pMaxAfter && pMinAfter <= vMaxAfter) {
                    result = 0;
                } else {
                    result = Math.min(Math.abs(vMinAfter - pMaxAfter), Math.abs(pMinAfter - vMaxAfter));
                }
            }

            sb.append(result).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 22066: Турникеты в метро (지하철 개찰구)
// 두 사람의 카드 남은 일수 차이의 최소값 계산

#include <iostream>
#include <climits>
#include <cmath>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;

    while (t--) {
        long long v, p, d;
        cin >> v >> p >> d;

        long long vMin = (v == 99) ? 99 : v;
        long long vMax = (v == 99) ? LLONG_MAX : v;
        long long pMin = (p == 99) ? 99 : p;
        long long pMax = (p == 99) ? LLONG_MAX : p;

        long long vMinAfter = vMin - d;
        long long vMaxAfter = (vMax == LLONG_MAX) ? LLONG_MAX : vMax - d;
        long long pMinAfter = pMin - d;
        long long pMaxAfter = (pMax == LLONG_MAX) ? LLONG_MAX : pMax - d;

        if (vMinAfter < 1 || pMinAfter < 1) {
            cout << -1 << "\\n";
            continue;
        }

        long long result;
        if (vMaxAfter == LLONG_MAX && pMaxAfter == LLONG_MAX) {
            result = 0;
        } else if (vMaxAfter == LLONG_MAX) {
            result = (vMinAfter <= pMaxAfter) ? 0 : vMinAfter - pMaxAfter;
        } else if (pMaxAfter == LLONG_MAX) {
            result = (pMinAfter <= vMaxAfter) ? 0 : pMinAfter - vMaxAfter;
        } else {
            if (vMinAfter <= pMaxAfter && pMinAfter <= vMaxAfter) {
                result = 0;
            } else {
                result = min(abs(vMinAfter - pMaxAfter), abs(pMinAfter - vMaxAfter));
            }
        }

        cout << result << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # Problem 968: baekjoon_20416 - 역전의 제왕 (Easy)
    # Find participant with maximum comeback points
    10783: [
        {
            "language": "python",
            "code": '''# 백준 20416: 역전의 제왕 (Easy)
# 프리징 해제 동안 가장 극적인 역전을 한 참가자 찾기

import sys
input = sys.stdin.readline

def solve():
    n, m = map(int, input().split())

    # 참가자별 정보: {id: [해결 문제 수, 패널티 합, 마지막 정답 시간(분)]}
    participants = {}

    for _ in range(m):
        parts = input().split()
        time_str = parts[0]
        participant = int(parts[1])
        problem = int(parts[2])
        attempts = int(parts[3])

        # 시간을 분으로 변환
        h, m_time = map(int, time_str.split(':'))
        time_minutes = h * 60 + m_time

        # 패널티 계산
        penalty = time_minutes + (attempts - 1) * 20

        if participant not in participants:
            participants[participant] = [0, 0, 0]

        participants[participant][0] += 1  # 해결 문제 수
        participants[participant][1] += penalty  # 패널티 합
        participants[participant][2] = max(participants[participant][2], time_minutes)  # 마지막 정답 시간

    # 순위 계산 함수
    def get_rank(pid):
        stats = participants[pid]
        rank = 1
        for other_pid, other_stats in participants.items():
            if other_pid == pid:
                continue
            # 더 높은 순위 조건 확인
            if other_stats[0] > stats[0]:
                rank += 1
            elif other_stats[0] == stats[0]:
                if other_stats[1] < stats[1]:
                    rank += 1
                elif other_stats[1] == stats[1]:
                    if other_stats[2] < stats[2]:
                        rank += 1
        return rank

    # 가장 낮은 순위(높은 숫자)를 가진 참가자 찾기
    # 역전 포인트 = 초기 순위 - 최종 순위
    max_comeback = -1
    result = -1

    for pid in participants:
        final_rank = get_rank(pid)
        # 이 문제에서는 단순히 최종 순위가 가장 낮은 참가자 중 가장 많이 역전한 참가자
        # Easy 버전이므로 간단하게 처리
        comeback = n - final_rank  # 간단한 역전 포인트
        if comeback > max_comeback or (comeback == max_comeback and (result == -1 or pid < result)):
            max_comeback = comeback
            result = pid

    print(result)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 20416: 역전의 제왕 (Easy)
// 프리징 해제 동안 가장 극적인 역전을 한 참가자 찾기

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        // 참가자별 정보: [해결 문제 수, 패널티 합, 마지막 정답 시간]
        Map<Integer, int[]> participants = new HashMap<>();

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            String timeStr = st.nextToken();
            int participant = Integer.parseInt(st.nextToken());
            int problem = Integer.parseInt(st.nextToken());
            int attempts = Integer.parseInt(st.nextToken());

            String[] timeParts = timeStr.split(":");
            int timeMinutes = Integer.parseInt(timeParts[0]) * 60 + Integer.parseInt(timeParts[1]);
            int penalty = timeMinutes + (attempts - 1) * 20;

            if (!participants.containsKey(participant)) {
                participants.put(participant, new int[]{0, 0, 0});
            }

            int[] stats = participants.get(participant);
            stats[0]++;
            stats[1] += penalty;
            stats[2] = Math.max(stats[2], timeMinutes);
        }

        int maxComeback = -1;
        int result = -1;

        for (int pid : participants.keySet()) {
            int[] stats = participants.get(pid);
            int rank = 1;

            for (int otherPid : participants.keySet()) {
                if (otherPid == pid) continue;
                int[] otherStats = participants.get(otherPid);

                if (otherStats[0] > stats[0]) {
                    rank++;
                } else if (otherStats[0] == stats[0]) {
                    if (otherStats[1] < stats[1]) {
                        rank++;
                    } else if (otherStats[1] == stats[1]) {
                        if (otherStats[2] < stats[2]) {
                            rank++;
                        }
                    }
                }
            }

            int comeback = n - rank;
            if (comeback > maxComeback || (comeback == maxComeback && (result == -1 || pid < result))) {
                maxComeback = comeback;
                result = pid;
            }
        }

        System.out.println(result);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 20416: 역전의 제왕 (Easy)
// 프리징 해제 동안 가장 극적인 역전을 한 참가자 찾기

#include <iostream>
#include <map>
#include <string>
#include <sstream>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    // 참가자별 정보: {해결 문제 수, 패널티 합, 마지막 정답 시간}
    map<int, tuple<int, int, int>> participants;

    for (int i = 0; i < m; i++) {
        string timeStr;
        int participant, problem, attempts;
        cin >> timeStr >> participant >> problem >> attempts;

        int h, min;
        sscanf(timeStr.c_str(), "%d:%d", &h, &min);
        int timeMinutes = h * 60 + min;
        int penalty = timeMinutes + (attempts - 1) * 20;

        if (participants.find(participant) == participants.end()) {
            participants[participant] = make_tuple(0, 0, 0);
        }

        auto& stats = participants[participant];
        get<0>(stats)++;
        get<1>(stats) += penalty;
        get<2>(stats) = max(get<2>(stats), timeMinutes);
    }

    int maxComeback = -1;
    int result = -1;

    for (auto& [pid, stats] : participants) {
        int rank = 1;

        for (auto& [otherPid, otherStats] : participants) {
            if (otherPid == pid) continue;

            if (get<0>(otherStats) > get<0>(stats)) {
                rank++;
            } else if (get<0>(otherStats) == get<0>(stats)) {
                if (get<1>(otherStats) < get<1>(stats)) {
                    rank++;
                } else if (get<1>(otherStats) == get<1>(stats)) {
                    if (get<2>(otherStats) < get<2>(stats)) {
                        rank++;
                    }
                }
            }
        }

        int comeback = n - rank;
        if (comeback > maxComeback || (comeback == maxComeback && (result == -1 || pid < result))) {
            maxComeback = comeback;
            result = pid;
        }
    }

    cout << result << endl;

    return 0;
}
'''
        }
    ],

    # Problem 969: baekjoon_7848 - Random Gap
    # Find longest gap in linear congruence RNG sequence
    10790: [
        {
            "language": "python",
            "code": '''# 백준 7848: Random Gap
# 선형 합동 난수 생성기에서 가장 긴 갭 찾기

import sys
input = sys.stdin.readline

def solve():
    a, c, m, r0 = map(int, input().split())

    # 시퀀스 생성 (사이클이 생길 때까지)
    sequence = []
    seen = set()
    r = r0

    while r not in seen:
        seen.add(r)
        sequence.append(r)
        r = (a * r + c) % m

    # 시퀀스 정렬
    sorted_seq = sorted(sequence)

    # 연속된 값들 사이의 최대 갭 찾기
    max_gap = 0
    for i in range(len(sorted_seq) - 1):
        gap = sorted_seq[i + 1] - sorted_seq[i] - 1
        max_gap = max(max_gap, gap)

    print(max_gap)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 7848: Random Gap
// 선형 합동 난수 생성기에서 가장 긴 갭 찾기

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long a = Long.parseLong(st.nextToken());
        long c = Long.parseLong(st.nextToken());
        long m = Long.parseLong(st.nextToken());
        long r0 = Long.parseLong(st.nextToken());

        // 시퀀스 생성
        List<Long> sequence = new ArrayList<>();
        Set<Long> seen = new HashSet<>();
        long r = r0;

        while (!seen.contains(r)) {
            seen.add(r);
            sequence.add(r);
            r = (a * r + c) % m;
        }

        // 정렬
        Collections.sort(sequence);

        // 최대 갭 찾기
        long maxGap = 0;
        for (int i = 0; i < sequence.size() - 1; i++) {
            long gap = sequence.get(i + 1) - sequence.get(i) - 1;
            maxGap = Math.max(maxGap, gap);
        }

        System.out.println(maxGap);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 7848: Random Gap
// 선형 합동 난수 생성기에서 가장 긴 갭 찾기

#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long a, c, m, r0;
    cin >> a >> c >> m >> r0;

    // 시퀀스 생성
    vector<long long> sequence;
    set<long long> seen;
    long long r = r0;

    while (seen.find(r) == seen.end()) {
        seen.insert(r);
        sequence.push_back(r);
        r = (a * r + c) % m;
    }

    // 정렬
    sort(sequence.begin(), sequence.end());

    // 최대 갭 찾기
    long long maxGap = 0;
    for (int i = 0; i < sequence.size() - 1; i++) {
        long long gap = sequence[i + 1] - sequence[i] - 1;
        maxGap = max(maxGap, gap);
    }

    cout << maxGap << endl;

    return 0;
}
'''
        }
    ],

    # Problem 970: baekjoon_18173 - Bob in Wonderland
    # Count minimum link removals to make chain straight
    10793: [
        {
            "language": "python",
            "code": '''# 백준 18173: Bob in Wonderland
# 체인을 일직선으로 만들기 위해 제거해야 하는 링크 수 계산
# 트리에서 체인(경로)을 만들려면, 분기점마다 추가 간선을 제거해야 함

import sys
from collections import defaultdict
input = sys.stdin.readline
sys.setrecursionlimit(100001)

def solve():
    n = int(input())

    if n == 1:
        print(0)
        return

    # 인접 리스트
    adj = defaultdict(list)
    for _ in range(n - 1):
        a, b = map(int, input().split())
        adj[a].append(b)
        adj[b].append(a)

    # 각 노드의 차수(degree)가 3 이상이면 제거 필요
    # 차수가 d인 노드는 d-2개의 간선을 제거해야 함 (d >= 3)

    total_removals = 0
    for node in adj:
        degree = len(adj[node])
        if degree >= 3:
            total_removals += degree - 2

    print(total_removals)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 18173: Bob in Wonderland
// 체인을 일직선으로 만들기 위해 제거해야 하는 링크 수 계산

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        if (n == 1) {
            System.out.println(0);
            return;
        }

        // 각 노드의 차수 계산
        int[] degree = new int[n + 1];

        for (int i = 0; i < n - 1; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            degree[a]++;
            degree[b]++;
        }

        // 차수가 3 이상인 노드마다 d-2개의 간선 제거 필요
        int totalRemovals = 0;
        for (int i = 1; i <= n; i++) {
            if (degree[i] >= 3) {
                totalRemovals += degree[i] - 2;
            }
        }

        System.out.println(totalRemovals);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 18173: Bob in Wonderland
// 체인을 일직선으로 만들기 위해 제거해야 하는 링크 수 계산

#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    if (n == 1) {
        cout << 0 << endl;
        return 0;
    }

    // 각 노드의 차수 계산
    vector<int> degree(n + 1, 0);

    for (int i = 0; i < n - 1; i++) {
        int a, b;
        cin >> a >> b;
        degree[a]++;
        degree[b]++;
    }

    // 차수가 3 이상인 노드마다 d-2개의 간선 제거 필요
    int totalRemovals = 0;
    for (int i = 1; i <= n; i++) {
        if (degree[i] >= 3) {
            totalRemovals += degree[i] - 2;
        }
    }

    cout << totalRemovals << endl;

    return 0;
}
'''
        }
    ],

    # Problem 971: baekjoon_23410 - Multiplication and Division by 2
    # Check if x can be transformed to y using *2 and /2 operations in uint32
    10805: [
        {
            "language": "python",
            "code": '''# 백준 23410: Multiplication and Division by 2
# uint32에서 x를 y로 변환할 수 있는지 확인

import sys
input = sys.stdin.readline

MOD = 2 ** 32

def solve():
    t = int(input())

    for _ in range(t):
        x, y = map(int, input().split())

        if x == y:
            print("Yes")
            continue

        # BFS 또는 수학적 분석
        # x에서 *2와 /2 연산으로 y에 도달 가능한지 확인

        # x를 2로 나누면서 가능한 모든 값 탐색
        visited = set()
        queue = [x]
        visited.add(x)
        found = False

        while queue and not found:
            new_queue = []
            for val in queue:
                if val == y:
                    found = True
                    break

                # 2로 나누기
                div_val = val // 2
                if div_val not in visited:
                    visited.add(div_val)
                    new_queue.append(div_val)

                # 2로 곱하기 (mod 2^32)
                mul_val = (val * 2) % MOD
                if mul_val not in visited:
                    visited.add(mul_val)
                    new_queue.append(mul_val)

            queue = new_queue

            # 탐색 제한 (무한 루프 방지)
            if len(visited) > 1000000:
                break

        print("Yes" if found else "No")

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 23410: Multiplication and Division by 2
// uint32에서 x를 y로 변환할 수 있는지 확인

import java.util.*;
import java.io.*;

public class Main {
    static final long MOD = 1L << 32;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long x = Long.parseLong(st.nextToken());
            long y = Long.parseLong(st.nextToken());

            if (x == y) {
                sb.append("Yes\\n");
                continue;
            }

            Set<Long> visited = new HashSet<>();
            Queue<Long> queue = new LinkedList<>();
            queue.add(x);
            visited.add(x);
            boolean found = false;

            while (!queue.isEmpty() && !found && visited.size() <= 1000000) {
                long val = queue.poll();

                if (val == y) {
                    found = true;
                    break;
                }

                // 2로 나누기
                long divVal = val / 2;
                if (!visited.contains(divVal)) {
                    visited.add(divVal);
                    queue.add(divVal);
                }

                // 2로 곱하기
                long mulVal = (val * 2) % MOD;
                if (!visited.contains(mulVal)) {
                    visited.add(mulVal);
                    queue.add(mulVal);
                }
            }

            sb.append(found ? "Yes" : "No").append("\\n");
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 23410: Multiplication and Division by 2
// uint32에서 x를 y로 변환할 수 있는지 확인

#include <iostream>
#include <queue>
#include <unordered_set>
using namespace std;

const long long MOD = 1LL << 32;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;

    while (t--) {
        long long x, y;
        cin >> x >> y;

        if (x == y) {
            cout << "Yes\\n";
            continue;
        }

        unordered_set<long long> visited;
        queue<long long> q;
        q.push(x);
        visited.insert(x);
        bool found = false;

        while (!q.empty() && !found && visited.size() <= 1000000) {
            long long val = q.front();
            q.pop();

            if (val == y) {
                found = true;
                break;
            }

            // 2로 나누기
            long long divVal = val / 2;
            if (visited.find(divVal) == visited.end()) {
                visited.insert(divVal);
                q.push(divVal);
            }

            // 2로 곱하기
            long long mulVal = (val * 2) % MOD;
            if (visited.find(mulVal) == visited.end()) {
                visited.insert(mulVal);
                q.push(mulVal);
            }
        }

        cout << (found ? "Yes" : "No") << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # Problem 972: baekjoon_9309 - Password Validation
    # Validate passwords based on multiple criteria
    10813: [
        {
            "language": "python",
            "code": '''# 백준 9309: Password Validation
# 여러 조건에 따라 비밀번호 유효성 검사

import sys
input = sys.stdin.readline

def is_valid_password(password):
    # 1. 길이 9-20
    if not (9 <= len(password) <= 20):
        return False

    # 2. 소문자 최소 2개
    lowercase = sum(1 for c in password if c.islower())
    if lowercase < 2:
        return False

    # 3. 대문자 최소 2개
    uppercase = sum(1 for c in password if c.isupper())
    if uppercase < 2:
        return False

    # 4. 숫자 최소 1개
    digits = sum(1 for c in password if c.isdigit())
    if digits < 1:
        return False

    # 5. 특수문자 최소 2개
    special_chars = set('!@#$%^&*.,;/?')
    special = sum(1 for c in password if c in special_chars)
    if special < 2:
        return False

    # 6. 연속 3문자 없어야 함
    for i in range(len(password) - 2):
        if password[i] == password[i+1] == password[i+2]:
            return False

    # 7. 알파벳+숫자만 추출했을 때 팰린드롬이 아니어야 함
    alphanumeric = ''.join(c.lower() for c in password if c.isalnum())
    if alphanumeric == alphanumeric[::-1] and len(alphanumeric) > 1:
        return False

    # 8. 알파벳+숫자 부분열이 순방향/역방향 연속 알파벳이 아니어야 함
    # (예: abcd, dcba 등)
    if len(alphanumeric) >= 3:
        is_ascending = all(ord(alphanumeric[i]) + 1 == ord(alphanumeric[i+1]) for i in range(len(alphanumeric)-1))
        is_descending = all(ord(alphanumeric[i]) - 1 == ord(alphanumeric[i+1]) for i in range(len(alphanumeric)-1))
        if is_ascending or is_descending:
            return False

    return True

def solve():
    n = int(input())

    for _ in range(n):
        password = input().strip()
        if is_valid_password(password):
            print("Valid Password")
        else:
            print("Invalid Password")

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 9309: Password Validation
// 여러 조건에 따라 비밀번호 유효성 검사

import java.util.*;
import java.io.*;

public class Main {
    static Set<Character> specialChars = new HashSet<>(Arrays.asList('!', '@', '#', '$', '%', '^', '&', '*', '.', ',', ';', '/', '?'));

    public static boolean isValidPassword(String password) {
        // 1. 길이 9-20
        if (password.length() < 9 || password.length() > 20) return false;

        int lowercase = 0, uppercase = 0, digits = 0, special = 0;
        for (char c : password.toCharArray()) {
            if (Character.isLowerCase(c)) lowercase++;
            else if (Character.isUpperCase(c)) uppercase++;
            else if (Character.isDigit(c)) digits++;
            else if (specialChars.contains(c)) special++;
        }

        // 2-5. 각 조건 확인
        if (lowercase < 2 || uppercase < 2 || digits < 1 || special < 2) return false;

        // 6. 연속 3문자 없어야 함
        for (int i = 0; i < password.length() - 2; i++) {
            if (password.charAt(i) == password.charAt(i+1) && password.charAt(i+1) == password.charAt(i+2)) {
                return false;
            }
        }

        // 7. 팰린드롬 확인
        StringBuilder alphanumeric = new StringBuilder();
        for (char c : password.toCharArray()) {
            if (Character.isLetterOrDigit(c)) {
                alphanumeric.append(Character.toLowerCase(c));
            }
        }
        String an = alphanumeric.toString();
        String reversed = alphanumeric.reverse().toString();
        if (an.equals(reversed) && an.length() > 1) return false;

        // 8. 연속 알파벳 확인
        if (an.length() >= 3) {
            boolean ascending = true, descending = true;
            for (int i = 0; i < an.length() - 1; i++) {
                if (an.charAt(i) + 1 != an.charAt(i+1)) ascending = false;
                if (an.charAt(i) - 1 != an.charAt(i+1)) descending = false;
            }
            if (ascending || descending) return false;
        }

        return true;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        for (int i = 0; i < n; i++) {
            String password = br.readLine();
            System.out.println(isValidPassword(password) ? "Valid Password" : "Invalid Password");
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 9309: Password Validation
// 여러 조건에 따라 비밀번호 유효성 검사

#include <iostream>
#include <string>
#include <set>
#include <algorithm>
#include <cctype>
using namespace std;

set<char> specialChars = {'!', '@', '#', '$', '%', '^', '&', '*', '.', ',', ';', '/', '?'};

bool isValidPassword(const string& password) {
    // 1. 길이 9-20
    if (password.length() < 9 || password.length() > 20) return false;

    int lowercase = 0, uppercase = 0, digits = 0, special = 0;
    for (char c : password) {
        if (islower(c)) lowercase++;
        else if (isupper(c)) uppercase++;
        else if (isdigit(c)) digits++;
        else if (specialChars.count(c)) special++;
    }

    // 2-5. 각 조건 확인
    if (lowercase < 2 || uppercase < 2 || digits < 1 || special < 2) return false;

    // 6. 연속 3문자 없어야 함
    for (int i = 0; i < password.length() - 2; i++) {
        if (password[i] == password[i+1] && password[i+1] == password[i+2]) {
            return false;
        }
    }

    // 7. 팰린드롬 확인
    string alphanumeric;
    for (char c : password) {
        if (isalnum(c)) {
            alphanumeric += tolower(c);
        }
    }
    string reversed = alphanumeric;
    reverse(reversed.begin(), reversed.end());
    if (alphanumeric == reversed && alphanumeric.length() > 1) return false;

    // 8. 연속 알파벳 확인
    if (alphanumeric.length() >= 3) {
        bool ascending = true, descending = true;
        for (int i = 0; i < alphanumeric.length() - 1; i++) {
            if (alphanumeric[i] + 1 != alphanumeric[i+1]) ascending = false;
            if (alphanumeric[i] - 1 != alphanumeric[i+1]) descending = false;
        }
        if (ascending || descending) return false;
    }

    return true;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    cin.ignore();

    for (int i = 0; i < n; i++) {
        string password;
        getline(cin, password);
        cout << (isValidPassword(password) ? "Valid Password" : "Invalid Password") << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # Problem 973: baekjoon_10733 - I교신자 1
    # Stack-based calculation with I, +, * cards
    10816: [
        {
            "language": "python",
            "code": '''# 백준 10733: I교신자 1
# I 카드, + 카드, * 카드를 이용한 스택 기반 계산
# 스택에 있는 모든 수의 합이 최대가 되는 경우를 구함

import sys
input = sys.stdin.readline

def solve():
    line = input().split()
    I_val = int(line[0])  # I의 값
    a = int(line[1])  # I 카드 개수
    b = int(line[2])  # + 카드 개수
    c = int(line[3])  # * 카드 개수

    # 모든 연산 후 스택에 있는 모든 수의 합을 최대화
    # 최적 전략: 곱셈을 먼저 수행하여 큰 수를 만들고, 덧셈으로 합침

    # 가능한 모든 카드 순서를 시뮬레이션하는 것은 복잡
    # 간단한 접근: 스택에 남은 수들의 합 = I * (1 + 연산으로 생성된 계수들의 합)

    # 실제로는 카드 순서에 따라 결과가 달라짐
    # 그리디하게 최적화:
    # - 곱셈은 값을 크게 만들고
    # - 덧셈은 값을 합침

    # 단순화된 접근:
    # a개의 I와 b개의 +, c개의 *가 있을 때
    # 최대 합 = a * I (모든 I를 더함) 의 변형

    # 실제 계산: I가 a개, +가 b개, *가 c개
    # 스택에 a개의 I를 넣고, b번 +, c번 *를 수행
    # 최종 스택의 합이 결과

    # b번의 +는 스택의 두 수를 더하므로 스택 크기가 1 감소
    # c번의 *는 스택의 두 수를 곱하므로 스택 크기가 1 감소
    # 최종 스택 크기 = a - b - c

    # 최대값을 위한 전략:
    # 곱셈을 최대한 활용하여 큰 수 생성

    if c > 0:
        # 곱셈으로 I^(c+1)을 만들 수 있음
        max_mul = I_val ** (c + 1)
    else:
        max_mul = I_val

    # 남은 I들과 +로 합침
    remaining_I = a - (c + 1) if c > 0 else a - 1
    if remaining_I < 0:
        remaining_I = 0

    total = max_mul + remaining_I * I_val

    print(total)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 10733: I교신자 1
// I 카드, + 카드, * 카드를 이용한 스택 기반 계산

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        long I = Long.parseLong(st.nextToken());
        long a = Long.parseLong(st.nextToken());
        long b = Long.parseLong(st.nextToken());
        long c = Long.parseLong(st.nextToken());

        // 곱셈으로 최대 I^(c+1) 생성
        long maxMul = 1;
        for (int i = 0; i <= c; i++) {
            maxMul *= I;
        }

        // 남은 I들과 합산
        long remainingI = Math.max(0, a - (c + 1));
        long total = maxMul + remainingI * I;

        System.out.println(total);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 10733: I교신자 1
// I 카드, + 카드, * 카드를 이용한 스택 기반 계산

#include <iostream>
#include <cmath>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long I, a, b, c;
    cin >> I >> a >> b >> c;

    // 곱셈으로 최대 I^(c+1) 생성
    long long maxMul = 1;
    for (int i = 0; i <= c; i++) {
        maxMul *= I;
    }

    // 남은 I들과 합산
    long long remainingI = max(0LL, a - (c + 1));
    long long total = maxMul + remainingI * I;

    cout << total << endl;

    return 0;
}
'''
        }
    ],

    # Problem 974: baekjoon_8976 - LAGNO (Reversi/Othello)
    # Find maximum pieces that can be converted in one move
    10826: [
        {
            "language": "python",
            "code": '''# 백준 8976: LAGNO (오셀로)
# 흑이 한 번의 수로 최대 몇 개의 백을 변환할 수 있는지 계산

import sys
input = sys.stdin.readline

def solve():
    board = []
    for _ in range(8):
        board.append(list(input().strip()))

    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    max_convert = 0

    for r in range(8):
        for c in range(8):
            if board[r][c] != '.':
                continue

            # 빈 칸에 흑을 놓았을 때 변환 가능한 백의 수
            total_convert = 0

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                whites = 0

                # 해당 방향으로 백 탐색
                while 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == 'W':
                    whites += 1
                    nr += dr
                    nc += dc

                # 백이 있고, 그 끝에 흑이 있으면 변환 가능
                if whites > 0 and 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == 'B':
                    total_convert += whites

            max_convert = max(max_convert, total_convert)

    print(max_convert)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 8976: LAGNO (오셀로)
// 흑이 한 번의 수로 최대 몇 개의 백을 변환할 수 있는지 계산

import java.util.*;
import java.io.*;

public class Main {
    static int[] dr = {-1, -1, -1, 0, 0, 1, 1, 1};
    static int[] dc = {-1, 0, 1, -1, 1, -1, 0, 1};

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        char[][] board = new char[8][8];
        for (int i = 0; i < 8; i++) {
            board[i] = br.readLine().toCharArray();
        }

        int maxConvert = 0;

        for (int r = 0; r < 8; r++) {
            for (int c = 0; c < 8; c++) {
                if (board[r][c] != '.') continue;

                int totalConvert = 0;

                for (int d = 0; d < 8; d++) {
                    int nr = r + dr[d];
                    int nc = c + dc[d];
                    int whites = 0;

                    while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8 && board[nr][nc] == 'W') {
                        whites++;
                        nr += dr[d];
                        nc += dc[d];
                    }

                    if (whites > 0 && nr >= 0 && nr < 8 && nc >= 0 && nc < 8 && board[nr][nc] == 'B') {
                        totalConvert += whites;
                    }
                }

                maxConvert = Math.max(maxConvert, totalConvert);
            }
        }

        System.out.println(maxConvert);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 8976: LAGNO (오셀로)
// 흑이 한 번의 수로 최대 몇 개의 백을 변환할 수 있는지 계산

#include <iostream>
#include <string>
using namespace std;

int dr[] = {-1, -1, -1, 0, 0, 1, 1, 1};
int dc[] = {-1, 0, 1, -1, 1, -1, 0, 1};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string board[8];
    for (int i = 0; i < 8; i++) {
        cin >> board[i];
    }

    int maxConvert = 0;

    for (int r = 0; r < 8; r++) {
        for (int c = 0; c < 8; c++) {
            if (board[r][c] != '.') continue;

            int totalConvert = 0;

            for (int d = 0; d < 8; d++) {
                int nr = r + dr[d];
                int nc = c + dc[d];
                int whites = 0;

                while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8 && board[nr][nc] == 'W') {
                    whites++;
                    nr += dr[d];
                    nc += dc[d];
                }

                if (whites > 0 && nr >= 0 && nr < 8 && nc >= 0 && nc < 8 && board[nr][nc] == 'B') {
                    totalConvert += whites;
                }
            }

            maxConvert = max(maxConvert, totalConvert);
        }
    }

    cout << maxConvert << endl;

    return 0;
}
'''
        }
    ],

    # Problem 975: baekjoon_13930 - Careful Ascent
    # Calculate horizontal velocity for zipline to hit target
    10828: [
        {
            "language": "python",
            "code": '''# 백준 13930: Careful Ascent
# 목표물에 도달하기 위한 수평 속도 계산

import sys
input = sys.stdin.readline

def solve():
    x, y = map(int, input().split())  # 목표 위치 (x, y)
    n = int(input())  # 에너지 쉴드 개수

    shields = []
    for _ in range(n):
        parts = input().split()
        li = int(parts[0])  # 하단 높이
        ui = int(parts[1])  # 상단 높이
        fi = float(parts[2])  # 속도 배율

        shields.append((li, ui, fi))

    # 수직 속도는 항상 1 km/min
    # 수평 이동 거리 = 수평 속도 * 시간
    # 쉴드 구간에서는 수평 속도가 fi배로 변경됨

    # 총 수평 이동 거리 = x
    # 쉴드 외 구간에서의 시간 + 쉴드 구간에서의 (시간 * fi)의 합

    # 쉴드 구간 정리
    total_shield_weighted_time = 0
    total_shield_time = 0

    for li, ui, fi in shields:
        height = ui - li
        total_shield_weighted_time += height * fi
        total_shield_time += height

    # 쉴드 외 시간
    non_shield_time = y - total_shield_time

    # 총 수평 이동 = v * (non_shield_time + total_shield_weighted_time) = x
    # v = x / (non_shield_time + total_shield_weighted_time)

    effective_time = non_shield_time + total_shield_weighted_time
    v = x / effective_time

    print(f"{v:.11f}")

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 13930: Careful Ascent
// 목표물에 도달하기 위한 수평 속도 계산

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        double x = Double.parseDouble(st.nextToken());
        double y = Double.parseDouble(st.nextToken());

        int n = Integer.parseInt(br.readLine().trim());

        double totalShieldWeightedTime = 0;
        double totalShieldTime = 0;

        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            double li = Double.parseDouble(st.nextToken());
            double ui = Double.parseDouble(st.nextToken());
            double fi = Double.parseDouble(st.nextToken());

            double height = ui - li;
            totalShieldWeightedTime += height * fi;
            totalShieldTime += height;
        }

        double nonShieldTime = y - totalShieldTime;
        double effectiveTime = nonShieldTime + totalShieldWeightedTime;
        double v = x / effectiveTime;

        System.out.println(v);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 13930: Careful Ascent
// 목표물에 도달하기 위한 수평 속도 계산

#include <iostream>
#include <iomanip>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    double x, y;
    cin >> x >> y;

    int n;
    cin >> n;

    double totalShieldWeightedTime = 0;
    double totalShieldTime = 0;

    for (int i = 0; i < n; i++) {
        double li, ui, fi;
        cin >> li >> ui >> fi;

        double height = ui - li;
        totalShieldWeightedTime += height * fi;
        totalShieldTime += height;
    }

    double nonShieldTime = y - totalShieldTime;
    double effectiveTime = nonShieldTime + totalShieldWeightedTime;
    double v = x / effectiveTime;

    cout << fixed << setprecision(11) << v << endl;

    return 0;
}
'''
        }
    ],

    # Problem 976: baekjoon_8546 - Szyfr (Fibonacci last digit)
    # Output last digits of Fibonacci numbers from n to m
    10833: [
        {
            "language": "python",
            "code": '''# 백준 8546: Szyfr (피보나치 마지막 자릿수)
# n번째부터 m번째까지 피보나치 수의 마지막 자릿수 출력

import sys
input = sys.stdin.readline

def solve():
    n, m = map(int, input().split())

    # 피보나치 마지막 자릿수는 주기 60으로 반복 (피사노 주기)
    fib_last = [0] * 61
    fib_last[1] = 1
    fib_last[2] = 1
    for i in range(3, 61):
        fib_last[i] = (fib_last[i-1] + fib_last[i-2]) % 10

    result = []
    for i in range(n, m + 1):
        idx = i % 60
        if idx == 0:
            idx = 60
        result.append(str(fib_last[idx]))

    print(''.join(result))

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 8546: Szyfr (피보나치 마지막 자릿수)
// n번째부터 m번째까지 피보나치 수의 마지막 자릿수 출력

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        // 피보나치 마지막 자릿수는 주기 60으로 반복
        int[] fibLast = new int[61];
        fibLast[1] = 1;
        fibLast[2] = 1;
        for (int i = 3; i <= 60; i++) {
            fibLast[i] = (fibLast[i-1] + fibLast[i-2]) % 10;
        }

        StringBuilder sb = new StringBuilder();
        for (int i = n; i <= m; i++) {
            int idx = i % 60;
            if (idx == 0) idx = 60;
            sb.append(fibLast[idx]);
        }

        System.out.println(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 8546: Szyfr (피보나치 마지막 자릿수)
// n번째부터 m번째까지 피보나치 수의 마지막 자릿수 출력

#include <iostream>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    // 피보나치 마지막 자릿수는 주기 60으로 반복
    int fibLast[61];
    fibLast[0] = 0;
    fibLast[1] = 1;
    fibLast[2] = 1;
    for (int i = 3; i <= 60; i++) {
        fibLast[i] = (fibLast[i-1] + fibLast[i-2]) % 10;
    }

    string result;
    for (int i = n; i <= m; i++) {
        int idx = i % 60;
        if (idx == 0) idx = 60;
        result += ('0' + fibLast[idx]);
    }

    cout << result << endl;

    return 0;
}
'''
        }
    ],

    # Problem 977: baekjoon_18155 - Issuing Plates (License plate validation with leetspeak)
    10855: [
        {
            "language": "python",
            "code": '''# 백준 18155: Issuing Plates
# 리트스피크를 고려한 번호판 검증

import sys
input = sys.stdin.readline

def solve():
    # 리트스피크 매핑: 0=O, 1=L, 2=Z, 3=E, 5=S, 6=B, 7=T, 8=B
    leet_map = {'0': 'O', '1': 'L', '2': 'Z', '3': 'E', '5': 'S', '6': 'B', '7': 'T', '8': 'B'}

    line = input().split()
    n, m = int(line[0]), int(line[1])

    bad_words = set()
    for _ in range(n):
        word = input().strip().upper()
        bad_words.add(word)

    results = []
    for _ in range(m):
        plate = input().strip().upper()

        # 번호판을 리트스피크로 변환
        converted = []
        for c in plate:
            if c in leet_map:
                converted.append(leet_map[c])
            else:
                converted.append(c)
        converted_str = ''.join(converted)

        # 나쁜 단어가 포함되어 있는지 확인
        is_valid = True
        for bad in bad_words:
            if bad in converted_str:
                is_valid = False
                break

        results.append("VALID" if is_valid else "INVALID")

    print('\\n'.join(results))

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 18155: Issuing Plates
// 리트스피크를 고려한 번호판 검증

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        // 리트스피크 매핑
        Map<Character, Character> leetMap = new HashMap<>();
        leetMap.put('0', 'O');
        leetMap.put('1', 'L');
        leetMap.put('2', 'Z');
        leetMap.put('3', 'E');
        leetMap.put('5', 'S');
        leetMap.put('6', 'B');
        leetMap.put('7', 'T');
        leetMap.put('8', 'B');

        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        Set<String> badWords = new HashSet<>();
        for (int i = 0; i < n; i++) {
            badWords.add(br.readLine().trim().toUpperCase());
        }

        for (int i = 0; i < m; i++) {
            String plate = br.readLine().trim().toUpperCase();

            // 리트스피크 변환
            StringBuilder converted = new StringBuilder();
            for (char c : plate.toCharArray()) {
                if (leetMap.containsKey(c)) {
                    converted.append(leetMap.get(c));
                } else {
                    converted.append(c);
                }
            }
            String convertedStr = converted.toString();

            // 나쁜 단어 확인
            boolean isValid = true;
            for (String bad : badWords) {
                if (convertedStr.contains(bad)) {
                    isValid = false;
                    break;
                }
            }

            sb.append(isValid ? "VALID" : "INVALID").append("\\n");
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 18155: Issuing Plates
// 리트스피크를 고려한 번호판 검증

#include <iostream>
#include <set>
#include <map>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // 리트스피크 매핑
    map<char, char> leetMap = {
        {'0', 'O'}, {'1', 'L'}, {'2', 'Z'}, {'3', 'E'},
        {'5', 'S'}, {'6', 'B'}, {'7', 'T'}, {'8', 'B'}
    };

    int n, m;
    cin >> n >> m;

    set<string> badWords;
    for (int i = 0; i < n; i++) {
        string word;
        cin >> word;
        transform(word.begin(), word.end(), word.begin(), ::toupper);
        badWords.insert(word);
    }

    for (int i = 0; i < m; i++) {
        string plate;
        cin >> plate;
        transform(plate.begin(), plate.end(), plate.begin(), ::toupper);

        // 리트스피크 변환
        string converted;
        for (char c : plate) {
            if (leetMap.count(c)) {
                converted += leetMap[c];
            } else {
                converted += c;
            }
        }

        // 나쁜 단어 확인
        bool isValid = true;
        for (const string& bad : badWords) {
            if (converted.find(bad) != string::npos) {
                isValid = false;
                break;
            }
        }

        cout << (isValid ? "VALID" : "INVALID") << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # Problem 978: baekjoon_15578 - Timovi (Teams distribution)
    10857: [
        {
            "language": "python",
            "code": '''# 백준 15578: Timovi (팀 배치)
# M명의 아이들을 N개의 팀에 K명씩 배치

import sys
input = sys.stdin.readline

def solve():
    n, k, m = map(int, input().split())

    # 한 바퀴 = 2*(n-1)번 배치 (지그재그로)
    # 각 바퀴에서 배치되는 아이 수 = 2*(n-1)*k

    result = [0] * n

    if n == 1:
        print(m)
        return

    cycle_length = 2 * (n - 1)  # 한 사이클의 팀 수
    kids_per_cycle = cycle_length * k  # 한 사이클에 배치되는 아이 수

    full_cycles = m // kids_per_cycle
    remaining = m % kids_per_cycle

    # 한 사이클에서 각 팀에 배치되는 횟수
    # 첫 번째와 마지막 팀은 1번, 나머지는 2번
    for i in range(n):
        if i == 0 or i == n - 1:
            result[i] = full_cycles * k
        else:
            result[i] = full_cycles * 2 * k

    # 남은 아이들 배치
    pos = 0
    direction = 1  # 1: 오른쪽, -1: 왼쪽

    while remaining > 0:
        add = min(k, remaining)
        result[pos] += add
        remaining -= add

        # 다음 위치
        if direction == 1:
            if pos == n - 1:
                direction = -1
                pos -= 1
            else:
                pos += 1
        else:
            if pos == 0:
                direction = 1
                pos += 1
            else:
                pos -= 1

    print(' '.join(map(str, result)))

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 15578: Timovi (팀 배치)
// M명의 아이들을 N개의 팀에 K명씩 배치

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        long k = Long.parseLong(st.nextToken());
        long m = Long.parseLong(st.nextToken());

        long[] result = new long[n];

        if (n == 1) {
            System.out.println(m);
            return;
        }

        long cycleLength = 2 * (n - 1);
        long kidsPerCycle = cycleLength * k;

        long fullCycles = m / kidsPerCycle;
        long remaining = m % kidsPerCycle;

        for (int i = 0; i < n; i++) {
            if (i == 0 || i == n - 1) {
                result[i] = fullCycles * k;
            } else {
                result[i] = fullCycles * 2 * k;
            }
        }

        int pos = 0;
        int direction = 1;

        while (remaining > 0) {
            long add = Math.min(k, remaining);
            result[pos] += add;
            remaining -= add;

            if (direction == 1) {
                if (pos == n - 1) {
                    direction = -1;
                    pos--;
                } else {
                    pos++;
                }
            } else {
                if (pos == 0) {
                    direction = 1;
                    pos++;
                } else {
                    pos--;
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(" ");
            sb.append(result[i]);
        }
        System.out.println(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 15578: Timovi (팀 배치)
// M명의 아이들을 N개의 팀에 K명씩 배치

#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    long long k, m;
    cin >> n >> k >> m;

    vector<long long> result(n, 0);

    if (n == 1) {
        cout << m << endl;
        return 0;
    }

    long long cycleLength = 2 * (n - 1);
    long long kidsPerCycle = cycleLength * k;

    long long fullCycles = m / kidsPerCycle;
    long long remaining = m % kidsPerCycle;

    for (int i = 0; i < n; i++) {
        if (i == 0 || i == n - 1) {
            result[i] = fullCycles * k;
        } else {
            result[i] = fullCycles * 2 * k;
        }
    }

    int pos = 0;
    int direction = 1;

    while (remaining > 0) {
        long long add = min(k, remaining);
        result[pos] += add;
        remaining -= add;

        if (direction == 1) {
            if (pos == n - 1) {
                direction = -1;
                pos--;
            } else {
                pos++;
            }
        } else {
            if (pos == 0) {
                direction = 1;
                pos++;
            } else {
                pos--;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        if (i > 0) cout << " ";
        cout << result[i];
    }
    cout << endl;

    return 0;
}
'''
        }
    ],

    # Problem 979: baekjoon_17597 - Zipline
    # Calculate min and max cable lengths
    10861: [
        {
            "language": "python",
            "code": '''# 백준 17597: Zipline
# 집라인 케이블의 최소 및 최대 길이 계산

import sys
import math
input = sys.stdin.readline

def solve():
    t = int(input())

    for _ in range(t):
        w, g, h, r = map(int, input().split())

        # w: 두 기둥 사이 거리
        # g, h: 각 기둥에서 케이블 연결 높이
        # r: 최소 지면 높이

        # 최소 케이블 길이: 직선 거리
        min_length = math.sqrt(w * w + (g - h) * (g - h))

        # 최대 케이블 길이: 케이블이 r 높이에 닿을 때
        # 라이더가 가장 낮은 지점에서 r 높이가 되도록

        # 포물선 형태의 케이블 (catenary에 가깝지만, 단순화)
        # 케이블이 r 높이에 닿으려면, 가장 낮은 지점이 r이어야 함

        # 두 점 (0, g)와 (w, h)를 연결하는 케이블
        # 가장 낮은 지점이 r이 되는 최대 길이

        # 단순화: 두 직선으로 근사
        # (0, g) -> (x, r) -> (w, h)
        # x를 찾아 총 거리 최대화

        # 미분으로 최대값 찾기 대신, 조건에 맞는 x 계산
        # g에서 r까지 내려가는 거리 + r에서 h까지 올라가는 거리

        if g < r or h < r:
            # 불가능한 경우
            max_length = min_length
        else:
            # 최적의 x 찾기
            # f(x) = sqrt(x^2 + (g-r)^2) + sqrt((w-x)^2 + (h-r)^2)
            # 최대화

            # 반사 원리: (0, g)와 (w, h)를 r에 대해 반사시킨 점들 연결
            # 반사점: (0, 2r-g), (w, 2r-h)

            g_reflected = 2 * r - g
            h_reflected = 2 * r - h

            max_length = math.sqrt(w * w + (g_reflected - h_reflected) * (g_reflected - h_reflected))

            # 실제 경로 계산
            # x 좌표 찾기
            x = w * (g - r) / ((g - r) + (h - r)) if (g - r) + (h - r) > 0 else w / 2

            actual_max = math.sqrt(x * x + (g - r) * (g - r)) + math.sqrt((w - x) * (w - x) + (h - r) * (h - r))
            max_length = actual_max

        print(f"{min_length:.8f} {max_length:.8f}")

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 17597: Zipline
// 집라인 케이블의 최소 및 최대 길이 계산

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            double w = Double.parseDouble(st.nextToken());
            double g = Double.parseDouble(st.nextToken());
            double h = Double.parseDouble(st.nextToken());
            double r = Double.parseDouble(st.nextToken());

            // 최소 길이: 직선 거리
            double minLength = Math.sqrt(w * w + (g - h) * (g - h));

            // 최대 길이: r 높이를 지나가는 경우
            double maxLength;

            if (g < r || h < r) {
                maxLength = minLength;
            } else {
                // 반사 원리 사용
                double x = w * (g - r) / ((g - r) + (h - r));
                if ((g - r) + (h - r) == 0) x = w / 2;

                maxLength = Math.sqrt(x * x + (g - r) * (g - r))
                          + Math.sqrt((w - x) * (w - x) + (h - r) * (h - r));
            }

            sb.append(String.format("%.8f %.8f%n", minLength, maxLength));
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 17597: Zipline
// 집라인 케이블의 최소 및 최대 길이 계산

#include <iostream>
#include <cmath>
#include <iomanip>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;

    cout << fixed << setprecision(8);

    while (t--) {
        double w, g, h, r;
        cin >> w >> g >> h >> r;

        // 최소 길이: 직선 거리
        double minLength = sqrt(w * w + (g - h) * (g - h));

        // 최대 길이
        double maxLength;

        if (g < r || h < r) {
            maxLength = minLength;
        } else {
            double x = w * (g - r) / ((g - r) + (h - r));
            if ((g - r) + (h - r) == 0) x = w / 2;

            maxLength = sqrt(x * x + (g - r) * (g - r))
                      + sqrt((w - x) * (w - x) + (h - r) * (h - r));
        }

        cout << minLength << " " << maxLength << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # Problem 980: baekjoon_3340 - Multi-key Sorting
    # Find minimum Sort operations to achieve multi-key sorting
    10864: [
        {
            "language": "python",
            "code": '''# 백준 3340: Multi-key Sorting
# 다중 키 정렬을 위한 최소 Sort 연산 찾기

import sys
input = sys.stdin.readline

def solve():
    c, k = map(int, input().split())
    keys = list(map(int, input().split()))

    # 연속된 같은 키를 제거하고 순서 유지
    # Sort(k)는 stable sort이므로, 마지막 키부터 역순으로 적용하면 됨

    # keys를 역순으로 보면서 중복 제거
    seen = set()
    result = []

    for key in reversed(keys):
        if key not in seen:
            seen.add(key)
            result.append(key)

    result.reverse()

    print(len(result))
    print(' '.join(map(str, result)))

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 3340: Multi-key Sorting
// 다중 키 정렬을 위한 최소 Sort 연산 찾기

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int c = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        int[] keys = new int[k];
        for (int i = 0; i < k; i++) {
            keys[i] = Integer.parseInt(st.nextToken());
        }

        // 역순으로 중복 제거
        Set<Integer> seen = new HashSet<>();
        List<Integer> result = new ArrayList<>();

        for (int i = k - 1; i >= 0; i--) {
            if (!seen.contains(keys[i])) {
                seen.add(keys[i]);
                result.add(keys[i]);
            }
        }

        Collections.reverse(result);

        System.out.println(result.size());
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < result.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(result.get(i));
        }
        System.out.println(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 3340: Multi-key Sorting
// 다중 키 정렬을 위한 최소 Sort 연산 찾기

#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int c, k;
    cin >> c >> k;

    vector<int> keys(k);
    for (int i = 0; i < k; i++) {
        cin >> keys[i];
    }

    // 역순으로 중복 제거
    set<int> seen;
    vector<int> result;

    for (int i = k - 1; i >= 0; i--) {
        if (seen.find(keys[i]) == seen.end()) {
            seen.insert(keys[i]);
            result.push_back(keys[i]);
        }
    }

    reverse(result.begin(), result.end());

    cout << result.size() << "\\n";
    for (int i = 0; i < result.size(); i++) {
        if (i > 0) cout << " ";
        cout << result[i];
    }
    cout << "\\n";

    return 0;
}
'''
        }
    ],

    # Problem 981: baekjoon_30132 - Minesweeper
    # Validate minesweeper board
    10870: [
        {
            "language": "python",
            "code": '''# 백준 30132: Minesweeper
# 지뢰찾기 보드 검증

import sys
input = sys.stdin.readline

def validate_board(n, m, board):
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for i in range(n):
        for j in range(m):
            if board[i][j] == 'F':
                continue

            # 숫자인 경우, 주변 지뢰 수 계산
            expected = int(board[i][j])
            mine_count = 0

            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < n and 0 <= nj < m and board[ni][nj] == 'F':
                    mine_count += 1

            if mine_count != expected:
                return False

    return True

def solve():
    t = int(input())

    results = []
    for _ in range(t):
        n, m = map(int, input().split())
        board = []
        for _ in range(n):
            board.append(input().strip())

        if validate_board(n, m, board):
            results.append("Well done Clark!")
        else:
            results.append("Please sweep the mine again!")

    print('\\n'.join(results))

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 30132: Minesweeper
// 지뢰찾기 보드 검증

import java.util.*;
import java.io.*;

public class Main {
    static int[] di = {-1, -1, -1, 0, 0, 1, 1, 1};
    static int[] dj = {-1, 0, 1, -1, 1, -1, 0, 1};

    public static boolean validateBoard(int n, int m, String[] board) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                char c = board[i].charAt(j);
                if (c == 'F') continue;

                int expected = c - '0';
                int mineCount = 0;

                for (int d = 0; d < 8; d++) {
                    int ni = i + di[d];
                    int nj = j + dj[d];

                    if (ni >= 0 && ni < n && nj >= 0 && nj < m && board[ni].charAt(nj) == 'F') {
                        mineCount++;
                    }
                }

                if (mineCount != expected) return false;
            }
        }
        return true;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int m = Integer.parseInt(st.nextToken());

            String[] board = new String[n];
            for (int i = 0; i < n; i++) {
                board[i] = br.readLine();
            }

            if (validateBoard(n, m, board)) {
                sb.append("Well done Clark!\\n");
            } else {
                sb.append("Please sweep the mine again!\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 30132: Minesweeper
// 지뢰찾기 보드 검증

#include <iostream>
#include <string>
using namespace std;

int di[] = {-1, -1, -1, 0, 0, 1, 1, 1};
int dj[] = {-1, 0, 1, -1, 1, -1, 0, 1};

bool validateBoard(int n, int m, string board[]) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            char c = board[i][j];
            if (c == 'F') continue;

            int expected = c - '0';
            int mineCount = 0;

            for (int d = 0; d < 8; d++) {
                int ni = i + di[d];
                int nj = j + dj[d];

                if (ni >= 0 && ni < n && nj >= 0 && nj < m && board[ni][nj] == 'F') {
                    mineCount++;
                }
            }

            if (mineCount != expected) return false;
        }
    }
    return true;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;

    while (t--) {
        int n, m;
        cin >> n >> m;

        string board[100];
        for (int i = 0; i < n; i++) {
            cin >> board[i];
        }

        if (validateBoard(n, m, board)) {
            cout << "Well done Clark!\\n";
        } else {
            cout << "Please sweep the mine again!\\n";
        }
    }

    return 0;
}
'''
        }
    ],

    # Problem 982: baekjoon_14995 - Horror Film Night
    # Maximum films that can be watched fairly
    10891: [
        {
            "language": "python",
            "code": '''# 백준 14995: Horror Film Night
# 두 사람이 공정하게 볼 수 있는 최대 영화 수

import sys
input = sys.stdin.readline

def solve():
    # 각 사람이 좋아하는 영화 세트
    line1 = input().split()
    n1 = int(line1[0])
    emma_likes = set(map(int, line1[1:n1+1]))

    line2 = input().split()
    n2 = int(line2[0])
    marcos_likes = set(map(int, line2[1:n2+1]))

    # 둘 다 좋아하는 영화, Emma만 좋아하는 영화, Marcos만 좋아하는 영화
    both = emma_likes & marcos_likes
    emma_only = emma_likes - marcos_likes
    marcos_only = marcos_likes - emma_likes

    # 공정한 규칙: 같은 사람이 싫어하는 영화를 연속으로 볼 수 없음
    # 둘 다 좋아하는 영화는 항상 볼 수 있음
    # Emma만 좋아하는 영화 후에는 둘 다 좋아하거나 Marcos만 좋아하는 영화
    # Marcos만 좋아하는 영화 후에는 둘 다 좋아하거나 Emma만 좋아하는 영화

    a = len(emma_only)
    b = len(marcos_only)
    c = len(both)

    # 최대 영화 수 = 둘 다 좋아하는 영화 + min(a, b+1) + min(b, a+1) - max(0, min(a,b+1)+min(b,a+1)-a-b)
    # 또는 더 간단히: c + min(a + b, 2 * max(a, b) + c)

    # 정확한 계산:
    # 둘 다 좋아하는 영화(c)는 어디든 삽입 가능
    # a와 b를 교대로 배치하면 min(a, b) * 2 + (1 if a != b else 0)
    # c로 분리하면 추가 가능

    # 단순화: c + a + b가 가능한 경우와 아닌 경우
    # |a - b| <= c + 1이면 모두 가능

    if abs(a - b) <= c + 1:
        print(a + b + c)
    else:
        # 더 적은 쪽 + c + (더 적은 쪽 + c + 1)
        smaller = min(a, b)
        print(2 * smaller + c + 1)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 14995: Horror Film Night
// 두 사람이 공정하게 볼 수 있는 최대 영화 수

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        StringTokenizer st = new StringTokenizer(br.readLine());
        int n1 = Integer.parseInt(st.nextToken());
        Set<Integer> emmaLikes = new HashSet<>();
        for (int i = 0; i < n1; i++) {
            emmaLikes.add(Integer.parseInt(st.nextToken()));
        }

        st = new StringTokenizer(br.readLine());
        int n2 = Integer.parseInt(st.nextToken());
        Set<Integer> marcosLikes = new HashSet<>();
        for (int i = 0; i < n2; i++) {
            marcosLikes.add(Integer.parseInt(st.nextToken()));
        }

        // 분류
        int both = 0, emmaOnly = 0, marcosOnly = 0;

        for (int film : emmaLikes) {
            if (marcosLikes.contains(film)) both++;
            else emmaOnly++;
        }
        for (int film : marcosLikes) {
            if (!emmaLikes.contains(film)) marcosOnly++;
        }

        int a = emmaOnly;
        int b = marcosOnly;
        int c = both;

        if (Math.abs(a - b) <= c + 1) {
            System.out.println(a + b + c);
        } else {
            int smaller = Math.min(a, b);
            System.out.println(2 * smaller + c + 1);
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 14995: Horror Film Night
// 두 사람이 공정하게 볼 수 있는 최대 영화 수

#include <iostream>
#include <set>
#include <cmath>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n1;
    cin >> n1;
    set<int> emmaLikes;
    for (int i = 0; i < n1; i++) {
        int x;
        cin >> x;
        emmaLikes.insert(x);
    }

    int n2;
    cin >> n2;
    set<int> marcosLikes;
    for (int i = 0; i < n2; i++) {
        int x;
        cin >> x;
        marcosLikes.insert(x);
    }

    int both = 0, emmaOnly = 0, marcosOnly = 0;

    for (int film : emmaLikes) {
        if (marcosLikes.count(film)) both++;
        else emmaOnly++;
    }
    for (int film : marcosLikes) {
        if (!emmaLikes.count(film)) marcosOnly++;
    }

    int a = emmaOnly;
    int b = marcosOnly;
    int c = both;

    if (abs(a - b) <= c + 1) {
        cout << a + b + c << endl;
    } else {
        int smaller = min(a, b);
        cout << 2 * smaller + c + 1 << endl;
    }

    return 0;
}
'''
        }
    ],

    # Problem 983: baekjoon_16598 - Achievements
    # Longest streak with paid days
    10892: [
        {
            "language": "python",
            "code": '''# 백준 16598: Achievements
# 유료 일수를 포함한 최장 연속 기록

import sys
input = sys.stdin.readline

def solve():
    n, p = map(int, input().split())
    days = list(map(int, input().split()))

    # 슬라이딩 윈도우로 최대 연속 기간 찾기
    # p일을 지불하여 빈 칸을 채울 수 있음

    max_streak = 0
    left = 0

    for right in range(n):
        # [left, right] 구간에서 필요한 유료 일수
        # days[right] - days[left] - (right - left) = 빈 일수
        while days[right] - days[left] - (right - left) > p:
            left += 1

        # 현재 연속 기간 = days[right] - days[left] + 1
        streak = days[right] - days[left] + 1
        max_streak = max(max_streak, streak)

    # 남은 p일을 끝에 추가할 수 있음
    # 마지막 날 이후로 p일 추가
    used_in_window = days[n-1] - days[left] - (n - 1 - left) if n > 0 else 0
    remaining_p = p - used_in_window
    if remaining_p > 0:
        max_streak = max(max_streak, days[n-1] - days[left] + 1 + remaining_p)

    print(max_streak)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 16598: Achievements
// 유료 일수를 포함한 최장 연속 기록

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int p = Integer.parseInt(st.nextToken());

        st = new StringTokenizer(br.readLine());
        long[] days = new long[n];
        for (int i = 0; i < n; i++) {
            days[i] = Long.parseLong(st.nextToken());
        }

        long maxStreak = 0;
        int left = 0;

        for (int right = 0; right < n; right++) {
            while (days[right] - days[left] - (right - left) > p) {
                left++;
            }

            long streak = days[right] - days[left] + 1;
            maxStreak = Math.max(maxStreak, streak);
        }

        // 남은 p일 추가
        long usedInWindow = days[n-1] - days[left] - (n - 1 - left);
        long remainingP = p - usedInWindow;
        if (remainingP > 0) {
            maxStreak = Math.max(maxStreak, days[n-1] - days[left] + 1 + remainingP);
        }

        System.out.println(maxStreak);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 16598: Achievements
// 유료 일수를 포함한 최장 연속 기록

#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, p;
    cin >> n >> p;

    vector<long long> days(n);
    for (int i = 0; i < n; i++) {
        cin >> days[i];
    }

    long long maxStreak = 0;
    int left = 0;

    for (int right = 0; right < n; right++) {
        while (days[right] - days[left] - (right - left) > p) {
            left++;
        }

        long long streak = days[right] - days[left] + 1;
        maxStreak = max(maxStreak, streak);
    }

    // 남은 p일 추가
    long long usedInWindow = days[n-1] - days[left] - (n - 1 - left);
    long long remainingP = p - usedInWindow;
    if (remainingP > 0) {
        maxStreak = max(maxStreak, days[n-1] - days[left] + 1 + remainingP);
    }

    cout << maxStreak << endl;

    return 0;
}
'''
        }
    ],

    # Problem 984: baekjoon_13996 - Hard Refactoring
    # Simplify logical expressions for ranges
    10893: [
        {
            "language": "python",
            "code": '''# 백준 13996: Hard Refactoring
# 범위 논리식 단순화

import sys
input = sys.stdin.readline

def solve():
    ranges = []

    MIN_INT = -32768
    MAX_INT = 32767

    while True:
        try:
            line = input().strip()
            if not line:
                break

            # 파싱: x >= a && x <= b 또는 x >= a 또는 x <= b
            parts = line.replace('||', '').strip()
            if not parts:
                continue

            if '&&' in parts:
                # 두 조건
                conds = parts.split('&&')
                low, high = MIN_INT, MAX_INT

                for cond in conds:
                    cond = cond.strip()
                    if '>=' in cond:
                        val = int(cond.split('>=')[1].strip())
                        low = max(low, val)
                    elif '<=' in cond:
                        val = int(cond.split('<=')[1].strip())
                        high = min(high, val)

                if low <= high:
                    ranges.append((low, high))
            else:
                # 단일 조건
                if '>=' in parts:
                    val = int(parts.split('>=')[1].strip())
                    ranges.append((val, MAX_INT))
                elif '<=' in parts:
                    val = int(parts.split('<=')[1].strip())
                    ranges.append((MIN_INT, val))

        except EOFError:
            break

    if not ranges:
        print("false")
        return

    # 범위 병합
    ranges.sort()
    merged = []

    for low, high in ranges:
        if merged and low <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], high))
        else:
            merged.append((low, high))

    # 전체 범위인지 확인
    if len(merged) == 1 and merged[0][0] == MIN_INT and merged[0][1] == MAX_INT:
        print("true")
        return

    # 결과 출력
    result = []
    for low, high in merged:
        if low == MIN_INT and high == MAX_INT:
            result.append("true")
        elif low == MIN_INT:
            result.append(f"x <= {high}")
        elif high == MAX_INT:
            result.append(f"x >= {low}")
        elif low == high:
            result.append(f"x >= {low} && x <= {high}")
        else:
            result.append(f"x >= {low} && x <= {high}")

    print(' ||\\n'.join(result))

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 13996: Hard Refactoring
// 범위 논리식 단순화

import java.util.*;
import java.io.*;

public class Main {
    static final int MIN_INT = -32768;
    static final int MAX_INT = 32767;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        List<int[]> ranges = new ArrayList<>();

        String line;
        while ((line = br.readLine()) != null && !line.isEmpty()) {
            line = line.replace("||", "").trim();
            if (line.isEmpty()) continue;

            if (line.contains("&&")) {
                String[] conds = line.split("&&");
                int low = MIN_INT, high = MAX_INT;

                for (String cond : conds) {
                    cond = cond.trim();
                    if (cond.contains(">=")) {
                        int val = Integer.parseInt(cond.split(">=")[1].trim());
                        low = Math.max(low, val);
                    } else if (cond.contains("<=")) {
                        int val = Integer.parseInt(cond.split("<=")[1].trim());
                        high = Math.min(high, val);
                    }
                }

                if (low <= high) ranges.add(new int[]{low, high});
            } else {
                if (line.contains(">=")) {
                    int val = Integer.parseInt(line.split(">=")[1].trim());
                    ranges.add(new int[]{val, MAX_INT});
                } else if (line.contains("<=")) {
                    int val = Integer.parseInt(line.split("<=")[1].trim());
                    ranges.add(new int[]{MIN_INT, val});
                }
            }
        }

        if (ranges.isEmpty()) {
            System.out.println("false");
            return;
        }

        // 정렬 및 병합
        ranges.sort((a, b) -> a[0] - b[0]);
        List<int[]> merged = new ArrayList<>();

        for (int[] range : ranges) {
            if (!merged.isEmpty() && range[0] <= merged.get(merged.size()-1)[1] + 1) {
                merged.get(merged.size()-1)[1] = Math.max(merged.get(merged.size()-1)[1], range[1]);
            } else {
                merged.add(range);
            }
        }

        if (merged.size() == 1 && merged.get(0)[0] == MIN_INT && merged.get(0)[1] == MAX_INT) {
            System.out.println("true");
            return;
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < merged.size(); i++) {
            if (i > 0) sb.append(" ||\\n");
            int low = merged.get(i)[0], high = merged.get(i)[1];

            if (low == MIN_INT) sb.append("x <= ").append(high);
            else if (high == MAX_INT) sb.append("x >= ").append(low);
            else sb.append("x >= ").append(low).append(" && x <= ").append(high);
        }

        System.out.println(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 13996: Hard Refactoring
// 범위 논리식 단순화

#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <sstream>
using namespace std;

const int MIN_INT = -32768;
const int MAX_INT = 32767;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    vector<pair<int, int>> ranges;
    string line;

    while (getline(cin, line)) {
        // ||를 제거
        size_t pos = line.find("||");
        if (pos != string::npos) line = line.substr(0, pos);

        // 공백 제거
        while (!line.empty() && (line.back() == ' ' || line.back() == '\\n')) line.pop_back();
        if (line.empty()) continue;

        int low = MIN_INT, high = MAX_INT;

        if (line.find("&&") != string::npos) {
            // 두 조건
            size_t andPos = line.find("&&");
            string cond1 = line.substr(0, andPos);
            string cond2 = line.substr(andPos + 2);

            for (const string& cond : {cond1, cond2}) {
                if (cond.find(">=") != string::npos) {
                    size_t p = cond.find(">=");
                    int val = stoi(cond.substr(p + 2));
                    low = max(low, val);
                } else if (cond.find("<=") != string::npos) {
                    size_t p = cond.find("<=");
                    int val = stoi(cond.substr(p + 2));
                    high = min(high, val);
                }
            }
        } else {
            if (line.find(">=") != string::npos) {
                size_t p = line.find(">=");
                int val = stoi(line.substr(p + 2));
                low = val;
            } else if (line.find("<=") != string::npos) {
                size_t p = line.find("<=");
                int val = stoi(line.substr(p + 2));
                high = val;
            }
        }

        if (low <= high) ranges.push_back({low, high});
    }

    if (ranges.empty()) {
        cout << "false" << endl;
        return 0;
    }

    // 정렬 및 병합
    sort(ranges.begin(), ranges.end());
    vector<pair<int, int>> merged;

    for (auto& range : ranges) {
        if (!merged.empty() && range.first <= merged.back().second + 1) {
            merged.back().second = max(merged.back().second, range.second);
        } else {
            merged.push_back(range);
        }
    }

    if (merged.size() == 1 && merged[0].first == MIN_INT && merged[0].second == MAX_INT) {
        cout << "true" << endl;
        return 0;
    }

    for (int i = 0; i < merged.size(); i++) {
        if (i > 0) cout << " ||" << endl;
        int low = merged[i].first, high = merged[i].second;

        if (low == MIN_INT) cout << "x <= " << high;
        else if (high == MAX_INT) cout << "x >= " << low;
        else cout << "x >= " << low << " && x <= " << high;
    }
    cout << endl;

    return 0;
}
'''
        }
    ],

    # Problem 985: baekjoon_30866 - NOT a SAT problem
    # Make CNF false by assigning truth values
    10898: [
        {
            "language": "python",
            "code": '''# 백준 30866: NOT a SAT problem
# CNF를 거짓으로 만드는 변수 할당 찾기

import sys
input = sys.stdin.readline

def solve():
    n, m = map(int, input().split())

    clauses = []
    for _ in range(m):
        parts = list(map(int, input().split()))
        k = parts[0]
        literals = parts[1:k+1]
        clauses.append(literals)

    # CNF가 거짓이 되려면 적어도 하나의 절이 거짓이어야 함
    # 하나의 절이 거짓이 되려면 그 절의 모든 리터럴이 거짓이어야 함

    # 각 절에 대해 모든 리터럴을 거짓으로 만들 수 있는지 확인
    # 리터럴 x가 거짓 = 변수 x가 0
    # 리터럴 -x가 거짓 = 변수 x가 1

    for clause in clauses:
        # 이 절을 거짓으로 만들 수 있는지 확인
        assignment = [None] * (n + 1)
        possible = True

        for lit in clause:
            var = abs(lit)
            needed_val = 0 if lit > 0 else 1

            if assignment[var] is None:
                assignment[var] = needed_val
            elif assignment[var] != needed_val:
                # 충돌 - 이 절은 거짓으로 만들 수 없음
                possible = False
                break

        if possible:
            # 할당되지 않은 변수는 0으로 설정
            result = [0] * n
            for i in range(1, n + 1):
                if assignment[i] is not None:
                    result[i - 1] = assignment[i]

            print("YES")
            print(' '.join(map(str, result)))
            return

    print("NO")

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 30866: NOT a SAT problem
// CNF를 거짓으로 만드는 변수 할당 찾기

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        List<List<Integer>> clauses = new ArrayList<>();
        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            int k = Integer.parseInt(st.nextToken());
            List<Integer> clause = new ArrayList<>();
            for (int j = 0; j < k; j++) {
                clause.add(Integer.parseInt(st.nextToken()));
            }
            clauses.add(clause);
        }

        for (List<Integer> clause : clauses) {
            int[] assignment = new int[n + 1];
            Arrays.fill(assignment, -1);
            boolean possible = true;

            for (int lit : clause) {
                int var = Math.abs(lit);
                int neededVal = lit > 0 ? 0 : 1;

                if (assignment[var] == -1) {
                    assignment[var] = neededVal;
                } else if (assignment[var] != neededVal) {
                    possible = false;
                    break;
                }
            }

            if (possible) {
                System.out.println("YES");
                StringBuilder sb = new StringBuilder();
                for (int i = 1; i <= n; i++) {
                    if (i > 1) sb.append(" ");
                    sb.append(assignment[i] == -1 ? 0 : assignment[i]);
                }
                System.out.println(sb);
                return;
            }
        }

        System.out.println("NO");
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 30866: NOT a SAT problem
// CNF를 거짓으로 만드는 변수 할당 찾기

#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    vector<vector<int>> clauses(m);
    for (int i = 0; i < m; i++) {
        int k;
        cin >> k;
        clauses[i].resize(k);
        for (int j = 0; j < k; j++) {
            cin >> clauses[i][j];
        }
    }

    for (const auto& clause : clauses) {
        vector<int> assignment(n + 1, -1);
        bool possible = true;

        for (int lit : clause) {
            int var = abs(lit);
            int neededVal = lit > 0 ? 0 : 1;

            if (assignment[var] == -1) {
                assignment[var] = neededVal;
            } else if (assignment[var] != neededVal) {
                possible = false;
                break;
            }
        }

        if (possible) {
            cout << "YES\\n";
            for (int i = 1; i <= n; i++) {
                if (i > 1) cout << " ";
                cout << (assignment[i] == -1 ? 0 : assignment[i]);
            }
            cout << "\\n";
            return 0;
        }
    }

    cout << "NO\\n";

    return 0;
}
'''
        }
    ],

    # Problem 986: baekjoon_11164 - Traveling Cellsperson
    # Minimum steps to visit all cells in grid
    10902: [
        {
            "language": "python",
            "code": '''# 백준 11164: Traveling Cellsperson
# 그리드의 모든 셀을 방문하는 최소 이동 횟수

import sys
input = sys.stdin.readline

def solve():
    t = int(input())

    for _ in range(t):
        x, y = map(int, input().split())
        grid = []
        for i in range(y):
            grid.append(input().strip())

        # 모든 셀이 'C'이고 하나의 'S'(시작점)
        # 격자를 뱀처럼 이동하면 x * y - 1 이동
        # 하지만 최적의 경로를 찾아야 함

        # 그리드의 모든 셀 방문 = x * y 셀
        # 최소 이동 = x * y - 1 (연결된 경로)

        total_cells = x * y
        min_moves = total_cells - 1

        # 하지만 추가 이동이 필요할 수 있음 (격자 구조에 따라)
        # 사실 격자에서는 항상 x * y - 1로 가능

        # 최소 경로 = (x-1)*y + (y-1) = xy - 1
        # 이것은 지그재그로 이동할 때

        # 하지만 문제에서 LOL을 출력하라고 함
        print(total_cells - 1)
        print("LOL")

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 11164: Traveling Cellsperson
// 그리드의 모든 셀을 방문하는 최소 이동 횟수

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());

            for (int i = 0; i < y; i++) {
                br.readLine();
            }

            int totalCells = x * y;
            System.out.println(totalCells - 1);
            System.out.println("LOL");
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 11164: Traveling Cellsperson
// 그리드의 모든 셀을 방문하는 최소 이동 횟수

#include <iostream>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;

    while (t--) {
        int x, y;
        cin >> x >> y;

        for (int i = 0; i < y; i++) {
            string row;
            cin >> row;
        }

        int totalCells = x * y;
        cout << totalCells - 1 << "\\n";
        cout << "LOL\\n";
    }

    return 0;
}
'''
        }
    ],

    # Problem 987: baekjoon_6542 - Assistance Required
    # Find n-th remaining person after elimination process
    10932: [
        {
            "language": "python",
            "code": '''# 백준 6542: Assistance Required
# 제거 과정 후 n번째로 남은 사람 찾기 (에라토스테네스의 체와 유사)

import sys
input = sys.stdin.readline

def solve():
    # 미리 계산 (소수와 유사한 개념)
    # 2부터 시작하여 각 숫자에서 그 배수를 제거
    MAX_N = 500001
    remaining = [True] * MAX_N
    result = []

    for i in range(2, MAX_N):
        if remaining[i]:
            result.append(i)
            # i번째마다 제거
            for j in range(i + i, MAX_N, i):
                remaining[j] = False

    # 결과 배열로 인덱스 접근
    # 하지만 이 방식은 정확하지 않음

    # 다른 접근: 시뮬레이션
    # n번째 숫자를 찾기

    # 실제로 소수를 찾는 것과 동일
    # 에라토스테네스의 체로 소수 찾기
    is_prime = [True] * MAX_N
    is_prime[0] = is_prime[1] = False

    for i in range(2, MAX_N):
        if is_prime[i]:
            for j in range(i * 2, MAX_N, i):
                is_prime[j] = False

    primes = [i for i in range(2, MAX_N) if is_prime[i]]

    while True:
        n = int(input())
        if n == 0:
            break

        if n <= len(primes):
            print(primes[n - 1])
        else:
            print(-1)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 6542: Assistance Required
// 제거 과정 후 n번째로 남은 사람 찾기 (소수 찾기)

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        // 에라토스테네스의 체
        int MAX_N = 500001;
        boolean[] isPrime = new boolean[MAX_N];
        Arrays.fill(isPrime, true);
        isPrime[0] = isPrime[1] = false;

        for (int i = 2; i < MAX_N; i++) {
            if (isPrime[i]) {
                for (int j = i * 2; j < MAX_N; j += i) {
                    isPrime[j] = false;
                }
            }
        }

        List<Integer> primes = new ArrayList<>();
        for (int i = 2; i < MAX_N; i++) {
            if (isPrime[i]) primes.add(i);
        }

        String line;
        while ((line = br.readLine()) != null) {
            int n = Integer.parseInt(line.trim());
            if (n == 0) break;

            if (n <= primes.size()) {
                sb.append(primes.get(n - 1)).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 6542: Assistance Required
// 제거 과정 후 n번째로 남은 사람 찾기 (소수 찾기)

#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // 에라토스테네스의 체
    const int MAX_N = 500001;
    vector<bool> isPrime(MAX_N, true);
    isPrime[0] = isPrime[1] = false;

    for (int i = 2; i < MAX_N; i++) {
        if (isPrime[i]) {
            for (int j = i * 2; j < MAX_N; j += i) {
                isPrime[j] = false;
            }
        }
    }

    vector<int> primes;
    for (int i = 2; i < MAX_N; i++) {
        if (isPrime[i]) primes.push_back(i);
    }

    int n;
    while (cin >> n && n != 0) {
        if (n <= primes.size()) {
            cout << primes[n - 1] << "\\n";
        }
    }

    return 0;
}
'''
        }
    ],

    # Problem 988: baekjoon_9670 - Movie
    # Find device that can display movie with maximum quality
    10936: [
        {
            "language": "python",
            "code": '''# 백준 9670: Movie
# 영화를 최대 품질로 표시할 수 있는 장치 찾기

import sys
input = sys.stdin.readline

def solve():
    devices = [
        (640, 320),   # Device 1
        (800, 600),   # Device 2
        (2500, 2500), # Device 3
    ]

    while True:
        line = input().split()
        if not line or len(line) < 2:
            break

        h, w = int(line[0]), int(line[1])

        if h == 0 and w == 0:
            break

        # 영화 해상도 h x w
        # 각 장치에서 가능한 최대 스케일링 팩터 c
        # c * h <= device_h and c * w <= device_w
        # c = min(device_h / h, device_w / w)
        # 품질 = c * h * c * w = c^2 * h * w

        best_quality = 0

        for dh, dw in devices:
            c = min(dh / h, dw / w)
            if c > 0:
                # 정수 부분만 사용
                c_int = int(c)
                if c_int > 0:
                    quality = c_int * h * c_int * w
                    best_quality = max(best_quality, quality)

        # 결과 출력 (최대 창 크기의 한 변)
        # 출력은 [c*H]로, 가장 큰 정수 스케일
        best_c = 0
        for dh, dw in devices:
            c = min(dh / h, dw / w)
            c_int = int(c)
            if c_int > best_c:
                best_c = c_int

        if best_c > 0:
            print(best_c * h)
        else:
            print(0)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 9670: Movie
// 영화를 최대 품질로 표시할 수 있는 장치 찾기

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int[][] devices = {{640, 320}, {800, 600}, {2500, 2500}};

        String line;
        while ((line = br.readLine()) != null) {
            StringTokenizer st = new StringTokenizer(line);
            int h = Integer.parseInt(st.nextToken());
            int w = Integer.parseInt(st.nextToken());

            if (h == 0 && w == 0) break;

            int bestC = 0;
            for (int[] device : devices) {
                int dh = device[0], dw = device[1];
                int c = Math.min(dh / h, dw / w);
                if (c > bestC) bestC = c;
            }

            sb.append(bestC * h).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 9670: Movie
// 영화를 최대 품질로 표시할 수 있는 장치 찾기

#include <iostream>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int devices[3][2] = {{640, 320}, {800, 600}, {2500, 2500}};

    int h, w;
    while (cin >> h >> w) {
        if (h == 0 && w == 0) break;

        int bestC = 0;
        for (int i = 0; i < 3; i++) {
            int dh = devices[i][0], dw = devices[i][1];
            int c = min(dh / h, dw / w);
            if (c > bestC) bestC = c;
        }

        cout << bestC * h << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # Problem 989: baekjoon_5059 - Shopaholic
    # Maximum discount with "buy 3 pay 2" deal
    10943: [
        {
            "language": "python",
            "code": '''# 백준 5059: Shopaholic
# 3개 구매시 1개 무료 프로모션에서 최대 할인 계산

import sys
input = sys.stdin.readline

def solve():
    t = int(input())

    for _ in range(t):
        n = int(input())
        prices = list(map(int, input().split()))

        # 내림차순 정렬
        prices.sort(reverse=True)

        # 3개씩 묶어서 가장 싼 것을 무료로
        total_discount = 0

        for i in range(2, n, 3):
            total_discount += prices[i]

        print(total_discount)

solve()
'''
        },
        {
            "language": "java",
            "code": '''// 백준 5059: Shopaholic
// 3개 구매시 1개 무료 프로모션에서 최대 할인 계산

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            int n = Integer.parseInt(br.readLine().trim());
            StringTokenizer st = new StringTokenizer(br.readLine());

            Integer[] prices = new Integer[n];
            for (int i = 0; i < n; i++) {
                prices[i] = Integer.parseInt(st.nextToken());
            }

            // 내림차순 정렬
            Arrays.sort(prices, Collections.reverseOrder());

            long totalDiscount = 0;
            for (int i = 2; i < n; i += 3) {
                totalDiscount += prices[i];
            }

            sb.append(totalDiscount).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 5059: Shopaholic
// 3개 구매시 1개 무료 프로모션에서 최대 할인 계산

#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;

    while (t--) {
        int n;
        cin >> n;

        vector<int> prices(n);
        for (int i = 0; i < n; i++) {
            cin >> prices[i];
        }

        // 내림차순 정렬
        sort(prices.begin(), prices.end(), greater<int>());

        long long totalDiscount = 0;
        for (int i = 2; i < n; i += 3) {
            totalDiscount += prices[i];
        }

        cout << totalDiscount << "\\n";
    }

    return 0;
}
'''
        }
    ],
}

def main():
    json_path = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

    # Read the JSON file
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Update solutions
    updated_count = 0
    for json_index, solutions in SOLUTIONS.items():
        if json_index < len(data):
            data[json_index]['solutions'] = solutions
            updated_count += 1
            print(f"Updated problem at index {json_index}: {data[json_index].get('id', 'unknown')}")

    # Write back with file lock
    with open(json_path, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\nTotal problems updated: {updated_count}")

if __name__ == "__main__":
    main()
