#!/usr/bin/env python3
"""
Generate solutions for remaining problems (405-409, 411-414, 416-418)
"""
import json
import fcntl

def get_remaining_solutions():
    """Return solutions for remaining problems."""
    solutions = {}

    # Problem 405: baekjoon_31909 - FOCUS
    solutions[6230] = [
        {
            "language": "python",
            "code": '''# FOCUS - 키 섞기 시뮬레이션
import sys
input = sys.stdin.readline

n = int(input())
commands = list(map(int, input().split()))
k = int(input())

# 각 키의 위치 (키 번호 -> 위치)
pos = list(range(8))  # pos[i] = 키 i가 있는 위치

# 유효한 명령: 2^i + 2^j (i < j)
valid = {}
for i in range(8):
    for j in range(i + 1, 8):
        valid[2**i + 2**j] = (i, j)

for cmd in commands:
    if cmd in valid:
        i, j = valid[cmd]
        # i번 키와 j번 키의 위치 교환
        pos[i], pos[j] = pos[j], pos[i]

print(pos[k])
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
        int[] commands = new int[n];
        for (int i = 0; i < n; i++) {
            commands[i] = Integer.parseInt(st.nextToken());
        }
        int k = Integer.parseInt(br.readLine().trim());

        // 유효한 명령 계산
        Map<Integer, int[]> valid = new HashMap<>();
        for (int i = 0; i < 8; i++) {
            for (int j = i + 1; j < 8; j++) {
                valid.put((1 << i) + (1 << j), new int[]{i, j});
            }
        }

        int[] pos = new int[8];
        for (int i = 0; i < 8; i++) pos[i] = i;

        for (int cmd : commands) {
            if (valid.containsKey(cmd)) {
                int[] pair = valid.get(cmd);
                int temp = pos[pair[0]];
                pos[pair[0]] = pos[pair[1]];
                pos[pair[1]] = temp;
            }
        }

        System.out.println(pos[k]);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <map>
using namespace std;

int main() {
    int n;
    cin >> n;

    map<int, pair<int, int>> valid;
    for (int i = 0; i < 8; i++) {
        for (int j = i + 1; j < 8; j++) {
            valid[(1 << i) + (1 << j)] = {i, j};
        }
    }

    int pos[8];
    for (int i = 0; i < 8; i++) pos[i] = i;

    for (int i = 0; i < n; i++) {
        int cmd;
        cin >> cmd;
        if (valid.count(cmd)) {
            auto [a, b] = valid[cmd];
            swap(pos[a], pos[b]);
        }
    }

    int k;
    cin >> k;
    cout << pos[k] << endl;
    return 0;
}
'''
        }
    ]

    # Problem 406: baekjoon_13021 - 공 색칠하기
    solutions[6233] = [
        {
            "language": "python",
            "code": '''# 공 색칠하기 - 좌표 압축으로 구간 분할
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
ranges = []
for _ in range(m):
    l, r = map(int, input().split())
    ranges.append((l, r))

# 좌표 압축
points = set([1, n + 1])
for l, r in ranges:
    points.add(l)
    points.add(r + 1)
points = sorted(points)

# 각 구간이 어떤 range에 포함되는지 확인
# 같은 집합에 속한 구간들은 같은 색
# 다른 집합이면 독립적으로 2가지 색 가능

# 각 기계 사용이 커버하는 구간들
seg_count = len(points) - 1
# 각 segment가 마지막으로 커버된 기계 번호
last_cover = [0] * seg_count

for idx, (l, r) in enumerate(ranges):
    for i, p in enumerate(points[:-1]):
        if l <= p and points[i + 1] - 1 <= r:
            last_cover[i] = idx + 1

# 독립적인 색 조합 수
# 같은 last_cover 값을 가진 segment들은 같은 색
unique_groups = len(set(last_cover))
print(2 ** unique_groups)
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
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        int[][] ranges = new int[m][2];
        Set<Integer> points = new TreeSet<>();
        points.add(1);
        points.add(n + 1);

        for (int i = 0; i < m; i++) {
            st = new StringTokenizer(br.readLine());
            ranges[i][0] = Integer.parseInt(st.nextToken());
            ranges[i][1] = Integer.parseInt(st.nextToken());
            points.add(ranges[i][0]);
            points.add(ranges[i][1] + 1);
        }

        Integer[] pts = points.toArray(new Integer[0]);
        int segCount = pts.length - 1;
        int[] lastCover = new int[segCount];

        for (int idx = 0; idx < m; idx++) {
            int l = ranges[idx][0], r = ranges[idx][1];
            for (int i = 0; i < segCount; i++) {
                if (l <= pts[i] && pts[i + 1] - 1 <= r) {
                    lastCover[i] = idx + 1;
                }
            }
        }

        Set<Integer> unique = new HashSet<>();
        for (int v : lastCover) unique.add(v);
        System.out.println(1L << unique.size());
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
    int n, m;
    cin >> n >> m;

    vector<pair<int, int>> ranges(m);
    set<int> pts;
    pts.insert(1);
    pts.insert(n + 1);

    for (int i = 0; i < m; i++) {
        cin >> ranges[i].first >> ranges[i].second;
        pts.insert(ranges[i].first);
        pts.insert(ranges[i].second + 1);
    }

    vector<int> points(pts.begin(), pts.end());
    int segCount = points.size() - 1;
    vector<int> lastCover(segCount, 0);

    for (int idx = 0; idx < m; idx++) {
        int l = ranges[idx].first, r = ranges[idx].second;
        for (int i = 0; i < segCount; i++) {
            if (l <= points[i] && points[i + 1] - 1 <= r) {
                lastCover[i] = idx + 1;
            }
        }
    }

    set<int> unique(lastCover.begin(), lastCover.end());
    cout << (1LL << unique.size()) << endl;
    return 0;
}
'''
        }
    ]

    # Problem 407: baekjoon_5186 - 파티를 열어라!!!
    solutions[6235] = [
        {
            "language": "python",
            "code": '''# 파티를 열어라!!! - 친구들 집으로 보내기
import sys
input = sys.stdin.readline

k = int(input())
for case in range(1, k + 1):
    n, c, l = map(int, input().split())

    # 친구 정보
    friends = []
    for _ in range(n):
        parts = input().split()
        region = int(parts[0])
        drunk = parts[1] == 'I'  # I면 취함
        friends.append((region, drunk))

    # 자동차 정보
    cars = []
    for _ in range(c):
        parts = input().split()
        region = int(parts[0])
        seats = int(parts[1])
        cars.append((region, seats))

    # 각 지역별 친구 분류
    region_friends = {}
    for region, drunk in friends:
        if region not in region_friends:
            region_friends[region] = {'sober': 0, 'drunk': 0}
        if drunk:
            region_friends[region]['drunk'] += 1
        else:
            region_friends[region]['sober'] += 1

    # 각 지역별 자동차 좌석 합
    region_cars = {}
    for region, seats in cars:
        if region not in region_cars:
            region_cars[region] = 0
        region_cars[region] += seats

    # 집에 가지 못하는 친구 수
    stay = 0
    for region in region_friends:
        sober = region_friends[region]['sober']
        drunk = region_friends[region]['drunk']
        total = sober + drunk

        if region not in region_cars:
            stay += total
        else:
            seats = region_cars[region]
            if sober == 0:
                # 운전할 사람 없음
                stay += total
            else:
                # 최대 태울 수 있는 수 = min(seats, total)
                can_go = min(seats, total)
                stay += total - can_go

    print(f"Data Set {case}:")
    print(stay)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int K = Integer.parseInt(br.readLine().trim());

        for (int cs = 1; cs <= K; cs++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int c = Integer.parseInt(st.nextToken());
            int l = Integer.parseInt(st.nextToken());

            Map<Integer, int[]> regionFriends = new HashMap<>();
            for (int i = 0; i < n; i++) {
                st = new StringTokenizer(br.readLine());
                int region = Integer.parseInt(st.nextToken());
                boolean drunk = st.nextToken().equals("I");
                regionFriends.putIfAbsent(region, new int[]{0, 0});
                if (drunk) regionFriends.get(region)[1]++;
                else regionFriends.get(region)[0]++;
            }

            Map<Integer, Integer> regionCars = new HashMap<>();
            for (int i = 0; i < c; i++) {
                st = new StringTokenizer(br.readLine());
                int region = Integer.parseInt(st.nextToken());
                int seats = Integer.parseInt(st.nextToken());
                regionCars.merge(region, seats, Integer::sum);
            }

            int stay = 0;
            for (int region : regionFriends.keySet()) {
                int sober = regionFriends.get(region)[0];
                int drunk = regionFriends.get(region)[1];
                int total = sober + drunk;

                if (!regionCars.containsKey(region) || sober == 0) {
                    stay += total;
                } else {
                    int seats = regionCars.get(region);
                    int canGo = Math.min(seats, total);
                    stay += total - canGo;
                }
            }

            System.out.println("Data Set " + cs + ":");
            System.out.println(stay);
        }
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <map>
#include <string>
using namespace std;

int main() {
    int K;
    cin >> K;

    for (int cs = 1; cs <= K; cs++) {
        int n, c, l;
        cin >> n >> c >> l;

        map<int, pair<int, int>> regionFriends;
        for (int i = 0; i < n; i++) {
            int region;
            string status;
            cin >> region >> status;
            if (status == "I") regionFriends[region].second++;
            else regionFriends[region].first++;
        }

        map<int, int> regionCars;
        for (int i = 0; i < c; i++) {
            int region, seats;
            cin >> region >> seats;
            regionCars[region] += seats;
        }

        int stay = 0;
        for (auto& [region, cnt] : regionFriends) {
            int sober = cnt.first, drunk = cnt.second;
            int total = sober + drunk;

            if (regionCars.find(region) == regionCars.end() || sober == 0) {
                stay += total;
            } else {
                int seats = regionCars[region];
                int canGo = min(seats, total);
                stay += total - canGo;
            }
        }

        cout << "Data Set " << cs << ":\\n" << stay << "\\n";
    }
    return 0;
}
'''
        }
    ]

    # Problem 408: baekjoon_33043 - 이변마작 9
    solutions[6237] = [
        {
            "language": "python",
            "code": '''# 이변마작 9 - 최소 기억력
import sys
input = sys.stdin.readline

n = int(input())
tiles = input().split()

# 5장 이상 같은 패가 기억 범위 내에 있어야 함
# 최소 기억력 X 찾기

min_memory = -1

for i in range(n):
    # i번째 위치에서 이변을 눈치채려면
    # 최근 X장 중 같은 패가 5장 이상
    count = {}
    for j in range(i, -1, -1):
        tile = tiles[j]
        count[tile] = count.get(tile, 0) + 1
        if count[tile] >= 5:
            memory_needed = i - j + 1
            if min_memory == -1:
                min_memory = memory_needed
            else:
                min_memory = min(min_memory, memory_needed)
            break

print(min_memory)
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
        String[] tiles = br.readLine().split(" ");

        int minMemory = -1;

        for (int i = 0; i < n; i++) {
            Map<String, Integer> count = new HashMap<>();
            for (int j = i; j >= 0; j--) {
                count.merge(tiles[j], 1, Integer::sum);
                if (count.get(tiles[j]) >= 5) {
                    int memoryNeeded = i - j + 1;
                    if (minMemory == -1) minMemory = memoryNeeded;
                    else minMemory = Math.min(minMemory, memoryNeeded);
                    break;
                }
            }
        }

        System.out.println(minMemory);
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

int main() {
    int n;
    cin >> n;
    string tiles[n];
    for (int i = 0; i < n; i++) cin >> tiles[i];

    int minMemory = -1;

    for (int i = 0; i < n; i++) {
        map<string, int> count;
        for (int j = i; j >= 0; j--) {
            count[tiles[j]]++;
            if (count[tiles[j]] >= 5) {
                int memoryNeeded = i - j + 1;
                if (minMemory == -1) minMemory = memoryNeeded;
                else minMemory = min(minMemory, memoryNeeded);
                break;
            }
        }
    }

    cout << minMemory << endl;
    return 0;
}
'''
        }
    ]

    # Problem 409: baekjoon_33925 - 쿠키런
    solutions[6238] = [
        {
            "language": "python",
            "code": '''# 쿠키런 - 장애물 피하기
import sys
input = sys.stdin.readline

line = input().split()
n, j, s, h, k = int(line[0]), int(line[1]), int(line[2]), int(line[3]), int(line[4])

stage = []
for _ in range(3):
    stage.append(input().strip())

# 장애물 타입 파악
obstacles = []
for col in range(n):
    top = stage[0][col]
    mid = stage[1][col]
    bot = stage[2][col]

    if top == '.' and mid == '.' and bot == '.':
        obstacles.append(None)
    elif top == 'v' and mid == 'v' and bot == '.':
        obstacles.append('top')  # 상단 장애물: 슬라이드 1번
    elif top == '.' and mid == '^' and bot == '^':
        obstacles.append('low')  # 낮은 장애물: 점프 1번
    elif top == '.' and mid == '.' and bot == '^':
        obstacles.append('low')  # 낮은 장애물
    elif top == '^' and mid == '^' and bot == '^':
        obstacles.append('high')  # 높은 장애물: 점프 2번
    elif top == '.' and mid == '^' and bot == '^':
        obstacles.append('high')  # 높은 장애물
    else:
        # 기타 패턴
        if '^' in [top, mid, bot]:
            if top == '^':
                obstacles.append('high')
            else:
                obstacles.append('low')
        elif 'v' in [top, mid, bot]:
            obstacles.append('top')
        else:
            obstacles.append(None)

# 그리디: 가능하면 스킬 사용, 아니면 충돌
jump_used = 0
slide_used = 0
hp = h

for i, obs in enumerate(obstacles):
    if obs is None:
        continue

    if obs == 'low':
        if jump_used < j:
            jump_used += 1
        else:
            hp -= k
    elif obs == 'high':
        if jump_used + 1 < j:
            jump_used += 2
        elif jump_used < j:
            jump_used += 1
            hp -= k  # 한 번만 피함
        else:
            hp -= k
    elif obs == 'top':
        if slide_used < s:
            slide_used += 1
        else:
            hp -= k

    if hp <= 0:
        print(-1)
        exit()

print(hp)
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
        int J = Integer.parseInt(st.nextToken());
        int S = Integer.parseInt(st.nextToken());
        int H = Integer.parseInt(st.nextToken());
        int K = Integer.parseInt(st.nextToken());

        String[] stage = new String[3];
        for (int i = 0; i < 3; i++) stage[i] = br.readLine();

        int jumpUsed = 0, slideUsed = 0, hp = H;

        for (int col = 0; col < N; col++) {
            char top = stage[0].charAt(col);
            char mid = stage[1].charAt(col);
            char bot = stage[2].charAt(col);

            if (top == '.' && mid == '.' && bot == '.') continue;

            boolean hasV = top == 'v' || mid == 'v' || bot == 'v';
            boolean hasCaret = top == '^' || mid == '^' || bot == '^';

            if (hasV) {
                if (slideUsed < S) slideUsed++;
                else hp -= K;
            } else if (hasCaret) {
                int count = (top == '^' ? 1 : 0) + (mid == '^' ? 1 : 0) + (bot == '^' ? 1 : 0);
                if (count >= 2) {
                    if (jumpUsed + 2 <= J) jumpUsed += 2;
                    else hp -= K;
                } else {
                    if (jumpUsed + 1 <= J) jumpUsed += 1;
                    else hp -= K;
                }
            }

            if (hp <= 0) {
                System.out.println(-1);
                return;
            }
        }

        System.out.println(hp);
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
    int N, J, S, H, K;
    cin >> N >> J >> S >> H >> K;

    string stage[3];
    for (int i = 0; i < 3; i++) cin >> stage[i];

    int jumpUsed = 0, slideUsed = 0, hp = H;

    for (int col = 0; col < N; col++) {
        char top = stage[0][col];
        char mid = stage[1][col];
        char bot = stage[2][col];

        if (top == '.' && mid == '.' && bot == '.') continue;

        bool hasV = top == 'v' || mid == 'v' || bot == 'v';
        bool hasCaret = top == '^' || mid == '^' || bot == '^';

        if (hasV) {
            if (slideUsed < S) slideUsed++;
            else hp -= K;
        } else if (hasCaret) {
            int count = (top == '^') + (mid == '^') + (bot == '^');
            if (count >= 2) {
                if (jumpUsed + 2 <= J) jumpUsed += 2;
                else hp -= K;
            } else {
                if (jumpUsed + 1 <= J) jumpUsed += 1;
                else hp -= K;
            }
        }

        if (hp <= 0) {
            cout << -1 << endl;
            return 0;
        }
    }

    cout << hp << endl;
    return 0;
}
'''
        }
    ]

    # Problem 411: baekjoon_5848 - Message Relay
    solutions[6246] = [
        {
            "language": "python",
            "code": '''# Message Relay - loopy가 아닌 소 개수
import sys
input = sys.stdin.readline

n = int(input())
forward = [0] * (n + 1)
for i in range(1, n + 1):
    forward[i] = int(input())

# 각 소가 loopy인지 확인
def is_loopy(start):
    visited = set()
    curr = start
    while curr != 0 and curr not in visited:
        visited.add(curr)
        curr = forward[curr]
    return curr != 0  # 0이 아니면 루프

count = 0
for i in range(1, n + 1):
    if not is_loopy(i):
        count += 1

print(count)
'''
        },
        {
            "language": "java",
            "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int[] forward;

    static boolean isLoopy(int start) {
        Set<Integer> visited = new HashSet<>();
        int curr = start;
        while (curr != 0 && !visited.contains(curr)) {
            visited.add(curr);
            curr = forward[curr];
        }
        return curr != 0;
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        forward = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            forward[i] = Integer.parseInt(br.readLine().trim());
        }

        int count = 0;
        for (int i = 1; i <= n; i++) {
            if (!isLoopy(i)) count++;
        }
        System.out.println(count);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <set>
using namespace std;

int forward[1001];

bool isLoopy(int start) {
    set<int> visited;
    int curr = start;
    while (curr != 0 && visited.find(curr) == visited.end()) {
        visited.insert(curr);
        curr = forward[curr];
    }
    return curr != 0;
}

int main() {
    int n;
    cin >> n;
    for (int i = 1; i <= n; i++) cin >> forward[i];

    int count = 0;
    for (int i = 1; i <= n; i++) {
        if (!isLoopy(i)) count++;
    }
    cout << count << endl;
    return 0;
}
'''
        }
    ]

    # Problem 412: baekjoon_32331 - 원교수님 A+ 주세요
    solutions[6250] = [
        {
            "language": "python",
            "code": '''# 원교수님 A+ 주세요
import sys
input = sys.stdin.readline

n, m, x, y = map(int, input().split())

# 김한양 정보
hanyang_line = input().split()
hanyang_id = hanyang_line[0]
hanyang_mid = int(hanyang_line[1])

# 다른 학생들 정보
students_2024 = []
for _ in range(n - 1):
    line = input().split()
    student_id = line[0]
    mid_score = int(line[1])
    if student_id.startswith("2024"):
        # 기말 예측: y - (x - mid_score) = y - x + mid_score, 최소 0
        final_pred = max(0, y - (x - mid_score))
        total_pred = mid_score + final_pred
        students_2024.append(total_pred)

# 2024 학생들의 총점 예측값 정렬 (내림차순)
students_2024.sort(reverse=True)

# 김한양이 M등 안에 들어야 함
# 김한양의 총점 = hanyang_mid + 기말점수
# M번째로 높은 예측 총점보다 높아야 함

if len(students_2024) < m:
    # 다른 2024 학생이 m명 미만이면 무조건 A+
    print("YES")
    print(0)
else:
    # m번째 학생의 예측 총점
    threshold = students_2024[m - 1]

    # 김한양 총점 > threshold 필요
    need = threshold - hanyang_mid + 1
    if need <= y:
        print("YES")
        print(max(0, need))
    else:
        print("NO")
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
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());
        long x = Long.parseLong(st.nextToken());
        long y = Long.parseLong(st.nextToken());

        st = new StringTokenizer(br.readLine());
        String hanyangId = st.nextToken();
        long hanyangMid = Long.parseLong(st.nextToken());

        List<Long> students2024 = new ArrayList<>();
        for (int i = 0; i < n - 1; i++) {
            st = new StringTokenizer(br.readLine());
            String id = st.nextToken();
            long midScore = Long.parseLong(st.nextToken());
            if (id.startsWith("2024")) {
                long finalPred = Math.max(0, y - (x - midScore));
                students2024.add(midScore + finalPred);
            }
        }

        Collections.sort(students2024, Collections.reverseOrder());

        if (students2024.size() < m) {
            System.out.println("YES");
            System.out.println(0);
        } else {
            long threshold = students2024.get(m - 1);
            long need = threshold - hanyangMid + 1;
            if (need <= y) {
                System.out.println("YES");
                System.out.println(Math.max(0, need));
            } else {
                System.out.println("NO");
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
#include <algorithm>
#include <string>
using namespace std;

int main() {
    int n, m;
    long long x, y;
    cin >> n >> m >> x >> y;

    string hanyangId;
    long long hanyangMid;
    cin >> hanyangId >> hanyangMid;

    vector<long long> students2024;
    for (int i = 0; i < n - 1; i++) {
        string id;
        long long midScore;
        cin >> id >> midScore;
        if (id.substr(0, 4) == "2024") {
            long long finalPred = max(0LL, y - (x - midScore));
            students2024.push_back(midScore + finalPred);
        }
    }

    sort(students2024.rbegin(), students2024.rend());

    if ((int)students2024.size() < m) {
        cout << "YES\\n0\\n";
    } else {
        long long threshold = students2024[m - 1];
        long long need = threshold - hanyangMid + 1;
        if (need <= y) {
            cout << "YES\\n" << max(0LL, need) << "\\n";
        } else {
            cout << "NO\\n";
        }
    }
    return 0;
}
'''
        }
    ]

    # Problem 413: baekjoon_5179 - 우승자는 누구?
    solutions[6252] = [
        {
            "language": "python",
            "code": '''# 우승자는 누구? - ACM 스타일 순위
import sys
input = sys.stdin.readline

k = int(input())
for case in range(1, k + 1):
    m, n, p = map(int, input().split())

    # 참가자별 정보
    solved = {}  # participant -> {problem -> (time, wrong_count)}
    wrong = {}   # participant -> {problem -> wrong_count}

    for _ in range(n):
        parts = input().split()
        participant = int(parts[0])
        problem = parts[1]
        time = int(parts[2])
        correct = int(parts[3])

        if participant not in solved:
            solved[participant] = {}
            wrong[participant] = {}

        if problem not in solved[participant]:
            if correct == 1:
                wc = wrong[participant].get(problem, 0)
                solved[participant][problem] = time + wc * 20
            else:
                wrong[participant][problem] = wrong[participant].get(problem, 0) + 1
        # 이미 맞힌 문제는 무시

    # 점수 계산
    scores = []
    for i in range(1, p + 1):
        if i in solved:
            num_solved = len(solved[i])
            total_time = sum(solved[i].values())
        else:
            num_solved = 0
            total_time = 0
        scores.append((i, num_solved, total_time))

    # 정렬: 푼 문제 많은 순, 시간 적은 순
    scores.sort(key=lambda x: (-x[1], x[2]))

    print(f"Data Set {case}:")
    for i, num, time in scores:
        print(i, num, time)

    if case < k:
        print()
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
        int K = Integer.parseInt(br.readLine().trim());

        for (int cs = 1; cs <= K; cs++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int M = Integer.parseInt(st.nextToken());
            int N = Integer.parseInt(st.nextToken());
            int P = Integer.parseInt(st.nextToken());

            Map<Integer, Map<String, Integer>> solved = new HashMap<>();
            Map<Integer, Map<String, Integer>> wrong = new HashMap<>();

            for (int i = 0; i < N; i++) {
                st = new StringTokenizer(br.readLine());
                int p = Integer.parseInt(st.nextToken());
                String prob = st.nextToken();
                int t = Integer.parseInt(st.nextToken());
                int j = Integer.parseInt(st.nextToken());

                solved.putIfAbsent(p, new HashMap<>());
                wrong.putIfAbsent(p, new HashMap<>());

                if (!solved.get(p).containsKey(prob)) {
                    if (j == 1) {
                        int wc = wrong.get(p).getOrDefault(prob, 0);
                        solved.get(p).put(prob, t + wc * 20);
                    } else {
                        wrong.get(p).merge(prob, 1, Integer::sum);
                    }
                }
            }

            int[][] scores = new int[P][3];
            for (int i = 1; i <= P; i++) {
                scores[i-1][0] = i;
                if (solved.containsKey(i)) {
                    scores[i-1][1] = solved.get(i).size();
                    scores[i-1][2] = solved.get(i).values().stream().mapToInt(Integer::intValue).sum();
                }
            }

            Arrays.sort(scores, (a, b) -> a[1] != b[1] ? b[1] - a[1] : a[2] - b[2]);

            sb.append("Data Set ").append(cs).append(":\\n");
            for (int[] s : scores) {
                sb.append(s[0]).append(" ").append(s[1]).append(" ").append(s[2]).append("\\n");
            }
            if (cs < K) sb.append("\\n");
        }
        System.out.print(sb);
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <map>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int K;
    cin >> K;

    for (int cs = 1; cs <= K; cs++) {
        int M, N, P;
        cin >> M >> N >> P;

        map<int, map<string, int>> solved;
        map<int, map<string, int>> wrong;

        for (int i = 0; i < N; i++) {
            int p, t, j;
            string prob;
            cin >> p >> prob >> t >> j;

            if (solved[p].find(prob) == solved[p].end()) {
                if (j == 1) {
                    int wc = wrong[p][prob];
                    solved[p][prob] = t + wc * 20;
                } else {
                    wrong[p][prob]++;
                }
            }
        }

        vector<tuple<int, int, int>> scores;
        for (int i = 1; i <= P; i++) {
            int num = solved[i].size();
            int total = 0;
            for (auto& [k, v] : solved[i]) total += v;
            scores.push_back({i, num, total});
        }

        sort(scores.begin(), scores.end(), [](auto& a, auto& b) {
            if (get<1>(a) != get<1>(b)) return get<1>(a) > get<1>(b);
            return get<2>(a) < get<2>(b);
        });

        cout << "Data Set " << cs << ":\\n";
        for (auto& [id, num, time] : scores) {
            cout << id << " " << num << " " << time << "\\n";
        }
        if (cs < K) cout << "\\n";
    }
    return 0;
}
'''
        }
    ]

    # Problem 414: baekjoon_23826 - 와이파이
    solutions[6268] = [
        {
            "language": "python",
            "code": '''# 와이파이
import sys
input = sys.stdin.readline

n = int(input())

# 소학습실 정보
x0, y0, e0 = map(int, input().split())

rooms = []
hotspots = []  # (x, y, e) for rooms with hotspot

for i in range(n):
    x, y, e = map(int, input().split())
    rooms.append((x, y))
    if e > 0:
        hotspots.append((x, y, e))

max_speed = -1

for i, (rx, ry) in enumerate(rooms):
    # 공용 WiFi 세기
    dist_main = abs(rx - x0) + abs(ry - y0)
    main_strength = max(0, e0 - dist_main)

    # 핫스팟 방해
    interference = 0
    for hx, hy, he in hotspots:
        dist = abs(rx - hx) + abs(ry - hy)
        interference += max(0, he - dist)

    speed = main_strength - interference
    if speed > 0:
        max_speed = max(max_speed, speed)

if max_speed > 0:
    print(max_speed)
else:
    print("IMPOSSIBLE")
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
        long x0 = Long.parseLong(st.nextToken());
        long y0 = Long.parseLong(st.nextToken());
        long e0 = Long.parseLong(st.nextToken());

        long[][] rooms = new long[n][2];
        List<long[]> hotspots = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            st = new StringTokenizer(br.readLine());
            rooms[i][0] = Long.parseLong(st.nextToken());
            rooms[i][1] = Long.parseLong(st.nextToken());
            long e = Long.parseLong(st.nextToken());
            if (e > 0) hotspots.add(new long[]{rooms[i][0], rooms[i][1], e});
        }

        long maxSpeed = -1;

        for (int i = 0; i < n; i++) {
            long rx = rooms[i][0], ry = rooms[i][1];
            long distMain = Math.abs(rx - x0) + Math.abs(ry - y0);
            long mainStrength = Math.max(0, e0 - distMain);

            long interference = 0;
            for (long[] h : hotspots) {
                long dist = Math.abs(rx - h[0]) + Math.abs(ry - h[1]);
                interference += Math.max(0, h[2] - dist);
            }

            long speed = mainStrength - interference;
            if (speed > 0) maxSpeed = Math.max(maxSpeed, speed);
        }

        if (maxSpeed > 0) System.out.println(maxSpeed);
        else System.out.println("IMPOSSIBLE");
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <vector>
#include <cstdlib>
using namespace std;

int main() {
    int n;
    cin >> n;

    long long x0, y0, e0;
    cin >> x0 >> y0 >> e0;

    vector<pair<long long, long long>> rooms(n);
    vector<tuple<long long, long long, long long>> hotspots;

    for (int i = 0; i < n; i++) {
        long long x, y, e;
        cin >> x >> y >> e;
        rooms[i] = {x, y};
        if (e > 0) hotspots.push_back({x, y, e});
    }

    long long maxSpeed = -1;

    for (int i = 0; i < n; i++) {
        long long rx = rooms[i].first, ry = rooms[i].second;
        long long distMain = abs(rx - x0) + abs(ry - y0);
        long long mainStrength = max(0LL, e0 - distMain);

        long long interference = 0;
        for (auto& [hx, hy, he] : hotspots) {
            long long dist = abs(rx - hx) + abs(ry - hy);
            interference += max(0LL, he - dist);
        }

        long long speed = mainStrength - interference;
        if (speed > 0) maxSpeed = max(maxSpeed, speed);
    }

    if (maxSpeed > 0) cout << maxSpeed << endl;
    else cout << "IMPOSSIBLE" << endl;
    return 0;
}
'''
        }
    ]

    # Problem 416: baekjoon_31927 - 렬정! 렬정! 렬정!
    solutions[6278] = [
        {
            "language": "python",
            "code": '''# 렬정! 렬정! 렬정! - 내림차순 만들기
import sys
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))

