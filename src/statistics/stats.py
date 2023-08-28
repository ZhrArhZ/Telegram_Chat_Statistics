import re
from collections import Counter
from pathlib import Path
from typing import Union

import arabic_reshaper
import emoji
from bidi.algorithm import get_display
from hazm import Normalizer, word_tokenize, stopwords_list
from wordcloud import WordCloud

from src.Data import DATA_DIR, verbal_stopwords
from src.utils.io import read_json, write_file
from loguru import logger


json_file = input('Please enter the name of your json file like result.json: ')

PATH = DATA_DIR / f'{json_file}'
FONT_PATH = DATA_DIR / 'B-NAZANIN.TTF'


class ChatStatistics:
    def __init__(self, Chat_file: Union[str, Path]):

        """
        Generate chat statistics from a Telegram chat json file.
        :param chat_file: Path to Telegram export json file.
        """
        logger.info(f"Loading chat data from {Chat_file}")
        self.chat_data = read_json(PATH)

        # load persian stopwords
        stopwords = stopwords_list()
        stopwords.extend(verbal_stopwords.extra_stopwords)
        self.stopwords = set(stopwords)

        # Extract all kinds of text from the json file
        self.text_content = self.extract_text_content()

    def extract_text_content(self):
        """
        Extract various types of text content from the chat data.
        :return: Dictionary containing different types of text content.
        """
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

        logger.info("extracting texts from chat_data")

        for msg in self.chat_data['messages']:
            for item in msg['text_entities']:

                item_text = re.sub(u'[\u200c\U0001fae3]', ' ', item['text'])

                if item['type'] == 'plain':
                    text_content['plain text'] += f"  {item_text}"

                elif item['type'] in ['text_link', 'link', 'email', 'code',
                                      'italic', 'mention', 'hashtag', 'bold']:
                    text_content[item['type']].append(item_text)
      
        return text_content

    def clean_plain_text(self):

        """
        removing emojies, punctuations and stopwords from text
        then tokenize and reshape it, makeing a filtered text.

        Returns:
            reshaped_text: a clean ready string for making wordcloud
        """

        logger.info("Cleaning, normalizing, and reshaping chat data")

        clean_txt = emoji.replace_emoji(self.text_content['plain text'],
                                        replace='')
        normalizer = Normalizer()
        normalized_text = normalizer.normalize(clean_txt)
        words = word_tokenize(normalized_text)
        filtered_words = list(filter(lambda word: word not in self.stopwords,
                                     words))
        filtered_text = ' '.join(filtered_words)
        reshaped_text = arabic_reshaper.reshape(filtered_text)

        return reshaped_text

    def generate_wordcloud_from_plainText(self, output_dir=DATA_DIR):

        """
        Generate a wordcloud from the chat data.
        :param output_dir: path to output directory for wordcloud image
        """

        bidi_text = get_display(self.clean_plain_text())
        logger.info("Generating WordCloud")
        wordcloud = WordCloud(str(FONT_PATH)).generate(bidi_text)
        logger.info(f'saving wordcloud to {output_dir}')
        wordcloud.to_file(str(output_dir.parent/'result_Data'/'wordcloud.png'))

    def show_emails(self):

        """
        Creates a text file to store and gather all emails from a list of
        emails.
        """
        write_file('Emails.txt', self.text_content['email'])
        logger.info("Emails written to Emails.txt")

    def show_hashtags(self):

        """
        Creates a text file to store and gather all hashtags from a list of
        hashtags.
        """

        write_file('Hashtags.txt', self.text_content['hashtag'])
        logger.info("Hashtags written to Hashtags.txt")

    def show_links(self):

        """
        Creates a text file to gather and store all Link addresses from a lsit
        of links.
        """

        write_file('Links.txt', self.text_content['link'])
        logger.info("Links written to Links.txt")

    def show_ids(self):

        """
        Creates a text file to store and gather all IDs from a list of
        IDs.
        """

        write_file('IDs.txt', self.text_content['mention'])
        logger.info("IDs written to ids.txt")


