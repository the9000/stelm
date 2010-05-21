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
from cgi import escape as html_escape

from marker_based import _MarkerBased, produce

class _QuoteWrapper(_MarkerBased):
  def getOpening(self):
    return []
  #
  def getClosing(self):
    return []


QuoteWrapper = produce(_QuoteWrapper, '"', "", False)

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

  LINK_RE = re.compile("([a-zA-Z0-9]+://\S+?)(\s|\||$)")
  SPACE_RE = re.compile("\s")

  PROTO_CLASS_MAP = { # TODO: move this to options
    'http': 'http',
    'https': 'https',
    'ftp': 'ftp',
    'mailto': 'mailto',
    'xmpp': 'xmpp',
    '*': 'unknown'
  }

  @classmethod
  def configure(cls, data_dict):
    # TODO: add better config validation; maybe use yaml
    proto_classes = data_dict.get("protocol_classes", None)
    if proto_classes:
      good_types = (str, unicode, (type(None)))
      for k, v in proto_classes.iteritems():
        if not isinstance(v, good_types):
          print "Bad value %r for key %r" % (r, k)
          continue
        cls.PROTO_CLASS_MAP[unicode(k)] = v

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
      if not self.has_text:
        # strip pieces that may not belong to URL
        while True:
          last_of_url = url[-1]
          if last_of_url == ")" and "(" not in url or last_of_url in ".,;:?!\"'":
            # last ")" is not a part of URL unless there's an "(" earlier in it;
            # common punctuation is usually not a part of URL
            self.end -= 1
            url = s[self.start : self.end]
          else:
            break
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
      proto_pos = url.find("://")
      if proto_pos > 0:
        proto = self.PROTO_CLASS_MAP.get(url[:proto_pos], self.PROTO_CLASS_MAP.get("*", None))
      else:
        proto = None
      if any(bad_char in url for bad_char in '<>"'): # being defensive
        url = html_escape(url, True)  
      res_list.extend(('<a href="', url, '"'))
      if proto:
        res_list.extend((' class="', proto, '"'))
      res_list.append('>')
      res_list.extend(text_frags)
      res_list.append("</a>")
    else:
      # no start
      start = pos
      res_list = []
    return (res_list, start)


from combinator import applyQueue
