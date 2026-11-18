#!/usr/bin/env python3
"""AgentGate demo video slides — site visual identity, real data (2026-11-18)."""
import glob
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
GOLD = (240, 185, 11)
WHITE = (232, 236, 244)
MUTED = (152, 162, 184)
PANEL = (26, 33, 51)
PANEL_EDGE = (42, 51, 80)
DARK = (13, 20, 32)
GREEN = (63, 185, 111)
RED = (229, 83, 75)
NAVY = (18, 48, 92)

def font(bold=False, mono=False, size=40):
    if mono:
        paths = glob.glob('/usr/share/fonts/**/DejaVuSansMono*.ttf', recursive=True)
        return ImageFont.truetype(paths[0], size)
    name = 'NotoSansCJK-Bold.ttc' if bold else 'NotoSansCJK-Regular.ttc'
    paths = glob.glob(f'/usr/share/fonts/**/{name}', recursive=True)
    return ImageFont.truetype(paths[0], size)

def bg():
    img = Image.new('RGB', (W, H), (11, 14, 23))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(11 + (16 - 11) * t); g = int(14 + (24 - 14) * t); b = int(23 + (43 - 23) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    return img

def panel(d, box, edge=PANEL_EDGE, fill=PANEL, radius=24, width=2):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=edge, width=width)

def caption(d, text):
    d.rectangle([0, H - 92, W, H], fill=(8, 10, 16))
    d.line([(0, H - 92), (W, H - 92)], fill=GOLD, width=3)
    f = font(size=36)
    d.text((W / 2, H - 46), text, font=f, fill=WHITE, anchor='mm')

def footer(d, n):
    f = font(size=26)
    d.text((48, H - 130), 'AgentGate · Binance Agentic Wallet Hackathon', font=f, fill=MUTED, anchor='lm')
    d.text((W - 48, H - 130), f'{n} / 6', font=f, fill=MUTED, anchor='rm')

def title_text(d, text, y=110, size=66):
    d.text((W / 2, y), text, font=font(bold=True, size=size), fill=WHITE, anchor='mm')

def medallion(d, cx, cy, s=1.0):
    w, h = int(470 * s), int(320 * s)
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    d.rounded_rectangle(box, radius=int(30 * s), fill=NAVY, outline=GOLD, width=max(2, int(6 * s)))
    # shield
    sw, sh = int(150 * s), int(180 * s)
    x0, y0 = cx - sw / 2, cy - sh / 2
    pts = [(cx, y0), (x0 + sw, y0 + int(30 * s)), (x0 + sw, y0 + int(95 * s)),
           (cx, y0 + sh), (x0, y0 + int(95 * s)), (x0, y0 + int(30 * s))]
    d.polygon(pts, outline=GOLD, width=max(2, int(7 * s)))
    # check
    ck = [(cx - int(42 * s), cy + int(2 * s)), (cx - int(12 * s), cy + int(34 * s)), (cx + int(48 * s), cy - int(30 * s))]
    d.line(ck, fill=GOLD, width=max(2, int(11 * s)), joint='curve')

# ---------- S1 title ----------
img = bg(); d = ImageDraw.Draw(img)
medallion(d, W / 2, 300, 1.0)
f1 = font(bold=True, size=128)
d.text((W / 2 - 8, 560), 'Agent', font=f1, fill=WHITE, anchor='rm')
d.text((W / 2 - 8, 560), 'Gate', font=f1, fill=GOLD, anchor='lm')
d.text((W / 2, 665), 'One verified person. One pass. No Sybil farms.', font=font(size=42), fill=WHITE, anchor='mm')
d.text((W / 2, 745), 'Agent ID 门禁免费 Mint 发射台 · BNB Chain', font=font(size=42), fill=MUTED, anchor='mm')
d.text((W / 2, 830), '为项目方提供一行接入的链上身份门禁，为 Agent ID 持有者解锁真实权益', font=font(size=34), fill=MUTED, anchor='mm')
caption(d, 'AgentGate 演示 · 已上线运行的产品，不是概念稿')
img.save('s1.png')

