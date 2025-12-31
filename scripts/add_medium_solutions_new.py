#!/usr/bin/env python3
"""
10개의 medium 난이도 문제에 대한 솔루션을 생성하고 저장하는 스크립트
fcntl.LOCK_EX를 사용하여 파일 잠금 적용
"""

import json
import fcntl
import os

# 문제 인덱스와 솔루션 매핑
SOLUTIONS = {
    # 문제 1: 29753 - 최소 성적
    2299: [
        {
            "language": "python",
            "code": '''# 백준 29753: 최소 성적
# 평균 평점 기준을 충족하기 위한 최소 성적 계산
import sys
from decimal import Decimal, ROUND_DOWN

input = sys.stdin.readline

# 성적 -> 평점 변환 테이블 (Decimal 사용하여 정밀도 유지)
grade_to_point = {
    "A+": Decimal("4.50"),
    "A0": Decimal("4.00"),
    "B+": Decimal("3.50"),
    "B0": Decimal("3.00"),
    "C+": Decimal("2.50"),
    "C0": Decimal("2.00"),
    "D+": Decimal("1.50"),
    "D0": Decimal("1.00"),
    "F": Decimal("0.00")
}

# 평점 순서 (높은 순)
grades_order = ["A+", "A0", "B+", "B0", "C+", "C0", "D+", "D0", "F"]

# 입력 처리
first_line = input().split()
n = int(first_line[0])
target = Decimal(first_line[1])

total_credits = 0
total_points = Decimal("0")

# n-1개 과목 정보 읽기
for _ in range(n - 1):
    line = input().split()
    credit = int(line[0])
    grade = line[1]
    total_credits += credit
    total_points += credit * grade_to_point[grade]

# 마지막 과목 학점
last_credit = int(input().strip())
total_credits += last_credit

# 각 성적에 대해 검사 (가장 낮은 성적부터)
result = "impossible"
for grade in reversed(grades_order):
    point = grade_to_point[grade]
    final_points = total_points + last_credit * point
    # 평균 계산 후 소수점 셋째자리에서 버림
    avg = (final_points / total_credits).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    # 기준 초과 여부 확인
    if avg > target:
        result = grade

if result == "impossible":
    print("impossible")
else:
    print(result)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;

// 백준 29753: 최소 성적
// 평균 평점 기준을 충족하기 위한 최소 성적 계산
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        // 성적 -> 평점 매핑
        Map<String, BigDecimal> gradeToPoint = new HashMap<>();
        gradeToPoint.put("A+", new BigDecimal("4.50"));
        gradeToPoint.put("A0", new BigDecimal("4.00"));
        gradeToPoint.put("B+", new BigDecimal("3.50"));
        gradeToPoint.put("B0", new BigDecimal("3.00"));
        gradeToPoint.put("C+", new BigDecimal("2.50"));
        gradeToPoint.put("C0", new BigDecimal("2.00"));
        gradeToPoint.put("D+", new BigDecimal("1.50"));
        gradeToPoint.put("D0", new BigDecimal("1.00"));
        gradeToPoint.put("F", new BigDecimal("0.00"));

        String[] grades = {"A+", "A0", "B+", "B0", "C+", "C0", "D+", "D0", "F"};

        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        BigDecimal target = new BigDecimal(st.nextToken());

        int totalCredits = 0;
        BigDecimal totalPoints = BigDecimal.ZERO;

        // n-1개 과목 처리
        for (int i = 0; i < n - 1; i++) {
            st = new StringTokenizer(br.readLine());
            int credit = Integer.parseInt(st.nextToken());
            String grade = st.nextToken();
            totalCredits += credit;
            totalPoints = totalPoints.add(gradeToPoint.get(grade).multiply(new BigDecimal(credit)));
        }

        // 마지막 과목 학점
        int lastCredit = Integer.parseInt(br.readLine().trim());
        totalCredits += lastCredit;

        // 가장 낮은 성적부터 확인
        String result = "impossible";
        for (int i = grades.length - 1; i >= 0; i--) {
            BigDecimal point = gradeToPoint.get(grades[i]);
            BigDecimal finalPoints = totalPoints.add(point.multiply(new BigDecimal(lastCredit)));
            BigDecimal avg = finalPoints.divide(new BigDecimal(totalCredits), 2, RoundingMode.DOWN);

            if (avg.compareTo(target) > 0) {
                result = grades[i];
            }
        }

        System.out.println(result);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
#include <map>
using namespace std;

// 백준 29753: 최소 성적
// 정수 연산으로 부동소수점 오차 방지
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // 성적 -> 평점 * 100 (정수로 변환)
    map<string, int> gradeToPoint;
    gradeToPoint["A+"] = 450;
    gradeToPoint["A0"] = 400;
    gradeToPoint["B+"] = 350;
    gradeToPoint["B0"] = 300;
    gradeToPoint["C+"] = 250;
    gradeToPoint["C0"] = 200;
    gradeToPoint["D+"] = 150;
    gradeToPoint["D0"] = 100;
    gradeToPoint["F"] = 0;

    string grades[] = {"A+", "A0", "B+", "B0", "C+", "C0", "D+", "D0", "F"};

    int n;
    string targetStr;
    cin >> n >> targetStr;

    // 목표 평점을 정수로 변환 (100배)
    int target = 0;
    bool afterDot = false;
    int decimalCount = 0;
    for (char c : targetStr) {
        if (c == '.') {
            afterDot = true;
        } else {
            target = target * 10 + (c - '0');
            if (afterDot) decimalCount++;
        }
    }
    while (decimalCount < 2) {
        target *= 10;
        decimalCount++;
    }

    long long totalCredits = 0;
    long long totalPoints = 0;

    // n-1개 과목 처리
    for (int i = 0; i < n - 1; i++) {
        int credit;
        string grade;
        cin >> credit >> grade;
        totalCredits += credit;
        totalPoints += (long long)credit * gradeToPoint[grade];
    }

    int lastCredit;
    cin >> lastCredit;
    totalCredits += lastCredit;

    // 가장 낮은 성적부터 확인
    string result = "impossible";
    for (int i = 8; i >= 0; i--) {
        long long finalPoints = totalPoints + (long long)lastCredit * gradeToPoint[grades[i]];
        // 평균 계산 (소수점 셋째자리 버림 = 100배 기준에서 그냥 나눔)
        long long avg = finalPoints / totalCredits;

        if (avg > target) {
            result = grades[i];
        }
    }

    cout << result << endl;
    return 0;
}
'''
        }
    ],

    # 문제 2: 26099 - 설탕 배달 2
    2302: [
        {
            "language": "python",
            "code": '''# 백준 26099: 설탕 배달 2
# 3kg과 5kg 봉지로 N kg을 만들 때 최소 봉지 수
import sys

n = int(sys.stdin.readline())

# 5로 나누어 떨어지면 가장 적은 봉지
if n % 5 == 0:
    print(n // 5)
# 5로 나눈 나머지가 3의 배수인 경우
elif n % 5 == 1 and n >= 6:
    # 5kg 봉지 (n//5 - 1)개 + 3kg 봉지 2개
    print(n // 5 - 1 + 2)
elif n % 5 == 2 and n >= 12:
    # 5kg 봉지 (n//5 - 2)개 + 3kg 봉지 4개
    print(n // 5 - 2 + 4)
elif n % 5 == 3:
    # 3kg 봉지 1개 사용
    print(n // 5 + 1)
elif n % 5 == 4 and n >= 9:
    # 3kg 봉지 3개 (9kg) 사용 후 나머지 5kg으로
    print(n // 5 - 1 + 3)
elif n == 3:
    print(1)
else:
    print(-1)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;

// 백준 26099: 설탕 배달 2
// 3kg과 5kg 봉지로 N kg을 만들 때 최소 봉지 수
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        long n = Long.parseLong(br.readLine().trim());

        long result;
        int remainder = (int)(n % 5);

        if (remainder == 0) {
            // 5로 나누어 떨어짐
            result = n / 5;
        } else if (remainder == 1 && n >= 6) {
            // 5kg (n/5 - 1)개 + 3kg 2개 = 6kg으로 나머지 1 처리
            result = n / 5 - 1 + 2;
        } else if (remainder == 2 && n >= 12) {
            // 5kg (n/5 - 2)개 + 3kg 4개 = 12kg으로 나머지 2 처리
            result = n / 5 - 2 + 4;
        } else if (remainder == 3) {
            // 3kg 1개 사용
            result = n / 5 + 1;
        } else if (remainder == 4 && n >= 9) {
            // 3kg 3개 = 9kg으로 나머지 4 처리
            result = n / 5 - 1 + 3;
        } else if (n == 3) {
            result = 1;
        } else {
            result = -1;
        }

        System.out.println(result);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
using namespace std;

// 백준 26099: 설탕 배달 2
// 3kg과 5kg 봉지로 N kg을 만들 때 최소 봉지 수
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long n;
    cin >> n;

    long long result;
    int remainder = n % 5;

    if (remainder == 0) {
        // 5로 나누어 떨어짐
        result = n / 5;
    } else if (remainder == 1 && n >= 6) {
        // 5kg (n/5 - 1)개 + 3kg 2개
        result = n / 5 - 1 + 2;
    } else if (remainder == 2 && n >= 12) {
        // 5kg (n/5 - 2)개 + 3kg 4개
        result = n / 5 - 2 + 4;
    } else if (remainder == 3) {
        // 3kg 1개 사용
        result = n / 5 + 1;
    } else if (remainder == 4 && n >= 9) {
        // 3kg 3개 = 9kg 사용
        result = n / 5 - 1 + 3;
    } else if (n == 3) {
        result = 1;
    } else {
        result = -1;
    }

    cout << result << endl;
    return 0;
}
'''
        }
    ],

    # 문제 3: 28125 - 2023 아주머학교 프로그래딩 정시머힌
    2310: [
        {
            "language": "python",
            "code": r'''# 백준 28125: 2023 아주머학교 프로그래딩 정시머힌
# 변환된 문자열을 원래대로 복원
import sys

input = sys.stdin.readline

n = int(input())

for _ in range(n):
    s = input().rstrip()
    result = []
    change_count = 0
    i = 0

    while i < len(s):
        # \' 패턴 확인 (w의 변환)
        if i + 1 < len(s) and s[i:i+2] == "\\'":
            result.append('w')
            change_count += 1
            i += 2
        # ' 는 v의 변환
        elif s[i] == "'":
            result.append('v')
            change_count += 1
            i += 1
        elif s[i] == '@':
            result.append('a')
            change_count += 1
            i += 1
        elif s[i] == '[':
            result.append('c')
            change_count += 1
            i += 1
        elif s[i] == '!':
            result.append('i')
            change_count += 1
            i += 1
        elif s[i] == ';':
            result.append('j')
            change_count += 1
            i += 1
        elif s[i] == '^':
            result.append('n')
            change_count += 1
            i += 1
        elif s[i] == '0':
            result.append('o')
            change_count += 1
            i += 1
        elif s[i] == '7':
            result.append('t')
            change_count += 1
            i += 1
        else:
            result.append(s[i])
            i += 1

    original = ''.join(result)
    # 절반 이상 바뀌었으면 이해 불가
    if change_count >= (len(original) + 1) // 2:
        print("I don't understand")
    else:
        print(original)
'''
        },
        {
            "language": "java",
            "code": r'''import java.io.*;

// 백준 28125: 2023 아주머학교 프로그래딩 정시머힌
// 변환된 문자열을 원래대로 복원
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int n = Integer.parseInt(br.readLine().trim());

        for (int t = 0; t < n; t++) {
            String s = br.readLine();
            StringBuilder result = new StringBuilder();
            int changeCount = 0;

            for (int i = 0; i < s.length(); i++) {
                // \' 패턴 확인 (w의 변환)
                if (i + 1 < s.length() && s.charAt(i) == '\\' && s.charAt(i + 1) == '\'') {
                    result.append('w');
                    changeCount++;
                    i++;
                } else if (s.charAt(i) == '\'') {
                    // ' 는 v의 변환
                    result.append('v');
                    changeCount++;
                } else {
                    char c = s.charAt(i);
                    switch (c) {
                        case '@': result.append('a'); changeCount++; break;
                        case '[': result.append('c'); changeCount++; break;
                        case '!': result.append('i'); changeCount++; break;
                        case ';': result.append('j'); changeCount++; break;
                        case '^': result.append('n'); changeCount++; break;
                        case '0': result.append('o'); changeCount++; break;
                        case '7': result.append('t'); changeCount++; break;
                        default: result.append(c); break;
                    }
                }
            }

            String original = result.toString();
            // 절반 이상 바뀌었으면 이해 불가
            if (changeCount >= (original.length() + 1) / 2) {
                sb.append("I don't understand\n");
            } else {
                sb.append(original).append("\n");
            }
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": r'''#include <iostream>
#include <string>
using namespace std;

// 백준 28125: 2023 아주머학교 프로그래딩 정시머힌
// 변환된 문자열을 원래대로 복원
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    cin.ignore();

    while (n--) {
        string s;
        getline(cin, s);

        string result;
        int changeCount = 0;

        for (int i = 0; i < s.length(); i++) {
            // \' 패턴 확인 (w의 변환)
            if (i + 1 < s.length() && s[i] == '\\' && s[i + 1] == '\'') {
                result += 'w';
                changeCount++;
                i++;
            } else if (s[i] == '\'') {
                // ' 는 v의 변환
                result += 'v';
                changeCount++;
            } else {
                char c = s[i];
                if (c == '@') { result += 'a'; changeCount++; }
                else if (c == '[') { result += 'c'; changeCount++; }
                else if (c == '!') { result += 'i'; changeCount++; }
                else if (c == ';') { result += 'j'; changeCount++; }
                else if (c == '^') { result += 'n'; changeCount++; }
                else if (c == '0') { result += 'o'; changeCount++; }
                else if (c == '7') { result += 't'; changeCount++; }
                else { result += c; }
            }
        }

        // 절반 이상 바뀌었으면 이해 불가
        if (changeCount >= (result.length() + 1) / 2) {
            cout << "I don't understand\n";
        } else {
            cout << result << "\n";
        }
    }

    return 0;
}
'''
        }
    ],

    # 문제 4: 18230 - 2xN 예쁜 타일링
    2312: [
        {
            "language": "python",
            "code": '''# 백준 18230: 2xN 예쁜 타일링
# 2x1, 2x2 타일로 2xN 바닥 채우기 (최대 예쁨)
import sys

input = sys.stdin.readline

n, a, b = map(int, input().split())

# 2x1 타일 예쁨 값들 (내림차순 정렬)
tiles_1 = sorted(list(map(int, input().split())), reverse=True)
# 2x2 타일 예쁨 값들 (내림차순 정렬)
tiles_2 = sorted(list(map(int, input().split())), reverse=True)

# 2x1 타일 2개의 합 누적 (한 칸 채우는데 2개 필요)
tiles_1_pair = [0]
for i in range(0, len(tiles_1) - 1, 2):
    tiles_1_pair.append(tiles_1_pair[-1] + tiles_1[i] + tiles_1[i + 1])

# 2x2 타일 누적
tiles_2_sum = [0]
for i in range(len(tiles_2)):
    tiles_2_sum.append(tiles_2_sum[-1] + tiles_2[i])

max_beauty = 0

# 2x2 타일 j개 사용 (n이 홀수면 최소 1개)
for j in range(n % 2, min(b, n) + 1):
    remain = n - j  # 남은 칸은 2x1 타일 쌍으로 채움
    if remain <= len(tiles_1_pair) - 1:
        beauty = tiles_2_sum[j] + tiles_1_pair[remain]
        max_beauty = max(max_beauty, beauty)

print(max_beauty)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 18230: 2xN 예쁜 타일링
// 2x1, 2x2 타일로 2xN 바닥 채우기 (최대 예쁨)
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int a = Integer.parseInt(st.nextToken());
        int b = Integer.parseInt(st.nextToken());

        // 2x1 타일 예쁨 값들
        Integer[] tiles1 = new Integer[a];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < a; i++) {
            tiles1[i] = Integer.parseInt(st.nextToken());
        }
        Arrays.sort(tiles1, Collections.reverseOrder());

        // 2x2 타일 예쁨 값들
        Integer[] tiles2 = new Integer[b];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < b; i++) {
            tiles2[i] = Integer.parseInt(st.nextToken());
        }
        Arrays.sort(tiles2, Collections.reverseOrder());

        // 2x1 타일 2개씩 묶은 누적합
        long[] pair1 = new long[a / 2 + 1];
        for (int i = 0; i < a / 2; i++) {
            pair1[i + 1] = pair1[i] + tiles1[i * 2] + tiles1[i * 2 + 1];
        }

        // 2x2 타일 누적합
        long[] sum2 = new long[b + 1];
        for (int i = 0; i < b; i++) {
            sum2[i + 1] = sum2[i] + tiles2[i];
        }

        long maxBeauty = 0;

        // 2x2 타일 j개 사용
        for (int j = n % 2; j <= Math.min(b, n); j++) {
            int remain = n - j;
            if (remain <= a / 2) {
                long beauty = sum2[j] + pair1[remain];
                maxBeauty = Math.max(maxBeauty, beauty);
            }
        }

        System.out.println(maxBeauty);
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

