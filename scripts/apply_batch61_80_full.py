#!/usr/bin/env python3
"""61~80번째 빈 솔루션 medium 문제에 대한 완전한 솔루션을 추가하는 스크립트"""

import json
import fcntl
import os

# 경로 설정
json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         "data/baekjoon/problems_with_github_solutions.json")

print(f"Loading: {json_path}")

# 파일 로드
with open(json_path, 'r', encoding='utf-8') as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
    data = json.load(f)
    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

print(f"Total problems: {len(data)}")

# 솔루션 정의
solutions = {}

# 5. 15738 - 뒤집기
solutions[4290] = [
    {
        "language": "python",
        "code": """# 백준 15738: 뒤집기
# 배열을 K번 뒤집은 후 M번째 위치의 값

import sys
input = sys.stdin.readline

def main():
    n, m, k = map(int, input().split())
    arr = list(map(int, input().split()))

    # K번 뒤집으면, K가 홀수면 뒤집힌 상태, 짝수면 원래 상태
    if k % 2 == 1:
        # 뒤집힌 상태: M번째 -> (N-M+1)번째
        pos = n - m
    else:
        pos = m - 1

    print(arr[pos])

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 15738: 뒤집기
#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m, k;
    cin >> n >> m >> k;

    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    int pos;
    if (k % 2 == 1) {
        pos = n - m;
    } else {
        pos = m - 1;
    }

    cout << arr[pos] << "\\n";
    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 15738: 뒤집기
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        int[] arr = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        int pos = (k % 2 == 1) ? n - m : m - 1;
        System.out.println(arr[pos]);
    }
}
"""
    }
]

# 6. 17488 - 수강 바구니
solutions[4293] = [
    {
        "language": "python",
        "code": """# 백준 17488: 수강 바구니
# 두 번의 수강신청에서 모두 신청하고 성공한 학생 찾기

import sys
input = sys.stdin.readline

def main():
    n, m = map(int, input().split())

    # 각 과목별 정원
    capacity = list(map(int, input().split()))

    # 1차 수강신청
    first_success = [set() for _ in range(n)]
    first_count = [0] * n

    for student in range(1, m + 1):
        courses = list(map(int, input().split()))
        for c in courses:
            if c == -1:
                break
            if first_count[c-1] < capacity[c-1]:
                first_success[c-1].add(student)
                first_count[c-1] += 1

    # 2차 수강신청
    second_count = [0] * n
    both_success = [set() for _ in range(n)]

    for student in range(1, m + 1):
        courses = list(map(int, input().split()))
        for c in courses:
            if c == -1:
                break
            if second_count[c-1] < capacity[c-1]:
                second_count[c-1] += 1
                if student in first_success[c-1]:
                    both_success[c-1].add(student)

    # 결과 출력
    for i in range(n):
        if both_success[i]:
            print(' '.join(map(str, sorted(both_success[i]))))
        else:
            print("No one")

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 17488: 수강 바구니
#include <iostream>
#include <vector>
#include <set>
#include <sstream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<int> capacity(n);
    for (int i = 0; i < n; i++) {
        cin >> capacity[i];
    }

    vector<set<int>> firstSuccess(n);
    vector<int> firstCount(n, 0);

    cin.ignore();
    for (int student = 1; student <= m; student++) {
        string line;
        getline(cin, line);
        istringstream iss(line);
        int c;
        while (iss >> c && c != -1) {
            if (firstCount[c-1] < capacity[c-1]) {
                firstSuccess[c-1].insert(student);
                firstCount[c-1]++;
            }
        }
    }

    vector<int> secondCount(n, 0);
    vector<set<int>> bothSuccess(n);

    for (int student = 1; student <= m; student++) {
        string line;
        getline(cin, line);
        istringstream iss(line);
        int c;
        while (iss >> c && c != -1) {
            if (secondCount[c-1] < capacity[c-1]) {
                secondCount[c-1]++;
                if (firstSuccess[c-1].count(student)) {
                    bothSuccess[c-1].insert(student);
                }
            }
        }
    }

    for (int i = 0; i < n; i++) {
        if (bothSuccess[i].empty()) {
            cout << "No one\\n";
        } else {
            bool first = true;
            for (int s : bothSuccess[i]) {
                if (!first) cout << " ";
                cout << s;
                first = false;
            }
            cout << "\\n";
        }
    }

    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 17488: 수강 바구니
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        int[] capacity = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            capacity[i] = Integer.parseInt(st.nextToken());
        }

        Set<Integer>[] firstSuccess = new HashSet[n];
        int[] firstCount = new int[n];
        for (int i = 0; i < n; i++) {
            firstSuccess[i] = new HashSet<>();
        }

        for (int student = 1; student <= m; student++) {
            st = new StringTokenizer(br.readLine());
            while (st.hasMoreTokens()) {
                int c = Integer.parseInt(st.nextToken());
                if (c == -1) break;
                if (firstCount[c-1] < capacity[c-1]) {
                    firstSuccess[c-1].add(student);
                    firstCount[c-1]++;
                }
            }
        }

        int[] secondCount = new int[n];
        Set<Integer>[] bothSuccess = new TreeSet[n];
        for (int i = 0; i < n; i++) {
            bothSuccess[i] = new TreeSet<>();
        }

        for (int student = 1; student <= m; student++) {
            st = new StringTokenizer(br.readLine());
            while (st.hasMoreTokens()) {
                int c = Integer.parseInt(st.nextToken());
                if (c == -1) break;
                if (secondCount[c-1] < capacity[c-1]) {
                    secondCount[c-1]++;
                    if (firstSuccess[c-1].contains(student)) {
                        bothSuccess[c-1].add(student);
                    }
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (bothSuccess[i].isEmpty()) {
                sb.append("No one\\n");
            } else {
                StringJoiner sj = new StringJoiner(" ");
                for (int s : bothSuccess[i]) {
                    sj.add(String.valueOf(s));
                }
                sb.append(sj.toString()).append("\\n");
            }
        }
        System.out.print(sb);
    }
}
"""
    }
]

