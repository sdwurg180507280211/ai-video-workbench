# AI 画图，怎么从一团雪花变出一张画 — 配乐和音效，全部按 cues.json 的时间点合成
# 配乐：mgaudio 的 explainer（马林巴科技解说风）；雪花用电视雪花声，擦用纸布摩擦声；高潮"图走出来"前抽空再砸下
import sys, os, json
D = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, os.path.join(D, '..', 'lib', 'audio'))
import mgaudio as mg
from mgaudio import recipes, sfx

C = json.load(open(D + 'cues.json'))
E = C['ev']
DUR = C['duration']

m = recipes.explainer(duration=DUR, key='F', drop=E['fly1'][1], outro=E['e_calm'])
print('bpm', round(m.form.bpm, 2), 'tracks', list(m.tracks))
S = m.sfx
key_note = lambda t, i=0, up=12: m.form.chord_at(t)[i % len(m.form.chord_at(t))] + up


def wipe(t, dur=.45, seed=0, gain=-12, pan=.2):          # 抹布擦一下
    S(sfx.paper('rustle', dur=dur, seed=seed), at=t, gain=gain, pan=pan)


# ---- 钩子：输入框、打字、按生成；铅笔画一笔被划掉；一屏雪花，一点点擦出猫；片名两下 ----
S(sfx.pop('bubble', pitch=1.1), at=E['box_in'] + .05, gain=-10)
S(sfx.typing(n_keys=8, rate=9, kind='typewriter', seed=1), at=E['type'][0], gain=-12, pan=-.3)
S(sfx.click('hard'), at=E['press'], gain=-7, pan=-.3)
S(sfx.pen('pencil', dur=E['pencil'][1] - E['pencil'][0], seed=2), at=E['pencil'][0], gain=-9, pan=-.3)
S(sfx.ui('error'), at=E['xmark'], gain=-9, pan=-.3)
S(sfx.static(dur=E['clean0'][0] - E['snow0'] + .6, kind='tv', seed=3), at=E['snow0'], gain=-16, pan=-.3)
S(sfx.magic(dur=E['clean0'][1] - E['clean0'][0], key='F', up=True, seed=4), at=E['clean0'][0], gain=-12, pan=-.3)
S(sfx.text_hit('slam'), at=E['title1'], gain=-3)
S(sfx.text_hit('slam', seed=5), at=E['title2'], gain=-1)
S(sfx.pen('marker', dur=.4, seed=6), at=E['title2'] + .35, gain=-12, pan=.2)
S(sfx.swish(dur=.24, seed=7), at=E['sub'] + .1, gain=-12, pan=.3)

# ---- 场景之间的飞行：嗖声峰值放在飞行中点 ----
for i, k in enumerate(['fly1', 'fly2', 'fly3', 'fly4', 'fly5', 'fly6', 'pull', 'fly_cl']):
    a, b = E[k]
    S(sfx.whoosh(dur=b - a + .2, kind='swish', direction=1 if i % 2 == 0 else -1, peak=.5, seed=10 + i), at=(a + b) / 2, gain=-6)
S(sfx.whoosh(dur=1.3, kind='air', direction=1, peak=.5, seed=19), at=E['end_b'] + .3, gain=-12)

# ---- 章节标签：弹出 + 记号笔 ----
for i in range(6):
    t = E[f'ch{i + 1}_tag'] - .3
    S(sfx.pop('mouth', pitch=1.0 + .05 * i), at=t + .05, gain=-6)
    S(sfx.pen('marker', dur=.4, seed=20 + i), at=t + .42, gain=-14, pan=-.2)

# ---- ① 先学认雾 ----
for i in range(3):
    S(sfx.sticker_slap(seed=30 + i), at=E['many'] + .12 * i + .05, gain=-12, pan=-.5)
s0, s1 = E['steps'][0], E['fog'][1] - .3
for k in range(4):
    t = s0 + (s1 - s0) * k / 3
    S(sfx.static(dur=.35, kind='tv', seed=34 + k), at=t, gain=-24 + 2.5 * k, pan=-.2)
    S(sfx.tick('hi'), at=t + .02, gain=-14, pan=-.2)
S(sfx.pop('bubble', pitch=1.2), at=E['dots_hi'] + .05, gain=-9, pan=.2)
S(sfx.swish(dur=.4, seed=38), at=E['window'] + .05, gain=-13)
S(sfx.sticker_slap(seed=39), at=E['note'] + .1, gain=-8, pan=.5)
S(sfx.ding(note=key_note(E['pick'], 0, 24)), at=E['pick'] + .1, gain=-11, pan=.3)
S(sfx.pop('bubble', pitch=.95), at=E['guess'] + .05, gain=-9, pan=.3)
S(sfx.pop('bubble', pitch=1.05), at=E['guess'] + .3, gain=-9, pan=.4)
t0, t1 = E['train']
for k in range(24):
    f = (k / 24) ** .6
    S(sfx.tick('hi'), at=t0 + (t1 - t0) * f, gain=-20 + 6 * k / 24, pan=.3)
