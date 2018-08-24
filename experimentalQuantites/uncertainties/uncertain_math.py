# -*- coding: utf-8 -*-

"""
 In this file, most functions defined in pythons math package are wrapped to
 be used with uncertain values from this module.
 
 Call help(uncertain_math) to list all functions. 
 
 @author: d0cod3r
"""


# wrap a lot of math functions using wrap() from uncertain_values

from .uncertain_values import wrap
import math


# float("nan") is used for derivatives that could not be calculated
NOT_DIFFERENTIABLE = float("nan")

# an exception in the derivative is replaced by the flag
def nan_if_exception(function):
    """
    Wraps a functin tow return the NOT_DIFFERENTIALBE flag used in this
    module, float("nan"]). Even if a derivative can not be calculated, the
    function is still well definded if the uncertainty is zero.
    """
    def wrapped_func(*args):
        try:
               return function(*args)
        except (ValueError, ZeroDivisionError, OverflowError):
               return NOT_DIFFERENTIABLE
    return wrapped_func


# define more complex derivatives and some constants used later

def log_derivative_0(*args):
    if len(args)==1:
        # base e
        return 1/args[0]
    else:
        return 1/args[0]/math.log(args[1])

degrees_per_rad = 180/math.pi
rads_per_degree = math.pi/180

erf_coef = 2/math.sqrt(math.pi)


# wrap functions

__all__ = []

###############################################################################
# power and logarithmic functions

exp = wrap(math.exp,
           [ math.exp
           ])

log = wrap(math.log,
           [ log_derivative_0,
             lambda x, y: -math.log(x)/(math.log(y)**2)/y
           ])

expm1 = wrap(math.expm1,
             [ math.exp
             ])

log1p = wrap(math.log1p,
             [ lambda x: 1/(1+x)
             ])

log10 = wrap(math.log10,
            [ lambda x: 1/x/math.log(10)
            ])

sqrt = wrap(math.sqrt,
            [ nan_if_exception(lambda x: 1/2/math.sqrt(x))
            ])

__all__.extend(["exp", "log", "expm1", "log1p", "log10", "sqrt"])

###############################################################################
# trigonometric functions

sin = wrap(math.sin, [math.cos])

cos = wrap(math.cos,
           [ lambda x: -math.sin(x) ])

tan = wrap(math.tan,
           [ lambda x: 1+math.tan(x)**2 ])

asin = wrap(math.asin,
            [ nan_if_exception(lambda x: 1/math.sqrt(1-x**2)) ])

acos = wrap(math.acos,
            [ nan_if_exception(lambda x: -1/math.sqrt(1-x**2)) ])

atan = wrap(math.atan,
            [ lambda x: 1/(1+x**2) ])

atan2 = wrap(math.atan2,
             [ nan_if_exception(lambda x,y: y/(x**2+y**2)),
                  nan_if_exception(lambda x,y: -x/(x**2+y**2)) ])

hypot = wrap(math.hypot,
             [ nan_if_exception(lambda x,y: x/math.hypot(x,y)),
               nan_if_exception(lambda x,y: y/math.hypot(x,y)) ])

__all__.extend(["sin", "cos", "tan", "asin", "acos", "atan", "atan2", "hypot"])

###############################################################################
# angular conversion

degrees = wrap(math.degrees,
               [ lambda x: degrees_per_rad ])

radians = wrap(math.radians,
               [ lambda x: rads_per_degree ])

__all__.extend(["degrees", "radians"])

###############################################################################
# hyperbolic functions

sinh = wrap(math.sinh, [math.cosh])

cosh = wrap(math.cosh, [math.sinh])

tanh = wrap(math.tanh,
            [ nan_if_exception(lambda x: 1-math.tanh(x)**2) ])

asinh = wrap(math.asinh,
             [ nan_if_exception(lambda x: 1/math.sqrt(1+x**2)) ])

acosh = wrap(math.acosh,
             [ nan_if_exception(lambda x: 1/math.sqrt(x**2-1)) ])

atanh = wrap(math.atanh,
             [ nan_if_exception(lambda x: 1/(1-x**2)) ])

__all__.extend(["sinh", "cosh", "tanh", "asinh", "acosh", "atanh"])

###############################################################################
# Special function

erf = wrap(math.erf,
           [ lambda x: erf_coef*math.exp(-x**2) ])

erfc = wrap(math.erfc,
            [ lambda x: -erf_coef*math.exp(-x**2) ])

__all__.extend(["erf", "erfc"])
