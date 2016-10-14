##	PETRreader.py [module]
##
# Dictionary and text input routines for the PETRARCH event coder
##
# CODE REPOSITORY: https://github.com/eventdata/PETRARCH
##
# SYSTEM REQUIREMENTS
# This program has been successfully run under Mac OS 10.10; it is standard Python 2.7
# so it should also run in Unix or Windows.
#
# INITIAL PROVENANCE:
# Programmer: Philip A. Schrodt
#			  Parus Analytics
#			  Charlottesville, VA, 22901 U.S.A.
#			  http://eventdata.parusanalytics.com
#
#
#             Clayton Norris
#             Caerus Associates/ University of Chicago
#
# GitHub repository: https://github.com/openeventdata/petrarch
#
# Copyright (c) 2014	Philip A. Schrodt.	All rights reserved.
#
# This project is part of the Open Event Data Alliance tool set; earlier developments
# were funded in part by National Science Foundation grant SES-1259190
#
# This code is covered under the MIT license
#
# Report bugs to: schrodt735@gmail.com
#
# REVISION HISTORY:
# 22-Nov-13:	Initial version
# Summer-14:	Numerous modifications to handle synonyms in actor and verb dictionaries
# 20-Nov-14:	write_actor_root/text added to parse_Config
# ------------------------------------------------------------------------

from __future__ import print_function
from __future__ import unicode_literals

import io
import re
import os
import sys
import math  # required for ordinal date calculations
import logging
import xml.etree.ElementTree as ET
from datetime import datetime

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

import PETRglobals
import utilities




# ================== STRINGS ================== #

ErrMsgMissingDate = "<Sentence> missing required date; record was skipped"


# ================== EXCEPTIONS ================== #

class DateError(Exception):  # invalid date
    pass

# ================== CONFIG FILE INPUT ================== #


def parse_Config(config_path):
    """
    Parse PETRglobals.ConfigFileName. The file should be ; the default is PETR_config.ini
    in the working directory but this can be changed using the -c option in the command
    line. Most of the entries are obvious (but will eventually be documented) with the
    exception of

    1. actorfile_list and textfile_list are comma-delimited lists. Per the usual rules
            for Python config files, these can be continued on the next line provided the
            the first char is a space or tab.

    2. If both textfile_list and textfile_name are present, textfile_list takes priority.
       textfile_list should be the name of a file containing text file names; # is allowed
       as a comment delimiter at the beginning of individual lines and following the file
       name.

    3. For additional info on config files, see
                    http://docs.python.org/3.4/library/configparser.html
       or try Google, but basically, it is fairly simple, and you can probably just
       follow the examples.
    """

    def get_config_boolean(optname):
        """ Checks for the option optname, prints outcome and returns the result.
        If optname not present, returns False """
        if parser.has_option('Options', optname):
            try:
                result = parser.getboolean('Options', optname)
                print(optname, "=", result)
                return result
            except ValueError:
                print(
                    "Error in config.ini: " +
                    optname +
                    " value must be `true' or `false'")
                raise
        else:
            return False

    print('\n', end=' ')
    parser = ConfigParser()
#		logger.info('Found a config file in working directory')
#	print "pc",PETRglobals.ConfigFileName
    confdat = parser.read(config_path)
    if len(confdat) == 0:
        print(
            "\aError: Could not find the config file:",
            PETRglobals.ConfigFileName)
        print("Terminating program")
        sys.exit()

    try:
        PETRglobals.VerbFileName = parser.get('Dictionaries', 'verbfile_name')
        PETRglobals.AgentFileName = parser.get(
            'Dictionaries',
            'agentfile_name')
#		print "pc",PETRglobals.AgentFileName
        PETRglobals.DiscardFileName = parser.get(
            'Dictionaries',
            'discardfile_name')

        direct = parser.get('StanfordNLP', 'stanford_dir')
        PETRglobals.stanfordnlp = os.path.expanduser(direct)

        filestring = parser.get('Dictionaries', 'actorfile_list')
        PETRglobals.ActorFileList = filestring.split(', ')

        # otherwise this was set in command line
        if len(PETRglobals.TextFileList) == 0:
            if parser.has_option('Options', 'textfile_list'):  # takes priority
                filestring = parser.get('Options', 'textfile_list')
                PETRglobals.TextFileList = filestring.split(', ')
            else:
                filename = parser.get('Options', 'textfile_name')
                try:
                    fpar = open(filename, 'r')
                except IOError:
                    print(
                        "\aError: Could not find the text file list file:",
                        filename)
                    print("Terminating program")
                    sys.exit()
                PETRglobals.TextFileList = []
                line = fpar.readline()
                while len(line) > 0:   # go through the entire file
                    if '#' in line:
                        line = line[:line.find('#')]
                    line = line.strip()
                    if len(line) > 0:
                        PETRglobals.TextFileList.append(line)
                    line = fpar.readline()
                fpar.close()


        if parser.has_option('Dictionaries', 'issuefile_name'):
            PETRglobals.IssueFileName = parser.get(
                'Dictionaries',
                'issuefile_name')

        if parser.has_option('Options', 'new_actor_length'):
            try:
                PETRglobals.NewActorLength = parser.getint(
                    'Options',
                    'new_actor_length')
            except ValueError:
                print(
                    "Error in config.ini Option: new_actor_length value must be an integer")
                raise
        print("new_actor_length =", PETRglobals.NewActorLength)

        PETRglobals.StoponError = get_config_boolean('stop_on_error')
        PETRglobals.WriteActorRoot = get_config_boolean('write_actor_root')
        PETRglobals.WriteActorText = get_config_boolean('write_actor_text')
        PETRglobals.WriteEventText = get_config_boolean('write_event_text')

        if parser.has_option(
                'Options', 'require_dyad'):  # this one defaults to True
            PETRglobals.RequireDyad = get_config_boolean('require_dyad')
        else:
            PETRglobals.RequireDyad = True

        # otherwise this was set in command line
        if len(PETRglobals.EventFileName) == 0:
            PETRglobals.EventFileName = parser.get('Options', 'eventfile_name')

        PETRglobals.CodeBySentence = parser.has_option(
            'Options',
            'code_by_sentence')
        print("code-by-sentence", PETRglobals.CodeBySentence)

        PETRglobals.PauseBySentence = parser.has_option(
            'Options',
            'pause_by_sentence')
        print("pause_by_sentence", PETRglobals.PauseBySentence)

        PETRglobals.PauseByStory = parser.has_option(
            'Options',
            'pause_by_story')
        print("pause_by_story", PETRglobals.PauseByStory)

        try:
            if parser.has_option('Options', 'comma_min'):
                PETRglobals.CommaMin = parser.getint('Options', 'comma_min')
            elif parser.has_option('Options', 'comma_max'):
                PETRglobals.CommaMax = parser.getint('Options', 'comma_max')
            elif parser.has_option('Options', 'comma_bmin'):
                PETRglobals.CommaBMin = parser.getint('Options', 'comma_bmin')
            elif parser.has_option('Options', 'comma_bmax'):
                PETRglobals.CommaBMax = parser.getint('Options', 'comma_bmax')
            elif parser.has_option('Options', 'comma_emin'):
                PETRglobals.CommaEMin = parser.getint('Options', 'comma_emin')
            elif parser.has_option('Options', 'comma_emax'):
                PETRglobals.CommaEMax = parser.getint('Options', 'comma_emax')
        except ValueError:
            print(
                "Error in config.ini Option: comma_*  value must be an integer")
            raise
        print("Comma-delimited clause elimination:")
        print("Initial :", end=' ')
        if PETRglobals.CommaBMax == 0:
            print("deactivated")
        else:
            print(
                "min =",
                PETRglobals.CommaBMin,
                "   max =",
                PETRglobals.CommaBMax)
        print("Internal:", end=' ')
        if PETRglobals.CommaMax == 0:
            print("deactivated")
        else:
            print(
                "min =",
                PETRglobals.CommaMin,
                "   max =",
                PETRglobals.CommaMax)
        print("Terminal:", end=' ')
        if PETRglobals.CommaEMax == 0:
            print("deactivated")
        else:
            print(
                "min =",
                PETRglobals.CommaEMin,
                "   max =",
                PETRglobals.CommaEMax)

    except Exception as e:
        print(
            'parse_config() encountered an error: check the options in',
            PETRglobals.ConfigFileName)
        print("Terminating program")
        sys.exit()
#		logger.warning('Problem parsing config file. {}'.format(e))


# ================== PRIMARY INPUT USING FIN ================== #


def open_FIN(filename, descrstr):
    # opens the global input stream fin using filename;
    # descrstr provides information about the file in the event it isn't found
    global FIN
    global FINline, FINnline, CurrentFINname
    try:
        FIN = io.open(filename, 'r', encoding='utf-8')
        CurrentFINname = filename
        FINnline = 0
    except IOError:
        print("\aError: Could not find the", descrstr, "file:", filename)
        print("Terminating program")
        sys.exit()


def close_FIN():
    # closes the global input stream fin.
    # IOError should only happen during debugging or if something has seriously gone wrong
    # with the system, so exit if this occurs.
    global FIN
    try:
        FIN.close()
    except IOError:
        print("\aError: Could not close the input file")
        print("Terminating program")
        sys.exit()


