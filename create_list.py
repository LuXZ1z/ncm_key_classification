import pandas as pd
from tqdm import tqdm
from ncmbot.ncmbot import *
import os
import json
import getpass
from math import ceil
from time import sleep

def separator():
    try:
        print("-" * os.get_terminal_size().columns)
    except OSError:
        print("-" * 17)

def login_to_netease():
    while True:
        separator()
        try:
            option = int(input("想要如何登录到网易云音乐？(推荐使用 Cookie 登录)\n\t1 - 用账号和密码\n\t2 - 用 HTTP Cookie\n>>> "))
        except KeyboardInterrupt:
            exit(0)
        except:
            continue
        if option == 1:
            separator()
            login_name = input("输入手机号码…\n>>> ")
            login_password = getpass.getpass("以及密码…\n>>> ")
            bot, resp = login(login_password, phone=login_name)
            login_resp = json.loads(json.dumps(dict(resp.headers)))['Set-Cookie']
        elif option == 2:
            separator()
            cookie_content = input("输入 Cookie 内容…\n>>> \n")
            login_resp = cookie_content

        try:
            MUSIC_U = login_resp.split('MUSIC_U=')[1].split(';')[0]
            user_token = login_resp.split('__csrf=')[1].split(';')[0]
            bot = NCloudBot(MUSIC_U)
            return bot, user_token
        except KeyboardInterrupt:
            exit(0)
        except:
            print("发生问题。请再试一次。")

def create_playlist(bot, user_token, playlist_name, song_id_list):
    chunk_size = 100
    separator()
    bot.method = 'CREATE_LIST'
    bot.params = {"csrf_token": user_token}
    bot.data = {"name": str(playlist_name), "csrf_token": user_token}
    bot.send()
    result = json.loads(bot.response.content.decode())

    separator()
    if result['code'] != 200:
        print("创建歌单失败。")
        return None

    new_playlist_id = result['id']
    sleep(1)

    for i in range(ceil(len(song_id_list) / chunk_size)):
        song_chunk = song_id_list[i * chunk_size: min((i + 1) * chunk_size, len(song_id_list))]
        bot.method = 'ADD_SONG'
        bot.params = {"csrf_token": user_token}
        bot.data = {"op": "add", "pid": new_playlist_id,
                    "trackIds": '[' + ','.join([str(v) for v in song_chunk]) + ']', "csrf_token": user_token}
        bot.send()
        final_response = json.loads(bot.response.content.decode())
        if final_response['code'] != 200:
            error_message = f"\n往歌单中添加歌曲{','.join([str(v) for v in song_chunk])}失败…\n{final_response}"
            print(error_message)
            with open('error_log.txt', 'a') as f:
                f.write(error_message + '\n')
        sleep(1)
    return new_playlist_id

def main():
    bot, user_token = login_to_netease()
    separator()

    df = pd.read_csv(r'xxx_Key_Classification.csv')
    df_group = df.groupby(by=['Key'])
    playlist_name = 'xxx歌单'

    for name, group in tqdm(df_group):
        song_id_list = group['Song ID'].tolist()
        new_playlist_name = playlist_name + '_Key_' + name[0]
        create_playlist(bot, user_token, new_playlist_name, song_id_list)

if __name__ == "__main__":
    main()
