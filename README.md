# Telegram_Chat_Statistics
Utilize a Telegram group chat as a JSON data source, extract its plain text content, and generate a word cloud.

# How to Run
First, in main repo directory, run the following code to
add 'src' to your 'PYTHONPATH':

"""
export PYTHONPATH=${PWD}
"""
Then Run:
"""
python src/statistics/stats.py
"""
to generate a wordcloud of json data in 'DATA_DIR'