// 백준 18230: 2xN 예쁜 타일링
// 2x1, 2x2 타일로 2xN 바닥 채우기 (최대 예쁨)
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, a, b;
    cin >> n >> a >> b;

    // 2x1 타일 예쁨 값들
    vector<int> tiles1(a);
    for (int i = 0; i < a; i++) {
        cin >> tiles1[i];
    }
    sort(tiles1.rbegin(), tiles1.rend());

    // 2x2 타일 예쁨 값들
    vector<int> tiles2(b);
    for (int i = 0; i < b; i++) {
        cin >> tiles2[i];
    }
    sort(tiles2.rbegin(), tiles2.rend());

    // 2x1 타일 2개씩 묶은 누적합
    vector<long long> pair1(a / 2 + 1);
    for (int i = 0; i < a / 2; i++) {
        pair1[i + 1] = pair1[i] + tiles1[i * 2] + tiles1[i * 2 + 1];
    }

    // 2x2 타일 누적합
    vector<long long> sum2(b + 1);
    for (int i = 0; i < b; i++) {
        sum2[i + 1] = sum2[i] + tiles2[i];
    }

    long long maxBeauty = 0;

    // 2x2 타일 j개 사용 (n이 홀수면 최소 1개)
    for (int j = n % 2; j <= min(b, n); j++) {
        int remain = n - j;
        if (remain <= a / 2) {
            long long beauty = sum2[j] + pair1[remain];
            maxBeauty = max(maxBeauty, beauty);
        }
    }

    cout << maxBeauty << endl;
    return 0;
}
'''
        }
    ],

    # 문제 5: 25918 - 북극곰은 괄호를 찢어
    2315: [
        {
            "language": "python",
            "code": '''# 백준 25918: 북극곰은 괄호를 찢어
