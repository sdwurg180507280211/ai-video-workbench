# AI 为什么会一本正经地胡说八道 — 配乐和音效，全部按 cues.json 的时间点合成
# 配乐：mgaudio 的 explainer（马林巴科技解说风）；考卷用纸声和红笔，翻格子用嘀嗒；高潮奖杯砸下前抽空
import sys, os, json
D = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, os.path.join(D, '..', 'lib', 'audio'))
import mgaudio as mg
from mgaudio import recipes, sfx

C = json.load(open(D + 'cues.json'))
E = C['ev']
DUR = C['duration']

m = recipes.explainer(duration=DUR, key='F', drop=E['fly1'][1], outro=E['e_trust'])
print('bpm', round(m.form.bpm, 2), 'tracks', list(m.tracks))
S = m.sfx
key_note = lambda t, i=0, up=12: m.form.chord_at(t)[i % len(m.form.chord_at(t))] + up


# ---- 钩子：打字发送；三次回答（加载点点 + 出答案）、两次「重新生成」；语气标签；红章「都不对」；片名两下 ----
S(sfx.pop('bubble', pitch=1.1), at=E['box_in'] + .05, gain=-10)
S(sfx.typing(n_keys=10, rate=13, kind='typewriter', seed=1), at=E['type'][0], gain=-13, pan=-.3)
S(sfx.click('hard'), at=E['send'], gain=-8, pan=-.2)
S(sfx.swish(dur=.25, seed=2), at=E['send'] + .02, gain=-13, pan=-.2)
for k, (a, rg) in enumerate([(E['a1'], None), (E['a2'], E['regen1']), (E['a3'], E['regen2'])]):
    if rg is not None:
        S(sfx.click('soft'), at=rg, gain=-8, pan=-.3)
    S(sfx.pop('bubble', pitch=1.0 + .08 * k), at=a - .12, gain=-9, pan=-.3)
    S(sfx.blip(note=key_note(a, k, 24), kind='sine'), at=a - .1, gain=-15, pan=-.3)
S(sfx.pop('mouth', pitch=1.2), at=E['tone'], gain=-10, pan=-.2)
S(sfx.stamp('rubber', seed=3), at=E['wrong'] + .02, gain=-3)
S(sfx.sticker_slap(seed=4), at=E['wrong'] + .1, gain=-8, pan=.3)
S(sfx.whoosh(dur=.9, kind='air', direction=1, peak=.5, seed=5), at=E['hook_pan'][0] + .4, gain=-14)
S(sfx.text_hit('slam'), at=E['title1'], gain=-3)
S(sfx.text_hit('slam', seed=5), at=E['title2'], gain=-1)
S(sfx.pen('marker', dur=.4, seed=6), at=E['title2'] + .35, gain=-12, pan=.2)
S(sfx.swish(dur=.24, seed=7), at=E['sub'] + .1, gain=-12, pan=.3)

# ---- 场景之间的飞行：嗖声峰值放在飞行中点 ----
for i, k in enumerate(['fly1', 'fly2', 'fly3', 'fly4', 'fly5', 'fly_cl', 'fly6', 'pull', 'fly_end']):
    a, b = E[k]
    S(sfx.whoosh(dur=b - a + .2, kind='swish', direction=1 if i % 2 == 0 else -1, peak=.5, seed=10 + i), at=(a + b) / 2, gain=-6)

# ---- 章节标签：弹出 + 记号笔 ----
for i in range(6):
    t = E[f'ch{i + 1}_tag'] - .3
    S(sfx.pop('mouth', pitch=1.0 + .05 * i), at=t + .05, gain=-6)
    S(sfx.pen('marker', dur=.4, seed=20 + i), at=t + .42, gain=-14, pan=-.2)

# ---- ① 练的是接话 ----
S(sfx.sticker_slap(seed=30), at=E['books'] + .1, gain=-10, pan=-.5)
S(sfx.paper('rustle', dur=.6, seed=31), at=E['read'], gain=-14, pan=-.5)
for i in range(4):
    S(sfx.pop('bubble', pitch=.95 + .06 * i), at=E['half'] + .1 * i + .03, gain=-11, pan=.2 + .05 * i)
