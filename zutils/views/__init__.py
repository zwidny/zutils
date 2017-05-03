# -*- coding: utf-8 -*-
import logging
from django import http
from django.views.generic import View

logger = logging.getLogger('django.request')


class BaseView(View):
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