# 최대 n//2번 연산
# 한 번에 i에 x를 더하고 j에 x를 빼기

# 내림차순: a[0] >= a[1] >= ... >= a[n-1]

# 그리디: 가장 큰 값을 앞으로, 가장 작은 값을 뒤로

ops = []

for k in range(n // 2):
    # 현재 배열 복사
    arr = a[:]

    # 정렬
    target = sorted(arr, reverse=True)

    # 이미 내림차순인지 확인
    is_sorted = True
    for i in range(n - 1):
        if arr[i] < arr[i + 1]:
            is_sorted = False
            break

    if is_sorted:
        break

    # 가장 앞에 가장 큰 값 필요
    # i=0에 x를 더하고, j=n-1에 x를 뺌
    diff = max(arr) - arr[0] + 1

    a[0] += diff
    a[n - 1] -= diff
    ops.append(a[:])

# 결과 확인
is_sorted = True
for i in range(n - 1):
    if a[i] < a[i + 1]:
        is_sorted = False
        break

if not is_sorted:
    print(-1)
else:
    print(len(ops))
    for arr in ops:
        print(' '.join(map(str, arr)))
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
        long[] a = new long[n];
        for (int i = 0; i < n; i++) a[i] = Long.parseLong(st.nextToken());

        List<long[]> ops = new ArrayList<>();

        for (int k = 0; k < n / 2; k++) {
            boolean sorted = true;
            for (int i = 0; i < n - 1; i++) {
                if (a[i] < a[i + 1]) {
                    sorted = false;
                    break;
                }
            }
            if (sorted) break;

            long maxVal = a[0];
            for (int i = 1; i < n; i++) maxVal = Math.max(maxVal, a[i]);

            long diff = maxVal - a[0] + 1;
            a[0] += diff;
            a[n - 1] -= diff;
            ops.add(a.clone());
        }

        boolean sorted = true;
        for (int i = 0; i < n - 1; i++) {
            if (a[i] < a[i + 1]) {
                sorted = false;
                break;
            }
        }

        if (!sorted) {
            System.out.println(-1);
        } else {
            System.out.println(ops.size());
            StringBuilder sb = new StringBuilder();
            for (long[] arr : ops) {
                for (int i = 0; i < n; i++) {
                    if (i > 0) sb.append(" ");
                    sb.append(arr[i]);
                }
                sb.append("\\n");
            }
            System.out.print(sb);
        }
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
    int n;
    cin >> n;
    vector<long long> a(n);
    for (int i = 0; i < n; i++) cin >> a[i];

    vector<vector<long long>> ops;

    for (int k = 0; k < n / 2; k++) {
        bool sorted = true;
        for (int i = 0; i < n - 1; i++) {
            if (a[i] < a[i + 1]) {
                sorted = false;
                break;
            }
        }
        if (sorted) break;

        long long maxVal = *max_element(a.begin(), a.end());
        long long diff = maxVal - a[0] + 1;
        a[0] += diff;
        a[n - 1] -= diff;
        ops.push_back(a);
    }

    bool sorted = true;
    for (int i = 0; i < n - 1; i++) {
        if (a[i] < a[i + 1]) {
            sorted = false;
            break;
        }
    }

    if (!sorted) {
        cout << -1 << endl;
    } else {
        cout << ops.size() << endl;
        for (auto& arr : ops) {
            for (int i = 0; i < n; i++) {
                if (i > 0) cout << " ";
                cout << arr[i];
            }
            cout << "\\n";
        }
    }
    return 0;
}
'''
        }
    ]

    # Problem 417: baekjoon_17508 - 6789
    solutions[6279] = [
        {
            "language": "python",
            "code": '''# 6789 - 점대칭 매트릭스
