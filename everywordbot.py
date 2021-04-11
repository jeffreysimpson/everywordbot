import tweepy
from nltk.corpus import words
import random


class EverywordBot(object):

    def __init__(self, consumer_key, consumer_secret,
                 access_token, token_secret,
                 lat=None, long=None, place_id=None,
                 prefix=None, suffix=None, bbox=None,
                 dry_run=False):
        self.lat = lat
        self.long = long
        self.place_id = place_id
        self.prefix = prefix
        self.suffix = suffix
        self.bbox = bbox
        self.dry_run = dry_run

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, token_secret)
        self.twitter = tweepy.API(auth)

    def _get_current_line(self):
        new_word = False
        word_list = words.words()
        while new_word is False:
            word_set = set(line.strip() for line in open("used_words"))

            rand_idx = random.randint(a=0, b=len(word_list)-1)
            rand_word = word_list[rand_idx]

            if rand_word in word_set:
                print(f"We've already tweeted {rand_word}!")
            else:
                print(f"New word to tweet: {rand_word}!")
                with open("used_words", 'a') as f:
                    f.write(f"{rand_word}\n")
                new_word = True
        return rand_word.capitalize()

    def _random_point_in(self, bbox):
        """Given a bounding box of (swlat, swlon, nelat, nelon),
         return random (lat, long)"""
        import random
        lat = random.uniform(bbox[0], bbox[2])
        long = random.uniform(bbox[1], bbox[3])
        return (lat, long)

    def post(self):
        status_str = self._get_current_line()
        if self.prefix:
            status_str = self.prefix + status_str
        if self.suffix:
            status_str = status_str + self.suffix
        if self.bbox:
            self.lat, self.long = self._random_point_in(self.bbox)

        if self.dry_run:
            print(status_str)
        else:
            self.twitter.update_status(status=status_str,
                                       lat=self.lat, long=self.long,
                                       place_id=self.place_id)


def _csv_to_float_list(csv):
    return list(map(float, csv.split(',')))


if __name__ == '__main__':

    def _get_comma_separated_args(option, opt, value, parser):
        setattr(parser.values, option.dest, _csv_to_float_list(value))

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--consumer_key', dest='consumer_key',
                      help="twitter consumer key")
    parser.add_option('--consumer_secret', dest='consumer_secret',
                      help="twitter consumer secret")
    parser.add_option('--access_token', dest='access_token',
                      help="twitter token key")
    parser.add_option('--token_secret', dest='token_secret',
                      help="twitter token secret")
    parser.add_option('--lat', dest='lat',
                      help="The latitude for tweets")
    parser.add_option('--long', dest='long',
                      help="The longitude for tweets")
    parser.add_option('--place_id', dest='place_id',
                      help="Twitter ID of location for tweets")
    parser.add_option('--bbox', dest='bbox',
                      type='string',
                      action='callback',
                      callback=_get_comma_separated_args,
                      help="Bounding box (swlat, swlon, nelat, nelon) "
                           "of random tweet location")
    parser.add_option('--prefix', dest='prefix',
                      help="string to add to the beginning of each post "
                           "(if you want a space, include a space)")
    parser.add_option('--suffix', dest='suffix',
                      help="string to add to the end of each post "
                           "(if you want a space, include a space)")
    parser.add_option('-n', '--dry_run', dest='dry_run', action='store_true',
                      help="Do everything except actually send the tweet or "
                           "update the index file")
    (options, args) = parser.parse_args()

    bot = EverywordBot(options.consumer_key, options.consumer_secret,
                       options.access_token, options.token_secret,
                       options.lat, options.long, options.place_id,
                       options.prefix, options.suffix, options.bbox,
                       options.dry_run)

    bot.post()
