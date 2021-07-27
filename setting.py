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

# 패키지
from .plugin import P
logger = P.logger
package_name = P.package_name
ModelSetting = P.ModelSetting

#########################################################

class LogicSetting(LogicModuleBase):
    db_default = {
        'db_version' : '1',
        # 스케쥴러
        'setting_interval'   : '60',
        'auto_start' : 'False',

        # 유형별 설정값
        'naverId'    : 'id',
        'naverPw'    : u'pass',
        'savePath'       : os.path.join(path_data, package_name),
        'saveFileName'   : '%albumTitle% - %trackNumber% - %trackTitle% - %artist%',
        'savePathByTOP100'       : os.path.join(path_data, package_name, "TOP100", "%toptitle%","%today%"),
        'saveFileNameByTOP100'       : '%rank% - %trackTitle% - %artist%',
        'savePathByAlbum'       : os.path.join(path_data, package_name, "album","%albumTitle%"),
        'saveFileNameByAlbum'       : '%trackNumber% - %trackTitle% - %artist%',
        'savePathByArtist'       : os.path.join(path_data, package_name, "artist","%artist%","%albumTitle%"),
        'saveFileNameByArtist'       : '%trackNumber% - %trackTitle%',
        'ffmpegDownload' : False,
        'newAlbumDownload1' : False,
        'newAlbumDownload2' : False,
        'newAlbumDownload3' : False,
        'albumId' : '',
        'artistId' : '',
        'top100Key' : '',
        'top100Download1' : False,
        'top100Download2' : False,
        'top100Download3' : False,
        'top100Download4' : False,
        'top100Download5' : False,
        'top100Download6' : False,
        'top100Download7' : False,
        'top100Download8' : False,
        'top100Download9' : False,
        'delayTime' : 3,
        'lastloginTime' : 0

    }

    def __init__(self, P):
        super(LogicSetting, self).__init__(P, 'setting') # 해당모듈의 기본 sub
        self.name = 'setting'    # 모듈명

    # 플러그인 로딩시 실행할 내용이 있으면 작성
    def plugin_load(self):
        self.db_migration()
        self.initialize()
        if ModelSetting.query.filter_by(key='auto_start').first().value == 'True':
            LogicSetting.scheduler_start()

    def process_menu(self, sub, req):
        # 각 메뉴들이 호출될때 필요한 값들을 arg에 넘겨주어야함
        arg = P.ModelSetting.to_dict()
        arg['sub'] = self.name
        P.logger.debug('sub:%s', sub)
        
        if sub == 'setting':    # 설정페이지의 경우 스케쥴러 포함여부와 실행상태 전달
            job_id = '%s_%s' % (self.P.package_name, self.name)
            arg['scheduler'] = str(scheduler.is_include(job_id))
            arg['is_running'] = str(scheduler.is_running(job_id))
        P.logger.debug('{package_name}_{sub}.html'.format(package_name=P.package_name, module_name=self.name, sub=sub))
        return render_template('{package_name}_{sub}.html'.format(package_name=P.package_name,sub=sub), arg=arg)

    # 각 페이지에서의 요청 처리
    def process_ajax(self, sub, req):
        try:
            ret = {'ret':'success', 'data':[]}
            logger.debug('AJAX %s', sub)
            logger.debug('AJAX!!!!!!!!!!!!! %s', sub)
            #logger.debug(req.form)
            if sub == 'register_item':
                ret = LogicSetting.register_item(req.form)
            elif sub == 'modify_item':
                ret = LogicSetting.modify_item(req.form)
            elif sub == 'delete_item':
                ret = LogicSetting.delete_item(req.form)
            elif sub == 'web_list':
                ret = ModelItem.web_list(req)
            return jsonify(ret)

        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return jsonify({'ret':'exception', 'msg':str(e)})

    @staticmethod
    def scheduler_start():
        try:
            job = Job(package_name, package_name+'_setting', ModelSetting.get('setting_interval'), LogicSetting.scheduler_function, u"vibeDownloader_setting", False)
            scheduler.add_job_instance(job)
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    # 스케쥴러에 의한 메인 로직 작동
    @staticmethod
    def scheduler_function():
        logger.debug('scheduler function!!!!!!!!!!!!!!')
        from .download import LogicDownload
        if app.config['config']['use_celery']:
            result = LogicDownload.task.apply_async()
            result.get()
        else:
            LogicDownload.task()
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
# DB 모델 정의: @classmethod 사용
class ModelAutoAlbum(db.Model):
    __tablename__ = '%s_AutoAlbum' % package_name
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime)
    reserved = db.Column(db.JSON)
    # 사용할 필드 정의
    albumType = db.Column(db.String)
    albumId = db.Column(db.String)
    
    def __init__(self, albumType, albumId):
        self.created_time = datetime.now()
        self.albumType = py_unicode(albumType)
        self.albumId = py_unicode(albumId)
        
    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        ret = {x.name: getattr(self, x.name) for x in self.__table__.columns}
        ret['created_time'] = self.created_time.strftime('%m-%d %H:%M:%S') 
        return ret

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def delete(cls, id):
        db.session.query(cls).filter_by(id=id).delete()
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return db.session.query(cls).filter_by(id=id).first()
    
    @classmethod
    def get_by_albumId(cls, albumId):
        return db.session.query(cls).filter_by(albumId=albumId).first()
    
    @classmethod
    def get_by_typeByAlbumId(cls, albumType, albumId):
        return db.session.query(cls).filter_by(albumType=albumType,albumId=albumId).first()

    # @classmethod
    # def get_by_integer(cls, integer):
    #     return db.session.query(cls).filter_by(sample_integer=sample_integer).first()

    # @classmethod
    # def get_all_entities(cls):
    #     return db.session.query(cls).all()

    # @classmethod
    # def web_list(cls, req):
    #     try:
    #         ret = {}
    #         page = 1
    #         page_size = 30
    #         job_id = ''
    #         search = ''
    #         category = ''
    #         if 'page' in req.form:
    #             page = int(req.form['page'])
    #         if 'search_word' in req.form:
    #             search = req.form['search_word']
    #         if 'order' in req.form:
    #             order = req.form['order']

    #         query = cls.make_query(search=search, order=order)
    #         count = query.count()
    #         query = query.limit(page_size).offset((page-1)*page_size)
    #         logger.debug('cls count:%s', count)
    #         lists = query.all()
    #         ret['list'] = [item.as_dict() for item in lists]
    #         ret['paging'] = Util.get_paging_info(count, page, page_size)
    #         return ret
    #     except Exception as e:
    #         logger.error('Exception:%s', e)
    #         logger.error(traceback.format_exc())

    # @classmethod
    # def make_query(cls, search='', order='desc'):
    #     query = db.session.query(cls)
    #     if search is not None and search != '':
    #         if search.find('|') != -1:
    #             tmp = search.split('|')
    #             conditions = []
    #             for tt in tmp:
    #                 if tt != '':
    #                     conditions.append(cls.sample_string.like('%'+tt.strip()+'%') )
    #             query = query.filter(or_(*conditions))
    #         elif search.find(',') != -1:
    #             tmp = search.split(',')
    #             for tt in tmp:
    #                 if tt != '':
    #                     query = query.filter(cls.sample_string.like('%'+tt.strip()+'%'))
    #         else:
    #             query = query.filter(cls.sample_string.like('%'+search+'%'))

    #     if order == 'desc': query = query.order_by(desc(cls.id))
    #     else: query = query.order_by(cls.id)
    #     return query 

