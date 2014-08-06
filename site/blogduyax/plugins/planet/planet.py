from pelican import signals
from pelican import writers

def planet_generator(generator):
        planet_atom = []
        for article in generator.articles:
                if 'planet' in article.metadata.keys() and article.metadata['planet'] == 'true':
                        planet_atom.append(article) 

        writer = writers.Writer(generator.settings['OUTPUT_PATH'], generator.settings)
        writer.write_feed(planet_atom, generator.context, generator.settings['FEED_ATOM_CUSTOM'] % 'planet')

def register():
        signals.article_generator_finalized.connect(planet_generator)

