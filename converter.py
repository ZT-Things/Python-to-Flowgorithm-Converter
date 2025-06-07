import ast
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
import os
import re
from datetime import datetime
import base64

class PythonToFlowgorithmConverter:
    def __init__(self):
        self.variables = {}
        self.element_id = 0
        self.comments = {}
        self.function_signatures = {}
        
    def get_next_id(self):
        """Generate unique element IDs"""
        self.element_id += 1
        return str(self.element_id)
    
    def create_flowgorithm_xml(self, python_file):
        """Create the base Flowgorithm XML structure"""
        root = ET.Element("flowgorithm", fileversion="4.2")
        
        attributes = ET.SubElement(root, "attributes")
        
        filename = os.path.splitext(os.path.basename(python_file))[0]
        ET.SubElement(attributes, "attribute", name="name", value=f"{filename}_converted")
        ET.SubElement(attributes, "attribute", name="authors", value="Python Converter")
        ET.SubElement(attributes, "attribute", name="about", value=f"Converted from {filename}.py")
        
        now = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        ET.SubElement(attributes, "attribute", name="saved", value=now)
        
        creation_info = f"Converted;{now}".encode('utf-8')
        creation_b64 = base64.b64encode(creation_info).decode('utf-8')
        ET.SubElement(attributes, "attribute", name="created", value=creation_b64)
        ET.SubElement(attributes, "attribute", name="edited", value=creation_b64)
        
        return root
    
    def parse_python_file(self, file_path):
        """Parse Python file and return AST with comments"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.extract_comments(content)
            
            return ast.parse(content)
        except Exception as e:
            print(f"Error parsing Python file: {e}")
            return None
    
    def extract_comments(self, content):
        """Extract comments for type hints"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '#' in line:
                comment = line.split('#')[1].strip().lower()
                

                if 'def ' in line:
                    func_match = re.search(r'def\s+(\w+)\s*\([^)]*\)', line)
                    if func_match:
                        func_name = func_match.group(1)
                        types = comment.split()
                        if types:
                            return_type = types[0] if types else 'void'
                            param_types = types[1:] if len(types) > 1 else []
                            self.function_signatures[func_name] = {
                                'return_type': return_type,
                                'param_types': param_types
                            }
                
                if comment in ['int', 'integer', 'string', 'str', 'float', 'double', 'boolean', 'bool']:
                    decl_line = i
                    while decl_line >= 0 and not lines[decl_line].strip():
                        decl_line -= 1
                    
                    if decl_line >= 0:
                        match = re.search(r'(\w+)\s*=', lines[decl_line])
                        if match:
                            var_name = match.group(1)
                            self.comments[var_name] = comment
    
    def convert_type_to_flowgorithm(self, type_str):
        """Convert type string to Flowgorithm type"""
        type_map = {
            'int': 'Integer',
            'integer': 'Integer',
            'str': 'String',
            'string': 'String',
            'float': 'Real',
            'double': 'Real',
            'real': 'Real',
            'bool': 'Boolean',
            'boolean': 'Boolean',
            'void': 'None'
        }
        return type_map.get(type_str.lower(), 'Integer')
    
    def convert_expression(self, expr):
        """Convert Python expression to string representation"""
        if isinstance(expr, ast.Constant):
            if isinstance(expr.value, str):
                return f'"{expr.value}"'
            return str(expr.value)
        elif isinstance(expr, ast.Name):
            return expr.id
        elif isinstance(expr, ast.BinOp):
            left = self.convert_expression(expr.left)
            right = self.convert_expression(expr.right)
            op_map = {
                ast.Add: '+', ast.Sub: '-', ast.Mult: '*', 
                ast.Div: '/', ast.Mod: '%', ast.Pow: '^',
                ast.BitAnd: '&'
            }
            op = op_map.get(type(expr.op), '?')
            return f"{left} {op} {right}"
        elif isinstance(expr, ast.Compare):
            left = self.convert_expression(expr.left)
            comparisons = []
            for i, (op, comp) in enumerate(zip(expr.ops, expr.comparators)):
                op_map = {
                    ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<',
                    ast.LtE: '<=', ast.Gt: '>', ast.GtE: '>='
                }
                op_str = op_map.get(type(op), '==')
                comp_str = self.convert_expression(comp)
                if i == 0:
                    comparisons.append(f"{left} {op_str} {comp_str}")
                else:
                    comparisons.append(f"{op_str} {comp_str}")
            return " and ".join(comparisons)
        elif isinstance(expr, ast.BoolOp):
            if isinstance(expr.op, ast.And):
                return " and ".join(self.convert_expression(v) for v in expr.values)
            elif isinstance(expr.op, ast.Or):
                return " or ".join(self.convert_expression(v) for v in expr.values)
        elif isinstance(expr, ast.Call):
            if isinstance(expr.func, ast.Name):
                if expr.func.id == 'input':
                    prompt = '""'
                    if expr.args:
                        prompt = self.convert_expression(expr.args[0])
                    return prompt
                elif expr.func.id == 'print':
                    if expr.args:
                        return self.convert_expression(expr.args[0])
                    return '""'
                elif expr.func.id in ['int', 'float', 'str']:
                    if expr.args:
                        return self.convert_expression(expr.args[0])
                else:
                    args = [self.convert_expression(arg) for arg in expr.args]
                    return f"{expr.func.id}({', '.join(args)})"
            return "function_call"
        else:
            return str(expr)
    
    def get_variable_type(self, var_name, default="Integer"):
        """Get variable type from comments or context"""
        if var_name in self.comments:
            comment = self.comments[var_name]
            if comment in ['int', 'integer']:
                return "Integer"
            elif comment in ['str', 'string']:
                return "String"
            elif comment in ['float', 'double']:
                return "Real"
            elif comment in ['bool', 'boolean']:
                return "Boolean"
        
        if var_name in self.variables:
            return self.variables[var_name]
        
        return default
    
    def create_element(self, tag, **attrs):
        elem = ET.Element(tag)
        for key, value in attrs.items():
            elem.set(key, str(value))
        return elem

    
    def declare_variable(self, parent, var_name, default_type="Integer"):
        """Declare a variable if not already declared"""
        if var_name not in self.variables:
            var_type = self.get_variable_type(var_name, default_type)
            declare_elem = self.create_element("declare", 
                                             name=var_name,
                                             type=var_type,
                                             array="False",
                                             size="")
            parent.append(declare_elem)
            self.variables[var_name] = var_type
    
    def convert_statements(self, statements, parent):
        """Convert list of Python statements to Flowgorithm elements"""
        if not statements:
            return
            
        for stmt in statements:
            element = None
            
            if isinstance(stmt, ast.FunctionDef):
                continue
                
            elif isinstance(stmt, ast.Return):
                continue
                
            elif isinstance(stmt, ast.Assign):
                if len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                    var_name = stmt.targets[0].id
                    
                    if isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'input':
                        prompt = self.convert_expression(stmt.value.args[0]) if stmt.value.args else '""'
                        
                        var_type = self.get_variable_type(var_name, "String")
                        
                        output_elem = self.create_element("output", expression=prompt, newline="True")
                        parent.append(output_elem)
                        
                        self.declare_variable(parent, var_name, var_type)
                        
                        input_elem = self.create_element("input", variable=var_name)
                        parent.append(input_elem)
                        
                        continue
                    else:
                        if isinstance(stmt.value, ast.Constant):
                            if isinstance(stmt.value.value, str):
                                default_type = "String"
                            elif isinstance(stmt.value.value, (int, float)):
                                default_type = "Integer" if isinstance(stmt.value.value, int) else "Real"
                            else:
                                default_type = "String"
                        else:
                            default_type = "Integer"
                        
                        self.declare_variable(parent, var_name, default_type)
                        element = self.create_element("assign", 
                                                    variable=var_name,
                                                    expression=self.convert_expression(stmt.value))
                    
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Name):
                    if stmt.value.func.id == 'print':
                        output_text = '""'
                        if stmt.value.args:
                            output_text = self.convert_expression(stmt.value.args[0])
                        
                        element = self.create_element("output", 
                                                    expression=output_text,
                                                    newline="True")
                    else:
                        func_name = stmt.value.func.id
                        args = [self.convert_expression(arg) for arg in stmt.value.args]
                        call_expr = f"{func_name}({', '.join(args)})"
                        
                        if func_name in self.function_signatures:
                            sig = self.function_signatures[func_name]
                            if sig['return_type'] == 'void':
                                element = self.create_element("call", expression=call_expr)
                            else:
                                element = self.create_element("call", expression=call_expr)
                        else:
                            element = self.create_element("call", expression=call_expr)
                    
            elif isinstance(stmt, ast.If):
                condition = self.convert_condition(stmt.test)
                element = self.create_element("if", expression=condition)
                
                then_elem = self.create_element("then")
                element.append(then_elem)
                self.convert_statements(stmt.body, then_elem)
                
                else_elem = self.create_element("else")
                element.append(else_elem)
                if stmt.orelse:
                    self.convert_statements(stmt.orelse, else_elem)
                    
            elif isinstance(stmt, ast.While):
                condition = self.convert_condition(stmt.test)
                element = self.create_element("while", expression=condition)
                
                self.convert_statements(stmt.body, element)
                
            elif isinstance(stmt, ast.For):
                if isinstance(stmt.iter, ast.Call) and isinstance(stmt.iter.func, ast.Name):
                    if stmt.iter.func.id == 'range':
                        start, stop, step = 0, 10, 1
                        
                        if len(stmt.iter.args) == 1:
                            stop = self.convert_expression(stmt.iter.args[0])
                        elif len(stmt.iter.args) == 2:
                            start = self.convert_expression(stmt.iter.args[0])
                            stop = self.convert_expression(stmt.iter.args[1])
                        elif len(stmt.iter.args) == 3:
                            start = self.convert_expression(stmt.iter.args[0])
                            stop = self.convert_expression(stmt.iter.args[1])
                            step = self.convert_expression(stmt.iter.args[2])
                        
                        if isinstance(stmt.target, ast.Name):
                            var_name = stmt.target.id
                            var_type = self.get_variable_type(var_name, "Integer")
                            self.declare_variable(parent, var_name, var_type)
                            
                            init_elem = self.create_element("assign",
                                                          variable=var_name,
                                                          expression=str(start))
                            parent.append(init_elem)
                            
                            condition = f"{var_name} < {stop}"
                            element = self.create_element("while", expression=condition)
                            
                            self.convert_statements(stmt.body, element)
                            
                            increment = self.create_element("assign",
                                                          variable=var_name,
                                                          expression=f"{var_name} + {step}")
                            element.append(increment)
            
            if element is not None:
                parent.append(element)
    
    def find_return_variable(self, func_body):
        """Find the variable name that gets returned in a function"""
        for stmt in func_body:
            if isinstance(stmt, ast.Return) and stmt.value:
                if isinstance(stmt.value, ast.Name):
                    return stmt.value.id
        return None
    
    def convert_function(self, func_def, root):
        """Convert a Python function definition to Flowgorithm function"""
        func_name = func_def.name
        
        return_type = "None"
        param_types = []
        
        if func_name in self.function_signatures:
            sig = self.function_signatures[func_name]
            return_type = self.convert_type_to_flowgorithm(sig['return_type'])
            param_types = [self.convert_type_to_flowgorithm(t) for t in sig['param_types']]
        
        return_variable = ""
        if return_type != "None":
            return_variable = self.find_return_variable(func_def.body)
            if return_variable is None:
                return_variable = "result"
        
        func_elem = ET.SubElement(root, "function",
                                 name=func_name,
                                 type=return_type,
                                 variable=return_variable)
        
        params_elem = ET.SubElement(func_elem, "parameters")
        for i, param in enumerate(func_def.args.args):
            param_type = param_types[i] if i < len(param_types) else "Integer"
            ET.SubElement(params_elem, "parameter",
                         name=param.arg,
                         type=param_type,
                         array="False")
        
        body_elem = ET.SubElement(func_elem, "body")
        
        if return_type != "None" and return_variable:
            pass
        
        self.convert_statements(func_def.body, body_elem)
    
    def convert_condition(self, test):
        """Convert if test condition, handling nested ifs"""
        if isinstance(test, ast.Compare):
            return self.convert_expression(test)
        elif isinstance(test, ast.BoolOp):
            return self.convert_expression(test)
        elif isinstance(test, ast.IfExp):
            return f"{self.convert_condition(test.test)} and {self.convert_condition(test.body)}"
        else:
            return self.convert_expression(test)
    
    def convert_file(self, python_file, output_file=None):
        """Convert Python file to Flowgorithm format"""
        if not os.path.exists(python_file):
            print(f"Error: File '{python_file}' not found")
            return False
        
        tree = self.parse_python_file(python_file)
        if tree is None:
            return False
        
        root = self.create_flowgorithm_xml(python_file)
        
        functions = []
        main_statements = []
        
        for stmt in tree.body:
            if isinstance(stmt, ast.FunctionDef):
                functions.append(stmt)
            else:
                main_statements.append(stmt)
        
        for func_def in functions:
            self.convert_function(func_def, root)
        
        main_func = ET.SubElement(root, "function", 
                                 name="Main", 
                                 type="None", 
                                 variable="")
        
        ET.SubElement(main_func, "parameters")
        
        body = ET.SubElement(main_func, "body")
        
        self.convert_statements(main_statements, body)
        
        if output_file is None:
            base_name = os.path.splitext(python_file)[0]
            output_file = f"{base_name}.fprg"
        
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="    ")
        
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        final_xml = '\n'.join(lines)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_xml)
            print(f"Successfully converted '{python_file}' to '{output_file}'")
            return True
        except Exception as e:
            print(f"Error writing output file: {e}")
            return False

def main():
    """Main function to handle command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python converter.py <input.py> [output.fprg]")
        print("Example: python converter.py hello.py")
        print("         python converter.py hello.py hello.fprg")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{base_name}.fprg"
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, output_file)
    
    converter = PythonToFlowgorithmConverter()
    
    success = converter.convert_file(input_file, output_file)
    
    if success:
        print("\nConversion completed successfully!")
        print("You can now open the .fprg file in Flowgorithm.")
    else:
        print("\nConversion failed. Please check the error messages above.")

if __name__ == "__main__":
    main()