#!/usr/bin/env python3
"""네 번째 배치 솔루션 추가 스크립트"""
import json

# 기존 baek_medium.json 읽기
with open('data/baekjoon/baek_medium.json', 'r', encoding='utf-8') as f:
    medium_data = json.load(f)

print(f"기존 솔루션 수: {len(medium_data)}")

# 새로운 솔루션
new_solutions = {
  "28238": {
    "solutions": [
      {
        "language": "python",
        "code": "# 정보 선생님의 야망 - 주 2회 특강 일정 최적화\nimport sys\nfrom itertools import combinations\ninput = sys.stdin.readline\n\nn = int(input())\nstudents = []\nfor _ in range(n):\n    avail = list(map(int, input().split()))\n    students.append(avail)\n\nbest_count = 0\nbest_schedule = [0, 1, 0, 0, 0]  # 기본값\n\n# 5일 중 2일 선택하는 모든 조합\nfor days in combinations(range(5), 2):\n    count = 0\n    for student in students:\n        # 학생이 두 요일 모두 참가 가능한지 확인\n        if student[days[0]] == 1 and student[days[1]] == 1:\n            count += 1\n    \n    if count > best_count:\n        best_count = count\n        best_schedule = [0] * 5\n        best_schedule[days[0]] = 1\n        best_schedule[days[1]] = 1\n\nprint(best_count)\nprint(*best_schedule)"
      },
      {
        "language": "java",
        "code": "// 정보 선생님의 야망\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        int n = Integer.parseInt(br.readLine());\n        \n        int[][] students = new int[n][5];\n        for (int i = 0; i < n; i++) {\n            StringTokenizer st = new StringTokenizer(br.readLine());\n            for (int j = 0; j < 5; j++) {\n                students[i][j] = Integer.parseInt(st.nextToken());\n            }\n        }\n        \n        int bestCount = 0;\n        int[] bestSchedule = {0, 1, 1, 0, 0};\n        \n        // 5일 중 2일 선택\n        for (int d1 = 0; d1 < 5; d1++) {\n            for (int d2 = d1 + 1; d2 < 5; d2++) {\n                int count = 0;\n                for (int i = 0; i < n; i++) {\n                    if (students[i][d1] == 1 && students[i][d2] == 1) {\n                        count++;\n                    }\n                }\n                if (count > bestCount) {\n                    bestCount = count;\n                    bestSchedule = new int[5];\n                    bestSchedule[d1] = 1;\n                    bestSchedule[d2] = 1;\n                }\n            }\n        }\n        \n        System.out.println(bestCount);\n        StringBuilder sb = new StringBuilder();\n        for (int i = 0; i < 5; i++) {\n            sb.append(bestSchedule[i]);\n            if (i < 4) sb.append(\" \");\n        }\n        System.out.println(sb);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 정보 선생님의 야망\n#include <iostream>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    int students[1001][5];\n    for (int i = 0; i < n; i++) {\n        for (int j = 0; j < 5; j++) {\n            cin >> students[i][j];\n        }\n    }\n    \n    int bestCount = 0;\n    int bestD1 = 0, bestD2 = 1;\n    \n    // 5일 중 2일 선택\n    for (int d1 = 0; d1 < 5; d1++) {\n        for (int d2 = d1 + 1; d2 < 5; d2++) {\n            int count = 0;\n            for (int i = 0; i < n; i++) {\n                if (students[i][d1] == 1 && students[i][d2] == 1) {\n                    count++;\n                }\n            }\n            if (count > bestCount) {\n                bestCount = count;\n                bestD1 = d1;\n                bestD2 = d2;\n            }\n        }\n    }\n    \n    cout << bestCount << \"\\n\";\n    for (int i = 0; i < 5; i++) {\n        if (i == bestD1 || i == bestD2) cout << 1;\n        else cout << 0;\n        if (i < 4) cout << \" \";\n    }\n    cout << endl;\n    \n    return 0;\n}"
      }
    ]
  },
  "33613": {
    "solutions": [
      {
        "language": "python",
        "code": "# 나이트의 이동 - 연속 두 번 이동 후 도달 가능한 칸 수\n# 나이트가 두 번 이동하면 원래 위치 또는 다양한 위치에 도달 가능\n# 패턴 분석 필요\n\nn = int(input())\nr, c = map(int, input().split())\n\n# 나이트의 한 번 이동: 8가지 방향\nmoves = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]\n\n# BFS로 도달 가능한 모든 위치 탐색 (두 번 이동의 배수)\nfrom collections import deque\n\nvisited = set()\nq = deque([(r, c, 0)])\nvisited.add((r, c))\nreachable = set()\nreachable.add((r, c))\n\n# 제한된 탐색 (N이 크므로 효율적으로)\nwhile q:\n    cr, cc, dist = q.popleft()\n    if dist >= 2 * n:  # 충분히 탐색\n        continue\n    \n    for dr, dc in moves:\n        nr, nc = cr + dr, cc + dc\n        if 1 <= nr <= n and 1 <= nc <= n:\n            if (nr, nc) not in visited:\n                visited.add((nr, nc))\n                q.append((nr, nc, dist + 1))\n                if dist % 2 == 1:  # 짝수 번 이동 후\n                    reachable.add((nr, nc))\n\n# 실제로는 두 번 이동의 합이므로 패턴이 있음\n# 두 번 이동 가능한 모든 위치 계산\nresult = set()\nresult.add((r, c))\n\n# 첫 번째 이동\nfirst = []\nfor dr, dc in moves:\n    nr, nc = r + dr, c + dc\n    if 1 <= nr <= n and 1 <= nc <= n:\n        first.append((nr, nc))\n\n# 두 번째 이동\nfor fr, fc in first:\n    for dr, dc in moves:\n        nr, nc = fr + dr, fc + dc\n        if 1 <= nr <= n and 1 <= nc <= n:\n            result.add((nr, nc))\n\nprint(len(result))"
      },
      {
        "language": "java",
        "code": "// 나이트의 이동\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int r = sc.nextInt();\n        int c = sc.nextInt();\n        \n        int[][] moves = {{2,1}, {2,-1}, {-2,1}, {-2,-1}, {1,2}, {1,-2}, {-1,2}, {-1,-2}};\n        \n        Set<Long> result = new HashSet<>();\n        result.add((long)r * 100001 + c);\n        \n        // 첫 번째 이동\n        List<int[]> first = new ArrayList<>();\n        for (int[] m : moves) {\n            int nr = r + m[0];\n            int nc = c + m[1];\n            if (nr >= 1 && nr <= n && nc >= 1 && nc <= n) {\n                first.add(new int[]{nr, nc});\n            }\n        }\n        \n        // 두 번째 이동\n        for (int[] f : first) {\n            for (int[] m : moves) {\n                int nr = f[0] + m[0];\n                int nc = f[1] + m[1];\n                if (nr >= 1 && nr <= n && nc >= 1 && nc <= n) {\n                    result.add((long)nr * 100001 + nc);\n                }\n            }\n        }\n        \n        System.out.println(result.size());\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 나이트의 이동\n#include <iostream>\n#include <set>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    long long n, r, c;\n    cin >> n >> r >> c;\n    \n    int moves[8][2] = {{2,1}, {2,-1}, {-2,1}, {-2,-1}, {1,2}, {1,-2}, {-1,2}, {-1,-2}};\n    \n    set<pair<long long, long long>> result;\n    result.insert({r, c});\n    \n    // 첫 번째 이동\n    vector<pair<long long, long long>> first;\n    for (auto& m : moves) {\n        long long nr = r + m[0];\n        long long nc = c + m[1];\n        if (nr >= 1 && nr <= n && nc >= 1 && nc <= n) {\n            first.push_back({nr, nc});\n        }\n    }\n    \n    // 두 번째 이동\n    for (auto& f : first) {\n        for (auto& m : moves) {\n            long long nr = f.first + m[0];\n            long long nc = f.second + m[1];\n            if (nr >= 1 && nr <= n && nc >= 1 && nc <= n) {\n                result.insert({nr, nc});\n            }\n        }\n    }\n    \n    cout << result.size() << endl;\n    return 0;\n}"
      }
    ]
  },
  "11972": {
    "solutions": [
      {
        "language": "python",
        "code": "# Contaminated Milk - 오염된 우유 추정\nimport sys\ninput = sys.stdin.readline\n\nn, m, d, s = map(int, input().split())\n\n# d개의 음료 섭취 기록\ndrinks = []  # (사람, 우유종류, 시간)\nfor _ in range(d):\n    p, milk, t = map(int, input().split())\n    drinks.append((p, milk, t))\n\n# s개의 병 기록\nsick = []  # (사람, 시간)\nfor _ in range(s):\n    p, t = map(int, input().split())\n    sick.append((p, t))\n\nsick_people = {p for p, t in sick}\nsick_times = {p: t for p, t in sick}\n\n# 가능한 오염 우유 찾기\npossible_bad = set(range(1, m + 1))\n\nfor p, t in sick:\n    # 이 사람이 아프기 전에 마신 우유들만 가능\n    can_cause = set()\n    for dp, dm, dt in drinks:\n        if dp == p and dt < t:\n            can_cause.add(dm)\n    possible_bad &= can_cause\n\n# 각 가능한 오염 우유에 대해 필요한 약 수 계산\nmax_medicine = 0\n\nfor bad in possible_bad:\n    # 이 우유를 마신 사람 중 아직 안 아픈 사람 수\n    at_risk = set()\n    for dp, dm, dt in drinks:\n        if dm == bad:\n            at_risk.add(dp)\n    # 아프거나 아플 위험이 있는 사람\n    max_medicine = max(max_medicine, len(at_risk))\n\nprint(max_medicine)"
      },
      {
        "language": "java",
        "code": "// Contaminated Milk\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int m = sc.nextInt();\n        int d = sc.nextInt();\n        int s = sc.nextInt();\n        \n        int[][] drinks = new int[d][3];\n        for (int i = 0; i < d; i++) {\n            drinks[i][0] = sc.nextInt(); // person\n            drinks[i][1] = sc.nextInt(); // milk\n            drinks[i][2] = sc.nextInt(); // time\n        }\n        \n        int[][] sick = new int[s][2];\n        for (int i = 0; i < s; i++) {\n            sick[i][0] = sc.nextInt(); // person\n            sick[i][1] = sc.nextInt(); // time\n        }\n        \n        // 가능한 오염 우유 찾기\n        Set<Integer> possible = new HashSet<>();\n        for (int i = 1; i <= m; i++) possible.add(i);\n        \n        for (int[] sickInfo : sick) {\n            int p = sickInfo[0], t = sickInfo[1];\n            Set<Integer> canCause = new HashSet<>();\n            for (int[] drink : drinks) {\n                if (drink[0] == p && drink[2] < t) {\n                    canCause.add(drink[1]);\n                }\n            }\n            possible.retainAll(canCause);\n        }\n        \n        int maxMedicine = 0;\n        for (int bad : possible) {\n            Set<Integer> atRisk = new HashSet<>();\n            for (int[] drink : drinks) {\n                if (drink[1] == bad) {\n                    atRisk.add(drink[0]);\n                }\n            }\n            maxMedicine = Math.max(maxMedicine, atRisk.size());\n        }\n        \n        System.out.println(maxMedicine);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// Contaminated Milk\n#include <iostream>\n#include <set>\n#include <vector>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n, m, d, s;\n    cin >> n >> m >> d >> s;\n    \n    vector<tuple<int,int,int>> drinks(d);\n    for (int i = 0; i < d; i++) {\n        int p, milk, t;\n        cin >> p >> milk >> t;\n        drinks[i] = {p, milk, t};\n    }\n    \n    vector<pair<int,int>> sick(s);\n    for (int i = 0; i < s; i++) {\n        cin >> sick[i].first >> sick[i].second;\n    }\n    \n    set<int> possible;\n    for (int i = 1; i <= m; i++) possible.insert(i);\n    \n    for (auto& [p, t] : sick) {\n        set<int> canCause;\n        for (auto& [dp, dm, dt] : drinks) {\n            if (dp == p && dt < t) {\n                canCause.insert(dm);\n            }\n        }\n        set<int> newPossible;\n        for (int x : possible) {\n            if (canCause.count(x)) newPossible.insert(x);\n        }\n        possible = newPossible;\n    }\n    \n    int maxMedicine = 0;\n    for (int bad : possible) {\n        set<int> atRisk;\n        for (auto& [dp, dm, dt] : drinks) {\n            if (dm == bad) atRisk.insert(dp);\n        }\n        maxMedicine = max(maxMedicine, (int)atRisk.size());\n    }\n    \n    cout << maxMedicine << endl;\n    return 0;\n}"
      }
    ]
  },
  "28357": {
    "solutions": [
      {
        "language": "python",
        "code": "# 사탕 나눠주기 - 이진 탐색으로 X 최솟값 찾기\nimport sys\ninput = sys.stdin.readline\n\nn, k = map(int, input().split())\nscores = list(map(int, input().split()))\nscores.sort(reverse=True)  # 내림차순 정렬\n\n# X가 주어졌을 때 필요한 사탕 수 계산\ndef candy_count(x):\n    total = 0\n    for s in scores:\n        if s > x:\n            total += s - x\n        else:\n            break\n    return total\n\n# 이진 탐색\nleft, right = 0, max(scores)\n\nwhile left < right:\n    mid = (left + right) // 2\n    if candy_count(mid) <= k:\n        right = mid\n    else:\n        left = mid + 1\n\nprint(left)"
      },
      {
        "language": "java",
        "code": "// 사탕 나눠주기 - 이진 탐색\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    static long[] scores;\n    \n    static long candyCount(long x) {\n        long total = 0;\n        for (long s : scores) {\n            if (s > x) {\n                total += s - x;\n            }\n        }\n        return total;\n    }\n    \n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int n = Integer.parseInt(st.nextToken());\n        long k = Long.parseLong(st.nextToken());\n        \n        scores = new long[n];\n        st = new StringTokenizer(br.readLine());\n        long maxScore = 0;\n        for (int i = 0; i < n; i++) {\n            scores[i] = Long.parseLong(st.nextToken());\n            maxScore = Math.max(maxScore, scores[i]);\n        }\n        \n        long left = 0, right = maxScore;\n        while (left < right) {\n            long mid = (left + right) / 2;\n            if (candyCount(mid) <= k) {\n                right = mid;\n            } else {\n                left = mid + 1;\n            }\n        }\n        \n        System.out.println(left);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 사탕 나눠주기 - 이진 탐색\n#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n\nvector<long long> scores;\n\nlong long candyCount(long long x) {\n    long long total = 0;\n    for (long long s : scores) {\n        if (s > x) {\n            total += s - x;\n        }\n    }\n    return total;\n}\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    long long k;\n    cin >> n >> k;\n    \n    scores.resize(n);\n    long long maxScore = 0;\n    for (int i = 0; i < n; i++) {\n        cin >> scores[i];\n        maxScore = max(maxScore, scores[i]);\n    }\n    \n    long long left = 0, right = maxScore;\n    while (left < right) {\n        long long mid = (left + right) / 2;\n        if (candyCount(mid) <= k) {\n            right = mid;\n        } else {\n            left = mid + 1;\n        }\n    }\n    \n    cout << left << endl;\n    return 0;\n}"
      }
    ]
  },
  "18242": {
    "solutions": [
      {
        "language": "python",
        "code": "# 네모네모 시력검사 - 정사각형의 열린 변 찾기\nimport sys\ninput = sys.stdin.readline\n\nn, m = map(int, input().split())\ngrid = []\nfor _ in range(n):\n    grid.append(input().strip())\n\n# 정사각형 테두리 위치 찾기\nmin_r, max_r = n, -1\nmin_c, max_c = m, -1\n\nfor i in range(n):\n    for j in range(m):\n        if grid[i][j] == '#':\n            min_r = min(min_r, i)\n            max_r = max(max_r, i)\n            min_c = min(min_c, j)\n            max_c = max(max_c, j)\n\n# 한 변의 가운데가 비어있는 위치 찾기\nside_len = max_r - min_r + 1\nmid = side_len // 2\n\n# 윗변 가운데 확인\nif grid[min_r][min_c + mid] == '.':\n    print(\"UP\")\n# 아랫변 가운데 확인\nelif grid[max_r][min_c + mid] == '.':\n    print(\"DOWN\")\n# 왼쪽 변 가운데 확인\nelif grid[min_r + mid][min_c] == '.':\n    print(\"LEFT\")\n# 오른쪽 변 가운데 확인\nelse:\n    print(\"RIGHT\")"
      },
      {
        "language": "java",
        "code": "// 네모네모 시력검사\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        String[] nm = br.readLine().split(\" \");\n        int n = Integer.parseInt(nm[0]);\n        int m = Integer.parseInt(nm[1]);\n        \n        char[][] grid = new char[n][m];\n        int minR = n, maxR = -1, minC = m, maxC = -1;\n        \n        for (int i = 0; i < n; i++) {\n            grid[i] = br.readLine().toCharArray();\n            for (int j = 0; j < m; j++) {\n                if (grid[i][j] == '#') {\n                    minR = Math.min(minR, i);\n                    maxR = Math.max(maxR, i);\n                    minC = Math.min(minC, j);\n                    maxC = Math.max(maxC, j);\n                }\n            }\n        }\n        \n        int sideLen = maxR - minR + 1;\n        int mid = sideLen / 2;\n        \n        if (grid[minR][minC + mid] == '.') {\n            System.out.println(\"UP\");\n        } else if (grid[maxR][minC + mid] == '.') {\n            System.out.println(\"DOWN\");\n        } else if (grid[minR + mid][minC] == '.') {\n            System.out.println(\"LEFT\");\n        } else {\n            System.out.println(\"RIGHT\");\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 네모네모 시력검사\n#include <iostream>\n#include <string>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n, m;\n    cin >> n >> m;\n    \n    string grid[101];\n    int minR = n, maxR = -1, minC = m, maxC = -1;\n    \n    for (int i = 0; i < n; i++) {\n        cin >> grid[i];\n        for (int j = 0; j < m; j++) {\n            if (grid[i][j] == '#') {\n                minR = min(minR, i);\n                maxR = max(maxR, i);\n                minC = min(minC, j);\n                maxC = max(maxC, j);\n            }\n        }\n    }\n    \n    int sideLen = maxR - minR + 1;\n    int mid = sideLen / 2;\n    \n    if (grid[minR][minC + mid] == '.') {\n        cout << \"UP\" << endl;\n    } else if (grid[maxR][minC + mid] == '.') {\n        cout << \"DOWN\" << endl;\n    } else if (grid[minR + mid][minC] == '.') {\n        cout << \"LEFT\" << endl;\n    } else {\n        cout << \"RIGHT\" << endl;\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "28116": {
    "solutions": [
      {
        "language": "python",
        "code": "# 선택 정렬의 이동 거리\nimport sys\ninput = sys.stdin.readline\n\nn = int(input())\nA = list(map(int, input().split()))\n\n# 각 값의 현재 위치 저장\npos = [0] * (n + 1)\nfor i in range(n):\n    pos[A[i]] = i\n\n# 이동 거리\ndist = [0] * (n + 1)\n\n# 선택 정렬 시뮬레이션\nfor i in range(n - 1):\n    # i 위치에 i+1 값이 와야 함\n    target = i + 1\n    j = pos[target]\n    \n    if i != j:\n        # A[i]와 A[j] 교환\n        move = j - i\n        dist[A[i]] += move\n        dist[A[j]] += move\n        \n        # 위치 업데이트\n        pos[A[i]] = j\n        pos[A[j]] = i\n        A[i], A[j] = A[j], A[i]\n\nprint(' '.join(map(str, dist[1:])))"
      },
      {
        "language": "java",
        "code": "// 선택 정렬의 이동 거리\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        int n = Integer.parseInt(br.readLine());\n        int[] A = new int[n];\n        int[] pos = new int[n + 1];\n        int[] dist = new int[n + 1];\n        \n        StringTokenizer st = new StringTokenizer(br.readLine());\n        for (int i = 0; i < n; i++) {\n            A[i] = Integer.parseInt(st.nextToken());\n            pos[A[i]] = i;\n        }\n        \n        for (int i = 0; i < n - 1; i++) {\n            int target = i + 1;\n            int j = pos[target];\n            \n            if (i != j) {\n                int move = j - i;\n                dist[A[i]] += move;\n                dist[A[j]] += move;\n                \n                pos[A[i]] = j;\n                pos[A[j]] = i;\n                int tmp = A[i]; A[i] = A[j]; A[j] = tmp;\n            }\n        }\n        \n        StringBuilder sb = new StringBuilder();\n        for (int i = 1; i <= n; i++) {\n            sb.append(dist[i]);\n            if (i < n) sb.append(\" \");\n        }\n        System.out.println(sb);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 선택 정렬의 이동 거리\n#include <iostream>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    int A[500001], pos[500001], dist[500001] = {0};\n    \n    for (int i = 0; i < n; i++) {\n        cin >> A[i];\n        pos[A[i]] = i;\n    }\n    \n    for (int i = 0; i < n - 1; i++) {\n        int target = i + 1;\n        int j = pos[target];\n        \n        if (i != j) {\n            int move = j - i;\n            dist[A[i]] += move;\n            dist[A[j]] += move;\n            \n            pos[A[i]] = j;\n            pos[A[j]] = i;\n            swap(A[i], A[j]);\n        }\n    }\n    \n    for (int i = 1; i <= n; i++) {\n        cout << dist[i];\n        if (i < n) cout << \" \";\n    }\n    cout << endl;\n    \n    return 0;\n}"
      }
    ]
  },
  "22973": {
    "solutions": [
      {
        "language": "python",
        "code": "# 점프 숨바꼭질 - 점프 거리가 2배씩 증가\n# 0에서 시작, 점프: 1, 2, 4, 8, ... (2^(i-1))\n# K 위치에 도달하는 최소 점프 횟수\n\nk = int(input())\n\nif k == 0:\n    print(0)\nelse:\n    # 점프 합: 1 + 2 + 4 + ... + 2^(n-1) = 2^n - 1\n    # 각 점프마다 + 또는 - 선택\n    # n번 점프로 도달 가능한 위치: 홀수 개의 + (합이 K가 되도록)\n    \n    # 2^n - 1 >= |K| 이고, (2^n - 1 - |K|)가 짝수여야 함\n    # (2^n - 1 - |K|) / 2 만큼의 점프를 -로 바꾸면 됨\n    \n    k = abs(k)\n    n = 0\n    total = 0\n    \n    while True:\n        n += 1\n        total = total * 2 + 1  # 2^n - 1\n        \n        if total >= k and (total - k) % 2 == 0:\n            print(n)\n            break\n        \n        if n > 50:  # 불가능\n            print(-1)\n            break"
      },
      {
        "language": "java",
        "code": "// 점프 숨바꼭질\nimport java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long k = sc.nextLong();\n        \n        if (k == 0) {\n            System.out.println(0);\n            return;\n        }\n        \n        k = Math.abs(k);\n        int n = 0;\n        long total = 0;\n        \n        while (true) {\n            n++;\n            total = total * 2 + 1;\n            \n            if (total >= k && (total - k) % 2 == 0) {\n                System.out.println(n);\n                return;\n            }\n            \n            if (n > 50) {\n                System.out.println(-1);\n                return;\n            }\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 점프 숨바꼭질\n#include <iostream>\n#include <cmath>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    long long k;\n    cin >> k;\n    \n    if (k == 0) {\n        cout << 0 << endl;\n        return 0;\n    }\n    \n    k = abs(k);\n    int n = 0;\n    long long total = 0;\n    \n    while (true) {\n        n++;\n        total = total * 2 + 1;\n        \n        if (total >= k && (total - k) % 2 == 0) {\n            cout << n << endl;\n            return 0;\n        }\n        \n        if (n > 50) {\n            cout << -1 << endl;\n            return 0;\n        }\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "24954": {
    "solutions": [
      {
        "language": "python",
        "code": "# 물약 구매 - 순열로 최소 비용 찾기\nfrom itertools import permutations\nimport sys\ninput = sys.stdin.readline\n\nn = int(input())\nprices = list(map(int, input().split()))\n\n# 할인 정보\ndiscounts = []\nfor i in range(n):\n    p = int(input())\n    disc = []\n    for _ in range(p):\n        a, d = map(int, input().split())\n        disc.append((a - 1, d))  # 0-indexed\n    discounts.append(disc)\n\nmin_cost = float('inf')\n\n# 모든 구매 순서 시도 (N <= 10이므로 가능)\nfor order in permutations(range(n)):\n    current_prices = prices[:]\n    cost = 0\n    \n    for i in order:\n        cost += max(1, current_prices[i])  # 최소 1원\n        # 할인 적용\n        for target, discount in discounts[i]:\n            current_prices[target] -= discount\n    \n    min_cost = min(min_cost, cost)\n\nprint(min_cost)"
      },
      {
        "language": "java",
        "code": "// 물약 구매 - 순열로 최소 비용 찾기\nimport java.util.*;\n\npublic class Main {\n    static int n;\n    static int[] prices;\n    static int[][] discounts;\n    static int[] discountCounts;\n    static int minCost = Integer.MAX_VALUE;\n    static boolean[] used;\n    static int[] order;\n    \n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        n = sc.nextInt();\n        prices = new int[n];\n        for (int i = 0; i < n; i++) {\n            prices[i] = sc.nextInt();\n        }\n        \n        discounts = new int[n][20];\n        discountCounts = new int[n];\n        for (int i = 0; i < n; i++) {\n            int p = sc.nextInt();\n            discountCounts[i] = p;\n            for (int j = 0; j < p; j++) {\n                int a = sc.nextInt() - 1;\n                int d = sc.nextInt();\n                discounts[i][j * 2] = a;\n                discounts[i][j * 2 + 1] = d;\n            }\n        }\n        \n        used = new boolean[n];\n        order = new int[n];\n        permute(0);\n        System.out.println(minCost);\n    }\n    \n    static void permute(int idx) {\n        if (idx == n) {\n            int[] cp = prices.clone();\n            int cost = 0;\n            for (int i : order) {\n                cost += Math.max(1, cp[i]);\n                for (int j = 0; j < discountCounts[i]; j++) {\n                    int t = discounts[i][j * 2];\n                    int d = discounts[i][j * 2 + 1];\n                    cp[t] -= d;\n                }\n            }\n            minCost = Math.min(minCost, cost);\n            return;\n        }\n        for (int i = 0; i < n; i++) {\n            if (!used[i]) {\n                used[i] = true;\n                order[idx] = i;\n                permute(idx + 1);\n                used[i] = false;\n            }\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 물약 구매 - 순열로 최소 비용 찾기\n#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    vector<int> prices(n);\n    for (int i = 0; i < n; i++) {\n        cin >> prices[i];\n    }\n    \n    vector<vector<pair<int,int>>> discounts(n);\n    for (int i = 0; i < n; i++) {\n        int p;\n        cin >> p;\n        for (int j = 0; j < p; j++) {\n            int a, d;\n            cin >> a >> d;\n            discounts[i].push_back({a - 1, d});\n        }\n    }\n    \n    vector<int> order(n);\n    for (int i = 0; i < n; i++) order[i] = i;\n    \n    int minCost = INT_MAX;\n    \n    do {\n        vector<int> cp = prices;\n        int cost = 0;\n        for (int i : order) {\n            cost += max(1, cp[i]);\n            for (auto& [t, d] : discounts[i]) {\n                cp[t] -= d;\n            }\n        }\n        minCost = min(minCost, cost);\n    } while (next_permutation(order.begin(), order.end()));\n    \n    cout << minCost << endl;\n    return 0;\n}"
      }
    ]
  },
  "16162": {
    "solutions": [
      {
        "language": "python",
        "code": "# 가희와 3단 고음 - 등차수열 최대 길이 찾기\nimport sys\ninput = sys.stdin.readline\n\nn, a, d = map(int, input().split())\nnotes = list(map(int, input().split()))\n\n# 현재 찾아야 하는 음\ntarget = a\ncount = 0\n\nfor note in notes:\n    if note == target:\n        count += 1\n        target += d\n\nprint(count)"
      },
      {
        "language": "java",
        "code": "// 가희와 3단 고음\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int n = Integer.parseInt(st.nextToken());\n        long a = Long.parseLong(st.nextToken());\n        long d = Long.parseLong(st.nextToken());\n        \n        st = new StringTokenizer(br.readLine());\n        long target = a;\n        int count = 0;\n        \n        for (int i = 0; i < n; i++) {\n            long note = Long.parseLong(st.nextToken());\n            if (note == target) {\n                count++;\n                target += d;\n            }\n        }\n        \n        System.out.println(count);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 가희와 3단 고음\n#include <iostream>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    long long a, d;\n    cin >> n >> a >> d;\n    \n    long long target = a;\n    int count = 0;\n    \n    for (int i = 0; i < n; i++) {\n        long long note;\n        cin >> note;\n        if (note == target) {\n            count++;\n            target += d;\n        }\n    }\n    \n    cout << count << endl;\n    return 0;\n}"
      }
    ]
  },
  "18265": {
    "solutions": [
      {
        "language": "python",
        "code": "# MooBuzz - FizzBuzz에서 숫자만 세기\n# 3의 배수나 5의 배수가 아닌 n번째 숫자 찾기\n\nn = int(input())\n\n# 15개 숫자 중 3의 배수: 3,6,9,12,15 (5개)\n# 15개 숫자 중 5의 배수: 5,10,15 (3개)\n# 15개 숫자 중 15의 배수: 15 (1개)\n# 3 또는 5의 배수: 5 + 3 - 1 = 7개\n# 숫자만 세는 것: 15 - 7 = 8개\n\n# 이진 탐색으로 n번째 숫자 찾기\ndef count_numbers(x):\n    \"\"\"x까지의 숫자 중 3의 배수도 5의 배수도 아닌 수의 개수\"\"\"\n    return x - x // 3 - x // 5 + x // 15\n\nleft, right = 1, 2 * n  # 넉넉하게\n\nwhile left < right:\n    mid = (left + right) // 2\n    if count_numbers(mid) >= n:\n        right = mid\n    else:\n        left = mid + 1\n\nprint(left)"
      },
      {
        "language": "java",
        "code": "// MooBuzz\nimport java.util.Scanner;\n\npublic class Main {\n    static long countNumbers(long x) {\n        return x - x / 3 - x / 5 + x / 15;\n    }\n    \n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long n = sc.nextLong();\n        \n        long left = 1, right = 2 * n;\n        \n        while (left < right) {\n            long mid = (left + right) / 2;\n            if (countNumbers(mid) >= n) {\n                right = mid;\n            } else {\n                left = mid + 1;\n            }\n        }\n        \n        System.out.println(left);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// MooBuzz\n#include <iostream>\nusing namespace std;\n\nlong long countNumbers(long long x) {\n    return x - x / 3 - x / 5 + x / 15;\n}\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    long long n;\n    cin >> n;\n    \n    long long left = 1, right = 2 * n;\n    \n    while (left < right) {\n        long long mid = (left + right) / 2;\n        if (countNumbers(mid) >= n) {\n            right = mid;\n        } else {\n            left = mid + 1;\n        }\n    }\n    \n    cout << left << endl;\n    return 0;\n}"
      }
    ]
  }
}

# 기존 데이터에 새로운 솔루션 추가
added = 0
for pid, data in new_solutions.items():
    if pid not in medium_data:
        medium_data[pid] = data
        added += 1

# 저장
with open('data/baekjoon/baek_medium.json', 'w', encoding='utf-8') as f:
    json.dump(medium_data, f, ensure_ascii=False, indent=2)

print(f"새로 추가된 솔루션: {added}개")
print(f"총 솔루션 수: {len(medium_data)}개")
