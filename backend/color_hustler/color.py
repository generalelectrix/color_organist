"""Color model, color generation, and color operations."""
from husl import rgb_to_husl as rgb_to_husl_args
from husl import husl_to_rgb as husl_to_rgb_args

from random import Random

from . import param_gen as pgen

def rgb_to_husl(coordinates):
    # fix the stupid range used for HUSL
    h, s, l = rgb_to_husl_args(*coordinates)
    return [h / 360., s / 100., l / 100.]

def husl_to_rgb(coordinates):
    # fix the stupid range used for HUSL
    h, s, l = coordinates
    return husl_to_rgb_args(h * 360., s * 100., l * 100.)

def hsv_to_rgb(coordinates):
    hue, saturation, value = coordinates
    if saturation == 0.0:
        return value, value, value

    hue = hue * 6.0
    if hue == 6.0:
        hue = 0.0
    sector = int(hue)
    v_1 = value*(1.0-saturation)
    v_2 = value*(1.0 - saturation * (hue - sector))
    v_3 = value*(1.0 - saturation * (1 - (hue - sector)))

    if sector == 0:
        r, g, b = value, v_3, v_1
    elif sector == 1:
        r, g, b = v_2, value, v_1
    elif sector == 2:
        r, g, b = v_1, value, v_3
    elif sector == 3:
        r, g, b = v_1, v_2, value
    elif sector == 4:
        r, g, b = v_3, v_1, value
    else:
        r, g, b = value, v_1, v_2

    return [r, g, b]

def rgb_to_hsv(coordinates):
    red, green, blue = coordinates
    min_val = min(red, green, blue)
    max_val = max(red, green, blue)
    delta = max_val - min_val

    value = max_val

    if delta == 0.0:
        # this is a gray, arbitrarily choose hue = 0
        hue = 0.0
        saturation = 0.0
    else:
        saturation = delta / max_val

        delta_r = (((max_val - red)/6) + (delta/2))/delta
        delta_g = (((max_val - green)/6) + (delta/2))/delta
        delta_b = (((max_val - blue)/6) + (delta/2))/delta

        if red == max_val:
            hue = delta_b - delta_g
        elif green == max_val:
            hue = (1.0 / 3.0) + delta_r - delta_b
        else:
            hue = (2.0 / 3.0) + delta_g - delta_r

        if hue < 0.0:
            hue += 1.0
        elif hue > 1.0:
            hue -= 1.0

    return [hue, saturation, value]

def identity(coordinates):
    return coordinates

space_to_rgb_map = {'rgb': identity,
                    'hsv': hsv_to_rgb,
                    'husl': husl_to_rgb}

rgb_to_space_map = {'rgb': identity,
                    'hsv': rgb_to_hsv,
                    'husl': rgb_to_husl}

def convert_color_space(source_space, target_space, coordinates):
    rgb_representation = space_to_rgb_map[source_space](coordinates)
    return rgb_to_space_map[target_space](rgb_representation)

def clamp(val, min_val, max_val):
    return min(max(min_val, val), max_val)

class Color(object):
    """A color in a particular color space.
    """
    def __init__(self, color_space, coordinates):
        """Create a new color using a particular color space and coordinates."""
        self.space = color_space

        # ensure valid values for coordinates
        clamped_coordinates = [clamp(coord, 0.0, 1.0) for coord in coordinates]

        self.coordinates = clamped_coordinates

    def in_rgb(self):
        return self.in_color_space('rgb')

    def in_hsv(self):
        return self.in_color_space('hsv')

    def in_husl(self):
        return self.in_color_space('husl')

    def in_color_space(self, color_space):
        return Color(color_space, convert_color_space(self.space, color_space, self.coordinates))

    def __str__(self):
        return "{} color with coordinates ({}).".format(self.space, self.coordinates)

    def __eq__(self, other):
        """Use RGB color space for comparisons."""
        if isinstance(other, Color):
            return self.in_rgb() == other.in_rgb()

    def __ne__(self, other):
        return not self == other

    def get_coordinate(self, color_space, coordinate_index):
        """Get a coordinate of this color in any color space."""
        shifted_coordinates = convert_color_space(self.space, color_space, self.coordinates)
        return shifted_coordinates[coordinate_index]

    def set_coordinate(self, color_space, coordinate_index, value):
        """Set a coordinate of this color in any color space.

        Does not change the color space representation of this color.
        Clamps the value to be a unit float.
        """
        value = clamp(value, 0.0, 1.0)
        shifted_coordinates = convert_color_space(self.space, color_space, self.coordinates)
        shifted_coordinates[coordinate_index] = value
        self.coordinates = convert_color_space(color_space, self.space, shifted_coordinates)

    # coordinate getters and setters
    # RGB

    @property
    def red(self):
        return self.get_coordinate('rgb', 0)

    @red.setter
    def red(self, value):
        self.set_coordinate('rgb', 0, value)

    @property
    def green(self):
        return self.get_coordinate('rgb', 1)

    @green.setter
    def green(self, value):
        self.set_coordinate('rgb', 1, value)

    @property
    def blue(self):
        return self.get_coordinate('rgb', 2)

    @blue.setter
    def blue(self, value):
        self.set_coordinate('rgb', 2, value)

    # HSV

    @property
    def hue_hsv(self):
        return self.get_coordinate('hsv', 0)

    @hue_hsv.setter
    def hue_hsv(self, value):
        self.set_coordinate('hsv', 0, value)

    @property
    def sat_hsv(self):
        return self.get_coordinate('hsv', 1)

    @sat_hsv.setter
    def sat_hsv(self, value):
        self.set_coordinate('hsv', 1, value)

    @property
    def val_hsv(self):
        return self.get_coordinate('hsv', 2)

    @val_hsv.setter
    def val_hsv(self, value):
        self.set_coordinate('hsv', 2, value)

    # HUSL

    @property
    def hue_husl(self):
        return self.get_coordinate('husl', 0)

    @hue_husl.setter
    def hue_husl(self, value):
        self.set_coordinate('husl', 0, value)

    @property
    def sat_husl(self):
        return self.get_coordinate('husl', 1)

    @sat_husl.setter
    def sat_husl(self, value):
        self.set_coordinate('husl', 1, value)

    @property
    def lev_husl(self):
        return self.get_coordinate('husl', 2)

    @lev_husl.setter
    def lev_husl(self, value):
        self.set_coordinate('husl', 2, value)