def read_FIN_line():
    """
    def read_FIN_line():
    Reads a line from the input stream fin, deleting xml comments and lines beginning with #
    returns next non-empty line or EOF
    tracks the current line number (FINnline) and content (FINline)
    calling function needs to handle EOF (len(line) == 0)
    """
    """
	Comments in input files:
	Comments should be delineated in the XML style (which is inherited from HTML which
	inherited it from SGML) are allowed, as long as you don't get too clever. Basically,
	anything that looks like any of these

		<!-- [comment] -->

		things I want to actually read <!-- [comment] -->

		some things I want <!-- [comment] --> and more of them

		<!-- start of the comment
		 [1 or more additional lines
	  	end of the comment -->

	is treated like a comment and skipped.

	Note: the system doesn't use the formal definition that also says '--' is not allowed
	inside a comment: it just looks for --> as a terminator

	The system is *not* set up to handle clever variations like nested comments,  multiple
	comments on a line, or non-comment information in multi-line comments: yes, we are
	perfectly capable of writing code that could handle these contingencies, but it
	is not a priority at the moment. We trust you can cope within these limits.

	For legacy purposes, the perl/Python one-line comment delimiter # the beginning of a
	line is also recognized.

	To accommodate my habits, the perl/Python one-line comment delimiter ' #' is also
	recognized at the end of a line and material following it is eliminated. Note that the
	initial space is required.

	Blank lines and lines with only whitespace are also skipped.
	"""
    global FIN
    global FINline, FINnline

    line = FIN.readline()
    FINnline += 1
    while True:
        #		print '==',line,
        if len(line) == 0:
            break  # calling function needs to handle EOF
        # deal with simple lines we need to skip
        if line[0] == '#' or line[0] == '\n' or line[
                0:2] == '<!' or len(line.strip()) == 0:
            line = FIN.readline()
            FINnline += 1
            continue
        if not line:  # handle EOF
            print("EOF hit in read_FIN_line()")
            raise EOFError
            return line
        if ('#' in line):
            line = line[:line.find('#')]
        if ('<!--' in line):
            if ('-->' in line):  # just remove the substring
                pline = line.partition('<!--')
                line = pline[0] + pline[2][pline[2].find('-->') + 3:]
            else:
                while ('-->' not in line):
                    line = FIN.readline()
                    FINnline += 1
                line = FIN.readline()
                FINnline += 1
        if len(line.strip()) > 0:
            break
        line = FIN.readline()
        FINnline += 1
#	print "++",line
    FINline = line
    return line


# ========================== TAG EVALUATION FUNCTIONS ========================== #

def find_tag(tagstr):
    # reads fin until tagstr is found
    # can inherit EOFError raised in PETRreader.read_FIN_line()
    line = read_FIN_line()
    while (tagstr not in line):
        line = read_FIN_line()


def extract_attributes(theline):
    # puts list of attribute and content pairs in the global AttributeList. First item is
    # the tag itself
    # If a twice-double-quote occurs -- "" -- this treated as "\"
    # still to do: need error checking here
    """
    Structure of attributes extracted to AttributeList
    At present, these always require a quoted field which follows an '=', though it
    probably makes sense to make that optional and allow attributes without content
    """
#	print "PTR-1:", theline,
    theline = theline.strip()
    if ' ' not in theline:  # theline only contains a keyword
        PETRglobals.AttributeList = theline[1:-2]
#		print "PTR-1.1:", PETRglobals.AttributeList
        return
    pline = theline[1:].partition(' ')  # skip '<'
    PETRglobals.AttributeList = [pline[0]]
    theline = pline[2]
    while ('=' in theline):  # get the field and content pairs
        pline = theline.partition('=')
        PETRglobals.AttributeList.append(pline[0].strip())
        theline = pline[2]
        pline = theline.partition('"')
        if pline[2][0] == '"':   # twice-double-quote
            pline = pline[2][1:].partition('"')
            PETRglobals.AttributeList.append('"' + pline[0] + '"')
            theline = pline[2][1:]
        else:
            pline = pline[2].partition('"')
            PETRglobals.AttributeList.append(pline[0].strip())
            theline = pline[2]
#	print "PTR-2:", PETRglobals.AttributeList


def check_attribute(targattr):
    """ Looks for targetattr in AttributeList; returns value if found, null string otherwise."""
# This is used if the attribute is optional (or if error checking is handled by the calling
# routine); if an error needs to be raised, use get_attribute()
    if (targattr in PETRglobals.AttributeList):
        return (
            PETRglobals.AttributeList[
                PETRglobals.AttributeList.index(targattr) + 1]
        )
    else:
        return ""


def get_attribute(targattr):
    """ Similar to check_attribute() except it raises a MissingAttr error when the attribute is missing."""
    if (targattr in PETRglobals.AttributeList):
        return (
            PETRglobals.AttributeList[
                PETRglobals.AttributeList.index(targattr) + 1]
        )
    else:
        #raise MissingAttr #commented by me
        return ""


# ================== ANCILLARY DICTIONARY INPUT ================== #

def read_discard_list(discard_path):
    """
    Reads file containing the discard list: these are simply lines containing strings.
    If the string, prefixed with ' ', is found in the <Text>...</Text> sentence, the
    sentence is not coded. Prefixing the string with a '+' means the entire story is not
    coded with the string is found [see read_record() for details on story/sentence
    identification]. If the string ends with '_', the matched string must also end with
    a blank or punctuation mark; otherwise it is treated as a stem. The matching is not
    case sensitive.

    The file format allows # to be used as a in-line comment delimiter.

    File is stored as a simple list and the interpretation of the strings is done in
    check_discards()

    ===== EXAMPLE =====
    +5K RUN #  ELH 06 Oct 2009
    +ACADEMY AWARD   # LRP 08 Mar 2004
    AFL GRAND FINAL   # MleH 06 Aug 2009
    AFRICAN NATIONS CUP   # ab 13 Jun 2005
    AMATEUR BOXING TOURNAMENT   # CTA 30 Jul 2009
    AMELIA EARHART
    ANDRE AGASSI   # LRP 10 Mar 2004
    ASIAN CUP   # BNL 01 May 2003
    ASIAN FOOTBALL   # ATS 9/27/01
    ASIAN MASTERS CUP   # CTA 28 Jul 2009
    +ASIAN WINTER GAMES   # sls 14 Mar 2008
    ATP HARDCOURT TOURNAMENT   # mj 26 Apr 2006
    ATTACK ON PEARL HARBOR   # MleH 10 Aug 2009
    AUSTRALIAN OPEN
    AVATAR   # CTA 14 Jul 2009
    AZEROTH   # CTA 14 Jul 2009  (World of Warcraft)
    BADMINTON  # MleH 28 Jul 2009
    BALLCLUB   # MleH 10 Aug 2009
    BASEBALL
    BASKETBALL
    BATSMAN  # MleH 14 Jul 2009
    BATSMEN  # MleH 12 Jul 2009


    """

    logger = logging.getLogger('petr_log')
    logger.info("Reading " + PETRglobals.DiscardFileName)
    open_FIN(discard_path, "discard")

    line = read_FIN_line()
    while len(line) > 0:  # loop through the file
        if '#' in line:
            line = line[:line.find('#')]
        targ = line.strip()
        if targ.startswith('+'):
            targ = targ[1:].upper() + ' +'
        else:
            targ = targ.upper() + ' $'

        targ = targ.split()
        prev = targ[0]       # Add words to search tree
        targ = targ[1:]
        list = PETRglobals.DiscardList.setdefault(prev, {})
        while targ != []:
            list = list.setdefault(targ[0], {})
            targ = targ[1:]

        line = read_FIN_line()
    close_FIN()


