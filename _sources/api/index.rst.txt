API
===

application Module
------------------

.. module:: nanohttp.application

Application
^^^^^^^^^^^

.. autoclass:: Application

    .. autoattribute:: __logger__
    .. autoattribute:: __root__
    .. automethod:: __init__


configuration Module
--------------------

.. module:: nanohttp.configuration

configure
^^^^^^^^^

.. autofunction:: configure


contexts Module
---------------

.. module:: nanohttp.contexts

Context
^^^^^^^
.. autoclass:: Context


controllers Module
------------------

.. module:: nanohttp.controllers

Controller
^^^^^^^^^^

.. autoclass:: Controller

RestController
^^^^^^^^^^^^^^

.. autoclass:: RestController

Static
^^^^^^
.. autoclass:: Static


RegexRouteController
^^^^^^^^^^^^^^^^^^^^
.. autoclass:: RegexRouteController


decorators Module
-----------------

.. automodule:: nanohttp.decorators

validations Module
------------------

.. automodule:: nanohttp.validation


Field
^^^^^

.. autoclass:: Field
.. autoclass:: Criterion
.. autoclass:: RequiredValidator
.. autoclass:: NotNoneValidator
.. autoclass:: TypeValidator
.. autoclass:: MinLengthValidator
.. autoclass:: MaxLengthValidator
.. autoclass:: MinimumValidator
.. autoclass:: MaximumValidator
.. autoclass:: PatternValidator
.. autoclass:: CallableValidator
.. autoclass:: RequestValidator


exceptions Module
-----------------

.. automodule:: nanohttp.exceptions

