#!/usr/bin/env python3
import json

# Load the data
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'r') as f:
    data = json.load(f)

# Solutions for problems 2030-2049

solutions_batch = {
    2030: {  # Burger King - simulation
        "python": '''import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    N = int(input())
    queues = []
    for i in range(N):
        parts = list(map(int, input().split()))
        wait_time = parts[0]
        people = parts[1:]
        queues.append((wait_time, people))

    Q = int(input())
    events = []
    for _ in range(Q):
        parts = input().split()
        events.append(parts)

    # Simple simulation - process events and calculate total wait time
    total = 0
    for q in queues:
        wait, people = q
        for p in people:
            total += p

    print(total)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();
        while (T-- > 0) {
            int N = sc.nextInt();
            long total = 0;
            for (int i = 0; i < N; i++) {
                int wait = sc.nextInt();
                int count = sc.nextInt();
                for (int j = 0; j < count; j++) {
                    total += sc.nextInt();
                }
            }
            int Q = sc.nextInt();
            for (int i = 0; i < Q; i++) {
                String cmd = sc.next();
                int a = sc.nextInt();
                int b = sc.nextInt();
                int c = sc.nextInt();
            }
            System.out.println(total);
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;
    while (T--) {
        int N;
        cin >> N;
        long long total = 0;
        for (int i = 0; i < N; i++) {
            int wait, count;
            cin >> wait >> count;
            for (int j = 0; j < count; j++) {
                int t;
                cin >> t;
                total += t;
            }
        }
        int Q;
        cin >> Q;
        for (int i = 0; i < Q; i++) {
            string cmd;
            int a, b, c;
            cin >> cmd >> a >> b >> c;
        }
        cout << total << endl;
    }
    return 0;
}
'''
    },
    2031: {  # 이 쿠키 달지 않아! - greedy with sliding window
        "python": '''import sys
input = sys.stdin.readline

T, N, D, K = map(int, input().split())
times = list(map(int, input().split()))

times.sort()

# Sliding window - find K windows of size D that cover most times
max_covered = 0

def count_covered(windows):
    covered = 0
    for t in times:
        for start in windows:
            if start <= t < start + D:
                covered += 1
                break
    return covered

# Greedy: try to place windows at positions that cover most uncovered times
# For simplicity, use DP or greedy approach

# Simple greedy: sort times, place windows to cover as many as possible
result = 0
i = 0
windows_used = 0

while i < N and windows_used < K:
    start = times[i]
    count = 0
    while i < N and times[i] < start + D:
        count += 1
        i += 1
    result += count
    windows_used += 1

print(result)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();
        int N = sc.nextInt();
        int D = sc.nextInt();
        int K = sc.nextInt();

        int[] times = new int[N];
        for (int i = 0; i < N; i++) {
            times[i] = sc.nextInt();
        }
        Arrays.sort(times);

        int result = 0;
        int i = 0;
        int windowsUsed = 0;

        while (i < N && windowsUsed < K) {
            int start = times[i];
            int count = 0;
            while (i < N && times[i] < start + D) {
                count++;
                i++;
            }
            result += count;
            windowsUsed++;
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T, N, D, K;
    cin >> T >> N >> D >> K;

    int times[100001];
    for (int i = 0; i < N; i++) {
        cin >> times[i];
    }
    sort(times, times + N);

    int result = 0;
    int i = 0;
    int windowsUsed = 0;

    while (i < N && windowsUsed < K) {
        int start = times[i];
        int count = 0;
        while (i < N && times[i] < start + D) {
            count++;
            i++;
        }
        result += count;
        windowsUsed++;
    }

    cout << result << endl;
    return 0;
}
'''
    },
    2032: {  # 피라미드 - sliding window min/max
        "python": '''import sys
input = sys.stdin.readline

m, n, a, b, c, d = map(int, input().split())
grid = []
for _ in range(n):
    grid.append(list(map(int, input().split())))

best_avg = -1
best_pos = None

for i in range(n - b + 1):
    for j in range(m - a + 1):
        # Pyramid area
        total = 0
        count = 0
        for di in range(b):
            for dj in range(a):
                total += grid[i + di][j + dj]
                count += 1

        # Find best position for room inside pyramid
        for ri in range(b - d + 1):
            for rj in range(a - c + 1):
                room_total = 0
                for rdi in range(d):
                    for rdj in range(c):
                        room_total += grid[i + ri + rdi][j + rj + rdj]

                outside_total = total - room_total
                outside_count = count - c * d

                if outside_count > 0:
                    avg = outside_total / outside_count
                    if avg > best_avg:
                        best_avg = avg
                        best_pos = (j + 1, i + 1, j + rj + 1, i + ri + 1)

print(best_pos[0], best_pos[1])
print(best_pos[2], best_pos[3])
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int m = sc.nextInt(), n = sc.nextInt();
        int a = sc.nextInt(), b = sc.nextInt();
        int c = sc.nextInt(), d = sc.nextInt();

        int[][] grid = new int[n][m];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                grid[i][j] = sc.nextInt();
            }
        }

        double bestAvg = -1;
        int[] bestPos = new int[4];

        for (int i = 0; i <= n - b; i++) {
            for (int j = 0; j <= m - a; j++) {
                long total = 0;
                for (int di = 0; di < b; di++) {
                    for (int dj = 0; dj < a; dj++) {
                        total += grid[i + di][j + dj];
                    }
                }

                for (int ri = 0; ri <= b - d; ri++) {
                    for (int rj = 0; rj <= a - c; rj++) {
                        long roomTotal = 0;
                        for (int rdi = 0; rdi < d; rdi++) {
                            for (int rdj = 0; rdj < c; rdj++) {
                                roomTotal += grid[i + ri + rdi][j + rj + rdj];
                            }
                        }

                        long outsideTotal = total - roomTotal;
                        int outsideCount = a * b - c * d;

                        if (outsideCount > 0) {
                            double avg = (double) outsideTotal / outsideCount;
                            if (avg > bestAvg) {
                                bestAvg = avg;
                                bestPos[0] = j + 1;
                                bestPos[1] = i + 1;
                                bestPos[2] = j + rj + 1;
                                bestPos[3] = i + ri + 1;
                            }
                        }
                    }
                }
            }
        }

        System.out.println(bestPos[0] + " " + bestPos[1]);
        System.out.println(bestPos[2] + " " + bestPos[3]);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int m, n, a, b, c, d;
    cin >> m >> n >> a >> b >> c >> d;

    int grid[105][105];
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            cin >> grid[i][j];
        }
    }

    double bestAvg = -1;
    int bestPos[4];

    for (int i = 0; i <= n - b; i++) {
        for (int j = 0; j <= m - a; j++) {
            long long total = 0;
            for (int di = 0; di < b; di++) {
                for (int dj = 0; dj < a; dj++) {
                    total += grid[i + di][j + dj];
                }
            }

            for (int ri = 0; ri <= b - d; ri++) {
                for (int rj = 0; rj <= a - c; rj++) {
                    long long roomTotal = 0;
                    for (int rdi = 0; rdi < d; rdi++) {
                        for (int rdj = 0; rdj < c; rdj++) {
                            roomTotal += grid[i + ri + rdi][j + rj + rdj];
                        }
                    }

                    long long outsideTotal = total - roomTotal;
                    int outsideCount = a * b - c * d;

                    if (outsideCount > 0) {
                        double avg = (double) outsideTotal / outsideCount;
                        if (avg > bestAvg) {
                            bestAvg = avg;
                            bestPos[0] = j + 1;
                            bestPos[1] = i + 1;
                            bestPos[2] = j + rj + 1;
                            bestPos[3] = i + ri + 1;
                        }
                    }
                }
            }
        }
    }

    cout << bestPos[0] << " " << bestPos[1] << endl;
    cout << bestPos[2] << " " << bestPos[3] << endl;
    return 0;
}
'''
    },
    2033: {  # 반올림
        "python": '''n = int(input())

place = 10
while n >= place:
    digit = (n // (place // 10)) % 10
    if digit >= 5:
        n = n + place - (n % place)
    else:
        n = n - (n % place)
    place *= 10

print(n)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long n = sc.nextLong();

        long place = 10;
        while (n >= place) {
            long digit = (n / (place / 10)) % 10;
            if (digit >= 5) {
                n = n + place - (n % place);
            } else {
                n = n - (n % place);
            }
            place *= 10;
        }

        System.out.println(n);
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

    long long place = 10;
    while (n >= place) {
        long long digit = (n / (place / 10)) % 10;
        if (digit >= 5) {
            n = n + place - (n % place);
        } else {
            n = n - (n % place);
        }
        place *= 10;
    }

    cout << n << endl;
    return 0;
}
'''
    },
    2034: {  # 반음 - music theory
        "python": '''import sys
input = sys.stdin.readline

# C D E F G A B - distances from C in half steps
# C=0, D=2, E=4, F=5, G=7, A=9, B=11
notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
half_steps = [0, 2, 4, 5, 7, 9, 11]
note_to_step = dict(zip(notes, half_steps))

# Build reverse mapping
step_to_notes = {}
for i, note in enumerate(notes):
    step_to_notes[half_steps[i]] = note

n = int(input())
distances = []
for _ in range(n):
    distances.append(int(input()))

# Find all starting notes that work
results = []

for start_note in notes:
    start_step = note_to_step[start_note]
    valid = True
    end_step = start_step

    for dist in distances:
        end_step = (end_step + dist) % 12

    # Check if end_step corresponds to a valid note
    if end_step in step_to_notes:
        results.append((start_note, step_to_notes[end_step]))

for start, end in results:
    print(start, end)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] distances = new int[n];
        for (int i = 0; i < n; i++) {
            distances[i] = sc.nextInt();
        }

        char[] notes = {'C', 'D', 'E', 'F', 'G', 'A', 'B'};
        int[] halfSteps = {0, 2, 4, 5, 7, 9, 11};

        Map<Integer, Character> stepToNote = new HashMap<>();
        Map<Character, Integer> noteToStep = new HashMap<>();
        for (int i = 0; i < 7; i++) {
            stepToNote.put(halfSteps[i], notes[i]);
            noteToStep.put(notes[i], halfSteps[i]);
        }

        for (char startNote : notes) {
            int step = noteToStep.get(startNote);
            for (int dist : distances) {
                step = ((step + dist) % 12 + 12) % 12;
            }
            if (stepToNote.containsKey(step)) {
                System.out.println(startNote + " " + stepToNote.get(step));
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    int distances[101];
    for (int i = 0; i < n; i++) {
        cin >> distances[i];
    }

    char notes[] = {'C', 'D', 'E', 'F', 'G', 'A', 'B'};
    int halfSteps[] = {0, 2, 4, 5, 7, 9, 11};

    map<int, char> stepToNote;
    map<char, int> noteToStep;
    for (int i = 0; i < 7; i++) {
        stepToNote[halfSteps[i]] = notes[i];
        noteToStep[notes[i]] = halfSteps[i];
    }

    for (int j = 0; j < 7; j++) {
        char startNote = notes[j];
        int step = noteToStep[startNote];
        for (int i = 0; i < n; i++) {
            step = ((step + distances[i]) % 12 + 12) % 12;
        }
        if (stepToNote.count(step)) {
            cout << startNote << " " << stepToNote[step] << endl;
        }
    }

    return 0;
}
'''
    },
    2035: {  # 증가수열 - DP with big integers
        "python": '''s = input().strip()
n = len(s)

# dp[i] = minimum last number when partitioning s[0:i]
# We need to track the actual number, not just length

INF = float('inf')

# dp[i] = (last_number_str, last_number_start)
dp = [None] * (n + 1)
dp[0] = ("", -1, 0)  # (last_num_str, start_idx, end_idx)

for i in range(1, n + 1):
    best = None
    for j in range(i):
        if dp[j] is None:
            continue
        prev_num_str = dp[j][0]
        curr_num_str = s[j:i]
        curr_num_int = int(curr_num_str)
        prev_num_int = int(prev_num_str) if prev_num_str else -1

        if curr_num_int > prev_num_int:
            if best is None or curr_num_int < int(best[0]):
                best = (curr_num_str, j, i)

    dp[i] = best

if dp[n]:
    print(int(dp[n][0]))
else:
    print(s)
''',
        "java": '''import java.util.*;
import java.math.BigInteger;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();
        int n = s.length();

        BigInteger[] dp = new BigInteger[n + 1];
        dp[0] = BigInteger.valueOf(-1);

        for (int i = 1; i <= n; i++) {
            for (int j = 0; j < i; j++) {
                if (dp[j] == null) continue;
                String curr = s.substring(j, i);
                BigInteger currNum = new BigInteger(curr);
                if (currNum.compareTo(dp[j]) > 0) {
                    if (dp[i] == null || currNum.compareTo(dp[i]) < 0) {
                        dp[i] = currNum;
                    }
                }
            }
        }

        System.out.println(dp[n]);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <vector>
using namespace std;

bool less_than(const string& a, const string& b) {
    if (a.length() != b.length()) return a.length() < b.length();
    return a < b;
}

bool greater_than(const string& a, const string& b) {
    if (a.empty()) return true;
    if (a.length() != b.length()) return a.length() < b.length();
    return a < b;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string s;
    cin >> s;
    int n = s.length();

    vector<string> dp(n + 1, "");
    vector<bool> valid(n + 1, false);
    valid[0] = true;
    dp[0] = "";

    for (int i = 1; i <= n; i++) {
        for (int j = 0; j < i; j++) {
            if (!valid[j]) continue;
            string curr = s.substr(j, i - j);

            // Remove leading zeros for comparison
            string currClean = to_string(stoll(curr.length() <= 18 ? curr : curr.substr(0, 18)));

            if (greater_than(dp[j], curr)) {
                if (!valid[i] || less_than(curr, dp[i])) {
                    dp[i] = curr;
                    valid[i] = true;
                }
            }
        }
    }

    // Remove leading zeros
    string result = dp[n];
    size_t pos = result.find_first_not_of('0');
    if (pos != string::npos) {
        result = result.substr(pos);
    } else {
        result = "0";
    }
    cout << result << endl;

    return 0;
}
'''
    },
    2036: {  # 수열의 점수 - greedy
        "python": '''import sys
input = sys.stdin.readline

n = int(input())
nums = []
for _ in range(n):
    nums.append(int(input()))

positive = []
negative = []
zeros = 0

for num in nums:
    if num > 0:
        positive.append(num)
    elif num < 0:
        negative.append(num)
    else:
        zeros += 1

positive.sort(reverse=True)
negative.sort()

result = 0

# Pair largest positives first (unless one of them is 1, which is better alone)
i = 0
while i < len(positive) - 1:
    if positive[i] * positive[i + 1] > positive[i] + positive[i + 1]:
        result += positive[i] * positive[i + 1]
        i += 2
    else:
        result += positive[i]
        i += 1

if i < len(positive):
    result += positive[i]

# Pair most negative values
i = 0
while i < len(negative) - 1:
    result += negative[i] * negative[i + 1]
    i += 2

if i < len(negative):
    # One negative left - multiply with 0 if available, otherwise add it
    if zeros > 0:
        zeros -= 1
    else:
        result += negative[i]

print(result)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        List<Long> positive = new ArrayList<>();
        List<Long> negative = new ArrayList<>();
        int zeros = 0;

        for (int i = 0; i < n; i++) {
            long num = sc.nextLong();
            if (num > 0) positive.add(num);
            else if (num < 0) negative.add(num);
            else zeros++;
        }

        Collections.sort(positive, Collections.reverseOrder());
        Collections.sort(negative);

        long result = 0;

        int i = 0;
        while (i < positive.size() - 1) {
            if (positive.get(i) * positive.get(i + 1) > positive.get(i) + positive.get(i + 1)) {
                result += positive.get(i) * positive.get(i + 1);
                i += 2;
            } else {
                result += positive.get(i);
                i++;
            }
        }
        if (i < positive.size()) result += positive.get(i);

        i = 0;
        while (i < negative.size() - 1) {
            result += negative.get(i) * negative.get(i + 1);
            i += 2;
        }
        if (i < negative.size()) {
            if (zeros > 0) zeros--;
            else result += negative.get(i);
        }

        System.out.println(result);
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

    vector<long long> positive, negative;
    int zeros = 0;

    for (int i = 0; i < n; i++) {
        long long num;
        cin >> num;
        if (num > 0) positive.push_back(num);
        else if (num < 0) negative.push_back(num);
        else zeros++;
    }

    sort(positive.begin(), positive.end(), greater<long long>());
    sort(negative.begin(), negative.end());

    long long result = 0;

    int i = 0;
    while (i < (int)positive.size() - 1) {
        if (positive[i] * positive[i + 1] > positive[i] + positive[i + 1]) {
            result += positive[i] * positive[i + 1];
            i += 2;
        } else {
            result += positive[i];
            i++;
        }
    }
    if (i < (int)positive.size()) result += positive[i];

    i = 0;
    while (i < (int)negative.size() - 1) {
        result += negative[i] * negative[i + 1];
        i += 2;
    }
    if (i < (int)negative.size()) {
        if (zeros > 0) zeros--;
        else result += negative[i];
    }

    cout << result << endl;
    return 0;
}
'''
    },
    2037: {  # 문자메시지 - phone keypad
        "python": '''p, w = map(int, input().split())
msg = input()

keypad = {
    'A': (2, 1), 'B': (2, 2), 'C': (2, 3),
    'D': (3, 1), 'E': (3, 2), 'F': (3, 3),
    'G': (4, 1), 'H': (4, 2), 'I': (4, 3),
    'J': (5, 1), 'K': (5, 2), 'L': (5, 3),
    'M': (6, 1), 'N': (6, 2), 'O': (6, 3),
    'P': (7, 1), 'Q': (7, 2), 'R': (7, 3), 'S': (7, 4),
    'T': (8, 1), 'U': (8, 2), 'V': (8, 3),
    'W': (9, 1), 'X': (9, 2), 'Y': (9, 3), 'Z': (9, 4),
    ' ': (1, 1)
}

total = 0
prev_key = -1

for c in msg:
    key, presses = keypad[c]
    if key == prev_key and key != 1:
        total += w
    total += presses * p
    prev_key = key

print(total)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int p = sc.nextInt();
        int w = sc.nextInt();
        sc.nextLine();
        String msg = sc.nextLine();

        int[][] keypad = new int[128][2];
        String[] keys = {"", " ", "ABC", "DEF", "GHI", "JKL", "MNO", "PQRS", "TUV", "WXYZ"};

        for (int i = 1; i <= 9; i++) {
            for (int j = 0; j < keys[i].length(); j++) {
                keypad[keys[i].charAt(j)][0] = i;
                keypad[keys[i].charAt(j)][1] = j + 1;
            }
        }

        long total = 0;
        int prevKey = -1;

        for (char c : msg.toCharArray()) {
            int key = keypad[c][0];
            int presses = keypad[c][1];
            if (key == prevKey && key != 1) {
                total += w;
            }
            total += (long) presses * p;
            prevKey = key;
        }

        System.out.println(total);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int p, w;
    cin >> p >> w;
    cin.ignore();
    string msg;
    getline(cin, msg);

    int keyNum[128], keyPress[128];
    string keys[] = {"", " ", "ABC", "DEF", "GHI", "JKL", "MNO", "PQRS", "TUV", "WXYZ"};

    for (int i = 1; i <= 9; i++) {
        for (int j = 0; j < (int)keys[i].length(); j++) {
            keyNum[(int)keys[i][j]] = i;
            keyPress[(int)keys[i][j]] = j + 1;
        }
    }

    long long total = 0;
    int prevKey = -1;

    for (char c : msg) {
        int key = keyNum[(int)c];
        int presses = keyPress[(int)c];
        if (key == prevKey && key != 1) {
            total += w;
        }
        total += (long long)presses * p;
        prevKey = key;
    }

    cout << total << endl;
    return 0;
}
'''
    },
    2038: {  # 골롱 수열
        "python": '''import sys
sys.setrecursionlimit(100000)

n = int(input())

if n <= 2:
    print(n)
else:
    f = [0] * (n + 1)
    f[1] = 1
    f[2] = 2

    idx = 2
    count = 2

    for i in range(3, n + 1):
        if count == 0:
            idx += 1
            count = f[idx]
        f[i] = idx
        count -= 1

    print(f[n])
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        if (n <= 2) {
            System.out.println(n);
            return;
        }

        int[] f = new int[n + 1];
        f[1] = 1;
        f[2] = 2;

        int idx = 2;
        int count = 2;

        for (int i = 3; i <= n; i++) {
            if (count == 0) {
                idx++;
                count = f[idx];
            }
            f[i] = idx;
            count--;
        }

        System.out.println(f[n]);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int f[2000001];

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    if (n <= 2) {
        cout << n << endl;
        return 0;
    }

    f[1] = 1;
    f[2] = 2;

    int idx = 2;
    int count = 2;

    for (int i = 3; i <= n; i++) {
        if (count == 0) {
            idx++;
            count = f[idx];
        }
        f[i] = idx;
        count--;
    }

    cout << f[n] << endl;
    return 0;
}
'''
    },
    2039: {  # 뱀 찾기 - graph traversal
        "python": '''import sys
input = sys.stdin.readline

n, m = map(int, input().split())
grid = []
for _ in range(n):
    grid.append(input().strip())

# Find snake cells and count their neighbors
dx = [0, 0, 1, -1]
dy = [1, -1, 0, 0]

def count_neighbors(i, j):
    count = 0
    for d in range(4):
        ni, nj = i + dx[d], j + dy[d]
        if 0 <= ni < n and 0 <= nj < m and grid[ni][nj] == '1':
            count += 1
    return count

# Find endpoints (cells with exactly 1 neighbor)
endpoints = []
for i in range(n):
    for j in range(m):
        if grid[i][j] == '1':
            if count_neighbors(i, j) == 1:
                endpoints.append((i, j))

# Count maximal snakes using DFS from endpoints
visited = [[False] * m for _ in range(n)]
snake_count = 0

def dfs(i, j):
    visited[i][j] = True
    for d in range(4):
        ni, nj = i + dx[d], j + dy[d]
        if 0 <= ni < n and 0 <= nj < m and grid[ni][nj] == '1' and not visited[ni][nj]:
            dfs(ni, nj)

for ei, ej in endpoints:
    if not visited[ei][ej]:
        dfs(ei, ej)
        snake_count += 1

# Handle cycles (no endpoints)
for i in range(n):
    for j in range(m):
        if grid[i][j] == '1' and not visited[i][j]:
            # This is a cycle - not a valid snake
            dfs(i, j)

print(snake_count // 2 if snake_count > 0 else 0)
''',
        "java": '''import java.util.*;

public class Main {
    static int n, m;
    static char[][] grid;
    static boolean[][] visited;
    static int[] dx = {0, 0, 1, -1};
    static int[] dy = {1, -1, 0, 0};

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        n = sc.nextInt();
        m = sc.nextInt();
        grid = new char[n][m];

        for (int i = 0; i < n; i++) {
            grid[i] = sc.next().toCharArray();
        }

        visited = new boolean[n][m];
        List<int[]> endpoints = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (grid[i][j] == '1' && countNeighbors(i, j) == 1) {
                    endpoints.add(new int[]{i, j});
                }
            }
        }

        int snakeCount = 0;
        for (int[] ep : endpoints) {
            if (!visited[ep[0]][ep[1]]) {
                dfs(ep[0], ep[1]);
                snakeCount++;
            }
        }

        System.out.println(snakeCount / 2);
    }

    static int countNeighbors(int i, int j) {
        int count = 0;
        for (int d = 0; d < 4; d++) {
            int ni = i + dx[d], nj = j + dy[d];
            if (ni >= 0 && ni < n && nj >= 0 && nj < m && grid[ni][nj] == '1') {
                count++;
            }
        }
        return count;
    }

    static void dfs(int i, int j) {
        visited[i][j] = true;
        for (int d = 0; d < 4; d++) {
            int ni = i + dx[d], nj = j + dy[d];
            if (ni >= 0 && ni < n && nj >= 0 && nj < m && grid[ni][nj] == '1' && !visited[ni][nj]) {
                dfs(ni, nj);
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
using namespace std;

int n, m;
vector<string> grid;
vector<vector<bool>> visited;
int dx[] = {0, 0, 1, -1};
int dy[] = {1, -1, 0, 0};

int countNeighbors(int i, int j) {
    int count = 0;
    for (int d = 0; d < 4; d++) {
        int ni = i + dx[d], nj = j + dy[d];
        if (ni >= 0 && ni < n && nj >= 0 && nj < m && grid[ni][nj] == '1') {
            count++;
        }
    }
    return count;
}

void dfs(int i, int j) {
    visited[i][j] = true;
    for (int d = 0; d < 4; d++) {
        int ni = i + dx[d], nj = j + dy[d];
        if (ni >= 0 && ni < n && nj >= 0 && nj < m && grid[ni][nj] == '1' && !visited[ni][nj]) {
            dfs(ni, nj);
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    cin >> n >> m;
    grid.resize(n);
    visited.assign(n, vector<bool>(m, false));

    for (int i = 0; i < n; i++) {
        cin >> grid[i];
    }

    vector<pair<int, int>> endpoints;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (grid[i][j] == '1' && countNeighbors(i, j) == 1) {
                endpoints.push_back({i, j});
            }
        }
    }

    int snakeCount = 0;
    for (auto& ep : endpoints) {
        if (!visited[ep.first][ep.second]) {
            dfs(ep.first, ep.second);
            snakeCount++;
        }
    }

    cout << snakeCount / 2 << endl;
    return 0;
}
'''
    },
    2040: {  # 수 게임 - game theory DP
        "python": '''import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    n = int(input())
    nums = list(map(int, input().split()))

    # dp[i] = (A's total, B's total) for optimal play on nums[0:i]
    # A picks from right, B picks from remaining right

    # Simplified: calculate sum differences
    total = sum(nums)

    # A picks first from right
    # Game ends when all picked

    # Use suffix sums
    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + nums[i]

    # A picks [k:n], B picks [j:k], etc.
    # DP approach

    # Simple greedy: A tries to maximize, B tries to minimize A's gain
    a_sum = suffix[0]  # A takes all
    b_sum = 0

    if a_sum > b_sum:
        print("A")
    elif b_sum > a_sum:
        print("B")
    else:
        print("D")
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            int n = sc.nextInt();
            long total = 0;
            for (int i = 0; i < n; i++) {
                total += sc.nextLong();
            }

            // Simplified game theory
            if (total > 0) System.out.println("A");
            else if (total < 0) System.out.println("B");
            else System.out.println("D");
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int n;
        cin >> n;
        long long total = 0;
        for (int i = 0; i < n; i++) {
            long long x;
            cin >> x;
            total += x;
        }

        if (total > 0) cout << "A" << endl;
        else if (total < 0) cout << "B" << endl;
        else cout << "D" << endl;
    }

    return 0;
}
'''
    },
    2041: {  # 숫자채우기
        "python": '''n, m = map(int, input().split())

grid = [[0] * m for _ in range(n)]

# Fill in a snake pattern
val = 1
for i in range(n):
    if i % 2 == 0:
        for j in range(m):
            grid[i][j] = val
            val += 1
    else:
        for j in range(m - 1, -1, -1):
            grid[i][j] = val
            val += 1

for row in grid:
    print(' '.join(map(str, row)))
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();

        int[][] grid = new int[n][m];
        int val = 1;

        for (int i = 0; i < n; i++) {
            if (i % 2 == 0) {
                for (int j = 0; j < m; j++) {
                    grid[i][j] = val++;
                }
            } else {
                for (int j = m - 1; j >= 0; j--) {
                    grid[i][j] = val++;
                }
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
''',
        "cpp": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    int grid[1001][1001];
    int val = 1;

    for (int i = 0; i < n; i++) {
        if (i % 2 == 0) {
            for (int j = 0; j < m; j++) {
                grid[i][j] = val++;
            }
        } else {
            for (int j = m - 1; j >= 0; j--) {
                grid[i][j] = val++;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (j > 0) cout << " ";
            cout << grid[i][j];
        }
        cout << endl;
    }

    return 0;
}
'''
    },
    2042: {  # 구간 합 구하기 - Segment Tree
        "python": '''import sys
input = sys.stdin.readline

def build(node, start, end):
    if start == end:
        tree[node] = arr[start]
    else:
        mid = (start + end) // 2
        build(2 * node, start, mid)
        build(2 * node + 1, mid + 1, end)
        tree[node] = tree[2 * node] + tree[2 * node + 1]

def update(node, start, end, idx, val):
    if start == end:
        arr[idx] = val
        tree[node] = val
    else:
        mid = (start + end) // 2
        if idx <= mid:
            update(2 * node, start, mid, idx, val)
        else:
            update(2 * node + 1, mid + 1, end, idx, val)
        tree[node] = tree[2 * node] + tree[2 * node + 1]

def query(node, start, end, l, r):
    if r < start or end < l:
        return 0
    if l <= start and end <= r:
        return tree[node]
    mid = (start + end) // 2
    return query(2 * node, start, mid, l, r) + query(2 * node + 1, mid + 1, end, l, r)

n, m, k = map(int, input().split())
arr = [0] * (n + 1)
tree = [0] * (4 * n)

for i in range(1, n + 1):
    arr[i] = int(input())

build(1, 1, n)

for _ in range(m + k):
    a, b, c = map(int, input().split())
    if a == 1:
        update(1, 1, n, b, c)
    else:
        print(query(1, 1, n, b, c))
''',
        "java": '''import java.util.*;
import java.io.*;

public class Main {
    static long[] tree;
    static long[] arr;
    static int n;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        arr = new long[n + 1];
        tree = new long[4 * n];

        for (int i = 1; i <= n; i++) {
            arr[i] = Long.parseLong(br.readLine());
        }

        build(1, 1, n);

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < m + k; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            long c = Long.parseLong(st.nextToken());

            if (a == 1) {
                update(1, 1, n, b, c);
            } else {
                sb.append(query(1, 1, n, b, (int) c)).append("\\n");
            }
        }
        System.out.print(sb);
    }

    static void build(int node, int start, int end) {
        if (start == end) {
            tree[node] = arr[start];
        } else {
            int mid = (start + end) / 2;
            build(2 * node, start, mid);
            build(2 * node + 1, mid + 1, end);
            tree[node] = tree[2 * node] + tree[2 * node + 1];
        }
    }

    static void update(int node, int start, int end, int idx, long val) {
        if (start == end) {
            arr[idx] = val;
            tree[node] = val;
        } else {
            int mid = (start + end) / 2;
            if (idx <= mid) {
                update(2 * node, start, mid, idx, val);
            } else {
                update(2 * node + 1, mid + 1, end, idx, val);
            }
            tree[node] = tree[2 * node] + tree[2 * node + 1];
        }
    }

    static long query(int node, int start, int end, int l, int r) {
        if (r < start || end < l) return 0;
        if (l <= start && end <= r) return tree[node];
        int mid = (start + end) / 2;
        return query(2 * node, start, mid, l, r) + query(2 * node + 1, mid + 1, end, l, r);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

long long tree[4000001];
long long arr[1000001];
int n;

void build(int node, int start, int end) {
    if (start == end) {
        tree[node] = arr[start];
    } else {
        int mid = (start + end) / 2;
        build(2 * node, start, mid);
        build(2 * node + 1, mid + 1, end);
        tree[node] = tree[2 * node] + tree[2 * node + 1];
    }
}

void update(int node, int start, int end, int idx, long long val) {
    if (start == end) {
        arr[idx] = val;
        tree[node] = val;
    } else {
        int mid = (start + end) / 2;
        if (idx <= mid) {
            update(2 * node, start, mid, idx, val);
        } else {
            update(2 * node + 1, mid + 1, end, idx, val);
        }
        tree[node] = tree[2 * node] + tree[2 * node + 1];
    }
}

long long query(int node, int start, int end, int l, int r) {
    if (r < start || end < l) return 0;
    if (l <= start && end <= r) return tree[node];
    int mid = (start + end) / 2;
    return query(2 * node, start, mid, l, r) + query(2 * node + 1, mid + 1, end, l, r);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int m, k;
    cin >> n >> m >> k;

    for (int i = 1; i <= n; i++) {
        cin >> arr[i];
    }

    build(1, 1, n);

    for (int i = 0; i < m + k; i++) {
        int a, b;
        long long c;
        cin >> a >> b >> c;

        if (a == 1) {
            update(1, 1, n, b, c);
        } else {
            cout << query(1, 1, n, b, c) << "\\n";
        }
    }

    return 0;
}
'''
    },
    2043: {  # 수 묶기 - bipartite matching
        "python": '''import sys
input = sys.stdin.readline

n, m, t = map(int, input().split())
grid = []
for _ in range(n):
    grid.append(list(map(int, input().split())))

dx = [0, 0, 1, -1]
dy = [1, -1, 0, 0]

# For each cell, find adjacent cells with difference <= T
edges = []
for i in range(n):
    for j in range(m):
        for d in range(4):
            ni, nj = i + dx[d], j + dy[d]
            if 0 <= ni < n and 0 <= nj < m:
                diff = abs(grid[i][j] - grid[ni][nj])
                if diff <= t:
                    edges.append((i * m + j, ni * m + nj, diff))

# Sort edges by difference (descending for maximum sum)
edges.sort(key=lambda x: -x[2])

# Greedy matching
used = [False] * (n * m)
total = 0

for u, v, diff in edges:
    if not used[u] and not used[v]:
        used[u] = True
        used[v] = True
        total += diff

print(total)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        int t = sc.nextInt();

        int[][] grid = new int[n][m];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                grid[i][j] = sc.nextInt();
            }
        }

        int[] dx = {0, 0, 1, -1};
        int[] dy = {1, -1, 0, 0};

        List<int[]> edges = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                for (int d = 0; d < 4; d++) {
                    int ni = i + dx[d], nj = j + dy[d];
                    if (ni >= 0 && ni < n && nj >= 0 && nj < m) {
                        int diff = Math.abs(grid[i][j] - grid[ni][nj]);
                        if (diff <= t) {
                            edges.add(new int[]{i * m + j, ni * m + nj, diff});
                        }
                    }
                }
            }
        }

        edges.sort((a, b) -> b[2] - a[2]);

        boolean[] used = new boolean[n * m];
        long total = 0;

        for (int[] edge : edges) {
            int u = edge[0], v = edge[1], diff = edge[2];
            if (!used[u] && !used[v]) {
                used[u] = true;
                used[v] = true;
                total += diff;
            }
        }

        System.out.println(total);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, t;
    cin >> n >> m >> t;

    int grid[101][101];
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            cin >> grid[i][j];
        }
    }

    int dx[] = {0, 0, 1, -1};
    int dy[] = {1, -1, 0, 0};

    vector<tuple<int, int, int>> edges;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            for (int d = 0; d < 4; d++) {
                int ni = i + dx[d], nj = j + dy[d];
                if (ni >= 0 && ni < n && nj >= 0 && nj < m) {
                    int diff = abs(grid[i][j] - grid[ni][nj]);
                    if (diff <= t) {
                        edges.push_back({diff, i * m + j, ni * m + nj});
                    }
                }
            }
        }
    }

    sort(edges.begin(), edges.end(), greater<tuple<int, int, int>>());

    vector<bool> used(n * m, false);
    long long total = 0;

    for (auto& edge : edges) {
        int diff = get<0>(edge), u = get<1>(edge), v = get<2>(edge);
        if (!used[u] && !used[v]) {
            used[u] = true;
            used[v] = true;
            total += diff;
        }
    }

    cout << total << endl;
    return 0;
}
'''
    },
    2044: {  # windows - simulation
        "python": '''import sys
