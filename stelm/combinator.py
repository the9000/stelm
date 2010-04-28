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
Combines multiple formatters recursively.
"""

from cgi import escape as html_escape

def format(s):
  """
  Apply all formatters to the string and return the resulting string.
  The string is html-escaped first.
  """
  return u"".join(applyQueue(html_escape(s)))

def applyQueue(s):
  """
  string -> list of recursively formatted substrings.

  The formatter class that reports a fomatting oppostunity closer to the beginning of s than others
  gets called and formats a part of string; the process is repeated with the remaining part.
  Resulting formatted substrings are accumulated in a list and returned.


  A conforming formatter class defines three methods:
  *  formatter(s) creates a new formatter for string s.
  *  formatter.getStart(index) -> returns the offset in s where this formatter would start
      and which is greater than index, or None, if this formatter can not format anything in s.
  *  formatter.apply(s, pos) -> (fragments, next_index). Here next_index is the position where this formatter
      finished its work. The fragments list contains strings of applied formatting, e.g. ['<b>', 'foo', '</b>'].
      Every fragment that may contain nested formatting must be put through applyQueue() before being put
      into the fragments list.
  """
  ret = []
  pos = 0
  maxlen = len(s)
  while pos < maxlen:
    candidate = None
    bet = maxlen
    for proc_class in QUEUE:
      # find a betting processor
      taker = proc_class(s, pos)
      take = taker.getStart()
      if take is not None and take < bet:
        candidate = taker
        bet = take
        if bet == 0:
          break # others cannot bet for less anyway
    if candidate is None:
      break
    else:
      frags, pos = candidate.apply(s, pos)
      ret.extend(frags)
  if pos < maxlen:
    ret.append(s[pos:])
  return ret


from marker_based import Striker, Boldfacer, Italicizer
from escaper import Escaper
from preformatter import PreFormatter
from linker import Linker
#from hashtagger import HashTagger

QUEUE = (PreFormatter, Linker, Boldfacer, Italicizer, Striker, Escaper) 