# 올바른 괄호 문자열 만들기 위한 최소 일수
import sys

input = sys.stdin.readline

n = int(input())
s = input().rstrip()

# 괄호 개수 확인
open_count = s.count('(')
close_count = s.count(')')

# 열린 괄호와 닫힌 괄호 수가 다르면 불가능
if open_count != close_count:
    print(-1)
else:
    # 괄호 깊이 추적
    # 최대 깊이가 필요한 일수
    depth = 0
    max_depth = 0

    for c in s:
        if c == '(':
            depth += 1
        else:
            depth -= 1
        max_depth = max(max_depth, abs(depth))

    print(max_depth)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;

// 백준 25918: 북극곰은 괄호를 찢어
// 올바른 괄호 문자열 만들기 위한 최소 일수
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        String s = br.readLine().trim();

        // 괄호 개수 확인
        int openCount = 0, closeCount = 0;
        for (char c : s.toCharArray()) {
            if (c == '(') openCount++;
            else closeCount++;
        }

        // 열린 괄호와 닫힌 괄호 수가 다르면 불가능
        if (openCount != closeCount) {
            System.out.println(-1);
            return;
        }

        // 괄호 깊이 추적
        int depth = 0;
        int maxDepth = 0;

        for (char c : s.toCharArray()) {
            if (c == '(') {
                depth++;
            } else {
                depth--;
            }
            maxDepth = Math.max(maxDepth, Math.abs(depth));
        }

        System.out.println(maxDepth);
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