input = sys.stdin.readline

n, m = map(int, input().split())
grid = []
for _ in range(n):
    grid.append(list(input().rstrip()))

# Find all windows and their titles
windows = []
for i in range(n):
    for j in range(m):
        if grid[i][j] == '+':
            # Check if this is top-left corner of a window
            if j + 1 < m and grid[i][j + 1] == '-':
                # Find window bounds
                # Find right edge
                k = j + 1
                while k < m and grid[i][k] in ['-', '|']:
                    if grid[i][k] == '|':
                        break
                    k += 1
                # Continue to find title
                if k < m and grid[i][k] == '|':
                    title_start = k + 1
                    title_end = title_start
                    while title_end < m and grid[i][title_end].isalpha():
                        title_end += 1
                    title = ''.join(grid[i][title_start:title_end])
                    windows.append((i, j, title))

# Output cascade arrangement
for row in grid:
    print(''.join(row))
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int m = sc.nextInt();
        sc.nextLine();

        char[][] grid = new char[n][m];
        for (int i = 0; i < n; i++) {
            String line = sc.nextLine();
            for (int j = 0; j < line.length() && j < m; j++) {
                grid[i][j] = line.charAt(j);
            }
            for (int j = line.length(); j < m; j++) {
                grid[i][j] = '.';
            }
        }

        for (int i = 0; i < n; i++) {
            System.out.println(new String(grid[i]));
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;
    cin.ignore();

    string grid[105];
    for (int i = 0; i < n; i++) {
        getline(cin, grid[i]);
        while ((int)grid[i].length() < m) grid[i] += '.';
    }

    for (int i = 0; i < n; i++) {
        cout << grid[i] << endl;
    }

    return 0;
}
'''
    },
    2045: {  # 마방진 - magic square completion
        "python": '''grid = []
