# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import threading
from os import path, remove

class SdamGIA:
    def __init__(self):
        self._BASE_DOMAIN = 'sdamgia.ru'
        self._SUBJECT_BASE_URL = {
            'inf': f'https://inf-oge.{self._BASE_DOMAIN}',
        }

    def get_problem_by_id(self, subject, id, img=None, path_to_img=None, path_to_html='', grabzit_auth=None):
        """
        Получение информации о задаче по ее идентификатору

        :param subject: Наименование предмета
        :type subject: str

        :param id: Идентификатор задачи
        :type subject: str

        :param img: Принимает одно из двух значений: pyppeteer или grabzit;
                    В результате будет использована одна из библиотек для генерации изображения с задачей.
                    Если не передавать этот аргумент, изображение генерироваться не будет
        :type img: str

        :param path_to_img: Путь до изображения, куда сохранить сохранить задание.
        :type path_to_img: str

        :param path_to_html: Можно указать директорию, куда будут сохраняться временные html-файлы заданий при использовании pyppeteer
        :type path_to_html: str

        :param grabzit_auth: При использовании GrabzIT укажите данные для аутентификации: {"AppKey":"...", "AppSecret":"..."}
        :type grabzit_auth: dict
        """

        doujin_page = requests.get(
            f'{self._SUBJECT_BASE_URL[subject]}/problem?id={id}')
        soup = BeautifulSoup(doujin_page.content, 'html.parser')

        probBlock = soup.find('div', {'class': 'prob_maindiv'})
        if probBlock is None:
            return Noneqaz1wcb
        for i in probBlock.find_all('img'):
            if not 'sdamgia.ru' in i['src']:
                i['src'] = self._SUBJECT_BASE_URL[subject] + i['src']


        URL = f'{self._SUBJECT_BASE_URL[subject]}/problem?id={id}'
        TOPIC_ID = ' '.join(probBlock.find(
            'span', {'class': 'prob_nums'}).text.split()[1:][:-2])
        ID = id

        CONDITION, SOLUTION, ANSWER, ANALOGS = {}, {}, '', []

        try:
            CONDITION = {'text': probBlock.find_all('div', {'class': 'pbody'})[0].text,
                         'images': [i['src'] for i in probBlock.find_all('div', {'class': 'pbody'})[0].find_all('img')]
                         }
        except IndexError:
            pass

        try:
            SOLUTION = {'text': probBlock.find_all('div', {'class': 'pbody'})[1].text,
                        'images': [i['src'] for i in probBlock.find_all('div', {'class': 'pbody'})[1].find_all('img')]
                        }
        except IndexError:
            pass
        except AttributeError:
            pass

        try:
            ANSWER = probBlock.find(
                'div', {'class': 'answer'}).text.replace('Ответ: ', '')
        except IndexError:
            pass
        except AttributeError:
            pass

        try:
            ANALOGS = [i.text for i in probBlock.find(
                'div', {'class': 'minor'}).find_all('a')]
            if 'Все' in ANALOGS:
                ANALOGS.remove('Все')
        except IndexError:
            pass
        except AttributeError:
            pass


        if not img is None:

            for i in probBlock.find_all('div', {'class': 'minor'}):
                i.decompose()
            probBlock.find_all('div')[-1].decompose()


            if img == 'pyppeteer':
                import asyncio
                from pyppeteer import launch
                open(f'{path_to_html}{id}.html', 'w').write(str(probBlock))
                async def main():
                    browser = await launch()
                    page = await browser.newPage()
                    await page.goto('file:' + path.abspath(f'{path_to_html}{id}.html'))
                    await page.screenshot({'path': path_to_img, 'fullPage': 'true'})
                    await browser.close()
                asyncio.get_event_loop().run_until_complete(main())
                remove(path.abspath(f'{path_to_html}{id}.html'))
            elif img == 'grabzit':
                from GrabzIt import GrabzItClient, GrabzItImageOptions
                grabzIt = GrabzItClient.GrabzItClient(grabzit_auth['AppKey'], grabzit_auth['AppSecret'])
                options = GrabzItImageOptions.GrabzItImageOptions()
                options.browserWidth = 800
                options.browserHeight = -1
                grabzIt.HTMLToImage(str(probBlock), options=options)
                grabzIt.SaveTo(path_to_img)

        return {'id': ID, 'topic': TOPIC_ID, 'condition': CONDITION, 'solution': SOLUTION, 'answer': ANSWER,
                'analogs': ANALOGS, 'url': URL}

    def get_category_by_id(self, subject, categoryid, page=1):
        """
        Получение списка задач, включенных в категорию

        :param subject: Наименование предмета
        :type subject: str

        :param categoryid: Идентификатор категории
        :type categoryid: str

        :param page: Номер страницы поиска
        :type page: int
        """
        tasks = []
        for page in range(1, 10):
            doujin_page = requests.get(
                f'{self._SUBJECT_BASE_URL[subject]}/test?&filter=all&theme={categoryid}&page={page}')
            if doujin_page.status_code != 200:
                break
            soup = BeautifulSoup(doujin_page.content, 'html.parser')
            for i in soup.find_all('span', {'class': 'prob_nums'}):
                tasks.append(i.find('a').text)
        return tasks

    def get_catalog(self, subject):
        """
        Получение каталога заданий для определенного предмета

        :param subject: Наименование предмета
        :type subject: str
        """

        doujin_page = requests.get(
            f'{self._SUBJECT_BASE_URL[subject]}/prob_catalog')
        soup = BeautifulSoup(doujin_page.content, 'html.parser')
        catalog = []
        CATALOG = []

        for i in soup.find_all('div', {'class': 'cat_category'}):
            try:
                i['data-id']
                catalog.append(i)
            except:
                continue

        for topic in catalog[:12]:
            TOPIC_NAME = topic.find(
                'a', {'class': 'cat_name'}).text.split('. ')[1]
            TOPIC_ID = topic['data-id']

            CATALOG.append(
                dict(
                    topic_id=TOPIC_ID,
                    topic_name=TOPIC_NAME
                )
            )

        return CATALOG

if __name__ == '__main__':
    sdamgia = SdamGIA()
    test = sdamgia.get_problem_by_id('math', '505452')
    print(test)
