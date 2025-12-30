#!/usr/bin/env python3
"""Batch 14: 15개 Medium 문제 솔루션 추가"""
import json

new_solutions = {
    "baekjoon_23306": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys

def solve():
    n = int(input())
    # 로그 N번 질문으로 첫 번째 비트와 마지막 비트 확인
    # 오르막(01)과 내리막(10) 개수 비교

    # 첫 번째 위치 질문
    print("? 1", flush=True)
    first = int(input())

    # 마지막 위치 질문
    print(f"? {n}", flush=True)
    last = int(input())

    # 첫 비트가 0이고 마지막이 1이면 오르막이 더 많을 가능성
    # 첫 비트가 1이고 마지막이 0이면 내리막이 더 많을 가능성
    if first < last:
        print("! 1", flush=True)
    elif first > last:
        print("! -1", flush=True)
    else:
        print("! 0", flush=True)

solve()
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

    // 첫 번째 위치 질문
    cout << "? 1" << endl;
    int first;
    cin >> first;

    // 마지막 위치 질문
    cout << "? " << n << endl;
    int last;
    cin >> last;

    // 오르막과 내리막 비교
    if (first < last) {
        cout << "! 1" << endl;
    } else if (first > last) {
        cout << "! -1" << endl;
    } else {
        cout << "! 0" << endl;
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(System.out)));

        int n = Integer.parseInt(br.readLine().trim());

        // 첫 번째 위치 질문
        out.println("? 1");
        out.flush();
        int first = Integer.parseInt(br.readLine().trim());

        // 마지막 위치 질문
        out.println("? " + n);
        out.flush();
        int last = Integer.parseInt(br.readLine().trim());

        // 오르막과 내리막 비교
        if (first < last) {
            out.println("! 1");
        } else if (first > last) {
            out.println("! -1");
        } else {
            out.println("! 0");
        }
        out.flush();
    }
}
'''
            }
        ]
    },
    "baekjoon_4884": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

while True:
    line = input().split()
    G, T, A, D = map(int, line)

    if G == -1 and T == -1 and A == -1 and D == -1:
        break

    # 조별 리그 경기 수: 각 조에서 T팀이 서로 한 번씩 = T*(T-1)/2, 총 G개 조
    group_matches = G * (T * (T - 1) // 2)

    # 토너먼트 진출 팀 수
    tournament_teams = G * A + D

    # 2의 제곱으로 올림
    power = 1
    while power < tournament_teams:
        power *= 2

    # 추가해야 하는 팀 수
    extra_teams = power - tournament_teams

    # 토너먼트 경기 수 (단판 토너먼트: 팀 수 - 1)
    tournament_matches = power - 1

    # 총 경기 수
    total_matches = group_matches + tournament_matches

    print(f"{G}*{A}/{T}+{D}={total_matches}+{extra_teams}")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long G, T, A, D;
    while (cin >> G >> T >> A >> D) {
        if (G == -1 && T == -1 && A == -1 && D == -1) break;

        // 조별 리그 경기 수
        long long group_matches = G * (T * (T - 1) / 2);

        // 토너먼트 진출 팀 수
        long long tournament_teams = G * A + D;

        // 2의 제곱으로 올림
        long long power = 1;
        while (power < tournament_teams) {
            power *= 2;
        }

        // 추가 팀 수와 토너먼트 경기 수
        long long extra_teams = power - tournament_teams;
        long long tournament_matches = power - 1;
        long long total_matches = group_matches + tournament_matches;

        cout << G << "*" << A << "/" << T << "+" << D << "="
             << total_matches << "+" << extra_teams << endl;
    }

    return 0;
}
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

        String line;
        while ((line = br.readLine()) != null) {
            StringTokenizer st = new StringTokenizer(line);
            long G = Long.parseLong(st.nextToken());
            long T = Long.parseLong(st.nextToken());
            long A = Long.parseLong(st.nextToken());
            long D = Long.parseLong(st.nextToken());

            if (G == -1 && T == -1 && A == -1 && D == -1) break;

            // 조별 리그 경기 수
            long groupMatches = G * (T * (T - 1) / 2);

            // 토너먼트 진출 팀 수
            long tournamentTeams = G * A + D;

            // 2의 제곱으로 올림
            long power = 1;
            while (power < tournamentTeams) {
                power *= 2;
            }

            long extraTeams = power - tournamentTeams;
            long tournamentMatches = power - 1;
            long totalMatches = groupMatches + tournamentMatches;

            sb.append(G).append("*").append(A).append("/").append(T)
              .append("+").append(D).append("=").append(totalMatches)
              .append("+").append(extraTeams).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_26265": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
pairs = []
for _ in range(n):
    mentor, mentee = input().split()
    pairs.append((mentor, mentee))

# 멘토 기준 사전순, 같은 멘토면 멘티 사전 역순
pairs.sort(key=lambda x: (x[0], x[1]), reverse=False)
pairs.sort(key=lambda x: x[0])

# 같은 멘토 그룹 내에서 멘티 역순 정렬
from itertools import groupby
result = []
for mentor, group in groupby(pairs, key=lambda x: x[0]):
    group_list = list(group)
    group_list.sort(key=lambda x: x[1], reverse=True)
    result.extend(group_list)

for mentor, mentee in result:
    print(mentor, mentee)
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
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<pair<string, string>> pairs(n);
    for (int i = 0; i < n; i++) {
        cin >> pairs[i].first >> pairs[i].second;
    }

    // 멘토 사전순, 멘티 사전 역순
    sort(pairs.begin(), pairs.end(), [](const auto& a, const auto& b) {
        if (a.first != b.first) return a.first < b.first;
        return a.second > b.second;  // 멘티는 역순
    });

    for (const auto& p : pairs) {
        cout << p.first << " " << p.second << "\\n";
    }

    return 0;
}
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

        String[][] pairs = new String[n][2];
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            pairs[i][0] = st.nextToken();  // 멘토
            pairs[i][1] = st.nextToken();  // 멘티
        }

        // 멘토 사전순, 멘티 사전 역순
        Arrays.sort(pairs, (a, b) -> {
            int cmp = a[0].compareTo(b[0]);
            if (cmp != 0) return cmp;
            return b[1].compareTo(a[1]);  // 멘티는 역순
        });

        StringBuilder sb = new StringBuilder();
        for (String[] pair : pairs) {
            sb.append(pair[0]).append(" ").append(pair[1]).append("\\n");
        }
        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_3018": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
e = int(input())

# 각 사람이 아는 노래 집합
songs = [set() for _ in range(n + 1)]
song_count = 0  # 총 노래 수

for day in range(e):
    line = list(map(int, input().split()))
    k = line[0]
    participants = line[1:k+1]

    if 1 in participants:  # 선영이가 참가하면 새 노래
        song_count += 1
        for p in participants:
            songs[p].add(song_count)
    else:  # 선영이가 없으면 노래 공유
        shared = set()
        for p in participants:
            shared = shared.union(songs[p])
        for p in participants:
            songs[p] = songs[p].union(shared)

# 모든 노래를 아는 사람 찾기
all_songs = set(range(1, song_count + 1))
for i in range(1, n + 1):
    if songs[i] == all_songs:
        print(i)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <set>
#include <vector>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, e;
    cin >> n >> e;

    vector<set<int>> songs(n + 1);
    int songCount = 0;

    for (int day = 0; day < e; day++) {
        int k;
        cin >> k;
        vector<int> participants(k);
        bool sunyoung = false;

        for (int i = 0; i < k; i++) {
            cin >> participants[i];
            if (participants[i] == 1) sunyoung = true;
        }

        if (sunyoung) {
            // 선영이가 참가: 새 노래 생성
            songCount++;
            for (int p : participants) {
                songs[p].insert(songCount);
            }
        } else {
            // 선영이 없음: 노래 공유
            set<int> shared;
            for (int p : participants) {
                shared.insert(songs[p].begin(), songs[p].end());
            }
            for (int p : participants) {
                songs[p].insert(shared.begin(), shared.end());
            }
        }
    }

    // 모든 노래를 아는 사람 출력
    for (int i = 1; i <= n; i++) {
        if ((int)songs[i].size() == songCount) {
            cout << i << "\\n";
        }
    }

    return 0;
}
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
        int e = Integer.parseInt(br.readLine().trim());

        Set<Integer>[] songs = new HashSet[n + 1];
        for (int i = 0; i <= n; i++) {
            songs[i] = new HashSet<>();
        }

        int songCount = 0;

        for (int day = 0; day < e; day++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int k = Integer.parseInt(st.nextToken());
            int[] participants = new int[k];
            boolean sunyoung = false;

            for (int i = 0; i < k; i++) {
                participants[i] = Integer.parseInt(st.nextToken());
                if (participants[i] == 1) sunyoung = true;
            }

            if (sunyoung) {
                songCount++;
                for (int p : participants) {
                    songs[p].add(songCount);
                }
            } else {
                Set<Integer> shared = new HashSet<>();
                for (int p : participants) {
                    shared.addAll(songs[p]);
                }
                for (int p : participants) {
                    songs[p].addAll(shared);
                }
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= n; i++) {
            if (songs[i].size() == songCount) {
                sb.append(i).append("\\n");
            }
        }
        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_15595": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())

# 각 사용자별 정보 저장
user_data = {}  # user_id -> [맞았는지, 맞기 전 틀린 횟수]

for _ in range(n):
    parts = input().split()
    user_id = parts[1]
    result = int(parts[2])

    if user_id == "megalusion":  # 관리자 제외
        continue

    if user_id not in user_data:
        user_data[user_id] = [False, 0]

    if user_data[user_id][0]:  # 이미 맞은 사람은 무시
        continue

    if result == 4:  # 맞았습니다
        user_data[user_id][0] = True
    else:
        user_data[user_id][1] += 1

# 정답 비율 계산
correct_count = 0
wrong_before_correct = 0

for user_id, (solved, wrong) in user_data.items():
    if solved:
        correct_count += 1
        wrong_before_correct += wrong

if correct_count == 0:
    print(0)
else:
    ratio = correct_count / (correct_count + wrong_before_correct) * 100
    print(ratio)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <map>
#include <iomanip>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    map<string, pair<bool, int>> userData;  // 맞았는지, 틀린 횟수

    for (int i = 0; i < n; i++) {
        long long submitId;
        string userId;
        int result, mem, time, lang, len;
        cin >> submitId >> userId >> result >> mem >> time >> lang >> len;

        if (userId == "megalusion") continue;  // 관리자 제외

        if (userData.find(userId) == userData.end()) {
            userData[userId] = {false, 0};
        }

        if (userData[userId].first) continue;  // 이미 맞은 사람

        if (result == 4) {
            userData[userId].first = true;
        } else {
            userData[userId].second++;
        }
    }

    int correctCount = 0;
    int wrongBeforeCorrect = 0;

    for (auto& p : userData) {
        if (p.second.first) {
            correctCount++;
            wrongBeforeCorrect += p.second.second;
        }
    }

    cout << fixed << setprecision(20);
    if (correctCount == 0) {
        cout << 0 << endl;
    } else {
        double ratio = (double)correctCount / (correctCount + wrongBeforeCorrect) * 100.0;
        cout << ratio << endl;
    }

    return 0;
}
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

        // 맞았는지, 맞기 전 틀린 횟수
        Map<String, int[]> userData = new HashMap<>();

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            st.nextToken();  // submitId
            String userId = st.nextToken();
            int result = Integer.parseInt(st.nextToken());

            if (userId.equals("megalusion")) continue;  // 관리자 제외

            if (!userData.containsKey(userId)) {
                userData.put(userId, new int[]{0, 0});  // solved, wrongCount
            }

            int[] data = userData.get(userId);
            if (data[0] == 1) continue;  // 이미 맞은 사람

            if (result == 4) {
                data[0] = 1;
            } else {
                data[1]++;
            }
        }

        int correctCount = 0;
        int wrongBeforeCorrect = 0;

        for (int[] data : userData.values()) {
            if (data[0] == 1) {
                correctCount++;
                wrongBeforeCorrect += data[1];
            }
        }

        if (correctCount == 0) {
            System.out.println(0);
        } else {
            double ratio = (double) correctCount / (correctCount + wrongBeforeCorrect) * 100.0;
            System.out.println(ratio);
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_15779": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
a = list(map(int, input().split()))

if n <= 2:
    print(n)
else:
    max_len = 2
    curr_len = 2

    for i in range(2, n):
        # 연속 3개가 단조증가 또는 단조감소인지 확인
        if (a[i-2] <= a[i-1] <= a[i]) or (a[i-2] >= a[i-1] >= a[i]):
            # 지그재그가 아님, 새로 시작
            curr_len = 2
        else:
            curr_len += 1
        max_len = max(max_len, curr_len)

    print(max_len)
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

    int* a = new int[n];
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    if (n <= 2) {
        cout << n << endl;
        delete[] a;
        return 0;
    }

    int maxLen = 2;
    int currLen = 2;

    for (int i = 2; i < n; i++) {
        // 연속 3개가 단조증가 또는 단조감소인지 확인
        if ((a[i-2] <= a[i-1] && a[i-1] <= a[i]) ||
            (a[i-2] >= a[i-1] && a[i-1] >= a[i])) {
            currLen = 2;
        } else {
            currLen++;
        }
        maxLen = max(maxLen, currLen);
    }

    cout << maxLen << endl;
    delete[] a;
    return 0;
}
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
        int[] a = new int[n];
        for (int i = 0; i < n; i++) {
            a[i] = Integer.parseInt(st.nextToken());
        }

        if (n <= 2) {
            System.out.println(n);
            return;
        }

        int maxLen = 2;
        int currLen = 2;

        for (int i = 2; i < n; i++) {
            // 연속 3개가 단조증가 또는 단조감소인지 확인
            if ((a[i-2] <= a[i-1] && a[i-1] <= a[i]) ||
                (a[i-2] >= a[i-1] && a[i-1] >= a[i])) {
                currLen = 2;
            } else {
                currLen++;
            }
            maxLen = Math.max(maxLen, currLen);
        }

        System.out.println(maxLen);
    }
}
'''
            }
        ]
    },
    "baekjoon_3088": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from collections import defaultdict
