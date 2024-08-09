import os
import requests
from bs4 import BeautifulSoup
from mutagen.mp3 import MP3
def get_songs_id(singer_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Cookie': 'NMTID=00OPmoqe3PrjUn15E8GgeMhQ-CqRdgAAAGQ_Y0Yqg; _iuqxldmzr_=32; _ntes_nnid=3066f2cd4f5116246b0b223475ae7525,1722240799513; _ntes_nuid=3066f2cd4f5116246b0b223475ae7525; WEVNSM=1.0.0; WNMCID=loicxc.1722240800126.01.0; WM_TID=I5TGlZbFoc5BQAAFVEbDELqi1PcYeTZc; sDeviceId=YD-4G%2FCGZx4179BRgVVVFKXAf6nwOINfssy; ntes_utid=tid._.%252BNEV5pvqyMJFAlEUQEaSRfr2wLJMOspd._.0; __snaker__id=NNwQEXc8Og4LvpUk; __csrf=41458e754fb2c6001519e5980bdd30d5; MUSIC_U=00E6575FE7126AAE6D6A6908733EA8FF961684B127C9FE9809F2F8C3AD7D3853342A22292DF5F6FE479E3F54E64FF7C99C137DB41D63892A4DF17EC3C50F5E174B354E93494BD31C1C8CA4240B4CC75A5E3C2E7C74783B42F182A74A7D74E4F369EFAC8F84170E5898217BF11AED471FEF88BFB6AEE7BAF021EDB8B4F6920CBC23E7AE2994F4E00E3C3347061CB8A59D95FA324A6FBEF68E069A8926A8CEF8C9E7638128C12DDCF3C99339F59F166FEC31D6DC2FEF0046CC8A8267215BE23452900B78C480705843317EF75B7E5A088611C6BA58E4072C5EE514B0E1A8C7782D5FBE9661B44BADD6E6419DB8B59B77B1F606C0B0E60AF995FD3F1874552C16B08FCF153A3BCD2BC80805B9ECC8114B8A547E5863A6595223F02F0B0F2B493B1D4F7DC5BC61FE0FB0DC52D4BE097CCA367610547FBC321A138BB4138086921CEEBE37BD1BA8797A87906473A88B310FDA13540BBF53347BFD7D56EB2CE8F4F5A1A8; ntes_kaola_ad=1; gdxidpyhxdE=TlY03ehBjgt3yxL%2FBJqasTbuG36KNWS%2FdBkt8REsQ3o0uu4HSmS1Dnf2%2FT48hSj8s9OjKw7wh0dz%2FS32gEk%5CLh5o%2B8HSz5SarVlIzg9jIkgtNeSBgOVHncmi%2FnkSBRmhWaaVIIOK0D3%2Fjl7zSXSOBRXO5OWAl%2BvuWHAddYHXwcKiqGUY%3A1722831221887; WM_NI=gqgaegyr0IllMeAyTPSYP0b7eAiUJ7OrJe%2F8rjOwmiwmCN8k7HSww5d2eYpZhtL%2F%2FJvwBbX0CbETylq9lweT3FK6NZ45w6HYeUDiNDwfU6PKHEay8CiRE4yEQi3%2BLAPbZEk%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeccec7da78fbb8aaa3aaeeb8fa3d44e829b9fadc64fb5b30098c1668e8e9888c72af0fea7c3b92aa5afa982e86dbbae00aaef688fbb8f9ad75c9187a0d1e13da79fa7b6c93d8dae8686ae34b2b68198f063b5b38dafbb61f5989d98f63fa8eeabbaf352acac84d0ae42b6a98e83db3c81be8bb5fc68b3e7a498e860f19a85d7cd52f8ebb9d7cb53a78b8c8acd50b5ba9bd7d3418c9baf9abb49ab8e8bd5fc4f93b7fdcccf4b94be96a6ea37e2a3; JSESSIONID-WYYY=GMRFASyBBdjo9W5Mxf7lixCdSDjqPIvE0bPQBuJWQTuRzsr6RQAdhuCs%2F%5C%2BCqCxwsgIsMPiBUwO1%2B9eoGBIh8ejBYfPX73ss5g4W30jlcPgTeXQJdhz0Mgy0jx8GZzEVb%2BbYv7xT9me9T5Xf79AmgBBJs6DS0rnBCuvI09skYFef4qxi%3A1723032181926'
    }

    # 格式化下载链接
    url = singer_url.replace("/#", '')
    response = requests.get(url=url, headers=headers)

    # 实例化bs4
    soup = BeautifulSoup(response.text, 'lxml')

    # 获取歌曲列表
    song_list = soup.select("ul.f-hide li a")
    playlist_name = soup.select(".f-ff2.f-brk")

    songs_id = []
    for song in song_list:
        # 获取歌曲名称
        song_name = song.text
        # 获取歌曲ID
        song_id = song['href'].split("=")[1]
        songs_id.append([song_name, song_id])

    return songs_id, playlist_name[0].text

def is_valid_mp3(file_path):
    try:
        audio = MP3(file_path)
        return audio.info is not None
    except Exception:
        return False

def download_song(song_name, song_id, download_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    music_open_api = "http://music.163.com/song/media/outer/url?id=" + song_id
    music = requests.get(url=music_open_api, headers=headers)

    song_file = os.path.join(download_path, f"{song_name}.mp3")
    try:
        if not is_valid_mp3(song_file):
            raise Exception("Invalid MP3 file header.")

        with open(song_file, 'wb') as file:
            file.write(music.content)
            # print(f"《{song_name}》下载成功")

    except Exception as e:
        # print(f"{song_name} 下载异常: {e}，尝试使用外链下载")

        try:
            # 外链是针对 VIP 歌曲进行的，但是 VIP 歌曲只能下载 30s，对于我们的程序来说，够用了。
            music_open_api_2 = "https://link.hhtjim.com/163/" + song_id + '.mp3'
            music = requests.get(url=music_open_api_2, headers=headers)

            with open(song_file, 'wb') as file:
                file.write(music.content)
                # print(f"《{song_name}》外链下载成功")

        except Exception as e:
            print(f"{song_name} 下载异常: {e}")


if __name__ == '__main__':

    singer_url = "https://music.163.com/#/playlist?id=9858842273"
    song_list = get_songs_id(singer_url)

    for song_name, song_id in song_list:
        download_song(song_name, song_id, './music')