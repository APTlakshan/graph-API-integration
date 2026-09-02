import os
import random
import json
import feedparser
import requests
import time
from dotenv import load_dotenv
from supabase import create_client, Client

# .env ෆයිල් එකෙන් රහස් දත්ත ලබා ගැනීම
load_dotenv()

PAGE_ID = os.getenv("PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Supabase Configurations
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://www.investing.com/rss/news_25.rss",
    "https://finance.yahoo.com/news/rssindex"
]

def load_posted_news_from_db():
    """Supabase ඩේටාබේස් එකෙන් මීට පෙර පෝස්ට් කළ නිව්ස් වල මාතෘකා ලබා ගැනීම"""
    try:
        response = supabase.table("posted_news").select("news_title").execute()
        return set(row["news_title"] for row in response.data)
    except Exception as e:
        print(f"Error loading from Supabase: {e}")
        return set()

def save_posted_news_to_db(news_title):
    """අලුතින් පෝස්ට් කළ නිව්ස් එක Supabase ඩේටාබේස් එකට ඇතුළත් කිරීම"""
    try:
        supabase.table("posted_news").insert({"news_title": news_title}).execute()
        print("News successfully saved to Supabase database!")
    except Exception as e:
        print(f"Error saving to Supabase: {e}")

def fetch_latest_financial_news():
    posted_news = load_posted_news_from_db()
    shuffled_feeds = RSS_FEEDS.copy()
    random.shuffle(shuffled_feeds)
    
    for feed_url in shuffled_feeds:
        print(f"Checking feed: {feed_url}")
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries:
            title = entry.title
            if title not in posted_news:
                summary = getattr(entry, 'summary', title)
                return title, f"{title}. {summary}"
                
    return None, None

def analyze_news_with_deepseek(raw_news):
    try:
        deepseek_url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = (
            "You are an objective financial news writer. Analyze the following news and return a JSON object with 2 keys:\n"
            "1. 'post_content': A clear, professional, neutral summary of the news, strictly avoiding financial advice, "
            "hype words, or speculative guarantees. Make it educational and conclude with 3 relevant hashtags.\n"
            "2. 'search_keyword': A highly specific English search query (3-5 words) to find a matching photo or video "
            "on Unsplash/Pexels (e.g., 'ethereum cryptocurrency blockchain', 'forex trading candlestick chart').\n\n"
            f"News text: {raw_news}"
        )

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You must respond strictly in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        
        ds_resp = requests.post(deepseek_url, json=payload, headers=headers, timeout=25)
        if ds_resp.status_code == 200:
            result = json.loads(ds_resp.json()['choices'][0]['message']['content'])
            return result.get("post_content"), result.get("search_keyword")
    except Exception as e:
        print(f"DeepSeek API Error: {e}")
    return None, None

