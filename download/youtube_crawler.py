import time
from selenium import webdriver
import re
from download.downloader import download_by_song_object
from download.song import Song
import numpy as np
from constants.configs import config
from constants.configs import config_example
import os
import pandas as pd
from constants.parameters import filenames_parameters
from constants.parameters.url_parameters import youtube_karaoke_page_url

NUM_OF_SAMPLE = 10000


def get_all_youtubes_names():
    driver = webdriver.Chrome(config.web_driver_path)
    driver.get(youtube_karaoke_page_url)

    names = get_names(driver)

    driver.quit()

    # np.save('songs_name.npy', np.array(names))

    songs = get_songs_from_strings(names)

    return songs


def get_songs_from_strings(names):
    songs = []
    for name in names:
        try:
            parts = name.split('-')
            hebrew_song = parts[0]
            hebrew_singer = parts[1]
            english_song = to_english(hebrew_song)
            english_singer = to_english(hebrew_singer)
            songs.append(Song(hebrew_singer, hebrew_song, english_singer, english_song))
        except:
            print(f'failed in {name}')
    return songs


def get_names(driver):
    html = driver.page_source
    pattern = 'views" title="(.*?שרים קריוקי)" href="/watch?'
    names = re.findall(pattern, html)
    old_names = -1
    while not old_names == len(names) and len(names) < NUM_OF_SAMPLE:
        old_names = len(names)
        driver.execute_script("window.scrollTo(0, 100000);")
        time.sleep(config.sleep_time)
        html = driver.page_source
        pattern = 'views" title="(.*?שרים קריוקי)" href="/watch?'
        names = re.findall(pattern, html)
    return names[:NUM_OF_SAMPLE]


def to_english(hebrew_singer):
    hebrew_singer = re.sub('א', 'a', hebrew_singer)
    hebrew_singer = re.sub('ב', 'b', hebrew_singer)
    hebrew_singer = re.sub('ג', 'g', hebrew_singer)
    hebrew_singer = re.sub('ד', 'd', hebrew_singer)
    hebrew_singer = re.sub('ה', 'e', hebrew_singer)
    hebrew_singer = re.sub('ו', 'o', hebrew_singer)
    hebrew_singer = re.sub('ז', 'z', hebrew_singer)
    hebrew_singer = re.sub('ח', 'h', hebrew_singer)
    hebrew_singer = re.sub('ט', 't', hebrew_singer)
    hebrew_singer = re.sub('י', 'i', hebrew_singer)
    hebrew_singer = re.sub('כ', 'k', hebrew_singer)
    hebrew_singer = re.sub('ל', 'l', hebrew_singer)
    hebrew_singer = re.sub('מ', 'm', hebrew_singer)
    hebrew_singer = re.sub('נ', 'n', hebrew_singer)
    hebrew_singer = re.sub('ס', 's', hebrew_singer)
    hebrew_singer = re.sub('ע', 'a', hebrew_singer)
    hebrew_singer = re.sub('פ', 'p', hebrew_singer)
    hebrew_singer = re.sub('צ', 'ts', hebrew_singer)
    hebrew_singer = re.sub('ק', 'k', hebrew_singer)
    hebrew_singer = re.sub('ר', 'r', hebrew_singer)
    hebrew_singer = re.sub('ש', 'sh', hebrew_singer)
    hebrew_singer = re.sub('ת', 't', hebrew_singer)
    hebrew_singer = re.sub('ך', 'h', hebrew_singer)
    hebrew_singer = re.sub('ף', 'f', hebrew_singer)
    hebrew_singer = re.sub('צ', 'ch', hebrew_singer)
    hebrew_singer = re.sub('ץ', 'tz', hebrew_singer)
    hebrew_singer = re.sub('ם', 'm', hebrew_singer)
    hebrew_singer = re.sub('ן', 'n', hebrew_singer)
    return hebrew_singer


def save_metadata(downloaded_songs):


    hebrew_singer = []
    hebrew_song = []
    english_singer = []
    english_song = []
    directory_name = []
    is_karaoke = []
    relative_url = []
    youtube_url = []
    for song in downloaded_songs:
        hebrew_singer.append(song.singer_hebrew)
        hebrew_singer.append(song.singer_hebrew)
        hebrew_song.append(song.song_hebrew)
        hebrew_song.append(song.song_hebrew)
        english_singer.append(song.singer_english)
        english_singer.append(song.singer_english)
        english_song.append(song.song_english)
        english_song.append(song.song_english)
        directory_name.append(song.download_dir)
        directory_name.append(song.download_dir)

        is_karaoke.append(True)
        relative_url.append(os.path.join(song.get_song_file_name(), filenames_parameters.karaoke_name))
        youtube_url.append(song.karaoke_url)

        is_karaoke.append(False)
        relative_url.append(os.path.join(song.get_song_file_name(), filenames_parameters.song_name))
        youtube_url.append(song.song_url)

    df = pd.DataFrame({
        'hebrew_singer': hebrew_singer,
        'hebrew_song': hebrew_song,
        'english_singer': english_singer,
        'english_song': english_song,
        'directory_name': directory_name,
        'is_karaoke': is_karaoke,
        'relative_url': relative_url,
        'youtube_url': youtube_url
    })
    if os.path.exists(config.meta_data_file):
        initial_metadata = pd.read_csv(config.meta_data_file).reset_index(drop=True)
        if len(df) > 0:
            df = pd.concat([df,initial_metadata], join='outer')
        else:
            df = initial_metadata
    df = df.reset_index(drop=True)
    df.to_csv(config.meta_data_file, encoding='utf-8',index=False)


def main():
    config_attributes = dir(eval('config'))
    requested_attributes = dir(eval('config_example'))
    if any(x not in config_attributes for x in requested_attributes):
        raise Exception('config is not competable with config example')

    downloaded_songs = []

    # songs = get_all_youtubes_names()
    names = np.load(filenames_parameters.songs_npy_name + '.npy')
    songs = get_songs_from_strings(names)
    songs = songs[:NUM_OF_SAMPLE]
    songs = songs[3:6]
    # songs = songs[10:12]
    for s in songs:
        s.print_me()
        try:
            download_by_song_object(downloaded_songs, s)
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)

    save_metadata(downloaded_songs)


if __name__ == '__main__':
    main()
