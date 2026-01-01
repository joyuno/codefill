#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배치 9: 인덱스 1379, 1391, 1393, 1403, 1410, 1416, 1424, 1425, 1427, 1434 솔루션 추가
"""

import json

def main():
    # 메인 파일 로드
    with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'r', encoding='utf-8') as f:
        problems = json.load(f)

    # 문제 1379 (2505) - 두 번 뒤집기
    solutions_1379 = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    arr = list(map(int, input().split()))

    def reverse_segment(a, i, j):
        result = a[:]
        while i < j:
            result[i], result[j] = result[j], result[i]
            i += 1
            j -= 1
        return result

    def is_sorted(a):
        for i in range(len(a)):
            if a[i] != i + 1:
                return False
        return True

    def find_segment(a):
        left = 0
        while left < len(a) and a[left] == left + 1:
            left += 1
        if left == len(a):
            return -1, -1
        right = len(a) - 1
        while right >= 0 and a[right] == right + 1:
            right -= 1
        return left, right

    def try_front_first(a):
        left1, right1 = find_segment(a)
        if left1 == -1:
            return (1, 1, 1, 1)
        a2 = reverse_segment(a, left1, right1)
        left2, right2 = find_segment(a2)
        if left2 == -1:
            return (left1 + 1, right1 + 1, 1, 1)
        a3 = reverse_segment(a2, left2, right2)
        if is_sorted(a3):
            return (left1 + 1, right1 + 1, left2 + 1, right2 + 1)
        return None

    def try_back_first(a):
        right1 = len(a) - 1
        while right1 >= 0 and a[right1] == right1 + 1:
            right1 -= 1
        if right1 == -1:
            return (1, 1, 1, 1)
        left1 = right1
        while left1 > 0 and a[left1 - 1] > a[left1]:
            left1 -= 1
        a2 = reverse_segment(a, left1, right1)
        left2, right2 = find_segment(a2)
        if left2 == -1:
            return (left1 + 1, right1 + 1, 1, 1)
        a3 = reverse_segment(a2, left2, right2)
        if is_sorted(a3):
            return (left1 + 1, right1 + 1, left2 + 1, right2 + 1)
        return None

    result = try_front_first(arr)
    if result:
        print(result[0], result[1])
        print(result[2], result[3])
        return
    result = try_back_first(arr)
    if result:
        print(result[0], result[1])
        print(result[2], result[3])

solve()
"""
        },
        {
            "language": "java",
            "code": """import java.io.*;
import java.util.*;

public class Main {
    static int n;
    static int[] arr;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        n = Integer.parseInt(br.readLine().trim());
        arr = new int[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }
        int[] result = tryFromFront(arr.clone());
        if (result != null) {
            System.out.println(result[0] + " " + result[1]);
            System.out.println(result[2] + " " + result[3]);
            return;
        }
        result = tryFromBack(arr.clone());
        if (result != null) {
            System.out.println(result[0] + " " + result[1]);
            System.out.println(result[2] + " " + result[3]);
        }
    }

    static void reverse(int[] a, int l, int r) {
        while (l < r) {
            int tmp = a[l]; a[l] = a[r]; a[r] = tmp;
            l++; r--;
        }
    }

    static boolean isSorted(int[] a) {
        for (int i = 0; i < n; i++) if (a[i] != i + 1) return false;
        return true;
    }

    static int[] findSegment(int[] a) {
        int l = 0;
        while (l < n && a[l] == l + 1) l++;
        if (l == n) return new int[]{-1, -1};
        int r = n - 1;
        while (r >= 0 && a[r] == r + 1) r--;
        return new int[]{l, r};
    }

    static int[] tryFromFront(int[] a) {
        int[] seg1 = findSegment(a);
        if (seg1[0] == -1) return new int[]{1, 1, 1, 1};
        reverse(a, seg1[0], seg1[1]);
        int[] seg2 = findSegment(a);
        if (seg2[0] == -1) return new int[]{seg1[0]+1, seg1[1]+1, 1, 1};
        reverse(a, seg2[0], seg2[1]);
        if (isSorted(a)) return new int[]{seg1[0]+1, seg1[1]+1, seg2[0]+1, seg2[1]+1};
        return null;
    }

    static int[] tryFromBack(int[] a) {
        int r = n - 1;
        while (r >= 0 && a[r] == r + 1) r--;
        if (r == -1) return new int[]{1, 1, 1, 1};
        int l = r;
        while (l > 0 && a[l-1] > a[l]) l--;
        reverse(a, l, r);
        int[] seg2 = findSegment(a);
        if (seg2[0] == -1) return new int[]{l+1, r+1, 1, 1};
        reverse(a, seg2[0], seg2[1]);
        if (isSorted(a)) return new int[]{l+1, r+1, seg2[0]+1, seg2[1]+1};
        return null;
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

int n;
vector<int> arr;

void reverseSegment(vector<int>& a, int l, int r) {
    while (l < r) { swap(a[l], a[r]); l++; r--; }
}

bool isSorted(vector<int>& a) {
    for (int i = 0; i < n; i++) if (a[i] != i + 1) return false;
    return true;
}

pair<int, int> findSegment(vector<int>& a) {
    int l = 0;
    while (l < n && a[l] == l + 1) l++;
    if (l == n) return {-1, -1};
    int r = n - 1;
    while (r >= 0 && a[r] == r + 1) r--;
    return {l, r};
}

vector<int> tryFromFront(vector<int> a) {
    auto [l1, r1] = findSegment(a);
    if (l1 == -1) return {1, 1, 1, 1};
    reverseSegment(a, l1, r1);
    auto [l2, r2] = findSegment(a);
    if (l2 == -1) return {l1+1, r1+1, 1, 1};
    reverseSegment(a, l2, r2);
    if (isSorted(a)) return {l1+1, r1+1, l2+1, r2+1};
    return {};
}

vector<int> tryFromBack(vector<int> a) {
    int r = n - 1;
    while (r >= 0 && a[r] == r + 1) r--;
    if (r == -1) return {1, 1, 1, 1};
    int l = r;
    while (l > 0 && a[l-1] > a[l]) l--;
    reverseSegment(a, l, r);
    auto [l2, r2] = findSegment(a);
    if (l2 == -1) return {l+1, r+1, 1, 1};
    reverseSegment(a, l2, r2);
    if (isSorted(a)) return {l+1, r+1, l2+1, r2+1};
    return {};
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cin >> n;
    arr.resize(n);
    for (int i = 0; i < n; i++) cin >> arr[i];
    vector<int> result = tryFromFront(arr);
    if (!result.empty()) {
        cout << result[0] << " " << result[1] << "\\n";
        cout << result[2] << " " << result[3] << "\\n";
        return 0;
    }
    result = tryFromBack(arr);
    if (!result.empty()) {
        cout << result[0] << " " << result[1] << "\\n";
        cout << result[2] << " " << result[3] << "\\n";
    }
    return 0;
}
"""
        }
    ]

    # 문제 1391 (14865) - 곡선 자르기
    solutions_1391 = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    points = []
    for _ in range(n):
        x, y = map(int, input().split())
        points.append((x, y))
    peaks = []
    m = len(points)
    for i in range(m):
        curr_y = points[i][1]
        next_y = points[(i + 1) % m][1]
        if curr_y < 0 and next_y > 0:
            start_x = points[i][0]
            j = (i + 1) % m
            while True:
                curr_y2 = points[j][1]
                next_y2 = points[(j + 1) % m][1]
                if curr_y2 > 0 and next_y2 < 0:
                    end_x = points[j][0]
                    peaks.append((min(start_x, end_x), max(start_x, end_x)))
                    break
                j = (j + 1) % m
    peaks.sort()
    top_level = 0
    contains_child = set()
    stack = []
    for i, (l, r) in enumerate(peaks):
        while stack and peaks[stack[-1]][1] < l:
            stack.pop()
        if not stack:
            top_level += 1
        else:
            contains_child.add(stack[-1])
        stack.append(i)
    leaf = len(peaks) - len(contains_child)
    print(top_level, leaf)

