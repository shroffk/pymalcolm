from malcolm.compat import str_
from malcolm.core.serializable import Serializable, deserialize_object
from malcolm.core.vmeta import VMeta
from malcolm.core.stringarray import StringArray


@Serializable.register_subclass("malcolm:core/ChoiceMeta:1.0")
class ChoiceMeta(VMeta):
    """Meta object containing information for a enum"""

    endpoints = ["description", "choices", "tags", "writeable", "label"]

    def __init__(self, description="", choices=None, tags=None, writeable=False,
                 label=""):
        super(ChoiceMeta, self).__init__(description, tags, writeable, label)
        if choices is None:
            choices = []
        self.set_choices(choices)

    def set_choices(self, choices, notify=True):
        """Set the choices list"""
        choices = StringArray(deserialize_object(c, str_) for c in choices)
        self.set_endpoint_data("choices", choices, notify)

    def validate(self, value):
        """
        Check if the value is valid returns it

        Args:
            value: Value to validate

        Returns:
            Value if it is valid
        Raises:
            ValueError: If value not valid
        """
        if value is None:
            if self.choices:
                return self.choices[0]
            else:
                return ""
        elif value in self.choices:
            return value
        elif isinstance(value, int) and value < len(self.choices):
            return self.choices[value]
        else:
            raise ValueError(
                "%s is not a valid value in %s" % (value, self.choices))
