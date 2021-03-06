from malcolm.core.meta import Meta
from malcolm.core.ntscalar import NTScalar


class VMeta(Meta):
    """Abstract base class for Validating Meta objects"""
    attribute_class = NTScalar

    def validate(self, value):
        """Abstract function to validate a given value

        Args:
            value: Value to validate
        """
        raise NotImplementedError(
            "Abstract validate function must be implemented in child classes")

    def make_attribute(self, initial_value=None):
        """Make an Attribute instance of the correct type for this Meta

        Args:
            initial_value: The initial value the Attribute should take
        """
        attr = self.attribute_class(self, initial_value)
        return attr