def read_issue_list(issue_path):
    """
    "Issues" do simple string matching and return a comma-delimited list of codes.
    The standard format is simply
            <string> [<code>]
    For purposes of matching, a ' ' is added to the beginning and end of the string: at
    present there are not wild cards, though that is easily added.

    The following expansions can be used (these apply to the string that follows up to
    the next blank)
            n: Create the singular and plural of the noun
            v: Create the regular verb forms ('S','ED','ING')
            +: Create versions with ' ' and '-'

    The file format allows # to be used as a in-line comment delimiter.

    File is stored in PETRglobals.IssueList as a list of tuples (string, index) where
    index refers to the location of the code in PETRglobals.IssueCodes. The coding is done
    in check_issues()

    Issues are written to the event record as a comma-delimited list to a tab-delimited
    field, e.g.

    20080801	ABC	EDF	0001	POSTSECONDARY_EDUCATION 2, LITERACY 1	AFP0808-01-M008-02
    20080801	ABC	EDF	0004		AFP0808-01-M007-01
    20080801	ABC	EDF	0001	NUCLEAR_WEAPONS 1	AFP0808-01-M008-01

    where XXXX NN, corresponds to the issue code and the number of matched phrases in the
    sentence that generated the event.

    This feature is optional and triggered by a file name in the PETR_config.ini file at

            issuefile_name = Phoenix.issues.140225.txt

    <14.02.28> NOT YET FULLY IMPLEMENTED
    The prefixes '~' and '~~' indicate exclusion phrases:
            ~ : if the string is found in the current sentence, do not code any of the issues
                    in section -- delimited by <ISSUE CATEGORY="...">...</ISSUE> -- containing
                    the string
            ~~ : if the string is found in the current *story*, do not code any of the issues
                    in section
    In the current code, the occurrence of an ignore phrase of either type cancels all
    coding of issues from the sentence

    ===== EXAMPLE =====

    <ISSUE CATEGORY="ID_ATROCITY">
    n:atrocity [ID_ATROCITY]
    n:genocide [ID_ATROCITY]
    ethnic cleansing [ID_ATROCITY]
    ethnic v:purge [ID_ATROCITY]
    ethnic n:purge [ID_ATROCITY]
    war n:crime [ID_ATROCITY]
    n:crime against humanity [ID_ATROCITY]
    n:massacre [ID_ATROCITY]
    v:massacre [ID_ATROCITY]
    al+zarqawi network [NAMED_TERROR_GROUP]
    ~Saturday Night massacre
    ~St. Valentine's Day massacre
    ~~Armenian genocide  # not coding historical cases
    </ISSUE>

    """
    PETRglobals.IssueList = {}
    logger = logging.getLogger('petr_log')
    logger.info("Reading " + PETRglobals.IssueFileName)
    open_FIN(issue_path, "issues")

    PETRglobals.IssueCodes.append('~')  # initialize the ignore codes
    PETRglobals.IssueCodes.append('~~')

    line = read_FIN_line()
    while len(line) > 0:  # loop through the file
        if '#' in line:
            line = line[:line.find('#')]
        if line[0] == '~':  # ignore codes are only partially implemented
            if line[1] == '~':
                target = line[2:].strip().upper()
                codeindex = 1
            else:
                target = line[1:].strip().upper()
                codeindex = 0
        else:
            if '[' not in line:  # just do the codes now
                line = read_FIN_line()
                continue
            code = line[line.find('[') + 1:line.find(']')]  # get the code
            if code in PETRglobals.IssueCodes:
                codeindex = PETRglobals.IssueCodes.index(code)
            else:
                PETRglobals.IssueCodes.append(code)
                codeindex = len(PETRglobals.IssueCodes) - 1
            target = line[:line.find('[')].strip().upper()

        forms = [target]
        madechange = True
        while madechange:  # iterate until no more changes to make
            ka = 0
            madechange = False
            while ka < len(forms):
                if '+' in forms[ka]:
                    str = forms[ka]
                    forms[ka] = str.replace('+', ' ', 1)
                    forms.insert(ka + 1, str.replace('+', '-', 1))
                    madechange = True
                if 'N:' in forms[ka]:  # regular noun forms
                    part = forms[ka].partition('N:')
                    forms[ka] = part[0] + part[2]
                    plur = part[2].partition(' ')
                    if 'Y' == plur[0][-1]:
                        plural = plur[0][:-1] + 'IES'
                    else:
                        plural = plur[0] + 'S'
                    forms.insert(ka + 1, part[0] + plural + ' ' + plur[2])
                    madechange = True
                if 'V:' in forms[ka]:  # regular verb forms
                    part = forms[ka].partition('V:')
                    forms[ka] = part[0] + part[2]
                    root = part[2].partition(' ')
                    vscr = root[0] + "S"
                    forms.insert(ka + 1, part[0] + vscr + ' ' + root[2])
                    if root[0][-1] == 'E':  # root ends in 'E'
                        vscr = root[0] + "D "
                        forms.insert(ka + 2, part[0] + vscr + ' ' + root[2])
                        vscr = root[0][:-1] + "ING "
                    else:
                        vscr = root[0] + "ED "
                        forms.insert(ka + 2, part[0] + vscr + ' ' + root[2])
                        vscr = root[0] + "ING "
                    forms.insert(ka + 3, part[0] + vscr + ' ' + root[2])
                    madechange = True

                ka += 1

        for item in forms:
            segs = item.split()+['#']
            path = PETRglobals.IssueList
            while not segs == ['#']:
                path = path.setdefault(segs[0],{})
                segs = segs[1:]
            path[segs[0]] = codeindex
        line = read_FIN_line()
    close_FIN()

    """ debug
	ka = 0
	while ka < 128 :
		print PETRglobals.IssueList[ka],PETRglobals.IssueCodes[PETRglobals.IssueList[ka][1]]
		ka += 1
	"""

# ================== VERB DICTIONARY INPUT ================== #



def make_plural_noun(noun):
   
    """ Create the plural of a synonym noun st """
    
    if noun[-1] == '_' or noun[0] == '{':
        return None
    if 'Y' == noun[-1]:
        return noun[:-1] + 'IES'
    elif 'S' == noun[-1]:
        return noun[:-1] + 'ES'
    else:
        return noun + 'S'



def read_verb_dictionary(verb_path):

    """


    Verb storage:  
    
        Storage sequence:
        
                Upper Noun phrases
                    |
                Upper prepositional phrases
                    *
                Lower noun phrases
                    |
                Lower prepositional phrases
                    #
                    
        - symbol acts as extender, indicating the noun phrase is longer
        , symbol acts as delimiter between several selected options
        
    """

    logger = logging.getLogger('petr_log')
    logger.info("Reading " + PETRglobals.VerbFileName)
    file = open(verb_path,'r')

    block_meaning = ""
    block_code = ""
    record_patterns = 1
    synsets = {}
    syn  =1
    
    
    def resolve_synset(line):
    
        segs = line.split()
        #print(line)
        syns = filter(lambda a: a.startswith('&'), segs)
        lines = []
        if syns:
            set = syns[0].replace("{","").replace("}","").replace("(","").replace(")","")
            if set in synsets:
                for word in synsets[set]:
                    #print(word)
                    lines += resolve_synset(line.replace(set,word,1))
                    plural = make_plural_noun(word)
                    if plural :
                        lines+=resolve_synset(line.replace(set,plural,1))
                return lines
            else:
                print("Undefined synset", set)
        return [line]
    
    

    def resolve_patseg(segment):
        prepphrase = 0
        nounphrase = 0
        nps = []
        head = ""
        modifiers = []
        index = 0
        prepstarts=[]
        prepends=[]
        
        
        for element in segment:
            
            # SKIP OVER PREPS, We consider these later
            if element.endswith(")"):
                prepends.append(index)
                if element.startswith("("):
                    prepstarts.append(index)
                prepphrase = 0
            
            elif element.startswith("("):
                prepstarts.append(index)
                prepphrase = 1
            
            elif not prepphrase:
                # Find noun phrases
                if element.endswith("}"):
                    nounphrase = 0
                    head = element[:-1]
                    nps.append((head,modifiers))
                    modifiers = []
                elif nounphrase:
                    modifiers.append(element)
                elif element.startswith("{"):
                    modifiers.append(element[1:])
                    nounphrase = 1
                else:
                    nps.append(element)
                    
            index += 1
            
        preps = map(lambda a: segment[a[0]:a[1]+1], zip(prepstarts,prepends))
        prep_pats = []
        for phrase in preps:
            phrase = map(lambda a: a.replace("(","").replace(")",""), phrase)
            p = phrase[0]
            pnps = []
            pmodifiers = []
            if len(phrase)> 1:
                
                head = ""
                for element in phrase[1:]:
                    # Find noun phrases
                    if element.endswith("}"):
                        nounphrase = 0
                        head = element[:-1]
                        pnps.append((head,pmodifiers))
                        pmodifiers = []
                    elif nounphrase:
                        pmodifiers.append(element)
                    elif element.startswith("{"):
                        pmodifiers.append(element[1:])
                        nounphrase = 1
                    else:
                        pnps.append(element)
            prep_pats.append((p,pnps))
        return nps,prep_pats



    for line in file:
        if line.startswith("<!"):
            record_patterns= 0
            continue
        elif line.startswith("####### VERB PATTERNS #######"):
            syn = 0
        if not line.strip():
            continue
        if line.startswith("---"):
            segs = line.split()
            block_meaning  = segs[1]
            block_code = segs[2]
        elif line.startswith("-"):
            if not record_patterns:
                continue
            dict_entry = {}
            pattern = line[1:].split("#")[0]
            #print(line)
            for pat in resolve_synset(pattern):
            
                segs = pat.split("*")
                
                pre = segs[0].split()
                pre = resolve_patseg(pre)
                post = segs[1].split()
                code = post.pop()
                post = resolve_patseg(post)
                
                path =  PETRglobals.VerbDict['phrases'].setdefault(block_meaning,{})
                if not pre == ([],[]):
                    if pre[0]:
                        count = 1
                        
                        for noun in pre[0]:
                            if not isinstance(noun,tuple):
                                path  = path.setdefault(noun,{})
                            else:
                                head = noun[0]
                                path = path.setdefault(head,{})
                                for element in noun[1]:
                                    path = path.setdefault("-",{})
                                    path = path.setdefault(element,{})
                            
                            path = path.setdefault(",",{}) if not count == len(pre[0]) else path
                            count += 1
                
                    if pre[1]:
                        path = path.setdefault("|",{})
                        for phrase in pre[1]:
                            head = phrase[0]
                            path = path.setdefault(head,{})
                            count = 1
                            for noun in phrase[1]:
                                if not isinstance(noun,tuple):
                                    path = path.setdefault("-",{})
                                    path  = path.setdefault(noun,{})
                                else:
                            
                                    head = noun[0]
                                    path = path.setdefault(head,{})
                                    for element in noun[1]:
                                        path = path.setdefault("-",{})
                                        path = path.setdefault(element,{})
                                path = path.setdefault(",",{}) if not count == len(phrase[1]) else path
                                count += 1
                
                if not post == ([],[]):
                    path = path.setdefault('*',{})
                    if post[0]:
                        count = 1
                        for noun in post[0]:
                            if not isinstance(noun,tuple):
                                path  = path.setdefault(noun,{})
                            else:
                        
                                head = noun[0]
                                path = path.setdefault(head,{})
                                for element in noun[1]:
                                    path = path.setdefault("-",{})
                                    path = path.setdefault(element,{})
                                
                            path = path.setdefault(",",{}) if not count == len(post[0]) else path
                
                    if post[1]:
                        for phrase in post[1]:
                            head = phrase[0]
                            path = path.setdefault("|",{})
                            path = path.setdefault(head,{})
                            count = 1
                            for noun in phrase[1]:
                                if not isinstance(noun,tuple):
                                    path = path.setdefault("-",{})
                                    path  = path.setdefault(noun,{})
                                else:
                                    head = noun[0]
                                    path = path.setdefault("-",{})
                                    path = path.setdefault(head,{})
                                    for element in noun[1]:
                                        path = path.setdefault("-",{})
                                        path = path.setdefault(element,{})
                                path = path.setdefault(",",{}) if not count == len(phrase[1]) else path
                                count += 1

                path["#"] = {'code' : code[1:-1], 'line' : line[:-1]}
        elif syn and line.startswith("&"):
            block_meaning = line.strip()
        elif syn and line.startswith("+"):
            term = line.strip()[1:]
            if "_" in term:
                if len(term.replace("_"," ").split()) > 1:
                    term = "{" + term.replace("_"," ") + "}"
                else:
                    term = term.replace("_"," ")
            synsets[block_meaning] = synsets.setdefault(block_meaning,[]) + [term]
        elif line.startswith("~"):
            # VERB TRANSFORMATION
            p = line[1:].replace("(","").replace(")","")
            segs = p.split("=")
            pat = segs[0].split()
            answer = segs[1].split()
            ev2 = pat
            path = PETRglobals.VerbDict['transformations']
            while len(ev2) > 1:
                source = ev2[0]
                verb = reduce(lambda a,b : a + b ,
                    map(lambda c: utilities.convert_code(PETRglobals.VerbDict['verbs'][c]['#']['#']['code'])[0] if not c== "Q" else -1,
                    ev2[-1].split("_")), 0)
                
                path = path.setdefault(verb,{})
                path = path.setdefault(source,{})
                ev2 = ev2[1:-1]
            path[ev2[0]] = [answer,line]

        else:
            # Add synonyms
            word = line.split("#")[0]
            words = word.replace("}","").replace("{","").split()
            if not words:
                continue
        
            code = block_code
            front = []
            back  = []
            compound = 0
            stem = words[0]
            if "_" in stem:
                # We're dealing with a compound verb
