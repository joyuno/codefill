import json

# JSON 파일 읽기
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# medium 난이도이고 solutions가 비어있는 문제의 인덱스 찾기
empty_medium_indices = []
for idx, problem in enumerate(data):
    if problem.get('difficulty') == 'medium' and (not problem.get('solutions') or len(problem.get('solutions', [])) == 0):
        empty_medium_indices.append(idx)

print(f"총 빈 medium 문제 수: {len(empty_medium_indices)}")
print(f"처음 20개 문제 인덱스: {empty_medium_indices[:20]}")

# 처음 20개 문제에 대한 솔루션 생성
solutions_batch = {}

# 문제 1: baekjoon_28136 - 원, 탁!
solutions_batch[2993] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 원형 수열에서 연결을 끊어서 오름차순 수열을 만드는 문제
# 연속으로 증가하지 않는 곳의 개수가 필요한 "원, 탁!" 횟수

n = int(input())
a = list(map(int, input().split()))

# 연속해서 증가하지 않는 위치의 개수 카운트
# a[i] >= a[(i+1) % n] 인 곳이 끊어야 할 위치
count = 0
for i in range(n):
    if a[i] >= a[(i + 1) % n]:
        count += 1

# 모든 곳이 증가한다면 1번만 끊으면 됨 (원형이므로)
# 그 외에는 끊어야 할 위치 개수만큼
print(count)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] a = new int[n];
        for (int i = 0; i < n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
        }

        // 연속해서 증가하지 않는 위치의 개수 카운트
        int count = 0;
        for (int i = 0; i < n; i++) {
            if (a[i] >= a[(i + 1) % n]) {
                count++;
            }
        }

        System.out.println(count);
    }
}
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

    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    // 연속해서 증가하지 않는 위치의 개수 카운트
    int count = 0;
    for (int i = 0; i < n; i++) {
        if (a[i] >= a[(i + 1) % n]) {
            count++;
        }
    }

    cout << count << endl;

    return 0;
}
'''
    }
]

# 문제 2: baekjoon_28470 - 슥~빡! 빡~슥!
solutions_batch[2998] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 각 동작에서 공격을 먼저 하면 공격 증가량에 K를 곱함
# 회피를 먼저 하면 회피 감소량에 K를 곱함
# 최대 아드레날린을 구해야 함

n = int(input())
A = list(map(int, input().split()))  # 공격 시 증가량
B = list(map(int, input().split()))  # 회피 시 감소량
K = list(map(float, input().split()))  # 배수

total = 0
for i in range(n):
    # 공격 먼저: A[i] * K[i] 증가, B[i] 감소 -> 순수익 = A[i] * K[i] - B[i]
    attack_first = int(A[i] * K[i]) - B[i]
    # 회피 먼저: A[i] 증가, B[i] * K[i] 감소 -> 순수익 = A[i] - B[i] * K[i]
    dodge_first = A[i] - int(B[i] * K[i])

    # 더 큰 순수익을 선택
    total += max(attack_first, dodge_first)

print(total)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine());

        int[] A = new int[n];
        int[] B = new int[n];
        double[] K = new double[n];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            A[i] = Integer.parseInt(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            B[i] = Integer.parseInt(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            K[i] = Double.parseDouble(st.nextToken());
        }

        long total = 0;
        for (int i = 0; i < n; i++) {
            // 공격 먼저: A[i] * K[i] 증가, B[i] 감소
            long attackFirst = (long)(A[i] * K[i]) - B[i];
            // 회피 먼저: A[i] 증가, B[i] * K[i] 감소
            long dodgeFirst = A[i] - (long)(B[i] * K[i]);

            total += Math.max(attackFirst, dodgeFirst);
        }

        System.out.println(total);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int A[100000], B[100000];
    double K[100000];

    for (int i = 0; i < n; i++) cin >> A[i];
    for (int i = 0; i < n; i++) cin >> B[i];
    for (int i = 0; i < n; i++) cin >> K[i];

    long long total = 0;
    for (int i = 0; i < n; i++) {
        // 공격 먼저: A[i] * K[i] 증가, B[i] 감소
        long long attackFirst = (long long)(A[i] * K[i]) - B[i];
        // 회피 먼저: A[i] 증가, B[i] * K[i] 감소
        long long dodgeFirst = A[i] - (long long)(B[i] * K[i]);

        total += max(attackFirst, dodgeFirst);
    }

    cout << total << endl;

    return 0;
}
'''
    }
]

# 문제 3: baekjoon_2777 - 숫자 놀이
solutions_batch[3006] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

def solve(n):
    if n == 1:
        return 1

    # n을 2~9의 인수로 분해
    # 가장 작은 수를 만들려면 큰 인수부터 사용
    digits = []

    for d in range(9, 1, -1):
        while n % d == 0:
            digits.append(d)
            n //= d

    # n이 1이 아니면 2~9로 분해 불가능
    if n != 1:
        return -1

    # 자릿수 개수 반환
    return len(digits)

