# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
from django.db import models


class HTMLModel(models.Model):
    def form_fields(self, with_value=False):
        """
        form_$(field.name), default_form_fields

        Returns:

        """
        # 如果有指定field的格式化方法， 就使用指定的格式化方法，
        # 否则使用Field的格式化
        result = []
        for field in self._meta.fields:
            func = getattr(self, "form_{}".format(field.name), self.default_form_fields)
            result.append(func(field, with_value=with_value))
        return result

    def default_form_fields(self, field, with_value=False):
        """
        form_$(field_type)_value, values_form_field

        Args:
            field:
            with_value:

        Returns:

        """
        if with_value:
            field_processor = getattr(self,
                                      "form_{}_value".format(field.get_internal_type()),
                                      self.values_form_field)
        else:
            field_processor = lambda x: None
        return {'name': field.verbose_name,
                'value': field_processor(getattr(self, field.name)),
                'type': field.get_internal_type()
                }

    @staticmethod
    def values_form_field(value):
        return value

    @staticmethod
    def form_DateTimeField_value(value):
        return int(time.mktime(value.timetuple()))

    @staticmethod
    def form_DateField_value(value):
        return int(time.mktime(value.timetuple()))

    class Meta:
        abstract = True
