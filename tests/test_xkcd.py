# coding: utf-8

import unittest

from xxkcd import xkcd

expect = {
    '353_trans': u'[[ Guy 1 is talking to Guy 2, who is floating in the sky ]]\nGuy 1: You\'re flying! How?\nGuy 2: Python!\nGuy 2: I learned it last night! Everything is so simple!\nGuy 2: Hello world is just \'print "Hello, World!" \'\nGuy 1: I dunno... Dynamic typing? Whitespace?\nGuy 2: Come join us! Programming is fun again! It\'s a whole new world up here!\nGuy 1: But how are you flying?\nGuy 2: I just typed \'import antigravity\'\nGuy 1: That\'s it?\nGuy 2: ...I also sampled everything in the medicine cabinet for comparison.\nGuy 2: But i think this is the python.\n{{ I wrote 20 short programs in Python yesterday.  It was wonderful.  Perl, I\'m leaving you. }}',
    '1609_trans': u'Figure: You know what\'s actually really good? FOOD and FOOD.\nFigures: Huh. I guess I can see it.\nCaption: FUN FACT: If you say "YOU KNOW WHAT\'S ACTUALLY REALLY GOOD?" in the right tone of voice, you can name any two individually-good foods here and no one will challenge you on it.\nList of foods: Ice cream, ham, relish, pancakes, ketchup, cheese, eggs, cupcakes, sour cream, hot chocolate, avocado, skittles.\n\n{{Title text: If anyone tries this on you, the best reply is a deadpan "Oh yeah, that\'s a common potato chip flavor in Canada."}}',
    '1664_trans': u"[[Two women and a man are standing around, talking.]]\nWoman: Our lab is studying a fungus that takes over mammal brains and makes them want to study fungi.\nMan: It's very promising! We're opening a whole new wing of the lab just to cultivate it!\n\n{{Title text: Conspiracy theory: There's no such thing as corn. Those fields you see are just the stalks of a fungus that's controlling our brains to make us want to spread it.}}",
    '259_title': u'Clichéd Exchanges',
    '259_trans': u"Narrator: MY HOBBY: DERAILING CLICHÉD EXCHANGES BY USING THE WRONG REPLIES\nMan 1: O RLY?\nMan 2: O RLY? I 'ARDLY KNOW 'ER!\n{{It's like they say, you gotta fight fire with clichés.}}",
    '124_trans': u'From the makers of the Blogosphere, Blogocube, and Blogodrome comes\nthe Blogofractal\n[[A large rectangle subdivided into rectangles in a fractal pattern, most with a phrase or word inside]]\n[[Mostly left to right from top-left corner]]\nTripMaster Monkey says\n118th Post!!\nWikiconstitution!\nOMG\nDeCSS\nCasemod your Boyfriend!!\nFLICKR\nThey\'re saying on Kos that\nhttp:\nslashdot.org\narticl\ntagCloud\nCory Doctorow is a little upset about copyright law.\nHey guys what if Google is evil?!?\nI\'ll sleep with you for a FreeIpods deal.\nFirstPsot!!\nSnakes on an I don\'t Even Care Anymore\nKiwiWiki\nCSS\nComments (0)\nBlogotesseract\n¡play games!\n[[RSS icon]]\nis AYB retro yet?\nGoogle Google Google Apple Google Goog\nCheney totally shot a dude!!!\nWatch this doddler get owned by a squirrel!!!\nDevelopers\nDevelopers\nDevelopers\nDevelopers\nI installed a Mac Mini inside ANOTHER Mac Mini!\nCheck out this vid of Jon Stewart\n9-11 <-> Trent Lott!\nWeb 7.1\nKryptonite™ locks vulnerable to "keys!"\nInteresting post!  Check out my blog, it has useful info on CARBON MONOXIDE LITIGATION\nFIREFLY!!\nHELP ME\nEngadget\nBoing Boing\nGizmodo\nMAKE Blog: DIY baby\nMy friend has a band!!\nJon released an exploit in the protocol for meeting girls.\nInternets!\nHoward Dean?\nSo I hear there\'s a hurricane.\nWe should elect this dude!\nGoogle Maps is da best!!\nModeration:  +1 Sassy\nRSS!\nA-list\n<3\nTrackable URL?\nI shot a man in Reno check it out on YouTube!\nHEY LOOK ROBOTS!\nNet Neutrality!\nFriends Only.\nDupe!\nAJAX?\nCOMPLY\nCowboy Neal\nBlogodrome\nHey look I got Linux running on my tonsils!\nLook alive, blogonauts!\nCafepress cockrings\nBOOBIES!!\nMIA\nA Beowulf Cluster... of BLOGS!!\nSPOILER ALERT\nDupe!\nYou have been eaten by a Grue.\nRuby on a monorail\nLesbians!\nDNF Released!\nSteampunk\nBLAG\nPONIES!\nXeni found some porn!\nIRONY\nLIARS!\nLinux on Rails!\nBlogocube\ndel.icio.us!\n404\no.O\nDon\'t slam the source when you close it.\n{{title text: Edward Tufte\'s \'The Visual Display of Quantitative Information\' is a fantastic book, and should be required reading for anyone in either the sciences or graphic design.}}',
    '353_alt': u"I wrote 20 short programs in Python yesterday.  It was wonderful.  Perl, I'm leaving you.",
    '859_alt': u'Brains aside, I wonder how many poorly-written xkcd.com-parsing scripts will break on this title (or ;;"\'\'{<<[\' this mouseover text."',
    '1723_link': 'http://meteorites.wustl.edu/check-list.htm'

}