T = int(input())
for _ in range(T):
    n = int(input())
    print(solve(n))
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine());

        while (T-- > 0) {
            long n = Long.parseLong(br.readLine());
            sb.append(solve(n)).append("\\n");
        }

        System.out.print(sb);
    }

    static int solve(long n) {
        if (n == 1) return 1;

        int count = 0;

        // 큰 인수부터 분해
        for (int d = 9; d >= 2; d--) {
            while (n % d == 0) {
                count++;
                n /= d;
            }
        }

        // n이 1이 아니면 분해 불가능
        if (n != 1) return -1;

        return count;
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
using namespace std;

int solve(long long n) {
    if (n == 1) return 1;

    int count = 0;

    // 큰 인수부터 분해
    for (int d = 9; d >= 2; d--) {
        while (n % d == 0) {
            count++;
            n /= d;
        }
    }

    // n이 1이 아니면 분해 불가능
    if (n != 1) return -1;

    return count;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        long long n;
        cin >> n;
        cout << solve(n) << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 4: baekjoon_2545 - 팬케익 먹기
solutions_batch[3018] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# A x B x C 크기의 케익에서 D번 1cm 두께로 자름
# 최대한 많이 남기려면 가장 작은 면적의 방향으로 자름
# 각 방향에서 자를 수 있는 최대 횟수: A, B, C
# 매번 가장 작은 면적을 자르면 됨

T = int(input())

for _ in range(T):
    line = input().split()
    A, B, C, D = int(line[0]), int(line[1]), int(line[2]), int(line[3])

    # 현재 케익 크기
    dims = [A, B, C]

    for _ in range(D):
        # 가장 작은 면적(= 가장 작은 두 변의 곱)의 방향으로 자름
        # 즉, 가장 큰 변을 1 줄임
        dims.sort()
        if dims[2] > 0:
            dims[2] -= 1

    # 남은 부피
    volume = dims[0] * dims[1] * dims[2]
    print(volume)
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

        int T = Integer.parseInt(br.readLine().trim());

        for (int t = 0; t < T; t++) {
            br.readLine(); // 빈 줄 처리
            StringTokenizer st = new StringTokenizer(br.readLine());
            long A = Long.parseLong(st.nextToken());
            long B = Long.parseLong(st.nextToken());
            long C = Long.parseLong(st.nextToken());
            long D = Long.parseLong(st.nextToken());

            long[] dims = {A, B, C};

            for (long i = 0; i < D; i++) {
                Arrays.sort(dims);
                if (dims[2] > 0) {
                    dims[2]--;
                }
            }

            sb.append(dims[0] * dims[1] * dims[2]).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        long long A, B, C, D;
        cin >> A >> B >> C >> D;

        long long dims[3] = {A, B, C};

        for (long long i = 0; i < D; i++) {
            sort(dims, dims + 3);
            if (dims[2] > 0) {
                dims[2]--;
            }
        }

        cout << dims[0] * dims[1] * dims[2] << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 5: baekjoon_11819 - A^B mod C (거듭제곱 모듈러)
solutions_batch[3038] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# A^B mod C를 구하는 문제 (큰 수 거듭제곱)

def mod_pow(a, b, c):
    # 분할 정복으로 a^b mod c 계산
    result = 1
    a = a % c

    while b > 0:
        if b % 2 == 1:
            result = (result * a) % c
        b //= 2
        a = (a * a) % c

    return result

A, B, C = map(int, input().split())
print(mod_pow(A, B, C))
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;
import java.math.BigInteger;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        BigInteger A = new BigInteger(st.nextToken());
        BigInteger B = new BigInteger(st.nextToken());
        BigInteger C = new BigInteger(st.nextToken());

        // A^B mod C
        System.out.println(A.modPow(B, C));
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
using namespace std;

typedef unsigned long long ull;

// 큰 수 곱셈에서 오버플로우 방지를 위한 모듈러 곱셈
ull mulmod(ull a, ull b, ull m) {
    ull result = 0;
    a %= m;
    while (b > 0) {
        if (b & 1) {
            result = (result + a) % m;
        }
        a = (a * 2) % m;
        b >>= 1;
    }
    return result;
}

// 모듈러 거듭제곱
ull modpow(ull a, ull b, ull c) {
    ull result = 1;
    a %= c;

    while (b > 0) {
        if (b & 1) {
            result = mulmod(result, a, c);
        }
        b >>= 1;
        a = mulmod(a, a, c);
    }

    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    ull A, B, C;
    cin >> A >> B >> C;

    cout << modpow(A, B, C) << endl;

    return 0;
}
'''
    }
]

# 문제 6: baekjoon_1262 - 알파벳 다이아몬드
solutions_batch[3039] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# N 크기의 다이아몬드 패턴을 타일링하여 특정 영역 출력
# 다이아몬드 크기는 (2N-1) x (2N-1)

N, R1, R2, C1, C2 = map(int, input().split())

# 다이아몬드 한 변의 크기
size = 2 * N - 1

def get_char(row, col):
    # 무한 타일링된 다이아몬드에서 (row, col) 위치의 문자
    # 다이아몬드 내부 좌표로 변환
    r = row % size
    c = col % size

    # 다이아몬드 중심으로부터의 거리
    center = N - 1
    dist = abs(r - center) + abs(c - center)

    if dist >= N:
        return '.'
    else:
        # 거리에 따른 알파벳 (중심이 'a', 바깥으로 갈수록 b, c, ...)
        return chr(ord('a') + dist)

result = []
for row in range(R1 - 1, R2):
    line = []
    for col in range(C1 - 1, C2):
        line.append(get_char(row, col))
    result.append(''.join(line))

print('\\n'.join(result))
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int N, size;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        N = Integer.parseInt(st.nextToken());
        int R1 = Integer.parseInt(st.nextToken());
        int R2 = Integer.parseInt(st.nextToken());
        int C1 = Integer.parseInt(st.nextToken());
        int C2 = Integer.parseInt(st.nextToken());

        size = 2 * N - 1;

        StringBuilder sb = new StringBuilder();
        for (int row = R1 - 1; row < R2; row++) {
            for (int col = C1 - 1; col < C2; col++) {
                sb.append(getChar(row, col));
            }
            sb.append("\\n");
        }

        System.out.print(sb);
    }

    static char getChar(int row, int col) {
        // 다이아몬드 내부 좌표로 변환
        int r = ((row % size) + size) % size;
        int c = ((col % size) + size) % size;

        int center = N - 1;
        int dist = Math.abs(r - center) + Math.abs(c - center);

        if (dist >= N) {
            return '.';
        } else {
            return (char)('a' + dist);
        }
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <cstdlib>
using namespace std;

int N, sizeD;

char getChar(int row, int col) {
    // 다이아몬드 내부 좌표로 변환
    int r = ((row % sizeD) + sizeD) % sizeD;
    int c = ((col % sizeD) + sizeD) % sizeD;

    int center = N - 1;
    int dist = abs(r - center) + abs(c - center);

    if (dist >= N) {
        return '.';
    } else {
        return 'a' + dist;
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int R1, R2, C1, C2;
    cin >> N >> R1 >> R2 >> C1 >> C2;

    sizeD = 2 * N - 1;

    for (int row = R1 - 1; row < R2; row++) {
        for (int col = C1 - 1; col < C2; col++) {
            cout << getChar(row, col);
        }
        cout << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 7: baekjoon_20004 - 베스킨라빈스 31
solutions_batch[3045] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 1~n개의 수를 부를 수 있을 때, 31을 부르면 지는 게임
# 선공(민우)이 유리한 상황에서 시온이(후공)가 이길 수 있는 n의 값
# 후공이 이기려면: 31 % (n+1) == 1 이면 선공 승리
# 따라서 31 % (n+1) != 1 이면 후공(시온) 승리

A = int(input())

for n in range(1, A + 1):
    # n개까지 부를 수 있을 때
    # 선공이 이기려면 31 % (n+1) == 1
    # 후공(시온)이 이기려면 31 % (n+1) != 1
    # 즉, 31이 (n+1)로 나눴을 때 나머지가 1이 아니면 시온 승리
    # 단, 30 % (n+1) == 0 이면 후공 승리 (상대가 마지막에 31을 부르게 됨)
    if 30 % (n + 1) == 0:
        print(n)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int A = Integer.parseInt(br.readLine());

        for (int n = 1; n <= A; n++) {
            // n개까지 부를 수 있을 때, 30이 (n+1)로 나누어 떨어지면 후공 승리
            if (30 % (n + 1) == 0) {
                sb.append(n).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int A;
    cin >> A;

    for (int n = 1; n <= A; n++) {
        // n개까지 부를 수 있을 때, 30이 (n+1)로 나누어 떨어지면 후공 승리
        if (30 % (n + 1) == 0) {
            cout << n << "\\n";
        }
    }

    return 0;
}
'''
    }
]

# 문제 8: baekjoon_3063 - 게시판
solutions_batch[3047] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 첫 번째 포스터에서 두 번째 포스터와 겹치는 부분을 빼고 남은 넓이

T = int(input())

for _ in range(T):
    coords = list(map(int, input().split()))
    x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]  # 첫 번째 포스터
    x3, y3, x4, y4 = coords[4], coords[5], coords[6], coords[7]  # 두 번째 포스터 (덮는 포스터)

    # 첫 번째 포스터의 넓이
    area1 = (x2 - x1) * (y2 - y1)

    # 겹치는 영역 계산
    ox1 = max(x1, x3)
    oy1 = max(y1, y3)
    ox2 = min(x2, x4)
    oy2 = min(y2, y4)

    # 겹치는 영역의 넓이
    if ox1 < ox2 and oy1 < oy2:
        overlap = (ox2 - ox1) * (oy2 - oy1)
    else:
        overlap = 0

    print(area1 - overlap)
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

        int T = Integer.parseInt(br.readLine());

        while (T-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int x1 = Integer.parseInt(st.nextToken());
            int y1 = Integer.parseInt(st.nextToken());
            int x2 = Integer.parseInt(st.nextToken());
            int y2 = Integer.parseInt(st.nextToken());
            int x3 = Integer.parseInt(st.nextToken());
            int y3 = Integer.parseInt(st.nextToken());
            int x4 = Integer.parseInt(st.nextToken());
            int y4 = Integer.parseInt(st.nextToken());

            // 첫 번째 포스터의 넓이
            int area1 = (x2 - x1) * (y2 - y1);

            // 겹치는 영역 계산
            int ox1 = Math.max(x1, x3);
            int oy1 = Math.max(y1, y3);
            int ox2 = Math.min(x2, x4);
            int oy2 = Math.min(y2, y4);

            int overlap = 0;
            if (ox1 < ox2 && oy1 < oy2) {
                overlap = (ox2 - ox1) * (oy2 - oy1);
            }

            sb.append(area1 - overlap).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int x1, y1, x2, y2, x3, y3, x4, y4;
        cin >> x1 >> y1 >> x2 >> y2 >> x3 >> y3 >> x4 >> y4;

        // 첫 번째 포스터의 넓이
        int area1 = (x2 - x1) * (y2 - y1);

        // 겹치는 영역 계산
        int ox1 = max(x1, x3);
        int oy1 = max(y1, y3);
        int ox2 = min(x2, x4);
        int oy2 = min(y2, y4);

        int overlap = 0;
        if (ox1 < ox2 && oy1 < oy2) {
            overlap = (ox2 - ox1) * (oy2 - oy1);
        }

        cout << area1 - overlap << "\\n";
    }

    return 0;
}
'''
    }
]

# 문제 9: baekjoon_23797 - 개구리
solutions_batch[3052] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 개구리 울음: K와 P가 번갈아 나옴
# 최소 몇 마리의 개구리가 필요한지

S = input().strip()

# K를 울 수 있는 개구리 수 (이전에 P를 울은 개구리)
# P를 울 수 있는 개구리 수 (이전에 K를 울은 개구리)
can_K = 0  # P를 울고 나서 K를 기다리는 개구리
can_P = 0  # K를 울고 나서 P를 기다리는 개구리
total_frogs = 0

for c in S:
    if c == 'K':
        if can_K > 0:
            # P를 울은 개구리가 K를 울음
            can_K -= 1
            can_P += 1
        else:
            # 새 개구리 필요
            total_frogs += 1
            can_P += 1
    else:  # c == 'P'
        if can_P > 0:
            # K를 울은 개구리가 P를 울음
            can_P -= 1
            can_K += 1
        else:
            # 새 개구리 필요
            total_frogs += 1
            can_K += 1

print(total_frogs)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String S = br.readLine();

        int canK = 0;  // P를 울고 나서 K를 기다리는 개구리
        int canP = 0;  // K를 울고 나서 P를 기다리는 개구리
        int totalFrogs = 0;

        for (char c : S.toCharArray()) {
            if (c == 'K') {
                if (canK > 0) {
                    canK--;
                    canP++;
                } else {
                    totalFrogs++;
                    canP++;
                }
            } else {  // c == 'P'
                if (canP > 0) {
                    canP--;
                    canK++;
                } else {
                    totalFrogs++;
                    canK++;
                }
            }
        }

        System.out.println(totalFrogs);
    }
}
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

    string S;
    cin >> S;

    int canK = 0;  // P를 울고 나서 K를 기다리는 개구리
    int canP = 0;  // K를 울고 나서 P를 기다리는 개구리
    int totalFrogs = 0;

    for (char c : S) {
        if (c == 'K') {
            if (canK > 0) {
                canK--;
                canP++;
            } else {
                totalFrogs++;
                canP++;
            }
        } else {  // c == 'P'
            if (canP > 0) {
                canP--;
                canK++;
            } else {
                totalFrogs++;
                canK++;
            }
        }
    }

    cout << totalFrogs << endl;

    return 0;
}
'''
    }
]

