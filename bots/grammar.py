import random
import re

class KeyReference:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"<{self.name}>"

class Key:
    def __init__(self, name, results):
        self.name = name
        self.results = results

class Grammar:

    def __init__(self, text):
        self.text = text
        self.keys = {}
        self._parse()

    def _parse(self):

        for line in re.findall(r"\s*<[A-Za-z\-_0-9]+>\s*::=\s*.+?(?=\s*<[A-Za-z\-_0-9]+>\s*::=|$)", self.text, re.DOTALL):
            name, right_side = re.split("\s*::=\s*", line, maxsplit=1)
            name = name.strip().strip("<").strip(">")
            self.keys[name] = Key(name, self._parse_right_side(right_side))

    def _parse_right_side(self, right_side):
        output = []
        current_choice = []

        quote_chars = ["'", '"']
        inside_quote_char = None

        result = ""
        bracket_level = 0

        recording_key = False
        
        for c in right_side:
            
            if c == inside_quote_char and bracket_level == 0:
                current_choice.append(result)
                result = ""
                inside_quote_char = None
            elif c in quote_chars and bracket_level == 0 and inside_quote_char is None:
                inside_quote_char = c
            elif inside_quote_char is not None and bracket_level == 0:
                result += c
            
            elif c == "(":
                bracket_level += 1
            elif c == ")":
                bracket_level -= 1
                if bracket_level == 0:
                    current_choice.append(self._parse_right_side(result))
                    result = ""
            elif bracket_level > 0:
                result += c
            
            elif c == "<":
                recording_key = True
                result = ""
            elif c == ">":
                current_choice.append(KeyReference(result))
                result = ""
                recording_key = False
            elif recording_key:
                result += c

            elif c == "|":
                if result:
                    current_choice.append(result)
                if current_choice:
                    output.append(current_choice)
                current_choice = []
                result = ""

        if current_choice:
            output.append(current_choice)
        return output

    def random_chain(self, start_results):
        output = ""
        
        results = start_results[:]
        
        all_list = True
        for result in results:
            if not isinstance(result, list):
                all_list = False

        if len(results) > 0 and all_list:
            results = random.choice(results)[:]
        
        while len(results) > 0:
            item = results.pop(0)
            
            if isinstance(item, str):
                output += item
            elif isinstance(item, list):
                output += self.random_chain(item)
            elif isinstance(item, KeyReference):
                if item.name in self.keys:
                    output += self.random_chain(self.keys[item.name].results)
                else:
                    output += str(item)

        return output

if __name__ == "__main__":
    g = Grammar("""<test> ::= '"' "hello" '"'""")
    print(g.random_chain(g.keys["test"].results))
