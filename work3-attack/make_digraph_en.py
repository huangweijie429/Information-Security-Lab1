"""Render the Work 3 attack digraph (SQL injection) to PNG - English version."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from shared.diagram import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).with_name("digraph-en.png")

d = Diagram(1860, 1180, "SQL injection attack digraph: S0 -> Si -> Sk")

d.box("S0", 50, 470, 230, 140, "S0\nNormal operation\nattacker idle", "entity")
d.box("S1", 330, 150, 215, 140, "S1\nReconnaissance\ncrawl / port scan", "state")
d.box("S2", 660, 150, 215, 140, "S2\nInput probing\nquote -> SQL error", "state")
d.box("S3", 985, 150, 215, 140, "S3\nInjection succeeded\nauth bypass / UNION", "state")
d.box("S4", 1300, 50, 215, 140, "S4\nData exfiltration\nusers/posts dump", "state")
d.box("S5", 1300, 300, 215, 140, "S5\nTampering/delete\nUPDATE / DROP", "state")
d.box("S6", 985, 640, 215, 140, "S6\nBlind injection\nboolean, SLEEP()", "state")
d.box("K1", 1610, 50, 200, 140, "Sk1\nData theft", "loss")
d.box("K2", 1610, 300, 200, 140, "Sk2\nData tampered / lost", "loss")
d.box("K3", 1610, 640, 200, 140, "Sk3\nDenial of service", "loss")

d.arrow("S0", "S1", "start", offset=-30)
d.arrow("S1", "S2", "find endpoint", offset=-38)
d.arrow("S2", "S3", "craft payload", offset=-38)
d.arrow("S2", "S6", "go blind", offset=-30)
d.arrow("S3", "S4", "read tables", offset=-42)
d.arrow("S3", "S5", "write / drop", offset=42)
d.arrow("S4", "K1", "exfiltrate", offset=-40)
d.arrow("S5", "K2", "corrupt", offset=-55)
d.arrow("S6", "K3", "exhaust pool", offset=-40)

d.box("L1", 60, 940, 330, 90, "Legend  S0: initial state", "entity")
d.box("L2", 60, 1050, 330, 90, "Legend  Si: attacker action", "state")
d.box("L3", 420, 940, 350, 90, "Legend  Sk: final state, loss", "loss")
d.box("L4", 420, 1050, 350, 90, "Each edge = one described action", "process")

path = d.save(str(OUT))
print("saved", path)
