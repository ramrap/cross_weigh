from flair.data import Corpus
from flair.data_fetcher import NLPTaskDataFetcher
from flair.embeddings import TokenEmbeddings, WordEmbeddings, StackedEmbeddings, FlairEmbeddings, PooledFlairEmbeddings
from flair.trainers import ModelTrainer
from flair.models import SequenceTagger
from typing import List
import argparse
import os
from sequence_tagger_with_weights import WeightedSequenceTagger

import flair, torch
flair.device = torch.device('cuda:2')

parser = argparse.ArgumentParser()
parser.add_argument('--folder_name', required=True)
parser.add_argument('--include_weight', action='store_true')
parser.add_argument('--data_folder_prefix')
parser.add_argument('--model_folder_prefix')
args = parser.parse_args()
print(vars(args))

column_format = {0: 'text', 1: 'ner'} # the datafiles generated by our scripts have columns: text ner [weight]
if args.include_weight:
    column_format[2] = 'weight'

# this can be modified to individual needs.
data_folder = os.path.join(args.data_folder_prefix, args.folder_name)
model_folder = os.path.join(args.model_folder_prefix, args.folder_name)

if args.include_weight:
    model_folder += '_w'
# print(column_format)
corpus: Corpus = NLPTaskDataFetcher.load_column_corpus(data_folder,
                                                       column_format=column_format,
                                                       tag_to_biloes="ner")

tag_type = 'ner'

tag_dictionary = corpus.make_tag_dictionary(tag_type=tag_type)

embedding_types: List[TokenEmbeddings] = [

    # GloVe embeddings
    WordEmbeddings('glove'),

    # contextual string embeddings, forward
    FlairEmbeddings('news-forward'),
    # PooledFlairEmbeddings('news-forward', pooling='min'),

    # contextual string embeddings, backward
    FlairEmbeddings('news-backward'),
    # PooledFlairEmbeddings('news-backward', pooling='min'),
]

embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)

tagger: SequenceTagger = WeightedSequenceTagger(hidden_size=256,
                                                embeddings=embeddings,
                                                tag_dictionary=tag_dictionary,
                                                tag_type=tag_type)

trainer: ModelTrainer = ModelTrainer(tagger, corpus)
# 20 
trainer.train(model_folder,
              max_epochs=3,
              monitor_test=True,
              train_with_dev=True,
              embeddings_storage_mode='gpu'
              )


def get_tokens_and_labels(sentence):
    tokens = []
    labels = []
    for token in sentence.tokens:
        tokens.append(token.text)
        labels.append(token.get_tag("ner").value)
    return tokens, labels


def iobes2bio(iobes_labels):
    bio_labels = []
    for label in iobes_labels:
        if label[0] == 'S':
            bio_labels.append('B' + label[1:])
        elif label[0] == 'E':
            bio_labels.append('I' + label[1:])
        else:
            bio_labels.append(label)
    return bio_labels


tagger = SequenceTagger.load(os.path.join(model_folder, 'final-model.pt'))

test_sentences = [x for x in corpus.test]
tagger.predict(test_sentences)
sentences = []
for sentence in test_sentences:
    tokens, labels = get_tokens_and_labels(sentence)
    labels = iobes2bio(labels)
    sentences.append((tokens, labels))
with open(os.path.join(data_folder, 'predict.bio'), 'w') as f:
    for tokens, labels in sentences:
        for token, label in zip(tokens, labels):
            f.write(f'{token}\t{label}\n')
        f.write('\n')
