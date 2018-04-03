import functools
import re

from nanohttp.exceptions import HttpBadRequest


class ActionValidator:
    def __init__(self, fields):
        default = dict(
            required=False,
            form=True,
            query_string=False
        )

        for field_name in fields:
            default_copy = default.copy()
            default_copy.update(fields[field_name])
            fields[field_name] = default_copy

        self.fields = fields

    def __call__(self, form=None, query_string=None, *args, **kwargs):
        for field_name in self.fields:
            if form and self.fields[field_name]['form']:
                self.validate_field(field_name, form)

            if query_string and self.fields[field_name]['query_string']:
                self.validate_field(field_name, query_string)

        return form, query_string

    def validate_type(self, field, value):
        specification = self.fields.get(field)
        if 'type' in specification:
            try:
                return specification.get('type')(value)
            except ValueError:
                raise HttpBadRequest()
        return value

    def validate_length(self, field, value):
        specification = self.fields.get(field)
        if 'min_length' in specification:
            value = str(value)
            if len(value) < specification.get('min_length'):
                raise HttpBadRequest()
        if 'max_length' in specification:
            value = str(value)
            if len(value) > specification.get('max_length'):
                raise HttpBadRequest()
        return value

    def validate_range(self, field, value):
        specification = self.fields.get(field)
        try:
            if 'min' in specification:
                value = int(value)
                if value < specification.get('min'):
                    raise HttpBadRequest()
            if 'max' in specification:
                value = int(value)
                if value > specification.get('max'):
                    raise HttpBadRequest()
        except ValueError:
            raise HttpBadRequest()
        else:
            return value

    def validate_pattern(self, field, value):
        specification = self.fields.get(field)
        if 'pattern' in specification:
            desired_pattern = specification.get('pattern')
            pattern = re.compile(desired_pattern) if isinstance(desired_pattern, str) else desired_pattern
            if pattern.match(value) is None:
                raise HttpBadRequest()
        return value

    def validate_field(self, field, container):
        """
        :param field: A field_name that should be validate with self.fields specification
        :param container: A dictionary that will be validate according to the above specification
        """

        specification = self.fields.get(field)

        value = container.get(field)
        if not value:
            if specification['required']:
                raise HttpBadRequest()
            return

        value = self.validate_type(field, value)
        value = self.validate_length(field, value)
        value = self.validate_range(field, value)
        value = self.validate_pattern(field, value)
        container[field] = value


def validate(fields):  # pragma: no cover

    def decorator(func):
        validator = ActionValidator(fields)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args, kwargs = validator(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
