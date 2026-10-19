"""Render the Work 2 data-flow diagram with STRIDE threat annotations - English."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from shared.diagram import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).with_name("dfd-en.png")

d = Diagram(1720, 1120, "Juice Shop data-flow diagram (DFD) with STRIDE threats")

d.box("E1", 40, 470, 230, 150, "E1\nUser browser\n(untrusted)", "entity")

d.box("P1", 350, 70, 240, 130, "1.0\nAuthentication", "process")
d.box("P2", 350, 280, 240, 130, "2.0\nBrowse & search", "process")
d.box("P3", 350, 490, 240, 130, "3.0\nReviews", "process")
d.box("P4", 350, 700, 240, 130, "4.0\nBasket & checkout", "process")

d.box("D1", 800, 70, 240, 130, "D1  Users\nemail / password hash", "store")
d.box("D2", 800, 280, 240, 130, "D2  Products\nname / price", "store")
d.box("D3", 800, 490, 240, 130, "D3  Reviews\nreview text", "store")
d.box("D4", 800, 700, 240, 130, "D4  Basket/Orders\nitems / address", "store")

d.arrow("E1", "P1", "login", offset=-45)
d.arrow("P1", "D1", "query / verify", offset=-25)
d.arrow("E1", "P2", "search", offset=-30)
d.arrow("P2", "D2", "SELECT", offset=-25)
d.arrow("E1", "P3", "review", offset=-30)
d.arrow("P3", "D3", "INSERT", offset=-25)
d.arrow("E1", "P4", "order", offset=-30)
d.arrow("P4", "D4", "write order", offset=-25)
d.arrow("P1", "E1", "JWT", offset=18)
d.arrow("D2", "P2", "results", offset=18)

d.box("T1", 1150, 70, 480, 110, "S  Spoofing: steal JWT, impersonate user\n(consequence of XSS)", "loss")
d.box("T2", 1150, 280, 480, 110, "T  Tampering: SQL injection in search\n(A03 Injection)", "loss")
d.box("T3", 1150, 490, 480, 110, "I/T  XSS: review text echoed unescaped\n-> session hijacking", "loss")
d.box("T4", 1150, 700, 480, 110, "E  Elevation: change prices / read others' basket\n(A01 Broken Access Control)", "loss")

d.arrow("P1", "T1", "", dashed=True)
d.arrow("P2", "T2", "", dashed=True)
d.arrow("P3", "T3", "", dashed=True)
d.arrow("P4", "T4", "", dashed=True)

d.box("L1", 60, 900, 460, 80, "Legend: entity / process / data store", "state")
d.box("L2", 60, 1000, 460, 80, "Red bubble = STRIDE threat and where it lands", "loss")
d.box("L3", 520, 900, 460, 80, "D  Denial of Service: search/blind SQLi", "process")
d.box("L4", 520, 1000, 460, 80, "R  Repudiation: no audit log", "process")

path = d.save(str(OUT))
print("saved", path)