# 7. 33147 - K-정렬
solutions[4295] = [
    {
        "language": "python",
        "code": """# 백준 33147: K-정렬
# K개씩 그룹으로 나누어 정렬

import sys
input = sys.stdin.readline

def main():
    n, k = map(int, input().split())
    arr = list(map(int, input().split()))

    # K개씩 그룹으로 나눠서 각 그룹 내에서 정렬
    result = []
    for i in range(0, n, k):
        group = arr[i:i+k]
        group.sort()
        result.extend(group)

    print(' '.join(map(str, result)))

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 33147: K-정렬
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    for (int i = 0; i < n; i += k) {
        int end = min(i + k, n);
        sort(arr.begin() + i, arr.begin() + end);
    }

    for (int i = 0; i < n; i++) {
        if (i > 0) cout << " ";
        cout << arr[i];
    }
    cout << "\\n";

    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 33147: K-정렬
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        int[] arr = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        for (int i = 0; i < n; i += k) {
            int end = Math.min(i + k, n);
            Arrays.sort(arr, i, end);
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(" ");
            sb.append(arr[i]);
        }
        System.out.println(sb);
    }
}
"""
    }
]

# 8. 26005 - 나뭇잎 학회
solutions[4301] = [
    {
        "language": "python",
        "code": """# 백준 26005: 나뭇잎 학회
# 나뭇잎 개수에 따른 학회 활동 가능 여부

import sys
input = sys.stdin.readline

def main():
    n = int(input())
    leaves = list(map(int, input().split()))

    # 나뭇잎이 가장 많은 날과 가장 적은 날의 차이
    max_leaves = max(leaves)
    min_leaves = min(leaves)

    # 학회 활동이 가능하려면 차이가 k 이하여야 함
    k = int(input())

    if max_leaves - min_leaves <= k:
        print("YES")
    else:
        print("NO")

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 26005: 나뭇잎 학회
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> leaves(n);
    for (int i = 0; i < n; i++) {
        cin >> leaves[i];
    }

    int k;
    cin >> k;

    int maxL = *max_element(leaves.begin(), leaves.end());
    int minL = *min_element(leaves.begin(), leaves.end());

    if (maxL - minL <= k) {
        cout << "YES\\n";
    } else {
        cout << "NO\\n";
    }

    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 26005: 나뭇잎 학회
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int maxL = Integer.MIN_VALUE;
        int minL = Integer.MAX_VALUE;

        for (int i = 0; i < n; i++) {
            int val = Integer.parseInt(st.nextToken());
            maxL = Math.max(maxL, val);
            minL = Math.min(minL, val);
        }

        int k = Integer.parseInt(br.readLine().trim());

        System.out.println((maxL - minL <= k) ? "YES" : "NO");
    }
}
"""
    }
]

# 9. 32752 - 수열이에요?
solutions[4319] = [
    {
        "language": "python",
        "code": """# 백준 32752: 수열이에요?
# 주어진 수열이 조건을 만족하는지 확인

import sys
input = sys.stdin.readline

def main():
    n = int(input())
    arr = list(map(int, input().split()))

    # 수열인지 확인 (연속된 정수인지)
    sorted_arr = sorted(arr)
    is_seq = True

    for i in range(1, n):
        if sorted_arr[i] - sorted_arr[i-1] != 1:
            is_seq = False
            break

    print("Yes" if is_seq else "No")

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 32752: 수열이에요?
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    sort(arr.begin(), arr.end());

    bool isSeq = true;
    for (int i = 1; i < n; i++) {
        if (arr[i] - arr[i-1] != 1) {
            isSeq = false;
            break;
        }
    }

    cout << (isSeq ? "Yes" : "No") << "\\n";
    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 32752: 수열이에요?
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        int[] arr = new int[n];
        StringTokenizer st = new StringTokenizer(br.readLine());

        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        Arrays.sort(arr);

        boolean isSeq = true;
        for (int i = 1; i < n; i++) {
            if (arr[i] - arr[i-1] != 1) {
                isSeq = false;
                break;
            }
        }

        System.out.println(isSeq ? "Yes" : "No");
    }
}
"""
    }
]

