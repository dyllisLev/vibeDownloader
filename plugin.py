# -*- coding: utf-8 -*-
#########################################################
# python
import os
import traceback

# third-party
import requests
from flask import Blueprint, request, send_file, redirect

# sjva 공용
from framework import app, path_data, check_api, py_urllib, SystemModelSetting
from framework.logger import get_logger
from framework.util import Util
from framework.common.plugin import get_model_setting, Logic, default_route

# 패키지
#########################################################
class P(object):
    package_name = __name__.split('.')[0]
    logger = get_logger(package_name)
    blueprint = Blueprint(package_name, package_name, url_prefix='/%s' %  package_name, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

    # 메뉴 정의
    menu = {
        'main' : [package_name, u'플러그인샘플'],
        'sub' : [
            ['sample', u'sample'], ['log', u'로그']
        ],
        'category' : 'tool',
        'sub2' : {
            'sample': [
                ['setting',u'설정'],['list', u'목록'], ['cardlist', u'카드목록'], ['uisample', u'UI샘플']
            ],
        },
    }

    plugin_info = {
        'version' : '0.1.0.0',
        'name' : package_name,
        'category_name' : 'tool',
        'icon' : '',
        'developer' : u'orial',
        'description' : u'Plugin sample for SJVA',
        'home' : 'https://github.com/byorial/%s' % package_name,
        'more' : '',
    }
    ModelSetting = get_model_setting(package_name, logger)
    logic = None
    module_list = None
    home_module = 'sample'  # 기본모듈


def initialize():
    try:
        app.config['SQLALCHEMY_BINDS'][P.package_name] = 'sqlite:///%s' % (os.path.join(path_data, 'db', '{package_name}.db'.format(package_name=P.package_name)))
        from framework.util import Util
        Util.save_from_dict_to_json(P.plugin_info, os.path.join(os.path.dirname(__file__), 'info.json'))

        # 로드할 모듈 정의
        from .sample import LogicSample
        P.module_list = [LogicSample(P)]

        P.logic = Logic(P)
        default_route(P)

    except Exception as e: 
        P.logger.error('Exception:%s', e)
        P.logger.error(traceback.format_exc())

@P.blueprint.route('/api/<sub>', methods=['GET', 'POST'])                                                                         
def baseapi(sub):                                                                                                                 
    P.logger.debug('API: %s', sub)
    try:
        from .sample import LogicSample
        P.logger.debug(request.form)
        return 'ok'
    except Exception as e: 
        P.logger.error('Exception:%s', e)
        P.logger.error(traceback.format_exc())

logger = P.logger
initialize()
