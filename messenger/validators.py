import os
import re
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
isalphavalidator = RegexValidator(r'^[A-Za-z0-9-À-ÿ? ,_\':-]+$',message='This field must be alphanumeric',code='Invalid field')
