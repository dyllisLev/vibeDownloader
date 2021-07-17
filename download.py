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

# 패키지
from .plugin import P
logger = P.logger
package_name = P.package_name
ModelSetting = P.ModelSetting

#########################################################

class LogicDownload(LogicModuleBase):
    
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Whale/2.7.100.20 Safari/537.36'}
    data = None
    session = None
    def __init__(self, P):
        super(LogicDownload, self).__init__(P, 'TOP100') # 해당모듈의 기본 sub
        self.name = 'download'    # 모듈명

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
        P.logger.debug('{package_name}_{module_name}_{sub}.html'.format(package_name=P.package_name, module_name=self.name, sub=sub))
        return render_template('{package_name}_{module_name}_{sub}.html'.format(package_name=P.package_name, module_name=self.name, sub=sub), arg=arg)

    # 각 페이지에서의 요청 처리
    def process_ajax(self, sub, req):
        try:
            ret = {'ret':'success', 'data':[]}
            logger.debug('AJAX %s', sub)
            if sub == 'top100':
                ret = LogicDownload.top100List()
            elif sub == 'musicDownloadById':
                ret = LogicDownload.musicDownloadById(req.form)
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

    # #@staticmethod
    # @celery.task
    # def task():
    #     try:
    #         # 여기다 로직 구현
    #         logger.debug('main process started!!!!')
            
    #         # 설정값 접근 및 출력 예제
    #         # Boolean 값
    #         sample_boolean = ModelSetting.get_bool('sample_boolean')
    #         if sample_boolean: logger.debug('sample_boolean: True')
    #         else: logger.debug('sample_boolean: False')

    #         # 텍스트 값
    #         sample_text = ModelSetting.get('sample_text')
    #         logger.debug('sample_text: %s', sample_text)

    #         # 숫자값
    #         sample_integer = ModelSetting.get_int('sample_integer')
    #         logger.debug('sample_int : %s', sample_integer)

    #         # 리스트 처리-1
    #         sample_pathes = ModelSetting.get_list('sample_path', ',')
    #         for path in sample_pathes:
    #             logger.debug('sample_path: %s', path)

    #         # 리스트 처리-2
    #         sample_list = ModelSetting.get_list('sample_list', '|')
    #         for item in sample_list:
    #             logger.debug('sample_item: %s', item)

    #     except Exception as e:
    #         logger.debug('Exception:%s', e)
    #         logger.debug(traceback.format_exc())


    #########################################################
    # 필요함수 정의 및 구현부분
    @staticmethod
    def musicPlay(req):

        trackId = req['trackId'];
        naverId = P.ModelSetting.to_dict()['naverId']
        naverPw = P.ModelSetting.to_dict()['naverPw']
        
        if LogicDownload.session is None :
            LogicDownload.session = LogicDownload.naver_login(naverId, naverPw)
            if LogicDownload.session is None :
                return False

        resp = LogicDownload.session.post('https://apis.naver.com/nmwebplayer/music/stplay_trackStPlay_NO_HMAC?play.trackId='+trackId+'&deviceType=VIBE_WEB&play.mediaSourceType=AAC_320_ENC', data=LogicDownload.data, headers=LogicDownload.headers)
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
    def top100List():
        resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/vibe/v1/chart/track/total')
    
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
    def musicDownloadById(req):
        
        trackId = req['trackId']
        downloadType = req['type']
        
        trackInfo = None
        result = False
        if downloadType == "TOP100":
            info = LogicDownload.top100List()

            
            for track in info['content']['response']['result']['chart']['items']['tracks']['track']:
                result = LogicDownload.musicDownload(track, downloadType)

            if result is True:
                return {'ret':'success', 'content':info}
            else:
                return {'ret':'failed'}
        elif downloadType == "album":
            
            info = LogicDownload.albumInfo(req)

            for track in info['albumTracks']['response']['result']['tracks']['track']:
                result = LogicDownload.musicDownload(track, downloadType)

            if result is True:
                return {'ret':'success', 'content':info}
            else:
                return {'ret':'failed'}

        else:
            resp = requests.get('https://apis.naver.com/vibeWeb/musicapiweb/track/'+trackId)
            if resp.status_code == 200 :
                dictionary = xmltodict.parse(resp.text)
                trackInfo = json.loads(json.dumps(dictionary))
                result = LogicDownload.musicDownload(trackInfo['response']['result']['track'], downloadType)

                if result is True:
                    return {'ret':'success', 'content':trackInfo}
                else:
                    return {'ret':'failed'}
        
    
    @staticmethod
    def musicDownload(track, type):

        trackId = track['trackId']
        trackTitle = track['trackTitle']
        
        albumTitle  = track['album']['albumTitle'].replace('/', '')
        trackNumber = track['trackNumber']
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
        from datetime import datetime
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
            
            saveFileName = saveFileName.replace('%albumTitle%', albumTitle)
            saveFileName = saveFileName.replace('%trackNumber%', trackNumber)
            saveFileName = saveFileName.replace('%trackTitle%', trackTitle)
            saveFileName = saveFileName.replace('%artist%', artist)
            saveFileName = saveFileName.replace('%today%', today)
            
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
            
            saveFileNameByAlbum = saveFileNameByAlbum.replace('%albumTitle%', albumTitle)
            saveFileNameByAlbum = saveFileNameByAlbum.replace('%trackNumber%', trackNumber)
            saveFileNameByAlbum = saveFileNameByAlbum.replace('%trackTitle%', trackTitle)
            saveFileNameByAlbum = saveFileNameByAlbum.replace('%artist%', artist)
            saveFileNameByAlbum = saveFileNameByAlbum.replace('%today%', today)
            
            fileName = saveFileNameByAlbum+".mp3"
            savePath = savePathByAlbum
        
        elif type == "TOP100":

            rank = track['rank']['currentRank']
            rank = rank.rjust(3,"0")

            savePathByTOP100 = P.ModelSetting.to_dict()['savePathByTOP100']
            saveFileNameByTOP100 = P.ModelSetting.to_dict()['saveFileNameByTOP100']
            
            savePathByTOP100 = savePathByTOP100.replace('%albumTitle%', albumTitle)
            savePathByTOP100 = savePathByTOP100.replace('%trackNumber%', trackNumber)
            savePathByTOP100 = savePathByTOP100.replace('%trackTitle%', trackTitle)
            savePathByTOP100 = savePathByTOP100.replace('%artist%', artist)
            savePathByTOP100 = savePathByTOP100.replace('%today%', today)
            savePathByTOP100 = savePathByTOP100.replace('%rank%', rank)
            
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%albumTitle%', albumTitle)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%trackNumber%', trackNumber)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%trackTitle%', trackTitle)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%artist%', artist)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%today%', today)
            saveFileNameByTOP100 = saveFileNameByTOP100.replace('%rank%', rank)

            fileName = saveFileNameByTOP100+".mp3"
            savePath = savePathByTOP100
            

        logger.debug('savePath : ' + savePath)
        logger.debug('fileName : ' + fileName)

        naverId = P.ModelSetting.to_dict()['naverId']
        naverPw = P.ModelSetting.to_dict()['naverPw']

        if LogicDownload.session is None :
            LogicDownload.session = LogicDownload.naver_login(naverId, naverPw)
            if LogicDownload.session is None :
                return False
                

                
        if not os.path.isdir(savePath):
            os.makedirs(savePath)

        logger.debug("다운로드 시작" + trackId)
        logger.debug(P.ModelSetting.to_dict()['ffmpegDownload'])
        if P.ModelSetting.to_dict()['ffmpegDownload'] == "True":
            logger.debug("다운로드 시작 by ffmpeg" + trackId)
            resp = LogicDownload.session.post('https://apis.naver.com/nmwebplayer/music/stplay_trackStPlay_NO_HMAC?play.trackId='+trackId+'&deviceType=VIBE_WEB&play.mediaSourceType=AAC_320_ENC', data=LogicDownload.data, headers=LogicDownload.headers)
            rj = resp.json()
            musicDownloadUrl = rj["moduleInfo"]["hlsManifestUrl"]
            logger.debug( os.path.join(savePath, fileName) )
            logger.debug( musicDownloadUrl )
            command = ['ffmpeg', '-y', '-i', str( musicDownloadUrl ), '-acodec', 'mp3', '-ab', '320k', 
                        '-metadata', 'title='+trackTitle, '-metadata', 'artist='+artist , '-metadata', 'album='+albumTitle, '-metadata', 'track='+trackNumber, 
                        '-metadata', 'album_artist='+artist, os.path.join(savePath, fileName)]
                        # '"'++'"']
            
            output = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, encoding='utf-8')
            logger.debug(output.communicate())
        else:
            logger.debug("다운로드 시작 by curl" + trackId)
            resp = LogicDownload.session.post('https://apis.naver.com/nmwebplayer/music/stplay_trackStPlay_NO_HMAC?play.trackId='+trackId+'&deviceType=VIBE_WEB', data=LogicDownload.data, headers=LogicDownload.headers)
            rj = resp.json()
            musicDownloadUrl = rj["moduleInfo"]["hlsManifestUrl"]
            logger.debug(musicDownloadUrl)
            command = ['curl', str( musicDownloadUrl ), '--output', os.path.join(savePath, fileName)]
            output = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, encoding='utf-8')
            logger.debug(output.communicate())
        
        logger.debug("다운로드 종료" + trackTitle)
        if type != "track":
            import time
            time.sleep(1)
        return True


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
    def naver_login(nid, npw):
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
            print("로그인 성공")
            return session
        else:
            print("로그인 실패")
            return None
            
    # def register_item(req):
    #     try:
    #         naverId = req['naverId']
    #         naverPw = req['naverPw']
    #         savePath = req['savePath']

    #         entity = ModelItem(naverId, naverPw, savePath)
    #         entity.save()

    #         return {'ret':'success', 'msg':'아이템 등록완료'}
    #     except Exception as e:
    #         logger.debug('Exception:%s', e)
    #         logger.debug(traceback.format_exc())
    #         return {'ret':'error', 'msg':str(e)}

    # @staticmethod
    # def modify_item(req):
    #     try:
    #         item_id = int(req['item_id'])

    #         entity = ModelItem.get_by_id(item_id)
    #         entity.sample_string = req['sample_string']
    #         entity.sample_integer = int(req['sample_integer'])
    #         entity.sample_boolean = True if req['sample_boolean'] == 'True' else False
    #         entity.sample_imgurl = req['sample_imgurl']
    #         entity.save()

    #         return {'ret':'success', 'msg':'아이템 수정완료'}
    #     except Exception as e:
    #         logger.debug('Exception:%s', e)
    #         logger.debug(traceback.format_exc())
    #         return {'ret':'error', 'msg':str(e)}

    