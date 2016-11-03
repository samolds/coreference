,=============================================================================
                    Coreference Resolution Scorer
=============================================================================

RUNNING THE SCORER ON CADE:
   
   To run the program, use this command: 
       python coref-scorer.py <responselist> <directory-with-keys>

   For example: 
       python coref-scorer.py /home/username/responselist.txt /home/username/dev/

   You can use the sample files provided to test out the program like this:
       python coref-scorer.py responselist.txt dev/

ADDITIONAL ARGUMENTS:

   -V : Verbose output, gives you more information regarding how well your 
        system performed on different types of noun phrases.  

        For example: ./coref-scorer.py /home/username/responselist.txt /home/username/dev/ -V

        CAVEAT: this option uses *heuristics* to guess which NPs are
        pronouns, common nouns, or proper nouns. So the breakdown by
        types is not guaranteed to be perfect, but should give you a
        general idea of how your coreference resolver is doing on
        different types of anaphora.

----------------------------------------------------------------------------
NOTES:

  a. The responselist file should have a response filename on each
     line. Each filename should include an absolute path, or a
     relative path from the directory in which the scoring program is
     run.

  b. The directory-with-keys should be a directory path that contains the
     official answer key (.key) files.

  c. The scoring program only uses the information surrounded by the
     <COREF></COREF> XML tags to do scoring. So, your program does not
     necessarily have to reproduce the original document as a response
     file. If you prefer, it is sufficient to simply output the
     portions of the text that have the <COREF></COREF> XML tags. If
     you choose this option, be sure to include ALL of the XML
     annotations needed for resolutions though (i.e., both the XML
     annotations for the antecedents and for the resolved anaphora),
     or the scoring program will crash. Also remember that the file
     needs to have <TXT> at the beginning and </TXT> at the end.

     In the sample files provided, the b1.response file shows you what
     a fully XML-annotated response file would look like, and the
     b2.response file shows you what a reduced XML file would look
     like.

***************************************************************************
   
If you detect any problems with the scorer or have questions about it, 
send email to: teach-cs5340@list.eng.utah.edu