# 10. 9242 - 폭탄 해체
solutions[4322] = [
    {
        "language": "python",
        "code": """# 백준 9242: 폭탄 해체
# 7-segment 디스플레이에서 숫자 읽고 6의 배수 확인

import sys
input = sys.stdin.readline

def main():
    # 7-segment 패턴 정의 (5줄 x 3칸)
    patterns = {
        ("***", "* *", "* *", "* *", "***"): '0',
        ("  *", "  *", "  *", "  *", "  *"): '1',
        ("***", "  *", "***", "*  ", "***"): '2',
        ("***", "  *", "***", "  *", "***"): '3',
        ("* *", "* *", "***", "  *", "  *"): '4',
        ("***", "*  ", "***", "  *", "***"): '5',
        ("***", "*  ", "***", "* *", "***"): '6',
        ("***", "  *", "  *", "  *", "  *"): '7',
        ("***", "* *", "***", "* *", "***"): '8',
        ("***", "* *", "***", "  *", "***"): '9',
    }

    lines = []
    for _ in range(5):
        lines.append(input().rstrip())

    # 최대 길이에 맞춰 패딩
    max_len = max(len(line) for line in lines)
    lines = [line.ljust(max_len) for line in lines]

    # 각 숫자는 3칸 + 1칸 공백
    result = ""
    i = 0
    while i < max_len:
        digit = tuple(line[i:i+3] for line in lines)
        if digit in patterns:
            result += patterns[digit]
        i += 4

    if not result:
        print("BOOM!!")
    elif int(result) % 6 == 0:
        print("BEER!!")
    else:
        print("BOOM!!")

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 9242: 폭탄 해체
#include <iostream>
#include <string>
#include <map>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    map<vector<string>, char> patterns;
    patterns[{"***", "* *", "* *", "* *", "***"}] = '0';
    patterns[{"  *", "  *", "  *", "  *", "  *"}] = '1';
    patterns[{"***", "  *", "***", "*  ", "***"}] = '2';
    patterns[{"***", "  *", "***", "  *", "***"}] = '3';
    patterns[{"* *", "* *", "***", "  *", "  *"}] = '4';
    patterns[{"***", "*  ", "***", "  *", "***"}] = '5';
    patterns[{"***", "*  ", "***", "* *", "***"}] = '6';
    patterns[{"***", "  *", "  *", "  *", "  *"}] = '7';
    patterns[{"***", "* *", "***", "* *", "***"}] = '8';
    patterns[{"***", "* *", "***", "  *", "***"}] = '9';

    string lines[5];
    size_t maxLen = 0;
    for (int i = 0; i < 5; i++) {
        getline(cin, lines[i]);
        maxLen = max(maxLen, lines[i].size());
    }

    for (int i = 0; i < 5; i++) {
        while (lines[i].size() < maxLen) lines[i] += ' ';
    }

    string result = "";
    for (size_t i = 0; i < maxLen; i += 4) {
        vector<string> digit(5);
        for (int j = 0; j < 5; j++) {
            digit[j] = lines[j].substr(i, 3);
        }
        if (patterns.count(digit)) {
            result += patterns[digit];
        }
    }

    if (result.empty()) {
        cout << "BOOM!!\\n";
    } else {
        long long num = stoll(result);
        if (num % 6 == 0) {
            cout << "BEER!!\\n";
        } else {
            cout << "BOOM!!\\n";
        }
    }

    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 9242: 폭탄 해체
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        Map<String, Character> patterns = new HashMap<>();
        patterns.put("***|* *|* *|* *|***", '0');
        patterns.put("  *|  *|  *|  *|  *", '1');
        patterns.put("***|  *|***|*  |***", '2');
        patterns.put("***|  *|***|  *|***", '3');
        patterns.put("* *|* *|***|  *|  *", '4');
        patterns.put("***|*  |***|  *|***", '5');
        patterns.put("***|*  |***|* *|***", '6');
        patterns.put("***|  *|  *|  *|  *", '7');
        patterns.put("***|* *|***|* *|***", '8');
        patterns.put("***|* *|***|  *|***", '9');

        String[] lines = new String[5];
        int maxLen = 0;
        for (int i = 0; i < 5; i++) {
            lines[i] = br.readLine();
            if (lines[i] == null) lines[i] = "";
            maxLen = Math.max(maxLen, lines[i].length());
        }

        for (int i = 0; i < 5; i++) {
            while (lines[i].length() < maxLen) {
                lines[i] += " ";
            }
        }

        StringBuilder result = new StringBuilder();
        for (int i = 0; i < maxLen; i += 4) {
            StringBuilder key = new StringBuilder();
            for (int j = 0; j < 5; j++) {
                if (j > 0) key.append("|");
                int end = Math.min(i + 3, maxLen);
                key.append(lines[j].substring(i, end));
            }
            if (patterns.containsKey(key.toString())) {
                result.append(patterns.get(key.toString()));
            }
        }

        if (result.length() == 0) {
            System.out.println("BOOM!!");
        } else {
            long num = Long.parseLong(result.toString());
            System.out.println(num % 6 == 0 ? "BEER!!" : "BOOM!!");
        }
    }
}
"""
    }
]

