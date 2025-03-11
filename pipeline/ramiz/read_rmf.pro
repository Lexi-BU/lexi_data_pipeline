PRO read_rmf,file,e_low,e_hig,det_mat,chan,e_min,e_max

  if(n_params(0) LT 7)then begin
    print,"read_rmf,file,emlow,emhig,det_mat,chan,eolow,eohig"
    print,"Purpose:to read an rmf response file"
    print,"Inputs:"
    print,"  file:the rmf file to be read"
    print,"Outputs:"
    print,"  e_low:energy of the low side of the energy bins of model"
    print,"  e_hig:energy of the high side of the energy bins of model"
    print,"  det_mat:the detector response matrix"
    print,"  chan:vector of channel numbers"
    print,"  e_min:energy of the low side of the energy bins of output"
    print,"  e_max:energy of the high side of the energy bins of output"
    return
  endif

  fxbopen,unit1,file,'matrix',header
  n_chan=sxpar(header,'DETCHANS')
  n_rows=sxpar(header,'NAXIS2')
  det_mat=fltarr(n_chan,n_rows)

  fxbread,unit1,e_low,1
  fxbread,unit1,e_hig,2

  for i=0,n_rows-1 do begin
    fxbread,unit1,n_grp,3,i+1
    fxbread,unit1,f_chan,4,i+1
    fxbread,unit1,n_chan,5,i+1
    fxbread,unit1,matrix,6,i+1
    if(n_grp EQ 1)then begin
      f_chan=f_chan(0)
      n_chan=n_chan(0)
      det_mat(f_chan:f_chan+n_chan-1,i)=matrix(0:n_chan-1)
    endif else begin
      matrixi=0
      for j=0,n_grp-1 do begin
        det_mat(f_chan(j):f_chan(j)+n_chan(j)-1,i)=matrix(matrixi:matrixi+n_chan(j)-1)
        matrixi=matrixi+n_chan(j)
      endfor
    endelse
  endfor

  fxbclose,unit1

  fxbopen,unit2,file,'ebounds',header
  fxbread,unit2,chan,1
  fxbread,unit2,e_min,2
  fxbread,unit2,e_max,3
  fxbclose,unit2

  end
