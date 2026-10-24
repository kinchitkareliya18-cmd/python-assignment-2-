
def minimum_cost_path(matrix):
    """Return minimum path cost and path coordinates."""
    rows = len(matrix)
    cols = len(matrix[0])

    # dp[r][c] stores the minimum cost to reach cell (r, c).
    dp = [[0] * cols for _ in range(rows)]
    parent = [[None] * cols for _ in range(rows)]

    dp[0][0] = matrix[0][0]

    for r in range(1, rows):
        dp[r][0] = dp[r - 1][0] + matrix[r][0]
        parent[r][0] = (r - 1, 0)

    for c in range(1, cols):
        dp[0][c] = dp[0][c - 1] + matrix[0][c]
        parent[0][c] = (0, c - 1)

    for r in range(1, rows):
        for c in range(1, cols):
            if dp[r - 1][c] <= dp[r][c - 1]:
                dp[r][c] = dp[r - 1][c] + matrix[r][c]
                parent[r][c] = (r - 1, c)
            else:
                dp[r][c] = dp[r][c - 1] + matrix[r][c]
                parent[r][c] = (r, c - 1)

    # Reconstruct path from destination to source.
    path = []
    r, c = rows - 1, cols - 1

    while True:
        path.append((r, c))
        if (r, c) == (0, 0):
            break
        r, c = parent[r][c]

    path.reverse()
    return dp[-1][-1], path, dp


def main():
    print("Matrix Path Optimizer")
    print("---------------------")

    try:
        rows = int(input("Enter number of rows: "))
        cols = int(input("Enter number of columns: "))

        if rows <= 0 or cols <= 0:
            print("Rows and columns must be positive.")
            return

        print("Enter each matrix row as space-separated integers:")

        matrix = []
        for r in range(rows):
            row = list(map(int, input(f"Row {r + 1}: ").split()))

            if len(row) != cols:
                print(f"Error: Enter exactly {cols} values.")
                return

            matrix.append(row)

        cost, path, dp = minimum_cost_path(matrix)

        print("\nMinimum path cost:", cost)
        print("Path (1-based row, column coordinates):")
        print(" -> ".join(f"({r + 1},{c + 1})" for r, c in path))

        print("\nDynamic programming table:")
        for row in dp:
            print(" ".join(f"{value:5}" for value in row))

    except ValueError:
        print("Invalid input. Enter integers only.")


if __name__ == "__main__":
    main()
