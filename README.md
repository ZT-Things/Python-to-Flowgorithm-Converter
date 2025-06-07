# .py to .fprg Converter

## Usage

```bash
python converter.py [input_file.py] [output_file.fprg]
```

## Requirements

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

## Known Issues

- Return statements **must return a single variable only**.
  - ✅ Allowed: `return result`
  - ❌ Not allowed: `return a + b`