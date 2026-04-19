from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import random
import math
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# ─── Mock Data ────────────────────────────────────────────────────────────────

STOCKS = {
    "BBCA": {"name": "Bank Central Asia Tbk", "sector": "Financials", "cap": "large", "price": 9450, "change": 1.2, "pe": 22.4, "pb": 3.8, "roe": 18.5, "dividend": 1.8, "volume": 12500000, "country": "ID", "desc": "Bank terbesar di Indonesia berdasarkan aset."},
    "TLKM": {"name": "Telkom Indonesia Tbk", "sector": "Telecommunications", "cap": "large", "price": 3180, "change": -0.5, "pe": 14.2, "pb": 2.1, "roe": 15.3, "dividend": 4.2, "volume": 45000000, "country": "ID", "desc": "Perusahaan telekomunikasi terbesar di Indonesia."},
    "ASII": {"name": "Astra International Tbk", "sector": "Consumer Discretionary", "cap": "large", "price": 5500, "change": 0.9, "pe": 12.8, "pb": 1.9, "roe": 14.7, "dividend": 3.5, "volume": 8700000, "country": "ID", "desc": "Konglomerat multinasional terkemuka di Indonesia."},
    "BMRI": {"name": "Bank Mandiri Tbk", "sector": "Financials", "cap": "large", "price": 6350, "change": 2.1, "pe": 10.5, "pb": 1.8, "roe": 17.2, "dividend": 5.1, "volume": 32000000, "country": "ID", "desc": "Bank BUMN terbesar di Indonesia."},
    "UNVR": {"name": "Unilever Indonesia Tbk", "sector": "Consumer Staples", "cap": "large", "price": 2150, "change": -1.3, "pe": 28.6, "pb": 15.2, "roe": 72.4, "dividend": 6.8, "volume": 5200000, "country": "ID", "desc": "Perusahaan consumer goods multinasional."},
    "GOTO": {"name": "GoTo Gojek Tokopedia Tbk", "sector": "Technology", "cap": "large", "price": 87, "change": 3.6, "pe": -8.2, "pb": 1.1, "roe": -12.1, "dividend": 0, "volume": 890000000, "country": "ID", "desc": "Ekosistem digital terbesar di Indonesia."},
    "ICBP": {"name": "Indofood CBP Sukses Makmur", "sector": "Consumer Staples", "cap": "large", "price": 10700, "change": 0.5, "pe": 18.3, "pb": 3.4, "roe": 19.8, "dividend": 2.9, "volume": 3100000, "country": "ID", "desc": "Produsen makanan kemasan terbesar di Asia Tenggara."},
    "PGAS": {"name": "Perusahaan Gas Negara Tbk", "sector": "Energy", "cap": "mid", "price": 1680, "change": 1.8, "pe": 8.7, "pb": 1.3, "roe": 15.6, "dividend": 6.2, "volume": 28000000, "country": "ID", "desc": "Distributor gas bumi terbesar di Indonesia."},
    "ANTM": {"name": "Aneka Tambang Tbk", "sector": "Materials", "cap": "mid", "price": 1540, "change": -2.4, "pe": 11.2, "pb": 1.5, "roe": 13.8, "dividend": 3.1, "volume": 41000000, "country": "ID", "desc": "Perusahaan tambang nikel, emas, dan bauksit."},
    "BBRI": {"name": "Bank Rakyat Indonesia Tbk", "sector": "Financials", "cap": "large", "price": 4890, "change": 0.8, "pe": 11.8, "pb": 2.0, "roe": 16.9, "dividend": 4.7, "volume": 67000000, "country": "ID", "desc": "Bank dengan jaringan terluas di Indonesia."},
}

SECTORS = list(set(s["sector"] for s in STOCKS.values()))
NEWS = [
    {"title": "BBCA Catat Laba Bersih Rp 48,6 Triliun di 2024", "source": "Bisnis.com", "time": "2 jam lalu", "ticker": "BBCA", "sentiment": "positive"},
    {"title": "Gojek Perluas Layanan ke 10 Kota Baru", "source": "Kontan", "time": "4 jam lalu", "ticker": "GOTO", "sentiment": "positive"},
    {"title": "IHSG Menguat 0.8% Ditopang Sektor Perbankan", "source": "CNBC Indonesia", "time": "1 jam lalu", "ticker": None, "sentiment": "positive"},
    {"title": "Telkom Investasi Rp 5T untuk Infrastruktur 5G", "source": "Detik Finance", "time": "6 jam lalu", "ticker": "TLKM", "sentiment": "positive"},
    {"title": "Harga Nikel Global Tertekan, Saham Tambang Turun", "source": "Bloomberg Indonesia", "time": "3 jam lalu", "ticker": "ANTM", "sentiment": "negative"},
    {"title": "Unilever Rilis Produk Baru, Target Pertumbuhan 8%", "source": "Kompas", "time": "5 jam lalu", "ticker": "UNVR", "sentiment": "neutral"},
]

DIVIDENDS = [
    {"ticker": "BBCA", "cum_date": "2025-02-14", "payment": "2025-03-01", "amount": 168, "yield": 1.8},
    {"ticker": "TLKM", "cum_date": "2025-02-20", "payment": "2025-03-10", "amount": 133, "yield": 4.2},
    {"ticker": "BMRI", "cum_date": "2025-03-05", "payment": "2025-03-20", "amount": 324, "yield": 5.1},
    {"ticker": "BBRI", "cum_date": "2025-03-12", "payment": "2025-04-01", "amount": 230, "yield": 4.7},
]

