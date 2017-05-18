# -*- coding: utf-8 -*-
import logging
from django import http
from django.views.generic import View as DJView
from django.http import Http404

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


class View(BaseView):
    """Generate rest field for model, 配合HTMLModel使用

    """
    pk_url_kwarg = 'pk'
    model = None
    template = 'detail.html'
    display_list = []

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
