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


class MarkerBased(object):

  @classmethod
  def prepare(cls, **attrs):
    "Patch the class with whatever we want"
    for k,v in attrs.iteritems():
      setattr(cls, k, v)

  def __init__(self, s, pos):
    "Start finding in string s at given pos"
    hit = self.START_RE.search(s, pos)
    if hit:
      self.start = hit.start()
      self.end = hit.end()
    else:
      self.start = self.end = None

  def getStart(self):
    "Returns possible start of formatting position, or None if impossible"
    return self.start

  def apply(self, s, pos):
    "Apply formatter; returns a tuple (list of fragments, next position)."
    start = self.start
    if start is not None:
      res_list = []
      if pos != start:
        res_list.append(s[pos:start])
      left_limit = self.end
      look_for_closing = True
      while look_for_closing:
        look_for_closing = False # usually we need only 1 iteration
        hit = self.END_RE.search(s, left_limit)
        if hit and hit.start() != self.end:
          mark = hit.groups()[0]
          if mark == u'\\':
            # escape; ignore and continue
            left_limit = hit.end()+1
            look_for_closing = True
          else:
            # wrap in tag
            res_list.extend(self.getOpening())
            # recursively format the inside of match
            res_list.extend(applyQueue(s[self.end:hit.start()]))
            res_list.extend(self.getClosing())
            start = hit.end()
        else:
          # start but no end
          res_list.append(s[self.start:self.end]) # the unmatched marker
          start = self.end
    else:
      # no start
      start = pos
      res_list = []
    return (res_list, start)

  def getOpening(self):
    return [self.open_tag]

  def getClosing(self):
    return [self.close_tag]



def produce(base_class, marker, tag):
  open_tag, close_tag = "<%s>" % tag, "</%s>" % tag

  # match only our opening mark
  START_RE = re.compile(ur"(\%s(?=\S))" % marker)

  # match either escape or closing mark + end of word
  END_RE = re.compile(ur"((?:\\)|(?:(?<=\S)\%s(?=\W|$)))" % marker)

  class MarkerWrapper(base_class):
    def __str__(self):
      return "%r(%s->%s)@%r" % (self.__class__, marker, tag, id(self))


  MarkerWrapper.prepare(START_RE=START_RE, END_RE=END_RE, open_tag=open_tag, close_tag=close_tag)

  return MarkerWrapper


Boldfacer = produce(MarkerBased, "*", "b")
Italicizer = produce(MarkerBased, "_", "i")
Striker = produce(MarkerBased, "-", "s")

from combinator import applyQueue # not earlier, else circular definition error happens