#                print(stem)
                segs = stem.split('+')
                front = segs[0].split('_')
                back = segs[1].split('_')[1:]
                stem = segs[1].split('_')[0]
                compound = 1
            
            if words[-1].startswith("["):
                code = words.pop()

            
            if not (len(words) > 1 or '{' in word):
                
                if stem.endswith("S") or stem.endswith("X") or stem.endswith("Z"):
                     words.append(stem + "ES")
                elif stem.endswith("Y"):
                    words.append(stem[:-1] + "IES")
                else:
                    words.append(stem + "S")
                
                if stem.endswith("E"):
                    words.append(stem + "D")
                else:
                    words.append(stem+"ED")
                
                if stem.endswith("E") and not stem[-2] in "AEIOU":
                    words.append(stem[:-1] + "ING")
                else:
                    words.append(stem + "ING")
        
            for w in words:
                wstem = w
                if "_" in w:
                    segs = w.split('+')
                    front = segs[0].split('_')
                    back = segs[1].split('_')[1:]
                    
                    wstem = segs[1].split('_')[0]

                path = PETRglobals.VerbDict['verbs']
                path = path.setdefault(wstem,{})
                for item in back:
                    if not item:
                        continue
                    path = path.setdefault(item,{})
                path = path.setdefault("#",{})
                for item in front:
                    if not item:
                        continue
                    path = path.setdefault(item,{})
                path = path.setdefault("#",{'code':code[1:-1],'meaning':block_meaning,'line':line[:-1]})



    #print(sorted(PETRglobals.VerbDict['phrases'].keys()))
    #print(PETRglobals.VerbDict.__sizeof__())
    #print(PETRglobals.VerbDict['phrases'].__sizeof__())
    #exit()
    #for root , k in sorted(PETRglobals.VerbDict['verbs'].items()):
    #    print(root)
    #    print("\t",k)





