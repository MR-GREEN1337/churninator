# forge/utils/function_parser.py
# (This is the complete, correct code from the smoloperator context)
import re
from typing import Dict, List, Tuple, Any
from collections import OrderedDict
from pydantic import BaseModel


class FunctionCall(BaseModel):
    function_name: str
    parameters: Dict[str, Any]
    original_string: str
    description: str = ""

    def to_string(self) -> str:
        if not self.parameters:
            return f"{self.function_name}()"
        positional_args, named_args = [], []
        for name, value in self.parameters.items():
            if name.startswith("arg_"):
                positional_args.append((int(name.split("_")[1]), value))
            else:
                named_args.append((name, value))
        positional_args.sort(key=lambda x: x[0])
        param_parts = [self._value_to_string(v) for _, v in positional_args]
        param_parts.extend(f"{n}={self._value_to_string(v)}" for n, v in named_args)
        return f"{self.function_name}({', '.join(param_parts)})"

    def _value_to_string(self, value: Any) -> str:
        if isinstance(value, str):
            return f"'{value}'"
        if isinstance(value, (list, tuple)):
            return f"[{', '.join(self._value_to_string(i) for i in value)}]"
        if isinstance(value, dict):
            return f"{{{', '.join(f'{self._value_to_string(k)}: {self._value_to_string(v)}' for k, v in value.items())}}}"
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)


def parse_function_call(s: str) -> List[FunctionCall]:
    pattern = r"([a-zA-Z_][a-zA-Z0-9_.]*)\(([^)]*)\)"
    matches = re.findall(pattern, s.strip())
    results = []
    for match in matches:
        name, params_str = match[0], match[1]
        params = parse_parameters(params_str)
        results.append(
            FunctionCall(
                function_name=name,
                parameters=params,
                original_string=f"{name}({params_str})",
            )
        )
    return results


def parse_parameters(params_str: str) -> Dict[str, Any]:
    if not params_str.strip():
        return {}
    params = OrderedDict()
    parts = split_parameters(params_str)
    pos_idx = 0
    for part in parts:
        part = part.strip()
        if not part:
            continue
        name, value = parse_single_parameter(part)
        if name.startswith("arg_"):
            name = f"arg_{pos_idx}"
            pos_idx += 1
        params[name] = value
    return params


def split_parameters(params_str: str) -> List[str]:
    parts, current_part, depth, in_quotes = [], "", 0, False
    for char in params_str:
        if char in "\"'":
            in_quotes = not in_quotes
        elif not in_quotes and char == "(":
            depth += 1
        elif not in_quotes and char == ")":
            depth -= 1
        elif not in_quotes and char == "," and depth == 0:
            parts.append(current_part.strip())
            current_part = ""
            continue
        current_part += char
    if current_part.strip():
        parts.append(current_part.strip())
    return parts


def parse_single_parameter(param_str: str) -> Tuple[str, Any]:
    match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$", param_str)
    if match:
        return match.group(1), parse_value(match.group(2).strip())
    return "arg_0", parse_value(param_str)


def parse_value(v_str: str) -> Any:
    v_str = v_str.strip()
    if (v_str.startswith("'") and v_str.endswith("'")) or (
        v_str.startswith('"') and v_str.endswith('"')
    ):
        return v_str[1:-1]
    if v_str.lower() == "true":
        return True
    if v_str.lower() == "false":
        return False
    try:
        if "." in v_str:
            return float(v_str)
        return int(v_str)
    except ValueError:
        return v_str


def extract_function_calls_from_text(text: str) -> List[FunctionCall]:
    pattern = r"[a-zA-Z_][a-zA-Z0-9_.]*\([^)]*\)"
    matches = re.findall(pattern, text)
    results = []
    for m in matches:
        results.extend(parse_function_call(m))
    return results
