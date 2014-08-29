import six


def force_str(s):
    if isinstance(s, str):
        return s
    elif isinstance(s, six.text_type):
        return s.encode("utf-8")
    elif isinstance(s, six.binary_type):
        return s.decode("utf-8")
    raise ValueError("Not a string")


def force_bytes(s):
    if isinstance(s, six.binary_type):
        return s
    elif isinstance(s, six.text_type):
        return s.encode("utf-8")
    raise ValueError("Not a string")
