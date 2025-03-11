PRO sxi_read_atti,atti_file,atti,n_atti,atti_head,atti_path,atti_roll,atti_devi,atti_time,step_time,diag

;auth:kdkvp
;date:20/10/23
;purp:read the attitude file
;     fix the attitude (unwrap RA and Dec)
;     calculate the scan path direction
;mods:01/03/24 modified to return angle between detx and path
;TBDS:
;inputs:
;  atti_file: name of attitude file
;  diag: if not 0 then create diagnostic plots and other output
;outputs:
;  atti: attitude structure (see code)
;  n_atti: number of entries in attitude structure
;  atti_head: header for attitude file (may not be needed)
;  atti_path: direction of scan path between each step in atti
;  atti_time: goes with atti_path
;  atti_roll: goes with atti_path
;  atti_devi: abs value of angle between detx and path
;  step_time: time interval between attitude steps

  atti=mrdfits(atti_file,1,atti_head)
  n_atti=n_elements(atti)

  step_time=total(atti(1:n_atti-1).time-atti(0:n_atti-2).time)/(n_atti-1)

  ;  make necessary adjust so interpolation works
  ;    wrap/unwrap RA
  !y.range=[-180,360]
  if(diag)then plot,atti.ra,psym=6
  tmp=atti(1:n_atti-1).ra-atti(0:n_atti-2).ra
  plc=where(abs(tmp) GT 330.0)
  if(plc(0) NE -1)then begin
    if(tmp(plc) LT 0)then begin
      atti(0:plc(0)).ra=atti(0:plc(0)).ra-360.
    endif else begin
      atti(plc(0)+1:n_atti-1).ra=atti(plc(0)+1:n_atti-1).ra-360.
    endelse
  endif 
  if(diag)then oplot,atti.ra,psym=6,symsize=0.5,color=220

  ;    wrap/unwrap PA
  if(diag)then plot,atti.angnorth,psym=6
  tmp=atti(1:n_atti-1).angnorth-atti(0:n_atti-2).angnorth
  plc=where(abs(tmp) GT 330.0)
  if(plc(0) NE -1)then begin
    if(tmp(plc) GT 0)then begin
      atti(0:plc(0)).angnorth=atti(0:plc(0)).angnorth+360.
    endif else begin
      atti(plc(0)+1:n_atti-1).angnorth=atti(plc(0)+1:n_atti-1).angnorth+360.
    endelse
  endif
  if(diag)then oplot,atti.angnorth,psym=6,symsize=0.5,color=220

  ; determine the angle between path and roll+90 between each entry
  ;   so there is one fewer of these than n_atti
  atti_path=dblarr(n_atti-1)
  atti_roll=dblarr(n_atti-1)
  atti_devi=dblarr(n_atti-1)
  atti_time=dblarr(n_atti-1)
  for i=0,n_atti-2 do begin
    posang,1,atti(i).ra/15.,atti(i).dec,atti(i+1).ra/15.,atti(i+1).dec,ang
    atti_path(i)=ang
    atti_devi(i)=acos(cos(((180.-atti(i).angnorth)-ang)*!pi/180.))*180./!pi
    atti_time(i)=(atti(i).time+atti(i+1).time)/2.
    atti_roll(i)=(atti(i).angnorth+atti(i+1).angnorth)/2. ; an average!
  endfor

  if(diag)then begin
  ; !x.title='!17AngNorth (!9%!17)'
  ; !y.title='!17P.A. of Motion( !9%!17)'
  ; plot,atti_roll,atti_path,psym=6
    !x.title='!17Step'
    !y.title='!17Angle'
    !x.range=[-10,n_atti+10]
    !y.range=[-180,180]
    junk_roll=atti_roll
    plc=where(atti_roll GT 180)
    if(plc(0) NE -1)then junk_roll=junk_roll-90
    plot,0-junk_roll
    oplot,atti_path,color=60
    junk=(atti_path-atti_path(1))-(atti_roll(1)-atti_roll)
    oplot,junk,color=220
    oplot,atti_devi,color=120
  endif

  ; temporary step - write out the regions for the attitude steps
  if(diag)then begin
    fits2reg,atti_file,1,'temp_atti.reg',1,2,-240,-1,'orange'
  endif
  !x.range=0
  !y.range=0

  end
