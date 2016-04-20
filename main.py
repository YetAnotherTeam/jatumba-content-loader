import random
from urllib.parse import urljoin
from faker import Faker
import requests

from settings import *

fake = Faker('ru_RU')


class DataGenerator(object):
    access_tokens = []
    bands = []
    compositions = []

    def generate_access_tokens(self):
        for i in range(USERS_COUNT):
            first_name, last_name = fake.name().split(' ', 1)
            response = requests.post(
                urljoin(URL, SIGN_UP_URL),
                {'username': fake.user_name(), 'password': fake.password(),
                 'first_name': first_name, 'last_name': last_name})
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

    def run(self):
        self.generate_access_tokens()
        self.create_bands()
        self.create_compositions()


def main():
    DataGenerator().run()


if __name__ == '__main__':
    main()
