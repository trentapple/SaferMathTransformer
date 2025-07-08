import ast

class SafeMathTransformer(ast.NodeVisitor):
    def init(self, allowed_operators=None):
        self.allowed_operators = {
            'Add': lambda x, y: x + y,
            'Sub': lambda x, y: x - y,
            'Mult': lambda x, y: x * y,
            'Div': lambda x, y: self.handle_division(x, y),
            'Pow': lambda x, y: x ** y
        }

        self.result = None

    def handle_division(self, numerator, denominator):
        if denominator == 0:
            raise ValueError(f"Division by zero: {numerator} / {denominator}")

        return numerator / denominator

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        operator_func = self.allowed_operators.get(type(node.op).__name__)

        if not operator_func:
            raise ValueError(f"Operator {type(node.op)} not allowed")

        return operator_func(left, right)

    def visit_Num(self, node):
        return node.n

    def visit_Constant(self, node):
        # Python 3.8+ uses Constant instead of Num
        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numeric constants allowed")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)

        operator_func = {
            'USub': lambda x: -x,
            'UAdd': lambda x: +x
        }.get(type(node.op).__name__)  

        if not operator_func:
            raise ValueError(f"Unary operator {type(node.op)} not allowed")

        return operator_func(operand)

    def visit(self, node):
        self.result = super().visit(node)

        return self.result

def calculator(equation: str) -> str:
    """
    Calculate the result of an equation safely.
    """

    try:
        # (consider more broad code point allow list)
        # Clear whitespace for parsing
        cleaned_equation = ''.join(equation.split())

        # Parse the expression
        tree = ast.parse(cleaned_equation, mode='eval')

        # Verify only allowed node types are present
        valid_nodes = (ast.BinOp, ast.Num, ast.Constant, 
                      ast.UnaryOp, ast.UAdd, ast.USub)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):  # Reject function calls
                return "Invalid equation"

            if isinstance(node, valid_nodes) or isinstance(type(node).__name__, str):
                continue

            return "Invalid equation"

        transformer = SafeMathTransformer()

        result = transformer.visit(tree.body)

        # Check for overflow
        if abs(result) > 1e308: # Beyond float64 limits (ensure portable)
            raise ValueError("Result too large")

        return f"{equation} = {result}"

    except Exception as e:
        print(f"Calculation error: {str(e)}")

        return "Invalid equation"