input = sys.stdin.readline

n = int(input())
pots = []
num_to_pots = defaultdict(list)  # 숫자 -> 해당 숫자를 가진 화분 인덱스

for i in range(n):
    a, b, c = map(int, input().split())
    pots.append({a, b, c})
    num_to_pots[a].append(i)
    num_to_pots[b].append(i)
    num_to_pots[c].append(i)

# 각 화분에서 시작해서 오른쪽으로 몇 번째까지 연쇄가 가능한지 계산
# reach[i] = i번 화분을 깨면 연쇄적으로 깨지는 가장 오른쪽 화분 인덱스

def find_reach(start):
    """start 화분을 깨면 연쇄적으로 깨지는 가장 오른쪽 인덱스"""
    reach = start
    changed = True
    while changed:
        changed = False
        new_reach = reach
        for i in range(start, reach + 1):
            for num in pots[i]:
                for pot_idx in num_to_pots[num]:
                    if pot_idx > reach:
                        new_reach = max(new_reach, pot_idx)
                        changed = True
        reach = new_reach
    return reach

# 그리디: 왼쪽부터 깨면서 가장 멀리 연쇄되는 것 선택
count = 0
current = 0
while current < n:
    count += 1
    reach = find_reach(current)
    current = reach + 1

print(count)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <set>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<set<int>> pots(n);
    map<int, vector<int>> numToPots;

    for (int i = 0; i < n; i++) {
        int a, b, c;
        cin >> a >> b >> c;
        pots[i].insert(a);
        pots[i].insert(b);
        pots[i].insert(c);
        numToPots[a].push_back(i);
        numToPots[b].push_back(i);
        numToPots[c].push_back(i);
    }

    // 그리디: 왼쪽부터 연쇄 계산
    int count = 0;
    int current = 0;

    while (current < n) {
        count++;
        int reach = current;
        bool changed = true;

        while (changed) {
            changed = false;
            int newReach = reach;
            for (int i = current; i <= reach; i++) {
                for (int num : pots[i]) {
                    for (int potIdx : numToPots[num]) {
                        if (potIdx > reach) {
                            newReach = max(newReach, potIdx);
                            changed = true;
                        }
                    }
                }
            }
            reach = newReach;
        }
        current = reach + 1;
    }

    cout << count << endl;
    return 0;
}
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

        Set<Integer>[] pots = new HashSet[n];
        Map<Integer, List<Integer>> numToPots = new HashMap<>();

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int a = Integer.parseInt(st.nextToken());
            int b = Integer.parseInt(st.nextToken());
            int c = Integer.parseInt(st.nextToken());

            pots[i] = new HashSet<>();
            pots[i].add(a);
            pots[i].add(b);
            pots[i].add(c);

            numToPots.computeIfAbsent(a, k -> new ArrayList<>()).add(i);
            numToPots.computeIfAbsent(b, k -> new ArrayList<>()).add(i);
            numToPots.computeIfAbsent(c, k -> new ArrayList<>()).add(i);
        }

        int count = 0;
        int current = 0;

        while (current < n) {
            count++;
            int reach = current;
            boolean changed = true;

            while (changed) {
                changed = false;
                int newReach = reach;
                for (int i = current; i <= reach; i++) {
                    for (int num : pots[i]) {
                        List<Integer> potList = numToPots.get(num);
                        if (potList != null) {
                            for (int potIdx : potList) {
                                if (potIdx > reach) {
                                    newReach = Math.max(newReach, potIdx);
                                    changed = true;
                                }
                            }
                        }
                    }
                }
                reach = newReach;
            }
            current = reach + 1;
        }

        System.out.println(count);
    }
}
'''
            }
        ]
    },
    "baekjoon_12787": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    line = input().split()
    m = int(line[0])
    val = line[1]

    if m == 1:
        # IPv8 주소를 정수로 변환
        parts = list(map(int, val.split('.')))
        result = 0
        for p in parts:
            result = result * 256 + p
        print(result)
    else:
        # 정수를 IPv8 주소로 변환
        n = int(val)
        parts = []
        for _ in range(8):
            parts.append(n % 256)
            n //= 256
        parts.reverse()
        print('.'.join(map(str, parts)))
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <string>
#include <vector>
#include <sstream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        int m;
        string val;
        cin >> m >> val;

        if (m == 1) {
            // IPv8 주소를 정수로 변환
            unsigned long long result = 0;
            stringstream ss(val);
            string token;
            while (getline(ss, token, '.')) {
                result = result * 256 + stoi(token);
            }
            cout << result << "\\n";
        } else {
            // 정수를 IPv8 주소로 변환
            unsigned long long n = stoull(val);
            vector<int> parts(8);
            for (int i = 7; i >= 0; i--) {
                parts[i] = n % 256;
                n /= 256;
            }
            for (int i = 0; i < 8; i++) {
                if (i > 0) cout << ".";
                cout << parts[i];
            }
            cout << "\\n";
        }
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.math.BigInteger;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int m = Integer.parseInt(st.nextToken());
            String val = st.nextToken();

            if (m == 1) {
                // IPv8 주소를 정수로 변환
                String[] parts = val.split("\\\\.");
                BigInteger result = BigInteger.ZERO;
                BigInteger base = BigInteger.valueOf(256);
                for (String part : parts) {
                    result = result.multiply(base).add(new BigInteger(part));
                }
                sb.append(result).append("\\n");
            } else {
                // 정수를 IPv8 주소로 변환
                BigInteger n = new BigInteger(val);
                BigInteger base = BigInteger.valueOf(256);
                int[] parts = new int[8];
                for (int i = 7; i >= 0; i--) {
                    parts[i] = n.mod(base).intValue();
                    n = n.divide(base);
                }
                for (int i = 0; i < 8; i++) {
                    if (i > 0) sb.append(".");
                    sb.append(parts[i]);
                }
                sb.append("\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_15916": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
y = [0] + list(map(int, input().split()))  # y[0] = 0, y[1..n]
k = int(input())

# y = kx 직선과 f(x) 함수가 (0,0) 외에 만나는지 확인
# 각 구간 [i-1, i]에서 선분의 양 끝점이 y = kx 직선의 위아래에 있는지 확인

for i in range(1, n + 1):
    # 점 (i-1, y[i-1])과 (i, y[i])를 잇는 선분
    # y = kx 직선과의 관계
    # 점 (x, y)가 y = kx 직선 위: y = kx
    # 점 (x, y)가 y = kx 직선 아래: y < kx
    # 점 (x, y)가 y = kx 직선 위: y > kx

    # (i-1, y[i-1]): y[i-1] - k*(i-1)
    # (i, y[i]): y[i] - k*i

    diff1 = y[i-1] - k * (i - 1)
    diff2 = y[i] - k * i

    # 두 점이 직선의 반대편에 있거나, 끝점이 직선 위에 있으면 만남
    if i > 0:  # (0,0)은 제외
        if diff2 == 0:  # 끝점이 정확히 직선 위
            print("T")
            exit()
        if diff1 * diff2 < 0:  # 부호가 다르면 교차
            print("T")
            exit()

print("F")
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

    long long* y = new long long[n + 1];
    y[0] = 0;
    for (int i = 1; i <= n; i++) {
        cin >> y[i];
    }

    long long k;
    cin >> k;

    for (int i = 1; i <= n; i++) {
        // (i-1, y[i-1])과 (i, y[i])를 잇는 선분
        // y = kx 직선과의 관계 확인

        long long diff1 = y[i-1] - k * (i - 1);
        long long diff2 = y[i] - k * i;

        if (diff2 == 0) {
            // 끝점이 정확히 직선 위
            cout << "T" << endl;
            delete[] y;
            return 0;
        }
        if ((diff1 > 0 && diff2 < 0) || (diff1 < 0 && diff2 > 0)) {
            // 부호가 다르면 교차
            cout << "T" << endl;
            delete[] y;
            return 0;
        }
    }

    cout << "F" << endl;
    delete[] y;
    return 0;
}
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

        long[] y = new long[n + 1];
        y[0] = 0;
        StringTokenizer st = new StringTokenizer(br.readLine());
        for (int i = 1; i <= n; i++) {
            y[i] = Long.parseLong(st.nextToken());
        }

        long k = Long.parseLong(br.readLine().trim());

        for (int i = 1; i <= n; i++) {
            long diff1 = y[i-1] - k * (i - 1);
            long diff2 = y[i] - k * i;

            if (diff2 == 0) {
                System.out.println("T");
                return;
            }
            if ((diff1 > 0 && diff2 < 0) || (diff1 < 0 && diff2 > 0)) {
                System.out.println("T");
                return;
            }
        }

        System.out.println("F");
    }
}
'''
            }
        ]
    },
    "baekjoon_1821": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
