#!/usr/bin/env python3
import logging
import os

import requests
import json
import datetime
import time
from sys import stdout


class database_builder:

    def __init__(self):
        self.api_url = "https://api.scryfall.com"
        api_response = requests.get(self.api_url + "/sets")
        time.sleep(0.1)
        if api_response.status_code != 200:
            raise ValueError("API Not avaiable")
        with open('config.json') as json_file:
            self.config = json.load(json_file)
        self.set_list = []
        self.set_card_dict = {}
        logging.getLogger().setLevel(logging.INFO)

    def get_list_of_sets(self):
        time.sleep(0.1)
        api_response = requests.get(self.api_url + "/sets")
        if api_response.status_code != 200:
            raise ValueError("API Not avaiable")
        self.set_list_raw_data = json.loads(api_response.text)
        self.filter_list_of_sets()

    def filter_list_of_sets(self):
        for set in self.set_list_raw_data["data"]:
            date = time.mktime(datetime.datetime.strptime(set["released_at"], "%Y-%m-%d").timetuple())
            date_min = time.mktime(datetime.datetime.strptime(self.config["set_filter"]["date_min"], "%Y-%m-%d").timetuple())
            date_max = time.mktime(datetime.datetime.strptime(self.config["set_filter"]["date_max"], "%Y-%m-%d").timetuple())
            if date_min < date < date_max:
                if set["set_type"] in ["expansion", "core"]:
                    self.set_list.append(set)

    def gather_cards_in_set(self):
        for set in self.set_list:
            raw_card_data = []
            logging.info("Add data from {}".format(set["name"]))
            uri = set["search_uri"]
            self.gather_data_recursive(raw_card_data, uri)
            self.create_set_card_database(raw_card_data, set)

    def write_dict_to_file(self):
        logging.info("Write label data to file")
        with open('data/card_database.json', 'w') as outfile:
            json.dump(self.set_card_dict, outfile)

    def gather_data_recursive(self, raw_card_data, uri):
        time.sleep(0.11)  # API rejects too fast/many reqeuests and suggests waiting 0.1
        api_response = requests.get(uri)
        response = json.loads(api_response.text)
        raw_card_data.extend(response["data"])
        if response["has_more"]:
            self.gather_data_recursive(raw_card_data, response["next_page"])

    def create_set_card_database(self, raw_data, set):
        self.set_card_dict.update({set["code"]: self.filter_cards_from_sets(raw_data)})

    def filter_cards_from_sets(self, raw_card_data):
        filtered_card_data = []
        for card in raw_card_data:
            if card["object"] == "card" and \
                    card["layout"] == "normal" and \
                    "land" not in card["type_line"].lower():
                filtered_card_data.append(card)
        return filtered_card_data

    def download_images(self):
        for set, card_list in self.set_card_dict.items():
            logging.info("Downlaod Cards for {}".format(set))
            os.mkdir("data/mtg_" + set)
            i = 1
            for card in card_list:
                stdout.write("\rCard {:03d} of {:03d}".format(i, len(card_list)))
                stdout.flush()
                time.sleep(0.11)
                api_response = requests.get(card["image_uris"]["large"], allow_redirects=True)
                file = open("data/mtg_" + set + "/" + card["name"] + ".jpg", "wb")
                file.write(api_response.content)
                file.close()
                i += 1
            print("\n")
            time.sleep(0.05)

    def generate_database(self):
        logging.info("Gather all applicable sets")
        self.get_list_of_sets()
        logging.info("Gather card infos for data labeling")
        self.gather_cards_in_set()
        logging.info("Download Images for image recognition")
        self.download_images()
        self.write_dict_to_file()


if __name__ == "__main__":
    d = database_builder()
    d.generate_database()
