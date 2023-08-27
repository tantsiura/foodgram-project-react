import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if value.lower() == "me":
        raise ValidationError(
            ('You cannot use "me" as a username.'),
            params={"value": value},
        )
    if not re.match(r'^[a-zA-Z_.]*$', value):
        raise ValidationError('Name can only contain letters.')


def validate_name(value):
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s]*$', value):
        raise ValidationError('Name can only contain letters.')
