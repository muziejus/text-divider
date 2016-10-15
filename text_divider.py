# text_divider.py, © 2016, Moacir P. de Sá Pereira
#
# Available on github: https://github.com/muziejus/text-divider
# 
# A Python implementation of David Hoover’s Analyze Textual Divisions Spreadsheet:
#
# https://wp.nyu.edu/exceltextanalysis/analyzetextualdivisions/

import click # make the command line version easy
import re
import os

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
    text = Text(input)
    text.to_csv(output)

class Text():
    def __init__(self, input):
        self.input = input
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
        chapter = None
        for line in self.lines:
            text = line
            if(re.search(r'^\s*$', line)): # blank line reset
                speaker = None
            else:
                if(line[0] == '/'): # dialogue trigger
                    match = re.match(r'/([^"]*)"(.*)$', line)
                    speaker = match.group(1)
                    text = match.group(2)
                if(speaker != None): # strip trailing " from dialogue.
                    if(re.search(r'"\s*$', text)):
                        text = re.sub(r'"\s*$', '', text)
                if(line[0:3] == "<1>"):
                    chapter = line[3:]
                    text = line[3:]
                list.append({"text": text, "speaker": speaker, "chapter": chapter})
        return list

    def speakers(self, speaker):
        """
        Gives all of the dialogue of a specific speaker in one string.
        """
        lines = self.parse()
        speaker_lines = [line['text'] for line in lines if line['speaker'] == speaker]
        if(len(speaker_lines) == 0):
            raise Exception("No such speaker found!")
        return " ".join(speaker_lines)

    def all_speakers(self):
        """
        Gives a list of tuples of the form (speaker, lines of dialogue)
        """
        lines = self.parse()
        speakers = set([line['speaker'] for line in lines])
        list = []
        for speaker in speakers:
            lines_of_dialogue = len([line for line in lines if line['speaker'] == speaker])
            list.append((speaker, lines_of_dialogue))
        return list

    def export_speakers_as_text(self, output_dir = "speakers_export"):
        # this should be an option available in the cli.
        # and the output dir should be passable from the cli.
        """
        Exports each speaker’s dialogue as a string into its own text file.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        speakers = [speaker[0] for speaker in self.all_speakers()]
        for speaker in speakers:
            if not speaker == None:
                f = open("{0}/{1}.txt".format(output_dir, self.parameterize(speaker)), "w")
                f.write(self.speakers(speaker))
                f.close()

    def to_csv(self, output):
        """
        Dumps all the data to a (tab-delimited) .csv
        """
        lines = self.parse()
        output.write("CHAPTER\tSPEAKER\tTEXT\n")
        for line in lines:
            output.write("{0}\t{1}\t{2}\n".format(line['chapter'], line['speaker'], line['text']))

    def parameterize(self, string):
        """
        Strips down a string to make a filename.
        """
        return "".join([c.lower() for c in string if c.isalpha() or c.isdigit()]).rstrip()

if __name__ == '__main__':
    cli()