// 백준 25918: 북극곰은 괄호를 찢어
// 올바른 괄호 문자열 만들기 위한 최소 일수
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    string s;
    cin >> n >> s;

    // 괄호 개수 확인
    int openCount = 0, closeCount = 0;
    for (char c : s) {
        if (c == '(') openCount++;
        else closeCount++;
    }

    // 열린 괄호와 닫힌 괄호 수가 다르면 불가능
    if (openCount != closeCount) {
        cout << -1 << endl;
        return 0;
    }

    // 괄호 깊이 추적
    int depth = 0;
    int maxDepth = 0;

    for (char c : s) {
        if (c == '(') {
            depth++;
        } else {
            depth--;
        }
        maxDepth = max(maxDepth, abs(depth));
    }

    cout << maxDepth << endl;
    return 0;
}
'''
        }
    ],

    # 문제 6: 1411 - 비슷한 단어
    2322: [
        {
            "language": "python",
            "code": '''# 백준 1411: 비슷한 단어
# 알파벳 치환으로 같아지는 단어 쌍 개수 찾기
import sys

input = sys.stdin.readline

def is_similar(w1, w2):
    """두 단어가 비슷한지 확인"""
    if len(w1) != len(w2):
        return False

    # w1 -> w2 매핑
    map1 = {}
    # w2 -> w1 매핑 (역방향 확인)
    map2 = {}

    for c1, c2 in zip(w1, w2):
        if c1 in map1:
            if map1[c1] != c2:
                return False
        else:
            map1[c1] = c2

        if c2 in map2:
            if map2[c2] != c1:
                return False
        else:
            map2[c2] = c1

    return True