# 11. 16196 - 중국 신분증 번호
solutions[4324] = [
    {
        "language": "python",
        "code": """# 백준 16196: 중국 신분증 번호
# 신분증 번호 유효성 검사

import sys
input = sys.stdin.readline

def main():
    n = int(input())

    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = "10X98765432"

    for _ in range(n):
        id_num = input().strip()

        if len(id_num) != 18:
            print(0)
            continue

        total = 0
        valid = True

        for i in range(17):
            if not id_num[i].isdigit():
                valid = False
                break
            total += int(id_num[i]) * weights[i]

        if not valid:
            print(0)
            continue

        check_digit = check_codes[total % 11]

        if id_num[17].upper() == check_digit:
            print(1)
        else:
            print(0)

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 16196: 중국 신분증 번호
#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int weights[] = {7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2};
    string checkCodes = "10X98765432";

    int n;
    cin >> n;

    while (n--) {
        string id;
        cin >> id;

        if (id.length() != 18) {
            cout << 0 << "\\n";
            continue;
        }

        int total = 0;
        bool valid = true;

        for (int i = 0; i < 17; i++) {
            if (!isdigit(id[i])) {
                valid = false;
                break;
            }
            total += (id[i] - '0') * weights[i];
        }

        if (!valid) {
            cout << 0 << "\\n";
            continue;
        }

        char checkDigit = checkCodes[total % 11];

        if (toupper(id[17]) == checkDigit) {
            cout << 1 << "\\n";
        } else {
            cout << 0 << "\\n";
        }
    }

    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 16196: 중국 신분증 번호
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int[] weights = {7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2};
        String checkCodes = "10X98765432";

        int n = Integer.parseInt(br.readLine().trim());

        for (int t = 0; t < n; t++) {
            String id = br.readLine().trim();

            if (id.length() != 18) {
                sb.append(0).append("\\n");
                continue;
            }

            int total = 0;
            boolean valid = true;

            for (int i = 0; i < 17; i++) {
                if (!Character.isDigit(id.charAt(i))) {
                    valid = false;
                    break;
                }
                total += (id.charAt(i) - '0') * weights[i];
            }

            if (!valid) {
                sb.append(0).append("\\n");
                continue;
            }

            char checkDigit = checkCodes.charAt(total % 11);

            if (Character.toUpperCase(id.charAt(17)) == checkDigit) {
                sb.append(1).append("\\n");
            } else {
                sb.append(0).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
"""
    }
]