solve()
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
        long[][] points = new long[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            points[i][0] = Long.parseLong(st.nextToken());
            points[i][1] = Long.parseLong(st.nextToken());
        }
        List<long[]> peaks = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            long currY = points[i][1];
            long nextY = points[(i + 1) % n][1];
            if (currY < 0 && nextY > 0) {
                long startX = points[i][0];
                int j = (i + 1) % n;
                while (true) {
                    long currY2 = points[j][1];
                    long nextY2 = points[(j + 1) % n][1];
                    if (currY2 > 0 && nextY2 < 0) {
                        long endX = points[j][0];
                        peaks.add(new long[]{Math.min(startX, endX), Math.max(startX, endX)});
                        break;
                    }
                    j = (j + 1) % n;
                }
            }
        }
        peaks.sort((a, b) -> Long.compare(a[0], b[0]));
        int topLevel = 0;
        Set<Integer> containsChild = new HashSet<>();
        Stack<Integer> stack = new Stack<>();
        for (int i = 0; i < peaks.size(); i++) {
            long l = peaks.get(i)[0];
            while (!stack.isEmpty() && peaks.get(stack.peek())[1] < l) stack.pop();
            if (stack.isEmpty()) topLevel++;
            else containsChild.add(stack.peek());
            stack.push(i);
        }
        int leaf = peaks.size() - containsChild.size();
        System.out.println(topLevel + " " + leaf);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <algorithm>
#include <stack>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<pair<long long, long long>> points(n);
    for (int i = 0; i < n; i++) cin >> points[i].first >> points[i].second;
    vector<pair<long long, long long>> peaks;
    for (int i = 0; i < n; i++) {
        long long currY = points[i].second;
        long long nextY = points[(i + 1) % n].second;
        if (currY < 0 && nextY > 0) {
            long long startX = points[i].first;
            int j = (i + 1) % n;
            while (true) {
                long long currY2 = points[j].second;
                long long nextY2 = points[(j + 1) % n].second;
                if (currY2 > 0 && nextY2 < 0) {
                    long long endX = points[j].first;
                    peaks.push_back({min(startX, endX), max(startX, endX)});
                    break;
                }
                j = (j + 1) % n;
            }
        }
    }
    sort(peaks.begin(), peaks.end());
    int topLevel = 0;
    set<int> containsChild;
    stack<int> st;
    for (int i = 0; i < (int)peaks.size(); i++) {
        long long l = peaks[i].first;
        while (!st.empty() && peaks[st.top()].second < l) st.pop();
        if (st.empty()) topLevel++;
        else containsChild.insert(st.top());
        st.push(i);
    }
    int leaf = peaks.size() - containsChild.size();
    cout << topLevel << " " << leaf << endl;
    return 0;
}
"""
        }
    ]

    # 문제 1393 (10827) - a^b
    solutions_1393 = [
        {
            "language": "python",
            "code": """from decimal import Decimal, getcontext
getcontext().prec = 1000
line = input().split()
a = Decimal(line[0])
b = int(line[1])
result = a ** b
result_str = str(result)
if '.' in result_str:
    result_str = result_str.rstrip('0').rstrip('.')
print(result_str)
"""
        },
        {
            "language": "java",
            "code": """import java.io.*;
import java.math.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] parts = br.readLine().split(" ");
        String aStr = parts[0];
        int b = Integer.parseInt(parts[1]);
        int dotIndex = aStr.indexOf('.');
        int decimalPlaces = aStr.length() - dotIndex - 1;
        String intStr = aStr.replace(".", "");
        BigInteger base = new BigInteger(intStr);
        BigInteger result = base.pow(b);
        int totalDecimalPlaces = decimalPlaces * b;
        String resultStr = result.toString();
        if (totalDecimalPlaces == 0) {
            System.out.println(resultStr);
        } else if (totalDecimalPlaces >= resultStr.length()) {
            StringBuilder sb = new StringBuilder("0.");
            for (int i = 0; i < totalDecimalPlaces - resultStr.length(); i++) sb.append('0');
            sb.append(resultStr);
            String s = sb.toString();
            while (s.endsWith("0")) s = s.substring(0, s.length() - 1);
            if (s.endsWith(".")) s = s.substring(0, s.length() - 1);
            System.out.println(s);
        } else {
            int intPartLen = resultStr.length() - totalDecimalPlaces;
            String intPart = resultStr.substring(0, intPartLen);
            String decPart = resultStr.substring(intPartLen);
            while (decPart.endsWith("0")) decPart = decPart.substring(0, decPart.length() - 1);
            if (decPart.isEmpty()) System.out.println(intPart);
            else System.out.println(intPart + "." + decPart);
        }
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
#include <vector>
using namespace std;