n = int(input())
words = [input().rstrip() for _ in range(n)]

count = 0
for i in range(n):
    for j in range(i + 1, n):
        if is_similar(words[i], words[j]):
            count += 1

print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;

// 백준 1411: 비슷한 단어
// 알파벳 치환으로 같아지는 단어 쌍 개수 찾기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        String[] words = new String[n];

        for (int i = 0; i < n; i++) {
            words[i] = br.readLine().trim();
        }

        int count = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (isSimilar(words[i], words[j])) {
                    count++;
                }
            }
        }

        System.out.println(count);
    }

    // 두 단어가 비슷한지 확인
    static boolean isSimilar(String w1, String w2) {
        if (w1.length() != w2.length()) return false;

        int[] map1 = new int[26];  // w1 -> w2 매핑
        int[] map2 = new int[26];  // w2 -> w1 매핑

        for (int i = 0; i < 26; i++) {
            map1[i] = -1;
            map2[i] = -1;
        }

        for (int i = 0; i < w1.length(); i++) {
            int c1 = w1.charAt(i) - 'a';
            int c2 = w2.charAt(i) - 'a';

            if (map1[c1] == -1) {
                map1[c1] = c2;
            } else if (map1[c1] != c2) {
                return false;
            }

            if (map2[c2] == -1) {
                map2[c2] = c1;
            } else if (map2[c2] != c1) {
                return false;
            }
        }

        return true;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
#include <vector>
using namespace std;

// 백준 1411: 비슷한 단어
// 알파벳 치환으로 같아지는 단어 쌍 개수 찾기

// 두 단어가 비슷한지 확인
bool isSimilar(const string& w1, const string& w2) {
    if (w1.length() != w2.length()) return false;

    int map1[26], map2[26];
    fill(map1, map1 + 26, -1);
    fill(map2, map2 + 26, -1);

    for (int i = 0; i < w1.length(); i++) {
        int c1 = w1[i] - 'a';
        int c2 = w2[i] - 'a';

        if (map1[c1] == -1) {
            map1[c1] = c2;
        } else if (map1[c1] != c2) {
            return false;
        }

        if (map2[c2] == -1) {
            map2[c2] = c1;
        } else if (map2[c2] != c1) {
            return false;
        }
    }

    return true;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<string> words(n);
    for (int i = 0; i < n; i++) {
        cin >> words[i];
    }

    int count = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (isSimilar(words[i], words[j])) {
                count++;
            }
        }
    }

    cout << count << endl;
    return 0;
}
'''
        }
    ],

    # 문제 7: 15729 - 방탈출
    2323: [
        {
            "language": "python",
            "code": '''# 백준 15729: 방탈출
