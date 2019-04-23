import csv
import os

from .item import Item


class Pipeline:
    def process_item(self, item: Item):
        raise NotImplementedError

    def close_pipeline(self):
        pass


class DefaultPipeline(Pipeline):

    def __init__(self, spider):
        self.spider = spider
        self.name = spider.__class__.__name__

        self.init = False
        if not os.path.exists("_items"):
            os.mkdir("_items")

        self.file = None
        self.writer = None

    def init_file(self, item):
        file = '_items/' + self.name + '.csv'

        if os.path.exists(file) and not self.spider.reset_saved_data:
            self.file = open('_items/' + self.name + '.csv', 'a')
            self.writer = csv.writer(self.file)
        else:
            self.file = open('_items/' + self.name + '.csv', 'w')
            self.writer = csv.writer(self.file)
            self.writer.writerow(item.row)
        self.init = True

    def process_item(self, item: Item):
        if not self.init:
            self.init_file(item)
        self.writer.writerow(list(item.value_map.values()))

    def close_pipeline(self):
        if self.file is not None:
            self.file.close()
