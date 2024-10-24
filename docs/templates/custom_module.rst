{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. automodule:: {{ fullname }}
    :member-order: bysource

    Summary
    -------
    .. autosummary::
        {% for item in members %}
        {% if not item.startswith("_") %}
        {{ item }}
        {% endif %}
        {%- endfor %}

    {% if classes %}
    Classes
    -------
    {% for item in classes | sort(case_sensitive=True) %}
    .. autoclass:: {{ item }}
        :members:
        :undoc-members:
    {%- endfor %}
    {% endif %}

    {% if functions %}
    Functions
    ---------
    {% for item in functions | sort(case_sensitive=True) %}
    .. autofunction:: {{ item }}
    {%- endfor %}
    {% endif %}

    {% if attributes %}
    Module Attributes
    -----------------
    {% for item in attributes | sort(case_sensitive=True) %}
    {% if item not in classes %}
    .. autodata:: {{ item }}
    {% endif %}
    {%- endfor %}
    {% endif %}

    {% if exceptions %}
    Exceptions
    ----------
    {% for item in exceptions | sort(case_sensitive=True) %}
    .. autoexception:: {{ item }}
    {%- endfor %}
    {% endif %}

{% if modules %}
Modules
-------
.. autosummary::
:toctree:
:template: custom_module.rst
:recursive:
{% for item in modules %}
{{ item }}
{%- endfor %}
{% endif %}
