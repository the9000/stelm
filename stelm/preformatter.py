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

import re

class _PreFormatter(object):
  """
  Makes text pre-formatted and non-interpreted, e.g. for easy quotation of source code.
  Any possible markup inside is rendered as is, without further formatting.
  Starting sequence is {{, ending is }}, each on its own line.
  To quote in inside, use \}}. Nothing else is interpreted.

  Since this formatter prints what other formatters might interpret, it must come first in the queue.
  """

  @classmethod
  def prepare(cls, **attrs):
    "Patch the class with whatever we want"
    for k,v in attrs.iteritems():
      setattr(cls, k, v)
    return cls

  def __init__(self, s, pos):
    self.source = s
    self.boundary = pos
    hit = self.START_RE.search(s, pos)
    if hit is None:
      self.start = self.end = None
    else:
      self.start = hit.start()
      self.end = hit.end()

  def getStart(self):
    return self.start

  def apply(self):
    source, boundary = self.source, self.boundary
    if self.start is not None:
      res_list = []
      innards = []
      start = self.start
      if boundary != start:
        res_list.append(source[boundary:start])
      left_limit = self.end
      look_for_closing = True
      while look_for_closing:
        look_for_closing = False # usually we need only 1 iteration
        hit = self.END_RE.search(source, left_limit)
        if hit:
          mark = hit.groups()[0]
          if mark == self.ESCAPED:
            # cut out and continue
            innards.append(source[self.end:hit.start()])
            innards.append(self.END_SEQ)
            self.end = left_limit = hit.end()
            look_for_closing = True
          else:
            # wrap in tag
            res_list.append(self.open_tag)
            res_list.extend(innards)
            res_list.append(source[self.end:hit.start()])
            res_list.append(self.close_tag)
            start = hit.end()
        else:
          # start but no end
          res_list.append(source[self.start:self.end]) # the unmatched marker
          start = self.end
    else:
      # no start
      start = boundary
      res_list = []
    return (res_list, start)



def _produceCodeBlockFromatter(start_seq, end_seq, tag_name):
  open_tag, close_tag = "<%s>" % tag_name, "</%s>" % tag_name

  START = ur"\n?\s*" + start_seq + "\s*\n"
  END = ur"\n\s*" + end_seq + "\s*\n?"
  ESCAPED = u"\\" + end_seq

  START_RE = re.compile(u"("+START+")", re.U + re.MULTILINE)
  END_RE = re.compile(u"((?:\\"+ESCAPED+")|(?:"+END+"))", re.U + re.MULTILINE) # either escaped or normal end

  class CodeBlockWrapper(_PreFormatter):
    def __str__(self):
      return "%s(%r %r -> %r)%r" % (self.__class__.__name__, start_seq, end_seq, tag_name, id(self))

  return CodeBlockWrapper.prepare(
    START_RE = START_RE, END_RE=END_RE, ESCAPED=ESCAPED, END_SEQ=end_seq,
    open_tag=open_tag, close_tag=close_tag
  )

def _produceInlineCodeFromatter(start_seq, end_seq, tag_name):
  open_tag, close_tag = "<%s>" % tag_name, "</%s>" % tag_name

  START = start_seq
  END = end_seq
  ESCAPED = u"\\" + end_seq

  START_RE = re.compile(u"("+START+")")
  END_RE = re.compile(u"((?:\\"+ESCAPED+")|(?:"+END+"))") # either escaped or normal end

  class InlineBlockWrapper(_PreFormatter):
    def __str__(self):
      return "%s(%r %r -> %r)%r" % (self.__class__.__name__, start_seq, end_seq, tag_name, id(self))

  return InlineBlockWrapper.prepare(
    START_RE = START_RE, END_RE=END_RE, ESCAPED=ESCAPED, END_SEQ=end_seq,
    open_tag=open_tag, close_tag=close_tag
  )


BlockCodeFormatter = _produceCodeBlockFromatter("{{", "}}", "pre")

InlineCodeFormatter = _produceInlineCodeFromatter("{{", "}}", "code")