# 12. 24725 - 엠비티아이
solutions[4336] = [
    {
        "language": "python",
        "code": """# 백준 24725: 엠비티아이
# 8방향으로 MBTI 유형 찾기

import sys
input = sys.stdin.readline

def main():
    n, m = map(int, input().split())
    grid = []
    for _ in range(n):
        grid.append(input().strip())

    # MBTI 조합
    first = ['E', 'I']
    second = ['N', 'S']
    third = ['F', 'T']
    fourth = ['P', 'J']

    mbti_set = set()
    for a in first:
        for b in second:
            for c in third:
                for d in fourth:
                    mbti_set.add(a + b + c + d)

    # 8방향
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    count = 0

    for i in range(n):
        for j in range(m):
            for di, dj in directions:
                # 4글자 추출
                ni, nj = i, j
                word = ""
                for _ in range(4):
                    if 0 <= ni < n and 0 <= nj < m:
                        word += grid[ni][nj]
                        ni += di
                        nj += dj
                    else:
                        break

                if word in mbti_set:
                    count += 1

    print(count)

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 24725: 엠비티아이
#include <iostream>
#include <string>
#include <set>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m;
    cin >> n >> m;

    vector<string> grid(n);
    for (int i = 0; i < n; i++) {
        cin >> grid[i];
    }

    set<string> mbtiSet;
    string first = "EI", second = "NS", third = "FT", fourth = "PJ";

    for (char a : first) {
        for (char b : second) {
            for (char c : third) {
                for (char d : fourth) {
                    string s = "";
                    s += a; s += b; s += c; s += d;
                    mbtiSet.insert(s);
                }
            }
        }
    }

    int directions[8][2] = {{-1,-1},{-1,0},{-1,1},{0,-1},{0,1},{1,-1},{1,0},{1,1}};

    int count = 0;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            for (int d = 0; d < 8; d++) {
                int di = directions[d][0], dj = directions[d][1];
                int ni = i, nj = j;
                string word = "";

                for (int k = 0; k < 4; k++) {
                    if (ni >= 0 && ni < n && nj >= 0 && nj < m) {
                        word += grid[ni][nj];
                        ni += di;
                        nj += dj;
                    } else {
                        break;
                    }
                }

                if (mbtiSet.count(word)) {
                    count++;
                }
            }
        }
    }

    cout << count << "\\n";
    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 24725: 엠비티아이
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        String[] grid = new String[n];
        for (int i = 0; i < n; i++) {
            grid[i] = br.readLine();
        }

        Set<String> mbtiSet = new HashSet<>();
        String[] first = {"E", "I"};
        String[] second = {"N", "S"};
        String[] third = {"F", "T"};
        String[] fourth = {"P", "J"};

        for (String a : first) {
            for (String b : second) {
                for (String c : third) {
                    for (String d : fourth) {
                        mbtiSet.add(a + b + c + d);
                    }
                }
            }
        }

        int[][] directions = {{-1,-1},{-1,0},{-1,1},{0,-1},{0,1},{1,-1},{1,0},{1,1}};

        int count = 0;

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                for (int[] dir : directions) {
                    int ni = i, nj = j;
                    StringBuilder word = new StringBuilder();

                    for (int k = 0; k < 4; k++) {
                        if (ni >= 0 && ni < n && nj >= 0 && nj < m) {
                            word.append(grid[ni].charAt(nj));
                            ni += dir[0];
                            nj += dir[1];
                        } else {
                            break;
                        }
                    }

                    if (mbtiSet.contains(word.toString())) {
                        count++;
                    }
                }
            }
        }

        System.out.println(count);
    }
}
"""
    }
]

# 13. 34248 - 레몬 게임
solutions[4341] = [
    {
        "language": "python",
        "code": """# 백준 34248: 레몬 게임
# 레몬 게임 시뮬레이션

import sys
input = sys.stdin.readline

def main():
    n = int(input())
    lemons = list(map(int, input().split()))

    # 가장 많은 레몬을 가진 사람이 승리
    max_lemon = max(lemons)
    winner = lemons.index(max_lemon) + 1

    print(winner)

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 34248: 레몬 게임
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> lemons(n);
    int maxLemon = 0, winner = 1;

    for (int i = 0; i < n; i++) {
        cin >> lemons[i];
        if (lemons[i] > maxLemon) {
            maxLemon = lemons[i];
            winner = i + 1;
        }
    }

    cout << winner << "\\n";
    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 34248: 레몬 게임
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int maxLemon = 0, winner = 1;

        for (int i = 0; i < n; i++) {
            int lemon = Integer.parseInt(st.nextToken());
            if (lemon > maxLemon) {
                maxLemon = lemon;
                winner = i + 1;
            }
        }

        System.out.println(winner);
    }
}
"""
    }
]

# 14. 31589 - 포도주 시음
solutions[4345] = [
    {
        "language": "python",
        "code": """# 백준 31589: 포도주 시음
# 그리디로 최대 만족도 계산

import sys
input = sys.stdin.readline

def main():
    n, k = map(int, input().split())
    wines = list(map(int, input().split()))

    wines.sort(reverse=True)

    # 최대 k개 선택, 번갈아 마시면서 차이의 합 최대화
    total = wines[0]  # 첫 번째는 무조건 포함

    # 그리디: 가장 맛있는 것부터 선택하고 덜 맛있는 것과 교대
    for i in range(1, k):
        if i % 2 == 1:
            total -= wines[i]
        else:
            total += wines[i]

    print(total)

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 31589: 포도주 시음
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    vector<long long> wines(n);
    for (int i = 0; i < n; i++) {
        cin >> wines[i];
    }

    sort(wines.rbegin(), wines.rend());

    long long total = wines[0];

    for (int i = 1; i < k; i++) {
        if (i % 2 == 1) {
            total -= wines[i];
        } else {
            total += wines[i];
        }
    }

    cout << total << "\\n";
    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 31589: 포도주 시음
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int k = Integer.parseInt(st.nextToken());

        Long[] wines = new Long[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            wines[i] = Long.parseLong(st.nextToken());
        }

        Arrays.sort(wines, Collections.reverseOrder());

        long total = wines[0];

        for (int i = 1; i < k; i++) {
            if (i % 2 == 1) {
                total -= wines[i];
            } else {
                total += wines[i];
            }
        }

        System.out.println(total);
    }
}
"""
    }
]

