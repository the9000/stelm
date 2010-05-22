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

class HashTagger(object):
  """
  Detects and turns to links sequences of letters preceded by a hash sign, like #this.
  A hashtag ends at any non-word character, except underscore and dot,
  if these are followed by more word characters.
  Examples:
  #foo -> foo
  #python-style -> python
  Period of #foo. -> foo
  _Italic #foo_ -> foo
  #under_score -> under_score
  #dot.com -> dot.com
  """

  TAG_RE = re.compile(u"#(\w+(?:[\\.]\w+)*)", re.U)
  TAG_URL = u"/tag/"

  def __init__(self, s, pos):
    self.source = s
    self.boundary = pos
    hit = self.TAG_RE.search(s, pos)
    self.hit = hit

  def getStart(self):
    return self.hit and self.hit.start() or None

  def apply(self):
    source, boundary = self.source, self.boundary
    if self.hit is not None:
      res_list = []
      start = self.hit.start()
      if boundary != start:
        res_list.append(source[boundary:start])
      text = self.hit.groups()[0]
      if text.endswith("_"):
        text = text[:-1]
        next = self.hit.end()-1
      else:
        next = self.hit.end()
      res_list.append('<a href="')
      res_list.append(self.TAG_URL)
      res_list.append(text)
      res_list.append('">#')
      res_list.append(text)
      res_list.append("</a>")
    else:
      # no start
      next = boundary
      res_list = []
    return (res_list, next)

