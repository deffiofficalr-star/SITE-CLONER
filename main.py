import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class SiteCloner:
    def __init__(self, url, output_folder="site_clone"):
        self.url = url
        self.base_domain = urlparse(url).netloc
        self.output_folder = output_folder
        self.visited = set()
        self.downloaded = set()
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        self.images_folder = os.path.join(output_folder, "images")
        self.css_folder = os.path.join(output_folder, "css")
        self.js_folder = os.path.join(output_folder, "js")
        self.fonts_folder = os.path.join(output_folder, "fonts")
        
        for folder in [self.images_folder, self.css_folder, self.js_folder, self.fonts_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
    
    def download_file(self, url, local_path):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            return False
    
    def save_page(self, url, html):
        parsed = urlparse(url)
        filename = "index.html" if parsed.path in ['', '/'] else parsed.path.replace('/', '_')
        if not filename.endswith('.html'):
            filename += '.html'
        filepath = os.path.join(self.output_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return filepath
    
    def fix_links(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        
        for tag in soup.find_all(['link', 'script', 'img', 'a']):
            if tag.name == 'link' and tag.get('href'):
                href = tag['href']
                full_url = urljoin(base_url, href)
                
                if urlparse(full_url).netloc == self.base_domain:
                    if href.startswith('/'):
                        tag['href'] = f"{self.output_folder}{href}"
                    else:
                        tag['href'] = href
            
            elif tag.name == 'script' and tag.get('src'):
                src = tag['src']
                full_url = urljoin(base_url, src)
                if urlparse(full_url).netloc == self.base_domain:
                    tag['src'] = os.path.basename(src)
            
            elif tag.name == 'img' and tag.get('src'):
                src = tag['src']
                full_url = urljoin(base_url, src)
                if urlparse(full_url).netloc == self.base_domain:
                    img_name = os.path.basename(src)
                    tag['src'] = f"images/{img_name}"
                    self.download_file(full_url, os.path.join(self.images_folder, img_name))
            
            elif tag.name == 'a' and tag.get('href'):
                href = tag['href']
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == self.base_domain and full_url not in self.visited:
                    self.visited.add(full_url)
        
        return str(soup)
    
    def clone(self):
        print(f"🌐 Начинаю клонирование: {self.url}")
        print(f"📁 Сохранение в: {self.output_folder}")
        print("="*60)
        
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            html = response.text
            
            print("📄 Сохранение HTML...")
            saved_html = self.fix_links(html, self.url)
            self.save_page(self.url, saved_html)
            
            self.downloaded.add(self.url)
            print("✅ Главная страница сохранена")
            
            print("🔗 Ссылки исправлены")
            print(f"📁 Папки созданы: {self.output_folder}")
            print("="*60)
            print(f"✅ Готово! Открой {self.output_folder}/index.html")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def main():
    print("""
╔═══════════════════════════════════════════╗
║                                           ║
║   ███████╗██╗████████╗███████╗            ║
║   ██╔════╝██║╚══██╔══╝██╔════╝            ║
║   █████╗  ██║   ██║   █████╗              ║
║   ██╔══╝  ██║   ██║   ██╔══╝              ║
║   ██║     ██║   ██║   ███████╗            ║
║   ╚═╝     ╚═╝   ╚═╝   ╚══════╝            ║
║                                           ║
║         SITE-CLONER v1.0                   ║
║                                           ║
╚═══════════════════════════════════════════╝
    """)
    
    url = input("🌐 Введите URL сайта: ").strip()
    if not url:
        url = "https://example.com"
    
    if not url.startswith("http"):
        url = "https://" + url
    
    output = input("📁 Имя папки (Enter = site_clone): ").strip() or "site_clone"
    
    cloner = SiteCloner(url, output)
    cloner.clone()

if __name__ == "__main__":
    main()
