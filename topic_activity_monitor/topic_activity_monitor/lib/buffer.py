class Buffer(list):
    """ A buffer made from a list() """
    def __init__(self, max_size):
        list.__init__(self)
        self.max_size = max_size

    def push(self, data):
        """ Adds data to the buffer """
        # Add data to the end of the list
        list.append(self, data)
        # If buffer is over capacity, remove the first item from the list
        if len(self) > self.max_size:
            self.pop(0)

    def full(self):
        """ return True if the buffer has reached capacity """
        return len(self) == self.max_size

def example():
    b = Buffer(4)

    b.push('a')
    print(b)

    b.push('b')
    print(b)

    b.push('c')
    print(b)
    print("Is Full?", b.full())

    b.push('d')
    print(b)
    print("Is Full?", b.full())

    b.push('e')
    print(b)
    print("Is Full?", b.full())

    b.clear()
    print(b)

    b.push('f')
    print(b)

if __name__ == "__main__":
    example()
