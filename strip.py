#!/usr/bin/python3

# Copyright (c) 2021, Craig Altenburg
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Strip comments and docstrings from a file. """

import sys, token, tokenize

# ------------------------------------------------------------------------------
#  Function  stripFile
# ------------------------------------------------------------------------------

def stripFile( source, destination, indent, debug = False ):
    """ Strip comments, document strings and extranious white space
        from a file

        Parameters:
          source:      A readable file with source to strip.
          destination: A writable file when we put the stripped source.
          debug:       Pass "True" to dump tokens to stderr as they are processed

    """

    previousTokenType = token.INDENT
    indentLevel       = 0
    didNewLine        = False
    needNewLine       = False
    indentChar        = "\t" if indent == 0 else " " * indent

    tokenizer = tokenize.generate_tokens( source.readline )

    for tokenType, tokenText, (startLine, startCol), (endLine, endCol), lineText in tokenizer:

        if debug:
            print( "%2d %10s %4d.%3d %4d.%3d %-20r %r"
                      % (indentCount,
                        tokenize.tok_name.get( tokenType, tokenType ),
                        srcLine,
                        srcCol,
                        elineno,
                        ecol,
                        tokenText,
                        ltext), file=sys.stderr )

        # We want to eliminate comments and doc string so if we have one
        # of those we just ignore the token.

        if (    (tokenType != token.STRING or previousTokenType != token.INDENT)
            and  tokenType != token.COMMENT):


            if tokenType == token.INDENT:
                # If we have an INDENT token we update the indentLevel count.

                indentLevel += 1

                # If we just generated a new line we add one more indentLevel character
                # Otherwise, we set the flag to generate a new line

                if (didNewLine):
                    mod.write( indentChar )
                else:
                    needNewLine = True
            
            elif tokenType == token.DEDENT:
                # If we have a DEDENT token we decrement the  indentLevel count

                indentLevel -= 1

                # If we just started a new line, we'll have to start another
                # with the correct indentation.

                if (didNewLine):
                    needNewLine = True;

            elif tokenType == token.NEWLINE   or   tokenType == token.NL:
                # If we saw a NEWLINE or NL token we'll need a new line
                needNewLine = True

            else:
                if needNewLine:
                    destination.write( "\n" )

                    destination.write( indentChar * indentLevel )
                    
                    didNewLine  = True
                    needNewLine = False
                else:
                    didNewLine = False

                # If we have two names or numbers (or one of each) side by
                # side, put a space between them.

                if (    (tokenType         == token.NAME or tokenType         == token.NUMBER)
                    and (previousTokenType == token.NAME or previousTokenType == token.NUMBER)):

                    destination.write( " " )

                destination.write( tokenText )
            
            previousTokenType = tokenType

# ------------------------------------------------------------------------------
#  Main code
# ------------------------------------------------------------------------------

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
      formatter_class = argparse.RawDescriptionHelpFormatter,
      description = ( """\
      Strip comments, docstrings, and extra space from python source.

      If no ouput file is specified, each converted file will be
      written to a file matching the name of the input file but
      with "-strip" inserted before the file extension.
      """) )

    parser.add_argument( "-V", "--version",
                         action  = 'version',
                         version = '%(prog)s 1.0' )

    parser.add_argument( "-o", "--output",
                         action  = 'store',
                         metavar = 'output-file',
                         help    = 'specifiy output file (use - to output to stdout)' )

    parser.add_argument( "-i", "--indent",
                         action  = 'store',
                         metavar = 'count',
                         type    = int,
                         default = 0,
                         help    = 'number of spaces to indent, or zero (default) to indent with tabs' )

    parser.add_argument( "-d", "--dump",
                         action  = 'store_true',
                         help    = 'dump tokens to stderr' )

    parser.add_argument( 'files',
                         nargs   = '+' )

    args = parser.parse_args()

    if args.output == None:
      outputFile = None

    elif args.output == "-":
      outputFile = sys.stdout

    else:
      outputFile = open( args.output, "w" )

    for sourcePath in args.files:

      sourceFile = open( sourcePath, "r" )

      if outputFile == None:
        parts = sourcePath.rpartition( '.' )

        if parts[0]:
          destinationPath = parts[0] + "-strip" + parts[1] + parts[2]
        else:
          destinationPath = sourcePath + "-strip"

        destinationFile = open( destinationPath, "w" )

      else:
        destinationFile = outputFile

      stripFile( sourceFile, destinationFile, args.indent )

      sourceFile.close()

      if outputFile != None  and  outputFile != sys.stdout:
          outputFile.close()