# 문제 10: baekjoon_31937 - 로그프레소 마에스트로
solutions_batch[3118] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 바이러스 전파 추적: 처음 감염된 컴퓨터 찾기
# 감염된 컴퓨터에서 다른 컴퓨터로 파일 전송하면 감염

N, M, K = map(int, input().split())
infected = set(map(int, input().split()))

logs = []
for _ in range(M):
    t, a, b = input().split()
    logs.append((int(t), int(a), int(b)))

# 시간순 정렬
logs.sort()

# 각 감염된 컴퓨터가 최초 감염원일 때 시뮬레이션
for start in infected:
    # start가 처음부터 감염되어 있다고 가정
    current_infected = {start}

    for t, a, b in logs:
        if a in current_infected:
            current_infected.add(b)

    # 최종 감염 상태가 주어진 감염 목록과 일치하는지 확인
    if current_infected == infected:
        print(start)
        break
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        Set<Integer> infected = new HashSet<>();
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < K; i++) {
            infected.add(Integer.parseInt(st.nextToken()));
        }

        int[][] logs = new int[M][3];
        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            logs[i][0] = Integer.parseInt(st.nextToken());
            logs[i][1] = Integer.parseInt(st.nextToken());
            logs[i][2] = Integer.parseInt(st.nextToken());
        }

        // 시간순 정렬
        Arrays.sort(logs, (a, b) -> a[0] - b[0]);

        // 각 감염된 컴퓨터가 최초 감염원일 때 시뮬레이션
        for (int start : infected) {
            Set<Integer> currentInfected = new HashSet<>();
            currentInfected.add(start);

            for (int[] log : logs) {
                int a = log[1], b = log[2];
                if (currentInfected.contains(a)) {
                    currentInfected.add(b);
                }
            }

            if (currentInfected.equals(infected)) {
                System.out.println(start);
                break;
            }
        }
    }
}
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

    int N, M, K;
    cin >> N >> M >> K;

    set<int> infected;
    for (int i = 0; i < K; i++) {
        int x;
        cin >> x;
        infected.insert(x);
    }

    vector<tuple<int, int, int>> logs(M);
    for (int i = 0; i < M; i++) {
        int t, a, b;
        cin >> t >> a >> b;
        logs[i] = make_tuple(t, a, b);
    }

    // 시간순 정렬
    sort(logs.begin(), logs.end());

    // 각 감염된 컴퓨터가 최초 감염원일 때 시뮬레이션
    for (int start : infected) {
        set<int> currentInfected;
        currentInfected.insert(start);

        for (auto& log : logs) {
            int a = get<1>(log), b = get<2>(log);
            if (currentInfected.count(a)) {
                currentInfected.insert(b);
            }
        }

        if (currentInfected == infected) {
            cout << start << endl;
            break;
        }
    }

    return 0;
}
'''
    }
]

# 문제 11: baekjoon_29700 - 우당탕탕 영화예매
solutions_batch[3136] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# N행 M열에서 K명이 가로로 연속 앉을 수 있는 경우의 수

N, M, K = map(int, input().split())

total = 0
for _ in range(N):
    row = input().strip()
    # 연속된 0의 개수를 세고, K개 이상인 구간에서 경우의 수 계산
    count = 0
    for c in row:
        if c == '0':
            count += 1
        else:
            if count >= K:
                # 길이 count인 구간에서 K개 연속 선택하는 경우의 수
                total += count - K + 1
            count = 0
    # 마지막 구간 처리
    if count >= K:
        total += count - K + 1

print(total)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        long total = 0;

        for (int i = 0; i < N; i++) {
            String row = br.readLine();
            int count = 0;

            for (int j = 0; j < M; j++) {
                if (row.charAt(j) == '0') {
                    count++;
                } else {
                    if (count >= K) {
                        total += count - K + 1;
                    }
                    count = 0;
                }
            }
            if (count >= K) {
                total += count - K + 1;
            }
        }

        System.out.println(total);
    }
}
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

    int N, M, K;
    cin >> N >> M >> K;

    long long total = 0;

    for (int i = 0; i < N; i++) {
        string row;
        cin >> row;
        int count = 0;

        for (int j = 0; j < M; j++) {
            if (row[j] == '0') {
                count++;
            } else {
                if (count >= K) {
                    total += count - K + 1;
                }
                count = 0;
            }
        }
        if (count >= K) {
            total += count - K + 1;
        }
    }

    cout << total << endl;

    return 0;
}
'''
    }
]

