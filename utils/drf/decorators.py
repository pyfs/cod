import wrapt
from rest_framework.fields import empty
from rest_framework.utils import html


@wrapt.decorator
def validate_field_value(wrapped, instance, args, kwargs):
    """验证字段数据"""
    field = args[0]
    data = args[1]

    if html.is_html_input(data):
        if field.field_name not in data:
            if getattr(field.root, 'partial', False):
                return empty
            return field.default_empty_html

        ret = wrapped(*args, **kwargs)
        if ret == '' and field.allow_null:
            return '' if getattr(field, 'allow_blank', False) else None
        elif ret == '' and not field.required:
            return '' if getattr(field, 'allow_blank', False) else empty
        return ret
    return wrapped(*args, **kwargs)