S(sfx.stamp('rubber', seed=40), at=E['match'] + .02, gain=-4, pan=.3)
S(sfx.ding(note=key_note(E['match'], 2, 24)), at=E['match'], gain=-9, pan=.3)

# ---- ② 往回擦 ----
S(sfx.static(dur=.8, kind='tv', seed=41), at=E['canvas2'], gain=-18, pan=-.2)
S(sfx.swish(dur=.6, direction=-1, seed=42), at=E['flip'], gain=-10, pan=.3)
for g0, w0, sd in [(E['g1'], E['w1'], 43), (E['g2'], E['w2'], 45)]:
    S(sfx.pop('bubble', pitch=1.1), at=g0 + .05, gain=-9, pan=.4)
    S(sfx.swish(dur=.35, direction=-1, seed=sd), at=w0 + .1, gain=-12, pan=.1)
    wipe(w0, .5, sd + 1, -10, -.1)
f0, f1 = E['fast']
for k in range(16):
    t = f0 + (f1 - f0) * k / 16
    wipe(t, .14, 50 + k, -17, -.2 + .025 * k)
    S(sfx.blip(note=key_note(t, k, 12 + k), kind='sine'), at=t, gain=-20, pan=.2)
S(sfx.stamp('seal', seed=60), at=E['done2'] + .02, gain=-4)
S(sfx.shimmer_hit(note=key_note(E['done2'], 0, 12)), at=E['done2'], gain=-9)

# ---- ③ 文字指路 ----
S(sfx.static(dur=.7, kind='tv', seed=61), at=E['canvas3'], gain=-19, pan=.3)
S(sfx.sticker_slap(seed=62), at=E['q3'] + .1, gain=-8, pan=-.5)
S(sfx.pop('bubble', pitch=1.0), at=E['prompt3'] + .05, gain=-9, pan=-.3)
c0, c1 = E['cells']
for k in range(13):
    S(sfx.tick('hi'), at=c0 + k * .05 + .05, gain=-19 + k * .3, pan=-.4 + k * .03)
S(sfx.whoosh(dur=.6, kind='air', direction=1, peak=.6, seed=63), at=E['arrow3'] + .3, gain=-10, pan=0)
g0, g1 = E['guide']
t = E['look3']
k = 0
while t < g1 + .3:                                      # 箭头每往前拽一下，一声闷闷的推
    S(sfx.impact(kind='punch', size=.25), at=t + .35, gain=-20, pan=.2)
    t += .7; k += 1
S(sfx.magic(dur=g1 - g0, key='F', up=True, seed=64), at=g0, gain=-13, pan=.3)
S(sfx.shimmer_hit(note=key_note(E['scarf'], 2, 12)), at=(g0 + g1) / 2 + .6, gain=-10, pan=.3)

# ---- ④ 指路力度 ----
S(sfx.pop('bubble', pitch=.9), at=E['knob_in'] + .05, gain=-9)
S(sfx.whoosh(dur=.5, kind='air', direction=1, peak=.5, seed=65), at=E['strength'] + .1, gain=-14, pan=.4)
for t0_, dur, n in [(E['low'], .6, 7), (E['high'], .7, 8), (E['back4'], .6, 6)]:
    for k in range(n):
        S(sfx.tick('clock'), at=t0_ + dur * k / n, gain=-15, pan=0)
S(sfx.pop('bubble', pitch=.8), at=E['low'] + .3, gain=-10, pan=-.5)
S(sfx.impact(kind='punch', size=.5), at=E['high'] + .3, gain=-9, pan=.5)
S(sfx.glitch(dur=.25, seed=66), at=E['hard'] + .05, gain=-16, pan=.5)
S(sfx.ui('confirm'), at=E['back4'] + .4, gain=-9)

# ---- ⑤ 换一屏雪花 ----
for p0, sd in [(E['press1'], 70), (E['press2'], 72)]:
    S(sfx.click('hard'), at=p0, gain=-6, pan=-.4)
    for k in range(6):
        S(sfx.tick('clock'), at=p0 + .02 + k * .05, gain=-15 - k, pan=-.4)
    S(sfx.static(dur=.45, kind='tv', seed=sd), at=p0 + .3, gain=-18, pan=-.3)
