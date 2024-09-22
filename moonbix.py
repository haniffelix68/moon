import requests, time

class MoonBix:
    def __init__(self, token, proxy=None):
        self.session = requests.session()
        self.session.headers.update({
            'authority': 'www.binance.com',
            'accept': '*/*',
            'accept-language': 'en-EG,en;q=0.9,ar-EG;q=0.8,ar;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'bnc-location': '',
            'clienttype': 'web',
            'content-type': 'application/json',
            'lang': 'en',
            'origin': 'https://www.binance.com',
            'referer': 'https://www.binance.com/en/game/tg/moon-bix',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        })
        
        # Gunakan proxy jika tersedia
        if proxy:
            self.session.proxies.update({
                'http': proxy,
                'https': proxy,
            })

        self.token = token
        self.game_response = None

    def login(self):
        json_data = {
            'queryString': self.token,
            'socialType': 'telegram',
        }

        response = self.session.post(
            'https://www.binance.com/bapi/growth/v1/friendly/growth-paas/third-party/access/accessToken',
            json=json_data,
        )


        if response.status_code != 200:
            return False

        data = response.json()

        accessToken = data['data']['accessToken']
        self.session.headers['x-growth-token'] = accessToken

        return response.status_code == 200

    def user_info(self):
        json_data = {
            'resourceId': 2056,
        }

        response = self.session.post(
            'https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info',
            json=json_data,
        )

        # Cetak response JSON untuk user info
        print("User Info Response JSON:", response.json())

        return response.json()

    def game_data(self):
        url = 'https://vemid42929.pythonanywhere.com/api/v1/moonbix/play'

        response = requests.post(url, json=self.game_response).json()

        if response['message'] == 'success':
            self.game = response['game']
            return True

        print(response['message'])
        return False

    def complete_game(self):
        json_data = {
            'resourceId': 2056,
            'payload': self.game['payload'],
            'log': self.game['log'],
        }

        response = self.session.post(
            'https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/complete',
            json=json_data,
        )

        return response.json()['success']
    def start_game(self):
        while True:  # Terus mencoba sampai tidak ada lagi attempts
            json_data = {
                'resourceId': 2056,
            }

            response = self.session.post(
                'https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/start',
                json=json_data,
            )

            self.game_response = response.json()

            if self.game_response['code'] == '000000':
                return True  # Game berhasil dimulai

            elif self.game_response['code'] == '116002':  # Attempts not enough
                print('Attempts not enough! Pindah ke akun berikutnya.')
                return False  # Keluar dari loop dan pindah ke akun berikutnya

            else:
                print("ERROR! Tidak dapat memulai game.")
                return False  # Jika error lain, langsung pindah akun


    def start(self):
        if not self.login():
            print("Failed to login")
            return
        print("Logged in successfully!")

        while self.start_game():
            print("Game has started!")
            sleep(45)  # Waktu menunggu sebelum mengambil game data

            if not self.game_data():
                print("Failed to generate game data!")
                return

            print("Game data generated successfully!")

            if not self.complete_game():
                print("Failed to complete game")

            print(f"Game completed! You earned + {self.game['log']}")
            sleep(15)  # Menunggu sebentar sebelum mencoba memulai game berikutnya

        print("Attempts not enough! Pindah ke akun berikutnya.")

def sleep(seconds):
    """Menampilkan hitungan mundur dalam format 00:00:00"""
    while seconds > 0:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds_left = divmod(remainder, 60)
        time_str = f'{hours:02}:{minutes:02}:{seconds_left:02}'
        print(f'\rMenunggu {time_str}', end='', flush=True)
        time.sleep(1)
        seconds -= 1
    print()  # Baris baru setelah hitung mundur selesai



if __name__ == '__main__':
    # Membaca proxy jika tersedia
    use_proxy = input("Apakah ingin menggunakan proxy? (y/n): ").strip().lower()
    proxies = []

    if use_proxy == 'y':
        with open('proxie.txt') as p:
            proxies = [line.strip() for line in p.readlines()]

    while True:
        # Membaca token dari file tokens.txt
        with open('tokens.txt') as f:
            tokens = f.readlines()

        for index, token in enumerate(tokens, start=1):
            print(f'============================= Akun {index} =============================')
            proxy = proxies[(index - 1) % len(proxies)] if proxies else None
            x = MoonBix(token.strip(), proxy)
            x.start()
            print(f'============================= Akun {index} selesai ======================')
            sleep(15)

        # Delay 1 jam sebelum memulai lagi dari akun pertama dengan hitungan mundur
        print("Semua akun telah selesai")
        sleep(3600)
