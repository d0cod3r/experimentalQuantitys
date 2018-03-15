# -*- coding: utf-8 -*-

"""
Testing uncertaincys

@author: d0cod3r
"""

from uncertain_values import *

a = UncertainVariable(20, 2, .2)
b = UncertainVariable(30, 3, .3)
c = UncertainVariable(12, 1, .2)

x = 2*a + b
assert x.n == 70.0
assert x.stat == 5.0
assert x.sys == 0.5

y = [a*b, a*2, 2*a, a+2, 2+a, 2/a, b/3, c/b, x-b, 3*(-a)]