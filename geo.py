# -*- coding: utf-8 -*-
#Все затеял Merron
from telebot import types
import telebot
import requests
import threading
import time
from datetime import datetime

from urllib.parse import urlparse
import urllib
import tldextract
import re



instagram_token = ''#тут апитокен инстаграма
bot = telebot.TeleBot('')# а тут не скажу что

DEFAULT_RADIUS = 100

def geo(latitude, longitude, radius=DEFAULT_RADIUS):
    global instagram_token
    url_instagram = 'https://api.instagram.com/v1/media/search?lat={}&lng={}&distance={}&access_token={}'\
        .format(latitude, longitude, radius, instagram_token)
    url_vk = 'https://api.vk.com/method/photos.search?lat={}&long={}&sort=0&radius={}'\
        .format(latitude, longitude, radius)
    result_instagram = requests.get(url_instagram).json()['data']
    result_vk = requests.get(url_vk).json()['response'][1:]
    instagram = []
    for ig in result_instagram:
        link = ig['link']
        date = datetime.fromtimestamp(int(ig['created_time']))
        location = ig['location']['name'] if ig['location']['name'] else 'Unknown place'
        message = "{}: {} ({})".format(date, link, location)
        instagram.append(message)
    print('inst'+str(instagram))
    vk = []
    for vkcom in result_vk:
        link = 'https://m.vk.com/photo{}_{}'.format(vkcom['owner_id'], vkcom['pid'])
        date = datetime.fromtimestamp(int(vkcom['created']))
        message = "{}: {}".format(date,link)
        vk.append(message)
    print('vk'+str(vk))
    return instagram, vk

def GetRadius(z):
    z = float(z) #FIREBALL
    return {
            z < 13:	1000,#F
        	z == 13:	800,#I
        	z == 14:	400,#R
        	z == 15:	 200,#E
        	z == 16:	100,#B
        	z == 17:	50,#A
        	z > 17:	30#L
    }[True]#L

def isfloat(value): # лол
  try:
    float(value)
    return True
  except ValueError:
    return False

def GetCoord(message):# Не бейте меня
    try:
        if urlparse(message):
            o = urlparse(message)
            if tldextract.extract(message).domain == "google":
                try:
                    if urllib.parse.parse_qs(o.query)['q']:
                        coord = urllib.parse.parse_qs(o.query)
                        x = coord['q'][0].split(',')[0]
                        y = coord['q'][0].split(',')[1]
                        return x, y, DEFAULT_RADIUS
                except:
                    pass

                if message[-1] != 'z':
                    coord = re.search(r'@.+(z)(/|\?)', message).group(0)[1:-2].split(',')
                else:
                    coord = re.search(r'@.+(z)($)', message).group(0)[1:-1].split(',')

                x = coord[0]
                y = coord[1]
                z = coord[2]
                return x, y, z
#я не погромист, прастити
            if tldextract.extract(message).domain == "yandex":
                coord = urllib.parse.parse_qs(o.query)
                try:
                    if coord['ll']:
                        y = coord['ll'][0].split(',')[0]
                        x = coord['ll'][0].split(',')[1]
                        if coord['z'][0]:
                            z = coord['z'][0]
                        else:
                            z = DEFAULT_RADIUS
                except:
                    pass
                    if coord['sll']:
                        y = coord['sll'][0].split(',')[0]
                        x = coord['sll'][0].split(',')[1]
                        z = DEFAULT_RADIUS
                    return x, y, z


        float(message.split(' ')[0])
        float(message.split(' ')[1])
        return message.split(' ')[0], message.split(' ')[1], DEFAULT_RADIUS
    except:
        return False, False, False

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Share the location or send a link to google/yandex map')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def location(message):

    x, y, z=GetCoord(message.text)

    if x and y:

        try:
            inst_result, vk_result = geo(x,y,z)
            if (inst_result):
                inst_message=('Instaram (Radius '+str(z)+'):\n'+'\n\n'.join(inst_result))[:4000]
                if len(inst_message)==4000:
                    bot.send_message(message.chat.id, inst_message[:inst_message.rfind('\n\n')], disable_web_page_preview=True)
                else:
                    bot.send_message(message.chat.id, inst_message,
                                     disable_web_page_preview=True)
            if (vk_result):
                vk_message=('VK (Radius '+str(z)+'):\n'+'\n\n'.join(vk_result))[:4000]
                if len(vk_message)==4000:
                    bot.send_message(message.chat.id, vk_message[:vk_message.rfind('\n\n')], disable_web_page_preview=True)
                else:
                    bot.send_message(message.chat.id, vk_message,
                                     disable_web_page_preview=True)
            if not vk_result and not inst_result:
                bot.send_message(message.chat.id, '¯\_(ツ)_/¯', disable_web_page_preview=True)
        except:
            bot.send_message(message.chat.id, 'Error?', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, 'Yo! For example:\n\nhttps://www.google.ru/maps/@55.7546777,37.6214901,21z/\n\nhttps://yandex.ru/maps/213/moscow/?ll=37.588091%2C55.734155&spn=90.175781%2C37.265672&z=19\n\n52.7327785 41.4293857\n\nOr share your location', disable_web_page_preview=True)





@bot.message_handler(content_types=['location'])
def location(message):
    longitude = message.location.longitude
    latitude = message.location.latitude
    inst_result, vk_result = geo(latitude, longitude)

    if (inst_result):
        inst_message=('Instaram (Radius 100):\n'+'\n\n'.join(inst_result))[:4000]
        bot.send_message(message.chat.id, inst_message[:inst_message.rfind('\n\n')], disable_web_page_preview=True)
    if (vk_result):
        vk_message=('VK (Radius 100):\n'+'\n\n'.join(vk_result))[:4000]
        bot.send_message(message.chat.id, vk_message[:vk_message.rfind('\n\n')], disable_web_page_preview=True)


@bot.message_handler(commands=['me']) #Запрос локации
def request_location(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Send location", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Share location", reply_markup=keyboard)


if __name__ == '__main__':
    while 1:
        try:# апи телеги пятисотит - скриптос работает, не трожж
            bot.polling(none_stop=True)
        except BaseException as e:
           print ('Error'+str(e))
           time.sleep(3)