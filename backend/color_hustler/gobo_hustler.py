from .controllable import Controllable, validate_string_constant
from itertools import cycle
from . import frame_clock

def validate_iterable(subvalidator):
    def validate(items):
        try:
            iter(items)
        except TypeError:
            raise ValueError("Input must be iterable; got {}".format(items))

        values = [subvalidator(i) for i in items]
        if not values:
            raise ValueError("Must provide at least one value.")
        return values
    return validate

def validate_easing(value):
    value = float(value)
    if value <= 0.0:
        raise ValueError("Negative easing makes no sense.")

def create_banks(n):
    indices = list(range(n))

    every = cycle([indices])
    singles = cycle([[i] for i in range(n)])

    evens = [i for i in indices if i % 2 == 0]
    odds = [i for i in indices if i % 2 == 1]

    two_values = cycle([evens, odds])

    return {
        GoboHustler.ALL: every,
        GoboHustler.SINGLE: singles,
        GoboHustler.TWO_VALUE: two_values,
    }



class GoboHustler(Controllable):
    ALL = 'all'
    SINGLE = 'single'
    TWO_VALUE = 'two_value'

    parameters = dict(
        easing=validate_easing,
        bank_name=validate_string_constant([ALL, SINGLE, TWO_VALUE], 'bank name'),
    )

    def __init__(self, param_gen, trig, rotos):
        self.easing = 0.1
        self.param_gen = param_gen
        self.controls = []

        self.trig = trig

        self.rotos = rotos

        for roto in rotos:
            self.controls.extend(roto.get_controls())

        self.control_params = [Easer(0.0) for _ in self.controls]

        self.last_render = frame_clock.time()

        self._bank_name = self.SINGLE
        self.banks = create_banks(len(self.control_params))
        self.bank = self.banks[self._bank_name]


    @property
    def bank_name(self):
        return None

    @bank_name.setter
    def bank_name(self, bank_name):
        self._bank_name = bank_name
        self.bank = self.banks[bank_name]

    def render(self, dmx_frame):
        # we may need to switch banks
        # FIXME this does NOT belong in the render method

        now = frame_clock.time()

        dt = now - self.last_render
        self.last_render = now

        if self.trig.trigger():
            input_value = self.param_gen.get()

            # If triggering, set new targets for the next pattern in the bank.
            pattern = next(self.bank)
            for i in pattern:
                self.control_params[i].target = input_value

        for control, param in zip(self.controls, self.control_params):
            value = param.ease(dt, self.easing)
            control(value)

        for roto in self.rotos:
            roto.render(dmx_frame)

class Easer:
    """Linearly ease current value towards target by at most easing/second."""
    def __init__(self, initial_value):
        self.target = initial_value
        self.current = initial_value

    def ease(self, dt, easing):
        dv = self.target - self.current

        dv_max = dt * easing


        # TODO clean this up once the internet is available
        if abs(dv) > dv_max:
            if dv > 0.0:
                actual_dv = dv_max
            else:
                actual_dv = -1.0*dv_max
        else:
            actual_dv = dv

        self.current += actual_dv
        return self.current
