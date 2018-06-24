# -*- coding: utf-8 -*-
"""
For automated handling of units.

@author: d0cod3r
"""

class NumberDict(dict):
    """
    A dict for storing numeric values as values. Can perform mathematical
    operations element-wise.
    A key not present is equivalent to a key with value 0.
    """
    
    def __missing__(self, key):
        return 0
    
    def __setitem__(self, key, value):
        if value == 0:
            del self[key]
        else:
            super(NumberDict, self).__setitem__(key, value)
    
    def __add__(self, other):
        """
        Element-wise addition of another NumberDict
        """
        re = NumberDict(self.copy())
        for key, val in other.items():
            re[key] += val
        return re
    
    def __sub__(self, other):
        re = NumberDict(self.copy())
        for key, val in other.items():
            re[key] -= val
        return re
    
    def __neg__(self):
        """
        Element-wise negation
        """
        re = NumberDict()
        for key, val in self.items():
            re[key] = - val
        return re
    
    def __mul__(self, other):
        """
        Element-wise multiplicaion with a scalar
        """
        re = NumberDict()
        for key, val in self.items():
            re[key] = other * val
        return re
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __div__(self, other):
        re = NumberDict()
        for key, val in self.items():
            re[key] = other / val
        return re
    
    def copy(self):
        return NumberDict(super(NumberDict, self).copy())
    
    # Note: __bool__ returns False if the dict is empty
    

class DimensionError(ValueError):
    """
    Raised if variables do not fullfill the given assumtions, for example when
    adding two values with different dimensions.
    """
    
    def __init__(self, *units):
        """
        Can be given one ore two units.
        Give one unit, if this unit should be dimensionless but is not.
        Give two units, if they should be the same dimension but are not.
        """
        if len(units)==1:
            super(DimensionError, self).__init__("Needed a dimensionless "
                 "quantity, got unit {}".format(units[0]))
        else:
            # Note: units can be 1, do not depend on methods from class Unit
            super(DimensionError, self).__init__("The units {} and {} do not "
                 "have the same dimension, which is necessary in this "
                 "context.".format(units[0], units[1]))
    