from itertools import permutations

def calculate_sum(arr):
    """파스칼 삼각형 방식으로 최종 합 계산"""
    n = len(arr)
    # 이항계수 활용: 최종 합 = sum(C(n-1, i) * arr[i])
    # C(n-1, 0)*a[0] + C(n-1,1)*a[1] + ... + C(n-1,n-1)*a[n-1]
    result = 0
    c = 1
    for i in range(n):
        result += c * arr[i]
        c = c * (n - 1 - i) // (i + 1)
    return result

n, f = map(int, input().split())

# 1부터 N까지 순열을 사전순으로 확인
for perm in permutations(range(1, n + 1)):
    if calculate_sum(perm) == f:
        print(' '.join(map(str, perm)))
        break
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <algorithm>
#include <vector>
using namespace std;

int binom[11][11];

void calcBinom() {
    for (int i = 0; i <= 10; i++) {
        binom[i][0] = binom[i][i] = 1;
        for (int j = 1; j < i; j++) {
            binom[i][j] = binom[i-1][j-1] + binom[i-1][j];
        }
    }
}

int calculateSum(vector<int>& arr, int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += binom[n-1][i] * arr[i];
    }
    return result;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    calcBinom();

    int n, f;
    cin >> n >> f;

    vector<int> perm(n);
    for (int i = 0; i < n; i++) {
        perm[i] = i + 1;
    }

    do {
        if (calculateSum(perm, n) == f) {
            for (int i = 0; i < n; i++) {
                if (i > 0) cout << " ";
                cout << perm[i];
            }
            cout << endl;
            break;
        }
    } while (next_permutation(perm.begin(), perm.end()));

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static int[][] binom = new int[11][11];
    static int n, f;
    static int[] perm;
    static boolean[] used;
    static boolean found = false;

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());
        n = Integer.parseInt(st.nextToken());
        f = Integer.parseInt(st.nextToken());

        // 이항계수 계산
        for (int i = 0; i <= 10; i++) {
            binom[i][0] = binom[i][i] = 1;
            for (int j = 1; j < i; j++) {
                binom[i][j] = binom[i-1][j-1] + binom[i-1][j];
            }
        }

        perm = new int[n];
        used = new boolean[n + 1];

        solve(0);
    }

    static void solve(int idx) {
        if (found) return;

        if (idx == n) {
            int sum = 0;
            for (int i = 0; i < n; i++) {
                sum += binom[n-1][i] * perm[i];
            }
            if (sum == f) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < n; i++) {
                    if (i > 0) sb.append(" ");
                    sb.append(perm[i]);
                }
                System.out.println(sb);
                found = true;
            }
            return;
        }

        for (int i = 1; i <= n; i++) {
            if (!used[i]) {
                used[i] = true;
                perm[idx] = i;
                solve(idx + 1);
                used[i] = false;
            }
        }
    }
}
'''
            }
        ]
    },
    "baekjoon_29891": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n, k = map(int, input().split())
checkpoints = []
for _ in range(n):
    checkpoints.append(int(input()))

# 양수와 음수 체크포인트 분리
positive = sorted([x for x in checkpoints if x > 0], reverse=True)
negative = sorted([x for x in checkpoints if x < 0])  # 절댓값 큰 순 (음수라 정렬하면 작은 값부터)

# 각 방향에서 k개씩 묶어서 처리
# 한 번에 k개 체크 가능, 가장 먼 곳까지 갔다가 돌아옴

def calculate_distance(points, k):
    """한 방향의 점들을 k개씩 묶어서 왕복 거리 계산"""
    if not points:
        return 0
    total = 0
    for i in range(0, len(points), k):
        # i번째부터 k개, 가장 먼 곳까지 왕복
        total += 2 * abs(points[i])
    return total

result = calculate_distance(positive, k) + calculate_distance(negative, k)
print(result)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k;
    cin >> n >> k;

    vector<long long> positive, negative;

    for (int i = 0; i < n; i++) {
        long long x;
        cin >> x;
        if (x > 0) positive.push_back(x);
        else negative.push_back(-x);  // 절댓값으로 저장
    }

    // 내림차순 정렬 (가장 먼 것부터)
    sort(positive.rbegin(), positive.rend());
    sort(negative.rbegin(), negative.rend());

    long long result = 0;

    // 양수 방향
    for (int i = 0; i < (int)positive.size(); i += k) {
        result += 2 * positive[i];
    }

    // 음수 방향
    for (int i = 0; i < (int)negative.size(); i += k) {
        result += 2 * negative[i];
    }

    cout << result << endl;
    return 0;
}
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
        int k = Integer.parseInt(st.nextToken());

        List<Long> positive = new ArrayList<>();
        List<Long> negative = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            long x = Long.parseLong(br.readLine().trim());
            if (x > 0) positive.add(x);
            else negative.add(-x);  // 절댓값
        }

        // 내림차순 정렬
        Collections.sort(positive, Collections.reverseOrder());
        Collections.sort(negative, Collections.reverseOrder());

        long result = 0;

        // 양수 방향
        for (int i = 0; i < positive.size(); i += k) {
            result += 2 * positive.get(i);
        }

        // 음수 방향
        for (int i = 0; i < negative.size(); i += k) {
            result += 2 * negative.get(i);
        }

        System.out.println(result);
    }
}
'''
            }
        ]
    },
    "baekjoon_28292": {
        "solutions": [
            {
                "language": "python",
                "code": '''n = int(input())

# 개미 수열 생성
seq = "1"

for _ in range(n - 1):
    new_seq = ""
    i = 0
    while i < len(seq):
        digit = seq[i]
        count = 1
        while i + count < len(seq) and seq[i + count] == digit:
            count += 1
        new_seq += digit + str(count)
        i += count
    seq = new_seq

# 가장 큰 숫자 찾기
print(max(int(c) for c in seq))
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

    int n;
    cin >> n;

    string seq = "1";

    for (int iter = 1; iter < n; iter++) {
        string newSeq = "";
        int i = 0;
        while (i < (int)seq.length()) {
            char digit = seq[i];
            int count = 1;
            while (i + count < (int)seq.length() && seq[i + count] == digit) {
                count++;
            }
            newSeq += digit;
            newSeq += to_string(count);
            i += count;
        }
        seq = newSeq;
    }

    // 가장 큰 숫자 찾기
    int maxDigit = 0;
    for (char c : seq) {
        maxDigit = max(maxDigit, c - '0');
    }

    cout << maxDigit << endl;
    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());

        String seq = "1";

        for (int iter = 1; iter < n; iter++) {
            StringBuilder newSeq = new StringBuilder();
            int i = 0;
            while (i < seq.length()) {
                char digit = seq.charAt(i);
                int count = 1;
                while (i + count < seq.length() && seq.charAt(i + count) == digit) {
                    count++;
                }
                newSeq.append(digit);
                newSeq.append(count);
                i += count;
            }
            seq = newSeq.toString();
        }

        // 가장 큰 숫자 찾기
        int maxDigit = 0;
        for (int i = 0; i < seq.length(); i++) {
            maxDigit = Math.max(maxDigit, seq.charAt(i) - '0');
        }

        System.out.println(maxDigit);
    }
}
'''
            }
        ]
    },
    "baekjoon_6615": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

