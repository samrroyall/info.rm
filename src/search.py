##############
#### TREE ####
#############

class Tree:
    """ String search Tree implementation
    """
    def __init__(self, label, data):
        self.label = label
        self.data = data
        self.children = None

    def has_children(self):
        return self.children is not None

    def has_child(self, key):
        return key in self.children

    def has_data(self):
        return self.data is not None

###############
#### STACK ####
###############

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

#################
#### GLOBALS ####
#################

TREE = Tree("", None)
PLAYER_DICT = None

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

###############
### SEARCH  ###
###############

def get_child_data(tree):
    if tree.has_children():
        STACK = Stack()
        for child in tree.children.values(): 
            STACK.push(child)
        data = []
        while len(STACK.data) > 0:
            current_child = STACK.pop()
            if current_child.has_children():
                for child in current_child.children.values():
                    STACK.push(child)
            else:
                data += current_child.data[1]
        return data
    else:
        return tree.data[1]

def search(search_key):
    current_tree = TREE
    next_label = search_key[0]
    # handle one character searches
    if len(search_key) == 1:
        return get_child_data(current_tree.children.get(next_label))
    while True:
        current_tree = current_tree.children.get(next_label)
        if current_tree is None:
            return []
        if current_tree.has_children():
            for child in current_tree.children.values():
                if child.label == search_key:
                    return get_child_data(child)
                elif search_key.startswith(child.label):
                    next_label = child.label
        else:
            return current_tree.data[1]