# ---------- S2 problem / solution ----------
img = bg(); d = ImageDraw.Draw(img)
title_text(d, '问题：免费 Mint 总被女巫农场抢光')
panel(d, [90, 230, 930, 800])
d.text((130, 275), '没有门禁时', font=font(bold=True, size=44), fill=RED, anchor='lm')
bad = ['机器人批量生成钱包，额度被秒抢', '真实用户点开页面时早已售罄', '项目方被迫自建黑名单与人工审核']
y = 380
for t in bad:
    d.text((140, y), '✗', font=font(bold=True, size=40), fill=RED, anchor='lm')
    d.text((205, y), t, font=font(size=38), fill=WHITE, anchor='lm'); y += 120
panel(d, [990, 230, 1830, 800], edge=GOLD, width=3)
d.text((1030, 275), 'AgentGate 的解法', font=font(bold=True, size=44), fill=GOLD, anchor='lm')
good = ['Agent ID 是经验证的链上身份，自带门槛', '校验写进智能合约，前端绕不过去', '一个 ID 一份额度，女巫农场直接失效']
y = 380
for t in good:
    d.text((1040, y), '✓', font=font(bold=True, size=40), fill=GREEN, anchor='lm')
    d.text((1105, y), t, font=font(size=38), fill=WHITE, anchor='lm'); y += 120
footer(d, 2)
caption(d, '把身份校验放进合约层，而不是靠前端自觉')
img.save('s2.png')

# ---------- S3 product / website ----------
img = bg(); d = ImageDraw.Draw(img)
title_text(d, '产品已上线：官网 + 演示徽章')
panel(d, [110, 210, 1810, 830], fill=(16, 22, 38))
d.ellipse([150, 240, 178, 268], fill=RED); d.ellipse([195, 240, 223, 268], fill=GOLD); d.ellipse([240, 240, 268, 268], fill=GREEN)
d.rounded_rectangle([300, 232, 1450, 278], radius=23, fill=DARK, outline=PANEL_EDGE, width=2)
d.text((325, 255), 'https://zhangrong121387-hue.github.io/agentgate', font=font(mono=True, size=30), fill=MUTED, anchor='lm')
d.text((160, 350), 'One verified person. One pass. No Sybil farms.', font=font(bold=True, size=46), fill=WHITE, anchor='lm')
chips = ['Check your eligibility', 'Demo: the AgentGate Badge', 'For projects: integrate in three lines']
x = 160
for c in chips:
    f = font(size=30); tw = d.textlength(c, font=f)
    d.rounded_rectangle([x, 420, x + tw + 44, 478], radius=29, fill=PANEL, outline=PANEL_EDGE, width=2)
    d.text((x + 22, 449), c, font=f, fill=WHITE, anchor='lm'); x += tw + 70
panel(d, [160, 520, 1760, 790], fill=PANEL)
d.text((200, 565), 'AgentGate Badge（AGB）', font=font(bold=True, size=40), fill=GOLD, anchor='lm')
d.text((200, 625), '免费铸造 · 每个 Agent ID 限领 1 枚 · 上限 10,000 枚', font=font(size=36), fill=WHITE, anchor='lm')
d.rounded_rectangle([200, 680, 1400, 724], radius=22, fill=DARK, outline=PANEL_EDGE, width=2)
d.rounded_rectangle([200, 680, 221, 724], radius=22, fill=GOLD)
d.text((1440, 702), '176 / 10,000 已铸造', font=font(bold=True, size=36), fill=WHITE, anchor='lm')
d.text((200, 758), 'Contract: 0x42c9ED912025DF33cA1676AAD4651cDdeD3F09ED', font=font(mono=True, size=28), fill=MUTED, anchor='lm')
footer(d, 3)
caption(d, '任何人现在就能打开官网，连接钱包查资格、领徽章')
img.save('s3.png')

