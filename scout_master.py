#!/usr/bin/env python3
"""
SCOUT MASTER - Comprehensive Data Intelligence Engine
====================================================

Unified scout system combining:
- Local business discovery (Yelp, OSM, Nominatim)
- Economic/market data (BLS, FRED, World Bank)
- Developer forums (Stack Overflow, GitHub, Dev.to, Reddit)
- Trade forums (PlumbersRule, ElectricianTalk, etc.)
- Business forums (Indie Hackers, Product Hunt, HN)
- Market research (Google Trends, Census, SEC)
- Real-time sentiment (Twitter, Reddit, HN)
- Competitive intel (SimilarWeb, BuiltWith)

Usage:
  python scout_master.py --query "gamified code debugger" --vertical saas
  python scout_master.py --domain programming --limit 20
  python scout_master.py --forum dev --keywords "onboarding visualization"
"""

import sys
import os
import json
import time
import random
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# Add existing Vertical AI core to path
VERTICAL_CORE = Path("/data/data/com.termux/files/home/Gospel-A9-Whorl-Staging/Kindred_Core")
sys.path.insert(0, str(VERTICAL_CORE))

# ============================================================================
# CONFIGURATION
# ============================================================================

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; BleakNarratives/Research/1.0)'}
TIMEOUT = 20

# API Keys (from environment - free tier OK)
YELP_API_KEY = os.getenv('YELP_API_KEY', '')
TWITTER_BEARER = os.getenv('TWITTER_BEARER', '')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

def fetch(url, json_response=True, timeout=TIMEOUT):
    """Universal fetch with retry."""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode('utf-8', errors='replace')
            if json_response:
                return json.loads(raw), None
            return raw, None
        except Exception as e:
            time.sleep(2 ** attempt)
            if attempt == 2:
                return None, str(e)


# ============================================================================
# SOURCE: DEVELOPER FORUMS
# ============================================================================

def search_stack_overflow(query, site="stackoverflow", limit=10):
    """
    Stack Overflow API - free, no key required (rate limited)
    Returns: [{'title', 'link', 'score', 'tags', 'views', 'answers'}]
    """
    url = f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={urllib.parse.quote(query)}&site={site}&filter=withbody&pagesize={limit}"
    data, err = fetch(url)
    if err or not data or 'items' not in data:
        return [], f"StackOverflow: {err}"
    
    results = []
    for item in data['items']:
        results.append({
            'source': 'stackoverflow',
            'title': item.get('title', ''),
            'link': item.get('link', ''),
            'score': item.get('score', 0),
            'views': item.get('view_count', 0),
            'answers': item.get('answer_count', 0),
            'tags': item.get('tags', []),
            'body': item.get('body', '')[:500] if 'body' in item else '',
            'timestamp': datetime.fromtimestamp(item.get('creation_date', 0)).isoformat()
        })
    
    return results, None


def search_github(query, sort="best-match", limit=10):
    """
    GitHub API - free tier: 60 requests/hour unauthenticated
    Returns: repos, issues, discussions matching query
    """
    headers = dict(HEADERS)
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort={sort}&per_page={limit}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.loads(r.read().decode('utf-8'))
        if 'items' in data:
            results = []
            for item in data['items']:
                results.append({
                    'source': 'github',
                    'repo': item.get('full_name', ''),
                    'name': item.get('name', ''),
                    'description': item.get('description', ''),
                    'stars': item.get('stargazers_count', 0),
                    'forks': item.get('forks_count', 0),
                    'issues': item.get('open_issues_count', 0),
                    'language': item.get('language', ''),
                    'url': item.get('html_url', ''),
                    'updated': item.get('updated_at', '')
                })
            return results, None
    except Exception as e:
        return [], f"GitHub: {e}"
    return [], "GitHub: no results"


def search_dev_to(query, limit=10):
    """
    Dev.to API - free, no key
    Returns: articles, discussions
    """
    url = f"https://dev.to/api/articles?page=1&q={urllib.parse.quote(query)}&per_page={limit}"
    data, err = fetch(url)
    if err or not data:
        return [], f"Dev.to: {err}"
    
    results = []
    for item in data:
        results.append({
            'source': 'dev.to',
            'title': item.get('title', ''),
            'url': item.get('url', ''),
            'description': item.get('description', ''),
            'tags': item.get('tag_list', []),
            'reactions': item.get('public_reactions_count', 0),
            'comments': item.get('comments_count', 0),
            'published': item.get('published_at', '')
        })
    
    return results, None