def collatz_sequence(n):
    """콜라츠 수열을 생성하고 각 숫자에 도달하는 스텝 수 반환"""
    seq = {n: 0}
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        steps += 1
        if n not in seq:
            seq[n] = steps
    return seq

while True:
    a, b = map(int, input().split())
    if a == 0 and b == 0:
        break

    # A의 콜라츠 수열 생성
    seq_a = collatz_sequence(a)

    # B의 콜라츠 수열을 따라가며 A와 만나는 지점 찾기
    n = b
    steps_b = 0

    while n not in seq_a:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        steps_b += 1

    # 만나는 지점
    c = n
    steps_a = seq_a[c]

    print(f"{a} needs {steps_a} steps, {b} needs {steps_b} steps, they meet at {c}")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <map>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    long long a, b;
    while (cin >> a >> b) {
        if (a == 0 && b == 0) break;

        // A의 콜라츠 수열 생성
        map<long long, int> seqA;
        long long n = a;
        int steps = 0;
        seqA[n] = steps;

        while (n != 1) {
            if (n % 2 == 0) n = n / 2;
            else n = 3 * n + 1;
            steps++;
            if (seqA.find(n) == seqA.end()) {
                seqA[n] = steps;
            }
        }

        // B의 콜라츠 수열을 따라가며 A와 만나는 지점 찾기
        n = b;
        int stepsB = 0;

        while (seqA.find(n) == seqA.end()) {
            if (n % 2 == 0) n = n / 2;
            else n = 3 * n + 1;
            stepsB++;
        }

        long long c = n;
        int stepsA = seqA[c];

        cout << a << " needs " << stepsA << " steps, "
             << b << " needs " << stepsB << " steps, they meet at " << c << endl;
    }

    return 0;
}
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

        String line;
        while ((line = br.readLine()) != null) {
            StringTokenizer st = new StringTokenizer(line);
            long a = Long.parseLong(st.nextToken());
            long b = Long.parseLong(st.nextToken());

            if (a == 0 && b == 0) break;

            // A의 콜라츠 수열 생성
            Map<Long, Integer> seqA = new HashMap<>();
            long n = a;
            int steps = 0;
            seqA.put(n, steps);

            while (n != 1) {
                if (n % 2 == 0) n = n / 2;
                else n = 3 * n + 1;
                steps++;
                if (!seqA.containsKey(n)) {
                    seqA.put(n, steps);
                }
            }

            // B의 콜라츠 수열을 따라가며 A와 만나는 지점 찾기
            n = b;
            int stepsB = 0;

            while (!seqA.containsKey(n)) {
                if (n % 2 == 0) n = n / 2;
                else n = 3 * n + 1;
                stepsB++;
            }

            long c = n;
            int stepsA = seqA.get(c);

            sb.append(a).append(" needs ").append(stepsA).append(" steps, ")
              .append(b).append(" needs ").append(stepsB).append(" steps, they meet at ")
              .append(c).append("\\n");
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    },
    "baekjoon_15788": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
