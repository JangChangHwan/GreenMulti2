# coding: utf-8

basicMenu = u"""
# 시작
top	초기메뉴		green|guide|mail|bbs|computer|potion|blindnews|magazin|pds|lib|amcenter|pds2012

# 초록등대
green	0. 초록등대	top	green1|green2|green3|green4|green5|green6|green7|green8|green9|green10
green1	1. 공지사항	green	/bbs/board.php?bo_table=green1&cl=green
green2	2. 나눔장터	top	/bbs/board.php?bo_table=green2&cl=green
green3	3. 우리들의 이야기	green	/bbs/board.php?bo_table=green3&cl=green
green4	4. 자료실	green	green41|green42|green43|green44|green45|green46|green47
green41	1. 운영체제/드라이버	green4	/bbs/board.php?bo_table=green41&cl=green
green42	2. 일반자료실	green4	/bbs/board.php?bo_table=green42&cl=green
green43	3. 포터블 자료실	green4	/bbs/board.php?bo_table=green43&cl=green
green44	4. 멀티미디어/인터넷	green4	/bbs/board.php?bo_table=green44&cl=green
green45	5. 프로그램 자동설치	green4	/bbs/board.php?bo_table=green45&cl=green
green46	6. 강의실	green4	/bbs/board.php?bo_table=green46&cl=green
green47	7. 기타자료실	green4	/bbs/board.php?bo_table=green47&cl=green
green5	5. 시각장애인 대학생 후원 희망통장	green	/bbs/board.php?bo_table=green5&cl=green
green6	6. 엔터테인먼트	green	green61|green62|green63|green64|green65|green66|green67|green68|green699
green61	1. 가요	green6	/bbs/board.php?bo_table=green61&cl=green
green62	2. 동영상	green6	/bbs/board.php?bo_table=green62&cl=green
green63	3. 팝/클래식	green6	/bbs/board.php?bo_table=green63&cl=green
green64	4. MR노래방	green6	/bbs/board.php?bo_table=green64&cl=green
green65	5. 앨범	green6	/bbs/board.php?bo_table=green65&cl=green
green66	6. 기타 자료실	green6	/bbs/board.php?bo_table=green66&cl=green
green67	7. 초록 시네마	green6	/bbs/board.php?bo_table=green67&cl=green
green68	8. 애니 자료실	green6	/bbs/board.php?bo_table=green68&cl=green
green699	99. 요청게시판	green6	/bbs/board.php?bo_table=green699&cl=green
green7	7. Youtube	green	/bbs/board.php?bo_table=green7&cl=green
green8	8. 건의함	green	/bbs/board.php?bo_table=green8&cl=green
green9	9. 질문게시판	green	/bbs/board.php?bo_table=green9&cl=green
green10	10. 회원가입 및 정보 확인	green	http://web.kbuwel.or.kr/plugin/ar.club/member.php?cl=green

# 공지사항
guide	1. 공지 및 이용안내	top	notice|oldinfo|rtguide
notice	1. 공지사항	guide	/bbs/board.php?bo_table=notice
oldinfo	2. 지난 공지	guide	/bbs/board.php?bo_table=oldinfo
rtguide	3. 마을이용안내	guide	/bbs/board.php?bo_table=rtguide

# 전자우편
mail	2. 전자우편	top	inbox|wmail|sent|spam|trash|rmemo|wmemo|smemo
inbox	1. 편지 읽기	mail	/bbs/board.php?bo_table=rmail&sca=Inbox
wmail	2. 편지쓰기	mail	/bbs/write.php?bo_table=rmail&sca=Inbox
sent	3. 보낸 편지함	mail	/bbs/board.php?bo_table=rmail&sca=Sent
spam	4. 스팸 편지함	mail	/bbs/board.php?bo_table=rmail&sca=spam
trash	5. 지운 편지함	mail	/bbs/board.php?bo_table=rmail&sca=Trash
rmemo	6. 받은 메모	mail	http://web.kbuwel.or.kr/plugin/ar.memo/memo.php?kind=recv
wmemo	7. 메모 쓰기	mail	http://web.kbuwel.or.kr/plugin/ar.memo/memo_form.php
smemo	8. 보낸 메모	mail	http://web.kbuwel.or.kr/plugin/ar.memo/memo.php?kind=send

# 게시판
bbs	3. 게시판	top	free|freeinfo|mark|story|news|agora|humor|ff|broadcast|kbu4|stress1|comma|dvsbbs|cardbbs|relibbs|prevbbs
free	1. 자유게시판	bbs	/bbs/board.php?bo_table=free
freeinfo	2. 자유공지 / 광고	bbs	/bbs/board.php?bo_table=freeinfo
mark	3. 벼룩시장 / 구인, 구직	bbs	/bbs/board.php?bo_table=mark
story	4. 이야기 벤치	bbs	/bbs/board.php?bo_table=story
news	5. 뉴스 광장	bbs	news1|news2|news3|news4|news5|news6|news7|news8|news9|welbbs|allnews
news1	1. 속보	news	/bbs/board.php?bo_table=news1
news2	2. 정치	news	/bbs/board.php?bo_table=news2
news3	3. 경제	news	/bbs/board.php?bo_table=news3
news4	4. 사회	news	/bbs/board.php?bo_table=news4
news5	5. 생활 / 문화	news	/bbs/board.php?bo_table=news5
news6	6. 세계	news	/bbs/board.php?bo_table=news6
news7	7. I T / 과학	news	/bbs/board.php?bo_table=news7
news8	8. 연예	news	/bbs/board.php?bo_table=news8
news9	9. 스포츠	news	/bbs/board.php?bo_table=news9
welbbs	10. 복지통신	news	/bbs/board.php?bo_table=welbbs
allnews	12. 전체뉴스 보기	news	/bbs/board.php?bo_table=allnews
agora	6. 아고라 토론	bbs	/bbs/board.php?bo_table=agora
humor	7. 유머 / 공포 / 황당	bbs	/bbs/board.php?bo_table=humor
ff	8. 가입인사 / 초보 연습	bbs	/bbs/board.php?bo_table=ff
broadcast	9. 화면해설방송 게시판	bbs	/bbs/board.php?bo_table=broadcast
kbu4	10. 녹음도서 목록	bbs	/bbs/board.php?bo_table=kbu4
stress1	12. 속상한 것 털어 놓는 방	bbs	/bbs/board.php?bo_table=stress1
comma	13. 쉼표가 찍힌 일상	bbs	/bbs/board.php?bo_table=comma
dvsbbs	14. 화면해설방송수신기 불편 신고 게시판	bbs	/bbs/board.php?bo_table=dvsbbs
cardbbs	15. 의약품 부작용 불편 신고 게시판	bbs	/bbs/board.php?bo_table=cardbbs
relibbs	16. 종교게시판	bbs	/bbs/board.php?bo_table=relibbs
prevbbs	17. 이전 자유게시판	bbs	free2014|free2011|free2006|free2003
free2014	1. 2014년 이전 자유게시판	prevbbs	/bbs/board.php?bo_table=free2014
free2011	2. 2011년 이전 자유게시판	prevbbs	/bbs/board.php?bo_table=free2011
free2006	3. 2007년 이전 자유게시판	prevbbs	/bbs/board.php?bo_table=free2006
free2003	4. 2004년 이전 자유게시판	prevbbs	/bbs/board.php?bo_table=free2003

# 전자도서관
lib	12. 전자도서관	top	novs|poes|eco|soci|hum|his|sci|hea|lan|chi|rel|etcs|alllib4|alllib5|alllib99

novs	1. 소설	lib	aetcs|romances|chils|detes|wars
aetcs	1. 일반소설	novs	/bbs/board.php?bo_table=aetcs&cl=lib2013
romances	2. 로맨스소설	novs	/bbs/board.php?bo_table=romances&cl=lib2013
chils	3. 무협/판타지	novs	/bbs/board.php?bo_table=chils&cl=lib2013
detes	4. 추리/스릴러	novs	/bbs/board.php?bo_table=detes&cl=lib2013
wars	5. 역사소설	novs	/bbs/board.php?bo_table=wars&cl=lib2013

poes	2. 시/에세이	lib	poe|essa
poe	1. 시	poes	/bbs/board.php?bo_table=poe&cl=lib2013
essa	2. 에세이	poes	/bbs/board.php?bo_table=essa&cl=lib2013

eco	3. 경제/경영	lib	/bbs/board.php?bo_table=eco&cl=lib2013
soci	4. 정치/사회	lib	/bbs/board.php?bo_table=soci&cl=lib2013
hum	5. 인문	lib	/bbs/board.php?bo_table=hum&cl=lib2013
his	6. 역사	lib	/bbs/board.php?bo_table=his&cl=lib2013
sci	7. 과학/기술	lib	/bbs/board.php?bo_table=sci&cl=lib2013
hea	8. 건강/심리	lib	/bbs/board.php?bo_table=hea&cl=lib2013
lan	9. 국어/외국어	lib	/bbs/board.php?bo_table=lan&cl=lib2013
chi	10. 유아/어린이/청소년	lib	/bbs/board.php?bo_table=chi&cl=lib2013
rel	11. 종교	lib	/bbs/board.php?bo_table=rel&cl=lib2013
etcs	12. 기타 (예술, 대중문화, 가정, 취미)	lib	/bbs/board.php?bo_table=etcs&cl=lib2013
alllib4	77. 공지사항	lib	/bbs/board.php?bo_table=alllib4&cl=lib2013
alllib5	88. 전자도서 요청 및 문의	lib	/bbs/board.php?bo_table=alllib5&cl=lib2013
alllib99	99. 전체 도서관	lib	/bbs/board.php?bo_table=alllib99&cl=lib2013

"""