S(sfx.ui('confirm'), at=E['guess1'], gain=-14, pan=.4)
for i in range(3):
    S(sfx.swish(dur=.3, seed=32 + i), at=E['bars1'] + .15 + .12 * i, gain=-15, pan=.3)
S(sfx.whoosh(dur=.5, kind='air', direction=1, peak=.6, seed=35), at=E['fill1'] + .1, gain=-12, pan=.4)
S(sfx.ding(note=key_note(E['fill1'], 0, 24)), at=E['fill1'] + .5, gain=-8, pan=.4)
p0, p1 = E['practice']
for k in range(12):
    S(sfx.tick('hi'), at=p0 + (p1 - p0) * k / 12, gain=-20 + .5 * k, pan=.2)

# ---- ② 见得少，就靠猜 ----
m0, m1 = E['many'], E['cat'] + .6
for k in range(9):
    S(sfx.pen('marker', dur=.12, seed=40 + k), at=m0 + (m1 - m0) * k / 8, gain=-17, pan=-.4)
S(sfx.ding(note=key_note(E['fish'], 0, 24)), at=E['fish'] + .05, gain=-9, pan=-.4)
S(sfx.pop('bubble', pitch=1.0), at=E['cardR'] + .05, gain=-9, pan=.4)
S(sfx.whoosh(dur=.7, kind='air', direction=1, peak=.5, seed=50), at=E['rare'] - .1, gain=-16, pan=.4)
for k in range(6):
    S(sfx.blip(note=key_note(E['barsR'], k, 12), kind='tri'), at=E['barsR'] + .1 + .06 * k, gain=-18, pan=.3)
S(sfx.click('hard'), at=E['dice'], gain=-8, pan=.6)
for k in range(5):
    S(sfx.tick('clock'), at=E['dice'] + .1 + k * .17, gain=-11 - k, pan=.5 - .1 * k)
S(sfx.pop('mouth', pitch=1.1), at=E['dice'] + 1.0, gain=-9, pan=.2)
S(sfx.swish(dur=.3, seed=51), at=E['slot2'] - .05, gain=-12, pan=.3)
S(sfx.ding(note=key_note(E['slot2'], 2, 24)), at=E['slot2'] + .35, gain=-9, pan=.3)

# ---- ③ 口气很肯定 ----
for k in range(8):
    t = E['cards3'] + (E['read3'] + .8 - E['cards3']) * k / 7
    S(sfx.pop('bubble', pitch=.9 + .04 * k), at=t + .02, gain=-15, pan=-.6 + .1 * k)
S(sfx.sticker_slap(seed=60), at=E['ask3'] + .05, gain=-9, pan=.6)
S(sfx.pen('marker', dur=.4, seed=61), at=E['idk'], gain=-11, pan=-.1)
S(sfx.ding(note=key_note(E['ck1'], 0, 24)), at=E['ck1'] + .2, gain=-10, pan=.4)
S(sfx.ding(note=key_note(E['ck2'], 1, 24)), at=E['ck2'] + .2, gain=-10, pan=.4)
S(sfx.ui('error'), at=E['ck3'] + .3, gain=-8, pan=.4)

# ---- ④ 考试不会也写满 ----
S(sfx.paper('rustle', dur=.5, seed=70), at=E['paper'], gain=-12, pan=-.4)
for k in range(2):
    S(sfx.pen('marker', dur=.2, seed=71 + k), at=E['paper'] + .3 + .15 * k, gain=-15, pan=-.4)
S(sfx.sticker_slap(seed=73), at=E['ask4'] + .1, gain=-9, pan=-.6)
S(sfx.pen('marker', dur=.4, seed=74), at=E['exam'], gain=-12, pan=-.4)
S(sfx.pop('bubble', pitch=.95), at=E['blank'] + .05, gain=-10)
S(sfx.stamp('rubber', seed=75), at=E['zero'] + .02, gain=-5)
S(sfx.pop('bubble', pitch=1.1), at=E['guessC'] + .05, gain=-10, pan=.4)
S(sfx.pen('pencil', dur=.4, seed=76), at=E['guessC'] + .4, gain=-11, pan=.4)
for k in range(9):
    S(sfx.tick('clock'), at=E['quarter'] + .9 * (k / 9) ** 1.8, gain=-12 - .4 * k, pan=.5)
