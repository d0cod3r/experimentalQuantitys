# -*- coding: utf-8 -*-

"""
 TODO documentation
 
 @author: d0cod3r
"""


# TODO how it works

from numbers import Number
from sys import float_info
from itertools import repeat
from collections import defaultdict
from math import sqrt, floor, log, log10
from types import MappingProxyType


# float("nan") is used for derivatives that could not be calculated
NOT_DIFFERENTIALBE = float("nan")

# The amount of significant digits with the same or a smaller order of 
# magnitude as the greatest uncertainty 
SIGNIFICANT_DIGITS = 2

FLOAT_LIKE_TYPES = (Number,)

# Step size for numeric differentiation
try:
    # should give good results in most cases
    EPSILON = sqrt(float_info.epsilon)
except AttributeError:
    EPSILON = 1e-8


def partial_derivate(function, arg_index):
    """
    Partial derivative of a function with respect to the arg_index-th
    argument.
    
    The derivative is calculated numerically as ( f(x+e) - f(x-e) ) / (2*e)
    """
    def partial_derivative(*args):
        """
        Numerically calculated partial derivative of %s.
        """ % function.__name__
        
        # numerical step must be greater with greater arguments because of
        # precision limits
        epsilon = EPSILON*(abs(args[arg_index])+1)
        
        args = list(args)
        
        args[arg_index] += epsilon
        f_shifted_pos = function(*args)
        
        args[arg_index] -= 2 * epsilon
        f_shifted_neg = function(*args)
        
        return (f_shifted_pos - f_shifted_neg) /epsilon /2
        
    return partial_derivative


# Define derivatives of x**y.
# The function is not defined if x<0 and y%1 != 0 or if x=0 and y<0

def pow_derivative_0(x, y):
    # derivative of x**y with respect to x. Not differentiabe in x=0, except
    # if y%1=0
    # Test y==0 first, as this is differentiable even in x=0
    if y==0:
        return 0.
    elif x != 0 or y%1==0:
        return y*x**(y-1)
    else:
        return NOT_DIFFERENTIALBE

def pow_derivative_1(x, y):
    # derivative of x**y with respect to y.
    if x==0 and y>0:
        return 0.
    elif x>0:
        return log(x)*x**y
    else: # cases x<0 and (x,y)=(0,0)
        return NOT_DIFFERENTIALBE


class IndexableIterator(object):
    """
    Wrapper around an iterator that allows to access it like a list. It caches
    the results in a list and generates new ones if needed.
    It is possible to give a function to convert None, if it appears in the
    iterator.
    """
    
    def __init__(self, iterator, none_converter=lambda i: None):
        """
        Initialise an IndexableIterator.
        
        iterator -- The iterable to wrap.
        
        none_converter -- Optional: A function that takes an index and is
        called to replace None, if it is returned from the iterator. The defalt
        converter does nothing.
        """
        self._iter = iterator
        self._none_converter = none_converter
        self._cache = []
    
    def __getitem__(self, index):
        """
        Acces the index-th element of the wrapped iterable.
        """
        while index >= len(self._cache):
            next_element = next(self._iter)
            if next_element is None:
                next_element = self._none_converter(index)
            self._cache.append(next_element)
        return self._cache[index]


class NegativeStandardDeviation(ValueError):
    """
    Raised if a negative standard deviation is given.
    """
    pass


def to_affine_approximation(x):
    """
    If x is an AffineApproximation, return x.
    Otherwise, attempt to wrap x as an AffineApproximation with uncertainty 0.
    """
    if isinstance(x,AffineApproximation):
        return x
    if isinstance(x, FLOAT_LIKE_TYPES):
        # Return a AffineApproximation, not a Variable, as the uncertainty does
        # not have to be saved, it is 0 by default
        return AffineApproximation(x, LinearPart({}))
    raise ValueError("Can not transform other than floatlike values to a"
                     "constant AffineApproximation.")


