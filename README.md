#### 오류 발생시 홈페이지에 로그와 함께 글작성 하시면 조치 하겠습니다.
#### 2024.03.23
+ 네이버 로그인 셀레니움으로 변경
  실행하여 셀레니움 설치 필요함
  
  ```bash
  apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y \
    google-chrome-stable \
    && CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}' | cut -d '.' -f1) \
    && CHROME_DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") \
    && wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/bin \
    && chmod +x /usr/bin/chromedriver \
    && rm /tmp/chromedriver.zip
  ```
  
##### 2022.10.13
+ 검색시 무한로딩 오류 수정
##### 2022.02.10
+ 다운로드 오류 수정.
  음원 다운로드 원본 파일을 받지 못하게 변경됨.
  인코딩된 파일을 받아 TAG 정보를 강제로 삽입.
##### 2021.07.29
+ 폴더, 파일 형식 디스크번호 추가.
    + 폴더, 파일명 설정시 디스크번호를 추가합니다.  
    %discNumber%  
##### 2021.07.28
+ 관리 메뉴 추가.
    + 관리 메뉴를 추가 합니다.  
    mp3 다운로드, 재생을 할 수 있습니다.  
    초기 관리 경로는 설정에서 지정할 수 있습니다.  
    이동, 삭제, 태그 수정 추가 예정.

##### 2021.07.27
+ 로그인 시간체크
    + 로그인후 3시간이 지나면 다시 로그인 합니다.
##### 2021.07.22
+ 다운로드 목록 추가
![](https://cdn.discordapp.com/attachments/621288921493667872/867756513421557770/unknown.png)
    + 다운로드 목록 화면추가  
    다운로드 목록 화면이 추가됩니다.  
    해당화면은 다운로드 받은 최신 30개의 목록이 보여지고 3초마다 자동 재조회 하게 됩니다.  
    목록에 나오는 정보로 다운로드 상태를 확인할 수 있습니다.  
***
+ ffmpeg 사용여부 삭제
     + ffmpeg 사용여부 설정이 삭제 됩니다.  
    무조건 ffmpeg로 받게 변경되었습니다.  
    320K로 받게 하면서 바뀌었는데 바뀌게된 자세한 설명은 생략합니다.  
***
+ 로그인실패시 알림
    + 로그인 실패시  
    "**로그인 실패**", "**자동입력 방지활성화 직접로그인 후 재시도 하세요.**"라고 알림이 표시됩니다.
***
+ 다운로드시 tmp폴더 사용
    + 다운로드시 data/tmp 폴더를 사용합니다.  
    tmp 폴더에 다운로드후 태그를 입히고 설정된 폴더로 이동합니다.

***
##### 2021.07.21
+ 최신앨범 스케쥴링 추가
![](https://cdn.discordapp.com/attachments/621288921493667872/867415302882197514/unknown.png)
    + 최신앨범이 스케쥴링에 추가됩니다.  
    최신앨범은 스케쥴이 여러번 돌아도 한번 다운받은 최신앨범은 새로 다운받지 않습니다.  
    스케쥴로 다운받은 앨범을 다시 다운로드시 수동으로 받으셔야 합니다.
***
+ 설정 - 지연시간 입력값 추가
![](https://cdn.discordapp.com/attachments/621288921493667872/867416602743537694/unknown.png)  
    + 기존 스케쥴 및 전체 다운로드시 간혹 데이터를 제대로 못받아오는 현상이 있어 다운로드시 3초의 지연시간을 주었습니다.  
    해당항목을 설정으로 빼서 개인의 설정에 맞게 지연시킬수 있습니다.

