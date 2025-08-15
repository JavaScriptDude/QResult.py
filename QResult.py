from __future__ import annotations, print_function
# see http://python-future.org/compatible_idioms.html
#########################################
# QResult.py - 
#  - New Approach for functional programming code styling in Python
#  - Ported over from inhouse .Net development
#  - some optimizations would be needed for performance in production in ok() result validation for some business cases
#  - See readme.md for more information
# .: example :.
# (see inline)
# .: Other :.
# Author: Timothy C. Quinn
#########################################

import sys
import traceback
from types import FrameType
from typing import Generic, TypeVar, Optional, Any, Type, ForwardRef, Tuple, Union, List, get_origin, get_args
from enum import Enum
from abc import ABC

from decimal import Decimal


# =====================================================
# QResult Backend
TInst = TypeVar('TInst', bound='CResult')
TCode = TypeVar('TCode', bound=Enum)
TResult = TypeVar('TResult')

class ResultBase(Exception, ABC):
    pass

class CResult(ResultBase, Generic[TInst, TCode, TResult], ABC):
    __code__:TCode
    __result__:TResult
    __reason__:Optional[str]
    __ex__:Optional[Exception]
    __call_frame__:Optional[FrameType]

    def __init__(self, code: Optional[TCode] = None, result: Optional[TResult] = None,
                 reason: Optional[str] = None, ex: Optional[Exception] = None, caller: Optional[FrameType] = None):
        self.__code__ = code
        self.__result__ = result
        self.__reason__ = reason
        self.__ex__ = ex
        self.__call_frame__ = caller


    def isOk(self) -> bool: return (self.__ex__ is None and self.__reason__ is None)
    def isNotOk(self) -> bool: return not(self.isOk())
    def hasEx(self) -> bool: return self.__ex__ is not None

    # Define Read Only Property for Code
    @property
    def code(self) -> Optional[TCode]:
        return self.__code__

    @property
    def result(self) -> Optional[TResult]:
        return self.__result__

    @property
    def reason(self) -> Optional[str]:
        return self.__reason__

    @property
    def ex(self) -> Optional[Exception]:
        return self.__ex__

    @property
    def call_frame(self) -> Optional[FrameType]:
        return self.__call_frame__


    @classmethod
    def ok(cls, result: Optional[Any] = None):
        _orig_bases = getattr(cls, '__orig_bases__', [None])[0]
        _result_t = _orig_bases.__args__[2]
        __Result_Tools__.__check_ok_result__(cls, result, _result_t)
        return cls(result=result)

    @classmethod
    def fail(cls, code: Any, reason: Optional[str] = None, ex: Optional[Exception] = None):
        expected_type = getattr(cls, '__orig_bases__', [None])[0]

        _caller = None
        if expected_type and hasattr(expected_type, '__args__'):
            expected_code_type = expected_type.__args__[1]
            if not isinstance(code, expected_code_type):
                raise TypeError(f"Result.fail: code type {type(code)} does not match expected {expected_code_type}")
            if code not in list(expected_code_type):
                raise ValueError(f"Result.fail: code {code} is not a valid member of {expected_code_type}")

        if ex is None:
            if reason is None or str(reason).strip() == "":
                raise ValueError("Result.fail: reason must not be blank if ex is not provided")
            _caller = sys._getframe(1).f_code
        else:
            if reason is not None and str(reason).strip() == "":
                raise ValueError("Result.fail: reason must not be blank if provided")
            if not isinstance(ex, Exception):
                raise TypeError("Result.fail: ex must be an Exception if reason is None")

        return cls(code=code, reason=reason, ex=ex, caller=_caller)
    

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def ppstr(self, incl_type:bool=False) -> str:
        return self.__str__(incl_type=incl_type)

    def __str__(self, incl_type:bool=True, incl_caller:bool=True):
        sb = []
        if incl_type:
            sb.append(f"<{self.__class__.__name__}> ")
        
        if self.isOk():
            sb.append(f"OK result={self.result}")
        elif self.hasEx():
            sb.append(f"ERR code: {self.code}, ex: {self.ex}")
        else:
            sb.append(f"FAIL code: {self.code}")

        if self.reason:
            sb.append(f" reason: {self.reason}")

        if self.call_frame and incl_caller:
            sb.append(f" caller: {self.call_frame.co_filename} {self.call_frame.co_name}():{self.call_frame.co_firstlineno}")

        return "".join(sb)
    

