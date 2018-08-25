# -*- coding: utf-8 -*-

"""
 In this file, most functions defined in pythons math package are wrapped to
 be used with quantites.
  
 @author: d0cod3r
"""


# wrap a lot of math functions using wrap() from quantites.py

from .quantities import PhysicalQuantity, UNITONE, to_quantity, wrap
from .units import rad
import math

# wrap functions

__all__ = []

###############################################################################
# power and logarithmic functions

exp = wrap(math.exp,
           UNITONE,
           [UNITONE])

log = wrap(math.log,
           UNITONE,
           [UNITONE])

expm1 = wrap(math.expm1,
             UNITONE,
             [UNITONE])

log1p = wrap(math.log1p,
             UNITONE,
             [UNITONE])

log10 = wrap(math.log10,
             UNITONE,
             [UNITONE])

def sqrt(x):
    if isinstance(x, PhysicalQuantity):
        return PhysicalQuantity(math.sqrt(x.value), x._unit**(1/2))
    else:
        return PhysicalQuantity(math.sqrt(x), UNITONE)

__all__.extend(["exp", "log", "expm1", "log1p", "log10", "sqrt"])

###############################################################################
# trigonometric functions

sin = wrap(math.sin,
           UNITONE,
           [rad])

cos = wrap(math.cos,
           UNITONE,
           [rad])

tan = wrap(math.tan,
           UNITONE,
           [rad])

asin = wrap(math.asin,
            rad,
            [UNITONE])

acos = wrap(math.acos,
            rad,
            [UNITONE])

atan = wrap(math.atan,
            rad,
            [UNITONE])

def atan2(x,y):
    x = to_quantity(x)
    y = to_quantity(y).in_unit(x._unit)
    return PhysicalQuantity(math.atan2(x._value, y._value), UNITONE)

def hypot(x, y):
    x = to_quantity(x)
    y = to_quantity(y).in_unit(x._unit)
    return PhysicalQuantity(math.hypot(x._value, y._value), x._unit)

__all__.extend(["sin", "cos", "tan", "asin", "acos", "atan", "atan2", "hypot"])

###############################################################################
# hyperbolic functions

sinh = wrap(math.sinh,
            UNITONE,
            [UNITONE])

cosh = wrap(math.cosh,
            UNITONE,
            [UNITONE])

tanh = wrap(math.tanh,
            UNITONE,
            [UNITONE])

asinh = wrap(math.asinh,
             UNITONE,
             [UNITONE])

acosh = wrap(math.acosh,
             UNITONE,
             [UNITONE])

atanh = wrap(math.atanh,
             UNITONE,
             [UNITONE])

__all__.extend(["sinh", "cosh", "tanh", "asinh", "acosh", "atanh"])

###############################################################################
# Special function

erf = wrap(math.erf,
           UNITONE,
           [UNITONE])

erfc = wrap(math.erfc,
            UNITONE,
            [UNITONE])

__all__.extend(["erf", "erfc"])

