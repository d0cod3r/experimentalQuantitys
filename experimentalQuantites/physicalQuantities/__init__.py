# -*- coding: utf-8 -*-
"""
TODO doc

!!! Important !!! Comparing quantities checks whether the units are compatible.
Comparing two quantites with different dimensions will not return False but
raise an exception.

@author: d0cod3r
"""

from .quantities import PhysicalQuantity, to_quantity, in_unit, \
                        is_compatible, userUnit, wrap, UNITONE

from .units import *

from .math import *