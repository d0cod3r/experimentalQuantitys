# -*- coding: utf-8 -*-
"""
For automated handling of units.

See init file for explanations.

@author: d0cod3r
"""

# Values with units are represented by the class PhysicalQuantity, which
# consists of a float-like value and a unit, which has to be an instance of
# class Unit. Calculations here a pretty much straight forward.
# A unit can have a name and / or a representation through other units. A unit
# without a representation is considered a base unit and must have a name.
# Each base unit introduces a dimension.
# Calculations with units can be performed by building new units with according
# representations through the arguments units or by converting units into
# other using their representation.
# A representation consists of a float-like factor and other units with their
# poweres, which are stored in a dict optimized for numeric values.


from math import floor, ceil

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
            unit = Unit(Representation(NumberDict(), unit))
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
        return PhysicalQuantity(value, unit)
    
    def in_base_units(self):
        """
        Returns a quantity representing the same content, but as a unit
        directly composed from base units.
        """
        repres = self._unit.get_base_unit_representation()
        # We want the new unit without a factor, so just set it to one. As this
        # only alters the unit, in_unit will still work correctly.
        repres._factor = 1
        return self.in_unit(Unit(repres))
    
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
    
    def __round__(self, ndigits=0):
        return PhysicalQuantity(round(self._value, ndigits), self._unit)
    
    def __floor__(self):
        return PhysicalQuantity(floor(self._value), self._unit)
    
    def __ceil__(self):
        return PhysicalQuantity(ceil(self._value), self._unit)
        
    def __bool__(self):
        # assume all units != 0, other cases are possible, but do not make
        # sense
        return self._value != 0
    
    def __float__(self):
        return self.in_unit(UNITONE)._value
    
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
        self._units = units
        self._factor = factor
        self._dec_pow = dec_pow
    
    def copy(self):
        """
        Returns a copy. A new NumberDict for the units will be created, as it
        is altered in some methods.
        """
        return Representation(self._units.copy(), self._factor, self._dec_pow)
    
    def reduce_to_named(self):
        """
        Reduces the representation to units that are named. Units in this
        representation that are not named are taken apart by using their
        representations.
        Returns self.
        """
        reduced_units = NumberDict()
        while self._units:
            # take one factor off the stack
            unit, exp = self._units.popitem()
            if unit.is_named():
                # add named units to the reduced form
                reduced_units[unit] += exp
            else:
                # units without name are taken apart
                repres = unit.get_representation()
                # Note: *exp creates a copy, which is allowed to be changed
                self._units += repres._units * exp
                self._factor *= repres._factor**exp
                self._dec_pow += repres._dec_pow * exp
        self._units = reduced_units
        return self
    
    def reduce_to_base(self):
        """
        Reduces the representation to base units (units that do not have a
        representation through other units). Units in this representation that
        are not base units are taken apart by using their representations.
        Returns self.
        """
        # If two quantities with the same unit are added, this method will be
        # called with an empty self._units. As this is normally the only case
        # that occours in large numbers, optimize:
        if not self._units:
            return self
        reduced_units = NumberDict()
        while self._units:
            # take one factor off the stack
            unit, exp = self._units.popitem()
            if unit.is_base():
                # add base units to the reduced form
                reduced_units[unit] += exp
            else:
                # other units are taken apart
                repres = unit.get_representation()
                self._units += repres._units * exp
                self._factor *= repres._factor**exp
                self._dec_pow += repres._dec_pow * exp
        self._units = reduced_units
        return self


# A unit should have a name, a short symbol, sometimes a different latex
# representation and sometimes a documentation. Sometimes all of them are
# given, sometimes defaults are used.

class FullName:
    """
    Store a name, a (one or two charakter) symbol, latex representation and
    a documentation for a unit.
    """
    
    __slots__ = ["_name", "_symbol", "_latex", "_doc"]
    
    def __init__(self, name, symbol, latex, doc=""):
        self._name = name
        self._symbol = symbol
        self._latex = latex
        self._doc = doc
    
    @property
    def name(self):
        return self._name
    
    @property
    def symbol(self):
        return self._symbol
    
    @property
    def latex(self):
        return self._latex
    
    @property
    def doc(self):
        return self._doc


