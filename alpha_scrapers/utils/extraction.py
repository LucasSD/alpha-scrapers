import jmespath


def jmes_get(pattern, data, default=None):
    result = jmespath.search(pattern, data)
    if result is None and default is not None:
        return default
    return result
