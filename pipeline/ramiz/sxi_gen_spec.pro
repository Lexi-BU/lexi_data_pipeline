FUNCTION extr_apec,kt

COMMON spec_models,apec_file,apec,kts,tbab_file,tbab,nhs

  lkts=alog10(kts)
  lkt=alog10(kt)
  uppr=min(where(kts GT kt))
  lowr=max(where(kts LT kt))
; print,lowr,kts(lowr),uppr,kts(uppr)
  if(uppr-lowr GT 1)then begin
    spec=apec(lowr+1,*)
  endif else begin
;   print,(lkts(uppr)-lkt),(lkt-lkts(lowr)),(lkts(uppr)-lkts(lowr))
    spec=((lkts(uppr)-lkt)*apec(lowr,*)+(lkt-lkts(lowr))*apec(uppr,*))/$
      (lkts(uppr)-lkts(lowr))
  endelse
  return,reform(spec)
  end

FUNCTION extr_powl,indx

COMMON spec_pars,rmf,effa,ener

  if(indx EQ 1.0)then begin
    spec=alog10(ener.e_max)-alog10(ener.e_min)
  endif else begin
    spec=(double(ener.e_max)^(1.-double(indx))-double(ener.e_min)^(1.-double(indx)))/(1.-double(indx))
  endelse
  return,spec
  end

FUNCTION extr_tbab,lnh

COMMON spec_models,apec_file,apec,kts,tbab_file,tbab,nhs

  if(lnh EQ 0)then begin
    spec=tbab(0,*)*0.0+1.0
    return,reform(spec)
  endif

  uppr=min(where(nhs GT lnh))
  lowr=max(where(nhs LT lnh))
; print,lowr,nhs(lowr),uppr,nhs(uppr)
  if(uppr-lowr GT 1)then begin
    spec=tbab(lowr+1,*)
  endif else begin
;   print,(nhs(uppr)-lnh),(lnh-nhs(lowr)),(nhs(uppr)-nhs(lowr))
    spec=(nhs(uppr)-lnh)*tbab(lowr,*)+(lnh-nhs(lowr))*tbab(uppr,*)
    spec=spec/(nhs(uppr)-nhs(lowr))
  endelse
  return,reform(spec)
  end
  
FUNCTION sxi_gen_spec,comp

;auth: kdkvp
;date: 01/12/24
;mods: none yet
;TBDS:
;purp: to create a spectrum in SMILE native energy bins
;      output is in counts/s/bin/arcmin^2
;inpt: comp: an emission component structure which is of the form
;      {mask:0,n_comp:6,type:strarr(7,1),lnh:fltarr(n_comp),par:fltarr(n_comp),norm:fltarr(n_comp)}
;        mask is ignored by this routine
;        n_comp is the number of valid components, which is <= the number elements of the following
;        type is a string array containing 'T' for thermal and 'P' for powerlaw
;        lnh is an array containing the log N(H) for each emission component
;        par is an array containing kT (for 'T') or index (for 'P') for each component
;        norm is an array containing the normalization per arcmin^2 for each component
;otpt: returns the spectrum (no response applied)

COMMON fixed,fov_x_size,fov_y_size,fov_x_0,fov_y_0,fov_pix_size,$
  pi_bin_size,frame_time,n_pi,n_ener,n_lcrv

  n_comp=comp.n_comp
  spec=fltarr(n_ener)

  for i=0,n_comp-1 do begin
    lnh=comp.lnh(i)
    abs_fact=extr_tbab(lnh)
    norm=comp.norm(i)

    if(comp.type(i) EQ 'T')then begin
      temp=extr_apec(comp.par(i))
    endif else begin
      temp=extr_powl(comp.par(i))
    endelse

    spec=spec+norm*temp*abs_fact
  endfor
  return,spec

  end

PRO test_bits