# 문제 12: baekjoon_17393 - 다이나믹 롤러
solutions_batch[3141] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline
from bisect import bisect_right

# i번째 칸에서 오른쪽으로 A[i] 이하의 B값을 가진 칸을 칠할 수 있음
# B는 오름차순이므로 이분 탐색 사용

N = int(input())
A = list(map(int, input().split()))
B = list(map(int, input().split()))

result = []
for i in range(N):
    # i+1부터 끝까지에서 B[j] <= A[i]인 가장 오른쪽 위치 찾기
    # B[i+1:]에서 A[i] 이하인 개수
    if i == N - 1:
        result.append(0)
    else:
        # B 배열에서 i+1부터 끝까지 중 A[i] 이하인 개수
        # bisect_right(B, A[i], i+1, N) - (i+1)
        right_idx = bisect_right(B, A[i], i + 1, N)
        count = right_idx - (i + 1)
        result.append(count)

print(' '.join(map(str, result)))
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine());

        long[] A = new long[N];
        long[] B = new long[N];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            A[i] = Long.parseLong(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            B[i] = Long.parseLong(st.nextToken());
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < N; i++) {
            if (i == N - 1) {
                sb.append(0);
            } else {
                // i+1부터 끝까지에서 B[j] <= A[i]인 개수 (이분 탐색)
                int left = i + 1, right = N;
                while (left < right) {
                    int mid = (left + right) / 2;
                    if (B[mid] <= A[i]) {
                        left = mid + 1;
                    } else {
                        right = mid;
                    }
                }
                sb.append(left - (i + 1));
            }
            if (i < N - 1) sb.append(" ");
        }

        System.out.println(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    long long A[500001], B[500001];

    for (int i = 0; i < N; i++) cin >> A[i];
    for (int i = 0; i < N; i++) cin >> B[i];

    for (int i = 0; i < N; i++) {
        if (i == N - 1) {
            cout << 0;
        } else {
            // i+1부터 끝까지에서 B[j] <= A[i]인 개수
            int idx = upper_bound(B + i + 1, B + N, A[i]) - B;
            cout << idx - (i + 1);
        }
        if (i < N - 1) cout << " ";
    }
    cout << endl;

    return 0;
}
'''
    }
]

# 문제 13: baekjoon_25943 - 양팔저울
solutions_batch[3155] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 규칙에 따라 자갈을 양팔저울에 올린 후
# 균형을 맞추기 위한 최소 무게추 개수

n = int(input())
weights = list(map(int, input().split()))

# 왼쪽, 오른쪽에 올린 무게 합
left = weights[0]
right = weights[1]

for i in range(2, n):
    if left == right:
        # 평형이면 왼쪽에
        left += weights[i]
    elif left < right:
        # 가벼운 쪽(왼쪽)에
        left += weights[i]
    else:
        # 가벼운 쪽(오른쪽)에
        right += weights[i]

# 차이를 무게추로 메우기
diff = abs(left - right)

# 가능한 무게추: 100, 50, 20, 10, 5, 2, 1
weight_types = [100, 50, 20, 10, 5, 2, 1]
count = 0

for w in weight_types:
    count += diff // w
    diff %= w

print(count)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] weights = new int[n];
        for (int i = 0; i < n; i++) {
            weights[i] = Integer.parseInt(st.nextToken());
        }

        long left = weights[0];
        long right = weights[1];

        for (int i = 2; i < n; i++) {
            if (left == right) {
                left += weights[i];
            } else if (left < right) {
                left += weights[i];
            } else {
                right += weights[i];
            }
        }

        long diff = Math.abs(left - right);

        int[] weightTypes = {100, 50, 20, 10, 5, 2, 1};
        long count = 0;

        for (int w : weightTypes) {
            count += diff / w;
            diff %= w;
        }

        System.out.println(count);
    }
}
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

    int weights[10001];
    for (int i = 0; i < n; i++) {
        cin >> weights[i];
    }

    long long left = weights[0];
    long long right = weights[1];

    for (int i = 2; i < n; i++) {
        if (left == right) {
            left += weights[i];
        } else if (left < right) {
            left += weights[i];
        } else {
            right += weights[i];
        }
    }

    long long diff = abs(left - right);

    int weightTypes[] = {100, 50, 20, 10, 5, 2, 1};
    long long count = 0;

    for (int w : weightTypes) {
        count += diff / w;
        diff %= w;
    }

    cout << count << endl;

    return 0;
}
'''
    }
]

