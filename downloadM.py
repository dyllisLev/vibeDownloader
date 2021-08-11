# -*- coding: utf-8 -*-
#########################################################
# python
import os, sys, traceback, re, json, threading, time, shutil
from datetime import datetime, timedelta
# third-party
import requests
# third-party
from flask import request, render_template, jsonify, redirect, send_from_directory
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
from .download import LogicDownload

#########################################################

class LogicDownloadM(LogicModuleBase):
    
    def __init__(self, P):
        super(LogicDownloadM, self).__init__(P, 'downloadM') # 해당모듈의 기본 sub
        self.name = 'downloadM'    # 모듈명

    # 플러그인 로딩시 실행할 내용이 있으면 작성
    def plugin_load(self):
        # self.db_migration()
        # self.initialize()
        P.logger.debug('plugin_load')
    
    @P.blueprint.route('/downloadM', methods=['GET'])
    def page():
        self_instance = P.logic.get_module('downloadM')
        arg = P.ModelSetting.to_dict()
        arg['sub'] = self_instance.name
        import random
        arg['v'] = random.random()
        return render_template('vibeDownloader_download_M.html', arg=arg)
    
    @P.blueprint.route('/musicFileDownload/<path:path>', methods=['GET'])
    def download(path):
        logger.debug( path )
        if path.startswith('root/SJVA3/data/tmp'):
            return send_from_directory('/', path, as_attachment=True)
        else:
            return None
    
    def process_ajax(self, sub, req):
        try:
            ret = {'ret':'success', 'data':[]}
            
            if sub == 'search':
                logger.debug(req.form)
                ret = LogicDownload.search(req.form)
            elif sub == 'searchByTrack':
                ret = LogicDownload.searchByTrack(req.form)                
            elif sub == 'musicDownload':
                ret = LogicDownloadM.musicDownload(req.form)
            
            return jsonify(ret)

        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return jsonify({'ret':'exception', 'msg':str(e)})
    def musicDownload(req):
        logger.debug( req )

        trackId = req['trackId']
        
        trackInfo = None
        result = False
        
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/track/'+trackId)
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            trackInfo = json.loads(json.dumps(dictionary))
            
            info = LogicDownload.getDownloadFilePath(trackInfo['response']['result']['track'], type="track")
            path = "/root/SJVA3/data/tmp/"+trackId+".mp3"
            filePath = "/root/SJVA3/data/tmp/"+info['trackTitle']+"_"+info['artist']+".mp3"
            if os.path.isfile( path ) :
                logger.debug("파일 삭제")
                os.remove(path)
            trackId = LogicDownload.download(info)
            logger.debug(trackId)
            if trackId != False:
                logger.debug("setMetadata")
                LogicDownload.setMetadata(trackId)
                if os.path.isfile( os.path.join(path_data, 'tmp',trackId+".mp3") ):
                    shutil.move(os.path.join(path_data, 'tmp',trackId+".mp3") , filePath)
            
        return {'ret':'success', 'path':filePath}