# 최소 버튼 누름 횟수로 목표 상태 만들기
import sys

input = sys.stdin.readline

n = int(input())
target = list(map(int, input().split()))

# 현재 상태 (모두 꺼진 상태)
current = [0] * n
count = 0

# 왼쪽부터 순서대로 처리 (그리디)
for i in range(n):
    if current[i] != target[i]:
        # 버튼 누르기 (현재 버튼과 오른쪽 2개 토글)
        count += 1
        for j in range(i, min(i + 3, n)):
            current[j] = 1 - current[j]

print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 15729: 방탈출
// 최소 버튼 누름 횟수로 목표 상태 만들기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        int[] target = new int[n];

        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            target[i] = Integer.parseInt(st.nextToken());
        }

        // 현재 상태 (모두 꺼진 상태)
        int[] current = new int[n];
        int count = 0;

        // 왼쪽부터 순서대로 처리 (그리디)
        for (int i = 0; i < n; i++) {
            if (current[i] != target[i]) {
                // 버튼 누르기 (현재 버튼과 오른쪽 2개 토글)
                count++;
                for (int j = i; j < Math.min(i + 3, n); j++) {
                    current[j] = 1 - current[j];
                }
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

// 백준 15729: 방탈출
// 최소 버튼 누름 횟수로 목표 상태 만들기
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> target(n);
    for (int i = 0; i < n; i++) {
        cin >> target[i];
    }

    // 현재 상태 (모두 꺼진 상태)
    vector<int> current(n, 0);
    int count = 0;

    // 왼쪽부터 순서대로 처리 (그리디)
    for (int i = 0; i < n; i++) {
        if (current[i] != target[i]) {
            // 버튼 누르기 (현재 버튼과 오른쪽 2개 토글)
            count++;
            for (int j = i; j < min(i + 3, n); j++) {
                current[j] = 1 - current[j];
            }
        }
    }

    cout << count << endl;
    return 0;
}
'''
        }
    ],

    # 문제 8: 3213 - 피자
    2338: [
        {
            "language": "python",
            "code": '''# 백준 3213: 피자
# 1/4, 1/2, 3/4 조각으로 최소 피자 판수 구하기
import sys

input = sys.stdin.readline

n = int(input())

# 각 크기별 개수
count = {1: 0, 2: 0, 3: 0}  # 1/4, 1/2, 3/4

for _ in range(n):
    s = input().strip()
    if s == "1/4":
        count[1] += 1
    elif s == "1/2":
        count[2] += 1
    else:  # 3/4
        count[3] += 1

pizzas = 0

# 3/4와 1/4 매칭
pairs_34_14 = min(count[3], count[1])
pizzas += pairs_34_14
count[3] -= pairs_34_14
count[1] -= pairs_34_14

# 남은 3/4는 각각 1판씩 필요
pizzas += count[3]

# 1/2끼리 2개씩 매칭
pizzas += count[2] // 2
count[2] %= 2

# 남은 1/2가 있으면 1/4와 매칭
if count[2] == 1:
    if count[1] >= 2:
        pizzas += 1
        count[1] -= 2
    elif count[1] == 1:
        pizzas += 1
        count[1] = 0
    else:
        pizzas += 1

# 남은 1/4는 4개씩 묶기
pizzas += (count[1] + 3) // 4

print(pizzas)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;

// 백준 3213: 피자
// 1/4, 1/2, 3/4 조각으로 최소 피자 판수 구하기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());

        // 각 크기별 개수 (1/4, 1/2, 3/4)
        int[] count = new int[4];

        for (int i = 0; i < n; i++) {
            String s = br.readLine().trim();
            if (s.equals("1/4")) {
                count[1]++;
            } else if (s.equals("1/2")) {
                count[2]++;
            } else {
                count[3]++;
            }
        }

        int pizzas = 0;

        // 3/4와 1/4 매칭
        int pairs = Math.min(count[3], count[1]);
        pizzas += pairs;
        count[3] -= pairs;
        count[1] -= pairs;

        // 남은 3/4는 각각 1판씩 필요
        pizzas += count[3];

        // 1/2끼리 2개씩 매칭
        pizzas += count[2] / 2;
        count[2] %= 2;

        // 남은 1/2가 있으면 1/4와 매칭
        if (count[2] == 1) {
            if (count[1] >= 2) {
                pizzas++;
                count[1] -= 2;
            } else if (count[1] == 1) {
                pizzas++;
                count[1] = 0;
            } else {
                pizzas++;
            }
        }

        // 남은 1/4는 4개씩 묶기
        pizzas += (count[1] + 3) / 4;

        System.out.println(pizzas);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
using namespace std;

// 백준 3213: 피자
// 1/4, 1/2, 3/4 조각으로 최소 피자 판수 구하기
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    // 각 크기별 개수 (1/4, 1/2, 3/4)
    int count[4] = {0, 0, 0, 0};

    for (int i = 0; i < n; i++) {
        string s;
        cin >> s;
        if (s == "1/4") {
            count[1]++;
        } else if (s == "1/2") {
            count[2]++;
        } else {
            count[3]++;
        }
    }

    int pizzas = 0;

    // 3/4와 1/4 매칭
    int pairs = min(count[3], count[1]);
    pizzas += pairs;
    count[3] -= pairs;
    count[1] -= pairs;

    // 남은 3/4는 각각 1판씩 필요
    pizzas += count[3];

    // 1/2끼리 2개씩 매칭
    pizzas += count[2] / 2;
    count[2] %= 2;

    // 남은 1/2가 있으면 1/4와 매칭
    if (count[2] == 1) {
        if (count[1] >= 2) {
            pizzas++;
            count[1] -= 2;
        } else if (count[1] == 1) {
            pizzas++;
            count[1] = 0;
        } else {
            pizzas++;
        }
    }

    // 남은 1/4는 4개씩 묶기
    pizzas += (count[1] + 3) / 4;

    cout << pizzas << endl;
    return 0;
}
'''
        }
    ],

    # 문제 9: 16508 - 전공책
    2342: [
        {
            "language": "python",
            "code": '''# 백준 16508: 전공책
