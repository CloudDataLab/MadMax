"""lattice.py: define lattices for use in meet-over-paths calculations."""

import typing
import functools
from copy import copy
import abc


class BoundedLatticeElement(abc.ABC):
  TOP_SYMBOL = "⊤"
  BOTTOM_SYMBOL = "⊥"

  @abc.abstractmethod
  def __init__(self, value=None, top:bool=False, bottom:bool=False):
    """Construct a lattice element with the given value."""
    self.value = value
    self.is_top = top
    self.is_bottom = bottom

    if value is None and not (top or bottom):
      self.is_top = True

  def __eq__(self, other):
    return self.value == other.value

  def __str__(self):
    if self.is_top:
      return self.TOP_SYMBOL
    elif self.is_bottom:
      return self.BOTTOM_SYMBOL
    else:
      return str(self.value)

  def __repr__(self):
    return "<{0} object {1}, {2}>".format(
      self.__class__.__name__,
      hex(id(self)),
      str(self)
    )

  @abc.abstractclassmethod
  def _top_val(cls):
    """Return the Top value of this lattice."""

  @abc.abstractclassmethod
  def _bottom_val(cls):
    """Return the Bottom value of this lattice."""

  @classmethod
  def top(cls) -> 'BoundedLatticeElement':
    """Return the Top lattice element."""
    return cls(top=True)

  @classmethod
  def bottom(cls) -> 'BoundedLatticeElement':
    """Return the Bottom lattice element."""
    return cls(bottom=True)

  @abc.abstractclassmethod
  def meet(cls, a:'BoundedLatticeElement',
           b:'BoundedLatticeElement') -> 'BoundedLatticeElement':
    """Return the infimum of the given elements."""

  @classmethod
  def meet_all(cls, elements:typing.Iterable['BoundedLatticeElement']) \
  -> 'BoundedLatticeElement':
    """Return the infimum of the given iterable of elements."""
    return functools.reduce(
      lambda a, b: cls.meet(a, b),
      elements,
      cls.top()
    )

  @abc.abstractclassmethod
  def join(cls, a:'BoundedLatticeElement',
           b:'BoundedLatticeElement') -> 'BoundedLatticeElement':
    """Return the infimum of the given elements."""

  @classmethod
  def join_all(cls, elements:typing.Iterable['BoundedLatticeElement']) \
  -> 'BoundedLatticeElement':
    """Return the supremum of the given iterable of elements."""
    return functools.reduce(
      lambda a, b: cls.join(a, b),
      elements,
      cls.bottom()
    )


class IntLatticeElement(BoundedLatticeElement):
  """An element of the meet-semilattice defined by augmenting
  the (unordered) set of integers with top and bottom elements.

  Integers are incomparable with one another, while top and bottom
  compare superior and inferior with every other element, respectively."""

  def __init__(self, value:int=None, top:bool=False, bottom:bool=False) -> None:
    super().__init__(value, top, bottom)

  def is_int(self) -> bool:
    """True iff this lattice element is neither Top nor Bottom."""
    return not (self.is_top or self.is_bottom)

  def __add__(self, other):
    if self.is_int() and other.is_int():
      return IntLatticeElement(self.value + other.value)
    return self.bottom()

  @classmethod
  def _top_val(cls):
    return cls.TOP_SYMBOL

  @classmethod
  def _bottom_val(cls):
    return cls.BOTTOM_SYMBOL

  @classmethod
  def meet(cls, a:'IntLatticeElement', b:'IntLatticeElement') \
  -> 'IntLatticeElement':
    """Return the infimum of the given elements."""

    if a.is_bottom or b.is_bottom:
      return cls.bottom()

    if a.is_top:
      return copy(b)
    if b.is_top:
      return copy(a)
    if a.value == b.value:
      return copy(a)

    return cls.bottom()

  @classmethod
  def join(cls, a:'IntLatticeElement', b:'IntLatticeElement') \
  -> 'IntLatticeElement':
    """Return the supremum of the given elements."""

    if a.is_top or b.is_top:
      return cls.top()

    if a.is_bottom:
      return copy(b)
    if b.is_bottom:
      return copy(a)
    if a.value == b.value:
      return copy(a)

    return cls.top()


class SubsetLatticeElement(BoundedLatticeElement):
  """
  A subset lattice element. The top element is the complete set of all
  elements, the bottom is the empty set, and other elements are subsets of top.
  """

  def __init__(self, value:typing.Iterable=None, top:bool=False, bottom:bool=False):
    super().__init__(set(value), top, bottom)

  @classmethod
  def _top_val(cls):
    return cls.TOP_SYMBOL

  @classmethod
  def _bottom_val(cls):
    return set()

  @classmethod
  def meet(cls, a:'SubsetLatticeElement', b:'SubsetLatticeElement') \
  -> 'SubsetLatticeElement':
    if a.is_top:
      return copy(b)
    if b.is_top:
      return copy(a)

    return SubsetLatticeElement(a.value & b.value)

  @classmethod
  def join(cls, a:'SubsetLatticeElement', b:'SubsetLatticeElement') \
    -> 'SubsetLatticeElement':
    if a.is_top or b.is_top:
      return cls.top()

    return SubsetLatticeElement(a.value | b.value)
