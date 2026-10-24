"""按配音的逐字时间戳排节拍：python3 film/build_cues.py  → film/cues_base.json

每段长度 = 开口前留白 + 这句说话时长 + 段尾余量（含飞到下一章的镜头），画面事件钉在旁白里的某个词上。
段长都装得下配音，所以 retime.py 不会再拉长，只补 voice 和 subs。改节奏就改这里的 LEAD / EXTRA 或事件，再重跑。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINES = (ROOT / 'voice/旁白.txt').read_text(encoding='utf-8').strip().split('\n')
PUNCT = '，。：？、！；“”'
#        钩子 ①   ②   ③   ④   ⑤   ⑥   总览 结尾
LEAD = [.9, .4, .3, .3, .3, .3, .3, .5, .4]
EXTRA = [4.6, 4.4, 3.0, 3.2, 3.4, 3.2, 3.4, 5.0, 3.2]


def words(i):
    q = json.loads((ROOT / f'voice/lines/{i:02d}.mp3.json').read_text(encoding='utf-8'))
    return [w for s in q['data']['sentences'] for w in s['words']]


W = [words(i) for i in range(len(LINES))]
SPAN = [(w[0]['startTime'], w[-1]['endTime']) for w in W]
B = [0.0]
for k in range(len(LINES)):
    B.append(round(B[-1] + LEAD[k] + SPAN[k][1] - SPAN[k][0] + EXTRA[k], 3))
SP = [B[k] + LEAD[k] for k in range(len(LINES))]          # 每句开口的时刻


def at(k, phrase, nth=0):
    """第 k 句里 phrase 第一个字开口的时刻（片内绝对时间）。"""
    chars, times = '', []
    for w in W[k]:
        for ch in w['word']:
            if ch not in PUNCT and not ch.isspace():
                chars += ch
                times.append(w['startTime'])
    pos = -1
    for _ in range(nth + 1):
        pos = chars.find(phrase, pos + 1)
    if pos < 0:
        raise ValueError(f'第 {k} 句里没有 {phrase!r}：{chars}')
    return round(SP[k] + times[pos] - SPAN[k][0], 3)


def end(k):
    return round(SP[k] + SPAN[k][1] - SPAN[k][0], 3)


def fly_into(k, before=.9, after=.3):
    return [round(B[k] - before, 3), round(B[k] + after, 3)]


arrive = lambda f: round(f[0] + (f[1] - f[0]) * .42, 3)
r = lambda x: round(x, 3)

ev = {}
# ---- 0 钩子：输入框打字、按生成；先以为是一笔一笔画（铅笔被划掉），其实是一屏雪花里擦出猫；片名砸下 ----
ev.update(box_in=.05, type=[.15, 1.0], press=1.12, canvas_in=.1,
          pencil=[r(at(0, '不是') - .15), r(at(0, '画的') + .1)], xmark=r(at(0, '画的') + .15),
          snow0=r(at(0, '一屏') - .1), clean0=[at(0, '一点一点'), r(end(0) + 1.5)])
ev.update(title1=r(end(0) + .45))
ev.update(title2=r(ev['title1'] + .35), sub=r(ev['title1'] + .9))
# ---- ① 先学认雾 ----
ev['fly1'] = fly_into(1)
ev.update(ch1_tag=B[1], photos=arrive(ev['fly1']), many=at(1, '很多图'), steps=[at(1, '一步步'), r(at(1, '雪花点') + .2)],
          dots_hi=at(1, '雪花点'), window=r(at(1, '车窗') - .1), fog=[at(1, '慢慢'), r(at(1, '起雾') + 1.0)],
          note=at(1, '它天天'), pick=at(1, '看一眼'), guess=at(1, '猜出'), train=[r(end(1) + .1), r(end(1) + 2.6)])
ev['match'] = r(ev['train'][1] + .05)
# ---- ② 往回擦 ----
ev['fly2'] = fly_into(2)
ev.update(ch2_tag=B[2], canvas2=arrive(ev['fly2']), flip=at(2, '反过来'), rand=at(2, '随机'),
          g1=at(2, '猜哪些'), w1=at(2, '擦掉'), g2=at(2, '再猜'), w2=at(2, '再擦'),
          fast=[at(2, '几十步'), r(at(2, '出来了') + .2)])
ev['done2'] = r(ev['fast'][1] + .1)
# ---- ③ 文字指路 ----
ev['fly3'] = fly_into(3)
ev.update(ch3_tag=B[3], canvas3=arrive(ev['fly3']), q3=at(3, '怎么知道'), prompt3=at(3, '你写的话'),
          cells=[at(3, '一串数字'), r(at(3, '一串数字') + .8)], arrow3=at(3, '每擦一步'), look3=at(3, '看一眼'),
          guide=[at(3, '往'), r(end(3) + 1.4)], scarf=at(3, '红围巾'))
# ---- ④ 指路力度 ----
ev['fly4'] = fly_into(4)
ev.update(ch4_tag=B[4], knob_in=arrive(ev['fly4']), strength=at(4, '这股劲儿'), low=at(4, '太小'), high=at(4, '太大'),
          hard=at(4, '线条'), back4=r(end(4) + .5))
# ---- ⑤ 换一屏雪花（种子） ----
ev['fly5'] = fly_into(5)
ev.update(ch5_tag=B[5], seed_in=arrive(ev['fly5']), press1=r(B[5] + .2), why=at(5, '为什么'),
          press2=at(5, '起点'), rand5=at(5, '随机'), retype=at(5, '同一个模型'), same=at(5, '同一张'))
ev.update(genA=[r(ev['press1'] + .35), r(ev['press1'] + 2.0)], genB=[r(ev['press2'] + .35), r(ev['press2'] + 1.9)],
          genA2=[r(ev['retype'] + .8), r(ev['same'] + .1)])
# ---- ⑥ 先在小图上擦 ----
ev['fly6'] = fly_into(6)
ev.update(ch6_tag=B[6], big6=arrive(ev['fly6']), save=at(6, '省力'), compress=at(6, '压缩'),
          wipe6=[at(6, '小图上擦'), r(at(6, '最后') + .3)], decode=at(6, '还原'))
ev['decoded'] = [ev['decode'], r(ev['decode'] + 1.1)]
# ---- 总览 + 高潮：雪花 → 你的话指路 → 猜雾、擦掉（转圈）→ 解码还原 → 成图；满屏噪点沿弯弯的轨迹聚成猫 ----
ev['pull'] = [r(B[7] - .9), r(B[7] + .3)]
ev.update(ov_b=B[7], n_snow=at(7, '一屏雪花'), n_text=at(7, '你的'), n_guess=at(7, '猜雾'), n_wipe=at(7, '擦掉'),
          n_rep=[at(7, '重复'), at(7, '图就')], n_out=at(7, '图就'))
ev['fly_cl'] = [r(at(7, '图就') + .2), r(at(7, '图就') + 1.3)]
ev['cl'] = [r(ev['fly_cl'][0] + .3), r(end(7) + 1.9)]
ev['land'] = ev['cl'][1]
# ---- 结尾 ----
ev.update(end_b=B[8], e_next=at(8, '下次'), e_snow=at(8, '冒出'), e_calm=at(8, '别着急'), e_wipe=at(8, '正在擦'),
          sign=r(end(8) + .5))

base = {
    'fps': 30, 'duration': B[-1],
    'note': '《AI 画图，怎么从一团雪花变出一张画》的节拍，由 build_cues.py 按配音时间戳生成；画面 index.html 和配乐 audio.py 都读 cues.json',
    'ev': ev,
    'narration': {
        'lines': 'voice/旁白.txt',
        'bounds': [0, 'ch1_tag', 'ch2_tag', 'ch3_tag', 'ch4_tag', 'ch5_tag', 'ch6_tag', 'ov_b', 'end_b', 'duration'],
        'place': [{'seg': k, 'lead': LEAD[k]} for k in range(len(LINES))],
        'tail': .5, 'end_hold': 1.2, 'show': {},
    },
    'brand': {'name': '小团子AI', 'mascot': '/assets/xiaotuanzi/07_跳起欢呼.png'},
    # 生图网关 2026-10-23 出不了图，先用素材库现有动作 + 代码画的道具（抹布、旋钮、骰子）
    'stickers': {'wipe': '11_拿抹布擦.png', 'note': '12_记笔记.png', 'knob': '13_拧旋钮.png', 'dice': '14_按骰子.png',
                 'ask': '03_疑惑.png', 'hold': '15_举着抹布.png'},
}
(ROOT / 'film/cues_base.json').write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'时长 {B[-1]:.1f} 秒；段落边界', [round(b, 1) for b in B])