import sys
input = sys.stdin.readline

n, m = map(int, input().split())
grid = []
for _ in range(n):
    grid.append(list(input().strip()))

# 점대칭: grid[i][j]와 grid[n-1-i][m-1-j]가 대칭
# 6 <-> 9, 8 <-> 8, 7 <-> 7 (불가능)

count = 0
possible = True

for i in range(n):
    for j in range(m):
        ni, nj = n - 1 - i, m - 1 - j
        if (i, j) >= (ni, nj):
            continue

        a, b = grid[i][j], grid[ni][nj]

        # 둘 다 회전해서 맞출 수 있는지
        def get_rotated(c):
            if c == '6':
                return '9'
            elif c == '9':
                return '6'
            elif c == '8':
                return '8'
            else:  # 7
                return None

        ra, rb = get_rotated(a), get_rotated(b)

        if ra is None or rb is None:
            # 7이 있으면 대칭 불가
            possible = False
            break

        # 맞출 수 있는 경우의 수
        # a -> ra 또는 a 유지, b -> rb 또는 b 유지
        # 대칭이 되려면: (a 유지, b 회전 -> rb==a) or (a 회전, b 유지 -> ra==b)

        matches = 0
        if a == rb:
            matches += 1  # a 유지, b 회전
        if ra == b:
            matches += 1  # a 회전, b 유지

        if matches == 0:
            possible = False
            break
        elif matches == 1:
            count += 1

    if not possible:
        break