# 문제 14: baekjoon_23056 - 참가자 명단
solutions_batch[3156] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 학급별 M명 선착순, 청팀(홀수반) 먼저, 백팀(짝수반) 나중에
# 각 팀 내에서 학급 오름차순, 학급 내에서 이름 길이순/사전순

N, M = map(int, input().split())

# 학급별 참가자 저장
classes = {}
for i in range(1, N + 1):
    classes[i] = []

while True:
    line = input().split()
    class_num = int(line[0])

    if class_num == 0:
        break

    name = line[1]

    if len(classes[class_num]) < M:
        classes[class_num].append(name)

# 정렬: 이름 길이순, 같으면 사전순
for i in range(1, N + 1):
    classes[i].sort(key=lambda x: (len(x), x))

# 청팀(홀수 학급) 먼저 출력
for i in range(1, N + 1, 2):
    for name in classes[i]:
        print(i, name)

# 백팀(짝수 학급) 출력
for i in range(2, N + 1, 2):
    for name in classes[i]:
        print(i, name)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int M = Integer.parseInt(st.nextToken());

        List<List<String>> classes = new ArrayList<>();
        for (int i = 0; i <= N; i++) {
            classes.add(new ArrayList<>());
        }

        while (true) {
            st = new StringTokenizer(br.readLine());
            int classNum = Integer.parseInt(st.nextToken());

            if (classNum == 0) break;

            String name = st.nextToken();

            if (classes.get(classNum).size() < M) {
                classes.get(classNum).add(name);
            }
        }

        // 정렬: 이름 길이순, 같으면 사전순
        for (int i = 1; i <= N; i++) {
            Collections.sort(classes.get(i), (a, b) -> {
                if (a.length() != b.length()) {
                    return a.length() - b.length();
                }
                return a.compareTo(b);
            });
        }

        StringBuilder sb = new StringBuilder();

        // 청팀(홀수 학급) 먼저
        for (int i = 1; i <= N; i += 2) {
            for (String name : classes.get(i)) {
                sb.append(i).append(" ").append(name).append("\\n");
            }
        }

        // 백팀(짝수 학급)
        for (int i = 2; i <= N; i += 2) {
            for (String name : classes.get(i)) {
                sb.append(i).append(" ").append(name).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

bool cmp(const string& a, const string& b) {
    if (a.length() != b.length()) {
        return a.length() < b.length();
    }
    return a < b;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    vector<vector<string>> classes(N + 1);

    int classNum;
    string name;

    while (cin >> classNum >> name) {
        if (classNum == 0) break;

        if (classes[classNum].size() < M) {
            classes[classNum].push_back(name);
        }
    }

    // 정렬
    for (int i = 1; i <= N; i++) {
        sort(classes[i].begin(), classes[i].end(), cmp);
    }

    // 청팀(홀수 학급) 먼저
    for (int i = 1; i <= N; i += 2) {
        for (const string& n : classes[i]) {
            cout << i << " " << n << "\\n";
        }
    }

    // 백팀(짝수 학급)
    for (int i = 2; i <= N; i += 2) {
        for (const string& n : classes[i]) {
            cout << i << " " << n << "\\n";
        }
    }

    return 0;
}
'''
    }
]

# 문제 15: baekjoon_30701 - 돌아온 똥게임
solutions_batch[3158] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 몬스터: 전투력 > 몬스터면 쓰러뜨리고 전투력에 더함
# 장비: 이전 장비 다 얻어야 하고, 전투력에 곱함

N, D = map(int, input().split())

monsters = []
equipments = []

for _ in range(N):
    a, x = map(int, input().split())
    if a == 1:
        monsters.append(x)
    else:
        equipments.append(x)

# 장비는 오름차순으로 정렬 (작은 것부터 얻어야 함)
equipments.sort()
# 몬스터는 오름차순으로 정렬 (쉬운 것부터)
monsters.sort()

power = D
cleared = 0
equip_idx = 0
mon_idx = 0

# 그리디: 가능한 한 장비를 먼저 얻고, 안되면 몬스터 처치
while True:
    progress = False

    # 얻을 수 있는 장비 모두 얻기
    while equip_idx < len(equipments):
        power *= equipments[equip_idx]
        equip_idx += 1
        cleared += 1
        progress = True

    # 처치할 수 있는 몬스터 처치
    while mon_idx < len(monsters) and power > monsters[mon_idx]:
        power += monsters[mon_idx]
        mon_idx += 1
        cleared += 1
        progress = True

    if not progress:
        break

print(cleared)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        long D = Long.parseLong(st.nextToken());

        List<Long> monsters = new ArrayList<>();
        List<Long> equipments = new ArrayList<>();

        for (int i = 0; i < N; i++) {
            st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            long x = Long.parseLong(st.nextToken());

            if (a == 1) {
                monsters.add(x);
            } else {
                equipments.add(x);
            }
        }

        Collections.sort(equipments);
        Collections.sort(monsters);

        // BigInteger 사용 (곱셈으로 인해 매우 커질 수 있음)
        java.math.BigInteger power = java.math.BigInteger.valueOf(D);
        int cleared = 0;
        int equipIdx = 0;
        int monIdx = 0;

        while (true) {
            boolean progress = false;

            // 장비 얻기
            while (equipIdx < equipments.size()) {
                power = power.multiply(java.math.BigInteger.valueOf(equipments.get(equipIdx)));
                equipIdx++;
                cleared++;
                progress = true;
            }

            // 몬스터 처치
            while (monIdx < monsters.size() &&
                   power.compareTo(java.math.BigInteger.valueOf(monsters.get(monIdx))) > 0) {
                power = power.add(java.math.BigInteger.valueOf(monsters.get(monIdx)));
                monIdx++;
                cleared++;
                progress = true;
            }

            if (!progress) break;
        }

        System.out.println(cleared);
    }
}
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

    int N;
    long long D;
    cin >> N >> D;

    vector<long long> monsters;
    vector<long long> equipments;

    for (int i = 0; i < N; i++) {
        int a;
        long long x;
        cin >> a >> x;

        if (a == 1) {
            monsters.push_back(x);
        } else {
            equipments.push_back(x);
        }
    }

    sort(equipments.begin(), equipments.end());
    sort(monsters.begin(), monsters.end());

    // 전투력이 매우 커질 수 있으므로 상한선 설정
    const long long INF = 2e18;
    long long power = D;
    int cleared = 0;
    int equipIdx = 0;
    int monIdx = 0;

    while (true) {
        bool progress = false;

        // 장비 얻기
        while (equipIdx < equipments.size()) {
            if (power > INF / equipments[equipIdx]) {
                power = INF;
            } else {
                power *= equipments[equipIdx];
            }
            equipIdx++;
            cleared++;
            progress = true;
        }

        // 몬스터 처치
        while (monIdx < monsters.size() && power > monsters[monIdx]) {
            power += monsters[monIdx];
            if (power > INF) power = INF;
            monIdx++;
            cleared++;
            progress = true;
        }

        if (!progress) break;
    }

    cout << cleared << endl;

    return 0;
}
'''
    }
]

