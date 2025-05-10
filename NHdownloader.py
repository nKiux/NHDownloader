import requests
from multiprocessing import Pool, Manager
import os
from itertools import takewhile

def download_image(args):
    number, photo, shared_dict = args
    
    try:
        image_url = f"https://i1.nhentai.net/galleries/{number}/{photo}.jpg"
        filename = f"{number}/{number}_{photo}.jpg"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        print(f'Sending request to {image_url}')
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as file_path:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file_path.write(chunk)
        print(f"Image downloaded successfully as {filename}.")
        return True
    except requests.exceptions.RequestException:
        try:
            print(f"Retrying with webp format for image {photo}")
            image_url = f"https://i4.nhentai.net/galleries/{number}/{photo}.webp"
            filename = f"{number}/{number}_{photo}.webp"
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            with open(filename, 'wb') as file_path:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file_path.write(chunk)
            print(f"Image downloaded successfully as {filename}.")
            return True
        except requests.exceptions.RequestException:
            print(f"Both jpg and webf format failed for image {photo}")
            return False

def main():
    book_number = input("請輸入書籍編號: ")
    book_url = f"https://nhentai.net/g/{book_number}/1/"
    html = requests.get(book_url).text.split('>')
    for _ in html:
        if _.startswith('<img src="https://'):
            html_cpy = _
            number = html_cpy[43:50]

    with Manager() as manager:
        shared_dict = manager.dict()
        pool = Pool(processes=os.cpu_count())
        st, ed = map(int, input("請輸入下載範圍 (例如: 1-3000): ").split('-'))
        if st == 0:
            print("請將首頁設置為1")
            return
        tasks = [(number, i, shared_dict) for i in range(st, ed)]
        
        try:
            for i, success in enumerate(pool.imap(download_image, tasks), 1):
                if not success:
                    print(f"\n遇到錯誤，停止下載。")
                    print(f"已成功下載 {i-1} 張圖片")
                    break
        finally:
            pool.close()
            pool.join()

if __name__ == '__main__':
    main()

