# text-divider.py, © 2016, Moacir P. de Sá Pereira
#
# Available on github: https://github.com/muziejus/text-divider
# 
# A Python implementation of David Hoover’s Analyze Textual Divisions Spreadsheet:
#
# https://wp.nyu.edu/exceltextanalysis/analyzetextualdivisions/

import click # make the command line version easy

@click.command()
@click.argument('input') #, type=click.File('rb'))
@click.argument('output', type=click.File('w'), default='-', required=False)
def cli(input, output):
    """This script takes a lightly-marked text file and generates a .csv file where each line of text is tagged in some way.
    
    It accepts two arguments, INPUT and OUTPUT. INPUT is required, and it is a .txt file. OUTPUT defaults to standard out, but it’s probably more useful to include a .csv file name.
    
    For more information, see https://github.com/muziejus/text_divider"""
    text = Text(input)
    # For now, it just writes the contents.
    output.write(text.writeContents())

class Text():
    def __init__(self, input):
        self.input = input
        self.contents = self.getContents()

    def getContents(self):
        """
        Reads the input file into memory.
        """
        with open(self.input) as f:
            contents = f.read()
        return contents

    def writeContents(self):
        return self.contents

if __name__ == '__main__':
    cli()
