# -*- coding: utf-8 -*-

"""
 TODO documentation
 
 @author: d0cod3r
"""


# The idea behind this module is the fact that every quantity can be used as a
# unit again.


class NumberDict(dict):
    """
    A dict for numeric values, supporting addition, substaction and
    multiplication. The value to a key not present is 0.
    
    The keys can be arbitary objects, the values have to be numbers.
    
    The sum of two dictionarys is a dictionary again, where the value to each
    key is the sum of the values to this key from the two inputs.
    The difference of two dictionaries works equally, but with negative values
    in the second argument.
    A dict can be multiplied with a scalar factor, so that this
    operation will be performed on each element.
    """
    
    def __missing__(self, key):
        return 0
    
    def __add__(self, other):
        res = NumberDict(self.copy())
        for key in iter(other):
            res[key] += other[key]
            if res[key] == 0:
                del res[key]
        return res
    
    def __sub__(self, other):
        res = NumberDict(self.copy())
        for key in iter(other):
            res[key] -= other[key]
            if res[key] == 0:
                del res[key]
        return res
    
    def __mul__(self, other):
        res = NumberDict(self.copy())
        for key in iter(self):
            res[key] = other * self[key]
        return res
        
    def __neg__(self):
        res = NumberDict(self.copy())
        for key in iter(self):
            res[key] = - self[key]
        return res


class PhysicalQuantity:
    """
    A physical quantity consists of a value and a unit.
    
    This class represents a physical quantity by storing a value, a compositum
    of units and a decimal power.
    
    The value should be a float or similar.
    The unit is represented as a product of other units, precisely as a
    NumberDict mapping from underlying units to exponents. Base units can be
    defined using UnitQuantity.
    The decimal power should be an int.
    """
    
    # faster acces and less storage consumption
    __slots__ = ("_value", "_components", "_dec_pow")
    
    def __init__(self, value, unit, decimal_power=0):
        """
        value -- a float or similar
        unit -- Has to be a NumberDict. For dimensionless units, the dict
        may be empty, for base units it should contain {self: 1}
        decimal_power -- an optional decimal power to the value. Should be int
        """
        self._value = value
        self._components = unit
        self._dec_pow = decimal_power
    
#    # iterative attempt, not considering factors
#    def reduced(self):
#        base_components = NumberDict()
#        stack = [(self, 1)]
#        while len(stack) > 0:
#            quantity, exp = stack.pop()
#            # if the quantity has no components, it is a base component
#            if quantity._components is None:
#                base_components[quantity] += exp
#            # every other quantity is taken apart and added back to the stack
#            else:
#                for (quantity2, exp2) in quantity._components.items():
#                    stack.append((quantity2, exp*exp2))
#        return PhysicalQuantity(self._value, base_components, self._dec_pow)
    
    def reduced(self):
        base_components = NumberDict()
        value = self._value
        dec_pow = self._dec_pow
        for component, exp in self._components.items():
            reduced_component = component.reduced()
            value *= reduced_component._value ** exp
            dec_pow += reduced_component._dec_pow + exp
            base_components = base_components + exp * reduced_component._components
        return PhysicalQuantity(value, base_components, dec_pow)
    
    def __repr__(self):
        #TODO better
        unitstr = ""
        for unit, exp in self._components.items():
            unitstr += unit.__repr__()+"^"+str(exp)+" "
        return "{:}e{:+} ".format(self._value, self._dec_pow) + unitstr
    
    def __mul__(self, other):
        if isinstance(other, UnitQuantity):
            val = self._value
            comps = NumberDict({other: 1}) + self._components
            dec_pow = self._dec_pow
        elif isinstance(other, PhysicalQuantity):
            val = self._value * other._value
            comps = self._components + other._components
            dec_pow = self._dec_pow + other._dec_pow
        else:
            val = self._value * other
            comps = self._components
            dec_pow = self._dec_pow
        return PhysicalQuantity(val, comps, dec_pow)
    
    def __rmul__(self, other):
        if isinstance(other, UnitQuantity):
            val = self._value
            comps = NumberDict({other: 1}) + self._components
            dec_pow = self._dec_pow
        elif isinstance(other, PhysicalQuantity):
            val = self._value * other._value
            comps = self._components + other._components
            dec_pow = self._dec_pow + other._dec_pow
        else:
            val = self._value * other
            comps = self._components
            dec_pow = self._dec_pow
        return PhysicalQuantity(val, comps, dec_pow)
    
    def __truediv__(self, other):
        if isinstance(other, UnitQuantity):
            val = self._value
            comps =  self._components - NumberDict({other: 1})
            dec_pow = self._dec_pow
        elif isinstance(other, PhysicalQuantity):
            val = self._value / other._value
            comps = self._components - other._components
            dec_pow = self._dec_pow - other._dec_pow
        else:
            val = self._value / other
            comps = self._components
            dec_pow = self._dec_pow
        return PhysicalQuantity(val, comps, dec_pow)
    
    def __rtruediv__(self, other):
        if isinstance(other, UnitQuantity):
            val = 1 / self._value
            comps =  NumberDict({other: 1}) - self._components
            dec_pow = - self._dec_pow
        elif isinstance(other, PhysicalQuantity):
            val = other._value / self._value
            comps = other._components - self._components
            dec_pow = other._dec_pow - self._dec_pow
        else:
            val = other / self._value
            comps = - self._components
            dec_pow = - self._dec_pow
        return PhysicalQuantity(val, comps, dec_pow)

