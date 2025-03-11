PRO sxi_cxrb_bkg,init,atti_file,gti_file,ei,ef,t_step,t_lim,out_dir

;auth: kdkvp
;date: 21/11/24 
;purp: create cxrb images for a series of time steps
;mods:
;TBDS:
;inpt:
;      init      :
;      atti_file :
;      gtis_file :
;      ei        : lower energy bound (eV)
;      ef        : upper energy bound (eV)
;      t_step    : length of time step
;      t_lim     : [start,stop] times in spacecraft seconds
;      out_dir   : name of directory in which to save
; otpt:
;      
; as well as the following files
;

COMMON fixed,fov_x_size,fov_y_size,fov_x_0,fov_y_0,fov_pix_size,$
  pi_bin_size,frame_time,n_pi,n_ener,n_lcrv
COMMON struc,coor,raw_src,prc_src
COMMON dirs,calib,psf_file,fov_file,vig_file,arf_file,rmf_file,bsc_file,$
  cxrb_file,ps_spec_file
COMMON spec_models,apec_file,apec,kts,tbab_file,tbab,nhs
COMMON spec_pars,rmf,effa,ener

; sets up for multiple snapshots

  tt1=systime(/seconds)
  spawn,'mkdir '+out_dir
  diag=1

; reading the cxrb database into a common block, if it isn't already

  if(init)then begin

    ; read the CXRB database

    t1=systime(/seconds)
    db=mrdfits(calib+cxrb_file,1,db_head)
    n_side=sxpar(db_head,'NSIDE')
    n_pix=nside2npix(n_side)
    n_db=n_elements(db)
    if(n_db NE n_pix)then begin
      print,'Fatal error, DB incorrect number of entries'
      stop
    endif
    htype=strtrim(sxpar(db_head,'ORDERING'),2)
    t2=systime(/seconds)
    print,'Time to read CXRB-DB: ',t2-t1

    ; read the spectral data files - add to common blocks

    apec=mrdfits(calib+apec_file,'SPECBLOC')
    kts=mrdfits(calib+apec_file,'kT')
    tbab=mrdfits(calib+tbab_file,'SPECBLOC')
    nhs=mrdfits(calib+tbab_file,'LOG_COL_DEN')
    ener=mrdfits(calib+tbab_file,'EBOUNDS')
    ener(0).e_min=5e-6

    init=0
  endif  

  ; get the vignetting image - which sets the output image size
  ;   input pixel size is 1'
  ;   output pixel size is 3'
  vig=mrdfits(calib+'vig.fits',0,head)
  coor_head,head,coor
  n_detx=coor.naxis(0)/3.
  n_dety=coor.naxis(1)/3.
  coor.cdelt=coor.cdelt*3*[-1,1]
  coor.crpix=[n_detx/2.,n_dety/2.]-0.5
  vig=rebin(vig,n_detx,n_dety)

; read the attitude file

  sxi_read_atti,atti_file,atti,n_atti,atti_head,atti_path,atti_roll,$
    atti_devi,atti_time,step_time,diag

; read the ARF & RMF 

  arf=mrdfits(calib+arf_file,1)
  arf=arf.specresp
  n_arf=n_elements(arf)
  read_rmf,calib+rmf_file,emlo,emhi,drmf,indx,eolo,eohi
  ; note that drmf has dimensions [output channel,input e_bins]
  ; note that the output channel size is bigger than n_pi
  ; emlo and emhi (corresponding to input e_bins), eolo and eohi
  ;   corresponding to output channels are all in keV

  ; now figure out which channels we will need
  plc=where(eohi GT ei/1000. and eolo LT ef/1000.)
  clo=min(plc)
  chi=max(plc)

; set up the time step list

  d_time=t_lim(1)-t_lim(0)
  n_time=fix(d_time/t_step)
  if(d_time-n_time*t_step GT 0)then begin
    time_list=dindgen(n_time+1)*t_step+t_lim(0) ; start of each time interval
  endif else begin
    time_list=dindgen(n_time)*t_step+t_lim(0) ; start of each time interval
  endelse
  n_time=n_elements(time_list)

; apply the GTI to the time step list
  sxi_gti_filt,gti_file,[time_list,t_lim(1)],time_frac
  ; time_frac has one more element than time_list, but it will be zero

; interpolate attitude to time step list

  kinterp,atti.time,atti.ra,time_list,time_ra
  kinterp,atti.time,atti.dec,time_list,time_de
  kinterp,atti.time,atti.angnorth,time_list,time_pa
  time_pa=(time_pa-90.)*!dpi/180.

