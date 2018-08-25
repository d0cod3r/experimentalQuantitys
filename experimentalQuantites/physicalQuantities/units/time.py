# -*- coding: utf-8 -*-
"""
Definitions of units regarding TODO

@author: d0cod3r
"""

from ..quantities import Unit, Representation, NumberDict, FullName

s = second = seconds = Unit(
    None,
    FullName("seconds", "s", "s"))

minutes = Unit(
    Representation(NumberDict({second: 1}), 60),
    FullName("minutes", "min", "min"))

hour = hours = Unit(
    Representation(NumberDict({minutes: 1}), 60),
    FullName("hours", "h", "h"))

d = day = days = Unit(
    Representation(NumberDict({hours: 1}), 24),
    FullName("days", "d", "d"))

week = weeks = Unit(
    Representation(NumberDict({day: 1}), 7),
    FullName("weeks", "weeks", "weeks"))

month = months = Unit(
    Representation(NumberDict({day: 1}), 30),
    FullName("months", "months", "months"))

year = years = Unit(
    Representation(NumberDict({day: 1}), 356.25),
    FullName("years", "years", "years"))

ms = milliseconds = Unit(
        Representation(NumberDict({s: 1}), 1/1000),
        FullName("milliseconds", "ms", "ms"))

us = microseconds = Unit(
        Representation(NumberDict({ms: 1}), 1/1000),
        FullName("microseconds", "us", "\mu s"))

ns = nanoseconds = Unit(
        Representation(NumberDict({us: 1}), 1/1000),
        FullName("nanoseconds", "ns", "ns"))


del Unit, Representation, NumberDict, FullName