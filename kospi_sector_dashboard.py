"""
코스피 대비 섹터/종목 상대강도 대시보드

실행 방법:
1. pip install streamlit pandas plotly yfinance
2. streamlit run kospi_sector_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')


# ========================================================================================
# 페이지 설정
# ========================================================================================
st.set_page_config(
    page_title="지수 vs 섹터/종목 상대강도",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google AdSense
st.markdown("""
    <meta name="google-adsense-account" content="ca-pub-9688338422874533">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9688338422874533"
         crossorigin="anonymous"></script>
""", unsafe_allow_html=True)

# ========================================================================================
# 한국 섹터 및 대표종목 정의 (이모지 포함)
# 첫 번째 종목이 대표종목 (기본 선택됨)
# 코스피/코스닥 별로 다른 대표종목
# ========================================================================================
SECTORS_KR = {
    "📊지수": {
        "kospi": [
            {"code": "^KQ11", "name": "코스닥"},
            {"code": "^IXIC", "name": "나스닥"},
            {"code": "^GSPC", "name": "S&P500"},
            {"code": "^DJI", "name": "다우존스"},
        ],
        "kosdaq": [
            {"code": "^KS11", "name": "코스피"},
            {"code": "^IXIC", "name": "나스닥"},
            {"code": "^GSPC", "name": "S&P500"},
            {"code": "^DJI", "name": "다우존스"},
        ]
    },
    "🔬반도체": {
        "kospi": [
            {"code": "091160.KS", "name": "KODEX 반도체"},
            {"code": "005930.KS", "name": "삼성전자"},
            {"code": "000660.KS", "name": "SK하이닉스"},
        ],
        "kosdaq": [
            {"code": "403870.KQ", "name": "HPSP"},
            {"code": "058470.KQ", "name": "리노공업"},
        ]
    },
    "🚗자동차": {
        "kospi": [
            {"code": "091180.KS", "name": "KODEX 자동차"},
            {"code": "005380.KS", "name": "현대차"},
            {"code": "000270.KS", "name": "기아"},
        ],
        "kosdaq": [
            {"code": "015750.KQ", "name": "성우하이텍"},
            {"code": "118990.KQ", "name": "모트렉스"},
        ]
    },
    "🚢조선": {
        "kospi": [
            {"code": "494670.KS", "name": "TIGER 조선TOP10"},
            {"code": "329180.KS", "name": "HD현대중공업"},
            {"code": "042660.KS", "name": "한화오션"},
        ],
        "kosdaq": []
    },
    "⚙️철강": {
        "kospi": [
            {"code": "117680.KS", "name": "KODEX 철강"},
            {"code": "005490.KS", "name": "POSCO홀딩스"},
            {"code": "004020.KS", "name": "현대제철"},
        ],
        "kosdaq": []
    },
    "🧪화학": {
        "kospi": [
            {"code": "117460.KS", "name": "KODEX 에너지화학"},
            {"code": "051910.KS", "name": "LG화학"},
            {"code": "011170.KS", "name": "롯데케미칼"},
        ],
        "kosdaq": [
            {"code": "357780.KQ", "name": "솔브레인"},
            {"code": "348370.KQ", "name": "엔켐"},
        ]
    },
    "☀️태양광/에너지": {
        "kospi": [
            {"code": "377990.KS", "name": "TIGER Fn신재생에너지"},
            {"code": "009830.KS", "name": "한화솔루션"},
            {"code": "112610.KS", "name": "CS윈드"},
        ],
        "kosdaq": []
    },
    "🛡️방산/우주": {
        "kospi": [
            {"code": "463250.KS", "name": "TIGER K방산&우주"},
            {"code": "012450.KS", "name": "한화에어로스페이스"},
            {"code": "079550.KS", "name": "LIG넥스원"},
        ],
        "kosdaq": [
            {"code": "189300.KQ", "name": "인텔리안테크"},
            {"code": "099320.KQ", "name": "쎄트렉아이"},
        ]
    },
    "🔋2차전지": {
        "kospi": [
            {"code": "305720.KS", "name": "KODEX 2차전지산업"},
            {"code": "373220.KS", "name": "LG에너지솔루션"},
            {"code": "006400.KS", "name": "삼성SDI"},
        ],
        "kosdaq": [
            {"code": "247540.KQ", "name": "에코프로비엠"},
            {"code": "086520.KQ", "name": "에코프로"},
        ]
    },
    "💊바이오": {
        "kospi": [
            {"code": "244580.KS", "name": "KODEX 바이오"},
            {"code": "207940.KS", "name": "삼성바이오로직스"},
            {"code": "068270.KS", "name": "셀트리온"},
        ],
        "kosdaq": [
            {"code": "196170.KQ", "name": "알테오젠"},
            {"code": "028300.KQ", "name": "HLB"},
        ]
    },
    "🏦금융": {
        "kospi": [
            {"code": "091170.KS", "name": "KODEX 은행"},
            {"code": "105560.KS", "name": "KB금융"},
            {"code": "055550.KS", "name": "신한지주"},
        ],
        "kosdaq": []
    },
    "📈증권": {
        "kospi": [
            {"code": "102970.KS", "name": "KODEX 증권"},
            {"code": "039490.KS", "name": "키움증권"},
            {"code": "016360.KS", "name": "삼성증권"},
        ],
        "kosdaq": []
    },
    "💻인터넷": {
        "kospi": [
            {"code": "365000.KS", "name": "TIGER 인터넷TOP10"},
            {"code": "035420.KS", "name": "NAVER"},
            {"code": "035720.KS", "name": "카카오"},
        ],
        "kosdaq": [
            {"code": "067160.KQ", "name": "SOOP"},
            {"code": "042000.KQ", "name": "카페24"},
        ]
    },
    "☢️원자력": {
        "kospi": [
            {"code": "434730.KS", "name": "HANARO 원자력iSelect"},
            {"code": "034020.KS", "name": "두산에너빌리티"},
            {"code": "052690.KS", "name": "한전기술"},
        ],
        "kosdaq": [
            {"code": "032820.KQ", "name": "우리기술"},
            {"code": "046120.KQ", "name": "오르비텍"},
        ]
    },
    "⚡전력인프라": {
        "kospi": [
            {"code": "487240.KS", "name": "KODEX AI전력핵심설비"},
            {"code": "010120.KS", "name": "LS ELECTRIC"},
            {"code": "267260.KS", "name": "HD현대일렉트릭"},
        ],
        "kosdaq": [
            {"code": "033100.KQ", "name": "제룡전기"},
            {"code": "017510.KQ", "name": "세명전기"},
        ]
    },
    "🤖로봇": {
        "kospi": [
            {"code": "445290.KS", "name": "KODEX K-로봇액티브"},
            {"code": "454910.KS", "name": "두산로보틱스"},
            {"code": "004380.KS", "name": "삼익THK"},
        ],
        "kosdaq": [
            {"code": "277810.KQ", "name": "레인보우로보틱스"},
            {"code": "108490.KQ", "name": "로보티즈"},
        ]
    },
    "📡통신": {
        "kospi": [
            {"code": "315270.KS", "name": "TIGER 200 커뮤니케이션서비스"},
            {"code": "017670.KS", "name": "SK텔레콤"},
            {"code": "030200.KS", "name": "KT"},
        ],
        "kosdaq": []
    },
    "⛽에너지/정유": {
        "kospi": [
            {"code": "139250.KS", "name": "TIGER 200 에너지화학"},
            {"code": "096770.KS", "name": "SK이노베이션"},
            {"code": "010950.KS", "name": "S-Oil"},
        ],
        "kosdaq": []
    },
    "🏗️건설": {
        "kospi": [
            {"code": "117700.KS", "name": "KODEX 건설"},
            {"code": "000720.KS", "name": "현대건설"},
            {"code": "375500.KS", "name": "DL이앤씨"},
        ],
        "kosdaq": []
    },
    "🛒유통": {
        "kospi": [
            {"code": "266390.KS", "name": "KODEX 경기소비재"},
            {"code": "004170.KS", "name": "신세계"},
            {"code": "139480.KS", "name": "이마트"},
        ],
        "kosdaq": []
    },
    "💄화장품": {
        "kospi": [
            {"code": "228790.KS", "name": "TIGER 화장품"},
            {"code": "278470.KS", "name": "에이피알"},
            {"code": "192820.KS", "name": "코스맥스"},
        ],
        "kosdaq": [
            {"code": "257720.KQ", "name": "실리콘투"},
            {"code": "018290.KQ", "name": "브이티"},
        ]
    },
    "🎤케이팝": {
        "kospi": [
            {"code": "475050.KS", "name": "ACE KPOP포커스"},
            {"code": "352820.KS", "name": "하이브"},
        ],
        "kosdaq": [
            {"code": "035900.KQ", "name": "JYP Ent."},
            {"code": "041510.KQ", "name": "에스엠"},
        ]
    },
    "✈️여행": {
        "kospi": [
            {"code": "228800.KS", "name": "TIGER 여행레저"},
            {"code": "003490.KS", "name": "대한항공"},
            {"code": "008770.KS", "name": "호텔신라"},
        ],
        "kosdaq": [
            {"code": "080160.KQ", "name": "모두투어"},
            {"code": "104040.KQ", "name": "노랑풍선"},
        ]
    },
    "🍔푸드": {
        "kospi": [
            {"code": "438900.KS", "name": "HANARO Fn K-푸드"},
            {"code": "097950.KS", "name": "CJ제일제당"},
            {"code": "271560.KS", "name": "오리온"},
        ],
        "kosdaq": [
            {"code": "260970.KQ", "name": "에스앤디"},
            {"code": "290720.KQ", "name": "푸드나무"},
        ]
    },
    "🎮게임": {
        "kospi": [
            {"code": "300950.KS", "name": "KODEX 게임산업"},
            {"code": "259960.KS", "name": "크래프톤"},
            {"code": "036570.KS", "name": "엔씨소프트"},
        ],
        "kosdaq": [
            {"code": "293490.KQ", "name": "카카오게임즈"},
            {"code": "263750.KQ", "name": "펄어비스"},
        ]
    },
    "🩺의료기기": {
        "kospi": [
            {"code": "266420.KS", "name": "KODEX 헬스케어"},
            {"code": "145720.KS", "name": "덴티움"},
        ],
        "kosdaq": [
            {"code": "214150.KQ", "name": "클래시스"},
            {"code": "214450.KQ", "name": "파마리서치"},
        ]
    },
    "📺콘텐츠/미디어": {
        "kospi": [
            {"code": "266360.KS", "name": "KODEX K콘텐츠"},
        ],
        "kosdaq": [
            {"code": "035760.KQ", "name": "CJ ENM"},
            {"code": "253450.KQ", "name": "스튜디오드래곤"},
        ]
    },
}

# ========================================================================================
# 미국 섹터 및 대표종목 정의
# ========================================================================================
SECTORS_US = {
    "📊지수": {
        "us": [
            {"code": "^GSPC", "name": "S&P500"},
            {"code": "^IXIC", "name": "나스닥 종합"},
        ]
    },
    "🧠AI/가속기 반도체": {
        "us": [
            {"code": "SMH", "name": "반에크 반도체 ETF"},
            {"code": "NVDA", "name": "엔비디아"},
            {"code": "AMD", "name": "AMD"},
        ]
    },
    "🏭반도체_파운드리/제조": {
        "us": [
            {"code": "SOXQ", "name": "인베스코 반도체 ETF"},
            {"code": "TSM", "name": "TSMC"},
            {"code": "INTC", "name": "인텔"},
        ]
    },
    "🛠️반도체_장비": {
        "us": [
            {"code": "FTXL", "name": "퍼스트트러스트 나스닥 반도체 ETF"},
            {"code": "ASML", "name": "ASML"},
            {"code": "AMAT", "name": "어플라이드 머티리얼즈"},
        ]
    },
    "💾반도체_메모리/스토리지": {
        "us": [
            {"code": "SOXX", "name": "아이셰어즈 반도체 ETF"},
            {"code": "MU", "name": "마이크론"},
            {"code": "WDC", "name": "웨스턴 디지털"},
        ]
    },
    "🔎검색/광고플랫폼": {
        "us": [
            {"code": "VOX", "name": "뱅가드 커뮤니케이션서비스 ETF"},
            {"code": "GOOG", "name": "구글(알파벳)"},
            {"code": "TTD", "name": "트레이드 데스크"},
        ]
    },
    "👥소셜/커뮤니티": {
        "us": [
            {"code": "SOCL", "name": "글로벌엑스 소셜미디어 ETF"},
            {"code": "META", "name": "메타"},
            {"code": "SNAP", "name": "스냅"},
        ]
    },
    "🛒이커머스": {
        "us": [
            {"code": "IBUY", "name": "앰플리파이 온라인리테일 ETF"},
            {"code": "AMZN", "name": "아마존"},
            {"code": "MELI", "name": "메르카도리브레"},
        ]
    },
    "🏷️리테일(오프라인)": {
        "us": [
            {"code": "RTH", "name": "반에크 리테일 ETF"},
            {"code": "WMT", "name": "월마트"},
            {"code": "COST", "name": "코스트코"},
        ]
    },
    "☁️클라우드/엔터프라이즈": {
        "us": [
            {"code": "SKYY", "name": "퍼스트트러스트 클라우드컴퓨팅 ETF"},
            {"code": "MSFT", "name": "마이크로소프트"},
            {"code": "ORCL", "name": "오라클"},
        ]
    },
    "📊데이터/AI 분석SW": {
        "us": [
            {"code": "IGV", "name": "아이셰어즈 소프트웨어 ETF"},
            {"code": "PLTR", "name": "팔란티어"},
            {"code": "SNOW", "name": "스노우플레이크"},
        ]
    },
    "🛡️사이버보안": {
        "us": [
            {"code": "CIBR", "name": "퍼스트트러스트 사이버보안 ETF"},
            {"code": "PANW", "name": "팔로알토 네트웍스"},
            {"code": "CRWD", "name": "크라우드스트라이크"},
        ]
    },
    "📺미디어/스트리밍": {
        "us": [
            {"code": "GGME", "name": "인베스코 넥스트젠 미디어&게이밍 ETF"},
            {"code": "NFLX", "name": "넷플릭스"},
            {"code": "CMCSA", "name": "컴캐스트"},
        ]
    },
    "🚗전기차/EV": {
        "us": [
            {"code": "DRIV", "name": "글로벌엑스 자율주행&EV ETF"},
            {"code": "TSLA", "name": "테슬라"},
            {"code": "RIVN", "name": "리비안"},
        ]
    },
    "⚡전력인프라(그리드)": {
        "us": [
            {"code": "GRID", "name": "퍼스트트러스트 스마트그리드 ETF"},
            {"code": "ETN", "name": "이튼"},
            {"code": "GEV", "name": "GE 버노바"},
        ]
    },
    "☀️신재생/태양광": {
        "us": [
            {"code": "TAN", "name": "인베스코 태양광 ETF"},
            {"code": "FSLR", "name": "퍼스트솔라"},
            {"code": "ENPH", "name": "엔페이즈"},
        ]
    },
    "🤖로봇": {
        "us": [
            {"code": "BOTZ", "name": "글로벌엑스 로봇&AI ETF"},
            {"code": "ISRG", "name": "인튜이티브 서지컬"},
            {"code": "SYM", "name": "심보틱"},
        ]
    },
    "⚛️양자컴퓨팅": {
        "us": [
            {"code": "QTUM", "name": "디파이언스 퀀텀&머신러닝 ETF"},
            {"code": "IONQ", "name": "아이온큐"},
            {"code": "QBTS", "name": "디웨이브 퀀텀"},
        ]
    },
    "💳결제/카드네트워크": {
        "us": [
            {"code": "IPAY", "name": "앰플리파이 디지털페이먼츠 ETF"},
            {"code": "V", "name": "비자"},
            {"code": "MA", "name": "마스터카드"},
        ]
    },
    "🏦은행": {
        "us": [
            {"code": "KBWB", "name": "인베스코 KBW 은행 ETF"},
            {"code": "JPM", "name": "JP모건체이스"},
            {"code": "BAC", "name": "뱅크오브아메리카"},
        ]
    },
    "🧾자산운용/투자": {
        "us": [
            {"code": "KCE", "name": "SPDR S&P 캐피탈마켓 ETF"},
            {"code": "BRK-B", "name": "버크셔 해서웨이"},
            {"code": "BLK", "name": "블랙록"},
        ]
    },
}

# 기간 옵션
PERIOD_OPTIONS = {
    "3일": 3,
    "5일": 5,
    "10일": 10,
    "20일": 20,
    "40일": 40,
    "60일": 60,
    "6개월": 126,
    "1년": 252,
    "1년6개월": 378,
    "2년": 504,
    "3년": 756,
    "4년": 1008,
    "5년": 1260,
    "6년": 1512,
    "7년": 1764,
    "8년": 2016,
    "9년": 2268,
    "10년": 2520,
}

# 벤치마크 지수 옵션
BENCHMARK_OPTIONS = {
    "코스피": {"ticker": "^KS11", "name": "코스피", "emoji": "📈", "color": "#00FF7F", "market": "kospi", "region": "kr"},
    "코스닥": {"ticker": "^KQ11", "name": "코스닥", "emoji": "📊", "color": "#00BFFF", "market": "kosdaq", "region": "kr"},
    "나스닥": {"ticker": "^IXIC", "name": "나스닥", "emoji": "🇺🇸", "color": "#FF3366", "market": "us", "region": "us"},
}

# 색상 팔레트 (섹터별 - 한국 + 미국)
SECTOR_COLORS = {
    # 지수 비교
    "📊지수": "#FFD700",
    # 한국 섹터
    "🔬반도체": "#E74C3C",
    "🚗자동차": "#3498DB",
    "🚢조선": "#9B59B6",
    "⚙️철강": "#E67E22",
    "🧪화학": "#1ABC9C",
    "☀️태양광/에너지": "#FFD93D",
    "🛡️방산/우주": "#34495E",
    "🔋2차전지": "#27AE60",
    "💊바이오": "#E91E63",
    "🏦금융": "#795548",
    "📈증권": "#8D6E63",
    "💻인터넷": "#00BCD4",
    "☢️원자력": "#FF5722",
    "⚡전력인프라": "#FFC107",
    "🤖로봇": "#9E9E9E",
    "📡통신": "#607D8B",
    "⛽에너지/정유": "#4E342E",
    "🏗️건설": "#78909C",
    "🛒유통": "#FF7043",
    "💄화장품": "#FF69B4",
    "🎤케이팝": "#9C27B0",
    "✈️여행": "#03A9F4",
    "🍔푸드": "#8BC34A",
    "🎮게임": "#673AB7",
    "🩺의료기기": "#00ACC1",
    "📺콘텐츠/미디어": "#F44336",
    
    # 미국 섹터 - 반도체/AI 하드웨어
    "🧠AI/가속기 반도체": "#E74C3C",
    "🏭반도체_파운드리/제조": "#C0392B",
    "🛠️반도체_장비": "#D35400",
    "💾반도체_메모리/스토리지": "#E67E22",
    # 미국 섹터 - 인터넷/플랫폼
    "🔎검색/광고플랫폼": "#3498DB",
    "👥소셜/커뮤니티": "#9B59B6",
    "🛒이커머스": "#FF9800",
    "🏷️리테일(오프라인)": "#F39C12",
    # 미국 섹터 - 클라우드/SW
    "☁️클라우드/엔터프라이즈": "#00ACC1",
    "📊데이터/AI 분석SW": "#00BCD4",
    # 미국 섹터 - 보안/미디어
    "🛡️사이버보안": "#607D8B",
    "📺미디어/스트리밍": "#F44336",
    # 미국 섹터 - 모빌리티/에너지
    "🚗전기차/EV": "#4CAF50",
    "⚡전력인프라(그리드)": "#FFC107",
    "☀️신재생/태양광": "#FFEB3B",
    # 미국 섹터 - 로봇/양자
    "🤖로봇": "#9E9E9E",
    "⚛️양자컴퓨팅": "#7C4DFF",
    # 미국 섹터 - 금융
    "💳결제/카드네트워크": "#795548",
    "🏦은행": "#8D6E63",
    "🧾자산운용/투자": "#6D4C41",
}

# 지수별 색상 (섹터별 지수 비교 시 사용)
INDEX_COLORS = {
    "^KS11": "#00FF7F",    # 코스피 - 밝은 형광 연두
    "^KQ11": "#00BFFF",    # 코스닥 - 밝은 형광 하늘
    "^IXIC": "#FFFF00",    # 나스닥 - 밝은 형광 노랑
    "^GSPC": "#FF69B4",    # S&P500 - 핫핑크
    "^DJI": "#FF8C00",     # 다우존스 - 다크오렌지
    "코스닥": "#00BFFF",
    "코스피": "#00FF7F",
    "나스닥": "#FFFF00",
    "S&P500": "#FF69B4",
    "다우존스": "#FF8C00",
}

# 선 스타일 옵션
LINE_STYLES = {
    "solid": "실선",
    "dash": "점선",
    "dot": "도트",
    "dashdot": "점선+도트",
}

# 글씨 크기 (고정)
FONT_SIZE = 14


# ========================================================================================
# 데이터 수집 함수
# ========================================================================================
@st.cache_data(ttl=3600)
def get_batch_stock_data(tickers_tuple, start_date, end_date):
    """yfinance로 여러 주식/지수 데이터 한 번에 가져오기 (배치 다운로드)"""
    tickers = list(tickers_tuple)  # tuple을 list로 변환 (캐시 키용)
    if not tickers:
        return pd.DataFrame()
    try:
        data = yf.download(tickers, start=start_date, end=end_date, progress=False, group_by='ticker', threads=True)
        if data.empty:
            return pd.DataFrame()

        # 단일 티커인 경우
        if len(tickers) == 1:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            df = data[['Close']].copy()
            df.columns = [tickers[0]]
            df.index = pd.to_datetime(df.index).tz_localize(None)
            return df

        # 여러 티커인 경우: Close 가격만 추출
        result = pd.DataFrame()
        for ticker in tickers:
            try:
                if ticker in data.columns.get_level_values(0):
                    close_data = data[ticker]['Close']
                    result[ticker] = close_data
            except:
                pass

        if not result.empty:
            result.index = pd.to_datetime(result.index).tz_localize(None)
        return result
    except Exception as e:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_stock_data(ticker, name, start_date, end_date):
    """yfinance로 주식/지수 데이터 가져오기 (단일 종목용 - 호환성 유지)"""
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            return pd.DataFrame()
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        df = data[['Close']].rename(columns={'Close': name})
        df.index = pd.to_datetime(df.index).tz_localize(None)
        return df
    except Exception as e:
        return pd.DataFrame()


def normalize_data(df, method='rebase100'):
    """데이터 표준화"""
    if df.empty:
        return df
    first_valid = df.apply(lambda x: x.dropna().iloc[0] if len(x.dropna()) > 0 else 1)
    if method == 'rebase100':
        return ((df / first_valid) * 100).round(1)
    else:
        return (((df / first_valid) - 1) * 100).round(1)


def calculate_relative_strength(df, benchmark_col='코스피'):
    """벤치마크 대비 상대강도 계산"""
    if benchmark_col not in df.columns:
        return pd.DataFrame()
    result = pd.DataFrame(index=df.index)
    bench_first = df[benchmark_col].dropna().iloc[0] if len(df[benchmark_col].dropna()) > 0 else 1
    bench_return = ((df[benchmark_col] / bench_first) - 1) * 100
    for col in df.columns:
        if col != benchmark_col:
            first_val = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else 1
            stock_return = ((df[col] / first_val) - 1) * 100
            result[col] = (stock_return - bench_return).round(1)
    return result


def calculate_outperform_days(relative_df):
    """연속 아웃퍼폼/언더퍼폼 일수 계산"""
    results = {}
    for col in relative_df.columns:
        series = relative_df[col].dropna()
        if len(series) < 2:
            results[col] = {'days': 0, 'status': '-', 'relative_return': 0}
            continue
        latest = series.iloc[-1]
        is_outperform = latest > 0
        count = 0
        for i in range(len(series)-1, -1, -1):
            if (series.iloc[i] > 0) == is_outperform:
                count += 1
            else:
                break
        results[col] = {
            'days': count,
            'status': '🔥 주도' if is_outperform else '❄️ 소외',
            'relative_return': latest
        }
    return results


def search_korean_stocks(keyword):
    """한국 주식 검색"""
    all_stocks = [
        {"code": "005930.KS", "name": "삼성전자"},
        {"code": "000660.KS", "name": "SK하이닉스"},
        {"code": "005380.KS", "name": "현대차"},
        {"code": "000270.KS", "name": "기아"},
        {"code": "005490.KS", "name": "POSCO홀딩스"},
        {"code": "051910.KS", "name": "LG화학"},
        {"code": "006400.KS", "name": "삼성SDI"},
        {"code": "035420.KS", "name": "NAVER"},
        {"code": "035720.KS", "name": "카카오"},
        {"code": "068270.KS", "name": "셀트리온"},
        {"code": "207940.KS", "name": "삼성바이오로직스"},
        {"code": "012450.KS", "name": "한화에어로스페이스"},
        {"code": "047810.KS", "name": "한국항공우주"},
        {"code": "079550.KS", "name": "LIG넥스원"},
        {"code": "042660.KS", "name": "한화오션"},
        {"code": "329180.KS", "name": "HD현대중공업"},
        {"code": "009540.KS", "name": "HD한국조선해양"},
        {"code": "373220.KS", "name": "LG에너지솔루션"},
        {"code": "247540.KS", "name": "에코프로비엠"},
        {"code": "086520.KS", "name": "에코프로"},
        {"code": "003670.KS", "name": "포스코퓨처엠"},
        {"code": "105560.KS", "name": "KB금융"},
        {"code": "055550.KS", "name": "신한지주"},
        {"code": "086790.KS", "name": "하나금융지주"},
        {"code": "096770.KS", "name": "SK이노베이션"},
        {"code": "004020.KS", "name": "현대제철"},
        {"code": "066570.KS", "name": "LG전자"},
        {"code": "003550.KS", "name": "LG"},
        {"code": "034730.KS", "name": "SK"},
        {"code": "017670.KS", "name": "SK텔레콤"},
        {"code": "030200.KS", "name": "KT"},
        {"code": "032830.KS", "name": "삼성생명"},
        {"code": "010950.KS", "name": "S-Oil"},
        {"code": "009150.KS", "name": "삼성전��"},
        {"code": "028260.KS", "name": "삼성물산"},
        {"code": "018260.KS", "name": "삼성에스디에스"},
        {"code": "000810.KS", "name": "삼성화재"},
        {"code": "036570.KS", "name": "엔씨소프트"},
        {"code": "251270.KS", "name": "넷마블"},
        {"code": "263750.KS", "name": "펄어비스"},
        {"code": "259960.KS", "name": "크래프톤"},
        {"code": "352820.KS", "name": "하이브"},
        {"code": "011200.KS", "name": "HMM"},
        {"code": "402340.KS", "name": "SK스퀘어"},
        {"code": "000100.KS", "name": "유한양행"},
        {"code": "128940.KS", "name": "한미약품"},
        {"code": "302440.KS", "name": "SK바이오사이언스"},
        {"code": "326030.KS", "name": "SK바이오팜"},
        {"code": "010130.KS", "name": "고려아연"},
        {"code": "011070.KS", "name": "LG이노텍"},
        {"code": "034220.KS", "name": "LG디스플레이"},
        {"code": "267250.KS", "name": "HD현대"},
        {"code": "010620.KS", "name": "HD현대미포"},
        {"code": "241560.KS", "name": "두산밥캣"},
        {"code": "042700.KS", "name": "한미반도체"},
        {"code": "000720.KS", "name": "현대건설"},
        {"code": "006360.KS", "name": "GS건설"},
        {"code": "047040.KS", "name": "대우건설"},
        {"code": "323410.KS", "name": "카카오뱅크"},
        {"code": "377300.KS", "name": "카카오페이"},
        {"code": "293490.KS", "name": "카카오게임즈"},
        {"code": "099320.KQ", "name": "쎄트렉아이"},
        {"code": "095340.KQ", "name": "ISC"},
        {"code": "357780.KQ", "name": "솔브레인"},
        {"code": "041510.KQ", "name": "에스엠"},
        {"code": "122870.KQ", "name": "와이지엔터테인먼트"},
        {"code": "035900.KQ", "name": "JYP Ent."},
        {"code": "293480.KQ", "name": "하나기술"},
        {"code": "039030.KQ", "name": "이오테크닉스"},
        {"code": "214150.KQ", "name": "클래시스"},
        {"code": "145020.KQ", "name": "휴젤"},
        {"code": "196170.KQ", "name": "알테오젠"},
        {"code": "028300.KQ", "name": "에이치엘비"},
        {"code": "067160.KQ", "name": "아프리카TV"},
        {"code": "240810.KQ", "name": "원익IPS"},
        {"code": "058470.KQ", "name": "리노공업"},
        {"code": "272210.KS", "name": "한화시스템"},
    ]
    results = []
    keyword_lower = keyword.lower()
    for stock in all_stocks:
        if keyword_lower in stock['name'].lower() or keyword in stock['code']:
            results.append(stock)
            if len(results) >= 15:
                break
    return results


def search_us_stocks(keyword):
    """미국 주식 검색"""
    all_stocks = [
        # AI/가속기 반도체
        {"code": "NVDA", "name": "NVIDIA"},
        {"code": "AVGO", "name": "Broadcom"},
        {"code": "AMD", "name": "AMD"},
        # 반도체 파운드리/제조
        {"code": "TSM", "name": "TSMC"},
        {"code": "INTC", "name": "Intel"},
        {"code": "GFS", "name": "GlobalFoundries"},
        # 반도체 장비
        {"code": "LRCX", "name": "Lam Research"},
        {"code": "AMAT", "name": "Applied Materials"},
        {"code": "KLAC", "name": "KLA Corp"},
        {"code": "ASML", "name": "ASML"},
        # 반도체 메모리/스토리지
        {"code": "MU", "name": "Micron"},
        {"code": "WDC", "name": "Western Digital"},
        {"code": "STX", "name": "Seagate"},
        # 검색/광고플랫폼
        {"code": "GOOG", "name": "Alphabet"},
        {"code": "APP", "name": "AppLovin"},
        {"code": "TTD", "name": "The Trade Desk"},
        # 소셜/커뮤니티
        {"code": "META", "name": "Meta"},
        {"code": "PINS", "name": "Pinterest"},
        {"code": "SNAP", "name": "Snap"},
        # 이커머스
        {"code": "AMZN", "name": "Amazon"},
        {"code": "PDD", "name": "PDD Holdings"},
        {"code": "MELI", "name": "MercadoLibre"},
        # 리테일(오프라인)
        {"code": "WMT", "name": "Walmart"},
        {"code": "COST", "name": "Costco"},
        {"code": "TGT", "name": "Target"},
        # 클라우드/엔터프라이즈
        {"code": "MSFT", "name": "Microsoft"},
        {"code": "ORCL", "name": "Oracle"},
        {"code": "NOW", "name": "ServiceNow"},
        # 데이터/AI 분석SW
        {"code": "PLTR", "name": "Palantir"},
        {"code": "SNOW", "name": "Snowflake"},
        {"code": "DDOG", "name": "Datadog"},
        # 사이버보안
        {"code": "PANW", "name": "Palo Alto"},
        {"code": "CRWD", "name": "CrowdStrike"},
        {"code": "FTNT", "name": "Fortinet"},
        {"code": "ZS", "name": "Zscaler"},
        {"code": "NET", "name": "Cloudflare"},
        # 미디어/스트리밍
        {"code": "NFLX", "name": "Netflix"},
        {"code": "CMCSA", "name": "Comcast"},
        {"code": "ROKU", "name": "Roku"},
        {"code": "DIS", "name": "Disney"},
        # 전기차/EV
        {"code": "TSLA", "name": "Tesla"},
        {"code": "RIVN", "name": "Rivian"},
        {"code": "LCID", "name": "Lucid"},
        {"code": "NIO", "name": "NIO"},
        # 전력인프라(그리드)
        {"code": "GEV", "name": "GE Vernova"},
        {"code": "ETN", "name": "Eaton"},
        {"code": "CEG", "name": "Constellation Energy"},
        # 신재생/태양광
        {"code": "FSLR", "name": "First Solar"},
        {"code": "ENPH", "name": "Enphase"},
        {"code": "SEDG", "name": "SolarEdge"},
        # 로봇
        {"code": "ISRG", "name": "Intuitive Surgical"},
        {"code": "SYM", "name": "Symbotic"},
        {"code": "PRCT", "name": "PROCEPT BioRobotics"},
        # 양자컴퓨팅
        {"code": "IONQ", "name": "IonQ"},
        {"code": "RGTI", "name": "Rigetti"},
        {"code": "QBTS", "name": "D-Wave"},
        # 결제/카드네트워크
        {"code": "V", "name": "Visa"},
        {"code": "MA", "name": "Mastercard"},
        {"code": "AXP", "name": "American Express"},
        # 은행
        {"code": "JPM", "name": "JPMorgan"},
        {"code": "BAC", "name": "Bank of America"},
        {"code": "GS", "name": "Goldman Sachs"},
        # 자산운용/투자
        {"code": "BRK-B", "name": "Berkshire Hathaway"},
        {"code": "BLK", "name": "BlackRock"},
        # 기타
        {"code": "AAPL", "name": "Apple"},
        {"code": "JNJ", "name": "Johnson & Johnson"},
        {"code": "PFE", "name": "Pfizer"},
        {"code": "UNH", "name": "UnitedHealth"},
        {"code": "PG", "name": "Procter & Gamble"},
        {"code": "KO", "name": "Coca-Cola"},
        {"code": "PEP", "name": "PepsiCo"},
        {"code": "MCD", "name": "McDonald's"},
        {"code": "NKE", "name": "Nike"},
        {"code": "SBUX", "name": "Starbucks"},
    ]
    results = []
    keyword_lower = keyword.lower()
    for stock in all_stocks:
        if keyword_lower in stock['name'].lower() or keyword_lower in stock['code'].lower():
            results.append(stock)
            if len(results) >= 15:
                break
    return results


def get_sector_from_col(col_name):
    """컬럼명에서 섹터 추출"""
    if '[' in col_name and ']' in col_name:
        return col_name.split(']')[0] + ']'
    return None


# ========================================================================================
# 메인 앱
# ========================================================================================
def main():
    # 글씨 크기 고정
    font_size = FONT_SIZE

    # ========== 사이드바 설정 ==========
    with st.sidebar:
        # 기간 선택 (아코디언)
        with st.expander("**📅 기간**", expanded=False):
            period_name = st.radio(
                "기간",
                options=list(PERIOD_OPTIONS.keys()),
                index=2,  # 기본값: 10일
                label_visibility="collapsed"
            )
        period_days = PERIOD_OPTIONS[period_name]

        st.divider()

        # 표준화 방법
        st.markdown("**📐 표준화 방법**")
        normalize_method = st.radio(
            "방식",
            options=['rebase100', 'return'],
            format_func=lambda x: "시작=100" if x == 'rebase100' else "수익률%",
            horizontal=True,
            index=1,  # 기본값: 수익률%
            label_visibility="collapsed"
        )

        st.divider()

        # 차트 스타일 설정
        st.markdown("**🎨 선 스타일**")
        stock_line_width = st.slider("두께", 1, 4, 1, key="stock_width")  # 기본값: 1
        stock_line_style = st.selectbox(
            "스타일",
            options=list(LINE_STYLES.keys()),
            format_func=lambda x: LINE_STYLES[x],
            index=2,  # 기본값: 도트
            key="stock_style"
        )

        st.divider()

        # 지수 선택 (섹터 선택 바로 위)
        st.markdown("**📊 지수별**")
        benchmark_name = st.radio(
            "지수",
            options=list(BENCHMARK_OPTIONS.keys()),
            horizontal=True,
            index=0,  # 기본값: 코스피
            label_visibility="collapsed"
        )
        benchmark_info = BENCHMARK_OPTIONS[benchmark_name]

        # 지역에 따라 섹터 딕셔너리 선택
        region = benchmark_info.get('region', 'kr')
        SECTORS = SECTORS_KR if region == 'kr' else SECTORS_US

        st.divider()

        # 종목 유형 필터 (전체/ETF)
        st.markdown("**🏷️ 종목 유형**")
        stock_type_filter = st.radio(
            "유형",
            options=["전체", "ETF만"],
            horizontal=True,
            index=1,  # 기본값: ETF만
            label_visibility="collapsed"
        )

        st.divider()

        # 섹터 선택 (기본값: 모든 섹터)
        st.markdown("**🏭 섹터 선택**")

        # 지역 변경 시 섹터 선택 초기화
        if 'last_region' not in st.session_state:
            st.session_state.last_region = region
        if st.session_state.last_region != region:
            st.session_state.selected_sectors = list(SECTORS.keys())
            st.session_state.last_region = region

        # 섹터 선택 상태 관리
        if 'selected_sectors' not in st.session_state:
            st.session_state.selected_sectors = list(SECTORS.keys())

        # 유효한 섹터만 필터링 (지역 변경 시 잘못된 섹터 제거)
        valid_sectors = [s for s in st.session_state.selected_sectors if s in SECTORS]
        if not valid_sectors:
            valid_sectors = list(SECTORS.keys())

        selected_sectors = st.multiselect(
            "섹터",
            options=list(SECTORS.keys()),
            default=valid_sectors,
            label_visibility="collapsed"
        )
        st.session_state.selected_sectors = selected_sectors

        st.divider()

        # 종목 검색 추가
        search_label = "**🔍 종목 추가**" if region == 'kr' else "**🔍 Stock Search**"
        st.markdown(search_label)
        placeholder = "종목명 검색..." if region == 'kr' else "Search stocks..."
        search_keyword = st.text_input("검색", label_visibility="collapsed", placeholder=placeholder)

        if search_keyword and len(search_keyword) >= 2:
            # 지역에 따라 검색 함수 선택
            search_results = search_korean_stocks(search_keyword) if region == 'kr' else search_us_stocks(search_keyword)
            if search_results:
                selected_search = st.selectbox(
                    "결과",
                    options=search_results,
                    format_func=lambda x: f"{x['name']}",
                    label_visibility="collapsed"
                )
            else:
                st.caption("검색 결과 없음")
                selected_search = None
        else:
            selected_search = None

        if 'custom_stocks' not in st.session_state:
            st.session_state.custom_stocks = []

        if selected_search and st.button("➕ 추가", use_container_width=True):
            if selected_search not in st.session_state.custom_stocks:
                st.session_state.custom_stocks.append(selected_search)
                st.rerun()

        if st.session_state.custom_stocks:
            for i, s in enumerate(st.session_state.custom_stocks):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.caption(f"📌 {s['name']}")
                with col2:
                    if st.button("✕", key=f"del_{i}"):
                        st.session_state.custom_stocks.pop(i)
                        st.rerun()


    # ========== CSS (Linear-Inspired Premium Dark) ==========
    st.markdown("""
    <style>
        /* ====== GLOBAL ====== */
        * { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; }
        .stApp { background-color: #0D0D0E !important; }

        .main .block-container {
            padding: 1rem 2rem;
            max-width: 1400px;
        }

        /* ====== SIDEBAR ====== */
        section[data-testid="stSidebar"] {
            width: 260px !important;
            background: #111113 !important;
            border-right: 1px solid rgba(255,255,255,0.08) !important;
        }
        div[data-testid="stSidebarContent"] {
            padding: 6px 12px;
        }
        div[data-testid="stSidebarContent"] p strong {
            color: #777 !important;
            font-size: 14px !important;
            line-height: 20px !important;
            text-transform: none;
            letter-spacing: 0;
            font-weight: 600 !important;
        }
        div[data-testid="stSidebarContent"] hr {
            margin: 4px 0 !important;
            border-color: rgba(255,255,255,0.06);
        }

        /* ====== TABS (Linear underline) ====== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background: transparent;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            border-radius: 0;
            padding: 0;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            font-weight: 500;
            font-size: 13px;
            border-radius: 0;
            color: #666;
            border-bottom: 2px solid transparent;
            transition: color 0.15s ease;
            background: transparent !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #9B9B9B;
            background: transparent !important;
        }
        .stTabs [aria-selected="true"] {
            color: #EDEDED !important;
            border-bottom-color: #787EE7 !important;
            background: transparent !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #787EE7 !important;
        }
        .stTabs [data-baseweb="tab-border"] {
            display: none;
        }

        /* ====== RADIO (compact, unified with checkbox) ====== */
        .stRadio > div { gap: 0px !important; }
        section[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] { display: none !important; }
        .stRadio label {
            padding: 3px 10px !important;
            border-radius: 6px !important;
            font-size: 11px !important;
            font-weight: 500 !important;
            line-height: 14px !important;
            min-height: 26px !important;
            display: flex !important;
            align-items: center !important;
            background: transparent;
            border: none;
            transition: all 0.12s ease;
        }
        .stRadio label p, .stRadio label span, .stRadio label div {
            font-size: 11px !important;
            line-height: 14px !important;
        }
        .stRadio label:hover {
            background: rgba(255,255,255,0.04);
        }
        .stRadio label[data-checked="true"] {
            background: rgba(120,126,231,0.12) !important;
            color: #EDEDED !important;
        }

        /* ====== EXPANDER (compact) ====== */
        div[data-testid="stExpander"] {
            border: 1px solid rgba(255,255,255,0.06);
            background: transparent;
            border-radius: 8px;
            margin-bottom: 0px !important;
        }
        div[data-testid="stExpander"] details summary {
            padding: 3px 8px !important;
            min-height: 28px !important;
        }
        div[data-testid="stExpander"] details summary p,
        div[data-testid="stExpander"] details summary span {
            font-size: 12px !important;
            font-weight: 500 !important;
            line-height: 16px !important;
            color: #9B9B9B !important;
        }

        /* ====== CHECKBOX (compact, unified with radio) ====== */
        .stCheckbox { padding: 0 !important; margin: 0 !important; min-height: 20px !important; }
        .stCheckbox label {
            font-size: 11px !important;
            font-weight: 500 !important;
            line-height: 14px !important;
            padding: 2px 10px !important;
            gap: 6px !important;
            min-height: 26px !important;
            display: flex !important;
            align-items: center !important;
            border-radius: 6px;
            transition: background 0.12s ease;
        }
        .stCheckbox label:hover {
            background: rgba(255,255,255,0.04);
        }
        .stCheckbox label span, .stCheckbox label p {
            font-size: 11px !important;
            line-height: 14px !important;
            margin: 0 !important;
        }
        .stCheckbox label div[data-testid="stCheckboxIcon"] {
            width: 14px !important;
            height: 14px !important;
            min-width: 14px !important;
        }
        div[data-testid="stExpander"] [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 2px 6px 2px 6px !important;
        }

        /* ====== MULTISELECT (sidebar-dense) ====== */
        .stMultiSelect [data-baseweb="tag"] {
            background: transparent;
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 6px;
            font-size: 11px;
            height: 24px;
            line-height: 24px;
        }
        .stMultiSelect [data-baseweb="input"] {
            font-size: 13px !important;
        }

        /* ====== METRIC (flat card) ====== */
        div[data-testid="stMetric"] {
            background: #161618;
            border-radius: 8px;
            padding: 16px 20px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: none;
        }
        div[data-testid="stMetric"] label {
            font-size: 11px;
            color: #666 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 20px;
            font-weight: 600;
            color: #EDEDED;
        }
        div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
            font-size: 12px;
        }

        /* ====== DATAFRAME ====== */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.08);
        }

        /* ====== BUTTON (sidebar-dense) ====== */
        .stButton button {
            border-radius: 6px;
            font-weight: 500;
            font-size: 11px;
            height: 28px;
            padding: 0 12px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.03);
            color: #9B9B9B;
            transition: all 0.12s ease;
        }
        .stButton button:hover {
            background: rgba(255,255,255,0.06);
            border-color: rgba(255,255,255,0.12);
            color: #EDEDED;
        }

        /* ====== DROPDOWN MENU ITEMS (match 11px) ====== */
        [data-baseweb="menu"] [role="option"],
        [data-baseweb="popover"] [role="option"],
        [data-baseweb="menu"] li,
        [data-baseweb="select"] [role="option"],
        ul[role="listbox"] li {
            font-size: 11px !important;
            padding: 4px 10px !important;
            min-height: 26px !important;
            line-height: 14px !important;
        }
        [data-baseweb="popover"],
        [data-baseweb="menu"] {
            font-size: 11px !important;
        }

        /* ====== EXPANDER STOCK LIST (dense) ====== */
        div[data-testid="stExpander"] [data-testid="stVerticalBlock"] > div {
            gap: 0px !important;
        }
        div[data-testid="stExpander"] .stCheckbox {
            min-height: 18px !important;
        }
        div[data-testid="stExpander"] .stCheckbox label {
            min-height: 22px !important;
            padding: 1px 8px !important;
        }

        /* ====== FORM (compact) ====== */
        .stSlider { padding-top: 0 !important; margin-bottom: -4px !important; }
        .stSlider label { font-size: 10px !important; font-weight: 500 !important; color: #555 !important; line-height: 14px !important; }
        .stSelectbox label { font-size: 10px !important; font-weight: 500 !important; color: #555 !important; line-height: 14px !important; }
        .stSelectbox [data-baseweb="select"] {
            font-size: 11px !important;
        }
        .stSelectbox [data-baseweb="select"] > div {
            min-height: 26px !important;
            border-radius: 6px !important;
        }
        .stTextInput input {
            height: 26px !important;
            font-size: 11px !important;
            border-radius: 6px !important;
        }

        /* ====== SIDEBAR DENSITY ====== */
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
            gap: 0px !important;
        }
        section[data-testid="stSidebar"] .stMarkdown {
            margin-bottom: 2px !important;
        }
        section[data-testid="stSidebar"] .stMarkdown p {
            font-size: 13px !important;
            line-height: 18px !important;
        }

        /* ====== ACCENT COLOR (#787EE7 soft purple-blue, replaces red) ====== */
        /* Radio dot - all possible Streamlit DOM variants */
        [data-baseweb="radio"] div[aria-checked="true"] > div:first-child,
        [data-baseweb="radio"] [aria-checked="true"] > div:first-child,
        [role="radio"][aria-checked="true"] > div:first-child,
        [role="radio"][aria-checked="true"] > div > div {
            background-color: #787EE7 !important;
            border-color: #787EE7 !important;
        }
        [data-baseweb="radio"] div:not([aria-checked="true"]) > div:first-child,
        [role="radio"]:not([aria-checked="true"]) > div:first-child {
            border-color: rgba(255,255,255,0.2) !important;
        }
        /* Checkbox box + checkmark SVG */
        .stCheckbox svg { fill: #787EE7 !important; }
        [data-baseweb="checkbox"] [aria-checked="true"] > span:first-child,
        [data-baseweb="checkbox"] [aria-checked="true"] > div:first-child,
        [role="checkbox"][aria-checked="true"] > span:first-child {
            background-color: #787EE7 !important;
            border-color: #787EE7 !important;
        }
        [data-baseweb="checkbox"] span:first-child,
        [data-baseweb="checkbox"] > div:first-child {
            border-color: rgba(255,255,255,0.2) !important;
            border-radius: 4px !important;
        }
        /* Slider thumb */
        .stSlider [data-baseweb="slider"] div[role="slider"] {
            background-color: #787EE7 !important;
        }
        .stSlider [data-testid="stThumbValue"] { color: #787EE7 !important; }
        /* Multiselect tags */
        .stMultiSelect [data-baseweb="tag"] svg { fill: #787EE7 !important; }
        /* Override any inline red (#FF4B4B) that Streamlit injects */
        [style*="rgb(255, 75, 75)"] { color: #787EE7 !important; }
        [style*="background-color: rgb(255, 75, 75)"] { background-color: #787EE7 !important; }
        [style*="border-color: rgb(255, 75, 75)"] { border-color: #787EE7 !important; }

        /* ====== SCROLLBAR ====== */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }
    </style>
    """, unsafe_allow_html=True)

    # ========== 타이틀 ==========
    bench_emoji = benchmark_info['emoji']
    bench_name = benchmark_info['name']
    bench_color = benchmark_info['color']
    market_key = benchmark_info['market']
    region = benchmark_info.get('region', 'kr')
    SECTORS = SECTORS_KR if region == 'kr' else SECTORS_US
    st.markdown(f"""
        <div style='margin-bottom: 16px;'>
            <p style='color: #666; font-size: 11px; text-transform: uppercase; letter-spacing: 2px;
                       margin: 0 0 6px 0; font-weight: 500;'>
                {bench_name.upper()} VS SECTOR / STOCK RELATIVE STRENGTH
            </p>
            <h2 style='margin: 0; font-size: 22px; font-weight: 600; color: #EDEDED; line-height: 1.3;'>
                {bench_emoji} {bench_name} 대비 섹터/종목 상대강도
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # ========== 데이터 수집 (배치 다운로드) ==========
    end_date = datetime.now()
    start_date = end_date - timedelta(days=int(period_days * 3) + 100)

    with st.spinner("📡 데이터 로딩..."):
        # 1. 모든 티커 수집 (벤치마크 + 섹터 종목 + 커스텀 종목)
        ticker_info = {}  # {ticker_code: display_name}
        ticker_info[benchmark_info['ticker']] = bench_name

        ETF_KEYWORDS = ("KODEX", "TIGER", "HANARO", "ACE", "KBSTAR", "SOL", "ARIRANG", "KOSEF", "ETF")
        etf_only = stock_type_filter == "ETF만"

        for sector_name in selected_sectors:
            sector = SECTORS[sector_name]
            for stock_info in sector[market_key]:
                if etf_only and not any(kw in stock_info['name'] for kw in ETF_KEYWORDS):
                    continue
                code = stock_info['code']
                if code not in ticker_info:
                    ticker_info[code] = f"[{sector_name}]{stock_info['name']}"

        for custom in st.session_state.custom_stocks:
            code = custom['code']
            if code not in ticker_info:
                ticker_info[code] = f"[➕추가]{custom['name']}"

        # 2. 배치 다운로드 (한 번의 API 호출)
        all_tickers = tuple(sorted(ticker_info.keys()))  # 캐시 키용 tuple
        batch_data = get_batch_stock_data(all_tickers, start_date, end_date)

        if batch_data.empty or benchmark_info['ticker'] not in batch_data.columns:
            st.error(f"❌ {bench_name} 데이터를 가져올 수 없습니다.")
            return

        # 3. 컬럼명을 표시명으로 변경
        all_data = pd.DataFrame(index=batch_data.index)
        for ticker, display_name in ticker_info.items():
            if ticker in batch_data.columns:
                all_data[display_name] = batch_data[ticker]

    all_data = all_data.dropna(subset=[bench_name]).tail(period_days)
    all_data = all_data.ffill().bfill()

    if all_data.empty or len(all_data) < 2:
        st.warning("⚠️ 데이터가 부족합니다.")
        return

    # 현재 설정 요약 표시 (태그 스타일) - 실제 데이터 날짜 사용
    norm_label = "시작=100" if normalize_method == 'rebase100' else "수익률%"
    data_start = all_data.index[0].strftime('%Y-%m-%d')
    data_end = all_data.index[-1].strftime('%Y-%m-%d')
    st.markdown(f"""
        <div style='display: flex; gap: 6px; margin: 0 0 16px 0; flex-wrap: wrap;'>
            <span style='background: #161618; padding: 4px 10px; border-radius: 4px;
                         font-size: 11px; color: #9B9B9B; border: 1px solid rgba(255,255,255,0.08);'>
                📅 {period_name} · {data_start} ~ {data_end}
            </span>
            <span style='background: #161618; padding: 4px 10px; border-radius: 4px;
                         font-size: 11px; color: #9B9B9B; border: 1px solid rgba(255,255,255,0.08);'>
                📐 {norm_label}
            </span>
            <span style='background: #161618; padding: 4px 10px; border-radius: 4px;
                         font-size: 11px; color: #9B9B9B; border: 1px solid rgba(255,255,255,0.08);'>
                🏭 {len(selected_sectors)}개 섹터
            </span>
            <span style='background: #161618; padding: 4px 10px; border-radius: 4px;
                         font-size: 11px; color: #9B9B9B; border: 1px solid rgba(255,255,255,0.08);'>
                🏷️ {stock_type_filter}
            </span>
        </div>
    """, unsafe_allow_html=True)

    # ========== 상대강도 미리 계산 (주도/소외 분류용) ==========
    relative_df_all = calculate_relative_strength(all_data, benchmark_col=bench_name)

    # 주도/소외 종목 분류
    outperform_cols = []  # 상대수익률 > 0
    underperform_cols = []  # 상대수익률 < 0
    for col in relative_df_all.columns:
        if len(relative_df_all[col].dropna()) > 0:
            latest_val = relative_df_all[col].dropna().iloc[-1]
            if latest_val > 0:
                outperform_cols.append(col)
            else:
                underperform_cols.append(col)

    # ========== 공유 그룹 필터 (session_state) ==========
    if 'shared_group_filter' not in st.session_state:
        st.session_state.shared_group_filter = "🔥 주도"

    # ========== 탭 구성 ==========
    tab1, tab2, tab3 = st.tabs(["📈 표준화 차트", "📊 상대강도 차트", "📋 랭킹표"])

    # ========== 탭1: 표준화 차트 ==========
    with tab1:
        normalized = normalize_data(all_data, normalize_method)
        available_cols = [c for c in normalized.columns if c != bench_name]

        # 좁은 왼쪽 컬럼
        col1, col2 = st.columns([1, 5])

        with col1:
            st.markdown("<p style='font-size:10px; font-weight:500; text-transform:uppercase; letter-spacing:1.5px; color:#666; margin:0 0 8px 0;'>BENCHMARK</p>", unsafe_allow_html=True)
            show_bench = st.checkbox(f"{bench_emoji} {bench_name}", value=True, key="show_bench_main")

            # 주도/소외 필터 (session_state 연동)
            st.markdown("<p style='font-size:10px; font-weight:500; text-transform:uppercase; letter-spacing:1.5px; color:#666; margin:16px 0 8px 0;'>GROUP FILTER</p>", unsafe_allow_html=True)
            filter_options = ["전체", "🔥 주도", "❄️ 소외"]
            current_idx = filter_options.index(st.session_state.shared_group_filter) if st.session_state.shared_group_filter in filter_options else 0

            group_filter = st.radio(
                "필터",
                options=filter_options,
                horizontal=True,
                index=current_idx,
                key="group_filter_tab1",
                label_visibility="collapsed"
            )
            # session_state 업데이트
            st.session_state.shared_group_filter = group_filter

            # 필터에 따라 표시할 종목 결정
            if group_filter == "🔥 주도":
                filtered_cols = [c for c in available_cols if c in outperform_cols]
                st.caption(f"🔥 {len(filtered_cols)}개 종목")
            elif group_filter == "❄️ 소외":
                filtered_cols = [c for c in available_cols if c in underperform_cols]
                st.caption(f"❄️ {len(filtered_cols)}개 종목")
            else:
                filtered_cols = available_cols
                st.caption(f"전체 {len(filtered_cols)}개 종목")

            st.markdown("<p style='font-size:10px; font-weight:500; text-transform:uppercase; letter-spacing:1.5px; color:#666; margin:16px 0 8px 0;'>SECTORS</p>", unsafe_allow_html=True)

            # 섹터별로 그룹화하여 표시
            selected_items = []
            processed_cols = set()

            for sector_name in selected_sectors:
                sector_cols = [c for c in filtered_cols if f"[{sector_name}]" in c and c not in processed_cols]
                if sector_cols:
                    with st.expander(sector_name, expanded=False):
                        for idx, col in enumerate(sector_cols):
                            stock_name = col.split(']')[-1]
                            # 주도/소외 표시
                            status_icon = "🔥" if col in outperform_cols else "❄️"
                            default_val = (idx == 0)  # 대표종목만 기본 선택
                            unique_key = f"chk_{sector_name}_{stock_name}_{idx}"
                            if st.checkbox(f"{status_icon} {stock_name}", value=default_val, key=unique_key):
                                selected_items.append(col)
                            processed_cols.add(col)

            # 추가된 종목
            custom_cols = [c for c in filtered_cols if "[➕추가]" in c and c not in processed_cols]
            if custom_cols:
                with st.expander("➕ 추가 종목", expanded=True):
                    for idx, col in enumerate(custom_cols):
                        stock_name = col.split(']')[-1]
                        status_icon = "🔥" if col in outperform_cols else "❄️"
                        unique_key = f"chk_custom_{stock_name}_{idx}"
                        if st.checkbox(f"{status_icon} {stock_name}", value=True, key=unique_key):
                            selected_items.append(col)
                        processed_cols.add(col)

            # 선택된 종목을 session_state에 저장 (탭2, 탭3에서 사용)
            st.session_state.selected_items = selected_items

        with col2:
            fig = go.Figure()

            # 벤치마크 지수 - 선택된 지수 색상, 굵은 실선
            if show_bench:
                # 더블클릭 시에도 유지되는 숨겨진 지수 (범례에 안 보임)
                fig.add_trace(go.Scatter(
                    x=normalized.index,
                    y=normalized[bench_name],
                    name=f'_{bench_name}_always',
                    line=dict(color=bench_color, width=4, dash='solid'),
                    hoverinfo='skip',
                    showlegend=False
                ))
                # 범례에 표시되는 지수
                fig.add_trace(go.Scatter(
                    x=normalized.index,
                    y=normalized[bench_name],
                    name=f'{bench_emoji} {bench_name}',
                    line=dict(color=bench_color, width=4, dash='solid'),
                    hovertemplate=f'%{{x|%Y-%m-%d}}<br>{bench_name}: %{{y:.1f}}<extra></extra>'
                ))

            # 종목별 - 섹터 색상 + 사용자 설정 스타일 (지수는 굵은 실선)
            for col in selected_items:
                sector = get_sector_from_col(col)
                stock_name = col.split(']')[-1] if ']' in col else col

                # 지수인지 확인 (INDEX_COLORS에 있는 이름이면 지수)
                is_index = stock_name in INDEX_COLORS

                if is_index:
                    # 지수는 굵은 실선 + 고유 색상
                    color = INDEX_COLORS.get(stock_name, '#FFD700')
                    line_width = 3
                    line_dash = 'solid'
                else:
                    # 일반 종목은 섹터 색상 + 사용자 설정 스타일
                    color = SECTOR_COLORS.get(sector.replace('[', '').replace(']', ''), '#888888') if sector else '#888888'
                    line_width = stock_line_width
                    line_dash = stock_line_style

                fig.add_trace(go.Scatter(
                    x=normalized.index,
                    y=normalized[col],
                    name=col,
                    line=dict(color=color, width=line_width, dash=line_dash),
                    hovertemplate=f'%{{x|%Y-%m-%d}}<br>{col}: %{{y:.1f}}<extra></extra>'
                ))

            baseline = 100 if normalize_method == 'rebase100' else 0
            fig.add_hline(y=baseline, line_dash="dash", line_color="rgba(255,255,255,0.12)", opacity=0.5)

            y_title = "지수 (시작=100)" if normalize_method == 'rebase100' else "수익률 (%)"
            fig.update_layout(
                height=520,
                margin=dict(l=10, r=10, t=50, b=40),
                xaxis_title="",
                yaxis_title=y_title,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0,
                    font=dict(size=11, color='#9B9B9B'),
                    bgcolor="rgba(0,0,0,0)",
                    itemclick='toggle',
                    itemdoubleclick='toggleothers'
                ),
                hovermode='closest',
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12, color='#666'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.04)', showgrid=True, zeroline=False),
                yaxis=dict(gridcolor='rgba(255,255,255,0.04)', showgrid=True, zeroline=False),
            )

            st.plotly_chart(fig, use_container_width=True, config={
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            })

    # ========== 탭2: 상대강도 차트 (선택된 종목만) ==========
    with tab2:
        # 탭1에서 선택한 종목만 필터링 (session_state 사용)
        tab_selected = st.session_state.get('selected_items', [])
        if not tab_selected:
            tab_selected = available_cols[:6]

        # 탭1과 같은 레이아웃 (왼쪽 컬럼 + 오른쪽 차트)
        col1_t2, col2_t2 = st.columns([1, 5])

        with col1_t2:
            # 그룹 필터 (session_state 연동)
            st.markdown("<p style='font-size:10px; font-weight:500; text-transform:uppercase; letter-spacing:1.5px; color:#666; margin:0 0 8px 0;'>GROUP FILTER</p>", unsafe_allow_html=True)
            filter_options = ["전체", "🔥 주도", "❄️ 소외"]
            current_idx = filter_options.index(st.session_state.shared_group_filter) if st.session_state.shared_group_filter in filter_options else 0

            group_filter_tab2 = st.radio(
                "필터",
                options=filter_options,
                horizontal=True,
                index=current_idx,
                key="group_filter_tab2",
                label_visibility="collapsed"
            )
            # session_state 업데이트
            st.session_state.shared_group_filter = group_filter_tab2

            # 필터 적용
            if group_filter_tab2 == "🔥 주도":
                tab_selected = [c for c in tab_selected if c in outperform_cols]
                st.caption(f"🔥 {len(tab_selected)}개 종목")
            elif group_filter_tab2 == "❄️ 소외":
                tab_selected = [c for c in tab_selected if c in underperform_cols]
                st.caption(f"❄️ {len(tab_selected)}개 종목")
            else:
                st.caption(f"전체 {len(tab_selected)}개 종목")

            # 차트 설명
            st.markdown("<p style='font-size:10px; font-weight:500; text-transform:uppercase; letter-spacing:1.5px; color:#666; margin:20px 0 8px 0;'>RELATIVE STRENGTH</p>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style='font-size:11px; color:#666; line-height:1.8;'>
                <span style='color:{bench_color};'>● 0선</span> = {bench_name}<br>
                <span style='color:#4ade80;'>▲ 양수</span> = 아웃퍼폼<br>
                <span style='color:#f87171;'>▼ 음수</span> = 언더퍼폼
                </div>
            """, unsafe_allow_html=True)

        with col2_t2:
            filtered_data = all_data[[bench_name] + [c for c in tab_selected if c in all_data.columns]]
            relative_df = calculate_relative_strength(filtered_data, benchmark_col=bench_name)

            if not relative_df.empty:
                fig2 = go.Figure()

                for col in relative_df.columns:
                    sector = get_sector_from_col(col)
                    stock_name = col.split(']')[-1] if ']' in col else col

                    # 지수인지 확인
                    is_index = stock_name in INDEX_COLORS

                    if is_index:
                        color = INDEX_COLORS.get(stock_name, '#FFD700')
                        line_width = 3
                        line_dash = 'solid'
                    else:
                        color = SECTOR_COLORS.get(sector.replace('[', '').replace(']', ''), '#888888') if sector else '#888888'
                        line_width = stock_line_width
                        line_dash = stock_line_style

                    fig2.add_trace(go.Scatter(
                        x=relative_df.index,
                        y=relative_df[col],
                        name=col,
                        line=dict(color=color, width=line_width, dash=line_dash),
                        hovertemplate=f'%{{x|%Y-%m-%d}}<br>{col}: %{{y:+.1f}}%p<extra></extra>'
                    ))

                fig2.add_hline(y=0, line_dash="solid", line_color=bench_color, line_width=2)

                max_val = relative_df.max().max() if not relative_df.empty else 10
                min_val = relative_df.min().min() if not relative_df.empty else -10

                fig2.add_hrect(y0=0, y1=max_val*1.1 if max_val > 0 else 10,
                              fillcolor="green", opacity=0.03, line_width=0)
                fig2.add_hrect(y0=min_val*1.1 if min_val < 0 else -10, y1=0,
                              fillcolor="red", opacity=0.03, line_width=0)

                fig2.update_layout(
                    height=520,
                    margin=dict(l=10, r=10, t=50, b=40),
                    xaxis_title="",
                    yaxis_title="상대수익률 (%p)",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="left",
                        x=0,
                        font=dict(size=11, color='#9B9B9B'),
                        bgcolor="rgba(0,0,0,0)",
                        itemclick='toggle',
                        itemdoubleclick='toggleothers'
                    ),
                    hovermode='closest',
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12, color='#666'),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.04)', showgrid=True, zeroline=False),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.04)', showgrid=True, zeroline=False),
                )

                st.plotly_chart(fig2, use_container_width=True, config={
                    'displayModeBar': True,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                })

    # ========== 탭3: 랭킹표 (이전 vs 현재 비교) ==========
    with tab3:
        # 선택된 종목만 랭킹 (session_state 사용)
        tab3_selected = st.session_state.get('selected_items', [])

        # ===== 현재 기간 데이터 (이미 all_data에 있음) =====
        filtered_data_now = all_data[[bench_name] + [c for c in tab3_selected if c in all_data.columns]]
        relative_df_now = calculate_relative_strength(filtered_data_now, benchmark_col=bench_name)

        # ===== 이전 기간 데이터 (한 기�� 전) =====
        # all_data는 이미 period_days로 잘려있으므로, 원본 batch_data에서 이전 기간 추출
        prev_end_idx = len(batch_data) - period_days  # 이전 기간의 끝 인덱스
        prev_start_idx = max(0, prev_end_idx - period_days)  # 이전 기간의 시작 인덱스

        if prev_end_idx > prev_start_idx:
            # 이전 기간 데이터 추출
            prev_batch = batch_data.iloc[prev_start_idx:prev_end_idx]
            prev_data = pd.DataFrame(index=prev_batch.index)
            for ticker, display_name in ticker_info.items():
                if ticker in prev_batch.columns:
                    prev_data[display_name] = prev_batch[ticker]
            prev_data = prev_data.ffill().bfill()

            if not prev_data.empty and bench_name in prev_data.columns:
                filtered_data_prev = prev_data[[bench_name] + [c for c in tab3_selected if c in prev_data.columns]]
                relative_df_prev = calculate_relative_strength(filtered_data_prev, benchmark_col=bench_name)
                has_prev_data = True
            else:
                has_prev_data = False
        else:
            has_prev_data = False

        # ===== 기간 날짜 표시 =====
        current_start = filtered_data_now.index[0].strftime('%Y-%m-%d') if len(filtered_data_now) > 0 else ''
        current_end = filtered_data_now.index[-1].strftime('%Y-%m-%d') if len(filtered_data_now) > 0 else ''

        if has_prev_data and len(filtered_data_prev) > 0:
            prev_start = filtered_data_prev.index[0].strftime('%Y-%m-%d')
            prev_end = filtered_data_prev.index[-1].strftime('%Y-%m-%d')
        else:
            prev_start, prev_end = '', ''

        # ===== 랭킹 데이터 생성 함수 =====
        def create_ranking_df(filtered_data, relative_df, include_rank_col=True):
            if relative_df.empty:
                return pd.DataFrame()
            ranking_data = []
            for col in relative_df.columns:
                if col in filtered_data.columns:
                    first_val = filtered_data[col].iloc[0]
                    last_val = filtered_data[col].iloc[-1]
                    rel_val = relative_df[col].iloc[-1] if len(relative_df[col]) > 0 else 0

                    if pd.isna(first_val) or pd.isna(last_val) or first_val == 0 or pd.isna(rel_val):
                        stock_return = None
                        rel_return = None
                        status = '⚠️'
                    else:
                        stock_return = round((last_val / first_val - 1) * 100, 1)
                        rel_return = round(rel_val, 1)
                        status = '🔥' if rel_return > 0 else '❄️'

                    stock_name = col.split(']')[-1] if ']' in col else col
                    if '[' in col and ']' in col:
                        sector = col.split('[')[1].split(']')[0]
                    else:
                        sector = '-'
                    ranking_data.append({
                        '섹터': sector,
                        '종목': stock_name,
                        '상대수익률': rel_return,
                        '수익률': stock_return,
                        '상태': status,
                        '_full_name': col
                    })
            df = pd.DataFrame(ranking_data)
            if df.empty:
                return df
            df = df.sort_values('상대수익률', ascending=False, na_position='last')
            df['순위'] = range(1, len(df) + 1)
            return df

        # ===== 현재 기간 랭킹 =====
        ranking_now = create_ranking_df(filtered_data_now, relative_df_now)

        # ===== 이전 기간 랭킹 =====
        if has_prev_data:
            ranking_prev = create_ranking_df(filtered_data_prev, relative_df_prev)
        else:
            ranking_prev = pd.DataFrame()

        # ===== 이전 기간 부족 종목 보완 =====
        if not ranking_now.empty:
            prev_names = set(ranking_prev['_full_name']) if not ranking_prev.empty else set()
            missing_rows = []
            for _, row in ranking_now.iterrows():
                if row['_full_name'] not in prev_names:
                    missing_rows.append({
                        '섹터': row['섹터'],
                        '종목': row['종목'],
                        '상대수익률': None,
                        '수익률': None,
                        '상태': '⚠️',
                        '_full_name': row['_full_name'],
                    })
            if missing_rows:
                missing_df = pd.DataFrame(missing_rows)
                if not ranking_prev.empty:
                    ranking_prev = pd.concat([ranking_prev, missing_df], ignore_index=True)
                    ranking_prev = ranking_prev.sort_values('상대수익률', ascending=False, na_position='last')
                else:
                    ranking_prev = missing_df
                ranking_prev['순위'] = range(1, len(ranking_prev) + 1)

            if not ranking_prev.empty and not has_prev_data:
                has_prev_data = True
                if not prev_start:
                    prev_start = '(부족)'
                    prev_end = ''

        # ===== 순위 변동 계산 =====
        if not ranking_now.empty and not ranking_prev.empty:
            prev_valid = set(ranking_prev[ranking_prev['상대수익률'].notna()]['_full_name']) if not ranking_prev.empty else set()
            prev_rank_map = dict(zip(ranking_prev['_full_name'], ranking_prev['순위']))
            rank_changes = []
            for _, row in ranking_now.iterrows():
                full_name = row['_full_name']
                if full_name not in prev_valid:
                    rank_changes.append('⚠️')
                    continue
                curr_rank = row['순위']
                prev_rank = prev_rank_map.get(full_name, curr_rank)
                change = prev_rank - curr_rank
                if change > 0:
                    rank_changes.append(f'▲{change}')
                elif change < 0:
                    rank_changes.append(f'▼{abs(change)}')
                else:
                    rank_changes.append('-')
            ranking_now['변동'] = rank_changes

        # ===== 요약 카드 =====
        c1, c2, c3, c4 = st.columns(4)
        outperform_now = len(ranking_now[ranking_now['상대수익률'] > 0]) if not ranking_now.empty else 0
        underperform_now = len(ranking_now[ranking_now['상대수익률'] < 0]) if not ranking_now.empty else 0

        with c1:
            st.metric("🔥 현재 아웃퍼폼", f"{outperform_now}개")
        with c2:
            st.metric("❄️ 현재 언더퍼폼", f"{underperform_now}개")

        # 최강/최약
        if not ranking_now.empty:
            valid_ranking = ranking_now[ranking_now['상대수익률'].notna()]
            if not valid_ranking.empty:
                best = valid_ranking.iloc[0]
                worst = valid_ranking.iloc[-1]
                with c3:
                    st.metric("🥇 현재 최강", best['종목'], f"{best['상대수익률']:+.1f}%p")
                with c4:
                    st.metric("💀 현재 최약", worst['종목'], f"{worst['상대수익률']:+.1f}%p")

        st.markdown("")

        # ===== 스타일 함수 =====
        def color_relative(val):
            if isinstance(val, (int, float)) and pd.notna(val):
                if val > 0:
                    return 'background-color: rgba(74,222,128,0.15); color: #4ade80'
                elif val < 0:
                    return 'background-color: rgba(248,113,113,0.15); color: #f87171'
            return ''

        def color_change(val):
            if isinstance(val, str):
                if '▲' in val:
                    return 'color: #4ade80; font-weight: 600'
                elif '▼' in val:
                    return 'color: #f87171; font-weight: 600'
            return 'color: #666'

        # ===== 두 개의 테이블 나란히 표시 =====
        if has_prev_data and not ranking_prev.empty:
            col_prev, col_now = st.columns(2)

            # 이전 기간 테이블 (왼쪽)
            with col_prev:
                st.markdown(f"""
                    <p style='text-align:center; color:#666; font-size:11px; font-weight:500;
                              text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>
                    이전 기간 · {prev_start} ~ {prev_end}
                    </p>
                """, unsafe_allow_html=True)

                display_prev = ranking_prev[['순위', '섹터', '종목', '상대수익률', '수익률', '상태']].copy()
                display_prev.index = range(1, len(display_prev) + 1)

                styled_prev = display_prev.style.applymap(
                    color_relative, subset=['상대수익률']
                ).format({
                    '상대수익률': '{:+.1f}%p',
                    '수익률': '{:+.1f}%',
                }, na_rep='⚠️ 기간 부족')
                st.dataframe(styled_prev, use_container_width=True, height=400)

            # 현재 기간 테이블 (오른쪽)
            with col_now:
                st.markdown(f"""
                    <p style='text-align:center; color:#EDEDED; font-size:11px; font-weight:500;
                              text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>
                    현재 기간 · {current_start} ~ {current_end}
                    </p>
                """, unsafe_allow_html=True)

                now_cols = ['순위', '변동', '섹터', '종목', '상대수익률', '수익률', '상태'] if '변동' in ranking_now.columns else ['순위', '섹터', '종목', '상대수익률', '수익률', '상태']
                display_now = ranking_now[now_cols].copy()
                display_now.index = range(1, len(display_now) + 1)

                styler = display_now.style.applymap(
                    color_relative, subset=['상대수익률']
                )
                if '변동' in display_now.columns:
                    styler = styler.applymap(color_change, subset=['변동'])
                styler = styler.format({
                    '상대수익률': '{:+.1f}%p',
                    '수익률': '{:+.1f}%',
                }, na_rep='⚠️ 기간 부족')
                st.dataframe(styler, use_container_width=True, height=400)

        else:
            # 이전 데이터도 보완할 수 없는 경우 현재만 표시
            st.markdown(f"""
                <p style='text-align:center; color:#EDEDED; font-size:11px; font-weight:500;
                          text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>
                현재 기간 · {current_start} ~ {current_end}
                </p>
            """, unsafe_allow_html=True)

            if not ranking_now.empty:
                display_now = ranking_now[['순위', '섹터', '종목', '상대수익률', '수익률', '상태']].copy()
                display_now.index = range(1, len(display_now) + 1)

                styled_now = display_now.style.applymap(
                    color_relative, subset=['상대수익률']
                ).format({
                    '상대수익률': '{:+.1f}%p',
                    '수익률': '{:+.1f}%',
                }, na_rep='⚠️ 기간 부족')
                st.dataframe(styled_now, use_container_width=True, height=420)

    # ========== 하단 가이드 ==========
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    with st.expander("💡 사용 가이드", expanded=False):
        st.markdown("""
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; padding: 12px 0;'>
            <div>
                <p style='color: #9B9B9B; font-weight: 500; font-size: 12px; margin-bottom: 8px;'>기본 사용법</p>
                <p style='color: #666; font-size: 11px; line-height: 1.8; margin: 0;'>
                • 사이드바에서 설정 조절<br>
                • 섹터 토글 열어서 종목 선택<br>
                • 선택한 종목만 차트에 표시
                </p>
            </div>
            <div>
                <p style='color: #9B9B9B; font-weight: 500; font-size: 12px; margin-bottom: 8px;'>차트 조작</p>
                <p style='color: #666; font-size: 11px; line-height: 1.8; margin: 0;'>
                • 범례 클릭: 종목 숨김/표시<br>
                • 범례 더블클릭: 해당 종목만 표시<br>
                • 드래그: 확대 / 더블클릭: 원래대로
                </p>
            </div>
            <div>
                <p style='color: #9B9B9B; font-weight: 500; font-size: 12px; margin-bottom: 8px;'>지표 설명</p>
                <p style='color: #666; font-size: 11px; line-height: 1.8; margin: 0;'>
                • 상대수익률 = 종목 - 벤치마크<br>
                • 🔥 양수 → 아웃퍼폼 (주도)<br>
                • ❄️ 음수 → 언더퍼폼 (소외)
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