# 홀수 위치 (가운데)
if possible and n % 2 == 1 and m % 2 == 1:
    center = grid[n // 2][m // 2]
    if center == '7':
        possible = False
    # 8은 그대로, 6/9는 회전 필요

if possible:
    print(count)
else:
    print(-1)
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
        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());

        char[][] grid = new char[n][m];
        for (int i = 0; i < n; i++) {
            grid[i] = br.readLine().toCharArray();
        }

        int count = 0;
        boolean possible = true;

        outer:
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                int ni = n - 1 - i, nj = m - 1 - j;
                if (i * m + j >= ni * m + nj) continue;

                char a = grid[i][j], b = grid[ni][nj];
                char ra = getRotated(a), rb = getRotated(b);

                if (ra == 0 || rb == 0) {
                    possible = false;
                    break outer;
                }

                int matches = 0;
                if (a == rb) matches++;
                if (ra == b) matches++;

                if (matches == 0) {
                    possible = false;
                    break outer;
                } else if (matches == 1) {
                    count++;
                }
            }
        }

        if (possible && n % 2 == 1 && m % 2 == 1) {
            if (grid[n / 2][m / 2] == '7') possible = false;
        }

        System.out.println(possible ? count : -1);
    }

    static char getRotated(char c) {
        if (c == '6') return '9';
        if (c == '9') return '6';
        if (c == '8') return '8';
        return 0;
    }
}
'''
        },
        {
            "language": "cpp",
            "code": '''#include <iostream>
