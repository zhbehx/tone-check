# 推广素材：职场语气

> 测出哪句话会被读成甩锅或被动攻击，并给保留原意的改写。

下面每条文案都用本仓脚本测过 AI 味。

---

## 一、GitHub 仓库元信息

**About**：见仓库设置（已由发布脚本写入）。

**Social preview**：`market/social-preview.png`（1280×640，已生成）。


---

## 二、小红书

**标题（5 选 1）**

1. 「这个我之前说过了」——这七个字让我多了一个敌人
2. 发出去之前，建议你先测一下这句话的语气
3. 职场上最贵的三个字，是「我没错」
4. 我把团队的冲突消息做了一次体检
5. 「呵呵」在中文职场里，没有中性用法

**正文**

有个设计师朋友，方案被研发驳回三次。第四次沟通前，他写好了这样一段话准备发群里：

「这个我之前说过了，你自己看需求文档吧。这不是我负责的，你们部门的问题你们自己解决。我早就提醒过了，现在出事了吧，呵呵。行吧，你开心就好，我随便。我尽快看看，应该没问题。大家确认一下，相关同学尽快跟进。马上就要，我不管，反正今天必须给我。」

我拿测了一下，**风险分 100/100，命中 15 句**。

最致命的三句：

❌「这个我之前说过了」→ 对方读成「你在撇清责任，暗示是我的错」
❌「呵呵」→ 对方读成「我在鄙视你」
❌「我不管，反正今天必须给我」→ 对方读成「我不讲理」

但我后来发现，**真正的问题不是语气，是信息不足**。

这 7 句话里，6 句在处理情绪，只有最后一句在提要求——而那句要求没有任何支撑。

改成「事实 + 影响 + 请求 + 时间」之后：

「文档第 3 节写的是『按钮点击后 200ms 内给出反馈』，这版实现是 800ms，测试环境可以复现（附录屏）。

我这边的排期卡在这上面：视觉稿已经定了，实现不改的话上线要延后，而 11/3 是市场部的活动日。

我的建议是两个选项：A. 今天下班前把响应时间改到 200ms 内；B. 如果技术上要多花时间，我们今天下午 3 点拉 15 分钟，把标准改成可实现的数字。

@张工 这块是你判断，今天 17:00 前能给个方向吗？」

字数从 101 涨到 312，但多出来的全是**信息**：具体标准、可复现的证据、影响、两个方案、具名的责任人、具体时间点。

重跑：**0 分**。

「别把保护自己当成语气不好」——明确拒绝、指出事实冲突、设定边界，这三件事不该改。

`#职场` `#沟通` `#情商` `#打工人` / `#职场沟通` `#说话技巧` `#同事关系` `#向上管理` / `#我的职场生活`

**首评（置顶）**

反向说一句：脚本会提示「该换渠道」——涉及绩效、薪资、晋升，或者要指出某个具体人的失误，别发文字。文字会留存、会被转发、会被截图。


---

## 三、X / Twitter（英文）

```
A designer drafted this for a project group chat after his design was rejected a third time:

"I already said this. Read the spec yourself. Not my area. This is your
department's problem. I warned you. Fine, whatever, do what you want."

Scored 100/100. 15 hits.

The real problem wasn't tone though — out of 7 sentences, 6 were processing
emotion and 1 was making a demand with zero support.

Rewrote it as fact → impact → request → deadline. 101 words → 312 words, and
every added word was *information*: the actual spec value, a reproducible
environment, the date it blocks, two options with costs, a named owner.

Re-scored: 0.
```


---

## 四、Show HN

```
Show HN: Tone-check – scan workplace messages for blame-shifting and passive aggression

Built this after watching a colleague's message get him quietly cut out of a
project. He wasn't wrong on the facts — he was wrong on what the reader would
hear.

Five dimensions, each rule carrying "how the other side reads it" plus a
rewrite: blame-shifting ("I already said this"), passive aggression ("whatever",
"fine"), vague commitments ("ASAP", "should be fine"), commands ("do it now"),
and responsibility dilution ("could everyone take a look").

The insight that made it useful rather than moralizing: most "tone problems"
are actually *underspecification*. "This isn't finished?!" becomes neutral when
you write fact + impact + request + deadline — because the reader is then
responding to information instead of emotion.

It also flags messages that shouldn't be text at all: performance, comp,
promotion, or naming someone's specific mistake. Text persists and gets
forwarded.

Honest limitation: no model of relationship or power. The same "fine" is
submission to a boss and sarcasm to a peer.

github.com/zhbehx/tone-check
```


---

## 五、发布清单

| 渠道 | 素材 | 关键动作 |
| --- | --- | --- |
| GitHub | Release v1.0.0 | 已发布 |
| X | 上面的英文稿 | 配终端截图，分数可见 |
| Show HN | 上面的 HN 稿 | 周二至周四 UTC 14:00–16:00 |
| 社群 / 即刻 | 一句话 + 链接 | 只讲一个点，别贴 README |