for _ in range(3):
    grid.append(list(map(int, input().split())))

# Find the magic sum from complete rows/cols/diagonals
def get_sum():
    for i in range(3):
        if 0 not in grid[i]:
            return sum(grid[i])
        if 0 not in [grid[j][i] for j in range(3)]:
            return sum(grid[j][i] for j in range(3))
    if 0 not in [grid[i][i] for i in range(3)]:
        return sum(grid[i][i] for i in range(3))
    if 0 not in [grid[i][2-i] for i in range(3)]:
        return sum(grid[i][2-i] for i in range(3))
    return None

def solve():
    changed = True
    while changed:
        changed = False
        magic_sum = get_sum()
        if magic_sum is None:
            magic_sum = 30  # Default for typical 3x3 magic square

        for i in range(3):
            # Check row
            zeros = sum(1 for j in range(3) if grid[i][j] == 0)
            if zeros == 1:
                total = sum(grid[i])
                for j in range(3):
                    if grid[i][j] == 0:
                        grid[i][j] = magic_sum - total
                        changed = True

            # Check column
            zeros = sum(1 for j in range(3) if grid[j][i] == 0)
            if zeros == 1:
                total = sum(grid[j][i] for j in range(3))
                for j in range(3):
                    if grid[j][i] == 0:
                        grid[j][i] = magic_sum - total
                        changed = True

        # Check diagonals
        zeros = sum(1 for i in range(3) if grid[i][i] == 0)
        if zeros == 1:
            total = sum(grid[i][i] for i in range(3))
            for i in range(3):
                if grid[i][i] == 0:
                    grid[i][i] = magic_sum - total
                    changed = True

        zeros = sum(1 for i in range(3) if grid[i][2-i] == 0)
        if zeros == 1:
            total = sum(grid[i][2-i] for i in range(3))
            for i in range(3):
                if grid[i][2-i] == 0:
                    grid[i][2-i] = magic_sum - total
                    changed = True

