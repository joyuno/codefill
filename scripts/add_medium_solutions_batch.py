#!/usr/bin/env python3
"""
백준 문제에 대한 솔루션을 생성하고 추가하는 스크립트
Medium 난이도 문제 중 솔루션이 비어있는 문제 5개를 처리합니다.
"""

import json
import fcntl
import os

# 파일 경로
FILE_PATH = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

# 각 문제에 대한 솔루션 정의
SOLUTIONS = {
    # Problem 1: baekjoon_13423 - Three Dots
    "baekjoon_13423": [
        {
            "language": "python",
            "code": '''# 백준 13423 - Three Dots
# 등간격의 세 점을 찾는 문제
import sys
input = sys.stdin.readline

T = int(input())  # 테스트 케이스 수
for _ in range(T):
    N = int(input())  # 점의 개수
    points = list(map(int, input().split()))
    points.sort()  # 정렬

    # 점들을 집합으로 변환하여 빠른 검색
    point_set = set(points)
    count = 0

    # 두 점 a, b를 선택하고, c = 2*b - a가 존재하는지 확인
    for i in range(N):
        for j in range(i + 1, N):
            a = points[i]
            b = points[j]
            # c = b + (b - a) = 2*b - a
            c = 2 * b - a
            if c in point_set:
                count += 1

    print(count)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 13423 - Three Dots
// 등간격의 세 점을 찾는 문제
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int T = Integer.parseInt(br.readLine().trim());  // 테스트 케이스 수

        while (T-- > 0) {
            int N = Integer.parseInt(br.readLine().trim());  // 점의 개수
            int[] points = new int[N];
            StringTokenizer st = new StringTokenizer(br.readLine());

            for (int i = 0; i < N; i++) {
                points[i] = Integer.parseInt(st.nextToken());
            }

            Arrays.sort(points);  // 정렬

            // 점들을 집합으로 변환
            Set<Integer> pointSet = new HashSet<>();
            for (int p : points) {
                pointSet.add(p);
            }

            int count = 0;

            // 두 점 a, b를 선택하고, c = 2*b - a가 존재하는지 확인
            for (int i = 0; i < N; i++) {
                for (int j = i + 1; j < N; j++) {
                    int a = points[i];
                    int b = points[j];
                    int c = 2 * b - a;  // c = b + (b - a)

                    if (pointSet.contains(c)) {
                        count++;
                    }
                }
            }

            sb.append(count).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 13423 - Three Dots
// 등간격의 세 점을 찾는 문제
#include <iostream>
#include <algorithm>
#include <set>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T;  // 테스트 케이스 수
    cin >> T;

    while (T--) {
        int N;  // 점의 개수
        cin >> N;

        int points[1001];
        set<int> pointSet;

        for (int i = 0; i < N; i++) {
            cin >> points[i];
            pointSet.insert(points[i]);
        }

        sort(points, points + N);  // 정렬

        int count = 0;

        // 두 점 a, b를 선택하고, c = 2*b - a가 존재하는지 확인
        for (int i = 0; i < N; i++) {
            for (int j = i + 1; j < N; j++) {
                int a = points[i];
                int b = points[j];
                int c = 2 * b - a;  // c = b + (b - a)

                if (pointSet.count(c)) {
                    count++;
                }
            }
        }

        cout << count << "\\n";
    }

    return 0;
}
'''
        }
    ],

    # Problem 2: baekjoon_17827 - 달팽이 리스트
    "baekjoon_17827": [
        {
            "language": "python",
            "code": '''# 백준 17827 - 달팽이 리스트
# 순환 연결 리스트에서 K번 이동 후 값 찾기
import sys
input = sys.stdin.readline

# N: 노드 개수, M: 질문 횟수, V: N번 노드가 가리키는 노드 번호
N, M, V = map(int, input().split())
nodes = list(map(int, input().split()))  # 각 노드의 값 (0-indexed)

# 사이클 길이 계산 (V번 노드부터 N번 노드까지)
cycle_length = N - V + 1

result = []
for _ in range(M):
    K = int(input())

    if K < N:
        # 사이클에 도달하기 전
        result.append(nodes[K])
    else:
        # 사이클 내에서의 위치 계산
        # V-1 인덱스부터 사이클 시작 (0-indexed)
        remaining = (K - (V - 1)) % cycle_length
        result.append(nodes[V - 1 + remaining])

print('\\n'.join(map(str, result)))
'''
        },
        {
            "language": "java",
            "code": '''// 백준 17827 - 달팽이 리스트
// 순환 연결 리스트에서 K번 이동 후 값 찾기
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        StringTokenizer st = new StringTokenizer(br.readLine());
        int N = Integer.parseInt(st.nextToken());  // 노드 개수
        int M = Integer.parseInt(st.nextToken());  // 질문 횟수
        int V = Integer.parseInt(st.nextToken());  // N번 노드가 가리키는 노드

        int[] nodes = new int[N];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < N; i++) {
            nodes[i] = Integer.parseInt(st.nextToken());
        }

        // 사이클 길이 계산
        int cycleLength = N - V + 1;

        for (int i = 0; i < M; i++) {
            int K = Integer.parseInt(br.readLine().trim());

            if (K < N) {
                // 사이클에 도달하기 전
                sb.append(nodes[K]).append("\\n");
            } else {
                // 사이클 내에서의 위치 계산
                int remaining = (K - (V - 1)) % cycleLength;
                sb.append(nodes[V - 1 + remaining]).append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 17827 - 달팽이 리스트
// 순환 연결 리스트에서 K번 이동 후 값 찾기
#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, M, V;
    cin >> N >> M >> V;  // 노드 개수, 질문 횟수, N번 노드가 가리키는 노드

    vector<int> nodes(N);
    for (int i = 0; i < N; i++) {
        cin >> nodes[i];
    }

    // 사이클 길이 계산
    int cycleLength = N - V + 1;

    for (int i = 0; i < M; i++) {
        int K;
        cin >> K;

        if (K < N) {
            // 사이클에 도달하기 전
            cout << nodes[K] << "\\n";
        } else {
            // 사이클 내에서의 위치 계산
            int remaining = (K - (V - 1)) % cycleLength;
            cout << nodes[V - 1 + remaining] << "\\n";
        }
    }

    return 0;
}
'''
        }
    ],

    # Problem 3: baekjoon_2594 - 놀이공원
    "baekjoon_2594": [
        {
            "language": "python",
            "code": '''# 백준 2594 - 놀이공원
# 놀이기구 운영 시간 사이의 최대 휴식 시간 찾기
import sys
input = sys.stdin.readline

def time_to_minutes(t):
    """HHMM 형식의 시간을 분 단위로 변환"""
    return (t // 100) * 60 + (t % 100)

N = int(input())  # 놀이기구 개수

# 운영 시간을 분 단위로 변환하여 저장
# 시작 10분 전부터 종료 10분 후까지 일해야 함
intervals = []
for _ in range(N):
    start, end = map(int, input().split())
    start_min = time_to_minutes(start) - 10  # 10분 전부터
    end_min = time_to_minutes(end) + 10      # 10분 후까지
    intervals.append((start_min, end_min))

# 시간순으로 정렬
intervals.sort()

# 일과 시작: 오전 10시 (600분), 일과 종료: 오후 10시 (1320분)
DAY_START = 600
DAY_END = 1320

# 겹치는 구간들을 병합
merged = []
for start, end in intervals:
    if merged and merged[-1][1] >= start:
        # 이전 구간과 겹치면 병합
        merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    else:
        merged.append((start, end))

# 휴식 가능 시간 계산
max_rest = 0

# 첫 번째 작업 전 휴식 시간
if merged:
    first_start = merged[0][0]
    if first_start > DAY_START:
        max_rest = max(max_rest, first_start - DAY_START)

# 작업 사이 휴식 시간
for i in range(1, len(merged)):
    gap = merged[i][0] - merged[i-1][1]
    if gap > 0:
        max_rest = max(max_rest, gap)

# 마지막 작업 후 휴식 시간
if merged:
    last_end = merged[-1][1]
    if last_end < DAY_END:
        max_rest = max(max_rest, DAY_END - last_end)

# 놀이기구가 없는 경우
if not merged:
    max_rest = DAY_END - DAY_START

print(max_rest)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 2594 - 놀이공원
// 놀이기구 운영 시간 사이의 최대 휴식 시간 찾기
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        int N = Integer.parseInt(br.readLine().trim());  // 놀이기구 개수

        // 운영 시간을 분 단위로 변환하여 저장
        int[][] intervals = new int[N][2];
        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int start = Integer.parseInt(st.nextToken());
            int end = Integer.parseInt(st.nextToken());

            // HHMM을 분 단위로 변환, 10분 여유 추가
            intervals[i][0] = (start / 100) * 60 + (start % 100) - 10;
            intervals[i][1] = (end / 100) * 60 + (end % 100) + 10;
        }

        // 시작 시간 기준 정렬
        Arrays.sort(intervals, (a, b) -> a[0] - b[0]);

        int DAY_START = 600;   // 오전 10시
        int DAY_END = 1320;    // 오후 10시

        // 겹치는 구간들을 병합
        List<int[]> merged = new ArrayList<>();
        for (int[] interval : intervals) {
            if (!merged.isEmpty() && merged.get(merged.size() - 1)[1] >= interval[0]) {
                merged.get(merged.size() - 1)[1] = Math.max(merged.get(merged.size() - 1)[1], interval[1]);
            } else {
                merged.add(new int[]{interval[0], interval[1]});
            }
        }

        int maxRest = 0;

        // 첫 번째 작업 전 휴식 시간
        if (!merged.isEmpty()) {
            int firstStart = merged.get(0)[0];
            if (firstStart > DAY_START) {
                maxRest = Math.max(maxRest, firstStart - DAY_START);
            }
        }

        // 작업 사이 휴식 시간
        for (int i = 1; i < merged.size(); i++) {
            int gap = merged.get(i)[0] - merged.get(i - 1)[1];
            if (gap > 0) {
                maxRest = Math.max(maxRest, gap);
            }
        }

        // 마지막 작업 후 휴식 시간
        if (!merged.isEmpty()) {
            int lastEnd = merged.get(merged.size() - 1)[1];
            if (lastEnd < DAY_END) {
                maxRest = Math.max(maxRest, DAY_END - lastEnd);
            }
        }

        // 놀이기구가 없는 경우
        if (merged.isEmpty()) {
            maxRest = DAY_END - DAY_START;
        }

        System.out.println(maxRest);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 2594 - 놀이공원
// 놀이기구 운영 시간 사이의 최대 휴식 시간 찾기
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;  // 놀이기구 개수
    cin >> N;

    vector<pair<int, int>> intervals;

    for (int i = 0; i < N; i++) {
        int start, end;
        cin >> start >> end;

        // HHMM을 분 단위로 변환, 10분 여유 추가
        int startMin = (start / 100) * 60 + (start % 100) - 10;
        int endMin = (end / 100) * 60 + (end % 100) + 10;
        intervals.push_back({startMin, endMin});
    }

    // 시작 시간 기준 정렬
    sort(intervals.begin(), intervals.end());

    int DAY_START = 600;   // 오전 10시
    int DAY_END = 1320;    // 오후 10시

    // 겹치는 구간들을 병합
    vector<pair<int, int>> merged;
    for (auto& interval : intervals) {
        if (!merged.empty() && merged.back().second >= interval.first) {
            merged.back().second = max(merged.back().second, interval.second);
        } else {
            merged.push_back(interval);
        }
    }

    int maxRest = 0;

    // 첫 번째 작업 전 휴식 시간
    if (!merged.empty()) {
        int firstStart = merged[0].first;
        if (firstStart > DAY_START) {
            maxRest = max(maxRest, firstStart - DAY_START);
        }
    }

    // 작업 사이 휴식 시간
    for (int i = 1; i < (int)merged.size(); i++) {
        int gap = merged[i].first - merged[i - 1].second;
        if (gap > 0) {
            maxRest = max(maxRest, gap);
        }
    }

    // 마지막 작업 후 휴식 시간
    if (!merged.empty()) {
        int lastEnd = merged.back().second;
        if (lastEnd < DAY_END) {
            maxRest = max(maxRest, DAY_END - lastEnd);
        }
    }

    // 놀이기구가 없는 경우
    if (merged.empty()) {
        maxRest = DAY_END - DAY_START;
    }

    cout << maxRest << endl;

    return 0;
}
'''
        }
    ],

    # Problem 4: baekjoon_1195 - 킥다운
    "baekjoon_1195": [
        {
            "language": "python",
            "code": '''# 백준 1195 - 킥다운
# 두 기어를 맞물리게 할 때 최소 가로 너비 찾기
# 1은 홈(낮음), 2는 이(높음)

def can_mesh(gear1, gear2, offset):
    """
    gear1을 기준으로 gear2를 offset만큼 이동했을 때 맞물릴 수 있는지 확인
    offset이 음수면 gear2가 왼쪽으로, 양수면 오른쪽으로 이동
    """
    for i in range(len(gear2)):
        pos = offset + i  # gear2의 i번째 위치가 gear1에서의 위치
        if 0 <= pos < len(gear1):
            # 두 기어가 겹치는 부분에서 둘 다 2(이)이면 맞물릴 수 없음
            if gear1[pos] == '2' and gear2[i] == '2':
                return False
    return True

def get_width(gear1, gear2, offset):
    """주어진 offset에서 전체 가로 너비 계산"""
    # gear1의 범위: 0 ~ len(gear1)-1
    # gear2의 범위: offset ~ offset+len(gear2)-1
    left = min(0, offset)
    right = max(len(gear1) - 1, offset + len(gear2) - 1)
    return right - left + 1

gear1 = input().strip()
gear2 = input().strip()

min_width = len(gear1) + len(gear2)  # 최대 너비 (겹치지 않을 때)

# gear2를 왼쪽에서 오른쪽으로 이동시키며 확인
# offset 범위: gear2가 gear1 왼쪽 끝에서 오른쪽 끝까지
for offset in range(-len(gear2) + 1, len(gear1)):
    if can_mesh(gear1, gear2, offset):
        width = get_width(gear1, gear2, offset)
        min_width = min(min_width, width)

# gear1과 gear2를 바꿔서도 확인
for offset in range(-len(gear1) + 1, len(gear2)):
    if can_mesh(gear2, gear1, offset):
        width = get_width(gear2, gear1, offset)
        min_width = min(min_width, width)

print(min_width)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 1195 - 킥다운
// 두 기어를 맞물리게 할 때 최소 가로 너비 찾기
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        String gear1 = br.readLine().trim();
        String gear2 = br.readLine().trim();

        int len1 = gear1.length();
        int len2 = gear2.length();

        int minWidth = len1 + len2;  // 최대 너비

        // gear2를 왼쪽에서 오른쪽으로 이동
        for (int offset = -len2 + 1; offset < len1; offset++) {
            if (canMesh(gear1, gear2, offset)) {
                int width = getWidth(len1, len2, offset);
                minWidth = Math.min(minWidth, width);
            }
        }

        // gear1과 gear2를 바꿔서 확인
        for (int offset = -len1 + 1; offset < len2; offset++) {
            if (canMesh(gear2, gear1, offset)) {
                int width = getWidth(len2, len1, offset);
                minWidth = Math.min(minWidth, width);
            }
        }

        System.out.println(minWidth);
    }

    // gear1을 기준으로 gear2를 offset만큼 이동했을 때 맞물릴 수 있는지 확인
    static boolean canMesh(String gear1, String gear2, int offset) {
        for (int i = 0; i < gear2.length(); i++) {
            int pos = offset + i;
            if (pos >= 0 && pos < gear1.length()) {
                // 둘 다 이(2)이면 맞물릴 수 없음
                if (gear1.charAt(pos) == '2' && gear2.charAt(i) == '2') {
                    return false;
                }
            }
        }
        return true;
    }

    // 전체 가로 너비 계산
    static int getWidth(int len1, int len2, int offset) {
        int left = Math.min(0, offset);
        int right = Math.max(len1 - 1, offset + len2 - 1);
        return right - left + 1;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 1195 - 킥다운
// 두 기어를 맞물리게 할 때 최소 가로 너비 찾기
#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

// gear1을 기준으로 gear2를 offset만큼 이동했을 때 맞물릴 수 있는지 확인
bool canMesh(const string& gear1, const string& gear2, int offset) {
    int len1 = gear1.length();
    int len2 = gear2.length();

    for (int i = 0; i < len2; i++) {
        int pos = offset + i;
        if (pos >= 0 && pos < len1) {
            // 둘 다 이(2)이면 맞물릴 수 없음
            if (gear1[pos] == '2' && gear2[i] == '2') {
                return false;
            }
        }
    }
    return true;
}

// 전체 가로 너비 계산
int getWidth(int len1, int len2, int offset) {
    int left = min(0, offset);
    int right = max(len1 - 1, offset + len2 - 1);
    return right - left + 1;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string gear1, gear2;
    cin >> gear1 >> gear2;

    int len1 = gear1.length();
    int len2 = gear2.length();

    int minWidth = len1 + len2;  // 최대 너비

    // gear2를 왼쪽에서 오른쪽으로 이동
    for (int offset = -len2 + 1; offset < len1; offset++) {
        if (canMesh(gear1, gear2, offset)) {
            int width = getWidth(len1, len2, offset);
            minWidth = min(minWidth, width);
        }
    }

    // gear1과 gear2를 바꿔서 확인
    for (int offset = -len1 + 1; offset < len2; offset++) {
        if (canMesh(gear2, gear1, offset)) {
            int width = getWidth(len2, len1, offset);
            minWidth = min(minWidth, width);
        }
    }

    cout << minWidth << endl;

    return 0;
}
'''
        }
    ],

    # Problem 5: baekjoon_2097 - 조약돌
    "baekjoon_2097": [
        {
            "language": "python",
            "code": '''# 백준 2097 - 조약돌
# N개의 조약돌을 격자점에 배치할 때 최소 둘레의 직사각형 찾기
# 직사각형의 가로와 세로는 최소 1 이상이어야 함
import math

N = int(input())

# N개의 점을 가로 a, 세로 b인 직사각형에 배치
# 격자점 수: (a+1) * (b+1) >= N
# 둘레: 2 * (a + b) 를 최소화

# 가로와 세로가 최소 1이어야 하므로 최소 격자점 수는 4 (2x2)
# N <= 4인 경우: 가로=세로=1, 둘레=4

min_perimeter = float('inf')

# a를 1부터 시작하여 탐색
# (a+1) * (b+1) >= N 이고 b >= 1 이어야 함
# 즉 b+1 >= ceil(N / (a+1)) 이고 b >= 1
# a+1 <= N 이면 됨 (b=1일 때 최소 2개 행)

for a in range(1, N + 1):
    # (a+1) * (b+1) >= N
    # b+1 >= N / (a+1)
    # b >= max(1, ceil(N / (a+1)) - 1)

    min_b = max(1, math.ceil(N / (a + 1)) - 1)

    # (a+1) * (min_b + 1) >= N 인지 확인
    if (a + 1) * (min_b + 1) >= N:
        perimeter = 2 * (a + min_b)
        min_perimeter = min(min_perimeter, perimeter)

    # a가 너무 커지면 중단 (최적화)
    if a >= min_perimeter:
        break

print(min_perimeter)
'''
        },
        {
            "language": "java",
            "code": '''// 백준 2097 - 조약돌
// N개의 조약돌을 격자점에 배치할 때 최소 둘레의 직사각형 찾기
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        long N = Long.parseLong(br.readLine().trim());

        // N개의 점을 가로 a, 세로 b인 직사각형에 배치
        // 격자점 수: (a+1) * (b+1) >= N
        // 둘레: 2 * (a + b) 를 최소화

        long minPerimeter = Long.MAX_VALUE;

        // a를 1부터 시작하여 탐색
        for (long a = 1; a <= N && a < minPerimeter; a++) {
            // (a+1) * (b+1) >= N
            // b >= ceil(N / (a+1)) - 1
            // b >= 1

            long minB = Math.max(1, (N + a) / (a + 1) - 1);

            // (a+1) * (minB + 1) >= N 인지 확인
            while ((a + 1) * (minB + 1) < N) {
                minB++;
            }

            long perimeter = 2 * (a + minB);
            minPerimeter = Math.min(minPerimeter, perimeter);
        }

        System.out.println(minPerimeter);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''// 백준 2097 - 조약돌
// N개의 조약돌을 격자점에 배치할 때 최소 둘레의 직사각형 찾기
#include <iostream>
#include <cmath>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long N;
    cin >> N;

    // N개의 점을 가로 a, 세로 b인 직사각형에 배치
    // 격자점 수: (a+1) * (b+1) >= N
    // 둘레: 2 * (a + b) 를 최소화

    long long minPerimeter = LLONG_MAX;

    // a를 1부터 시작하여 탐색
    for (long long a = 1; a <= N && a < minPerimeter; a++) {
        // (a+1) * (b+1) >= N
        // b >= ceil(N / (a+1)) - 1
        // b >= 1

        long long minB = max(1LL, (N + a) / (a + 1) - 1);

        // (a+1) * (minB + 1) >= N 인지 확인
        while ((a + 1) * (minB + 1) < N) {
            minB++;
        }

        long long perimeter = 2 * (a + minB);
        minPerimeter = min(minPerimeter, perimeter);
    }

    cout << minPerimeter << endl;

    return 0;
}
'''
        }
    ]
}

