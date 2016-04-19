from urllib.parse import urljoin
from faker import Faker
import requests

from settings import *

fake = Faker()


class DataGenerator(object):
    access_tokens = []

    def generate_access_tokens(self):
        for i in range(USERS_COUNT):
            response = requests.post(
                urljoin(URL, SIGN_UP_URL),
                {'username': fake.user_name(), 'password': fake.password(),
                 'first_name': fake.first_name(), 'last_name': fake.last_name()})
            self.access_tokens.append(response.json()['session']['access_token'])

    def create_bands(self):
        for i in range(BANDS_COUNT):
            access_token = self.access_tokens[i % len(self.access_tokens)]
            response = requests.post(
                urljoin(URL, BANDS_URL),
                {'name': fake.company(), 'description': fake.text()},
                headers={'token': access_token}
            )
            print(response.json())

    def create_compositions(self):
        pass

    def run(self):
        self.generate_access_tokens()
        self.create_bands()
        self.create_compositions()


def main():
    DataGenerator().run()


if __name__ == '__main__':
    main()
