import json
import os
import re
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

DATA_FILE = os.path.join(BASE_DIR, 'missiles.json')

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    DATA = json.load(f)

SEARCH_FIELDS = ['参战国家', '武器类别', '简介', '核心性能', '制导方式', '本次战争使用情况及战果']


def score_item(item, keywords):
    score = 0
    text = ' '.join(str(item.get(f, '')) for f in SEARCH_FIELDS).lower()
    for kw in keywords:
        kw = kw.lower()
        if not kw:
            continue
        count = text.count(kw)
        if count > 0:
            score += count
            if kw in str(item.get('武器类别', '')).lower():
                score += 5
            if kw in str(item.get('参战国家', '')).lower():
                score += 3
    return score


def tokenize(query):
    tokens = re.split(r'[\s，,、；;]+', query.strip())
    chars = list(re.sub(r'\s+', '', query))
    result = set(tokens) | set(chars) if len(query) <= 4 else set(tokens)
    return [t for t in result if t]


@app.route('/')
def index():
    return send_from_directory(os.path.join(BASE_DIR, 'templates'), 'index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)


@app.route('/images/<path:filename>')
def image_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'images'), filename)


@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = (data or {}).get('query', '').strip()
    if not query:
        return jsonify([])

    keywords = tokenize(query)
    scored = []
    for item in DATA:
        s = score_item(item, keywords)
        if s > 0:
            scored.append((s, item))

    scored.sort(key=lambda x: -x[0])
    results = [item for _, item in scored[:10]]
    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