def wrap(function, derivatives=None):
    # using itertools.repeat to generate numeric derivatives for any amount of
    # arguments
    """
    Build a wrapper around a function. The new function will accept uncertain
    values as well as other types and return an uncertain variable with the
    right uncertainties and correlations.
    It can therefor be used in the same way as the orgininal function, only
    with some arguments being uncertain numbers instead of floats.
    
    WARNING: Keyword-arguments are not supported
    
    The function must return a value that can be converted to float.
    
    
    function -- The function to wrap
    
    derivatives -- If known, analytical derivatives can be given as an iterable.
    The n-th element must be the partial derivative of the function with
    respect to the n-th argument and accept the same amount and types as
    arguments as the original function.
    If None occours, it will be replaced by a numerical derivative.
    If the argument is a list, it must have the same length as the amount
    of arguments given to the function.
    """
    if derivatives is None:
        derivatives = repeat(None)
    if isinstance(derivatives, list):
        # Replace None with numeric derivative
        for (index, element) in enumerate(derivatives):
            if element is None:
                derivatives[index] = partial_derivate(function, index)
    else: # case of every other iterable
        none_converter = lambda i: partial_derivate(function, i)
        derivatives = IndexableIterator(derivatives, none_converter)
    
    def wrapped_function(*args):
        """
        A wrapped version of %s to also accept uncertain values as arguments
        and to return an uncertain value.
        
        Original documentation:
        %s
        """ % (function.__name__, function.__doc__) 
        # Search uncertain inputs
        pos_with_uncert = [index for (index, value) in enumerate(args) if
                   isinstance(value, AffineApproximation)]
        
        # extract nominal values from uncertain arguments and use them to
        # calculate the nomainal result
        # must be done first, so in case of an error the exception is raised
        # by calculating the nominal value, not the derivatives
        nominal_args = list(args)
        for index in pos_with_uncert:
            nominal_args[index] = args[index].nominal_value
        nominal_result = function(*nominal_args)
        
        # build the linear part using the derivatives
        linear_part = []
        for index in pos_with_uncert:
            linear_part.append((
                    # get the LinearPart from the uncertain value
                    args[index]._linear_part,
                    # calculate the coefficient from the derivative
                    derivatives[index](*nominal_args) ))
        
        return AffineApproximation(nominal_result, LinearPart(linear_part))
    
    wrapped_function.__name__ = function.__name__
    
    return wrapped_function


class LinearPart(object):
    """
    This helper class stores the linear part of an uncertain variable.
    
    It basicially maps from variables to the coefficient of their
    differential.
    At first, the variables do not have to be the independent variables
    lying underneath. Only if the LinearPart is expanded, it will resolve
    the given variables to those.
    At this, the form of this object might change, but it will still
    contain the same content.
    """
    
    __slots__ = "_linear_combo"
    
    def __init__(self, linear_combination):
        """
        The given linear_combo can be modified by the object.
        This is needed when expanding it, when replacing the depencies
        from the given variables to the independent ones lying
        underneath.

        linear_combination -- Can be either a dict or a list.
        If it is a dict, it should represent an expanded linear combination
        and map underlying independet variables to the coefficient of their
        differential.
        If it is a list, it should contain (LinearPart, coefficient) pairs
        to map (not independent) variables to the coefficient of their
        differential. This form might be converted to a dict.
        """
        
        self._linear_combo = linear_combination
    
    def is_expanded(self):
        """
        Returns True if the linear combination is expanded, False otherwise.
        """
        return isinstance(self._linear_combo, dict)
    
    def expand(self):
        """
        Expands the linear combination, converts a list to a dict.
        
        This method should only be called if the linear combination is not yet
        expanded.
        
        The new linear combination will be a collections.defaultdict(float)
        """
        
        # The list in self._linear_combo will be emptied and each element be
        # used to build the derivatives. Expanded LinearParts are directly
        # added to the factors, non expanded LinearParts will be appended
        # and expanded here.
        
        # Alternative method: Call not expanded LinearParts recursively. This
        # would need more space, but save time if several calculations are
        # done with the same variables.
        # The here used method is more efficient in large calculations with
        # only one result, which is the more typical case. For example, large
        # sums have linear runtime with this, quadratic runtime with the
        # recursive method
        
        # new linear combination, start with an empty dict
        new_linear_combo = defaultdict(float)
        
        # disasseble the list
        while self._linear_combo:
            
            # extract one list element
            (main_linear_part, main_factor) = self._linear_combo.pop()
            
            if main_linear_part.is_expanded():
                for (variable, factor) in main_linear_part._linear_combo.items():
                    
                    # adjust derivative
                    new_linear_combo[variable] += main_factor*factor
            
            else: # non expanded form
                for (linear_part, factor) in main_linear_part._linear_combo:
                    
                    # add all elements with combined factor
                    self._linear_combo.append((linear_part, main_factor*factor))
            
        self._linear_combo = new_linear_combo
    
    def get_linear_combo(self):
        """
        Expands the linear combo, if it not already is expanded.
        
        Returns the linear combo, a collections.defaultdict(float)
        """
        
        if not self.is_expanded():
            self.expand()
        
        return self._linear_combo


