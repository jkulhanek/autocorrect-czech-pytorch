from download import resource
from encoder import Tokenizer
from torchvision.transforms import Compose
import torch

SOS_token = 0
EOS_token = 1

class TextDataset:
    def __init__(self, file, transform = None):
        with open(file, 'r', encoding = 'utf-8') as f:
            self.lines = [x.strip('\n') for x in f.readlines()]
        self.max_length = max((len(x) for x in self.lines))
        self.transform = transform

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):
        item = self.lines[index]

        if self.transform is not None:
            item = self.transform(item)
        return item

class Tokenize:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        pass

    def __call__(self, string):
        if isinstance(string, tuple):
            return tuple(map(self, string))
            
        return self.tokenizer.to_embedding(string)

class Augment:
    def __init__(self, augmenter):
        self.augmenter = augmenter
        pass

    def __call__(self, input):
        return (input, self.augmenter.augment(input))

class ToTensor:
    def __init__(self, device):
        self.device = device
        pass

    def __call__(self, stream):
        if isinstance(stream, tuple):
            return tuple(map(self, stream))

        stream.append(EOS_token)
        return torch.tensor(stream, dtype=torch.long, device=self.device).view(-1, 1)

def create_dataset(augmenter, device):
    f, charmap = resource('phword')
    tokenizer = Tokenizer(charmap, offset = 2)
    dataset = TextDataset(f, transform=Compose([Augment(augmenter), Tokenize(tokenizer), ToTensor(device)]))
    dataset.embedding_size = len(tokenizer)
    return dataset