def search_reddit(query, subreddit=None, limit=10):
    """
    Reddit API - free, no key (rate limited)
    Returns: posts from Reddit
    """
    if subreddit:
        url = f"https://www.reddit.com/r/{subreddit}/search.json?q={urllib.parse.quote(query)}&limit={limit}&raw_json=1"
    else:
        url = f"https://www.reddit.com/search.json?q={urllib.parse.quote(query)}&limit={limit}&raw_json=1"
    
    try:
        req = urllib.request.Request(url, headers={**HEADERS, 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read().decode('utf-8')
            # Reddit returns JSON wrapped in HTML comments sometimes
            if raw.startswith('<!--'):
                import re
                match = re.search(r'<!--\s*({.*?})\s*-->', raw, re.DOTALL)
                if match:
                    raw = match.group(1)
            data = json.loads(raw)
    except Exception as e:
        return [], f"Reddit: {e}"
    
    if 'data' not in data or 'children' not in data['data']:
        return [], "Reddit: no results"
    
    results = []
    for child in data['data']['children']:
        post = child.get('data', {})
        results.append({
            'source': 'reddit',
            'subreddit': f"r/{post.get('subreddit', '')}",
            'title': post.get('title', ''),
            'url': f"https://reddit.com{post.get('permalink', '')}",
            'score': post.get('score', 0),
            'comments': post.get('num_comments', 0),
            'body': post.get('selftext', '')[:500],
            'author': post.get('author', 'unknown'),
            'created': datetime.fromtimestamp(post.get('created_utc', 0)).isoformat()
        })
    
    return results, None


# ============================================================================
# SOURCE: TRADE FORUMS (Enhanced with actual scraping)
# ============================================================================

# Trade forum URLs - many are PHP-based, harder to scrape cleanly
TRADE_FORUMS = {
    'plumbing': [
        {'name': 'PlumbersRule', 'url': 'https://www.plumbersrule.com/', 'search': '/search.php?search={query}'},
        {'name': 'PlumbingZone', 'url': 'https://www.plumbingzone.com/', 'search': '/forums/search.php?search={query}'},
        {'name': 'TerryLove', 'url': 'https://terrylove.com/', 'search': '/forums/search.php?keywords={query}'},
        {'name': 'PlumbingForums', 'url': 'https://www.plumbingforums.com/', 'search': '/search.php?search={query}'},
    ],
    'hvac': [
        {'name': 'HVAC-Talk', 'url': 'https://hvac-talk.com/', 'search': '/vbb/search.php?do=process&query={query}'},
        {'name': 'HVAC School', 'url': 'https://hvacrschool.com/', 'search': '?s={query}'},
        {'name': 'HVAC Forums', 'url': 'https://www.hvacforums.net/', 'search': '/search.php?search={query}'},
    ],
    'electrical': [
        {'name': 'ElectricianTalk', 'url': 'https://www.electriciantalk.com/', 'search': '/f2/search.php?search={query}'},
        {'name': 'ECN Mag', 'url': 'https://www.ecnmag.com/', 'search': '?s={query}'},
        {'name': 'Electrician Forum', 'url': 'https://www.electricianforum.com/', 'search': '/search.php?search={query}'},
        {'name': 'Sparkys Corner', 'url': 'https://www.sparkyscorner.com/', 'search': '/search.php?search={query}'},
    ],
    'construction': [
        {'name': 'ContractorTalk', 'url': 'https://www.contractortalk.com/', 'search': '/forums/search.php?search={query}'},
        {'name': 'ConstructionJunkie', 'url': 'https://www.constructionjunkie.com/', 'search': '?s={query}'},
        {'name': 'Fine Homebuilding', 'url': 'https://www.finehomebuilding.com/forum/', 'search': '?s={query}'},
    ],
    'general_trades': [
        {'name': 'City-Data Trades', 'url': 'https://www.city-data.com/forum/', 'search': '/search.php?search={query}'},
        {'name': 'DIYChatroom', 'url': 'https://www.diychatroom.com/', 'search': '/search.php?search={query}'},
    ],
    'automotive': [
        {'name': 'GarageJournal', 'url': 'https://www.garagejournal.com/', 'search': '/search.php?search={query}'},
        {'name': 'NASIOC', 'url': 'https://forums.nasioc.com/', 'search': '/search.php?search={query}'},
    ]
}


def search_trade_forums(query, trade_type='plumbing', limit=10):
    """
    Search trade-specific forums.
    Note: Many trade forums use vBulletin and have anti-scraping.
    This provides direct links and attempts to scrape when possible.
    """
    if trade_type not in TRADE_FORUMS:
        return [], f"Unknown trade type: {trade_type}"
    
    forums = TRADE_FORUMS[trade_type]
    results = []
    
    for forum in forums:
        search_url = forum['url'].rstrip('/') + forum['search'].replace('{query}', urllib.parse.quote(query))
        
        # Try to scrape if possible
        try:
            req = urllib.request.Request(search_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                html = r.read().decode('utf-8', errors='replace')
            
            # Look for forum posts in HTML
            import re
            # Try to find post titles and links
            title_pattern = re.compile(r'<a[^>]*class=["\'].*title["\'].*>[^<]*([^<]+)[^>]*</a>', re.IGNORECASE)
            link_pattern = re.compile(r'<a[^>]*href=["\']([^"\']+)["\']', re.IGNORECASE)
            
            titles = title_pattern.findall(html)
            links = link_pattern.findall(html)
            
            if titles:
                for i, title in enumerate(titles[:3]):
                    results.append({
                        'source': 'trade_forum',
                        'forum_name': forum['name'],
                        'forum_url': forum['url'],
                        'search_url': search_url,
                        'query': query,
                        'trade': trade_type,
                        'title': title.strip()[:100],
                        'link': links[i] if i < len(links) else search_url
                    })
            else:
                # Just provide the search URL
                results.append({
                    'source': 'trade_forum',
                    'forum_name': forum['name'],
                    'forum_url': forum['url'],
                    'search_url': search_url,
                    'query': query,
                    'trade': trade_type
                })
        except Exception as e:
            # If scraping fails, just provide the search URL
            results.append({
                'source': 'trade_forum',
                'forum_name': forum['name'],
                'forum_url': forum['url'],
                'search_url': search_url,
                'query': query,
                'trade': trade_type,
                'error': str(e)[:100]
            })
    
    return results[:limit], None


# ============================================================================
# SOURCE: BUSINESS/STARTUP FORUMS
# ============================================================================

def search_indie_hackers(query, limit=10):
    """
    Indie Hackers - no official API, but we can search
    """
    # Use Google to find IH posts (IH doesn't have public search API)
    url = f"https://www.google.com/search?q=site:indiehackers.com {urllib.parse.quote(query)}&num={limit}"
    # This will return HTML, not JSON - need browser automation ideally
    # For now, return the search URL
    return [{'source': 'indie_hackers', 'search_url': url, 'query': query}], None


def search_product_hunt(query, limit=10):
    """
    Product Hunt API - needs key but has free tier
    """
    api_key = os.getenv('PRODUCT_HUNT_API_KEY', '')
    if not api_key:
        # Return search URL
        url = f"https://www.producthunt.com/search/{urllib.parse.quote(query)}"
        return [{'source': 'product_hunt', 'search_url': url, 'query': query}], None
    
    url = f"https://api.producthunt.com/v2/posts?search={urllib.parse.quote(query)}&per_page={limit}"
    headers = {**HEADERS, 'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.loads(r.read().decode('utf-8'))
        
        results = []
        for item in data.get('posts', []):
            results.append({
                'source': 'product_hunt',
                'name': item.get('name', ''),
                'tagline': item.get('tagline', ''),
                'url': item.get('url', ''),
                'votes': item.get('votes_count', 0),
                'comments': item.get('comments_count', 0),
                'makers': [m.get('name', '') for m in item.get('makers', [])],
                'published': datetime.fromtimestamp(item.get('created_at', 0)).isoformat()
            })
        
        return results, None
    except Exception as e:
        return [], f"ProductHunt: {e}"


def search_hacker_news(query, limit=10):
    """
    Hacker News via Algolia API - free, no key
    """
    url = f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(query)}&tags=story&hitsPerPage={limit}"
    data, err = fetch(url)
    if err or not data or 'hits' not in data:
        return [], f"HackerNews: {err}"
    
    results = []
    for hit in data['hits']:
        results.append({
            'source': 'hacker_news',
            'title': hit.get('title', ''),
            'url': hit.get('url', hit.get('story_url', '')),
            'points': hit.get('points', 0),
            'comments': hit.get('num_comments', 0),
            'author': hit.get('author', ''),
            'created': datetime.fromtimestamp(hit.get('created_at_i', 0)).isoformat()
        })
    
    return results, None


def search_google_trends(query, country='US'):
    """
    Google Trends - no official API, use trend data
    Returns: Interest over time data
    """
    # Use unofficial method
    try:
        import requests
        url = f"https://trends.google.com/trends/api/explore?hl=en-US&tz=-360&req={json.dumps({'comparisonItem': [{'keyword': query, 'geo': country, 'time': 'today 12-m'}], 'category': 0, 'property': ''})}"
        # This returns JSONP
        return [], "Google Trends: requires browser automation"
    except:
        return [], "Google Trends: unavailable"


# ============================================================================
# SOURCE: MARKET RESEARCH
# ============================================================================

def fetch_census_data(query, dataset='acs', year=2022):
    """
    US Census Bureau API - free, requires key
    """
    api_key = os.getenv('CENSUS_API_KEY', '')
    if not api_key:
        return [], "Census: API key required (free at census.gov)"
    
    url = f"https://api.census.gov/data/{year}/{dataset}?get=NAME,{query}&for=state:*&key={api_key}"
    data, err = fetch(url)
    if err or not data:
        return [], f"Census: {err}"
    
    return data[1:11], None  # Top 10 states


def fetch_sec_filings(ticker, limit=5):
    """
    SEC Edgar API - free, no key
    Returns: Recent filings for a ticker
    """
    url = f"https://data.sec.gov/submissions/CIK{get_cik(ticker)}.json"
    data, err = fetch(url)
    if err or not data or 'filings' not in data:
        return [], f"SEC: {err}"
    
    filings = data['filings'].get('recent', {})
    results = []
    for form_type, items in list(filings.items())[:limit]:
        for item in items[:1]:
            results.append({
                'source': 'sec_edgar',
                'ticker': ticker,
                'form': form_type,
                'date': item.get('filingDate', ''),
                'url': f"https://www.sec.gov/Archives/edgar/data/{ticker.replace('$','')}/{item['accessionNumber'].replace('-','')}/{item['primaryDocument']}"
            })
    
    return results, None


def get_cik(ticker):
    """Get CIK for a ticker - simplified mapping."""
    # This would normally come from a database
    # For demo, return placeholder
    return "0001652044"  # Apple's CIK


# ============================================================================
# SOURCE: COMPETITIVE INTEL
# ============================================================================

def check_similarweb(domain):
    """
    SimilarWeb - free tier available
    Returns: Traffic estimates, ranking, category
    """
    api_key = os.getenv('SIMILARWEB_API_KEY', '')
    if not api_key:
        url = f"https://www.similarweb.com/website/{domain}/#overview"
        return [{'source': 'similarweb', 'url': url, 'domain': domain}], None
    
    url = f"https://api.similarweb.com/v1/website/{domain}/traffic-and-engagement/estimations?api_key={api_key}"
    data, err = fetch(url)
    if err or not data:
        return [], f"SimilarWeb: {err}"
    
    return [{'source': 'similarweb', 'data': data, 'domain': domain}], None


def check_builtinwith(url):
    """
    BuiltWith API - free tier available
    Returns: Technology stack used by a website
    """
    api_key = os.getenv('BUILTWITH_API_KEY', '')
    if not api_key:
        url = f"https://builtwith.com/{urllib.parse.urlparse(url).netloc}"
        return [{'source': 'builtinwith', 'url': url}], None
    
    url = f"https://api.builtwith.com/v19/api.json?APIKEY={api_key}&LOOKUP={urllib.parse.quote(url)}"
    data, err = fetch(url)
    if err or not data:
        return [], f"BuiltWith: {err}"
    
    return [{'source': 'builtinwith', 'data': data, 'url': url}], None


# ============================================================================
# SOURCE: REAL-TIME & SENTIMENT
# ============================================================================

def search_twitter(query, limit=10):
    """
    Twitter API v2 - requires bearer token
    """
    if not TWITTER_BEARER:
        url = f"https://twitter.com/search?q={urllib.parse.quote(query)}&src=typed_query"
        return [{'source': 'twitter', 'search_url': url, 'query': query}], None
    
    url = f"https://api.twitter.com/2/tweets/search/recent?query={urllib.parse.quote(query)}&max_results={limit}&tweet.fields=created_at,public_metrics"
    headers = {**HEADERS, 'Authorization': f'Bearer {TWITTER_BEARER}'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.loads(r.read().decode('utf-8'))
        
        results = []
        for tweet in data.get('data', []):
            results.append({
                'source': 'twitter',
                'id': tweet.get('id', ''),
                'text': tweet.get('text', ''),
                'author': tweet.get('author_id', ''),
                'created': tweet.get('created_at', ''),
                'retweets': tweet.get('public_metrics', {}).get('retweet_count', 0),
                'likes': tweet.get('public_metrics', {}).get('like_count', 0)
            })
        
        return results, None
    except Exception as e:
        return [], f"Twitter: {e}"


# ============================================================================
# SOURCE: GOVERNMENT & ECONOMIC (from firefly_lite.py)
# ============================================================================

def fetch_bls(series_id):
    """BLS - employment/wages by industry."""
    url = f"https://api.bls.gov/publicAPI/v1/timeseries/data/{series_id}"
    data, err = fetch(url)
    if err or not data:
        return [], f"BLS: {err}"
    try:
        points = data['Results']['series'][0]['data'][:6]
        results = []
        for p in points:
            results.append({
                'source': 'bls',
                'series': series_id,
                'period': p['periodName'],
                'year': p['year'],
                'value': p['value']
            })
        return results, None
    except:
        return [], "BLS: parse error"


def fetch_fred(series_id, label):
    """FRED - economic time series."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    raw, err = fetch(url, json_response=False)
    if err or not raw:
        return [], f"FRED: {err}"
    try:
        lines = raw.strip().split('\n')
        results = []
        for line in lines[-6:]:
            parts = line.split(',')
            if len(parts) >= 2:
                results.append({
                    'source': 'fred',
                    'series': series_id,
                    'label': label,
                    'date': parts[0],
                    'value': parts[1]
                })
        return results, None
    except:
        return [], "FRED: parse error"


def fetch_worldbank(indicator, country='US'):
    """World Bank - macro indicators."""
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&mrv=4"
    data, err = fetch(url)
    if err or not data:
        return [], f"WorldBank: {err}"
    try:
        points = data[1][:4]
        results = []
        for p in points:
            if p['value']:
                results.append({
                    'source': 'worldbank',
                    'indicator': indicator,
                    'country': country,
                    'date': p['date'],
                    'value': p['value']
                })
        return results, None
    except:
        return [], "WorldBank: parse error"


# ============================================================================
# VERTICAL CONTEXTS (from firefly_lite.py + expanded)
# ============================================================================

VERTICAL_CONFIGS = {
    'saas': {
        'name': 'SaaS/Software',
        'description': 'Software-as-a-Service and software products',
        'bls_series': 'CEU5051000001',
        'fred_series': ('PCEC96', 'Personal Consumption'),
        'wb_indicator': 'NY.GDP.MKTP.CD',
        'search_terms': ['SaaS', 'software', 'startup', 'bootstrapped', 'revenue', 'churn'],
        'forums': ['r/Entrepreneur', 'r/saaS', 'r/startups', 'Indie Hackers'],
        'intel': """
SAAS INTEL:
- Avg SaaS churn: 5-7% monthly for SMB
- CAC payback target: under 12 months
- NRR > 100% = growth without new customers
- Pricing anchors: $29/$99/$299 tiers standard
- Free trial converts at 2-5%, freemium at 1-3%
- LTV:CAC ratio ideal: 3:1 or higher
- Solo founder SaaS: 70% fail within 2 years
- Successful solo SaaS: $1-10M ARR typical ceiling
- Micro-SaaS (<$5K MRR): 80% are solo or small team
        """
    },
    'programming': {
        'name': 'Programming/Development',
        'description': 'Software development tools and services',
        'bls_series': 'CEU5051000001',
        'fred_series': ('IPFINAL', 'Intellectual Property'),
        'wb_indicator': 'NY.GDP.MKTP.CD',
        'search_terms': ['programming', 'developer', 'coding', 'tool', 'IDE', 'debugger'],
        'forums': ['Stack Overflow', 'r/programming', 'r/learnprogramming', 'Dev.to'],
        'intel': """
PROGRAMMING INTEL:
- 28M software developers worldwide (2024)
- 4.7M professional developers in US
- Avg developer salary: $110K US, $45K global
- Open source: 90% of codebases use OSS
- GitHub: 100M+ repositories, 40M+ users
- Most popular languages: JavaScript, Python, Java, C#, PHP
- Developer pain points: debugging (30%), technical debt (25%), onboarding (20%)
- Tools market: $50B+ annually
- Solo developer market growing 15% YoY
- Remote work: 60% of developers now hybrid/remote
        """
    },
    'plumbing': {
        'name': 'Plumbing',
        'description': 'Plumbing contractors and services',
        'bls_series': 'CEU2000000001',
        'fred_series': ('HOUST', 'Housing Starts'),
        'wb_indicator': 'NY.GDP.MKTP.CD',
        'search_terms': ['plumber', 'plumbing', 'drain', 'pipe', 'leak', 'sewer'],
        'forums': ['PlumbersRule', 'PlumbingZone', 'TerryLove', 'r/Plumbing'],
        'intel': """
PLUMBING INTEL:
- Avg service call: $175-450
- Emergency premium: 1.5-2x standard rate
- Lead gen platforms: Angi, Thumbtack, HomeAdvisor 15-25% fees
- License required all 50 states
- Biggest pain: no-shows, price shoppers, slow seasons
- Industry size: $120B US market
- Avg plumber revenue: $250K-500K/year (small business)
- Profit margins: 10-20%
- Labor shortage: 100K+ unfilled positions
- Home service market growing 4.5% annually
        """
    },
    'hvac': {
        'name': 'HVAC',
        'description': 'Heating, Ventilation, Air Conditioning',
        'bls_series': 'CEU7072200001',
        'fred_series': ('HOUST', 'Housing Starts'),
        'wb_indicator': 'NY.GDP.MKTP.CD',
        'search_terms': ['HVAC', 'heating', 'cooling', 'air conditioning', 'furnace', 'AC'],
        'forums': ['HVAC-Talk', 'HVAC School', 'r/HVAC'],
        'intel': """
HVAC INTEL:
- Avg repair cost: $150-500
- New system install: $3,500-7,500
- Emergency calls: $200-400
- Maintenance contracts: $150-300/year
- License required all states
- Equipment markups: 50-100%
- Labor rates: $75-150/hour
- Industry size: $150B US market
- Growth: 5% annually (aging equipment + climate change)
- Seasonality: Summer (AC) and Winter (heating) peaks
        """
    },
    'electrical': {
        'name': 'Electrical',
        'description': 'Electrical contractors and services',
        'bls_series': 'CEU2000000001',
        'fred_series': ('HOUST', 'Housing Starts'),
        'wb_indicator': 'NY.GDP.MKTP.CD',
        'search_terms': ['electrician', 'electrical', 'wiring', 'circuit', 'outlet', 'panel'],
        'forums': ['ElectricianTalk', 'ECN Mag', 'r/Electricians'],
        'intel': """
ELECTRICAL INTEL:
- Avg service call: $150-300
- Panel upgrade: $1,500-3,000
- New construction: $3-5/sq ft
- Emergency rate: 1.5-2x standard
- License required all states
- Insurance: $1M+ liability typical
- Equipment: $5K-20K per van
- Industry size: $140B US market
- Growth: 4.2% annually (new construction + retrofits)
- NEC code updates every 3 years
        """
    },
    'contractor': {
        'name': 'General Contracting',
        'description': 'Construction and remodeling contractors',
        'bls_series': 'CEU2000000001',
        'fred_series': ('HOUST', 'Housing Starts'),
        'wb_indicator': 'NY.GDP.MKTP.CD',
        'search_terms': ['contractor', 'construction', 'remodel', 'renovation', 'build'],
        'forums': ['ContractorTalk', 'ConstructionJunkie', 'r/Construction'],
        'intel': """
CONTRACTOR INTEL:
- Avg project: $10K-50K (residential)
- Markup: 15-30% typical
- Labor: 30-40% of project cost
- Materials: 40-50% of project cost
- Profit margins: 10-20%
- License required all states
- Insurance: $1-3M liability
- Lead time: 2-6 weeks for residential
- Industry size: $800B US market
- Growth: 3.8% annually
- Biggest challenges: labor shortage, material costs, permits
        """
    }
}


# ============================================================================
# SOURCE: SPECIALIZED DATA SOURCES
# ============================================================================

# Better sources for different needs
BETTER_SOURCES = {
    'market_size': [
        {'name': 'IBISWorld', 'url': 'https://www.ibisworld.com/', 'free': False, 'quality': 'gold'},
        {'name': 'Statista', 'url': 'https://www.statista.com/', 'free': False, 'quality': 'gold'},
        {'name': 'Grand View Research', 'url': 'https://www.grandviewresearch.com/', 'free': False, 'quality': 'gold'},
        {'name': 'US Census Economic Census', 'url': 'https://www.census.gov/programs-surveys/economic-census.html', 'free': True, 'quality': 'gold'},
    ],
    'trends': [
        {'name': 'Google Trends', 'url': 'https://trends.google.com/', 'free': True, 'quality': 'gold'},
        {'name': 'Exploding Topics', 'url': 'https://explodingtopics.com/', 'free': True, 'quality': 'silver'},
        {'name': 'TrendHunter', 'url': 'https://www.trendhunter.com/', 'free': True, 'quality': 'silver'},
        {'name': 'Gartner Hype Cycle', 'url': 'https://www.gartner.com/en/research/methodologies/gartner-hype-cycle', 'free': False, 'quality': 'gold'},
    ],
    'competitive_analysis': [
        {'name': 'SimilarWeb', 'url': 'https://www.similarweb.com/', 'free': True, 'quality': 'gold'},
        {'name': 'SEMrush', 'url': 'https://www.semrush.com/', 'free': False, 'quality': 'gold'},
        {'name': 'Ahrefs', 'url': 'https://ahrefs.com/', 'free': False, 'quality': 'gold'},
        {'name': 'BuiltWith', 'url': 'https://builtwith.com/', 'free': True, 'quality': 'silver'},
        {'name': 'Wappalyzer', 'url': 'https://www.wappalyzer.com/', 'free': True, 'quality': 'silver'},
    ],
    'funding': [
        {'name': 'Crunchbase', 'url': 'https://www.crunchbase.com/', 'free': True, 'quality': 'gold'},
        {'name': 'AngelList', 'url': 'https://angel.co/', 'free': True, 'quality': 'silver'},
        {'name': 'PitchBook', 'url': 'https://pitchbook.com/', 'free': False, 'quality': 'gold'},
        {'name': 'CB Insights', 'url': 'https://www.cbinsights.com/', 'free': False, 'quality': 'gold'},
    ],
    'startups': [
        {'name': 'Indie Hackers', 'url': 'https://www.indiehackers.com/', 'free': True, 'quality': 'gold'},
        {'name': 'Product Hunt', 'url': 'https://www.producthunt.com/', 'free': True, 'quality': 'gold'},
        {'name': 'BetaList', 'url': 'https://betalist.com/', 'free': True, 'quality': 'silver'},
        {'name': 'Y Combinator Requests', 'url': 'https://news.ycombinator.com/ask', 'free': True, 'quality': 'gold'},
    ],
    'developer': [
        {'name': 'Stack Overflow', 'url': 'https://stackoverflow.com/', 'free': True, 'quality': 'gold'},
        {'name': 'GitHub', 'url': 'https://github.com/', 'free': True, 'quality': 'gold'},
        {'name': 'Dev.to', 'url': 'https://dev.to/', 'free': True, 'quality': 'silver'},
        {'name': 'Hashnode', 'url': 'https://hashnode.com/', 'free': True, 'quality': 'silver'},
        {'name': 'Reddit r/programming', 'url': 'https://www.reddit.com/r/programming/', 'free': True, 'quality': 'gold'},
    ],
    'trades': [
        {'name': 'PlumbersRule', 'url': 'https://www.plumbersrule.com/', 'free': True, 'quality': 'gold'},
        {'name': 'ElectricianTalk', 'url': 'https://www.electriciantalk.com/', 'free': True, 'quality': 'gold'},
        {'name': 'HVAC-Talk', 'url': 'https://hvac-talk.com/', 'free': True, 'quality': 'gold'},
        {'name': 'ContractorTalk', 'url': 'https://www.contractortalk.com/', 'free': True, 'quality': 'gold'},
        {'name': 'City-Data Trades', 'url': 'https://www.city-data.com/forum/', 'free': True, 'quality': 'silver'},
    ],
    'government': [
        {'name': 'BLS', 'url': 'https://www.bls.gov/', 'free': True, 'quality': 'gold'},
        {'name': 'FRED', 'url': 'https://fred.stlouisfed.org/', 'free': True, 'quality': 'gold'},
        {'name': 'Census Bureau', 'url': 'https://www.census.gov/', 'free': True, 'quality': 'gold'},
        {'name': 'World Bank', 'url': 'https://data.worldbank.org/', 'free': True, 'quality': 'gold'},
        {'name': 'SEC Edgar', 'url': 'https://www.sec.gov/edgar/searchedgar/companysearch.html', 'free': True, 'quality': 'gold'},
    ]
}


def recommend_sources(domain):
    """Recommend best free sources for a given domain."""
    domain = domain.lower()
    
    if domain in ['saas', 'software', 'startup', 'tech']:
        return BETTER_SOURCES['startups'] + BETTER_SOURCES['developer'] + BETTER_SOURCES['trends']
    elif domain in ['plumbing', 'hvac', 'electrical', 'contractor']:
        return BETTER_SOURCES['trades'] + BETTER_SOURCES['market_size'] + BETTER_SOURCES['government']
    elif domain in ['market', 'research', 'data']:
        return BETTER_SOURCES['market_size'] + BETTER_SOURCES['trends'] + BETTER_SOURCES['competitive_analysis']
    elif domain in ['funding', 'investment', 'vc']:
        return BETTER_SOURCES['funding'] + BETTER_SOURCES['startups']
    else:
        # General purpose
        return (
            BETTER_SOURCES['developer'] +
            BETTER_SOURCES['startups'] +
            BETTER_SOURCES['trades'] +
            BETTER_SOURCES['government']
        )


# ============================================================================
# MAIN SCOUT FUNCTIONS
# ============================================================================

def scout_all(query, vertical=None, limit=15):
    """
    Scout across ALL available sources.
    Returns comprehensive data package.
    """
    print(f"\n{'='*60}")
    print(f"  SCOUT MASTER: {query}")
    print(f"  Vertical: {vertical or 'general'}")
    print(f"{'='*60}\n")
    
    all_results = {}
    start_time = time.time()
    
    # 1. Developer Forums
    print("  [1/7] Developer Forums...")
    so, so_err = search_stack_overflow(query, limit=5)
    all_results['stackoverflow'] = so
    print(f"    Stack Overflow: {len(so)} results")
    
    gh, gh_err = search_github(query, limit=5)
    all_results['github'] = gh
    print(f"    GitHub: {len(gh)} results")
    
    dt, dt_err = search_dev_to(query, limit=5)
    all_results['dev_to'] = dt
    print(f"    Dev.to: {len(dt)} results")
    
    # 2. Reddit (multiple subs)
    print("  [2/7] Reddit...")
    subs = ['programming', 'learnprogramming', 'startups', 'Entrepreneur', 'saas', 'smallbusiness']
    all_results['reddit'] = {}
    for sub in subs[:3]:  # Limit to 3 to avoid rate limiting
        r, r_err = search_reddit(query, subreddit=sub, limit=3)
        all_results['reddit'][sub] = r
        print(f"    r/{sub}: {len(r)} results")
    
    # 3. Business/Startup Forums
    print("  [3/7] Business Forums...")
    ih, ih_err = search_indie_hackers(query, limit=3)
    all_results['indie_hackers'] = ih
    
    ph, ph_err = search_product_hunt(query, limit=3)
    all_results['product_hunt'] = ph
    
    hn, hn_err = search_hacker_news(query, limit=5)
    all_results['hacker_news'] = hn
    print(f"    Indie Hackers: {len(ih)} links")
    print(f"    Product Hunt: {len(ph)} results")
    print(f"    Hacker News: {len(hn)} results")
    
    # 4. Economic Data (if vertical specified)
    if vertical and vertical in VERTICAL_CONFIGS:
        print("  [4/7] Economic Data...")
        config = VERTICAL_CONFIGS[vertical]
        
        bls, bls_err = fetch_bls(config['bls_series'])
        all_results['bls'] = bls
        print(f"    BLS: {len(bls)} data points")
        
        fred, fred_err = fetch_fred(config['fred_series'][0], config['fred_series'][1])
        all_results['fred'] = fred
        print(f"    FRED: {len(fred)} data points")
        
        wb, wb_err = fetch_worldbank(config['wb_indicator'])
        all_results['worldbank'] = wb
        print(f"    World Bank: {len(wb)} data points")
    
    # 5. Trade Forums (if applicable)
    trade_types = ['plumbing', 'hvac', 'electrical', 'contractor']
    if any(t in query.lower() for t in trade_types):
        print("  [5/7] Trade Forums...")
        for t in trade_types:
            if t in query.lower():
                tf, tf_err = search_trade_forums(query, trade_type=t, limit=3)
                all_results['trade_forums'] = tf
                print(f"    {t.capitalize()} forums: {len(tf)} links")
                break
    
    # 6. Recommended Sources
    print("  [6/7] Recommended Sources...")
    rec = recommend_sources(vertical or query)
    all_results['recommended_sources'] = rec
    print(f"    Found {len(rec)} relevant source categories")
    
    # 7. Google Trends (placeholder)
    print("  [7/7] Trends...")
    tr, tr_err = search_google_trends(query)
    all_results['trends'] = tr
    print(f"    Trends: {len(tr)} results")
    
    # Generate summary
    total = sum(len(v) if isinstance(v, list) else sum(len(x) for x in v.values()) if isinstance(v, dict) else 0 
                for v in all_results.values())
    
    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"  SCOUT COMPLETE: {total} total data points in {elapsed:.1f}s")
    print(f"{'='*60}\n")
    
    return all_results


def format_scout_report(all_results, query, vertical=None):
    """
    Format scout results into a boardroom-ready report.
    """
    report = f"""SCOUT MASTER REPORT
Query: {query}
Vertical: {vertical or 'general'}
Generated: {datetime.now().isoformat()}

{'='*60}
"""
    
    # Stack Overflow
    if all_results.get('stackoverflow'):
        report += f"\nSTACK OVERFLOW INSIGHTS ({len(all_results['stackoverflow'])} results):\n"
        for i, item in enumerate(all_results['stackoverflow'][:3], 1):
            report += f"  {i}. [{item['score']}↑] {item['title']}\n"
            report += f"     Views: {item['views']} | Answers: {item['answers']}\n"
            report += f"     Tags: {', '.join(item['tags'][:3])}\n"
    
    # GitHub
    if all_results.get('github'):
        report += f"\nGITHUB INSIGHTS ({len(all_results['github'])} results):\n"
        for i, item in enumerate(all_results['github'][:3], 1):
            report += f"  {i}. {item['name']} ({item['stars']}⭐ {item['forks']}🍴)\n"
            report += f"     {item['language']} | {item['description'][:60]}\n"
    
    # Reddit
    if all_results.get('reddit'):
        report += f"\nREDDIT DISCUSSONS:\n"
        for sub, posts in all_results['reddit'].items():
            if posts:
                report += f"  r/{sub}:\n"
                for post in posts[:2]:
                    report += f"    - [{post['score']}↑ {post['comments']}💬] {post['title'][:60]}\n"
    
    # Hacker News
    if all_results.get('hacker_news'):
        report += f"\nHACKER NEWS:\n"
        for i, item in enumerate(all_results['hacker_news'][:5], 1):
            report += f"  {i}. [{item['points']}pts] {item['title'][:60]}\n"
    
    # Economic Data
    if all_results.get('bls'):
        report += f"\nBLS DATA:\n"
        for item in all_results['bls'][:3]:
            report += f"  {item['period']} {item['year']}: {item['value']} ({item['series']})\n"
    
    if all_results.get('fred'):
        report += f"\nFRED DATA:\n"
        for item in all_results['fred'][:3]:
            report += f"  {item['date']}: {item['value']} ({item['label']})\n"
    
    # Recommended Sources
    if all_results.get('recommended_sources'):
        report += f"\nRECOMMENDED SOURCES:\n"
        for src in all_results['recommended_sources'][:5]:
            report += f"  - {src['name']} ({src['quality']}): {src['url']}\n"
    
    # Add vertical intel if available
    if vertical and vertical in VERTICAL_CONFIGS:
        report += f"\n{VERTICAL_CONFIGS[vertical]['name']} DOMAIN INTEL:\n"
        report += VERTICAL_CONFIGS[vertical]['intel']
    
    return report


def scout_for_boardroom(query, vertical=None, deep=True):
    """
    Scout specifically for boardroom input.
    Returns formatted context to feed into boardroom.
    """
    # First, try to get vertical context
    context_parts = []
    
    if vertical and vertical in VERTICAL_CONFIGS:
        context_parts.append(f"VERTICAL: {VERTICAL_CONFIGS[vertical]['name']}")
        context_parts.append(f"INTEL: {VERTICAL_CONFIGS[vertical]['intel'][:500]}")
    
    # Scout across key sources
    print(f"\n  Scouting for boardroom: {query}...")
    
    # Developer forums
    so, _ = search_stack_overflow(query, limit=3)
    if so:
        context_parts.append(f"DEVELOPER PAIN POINTS: {'; '.join([item['title'][:50] for item in so[:3]])}")
    
    # Reddit discussions - expanded subreddits
    trade_subs = ['Plumbing', 'HVAC', 'Electricians', 'Construction', ' Contractor', 'DIY', 'HomeImprovement']
    general_subs = ['programming', 'learnprogramming', 'startups', 'Entrepreneur', 'saas', 'smallbusiness', 'sideproject']
    
    all_reddit = []
    for sub in general_subs + trade_subs:
        r, _ = search_reddit(query, subreddit=sub, limit=2)
        if r:
            all_reddit.extend([f"r/{sub}: {item['title'][:40]}" for item in r])
    if all_reddit:
        context_parts.append(f"REDDIT BUZZ: {' | '.join(all_reddit[:5])}")
    
    # Hacker News
    hn, _ = search_hacker_news(query, limit=3)
    if hn:
        context_parts.append(f"TECH TRENDS: {'; '.join([item['title'][:40] for item in hn[:3]])}")
    
    # Trade forums (if applicable)
    trade_keywords = ['plumbing', 'hvac', 'electrical', 'contractor', 'construction', 'trade', 'craftsman']
    if any(kw in query.lower() for kw in trade_keywords):
        for trade in ['plumbing', 'hvac', 'electrical', 'construction']:
            tf, _ = search_trade_forums(query, trade_type=trade, limit=2)
            if tf:
                context_parts.append(f"{trade.upper()} FORUMS: {'; '.join([f"{t['forum_name']}: {t.get('title', 'search available')}" for t in tf[:2]])}")
                break
    
    # Economic data
    if vertical and vertical in VERTICAL_CONFIGS:
        config = VERTICAL_CONFIGS[vertical]
        bls, _ = fetch_bls(config['bls_series'])
        if bls:
            context_parts.append(f"MARKET DATA: {bls[0]['value']} {bls[0]['series']} in {bls[0]['year']}")
    
    # GitHub activity
    gh, _ = search_github(query, limit=3)
    if gh:
        context_parts.append(f"GITHUB ACTIVITY: {'; '.join([f'{item['name']} ({item['stars']}⭐)' for item in gh[:3]])}")
    
    return "\n".join(context_parts)


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Scout Master - Comprehensive Data Intelligence'
    )
    parser.add_argument(
        '--query', 
        type=str,
        help='Search query for scouting'
    )
    parser.add_argument(
        '--vertical', 
        type=str,
        help='Vertical/industry (saas, programming, plumbing, hvac, electrical, contractor)'
    )
    parser.add_argument(
        '--deep', 
        action='store_true',
        help='Deep scout with economic data'
    )
    parser.add_argument(
        '--for-boardroom', 
        action='store_true',
        help='Format output for boardroom input'
    )
    parser.add_argument(
        '--limit', 
        type=int,
        default=15,
        help='Max results per source'
    )
    parser.add_argument(
        '--output', 
        type=str,
        default=None,
        help='Save report to file'
    )
    
    args = parser.parse_args()
    
    if not args.query:
        print("Error: --query required")
        print("Try: python scout_master.py --query 'gamified debugger' --vertical saas")
        sys.exit(1)
    
    if args.for_boardroom:
        # Quick scout for boardroom
        context = scout_for_boardroom(args.query, args.vertical, args.deep)
        print(f"\nBOARDROOM CONTEXT:\n{context}")
    else:
        # Full scout
        results = scout_all(args.query, args.vertical, args.limit)
        report = format_scout_report(results, args.query, args.vertical)
        print(report)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
