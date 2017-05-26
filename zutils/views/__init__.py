# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from django import http
from django.views.generic import View as DJView
from django.template import loader
from django.http import Http404, JsonResponse, HttpResponse
from django.forms.models import modelform_factory
from django.utils.translation import gettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from zutils import abstractclassmethod

logger = logging.getLogger('django.request')


class BaseView(DJView):
    func = None

    def http_method_not_allowed(self, request, *args, **kwargs):
        logger.warning(
            'Method Not Allowed (%s): %s',
            request.method.lower() if not request.is_ajax() else "ajax_{}".format(request.method.lower()),
            request.path,
            extra={'status_code': 405, 'request': request}
        )
        return http.HttpResponseNotAllowed(self._allowed_methods())

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        handler = getattr(self, "{}".format(self.func), None)
        if not handler:
            req_method = request.method.lower()
            handler = getattr(self, "{}_{}".format(self.func, req_method), None)
            if not handler:
                if req_method in self.http_method_names:
                    # handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    handler = getattr(self, "{}".format(request.method.lower()), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class RestPaginator(Paginator):
    def page(self, number):
        page = super(RestPaginator, self).page(number)
        return {
            'number': page.number,
            'object_list': [obj.to_dict() for obj in page.object_list],
            'count': page.paginator.count,
            'per_page': page.paginator.per_page
        }


class ListView(BaseView):
    PER_PAGE = 25
    PAGE = 'page'
    Paginator = None

    @abstractclassmethod
    def get_queryset(cls):
        pass

    @classmethod
    def get_paginator_class(cls):
        if not Paginator:
            return RestPaginator
        else:
            return cls.Paginator

    @classmethod
    def get_page_num(cls, request, *args, **kwargs):
        return request.GET.get(cls.PAGE, '1')

    @classmethod
    def get_object_list(cls, page_num):
        object_list = cls.get_queryset()
        paginator_cls = cls.get_paginator_class()
        paginator = paginator_cls(object_list, per_page=cls.PER_PAGE)
        try:
            object_list = paginator.page(page_num)
        except PageNotAnInteger:
            object_list = paginator.page(1)
        except EmptyPage:
            object_list = paginator.page(paginator.num_pages)
        return object_list


class View(ListView):
    """Generate rest field for model, 配合HTMLModel使用

    """
    pk_url_kwarg = 'pk'
    model = None
    template_detail = 'detail.html'
    template = 'form.html'
    display_list = []
    validator_class = None
    queryset = None

    def get_queryset(self):
        if not self.queryset:
            return self.model.objects.all()
        return self.queryset

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            form_fields = self.form_fields()
            return JsonResponse(form_fields, safe=False)
        else:
            template = loader.get_template(self.template)
            return HttpResponse(template.render({}, request))

    def post(self, request, *args, **kwargs):
        form = self.get_validator()(request.POST)
        if form.is_valid():
            ins = form.save()
            return JsonResponse({'status': 1,
                                 'url': ins.get_absolute_url()})
        errors = form.errors
        return JsonResponse(errors)

    @classmethod
    def get_display_list(cls):
        return cls.display_list

    @classmethod
    def get_validator(cls):
        if not cls.validator_class:
            error_messages = {}
            for field in cls.get_display_list():
                error_messages[field] = {
                    'required': _("{} is required.".format(cls.model._meta.get_field(field).verbose_name)),
                }
            return modelform_factory(cls.model, fields=cls.display_list, error_messages=error_messages)
        else:
            return cls.validator_class

    def detail_get(self, request, *args, **kwargs):
        obj = self.get_object(**kwargs)
        obj = obj.form_ins_fields(with_value=True)
        if self.display_list:
            try:
                obj = map(lambda x: obj[x], self.display_list)
            except KeyError as e:
                raise Exception("Fields must belong to {}".format(self.model._meta.model_name))

        if not request.is_ajax():
            template = loader.get_template(self.template_detail)
            return HttpResponse(template.render({'pk': self.get_pk(**kwargs)}, request))

        return JsonResponse(obj, safe=False)

    def get_pk(self, **kwargs):
        return kwargs.get(self.pk_url_kwarg, None)

    def get_object(self, *args, **kwargs):
        pk = self.get_pk(**kwargs)
        try:
            if pk is not None:
                obj = self.model.objects.get(pk=pk)
            else:
                raise AttributeError("Generic detail view %s must be called with "
                                     "either an object pk or a slug."
                                     % self.__class__.__name__)
        except self.model.DoesNotExist as e:
            raise Http404(str(e))
        return obj

    def form_fields(self):
        """

        Returns(list):

        """
        fields = self.model.form_fields()
        try:
            obj = map(lambda x: fields[x], self.display_list)
        except KeyError as e:
            raise Exception(
                "Field {} not belong to {}. Please check 'display_list' ".format(e, self.model._meta.model_name))
        return obj

    def form_ins_fields(self, obj):
        obj = obj.form_ins_fields()
        if self.display_list:
            try:
                obj = map(lambda x: obj[x], self.display_list)
            except KeyError as e:
                raise Exception("Fields must belong to {}".format(self.model._meta.model_name))
        return obj
