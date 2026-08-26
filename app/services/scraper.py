import urllib.request, urllib.parse, json, re, xml.etree.ElementTree as ET
from typing import List, Dict, Any

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36', 'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'}

def parse_balanced_json(html: str, marker: str = 'ytInitialData') -> dict:
    start = html.find(marker)
    if start == -1: return {}
    b_start = html.find('{', start)
    if b_start == -1: return {}
    depth, in_s, esc, b_end = 0, False, False, -1
    for i in range(b_start, len(html)):
        c = html[i]
        if esc: esc = False; continue
        if c == chr(92): esc = True; continue
        if c == chr(34): in_s = not in_s; continue
        if not in_s:
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    b_end = i + 1
                    break
    if b_end != -1:
        try: return json.loads(html[b_start:b_end])
        except Exception: pass
    return {}

def extract_videos_from_json(data: Any, videos: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    if videos is None: videos = []
    if isinstance(data, dict):
        if 'videoRenderer' in data:
            vr = data['videoRenderer']
            vid = vr.get('videoId')
            if vid:
                title = ''
                if 'title' in vr:
                    runs = vr['title'].get('runs')
                    if runs and len(runs) > 0: title = runs[0].get('text', '')
                    else: title = vr['title'].get('simpleText', '')
                channel = 'Canal'
                if 'ownerText' in vr and 'runs' in vr['ownerText'] and vr['ownerText']['runs']:
                    channel = vr['ownerText']['runs'][0].get('text', '')
                elif 'shortBylineText' in vr and 'runs' in vr['shortBylineText'] and vr['shortBylineText']['runs']:
                    channel = vr['shortBylineText']['runs'][0].get('text', '')
                views = 'N/A'
                if 'viewCountText' in vr:
                    if 'simpleText' in vr['viewCountText']: views = vr['viewCountText']['simpleText']
                    elif 'runs' in vr['viewCountText'] and vr['viewCountText']['runs']: views = vr['viewCountText']['runs'][0].get('text', '')
                published = vr.get('publishedTimeText', {}).get('simpleText', 'Recente')
                thumbs = vr.get('thumbnail', {}).get('thumbnails', [])
                thumb = thumbs[-1].get('url', f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg') if thumbs else f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'
                duration = ''
                if 'lengthText' in vr: duration = vr['lengthText'].get('simpleText', '')
                if title and not any(v['id'] == vid for v in videos):
                    videos.append({'id': vid, 'title': title, 'channel': channel, 'views': views, 'published': published, 'duration': duration, 'url': f'https://www.youtube.com/watch?v={vid}', 'thumbnail': thumb})
        for v in data.values():
            if isinstance(v, (dict, list)): extract_videos_from_json(v, videos)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)): extract_videos_from_json(item, videos)
    return videos

def get_daily_google_trends(geo: str = 'BR') -> List[Dict[str, Any]]:
    trends = []
    try:
        url = f'https://trends.google.com/trending/rss?geo={geo}'
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=6) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else ''
                traffic = item.find('{https://trends.google.com/trending/rss}approx_traffic')
                traffic_str = traffic.text if traffic is not None else '+50K'
                link = item.find('link').text if item.find('link') is not None else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                news_items = []
                for news in item.findall('{https://trends.google.com/trending/rss}news_item'):
                    nt = news.find('{https://trends.google.com/trending/rss}news_item_title')
                    nu = news.find('{https://trends.google.com/trending/rss}news_item_url')
                    if nt is not None and nt.text:
                        news_items.append({'title': nt.text, 'url': nu.text if nu is not None else ''})
                if title:
                    trends.append({'title': title, 'traffic': traffic_str, 'link': link, 'pub_date': pub_date, 'news': news_items})
    except Exception as e:
        print(f'Error fetching Google Trends: {e}')
    return trends

def search_youtube_niche(query: str, filter_type: str = 'relevant') -> List[Dict[str, Any]]:
    encoded_query = urllib.parse.quote(query)
    sp = ''
    if filter_type == 'this_week': sp = '&sp=CAMSAkAB'
    elif filter_type == 'views': sp = '&sp=CAMSAkAE'
    url = f'https://www.youtube.com/results?search_query={encoded_query}{sp}'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        data = parse_balanced_json(html)
        return extract_videos_from_json(data)[:25]
    except Exception as e:
        print(f'Error searching YouTube: {e}')
        return []

def get_youtube_trending_feed(gl: str = 'BR') -> List[Dict[str, Any]]:
    try:
        url = f'https://www.youtube.com/feed/trending?gl={gl}&hl=pt'
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        data = parse_balanced_json(html)
        vids = extract_videos_from_json(data)
        if vids: return vids[:25]
    except Exception as e:
        pass
    return search_youtube_niche('em alta brasil hoje', 'relevant')[:20]

def get_youtube_autocomplete_keywords(seed: str) -> List[str]:
    try:
        encoded_seed = urllib.parse.quote(seed)
        url = f'https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={encoded_seed}'
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read().decode('latin1', errors='ignore')
            m = re.search(r'\((.*)\)', content)
            if m:
                data = json.loads(m.group(1))
                return [item[0] for item in data[1] if item and len(item) > 0]
    except Exception as e:
        pass
    return []