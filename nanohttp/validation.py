import functools
import re

from nanohttp.exceptions import HttpBadRequest


class ActionValidator:
    def __init__(self, fields):
        self.fields = fields

    def __call__(self, form=None, query_string=None, *args, **kwargs):
        for field_name in self.fields:
            self.validate_field(field_name, form, query_string)
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

    def validate_field(self, field, form, query_string):
        """
        :param field: A dictionary of {field_name: validation_specification}
        :param form: A dictionary of request body that will be validate according to the above specification
        :param query_string: A dictionary of request query string that will be validate according to the above
            specification
        """

        specification = self.fields.get(field)
        accept_specification = specification.get('accept', 'form')
        accept_specification = set(accept_specification) if type(accept_specification) is list \
            else {accept_specification}

        if form and 'form' not in accept_specification and field in form:
            raise HttpBadRequest()
        elif query_string and 'query_string' not in accept_specification and field in query_string:
            raise HttpBadRequest()
        else:
            if form and field in form:
                value, parent = (form[field], 'form')
            elif query_string and field in query_string:
                value, parent = (query_string[field], 'query_string')
            else:
                value, parent = (None, None)

        if not value:
            if specification.get('required', False):
                raise HttpBadRequest()
            return

        value = self.validate_type(field, value)
        value = self.validate_length(field, value)
        value = self.validate_range(field, value)
        value = self.validate_pattern(field, value)
        locals()[parent][field] = value


def validate(fields):  # pragma: no cover

    def decorator(func):
        validator = ActionValidator(fields)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args, kwargs = validator(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
