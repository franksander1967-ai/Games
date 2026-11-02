"""Synthesised score + sound design for the SV Barkhausen spot (30 s, 48 kHz stereo).
Everything is generated from code: drums, bass, pad, synth brass, foley-style SFX."""
import numpy as np, wave
SR = 48000; DUR = 30.0; N = int(SR * DUR)
rng = np.random.default_rng(1899)
music = np.zeros((N, 2)); sfx = np.zeros((N, 2)); verb_send = np.zeros((N, 2))

def tt(d): return np.arange(int(d * SR)) / SR
def place(buf, t0, sig, gain=1.0, pan=0.0, send=0.0):
    i = int(round(t0 * SR));
    if i >= N: return
    sig = np.asarray(sig, float)
    if sig.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l * 1.414, sig * r * 1.414], 1)
    if i < 0: sig = sig[-i:]; i = 0
    n = min(len(sig), N - i)
    buf[i:i + n] += sig[:n] * gain
    if send: verb_send[i:i + n] += sig[:n] * gain * send

def onepole_lp(x, fc):
    """time-varying one-pole lowpass; fc scalar or array (Hz)"""
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); z = 0.0
    for i in range(len(x)):
        z = (1 - a[i]) * x[i] + a[i] * z; y[i] = z
    return y
def hp(x, fc):
    return x - onepole_lp(x, fc)
def fft_band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def noise(d): return rng.standard_normal(int(d * SR))

# ---------------- instruments ----------------
def kick(amp=1.0, d=0.45):
    t = tt(d); f = 46 + 110 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5) + 0.35 * np.exp(-t * 300) * noise(d)[:len(t)] * 0.3
    return np.tanh(s * 1.6) * amp
def clap(amp=1.0):
    d = 0.32; t = tt(d); n = fft_band(noise(d), 900, 5000)
    env = np.zeros_like(t)
    for o in (0, 0.011, 0.022): env += np.where(t >= o, np.exp(-(t - o) * 90), 0)
    env += 0.5 * np.where(t >= 0.03, np.exp(-(t - 0.03) * 16), 0)
    return n * env * amp * 0.6
def hat(amp=1.0, open_=False):
    d = 0.35 if open_ else 0.06; t = tt(d); n = fft_band(noise(d), 7000, 16000)
    return n * np.exp(-t * (14 if open_ else 70)) * amp * 0.5
def crash(amp=1.0, d=2.4):
    t = tt(d); n = fft_band(noise(d), 3500, 17000)
    return n * np.exp(-t * 1.9) * amp * 0.45
def additive(freq, d, bright, n_h=24, detune=(0,), vib=0.0):
    """bandlimited saw-ish tone; bright(t) -> spectral tilt (0 dark .. 1 bright)"""
    t = tt(d); out = np.zeros_like(t); b = bright(t)
    vibr = 1 + vib * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.12) * 4, 0, 1)
    for dt in detune:
        f0 = freq * (1 + dt) * vibr; ph = 2 * np.pi * np.cumsum(f0) / SR
        for k in range(1, n_h + 1):
            if freq * k > 15000: break
            out += np.sin(k * ph) / k * np.exp(-(k - 1) * (1.0 - b) * 0.9)
    return out / len(detune)
def brass(freq, d, amp=1.0):
    t = tt(d)
    att = np.clip(t / 0.035, 0, 1); rel = np.clip((d - t) / 0.08, 0, 1)
    s = additive(freq, d, lambda t: 0.35 + 0.55 * np.clip(t / 0.09, 0, 1) * np.exp(-t * 1.2), n_h=28,
                 detune=(-0.004, 0, 0.005), vib=0.006)
    return s * att * rel * amp * 0.35
def bass(freq, d, amp=1.0):
    t = tt(d); env = np.clip(t / 0.005, 0, 1) * np.exp(-t * 4.5) * np.clip((d - t) / 0.02, 0, 1)
    s = additive(freq, d, lambda t: 0.25 + 0.4 * np.exp(-t * 18), n_h=14)
    s += 0.8 * np.sin(2 * np.pi * freq * t)
    return np.tanh(s * env * 1.3) * amp * 0.5
