from collections import OrderedDict
from collections.abc import Mapping
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.fields import get_error_detail, set_value
from rest_framework.settings import api_settings
from rest_framework.fields import SkipField
from rest_framework.serializers import ModelSerializer


class RobustSerializer(ModelSerializer):
    """鲁棒性更好的 ModeSerializer, 支持自定义获取数据字段"""

    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')

        errors = OrderedDict()
        ret = self.loop_fields(data, errors)
        if errors:
            raise ValidationError(errors)

        return ret

    def loop_fields(self, data, errors):
        fields = self._writable_fields
        ret = OrderedDict()

        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)

            # ---- start core code ----
            get_value_method = getattr(self, 'get_' + field.field_name, None)
            if get_value_method:
                primitive_value = get_value_method(field, data)
            else:
                primitive_value = field.get_value(data)
            # ---- end core code ----

            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = get_error_detail(exc)
            except SkipField:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)

        return ret
