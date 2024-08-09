import os
import csv

import pandas as pd

from create_list import login_to_netease, create_playlist
from download import get_songs_id, download_song
from ks_key import estimate_key
from tqdm import tqdm

def download_and_classify_songs(singer_url, download_path='./music', key_duration=30, k=None):
    # 获取歌曲ID列表
    song_list, playlist_name = get_songs_id(singer_url)

    # 确保下载目录存在
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # CSV 文件路径
    csv_file_path = os.path.join(download_path, f'{playlist_name}_Key_Classification.csv')
    # 创建或清空 CSV 文件，并写入表头
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Song Name', 'Song ID', 'Key'])

    # 遍历下载每首歌曲并计算 Key
    for song_name, song_id in tqdm(song_list):
        # 下载歌曲
        download_song(song_name, song_id, download_path)

        # 构建歌曲文件路径
        song_file = os.path.join(download_path, f"{song_name}.mp3")

        # 判断歌曲文件是否存在
        if os.path.exists(song_file):
            try:
                # 估算歌曲的 Key
                key = estimate_key(song_file, duration=key_duration, key=k)

                # 检查 key 是否成功计算
                if key is not None:
                    # 将歌曲信息和 Key 写入 CSV 文件
                    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([song_name, song_id, key])
                    # print(f"《{song_name}》已下载并分类，Key：{key}")
                else:
                    print(f"无法计算《{song_name}》的 Key")

                # 删除原始歌曲文件
                os.remove(song_file)
                # print(f"《{song_name}》的原始文件已删除")

            except Exception as e:
                print(f"处理《{song_name}》时出错: {e}")

        else:
            print(f"歌曲文件《{song_name}》未找到，跳过分类")

    return csv_file_path, playlist_name
if __name__ == '__main__':

    # 爬取歌曲 你的歌单
    playlist_id = str(input('输入你的歌单id: '))
    singer_url = "https://music.163.com/playlist?id=" + playlist_id
    try:
        option = int(input("想要进行分类的调性 (输入序号): \n\t1 - Major \n\t2 - Minor \n\t3 - Both\n\t推荐 Major, 现在的算法区分不清大小调>>> "))
    except KeyboardInterrupt:
        exit(0)
    if option == 1:
        k = 'major'
    elif option == 2:
        k = 'minor'
    else:
        k = 'both'
    KC_file_path, playlist_name = download_and_classify_songs(singer_url, k=k)

    bot, user_token = login_to_netease()

    df = pd.read_csv(KC_file_path)
    df_group = df.groupby(by=['Key'])

    for name, group in tqdm(df_group):
        song_id_list = group['Song ID'].tolist()
        new_playlist_name = playlist_name + '_Key_' + name[0]
        create_playlist(bot, user_token, new_playlist_name, song_id_list)



