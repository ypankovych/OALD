import os
import funcy
import requests
from mixpanel import Mixpanel
from bs4 import BeautifulSoup
from telegraph import Telegraph

mp = Mixpanel(os.environ.get('mix_token'))
telegraph = Telegraph()
telegraph.create_account(short_name='1337')
accents = {
    'uk': {'class': 'sound audio_play_button pron-uk icon-audio',
           'name': 'United Kingdom'},
    'us': {'class': 'sound audio_play_button pron-us icon-audio',
           'name': 'United States'}
}

audio_url = os.environ.get('audio_url')
search_url = os.environ.get('search_url')
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
}


def track_action(user_id, word):
    mp.track(str(user_id), 'search', {'word': word})


def search(query):
    result = requests.get(search_url.format(query),
                          timeout=1000,
                          headers=headers).json()
    return [x['searchtext'] for x in result['results']]


def get_soup(text, ):
    response = requests.get(audio_url.format(text.replace(" ", '+'), text),
                            headers=headers,
                            allow_redirects=False,
                            timeout=10000)
    if response.status_code == 200:
        return BeautifulSoup(response.text, features='lxml')


@funcy.ignore(AttributeError)
def get_audio(word, accent):
    html = get_soup(word.replace(' ', '+'))
    audio = html.find('div', class_=accents[accent]['class']).get('data-src-mp3')
    if audio:
        return {
            'audio': audio,
            'examples': get_examples(word, html)
        }


def get_examples(word, soup):
    examples = [x.text for x in soup.find_all('span', class_='x')]
    if not examples:
        return False
    return make_telegraph(word, '\n-\n'.join(examples))


def make_telegraph(word, text):
    response = telegraph.create_page(
        f'Examples for [{word}]',
        html_content=text
    )
    return 'http://telegra.ph/{}'.format(response['path'])
