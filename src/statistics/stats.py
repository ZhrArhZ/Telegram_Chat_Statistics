import emoji
import arabic_reshaper

from typing import Union
from pathlib import Path
from src.Data import DATA_DIR, verbal_stopwords
from hazm import word_tokenize, Normalizer, stopwords_list
from wordcloud import WordCloud
from bidi.algorithm import get_display
from loguru import logger
from src.utils.io import read_json, write_file


json_file = input('Please enter the name of your json file like result.json: ')

PATH = DATA_DIR / f'{json_file}'
FONT_PATH = DATA_DIR / 'B-NAZANIN.TTF'


class ChatStatistics:
    """
    Generate chat statistics from a Telegram chat json file.
    """
    def __init__(self, Chat_file: Union[str, Path]):

        """Initializes the ChatStatistics class.

        :param chat_file: Path to Telegram export json file.
        """

        # load chat data
        logger.info(f"Loading chat data from {Chat_file}")
        self.chat_data = read_json(PATH)

        # load persian stopwords
        stopwords = stopwords_list()
        stopwords.extend(verbal_stopwords.extra_stopwords)
        self.stopwords = set(stopwords)

        # extract all kinds of text from the json file
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

                item_type = item['type']
                item_text = item['text']

                if item_type == 'plain':
                    text_content['plain text'] += f"  {item_text}"
                elif item_type in ['text_link', 'link', 'email', 'code',
                                   'italic', 'mention', 'hashtag', 'bold']:
                    text_content[item_type].append(item_text)

        self.text_content = text_content

    # clean, normalize and reshape the plain text content for final word cloud.

    def clean_plain_text(self) -> str:

        """removing emojies, punctuations and stopwords from text
            then tokenize and reshape it, makeing a filtered text.

        Returns:
            reshaped_text: a clean ready string for making wordcloud
        """

        logger.info("Cleaning, normalizing, and reshaping chat data")

        # Remove emojis from plain text
     
        clean_txt = emoji.replace_emoji(self.text_content['plain text'],
                                        replace='')

        # Normalize and tokenize the cleaned text

        normalizer = Normalizer()
        normalized_text = normalizer.normalize(clean_txt)
        words = word_tokenize(normalized_text)

        # remove persian punctuations and stopwords.

        filtered_words = list(filter(lambda word:
                                     word not in self.stopwords, words))

        filtered_text = ' '.join(filtered_words)

        # Reshape the text for proper rendering

        reshaped_text = arabic_reshaper.reshape(filtered_text)

        return reshaped_text

    def generate_wordcloud_from_plainText(self, output_dir=DATA_DIR):

        """Generate a wordcloud from the chat data.

        :param output_dir: path to output directory for wordcloud image
        """

        bidi_text = get_display(self.clean_plain_text())
        logger.info("Generating WordCloud")
        wordcloud = WordCloud(str(FONT_PATH)).generate(bidi_text)
        logger.info(f'saving wordcloud to {output_dir}')
        wordcloud.to_file(str(output_dir.parent/'result_Data'/'wordcloud.png'))

    def show_emails(self):

        """ Creates a text file to store and gather all emails from a list
          of emails.
        """

        write_file('Emails.txt', self.text_content['email'])

        logger.info("Emails written to Emails.txt")

    def show_hashtags(self):

        """ Creates a text file to store and gather all hashtags from a list
          of hashtags.
        """

        write_file('Hashtags.txt', self.text_content['hashtag'])

        logger.info("Hashtags written to Hashtags.txt")

    def show_links(self):

        """Creates a text file to gather and store all Link addresses from
         a lsit of links.
        """

        write_file('Links.txt', self.text_content['link'])

        logger.info("Links written to Links.txt")

    def show_Channel_id(self):

        """Creates a text file to store and gather all channel IDs from a list
          of IDs.
        """

        write_file('Channel_id.txt', self.text_content['mention'])

        logger.info("Channel IDs written to hanel_id.txt")


if __name__ == '__main__':
    ch1 = ChatStatistics(PATH)
    ch1.generate_wordcloud_from_plainText()
    ch1.show_hashtags()
    ch1.show_Channel_id()
    ch1.show_links()
    ch1.show_emails()
