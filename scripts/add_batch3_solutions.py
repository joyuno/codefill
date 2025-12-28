#!/usr/bin/env python3
"""세 번째 배치 솔루션 추가 스크립트"""
import json

# 기존 baek_medium.json 읽기
with open('data/baekjoon/baek_medium.json', 'r', encoding='utf-8') as f:
    medium_data = json.load(f)

print(f"기존 솔루션 수: {len(medium_data)}")

# 새로운 솔루션
new_solutions = {
  "27514": {
    "solutions": [
      {
        "language": "python",
        "code": "# 1차원 2048 - 같은 값을 합쳐서 최댓값 만들기\nimport sys\nfrom collections import Counter\ninput = sys.stdin.readline\n\nn = int(input())\narr = list(map(int, input().split()))\n\n# 각 값의 개수 세기 (0 제외)\ncnt = Counter()\nfor x in arr:\n    if x > 0:\n        cnt[x] += 1\n\n# 작은 값부터 합쳐 올라감\nkeys = sorted(cnt.keys())\nfor k in keys:\n    # 개수가 2 이상이면 합칠 수 있음\n    while cnt[k] >= 2:\n        cnt[k] -= 2\n        cnt[k * 2] = cnt.get(k * 2, 0) + 1\n        if cnt[k] == 0:\n            del cnt[k]\n\n# 최댓값 출력\nprint(max(cnt.keys()))"
      },
      {
        "language": "java",
        "code": "// 1차원 2048\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        int n = Integer.parseInt(br.readLine());\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        \n        TreeMap<Long, Long> cnt = new TreeMap<>();\n        for (int i = 0; i < n; i++) {\n            long x = Long.parseLong(st.nextToken());\n            if (x > 0) {\n                cnt.put(x, cnt.getOrDefault(x, 0L) + 1);\n            }\n        }\n        \n        // 작은 값부터 합쳐 올라감\n        while (true) {\n            boolean merged = false;\n            for (long k : new ArrayList<>(cnt.keySet())) {\n                long c = cnt.getOrDefault(k, 0L);\n                if (c >= 2) {\n                    cnt.put(k, c % 2);\n                    if (cnt.get(k) == 0) cnt.remove(k);\n                    cnt.put(k * 2, cnt.getOrDefault(k * 2, 0L) + c / 2);\n                    merged = true;\n                }\n            }\n            if (!merged) break;\n        }\n        \n        System.out.println(cnt.lastKey());\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 1차원 2048\n#include <iostream>\n#include <map>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    map<long long, long long> cnt;\n    for (int i = 0; i < n; i++) {\n        long long x;\n        cin >> x;\n        if (x > 0) cnt[x]++;\n    }\n    \n    // 작은 값부터 합쳐 올라감\n    while (true) {\n        bool merged = false;\n        for (auto it = cnt.begin(); it != cnt.end(); ) {\n            long long k = it->first;\n            long long c = it->second;\n            if (c >= 2) {\n                cnt[k * 2] += c / 2;\n                it->second = c % 2;\n                if (it->second == 0) {\n                    it = cnt.erase(it);\n                } else {\n                    ++it;\n                }\n                merged = true;\n            } else {\n                ++it;\n            }\n        }\n        if (!merged) break;\n    }\n    \n    cout << cnt.rbegin()->first << endl;\n    return 0;\n}"
      }
    ]
  },
  "20206": {
    "solutions": [
      {
        "language": "python",
        "code": "# 푸앙이가 길을 건너간 이유 - 직선이 직사각형 내부를 통과하는지\na, b, c = map(int, input().split())\nx1, x2, y1, y2 = map(int, input().split())\n\n# 직선 Ax + By + C = 0\n# 네 꼭짓점에서의 부호 확인\n# (x1, y1), (x1, y2), (x2, y1), (x2, y2)\n\ndef f(x, y):\n    return a * x + b * y + c\n\nv1 = f(x1, y1)\nv2 = f(x1, y2)\nv3 = f(x2, y1)\nv4 = f(x2, y2)\n\n# 네 꼭짓점의 값이 모두 같은 부호면 통과하지 않음\n# 값이 0인 경우는 경계를 통과하는 것이므로 제외\n# 양수와 음수가 섞여있고, 0이 아닌 경우에만 Poor\n\nvalues = [v1, v2, v3, v4]\nhas_pos = any(v > 0 for v in values)\nhas_neg = any(v < 0 for v in values)\n\nif has_pos and has_neg:\n    print(\"Poor\")\nelse:\n    print(\"Lucky\")"
      },
      {
        "language": "java",
        "code": "// 푸앙이가 길을 건너간 이유\nimport java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long a = sc.nextLong();\n        long b = sc.nextLong();\n        long c = sc.nextLong();\n        long x1 = sc.nextLong();\n        long x2 = sc.nextLong();\n        long y1 = sc.nextLong();\n        long y2 = sc.nextLong();\n        \n        long v1 = a * x1 + b * y1 + c;\n        long v2 = a * x1 + b * y2 + c;\n        long v3 = a * x2 + b * y1 + c;\n        long v4 = a * x2 + b * y2 + c;\n        \n        boolean hasPos = v1 > 0 || v2 > 0 || v3 > 0 || v4 > 0;\n        boolean hasNeg = v1 < 0 || v2 < 0 || v3 < 0 || v4 < 0;\n        \n        System.out.println(hasPos && hasNeg ? \"Poor\" : \"Lucky\");\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 푸앙이가 길을 건너간 이유\n#include <iostream>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    long long a, b, c, x1, x2, y1, y2;\n    cin >> a >> b >> c >> x1 >> x2 >> y1 >> y2;\n    \n    long long v1 = a * x1 + b * y1 + c;\n    long long v2 = a * x1 + b * y2 + c;\n    long long v3 = a * x2 + b * y1 + c;\n    long long v4 = a * x2 + b * y2 + c;\n    \n    bool hasPos = v1 > 0 || v2 > 0 || v3 > 0 || v4 > 0;\n    bool hasNeg = v1 < 0 || v2 < 0 || v3 < 0 || v4 < 0;\n    \n    cout << (hasPos && hasNeg ? \"Poor\" : \"Lucky\") << endl;\n    return 0;\n}"
      }
    ]
  },
  "9518": {
    "solutions": [
      {
        "language": "python",
        "code": "# 로마 카톨릭 미사 - 악수 횟수 계산\nr, s = map(int, input().split())\ngrid = []\nfor _ in range(r):\n    grid.append(input().strip())\n\n# 상근이가 앉을 자리 찾기 (최대 이웃 수)\nbest_seat = None\nbest_neighbors = -1\n\nfor i in range(r):\n    for j in range(s):\n        if grid[i][j] == '.':\n            neighbors = 0\n            for di in [-1, 0, 1]:\n                for dj in [-1, 0, 1]:\n                    if di == 0 and dj == 0:\n                        continue\n                    ni, nj = i + di, j + dj\n                    if 0 <= ni < r and 0 <= nj < s and grid[ni][nj] == 'o':\n                        neighbors += 1\n            if neighbors > best_neighbors:\n                best_neighbors = neighbors\n                best_seat = (i, j)\n\n# 상근이 자리에 앉히기\nif best_seat:\n    grid = [list(row) for row in grid]\n    grid[best_seat[0]][best_seat[1]] = 'o'\n    grid = [''.join(row) for row in grid]\n\n# 총 악수 횟수 계산 (각 쌍은 한 번만)\nhandshakes = 0\ndirections = [(0, 1), (1, 0), (1, 1), (1, -1)]  # 오른쪽, 아래, 대각선 두 방향\n\nfor i in range(r):\n    for j in range(s):\n        if grid[i][j] == 'o':\n            for di, dj in directions:\n                ni, nj = i + di, j + dj\n                if 0 <= ni < r and 0 <= nj < s and grid[ni][nj] == 'o':\n                    handshakes += 1\n\nprint(handshakes)"
      },
      {
        "language": "java",
        "code": "// 로마 카톨릭 미사 - 악수 횟수 계산\nimport java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int r = sc.nextInt();\n        int s = sc.nextInt();\n        char[][] grid = new char[r][s];\n        \n        for (int i = 0; i < r; i++) {\n            grid[i] = sc.next().toCharArray();\n        }\n        \n        // 상근이가 앉을 자리 찾기\n        int[] dx = {-1, -1, -1, 0, 0, 1, 1, 1};\n        int[] dy = {-1, 0, 1, -1, 1, -1, 0, 1};\n        \n        int bestI = -1, bestJ = -1, bestNeighbors = -1;\n        for (int i = 0; i < r; i++) {\n            for (int j = 0; j < s; j++) {\n                if (grid[i][j] == '.') {\n                    int neighbors = 0;\n                    for (int d = 0; d < 8; d++) {\n                        int ni = i + dx[d], nj = j + dy[d];\n                        if (ni >= 0 && ni < r && nj >= 0 && nj < s && grid[ni][nj] == 'o') {\n                            neighbors++;\n                        }\n                    }\n                    if (neighbors > bestNeighbors) {\n                        bestNeighbors = neighbors;\n                        bestI = i;\n                        bestJ = j;\n                    }\n                }\n            }\n        }\n        \n        if (bestI != -1) {\n            grid[bestI][bestJ] = 'o';\n        }\n        \n        // 총 악수 횟수 계산\n        int[][] dir = {{0, 1}, {1, 0}, {1, 1}, {1, -1}};\n        int handshakes = 0;\n        for (int i = 0; i < r; i++) {\n            for (int j = 0; j < s; j++) {\n                if (grid[i][j] == 'o') {\n                    for (int[] d : dir) {\n                        int ni = i + d[0], nj = j + d[1];\n                        if (ni >= 0 && ni < r && nj >= 0 && nj < s && grid[ni][nj] == 'o') {\n                            handshakes++;\n                        }\n                    }\n                }\n            }\n        }\n        \n        System.out.println(handshakes);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 로마 카톨릭 미사 - 악수 횟수 계산\n#include <iostream>\n#include <vector>\n#include <string>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int r, s;\n    cin >> r >> s;\n    \n    vector<string> grid(r);\n    for (int i = 0; i < r; i++) {\n        cin >> grid[i];\n    }\n    \n    // 상근이가 앉을 자리 찾기\n    int dx[] = {-1, -1, -1, 0, 0, 1, 1, 1};\n    int dy[] = {-1, 0, 1, -1, 1, -1, 0, 1};\n    \n    int bestI = -1, bestJ = -1, bestNeighbors = -1;\n    for (int i = 0; i < r; i++) {\n        for (int j = 0; j < s; j++) {\n            if (grid[i][j] == '.') {\n                int neighbors = 0;\n                for (int d = 0; d < 8; d++) {\n                    int ni = i + dx[d], nj = j + dy[d];\n                    if (ni >= 0 && ni < r && nj >= 0 && nj < s && grid[ni][nj] == 'o') {\n                        neighbors++;\n                    }\n                }\n                if (neighbors > bestNeighbors) {\n                    bestNeighbors = neighbors;\n                    bestI = i;\n                    bestJ = j;\n                }\n            }\n        }\n    }\n    \n    if (bestI != -1) {\n        grid[bestI][bestJ] = 'o';\n    }\n    \n    // 총 악수 횟수 계산\n    int dir[][2] = {{0, 1}, {1, 0}, {1, 1}, {1, -1}};\n    int handshakes = 0;\n    for (int i = 0; i < r; i++) {\n        for (int j = 0; j < s; j++) {\n            if (grid[i][j] == 'o') {\n                for (auto& d : dir) {\n                    int ni = i + d[0], nj = j + d[1];\n                    if (ni >= 0 && ni < r && nj >= 0 && nj < s && grid[ni][nj] == 'o') {\n                        handshakes++;\n                    }\n                }\n            }\n        }\n    }\n    \n    cout << handshakes << endl;\n    return 0;\n}"
      }
    ]
  },
  "29615": {
    "solutions": [
      {
        "language": "python",
        "code": "# 알파빌과 베타빌 - 친구들을 앞으로 보내는 최소 교환 횟수\nimport sys\ninput = sys.stdin.readline\n\nn, m = map(int, input().split())\nwaitlist = list(map(int, input().split()))\nfriends = set(map(int, input().split()))\n\n# 친구들이 처음 m개 위치에 있어야 함\n# 현재 처음 m개 위치에 친구가 아닌 사람 수 = 교환 횟수\ncount = 0\nfor i in range(m):\n    if waitlist[i] not in friends:\n        count += 1\n\nprint(count)"
      },
      {
        "language": "java",
        "code": "// 알파빌과 베타빌\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int n = Integer.parseInt(st.nextToken());\n        int m = Integer.parseInt(st.nextToken());\n        \n        int[] waitlist = new int[n];\n        st = new StringTokenizer(br.readLine());\n        for (int i = 0; i < n; i++) {\n            waitlist[i] = Integer.parseInt(st.nextToken());\n        }\n        \n        Set<Integer> friends = new HashSet<>();\n        st = new StringTokenizer(br.readLine());\n        for (int i = 0; i < m; i++) {\n            friends.add(Integer.parseInt(st.nextToken()));\n        }\n        \n        int count = 0;\n        for (int i = 0; i < m; i++) {\n            if (!friends.contains(waitlist[i])) {\n                count++;\n            }\n        }\n        \n        System.out.println(count);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 알파빌과 베타빌\n#include <iostream>\n#include <set>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n, m;\n    cin >> n >> m;\n    \n    int waitlist[1001];\n    for (int i = 0; i < n; i++) {\n        cin >> waitlist[i];\n    }\n    \n    set<int> friends;\n    for (int i = 0; i < m; i++) {\n        int f;\n        cin >> f;\n        friends.insert(f);\n    }\n    \n    int count = 0;\n    for (int i = 0; i < m; i++) {\n        if (friends.find(waitlist[i]) == friends.end()) {\n            count++;\n        }\n    }\n    \n    cout << count << endl;\n    return 0;\n}"
      }
    ]
  },
  "24174": {
    "solutions": [
      {
        "language": "python",
        "code": "# 알고리즘 수업 - 힙 정렬 2\nimport sys\nsys.setrecursionlimit(600000)\ninput = sys.stdin.readline\n\nn, k = map(int, input().split())\nA = [0] + list(map(int, input().split()))  # 1-indexed\n\nswap_count = 0\nresult = None\n\ndef heapify(arr, k_idx, n_size):\n    global swap_count, result\n    if result:\n        return\n    \n    left = 2 * k_idx\n    right = 2 * k_idx + 1\n    \n    if right <= n_size:\n        if arr[left] < arr[right]:\n            smaller = left\n        else:\n            smaller = right\n    elif left <= n_size:\n        smaller = left\n    else:\n        return\n    \n    if arr[smaller] < arr[k_idx]:\n        arr[k_idx], arr[smaller] = arr[smaller], arr[k_idx]\n        swap_count += 1\n        if swap_count == k:\n            result = arr[1:]\n            return\n        heapify(arr, smaller, n_size)\n\ndef build_min_heap(arr, n_size):\n    global result\n    for i in range(n_size // 2, 0, -1):\n        if result:\n            return\n        heapify(arr, i, n_size)\n\ndef heap_sort(arr, n_size):\n    global swap_count, result\n    build_min_heap(arr, n_size)\n    if result:\n        return\n    \n    for i in range(n_size, 1, -1):\n        arr[1], arr[i] = arr[i], arr[1]\n        swap_count += 1\n        if swap_count == k:\n            result = arr[1:]\n            return\n        heapify(arr, 1, i - 1)\n        if result:\n            return\n\nheap_sort(A, n)\n\nif result:\n    print(' '.join(map(str, result)))\nelse:\n    print(-1)"
      },
      {
        "language": "java",
        "code": "// 알고리즘 수업 - 힙 정렬 2\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    static int[] A;\n    static int swapCount = 0;\n    static int k;\n    static boolean found = false;\n    \n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int n = Integer.parseInt(st.nextToken());\n        k = Integer.parseInt(st.nextToken());\n        \n        A = new int[n + 1];\n        st = new StringTokenizer(br.readLine());\n        for (int i = 1; i <= n; i++) {\n            A[i] = Integer.parseInt(st.nextToken());\n        }\n        \n        heapSort(n);\n        \n        if (found) {\n            StringBuilder sb = new StringBuilder();\n            for (int i = 1; i <= n; i++) {\n                sb.append(A[i]);\n                if (i < n) sb.append(\" \");\n            }\n            System.out.println(sb);\n        } else {\n            System.out.println(-1);\n        }\n    }\n    \n    static void heapify(int idx, int size) {\n        if (found) return;\n        int left = 2 * idx;\n        int right = 2 * idx + 1;\n        int smaller;\n        \n        if (right <= size) {\n            smaller = A[left] < A[right] ? left : right;\n        } else if (left <= size) {\n            smaller = left;\n        } else {\n            return;\n        }\n        \n        if (A[smaller] < A[idx]) {\n            int tmp = A[idx]; A[idx] = A[smaller]; A[smaller] = tmp;\n            swapCount++;\n            if (swapCount == k) { found = true; return; }\n            heapify(smaller, size);\n        }\n    }\n    \n    static void buildMinHeap(int size) {\n        for (int i = size / 2; i >= 1; i--) {\n            if (found) return;\n            heapify(i, size);\n        }\n    }\n    \n    static void heapSort(int size) {\n        buildMinHeap(size);\n        if (found) return;\n        \n        for (int i = size; i >= 2; i--) {\n            int tmp = A[1]; A[1] = A[i]; A[i] = tmp;\n            swapCount++;\n            if (swapCount == k) { found = true; return; }\n            heapify(1, i - 1);\n            if (found) return;\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 알고리즘 수업 - 힙 정렬 2\n#include <iostream>\n#include <vector>\nusing namespace std;\n\nvector<int> A;\nint swapCount = 0;\nint k;\nbool found = false;\n\nvoid heapify(int idx, int size) {\n    if (found) return;\n    int left = 2 * idx;\n    int right = 2 * idx + 1;\n    int smaller;\n    \n    if (right <= size) {\n        smaller = A[left] < A[right] ? left : right;\n    } else if (left <= size) {\n        smaller = left;\n    } else {\n        return;\n    }\n    \n    if (A[smaller] < A[idx]) {\n        swap(A[idx], A[smaller]);\n        swapCount++;\n        if (swapCount == k) { found = true; return; }\n        heapify(smaller, size);\n    }\n}\n\nvoid buildMinHeap(int size) {\n    for (int i = size / 2; i >= 1; i--) {\n        if (found) return;\n        heapify(i, size);\n    }\n}\n\nvoid heapSort(int size) {\n    buildMinHeap(size);\n    if (found) return;\n    \n    for (int i = size; i >= 2; i--) {\n        swap(A[1], A[i]);\n        swapCount++;\n        if (swapCount == k) { found = true; return; }\n        heapify(1, i - 1);\n        if (found) return;\n    }\n}\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n >> k;\n    \n    A.resize(n + 1);\n    for (int i = 1; i <= n; i++) {\n        cin >> A[i];\n    }\n    \n    heapSort(n);\n    \n    if (found) {\n        for (int i = 1; i <= n; i++) {\n            cout << A[i];\n            if (i < n) cout << \" \";\n        }\n        cout << endl;\n    } else {\n        cout << -1 << endl;\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "4172": {
    "solutions": [
      {
        "language": "python",
        "code": "# sqrt log sin - 재귀 수열 계산\nimport math\n\nMOD = 1000000\nMAX_N = 1000001\n\n# 메모이제이션\nx = [0] * MAX_N\nx[0] = 1\n\nfor i in range(1, MAX_N):\n    a = int(i - math.sqrt(i))\n    b = int(math.log(i))\n    c = int(i * (math.sin(i) ** 2))\n    x[i] = (x[a] + x[b] + x[c]) % MOD\n\nimport sys\nfor line in sys.stdin:\n    i = int(line.strip())\n    if i == -1:\n        break\n    print(x[i])"
      },
      {
        "language": "java",
        "code": "// sqrt log sin - 재귀 수열 계산\nimport java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        int MOD = 1000000;\n        int MAX_N = 1000001;\n        \n        int[] x = new int[MAX_N];\n        x[0] = 1;\n        \n        for (int i = 1; i < MAX_N; i++) {\n            int a = (int)(i - Math.sqrt(i));\n            int b = (int)Math.log(i);\n            int c = (int)(i * Math.pow(Math.sin(i), 2));\n            x[i] = (x[a] + x[b] + x[c]) % MOD;\n        }\n        \n        Scanner sc = new Scanner(System.in);\n        while (sc.hasNextInt()) {\n            int i = sc.nextInt();\n            if (i == -1) break;\n            System.out.println(x[i]);\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// sqrt log sin - 재귀 수열 계산\n#include <iostream>\n#include <cmath>\nusing namespace std;\n\nconst int MOD = 1000000;\nconst int MAX_N = 1000001;\nint x[MAX_N];\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    x[0] = 1;\n    \n    for (int i = 1; i < MAX_N; i++) {\n        int a = (int)(i - sqrt(i));\n        int b = (int)log(i);\n        int c = (int)(i * pow(sin(i), 2));\n        x[i] = (x[a] + x[b] + x[c]) % MOD;\n    }\n    \n    int i;\n    while (cin >> i && i != -1) {\n        cout << x[i] << \"\\n\";\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "30618": {
    "solutions": [
      {
        "language": "python",
        "code": "# donstructive - 순열의 점수 최대화\n# 가운데에 큰 수를 배치하면 점수가 최대화됨\nn = int(input())\n\n# 가운데부터 큰 수를 배치\nresult = [0] * n\nleft, right = 0, n - 1\n\nfor i in range(n, 0, -1):\n    if (n - i) % 2 == 0:\n        result[left] = i\n        left += 1\n    else:\n        result[right] = i\n        right -= 1\n\nprint(*result)"
      },
      {
        "language": "java",
        "code": "// donstructive - 순열의 점수 최대화\nimport java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        \n        int[] result = new int[n];\n        int left = 0, right = n - 1;\n        \n        for (int i = n; i >= 1; i--) {\n            if ((n - i) % 2 == 0) {\n                result[left++] = i;\n            } else {\n                result[right--] = i;\n            }\n        }\n        \n        StringBuilder sb = new StringBuilder();\n        for (int i = 0; i < n; i++) {\n            sb.append(result[i]);\n            if (i < n - 1) sb.append(\" \");\n        }\n        System.out.println(sb);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// donstructive - 순열의 점수 최대화\n#include <iostream>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    int result[200001];\n    int left = 0, right = n - 1;\n    \n    for (int i = n; i >= 1; i--) {\n        if ((n - i) % 2 == 0) {\n            result[left++] = i;\n        } else {\n            result[right--] = i;\n        }\n    }\n    \n    for (int i = 0; i < n; i++) {\n        cout << result[i];\n        if (i < n - 1) cout << \" \";\n    }\n    cout << endl;\n    \n    return 0;\n}"
      }
    ]
  },
  "8891": {
    "solutions": [
      {
        "language": "python",
        "code": "# 점 숫자 - 대각선 순서로 번호 매기기\ndef num_to_point(n):\n    \"\"\"점 숫자를 좌표로 변환\"\"\"\n    # 대각선 k에서 합 = k+1\n    # 대각선 k까지의 점 개수 = k*(k+1)/2\n    # n이 속한 대각선 찾기\n    k = 1\n    total = 0\n    while total + k < n:\n        total += k\n        k += 1\n    # n은 대각선 k에 있음 (합이 k+1인 대각선)\n    pos = n - total  # 대각선에서의 위치 (1부터)\n    x = pos\n    y = k + 1 - pos\n    return x, y\n\ndef point_to_num(x, y):\n    \"\"\"좌표를 점 숫자로 변환\"\"\"\n    k = x + y - 1  # 대각선 번호 (합-1)\n    total = k * (k - 1) // 2  # 이전 대각선까지의 점 개수\n    return total + x\n\nt = int(input())\nfor _ in range(t):\n    a, b = map(int, input().split())\n    x1, y1 = num_to_point(a)\n    x2, y2 = num_to_point(b)\n    result = point_to_num(x1 + x2, y1 + y2)\n    print(result)"
      },
      {
        "language": "java",
        "code": "// 점 숫자 - 대각선 순서로 번호 매기기\nimport java.util.Scanner;\n\npublic class Main {\n    static int[] numToPoint(int n) {\n        int k = 1;\n        int total = 0;\n        while (total + k < n) {\n            total += k;\n            k++;\n        }\n        int pos = n - total;\n        int x = pos;\n        int y = k + 1 - pos;\n        return new int[]{x, y};\n    }\n    \n    static int pointToNum(int x, int y) {\n        int k = x + y - 1;\n        int total = k * (k - 1) / 2;\n        return total + x;\n    }\n    \n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int t = sc.nextInt();\n        \n        while (t-- > 0) {\n            int a = sc.nextInt();\n            int b = sc.nextInt();\n            \n            int[] p1 = numToPoint(a);\n            int[] p2 = numToPoint(b);\n            int result = pointToNum(p1[0] + p2[0], p1[1] + p2[1]);\n            System.out.println(result);\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 점 숫자 - 대각선 순서로 번호 매기기\n#include <iostream>\nusing namespace std;\n\npair<int, int> numToPoint(int n) {\n    int k = 1;\n    int total = 0;\n    while (total + k < n) {\n        total += k;\n        k++;\n    }\n    int pos = n - total;\n    int x = pos;\n    int y = k + 1 - pos;\n    return {x, y};\n}\n\nint pointToNum(int x, int y) {\n    int k = x + y - 1;\n    int total = k * (k - 1) / 2;\n    return total + x;\n}\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int t;\n    cin >> t;\n    \n    while (t--) {\n        int a, b;\n        cin >> a >> b;\n        \n        auto [x1, y1] = numToPoint(a);\n        auto [x2, y2] = numToPoint(b);\n        int result = pointToNum(x1 + x2, y1 + y2);\n        cout << result << \"\\n\";\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "26071": {
    "solutions": [
      {
        "language": "python",
        "code": "# 오락실에 간 총총이 - 모든 곰곰이를 한 칸에 모으기\nimport sys\ninput = sys.stdin.readline\n\nn = int(input())\ngrid = []\nfor _ in range(n):\n    grid.append(input().strip())\n\n# 곰곰이 위치 찾기\nmin_r, max_r = n, -1\nmin_c, max_c = n, -1\n\nfor i in range(n):\n    for j in range(n):\n        if grid[i][j] == 'G':\n            min_r = min(min_r, i)\n            max_r = max(max_r, i)\n            min_c = min(min_c, j)\n            max_c = max(max_c, j)\n\n# 모든 곰곰이를 한 칸에 모으려면\n# 상하좌우 버튼으로 전체가 같은 방향으로 이동\n# 필요한 이동 횟수 = 가로 범위 + 세로 범위\nprint((max_r - min_r) + (max_c - min_c))"
      },
      {
        "language": "java",
        "code": "// 오락실에 간 총총이\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        int n = Integer.parseInt(br.readLine());\n        \n        int minR = n, maxR = -1;\n        int minC = n, maxC = -1;\n        \n        for (int i = 0; i < n; i++) {\n            String row = br.readLine();\n            for (int j = 0; j < n; j++) {\n                if (row.charAt(j) == 'G') {\n                    minR = Math.min(minR, i);\n                    maxR = Math.max(maxR, i);\n                    minC = Math.min(minC, j);\n                    maxC = Math.max(maxC, j);\n                }\n            }\n        }\n        \n        System.out.println((maxR - minR) + (maxC - minC));\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 오락실에 간 총총이\n#include <iostream>\n#include <string>\n#include <algorithm>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    int minR = n, maxR = -1;\n    int minC = n, maxC = -1;\n    \n    for (int i = 0; i < n; i++) {\n        string row;\n        cin >> row;\n        for (int j = 0; j < n; j++) {\n            if (row[j] == 'G') {\n                minR = min(minR, i);\n                maxR = max(maxR, i);\n                minC = min(minC, j);\n                maxC = max(maxC, j);\n            }\n        }\n    }\n    \n    cout << (maxR - minR) + (maxC - minC) << endl;\n    return 0;\n}"
      }
    ]
  },
  "28015": {
    "solutions": [
      {
        "language": "python",
        "code": "# 영역 색칠 - 최소 붓질 횟수\nimport sys\ninput = sys.stdin.readline\n\nn, m = map(int, input().split())\ntotal = 0\n\nfor _ in range(n):\n    row = list(map(int, input().split()))\n    # 각 행에서 붓질 횟수 계산\n    # 연속된 같은 색은 한 번에 칠할 수 있음\n    # 다른 색으로 바뀌면 새로운 붓질 필요\n    \n    # 각 색별로 영역 개수 세기\n    count1 = 0  # 색 1의 영역 수\n    count2 = 0  # 색 2의 영역 수\n    prev = 0\n    \n    for cell in row:\n        if cell == 1 and prev != 1:\n            count1 += 1\n        elif cell == 2 and prev != 2:\n            count2 += 1\n        prev = cell\n    \n    # 덧칠이 가능하므로 한 색을 전체 칠하고 다른 색으로 덮을 수 있음\n    # 하지만 가로로만 칠할 수 있으므로 각 색의 연속 영역 수의 합이 최소\n    # 단, 색1, 색2 둘 다 있으면 겹치는 경우 최적화 가능\n    \n    # 실제로는 단순히 색이 0이 아닌 영역을 세면 됨\n    # 같은 색이 연속되면 한 번에 칠함\n    strokes = 0\n    prev = 0\n    for cell in row:\n        if cell != 0 and cell != prev:\n            strokes += 1\n        prev = cell if cell != 0 else prev\n    \n    # 다시 계산: 0이 아닌 칸마다 이전과 같으면 패스, 다르면 +1\n    strokes = 0\n    prev = 0\n    for cell in row:\n        if cell != 0:\n            if prev == 0 or cell != prev:\n                strokes += 1\n            prev = cell\n        else:\n            prev = 0\n    \n    total += strokes\n\nprint(total)"
      },
      {
        "language": "java",
        "code": "// 영역 색칠 - 최소 붓질 횟수\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int n = Integer.parseInt(st.nextToken());\n        int m = Integer.parseInt(st.nextToken());\n        \n        int total = 0;\n        \n        for (int i = 0; i < n; i++) {\n            st = new StringTokenizer(br.readLine());\n            int[] row = new int[m];\n            for (int j = 0; j < m; j++) {\n                row[j] = Integer.parseInt(st.nextToken());\n            }\n            \n            int strokes = 0;\n            int prev = 0;\n            \n            for (int j = 0; j < m; j++) {\n                if (row[j] != 0) {\n                    if (prev == 0 || row[j] != prev) {\n                        strokes++;\n                    }\n                    prev = row[j];\n                } else {\n                    prev = 0;\n                }\n            }\n            \n            total += strokes;\n        }\n        \n        System.out.println(total);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 영역 색칠 - 최소 붓질 횟수\n#include <iostream>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n, m;\n    cin >> n >> m;\n    \n    int total = 0;\n    \n    for (int i = 0; i < n; i++) {\n        int strokes = 0;\n        int prev = 0;\n        \n        for (int j = 0; j < m; j++) {\n            int cell;\n            cin >> cell;\n            \n            if (cell != 0) {\n                if (prev == 0 || cell != prev) {\n                    strokes++;\n                }\n                prev = cell;\n            } else {\n                prev = 0;\n            }\n        }\n        \n        total += strokes;\n    }\n    \n    cout << total << endl;\n    return 0;\n}"
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