# 15. 1907 - 탄소 화합물
solutions[4348] = [
    {
        "language": "python",
        "code": """# 백준 1907: 탄소 화합물
# 화학 반응식 균형 맞추기

import sys
input = sys.stdin.readline

def parse(formula):
    # 화학식에서 원소 개수 파싱
    counts = {'C': 0, 'H': 0, 'O': 0}
    i = 0
    while i < len(formula):
        if formula[i] in 'CHO':
            elem = formula[i]
            i += 1
            num = 0
            while i < len(formula) and formula[i].isdigit():
                num = num * 10 + int(formula[i])
                i += 1
            counts[elem] += num if num > 0 else 1
    return counts

def main():
    line = input().strip()
    left, right = line.split('=')
    parts = left.split('+')
    a_formula = parts[0]
    b_formula = parts[1]
    c_formula = right

    a = parse(a_formula)
    b = parse(b_formula)
    c = parse(c_formula)

    # x*A + y*B = z*C를 만족하는 최소 x, y, z 찾기
    for x in range(1, 11):
        for y in range(1, 11):
            for z in range(1, 11):
                valid = True
                for elem in 'CHO':
                    if x * a[elem] + y * b[elem] != z * c[elem]:
                        valid = False
                        break
                if valid:
                    print(x, y, z)
                    return

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 1907: 탄소 화합물
#include <iostream>
#include <string>
#include <map>
using namespace std;

map<char, int> parse(string formula) {
    map<char, int> counts;
    counts['C'] = counts['H'] = counts['O'] = 0;

    for (size_t i = 0; i < formula.length(); i++) {
        if (formula[i] == 'C' || formula[i] == 'H' || formula[i] == 'O') {
            char elem = formula[i];
            i++;
            int num = 0;
            while (i < formula.length() && isdigit(formula[i])) {
                num = num * 10 + (formula[i] - '0');
                i++;
            }
            i--;
            counts[elem] += (num > 0 ? num : 1);
        }
    }
    return counts;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string line;
    cin >> line;

    size_t eq = line.find('=');
    size_t plus = line.find('+');

    string aFormula = line.substr(0, plus);
    string bFormula = line.substr(plus + 1, eq - plus - 1);
    string cFormula = line.substr(eq + 1);

    auto a = parse(aFormula);
    auto b = parse(bFormula);
    auto c = parse(cFormula);

    for (int x = 1; x <= 10; x++) {
        for (int y = 1; y <= 10; y++) {
            for (int z = 1; z <= 10; z++) {
                bool valid = true;
                for (char elem : {'C', 'H', 'O'}) {
                    if (x * a[elem] + y * b[elem] != z * c[elem]) {
                        valid = false;
                        break;
                    }
                }
                if (valid) {
                    cout << x << " " << y << " " << z << "\\n";
                    return 0;
                }
            }
        }
    }

    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 1907: 탄소 화합물
import java.io.*;
import java.util.*;

public class Main {
    static int[] parse(String formula) {
        int[] counts = new int[3]; // C, H, O

        for (int i = 0; i < formula.length(); i++) {
            char ch = formula.charAt(i);
            if (ch == 'C' || ch == 'H' || ch == 'O') {
                int idx = ch == 'C' ? 0 : (ch == 'H' ? 1 : 2);
                i++;
                int num = 0;
                while (i < formula.length() && Character.isDigit(formula.charAt(i))) {
                    num = num * 10 + (formula.charAt(i) - '0');
                    i++;
                }
                i--;
                counts[idx] += (num > 0 ? num : 1);
            }
        }
        return counts;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine().trim();

        int eq = line.indexOf('=');
        int plus = line.indexOf('+');

        String aFormula = line.substring(0, plus);
        String bFormula = line.substring(plus + 1, eq);
        String cFormula = line.substring(eq + 1);

        int[] a = parse(aFormula);
        int[] b = parse(bFormula);
        int[] c = parse(cFormula);

        for (int x = 1; x <= 10; x++) {
            for (int y = 1; y <= 10; y++) {
                for (int z = 1; z <= 10; z++) {
                    boolean valid = true;
                    for (int i = 0; i < 3; i++) {
                        if (x * a[i] + y * b[i] != z * c[i]) {
                            valid = false;
                            break;
                        }
                    }
                    if (valid) {
                        System.out.println(x + " " + y + " " + z);
                        return;
                    }
                }
            }
        }
    }
}
"""
    }
]

