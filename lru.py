

# Cache implementaion with a Least Recently Used (LRU) replacement policy and a
# basic dictionary interface.

# Copyright (C) 2006, 2009  Jay Hutchinson

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



# The cache is implemented using a combination of a hash table (python
# dictionary) and a circluar doubly linked list. Objects in the cache are
# stored in nodes. These nodes make up the linked list. The list is used to
# efficiently maintain the order that the objects have been used in. The front
# or "head" of the list contains the most recently used object, the "tail" of
# the list contains the least recently used object. When an object is "used" it
# can easily (in a constant amount of time) be moved to the front of the list,
# thus updating its position in the ordering. These nodes are also placed in
# the hash table under their associated key. The hash table allows efficient
# lookup of objects by key.



class lrucache:
  
  def __init__(self, size):
      
    assert size > 0
    
    # Initialize the hash table as empty.
    self.table = {}
    
    # The doubly linked list is composed of nodes. The nodes for the list are
    # all pre-built upfront, so the class definition is only needed here. Each
    # node has a 'prev' and 'next' variable to hold the node that comes before
    # it and after it respectivly. Initially the two variables each point to
    # the node itself, creating a circular doubly linked list of size one. Each
    # node has a 'obj' and 'key' variable, holding the object and the key it is
    # stored under respectivly.
    class dlnode:
      def __init__(self):
	
	self.next = self
	self.prev = self
             
	self.key = None
	self.obj = None
    
    
    # Initalize the list with 'size' empty nodes. Create the first node and
    # assign it to the 'head' variable, which represents the head node in the
    # list. Then each iteration of the loop creates a subsequent node and
    # inserts it directly after the head node.
    self.head = dlnode()
    for i in range(1, size):
      node = dlnode()
      
      node.prev = self.head
      node.next = self.head.next
  
      self.head.next.prev = node
      self.head.next = node

  def __len__(self):
    return len(self.table)
    
  def clear(self):
      self.table.clear()
    
  def __contains__(self, key):
    return key in self.table
    
    
  def __getitem__(self, key):
    
    # Look up the node
    node = self.table[key]
    
    # Update the list ordering. Move this node so that is directly proceeds the
    # head node. Then set the 'head' variable to it. This makes it the new head
    # of the list.
    self.mtf(node)
    self.head = node
    
    # Return the object
    return node.obj
  
  
  def __setitem__(self, key, obj):
    
    # First, see if any object is stored under 'key' in the cache already. If
    # so we are going to replace that object with the new one.
    if key in self.table:
      
      # Lookup the node
      node = self.table[key]
      
      # Replace the object
      node.obj = obj
      
      # Update the list ordering.
      self.mtf(node)
      self.head = node
      
      return
      
    # Ok, no object is currently stored under 'key' in the cache. We need to
    # choose a node to place the object 'obj' in. There are two cases. If the
    # cache is full some object will have to be pushed out of the cache. We
    # want to choose the node with the least recently used object. This is the
    # node at the tail of the list. If the cache is not full we want to choose
    # a node that is empty. Because of the way the list is managed, the empty
    # nodes are always together at the tail end of the list. Thus, in either
    # case, by chooseing the node at the tail of the list our conditions are
    # satisfied.
    
    # Since the list is circular, the tail node directly preceeds the 'head'
    # node.
    node = self.head.prev
    
    # If the node already contains something we need to remove the old key from
    # the dictionary.
    if not node.key == None:
      del self.table[node.key]
    
    # Place the key and the object in the node
    node.key = key
    node.obj = obj
    
    # Add the node to the dictionary under the new key.
    self.table[node.key] = node 
    
    # We need to move the node to the head of the list. The node is the tail
    # node, so it directly preceeds the head node due to the list being
    # circular. Therefore, the ordering is already correct, we just need to
    # adjust the 'head' variable.
    self.head = node
  
  
  def __delitem__(self, key):
    
    # Lookup the node, then remove it from the hash table.
    node = self.table[key]
    del self.table[key]
    
    # Set the 'key' to None to indicate that the node is empty. We also set the
    # 'obj' to None to release the reference to the object, though it is not
    # strictly necessary.
    node.key = None
    node.obj = None
    
    # Because this node is now empty we want to reuse it before any non-empty
    # node. To do that we want to move it to the tail of the list. We move it
    # so that it directly preceeds the 'head' node. This makes it the tail
    # node. The 'head' is then adjusted. This adjustment ensures correctness
    # even for the case where the 'node' is the 'head' node.
    self.mtf(node)
    self.head = node.next
    
    return
      
    
  
  
  def __del__(self):
    # When we are finished with the cache, special care is taken to break the
    # doubly linked list, so that there are no cycles. First all of the 'prev'
    # links are broken. Then the 'next' link between the 'tail' node and the
    # 'head' node is broken.
    
    tail = self.head.prev
    
    node = self.head
    while node.prev:
      node = node.prev
      node.next.prev = None
      
    tail.next = None
  
  
  # This method adjusts the doubly linked list so that 'node' directly preeceds
  # the 'head' node. Note that it works even if 'node' already directly
  # preceeds the 'head' node or if 'node' is the 'head' node, in either case
  # the order of the list is unchanged.
  def mtf(self, node):
    
    node.prev.next = node.next
    node.next.prev = node.prev

    node.prev = self.head.prev
    node.next = self.head.prev.next
    
    node.next.prev = node
    node.prev.next = node

    
  def _selftest():
    
    class simplelrucache:
      
      def __init__(self, size):
	self.size = size
	self.length = 0
	self.items = []
	
      def __contains__(self, key):
	for x in self.items:
	  if x[0] == key:
	    return True
	    
	return False
  
	
	
	
	
