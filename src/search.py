from .query import get_players

##############
#### TREE ####
##############

#class Node:
#    def __init__(self, name, data):
#      self.name = name
#      self.data = data
#    
#    def __repr__(self):
#        return f"{self.data[0][0]} ({self.data[0][1]})"


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
    
    def clear(self):
        self.data = []


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
        print(f"{padding}--------------")

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

def create_child(label, prefix, name):
    tree = Tree(
             label=label, 
             data=(prefix, name)
           )
    return tree

def insert(prefix, name):
    # insert to root
    if not TREE.has_children() or not TREE.has_child(prefix[0]):
        if not TREE.has_children():
            TREE.children = dict()
        TREE.children[prefix[0]] = create_child(
                                            prefix[0], 
                                            prefix,
                                            [name]
                                        )
    # insert below root 
    else:
        next_label = prefix[0]
        current_tree = TREE
        while True:
            # get new tree
            current_tree = current_tree.children.get(next_label)

            # ensure that each additional player with the same prefix
            # does not create a new tree
            if next_label == prefix:
                if current_tree.has_children():
                    if current_tree.has_child(prefix):
                        current_data = current_tree.children.get(prefix).data
                        current_data[1].append(name)
                        current_tree.children.get(prefix).data = current_data
                    else:
                        current_tree.children[prefix] = create_child(
                                                                prefix, 
                                                                prefix,
                                                                [name]
                                                            )
                else:
                    current_data = current_tree.data
                    current_data[1].append(name)
                    current_tree.data = current_data
                return

            # insert regularly
            child_label = prefix[:len(current_tree.label) + 1]
            if current_tree.has_children():
                if current_tree.has_child(child_label):
                    # move insertion to new child
                    next_label = child_label
                    continue
            else:
                current_tree.children = dict()
                if current_tree.has_data():
                    # move current value to new child 
                    current_prefix = current_tree.data[0]
                    current_name = current_tree.data[1]
                    current_child_label = current_prefix[:len(current_tree.label) + 1]
                    current_tree.children[current_child_label] = create_child(
                                                                     current_child_label, 
                                                                     current_prefix,
                                                                     current_name
                                                                 )
                    # remove current data
                    current_tree.data = None
                    # deal with new value
                    if current_child_label == child_label:
                        # move insertion to new child
                        next_label = child_label
                        continue
            # insert new child
            current_tree.children[child_label] = create_child(
                                                    child_label, 
                                                    prefix,
                                                    [name]
                                                )
            return

def get_prefixes(name):
    split_name = name.split(" ")
    prefix_list = []
    for idx in range(len(split_name)):
        chunk = split_name[idx:]
        prefix_list.append(" ".join(chunk))
    return prefix_list

def generate_tree():
    player_dict = get_players()
    for name in player_dict.keys():
        prefixes = get_prefixes(name)
        for prefix in prefixes:
            insert(prefix, name)

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