; construct the cube of indices

  t1=systime(/seconds)
  indx=lonarr(n_detx,n_dety,n_time)
  t2=systime(/seconds)
  print,'Time to construct index cube: ',t2-t1

; create data for the cube of indices

  t1=systime(/seconds)
  fov_x=fltarr(n_detx,n_dety)
  for i=0,n_detx-1 do fov_x(i,*)=i
  fov_y=fltarr(n_detx,n_dety)
  for i=0,n_dety-1 do fov_y(*,i)=i
  cdelt=coor.cdelt
  crpix=coor.crpix
  ctype=['RA---TAN','DEC--TAN']
  x=(fov_x-crpix(0))*(0-1)*cdelt(0)
  y=(fov_y-crpix(1))*cdelt(1)

  !x.range=0
  !y.range=0
  for i=0,n_time-1 do begin ; for each time step
  ; create R.A. & Dec. for each pixel
    ; want to rotate around the center of the FOV, not corner
    tx=x*cos(time_pa(i))-y*sin(time_pa(i))
    ty=x*sin(time_pa(i))+y*cos(time_pa(i))
    wcsxy2sph,tx,ty,ra,de,crval=[time_ra(i),time_de(i)],ctype=coor.ctype
    euler,ra,de,lii,bii,1

  ; determine index (location in db)  for each pixel
    de=(90.0-bii)*!dpi/180.
    ra=lii*!dpi/180.
    
    if(htype EQ 'RING')then begin
      ang2pix_ring,n_side,de,ra,ind
    endif else begin
      ang2pix_nest,n_side,de,ra,ind
    endelse  
    indx(*,*,i)=ind
  endfor
  t2=systime(/seconds)
  print,'Time to fill the index cube: ',t2-t1

; the following is done to reduce the amount of memory needed
  ; get a list of unique index entries

  uniq=indx(sort(indx))
  uniq=unique(uniq)
  n_uniq=n_elements(uniq)

  ; extract from the DB only the items needed
  t1=systime(/seconds)
  tdb=db(uniq) ; note that the new indices match those now in index
  t2=systime(/seconds)
  print,'Time to extract subset of database: ',t2-t1

  ; convert index to location in tdb rather than position in db
  for i=0,n_uniq-1 do begin
    plc=where(indx EQ uniq(i))
    indx(plc)=i
  endfor

  ; reduce the point spead function to just the channels we need
  rmf=drmf(clo:chi,*)

; construct a spectrum for each unique index
  ; and, in order to be efficient, multiply by the arf and convolve with rmf
 
  t1=systime(/seconds)
; tspec=fltarr(n_uniq,n_arf)
  tphot=fltarr(n_uniq)
  for i=0,n_uniq-1 do begin
;   tspec(i,*)=sxi_gen_spec(tdb(i)) 
    tphot(i)=total(rmf#(sxi_gen_spec(tdb(i))*arf))
  endfor
  t2=systime(/seconds)
  print,'Time to create spectra: ',t2-t1 
  stop
 
; construct the images

  t1=systime(/seconds)
  for i=0,n_time-1 do begin
    imag=fltarr(n_detx,n_dety)
    for ix=0,n_detx-1 do begin
      for iy=0,n_dety-1 do begin
        ;convolve with LSF
        imag(ix,iy)=tphot(indx(ix,iy,i))
;0        imag(ix,iy)=tdb(indx(ix,iy,i)).lnh(1) ; debugging [ra,dec] probs
      endfor ; loop over dety
    endfor ; loop over detx

    ; scale the image from counts/s/arcmin to counts/pixel
    imag=imag*abs(cdelt(0)*cdelt(1)*3600.)*time_frac(i)
    ; apply the vignetting map
    imag=imag*vig
    out_name=out_dir+'/'+'test_file_'+string(i,format='(i3.3)')+'.fits'
    mwrfits,imag,out_name,/create
    head=headfits(out_name,exten=0)
    sxaddpar,head,'TIMEINIT',time_list(i)
    sxaddpar,head,'TIMEFINL',time_list(i)+t_step
    sxaddpar,head,'EXPOSURE',time_frac(i)
    sxaddpar,head,'COMMENT','created by sxi_cxrb_bkg'
    modfits,out_name,0,head
  endfor ; loop over time steps  
  t2=systime(/seconds)
  print,t2-t1
  print,t2-tt1

  end