# 문제 16: baekjoon_1291 - 이면수와 임현수
solutions_batch[3163] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 1: 제1계급 (1만)
# 2, 3: 시작의 계급
# 4, 6, 7, 8, 9, 10, ...: 완전 (4 또는 2,3의 합으로 표현 가능 = 4 이상)
# 5: 인류의 계급 (나머지)

n = int(input())

if n == 1:
    print(1)
elif n == 2 or n == 3:
    print(2)
elif n >= 4:
    print(3)
else:  # n == 5는 없지만 혹시 모를 경우
    print(4)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine());

        if (n == 1) {
            System.out.println(1);
        } else if (n == 2 || n == 3) {
            System.out.println(2);
        } else {
            System.out.println(3);
        }
    }
}
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

    if (n == 1) {
        cout << 1 << endl;
    } else if (n == 2 || n == 3) {
        cout << 2 << endl;
    } else {
        cout << 3 << endl;
    }

    return 0;
}
'''
    }
]

# 문제 17: baekjoon_10263 - Opening Ceremony
solutions_batch[3172] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 건물을 제거하는 방법:
# 1. 한 건물 전체 제거
# 2. 모든 건물의 x번째 층 제거
# 최소 횟수로 모두 제거

n = int(input())
heights = list(map(int, input().split()))

# DP: 높이 h까지의 건물들을 제거하는 최소 비용
# 정렬하여 처리
heights.sort(reverse=True)

# dp[i] = i번째 건물까지 처리하는 최소 비용
# 전략: 높은 건물부터 처리
# i번째 건물의 높이가 h일 때,
# 이전 건물의 높이가 prev_h였다면
# h - prev_h 개의 층을 폭파하거나, 건물 하나씩 폭파

# 높이순 정렬 후, 각 높이에서 몇 개의 건물이 있는지 확인
# 높이 h에서: 건물 개수 >= (h - prev_h) 면 층 폭파가 이득

result = 0
prev_h = 0

for i in range(n):
    current_h = heights[i]
    buildings_remaining = n - i  # 현재 이상의 높이를 가진 건물 수

    # 현재 높이까지 (prev_h ~ current_h 사이) 처리
    diff = current_h - prev_h

    # 층 폭파 vs 건물 폭파 중 유리한 것 선택
    # diff 개의 층을 폭파 = diff 비용
    # 남은 buildings_remaining 개의 건물을 개별 폭파 = buildings_remaining 비용

    result += min(diff, buildings_remaining)
    prev_h = current_h

print(result)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine());
        int[] heights = new int[n];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            heights[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(heights);

        // 역순으로 처리 (높은 건물부터)
        int result = 0;
        int prevH = 0;

        for (int i = n - 1; i >= 0; i--) {
            int currentH = heights[i];
            int buildingsRemaining = n - i;

            int diff = currentH - prevH;

            result += Math.min(diff, buildingsRemaining);
            prevH = currentH;
        }

        System.out.println(result);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    int heights[100001];
    for (int i = 0; i < n; i++) {
        cin >> heights[i];
    }

    sort(heights, heights + n);

    // 역순으로 처리 (높은 건물부터)
    int result = 0;
    int prevH = 0;

    for (int i = n - 1; i >= 0; i--) {
        int currentH = heights[i];
        int buildingsRemaining = n - i;

        int diff = currentH - prevH;

        result += min(diff, buildingsRemaining);
        prevH = currentH;
    }

    cout << result << endl;

    return 0;
}
'''
    }
]