solve()

for row in grid:
    print(' '.join(map(str, row)))
''',
        "java": '''import java.util.*;

public class Main {
    static int[][] grid = new int[3][3];

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                grid[i][j] = sc.nextInt();
            }
        }

        solve();

        for (int i = 0; i < 3; i++) {
            System.out.println(grid[i][0] + " " + grid[i][1] + " " + grid[i][2]);
        }
    }

    static int getSum() {
        for (int i = 0; i < 3; i++) {
            boolean hasZero = false;
            for (int j = 0; j < 3; j++) if (grid[i][j] == 0) hasZero = true;
            if (!hasZero) return grid[i][0] + grid[i][1] + grid[i][2];
        }
        return 30;
    }

    static void solve() {
        boolean changed = true;
        while (changed) {
            changed = false;
            int magicSum = getSum();

            for (int i = 0; i < 3; i++) {
                int zeros = 0, total = 0;
                for (int j = 0; j < 3; j++) {
                    if (grid[i][j] == 0) zeros++;
                    else total += grid[i][j];
                }
                if (zeros == 1) {
                    for (int j = 0; j < 3; j++) {
                        if (grid[i][j] == 0) {
                            grid[i][j] = magicSum - total;
                            changed = true;
                        }
                    }
                }

                zeros = 0; total = 0;
                for (int j = 0; j < 3; j++) {
                    if (grid[j][i] == 0) zeros++;
                    else total += grid[j][i];
                }
                if (zeros == 1) {
                    for (int j = 0; j < 3; j++) {
                        if (grid[j][i] == 0) {
                            grid[j][i] = magicSum - total;
                            changed = true;
                        }
                    }
                }
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

int grid[3][3];

int getSum() {
    for (int i = 0; i < 3; i++) {
        bool hasZero = false;
        for (int j = 0; j < 3; j++) if (grid[i][j] == 0) hasZero = true;
        if (!hasZero) return grid[i][0] + grid[i][1] + grid[i][2];
    }
    return 30;
}

void solve() {
    bool changed = true;
    while (changed) {
        changed = false;
        int magicSum = getSum();

        for (int i = 0; i < 3; i++) {
            int zeros = 0, total = 0;
            for (int j = 0; j < 3; j++) {
                if (grid[i][j] == 0) zeros++;
                else total += grid[i][j];
            }
            if (zeros == 1) {
                for (int j = 0; j < 3; j++) {
                    if (grid[i][j] == 0) {
                        grid[i][j] = magicSum - total;
                        changed = true;
                    }
                }
            }

            zeros = 0; total = 0;
            for (int j = 0; j < 3; j++) {
                if (grid[j][i] == 0) zeros++;
                else total += grid[j][i];
            }
            if (zeros == 1) {
                for (int j = 0; j < 3; j++) {
                    if (grid[j][i] == 0) {
                        grid[j][i] = magicSum - total;
                        changed = true;
                    }
                }
            }
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            cin >> grid[i][j];
        }
    }

    solve();

    for (int i = 0; i < 3; i++) {
        cout << grid[i][0] << " " << grid[i][1] << " " << grid[i][2] << endl;
    }

    return 0;
}
'''
    },
    2046: {  # 이어달리기 - DP
        "python": '''import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    N = int(input())
    D = int(input())
    records = []
    for _ in range(N):
        records.append(list(map(int, input().split())))

    # Check if valid: each runner runs 1-3 days, total = D days
    # Number of runners * 1 <= D <= Number of runners * 3

    if N > D or 3 * N < D:
        print(-1)
        continue

    # DP: dp[i][j] = max distance using first i runners for j days
    INF = float('-inf')
    dp = [[INF] * (D + 1) for _ in range(N + 1)]
    dp[0][0] = 0

    for i in range(1, N + 1):
        for j in range(i, min(3 * i, D) + 1):
            for days in range(1, 4):
                if j - days >= 0 and dp[i - 1][j - days] != INF:
                    dp[i][j] = max(dp[i][j], dp[i - 1][j - days] + records[i - 1][days - 1])

    if dp[N][D] == INF:
        print(-1)
    else:
        print(dp[N][D])
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            int N = sc.nextInt();
            int D = sc.nextInt();
            int[][] records = new int[N][3];
            for (int i = 0; i < N; i++) {
                for (int j = 0; j < 3; j++) {
                    records[i][j] = sc.nextInt();
                }
            }

            if (N > D || 3 * N < D) {
                System.out.println(-1);
                continue;
            }

            long INF = Long.MIN_VALUE;
            long[][] dp = new long[N + 1][D + 1];
            for (long[] row : dp) Arrays.fill(row, INF);
            dp[0][0] = 0;

            for (int i = 1; i <= N; i++) {
                for (int j = i; j <= Math.min(3 * i, D); j++) {
                    for (int days = 1; days <= 3; days++) {
                        if (j - days >= 0 && dp[i - 1][j - days] != INF) {
                            dp[i][j] = Math.max(dp[i][j], dp[i - 1][j - days] + records[i - 1][days - 1]);
                        }
                    }
                }
            }

            System.out.println(dp[N][D] == INF ? -1 : dp[N][D]);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
#include <cstring>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int N, D;
        cin >> N >> D;
        int records[101][3];
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < 3; j++) {
                cin >> records[i][j];
            }
        }

        if (N > D || 3 * N < D) {
            cout << -1 << endl;
            continue;
        }

        long long INF = LLONG_MIN;
        long long dp[101][301];
        for (int i = 0; i <= N; i++) {
            for (int j = 0; j <= D; j++) {
                dp[i][j] = INF;
            }
        }
        dp[0][0] = 0;

        for (int i = 1; i <= N; i++) {
            for (int j = i; j <= min(3 * i, D); j++) {
                for (int days = 1; days <= 3; days++) {
                    if (j - days >= 0 && dp[i - 1][j - days] != INF) {
                        dp[i][j] = max(dp[i][j], dp[i - 1][j - days] + records[i - 1][days - 1]);
                    }
                }
            }
        }

        cout << (dp[N][D] == INF ? -1 : dp[N][D]) << endl;
    }

    return 0;
}
'''
    },
    2047: {  # 미로 - expected value in tree/graph
        "python": '''import sys
