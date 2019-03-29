class Tokenizer:
    def __init__(self, charmap, offset = 0):
        self.char_to_embedding = { key: i for i, key in enumerate(charmap) }
        self.charmap = charmap
        self.offset = offset

    def to_embedding(self, string):
        output = []
        for char in string:
            output.append(self.char_to_embedding.get(char))
        return output

    def to_text(self, embedding):
        output = []
        for i in embedding:
            output.append(self.charmap[i])
        return ''.join(output)

    def __len__(self):
        return len(self.charmap) + self.offset