class Result(ResultBase, Generic[TInst, TResult], ABC):
    __result__:TResult
    __reason__:Optional[str]
    __ex__:Optional[Exception]
    __call_frame__:Optional[FrameType]

    def __init__(self, result: Optional[TResult] = None,
                 reason: Optional[str] = None, ex: Optional[Exception] = None, caller: Optional[FrameType] = None):
        self.__result__ = result
        self.__reason__ = reason
        self.__ex__ = ex
        self.__call_frame__ = caller


    def isOk(self) -> bool: return (self.__ex__ is None and self.__reason__ is None)
    def isNotOk(self) -> bool: return not(self.isOk())
    def hasEx(self) -> bool: return self.__ex__ is not None

    @property
    def result(self) -> Optional[TResult]:
        return self.__result__

    @property
    def reason(self) -> Optional[str]:
        return self.__reason__

    @property
    def ex(self) -> Optional[Exception]:
        return self.__ex__

    @property
    def call_frame(self) -> Optional[FrameType]:
        return self.__call_frame__


    @classmethod
    def ok(cls, result: Optional[Any] = None):
        _orig_bases = getattr(cls, '__orig_bases__', [None])[0]
        _result_t = _orig_bases.__args__[1]
        __Result_Tools__.__check_ok_result__(cls, result, _result_t)
        return cls(result=result)

    @classmethod
    def fail(cls, reason: Optional[str] = None, ex: Optional[Exception] = None):
        expected_type = getattr(cls, '__orig_bases__', [None])[0]

        _caller = None

        if ex is None:
            if reason is None or str(reason).strip() == "":
                raise ValueError("Result.fail: reason must not be blank if ex is not provided")
            _caller = sys._getframe(1).f_code
        else:
            if reason is not None and str(reason).strip() == "":
                raise ValueError("Result.fail: reason must not be blank if provided")
            if not isinstance(ex, Exception):
                raise TypeError("Result.fail: ex must be an Exception if reason is None")

        return cls(reason=reason, ex=ex, caller=_caller)
    

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def ppstr(self, incl_type:bool=False) -> str:
        return self.__str__(incl_type=incl_type)

    def __str__(self, incl_type:bool=True, incl_caller:bool=True):
        sb = []
        if incl_type:
            sb.append(f"<{self.__class__.__name__}> ")
        
        if self.isOk():
            sb.append(f"OK result: `{self.result}`")
        elif self.hasEx():
            sb.append(f"ERR ex: `{self.ex}`")
        else:
            sb.append(f"FAIL")

        if self.reason:
            sb.append(f" reason: `{self.reason}`")

        if self.call_frame and incl_caller:
            sb.append(f" caller: {self.call_frame.co_filename} {self.call_frame.co_name}():{self.call_frame.co_firstlineno}")

        return "".join(sb)



