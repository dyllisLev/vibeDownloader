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

class LogicDownload(LogicModuleBase):
    
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Whale/2.7.100.20 Safari/537.36','sec-ch-ua': '"Chromium";v="86", "\"Not\\A;Brand";v="99", "Whale";v="2"'}
    # headers = {':authority': 'apis.naver.com',
    #            ':method': 'GET',
    #            ':path': '/nmwebplayer/musicapiweb/device/VIBE_WEB/deviceId',
    #            ':scheme': 'https',
    # headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #            'accept-encoding': 'gzip, deflate, br',
    #            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    #            'cache-control': 'max-age=0',
    #            'cookie': 'NNB=3QARWPW6A4PGA; NRTK=ag#all_gr#1_ma#-2_si#0_en#0_sp#0; ASID=dd8ac2c40000017811b4d63900000063; MM_NEW=1; NFS=2; MM_NOW_COACH=1; _ga_7VKFYR6RV1=GS1.1.1618118451.11.0.1618118451.60; NV_WETR_LOCATION_RGN_M="MDk3MTAxMDQ="; _fbp=fb.1.1623667116383.1120077572; NV_WETR_LAST_ACCESS_RGN_M="MDk3MTAxMDQ="; _gid=GA1.2.1062218854.1626619459; NDARK=N; nid_inf=508779156; NID_AUT=878rvxC5BR5vtLg+4Gg03qaRXMpSB+rFe13yKKJiN/tWgo2KF9ouzXT5gPxOyR74; NID_JKL=1KsBi0zoMJ9egg6GVh3MnQGiVt+Lt2RHhy7/GoIYNgM=; X-Tx-Id=144d731e-750a-4d9b-966d-4f856a7f3e49; _ga=GA1.2.51896110.1626336485; NID_SES=AAABrlk04ldWViyN1pI/HclReYXsiNfa3pQm8JX6zCZLw5otoSj3fRGAkA1wVecvCSHFuQdVQUpIGEugtwZmr/7OKmMMvyPaP7q1YbZEgKq9UjCJxtFBtdpvZPDRdCmcf4SoW3eSu/JAcH7X0b9D+wHq0Cp54ksTF4wGK+oEHcDQ4aGC4IrQq74sLqLMvA0YTh68Hn91w7kTXiU7/ryPwhVBuwC+KQ6J/uVuedmCYVxhCtvldBgy2TsAyfVgD4YJItRz1gZofJc+hW4umT8R+oYzEHjWuvdMMhTxmTijiWHucM2d3psvXwHeB0lMaJSZ2jGN1vgD9rkFifMUIaaOg4oqSbeMgfAeBJJGf6RScZMFVP4r0d/IFSoaGy++v1chXXTwe/ov2JuxoyJj9kCB1BeJhCgiX3ENqYcLhKIArzRCHmlgIOzGofN6unMzWhFxDf3SJOj2K5MZBEJY4bSANdTLyGh7wklB3IcxCMUOZVxmhhecLJqHE8xDJcvKwt5jFOlxQxuT5bKQuWc/+zf6dQ79b55F7NpgK343mVSV/4wVz5n9Zvse/vB0ad4z+pW8Zsn0Xg==; JSESSIONID=AF0438B58F03428DB9031B6A35A467C4; _ga_4BKHBFKFK0=GS1.1.1626656647.38.1.1626656762.12',
    #            'sec-ch-ua': '"Chromium";v="86", "\"Not\\A;Brand";v="99", "Whale";v="2"',
    #            'sec-ch-ua-mobile': '?0',
    #            'sec-fetch-dest': 'document',
    #            'sec-fetch-mode': 'navigate',
    #            'sec-fetch-site': 'none',
    #            'sec-fetch-user': '?1',
    #            'upgrade-insecure-requests': '1',
    #            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Whale/2.7.100.20 Safari/537.36','sec-ch-ua': '"Chromium";v="86", "\"Not\\A;Brand";v="99", "Whale";v="2"'}
    # deviceId = LogicDownload.getDeviceId()
    data = None
    session = None
    
    def __init__(self, P):
        super(LogicDownload, self).__init__(P, 'TOP100') # 해당모듈의 기본 sub
        self.name = 'download'    # 모듈명

    # 플러그인 로딩시 실행할 내용이 있으면 작성
    def plugin_load(self):
        # self.db_migration()
        # self.initialize()
        P.logger.debug('plugin_load')

    def process_menu(self, sub, req):
        # 각 메뉴들이 호출될때 필요한 값들을 arg에 넘겨주어야함
        arg = P.ModelSetting.to_dict()
        arg['sub'] = self.name
        P.logger.debug('sub:%s', sub)
        import random
        arg['v'] = random.random()
        P.logger.debug('{package_name}_{module_name}_{sub}.html'.format(package_name=P.package_name, module_name=self.name, sub=sub))
        return render_template('{package_name}_{module_name}_{sub}.html'.format(package_name=P.package_name, module_name=self.name, sub=sub), arg=arg)

    # 각 페이지에서의 요청 처리
    def process_ajax(self, sub, req):
        try:
            ret = {'ret':'success', 'data':[]}
            logger.debug('AJAX %s', sub)
            
            ################################################
            ##################다운로드 시작##################
            ################################################
            #한곡 다운로드
            if sub == 'musicDownloadById':
                ret = LogicDownload.musicDownloadById(req.form)
            #전체 다운로드
            elif sub == 'allDownload':
                ret = LogicDownload.allDownload(req.form)
            ################################################
            ##################다운로드 종료##################
            ################################################

            ################################################
            ##################조회영역 시작##################
            ################################################
            elif sub == 'top100':
                ret = LogicDownload.top100List(req.form)
            elif sub == 'new':
                ret = LogicDownload.newalbum(req.form)
            elif sub == 'albumInfo':
                ret = LogicDownload.albumInfo(req.form)
            elif sub == 'artistInfo':
                ret = LogicDownload.artistInfo(req.form)
            elif sub == 'search':
                ret = LogicDownload.search(req.form)
            elif sub == 'searchByTrack':
                ret = LogicDownload.searchByTrack(req.form)
            elif sub == 'searchByAlbum':
                ret = LogicDownload.searchByAlbum(req.form)
            elif sub == 'musicPlay':
                ret = LogicDownload.musicPlay(req.form)
            elif sub == 'select':
                ret = LogicDownload.downloadList()
            ################################################
            ##################조회영역 끝##################
            ################################################
                
            #     ret = LogicDownload.register_item(req.form)
            # elif sub == 'modify_item':
            #     ret = LogicDownload.modify_item(req.form)
            # elif sub == 'delete_item':
            #     ret = LogicDownload.delete_item(req.form)
            # elif sub == 'web_list':
            #     ret = ModelItem.web_list(req)
            return jsonify(ret)

        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return jsonify({'ret':'exception', 'msg':str(e)})

    # 스케쥴 요청처리
    @celery.task
    def task():
        try:
            # 여기다 로직 구현
            logger.debug('LogicDownload main process started!!!!')
            if P.ModelSetting.get("top100Download1") == "True":
                P.ModelSetting.set("top100Key", "1")
                LogicDownload.musicDownloadTOP100()
            if P.ModelSetting.get("top100Download2") == "True":
                P.ModelSetting.set("top100Key", "2")
                LogicDownload.musicDownloadTOP100()
            if P.ModelSetting.get("top100Download3") == "True":
                P.ModelSetting.set("top100Key", "3")
                LogicDownload.musicDownloadTOP100()
            if P.ModelSetting.get("top100Download4") == "True":
                P.ModelSetting.set("top100Key", "4")
                LogicDownload.musicDownloadTOP100()
            if P.ModelSetting.get("top100Download5") == "True":
                P.ModelSetting.set("top100Key", "5")
                LogicDownload.musicDownloadTOP100()
            if P.ModelSetting.get("top100Download6") == "True":
                P.ModelSetting.set("top100Key", "6")
                LogicDownload.musicDownloadTOP100()
            if P.ModelSetting.get("top100Download7") == "True":
                P.ModelSetting.set("top100Key", "7")
                LogicDownload.musicDownloadTOP100()
            if P.ModelSetting.get("top100Download8") == "True":
                P.ModelSetting.set("top100Key", "8")
                LogicDownload.musicDownloadTOP100()
            if P.ModelSetting.get("top100Download9") == "True":
                P.ModelSetting.set("top100Key", "9")
                LogicDownload.musicDownloadTOP100()
            if P.ModelSetting.get("newAlbumDownload1") == "True":
                LogicDownload.musicDownloadNewAlbum(1)
            if P.ModelSetting.get("newAlbumDownload2") == "True":
                LogicDownload.musicDownloadNewAlbum(2)
            if P.ModelSetting.get("newAlbumDownload3") == "True":
                LogicDownload.musicDownloadNewAlbum(3)
            
            logger.debug('LogicDownload main process END!!!!')
            
        except Exception as e:
            logger.debug('Exception:%s', e)
            logger.debug(traceback.format_exc())


    # #########################################################
    # def db_migration(self):
    #     try:
    #         # db 마이그레이션: 필요한 경우에 작성 
    #         # ex) 배포 후 버전업에 따라 DB에 필드의 추가가 필요하거나 할떄 사용 설정의 db_version을 업데이트 하며 사용
    #         pass
    #     except Exception as e:
    #         logger.debug('Exception:%s', e)
    #         logger.debug(traceback.format_exc())

    # def initialize(self):
    #     try:
    #         # 플러그인 로딩시 실행할 것들: Thread나 Queue 생성, 전역변수나 설정값들 초기화 등 처리
    #         pass
    #     except Exception as e: 
    #         P.logger.error('Exception:%s', e)
    #         P.logger.error(traceback.format_exc())
    #         return

    # #########################################################
    # 필요함수 정의 및 구현부분


    # #########################################################
    # ###################조회영역 시작##########################
    # #########################################################
    @staticmethod
    def musicPlay(req):

        trackId = req['trackId'];

        LogicDownload.session = LogicDownload.naver_login()

        resp = LogicDownload.session.post('https://apis.naver.com/nmwebplayer/music/stplay_trackStPlay_NO_HMAC?play.trackId='+trackId+'&deviceType=VIBE_WEB&&deviceId=VIBE_WEB&play.mediaSourceType=AAC_320_ENC', data=LogicDownload.data, headers=LogicDownload.headers)
        rj = resp.json()
        musicDownloadUrl = rj["moduleInfo"]["hlsManifestUrl"]

        return {'ret':'success', 'musicUrl':musicDownloadUrl}

    @staticmethod
    def searchByTrack(req):

        keyword = req['keyword']
        start = req['start']
        logger.debug(keyword)
        
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/v3/search/track?query='+keyword+'&start='+start+'&sort=RELEVANCE')
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            trackInfo = json.dumps(dictionary) 
        return {'ret':'success', 'trackInfo':json.loads(trackInfo)['response']['result']}
    
    @staticmethod
    def searchByAlbum(req):

        keyword = req['keyword']
        start = req['start']
        logger.debug(keyword)
        
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/v3/search/album?query='+keyword+'&start='+start+'&&sort=RELEVANCE')
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            albumInfo = json.dumps(dictionary) 
        return {'ret':'success', 'albumInfo':json.loads(albumInfo)['response']['result']}
    @staticmethod
    def search(req):

        keyword = req['keyword']
        logger.debug(keyword)
        
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/v3/search/track?query='+keyword+'&start=1&sort=RELEVANCE')
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            trackInfo = json.dumps(dictionary) 
        
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/v3/search/album?query='+keyword+'&start=1&&sort=RELEVANCE')
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            albumInfo = json.dumps(dictionary) 
        
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/v3/search/artist?query='+keyword+'&start=1&&sort=RELEVANCE')
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            artistInfo = json.dumps(dictionary) 
        return {'ret':'success', 'trackInfo':json.loads(trackInfo)['response']['result'], 'albumInfo':json.loads(albumInfo)['response']['result'], 'artistInfo':json.loads(artistInfo)['response']['result']}
    
    @staticmethod
    def top100List(req):

        key = req['top100Key']
        logger.debug("key : " + key)
        
        url = ''

        if key == '1':
            url = 'https://apis.naver.com/vibeWeb/musicapiweb/vibe/v1/chart/track/total'
        elif key == '2':
            url = 'https://apis.naver.com/vibeWeb/musicapiweb/vibe/v1/chart/track/domestic'
        elif key == '3':
            url = 'https://apis.naver.com/vibeWeb/musicapiweb/vibe/v1/chart/billboard/kpop'
        elif key == '4':
            url = 'https://apis.naver.com/vibeWeb/musicapiweb/vibe/v1/chart/track/oversea'
        elif key == '5':
            url = 'https://apis.naver.com/vibeWeb/musicapiweb/chart/billboard/track'
        elif key == '6':
            url = 'https://apis.naver.com/vibeWeb/musicapiweb/chart/karaoke'
        elif key == '7':
            url = 'https://apis.naver.com/vibeWeb/musicapiweb/vibe/v1/chart/track/genres/DS102'
        elif key == '8':
            url = 'https://apis.naver.com/vibeWeb/musicapiweb/vibe/v1/chart/track/genres/DS103'
        elif key == '9':
            url = 'https://apis.naver.com/vibeWeb/musicapiweb/vibe/v1/chart/track/search'


        resp = requests.get(url)
    
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            json_object = json.dumps(dictionary) 
        return {'ret':'success', 'content':json.loads(json_object)}
    
    @staticmethod
    def albumInfo(req):

        albumId = req['albumId']

        
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/album/'+albumId)
    
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            albumInfo = json.dumps(dictionary) 
        
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/album/'+albumId+'/tracks?start=1&display=1000')
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            albumTrack = json.dumps(dictionary) 

            
        return {'ret':'success', 'albumInfo':json.loads(albumInfo), 'albumTracks':json.loads(albumTrack)}
    
    @staticmethod
    def artistInfo(req):

        artistId = req['artistId']
        logger.debug( artistId )
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/v1/artist/'+artistId)
    
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            artistInfo = json.dumps(dictionary)
        
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/v1/artist/'+artistId+'/tracks?display=9999&sort=popular')
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            artistTrack = json.dumps(dictionary)

            
        return {'ret':'success', 'artistInfo':json.loads(artistInfo), 'artistTrack':json.loads(artistTrack)}

    @staticmethod
    def newalbum(req):

        searchType = req['search']
        url = ""
        if searchType == "국내":
            url = "https://apis.naver.com/vibeWeb/musicapiweb/chart/domain/DOMESTIC/newrelease/albumChart?start=1&display=50"
        elif searchType == "해외":
            url = "https://apis.naver.com/vibeWeb/musicapiweb/chart/domain/OVERSEA/newrelease/albumChart?start=1&display=50"
        elif searchType == "모든앨범":
            url = "https://apis.naver.com/vibeWeb/musicapiweb/chart/newrelease/totalAlbumChart?start=51"
        
        resp = requests.get(url)    
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            json_object = json.dumps(dictionary) 
        return {'ret':'success', 'content':json.loads(json_object)}

    @staticmethod
    def downloadList():
        from .setting import ModelDownloadList
        return ModelDownloadList.web_list()

    # #########################################################
    # ###################조회영역 끝############################
    # #########################################################
    @staticmethod
    def musicDownloadById(req):
        
        trackId = req['trackId']
        downloadType = req['type']
        
        trackInfo = None
        result = False
        
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/track/'+trackId)
        if resp.status_code == 200 :
            dictionary = xmltodict.parse(resp.text)
            trackInfo = json.loads(json.dumps(dictionary))

            data = {'type':'success', 'msg':trackInfo['response']['result']['track']['trackTitle'] + ' 다운로드 시작.'}
            socketio.emit('notify', data, namespace='/framework', broadcast=True)
            
            downInfo = {'type':downloadType,'detail':trackInfo['response']['result']['track']['trackTitle'],'cnt': 0, 'allCnt':1, 'downalodStatus' : '다운로드중'}
            id = LogicDownload.insertDownList(downInfo)
            logger.debug("id : %s", id)
            thread = threading.Thread(target=LogicDownload.musicDownload, args=(trackInfo['response']['result']['track'], downloadType, None, id))
            thread.setDaemon(True)
            thread.start()
            

    @staticmethod
    def allDownload(req):
        
        downloadType = req['type']
        
        if downloadType == "TOP100":
            logger.debug(req)
            P.ModelSetting.set("top100Key", req['top100Key'])
            thread = threading.Thread(target=LogicDownload.musicDownloadTOP100, args=())
            thread.setDaemon(True)
            thread.start()
        elif downloadType == "album":
            P.ModelSetting.set("albumId", req['albumId'])
            thread = threading.Thread(target=LogicDownload.musicDownloadAlbum, args=())
            thread.setDaemon(True)
            thread.start()
        elif downloadType == "artist":
            P.ModelSetting.set("artistId", req['artistId'])
            thread = threading.Thread(target=LogicDownload.musicDownloadArtist, args=())
            thread.setDaemon(True)
            thread.start()
        return {'ret':'success'}

    
    
    @staticmethod
    def musicDownloadNewAlbum(type):
        logger.debug('LogicDownload musicDownloadNewAlbum process started!!!!')

        
        info = None
        if type == 1:
            req = {'search':'국내'}
            info = LogicDownload.newalbum(req)
        elif type == 2:
            req = {'search':'해외'}
            info = LogicDownload.newalbum(req)
        elif type == 3:
            req = {'search':'모든앨범'}
            info = LogicDownload.newalbum(req)

        from .setting import LogicSetting, ModelAutoAlbum
        
        for album in info['content']['response']['result']['chart']['albums']['album']:
            try:
                if ModelAutoAlbum.get_by_typeByAlbumId(req['search'], album['albumId']) is None:
                    P.ModelSetting.set("albumId", album['albumId'])
                    LogicDownload.musicDownloadAlbum()
                    entity = ModelAutoAlbum(req['search'], album['albumId'])
                    entity.save()
                    logger.debug("다운로드!")
                else:
                    logger.debug("이미 다운로드!")

            except Exception as e:
                logger.debug('Exception:%s', e)
                logger.debug(traceback.format_exc())

        # from framework import socketio
        # data = {'type':'success', 'msg':'최신앨범 다운로드 완료.'}
        # socketio.emit('notify', data, namespace='/framework', broadcast=True)
        
        logger.debug('LogicDownload musicDownloadNewAlbum process END!!!!')
    
    
    @staticmethod
    def musicDownloadTOP100():
        logger.debug('LogicDownload musicDownloadTOP100 process started!!!!')

        info = LogicDownload.top100List(P.ModelSetting.to_dict())
        
        downInfo = {'type':"TOP100",'detail':LogicDownload.getTop100Title(P.ModelSetting.to_dict()['top100Key']),'cnt': 0, 'allCnt':info['content']['response']['result']['chart']['items']['trackTotalCount'], 'downalodStatus' : '다운로드중'}
        id = LogicDownload.insertDownList(downInfo)
        
        cnt = 1
        for track in info['content']['response']['result']['chart']['items']['tracks']['track']:
            try:
                result = LogicDownload.musicDownload(track, "TOP100", topRank=cnt)
                cnt = cnt + 1

                downInfo = {'id':id, 'downalodCnt': cnt}
                LogicDownload.updateDownList(downInfo)
            except Exception as e:
                logger.debug('Exception:%s', e)
                logger.debug(traceback.format_exc())

        data = {'type':'success', 'msg':'TOP100 다운로드 완료.'}
        socketio.emit('notify', data, namespace='/framework', broadcast=True)

        downInfo = {'id':id, 'downalodCnt': info['content']['response']['result']['chart']['items']['trackTotalCount'], 'downalodEndDate': datetime.now(), 'downalodStatus' : '종료'}
        LogicDownload.updateDownList(downInfo)
        
        logger.debug('LogicDownload musicDownloadTOP100 process END!!!!')
    
    @staticmethod
    def musicDownloadAlbum():
        logger.debug('LogicDownload musicDownloadAlbum process started!!!!')
        
        info = LogicDownload.albumInfo(P.ModelSetting.to_dict())
        downInfo = {'type':"앨범",'detail':info['albumInfo']['response']['result']['album']['albumTitle'],'cnt': 0, 'allCnt':info['albumTracks']['response']['result']['trackTotalCount'], 'downalodStatus' : '다운로드중'}
        id = LogicDownload.insertDownList(downInfo)

        cnt = 0
        if info['albumTracks']['response']['result']['trackTotalCount'] == "1" :
            track = info['albumTracks']['response']['result']['tracks']['track']
            result = LogicDownload.musicDownload(track, "album")

            cnt = cnt + 1
            downInfo = {'id':id, 'downalodCnt': cnt}
            LogicDownload.updateDownList(downInfo)
        else:
            try:
                for track in info['albumTracks']['response']['result']['tracks']['track']:
                    
                    result = LogicDownload.musicDownload(track, "album")
                    cnt = cnt + 1
                    downInfo = {'id':id, 'downalodCnt': cnt}
                    LogicDownload.updateDownList(downInfo)

            except Exception as e:
                logger.debug('Exception:%s', e)
                logger.debug(traceback.format_exc())
        
        downInfo = {'id':id, 'downalodCnt': info['albumTracks']['response']['result']['trackTotalCount'], 'downalodEndDate': datetime.now(), 'downalodStatus' : '종료'}
        LogicDownload.updateDownList(downInfo)
        data = {'type':'success', 'msg':'앨범 다운로드 완료.'}
        socketio.emit('notify', data, namespace='/framework', broadcast=True)
        
        logger.debug('LogicDownload musicDownloadAlbum process END!!!!')
    
    @staticmethod
    def musicDownloadArtist():
        logger.debug('LogicDownload musicDownloadArtist process started!!!!')
        
        info = LogicDownload.artistInfo(P.ModelSetting.to_dict())

        downInfo = {'type':"가수",'detail':info['artistInfo']['response']['result']['artist']['artistName'],'cnt': 0, 'allCnt':info['artistTrack']['response']['result']['trackTotalCount'], 'downalodStatus' : '다운로드중'}
        id = LogicDownload.insertDownList(downInfo)

        cnt = 0
        for track in info['artistTrack']['response']['result']['tracks']['track']:
            try:
                result = LogicDownload.musicDownload(track, "artist")

                cnt = cnt + 1
                downInfo = {'id':id, 'downalodCnt': cnt}
                LogicDownload.updateDownList(downInfo)
            except Exception as e:
                logger.debug('Exception:%s', e)
                logger.debug(traceback.format_exc())
        
        data = {'type':'success', 'msg':'가수별 다운로드 완료.'}
        socketio.emit('notify', data, namespace='/framework', broadcast=True)
        downInfo = {'id':id, 'downalodCnt': info['artistTrack']['response']['result']['trackTotalCount'], 'downalodEndDate': datetime.now(), 'downalodStatus' : '종료'}
        LogicDownload.updateDownList(downInfo)
        logger.debug('LogicDownload musicDownloadArtist process END!!!!')