class AffineApproximation(object):
    """
    AffineApproximation is the superclass of UncertainVariable and the
    most general representation of an uncertain number.
    
    It contains a nominal value and a linear part, describing the result
    of a calculation and its local surronding, which is approximated linear.
    According to the laws of error propagation, this can be used for
    further calculations.
    
    The class supports basic arithmetics and can be used in the mathematical
    functions defined in uncertain_math.
    """
    
    # faster acces and less storage consumption
    __slots__ = ("_nominal_value", "_linear_part")
    
    def __init__(self, nominal_value, linear_part):
        """
        Initialises an AffineApproximation.
        
        nominal_value -- value of the approximation when the linear part
        is zero.
        
        linear_part -- an instance of class LinearPart describing the linear
        approximation of a calculation around the nominal value.
        """
        
        # Converting to a float.
        # If nominal_value can not be converted to float, it does not
        # make sense to be used here.
        self._nominal_value = float(nominal_value)
        
        # The linear part will only be expanded if needed. This should
        # make calculations faster. See LinearPart for details.
        self._linear_part = linear_part
    
    def __hash__(self):
        return id(self)
    
    @property
    def nominal_value(self):
        """
        Nominal value of this uncertain value.
        """
        return self._nominal_value
    
    # Abbrevation to make formulars shorter
    n = nominal_value
    
    @property
    def derivatives(self):
        """
        Return a map from variables to derivatives of this function to these
        variables.
        """
        # Using types.MappingProxyType to give a readonly view
        return MappingProxyType( self._linear_part.get_linear_combo() )
    
    def uncertainty_components(self, kind="stat"):
        """
        Return a map from variables to the uncertainty of this object coming
        from that variable. Depending on argument kind, you can either access
        statistical or systematical uncertainty.
        The variables will be the independent ones lying underneath.
        
        kind -- can be either "stat", which is default, or "sys"
        """
        derivatives = self.derivatives
        
        uncertainty_components = {}
        
        if kind == "stat":
            for (variable, derivative) in derivatives.items():
                uncert = variable.stat_std_dev
                # derivative can be nan if uncertainty is 0
                if uncert == 0:
                    uncertainty_components[variable] = 0
                else:
                    uncertainty_components[variable] = abs(derivative*uncert)
            return uncertainty_components
            
        elif kind == "sys":
            for (variable, derivative) in derivatives.items():
                uncert = variable.sys_std_dev
                # derivative can be nan if uncertainty is 0
                if uncert == 0:
                    uncertainty_components[variable] = 0
                else:
                    uncertainty_components[variable] = abs(derivative*uncert)
            return uncertainty_components
        
        else:
            raise ValueError("kind has to be stat or sys")
    
    
    @property
    def statistical_standard_deviation(self):
        """
        Resulting statistical standard deviation.
        """
        stat_std_dev = sqrt(sum(
                d**2 for d in self.uncertainty_components("stat").values()))
        
        return stat_std_dev
    
    stat_std_dev = statistical_standard_deviation
    
    stat = statistical_standard_deviation
    
    @property
    def systematic_standard_deviation(self):
        """
        Resulting systematical standard deviation
        """
        sys_std_dev = sqrt(sum(
                d**2 for d in self.uncertainty_components("sys").values()))
        
        return sys_std_dev
    
    sys_std_dev = systematic_standard_deviation
    
    sys = systematic_standard_deviation
    
    def significant_digits(self):
        """
        Return the index of the last significant digit.
        
        
        The convention of how many digits with the same or a smaller order of
        magnitude as the greater uncertainty are relevant is set in the
        constant SIGNIFICANT_DIGITS.
        """
        max_std_dev = max(self.stat_std_dev, self.sys_std_dev)
        return int(floor(log10(abs(max_std_dev))))-SIGNIFICANT_DIGITS
    
    def __repr__(self):
        #TODO only give significant digits (or dont?)
        return "%r+-%r(stat)+-%r(sys)" % (self.n, self.stat, self.sys)
        
    # TODO __str__, __format__
    
    def __add__(self, other):
        if isinstance(other, AffineApproximation):
            linear_part = LinearPart([(self._linear_part, 1), (other._linear_part, 1)])
            nominal_value = self.nominal_value + other.nominal_value
        elif isinstance(other, FLOAT_LIKE_TYPES):
            linear_part = LinearPart([(self._linear_part, 1)])
            nominal_value = self.nominal_value + other
        else:
            return NotImplemented
        return AffineApproximation(nominal_value, linear_part)
    
    def __sub__(self, other):
        if isinstance(other, AffineApproximation):
            linear_part = LinearPart([(self._linear_part, 1), (other._linear_part, -1)])
            nominal_value = self.nominal_value - other.nominal_value
        elif isinstance(other, FLOAT_LIKE_TYPES):
            linear_part = LinearPart([(self._linear_part, 1)])
            nominal_value = self.nominal_value - other
        else:
            return NotImplemented
        return AffineApproximation(nominal_value, linear_part)
    
    def __mul__(self, other):
        if isinstance(other, AffineApproximation):
            linear_part = LinearPart([(self._linear_part, other.nominal_value),
                                  (other._linear_part, self.nominal_value)])
            nominal_value = self.nominal_value * other.nominal_value
        elif isinstance(other, FLOAT_LIKE_TYPES):
            linear_part = LinearPart([(self._linear_part, other)])
            nominal_value = self.nominal_value * other
        else:
            return NotImplemented
        return AffineApproximation(nominal_value, linear_part)
    
    def __truediv__(self, other):
        if isinstance(other, AffineApproximation):
            linear_part = LinearPart([(self._linear_part, 1/other.nominal_value),
                        (other._linear_part, -self.nominal_value/other.nominal_value**2)])
            nominal_value = self.nominal_value / other.nominal_value
        elif isinstance(other, FLOAT_LIKE_TYPES):
            linear_part = LinearPart([(self._linear_part, 1/other)])
            nominal_value = self.nominal_value / other
        else:
            return NotImplemented
        return AffineApproximation(nominal_value, linear_part)
    
    # The reflected operators are only called if the left operand is not an
    # AffineApproximation, so there is no need to consider this case
    
    def __radd__(self, other):
        if isinstance(other, FLOAT_LIKE_TYPES):
            linear_part = LinearPart([(self._linear_part, 1)])
            nominal_value = self.nominal_value + other
            return AffineApproximation(nominal_value, linear_part)
        else:
            return NotImplemented
    
    def __rsub__(self, other):
        if isinstance(other, FLOAT_LIKE_TYPES):
            linear_part = LinearPart([(self._linear_part, -1)])
            nominal_value = other - self.nominal_value
        else:
            return NotImplemented
        return AffineApproximation(nominal_value, linear_part)
    
    def __rmul__(self, other):
        if isinstance(other, FLOAT_LIKE_TYPES):
            linear_part = LinearPart([(self._linear_part, other)])
            nominal_value = self.nominal_value * other
            return AffineApproximation(nominal_value, linear_part)
        else:
            return NotImplemented
    
    def __rtruediv__(self, other):
        if isinstance(other, FLOAT_LIKE_TYPES):
            linear_part = LinearPart([(self._linear_part, -other/self.nominal_value**2)])
            nominal_value = other / self.nominal_value
            return AffineApproximation(nominal_value, linear_part)
        else:
            return NotImplemented
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        return self * (-1) # Using __mul__
    
    def __ne__(self, other):
        # only a difference of excactly zero, without uncertainty, is
        # considered equal
        d = self - other
        return (d.nominal_value or d.stat_std_dev or d.sys_std_dev)
    
    def __eq__(self, other):
        return not self.__ne__(other)
    
    def __lt__(self, other):
        if isinstance(other, AffineApproximation):
            return self.nominal_value < other.nominal_value
        elif isinstance(other, FLOAT_LIKE_TYPES):
            return self.nominal_value < other
        else:
            return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, AffineApproximation):
            return self.nominal_value <= other.nominal_value
        elif isinstance(other, FLOAT_LIKE_TYPES):
            return self.nominal_value <= other
        else:
            return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, AffineApproximation):
            return self.nominal_value > other.nominal_value
        elif isinstance(other, FLOAT_LIKE_TYPES):
            return self.nominal_value > other
        else:
            return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, AffineApproximation):
            return self.nominal_value >= other.nominal_value
        elif isinstance(other, FLOAT_LIKE_TYPES):
            return self.nominal_value >= other
        else:
            return NotImplemented
    
    def __abs__(self):
        if self >= 0: # using __ge__
            return self
        else:
            return -self # using __neg__
    
    def __bool__(self):
        # Everything except exactly zero is considered True
        return self != 0 # using __ne__
    
    def __float__(self):
        return self.nominal_value
    
    def __int__(self):
        return int(float(self)) # using __float__
    
    # TODO round, floor, ceil,
    
    __pow__ = wrap(lambda x,y: x**y, [pow_derivative_0, pow_derivative_1])
    __rpow__ = wrap(lambda x,y: y**x, [lambda x,y: pow_derivative_1(y,x),
                                       lambda x,y: pow_derivative_0(y,x)])

