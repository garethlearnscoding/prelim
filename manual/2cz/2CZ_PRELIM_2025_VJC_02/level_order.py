def level_order(self):
    '''
    print tree from root
    print out all the nodes of the same level in a row 
    '''
    self._level_order(self.root)
    
def _level_order(self, node_list):
    '''
    Helper function for internal use
    print tree from node list
    '''
    # convert node_list to a list if it is not
    if not isinstance(node_list, list):
        node_list = [node_list]
    # Stop recursion if the list is empty
    if not node_list:
        return
    # define a list to collect node in next layer
    next_layer = []
    while node_list:
        node = node_list.pop(0) # Remove the first item
        print(node, end = ' ')
        if node.left_ptr:
            next_layer.append(node.left_ptr)
        if node.right_ptr:
            next_layer.append(node.right_ptr)
    print() # print new line after processing a layer
    self._level_order(next_layer)
