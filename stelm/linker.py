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

from marker_based import MarkerBased, produce

class _QuoteWrapper(MarkerBased):
  def getOpening(self):
    return []
  #
  def getClosing(self):
    return []


QuoteWrapper = produce(_QuoteWrapper, '"', "")

class Linker(object):
  """
  Converts links.

  * http://whatever-without-whitespace -> <a href="...">...</a>.
  * http://whatever-without-whitespace|name -> <a href="...">name</a>.
  * http://whatever-without-whitespace|"quoted string" -> <a href="...">quoted string</a>.

  Strings after vertical bar are further formatted.
  A literal double quote may be included into a quoted string by escaping with a backslash.
  Current limitation: a literal vertical bar cannot be inserted into the URL. Use %7C instead.
  """

  LINK_RE = re.compile("(http://\S+?)(\s|\||$)")
  SPACE_RE = re.compile("\s")

  def __init__(self, s, pos):
    hit = self.LINK_RE.search(s, pos)
    if hit is None:
      self.start = self.end = None
    else:
      self.start = hit.start()
      self.end = hit.end(1)
      self.has_text = hit.groups()[1] == "|"

  def getStart(self):
    return self.start

  def apply(self, s, pos):
    if self.start is not None:
      res_list = []
      start = self.start
      if pos != start:
        res_list.append(s[pos:start])
      url = s[self.start : self.end]
      if self.has_text:
        after_end = self.end+1 # including the space
        # cut out the link text
        maybe_quote = s[after_end : after_end+1]
        if maybe_quote == '"':
          quoter = QuoteWrapper(s, after_end)
          text_frags, start = quoter.apply(s, after_end)
        else:
          # skip to next space
          hit = self.SPACE_RE.search(s, after_end+1)
          if hit:
            start = hit.start()
          else:
            start = len(s) # had no space till EOL
          text_frags = applyQueue(s[after_end : start])
      else:
        text_frags = [url]
        start = self.end
      res_list.append('<a href="')
      res_list.append(url)
      res_list.append('">')
      res_list.extend(text_frags)
      res_list.append("</a>")
    else:
      # no start
      start = pos
      res_list = []
    return (res_list, start)




from combinator import applyQueue