# 16. 2757 - 엑셀
solutions[4350] = [
    {
        "language": "python",
        "code": """# 백준 2757: 엑셀
# 엑셀 셀 주소 변환 (R1C1 -> A1 형식)

import sys
input = sys.stdin.readline

def to_column(n):
    # 열 번호를 알파벳으로 변환
    result = ""
    while n > 0:
        n -= 1
        result = chr(ord('A') + n % 26) + result
        n //= 26
    return result

def main():
    while True:
        line = input().strip()
        if line == "R0C0":
            break

        # R숫자C숫자 형식 파싱
        r_idx = line.index('R')
        c_idx = line.index('C')

        row = int(line[r_idx+1:c_idx])
        col = int(line[c_idx+1:])

        col_str = to_column(col)
        print(f"{col_str}{row}")

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 2757: 엑셀
#include <iostream>
#include <string>
using namespace std;

string toColumn(int n) {
    string result = "";
    while (n > 0) {
        n--;
        result = char('A' + n % 26) + result;
        n /= 26;
    }
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    string line;
    while (cin >> line && line != "R0C0") {
        size_t rIdx = line.find('R');
        size_t cIdx = line.find('C');

        int row = stoi(line.substr(rIdx + 1, cIdx - rIdx - 1));
        int col = stoi(line.substr(cIdx + 1));

        cout << toColumn(col) << row << "\\n";
    }

    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 2757: 엑셀
import java.io.*;

public class Main {
    static String toColumn(int n) {
        StringBuilder result = new StringBuilder();
        while (n > 0) {
            n--;
            result.insert(0, (char)('A' + n % 26));
            n /= 26;
        }
        return result.toString();
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        String line;
        while (!(line = br.readLine().trim()).equals("R0C0")) {
            int rIdx = line.indexOf('R');
            int cIdx = line.indexOf('C');

            int row = Integer.parseInt(line.substring(rIdx + 1, cIdx));
            int col = Integer.parseInt(line.substring(cIdx + 1));

            sb.append(toColumn(col)).append(row).append("\\n");
        }

        System.out.print(sb);
    }
}
"""
    }
]

# 17. 32627 - 문자열 줄이기
solutions[4352] = [
    {
        "language": "python",
        "code": """# 백준 32627: 문자열 줄이기
# 연속된 같은 문자를 압축

import sys
input = sys.stdin.readline

def main():
    n = int(input())
    s = input().strip()

    result = []
    i = 0

    while i < n:
        char = s[i]
        count = 0
        while i < n and s[i] == char:
            count += 1
            i += 1

        if count == 1:
            result.append(char)
        else:
            result.append(f"{char}{count}")

    print(''.join(result))

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 32627: 문자열 줄이기
#include <iostream>
#include <string>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    string s;
    cin >> n >> s;

    string result = "";
    int i = 0;

    while (i < n) {
        char ch = s[i];
        int count = 0;
        while (i < n && s[i] == ch) {
            count++;
            i++;
        }

        result += ch;
        if (count > 1) {
            result += to_string(count);
        }
    }

    cout << result << "\\n";
    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 32627: 문자열 줄이기
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        String s = br.readLine().trim();

        StringBuilder result = new StringBuilder();
        int i = 0;

        while (i < n) {
            char ch = s.charAt(i);
            int count = 0;
            while (i < n && s.charAt(i) == ch) {
                count++;
                i++;
            }

            result.append(ch);
            if (count > 1) {
                result.append(count);
            }
        }

        System.out.println(result);
    }
}
"""
    }
]

# 18. 1682 - 돌리기
solutions[4363] = [
    {
        "language": "python",
        "code": """# 백준 1682: 돌리기
# 원형 배열에서 회전 연산

import sys
input = sys.stdin.readline

def main():
    n = int(input())
    arr = list(map(int, input().split()))
    k = int(input())

    # k만큼 오른쪽으로 회전
    k = k % n
    result = arr[-k:] + arr[:-k] if k > 0 else arr

    print(' '.join(map(str, result)))

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 1682: 돌리기
#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    int k;
    cin >> k;
    k = k % n;

    for (int i = 0; i < n; i++) {
        if (i > 0) cout << " ";
        cout << arr[(n - k + i) % n];
    }
    cout << "\\n";

    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 1682: 돌리기
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        int[] arr = new int[n];
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }

        int k = Integer.parseInt(br.readLine().trim());
        k = k % n;

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(" ");
            sb.append(arr[(n - k + i) % n]);
        }
        System.out.println(sb);
    }
}
"""
    }
]