def _read_verb_dictionary(verb_path):
    """ Reads the verb dictionary from VerbFileName """

    """
    ======= VERB DICTIONARY ORGANIZATION =======

    The verb dictionary consists of a set of synsets followed by a series of verb
    synonyms and patterns, followed by a list of verb transformations.

    VERB SYNONYM BLOCKS AND PATTERNS

    A verb synonym block is a set of verbs which are synonymous (or close enough) with
    respect to the patterns. The program automatically generates the regular forms of the
    verb -- endings of 'S','ED' and 'ING' -- if it is regular (and, implicitly, English);
    otherwise the irregular forms can be specified in {...} following the primary verb.
    Note that if irregular forms are provided in {...}, ALL forms need to be included,
    even if some of those are the same as the regular form (in other words, no
    alternative forms are generated when {...} is present). An optional code for the
    isolated verb can follow in [...].

    The verb block begins with a comment of the form

    --- <GENERAL DESCRIPTION> [<CODE>] ---

    where the "---" signals the beginning of a new block. The code in [...] is the
    primary code -- typically a two-digit+0 cue-category code -- for the block, and this
    will be used for all other verbs unless these have their own code. If no code is
    present, this defaults to the null code "---"  which indicates that the isolated verb
    does not generate an event. The null code also can be used as a secondary code.

    This is followed by a set of patterns -- these begin with '-' -- which generally
    follow a syntax that is based on that of TABARI patterns, but contains more grammatical
    information. Patterns now have four sections: 
    
    - Pre-Verb Nouns (Pre-Verb Prep Phrases) * Post-Verb Nouns (Post-Verb Prep Phrases)
    
    These contain several symbolic annotations:
    
        ()  Parentheses indicate a Prepositional phrase. The first word is the preposition,
            followed by the noun(s) that it governs
        
        Single words without annotation denote nouns. These are the "heads" of the phrases they
            represent.
            
        {}  Brackets denote a longer noun phrase. The last word in the brackets will be the head,
            remaining words are descriptors.
        
        +$  In rare cases, the + and $ symbols will be used to mark target and source respectively.
            These should only be used in instances where it would be possible to confuse one with 
            the other going strictly off syntactic information, such as both would occur after the verb
            in prepositional phrases
            

    MULTIPLE-WORD VERBS
    Multiple-word "compound verbs" such as "CORDON OFF", "WIRE TAP" and "BEEF UP" are entered by
    connecting the word with an underscore (these must be consecutive) and putting a '+'
    in front of the word -- only the first and last are currently allowed -- of the
    phrase that TreeBank is going to designate as the verb.If there is no {...}, regular
    forms are constructed for the word designated by '+'; otherwise all of the irregular
    forms are given in {...}. If you can't figure out which part of the phrase is the
    verb, the phrase you are looking at is probably a noun, not a verb. Multi-word verbs
    are treated in patterns just as single-word verbs are treated.

    Examples
    +BEEF_UP
    RE_+ARREST
    +CORDON_OFF {+CORDONED_OFF +CORDONS_OFF +CORDONING_OFF}
    +COME_UPON {+COMES_UPON +CAME_UPON +COMING_UPON}
    WIRE_+TAP {WIRE_+TAPS WIRE_+TAPPED  WIRE_+TAPPING }

    Multi-words are stored in a list consisting of
        code
        primary form (use as a pointer to the pattern
        tuple: (True if verb is at start of phrase, False otherwise; remaining words)

    [15.04.30]
    If a word occurs both as the verb in a multi-word and as a single word, it will be at
    the end of the list of multi-word candidate strings: that is, the multi-world
    combinations are checked first, then only if none of these match is the single word
    option used. Due to sub-optimized code, words that are the verb in a multi-word verb
    cannot be the first word in a block of verbs. The current dictionary has removed
    all of these.

    SYNSETS
    Synonym sets (synsets) are labelled with a string beginning with & and defined using
    the label followed by a series of lines beginning with + containing words or phrases.
    The phrases are interpreted as requiring consecutive words; the words can be separated
    with either spaces or underscores (they are converted to spaces). Synset phrases can
    only contain words, not $, +, % or ^ tokens or synsets. At present, a synsets cannot
    contain another synset as an element. [see note below] Synsets be used anywhere in a
    pattern that a word or phrase can be used. A synset must be defined before it is used:
    a pattern containing an undefined synset will be ignored -- but those definitions can
    occur anywhere in the file.

    Plurals are generated automatically using the rules in read_verb_dictionary/
    make_plural(st) except when

      -- The phrase ends with '_'

      -- The label ends with '_', in which case plurals are not generated for any of the
         phrases; this is typically used for synonyms that are not nouns

    The '_' is dropped in both cases

    ====== EXAMPLE =====

    &CURRENCY
    +DOLLARS
    +EUROS
    +AUSTRIAN FLORIN
    +GOLDEN_GOBLIN_GALLEONS_
    +PESO
    +KRONER_
    +YUM YENNYEN
    +JAVANESE YEN
    +SWISS FRANCS
    +YEN

    &ALTCURR
    +BITCOIN
    +PIRATE GOLD_
    +LEPRECHAUN GOLD_

    &AUXVERB3_
    +HAVE
    +HAS
    +HAD


    --- GRANT [070] ---
    GRANT
    GIVE {GAVE GIVEN GIVING }  # jw  11/14/91
    CONTRIBUTE # tony  3/12/91
    - * &CURRENCY [903] # -PAS 12.01.12
    - * &ALTCURR [904] # -PAS 14.05.08
    - * RUPEES  [071]


    --- EXPLAIN_VERBAL [010] ---
    EXPLAIN
    COMMENT
    ASSERT
    SAY  {SAID SAYING }
    CLARIFY {CLARIFIES CLARIFIED CLARIFYING} [040]
    CLEAR_UP
    - * RESTORATION RELATIONS [050:050]  # ANNOUNCE <ab 02 Dec 2005>
    - * COMMIT &MILITARY TO + [0332]  # SAY <sls 13 Mar 2008>
    - * ATTACK ON + AS &CRIME [018]  # DESCRIBE <ab 31 Dec 2005>
    - * &CURRENCY DEBT_RELIEF [0331]  # ANNOUNCE <ab 02 Dec 2005>  , ANNOUNCE
    - * WELCOMED OFFER FROM + [050]  # ANNOUNCE <ab 02 Dec 2005>
    - * + THAT $ WILL PULLOUT [0356]  # INFORM <sms 30 Nov 2007>
    - * POSSIBILITY OF &FIGHT [138]  # MENTION <OY 11 Mar 2006>
    - * AGREED JOIN COALITION [031]  # ANNOUNCE <OY 15 Mar 2006>
    - * TRACES RESPONSIBILITY [112]  # REPORT
    - CONFIRMED * OF BOMBINGS [010]  # REPORT
    - * INITIATIVE END &FIGHT [036]  # ANNOUNCE <ab 02 Dec 2005>

    &TESTSYN3
        +TO THE END
    +TO THE DEATH
    +UNTIL HELL FREEZES OVER

    &TESTSYN4
    +TO THE END OF THE EARTH
    +TO THE DEATH

    --- VOW  [170] ---
    VOW ;tony  3/9/91
    - * RESIST &TESTSYN3 [113] ; pas 4/20/03
    - * RESIST &TESTSYN4  [115] ; pas 4/20/03
    - * RESISTANCE TO THE INVADING  [114] ; pas 4/20/03
    - * RESIST  [112] ;tony  4/29/91
    - * WAR  [173] ;tony  4/22/91

    PROGRAMMING NOTES

    Notes
    1.  TABARI allowed recursive synsets -- that is, synsetS embedded in patterns and other
        synsets. It should be possible to do this fairly easily, at least with basic
        synsets as elements (not as patterns) but a simple call in syn_match(isupperseq)
        was not sufficient, so this needs more work.

    2.  For TABARI legacy purposes, the construction "XXXX_ " is converted to "XXXX ",
        an open match.  However, per the comments below, generally TABARI dictionaries
        should be converted before being used with PETRARCH.

    3. The verb dictionary is stored as follows:
        [0] True: primary form
        [1] Code
        [2:n] 3-lists of multi-words: [code, primary form (use as a pointer to the pattern
              list, tuple of words -- see store_multi_word_verb(loccode):)
        [n:] 3-lists of lower pattern, upper pattern and code. Upper pattern is stored
             in reverse order

        [0] False
        [1]: optional verb-specific code (otherwise use the primary code)
        [2]: primary form (use as a pointer to the pattern list)

    VERB DICTIONARY DIFFERENCES FROM TABARI

    On the *very* remote chance -- see Note 1 -- that you are trying to modify a TABARI
    .verbs dictionary to the PETRARCH format, the main thing you will need to eliminate
    are stemmed words:  PETRARCH only works with complete words. On the positive side,
    PETRARCH will only look at string as a "verb" if it has been identified as such by
    the parser -- that is, it is preceded with (VP and a tag that starts with (VB, so
    the [numerous] patterns required for noun/verb disambiguation are no longer
    needed. PETRARCH also does not allow disconjunctive sets in patterns: to accommodate
    legacy dictionaries, patterns containing these are skipped, but in order to work,
    these should be replaced with synsets. Also see additional remarks at the beginning
    of the file.

    The other big difference between PETRARCH and TABARI is verb-noun disambiguation:
    the pattern-based approach of TABARI needed a lot of information to insure that a
    word that *might* be a verb was, in fact, a verb (or was a noun that occurred in a
    context where it indicated an event anyway: TABARI's [in]famous tendency to code the
    right thing for the wrong reason). PETRARCH, in contrast, only looks as a verb when
    the parsing has identified it as, in fact, a verb. This dramatically reduces false
    positives and eliminates the need for any pattern which was required simply for
    disambiguation, but it also means that PETRARCH is a lot more discriminating about
    what actually constitutes an event. The big difference here is that verb-only
    codes are the norm in PETRARCH dictionaries but the exception in TABARI dictionaries.

    The active PETRARCH verbs dictionary has been extensively reorganized into both
    verb and noun synonym sets, and you are probably better off adding vocabulary to
    this [see Note 1] than converting a dictionary, but it can be done. An unconverted
    TABARI dictionary, on the other hand, will generally not work particularly well with
    PETRARCH.

    Note 1.

    Yeah, right. Every project we've encountered -- including those lavishly funded by
    multiple millions of taxpayers dollars and those allegedly producing multiple millions
    of events -- has regarded the NSF-funded CAMEO verbs dictionaries as a sacred artifact
    of the [infamous] Data Fairy, lowered from Asgaard along the lines of this

    http://www.wikiart.org/en/jacob-jordaens/allegory-of-the-peace-of-westphalia-1654

    [not exactly sure where the .verbs file is in that painting, but it must be in
    there somewhere]

    but then subsequently subject said dictionaries to bitter complaints that they aren't
    coding comprehensively.

    Look, dudes and dudettes, these dictionaries have been open source for about as long
    as the US has been at war in Afghanistan -- which is to say, a really long time -- and
    if you don't like how the coding is being done, add some new open-source vocabulary
    to the dictionaries instead of merely parasitizing the existing work. Dudes.

    The *real* problem, one suspects, is embodied in the following nugget of wisdom:

    Opportunity is missed by most people because it is dressed in overalls and looks
    like work.
    Thomas A. Edison

    Dudes.

    """
    global theverb, verb  # <14.05.07> : not needed, right?
    PETRglobals.VerbDict = {'verbs': {}, 'phrases': {}}

    def add_dict_tree(targ, verb, meaning="", code='---',
                      upper=[], synset=False, dict='phrases', line=""):
        # DOUBLE CHECK THAT VERB =/= targ[0]
        prev = verb
        list = PETRglobals.VerbDict[dict].setdefault(verb, {})
        while targ != []:
            if targ[0] in [' ', '']:
                targ = targ[1:]
                continue

            # Put synset trees in their own bin so we can
            if targ[0][0] == '&':
                list = list.setdefault(
                    'synsets',
                    {})   # consider this case later
            list = list.setdefault(targ[0], {})
            targ = targ[1:]

        list["#"] = list.setdefault(
            "#",
            {})  # termination symbol for the lower phrase

        list = list["#"]

        targ = upper
        while targ != []:
            if targ[-1] in [' ', '']:
                targ = targ[:-1]
                continue

            # Put synset trees in their own bin so we can
            if targ[-1][0] == '&':
                list = list.setdefault(
                    'synsets',
                    {})   # consider this case later
            list = list.setdefault(targ[-1], {})
            targ = targ[:-1]

        list['#'] = {'meaning': meaning, 'code': code, 'line': line}

    def make_phrase_list(thepat):
        """ Converts a pattern phrase into a list of alternating words and connectors """
        if len(thepat) == 0:
            return []
        phlist = []
        start = 0
        maxlen = len(thepat) + 1  # this is just a telltail
        while start < len(thepat):  # break phrase on ' ' and '_'
            spfind = thepat.find(' ', start)
            if spfind == -1:
                spfind = maxlen
            unfind = thepat.find('_', start)
            if unfind == -1:
                unfind = maxlen
            # somehow think I don't need this check...well, I just need the
            # terminating point, still need to see which is lower
            if unfind < spfind:
                phlist.append(thepat[start:unfind])
                start = unfind + 1
            else:
                phlist.append(thepat[start:spfind])
                phlist.append(' ')
                start = spfind + 1
                # check for missing synsets
        ka = 0
        while ka < len(phlist):
            if len(phlist[ka]) > 0:
                if (phlist[ka][0] == '&') and (
                        phlist[ka] not in PETRglobals.VerbDict):
                    print("WTF", phlist[ka])
                    print(sorted(PETRglobals.VerbDict.keys()))
                    exit()

                    logger.warning("Synset " + phlist[ka] +
                                   " has not been defined; pattern skipped")
                    raise ValueError  # this will do...
            ka += 2
        return phlist

    def get_verb_forms(loccode, line):
        """  Read the irregular forms of a verb. """
        # need error checking here
        global verb, theverb

        forms = verb[verb.find('{') + 1:verb.find('}')].split()
        for wrd in forms:
            vscr = wrd
            add_dict_tree([], vscr, theverb, loccode, dict='verbs', line=line)

    def store_multi_word_verb(loccode, line):
        """  Store a multi-word verb and optional irregular forms. """
        global verb, theverb

        if '{' in verb:
            forms = verb[verb.find('{') + 1:verb.find('}')].split()
            forms.append(verb[:verb.find('{')].strip())
        else:
            forms = [verb]
            # add the regular forms to the verb designated by '+'
            plind = verb.index('+') + 1
            if verb.find('_', plind) > 0:
                vroot = verb[plind:verb.find('_', plind)]
            else:
                vroot = verb[plind:]
            forms.append(verb.replace(vroot, vroot + "S"))
            if vroot[-1] == 'E':  # root ends in 'E'
                forms.append(verb.replace(vroot, vroot + "D"))
                forms.append(verb.replace(vroot, vroot[:-1] + "ING"))
            else:
                forms.append(verb.replace(vroot, vroot + "ED"))
                forms.append(verb.replace(vroot, vroot + "ING"))

        for phrase in forms:
            if '+' in phrase:  # otherwise not in correct form so skip it
                words = phrase.split('_')

                multilist = []
                upper = []
                phrase
                if words[0].startswith('+'):
                    multilist = [True]
                    for ka in range(1, len(words)):
                        multilist.append(words[ka])
                    targverb = words[0][1:]

                else:
                    upper = [False]
                    for ka in range(2, len(words) + 1):

                        upper.append(words[len(words) - ka])
                    targverb = words[len(words) - 1][1:]

                add_dict_tree(
                    multilist[
                        1:], targverb, theverb, loccode, upper=upper[
                        1:], dict='verbs', line=line)

            else:
                logger.warning(
                    'Error in read_verb_dictionary()/store_multi_word_verb(): ' +
                    phrase +
                    ' in ' +
                    verb +
                    ' is part of a multi-word verb and should contain a +; this was skipped')

    def make_verb_forms(loccode, line):
        """ Create the regular forms of a verb. """
        global verb, theverb
        vroot = verb
        vscr = vroot + \
            "S" if vroot[-1] not in ["S", "X", "Z"] else vroot + "ES"
        add_dict_tree([], vscr, theverb, loccode, dict='verbs', line=line)
        if vroot[-1] == 'E':  # root ends in 'E'
            vscr = vroot + "D"

            add_dict_tree([], vscr, theverb, loccode, dict='verbs', line=line)

            vscr = vroot[:-1] + "ING"

        else:
            vscr = vroot + "ED"  # if vroot[-1] not == "Y" else vroot[-1]+"IES"

            add_dict_tree([], vscr, theverb, loccode, dict='verbs', line=line)
            vscr = vroot + "ING"

        add_dict_tree([], vscr, theverb, loccode, dict='verbs', line=line)

    def make_plural(st):
        """ Create the plural of a synonym noun st """

        if 'Y' == st[-1]:
            return st[:-1] + 'IES'  # space is added below
        elif 'S' == st[-1]:
            return st[:-1] + 'ES'
        else:
            return st + 'S'

    # note that this will be ignored if there are no errors
    logger = logging.getLogger('petr_log')
    logger.info("Reading " + PETRglobals.VerbFileName)
    open_FIN(verb_path, "verb")

    theverb = ''
    newblock = False
    ka = 0   # primary verb count ( debug )
    line = read_FIN_line()
    while len(line) > 0:  # loop through the file

        if '[' in line:
            part = line.partition('[')
            verb = part[0].strip()
            code = part[2][:part[2].find(']')]
        else:
            verb = line.strip()
            code = ''
        if verb.startswith('---'):  # start of new block
            if len(code) > 0:
                primarycode = code
            else:
                primarycode = '---'
            newblock = True
            line = read_FIN_line()

        elif verb[0] == '-':   # pattern

            # TABARI legacy: currently aren't processing these
            if '{' in verb:
                line = read_FIN_line()
                continue
            # resolve the ambiguous '_ ' construction to ' '

            verb = verb.replace('_ ', ' ')
            if verb[-1] == "_":
                verb = verb[:-1]
            targ = verb[1:].partition('*')
            try:
                highpat = make_phrase_list(targ[0].lstrip())
                lowphrase = targ[2].rstrip()
                if len(lowphrase) == 0:
                    lowpat = []
                else:
                    lowpat = [targ[2][0]]   # start with connector
                    loclist = make_phrase_list(lowphrase[1:])
                    lowpat.extend(loclist[:-1])   # don't need the final blank

                add_dict_tree(lowpat, theverb, "", code, highpat, line=line)

            except ValueError:
                # just trap the error, which will skip the line containing it
                pass
            line = read_FIN_line()

        elif verb[0] == '&':  # Read and store a synset.

            if verb[-1] == '_':
                noplural = True
                verb = verb[:-1]  # remove final blank and _
            else:
                noplural = False
            PETRglobals.VerbDict[verb] = {}
            line = read_FIN_line()
            while line[0] == '+':
                wordstr = line[1:].strip()
                if noplural or wordstr[-1] == '_':
                    wordstr = wordstr.strip().replace('_', ' ')
                    add_dict_tree(
                        wordstr.split(),
                        verb,
                        synset=True,
                        dict='verbs',
                        line=line)
                else:
                    wordstr = wordstr.replace('_', ' ')
                    add_dict_tree(
                        wordstr.split(),
                        verb,
                        synset=True,
                        dict='verbs',
                        line=line)
                    add_dict_tree(
                        make_plural(wordstr).split(),
                        verb,
                        synset=True,
                        dict='verbs',
                        line=line)

                line = read_FIN_line()

        else:  # verb
            if len(code) > 0:
                curcode = code
            else:
                curcode = primarycode
            if newblock:
                if '{' in verb:
                    # theverb is the index to the pattern storage for the
                    # remainder of the block
                    theverb = verb[:verb.find('{')].strip()

                else:
                    theverb = verb
                add_dict_tree([], theverb, code=curcode, line=line)
                newblock = False
            if '_' in verb:
                store_multi_word_verb(curcode, line)
            else:
                add_dict_tree(
                    [],
                    verb.split()[0],
                    theverb,
                    curcode,
                    dict='verbs',
                    line=line)
                if '{' in verb:
                    get_verb_forms(curcode, line)
                else:
                    make_verb_forms(curcode, line)
            ka += 1   # counting primary verbs
            line = read_FIN_line()

    close_FIN()

    # for k,v in sorted(PETRglobals.VerbDict.items()):
    #    print(k)
    #    for i,j in v.items():
    #        print('\t',i,j)
    # exit()