COMMON spec_models,apec_file,apec,kts,tbab_file,tbab,nhs
COMMON spec_pars,rmf,effa,ener

  sxi_kk_init
  n_comp=7
  comp={mask:0,n_comp:6,type:strarr(7,1),$
    lnh:fltarr(n_comp),$
    par:fltarr(n_comp),norm:fltarr(n_comp)}

; comp.n_comp=1
; comp.type(0)='T'
; comp.lnh(0)=19.05
; comp.par(0)=0.108486
; comp.norm(0)=1.0e-6

; comp.type(1)='P'
; comp.lnh(1)=20.0
; comp.par(1)=1.7
; comp.norm(1)=1.0e-7

  comp.n_comp=1
  comp.type(0)='P'
  comp.lnh(0)=20.0
  comp.par(0)=1.7
  comp.norm(0)=1.0e-7

  apec_file='/Users/kuntz/idl/smile_task/calib/smile_apec.fits'
  tbab_file='/Users/kuntz/idl/smile_task/calib/smile_tbab.fits'
  apec=mrdfits(apec_file,'SPECBLOC')
  kts=mrdfits(apec_file,'kT')
  tbab=mrdfits(tbab_file,'SPECBLOC')
  nhs=mrdfits(tbab_file,'LOG_COL_DEN')
  ener=mrdfits(tbab_file,'EBOUNDS') 
  ener(0).e_min=5e-6

  arf_file='/Users/kuntz/idl/smile_task/calib/sxi_sim_test.arf'
  rmf_file='/Users/kuntz/idl/smile_task/calib/sxi_sim_test.rmf'
  read_rmf,rmf_file,emlo,emhi,rmf,chan,eolo,eohi
  read_arf,arf_file,emlo,emhi,effa
  e_mid=(eolo+eohi)/2.

; fact=extr_tbab(comp.lnh(0))
; emmi=extr_apec(comp.par(0))
; test=emmi*fact*comp.norm(0)*effa
  fact=extr_tbab(comp.lnh(0))
  emmi=extr_powl(comp.par(0))
  test=emmi*fact*comp.norm(0)*effa
  
  test=rmf#test
  print,'In spectrum: ',total(test(10:110))

; fact=extr_tbab(comp(1).lnh)
; emmi=extr_powl(comp(1).par)
; stop
; test=test+(emmi*fact*comp(1).norm*effa)

  test=sxi_gen_spec(comp)*effa
  spec=rmf#test
  print,'In generated: ',total(spec(10:110))

  spawn,'rm test.scr'
  spawn,'rm test.fak'
  openw,olun,'test.scr',/get_lun
  printf,olun,'abund wilm'
  printf,olun,'cpd /xs'
; printf,olun,'model tbabs(apec)
  printf,olun,'model tbabs(pow)'
  printf,olun,10.0^(comp.lnh(0)-22.0)
; printf,olun,comp.par(0)
; printf,olun,'1.0'
; printf,olun,'0.0'
; printf,olun,comp.norm(0)
  printf,olun,comp.par(0)
  printf,olun,comp.norm(0)
  printf,olun,''
  printf,olun,'fakeit none'
  printf,olun,'/Users/kuntz/idl/smile_task/calib/sxi_sim_test.rmf'
  printf,olun,'/Users/kuntz/idl/smile_task/calib/sxi_sim_test.arf'
  printf,olun,'n'
  printf,olun,''
  printf,olun,'test.fak'
  printf,olun,'1.0e8'
  printf,olun,'cpd /xs'
  printf,olun,'setp en'
  printf,olun,'ig 0.0-0.1'
  printf,olun,'ig 10.0-**'
  printf,olun,'plot data'
  printf,olun,'ig 0-10,112-**'
  printf,olun,'show files'
  printf,olun,'exit'
  free_lun,olun
  spawn,'xspec < test.scr'

  test=mrdfits('test.fak',1)
  oplot,e_mid,test.rate,psym=10,color=220
  stop

  end
