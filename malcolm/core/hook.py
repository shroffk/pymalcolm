import inspect

from malcolm.core.methodmeta import MethodMeta


class Hook(object):

    def __call__(self, func):
        """
        Decorator function to add a Hook to a Part's function

        Args:
            func: Function to decorate with Hook

        Returns:
            Decorated function
        """

        if not hasattr(func, "Hooked"):
            func.Hooked = []
        func.Hooked.append(self)
        # TODO: is this needed?
        MethodMeta.wrap_method(func)
        return func

    def find_hooked_functions(self, parts):
        # Filter part dict to find parts that have a function hooked to us
        # {Part: func_name}
        part_funcs = {}

        for part in parts.values():
            for func_name, part_hook, func in get_hook_decorated(part):
                if part_hook is self:
                    assert part not in part_funcs, \
                        "Function %s is second defined for a hook" % func_name
                    part_funcs[part] = func_name

        return part_funcs


def get_hook_decorated(part):
    for name, member in inspect.getmembers(part, inspect.ismethod):
        if hasattr(member, "Hooked"):
            for hook in member.Hooked:
                yield name, hook, member
