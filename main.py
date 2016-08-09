import random
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from faker import Faker

from settings import *
from utils import Gender

fake = Faker()


class GOTParser(object):
    BASE_URL_TEMPLATE = (
        'http://gameofthrones.wikia.com/index.php?action=ajax&articleId=Characters'
        '&method=axGetArticlesPage&rs=CategoryExhibitionAjax&page={page}'
    )
    partition_part = 'gameofthrones/images'

    def get_pages_count(self):
        json_response = requests.get(self.BASE_URL_TEMPLATE.format(page=1)).json()
        soup = BeautifulSoup(json_response['paginator'], 'html.parser')
        return int(soup.find_all('a', attrs={'class': 'paginator-page'})[-1].string)

    def prepare_image_url(self, url):
        prepared_url = (
            'http://vignette2.wikia.nocookie.net/' + self.partition_part +
            url.partition(self.partition_part)[2]
        )
        prepared_url = prepared_url.replace('images/thumb', 'images/').rsplit('/', 1)[0]
        return prepared_url

    def parse_page(self, page):
        json_response = requests.get(self.BASE_URL_TEMPLATE.format(page=page)).json()
        soup = BeautifulSoup(json_response['page'], 'html.parser')
        characters_imgs = soup.find_all('img')
        result = [{
            'character_name': character_img['alt'],
            'image': self.prepare_image_url(character_img['src'])
        } for character_img in characters_imgs]
        return result

    def parse(self):
        pages_count = self.get_pages_count()
        result_list = []
        for page in range(1, pages_count + 1):
            result_list.extend(self.parse_page(page))
        for i in result_list:
            print(i)
        print(len(result_list))
        return result_list


class DataGenerator(object):
    avatar_urls = []
    access_tokens = []
    bands = []
    compositions = []
    instruments = []

    GENDER_CHOOSE_MAP = {
        Gender.M: ('first_name_male', 'last_name_male'),
        Gender.F: ('first_name_female', 'last_name_female')
    }

    def __init__(self, parsed_characters):
        self.parsed_characters = parsed_characters

    def _get_split_full_name(self):
        gender = random.choice([Gender.M, Gender.F])
        return [getattr(fake, method_name)() for method_name in self.GENDER_CHOOSE_MAP[gender]]

    def generate_access_tokens(self):
        for parsed_character in self.parsed_characters:
            name = parsed_character['character_name']
            split_full_name = name.split(maxsplit=1)
            first_name = split_full_name[0]
            last_name = '' if len(split_full_name) == 1 else split_full_name[1]
            username = name.replace(' ', '')
            avatar_url = parsed_character['image']
            avatar_response = requests.get(avatar_url)
            response = requests.post(
                urljoin(URL, SIGN_UP_URL),
                data={
                    'username': username,
                    'password': fake.password(),
                    'first_name': first_name,
                    'last_name': last_name
                },
                files={
                    'avatar': (avatar_url.rsplit('/', 1), avatar_response.content)
                }
            )
            print(response.content)
            if response.status_code != 201:
                print('{error}'.format(error=response.json()['username'][0]))
            else:
                self.access_tokens.append(response.json()['session']['access_token'])

    def create_bands(self):
        for i in range(BANDS_COUNT):
            access_token = self.access_tokens[i % len(self.access_tokens)]
            response = requests.post(
                urljoin(URL, BANDS_URL),
                {'name': fake.company(), 'description': fake.text()},
                headers={'token': access_token}
            )
            self.bands.append(response.json())

    def create_compositions(self):
        for i in range(COMPOSITIONS_COUNT):
            access_token = self.access_tokens[i % len(self.access_tokens)]
            response = requests.post(
                urljoin(URL, COMPOSITIONS_URL),
                {
                    'name': fake.text(max_nb_chars=30),
                    'band': self.bands[random.randint(0, len(self.bands) - 1)]['id']
                },
                headers={'token': access_token}
            )
            self.compositions.append(response.json())

    def get_instruments(self):
        access_token = self.access_tokens[0]
        json_response = requests.get(
            urljoin(URL, INSRTUMENT_URL),
            headers={'token': access_token}
        ).json()
        self.instruments_ids = [instrument['id'] for instrument in json_response]

    def create_members(self):
        for i in range(MEMBER_COUNT):
            access_token = self.access_tokens[i % len(self.access_tokens)]
            response = requests.post(
                urljoin(URL, MEMBER_URL),
                {
                    'instrument': self.instruments_ids[random.randint(
                        0,
                        len(self.instruments_ids) - 1)
                    ],
                    'band': self.bands[random.randint(0, len(self.bands) - 1)]['id']
                },
                headers={'token': access_token}
            )

    def run(self):
        # self.get_fake_avatars()
        self.generate_access_tokens()
        self.create_bands()
        self.create_compositions()
        self.get_instruments()
        self.create_members()


def main():
    parsed_characters = GOTParser().parse()
    DataGenerator(parsed_characters).run()


if __name__ == '__main__':
    main()