# 문제 18: baekjoon_23057 - 도전 숫자왕
solutions_batch[3184] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# N개의 카드로 만들 수 없는 수의 개수 (1 ~ M 사이)
# 부분집합 합 문제

N = int(input())
cards = list(map(int, input().split()))

M = sum(cards)

# DP로 만들 수 있는 합 체크
possible = [False] * (M + 1)
possible[0] = True

for card in cards:
    # 역순으로 순회해야 같은 카드를 여러 번 사용하지 않음
    for i in range(M, card - 1, -1):
        if possible[i - card]:
            possible[i] = True

# 1부터 M까지 중 만들 수 없는 수 카운트
count = 0
for i in range(1, M + 1):
    if not possible[i]:
        count += 1

print(count)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] cards = new int[N];
        int M = 0;
        for (int i = 0; i < N; i++) {
            cards[i] = Integer.parseInt(st.nextToken());
            M += cards[i];
        }

        // DP로 만들 수 있는 합 체크
        boolean[] possible = new boolean[M + 1];
        possible[0] = true;

        for (int card : cards) {
            for (int i = M; i >= card; i--) {
                if (possible[i - card]) {
                    possible[i] = true;
                }
            }
        }

        // 만들 수 없는 수 카운트
        int count = 0;
        for (int i = 1; i <= M; i++) {
            if (!possible[i]) {
                count++;
            }
        }

        System.out.println(count);
    }
}
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

    int N;
    cin >> N;

    vector<int> cards(N);
    int M = 0;
    for (int i = 0; i < N; i++) {
        cin >> cards[i];
        M += cards[i];
    }

    // DP로 만들 수 있는 합 체크
    vector<bool> possible(M + 1, false);
    possible[0] = true;

    for (int card : cards) {
        for (int i = M; i >= card; i--) {
            if (possible[i - card]) {
                possible[i] = true;
            }
        }
    }

    // 만들 수 없는 수 카운트
    int count = 0;
    for (int i = 1; i <= M; i++) {
        if (!possible[i]) {
            count++;
        }
    }

    cout << count << endl;

    return 0;
}
'''
    }
]

# 문제 19: baekjoon_15728 - 에리 - 카드
solutions_batch[3192] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# N장의 공유 카드, N장의 팀 카드
# 상대가 K장 견제 후, 공유 1장 * 팀 1장이 점수
# 상대는 우리 점수를 최소화하도록 견제

N, K = map(int, input().split())
shared = list(map(int, input().split()))
team = list(map(int, input().split()))

# 팀 카드를 정렬하여 상대가 최적으로 견제할 때 남는 카드 확인
# 상대는 우리의 최대 점수를 최소화하려 함

# 모든 가능한 곱 계산
products = []
for s in shared:
    for t in team:
        products.append((s * t, t))

# 상대가 K장의 팀 카드를 제거할 때 최대 점수
# 상대는 우리가 사용할 팀 카드 K개를 제거함

# 전략: 팀 카드 중 K개를 제거했을 때 남은 카드로 얻을 수 있는 최대 점수
# 팀 카드를 정렬하고, 양 끝에서 K개를 제거하는 경우들을 시뮬레이션

team.sort()

max_score = float('-inf')

# K개를 제거하는 모든 방법: 양 끝에서 i개, K-i개 제거
for i in range(K + 1):
    # 작은 쪽에서 i개, 큰 쪽에서 K-i개 제거
    remaining = team[i:N - (K - i)] if K - i > 0 else team[i:]

    if not remaining:
        continue

    # 남은 팀 카드로 최대 점수 계산
    min_t = remaining[0]
    max_t = remaining[-1]

    min_s = min(shared)
    max_s = max(shared)

    # 가능한 조합 중 최대
    score = max(min_s * min_t, min_s * max_t, max_s * min_t, max_s * max_t)
    max_score = max(max_score, score)

print(max_score)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        int[] shared = new int[N];
        int[] team = new int[N];

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            shared[i] = Integer.parseInt(st.nextToken());
        }

        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            team[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(team);

        int minS = shared[0], maxS = shared[0];
        for (int s : shared) {
            minS = Math.min(minS, s);
            maxS = Math.max(maxS, s);
        }

        long maxScore = Long.MIN_VALUE;

        for (int i = 0; i <= K; i++) {
            int left = i;
            int right = K - i;

            if (left + right > N - 1) continue;

            int minT = team[left];
            int maxT = team[N - 1 - right];

            if (minT > maxT) continue;

            long score = Math.max(
                Math.max((long)minS * minT, (long)minS * maxT),
                Math.max((long)maxS * minT, (long)maxS * maxT)
            );
            maxScore = Math.max(maxScore, score);
        }

        System.out.println(maxScore);
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <algorithm>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, K;
    cin >> N >> K;

    int shared[101], team[101];

    for (int i = 0; i < N; i++) cin >> shared[i];
    for (int i = 0; i < N; i++) cin >> team[i];

    sort(team, team + N);

    int minS = shared[0], maxS = shared[0];
    for (int i = 0; i < N; i++) {
        minS = min(minS, shared[i]);
        maxS = max(maxS, shared[i]);
    }

    long long maxScore = LLONG_MIN;

    for (int i = 0; i <= K; i++) {
        int left = i;
        int right = K - i;

        if (left + right > N - 1) continue;

        int minT = team[left];
        int maxT = team[N - 1 - right];

        if (minT > maxT) continue;

        long long score = max({
            (long long)minS * minT,
            (long long)minS * maxT,
            (long long)maxS * minT,
            (long long)maxS * maxT
        });
        maxScore = max(maxScore, score);
    }

    cout << maxScore << endl;

    return 0;
}
'''
    }
]