S(sfx.ding(note=key_note(E['quarter'], 0, 24)), at=E['quarter'] + .95, gain=-9, pan=.5)

# ---- ⑤ 打分奖励蒙 ----
S(sfx.pop('bubble', pitch=.9), at=E['rules'] + .05, gain=-9, pan=-.2)
S(sfx.sticker_slap(seed=80), at=E['rules'] + .35, gain=-11, pan=.5)
S(sfx.pop('mouth', pitch=1.0), at=E['rules'] + .45, gain=-10, pan=-.3)
S(sfx.pop('mouth', pitch=.9), at=E['rules'] + .75, gain=-10, pan=-.3)
S(sfx.pop('mouth', pitch=.85), at=E['r_idk'] + .05, gain=-9, pan=-.3)
S(sfx.pen('marker', dur=.5, seed=81), at=E['same0'], gain=-11, pan=-.2)
S(sfx.ding(note=key_note(E['r_ok'], 0, 24)), at=E['r_ok'] + .1, gain=-9, pan=-.2)
S(sfx.whoosh(dur=.6, kind='air', direction=-1, peak=.5, seed=82), at=E['train5'] + .2, gain=-13, pan=.5)
S(sfx.impact(kind='punch', size=.3), at=E['train5'] + .6, gain=-14, pan=.5)
S(sfx.sticker_slap(seed=83), at=E['full'] + .1, gain=-7, pan=.6)

# ---- 高潮：两排格子翻开、分数跳、奖杯砸下；推近看蒙的四道 ----
S(sfx.pop('bubble', pitch=1.0), at=E['grids'] + .2, gain=-10)
S(sfx.sticker_slap(seed=90), at=E['grids'] + .35, gain=-11)
for k0, sd, pan in [(E['L1'], 91, -.5), (E['L2'], 92, -.5), (E['R1'], 93, .5), (E['R2'], 94, .5)]:
    for k in range(5):
        S(sfx.tick('hi'), at=k0 + .05 * k + .12, gain=-14, pan=pan)
S(sfx.ding(note=key_note(E['Ls'], 0, 24)), at=E['Ls'], gain=-8, pan=-.5)
S(sfx.ding(note=key_note(E['Rs'], 2, 24)), at=E['Rs'], gain=-8, pan=.5)
land = E['land']
S(sfx.riser(dur=1.4, kind='hybrid', end='cut'), at=land - .1, gain=-8)
S(sfx.impact(kind='punch', size=1.0), at=land, gain=1)
S(sfx.boom(dur=1.6), at=land, gain=-3)
S(sfx.shimmer_hit(note=key_note(land, 0, 12)), at=land + .05, gain=-6)
S(sfx.whoosh(dur=1.0, kind='air', direction=1, peak=.6, seed=95), at=E['push'] + .4, gain=-12, pan=.4)
for k in range(4):
    S(sfx.pop('mouth', pitch=1.0 + .06 * k), at=E['tags'] + .12 * k + .03, gain=-10, pan=.4)
S(sfx.ding(note=key_note(E['lucky'], 1, 24)), at=E['lucky'] + .05, gain=-11, pan=.3)
for k in range(3):
    S(sfx.ui('error'), at=E['xs'] + .35 * k, gain=-13 - k, pan=.5)

