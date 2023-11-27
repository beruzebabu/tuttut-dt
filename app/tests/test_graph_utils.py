import unittest
import pretty_midi

from app import graph_utils

class TestGraphUtils(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_distance_between(self):
        p1 = (0, 0)
        
        p2 = (1, 0)
        self.assertEqual(graph_utils.distance_between(p1, p2), 1/6)
        
        p2 = (0, 1)
        self.assertEqual(graph_utils.distance_between(p1, p2), 1)
        
        p2 = (18, 4) #for 3 (18/6), 4 and 5 triangle
        self.assertEqual(graph_utils.distance_between(p1, p2), 5) 
        
    def test_get_fret_distance(self):
        scale_length = 650
        
        nfret = 0
        self.assertAlmostEqual(graph_utils.get_fret_distance(nfret, scale_length=scale_length), 0, places=1)
        
        nfret = 10
        self.assertAlmostEqual(graph_utils.get_fret_distance(nfret, scale_length=scale_length), 285.20, places=1)
        
        scale_length = 660
        
        nfret = 0
        self.assertAlmostEqual(graph_utils.get_fret_distance(nfret, scale_length=scale_length), 0, places=1)
        
        nfret = 20
        self.assertAlmostEqual(graph_utils.get_fret_distance(nfret, scale_length=scale_length), 452.11, places=1)
        
    def test_get_notes_in_graph(self):
        pass
    
    def test_build_path_graph(self):
        pass
    
    def test_is_edge_possible(self):
        pass
    
    def test_find_all_paths(self):
        pass
    
    def test_is_path_already_checked(self):
        pass
    
    def test_is_path_possible(self):
        pass
    
    def test_compute_path_difficulty(self):
        pass
    
    def test_compute_isolated_path_difficulty(self):
        pass
    
    def test_laplace_distro(self):
        pass
    
    def test_get_nfingers(self):
        pass
    
    def test_get_n_changed_strings(self):
        pass
    
    def test_get_height(self):
        pass
    
    def test_get_path_length(self):
        pass
    
    def test_display_path_graph(self):
        pass
    
    def test_viterbi(self):
        pass
    
    def test_build_transition_matrix(self):
        pass
    
    def test_difficulties_to_probabilities(self):
        pass
    
    def test_expand_emission_matrix(self):
        pass
    
    def test_display_notes_on_graph(self):
        pass
        
        