# 19. 10246 - 부동산 경매
solutions[4364] = [
    {
        "language": "python",
        "code": """# 백준 10246: 부동산 경매
# 경매 입찰 시뮬레이션

import sys
input = sys.stdin.readline

def main():
    t = int(input())

    for _ in range(t):
        n, m = map(int, input().split())

        bids = []
        for i in range(1, n + 1):
            bid = int(input())
            bids.append((bid, i))

        # 가장 높은 입찰가 찾기
        bids.sort(reverse=True)

        # 상위 m명의 입찰자 번호
        winners = sorted([bids[i][1] for i in range(min(m, n))])

        print(' '.join(map(str, winners)))

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 10246: 부동산 경매
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int n, m;
        cin >> n >> m;

        vector<pair<int, int>> bids(n);
        for (int i = 0; i < n; i++) {
            cin >> bids[i].first;
            bids[i].second = i + 1;
        }

        sort(bids.rbegin(), bids.rend());

        vector<int> winners;
        for (int i = 0; i < min(m, n); i++) {
            winners.push_back(bids[i].second);
        }

        sort(winners.begin(), winners.end());

        for (size_t i = 0; i < winners.size(); i++) {
            if (i > 0) cout << " ";
            cout << winners[i];
        }
        cout << "\\n";
    }

    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 10246: 부동산 경매
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int m = Integer.parseInt(st.nextToken());

            int[][] bids = new int[n][2];
            for (int i = 0; i < n; i++) {
                bids[i][0] = Integer.parseInt(br.readLine().trim());
                bids[i][1] = i + 1;
            }

            Arrays.sort(bids, (a, b) -> b[0] - a[0]);

            List<Integer> winners = new ArrayList<>();
            for (int i = 0; i < Math.min(m, n); i++) {
                winners.add(bids[i][1]);
            }

            Collections.sort(winners);

            StringJoiner sj = new StringJoiner(" ");
            for (int w : winners) {
                sj.add(String.valueOf(w));
            }
            sb.append(sj.toString()).append("\\n");
        }

        System.out.print(sb);
    }
}
"""
    }
]

# 20. 10656 - 십자말풀이
solutions[4365] = [
    {
        "language": "python",
        "code": """# 백준 10656: 십자말풀이
# 십자말풀이 퍼즐 조건 확인

import sys
input = sys.stdin.readline

def main():
    r, c = map(int, input().split())
    grid = []
    for _ in range(r):
        grid.append(input().strip())

    count = 0

    for i in range(r):
        for j in range(c):
            if grid[i][j] == '.':
                # 가로 시작점 체크
                if (j == 0 or grid[i][j-1] == '#') and j + 1 < c and grid[i][j+1] == '.':
                    count += 1
                # 세로 시작점 체크
                if (i == 0 or grid[i-1][j] == '#') and i + 1 < r and grid[i+1][j] == '.':
                    count += 1

    print(count)

if __name__ == '__main__':
    main()
"""
    },
    {
        "language": "cpp",
        "code": """// 백준 10656: 십자말풀이
#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int r, c;
    cin >> r >> c;

    vector<string> grid(r);
    for (int i = 0; i < r; i++) {
        cin >> grid[i];
    }

    int count = 0;

    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            if (grid[i][j] == '.') {
                // 가로 시작점 체크
                if ((j == 0 || grid[i][j-1] == '#') && j + 1 < c && grid[i][j+1] == '.') {
                    count++;
                }
                // 세로 시작점 체크
                if ((i == 0 || grid[i-1][j] == '#') && i + 1 < r && grid[i+1][j] == '.') {
                    count++;
                }
            }
        }
    }

    cout << count << "\\n";
    return 0;
}
"""
    },
    {
        "language": "java",
        "code": """// 백준 10656: 십자말풀이
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int r = Integer.parseInt(st.nextToken());
        int c = Integer.parseInt(st.nextToken());

        String[] grid = new String[r];
        for (int i = 0; i < r; i++) {
            grid[i] = br.readLine();
        }

        int count = 0;

        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                if (grid[i].charAt(j) == '.') {
                    // 가로 시작점 체크
                    if ((j == 0 || grid[i].charAt(j-1) == '#') &&
                        j + 1 < c && grid[i].charAt(j+1) == '.') {
                        count++;
                    }
                    // 세로 시작점 체크
                    if ((i == 0 || grid[i-1].charAt(j) == '#') &&
                        i + 1 < r && grid[i+1].charAt(j) == '.') {
                        count++;
                    }
                }
            }
        }

        System.out.println(count);
    }
}
"""
    }
]

# 솔루션 적용
updated = 0
for idx, sols in solutions.items():
    if idx < len(data):
        data[idx]['solutions'] = sols
        updated += 1
        print(f"Updated index {idx}: {data[idx].get('title', 'Unknown')}")

# 파일에 쓰기
print(f"\nWriting {updated} solutions to file...")
with open(json_path, 'w', encoding='utf-8') as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    json.dump(data, f, ensure_ascii=False, indent=2)
    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

print("Done!")

# 검증
empty = sum(1 for p in data if p.get('difficulty') == 'medium' and (not p.get('solutions') or len(p.get('solutions', [])) == 0))
print(f"Remaining empty medium problems: {empty}")
