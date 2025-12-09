import requests
import csv
import parsel
import time

# 1. 定義目標 URL 基礎和頁數範圍
BASE_URL = 'https://ssr1.scrape.center/page/'
START_PAGE = 1
END_PAGE = 10
# 輸出檔案名稱
OUTPUT_FILE = 'movie.csv'

# 設定 CSV 檔案的標頭
FIELDNAMES = ['電影名稱', '電影圖片 URL', '評分', '類型']

def scrape_movie_data():
    """
    執行爬蟲和資料儲存的主要函數。
    """
    all_movies = []

    print(f"--- 🚀 開始爬取 {START_PAGE} 到 {END_PAGE} 頁的電影資訊 ---\n")
    
    # 遍歷所有頁面
    for page in range(START_PAGE, END_PAGE + 1):
        url = f'{BASE_URL}{page}'
        print(f"正在爬取：{url}")
        
        try:
            # 發送 HTTP GET 請求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            # 使用 parsel 進行解析
            selector = parsel.Selector(response.text)
            
            # 找到所有電影資訊的區塊 (每個 .item)
            movie_items = selector.css('.item')
            
            print(f"  📽️ 找到 {len(movie_items)} 部電影")
            
            # 從每一頁解析「電影資訊」
            for item in movie_items:
                # 擷取 電影名稱
                # ✅ 正確路徑：.item 中的 h2 標籤
                title = item.css('h2::text').get(default='N/A')
                if title:
                    title = title.strip()
                else:
                    title = 'N/A'
                
                # 擷取 電影圖片 URL
                # ✅ 正確路徑：.item 中 img.cover 的 src 屬性
                image_url = item.css('img.cover::attr(src)').get(default='N/A')
                if image_url:
                    image_url = image_url.strip()
                else:
                    image_url = 'N/A'
                
                # 擷取 評分
                # ✅ 正確路徑：.item 中 .score 的文本內容
                score = item.css('.score::text').get(default='N/A')
                if score:
                    score = score.strip()
                else:
                    score = 'N/A'
                
                # 擷取 類型
                # ✅ 正確路徑：.item 中 .categories 內所有 button 的 span 文本
                categories = item.css('.categories button span::text').getall()
                genres = ' | '.join([c.strip() for c in categories]) if categories else 'N/A'
                
                # 將資料儲存為字典
                movie_data = {
                    '電影名稱': title,
                    '電影圖片 URL': image_url,
                    '評分': score,
                    '類型': genres
                }
                
                all_movies.append(movie_data)
                
                # 除錯: 印出爬取的資料
                print(f"    ✓ {title} | 評分: {score} | 類型: {genres}")
            
            print(f"✅ 第 {page} 頁爬取完成，共新增 {len(movie_items)} 筆資料。\n")
            
            # 禮貌性延遲，避免頻繁請求
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"❌ 爬取 {url} 時發生錯誤: {e}\n")
            continue

    print("--- 💾 爬取結束，開始儲存資料 ---")
    
    # 存成 movie.csv
    try:
        # 使用 utf-8-sig 確保中文在 Excel 中正確顯示
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            
            # 寫入標頭
            writer.writeheader()
            
            # 寫入電影資料
            writer.writerows(all_movies)
            
        print(f"🎉 資料成功儲存至檔案：{OUTPUT_FILE}")
        print(f"📊 共爬取 {len(all_movies)} 筆電影紀錄。\n")
        
    except Exception as e:
        print(f"❌ 儲存檔案時發生錯誤: {e}")

if __name__ == "__main__":
    scrape_movie_data()