#include <string>
using namespace std;

char getRotated(char c) {
    if (c == '6') return '9';
    if (c == '9') return '6';
    if (c == '8') return '8';
    return 0;
}

int main() {
    int n, m;
    cin >> n >> m;

    string grid[n];
    for (int i = 0; i < n; i++) cin >> grid[i];

    int count = 0;
    bool possible = true;

    for (int i = 0; i < n && possible; i++) {
        for (int j = 0; j < m && possible; j++) {
            int ni = n - 1 - i, nj = m - 1 - j;
            if (i * m + j >= ni * m + nj) continue;

            char a = grid[i][j], b = grid[ni][nj];
            char ra = getRotated(a), rb = getRotated(b);

            if (ra == 0 || rb == 0) {
                possible = false;
                break;
            }

            int matches = 0;
            if (a == rb) matches++;
            if (ra == b) matches++;

            if (matches == 0) possible = false;
            else if (matches == 1) count++;
        }
    }

    if (possible && n % 2 == 1 && m % 2 == 1) {
        if (grid[n / 2][m / 2] == '7') possible = false;
    }

    cout << (possible ? count : -1) << endl;
    return 0;
}
'''
        }
    ]

    # Problem 418: baekjoon_2949 - 45도
    solutions[6280] = [
        {
            "language": "python",
            "code": '''# 45도 - 표 회전
