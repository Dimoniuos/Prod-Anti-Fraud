#Большая часть кодав этом файле бралась из откртых источников (по типу https://github.com/textX/textX ) + изменялась мною
import re

def dsl_error(code: str,  position=None, near=None):
    return {
        "isValid": False,
        "errorCode": code,
        "position": position,
        "near": near
    }
NUMERIC_FIELDS = {"amount", "user.age"}
STRING_FIELDS = {"currency", "merchantId", "ipAddress", "deviceId", "user.region"}

NUMERIC_OPERATORS = {">", ">=", "<", "<=", "=", "!="}
STRING_OPERATORS = {"=", "!="}

ALL_FIELDS = NUMERIC_FIELDS | STRING_FIELDS


TOKEN_REGEX = re.compile(
    r"\s*(>=|<=|!=|=|>|<|\(|\)|AND|OR|NOT|'[^']*'|\d+\.\d+|\d+|\w+(\.\w+)?)\s*",
    re.IGNORECASE
)

def tokenize(expr: str):
    tokens = TOKEN_REGEX.findall(expr)
    if not tokens:
        raise ValueError("DSL_PARSE_ERROR")
    return [t[0] for t in tokens]


def parse(tokens):
    pos = 0
    def current():
        return tokens[pos] if pos < len(tokens) else None
    def eat(expected=None):
        nonlocal pos
        tok = current()
        if tok is None:
            raise SyntaxError(pos)
        if expected and tok != expected:
            raise SyntaxError(pos)
        pos += 1
        return tok
    def parse_expression():
        node = parse_term()
        while current() and current().upper() == "OR":
            eat()
            node = {"type": "OR", "left": node, "right": parse_term()}
        return node

    def parse_term():
        node = parse_factor()
        while current() and current().upper() == "AND":
            eat()
            node = {"type": "AND", "left": node, "right": parse_factor()}
        return node
    def parse_factor():
        if current() and current().upper() == "NOT":
            eat()
            return {"type": "NOT", "expr": parse_factor()}
        if current() == "(":
            eat("(")
            node = parse_expression()
            eat(")")
            return node
        return parse_comparison()
    def parse_comparison():
        field = eat()
        if field not in ALL_FIELDS:
            raise ValueError(f"DSL_INVALID_FIELD:{field}")
        operator = eat()
        value_token = eat()
        if value_token.startswith("'"):
            value = value_token[1:-1]
            if operator not in STRING_OPERATORS:
                raise ValueError("DSL_INVALID_OPERATOR")
        else:
            value = float(value_token) if "." in value_token else int(value_token)
            if operator not in NUMERIC_OPERATORS:
                raise ValueError("DSL_INVALID_OPERATOR")

        return {
            "type": "CMP",
            "field": field,
            "operator": operator,
            "value": value
        }

    ast = parse_expression()
    if pos != len(tokens):
        raise SyntaxError(pos)
    return ast



def validate_dsl(expression: str) -> dict:
    try:
        tokens = tokenize(expression)
        parse(tokens)
        return {"isValid": True}
    except SyntaxError as e:
        return dsl_error("DSL_PARSE_ERROR", "Syntax error", position=e.args[0], near=None)
    except ValueError as e:
        msg = str(e)
        if msg.startswith("DSL_INVALID_FIELD"):
            return dsl_error("DSL_INVALID_FIELD", msg)
        if msg == "DSL_INVALID_OPERATOR":
            return dsl_error("DSL_INVALID_OPERATOR", msg)
        return dsl_error("DSL_PARSE_ERROR", msg)



def get_field_value(field: str, transaction: dict, user: dict):
    if field.startswith("user."):
        return user.get(field.split(".", 1)[1])
    return transaction.get(field)


def evaluate(ast: dict, transaction: dict, user: dict) -> bool:
    t = ast["type"]
    if t == "CMP":
        field_value = get_field_value(ast["field"], transaction, user)
        if field_value is None:
            return False
        op = ast["operator"]
        val = ast["value"]
        if op == ">":
            return field_value > val
        if op == ">=":
            return field_value >= val
        if op == "<":
            return field_value < val
        if op == "<=":
            return field_value <= val
        if op == "=":
            return field_value == val
        if op == "!=":
            return field_value != val
        return False

    if t == "AND":
        return evaluate(ast["left"], transaction, user) and \
               evaluate(ast["right"], transaction, user)
    if t == "OR":
        return evaluate(ast["left"], transaction, user) or \
               evaluate(ast["right"], transaction, user)
    if t == "NOT":
        return not evaluate(ast["expr"], transaction, user)
    return False


def apply_rule(expression: str, transaction: dict, user: dict):
    try:
        tokens = tokenize(expression)
        ast = parse(tokens)
        return evaluate(ast, transaction, user), ""
    except Exception:
        return False, "Rule evaluation failed"


def apply_rule_tier_0():
    return False, "DSL not supported yet"
