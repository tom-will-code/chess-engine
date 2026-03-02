from src.engine import Game


# perft test
def count_nodes_at_depth(position,depth):
    if depth == 0:
        return 1

    node_count = 0
    for move in position.get_legal_moves():
        new_position, _ = position.after_move(*move)
        node_count += count_nodes_at_depth(new_position,depth - 1)
    
    return node_count

# checks we have correct number of terminal nodes in engine search tree
def test_start_position():
    game = Game() 
    assert count_nodes_at_depth(game.position,1) == 20
    assert count_nodes_at_depth(game.position,2) == 400
    assert count_nodes_at_depth(game.position,3) == 8902
    assert count_nodes_at_depth(game.position,4) == 197281
    print("All tests passed!")