class Testxkcd(unittest.TestCase):
    def test_url(self):
        self.assertEqual(xkcd().url, 'https://xkcd.com', 'Incorrect "latest" url')
        self.assertEqual(xkcd().mobile_url, 'https://m.xkcd.com', 'Incorrect mobile "latest" url')
        self.assertEqual(xkcd(353).url, 'https://xkcd.com/353/', 'Incorrect comic url')
        self.assertEqual(xkcd(353).mobile_url, 'https://m.xkcd.com/353/', 'Incorrect mobile comic url')

    def test_transcript(self):
        self.assertEqual(xkcd(353).transcript, expect['353_trans'], 'Incorrect early transcript')
        self.assertEqual(xkcd(1609).transcript, expect['1609_trans'], 'Incorrect middle transcript')
        self.assertEqual(xkcd(1664).transcript, expect['1664_trans'], 'Incorrect late transcript')

    def test_decoding(self):
        self.assertEqual(xkcd(259).title, expect['259_title'], 'Incorrect html entity parsing')
        self.assertEqual(xkcd(259).transcript, expect['259_trans'], 'Incorrect utf-8 double encoding decoding')
        self.assertEqual(xkcd(124).transcript, expect['124_trans'], 'Incorrect multiple utf-8 encoding decoding')

    def test_alt_text(self):
        self.assertEqual(xkcd(353).alt, expect['353_alt'], 'Incorrect alt text')
        self.assertEqual(xkcd(859).alt, expect['859_alt'], 'Incorrect alt text')

    def test_link(self):
        self.assertEqual(xkcd(1723).link, expect['1723_link'], 'Incorrect link')

    def test_load_all(self):
        # Can't get mock to work in Python 2.
        # Just manually setting methods and setting them back.
        i = None
        def should_not_call(*_, **__):
            if i is None:
                raise RuntimeError('should_not_call should not have been called yet. How is that even possible?')
            raise AssertionError('xkcd.urlopen called for {}'.format(i))

        xkcd_urlopen = staticmethod(xkcd.urlopen)
        xkcd_range = xkcd.range

        xkcd.delete_all()

        try:
            # Just test with first few comics for test.
            xkcd.range = classmethod(lambda *_, **__: range(1, 6))

            xkcd.load_all(True)

            xkcd.urlopen = should_not_call
            for i in xkcd.range()[:-1]:
                xkcd(i).json
        finally:
            xkcd.urlopen = xkcd_urlopen
            xkcd.range = xkcd_range
