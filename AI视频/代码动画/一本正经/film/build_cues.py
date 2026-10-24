"""按配音的逐字时间戳排节拍：python3 film/build_cues.py  → film/cues_base.json

每段长度 = 开口前留白 + 这句说话时长 + 段尾余量（含飞到下一章的镜头），画面事件钉在旁白里的某个词上。
段长都装得下配音，所以 retime.py 不会再拉长，只补 voice 和 subs。改节奏就改这里的 LEAD / EXTRA 或事件，再重跑。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINES = (ROOT / 'voice/旁白.txt').read_text(encoding='utf-8').strip().split('\n')
PUNCT = '，。：？、！；“”'
#        钩子 ①   ②   ③   ④   ⑤   高潮 ⑥   总览 结尾
LEAD = [.6, .4, .3, .3, .3, .3, .3, .3, .5, .4]
EXTRA = [4.4, 3.4, 3.6, 3.4, 3.2, 3.2, 4.4, 3.6, 3.4, 3.4]


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
# ---- 0 钩子：聊天框里问生日，AI 三次给出三个日期，都说得很肯定；红章「都不对」；片名砸下 ----
ev.update(box_in=.05, type=[.15, .9], send=1.0,
          a1=at(0, '三月'), regen1=r(at(0, '再问一次') - .1), a2=at(0, '六月'), regen2=r(at(0, '再问') - .1, ), a3=at(0, '一月一号'),
          tone=at(0, '特别肯定'), wrong=at(0, '一个都不对'))
ev['regen2'] = r(at(0, '再问', 1) - .1)
ev['title1'] = r(end(0) + .45)
ev.update(title2=r(ev['title1'] + .35), sub=r(ev['title1'] + .9), hook_pan=[r(ev['title1'] - .7), r(ev['title1'] + .1)])
# ---- ① 练的是接话 ----
ev['fly1'] = fly_into(1)
ev.update(ch1_tag=B[1], books=arrive(ev['fly1']), read=at(1, '读'), half=at(1, '看前半句'), guess1=at(1, '猜下一个'),
          bars1=at(1, '最可能'), fill1=r(end(1) - 1.9), practice=[at(1, '练得越多'), r(end(1) + .2)])
ev['fill1'] = r(at(1, '什么') + .25)
# ---- ② 见得少，就靠猜 ----
ev['fly2'] = fly_into(2)
ev.update(ch2_tag=B[2], cardL=arrive(ev['fly2']), many=at(2, '很多遍'), cat=at(2, '小猫爱吃鱼'), fish=at(2, '又顺'),
          cardR=at(2, '可小团子'), rare=at(2, '几乎没写过'), barsR=at(2, '不知道'), dice=at(2, '只能挑'), slot2=at(2, '接上去'))
# ---- ③ 口气很肯定 ----
ev['fly3'] = fly_into(3)
ev.update(ch3_tag=B[3], cards3=arrive(ev['fly3']), ask3=at(3, '为什么'), read3=at(3, '读过的句子'), idk=at(3, '很少有人'),
          ck1=at(3, '又顺'), ck2=at(3, '又肯定'), ck3=at(3, '查一查'))
# ---- ④ 考试不会也写满 ----
ev['fly4'] = fly_into(4)
ev.update(ch4_tag=B[4], paper=arrive(ev['fly4']), ask4=at(4, '为什么'), exam=at(4, '考试'), blank=at(4, '选择题空着'),
          zero=at(4, '零分'), guessC=at(4, '随便蒙'), quarter=at(4, '四分之一'))
# ---- ⑤ 打分奖励蒙 ----
ev['fly5'] = fly_into(5)
ev.update(ch5_tag=B[5], rules=arrive(ev['fly5']), test=at(5, '考AI'), r_idk=at(5, '说不知道'), same0=at(5, '不得分'),
          r_ok=at(5, '蒙对了'), train5=at(5, '训练成'), full=at(5, '不会也要写满'))
# ---- 高潮：十道题，老老实实 6 分，不会就蒙 7 分排第一；推近看它蒙的四道 ----
ev['fly_cl'] = fly_into(6)
ev.update(cl_b=B[6], grids=arrive(ev['fly_cl']), ten=at(6, '十道题'), honest=at(6, '老老实实'), L1=r(at(6, '得六分') - .9),
          L2=r(at(6, '得六分') - .2), Ls=at(6, '六分'), guesser=at(6, '不会就蒙'), R1=r(at(6, '得七分') - .9), R2=r(at(6, '得七分') - .2),
          Rs=at(6, '七分'), land=at(6, '第一'), push=at(6, '可它'), tags=at(6, '都是猜的'), lucky=at(6, '碰巧对'), xs=at(6, '三道错'))
# ---- ⑥ 怎么防 ----
ev['fly6'] = fly_into(7)
ev.update(ch6_tag=B[7], cards6=arrive(ev['fly6']), src=at(7, '出处'), open6=at(7, '点开'), check=at(7, '里面'), nope=at(7, '这么说'),
          search=at(7, '上网'), sure=at(7, '直接说'), sure_t=at(7, '这个我'))
# ---- 总览 ----
ev['pull'] = fly_into(8)
ev.update(ov_b=B[8], s1=at(8, '接得顺'), s1b=at(8, '不等于'), s2=at(8, '见得少'), s3=at(8, '不会的'), bubble=at(8, '写满'))
# ---- 结尾：回到聊天框 ----
ev['fly_end'] = [r(B[9] - .9), r(B[9] + .4)]
ev.update(end_b=B[9], e_sure=at(9, '特别肯定'), e_trust=at(9, '先别急'), e_white=at(9, '交白卷'), sign=r(end(9) + .5))

base = {
    'fps': 30, 'duration': B[-1],
    'note': '《AI 为什么会一本正经地胡说八道》的节拍，由 build_cues.py 按配音时间戳生成；画面 index.html 和配乐 audio.py 都读 cues.json',
    'ev': ev,
    'narration': {
        'lines': 'voice/旁白.txt',
        'bounds': [0, 'ch1_tag', 'ch2_tag', 'ch3_tag', 'ch4_tag', 'ch5_tag', 'cl_b', 'ch6_tag', 'ov_b', 'end_b', 'duration'],
        'place': [{'seg': k, 'lead': LEAD[k]} for k in range(len(LINES))],
        'tail': .5, 'end_hold': 1.2, 'show': {},
    },
    'brand': {'name': '小团子AI', 'mascot': '/assets/xiaotuanzi/05_放大镜研究.png'},
    'stickers': {'shock': '02_震惊.png', 'teach': '06_小白板讲课.png', 'dice': '14_按骰子.png', 'ask': '03_疑惑.png',
                 'sweat': '09_无语流汗.png', 'paper': '16_举着写满的试卷.png', 'judge': '11_注意.png', 'mag': '05_放大镜研究.png'},
}
(ROOT / 'film/cues_base.json').write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'时长 {B[-1]:.1f} 秒；段落边界', [round(b, 1) for b in B])
print('高潮砸点', ev['land'], f'{ev["land"] / B[-1]:.0%}')
