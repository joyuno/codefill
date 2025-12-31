#!/usr/bin/env python3
"""
배치 5: 인덱스 [1132, 1138, 1144, 1151, 1163, 1174, 1184, 1193, 1211, 1212]의 솔루션 생성
"""

import json

# 메인 파일 경로
MAIN_FILE = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

# 각 문제에 대한 솔루션
solutions_data = {
    # 1132: baekjoon_1422 - 숫자의 신 (K개 수 중 N개를 뽑아 가장 큰 수 만들기)
    1132: [
        {
            "language": "python",
            "code": '''import sys
input = sys.stdin.readline

# K개의 수 중 N개를 뽑아 가장 큰 수 만들기
# 모든 수는 적어도 한 번 이상 사용

def compare(a, b):
    # a+b와 b+a를 비교하여 정렬 기준 결정
    return a + b > b + a

def solve():
    K, N = map(int, input().split())
    nums = []
    for _ in range(K):
        nums.append(input().strip())

    # 문자열 비교로 정렬 (a+b > b+a 기준)
    from functools import cmp_to_key
    nums.sort(key=cmp_to_key(lambda a, b: -1 if a + b > b + a else 1))

    # 추가로 뽑을 수: N - K개
    extra = N - K

    # 가장 긴 수를 찾아서 extra번 추가
    # 단, 반복할 수는 자기 자신을 반복했을 때 가장 큰 값을 만드는 수
    max_num = ""
    max_len = 0
    for num in nums:
        if len(num) > max_len:
            max_len = len(num)
            max_num = num
        elif len(num) == max_len:
            if num + max_num > max_num + num:
                max_num = num

    # 결과 리스트 생성 (모든 수 + 가장 좋은 수 extra번)
    result = nums[:]
    for _ in range(extra):
        result.append(max_num)

    # 다시 정렬
    result.sort(key=cmp_to_key(lambda a, b: -1 if a + b > b + a else 1))

    print(''.join(result))

solve()
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

        int K = Integer.parseInt(st.nextToken());
        int N = Integer.parseInt(st.nextToken());

        String[] nums = new String[K];
        for (int i = 0; i < K; i++) {
            nums[i] = br.readLine().trim();
        }

        // 가장 큰 수를 만들기 위한 비교 정렬
        Arrays.sort(nums, (a, b) -> (b + a).compareTo(a + b));

        // 반복할 최적의 수 찾기 (가장 긴 것 중 반복 시 가장 큰 것)
        String maxNum = "";
        int maxLen = 0;
        for (String num : nums) {
            if (num.length() > maxLen) {
                maxLen = num.length();
                maxNum = num;
            } else if (num.length() == maxLen) {
                if ((num + maxNum).compareTo(maxNum + num) > 0) {
                    maxNum = num;
                }
            }
        }

        // 결과 리스트 구성
        int extra = N - K;
        List<String> result = new ArrayList<>();
        for (String num : nums) {
            result.add(num);
        }
        for (int i = 0; i < extra; i++) {
            result.add(maxNum);
        }

        // 다시 정렬
        result.sort((a, b) -> (b + a).compareTo(a + b));

        StringBuilder sb = new StringBuilder();
        for (String s : result) {
            sb.append(s);
        }
        System.out.println(sb);
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

// 문자열 비교 함수: a+b > b+a 기준 정렬
bool compare(const string& a, const string& b) {
    return a + b > b + a;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int K, N;
    cin >> K >> N;

    vector<string> nums(K);
    for (int i = 0; i < K; i++) {
        cin >> nums[i];
    }

    // 반복할 최적의 수 찾기 (가장 긴 것 중 반복 시 가장 큰 것)
    string maxNum = "";
    int maxLen = 0;
    for (const string& num : nums) {
        if ((int)num.length() > maxLen) {
            maxLen = num.length();
            maxNum = num;
        } else if ((int)num.length() == maxLen) {
            if (num + maxNum > maxNum + num) {
                maxNum = num;
            }
        }
    }

    // 결과 리스트 구성 (모든 수 + 최적의 수 extra번)
    int extra = N - K;
    vector<string> result = nums;
    for (int i = 0; i < extra; i++) {
        result.push_back(maxNum);
    }

    // 정렬 후 출력
    sort(result.begin(), result.end(), compare);

    for (const string& s : result) {
        cout << s;
    }
    cout << endl;

    return 0;
}
'''
        }
    ],

    # 1138: baekjoon_1695 - 팰린드롬 만들기 (최소 삽입 수)
    1138: [
        {
            "language": "python",
            "code": '''import sys
input = sys.stdin.readline

# 수열을 팰린드롬으로 만들기 위해 끼워 넣을 최소 개수
# LCS를 이용: n - LCS(원본, 역순) = 최소 삽입 개수

def solve():
    n = int(input())
    arr = list(map(int, input().split()))

    # 역순 배열
    rev = arr[::-1]

    # LCS (Longest Common Subsequence) 계산
    # 메모리 최적화: 2행만 사용
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)

    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if arr[i - 1] == rev[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev, curr = curr, prev

    # 최소 삽입 개수 = n - LCS 길이
    lcs_len = prev[n]
    print(n - lcs_len)

solve()
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int[] arr = new int[n];
        int[] rev = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
            rev[n - 1 - i] = arr[i];
        }

        // LCS 계산 (메모리 최적화: 2행만 사용)
        int[] prev = new int[n + 1];
        int[] curr = new int[n + 1];

        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++) {
                if (arr[i - 1] == rev[j - 1]) {
                    curr[j] = prev[j - 1] + 1;
                } else {
                    curr[j] = Math.max(prev[j], curr[j - 1]);
                }
            }
            // swap
            int[] temp = prev;
            prev = curr;
            curr = temp;
            Arrays.fill(curr, 0);
        }

        // 최소 삽입 개수 = n - LCS 길이
        System.out.println(n - prev[n]);
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

    int n;
    cin >> n;

    vector<int> arr(n), rev(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
        rev[n - 1 - i] = arr[i];
    }

    // LCS 계산 (메모리 최적화: 2행만 사용)
    vector<int> prev(n + 1, 0), curr(n + 1, 0);

    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= n; j++) {
            if (arr[i - 1] == rev[j - 1]) {
                curr[j] = prev[j - 1] + 1;
            } else {
                curr[j] = max(prev[j], curr[j - 1]);
            }
        }
        swap(prev, curr);
        fill(curr.begin(), curr.end(), 0);
    }

    // 최소 삽입 개수 = n - LCS 길이
    cout << n - prev[n] << endl;

    return 0;
}
'''
        }
    ],

    # 1144: baekjoon_17069 - 파이프 옮기기 2 (N <= 32, 경우의 수)
    1144: [
        {
            "language": "python",
            "code": '''import sys
input = sys.stdin.readline

# 파이프 옮기기 2: (1,2)에서 (N,N)까지 이동하는 방법의 수
# 상태: 가로(0), 세로(1), 대각선(2)

def solve():
    N = int(input())
    grid = []
    for _ in range(N):
        grid.append(list(map(int, input().split())))

    # dp[r][c][state] = (r,c)에 state 상태로 도달하는 경우의 수
    # state: 0=가로, 1=세로, 2=대각선
    dp = [[[0] * 3 for _ in range(N)] for _ in range(N)]

    # 초기 상태: (0,1)에 가로 상태로 시작
    dp[0][1][0] = 1

    for r in range(N):
        for c in range(N):
            if grid[r][c] == 1:
                continue

            # 가로 상태로 (r, c)에 도달
            if c > 0 and grid[r][c] == 0:
                # 이전이 가로였거나 대각선이었을 때
                if c >= 1:
                    dp[r][c][0] += dp[r][c-1][0]  # 가로에서 가로
                    dp[r][c][0] += dp[r][c-1][2]  # 대각선에서 가로

            # 세로 상태로 (r, c)에 도달
            if r > 0 and grid[r][c] == 0:
                # 이전이 세로였거나 대각선이었을 때
                dp[r][c][1] += dp[r-1][c][1]  # 세로에서 세로
                dp[r][c][1] += dp[r-1][c][2]  # 대각선에서 세로

            # 대각선 상태로 (r, c)에 도달
            if r > 0 and c > 0 and grid[r][c] == 0 and grid[r-1][c] == 0 and grid[r][c-1] == 0:
                # 이전이 가로, 세로, 대각선 모두 가능
                dp[r][c][2] += dp[r-1][c-1][0]  # 가로에서 대각선
                dp[r][c][2] += dp[r-1][c-1][1]  # 세로에서 대각선
                dp[r][c][2] += dp[r-1][c-1][2]  # 대각선에서 대각선

    # (N-1, N-1)에 도달하는 모든 경우의 수
    print(sum(dp[N-1][N-1]))

solve()
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());
        int[][] grid = new int[N][N];

        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < N; j++) {
                grid[i][j] = Integer.parseInt(st.nextToken());
            }
        }

        // dp[r][c][state]: (r,c)에 state 상태로 도달하는 경우의 수
        // state: 0=가로, 1=세로, 2=대각선
        long[][][] dp = new long[N][N][3];

        // 초기 상태: (0,1)에 가로 상태로 시작
        dp[0][1][0] = 1;

        for (int r = 0; r < N; r++) {
            for (int c = 0; c < N; c++) {
                if (grid[r][c] == 1) continue;

                // 가로 상태로 도달
                if (c > 0 && grid[r][c] == 0) {
                    dp[r][c][0] += dp[r][c-1][0];  // 가로에서 가로
                    dp[r][c][0] += dp[r][c-1][2];  // 대각선에서 가로
                }

                // 세로 상태로 도달
                if (r > 0 && grid[r][c] == 0) {
                    dp[r][c][1] += dp[r-1][c][1];  // 세로에서 세로
                    dp[r][c][1] += dp[r-1][c][2];  // 대각선에서 세로
                }

                // 대각선 상태로 도달
                if (r > 0 && c > 0 && grid[r][c] == 0 && grid[r-1][c] == 0 && grid[r][c-1] == 0) {
                    dp[r][c][2] += dp[r-1][c-1][0];  // 가로에서 대각선
                    dp[r][c][2] += dp[r-1][c-1][1];  // 세로에서 대각선
                    dp[r][c][2] += dp[r-1][c-1][2];  // 대각선에서 대각선
                }
            }
        }

        // (N-1, N-1)에 도달하는 모든 경우의 수
        System.out.println(dp[N-1][N-1][0] + dp[N-1][N-1][1] + dp[N-1][N-1][2]);
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

    vector<vector<int>> grid(N, vector<int>(N));
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            cin >> grid[i][j];
        }
    }

    // dp[r][c][state]: (r,c)에 state 상태로 도달하는 경우의 수
    // state: 0=가로, 1=세로, 2=대각선
    vector<vector<vector<long long>>> dp(N, vector<vector<long long>>(N, vector<long long>(3, 0)));

    // 초기 상태: (0,1)에 가로 상태로 시작
    dp[0][1][0] = 1;

    for (int r = 0; r < N; r++) {
        for (int c = 0; c < N; c++) {
            if (grid[r][c] == 1) continue;

            // 가로 상태로 도달
            if (c > 0 && grid[r][c] == 0) {
                dp[r][c][0] += dp[r][c-1][0];  // 가로에서 가로
                dp[r][c][0] += dp[r][c-1][2];  // 대각선에서 가로
            }

            // 세로 상태로 도달
            if (r > 0 && grid[r][c] == 0) {
                dp[r][c][1] += dp[r-1][c][1];  // 세로에서 세로
                dp[r][c][1] += dp[r-1][c][2];  // 대각선에서 세로
            }

            // 대각선 상태로 도달
            if (r > 0 && c > 0 && grid[r][c] == 0 && grid[r-1][c] == 0 && grid[r][c-1] == 0) {
                dp[r][c][2] += dp[r-1][c-1][0];  // 가로에서 대각선
                dp[r][c][2] += dp[r-1][c-1][1];  // 세로에서 대각선
                dp[r][c][2] += dp[r-1][c-1][2];  // 대각선에서 대각선
            }
        }
    }

    // (N-1, N-1)에 도달하는 모든 경우의 수
    cout << dp[N-1][N-1][0] + dp[N-1][N-1][1] + dp[N-1][N-1][2] << endl;

    return 0;
}
'''
        }
    ],

    # 1151: baekjoon_2591 - 숫자 카드 (1~34 카드로 수열 만들기)
    1151: [
        {
            "language": "python",
            "code": '''import sys
input = sys.stdin.readline

# 1~34까지의 카드로 숫자 문자열을 만들 수 있는 경우의 수
# DP: dp[i] = i번째 위치까지 해석할 수 있는 경우의 수

def solve():
    s = input().strip()
    n = len(s)

    if n == 0 or s[0] == '0':
        print(0)
        return

    # dp[i] = s[0:i]를 해석할 수 있는 경우의 수
    dp = [0] * (n + 1)
    dp[0] = 1  # 빈 문자열
    dp[1] = 1  # 첫 글자 (0이 아님)

    for i in range(2, n + 1):
        # 한 자리 수로 해석 (1~9)
        one_digit = int(s[i-1])
        if 1 <= one_digit <= 9:
            dp[i] += dp[i-1]

        # 두 자리 수로 해석 (10~34)
        two_digit = int(s[i-2:i])
        if 10 <= two_digit <= 34:
            dp[i] += dp[i-2]

    print(dp[n])

solve()
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        String s = br.readLine().trim();
        int n = s.length();

        if (n == 0 || s.charAt(0) == '0') {
            System.out.println(0);
            return;
        }

        // dp[i] = s[0:i]를 해석할 수 있는 경우의 수
        long[] dp = new long[n + 1];
        dp[0] = 1;  // 빈 문자열
        dp[1] = 1;  // 첫 글자 (0이 아님)

        for (int i = 2; i <= n; i++) {
            // 한 자리 수로 해석 (1~9)
            int oneDigit = s.charAt(i - 1) - '0';
            if (1 <= oneDigit && oneDigit <= 9) {
                dp[i] += dp[i - 1];
            }

            // 두 자리 수로 해석 (10~34)
            int twoDigit = Integer.parseInt(s.substring(i - 2, i));
            if (10 <= twoDigit && twoDigit <= 34) {
                dp[i] += dp[i - 2];
            }
        }

        System.out.println(dp[n]);
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

    string s;
    cin >> s;
    int n = s.length();

    if (n == 0 || s[0] == '0') {
        cout << 0 << endl;
        return 0;
    }

    // dp[i] = s[0:i]를 해석할 수 있는 경우의 수
    long long dp[n + 1];
    for (int i = 0; i <= n; i++) dp[i] = 0;

    dp[0] = 1;  // 빈 문자열
    dp[1] = 1;  // 첫 글자 (0이 아님)

    for (int i = 2; i <= n; i++) {
        // 한 자리 수로 해석 (1~9)
        int oneDigit = s[i - 1] - '0';
        if (1 <= oneDigit && oneDigit <= 9) {
            dp[i] += dp[i - 1];
        }

        // 두 자리 수로 해석 (10~34)
        int twoDigit = (s[i - 2] - '0') * 10 + (s[i - 1] - '0');
        if (10 <= twoDigit && twoDigit <= 34) {
            dp[i] += dp[i - 2];
        }
    }

    cout << dp[n] << endl;

    return 0;
}
'''
        }
    ],

    # 1163: baekjoon_2662 - 기업 투자 (배낭 문제 변형, 경로 추적)
    1163: [
        {
            "language": "python",
            "code": '''import sys
input = sys.stdin.readline

# 기업 투자: N만원을 M개 기업에 투자하여 최대 이익 얻기
# 각 기업에 투자한 액수도 출력해야 함

def solve():
    N, M = map(int, input().split())

    # profit[i][j] = i만원을 j번 기업에 투자했을 때 이익
    profit = [[0] * (M + 1) for _ in range(N + 1)]

    for i in range(1, N + 1):
        line = list(map(int, input().split()))
        # line[0]은 투자액수, line[1:]은 각 기업의 이익
        for j in range(1, M + 1):
            profit[i][j] = line[j]

    # dp[i][j] = j번 기업까지 고려하여 i만원을 투자했을 때 최대 이익
    dp = [[0] * (M + 1) for _ in range(N + 1)]
    # choice[i][j] = dp[i][j]를 달성할 때 j번 기업에 투자한 금액
    choice = [[0] * (M + 1) for _ in range(N + 1)]

    for j in range(1, M + 1):  # 각 기업
        for i in range(N + 1):  # 총 투자금액
            # j번 기업에 k만원 투자
            for k in range(i + 1):
                if dp[i - k][j - 1] + profit[k][j] > dp[i][j]:
                    dp[i][j] = dp[i - k][j - 1] + profit[k][j]
                    choice[i][j] = k

    # 결과 출력
    print(dp[N][M])

    # 역추적: 각 기업에 투자한 금액
    investments = [0] * (M + 1)
    remaining = N
    for j in range(M, 0, -1):
        investments[j] = choice[remaining][j]
        remaining -= investments[j]

    print(' '.join(map(str, investments[1:])))

solve()
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

        int N = Integer.parseInt(st.nextToken());  // 투자 금액
        int M = Integer.parseInt(st.nextToken());  // 기업 수

        // profit[i][j] = i만원을 j번 기업에 투자했을 때 이익
        int[][] profit = new int[N + 1][M + 1];

        for (int i = 1; i <= N; i++) {
            st = new StringTokenizer(br.readLine());
            st.nextToken();  // 투자액수 (i와 동일)
            for (int j = 1; j <= M; j++) {
                profit[i][j] = Integer.parseInt(st.nextToken());
            }
        }

        // dp[i][j] = j번 기업까지 고려하여 i만원을 투자했을 때 최대 이익
        int[][] dp = new int[N + 1][M + 1];
        int[][] choice = new int[N + 1][M + 1];

        for (int j = 1; j <= M; j++) {
            for (int i = 0; i <= N; i++) {
                for (int k = 0; k <= i; k++) {
                    if (dp[i - k][j - 1] + profit[k][j] > dp[i][j]) {
                        dp[i][j] = dp[i - k][j - 1] + profit[k][j];
                        choice[i][j] = k;
                    }
                }
            }
        }

        // 결과 출력
        StringBuilder sb = new StringBuilder();
        sb.append(dp[N][M]).append("\\n");

        // 역추적
        int[] investments = new int[M + 1];
        int remaining = N;
        for (int j = M; j >= 1; j--) {
            investments[j] = choice[remaining][j];
            remaining -= investments[j];
        }

        for (int j = 1; j <= M; j++) {
            sb.append(investments[j]);
            if (j < M) sb.append(" ");
        }
        System.out.println(sb);
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

    int N, M;
    cin >> N >> M;

    // profit[i][j] = i만원을 j번 기업에 투자했을 때 이익
    vector<vector<int>> profit(N + 1, vector<int>(M + 1, 0));

    for (int i = 1; i <= N; i++) {
        int amount;
        cin >> amount;  // 투자액수 (i와 동일)
        for (int j = 1; j <= M; j++) {
            cin >> profit[i][j];
        }
    }

    // dp[i][j] = j번 기업까지 고려하여 i만원을 투자했을 때 최대 이익
    vector<vector<int>> dp(N + 1, vector<int>(M + 1, 0));
    vector<vector<int>> choice(N + 1, vector<int>(M + 1, 0));

    for (int j = 1; j <= M; j++) {
        for (int i = 0; i <= N; i++) {
            for (int k = 0; k <= i; k++) {
                if (dp[i - k][j - 1] + profit[k][j] > dp[i][j]) {
                    dp[i][j] = dp[i - k][j - 1] + profit[k][j];
                    choice[i][j] = k;
                }
            }
        }
    }

    // 결과 출력
    cout << dp[N][M] << "\\n";

    // 역추적
    vector<int> investments(M + 1, 0);
    int remaining = N;
    for (int j = M; j >= 1; j--) {
        investments[j] = choice[remaining][j];
        remaining -= investments[j];
    }

    for (int j = 1; j <= M; j++) {
        cout << investments[j];
        if (j < M) cout << " ";
    }
    cout << endl;

    return 0;
}
'''
        }
    ],

    # 1174: baekjoon_3111 - 검열 (앞/뒤에서 번갈아가며 패턴 삭제)
    1174: [
        {
            "language": "python",
            "code": '''import sys
input = sys.stdin.readline

# 검열: A를 앞에서, 뒤에서 번갈아가며 삭제

def solve():
    A = input().strip()
    T = input().strip()

    lenA = len(A)
    lenT = len(T)

    # 앞에서부터 처리한 결과 (스택)
    front = []
    # 뒤에서부터 처리한 결과 (스택, 역순)
    back = []

    left = 0
    right = lenT - 1
    turn = True  # True: 앞에서, False: 뒤에서

    while left <= right:
        if turn:
            # 앞에서 A 찾기
            while left <= right:
                front.append(T[left])
                left += 1
                # front 끝에서 A가 완성되었는지 확인
                if len(front) >= lenA and ''.join(front[-lenA:]) == A:
                    for _ in range(lenA):
                        front.pop()
                    break
            turn = False
        else:
            # 뒤에서 A 찾기
            while left <= right:
                back.append(T[right])
                right -= 1
                # back 끝에서 A의 역순이 완성되었는지 확인
                if len(back) >= lenA:
                    check = ''.join(back[-lenA:][::-1])
                    if check == A:
                        for _ in range(lenA):
                            back.pop()
                        break
            turn = True

    # front + back(역순)을 합쳐서 A 제거 반복
    result = front + back[::-1]

    # 추가로 A가 있으면 제거
    while True:
        s = ''.join(result)
        idx = s.find(A)
        if idx == -1:
            break
        result = list(s[:idx] + s[idx + lenA:])

    print(''.join(result))

solve()
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        String A = br.readLine().trim();
        String T = br.readLine().trim();

        int lenA = A.length();
        int lenT = T.length();

        // 앞에서부터 처리한 결과
        StringBuilder front = new StringBuilder();
        // 뒤에서부터 처리한 결과 (역순)
        StringBuilder back = new StringBuilder();

        int left = 0;
        int right = lenT - 1;
        boolean turn = true;  // true: 앞에서, false: 뒤에서

        while (left <= right) {
            if (turn) {
                // 앞에서 A 찾기
                while (left <= right) {
                    front.append(T.charAt(left));
                    left++;
                    if (front.length() >= lenA) {
                        String suffix = front.substring(front.length() - lenA);
                        if (suffix.equals(A)) {
                            front.setLength(front.length() - lenA);
                            break;
                        }
                    }
                }
                turn = false;
            } else {
                // 뒤에서 A 찾기 (역순으로 저장)
                while (left <= right) {
                    back.append(T.charAt(right));
                    right--;
                    if (back.length() >= lenA) {
                        // back의 끝 lenA개를 뒤집어서 A와 비교
                        StringBuilder check = new StringBuilder(back.substring(back.length() - lenA));
                        if (check.reverse().toString().equals(A)) {
                            back.setLength(back.length() - lenA);
                            break;
                        }
                    }
                }
                turn = true;
            }
        }

        // front + back(역순) 합치기
        StringBuilder result = new StringBuilder();
        result.append(front);
        result.append(back.reverse());

        // 추가로 A 제거
        String s = result.toString();
        while (true) {
            int idx = s.indexOf(A);
            if (idx == -1) break;
            s = s.substring(0, idx) + s.substring(idx + lenA);
        }

        System.out.println(s);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string A, T;
    cin >> A >> T;

    int lenA = A.length();
    int lenT = T.length();

    // 앞에서부터 처리한 결과
    string front = "";
    // 뒤에서부터 처리한 결과 (역순)
    string back = "";

    int left = 0;
    int right = lenT - 1;
    bool turn = true;  // true: 앞에서, false: 뒤에서

    while (left <= right) {
        if (turn) {
            // 앞에서 A 찾기
            while (left <= right) {
                front += T[left];
                left++;
                if ((int)front.length() >= lenA) {
                    string suffix = front.substr(front.length() - lenA);
                    if (suffix == A) {
                        front.erase(front.length() - lenA);
                        break;
                    }
                }
            }
            turn = false;
        } else {
            // 뒤에서 A 찾기 (역순으로 저장)
            while (left <= right) {
                back += T[right];
                right--;
                if ((int)back.length() >= lenA) {
                    // back의 끝 lenA개를 뒤집어서 A와 비교
                    string check = back.substr(back.length() - lenA);
                    reverse(check.begin(), check.end());
                    if (check == A) {
                        back.erase(back.length() - lenA);
                        break;
                    }
                }
            }
            turn = true;
        }
    }

    // back 뒤집기
    reverse(back.begin(), back.end());

    // front + back 합치기
    string result = front + back;

    // 추가로 A 제거
    while (true) {
        size_t idx = result.find(A);
        if (idx == string::npos) break;
        result = result.substr(0, idx) + result.substr(idx + lenA);
    }

    cout << result << endl;

    return 0;
}
'''
        }
    ],

    # 1184: baekjoon_2253 - 점프 (돌다리 건너기)
    1184: [
        {
            "language": "python",
            "code": '''import sys
from collections import deque
input = sys.stdin.readline

# 돌다리 건너기: 1번에서 N번으로 최소 점프 횟수
# 첫 점프는 1칸, 이후 x-1, x, x+1칸 점프 가능

def solve():
    line = input().split()
    N = int(line[0])
    M = int(line[1])

    # 작은 돌 집합
    small = set()
    for _ in range(M):
        small.add(int(input()))

    if N == 1:
        print(0)
        return

    # 최대 속도 계산: 1+2+3+...+v <= N-1 => v*(v+1)/2 <= N-1
    # v <= sqrt(2*N)
    import math
    max_v = int(math.sqrt(2 * N)) + 2

    # BFS: (위치, 속도)
    # dp[pos][v] = 최소 점프 횟수
    INF = float('inf')
    dp = [[INF] * (max_v + 1) for _ in range(N + 1)]

    queue = deque()

    # 시작: 1번 돌, 첫 점프는 1칸
    if 2 not in small:
        dp[2][1] = 1
        queue.append((2, 1))

    while queue:
        pos, v = queue.popleft()

        if pos == N:
            print(dp[pos][v])
            return

        # 다음 점프: v-1, v, v+1
        for dv in [-1, 0, 1]:
            nv = v + dv
            if nv < 1 or nv > max_v:
                continue
            npos = pos + nv
            if npos < 1 or npos > N:
                continue
            if npos in small:
                continue
            if dp[npos][nv] > dp[pos][v] + 1:
                dp[npos][nv] = dp[pos][v] + 1
                queue.append((npos, nv))

    # N에 도달할 수 없는 경우
    result = min(dp[N])
    if result == INF:
        print(-1)
    else:
        print(result)

solve()
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

        Set<Integer> small = new HashSet<>();
        for (int i = 0; i < M; i++) {
            small.add(Integer.parseInt(br.readLine().trim()));
        }

        if (N == 1) {
            System.out.println(0);
            return;
        }

        // 최대 속도 계산
        int maxV = (int) Math.sqrt(2 * N) + 2;

        // BFS: (위치, 속도)
        int[][] dp = new int[N + 1][maxV + 1];
        for (int[] row : dp) Arrays.fill(row, Integer.MAX_VALUE);

        Queue<int[]> queue = new LinkedList<>();

        if (!small.contains(2)) {
            dp[2][1] = 1;
            queue.offer(new int[]{2, 1});
        }

        while (!queue.isEmpty()) {
            int[] curr = queue.poll();
            int pos = curr[0];
            int v = curr[1];

            if (pos == N) {
                System.out.println(dp[pos][v]);
                return;
            }

            // 다음 점프: v-1, v, v+1
            for (int dv = -1; dv <= 1; dv++) {
                int nv = v + dv;
                if (nv < 1 || nv > maxV) continue;
                int npos = pos + nv;
                if (npos < 1 || npos > N) continue;
                if (small.contains(npos)) continue;
                if (dp[npos][nv] > dp[pos][v] + 1) {
                    dp[npos][nv] = dp[pos][v] + 1;
                    queue.offer(new int[]{npos, nv});
                }
            }
        }

        // N에 도달할 수 있는지 확인
        int result = Integer.MAX_VALUE;
        for (int v = 1; v <= maxV; v++) {
            result = Math.min(result, dp[N][v]);
        }

        System.out.println(result == Integer.MAX_VALUE ? -1 : result);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
#include <queue>
#include <set>
#include <cmath>
#include <climits>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    set<int> small;
    for (int i = 0; i < M; i++) {
        int x;
        cin >> x;
        small.insert(x);
    }

    if (N == 1) {
        cout << 0 << endl;
        return 0;
    }

    // 최대 속도 계산
    int maxV = (int)sqrt(2.0 * N) + 2;

    // BFS: (위치, 속도)
    vector<vector<int>> dp(N + 1, vector<int>(maxV + 1, INT_MAX));

    queue<pair<int, int>> q;

    if (small.find(2) == small.end()) {
        dp[2][1] = 1;
        q.push({2, 1});
    }

    while (!q.empty()) {
        auto [pos, v] = q.front();
        q.pop();

        if (pos == N) {
            cout << dp[pos][v] << endl;
            return 0;
        }

        // 다음 점프: v-1, v, v+1
        for (int dv = -1; dv <= 1; dv++) {
            int nv = v + dv;
            if (nv < 1 || nv > maxV) continue;
            int npos = pos + nv;
            if (npos < 1 || npos > N) continue;
            if (small.find(npos) != small.end()) continue;
            if (dp[npos][nv] > dp[pos][v] + 1) {
                dp[npos][nv] = dp[pos][v] + 1;
                q.push({npos, nv});
            }
        }
    }

    // N에 도달할 수 있는지 확인
    int result = INT_MAX;
    for (int v = 1; v <= maxV; v++) {
        result = min(result, dp[N][v]);
    }

    cout << (result == INT_MAX ? -1 : result) << endl;

    return 0;
}
'''
        }
    ],

    # 1193: baekjoon_13308 - 주유소 (다익스트라 + 상태)
    1193: [
        {
            "language": "python",
            "code": '''import sys
import heapq
input = sys.stdin.readline

# 주유소: 1번에서 N번 도시로 최소 비용 이동
# 다익스트라 + 상태 (현재 최소 기름 가격)

def solve():
    N, M = map(int, input().split())
    prices = [0] + list(map(int, input().split()))  # 1-indexed

    # 그래프 구성
    graph = [[] for _ in range(N + 1)]
    for _ in range(M):
        u, v, w = map(int, input().split())
        graph[u].append((v, w))
        graph[v].append((u, w))

    # dist[city][min_price] = 최소 비용
    # min_price: 지금까지 방문한 도시 중 가장 싼 기름 가격
    INF = float('inf')
    max_price = 2501
    dist = [[INF] * max_price for _ in range(N + 1)]

    # 시작: 1번 도시, 최소 가격 = prices[1]
    pq = [(0, 1, prices[1])]  # (비용, 도시, 최소가격)
    dist[1][prices[1]] = 0

    while pq:
        cost, city, min_price = heapq.heappop(pq)

        if city == N:
            print(cost)
            return

        if cost > dist[city][min_price]:
            continue

        for next_city, road_len in graph[city]:
            new_cost = cost + min_price * road_len
            new_min_price = min(min_price, prices[next_city])

            if new_cost < dist[next_city][new_min_price]:
                dist[next_city][new_min_price] = new_cost
                heapq.heappush(pq, (new_cost, next_city, new_min_price))

    print(-1)

solve()
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

        int[] prices = new int[N + 1];
        st = new StringTokenizer(br.readLine());
        for (int i = 1; i <= N; i++) {
            prices[i] = Integer.parseInt(st.nextToken());
        }

        // 그래프 구성
        List<int[]>[] graph = new ArrayList[N + 1];
        for (int i = 0; i <= N; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < M; i++) {
            st = new StringTokenizer(br.readLine());
            int u = Integer.parseInt(st.nextToken());
            int v = Integer.parseInt(st.nextToken());
            int w = Integer.parseInt(st.nextToken());
            graph[u].add(new int[]{v, w});
            graph[v].add(new int[]{u, w});
        }

        // dist[city][min_price] = 최소 비용
        int maxPrice = 2501;
        long[][] dist = new long[N + 1][maxPrice];
        for (long[] row : dist) Arrays.fill(row, Long.MAX_VALUE);

        // 우선순위 큐: (비용, 도시, 최소가격)
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        pq.offer(new long[]{0, 1, prices[1]});
        dist[1][prices[1]] = 0;

        while (!pq.isEmpty()) {
            long[] curr = pq.poll();
            long cost = curr[0];
            int city = (int) curr[1];
            int minPrice = (int) curr[2];

            if (city == N) {
                System.out.println(cost);
                return;
            }

            if (cost > dist[city][minPrice]) continue;

            for (int[] edge : graph[city]) {
                int nextCity = edge[0];
                int roadLen = edge[1];
                long newCost = cost + (long) minPrice * roadLen;
                int newMinPrice = Math.min(minPrice, prices[nextCity]);

                if (newCost < dist[nextCity][newMinPrice]) {
                    dist[nextCity][newMinPrice] = newCost;
                    pq.offer(new long[]{newCost, nextCity, newMinPrice});
                }
            }
        }

        System.out.println(-1);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
#include <queue>
#include <climits>
using namespace std;

typedef long long ll;
typedef tuple<ll, int, int> pli;  // cost, city, min_price

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    cin >> N >> M;

    vector<int> prices(N + 1);
    for (int i = 1; i <= N; i++) {
        cin >> prices[i];
    }

    // 그래프 구성
    vector<vector<pair<int, int>>> graph(N + 1);
    for (int i = 0; i < M; i++) {
        int u, v, w;
        cin >> u >> v >> w;
        graph[u].push_back({v, w});
        graph[v].push_back({u, w});
    }

    // dist[city][min_price] = 최소 비용
    int maxPrice = 2501;
    vector<vector<ll>> dist(N + 1, vector<ll>(maxPrice, LLONG_MAX));

    // 우선순위 큐: (비용, 도시, 최소가격)
    priority_queue<pli, vector<pli>, greater<pli>> pq;
    pq.push({0, 1, prices[1]});
    dist[1][prices[1]] = 0;

    while (!pq.empty()) {
        auto [cost, city, minPrice] = pq.top();
        pq.pop();

        if (city == N) {
            cout << cost << endl;
            return 0;
        }

        if (cost > dist[city][minPrice]) continue;

        for (auto& [nextCity, roadLen] : graph[city]) {
            ll newCost = cost + (ll)minPrice * roadLen;
            int newMinPrice = min(minPrice, prices[nextCity]);

            if (newCost < dist[nextCity][newMinPrice]) {
                dist[nextCity][newMinPrice] = newCost;
                pq.push({newCost, nextCity, newMinPrice});
            }
        }
    }

    cout << -1 << endl;

    return 0;
}
'''
        }
    ],

    # 1211: baekjoon_9659 - 돌 게임 5 (이미 Python 솔루션 있음, Java/C++ 추가)
    1211: [
        {
            "language": "python",
            "code": '''# 돌 게임 5: N개의 돌, 1개 또는 3개 가져갈 수 있음
# 상근이 먼저 시작, 마지막 돌 가져가는 사람이 승리
# N이 홀수면 상근 승리, 짝수면 창영 승리

n = int(input())
print("SK" if n % 2 == 1 else "CY")
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        long n = Long.parseLong(br.readLine().trim());

        // N이 홀수면 상근 승리, 짝수면 창영 승리
        System.out.println(n % 2 == 1 ? "SK" : "CY");
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

    long long n;
    cin >> n;

    // N이 홀수면 상근 승리, 짝수면 창영 승리
    cout << (n % 2 == 1 ? "SK" : "CY") << endl;

    return 0;
}
'''
        }
    ],

    # 1212: baekjoon_28325 - 개미굴 (원형 배치, 최대 개미 수)
    1212: [
        {
            "language": "python",
            "code": '''import sys
input = sys.stdin.readline

# 개미굴: 원형으로 N개의 방, 각 방에 C[i]개의 쪽방
# 인접한 곳에 동시에 개미가 살 수 없음
# 최대 개미 수

def solve():
    N = int(input())
    C = list(map(int, input().split()))

    # 특수 케이스: N == 1
    if N == 1:
        # 방에 개미 1마리 또는 쪽방에 C[0]마리
        print(max(1, C[0]))
        return

    # 쪽방이 있는 방의 경우:
    # - 방에 개미가 살면 쪽방 사용 불가 (이득: 1)
    # - 방에 개미가 안 살면 쪽방 모두 사용 가능 (이득: C[i])
    # 따라서 C[i] >= 1이면 쪽방 선택이 유리

    # C[i] == 0인 방만 고려 (빈 방)
    # 빈 방들 사이에서 원형으로 최대 독립 집합

    # 전략:
    # C[i] > 0이면 무조건 쪽방에 C[i]마리 배치 (방은 비움)
    # C[i] == 0인 연속 구간에서 교대로 배치

    total = sum(C)  # 모든 쪽방의 개미 수

    # C[i] == 0인 연속 구간 찾기
    # 원형이므로 시작점을 C[i] > 0인 곳으로 잡음

    # 모든 C[i] == 0인 경우
    if total == 0:
        # 원형 배치: N개 중 최대 N//2개
        print(N // 2)
        return

    # C[i] > 0인 곳이 있음
    # 연속된 0 구간의 길이에 따라 추가
    # 구간 길이 L에서 추가 가능한 개미 수: (L + 1) // 2

    # 시작점 찾기: C[i] > 0인 인덱스
    start = -1
    for i in range(N):
        if C[i] > 0:
            start = i
            break

    # start부터 시작하여 연속된 0 구간 찾기
    i = start
    count = 0
    while True:
        # C[i] > 0인 곳 찾기
        while C[i] == 0:
            i = (i + 1) % N

        # 0 구간 시작
        j = (i + 1) % N
        length = 0
        while C[j] == 0:
            length += 1
            j = (j + 1) % N

        # 구간 길이 length에서 추가 가능한 개미 수
        count += (length + 1) // 2

        i = j
        if i == start:
            break

    print(total + count)

solve()
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());
        long[] C = new long[N];
        StringTokenizer st = new StringTokenizer(br.readLine());
        long total = 0;

        for (int i = 0; i < N; i++) {
            C[i] = Long.parseLong(st.nextToken());
            total += C[i];
        }

        // 특수 케이스: N == 1
        if (N == 1) {
            System.out.println(Math.max(1, C[0]));
            return;
        }

        // 모든 C[i] == 0인 경우
        if (total == 0) {
            System.out.println(N / 2);
            return;
        }

        // C[i] > 0인 곳이 있음
        // 연속된 0 구간의 길이에 따라 추가

        int start = -1;
        for (int i = 0; i < N; i++) {
            if (C[i] > 0) {
                start = i;
                break;
            }
        }

        int i = start;
        long count = 0;

        do {
            // C[i] > 0인 곳 찾기
            while (C[i] == 0) {
                i = (i + 1) % N;
            }

            // 0 구간 시작
            int j = (i + 1) % N;
            int length = 0;
            while (C[j] == 0) {
                length++;
                j = (j + 1) % N;
            }

            // 구간 길이 length에서 추가 가능한 개미 수
            count += (length + 1) / 2;

            i = j;
        } while (i != start);

        System.out.println(total + count);
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
    cin >> N;

    vector<long long> C(N);
    long long total = 0;

    for (int i = 0; i < N; i++) {
        cin >> C[i];
        total += C[i];
    }

    // 특수 케이스: N == 1
    if (N == 1) {
        cout << max(1LL, C[0]) << endl;
        return 0;
    }

    // 모든 C[i] == 0인 경우
    if (total == 0) {
        cout << N / 2 << endl;
        return 0;
    }

    // C[i] > 0인 곳이 있음
    int start = -1;
    for (int i = 0; i < N; i++) {
        if (C[i] > 0) {
            start = i;
            break;
        }
    }

    int i = start;
    long long count = 0;

    do {
        // C[i] > 0인 곳 찾기
        while (C[i] == 0) {
            i = (i + 1) % N;
        }

        // 0 구간 시작
        int j = (i + 1) % N;
        int length = 0;
        while (C[j] == 0) {
            length++;
            j = (j + 1) % N;
        }

        // 구간 길이 length에서 추가 가능한 개미 수
        count += (length + 1) / 2;

        i = j;
    } while (i != start);

    cout << total + count << endl;

    return 0;
}
'''
        }
    ]
}

def main():
    # 메인 파일 로드
    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        problems = json.load(f)

    # 각 인덱스에 솔루션 저장
    for idx, solutions in solutions_data.items():
        if idx < len(problems):
            # 기존 솔루션이 있으면 유지하면서 없는 언어만 추가
            existing = {s['language']: s for s in problems[idx].get('solutions', [])}
            for sol in solutions:
                if sol['language'] not in existing:
                    if 'solutions' not in problems[idx]:
                        problems[idx]['solutions'] = []
                    problems[idx]['solutions'].append(sol)
                    existing[sol['language']] = sol
            print(f"Index {idx} ({problems[idx]['id']}): {len(problems[idx]['solutions'])} solutions")

    # 파일 저장
    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)

    print(f"\n저장 완료: {MAIN_FILE}")

if __name__ == "__main__":
    main()
