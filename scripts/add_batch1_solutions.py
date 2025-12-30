#!/usr/bin/env python3
"""첫 번째 배치 솔루션 추가 스크립트"""
import json

# 기존 baek_medium.json 읽기
with open('data/baekjoon/baek_medium.json', 'r', encoding='utf-8') as f:
    medium_data = json.load(f)

print(f"기존 솔루션 수: {len(medium_data)}")

# 새로운 솔루션
new_solutions = {
  "15687": {
    "solutions": [
      {
        "language": "cpp",
        "code": "// 직사각형 클래스 구현\n#include <iostream>\nusing namespace std;\n\nclass Rectangle {\npublic:\n    int width;   // 가로 길이\n    int height;  // 세로 길이\n    \n    // 생성자: 가로와 세로 길이를 초기화\n    Rectangle(int w, int h) : width(w), height(h) {}\n    \n    // 가로 길이 반환\n    int get_width() const {\n        return width;\n    }\n    \n    // 세로 길이 반환\n    int get_height() const {\n        return height;\n    }\n    \n    // 가로 길이 설정 (유효성 검사 포함)\n    void set_width(int w) {\n        if (w > 0 && w <= 1000) {\n            width = w;\n        }\n    }\n    \n    // 세로 길이 설정 (유효성 검사 포함)\n    void set_height(int h) {\n        if (h > 0 && h <= 2000) {\n            height = h;\n        }\n    }\n    \n    // 넓이 계산\n    int area() const {\n        return width * height;\n    }\n    \n    // 둘레 계산\n    int perimeter() const {\n        return 2 * (width + height);\n    }\n    \n    // 정사각형 여부 확인\n    bool is_square() const {\n        return width == height;\n    }\n};"
      }
    ]
  },
  "2090": {
    "solutions": [
      {
        "language": "python",
        "code": "# 조화평균 계산 - 분수 형태로 출력\nfrom fractions import Fraction\n\nn = int(input())\nnums = list(map(int, input().split()))\n\n# 모든 수의 역수의 합을 분수로 계산\nresult = Fraction(0)\nfor num in nums:\n    result += Fraction(1, num)\n\n# 역수를 취함\nif result.numerator == 0:\n    print(\"0\")\nelse:\n    final = Fraction(1, 1) / result\n    # 기약분수로 출력\n    if final.denominator == 1:\n        print(final.numerator)\n    else:\n        print(f\"{final.numerator}/{final.denominator}\")"
      },
      {
        "language": "java",
        "code": "// 조화평균 계산\nimport java.util.*;\nimport java.math.BigInteger;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) {\n            nums[i] = sc.nextInt();\n        }\n        \n        // 공통 분모 구함\n        BigInteger denom = BigInteger.ONE;\n        for (int num : nums) {\n            denom = denom.multiply(BigInteger.valueOf(num)).divide(denom.gcd(BigInteger.valueOf(num)));\n        }\n        \n        // 분자의 합 계산\n        BigInteger numer = BigInteger.ZERO;\n        for (int num : nums) {\n            numer = numer.add(denom.divide(BigInteger.valueOf(num)));\n        }\n        \n        // 결과는 denom / numer (역수)\n        BigInteger g = denom.gcd(numer);\n        BigInteger resNum = denom.divide(g);\n        BigInteger resDen = numer.divide(g);\n        \n        if (resDen.equals(BigInteger.ONE)) {\n            System.out.println(resNum);\n        } else {\n            System.out.println(resNum + \"/\" + resDen);\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 조화평균 계산\n#include <iostream>\nusing namespace std;\n\ntypedef long long ll;\n\nll gcd(ll a, ll b) { return b ? gcd(b, a % b) : a; }\nll lcm(ll a, ll b) { return a / gcd(a, b) * b; }\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    ll nums[10];\n    for (int i = 0; i < n; i++) {\n        cin >> nums[i];\n    }\n    \n    // 공통 분모 계산 (LCM)\n    ll denom = 1;\n    for (int i = 0; i < n; i++) {\n        denom = lcm(denom, nums[i]);\n    }\n    \n    // 분자의 합 계산\n    ll numer = 0;\n    for (int i = 0; i < n; i++) {\n        numer += denom / nums[i];\n    }\n    \n    // 결과는 denom / numer (역수)\n    ll g = gcd(denom, numer);\n    ll resNum = denom / g;\n    ll resDen = numer / g;\n    \n    if (resDen == 1) {\n        cout << resNum << endl;\n    } else {\n        cout << resNum << \"/\" << resDen << endl;\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "25375": {
    "solutions": [
      {
        "language": "python",
        "code": "# 아주 간단한 문제\n# gcd(x, y) = a이고 x + y = b인 자연수 쌍 존재 여부\nimport sys\ninput = sys.stdin.readline\n\nq = int(input())\nfor _ in range(q):\n    a, b = map(int, input().split())\n    # x = a*p, y = a*q (p, q는 서로소)\n    # a*(p + q) = b -> p + q = b/a >= 2\n    if b % a == 0 and b // a >= 2:\n        print(1)\n    else:\n        print(0)"
      },
      {
        "language": "java",
        "code": "// 아주 간단한 문제\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringBuilder sb = new StringBuilder();\n        \n        int q = Integer.parseInt(br.readLine());\n        while (q-- > 0) {\n            StringTokenizer st = new StringTokenizer(br.readLine());\n            long a = Long.parseLong(st.nextToken());\n            long b = Long.parseLong(st.nextToken());\n            \n            if (b % a == 0 && b / a >= 2) {\n                sb.append(1).append(\"\\n\");\n            } else {\n                sb.append(0).append(\"\\n\");\n            }\n        }\n        System.out.print(sb);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 아주 간단한 문제\n#include <iostream>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int q;\n    cin >> q;\n    \n    while (q--) {\n        long long a, b;\n        cin >> a >> b;\n        \n        if (b % a == 0 && b / a >= 2) {\n            cout << 1 << \"\\n\";\n        } else {\n            cout << 0 << \"\\n\";\n        }\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "29197": {
    "solutions": [
      {
        "language": "python",
        "code": "# 아침 태권도 - 원점에서 보이는 학생 수 계산\nimport sys\nfrom math import gcd\ninput = sys.stdin.readline\n\nn = int(input())\nseen = set()  # 이미 본 방향 저장\ncount = 0\n\nfor _ in range(n):\n    x, y = map(int, input().split())\n    \n    # 방향 벡터를 기약분수로 정규화\n    g = gcd(abs(x), abs(y))\n    dx, dy = x // g, y // g\n    \n    if (dx, dy) not in seen:\n        seen.add((dx, dy))\n        count += 1\n\nprint(count)"
      },
      {
        "language": "java",
        "code": "// 아침 태권도 - 원점에서 보이는 학생 수 계산\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    static int gcd(int a, int b) {\n        return b == 0 ? a : gcd(b, a % b);\n    }\n    \n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        int n = Integer.parseInt(br.readLine());\n        \n        Set<String> seen = new HashSet<>();\n        int count = 0;\n        \n        for (int i = 0; i < n; i++) {\n            StringTokenizer st = new StringTokenizer(br.readLine());\n            int x = Integer.parseInt(st.nextToken());\n            int y = Integer.parseInt(st.nextToken());\n            \n            int g = gcd(Math.abs(x), Math.abs(y));\n            int dx = x / g;\n            int dy = y / g;\n            \n            String key = dx + \",\" + dy;\n            if (!seen.contains(key)) {\n                seen.add(key);\n                count++;\n            }\n        }\n        \n        System.out.println(count);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 아침 태권도 - 원점에서 보이는 학생 수 계산\n#include <iostream>\n#include <set>\n#include <cmath>\nusing namespace std;\n\nint gcd(int a, int b) { return b ? gcd(b, a % b) : a; }\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    set<pair<int, int>> seen;\n    int count = 0;\n    \n    for (int i = 0; i < n; i++) {\n        int x, y;\n        cin >> x >> y;\n        \n        int g = gcd(abs(x), abs(y));\n        int dx = x / g;\n        int dy = y / g;\n        \n        if (seen.find({dx, dy}) == seen.end()) {\n            seen.insert({dx, dy});\n            count++;\n        }\n    }\n    \n    cout << count << endl;\n    \n    return 0;\n}"
      }
    ]
  },
  "15996": {
    "solutions": [
      {
        "language": "python",
        "code": "# 팩토리얼 나누기 - 르장드르 공식\nn, a = map(int, input().split())\n\nk = 0\npower = a\n\nwhile power <= n:\n    k += n // power\n    power *= a\n\nprint(k)"
      },
      {
        "language": "java",
        "code": "// 팩토리얼 나누기 - 르장드르 공식\nimport java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long n = sc.nextLong();\n        long a = sc.nextLong();\n        \n        long k = 0;\n        long power = a;\n        \n        while (power <= n) {\n            k += n / power;\n            power *= a;\n        }\n        \n        System.out.println(k);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 팩토리얼 나누기 - 르장드르 공식\n#include <iostream>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    long long n, a;\n    cin >> n >> a;\n    \n    long long k = 0;\n    long long power = a;\n    \n    while (power <= n) {\n        k += n / power;\n        power *= a;\n    }\n    \n    cout << k << endl;\n    \n    return 0;\n}"
      }
    ]
  },
  "11564": {
    "solutions": [
      {
        "language": "python",
        "code": "# 점프왕 최준민 - k 간격으로 [a, b] 구간의 k의 배수 개수\nimport math\n\nk, a, b = map(int, input().split())\n\n# a 이상의 최소 k의 배수\nfirst = math.ceil(a / k) * k\n# b 이하의 최대 k의 배수  \nlast = math.floor(b / k) * k\n\nif first > b or last < a:\n    print(0)\nelse:\n    count = (last - first) // k + 1\n    print(count)"
      },
      {
        "language": "java",
        "code": "// 점프왕 최준민\nimport java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long k = sc.nextLong();\n        long a = sc.nextLong();\n        long b = sc.nextLong();\n        \n        // a 이상의 최소 k의 배수\n        long first;\n        if (a >= 0) {\n            first = ((a + k - 1) / k) * k;\n        } else {\n            first = (a / k) * k;\n            if (first < a) first += k;\n        }\n        \n        // b 이하의 최대 k의 배수\n        long last;\n        if (b >= 0) {\n            last = (b / k) * k;\n        } else {\n            last = ((b - k + 1) / k) * k;\n            if (last > b) last -= k;\n        }\n        \n        if (first > b || last < a) {\n            System.out.println(0);\n        } else {\n            long count = (last - first) / k + 1;\n            System.out.println(count);\n        }\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 점프왕 최준민\n#include <iostream>\n#include <cmath>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    long long k, a, b;\n    cin >> k >> a >> b;\n    \n    // a 이상의 최소 k의 배수\n    long long first;\n    if (a % k == 0) first = a;\n    else if (a > 0) first = (a / k + 1) * k;\n    else first = (a / k) * k;\n    \n    // b 이하의 최대 k의 배수\n    long long last;\n    if (b % k == 0) last = b;\n    else if (b > 0) last = (b / k) * k;\n    else last = (b / k - 1) * k;\n    \n    if (first > b || last < a) {\n        cout << 0 << endl;\n    } else {\n        long long count = (last - first) / k + 1;\n        cout << count << endl;\n    }\n    \n    return 0;\n}"
      }
    ]
  },
  "31926": {
    "solutions": [
      {
        "language": "python",
        "code": "# 밤양갱 - 최소 입력 시간 계산\nimport math\n\nn = int(input())\n\n# daldidalgo 입력: 10초\ntime = 10\n\n# N개까지 복사로 늘리기: ceil(log2(N))번\nif n > 1:\n    time += math.ceil(math.log2(n))\n\n# daldidan의 마지막 'n' 입력: 1초\ntime += 1\n\nprint(time)"
      },
      {
        "language": "java",
        "code": "// 밤양갱 - 최소 입력 시간 계산\nimport java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long n = sc.nextLong();\n        \n        // daldidalgo 입력: 10초\n        long time = 10;\n        \n        // N개까지 복사로 늘리기\n        if (n > 1) {\n            time += (long) Math.ceil(Math.log(n) / Math.log(2));\n        }\n        \n        // daldidan의 마지막 'n' 입력: 1초\n        time += 1;\n        \n        System.out.println(time);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 밤양갱 - 최소 입력 시간 계산\n#include <iostream>\n#include <cmath>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    long long n;\n    cin >> n;\n    \n    // daldidalgo 입력: 10초\n    long long time = 10;\n    \n    // N개까지 복사로 늘리기\n    if (n > 1) {\n        time += (long long) ceil(log2((double)n));\n    }\n    \n    // daldidan의 마지막 'n' 입력: 1초\n    time += 1;\n    \n    cout << time << endl;\n    \n    return 0;\n}"
      }
    ]
  },
  "20003": {
    "solutions": [
      {
        "language": "python",
        "code": "# 거스름돈이 싫어요 - 분수들의 GCD 계산\ndef gcd(a, b):\n    while b:\n        a, b = b, a % b\n    return a\n\ndef lcm(a, b):\n    return a // gcd(a, b) * b\n\nn = int(input())\nfractions = []\nfor _ in range(n):\n    a, b = map(int, input().split())\n    g = gcd(a, b)\n    fractions.append((a // g, b // g))\n\n# 분수들의 GCD = gcd(분자들) / lcm(분모들)\nresult_num = fractions[0][0]\nresult_den = fractions[0][1]\n\nfor i in range(1, n):\n    num, den = fractions[i]\n    result_num = gcd(result_num, num)\n    result_den = lcm(result_den, den)\n\ng = gcd(result_num, result_den)\nresult_num //= g\nresult_den //= g\n\nprint(result_num, result_den)"
      },
      {
        "language": "java",
        "code": "// 거스름돈이 싫어요 - 분수들의 GCD 계산\nimport java.util.Scanner;\n\npublic class Main {\n    static long gcd(long a, long b) {\n        return b == 0 ? a : gcd(b, a % b);\n    }\n    \n    static long lcm(long a, long b) {\n        return a / gcd(a, b) * b;\n    }\n    \n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        \n        long[] nums = new long[n];\n        long[] dens = new long[n];\n        \n        for (int i = 0; i < n; i++) {\n            long a = sc.nextLong();\n            long b = sc.nextLong();\n            long g = gcd(a, b);\n            nums[i] = a / g;\n            dens[i] = b / g;\n        }\n        \n        long resNum = nums[0];\n        long resDen = dens[0];\n        \n        for (int i = 1; i < n; i++) {\n            resNum = gcd(resNum, nums[i]);\n            resDen = lcm(resDen, dens[i]);\n        }\n        \n        long g = gcd(resNum, resDen);\n        resNum /= g;\n        resDen /= g;\n        \n        System.out.println(resNum + \" \" + resDen);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 거스름돈이 싫어요 - 분수들의 GCD 계산\n#include <iostream>\nusing namespace std;\n\ntypedef long long ll;\n\nll gcd(ll a, ll b) { return b ? gcd(b, a % b) : a; }\nll lcm(ll a, ll b) { return a / gcd(a, b) * b; }\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    ll nums[50], dens[50];\n    \n    for (int i = 0; i < n; i++) {\n        ll a, b;\n        cin >> a >> b;\n        ll g = gcd(a, b);\n        nums[i] = a / g;\n        dens[i] = b / g;\n    }\n    \n    ll resNum = nums[0];\n    ll resDen = dens[0];\n    \n    for (int i = 1; i < n; i++) {\n        resNum = gcd(resNum, nums[i]);\n        resDen = lcm(resDen, dens[i]);\n    }\n    \n    ll g = gcd(resNum, resDen);\n    resNum /= g;\n    resDen /= g;\n    \n    cout << resNum << \" \" << resDen << endl;\n    \n    return 0;\n}"
      }
    ]
  },
  "18243": {
    "solutions": [
      {
        "language": "python",
        "code": "# Small World Network - 모든 정점 쌍의 최단 거리가 6 이하인지 확인\nimport sys\nfrom collections import deque\ninput = sys.stdin.readline\n\ndef bfs(start, n, adj):\n    dist = [-1] * (n + 1)\n    dist[start] = 0\n    q = deque([start])\n    \n    while q:\n        cur = q.popleft()\n        for next_node in adj[cur]:\n            if dist[next_node] == -1:\n                dist[next_node] = dist[cur] + 1\n                q.append(next_node)\n    \n    return dist\n\nn, k = map(int, input().split())\nadj = [[] for _ in range(n + 1)]\n\nfor _ in range(k):\n    a, b = map(int, input().split())\n    adj[a].append(b)\n    adj[b].append(a)\n\nis_small_world = True\n\nfor i in range(1, n + 1):\n    dist = bfs(i, n, adj)\n    for j in range(1, n + 1):\n        if dist[j] == -1 or dist[j] > 6:\n            is_small_world = False\n            break\n    if not is_small_world:\n        break\n\nprint(\"Small World!\" if is_small_world else \"Big World!\")"
      },
      {
        "language": "java",
        "code": "// Small World Network - Floyd-Warshall\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        \n        int n = Integer.parseInt(st.nextToken());\n        int k = Integer.parseInt(st.nextToken());\n        \n        int INF = 1000000;\n        int[][] dist = new int[n + 1][n + 1];\n        \n        for (int i = 1; i <= n; i++) {\n            Arrays.fill(dist[i], INF);\n            dist[i][i] = 0;\n        }\n        \n        for (int i = 0; i < k; i++) {\n            st = new StringTokenizer(br.readLine());\n            int a = Integer.parseInt(st.nextToken());\n            int b = Integer.parseInt(st.nextToken());\n            dist[a][b] = 1;\n            dist[b][a] = 1;\n        }\n        \n        for (int m = 1; m <= n; m++) {\n            for (int i = 1; i <= n; i++) {\n                for (int j = 1; j <= n; j++) {\n                    if (dist[i][m] + dist[m][j] < dist[i][j]) {\n                        dist[i][j] = dist[i][m] + dist[m][j];\n                    }\n                }\n            }\n        }\n        \n        boolean isSmallWorld = true;\n        for (int i = 1; i <= n && isSmallWorld; i++) {\n            for (int j = 1; j <= n && isSmallWorld; j++) {\n                if (dist[i][j] > 6) {\n                    isSmallWorld = false;\n                }\n            }\n        }\n        \n        System.out.println(isSmallWorld ? \"Small World!\" : \"Big World!\");\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// Small World Network - Floyd-Warshall\n#include <iostream>\n#include <algorithm>\nusing namespace std;\n\nconst int INF = 1000000;\nint dist[101][101];\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n, k;\n    cin >> n >> k;\n    \n    for (int i = 1; i <= n; i++) {\n        for (int j = 1; j <= n; j++) {\n            dist[i][j] = (i == j) ? 0 : INF;\n        }\n    }\n    \n    for (int i = 0; i < k; i++) {\n        int a, b;\n        cin >> a >> b;\n        dist[a][b] = 1;\n        dist[b][a] = 1;\n    }\n    \n    for (int m = 1; m <= n; m++) {\n        for (int i = 1; i <= n; i++) {\n            for (int j = 1; j <= n; j++) {\n                dist[i][j] = min(dist[i][j], dist[i][m] + dist[m][j]);\n            }\n        }\n    }\n    \n    bool isSmallWorld = true;\n    for (int i = 1; i <= n && isSmallWorld; i++) {\n        for (int j = 1; j <= n && isSmallWorld; j++) {\n            if (dist[i][j] > 6) {\n                isSmallWorld = false;\n            }\n        }\n    }\n    \n    cout << (isSmallWorld ? \"Small World!\" : \"Big World!\") << endl;\n    \n    return 0;\n}"
      }
    ]
  },
  "23758": {
    "solutions": [
      {
        "language": "python",
        "code": "# 중앙값 제거 - 두 개의 힙으로 중앙값 관리\nimport sys\nimport heapq\ninput = sys.stdin.readline\n\nn = int(input())\narr = list(map(int, input().split()))\n\n# 최대힙 (작은 값들)\nsmall = []\n# 최소힙 (큰 값들)\nlarge = []\n\nfor num in arr:\n    if len(small) == 0 or num <= -small[0]:\n        heapq.heappush(small, -num)\n    else:\n        heapq.heappush(large, num)\n    \n    if len(small) > len(large) + 1:\n        heapq.heappush(large, -heapq.heappop(small))\n    elif len(large) > len(small):\n        heapq.heappush(small, -heapq.heappop(large))\n\ncount = 0\n\nwhile -small[0] > 0:\n    median = -heapq.heappop(small)\n    new_val = median // 2\n    \n    if len(small) == 0 or new_val <= -small[0]:\n        heapq.heappush(small, -new_val)\n    else:\n        heapq.heappush(large, new_val)\n    \n    if len(small) > len(large) + 1:\n        heapq.heappush(large, -heapq.heappop(small))\n    elif len(large) > len(small):\n        heapq.heappush(small, -heapq.heappop(large))\n    \n    count += 1\n\nprint(count)"
      },
      {
        "language": "java",
        "code": "// 중앙값 제거 - 두 개의 힙으로 중앙값 관리\nimport java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        int n = Integer.parseInt(br.readLine());\n        StringTokenizer st = new StringTokenizer(br.readLine());\n        \n        PriorityQueue<Long> small = new PriorityQueue<>(Collections.reverseOrder());\n        PriorityQueue<Long> large = new PriorityQueue<>();\n        \n        for (int i = 0; i < n; i++) {\n            long num = Long.parseLong(st.nextToken());\n            \n            if (small.isEmpty() || num <= small.peek()) {\n                small.offer(num);\n            } else {\n                large.offer(num);\n            }\n            \n            if (small.size() > large.size() + 1) {\n                large.offer(small.poll());\n            } else if (large.size() > small.size()) {\n                small.offer(large.poll());\n            }\n        }\n        \n        long count = 0;\n        \n        while (small.peek() > 0) {\n            long median = small.poll();\n            long newVal = median / 2;\n            \n            if (small.isEmpty() || newVal <= small.peek()) {\n                small.offer(newVal);\n            } else {\n                large.offer(newVal);\n            }\n            \n            if (small.size() > large.size() + 1) {\n                large.offer(small.poll());\n            } else if (large.size() > small.size()) {\n                small.offer(large.poll());\n            }\n            \n            count++;\n        }\n        \n        System.out.println(count);\n    }\n}"
      },
      {
        "language": "cpp",
        "code": "// 중앙값 제거 - 두 개의 힙으로 중앙값 관리\n#include <iostream>\n#include <queue>\n#include <vector>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    int n;\n    cin >> n;\n    \n    priority_queue<long long> small;\n    priority_queue<long long, vector<long long>, greater<long long>> large;\n    \n    for (int i = 0; i < n; i++) {\n        long long num;\n        cin >> num;\n        \n        if (small.empty() || num <= small.top()) {\n            small.push(num);\n        } else {\n            large.push(num);\n        }\n        \n        if (small.size() > large.size() + 1) {\n            large.push(small.top());\n            small.pop();\n        } else if (large.size() > small.size()) {\n            small.push(large.top());\n            large.pop();\n        }\n    }\n    \n    long long count = 0;\n    \n    while (small.top() > 0) {\n        long long median = small.top();\n        small.pop();\n        long long newVal = median / 2;\n        \n        if (small.empty() || newVal <= small.top()) {\n            small.push(newVal);\n        } else {\n            large.push(newVal);\n        }\n        \n        if (small.size() > large.size() + 1) {\n            large.push(small.top());\n            small.pop();\n        } else if (large.size() > small.size()) {\n            small.push(large.top());\n            large.pop();\n        }\n        \n        count++;\n    }\n    \n    cout << count << endl;\n    \n    return 0;\n}"
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
