# encoding: utf-8

# Copyright 2010 by Dmitry Cheryasov. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
# 
#    1. Redistributions of source code must retain the above copyright notice, this list of
#       conditions and the following disclaimer.
# 
#    2. Redistributions in binary form must reproduce the above copyright notice, this list
#       of conditions and the following disclaimer in the documentation and/or other materials
#       provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ^^^ This is the "Simplified BSD License"

import unittest

from marker_based import Boldfacer, Italicizer, Striker
from preformatter import PreFormatter
from linker import Linker
from linebreaker import LineBreaker
from dasher import Dasher
import combinator

class MarkerBasedTests(unittest.TestCase):

  def testBold(self):
    s = u"abc *def* ghi"
    f = Boldfacer(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"abc <b>def</b>"))
    self.assertEqual(next, s.index(" g"))

  def testBoldEndingNonWord(self):
    # Serves for all marker-based formatters
    s = u"abc *2*2=4*. yeah"
    f = Boldfacer(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"abc <b>2*2=4</b>"))
    self.assertEqual(next, s.index("."))

  def testBoldEndingEOL(self):
    # Serves for all marker-based formatters
    s = u"abc *2*2=4*"
    f = Boldfacer(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"abc <b>2*2=4</b>"))
    self.assertEqual(next, len(s))

  def testItalic(self):
    s = u"abc _def_ ghi"
    f = Italicizer(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"abc <i>def</i>"))
    self.assertEqual(next, s.index(" g"))

  def testStrikeout(self):
    s = u"abc -def- ghi"
    f = Striker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"abc <s>def</s>"))
    self.assertEqual(next, s.index(" g"))

  def testStrikeoutHyphen(self):
    s = u"abc-def-ghi"
    f = Striker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"abc-"))
    self.assertEqual(next, s.index("d"))

  def testStrikeoutHyphenUnicode(self):
    s = u"нет-нет и да-да"
    f = Striker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"нет-"))
    self.assertEqual(next, s.index(u"нет "))

  def testMarkedEscapeInside(self):
    s = ur"a *bc\*def* ghi"
    f = Boldfacer(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"a <b>bc*def</b>"))
    self.assertEqual(next, s.index(" g"))


class CombinatorTests(unittest.TestCase):

  def testSimple(self):
    s = u"abc *def* _ghi_ -jkl- mno"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), u"abc <b>def</b> <i>ghi</i> <s>jkl</s> mno")

  def testNested(self):
    s = u"abc _*def*_ _-ghi-_ jkl"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), u"abc <i><b>def</b></i> <i><s>ghi</s></i> jkl")

  def testEscapeCombinedBegin(self):
    s = ur"a\*bc *def* ghi"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), u"a*bc <b>def</b> ghi")

  def testMarkedEscapeCombinedInside(self):
    s = ur"a *b _c\*d_ ef* ghi"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), u"a <b>b <i>c*d</i> ef</b> ghi")

  def testLiteralBackslash(self):
    s = ur"a\\b"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), ur"a\b")

  def testLiteralBackslashThenEscapeBegin(self):
    s = ur"a\\\*b"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), ur"a\*b")

  def testLiteralBackslashThenEscapeInside(self):
    s = ur"*a\\\\\*b*"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), ur"<b>a\\*b</b>")


class PreformatTests(unittest.TestCase):

  def testOneLiner(self):
    s = ur"abc %!%def ghi%!%jkl"
    f = PreFormatter(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"abc <pre>def ghi</pre>"))
    self.assertEqual(next, s.index("jkl"))

  def testEscapeInside(self):
    s = ur"abc %!% end with \%!% and you're done %!% aaa"
    f = PreFormatter(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"abc <pre> end with \\%!% and you're done </pre>"))
    self.assertEqual(next, s.index(" aaa"))

  def testContainingMarkup(self):
    s = ur"code %!%*char*%!% done"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), ur"code <pre>*char*</pre> done")

  def testPWrappedInMarkup(self):
    s = ur"remember: *%!%i += 1%!%* and only so!"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), ur"remember: <b><pre>i += 1</pre></b> and only so!")


class LinkerTests(unittest.TestCase):

  def testSimple(self):
    s = ur"abc http://d.e.f ghi"
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'abc <a href="http://d.e.f">http://d.e.f</a>'))
    self.assertEqual(next, s.index(" ghi"))

  def testNamed(self):
    s = ur"abc http://d.e.f|DEF ghi"
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'abc <a href="http://d.e.f">DEF</a>'))
    self.assertEqual(next, s.index(" ghi"))

  def testNamedSpaced(self):
    s = ur'abc http://d.e.f|"D EF" ghi'
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'abc <a href="http://d.e.f">D EF</a>'))
    self.assertEqual(next, s.index(" ghi"))

  def testNamedEscaped(self):
    s = ur'abc http://d.e.f|"D\"E\"F" ghi'
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'abc <a href="http://d.e.f">D"E"F</a>'))
    self.assertEqual(next, s.index(" ghi"))

  def testWrappedInMarkup(self):
    s = ur'abc *http://d.e.f|"DEF"* ghi'
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), u'abc <b><a href="http://d.e.f">DEF</a></b> ghi')

  def testNameWithInMarkup(self):
    s = ur'abc http://d.e.f|"D _E_ F" ghi'
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), u'abc <a href="http://d.e.f">D <i>E</i> F</a> ghi')

  def testEOL(self):
    s = ur'abc http://d.e.f'
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), u'abc <a href="http://d.e.f">http://d.e.f</a>')


class BreakerTests(unittest.TestCase):

  def testN(self):
    s = u'a\nb'
    f = LineBreaker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'a<br/>'))
    self.assertEqual(next, s.index("b"))

  def testR(self):
    s = u'a\rb'
    f = LineBreaker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'a<br/>'))
    self.assertEqual(next, s.index("b"))

  def testNR(self):
    s = u'a\n\rb'
    f = LineBreaker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'a<br/>'))
    self.assertEqual(next, s.index("b"))

  def testRN(self):
    s = u'a\r\nb'
    f = LineBreaker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'a<br/>'))
    self.assertEqual(next, s.index("b"))


class DasherTests(unittest.TestCase):

  def testSimple(self):
    s = u'a -- b'
    f = Dasher(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'a \u2014'))
    self.assertEqual(next, s.index(" b"))

  def testBOL_Hard(self):
    s = u'-- b'
    f = Dasher(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'\u2014'))
    self.assertEqual(next, s.index(" b"))

  def testBOL_Soft(self):
    s = u'Whatnot\n-- b'
    f = Dasher(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'Whatnot\n\u2014'))
    self.assertEqual(next, s.index(" b"))

if __name__ == "__main__":
  unittest.main()