for a0, a1, sd in [(*E['genA'], 74), (*E['genB'], 75), (*E['genA2'], 76)]:
    S(sfx.magic(dur=a1 - a0, key='F', up=True, seed=sd), at=a0, gain=-15, pan=-.3)
    S(sfx.pop('bubble', pitch=1.15), at=a1 + .2, gain=-10, pan=.4)
S(sfx.typing(n_keys=2, rate=6, kind='typewriter', seed=77), at=E['retype'] + .2, gain=-12, pan=-.4)
S(sfx.static(dur=.45, kind='tv', seed=70), at=E['retype'] + .7, gain=-18, pan=-.3)
bt = max(E['same'], E['genA2'][1] + .4)
S(sfx.pen('marker', dur=.5, seed=78), at=bt, gain=-12, pan=.3)
S(sfx.ding(note=key_note(bt, 0, 24)), at=bt + .3, gain=-8, pan=.3)

# ---- ⑥ 先在小图上擦 ----
S(sfx.static(dur=.7, kind='tv', seed=80), at=E['big6'], gain=-19, pan=-.4)
S(sfx.morph(dur=.6, up=False), at=E['compress'], gain=-11, pan=-.2)
w0, w1 = E['wipe6']
for k in range(5):
    wipe(w0 + (w1 - w0) * k / 5, .25, 81 + k, -14, 0)
S(sfx.morph(dur=.7, up=True), at=E['decode'], gain=-10, pan=.3)
S(sfx.shimmer_hit(note=key_note(E['decoded'][1], 0, 12)), at=E['decoded'][0] + .4, gain=-8, pan=.4)

# ---- 总览：雪花、你的话、猜雾、擦掉、转圈、成图 ----
for i, k in enumerate(['n_snow', 'n_text', 'n_guess', 'n_wipe']):
    S(sfx.pop('mouth', pitch=1.0 + .08 * i), at=E[k] + .05, gain=-8, pan=-.4 + .25 * i)
r0, r1 = E['n_rep']
for k in range(10):
    t = E['n_wipe'] + (r1 - E['n_wipe']) * k / 10
    S(sfx.blip(note=key_note(t, k, 24), kind='tri'), at=t, gain=-15, pan=-.3 + .06 * k)
S(sfx.ding(note=key_note(E['n_out'], 0, 24)), at=E['n_out'] - .3, gain=-9, pan=.4)

# ---- 高潮：满屏雪花沿弯弯的轨迹聚成猫；落地前抽空，砸下 ----
c0, land = E['cl'][0], E['land']
S(sfx.static(dur=land - c0 - .2, kind='tv', seed=90), at=c0, gain=-15)
S(sfx.sparkle(dur=land - c0 - .3, density=34, key='F', seed=91), at=c0 + .4, gain=-12)
S(sfx.riser(dur=2.2, kind='hybrid', end='cut'), at=land - .1, gain=-6)
S(sfx.impact(kind='punch', size=1.0), at=land, gain=2)
S(sfx.boom(dur=1.8), at=land, gain=-2)
S(sfx.shimmer_hit(note=key_note(land, 0, 12)), at=land + .05, gain=-6)


def suck(t):             # "走出来"砸下前，配乐抽空 3 帧
    pts = [(0, 0), (land - 1.1, 0), (land - .6, -8), (land - .11, -8), (land - .1, -40), (land - .004, -40), (land, 0), (DUR, 0)]
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

# ---- 结尾：又冒出一屏雪花，小团子擦掉；字砸下，落款 ----
S(sfx.static(dur=E['e_wipe'] - E['e_snow'] + .5, kind='tv', seed=100), at=E['e_snow'], gain=-19, pan=-.3)
for k in range(4):
    wipe(E['e_wipe'] + .3 * k, .3, 101 + k, -12, -.3)
S(sfx.text_hit('slam', seed=110), at=E['e_calm'] + .05, gain=-5)
S(sfx.text_hit('slam', seed=111), at=E['e_wipe'] + .05, gain=-3)
S(sfx.sticker_slap(seed=112), at=E['e_wipe'] + .1, gain=-6, pan=.4)
S(sfx.ding(note=key_note(E['sign'], 0, 24)), at=E['sign'], gain=-7)

m.master_kw.update(tilt=.4)
os.makedirs(D + 'out', exist_ok=True)
res = m.export(D + 'out/bed.wav', lufs=-16, tp=-2, spectrogram=D + 'out/qc_audio_spec.png')
print({k: v for k, v in res.items() if k not in ('spectrum', 'onsets')} if isinstance(res, dict) else res)
print(mg.hit_alignment(D + 'out/bed.wav', [E['title2'], E['match'], E['done2'], E['land'], E['e_wipe']]))

# 旁白由 opus-code-video 的 scripts/mix_voice.py 叠上去（读 out/bed.wav 和 cues.json 的 voice，写 out/audio.wav）