def show_verb_dictionary(filename=''):
    # debugging function: displays VerbDict to screen or writes to filename
    if len(filename) > 0:
        fout = open(filename, 'w')
        fout.write('PETRARCH Verb Dictionary Internal Format\n')
        fout.write('Run time: ' + PETRglobals.RunTimeString + '\n')

        for locword, loclist in PETRglobals.VerbDict.items():
            if locword[0] == '&':   # debug: skip the synsets
                continue
            fout.write(locword)
            if loclist[0]:
                if len(loclist) > 1:
                    # pattern list
                    fout.write("::\n" + str(loclist[1:]) + "\n")
                else:
                    fout.write(":: " + str(loclist[1]) + "\n")    # simple code
            else:
                # pointer
                fout.write(
                    '-> ' + str(loclist[2]) + ' [' + loclist[1] + ']\n')
        fout.close()

    else:
        for locword, loclist in PETRglobals.VerbDict.items():
            print(locword, end=' ')
            if loclist[0]:
                if len(loclist) > 2:
                    print('::\n', loclist[1:])   # pattern list
                else:
                    print(':: ', loclist[1])   # simple code
            else:
                print('-> ', loclist[2], '[' + loclist[1] + ']')

# ================== ACTOR DICTIONARY INPUT ================== #


def make_noun_list(nounst):
    # parses a noun string -- actor, agent or agent plural -- and returns in a list which
    # has the keyword and initial connector in the first tuple
    nounlist = []
    start = 0
    maxlen = len(nounst) + 1  # this is just a telltail
    while start < len(nounst):  # break phrase on ' ' and '_'
        spfind = nounst.find(' ', start)
        if spfind == -1:
            spfind = maxlen
        unfind = nounst.find('_', start)
        if unfind == -1:
            unfind = maxlen
        # <13.06.05> not sure we need this check...well, I just need the terminating point, still need to see which is lower
        if unfind < spfind:
            # this won't change, so use a tuple
            nounlist.append((nounst[start:unfind], '_'))
            start = unfind + 1
        else:
            nounlist.append((nounst[start:spfind], ' '))
            start = spfind + 1
    return nounlist


def dstr_to_ordate(datestring):
    """ Computes an ordinal date from a Gregorian calendar date string YYYYMMDD or YYMMDD."""
    """
	This uses the 'ANSI date' with the base -- ordate == 1 -- of 1 Jan 1601.  This derives
	from [OMG!] COBOL (see http://en.wikipedia.org/wiki/Julian_day) but in fact should
	work fairly well for our applications.

	For consistency with KEDS and TABARI, YY years between 00 and 30 are interpreted as
	20YY; otherwise 19YY is assumed.

	Formatting and error checking:
	1. YYMMDD dates *must* be <=7 characters, otherwise YYYYMMDD is assumed
	2. If YYYYMMDD format is used, only the first 8 characters are checked so it is okay
       to have junk at the end of the string.
	3. Days are checked for validity according to the month and year, e.g. 20100931 is
	   never allowed; 20100229 is not valid but 20120229 is valid
	4. Invalid dates raise DateError

	Source of algorithm: http://en.wikipedia.org/wiki/Julian_day

	Unit testing:
	Julian dates from http://aa.usno.navy.mil/data/docs/JulianDate.php (set time to noon)
	Results:
		dstr_to_ordate("20130926") # 2456562
		dstr_to_ordate("090120") # 2454852
		dstr_to_ordate("510724")  # 2433852
		dstr_to_ordate("19411207")  # 2430336
		dstr_to_ordate("18631119")  # 2401829
		dstr_to_ordate("17760704")  # 2369916
		dstr_to_ordate("16010101")  # 2305814
	"""

# print datestring        # debug
    try:
        if len(datestring) > 7:
            year = int(datestring[:4])
            month = int(datestring[4:6])
            day = int(datestring[6:8])
        else:
            year = int(datestring[:2])
            if year <= 30:
                year += 2000
            else:
                year += 1900
            month = int(datestring[2:4])
            day = int(datestring[4:6])
    except ValueError:
        raise DateError
# print year, month, day    # debug

    if day <= 0:
        raise DateError

    if month == 2:
        if year % 400 == 0:
            if day > 29:
                raise DateError
        elif year % 100 == 0:
            if day > 28:
                raise DateError
        elif year % 4 == 0:
            if day > 29:
                raise DateError
        else:
            if day > 28:
                raise DateError
    elif month in [4, 6, 9, 11]:         # 30 days have September...
        if day > 30:
            raise DateError
    else:                             # all the rest I don't remember...
        if day > 31:
            raise DateError

    if (month < 3):
        adj = 1
    else:
        adj = 0
    yr = year + 4800 - adj
    mo = month + (12 * adj) - 3
    ordate = day + math.floor((153 * mo + 2) / 5) + 365 * yr
    ordate += math.floor(yr / 4) - math.floor(yr / 100) + \
        math.floor(yr / 400) - 32045  # pure Julian date
    ordate -= 2305813   # adjust for ANSI date

    return int(ordate)