# 문제 20: baekjoon_15465 - Milk Measurement
solutions_batch[3267] = [
    {
        "language": "python",
        "code": '''import sys
input = sys.stdin.readline

# 세 마리 소: Bessie, Elsie, Mildred - 각각 초기 7갤런
# 측정 로그에 따라 우유 생산량 변화
# 가장 많이 생산하는 소의 사진을 벽에 걸기
# 사진을 바꿔야 하는 날 수

N = int(input())

logs = []
for _ in range(N):
    parts = input().split()
    day = int(parts[0])
    cow = parts[1]
    change = int(parts[2])
    logs.append((day, cow, change))

# 날짜순 정렬
logs.sort()

# 초기 상태
milk = {'Bessie': 7, 'Elsie': 7, 'Mildred': 7}

def get_top_cows():
    max_milk = max(milk.values())
    return set(cow for cow, m in milk.items() if m == max_milk)

current_display = get_top_cows()
changes = 0

for day, cow, change in logs:
    milk[cow] += change
    new_display = get_top_cows()

    if new_display != current_display:
        changes += 1
        current_display = new_display

print(changes)
'''
    },
    {
        "language": "java",
        "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine());

        int[][] logs = new int[N][3];  // day, cow(0=Bessie, 1=Elsie, 2=Mildred), change

        Map<String, Integer> cowIndex = new HashMap<>();
        cowIndex.put("Bessie", 0);
        cowIndex.put("Elsie", 1);
        cowIndex.put("Mildred", 2);

        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            logs[i][0] = Integer.parseInt(st.nextToken());
            logs[i][1] = cowIndex.get(st.nextToken());
            String change = st.nextToken();
            logs[i][2] = Integer.parseInt(change);
        }

        // 날짜순 정렬
        Arrays.sort(logs, (a, b) -> a[0] - b[0]);

        int[] milk = {7, 7, 7};  // Bessie, Elsie, Mildred

        int changes = 0;
        Set<Integer> currentDisplay = getTopCows(milk);

        for (int[] log : logs) {
            milk[log[1]] += log[2];
            Set<Integer> newDisplay = getTopCows(milk);

            if (!newDisplay.equals(currentDisplay)) {
                changes++;
                currentDisplay = newDisplay;
            }
        }

        System.out.println(changes);
    }

    static Set<Integer> getTopCows(int[] milk) {
        int maxMilk = Math.max(Math.max(milk[0], milk[1]), milk[2]);
        Set<Integer> top = new HashSet<>();
        for (int i = 0; i < 3; i++) {
            if (milk[i] == maxMilk) {
                top.add(i);
            }
        }
        return top;
    }
}
'''
    },
    {
        "language": "cpp",
        "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <set>
#include <map>
#include <string>
using namespace std;

set<int> getTopCows(int milk[]) {
    int maxMilk = max({milk[0], milk[1], milk[2]});
    set<int> top;
    for (int i = 0; i < 3; i++) {
        if (milk[i] == maxMilk) {
            top.insert(i);
        }
    }
    return top;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    map<string, int> cowIndex;
    cowIndex["Bessie"] = 0;
    cowIndex["Elsie"] = 1;
    cowIndex["Mildred"] = 2;

    vector<tuple<int, int, int>> logs;

    for (int i = 0; i < N; i++) {
        int day;
        string cow;
        int change;
        cin >> day >> cow >> change;
        logs.push_back(make_tuple(day, cowIndex[cow], change));
    }

    // 날짜순 정렬
    sort(logs.begin(), logs.end());

    int milk[3] = {7, 7, 7};

    int changes = 0;
    set<int> currentDisplay = getTopCows(milk);

    for (auto& log : logs) {
        milk[get<1>(log)] += get<2>(log);
        set<int> newDisplay = getTopCows(milk);

        if (newDisplay != currentDisplay) {
            changes++;
            currentDisplay = newDisplay;
        }
    }

    cout << changes << endl;

    return 0;
}
'''
    }
]

# 솔루션 적용
for idx, solutions in solutions_batch.items():
    data[idx]['solutions'] = solutions
    print(f"적용 완료: index {idx}, 문제 ID: {data[idx]['id']}")

# 파일에 저장
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n완료! 총 {len(solutions_batch)}개 문제에 솔루션 적용")
