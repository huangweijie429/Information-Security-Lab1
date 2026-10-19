"""Render the Work 3 attack digraph (SQL injection) to PNG."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from shared.diagram import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).with_name("digraph.png")

d = Diagram(1860, 1180, "SQL 注入攻击的有向图模型：S0 → Si → Sk")

# ---- states -----------------------------------------------------------
d.box("S0", 50, 470, 230, 140, "S0\n正常状态\n攻击者未介入", "entity")
d.box("S1", 330, 150, 215, 140, "S1\n踩点侦察\n爬站/端口扫描", "state")
d.box("S2", 660, 150, 215, 140, "S2\n输入点探测\n引号触发报错", "state")
d.box("S3", 985, 150, 215, 140, "S3\n注入成功\n绕过认证/UNION", "state")
d.box("S4", 1300, 50, 215, 140, "S4\n导出数据\nusers/posts 全表", "state")
d.box("S5", 1300, 300, 215, 140, "S5\n篡改或删除\nUPDATE/DROP", "state")
d.box("S6", 985, 640, 215, 140, "S6\n盲注/重查询\n布尔、SLEEP()", "state")
d.box("K1", 1610, 50, 200, 140, "Sk1\n信息窃取", "loss")
d.box("K2", 1610, 300, 200, 140, "Sk2\n信息篡改或丢失", "loss")
d.box("K3", 1610, 640, 200, 140, "Sk3\n拒绝服务", "loss")

# ---- transitions (labels = attacker actions, one per edge) ------------
d.arrow("S0", "S1", "发起攻击", offset=-30)
d.arrow("S1", "S2", "发现接口", offset=-38)
d.arrow("S2", "S3", "构造注入", offset=-38)
d.arrow("S2", "S6", "改用盲注", offset=-30)
d.arrow("S3", "S4", "读取全表", offset=-42)
d.arrow("S3", "S5", "越权写入", offset=42)
d.arrow("S4", "K1", "数据外泄", offset=-40)
d.arrow("S5", "K2", "数据损坏", offset=-40)
d.arrow("S6", "K3", "资源耗尽", offset=-40)

# ---- legend -----------------------------------------------------------
d.box("L1", 60, 940, 330, 90, "图例  S0 初始态：无入侵者影响", "entity")
d.box("L2", 60, 1050, 330, 90, "图例  Si 中间态：攻击者动作", "state")
d.box("L3", 420, 940, 350, 90, "图例  Sk 终态：造成损失", "loss")
d.box("L4", 420, 1050, 350, 90, "每条边 = 一个已描述的攻击动作", "process")

path = d.save(str(OUT))
print("saved", path)