def pad(freqs, d, amp=1.0, bright=0.25):
    t = tt(d); env = np.clip(t / 0.25, 0, 1) * np.clip((d - t) / 0.3, 0, 1)
    s = sum(additive(f, d, lambda t: bright + 0 * t, n_h=10, detune=(-0.006, 0.006)) for f in freqs)
    return s * env * amp * 0.12
def pluck(freq, amp=1.0, d=0.35):
    t = tt(d); s = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t) * np.exp(-t * 30)
    return s * np.exp(-t * 14) * np.clip(t / 0.002, 0, 1) * amp * 0.3
def bell(freq, amp=1.0, d=1.2):
    t = tt(d); s = sum(a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t * dc) for r, a, dc in
                      ((1, 1, 3), (2.76, .5, 6), (5.4, .25, 10), (8.9, .12, 16)))
    return s * np.clip(t / 0.002, 0, 1) * amp * 0.25
def tick(amp=1.0, f=2600):
    t = tt(0.03); return np.sin(2 * np.pi * f * t) * np.exp(-t * 260) * amp * 0.5 + fft_band(noise(0.03), 2000, 9000) * np.exp(-t * 400) * amp * 0.15
def thud(amp=1.0, f=95):
    t = tt(0.3); ph = 2 * np.pi * np.cumsum(f * (1 + 0.8 * np.exp(-t * 40))) / SR
    return (np.sin(ph) * np.exp(-t * 14) + onepole_lp(noise(0.3), 600) * np.exp(-t * 25) * 1.2) * amp
def whoosh(d, amp=1.0, f0=300, f1=5000, shape='up'):
    t = tt(d); x = t / d
    env = np.sin(np.pi * np.clip(x, 0, 1)) ** 1.5 if shape == 'arc' else (x ** 2.2 if shape == 'up' else (1 - x) ** 2)
    if shape == 'up': env = env * np.clip((d - t) / 0.01, 0, 1)
    fc = f0 * (f1 / f0) ** (x if shape != 'down' else 1 - x)
    s = onepole_lp(onepole_lp(noise(d), fc), fc)
    return s * env * amp * 2.2
def shot():
    d = 1.6; t = tt(d)
    pop = fft_band(noise(d), 700, 9000) * np.exp(-t * 150) * 1.4          # air release
    clk = np.sin(2 * np.pi * 4200 * t) * np.exp(-t * 500)                   # trigger click
    ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dc) * a for f, a, dc in ((2130, .12, 7), (3410, .08, 9), (5310, .05, 12)))
    f = 40 + 90 * np.exp(-t * 10); boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6) * 1.1
    rum = onepole_lp(noise(d), 180) * np.exp(-t * 3) * 1.5
    return np.tanh((pop + clk * .5 + ring + boom + rum) * 1.2)
def heartbeat(amp=1.0):
    d = 0.5; out = np.zeros(int(d * SR))
    for o, a in ((0, 1), (0.17, 0.6)):
        t = tt(0.25); f = 52 + 30 * np.exp(-t * 30)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16) * a
        i = int(o * SR); out[i:i + len(s)] += s
    return np.tanh(out * 1.5) * amp
def jingle(amp=1.0, f=None):
    t = tt(0.25); f = f or rng.uniform(3000, 7000)
    s = sum(np.sin(2 * np.pi * f * r * t) * np.exp(-t * (25 + 10 * r)) for r in (1, 1.47, 2.09))
    return s * amp * 0.12

# ---------------- note helpers ----------------
def hz(n):  # n like 'D2'
    names = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}
    nm, o = n[:-1], int(n[-1]); return 440 * 2 ** ((names[nm] + 12 * (o + 1) - 69) / 12)
CH = {'Dm': (['D3', 'F3', 'A3'], 'D2'), 'Bb': (['Bb2', 'D3', 'F3'], 'Bb1'), 'F': (['F3', 'A3', 'C4'], 'F2'), 'C': (['C3', 'E3', 'G3'], 'C2')}
BEAT = 0.5

