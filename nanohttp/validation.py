import re
import functools
from _decimal import InvalidOperation

from nanohttp import context
from nanohttp.exceptions import HTTPStatus, HTTPBadRequest


class Field:
    def __init__(self, title, form=True, query_string=False, required=None,
                 type_=None, minimum=None, maximum=None, pattern=None,
                 min_length=None, max_length=None, callback=None,
                 not_none=None):
        self.title = title
        self.form = form
        self.query_string = query_string
        self.criteria = []

        if required:
            self.criteria.append(RequiredValidator(required))

        if not_none:
            self.criteria.append(NotNoneValidator(not_none))

        if type_:
            self.criteria.append(TypeValidator(type_))

        if minimum:
            self.criteria.append(MinimumValidator(minimum))

        if maximum:
            self.criteria.append(MaximumValidator(maximum))

        if pattern:
            self.criteria.append(PatternValidator(pattern))

        if min_length:
            self.criteria.append(MinLengthValidator(min_length))

        if max_length:
            self.criteria.append(MaxLengthValidator(max_length))

        if callback:
            self.criteria.append(CallableValidator(callback))

    def validate(self, container):
        for criterion in self.criteria:
            criterion.validate(self, container)

        return container


class Criterion:
    def __init__(self, expression):
        if isinstance(expression, tuple):
            error = expression[1]
            self.expression = expression[0]
        else:
            self.expression = expression
            error = '400 Bad request'

        parsed_error = error.split(' ', 1)

        self.status_code = int(parsed_error[0])

        if len(parsed_error) == 2:
            self.status_text = parsed_error[1]
        else:
            self.status_text = 'Bad request'

    def validate(self, field: Field, container: dict) -> None:
        value = container.get(field.title)
        if value is None:
            return

        container[field.title] = self._validate(
            container[field.title],
            container,
            field
        )

    def _validate(self, value, container: dict, field: Field
                  ):  # pragma: no cover
        """
        It must be overridden in the child class.

        This method should raise exception if the criterion is not met. there
        is a chance to set
        a new value because the
        container is available here.
        :param value: The value to validate
        :param field:
        :param container:
        :return:
        """
        raise NotImplementedError()

    def create_exception(self):
        if self.status_code == 400:
            return HTTPBadRequest(self.status_text)

        return HTTPStatus(
            status=f'{self.status_code} {self.status_text}'
        )


class FlagCriterion(Criterion):
    def __init__(self, expression):
        if isinstance(expression, bool):
            error = '400 Bad request'
        elif isinstance(expression, str):
            error = expression
        else:
            raise ValueError('Only bool and or string will be accepted.')

        super().__init__((True, error))


class RequiredValidator(FlagCriterion):
    def validate(self, field, container):
        if field.title not in container:
            raise self.create_exception()


class NotNoneValidator(FlagCriterion):
    def validate(self, field, container):
        if container.get(field.title) is None:
            raise self.create_exception()


class TypeValidator(Criterion):

    def _validate(self, value, container, field):
        type_ = self.expression
        try:
            return type_(value)
        except (ValueError, TypeError, InvalidOperation):
            raise self.create_exception()


class MinLengthValidator(Criterion):

    def _validate(self, value, container, field):
        value = str(value)
        if len(value) < self.expression:
            raise self.create_exception()

        return value


class MaxLengthValidator(Criterion):

    def _validate(self, value, container, field):
        value = str(value)
        if len(value) > self.expression:
            raise self.create_exception()

        return value


class MinimumValidator(Criterion):

    def _validate(self, value, container, field):
        try:
            if value < self.expression:
                raise self.create_exception()
        except TypeError:
            raise self.create_exception()

        return value


class MaximumValidator(Criterion):

    def _validate(self, value, container, field):
        try:
            if value > self.expression:
                raise self.create_exception()
        except TypeError:
            raise self.create_exception()

        return value


class PatternValidator(Criterion):

    def _validate(self, value, container, field):
        pattern = re.compile(self.expression)\
            if isinstance(self.expression, str)\
            else self.expression
        if pattern.match(value) is None:
            raise self.create_exception()

        return value


class RequestValidator:
    def __init__(self, fields):
        # Merging default specification
        self.fields = {}
        for field_name, specification in fields.items():
            kwargs = dict(callback=specification) \
                if callable(specification) else specification

            self.fields[field_name] = Field(field_name, **kwargs)

    def __call__(self, form=None, query_string=None, *args, **kwargs):
        for field_name, field in self.fields.items():

            if query_string and field.query_string:
                query_string = field.validate(query_string)

            if field.form \
                    and field.title is not None \
                    and (
                        query_string is None or field.title not in query_string
                    ):
                form = field.validate(form)

        return form, query_string


class CallableValidator(Criterion):

    def _validate(self, value, container, field):
        return self.expression(value, container, field)


def validate(**fields):

    def decorator(func):
        validator = RequestValidator(fields)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            validator(form=context.form, query_string=context.query)
            return func(*args, **kwargs)

        return wrapper

    return decorator



