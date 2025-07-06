"""
utils.extraction module
Provides utility functions for extracting data from JSON-like structures.
"""

import jmespath


def jmes_get(pattern, data, default=None):
    """
    Extract a value from a data structure using a JMESPath expression.

    :param pattern: JMESPath expression to apply.
    :type pattern: str
    :param data: The data to search (typically a dict or list).
    :type data: Any
    :param default: Value to return if the expression yields None.
    :type default: Any, optional
    :returns: The result of the JMESPath search, or `default` if no match is found.
    :rtype: Any
    """
    result = jmespath.search(pattern, data)
    if result is None and default is not None:
        return default
    return result
