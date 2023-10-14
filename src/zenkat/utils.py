from typing import Callable

def node_tree_dft(root, child_property: str, do_fn: Callable[[object],bool]):
    '''
    Perform a depth first traversal of a node tree of objects and call do_fn at each node. If do_fn returns False, don't continue to navigate that branch of the tree.
    '''
    # perform a Depth First Traversal of a node tree and do something at each node
    outcome = do_fn(root)
    if not outcome:
        return False
    children = root.__dict__[child_property]
    for child in children:
        node_tree_dft(child, child_property, do_fn)
    return True