class PhysicalQuantity:
    
    # value and unit may change values, but the quantity behind should not be
    # altered
    
    __slots__ = ["_value", "_unit"]
    
    def __init__(self, value, unit=1):
        self._value = value
        if not isinstance(unit, Unit):
            # if the unit is just a number, represent it by a dimensionless
            # unit
            unit = Unit(Representation(NumberDict(), unit))
        self._unit = unit
    
    @property
    def value(self):
        return self._value
    
    @property
    def unit(self):
        return self._unit
    
    @unit.setter
    def unit(self, unit):
        """
        Change the unit. The new unit must have the same dimension.
        The value will be changed, so that the content remains unchaged:
            (old value)*(old unit) = (new value)*(new unit)
        """
        if not self._unit.is_compatible(unit):
            raise DimensionError(self._unit, unit)
        self._value *= self._unit.conversion_factor(unit)
        self._unit = unit
    
    def in_unit(self, unit):
        """
        Returns a copy of this quantity, as a value times the given unit
        """
        # make a copy and use the setter method for the unit
        res = PhysicalQuantity(self._value, self._unit)
        res.unit = unit
        return res
    
    def make_unit(self):
        """
        Let this quantity define a new unit. Returns the new unit as instance
        of the class Unit
        """
        # TODO extract decimal power from self._value
        unit = Unit(Representation(NumberDict({self._unit: 1}), self._value))
        return unit
        
    def __mul__(self, other):
        if isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(self._value * other._value,
                                    self._unit * other._unit)
        elif isinstance(other, Unit):
            return PhysicalQuantity(self._value, self._unit * other)
        else:
            return PhysicalQuantity(self._value * other, self._unit)
    
    def __rmul__(self, other):
        if isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(other._value * self._value,
                                    other._unit * self._unit)
        elif isinstance(other, Unit):
            return PhysicalQuantity(self._value, other * self._unit)
        else:
            return PhysicalQuantity(other * self._value, self._unit)
    
    def __truediv__(self, other):
        if isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(self._value / other._value,
                                    self._unit / other._unit)
        elif isinstance(other, Unit):
            return PhysicalQuantity(self._value, self._unit / other)
        else:
            return PhysicalQuantity(self._value / other, self._unit)
    
    def __rtruediv__(self, other):
        if isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(other._value / self._value,
                                    other._unit / self._unit)
        elif isinstance(other, Unit):
            return PhysicalQuantity(1/self._value, other / self._unit)
        else:
            return PhysicalQuantity(other / self._value, self._unit**(-1))
    
    def __add__(self, other):
        if isinstance(other, Unit):
            raise NotImplementedError("Cannot add a unit. Add 1*unit instead.")
        if isinstance(other, PhysicalQuantity):
            othervalue = other._value * other._unit.conversion_factor(self._unit)
        else:
            othervalue = other / self._unit.conversion_factor(1)
        return PhysicalQuantity(self._value + othervalue, self._unit)
    
    def __radd__(self, other):
        if isinstance(other, Unit):
            raise NotImplementedError("Cannot add a unit. Add 1*unit instead.")
        if isinstance(other, PhysicalQuantity):
            selfvalue = self._value * self._unit.conversion_factor(other._unit)
            othervalue = other._value
            unit = other._unit
        else:
            selfvalue = self._value * self._unit.conversion_factor(1)
            othervalue = other
            unit = 1
        return PhysicalQuantity(othervalue + selfvalue, unit)
    
    def __sub__(self, other):
        if isinstance(other, Unit):
            raise NotImplementedError("Cannot add a unit. Add 1*unit instead.")
        if isinstance(other, PhysicalQuantity):
            othervalue = other._value * other._unit.conversion_factor(self._unit)
        else:
            othervalue = other / self._unit.conversion_factor(1)
        return PhysicalQuantity(self._value - othervalue, self._unit)
    
    def __rsub__(self, other):
        if isinstance(other, Unit):
            raise NotImplementedError("Cannot add a unit. Add 1*unit instead.")
        if isinstance(other, PhysicalQuantity):
            selfvalue = self._value * self._unit.conversion_factor(other._unit)
            othervalue = other._value
            unit = other._unit
        else:
            selfvalue = self._value * self._unit.conversion_factor(1)
            othervalue = other
            unit = 1
        return PhysicalQuantity(othervalue - selfvalue, unit)
    
    def __pow__(self, other):
        if isinstance(other, Unit):
            raise NotImplementedError("Cannot raise to a unit. "
                                      "Use 1*unit instead.")
        elif isinstance(other, PhysicalQuantity):
            other = other._value * other._unit.conversion_factor(1)
        return PhysicalQuantity(self._value**other, self._unit**other)
    
    def __rpow__(self, other):
        exp = self._value * self._unit.conversion_factor(1)
        if isinstance(other, Unit):
            return PhysicalQuantity(1, other**exp)
        elif isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(other._value**exp, other._unit**exp)
        else:
            return PhysicalQuantity(other**exp, 1)
    
    def __pos__(self):
        # make a copy, as all other operators also generate a new instance
        return PhysicalQuantity(self._value, self._unit)
    
    def __neg__(self):
        return PhysicalQuantity(- self._value, self._unit)
    
    def __eq__(self, other):
        return (self - other).value == 0
    
    def __ne__(self, other):
        return not (self == other)
    
    def __lt__(self, other):
        return (self - other).value < 0
    
    def __le__(self, other):
        return (self - other).value <= 0
        
    def __gt__(self, other):
        return (self - other).value > 0
        
    def __ge__(self, other):
        return (self - other).value >= 0
    
    def __abs__(self):
        if self >= 0:
            return +self
        else:
            return -self
    
    # TODO round, floor, ceil
    
    def __bool__(self):
        return self != 0 # using __ne__
    
    # TODO format, str
    
    def __repr__(self):
        return str(self._value)+self._unit.__repr__()
    

class Representation:
    
    __slots__ = ["_units", "_factor", "_dec_pow"]
    
    # To express a unit throught other units. Such a relation is a product of
    # other units, handled as a NumberDict, together with a factor and a
    # decimal power. Should not change at all.
    
    def __init__(self, units, factor=1, dec_pow=0):
        """
        Create a new representation from a product of units, a factor and a
        decimal power.
        The product needs to be given as a NumberDict mapping from factors
        (other units) to their exponents. The dict will be altered!
        """
        # save factor and decimal power
        self._factor = factor
        self._dec_pow = dec_pow
        reduced_units = NumberDict()
        while units:
            # take one factor off the stack
            unit, exp = units.popitem()
            if unit.is_named():
                # add named units to the reduced form
                reduced_units[unit] += exp
            else:
                # units without name are taken apart
                repres = unit.get_representation()
                # Note: *exp creates a copy, which is allowed to be changed
                units += repres._units * exp
                self._factor *= repres._factor**exp
                self._dec_pow += repres._dec_pow * exp
        self._units = reduced_units
    
    def in_base_units(self):
        """
        Returns a reduced representation that only links to base units (units
        that do not have a representation through other units).
        """
        # if two quantities with the same unit are added, this method will be
        # called with an empty self._units. As this is normally the only case
        # that occours in large numbers, optimize:
        if not self._units:
            return self
        factor = 1
        dec_pow = 0
        unit_stack = self._units.copy()
        reduced_units = NumberDict()
        while unit_stack:
            # take one factor off the stack
            unit, exp = unit_stack.popitem()
            if unit.is_base():
                # add base units to the reduced form
                reduced_units[unit] += exp
            else:
                # other units are taken apart
                repres = unit.get_representation()
                unit_stack += repres._units * exp
                factor *= repres._factor**exp
                dec_pow += repres._dec_pow * exp
        return Representation(reduced_units, factor, dec_pow)
    