# ---------------- arrangement ----------------
# chord timeline (start, end, chord)
prog = [(3, 5, 'Dm'), (5, 7, 'Bb'), (7, 9, 'F'), (9, 11, 'C'), (11, 13, 'Dm'), (13, 15, 'Bb'), (15, 17, 'F'), (17, 19, 'C'),
        (19, 21, 'Dm'), (22.5, 23.5, 'Bb'), (23.5, 25, 'C'), (25, 27, 'Bb'), (27, 29, 'C')]
kicks = []
def drums(a, b, kind='A'):
    t = a
    while t < b - 1e-6:
        beat_i = round((t - 3.0) / BEAT)
        bi = beat_i % 4
        kicks.append(t); place(music, t, kick(1.0))
        if bi in (1, 3): place(music, t, clap(0.8), pan=0.05, send=0.25)
        if kind in ('A', 'B'):
            place(music, t + BEAT / 2, hat(0.55, open_=(kind == 'B')), pan=0.3)
            place(music, t, hat(0.3), pan=-0.25)
        if kind == 'B':
            place(music, t + BEAT * 0.25, hat(0.22), pan=-0.3); place(music, t + BEAT * 0.75, hat(0.22), pan=-0.3)
        if kind == 'C' and bi == 2: place(music, t + BEAT * 0.75, kick(0.6))
        t += BEAT
drums(3.0, 9.75, 'A'); drums(10.0, 15.0, 'B'); drums(15.0, 20.0, 'C'); drums(22.5, 24.5, 'B'); drums(25.0, 29.0, 'B')
place(music, 29.0, kick(1.1)); kicks.append(29.0)
for k in range(8): place(music, 24.0 + k * 0.0625, clap(0.25 + k * 0.08), pan=(-1) ** k * 0.2)  # snare roll into zoom
for (a, b, c) in prog:
    notes, bn = CH[c]
    place(music, a, pad([hz(n) for n in notes], b - a, amp=1.0, bright=0.35 if a < 21 else 0.45), send=0.4)
    t = a
    while t < b - 1e-6:
        if not (9.75 <= t < 10.0):
            place(music, t + BEAT / 2, bass(hz(bn), BEAT * 0.48, 0.9))
            if c in ('Dm', 'Bb') and round((t - a) / BEAT) % 2 == 1: place(music, t + BEAT * 0.75, bass(hz(bn) * 2, BEAT * 0.2, 0.5))
        t += BEAT
# final F chord
place(music, 29.0, pad([hz(n) for n in ['F3', 'A3', 'C4', 'F4']], 1.0, amp=1.4, bright=0.5), send=0.5)
place(music, 29.0, bass(hz('F2'), 0.9, 1.0))
# brass fanfares (synth horns)
def fanfare(t0, seq, amp=1.0):
    for (dt, n, d) in seq:
        place(music, t0 + dt, brass(hz(n), d, amp), pan=-0.15, send=0.5)
        place(music, t0 + dt, brass(hz(n) / 2, d, amp * 0.6), pan=0.15, send=0.5)
fanfare(15.0, [(0, 'A3', .2), (.25, 'D4', .2), (.5, 'F4', .2), (.75, 'A4', .9)], 0.9)
fanfare(25.0, [(0, 'C4', .2), (.25, 'F4', .2), (.5, 'A4', .2), (.75, 'C5', 1.0), (2.0, 'Bb4', .22), (2.25, 'A4', .22), (2.5, 'G4', .9)], 1.0)
for n in ['F3', 'A3', 'C4', 'F4']: place(music, 29.0, brass(hz(n), 0.95, 0.75), send=0.6)
place(music, 3.5, brass(hz('D3'), .45, .9), send=.4); place(music, 3.5, brass(hz('A3'), .45, .7), send=.4)
# crashes
for tc, a in ((3.0, .8), (10.0, .6), (15.0, .8), (22.5, .9), (25.0, 1.0), (29.0, .9)): place(music, tc, crash(a), send=0.2)

# sidechain ducking of music bus by kick
duck = np.ones(N)
for k in kicks:
    i = int(k * SR); t = tt(0.3); e = 1 - 0.55 * np.exp(-t * 14)
    n = min(len(e), N - i); duck[i:i + n] = np.minimum(duck[i:i + n], e[:n])