def read_actor_dictionary(actorfile):
    """ This is a simple dictionary of dictionaries indexed on the words in the actor string. The final node has the 
        key '#' and contains codes with their date restrictions and, optionally, the root phrase in the case
        of synonyms. """

    open_FIN(actorfile, "actor")

    line = read_FIN_line().strip()
    current_acts = []
    datelist = []
    while len(line) > 0:
        if line[0] == '[':  # Date
            data = line[1:-1].split()
            code = data[0]
            try:
                if '-' in data[1]:
                    dates = data[1].split('-')
                else:
                    dates = [data[1]]
            except:
                dates = []
            datelist.append((code, dates))
        else:
            if line[0] == '+':  # Synonym
                actor = line[1:].replace("_", ' ').split()
            else:  # Base actor
                # add previous actor entry to dictionary:
                if PETRglobals.WriteActorRoot and len(current_acts) > 0:  # store the root phrase if we're only to use it
                    datelist.append(current_acts[0])
                for targ in current_acts:
                    list = PETRglobals.ActorDict
                    while targ != []:
                        if targ[0] in [' ', '']:
                            targ = targ[1:]
                            continue
                        if not isinstance(list, dict):
                            print("BADNESS", list)
                            exit()
                        list = list.setdefault(targ[0], {})
                        targ = targ[1:]
                    list["#"] = datelist

                datelist = []  # reset for the new actor
                current_acts = []
                actor = line.replace("_", ' ').split()
                if actor[-1][-1] == ']':
                    data = actor[-1][1:-1].split()
                    code = data[0]
                    try:
                        if '-' in data[1]:
                            dates = data[1].split('-')
                        else:
                            dates = [data[1][1:]]
                    except:
                        dates = []
                    datelist.append((code, dates))
                    actor.pop()
            current_acts.append(actor)

        line = read_FIN_line().strip()

    """for j,k in sorted(PETRglobals.ActorDict.items()):
        print(j,'\t\t',k.keys())
        print(j,'\t\t',k)"""
#    exit()





# ================== AGENT DICTIONARY INPUT ================== #
def read_agent_dictionary(agent_path):
    """ Reads an agent dictionary
    Agents are stored in a simpler version of the Actors dictionary: a list of phrases
    keyed on the first word of the phrase.
    The individual phrase lists begin with the code, the connector from the key, and then
    a series of 2-tuples containing the remaining words and connectors. A 2-tuple of the
    form ('', ' ') signals the end of the list.

    Connector:
            blank: words can occur between the previous word and the next word
            _ (underscore): words must be consecutive: no intervening words

    FORMATTING OF THE AGENT DICTIONARY
    [With some additional coding, this can be relaxed, but anything following these
    rules should read correctly]
    Basic structure is a series of records of the form
            phrase_string {optional plural}  [agent_code]

    Material that is ignored
    1. Anything following '#'
    2. Any line beginning with '#' or '<!'
    3. Any null line (that is, line consisting of only \n

    A "phrase string" is a set of character strings separated by either blanks or
    underscores.

    A "agent_code" is a character string without blanks that is either preceded (typically)
    or followed by '~'. If the '~' precedes the code, the code is added after the actor
    code; if it follows the code, the code is added before the actor code (usually done
    for organizations, e.g. NGO~)

    Plurals:
            Regular plurals -- those formed by adding 'S' to the root, adding 'IES' if the
            root ends in 'Y', and added 'ES' if the root ends in 'SS' -- are generated automatically

            If the plural has some other form, it follows the root inside {...}

            If a plural should not be formed -- that is, the root is only singular or only
            plural, or the singular and plural have the same form (e.g. "police"), use a null
            string inside {}.

            If there is more than one form of the plural -- "attorneys general" and "attorneys
            generals" are both in use -- just make a second entry with one of the plural forms
            nulled (though in this instance -- ain't living English wonderful? -- you could null
            the singular and use an automatic plural on the plural form) Though in a couple
            test sentences, this phrase confused SCNLP.

    Substitution Markers:
            These are used to handle complex equivalents, notably

                    !PERSON! = MAN, MEN, WOMAN, WOMEN, PERSON
                    !MINST! = MINISTER, MINISTERS, MINISTRY, MINISTRIES

            and used in the form

                    CONGRESS!PERSON! [~LEG]
                    !MINIST!_OF_INTERNAL_AFFAIRS

            The marker for the substitution set is of the form !...! and is followed by an =
            and a comma-delimited list; spaces are stripped from the elements of the list so
            these can be added for clarity. Every time in the list is substituted for the marker,
            with no additional plural formation, so the first construction would generate

                    CONGRESSMAN [~LEG]
                    CONGRESSMEN [~LEG]
                    CONGRESSWOMAN [~LEG]
                    CONGRESSWOMEN [~LEG]
                    CONGRESSPERSON [~LEG]

    == Example ===
    <!-- PETRARCH VALIDATION SUITE AGENTS DICTIONARY -->
    <!-- VERSION: 0.1 -->
    <!-- Last Update: 27 November 2013 -->

    PARLIAMENTARY_OPPOSITION {} [~OPP] #jap 11 Oct 2002
    AMBASSADOR [~GOV] # LRP 02 Jun 2004
    COPTIC_CHRISTIAN [~CHRCPT] # BNL 10 Jan 2002
    FOREIGN_MINISTER [~GOVFRM] # jap 4/14/01
    PRESIDENT [~GOVPRS] # ns 6/26/01
    AIR_FORCE {} [~MIL] # ab 06 Jul 2005
    OFFICIAL_MEDIA {} [~GOVMED] # ab 16 Aug 2005
    ATTORNEY_GENERAL {ATTORNEYS_GENERAL} [~GOVATG] # mj 05 Jan 2006
    FOREIGN_MINISTRY [~GOV] # mj 17 Apr 2006
    HUMAN_RIGHTS_ACTIVISTS  [NGM~] # ns 6/14/01
    HUMAN_RIGHTS_BODY  [NGO~] # BNL 07 Dec 2001
    TROOP [~MIL] # ab 22 Aug 2005

    """
    global subdict

    def store_agent(nounst, code):
    # parses nounstring and stores the result with code
    
        list = PETRglobals.AgentDict
        targ = nounst.replace("_",' ').split()
        while targ != []:
            if targ[0] in [' ','']:
                targ = targ[1:]
                continue
            list = list.setdefault(targ[0],{})
            targ = targ[1:]
        list["#"] = code

        return
        
    
    def define_marker(line):
        global subdict
        if line[
                line.find('!') + 1:].find('!') < 0 or line[line.find('!'):].find('=') < 0:
            logger.warning(markdeferrorstr + enderrorstr)
            return
        ka = line.find('!') + 1
        marker = line[ka:line.find('!', ka)]
#		print marker
        loclist = line[line.find('=', ka) + 1:].strip()
        subdict[marker] = []
        for item in loclist.split(','):
            subdict[marker].append(item.strip())
#		print subdict[marker]

    def store_marker(agent, code):
        global subdict
        if agent[agent.find('!') + 1:].find('!') < 0:
            ka = agent.find('!')
            logger.warning("Substitution marker \"" +
                           agent[ka:agent.find(' ', ka) + 1] +
                           "\" syntax incorrect" + enderrorstr)
            return
        part = agent.partition('!')
        part2 = part[2].partition('!')
        if part2[0] not in subdict:
            logger.warning("Substitution marker !" + part2[0] +
                           "! missing in .agents file; line skipped")
            return
        for subst in subdict[part2[0]]:
            #			print part[0]+subst+part2[2]
            store_agent(part[0] + subst + part2[2], code)

    # this is just called when the program is loading, so keep them local.
    # <14.04.22> Or just put these as constants in the function calls: does it make a difference?
    enderrorstr = " in .agents file ; line skipped"
    codeerrorstr = "Codes are required for agents"
    brackerrorstr = "Missing '}'"
    markdeferrorstr = "Substitution marker incorrectly defined"

    subdict = {}  # substitution set dictionary

    # note that this will be ignored if there are no errors
    logger = logging.getLogger('petr_log')
    logger.info("Reading " + PETRglobals.AgentFileName + "\n")
    open_FIN(agent_path, "agent")

    line = read_FIN_line()
    while len(line) > 0:  # loop through the file

        if '!' in line and '=' in line:  # synonym set
            define_marker(line)
            line = read_FIN_line()
            continue

        if '[' not in line:  # code specified?
            logger.warning(codeerrorstr + enderrorstr)
            line = read_FIN_line()
            continue

        part = line.partition('[')
        code = part[2].partition(']')[0].strip()
        agent = part[0].strip() + ' '
        if '!' in part[0]:
            store_marker(agent, code)  # handle a substitution marker
        elif '{' in part[0]:
            if '}' not in part[0]:
                logger.warning(brackerrorstr + enderrorstr)
                line = read_FIN_line()
                continue
            agent = part[0][:part[0].find('{')].strip() + ' '
            # this will automatically set the null case
            plural = part[0][part[0].find('{') + 1:part[0].find('}')].strip()
        else:
            if 'Y' == agent[-2]:
                plural = agent[:-2] + 'IES'  # space is added below
            elif 'S' == agent[-2]:
                plural = agent[:-1] + 'ES'
            else:
                plural = agent[:-1] + 'S'

        store_agent(agent, code)
        if len(plural) > 0:
            store_agent(plural + ' ', code)

        line = read_FIN_line()

    close_FIN()

# ==== Input format reading