# 비트마스킹으로 책 조합 탐색하여 단어 만들기
import sys
from collections import Counter

input = sys.stdin.readline

target = input().rstrip()
n = int(input())

books = []
for _ in range(n):
    line = input().split()
    price = int(line[0])
    title = line[1]
    books.append((price, title))

target_count = Counter(target)
min_cost = float('inf')

# 모든 책 조합 탐색 (비트마스킹)
for mask in range(1, 1 << n):
    total_cost = 0
    char_count = Counter()

    for i in range(n):
        if mask & (1 << i):
            total_cost += books[i][0]
            char_count += Counter(books[i][1])

    # 이미 최소 비용보다 크면 스킵
    if total_cost >= min_cost:
        continue

    # 목표 단어를 만들 수 있는지 확인
    can_make = True
    for char, cnt in target_count.items():
        if char_count[char] < cnt:
            can_make = False
            break

    if can_make:
        min_cost = total_cost

if min_cost == float('inf'):
    print(-1)
else:
    print(min_cost)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 16508: 전공책
// 비트마스킹으로 책 조합 탐색하여 단어 만들기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        String target = br.readLine().trim();
        int n = Integer.parseInt(br.readLine().trim());

        int[] prices = new int[n];
        String[] titles = new String[n];

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            prices[i] = Integer.parseInt(st.nextToken());
            titles[i] = st.nextToken();
        }

        // 목표 문자 개수
        int[] targetCount = new int[26];
        for (char c : target.toCharArray()) {
            targetCount[c - 'A']++;
        }

        int minCost = Integer.MAX_VALUE;

        // 모든 책 조합 탐색 (비트마스킹)
        for (int mask = 1; mask < (1 << n); mask++) {
            int totalCost = 0;
            int[] charCount = new int[26];

            for (int i = 0; i < n; i++) {
                if ((mask & (1 << i)) != 0) {
                    totalCost += prices[i];
                    for (char c : titles[i].toCharArray()) {
                        charCount[c - 'A']++;
                    }
                }
            }

            // 이미 최소 비용보다 크면 스킵
            if (totalCost >= minCost) continue;

            // 목표 단어를 만들 수 있는지 확인
            boolean canMake = true;
            for (int i = 0; i < 26; i++) {
                if (charCount[i] < targetCount[i]) {
                    canMake = false;
                    break;
                }
            }

            if (canMake) {
                minCost = totalCost;
            }
        }

        System.out.println(minCost == Integer.MAX_VALUE ? -1 : minCost);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
#include <climits>
using namespace std;

