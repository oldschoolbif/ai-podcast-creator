"""List non-killed mutmut mutants from the local cache."""

import argparse
import sqlite3
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="List surviving mutmut mutants.")
    parser.add_argument("--limit", type=int, default=200, help="Number of rows to display (default: 200)")
    args = parser.parse_args()

    cache_path = Path(".mutmut-cache")
    if not cache_path.exists():
        print("Mutmut cache not found. Run mutation tests first.")
        return

    conn = sqlite3.connect(cache_path)
    cur = conn.cursor()

    sql = """
    SELECT
        SourceFile.filename,
        Line.line_number,
        Mutant.status,
        Line.line,
        Mutant.id
    FROM Mutant
    JOIN Line ON Line.id = Mutant.line
    JOIN SourceFile ON SourceFile.id = Line.sourcefile
    WHERE Mutant.status NOT IN ('killed', 'ok_killed')
    ORDER BY SourceFile.filename, Line.line_number
    """
    rows = cur.execute(sql).fetchall()
    conn.close()

    total = len(rows)
    print(f"Total mutants needing attention: {total}")
    limit = args.limit or total
    for filename, line_number, status, line_text, mid in rows[:limit]:
        snippet = (line_text or "").strip()
        print(f"{status:<10} {filename}:{line_number} -> {snippet} (id={mid})")

    if total > limit:
        print(f"... ({total - limit} more not shown)")


if __name__ == "__main__":
    main()