input = sys.stdin.readline

n = int(input())
grid = []
zero_pos = None

for i in range(n):
    row = list(map(int, input().split()))
    grid.append(row)
    for j in range(n):
        if row[j] == 0:
            zero_pos = (i, j)

if zero_pos is None:
    print(-1)
    exit()

row_idx, col_idx = zero_pos

# 각 행의 합 (0이 있는 행 제외)
row_sums = []
for i in range(n):
    if i != row_idx:
        row_sums.append(sum(grid[i]))

# 모든 행 합이 같아야 함
if len(set(row_sums)) > 1:
    print(-1)
    exit()

target_sum = row_sums[0] if row_sums else None

# M 계산: target_sum - (0이 있는 행의 나머지 합)
current_row_sum = sum(grid[row_idx])
m = target_sum - current_row_sum if target_sum else 0

if m <= 0:
    print(-1)
    exit()

# M을 넣고 모든 조건 확인
grid[row_idx][col_idx] = m

# 행 합 확인
for i in range(n):
    if sum(grid[i]) != target_sum:
        print(-1)
        exit()

# 열 합 확인
for j in range(n):
    col_sum = sum(grid[i][j] for i in range(n))
    if col_sum != target_sum:
        print(-1)
        exit()

# 대각선 합 확인
diag1 = sum(grid[i][i] for i in range(n))
diag2 = sum(grid[i][n-1-i] for i in range(n))

