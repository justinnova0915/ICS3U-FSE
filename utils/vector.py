from    __future__      import annotations
from    functools       import wraps

from    typing          import Self
from    collections.abc import Iterable

from    math            import isclose, sqrt, acos



########## ########## ==============  ============== ########## ##########
########## ########## ========= UTILITIES ========== ########## ##########
########## ########## ==============  ============== ########## ##########

def _coerce_xy(value : Iterable[int | float] | Vector) -> tuple[float, float]:
    # Vector
    if isinstance(value, Vector):
        return value.x, value.y
    
    # Type check
    if isinstance(value, (str, bytes)):
        raise TypeError("String is not a valid Vector input")
    
    # Get x & y components
    try:
        x, y = value
    # Unpacking error
    except (TypeError, ValueError):
        raise TypeError("Expected a Vector or iterable of 2 numbers")
    
    # Component type check
    if isinstance(x, (str, bytes)) or isinstance(y, (str, bytes)):
        raise ValueError("Elements must be numeric (cannot be string or char)")
    
    # Return components as floats
    return float(x), float(y)

def _coerce_vector(value : Iterable[int | float] | Vector) -> Vector:
    if isinstance(value, Vector):
        return value
    
    x, y = _coerce_xy(value)
    return Vector(x, y)

def _coerce_scalar(scalar : float | int):
    if isinstance(scalar, (int, float)):
        return scalar
    raise TypeError("Expected an integer or float")

def _assert_nonZeroMag(mag):
    if mag == 0:
        raise ValueError("Cannot operate on a zero vector")


    ########## ==========  ========== ##########
    ########## ===== DECORATOS ====== ##########
    ########## ==========  ========== ##########

def coerce_xy_otherVector(method):
    @wraps(method)

    def wrapper(self, other : Vector | Iterable[float]):
        try:
            ox, oy = _coerce_xy(other)
        except (TypeError, ValueError):
            return NotImplemented
        
        return method(self, ox, oy)
    
    return wrapper

def coerce_vector_otherVector(method):
    @wraps(method)
    
    def wrapper(self, other : Vector | Iterable[float]):
        try:
            other_vec = Vector(_coerce_vector(other))
        except (TypeError, ValueError):
            return NotImplemented
        
        return method(self, other_vec)
    
    return wrapper

def coerce_scalar(method):
    @wraps(method)

    def wrapper(self, other : float | int):
        try:
            other = _coerce_scalar(other)
        except TypeError:
            return NotImplemented
        
        return method(self, other)
    
    return wrapper

# def coerce_mag(method):
#     @wraps(method)

#     def wrapper(self):
#         if self.magnitude == 0:
#             raise ZeroDivisionError("Cannot divide by a zero vector")
        
#         return method(self)
    
#     return wrapper










########## ########## ==============  ============== ########## ##########
########## ########## ======== VECTOR CLASS ======== ########## ##########
########## ########## ==============  ============== ########## ##########

