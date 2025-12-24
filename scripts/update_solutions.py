#!/usr/bin/env python3
"""
백준 문제 솔루션 생성 및 업데이트 스크립트
difficulty가 "easy"이고 solutions가 비어있는 문제들에 대해
Python, Java, C++ 솔루션을 생성합니다.
"""

import json

# 솔루션 정의 (문제 ID별)
SOLUTIONS = {
    # 1975: Number Game - N의 약수 개수에서 1을 뺀 값
    "1975": {
        "python": '''# 백준 1975: Number Game
# N을 b진법으로 나타냈을 때 마지막에 따르는 연속된 0의 개수의 합
# 이는 N의 약수 개수에서 1을 뺀 값과 같다 (1은 제외)

def count_divisors(n):
    # N의 약수 개수를 구한다
    count = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            count += 1
            if i != n // i:
                count += 1
        i += 1
    return count

T = int(input())
for _ in range(T):
    N = int(input())
    # 약수 개수에서 1을 뺀다 (N 자신은 base가 N보다 클 때 한 자리가 됨)
    print(count_divisors(N) - 1)
''',
        "java": '''import java.util.Scanner;

// 백준 1975: Number Game
// N을 b진법으로 나타냈을 때 마지막에 따르는 연속된 0의 개수의 합
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            int N = sc.nextInt();
            // 약수 개수에서 1을 뺀다
            int count = 0;
            for (int i = 1; i * i <= N; i++) {
                if (N % i == 0) {
                    count++;
                    if (i != N / i) {
                        count++;
                    }
                }
            }
            System.out.println(count - 1);
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 1975: Number Game
// N을 b진법으로 나타냈을 때 마지막에 따르는 연속된 0의 개수의 합
int main() {
    int T;
    cin >> T;

    while (T--) {
        int N;
        cin >> N;

        // 약수 개수를 구한다
        int count = 0;
        for (int i = 1; i * i <= N; i++) {
            if (N % i == 0) {
                count++;
                if (i != N / i) {
                    count++;
                }
            }
        }
        // 약수 개수에서 1을 뺀다
        cout << count - 1 << endl;
    }

    return 0;
}
'''
    },

    # 31432: 소수가 아닌 수 3 - 0이 있으면 0, 아니면 같은 숫자 반복
    "31432": {
        "python": '''# 백준 31432: 소수가 아닌 수 3
# 주어진 숫자들로 소수가 아닌 수를 만든다
# 0이 있으면 0 출력, 1이 있으면 1 출력
# 그 외에는 같은 숫자를 여러 번 반복하면 합성수가 됨 (예: 22, 33, 44...)

N = int(input())
digits = list(map(int, input().split()))

# 0이 있으면 0은 소수가 아님
if 0 in digits:
    print("YES")
    print(0)
# 1이 있으면 1은 소수가 아님
elif 1 in digits:
    print("YES")
    print(1)
else:
    # 같은 숫자를 두 번 반복하면 11의 배수가 됨 (예: 22 = 11*2)
    print("YES")
    d = digits[0]
    print(str(d) * 2)
''',
        "java": '''import java.util.Scanner;

// 백준 31432: 소수가 아닌 수 3
// 주어진 숫자들로 소수가 아닌 수를 만든다
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] digits = new int[N];

        boolean hasZero = false;
        boolean hasOne = false;
        int first = -1;

        for (int i = 0; i < N; i++) {
            digits[i] = sc.nextInt();
            if (digits[i] == 0) hasZero = true;
            if (digits[i] == 1) hasOne = true;
            if (first == -1) first = digits[i];
        }

        System.out.println("YES");
        if (hasZero) {
            System.out.println(0);
        } else if (hasOne) {
            System.out.println(1);
        } else {
            // 같은 숫자 두 번 반복 (11의 배수)
            System.out.println("" + first + first);
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 31432: 소수가 아닌 수 3
// 주어진 숫자들로 소수가 아닌 수를 만든다
int main() {
    int N;
    cin >> N;

    bool hasZero = false, hasOne = false;
    int first = -1;

    for (int i = 0; i < N; i++) {
        int d;
        cin >> d;
        if (d == 0) hasZero = true;
        if (d == 1) hasOne = true;
        if (first == -1) first = d;
    }

    cout << "YES" << endl;
    if (hasZero) {
        cout << 0 << endl;
    } else if (hasOne) {
        cout << 1 << endl;
    } else {
        // 같은 숫자 두 번 반복
        cout << first << first << endl;
    }

    return 0;
}
'''
    },

    # 16675: 두 개의 손 - 가위바위보
    "16675": {
        "python": '''# 백준 16675: 두 개의 손
# 민성이 또는 태경이가 무조건 이기는 방법이 있는지 판별

def wins(a, b):
    # a가 b를 이기는지 확인
    # S(가위)는 P(보)를 이김, R(바위)는 S를 이김, P(보)는 R을 이김
    return (a == 'S' and b == 'P') or (a == 'R' and b == 'S') or (a == 'P' and b == 'R')

ML, MR, TL, TR = input().split()

# 민성이가 무조건 이기려면: 태경이 양손 모두 같고, 민성이 중 하나가 그걸 이김
ms_wins = False
if TL == TR:
    if wins(ML, TL) or wins(MR, TL):
        ms_wins = True

# 태경이가 무조건 이기려면: 민성이 양손 모두 같고, 태경이 중 하나가 그걸 이김
tk_wins = False
if ML == MR:
    if wins(TL, ML) or wins(TR, ML):
        tk_wins = True

if ms_wins and not tk_wins:
    print("MS")
elif tk_wins and not ms_wins:
    print("TK")
else:
    print("?")
''',
        "java": '''import java.util.Scanner;

// 백준 16675: 두 개의 손
// 민성이 또는 태경이가 무조건 이기는 방법이 있는지 판별
public class Main {
    static boolean wins(char a, char b) {
        // a가 b를 이기는지 확인
        return (a == 'S' && b == 'P') || (a == 'R' && b == 'S') || (a == 'P' && b == 'R');
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        char ML = sc.next().charAt(0);
        char MR = sc.next().charAt(0);
        char TL = sc.next().charAt(0);
        char TR = sc.next().charAt(0);

        // 민성이가 무조건 이기려면
        boolean msWins = false;
        if (TL == TR) {
            if (wins(ML, TL) || wins(MR, TL)) {
                msWins = true;
            }
        }

        // 태경이가 무조건 이기려면
        boolean tkWins = false;
        if (ML == MR) {
            if (wins(TL, ML) || wins(TR, ML)) {
                tkWins = true;
            }
        }

        if (msWins && !tkWins) {
            System.out.println("MS");
        } else if (tkWins && !msWins) {
            System.out.println("TK");
        } else {
            System.out.println("?");
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 16675: 두 개의 손
// a가 b를 이기는지 확인
bool wins(char a, char b) {
    return (a == 'S' && b == 'P') || (a == 'R' && b == 'S') || (a == 'P' && b == 'R');
}

int main() {
    char ML, MR, TL, TR;
    cin >> ML >> MR >> TL >> TR;

    // 민성이가 무조건 이기려면
    bool msWins = false;
    if (TL == TR) {
        if (wins(ML, TL) || wins(MR, TL)) {
            msWins = true;
        }
    }

    // 태경이가 무조건 이기려면
    bool tkWins = false;
    if (ML == MR) {
        if (wins(TL, ML) || wins(TR, ML)) {
            tkWins = true;
        }
    }

    if (msWins && !tkWins) {
        cout << "MS" << endl;
    } else if (tkWins && !msWins) {
        cout << "TK" << endl;
    } else {
        cout << "?" << endl;
    }

    return 0;
}
'''
    },

    # 1942: 디지털시계
    "1942": {
        "python": '''# 백준 1942: 디지털시계
# 시간 구간에서 3의 배수인 시계 정수의 개수를 구한다

def time_to_int(h, m, s):
    # hh:mm:ss를 시계 정수로 변환
    return h * 10000 + m * 100 + s

def count_multiples_of_3(h, m, s):
    # 00:00:00부터 h:m:s까지 3의 배수인 시계 정수 개수
    count = 0
    for hh in range(h + 1):
        for mm in range(60):
            for ss in range(60):
                if hh == h and mm * 60 + ss > m * 60 + s:
                    break
                if hh < h or (hh == h and mm < m) or (hh == h and mm == m and ss <= s):
                    val = hh * 10000 + mm * 100 + ss
                    if val % 3 == 0:
                        count += 1
    return count

def solve(start, end):
    sh, sm, ss = map(int, start.split(':'))
    eh, em, es = map(int, end.split(':'))

    count = 0
    if (sh, sm, ss) <= (eh, em, es):
        # 같은 날 구간
        for h in range(sh, eh + 1):
            for m in range(60):
                for s in range(60):
                    if (h, m, s) < (sh, sm, ss):
                        continue
                    if (h, m, s) > (eh, em, es):
                        break
                    val = h * 10000 + m * 100 + s
                    if val % 3 == 0:
                        count += 1
    else:
        # 자정을 넘는 구간
        # start ~ 23:59:59
        for h in range(sh, 24):
            for m in range(60):
                for s in range(60):
                    if (h, m, s) < (sh, sm, ss):
                        continue
                    val = h * 10000 + m * 100 + s
                    if val % 3 == 0:
                        count += 1
        # 00:00:00 ~ end
        for h in range(0, eh + 1):
            for m in range(60):
                for s in range(60):
                    if (h, m, s) > (eh, em, es):
                        break
                    val = h * 10000 + m * 100 + s
                    if val % 3 == 0:
                        count += 1

    return count

for _ in range(3):
    line = input().strip()
    parts = line.split()
    print(solve(parts[0], parts[1]))
''',
        "java": '''import java.util.Scanner;

// 백준 1942: 디지털시계
// 시간 구간에서 3의 배수인 시계 정수의 개수를 구한다
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        for (int t = 0; t < 3; t++) {
            String[] parts = sc.nextLine().split(" ");
            String[] start = parts[0].split(":");
            String[] end = parts[1].split(":");

            int sh = Integer.parseInt(start[0]);
            int sm = Integer.parseInt(start[1]);
            int ss = Integer.parseInt(start[2]);
            int eh = Integer.parseInt(end[0]);
            int em = Integer.parseInt(end[1]);
            int es = Integer.parseInt(end[2]);

            int count = 0;

            if (sh * 3600 + sm * 60 + ss <= eh * 3600 + em * 60 + es) {
                // 같은 날 구간
                for (int h = sh; h <= eh; h++) {
                    for (int m = 0; m < 60; m++) {
                        for (int s = 0; s < 60; s++) {
                            int cur = h * 3600 + m * 60 + s;
                            int startSec = sh * 3600 + sm * 60 + ss;
                            int endSec = eh * 3600 + em * 60 + es;
                            if (cur >= startSec && cur <= endSec) {
                                int val = h * 10000 + m * 100 + s;
                                if (val % 3 == 0) count++;
                            }
                        }
                    }
                }
            } else {
                // 자정을 넘는 구간
                for (int h = sh; h < 24; h++) {
                    for (int m = 0; m < 60; m++) {
                        for (int s = 0; s < 60; s++) {
                            int cur = h * 3600 + m * 60 + s;
                            int startSec = sh * 3600 + sm * 60 + ss;
                            if (cur >= startSec) {
                                int val = h * 10000 + m * 100 + s;
                                if (val % 3 == 0) count++;
                            }
                        }
                    }
                }
                for (int h = 0; h <= eh; h++) {
                    for (int m = 0; m < 60; m++) {
                        for (int s = 0; s < 60; s++) {
                            int cur = h * 3600 + m * 60 + s;
                            int endSec = eh * 3600 + em * 60 + es;
                            if (cur <= endSec) {
                                int val = h * 10000 + m * 100 + s;
                                if (val % 3 == 0) count++;
                            }
                        }
                    }
                }
            }

            System.out.println(count);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

// 백준 1942: 디지털시계
int main() {
    for (int t = 0; t < 3; t++) {
        int sh, sm, ss, eh, em, es;
        char c;
        cin >> sh >> c >> sm >> c >> ss >> eh >> c >> em >> c >> es;

        int count = 0;
        int startSec = sh * 3600 + sm * 60 + ss;
        int endSec = eh * 3600 + em * 60 + es;

        if (startSec <= endSec) {
            // 같은 날 구간
            for (int sec = startSec; sec <= endSec; sec++) {
                int h = sec / 3600;
                int m = (sec % 3600) / 60;
                int s = sec % 60;
                int val = h * 10000 + m * 100 + s;
                if (val % 3 == 0) count++;
            }
        } else {
            // 자정을 넘는 구간
            for (int sec = startSec; sec < 86400; sec++) {
                int h = sec / 3600;
                int m = (sec % 3600) / 60;
                int s = sec % 60;
                int val = h * 10000 + m * 100 + s;
                if (val % 3 == 0) count++;
            }
            for (int sec = 0; sec <= endSec; sec++) {
                int h = sec / 3600;
                int m = (sec % 3600) / 60;
                int s = sec % 60;
                int val = h * 10000 + m * 100 + s;
                if (val % 3 == 0) count++;
            }
        }

        cout << count << endl;
    }

    return 0;
}
'''
    },

    # 13322: 접두사 배열
    "13322": {
        "python": '''# 백준 13322: 접두사 배열
# 접두사를 사전순으로 정렬하면 길이순으로 정렬된다
# 따라서 접두사 배열은 단순히 0, 1, 2, ..., n-1

s = input().strip()
for i in range(len(s)):
    print(i)
''',
        "java": '''import java.util.Scanner;

// 백준 13322: 접두사 배열
// 접두사를 사전순으로 정렬하면 길이순으로 정렬된다
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            sb.append(i).append("\\n");
        }
        System.out.print(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

// 백준 13322: 접두사 배열
// 접두사를 사전순으로 정렬하면 길이순으로 정렬된다
int main() {
    string s;
    cin >> s;

    for (int i = 0; i < s.length(); i++) {
        cout << i << "\\n";
    }

    return 0;
}
'''
    },

    # 14614: Calculate! - XOR 연산
    "14614": {
        "python": '''# 백준 14614: Calculate!
# A에 B를 C번 XOR한 결과
# XOR의 성질: A ^ B ^ B = A
# 따라서 C가 홀수면 A ^ B, 짝수면 A

A, B, C = input().split()
A = int(A)
B = int(B)

# C가 매우 큰 수일 수 있으므로 마지막 자릿수만 확인
# (짝수/홀수 판별)
if int(C[-1]) % 2 == 1:
    print(A ^ B)
else:
    print(A)
''',
        "java": '''import java.util.Scanner;
import java.math.BigInteger;

// 백준 14614: Calculate!
// A에 B를 C번 XOR한 결과
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int A = sc.nextInt();
        int B = sc.nextInt();
        String C = sc.next();

        // C가 매우 큰 수일 수 있으므로 마지막 자릿수만 확인
        int lastDigit = C.charAt(C.length() - 1) - '0';

        if (lastDigit % 2 == 1) {
            System.out.println(A ^ B);
        } else {
            System.out.println(A);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

// 백준 14614: Calculate!
// A에 B를 C번 XOR한 결과
int main() {
    int A, B;
    string C;
    cin >> A >> B >> C;

    // C가 매우 큰 수일 수 있으므로 마지막 자릿수만 확인
    int lastDigit = C[C.length() - 1] - '0';

    if (lastDigit % 2 == 1) {
        cout << (A ^ B) << endl;
    } else {
        cout << A << endl;
    }

    return 0;
}
'''
    },

    # 27865: 랜덤 게임? (인터랙티브)
    "27865": {
        "python": '''# 백준 27865: 랜덤 게임?
# 같은 숫자를 계속 질문하면 언젠가 맞춘다

import sys

N = int(input())

while True:
    print("? 1", flush=True)
    response = input().strip()
    if response == "Y":
        print("! 1", flush=True)
        break
''',
        "java": '''import java.util.Scanner;

// 백준 27865: 랜덤 게임?
// 같은 숫자를 계속 질문하면 언젠가 맞춘다
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        while (true) {
            System.out.println("? 1");
            System.out.flush();
            String response = sc.next();
            if (response.equals("Y")) {
                System.out.println("! 1");
                System.out.flush();
                break;
            }
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 27865: 랜덤 게임?
// 같은 숫자를 계속 질문하면 언젠가 맞춘다
int main() {
    int N;
    cin >> N;

    while (true) {
        cout << "? 1" << endl;
        cout.flush();
        char response;
        cin >> response;
        if (response == 'Y') {
            cout << "! 1" << endl;
            cout.flush();
            break;
        }
    }

    return 0;
}
'''
    },

    # 23885: 비숍 투어
    "23885": {
        "python": '''# 백준 23885: 비숍 투어
# 비숍은 대각선으로만 이동하므로 (x+y)의 홀짝성이 같아야 이동 가능

N, M = map(int, input().split())
sx, sy = map(int, input().split())
ex, ey = map(int, input().split())

# (x + y)의 홀짝성이 같으면 이동 가능
if (sx + sy) % 2 == (ex + ey) % 2:
    print("YES")
else:
    print("NO")
''',
        "java": '''import java.util.Scanner;

// 백준 23885: 비숍 투어
// 비숍은 대각선으로만 이동하므로 (x+y)의 홀짝성이 같아야 이동 가능
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int M = sc.nextInt();
        int sx = sc.nextInt();
        int sy = sc.nextInt();
        int ex = sc.nextInt();
        int ey = sc.nextInt();

        if ((sx + sy) % 2 == (ex + ey) % 2) {
            System.out.println("YES");
        } else {
            System.out.println("NO");
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 23885: 비숍 투어
// 비숍은 대각선으로만 이동하므로 (x+y)의 홀짝성이 같아야 이동 가능
int main() {
    int N, M, sx, sy, ex, ey;
    cin >> N >> M >> sx >> sy >> ex >> ey;

    if ((sx + sy) % 2 == (ex + ey) % 2) {
        cout << "YES" << endl;
    } else {
        cout << "NO" << endl;
    }

    return 0;
}
'''
    },

    # 18868: 멀티버스 I
    "18868": {
        "python": '''# 백준 18868: 멀티버스 I
# 두 우주가 균등한지 확인 (모든 쌍의 대소관계가 같으면 균등)

def get_pattern(arr):
    # 모든 쌍의 대소관계를 튜플로 저장
    n = len(arr)
    pattern = []
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] < arr[j]:
                pattern.append(-1)
            elif arr[i] > arr[j]:
                pattern.append(1)
            else:
                pattern.append(0)
    return tuple(pattern)

M, N = map(int, input().split())
universes = []

for _ in range(M):
    arr = list(map(int, input().split()))
    universes.append(get_pattern(arr))

count = 0
for i in range(M):
    for j in range(i + 1, M):
        if universes[i] == universes[j]:
            count += 1

print(count)
''',
        "java": '''import java.util.*;

// 백준 18868: 멀티버스 I
// 두 우주가 균등한지 확인
public class Main {
    static String getPattern(int[] arr) {
        StringBuilder sb = new StringBuilder();
        int n = arr.length;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (arr[i] < arr[j]) sb.append("-");
                else if (arr[i] > arr[j]) sb.append("+");
                else sb.append("0");
            }
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int M = sc.nextInt();
        int N = sc.nextInt();

        String[] patterns = new String[M];
        for (int i = 0; i < M; i++) {
            int[] arr = new int[N];
            for (int j = 0; j < N; j++) {
                arr[j] = sc.nextInt();
            }
            patterns[i] = getPattern(arr);
        }

        int count = 0;
        for (int i = 0; i < M; i++) {
            for (int j = i + 1; j < M; j++) {
                if (patterns[i].equals(patterns[j])) {
                    count++;
                }
            }
        }

        System.out.println(count);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
#include <string>
using namespace std;

// 백준 18868: 멀티버스 I
string getPattern(vector<int>& arr) {
    string pattern;
    int n = arr.size();
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (arr[i] < arr[j]) pattern += '-';
            else if (arr[i] > arr[j]) pattern += '+';
            else pattern += '0';
        }
    }
    return pattern;
}

int main() {
    int M, N;
    cin >> M >> N;

    vector<string> patterns(M);
    for (int i = 0; i < M; i++) {
        vector<int> arr(N);
        for (int j = 0; j < N; j++) {
            cin >> arr[j];
        }
        patterns[i] = getPattern(arr);
    }

    int count = 0;
    for (int i = 0; i < M; i++) {
        for (int j = i + 1; j < M; j++) {
            if (patterns[i] == patterns[j]) {
                count++;
            }
        }
    }

    cout << count << endl;

    return 0;
}
'''
    },

    # 20113: 긴급 회의
    "20113": {
        "python": '''# 백준 20113: 긴급 회의
# 가장 표를 많이 받은 사람 퇴출, 동률이면 skipped

N = int(input())
votes = list(map(int, input().split()))

# 득표수 계산
count = [0] * (N + 1)
for v in votes:
    count[v] += 1

# 0번은 skip이므로 제외하고 최대 득표수 찾기
max_votes = 0
max_player = -1
tie = False

for i in range(1, N + 1):
    if count[i] > max_votes:
        max_votes = count[i]
        max_player = i
        tie = False
    elif count[i] == max_votes and max_votes > 0:
        tie = True

if max_votes == 0 or tie:
    print("skipped")
else:
    print(max_player)
''',
        "java": '''import java.util.Scanner;

// 백준 20113: 긴급 회의
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        int[] count = new int[N + 1];
        for (int i = 0; i < N; i++) {
            int v = sc.nextInt();
            count[v]++;
        }

        int maxVotes = 0;
        int maxPlayer = -1;
        boolean tie = false;

        for (int i = 1; i <= N; i++) {
            if (count[i] > maxVotes) {
                maxVotes = count[i];
                maxPlayer = i;
                tie = false;
            } else if (count[i] == maxVotes && maxVotes > 0) {
                tie = true;
            }
        }

        if (maxVotes == 0 || tie) {
            System.out.println("skipped");
        } else {
            System.out.println(maxPlayer);
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 20113: 긴급 회의
int main() {
    int N;
    cin >> N;

    int count[101] = {0};
    for (int i = 0; i < N; i++) {
        int v;
        cin >> v;
        count[v]++;
    }

    int maxVotes = 0;
    int maxPlayer = -1;
    bool tie = false;

    for (int i = 1; i <= N; i++) {
        if (count[i] > maxVotes) {
            maxVotes = count[i];
            maxPlayer = i;
            tie = false;
        } else if (count[i] == maxVotes && maxVotes > 0) {
            tie = true;
        }
    }

    if (maxVotes == 0 || tie) {
        cout << "skipped" << endl;
    } else {
        cout << maxPlayer << endl;
    }

    return 0;
}
'''
    },

    # 29196: 소수가 아닌 수 2 (분수 표현)
    "29196": {
        "python": '''# 백준 29196: 소수가 아닌 수 2
# 소수(decimal) k를 분수 p/q로 표현

k = input().strip()

# 소수점 아래 자릿수 확인
if '.' in k:
    integer_part, decimal_part = k.split('.')
    denominator = 10 ** len(decimal_part)
    numerator = int(integer_part) * denominator + int(decimal_part)
else:
    numerator = int(k)
    denominator = 1

# GCD로 기약분수 만들기
from math import gcd
g = gcd(numerator, denominator)
numerator //= g
denominator //= g

print("YES")
print(numerator, denominator)
''',
        "java": '''import java.util.Scanner;

// 백준 29196: 소수가 아닌 수 2
public class Main {
    static long gcd(long a, long b) {
        while (b != 0) {
            long t = b;
            b = a % b;
            a = t;
        }
        return a;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String k = sc.next();

        long numerator, denominator;

        if (k.contains(".")) {
            String[] parts = k.split("\\\\.");
            int decLen = parts[1].length();
            denominator = (long) Math.pow(10, decLen);
            numerator = Long.parseLong(parts[0]) * denominator + Long.parseLong(parts[1]);
        } else {
            numerator = Long.parseLong(k);
            denominator = 1;
        }

        long g = gcd(numerator, denominator);
        numerator /= g;
        denominator /= g;

        System.out.println("YES");
        System.out.println(numerator + " " + denominator);
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <cmath>
using namespace std;

// 백준 29196: 소수가 아닌 수 2
long long gcd(long long a, long long b) {
    while (b != 0) {
        long long t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int main() {
    string k;
    cin >> k;

    long long numerator, denominator;

    size_t dotPos = k.find('.');
    if (dotPos != string::npos) {
        string intPart = k.substr(0, dotPos);
        string decPart = k.substr(dotPos + 1);
        int decLen = decPart.length();
        denominator = (long long)pow(10, decLen);
        numerator = stoll(intPart) * denominator + stoll(decPart);
    } else {
        numerator = stoll(k);
        denominator = 1;
    }

    long long g = gcd(numerator, denominator);
    numerator /= g;
    denominator /= g;

    cout << "YES" << endl;
    cout << numerator << " " << denominator << endl;

    return 0;
}
'''
    },

    # 15593: Lifeguards (Bronze)
    "15593": {
        "python": '''# 백준 15593: Lifeguards (Bronze)
# N명의 lifeguard 중 1명을 해고할 때 최대 커버 시간

import sys
input = sys.stdin.readline

N = int(input())
shifts = []
for _ in range(N):
    s, e = map(int, input().split())
    shifts.append((s, e))

# 전체 시간을 배열로 표현 (0~999)
def get_coverage(excluded):
    timeline = [0] * 1001
    for i in range(N):
        if i == excluded:
            continue
        s, e = shifts[i]
        for t in range(s, e):
            timeline[t] = 1
    return sum(timeline)

# 각 lifeguard를 해고했을 때 커버리지 계산
max_coverage = 0
for i in range(N):
    coverage = get_coverage(i)
    max_coverage = max(max_coverage, coverage)

print(max_coverage)
''',
        "java": '''import java.util.Scanner;

// 백준 15593: Lifeguards (Bronze)
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        int[][] shifts = new int[N][2];
        for (int i = 0; i < N; i++) {
            shifts[i][0] = sc.nextInt();
            shifts[i][1] = sc.nextInt();
        }

        int maxCoverage = 0;

        for (int excluded = 0; excluded < N; excluded++) {
            int[] timeline = new int[1001];
            for (int i = 0; i < N; i++) {
                if (i == excluded) continue;
                for (int t = shifts[i][0]; t < shifts[i][1]; t++) {
                    timeline[t] = 1;
                }
            }
            int coverage = 0;
            for (int t = 0; t < 1001; t++) {
                coverage += timeline[t];
            }
            maxCoverage = Math.max(maxCoverage, coverage);
        }

        System.out.println(maxCoverage);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 15593: Lifeguards (Bronze)
int main() {
    int N;
    cin >> N;

    int shifts[100][2];
    for (int i = 0; i < N; i++) {
        cin >> shifts[i][0] >> shifts[i][1];
    }

    int maxCoverage = 0;

    for (int excluded = 0; excluded < N; excluded++) {
        int timeline[1001] = {0};
        for (int i = 0; i < N; i++) {
            if (i == excluded) continue;
            for (int t = shifts[i][0]; t < shifts[i][1]; t++) {
                timeline[t] = 1;
            }
        }
        int coverage = 0;
        for (int t = 0; t < 1001; t++) {
            coverage += timeline[t];
        }
        maxCoverage = max(maxCoverage, coverage);
    }

    cout << maxCoverage << endl;

    return 0;
}
'''
    },

    # 16360: Go Latin
    "16360": {
        "python": '''# 백준 16360: Go Latin
# 영어 단어를 pseudo-Latin으로 변환

n = int(input())

rules = [
    ('a', 'as'),
    ('i', 'ios'),
    ('y', 'ios'),
    ('l', 'les'),
    ('ne', 'anes'),
    ('n', 'anes'),
    ('o', 'os'),
    ('r', 'res'),
    ('t', 'tas'),
    ('u', 'us'),
    ('v', 'ves'),
    ('w', 'was')
]

for _ in range(n):
    word = input().strip()

    found = False
    # 먼저 2글자 규칙 확인
    if word.endswith('ne'):
        print(word[:-2] + 'anes')
        found = True
    elif not found:
        for suffix, replacement in rules:
            if len(suffix) == 1 and word.endswith(suffix):
                print(word[:-1] + replacement)
                found = True
                break

    if not found:
        print(word + 'us')
''',
        "java": '''import java.util.Scanner;

// 백준 16360: Go Latin
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = Integer.parseInt(sc.nextLine());

        for (int i = 0; i < n; i++) {
            String word = sc.nextLine();
            String result;

            if (word.endsWith("ne")) {
                result = word.substring(0, word.length() - 2) + "anes";
            } else if (word.endsWith("a")) {
                result = word.substring(0, word.length() - 1) + "as";
            } else if (word.endsWith("i") || word.endsWith("y")) {
                result = word.substring(0, word.length() - 1) + "ios";
            } else if (word.endsWith("l")) {
                result = word.substring(0, word.length() - 1) + "les";
            } else if (word.endsWith("n")) {
                result = word.substring(0, word.length() - 1) + "anes";
            } else if (word.endsWith("o")) {
                result = word.substring(0, word.length() - 1) + "os";
            } else if (word.endsWith("r")) {
                result = word.substring(0, word.length() - 1) + "res";
            } else if (word.endsWith("t")) {
                result = word.substring(0, word.length() - 1) + "tas";
            } else if (word.endsWith("u")) {
                result = word.substring(0, word.length() - 1) + "us";
            } else if (word.endsWith("v")) {
                result = word.substring(0, word.length() - 1) + "ves";
            } else if (word.endsWith("w")) {
                result = word.substring(0, word.length() - 1) + "was";
            } else {
                result = word + "us";
            }

            System.out.println(result);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

// 백준 16360: Go Latin
int main() {
    int n;
    cin >> n;

    while (n--) {
        string word;
        cin >> word;
        int len = word.length();
        string result;

        if (len >= 2 && word.substr(len - 2) == "ne") {
            result = word.substr(0, len - 2) + "anes";
        } else if (word[len - 1] == 'a') {
            result = word.substr(0, len - 1) + "as";
        } else if (word[len - 1] == 'i' || word[len - 1] == 'y') {
            result = word.substr(0, len - 1) + "ios";
        } else if (word[len - 1] == 'l') {
            result = word.substr(0, len - 1) + "les";
        } else if (word[len - 1] == 'n') {
            result = word.substr(0, len - 1) + "anes";
        } else if (word[len - 1] == 'o') {
            result = word.substr(0, len - 1) + "os";
        } else if (word[len - 1] == 'r') {
            result = word.substr(0, len - 1) + "res";
        } else if (word[len - 1] == 't') {
            result = word.substr(0, len - 1) + "tas";
        } else if (word[len - 1] == 'u') {
            result = word.substr(0, len - 1) + "us";
        } else if (word[len - 1] == 'v') {
            result = word.substr(0, len - 1) + "ves";
        } else if (word[len - 1] == 'w') {
            result = word.substr(0, len - 1) + "was";
        } else {
            result = word + "us";
        }

        cout << result << endl;
    }

    return 0;
}
'''
    },

    # 25373: 벼락치기 - 첫날 봐야 하는 영상 개수
    "25373": {
        "python": '''# 백준 25373: 벼락치기
# 첫날 k개를 보면 총 k + (k-1) + ... + 1 = k*(k+1)/2개 볼 수 있음
# N개 이상 보려면 k*(k+1)/2 >= N인 최소 k

import math

N = int(input())

# k*(k+1)/2 >= N
# k^2 + k - 2N >= 0
# k >= (-1 + sqrt(1 + 8N)) / 2

k = int((-1 + math.sqrt(1 + 8*N)) / 2)

# 확인
while k * (k + 1) // 2 < N:
    k += 1

print(k)
''',
        "java": '''import java.util.Scanner;

// 백준 25373: 벼락치기
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long N = sc.nextLong();

        // k*(k+1)/2 >= N인 최소 k
        long k = (long) ((-1 + Math.sqrt(1 + 8.0 * N)) / 2);

        while (k * (k + 1) / 2 < N) {
            k++;
        }

        System.out.println(k);
    }
}
''',
        "cpp": '''#include <iostream>
#include <cmath>
using namespace std;

// 백준 25373: 벼락치기
int main() {
    long long N;
    cin >> N;

    // k*(k+1)/2 >= N인 최소 k
    long long k = (long long)((-1 + sqrt(1 + 8.0 * N)) / 2);

    while (k * (k + 1) / 2 < N) {
        k++;
    }

    cout << k << endl;

    return 0;
}
'''
    },

    # 21965: 드높은 남산 위에 우뚝 선 (산 판별)
    "21965": {
        "python": '''# 백준 21965: 드높은 남산 위에 우뚝 선
# 수열이 산인지 판별 (증가하다가 감소)

N = int(input())
A = list(map(int, input().split()))

# 먼저 증가, 그 다음 감소
# 같은 값이 있으면 안 됨

i = 0
# 증가 구간
while i < N - 1 and A[i] < A[i + 1]:
    i += 1

# 정상에 도달 (i가 정상 위치)
# 최소한 첫 번째 원소까지는 증가해야 함 (i >= 0)

# 감소 구간
while i < N - 1 and A[i] > A[i + 1]:
    i += 1

# 끝까지 도달했으면 산
if i == N - 1:
    print("YES")
else:
    print("NO")
''',
        "java": '''import java.util.Scanner;

// 백준 21965: 드높은 남산 위에 우뚝 선
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] A = new int[N];
        for (int i = 0; i < N; i++) {
            A[i] = sc.nextInt();
        }

        int i = 0;
        // 증가 구간
        while (i < N - 1 && A[i] < A[i + 1]) {
            i++;
        }

        // 감소 구간
        while (i < N - 1 && A[i] > A[i + 1]) {
            i++;
        }

        if (i == N - 1) {
            System.out.println("YES");
        } else {
            System.out.println("NO");
        }
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 21965: 드높은 남산 위에 우뚝 선
int main() {
    int N;
    cin >> N;
    int A[100001];
    for (int i = 0; i < N; i++) {
        cin >> A[i];
    }

    int i = 0;
    // 증가 구간
    while (i < N - 1 && A[i] < A[i + 1]) {
        i++;
    }

    // 감소 구간
    while (i < N - 1 && A[i] > A[i + 1]) {
        i++;
    }

    if (i == N - 1) {
        cout << "YES" << endl;
    } else {
        cout << "NO" << endl;
    }

    return 0;
}
'''
    },

    # 28239: 배고파(Easy) - 2^x + 2^y = m
    "28239": {
        "python": '''# 백준 28239: 배고파(Easy)
# 2^x + 2^y = m인 x, y를 찾는다 (x <= y)

n = int(input())
for _ in range(n):
    m = int(input())

    # m의 이진 표현에서 1인 비트 위치 찾기
    # 2개의 1비트가 있으면 그 위치가 x, y
    # 1개의 1비트만 있으면 x = y - 1 (2^(k-1) + 2^(k-1) = 2^k)

    bits = []
    temp = m
    pos = 0
    while temp > 0:
        if temp & 1:
            bits.append(pos)
        temp >>= 1
        pos += 1

    if len(bits) == 1:
        # 2^k = 2^(k-1) + 2^(k-1)
        k = bits[0]
        print(k - 1, k - 1)
    else:
        # 두 개의 비트
        print(bits[0], bits[1])
''',
        "java": '''import java.util.Scanner;
import java.util.ArrayList;

// 백준 28239: 배고파(Easy)
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            long m = sc.nextLong();

            ArrayList<Integer> bits = new ArrayList<>();
            long temp = m;
            int pos = 0;
            while (temp > 0) {
                if ((temp & 1) == 1) {
                    bits.add(pos);
                }
                temp >>= 1;
                pos++;
            }

            if (bits.size() == 1) {
                int k = bits.get(0);
                sb.append((k - 1) + " " + (k - 1) + "\\n");
            } else {
                sb.append(bits.get(0) + " " + bits.get(1) + "\\n");
            }
        }
        System.out.print(sb);
    }
}
''',
        "cpp": '''#include <iostream>
#include <vector>
using namespace std;

// 백준 28239: 배고파(Easy)
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    while (n--) {
        long long m;
        cin >> m;

        vector<int> bits;
        long long temp = m;
        int pos = 0;
        while (temp > 0) {
            if (temp & 1) {
                bits.push_back(pos);
            }
            temp >>= 1;
            pos++;
        }

        if (bits.size() == 1) {
            int k = bits[0];
            cout << k - 1 << " " << k - 1 << "\\n";
        } else {
            cout << bits[0] << " " << bits[1] << "\\n";
        }
    }

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

        if original_id in SOLUTIONS:
            sol = SOLUTIONS[original_id]
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