if diag1 != target_sum or diag2 != target_sum:
    print(-1)
    exit()

print(m)
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <vector>
#include <set>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n;
    cin >> n;

    vector<vector<long long>> grid(n, vector<long long>(n));
    int zeroRow = -1, zeroCol = -1;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cin >> grid[i][j];
            if (grid[i][j] == 0) {
                zeroRow = i;
                zeroCol = j;
            }
        }
    }

    if (zeroRow == -1) {
        cout << -1 << endl;
        return 0;
    }

    // 각 행의 합 계산 (0이 있는 행 제외)
    set<long long> rowSums;
    for (int i = 0; i < n; i++) {
        if (i != zeroRow) {
            long long sum = 0;
            for (int j = 0; j < n; j++) sum += grid[i][j];
            rowSums.insert(sum);
        }
    }

    if (rowSums.size() > 1) {
        cout << -1 << endl;
        return 0;
    }

    long long targetSum = *rowSums.begin();

    // M 계산
    long long currentRowSum = 0;
    for (int j = 0; j < n; j++) currentRowSum += grid[zeroRow][j];
    long long m = targetSum - currentRowSum;

    if (m <= 0) {
        cout << -1 << endl;
        return 0;
    }

    grid[zeroRow][zeroCol] = m;

    // 모든 조건 확인
    // 열 합
    for (int j = 0; j < n; j++) {
        long long sum = 0;
        for (int i = 0; i < n; i++) sum += grid[i][j];
        if (sum != targetSum) {
            cout << -1 << endl;
            return 0;
        }
    }

    // 대각선
    long long diag1 = 0, diag2 = 0;
    for (int i = 0; i < n; i++) {
        diag1 += grid[i][i];
        diag2 += grid[i][n-1-i];
    }

    if (diag1 != targetSum || diag2 != targetSum) {
        cout << -1 << endl;
        return 0;
    }

    cout << m << endl;
    return 0;
}
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

        long[][] grid = new long[n][n];
        int zeroRow = -1, zeroCol = -1;

        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            for (int j = 0; j < n; j++) {
                grid[i][j] = Long.parseLong(st.nextToken());
                if (grid[i][j] == 0) {
                    zeroRow = i;
                    zeroCol = j;
                }
            }
        }

        if (zeroRow == -1) {
            System.out.println(-1);
            return;
        }

        // 각 행의 합 계산
        Set<Long> rowSums = new HashSet<>();
        for (int i = 0; i < n; i++) {
            if (i != zeroRow) {
                long sum = 0;
                for (int j = 0; j < n; j++) sum += grid[i][j];
                rowSums.add(sum);
            }
        }

        if (rowSums.size() > 1) {
            System.out.println(-1);
            return;
        }

        long targetSum = rowSums.iterator().next();

        // M 계산
        long currentRowSum = 0;
        for (int j = 0; j < n; j++) currentRowSum += grid[zeroRow][j];
        long m = targetSum - currentRowSum;

        if (m <= 0) {
            System.out.println(-1);
            return;
        }

        grid[zeroRow][zeroCol] = m;

        // 열 합 확인
        for (int j = 0; j < n; j++) {
            long sum = 0;
            for (int i = 0; i < n; i++) sum += grid[i][j];
            if (sum != targetSum) {
                System.out.println(-1);
                return;
            }
        }

        // 대각선 확인
        long diag1 = 0, diag2 = 0;
        for (int i = 0; i < n; i++) {
            diag1 += grid[i][i];
            diag2 += grid[i][n-1-i];
        }

        if (diag1 != targetSum || diag2 != targetSum) {
            System.out.println(-1);
            return;
        }

        System.out.println(m);
    }
}
'''
            }
        ]
    },
    "baekjoon_7481": {
        "solutions": [
            {
                "language": "python",
                "code": '''import sys
