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

class LogicSample(LogicModuleBase):
    db_default = {
        'db_version' : '1',
        # 스케쥴러
        'sample_interval'   : '60',
        'sample_auto_start' : 'False',

        # 유형별 설정값
        'sample_boolean'    : 'True',
        'sample_text'       : u'텍스트 설정값',
        'sample_path'       : os.path.join(path_data, package_name),
        'sample_integer'    : u'30',
        'sample_list'       : u'가|나|다|라|마',
    }

    def __init__(self, P):
        super(LogicSample, self).__init__(P, 'setting') # 해당모듈의 기본 sub
        self.name = 'sample'    # 모듈명

    # 플러그인 로딩시 실행할 내용이 있으면 작성
    def plugin_load(self):
        self.db_migration()
        self.initialize()

    def process_menu(self, sub, req):
        # 각 메뉴들이 호출될때 필요한 값들을 arg에 넘겨주어야함
        arg = P.ModelSetting.to_dict()
        arg['sub'] = self.name
        P.logger.debug('sub:%s', sub)
        if sub == 'setting':    # 설정페이지의 경우 스케쥴러 포함여부와 실행상태 전달
            job_id = '%s_%s' % (self.P.package_name, self.name)
            arg['scheduler'] = str(scheduler.is_include(job_id))
            arg['is_running'] = str(scheduler.is_running(job_id))
        return render_template('{package_name}_{module_name}_{sub}.html'.format(package_name=P.package_name, module_name=self.name, sub=sub), arg=arg)

    # 각 페이지에서의 요청 처리
    def process_ajax(self, sub, req):
        try:
            ret = {'ret':'success', 'data':[]}
            logger.debug('AJAX %s', sub)
            #logger.debug(req.form)
            if sub == 'register_item':
                ret = LogicSample.register_item(req.form)
            elif sub == 'modify_item':
                ret = LogicSample.modify_item(req.form)
            elif sub == 'delete_item':
                ret = LogicSample.delete_item(req.form)
            elif sub == 'web_list':
                ret = ModelSampleItem.web_list(req)
            return jsonify(ret)

        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return jsonify({'ret':'exception', 'msg':str(e)})

    # 스케쥴러에 의한 메인 로직 작동
    def scheduler_function(self):
        logger.debug('scheduler function!!!!!!!!!!!!!!')
        if app.config['config']['use_celery']:
            result = LogicSample.task.apply_async()
            result.get()
        else:
            LogicSample.task()

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

    #@staticmethod
    @celery.task
    def task():
        try:
            # 여기다 로직 구현
            logger.debug('main process started!!!!')
            
            # 설정값 접근 및 출력 예제
            # Boolean 값
            sample_boolean = ModelSetting.get_bool('sample_boolean')
            if sample_boolean: logger.debug('sample_boolean: True')
            else: logger.debug('sample_boolean: False')

            # 텍스트 값
            sample_text = ModelSetting.get('sample_text')
            logger.debug('sample_text: %s', sample_text)

            # 숫자값
            sample_integer = ModelSetting.get_int('sample_integer')
            logger.debug('sample_int : %s', sample_integer)

            # 리스트 처리-1
            sample_pathes = ModelSetting.get_list('sample_path', ',')
            for path in sample_pathes:
                logger.debug('sample_path: %s', path)

            # 리스트 처리-2
            sample_list = ModelSetting.get_list('sample_list', '|')
            for item in sample_list:
                logger.debug('sample_item: %s', item)

        except Exception as e:
            logger.debug('Exception:%s', e)
            logger.debug(traceback.format_exc())


    #########################################################
    # 필요함수 정의 및 구현부분
    @staticmethod
    def register_item(req):
        try:
            string = req['sample_string']
            integer = int(req['sample_integer'])
            boolean =  True if req['sample_boolean'] == 'True' else False
            imgurl = req['sample_imgurl']

            entity = ModelSampleItem(string, integer, boolean, imgurl)
            entity.save()

            return {'ret':'success', 'msg':'아이템 등록완료'}
        except Exception as e:
            logger.debug('Exception:%s', e)
            logger.debug(traceback.format_exc())
            return {'ret':'error', 'msg':str(e)}

    @staticmethod
    def modify_item(req):
        try:
            item_id = int(req['item_id'])

            entity = ModelSampleItem.get_by_id(item_id)
            entity.sample_string = req['sample_string']
            entity.sample_integer = int(req['sample_integer'])
            entity.sample_boolean = True if req['sample_boolean'] == 'True' else False
            entity.sample_imgurl = req['sample_imgurl']
            entity.save()

            return {'ret':'success', 'msg':'아이템 수정완료'}
        except Exception as e:
            logger.debug('Exception:%s', e)
            logger.debug(traceback.format_exc())
            return {'ret':'error', 'msg':str(e)}

    @staticmethod
    def delete_item(req):
        try:
            item_id = int(req['item_id'])

            entity = None
            entity = ModelSampleItem.get_by_id(item_id)
            if entity == None:
                return {'ret':'error', 'msg':'아이템이 존재하지 않습니다'}
            entity.delete(entity.id)
            return {'ret':'success', 'msg':'아이템 삭제완료'}
        except Exception as e:
            logger.debug('Exception:%s', e)
            logger.debug(traceback.format_exc())
            return {'ret':'error', 'msg':str(e)}


#########################################################
# DB 모델 정의: @classmethod 사용
class ModelSampleItem(db.Model):
    __tablename__ = '%s_item' % package_name
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime)
    reserved = db.Column(db.JSON)
    # 사용할 필드 정의
    sample_string = db.Column(db.String)
    sample_integer = db.Column(db.Integer)
    sample_boolean = db.Column(db.Boolean)
    sample_imgurl = db.Column(db.String)

    def __init__(self, string, integer, boolean, imgurl):
        self.created_time = datetime.now()
        self.sample_string = py_unicode(string)
        self.sample_integer = integer
        self.sample_boolean = boolean
        self.sample_imgurl = imgurl

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
    def get_by_string(cls, string):
        return db.session.query(cls).filter_by(sample_string=sample_string).first()

    @classmethod
    def get_by_integer(cls, integer):
        return db.session.query(cls).filter_by(sample_integer=sample_integer).first()

    @classmethod
    def get_all_entities(cls):
        return db.session.query(cls).all()

    @classmethod
    def web_list(cls, req):
        try:
            ret = {}
            page = 1
            page_size = 30
            job_id = ''
            search = ''
            category = ''
            if 'page' in req.form:
                page = int(req.form['page'])
            if 'search_word' in req.form:
                search = req.form['search_word']
            if 'order' in req.form:
                order = req.form['order']

            query = cls.make_query(search=search, order=order)
            count = query.count()
            query = query.limit(page_size).offset((page-1)*page_size)
            logger.debug('cls count:%s', count)
            lists = query.all()
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