def main():
    # JSON 파일 읽기
    print("JSON 파일 읽는 중...")
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"전체 문제 수: {len(data)}")

    # 업데이트할 문제 찾기 및 업데이트
    updated_count = 0
    updated_ids = []

    for problem in data:
        problem_id = problem.get('id')
        if problem_id in SOLUTIONS:
            current_solutions = problem.get('solutions')
            # 솔루션이 비어있는 경우에만 업데이트
            if current_solutions is None or current_solutions == []:
                problem['solutions'] = SOLUTIONS[problem_id]
                updated_count += 1
                updated_ids.append(problem_id)
                print(f"  업데이트: {problem_id}")
            else:
                print(f"  건너뜀 (이미 솔루션 있음): {problem_id}")

    # 파일 쓰기 (파일 잠금 사용)
    print("\nJSON 파일 저장 중...")
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"\n완료!")
    print(f"업데이트된 문제 수: {updated_count}")
    print(f"업데이트된 문제 ID: {updated_ids}")

    # 검증
    print("\n검증 중...")
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        verify_data = json.load(f)

    for problem in verify_data:
        if problem.get('id') in updated_ids:
            sols = problem.get('solutions', [])
            print(f"  {problem.get('id')}: {len(sols)}개 솔루션")

if __name__ == "__main__":
    main()
