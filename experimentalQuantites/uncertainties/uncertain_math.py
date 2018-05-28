# -*- coding: utf-8 -*-

"""
 In this file, most functions defined in pythons math package are wrapped to
 be used with uncertain values from this module.
 
 Call help(uncertain_math) to list all functions. 
 
 @author: d0cod3r
"""


# wrap a lot of math functions using wrap() from uncertain_values

import uncertainties.uncertain_values as uv
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

exp = uv.wrap(math.exp,
              [ math.exp
              ])

log = uv.wrap(math.log,
              [ log_derivative_0,
                lambda x, y: -math.log(x)/(math.log(y)**2)/y
              ])

expm1 = uv.wrap(math.expm1,
                [ math.exp
                ])

log1p = uv.wrap(math.log1p,
                [ lambda x: 1/(1+x)
                ])

log10 = uv.wrap(math.log10,
                [ lambda x: 1/x/math.log(10)
                ])

sqrt = uv.wrap(math.sqrt,
               [ nan_if_exception(lambda x: 1/2/math.sqrt(x))
               ])

__all__.extend(["exp", "log", "expm1", "log1p", "log10", "sqrt"])

###############################################################################
# trigonometric functions

sin = uv.wrap(math.sin, [math.cos])

cos = uv.wrap(math.cos,
              [ lambda x: -math.sin(x) ])

tan = uv.wrap(math.tan,
              [ lambda x: 1+math.tan(x)**2 ])

asin = uv.wrap(math.asin,
               [ nan_if_exception(lambda x: 1/math.sqrt(1-x**2)) ])

acos = uv.wrap(math.acos,
               [ nan_if_exception(lambda x: -1/math.sqrt(1-x**2)) ])

atan = uv.wrap(math.atan,
               [ lambda x: 1/(1+x**2) ])

atan2 = uv.wrap(math.atan2,
                [ nan_if_exception(lambda x,y: y/(x**2+y**2)),
                  nan_if_exception(lambda x,y: -x/(x**2+y**2)) ])

hypot = uv.wrap(math.hypot,
                [ nan_if_exception(lambda x,y: x/math.hypot(x,y)),
                  nan_if_exception(lambda x,y: y/math.hypot(x,y)) ])

__all__.extend(["sin", "cos", "tan", "asin", "acos", "atan", "atan2", "hypot"])

###############################################################################
# angular conversion

degrees = uv.wrap(math.degrees,
                  [ lambda x: degrees_per_rad ])

radians = uv.wrap(math.radians,
                  [ lambda x: rads_per_degree ])

###############################################################################
# hyperbolic functions

sinh = uv.wrap(math.sinh, [math.cosh])

cosh = uv.wrap(math.cosh, [math.sinh])

tanh = uv.wrap(math.tanh,
               [ nan_if_exception(lambda x: 1-math.tanh(x)**2) ])

asinh = uv.wrap(math.asinh,
                [ nan_if_exception(lambda x: 1/math.sqrt(1+x**2)) ])

acosh = uv.wrap(math.acosh,
                [ nan_if_exception(lambda x: 1/math.sqrt(x**2-1)) ])

atanh = uv.wrap(math.atanh,
                [ nan_if_exception(lambda x: 1/(1-x**2)) ])

__all__.extend(["sinh", "cosh", "tanh", "asinh", "acosh", "atanh"])

###############################################################################
# Special function

erf = uv.wrap(math.erf,
              [ lambda x: erf_coef*math.exp(-x**2) ])

erfc = uv.wrap(math.erfc,
               [ lambda x: -erf_coef*math.exp(-x**2) ])

__all__.extend(["erf", "erfc"])
