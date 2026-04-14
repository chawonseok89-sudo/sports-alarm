import os
import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_sports_final(team_name, category):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    rank, last, next_m = "순위 확인 중", "기록 없음", "일정 없음"
    
    try:
        # 1. 순위 가져오기 (종합 뉴스 페이지 활용)
        url_rank = f"https://sports.news.naver.com/{category}/record/index"
        res_r = requests.get(url_rank, headers=headers)
        soup_r = BeautifulSoup(res_r.text, 'html.parser')
        
        # 스크립트 데이터 내에서 순위 찾기
        import re
        content = res_r.text
        team_pattern = re.compile(rf'"{team_name}".*?"rank":(\d+)')
        if category == "kbaseball": # 야구는 영문명 KIA 사용 가능성
            team_pattern = re.compile(rf'"KIA".*?"rank":(\d+)')
            
        match = team_pattern.search(content)
        if match:
            rank = match.group(1) + "위"

        # 2. 결과 및 일정 (검색 결과의 텍스트 요약 활용)
        url_m = f"https://m.search.naver.com/search.naver?query={team_name}+경기일정"
        res_m = requests.get(url_m, headers=headers)
        soup_m = BeautifulSoup(res_m.text, 'html.parser')
        
        # 텍스트 덩어리에서 정보 추출
        all_text = soup_m.get_text(separator=" ")
        
        # 최근 결과 찾기
        if "종료" in all_text:
            parts = all_text.split("종료")
            last = parts[0].split()[-4:] # 종료 직전 단어들 조합
            last = " ".join(last)
            
        # 다음 일정 찾기
        if " vs " in all_text:
            parts = all_text.split(" vs ")
            next_m = " ".join(parts[0].split()[-2:]) + " vs " + parts[1].split()[0]

    except:
        pass
    return rank, last, next_m

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 데이터 수집
    k_rank, k_last, k_next = get_sports_final("기아", "kbaseball")
    j_rank, j_last, j_next = get_sports_final("전북", "kfootball")
    
    today = datetime.now().strftime('%m%d')
    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n🏆 순위: {k_rank}\n✅ 결과: {k_last}\n📅 일정: {k_next}\n"
        f"🎬 하이라이트: https://www.youtube.com/results?search_query=기아타이거즈+하이라이트\n\n"
        f"⚽ [전북 현대]\n🏆 순위: {j_rank}\n✅ 결과: {j_last}\n📅 일정: {j_next}\n"
        f"🎬 하이라이트: https://www.youtube.com/results?search_query=전북현대+하이라이트\n\n"
        f"포기하지 않고 끝까지 배달하겠습니다! 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
