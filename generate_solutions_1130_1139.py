#!/usr/bin/env python3
"""
Generate solutions for Baekjoon problems 1130-1139 in Python, Java, and C++
"""

import json

def generate_solutions():
    """Generate solution codes for problems 1130-1139"""

    # Load problem data
    with open('data/baekjoon/checkpoint_1000_5073.json', 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    # Extract problems 1130-1139
    problems = {}
    for item in all_data:
        if 'original_id' in item and item['original_id'].isdigit():
            pid = int(item['original_id'])
            if 1130 <= pid <= 1139:
                problems[pid] = item

    # Generate solutions
    solutions = []

    for pid in sorted(problems.keys()):
        problem = problems[pid]
        print(f"\nProcessing Problem {pid}: {problem.get('name', '')}")

        solution_entry = {
            "original_id": str(pid),
            "solutions": []
        }

        # Generate solutions based on problem type
        if pid == 1130:  # Paper Racing - BFS problem
            solution_entry["solutions"] = generate_1130_solutions()
        elif pid == 1131:  # Numbers - Graph/DP problem
            solution_entry["solutions"] = generate_1131_solutions()
        elif pid == 1132:  # Sum - Greedy problem
            solution_entry["solutions"] = generate_1132_solutions()
        elif pid == 1133:  # Non-repeating words - Backtracking
            solution_entry["solutions"] = generate_1133_solutions()
        elif pid == 1134:  # Expression - Implementation/DP
            solution_entry["solutions"] = generate_1134_solutions()
        elif pid == 1135:  # News delivery - Tree DP
            solution_entry["solutions"] = generate_1135_solutions()
        elif pid == 1136:  # Piece placement - DP/Knapsack
            solution_entry["solutions"] = generate_1136_solutions()
        elif pid == 1137:  # Robot race - DP
            solution_entry["solutions"] = generate_1137_solutions()
        elif pid == 1138:  # Standing in line - Greedy
            solution_entry["solutions"] = generate_1138_solutions()
        elif pid == 1139:  # Fence - DP with bitmask
            solution_entry["solutions"] = generate_1139_solutions()

        solutions.append(solution_entry)

    # Output JSON
    print("\n" + "="*80)
    print("GENERATED SOLUTIONS JSON:")
    print("="*80)
    print(json.dumps(solutions, ensure_ascii=False, indent=2))

    return solutions


def generate_1130_solutions():
    """Problem 1130: Paper Racing - BFS with velocity tracking"""
    return [
        {
            "language": "python",
            "code": """from collections import deque

R, C = map(int, input().split())
grid = [input().strip() for _ in range(R)]
vx, vy = map(int, input().split())

# Find start and finish
start = finish = None
for i in range(R):
    for j in range(C):
        if grid[i][j] == 'S':
            start = (i, j)
        elif grid[i][j] == 'F':
            finish = (i, j)

# BFS with state (row, col, velocity_x, velocity_y)
queue = deque([(start[0], start[1], vx, vy, 0)])
visited = set()
visited.add((start[0], start[1], vx, vy))

while queue:
    r, c, dx, dy, dist = queue.popleft()

    if (r, c) == finish:
        print(dist)
        exit()

    # Try 9 possible acceleration changes (-1, 0, +1 in each direction)
    for ax in [-1, 0, 1]:
        for ay in [-1, 0, 1]:
            new_dx = dx + ax
            new_dy = dy + ay
            new_r = r + new_dx
            new_c = c + new_dy

            if 0 <= new_r < R and 0 <= new_c < C and grid[new_r][new_c] != 'X':
                state = (new_r, new_c, new_dx, new_dy)
                if state not in visited:
                    visited.add(state)
                    queue.append((new_r, new_c, new_dx, new_dy, dist + 1))

print(-1)
"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static class State {
        int r, c, dx, dy, dist;
        State(int r, int c, int dx, int dy, int dist) {
            this.r = r; this.c = c; this.dx = dx; this.dy = dy; this.dist = dist;
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] line = br.readLine().split(" ");
        int R = Integer.parseInt(line[0]);
        int C = Integer.parseInt(line[1]);

        char[][] grid = new char[R][C];
        int sr = 0, sc = 0, fr = 0, fc = 0;

        for (int i = 0; i < R; i++) {
            grid[i] = br.readLine().toCharArray();
            for (int j = 0; j < C; j++) {
                if (grid[i][j] == 'S') { sr = i; sc = j; }
                if (grid[i][j] == 'F') { fr = i; fc = j; }
            }
        }

        line = br.readLine().split(" ");
        int vx = Integer.parseInt(line[0]);
        int vy = Integer.parseInt(line[1]);

        Queue<State> queue = new LinkedList<>();
        Set<String> visited = new HashSet<>();

        queue.offer(new State(sr, sc, vx, vy, 0));
        visited.add(sr + "," + sc + "," + vx + "," + vy);

        while (!queue.isEmpty()) {
            State s = queue.poll();

            if (s.r == fr && s.c == fc) {
                System.out.println(s.dist);
                return;
            }

            for (int ax = -1; ax <= 1; ax++) {
                for (int ay = -1; ay <= 1; ay++) {
                    int ndx = s.dx + ax;
                    int ndy = s.dy + ay;
                    int nr = s.r + ndx;
                    int nc = s.c + ndy;

                    if (nr >= 0 && nr < R && nc >= 0 && nc < C && grid[nr][nc] != 'X') {
                        String key = nr + "," + nc + "," + ndx + "," + ndy;
                        if (!visited.contains(key)) {
                            visited.add(key);
                            queue.offer(new State(nr, nc, ndx, ndy, s.dist + 1));
                        }
                    }
                }
            }
        }

        System.out.println(-1);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <queue>
#include <set>
#include <vector>
using namespace std;

struct State {
    int r, c, dx, dy, dist;
};

int main() {
    int R, C;
    cin >> R >> C;

    vector<string> grid(R);
    int sr, sc, fr, fc, vx, vy;

    for (int i = 0; i < R; i++) {
        cin >> grid[i];
        for (int j = 0; j < C; j++) {
            if (grid[i][j] == 'S') { sr = i; sc = j; }
            if (grid[i][j] == 'F') { fr = i; fc = j; }
        }
    }

    cin >> vx >> vy;

    queue<State> q;
    set<tuple<int,int,int,int>> visited;

    q.push({sr, sc, vx, vy, 0});
    visited.insert({sr, sc, vx, vy});

    while (!q.empty()) {
        State s = q.front();
        q.pop();

        if (s.r == fr && s.c == fc) {
            cout << s.dist << endl;
            return 0;
        }

        for (int ax = -1; ax <= 1; ax++) {
            for (int ay = -1; ay <= 1; ay++) {
                int ndx = s.dx + ax;
                int ndy = s.dy + ay;
                int nr = s.r + ndx;
                int nc = s.c + ndy;

                if (nr >= 0 && nr < R && nc >= 0 && nc < C && grid[nr][nc] != 'X') {
                    auto key = make_tuple(nr, nc, ndx, ndy);
                    if (visited.find(key) == visited.end()) {
                        visited.insert(key);
                        q.push({nr, nc, ndx, ndy, s.dist + 1});
                    }
                }
            }
        }
    }

    cout << -1 << endl;
    return 0;
}
"""
        }
    ]


def generate_1131_solutions():
    """Problem 1131: Numbers - Finding minimum in sequence"""
    return [
        {
            "language": "python",
            "code": """def S_k(n, k):
    result = 0
    while n > 0:
        digit = n % 10
        result += digit ** k
        n //= 10
    return result

def find_min_in_sequence(n, k):
    visited = set()
    current = n
    min_val = current

    while current not in visited:
        visited.add(current)
        min_val = min(min_val, current)
        current = S_k(current, k)

    # After cycle detected, find minimum in cycle
    cycle_start = current
    cycle = [current]
    current = S_k(current, k)

    while current != cycle_start:
        cycle.append(current)
        current = S_k(current, k)

    return min(min_val, min(cycle))

A, B, K = map(int, input().split())
total = 0

for n in range(A, B + 1):
    total += find_min_in_sequence(n, K)

print(total)
"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static int S_k(int n, int k) {
        int result = 0;
        while (n > 0) {
            int digit = n % 10;
            result += (int)Math.pow(digit, k);
            n /= 10;
        }
        return result;
    }

    static int findMinInSequence(int n, int k) {
        Set<Integer> visited = new HashSet<>();
        int current = n;
        int minVal = current;

        while (!visited.contains(current)) {
            visited.add(current);
            minVal = Math.min(minVal, current);
            current = S_k(current, k);
        }

        int cycleStart = current;
        List<Integer> cycle = new ArrayList<>();
        cycle.add(current);
        current = S_k(current, k);

        while (current != cycleStart) {
            cycle.add(current);
            current = S_k(current, k);
        }

        for (int val : cycle) {
            minVal = Math.min(minVal, val);
        }

        return minVal;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] line = br.readLine().split(" ");
        int A = Integer.parseInt(line[0]);
        int B = Integer.parseInt(line[1]);
        int K = Integer.parseInt(line[2]);

        long total = 0;
        for (int n = A; n <= B; n++) {
            total += findMinInSequence(n, K);
        }

        System.out.println(total);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <set>
#include <vector>
#include <cmath>
#include <algorithm>
using namespace std;

int S_k(int n, int k) {
    int result = 0;
    while (n > 0) {
        int digit = n % 10;
        result += pow(digit, k);
        n /= 10;
    }
    return result;
}

int findMinInSequence(int n, int k) {
    set<int> visited;
    int current = n;
    int minVal = current;

    while (visited.find(current) == visited.end()) {
        visited.insert(current);
        minVal = min(minVal, current);
        current = S_k(current, k);
    }

    int cycleStart = current;
    vector<int> cycle;
    cycle.push_back(current);
    current = S_k(current, k);

    while (current != cycleStart) {
        cycle.push_back(current);
        current = S_k(current, k);
    }

    for (int val : cycle) {
        minVal = min(minVal, val);
    }

    return minVal;
}

int main() {
    int A, B, K;
    cin >> A >> B >> K;

    long long total = 0;
    for (int n = A; n <= B; n++) {
        total += findMinInSequence(n, K);
    }

    cout << total << endl;
    return 0;
}
"""
        }
    ]


def generate_1132_solutions():
    """Problem 1132: Sum - Greedy alphabet assignment"""
    return [
        {
            "language": "python",
            "code": """N = int(input())
words = [input().strip() for _ in range(N)]

# Track weight of each letter and which can't be 0
weights = [0] * 10
cant_be_zero = [False] * 10

for word in words:
    for i, ch in enumerate(word):
        idx = ord(ch) - ord('A')
        weights[idx] += 10 ** (len(word) - 1 - i)
        if i == 0 and len(word) > 1:
            cant_be_zero[idx] = True

# Create list of (weight, idx, cant_be_zero)
letters = [(weights[i], i, cant_be_zero[i]) for i in range(10) if weights[i] > 0]
letters.sort(reverse=True)

# Assign digits 9, 8, 7, ... to letters by weight
# But save 0 for the smallest weight that can be 0
assignment = [-1] * 10
digit = 9

# First assign all letters that can't be zero
for w, idx, cbz in letters:
    if cbz:
        assignment[idx] = digit
        digit -= 1

# Then assign remaining letters (those that can be zero)
for w, idx, cbz in letters:
    if not cbz:
        assignment[idx] = digit
        digit -= 1

# Calculate total
total = 0
for i in range(10):
    if assignment[i] != -1:
        total += weights[i] * assignment[i]

print(total)
"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static class Letter implements Comparable<Letter> {
        long weight;
        int idx;
        boolean cantBeZero;

        Letter(long w, int i, boolean c) {
            weight = w; idx = i; cantBeZero = c;
        }

        public int compareTo(Letter o) {
            return Long.compare(o.weight, this.weight);
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine());
        String[] words = new String[N];

        for (int i = 0; i < N; i++) {
            words[i] = br.readLine();
        }

        long[] weights = new long[10];
        boolean[] cantBeZero = new boolean[10];

        for (String word : words) {
            for (int i = 0; i < word.length(); i++) {
                int idx = word.charAt(i) - 'A';
                weights[idx] += Math.pow(10, word.length() - 1 - i);
                if (i == 0 && word.length() > 1) {
                    cantBeZero[idx] = true;
                }
            }
        }

        List<Letter> letters = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            if (weights[i] > 0) {
                letters.add(new Letter(weights[i], i, cantBeZero[i]));
            }
        }
        Collections.sort(letters);

        int[] assignment = new int[10];
        Arrays.fill(assignment, -1);
        int digit = 9;

        for (Letter l : letters) {
            if (l.cantBeZero) {
                assignment[l.idx] = digit--;
            }
        }

        for (Letter l : letters) {
            if (!l.cantBeZero) {
                assignment[l.idx] = digit--;
            }
        }

        long total = 0;
        for (int i = 0; i < 10; i++) {
            if (assignment[i] != -1) {
                total += weights[i] * assignment[i];
            }
        }

        System.out.println(total);
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <cmath>
using namespace std;

struct Letter {
    long long weight;
    int idx;
    bool cantBeZero;

    bool operator<(const Letter& o) const {
        return weight > o.weight;
    }
};

int main() {
    int N;
    cin >> N;

    vector<string> words(N);
    for (int i = 0; i < N; i++) {
        cin >> words[i];
    }

    long long weights[10] = {0};
    bool cantBeZero[10] = {false};

    for (const string& word : words) {
        for (int i = 0; i < word.length(); i++) {
            int idx = word[i] - 'A';
            weights[idx] += pow(10, word.length() - 1 - i);
            if (i == 0 && word.length() > 1) {
                cantBeZero[idx] = true;
            }
        }
    }

    vector<Letter> letters;
    for (int i = 0; i < 10; i++) {
        if (weights[i] > 0) {
            letters.push_back({weights[i], i, cantBeZero[i]});
        }
    }
    sort(letters.begin(), letters.end());

    int assignment[10];
    fill(assignment, assignment + 10, -1);
    int digit = 9;

    for (const Letter& l : letters) {
        if (l.cantBeZero) {
            assignment[l.idx] = digit--;
        }
    }

    for (const Letter& l : letters) {
        if (!l.cantBeZero) {
            assignment[l.idx] = digit--;
        }
    }

    long long total = 0;
    for (int i = 0; i < 10; i++) {
        if (assignment[i] != -1) {
            total += weights[i] * assignment[i];
        }
    }

    cout << total << endl;
    return 0;
}
"""
        }
    ]


def generate_1133_solutions():
    """Problem 1133: Non-repeating word - Backtracking"""
    return [
        {
            "language": "python",
            "code": """def solve():
    N, M = map(int, input().split())

    def backtrack(word, used):
        if len(word) == M:
            print(word)
            return True

        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:N]:
            # Check if placing c here violates non-repeating constraint
            valid = True
            for length in range(1, len(word) + 1):
                if len(word) >= length and word[-length:] == (word + c)[len(word) - length + 1:len(word) + 1]:
                    valid = False
                    break

            if valid:
                if backtrack(word + c, used | {c}):
                    return True

        return False

    if backtrack('', set()):
        pass
    else:
        print('NONE')

solve()
"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static int N, M;

    static boolean backtrack(StringBuilder word) {
        if (word.length() == M) {
            System.out.println(word);
            return true;
        }

        for (char c = 'A'; c < 'A' + N; c++) {
            boolean valid = true;

            for (int len = 1; len <= word.length(); len++) {
                if (word.length() >= len) {
                    String suffix = word.substring(word.length() - len);
                    String check = word.substring(word.length() - len + 1) + c;
                    if (suffix.equals(check)) {
                        valid = false;
                        break;
                    }
                }
            }

            if (valid) {
                word.append(c);
                if (backtrack(word)) return true;
                word.deleteCharAt(word.length() - 1);
            }
        }

        return false;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] line = br.readLine().split(" ");
        N = Integer.parseInt(line[0]);
        M = Integer.parseInt(line[1]);

        if (!backtrack(new StringBuilder())) {
            System.out.println("NONE");
        }
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <string>
using namespace std;

int N, M;

bool backtrack(string word) {
    if (word.length() == M) {
        cout << word << endl;
        return true;
    }

    for (char c = 'A'; c < 'A' + N; c++) {
        bool valid = true;

        for (int len = 1; len <= word.length(); len++) {
            if (word.length() >= len) {
                string suffix = word.substr(word.length() - len);
                string check = word.substr(word.length() - len + 1) + c;
                if (suffix == check) {
                    valid = false;
                    break;
                }
            }
        }

        if (valid) {
            if (backtrack(word + c)) return true;
        }
    }

    return false;
}

int main() {
    cin >> N >> M;

    if (!backtrack("")) {
        cout << "NONE" << endl;
    }

    return 0;
}
"""
        }
    ]


def generate_1134_solutions():
    """Problem 1134: Expression - DP/Brute force"""
    return [
        {
            "language": "python",
            "code": """def solve():
    expr = input().strip()
    target = int(input())

    # Parse numbers from expression
    nums = []
    i = 0
    while i < len(expr):
        if expr[i].isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            nums.append(int(expr[i:j]))
            i = j
        else:
            i += 1

    n = len(nums)
    if n == 1:
        print(1 if nums[0] == target else 0)
        return

    # Try all combinations of operators
    from itertools import product
    count = 0

    for ops in product(['+', '-', '*'], repeat=n-1):
        # Evaluate expression
        result = nums[0]
        for i, op in enumerate(ops):
            if op == '+':
                result += nums[i+1]
            elif op == '-':
                result -= nums[i+1]
            else:  # '*'
                result *= nums[i+1]

        if result == target:
            count += 1

    print(count)

solve()
"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static int count = 0;
    static int target;
    static int[] nums;
    static int n;

    static void solve(int idx, int result) {
        if (idx == n) {
            if (result == target) count++;
            return;
        }

        solve(idx + 1, result + nums[idx]);
        solve(idx + 1, result - nums[idx]);
        solve(idx + 1, result * nums[idx]);
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String expr = br.readLine();
        target = Integer.parseInt(br.readLine());

        List<Integer> numList = new ArrayList<>();
        int i = 0;
        while (i < expr.length()) {
            if (Character.isDigit(expr.charAt(i))) {
                int j = i;
                while (j < expr.length() && Character.isDigit(expr.charAt(j))) {
                    j++;
                }
                numList.add(Integer.parseInt(expr.substring(i, j)));
                i = j;
            } else {
                i++;
            }
        }

        nums = new int[numList.size()];
        for (i = 0; i < numList.size(); i++) {
            nums[i] = numList.get(i);
        }
        n = nums.length;

        if (n == 1) {
            System.out.println(nums[0] == target ? 1 : 0);
        } else {
            solve(1, nums[0]);
            System.out.println(count);
        }
    }
}
"""
        },
        {
            "language": "cpp",
            "code": """#include <iostream>
#include <vector>
#include <string>
#include <cctype>
using namespace std;

int cnt = 0;
int target;
vector<int> nums;
int n;

void solve(int idx, int result) {
    if (idx == n) {
        if (result == target) cnt++;
        return;
    }

    solve(idx + 1, result + nums[idx]);
    solve(idx + 1, result - nums[idx]);
    solve(idx + 1, result * nums[idx]);
}

int main() {
    string expr;
    getline(cin, expr);
    cin >> target;

    int i = 0;
    while (i < expr.length()) {
        if (isdigit(expr[i])) {
            int j = i;
            while (j < expr.length() && isdigit(expr[j])) {
                j++;
            }
            nums.push_back(stoi(expr.substr(i, j - i)));
            i = j;
        } else {
            i++;
        }
    }

    n = nums.size();

    if (n == 1) {
        cout << (nums[0] == target ? 1 : 0) << endl;
    } else {
        solve(1, nums[0]);
        cout << cnt << endl;
    }

    return 0;
}
"""
        }
    ]


def generate_1135_solutions():
    """Problem 1135: News delivery - Tree DP with greedy"""
    return [
        {
            "language": "python",
            "code": """import sys
sys.setrecursionlimit(100000)

N = int(input())
parent = list(map(int, input().split()))

# Build adjacency list for children
children = [[] for _ in range(N)]
for i in range(1, N):
    children[parent[i]].append(i)

def dfs(node):
    if not children[node]:
        return 0

    # Get time for each child subtree
    child_times = []
    for child in children[node]:
        child_times.append(dfs(child))

    # Sort in descending order - call employees who take longer first
    child_times.sort(reverse=True)

    # Calculate total time
    max_time = 0
    for i, time in enumerate(child_times):
        # Each call takes 1 minute, plus the time for that subtree
        # i-th call happens at minute i+1
        max_time = max(max_time, (i + 1) + time)

    return max_time

print(dfs(0))
"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    static List<Integer>[] children;

    static int dfs(int node) {
        if (children[node].isEmpty()) {
            return 0;
        }

        List<Integer> childTimes = new ArrayList<>();
        for (int child : children[node]) {
            childTimes.add(dfs(child));
        }

        Collections.sort(childTimes, Collections.reverseOrder());

        int maxTime = 0;
        for (int i = 0; i < childTimes.size(); i++) {
            maxTime = Math.max(maxTime, (i + 1) + childTimes.get(i));
        }

        return maxTime;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine());
        String[] line = br.readLine().split(" ");

        children = new ArrayList[N];
        for (int i = 0; i < N; i++) {
            children[i] = new ArrayList<>();
        }

        for (int i = 0; i < N; i++) {
            int p = Integer.parseInt(line[i]);
            if (p != -1) {
                children[p].add(i);
            }
        }

        System.out.println(dfs(0));
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

vector<int> children[50];

int dfs(int node) {
    if (children[node].empty()) {
        return 0;
    }

    vector<int> childTimes;
    for (int child : children[node]) {
        childTimes.push_back(dfs(child));
    }

    sort(childTimes.rbegin(), childTimes.rend());

    int maxTime = 0;
    for (int i = 0; i < childTimes.size(); i++) {
        maxTime = max(maxTime, (i + 1) + childTimes[i]);
    }

    return maxTime;
}

int main() {
    int N;
    cin >> N;

    for (int i = 0; i < N; i++) {
        int p;
        cin >> p;
        if (p != -1) {
            children[p].push_back(i);
        }
    }

    cout << dfs(0) << endl;
    return 0;
}
"""
        }
    ]


def generate_1136_solutions():
    """Problem 1136: Piece placement - DP/Knapsack"""
    return [
        {
            "language": "python",
            "code": """N, K = map(int, input().split())
pieces = []
for _ in range(N):
    a, b = map(int, input().split())
    pieces.append((a, b))

# DP: dp[i][j] = max value using first i pieces with exactly j weight
INF = float('-inf')
dp = [[INF] * (K + 1) for _ in range(N + 1)]
dp[0][0] = 0

for i in range(N):
    a, b = pieces[i]
    for j in range(K + 1):
        if dp[i][j] == INF:
            continue
        # Don't use this piece
        dp[i + 1][j] = max(dp[i + 1][j], dp[i][j])
        # Use this piece
        if j + a <= K:
            dp[i + 1][j + a] = max(dp[i + 1][j + a], dp[i][j] + b)

result = max(dp[N])
print(result if result != INF else -1)
"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] line = br.readLine().split(" ");
        int N = Integer.parseInt(line[0]);
        int K = Integer.parseInt(line[1]);

        int[][] pieces = new int[N][2];
        for (int i = 0; i < N; i++) {
            line = br.readLine().split(" ");
            pieces[i][0] = Integer.parseInt(line[0]);
            pieces[i][1] = Integer.parseInt(line[1]);
        }

        final int INF = Integer.MIN_VALUE / 2;
        int[][] dp = new int[N + 1][K + 1];
        for (int i = 0; i <= N; i++) {
            Arrays.fill(dp[i], INF);
        }
        dp[0][0] = 0;

        for (int i = 0; i < N; i++) {
            int a = pieces[i][0];
            int b = pieces[i][1];
            for (int j = 0; j <= K; j++) {
                if (dp[i][j] == INF) continue;
                dp[i + 1][j] = Math.max(dp[i + 1][j], dp[i][j]);
                if (j + a <= K) {
                    dp[i + 1][j + a] = Math.max(dp[i + 1][j + a], dp[i][j] + b);
                }
            }
        }

        int result = INF;
        for (int j = 0; j <= K; j++) {
            result = Math.max(result, dp[N][j]);
        }

        System.out.println(result == INF ? -1 : result);
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

const int INF = -1e9;

int main() {
    int N, K;
    cin >> N >> K;

    vector<pair<int,int>> pieces(N);
    for (int i = 0; i < N; i++) {
        cin >> pieces[i].first >> pieces[i].second;
    }

    vector<vector<int>> dp(N + 1, vector<int>(K + 1, INF));
    dp[0][0] = 0;

    for (int i = 0; i < N; i++) {
        int a = pieces[i].first;
        int b = pieces[i].second;
        for (int j = 0; j <= K; j++) {
            if (dp[i][j] == INF) continue;
            dp[i + 1][j] = max(dp[i + 1][j], dp[i][j]);
            if (j + a <= K) {
                dp[i + 1][j + a] = max(dp[i + 1][j + a], dp[i][j] + b);
            }
        }
    }

    int result = INF;
    for (int j = 0; j <= K; j++) {
        result = max(result, dp[N][j]);
    }

    cout << (result == INF ? -1 : result) << endl;
    return 0;
}
"""
        }
    ]


def generate_1137_solutions():
    """Problem 1137: Robot race - DP"""
    return [
        {
            "language": "python",
            "code": """N = int(input())
obstacles = []
for _ in range(N):
    x, y = map(int, input().split())
    obstacles.append((x, y))

# Sort by x coordinate
obstacles.sort()

# DP: for each obstacle, find longest path ending there
dp = [1] * N

for i in range(N):
    for j in range(i):
        # Can go from j to i if j is to the left and below
        if obstacles[j][0] < obstacles[i][0] and obstacles[j][1] < obstacles[i][1]:
            dp[i] = max(dp[i], dp[j] + 1)

print(max(dp) if dp else 0)
"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine());

        int[][] obstacles = new int[N][2];
        for (int i = 0; i < N; i++) {
            String[] line = br.readLine().split(" ");
            obstacles[i][0] = Integer.parseInt(line[0]);
            obstacles[i][1] = Integer.parseInt(line[1]);
        }

        Arrays.sort(obstacles, (a, b) -> a[0] - b[0]);

        int[] dp = new int[N];
        Arrays.fill(dp, 1);

        for (int i = 0; i < N; i++) {
            for (int j = 0; j < i; j++) {
                if (obstacles[j][0] < obstacles[i][0] && obstacles[j][1] < obstacles[i][1]) {
                    dp[i] = Math.max(dp[i], dp[j] + 1);
                }
            }
        }

        int result = 0;
        for (int x : dp) {
            result = Math.max(result, x);
        }

        System.out.println(result);
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
    int N;
    cin >> N;

    vector<pair<int,int>> obstacles(N);
    for (int i = 0; i < N; i++) {
        cin >> obstacles[i].first >> obstacles[i].second;
    }

    sort(obstacles.begin(), obstacles.end());

    vector<int> dp(N, 1);

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < i; j++) {
            if (obstacles[j].first < obstacles[i].first && obstacles[j].second < obstacles[i].second) {
                dp[i] = max(dp[i], dp[j] + 1);
            }
        }
    }

    int result = 0;
    for (int x : dp) {
        result = max(result, x);
    }

    cout << result << endl;
    return 0;
}
"""
        }
    ]


def generate_1138_solutions():
    """Problem 1138: Standing in line - Greedy implementation"""
    return [
        {
            "language": "python",
            "code": """N = int(input())
taller = list(map(int, input().split()))

# Result array
result = [0] * N

# Place people from tallest to shortest (N down to 1)
for person in range(N, 0, -1):
    count = taller[person - 1]

    # Find the (count+1)-th empty position from left
    empty_count = 0
    for i in range(N):
        if result[i] == 0:
            if empty_count == count:
                result[i] = person
                break
            empty_count += 1

print(' '.join(map(str, result)))
"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine());
        String[] line = br.readLine().split(" ");

        int[] taller = new int[N];
        for (int i = 0; i < N; i++) {
            taller[i] = Integer.parseInt(line[i]);
        }

        int[] result = new int[N];

        for (int person = N; person >= 1; person--) {
            int count = taller[person - 1];
            int emptyCount = 0;

            for (int i = 0; i < N; i++) {
                if (result[i] == 0) {
                    if (emptyCount == count) {
                        result[i] = person;
                        break;
                    }
                    emptyCount++;
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < N; i++) {
            sb.append(result[i]);
            if (i < N - 1) sb.append(" ");
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
    int N;
    cin >> N;

    vector<int> taller(N);
    for (int i = 0; i < N; i++) {
        cin >> taller[i];
    }

    vector<int> result(N, 0);

    for (int person = N; person >= 1; person--) {
        int count = taller[person - 1];
        int emptyCount = 0;

        for (int i = 0; i < N; i++) {
            if (result[i] == 0) {
                if (emptyCount == count) {
                    result[i] = person;
                    break;
                }
                emptyCount++;
            }
        }
    }

    for (int i = 0; i < N; i++) {
        cout << result[i];
        if (i < N - 1) cout << " ";
    }
    cout << endl;

    return 0;
}
"""
        }
    ]


def generate_1139_solutions():
    """Problem 1139: Fence - DP with bitmask"""
    return [
        {
            "language": "python",
            "code": """def solve():
    N = int(input())
    fence = []
    for _ in range(N):
        fence.append(int(input()))

    # DP with bitmask: dp[mask] = min cost to paint posts in mask
    INF = float('inf')
    dp = [INF] * (1 << N)
    dp[0] = 0

    for mask in range(1 << N):
        if dp[mask] == INF:
            continue

        # Find first unpainted post
        first = -1
        for i in range(N):
            if not (mask & (1 << i)):
                first = i
                break

        if first == -1:
            continue

        # Try painting consecutive posts starting from first
        cost = 0
        for length in range(1, N - first + 1):
            if first + length - 1 >= N:
                break

            # Check if all posts in range are unpainted
            valid = True
            for j in range(first, first + length):
                if mask & (1 << j):
                    valid = False
                    break

            if not valid:
                break

            cost += fence[first + length - 1]
            new_mask = mask
            for j in range(first, first + length):
                new_mask |= (1 << j)

            dp[new_mask] = min(dp[new_mask], dp[mask] + cost)

    print(dp[(1 << N) - 1])

solve()
"""
        },
        {
            "language": "java",
            "code": """import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine());

        int[] fence = new int[N];
        for (int i = 0; i < N; i++) {
            fence[i] = Integer.parseInt(br.readLine());
        }

        final int INF = Integer.MAX_VALUE / 2;
        int[] dp = new int[1 << N];
        Arrays.fill(dp, INF);
        dp[0] = 0;

        for (int mask = 0; mask < (1 << N); mask++) {
            if (dp[mask] == INF) continue;

            int first = -1;
            for (int i = 0; i < N; i++) {
                if ((mask & (1 << i)) == 0) {
                    first = i;
                    break;
                }
            }

            if (first == -1) continue;

            int cost = 0;
            for (int length = 1; length <= N - first; length++) {
                if (first + length - 1 >= N) break;

                boolean valid = true;
                for (int j = first; j < first + length; j++) {
                    if ((mask & (1 << j)) != 0) {
                        valid = false;
                        break;
                    }
                }

                if (!valid) break;

                cost += fence[first + length - 1];
                int newMask = mask;
                for (int j = first; j < first + length; j++) {
                    newMask |= (1 << j);
                }

                dp[newMask] = Math.min(dp[newMask], dp[mask] + cost);
            }
        }

        System.out.println(dp[(1 << N) - 1]);
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

const int INF = 1e9;

int main() {
    int N;
    cin >> N;

    vector<int> fence(N);
    for (int i = 0; i < N; i++) {
        cin >> fence[i];
    }

    vector<int> dp(1 << N, INF);
    dp[0] = 0;

    for (int mask = 0; mask < (1 << N); mask++) {
        if (dp[mask] == INF) continue;

        int first = -1;
        for (int i = 0; i < N; i++) {
            if ((mask & (1 << i)) == 0) {
                first = i;
                break;
            }
        }

        if (first == -1) continue;

        int cost = 0;
        for (int length = 1; length <= N - first; length++) {
            if (first + length - 1 >= N) break;

            bool valid = true;
            for (int j = first; j < first + length; j++) {
                if (mask & (1 << j)) {
                    valid = false;
                    break;
                }
            }

            if (!valid) break;

            cost += fence[first + length - 1];
            int newMask = mask;
            for (int j = first; j < first + length; j++) {
                newMask |= (1 << j);
            }

            dp[newMask] = min(dp[newMask], dp[mask] + cost);
        }
    }

    cout << dp[(1 << N) - 1] << endl;
    return 0;
}
"""
        }
    ]


if __name__ == "__main__":
    generate_solutions()