#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################
    # 다운로드 모듈
    @staticmethod
    def musicDownload(track, type, topRank=None, id=None):

        info = LogicDownload.getDownloadFilePath(track, type, topRank)
        trackId = LogicDownload.download(info)
        if trackId != False:
            LogicDownload.setMetadata(trackId)
            LogicDownload.moveMusic(info)

        if type == "track":
            data = {'type':'success', 'msg':track['trackTitle'] + ' 다운로드 완료.'}
            socketio.emit('notify', data, namespace='/framework', broadcast=True)

            logger.debug(id)
            downInfo = {'id':id, 'downalodCnt': 1, 'downalodEndDate': datetime.now(), 'downalodStatus' : '종료'}
            LogicDownload.updateDownList(downInfo)

        return True

    @staticmethod
    def getDownloadFilePath(track, type, topRank=None):

        # logger.debug(track)
        trackId = track['trackId']
        trackTitle = track['trackTitle']
        
        albumTitle  = track['album']['albumTitle'].replace('/', '')
        trackNumber = track['trackNumber']
        trackNumber = str(trackNumber).rjust(2,"0")
        discNumber  = track['discNumber']
        discNumber  = str(discNumber).rjust(2,"0")

        trackTitle  = track['trackTitle'].replace('/', '')
        artist      = ''

        if track['artistTotalCount'] == "1" :
            artist = track['artists']['artist']['artistName']
        else:
            for artistTmp in track['artists']['artist']:
                if artist != '' :
                    artist = artist + ", "
                artist = artist + artistTmp['artistName']
        
        artist = artist.replace('/', '')
        
        yyyy = datetime.today().year        # 현재 연도 가져오기
        mm = str(datetime.today().month).rjust(2,"0") # 현재 월 가져오기
        dd = str(datetime.today().day).rjust(2,"0") # 현재 일 가져오기
        today = str(yyyy) +"-"+ str(mm) +"-"+ str(dd)
        
        fileName = ""
        savePath = ""

        if type == "track":
            savePath_base = P.ModelSetting.to_dict()['savePath']
            saveFileName = P.ModelSetting.to_dict()['saveFileName']

            savePath_base = savePath_base.replace('%albumTitle%', albumTitle)
            savePath_base = savePath_base.replace('%trackNumber%', trackNumber)
            savePath_base = savePath_base.replace('%trackTitle%', trackTitle)
            savePath_base = savePath_base.replace('%artist%', artist)
            savePath_base = savePath_base.replace('%today%', today)
            savePath_base = savePath_base.replace('%discNumber%', discNumber)
            
            saveFileName = saveFileName.replace('%albumTitle%', albumTitle)
            saveFileName = saveFileName.replace('%trackNumber%', trackNumber)
            saveFileName = saveFileName.replace('%trackTitle%', trackTitle)
            saveFileName = saveFileName.replace('%artist%', artist)
            saveFileName = saveFileName.replace('%today%', today)
            saveFileName = saveFileName.replace('%discNumber%', discNumber)
            
            fileName = saveFileName+".mp3"
            savePath = savePath_base
        elif type == "album":
            savePathByAlbum = P.ModelSetting.to_dict()['savePathByAlbum']
            saveFileNameByAlbum = P.ModelSetting.to_dict()['saveFileNameByAlbum']
            
            savePathByAlbum = savePathByAlbum.replace('%albumTitle%', albumTitle)
            savePathByAlbum = savePathByAlbum.replace('%trackNumber%', trackNumber)
            savePathByAlbum = savePathByAlbum.replace('%trackTitle%', trackTitle)
            savePathByAlbum = savePathByAlbum.replace('%artist%', artist)
            savePathByAlbum = savePathByAlbum.replace('%today%', today)
            savePathByAlbum = savePathByAlbum.replace('%discNumber%', discNumber)
            
            saveFileNameByAlbum = saveFileNameByAlbum.replace('%albumTitle%', albumTitle)
            saveFileNameByAlbum = saveFileNameByAlbum.replace('%trackNumber%', trackNumber)
            saveFileNameByAlbum = saveFileNameByAlbum.replace('%trackTitle%', trackTitle)
            saveFileNameByAlbum = saveFileNameByAlbum.replace('%artist%', artist)
            saveFileNameByAlbum = saveFileNameByAlbum.replace('%today%', today)
            saveFileNameByAlbum = saveFileNameByAlbum.replace('%discNumber%', discNumber)
            
            fileName = saveFileNameByAlbum+".mp3"
            savePath = savePathByAlbum
        
        elif type == "TOP100":

            if "rank" in track.keys() :
                rank = track['rank']['currentRank']
            else:
                rank = topRank
            
            rank = str(rank).rjust(3,"0")

            key = P.ModelSetting.to_dict()['top100Key']

            toptitle = LogicDownload.getTop100Title(key)
            
            savePathByTOP100 = P.ModelSetting.to_dict()['savePathByTOP100']
            saveFileNameByTOP100 = P.ModelSetting.to_dict()['saveFileNameByTOP100']
            
            savePathByTOP100 = savePathByTOP100.replace('%albumTitle%', albumTitle)
            savePathByTOP100 = savePathByTOP100.replace('%trackNumber%', trackNumber)
            savePathByTOP100 = savePathByTOP100.replace('%trackTitle%', trackTitle)
            savePathByTOP100 = savePathByTOP100.replace('%artist%', artist)
            savePathByTOP100 = savePathByTOP100.replace('%today%', today)
            savePathByTOP100 = savePathByTOP100.replace('%rank%', rank)
            savePathByTOP100 = savePathByTOP100.replace('%toptitle%', toptitle)
            savePathByTOP100 = savePathByTOP100.replace('%discNumber%', discNumber)
            
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%albumTitle%', albumTitle)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%trackNumber%', trackNumber)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%trackTitle%', trackTitle)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%artist%', artist)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%today%', today)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%rank%', rank)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%toptitle%', toptitle)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%discNumber%', discNumber)


            fileName = saveFileNameByTOP100+".mp3"
            savePath = savePathByTOP100
        
        elif type == "artist":

            savePathByArtist = P.ModelSetting.to_dict()['savePathByArtist']
            saveFileNameByArtist = P.ModelSetting.to_dict()['saveFileNameByArtist']
            
            savePathByArtist = savePathByArtist.replace('%albumTitle%', albumTitle)
            savePathByArtist = savePathByArtist.replace('%trackNumber%', trackNumber)
            savePathByArtist = savePathByArtist.replace('%trackTitle%', trackTitle)
            savePathByArtist = savePathByArtist.replace('%artist%', artist)
            savePathByArtist = savePathByArtist.replace('%today%', today)
            
            saveFileNameByArtist = saveFileNameByArtist.replace('%albumTitle%', albumTitle)
            saveFileNameByArtist = saveFileNameByArtist.replace('%trackNumber%', trackNumber)
            saveFileNameByArtist = saveFileNameByArtist.replace('%trackTitle%', trackTitle)
            saveFileNameByArtist = saveFileNameByArtist.replace('%artist%', artist)
            saveFileNameByArtist = saveFileNameByArtist.replace('%today%', today)
            
            fileName = saveFileNameByArtist+".mp3"
            savePath = savePathByArtist
        
        fileName = re.sub('[\\\:*?"<>|]','',fileName)
        savePath = re.sub('[\\\:*?"<>|]','',savePath)
        return {'trackId':trackId, 'path': os.path.join(savePath, fileName), 'albumTitle': albumTitle, 'trackNumber': trackNumber, 'trackTitle': trackTitle, 'artist': artist, 'type': type}

    @staticmethod
    def download(info):

        trackId = info['trackId']
        path = info['path']
        albumTitle = info['albumTitle']
        trackNumber = info['trackNumber']
        trackTitle = info['trackTitle']
        artist = info['artist']
        type = info['type']
        logger.debug("다운로드 시작" + trackId)
        logger.debug(P.ModelSetting.to_dict()['ffmpegDownload'])
        logger.debug( path )
        logger.debug( os.path.isfile( path ) )
        
        try:

            if os.path.isfile( path ) :
                logger.debug(path)
                logger.debug("이미 같은파일이 있음")
                return False
            else:
                
                LogicDownload.session = LogicDownload.naver_login()
                
                if not os.path.isdir(os.path.split(path)[0]):
                    os.makedirs(os.path.split(path)[0])
                
                resp = LogicDownload.session.post('https://apis.naver.com/nmwebplayer/music/stplay_trackStPlay_NO_HMAC?play.trackId='+trackId+'&deviceType=VIBE_WEB&deviceId=VIBE_WEB&play.mediaSourceType=AAC_320')
                rj = resp.json()
                # logger.debug(rj)
                musicDownloadUrl = rj["moduleInfo"]["hlsManifestUrl"]

                command = ['ffmpeg', '-i', str( musicDownloadUrl ), '-acodec', 'mp3', '-ab', '320k', os.path.join(path_data, 'tmp',trackId+".mp3")]
                logger.debug(command)
                output = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, encoding='utf-8')
                result = output.communicate()
                # logger.debug(result)
                
                
                if type != "track":
                    import time
                    delayTime = P.ModelSetting.to_dict()['delayTime']
                    time.sleep(int(delayTime))
                    
        except Exception as e: 
            logger.error("다운로드 오류 trackId : " + trackId)
            logger.error("다운로드 오류 type: " + type)
            logger.error("다운로드 오류 resp.text: " + resp.text)
            logger.error(traceback.format_exc())
            return False
        
        return trackId

    @staticmethod
    def setMetadata(trackId):

        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/track/'+trackId+'/info')
        filePath = os.path.join(path_data, 'tmp',trackId+".mp3")
        if resp.status_code == 200 :
            result = LogicDownload.parse_xml(resp.text)
            xml = ET.fromstring(resp.text)
            hasLyric = xml[0][0][1].text
            lyric = ""
            if hasLyric == "Y":
                cnt = 0
                while cnt < 10:
                    if os.path.isfile( filePath ):

                        lyric = xml[0][0][2].text
                        from mutagen.id3 import ID3, USLT
                        command = ['ffmpeg', '-i', filePath]
                        output = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, encoding='utf-8')
                        # logger.debug( output.communicate())
                        try:
                            audio = ID3(filePath)
                            audio.add(USLT(text=lyric, lang="kor", desc=""))
                            audio.save()
                        except Exception as e:
                            audio = ID3()
                            audio.add(USLT(text=lyric, lang="kor", desc=""))
                            audio.save(filePath)
                        
                        cnt = cnt + 10
                    else:
                        import time
                        time.sleep(1)
                    cnt = cnt + 1
    
    @staticmethod
    def moveMusic(info):

        trackId = info['trackId']
        filePath = info['path']

        if os.path.isfile( os.path.join(path_data, 'tmp',trackId+".mp3") ):
            shutil.move(os.path.join(path_data, 'tmp',trackId+".mp3") , filePath)
            
    @staticmethod
    def parse_xml(xml):
        return [dict([(j.tag, (j.text or list(filter(lambda l: l, [k.text for k in j.iter()])))) for j in i]) for i in ET.fromstring(xml)]
    
    @staticmethod
    def encrypt(naver_id, naver_pw):
        key_str = requests.get('https://nid.naver.com/login/ext/keys.nhn').content.decode("utf-8")
        sessionkey , Keyname, evalue, nvalue = key_str.split(',') 
        evalue, nvalue = int(evalue, 16), int(nvalue, 16)
        pubkey = rsa.PublicKey(evalue, nvalue)
        message = [sessionkey,naver_id,naver_pw]
        merge_message = ""
        for s in message:
            merge_message = merge_message + ''.join([chr(len(s)) + s])
        merge_message = merge_message.encode()
        encpw = rsa.encrypt(merge_message, pubkey).hex()
        return Keyname, encpw

    @staticmethod
    def naver_login():

        nid = P.ModelSetting.to_dict()['naverId']
        npw = P.ModelSetting.to_dict()['naverPw']
        
        lastloginTime = P.ModelSetting.to_dict()['lastloginTime']
        
        if float(datetime.now().timestamp()) - float(lastloginTime) > 10800 or LogicDownload.session is None:
            encnm, encpw = LogicDownload.encrypt(nid, npw)
            bvsd_uuid = uuid.uuid4()
            o = '{"a":"' + str(bvsd_uuid) + '","b":"1.3.4","h":"1f","i":{"a":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Whale/2.7.100.20 Safari/537.36"}}'  
            encData = lzstring.LZString.compressToEncodedURIComponent(o)
            bvsd = '{"uuid":"'+ str(bvsd_uuid) + '","encData":"'+ encData +'"}'
            session = requests.Session()
            
            LogicDownload.data = {
                'enctp': '1',
                'svctype': '0',
                'encnm': encnm,
                'locale' : 'ko_KR',
                'url': 'www.naver.com',
                'smart_level': '1',
                'encpw': encpw,
                'bvsd': bvsd
            }
            resp = session.post('https://nid.naver.com/nidlogin.login', data=LogicDownload.data, headers=LogicDownload.headers)

            from lxml.html import fromstring
            doc  = fromstring(resp.text)
            if(resp.text.find("location.replace")>-1):
                logger.debug("로그인 성공")
                P.ModelSetting.set("lastloginTime", str(datetime.now().timestamp()))
                return session
            else:
                logger.debug("로그인 실패")
                # logger.debug(resp.text)
                
                if(resp.text.find("자동입력 방지문자")>-1):
                    data = {'type':'danger', 'msg':'자동입력 방지활성화 직접로그인 후 재시도 하세요.'}
                else:
                    data = {'type':'danger', 'msg':'로그인 실패'}
                        
                socketio.emit('notify', data, namespace='/framework', broadcast=True)
                return None
        else:
            return LogicDownload.session
    
    @staticmethod
    def insertDownList(info):

        try:
            from .setting import ModelDownloadList    

            id = ModelDownloadList.getNextId()

            entity = ModelDownloadList()
            entity.id = id
            entity.downloadType = str(info['type'])
            entity.downloadDetail = str(info['detail'])
            entity.downalodCnt = info['cnt']
            entity.downalodAllCnt = info['allCnt']
            entity.downalodStartDate = datetime.now()
            
            db.session.add(entity)
            db.session.commit()
            return id
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
    
    @staticmethod
    def updateDownList(info):

        try:
            from .setting import ModelDownloadList    
            item = db.session.query(ModelDownloadList).filter_by(id=info['id']).with_for_update().first()
            if item is not None:
                for col in info.keys():
                    if col == "downalodCnt":
                        item.downalodCnt = info['downalodCnt']
                    if col == "downalodEndDate":
                        item.downalodEndDate = info['downalodEndDate']
                    if col == "downalodStatus":
                        item.downalodStatus = info['downalodStatus']
                db.session.commit()
            
        except Exception as e:
            logger.error('Exception:%s %s', e, key)
            logger.error(traceback.format_exc())

        except Exception as e:
            logger.error(d)
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def getTop100Title(key):
        if key == '1':
            toptitle = '오늘 TOP100'
        elif key == '2':
            toptitle = '국내 급상승'
        elif key == '3':
            toptitle = '빌보드 K-POP'
        elif key == '4':
            toptitle = '해외 급상승'
        elif key == '5':
            toptitle = '빌보드 HOT100'
        elif key == '6':
            toptitle = 'VIBE 노래방 TOP100'
        elif key == '7':
            toptitle = '국내 발라드 TOP100'
        elif key == '8':
            toptitle = '국내 댄스 TOP100'
        elif key == '9':
            toptitle = '음악검색 TOP100'
        return toptitle

