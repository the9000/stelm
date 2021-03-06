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

ESC_RE = re.compile(ur"(\\.)")

class Escaper(object):
  """
  Literal quotation formatter. A backslash quotes the following character, hiding it from further formatting.
  Does not call other formatters; must go last in the combinator queue.
  """
  def __init__(self, s, pos):
    "Start finding in string s at given pos"
    self.source = s
    self.boundary = pos
    hit = ESC_RE.search(s, pos)
    if hit:
      self.start = hit.start()
    else:
      self.start = None

  def getStart(self):
    "Returns possible start of formatting position, or None if impossible"
    return self.start

  def apply(self):
    "Apply formatter; returns a tuple (list of fragments, next position)."
    source, boundary, start = self.source, self.boundary, self.start
    return ([source[boundary:start], source[start+1]], start+2)
