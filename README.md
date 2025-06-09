# .py to .fprg Converter

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
| Classes / OOP         | ❌        |

## 🛠 Requirements

- Python 3.x