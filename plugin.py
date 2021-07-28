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
    blueprint = Blueprint(package_name, package_name, url_prefix='/%s' %  package_name, template_folder=os.path.join(os.path.dirname(__file__), 'templates'), static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    # 메뉴 정의
    menu = {
        'main' : [package_name, u'VIBE 다운로드'],
        'sub' : [
            ['setting', u'설정'],['download', u'다운로드'],['manage', u'관리'], ['manual', u'매뉴얼'] ,['log', u'로그']
        ],
        'category' : 'service',
        'sub2' : {
            'download': [
                ['TOP100',u'차트'],['NEW', u'최신앨범'], ['search', u'검색'], ['list', u'다운로드 목록']
            ],
            'manual': [
                ['README.md',u'업데이트']
            ],
        },
    }

    plugin_info = {
        'version' : '0.1.0.0',
        'name' : package_name,
        'category_name' : 'service',
        'icon' : '',
        'developer' : u'dyllis.lev',
        'description' : u'VIBE 다운로드 for SJVA',
        'home' : 'https://github.com/dyllisLev/%s' % package_name,
        'more' : '',
    }
    ModelSetting = get_model_setting(package_name, logger)
    logic = None
    module_list = None
    home_module = 'setting'  # 기본모듈


def initialize():
    try:
        app.config['SQLALCHEMY_BINDS'][P.package_name] = 'sqlite:///%s' % (os.path.join(path_data, 'db', '{package_name}.db'.format(package_name=P.package_name)))
        from framework.util import Util
        Util.save_from_dict_to_json(P.plugin_info, os.path.join(os.path.dirname(__file__), 'info.json'))
        try:
            import xmltodict
        except:
            try: os.system(f"{app.config['config']['pip']} install xmltodict")
            except: pass
        try:
            import lzstring
        except:
            try: os.system(f"{app.config['config']['pip']} install lzstring")
            except: pass
        try:
            import mutagen
        except:
            try: os.system(f"{app.config['config']['pip']} install mutagen")
            except: pass
        # 로드할 모듈 정의
        from .setting import LogicSetting
        from .download import LogicDownload
        from .manage import LogicManage
        
        P.module_list = [LogicSetting(P), LogicDownload(P), LogicManage(P)]

        P.logic = Logic(P)
        default_route(P)

    except Exception as e: 
        P.logger.error('Exception:%s', e)
        P.logger.error(traceback.format_exc())

@P.blueprint.route('/api/<sub>', methods=['GET', 'POST'])                                                                         
def baseapi(sub):                                                                                                                 
    P.logger.debug('API: %s', sub)
    try:
        from .setting import LogicSetting
        P.logger.debug(request.form)
        return 'ok'
    except Exception as e: 
        P.logger.error('Exception:%s', e)
        P.logger.error(traceback.format_exc())

logger = P.logger
initialize()
