{% macro safe_rate(numerator, denominator, digits=3) %}
    round(
        {{ numerator }} * 1.0 / nullif({{ denominator }}, 0),
        {{ digits }}
    )
{% endmacro %}
