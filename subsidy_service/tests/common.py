"""Common functions for testing"""


def dummy_func(return_value=None, return_arg=None, raises=None):
    """
    Return a dummy callable function that accepts any inputs and returns the
    specified output as follows:
    * `raises` is not none -> raise `raises`
    * return_arg is an int -> the function will return the positional argument
        at the specified position unchanged
    * return_arg is a string -> the function will return the key word argument
        with that name unchanged
    * else the dummy function will return whatever value is in return_value
        (even if this is None)

    Will raise a ValueError if both returns and return_arg are specified.

    :param return_value: The value to return
    :param return_arg: The argument to return (keyword or position)
    :return: the dummy function
    """
    if return_value is not None and return_arg is not None:
        raise ValueError('Please specify at most one of [returns, return_arg]')

    def the_func(*args, **kwargs):
        if raises is not None:
            raise raises

        if isinstance(return_arg, int):
            return args[return_arg]

        elif isinstance(return_arg, str):
            return kwargs[return_arg]

        return return_value

    return the_func
