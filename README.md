# tashu crawler

대전시 공공 자전거 시스템('타슈')의 실시간 사용량 예측 서비스를 개발하기 위해 필요한 데이터를 수집하는 도구

* src/feature_data_crawer.py : feature(기온, 습도, 강수량, 풍속) 데이터 수집 스크립트
* src/feature_data_DB_controller.py : 수집한 feature 데이터를 DB에 저장하는 스크립트
* src/tashu_current_status_crawler.py : <http://m.tashu.or.kr/m/mainAction.do?process=mainPage>에서 타슈 실시간 현황을 수집하는 스크립트
* src/tashu_status_DB_contoller.py : 수집한 실시간 현황을 DB에 저장하는 스크립트