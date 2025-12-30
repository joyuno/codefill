import json
import sys

with open("/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json", "r") as f:
    data = json.load(f)

# Find medium difficulty problems with empty solutions and valid input_output
empty_medium_problems = []
for i, p in enumerate(data):
    if (p.get("difficulty") == "medium" and
        (p.get("solutions") is None or len(p.get("solutions", [])) == 0) and
        p.get("input_output") and p.get("input_output") != "null"):
        empty_medium_problems.append((i, p))

print(f"Total empty medium problems: {len(empty_medium_problems)}")

start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 1110
end_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 1140

# Show problems
for idx in range(start_idx, min(end_idx, len(empty_medium_problems))):
    orig_idx, p = empty_medium_problems[idx]
    print("="*80)
    print(f"Index: {idx}, Original Index: {orig_idx}")
    pid = p["id"]
    print(f"ID: {pid}")
    name = p.get("name", "N/A")
    print(f"Name: {name}")
    question = p.get("question", "N/A")[:2000]
    print(f"Question: {question}")
    io = p.get("input_output", "N/A")
    print(f"Input/Output: {io}")
    print()
