import demoji
import json
import arabic_reshaper
import re

from typing import Union
from pathlib import Path
from src.Data import DATA_DIR, verbal_stopwords
from hazm import word_tokenize, Normalizer, stopwords_list
from wordcloud import WordCloud
from bidi.algorithm import get_display
from loguru import logger


PATH = DATA_DIR / 'result.json'
FONT_PATH = DATA_DIR / 'B-NAZANIN.TTF'


class ChatStatistics:
    """
    Generate chat statistics from a Telegram chat json file
    """
    def __init__(self, Chat_file: Union[str, Path]):

        """
        :param chat_file: path to Telegram export json file
        """

        # load chat data
        logger.info(f"Loading chat data from {Chat_file}")
        with open(Chat_file) as text:
            self.chat_data = json.load(text)

        # load persian stopwords
        stopwords = stopwords_list()
        stopwords.extend(verbal_stopwords.extra_stopwords)
        self.stopwords = stopwords

    def extract_all_text(self):

        """extract all kinds of text from the json file

        Returns:
            text_content: a Dictionary of all text types and their content
        """

        logger.info("extracting texts from chat_data")
        text_content = {'plain text': '',
                        'email': [],
                        'code': [],
                        'italic': [],
                        'mention': [],
                        'hashtag': [],
                        'text_link': [],
                        'bold': [],
                        'link': [],
                        }

        for msg in self.chat_data['messages']:
            for item in msg['text_entities']:
                if item['type'] == 'plain':
                    text_content['plain text'] += f"  {item['text']}"

                elif item['type'] == 'text_link':
                    text_content['text_link'].append(item['href'])

                elif item['type'] == 'hashtag':
                    text_content['hashtag'].append(item['text'])

                elif item['type'] == 'link':
                    text_content['link'].append(item['text'])

                elif item['type'] == 'link':
                    text_content['link'].append(item['text'])

                elif item['type'] == 'email':
                    text_content['email'].append(item['text'])

                elif item['type'] == 'code':
                    text_content['code'].append(item['text'])

                elif item['type'] == 'italic':
                    text_content['italic'].append(item['text'])

                elif item['type'] == 'mention':
                    text_content['mention'].append(item['text'])

                elif item['type'] == 'bold':
                    text_content['bold'].append(item['text'])
        return text_content

    # clean, normalize, reshape for final word cloud
    def clean_plain_text(self):

        """removing emojies, punctuations and stopwords from text
            then tokenize and reshape it, makeing a filtered text.

        Returns:
            reshaped_text: a clean ready string for making wordcloud
        """
        text_content = self.extract_all_text()
        logger.info("chat_data is cleaning,normalizing and reshaping")
        clean_txt = demoji.replace(text_content['plain text'], "")
        normalizer = Normalizer()
        normalized_text = normalizer.normalize(clean_txt)
        words = word_tokenize(normalized_text)

        # self.stopwords contains both persian punctuations and stopwords.
        filtered_words = list(filter(lambda word:
                                     word not in self.stopwords, words))
        filtered_text = ' '.join(filtered_words)

        reshaped = arabic_reshaper.reshape(filtered_text)
        reshaped_text = re.sub(
            u"[\u200b\u200c\u2063\u200f\U0001f979]", "", reshaped)
        return reshaped_text

    def generate_wordcloud_from_plainText(self, output_dir: Union[str, Path]):

        """Generate a wordcloud from the chat data

        :param output_dir: path to output directory for wordcloud image
        """

        bidi_text = get_display(self.clean_plain_text())
        logger.info("Generating WordCloud")
        wordcloud = WordCloud(str(FONT_PATH)).generate(bidi_text)
        logger.info(f'saving wordcloud to {output_dir}')
        wordcloud.to_file(str(Path(output_dir) / 'wordcloud.png'))


if __name__ == '__main__':
    ch1 = ChatStatistics(PATH)
    ch1.generate_wordcloud_from_plainText(DATA_DIR)