class UncertainVariable(AffineApproximation):
    """
    Represents a number with a statistical deviations and a systematical
    uncertainty.
    Diffrent from AffineApproximation, it represents an independet value,
    while AffineApproximations can have correlations. In return, an
    UncertainVariable stores its statistical and systematical standard
    deviation.
    """
    
    __slots__ = ("_stat_std_dev", "_sys_std_dev")
    
    def __init__(self, nominal_value, statistic_uncertainty=0,
                 systematic_uncertainty=0):
        """
        Initialise an independend variable.
        
        nominal_value -- nominal value, float-like
        statistic_uncertainc -- statistic uncertainty, float-like
        systematic_uncertainty -- systematic uncertainty, float-like
        """
        # With this, calculations can be handled the same as with
        # other AffineApproximations
        linear_part = LinearPart({self: 1.})
        super().__init__(nominal_value, linear_part)
        
        # Using not >= instead of < accepts nan as uncertainty, which is
        # used if the uncertainty could not be calculated
        if not (statistic_uncertainty >= 0 and systematic_uncertainty >= 0):
            raise NegativeStandardDeviation()
        
        self._stat_std_dev = float(statistic_uncertainty)
        self._sys_std_dev = float(systematic_uncertainty)
    
    @property
    def statistical_standard_deviation(self):
        """
        Resulting statistical standard deviation.
        """
        return self._stat_std_dev
    
    stat_std_dev = statistical_standard_deviation
    
    stat = statistical_standard_deviation
    
    @property
    def systematical_standard_deviation(self):
        """
        Resulting systematical standard deviation
        """
        return self._sys_std_dev
    
    sys_std_dev = systematical_standard_deviation
    
    sys = systematical_standard_deviation


