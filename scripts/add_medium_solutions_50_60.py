import json

# 읽기
with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'r') as f:
    data = json.load(f)

# 새로운 문제 솔루션 추가
new_solutions = {
    "1812": {
        "solutions": [
            {
                "language": "python",
                "code": """# 사탕 - 인접한 두 학생의 사탕 합으로 각 학생의 사탕 수 구하기
# N은 홀수, 원형으로 앉아있음
import sys
input = sys.stdin.readline

N = int(input())
S = [int(input()) for _ in range(N)]  # S[i] = A[i] + A[i+1]

# S[0] - S[1] + S[2] - ... + S[N-1] = 2*A[0] (N이 홀수)
total = 0
sign = 1
for i in range(N):
    total += sign * S[i]
    sign *= -1

A = [0] * N
A[0] = total // 2

# A[i] = S[i-1] - A[i-1]
for i in range(1, N):
    A[i] = S[i-1] - A[i-1]

for a in A:
    print(a)
"""
            },
            {
                "language": "java",
                "code": """// 사탕 - 인접한 두 학생의 사탕 합으로 각 학생의 사탕 수 구하기
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] S = new int[N];  // S[i] = A[i] + A[i+1]

        for (int i = 0; i < N; i++) {
            S[i] = sc.nextInt();
        }

        // S[0] - S[1] + S[2] - ... + S[N-1] = 2*A[0] (N이 홀수)
        int total = 0;
        int sign = 1;
        for (int i = 0; i < N; i++) {
            total += sign * S[i];
            sign *= -1;
        }

        int[] A = new int[N];
        A[0] = total / 2;

        // A[i] = S[i-1] - A[i-1]
        for (int i = 1; i < N; i++) {
            A[i] = S[i-1] - A[i-1];
        }

        StringBuilder sb = new StringBuilder();
        for (int a : A) {
            sb.append(a).append("\\n");
        }
        System.out.print(sb);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """// 사탕 - 인접한 두 학생의 사탕 합으로 각 학생의 사탕 수 구하기
#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    vector<int> S(N);  // S[i] = A[i] + A[i+1]
    for (int i = 0; i < N; i++) {
        cin >> S[i];
    }

    // S[0] - S[1] + S[2] - ... + S[N-1] = 2*A[0] (N이 홀수)
    int total = 0;
    int sign = 1;
    for (int i = 0; i < N; i++) {
        total += sign * S[i];
        sign *= -1;
    }

    vector<int> A(N);
    A[0] = total / 2;

    // A[i] = S[i-1] - A[i-1]
    for (int i = 1; i < N; i++) {
        A[i] = S[i-1] - A[i-1];
    }

    for (int a : A) {
        cout << a << "\\n";
    }

    return 0;
}
"""
            }
        ]
    },
    "10252": {
        "solutions": [
            {
                "language": "python",
                "code": """# 그리드 그래프 - m x n 그리드에서 해밀턴 경로 찾기
import sys
input = sys.stdin.readline

T = int(input())
for _ in range(T):
    m, n = map(int, input().split())

    # 그리드 그래프에서 모든 정점을 방문하는 경로 출력
    # 뱀 모양으로 순회
    print(1)  # 해밀턴 경로 존재

    path = []
    for row in range(m):
        if row % 2 == 0:
            # 왼쪽에서 오른쪽으로
            for col in range(n):
                path.append(f"({row},{col})")
        else:
            # 오른쪽에서 왼쪽으로
            for col in range(n - 1, -1, -1):
                path.append(f"({row},{col})")

    print("\\n".join(path))
"""
            },
            {
                "language": "java",
                "code": """// 그리드 그래프 - m x n 그리드에서 해밀턴 경로 찾기
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        StringBuilder sb = new StringBuilder();
        while (T-- > 0) {
            int m = sc.nextInt();
            int n = sc.nextInt();

            // 그리드 그래프에서 모든 정점을 방문하는 경로 출력
            // 뱀 모양으로 순회
            sb.append(1).append("\\n");  // 해밀턴 경로 존재

            for (int row = 0; row < m; row++) {
                if (row % 2 == 0) {
                    // 왼쪽에서 오른쪽으로
                    for (int col = 0; col < n; col++) {
                        sb.append("(").append(row).append(",").append(col).append(")\\n");
                    }
                } else {
                    // 오른쪽에서 왼쪽으로
                    for (int col = n - 1; col >= 0; col--) {
                        sb.append("(").append(row).append(",").append(col).append(")\\n");
                    }
                }
            }
        }
        System.out.print(sb);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """// 그리드 그래프 - m x n 그리드에서 해밀턴 경로 찾기
#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int T;
    cin >> T;

    while (T--) {
        int m, n;
        cin >> m >> n;

        // 그리드 그래프에서 모든 정점을 방문하는 경로 출력
        // 뱀 모양으로 순회
        cout << 1 << "\\n";  // 해밀턴 경로 존재

        for (int row = 0; row < m; row++) {
            if (row % 2 == 0) {
                // 왼쪽에서 오른쪽으로
                for (int col = 0; col < n; col++) {
                    cout << "(" << row << "," << col << ")\\n";
                }
            } else {
                // 오른쪽에서 왼쪽으로
                for (int col = n - 1; col >= 0; col--) {
                    cout << "(" << row << "," << col << ")\\n";
                }
            }
        }
    }

    return 0;
}
"""
            }
        ]
    },
    "2599": {
        "solutions": [
            {
                "language": "python",
                "code": """# 짝 정하기 - 다른 초등학교 출신끼리 짝짓기
import sys
input = sys.stdin.readline

N = int(input())
boys = []
girls = []
for _ in range(3):
    m, f = map(int, input().split())
    boys.append(m)
    girls.append(f)

# 완전 탐색으로 해결 (N <= 300)
def solve():
    for ab in range(min(boys[0], girls[1]) + 1):
        for ac in range(min(boys[0] - ab, girls[2]) + 1):
            for ba in range(min(boys[1], girls[0]) + 1):
                for bc in range(min(boys[1] - ba, girls[2] - ac) + 1):
                    remain = N - ab - ac - ba - bc
                    for ca in range(max(0, remain - min(boys[2], girls[1] - ab)),
                                   min(remain, min(boys[2], girls[0] - ba)) + 1):
                        cb = remain - ca
                        if cb >= 0 and cb <= boys[2] - ca and cb <= girls[1] - ab:
                            if ca + cb <= boys[2]:
                                print(1)
                                print(ab, ac)
                                print(ba, bc)
                                print(ca, cb)
                                return
    print(0)

solve()
"""
            },
            {
                "language": "java",
                "code": """// 짝 정하기 - 다른 초등학교 출신끼리 짝짓기
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] boys = new int[3];
        int[] girls = new int[3];
        for (int i = 0; i < 3; i++) {
            boys[i] = sc.nextInt();
            girls[i] = sc.nextInt();
        }

        // 완전 탐색
        for (int ab = 0; ab <= Math.min(boys[0], girls[1]); ab++) {
            for (int ac = 0; ac <= Math.min(boys[0] - ab, girls[2]); ac++) {
                for (int ba = 0; ba <= Math.min(boys[1], girls[0]); ba++) {
                    for (int bc = 0; bc <= Math.min(boys[1] - ba, girls[2] - ac); bc++) {
                        int remain = N - ab - ac - ba - bc;
                        if (remain < 0) continue;

                        int caMax = Math.min(remain, Math.min(boys[2], girls[0] - ba));
                        int caMin = Math.max(0, remain - Math.min(boys[2], girls[1] - ab));

                        for (int ca = caMin; ca <= caMax; ca++) {
                            int cb = remain - ca;
                            if (cb >= 0 && cb <= boys[2] - ca && cb <= girls[1] - ab) {
                                if (ca + cb <= boys[2]) {
                                    System.out.println(1);
                                    System.out.println(ab + " " + ac);
                                    System.out.println(ba + " " + bc);
                                    System.out.println(ca + " " + cb);
                                    return;
                                }
                            }
                        }
                    }
                }
            }
        }
        System.out.println(0);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """// 짝 정하기 - 다른 초등학교 출신끼리 짝짓기
#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;
    int boys[3], girls[3];
    for (int i = 0; i < 3; i++) {
        cin >> boys[i] >> girls[i];
    }

    // 완전 탐색
    for (int ab = 0; ab <= min(boys[0], girls[1]); ab++) {
        for (int ac = 0; ac <= min(boys[0] - ab, girls[2]); ac++) {
            for (int ba = 0; ba <= min(boys[1], girls[0]); ba++) {
                for (int bc = 0; bc <= min(boys[1] - ba, girls[2] - ac); bc++) {
                    int remain = N - ab - ac - ba - bc;
                    if (remain < 0) continue;

                    int caMax = min(remain, min(boys[2], girls[0] - ba));
                    int caMin = max(0, remain - min(boys[2], girls[1] - ab));

                    for (int ca = caMin; ca <= caMax; ca++) {
                        int cb = remain - ca;
                        if (cb >= 0 && cb <= boys[2] - ca && cb <= girls[1] - ab) {
                            if (ca + cb <= boys[2]) {
                                cout << 1 << "\\n";
                                cout << ab << " " << ac << "\\n";
                                cout << ba << " " << bc << "\\n";
                                cout << ca << " " << cb << "\\n";
                                return 0;
                            }
                        }
                    }
                }
            }
        }
    }
    cout << 0 << "\\n";
    return 0;
}
"""
            }
        ]
    },
    "26043": {
        "solutions": [
            {
                "language": "python",
                "code": """# 식당 메뉴 - 큐를 이용한 시뮬레이션
from collections import deque
import sys
input = sys.stdin.readline

n = int(input())
queue = deque()  # (학생번호, 선호메뉴)
A = []  # 좋아하는 메뉴를 먹은 학생
B = []  # 좋아하지 않는 메뉴를 먹은 학생

for _ in range(n):
    line = list(map(int, input().split()))
    if line[0] == 1:
        # 학생 도착
        student_id, pref = line[1], line[2]
        queue.append((student_id, pref))
    else:
        # 식사 준비됨 (메뉴 line[1])
        menu = line[1]
        if queue:
            student_id, pref = queue.popleft()
            if pref == menu:
                A.append(student_id)
            else:
                B.append(student_id)

# 남은 학생들은 식사 못함
C = [student_id for student_id, _ in queue]

# 출력
if A:
    print(' '.join(map(str, A)))
else:
    print('None')

if B:
    print(' '.join(map(str, B)))
else:
    print('None')

if C:
    print(' '.join(map(str, C)))
else:
    print('None')
"""
            },
            {
                "language": "java",
                "code": """// 식당 메뉴 - 큐를 이용한 시뮬레이션
import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        Queue<int[]> queue = new LinkedList<>();  // {학생번호, 선호메뉴}
        List<Integer> A = new ArrayList<>();  // 좋아하는 메뉴 먹은 학생
        List<Integer> B = new ArrayList<>();  // 좋아하지 않는 메뉴 먹은 학생

        for (int i = 0; i < n; i++) {
            int type = sc.nextInt();
            if (type == 1) {
                // 학생 도착
                int studentId = sc.nextInt();
                int pref = sc.nextInt();
                queue.add(new int[]{studentId, pref});
            } else {
                // 식사 준비됨
                int menu = sc.nextInt();
                if (!queue.isEmpty()) {
                    int[] student = queue.poll();
                    if (student[1] == menu) {
                        A.add(student[0]);
                    } else {
                        B.add(student[0]);
                    }
                }
            }
        }

        // 남은 학생들
        List<Integer> C = new ArrayList<>();
        while (!queue.isEmpty()) {
            C.add(queue.poll()[0]);
        }

        StringBuilder sb = new StringBuilder();
        if (A.isEmpty()) sb.append("None\\n");
        else {
            for (int i = 0; i < A.size(); i++) {
                if (i > 0) sb.append(" ");
                sb.append(A.get(i));
            }
            sb.append("\\n");
        }

        if (B.isEmpty()) sb.append("None\\n");
        else {
            for (int i = 0; i < B.size(); i++) {
                if (i > 0) sb.append(" ");
                sb.append(B.get(i));
            }
            sb.append("\\n");
        }

        if (C.isEmpty()) sb.append("None");
        else {
            for (int i = 0; i < C.size(); i++) {
                if (i > 0) sb.append(" ");
                sb.append(C.get(i));
            }
        }

        System.out.println(sb);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """// 식당 메뉴 - 큐를 이용한 시뮬레이션
#include <iostream>
#include <queue>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    queue<pair<int, int>> q;  // {학생번호, 선호메뉴}
    vector<int> A, B;  // 좋아하는/않는 메뉴 먹은 학생

    for (int i = 0; i < n; i++) {
        int type;
        cin >> type;
        if (type == 1) {
            // 학생 도착
            int studentId, pref;
            cin >> studentId >> pref;
            q.push({studentId, pref});
        } else {
            // 식사 준비됨
            int menu;
            cin >> menu;
            if (!q.empty()) {
                auto [studentId, pref] = q.front();
                q.pop();
                if (pref == menu) {
                    A.push_back(studentId);
                } else {
                    B.push_back(studentId);
                }
            }
        }
    }

    // 남은 학생들
    vector<int> C;
    while (!q.empty()) {
        C.push_back(q.front().first);
        q.pop();
    }

    // 출력
    if (A.empty()) cout << "None\\n";
    else {
        for (int i = 0; i < A.size(); i++) {
            if (i > 0) cout << " ";
            cout << A[i];
        }
        cout << "\\n";
    }

    if (B.empty()) cout << "None\\n";
    else {
        for (int i = 0; i < B.size(); i++) {
            if (i > 0) cout << " ";
            cout << B[i];
        }
        cout << "\\n";
    }

    if (C.empty()) cout << "None";
    else {
        for (int i = 0; i < C.size(); i++) {
            if (i > 0) cout << " ";
            cout << C[i];
        }
    }

    return 0;
}
"""
            }
        ]
    },
    "24368": {
        "solutions": [
            {
                "language": "python",
                "code": """# 알고리즘 수업 - 점근적 표기 4
# f(n) = a2*n^2 + a1*n + a0 가 O(n^2)에 속하는지 확인
# 조건: 모든 n >= n0에 대해 f(n) <= c * n^2

a2, a1, a0 = map(int, input().split())
c = int(input())
n0 = int(input())

# f(n) <= c * n^2 인지 확인
# n >= n0인 모든 n에 대해 성립해야 함

def f(n):
    return a2 * n * n + a1 * n + a0

def g(n):
    return c * n * n

# n >= n0인 모든 n에 대해 f(n) <= c * n^2 확인
valid = True
for n in range(n0, n0 + 101):
    if f(n) > g(n):
        valid = False
        break

# a2 > c면 결국 f(n) > g(n)
if a2 > c:
    valid = False

print(1 if valid else 0)
"""
            },
            {
                "language": "java",
                "code": """// 알고리즘 수업 - 점근적 표기 4
// f(n) = a2*n^2 + a1*n + a0 가 O(n^2)에 속하는지 확인
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long a2 = sc.nextLong();
        long a1 = sc.nextLong();
        long a0 = sc.nextLong();
        long c = sc.nextLong();
        long n0 = sc.nextLong();

        // f(n) <= c * n^2 인지 확인
        boolean valid = true;

        for (long n = n0; n <= n0 + 100; n++) {
            long fn = a2 * n * n + a1 * n + a0;
            long gn = c * n * n;
            if (fn > gn) {
                valid = false;
                break;
            }
        }

        // a2 > c면 결국 f(n) > g(n)이 됨
        if (a2 > c) {
            valid = false;
        }

        System.out.println(valid ? 1 : 0);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """// 알고리즘 수업 - 점근적 표기 4
// f(n) = a2*n^2 + a1*n + a0 가 O(n^2)에 속하는지 확인
#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long a2, a1, a0, c, n0;
    cin >> a2 >> a1 >> a0 >> c >> n0;

    // f(n) <= c * n^2 인지 확인
    bool valid = true;

    for (long long n = n0; n <= n0 + 100; n++) {
        long long fn = a2 * n * n + a1 * n + a0;
        long long gn = c * n * n;
        if (fn > gn) {
            valid = false;
            break;
        }
    }

    // a2 > c면 결국 f(n) > g(n)이 됨
    if (a2 > c) {
        valid = false;
    }

    cout << (valid ? 1 : 0) << endl;

    return 0;
}
"""
            }
        ]
    },
    "26070": {
        "solutions": [
            {
                "language": "python",
                "code": """# 곰곰이와 학식 - 식권 교환으로 최대 곰곰이 배불리기
import sys
input = sys.stdin.readline
from collections import deque

# A마리: 치킨, B마리: 피자, C마리: 햄버거
A, B, C = map(int, input().split())
# X장: 치킨식권, Y장: 피자식권, Z장: 햄버거식권
X, Y, Z = map(int, input().split())

# 교환: 치킨3 -> 피자1, 피자3 -> 햄버거1, 햄버거3 -> 치킨1
# BFS로 모든 교환 경우 탐색

visited = set()
queue = deque()
queue.append((X, Y, Z))
visited.add((X, Y, Z))

max_fed = 0

while queue:
    x, y, z = queue.popleft()

    # 현재 상태에서 먹일 수 있는 곰곰이 수
    fed = min(x, A) + min(y, B) + min(z, C)
    max_fed = max(max_fed, fed)

    # 교환 시도
    # 치킨 3 -> 피자 1
    if x >= 3:
        new_state = (x - 3, y + 1, z)
        if new_state not in visited:
            visited.add(new_state)
            queue.append(new_state)

    # 피자 3 -> 햄버거 1
    if y >= 3:
        new_state = (x, y - 3, z + 1)
        if new_state not in visited:
            visited.add(new_state)
            queue.append(new_state)

    # 햄버거 3 -> 치킨 1
    if z >= 3:
        new_state = (x + 1, y, z - 3)
        if new_state not in visited:
            visited.add(new_state)
            queue.append(new_state)

print(max_fed)
"""
            },
            {
                "language": "java",
                "code": """// 곰곰이와 학식 - 식권 교환으로 최대 곰곰이 배불리기
import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int A = sc.nextInt(), B = sc.nextInt(), C = sc.nextInt();
        int X = sc.nextInt(), Y = sc.nextInt(), Z = sc.nextInt();

        // BFS로 모든 교환 경우 탐색
        Set<String> visited = new HashSet<>();
        Queue<int[]> queue = new LinkedList<>();
        queue.add(new int[]{X, Y, Z});
        visited.add(X + "," + Y + "," + Z);

        int maxFed = 0;

        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            int x = cur[0], y = cur[1], z = cur[2];

            // 현재 상태에서 먹일 수 있는 곰곰이 수
            int fed = Math.min(x, A) + Math.min(y, B) + Math.min(z, C);
            maxFed = Math.max(maxFed, fed);

            // 치킨 3 -> 피자 1
            if (x >= 3) {
                String state = (x-3) + "," + (y+1) + "," + z;
                if (!visited.contains(state)) {
                    visited.add(state);
                    queue.add(new int[]{x-3, y+1, z});
                }
            }

            // 피자 3 -> 햄버거 1
            if (y >= 3) {
                String state = x + "," + (y-3) + "," + (z+1);
                if (!visited.contains(state)) {
                    visited.add(state);
                    queue.add(new int[]{x, y-3, z+1});
                }
            }

            // 햄버거 3 -> 치킨 1
            if (z >= 3) {
                String state = (x+1) + "," + y + "," + (z-3);
                if (!visited.contains(state)) {
                    visited.add(state);
                    queue.add(new int[]{x+1, y, z-3});
                }
            }
        }

        System.out.println(maxFed);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """// 곰곰이와 학식 - 식권 교환으로 최대 곰곰이 배불리기
#include <iostream>
#include <queue>
#include <set>
#include <tuple>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int A, B, C, X, Y, Z;
    cin >> A >> B >> C >> X >> Y >> Z;

    // BFS로 모든 교환 경우 탐색
    set<tuple<int,int,int>> visited;
    queue<tuple<int,int,int>> q;
    q.push({X, Y, Z});
    visited.insert({X, Y, Z});

    int maxFed = 0;

    while (!q.empty()) {
        auto [x, y, z] = q.front();
        q.pop();

        // 현재 상태에서 먹일 수 있는 곰곰이 수
        int fed = min(x, A) + min(y, B) + min(z, C);
        maxFed = max(maxFed, fed);

        // 치킨 3 -> 피자 1
        if (x >= 3) {
            auto state = make_tuple(x-3, y+1, z);
            if (visited.find(state) == visited.end()) {
                visited.insert(state);
                q.push(state);
            }
        }

        // 피자 3 -> 햄버거 1
        if (y >= 3) {
            auto state = make_tuple(x, y-3, z+1);
            if (visited.find(state) == visited.end()) {
                visited.insert(state);
                q.push(state);
            }
        }

        // 햄버거 3 -> 치킨 1
        if (z >= 3) {
            auto state = make_tuple(x+1, y, z-3);
            if (visited.find(state) == visited.end()) {
                visited.insert(state);
                q.push(state);
            }
        }
    }

    cout << maxFed << endl;

    return 0;
}
"""
            }
        ]
    },
    "16945": {
        "solutions": [
            {
                "language": "python",
                "code": """# 매직 스퀘어로 변경하기 - 3x3 배열을 매직 스퀘어로 변환
from itertools import permutations

# 입력
A = []
for _ in range(3):
    A.append(list(map(int, input().split())))

# 3x3 매직 스퀘어는 모든 행, 열, 대각선의 합이 15

def is_magic(sq):
    target = 15
    # 행
    for i in range(3):
        if sum(sq[i]) != target:
            return False
    # 열
    for j in range(3):
        if sq[0][j] + sq[1][j] + sq[2][j] != target:
            return False
    # 대각선
    if sq[0][0] + sq[1][1] + sq[2][2] != target:
        return False
    if sq[0][2] + sq[1][1] + sq[2][0] != target:
        return False
    return True

def cost(perm, A):
    sq = [[perm[i*3 + j] for j in range(3)] for i in range(3)]
    total = 0
    for i in range(3):
        for j in range(3):
            total += abs(A[i][j] - sq[i][j])
    return total

min_cost = float('inf')
for perm in permutations(range(1, 10)):
    sq = [[perm[i*3 + j] for j in range(3)] for i in range(3)]
    if is_magic(sq):
        c = cost(perm, A)
        min_cost = min(min_cost, c)

print(min_cost)
"""
            },
            {
                "language": "java",
                "code": """// 매직 스퀘어로 변경하기 - 3x3 배열을 매직 스퀘어로 변환
import java.util.*;

public class Main {
    static int[][] A = new int[3][3];
    static int minCost = Integer.MAX_VALUE;
    static boolean[] used = new boolean[10];
    static int[] perm = new int[9];

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                A[i][j] = sc.nextInt();
            }
        }

        // 모든 순열 생성
        permute(0);
        System.out.println(minCost);
    }

    static void permute(int idx) {
        if (idx == 9) {
            int[][] sq = new int[3][3];
            for (int i = 0; i < 3; i++) {
                for (int j = 0; j < 3; j++) {
                    sq[i][j] = perm[i * 3 + j];
                }
            }
            if (isMagic(sq)) {
                int cost = 0;
                for (int i = 0; i < 3; i++) {
                    for (int j = 0; j < 3; j++) {
                        cost += Math.abs(A[i][j] - sq[i][j]);
                    }
                }
                minCost = Math.min(minCost, cost);
            }
            return;
        }

        for (int i = 1; i <= 9; i++) {
            if (!used[i]) {
                used[i] = true;
                perm[idx] = i;
                permute(idx + 1);
                used[i] = false;
            }
        }
    }

    static boolean isMagic(int[][] sq) {
        int target = 15;
        // 행
        for (int i = 0; i < 3; i++) {
            if (sq[i][0] + sq[i][1] + sq[i][2] != target) return false;
        }
        // 열
        for (int j = 0; j < 3; j++) {
            if (sq[0][j] + sq[1][j] + sq[2][j] != target) return false;
        }
        // 대각선
        if (sq[0][0] + sq[1][1] + sq[2][2] != target) return false;
        if (sq[0][2] + sq[1][1] + sq[2][0] != target) return false;
        return true;
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """// 매직 스퀘어로 변경하기 - 3x3 배열을 매직 스퀘어로 변환
#include <iostream>
#include <algorithm>
#include <cmath>
using namespace std;

int A[3][3];

bool isMagic(int perm[]) {
    int sq[3][3];
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            sq[i][j] = perm[i * 3 + j];
        }
    }

    int target = 15;
    // 행
    for (int i = 0; i < 3; i++) {
        if (sq[i][0] + sq[i][1] + sq[i][2] != target) return false;
    }
    // 열
    for (int j = 0; j < 3; j++) {
        if (sq[0][j] + sq[1][j] + sq[2][j] != target) return false;
    }
    // 대각선
    if (sq[0][0] + sq[1][1] + sq[2][2] != target) return false;
    if (sq[0][2] + sq[1][1] + sq[2][0] != target) return false;
    return true;
}

int getCost(int perm[]) {
    int cost = 0;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            cost += abs(A[i][j] - perm[i * 3 + j]);
        }
    }
    return cost;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            cin >> A[i][j];
        }
    }

    int perm[] = {1, 2, 3, 4, 5, 6, 7, 8, 9};
    int minCost = 1e9;

    do {
        if (isMagic(perm)) {
            minCost = min(minCost, getCost(perm));
        }
    } while (next_permutation(perm, perm + 9));

    cout << minCost << endl;

    return 0;
}
"""
            }
        ]
    },
    "15460": {
        "solutions": [
            {
                "language": "python",
                "code": """# My Cow Ate My Homework - 처음 K개 제외하고 최솟값 제외 평균 최대화