import sys
input = sys.stdin.readline

r, c = map(int, input().split())
grid = []
for _ in range(r):
    grid.append(input().strip())

k = int(input())

def rotate_45(grid, r, c):
    """45도 시계방향 회전"""
    # 대각선 방향으로 출력
    result = []
    for d in range(r + c - 1):
        row = ""
        for i in range(r):
            j = d - i
            if 0 <= j < c:
                row += grid[i][j]
            else:
                row += " "
        # 공백 정리
        row = row.rstrip()
        if row or d < r + c - 2:
            result.append(row)
    return result

def rotate_90(grid, r, c):
    """90도 시계방향 회전"""
    result = []
    for j in range(c):
        row = ""
        for i in range(r - 1, -1, -1):
            row += grid[i][j]
        result.append(row)
    return result, c, r

# k를 45의 배수로 처리
k = k % 360

if k == 0:
    for row in grid:
        print(row)
elif k == 45:
    result = rotate_45(grid, r, c)
    for row in result:
        print(row)
elif k == 90:
    result, nr, nc = rotate_90(grid, r, c)
    for row in result:
        print(row)
elif k == 135:
    g90, nr, nc = rotate_90(grid, r, c)
    result = rotate_45(g90, nr, nc)
    for row in result:
        print(row)
elif k == 180:
    g90, nr, nc = rotate_90(grid, r, c)
    g180, nr, nc = rotate_90(g90, nr, nc)
    for row in g180:
        print(row)
