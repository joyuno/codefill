#!/usr/bin/env python3
"""
백준 문제 솔루션 생성 및 업데이트 스크립트 (Part 2)
추가 문제들에 대한 솔루션
"""

import json

# 추가 솔루션 정의
SOLUTIONS_PART2 = {
    # 2930: 가위 바위 보
    "2930": {
        "python": '''# 백준 2930: 가위 바위 보
# 상근이의 실제 점수와 최적 점수를 계산

def score(a, b):
    # a가 b를 상대로 얻는 점수
    if a == b:
        return 1
    elif (a == 'S' and b == 'P') or (a == 'R' and b == 'S') or (a == 'P' and b == 'R'):
        return 2
    else:
        return 0

R = int(input())
sg = input().strip()
N = int(input())
friends = []
for _ in range(N):
    friends.append(input().strip())

# 실제 점수 계산
actual_score = 0
for r in range(R):
    for f in friends:
        actual_score += score(sg[r], f[r])

# 최적 점수 계산 - 각 라운드마다 최적의 선택
optimal_score = 0
for r in range(R):
    best = 0
    for choice in 'SRP':
        round_score = 0
        for f in friends:
            round_score += score(choice, f[r])
        best = max(best, round_score)
    optimal_score += best

print(actual_score)
print(optimal_score)
''',
        "java": '''import java.util.Scanner;

// 백준 2930: 가위 바위 보
public class Main {
    static int score(char a, char b) {
        if (a == b) return 1;
        if ((a == 'S' && b == 'P') || (a == 'R' && b == 'S') || (a == 'P' && b == 'R'))
            return 2;
        return 0;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int R = sc.nextInt();
        String sg = sc.next();
        int N = sc.nextInt();
        String[] friends = new String[N];
        for (int i = 0; i < N; i++) {
            friends[i] = sc.next();
        }

        // 실제 점수
        int actual = 0;
        for (int r = 0; r < R; r++) {
            for (int f = 0; f < N; f++) {
                actual += score(sg.charAt(r), friends[f].charAt(r));
            }
        }

        // 최적 점수
        int optimal = 0;
        char[] choices = {'S', 'R', 'P'};
        for (int r = 0; r < R; r++) {
            int best = 0;
            for (char c : choices) {
                int roundScore = 0;
                for (int f = 0; f < N; f++) {
                    roundScore += score(c, friends[f].charAt(r));
                }
                best = Math.max(best, roundScore);
            }
            optimal += best;
        }

        System.out.println(actual);
        System.out.println(optimal);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

// 백준 2930: 가위 바위 보
int score(char a, char b) {
    if (a == b) return 1;
    if ((a == 'S' && b == 'P') || (a == 'R' && b == 'S') || (a == 'P' && b == 'R'))
        return 2;
    return 0;
}

int main() {
    int R;
    cin >> R;
    string sg;
    cin >> sg;
    int N;
    cin >> N;
    string friends[50];
    for (int i = 0; i < N; i++) {
        cin >> friends[i];
    }

    // 실제 점수
    int actual = 0;
    for (int r = 0; r < R; r++) {
        for (int f = 0; f < N; f++) {
            actual += score(sg[r], friends[f][r]);
        }
    }

    // 최적 점수
    int optimal = 0;
    char choices[] = {'S', 'R', 'P'};
    for (int r = 0; r < R; r++) {
        int best = 0;
        for (char c : choices) {
            int roundScore = 0;
            for (int f = 0; f < N; f++) {
                roundScore += score(c, friends[f][r]);
            }
            best = max(best, roundScore);
        }
        optimal += best;
    }

    cout << actual << endl;
    cout << optimal << endl;

    return 0;
}
'''
    },

    # 25593: 근무 지옥에 빠진 푸앙이 (Small)
    "25593": {
        "python": '''# 백준 25593: 근무 지옥에 빠진 푸앙이 (Small)
# 각 인원의 근무 시간이 12시간 이하로 차이 나는지 확인

N = int(input())
hours = [4, 6, 4, 10]  # 각 시간대별 근무 시간
work_time = {}

for _ in range(N):
    for h in range(4):
        names = input().split()
        for name in names:
            if name != '-':
                if name not in work_time:
                    work_time[name] = 0
                work_time[name] += hours[h]

if len(work_time) == 0:
    print("Yes")
else:
    times = list(work_time.values())
    if max(times) - min(times) <= 12:
        print("Yes")
    else:
        print("No")
''',
        "java": '''import java.util.*;

// 백준 25593: 근무 지옥에 빠진 푸앙이 (Small)
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        sc.nextLine();

        int[] hours = {4, 6, 4, 10};
        Map<String, Integer> workTime = new HashMap<>();

        for (int w = 0; w < N; w++) {
            for (int h = 0; h < 4; h++) {
                String[] names = sc.nextLine().split(" ");
                for (String name : names) {
                    if (!name.equals("-")) {
                        workTime.put(name, workTime.getOrDefault(name, 0) + hours[h]);
                    }
                }
            }
        }

        if (workTime.isEmpty()) {
            System.out.println("Yes");
        } else {
            int maxTime = Collections.max(workTime.values());
            int minTime = Collections.min(workTime.values());
            if (maxTime - minTime <= 12) {
                System.out.println("Yes");
            } else {
                System.out.println("No");
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <map>
#include <string>
#include <sstream>
#include <climits>
using namespace std;

// 백준 25593: 근무 지옥에 빠진 푸앙이 (Small)
int main() {
    int N;
    cin >> N;
    cin.ignore();

    int hours[] = {4, 6, 4, 10};
    map<string, int> workTime;

    for (int w = 0; w < N; w++) {
        for (int h = 0; h < 4; h++) {
            string line;
            getline(cin, line);
            stringstream ss(line);
            string name;
            while (ss >> name) {
                if (name != "-") {
                    workTime[name] += hours[h];
                }
            }
        }
    }

    if (workTime.empty()) {
        cout << "Yes" << endl;
    } else {
        int maxTime = INT_MIN, minTime = INT_MAX;
        for (auto& p : workTime) {
            maxTime = max(maxTime, p.second);
            minTime = min(minTime, p.second);
        }
        if (maxTime - minTime <= 12) {
            cout << "Yes" << endl;
        } else {
            cout << "No" << endl;
        }
    }

    return 0;
}
'''
    },

    # 15874: Caesar Cipher
    "15874": {
        "python": '''# 백준 15874: Caesar Cipher
# 카이사르 암호 - 알파벳을 K만큼 밀어서 암호화

first_line = input().split()
K = int(first_line[0])
# 나머지는 문자열 길이지만 필요없음

text = input()
K = K % 26  # 26으로 나눈 나머지만 필요

result = []
for c in text:
    if c.isalpha():
        if c.isupper():
            result.append(chr((ord(c) - ord('A') + K) % 26 + ord('A')))
        else:
            result.append(chr((ord(c) - ord('a') + K) % 26 + ord('a')))
    else:
        result.append(c)

print(''.join(result))
''',
        "java": '''import java.util.Scanner;

// 백준 15874: Caesar Cipher
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int K = sc.nextInt();
        int len = sc.nextInt();
        sc.nextLine();
        String text = sc.nextLine();

        K = K % 26;

        StringBuilder result = new StringBuilder();
        for (char c : text.toCharArray()) {
            if (Character.isLetter(c)) {
                if (Character.isUpperCase(c)) {
                    result.append((char)((c - 'A' + K) % 26 + 'A'));
                } else {
                    result.append((char)((c - 'a' + K) % 26 + 'a'));
                }
            } else {
                result.append(c);
            }
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

// 백준 15874: Caesar Cipher
int main() {
    int K, len;
    cin >> K >> len;
    cin.ignore();
    string text;
    getline(cin, text);

    K = K % 26;

    string result;
    for (char c : text) {
        if (isalpha(c)) {
            if (isupper(c)) {
                result += (char)((c - 'A' + K) % 26 + 'A');
            } else {
                result += (char)((c - 'a' + K) % 26 + 'a');
            }
        } else {
            result += c;
        }
    }

    cout << result << endl;

    return 0;
}
'''
    },

    # 11466: Alex Origami Squares
    "11466": {
        "python": '''# 백준 11466: Alex Origami Squares
# h x w 종이에서 3개의 같은 정사각형을 잘라낼 때 최대 크기

h, w = map(int, input().split())

# 작은 쪽을 h로 설정
if h > w:
    h, w = w, h

# 방법 1: 한 쪽에 2개, 다른 쪽에 1개 배치
# 가로로 3개 배치: w/3
# 세로로 2개, 가로로 1개: min(h/2, w)
# 가로로 2개, 세로로 1개: min(w/2, h)

size1 = w / 3  # 가로로 3개
size2 = min(h / 2, w)  # 세로 2개
size3 = min(w / 2, h)  # 가로 2개

result = max(size1, size2, size3)
print(result)
''',
        "java": '''import java.util.Scanner;

// 백준 11466: Alex Origami Squares
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        double h = sc.nextInt();
        double w = sc.nextInt();

        if (h > w) {
            double temp = h;
            h = w;
            w = temp;
        }

        double size1 = w / 3;
        double size2 = Math.min(h / 2, w);
        double size3 = Math.min(w / 2, h);

        double result = Math.max(size1, Math.max(size2, size3));
        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
using namespace std;

// 백준 11466: Alex Origami Squares
int main() {
    double h, w;
    cin >> h >> w;

    if (h > w) swap(h, w);

    double size1 = w / 3;
    double size2 = min(h / 2, w);
    double size3 = min(w / 2, h);

    double result = max({size1, size2, size3});
    cout << result << endl;

    return 0;
}
'''
    },

    # 15463: Blocked Billboard
    "15463": {
        "python": '''# 백준 15463: Blocked Billboard
# 두 광고판의 면적에서 트럭에 가려진 부분을 뺀다

def area(x1, y1, x2, y2):
    return (x2 - x1) * (y2 - y1)

def overlap(b, t):
    # 광고판 b와 트럭 t의 겹치는 영역
    x1 = max(b[0], t[0])
    y1 = max(b[1], t[1])
    x2 = min(b[2], t[2])
    y2 = min(b[3], t[3])

    if x1 < x2 and y1 < y2:
        return (x2 - x1) * (y2 - y1)
    return 0

b1 = list(map(int, input().split()))
b2 = list(map(int, input().split()))
t = list(map(int, input().split()))

# 각 광고판의 원래 면적
area1 = area(*b1)
area2 = area(*b2)

# 트럭과 겹치는 부분 제외
visible1 = area1 - overlap(b1, t)
visible2 = area2 - overlap(b2, t)

print(visible1 + visible2)
''',
        "java": '''import java.util.Scanner;

// 백준 15463: Blocked Billboard
public class Main {
    static int overlap(int[] b, int[] t) {
        int x1 = Math.max(b[0], t[0]);
        int y1 = Math.max(b[1], t[1]);
        int x2 = Math.min(b[2], t[2]);
        int y2 = Math.min(b[3], t[3]);

        if (x1 < x2 && y1 < y2) {
            return (x2 - x1) * (y2 - y1);
        }
        return 0;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int[] b1 = new int[4];
        int[] b2 = new int[4];
        int[] t = new int[4];

        for (int i = 0; i < 4; i++) b1[i] = sc.nextInt();
        for (int i = 0; i < 4; i++) b2[i] = sc.nextInt();
        for (int i = 0; i < 4; i++) t[i] = sc.nextInt();

        int area1 = (b1[2] - b1[0]) * (b1[3] - b1[1]);
        int area2 = (b2[2] - b2[0]) * (b2[3] - b2[1]);

        int visible1 = area1 - overlap(b1, t);
        int visible2 = area2 - overlap(b2, t);

        System.out.println(visible1 + visible2);
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
using namespace std;

// 백준 15463: Blocked Billboard
int overlap(int b[], int t[]) {
    int x1 = max(b[0], t[0]);
    int y1 = max(b[1], t[1]);
    int x2 = min(b[2], t[2]);
    int y2 = min(b[3], t[3]);

    if (x1 < x2 && y1 < y2) {
        return (x2 - x1) * (y2 - y1);
    }
    return 0;
}

int main() {
    int b1[4], b2[4], t[4];

    for (int i = 0; i < 4; i++) cin >> b1[i];
    for (int i = 0; i < 4; i++) cin >> b2[i];
    for (int i = 0; i < 4; i++) cin >> t[i];

    int area1 = (b1[2] - b1[0]) * (b1[3] - b1[1]);
    int area2 = (b2[2] - b2[0]) * (b2[3] - b2[1]);

    int visible1 = area1 - overlap(b1, t);
    int visible2 = area2 - overlap(b2, t);

    cout << visible1 + visible2 << endl;

    return 0;
}
'''
    },

    # 18322: Word Processor
    "18322": {
        "python": '''# 백준 18322: Word Processor
# 각 줄에 K글자 이하가 되도록 단어 배치

first_line = input().split()
N = int(first_line[0])
K = int(first_line[1])

words = input().split()

lines = []
current_line = []
current_len = 0

for word in words:
    if current_len + len(word) <= K:
        current_line.append(word)
        current_len += len(word)
    else:
        lines.append(' '.join(current_line))
        current_line = [word]
        current_len = len(word)

if current_line:
    lines.append(' '.join(current_line))

print('\\n'.join(lines))
''',
        "java": '''import java.util.*;

// 백준 18322: Word Processor
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int K = sc.nextInt();

        StringBuilder result = new StringBuilder();
        StringBuilder line = new StringBuilder();
        int lineLen = 0;

        for (int i = 0; i < N; i++) {
            String word = sc.next();
            if (lineLen + word.length() <= K) {
                if (lineLen > 0) line.append(" ");
                line.append(word);
                lineLen += word.length();
            } else {
                result.append(line).append("\\n");
                line = new StringBuilder(word);
                lineLen = word.length();
            }
        }
        result.append(line);

        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <vector>
using namespace std;

// 백준 18322: Word Processor
int main() {
    int N, K;
    cin >> N >> K;

    vector<string> lines;
    string currentLine;
    int currentLen = 0;

    for (int i = 0; i < N; i++) {
        string word;
        cin >> word;

        if (currentLen + (int)word.length() <= K) {
            if (!currentLine.empty()) currentLine += " ";
            currentLine += word;
            currentLen += word.length();
        } else {
            lines.push_back(currentLine);
            currentLine = word;
            currentLen = word.length();
        }
    }
    if (!currentLine.empty()) {
        lines.push_back(currentLine);
    }

    for (const string& line : lines) {
        cout << line << "\\n";
    }

    return 0;
}
'''
    },

    # 23739: 벼락치기
    "23739": {
        "python": '''# 백준 23739: 벼락치기
# 30분 공부 후 휴식, 절반 이상 공부한 챕터만 기억

N = int(input())
chapters = []
for _ in range(N):
    chapters.append(int(input()))

count = 0
time_left = 30

for t in chapters:
    if time_left >= t:
        # 챕터를 다 공부할 수 있음
        count += 1
        time_left -= t
    else:
        # 절반 이상 공부했는지 확인
        if time_left >= t / 2:
            count += 1
        # 다음 30분 시작
        time_left = 30 - (t - time_left) % 30
        if time_left == 30:
            time_left = 0

# 다시 계산 - 30분 단위로 계산
count = 0
time_in_session = 0

for t in chapters:
    # 현재 챕터에 사용할 수 있는 시간
    study_time = min(t, 30 - time_in_session)

    if study_time >= t / 2:
        count += 1

    time_in_session += t
    while time_in_session >= 30:
        time_in_session -= 30

print(count)
''',
        "java": '''import java.util.Scanner;

// 백준 23739: 벼락치기
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] chapters = new int[N];
        for (int i = 0; i < N; i++) {
            chapters[i] = sc.nextInt();
        }

        int count = 0;
        int timeInSession = 0;

        for (int t : chapters) {
            int studyTime = Math.min(t, 30 - timeInSession);

            if (studyTime * 2 >= t) {
                count++;
            }

            timeInSession += t;
            while (timeInSession >= 30) {
                timeInSession -= 30;
            }
        }

        System.out.println(count);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 23739: 벼락치기
int main() {
    int N;
    cin >> N;

    int count = 0;
    int timeInSession = 0;

    for (int i = 0; i < N; i++) {
        int t;
        cin >> t;

        int studyTime = min(t, 30 - timeInSession);

        if (studyTime * 2 >= t) {
            count++;
        }

        timeInSession += t;
        while (timeInSession >= 30) {
            timeInSession -= 30;
        }
    }

    cout << count << endl;

    return 0;
}
'''
    },

    # 18268: Cow Gymnastics
    "18268": {
        "python": '''# 백준 18268: Cow Gymnastics
# 모든 세션에서 일관된 순위를 가진 쌍의 개수

K, N = map(int, input().split())

# 각 세션의 순위 저장
sessions = []
for _ in range(K):
    ranking = list(map(int, input().split()))
    sessions.append(ranking)

# 각 쌍에 대해 일관성 확인
count = 0

for i in range(1, N + 1):
    for j in range(i + 1, N + 1):
        # i와 j의 모든 세션에서의 순위 비교
        consistent = True
        first_better = None

        for s in sessions:
            pos_i = s.index(i)
            pos_j = s.index(j)

            if first_better is None:
                first_better = pos_i < pos_j
            elif (pos_i < pos_j) != first_better:
                consistent = False
                break

        if consistent:
            count += 1

print(count)
''',
        "java": '''import java.util.Scanner;

// 백준 18268: Cow Gymnastics
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int K = sc.nextInt();
        int N = sc.nextInt();

        int[][] rank = new int[K][N + 1];  // rank[k][cow] = cow의 k번째 세션 순위

        for (int k = 0; k < K; k++) {
            for (int pos = 0; pos < N; pos++) {
                int cow = sc.nextInt();
                rank[k][cow] = pos;
            }
        }

        int count = 0;
        for (int i = 1; i <= N; i++) {
            for (int j = i + 1; j <= N; j++) {
                boolean consistent = true;
                boolean iFirst = rank[0][i] < rank[0][j];

                for (int k = 1; k < K; k++) {
                    if ((rank[k][i] < rank[k][j]) != iFirst) {
                        consistent = false;
                        break;
                    }
                }

                if (consistent) count++;
            }
        }

        System.out.println(count);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 18268: Cow Gymnastics
int main() {
    int K, N;
    cin >> K >> N;

    int rank[10][21];  // rank[k][cow] = cow의 k번째 세션 순위

    for (int k = 0; k < K; k++) {
        for (int pos = 0; pos < N; pos++) {
            int cow;
            cin >> cow;
            rank[k][cow] = pos;
        }
    }

    int count = 0;
    for (int i = 1; i <= N; i++) {
        for (int j = i + 1; j <= N; j++) {
            bool consistent = true;
            bool iFirst = rank[0][i] < rank[0][j];

            for (int k = 1; k < K; k++) {
                if ((rank[k][i] < rank[k][j]) != iFirst) {
                    consistent = false;
                    break;
                }
            }

            if (consistent) count++;
        }
    }

    cout << count << endl;

    return 0;
}
'''
    },

    # 20650: Do You Know Your ABCs?
    "20650": {
        "python": '''# 백준 20650: Do You Know Your ABCs?
# 7개의 수에서 A, B, C 찾기

nums = list(map(int, input().split()))
nums.sort()

# A <= B <= C
# 가장 작은 것들 중에서 A, B를 찾고
# A + B + C가 가장 큰 수

for a in nums:
    for b in nums:
        if a <= b:
            c = nums[-1] - a - b  # A + B + C = 가장 큰 수
            if c >= b and c in nums:
                # A, B, C, A+B, B+C, C+A, A+B+C 확인
                check = [a, b, c, a+b, b+c, c+a, a+b+c]
                check.sort()
                if check == nums:
                    print(a, b, c)
                    exit()
''',
        "java": '''import java.util.*;

// 백준 20650: Do You Know Your ABCs?
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int[] nums = new int[7];
        for (int i = 0; i < 7; i++) {
            nums[i] = sc.nextInt();
        }
        Arrays.sort(nums);

        for (int a : nums) {
            for (int b : nums) {
                if (a <= b) {
                    int c = nums[6] - a - b;
                    if (c >= b) {
                        int[] check = {a, b, c, a+b, b+c, c+a, a+b+c};
                        Arrays.sort(check);
                        if (Arrays.equals(check, nums)) {
                            System.out.println(a + " " + b + " " + c);
                            return;
                        }
                    }
                }
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
using namespace std;

// 백준 20650: Do You Know Your ABCs?
int main() {
    int nums[7];
    for (int i = 0; i < 7; i++) {
        cin >> nums[i];
    }
    sort(nums, nums + 7);

    for (int i = 0; i < 7; i++) {
        for (int j = 0; j < 7; j++) {
            int a = nums[i], b = nums[j];
            if (a <= b) {
                int c = nums[6] - a - b;
                if (c >= b) {
                    int check[7] = {a, b, c, a+b, b+c, c+a, a+b+c};
                    sort(check, check + 7);
                    bool match = true;
                    for (int k = 0; k < 7; k++) {
                        if (check[k] != nums[k]) {
                            match = false;
                            break;
                        }
                    }
                    if (match) {
                        cout << a << " " << b << " " << c << endl;
                        return 0;
                    }
                }
            }
        }
    }

    return 0;
}
'''
    },

    # 10275: 골드 러시
    "10275": {
        "python": '''# 백준 10275: 골드 러시
# 2^n을 a와 b로 나누기 위한 최소 일수 (반으로 자르기)

T = int(input())
for _ in range(T):
    n, a, b = map(int, input().split())

    # a + b = 2^n
    # a와 b를 이진수로 표현했을 때 1의 개수가 필요한 조각 수
    # 최소 일수 = 1의 개수 - 1 (처음 하나는 자르지 않아도 됨)

    # a의 이진수 표현에서 1의 개수
    count = bin(a).count('1')

    print(count - 1)
''',
        "java": '''import java.util.Scanner;

// 백준 10275: 골드 러시
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            int n = sc.nextInt();
            long a = sc.nextLong();
            long b = sc.nextLong();

            // a의 이진수 표현에서 1의 개수 - 1
            int count = Long.bitCount(a);
            System.out.println(count - 1);
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 10275: 골드 러시
int main() {
    int T;
    cin >> T;

    while (T--) {
        int n;
        long long a, b;
        cin >> n >> a >> b;

        // a의 이진수 표현에서 1의 개수 - 1
        int count = __builtin_popcountll(a);
        cout << count - 1 << endl;
    }

    return 0;
}
'''
    },

    # 14530: The Lost Cow
    "14530": {
        "python": '''# 백준 14530: The Lost Cow
# FJ가 Bessie를 찾기 위해 이동한 거리

x, y = map(int, input().split())

# 1, -2, 4, -8, 16, ... 방향으로 이동
# 시작: x
# 1단계: x+1, 2단계: x-2, 3단계: x+4, ...

pos = x
dist = 0
step = 1
direction = 1

while True:
    next_pos = x + direction * step

    if direction == 1:
        # 오른쪽으로 이동
        if x <= y <= next_pos or pos <= y <= next_pos:
            dist += abs(y - pos)
            break
    else:
        # 왼쪽으로 이동
        if next_pos <= y <= x or next_pos <= y <= pos:
            dist += abs(y - pos)
            break

    dist += abs(next_pos - pos)
    pos = next_pos
    direction *= -1
    step *= 2

print(dist)
''',
        "java": '''import java.util.Scanner;

// 백준 14530: The Lost Cow
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int x = sc.nextInt();
        int y = sc.nextInt();

        long pos = x;
        long dist = 0;
        int step = 1;
        int dir = 1;

        while (true) {
            long nextPos = x + (long) dir * step;

            if (dir == 1) {
                if ((pos <= y && y <= nextPos) || (x <= y && y <= nextPos)) {
                    dist += Math.abs(y - pos);
                    break;
                }
            } else {
                if ((nextPos <= y && y <= pos) || (nextPos <= y && y <= x)) {
                    dist += Math.abs(y - pos);
                    break;
                }
            }

            dist += Math.abs(nextPos - pos);
            pos = nextPos;
            dir *= -1;
            step *= 2;
        }

        System.out.println(dist);
    }
}
''',
        "cpp": '''#include <iostream>
#include <cmath>
using namespace std;

// 백준 14530: The Lost Cow
int main() {
    long long x, y;
    cin >> x >> y;

    long long pos = x;
    long long dist = 0;
    long long step = 1;
    int dir = 1;

    while (true) {
        long long nextPos = x + dir * step;

        if (dir == 1) {
            if ((pos <= y && y <= nextPos) || (x <= y && y <= nextPos)) {
                dist += abs(y - pos);
                break;
            }
        } else {
            if ((nextPos <= y && y <= pos) || (nextPos <= y && y <= x)) {
                dist += abs(y - pos);
                break;
            }
        }

        dist += abs(nextPos - pos);
        pos = nextPos;
        dir *= -1;
        step *= 2;
    }

    cout << dist << endl;

    return 0;
}
'''
    },

    # 28063: 동전 복사
    "28063": {
        "python": '''# 백준 28063: 동전 복사
# N x N 판에서 (x, y) 위치의 동전으로 전체를 채우는 최소 작동 횟수

N = int(input())
x, y = map(int, input().split())

if N == 1:
    print(0)
else:
    # 상하좌우로 확장
    # 필요한 방향 수 계산
    dirs = 0
    if x > 1:
        dirs += 1  # 왼쪽
    if x < N:
        dirs += 1  # 오른쪽
    if y > 1:
        dirs += 1  # 아래
    if y < N:
        dirs += 1  # 위
    print(dirs)
''',
        "java": '''import java.util.Scanner;

// 백준 28063: 동전 복사
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int x = sc.nextInt();
        int y = sc.nextInt();

        if (N == 1) {
            System.out.println(0);
        } else {
            int dirs = 0;
            if (x > 1) dirs++;
            if (x < N) dirs++;
            if (y > 1) dirs++;
            if (y < N) dirs++;
            System.out.println(dirs);
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 28063: 동전 복사
int main() {
    int N, x, y;
    cin >> N >> x >> y;

    if (N == 1) {
        cout << 0 << endl;
    } else {
        int dirs = 0;
        if (x > 1) dirs++;
        if (x < N) dirs++;
        if (y > 1) dirs++;
        if (y < N) dirs++;
        cout << dirs << endl;
    }

    return 0;
}
'''
    },

    # 16770: The Bucket List
    "16770": {
        "python": '''# 백준 16770: The Bucket List
# 동시에 필요한 최대 버킷 수

N = int(input())
events = []

for _ in range(N):
    s, t, b = map(int, input().split())
    events.append((s, b))   # 시작: 버킷 필요
    events.append((t, -b))  # 종료: 버킷 반환

events.sort()

current = 0
max_buckets = 0

for time, buckets in events:
    current += buckets
    max_buckets = max(max_buckets, current)

print(max_buckets)
''',
        "java": '''import java.util.*;

// 백준 16770: The Bucket List
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        int[] timeline = new int[1001];

        for (int i = 0; i < N; i++) {
            int s = sc.nextInt();
            int t = sc.nextInt();
            int b = sc.nextInt();

            for (int j = s; j < t; j++) {
                timeline[j] += b;
            }
        }

        int max = 0;
        for (int i = 0; i <= 1000; i++) {
            max = Math.max(max, timeline[i]);
        }

        System.out.println(max);
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
using namespace std;

// 백준 16770: The Bucket List
int main() {
    int N;
    cin >> N;

    int timeline[1001] = {0};

    for (int i = 0; i < N; i++) {
        int s, t, b;
        cin >> s >> t >> b;

        for (int j = s; j < t; j++) {
            timeline[j] += b;
        }
    }

    int maxBuckets = 0;
    for (int i = 0; i <= 1000; i++) {
        maxBuckets = max(maxBuckets, timeline[i]);
    }

    cout << maxBuckets << endl;

    return 0;
}
'''
    },

    # 27951: 옷걸이
    "27951": {
        "python": '''# 백준 27951: 옷걸이
# 상의(U)와 하의(D)를 옷걸이에 배정

N = int(input())
hangers = list(map(int, input().split()))
U, D = map(int, input().split())

# 1: 상의 전용, 2: 하의 전용, 3: 둘 다 가능

up_only = hangers.count(1)
down_only = hangers.count(2)
both = hangers.count(3)

# 상의 전용에 상의 먼저 배치
use_up = min(up_only, U)
U -= use_up

# 하의 전용에 하의 먼저 배치
use_down = min(down_only, D)
D -= use_down

# 남은 상의와 하의를 둘 다 가능한 옷걸이에 배치
if U + D <= both:
    # 가능
    result = []
    for h in hangers:
        if h == 1:
            if use_up > 0:
                result.append('U')
                use_up -= 1
            else:
                result.append('U')  # 빈 상태지만 U로 표시
        elif h == 2:
            if use_down > 0:
                result.append('D')
                use_down -= 1
            else:
                result.append('D')
        else:  # h == 3
            if U > 0:
                result.append('U')
                U -= 1
            elif D > 0:
                result.append('D')
                D -= 1
            else:
                result.append('U')  # 아무거나

    print("YES")
    print(''.join(result))
else:
    print("NO")
''',
        "java": '''import java.util.*;

// 백준 27951: 옷걸이
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] hangers = new int[N];

        int upOnly = 0, downOnly = 0, both = 0;
        for (int i = 0; i < N; i++) {
            hangers[i] = sc.nextInt();
            if (hangers[i] == 1) upOnly++;
            else if (hangers[i] == 2) downOnly++;
            else both++;
        }

        int U = sc.nextInt();
        int D = sc.nextInt();

        int useUp = Math.min(upOnly, U);
        U -= useUp;

        int useDown = Math.min(downOnly, D);
        D -= useDown;

        if (U + D <= both) {
            StringBuilder result = new StringBuilder();
            int u = useUp, d = useDown;

            for (int h : hangers) {
                if (h == 1) {
                    result.append('U');
                } else if (h == 2) {
                    result.append('D');
                } else {
                    if (U > 0) {
                        result.append('U');
                        U--;
                    } else if (D > 0) {
                        result.append('D');
                        D--;
                    } else {
                        result.append('U');
                    }
                }
            }
            System.out.println("YES");
            System.out.println(result);
        } else {
            System.out.println("NO");
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

// 백준 27951: 옷걸이
int main() {
    int N;
    cin >> N;

    int hangers[N];
    int upOnly = 0, downOnly = 0, both = 0;

    for (int i = 0; i < N; i++) {
        cin >> hangers[i];
        if (hangers[i] == 1) upOnly++;
        else if (hangers[i] == 2) downOnly++;
        else both++;
    }

    int U, D;
    cin >> U >> D;

    int useUp = min(upOnly, U);
    U -= useUp;

    int useDown = min(downOnly, D);
    D -= useDown;

    if (U + D <= both) {
        string result;
        for (int i = 0; i < N; i++) {
            if (hangers[i] == 1) {
                result += 'U';
            } else if (hangers[i] == 2) {
                result += 'D';
            } else {
                if (U > 0) {
                    result += 'U';
                    U--;
                } else if (D > 0) {
                    result += 'D';
                    D--;
                } else {
                    result += 'U';
                }
            }
        }
        cout << "YES" << endl;
        cout << result << endl;
    } else {
        cout << "NO" << endl;
    }

    return 0;
}
'''
    },

    # 18269: Where Am I?
    "18269": {
        "python": '''# 백준 18269: Where Am I?
# 위치를 유일하게 결정할 수 있는 최소 부분 문자열 길이

N = int(input())
S = input().strip()

for k in range(1, N + 1):
    substrings = set()
    unique = True
    for i in range(N - k + 1):
        sub = S[i:i+k]
        if sub in substrings:
            unique = False
            break
        substrings.add(sub)

    if unique:
        print(k)
        break
''',
        "java": '''import java.util.*;

// 백준 18269: Where Am I?
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        String S = sc.next();

        for (int k = 1; k <= N; k++) {
            Set<String> substrings = new HashSet<>();
            boolean unique = true;
            for (int i = 0; i <= N - k; i++) {
                String sub = S.substring(i, i + k);
                if (substrings.contains(sub)) {
                    unique = false;
                    break;
                }
                substrings.add(sub);
            }
            if (unique) {
                System.out.println(k);
                break;
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <set>
using namespace std;

// 백준 18269: Where Am I?
int main() {
    int N;
    cin >> N;
    string S;
    cin >> S;

    for (int k = 1; k <= N; k++) {
        set<string> substrings;
        bool unique = true;
        for (int i = 0; i <= N - k; i++) {
            string sub = S.substr(i, k);
            if (substrings.count(sub)) {
                unique = false;
                break;
            }
            substrings.insert(sub);
        }
        if (unique) {
            cout << k << endl;
            break;
        }
    }

    return 0;
}
'''
    },

    # 18786: Triangles (Bronze)
    "18786": {
        "python": '''# 백준 18786: Triangles (Bronze)
# x축과 y축에 평행한 변을 가진 직각삼각형의 최대 면적

N = int(input())
points = []
for _ in range(N):
    x, y = map(int, input().split())
    points.append((x, y))

max_area = 0

for i in range(N):
    for j in range(N):
        for k in range(N):
            if i == j or j == k or i == k:
                continue

            x1, y1 = points[i]
            x2, y2 = points[j]
            x3, y3 = points[k]

            # 직각 꼭짓점이 (x1, y1)이고, 한 변이 x축 평행, 다른 변이 y축 평행
            if x1 == x2 and y1 == y3:
                width = abs(x3 - x1)
                height = abs(y2 - y1)
                area = width * height
                max_area = max(max_area, area)

print(max_area)
''',
        "java": '''import java.util.*;

// 백준 18786: Triangles (Bronze)
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[][] points = new int[N][2];

        for (int i = 0; i < N; i++) {
            points[i][0] = sc.nextInt();
            points[i][1] = sc.nextInt();
        }

        int maxArea = 0;

        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                for (int k = 0; k < N; k++) {
                    if (i == j || j == k || i == k) continue;

                    int x1 = points[i][0], y1 = points[i][1];
                    int x2 = points[j][0], y2 = points[j][1];
                    int x3 = points[k][0], y3 = points[k][1];

                    if (x1 == x2 && y1 == y3) {
                        int width = Math.abs(x3 - x1);
                        int height = Math.abs(y2 - y1);
                        maxArea = Math.max(maxArea, width * height);
                    }
                }
            }
        }

        System.out.println(maxArea);
    }
}
''',
        "cpp": '''#include <iostream>
#include <algorithm>
using namespace std;

// 백준 18786: Triangles (Bronze)
int main() {
    int N;
    cin >> N;
    int points[100][2];

    for (int i = 0; i < N; i++) {
        cin >> points[i][0] >> points[i][1];
    }

    int maxArea = 0;

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = 0; k < N; k++) {
                if (i == j || j == k || i == k) continue;

                int x1 = points[i][0], y1 = points[i][1];
                int x2 = points[j][0], y2 = points[j][1];
                int x3 = points[k][0], y3 = points[k][1];

                if (x1 == x2 && y1 == y3) {
                    int width = abs(x3 - x1);
                    int height = abs(y2 - y1);
                    maxArea = max(maxArea, width * height);
                }
            }
        }
    }

    cout << maxArea << endl;

    return 0;
}
'''
    },

    # 19575: Polynomial (호너 법칙)
    "19575": {
        "python": '''# 백준 19575: Polynomial
# 호너 법칙으로 다항식 계산

import sys
input = sys.stdin.readline

MOD = 10**9 + 7

first_line = input().split()
N = int(first_line[0])
x = int(first_line[1])

result = 0
for _ in range(N + 1):
    line = input().split()
    a = int(line[0])
    result = (result * x + a) % MOD

print(result)
''',
        "java": '''import java.io.*;
import java.util.*;

// 백준 19575: Polynomial (호너 법칙)
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        long x = Long.parseLong(st.nextToken());
        long MOD = 1000000007L;

        long result = 0;
        for (int i = 0; i <= N; i++) {
            st = new StringTokenizer(br.readLine());
            long a = Long.parseLong(st.nextToken());
            result = (result * x + a) % MOD;
        }

        System.out.println(result);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 19575: Polynomial (호너 법칙)
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    long long x;
    cin >> N >> x;

    const long long MOD = 1000000007;
    long long result = 0;

    for (int i = 0; i <= N; i++) {
        long long a, e;
        cin >> a >> e;
        result = (result * x + a) % MOD;
    }

    cout << result << endl;

    return 0;
}
'''
    },
}


def main():
    # JSON 파일 읽기
    filepath = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 솔루션이 비어있고 difficulty가 easy인 문제들 찾기
    empty_easy_indices = []
    for i, prob in enumerate(data):
        if prob.get('solutions') == [] and prob.get('difficulty') == 'easy':
            empty_easy_indices.append(i)

    print(f"Total empty easy problems: {len(empty_easy_indices)}")

    # 솔루션 추가
    updated_count = 0
    for idx in empty_easy_indices:
        prob = data[idx]
        original_id = prob.get('original_id')

        if original_id in SOLUTIONS_PART2:
            sol = SOLUTIONS_PART2[original_id]
            data[idx]['solutions'] = [
                {"language": "python", "code": sol["python"]},
                {"language": "java", "code": sol["java"]},
                {"language": "cpp", "code": sol["cpp"]}
            ]
            updated_count += 1
            print(f"Updated: {original_id} - {prob.get('name')}")

    # 파일 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nTotal updated: {updated_count}")
    print(f"Remaining empty easy problems: {len(empty_easy_indices) - updated_count}")


if __name__ == '__main__':
    main()