import sys
input = sys.stdin.readline

N = int(input())
scores = list(map(int, input().split()))

# 처음 K개를 제외하고, 나머지 중 최솟값을 제외한 평균이 최대가 되는 K 찾기
# K는 1부터 N-2까지 가능

# 뒤에서부터 누적합과 최솟값 계산
suffix_sum = [0] * (N + 1)
suffix_min = [float('inf')] * (N + 1)

for i in range(N - 1, -1, -1):
    suffix_sum[i] = suffix_sum[i + 1] + scores[i]
    suffix_min[i] = min(suffix_min[i + 1], scores[i])

best_k = 1
best_avg = -1

for k in range(1, N - 1):
    # k개 제외하면 scores[k:]가 남음
    # 그 중 최솟값 제외
    total = suffix_sum[k] - suffix_min[k]
    count = N - k - 1
    avg = total / count
    if avg > best_avg:
        best_avg = avg
        best_k = k

print(best_k)
"""
            },
            {
                "language": "java",
                "code": """// My Cow Ate My Homework - 처음 K개 제외하고 최솟값 제외 평균 최대화
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] scores = new int[N];
        for (int i = 0; i < N; i++) {
            scores[i] = sc.nextInt();
        }

        // 뒤에서부터 누적합과 최솟값 계산
        long[] suffixSum = new long[N + 1];
        int[] suffixMin = new int[N + 1];
        suffixMin[N] = Integer.MAX_VALUE;

        for (int i = N - 1; i >= 0; i--) {
            suffixSum[i] = suffixSum[i + 1] + scores[i];
            suffixMin[i] = Math.min(suffixMin[i + 1], scores[i]);
        }

        int bestK = 1;
        double bestAvg = -1;

        for (int k = 1; k < N - 1; k++) {
            // k개 제외하면 scores[k:]가 남음
            // 그 중 최솟값 제외
            long total = suffixSum[k] - suffixMin[k];
            int count = N - k - 1;
            double avg = (double) total / count;
            if (avg > bestAvg) {
                bestAvg = avg;
                bestK = k;
            }
        }

        System.out.println(bestK);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """// My Cow Ate My Homework - 처음 K개 제외하고 최솟값 제외 평균 최대화
#include <iostream>
#include <vector>
#include <climits>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;
    vector<int> scores(N);
    for (int i = 0; i < N; i++) {
        cin >> scores[i];
    }

    // 뒤에서부터 누적합과 최솟값 계산
    vector<long long> suffixSum(N + 1, 0);
    vector<int> suffixMin(N + 1, INT_MAX);

    for (int i = N - 1; i >= 0; i--) {
        suffixSum[i] = suffixSum[i + 1] + scores[i];
        suffixMin[i] = min(suffixMin[i + 1], scores[i]);
    }

    int bestK = 1;
    double bestAvg = -1;

    for (int k = 1; k < N - 1; k++) {
        // k개 제외하면 scores[k:]가 남음
        // 그 중 최솟값 제외
        long long total = suffixSum[k] - suffixMin[k];
        int count = N - k - 1;
        double avg = (double) total / count;
        if (avg > bestAvg) {
            bestAvg = avg;
            bestK = k;
        }
    }

    cout << bestK << endl;

    return 0;
}
"""
            }
        ]
    },
    "21967": {
        "solutions": [
            {
                "language": "python",
                "code": """# 세워라 반석 위에 - 최대-최소 <= 2인 가장 긴 연속 부분 수열
import sys
input = sys.stdin.readline
from collections import defaultdict

N = int(input())
A = list(map(int, input().split()))

# 슬라이딩 윈도우 + 투 포인터
count = defaultdict(int)
left = 0
max_len = 0

for right in range(N):
    count[A[right]] += 1

    # 현재 윈도우의 최대 - 최소 > 2이면 left 증가
    while True:
        min_val = min(count.keys())
        max_val = max(count.keys())
        if max_val - min_val <= 2:
            break
        count[A[left]] -= 1
        if count[A[left]] == 0:
            del count[A[left]]
        left += 1

    max_len = max(max_len, right - left + 1)

print(max_len)
"""
            },
            {
                "language": "java",
                "code": """// 세워라 반석 위에 - 최대-최소 <= 2인 가장 긴 연속 부분 수열
import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();
        int[] A = new int[N];
        for (int i = 0; i < N; i++) {
            A[i] = sc.nextInt();
        }

        // 슬라이딩 윈도우 + 투 포인터
        // 값 범위가 1~10이므로 배열로 카운트
        int[] count = new int[11];
        int left = 0;
        int maxLen = 0;

        for (int right = 0; right < N; right++) {
            count[A[right]]++;

            // 현재 윈도우의 최대 - 최소 > 2이면 left 증가
            while (true) {
                int minVal = 0, maxVal = 0;
                for (int i = 1; i <= 10; i++) {
                    if (count[i] > 0) {
                        minVal = i;
                        break;
                    }
                }
                for (int i = 10; i >= 1; i--) {
                    if (count[i] > 0) {
                        maxVal = i;
                        break;
                    }
                }
                if (maxVal - minVal <= 2) break;

                count[A[left]]--;
                left++;
            }

            maxLen = Math.max(maxLen, right - left + 1);
        }

        System.out.println(maxLen);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """// 세워라 반석 위에 - 최대-최소 <= 2인 가장 긴 연속 부분 수열
#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;
    vector<int> A(N);
    for (int i = 0; i < N; i++) {
        cin >> A[i];
    }

    // 슬라이딩 윈도우 + 투 포인터
    // 값 범위가 1~10이므로 배열로 카운트
    int count[11] = {0};
    int left = 0;
    int maxLen = 0;

    for (int right = 0; right < N; right++) {
        count[A[right]]++;

        // 현재 윈도우의 최대 - 최소 > 2이면 left 증가
        while (true) {
            int minVal = 0, maxVal = 0;
            for (int i = 1; i <= 10; i++) {
                if (count[i] > 0) {
                    minVal = i;
                    break;
                }
            }
            for (int i = 10; i >= 1; i--) {
                if (count[i] > 0) {
                    maxVal = i;
                    break;
                }
            }
            if (maxVal - minVal <= 2) break;

            count[A[left]]--;
            left++;
        }

        maxLen = max(maxLen, right - left + 1);
    }

    cout << maxLen << endl;

    return 0;
}
"""
            }
        ]
    },
    "10434": {
        "solutions": [
            {
                "language": "python",
                "code": """# 행복한 소수 - 자릿수 제곱합 반복이 1이 되는 소수
import sys
input = sys.stdin.readline

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def is_happy(n):
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        # 자릿수 제곱합
        total = 0
        while n > 0:
            total += (n % 10) ** 2
            n //= 10
        n = total
    return n == 1

P = int(input())
for _ in range(P):
    parts = input().split()
    i = int(parts[0])
    m = int(parts[1])

    if is_prime(m) and is_happy(m):
        print(f"{i} {m} YES")
    else:
        print(f"{i} {m} NO")
"""
            },
            {
                "language": "java",
                "code": """// 행복한 소수 - 자릿수 제곱합 반복이 1이 되는 소수
import java.util.*;

public class Main {
    static boolean isPrime(int n) {
        if (n < 2) return false;
        if (n == 2) return true;
        if (n % 2 == 0) return false;
        for (int i = 3; i * i <= n; i += 2) {
            if (n % i == 0) return false;
        }
        return true;
    }

    static boolean isHappy(int n) {
        Set<Integer> seen = new HashSet<>();
        while (n != 1 && !seen.contains(n)) {
            seen.add(n);
            // 자릿수 제곱합
            int total = 0;
            while (n > 0) {
                int digit = n % 10;
                total += digit * digit;
                n /= 10;
            }
            n = total;
        }
        return n == 1;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int P = sc.nextInt();
        StringBuilder sb = new StringBuilder();

        for (int t = 0; t < P; t++) {
            int i = sc.nextInt();
            int m = sc.nextInt();

            if (isPrime(m) && isHappy(m)) {
                sb.append(i).append(" ").append(m).append(" YES\\n");
            } else {
                sb.append(i).append(" ").append(m).append(" NO\\n");
            }
        }

        System.out.print(sb);
    }
}
"""
            },
            {
                "language": "cpp",
                "code": """// 행복한 소수 - 자릿수 제곱합 반복이 1이 되는 소수
#include <iostream>
#include <set>
using namespace std;

bool isPrime(int n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    for (int i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return false;
    }
    return true;
}

bool isHappy(int n) {
    set<int> seen;
    while (n != 1 && seen.find(n) == seen.end()) {
        seen.insert(n);
        // 자릿수 제곱합
        int total = 0;
        while (n > 0) {
            int digit = n % 10;
            total += digit * digit;
            n /= 10;
        }
        n = total;
    }
    return n == 1;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int P;
    cin >> P;

    while (P--) {
        int i, m;
        cin >> i >> m;

        if (isPrime(m) && isHappy(m)) {
            cout << i << " " << m << " YES\\n";
        } else {
            cout << i << " " << m << " NO\\n";
        }
    }

    return 0;
}
"""
            }
        ]
    }
}

# 기존 데이터에 새로운 솔루션 추가
data.update(new_solutions)

# 저장
with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Added solutions for {len(new_solutions)} problems')
print('Problem IDs:', list(new_solutions.keys()))
print('Total problems now:', len(data))
