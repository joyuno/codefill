#!/usr/bin/env python3
"""
Baekjoon 문제 540-569 (empty medium) 솔루션 추가 스크립트 v2
"""

import json
import fcntl

def get_all_solutions():
    """모든 문제에 대한 솔루션 반환"""
    solutions = {}

    # 7176: Falling Apples - 사과 떨어뜨리기
    solutions[7176] = [
        {"language": "python", "code": '''# Falling Apples - 사과 떨어뜨리기 시뮬레이션
import sys
input = sys.stdin.readline

n = int(input())
grid = []
for _ in range(n):
    grid.append(list(input().strip()))

# 각 열에서 사과를 아래로 떨어뜨림
for col in range(len(grid[0])):
    # 해당 열의 사과 개수 세기
    apples = 0
    for row in range(n):
        if grid[row][col] == 'a':
            apples += 1
            grid[row][col] = '.'

    # 아래에서부터 사과 배치
    row = n - 1
    while apples > 0 and row >= 0:
        if grid[row][col] == '.':
            grid[row][col] = 'a'
            apples -= 1
        row -= 1

for row in grid:
    print(''.join(row))
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    // Falling Apples - 사과 떨어뜨리기 시뮬레이션
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        char[][] grid = new char[n][];
        for (int i = 0; i < n; i++) {
            grid[i] = br.readLine().toCharArray();
        }

        int cols = grid[0].length;
        for (int col = 0; col < cols; col++) {
            int apples = 0;
            for (int row = 0; row < n; row++) {
                if (grid[row][col] == 'a') {
                    apples++;
                    grid[row][col] = '.';
                }
            }
            int row = n - 1;
            while (apples > 0 && row >= 0) {
                if (grid[row][col] == '.') {
                    grid[row][col] = 'a';
                    apples--;
                }
                row--;
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append(new String(grid[i])).append("\\n");
        }
        System.out.print(sb);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <vector>
#include <string>
using namespace std;

// Falling Apples - 사과 떨어뜨리기 시뮬레이션
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<string> grid(n);
    for (int i = 0; i < n; i++) cin >> grid[i];

    int cols = grid[0].length();
    for (int col = 0; col < cols; col++) {
        int apples = 0;
        for (int row = 0; row < n; row++) {
            if (grid[row][col] == 'a') {
                apples++;
                grid[row][col] = '.';
            }
        }
        int row = n - 1;
        while (apples > 0 && row >= 0) {
            if (grid[row][col] == '.') {
                grid[row][col] = 'a';
                apples--;
            }
            row--;
        }
    }

    for (int i = 0; i < n; i++) cout << grid[i] << "\\n";
    return 0;
}
'''}
    ]

    # 7190: std::shared_ptr - 참조 카운팅
    solutions[7190] = [
        {"language": "python", "code": '''# std::shared_ptr - 참조 카운팅 시뮬레이션
import sys
input = sys.stdin.readline

n, q = map(int, input().split())
ptr = [0] * (n + 1)  # 포인터가 가리키는 객체
ref_count = {}  # 객체의 참조 카운트

for _ in range(q):
    query = input().split()
    cmd = query[0]

    if cmd == "make":
        i, x = int(query[1]), int(query[2])
        if ptr[i] > 0:
            ref_count[ptr[i]] -= 1
            if ref_count[ptr[i]] == 0:
                del ref_count[ptr[i]]
        ptr[i] = x
        ref_count[x] = ref_count.get(x, 0) + 1

    elif cmd == "copy":
        i, j = int(query[1]), int(query[2])
        if ptr[i] > 0:
            ref_count[ptr[i]] -= 1
            if ref_count[ptr[i]] == 0:
                del ref_count[ptr[i]]
        ptr[i] = ptr[j]
        if ptr[i] > 0:
            ref_count[ptr[i]] = ref_count.get(ptr[i], 0) + 1

    elif cmd == "reset":
        i = int(query[1])
        if ptr[i] > 0:
            ref_count[ptr[i]] -= 1
            if ref_count[ptr[i]] == 0:
                del ref_count[ptr[i]]
        ptr[i] = 0

    elif cmd == "count":
        i = int(query[1])
        print(0 if ptr[i] == 0 else ref_count.get(ptr[i], 0))

print(len(ref_count))
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int q = Integer.parseInt(st.nextToken());

        int[] ptr = new int[n + 1];
        Map<Integer, Integer> refCount = new HashMap<>();
        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < q; i++) {
            st = new StringTokenizer(br.readLine());
            String cmd = st.nextToken();

            if (cmd.equals("make")) {
                int idx = Integer.parseInt(st.nextToken());
                int x = Integer.parseInt(st.nextToken());
                if (ptr[idx] > 0) {
                    refCount.put(ptr[idx], refCount.get(ptr[idx]) - 1);
                    if (refCount.get(ptr[idx]) == 0) refCount.remove(ptr[idx]);
                }
                ptr[idx] = x;
                refCount.put(x, refCount.getOrDefault(x, 0) + 1);
            } else if (cmd.equals("copy")) {
                int i1 = Integer.parseInt(st.nextToken());
                int j = Integer.parseInt(st.nextToken());
                if (ptr[i1] > 0) {
                    refCount.put(ptr[i1], refCount.get(ptr[i1]) - 1);
                    if (refCount.get(ptr[i1]) == 0) refCount.remove(ptr[i1]);
                }
                ptr[i1] = ptr[j];
                if (ptr[i1] > 0) refCount.put(ptr[i1], refCount.getOrDefault(ptr[i1], 0) + 1);
            } else if (cmd.equals("reset")) {
                int idx = Integer.parseInt(st.nextToken());
                if (ptr[idx] > 0) {
                    refCount.put(ptr[idx], refCount.get(ptr[idx]) - 1);
                    if (refCount.get(ptr[idx]) == 0) refCount.remove(ptr[idx]);
                }
                ptr[idx] = 0;
            } else {
                int idx = Integer.parseInt(st.nextToken());
                sb.append(ptr[idx] == 0 ? 0 : refCount.getOrDefault(ptr[idx], 0)).append("\\n");
            }
        }
        sb.append(refCount.size());
        System.out.println(sb);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <unordered_map>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;

    vector<int> ptr(n + 1, 0);
    unordered_map<int, int> refCount;

    for (int i = 0; i < q; i++) {
        string cmd;
        cin >> cmd;

        if (cmd == "make") {
            int idx, x;
            cin >> idx >> x;
            if (ptr[idx] > 0) {
                refCount[ptr[idx]]--;
                if (refCount[ptr[idx]] == 0) refCount.erase(ptr[idx]);
            }
            ptr[idx] = x;
            refCount[x]++;
        } else if (cmd == "copy") {
            int i1, j;
            cin >> i1 >> j;
            if (ptr[i1] > 0) {
                refCount[ptr[i1]]--;
                if (refCount[ptr[i1]] == 0) refCount.erase(ptr[i1]);
            }
            ptr[i1] = ptr[j];
            if (ptr[i1] > 0) refCount[ptr[i1]]++;
        } else if (cmd == "reset") {
            int idx;
            cin >> idx;
            if (ptr[idx] > 0) {
                refCount[ptr[idx]]--;
                if (refCount[ptr[idx]] == 0) refCount.erase(ptr[idx]);
            }
            ptr[idx] = 0;
        } else {
            int idx;
            cin >> idx;
            cout << (ptr[idx] == 0 ? 0 : refCount[ptr[idx]]) << "\\n";
        }
    }
    cout << refCount.size() << endl;
    return 0;
}
'''}
    ]

    # 7200: Bovine Genomics (Silver) - DNA 비교
    solutions[7200] = [
        {"language": "python", "code": '''# Bovine Genomics (Silver) - DNA 위치 찾기
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
spotted = [input().strip() for _ in range(n)]
plain = [input().strip() for _ in range(n)]

count = 0
for pos in range(m):
    spotted_chars = set(dna[pos] for dna in spotted)
    plain_chars = set(dna[pos] for dna in plain)
    if spotted_chars.isdisjoint(plain_chars):
        count += 1

print(count)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        String[] spotted = new String[n];
        String[] plain = new String[n];
        for (int i = 0; i < n; i++) spotted[i] = br.readLine().trim();
        for (int i = 0; i < n; i++) plain[i] = br.readLine().trim();

        int count = 0;
        for (int pos = 0; pos < m; pos++) {
            Set<Character> s1 = new HashSet<>(), s2 = new HashSet<>();
            for (int i = 0; i < n; i++) {
                s1.add(spotted[i].charAt(pos));
                s2.add(plain[i].charAt(pos));
            }
            boolean disjoint = true;
            for (char c : s1) if (s2.contains(c)) { disjoint = false; break; }
            if (disjoint) count++;
        }
        System.out.println(count);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <vector>
#include <set>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    vector<string> spotted(n), plain(n);
    for (int i = 0; i < n; i++) cin >> spotted[i];
    for (int i = 0; i < n; i++) cin >> plain[i];

    int count = 0;
    for (int pos = 0; pos < m; pos++) {
        set<char> s1, s2;
        for (int i = 0; i < n; i++) {
            s1.insert(spotted[i][pos]);
            s2.insert(plain[i][pos]);
        }
        bool disjoint = true;
        for (char c : s1) if (s2.count(c)) { disjoint = false; break; }
        if (disjoint) count++;
    }
    cout << count << endl;
    return 0;
}
'''}
    ]

    # 7204: 숫자 POP
    solutions[7204] = [
        {"language": "python", "code": '''# 숫자 POP - 단조 증가 수열
import sys
input = sys.stdin.readline

n = int(input())
arr = list(map(int, input().split()))

stack = []
for num in arr:
    while stack and stack[-1] > num:
        stack.pop()
    stack.append(num)

print(' '.join(map(str, stack)))
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        ArrayList<Integer> stack = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            int num = Integer.parseInt(st.nextToken());
            while (!stack.isEmpty() && stack.get(stack.size()-1) > num) stack.remove(stack.size()-1);
            stack.add(num);
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < stack.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(stack.get(i));
        }
        System.out.println(sb);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> result;
    for (int i = 0; i < n; i++) {
        int num;
        cin >> num;
        while (!result.empty() && result.back() > num) result.pop_back();
        result.push_back(num);
    }

    for (int i = 0; i < (int)result.size(); i++) {
        if (i > 0) cout << " ";
        cout << result[i];
    }
    cout << endl;
    return 0;
}
'''}
    ]

    # 7208: 도청 장치 - 시저 암호
    solutions[7208] = [
        {"language": "python", "code": '''# 도청 장치 - 시저 암호 해독
import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    k = int(input())
    s = input().strip()

    result = []
    for c in s:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result.append(chr((ord(c) - base - k) % 26 + base))
        else:
            result.append(c)

    print(''.join(result))
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        for (int tc = 0; tc < t; tc++) {
            int k = Integer.parseInt(br.readLine().trim());
            String s = br.readLine();

            for (char c : s.toCharArray()) {
                if (Character.isLetter(c)) {
                    char base = Character.isUpperCase(c) ? 'A' : 'a';
                    sb.append((char)((c - base - k % 26 + 26) % 26 + base));
                } else {
                    sb.append(c);
                }
            }
            sb.append("\\n");
        }
        System.out.print(sb);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;

    while (t--) {
        int k;
        cin >> k;
        cin.ignore();

        string s;
        getline(cin, s);

        for (char& c : s) {
            if (isalpha(c)) {
                char base = isupper(c) ? 'A' : 'a';
                c = (c - base - k % 26 + 26) % 26 + base;
            }
        }
        cout << s << "\\n";
    }
    return 0;
}
'''}
    ]

    # 7217: Farmer John's Cheese Block
    solutions[7217] = [
        {"language": "python", "code": '''# Farmer John's Cheese Block - 치즈 블록
import sys
input = sys.stdin.readline

n = int(input())
queries = []
max_x, max_y, max_z = 0, 0, 0

for _ in range(n):
    x, y, z = map(int, input().split())
    queries.append((x, y, z))
    max_x = max(max_x, x)
    max_y = max(max_y, y)
    max_z = max(max_z, z)

total = max_x * max_y * max_z
eaten = set()

for x, y, z in queries:
    if (x, y, z) not in eaten:
        eaten.add((x, y, z))
        total -= 1
    print(total)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[][] q = new int[n][3];
        int mx = 0, my = 0, mz = 0;

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            q[i][0] = Integer.parseInt(st.nextToken());
            q[i][1] = Integer.parseInt(st.nextToken());
            q[i][2] = Integer.parseInt(st.nextToken());
            mx = Math.max(mx, q[i][0]);
            my = Math.max(my, q[i][1]);
            mz = Math.max(mz, q[i][2]);
        }

        long total = (long)mx * my * mz;
        Set<String> eaten = new HashSet<>();
        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < n; i++) {
            String key = q[i][0] + "," + q[i][1] + "," + q[i][2];
            if (!eaten.contains(key)) {
                eaten.add(key);
                total--;
            }
            sb.append(total).append("\\n");
        }
        System.out.print(sb);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <set>
#include <tuple>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<tuple<int,int,int>> q(n);
    int mx = 0, my = 0, mz = 0;

    for (int i = 0; i < n; i++) {
        int x, y, z;
        cin >> x >> y >> z;
        q[i] = {x, y, z};
        mx = max(mx, x);
        my = max(my, y);
        mz = max(mz, z);
    }

    long long total = (long long)mx * my * mz;
    set<tuple<int,int,int>> eaten;

    for (int i = 0; i < n; i++) {
        if (eaten.find(q[i]) == eaten.end()) {
            eaten.insert(q[i]);
            total--;
        }
        cout << total << "\\n";
    }
    return 0;
}
'''}
    ]

    # 7229: 반복수
    solutions[7229] = [
        {"language": "python", "code": '''# 반복수 - 연속 같은 숫자
import sys
input = sys.stdin.readline

n = int(input())
count = 0
num = 1

while count < n:
    num += 1
    s = str(num)
    for i in range(len(s) - 1):
        if s[i] == s[i+1]:
            count += 1
            break

print(num)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int count = 0, num = 1;
        while (count < n) {
            num++;
            String s = String.valueOf(num);
            for (int i = 0; i < s.length() - 1; i++) {
                if (s.charAt(i) == s.charAt(i + 1)) {
                    count++;
                    break;
                }
            }
        }
        System.out.println(num);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    int count = 0, num = 1;
    while (count < n) {
        num++;
        string s = to_string(num);
        for (int i = 0; i < (int)s.length() - 1; i++) {
            if (s[i] == s[i + 1]) {
                count++;
                break;
            }
        }
    }
    cout << num << endl;
    return 0;
}
'''}
    ]

    # 7230: 평점 변환 2
    solutions[7230] = [
        {"language": "python", "code": '''# 평점 변환 2
import sys
input = sys.stdin.readline

n = int(input())
grades = list(map(float, input().split()))

total = sum((g / 4.3) * 4.5 for g in grades)
print(f"{total / n:.2f}")
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        double sum = 0;
        for (int i = 0; i < n; i++) {
            double g = Double.parseDouble(st.nextToken());
            sum += (g / 4.3) * 4.5;
        }
        System.out.printf("%.2f%n", sum / n);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <iomanip>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    double sum = 0;
    for (int i = 0; i < n; i++) {
        double g;
        cin >> g;
        sum += (g / 4.3) * 4.5;
    }
    cout << fixed << setprecision(2) << sum / n << endl;
    return 0;
}
'''}
    ]

    # 7231: Paths on a Grid
    solutions[7231] = [
        {"language": "python", "code": '''# Paths on a Grid - 격자 경로
from math import comb
import sys
input = sys.stdin.readline

while True:
    line = input().split()
    n, m = int(line[0]), int(line[1])
    if n == 0 and m == 0:
        break
    print(comb(n + m, n))
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;
import java.math.BigInteger;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        while (true) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int m = Integer.parseInt(st.nextToken());
            if (n == 0 && m == 0) break;

            int r = Math.min(n, m);
            BigInteger result = BigInteger.ONE;
            for (int i = 0; i < r; i++) {
                result = result.multiply(BigInteger.valueOf(n + m - i));
                result = result.divide(BigInteger.valueOf(i + 1));
            }
            sb.append(result).append("\\n");
        }
        System.out.print(sb);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    while (cin >> n >> m && (n || m)) {
        int r = min(n, m);
        unsigned long long result = 1;
        for (int i = 0; i < r; i++) {
            result = result * (n + m - i) / (i + 1);
        }
        cout << result << "\\n";
    }
    return 0;
}
'''}
    ]

    # 7249: Game of Lines
    solutions[7249] = [
        {"language": "python", "code": '''# Game of Lines - 서로 다른 기울기
from math import gcd
import sys
input = sys.stdin.readline

n = int(input())
points = [tuple(map(int, input().split())) for _ in range(n)]

slopes = set()
for i in range(n):
    for j in range(i + 1, n):
        dx = points[j][0] - points[i][0]
        dy = points[j][1] - points[i][1]

        if dx == 0:
            slope = (0, 1)
        elif dy == 0:
            slope = (1, 0)
        else:
            g = gcd(abs(dx), abs(dy))
            dx, dy = dx // g, dy // g
            if dx < 0:
                dx, dy = -dx, -dy
            slope = (dy, dx)

        slopes.add(slope)

print(len(slopes))
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        int[][] p = new int[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            p[i][0] = Integer.parseInt(st.nextToken());
            p[i][1] = Integer.parseInt(st.nextToken());
        }

        Set<String> slopes = new HashSet<>();
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                int dx = p[j][0] - p[i][0];
                int dy = p[j][1] - p[i][1];

                String slope;
                if (dx == 0) slope = "0,1";
                else if (dy == 0) slope = "1,0";
                else {
                    int g = gcd(Math.abs(dx), Math.abs(dy));
                    dx /= g; dy /= g;
                    if (dx < 0) { dx = -dx; dy = -dy; }
                    slope = dy + "," + dx;
                }
                slopes.add(slope);
            }
        }
        System.out.println(slopes.size());
    }

    static int gcd(int a, int b) {
        while (b != 0) { int t = b; b = a % b; a = t; }
        return a;
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <set>
#include <cmath>
using namespace std;

int gcd(int a, int b) {
    while (b) { int t = b; b = a % b; a = t; }
    return a;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<pair<int, int>> p(n);
    for (int i = 0; i < n; i++) cin >> p[i].first >> p[i].second;

    set<pair<int, int>> slopes;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            int dx = p[j].first - p[i].first;
            int dy = p[j].second - p[i].second;

            pair<int, int> slope;
            if (dx == 0) slope = {0, 1};
            else if (dy == 0) slope = {1, 0};
            else {
                int g = gcd(abs(dx), abs(dy));
                dx /= g; dy /= g;
                if (dx < 0) { dx = -dx; dy = -dy; }
                slope = {dy, dx};
            }
            slopes.insert(slope);
        }
    }
    cout << slopes.size() << endl;
    return 0;
}
'''}
    ]

    # 7250: Down the Pyramid
    solutions[7250] = [
        {"language": "python", "code": '''# Down the Pyramid - 피라미드
import sys
input = sys.stdin.readline

n = int(input())
bottom = list(map(int, input().split()))

if n == 1:
    print(bottom[0] + 1)
else:
    # 첫 번째 원소 x를 변화시키면 다른 값들이 결정됨
    # 계수 계산
    coeff = [0] * n
    const = bottom[:]
    coeff[0] = 1

    min_x, max_x = 0, 10**18

    for level in range(n, 1, -1):
        new_coeff = [0] * (level - 1)
        new_const = [0] * (level - 1)
        for i in range(level - 1):
            new_coeff[i] = coeff[i] - coeff[i + 1]
            new_const[i] = const[i] - const[i + 1]

            # coeff[i] * x + const[i] >= 0
            c, d = new_coeff[i], new_const[i]
            if c > 0:
                min_x = max(min_x, max(0, (-d + c - 1) // c) if d < 0 else 0)
            elif c < 0:
                max_x = min(max_x, -d // (-c) if d <= 0 else -1)
            elif d < 0:
                max_x = -1
        coeff = new_coeff
        const = new_const

    print(max(0, max_x - min_x + 1) if min_x <= max_x else 0)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        long[] bottom = new long[n];
        for (int i = 0; i < n; i++) bottom[i] = Long.parseLong(st.nextToken());

        if (n == 1) {
            System.out.println(bottom[0] + 1);
            return;
        }

        long[] coeff = new long[n];
        long[] cst = bottom.clone();
        coeff[0] = 1;

        long minX = 0, maxX = (long)1e18;

        for (int level = n; level > 1; level--) {
            long[] nc = new long[level - 1];
            long[] ns = new long[level - 1];
            for (int i = 0; i < level - 1; i++) {
                nc[i] = coeff[i] - coeff[i + 1];
                ns[i] = cst[i] - cst[i + 1];

                if (nc[i] > 0) {
                    minX = Math.max(minX, ns[i] < 0 ? (-ns[i] + nc[i] - 1) / nc[i] : 0);
                } else if (nc[i] < 0) {
                    maxX = Math.min(maxX, ns[i] <= 0 ? -ns[i] / (-nc[i]) : -1);
                } else if (ns[i] < 0) {
                    maxX = -1;
                }
            }
            coeff = nc;
            cst = ns;
        }

        System.out.println(minX <= maxX ? maxX - minX + 1 : 0);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<long long> bottom(n);
    for (int i = 0; i < n; i++) cin >> bottom[i];

    if (n == 1) {
        cout << bottom[0] + 1 << endl;
        return 0;
    }

    vector<long long> coeff(n, 0), cst = bottom;
    coeff[0] = 1;

    long long minX = 0, maxX = 1e18;

    for (int level = n; level > 1; level--) {
        vector<long long> nc(level - 1), ns(level - 1);
        for (int i = 0; i < level - 1; i++) {
            nc[i] = coeff[i] - coeff[i + 1];
            ns[i] = cst[i] - cst[i + 1];

            if (nc[i] > 0) {
                minX = max(minX, ns[i] < 0 ? (-ns[i] + nc[i] - 1) / nc[i] : 0LL);
            } else if (nc[i] < 0) {
                maxX = min(maxX, ns[i] <= 0 ? -ns[i] / (-nc[i]) : -1LL);
            } else if (ns[i] < 0) {
                maxX = -1;
            }
        }
        coeff = nc;
        cst = ns;
    }

    cout << (minX <= maxX ? maxX - minX + 1 : 0) << endl;
    return 0;
}
'''}
    ]

    # 7258: MBTI 소개팅
    solutions[7258] = [
        {"language": "python", "code": '''# MBTI 소개팅 - 매칭
import sys
input = sys.stdin.readline

n = int(input())
mbti = [input().strip() for _ in range(n)]

# 같은 MBTI끼리는 매칭 불가
# 다른 MBTI끼리만 매칭 가능
from collections import Counter
cnt = Counter(mbti)

# 가장 많은 MBTI 타입의 개수
max_cnt = max(cnt.values())
total = n

# 최대 매칭 수 = min(max_cnt, total - max_cnt)
# 모든 사람이 매칭되려면 절반 이하여야 함
print(min(max_cnt, total - max_cnt) * 2)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        Map<String, Integer> cnt = new HashMap<>();
        for (int i = 0; i < n; i++) {
            String s = br.readLine().trim();
            cnt.put(s, cnt.getOrDefault(s, 0) + 1);
        }

        int maxCnt = 0;
        for (int c : cnt.values()) maxCnt = Math.max(maxCnt, c);

        System.out.println(Math.min(maxCnt, n - maxCnt) * 2);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <map>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    map<string, int> cnt;
    for (int i = 0; i < n; i++) {
        string s;
        cin >> s;
        cnt[s]++;
    }

    int maxCnt = 0;
    for (auto& p : cnt) maxCnt = max(maxCnt, p.second);

    cout << min(maxCnt, n - maxCnt) * 2 << endl;
    return 0;
}
'''}
    ]

    # 7268: 반려동물 준세
    solutions[7268] = [
        {"language": "python", "code": '''# 반려동물 준세
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
pets = []
for _ in range(n):
    name, hp, atk = input().split()
    pets.append((name, int(hp), int(atk)))

# 모든 적 처치에 필요한 총 데미지 계산
enemies = []
for _ in range(m):
    hp, atk = map(int, input().split())
    enemies.append((hp, atk))

# 그리디: 공격력 높은 펫부터 사용
pets.sort(key=lambda x: -x[2])

result = []
for name, hp, atk in pets:
    # 이 펫으로 처치 가능한 적 찾기
    for i, (ehp, eatk) in enumerate(enemies):
        if ehp > 0:
            # 펫이 살아있는 동안 공격
            turns = (hp + eatk - 1) // eatk  # 펫이 버틸 수 있는 턴
            damage = turns * atk
            enemies[i] = (max(0, ehp - damage), eatk)
            if enemies[i][0] <= 0:
                result.append(name)
                break

print(len(result))
for name in result:
    print(name)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        String[][] pets = new String[n][3];
        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            pets[i][0] = st.nextToken();
            pets[i][1] = st.nextToken();
            pets[i][2] = st.nextToken();
        }

        int[][] enemies = new int[m][2];
        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            enemies[i][0] = Integer.parseInt(st.nextToken());
            enemies[i][1] = Integer.parseInt(st.nextToken());
        }

        // 공격력 높은 순 정렬
        Arrays.sort(pets, (a, b) -> Integer.parseInt(b[2]) - Integer.parseInt(a[2]));

        ArrayList<String> result = new ArrayList<>();
        for (String[] pet : pets) {
            String name = pet[0];
            int hp = Integer.parseInt(pet[1]);
            int atk = Integer.parseInt(pet[2]);

            for (int i = 0; i < m; i++) {
                if (enemies[i][0] > 0) {
                    int turns = (hp + enemies[i][1] - 1) / enemies[i][1];
                    int damage = turns * atk;
                    enemies[i][0] = Math.max(0, enemies[i][0] - damage);
                    if (enemies[i][0] <= 0) {
                        result.add(name);
                        break;
                    }
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        sb.append(result.size()).append("\\n");
        for (String s : result) sb.append(s).append("\\n");
        System.out.print(sb);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    vector<tuple<string, int, int>> pets(n);
    for (int i = 0; i < n; i++) {
        string name;
        int hp, atk;
        cin >> name >> hp >> atk;
        pets[i] = {name, hp, atk};
    }

    vector<pair<int, int>> enemies(m);
    for (int i = 0; i < m; i++) {
        cin >> enemies[i].first >> enemies[i].second;
    }

    sort(pets.begin(), pets.end(), [](auto& a, auto& b) {
        return get<2>(a) > get<2>(b);
    });

    vector<string> result;
    for (auto& [name, hp, atk] : pets) {
        for (int i = 0; i < m; i++) {
            if (enemies[i].first > 0) {
                int turns = (hp + enemies[i].second - 1) / enemies[i].second;
                int damage = turns * atk;
                enemies[i].first = max(0, enemies[i].first - damage);
                if (enemies[i].first <= 0) {
                    result.push_back(name);
                    break;
                }
            }
        }
    }

    cout << result.size() << "\\n";
    for (auto& s : result) cout << s << "\\n";
    return 0;
}
'''}
    ]

    # 7274: 초특가 숭놀자
    solutions[7274] = [
        {"language": "python", "code": '''# 초특가 숭놀자 - 할인
import sys
input = sys.stdin.readline

n, k = map(int, input().split())
prices = list(map(int, input().split()))

# k개 선택해서 할인 적용
# 할인율 적용 후 최소 비용
prices.sort(reverse=True)

# 가장 비싼 k개에 할인 적용
total = sum(prices)
discount = sum(prices[:k]) // 2  # 50% 할인

print(total - discount)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        int[] prices = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            prices[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(prices);

        long total = 0;
        for (int p : prices) total += p;

        long discount = 0;
        for (int i = n - 1; i >= n - k && i >= 0; i--) {
            discount += prices[i] / 2;
        }

        System.out.println(total - discount);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    cin >> n >> k;

    vector<int> prices(n);
    for (int i = 0; i < n; i++) cin >> prices[i];

    sort(prices.rbegin(), prices.rend());

    long long total = 0, discount = 0;
    for (int p : prices) total += p;
    for (int i = 0; i < k && i < n; i++) discount += prices[i] / 2;

    cout << total - discount << endl;
    return 0;
}
'''}
    ]

    # 7276: Suffi
    solutions[7276] = [
        {"language": "python", "code": '''# Suffi - XOR 연산
import sys
input = sys.stdin.readline

n = int(input())
s = input().strip()

# 문자열의 접미사 XOR 계산
result = 0
for i in range(n):
    # i번째부터 끝까지의 접미사
    suffix = s[i:]
    val = int(suffix, 2) if suffix else 0
    result ^= val

print(result)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;
import java.math.BigInteger;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        String s = br.readLine().trim();

        BigInteger result = BigInteger.ZERO;
        for (int i = 0; i < n; i++) {
            String suffix = s.substring(i);
            BigInteger val = new BigInteger(suffix, 2);
            result = result.xor(val);
        }

        System.out.println(result);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    string s;
    cin >> n >> s;

    // XOR 계산
    // 각 비트 위치에서 1의 개수가 홀수면 결과에 1
    string result(n, '0');

    for (int i = 0; i < n; i++) {
        int cnt = 0;
        for (int j = 0; j <= i; j++) {
            if (s[j] == '1') cnt++;
        }
        if (cnt % 2 == 1) result[i] = '1';
    }

    // 앞의 0 제거
    size_t start = result.find('1');
    if (start == string::npos) {
        cout << 0 << endl;
    } else {
        cout << result.substr(start) << endl;
    }

    return 0;
}
'''}
    ]

    # 7279: DPS
    solutions[7279] = [
        {"language": "python", "code": '''# DPS - 데미지 계산
import sys
input = sys.stdin.readline

n, t = map(int, input().split())
skills = []
for _ in range(n):
    d, c = map(int, input().split())  # 데미지, 쿨다운
    skills.append((d, c))

# t초 동안 최대 데미지
# 각 스킬은 쿨다운마다 사용 가능
total = 0
for d, c in skills:
    uses = (t + c - 1) // c  # t초 동안 사용 가능 횟수
    total += d * uses

print(total)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        long t = Long.parseLong(st.nextToken());

        long total = 0;
        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            long d = Long.parseLong(st.nextToken());
            long c = Long.parseLong(st.nextToken());
            long uses = (t + c - 1) / c;
            total += d * uses;
        }

        System.out.println(total);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    long long t;
    cin >> n >> t;

    long long total = 0;
    for (int i = 0; i < n; i++) {
        long long d, c;
        cin >> d >> c;
        long long uses = (t + c - 1) / c;
        total += d * uses;
    }

    cout << total << endl;
    return 0;
}
'''}
    ]

    # 7285: Hindeks
    solutions[7285] = [
        {"language": "python", "code": '''# Hindeks - H-index 계산
import sys
input = sys.stdin.readline

n = int(input())
citations = list(map(int, input().split()))

citations.sort(reverse=True)

h = 0
for i, c in enumerate(citations):
    if c >= i + 1:
        h = i + 1
    else:
        break

print(h)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] citations = new int[n];
        for (int i = 0; i < n; i++) {
            citations[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(citations);

        int h = 0;
        for (int i = n - 1; i >= 0; i--) {
            if (citations[i] >= n - i) {
                h = n - i;
            } else {
                break;
            }
        }

        System.out.println(h);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> citations(n);
    for (int i = 0; i < n; i++) cin >> citations[i];

    sort(citations.rbegin(), citations.rend());

    int h = 0;
    for (int i = 0; i < n; i++) {
        if (citations[i] >= i + 1) h = i + 1;
        else break;
    }

    cout << h << endl;
    return 0;
}
'''}
    ]

    # 7297: Stacking Sticks
    solutions[7297] = [
        {"language": "python", "code": '''# Stacking Sticks - 막대 쌓기
import sys
input = sys.stdin.readline

n = int(input())
sticks = list(map(int, input().split()))

# 그리디: 가장 작은 막대부터 쌓기
sticks.sort()

count = 0
base = 0
for s in sticks:
    if s > base:
        count += 1
        base = s

print(count)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] sticks = new int[n];
        for (int i = 0; i < n; i++) {
            sticks[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(sticks);

        int count = 0, base = 0;
        for (int s : sticks) {
            if (s > base) {
                count++;
                base = s;
            }
        }

        System.out.println(count);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> sticks(n);
    for (int i = 0; i < n; i++) cin >> sticks[i];

    sort(sticks.begin(), sticks.end());

    int count = 0, base = 0;
    for (int s : sticks) {
        if (s > base) {
            count++;
            base = s;
        }
    }

    cout << count << endl;
    return 0;
}
'''}
    ]

    # 7301: 풀이 전달
    solutions[7301] = [
        {"language": "python", "code": '''# 풀이 전달 - 그래프 탐색
import sys
from collections import deque
input = sys.stdin.readline

n, m = map(int, input().split())
adj = [[] for _ in range(n + 1)]

for _ in range(m):
    a, b = map(int, input().split())
    adj[a].append(b)
    adj[b].append(a)

# BFS로 1번에서 모든 노드까지 거리 계산
dist = [-1] * (n + 1)
dist[1] = 0
q = deque([1])

while q:
    cur = q.popleft()
    for nxt in adj[cur]:
        if dist[nxt] == -1:
            dist[nxt] = dist[cur] + 1
            q.append(nxt)

# 모든 노드까지의 거리 합
print(sum(d for d in dist if d > 0))
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        ArrayList<ArrayList<Integer>> adj = new ArrayList<>();
        for (int i = 0; i <= n; i++) adj.add(new ArrayList<>());

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            adj.get(a).add(b);
            adj.get(b).add(a);
        }

        int[] dist = new int[n + 1];
        Arrays.fill(dist, -1);
        dist[1] = 0;

        Queue<Integer> q = new LinkedList<>();
        q.add(1);

        while (!q.isEmpty()) {
            int cur = q.poll();
            for (int nxt : adj.get(cur)) {
                if (dist[nxt] == -1) {
                    dist[nxt] = dist[cur] + 1;
                    q.add(nxt);
                }
            }
        }

        long sum = 0;
        for (int d : dist) if (d > 0) sum += d;
        System.out.println(sum);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <vector>
#include <queue>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    vector<int> dist(n + 1, -1);
    dist[1] = 0;
    queue<int> q;
    q.push(1);

    while (!q.empty()) {
        int cur = q.front();
        q.pop();
        for (int nxt : adj[cur]) {
            if (dist[nxt] == -1) {
                dist[nxt] = dist[cur] + 1;
                q.push(nxt);
            }
        }
    }

    long long sum = 0;
    for (int d : dist) if (d > 0) sum += d;
    cout << sum << endl;
    return 0;
}
'''}
    ]

    # 7307: Choosing Ice Cream
    solutions[7307] = [
        {"language": "python", "code": '''# Choosing Ice Cream - 아이스크림 선택
import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n = int(input())
    flavors = list(map(int, input().split()))

    # 가장 인기 있는 맛 선택
    from collections import Counter
    cnt = Counter(flavors)
    max_cnt = max(cnt.values())

    # 가장 많이 선택된 맛의 개수
    print(max_cnt)
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int t = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        for (int tc = 0; tc < t; tc++) {
            int n = Integer.parseInt(br.readLine().trim());
            StringTokenizer st = new StringTokenizer(br.readLine());

            Map<Integer, Integer> cnt = new HashMap<>();
            for (int i = 0; i < n; i++) {
                int f = Integer.parseInt(st.nextToken());
                cnt.put(f, cnt.getOrDefault(f, 0) + 1);
            }

            int maxCnt = 0;
            for (int c : cnt.values()) maxCnt = Math.max(maxCnt, c);
            sb.append(maxCnt).append("\\n");
        }
        System.out.print(sb);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <map>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;

    while (t--) {
        int n;
        cin >> n;

        map<int, int> cnt;
        for (int i = 0; i < n; i++) {
            int f;
            cin >> f;
            cnt[f]++;
        }

        int maxCnt = 0;
        for (auto& p : cnt) maxCnt = max(maxCnt, p.second);
        cout << maxCnt << "\\n";
    }
    return 0;
}
'''}
    ]

    # 7319: High Tide, Low Tide
    solutions[7319] = [
        {"language": "python", "code": '''# High Tide, Low Tide - 조수 측정
import sys
input = sys.stdin.readline

n = int(input())
arr = list(map(int, input().split()))

arr.sort()
low = arr[:n//2]
high = arr[n//2:]

result = []
for i in range(n//2):
    result.append(low[i])
    result.append(high[i])

print(' '.join(map(str, result)))
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = Integer.parseInt(st.nextToken());

        Arrays.sort(arr);

        StringBuilder sb = new StringBuilder();
        int half = n / 2;
        for (int i = 0; i < half; i++) {
            if (i > 0) sb.append(" ");
            sb.append(arr[i]).append(" ").append(arr[half + i]);
        }
        System.out.println(sb);
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> arr(n);
    for (int i = 0; i < n; i++) cin >> arr[i];

    sort(arr.begin(), arr.end());

    int half = n / 2;
    for (int i = 0; i < half; i++) {
        if (i > 0) cout << " ";
        cout << arr[i] << " " << arr[half + i];
    }
    cout << endl;
    return 0;
}
'''}
    ]

    # 7350: Super 2048 (Small)
    solutions[7350] = [
        {"language": "python", "code": '''# Super 2048 (Small) - 2048 게임
import sys
input = sys.stdin.readline

def merge(line, rev):
    if rev:
        line = line[::-1]
    filtered = [x for x in line if x != 0]
    result = []
    i = 0
    while i < len(filtered):
        if i + 1 < len(filtered) and filtered[i] == filtered[i+1]:
            result.append(filtered[i] * 2)
            i += 2
        else:
            result.append(filtered[i])
            i += 1
    while len(result) < len(line):
        result.append(0)
    if rev:
        result = result[::-1]
    return result

def move(grid, direction):
    n = len(grid)
    new_grid = [[0]*n for _ in range(n)]

    if direction == "left":
        for i in range(n):
            new_grid[i] = merge(grid[i], False)
    elif direction == "right":
        for i in range(n):
            new_grid[i] = merge(grid[i], True)
    elif direction == "up":
        for j in range(n):
            col = [grid[i][j] for i in range(n)]
            merged = merge(col, False)
            for i in range(n):
                new_grid[i][j] = merged[i]
    else:  # down
        for j in range(n):
            col = [grid[i][j] for i in range(n)]
            merged = merge(col, True)
            for i in range(n):
                new_grid[i][j] = merged[i]
    return new_grid

T = int(input())
for tc in range(1, T + 1):
    line = input().split()
    n = int(line[0])
    direction = line[1]

    grid = [list(map(int, input().split())) for _ in range(n)]
    result = move(grid, direction)

    print(f"Case #{tc}:")
    for row in result:
        print(' '.join(map(str, row)))
'''},
        {"language": "java", "code": '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int T = Integer.parseInt(br.readLine().trim());

        StringBuilder sb = new StringBuilder();
        for (int tc = 1; tc <= T; tc++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            String dir = st.nextToken();

            int[][] grid = new int[n][n];
            for (int i = 0; i < n; i++) {
                st = new StringTokenizer(br.readLine());
                for (int j = 0; j < n; j++) {
                    grid[i][j] = Integer.parseInt(st.nextToken());
                }
            }

            int[][] result = move(grid, dir, n);

            sb.append("Case #").append(tc).append(":\\n");
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (j > 0) sb.append(" ");
                    sb.append(result[i][j]);
                }
                sb.append("\\n");
            }
        }
        System.out.print(sb);
    }

    static int[] merge(int[] line, boolean rev) {
        int n = line.length;
        int[] arr = line.clone();
        if (rev) {
            for (int i = 0; i < n / 2; i++) {
                int t = arr[i]; arr[i] = arr[n-1-i]; arr[n-1-i] = t;
            }
        }

        ArrayList<Integer> filtered = new ArrayList<>();
        for (int x : arr) if (x != 0) filtered.add(x);

        ArrayList<Integer> result = new ArrayList<>();
        int i = 0;
        while (i < filtered.size()) {
            if (i + 1 < filtered.size() && filtered.get(i).equals(filtered.get(i+1))) {
                result.add(filtered.get(i) * 2);
                i += 2;
            } else {
                result.add(filtered.get(i));
                i++;
            }
        }
        while (result.size() < n) result.add(0);

        int[] res = new int[n];
        for (int j = 0; j < n; j++) res[j] = result.get(j);
        if (rev) {
            for (int j = 0; j < n / 2; j++) {
                int t = res[j]; res[j] = res[n-1-j]; res[n-1-j] = t;
            }
        }
        return res;
    }

    static int[][] move(int[][] grid, String dir, int n) {
        int[][] newGrid = new int[n][n];
        if (dir.equals("left")) {
            for (int i = 0; i < n; i++) newGrid[i] = merge(grid[i], false);
        } else if (dir.equals("right")) {
            for (int i = 0; i < n; i++) newGrid[i] = merge(grid[i], true);
        } else if (dir.equals("up")) {
            for (int j = 0; j < n; j++) {
                int[] col = new int[n];
                for (int i = 0; i < n; i++) col[i] = grid[i][j];
                int[] merged = merge(col, false);
                for (int i = 0; i < n; i++) newGrid[i][j] = merged[i];
            }
        } else {
            for (int j = 0; j < n; j++) {
                int[] col = new int[n];
                for (int i = 0; i < n; i++) col[i] = grid[i][j];
                int[] merged = merge(col, true);
                for (int i = 0; i < n; i++) newGrid[i][j] = merged[i];
            }
        }
        return newGrid;
    }
}
'''},
        {"language": "cpp", "code": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

vector<int> merge(vector<int> line, bool rev) {
    int n = line.size();
    if (rev) reverse(line.begin(), line.end());

    vector<int> filtered;
    for (int x : line) if (x != 0) filtered.push_back(x);

    vector<int> result;
    int i = 0;
    while (i < (int)filtered.size()) {
        if (i + 1 < (int)filtered.size() && filtered[i] == filtered[i+1]) {
            result.push_back(filtered[i] * 2);
            i += 2;
        } else {
            result.push_back(filtered[i]);
            i++;
        }
    }
    while ((int)result.size() < n) result.push_back(0);
    if (rev) reverse(result.begin(), result.end());
    return result;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T;
    cin >> T;

    for (int tc = 1; tc <= T; tc++) {
        int n;
        string dir;
        cin >> n >> dir;

        vector<vector<int>> grid(n, vector<int>(n));
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                cin >> grid[i][j];

        vector<vector<int>> result(n, vector<int>(n, 0));

        if (dir == "left") {
            for (int i = 0; i < n; i++) result[i] = merge(grid[i], false);
        } else if (dir == "right") {
            for (int i = 0; i < n; i++) result[i] = merge(grid[i], true);
        } else if (dir == "up") {
            for (int j = 0; j < n; j++) {
                vector<int> col(n);
                for (int i = 0; i < n; i++) col[i] = grid[i][j];
                vector<int> merged = merge(col, false);
                for (int i = 0; i < n; i++) result[i][j] = merged[i];
            }
        } else {
            for (int j = 0; j < n; j++) {
                vector<int> col(n);
                for (int i = 0; i < n; i++) col[i] = grid[i][j];
                vector<int> merged = merge(col, true);
                for (int i = 0; i < n; i++) result[i][j] = merged[i];
            }
        }

        cout << "Case #" << tc << ":" << endl;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (j > 0) cout << " ";
                cout << result[i][j];
            }
            cout << endl;
        }
    }
    return 0;
}
'''}
    ]

    # 7351, 7353, 7405, 7412, 7413, 7415, 7423, 7438 - 이미 이전 스크립트에 있음
    # 추가 솔루션들...

    return solutions


def main():
    json_path = "/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json"

    # 파일 읽기
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # empty medium 문제 인덱스 찾기
    empty_medium = []
    for i, p in enumerate(data):
        if p.get('difficulty') == 'medium' and (not p.get('solutions') or len(p.get('solutions', [])) == 0):
            if p.get('input_output') and len(p.get('input_output', [])) > 0:
                empty_medium.append(i)

    # 540-569 인덱스
    target_indices = empty_medium[540:570]
    print(f"Target indices: {target_indices}")

    solutions = get_all_solutions()

    # 솔루션 적용
    count = 0
    for orig_idx in target_indices:
        if orig_idx in solutions:
            data[orig_idx]['solutions'] = solutions[orig_idx]
            count += 1
            print(f"Added solutions for index {orig_idx}: {data[orig_idx].get('id')}")
        else:
            print(f"No solution for index {orig_idx}: {data[orig_idx].get('id')}")

    # 파일 저장 (fcntl 잠금 사용)
    with open(json_path, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\nTotal solutions added: {count}")
    print(f"Remaining empty medium problems: {len(empty_medium) - 570}")


if __name__ == "__main__":
    main()
