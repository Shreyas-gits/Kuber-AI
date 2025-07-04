"""Singleton metaclass for ensuring a class has only one instance.

This module provides a Singleton metaclass that can be used to make any class a singleton.
When a class uses this metaclass, only one instance of the class will be created, and
subsequent instantiations will return the same instance.

Example:
    class MyClass(metaclass=Singleton):
        pass

    a = MyClass()
    b = MyClass()
    assert a is b  # True

Classes:
    Singleton: Metaclass that implements the singleton pattern.
"""


class Singleton(type):
    """Metaclass for implementing the singleton pattern.

    Ensures that only one instance of a class exists.

    Attributes:
        _instances (dict): Dictionary mapping classes to their singleton instances.

    Methods:
        __call__(*args, **kwargs): Returns the singleton instance of the class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Return the singleton instance of the class.

        If the instance does not exist, create it. Otherwise, return the existing instance.

        Args:
            *args: Positional arguments for the class constructor.
            **kwargs: Keyword arguments for the class constructor.

        Returns:
            object: The singleton instance of the class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
