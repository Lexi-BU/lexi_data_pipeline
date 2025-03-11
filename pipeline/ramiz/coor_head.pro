PRO coor_head,head,coor

;auth: kdkvp
;date: 01/01/24 (documentation day)
;purp: extract the WCS paramters from a .fits header and to
;      put them into an IDL structure
;mods: 
;TBDS: 
;inpt:
;      head     : .fits file header
;otpt:
;      coor     : the structure

  ; creat the structure

  coor={naxis:long([0,0]),$
    crval:double([0.0,0.0]),crpix:double([0.0,0.0]),$
    cdelt:double([0.0,0.0]),ctype:['RA---TAN','DEC--TAN'],$
    crota:double(0)}

  ; fill it from the header

  coor.naxis=[sxpar(head,'NAXIS1'),sxpar(head,'NAXIS2')]
  coor.crval=[sxpar(head,'CRVAL1'),sxpar(head,'CRVAL2')]
  coor.crpix=[sxpar(head,'CRPIX1'),sxpar(head,'CRPIX2')]

  ; cdelt/cdnn always a problem

  coor.cdelt=[sxpar(head,'CDELT1'),sxpar(head,'CDELT2')]
  coor.crota=sxpar(head,'CROTA2')
  if(coor.cdelt(0) EQ 0 and coor.cdelt(1) EQ 0)then begin
    cd11=sxpar(head,'CD1_1')
    cd12=sxpar(head,'CD1_2')
    cd21=sxpar(head,'CD2_1')
    cd22=sxpar(head,'CD2_2')
    rot=atan(-cd12,-cd11)
    coor.crota=rot*180./!dpi
    coor.cdelt=[cd11/cos(rot),-cd12/sin(rot)]
  endif  

  ; here we need to do error checking to make sure that both exist

  tmp1=sxpar(head,'CTYPE1')
  tmp2=sxpar(head,'CTYPE2')
  if(typename(tmp1) NE 'STRING')then tmp1=''
  if(typename(tmp2) NE 'STRING')then tmp2=''
  coor.ctype=[tmp1,tmp2]

  end
