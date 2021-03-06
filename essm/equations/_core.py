# -*- coding: utf-8 -*-
#
# This file is part of essm.
# Copyright (C) 2017 ETH Zurich, Swiss Data Science Center.
#
# essm is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# essm is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with essm; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
"""Core equation type. Contains class definitions related to equations."""

from __future__ import absolute_import

import warnings

import six
from sympy.core.relational import Eq

from ..bases import RegistryType
from ..transformer import build_instance_expression
from ..variables import Variable
from ..variables._core import BaseVariable, Variable
from ..variables.units import unit_symbols


class EquationMeta(RegistryType):
    r"""Equation interface.

    Defines an equation with a docstring and internal variables,
    if needed.

    Example:

    .. code-block:: python

        from ..variables.units import meter, second
        class test(Equation):
            '''Test equation.'''

            class d(Variable):
                '''Internal variable.'''
                unit = meter

            class t(Variable):
                '''Internal variable.'''
                unit = second

            class v(Variable):
                '''Internal variable.'''
                unit = meter/second

            expr = v == d / t

    :raises ValueError: if the units are inconsistent.

        Example:

        .. testcode:: python

           from ..variables.units import meter, second
           class test(Equation):
               '''Test equation with inconsistent units.'''

               class d(Variable):
                   '''Internal variable.'''
                   unit = meter

               class t(Variable):
                   '''Internal variable.'''
                   unit = second

               class v(Variable):
                   '''Internal variable.'''
                   unit = meter/second

               expr = v == d * t

        Since the units of v and d*t are not the same, this returns:

        .. testoutput::

           ValueError: Invalid expression units: meter/second == meter*second
    """

    def __new__(cls, name, parents, dct):
        """Build and register new variable."""
        if '__registry__' not in dct:
            dct.setdefault('name', name)
            expr = dct.pop('expr')

            instance = super(EquationMeta, cls).__new__(
                cls, name, parents, dct)
            expr = build_instance_expression(instance, expr)
            instance.expr = expr = BaseEquation(instance, expr)
            instance[expr] = instance

            return expr

        return super(EquationMeta, cls).__new__(cls, name, parents, dct)


@six.add_metaclass(EquationMeta)
class Equation(object):
    """Base type for all equations."""

    __registry__ = {}

    @classmethod
    def args(cls):
        """Return equation arguments from registry if exist."""
        return tuple(
            Variable.__registry__.get(arg, arg)
            for arg in cls.expr.atoms(BaseVariable))


class BaseEquation(Eq):
    """Add definition and short unit."""

    def __new__(cls, definition, expr):
        if not isinstance(expr, Eq):
            return expr
        # The below raises an error if units are not consistent
        Variable.check_unit(expr.lhs + expr.rhs)
        self = super(BaseEquation, cls).__new__(cls, *expr.args)
        self.definition = definition
        return self

    @property
    def __doc__(self):
        return self.definition.__doc__


__all__ = ('Equation', 'EquationMeta')