class __Result_Tools__:

    @classmethod
    def __check_ok_result__(cls, t_cls, result, result_t):
        try:
            assert result is not None, f"Result.ok: result must not be None"

            def validate(val, typ, asrt:bool=True):
                origin = get_origin(typ)
                args = get_args(typ)
                if origin is Union:
                    if not any(validate(val, t, asrt=False) for t in args):
                        if asrt:
                            raise AssertionError(f"Result.ok: value {val} must match one of {args}")
                        return False

                elif origin is tuple:
                    if not(isinstance(val, tuple)):
                        if asrt:
                            raise AssertionError(f"Result.ok: value {val} must be a tuple")
                        return False

                    if len(val) != len(args):
                        if asrt:
                            raise AssertionError(f"Result.ok: tuple must have {len(args)} elements")
                        return False

                    for i, (v, t) in enumerate(zip(val, args)):
                        if not validate(v, t, asrt=False):
                            if asrt:
                                raise AssertionError(f"Result.ok: tuple element {v} must match {t}")
                            return False

                elif origin is list:
                    if not isinstance(val, list):
                        if asrt:
                            raise AssertionError(f"Result.ok: value {val} must be a list")
                        return False
                    
                    elem_type = args[0] if args else Any
                    for i, v in enumerate(val):
                        if not(validate(v, elem_type, asrt=False)):
                            if asrt:
                                raise AssertionError(f"Result.ok: list element {v} must match {elem_type}")
                            return False

                elif isinstance(typ, type):
                    if not isinstance(val, typ):
                        if asrt:
                            raise AssertionError(f"Result.ok: value {val} type {type(val)} does not match expected {typ}")
                        return False

                # else:
                #     # Accept Any or unknown typing types
                #     print(f"WARNING - Result.ok: value {val} does not match expected type {typ}, but will be accepted as Any or unknown typing type")
                #     pass

                return True

            validate(result, result_t)

        except Exception as ex:
            print("Failed while trying to process ok:")
            print("".join(traceback.format_exception(type(ex), value=ex, tb=ex.__traceback__)))
            print("")


    # Analyze the CResult class definition and print any errors to stdout
    @staticmethod
    def check_cresult_class_def(_type: Type[CResult]) -> None:
        try:
            assert _type is not None, \
                    "_type cannot be null"

            # 1. Check _type is subclass of CResult
            assert issubclass(_type, CResult), \
                    f"{_type} is not a subclass of CResult"

            # 2. Check generic params count and values
            orig_base = getattr(_type, '__orig_bases__', [None])[0]
            assert (orig_base and hasattr(orig_base, '__args__')), \
                    f"{_type} does not specify generic parameters"
            assert len(orig_base.__args__) == 3, \
                    f"{_type} must specify exactly 3 generic parameters, got {len(orig_base.__args__)}"

            first_param = orig_base.__args__[0]
            if isinstance(first_param, ForwardRef):
                assert first_param.__forward_arg__ == _type.__name__, \
                    f"First generic parameter ({first_param}) must refer to the class name ({_type.__name__})"
            else:
                assert first_param is _type, \
                    f"First generic parameter ({first_param}) must be the same as the class type ({_type})"

            second_param = orig_base.__args__[1]
            assert (isinstance(second_param, type) and issubclass(second_param, Enum)), \
                    f"Second generic parameter ({second_param}) must be an Enum type"

            third_param = orig_base.__args__[2]
            if not(isinstance(third_param, type)) \
               and not(getattr(third_param, '__module__', '').startswith('typing')):
                raise AssertionError(f"Third generic parameter ({third_param}) must be a valid type or a typing type (Union, Tuple, List)")


        except Exception as ex:
            print(f"__Result_Tools__.check_cresult_class_def failed: {ex}")


    # Analyze the Result class definition and print any errors to stdout
    @staticmethod
    def check_result_class_def(_type: Type[Result]) -> None:
        try:
            assert _type is not None, \
                    "_type cannot be null"

            # 1. Check _type is subclass of Result
            assert issubclass(_type, Result), \
                    f"{_type} is not a subclass of Result"

            # 2. Check generic params count and values
            orig_base = getattr(_type, '__orig_bases__', [None])[0]
            assert (orig_base and hasattr(orig_base, '__args__')), \
                    f"{_type} does not specify generic parameters"
            assert len(orig_base.__args__) == 2, \
                    f"{_type} must specify exactly 2 generic parameters, got {len(orig_base.__args__)}"

            first_param = orig_base.__args__[0]
            if isinstance(first_param, ForwardRef):
                assert first_param.__forward_arg__ == _type.__name__, \
                    f"First generic parameter ({first_param}) must refer to the class name ({_type.__name__})"
            else:
                assert first_param is _type, \
                    f"First generic parameter ({first_param}) must be the same as the class type ({_type})"

            second_param = orig_base.__args__[1]
            if not(isinstance(second_param, type)) \
               and not(getattr(second_param, '__module__', '').startswith('typing')):
                raise AssertionError(f"Second generic parameter ({second_param}) must be a valid type or a typing type (Union, Tuple, List)")


        except Exception as ex:
            print(f"__Result_Tools__.check_result_class_def failed: {ex}")
# END QResult Backend
#===========================================================


#===========================================================
# Implementation code:

# Contrived class that returns CResult
class CResultExample:
    class ECode(Enum):
        OK = 0
        INVALID = 1
        TIMEOUT = 2
        UNKNOWN = 3
        CORE_ERROR = 99

    class _R(CResult['_R', ECode, Tuple[str, int, List[Decimal]]]):
        pass

    @classmethod
    def do_something(cls, input:str) -> _R:
        _R = cls._R; ECode = cls.ECode

        try:
            # Simulate a timeout
            if input == "dbg_timeout":
                return _R.fail(ECode.TIMEOUT, ex=TimeoutError("timed out"))

            # Simulate invalid address
            if input == "dbg_invalid":
                return _R.fail(ECode.INVALID, reason="invalid data")

            if input == "dbg_unknown":
                return _R.fail(ECode.UNKNOWN, reason="unknown data")

            # Success path
            return _R.ok((input, 2, [Decimal(345),Decimal(567)],))
        
        
        except Exception as ex:
            return _R.fail(ECode.CORE_ERROR, ex=ex)


# Load time result type validation
__Result_Tools__.check_cresult_class_def(CResultExample._R)


