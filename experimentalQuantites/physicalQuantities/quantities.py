# -*- coding: utf-8 -*-
"""
For automated handling of units.

TODO doc

!!! Important !!! Comparing quantities checks whether the units are compatible.
Comparing two quantites with different dimensions will not return False but
raise an exception.

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
        # putting this in else might cause a key error
        super(NumberDict, self).__setitem__(key, value)
        if value == 0:
            del self[key]
    
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
    
    def __truediv__(self, other):
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
    
    def __init__(self, unit1, unit2):
        """
        Takes two units. Gives an error message naming both units and stating
        that they have different dimensions, which is wrong in this context.
        """
        # As the representation of UNITONE is just an empty string, which
        # will probably be confusing, test for this case. Testing identity
        # will not raise an exception, different from equality.
        if unit1 is UNITONE:
            super(DimensionError, self).__init__("Needed a dimensionless "
                 "quantity, got unit {}".format(unit2))
        elif unit2 is UNITONE:
            super(DimensionError, self).__init__("Needed a dimensionless "
                 "quantity, got unit {}".format(unit1))
        else:
            super(DimensionError, self).__init__("The units {} and {} do not "
                 "have the same dimension, which is necessary in this "
                 "context.".format(unit1, unit2))


class PhysicalQuantity:
    """
    In Physics, a quantity is a numeric value with a unit.
    This class describes such a physical quantity. You can perform the usual
    actions with them, such as addition, multiplication and powers. The units
    will be calculated automaticly and an exceptin will be raised if there is
    a dimension error.
    Value and unit can be accessed, the variable can be converted to another
    unit.
    """
    
    # value must be a float like scalar, unit must be an instance of class
    # Unit. Both must not be changed.
    
    __slots__ = ["_value", "_unit"]
    
    def __init__(self, value, unit=1):
        """
        Must be given a value, float like.
        Second argument is the unit. It is optional, but has to be an instance
        of class Unit.
        Creates a PhysicalQuantity representing value*unit
        
        (Instead of an instance of class Unit, the second argument can be a
        float, which will be replaced by a dimensionless unit.)
        """
        self._value = value
        if not isinstance(unit, Unit):
            # if the unit is just a number, represent it by a dimensionless
            # unit
            unit = unit * UNITONE
        self._unit = unit
    
    @property
    def value(self):
        """
        The numeric value of this quantity to the unit of it.
        Float like, without the unit.
        """
        return self._value
    
    @property
    def unit(self):
        """
        The unit of this quantity, an instance of class Unit.
        """
        return self._unit
    
    def in_unit(self, unit):
        """
        Returns a quantity representing the same content, but as a value times
        the given unit.
        """
        value = self._value * self._unit.conversion_factor(unit)
        res = PhysicalQuantity(value, unit)
        return res
    
    # TODO in_base_units
    
    # Multiplication and division are overwritten in class Unit, so that for
    # an operation on two Units is again a Unit. Thus, the second argument to
    # PhysicalQuantity() called below should always be a Unit.
    # The constant UNITONE represents a dimensionless 1 as a Unit.
    
    def __mul__(self, other):
        if isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(self._value * other._value,
                                    self._unit * other._unit)
        else:
            return PhysicalQuantity(self._value * other, self._unit)
    
    def __rmul__(self, other):
        if isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(self._value * other._value,
                                    self._unit * other._unit)
        else:
            return PhysicalQuantity(self._value * other, self._unit)
    
    def __truediv__(self, other):
        if isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(self._value / other._value,
                                    self._unit / other._unit)
        else:
            return PhysicalQuantity(self._value / other, self._unit)
    
    def __rtruediv__(self, other):
        if isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(other._value / self._value,
                                    other._unit / self._unit)
        else:
            return PhysicalQuantity(other / self._value,
                                    UNITONE / self._unit)
    
    # For addition and substraction, the right variable will be converted to
    # the unit of the left, which will be the unit of the result.
    
    def __add__(self, other):
        if isinstance(other, PhysicalQuantity):
            othervalue = other._value * other._unit.conversion_factor(self._unit)
        else:
            othervalue = other * UNITONE.conversion_factor(self._unit)
        return PhysicalQuantity(self._value + othervalue, self._unit)
    
    def __radd__(self, other):
        if isinstance(other, PhysicalQuantity):
            selfvalue = self._value * self._unit.conversion_factor(other._unit)
            othervalue = other._value
            unit = other._unit
        else:
            selfvalue = self._value * self._unit.conversion_factor(UNITONE)
            othervalue = other
            unit = UNITONE
        return PhysicalQuantity(othervalue + selfvalue, unit)
    
    def __sub__(self, other):
        if isinstance(other, PhysicalQuantity):
            othervalue = other._value * other._unit.conversion_factor(self._unit)
        else:
            othervalue = other * UNITONE.conversion_factor(self._unit)
        return PhysicalQuantity(self._value - othervalue, self._unit)
    
    def __rsub__(self, other):
        if isinstance(other, PhysicalQuantity):
            selfvalue = self._value * self._unit.conversion_factor(other._unit)
            othervalue = other._value
            unit = other._unit
        else:
            selfvalue = self._value * self._unit.conversion_factor(UNITONE)
            othervalue = other
            unit = UNITONE
        return PhysicalQuantity(othervalue - selfvalue, unit)
    
    def __pow__(self, other):
        if isinstance(other, PhysicalQuantity):
            other = other._value * other._unit.conversion_factor(UNITONE)
        return PhysicalQuantity(self._value**other, self._unit**other)
    
    def __rpow__(self, other):
        exp = self._value * self._unit.conversion_factor(UNITONE)
        if isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(other._value**exp, other._unit**exp)
        else:
            return PhysicalQuantity(other**exp, UNITONE)
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        return PhysicalQuantity(- self._value, self._unit)
    
    def __eq__(self, other):
        # __sub__ checks the units, so an exception is raised for non
        # compatible units.
        return (self - other).value == 0
    
    def __ne__(self, other):
        return not (self == other)
    
    # TODO all units are assumed >0, should better be only base units
    def __lt__(self, other):
        return (self - other).value < 0
    
    def __le__(self, other):
        return (self - other).value <= 0
        
    def __gt__(self, other):
        return (self - other).value > 0
        
    def __ge__(self, other):
        return (self - other).value >= 0
    
    def __abs__(self):
        if self._value >= 0:
            return +self
        else:
            return -self
    
    # TODO round, floor, ceil
    
    def __bool__(self):
        # assume all units != 0, other cases are possible, but do not make
        # sense
        return self._value != 0
    
    # TODO format, str
    
    def __repr__(self):
        return str(self._value)+self._unit.__repr__()


class Representation:
    
    # To express a unit throught other units. Such a relation is a product of
    # other units, handled as a NumberDict, together with a factor and a
    # decimal power. Should not change at all.
    
    __slots__ = ["_units", "_factor", "_dec_pow"]
    
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
        # If two quantities with the same unit are added, this method will be
        # called with an empty self._units. As this is normally the only case
        # that occours in large numbers, optimize:
        if not self._units:
            return self
        factor = self._factor
        dec_pow = self._dec_pow
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


class Unit( PhysicalQuantity ):
    """
    A unit is eqivalent to a quantity with value 1 and that unit as unit.
    Therefor, in this skript, a unit is always also a quantity.
    Apart from this, a unit is generally a predefined quantity for comparison.
    This can be defined by other units or in a more complex way. In this
    skript, a unit can have a name or a representation through other units, or
    both.
    A unit with only a name defines a new dimension.
    Units with only representations are created by mathematic operations on
    units. If needed, a name will be calculated from the representation.
    Multiplying with and dividing throught another unit forms a new unit, as
    well as raising to a power.
    Every operation will return a PhysicalQuantity.
    """
    
    __slots__ = ["_name", "_repr"]
    
    # A Unit is a PhysicalQuantity expanded by a name and a representation
    # throught other Units. One of them may be None, but never both.
    # The name can be None for Units generated in multiplications / ... or a
    # string for known Units.
    # A Unit may have a representation through other units.
    # The representation can be None, for the used base units that are the
    # used base units. Otherwise it must be an instance of Representation.
    
    def __init__(self, *args):
        """
        Can be given a name and / or a representation
        """
        super(Unit, self).__init__(1, self)
        if len(args) == 1:
            if isinstance(args[0], str):
                self._name = args[0]
                self._repr = None
            elif isinstance(args[0], Representation):
                self._name = None
                self._repr = args[0]
        else:
            if isinstance(args[0], str):
                self._name = args[0]
                self._repr = args[1]
            elif isinstance(args[0], Representation):
                self._name = args[1]
                self._repr = args[0]
    
    def __hash__(self):
        """
        Units need to be hashable as they are used as keys in a NumberDict to
        store a Representation. For this purpose, the hash values of two
        eqivalent units may differ.
        """
        return id(self)
    
    def set_name(self, name):
        """
        Give this unit an own name.
        Returns self.
        """
        self._name = name
        return self
    
    def is_named(self):
        """
        Returns whether this Unit was given a name.
        If False, a name for this Unit can still be calculated.
        """
        return self._name is not None
    
    def is_base(self):
        """
        Returns whether this Unit is a base unit, whether it has no
        representation throught other units.
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
        repres = (self / other)._repr.in_base_units()
        if (repres.in_base_units()._units):
            raise DimensionError(self, other)
        return repres._factor * 10**(repres._dec_pow)
    
    # If two units are multiplied or divided or a unit is raised to a power,
    # the result must be a unit again. These methods overwrite those from
    # PhysicalQuantity to cover this case. Every other case will be redirected
    # and handled appropriately there, as every unit is also a quantity of
    # 1*unit.
    
    def __mul__(self, other):
        if isinstance(other, Unit):
            product = NumberDict({self: 1}) + NumberDict({other: 1})
            return Unit(Representation(product))
        else:
            return super(Unit, self).__mul__(other)
    
    def __rmul__(self, other):
        if isinstance(other, Unit):
            product = NumberDict({other: 1}) + NumberDict({self: 1})
            return Unit(Representation(product))
        else:
            return super(Unit, self).__mul__(other)
    
    def __truediv__(self, other):
        if isinstance(other, Unit):
            product = NumberDict({self: 1}) - NumberDict({other: 1})
            return Unit(Representation(product))
        else:
            return super(Unit, self).__truediv__(other)
    
    def __rtruediv__(self, other):
        if isinstance(other, Unit):
            product = NumberDict({other: 1}) - NumberDict({self: 1})
            return Unit(Representation(product))
        else:
            return super(Unit, self).__rtruediv__(other)
    
    def __pow__(self, other):
        if isinstance(other, PhysicalQuantity):
            other = other._value * other._unit.conversion_factor(UNITONE)
        return Unit(Representation(NumberDict({self: 1}) * other))
    
    # TODO __format__, __str__
    
    def __repr__(self):
        if self._name:
            return self._name
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
                res += unit._name+"^"+str(abs(exp))
            return res


# This constant is used whenever contentual a simple 1 is needed, but for the
# skript it needs to be an instance of Unit.
UNITONE = Unit(Representation(NumberDict()), "")


def make_unit(quantity, name=None):
    """
    Let the given quantity define a new unit. Returns the new unit as instance
    of the class Unit.
    Optional, as a second argument, a name can be given. Has to be a string.
    """
    if isinstance(quantity, Unit):
        return quantity
    # TODO extract decimal power from self._value
    unit = Unit(Representation(NumberDict({quantity._unit: 1}),
                               quantity._value))
    if name is not None:
        unit.set_name(name)
    return unit



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
    


