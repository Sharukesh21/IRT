from typing import Any, Dict

class AssertionEngine:
    @staticmethod
    def evaluate(operator: str, expected: Any, actual: Any) -> bool:
        if operator == "EQUALS":
            return actual == expected
        elif operator == "NOT_EQUALS":
            return actual != expected
        elif operator == "GREATER_THAN":
            return actual > expected
        elif operator == "LESS_THAN":
            return actual < expected
        elif operator == "GREATER_OR_EQUAL":
            return actual >= expected
        elif operator == "LESS_OR_EQUAL":
            return actual <= expected
        elif operator == "CONTAINS":
            return expected in actual if actual is not None else False
        elif operator == "NOT_CONTAINS":
            return expected not in actual if actual is not None else True
        elif operator == "TRUE":
            return actual is True
        elif operator == "FALSE":
            return actual is False
        elif operator == "EXISTS":
            return actual is not None
        elif operator == "NOT_EXISTS":
            return actual is None
        
        raise ValueError(f"Unsupported operator: {operator}")

    @staticmethod
    def extract_value(state: Dict[str, Any], path: str) -> Any:
        keys = path.split('.')
        current = state
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current
