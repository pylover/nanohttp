import re
import functools

from nanohttp.exceptions import HttpBadRequest


class Criterion:
    def __init__(self, expression, status_code=400, status_text='Bad request'):
        self.expression = expression
        self.status_code = status_code
        self.status_text = status_text

    def validate(self, value):
        raise NotImplementedError()

    @classmethod
    def create(cls, type_, expression):
        if not isinstance(expression, tuple):
            expression = (expression, )

        return {
            'required': RequiredCriterion,
            'type': TypeCriterion,
            'min_length': MinLengthCriterion,
            'max_length': MaxLengthCriterion,
            'min': MinCriterion,
            'max': MaxCriterion,
            'pattern': PatternCriterion,
        }[type_](*expression)


class RequiredCriterion(Criterion):

    def validate(self, value):
        if not value:
            if self.expression:
                raise HttpBadRequest()
        return value


class TypeCriterion(Criterion):

    def validate(self, value):
        try:
            return self.expression(value)
        except ValueError:
            raise HttpBadRequest()


class MinLengthCriterion(Criterion):

    def validate(self, value):
        value = str(value)
        if len(value) < self.expression:
            raise HttpBadRequest()
        return value


class MaxLengthCriterion(Criterion):

    def validate(self, value):
        value = str(value)
        if len(value) > self.expression:
            raise HttpBadRequest()
        return value


class MinCriterion(Criterion):

    def validate(self, value):
        try:
            value = int(value)
            if value < self.expression:
                raise HttpBadRequest()
        except ValueError:
            raise HttpBadRequest()
        else:
            return value


class MaxCriterion(Criterion):

    def validate(self, value):
        try:
            value = int(value)
            if value > self.expression:
                raise HttpBadRequest()
        except ValueError:
            raise HttpBadRequest()
        else:
            return value


class PatternCriterion(Criterion):

    def validate(self, value):
        pattern = re.compile(self.expression) if isinstance(self.expression, str) else self.expression
        if pattern.match(value) is None:
            raise HttpBadRequest()
        return value


class Field:
    def __init__(self, title, form=True, query_string=False, **specification):
        self.title = title
        self.form = form
        self.query_string = query_string
        self.criteria = []
        for key, expression in specification.items():
            self.criteria.append(Criterion.create(key, expression))

    def validate(self, container):
        for criterion in self.criteria:
            result = criterion.validate(container.get(self.title) if container else None)
            if self.title in container:
                container[self.title] = result

        return container


class ActionValidator:
    def __init__(self, fields):
        default = dict(
            required=False,
            form=True,
            query_string=False
        )

        # Merging default specification
        self.fields = {}
        for field_name, specification in fields.items():
            default_copy = default.copy()
            default_copy.update(fields[field_name])
            self.fields[field_name] = Field(field_name, **specification)

    def __call__(self, form=None, query_string=None, *args, **kwargs):
        for field_name, field in self.fields.items():
            if form and field.form:
                form = field.validate(form)

            if query_string and field.query_string:
                query_string = field.validate(query_string)

        return form, query_string


def validate(fields):  # pragma: no cover

    def decorator(func):
        validator = ActionValidator(fields)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args, kwargs = validator(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
