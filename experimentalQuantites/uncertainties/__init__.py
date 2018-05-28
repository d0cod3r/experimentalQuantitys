# -*- coding: utf-8 -*-

"""
 This module allows to calculate uncertain values using error propagation.
 A statistic deviations as well as a systematic uncertainty can be
 defined and are handled including their correlations.
 
 TODO documentation, tutorial
 
 @author: d0cod3r
"""

from .uncertain_values import *
from .uncertain_values import __all__

from .uncertain_math import *
from .uncertain_math import __all__ as all_math

__all__.extend(all_math)
