def documented_at(original, **subs):
    def wrapper(target):
        target.__doc__ = original.__doc__
        if subs:
            for old, new in subs.items():
                target.__doc__ = target.__doc__.replace(old, new)
        return target

    return wrapper


def _series_itervals(s):
    """wrapper that turns a pandas/dask dataframe into a generator of values only (for sklearn)

    Args:
      s:

    Returns:

    """
    for n, val in s.iteritems():
        yield val