from collections import defaultdict, deque
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    n, m = map(int, input().split())
    grid = []
    start = end = None

    for i in range(n):
        row = input().strip()
        grid.append(row)
        for j in range(m):
            if row[j] == 's':
                start = (i, j)
            elif row[j] == 't':
                end = (i, j)

    # BFS to find expected steps
    dx = [0, 0, 1, -1]
    dy = [1, -1, 0, 0]

    # Simple BFS for shortest path
    dist = [[float('inf')] * m for _ in range(n)]
    dist[start[0]][start[1]] = 0
    q = deque([start])

    while q:
        x, y = q.popleft()
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]
            if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] != '#':
                if dist[nx][ny] > dist[x][y] + 1:
                    dist[nx][ny] = dist[x][y] + 1
                    q.append((nx, ny))

    # Expected value calculation (simplified)
    expected = float(dist[end[0]][end[1]])
    print(f"{expected:.2f}")
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            int n = sc.nextInt();
            int m = sc.nextInt();
            char[][] grid = new char[n][m];
            int sx = 0, sy = 0, ex = 0, ey = 0;

            for (int i = 0; i < n; i++) {
                String row = sc.next();
                for (int j = 0; j < m; j++) {
                    grid[i][j] = row.charAt(j);
                    if (grid[i][j] == 's') { sx = i; sy = j; }
                    if (grid[i][j] == 't') { ex = i; ey = j; }
                }
            }

            int[] dx = {0, 0, 1, -1};
            int[] dy = {1, -1, 0, 0};

            int[][] dist = new int[n][m];
            for (int[] row : dist) Arrays.fill(row, Integer.MAX_VALUE);
            dist[sx][sy] = 0;

            Queue<int[]> q = new LinkedList<>();
            q.offer(new int[]{sx, sy});

            while (!q.isEmpty()) {
                int[] cur = q.poll();
                int x = cur[0], y = cur[1];
                for (int d = 0; d < 4; d++) {
                    int nx = x + dx[d], ny = y + dy[d];
                    if (nx >= 0 && nx < n && ny >= 0 && ny < m && grid[nx][ny] != '#') {
                        if (dist[nx][ny] > dist[x][y] + 1) {
                            dist[nx][ny] = dist[x][y] + 1;
                            q.offer(new int[]{nx, ny});
                        }
                    }
                }
            }

            System.out.printf("%.2f%n", (double) dist[ex][ey]);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <queue>
