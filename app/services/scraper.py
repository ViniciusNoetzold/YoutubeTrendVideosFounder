import urllib.request
import urllib.parse
import json
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
}

def parse_balanced_json(html: str, marker: str = 'ytInitialData') -> dict:
    start = html.find(marker)
    if start == -1:
        return {}
    b_start = html.find('{', start)
    if b_start == -1:
        return {}
    
    depth = 0
    in_s = False
    esc = False
    b_end = -1
    for i in range(b_start, len(html)):
        c = html[i]
        if esc:
            esc = False
            continue
        if c == '\\':
            esc = True
            continue
        if c == '"':
            in_s = not in_s
            continue
        if not in_s:
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    b_end = i + 1
                    break
    if b_end != -1:
        try:
            return json.loads(html[b_start:b_end])
        except Exception:
            pass
    return {}

def extract_videos_from_json(data: Any, videos: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    if videos is None:
        videos = []
    
    if isinstance(data, dict):
        # Standard videoRenderer
        if 'videoRenderer' in data:
            vr = data['videoRenderer']
            vid = vr.get('videoId')
            if vid:
                title = ''
                if 'title' in vr:
                    runs = vr['title'].get('runs')
                    if runs and len(runs) > 0:
                        title = runs[0].get('text', '')
                    else:
                        title = vr['title'].get('simpleText', '')
                
                channel = 'Canal'
                if 'ownerText' in vr and 'runs' in vr['ownerText'] and vr['ownerText']['runs']:
                    channel = vr['ownerText']['runs'][0].get('text', '')
                elif 'shortBylineText' in vr and 'runs' in vr['shortBylineText'] and vr['shortBylineText']['runs']:
                    channel = vr['shortBylineText']['runs'][0].get('text', '')
                
                views = 'N/A'
                if 'viewCountText' in vr:
                    if 'simpleText' in vr['viewCountText']:
                        views = vr['viewCountText']['simpleText']
                    elif 'runs' in vr['viewCountText'] and vr['viewCountText']['runs']:
                        views = vr['viewCountText']['runs'][0].get('text', '')
                
                published = vr.get('publishedTimeText', {}).get('simpleText', 'Recente')
                
                thumbs = vr.get('thumbnail', {}).get('thumbnails', [])
                thumb = thumbs[-1].get('url', f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg') if thumbs else f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'
                
                duration = ''
                if 'lengthText' in vr:
                    duration = vr['lengthText'].get('simpleText', '')
                
                badges = [str(b) for b in vr.get('badges', [])]
                is_live = any('LIVE' in b.upper() or 'AO VIVO' in b.upper() for b in badges) or ('assistindo' in str(views).lower() or 'watching' in str(views).lower())
                is_short = '#shorts' in title.lower() or (duration and duration.count(':') == 1 and int(duration.split(':')[0]) == 0 and int(duration.split(':')[1]) <= 60)
                
                if title and not any(v['id'] == vid for v in videos):
                    videos.append({
                        'id': vid,
                        'title': title,
                        'channel': channel,
                        'views': views,
                        'published': published,
                        'duration': duration or ('AO VIVO' if is_live else ''),
                        'is_live': is_live,
                        'is_short': is_short,
                        'content_type': 'live' if is_live else ('short' if is_short else 'video'),
                        'url': f'https://www.youtube.com/watch?v={vid}',
                        'thumbnail': thumb
                    })
        
        # Shorts reelItemRenderer
        elif 'reelItemRenderer' in data:
            rr = data['reelItemRenderer']
            vid = rr.get('videoId')
            headline = ''
            if 'headline' in rr:
                headline = rr['headline'].get('simpleText', '') or (rr['headline'].get('runs', [{}])[0].get('text', '') if 'runs' in rr['headline'] else '')
            views = rr.get('viewCountText', {}).get('simpleText', 'Shorts')
            thumbs = rr.get('thumbnail', {}).get('thumbnails', [])
            thumb = thumbs[-1].get('url', f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg') if thumbs else f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'
            
            if vid and headline and not any(v['id'] == vid for v in videos):
                videos.append({
                    'id': vid,
                    'title': headline,
                    'channel': 'YouTube Shorts',
                    'views': views or 'Shorts',
                    'published': 'Recente',
                    'duration': 'Short',
                    'is_live': False,
                    'is_short': True,
                    'content_type': 'short',
                    'url': f'https://www.youtube.com/shorts/{vid}',
                    'thumbnail': thumb
                })
        
        for v in data.values():
            if isinstance(v, (dict, list)):
                extract_videos_from_json(v, videos)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                extract_videos_from_json(item, videos)
                
    return videos

def get_daily_google_trends(geo: str = 'BR') -> List[Dict[str, Any]]:
    trends = []
    try:
        url = f'https://trends.google.com/trending/rss?geo={geo}'
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=6) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            items = root.findall('.//item')
            for item in items:
                title = item.find('title').text if item.find('title') is not None else ''
                traffic = item.find('{https://trends.google.com/trending/rss}approx_traffic')
                traffic_str = traffic.text if traffic is not None else '+50K'
                link = item.find('link').text if item.find('link') is not None else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                
                news_items = []
                for news in item.findall('{https://trends.google.com/trending/rss}news_item'):
                    nt = news.find('{https://trends.google.com/trending/rss}news_item_title')
                    nu = news.find('{https://trends.google.com/trending/rss}news_item_url')
                    ns = news.find('{https://trends.google.com/trending/rss}news_item_source')
                    if nt is not None and nt.text:
                        news_items.append({
                            'title': nt.text,
                            'url': nu.text if nu is not None else '',
                            'source': ns.text if ns is not None else 'Notícia'
                        })
                        
                if title:
                    headline = news_items[0]['title'] if news_items else ''
                    source = news_items[0]['source'] if news_items else 'Google Trends'
                    trends.append({
                        'title': title,
                        'traffic': traffic_str,
                        'headline': headline,
                        'source': source,
                        'link': link,
                        'pub_date': pub_date,
                        'news': news_items
                    })
    except Exception as e:
        print(f'Error fetching Google Trends: {e}')
    return trends

def get_youtube_trending_feed(gl: str = 'BR') -> List[Dict[str, Any]]:
    # Search for trending Brazilian high-volume videos
    try:
        url = f'https://www.youtube.com/results?search_query=em+alta+brasil+hoje&sp=CAI%253D'
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        data = parse_balanced_json(html)
        videos = extract_videos_from_json(data)
        if videos:
            return videos[:25]
    except Exception as e:
        print(f'Trending feed exception: {e}')
    return []

def search_youtube_niche(query: str, date_filter: str = 'relevant', content_type: str = 'all') -> List[Dict[str, Any]]:
    search_q = query.strip()
    sp = ''
    
    # Content Type Filtering
    if content_type == 'lives':
        sp = '&sp=EgJAAQ%3D%3D'  # Live features
    elif content_type == 'shorts':
        if not '#shorts' in search_q.lower() and not 'shorts' in search_q.lower():
            search_q = f'{search_q} #shorts'
        sp = '&sp=EgIYAg%3D%3D'  # Short duration (< 4 min)
    elif content_type == 'videos':
        sp = '&sp=EgIQAQ%3D%3D'  # Video type
    
    # Date Filtering (combines or applies date filter if no restrictive type filter)
    if content_type == 'all' or content_type == 'videos':
        if date_filter == 'today':
            sp = '&sp=EgQIAhAB'      # Last 24 hours (Hoje)
        elif date_filter == 'this_week':
            sp = '&sp=EgQIAxAB'      # This week (Esta semana)
        elif date_filter == 'this_month':
            sp = '&sp=EgQIBBAB'      # This month (Este mês)
        elif date_filter == 'views':
            sp = '&sp=CAMSAhAB'      # Most viewed (Mais visualizados)
        elif date_filter == 'week_popular':
            sp = '&sp=CAMSAkAB'      # Most viewed this week
    
    encoded_query = urllib.parse.quote(search_q)
    url = f'https://www.youtube.com/results?search_query={encoded_query}{sp}'
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        data = parse_balanced_json(html)
        videos = extract_videos_from_json(data)
        
        # Post-filter by content_type if needed
        if content_type == 'lives':
            # ensure live flag or order lives first
            lives = [v for v in videos if v.get('is_live')]
            return lives if lives else videos[:25]
        elif content_type == 'shorts':
            shorts = [v for v in videos if v.get('is_short')]
            return shorts if shorts else videos[:25]
        elif content_type == 'videos':
            long_vids = [v for v in videos if not v.get('is_short') and not v.get('is_live')]
            return long_vids if long_vids else videos[:25]
            
        return videos[:25]
    except Exception as e:
        print(f'Error searching YouTube for niche: {e}')
        return []

def get_youtube_autocomplete_keywords(seed: str) -> List[str]:
    try:
        encoded_seed = urllib.parse.quote(seed.strip())
        url = f'https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={encoded_seed}'
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as resp:
            # FIX: Use UTF-8 decoding to prevent character mojibake
            content = resp.read().decode('utf-8', errors='ignore')
            m = re.search(r'\((.*)\)', content)
            if m:
                data = json.loads(m.group(1))
                return [item[0] for item in data[1] if item and len(item) > 0]
    except Exception as e:
        print(f'Error getting autocomplete: {e}')
    return []