class Unit:
    """
    TODO doc
    Multiplying with and dividing throught another unit forms a new unit, as
    well as raising to a power which is not a PhysicalQuantity.
    Every operation with a PhysicalQuantity will form another quantity.
    """
    
    __slots__ = ["_token", "_repr"]
    
    # A Unit consists of a token (short name) and one or more representations.
    # The token can be None for Units generated in multiplications / ... or a
    # string for known Units.
    # A Unit may have a representation throught other units.
    # The representation can be None, for the used base units that are the
    # used base units.
    
    def __init__(self, *args):
        """
        Can be given a token and / or a representation
        """
        if len(args) == 1:
            if isinstance(args[0], str):
                self._token = args[0]
                self._repr = None
            elif isinstance(args[0], Representation):
                self._token = None
                self._repr = args[0]
        else:
            if isinstance(args[0], str):
                self._token = args[0]
                self._repr = args[1]
            elif isinstance(args[0], Representation):
                self._token = args[1]
                self._repr = args[0]
    
    # TODO optimization: (?) save additional reduced representation for faster
    # unit comparison
    
    def set_name(self, name):
        """
        Give this unit an own name.
        """
        self._token = name
        return self
    
    def is_named(self):
        """
        Returns whether this Unit was given a name.
        If False, a name for this Unit can still be calculated.
        """
        return self._token is not None
    
    def is_base(self):
        """
        Returns whether is Unit is a base unit, wheter it has no representation
        throught other units.
        """
        return self._repr is None
    
    def get_representation(self):
        """
        Returns a representation of this unit.
        Base units are represented through themself.
        """
        if self._repr is not None:
            return self._repr
        else:
            return Representation(NumberDict({self: 1}))
    
    def is_compatible(self, other):
        """
        Returns whether this unit and another are compatible, whether they
        have the same dimension. Other can be a scalar to test if the unit is
        dimensionless.
        """
        try:
            self.conversion_factor(other)
        except DimensionError:
            return False
        return True
                
    
    def conversion_factor(self, other):
        """
        Returns the conversion factor for two compatible units, self and other,
        so that self = factor * other.
        Raises a DimensionError if the units are not compatible.
        """
        if isinstance(other, Unit):
            repres = (self / other)._repr.in_base_units()
            if (repres.in_base_units()._units):
                raise DimensionError(self, other)
            return repres._factor * 10**(repres._dec_pow)
        else:
            repres = self._repr.in_base_units()
            if (repres.in_base_units()._units):
                raise DimensionError(self, other)
            return repres._factor * 10**(repres._dec_pow) / other
    
    def make_unit(self):
        """
        Returns self. This method is present in class PhysicalQuantity and
        added here for an easy way to make sure your calculation defined a
        Unit and not a PhysicalQuantity.
        """
        return self
    
    # Note: In the following methdos, product is created from two NumberDicts
    # instead of a dict containing both, as this allows other to be self
    
    def __mul__(self, other):
        if isinstance(other, Unit):
            product = NumberDict({self: 1}) + NumberDict({other: 1})
            return Unit(Representation(product))
        else:
            return PhysicalQuantity(1, self) * other
    
    def __rmul__(self, other):
        if isinstance(other, Unit):
            product = NumberDict({other: 1}) + NumberDict({self: 1})
            return Unit(Representation(product))
        else:
            return other * PhysicalQuantity(1, self)
    
    def __truediv__(self, other):
        if isinstance(other, Unit):
            product = NumberDict({self: 1}) - NumberDict({other: 1})
            return Unit(Representation(product))
        else:
            return PhysicalQuantity(1, self) / other
    
    def __rtruediv__(self, other):
        if isinstance(other, Unit):
            product = NumberDict({other: 1}) - NumberDict({self: 1})
            return Unit(Representation(product))
        else:
            return other / PhysicalQuantity(1, self)
    
    def __pow__(self, other):
        if isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(1, self) ** other
        return Unit(Representation(NumberDict({self: 1}) * other))
    
    # TODO __format__, __str__
    
    def __repr__(self):
        if self._token:
            return self._token
        else: # TODO better
            rep = self._repr
            units, factor, dec_pow = rep._units, rep._factor, rep._dec_pow
            res = ""
            if factor != 1:
                res += "*"+str(factor)
            if dec_pow != 0:
                res += "*10^("+str(dec_pow)+")"
            for unit, exp in units.items():
                if exp > 0:
                    res += "*"
                else:
                    res += "/"
                res += unit._token+"^"+str(abs(exp))
            return res
    

#==============================================================================
# DEBUGGING
#==============================================================================

m = Unit("m")
s = Unit("s")
kg = Unit("kg")

N = kg*m/s**2
N.set_name("N")

g = 9.81 *N/kg
t = 2*s
l = g*t**2