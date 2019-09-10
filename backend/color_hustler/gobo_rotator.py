"""Fixture driver for various gobo rotators.

--- Roto-Q DMX ---
0: stopped

Max speed: DMX value 1, about 0.43 rot/sec
It looks like several values are bucketed to the same speed.  Buckets:
1
2
3 4 5
6 7
8 9 10
11 12
13
14 15
16 17
18
19 20
the remainder seem to be singlets

On the upper end:
255 254
253
252 251 250
249 248
247 246 245
244 243
242
241 240
239 238
237
236 235
singlets below

There's no actual DMX value in the center for no rotation. 127 and 128 are each
the slowest value for each rotation direction.  This explains some things...

Measurements:
[
    (128, 0.00479),
    (137, 0.01),
    (147, 0.0169),
    (157, 0.03),
    (167, 0.0454),
    (177, 0.063),
    (187, 0.0792),
    (197, 0.106),
    (207, 0.1425),
    (217, 0.177),
    (227, 0.242),
    (237, 0.308),
    (242, 0.345),
    (249, 0.3875),
    (255, 0.43),
]

--- Smart Move DMX ---

Some odd bucketing:
5 6 7 8 are the same speed
18 19 same speed

124 is slowest
133 is slowest in other direction
125-132 is stopped

251 250 249 248 same speed
238 237 same speed

Measurements:
[
    (135, 0.00193),
    (145, 0.0027),
    (155, 0.00583),
    (165, 0.0102),
    (175, 0.0175),
    (176, 0.0194),
    (179, 0.0244),
    (181, 0.0306),
    (183, 0.0406),
    (184, 0.0481),
    (185, 0.0604),
    (187, 0.0794),
    (189, 0.0909),
    (191, 0.0972),
    (193, 0.107),
    (195, 0.116),
    (205, 0.141),
    (215, 0.166),
    (225, 0.191),
    (235, 0.223),
    (245, 0.27),
    (249, 0.293),
    (255, 0.344),
]

This shit is bananas.

--- GOBO SPINNAZ ---

(DHA Varispeed driven by GOBO SPINNAZ driver)

Unsurprisingly, straight as an arrow, given linear voltage drive of a DC motor.
Max speed is MUCH slower than the other two rotator styles.

[
    (15, 0.0075),
    (35, 0.0225),
    (55, 0.0377),
    (75, 0.0523),
    (95, 0.0669),
    (115, 0.0825),
    (135, 0.0963),
    (155, 0.111),
    (175, 0.127),
    (195, 0.141),
    (215, 0.156),
    (235, 0.17),
    (255, 0.185),
]

If we normalize speed so the fastest rotator at max is 1, we lose a lot of the
upper range and resolution of the faster rotators.  I think I'll scale them so
that the slowest rotator's max speed is 1.0, but make the profiles understand
control signals outside of 1.0 if we want to reach up to higher values.

1.0 thus means 0.185 Hz or 11.1 rpm.
"""
from bisect import bisect_left
from .param_gen import clamp

class GoboSpinna:
    """Control profile for custom DHA Varispeed driven by GOBO SPINNAZ.

    Channel layout:
    0: gobo 1 direction
    1: gobo 1 speed
    2: gobo 2 direction
    3 gobo 2 speed
    """
    def __init__(self, address):
        self.address = address
        self.g0 = 0.0
        self.g1 = 0.0

    def render(self, buf):
        d0, s0 = self._render_single(self.g0)
        d1, s1 = self._render_single(self.g1)
        buf[self.address] = d0
        buf[self.address + 1] = s0
        buf[self.address + 2] = d1
        buf[self.address + 3] = s1

    def _render_single(self, value):
        direction = 0 if value <= 0.0 else 255
        speed = int(clamp(abs(value) * 255, 0, 255))
        return direction, speed

class RotoQDmx:
    """Control profile for Apollo Roto-Q DMX.

    Channel layout:
    0: direction/speed
    1: set to 0 for rotation mode
    """
    def __init__(self, address);
        self.address = address
        self.value = 0.0

    def render(self, buf):
        # 218 on the upper end is the speed for value = 1.0
        # 128 is the slowest in the positive direction
        # only about 90 real speed values otherwise in this range



def take_closest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after
    else:
       return before


def build_lut(meas):
    x = [m[0] for m in meas]
    s = [m[1] for m in meas]

    ds_dx = [ds/dx for ds, dx in zip(delta(s), delta(x))]

    values = []
    for value in range(x[0], x[-1]+1):
        base_s, base_x, base_ds_dx = s[0], x[0], ds_dx[0]
        for x0, s0, ds0 in zip(x, s, ds_dx):
            if value - x0 < 0:
                break
            base_s, base_x, base_ds_dx = s0, x0, ds0


        speed = base_s + (value - base_x)*base_ds_dx

        values.append((speed, value))
    return values

def delta(vals):
    return [h - l for l, h in zip(vals, vals[1:])]