# (applied to pads/bass only would be ideal; applied globally but kicks restore since they ride on top)

# ---------------- intro: heartbeat + tension ----------------
for b in (0.15, 1.05, 1.95): place(sfx, b, heartbeat(1.0))
t = tt(2.9); drone = (np.sin(2 * np.pi * 36.7 * t) + 0.4 * np.sin(2 * np.pi * 73.4 * t)) * (t / 2.9) ** 1.5 * 0.35
place(sfx, 0, drone)
place(sfx, 0.4, whoosh(2.45, 0.35, 200, 3000, 'up'))     # breath-in tension
for b in (0.15, 1.05, 1.95): place(sfx, b + 0.02, tick(0.4, 1800))

# ---------------- SFX timeline ----------------
place(sfx, 3.0, shot(), 1.0, send=0.35)
place(sfx, 3.38, whoosh(.25, .5, 400, 3000, 'arc'), pan=.4)
place(sfx, 3.5, thud(1.0, 70), send=.2)
place(sfx, 4.4, whoosh(.38, .7, 300, 6000, 'arc'), pan=-.6)
place(sfx, 4.55, whoosh(.45, .6, 200, 4000, 'up'), pan=.3)
place(sfx, 5.0, thud(.7, 110)); place(sfx, 5.0, tick(.6)); place(sfx, 5.12, tick(.5, 2300)); place(sfx, 5.3, tick(.5, 2000))
place(sfx, 5.45, whoosh(.6, .6, 500, 7000, 'arc'), pan=.7)
t = tt(.05); place(sfx, 5.95, (np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 120) + fft_band(noise(.05), 2000, 8000) * np.exp(-t * 150)) * .6)  # bolt click
for i, tw in enumerate((6.5, 6.62, 6.74, 6.86)): place(sfx, tw, tick(.3, 2000 + i * 150), pan=-.3)
place(sfx, 7.75, thud(.8, 80))
d = .26; t = tt(d); place(sfx, 8.25, fft_band(noise(d), 1500, 8000) * np.exp(-t * 9) * (1 + np.sin(2 * np.pi * 38 * t)) * .5, pan=.2)  # strike-through scratch
place(sfx, 8.75, tick(.4, 2200))
place(sfx, 9.62, whoosh(.5, 1.0, 200, 8000, 'up'), send=.2)    # wipe
place(sfx, 10.2, tick(.5)); place(sfx, 10.32, tick(.5, 2300)); place(sfx, 11.0, tick(.35, 2100)); place(sfx, 11.4, tick(.35, 2400))
place(sfx, 12.0, whoosh(.3, .5, 600, 6000, 'arc'))
place(sfx, 12.25, tick(.5)); place(sfx, 12.75, thud(.9, 75)); place(sfx, 12.75, clap(.6), send=.3)
t = tt(.25); place(sfx, 13.0, np.sin(2 * np.pi * np.cumsum(1800 - 1200 * t / .25) / SR) * .15 * np.clip(t / .05, 0, 1))  # falling whistle
place(sfx, 13.25, thud(1.0, 85), send=.15)
penta = ['D5', 'F5', 'G5', 'A5', 'C6', 'D6', 'F6']
order = [3, 11, 7, 0, 13, 5, 9, 1, 14, 6, 2, 10, 4, 12, 8]
for k in range(15): place(sfx, 13.55 + k * .045, pluck(hz(penta[k % 7]), .55), pan=rng.uniform(-.6, .6), send=.3)
for k in range(26): place(sfx, 14.4 + rng.uniform(0, .9) ** 1.6 * .9, jingle(rng.uniform(.4, 1)), pan=rng.uniform(-.5, .5), send=.3)
place(sfx, 14.85, whoosh(.6, .9, 150, 5000, 'arc'), send=.2)    # medallion mask
yrs = [1899 + round((2026 - 1899) * (1 - (1 - 2 ** (-10 * min(1, x / 1.25))))) for x in np.arange(0, 1.3, 1 / 120)]
last = None
for i, y in enumerate(yrs):
    if y != last and (i % 2 == 0 or y == 1899): place(sfx, 15.25 + i / 120, tick(.22, 3000), pan=.2)
    last = y
