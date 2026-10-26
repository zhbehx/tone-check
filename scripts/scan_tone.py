#!/usr/bin/env python3
"""检测职场消息的语气风险：甩锅、被动攻击、模糊承诺、命令式、责任稀释。

用法：
    python scripts/scan_tone.py message.txt
    python scripts/scan_tone.py message.txt --explain
    python scripts/scan_tone.py message.txt --json
    python scripts/scan_tone.py message.txt --fail-over 60

退出码：0 正常；--fail-over 触发时 1；文件错误 2。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# (正则, 维度, 级别, 对方的读法, 改写)
# 级别：H=高(12) M=中(6) L=低(2)
RULES: list[tuple[str, str, str, str, str]] = [
    # ---- 甩锅 ----
    (r"我之前(说过|提过|讲过)|早就(说过|提过)|不是(说|讲)过", "甩锅", "H",
     "你在撇清责任，暗示是我的错", "「可能我没说清楚，我再确认一遍：…」"),
    (r"这不是我(负责|的)|不归我管|我只负责", "甩锅", "H",
     "别找我，我不帮你", "「这块现在是 X 在跟，我把他拉进来」"),
    (r"你自己(看|去|查|找)|自己想办法", "甩锅", "H",
     "自己去找，别烦我", "「在文档第 3 节，具体是：…」"),
    (r"你们(部门|那边|团队)|是你们", "甩锅", "M",
     "我们不是一伙的", "「这事卡在 A 和 B 的接口上，两边一起看」"),
    (r"我(已经)?(发|抄)了?邮件|我通知过了", "甩锅", "M",
     "我尽到义务了，剩下不关我事", "「邮件里约了 X，还没回复，下午我再催一次」"),
    (r"按我(说|要求)的做(不就行|就行了|就好)", "甩锅", "H",
     "你不听我的才出事", "「我们当时的方案是 X，现在结果是 Y，差在哪对一下」"),

    # ---- 被动攻击 ----
    (r"呵呵|哈哈(?![哈哈])|微笑", "被动攻击", "H", "我在鄙视你", "（删掉，什么都别加）"),
    (r"随便|都行|无所谓|你决定就好", "被动攻击", "M",
     "我有意见但不说", "「我倾向 A，因为…；B 也行，你定」"),
    (r"你开心就好|随你|您随意", "被动攻击", "H",
     "你会后悔的", "「我担心的是 X，如果没问题就按你的来」"),
    (r"行吧|好吧|那算了|算了", "被动攻击", "M", "我不情愿", "「可以，那我按这个推进，X 日前给结果」"),
    (r"呢[~～]|哦[~～]|呀[~～]", "被动攻击", "L", "可能被读成阴阳怪气", "去掉语气词"),
    (r"你觉得(合适|好)吗|您觉得呢", "被动攻击", "M",
     "我觉得不合适，但我不直说", "「我有个顾虑：X，要不要再确认一下」"),
    (r"没事[，,]\s*我(自己|来)|我自己弄", "被动攻击", "M", "你欠我的", "「这次我来，下次这块提前一天给我可以吗」"),

    # ---- 模糊承诺 ----
    (r"尽快|尽早|抽空|有空(的)?时候", "模糊承诺", "H",
     "我不知道什么时候，也不会催你", "「今天 18:00 前给你初版」"),
    (r"我看看|我看下|再说吧|研究一下", "模糊承诺", "M",
     "我可能会忘", "「我下午看完，17:00 前给你结论」"),
    (r"回头(聊|说|看)|改天", "模糊承诺", "M", "我不想聊", "「明天上午 10 点我们 15 分钟对一下？」"),
    (r"应该(没问题|可以|行)|大概(可以|没问题)|差不多", "模糊承诺", "H",
     "有问题我不负责", "「目前看没问题，风险是 X，我周三确认后告诉你」"),
    (r"尽量|争取|试试看", "模糊承诺", "M", "大概率不行", "「能做，但需要 X；没有 X 就做不了」"),
    (r"在做了|正在做|处理中", "模糊承诺", "L", "别催了", "「已完成 A，还剩 B，X 日交付」"),
    (r"有进展(我)?同步|有情况(我)?说", "模糊承诺", "L", "别指望我主动说", "「每周三我在群里同步一次」"),

    # ---- 命令式 ----
    (r"马上|立刻|立即|现在就|赶紧", "命令式", "H",
     "你在命令我", "「这个比较急，能不能今天下班前先给个初版」"),
    (r"必须|务必|一定要", "命令式", "M", "我们不是同事，是上下级", "「这块需要 X，你看今天能安排吗」"),
    (r"我不管|反正(要|得)|不管怎样", "命令式", "H", "我不讲理", "「时间很紧，我们能砍掉哪部分保上线」"),
    (r"别(再)?犯(这种)?错|下不为例", "命令式", "H", "你能力不行", "「问题出在 X 环节，下次在那里加一道检查」"),
    (r"^[^。！？\n]{0,6}(给我|发我|弄好|搞定)[。！\n]?$", "命令式", "M", "像在派活", "补齐背景与时间"),

    # ---- 责任稀释 ----
    (r"大家(一起)?(看|确认|跟进|讨论|同步)[一下]?", "责任稀释", "H",
     "没人会看", "「@张三 看接口，@李四 看数据，今天 17:00 前」"),
    (r"相关(同学|同事|人员)|有关(部门|同事)", "责任稀释", "H", "我不知道是不是我", "「这块没明确 owner，我先认领」"),
    (r"我们(一起)?(努力|加油|推进)|共同(努力|推进)", "责任稀释", "M", "具体谁做什么？", "「我做 A（周三），你做 B（周四）」"),
    (r"需要.{0,8}(配合|支持)(?!\s*[，,]\s*我)", "责任稀释", "L", "谁牵头？", "「我牵头，需要 X 出…、Y 出…」"),
]

LEVEL_PENALTY = {"H": 12, "M": 6, "L": 2}
LEVEL_LABEL = {"H": "高危", "M": "中危", "L": "提醒"}

# 该换渠道的情况（不计算分数，单独提示）
CHANNEL_WARNINGS = [
    (r"绩效|薪资|涨薪|晋升|考核", "涉及绩效/薪资/晋升：文字极易被误解，建议当面说"),
    (r"你(的)?(错|失误|问题)|你(怎么|为什么)(这么|会)", "在指出具体人的失误：文字会留存，建议只对当事人当面说"),
    (r"离职|辞退|裁员|优化(?=掉)", "涉及劳动关系：务必当面，并留书面流程"),
]


def cjk_len(s: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def scan(text: str) -> dict:
    hits = []
    seen: set[tuple[str, str]] = set()
    for pattern, dim, level, reading, fix in RULES:
        for m in re.finditer(pattern, text, re.I | re.M):
            key = (dim, m.group(0))
            if key in seen:
                continue
            seen.add(key)
            line_no = text[: m.start()].count("\n") + 1
            hits.append({
                "text": m.group(0),
                "line": line_no,
                "dimension": dim,
                "level": level,
                "reading": reading,
                "fix": fix,
            })
    order = {"H": 0, "M": 1, "L": 2}
    hits.sort(key=lambda h: (order[h["level"]], h["line"]))

    penalty = sum(LEVEL_PENALTY[h["level"]] for h in hits)
    score = min(100, penalty)

    if score >= 60:
        band = "高概率被读成敌意：建议整段重写"
    elif score >= 30:
        band = "有风险：改掉最刺的一两句就够"
    else:
        band = "基本安全：检查有无模糊承诺即可"

    channels = [msg for pat, msg in CHANNEL_WARNINGS if re.search(pat, text)]

    by_dim: dict[str, int] = {}
    for h in hits:
        by_dim[h["dimension"]] = by_dim.get(h["dimension"], 0) + 1

    return {
        "score": score,
        "band": band,
        "total": len(hits),
        "counts": {k: sum(1 for h in hits if h["level"] == k) for k in ("H", "M", "L")},
        "by_dimension": by_dim,
        "hits": hits,
        "channel_warnings": channels,
        "cjk_chars": cjk_len(text),
    }


def render(r: dict, explain: bool) -> str:
    out = [f"风险分：{r['score']}/100    {r['band']}"]
    out.append(f"命中 {r['total']} 句：高危 {r['counts']['H']} · 中危 {r['counts']['M']} · "
               f"提醒 {r['counts']['L']}   （{r['cjk_chars']} 个汉字）")
    if r["hits"]:
        out.append("")
        for h in r["hits"]:
            out.append(f"  [{LEVEL_LABEL[h['level']]}]「{h['text']}」（第 {h['line']} 行，{h['dimension']}）")
            if explain:
                out.append(f"       对方会读成：{h['reading']}")
                out.append(f"       改写：{h['fix']}")
    if r["channel_warnings"]:
        out.append("\n【建议换渠道，而不是改措辞】")
        for w in r["channel_warnings"]:
            out.append(f"  - {w}")
    if not explain:
        out.append("\n加 --explain 看每句的「对方会读成什么」与改写建议。")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="检测职场消息的语气风险")
    ap.add_argument("file", help="消息文本文件")
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-over", type=float, default=None, help="风险分超过该值时退出码 1")
    args = ap.parse_args(argv)

    p = Path(args.file)
    if not p.is_file():
        print(f"找不到文件：{p}", file=sys.stderr)
        return 2
    text = p.read_text(encoding="utf-8-sig")
    if cjk_len(text) < 5:
        print("消息太短，无法判断语气。", file=sys.stderr)
        return 2

    r = scan(text)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(render(r, args.explain))

    if args.fail_over is not None and r["score"] > args.fail_over:
        return 1
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
