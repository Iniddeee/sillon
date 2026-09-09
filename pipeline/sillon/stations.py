from pathlib import Path

import duckdb


def search_stations(csv: Path, query: str) -> list[tuple[int, str]]:
    con = duckdb.connect()
    rows = con.execute(
        """
        SELECT DISTINCT BPUIC, HALTESTELLEN_NAME
        FROM read_csv(?, delim=';', header=true, all_varchar=true)
        WHERE PRODUKT_ID = 'Zug' AND HALTESTELLEN_NAME ILIKE ?
        ORDER BY HALTESTELLEN_NAME
        """,
        [str(csv), f"%{query}%"],
    ).fetchall()
    return [(int(bpuic), name) for bpuic, name in rows]
