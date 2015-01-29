
;-------------------------------------------------------------
;+
; NAME:
;       DELCHR
; PURPOSE:
;       Delete all occurrences of a character from a text string.
; CATEGORY:
; CALLING SEQUENCE:
;       new = delchr(old, char)
; INPUTS:
;       old = original text string.     in
;       char = character to delete.     in
; KEYWORD PARAMETERS:
; OUTPUTS:
;       new = resulting string.         out
; COMMON BLOCKS:
; NOTES:
; MODIFICATION HISTORY:
;       R. Sterner.  5 Jul, 1988.
;       Johns Hopkins Applied Physics Lab.
;       RES 11 Sep, 1989 --- converted to SUN.
;       R. Sterner, 27 Jan, 1993 --- dropped reference to array.
;
; Copyright (C) 1988, Johns Hopkins University/Applied Physics Laboratory
; This software may be used, copied, or redistributed as long as it is not
; sold and this copyright notice is reproduced on each copy made.  This
; routine is provided as is without any express or implied warranties
; whatsoever.  Other limitations apply as described in the file disclaimer.txt.
;-
;-------------------------------------------------------------
 
	FUNCTION DELCHR, OLD, C, help=hlp
 
	if (n_params(0) lt 2) or keyword_set(hlp) then begin
	  print,' Delete all occurrences of a character from a text string.'
	  print,' new = delchr(old, char)'
	  print,'   old = original text string.     in'
	  print,'   char = character to delete.     in'
	  print,'   new = resulting string.         out'
	  return, -1
	endif
 
	B = BYTE(OLD)			   ; convert string to a byte array.
	CB = BYTE(C)			   ; convert char to byte.
	w = where(b ne cb(0))
	if w(0) eq -1 then return, ''	   ; Nothing left.
	return, string(b(w))		   ; Return new string.
	END


;-------------------------------------------------------------
;+
; NAME:
;       NWRDS
; PURPOSE:
;       Return the number of words in the given text string.
; CATEGORY:
; CALLING SEQUENCE:
;       n = nwrds(txt)
; INPUTS:
;       txt = text string to examine.             in
; KEYWORD PARAMETERS:
;       Keywords:
;         DELIMITER = d.  Set delimiter character (def = space).
; OUTPUTS:
;       n = number of words found.                out
; COMMON BLOCKS:
; NOTES:
;       Notes: See also getwrd.
; MODIFICATION HISTORY:
;       R. Sterner,  7 Feb, 1985.
;       Johns Hopkins University Applied Physics Laboratory.
;       RES 4 Sep, 1989 --- converted to SUN.
;
; Copyright (C) 1985, Johns Hopkins University/Applied Physics Laboratory
; This software may be used, copied, or redistributed as long as it is not
; sold and this copyright notice is reproduced on each copy made.  This
; routine is provided as is without any express or implied warranties
; whatsoever.  Other limitations apply as described in the file disclaimer.txt.
;-
;-------------------------------------------------------------
 
 
	function nwrds,txtstr, help=hlp, delimiter=delim
 
	if (n_params(0) lt 1) or keyword_set(hlp) then begin
	  print,' Return the number of words in the given text string.'
	  print,' n = nwrds(txt)'
	  print,'   txt = text string to examine.             in'
	  print,'   n = number of words found.                out'
	  print,' Keywords:'
	  print,'   DELIMITER = d.  Set delimiter character (def = space).'
	  print,' Notes: See also getwrd.'
	  return, -1
	endif
 
	if strlen(txtstr) eq 0 then return,0	; A null string has 0 words.
	ddel = ' '			; Default word delimiter is a space.
	if n_elements(delim) ne 0 then ddel = delim ; Use given word delimiter.
	tst = (byte(ddel))(0)			; Delimiter as a byte value.
        tb = byte(txtstr)                             ; String to bytes.
        if ddel eq ' ' then begin                     ; Check for tabs?
          w = where(tb eq 9B, cnt)                    ; Yes.
          if cnt gt 0 then tb(w) = 32B                ; Convert any to space.
        endif
	x = tb ne tst				; Locate words.
	x = [0,x,0]				; Pad ends with delimiters.
 
	y = (x-shift(x,1)) eq 1			; Look for word beginnings.
 
	n = fix(total(y))			; Count word beginnings.
 
	return, n
 
	end