def publish_automated_post():
    print("1. Fetching unposted live news from RSS...")
    news_title, raw_news = fetch_latest_financial_news()
    
    if not news_title:
        print("No new unique financial news found at this moment.")
        return

    print(f"Selected News: {news_title}")

    print("2. Analyzing & Generating Content with DeepSeek AI...")
    content, search_keyword = analyze_news_with_deepseek(raw_news)
    
    if not content or not search_keyword:
        print("Failed to analyze content via DeepSeek.")
        return

    print(f"AI Suggested Search Keyword for Media: '{search_keyword}'")

    # ප්‍රචාරක විස්තරය (Promotional Footer) සකස් කිරීම
    promotional_footer = (
    "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🚨📊 𝗛𝗢𝗪 𝗪𝗜𝗟𝗟 𝗧𝗛𝗜𝗦 𝗡𝗘𝗪𝗦 𝗜𝗠𝗣𝗔𝗖𝗧 𝗧𝗛𝗘 𝗠𝗔𝗥𝗞𝗘𝗧? 📊🚨\n"
    "💭 𝗪𝗵𝗮𝘁 𝗱𝗼 𝘆𝗼𝘂 𝘁𝗵𝗶𝗻𝗸?\n"
    "📈 𝗕𝗨𝗟𝗟𝗜𝗦𝗛 𝗼𝗿 📉 𝗕𝗘𝗔𝗥𝗜𝗦𝗛?\n"
    "👇 𝗗𝗿𝗼𝗽 𝗬𝗼𝘂𝗿 𝗧𝗵𝗼𝘂𝗴𝗵𝘁𝘀 𝗶𝗻 𝘁𝗵𝗲 𝗖𝗼𝗺𝗺𝗲𝗻𝘁𝘀 𝗕𝗲𝗹𝗼𝘄! 👇\n\n"
    "⚠️ 𝗗𝗶𝘀𝗰𝗹𝗮𝗶𝗺𝗲𝗿:\n"
    "This post is for informational purposes only and should not be considered financial advice. Always conduct your own research before making investment decisions.\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🇱🇰 𝗦𝗪𝗔𝗣 𝗚𝗔𝗧𝗘 𝗧𝗘𝗔𝗠\n"
    "🚨 𝗨𝗦𝗗𝗧 𝗕𝗨𝗬 & 𝗦𝗘𝗟𝗟 – 𝗦𝗥𝗜 𝗟𝗔𝗡𝗞𝗔 𝗢𝗡𝗟𝗬 🇱🇰\n\n"
    "🔐 𝗦𝗲𝗰𝘂𝗿𝗲 & 𝗥𝗲𝗹𝗶𝗮𝗯𝗹𝗲\n"
    "⚡ 𝗙𝗮𝘀𝘁 𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴\n"
    "🏦 𝗟𝗼𝗰𝗮𝗹 𝗕𝗮𝗻𝗸 𝗦𝘂𝗽𝗽𝗼𝗿𝘁\n"
    "💬 𝗗𝗲𝗱𝗶𝗰𝗮𝘁𝗲𝗱 𝗖𝘂𝘀𝘁𝗼𝗺𝗲𝗿 𝗦𝘂𝗽𝗽𝗼𝗿𝘁\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🌍 𝗪𝗢𝗥𝗟𝗗𝗪𝗜𝗗𝗘 𝗡𝗘𝗪𝗦 𝗔𝗖𝗖𝗘𝗦𝗦\n\n"
    "📰 Understand how major global news can impact the 𝗙𝗼𝗿𝗲𝘅 & 𝗖𝗿𝘆𝗽𝘁𝗼 𝗺𝗮𝗿𝗸𝗲𝘁𝘀 — clearly explained in your own language, based on the country you are in.\n\n"
    "📊 Stay updated with the latest 𝗖𝗿𝘆𝗽𝘁𝗼 & 𝗠𝗮𝗿𝗸𝗲𝘁 𝗡𝗲𝘄𝘀 through our website’s 𝗡𝗲𝘄𝘀 𝗢𝗽𝗲𝗿𝗮𝘁𝗶𝗼𝗻 section.\n\n"
    "🔗 𝗪𝗵𝗮𝘁𝘀𝗔𝗽𝗽\n"
    "https://chat.whatsapp.com/LgCZ5CTuKujEdq9pR2xMMG\n\n"
    "🌐 𝗪𝗲𝗯𝘀𝗶𝘁𝗲\n"
    "http://www.swapgate-store.com\n\n"
    "📞 𝗖𝗮𝗹𝗹 / 𝗪𝗵𝗮𝘁𝘀𝗔𝗽𝗽\n"
    "+94 71 753 3547\n\n"
    "🚀 𝗦𝘄𝗮𝗽 𝗚𝗮𝘁𝗲 – 𝗧𝗿𝗮𝗱𝗲 𝘄𝗶𝘁𝗵 𝗖𝗼𝗻𝗳𝗶𝗱𝗲𝗻𝗰𝗲!"
)
    
    # AI කන්ටෙන්ට් එක සමඟ ප්‍රචාරක කොටස එකතු කිරීම
    final_content = content + promotional_footer

    chosen_media = random.choices(["photo", "video"], weights=[0.3, 0.7])[0]
    print(f"Selected Media Type: {chosen_media.upper()}")

    success = False

    try:
        if chosen_media == "photo":
            unsplash_url = f"https://api.unsplash.com/photos/random?query={search_keyword}&client_id={UNSPLASH_ACCESS_KEY}"
            img_resp = requests.get(unsplash_url, timeout=15)
            
            if img_resp.status_code == 200:
                media_url = img_resp.json()['urls']['regular']
                fb_url = f"https://graph.facebook.com/{PAGE_ID}/photos"
                fb_payload = {'url': media_url, 'caption': final_content, 'access_token': PAGE_ACCESS_TOKEN}
                res = requests.post(fb_url, data=fb_payload, timeout=20)
                
                if res.status_code == 200:
                    print("Photo Post Result:", res.json())
                    success = True
                else:
                    print("Facebook Photo Error:", res.json())
        else:
            pexels_url = f"https://api.pexels.com/videos/search?query={search_keyword}&per_page=5"
            headers = {"Authorization": PEXELS_API_KEY}
            
            vid_resp = requests.get(pexels_url, headers=headers, timeout=15)
            if vid_resp.status_code == 200 and vid_resp.json().get('videos'):
                videos_list = vid_resp.json()['videos']
                selected_video = random.choice(videos_list)
                video_url = selected_video['video_files'][0]['link']
                
                fb_url = f"https://graph.facebook.com/{PAGE_ID}/videos"
                fb_payload = {'file_url': video_url, 'description': final_content, 'access_token': PAGE_ACCESS_TOKEN}
                res = requests.post(fb_url, data=fb_payload, timeout=30)
                
                if res.status_code == 200:
                    print("Video Post Result:", res.json())
                    success = True
                else:
                    print("Facebook Video Error:", res.json())
    except Exception as e:
        print(f"Network or Publishing Exception: {e}")

    if success:
        save_posted_news_to_db(news_title)
        print("News marked as posted in Supabase successfully!")

if __name__ == "__main__":
    random_delay = random.randint(0, 40) * 60
    print(f"Waiting for {random_delay // 60} minutes before posting...")
    time.sleep(random_delay)
    
    publish_automated_post()