# Contrived class that returns Result
class ResultExample:
    
    class _R(Result['_R', Tuple[str, int, List[Decimal]]]):
    # class _R(Result['_R', Union[str, int, List[Decimal]]]):
        pass

    @classmethod
    def do_something(cls, input:str) -> _R:
        _R = cls._R

        try:
            # Simulate a timeout
            if input == "dbg_timeout":
                return _R.fail(ex=TimeoutError("timed out"))

            # Simulate invalid address
            if input == "dbg_invalid":
                return _R.fail(reason="invalid data")

            if input == "dbg_unknown":
                return _R.fail(reason="unknown data")

            # Success path
            return _R.ok((input, 2, [Decimal(345),Decimal(567)],))
            # return _R.ok('cool')
            # return _R.ok(123)
            # return _R.ok([123,123])   
            # return _R.ok([Decimal(345),Decimal(567)])
        
        except Exception as ex:
            return _R.fail(ex=ex)


# Load time result type validation
__Result_Tools__.check_result_class_def(ResultExample._R)

def main():
    try:
        # test_CResult()
        # test_Result()

        # example_CResult()
        example_Result()
    except ResultBase as ex:
        print(f"ResultBase error occurred: {ex}")
    


def test_CResult():
    _tests:List[Tuple[str, CResultExample._R, bool]] = None
    _tests = [("123 Main St", CResultExample._R.ok(("123 Main St", 2, [Decimal(345), Decimal(567)])) ),
              ("dbg_invalid", CResultExample._R.fail(CResultExample.ECode.INVALID, reason="invalid data")),
              ("dbg_timeout", CResultExample._R.fail(CResultExample.ECode.TIMEOUT, ex=TimeoutError("timed out"))),
              ("dbg_unknown", CResultExample._R.fail(CResultExample.ECode.UNKNOWN, reason="unknown data"))]

    for sInput, expected in _tests:
        with CResultExample.do_something(sInput) as R:
            sR = R.__str__(incl_caller=False)
            sExp = expected.__str__(incl_caller=False)
            if sR != sExp: 
                print(f"Test failed for input '{sInput}':\nexpected `{sExp}`\n    got: `{sR}`")
                pass


def example_CResult():
    # actual real world example:
    sInput = "123 Main St"
    sResult: Tuple[str, int, List[Decimal]] = None
    with CResultExample.do_something(sInput) as R:
        if R.isNotOk():
            if R.hasEx():
                if R.code == CResultExample.ECode.TIMEOUT:
                    print(f"Timeout Error: {R.ppstr()}")
                else:
                    # Its an CResult object is an error and can be raised as is
                    # You just need to make sure upstream catch blocks are CResult aware
                    # Just catch ResultBase type to detect
                    raise R
            else:
                if R.code == CResultExample.ECode.INVALID:
                    print(f"Invalid Address: {R.reason}")

                elif R.code == CResultExample.ECode.UNKNOWN:
                    print(f"Unknown Address: {R.ppstr()}")

                else:
                    print(f"Failed: {R.ppstr()}")
        else:
            sResult = R.result
            print(f"Success. result: {sResult}")


def test_Result():

    _tests = [("123 Main St", ResultExample._R.ok(("123 Main St", 2, [Decimal(345), Decimal(567)])) ),
              ("dbg_invalid", ResultExample._R.fail(reason="invalid data")),
              ("dbg_timeout", ResultExample._R.fail(ex=TimeoutError("timed out"))),
              ("dbg_unknown", ResultExample._R.fail(reason="unknown data"))]

    for sInput, expected in _tests:
        with ResultExample.do_something(sInput) as R:
            sR = R.__str__(incl_caller=False)
            sExp = expected.__str__(incl_caller=False)
            if sR != sExp:
                print(f"Test failed for input '{sInput}':\nexpected `{sExp}`\n    got: `{sR}`")
                pass    


def example_Result():
    # sInput = "123 Main st"
    # sInput = "dbg_invalid"
    sInput = "dbg_timeout"
    # sInput = "dbg_unknown"

    sResult: Union[str, int, List[Decimal]] = None
    with ResultExample.do_something(sInput) as R:
        if R.isNotOk():
            if R.hasEx():
                # Its an Result object is an error and can be raised as is
                # You just need to make sure upstream catch blocks are Result aware
                # Just catch ResultBase type to detect
                raise R
            else:
                print(f"Failed: {R.ppstr()}")
        else:
            sResult = R.result
            print(f"Success. result: {sResult}")


# Example usage:
if __name__ == "__main__":
    main()


