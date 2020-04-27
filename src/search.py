from .query import get_players

##############
#### TREE ####
##############

class Node:
    def __init__(self, name, data):
      self.name = name
      self.data = data
    
    def __repr__(self):
        return f"{self.data[0][0]} ({self.data[0][1]})"


class Tree:
    def __init__(self, label, data):
        self.label = label
        self.data = data
        self.children = None

    ######################
    ### HELPER METHODS ###
    ######################

    def has_children(self):
        return self.children is not None

    def has_child(self, key):
        return key in self.children

    def has_data(self):
        return self.data is not None

    #####################
    ### INSERT METHOD ###
    #####################

    def insert(self, name, data):
        key_string = name[:len(self.label)+1]
        if self.has_children():
            if self.has_child(key_string):
                self.children.get(key_string).insert(name, data)
            else:
                self.children[key_string] = self.__class__(
                                                    label=key_string, 
                                                    data=Node(name=name, data=data)
                                                )
        else:
            # create pointer to new subtree
            self.children = dict()

            # move current tree data to subtree
            if self.has_data():
                current_value = self.data
                self.data = None
                current_key_string = current_value.name[:len(self.label)+1]
                self.children[current_key_string] = self.__class__(
                                                            label=current_key_string, 
                                                            data=current_value
                                                        )

            # insert new data to subtree
            if self.has_child(key_string):
                self.children.get(key_string).insert(name, data)
            else:
                self.children[key_string] = self.__class__(
                                                label=key_string, 
                                                data=Node(name=name, data=data)
                                            )
    ######################
    ### SEARCH METHODS ###
    ######################

    def get_child_data(self):
        if self.has_children():
            result = []
            for child in self.children.values():
                result += child.get_child_data()
            return result
        else:
            return [self.data.data]

    def search(self, key_string):
        if key_string == self.label:
            if self.has_children():
                return self.get_child_data()
            else:
                return [self.data.data]
        elif key_string.startswith(self.label):
            sub_key_string = key_string[:len(self.label)+1]
            if self.has_children():
                if self.has_child(sub_key_string):
                    return self.children.get(sub_key_string).search(key_string)
                else:
                    return []
            else:
                return [self.data.data]
        else:
            return []

########################
### PUBLIC FUNCTIONS ###
########################

class Stack:
    def __init__(self):
        self.data = []

    def push(self, value):
        self.data = [value] + self.data

    def pop(self):
        value = self.data[0]
        self.data = self.data[1:]
        return value

TREE = Tree("", None)

###############
### DISPLAY ###
###############

def print_tree(tree, level):
    padding = ".."*level
    print(f"{padding}label: {tree.label}")
    print(f"{padding}data: {tree.data}")
    if tree.has_children():
        print(f"{padding}children:")
    else:
        print(f"{padding}children: NULL")

def print_children(STACK, tree):
    level = 0
    print_tree(tree, level)
    if tree.has_children():
        level = 1
        STACK.data = [(child, level) for child in tree.children.values()]
    else:
        return
    while len(STACK.data) > 0:
        current_tree, level = STACK.pop()
        print_tree(current_tree, level)
        if current_tree.has_children():
            for child in current_tree.children.values():
                STACK.push( (child, level + 1) )

def display(search_key):
    STACK = Stack()
    STACK.push(TREE)
    while len(STACK.data) > 0:
        current_tree = STACK.pop()
        if current_tree.has_children():
            for child in current_tree.children.values():
                if child.label == search_key:
                    print_children(STACK, child)
                elif search_key.startswith(child.label):
                    STACK.push(child)

###############
### INSERT  ###
###############

def get_prefixes(name):
    split_name = name.split(" ")
    prefix_list = []
    for idx in range(len(split_name)):
        chunk = split_name[idx:]
        prefix_list.append("".join(chunk))
    return prefix_list

def generate_tree():
    player_dict = get_players()
    for name, data in player_dict.items():
        prefixes = get_prefixes(name)
        TREE.insert(prefixes[0], data)
        #for prefix in prefixes:
        #   TREE.insert(prefix, data)

###############
### SEARCH  ###
###############

def search_tree(query):
    search_result = TREE.search(query)
    result = []
    for values in search_result:
        result += values
    result = list(set(result))
    return sorted(result, key=lambda elem: elem[1])