def read_xml_input(filepaths, parsed=False):
    """
    Reads input in the PETRARCH XML-input format and creates the global holding
    dictionary. Please consult the documentation for more information on the
    format of the global holding dictionary. The function iteratively parses
    each file so is capable of processing large inputs without failing.

    Parameters
    ----------

    filepaths: List.
                List of XML files to process.


    parsed: Boolean.
            Whether the input files contain parse trees as generated by
            StanfordNLP.

    Returns
    -------

    holding: Dictionary.
                Global holding dictionary with StoryIDs as keys and various
                sentence- and story-level attributes as the inner dictionaries.
                Please refer to the documentation for greater information on
                the format of this dictionary.
    """
    holding = {}

    for path in filepaths:
        tree = ET.iterparse(path)

        for event, elem in tree:
            if event == "end" and elem.tag == "Sentence":
                story = elem

                # Check to make sure all the proper XML attributes are included
                attribute_check = [key in story.attrib for key in
                                   ['date', 'id', 'sentence', 'source']]
                if not attribute_check:
                    print('Need to properly format your XML...')
                    break

                # If the XML contains StanfordNLP parsed data, pull that out
                # TODO: what to do about parsed content at the story level,
                # i.e., multiple parsed sentences within the XML entry?
                if parsed:
                    parsed_content = story.find('Parse').text
                    parsed_content = utilities._format_parsed_str(
                        parsed_content)
                else:
                    parsed_content = ''

                # Get the sentence information
                if story.attrib['sentence'] == 'True':
                    entry_id, sent_id = story.attrib['id'].split('_')

                    text = story.find('Text').text
                    text = text.replace('\n', ' ').replace('  ', ' ')
                    sent_dict = {'content': text, 'parsed': parsed_content}
                    meta_content = {'date': story.attrib['date'],
                                    'source': story.attrib['source']}
                    content_dict = {'sents': {sent_id: sent_dict},
                                    'meta': meta_content}
                else:
                    entry_id = story.attrib['id']

                    text = story.find('Text').text
                    text = text.replace('\n', ' ').replace('  ', ' ')
                    split_sents = _sentence_segmenter(text)
                    # TODO Make the number of sents a setting
                    sent_dict = {}
                    for i, sent in enumerate(split_sents[:7]):
                        sent_dict[i] = {'content': sent, 'parsed':
                                        parsed_content}

                    meta_content = {'date': story.attrib['date']}
                    content_dict = {'sents': sent_dict, 'meta': meta_content}

                if entry_id not in holding:
                    holding[entry_id] = content_dict
                else:
                    holding[entry_id]['sents'][sent_id] = sent_dict

                elem.clear()

    return holding


def read_pipeline_input(pipeline_list):
    """
    Reads input from the processing pipeline and MongoDB and creates the global
    holding dictionary. Please consult the documentation for more information
    on the format of the global holding dictionary. The function iteratively
    parses each file so is capable of processing large inputs without failing.

    Parameters
    ----------

    pipeline_list: List.
                    List of dictionaries as stored in the MongoDB instance.
                    These records are originally generated by the
                    `web scraper <https://github.com/openeventdata/scraper>`_.

    Returns
    -------

    holding: Dictionary.
                Global holding dictionary with StoryIDs as keys and various
                sentence- and story-level attributes as the inner dictionaries.
                Please refer to the documentation for greater information on
                the format of this dictionary.
    """
    holding = {}
    for entry in pipeline_list:
        entry_id = str(entry['_id'])
        meta_content = {'date': utilities._format_datestr(entry['date']),
                        'date_added': entry['date_added'],
                        'source': entry['source'],
                        'story_title': entry['title'],
                        'url': entry['url']}
        if 'parsed_sents' in entry:
            parsetrees = entry['parsed_sents']
        else:
            parsetrees = ''
        if 'corefs' in entry:
            corefs = entry['corefs']
            meta_content.update({'corefs': corefs})

        split_sents = _sentence_segmenter(entry['content'])
        # TODO Make the number of sents a setting
        sent_dict = {}
        for i, sent in enumerate(split_sents[:7]):
            if parsetrees:
                try:
                    tree = utilities._format_parsed_str(parsetrees[i])
                except IndexError:
                    tree = ''
                sent_dict[i] = {'content': sent, 'parsed': tree}
            else:
                sent_dict[i] = {'content': sent}

        content_dict = {'sents': sent_dict, 'meta': meta_content}
        holding[entry_id] = content_dict

    return holding


def _sentence_segmenter(paragr):
    """
    Function to break a string 'paragraph' into a list of sentences based on
    the following rules:

    1. Look for terminal [.,?,!] followed by a space and [A-Z]
    2. If ., check against abbreviation list ABBREV_LIST: Get the string
    between the . and the previous blank, lower-case it, and see if it is in
    the list. Also check for single-letter initials. If true, continue search
    for terminal punctuation
    3. Extend selection to balance (...) and "...". Reapply termination rules
    4. Add to sentlist if the length of the string is between MIN_SENTLENGTH
    and MAX_SENTLENGTH
    5. Returns sentlist

    Parameters
    ----------

    paragr: String.
            Content that will be split into constituent sentences.

    Returns
    -------

    sentlist: List.
                List of sentences.

    """
    # this is relatively high because we are only looking for sentences that
    # will have subject and object
    MIN_SENTLENGTH = 100
    MAX_SENTLENGTH = 512

    # sentence termination pattern used in sentence_segmenter(paragr)
    terpat = re.compile('[\.\?!]\s+[A-Z\"]')

    # source: LbjNerTagger1.11.release/Data/KnownLists/known_title.lst from
    # University of Illinois with editing
    ABBREV_LIST = ['mrs.', 'ms.', 'mr.', 'dr.', 'gov.', 'sr.', 'rev.', 'r.n.',
                   'pres.', 'treas.', 'sect.', 'maj.', 'ph.d.', 'ed. psy.',
                   'proc.', 'fr.', 'asst.', 'p.f.c.', 'prof.', 'admr.',
                   'engr.', 'mgr.', 'supt.', 'admin.', 'assoc.', 'voc.',
                   'hon.', 'm.d.', 'dpty.', 'sec.', 'capt.', 'c.e.o.',
                   'c.f.o.', 'c.i.o.', 'c.o.o.', 'c.p.a.', 'c.n.a.', 'acct.',
                   'llc.', 'inc.', 'dir.', 'esq.', 'lt.', 'd.d.', 'ed.',
                   'revd.', 'psy.d.', 'v.p.', 'senr.', 'gen.', 'prov.',
                   'cmdr.', 'sgt.', 'sen.', 'col.', 'lieut.', 'cpl.', 'pfc.',
                   'k.p.h.', 'cent.', 'deg.', 'doz.', 'Fahr.', 'Cel.', 'F.',
                   'C.', 'K.', 'ft.', 'fur.', 'gal.', 'gr.', 'in.', 'kg.',
                   'km.', 'kw.', 'l.', 'lat.', 'lb.', 'lb per sq in.', 'long.',
                   'mg.', 'mm.,, m.p.g.', 'm.p.h.', 'cc.', 'qr.', 'qt.', 'sq.',
                   't.', 'vol.', 'w.', 'wt.']

    sentlist = []
    # controls skipping over non-terminal conditions
    searchstart = 0
    terloc = terpat.search(paragr)
    while terloc:
        isok = True
        if paragr[terloc.start()] == '.':
            if (paragr[terloc.start() - 1].isupper() and
                    paragr[terloc.start() - 2] == ' '):
                isok = False      # single initials
            else:
                # check abbreviations
                loc = paragr.rfind(' ', 0, terloc.start() - 1)
                if loc > 0:
                    if paragr[
                            loc + 1:terloc.start() + 1].lower() in ABBREV_LIST:
                        isok = False
        if paragr[:terloc.start()].count(
                '(') != paragr[:terloc.start()].count(')'):
            isok = False
        if paragr[:terloc.start()].count('"') % 2 != 0:
            isok = False
        if isok:
            if (len(paragr[:terloc.start()]) > MIN_SENTLENGTH and
                    len(paragr[:terloc.start()]) < MAX_SENTLENGTH):
                sentlist.append(paragr[:terloc.start() + 2])
            paragr = paragr[terloc.end() - 1:]
            searchstart = 0
        else:
            searchstart = terloc.start() + 2

        terloc = terpat.search(paragr, searchstart)

    # add final sentence
    if (len(paragr) > MIN_SENTLENGTH and len(paragr) < MAX_SENTLENGTH):
        sentlist.append(paragr)

    return sentlist

#Newly added by Sayeed Salam sxs149331@utdallas.edu
import json
from StringIO import StringIO
from dateutil import parser

def read_json(jsonString):
    holding = {}
    sentence_limit = 7
    
    article = json.load(StringIO(jsonString))
    
    dateObject = None
    if len(article['date_line']) == 0:
        dateObject = datetime.now()
    else:    
        dateObject = parser.parse(article['date_line']) 

    
    try:
        entry_id = article['doc_id']
        sent_dict = {}
        print("1") 
        article_date = datetime.strftime(dateObject, '%Y%m%d')  
        print("2")
        meta_content = {'date': article_date, 'headline': article['head_line']}
        print("3")        
        
        print("4")
        counter = 0
    
        for sentence in article['sentences']:
            sent_id = sentence['sentence_id']
            print(sent_id)
            counter = counter + 1
            print (counter)
            if counter == sentence_limit:
                break #read only the first 7 sentences of a article
            parsed_text = utilities._format_parsed_str(sentence['parse_sentence'])
            print (parsed_text)
            sent_dict[sent_id] = {'content': sentence['sentence'], 'parsed':
                                        parsed_text}
            print (counter)
        content_dict = {'sents': sent_dict, 'meta': meta_content}
        holding[entry_id] = content_dict
        return holding
    except:
        print('Invalid JSON Format')
        print(sys.exc_info()[0])
        
        return {}