# ---- ⑥ 怎么防 ----
S(sfx.pop('bubble', pitch=1.0), at=E['cards6'] + .05, gain=-10, pan=-.5)
S(sfx.pop('mouth', pitch=1.1), at=E['src'] + .05, gain=-10, pan=-.5)
S(sfx.click('soft'), at=E['open6'] - .05, gain=-9, pan=-.5)
S(sfx.swish(dur=.3, seed=100), at=E['open6'] + .05, gain=-12, pan=-.5)
S(sfx.whoosh(dur=1.0, kind='air', direction=1, peak=.5, seed=101), at=E['check'] + .2, gain=-17, pan=-.5)
S(sfx.ui('error'), at=E['nope'] + .25, gain=-8, pan=-.5)
S(sfx.typing(n_keys=5, rate=12, kind='typewriter', seed=102), at=E['search'], gain=-13)
for k in range(3):
    S(sfx.pop('bubble', pitch=.95 + .06 * k), at=E['search'] + .45 + .2 * k, gain=-13)
S(sfx.pop('bubble', pitch=1.15), at=E['sure'] + .12, gain=-9, pan=.5)
S(sfx.typing(n_keys=7, rate=10, kind='typewriter', seed=103), at=E['sure_t'], gain=-14, pan=.5)
S(sfx.ui('confirm'), at=E['sure_t'] + .9, gain=-8, pan=.5)

# ---- 总览：三站逐个亮起，终点气泡 ----
for i, k in enumerate(['s1', 's2', 's3']):
    S(sfx.pop('mouth', pitch=1.0 + .1 * i), at=E[k] - .05, gain=-7, pan=-.5 + .4 * i)
    S(sfx.blip(note=key_note(E[k], i, 24), kind='tri'), at=E[k], gain=-13, pan=-.5 + .4 * i)
S(sfx.pen('marker', dur=.4, seed=110), at=E['s1b'], gain=-13, pan=-.5)
S(sfx.sticker_slap(seed=111), at=E['bubble'] + .05, gain=-6, pan=.6)
S(sfx.ding(note=key_note(E['bubble'], 0, 24)), at=E['bubble'] + .1, gain=-9, pan=.6)


def suck(t):             # "走出来"砸下前，配乐抽空 3 帧
    pts = [(0, 0), (land - .9, 0), (land - .5, -8), (land - .11, -8), (land - .1, -40), (land - .004, -40), (land, 0), (DUR, 0)]
    for (x0, g0_), (x1, g1_) in zip(pts, pts[1:]):
        if x0 <= t <= x1:
            return g0_ + (g1_ - g0_) * (t - x0) / max(x1 - x0, 1e-6)
    return 0


SPEECH = [v['speech'] for v in C.get('voice', [])]


def duck(t, depth=-8, pre=.15, post=.25, ramp=.12):
    g = 0
    for x0, x1 in SPEECH:
        x0, x1 = x0 - pre, x1 + post
        if x0 - ramp <= t <= x1 + ramp:
            k = min(1, (t - (x0 - ramp)) / ramp, ((x1 + ramp) - t) / ramp)
            g = min(g, depth * max(0, k))
    return g


m.group('music').automate('gain', [(round(t * .02, 3), round(min(suck(t * .02), duck(t * .02)), 2)) for t in range(int(DUR / .02) + 1)])

# ---- 结尾：三个回答跳一下；大字砸下，落款 ----
for k in range(3):
    S(sfx.blip(note=key_note(E['e_sure'], k, 24), kind='sine'), at=E['e_sure'] + .2 + .12 * k, gain=-14, pan=-.4)
S(sfx.sticker_slap(seed=120), at=E['end_b'] + .3, gain=-9, pan=-.2)
S(sfx.text_hit('slam', seed=121), at=E['e_trust'] + .05, gain=-4)
S(sfx.ding(note=key_note(E['sign'], 0, 24)), at=E['sign'], gain=-7)

m.master_kw.update(tilt=.4)
os.makedirs(D + 'out', exist_ok=True)
res = m.export(D + 'out/bed.wav', lufs=-16, tp=-2, spectrogram=D + 'out/qc_audio_spec.png')
print({k: v for k, v in res.items() if k not in ('spectrum', 'onsets')} if isinstance(res, dict) else res)
print(mg.hit_alignment(D + 'out/bed.wav', [E['title2'], E['wrong'], E['zero'], E['land'], E['e_trust'] + .05]))

# 旁白由 opus-code-video 的 scripts/mix_voice.py 叠上去（读 out/bed.wav 和 cues.json 的 voice，写 out/audio.wav）
