import re
import ast
from typing import Dict, List, Tuple, Optional
import json


class JavaScriptValidator:
    """Validates JavaScript code output from LLMs for security and correctness."""

    def __init__(self):
        # Dangerous patterns that could indicate malicious code
        self.dangerous_patterns = [
            # File system access
            r'\b(require\s*\(\s*[\'"]fs[\'"]|fs\.|readFile|writeFile|unlink|rmdir|mkdir)\b',
            # Process/shell execution
            r'\b(exec|spawn|fork|child_process|process\.exit|process\.kill)\b',
            # Network requests (could be used for data exfiltration)
            r'\b(fetch|XMLHttpRequest|axios|request|http\.|https\.|net\.|dgram\.)\b',
            # Eval and similar dangerous functions
            r'\b(eval|Function\s*\(|setTimeout\s*\([^,]+,|setInterval\s*\([^,]+,)\b',
            # Access to global objects that could be misused
            r'\b(global\.|process\.|__dirname|__filename|Buffer\.from)\b',
            # Crypto mining indicators
            r'\b(cryptonight|coinhive|coin-hive|miner|mining)\b',
            # Obfuscation attempts
            r'\\x[0-9a-fA-F]{2}|\\u[0-9a-fA-F]{4}|String\.fromCharCode',
            # Prototype pollution
            r'(__proto__|prototype\s*\[|constructor\s*\[)',
        ]

        # Suspicious patterns that warrant closer inspection
        self.suspicious_patterns = [
            # Base64 encoding (could hide malicious code)
            r'\b(atob|btoa|base64)\b',
            # Dynamic property access
            r'\[[\'"][^\'"]+[\'"]\]',
            # Large strings or arrays (could be obfuscated code)
            r'[\'"][^\'"]{1000,}[\'"]',
            r'\[(?:[^,\]]+,\s*){50,}',
        ]

        # Allowed safe patterns
        self.safe_patterns = [
            r'^console\.',
            r'^Math\.',
            r'^Array\.',
            r'^Object\.',
            r'^String\.',
            r'^Number\.',
            r'^Date\.',
            r'^JSON\.',
        ]

    def validate_javascript(self, code: str) -> Dict[str, any]:
        """
        Validates JavaScript code for security issues.

        Args:
            code: JavaScript code string to validate

        Returns:
            Dictionary containing:
                - is_valid: Boolean indicating if code passed validation
                - security_issues: List of security issues found
                - warnings: List of warnings about suspicious patterns
                - metrics: Code metrics (lines, complexity indicators)
        """
        result = {
            'is_valid': True,
            'security_issues': [],
            'warnings': [],
            'metrics': {}
        }

        # Basic validation
        if not code or not isinstance(code, str):
            result['is_valid'] = False
            result['security_issues'].append("Invalid input: code must be a non-empty string")
            return result

        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                result['is_valid'] = False
                result['security_issues'].append(
                    f"Dangerous pattern detected: {pattern} (found: {matches[0]})"
                )

        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                result['warnings'].append(f"Suspicious pattern detected: {pattern}")

        # Analyze code metrics
        result['metrics'] = self._analyze_metrics(code)

        # Check for syntax errors (basic)
        syntax_errors = self._check_syntax(code)
        if syntax_errors:
            result['is_valid'] = False
            result['security_issues'].extend(syntax_errors)

        # Check for infinite loops
        if self._check_infinite_loops(code):
            result['is_valid'] = False
            result['security_issues'].append("Potential infinite loop detected")

        # Check for excessive nesting
        if result['metrics']['max_nesting_depth'] > 10:
            result['warnings'].append(f"Excessive nesting depth: {result['metrics']['max_nesting_depth']}")

        return result

    def _analyze_metrics(self, code: str) -> Dict[str, int]:
        """Analyzes code metrics for complexity indicators."""
        metrics = {
            'lines': len(code.splitlines()),
            'characters': len(code),
            'functions': len(re.findall(r'\bfunction\b|\b=>\b', code)),
            'loops': len(re.findall(r'\b(for|while|do)\b', code)),
            'conditions': len(re.findall(r'\b(if|switch)\b', code)),
            'max_nesting_depth': self._calculate_nesting_depth(code),
        }
        return metrics

    def _calculate_nesting_depth(self, code: str) -> int:
        """Calculates maximum nesting depth of brackets."""
        max_depth = 0
        current_depth = 0

        for char in code:
            if char in '{[(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in '}])':
                current_depth = max(0, current_depth - 1)

        return max_depth

    def _check_syntax(self, code: str) -> List[str]:
        """Basic syntax checking."""
        errors = []

        # Check balanced brackets
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []

        for i, char in enumerate(code):
            if char in brackets:
                stack.append((char, i))
            elif char in brackets.values():
                if not stack:
                    errors.append(f"Unmatched closing bracket '{char}' at position {i}")
                else:
                    opening, _ = stack.pop()
                    if brackets[opening] != char:
                        errors.append(f"Mismatched brackets: '{opening}' and '{char}'")

        if stack:
            errors.append(f"Unclosed brackets: {[item[0] for item in stack]}")

        # Check for common syntax errors
        if re.search(r'\b(if|for|while|function)\s*[^(]', code):
            errors.append("Missing parentheses after control structure")

        return errors

    def _check_infinite_loops(self, code: str) -> bool:
        """Checks for obvious infinite loop patterns."""
        infinite_patterns = [
            r'while\s*\(\s*true\s*\)',
            r'while\s*\(\s*1\s*\)',
            r'for\s*\(\s*;\s*;\s*\)',
            r'for\s*\(\s*;true;\s*\)',
        ]

        for pattern in infinite_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                # Check if there's a break statement in the loop
                if not re.search(r'\bbreak\b', code):
                    return True

        return False

    def sanitize_output(self, code: str) -> str:
        """
        Attempts to sanitize code by removing dangerous patterns.
        Note: This is not foolproof and should not be relied upon for security.
        """
        sanitized = code

        # Remove dangerous function calls
        dangerous_functions = ['eval', 'Function', 'require']
        for func in dangerous_functions:
            sanitized = re.sub(rf'\b{func}\s*\(', f'/* REMOVED: {func} */(', sanitized)

        # Comment out file system and network operations
        sanitized = re.sub(r'\b(fs\.|http\.|https\.)', r'/* REMOVED: \1 */', sanitized)

        return sanitized

    def validate_llm_javascript(self, code: str, strict: bool = True) -> Tuple[bool, Dict[str, any]]:
        """
        Main function to validate JavaScript code from LLM output.

        Args:
            code: JavaScript code string to validate
            strict: If True, any security issue fails validation. If False, only critical issues fail.

        Returns:
            Tuple of (is_safe, validation_result)
        """
        result = self.validate_javascript(code)

        if strict:
            is_safe = result['is_valid'] and len(result['warnings']) == 0
        else:
            is_safe = result['is_valid']

        return is_safe, result
