"""Render the Work 2 data-flow diagram with STRIDE threat annotations."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from shared.diagram import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).with_name("dfd.png")

d = Diagram(1720, 1120, "Juice Shop 数据流图（DFD）与 STRIDE 威胁标注")

# ---- external entity / processes / stores ----------------------------
d.box("E1", 40, 470, 230, 150, "E1\n用户浏览器\n(不可信)", "entity")

d.box("P1", 350, 70, 240, 130, "1.0\n认证与登录", "process")
d.box("P2", 350, 280, 240, 130, "2.0\n商品浏览与搜索", "process")
d.box("P3", 350, 490, 240, 130, "3.0\n评论提交与展示", "process")
d.box("P4", 350, 700, 240, 130, "4.0\n购物车与下单", "process")

d.box("D1", 800, 70, 240, 130, "D1  Users\n邮箱 / 口令哈希", "store")
d.box("D2", 800, 280, 240, 130, "D2  Products\n名称 / 价格", "store")
d.box("D3", 800, 490, 240, 130, "D3  Reviews\n评论文本", "store")
d.box("D4", 800, 700, 240, 130, "D4  Basket/Orders\n条目 / 地址", "store")

# ---- data flows --------------------------------------------------------
d.arrow("E1", "P1", "凭据", offset=-20)
d.arrow("P1", "D1", "查询 / 校验", offset=-25)
d.arrow("E1", "P2", "搜索词", offset=-20)
d.arrow("P2", "D2", "SELECT", offset=-25)
d.arrow("E1", "P3", "评论文本", offset=-20)
d.arrow("P3", "D3", "INSERT", offset=-25)
d.arrow("E1", "P4", "下单请求", offset=-20)
d.arrow("P4", "D4", "写订单", offset=-25)
d.arrow("P1", "E1", "JWT", offset=18)
d.arrow("D2", "P2", "结果页", offset=18)

# ---- STRIDE threat badges --------------------------------------------
d.box("T1", 1150, 70, 480, 110, "S  Spoofing：窃取 JWT 后冒充用户\n（XSS 的后果）", "loss")
d.box("T2", 1150, 280, 480, 110, "T  Tampering：搜索参数 SQL 注入\n（A03 Injection）", "loss")
d.box("T3", 1150, 490, 480, 110, "I/T  XSS：评论文本未经转义回显\n→ 会话劫持", "loss")
d.box("T4", 1150, 700, 480, 110, "E  Elevation：越权改价 / 读他人购物车\n（A01 Broken Access Control）", "loss")

d.arrow("P1", "T1", "", dashed=True)
d.arrow("P2", "T2", "", dashed=True)
d.arrow("P3", "T3", "", dashed=True)
d.arrow("P4", "T4", "", dashed=True)

d.box("L1", 60, 900, 460, 80, "图例：实体 / 处理 / 数据存储", "state")
d.box("L2", 60, 1000, 420, 80, "红色气泡 = STRIDE 威胁及其落点", "loss")
d.box("L3", 520, 900, 420, 80, "D  Denial of Service：搜索/盲注拖垮服务", "process")
d.box("L4", 520, 1000, 420, 80, "R  Repudiation：缺少操作审计日志", "process")

path = d.save(str(OUT))
print("saved", path)