def nominal_value(x):
    """
    Return the nominal value of x if it is an uncertain value as
    defined in this module.
    Otherwise it returns x unchanged.

    This can be usefull to groups of numbers, where only some have
    an uncertainty while others are just floats.
    """

    if isinstance(x, AffineApproximation):
        return x.nominal_value
    else:
        return x

nom_val = nominal_value

def statistical_standard_deviation(x, default=0.0):
    """
    Return the statistical standard deviation of x if it is an uncertain
    value as defined in this module.
    Otherwise it will return default, which is default to 0.

    This can be usefull to groups of numbers, where only some have
    an uncertainty while others are just floats.
    """

    if isinstance(x, AffineApproximation):
        return x.stat_std_dev
    else:
        return default

stat = stat_std_dev = statistical_standard_deviation

def systematic_standard_deviation(x, default=0.0):
    """
    Return the systematical standard deviation of x if it is an uncertain
    value as defined in this module.
    Otherwise it will return default, which is default to 0.

    This can be usefull to groups of numbers, where only some have
    an uncertainty while others are just floats.
    """

    if isinstance(x, AffineApproximation):
        return x.sys_std_dev
    else:
        return default

sys = sys_std_dev = systematic_standard_deviation


def statistical_covariance_matrix(*numbers):
    """
    Calculate a matrix of statistic covariances to a vector of uncertain
    values. The order of the matrix depends on the order of the elements in
    the vector, covariance_matrix[i][j] is the covariance of numbers[i] and
    numbers[j].
    Returns a list of lists.
    
    numbers -- Some uncertain values
    """
    # build the left under part of the matrix
    covariance_matrix = []
    for (i, number1) in enumerate(numbers):
        derivatives1 = number1.derivatives
        vars1 = derivatives1.keys()
        matrix_line = []
        for number2 in numbers[:i+1]:
            derivatives2 = number2.derivatives
            # using dict.get to define 0 as default, as number2 may not depend
            # on var.
            matrix_line.append(sum(
                    ((derivatives1[var]*derivatives2.get(var,0.)*(var.stat_std_dev)**2)
                    for var in vars1))
                    # All elements shold be floats by convention, so add .0
                     + .0)
        covariance_matrix.append(matrix_line)
    
    # make the matrix symmetric
    size = len(numbers)
    for i in range(size-1):
        for j in range(i+1, size):
            covariance_matrix[i].append(covariance_matrix[j][i])
    
    return covariance_matrix