GLOSSARY = [
    {"term": "P/E Ratio", "definition": "Price-to-Earnings Ratio: Rasio harga saham terhadap laba per lembar saham. Semakin rendah, semakin murah saham tersebut secara relatif."},
    {"term": "P/B Ratio", "definition": "Price-to-Book Ratio: Rasio harga saham terhadap nilai buku per saham. Nilai di bawah 1 bisa mengindikasikan saham undervalued."},
    {"term": "ROE", "definition": "Return on Equity: Tingkat pengembalian modal pemegang saham. Semakin tinggi ROE, semakin efisien perusahaan menggunakan modal."},
    {"term": "Dividen", "definition": "Pembagian keuntungan perusahaan kepada pemegang saham. Biasanya dibayarkan dalam bentuk uang tunai per lembar saham."},
    {"term": "Lot", "definition": "Satuan pembelian saham di Indonesia. 1 lot = 100 lembar saham."},
    {"term": "IHSG", "definition": "Indeks Harga Saham Gabungan: Indeks yang mencerminkan pergerakan semua saham di Bursa Efek Indonesia."},
    {"term": "Market Cap", "definition": "Kapitalisasi Pasar: Nilai total perusahaan di pasar saham. Dihitung dari harga saham × jumlah saham beredar."},
    {"term": "EPS", "definition": "Earnings Per Share: Laba bersih perusahaan dibagi jumlah saham beredar. Indikator profitabilitas per lembar saham."},
]

def generate_price_history(base_price, days=180):
    history = []
    price = base_price * 0.85
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
        change = random.gauss(0.0005, 0.018)
        price = price * (1 + change)
        open_p = price * (1 + random.gauss(0, 0.005))
        high_p = max(price, open_p) * (1 + random.uniform(0, 0.012))
        low_p = min(price, open_p) * (1 - random.uniform(0, 0.012))
        vol = random.randint(1000000, 50000000)
        history.append({
            "date": date, "open": round(open_p), "high": round(high_p),
            "low": round(low_p), "close": round(price), "volume": vol
        })
    return history

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    sector = request.args.get('sector')
    cap = request.args.get('cap')
    min_pe = request.args.get('min_pe', type=float)
    max_pe = request.args.get('max_pe', type=float)
    min_dividend = request.args.get('min_dividend', type=float)
    q = request.args.get('q', '').upper()

    result = []
    for ticker, data in STOCKS.items():
        if q and q not in ticker and q not in data['name'].upper():
            continue
        if sector and data['sector'] != sector:
            continue
        if cap and data['cap'] != cap:
            continue
        if min_pe is not None and data['pe'] < min_pe:
            continue
        if max_pe is not None and data['pe'] > max_pe:
            continue
        if min_dividend is not None and data['dividend'] < min_dividend:
            continue
        result.append({"ticker": ticker, **data})

    return jsonify(result)

@app.route('/api/stocks/<ticker>', methods=['GET'])
def get_stock(ticker):
    ticker = ticker.upper()
    if ticker not in STOCKS:
        return jsonify({"error": "Stock not found"}), 404
    stock = STOCKS[ticker]
    history = generate_price_history(stock['price'])
    return jsonify({
        "ticker": ticker,
        **stock,
        "history": history,
        "financials": {
            "revenue": [45.2, 48.7, 52.1, 58.4, 63.8],
            "net_income": [12.1, 13.5, 14.8, 16.2, 18.4],
            "total_assets": [245, 268, 295, 318, 342],
            "equity": [85, 92, 101, 112, 125],
            "years": [2020, 2021, 2022, 2023, 2024]
        },
        "analyst": {
            "buy": random.randint(8, 18),
            "hold": random.randint(3, 8),
            "sell": random.randint(0, 4),
            "target_price": round(stock['price'] * random.uniform(1.05, 1.25))
        }
    })

@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    return jsonify(SECTORS)

@app.route('/api/news', methods=['GET'])
def get_news():
    ticker = request.args.get('ticker')
    if ticker:
        filtered = [n for n in NEWS if n.get('ticker') == ticker.upper() or n.get('ticker') is None]
        return jsonify(filtered[:4])
    return jsonify(NEWS)

@app.route('/api/dividends', methods=['GET'])
def get_dividends():
    return jsonify(DIVIDENDS)

@app.route('/api/glossary', methods=['GET'])
def get_glossary():
    return jsonify(GLOSSARY)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    risk = data.get('risk', 'moderate')
    horizon = data.get('horizon', 'medium')
    goal = data.get('goal', 'growth')

    recs = []
    for ticker, stock in STOCKS.items():
        score = 0
        if risk == 'conservative':
            if stock['dividend'] >= 4: score += 3
            if stock['pe'] < 15: score += 2
            if stock['cap'] == 'large': score += 2
        elif risk == 'moderate':
            if stock['roe'] >= 15: score += 3
            if 10 <= stock['pe'] <= 25: score += 2
            if stock['cap'] == 'large': score += 1
        else:  # aggressive
            if stock['sector'] in ['Technology', 'Consumer Discretionary']: score += 3
            if stock['change'] > 1: score += 2
        if goal == 'income' and stock['dividend'] >= 3: score += 3
        if goal == 'growth' and stock['roe'] >= 15: score += 2

        health_score = min(10, round(
            (min(stock['roe'], 30) / 30 * 4) +
            (min(stock['dividend'], 8) / 8 * 3) +
            (max(0, min(1, (30 - stock['pe']) / 30)) * 3)
        , 1))
        score += random.uniform(0, 1)
        recs.append({"ticker": ticker, **stock, "score": score, "health_score": health_score})

    recs.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(recs[:5])

@app.route('/api/compare', methods=['POST'])
def compare():
    tickers = request.json.get('tickers', [])
    result = []
    for t in tickers[:5]:
        t = t.upper()
        if t in STOCKS:
            result.append({"ticker": t, **STOCKS[t]})
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)