string multiply(const string& a, const string& b) {
    int n = a.size(), m = b.size();
    vector<int> result(n + m, 0);
    for (int i = n - 1; i >= 0; i--) {
        for (int j = m - 1; j >= 0; j--) {
            int mul = (a[i] - '0') * (b[j] - '0');
            int p1 = i + j, p2 = i + j + 1;
            int sum = mul + result[p2];
            result[p2] = sum % 10;
            result[p1] += sum / 10;
        }
    }
    string str;
    for (int i : result) if (!(str.empty() && i == 0)) str += to_string(i);
    return str.empty() ? "0" : str;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    string a; int b;
    cin >> a >> b;
    int dotPos = a.find('.');
    int decimalPlaces = a.size() - dotPos - 1;
    string intStr = a.substr(0, dotPos) + a.substr(dotPos + 1);
    while (intStr.size() > 1 && intStr[0] == '0') intStr = intStr.substr(1);
    string result = "1";
    for (int i = 0; i < b; i++) result = multiply(result, intStr);
    int totalDecimalPlaces = decimalPlaces * b;
    if (totalDecimalPlaces == 0) {
        cout << result << endl;
    } else if (totalDecimalPlaces >= (int)result.size()) {
        cout << "0.";
        for (int i = 0; i < totalDecimalPlaces - (int)result.size(); i++) cout << '0';
        while (!result.empty() && result.back() == '0') result.pop_back();
        cout << result << endl;
    } else {
        int intPartLen = result.size() - totalDecimalPlaces;
        string intPart = result.substr(0, intPartLen);
        string decPart = result.substr(intPartLen);
        while (!decPart.empty() && decPart.back() == '0') decPart.pop_back();
        if (decPart.empty()) cout << intPart << endl;
        else cout << intPart << "." << decPart << endl;
    }
    return 0;
}
"""
        }
    ]

    # 문제 1403 (1445) - 일요일 아침의 데이트
    solutions_1403 = [
        {
            "language": "python",
            "code": """import sys
import heapq
input = sys.stdin.readline

def solve():
    n, m = map(int, input().split())
    grid = []
    start = end = None
    for i in range(n):
        row = input().strip()
        grid.append(row)
        for j in range(len(row)):
            if row[j] == 'S': start = (i, j)
            elif row[j] == 'F': end = (i, j)
    near_garbage = [[False] * m for _ in range(n)]
    dx, dy = [-1, 1, 0, 0], [0, 0, -1, 1]
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 'g':
                for d in range(4):
                    ni, nj = i + dx[d], j + dy[d]
                    if 0 <= ni < n and 0 <= nj < m and grid[ni][nj] == '.':
                        near_garbage[ni][nj] = True
    dist = [[[float('inf'), float('inf')] for _ in range(m)] for _ in range(n)]
    dist[start[0]][start[1]] = [0, 0]
    pq = [(0, 0, start[0], start[1])]
    while pq:
        trash, near, x, y = heapq.heappop(pq)
        if x == end[0] and y == end[1]:
            print(trash, near)
            return
        if [trash, near] > dist[x][y]: continue
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]
            if 0 <= nx < n and 0 <= ny < m:
                cell = grid[nx][ny]
                new_trash, new_near = trash, near
                if cell == 'g': new_trash += 1
                elif cell == '.' and near_garbage[nx][ny]: new_near += 1
                if [new_trash, new_near] < dist[nx][ny]:
                    dist[nx][ny] = [new_trash, new_near]
                    heapq.heappush(pq, (new_trash, new_near, nx, ny))
    print(dist[end[0]][end[1]][0], dist[end[0]][end[1]][1])

solve()
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
        char[][] grid = new char[n][m];
        boolean[][] nearGarbage = new boolean[n][m];
        int startX = 0, startY = 0, endX = 0, endY = 0;
        int[] dx = {-1, 1, 0, 0}, dy = {0, 0, -1, 1};
        for (int i = 0; i < n; i++) {
            String line = br.readLine();
            for (int j = 0; j < m; j++) {
                grid[i][j] = line.charAt(j);
                if (grid[i][j] == 'S') { startX = i; startY = j; }
                else if (grid[i][j] == 'F') { endX = i; endY = j; }
            }
        }
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (grid[i][j] == 'g') {
                    for (int d = 0; d < 4; d++) {
                        int ni = i + dx[d], nj = j + dy[d];
                        if (ni >= 0 && ni < n && nj >= 0 && nj < m && grid[ni][nj] == '.') nearGarbage[ni][nj] = true;
                    }
                }
            }
        }
        int[][] dist = new int[n][m];
        for (int[] row : dist) Arrays.fill(row, Integer.MAX_VALUE);
        dist[startX][startY] = 0;
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
        pq.offer(new int[]{0, startX, startY});
        while (!pq.isEmpty()) {
            int[] curr = pq.poll();
            int cost = curr[0], x = curr[1], y = curr[2];
            if (cost > dist[x][y]) continue;
            for (int d = 0; d < 4; d++) {
                int nx = x + dx[d], ny = y + dy[d];
                if (nx >= 0 && nx < n && ny >= 0 && ny < m) {
                    int newCost = cost;
                    if (grid[nx][ny] == 'g') newCost += 10000;
                    else if (grid[nx][ny] == '.' && nearGarbage[nx][ny]) newCost += 1;
                    if (newCost < dist[nx][ny]) {
                        dist[nx][ny] = newCost;
                        pq.offer(new int[]{newCost, nx, ny});
                    }
                }
            }
        }
        int result = dist[endX][endY];
        System.out.println(result / 10000 + " " + result % 10000);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <queue>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<string> grid(n);
    vector<vector<bool>> nearGarbage(n, vector<bool>(m, false));
    int startX, startY, endX, endY;
    int dx[] = {-1, 1, 0, 0}, dy[] = {0, 0, -1, 1};
    for (int i = 0; i < n; i++) {
        cin >> grid[i];
        for (int j = 0; j < m; j++) {
            if (grid[i][j] == 'S') { startX = i; startY = j; }
            else if (grid[i][j] == 'F') { endX = i; endY = j; }
        }
    }
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (grid[i][j] == 'g') {
                for (int d = 0; d < 4; d++) {
                    int ni = i + dx[d], nj = j + dy[d];
                    if (ni >= 0 && ni < n && nj >= 0 && nj < m && grid[ni][nj] == '.') nearGarbage[ni][nj] = true;
                }
            }
        }
    }
    vector<vector<int>> dist(n, vector<int>(m, INT_MAX));
    dist[startX][startY] = 0;
    priority_queue<tuple<int, int, int>, vector<tuple<int, int, int>>, greater<>> pq;
    pq.push({0, startX, startY});
    while (!pq.empty()) {
        auto [cost, x, y] = pq.top(); pq.pop();
        if (cost > dist[x][y]) continue;
        for (int d = 0; d < 4; d++) {
            int nx = x + dx[d], ny = y + dy[d];
            if (nx >= 0 && nx < n && ny >= 0 && ny < m) {
                int newCost = cost;
                if (grid[nx][ny] == 'g') newCost += 10000;
                else if (grid[nx][ny] == '.' && nearGarbage[nx][ny]) newCost += 1;
                if (newCost < dist[nx][ny]) {
                    dist[nx][ny] = newCost;
                    pq.push({newCost, nx, ny});
                }
            }
        }
    }
    int result = dist[endX][endY];
    cout << result / 10000 << " " << result % 10000 << endl;
    return 0;
}
"""
        }
    ]

    # 문제 1410 (1315) - RPG
    solutions_1410 = [
        {
            "language": "python",
            "code": """import sys
