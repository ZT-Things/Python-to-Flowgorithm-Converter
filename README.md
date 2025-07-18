# .py to .fprg Converter

Turn code into .fprg for flowgorithm application

## 📦 Usage

```bash
python converter.py [input_file.py] [output_file.fprg]
```

## 📌 Requirements

- All functions **must include a type hint comment** in the following format:

```python
def function_name(param1, param2): # return_type param1_type param2_type
```

Example:

```python
def sum(a, b): # int int int
    s = a + b
    return s
```

- All array **must include a size hint comment** in the following format:
```python
arr = [1,2,3,4,5] # 5
```

- Check http://www.flowgorithm.org/documentation/language/intrinsic-functions.html for built-in functions

Example:

```python
s = input("Input a string") # str
n = ToInteger(s) # int

x = [1,2,3,4,5] # 5

print(Size(x))
```

## ⚠️ Known Issues

- Return statements **must return a single variable only**.
  - ✅ Allowed: `return result`
  - ❌ Not allowed: `return a + b`

- `+=` doesn't work, you'll have to do `i = i + 1` instead of `i += 1`

- `+` and `,`  doesn't work for joining strings or outputting variables onto the same line, use `&` instead
  - For example `print("Hello " & "World!")`

## 🔤 Supported Syntax

| Python Feature        | Supported |
|-----------------------|-----------|
| Function definitions  | ✅        |
| Variable assignments  | ✅        |
| `print()` function    | ✅        |
| `input()` function    | ✅        |
| Function calls        | ✅        |
| Return statements     | ✅        |
| Arithmetic operations | ✅        |
| `if` statements       | ✅        |
| `for` loops           | ✅        |
| `while` loops         | ✅        |
| Array                 | ✅        |
| Classes / OOP         | ❌        |
| I/O                   | ❌        |
| Turtle                | ❌        |
| Compile-time error    | ❌        |

## 🛠 Requirements

- Python 3.x

## Todo

- Support flowgorithm's built-in function and data type conversation (Done? But not polished)

- Support array

- Support for loops properly