# ---------- S4 how it works ----------
img = bg(); d = ImageDraw.Draw(img)
title_text(d, '工作原理：三步，全在链上')
steps = [('1', '连接钱包', '用户用 Binance\nAgentic Wallet 连接'), ('2', '合约校验 Agent ID', 'mint 时调用 Agent ID\n合约 balanceOf 校验'), ('3', '通过即免费铸造', '有 ID：铸造成功\n无 ID：交易直接 revert')]
x = 90
for num, t1, t2 in steps:
    panel(d, [x, 220, x + 540, 500], edge=GOLD if num == '2' else PANEL_EDGE, width=3 if num == '2' else 2)
    d.ellipse([x + 30, 250, x + 110, 330], fill=GOLD)
    d.text((x + 70, 290), num, font=font(bold=True, size=44), fill=(11, 14, 23), anchor='mm')
    d.text((x + 135, 290), t1, font=font(bold=True, size=40), fill=WHITE, anchor='lm')
    yy = 385
    for line in t2.split('\n'):
        d.text((x + 35, yy), line, font=font(size=34), fill=MUTED, anchor='lm'); yy += 52
    if num != '3':
        d.text((x + 565, 360), '→', font=font(bold=True, size=56), fill=GOLD, anchor='mm')
    x += 580
panel(d, [90, 550, 1830, 830], fill=DARK)
code = [
    ('function mint() external {', WHITE),
    ('    if (!mintOpen) revert MintClosed();', MUTED),
    ('    if (claimed[msg.sender]) revert AlreadyClaimed(msg.sender);', MUTED),
    ('    // The centerpiece: only an Agent ID holder gets through this line.', GREEN),
    ('    _requireAgentID();  // agentID.balanceOf(account) > 0', GOLD),
    ('    claimed[msg.sender] = true;', MUTED),
    ('    uint256 tokenId = ++totalMinted;', MUTED),
    ('}', WHITE),
]
y = 578
for line, col in code:
    d.text((130, y), line, font=font(mono=True, size=30), fill=col, anchor='lm'); y += 31
footer(d, 4)
caption(d, '没有前端白名单、没有人工审核——规则即代码')
img.save('s4.png')

# ---------- S5 live proof ----------
img = bg(); d = ImageDraw.Draw(img)
title_text(d, '上线首晚的真实数据（2026-11-18）')
stats = [('176', '枚徽章已被铸造', '链上实时计数，仍在增长'), ('150+', '个 Agent ID 地址完成交互', '全部为真实持有者自发铸造'),
         ('30 / 已达成', '创新奖交互地址门槛', '上线当晚即越过门槛 ✓'), ('Pass - Verified', 'BscScan 源码验证', 'Sourcify exact_match 双重核对')]
pos = [(90, 220), (975, 220), (90, 520), (975, 520)]
for (big, mid, small), (x, y) in zip(stats, pos):
    panel(d, [x, y, x + 855, y + 270])
    d.text((x + 40, y + 75), big, font=font(bold=True, size=64), fill=GOLD, anchor='lm')
    d.text((x + 40, y + 155), mid, font=font(bold=True, size=38), fill=WHITE, anchor='lm')
    d.text((x + 40, y + 215), small, font=font(size=32), fill=MUTED, anchor='lm')
footer(d, 5)
caption(d, '合约已部署、已验证、已开源——正在被真实用户使用')
img.save('s5.png')

# ---------- S6 end card ----------
img = bg(); d = ImageDraw.Draw(img)
medallion(d, W / 2, 240, 0.8)
f1 = font(bold=True, size=96)
d.text((W / 2 - 6, 460), 'Agent', font=f1, fill=WHITE, anchor='rm')
d.text((W / 2 - 6, 460), 'Gate', font=f1, fill=GOLD, anchor='lm')
d.text((W / 2, 545), '让 Agent ID 成为真正的通行证', font=font(size=44), fill=WHITE, anchor='mm')
rows = [('官网 Demo', 'zhangrong121387-hue.github.io/agentgate'),
        ('开源代码', 'github.com/zhangrong121387-hue/agentgate'),
        ('链上合约', 'bscscan.com/address/0x42c9ED912025DF33cA1676AAD4651cDdeD3F09ED')]
y = 660
for label, val in rows:
    d.text((330, y), label, font=font(bold=True, size=36), fill=GOLD, anchor='lm')
    d.text((560, y), val, font=font(mono=True, size=31), fill=WHITE, anchor='lm'); y += 62
d.text((W / 2, 905), 'Binance Agentic Wallet Hackathon · 2026', font=font(size=32), fill=MUTED, anchor='mm')
caption(d, 'AgentGate · 欢迎评委现场打开官网体验铸造')
img.save('s6.png')
print('slides done')
