0자 이내에서 '숫자+위' 패턴 찾기
            match = re.search(rf"{team_name[:2]}.*?(\d+)위", res.text)
            if match: rank = match.group(1) + "위"

        # 2. 결과 및 일정 추출 (박스 형태 데이터 공략)
        # 종료된 경기와 예정된 경기를 텍스트로 구분
        items = soup.select(".item_list li, .schedule_item, .inner")
        past_list = []
        future_list = []
        
        for item in items:
            text = item.get_text(" ", strip=True)
            if team_name[:2] in text:
                if "종료" in text or "취소" in text:
                    past_list.append(text.replace("종료", "").strip())
                elif "vs" in text or ":" in text:
                    future_list.append(text.strip())
        
        if past_list: last = past_list[-1]
        if future_list: next_m = future_list[0]

    except:
        pass
    return rank, last, next_m

async def send_sports_report():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=token)

    # 기아와 전북 데이터 수집
    k_rank, k_last, k_next = get_sports_info("기아타이거즈")
    j_rank, j_last, j_next = get_sports_info("전북현대")
    
    message = (
        f"📅 {datetime.now().strftime('%Y-%m-%d')} 스포츠 통합 리포트\n\n"
        f"🐯 [기아 타이거즈]\n"
        f"🏆 순위: {k_rank}\n"
        f"✅ 결과: {k_last}\n"
        f"📅 일정: {k_next}\n"
        f"🎬 영상: https://www.youtube.com/results?search_query=기아타이거즈+하이라이트\n\n"
        f"⚽ [전북 현대]\n"
        f"🏆 순위: {j_rank}\n"
        f"✅ 결과: {j_last}\n"
        f"📅 일정: {j_next}\n"
        f"🎬 영상: https://www.youtube.com/results?search_query=전북현대+하이라이트\n\n"
        f"끊김 없이 배달될 수 있도록 보완했습니다! 😊"
    )

    await bot.send_message(chat_id=chat_id, text=message)

if __name__ == "__main__":
    asyncio.run(send_sports_report())
