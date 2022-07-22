import random

PER_PATH = r"E:\games\SteamLibrary\steamapps\common\Age2HD\mods\Terrible AI Pack\resources\_common\ai\(TAP) Randobot2.per"

BINARY_OPERATORS = ["or", "and", "nor", "nand"]
UNARY_OPERATORS = ["not"]
CHAT_CHARACTERS = "abcdefghijklmnopqrstuvwxyz "

class Condition:
    
    def __init__(self, text):
        self.text = text

    def to_string(self):
        return f"({self.text})"

class OperatorCondition(Condition):
    
    def __init__(self, text, conditions):
        self.text = text
        self.conditions = conditions

    def to_string(self):
        return "(" + self.text + "\n  " + "  \n".join([x.to_string() for x in self.conditions]) + "\n)"

class Action:
    
    def __init__(self, text):
        self.text = text

    def to_string(self):
        return f"({self.text})"

class Defrule:

    def __init__(self):
        self.conditions = []
        self.actions = []

    def optimize(self):
        if len(self.conditions) == 0:
            self.conditions.append(Condition("true"))
        if len(self.actions) == 0:
            self.actions.append(Condition("do-nothing"))

        if len([x for x in self.conditions if x.text != "true"]) >= 1:
            for condition in self.conditions[::-1]:
                if condition.text == "true":
                    self.conditions.remove(condition)

        if len([x for x in self.actions if x.text != "do-nothing"]) >= 1:
            for action in self.actions[::-1]:
                if action.text == "do-nothing":
                    self.actions.remove(action)

    def to_string(self):
        return "(defrule\n  " + "\n  ".join([x.to_string() for x in self.conditions]) + "\n=>\n  " + "\n  ".join([x.to_string() for x in self.actions]) + "\n)"

class Pool:

    def __init__(self, weightings):
        self.weightings = weightings

    def pick(self):

        total_weight = sum(self.weightings.values())
        random_weight = random.randint(1, int(total_weight * 1000000)) / 1000000

        current_weight = 0
        for (item, weight) in self.weightings.items():
            current_weight += weight
            if current_weight >= random_weight:
                return item

class FromPoolGenerator:

    def __init__(self, pool):
        self.pool = pool

    def generate(self):
        return self.pool.pick()

class ItemGenerator:

    def __init__(self, generators):
        self.generators = generators

    def generate(self):
        return "".join([x.generate() for x in self.generators])

class StaticValueGenerator:

    def __init__(self, value):
        self.value = value

    def generate(self):
        return self.value

class TextGenerator:

    def __init__(self, min_length, max_length):
        self.min_length = min_length
        self.max_length = max_length

    def generate(self):
        output = ""
        for x in range(random.randint(self.min_length, self.max_length + 1)):
            output += random.choice(CHAT_CHARACTERS)
        return output

class NumberGenerator:

    def __init__(self, min_size, max_size):
        self.min_size = min_size
        self.max_size = max_size

    def generate(self):
        return str(random.randint(self.min_size, self.max_size + 1))

class ConditionGenerator:

    def __init__(self, pool, item_generators):
        self.pool = pool
        self.item_generators = item_generators

    def generate(self, max_depth=2):
        if max_depth > 0 and random.randint(1, 5) == 1:
            return OperatorCondition(random.choice(BINARY_OPERATORS), [self.generate(max_depth=max_depth - 1), self.generate(max_depth=max_depth - 1)])
        return Condition(self.item_generators[self.pool.pick()].generate())

class ActionGenerator:

    def __init__(self, pool, item_generators):
        self.pool = pool
        self.item_generators = item_generators

    def generate(self):
        return Action(self.item_generators[self.pool.pick()].generate())

class RuleGenerator:

    def __init__(self, condition_generator, action_generator):
        self.condition_generator = condition_generator
        self.action_generator = action_generator

    def generate(self):
        rule = Defrule()

        number_of_conditions = random.randint(1, 8)
        number_of_actions = random.randint(1, 3)

        number_of_conditions = 1
        number_of_actions = 1

        for x in range(1, number_of_conditions + 1):
            rule.conditions.append(self.condition_generator.generate())

        for x in range(1, number_of_actions + 1):
            rule.actions.append(self.action_generator.generate())

        rule.optimize()
        return rule

def load_pools(path):
    pools = {}

    current_pool = None

    with open(path, "r") as file:

        for line in file.read().split("\n"):
            if line == "":
                continue

            if line.startswith("!") and line.endswith("!"):
                current_pool = line[1:-1]
                if current_pool not in pools:
                    pools[current_pool] = Pool({})

            if "=>" in line:
                name, weight = line.split("=>")
                pools[current_pool].weightings[name.strip()] = float(weight.strip())

    return pools

def load_item_generators(path, pools):
    output = {
        "small-number": NumberGenerator(0, 20),
        "resource-number": NumberGenerator(0, 2000),
        "population-number": NumberGenerator(0, 200),
        "seconds": NumberGenerator(0, 3600),
        "player-number": NumberGenerator(1, 8),
        "short-text": TextGenerator(1, 30),
    }

    for (key, pool) in pools.items():
        output[key] = FromPoolGenerator(pool)

    with open(path, "r") as file:

        for line in file.read().split("\n"):
            if line == "":
                continue

            name, data = [x.strip() for x in line.split("=>")]
            data_parts = [x.strip() for x in data.split("+")]

            generators = []
            for part in data_parts:
                if part.startswith("\"") and part.endswith("\"") or part.startswith("'") and part.endswith("'"):
                    generators.append(StaticValueGenerator(part[1:-1]))
                else:
                    generators.append(output[part])

            output[name] = ItemGenerator(generators)
            
    return output

if __name__ == "__main__":

    pools = load_pools("pool_data.txt")
    
    item_generators = load_item_generators("generators.txt", pools)

    condition_generator = ConditionGenerator(pools["condition"], item_generators)
    action_generator = ActionGenerator(pools["action"], item_generators)

    rule_generator = RuleGenerator(condition_generator, action_generator)

    rules = []
    for x in range(2000):
        rules.append(rule_generator.generate())

    with open(PER_PATH, "w") as file:
        file.write("\n".join([x.to_string() for x in rules]))
        
