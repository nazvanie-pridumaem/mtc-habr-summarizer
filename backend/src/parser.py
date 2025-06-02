import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_comments_html(article_url, article_author):
    comments_url = article_url.rstrip('/') + '/comments/'
    try:
        response = requests.get(comments_url, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        comment_blocks = soup.find_all('div', class_='tm-comment__body-content')
        author_tags = soup.find_all('a', class_='tm-user-info__username')

        comments = []
        author_comments = []

        for block, author_tag in zip(comment_blocks, author_tags):
            comment_text = block.get_text(strip=True)
            author_name = author_tag.text.strip()
            comment_data = {'author': author_name, 'text': comment_text}
            comments.append(comment_data)
            if author_name == article_author:
                author_comments.append(comment_data)

        return comments, author_comments
    except Exception as e:
        return [], []

def parse_article(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {}

    try:
        data['url'] = url
        data['title'] = soup.find('h1', class_='tm-title').text.strip()
        data['author'] = soup.find('span', class_='tm-user-info__user').text.strip().split(' ')[0]
        data['date'] = soup.find('time')['datetime']

        reading_time_tag = soup.find('span', class_='tm-article-reading-time__label')
        data['reading_time'] = reading_time_tag.text.strip() if reading_time_tag else None

        views_tag = soup.find_all('span', class_='tm-icon-counter__value')
        data['views'] = views_tag[-1].text.strip() if views_tag else None

        text_block = soup.find('div', id='post-content-body')

        if text_block:
            for tag in text_block.find_all():
                if tag.name not in ['h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'li', 'blockquote', 'br', 'b']:
                    tag.unwrap()

            data['text_content'] = ''.join(str(child) for child in text_block.contents)
        else:
            data['text_content'] = ''

        images = text_block.find_all('img') if text_block else []
        data['image_content'] = [img['src'] for img in images if 'src' in img.attrs]

        tags = soup.find_all('a', class_='tm-tags-list__link')
        data['tags'] = [tag.text.strip() for tag in tags]

        comments, author_comments = get_comments_html(url, data['author'])
        data['comments'] = comments
        data['comments_from_author'] = author_comments

    except Exception as e:
        return None


    return data