class UserSatat(ChatStatistics):

    def __init__(self, Chat_file: Union[str, Path]):
        """
        A class to generate user statistics from a Telegram chat json file.
        Inherits functionality from ChatStatistics.
        :param Chat_file: Path to the Telegram export json file.
        """
        super().__init__(Chat_file)

        questioners = {}
        users = {}

        for msg in self.chat_data['messages']:
            self.map_ids_to_users(msg, users)

            self.Detect_Questions(msg, questioners)

        logger.info("User names and IDs extracted.")
        self.users = users
        logger.info("Top questioners extracted.")
        self.top_questioners = self.top_n_questioners(questioners)
        logger.info("Top repliers to questions extracted.")
        self.top_repliers_to_Qs = self.top_n_repliers_to_Qs(self.chat_data,
                                                            questioners)
        logger.info("Top repliers extracted.")
        self.top_repliers = self.top_n_repliers(self.chat_data)
       
    def map_ids_to_users(self, msg, users):
     
        """
        Maps user IDs to their names.
        :param msg: Message data.
        :param users: Dictionary to store user IDs and names.
        """
        if 'from' in msg:
            users[msg['id']] = msg['from']

        elif 'actor' in msg:
            users[msg['id']] = msg['actor']

    def Detect_Questions(self, msg, questioners):
   
        """
        Checks if a message has a question.
        :param sent: Message to check.
        :return: True if the message contains a question, False otherwise.
        """
        for item in msg['text_entities']:
            if item['type'] == 'plain':
                sent = re.sub(u'[\u200c\U0001fae3]', ' ', item['text'])

                if '?' in sent or '؟' in sent:
                    questioners[msg['id']] = msg['from']

    def top_n_questioners(self, questioners, top_n=10):

        """
        Get the top N questioners based on the number of questions asked.

        :param questioners: Dictionary of questioners' IDs and names.
        :param top_n: Number of top questioners to retrieve.
        :return: Dictionary containing the top N questioners and their 
        question counts.
        """
        return dict(Counter(list(questioners.values())).most_common(top_n))

    def top_n_repliers(self, messages, top_n=10):

        """
        Get the top N users who have replied to any messages.

        :param messages: Chat message data.
        :param is_question_id: Dictionary indicating if a message ID is a
          question ID.
        :param top_n: Number of top repliers to retrieve.
        :return: Dictionary containing the top N repliers and their reply
          counts.
        """
     
        repliers = []

        for msg in messages['messages']:
            if 'reply_to_message_id' in msg:
                repliers.append(msg['from'])
           
        return dict(Counter(repliers).most_common(top_n))

    def top_n_repliers_to_Qs(self, messages, is_question_id, top_n=10):

        """
        Get the top N users who replied to questions.

        :param messages: Chat message data.
        :param is_question_id: Dictionary indicating if a message ID is a
        question ID.
        :param top_n: Number of top repliers to retrieve.
        :return: Dictionary containing the top N repliers to questions and
        their reply counts.
        """

        repliers_to_Qs = []

        for msg in messages['messages']:
            if 'reply_to_message_id' in msg:
                if is_question_id.get(msg['reply_to_message_id'], False):
                    repliers_to_Qs.append(msg['from'])
             
        return dict(Counter(repliers_to_Qs).most_common(top_n))


if __name__ == '__main__':
    ch1 = ChatStatistics(PATH)
    ch1.generate_wordcloud_from_plainText()
    ch1.show_hashtags()
    ch1.show_ids()
    ch1.show_links()
    ch1.show_emails()

    ch2 = UserSatat(PATH)
    print(f"top 10 questioners: {ch2.top_questioners}")
    print(f"top 10 repliers to questions: {ch2.top_repliers_to_Qs}")
    print(f"top 10 repliers in general: {ch2.top_repliers}")

