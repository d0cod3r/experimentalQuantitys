# -*- coding: utf-8 -*-

"""
 This module allows to calculate with uncertain values using error propagation.
 A statistic deviation as well as a systematic uncertainty can be
 defined and are handled including their correlations.
 
 The common way to create an uncertain variable is the method
 "UncertainVariable" or short "UVar". It takes at least one and at most three
 arguments: The first is the nominal value, second "stat" the statistic
 standard deviation and third "sys" the systematic standard deviation. Both
 uncertainties are default to 0.
 All variables created as above are thougt to be independent. If you want to
 create variables with designated correlations, use "correlated_values",
 which takes a list of nominal values and a statistic and a systematic
 covariance matrix.
 
 Uncertain Variables can be used just like normal floats. They support +, -,
 *, /, ** with other uncertain variables or with floats. The result will an
 uncertain variable again and further calculations with it will consider the
 correlations.
 
 You can access the nominal value of an uncertain variable x with
 x.nominal_value or short x.n, the uncertainties with
 x.statistical_standard_deviation, x.stat_std_dev or x.stat respectivly
 x.systematic_standard_deviation, x.sys_std_dev or x.sys.
 All of those values are floats.
 
 This module also defines most functions of pyhtons math package, such as sqrt, 
 exp, log, sin, cos and others. These functions support uncertain variables
 as well as normal floats.
 
 If you are interested in the covariances or correaltions, the methods
 stat_cov_mat and stat_corr_mat (and same for sys) will calculate the
 covariance respectively correlation matrices.
 
 Uncertain variables support comparison (==, <, <=, ...).
 For every operation except ==, the values are compared, ignoring the
 uncertainties.
 For ==, only a difference of exactly 0, without uncertainty, will return true.
 Therefor, a>=b and a<=b does not imply a==b.
 
 You can wrap functions to wupport uncertain variables using the function wrap.
 It takes a function to wrap and an iterable of derivatives. If the derivatives
 are not known, they can be performed numerically.
 Call help(wrap) for details.
 
 To find everything not listed here, look up the functions name in __all__ and
 get information with help( <function> ).
 
 @author: d0cod3r
"""

from .uncertain_values import *
from .uncertain_values import __all__

from .uncertain_math import *
from .uncertain_math import __all__ as all_math

__all__.extend(all_math)