class simplelrucache:
  
  def __init__(self, size):
    
    # Initialize the cache as empty.
    self.cache = []
    self.size = size
    
  def __contains__(self, key):
    
    for x in self.cache:
      if x[0] == key:
	return True
	
    return False
    
    
  def __getitem__(self, key):
    
    for i in range(len(self.cache)):
      x = self.cache[i]
      if x[0] == key:
	del self.cache[i]
	self.cache.append(x)
	return x[1]
      
    assert False
  
  
  def __setitem__(self, key, obj):
    
    for i in range(len(self.cache)):
      x = self.cache[i]
      if x[0] == key:
	x[1] = obj
	del self.cache[i]
	self.cache.append(x)
	return
	
    if len(self.cache) == self.size:
      self.cache = self.cache[1:]
    
    self.cache.append([key, obj])
    
    return
  
  def __delitem__(self, key):
    
    for i in range(len(self.cache)):
      if self.cache[i][0] == key:
	del self.cache[i]
	return
    
    return
      
  
    
    
    
def testa():
  
  a = lrucache(16)
  
  for i in range(len(vect)):
    a[vect[i]] = 0
    
def testb():
  
  a = simplelrucache(16)
  
  for i in range(len(vect)):
    a[vect[i]] = 0
    
    
if __name__ == '__main__':
  
  import random
  
  a = lrucache(20)
  b = simplelrucache(20)
  
  for i in range(256):
    x = random.randint(0, 256)
    y = random.randint(0, 256)
    
    a[x] = y
    b[x] = y
    
    q = []
    z = a.head
    for j in range(len(a.table)):
      q.append([z.key, z.obj])
      z = z.next
      
    if q != b.cache[::-1]:
      print i
      print b.cache[::-1]
      print q
      print a.table.keys()
      assert False
  
  

  from timeit import Timer
  import random
  
  global vect
  
  vect = []
  for i in range(1000000):
    vect.append(random.randint(0, 1000))
  
  t = Timer("testa()", "from __main__ import testa")
  print t.timeit(1)

  t = Timer("testb()", "from __main__ import testb")
  print t.timeit(1)
  