# coordinate unpacking

def unpack_c0(color):
    return color.coordinates[0]

def unpack_c1(color):
    return color.coordinates[1]

def unpack_c2(color):
    return color.coordinates[2]

def repack_c0(color, c0):
    color.coordinates[0] = c0

def repack_c1(color, c1):
    color.coordinates[1] = c1

def repack_c2(color, c2):
    color.coordinates[2] = c2

def add_hue_hsv(color, value):
    """Add a value to the HSV hue.

    Returns a color in HSV.
    """
    col_hsv = color.in_hsv()
    col_hsv.hue_hsv = (col_hsv.hue_hsv + value) % 1.0
    return col_hsv

def add_hue_husl(color, value):
    """Add a value to the HUSL hue.

    Returns a color in HUSL.
    """
    col_husl = color.in_husl()
    col_husl.hue_husl = (col_husl.hue_husl + value) % 1.0
    return col_husl

# possibly useful color constants

def red():
    return Color('rgb', (1.0, 0.0, 0.0))

def green():
    return Color('rgb', (0.0, 1.0, 0.0))

def blue():
    return Color('rgb', (0.0, 0.0, 1.0))

def cyan():
    return Color('rgb', (0.0, 1.0, 1.0))

def yellow():
    return Color('rgb', (1.0, 1.0, 0.0))

def magenta():
    return Color('rgb', (1.0, 0.0, 1.0))

def black():
    return Color('rgb', (0.0, 0.0, 0.0))

def white():
    return Color('rgb', (1.0, 1.0, 1.0))

# FIXME: this entire notion is silly, these aren't anything special, refactor
# them away.

class ColorGenerator:
    def __init__(self, h_gen, s_gen, v_gen, colorspace='husl'):
        """Create a new random color generator."""
        self.h_gen = h_gen
        self.s_gen = s_gen
        self.v_gen = v_gen
        self.colorspace = colorspace

    def get(self):
        """Get the next random color from this generator."""
        h_val = self.h_gen.get_constrained(0.0, 1.0, mode='wrap')
        s_val = self.s_gen.get_constrained(0.0, 1.0, mode='fold')
        v_val = self.v_gen.get_constrained(0.0, 1.0, mode='fold')

        return Color(self.colorspace, (h_val, s_val, v_val))


class ColorSwarm:
    """Agglomerate multiple color generators."""
    def __init__(self, col_gens, random=False, seed=None):
        """Create a new ColorSwarm.

        Args:
            col_gens: ([color generator]) A list of color generators to agglomerate.
            random (default=False): pick a generator randomly when get is called.
            seed (optional): a seed for the swarm's internal RNG
        """
        self.random = random
        self.rand_gen = Random()
        if seed is not None:
            self.rand_gen.seed(seed)
        self.gens = col_gens
        self.next = 0

    def get(self):
        """Get a color from the next generator."""
        if self.random:
            gen = self.rand_gen.randint(0, len(self.gens)-1)
            return self.gens[gen].get()

        # advance to the next generator first in case the number of gens has
        # changed since the last call.
        self.next = (self.next + 1) % len(self.gens)
        col = self.gens[self.next].get()
        return col

