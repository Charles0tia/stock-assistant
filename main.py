!pip install pykrx -q
from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta

def find_volume_surge_price_stagnant_stocks():
    print("🚀 국내 전체 주식 시장 데이터 분석을 시작합니다... (약 1~2분 소요)")
    
    # 1. 오늘 날짜 및 45일 전 날짜 계산 (영업일 기준 30일 확보)
    today = datetime.today().strftime("%Y%m%d")
    start_date = (datetime.today() - timedelta(days=45)).strftime("%Y%m%d")
    
    # KOSPI, KOSDAQ 전체 상장 종목 코드 가져오기
    tickers = stock.get_market_ticker_list(today, market="ALL")
    
    results = []
    
    # 2. 전체 종목을 순회하며 조건 검사 (예시로 상위 일부 또는 전체 순회)
    # 초보자분들이 테스트할 수 있도록 전체 혹은 대형주 위주로 체크 가능합니다.
    count = 0
    for ticker in tickers:
        try:
            name = stock.get_market_ticker_name(ticker)
            df = stock.get_market_ohlcv(start_date, today, ticker)
            
            if len(df) < 30:
                continue
                
            # 최근 30거래일 데이터
            df_30 = df.tail(30)
            
            # 지표 계산
            avg_volume_30 = df_30['거래량'].mean() # 30일 평균 거래량
            recent_volume_5 = df_30.tail(5)['거래량'].mean() # 최근 5일 평균 거래량
            
            # 가격 변동성 (30일 전 가격 대비 최근 가격의 등락률)
            price_start = df_30.iloc[0]['종가']
            price_end = df_30.iloc[-1]['종가']
            price_change_rate = ((price_end - price_start) / price_start) * 100
            
            # 조건 필터링: 
            # 1) 최근 5일 평균 거래량이 30일 평균 거래량의 2배 이상 폭증
            # 2) 30일 동안 주가 변동률이 -5% ~ +5% 사이로 가격이 크게 오르지 않고 정체됨
            # 3) 시가총액이 너무 적은 품절주/동전주 제외를 위해 최소 종가 필터 등 적용 가능
            if avg_volume_30 > 10000: # 최소 유동성 조건
                volume_surge_ratio = recent_volume_5 / avg_volume_30
                
                if volume_surge_ratio >= 2.0 and -5.0 <= price_change_rate <= 5.0 and price_end > 1000:
                    results.append({
                        "종목코드": ticker,
                        "종목명": name,
                        "현재가": price_end,
                        "30일간 주가등락률(%)": round(price_change_rate, 2),
                        "거래량 급증 배수": round(volume_surge_ratio, 2)
                    })
        except Exception as e:
            continue
            
    # 결과를 데이터프레임으로 변환 및 정렬 (거래량 급증 순)
    result_df = pd.DataFrame(results)
    if not result_df.empty:
        result_df = result_df.sort_values(by="거래량 급증 배수", ascending=False)
        print(f"\n✨ [조건 만족 종목 발굴 완료: 총 {len(result_df)}개]")
        print(result_df.head(10)) # 상위 10개 출력
        return result_df
    else:
        print("조건에 맞는 종목이 없습니다.")
        return pd.DataFrame()

# 함수 실행
target_stocks = find_volume_surge_price_stagnant_stocks()