// 백준 16508: 전공책
// 비트마스킹으로 책 조합 탐색하여 단어 만들기
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string target;
    cin >> target;

    int n;
    cin >> n;

    int prices[16];
    string titles[16];

    for (int i = 0; i < n; i++) {
        cin >> prices[i] >> titles[i];
    }

    // 목표 문자 개수
    int targetCount[26] = {0};
    for (char c : target) {
        targetCount[c - 'A']++;
    }

    int minCost = INT_MAX;

    // 모든 책 조합 탐색 (비트마스킹)
    for (int mask = 1; mask < (1 << n); mask++) {
        int totalCost = 0;
        int charCount[26] = {0};

        for (int i = 0; i < n; i++) {
            if (mask & (1 << i)) {
                totalCost += prices[i];
                for (char c : titles[i]) {
                    charCount[c - 'A']++;
                }
            }
        }

        // 이미 최소 비용보다 크면 스킵
        if (totalCost >= minCost) continue;

        // 목표 단어를 만들 수 있는지 확인
        bool canMake = true;
        for (int i = 0; i < 26; i++) {
            if (charCount[i] < targetCount[i]) {
                canMake = false;
                break;
            }
        }

        if (canMake) {
            minCost = totalCost;
        }
    }

    cout << (minCost == INT_MAX ? -1 : minCost) << endl;
    return 0;
}
'''
        }
    ],

    # 문제 10: 2121 - 넷이 놀기
    2343: [
        {
            "language": "python",
            "code": '''# 백준 2121: 넷이 놀기
# 주어진 점들로 가로 A, 세로 B인 직사각형 개수 찾기
import sys

input = sys.stdin.readline

n = int(input())
a, b = map(int, input().split())

# 점들을 set에 저장
points = set()
for _ in range(n):
    x, y = map(int, input().split())
    points.add((x, y))

count = 0

# 각 점을 좌하단으로 하는 직사각형 확인
for (x, y) in points:
    # 나머지 3개 꼭짓점이 있는지 확인
    if (x + a, y) in points and (x, y + b) in points and (x + a, y + b) in points:
        count += 1

print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

// 백준 2121: 넷이 놀기
// 주어진 점들로 가로 A, 세로 B인 직사각형 개수 찾기
public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int n = Integer.parseInt(br.readLine().trim());
        StringTokenizer st = new StringTokenizer(br.readLine());
        int a = Integer.parseInt(st.nextToken());
        int b = Integer.parseInt(st.nextToken());

        // 점들을 HashSet에 저장
        Set<Long> points = new HashSet<>();
        int[][] coords = new int[n][2];

        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            int x = Integer.parseInt(st.nextToken());
            int y = Integer.parseInt(st.nextToken());
            coords[i][0] = x;
            coords[i][1] = y;
            // x, y를 하나의 long 값으로 인코딩
            points.add(encode(x, y));
        }

        int count = 0;

        // 각 점을 좌하단으로 하는 직사각형 확인
        for (int i = 0; i < n; i++) {
            int x = coords[i][0];
            int y = coords[i][1];

            // 나머지 3개 꼭짓점이 있는지 확인
            if (points.contains(encode(x + a, y)) &&
                points.contains(encode(x, y + b)) &&
                points.contains(encode(x + a, y + b))) {
                count++;
            }
        }

        System.out.println(count);
    }

    // 좌표를 long으로 인코딩 (x, y 범위가 -100000000 ~ 100000000)
    static long encode(long x, long y) {
        return x * 300000001L + y;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <set>
#include <vector>
using namespace std;

// 백준 2121: 넷이 놀기
// 주어진 점들로 가로 A, 세로 B인 직사각형 개수 찾기
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    int a, b;
    cin >> a >> b;

    // 점들을 set에 저장
    set<pair<int, int>> points;
    vector<pair<int, int>> coords(n);

    for (int i = 0; i < n; i++) {
        int x, y;
        cin >> x >> y;
        coords[i] = {x, y};
        points.insert({x, y});
    }

    int count = 0;

    // 각 점을 좌하단으로 하는 직사각형 확인
    for (int i = 0; i < n; i++) {
        int x = coords[i].first;
        int y = coords[i].second;

        // 나머지 3개 꼭짓점이 있는지 확인
        if (points.count({x + a, y}) &&
            points.count({x, y + b}) &&
            points.count({x + a, y + b})) {
            count++;
        }
    }

    cout << count << endl;
    return 0;
}
'''
        }
    ]
}

def main():
    file_path = "/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json"

    # 파일 읽기 (잠금 사용)
    with open(file_path, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # 솔루션 추가
    updated_count = 0
    for idx, solutions in SOLUTIONS.items():
        if idx < len(data):
            # 기존 솔루션이 비어있는 경우에만 추가
            if not data[idx].get('solutions') or len(data[idx]['solutions']) == 0:
                data[idx]['solutions'] = solutions
                updated_count += 1
                print(f"Updated problem at index {idx}: {data[idx].get('name')}")
            else:
                print(f"Skipped problem at index {idx}: already has solutions")

    # 파일 쓰기 (배타적 잠금 사용)
    with open(file_path, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\nTotal updated: {updated_count} problems")
    print("Done!")

if __name__ == "__main__":
    main()