stat_cov_mat = statistical_covariance_matrix

def systematic_covariance_matrix(*numbers):
    """
    Calculate a matrix of systematic covariances to a vector of uncertain
    values. The order of the matrix depends on the order of the elements in
    the vector, covariance_matrix[i][j] is the covariance of numbers[i] and
    numbers[j].
    Returns a list of lists.
    
    numbers -- Some uncertain values
    """
    # build the left under part of the matrix
    covariance_matrix = []
    for (i, number1) in enumerate(numbers):
        derivatives1 = number1.derivatives
        vars1 = derivatives1.keys()
        matrix_line = []
        for number2 in numbers[:i+1]:
            derivatives2 = number2.derivatives
            # using dict.get to define 0 as default, as number2 may not depend
            # on var.
            matrix_line.append(sum(
                    ((derivatives1[var]*derivatives2.get(var,0.)*(var.sys_std_dev)**2)
                    for var in vars1))
                    # All elements shold be floats by convention, so add .0
                     + .0)
        covariance_matrix.append(matrix_line)
    
    # make the matrix symmetric
    size = len(numbers)
    for i in range(size-1):
        for j in range(i+1, size):
            covariance_matrix[i].append(covariance_matrix[j][i])
    
    return covariance_matrix
    
    # make the matrix symmetric
    size = len(numbers)
    for i in range(size-1):
        for j in range(i+1, size):
            covariance_matrix[i].append(covariance_matrix[j][i])
    
    return covariance_matrix

sys_cov_mat = systematic_covariance_matrix


def statistical_correlation_matrix(*numbers):
    """
    Calculate a matrix of statistic correlations to a vector of uncertain
    values. The order of the matrix depends on the order of the elements in
    the vector, correlation_matrix[i][j] is the correlation of numbers[i]
    and numbers[j].
    Returns a list of lists.
    
    numbers -- Some uncertain values
    """
    size = len(numbers)
    matrix = statistical_covariance_matrix(numbers, kind)
    # copy variances, as the matrix is altered
    variances = [matrix[i][i] for i in range(size)]
    for i in range(size):
        for j in range(size):
            matrix[i][j] /= sqrt(variances[i]*variances[j])
    return matrix

stat_corr_mat = statistical_correlation_matrix


