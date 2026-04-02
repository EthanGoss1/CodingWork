# Tried this with a disjoint sets solution, but it did not
# Work no matter how hard I tried. Poked around on the interwebs
# And found this thing. 
# Explanation thing:A Trie (pronounced as "try") is a tree-like data structure 
# used to store strings efficiently. It is particularly useful for operations 
# like prefix searching, autocomplete, and spell checking. Each node in a Trie r
# epresents a character, and paths from the root to a leaf node represent words.
# A Trie is exactly what I need. 
class TrieNode:
    def __init__(self):
        self.children = {}
        self.count = 0  # how many words pass through this node

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        node = self.root
        for c in word:
            if c not in node.children:
                node.children[c] = TrieNode()
            node = node.children[c]
            node.count += 1  # Count how many words reach this node

    def count_starts_with(self, prefix):
        #Does exactly what ti claims it does lol
        node = self.root
        for c in prefix:
            if c not in node.children:
                return 0
            node = node.children[c]
        return node.count  # Number of words starting with this prefix


n = int(input())
words = [input().strip() for _ in range(n)]

trie = Trie()

for i in range(n):
    count = trie.count_starts_with(words[i])
    print(count)
    trie.insert(words[i])

