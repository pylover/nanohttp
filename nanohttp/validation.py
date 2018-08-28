import re
import functools
from _decimal import InvalidOperation

from nanohttp import context
from nanohttp.exceptions import HTTPStatus, HTTPBadRequest


NO_EMPTY_FORM = 'NO_EMPTY_FORM'
NO_FORM = 'NO_FORM'


class Field:
    def __init__(self, title, form=True, query=False, required=None,
                 type_=None, minimum=None, maximum=None, pattern=None,
                 min_length=None, max_length=None, callback=None,
                 not_none=None, readonly=None):
        self.title = title
        self.form = form
        self.query = query
        self.criteria = []

        if readonly:
            self.criteria.append(ReadonlyValidator(readonly))

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
            raise TypeError('Only bool and or string will be accepted.')

        super().__init__((True, error))


class RequiredValidator(FlagCriterion):
    def validate(self, field, container):
        if field.title not in container:
            raise self.create_exception()


class NotNoneValidator(FlagCriterion):
    def validate(self, field, container):
        if field.title not in container:
            return

        if container[field.title] is None:
            raise self.create_exception()


class ReadonlyValidator(FlagCriterion):
    def validate(self, field, container):
        if field.title in container:
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
        if len(value) < self.expression:
            raise self.create_exception()

        return value


class MaxLengthValidator(Criterion):

    def _validate(self, value, container, field):
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
        pattern = re.compile(self.expression) \
            if isinstance(self.expression, str) \
            else self.expression
        if pattern.match(value) is None:
            raise self.create_exception()

        return value


class RequestValidator:
    def __init__(self, fields, empty_form=None):
        # Merging default specification
        self.fields = {}
        self.empty_form = empty_form
        for field_name, specification in fields.items():
            kwargs = dict(callback=specification) \
                if callable(specification) else specification

            self.fields[field_name] = Field(field_name, **kwargs)

    def __call__(self, form=None, query=None, *args, **kwargs):
        for field_name, field in self.fields.items():

            if query and field.query:
                field.validate(query)

            if field.form \
                    and field.title is not None \
                    and (query is None or field.title not in query):
                field.validate(form)

        return form, query

class CallableValidator(Criterion):

    def _validate(self, value, container, field):
        return self.expression(value, container, field)


def validate(**fields):
    """Decorator to validate HTTP Forms and query string.

    .. code-block:: python

       @validate(field1=dict(required=True))
       def index(self, *, field1):
           ...


    Available parameters for validation is listed below:

    :param required: Boolean or str, indicates the field is required.
    :param not_none: Boolean or str, Raise when field is given and it's value
                     is None.

    :param type_: A callable to pass the received value to it as the only
                  argument and get it in the apprpriate type, Both
                  ``ValueError`` and `TypeError`` may be raised if the value
                  cannot casted to the specified type. A good example of this
                  callable would be the :class:`int`.
    :param minimum: Numeric, Minimum allowed value.
    :param maximum: Numeric, Maximum allowed value.
    :param pattern: Regex pattern to match the value.
    :param min_length: Only for strings, the minumum allowed length of the
                       value.
    :param max_length: Only for strings, the maximum allowed length of the
                       value.
    :param callback: A ``callable(value, container, field: Field)`` to be
                     called while validating the field.


    A detailed example:

    .. code-block:: python

       my_validator = validate(
           title=dict(
               required='710 Title not in form',
               max_length=(50, '704 At most 50 characters are valid for title')
           ),
           description=dict(
               max_length=(
                   512,
                   '703 At most 512 characters are valid for description'
               )
           ),
           dueDate=dict(
               pattern=(DATE_PATTERN, '701 Invalid due date format'),
               required='711 Due date not in form'
           ),
           cutoff=dict(
               pattern=(DATE_PATTERN, '702 Invalid cutoff format'),
               required='712 Cutoff not in form'
           ),
       )

       @json
       @my_validator
       def index(self):
           ...


    """

    validator = RequestValidator(fields)

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            validator(form=context.form, query=context.query)
            return func(*args, **kwargs)

        return wrapper

    return decorator