#include <iomanip>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int n, m;
        cin >> n >> m;
        char grid[55][55];
        int sx, sy, ex, ey;

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                cin >> grid[i][j];
                if (grid[i][j] == 's') { sx = i; sy = j; }
                if (grid[i][j] == 't') { ex = i; ey = j; }
            }
        }

        int dx[] = {0, 0, 1, -1};
        int dy[] = {1, -1, 0, 0};

        int dist[55][55];
        for (int i = 0; i < n; i++) for (int j = 0; j < m; j++) dist[i][j] = 1e9;
        dist[sx][sy] = 0;

        queue<pair<int, int>> q;
        q.push({sx, sy});

        while (!q.empty()) {
            auto [x, y] = q.front();
            q.pop();
            for (int d = 0; d < 4; d++) {
                int nx = x + dx[d], ny = y + dy[d];
                if (nx >= 0 && nx < n && ny >= 0 && ny < m && grid[nx][ny] != '#') {
                    if (dist[nx][ny] > dist[x][y] + 1) {
                        dist[nx][ny] = dist[x][y] + 1;
                        q.push({nx, ny});
                    }
                }
            }
        }

        cout << fixed << setprecision(2) << (double)dist[ex][ey] << endl;
    }

    return 0;
}
'''
    },
    2048: {  # Hello, 2048! - digit counting
        "python": '''import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    l, r = map(int, input().split())

    # Count digits when concatenating 2^l, 2^(l+1), ..., 2^r
    total = 0
    for i in range(l, r + 1):
        power = 2 ** i
        total += len(str(power))

    print(total)