sys.setrecursionlimit(100000)
input = sys.stdin.readline

n = int(input())
quests = []
for _ in range(n):
    s, i, p = map(int, input().split())
    quests.append((s, i, p))

memo = {}

def dfs(strength, intelligence):
    if (strength, intelligence) in memo:
        return memo[(strength, intelligence)]
    count = 0
    total_points = 0
    for idx in range(n):
        s, i, p = quests[idx]
        if strength >= s or intelligence >= i:
            count += 1
            total_points += p
    memo[(strength, intelligence)] = count
    available = total_points - (strength - 1) - (intelligence - 1)
    if available <= 0:
        return count
    for new_str in range(strength, min(1001, strength + available + 1)):
        remain = available - (new_str - strength)
        new_int = min(1000, intelligence + remain)
        if new_str > strength or new_int > intelligence:
            result = dfs(new_str, new_int)
            if result > count:
                count = result
                memo[(strength, intelligence)] = count
    return count

print(dfs(1, 1))
"""
        },
        {
            "language": "java",
            "code": """import java.io.*;
import java.util.*;

public class Main {
    static int n;
    static int[][] quests;
    static int[][] dp;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        n = Integer.parseInt(br.readLine().trim());
        quests = new int[n][3];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            quests[i][0] = Integer.parseInt(st.nextToken());
            quests[i][1] = Integer.parseInt(st.nextToken());
            quests[i][2] = Integer.parseInt(st.nextToken());
        }
        dp = new int[1001][1001];
        for (int[] row : dp) Arrays.fill(row, -1);
        System.out.println(solve(1, 1));
    }

    static int solve(int str, int intel) {
        if (dp[str][intel] != -1) return dp[str][intel];
        int count = 0, totalPoints = 0;
        for (int i = 0; i < n; i++) {
            if (str >= quests[i][0] || intel >= quests[i][1]) {
                count++;
                totalPoints += quests[i][2];
            }
        }
        dp[str][intel] = count;
        int available = totalPoints - (str - 1) - (intel - 1);
        if (available <= 0) return count;
        for (int newStr = str; newStr <= Math.min(1000, str + available); newStr++) {
            int remain = available - (newStr - str);
            int newInt = Math.min(1000, intel + remain);
            if (newStr > str || newInt > intel) {
                int result = solve(newStr, newInt);
                if (result > dp[str][intel]) dp[str][intel] = result;
            }
        }
        return dp[str][intel];
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <cstring>
#include <algorithm>
using namespace std;

int n;
int quests[51][3];
int dp[1001][1001];

int solve(int str, int intel) {
    if (dp[str][intel] != -1) return dp[str][intel];
    int count = 0, totalPoints = 0;
    for (int i = 0; i < n; i++) {
        if (str >= quests[i][0] || intel >= quests[i][1]) {
            count++;
            totalPoints += quests[i][2];
        }
    }
    dp[str][intel] = count;
    int available = totalPoints - (str - 1) - (intel - 1);
    if (available <= 0) return count;
    for (int newStr = str; newStr <= min(1000, str + available); newStr++) {
        int remain = available - (newStr - str);
        int newInt = min(1000, intel + remain);
        if (newStr > str || newInt > intel) {
            int result = solve(newStr, newInt);
            dp[str][intel] = max(dp[str][intel], result);
        }
    }
    return dp[str][intel];
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cin >> n;
    for (int i = 0; i < n; i++) cin >> quests[i][0] >> quests[i][1] >> quests[i][2];
    memset(dp, -1, sizeof(dp));
    cout << solve(1, 1) << endl;
    return 0;
}
"""
        }
    ]

    # 문제 1416 (32069) - 가로등
    solutions_1416 = [
        {
            "language": "python",
            "code": """import sys
import heapq
input = sys.stdin.readline

L, N, K = map(int, input().split())
A = list(map(int, input().split()))
pq = []
for i in range(N):
    heapq.heappush(pq, (0, i, 0))
count = 0
while pq and count < K:
    dist, idx, direction = heapq.heappop(pq)
    if direction == 0:
        pos = A[idx]
    elif direction == -1:
        pos = A[idx] - dist
    else:
        pos = A[idx] + dist
    if pos < 0 or pos > L:
        continue
    valid = True
    if direction == -1 and idx > 0:
        if pos <= (A[idx - 1] + A[idx]) // 2:
            valid = False
    if direction == 1 and idx < N - 1:
        mid = (A[idx] + A[idx + 1]) // 2
        if pos > mid:
            valid = False
        if pos == mid and (A[idx] + A[idx + 1]) % 2 == 0:
            valid = False
    if valid:
        print(dist)
        count += 1
    if direction == 0:
        heapq.heappush(pq, (1, idx, -1))
        heapq.heappush(pq, (1, idx, 1))
    else:
        heapq.heappush(pq, (dist + 1, idx, direction))
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
        long L = Long.parseLong(st.nextToken());
        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());
        long[] A = new long[N];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) A[i] = Long.parseLong(st.nextToken());
        StringBuilder sb = new StringBuilder();
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        for (int i = 0; i < N; i++) pq.offer(new long[]{0, i, 0});
        int count = 0;
        while (!pq.isEmpty() && count < K) {
            long[] curr = pq.poll();
            long dist = curr[0];
            int idx = (int)curr[1];
            long dir = curr[2];
            long pos = dir == 0 ? A[idx] : (dir == -1 ? A[idx] - dist : A[idx] + dist);
            if (pos < 0 || pos > L) continue;
            boolean valid = true;
            if (dir == -1 && idx > 0 && pos <= (A[idx - 1] + A[idx]) / 2) valid = false;
            if (dir == 1 && idx < N - 1) {
                long mid = (A[idx] + A[idx + 1]) / 2;
                if (pos > mid || (pos == mid && (A[idx] + A[idx + 1]) % 2 == 0)) valid = false;
            }
            if (valid) { sb.append(dist).append("\\n"); count++; }
            if (dir == 0) { pq.offer(new long[]{1, idx, -1}); pq.offer(new long[]{1, idx, 1}); }
            else pq.offer(new long[]{dist + 1, idx, dir});
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
#include <queue>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    long long L; int N, K;
    cin >> L >> N >> K;
    vector<long long> A(N);
    for (int i = 0; i < N; i++) cin >> A[i];
    priority_queue<tuple<long long, int, int>, vector<tuple<long long, int, int>>, greater<>> pq;
    for (int i = 0; i < N; i++) pq.push({0, i, 0});
    int count = 0;
    while (!pq.empty() && count < K) {
        auto [dist, idx, dir] = pq.top(); pq.pop();
        long long pos = dir == 0 ? A[idx] : (dir == -1 ? A[idx] - dist : A[idx] + dist);
        if (pos < 0 || pos > L) continue;
        bool valid = true;
        if (dir == -1 && idx > 0 && pos <= (A[idx - 1] + A[idx]) / 2) valid = false;
        if (dir == 1 && idx < N - 1) {
            long long mid = (A[idx] + A[idx + 1]) / 2;
            if (pos > mid || (pos == mid && (A[idx] + A[idx + 1]) % 2 == 0)) valid = false;
        }
        if (valid) { cout << dist << "\\n"; count++; }
        if (dir == 0) { pq.push({1, idx, -1}); pq.push({1, idx, 1}); }
        else pq.push({dist + 1, idx, dir});
    }
    return 0;
}
"""
        }
    ]

    # 문제 1424 (15311) - 약 팔기
    solutions_1424 = [
        {
            "language": "python",
            "code": """n = int(input())