class UnitQuantity(PhysicalQuantity):
    """
    TODO doc
    """
    
    __slots__=["_token", "_name", "_latex", "_expressions"]
    
    def __init__(self, quantity, token, name=""):
        """
        Define a new unit.
        A unit can be a composite of existing units or a new, independent one.
        For the first case, a PhysicalQuantity can be passed, which properties
        are copied.
        For the second case, quantity may be None.
        """
        if quantity is None:
            self._components = NumberDict({self: 1})
            self._value = 1
            self._dec_pow = 0
        else:
            args = (quantity._value, quantity._components, quantity._dec_pow)
            super(UnitQuantity, self).__init__(*args)
        self._token = token
        self._name = name
    
    def reduced(self):
        # as a UnitQuantity has a name, do not create a copy
        if self._components == NumberDict({self: 1}):
            return self
        return super(UnitQuantity, self).reduced()
    
    def __repr__(self):
        return self._token # TODO better
    
    def __mul__(self, other):
        if isinstance(other, UnitQuantity):
            # both units, save as it is
            components = NumberDict({self: 1, other: 1})
            return PhysicalQuantity(1, components)
        elif isinstance(other, PhysicalQuantity):
            val = other._value
            components = NumberDict({self: 1}) + other._components
            dec_pow = other._dec_pow
        else:
            val = other
            comps = NumberDict({self: 1})
            dec_pow = self._dec_pow
        return PhysicalQuantity(val, comps, dec_pow)
    
    def __rmul__(self, other):
        if isinstance(other, PhysicalQuantity):
            comps = other._components + NumberDict({self: 1})
            return PhysicalQuantity(other._value, comps, other._dec_pow)
        else:
            return PhysicalQuantity(other, NumberDict({self: 1}))
    
    def __truediv__(self, other):
        if isinstance(other, UnitQuantity):
            val = 1
            comps =  NumberDict({self: 1, other: -1})
            dec_pow = 0
        elif isinstance(other, PhysicalQuantity):
            val = 1 / other._value
            comps = NumberDict({self: 1}) - other._components
            dec_pow = - other._dec_pow
        else:
            val = 1 / other
            comps = NumberDict({self: 1})
            dec_pow = 0
        return PhysicalQuantity(val, comps, dec_pow)
    
    def __rtruediv__(self, other):
        if isinstance(other, PhysicalQuantity):
            val = other._value
            comps = other._components - NumberDict({self: 1})
            return PhysicalQuantity(val, comps, - self._dec_pow)
        else:
            return PhysicalQuantity(other, NumberDict({self: -1}))        

#==============================================================================
# DEBUGGING
#==============================================================================
m  = UnitQuantity(None, "m")
kg = UnitQuantity(None, "kg")
s  = UnitQuantity(None, "s")
N  = UnitQuantity( kg*m/s/s, "N")

J = N*m
J2 = J.reduced()