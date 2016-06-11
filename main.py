import random
from urllib.parse import urljoin

import requests
from faker import Faker

from settings import *
from utils import Gender

fake = Faker()


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

    def _get_split_full_name(self):
        gender = random.choice([Gender.M, Gender.F])
        return [getattr(fake, method_name)() for method_name in self.GENDER_CHOOSE_MAP[gender]]

    def get_fake_avatars(self):
        response = requests.get(RANDOM_USERS_URL_TEMPLATE.format(results=USERS_COUNT))
        for json_user in response.json()['results']:
            self.avatar_urls.append(json_user['picture']['large'])

    def generate_access_tokens(self):
        for i in range(USERS_COUNT):
            try_number = 0
            response = None
            avatar_url = self.avatar_urls[i]
            while True:
                first_name, last_name = self._get_split_full_name()
                avatar_response = requests.get(avatar_url)
                response = requests.post(
                    urljoin(URL, SIGN_UP_URL),
                    data={
                        'username': fake.user_name(),
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
                    try_number += 1
                    print(
                        'Try {count}: {error}'.format(
                            count=try_number,
                            error=response.json()['username'][0]
                        )
                    )
                else:
                    break
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
        self.get_fake_avatars()
        self.generate_access_tokens()
        self.create_bands()
        self.create_compositions()
        self.get_instruments()
        self.create_members()


def main():
    DataGenerator().run()


if __name__ == '__main__':
    main()
