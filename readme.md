# QResult.py

## Overview

This module's goal is to provide a robust, type-safe, and functional approach to error handling and result management in Python, inspired by Functional programming but modeled to fit the constraints of pythonic programming. It defines generic result classes (`CResult`, `Result`) for business logic and API responses, with a goal of complete code path coverage with results encoded in result objects rather than relying on exceptions.

Please note that this code is just an initial design with the goal of building a opinionated code styling for Result generators and consumers. The goal is clean and readable business logic with robust failure, error and exception handling.

---

## Features

- **Type Safety & Validation**
  - Generic result classes (`CResult`, `Result`) parameterized by result type and, for `CResult`, an error code enum.
  - Runtime validation ensures results conform to expected types, including complex nested types (`Tuple`, `List`, `Union`).
  - Load-time validation via `__Result_Tools__` catches misconfigurations early.

- **Functional Error Handling**
  - All code paths (success, known errors, unknown errors, exceptions) are handled explicitly.
  - Errors are encoded in the result object, not thrown as exceptions unless explicitly raised.
  - `CResult` uses an `Enum` for error codes; `Result` omits error codes for simpler use cases.

- **Usability**
  - Context manager support (`with` statement) for resource management and clearer code.
  - Consistent API: `isOk()`, `isNotOk()`, `hasEx()`, and properties for result, reason, exception, and call frame.
  - Custom string representations for debugging and logging.

- **Code Path Coverage**
  - Comprehensive tests and examples exercise all code paths: success, known error, unknown error, exceptions etc.

- **Error Coding**
  - Explicit error states: error codes (for `CResult`), reason string for fail states, and exceptions are always present in error cases.
  - Validation ensures only valid error codes are used.
  - Errors can be raised as exceptions if desired, but are always catchable or detectable as `ResultBase`.

---

## Example Usage

### CResult (with error codes)

```python
with CResultExample.do_something("123 Main St") as R:
    if R.isNotOk():
        if R.hasEx():
            if R.code == CResultExample.ECode.TIMEOUT:
                print(f"Timeout Error: {R.ppstr()}")
            else:
                raise R
        else:
            if R.code == CResultExample.ECode.INVALID:
                print(f"Invalid Address: {R.reason}")
            elif R.code == CResultExample.ECode.UNKNOWN:
                print(f"Unknown Address: {R.ppstr()}")
            else:
                print(f"Failed: {R.ppstr()}")
    else:
        print(f"Success. result: {R.result}")
```


### CResultExample class
```python
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
```