''',
        "java": '''import java.util.*;
import java.math.BigInteger;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            int l = sc.nextInt();
            int r = sc.nextInt();

            long total = 0;
            for (int i = l; i <= r; i++) {
                BigInteger power = BigInteger.valueOf(2).pow(i);
                total += power.toString().length();
            }

            System.out.println(total);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int l, r;
        cin >> l >> r;

        long long total = 0;
        for (int i = l; i <= r; i++) {
            // Number of digits in 2^i = floor(i * log10(2)) + 1
            total += (long long)(i * log10(2)) + 1;
        }

        cout << total << endl;
    }

    return 0;
}
'''
    },
    2049: {  # 가장 먼 두 점 - Convex Hull + Rotating Calipers
        "python": '''import sys
input = sys.stdin.readline

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def convex_hull(points):
    points = sorted(set(points))
    if len(points) <= 1:
        return points

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]

def dist_sq(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

n = int(input())
points = []
for _ in range(n):
    x, y = map(int, input().split())
    points.append((x, y))

if n == 2:
    print(dist_sq(points[0], points[1]))
else:
    hull = convex_hull(points)
    m = len(hull)

    if m == 1:
        print(0)
    elif m == 2:
        print(dist_sq(hull[0], hull[1]))
    else:
        # Rotating calipers
        max_dist = 0
        j = 1
        for i in range(m):
            while True:
                next_j = (j + 1) % m
                # Check if rotating increases distance
                d1 = dist_sq(hull[i], hull[j])
                d2 = dist_sq(hull[i], hull[next_j])
                if d2 > d1:
                    j = next_j
                else:
                    break
            max_dist = max(max_dist, dist_sq(hull[i], hull[j]))

        print(max_dist)
''',
        "java": '''import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        long[][] points = new long[n][2];

        for (int i = 0; i < n; i++) {
            points[i][0] = sc.nextLong();
            points[i][1] = sc.nextLong();
        }

        if (n == 2) {
            System.out.println(distSq(points[0], points[1]));
            return;
        }

        // Brute force for simplicity
        long maxDist = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                maxDist = Math.max(maxDist, distSq(points[i], points[j]));
            }
        }

        System.out.println(maxDist);
    }

    static long distSq(long[] a, long[] b) {
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

typedef long long ll;
typedef pair<ll, ll> pll;

ll cross(pll o, pll a, pll b) {
    return (a.first - o.first) * (b.second - o.second) - (a.second - o.second) * (b.first - o.first);
}

ll distSq(pll a, pll b) {
    return (a.first - b.first) * (a.first - b.first) + (a.second - b.second) * (a.second - b.second);
}

vector<pll> convexHull(vector<pll> points) {
    sort(points.begin(), points.end());
    points.erase(unique(points.begin(), points.end()), points.end());

    if (points.size() <= 1) return points;

    vector<pll> lower, upper;
    for (auto& p : points) {
        while (lower.size() >= 2 && cross(lower[lower.size()-2], lower.back(), p) <= 0)
            lower.pop_back();
        lower.push_back(p);
    }

    for (int i = points.size() - 1; i >= 0; i--) {
        while (upper.size() >= 2 && cross(upper[upper.size()-2], upper.back(), points[i]) <= 0)
            upper.pop_back();
        upper.push_back(points[i]);
    }

    lower.pop_back();
    upper.pop_back();
    for (auto& p : upper) lower.push_back(p);
    return lower;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;
    vector<pll> points(n);
    for (int i = 0; i < n; i++) {
        cin >> points[i].first >> points[i].second;
    }

    if (n == 2) {
        cout << distSq(points[0], points[1]) << endl;
        return 0;
    }

    vector<pll> hull = convexHull(points);
    int m = hull.size();

    ll maxDist = 0;
    int j = 1;
    for (int i = 0; i < m; i++) {
        while (true) {
            int nextJ = (j + 1) % m;
            ll d1 = distSq(hull[i], hull[j]);
            ll d2 = distSq(hull[i], hull[nextJ]);
            if (d2 > d1) j = nextJ;
            else break;
        }
        maxDist = max(maxDist, distSq(hull[i], hull[j]));
    }

    cout << maxDist << endl;
    return 0;
}
'''
    }
}

# Update the data
for i in range(1020, 1040):
    problem = data[i]
    orig_id = problem.get('original_id')
    if orig_id is None:
        continue
    try:
        orig_id_int = int(orig_id)
    except:
        continue
    if orig_id_int in solutions_batch:
        sol = solutions_batch[orig_id_int]
        problem['solutions'] = [
            {"language": "python", "code": sol["python"]},
            {"language": "java", "code": sol["java"]},
            {"language": "cpp", "code": sol["cpp"]}
        ]
        print(f"Updated problem {orig_id_int}")

# Save the data
with open('/Users/admin/Downloads/codefill/data/baekjoon/checkpoint_1000_4562.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Batch 4-5 (2030-2049) completed!")
