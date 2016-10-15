# text_divider.py, © 2016, Moacir P. de Sá Pereira
#
# Available on github: https://github.com/muziejus/text-divider
# 
# A Python implementation of David Hoover’s Analyze Textual Divisions Spreadsheet:
#
# https://wp.nyu.edu/exceltextanalysis/analyzetextualdivisions/

import click # make the command line version easy
import re

@click.command()
@click.argument('input') #, type=click.File('rb'))
@click.argument('output', type=click.File('w'), default='-', required=False)
def cli(input, output):
    """
    This script takes a lightly-marked text file and generates a .csv file
    where each line of text is tagged in some way.
    
    It accepts two arguments, INPUT and OUTPUT. INPUT is required, and it is a
    .txt file. OUTPUT defaults to standard out, but it’s probably more useful
    to include a .csv file name.
    
    For more information, see https://github.com/muziejus/text_divider
    """
    text = Text(input, output)
    text.toCsv()

class Text():
    def __init__(self, input, output):
        self.input = input
        self.output = output
        self.lines = self.getContentsByLine()

    def getContentsByLine(self):
        """
        Reads the input file into a list by line.
        """
        with open(self.input) as f:
            contents = f.readlines()
        return [line.strip("\n") for line in contents]

    def number_of_lines(self):
        """
        Gives the number of lines in the text.
        """
        return len(self.lines)

    def parse(self):
        """
        Returns a list of dicts, where each dict has a 
        series of keys and values depending on the markup.
        """
        list = []
        speaker = None
        for line in self.lines:
            text = line
            if(re.search(r'^\s*$', line)): # blank line reset
                speaker = None
            else:
                if line[0] == '/': # dialogue trigger
                    # print("dialogue triggered")
                    speaker = line.split('"')[0][1:]
                    text = line.split('"')[1]
                if(speaker != None): # strip trailing " from dialogue.
                    if(re.search(r'"$', line)):
                        line = re.sub(r'"$', '', line)
                        text = line
                list.append({"text": text, "speaker": speaker})
        return list

    def toCsv(self):
        lines = self.parse()
        self.output.write("SPEAKER\tTEXT\n")
        for line in lines:
            self.output.write("{0}\t{1}\n".format(line['speaker'], line['text']))

if __name__ == '__main__':
    cli()