class ModelDownloadList(db.Model):
    __tablename__ = '%s_DownloadList' % package_name
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime)
    reserved = db.Column(db.JSON)
    # 사용할 필드 정의
    downloadType = db.Column(db.String)
    downloadDetail = db.Column(db.String)
    downalodCnt = db.Column(db.Integer)
    downalodAllCnt = db.Column(db.Integer)
    downalodStartDate = db.Column(db.DateTime)
    downalodEndDate = db.Column(db.DateTime)
    downalodStatus = db.Column(db.String)
    
    def __init__(self):
        self.created_time = datetime.now()
        
    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        ret = {x.name: getattr(self, x.name) for x in self.__table__.columns}
        ret['created_time'] = self.created_time.strftime('%m-%d %H:%M:%S') 
        return ret

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def delete(cls, id):
        db.session.query(cls).filter_by(id=id).delete()
        db.session.commit()

    @classmethod
    def getNextId(cls):
        return db.session.query(cls).count()+1

    @classmethod
    def get_by_id(cls, id):
        return db.session.query(cls).filter_by(id=id).first()
    
    @classmethod
    def get_by_albumId(cls, albumId):
        return db.session.query(cls).filter_by(albumId=albumId).first()
    
    @classmethod
    def get_by_typeByAlbumId(cls, albumType, albumId):
        return db.session.query(cls).filter_by(albumType=albumType,albumId=albumId).first()

    # @classmethod
    # def get_by_integer(cls, integer):
    #     return db.session.query(cls).filter_by(sample_integer=sample_integer).first()

    # @classmethod
    # def get_all_entities(cls):
    #     return db.session.query(cls).all()

    @classmethod
    def web_list(cls):
        try:
            ret = {}
            page = 1
            page_size = 30
            job_id = ''
            search = ''
            category = ''
            # if 'page' in req.form:
            #     page = int(req.form['page'])
            # if 'search_word' in req.form:
            #     search = req.form['search_word']
            # if 'order' in req.form:
            #     order = req.form['order']

            query = cls.make_query(search=search, order='desc')
            count = query.count()
            query = query.limit(page_size).offset((page-1)*page_size)
            logger.debug('cls count:%s', count)
            lists = query.all()
            for list in lists:
                list.downalodStartDate = list.downalodStartDate.strftime('%m-%d %H:%M:%S')
                if list.downalodEndDate is not None:
                    list.downalodEndDate = list.downalodEndDate.strftime('%m-%d %H:%M:%S')
                
            ret['list'] = [item.as_dict() for item in lists]
            ret['paging'] = Util.get_paging_info(count, page, page_size)
            return ret
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @classmethod
    def make_query(cls, search='', order='desc'):
        query = db.session.query(cls)
        if search is not None and search != '':
            if search.find('|') != -1:
                tmp = search.split('|')
                conditions = []
                for tt in tmp:
                    if tt != '':
                        conditions.append(cls.sample_string.like('%'+tt.strip()+'%') )
                query = query.filter(or_(*conditions))
            elif search.find(',') != -1:
                tmp = search.split(',')
                for tt in tmp:
                    if tt != '':
                        query = query.filter(cls.sample_string.like('%'+tt.strip()+'%'))
            else:
                query = query.filter(cls.sample_string.like('%'+search+'%'))

        if order == 'desc': query = query.order_by(desc(cls.id))
        else: query = query.order_by(cls.id)
        return query 
