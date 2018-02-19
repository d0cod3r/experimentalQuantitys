# -*- coding: utf-8 -*-

"""
 TODO documentation
 
 @author: d0cod3r
"""


# TODO how it works


import math
import collections


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
        # This method is more efficient in large calculations with only one
        # result, which is the more typically case. For example, large sums
        # have linear runtime with this, quadratic runtime with the recursive
        # method
        
        # new linear combination, start with an empty dict
        new_linear_combo = collections.defaultdict(float)
        
        # disasseble the list
        while self._linear_combo:
            
            # extract one list element
            (main_factor, main_linear_part) = self._linear_combo.pop()
            
            if main_linear_part.is_expanded():
                for (variable, factor) in main_linear_part._linear_combo.iteritems():
                    
                    # adjust derivative
                    new_linear_combo[variable] += main_factor*factor
            
            else: # non expanded form
                for (factor, linear_part) in main_linear_part._linear_combo:
                    
                    # add all elements with combined factor
                    self._linear_combo.append((main_factor*factor, linear_part))
            
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
    slots = ("_nominal_value", "_linear_part")
    
    def __init__(self, nominal_value, linear_part):
        """
        Initialises an AffineApproximation.
        
        nominal_value -- value of the approximation when the linear part
        is zero.
        
        linear_part -- a LinearPart describing the linear approximation
        of a calculation around the nominal value.
        """
        
        # Converting to a float.
        # If nominal_value can not be converted to float, it does not
        # make sense to be used here.
        self._nominal_value = float(nominal_value)
        
        # The linear part will only be expanded if needed. This should
        # make calculations faster. See LinearPart for details.
        self._linear_part = linear_part
    
    @property
    def nominal_value(self):
        """
        Nominal value of this uncertain value.
        """
        return self._nominal_value
    
    # Abbrevation to make formulars shorter
    n = nominal_value
    
    # TODO def derivatives(self):
    
    # TODO def error_components(self, type=None):
    
    # TODO @property def statistical_standard_deviation(self):
    # stat_std_dev = statistical_standard_deviation
    # stat = statistical_standard_deviation
    
    # TODO @property def systematical_standard_deviation(self):
    # sys_std_dev = statistical_standard_deviation
    # sys = statistical_standard_deviation
    
    # TODO significant_digits(self)
    
    # TODO __repr__, __str__, __format__
    
    # TODO eq, neq, lt, gt, ...
    
    # TODO add, sub, mult, div, pow, ...


class UncertainVariable(AffineApproximation):
    """
    Represents a number with a statistical deviations and a systematical
    uncertainty.
    Diffrent from AffineApproximation, it represents an independet value,
    while AffineApproximations can have correlations. In return, an
    UncertainVariable stores its statistical and systematical standard
    deviation.
    """
    
    # TODO overwrite changed functions


def to_uncertain_value(x):
    pass # TODO

def nominal_value(x):
    """
    Return the nominal value of x if it is an uncertain value as
    defined in this module.
    Otherwise it returns x unchanged.

    This can be usefull to groups of numbers, where only some have
    an uncertaincy while others are just floats.
    """

    if isinstance(x, AffineApproximation):
        return x.nominal_value
    else:
        return x

def statistical_standart_deviation(x, default=0.0):
    """
    Return the statistical standard deviation of x if it is an uncertain
    value as defined in this module.
    Otherwise it will return default, which is default to 0.

    This can be usefull to groups of numbers, where only some have
    an uncertaincy while others are just floats.
    """

    if isinstance(x, AffineApproximation):
        return x.stat_std_dev
    else:
        return default

def systematical_standart_deviation(x, default=0.0):
    """
    Return the systematical standard deviation of x if it is an uncertain
    value as defined in this module.
    Otherwise it will return default, which is default to 0.

    This can be usefull to groups of numbers, where only some have
    an uncertaincy while others are just floats.
    """

    if isinstance(x, AffineApproximation):
        return x.sys_std_dev
    else:
        return default

# TODO def covariance_matrix(numbers)

# TODO wrapper

try:
    import numpy
except ImportError:
    pass
else:
    
    def correlated_values(nominal_values, statistic_covariances, \
                          systematic_covariances, tag=None):
        """
        
        """
        
        if tag is None:
            tag = [None for i in nominal_values]
        
        #TODO as below
        # diagonalise both
        # create independent variables holding the statistic uncertaincy
        #   and ones holding the systematic uncertaincy
        # recreate the original variables as AffineApproximations to both
        #   groups of independent variables
    
    # TODO other numpy depencies


# TODO wrap external functions