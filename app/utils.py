import numpy as np
import pretty_midi
from pretty_midi.utilities import note_name_to_number
import app.theory as theory
import math
import networkx as nx
import matplotlib.pyplot as plt
import itertools

def note_number_to_note(note_number): #Converts pretty_midi note number to a Note object
  note = str(pretty_midi.note_number_to_name(note_number))
  (degree, octave) = (note[:-1], note[-1:]) if not '-' in note else (note[:-2], note[-2:])
  degree = theory.Degree(degree)
  
  return theory.Note(degree, octave)

def midi_note_to_note(note): #Converts a pretty_midi note to a Note object
  return note_number_to_note(note.pitch)

def measure_length_ticks(midi, time_signature): #Returns the number of ticks in a measure for a midi file
  measure_length = time_signature.numerator * midi.resolution
  return measure_length

def get_notes_between(midi, notes, begin, end): #Return all notes between two specific timings in a midi file
  res = []
  for note in notes:
    start = midi.time_to_tick(note.start)
    if start >= begin and start< end:
      res.append(note)

  return res
  
def note_to_fret(string, note): #Converts a Note object to its corresponding fret number on a string
  string_name = string.degree.value + str(string.octave)
  note_name = note.degree.value + str(note.octave)
  n_string = pretty_midi.note_name_to_number(string_name)
  n_note = pretty_midi.note_name_to_number(note_name)

  return n_note - n_string

def get_non_drum(instruments): #Returns all instruments that are non-drums
  res = []
  for instrument in instruments:
    if not instrument.is_drum:
      res.append(instrument)
  return res

def get_all_possible_notes(tuning, nfrets = 20): #Returns all possible_notes on a fretboard for k strings and n frets
  nstrings = len(tuning.strings)
  res = []
  for string in tuning.strings:
    string_note_number = note_name_to_number(string.degree.value + str(string.octave))
    string_notes = []
    for ifret in range(nfrets):
      string_notes.append(note_number_to_note(string_note_number+ifret))
    res.append(string_notes)
  
  return res

def distance_between(x, y): #Computes the distance between two points (tuples)
  return math.dist(x,y)

def get_notes_in_graph(G, note): #Get all nodes that correspond to a specific note in a graph
  nodes = list(G.nodes)
  res = []
  for node in nodes:
    if node == note:
      res.append(node)
  return res

def build_path_graph(G, note_arrays): #Returns a path graph corresponding to all possible notes of a chord
  res = nx.Graph()
  
  for x, note_array in enumerate(note_arrays):
    for y, possible_note in enumerate(note_array):
      res.add_node(possible_note, pos = (x, y))

  for idx, note_array in enumerate(note_arrays[:-1]): #Go through every array except the last
    for possible_note in note_array:
      for possible_target_note in note_arrays[idx+1]:
        res.add_edge(possible_note, possible_target_note, distance = G[possible_note][possible_target_note]["distance"])

  return res 

def find_paths(G, path_graph, note_arrays): #Returns all possible paths in a path graph
  paths = []
  for possible_source_node in note_arrays[0]:
    for possible_target_node in note_arrays[-1]: 
      try:
        path = nx.shortest_path(path_graph, possible_source_node, possible_target_node, weight = "distance")
        if is_path_possible(G, path, note_arrays):
          paths.append(path)
      except nx.NetworkXNoPath:
        pass
        #print("No path ???")
        #display_path_graph(path_graph)

  return paths

def is_path_possible(G, path, note_arrays):
  #No 2 fingers on a single string
  plucked_strings = [G.nodes[note]["pos"][0] for note in path]

  #No more than 5 fret span
  used_frets = [G.nodes[note]["pos"][1] for note in path]

  #Path doesn't visit more nodes than necessary
  
  possible = (len(plucked_strings) == len(set(plucked_strings))
              and (max(used_frets) - min(used_frets)) < 5
              and len(path) <= len(note_arrays))

  return possible

def find_best_path(G, note_arrays, previous_path): #Returns the path that best matches the distance_length constraints
  paths = []

  for note_arrays_permutation in list(itertools.permutations(note_arrays)):
    path_graph = build_path_graph(G, note_arrays_permutation)
    # display_path_graph(path_graph)

    paths += find_paths(G, path_graph, note_arrays_permutation)

  path_scores = [compute_path_difficulty(G, path, previous_path) for path in paths]

  best_path = paths[np.argmin(path_scores)]

  return best_path

def compute_path_difficulty(G, path, previous_path):
  height = get_height(G, path)
  previous_height = get_height(G, previous_path) if len(previous_path) > 0 else 0
  dheight = np.abs(height-previous_height)

  length = get_path_length(G, path)

  nfingers = get_nfingers(G, path)

  difficulty = laplace_distro(dheight, b=1) * 1/(1+dheight) * 1/(1+nfingers) * 1/(1+length)

  return 1/difficulty

def laplace_distro(x, b, mu=0):
  return (1/(2*b))*math.exp(-abs(x-mu)/(b))

def get_nfingers(G, path):
  count = 0
  for note in path:
    ifret = G.nodes[note]["pos"][1]
    if ifret != 0:
      count += 1
    
  return count

def get_centroid(G, path): #Returns the centroid of all notes played in a path
  vectors = [G.nodes[note]["pos"] for note in path]
  x = [v[0] for v in vectors]
  y = [v[1] for v in vectors]
  centroid = (sum(x) / len(vectors), sum(y) / len(vectors))
  return centroid

def get_height(G, path): #Returns the average height on the fretboard of all notes played in a path
  y = [G.nodes[note]["pos"][1] for note in path]
  return np.mean(y)

def get_path_length(G, path): #Returns the total length of a path
  res = 0
  for i in range(len(path)-1):
    res += G[path[i]][path[i+1]]["distance"]
  return res
  
def display_path_graph(path_graph, show_distances=True, show_names=True): #Displays the path graph on a plt plot
  pos=nx.get_node_attributes(path_graph,'pos')
  nx.draw(path_graph, pos, with_labels=show_names)

  if show_distances:
    edge_labels = nx.get_edge_attributes(path_graph,'distance')

    for label in edge_labels:
      edge_labels[label] = round(edge_labels[label], 2)
    nx.draw_networkx_edge_labels(path_graph, pos, edge_labels = edge_labels, label_pos = 0.6)

  plt.show()

def fill_measure_str(str_array): #Fills column of a measure so that all strings are of equal length
  maxlen = len(max(str_array, key = len))
  res = []
  for str in str_array:
    res.append(str.ljust(maxlen, "-"))
  return res
  
def sort_notes_by_tick(notes): #Returns sorted notes by tick
  return sorted(notes, key = lambda n: n.start)

def display_notes_on_graph(G, path): #Displays notes played on a plt graph
  pos = nx.get_node_attributes(G,'pos')
  plt.figure(figsize=(2,6))
  nx.draw(G, pos)
  nx.draw(G.subgraph(path), pos = pos, node_color="red")
  plt.show()
  
def round_to_multiple(n, base=10):
    return base * round(n/base)

def quantize(midi):
    for instrument in midi.instruments:
        quantized_notes = []
        for note in instrument.notes:
            rounded = round_to_multiple(midi.time_to_tick(note.start), base=10)
            quantized_notes.append(pretty_midi.Note(velocity = note.velocity, pitch = note.pitch, start = midi.tick_to_time(rounded), end=note.end))

        instrument.notes = quantized_notes

def roll(arr, i): #Shifts array
  return arr[i:] + arr[:i]