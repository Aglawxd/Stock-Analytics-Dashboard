TICKER_SECTOR = {
    "NVDA": "Semiconductors / AI HW",
    "MRVL": "Semiconductors / AI HW",
    "MU": "Semiconductors / AI HW",
    "AVGO": "Semiconductors / AI HW",
    "ARM": "Semiconductors / AI HW",
    "LRCX" : "Semiconductors / AI HW",
    "TSM" : "Semiconductors / AI HW",
    "CRDO" : 'Semiconductors / AI HW',
    'LITE': 'Semiconductors / AI HW',
    'PLTR': 'Software / AI',
    'APP': 'Software / AI',
    'VRT': 'Data Center Infra',
    'JNJ': 'Healthcare',
    'UNH': 'Healthcare',
    'JPM': 'Banks',
    'BAC': 'Banks',
    'XOM': 'Energy',
    'KO': 'Consumer goods',
    'CAT': 'Industrial',
    'WMT': 'Retail'
}

TICKERS = list(TICKER_SECTOR.keys())

#print(TICKERS)

SECTOR_COLORS = {
    "Semiconductors / AI HW": '#FF6B6B',
    'Software / AI' : ' #FF9F45',
    'Data Center Infra': '#FFD93D',
    'Healthcare': '#4ECDC4',
    'Banks': '#1A8FE3',
    'Energy': '#6A4C93',
    'Consumer goods': '#95D5B2',
    'Industrial': '#577590',
    'Retail': '#F72585',

}
#print(SECTOR_COLORS)

def get_sector(ticker:str) -> str:
    return TICKER_SECTOR.get(ticker,'Unknown')

def get_color(ticker:str) -> str:
    return SECTOR_COLORS.get(get_sector(ticker),'#CCCCCC')

def sector_list() -> list:
    seen = []
    for s in TICKER_SECTOR.values():
        if s not in seen:
            seen.append(s)
    return seen

