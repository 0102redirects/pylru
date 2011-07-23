

PyLRU
=====

A least recently used (LRU) cache for Python.

Introduction
============

Pylru implements a true LRU cache along with several support classes. The cache is efficient and written in pure Python. It works with Python 2.6+ including the new 3.x series. Basic operations (lookup, insert, delete) all run in a constant amount of time.

You can install pylru, or you can just copy the source file pylru.py and use it in your own project.


Usage
=====


lrucache
--------

An LRU cache object has a dictionary like interface and can be used in the same way::

    import pylru

    size = 100          # Maximum number of key/value pairs you want the cache
                        # to hold.
    
    cache = pylru.lrucache(size)
                        # Create a cache object.
    
    value = cache[key]  # Lookup a value given its key.
    cache[key] = value  # Insert a key/value pair.
    del cache[key]      # Delete a value given its key.
                        #
                        # These three operations affect the order of the cache.
                        # Lookup and insert both move the key/value to the most
                        # recently used position. Delete (obviously) removes a
                        # key/value from whatever position it was in.
                        
    key in cache        # Test for membership. Does not affect the cache order.
    
    value = cache.peek(key)
                        # Lookup a value given its key. Does not affect the
                        # cache order.

    cache.keys()        # Return an iterator over the keys in the cache
    cache.values()      # Return an iterator over the values in the cache
    cache.items()       # Return an iterator over the (key, value) pairs in the
                        # cache.
                        #
                        # These calls have no effect on the cache order.
                        # The iterators iterate over their respective elements
                        # in the order of most recently used to least recently
                        # used.
                        #
                        # WARNING - While these iterators do not effect the
                        # cache order the lookup, insert, and delete operations
                        # do. The results of changing the cache's order
                        # during iteration is undefined. If you really need to
                        # do something of the sort use list(cache.keys()), then
                        # loop over the list elements.
                        
    for key in cache:   # Caches support __iter__ so you can use them directly
        pass            # in a for loop to loop over the keys just like
                        # cache.keys()

    cache.size()        # Returns the size of the cache
    cache.size(x)       # Changes the size of the cache. x MUST be greater than
                        # zero. Returns the new size x.

    x = len(cache)      # Returns the number of items stored in the cache.
                        # x will be less than or equal to cache.size()

    cache.clear()       # Remove all items from the cache.


The lrucache takes an optional callback function as a second argument. Since the cache has a fixed size, some operations (such as an insertion) may cause a key/value pair to be ejected. If the optional callback function is given it will be called when this occurs. For example::

    import pylru

    def callback(key, value):
        print (key, value)    # A dumb callback that just prints the key/value

    size = 100
    cache = pylru.lrucache(size, callback)

    # Use the cache... When it gets full some pairs may be ejected due to
    # the fixed cache size. But, not before the callback is called to let you
    # know.

WriteThroughCacheManager
========================

By default lruwrap uses write-through semantics. For instance, in the above example insertions are updated in the cache and written through to slowDict immediately. The cache and the underlying object are not allowed to get out of sync. So only lookup performance can be improved by the cache.


Often a cache is used to speed up access to some other high latency object. If that object has a dictionary interface a convenience wrapper class provided by PyLRU can be used. This class takes as an argument the object you want to wrap and the cache size. It then creates an LRU cache for the object and automatically manages it. For example, imagine you have a backend storage object with a dictionary interface that reads/writes its values to and from a remote server. Let us call this object *store*::

    import pylru

    size = 100
    cached = pylru.lruwrap(store, size)

    # Now the object *cached* can be used just like *store*, except all of the
    # basic operations (lookup, insert, delete) are automatically cached for
    # you using an LRU cache.
    
    # Lookup may be faster.
    
    value = cached[key] # Lookup a value given its key.
    cached[key] = value # Insert a key/value pair.
    del cached[key]     # Delete a value given its key.
    
    key in cache        # Test for membership. Does not affect the cache order.

    cached.keys()       # Returns store.keys()
    cached.values()     # Returns store.values() 
    cached.items()      # Returns store.items()
                        #
                        # These calls have no effect on the cache order.
                        # The iterators iterate over their respective elements
                        # in the order dictated by store.
                        
    for key in cached:  # Same as store.keys()

    cached.size()       # Returns the size of the cache
    cached.size(x)      # Changes the size of the cache. x MUST be greater than
                        # zero. Returns the new size x.

    x = len(cached)     # Returns the number of items stored in the store.

    cached.clear()      # Remove all items from the store and cache.


WriteBackCacheManager
=====================

lruwrap takes an optional third argument. If set to True write-back semantics will be used. Insertions will be updated to the cache. The underlying slowDict will automatically be updated only when a "dirty" key/value pair is ejected from the cache.

If write-back is used the programmer is responsible for one more thing. They MUST call sync() when they are finished. This ensures that the last of the "dirty" entries in the cache are written back::


    import pylru

    size = 100
    cacheDict = pylru.lruwrap(slowDict, size, True)

    # Now cacheDict can be used just like slowDict, except all of the lookups
    # are automatically cached for you using an LRU cache with Write-Back
    # semantics.

    # DON'T forget to call sync() when finished
    cacheDict.sync()
    
    cached.keys()       # Return an iterator over the keys in the cache/store
    cached.values()     # Return an iterator over the values in the cache/store
    cached.items()      # Return an iterator over the (key, value) pairs in the
                        # cache/store.
                        #
                        # The iterators iterate over a consistant view of the
                        # respective elements. That is, except for the order,
                        # the elements are the same as those returned if you
                        # first called sync() then called
                        # store.keys()[ or values() or items()]
                        #
                        # These calls have no effect on the cache order.
                        # The iterators iterate over their respective elements
                        # in arbitrary order.
                        #
                        # WARNING - While these iterators do not effect the
                        # cache order the lookup, insert, and delete operations
                        # do. The results of changing the cache's order
                        # during iteration is undefined. If you really need to
                        # do something of the sort use list(cache.keys()), then
                        # loop over the list elements.
                        
    for key in cached:  # Same as cached.keys()

    cached.size()       # Returns the size of the cache
    cached.size(x)      # Changes the size of the cache. x MUST be greater than
                        # zero. Returns the new size x.

    cached.clear()      # Remove all items from the store and cache.
    
    cached.sync()       # Make the store and cache consistant. Write all
                        # cached changes to the store that have not been
                        # updated yet.
                        
    cached.flush()      # Calls cached.sync() then clears the cache.
    

To help the programmer with this the lruwrap can be used in a with statement::

    with pylru.lruwrap(slowDict, size, True) as cacheDict

        # Use cacheDict, sync() is called automatically for you when leaving the
        # with statement block.


PyLRU also provides a function decorator::

    from pylru import lrudecorator

    @lrudecorator(100)
    def square(x):
        return x*x

    # Now results of the square function are cached for future lookup.


