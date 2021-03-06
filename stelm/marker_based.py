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

"""
Marker-based formatters. Starting sequence is a marker then non-space, ending sequence is non-space then marker.
"""

# Note: escape definitions here and in escaper.py should match. 

import re

__all__ = ["MarkerBased", "Boldfacer", "Italicizer", "Striker", "produce"]


class _MarkerBased(object):

  @classmethod
  def prepare(cls, **attrs):
    "Patch the class with whatever we want"
    for k,v in attrs.iteritems():
      setattr(cls, k, v)

  def __init__(self, s, pos):
    "Start finding in string s at given pos"
    self.source = s
    self.boundary = pos
    hit = self.START_RE.search(s, pos)
    if hit:
      self.start = hit.start(1)
      self.end = hit.end(1)
    else:
      self.start = self.end = None

  def getStart(self):
    "Returns possible start of formatting position, or None if impossible"
    return self.start

  def apply(self):
    "Apply formatter; returns a tuple (list of fragments, next position)."
    source, boundary = self.source, self.boundary
    start = self.start
    if start is not None:
      res_list = []
      if boundary != start:
        res_list.append(source[boundary:start])
      left_limit = self.end
      look_for_closing = True
      while look_for_closing:
        look_for_closing = False # usually we need only 1 iteration
        hit = self.END_RE.search(source, left_limit)
        if hit and hit.start() != self.end:
          is_escape = False
          escape_mark = hit.group(1)
          if escape_mark:
            i = j = hit.start(1)
            while i >= 0 and source[i] == "\\":
              i -= 1
            is_escape = (j - i) % 2 == 1 # odd number of \'s ends in a real escape
            print is_escape 
          if is_escape:
            # ignore and repeat
            left_limit = hit.end(1) + 1
            look_for_closing = True
            continue
          else:
            if escape_mark:
              # ...but not our ending sequence not escaped
              hit_index = 1
            else:
              # just an end marker matched
              hit_index = 2
            # wrap in tag
            res_list.extend(self.getOpening())
            # recursively format the inside of match
            res_list.extend(applyQueue(source[self.end:hit.start(hit_index)]))
            res_list.extend(self.getClosing())
            start = hit.end(hit_index)
        else:
          # start but no end
          res_list.append(source[self.start:self.end]) # the unmatched marker
          start = self.end
    else:
      # no start
      start = boundary
      res_list = []
    return (res_list, start)

  def getOpening(self):
    return [self.open_tag]

  def getClosing(self):
    return [self.close_tag]



def produce(base_class, marker, tag, start_with_nonword=True):
  open_tag, close_tag = "<%s>" % tag, "</%s>" % tag

  if start_with_nonword:
    # match nonword + our opening mark
    START_RE = re.compile(ur"(?:\W|^)(\%s(?=\S))" % marker, re.U)
  else:
    # match just our opening mark
    START_RE = re.compile(ur"("+marker+"(?=\S))", re.U)

  # match either escape or closing mark + end of word
  #END_RE = re.compile(ur"((?:\\)|(?:(?<=\S)"+marker+"(?=\W|$)))", re.U)

  # match either escape + closing mark or closing mark + end of word;
  # $1 only matches escapes, $2 only matches non-escaped end markers 
  END_RE = re.compile(r"(?:(\\\%(M)s))|((?<=\S)\%(M)s(?=\W|$))" % dict(M=marker), re.U)

  class MarkerWrapper(base_class):
    def __str__(self):
      return "%r(%s->%s)@%x" % (self.__class__, marker, tag, id(self))


  MarkerWrapper.prepare(START_RE=START_RE, END_RE=END_RE, open_tag=open_tag, close_tag=close_tag)

  return MarkerWrapper


Boldfacer = produce(_MarkerBased, "*", "b")
Italicizer = produce(_MarkerBased, "_", "i")
Striker = produce(_MarkerBased, "-", "s")

from combinator import applyQueue # not earlier, else circular definition error happens