result = []
val = 1
while val <= n:
    result.append(val)
    val *= 2
for i in range(len(result) - 2, -1, -1):
    result.append(result[i])
print(len(result))
print(' '.join(map(str, result)))
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
        List<Integer> result = new ArrayList<>();
        int val = 1;
        while (val <= n) { result.add(val); val *= 2; }
        for (int i = result.size() - 2; i >= 0; i--) result.add(result.get(i));
        StringBuilder sb = new StringBuilder();
        sb.append(result.size()).append("\\n");
        for (int i = 0; i < result.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(result.get(i));
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
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> result;
    int val = 1;
    while (val <= n) { result.push_back(val); val *= 2; }
    for (int i = result.size() - 2; i >= 0; i--) result.push_back(result[i]);
    cout << result.size() << "\\n";
    for (int i = 0; i < (int)result.size(); i++) {
        if (i > 0) cout << " ";
        cout << result[i];
    }
    cout << endl;
    return 0;
}
"""
        }
    ]

    # 문제 1425 (22866) - 탑 보기
    solutions_1425 = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

n = int(input())
heights = list(map(int, input().split()))
count = [0] * n
nearest = [-1] * n
nearest_dist = [float('inf')] * n

stack = []
for i in range(n):
    while stack and stack[-1][0] <= heights[i]:
        stack.pop()
    count[i] += len(stack)
    if stack:
        dist = i - stack[-1][1]
        if dist < nearest_dist[i]:
            nearest_dist[i] = dist
            nearest[i] = stack[-1][1] + 1
    stack.append((heights[i], i))

stack = []
for i in range(n - 1, -1, -1):
    while stack and stack[-1][0] <= heights[i]:
        stack.pop()
    count[i] += len(stack)
    if stack:
        dist = stack[-1][1] - i
        if dist < nearest_dist[i] or (dist == nearest_dist[i] and stack[-1][1] + 1 < nearest[i]):
            nearest_dist[i] = dist
            nearest[i] = stack[-1][1] + 1
    stack.append((heights[i], i))

for i in range(n):
    if count[i] == 0:
        print(0)
    else:
        print(count[i], nearest[i])
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
        int[] heights = new int[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) heights[i] = Integer.parseInt(st.nextToken());
        int[] count = new int[n];
        int[] nearest = new int[n];
        int[] nearestDist = new int[n];
        Arrays.fill(nearest, -1);
        Arrays.fill(nearestDist, Integer.MAX_VALUE);
        Stack<int[]> stack = new Stack<>();
        for (int i = 0; i < n; i++) {
            while (!stack.isEmpty() && stack.peek()[0] <= heights[i]) stack.pop();
            count[i] += stack.size();
            if (!stack.isEmpty()) {
                int dist = i - stack.peek()[1];
                if (dist < nearestDist[i]) { nearestDist[i] = dist; nearest[i] = stack.peek()[1] + 1; }
            }
            stack.push(new int[]{heights[i], i});
        }
        stack.clear();
        for (int i = n - 1; i >= 0; i--) {
            while (!stack.isEmpty() && stack.peek()[0] <= heights[i]) stack.pop();
            count[i] += stack.size();
            if (!stack.isEmpty()) {
                int dist = stack.peek()[1] - i;
                if (dist < nearestDist[i] || (dist == nearestDist[i] && stack.peek()[1] + 1 < nearest[i])) {
                    nearestDist[i] = dist; nearest[i] = stack.peek()[1] + 1;
                }
            }
            stack.push(new int[]{heights[i], i});
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (count[i] == 0) sb.append("0\\n");
            else sb.append(count[i]).append(" ").append(nearest[i]).append("\\n");
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
#include <stack>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> heights(n);
    for (int i = 0; i < n; i++) cin >> heights[i];
    vector<int> count(n, 0), nearest(n, -1), nearestDist(n, INT_MAX);
    stack<pair<int, int>> st;
    for (int i = 0; i < n; i++) {
        while (!st.empty() && st.top().first <= heights[i]) st.pop();
        count[i] += st.size();
        if (!st.empty()) {
            int dist = i - st.top().second;
            if (dist < nearestDist[i]) { nearestDist[i] = dist; nearest[i] = st.top().second + 1; }
        }
        st.push({heights[i], i});
    }
    while (!st.empty()) st.pop();
    for (int i = n - 1; i >= 0; i--) {
        while (!st.empty() && st.top().first <= heights[i]) st.pop();
        count[i] += st.size();
        if (!st.empty()) {
            int dist = st.top().second - i;
            if (dist < nearestDist[i] || (dist == nearestDist[i] && st.top().second + 1 < nearest[i])) {
                nearestDist[i] = dist; nearest[i] = st.top().second + 1;
            }
        }
        st.push({heights[i], i});
    }
    for (int i = 0; i < n; i++) {
        if (count[i] == 0) cout << "0\\n";
        else cout << count[i] << " " << nearest[i] << "\\n";
    }
    return 0;
}
"""
        }
    ]

    # 문제 1427 (4008) - 특공대 (CHT)
    solutions_1427 = [
        {
            "language": "python",
            "code": """import sys
input = sys.stdin.readline

n = int(input())
a, b, c = map(int, input().split())
x = list(map(int, input().split()))

prefix = [0] * (n + 1)
for i in range(n):
    prefix[i + 1] = prefix[i] + x[i]

lines = []

def bad(l1, l2, l3):
    m1, k1 = lines[l1]
    m2, k2 = lines[l2]
    m3, k3 = lines[l3]
    return (k1 - k2) * (m3 - m2) >= (k2 - k3) * (m2 - m1)

def add_line(m, k):
    lines.append((m, k))
    while len(lines) >= 3 and bad(len(lines) - 3, len(lines) - 2, len(lines) - 1):
        lines[-2] = lines[-1]
        lines.pop()

def query(x):
    lo, hi = 0, len(lines) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        m1, k1 = lines[mid]
        m2, k2 = lines[mid + 1]
        if m1 * x + k1 < m2 * x + k2:
            lo = mid + 1
        else:
            hi = mid
    m, k = lines[lo]
    return m * x + k

dp = [0] * (n + 1)
s0 = prefix[0]
add_line(2 * a * s0, dp[0] + a * s0 * s0 - b * s0)

for i in range(1, n + 1):
    si = prefix[i]
    dp[i] = a * si * si + b * si + c + query(si)
    mi = 2 * a * si
    ki = dp[i] + a * si * si - b * si
    add_line(mi, ki)

print(dp[n])
"""
        },
        {
            "language": "java",
            "code": """import java.io.*;
import java.util.*;

public class Main {
    static long[] lineM, lineK;
    static int lineSize = 0;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        long a = Long.parseLong(st.nextToken());
        long b = Long.parseLong(st.nextToken());
        long c = Long.parseLong(st.nextToken());
        long[] x = new long[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) x[i] = Long.parseLong(st.nextToken());
        long[] prefix = new long[n + 1];
        for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + x[i];
        lineM = new long[n + 1];
        lineK = new long[n + 1];
        long[] dp = new long[n + 1];
        addLine(2 * a * prefix[0], dp[0] + a * prefix[0] * prefix[0] - b * prefix[0]);
        for (int i = 1; i <= n; i++) {
            long si = prefix[i];
            dp[i] = a * si * si + b * si + c + query(si);
            addLine(2 * a * si, dp[i] + a * si * si - b * si);
        }
        System.out.println(dp[n]);
    }

    static boolean bad(int l1, int l2, int l3) {
        return (double)(lineK[l1] - lineK[l2]) * (lineM[l3] - lineM[l2]) >= (double)(lineK[l2] - lineK[l3]) * (lineM[l2] - lineM[l1]);
    }

    static void addLine(long m, long k) {
        lineM[lineSize] = m;
        lineK[lineSize] = k;
        while (lineSize >= 2 && bad(lineSize - 2, lineSize - 1, lineSize)) {
            lineM[lineSize - 1] = lineM[lineSize];
            lineK[lineSize - 1] = lineK[lineSize];
            lineSize--;
        }
        lineSize++;
    }

    static long query(long x) {
        int lo = 0, hi = lineSize - 1;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (lineM[mid] * x + lineK[mid] < lineM[mid + 1] * x + lineK[mid + 1]) lo = mid + 1;
            else hi = mid;
        }
        return lineM[lo] * x + lineK[lo];
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
using namespace std;
typedef long long ll;

vector<ll> lineM, lineK;

bool bad(int l1, int l2, int l3) {
    return (__int128)(lineK[l1] - lineK[l2]) * (lineM[l3] - lineM[l2]) >= (__int128)(lineK[l2] - lineK[l3]) * (lineM[l2] - lineM[l1]);
}

void addLine(ll m, ll k) {
    lineM.push_back(m);
    lineK.push_back(k);
    int sz = lineM.size();
    while (sz >= 3 && bad(sz - 3, sz - 2, sz - 1)) {
        lineM[sz - 2] = lineM[sz - 1];
        lineK[sz - 2] = lineK[sz - 1];
        lineM.pop_back();
        lineK.pop_back();
        sz--;
    }
}

ll query(ll x) {
    int lo = 0, hi = lineM.size() - 1;
    while (lo < hi) {
        int mid = (lo + hi) / 2;
        if (lineM[mid] * x + lineK[mid] < lineM[mid + 1] * x + lineK[mid + 1]) lo = mid + 1;
        else hi = mid;
    }
    return lineM[lo] * x + lineK[lo];
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    ll a, b, c; cin >> a >> b >> c;
    vector<ll> x(n);
    for (int i = 0; i < n; i++) cin >> x[i];
    vector<ll> prefix(n + 1, 0);
    for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + x[i];
    vector<ll> dp(n + 1, 0);
    addLine(2 * a * prefix[0], dp[0] + a * prefix[0] * prefix[0] - b * prefix[0]);
    for (int i = 1; i <= n; i++) {
        ll si = prefix[i];
        dp[i] = a * si * si + b * si + c + query(si);
        addLine(2 * a * si, dp[i] + a * si * si - b * si);
    }
    cout << dp[n] << endl;
    return 0;
}
"""
        }
    ]

    # 문제 1434 (5213) - 과외맨
    solutions_1434 = [
        {
            "language": "python",
            "code": """import sys
from collections import deque
input = sys.stdin.readline

n = int(input())
totalTiles = n * n - n // 2
tiles = [None] * (totalTiles + 1)
for i in range(1, totalTiles + 1):
    a, b = map(int, input().split())
    tiles[i] = (a, b)

def getTilePosition(tileNum):
    count, row = 0, 0
    while count < tileNum:
        row += 1
        count += n if row % 2 == 1 else n - 1
    prevCount = count - (n if row % 2 == 1 else n - 1)
    offset = tileNum - prevCount - 1
    col = offset * 2 if row % 2 == 1 else offset * 2 + 1
    return row, col

def getTileAt(row, col):
    if row < 1 or row > n: return -1
    if row % 2 == 1:
        if col < 0 or col >= 2 * n: return -1
        tileInRow = col // 2
        if tileInRow >= n: return -1
    else:
        if col < 1 or col >= 2 * n - 1: return -1
        tileInRow = (col - 1) // 2
        if tileInRow >= n - 1: return -1
    prevTiles = 0
    for r in range(1, row):
        prevTiles += n if r % 2 == 1 else n - 1
    return prevTiles + tileInRow + 1

def getNeighbors(tileNum):
    neighbors = []
    row, col = getTilePosition(tileNum)
    leftVal, rightVal = tiles[tileNum]
    leftTile = getTileAt(row, col - 1)
    if leftTile != -1 and tiles[leftTile][1] == leftVal:
        neighbors.append(leftTile)
    rightTile = getTileAt(row, col + 2)
    if rightTile != -1 and tiles[rightTile][0] == rightVal:
        neighbors.append(rightTile)
    for dr in [-1, 1]:
        newRow = row + dr
        for dc in [-1, 1]:
            newTile = getTileAt(newRow, col + dc)
            if newTile != -1:
                ntRow, ntCol = getTilePosition(newTile)
                if col + dc == ntCol:
                    if (dc == -1 and tiles[newTile][0] == leftVal) or (dc == 1 and tiles[newTile][0] == rightVal):
                        neighbors.append(newTile)
                elif col + dc == ntCol + 1:
                    if (dc == -1 and tiles[newTile][1] == leftVal) or (dc == 1 and tiles[newTile][1] == rightVal):
                        neighbors.append(newTile)
    return neighbors

dist = [-1] * (totalTiles + 1)
parent = [-1] * (totalTiles + 1)
dist[1] = 1
queue = deque([1])
maxReachable = 1
while queue:
    curr = queue.popleft()
    if curr > maxReachable: maxReachable = curr
    for neighbor in getNeighbors(curr):
        if dist[neighbor] == -1:
            dist[neighbor] = dist[curr] + 1
            parent[neighbor] = curr
            queue.append(neighbor)

target = totalTiles if dist[totalTiles] != -1 else maxReachable
path = []
curr = target
while curr != -1:
    path.append(curr)
    curr = parent[curr]
path.reverse()
print(len(path))
print(' '.join(map(str, path)))
"""
        },
        {
            "language": "java",
            "code": """import java.io.*;
import java.util.*;

public class Main {
    static int n, totalTiles;
    static int[][] tiles;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        n = Integer.parseInt(br.readLine().trim());
        totalTiles = n * n - n / 2;
        tiles = new int[totalTiles + 1][2];
        for (int i = 1; i <= totalTiles; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            tiles[i][0] = Integer.parseInt(st.nextToken());
            tiles[i][1] = Integer.parseInt(st.nextToken());
        }
        int[] dist = new int[totalTiles + 1];
        int[] parent = new int[totalTiles + 1];
        Arrays.fill(dist, -1);
        Arrays.fill(parent, -1);
        dist[1] = 1;
        Queue<Integer> queue = new LinkedList<>();
        queue.offer(1);
        int maxReachable = 1;
        while (!queue.isEmpty()) {
            int curr = queue.poll();
            if (curr > maxReachable) maxReachable = curr;
            for (int neighbor : getNeighbors(curr)) {
                if (dist[neighbor] == -1) {
                    dist[neighbor] = dist[curr] + 1;
                    parent[neighbor] = curr;
                    queue.offer(neighbor);
                }
            }
        }
        int target = (dist[totalTiles] != -1) ? totalTiles : maxReachable;
        List<Integer> path = new ArrayList<>();
        int curr = target;
        while (curr != -1) { path.add(curr); curr = parent[curr]; }
        Collections.reverse(path);
        StringBuilder sb = new StringBuilder();
        sb.append(path.size()).append("\\n");
        for (int i = 0; i < path.size(); i++) {
            if (i > 0) sb.append(" ");
            sb.append(path.get(i));
        }
        System.out.println(sb);
    }

    static int[] getTilePosition(int tileNum) {
        int count = 0, row = 0;
        while (count < tileNum) { row++; count += (row % 2 == 1) ? n : n - 1; }
        int prevCount = count - ((row % 2 == 1) ? n : n - 1);
        int offset = tileNum - prevCount - 1;
        int col = (row % 2 == 1) ? offset * 2 : offset * 2 + 1;
        return new int[]{row, col};
    }

    static int getTileAt(int row, int col) {
        if (row < 1 || row > n) return -1;
        int tileInRow;
        if (row % 2 == 1) {
            if (col < 0 || col >= 2 * n) return -1;
            tileInRow = col / 2;
            if (tileInRow >= n) return -1;
        } else {
            if (col < 1 || col >= 2 * n - 1) return -1;
            tileInRow = (col - 1) / 2;
            if (tileInRow >= n - 1) return -1;
        }
        int prevTiles = 0;
        for (int r = 1; r < row; r++) prevTiles += (r % 2 == 1) ? n : n - 1;
        return prevTiles + tileInRow + 1;
    }

    static List<Integer> getNeighbors(int tileNum) {
        List<Integer> neighbors = new ArrayList<>();
        int[] pos = getTilePosition(tileNum);
        int row = pos[0], col = pos[1];
        int leftVal = tiles[tileNum][0], rightVal = tiles[tileNum][1];
        int leftTile = getTileAt(row, col - 1);
        if (leftTile != -1 && tiles[leftTile][1] == leftVal) neighbors.add(leftTile);
        int rightTile = getTileAt(row, col + 2);
        if (rightTile != -1 && tiles[rightTile][0] == rightVal) neighbors.add(rightTile);
        for (int dr : new int[]{-1, 1}) {
            int newRow = row + dr;
            for (int dc : new int[]{-1, 1}) {
                int newTile = getTileAt(newRow, col + dc);
                if (newTile != -1) {
                    int[] ntPos = getTilePosition(newTile);
                    int ntCol = ntPos[1];
                    if (col + dc == ntCol) {
                        if ((dc == -1 && tiles[newTile][0] == leftVal) || (dc == 1 && tiles[newTile][0] == rightVal)) neighbors.add(newTile);
                    } else if (col + dc == ntCol + 1) {
                        if ((dc == -1 && tiles[newTile][1] == leftVal) || (dc == 1 && tiles[newTile][1] == rightVal)) neighbors.add(newTile);
                    }
                }
            }
        }
        return neighbors;
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

int n, totalTiles;
vector<pair<int,int>> tiles;

pair<int,int> getTilePosition(int tileNum) {
    int count = 0, row = 0;
    while (count < tileNum) { row++; count += (row % 2 == 1) ? n : n - 1; }
    int prevCount = count - ((row % 2 == 1) ? n : n - 1);
    int offset = tileNum - prevCount - 1;
    int col = (row % 2 == 1) ? offset * 2 : offset * 2 + 1;
    return {row, col};
}

int getTileAt(int row, int col) {
    if (row < 1 || row > n) return -1;
    int tileInRow;
    if (row % 2 == 1) {
        if (col < 0 || col >= 2 * n) return -1;
        tileInRow = col / 2;
        if (tileInRow >= n) return -1;
    } else {
        if (col < 1 || col >= 2 * n - 1) return -1;
        tileInRow = (col - 1) / 2;
        if (tileInRow >= n - 1) return -1;
    }
    int prevTiles = 0;
    for (int r = 1; r < row; r++) prevTiles += (r % 2 == 1) ? n : n - 1;
    return prevTiles + tileInRow + 1;
}

vector<int> getNeighbors(int tileNum) {
    vector<int> neighbors;
    auto [row, col] = getTilePosition(tileNum);
    int leftVal = tiles[tileNum].first, rightVal = tiles[tileNum].second;
    int leftTile = getTileAt(row, col - 1);
    if (leftTile != -1 && tiles[leftTile].second == leftVal) neighbors.push_back(leftTile);
    int rightTile = getTileAt(row, col + 2);
    if (rightTile != -1 && tiles[rightTile].first == rightVal) neighbors.push_back(rightTile);
    for (int dr : {-1, 1}) {
        int newRow = row + dr;
        for (int dc : {-1, 1}) {
            int newTile = getTileAt(newRow, col + dc);
            if (newTile != -1) {
                auto [ntRow, ntCol] = getTilePosition(newTile);
                if (col + dc == ntCol) {
                    if ((dc == -1 && tiles[newTile].first == leftVal) || (dc == 1 && tiles[newTile].first == rightVal)) neighbors.push_back(newTile);
                } else if (col + dc == ntCol + 1) {
                    if ((dc == -1 && tiles[newTile].second == leftVal) || (dc == 1 && tiles[newTile].second == rightVal)) neighbors.push_back(newTile);
                }
            }
        }
    }
    return neighbors;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cin >> n;
    totalTiles = n * n - n / 2;
    tiles.resize(totalTiles + 1);
    for (int i = 1; i <= totalTiles; i++) cin >> tiles[i].first >> tiles[i].second;
    vector<int> dist(totalTiles + 1, -1), parent(totalTiles + 1, -1);
    dist[1] = 1;
    queue<int> q; q.push(1);
    int maxReachable = 1;
    while (!q.empty()) {
        int curr = q.front(); q.pop();
        if (curr > maxReachable) maxReachable = curr;
        for (int neighbor : getNeighbors(curr)) {
            if (dist[neighbor] == -1) {
                dist[neighbor] = dist[curr] + 1;
                parent[neighbor] = curr;
                q.push(neighbor);
            }
        }
    }
    int target = (dist[totalTiles] != -1) ? totalTiles : maxReachable;
    vector<int> path;
    int curr = target;
    while (curr != -1) { path.push_back(curr); curr = parent[curr]; }
    reverse(path.begin(), path.end());
    cout << path.size() << "\\n";
    for (int i = 0; i < (int)path.size(); i++) {
        if (i > 0) cout << " ";
        cout << path[i];
    }
    cout << endl;
    return 0;
}
"""
        }
    ]

    # 솔루션 적용
    problems[1379]['solutions'] = solutions_1379
    problems[1391]['solutions'] = solutions_1391
    problems[1393]['solutions'] = solutions_1393
    problems[1403]['solutions'] = solutions_1403
    problems[1410]['solutions'] = solutions_1410
    problems[1416]['solutions'] = solutions_1416
    problems[1424]['solutions'] = solutions_1424
    problems[1425]['solutions'] = solutions_1425
    problems[1427]['solutions'] = solutions_1427
    problems[1434]['solutions'] = solutions_1434

    # 저장
    with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'w', encoding='utf-8') as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)

    print("모든 솔루션 추가 완료!")
    print("처리된 문제:")
    for idx in [1379, 1391, 1393, 1403, 1410, 1416, 1424, 1425, 1427, 1434]:
        print(f"  Index {idx}: {problems[idx]['name']} - {len(problems[idx]['solutions'])} solutions")

if __name__ == "__main__":
    main()
