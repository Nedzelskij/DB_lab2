import math
import numpy as np
import sys

class Node:
    def __init__(self, order: int, values: list[str] = [], keys: list[int] = [], childs: list['Node'] = []):
        self.order = order
        self.values = values
        self.keys = keys
        self.childs = childs
        self.nextKey = None
        self.parent = None
        self.is_leaf = False

    def insert_at_leaf(self, value: str, key: int) -> None:
        if (self.keys):
            temp_keys = self.keys
            for i in range(len(temp_keys)):
                if (key <= temp_keys[i]):
                    self.keys = self.keys[:i] + [key] + self.keys[i:]
                    self.values = self.values[:i] + [value] + self.values[i:]
                    break
                elif (i + 1 == len(temp_keys)):
                    self.keys.append(key)
                    self.values.append(value)
                    break
        else:
            self.keys = [key]
            self.values = [value]
        return
    

class BplusTree:
    def __init__(self, order: int, depth: int):
        self.root = Node(order + 1)
        self.root.is_leaf = True
        self.depth = depth

    def _tab(self, n: int) -> str:
        return n * '\t'
    
    def _calculate_hash(self, value: str) -> int:
        value = value.lower()
        chars_hash = np.array([ord(char) * float(sys.maxsize) for char in value])
    
        for i in range(1, len(chars_hash)):
            chars_hash[i] = chars_hash[i] / (i * 100017 + 98700)

        final_hash = np.sum(chars_hash)
        return int(final_hash)
    
    def _find_depth(self) -> int:
        current_level = [self.root]
        depth = 0
        while current_level:
            next_level = []
            for node in current_level:
                next_level.extend(node.childs)
            if next_level:
                depth += 1
            current_level = next_level
        return depth

    
    def _search_least(self) -> 'Node':
        current_node = self.root
        while(current_node.is_leaf == False):
            current_node = current_node.childs[0]
        return current_node
    
    def search(self, key: int) -> 'Node':
        current_node = self.root
        while(current_node.is_leaf == False):
            temp_keys = current_node.keys
            for i in range(len(temp_keys)):
                if (key == temp_keys[i]):
                    current_node = current_node.childs[i + 1]
                    break
                elif (key < temp_keys[i]):
                    current_node = current_node.childs[i]
                    break
                elif (i + 1 == len(current_node.keys)):
                    current_node = current_node.childs[i + 1]
                    break
        return current_node

    def insert(self, value: str) -> None:
        key = self._calculate_hash(value)
        old_leaf = self.search(key)
        old_leaf.insert_at_leaf(value, key)

        if (len(old_leaf.keys) == old_leaf.order):
            new_leaf = Node(old_leaf.order)
            new_leaf.is_leaf = True
            new_leaf.parent = old_leaf.parent
            mid = int(math.ceil(old_leaf.order / 2) - 1) - 1
            new_leaf.values = old_leaf.values[mid + 1:]
            new_leaf.keys = old_leaf.keys[mid + 1:]
            new_leaf.nextKey = old_leaf.nextKey
            old_leaf.values = old_leaf.values[:mid + 1]
            old_leaf.keys = old_leaf.keys[:mid + 1]
            old_leaf.nextKey = new_leaf
            self.insert_in_parent(old_leaf, new_leaf.keys[0], new_leaf)

        if self._find_depth() > 3:
            self.delete(key=key)

    def find(self, value: str = '', key: int = None) -> str:
        if key is None:
            key = self._calculate_hash(value) 

        leaf = self.search(key)
        for i, item in enumerate(leaf.keys):
            if item == key:
                return leaf.values[i]
        return 'No value found'
    
    def search_all_more(self, value: str = '', key: int = None) -> list[str]:
        if key is None:
            key = self._calculate_hash(value)
            
        current_leaf = self.search(key)

        results = []
        while current_leaf:
            for i, k in enumerate(current_leaf.keys):
                if k >= key:
                    results.append(current_leaf.values[i])
            current_leaf = current_leaf.nextKey
        return results
    
    def search_all_less(self, value: str = '', key: int = None) -> list[str]:
        if key is None:
            key = self._calculate_hash(value)

        current_leaf = self._search_least()
        
        results = []
        while current_leaf.keys[0] <= key:
            for i, k in enumerate(current_leaf.keys):
                if k <= key:
                    results.append(current_leaf.values[i])
            current_leaf = current_leaf.nextKey
        return results

    def insert_in_parent(self, node: 'Node', key: int, node_dash: 'Node') -> None:
        if (self.root == node):
            root_node = Node(node.order)
            root_node.keys = [key]
            root_node.childs = [node, node_dash]
            self.root = root_node
            node.parent = root_node
            node_dash.parent = root_node
            return

        parent_node = node.parent
        temp_childs = parent_node.childs
        for i in range(len(temp_childs)):
            if (temp_childs[i] == node):
                parent_node.keys = parent_node.keys[:i] + \
                    [key] + parent_node.keys[i:]
                parent_node.childs = parent_node.childs[:i +
                                                  1] + [node_dash] + parent_node.childs[i + 1:]
                if (len(parent_node.childs) > parent_node.order):
                    new_parent_node = Node(parent_node.order)
                    new_parent_node.parent = parent_node.parent
                    mid = int(math.ceil(parent_node.order / 2)) - 1
                    new_parent_node.keys = parent_node.keys[mid + 1:]
                    new_parent_node.childs = parent_node.childs[mid + 1:]
                    mid_key = parent_node.keys[mid]
                    if (mid == 0):
                        parent_node.keys = parent_node.keys[:mid + 1]
                    else:
                        parent_node.keys = parent_node.keys[:mid]
                    parent_node.childs = parent_node.childs[:mid + 1]
                    for child in parent_node.childs:
                        child.parent = parent_node
                    for child in new_parent_node.childs:
                        child.parent = new_parent_node
                    self.insert_in_parent(parent_node, mid_key, new_parent_node)

    def delete(self, value: str = '', key: int = None) -> None:
        if key is None:
            key = self._calculate_hash(value)

        leaf = self.search(key)

        for i, item in enumerate(leaf.keys):
            if item == key:
                if leaf == self.root:
                    leaf.values.pop(i)
                    leaf.keys.pop(i)
                else:
                    leaf.values.pop(i)
                    leaf.keys.pop(i)
                    self.delete_entry(leaf)
                break                 

    def delete_entry(self, upper_node: Node, key: int = None, lower_node: Node = None) -> None:

        if not upper_node.is_leaf:
            for i, child in enumerate(upper_node.childs):
                if child == lower_node:
                    upper_node.childs.pop(i)
                    break
            for i, child in enumerate(upper_node.keys):
                if child == key:
                    upper_node.keys.pop(i)
                    break

        if self.root == upper_node and len(upper_node.keys) == 1:
            return
        elif self.root == upper_node and len(upper_node.childs) == 1:
            self.root = upper_node.childs[0]
            upper_node.childs[0].parent = None
            del upper_node
            return
        elif (len(upper_node.childs) < int(math.ceil(upper_node.order / 2)) and upper_node.is_leaf == False) or \
             (len(upper_node.keys) < int(math.ceil((upper_node.order - 1) / 2)) and upper_node.is_leaf == True):
            
            is_predecessor = 0
            parent_node = upper_node.parent
            previous_node = next_node = -1
            previous_key = post_key = -1
            for i, child in enumerate(parent_node.childs):
                if child == upper_node:
                    if i > 0:
                        previous_node = parent_node.childs[i - 1]
                        previous_key = parent_node.keys[i - 1]

                    if i < len(parent_node.childs) - 1:
                        next_node = parent_node.childs[i + 1]
                        post_key = parent_node.keys[i]

            if previous_node == -1:
                changed_node = next_node
                key_ = post_key
            else:
                is_predecessor = 1
                changed_node = previous_node
                key_ = previous_key

            if is_predecessor == 1:
                if len(upper_node.keys) + len(changed_node.keys) >= upper_node.order - 1:
                    if not upper_node.is_leaf:
                        located_node = changed_node.childs.pop(-1)
                        located_key = changed_node.keys.pop(-1)
                        upper_node.childs = [located_node] + upper_node.childs
                        upper_node.keys = [key_] + upper_node.keys
                        parent_node = upper_node.parent
                        for i, item in enumerate(parent_node.keys):
                            if item == key_:
                                parent_node.keys[i] = located_key
                                break
                    else:
                        located_key = changed_node.keys.pop(-1)
                        located_value = changed_node.values.pop(-1)
                        upper_node.keys = [located_key] + upper_node.keys
                        upper_node.values = [located_value] + upper_node.values
                        parent_node = upper_node.parent
                        for i, item in enumerate(parent_node.keys):
                            if item == key_:
                                parent_node.keys[i] = located_key
                                break 
                    
                    if not changed_node.is_leaf:
                        for child in changed_node.childs:
                            child.parent = changed_node
                    if not upper_node.is_leaf:
                        for child in upper_node.childs:
                            child.parent = upper_node
                    if not parent_node.is_leaf:
                        for child in parent_node.childs:
                            child.parent = parent_node
                elif len(upper_node.keys) + len(changed_node.keys) < upper_node.order and upper_node.is_leaf == True:
                    changed_node.childs += upper_node.childs
                    changed_node.nextKey = upper_node.nextKey
                    changed_node.keys += upper_node.keys
                    changed_node.values += upper_node.values

                    self.delete_entry(upper_node.parent, key_, upper_node)
                    del upper_node
                else:
                    changed_node.childs += upper_node.childs
                    changed_node.keys.append(key_)
                    changed_node.keys += upper_node.keys
                    changed_node.values += upper_node.values

                    for child in changed_node.childs:
                        child.parent = changed_node

                    self.delete_entry(upper_node.parent, key_, upper_node)
                    del upper_node
            else:
                if len(upper_node.keys) + len(changed_node.keys) >= upper_node.order - 1:
                    if not upper_node.is_leaf:
                        located_node = changed_node.childs.pop(0)
                        located_key = changed_node.keys.pop(0)
                        upper_node.childs = upper_node.childs + [located_node]
                        upper_node.keys = upper_node.keys + [key_]
                        parent_node = upper_node.parent
                        for i, item in enumerate(parent_node.keys):
                            if item == key_:
                                parent_node.keys[i] = located_key
                                break
                    else:
                        located_key = changed_node.keys.pop(0)
                        located_value = changed_node.values.pop(0)
                        upper_node.keys = upper_node.keys + [located_key]
                        upper_node.values = upper_node.values + [located_value]
                        parent_node = upper_node.parent
                        for i, item in enumerate(parent_node.keys):
                            if item == key_:
                                parent_node.keys[i] = changed_node.keys[0]
                                break
                        
                    if not changed_node.is_leaf:
                        for child in changed_node.childs:
                            child.parent = changed_node
                    if not upper_node.is_leaf:
                        for child in upper_node.childs:
                            child.parent = upper_node
                    if not parent_node.is_leaf:
                        for child in parent_node.childs:
                            child.parent = parent_node
                elif len(upper_node.keys) + len(changed_node.keys) < upper_node.order and upper_node.is_leaf == True:
                    upper_node, changed_node = changed_node, upper_node
                    changed_node.childs += upper_node.childs
                    changed_node.nextKey = upper_node.nextKey
                    changed_node.keys += upper_node.keys
                    changed_node.values += upper_node.values

                    self.delete_entry(upper_node.parent, key_, upper_node)
                    del upper_node
                else:
                    upper_node, changed_node = changed_node, upper_node
                    changed_node.childs += upper_node.childs
                    changed_node.keys.append(key_)
                    changed_node.keys += upper_node.keys
                    changed_node.values += upper_node.values

                    for child in changed_node.childs:
                        child.parent = changed_node

                    self.delete_entry(upper_node.parent, key_, upper_node)
                    del upper_node

    def print_b_plus_tree(self, tree: Node, level: int = 0) -> None:
        lst = [tree]

        while (len(lst) != 0):
            x = lst.pop(0)
            if (x.is_leaf == False):
                print(f'{self._tab(level)}{x.keys}')
                level += 1
                for _, child in enumerate(x.childs):
                    self.print_b_plus_tree(child, level)
            else:
                print(f'{self._tab(level)}{x.keys}{x.values}')



names = ['Alice', 'Bob', 'Claire', 'David', 'Emily', 'Frank', 'Grace', 'Henry', 'Isabella', 
         'Jack', 'Kate', 'Liam', 'Mia', 'Noah', 'Olivia', 'Peter', 'Quinn', 'Rachel', 'Sam', 
         'Taylor', 'Uma', 'Victor', 'Wendy', 'Xavier', 'Yvonne', 'Zachary']

if __name__ == '__main__':
    record_len = 4
    depth = 3
    b_plus_tree = BplusTree(record_len, depth)

    for name in names:
        b_plus_tree.insert(name)

    for name in []:
        b_plus_tree.delete(value=name)
        
    # print(b_plus_tree.search_all_less(value='Isabella'))
    # print(b_plus_tree.search_all_more(value='Isabella'))

    # print(b_plus_tree.find(value='Uma'))
    # print(b_plus_tree.find(value='Umot'))

    # b_plus_tree.print_b_plus_tree(tree=b_plus_tree.root)
        