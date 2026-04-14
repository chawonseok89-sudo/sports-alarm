= row.select_one("th, td").text.strip() + "위"
                break
    except: rank = "확인 불가"

    # 2. 최근 결과 및 다음 일정 찾기
    last_game = "기록 없음"
    next_game = "일정 없음"
    video_link = f"https://www.youtube.com/results?search_query={team_keyword}+하이라이트"
    
    try:
        m_res = requests.get(f"https://search.naver.com/search.naver?query={team_keyword}+경기일정", headers=headers)
        m_soup = BeautifulSoup(m_res.text, 'html.parser')
        
        # 경기 목록 추출
        matches = m_soup.select(".item_list") or m_soup.select(".schedule_item")
        
        past_matches = []
        future_matches = []
        
        for m in m_soup.select(".inner"):
            m_text = m.get_text()
            if "종료" in m_text:
                past_matches.append(m_text.replace("\n", " ").strip())
            else:
                future_matches.append(m_text.replace("\n", " ").strip())
        
        if past_matches:
            last_game = past_matches[-1].split("종료")[0].strip() + " [종료]"
            # 최근 경기 팀들로 하이라이트 링크 업데이트
            video_link = f"https://www.youtube.com/results?search_query={last_game.replace(' ', '+')}+하이라이트"
            
        if future_matches:
            next_game = future_matches[0].strip()
    except: pass

    return rank, last_game, next_game, video_link

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 기아와 전북 데이터 수집
    k_rank, k_last, k_next, k_vid = get_sports_all_in_one("KBO", "기아타이거즈")
    j_rank, j_last, j_next, j_vid = get_sports_all_in_one("K리그1", "전북현대")
    
    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n"
        f"🏆 현재순위: {k_rank}\n"
        f"✅ 최근결과: {k_last}\n"
        f"📅 다음일정: {k_next}\n"
        f"🎬 하이라이트: {k_vid}\n\n"
        f"⚽ [전북 현대]\n"
        f"🏆 현재순위: {j_rank}\n"
        f"✅ 최근결과: {j_last}\n"
        f"📅 다음일정: {j_next}\n"
        f"🎬 하이라이트: {j_vid}\n\n"
        f"밤 10시 정식 알림에서 뵙겠습니다! 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