class Vector:

    ########## ==============  ============== ##########
    ########## ======= INITIALIZATION ======= ##########
    ########## ============================== ##########

    def __init__(self, *args):
        if len(args) == 1:
            coords = _coerce_xy(args[0])
        elif len(args) == 2:
            coords = _coerce_xy(args)
        else:
            raise TypeError("Vector requires (x, y) or iterable of length 2")
        
        self.x, self.y = coords





    ########## ============================== ##########
    ########## ======= REPRESENTATION ======= ##########
    ########## ============================== ##########

    def __repr__(self) -> str:
        return f"Vector<{self.x}, {self.y}>"
    
    def __str__(self) -> str:
        return f"Vector({self.x}, {self.y})"





    ########## ============================== ##########
    ########## ======= CORE PROTOCOL ======== ##########
    ########## ============================== ##########

        ########## ==========  ========== ##########
        ########## ===== ITERATING ====== ##########
        ########## ==========  ========== ##########

    def __iter__(self):
        yield self.x
        yield self.y

    def __len__(self) -> int:
        return 2
    
    def __getitem__(self, index : int) -> float:
        if isinstance(index, int):
            if index == 0 or index == -2:
                return self.x
            if index == 1 or index == -1:
                return self.y
            raise IndexError('Vector index out of range')
        
        raise TypeError('Vector indices must be integers')
        

        ########## ==========  ========== ##########
        ########## ===== COMPARISON ===== ##########
        ########## ==========  ========== ##########

    @coerce_xy_otherVector
    def __eq__(self, ox : float, oy : float) -> bool:
        return isclose(self.x, ox) and isclose(self.y, oy)
    
    @coerce_xy_otherVector
    def __ne__(self, ox : float, oy : float) -> bool:
        return not (isclose(self.x, ox) and isclose(self.y, oy))
    

        ########## ==========  ========== ##########
        ########## == UNARY OPERATORS === ##########
        ########## ==========  ========== ##########
    
    def __neg__(self):
        return type(self)(-self.x, -self.y)
    
    def __pos__(self):
        return type(self)(self.x, self.y)





    ########## ============================== ##########
    ########## === ARITHMETIC OPERATIONS ==== ##########
    ########## ============================== ##########

        ########## ==========  ========== ##########
        ########## ====== ADDITION ====== ##########
        ########## ==========  ========== ##########

    @coerce_xy_otherVector
    def __add__(self, ox : float, oy : float) -> Self:
        return type(self)(self.x + ox, self.y + oy)
    
    @coerce_xy_otherVector
    def __radd__(self, ox : float, oy : float) -> Self:
        return type(self)(ox + self.x, oy + self.y)

    @coerce_xy_otherVector
    def __iadd__(self, ox : float, oy : float) -> Self:
        self.x += ox
        self.y += oy

        return self


        ########## ==========  ========== ##########
        ########## ==== SUBSTRACTION ==== ##########
        ########## ==========  ========== ##########

    @coerce_xy_otherVector    
    def __sub__(self, ox : float, oy : float) -> Self:
        return type(self)(self.x - ox, self.y - oy)
    
    @coerce_xy_otherVector
    def __rsub__(self, ox : float, oy : float) -> Self:
        return type(self)(ox - self.x, oy - self.y)
    
    @coerce_xy_otherVector
    def __isub__(self, ox : float, oy : float) -> Self:
        self.x -= ox
        self.y -= oy

        return self


        ########## ==========  ========== ##########
        ########## === MULTIPLICATION === ##########
        ########## ==========  ========== ##########

    @coerce_scalar
    def __mul__(self, other : float | int) -> Self:
        return type(self)(self.x * other, self.y * other)
    
    @coerce_scalar
    def __rmul__(self, other : float | int) -> Self:
        return type(self)(other * self.x, other * self.y)
    
    @coerce_scalar
    def __imul__(self, other : float | int) -> Self:
        self.x *= other
        self.y *= other

        return self


        ########## ==========  ========== ##########
        ########## ====== DIVISON ======= ##########
        ########## ==========  ========== ##########

    @coerce_scalar
    def __truediv__(self, other : float | int):
        return type(self)(self.x / other, self.y / other)

    @coerce_scalar
    def __itruediv__(self, other : float | int):
        self.x /= other
        self.y /= other

        return self

    @coerce_scalar
    def __floordiv__(self, other : float | int):
        return type(self)(self.x // other, self.y // other)





    ########## ============================== ##########
    ########## ========= PROPERTIES ========= ##########
    ########## ============================== ##########
    @property
    def magnitude(self) -> float:
        return sqrt((self.x ** 2) + (self.y ** 2))
    
    @property
    def magnitude_squared(self) -> float:
        return ((self.x ** 2) + (self.y ** 2))





    ########## ============================== ##########
    ########## ===== VECTOR OPERATIONS ====== ##########
    ########## ============================== ##########
    
        ########## ==========  ========== ##########
        ########## ====== DISTANCE ====== ##########
        ########## ==========  ========== ##########

    @coerce_vector_otherVector
    def distanceTo(self, other : Vector | Iterable[float]) -> float:
        return (other - self).magnitude
    
    @coerce_vector_otherVector
    def distanceTo_squared(self, other : Vector | Iterable[float]) -> float:
        return (other - self).magnitude_squared

        ########## ==========  ========== ##########
        ########## ===== NORMALIZE ====== ##########
        ########## ==========  ========== ##########

    # @coerce_mag
    def normalized(self, mag = None) -> Self:
        smag    = self.magnitude; _assert_nonZeroMag(smag)
        nx      = self.x / smag
        ny      = self.y / smag
        if mag is not None:
            nx *= mag
            ny *= mag

        return type(self)(nx, ny)
    
    # @coerce_mag
    def normalize(self, mag = None) -> Self:
        smag    = self.magnitude; _assert_nonZeroMag(smag)
        self.x /= smag
        self.y /= smag
        if mag is not None:
            self.x *= mag
            self.y *= mag

        return self


        ########## ==========  ========== ##########
        ########## ====== PRODUCTS ====== ##########
        ########## ==========  ========== ##########


    @coerce_xy_otherVector
    def dot(self, ox : float, oy : float) -> float:
        return self.x * ox + self.y * oy
    
    @coerce_xy_otherVector
    def cross(self, ox: float, oy: float) -> float:
        return self.x * oy - self.y * ox


        ########## ==========  ========== ##########
        ########## ======= ANGLE ======== ##########
        ########## ==========  ========== ##########

    @coerce_vector_otherVector
    def angle_with(self, other : Self) -> float:
        # returns angle in RADIANS
        dot         = self.dot(other)
        magnitudes  = self.magnitude * other.magnitude; _assert_nonZeroMag(magnitudes)

        return acos(dot / magnitudes)


        ########## ==========  ========== ##########
        ########## ===== PROJECTION ===== ##########
        ########## ==========  ========== ##########

    @coerce_vector_otherVector
    def project_onto(self, other : Self) -> Self:
        dot     = self.dot(other)
        mag_sq  = other.magnitude_squared; _assert_nonZeroMag(mag_sq)
        scalar  = dot / mag_sq

        return type(self)(other.x * scalar, other.y * scalar)




    ########## ============================== ##########
    ########## ======== MISCELANEOUS ======== ##########
    ########## ============================== ##########
    
    def copy(self):
        return type(self)(self)
    

        ########## ==========  ========== ##########
        ########## ======== MATH ======== ##########
        ########## ==========  ========== ##########

    @coerce_scalar
    def clamp(self, mag : int | float) -> Vector:
        if self.magnitude > mag:
            return self.normalized(mag)
        return self.copy()
    
    def lerp(self, other, t):
        ox, oy  = _coerce_xy(other)
        t       = _coerce_scalar(t)

        return type(self)(self.x + t * (ox - self.x),
                          self.y + t * (oy - self.y))
    
        ########## ==========  ========== ##########
        ########## == TYPE CONVERSION === ##########
        ########## ==========  ========== ##########
    def to_int(self) -> tuple:
        return (int(self.x), int(self.y))

    def to_tuple(self) -> tuple:
        return (self.x, self.y)
    
    def to_list(self) -> list:
        return [self.x, self.y]