;-------------------------------------------------------------
;+
; NAME:
;       ISNUMBER
; PURPOSE:
;       Determine if a text string is a valid number.
; CATEGORY:
; CALLING SEQUENCE:
;       i = isnumber(txt, [x])
; INPUTS:
;       txt = text string to test.                      in
; KEYWORD PARAMETERS:
; OUTPUTS:
;       x = optionaly returned numeric value if valid.  out
;       i = test flag:                                  out
;           0: not a number.
;           1: txt is a long integer.
;           2: txt is a float.
;           -1: first word of txt is a long integer.
;           -2: first word of txt is a float.
; COMMON BLOCKS:
; NOTES:
; MODIFICATION HISTORY:
;       R. Sterner.  15 Oct, 1986.
;       Johns Hopkins Applied Physics Lab.
;       R. Sterner, 12 Mar, 1990 --- upgraded.
;	Richard Garrett, 14 June, 1992 --- fixed bug in returned float value.
;
; Copyright (C) 1986, Johns Hopkins University/Applied Physics Laboratory
; This software may be used, copied, or redistributed as long as it is not
; sold and this copyright notice is reproduced on each copy made.  This
; routine is provided as is without any express or implied warranties
; whatsoever.  Other limitations apply as described in the file disclaimer.txt.
;-
;-------------------------------------------------------------
 
	FUNCTION ISNUMBER, TXT0, X, help=hlp
 
	if (n_params(0) lt 1) or keyword_set(hlp) then begin
	  print,' Determine if a text string is a valid number.'
	  print,' i = isnumber(txt, [x])
	  print,'   txt = text string to test.                      in'
	  print,'   x = optionaly returned numeric value if valid.  out'
	  print,'   i = test flag:                                  out'
	  print,'       0: not a number.'
	  print,'       1: txt is a long integer.'
	  print,'       2: txt is a float.'
	  print,'       -1: first word of txt is a long integer.'
	  print,'       -2: first word of txt is a float.'
	  return, -1
	endif
 
	TXT = STRTRIM(TXT0,2)	; trim blanks.
	X = 0			; define X.
 
	IF TXT EQ '' THEN RETURN, 0	; null string not a number.
 
	SN = 1
	IF NWRDS(TXT) GT 1 THEN BEGIN	; get first word if more than one.
	  SN = -1
	  TXT = GETWRD(TXT,0)
	ENDIF
	  
	f_flag = 0		; Floating flag.
	b = byte(txt)
	w = where(b eq 43, cnt)
	if cnt gt 1 then return, 0
	t = delchr(txt,'+')
	w = where(b eq 45, cnt)
	if cnt gt 1 then return, 0
	t = delchr(t,'-')
	w = where(b eq 46, cnt)			; '.'
	if cnt gt 1 then return, 0		; May only be 1.
	if cnt eq 1 then f_flag = 1		; If one then floating.
	t = delchr(t,'.')
	w = where(b eq 101, cnt)		; 'e'
	if cnt gt 1 then return, 0
	if cnt eq 1 then f_flag = 1
	t = delchr(t,'e')
	w = where(b eq 69, cnt)			; 'E'
	if cnt gt 1 then return, 0
	if cnt eq 1 then f_flag = 1
	t = delchr(t,'E')
	w = where(b eq 100, cnt)		; 'd'
	if cnt gt 1 then return, 0
	if cnt eq 1 then f_flag = 1
	t = delchr(t,'d')
	w = where(b eq 68, cnt)			; 'D'
	if cnt gt 1 then return, 0
	if cnt eq 1 then f_flag = 1
	t = delchr(t,'D')
	if total((b eq 101)+(b eq 69)+(b eq 100)+(b eq 68)) gt 1 then return,0
	b = byte(t)
	if total((b ge 65) and (b le 122)) ne 0 then return, 0
 
	c = strmid(t,0,1)
	if (c lt '0') or (c gt '9') then return, 0  ; First char not a digit.
 
	x = txt + 0.0				    ; Convert to a float.
	if f_flag eq 1 then return, 2*sn	    ; Was floating.
	if x eq long(x) then begin
	  x = long(x)
	  return, sn
	endif else begin
	  return, 2*sn
	endelse
 
	END
