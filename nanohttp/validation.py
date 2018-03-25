import functools
import re

from nanohttp import context
from nanohttp.exceptions import HttpBadRequest


class ActionValidator:
    def __init__(self, fields):
        self.default_rules = {}
        self.fields = fields

    @staticmethod
    def ensure_exists(field_name, form):
        if field_name not in form:
            raise HttpBadRequest()

    @classmethod
    def required(cls, field_name, expected_value, form):
        if expected_value:
            cls.ensure_exists(field_name, form)

    @classmethod
    def min(cls, field_name, expected_value, form):
        cls.ensure_exists(field_name, form)
        cls.type(field_name, (int,), form)
        if form.get(field_name) < expected_value[0]:
            raise HttpBadRequest()

    @classmethod
    def max(cls, field_name, expected_value, form):
        cls.ensure_exists(field_name, form)
        cls.type(field_name, (int,), form)
        if form.get(field_name) > expected_value[0]:
            raise HttpBadRequest()

    @classmethod
    def min_length(cls, field_name, expected_value, form):
        cls.ensure_exists(field_name, form)
        cls.type(field_name, (str,), form)
        if len(form.get(field_name)) < expected_value[0]:
            raise HttpBadRequest()

    @classmethod
    def max_length(cls, field_name, expected_value, form):
        cls.ensure_exists(field_name, form)
        cls.type(field_name, (str,), form)
        if len(form.get(field_name)) > expected_value[0]:
            raise HttpBadRequest()

    @classmethod
    def pattern(cls, field_name, expected_value, form):
        cls.ensure_exists(field_name, form)
        pattern = re.compile(expected_value[0]) if isinstance(expected_value[0], str) else expected_value[0]
        if pattern.match(form.get(field_name)) is None:
            raise HttpBadRequest()

    @classmethod
    def type(cls, field_name, desired_type, form):
        cls.ensure_exists(field_name, form)
        try:
            form[field_name] = desired_type[0](form[field_name])
        except ValueError:
            raise HttpBadRequest()

    def __call__(self, form=None, *args, **kwargs):
        form = context.form if form is None else form
        for field_name, validation in self.fields.items():
            for validation_title, validation_value in validation.items():
                if callable(validation_value):
                    # Todo: if callable
                    pass
                validation_value = (validation_value, 400) if type(validation_value) != tuple else validation_value
                getattr(self, validation_title)(field_name, validation_value, form)
        return form


def validate(fields):

    def decorator(func):
        validator = ActionValidator(fields)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args, kwargs = validator(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