elif k == 225:
    g90, nr, nc = rotate_90(grid, r, c)
    g180, nr, nc = rotate_90(g90, nr, nc)
    result = rotate_45(g180, nr, nc)
    for row in result:
        print(row)
elif k == 270:
    g90, nr, nc = rotate_90(grid, r, c)
    g180, nr, nc = rotate_90(g90, nr, nc)
    g270, nr, nc = rotate_90(g180, nr, nc)
    for row in g270:
        print(row)
elif k == 315:
    g90, nr, nc = rotate_90(grid, r, c)
    g180, nr, nc = rotate_90(g90, nr, nc)
    g270, nr, nc = rotate_90(g180, nr, nc)
    result = rotate_45(g270, nr, nc)
    for row in result:
        print(row)
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
        int r = Integer.parseInt(st.nextToken());
        int c = Integer.parseInt(st.nextToken());

        String[] grid = new String[r];
        for (int i = 0; i < r; i++) {
            grid[i] = br.readLine();
            while (grid[i].length() < c) grid[i] += " ";
        }

        int k = Integer.parseInt(br.readLine().trim()) % 360;

        // 90도 회전
        int rotations = k / 90;
        for (int t = 0; t < rotations; t++) {
            String[] newGrid = new String[c];
            for (int j = 0; j < c; j++) {
                StringBuilder sb = new StringBuilder();
                for (int i = r - 1; i >= 0; i--) {
                    sb.append(grid[i].charAt(j));
                }
                newGrid[j] = sb.toString();
            }
            grid = newGrid;
            int temp = r; r = c; c = temp;
        }

        // 45도 회전 필요한 경우
        if (k % 90 == 45) {
            List<String> result = new ArrayList<>();
            for (int d = 0; d < r + c - 1; d++) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < r; i++) {
                    int j = d - i;
                    if (j >= 0 && j < c) sb.append(grid[i].charAt(j));
                    else sb.append(' ');
                }
                String row = sb.toString();
                while (row.endsWith(" ")) row = row.substring(0, row.length() - 1);
                result.add(row);
            }
            for (String row : result) System.out.println(row);
        } else {
            for (int i = 0; i < r; i++) {
                String row = grid[i];
                while (row.endsWith(" ")) row = row.substring(0, row.length() - 1);
                System.out.println(row);
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
#include <string>
using namespace std;

int main() {
    int r, c;
    cin >> r >> c;

    vector<string> grid(r);
    for (int i = 0; i < r; i++) {
        cin >> grid[i];
        while ((int)grid[i].length() < c) grid[i] += ' ';
    }

    int k;
    cin >> k;
    k %= 360;

    int rotations = k / 90;
    for (int t = 0; t < rotations; t++) {
        vector<string> newGrid(c);
        for (int j = 0; j < c; j++) {
            string row = "";
            for (int i = r - 1; i >= 0; i--) {
                row += grid[i][j];
            }
            newGrid[j] = row;
        }
        grid = newGrid;
        swap(r, c);
    }

    if (k % 90 == 45) {
        for (int d = 0; d < r + c - 1; d++) {
            string row = "";
            for (int i = 0; i < r; i++) {
                int j = d - i;
                if (j >= 0 && j < c) row += grid[i][j];
                else row += ' ';
            }
            while (!row.empty() && row.back() == ' ') row.pop_back();
            cout << row << "\\n";
        }
    } else {
        for (int i = 0; i < r; i++) {
            string row = grid[i];
            while (!row.empty() && row.back() == ' ') row.pop_back();
            cout << row << "\\n";
        }
    }
    return 0;
}
'''
        }
    ]

    return solutions


def main():
    json_path = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

    print("Reading JSON file...")
    with open(json_path, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    solutions = get_remaining_solutions()
    print(f"Solutions prepared for {len(solutions)} remaining problems")

    updated_count = 0
    for idx, sol_list in solutions.items():
        if idx < len(data):
            data[idx]['solutions'] = sol_list
            updated_count += 1
            print(f"Updated index {idx}: {data[idx].get('name', 'Unknown')}")

    print(f"\nWriting {updated_count} solutions to JSON file...")
    with open(json_path, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    print(f"Done! Updated {updated_count} more problems.")


if __name__ == '__main__':
    main()
