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

def _produce(pattern, replacement):

  PATTERN_RE = re.compile(pattern, re.U + re.MULTILINE)

  class Substitutor(object):
    """
    Replaces double minuses with em dashes.
    To be replaced, '--' must encompassed be by whitespace, or begin at line start.
    """

    def __init__(self, s, pos):
      hit = PATTERN_RE.search(s, pos)
      if hit is None:
        self.start = self.end = None
      else:
        self.start = hit.start(1)
        self.end = hit.end(1)

    def getStart(self):
      return self.start

    def apply(self, s, pos):
      if self.start is not None:
        res_list = []
        start = self.start
        if pos != start:
          res_list.append(s[pos:start])
        res_list.append(replacement)
        start = self.end
      else:
        # no start
        start = pos
        res_list = []
      return (res_list, start)

  return Substitutor

Dasher = _produce("(?:\s|^)(--)(?:\s)", u"\u2014")

# matching the newline is a bit clumsy, but works
NEWLINE = "\r\n|\n\r|\n|\r"
SPC = "[ \t]*"
HorizontalRuler = _produce("((?:"+NEWLINE+"|^)"+SPC+"-{3,}"+SPC+"(?:"+NEWLINE+"|$))", "<hr/>")