place(sfx, 16.55, thud(.5, 120))
place(sfx, 16.75, tick(.35)); place(sfx, 17.3, whoosh(.45, .9, 200, 6000, 'arc'))
place(sfx, 17.5, thud(.8, 80)); place(sfx, 18.0, thud(.8, 70))
for i, n in enumerate(['D5', 'F5', 'A5', 'D6', 'F6']): place(sfx, 18.0 + i * .07, bell(hz(n), .6), pan=.5, send=.5)
for i, tw in enumerate((18.75, 18.87, 19.0, 19.15)): place(sfx, tw, tick(.28, 2000 + i * 120))
# riser 20 -> 21, hard stop
d = 1.0; t = tt(d); rs = onepole_lp(noise(d), 300 * (40 ** (t / d))) * (t / d) ** 2 * 1.6
rs += np.sin(2 * np.pi * np.cumsum(200 * 4 ** (t / d)) / SR) * (t / d) ** 2 * .12
place(sfx, 20.0, rs)
# silence 21 -> 22.5
place(sfx, 21.2, tick(.25, 1600)); place(sfx, 21.42, tick(.25, 1500))
place(sfx, 21.7, heartbeat(.6))
t = tt(.75); place(sfx, 21.6, np.sin(2 * np.pi * np.cumsum(300 + 500 * (t / .75) ** 2) / SR) * .05 * np.sin(np.pi * t / .75))  # servo
t = tt(.06); bp = np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 40) * .25
place(sfx, 22.35, bp); place(sfx, 22.42, bp * .7)
d = .5; t = tt(d); place(sfx, 22.0, fft_band(noise(d), 2500, 15000) * (t / d) ** 3 * .9, send=.3)   # reverse swell
place(sfx, 22.5, shot(), .9, send=.3); place(sfx, 22.5, thud(.9, 65))
place(sfx, 23.25, pluck(hz('A5'), .8)); place(sfx, 23.25, tick(.4))
place(sfx, 23.5, pluck(hz('D6'), .8)); place(sfx, 23.5, tick(.4))
place(sfx, 24.45, whoosh(.55, 1.1, 150, 9000, 'up'), send=.25)   # zoom
place(sfx, 25.0, thud(.9, 60))
place(sfx, 26.05, tick(.4)); place(sfx, 26.5, whoosh(.5, .4, 2000, 9000, 'arc'), pan=.5)
for i in range(5): place(sfx, 26.75 + i * .06, tick(.18, 2600 + 90 * i), pan=.3)
place(sfx, 27.15, pluck(hz('C6'), .7)); place(sfx, 27.15, tick(.3))
for i, tw in enumerate((27.6, 27.72, 27.84, 27.96, 28.1)): place(sfx, tw, tick(.2, 1900 + i * 100))

# ---------------- mix ----------------
music *= duck[:, None]
# reverb: stereo exponential-noise IR
def reverb(x, dur=1.6, decay=3.2):
    t = tt(dur); out = np.zeros_like(x)
    for ch in range(2):
        ir = rng.standard_normal(len(t)) * np.exp(-t * decay); ir = onepole_lp(ir, 5000); ir[:int(.012 * SR)] = 0
        n = len(x) + len(ir); nf = 1 << (n - 1).bit_length()
        out[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch], nf) * np.fft.rfft(ir, nf), nf)[:len(x)]
    return out / 12
mix = music * 0.36 + sfx * 0.9 + reverb(verb_send) * 0.9
# silence window (21.0-22.5): hard cut of music tails
cut = np.ones(N); i0, i1 = int(21.0 * SR), int(22.5 * SR)
cut[i0:i1] = 0.0; cut[i0 - 240:i0] = np.linspace(1, 0, 240)
music_tail = mix.copy()
mix = mix * cut[:, None] + 0  # keep only sfx placed in the silent window:
sil = np.zeros_like(sfx); sil[i0:i1] = sfx[i0:i1]
mix[i0:i1] += sil[i0:i1] * 0.9
# end fade
fo = int(0.35 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
pk = np.max(np.abs(mix)); mix = mix / pk * 0.89
with wave.open('score.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok peak', pk)