import math
input = sys.stdin.readline

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    """확장 유클리드 알고리즘: ax + by = gcd(a,b)의 해 (x, y) 반환"""
    if b == 0:
        return a, 1, 0
    g, x, y = extended_gcd(b, a % b)
    return g, y, x - (a // b) * y

t = int(input())
for _ in range(t):
    a, b, s = map(int, input().split())

    g = gcd(a, b)

    if s % g != 0:
        print("Impossible")
        continue

    # ax + by = s의 해 찾기
    # ax + by = g의 해를 찾고, s/g 배
    _, x0, y0 = extended_gcd(a, b)
    x0 *= s // g
    y0 *= s // g

    # 일반해: x = x0 + (b/g)*t, y = y0 - (a/g)*t
    # x >= 0, y >= 0을 만족하는 t 찾기

    step_x = b // g
    step_y = a // g

    # x >= 0: t >= -x0 * g / b = -x0 / step_x
    # y >= 0: t <= y0 * g / a = y0 / step_y

    # t의 범위 계산
    if step_x > 0:
        t_min = math.ceil(-x0 / step_x) if x0 < 0 else math.ceil(-x0 / step_x)
    else:
        t_min = float('-inf')

    if step_y > 0:
        t_max = math.floor(y0 / step_y)
    else:
        t_max = float('inf')

    # x >= 0 조건
    if x0 < 0:
        t_min = max(t_min, math.ceil(-x0 / step_x))

    # y >= 0 조건
    if y0 < 0:
        t_max = min(t_max, math.floor(y0 / step_y))

    # t 범위에서 x + y 최소인 t 찾기
    # x + y = x0 + step_x * t + y0 - step_y * t = (x0 + y0) + (step_x - step_y) * t

    found = False
    min_total = float('inf')
    best_x, best_y = 0, 0

    # t 범위 재계산
    # x = x0 + step_x * t >= 0 => t >= -x0/step_x
    # y = y0 - step_y * t >= 0 => t <= y0/step_y

    t_low = -x0 / step_x if step_x != 0 else float('-inf')
    t_high = y0 / step_y if step_y != 0 else float('inf')

    t_min = math.ceil(t_low) if t_low != float('-inf') else -10**9
    t_max = math.floor(t_high) if t_high != float('inf') else 10**9

    if t_min <= t_max:
        # x + y = (x0 + y0) + (step_x - step_y) * t
        coef = step_x - step_y
        if coef > 0:
            # t가 작을수록 좋음
            t = t_min
        elif coef < 0:
            # t가 클수록 좋음
            t = t_max
        else:
            t = t_min

        x = x0 + step_x * t
        y = y0 - step_y * t

        if x >= 0 and y >= 0:
            print(x, y)
            found = True

    if not found:
        print("Impossible")
'''
            },
            {
                "language": "cpp",
                "code": '''#include <iostream>
#include <cmath>
using namespace std;

long long gcd(long long a, long long b) {
    while (b) {
        long long t = b;
        b = a % b;
        a = t;
    }
    return a;
}

long long extGcd(long long a, long long b, long long& x, long long& y) {
    if (b == 0) {
        x = 1;
        y = 0;
        return a;
    }
    long long x1, y1;
    long long g = extGcd(b, a % b, x1, y1);
    x = y1;
    y = x1 - (a / b) * y1;
    return g;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;

    while (t--) {
        long long a, b, s;
        cin >> a >> b >> s;

        long long g = gcd(a, b);

        if (s % g != 0) {
            cout << "Impossible\\n";
            continue;
        }

        long long x0, y0;
        extGcd(a, b, x0, y0);
        x0 *= s / g;
        y0 *= s / g;

        long long stepX = b / g;
        long long stepY = a / g;

        // t의 범위 계산
        // x = x0 + stepX * t >= 0
        // y = y0 - stepY * t >= 0

        long long tMin, tMax;

        // x >= 0: t >= ceil(-x0 / stepX)
        if (x0 >= 0) {
            tMin = (long long)ceil((double)(-x0) / stepX);
        } else {
            tMin = (long long)ceil((double)(-x0) / stepX);
        }

        // y >= 0: t <= floor(y0 / stepY)
        if (y0 >= 0) {
            tMax = y0 / stepY;
        } else {
            tMax = (y0 - stepY + 1) / stepY;
        }

        if (tMin > tMax) {
            cout << "Impossible\\n";
            continue;
        }

        // x + y 최소화
        long long coef = stepX - stepY;
        long long t;
        if (coef > 0) t = tMin;
        else if (coef < 0) t = tMax;
        else t = tMin;

        long long x = x0 + stepX * t;
        long long y = y0 - stepY * t;

        if (x >= 0 && y >= 0) {
            cout << x << " " << y << "\\n";
        } else {
            cout << "Impossible\\n";
        }
    }

    return 0;
}
'''
            },
            {
                "language": "java",
                "code": '''import java.io.*;
import java.util.*;

public class Main {
    static long gcd(long a, long b) {
        while (b != 0) {
            long t = b;
            b = a % b;
            a = t;
        }
        return a;
    }

    static long[] extGcd(long a, long b) {
        if (b == 0) return new long[]{a, 1, 0};
        long[] result = extGcd(b, a % b);
        return new long[]{result[0], result[2], result[1] - (a / b) * result[2]};
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();

        int t = Integer.parseInt(br.readLine().trim());

        while (t-- > 0) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            long a = Long.parseLong(st.nextToken());
            long b = Long.parseLong(st.nextToken());
            long s = Long.parseLong(st.nextToken());

            long g = gcd(a, b);

            if (s % g != 0) {
                sb.append("Impossible\\n");
                continue;
            }

            long[] result = extGcd(a, b);
            long x0 = result[1] * (s / g);
            long y0 = result[2] * (s / g);

            long stepX = b / g;
            long stepY = a / g;

            // t 범위 계산
            long tMin = (long) Math.ceil((double) (-x0) / stepX);
            long tMax = (long) Math.floor((double) y0 / stepY);

            if (tMin > tMax) {
                sb.append("Impossible\\n");
                continue;
            }

            long coef = stepX - stepY;
            long tt;
            if (coef > 0) tt = tMin;
            else if (coef < 0) tt = tMax;
            else tt = tMin;

            long x = x0 + stepX * tt;
            long y = y0 - stepY * tt;

            if (x >= 0 && y >= 0) {
                sb.append(x).append(" ").append(y).append("\\n");
            } else {
                sb.append("Impossible\\n");
            }
        }

        System.out.print(sb);
    }
}
'''
            }
        ]
    }
}

# 기존 솔루션 로드
with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)

# 새 솔루션 추가
existing.update(new_solutions)

# 저장
with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"총 {len(new_solutions)}개 문제 추가됨")
print(f"현재 총 솔루션 수: {len(existing)}")
