from   functools        import wraps
from   collections.abc  import Sequence, Iterable
from   typing           import overload, TypeVar, Self

def _coerce_pair(value : Iterable[int | float]) -> tuple[int, int]:    
    # Type check
    if isinstance(value, (str, bytes)):
        raise TypeError("String is not a valid NamedTuple input")
    
    # Get x & y components
    try:
        x, y = value
    # Unpacking error
    except (TypeError, ValueError):
        raise TypeError("Expected a NamedTuple or iterable of 2 numbers")
    
    # Component type check
    if isinstance(x, (str, bytes)) or isinstance(y, (str, bytes)):
        raise ValueError("Elements must be numeric (cannot be string or char)")
    
    # Return components as ints
    return int(x), int(y)

def _coerce_scalar(scalar : float | int):
    if isinstance(scalar, (int, float)):
        return scalar
    raise TypeError("Expected an integer or float")

def _wrapper_coerce_pair(method):
    @wraps(method)

    def wrapper(self, other):
        # 1. Enforce strict type matching for NamedPair subclasses
        if isinstance(other, NamedPair):
            if type(self) is not type(other):
                return NotImplemented
            # Since it's the exact same type, we know it's safe to unpack
            return method(self, other._data)
        
        # 2. Allow raw math-compatible sequences (like a standard tuple or list)
        try:
            otherData = _coerce_pair(other)
        except (TypeError, ValueError):
            return NotImplemented
        
        return method(self, otherData)
    
    return wrapper

def _wrapper_coerce_scalar(method):
    @wraps(method)

    def wrapper(self, other : float | int):
        try:
            other = _coerce_scalar(other)
        except TypeError:
            return NotImplemented
        
        return method(self, other)
    
    return wrapper


class NamedPair(Sequence[int]):
    __slots__ = ("_data") # No mutability
    _fields   = ('', '') # Subclasses define attribute names


    # --- Initialization --- #
    
    def __init__(self, *args, **kwargs):
        if len(args) == 2:
            self._data = _coerce_pair(args)
        elif len(args) == 1 and len(args[0]) == 2:
            self._data = _coerce_pair(args[0])
        elif kwargs and len(kwargs) == 2 and all(k in self._fields for k in kwargs):
            # Map keyword args to their index positions based on _fields order
            ordered_args = (kwargs[self._fields[0]], kwargs[self._fields[1]])
            self._data = _coerce_pair(ordered_args)
        else:
            raise TypeError(f"{type(self).__name__} requires (x, y) or iterable of length 2")

    def __init_subclass__(cls):
        if len(cls._fields) != 2:
            raise TypeError(f"{cls.__name__} must define exactly 2 string attributes in '_fields'")
        
        setattr(cls, cls._fields[0], property(lambda self: self._data[0]))
        setattr(cls, cls._fields[1], property(lambda self: self._data[1]))


    # --- Representation --- #

    def __repr__(self) -> str:
        f1, f2 = self._fields
        return f"{type(self).__name__}({f1}={self._data[0]}, {f2}={self._data[1]})"
    
    def __str__(self) -> str:
        f1, f2 = self._fields
        return f"{type(self).__name__}({f1}={self._data[0]}, {f2}={self._data[1]})"


    # --- Core Protocol --- #

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return 2
    
    def __getitem__(self, index : int) -> float:
        return self._data[index]


    # --- Comparison --- #

    def __eq__(self, other):
        if isinstance(other, (type(self), tuple)) and len(other) == 2:
            return self._data[0] == other[0] and self._data[1] == other[1]
        return NotImplemented


    # --- Arithmetic Operations --- #
    
    @_wrapper_coerce_pair
    def __add__(self, otherData):
        return type(self)(self._data[0] + otherData[0], self._data[1] + otherData[1])

    @_wrapper_coerce_pair
    def __radd__(self, otherData):
        return type(self)(otherData[0] + self._data[0], otherData[1] + self._data[1])
    

    @_wrapper_coerce_pair
    def __sub__(self, otherData):
        return type(self)(self._data[0] - otherData[0], self._data[1] - otherData[1])
    
    @_wrapper_coerce_pair
    def __rsub__(self, otherData):
        return type(self)(otherData[0] - self._data[0], otherData[1] - self._data[1])


    @_wrapper_coerce_scalar
    def __mul__(self, other):
        return type(self)(self._data[0] * other, self._data[1] * other)

    @_wrapper_coerce_scalar
    def __rmul__(self, other):
        return type(self)(other * self._data[0], other * self._data[1])

    
    @_wrapper_coerce_scalar
    def __truediv__(self, other):
        return type(self)(self._data[0] / other, self._data[1] / other)
    
    @_wrapper_coerce_scalar
    def __floordiv__(self, other):
        return type(self)(self._data[0] // other, self._data[1] // other)










class Coord(NamedPair):
    _fields = ('x', 'y')
    
class Size(NamedPair):
    _fields = ('w', 'h')
