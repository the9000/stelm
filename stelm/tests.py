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
from preformatter import BlockCodeFormatter, InlineCodeFormatter
from linker import Linker
from linebreaker import LineBreaker
from simple_substitutor import Dasher, HorizontalRuler
import combinator

class TMarkerBased(unittest.TestCase):

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

  def testBoldBOL(self):
    # Serves for all marker-based formatters
    s = u"*2*2=4* abc"
    f = Boldfacer(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"<b>2*2=4</b>"))
    self.assertEqual(next, s.index(" a"))

  def testBoldOnlyThing(self):
    # Serves for all marker-based formatters
    s = u"*2*2=4*"
    f = Boldfacer(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u"<b>2*2=4</b>")
    self.assertEqual(next, len(s))

  def testBoldBetweenCRs(self):
    # Serves for all marker-based formatters
    s = u"abc\n*2*2=4*\ndef"
    f = Boldfacer(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"abc\n<b>2*2=4</b>"))
    self.assertEqual(next, s.index("\ndef"))

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
    self.assertEqual(frags, [])
    self.assertEqual(next, 0)

  def testStrikeoutHyphenUnicode(self):
    s = u"нет-нет и да-да"
    f = Striker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(frags, [])
    self.assertEqual(next, 0)

  def testMarkedEscapeInside(self):
    s = ur"a *bc\* def* ghi"
    f = Boldfacer(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u"a <b>bc* def</b>"))
    self.assertEqual(next, s.index(" g"))

  def testNonStart(self):
    s = ur"ab*cd* ef"
    f = Boldfacer(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(frags, [])
    self.assertEqual(next, 0)


class TCombinator(unittest.TestCase):

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


class TBlockCode(unittest.TestCase):

  def testOneLiner(self):
    s = u"abc {{\ndef ghi\n}}jkl"
    f = BlockCodeFormatter(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u"abc<pre>def ghi</pre>")
    self.assertEqual(next, s.index("jkl"))

  def testEscapeInside(self):
    s = u"abc {{\n end with \}} and you're done \n}} aaa"
    f = BlockCodeFormatter(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u"abc<pre> end with }} and you're done </pre>")
    self.assertEqual(next, s.index("aaa"))

  def testContainingMarkup(self):
    s = u"code {{\nint *char*\n}} done"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), ur"code<pre>int *char*</pre>done")

  def testPWrappedInMarkup(self):
    s = u"remember: *{{\ni += 1\n}}* and only so!"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), ur"remember: <b><pre>i += 1</pre></b> and only so!")

class TInlineCode(unittest.TestCase):

  def testOneLiner(self):
    s = u"abc {{def ghi}} jkl"
    f = InlineCodeFormatter(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u"abc <code>def ghi</code>")
    self.assertEqual(next, s.index(" jkl"))

  def testEscapeInside(self):
    s = u"abc {{ end with \}} and you're done }} aaa"
    f = InlineCodeFormatter(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u"abc <code> end with }} and you're done </code>")
    self.assertEqual(next, s.index(" aaa"))

  def testContainingMarkup(self):
    s = u"code {{int *char*}} done"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), ur"code <code>int *char*</code> done")

  def testPWrappedInMarkup(self):
    s = u"remember: *{{i += 1}}* and only so!"
    frags = combinator.applyQueue(s)
    self.assertEqual(u"".join(frags), ur"remember: <b><code>i += 1</code></b> and only so!")


class TLinker(unittest.TestCase):

  def setUp(self):
    Linker.configure({
      "protocol_classes": {
        "http": None,
        'ftp': 'ftp',
        "*": "unknown"
      }
   })

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

  def testOuterParens(self):
    s = ur"abc (http://d.e.f) ghi"
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'abc (<a href="http://d.e.f">http://d.e.f</a>')
    self.assertEqual(next, s.index(") ghi"))

  def testComma(self):
    s = ur"abc http://d.e.f, ghi"
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'abc <a href="http://d.e.f">http://d.e.f</a>')
    self.assertEqual(next, s.index(", ghi"))

  def testOuterParensAndDot(self):
    s = ur"abc (http://d.e.f). ghi"
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'abc (<a href="http://d.e.f">http://d.e.f</a>')
    self.assertEqual(next, s.index("). ghi"))

  def testPunctuationAndName(self):
    s = ur"abc http://d.e.f?ghi!|foo. ghi"
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'abc <a href="http://d.e.f?ghi!">foo.</a>')
    self.assertEqual(next, s.index(" ghi"))

  def testInnerParens(self):
    s = ur"abc http://wiki/Foo_(Bar) ghi"
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'abc <a href="http://wiki/Foo_(Bar)">http://wiki/Foo_(Bar)</a>')
    self.assertEqual(next, s.index(" ghi"))

  def testKnownProtocolClass(self):
    s = ur"abc ftp://wiki/Foo ghi"
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'abc <a href="ftp://wiki/Foo" class="ftp">ftp://wiki/Foo</a>')
    self.assertEqual(next, s.index(" ghi"))

  def testUnknownProtocolClass(self):
    s = ur"abc zox://wiki/Foo ghi"
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'abc <a href="zox://wiki/Foo" class="unknown">zox://wiki/Foo</a>')
    self.assertEqual(next, s.index(" ghi"))

  def testBadCharsInUrl(self):
    s = ur'abc http://d.e.f?<a>+"b"|foo ghi'
    f = Linker(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'abc <a href="http://d.e.f?&lt;a&gt;+&quot;b&quot;">foo</a>')
    self.assertEqual(next, s.index(" ghi"))

class TBreaker(unittest.TestCase):

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


class TDasher(unittest.TestCase):

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
    f = combinator.Dasher(s, 0)
    frags, next = f.apply(s, 0)
    self.assertTrue(u"".join(frags).startswith(u'Whatnot\n\u2014'))
    self.assertEqual(next, s.index(" b"))


class THLiner(unittest.TestCase):

  def testBetweenNewLines(self):
    s = u'a\n----\nb'
    f = HorizontalRuler(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'a<hr/>')
    self.assertEqual(next, s.index("b"))

  def testBetweenManyLines(self):
    s = u'a\n\n----\n\nb'
    f = HorizontalRuler(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'a\n<hr/>')
    self.assertEqual(next, s.index("\nb"))

  def testBOL(self):
    s = u'---\n b'
    f = HorizontalRuler(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'<hr/>')
    self.assertEqual(next, s.index(" b"))

  def testEOL(self):
    s = u'Over!\n---'
    f = HorizontalRuler(s, 0)
    frags, next = f.apply(s, 0)
    self.assertEqual(u"".join(frags), u'Over!<hr/>')
    self.assertEqual(next, len(s))

if __name__ == "__main__":
  unittest.main()



