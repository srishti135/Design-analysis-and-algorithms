import os
import sys
import time

# Enable ANSI escape sequences on Windows 10+
if sys.platform == "win32":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def parse_input_file(filepath):
    if not os.path.exists(filepath):
        sys.exit(f"Error: Input file '{filepath}' not found.")

    test_cases = []
    current_test = None
    case_num = 0

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue

        if cleaned.startswith("#Test"):
            case_num += 1
            current_test = {"id": case_num, "items": []}
            test_cases.append(current_test)
        elif current_test is not None:
            parts = list(map(int, cleaned.split()))
            if "n" not in current_test:
                current_test["n"] = parts[0]
                current_test["W"] = parts[1]
            else:
                current_test["items"].append((parts[0], parts[1]))

    return test_cases


def print_ascii_table(case_id, dp, current_i, current_w, weights, values, W, n):
    col_width = 5
    header = "Item \\ W |" + "".join(f"{w:>{col_width}}" for w in range(W + 1))
    separator = "-" * len(header)

    # ANSI: Clear screen and reset cursor to home (top-left)
    sys.stdout.write("\033[H\033[J")
    sys.stdout.write(f"--- Test Case #{case_id} ---\n")
    sys.stdout.write(
        f"Evaluating Item {current_i} [Weight: {weights[current_i-1]}, Value: {values[current_i-1]}]\n"
    )
    sys.stdout.write(f"Current Capacity Slot: {current_w}/{W}\n\n")
    sys.stdout.write(header + "\n" + separator + "\n")

    for i in range(n + 1):
        row_str = f"  i={i:<4} |"
        for w in range(W + 1):
            val = dp[i][w]
            cell_str = str(val) if val != -1 else "."
            if i == current_i and w == current_w:
                # Highlight active cell in bright bold green
                row_str += f"\033[1;32m{cell_str:>{col_width}}\033[0m"
            else:
                row_str += f"{cell_str:>{col_width}}"
        sys.stdout.write(row_str + "\n")

    sys.stdout.flush()
    time.sleep(0.03)


def solve_knapsack(case_id, n, W, weights, values):
    dp = [[-1] * (W + 1) for _ in range(n + 1)]

    # Initialize item 0 row to 0 across all capacities
    for w in range(W + 1):
        dp[0][w] = 0

    # Only animate if table fits cleanly in standard terminal viewports
    should_animate = (n <= 15 and W <= 30)

    for i in range(1, n + 1):
        wt = weights[i - 1]
        val = values[i - 1]

        # Start from capacity 0 to properly handle zero-weight items
        for w in range(0, W + 1):
            if wt <= w:
                dp[i][w] = max(dp[i - 1][w], val + dp[i - 1][w - wt])
            else:
                dp[i][w] = dp[i - 1][w]

            if should_animate:
                print_ascii_table(case_id, dp, i, w, weights, values, W, n)

    if not should_animate:
        print(f"Test Case #{case_id} (n={n}, W={W}): Solved instantly (skipped live animation due to dimensions).")

    return dp[n][W]


def run_pipeline(input_filename, output_filename):
    test_cases = parse_input_file(input_filename)
    results = []

    for case in test_cases:
        cid = case["id"]
        n = case["n"]
        W = case["W"]
        weights = [item[0] for item in case["items"][:n]]
        values = [item[1] for item in case["items"][:n]]

        max_val = solve_knapsack(cid, n, W, weights, values)

        # Formatted string: #Test <id> input (n W) <result>
        result_line = f"#Test {cid} input ({n} {W}) {max_val}"
        results.append(result_line)

        if n <= 15 and W <= 30:
            time.sleep(0.5)

    with open(output_filename, "w", encoding="utf-8") as f_out:
        for line in results:
            f_out.write(line + "\n")

    print(f"\nExecution complete. Output written to '{output_filename}':")
    for line in results:
        print(line)


if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "Knapsack data (2).txt"
    out = sys.argv[2] if len(sys.argv) > 2 else "result.txt"
    run_pipeline(inp, out)