# -*- coding: utf-8 -*-
#########################################################
# python
import os, sys, traceback, re, json, threading, time, shutil
from datetime import datetime, timedelta
# third-party
import requests
# third-party
from flask import request, render_template, jsonify, redirect
from sqlalchemy import or_, and_, func, not_, desc

# sjva 공용
from framework import db, scheduler, path_data, socketio, SystemModelSetting, app, celery, py_unicode, py_urllib, py_queue
from framework.util import Util
from framework.common.util import headers, get_json_with_auth_session
from framework.common.plugin import LogicModuleBase, default_route_socketio
from framework.job import Job
import xmltodict, json, rsa, uuid, lzstring, subprocess

import xml.etree.ElementTree as ET

# 패키지
from .plugin import P
logger = P.logger
package_name = P.package_name
ModelSetting = P.ModelSetting

#########################################################

class LogicManage(LogicModuleBase):
    
    data = None
    session = None
    
    def __init__(self, P):
        super(LogicManage, self).__init__(P, 'manage') # 해당모듈의 기본 sub
        self.name = 'manage'    # 모듈명

    # 플러그인 로딩시 실행할 내용이 있으면 작성
    def plugin_load(self):
        self.db_migration()
        self.initialize()

    def process_menu(self, sub, req):
        # 각 메뉴들이 호출될때 필요한 값들을 arg에 넘겨주어야함
        arg = P.ModelSetting.to_dict()
        arg['sub'] = self.name
        P.logger.debug('sub:%s', sub)
        import random
        arg['v'] = random.random()
        P.logger.debug('{package_name}_{sub}.html'.format(package_name=P.package_name, module_name=self.name, sub=sub))
        return render_template('{package_name}_{sub}.html'.format(package_name=P.package_name, module_name=self.name, sub=sub), arg=arg)

    # 각 페이지에서의 요청 처리
    def process_ajax(self, sub, req):
        try:
            ret = {'ret':'success', 'data':[]}
            logger.debug('AJAX %s', sub)
            if sub == 'getFolderList':
                ret = LogicManage.getFolderList(req.form)
            elif sub == 'musicDownloadById':
                ret = LogicManage.musicDownloadById(req.form)
            
            return jsonify(ret)

        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return jsonify({'ret':'exception', 'msg':str(e)})

    #########################################################
    def db_migration(self):
        try:
            # db 마이그레이션: 필요한 경우에 작성 
            # ex) 배포 후 버전업에 따라 DB에 필드의 추가가 필요하거나 할떄 사용 설정의 db_version을 업데이트 하며 사용
            pass
        except Exception as e:
            logger.debug('Exception:%s', e)
            logger.debug(traceback.format_exc())

    def initialize(self):
        try:
            # 플러그인 로딩시 실행할 것들: Thread나 Queue 생성, 전역변수나 설정값들 초기화 등 처리
            pass
        except Exception as e: 
            P.logger.error('Exception:%s', e)
            P.logger.error(traceback.format_exc())
            return

    #########################################################
    # 필요함수 정의 및 구현부분
    @staticmethod
    def getFolderList(req):

        path = req['path']
        logger.debug(path)
        if path == '/' :
            # path = P.ModelSetting.to_dict()['rootPath']
            path = '/root/SJVA3'
        logger.debug(path)
        folderList = os.listdir(path)
        folderInfo = {}
        folderInfo.setdefault('folder')
        folderInfo['folder'] = {}
        folderInfo['folder'] = []
        logger.debug(folderInfo)
        for obj in folderList:
            
            name = str(obj)
            isdir = ''
            subObj = ''
            if os.path.isdir(os.path.join(path,obj)):
                isdir = "Y"
                subPathList = os.listdir(os.path.join(path,obj))
                for subobj in os.listdir(os.path.join(path,obj)):
                    if os.path.isdir(os.path.join(path,obj,subobj)):
                        subObj = "Y"                    
                folderInfo['folder'].append({'name':name, 'isdir':isdir, 'subObj':subObj, 'fullPath': os.path.join(path,obj)})
        return {'ret':'success', 'path':path, 'folderInfo':folderInfo}