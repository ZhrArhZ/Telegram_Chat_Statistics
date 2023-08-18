# Telegram Chat Statistics

Utilize a Telegram group chat as a JSON data source, extract its plain text content, and generate a word cloud.

## How to Run

In the main repo directory, run the following code to add 'src' to your 'PYTHONPATH':

   ```bash
   export PYTHONPATH=${PWD}
   ```
Then Run:

  ```bash
  python src/statistics/stats.py
  ```

to generate a wordcloud of json data in 'DATA_DIR'  