class SimpleName:
    """
    Stores only symbol and uses it in every context.
    """
    
    __slots__ = [ "_symbol"]
    
    def __init__(self, symbol):
        self._symbol = symbol
    
    @property
    def name(self):
        return self._symbol
    
    @property
    def symbol(self):
        return self._symbol
    
    @property
    def latex(self):
        return self._symbol
    
    @property
    def doc(self):
        return "%s (no documentation available)" % self._symbol


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
    
    def __init__(self, representation=None, name=None):
        super(Unit, self).__init__(1, self)
        self._repr = representation
        self._name = name
    
    def __hash__(self):
        """
        Units need to be hashable as they are used as keys in a NumberDict to
        store a Representation. For this purpose, the hash values of two
        eqivalent units may differ.
        """
        return id(self)
    
    # TODO better getter and setter, as name is now a class
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
    
    def get_base_unit_representation(self):
        """
        Returns a representation of this unit that contains only base units.
        """
        return self.get_representation().copy().reduce_to_base()
    
    def is_compatible(self, other):
        """
        Returns whether this unit and another are compatible, whether they
        have the same dimension.
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
        repres = (self / other)._repr.reduce_to_base()
        if (repres._units):
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
            return self._name.symbol
        else: # TODO better
            rep = self._repr.reduce_to_named()
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
                res += unit._name.symbol
                if exp != 1:
                    res += "^"+str(abs(exp))
            return res


# This constant is used whenever contentual a simple 1 is needed, but for the
# skript it needs to be an instance of Unit.
UNITONE = Unit(Representation(NumberDict()), None)


def to_quantity(x):
    """
    Returns x if x is a physical quantity. Returns a pyhsical quantity with
    value x and a dimensionless unit otherwise.
    """
    if isinstance(x, PhysicalQuantity):
        return x
    else:
        return PhysicalQuantity(x, UNITONE)

def in_unit(x, unit):
    """
    Returns x as a physical quantity with given unit.
    Other than x.in_unit(unit), this works also if x is a float-like and unit
    is dimensionless.
    This does not work for a float and a not dimensionless unit, it is not
    x*unit, but rather x converted to unit.
    """
    if isinstance(x, PhysicalQuantity):
        return x.in_unit(unit)
    else:
        return x / unit.conversion_factor(UNITONE) * unit

def is_compatible(x, y):
    """
    Returns whether the two quantites are compatible, whether they have the
    same dimension. Both can be a scalars, in which case this method will
    return true if the other unit is dimensionless.
    """
    if isinstance(x, PhysicalQuantity) and isinstance(y, PhysicalQuantity):
        return x._unit.is_compatible(y)
    elif isinstance(x, PhysicalQuantity):
        return x._unit.is_compatible(UNITONE)
    elif isinstance(y, PhysicalQuantity):
        return y._unit.is_compatible(UNITONE)
    else:
        return True


def userUnit(*args, **kwargs):
    """
    Create a new unit. Can be given a quantity, a name, a symbol, latex code
    and documentation or parts of that.
    If given without keywords, please use the order as above.
    If using keyword arguments, please use name, symbol, latex and doc as
    keywords and give the quantity as first, nameless argument.
    """
    quantity, name, symbol, latex, doc = None, None, None, None, ""
    if len(args) > 0 and isinstance(args[0], PhysicalQuantity):
        quantity = args[0]
        args = args[1:]
    if len(args) > 0:
        symbol = args[0]
    if len(args) > 1:
        name = args[1]
        if len(symbol) > len(name):
            name, symbol = symbol, name
    if len(args) > 2:
        latex = args[2]
    if len(args) > 3:
        doc = args[3]
    if "name" in kwargs.keys():
        name = kwargs["name"]
    if "symbol" in kwargs.keys():
        symbol = kwargs["symbol"]
    if "latex" in kwargs.keys():
        latex = kwargs["latex"]
    if "doc" in kwargs.keys():
        doc = kwargs["doc"]
    
    repres, uname = None, None
    if quantity is not None:
        repres = Representation(NumberDict({quantity._unit: 1}),
                                quantity._value)
    if name and symbol:
        if latex is None:
            latex = symbol
        uname = FullName(name, symbol, latex, doc)
    elif symbol:
        uname = SimpleName(symbol)
    elif not (name or symbol or latex):
        uname = None
    else:
        # TODO every possibility
        raise NotImplementedError("Sorry, I haven't implementet everything "
                                  "here. Try giving more detail.")
    return Unit(repres, uname)


def wrap(function, result_unit, arg_units, kw_arg_units={}):
    """
    Wraps a function to support quantities as arguments.
    First argument is the function to wrap.
    Second argument is the unit of the result. Can be None if the result
    should not be converted, i.e. when its a boolean.
    Third argument is a list of units that are expected for the arguments to
    the given function. Must be the same length as arguments can be given.
    If an argument is not expected to be a quantity, give None. If it is
    expected to be dimensionless (or a just a float or int), give UNITONE.
    Compatible units will be converted.
    Optional third argument can be a dict mapping keywords to units that are
    expected for arguments to the given function with that keyword.
    """
    
    indices_with_units = [index for (index, unit) in enumerate(arg_units) if
                                                         unit is not None]
    keys_with_units = kw_arg_units.keys()
    
    def wrapped_function(*args, **kwargs):
        """
        A wrapped version of %s to hadle arguments with units and return a
        value with a unit.
        
        Original documentation:
        %s
        """ % (function.__name__, function.__doc__)
        
        bare_args = list(args)
        for i in indices_with_units:
            bare_args[i] = in_unit(args[i], arg_units[i])._value
        
        for kw, kw_arg in kwargs.items():
            if kw in keys_with_units:
                kwargs[kw] = in_unit(kw_arg, kw_arg_units[kw])._value
        
        res = function(*bare_args, **kwargs)
        
        if result_unit is not None:
            res = PhysicalQuantity(res, result_unit)
        
        return res
    
    wrapped_function.__name__ = function.__name__
    
    return wrapped_function

