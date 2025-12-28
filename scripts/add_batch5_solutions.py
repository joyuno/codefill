#!/usr/bin/env python3
"""다섯 번째 배치 솔루션 추가 스크립트"""
import json

# 기존 baek_medium.json 읽기
with open('data/baekjoon/baek_medium.json', 'r', encoding='utf-8') as f:
    medium_data = json.load(f)

print(f"기존 솔루션 수: {len(medium_data)}")

# 새로운 솔루션
new_solutions = {
  "17358": {
    "solutions": [
      {
        "language": "python",
        "code": "# 복불복으로 지구 멸망 - N개 컵을 N/2 쌍으로 나누는 경우의 수\n# (2k-1)!! = (2k-1) * (2k-3) * ... * 3 * 1\nimport sys\ninput = sys.stdin.readline\n\nMOD = 10**9 + 7\n\nn = int(input())\n\n# 결과 = (n-1)!! = (n-1) * (n-3) * ... * 3 * 1\nresult = 1\nfor i in range(n - 1, 0, -2):\n    result = (result * i) % MOD\n\nprint(result)"
      },
      {
        "language": "java",
        "code": "// 복불복으로 지구 멸망\nimport java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        \n        long MOD = 1_000_000_007L;\n        long result = 1;\n        \n        for (int i = n - 1; i > 0; i -= 2) {\n            result = (result * i) % MOD;\n        }\n        \n        System.out.println(result);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 복불복으로 지구 멸망\n#include <iostream>\nusing namespace std;\n\nconst long long MOD = 1e9 + 7;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    long long result = 1;\n    for (int i = n - 1; i > 0; i -= 2) {\n        result = (result * i) % MOD;\n    }\n    \n    cout << result << endl;\n    return 0;\n}"
      }
    ]
  },
  "18248": {
    "solutions": [
      {
        "language": "python",
        "code": "# 제야의 종 - 가능한 상황인지 판별\nimport sys\ninput = sys.stdin.readline\n\nn, m = map(int, input().split())\npeople = []\nfor _ in range(n):\n    people.append(list(map(int, input().split())))\n\n# 두 사람 i, j에 대해\n# 어떤 타종 k에서 i가 듣고 j가 못들으면, i가 더 가까움\n# 어떤 타종 l에서 i가 못듣고 j가 들으면, j가 더 가까움\n# 이 두 조건이 동시에 성립하면 모순\n\npossible = True\n\nfor i in range(n):\n    for j in range(i + 1, n):\n        i_closer = False  # i가 더 가까운 경우 존재\n        j_closer = False  # j가 더 가까운 경우 존재\n        \n        for k in range(m):\n            if people[i][k] == 1 and people[j][k] == 0:\n                i_closer = True\n            if people[i][k] == 0 and people[j][k] == 1:\n                j_closer = True\n        \n        if i_closer and j_closer:\n            possible = False\n            break\n    if not possible:\n        break\n\nprint(\"YES\" if possible else \"NO\")"
      },
      {
        "language": "java",
        "code": "// 제야의 종\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int n = Integer.parseInt(st.nextToken());\n        int m = Integer.parseInt(st.nextToken());\n        \n        int[][] people = new int[n][m];\n        for (int i = 0; i < n; i++) {\n            st = new StringTokenizer(br.readLine());\n            for (int j = 0; j < m; j++) {\n                people[i][j] = Integer.parseInt(st.nextToken());\n            }\n        }\n        \n        boolean possible = true;\n        \n        outer:\n        for (int i = 0; i < n; i++) {\n            for (int j = i + 1; j < n; j++) {\n                boolean iCloser = false, jCloser = false;\n                \n                for (int k = 0; k < m; k++) {\n                    if (people[i][k] == 1 && people[j][k] == 0) iCloser = true;\n                    if (people[i][k] == 0 && people[j][k] == 1) jCloser = true;\n                }\n                \n                if (iCloser && jCloser) {\n                    possible = false;\n                    break outer;\n                }\n            }\n        }\n        \n        System.out.println(possible ? \"YES\" : \"NO\");\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 제야의 종\n#include <iostream>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n, m;\n    cin >> n >> m;\n    \n    int people[1001][101];\n    for (int i = 0; i < n; i++) {\n        for (int j = 0; j < m; j++) {\n            cin >> people[i][j];\n        }\n    }\n    \n    bool possible = true;\n    \n    for (int i = 0; i < n && possible; i++) {\n        for (int j = i + 1; j < n && possible; j++) {\n            bool iCloser = false, jCloser = false;\n            \n            for (int k = 0; k < m; k++) {\n                if (people[i][k] == 1 && people[j][k] == 0) iCloser = true;\n                if (people[i][k] == 0 && people[j][k] == 1) jCloser = true;\n            }\n            \n            if (iCloser && jCloser) {\n                possible = false;\n            }\n        }\n    }\n    \n    cout << (possible ? \"YES\" : \"NO\") << endl;\n    return 0;\n}"
      }
    ]
  },
  "24061": {
    "solutions": [
      {
        "language": "python",
        "code": "# 알고리즘 수업 - 병합 정렬 2\nimport sys\nsys.setrecursionlimit(600000)\ninput = sys.stdin.readline\n\nn, k = map(int, input().split())\nA = [0] + list(map(int, input().split()))  # 1-indexed\n\nchange_count = 0\nresult = None\n\ndef merge(p, q, r):\n    global change_count, result\n    if result:\n        return\n    \n    tmp = [0] * (r - p + 2)\n    i, j, t = p, q + 1, 1\n    \n    while i <= q and j <= r:\n        if A[i] <= A[j]:\n            tmp[t] = A[i]\n            i += 1\n        else:\n            tmp[t] = A[j]\n            j += 1\n        t += 1\n    \n    while i <= q:\n        tmp[t] = A[i]\n        i += 1\n        t += 1\n    \n    while j <= r:\n        tmp[t] = A[j]\n        j += 1\n        t += 1\n    \n    # 배열에 복사\n    for i in range(p, r + 1):\n        change_count += 1\n        A[i] = tmp[i - p + 1]\n        if change_count == k:\n            result = A[1:]\n            return\n\ndef merge_sort(p, r):\n    global result\n    if result:\n        return\n    if p < r:\n        q = (p + r) // 2\n        merge_sort(p, q)\n        if result:\n            return\n        merge_sort(q + 1, r)\n        if result:\n            return\n        merge(p, q, r)\n\nmerge_sort(1, n)\n\nif result:\n    print(' '.join(map(str, result)))\nelse:\n    print(-1)"
      },
      {
        "language": "java",
        "code": "// 알고리즘 수업 - 병합 정렬 2\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    static int[] A;\n    static int changeCount = 0;\n    static int k;\n    static boolean found = false;\n    \n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int n = Integer.parseInt(st.nextToken());\n        k = Integer.parseInt(st.nextToken());\n        \n        A = new int[n + 1];\n        st = new StringTokenizer(br.readLine());\n        for (int i = 1; i <= n; i++) {\n            A[i] = Integer.parseInt(st.nextToken());\n        }\n        \n        mergeSort(1, n);\n        \n        if (found) {\n            StringBuilder sb = new StringBuilder();\n            for (int i = 1; i <= n; i++) {\n                sb.append(A[i]);\n                if (i < n) sb.append(\" \");\n            }\n            System.out.println(sb);\n        } else {\n            System.out.println(-1);\n        }\n    }\n    \n    static void merge(int p, int q, int r) {\n        if (found) return;\n        int[] tmp = new int[r - p + 2];\n        int i = p, j = q + 1, t = 1;\n        \n        while (i <= q && j <= r) {\n            if (A[i] <= A[j]) tmp[t++] = A[i++];\n            else tmp[t++] = A[j++];\n        }\n        while (i <= q) tmp[t++] = A[i++];\n        while (j <= r) tmp[t++] = A[j++];\n        \n        for (int idx = p; idx <= r; idx++) {\n            changeCount++;\n            A[idx] = tmp[idx - p + 1];\n            if (changeCount == k) { found = true; return; }\n        }\n    }\n    \n    static void mergeSort(int p, int r) {\n        if (found) return;\n        if (p < r) {\n            int q = (p + r) / 2;\n            mergeSort(p, q);\n            if (found) return;\n            mergeSort(q + 1, r);\n            if (found) return;\n            merge(p, q, r);\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 알고리즘 수업 - 병합 정렬 2\n#include <iostream>\n#include <vector>\nusing namespace std;\n\nvector<int> A;\nint changeCount = 0;\nint k;\nbool found = false;\n\nvoid merge(int p, int q, int r) {\n    if (found) return;\n    vector<int> tmp(r - p + 2);\n    int i = p, j = q + 1, t = 1;\n    \n    while (i <= q && j <= r) {\n        if (A[i] <= A[j]) tmp[t++] = A[i++];\n        else tmp[t++] = A[j++];\n    }\n    while (i <= q) tmp[t++] = A[i++];\n    while (j <= r) tmp[t++] = A[j++];\n    \n    for (int idx = p; idx <= r; idx++) {\n        changeCount++;\n        A[idx] = tmp[idx - p + 1];\n        if (changeCount == k) { found = true; return; }\n    }\n}\n\nvoid mergeSort(int p, int r) {\n    if (found) return;\n    if (p < r) {\n        int q = (p + r) / 2;\n        mergeSort(p, q);\n        if (found) return;\n        mergeSort(q + 1, r);\n        if (found) return;\n        merge(p, q, r);\n    }\n}\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n >> k;\n    \n    A.resize(n + 1);\n    for (int i = 1; i <= n; i++) {\n        cin >> A[i];\n    }\n    \n    mergeSort(1, n);\n    \n    if (found) {\n        for (int i = 1; i <= n; i++) {\n            cout << A[i];\n            if (i < n) cout << \" \";\n        }\n        cout << endl;\n    } else {\n        cout << -1 << endl;\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "26091": {
    "solutions": [
      {
        "language": "python",
        "code": "# 현대모비스 소프트웨어 아카데미 - 2인 팀 최대 개수\nimport sys\ninput = sys.stdin.readline\n\nn, m = map(int, input().split())\nabilities = sorted(map(int, input().split()))\n\n# 투 포인터: 가장 작은 것과 큰 것 매칭\nleft, right = 0, n - 1\nteams = 0\n\nwhile left < right:\n    if abilities[left] + abilities[right] >= m:\n        teams += 1\n        left += 1\n        right -= 1\n    else:\n        left += 1  # 너무 약함, 더 강한 사람 필요\n\nprint(teams)"
      },
      {
        "language": "java",
        "code": "// 현대모비스 소프트웨어 아카데미\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int n = Integer.parseInt(st.nextToken());\n        long m = Long.parseLong(st.nextToken());\n        \n        long[] abilities = new long[n];\n        st = new StringTokenizer(br.readLine());\n        for (int i = 0; i < n; i++) {\n            abilities[i] = Long.parseLong(st.nextToken());\n        }\n        Arrays.sort(abilities);\n        \n        int left = 0, right = n - 1;\n        int teams = 0;\n        \n        while (left < right) {\n            if (abilities[left] + abilities[right] >= m) {\n                teams++;\n                left++;\n                right--;\n            } else {\n                left++;\n            }\n        }\n        \n        System.out.println(teams);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 현대모비스 소프트웨어 아카데미\n#include <iostream>\n#include <algorithm>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    long long m;\n    cin >> n >> m;\n    \n    long long abilities[100001];\n    for (int i = 0; i < n; i++) {\n        cin >> abilities[i];\n    }\n    sort(abilities, abilities + n);\n    \n    int left = 0, right = n - 1;\n    int teams = 0;\n    \n    while (left < right) {\n        if (abilities[left] + abilities[right] >= m) {\n            teams++;\n            left++;\n            right--;\n        } else {\n            left++;\n        }\n    }\n    \n    cout << teams << endl;\n    return 0;\n}"
      }
    ]
  },
  "12033": {
    "solutions": [
      {
        "language": "python",
        "code": "# 김인천씨의 식료품가게 - 할인가격 찾기\nimport sys\ninput = sys.stdin.readline\n\nt = int(input())\n\nfor case in range(1, t + 1):\n    n = int(input())\n    prices = list(map(int, input().split()))\n    \n    # 정상가 * 0.75 = 할인가\n    # 할인가 찾기: 작은 것부터 매칭\n    \n    from collections import Counter\n    cnt = Counter(prices)\n    discounts = []\n    \n    for p in sorted(prices):\n        if cnt[p] > 0:\n            cnt[p] -= 1\n            discounts.append(p)\n            # 정상가 = p * 4 / 3\n            normal = p * 4 // 3\n            if cnt[normal] > 0:\n                cnt[normal] -= 1\n            # 혹시 소수점 문제로 정상가 다를 수 있음\n    \n    print(f\"Case #{case}: {' '.join(map(str, discounts))}\")"
      },
      {
        "language": "java",
        "code": "// 김인천씨의 식료품가게 - 할인가격 찾기\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int t = sc.nextInt();\n        \n        for (int c = 1; c <= t; c++) {\n            int n = sc.nextInt();\n            int[] prices = new int[2 * n];\n            TreeMap<Integer, Integer> cnt = new TreeMap<>();\n            \n            for (int i = 0; i < 2 * n; i++) {\n                prices[i] = sc.nextInt();\n                cnt.put(prices[i], cnt.getOrDefault(prices[i], 0) + 1);\n            }\n            \n            Arrays.sort(prices);\n            List<Integer> discounts = new ArrayList<>();\n            \n            for (int p : prices) {\n                if (cnt.getOrDefault(p, 0) > 0) {\n                    cnt.put(p, cnt.get(p) - 1);\n                    discounts.add(p);\n                    int normal = p * 4 / 3;\n                    if (cnt.getOrDefault(normal, 0) > 0) {\n                        cnt.put(normal, cnt.get(normal) - 1);\n                    }\n                }\n            }\n            \n            StringBuilder sb = new StringBuilder();\n            sb.append(\"Case #\").append(c).append(\": \");\n            for (int i = 0; i < discounts.size(); i++) {\n                sb.append(discounts.get(i));\n                if (i < discounts.size() - 1) sb.append(\" \");\n            }\n            System.out.println(sb);\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 김인천씨의 식료품가게 - 할인가격 찾기\n#include <iostream>\n#include <map>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int t;\n    cin >> t;\n    \n    for (int c = 1; c <= t; c++) {\n        int n;\n        cin >> n;\n        \n        vector<int> prices(2 * n);\n        map<int, int> cnt;\n        \n        for (int i = 0; i < 2 * n; i++) {\n            cin >> prices[i];\n            cnt[prices[i]]++;\n        }\n        \n        sort(prices.begin(), prices.end());\n        vector<int> discounts;\n        \n        for (int p : prices) {\n            if (cnt[p] > 0) {\n                cnt[p]--;\n                discounts.push_back(p);\n                int normal = p * 4 / 3;\n                if (cnt[normal] > 0) {\n                    cnt[normal]--;\n                }\n            }\n        }\n        \n        cout << \"Case #\" << c << \": \";\n        for (int i = 0; i < (int)discounts.size(); i++) {\n            cout << discounts[i];\n            if (i < (int)discounts.size() - 1) cout << \" \";\n        }\n        cout << \"\\n\";\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "9367": {
    "solutions": [
      {
        "language": "python",
        "code": "# 관리 난항 - 렌트카 비용 계산\nimport sys\nfrom collections import defaultdict\nimport math\ninput = sys.stdin.readline\n\nwhile True:\n    line = input().split()\n    if not line or len(line) < 2:\n        break\n    c, e = int(line[0]), int(line[1])\n    if c == 0 and e == 0:\n        break\n    \n    # 자동차 정보\n    cars = {}\n    for _ in range(c):\n        parts = input().split()\n        name = parts[0]\n        price, pickup, rate = int(parts[1]), int(parts[2]), int(parts[3])\n        cars[name] = {'price': price, 'pickup': pickup, 'rate': rate}\n    \n    # 사건 기록\n    events = []\n    for _ in range(e):\n        parts = input().split()\n        time = int(parts[0])\n        person = parts[1]\n        etype = parts[2]\n        if etype == 'p':  # pickup\n            car = parts[3]\n            events.append((time, person, 'p', car))\n        elif etype == 'r':  # return\n            km = int(parts[3])\n            events.append((time, person, 'r', km))\n        elif etype == 'a':  # accident\n            damage = int(parts[3])\n            events.append((time, person, 'a', damage))\n    \n    # 시뮬레이션\n    rentals = {}  # person -> car\n    costs = defaultdict(int)  # person -> cost\n    inconsistent = set()\n    \n    for event in events:\n        time, person, etype = event[0], event[1], event[2]\n        \n        if etype == 'p':\n            car = event[3]\n            if car not in cars:\n                inconsistent.add(person)\n            else:\n                rentals[person] = car\n                costs[person] += cars[car]['pickup']\n        elif etype == 'r':\n            km = event[3]\n            if person not in rentals:\n                inconsistent.add(person)\n            else:\n                car = rentals[person]\n                costs[person] += cars[car]['rate'] * km\n                del rentals[person]\n        elif etype == 'a':\n            damage = event[3]\n            if person not in rentals:\n                inconsistent.add(person)\n            else:\n                car = rentals[person]\n                repair = math.ceil(cars[car]['price'] * damage / 100)\n                costs[person] += repair\n    \n    # 아직 반납 안 한 사람\n    for person in rentals:\n        inconsistent.add(person)\n    \n    # 결과 출력\n    all_people = sorted(set(costs.keys()) | inconsistent)\n    for person in all_people:\n        if person in inconsistent:\n            print(f\"{person} INCONSISTENT\")\n        else:\n            print(f\"{person} {costs[person]}\")"
      },
      {
        "language": "java",
        "code": "// 관리 난항\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        \n        while (sc.hasNext()) {\n            int c = sc.nextInt();\n            int e = sc.nextInt();\n            if (c == 0 && e == 0) break;\n            \n            Map<String, int[]> cars = new HashMap<>();\n            for (int i = 0; i < c; i++) {\n                String name = sc.next();\n                int price = sc.nextInt();\n                int pickup = sc.nextInt();\n                int rate = sc.nextInt();\n                cars.put(name, new int[]{price, pickup, rate});\n            }\n            \n            Map<String, String> rentals = new HashMap<>();\n            Map<String, Long> costs = new TreeMap<>();\n            Set<String> inconsistent = new HashSet<>();\n            \n            for (int i = 0; i < e; i++) {\n                int time = sc.nextInt();\n                String person = sc.next();\n                String type = sc.next();\n                \n                if (!costs.containsKey(person)) costs.put(person, 0L);\n                \n                if (type.equals(\"p\")) {\n                    String car = sc.next();\n                    if (!cars.containsKey(car)) {\n                        inconsistent.add(person);\n                    } else {\n                        rentals.put(person, car);\n                        costs.put(person, costs.get(person) + cars.get(car)[1]);\n                    }\n                } else if (type.equals(\"r\")) {\n                    int km = sc.nextInt();\n                    if (!rentals.containsKey(person)) {\n                        inconsistent.add(person);\n                    } else {\n                        String car = rentals.get(person);\n                        costs.put(person, costs.get(person) + (long)cars.get(car)[2] * km);\n                        rentals.remove(person);\n                    }\n                } else {\n                    int damage = sc.nextInt();\n                    if (!rentals.containsKey(person)) {\n                        inconsistent.add(person);\n                    } else {\n                        String car = rentals.get(person);\n                        long repair = (long)Math.ceil(cars.get(car)[0] * damage / 100.0);\n                        costs.put(person, costs.get(person) + repair);\n                    }\n                }\n            }\n            \n            for (String person : rentals.keySet()) {\n                inconsistent.add(person);\n            }\n            \n            for (String person : costs.keySet()) {\n                if (inconsistent.contains(person)) {\n                    System.out.println(person + \" INCONSISTENT\");\n                } else {\n                    System.out.println(person + \" \" + costs.get(person));\n                }\n            }\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 관리 난항\n#include <iostream>\n#include <map>\n#include <set>\n#include <cmath>\n#include <string>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int c, e;\n    while (cin >> c >> e && (c || e)) {\n        map<string, tuple<int,int,int>> cars;\n        for (int i = 0; i < c; i++) {\n            string name;\n            int price, pickup, rate;\n            cin >> name >> price >> pickup >> rate;\n            cars[name] = {price, pickup, rate};\n        }\n        \n        map<string, string> rentals;\n        map<string, long long> costs;\n        set<string> inconsistent;\n        \n        for (int i = 0; i < e; i++) {\n            int time;\n            string person, type;\n            cin >> time >> person >> type;\n            \n            if (costs.find(person) == costs.end()) costs[person] = 0;\n            \n            if (type == \"p\") {\n                string car;\n                cin >> car;\n                if (cars.find(car) == cars.end()) {\n                    inconsistent.insert(person);\n                } else {\n                    rentals[person] = car;\n                    costs[person] += get<1>(cars[car]);\n                }\n            } else if (type == \"r\") {\n                int km;\n                cin >> km;\n                if (rentals.find(person) == rentals.end()) {\n                    inconsistent.insert(person);\n                } else {\n                    string car = rentals[person];\n                    costs[person] += (long long)get<2>(cars[car]) * km;\n                    rentals.erase(person);\n                }\n            } else {\n                int damage;\n                cin >> damage;\n                if (rentals.find(person) == rentals.end()) {\n                    inconsistent.insert(person);\n                } else {\n                    string car = rentals[person];\n                    long long repair = (long long)ceil(get<0>(cars[car]) * damage / 100.0);\n                    costs[person] += repair;\n                }\n            }\n        }\n        \n        for (auto& [person, car] : rentals) {\n            inconsistent.insert(person);\n        }\n        \n        for (auto& [person, cost] : costs) {\n            if (inconsistent.count(person)) {\n                cout << person << \" INCONSISTENT\\n\";\n            } else {\n                cout << person << \" \" << cost << \"\\n\";\n            }\n        }\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "16131": {
    "solutions": [
      {
        "language": "python",
        "code": "# 기숙사 서바이벌 - 홍 군과 조 군의 방 차이\nimport sys\ninput = sys.stdin.readline\n\nn, a, b, m = map(int, input().split())\nplus = list(map(int, input().split()))  # 상점\nminus = list(map(int, input().split()))  # 벌점\n\n# 각 학생의 초기 방: 학번대로\n# 1번 학생(홍 군): 1번 방\n# A번 학생(조 군): A번 방\n\n# m주 동안 시뮬레이션\n# 매주 상점-벌점에 따라 순위 재배정\n\nstudents = list(range(1, n + 1))  # 학생 번호 (1-indexed)\nscores = [0] * (n + 1)  # 각 학생의 점수 (상점-벌점)\n\ngood_weeks = 0\nmax_consecutive = 0\ncurrent_consecutive = 0\n\nfor week in range(m):\n    # 현재 주의 방 배치 (점수 기준 정렬)\n    # 점수가 높을수록 좋은 방 (낮은 번호)\n    ranking = sorted(range(1, n + 1), key=lambda x: -scores[x])\n    room = {}  # 학생 -> 방 번호\n    for i, student in enumerate(ranking):\n        room[student] = i + 1\n    \n    # 홍 군(1번)과 조 군(A번)의 방 차이 확인\n    diff = abs(room[1] - room[a])\n    if diff <= b:\n        good_weeks += 1\n        current_consecutive += 1\n        max_consecutive = max(max_consecutive, current_consecutive)\n    else:\n        current_consecutive = 0\n    \n    # 마지막 주가 아니면 점수 업데이트\n    if week < m - 1:\n        for i in range(n):\n            scores[i + 1] += plus[i] - minus[i]\n\nprint(good_weeks, max_consecutive)"
      },
      {
        "language": "java",
        "code": "// 기숙사 서바이벌\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        int n = Integer.parseInt(st.nextToken());\n        int a = Integer.parseInt(st.nextToken());\n        int b = Integer.parseInt(st.nextToken());\n        int m = Integer.parseInt(st.nextToken());\n        \n        int[] plus = new int[n + 1];\n        int[] minus = new int[n + 1];\n        int[] scores = new int[n + 1];\n        \n        st = new StringTokenizer(br.readLine());\n        for (int i = 1; i <= n; i++) plus[i] = Integer.parseInt(st.nextToken());\n        st = new StringTokenizer(br.readLine());\n        for (int i = 1; i <= n; i++) minus[i] = Integer.parseInt(st.nextToken());\n        \n        int goodWeeks = 0;\n        int maxConsecutive = 0;\n        int currentConsecutive = 0;\n        \n        for (int week = 0; week < m; week++) {\n            Integer[] students = new Integer[n];\n            for (int i = 0; i < n; i++) students[i] = i + 1;\n            final int w = week;\n            Arrays.sort(students, (x, y) -> scores[y] - scores[x]);\n            \n            int[] room = new int[n + 1];\n            for (int i = 0; i < n; i++) {\n                room[students[i]] = i + 1;\n            }\n            \n            int diff = Math.abs(room[1] - room[a]);\n            if (diff <= b) {\n                goodWeeks++;\n                currentConsecutive++;\n                maxConsecutive = Math.max(maxConsecutive, currentConsecutive);\n            } else {\n                currentConsecutive = 0;\n            }\n            \n            if (week < m - 1) {\n                for (int i = 1; i <= n; i++) {\n                    scores[i] += plus[i] - minus[i];\n                }\n            }\n        }\n        \n        System.out.println(goodWeeks + \" \" + maxConsecutive);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 기숙사 서바이벌\n#include <iostream>\n#include <algorithm>\n#include <vector>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n, a, b, m;\n    cin >> n >> a >> b >> m;\n    \n    vector<int> plus_score(n + 1), minus_score(n + 1), scores(n + 1, 0);\n    \n    for (int i = 1; i <= n; i++) cin >> plus_score[i];\n    for (int i = 1; i <= n; i++) cin >> minus_score[i];\n    \n    int goodWeeks = 0;\n    int maxConsecutive = 0;\n    int currentConsecutive = 0;\n    \n    for (int week = 0; week < m; week++) {\n        vector<int> students(n);\n        for (int i = 0; i < n; i++) students[i] = i + 1;\n        sort(students.begin(), students.end(), [&](int x, int y) {\n            return scores[x] > scores[y];\n        });\n        \n        vector<int> room(n + 1);\n        for (int i = 0; i < n; i++) {\n            room[students[i]] = i + 1;\n        }\n        \n        int diff = abs(room[1] - room[a]);\n        if (diff <= b) {\n            goodWeeks++;\n            currentConsecutive++;\n            maxConsecutive = max(maxConsecutive, currentConsecutive);\n        } else {\n            currentConsecutive = 0;\n        }\n        \n        if (week < m - 1) {\n            for (int i = 1; i <= n; i++) {\n                scores[i] += plus_score[i] - minus_score[i];\n            }\n        }\n    }\n    \n    cout << goodWeeks << \" \" << maxConsecutive << endl;\n    return 0;\n}"
      }
    ]
  },
  "31836": {
    "solutions": [
      {
        "language": "python",
        "code": "# 피보나치 기념품 - 피보나치 수의 합이 같도록 분배\n# F(n) = F(n-2) + F(n-1) 이므로 F(n) = F(n-2) + F(n-1)\n# 즉 F(n-2)와 (n-1)번째를 세림, n번째를 성주에게\nn = int(input())\n\nif n == 1:\n    print(1)\n    print(1)\n    print(1)\n    print(1)\nelif n == 2:\n    print(1)\n    print(1)\n    print(1)\n    print(2)\nelse:\n    # F(n) = F(n-2) + F(n-1)\n    # F(1) + F(3) + F(5) + ... 와 F(2) + F(4) + F(6) + ...\n    # 짝수 번호와 홀수 번호로 나누면 합이 다름\n    \n    # 더 간단한 패턴: F(n) = F(1) + F(2) + ... + F(n-2) + F(n-1) - sum(F(1)..F(n-2))\n    # 실제로 F(n) = F(n-1) + F(n-2)\n    # 세림: n-2, 성주: n이면 F(n-2) = F(n) - F(n-1)이므로 다름\n    \n    # 정답: 세림에게 1, n-1번, 성주에게 n번\n    # F(1) + F(n-1) = 1 + F(n-1)\n    # F(n) = F(n-1) + F(n-2)\n    # 이것도 다름...\n    \n    # 올바른 분배: F(n) = F(n-1) + F(n-2)\n    # 세림: n-2와 어떤 것들, 성주: n과 나머지\n    # F(n-2) + F(n-1) = F(n)!\n    # 세림: n-2, n-1번 / 성주: n번\n    print(2)\n    print(n - 2, n - 1)\n    print(1)\n    print(n)"
      },
      {
        "language": "java",
        "code": "// 피보나치 기념품\nimport java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        \n        if (n == 1) {\n            System.out.println(1);\n            System.out.println(1);\n            System.out.println(1);\n            System.out.println(1);\n        } else if (n == 2) {\n            System.out.println(1);\n            System.out.println(1);\n            System.out.println(1);\n            System.out.println(2);\n        } else {\n            // F(n) = F(n-1) + F(n-2)\n            System.out.println(2);\n            System.out.println((n - 2) + \" \" + (n - 1));\n            System.out.println(1);\n            System.out.println(n);\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 피보나치 기념품\n#include <iostream>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    if (n == 1) {\n        cout << \"1\\n1\\n1\\n1\\n\";\n    } else if (n == 2) {\n        cout << \"1\\n1\\n1\\n2\\n\";\n    } else {\n        // F(n) = F(n-1) + F(n-2)\n        cout << 2 << \"\\n\";\n        cout << n - 2 << \" \" << n - 1 << \"\\n\";\n        cout << 1 << \"\\n\";\n        cout << n << \"\\n\";\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "9333": {
    "solutions": [
      {
        "language": "python",
        "code": "# 돈 갚기 - 이자와 상환 시뮬레이션\nimport math\n\nt = int(input())\n\nfor _ in range(t):\n    r, b, m = map(float, input().split())\n    \n    # 센트 단위로 계산\n    debt = int(b * 100)  # 센트\n    monthly = int(m * 100)  # 센트\n    rate = r / 100\n    \n    months = 0\n    while debt > 0 and months <= 1200:\n        # 이자 붙이기 (반올림)\n        interest = debt * rate\n        # 0.5센트 이상이면 올림\n        interest = int(interest + 0.5)\n        debt += interest\n        \n        # 상환\n        debt -= monthly\n        months += 1\n    \n    if months > 1200:\n        print(\"impossible\")\n    else:\n        print(months)"
      },
      {
        "language": "java",
        "code": "// 돈 갚기\nimport java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int t = sc.nextInt();\n        \n        while (t-- > 0) {\n            double r = sc.nextDouble();\n            double b = sc.nextDouble();\n            double m = sc.nextDouble();\n            \n            long debt = Math.round(b * 100);\n            long monthly = Math.round(m * 100);\n            double rate = r / 100;\n            \n            int months = 0;\n            while (debt > 0 && months <= 1200) {\n                double interest = debt * rate;\n                debt += Math.round(interest);\n                debt -= monthly;\n                months++;\n            }\n            \n            if (months > 1200) {\n                System.out.println(\"impossible\");\n            } else {\n                System.out.println(months);\n            }\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 돈 갚기\n#include <iostream>\n#include <cmath>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int t;\n    cin >> t;\n    \n    while (t--) {\n        double r, b, m;\n        cin >> r >> b >> m;\n        \n        long long debt = llround(b * 100);\n        long long monthly = llround(m * 100);\n        double rate = r / 100;\n        \n        int months = 0;\n        while (debt > 0 && months <= 1200) {\n            double interest = debt * rate;\n            debt += llround(interest);\n            debt -= monthly;\n            months++;\n        }\n        \n        if (months > 1200) {\n            cout << \"impossible\\n\";\n        } else {\n            cout << months << \"\\n\";\n        }\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "12001": {
    "solutions": [
      {
        "language": "python",
        "code": "# Load Balancing - 4개 영역의 소 수 균형 맞추기\nimport sys\ninput = sys.stdin.readline\n\nline = input().split()\nn, b = int(line[0]), int(line[1])\n\ncows = []\nfor _ in range(n):\n    x, y = map(int, input().split())\n    cows.append((x, y))\n\n# x, y 좌표들 수집\nxs = sorted(set(c[0] for c in cows))\nys = sorted(set(c[1] for c in cows))\n\nmin_m = n\n\n# 모든 가능한 분할선 시도\nfor a in range(0, b + 1, 2):  # x = a\n    for b_val in range(0, b + 1, 2):  # y = b_val\n        # 4개 영역의 소 수 계산\n        cnt = [0, 0, 0, 0]  # 좌하, 우하, 좌상, 우상\n        for x, y in cows:\n            idx = 0\n            if x > a:\n                idx += 1\n            if y > b_val:\n                idx += 2\n            cnt[idx] += 1\n        \n        m = max(cnt)\n        min_m = min(min_m, m)\n\nprint(min_m)"
      },
      {
        "language": "java",
        "code": "// Load Balancing\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int b = sc.nextInt();\n        \n        int[][] cows = new int[n][2];\n        for (int i = 0; i < n; i++) {\n            cows[i][0] = sc.nextInt();\n            cows[i][1] = sc.nextInt();\n        }\n        \n        int minM = n;\n        \n        for (int a = 0; a <= b; a += 2) {\n            for (int bVal = 0; bVal <= b; bVal += 2) {\n                int[] cnt = new int[4];\n                for (int[] cow : cows) {\n                    int idx = 0;\n                    if (cow[0] > a) idx += 1;\n                    if (cow[1] > bVal) idx += 2;\n                    cnt[idx]++;\n                }\n                \n                int m = Math.max(Math.max(cnt[0], cnt[1]), Math.max(cnt[2], cnt[3]));\n                minM = Math.min(minM, m);\n            }\n        }\n        \n        System.out.println(minM);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// Load Balancing\n#include <iostream>\n#include <algorithm>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n, b;\n    cin >> n >> b;\n    \n    int cows[101][2];\n    for (int i = 0; i < n; i++) {\n        cin >> cows[i][0] >> cows[i][1];\n    }\n    \n    int minM = n;\n    \n    for (int a = 0; a <= b; a += 2) {\n        for (int bVal = 0; bVal <= b; bVal += 2) {\n            int cnt[4] = {0};\n            for (int i = 0; i < n; i++) {\n                int idx = 0;\n                if (cows[i][0] > a) idx += 1;\n                if (cows[i][1] > bVal) idx += 2;\n                cnt[idx]++;\n            }\n            \n            int m = max({cnt[0], cnt[1], cnt[2], cnt[3]});\n            minM = min(minM, m);\n        }\n    }\n    \n    cout << minM << endl;\n    return 0;\n}"
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
