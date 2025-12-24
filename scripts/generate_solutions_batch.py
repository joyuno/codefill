#!/usr/bin/env python3
"""
백준 문제 솔루션 생성 스크립트
difficulty가 "easy"이고 solutions가 비어있는 문제들에 대해
Python, Java, C++ 솔루션을 생성합니다.
"""

import json

# 솔루션 정의 (문제 ID별)
SOLUTIONS = {
    # 2884: 알람 시계 - 45분 일찍 알람 설정
    "2884": {
        "python": '''# 백준 2884: 알람 시계
# 현재 알람 시각에서 45분을 빼서 새로운 알람 시각을 구한다

H, M = map(int, input().split())

# 45분을 뺀다
M -= 45

# 분이 음수가 되면 시간에서 1을 빼고 분에 60을 더한다
if M < 0:
    M += 60
    H -= 1
    # 시간이 음수가 되면 23시로 설정
    if H < 0:
        H = 23

print(H, M)
''',
        "java": '''import java.util.Scanner;

// 백준 2884: 알람 시계
// 현재 알람 시각에서 45분을 빼서 새로운 알람 시각을 구한다
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int H = sc.nextInt();
        int M = sc.nextInt();

        // 45분을 뺀다
        M -= 45;

        // 분이 음수가 되면 시간에서 1을 빼고 분에 60을 더한다
        if (M < 0) {
            M += 60;
            H -= 1;
            // 시간이 음수가 되면 23시로 설정
            if (H < 0) {
                H = 23;
            }
        }

        System.out.println(H + " " + M);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 2884: 알람 시계
// 현재 알람 시각에서 45분을 빼서 새로운 알람 시각을 구한다
int main() {
    int H, M;
    cin >> H >> M;

    // 45분을 뺀다
    M -= 45;

    // 분이 음수가 되면 시간에서 1을 빼고 분에 60을 더한다
    if (M < 0) {
        M += 60;
        H--;
        // 시간이 음수가 되면 23시로 설정
        if (H < 0) {
            H = 23;
        }
    }

    cout << H << " " << M << endl;
    return 0;
}
'''
    },

    # 2588: 곱셈 - 세 자리 수 곱셈 과정
    "2588": {
        "python": '''# 백준 2588: 곱셈
# (세 자리 수) × (세 자리 수)의 곱셈 과정을 출력한다

A = int(input())
B = int(input())

# B의 각 자릿수와 A를 곱한 결과 출력
print(A * (B % 10))           # (3) 일의 자리
print(A * ((B // 10) % 10))   # (4) 십의 자리
print(A * (B // 100))         # (5) 백의 자리
print(A * B)                   # (6) 최종 결과
''',
        "java": '''import java.util.Scanner;

// 백준 2588: 곱셈
// (세 자리 수) × (세 자리 수)의 곱셈 과정을 출력한다
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int A = sc.nextInt();
        int B = sc.nextInt();

        // B의 각 자릿수와 A를 곱한 결과 출력
        System.out.println(A * (B % 10));           // (3) 일의 자리
        System.out.println(A * ((B / 10) % 10));    // (4) 십의 자리
        System.out.println(A * (B / 100));          // (5) 백의 자리
        System.out.println(A * B);                   // (6) 최종 결과
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 2588: 곱셈
// (세 자리 수) × (세 자리 수)의 곱셈 과정을 출력한다
int main() {
    int A, B;
    cin >> A >> B;

    // B의 각 자릿수와 A를 곱한 결과 출력
    cout << A * (B % 10) << endl;           // (3) 일의 자리
    cout << A * ((B / 10) % 10) << endl;    // (4) 십의 자리
    cout << A * (B / 100) << endl;          // (5) 백의 자리
    cout << A * B << endl;                   // (6) 최종 결과

    return 0;
}
'''
    },

    # 1152: 단어의 개수
    "1152": {
        "python": '''# 백준 1152: 단어의 개수
# 문자열에서 단어의 개수를 센다 (공백으로 구분)

s = input().split()
print(len(s))
''',
        "java": '''import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

// 백준 1152: 단어의 개수
// 문자열에서 단어의 개수를 센다 (공백으로 구분)
public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine();
        StringTokenizer st = new StringTokenizer(s);
        System.out.println(st.countTokens());
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
using namespace std;

// 백준 1152: 단어의 개수
// 문자열에서 단어의 개수를 센다 (공백으로 구분)
int main() {
    string word;
    int count = 0;

    // 공백으로 구분된 단어를 읽어서 개수 센다
    while (cin >> word) {
        count++;
    }

    cout << count << endl;
    return 0;
}
'''
    },

    # 10818: 최소, 최대
    "10818": {
        "python": '''# 백준 10818: 최소, 최대
# N개의 정수 중 최솟값과 최댓값을 구한다

import sys
input = sys.stdin.readline

N = int(input())
nums = list(map(int, input().split()))
print(min(nums), max(nums))
''',
        "java": '''import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

// 백준 10818: 최소, 최대
// N개의 정수 중 최솟값과 최댓값을 구한다
public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine());
        StringTokenizer st = new StringTokenizer(br.readLine());

        int min = Integer.MAX_VALUE;
        int max = Integer.MIN_VALUE;

        for (int i = 0; i < N; i++) {
            int num = Integer.parseInt(st.nextToken());
            if (num < min) min = num;
            if (num > max) max = num;
        }

        System.out.println(min + " " + max);
    }
}
''',
        "cpp": '''#include <iostream>
#include <climits>
using namespace std;

// 백준 10818: 최소, 최대
// N개의 정수 중 최솟값과 최댓값을 구한다
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    int minVal = INT_MAX;
    int maxVal = INT_MIN;

    for (int i = 0; i < N; i++) {
        int num;
        cin >> num;
        if (num < minVal) minVal = num;
        if (num > maxVal) maxVal = num;
    }

    cout << minVal << " " << maxVal << endl;
    return 0;
}
'''
    },

    # 2562: 최댓값
    "2562": {
        "python": '''# 백준 2562: 최댓값
# 9개의 자연수 중 최댓값과 그 위치를 구한다

nums = []
for _ in range(9):
    nums.append(int(input()))

max_val = max(nums)
max_idx = nums.index(max_val) + 1  # 1부터 시작

print(max_val)
print(max_idx)
''',
        "java": '''import java.util.Scanner;

// 백준 2562: 최댓값
// 9개의 자연수 중 최댓값과 그 위치를 구한다
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int maxVal = 0;
        int maxIdx = 0;

        for (int i = 1; i <= 9; i++) {
            int num = sc.nextInt();
            if (num > maxVal) {
                maxVal = num;
                maxIdx = i;
            }
        }

        System.out.println(maxVal);
        System.out.println(maxIdx);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 2562: 최댓값
// 9개의 자연수 중 최댓값과 그 위치를 구한다
int main() {
    int maxVal = 0;
    int maxIdx = 0;

    for (int i = 1; i <= 9; i++) {
        int num;
        cin >> num;
        if (num > maxVal) {
            maxVal = num;
            maxIdx = i;
        }
    }

    cout << maxVal << endl;
    cout << maxIdx << endl;
    return 0;
}
'''
    },

    # 2525: 오븐 시계
    "2525": {
        "python": '''# 백준 2525: 오븐 시계
# 시작 시각에 요리 시간을 더해 종료 시각을 구한다

A, B = map(int, input().split())
C = int(input())

# 분에 요리 시간을 더함
B += C

# 분이 60 이상이면 시간으로 변환
A += B // 60
B = B % 60

# 시간이 24 이상이면 하루를 넘긴 것
A = A % 24

print(A, B)
''',
        "java": '''import java.util.Scanner;

// 백준 2525: 오븐 시계
// 시작 시각에 요리 시간을 더해 종료 시각을 구한다
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int A = sc.nextInt();
        int B = sc.nextInt();
        int C = sc.nextInt();

        // 분에 요리 시간을 더함
        B += C;

        // 분이 60 이상이면 시간으로 변환
        A += B / 60;
        B = B % 60;

        // 시간이 24 이상이면 하루를 넘긴 것
        A = A % 24;

        System.out.println(A + " " + B);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 2525: 오븐 시계
// 시작 시각에 요리 시간을 더해 종료 시각을 구한다
int main() {
    int A, B, C;
    cin >> A >> B >> C;

    // 분에 요리 시간을 더함
    B += C;

    // 분이 60 이상이면 시간으로 변환
    A += B / 60;
    B = B % 60;

    // 시간이 24 이상이면 하루를 넘긴 것
    A = A % 24;

    cout << A << " " << B << endl;
    return 0;
}
'''
    },

    # 10989: 수 정렬하기 3 (카운팅 정렬)
    "10989": {
        "python": '''# 백준 10989: 수 정렬하기 3
# 카운팅 정렬을 사용하여 N개의 수를 오름차순으로 정렬

import sys
input = sys.stdin.readline

N = int(input())
count = [0] * 10001  # 수의 범위가 1~10000

# 각 수의 개수를 센다
for _ in range(N):
    count[int(input())] += 1

# 개수만큼 출력
result = []
for i in range(1, 10001):
    if count[i] > 0:
        result.append((str(i) + '\\n') * count[i])

print(''.join(result), end='')
''',
        "java": '''import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;

// 백준 10989: 수 정렬하기 3
// 카운팅 정렬을 사용하여 N개의 수를 오름차순으로 정렬
public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(System.out));

        int N = Integer.parseInt(br.readLine());
        int[] count = new int[10001];  // 수의 범위가 1~10000

        // 각 수의 개수를 센다
        for (int i = 0; i < N; i++) {
            count[Integer.parseInt(br.readLine())]++;
        }

        // 개수만큼 출력
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= 10000; i++) {
            for (int j = 0; j < count[i]; j++) {
                sb.append(i).append("\\n");
            }
        }

        bw.write(sb.toString());
        bw.flush();
        bw.close();
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 10989: 수 정렬하기 3
// 카운팅 정렬을 사용하여 N개의 수를 오름차순으로 정렬
int count_arr[10001];  // 수의 범위가 1~10000

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    // 각 수의 개수를 센다
    for (int i = 0; i < N; i++) {
        int num;
        cin >> num;
        count_arr[num]++;
    }

    // 개수만큼 출력
    for (int i = 1; i <= 10000; i++) {
        for (int j = 0; j < count_arr[i]; j++) {
            cout << i << "\\n";
        }
    }

    return 0;
}
'''
    },

    # 1546: 평균
    "1546": {
        "python": '''# 백준 1546: 평균
# 점수를 조작하여 새로운 평균을 구한다

N = int(input())
scores = list(map(int, input().split()))

M = max(scores)  # 최댓값

# 새로운 점수 = 원래 점수 / M * 100
# 새로운 평균 = sum(점수들) / M * 100 / N = sum(점수들) / N / M * 100
new_avg = sum(scores) / M * 100 / N
print(new_avg)
''',
        "java": '''import java.util.Scanner;

// 백준 1546: 평균
// 점수를 조작하여 새로운 평균을 구한다
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        double[] scores = new double[N];
        double M = 0;  // 최댓값
        double sum = 0;

        for (int i = 0; i < N; i++) {
            scores[i] = sc.nextDouble();
            if (scores[i] > M) M = scores[i];
            sum += scores[i];
        }

        // 새로운 평균 계산
        double newAvg = sum / M * 100 / N;
        System.out.println(newAvg);
    }
}
''',
        "cpp": '''#include <iostream>
using namespace std;

// 백준 1546: 평균
// 점수를 조작하여 새로운 평균을 구한다
int main() {
    int N;
    cin >> N;

    double scores[1001];
    double M = 0;  // 최댓값
    double sum = 0;

    for (int i = 0; i < N; i++) {
        cin >> scores[i];
        if (scores[i] > M) M = scores[i];
        sum += scores[i];
    }

    // 새로운 평균 계산
    double newAvg = sum / M * 100 / N;
    cout << fixed;
    cout.precision(6);
    cout << newAvg << endl;

    return 0;
}
'''
    },

    # 1157: 단어 공부
    "1157": {
        "python": '''# 백준 1157: 단어 공부
# 가장 많이 사용된 알파벳을 구한다 (대소문자 구분 없음)

word = input().upper()
count = [0] * 26

for c in word:
    count[ord(c) - ord('A')] += 1

max_count = max(count)
max_char = ''
duplicate = False

for i in range(26):
    if count[i] == max_count:
        if max_char == '':
            max_char = chr(i + ord('A'))
        else:
            duplicate = True
            break

if duplicate:
    print('?')
else:
    print(max_char)
''',
        "java": '''import java.io.BufferedReader;
import java.io.InputStreamReader;

// 백준 1157: 단어 공부
// 가장 많이 사용된 알파벳을 구한다 (대소문자 구분 없음)
public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String word = br.readLine().toUpperCase();

        int[] count = new int[26];

        for (int i = 0; i < word.length(); i++) {
            count[word.charAt(i) - 'A']++;
        }

        int maxCount = 0;
        char maxChar = ' ';
        boolean duplicate = false;

        for (int i = 0; i < 26; i++) {
            if (count[i] > maxCount) {
                maxCount = count[i];
                maxChar = (char) ('A' + i);
                duplicate = false;
            } else if (count[i] == maxCount && maxCount > 0) {
                duplicate = true;
            }
        }

        if (duplicate) {
            System.out.println("?");
        } else {
            System.out.println(maxChar);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <string>
#include <cctype>
using namespace std;

// 백준 1157: 단어 공부
// 가장 많이 사용된 알파벳을 구한다 (대소문자 구분 없음)
int main() {
    string word;
    cin >> word;

    int count[26] = {0};

    for (int i = 0; i < word.length(); i++) {
        count[toupper(word[i]) - 'A']++;
    }

    int maxCount = 0;
    char maxChar = ' ';
    bool duplicate = false;

    for (int i = 0; i < 26; i++) {
        if (count[i] > maxCount) {
            maxCount = count[i];
            maxChar = 'A' + i;
            duplicate = false;
        } else if (count[i] == maxCount && maxCount > 0) {
            duplicate = true;
        }
    }

    if (duplicate) {
        cout << "?" << endl;
    } else {
        cout << maxChar << endl;
    }

    return 0;
}
'''
    },

    # 2869: 달팽이는 올라가고 싶다
    "2869": {
        "python": '''# 백준 2869: 달팽이는 올라가고 싶다
# 달팽이가 V미터 높이의 나무를 올라가는 데 걸리는 일수를 구한다

import math

A, B, V = map(int, input().split())

# 마지막 날에는 미끄러지지 않으므로
# (V - A)까지는 하루에 (A - B)씩 올라가고
# 마지막에 A만큼 올라가면 된다
# 따라서 (V - A) / (A - B) + 1일이 필요

if V <= A:
    print(1)
else:
    days = math.ceil((V - A) / (A - B)) + 1
    print(days)
''',
        "java": '''import java.util.Scanner;

// 백준 2869: 달팽이는 올라가고 싶다
// 달팽이가 V미터 높이의 나무를 올라가는 데 걸리는 일수를 구한다
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int A = sc.nextInt();
        int B = sc.nextInt();
        int V = sc.nextInt();

        // 마지막 날에는 미끄러지지 않으므로
        // (V - A)까지는 하루에 (A - B)씩 올라가고
        // 마지막에 A만큼 올라가면 된다

        if (V <= A) {
            System.out.println(1);
        } else {
            int days = (int) Math.ceil((double)(V - A) / (A - B)) + 1;
            System.out.println(days);
        }
    }
}
''',
        "cpp": '''#include <iostream>
#include <cmath>
using namespace std;

// 백준 2869: 달팽이는 올라가고 싶다
// 달팽이가 V미터 높이의 나무를 올라가는 데 걸리는 일수를 구한다
int main() {
    long long A, B, V;
    cin >> A >> B >> V;

    // 마지막 날에는 미끄러지지 않으므로
    // (V - A)까지는 하루에 (A - B)씩 올라가고
    // 마지막에 A만큼 올라가면 된다

    if (V <= A) {
        cout << 1 << endl;
    } else {
        long long days = (V - A - 1) / (A - B) + 1 + 1;
        cout << days << endl;
    }

    return 0;
}
'''
    },
}


def main():
    # JSON 파일 읽기
    with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_filtered_final_12071.json', 'r', encoding='utf-8') as f:
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
    with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_filtered_final_12071.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nTotal updated: {updated_count}")
    print(f"Remaining empty easy problems: {len(empty_easy_indices) - updated_count}")


if __name__ == '__main__':
    main()