def systematic_correlation_matrix(*numbers):
    """
    Calculate a matrix of systematic correlations to a vector of uncertain
    values. The order of the matrix depends on the order of the elements in
    the vector, correlation_matrix[i][j] is the correlation of numbers[i]
    and numbers[j].
    Returns a list of lists.
    
    numbers -- Some uncertain values
    """
    size = len(numbers)
    matrix = systematic_covariance_matrix(numbers, kind)
    # copy variances, as the matrix is altered
    variances = [matrix[i][i] for i in range(size)]
    for i in range(size):
        for j in range(size):
            matrix[i][j] /= sqrt(variances[i]*variances[j])
    return matrix

sys_corr_mat = systematic_correlation_matrix


# Exported functions
__all__ = [ "UncertainVariable",               # init an uncertain variable
            "to_affine_approximation",         # wrap a float
            "nominal_value",                   # access nominal values
            "nom_val",
            "statistical_standard_deviation",  # access statistical uncertainty 
            "stat_std_dev",
            "stat",
            "systematic_standard_deviation",   # acces systematic uncertainty
            "sys_std_dev",
            "sys",
            "statistical_covariance_matrix",   # statistical covariances
            "stat_cov_mat",
            "systematic_covariance_matrix",    # systematic covariances
            "sys_cov_mat",
            "statistical_correlation_matrix",  # statistic correlations
            "stat_corr_mat",
            "systematic_correlation_matrix",   # systematic correlations
            "sys_corr_mat",
            "wrap"                             # wrap functions
          ]

# some methods depend on numpy and are only defined if its is available
try:
    import numpy
    import numpy.matlib
except ImportError:
    pass
else:
    
    # numpy brings more types of numbers
    FLOAT_LIKE_TYPES += (numpy.number,)
    
    def correlated_values(nominal_values, statistic_covariances=0,
                          systematic_covariances=0):
        """
        To given covariance matrices and nominal values, create uncertain
        variables that satisfy these relations.
        Returns a list of uncertain variables, so that the covariance of
        variables[i] and variables[j] is covariances[i,j]
        
        nominal_values -- A list of nominal values for the created variables
        
        statistic_covariances -- The statistic covariance matrix of the values
        to create. Can be either a sqare matrix with the same lenght as
        nominal_values in both dimensions, or a scalar. In the second case, the
        covariance between any two created variables will be the given value.
        Default to 0.
        
        systematic_covariances -- The systematic covariance matrix of the
        values to create. Can be either a sqare matrix with the same lenght as
        nominal_values in both dimensions, or a scalar. In the second case, the
        covariance between any two created variables will be the given value.
        Default to 0.
        """
        
        # The idea of this method is to do a change of basis. The covariance
        # matrices are diagonalised and the inital basis is expressed as a
        # linear combination of the eigenvectors. As the eigenvectors are
        # uncorrelated, they can be represented by an UncertainVariable.
        
        # if a scalar is given, create a matrix
        size = len(nominal_values)
        if isinstance(statistic_covariances, FLOAT_LIKE_TYPES):
            statistic_covariances = [[statistic_covariances]*size]*size
        if isinstance(systematic_covariances, FLOAT_LIKE_TYPES):
            systematic_covariances = [[systematic_covariances]*size]*size
        
        # diagonalize the covariance matrix to get independent variables
        variances, vectors1 = numpy.linalg.eigh(statistic_covariances)
        
        # some uncertainties might be calculated negative due to numertic
        # errors. Setting them to 0 gives close and useful results
        variances[variances < 0] = 0.
        
        # indepentend variables
        variables1 = [UncertainVariable(0, sqrt(var), 0) for var in variances]
        
        # same for systematic uncertainties
        variances, vectors2 = numpy.linalg.eigh(systematic_covariances)
        variances[variances < 0] = 0.
        variables2 = [UncertainVariable(0, 0, sqrt(var)) for var in variances]
        
        # recreate requested variables from independent variables
        values = []
        for n, coefs1, coefs2 in zip(nominal_values, vectors1, vectors2):
            linear_part = dict(zip(variables1, coefs1))
            linear_part.update(dict(zip(variables2, coefs2)))
            values.append(AffineApproximation(n, LinearPart(linear_part)))
        
        return values
    
    __all__.append("correlated_values")