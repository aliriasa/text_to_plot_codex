import pandas as pd
import openai
import textwrap
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('SVG')

openai.api_key = "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"

class Text_to_Plot():
    def __init__(self, q):
        self.df = None #cheese
        self.description = q
        self.query = []
        self.completion = []
    
    def get_csv(self, csv):
        df = pd.read_csv(csv)
        self.df = df
        return self.get_description()

    def get_description(self):
        columns = self.df.columns
        description = "/* Description: The dataframe “df” only contains the following columns: "
        for c in columns:
            description += c + ", "
        description = description[:-2] + "*/ "
        self.description += description
        return description[2:-3]

    def text_to_query(self, text):
        return "/* Prompt: " + text + " */"

    def query_to_prompt(self, query):
        prompt = self.description
        if len(self.query) == 1:
            prompt += self.query[0] + self.completion[0]
        elif len(self.query) == 2:
            prompt += self.query[0] + self.completion[0] + self.query[1] + self.completion[1]
        elif len(self.query) > 2:
            n = len(self.query)
            prompt += self.query[n-3] + self.completion[n-3] + self.query[n-2] + self.completion[n-2] + self.query[n-1] + self.completion[n-1] 
        prompt += query
        return prompt

    def text_to_code(self, text):
        query = self.text_to_query(text)
        prompt = self.query_to_prompt(query)
        response = openai.Completion.create(
            model="code-davinci-002",
            prompt=prompt,
            temperature=0,
            max_tokens=256,
            top_p=1,
            stop = "<STOP>",
            frequency_penalty=0,
            presence_penalty=0,
        )
        code = response['choices'][0]['text']
        return query[2:-2], code
    
    def delete_memory(self):
        self.query = []
        self.completion = []

    def text_to_plot(self, text, path):
        query, code = self.text_to_code(text)
        df = self.df
        plt.clf()
        fig = eval(textwrap.dedent(code))
        fig = fig.figure
        fig.savefig(path, dpi=135, bbox_inches = "tight")
        self.query.append(query)
        self.completion.append(code + "<STOP>")
        return query, code
        