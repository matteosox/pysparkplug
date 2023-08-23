API Reference
=============

.. currentmodule:: pysparkplug

Summary
-------

.. autosummary::

    Client
    ClientOptions
    ConnackCode
    DBirth
    DCmd
    DData
    DDeath
    DataType
    Device
    EdgeNode
    ErrorCode
    MQTTError
    MQTTProtocol
    MULTI_LEVEL_WILDCARD
    Message
    MessageType
    Metric
    MetricValue
    NBirth
    NCmd
    NData
    NDeath
    QoS
    SINGLE_LEVEL_WILDCARD
    State
    TLSConfig
    Topic
    Transport
    WSConfig
    get_current_timestamp

Interfaces
----------

.. autoclass:: Client
    :members:

.. autoclass:: EdgeNode
    :members:

.. autoclass:: Device
    :members:


Nuts & Bolts
------------

.. autoclass:: Message
    :members:

.. autoclass:: Topic
    :members:

.. autoclass:: Metric
    :members:

Payloads
--------

.. autoclass:: NBirth
    :members:
    :inherited-members:

.. autoclass:: DBirth
    :members:
    :inherited-members:

.. autoclass:: NData
    :members:
    :inherited-members:

.. autoclass:: DData
    :members:
    :inherited-members:

.. autoclass:: NCmd
    :members:
    :inherited-members:

.. autoclass:: DCmd
    :members:
    :inherited-members:

.. autoclass:: NDeath
    :members:
    :inherited-members:

.. autoclass:: DDeath
    :members:
    :inherited-members:

.. autoclass:: State
    :members:
    :inherited-members:

Config Classes
--------------

.. autoclass:: ClientOptions

.. autoclass:: TLSConfig

.. autoclass:: WSConfig

Enums
-----

.. autoclass:: ConnackCode

.. autoclass:: DataType
    :members:

.. autoclass:: ErrorCode

.. autoclass:: MessageType
    :members:

.. autoclass:: MQTTProtocol

.. autoclass:: QoS

.. autoclass:: Transport

Odds & Ends
-----------

.. autofunction:: get_current_timestamp

.. autoclass:: MetricValue

.. autoexception:: MQTTError

.. autodata:: SINGLE_LEVEL_WILDCARD

.. autodata:: MULTI_LEVEL_WILDCARD
