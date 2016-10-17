# text_divider.py, © 2016, Moacir P. de Sá Pereira
#
# Available on github: https://github.com/muziejus/text_divider
# 
# A Python implementation of David Hoover’s Analyze Textual Divisions Spreadsheet:
#
# https://wp.nyu.edu/exceltextanalysis/analyzetextualdivisions/

import click # make the command line version easy
import re
import os

@click.command()
@click.option('--speakers-export', type=click.Path(file_okay=False, writable=True), help="This is the directory to which the separate speakers’ files will be exported. Setting this automatically triggers the export command.")
@click.option('--sections-export', type=click.Path(file_okay=False, writable=True), help="This is the directory to which the separate sections’ files will be exported. Setting this automatically triggers the export command.")
@click.argument('input') #, type=click.File('rb'))
@click.argument('output', type=click.File('w'), default='-', required=False)
def cli(input, output, speakers_export, sections_export):
    """
    This script takes a lightly-marked text file and generates a .csv file
    where each line of text is tagged in some way.
    
    It accepts two arguments, INPUT and OUTPUT. INPUT is required, and it is a
    .txt file. OUTPUT defaults to standard out, but it’s probably more useful
    to include a .csv file name.
    
    For more information, see https://github.com/muziejus/text_divider
    """
    text = Text(input)
    if sections_export:
        text.export_sections_to_txt(sections_export)
    if speakers_export:
        text.export_speakers_to_txt(speakers_export)
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
        section = None
        section_one = None
        section_two = None
        for line in self.lines:
            text = line
            if(re.search(r'^\s*$', line)): # blank line reset
                speaker = None
            else:
                if(line[0] == '/'): # dialogue trigger
                    match = re.match(r'/([^"“]*)["“](.*)$', line)
                    speaker = match.group(1)
                    text = match.group(2)
                elif(line[0] == '\\'): # reporting clause trigger
                    speaker = "Reporting clause"
                    text = line[1:]
                if(speaker != None): # strip trailing " from dialogue.
                    if(re.search(r'["”]\s*$', text)):
                        text = re.sub(r'["”]\s*$', '', text)
                if(line[0:3] == "<1>"):
                    section_one = line[3:]
                    section = section_one
                    text = line[3:]
                if(line[0:3] == "<2>"):
                    section = section_one + " - " + line[3:]
                    text = line[3:]
                list.append({"text": text, "speaker": speaker, "section": section})
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
        all_speakers = []
        for speaker in speakers:
            lines_of_dialogue = len([line for line in lines if line['speaker'] == speaker])
            all_speakers.append((speaker, lines_of_dialogue))
        all_speakers = list(reversed(sorted(all_speakers, key=lambda x: x[1])))
        return all_speakers

    def top_speakers(self, top_number):
        """
        Gives the top n speakers in a tuple with the name and the string of dialogue and collapses the rest into one value
        """
        all_speakers = self.all_speakers()
        top_speakers = all_speakers[:top_number]
        minor_speakers_tuple = self.collapse_speakers(all_speakers[top_number:])
        speakers_list = []
        for speaker in top_speakers:
            speakers_list.append((speaker[0], self.speakers(speaker[0])))
        speakers_list.append(minor_speakers_tuple)
        return speakers_list

    def collapse_speakers(self, speakers_list):
        """
        Returns a tuple that has the name "Minor speakers" as one value and the
        concatenated string of all of their dialogue as the second.
        """
        collapsed_string = ""
        for tuple in speakers_list:
            collapsed_string = collapsed_string + " " + self.speakers(tuple[0])
        return ("Minor Speakers", collapsed_string)

    def export_speakers_to_txt(self, output_dir = "speakers_export"):
        """
        Exports each speaker’s dialogue as a string into its own text file.
        """
        speakers = [speaker[0] for speaker in self.all_speakers()]
        speakers_tuple_list = [(speaker, self.speakers(speaker)) for speaker in speakers]
        self.export_to_txt(output_dir, speakers_tuple_list)

    def export_top_speakers_to_txt(self, top_number = 5, output_dir = "speakers_export"):
        """
        Exports the top n speakers’ dialogue as strings into their own text file.
        The rest are concatenated.
        """
        speakers_tuple_list = self.top_speakers(top_number)
        self.export_to_txt(output_dir, speakers_tuple_list)

    def export_sections_to_txt(self, output_dir = "sections_export"):
        """
        Exports each section as a string into its own text file. It recursively burrows
        through sections, meaning there will be duplication in the corpora.
        """
        sections = set([line["section"] for line in self.parse()])
        sections_tuple_list = [(section, self.collapse_section(section)) for section in sections]
        self.export_to_txt(output_dir, sections_tuple_list)

    def collapse_section(self, section_name):
        return " ".join([line['text'] for line in self.parse() if line["section"] == section_name])
 
    def export_to_txt(self, output_dir, tuple_list):
        """
        Creates an output directory and then creates a bunch of files based on
        a list of tuples of the format ("name", "text contents")
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for tuple in tuple_list:
            f = open("{0}/{1}.txt".format(output_dir, self.parameterize(str(tuple[0]))), "w")
            f.write(tuple[1])
            f.close()

    def to_csv(self, output):
        """
        Dumps all the data to a (tab-delimited) .csv
        """
        lines = self.parse()
        output.write("SECTION\tSPEAKER\tTEXT\n")
        for line in lines:
            output.write("{0}\t{1}\t{2}\n".format(line['section'], line['speaker'], line['text']))

    def parameterize(self, string):
        """
        Strips down a string to make a filename.
        """
        return "".join([c.lower() for c in string if c.isalpha() or c.isdigit()]).rstrip()


if __name__ == '__main__':
    cli()
