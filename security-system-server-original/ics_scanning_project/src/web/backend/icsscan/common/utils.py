# -*- coding:utf-8 -*-

from django.http import JsonResponse


def json_response(msg, ensure_ascii=False):
    """
    给django的JsonResponse增加中文编码支持
    :param ensure_ascii: 
    :param msg:
    :return:
    """
    dumps_params = {'ensure_ascii': ensure_ascii}
    return JsonResponse(msg, json_dumps_params=dumps_params)
